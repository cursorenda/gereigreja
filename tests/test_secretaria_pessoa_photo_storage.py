from unittest import skipUnless
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import InMemoryStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.test import TestCase

from configuracao.models import Igreja, Ministerio
from secretaria.models import Pessoa, StatusPessoa, TipoPessoa
from secretaria.pessoa_photo_storage import prepare_pessoa_photo


def person_fixture(using):
    user = get_user_model().objects.db_manager(using).create_user(username=f"photo-{using}")
    ministry, = Ministerio.objects.using(using).bulk_create([
        Ministerio(nome_fantasia=using, administrador_principal=user),
    ])
    church, = Igreja.objects.using(using).bulk_create([
        Igreja(nome_igreja=using, ministerio=ministry),
    ])
    kind = TipoPessoa.objects.using(using).create(nome="Membro")
    status = StatusPessoa.objects.using(using).create(nome="Ativo")
    return Pessoa(pk=7301, nome=using, igreja=church, tipo_pessoa=kind, status_pessoa=status)


class PessoaPhotoStorageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = person_fixture("default")
        cls.person.pk = None

    def setUp(self):
        self.storage = InMemoryStorage()
        storage_patch = patch.object(Pessoa._meta.get_field("foto"), "storage", self.storage)
        storage_patch.start()
        self.addCleanup(storage_patch.stop)

    def test_materializes_without_sql_and_isolates_names_and_caller_paths(self):
        keys = []
        for data in (b"first", b"second"):
            self.person.foto = ContentFile(data, name="../../segredo/igual.gif")
            with self.assertNumQueries(0):
                attempt = prepare_pessoa_photo(self.person, using="default")
            self.assertEqual(attempt.intent, "NEW")
            self.assertIsNone(attempt.previous_db_key)
            self.assertFalse(attempt.cleanup_eligible)
            self.assertIn(f"/_managed/{attempt.attempt_id}.gif", attempt.managed_candidate_key)
            self.assertNotIn("segredo", attempt.final_storage_key)
            self.assertNotIn("..", attempt.final_storage_key)
            self.assertEqual(self.person.foto.name, attempt.final_storage_key)
            self.assertTrue(self.person.foto._committed)
            with self.storage.open(attempt.final_storage_key, "rb") as saved:
                self.assertEqual(saved.read(), data)
            keys.append(attempt.final_storage_key)
        self.assertNotEqual(*keys)
        self.assertFalse(Pessoa.objects.exists())

    def test_returned_key_is_authoritative(self):
        self.person.foto = SimpleUploadedFile("nova.gif", b"photo")
        save = self.storage.save
        with patch.object(self.storage, "save", side_effect=lambda name, content, **kw: save(name + "-renamed", content, **kw)):
            attempt = prepare_pessoa_photo(self.person, using="default")
        self.assertEqual(attempt.final_storage_key, attempt.managed_candidate_key + "-renamed")
        self.assertEqual(self.person.foto.name, attempt.final_storage_key)
        self.assertTrue(self.storage.exists(attempt.final_storage_key))

    def test_legacy_manual_reference_and_clear_do_not_touch_storage(self):
        old = self.storage.save("fotos_pessoas/legacy.gif", ContentFile(b"old"))
        self.person.foto = old
        self.person.save()
        person = Pessoa.objects.get(pk=self.person.pk)
        with patch.object(self.storage, "save") as save, patch.object(self.storage, "delete") as delete:
            unchanged = prepare_pessoa_photo(person, using="default")
            self.assertEqual((unchanged.intent, unchanged.final_storage_key), ("NONE", old))
            person.foto = "fotos_pessoas/manual.gif"
            manual = prepare_pessoa_photo(person, using="default")
            self.assertEqual((manual.intent, manual.final_storage_key), ("NONE", person.foto.name))
            person.foto = None
            cleared = prepare_pessoa_photo(person, using="default")
            self.assertEqual((cleared.intent, cleared.previous_db_key), ("CLEAR", old))
            save.assert_not_called()
            delete.assert_not_called()
        self.assertTrue(self.storage.exists(old))
        self.assertEqual(Pessoa.objects.get(pk=person.pk).foto.name, old)

    def test_replacement_and_same_instance_retry_after_rollback_do_not_reupload(self):
        old = self.storage.save("fotos_pessoas/legacy.gif", ContentFile(b"old"))
        self.person.foto = old
        self.person.save()
        self.person.foto = SimpleUploadedFile("nova.gif", b"new")
        with patch.object(self.storage, "save", wraps=self.storage.save) as save, patch.object(self.storage, "delete") as delete:
            with self.assertNumQueries(1):
                attempt = prepare_pessoa_photo(self.person, using="default")
            self.assertEqual((attempt.intent, attempt.previous_db_key), ("REPLACE", old))
            self.assertEqual(Pessoa.objects.get(pk=self.person.pk).foto.name, old)
            with self.assertRaisesMessage(RuntimeError, "rollback"), transaction.atomic():
                self.person.save(update_fields=["foto"])
                raise RuntimeError("rollback")
            self.assertEqual(Pessoa.objects.get(pk=self.person.pk).foto.name, old)
            self.assertEqual(self.person.foto.name, attempt.final_storage_key)
            self.assertTrue(self.person.foto._committed)
            self.assertTrue(self.storage.exists(attempt.final_storage_key))
            self.person.save(update_fields=["foto"])
            save.assert_called_once()
            delete.assert_not_called()
        self.assertEqual(Pessoa.objects.get(pk=self.person.pk).foto.name, attempt.final_storage_key)
        self.assertTrue(self.storage.exists(old))

    def test_failed_upload_preserves_original_reference_and_stream_position(self):
        upload = SimpleUploadedFile("nova.gif", b"photo")
        upload.seek(2)
        self.person.foto = upload
        failure = RuntimeError("storage failed")

        def consume_then_fail(name, content, **kwargs):
            content.read()
            raise failure

        with patch.object(self.storage, "save", side_effect=consume_then_fail), patch.object(self.storage, "delete") as delete:
            with self.assertNumQueries(0), self.assertRaises(RuntimeError) as caught:
                prepare_pessoa_photo(self.person, using="default")
            delete.assert_not_called()
        self.assertIs(caught.exception, failure)
        self.assertIs(self.person.__dict__["foto"], upload)
        self.assertEqual(upload.tell(), 2)
        self.assertFalse(self.person.foto._committed)
        self.assertEqual(self.person.foto.name, "nova.gif")


HAS_SECONDARY = "secondary" in settings.DATABASES


@skipUnless(HAS_SECONDARY, "Use core.settings_test_multidb.")
class PessoaPhotoStorageMultiDBTests(TestCase):
    databases = {"default", "secondary"} if HAS_SECONDARY else {"default"}

    def test_previous_reference_uses_only_secondary_for_coincident_pk(self):
        for alias in self.databases:
            person = person_fixture(alias)
            person.foto = f"fotos_pessoas/{alias}.gif"
            Pessoa.objects.using(alias).bulk_create([person])
        person = Pessoa.objects.using("secondary").get(pk=7301)
        person.foto = SimpleUploadedFile("nova.gif", b"new")
        with patch.object(Pessoa._meta.get_field("foto"), "storage", InMemoryStorage()):
            with self.assertNumQueries(0, using="default"), self.assertNumQueries(1, using="secondary"):
                attempt = prepare_pessoa_photo(person, using="secondary")
        self.assertEqual(attempt.previous_db_key, "fotos_pessoas/secondary.gif")
        self.assertEqual(attempt.using, "secondary")
        for alias in self.databases:
            self.assertEqual(Pessoa.objects.using(alias).get(pk=7301).foto.name, f"fotos_pessoas/{alias}.gif")
