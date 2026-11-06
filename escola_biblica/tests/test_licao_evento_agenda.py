from datetime import timedelta
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from configuracao.models import Igreja, Ministerio
from escola_biblica.models import AnoLetivo, Classe, Licao, PeriodoEBD, Turma
from escola_biblica.services_agenda import set_licao_evento_agenda, sync_licao_evento_agenda
from eventos.models import Evento


class LicaoEventoAgendaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(username="agenda_admin")
        ministry = Ministerio.objects.create(
            nome_fantasia="Ministério Agenda", administrador_principal=cls.user,
        )
        cls.church = Igreja.objects.create(nome_igreja="Agenda EBD", ministerio=ministry, ebd_periodo="trimestre")
        cls.today = timezone.localdate()
        year = AnoLetivo.objects.create(ano=cls.today.year, ativo=True)
        PeriodoEBD.objects.create(
            ano_letivo=year, numero=1, tipo="trimestre",
            data_inicio=cls.today - timedelta(days=30), data_fim=cls.today + timedelta(days=30),
        )
        classroom = Classe.objects.create(nome="Classe Agenda", igreja=cls.church)
        cls.turma = Turma.objects.create(
            nome="Turma Agenda", igreja=cls.church, classe=classroom, ano_letivo=year,
        )
        cls.lesson = Licao.objects.create(turma=cls.turma, data=cls.today, tema="Original")
        cls.first = Evento.objects.create(igreja=cls.church, titulo="A", data_inicio=timezone.now())
        cls.second = Evento.objects.create(igreja=cls.church, titulo="B", data_inicio=timezone.now())

    def test_link_transitions_preserve_events_and_scope(self):
        other = Turma.objects.create(
            nome="Outra turma", igreja=self.church, classe=self.turma.classe,
            ano_letivo=self.turma.ano_letivo,
        )
        untouched = Licao.objects.create(
            turma=other, data=self.today, tema="Outra", evento_agenda=self.first,
        )
        events_before = set(Evento.objects.values_list("pk", flat=True))
        selected = Licao.objects.filter(pk=self.lesson.pk)
        for target, count in [(self.first.pk, 1), (self.first.pk, 0), (self.second.pk, 1), (None, 1)]:
            with self.subTest(target=target, count=count):
                self.assertEqual(
                    set_licao_evento_agenda(selected, evento_id=target, using=self.lesson._state.db),
                    count,
                )
                self.lesson.refresh_from_db()
                self.assertEqual(self.lesson.evento_agenda_id, target)
        untouched.refresh_from_db()
        self.assertEqual(untouched.evento_agenda_id, self.first.pk)
        self.assertEqual(set(Evento.objects.values_list("pk", flat=True)), events_before)

    def test_conflicting_explicit_alias_fails_before_transaction_without_writing(self):
        selected = Licao.objects.using("unused_alias").filter(pk=self.lesson.pk)
        with patch("escola_biblica.services_agenda.transaction.atomic") as atomic:
            with self.assertRaisesRegex(ValueError, "Queryset alias 'unused_alias' conflicts with write alias 'default'"):
                set_licao_evento_agenda(selected, evento_id=self.first.pk, using="default")
        atomic.assert_not_called()
        self.lesson.refresh_from_db()
        self.assertIsNone(self.lesson.evento_agenda_id)

    def test_matching_explicit_alias_is_accepted(self):
        selected = Licao.objects.using("default").filter(pk=self.lesson.pk)
        self.assertEqual(set_licao_evento_agenda(selected, evento_id=self.first.pk, using="default"), 1)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.evento_agenda_id, self.first.pk)

    def test_sync_assigns_the_normal_event(self):
        sync_licao_evento_agenda(self.lesson)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.evento_agenda.tipo, "escola_dominical")
        self.assertEqual(self.lesson.evento_agenda.igreja_id, self.church.pk)

    def test_sync_moves_all_duplicate_links_before_deleting_duplicate(self):
        for status in ("ativo", "cancelado"):
            with self.subTest(status=status):
                Evento.objects.filter(tipo="escola_dominical").delete()
                principal, duplicate = [
                    Evento.objects.create(
                        igreja=self.church, titulo=title, data_inicio=timezone.now(),
                        tipo="escola_dominical", status_evento=status,
                    )
                    for title in ("Principal", "Duplicado")
                ]
                another = Turma.objects.create(
                    nome=f"Turma {status}", igreja=self.church, classe=self.turma.classe,
                    ano_letivo=self.turma.ano_letivo,
                )
                other_lesson = Licao.objects.create(
                    turma=another, data=self.today, tema="Outra", evento_agenda=duplicate,
                )
                self.lesson.evento_agenda = duplicate
                self.lesson.save(update_fields=["evento_agenda"])
                sync_licao_evento_agenda(self.lesson)
                self.lesson.refresh_from_db()
                other_lesson.refresh_from_db()
                self.assertEqual(self.lesson.evento_agenda_id, principal.pk)
                self.assertEqual(other_lesson.evento_agenda_id, principal.pk)
                self.assertFalse(Evento.objects.filter(pk=duplicate.pk).exists())

    def test_registered_admin_displays_but_ignores_posted_event(self):
        set_licao_evento_agenda(
            Licao.objects.filter(pk=self.lesson.pk), evento_id=self.first.pk,
            using=self.lesson._state.db,
        )
        self.lesson.refresh_from_db()
        request = RequestFactory().get("/")
        request.user = self.user
        model_admin = admin.site._registry[Licao]
        self.assertNotIn("evento_agenda", model_admin.get_form(request, self.lesson).base_fields)
        self.assertIn("evento_agenda", model_admin.get_readonly_fields(request, self.lesson))

        self.client.force_login(self.user)
        url = reverse("admin:escola_biblica_licao_change", args=[self.lesson.pk])
        self.assertContains(self.client.get(url), 'field-evento_agenda')
        response = self.client.post(url, {
            "turma": self.turma.pk, "data": self.today.isoformat(), "tema": "Editada",
            "status": "ativa", "evento_agenda": self.second.pk, "_save": "Salvar",
        })
        self.assertEqual(response.status_code, 302)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.tema, "Editada")
        self.assertEqual(self.lesson.evento_agenda_id, self.first.pk)
