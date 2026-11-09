from unittest import skipUnless

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from configuracao.models import Igreja, Ministerio
from secretaria.models import GrupoCasa, Membro, Pessoa, StatusHistorico, StatusPessoa, TimelineEvent, TipoPessoa


HAS_SECONDARY = "secondary" in settings.DATABASES


@skipUnless(HAS_SECONDARY, "Use core.settings_test_multidb.")
class SecretariaSignalsMultiDBTests(TestCase):
    databases = {"default", "secondary"} if HAS_SECONDARY else {"default"}

    @classmethod
    def setUpTestData(cls):
        for alias in cls.databases:
            user = get_user_model().objects.db_manager(alias).create_user(username=alias)
            ministry, = Ministerio.objects.using(alias).bulk_create([
                Ministerio(nome_fantasia=alias, administrador_principal=user),
            ])
            church, = Igreja.objects.using(alias).bulk_create([
                Igreja(pk=7101, nome_igreja=alias, ministerio=ministry),
            ])
            TipoPessoa.objects.using(alias).bulk_create([
                TipoPessoa(pk=7101, nome="Membro"),
                TipoPessoa(pk=7102, nome=f"Congregado {alias}"),
            ])
            StatusPessoa.objects.using(alias).bulk_create([
                StatusPessoa(pk=7101, nome=f"Ativo {alias}"),
                StatusPessoa(pk=7102, nome=f"Inativo {alias}"),
            ])
            Pessoa.objects.using(alias).bulk_create([
                Pessoa(
                    pk=pk, nome=alias, igreja=church, tipo_pessoa_id=7101,
                    status_pessoa_id=7101, rua=f"Rua {alias}", numero_casa="12",
                )
                for pk in (7101, 7102)
            ])

    def test_existing_group_and_previous_address_with_coincident_primary_keys(self):
        GrupoCasa.objects.using("default").create(
            pk=7101, igreja_id=7101, rua="Rua secundária", numero="12",
        )
        group = GrupoCasa.objects.using("secondary").create(
            pk=7102, igreja_id=7101, rua="Rua secundária", numero="12",
        )
        member = Membro.objects.using("secondary").get(pk=7101)
        member.rua = "Rua secundária"
        with self.assertNumQueries(0, using="default"):
            member.save(using="secondary", update_fields=["rua"])
        self.assertEqual(member._prev_address["rua"], "Rua secondary")
        member.refresh_from_db(using="secondary")
        self.assertEqual(member.grupo_casa_id, group.pk)
        self.assertIsNone(Membro.objects.using("default").get(pk=7101).grupo_casa_id)

    def test_new_group_and_savepoint_are_on_secondary(self):
        member = Membro.objects.using("secondary").get(pk=7101)
        with self.assertNumQueries(0, using="default"), CaptureQueriesContext(connections["secondary"]) as queries:
            member.save(using="secondary", update_fields=["nome"])
        group = GrupoCasa.objects.using("secondary").get(igreja_id=7101)
        self.assertEqual(group.rua, "Rua secondary")
        self.assertEqual(
            list(Membro.objects.using("secondary").order_by("pk").values_list("grupo_casa_id", flat=True)),
            [group.pk, group.pk],
        )
        self.assertTrue(any(query["sql"].startswith("SAVEPOINT") for query in queries))
        self.assertFalse(GrupoCasa.objects.using("default").exists())
        self.assertFalse(Membro.objects.using("default").exclude(grupo_casa_id=None).exists())

    def test_entry_timeline_follows_sender_in_both_directions(self):
        for alias, other in (("secondary", "default"), ("default", "secondary")):
            with self.subTest(alias=alias):
                with self.assertNumQueries(0, using=other):
                    Membro.objects.using(alias).create(
                        pk=7103, nome=alias, igreja_id=7101,
                        tipo_pessoa_id=7101, status_pessoa_id=7101,
                    )
                event = TimelineEvent.objects.using(alias).get(membro_id=7103, tipo_evento="entrada")
                self.assertEqual(event.membro.nome, alias)

    def test_type_and_status_timeline_resolve_catalogs_and_write_on_secondary(self):
        with self.assertNumQueries(0, using="default"):
            StatusHistorico.objects.using("secondary").create(
                membro_id=7101, tipo_pessoa_anterior_id=7101, tipo_pessoa_novo_id=7102,
                status_pessoa_anterior_id=7101, status_pessoa_novo_id=7102,
                data_transicao=timezone.now(),
            )
        events = dict(TimelineEvent.objects.using("secondary").values_list("tipo_evento", "descricao"))
        self.assertEqual(set(events), {"mudanca_tipo", "mudanca_status"})
        self.assertIn("Congregado secondary", events["mudanca_tipo"])
        self.assertIn("Ativo secondary", events["mudanca_status"])
        self.assertIn("Inativo secondary", events["mudanca_status"])
        self.assertFalse(TimelineEvent.objects.using("default").exists())
