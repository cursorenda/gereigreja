from contextlib import contextmanager
from unittest import skipUnless
from unittest.mock import patch

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import InMemoryStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection, transaction
from django.db.models import QuerySet
from django.db.models.signals import post_save
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from secretaria.models import GrupoCasa, Membro, Pessoa, StatusHistorico, StatusPessoa, TimelineEvent, TipoPessoa
from secretaria.pessoa_photo_storage import prepare_pessoa_photo
from tests.test_secretaria_pessoa_photo_storage import person_fixture


@contextmanager
def fail_history():
    original = QuerySet.create
    error = RuntimeError("historico indisponivel")

    def create(queryset, **values):
        if queryset.model is StatusHistorico:
            raise error
        return original(queryset, **values)

    with patch.object(QuerySet, "create", create):
        yield error


class PessoaCoordinatorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = person_fixture("default")
        cls.person.save()
        cls.other_status = StatusPessoa.objects.create(nome="Inativo")
        cls.other_type = TipoPessoa.objects.create(nome="Congregado")

    def history(self, person):
        return StatusHistorico.objects.filter(membro_id=person.pk)

    def test_status_failure_rolls_back_and_outer_transaction_remains_usable(self):
        person = self.person
        old = person.status_pessoa_id
        person.status_pessoa = self.other_status
        with transaction.atomic():
            with fail_history() as error, self.assertRaises(RuntimeError) as caught:
                person.save(update_fields=["status_pessoa"])
            self.assertIs(caught.exception, error)
            self.assertEqual(Pessoa.objects.get(pk=person.pk).status_pessoa_id, old)
            self.assertEqual(person.status_pessoa_id, self.other_status.pk)
            self.assertEqual(person._original_status_pessoa_id, old)
            self.assertEqual(self.history(person).count(), 1)
            person.nome = "Outer usable"
            person.save(update_fields=["nome"])
        person.save(update_fields=["status_pessoa"])
        self.assertEqual(Pessoa.objects.get(pk=person.pk).status_pessoa_id, self.other_status.pk)
        self.assertEqual(self.history(person).count(), 2)

    def test_type_grade_failure_restores_complete_and_deferred_instances(self):
        original = self.person
        for queryset in (Pessoa.objects.all(), Pessoa.objects.only("pk")):
            with self.subTest(queryset=queryset.query):
                Pessoa.objects.filter(pk=original.pk).update(
                    tipo_pessoa_id=original.tipo_pessoa_id, grau_eclesiastico="membro_comum",
                )
                person = queryset.get(pk=original.pk)
                person.tipo_pessoa = self.other_type
                deferred = person.get_deferred_fields()
                snapshot = person._original_tipo_pessoa_id
                count = self.history(person).count()
                with fail_history(), self.assertRaises(RuntimeError):
                    person.save(update_fields=["tipo_pessoa"])
                stored = Pessoa.objects.get(pk=person.pk)
                self.assertEqual((stored.tipo_pessoa_id, stored.grau_eclesiastico), (original.tipo_pessoa_id, "membro_comum"))
                self.assertIs(person.tipo_pessoa, self.other_type)
                self.assertEqual(person.get_deferred_fields(), deferred)
                self.assertEqual(person._original_tipo_pessoa_id, snapshot)
                if "grau_eclesiastico" not in deferred:
                    self.assertEqual(person.grau_eclesiastico, "membro_comum")
                self.assertEqual(self.history(person).count(), count)
                person.save(update_fields=["tipo_pessoa"])
                self.assertIsNone(Pessoa.objects.get(pk=person.pk).grau_eclesiastico)
                self.assertEqual(self.history(person).count(), count + 1)

    def test_new_pk_and_state_restored_after_history_failure_and_retry(self):
        for pk in (None, 7311):
            with self.subTest(pk=pk):
                person = Pessoa(pk=pk, nome="Nova", igreja_id=self.person.igreja_id,
                                tipo_pessoa_id=self.person.tipo_pessoa_id, status_pessoa_id=self.person.status_pessoa_id)
                count = Pessoa.objects.count()
                with fail_history(), self.assertRaises(RuntimeError):
                    person.save()
                self.assertEqual(Pessoa.objects.count(), count)
                self.assertEqual(person.pk, pk)
                self.assertTrue(person._state.adding)
                self.assertIsNone(person._state.db)
                self.assertIsNone(person.criado_em)
                self.assertIsNone(person.atualizado_em)
                self.assertIsNone(person.grau_eclesiastico)
                self.assertNotIn("_original_tipo_entrada", person.__dict__)
                person.save()
                self.assertEqual(self.history(person).count(), 1)

    def test_initial_history_failure_reverts_successful_entry_timeline_and_group(self):
        existing = self.person
        Pessoa.objects.filter(pk=existing.pk).update(rua="Rua teste", numero_casa="42")
        member = Membro(nome="Nova", igreja_id=existing.igreja_id, tipo_pessoa_id=existing.tipo_pessoa_id,
                        status_pessoa_id=existing.status_pessoa_id, rua="Rua teste", numero_casa="42")
        with fail_history(), self.assertRaises(RuntimeError):
            member.save()
        self.assertFalse(TimelineEvent.objects.exists())
        self.assertFalse(GrupoCasa.objects.exists())
        self.assertIsNone(Pessoa.objects.get(pk=existing.pk).grupo_casa_id)
        self.assertNotIn("_prev_address", member.__dict__)
        member.save()
        self.assertEqual(self.history(member).count(), 1)
        self.assertEqual(TimelineEvent.objects.filter(membro_id=member.pk, tipo_evento="entrada").count(), 1)
        self.assertIsNotNone(Pessoa.objects.get(pk=existing.pk).grupo_casa_id)

    def test_signal_failure_after_person_write_restores_instance(self):
        person = self.person
        original_timestamp = person.atualizado_em
        original_status = person.status_pessoa_id
        person.status_pessoa = self.other_status
        error = RuntimeError("signal")

        def fail(**kwargs):
            raise error

        post_save.connect(fail, sender=Pessoa)
        try:
            with self.assertRaises(RuntimeError) as caught:
                person.save()
        finally:
            post_save.disconnect(fail, sender=Pessoa)
        self.assertIs(caught.exception, error)
        self.assertEqual(person.status_pessoa_id, self.other_status.pk)
        self.assertEqual(person._original_status_pessoa_id, original_status)
        self.assertEqual(person.atualizado_em, original_timestamp)
        self.assertEqual(Pessoa.objects.get(pk=person.pk).status_pessoa_id, original_status)
        self.assertEqual(self.history(person).count(), 1)

    def test_photo_reused_after_history_failure(self):
        person = self.person
        storage = InMemoryStorage()
        old = storage.save("legacy.gif", ContentFile(b"old"))
        Pessoa.objects.filter(pk=person.pk).update(foto=old)
        old_status = person.status_pessoa_id
        person.foto = SimpleUploadedFile("new.gif", b"new")
        person.status_pessoa = self.other_status
        with patch.object(Pessoa._meta.get_field("foto"), "storage", storage), patch.object(storage, "save", wraps=storage.save) as upload:
            with fail_history(), self.assertRaises(RuntimeError):
                person.save(update_fields=["foto", "status_pessoa"])
            stored = Pessoa.objects.get(pk=person.pk)
            self.assertEqual((stored.foto.name, stored.status_pessoa_id), (old, old_status))
            key = person.foto.name
            self.assertTrue(person.foto._committed)
            self.assertTrue(storage.exists(key))
            self.assertTrue(storage.exists(old))
            self.assertEqual(person._original_status_pessoa_id, old_status)
            person.save(update_fields=["foto", "status_pessoa"])
            upload.assert_called_once()
        stored = Pessoa.objects.get(pk=person.pk)
        self.assertEqual((stored.foto.name, stored.status_pessoa_id), (key, self.other_status.pk))
        self.assertEqual(self.history(person).count(), 2)

    def test_excluded_photo_and_empty_fields_do_not_prepare_or_generate_history(self):
        person = self.person
        person.foto = SimpleUploadedFile("pending.gif", b"pending")
        person.nome = "Novo"
        with patch("secretaria.models.prepare_pessoa_photo") as prepare:
            with self.assertNumQueries(0):
                person.save(update_fields=[])
            self.assertNotEqual(Pessoa.objects.get(pk=person.pk).nome, "Novo")
            with self.assertNumQueries(1):
                person.save(update_fields=["nome"])
            prepare.assert_not_called()
        self.assertEqual(Pessoa.objects.get(pk=person.pk).nome, "Novo")
        self.assertFalse(person.foto._committed)
        self.assertEqual(self.history(person).count(), 1)

    def test_combined_transition_generates_one_history(self):
        person = self.person
        person.tipo_pessoa = self.other_type
        person.status_pessoa = self.other_status
        person.save(update_fields=["tipo_pessoa", "status_pessoa"])
        self.assertEqual(self.history(person).count(), 2)
        self.assertTrue(self.history(person).filter(
            tipo_pessoa_novo=self.other_type, status_pessoa_novo=self.other_status,
        ).exists())

    def test_photo_storage_failure_precedes_atomic_and_database_writes(self):
        person = self.person
        person.status_pessoa = self.other_status
        person.foto = SimpleUploadedFile("new.gif", b"new")
        error = RuntimeError("storage")
        storage = InMemoryStorage()
        with patch.object(Pessoa._meta.get_field("foto"), "storage", storage), patch.object(
            storage, "save", side_effect=error,
        ), patch("secretaria.models.transaction.atomic") as atomic, self.assertRaises(RuntimeError) as caught:
            person.save(update_fields=["foto", "status_pessoa"])
        atomic.assert_not_called()
        self.assertIs(caught.exception, error)
        self.assertFalse(person.foto._committed)
        self.assertEqual(Pessoa.objects.get(pk=person.pk).status_pessoa_id, person._original_status_pessoa_id)
        self.assertEqual(self.history(person).count(), 1)

    def test_full_save_with_committed_photo_does_not_query_previous_reference(self):
        Pessoa.objects.filter(pk=self.person.pk).update(foto="legacy.gif")
        person = Pessoa.objects.select_related("tipo_pessoa", "status_pessoa").get(pk=self.person.pk)
        person.nome = "Nome alterado"
        with CaptureQueriesContext(connection) as queries:
            person.save()
        selects = [q["sql"] for q in queries if q["sql"].lstrip().upper().startswith("SELECT ")]
        updates = [q["sql"] for q in queries if q["sql"].lstrip().startswith('UPDATE "secretaria_pessoa"')]
        self.assertEqual(selects, [])
        self.assertEqual(len(updates), 1)
        person.refresh_from_db()
        self.assertEqual(person.nome, "Nome alterado")
        self.assertEqual(person.foto.name, "legacy.gif")

    def test_photo_only_upload_clear_and_manual_reference_use_light_path(self):
        person = self.person
        storage = InMemoryStorage()
        person.foto = SimpleUploadedFile("new.gif", b"new")
        with patch.object(Pessoa._meta.get_field("foto"), "storage", storage), patch.object(
            storage, "save", wraps=storage.save,
        ) as upload, patch("secretaria.models.transaction.atomic") as atomic, patch(
            "secretaria.models.prepare_pessoa_photo", wraps=prepare_pessoa_photo,
        ) as prepare, patch.object(storage, "delete", wraps=storage.delete) as delete:
            person.save(update_fields=["foto"])
            key = person.foto.name
            person.foto = None
            person.save()
            self.assertFalse(Pessoa.objects.get(pk=person.pk).foto)
            person.foto = "manual.gif"
            person.save()
            atomic.assert_not_called()
            prepare.assert_called_once_with(person, using="default")
            upload.assert_called_once()
            delete.assert_not_called()
        self.assertTrue(storage.exists(key))
        self.assertEqual(Pessoa.objects.get(pk=person.pk).foto.name, "manual.gif")
        self.assertEqual(self.history(person).count(), 1)


