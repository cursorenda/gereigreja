import re
from datetime import date

from django.contrib.auth import get_user_model
from django.db import connection
from django.db.models import DEFERRED, ProtectedError
from django.db.models.deletion import Collector
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from configuracao.models import Igreja, Ministerio
from secretaria.models import Pessoa, StatusHistorico, StatusPessoa, TipoPessoa


class PessoaDeferredTests(TestCase):
    def test_save_rejeitado_preserva_distincao_entre_grau_nulo_e_deferred(self):
        Pessoa.objects.filter(pk=self.pessoa.pk).update(
            tipo_pessoa=self.outro_tipo, grau_eclesiastico=None,
        )
        for queryset, deferred, queries in (
            (Pessoa.objects.only("pk", "tipo_pessoa"), True, 1),
            (Pessoa.objects.all(), False, 0),
        ):
            with self.subTest(deferred=deferred):
                pessoa = queryset.select_related("tipo_pessoa").get(pk=self.pessoa.pk)
                self.assertEqual("grau_eclesiastico" in pessoa.get_deferred_fields(), deferred)
                count = self.historico().count()
                with self.assertNumQueries(queries), self.assertRaisesMessage(ValueError, "invalido"):
                    pessoa.save(update_fields=["tipo_pessoa", "invalido"])
                if deferred:
                    self.assertNotIn("grau_eclesiastico", pessoa.__dict__)
                else:
                    self.assertIsNone(pessoa.__dict__["grau_eclesiastico"])
                self.assertEqual(pessoa._original_tipo_pessoa_id, self.outro_tipo.pk)
                self.assertEqual(self.historico().count(), count)

                pessoa.save(update_fields=["tipo_pessoa"])
                persisted = Pessoa.objects.get(pk=pessoa.pk)
                self.assertEqual(persisted.tipo_pessoa_id, self.outro_tipo.pk)
                self.assertIsNone(persisted.grau_eclesiastico)
                self.assertEqual(pessoa._original_tipo_pessoa_id, self.outro_tipo.pk)
                self.assertEqual(self.historico().count(), count)

    def test_save_rejeitado_restaura_grau_e_permite_retry_na_mesma_instancia(self):
        for inverse, deferred in ((False, False), (True, False), (False, True)):
            with self.subTest(inverse=inverse, deferred=deferred):
                old, new = (self.outro_tipo, self.tipo) if inverse else (self.tipo, self.outro_tipo)
                before, after = (None, "membro_comum") if inverse else ("membro_comum", None)
                Pessoa.objects.filter(pk=self.pessoa.pk).update(tipo_pessoa=old, grau_eclesiastico=before)
                queryset = Pessoa.objects.only("pk") if deferred else Pessoa.objects.all()
                pessoa = queryset.get(pk=self.pessoa.pk)
                pessoa.tipo_pessoa = new
                fields = ["tipo_pessoa", "invalido"]
                count = self.historico().count()
                with self.assertRaisesMessage(ValueError, "invalido"):
                    pessoa.save(update_fields=fields)
                self.assertEqual(fields, ["tipo_pessoa", "invalido"])
                persisted = Pessoa.objects.get(pk=pessoa.pk)
                self.assertEqual((persisted.tipo_pessoa_id, persisted.grau_eclesiastico), (old.pk, before))
                self.assertEqual(pessoa.tipo_pessoa_id, new.pk)
                if deferred:
                    self.assertIn("grau_eclesiastico", pessoa.get_deferred_fields())
                    self.assertIs(pessoa._original_tipo_pessoa_id, DEFERRED)
                else:
                    self.assertEqual(pessoa.grau_eclesiastico, before)
                    self.assertEqual(pessoa._original_tipo_pessoa_id, old.pk)
                self.assertEqual(self.historico().count(), count)

                pessoa.save(update_fields=["tipo_pessoa"])
                persisted.refresh_from_db()
                self.assertEqual((persisted.tipo_pessoa_id, persisted.grau_eclesiastico), (new.pk, after))
                self.assertEqual(pessoa.grau_eclesiastico, after)
                self.assertEqual(pessoa._original_tipo_pessoa_id, new.pk)
                registro = self.historico().last()
                self.assertEqual((registro.tipo_pessoa_anterior_id, registro.tipo_pessoa_novo_id), (old.pk, new.pk))
                self.assertEqual(self.historico().count(), count + 1)
                pessoa.save()
                self.assertEqual(self.historico().count(), count + 1)

    def test_save_rejeitado_restaura_grau_atribuido_pelo_caller(self):
        pessoa = Pessoa.objects.get(pk=self.pessoa.pk)
        pessoa.tipo_pessoa = self.outro_tipo
        pessoa.grau_eclesiastico = "pastor"
        with CaptureQueriesContext(connection) as queries, self.assertRaisesMessage(ValueError, "invalido"):
            pessoa.save(update_fields=["tipo_pessoa", "grau_eclesiastico", "invalido"])
        statements = [query["sql"].strip().removesuffix(";") for query in queries]
        savepoint = r'(?:"[a-zA-Z0-9_]+"|[a-zA-Z0-9_]+)'
        transaction_control = re.compile(
            rf"(?:BEGIN(?: TRANSACTION)?|COMMIT|ROLLBACK|"
            rf"(?:SAVEPOINT|ROLLBACK TO(?: SAVEPOINT)?|RELEASE(?: SAVEPOINT)?) {savepoint})",
            re.IGNORECASE,
        )
        selects = [sql for sql in statements if re.match(r"SELECT\b", sql, re.IGNORECASE)]
        self.assertEqual(len(selects), 1, statements)
        self.assertEqual(
            [sql for sql in statements if sql not in selects and not transaction_control.fullmatch(sql)],
            [],
            statements,
        )
        self.assertEqual(pessoa.grau_eclesiastico, "pastor")
        self.assertEqual(Pessoa.objects.get(pk=pessoa.pk).grau_eclesiastico, "membro_comum")

    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user(username="pessoa_deferred_admin")
        ministerio = Ministerio.objects.create(
            nome_fantasia="Pessoa deferred", administrador_principal=user, ativo=True,
        )
        cls.igreja = Igreja.objects.create(nome_igreja="Congregação deferred", ministerio=ministerio)
        cls.tipo = TipoPessoa.objects.create(nome="Membro")
        cls.outro_tipo = TipoPessoa.objects.create(nome="Congregado")
        cls.status = StatusPessoa.objects.create(nome="Ativo")
        cls.outro_status = StatusPessoa.objects.create(nome="Inativo")
        cls.pessoa = Pessoa.objects.create(
            nome="Pessoa inicial", igreja=cls.igreja, tipo_pessoa=cls.tipo,
            status_pessoa=cls.status,
        )

    def historico(self):
        return StatusHistorico.objects.filter(membro=self.pessoa).order_by("pk")

    def test_only_pk_e_defer_explicito_carregam_em_uma_consulta(self):
        for queryset in (
            Pessoa.objects.only("pk"),
            Pessoa.objects.defer("tipo_pessoa", "status_pessoa"),
        ):
            with self.subTest(queryset=queryset.query):
                with self.assertNumQueries(1):
                    pessoa = queryset.get(pk=self.pessoa.pk)
                self.assertIs(pessoa._original_tipo_pessoa_id, DEFERRED)
                self.assertIs(pessoa._original_status_pessoa_id, DEFERRED)
                self.assertTrue(
                    {"tipo_pessoa_id", "status_pessoa_id"} <= pessoa.get_deferred_fields()
                )

    def test_delete_direto_queryset_e_collector_protegem_pessoa(self):
        for root, field in ((self.tipo, "tipo_pessoa_id"), (self.status, "status_pessoa_id")):
            queryset = type(root).objects.filter(pk=root.pk)
            collector = Collector(using=root._state.db)
            for delete in (root.delete, queryset.delete, lambda: collector.collect([root])):
                with self.subTest(field=field, delete=delete):
                    with self.assertRaises(ProtectedError) as caught:
                        delete()
                    self.assertIn(self.pessoa, caught.exception.protected_objects)
                    self.assertTrue(queryset.exists())
                    self.assertEqual(
                        Pessoa.objects.values_list(field, flat=True).get(pk=self.pessoa.pk),
                        root.pk,
                    )

    def test_save_de_outro_campo_sem_carregar_tipo_ou_status(self):
        for update in ({}, {"update_fields": ["nome"]}):
            with self.subTest(update=update):
                pessoa = Pessoa.objects.only("pk").get(pk=self.pessoa.pk)
                pessoa.nome = "Nome atualizado"
                with self.assertNumQueries(1):
                    pessoa.save(**update)
                self.assertTrue(
                    {"tipo_pessoa_id", "status_pessoa_id"} <= pessoa.get_deferred_fields()
                )
                self.pessoa.refresh_from_db()
                self.assertEqual(self.pessoa.nome, "Nome atualizado")
                self.assertEqual(self.pessoa.tipo_pessoa_id, self.tipo.pk)
                self.assertEqual(self.pessoa.status_pessoa_id, self.status.pk)
                self.assertEqual(self.historico().count(), 1)

    def test_update_fields_exclui_atribuicoes_ate_serem_salvas(self):
        pessoa = Pessoa.objects.only("pk").get(pk=self.pessoa.pk)
        pessoa.nome = "Nome atualizado"
        pessoa.tipo_pessoa = self.outro_tipo
        pessoa.status_pessoa = self.outro_status
        with self.assertNumQueries(1):
            pessoa.save(update_fields=["nome"])
        self.assertEqual(self.historico().count(), 1)
        pessoa.save(update_fields=["status_pessoa_id"])
        self.pessoa.refresh_from_db()
        self.assertEqual(self.pessoa.status_pessoa, self.outro_status)
        self.assertEqual(self.pessoa.tipo_pessoa, self.tipo)
        registro = self.historico().last()
        self.assertEqual(registro.status_pessoa_anterior, self.status)
        self.assertEqual(registro.status_pessoa_novo, self.outro_status)
        self.assertEqual(registro.tipo_pessoa_novo, self.tipo)
        self.assertEqual(self.historico().count(), 2)

    def test_atribuicao_do_mesmo_status_deferred_nao_gera_historico(self):
        pessoa = Pessoa.objects.only("pk").get(pk=self.pessoa.pk)
        pessoa.status_pessoa_id = self.status.pk
        pessoa.save()
        self.assertEqual(self.historico().count(), 1)

    def test_mudanca_real_de_status_deferred_gera_um_registro(self):
        pessoa = Pessoa.objects.only("pk").get(pk=self.pessoa.pk)
        pessoa.status_pessoa = self.outro_status
        pessoa.save(motivo_transicao="Teste", data_mudanca_status=date(2026, 1, 8))
        pessoa.save()
        self.assertEqual(self.historico().count(), 2)
        registro = self.historico().last()
        self.assertEqual(registro.status_pessoa_anterior, self.status)
        self.assertEqual(registro.status_pessoa_novo, self.outro_status)
        self.assertEqual(registro.data_transicao.date(), date(2026, 1, 8))
        self.assertIn("Motivo informado: Teste", registro.observacao)
        self.pessoa.refresh_from_db()
        self.assertEqual(self.pessoa.status_pessoa, self.outro_status)

    def test_mudanca_real_de_tipo_deferred_preserva_historico_e_grau(self):
        pessoa = Pessoa.objects.only("pk").get(pk=self.pessoa.pk)
        pessoa.tipo_pessoa_id = self.outro_tipo.pk
        pessoa.save()
        self.assertEqual(self.historico().count(), 2)
        registro = self.historico().last()
        self.assertEqual(registro.tipo_pessoa_anterior, self.tipo)
        self.assertEqual(registro.tipo_pessoa_novo, self.outro_tipo)
        self.pessoa.refresh_from_db()
        self.assertEqual(self.pessoa.tipo_pessoa, self.outro_tipo)
        self.assertIsNone(self.pessoa.grau_eclesiastico)

    def test_refresh_de_status_e_refresh_completo_nao_inventam_transicao(self):
        pessoa = Pessoa.objects.only("pk").get(pk=self.pessoa.pk)
        Pessoa.objects.filter(pk=pessoa.pk).update(status_pessoa=self.outro_status)
        pessoa.refresh_from_db(fields=["status_pessoa"])
        pessoa.refresh_from_db()
        pessoa.save(update_fields=["status_pessoa"])
        self.assertEqual(pessoa.status_pessoa, self.outro_status)
        self.assertEqual(self.historico().count(), 1)

    def test_criacao_e_mudanca_com_instancia_completa(self):
        inicial = self.historico().get()
        self.assertIsNone(inicial.tipo_pessoa_anterior)
        self.assertIsNone(inicial.status_pessoa_anterior)
        self.assertEqual(inicial.tipo_pessoa_novo, self.tipo)
        self.assertEqual(inicial.status_pessoa_novo, self.status)
        pessoa = Pessoa.objects.get(pk=self.pessoa.pk)
        self.assertEqual(pessoa.grau_eclesiastico, "membro_comum")
        pessoa.tipo_pessoa = self.outro_tipo
        pessoa.status_pessoa = self.outro_status
        pessoa.save()
        self.assertEqual(self.historico().count(), 2)
        registro = self.historico().last()
        self.assertEqual(registro.tipo_pessoa_anterior, self.tipo)
        self.assertEqual(registro.tipo_pessoa_novo, self.outro_tipo)
        self.assertEqual(registro.status_pessoa_anterior, self.status)
        self.assertEqual(registro.status_pessoa_novo, self.outro_status)
        self.assertIsNone(pessoa.grau_eclesiastico)

    def test_instancia_completa_preserva_mudanca_excluida_para_o_proximo_save(self):
        for field, original, replacement in (
            ("status_pessoa", self.status, self.outro_status),
            ("tipo_pessoa", self.tipo, self.outro_tipo),
        ):
            with self.subTest(field=field):
                pessoa = Pessoa.objects.get(pk=self.pessoa.pk)
                attname = f"{field}_id"
                snapshot = f"_original_{attname}"
                setattr(pessoa, field, replacement)
                pessoa.nome = "Novo nome"
                count = self.historico().count()
                with self.assertNumQueries(1):
                    pessoa.save(update_fields=["nome"])
                self.assertEqual(getattr(Pessoa.objects.get(pk=pessoa.pk), attname), original.pk)
                self.assertEqual(getattr(pessoa, attname), replacement.pk)
                self.assertEqual(getattr(pessoa, snapshot), original.pk)
                self.assertEqual(pessoa.grau_eclesiastico, "membro_comum")
                self.assertEqual(
                    Pessoa.objects.get(pk=pessoa.pk).grau_eclesiastico, "membro_comum",
                )
                self.assertEqual(self.historico().count(), count)

                pessoa.save()
                self.assertEqual(getattr(Pessoa.objects.get(pk=pessoa.pk), attname), replacement.pk)
                self.assertEqual(getattr(pessoa, snapshot), replacement.pk)
                if field == "tipo_pessoa":
                    self.assertIsNone(Pessoa.objects.get(pk=pessoa.pk).grau_eclesiastico)
                registro = self.historico().last()
                self.assertEqual(getattr(registro, f"{field}_anterior_id"), original.pk)
                self.assertEqual(getattr(registro, f"{field}_novo_id"), replacement.pk)
                pessoa.save()
                self.assertEqual(self.historico().count(), count + 1)

    def test_update_fields_com_tipo_status_ou_ambos(self):
        for fields, partial in (
            (["tipo_pessoa"], False),
            (["tipo_pessoa", "grau_eclesiastico"], False),
            (["tipo_pessoa_id"], True),
            (["status_pessoa"], False),
            (["tipo_pessoa_id", "status_pessoa"], True),
        ):
            with self.subTest(fields=fields, partial=partial):
                Pessoa.objects.filter(pk=self.pessoa.pk).update(
                    tipo_pessoa=self.tipo, status_pessoa=self.status,
                    grau_eclesiastico="membro_comum",
                )
                queryset = Pessoa.objects.only("pk") if partial else Pessoa.objects.all()
                pessoa = queryset.get(pk=self.pessoa.pk)
                pessoa.tipo_pessoa = self.outro_tipo
                pessoa.status_pessoa = self.outro_status
                count = self.historico().count()
                pessoa.save(update_fields=fields)
                persisted = Pessoa.objects.get(pk=pessoa.pk)
                registro = self.historico().last()
                for field, original, replacement in (
                    ("tipo_pessoa", self.tipo, self.outro_tipo),
                    ("status_pessoa", self.status, self.outro_status),
                ):
                    attname = f"{field}_id"
                    included = field in fields or attname in fields
                    expected = replacement.pk if included else original.pk
                    self.assertEqual(getattr(persisted, attname), expected)
                    expected_snapshot = DEFERRED if partial and not included else expected
                    self.assertEqual(getattr(pessoa, f"_original_{attname}"), expected_snapshot)
                    self.assertEqual(getattr(registro, f"{field}_novo_id"), expected)
                    self.assertEqual(
                        getattr(registro, f"{field}_anterior_id"), original.pk if included else None,
                    )
                if "tipo_pessoa" in fields or "tipo_pessoa_id" in fields:
                    self.assertIsNone(pessoa.grau_eclesiastico)
                    self.assertIsNone(persisted.grau_eclesiastico)
                if fields == ["tipo_pessoa"]:
                    self.assertEqual(fields, ["tipo_pessoa"])
                    pessoa.status_pessoa = self.status
                    pessoa.save()
                else:
                    pessoa.save(update_fields=fields)
                self.assertEqual(self.historico().count(), count + 1)

    def test_tipo_membro_persiste_grau_padrao_na_mesma_gravacao(self):
        Pessoa.objects.filter(pk=self.pessoa.pk).update(
            tipo_pessoa=self.outro_tipo, grau_eclesiastico=None,
        )
        pessoa = Pessoa.objects.get(pk=self.pessoa.pk)
        pessoa.tipo_pessoa = self.tipo
        fields = ["tipo_pessoa"]
        pessoa.save(update_fields=fields)
        self.assertEqual(fields, ["tipo_pessoa"])
        persisted = Pessoa.objects.get(pk=pessoa.pk)
        self.assertEqual(persisted.tipo_pessoa_id, self.tipo.pk)
        self.assertEqual(pessoa.grau_eclesiastico, "membro_comum")
        self.assertEqual(persisted.grau_eclesiastico, "membro_comum")
        self.assertEqual(self.historico().count(), 2)

    def test_grau_inalterado_pela_regra_nao_e_incluido_na_gravacao(self):
        pessoa = Pessoa.objects.get(pk=self.pessoa.pk)
        pessoa.grau_eclesiastico = "pastor"
        pessoa.save(update_fields=["tipo_pessoa"])
        self.assertEqual(pessoa.grau_eclesiastico, "pastor")
        self.assertEqual(Pessoa.objects.get(pk=pessoa.pk).grau_eclesiastico, "membro_comum")
        self.assertEqual(self.historico().count(), 1)

    def test_refresh_sincroniza_somente_campos_recarregados(self):
        for fields in (["status_pessoa"], ["tipo_pessoa_id"], None):
            with self.subTest(fields=fields):
                Pessoa.objects.filter(pk=self.pessoa.pk).update(
                    tipo_pessoa=self.tipo, status_pessoa=self.status,
                )
                pessoa = Pessoa.objects.get(pk=self.pessoa.pk)
                update = {}
                if fields is None or "tipo_pessoa_id" in fields:
                    update["tipo_pessoa_id"] = self.outro_tipo.pk
                if fields is None or "status_pessoa" in fields:
                    update["status_pessoa_id"] = self.outro_status.pk
                Pessoa.objects.filter(pk=pessoa.pk).update(**update)
                pessoa.refresh_from_db(fields=fields)
                self.assertEqual(
                    pessoa._original_tipo_pessoa_id, update.get("tipo_pessoa_id", self.tipo.pk),
                )
                self.assertEqual(
                    pessoa._original_status_pessoa_id, update.get("status_pessoa_id", self.status.pk),
                )
                count = self.historico().count()
                pessoa.save()
                self.assertEqual(self.historico().count(), count)

    def test_refresh_de_nome_preserva_mudancas_em_memoria(self):
        pessoa = Pessoa.objects.get(pk=self.pessoa.pk)
        pessoa.tipo_pessoa = self.outro_tipo
        pessoa.status_pessoa = self.outro_status
        pessoa.refresh_from_db(fields=["nome"])
        pessoa.refresh_from_db(from_queryset=Pessoa.objects.only("nome"))
        self.assertEqual(pessoa.tipo_pessoa_id, self.outro_tipo.pk)
        self.assertEqual(pessoa.status_pessoa_id, self.outro_status.pk)
        self.assertEqual(pessoa._original_tipo_pessoa_id, self.tipo.pk)
        self.assertEqual(pessoa._original_status_pessoa_id, self.status.pk)
        pessoa.save()
        self.assertEqual(self.historico().count(), 2)

    def test_tipo_entrada_excluido_preserva_snapshot_inclusive_quando_nulo(self):
        pessoa = Pessoa.objects.get(pk=self.pessoa.pk)
        pessoa.save()
        self.assertIsNone(pessoa._original_tipo_entrada)
        pessoa.tipo_entrada = "BATISMO"
        pessoa.save(update_fields=["nome"])
        self.assertIsNone(pessoa._original_tipo_entrada)
        self.assertEqual(self.historico().count(), 1)
        pessoa.save(update_fields=["tipo_entrada"])
        self.assertEqual(pessoa._original_tipo_entrada, "BATISMO")
        self.assertIn("Tipo de entrada alterado", self.historico().last().observacao)
        self.assertEqual(self.historico().count(), 2)
