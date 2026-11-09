from datetime import datetime, time, timedelta, timezone as utc_timezone
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from configuracao.models import Igreja, Ministerio
from escola_biblica.models import AnoLetivo, Classe, Licao, PeriodoEBD, Turma
from escola_biblica.services_agenda import (
    set_licao_evento_agenda,
    sync_eventos_ebd_por_ministerio,
    sync_licao_evento_agenda,
)
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

    def test_deleting_last_lesson_keeps_event_after_commit_callbacks(self):
        self.first.tipo = "escola_dominical"
        self.first.save(update_fields=["tipo"])
        self._link_lesson(self.lesson, self.first)
        lesson_id = self.lesson.pk
        with self.captureOnCommitCallbacks(execute=True):
            self.lesson.delete()
        self.assertFalse(Licao.objects.filter(pk=lesson_id).exists())
        self.assertTrue(Evento.objects.filter(pk=self.first.pk).exists())

    def test_deleting_one_of_multiple_lessons_keeps_other_link(self):
        self.first.tipo = "escola_dominical"
        self.first.save(update_fields=["tipo"])
        self._link_lesson(self.lesson, self.first)
        other = self._create_other_lesson(self.first, "Outra")
        lesson_id = self.lesson.pk
        with self.captureOnCommitCallbacks(execute=True):
            self.lesson.delete()
        self.assertFalse(Licao.objects.filter(pk=lesson_id).exists())
        self.assertTrue(Evento.objects.filter(pk=self.first.pk).exists())
        other.refresh_from_db()
        self.assertEqual(other.evento_agenda_id, self.first.pk)

    def _link_lesson(self, lesson, event):
        set_licao_evento_agenda(
            Licao.objects.filter(pk=lesson.pk), evento_id=event.pk, using=lesson._state.db,
        )
        lesson.refresh_from_db()

    def _create_other_lesson(self, event, name):
        turma = Turma.objects.create(
            nome=name, igreja=self.church, classe=self.turma.classe,
            ano_letivo=self.turma.ano_letivo,
        )
        return Licao.objects.create(
            turma=turma, data=self.today, tema=name, evento_agenda=event,
        )

    def _assert_repeat_sync_retains_duplicates(self, status):
        principal, first_duplicate, second_duplicate = [
            Evento.objects.create(
                igreja=self.church, titulo=title, data_inicio=timezone.now(),
                tipo="escola_dominical", status_evento=event_status,
            )
            for title, event_status in (
                ("Principal", status), ("Duplicado 1", "ativo"), ("Duplicado 2", "ativo"),
            )
        ]
        self._link_lesson(self.lesson, first_duplicate)
        other = self._create_other_lesson(second_duplicate, "Outra")
        duplicates = Evento.objects.filter(pk__in=[first_duplicate.pk, second_duplicate.pk]).order_by("pk")
        duplicate_state = list(duplicates.values())
        event_ids = set(Evento.objects.values_list("pk", flat=True))

        # Keep the ministry's default occurrence on the same local day as the lessons.
        Igreja.objects.filter(pk=self.church.pk).update(ebd_dia_semana=self.today.weekday())
        sync_licao_evento_agenda(self.lesson)
        principal.refresh_from_db()
        self.assertEqual(principal.status_evento, status)
        for sync_number in (1, 2, 3):
            with self.subTest(sync=sync_number):
                sync_eventos_ebd_por_ministerio(self.church.ministerio)
                self.lesson.refresh_from_db()
                other.refresh_from_db()
                principal.refresh_from_db()
                self.assertEqual(principal.status_evento, status)
                self.assertEqual(self.lesson.evento_agenda_id, principal.pk)
                self.assertEqual(other.evento_agenda_id, principal.pk)
                self.assertEqual(set(Evento.objects.values_list("pk", flat=True)), event_ids)
                self.assertEqual(list(duplicates.values()), duplicate_state)

    def test_active_principal_retains_duplicates_and_repeat_sync_is_stable(self):
        self._assert_repeat_sync_retains_duplicates("ativo")

    def test_cancelled_principal_retains_duplicates_and_repeat_sync_is_stable(self):
        self._assert_repeat_sync_retains_duplicates("cancelado")

    def test_duplicate_selection_excludes_lower_pk_from_another_church(self):
        other_church = Igreja.objects.create(
            nome_igreja="Outra igreja agenda", ministerio=self.church.ministerio,
        )
        start = timezone.make_aware(datetime.combine(self.today, time(9)))
        other_event, principal, duplicate = [
            Evento.objects.create(
                igreja=church, titulo=title, data_inicio=start, tipo="escola_dominical",
            )
            for church, title in (
                (other_church, "Outra igreja"), (self.church, "Principal"),
                (self.church, "Duplicado"),
            )
        ]
        self.assertLess(other_event.pk, principal.pk)
        self._link_lesson(self.lesson, duplicate)
        other_state = Evento.objects.values().get(pk=other_event.pk)
        ids_before = set(Evento.objects.values_list("pk", flat=True))

        sync_licao_evento_agenda(self.lesson)

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.evento_agenda_id, principal.pk)
        self.assertEqual(Evento.objects.values().get(pk=other_event.pk), other_state)
        self.assertEqual(set(Evento.objects.values_list("pk", flat=True)), ids_before)

    def test_ministry_sync_separates_local_days_at_utc_boundary(self):
        next_day = self.today + timedelta(days=1)
        late_today = timezone.make_aware(datetime.combine(self.today, time(23, 59)))
        next_morning = timezone.make_aware(datetime.combine(next_day, time(9)))
        self.assertEqual(timezone.localdate(late_today), self.today)
        self.assertEqual(late_today.astimezone(utc_timezone.utc).date(), next_day)
        self.assertEqual(timezone.localdate(next_morning), next_day)
        self.assertEqual(next_morning.astimezone(utc_timezone.utc).date(), next_day)

        other_day = Evento.objects.create(
            igreja=self.church, titulo="Escola Dominical", data_inicio=next_morning,
            data_fim=next_morning + timedelta(minutes=90), tipo="escola_dominical",
            descricao=(
                "Evento consolidado da Escola Dominical gerado automaticamente pela EBD. "
                "As turmas e licoes continuam detalhadas no modulo Escola Biblica."
            ),
        )
        principal = Evento.objects.create(
            igreja=self.church, titulo="Hoje", data_inicio=late_today, tipo="escola_dominical",
        )
        Igreja.objects.filter(pk=self.church.pk).update(
            ebd_dia_semana=self.today.weekday(), ebd_horario=time(9),
        )
        other_state = Evento.objects.values().get(pk=other_day.pk)
        ids_before = set(Evento.objects.values_list("pk", flat=True))

        sync_licao_evento_agenda(self.lesson)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.evento_agenda_id, principal.pk)
        self.assertEqual(Evento.objects.values().get(pk=other_day.pk), other_state)

        # Exercise the final ministry normalization on a stored UTC boundary value.
        Evento.objects.filter(pk=principal.pk).update(data_inicio=late_today)
        with patch("escola_biblica.services_agenda.sync_licao_evento_agenda"):
            Igreja.objects.filter(pk=self.church.pk).update(ebd_dia_semana=next_day.weekday())
            sync_eventos_ebd_por_ministerio(self.church.ministerio)

        principal.refresh_from_db()
        self.lesson.refresh_from_db()
        self.assertEqual(timezone.localdate(principal.data_inicio), self.today)
        self.assertEqual(timezone.localtime(principal.data_inicio).time(), time(9))
        self.assertEqual(self.lesson.evento_agenda_id, principal.pk)
        self.assertEqual(Evento.objects.values().get(pk=other_day.pk), other_state)
        self.assertEqual(set(Evento.objects.values_list("pk", flat=True)), ids_before)

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