HAS_SECONDARY = "secondary" in settings.DATABASES


@skipUnless(HAS_SECONDARY, "Use core.settings_test_multidb.")
class PessoaCoordinatorMultiDBTests(TestCase):
    databases = {"default", "secondary"} if HAS_SECONDARY else {"default"}

    def test_secondary_photo_status_rollback_and_retry(self):
        for alias in self.databases:
            person = person_fixture(alias)
            person.foto = f"{alias}.gif"
            person.save(using=alias)
        person = Pessoa.objects.using("secondary").get(pk=7301)
        old = person.status_pessoa_id
        person.status_pessoa = StatusPessoa.objects.using("secondary").create(nome="Inativo secondary")
        person.foto = SimpleUploadedFile("new.gif", b"new")
        storage = InMemoryStorage()
        attempts = []

        def record(*args, **kwargs):
            attempt = prepare_pessoa_photo(*args, **kwargs)
            attempts.append(attempt)
            return attempt

        with patch.object(Pessoa._meta.get_field("foto"), "storage", storage), patch(
            "secretaria.models.prepare_pessoa_photo", side_effect=record,
        ):
            with self.assertNumQueries(0, using="default"):
                with fail_history(), self.assertRaises(RuntimeError):
                    person.save(update_fields=["foto", "status_pessoa"], data_mudanca_status=timezone.now())
                self.assertEqual(person._original_status_pessoa_id, old)
                self.assertEqual(Pessoa.objects.using("secondary").get(pk=person.pk).foto.name, "secondary.gif")
                self.assertEqual(StatusHistorico.objects.using("secondary").count(), 1)
                self.assertFalse(TimelineEvent.objects.using("secondary").exists())
                person.save(update_fields=["foto", "status_pessoa"], data_mudanca_status=timezone.now())
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0].previous_db_key, "secondary.gif")
        self.assertEqual(Pessoa.objects.using("default").get(pk=7301).foto.name, "default.gif")
        self.assertEqual(StatusHistorico.objects.using("secondary").count(), 2)
        self.assertEqual(TimelineEvent.objects.using("secondary").filter(tipo_evento="mudanca_status").count(), 1)
