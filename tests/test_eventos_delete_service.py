from datetime import time, timedelta
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from configuracao.models import Igreja, Ministerio, ProgramacaoPadraoIgreja
from escola_biblica.models import AnoLetivo, Classe, Licao, PeriodoEBD, Turma
from eventos.models import Evento
from eventos.services_mutations import delete_event, delete_events


class EventDeleteServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(username="delete_events")
        ministry = Ministerio.objects.create(nome_fantasia="Delete", administrador_principal=cls.user, ativo=True)
        church = Igreja.objects.create(nome_igreja="Delete Test Congregation", ministerio=ministry, ebd_periodo="trimestre")
        cls.first = Evento.objects.create(titulo="A", igreja=church, data_inicio=timezone.now())
        cls.second = Evento.objects.create(titulo="B", igreja=church, data_inicio=timezone.now())
        today = timezone.localdate()
        year = AnoLetivo.objects.create(ano=today.year, ativo=True)
        PeriodoEBD.objects.create(
            ano_letivo=year, numero=1, tipo="trimestre",
            data_inicio=today - timedelta(days=30), data_fim=today + timedelta(days=30),
        )
        classroom = Classe.objects.create(nome="Delete", igreja=church)
        turma = Turma.objects.create(nome="Delete", classe=classroom, igreja=church, ano_letivo=year)
        cls.lesson = Licao.objects.create(turma=turma, data=today, tema="Vínculo", evento_agenda=cls.first)

    def assert_first_deleted(self):
        self.assertFalse(Evento.objects.filter(pk=self.first_id).exists())
        self.assertTrue(Evento.objects.filter(pk=self.second.pk).exists())
        self.lesson.refresh_from_db()
        self.assertIsNone(self.lesson.evento_agenda_id)

    def setUp(self):
        self.first_id = self.first.pk

    def test_single_delete_owns_collector_set_null(self):
        delete_event(self.first)
        self.assert_first_deleted()

    def test_bulk_delete_preserves_selection_and_set_null(self):
        third = Evento.objects.create(
            titulo="C", igreja=self.second.igreja, data_inicio=timezone.now(),
        )
        delete_events(Evento.objects.filter(pk__in=[self.first.pk, third.pk]), using="default")
        self.assert_first_deleted()
        self.assertFalse(Evento.objects.filter(pk=third.pk).exists())

    def test_queryset_alias_mismatch_fails_before_transaction(self):
        with patch("eventos.services_mutations.transaction.atomic") as atomic:
            with self.assertRaisesRegex(ValueError, "unused_alias.*default"):
                delete_events(Evento.objects.using("unused_alias").filter(pk=self.first.pk), using="default")
        atomic.assert_not_called()
        self.assertTrue(Evento.objects.filter(pk=self.first.pk).exists())
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.evento_agenda_id, self.first.pk)

    def test_instance_alias_mismatch_fails_before_transaction(self):
        with patch("eventos.services_mutations.transaction.atomic") as atomic:
            with self.assertRaisesRegex(ValueError, "default.*unused_alias"):
                delete_event(self.first, using="unused_alias")
        atomic.assert_not_called()
        self.assertTrue(Evento.objects.filter(pk=self.first.pk).exists())

    def test_matching_explicit_queryset_alias(self):
        delete_events(Evento.objects.using("default").filter(pk=self.first.pk), using="default")
        self.assert_first_deleted()

    def test_view_preserves_get_and_post_behavior(self):
        self.client.force_login(self.user)
        url = reverse("eventos:excluir_evento", args=[self.first.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Evento.objects.filter(pk=self.first.pk).exists())
        response = self.client.post(url)
        self.assertRedirects(response, reverse("eventos:lista_eventos"), fetch_redirect_response=False)
        self.assert_first_deleted()

    def test_view_rejects_anonymous_request(self):
        response = self.client.post(reverse("eventos:excluir_evento", args=[self.first.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Evento.objects.filter(pk=self.first.pk).exists())

    def test_registered_admin_single_delete(self):
        request = RequestFactory().post("/")
        request.user = self.user
        admin.site._registry[Evento].delete_model(request, self.first)
        self.assert_first_deleted()

    def test_registered_admin_delete_selected_preserves_unselected_event(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("admin:eventos_evento_changelist"), {
            "action": "delete_selected", "_selected_action": [self.first.pk], "post": "yes",
        })
        self.assertEqual(response.status_code, 302)
        self.assert_first_deleted()

    def test_unsaved_manual_pk_cannot_delete_existing_row(self):
        fake = Evento(pk=self.first.pk)
        self.assertTrue(fake._state.adding)
        self.assertIsNone(fake._state.db)
        with patch("eventos.services_mutations.router.db_for_write") as router_write:
            with patch("eventos.services_mutations.transaction.atomic") as atomic:
                with self.assertRaisesRegex(ValueError, "requires a persisted Evento instance"):
                    delete_event(fake)
        router_write.assert_not_called()
        atomic.assert_not_called()
        self.first.refresh_from_db()
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.evento_agenda_id, self.first.pk)

    def test_unsaved_without_pk_is_rejected_before_router_and_atomic(self):
        event = Evento()
        with patch("eventos.services_mutations.router.db_for_write") as router_write:
            with patch("eventos.services_mutations.transaction.atomic") as atomic:
                with self.assertRaisesRegex(ValueError, "requires a persisted Evento instance"):
                    delete_event(event)
        router_write.assert_not_called()
        atomic.assert_not_called()

    def test_empty_queryset_returns_zero_and_preserves_events(self):
        before = set(Evento.objects.values_list("pk", flat=True))
        count, details = delete_events(Evento.objects.none(), using="default")
        self.assertEqual(count, 0)
        self.assertIsInstance(details, dict)
        self.assertEqual(set(Evento.objects.values_list("pk", flat=True)), before)

    def test_admin_bulk_deletes_multiple_selected_events(self):
        third = Evento.objects.create(
            titulo="Unselected", igreja=self.second.igreja, data_inicio=timezone.now(),
        )
        first_id, second_id = self.first.pk, self.second.pk
        self.client.force_login(self.user)
        response = self.client.post(reverse("admin:eventos_evento_changelist"), {
            "action": "delete_selected", "_selected_action": [first_id, second_id], "post": "yes",
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Evento.objects.filter(pk__in=[first_id, second_id]).exists())
        self.assertTrue(Evento.objects.filter(pk=third.pk).exists())

    def test_configuration_delete_preserves_event_selection(self):
        church = self.first.igreja
        other_church = Igreja.objects.create(nome_igreja="Other scope", ministerio=church.ministerio)
        program = ProgramacaoPadraoIgreja.objects.create(
            nome="Delete program", igreja=church, dia_semana=0, hora_inicio=time(9),
        )
        other_program = ProgramacaoPadraoIgreja.objects.create(
            nome="Other program", igreja=church, dia_semana=0, hora_inicio=time(9),
        )
        future = timezone.now() + timedelta(days=2)
        def event(title, **changes):
            values = dict(
                titulo=title, igreja=church, programacao_padrao=program,
                data_inicio=future, status_evento="ativo",
            )
            values.update(changes)
            return Evento.objects.create(**values)
        target = event("Selected")
        preserved = [
            event("Wrong church", igreja=other_church),
            event("Wrong program", programacao_padrao=other_program),
            event("Past", data_inicio=future - timedelta(days=5)),
            event("Cancelled", status_evento="cancelado"),
        ]
        url = reverse("configuracao:excluir_programacao_padrao_igreja", args=[church.pk, program.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Evento.objects.filter(pk=target.pk).exists())
        from django.contrib.auth.models import Group
        from contas.constants import ADMIN_MINISTERIO
        from configuracao.models import PerfilUsuario

        manager = get_user_model().objects.create_user(username="program_manager")
        group, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        manager.groups.add(group)
        PerfilUsuario.objects.update_or_create(user=manager, defaults={"ministerio": church.ministerio})
        self.client.force_login(manager)
        self.assertEqual(self.client.get(url).status_code, 302)
        self.assertTrue(Evento.objects.filter(pk=target.pk).exists())
        response = self.client.post(url)
        self.assertRedirects(
            response, reverse("configuracao:editar_igreja_config", args=[church.pk]) + "?aba=programacoes",
            fetch_redirect_response=False,
        )
        self.assertFalse(Evento.objects.filter(pk=target.pk).exists())
        self.assertEqual(Evento.objects.filter(pk__in=[item.pk for item in preserved]).count(), 4)
        self.assertFalse(ProgramacaoPadraoIgreja.objects.filter(pk=program.pk).exists())
