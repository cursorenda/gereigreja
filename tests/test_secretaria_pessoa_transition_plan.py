from django.contrib.auth import get_user_model
from django.db.models import DEFERRED
from django.test import TestCase

from configuracao.models import Igreja, Ministerio
from secretaria.models import Pessoa, StatusHistorico, StatusPessoa, TipoPessoa


class PessoaTransitionPlanTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user(username="pessoa_plan")
        ministry = Ministerio.objects.create(
            nome_fantasia="Plano", administrador_principal=user,
        )
        cls.church = Igreja.objects.create(nome_igreja="Congregação plano", ministerio=ministry)
        cls.member = TipoPessoa.objects.create(nome="Membro")
        cls.congregant = TipoPessoa.objects.create(nome="Congregado")
        cls.active = StatusPessoa.objects.create(nome="Ativo")
        cls.inactive = StatusPessoa.objects.create(nome="Inativo")

    def create_person(self):
        return Pessoa.objects.create(
            nome="Pessoa plano", igreja=self.church,
            tipo_pessoa=self.member, status_pessoa=self.active,
        )

    def test_creation_and_combined_transition_have_one_history_each(self):
        person = self.create_person()
        history = StatusHistorico.objects.filter(membro=person).order_by("pk")
        initial = history.get()
        self.assertIsNone(initial.tipo_pessoa_anterior_id)
        self.assertIsNone(initial.status_pessoa_anterior_id)
        self.assertEqual(initial.tipo_pessoa_novo_id, self.member.pk)
        self.assertEqual(initial.status_pessoa_novo_id, self.active.pk)
        self.assertEqual(person._original_tipo_pessoa_id, self.member.pk)
        self.assertEqual(person._original_status_pessoa_id, self.active.pk)
        self.assertEqual(person.grau_eclesiastico, "membro_comum")

        person.tipo_pessoa = self.congregant
        person.status_pessoa = self.inactive
        person.save(update_fields=["tipo_pessoa", "status_pessoa"], motivo_transicao="Teste")
        self.assertEqual(history.count(), 2)
        transition = history.last()
        self.assertEqual(transition.tipo_pessoa_anterior_id, self.member.pk)
        self.assertEqual(transition.tipo_pessoa_novo_id, self.congregant.pk)
        self.assertEqual(transition.status_pessoa_anterior_id, self.active.pk)
        self.assertEqual(transition.status_pessoa_novo_id, self.inactive.pk)
        self.assertIn("Motivo informado: Teste", transition.observacao)
        self.assertIsNone(Pessoa.objects.get(pk=person.pk).grau_eclesiastico)

    def test_plan_reads_deferred_original_without_writing_or_advancing_snapshots(self):
        original = self.create_person()
        person = Pessoa.objects.only("pk").get(pk=original.pk)
        person.tipo_pessoa = self.congregant
        fields = ["tipo_pessoa_id"]
        state = dict(person.__dict__)
        cache = dict(person._state.fields_cache)
        deferred = person.get_deferred_fields()
        with self.assertNumQueries(2):
            plan = person._build_mutation_plan(person._state.db, fields)
        with self.assertNumQueries(2):
            repeated = person._build_mutation_plan(person._state.db, fields)
        self.assertEqual(plan, repeated)
        self.assertEqual(person.__dict__, state)
        self.assertEqual(person._state.fields_cache, cache)
        self.assertIs(person._state.fields_cache["tipo_pessoa"], self.congregant)
        self.assertEqual(person.get_deferred_fields(), deferred)
        self.assertEqual(fields, ["tipo_pessoa_id"])
        self.assertTrue(plan.history_required)
        self.assertTrue(plan.changed_tipo)
        self.assertFalse(plan.status_written)
        self.assertEqual(plan.tipo_anterior_obj.pk, self.member.pk)
        self.assertEqual(plan.update_fields, {"tipo_pessoa_id", "grau_eclesiastico"})
        self.assertIs(plan.grau_na_entrada, DEFERRED)
        self.assertIsNone(plan.grau_derivado)
        self.assertIs(person._original_tipo_pessoa_id, DEFERRED)
        self.assertEqual(Pessoa.objects.get(pk=person.pk).tipo_pessoa_id, self.member.pk)
        self.assertEqual(StatusHistorico.objects.filter(membro=person).count(), 1)

    def test_deferred_grade_and_uncached_type_are_observed_without_loading(self):
        original = self.create_person()
        for old, grade, target, derived in (
            (self.congregant, None, self.member, "membro_comum"),
            (self.congregant, None, TipoPessoa.objects.create(nome="Visitante"), None),
            (self.member, "pastor", self.member, "pastor"),
        ):
            with self.subTest(target=target.nome, grade=grade):
                Pessoa.objects.filter(pk=original.pk).update(tipo_pessoa=old, grau_eclesiastico=grade)
                person = Pessoa.objects.only("pk", "tipo_pessoa").get(pk=original.pk)
                person.tipo_pessoa_id = target.pk
                state = dict(person.__dict__)
                self.assertEqual(person._state.fields_cache, {})
                first = person._build_mutation_plan(person._state.db, ["tipo_pessoa"])
                second = person._build_mutation_plan(person._state.db, ["tipo_pessoa"])
                self.assertEqual(first, second)
                self.assertIs(first.grau_na_entrada, DEFERRED)
                self.assertEqual(first.grau_derivado, derived)
                self.assertEqual("grau_eclesiastico" in first.update_fields, grade != derived)
                self.assertEqual(person.__dict__, state)
                self.assertEqual(person._state.fields_cache, {})
                self.assertIn("grau_eclesiastico", person.get_deferred_fields())

    def test_entry_transition_uses_established_snapshot_and_excludes_pending_status(self):
        person = self.create_person()
        person.tipo_entrada = "BATISMO"
        person.status_pessoa = self.inactive
        person.save(update_fields=["tipo_entrada"])
        history = StatusHistorico.objects.filter(membro=person).order_by("pk")
        self.assertEqual(history.count(), 2)
        self.assertIn("Tipo de entrada alterado", history.last().observacao)
        self.assertEqual(history.last().status_pessoa_novo_id, self.active.pk)
        self.assertEqual(person._original_status_pessoa_id, self.active.pk)
        self.assertEqual(person._original_tipo_entrada, "BATISMO")
        person.save(update_fields=["status_pessoa"])
        self.assertEqual(history.count(), 3)
        self.assertEqual(history.last().status_pessoa_anterior_id, self.active.pk)
        self.assertEqual(history.last().status_pessoa_novo_id, self.inactive.pk)
