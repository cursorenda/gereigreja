from unittest import skipUnless

from django.conf import settings
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone


@skipUnless(settings.MIGRATION_MODULES == {}, "Requires core.settings_test_migrations.")
class EventCriteriaMigrationTests(TransactionTestCase):
    before = ("eventos", "0018_alter_evento_tipo")
    after = ("eventos", "0019_protect_participation_criteria")

    def _migrate(self, target):
        executor = MigrationExecutor(connection)
        return executor.migrate([target]).apps

    def _layout(self, table, root_column, root_table):
        with connection.cursor() as cursor:
            description = connection.introspection.get_table_description(cursor, table)
            constraints = connection.introspection.get_constraints(cursor, table)
        self.assertEqual([(col.name, col.null_ok) for col in description], [
            ("id", False), ("evento_id", False), (root_column, False),
        ])
        self.assertTrue(any(c["primary_key"] and c["columns"] == ["id"] for c in constraints.values()))
        self.assertTrue(any(c["unique"] and c["columns"] == ["evento_id", root_column]
                            for c in constraints.values()))
        for column, target in (("evento_id", "eventos_evento"), (root_column, root_table)):
            self.assertTrue(any(c["columns"] == [column] and c["foreign_key"] == (target, "id")
                                for c in constraints.values()))
            self.assertTrue(any(c["columns"] == [column] and c["index"] for c in constraints.values()))
        return constraints

    def test_forward_and_reverse_preserve_existing_tables_and_link_pks(self):
        self.addCleanup(self._migrate, self.after)
        apps = self._migrate(self.before)
        user = apps.get_model("auth", "User").objects.create(username="migration_criteria")
        ministry = apps.get_model("configuracao", "Ministerio").objects.create(
            nome_fantasia="Criteria migration", administrador_principal_id=user.pk,
        )
        church = apps.get_model("configuracao", "Igreja").objects.create(
            nome_igreja="Criteria migration", ministerio_id=ministry.pk,
        )
        event = apps.get_model("eventos", "Evento").objects.create(
            titulo="Historical", igreja_id=church.pk, data_inicio=timezone.now(),
        )
        mappings = (
            ("tipos_participantes", "TipoPessoa", "tipopessoa_id", "EventoTipoParticipante"),
            ("status_participantes", "StatusPessoa", "statuspessoa_id", "EventoStatusParticipante"),
        )
        expected = []
        for field, root_model, column, _ in mappings:
            root = apps.get_model("secretaria", root_model).objects.create(nome="Historical")
            getattr(event, field).add(root)
            through = event._meta.get_field(field).remote_field.through
            table = "eventos_evento_" + field
            self.assertEqual(through._meta.db_table, table)
            layout = self._layout(table, column, "secretaria_" + root_model.lower())
            row = through.objects.values_list("pk", "evento_id", column).get()
            self.assertEqual(row[1:], (event.pk, root.pk))
            expected.append((table, layout, row))

        for target in (self.after, self.before):
            apps = self._migrate(target)
            event_model = apps.get_model("eventos", "Evento")
            for (field, root_model, column, explicit_model), (table, layout, row) in zip(mappings, expected):
                with self.subTest(target=target, field=field):
                    through = event_model._meta.get_field(field).remote_field.through
                    if target == self.after:
                        self.assertIs(through, apps.get_model("eventos", explicit_model))
                    else:
                        self.assertTrue(through._meta.auto_created)
                    self.assertEqual(through._meta.db_table, table)
                    self.assertEqual(self._layout(table, column, "secretaria_" + root_model.lower()), layout)
                    self.assertEqual(list(through.objects.values_list("pk", "evento_id", column)), [row])
