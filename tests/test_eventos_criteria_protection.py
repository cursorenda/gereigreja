from datetime import timedelta

from django.contrib import admin
from django.contrib.admin.utils import NestedObjects
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models import ProtectedError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from configuracao.models import Igreja, Ministerio
from eventos.forms import EventoForm
from eventos.models import Evento
from secretaria.models import Membro, Pessoa, StatusHistorico, StatusPessoa, TipoPessoa


class EventCriteriaProtectionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(username="criteria_admin")
        ministry = Ministerio.objects.create(
            nome_fantasia="Criteria", administrador_principal=cls.user, ativo=True,
        )
        cls.church = Igreja.objects.create(nome_igreja="Criteria Congregation", ministerio=ministry)
        cls.start = timezone.localtime().replace(second=0, microsecond=0)
        cls.event = Evento.objects.create(igreja=cls.church, titulo="Criteria", data_inicio=cls.start)

    def test_catalog_delete_requires_explicit_unlink(self):
        for model, field in ((TipoPessoa, "tipos_participantes"), (StatusPessoa, "status_participantes")):
            with self.subTest(model=model):
                free = model.objects.create(nome="Free")
                free_pk = free.pk
                free.delete()
                self.assertFalse(model.objects.filter(pk=free_pk).exists())
                root = model.objects.create(nome="Protected")
                root_pk = root.pk
                relation = getattr(self.event, field)
                relation.add(root)
                with self.assertRaises(ProtectedError):
                    root.delete()
                self.assertTrue(model.objects.filter(pk=root_pk).exists())
                self.assertTrue(Evento.objects.filter(pk=self.event.pk).exists())
                self.assertEqual(list(relation.all()), [root])
                relation.remove(root)
                root.delete()
                self.assertFalse(model.objects.filter(pk=root_pk).exists())

    def test_event_delete_cascades_only_to_links(self):
        event_pk = self.event.pk
        tipo = TipoPessoa.objects.create(nome="Type")
        status = StatusPessoa.objects.create(nome="Status")
        self.event.tipos_participantes.add(tipo)
        self.event.status_participantes.add(status)
        self.event.delete()
        self.assertFalse(Evento.objects.filter(pk=event_pk).exists())
        for relation, root in ((Evento.tipos_participantes, tipo), (Evento.status_participantes, status)):
            self.assertFalse(relation.through.objects.filter(evento_id=event_pk).exists())
            root.refresh_from_db()

    def test_m2m_manager_operations_preserve_catalogs(self):
        for model, field in ((TipoPessoa, "tipos_participantes"), (StatusPessoa, "status_participantes")):
            with self.subTest(model=model):
                first, second = [model.objects.create(nome=name) for name in ("First", "Second")]
                relation = getattr(self.event, field)
                relation.add(first)
                relation.set([second])
                self.assertEqual(list(relation.all()), [second])
                relation.remove(second)
                self.assertFalse(relation.exists())
                relation.add(first, second)
                relation.clear()
                self.assertFalse(relation.exists())
                self.assertEqual(model.objects.filter(pk__in=[first.pk, second.pk]).count(), 2)

    def test_person_protection_remains_and_history_survives_blocked_delete(self):
        tipo = TipoPessoa.objects.create(nome="Member type")
        member_status = StatusPessoa.objects.create(nome="Member status")
        status = StatusPessoa.objects.create(nome="Event status")
        member = Membro.objects.create(
            nome="Member", igreja=self.church, tipo_pessoa=tipo, status_pessoa=member_status,
        )
        self.event.tipos_participantes.add(tipo)
        self.event.tipos_participantes.remove(tipo)
        collector = NestedObjects(using=tipo._state.db)
        collector.collect([tipo])
        self.assertIn(Pessoa.objects.get(pk=member.pk), collector.protected)
        self.event.status_participantes.add(status)
        history = StatusHistorico.objects.create(membro=member, status_pessoa_novo=status)
        with self.assertRaises(ProtectedError):
            status.delete()
        history.refresh_from_db()
        self.assertEqual(history.status_pessoa_novo_id, status.pk)

    def _payload(self, tipo, status):
        return {
            "igreja": self.church.pk, "titulo": "Selected criteria", "tipo": "festa",
            "data_inicio": self.start.strftime("%Y-%m-%dT%H:%M"),
            "data_inicio_0": self.start.date().isoformat(),
            "data_inicio_1": self.start.time().isoformat(),
            "status_evento": "ativo", "status_operacional": "planejamento", "quantidade_dias": 1,
            "frequencia": "nenhuma", "intervalo": 1, "tipos_participantes": [tipo.pk],
            "status_participantes": [status.pk], "criado_por": self.user.pk,
        }

    def _assert_criteria(self, event, tipo, status):
        self.assertEqual(list(event.tipos_participantes.all()), [tipo])
        self.assertEqual(list(event.status_participantes.all()), [status])

    def test_product_form_saves_and_edits_criteria(self):
        tipo = TipoPessoa.objects.create(nome="Initial type")
        status = StatusPessoa.objects.create(nome="Initial status")
        request = RequestFactory().post("/")
        request.user = self.user
        request.igreja_ativa = self.church
        form = EventoForm(self._payload(tipo, status), request=request)
        self.assertTrue(form.is_valid(), form.errors)
        event = form.save(commit=False)
        event.save()
        form.save_m2m()
        self._assert_criteria(event, tipo, status)
        new_type = TipoPessoa.objects.create(nome="New type")
        new_status = StatusPessoa.objects.create(nome="New status")
        form = EventoForm(self._payload(new_type, new_status), instance=event, request=request)
        self.assertTrue(form.is_valid(), form.errors)
        self._assert_criteria(form.save(), new_type, new_status)

    def test_edit_view_copies_criteria_to_new_recurrence(self):
        tipo = TipoPessoa.objects.create(nome="Recurring type")
        status = StatusPessoa.objects.create(nome="Recurring status")
        payload = self._payload(tipo, status)
        payload.update(
            recorrente="on", frequencia="diaria",
            data_fim_recorrencia=(self.start.date() + timedelta(days=1)).isoformat(),
        )
        self.client.force_login(self.user)
        response = self.client.post(reverse("eventos:editar_evento", args=[self.event.pk]), payload)
        self.assertEqual(response.status_code, 302)
        recurrence = Evento.objects.get(titulo=payload["titulo"], igreja=self.church, data_inicio__gt=self.start)
        self._assert_criteria(recurrence, tipo, status)
        self.assertEqual(TipoPessoa.objects.filter(nome=tipo.nome).count(), 1)
        self.assertEqual(StatusPessoa.objects.filter(nome=status.nome).count(), 1)

    def test_event_admin_creates_edits_and_loads_criteria(self):
        tipo = TipoPessoa.objects.create(nome="Admin type")
        status = StatusPessoa.objects.create(nome="Admin status")
        extra_type = TipoPessoa.objects.create(nome="Extra admin type")
        payload = self._payload(tipo, status)
        payload["tipos_participantes"].append(extra_type.pk)
        self.client.force_login(self.user)
        response = self.client.post(reverse("admin:eventos_evento_add"), payload)
        self.assertEqual(response.status_code, 302, getattr(response, "context", None))
        event = Evento.objects.get(titulo="Selected criteria")
        self.assertCountEqual(event.tipos_participantes.all(), [tipo, extra_type])
        self.assertEqual(list(event.status_participantes.all()), [status])
        request = RequestFactory().get("/")
        request.user = self.user
        form = admin.site._registry[Evento].get_form(request, event)(instance=event)
        self.assertCountEqual(
            [item.pk for item in form.initial["tipos_participantes"]], [tipo.pk, extra_type.pk],
        )
        self.assertEqual([item.pk for item in form.initial["status_participantes"]], [status.pk])
        new_type = TipoPessoa.objects.create(nome="Replacement type")
        new_status = StatusPessoa.objects.create(nome="Replacement status")
        response = self.client.post(
            reverse("admin:eventos_evento_change", args=[event.pk]), self._payload(new_type, new_status),
        )
        self.assertEqual(response.status_code, 302, getattr(response, "context", None))
        self._assert_criteria(event, new_type, new_status)
        tipo.refresh_from_db()
        extra_type.refresh_from_db()
        status.refresh_from_db()

    def test_event_admin_criteria_widgets_respect_catalog_permissions_and_ordering(self):
        editor = get_user_model().objects.create_user(username="criteria_editor", is_staff=True)
        editor.user_permissions.add(Permission.objects.get(
            content_type__app_label="eventos", codename="change_evento",
        ))
        event_admin = admin.site._registry[Evento]
        for model, field_name in ((TipoPessoa, "tipos_participantes"), (StatusPessoa, "status_participantes")):
            with self.subTest(model=model):
                roots = [model.objects.create(nome=name) for name in ("Zeta", "Alfa", "Meio")]
                for may_add in (False, True):
                    if may_add:
                        editor.user_permissions.add(Permission.objects.get(
                            content_type__app_label="secretaria", codename=f"add_{model._meta.model_name}",
                        ))
                    request = RequestFactory().get("/")
                    request.user = get_user_model().objects.get(pk=editor.pk)
                    self.assertTrue(event_admin.has_change_permission(request, self.event))
                    form = event_admin.get_form(request, self.event)(instance=self.event)
                    self.assertIn(field_name, form.fields)
                    field = form.fields[field_name]
                    self.assertFalse(field.required)
                    self.assertIsInstance(field.widget, RelatedFieldWidgetWrapper)
                    self.assertEqual(field.widget.can_add_related, may_add)
                    self.assertEqual(list(field.queryset.filter(
                        pk__in=[root.pk for root in roots],
                    ).values_list("nome", flat=True)), ["Alfa", "Meio", "Zeta"])

    def test_root_admin_blocks_single_and_entire_bulk_selection(self):
        self.client.force_login(self.user)
        for model, field in ((TipoPessoa, "tipos_participantes"), (StatusPessoa, "status_participantes")):
            with self.subTest(model=model):
                protected = model.objects.create(nome="Protected criterion")
                free = model.objects.create(nome="Unreferenced criterion")
                getattr(self.event, field).add(protected)
                prefix = f"admin:secretaria_{model._meta.model_name}"
                single = self.client.post(reverse(prefix + "_delete", args=[protected.pk]), {"post": "yes"})
                self.assertEqual(single.status_code, 200)
                self.assertTrue(single.context["protected"])
                bulk = self.client.post(reverse(prefix + "_changelist"), {
                    "action": "delete_selected", "_selected_action": [protected.pk, free.pk], "post": "yes",
                })
                self.assertEqual(bulk.status_code, 200)
                self.assertTrue(bulk.context["protected"])
                self.assertEqual(model.objects.filter(pk__in=[protected.pk, free.pk]).count(), 2)
                self.assertTrue(getattr(self.event, field).filter(pk=protected.pk).exists())
