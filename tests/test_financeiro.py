import ast
from datetime import date, datetime, timedelta
from decimal import Decimal
import importlib
import inspect
import json
import textwrap
from types import SimpleNamespace
from unittest import skipUnless
from unittest.mock import MagicMock, call, patch
from uuid import uuid4

from django.conf import settings as django_settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from contas.constants import ADMIN_MINISTERIO, PASTOR_LOCAL, PASTOR_REGIONAL, TESOUREIRO
from configuracao.models import Departamento, DepartamentoCapacidade, Igreja, Ministerio, PerfilUsuario, Plano
from configuracao.models import Ministerio as CurrentMinisterio
from eventos.models import Evento
from financeiro.models import (
    CategoriaDespesa,
    ContaBancaria,
    ContaPagar,
    DepartamentoCaixa,
    DepartamentoFinanceiro,
    Despesas,
    FechamentoCaixa,
    Fornecedor,
    FundoDepartamental,
    ImportacaoExtratoOFX,
    LancamentoExtratoOFX,
    LogTransacaoFinanceira,
    ContaPagarAutorizacaoEvento,
    PoliticaFinanceiraIgreja,
    PoliticaDepartamentoFinanceiro,
    PermissaoCaixa,
    RecorrenciaContaPagar,
    Receitas,
    TransferenciaCaixa,
)
from financeiro.forms import ContaPagarForm, RecorrenciaContaPagarForm
from financeiro.forms import ContaBancariaForm, DespesaForm, ReceitaForm, TransferenciaCaixaForm
from financeiro.services import (
    _create_payable_authorization_event,
    _materialize_payable_edit_authorization_events,
    AlertaVencimentoContaPagarService,
    build_payable_material_snapshot_v1,
    build_payable_authorization_edit_snapshot,
    compute_payable_material_fingerprint_v1,
    plan_payable_authorization_after_edit,
    apply_payable_authorization_edit_plan,
    create_payable,
    approve_payable,
    reject_payable,
    refresh_payable_material_fingerprint,
    FechamentoCaixaService,
    OFXImportService,
    DepartamentoFinanceiroService,
    ReceitaFluxoService,
    RecorrenciaContaPagarService,
)
from financeiro.policies import (
    categorias_despesa_padrao_eventos,
    categoria_receita_padrao_por_fundo,
    categorias_receita_permitidas_por_fundo,
)
from notificacoes.models import Notificacao
from financeiro.views import (
    criar_recorrencia_conta_pagar,
    editar_recorrencia_conta_pagar,
    gerar_despesas_fixas_mes,
    lista_despesas,
    lista_receitas,
)
import financeiro.views as financeiro_views
from financeiro.authorization import can_approve_payable, get_finance_approval_scope, get_finance_write_scope
from financeiro.utils import get_allowed_churches_for_user


class BaseFinanceiroTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tesoureiro_financeiro_test",
            email="tesoureiro_financeiro_test@example.com",
            password="senha123",
        )

        self.ministerio = Ministerio.objects.create(
            nome_fantasia="Ministerio Financeiro Teste",
            administrador_principal=self.user,
            ativo=True,
            cnpj="12345678000199",
        )

        self.igreja = Igreja.objects.create(
            nome_igreja="Igreja Financeiro Teste",
            ministerio=self.ministerio,
            tipo_igreja="sede",
        )


class DespesaCriadorModelTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Criador Despesa',
        )

    def test_despesa_persiste_criador(self):
        despesa = Despesas.objects.create(
            igreja=self.igreja,
            categoria=self.categoria,
            data=date(2026, 10, 15),
            descricao='Despesa com criador',
            valor=Decimal('10.00'),
            criado_por=self.user,
        )

        despesa.refresh_from_db()

        self.assertEqual(despesa.criado_por, self.user)

    def test_despesa_historica_aceita_criador_nulo(self):
        despesa = Despesas.objects.create(
            igreja=self.igreja,
            categoria=self.categoria,
            data=date(2026, 10, 15),
            descricao='Despesa historica sem criador conhecido',
            valor=Decimal('10.00'),
            criado_por=None,
        )

        despesa.refresh_from_db()

        self.assertIsNone(despesa.criado_por)


class PoliticaFinanceiraIgrejaModelTest(BaseFinanceiroTestCase):
    def test_one_to_one_defaults_and_valid_combinations(self):
        politica = PoliticaFinanceiraIgreja.objects.get(igreja=self.igreja)

        self.assertEqual(politica.igreja, self.igreja)
        self.assertFalse(politica.approval_required)
        self.assertEqual(politica.segregation_level, PoliticaFinanceiraIgreja.LEVEL_1_SIMPLE)
        self.assertEqual(politica.version, 1)
        self.assertEqual(PoliticaFinanceiraIgreja.objects.filter(igreja=self.igreja).count(), 1)

        for indice, approval_required, segregation_level in (
            (1, False, PoliticaFinanceiraIgreja.LEVEL_1_SIMPLE),
            (2, True, PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED),
            (3, True, PoliticaFinanceiraIgreja.LEVEL_3_STRONG),
        ):
            igreja = Igreja.objects.create(
                ministerio=self.ministerio,
                nome_igreja=f'Igreja Politica Valida {indice}',
                tipo_igreja='congregacao',
            )
            politica = PoliticaFinanceiraIgreja.objects.get(igreja=igreja)
            politica.approval_required = approval_required
            politica.segregation_level = segregation_level
            politica.full_clean()

    def test_clean_rejects_incoherent_approval_mode(self):
        for indice, approval_required, segregation_level in (
            (1, False, PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED),
            (2, True, PoliticaFinanceiraIgreja.LEVEL_1_SIMPLE),
        ):
            igreja = Igreja.objects.create(
                ministerio=self.ministerio,
                nome_igreja=f'Igreja Politica Invalida {indice}',
                tipo_igreja='congregacao',
            )
            politica = PoliticaFinanceiraIgreja.objects.get(igreja=igreja)
            politica.approval_required = approval_required
            politica.segregation_level = segregation_level
            with self.assertRaises(ValidationError):
                politica.full_clean()


class PoliticaFinanceiraIgrejaProvisioningSignalTest(BaseFinanceiroTestCase):
    def test_new_church_receives_exact_default_policy_once(self):
        igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja com Politica Provisionada',
            tipo_igreja='congregacao',
        )

        politica = PoliticaFinanceiraIgreja.objects.get(igreja=igreja)

        self.assertFalse(politica.approval_required)
        self.assertEqual(politica.segregation_level, PoliticaFinanceiraIgreja.LEVEL_1_SIMPLE)
        self.assertEqual(politica.version, 1)
        self.assertEqual(PoliticaFinanceiraIgreja.objects.filter(igreja=igreja).count(), 1)

    def test_repeated_church_saves_keep_a_single_policy(self):
        igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja com Signal Idempotente',
            tipo_igreja='congregacao',
        )

        igreja.save()
        igreja.save()

        self.assertEqual(PoliticaFinanceiraIgreja.objects.filter(igreja=igreja).count(), 1)

    def test_existing_church_save_does_not_introspect_schema(self):
        igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja sem Introspeccao em Update',
            tipo_igreja='congregacao',
        )

        with patch('financeiro.signals.connection.introspection.table_names') as table_names:
            igreja.save()

        table_names.assert_not_called()

    def test_repeated_church_saves_preserve_configured_policy(self):
        igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja com Politica Configurada',
            tipo_igreja='congregacao',
        )
        PoliticaFinanceiraIgreja.objects.filter(igreja=igreja).update(
            approval_required=True,
            segregation_level=PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED,
            version=9,
        )

        igreja.save()
        igreja.save()

        politica = PoliticaFinanceiraIgreja.objects.get(igreja=igreja)
        self.assertTrue(politica.approval_required)
        self.assertEqual(politica.segregation_level, PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED)
        self.assertEqual(politica.version, 9)
        self.assertEqual(PoliticaFinanceiraIgreja.objects.filter(igreja=igreja).count(), 1)


class ContaPagarPrePaymentAuthorizationExpansiveSchemaTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Schema Expansivo',
        )

    def test_direct_creation_keeps_transitional_authorization_fields_null(self):
        conta = ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            descricao='Conta direta transitoria',
            valor=Decimal('15.00'),
            data_emissao=date(2026, 10, 13),
            data_vencimento=date(2026, 10, 20),
        )

        self.assertIsNone(conta.authorization_status)
        self.assertIsNone(conta.authorization_origin)
        self.assertIsNone(conta.authorization_policy_version)
        self.assertIsNone(conta.current_material_fingerprint)
        self.assertFalse(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta).exists())
        self.assertTrue(ContaPagar._meta.get_field('authorization_status').null)
        self.assertFalse(ContaPagar._meta.get_field('authorization_status').has_default())
        self.assertTrue(ContaPagar._meta.get_field('authorization_origin').null)
        self.assertFalse(ContaPagar._meta.get_field('authorization_origin').has_default())


class ContaPagarCreationAuthorizationServiceTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Service Authorization',
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Service Authorization',
        )

    def _create_payable(self, **overrides):
        payload = {
            'ministerio': self.ministerio,
            'igreja': self.igreja,
            'fornecedor': self.fornecedor,
            'categoria': self.categoria,
            'descricao': 'Conta de servico',
            'valor': Decimal('10.00'),
            'data_emissao': date(2026, 10, 13),
            'data_vencimento': date(2026, 10, 20),
            'usuario_criacao': self.user,
        }
        payload.update(overrides)
        return create_payable(**payload)

    def _create_other_ministry_context(self):
        other_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministerio Service Authorization',
            administrador_principal=self.user,
            ativo=True,
            cnpj='98765432000199',
        )
        other_igreja = Igreja.objects.create(
            nome_igreja='Outra Igreja Service Authorization',
            ministerio=other_ministerio,
            tipo_igreja='sede',
        )
        other_fornecedor = Fornecedor.objects.create(
            ministerio=other_ministerio,
            nome='Outro Fornecedor Service Authorization',
        )
        other_categoria = CategoriaDespesa.objects.create(
            ministerio=other_ministerio,
            nome='Outra Categoria Service Authorization',
        )
        other_conta_debito = ContaBancaria.objects.create(
            igreja=other_igreja,
            nome_identificacao='Outra Conta Service Authorization',
            tipo='caixa_fisico',
        )
        other_recorrencia = RecorrenciaContaPagar.objects.create(
            ministerio=other_ministerio,
            igreja=other_igreja,
            fornecedor=other_fornecedor,
            categoria=other_categoria,
            descricao='Outra recorrencia Service Authorization',
            valor=Decimal('10.00'),
            dia_vencimento=10,
        )
        return {
            'ministerio': other_ministerio,
            'igreja': other_igreja,
            'fornecedor': other_fornecedor,
            'categoria': other_categoria,
            'conta_debito': other_conta_debito,
            'recorrencia': other_recorrencia,
        }

    def _assert_domain_integrity_failure(self, **overrides):
        with self.assertRaises(ValidationError):
            self._create_payable(**overrides)

        self.assertEqual(ContaPagar.objects.count(), 0)
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.count(), 0)

    def test_rejects_church_from_other_ministry_before_persisting(self):
        other = self._create_other_ministry_context()

        self._assert_domain_integrity_failure(igreja=other['igreja'])

    def test_rejects_supplier_from_other_ministry_before_persisting(self):
        other = self._create_other_ministry_context()

        self._assert_domain_integrity_failure(fornecedor=other['fornecedor'])

    def test_rejects_category_from_other_ministry_before_persisting(self):
        other = self._create_other_ministry_context()

        self._assert_domain_integrity_failure(categoria=other['categoria'])

    def test_rejects_debit_account_from_other_church_before_persisting(self):
        other = self._create_other_ministry_context()

        self._assert_domain_integrity_failure(conta_debito=other['conta_debito'])

    def test_rejects_recurrence_from_other_context_before_persisting(self):
        other = self._create_other_ministry_context()

        self._assert_domain_integrity_failure(
            recorrencia_origem=other['recorrencia'],
            competencia='2026-10',
            criado_automaticamente=True,
        )

    def test_creates_payable_with_coherent_debit_account_and_recurrence(self):
        conta_debito = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Conta Coerente Service Authorization',
            tipo='caixa_fisico',
        )
        recorrencia = RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Recorrencia Coerente Service Authorization',
            valor=Decimal('10.00'),
            dia_vencimento=10,
        )

        payable = self._create_payable(
            conta_debito=conta_debito,
            recorrencia_origem=recorrencia,
            competencia='2026-10',
            criado_automaticamente=True,
        )

        self.assertEqual(payable.conta_debito, conta_debito)
        self.assertEqual(payable.recorrencia_origem, recorrencia)
        self.assertTrue(payable.criado_automaticamente)
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=payable).count(), 1)

    def test_fingerprint_v1_golden_vectors_are_canonical_and_case_preserving(self):
        vector = SimpleNamespace(
            igreja_id=7,
            fornecedor_id=11,
            valor=Decimal('10.005'),
            data_vencimento=date(2026, 1, 2),
            descricao='  Cafe\r\nCom\rLeite  ',
        )
        expected_snapshot = {
            'fingerprint_schema_version': 1,
            'igreja_id': 7,
            'fornecedor_id': 11,
            'valor': '10.01',
            'data_vencimento': '2026-01-02',
            'descricao': 'Cafe\nCom\nLeite',
        }
        expected_json = (
            '{"data_vencimento":"2026-01-02","descricao":"Cafe\\nCom\\nLeite",'
            '"fingerprint_schema_version":1,"fornecedor_id":11,"igreja_id":7,"valor":"10.01"}'
        )
        expected_fingerprint = 'v1:sha256:ea31b5d371e2b7974562211a4945f2572791d6b6d3a8ca104954610d98f774cd'

        snapshot = build_payable_material_snapshot_v1(vector)

        self.assertEqual(snapshot, expected_snapshot)
        self.assertEqual(
            json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(',', ':')),
            expected_json,
        )
        self.assertEqual(compute_payable_material_fingerprint_v1(snapshot), expected_fingerprint)
        second_vector = SimpleNamespace(
            igreja_id=7,
            fornecedor_id=11,
            valor=Decimal('10'),
            data_vencimento=date(2026, 1, 2),
            descricao='  CaFe\r\nCafe\u0301  ',
        )
        second_expected_snapshot = {
            'fingerprint_schema_version': 1,
            'igreja_id': 7,
            'fornecedor_id': 11,
            'valor': '10.00',
            'data_vencimento': '2026-01-02',
            'descricao': 'CaFe\nCafé',
        }
        second_expected_json = (
            '{"data_vencimento":"2026-01-02","descricao":"CaFe\\nCafé",'
            '"fingerprint_schema_version":1,"fornecedor_id":11,"igreja_id":7,"valor":"10.00"}'
        )
        second_expected_fingerprint = 'v1:sha256:c5787373b3c805483cf025fc3d09fb8c7fa9a5e71ac19b1b66ce19e2dfd05268'

        second_snapshot = build_payable_material_snapshot_v1(second_vector)
        self.assertEqual(second_snapshot, second_expected_snapshot)
        self.assertEqual(
            json.dumps(second_snapshot, ensure_ascii=False, sort_keys=True, separators=(',', ':')),
            second_expected_json,
        )
        self.assertEqual(
            compute_payable_material_fingerprint_v1(second_snapshot),
            second_expected_fingerprint,
        )

    def test_runtime_fingerprint_is_byte_compatible_with_migration_0020(self):
        migration_module = importlib.import_module(
            'financeiro.migrations.0020_prepayment_authorization_expansive',
        )
        payable = SimpleNamespace(
            igreja_id=17,
            fornecedor_id=23,
            valor=Decimal('10.005'),
            data_vencimento=date(2026, 2, 3),
            descricao='  Café\r\nConta  ',
        )

        snapshot = build_payable_material_snapshot_v1(payable)

        self.assertEqual(snapshot, migration_module._material_snapshot(payable))
        self.assertEqual(
            compute_payable_material_fingerprint_v1(snapshot),
            migration_module._material_fingerprint(migration_module._material_snapshot(payable)),
        )

    def test_simple_policy_creates_not_required_payable_and_created_event_without_actor(self):
        payable = self._create_payable(actor=None)

        policy = PoliticaFinanceiraIgreja.objects.get(igreja=self.igreja)
        event = ContaPagarAutorizacaoEvento.objects.get(conta_pagar=payable)
        snapshot = build_payable_material_snapshot_v1(payable)
        self.assertEqual(payable.status, 'PEN')
        self.assertEqual(payable.authorization_status, ContaPagar.AUTHORIZATION_NOT_REQUIRED)
        self.assertEqual(payable.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED)
        self.assertEqual(payable.authorization_policy_version, policy.version)
        self.assertEqual(payable.current_material_fingerprint, compute_payable_material_fingerprint_v1(snapshot))
        self.assertIsNone(payable.approved_material_fingerprint)
        self.assertIsNone(payable.approved_by)
        self.assertIsNone(payable.approved_at)
        self.assertIsNone(payable.rejected_by)
        self.assertIsNone(payable.rejected_at)
        self.assertIsNone(payable.current_rejection_reason)
        self.assertEqual(event.event_type, ContaPagarAutorizacaoEvento.EVENT_CREATED)
        self.assertIsNone(event.actor)
        self.assertIsNone(event.actor_user_id_snapshot)
        self.assertIsNone(event.actor_display_name_snapshot)
        self.assertIsNone(event.authorization_status_before)
        self.assertEqual(event.authorization_status_after, ContaPagar.AUTHORIZATION_NOT_REQUIRED)
        self.assertIsNone(event.financial_status_before)
        self.assertEqual(event.financial_status_after, 'PEN')
        self.assertEqual(event.material_fingerprint, payable.current_material_fingerprint)
        self.assertEqual(event.material_snapshot, snapshot)
        self.assertEqual(event.policy_snapshot, {
            'policy_id': policy.pk,
            'policy_version': policy.version,
            'approval_required': False,
            'segregation_level': PoliticaFinanceiraIgreja.LEVEL_1_SIMPLE,
        })
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=payable).count(), 1)

    def test_configured_policy_is_preserved_and_creates_pending_payable_with_actor_snapshot(self):
        policy = PoliticaFinanceiraIgreja.objects.get(igreja=self.igreja)
        policy.approval_required = True
        policy.segregation_level = PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED
        policy.version = 9
        policy.save()
        self.user.first_name = 'Ator'
        self.user.last_name = 'Real'
        self.user.save(update_fields=['first_name', 'last_name'])

        payable = self._create_payable(actor=self.user)

        policy.refresh_from_db()
        event = ContaPagarAutorizacaoEvento.objects.get(conta_pagar=payable)
        self.assertTrue(policy.approval_required)
        self.assertEqual(policy.segregation_level, PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED)
        self.assertEqual(policy.version, 9)
        self.assertEqual(payable.authorization_status, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(payable.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED)
        self.assertEqual(payable.authorization_policy_version, 9)
        self.assertEqual(event.actor, self.user)
        self.assertEqual(event.actor_user_id_snapshot, self.user.pk)
        self.assertEqual(event.actor_display_name_snapshot, 'Ator Real')
        self.assertEqual(event.policy_snapshot['policy_id'], policy.pk)
        self.assertEqual(event.policy_snapshot['policy_version'], 9)
        self.assertTrue(event.policy_snapshot['approval_required'])
        self.assertEqual(event.policy_snapshot['segregation_level'], PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED)

    def test_missing_policy_is_recovered_with_default_and_classifies_payable(self):
        PoliticaFinanceiraIgreja.objects.filter(igreja=self.igreja).delete()

        payable = self._create_payable()

        policy = PoliticaFinanceiraIgreja.objects.get(igreja=self.igreja)
        self.assertFalse(policy.approval_required)
        self.assertEqual(policy.segregation_level, PoliticaFinanceiraIgreja.LEVEL_1_SIMPLE)
        self.assertEqual(policy.version, 1)
        self.assertEqual(payable.authorization_status, ContaPagar.AUTHORIZATION_NOT_REQUIRED)
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=payable).count(), 1)

    def test_invalid_existing_policy_fails_closed_without_payable_or_event(self):
        policy = PoliticaFinanceiraIgreja.objects.get(igreja=self.igreja)
        PoliticaFinanceiraIgreja.objects.filter(pk=policy.pk).update(
            approval_required=False,
            segregation_level=PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED,
        )

        with self.assertRaises(ValidationError):
            self._create_payable()

        self.assertEqual(ContaPagar.objects.count(), 0)
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.count(), 0)

    def test_event_creation_failure_rolls_back_payable(self):
        with patch(
            'financeiro.services.ContaPagarAutorizacaoEvento.objects.create',
            side_effect=RuntimeError('event failure'),
        ):
            with self.assertRaisesRegex(RuntimeError, 'event failure'):
                self._create_payable()

        self.assertEqual(ContaPagar.objects.count(), 0)
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.count(), 0)

    def test_direct_orm_creation_remains_transitionally_possible_with_null_authorization(self):
        payable = ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            descricao='Conta direta transitoria do service',
            valor=Decimal('10.00'),
            data_emissao=date(2026, 10, 13),
            data_vencimento=date(2026, 10, 20),
        )

        self.assertIsNone(payable.authorization_status)
        self.assertIsNone(payable.current_material_fingerprint)
        self.assertFalse(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=payable).exists())


class ContaPagarFormalAuthorizationServiceTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Formal Authorization',
        )
        self.creator = get_user_model().objects.create_user(username='creator-formal-authorization')
        self.approver = get_user_model().objects.create_user(
            username='approver-formal-authorization',
            first_name='Aprovador',
            last_name='Formal',
        )
        self._grant_approval_permission(self.approver)
        self._set_explicit_scope(self.approver, [self.igreja])
        self._configure_policy()

    def _approval_permission(self):
        return Permission.objects.get(
            content_type__app_label='financeiro',
            codename='approve_contapagar',
        )

    def _grant_approval_permission(self, user):
        user.user_permissions.add(self._approval_permission())

    def _set_explicit_scope(self, user, churches, ministerio=None):
        perfil, _ = PerfilUsuario.objects.get_or_create(
            user=user,
            defaults={'ministerio': ministerio or self.ministerio},
        )
        if perfil.ministerio_id != (ministerio or self.ministerio).pk:
            perfil.ministerio = ministerio or self.ministerio
            perfil.save(update_fields=['ministerio'])
        perfil.igrejas_permitidas.set(churches)
        return perfil

    def _configure_policy(self, *, required=True, level=None, version=1):
        policy = PoliticaFinanceiraIgreja.objects.get(igreja=self.igreja)
        policy.approval_required = required
        policy.segregation_level = level or (
            PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED
            if required else PoliticaFinanceiraIgreja.LEVEL_1_SIMPLE
        )
        policy.version = version
        policy.save()
        return policy

    def _create_pending_payable(self, **overrides):
        payload = {
            'ministerio': self.ministerio,
            'igreja': self.igreja,
            'fornecedor': self.fornecedor,
            'descricao': 'Conta pendente para decisão formal',
            'valor': Decimal('123.45'),
            'data_emissao': date(2026, 10, 13),
            'data_vencimento': date(2026, 10, 20),
            'usuario_criacao': self.creator,
            'actor': self.creator,
        }
        payload.update(overrides)
        return create_payable(**payload)

    def _assert_unchanged_without_event(self, payable, before):
        payable.refresh_from_db()
        self.assertEqual(payable.authorization_status, before['authorization_status'])
        self.assertEqual(payable.current_material_fingerprint, before['current_material_fingerprint'])
        self.assertEqual(
            ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=payable).count(),
            before['event_count'],
        )

    def _state_before_invalid_decision(self, payable):
        return {
            'authorization_status': payable.authorization_status,
            'current_material_fingerprint': payable.current_material_fingerprint,
            'event_count': ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=payable).count(),
        }

    def test_custom_permission_is_declared_and_created_by_django(self):
        permission = self._approval_permission()

        self.assertEqual(ContaPagar._meta.app_label, 'financeiro')
        self.assertIn(
            ('approve_contapagar', 'Pode aprovar ou rejeitar contas a pagar'),
            ContaPagar._meta.permissions,
        )
        self.assertEqual(permission.content_type.app_label, 'financeiro')
        self.assertEqual(permission.codename, 'approve_contapagar')

    def test_capability_and_approval_scope_are_independent_and_fail_closed(self):
        no_capability = get_user_model().objects.create_user(username='no-capability-formal-authorization')
        no_scope = get_user_model().objects.create_user(username='no-scope-formal-authorization')
        self._set_explicit_scope(no_capability, [self.igreja])
        self._grant_approval_permission(no_scope)
        self._set_explicit_scope(no_scope, [])

        self.assertTrue(can_approve_payable(self.approver))
        self.assertFalse(can_approve_payable(no_capability))
        self.assertTrue(can_approve_payable(no_scope))
        self.assertEqual(
            list(get_finance_approval_scope(no_scope, self.ministerio)),
            [],
        )

    def test_approve_persists_current_policy_evidence_and_heals_stale_fingerprint(self):
        payable = self._create_pending_payable()
        payable.current_material_fingerprint = 'v1:sha256:' + ('0' * 64)
        payable.rejected_by = self.creator
        payable.rejected_at = timezone.now()
        payable.current_rejection_reason = 'evidência corrente a limpar'
        payable.save(update_fields=[
            'current_material_fingerprint', 'rejected_by', 'rejected_at', 'current_rejection_reason',
        ])
        policy = self._configure_policy(version=2)

        approved = approve_payable(payable_id=payable.pk, actor=self.approver)
        event = ContaPagarAutorizacaoEvento.objects.get(
            conta_pagar=payable,
            event_type=ContaPagarAutorizacaoEvento.EVENT_APPROVED,
        )
        snapshot = build_payable_material_snapshot_v1(approved)
        fingerprint = compute_payable_material_fingerprint_v1(snapshot)

        self.assertEqual(approved.authorization_status, ContaPagar.AUTHORIZATION_APPROVED)
        self.assertEqual(approved.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_USER_APPROVAL)
        self.assertEqual(approved.authorization_policy_version, 2)
        self.assertEqual(approved.current_material_fingerprint, fingerprint)
        self.assertEqual(approved.approved_material_fingerprint, fingerprint)
        self.assertEqual(approved.approved_by, self.approver)
        self.assertIsNotNone(approved.approved_at)
        self.assertIsNone(approved.rejected_by)
        self.assertIsNone(approved.rejected_at)
        self.assertIsNone(approved.current_rejection_reason)
        self.assertEqual(approved.status, 'PEN')
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=payable).count(), 2)
        self.assertEqual(event.actor, self.approver)
        self.assertEqual(event.actor_user_id_snapshot, self.approver.pk)
        self.assertEqual(event.actor_display_name_snapshot, 'Aprovador Formal')
        self.assertEqual(event.authorization_status_before, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(event.authorization_status_after, ContaPagar.AUTHORIZATION_APPROVED)
        self.assertEqual(event.financial_status_before, 'PEN')
        self.assertEqual(event.financial_status_after, 'PEN')
        self.assertEqual(event.material_snapshot, snapshot)
        self.assertEqual(event.material_fingerprint, fingerprint)
        self.assertEqual(event.policy_snapshot, {
            'policy_id': policy.pk,
            'policy_version': 2,
            'approval_required': True,
            'segregation_level': PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED,
        })
        self.assertIsNone(event.reason)

    def test_reject_persists_reason_event_and_heals_null_fingerprint(self):
        payable = self._create_pending_payable()
        payable.current_material_fingerprint = None
        payable.approved_material_fingerprint = 'v1:sha256:' + ('1' * 64)
        payable.approved_by = self.creator
        payable.approved_at = timezone.now()
        payable.save(update_fields=[
            'current_material_fingerprint', 'approved_material_fingerprint', 'approved_by', 'approved_at',
        ])

        rejected = reject_payable(
            payable_id=payable.pk,
            actor=self.approver,
            reason='  Documento fiscal insuficiente.  ',
        )
        event = ContaPagarAutorizacaoEvento.objects.get(
            conta_pagar=payable,
            event_type=ContaPagarAutorizacaoEvento.EVENT_REJECTED,
        )
        snapshot = build_payable_material_snapshot_v1(rejected)
        fingerprint = compute_payable_material_fingerprint_v1(snapshot)

        self.assertEqual(rejected.authorization_status, ContaPagar.AUTHORIZATION_REJECTED)
        self.assertEqual(rejected.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED)
        self.assertEqual(rejected.current_material_fingerprint, fingerprint)
        self.assertIsNone(rejected.approved_material_fingerprint)
        self.assertIsNone(rejected.approved_by)
        self.assertIsNone(rejected.approved_at)
        self.assertEqual(rejected.rejected_by, self.approver)
        self.assertIsNotNone(rejected.rejected_at)
        self.assertEqual(rejected.current_rejection_reason, 'Documento fiscal insuficiente.')
        self.assertEqual(rejected.status, 'PEN')
        self.assertEqual(event.authorization_status_before, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(event.authorization_status_after, ContaPagar.AUTHORIZATION_REJECTED)
        self.assertEqual(event.financial_status_before, 'PEN')
        self.assertEqual(event.financial_status_after, 'PEN')
        self.assertEqual(event.material_snapshot, snapshot)
        self.assertEqual(event.material_fingerprint, fingerprint)
        self.assertEqual(event.reason, 'Documento fiscal insuficiente.')

    def test_reject_reason_validation_fails_before_mutation(self):
        payable = self._create_pending_payable()
        before = self._state_before_invalid_decision(payable)

        for reason in ('   ', 'x' * 1001):
            with self.assertRaises(ValidationError):
                reject_payable(payable_id=payable.pk, actor=self.approver, reason=reason)
            self._assert_unchanged_without_event(payable, before)

    def test_creator_cannot_approve_or_reject_own_pending_payable(self):
        self._grant_approval_permission(self.creator)
        self._set_explicit_scope(self.creator, [self.igreja])
        payable = self._create_pending_payable()
        before = self._state_before_invalid_decision(payable)

        with self.assertRaises(PermissionDenied):
            approve_payable(payable_id=payable.pk, actor=self.creator)
        self._assert_unchanged_without_event(payable, before)
        with self.assertRaises(PermissionDenied):
            reject_payable(payable_id=payable.pk, actor=self.creator, reason='Não pode auto-rejeitar')
        self._assert_unchanged_without_event(payable, before)

    def test_null_creator_does_not_block_both_formal_decisions(self):
        payable_to_approve = self._create_pending_payable(usuario_criacao=None)
        payable_to_reject = self._create_pending_payable(
            usuario_criacao=None,
            descricao='Conta sem criador para rejeição',
        )

        approve_payable(payable_id=payable_to_approve.pk, actor=self.approver)
        reject_payable(payable_id=payable_to_reject.pk, actor=self.approver, reason='Rejeição válida')

        payable_to_approve.refresh_from_db()
        payable_to_reject.refresh_from_db()
        self.assertEqual(payable_to_approve.authorization_status, ContaPagar.AUTHORIZATION_APPROVED)
        self.assertEqual(payable_to_reject.authorization_status, ContaPagar.AUTHORIZATION_REJECTED)

    def test_capability_scope_hierarchy_admin_and_active_church_do_not_bypass_guards(self):
        payable = self._create_pending_payable()
        no_scope = get_user_model().objects.create_user(username='capability-without-scope')
        scope_only = get_user_model().objects.create_user(username='scope-without-capability')
        admin_without_scope = get_user_model().objects.create_user(username='admin-without-scope')
        hierarchy_without_capability = get_user_model().objects.create_user(username='hierarchy-without-capability')
        active_church_without_scope = get_user_model().objects.create_user(username='active-church-without-scope')
        self._grant_approval_permission(no_scope)
        self._set_explicit_scope(no_scope, [])
        self._set_explicit_scope(scope_only, [self.igreja])
        Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        Group.objects.get_or_create(name=PASTOR_REGIONAL)
        admin_without_scope.groups.add(Group.objects.get(name=ADMIN_MINISTERIO))
        hierarchy_without_capability.groups.add(Group.objects.get(name=PASTOR_REGIONAL))
        self._set_explicit_scope(admin_without_scope, [])
        self._set_explicit_scope(hierarchy_without_capability, [self.igreja])
        self._grant_approval_permission(active_church_without_scope)
        self._set_explicit_scope(active_church_without_scope, [])
        active_church_without_scope.igreja_ativa = self.igreja

        for actor in (no_scope, scope_only, admin_without_scope, hierarchy_without_capability, active_church_without_scope):
            with self.assertRaises(PermissionDenied):
                approve_payable(payable_id=payable.pk, actor=actor)
            with self.assertRaises(PermissionDenied):
                reject_payable(payable_id=payable.pk, actor=actor, reason='Sem autoridade')

        payable.refresh_from_db()
        self.assertEqual(payable.authorization_status, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=payable).count(), 1)

    def test_null_not_required_legacy_and_financial_terminal_states_are_blocked(self):
        payable = self._create_pending_payable()
        cases = (
            (None, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED, 'PEN'),
            (ContaPagar.AUTHORIZATION_NOT_REQUIRED, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED, 'PEN'),
            (ContaPagar.AUTHORIZATION_NOT_REQUIRED, ContaPagar.AUTHORIZATION_ORIGIN_LEGACY_MIGRATION, 'PEN'),
            (ContaPagar.AUTHORIZATION_PENDING, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED, 'PAG'),
            (ContaPagar.AUTHORIZATION_PENDING, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED, 'CAN'),
        )

        for authorization_status, origin, financial_status in cases:
            payable.authorization_status = authorization_status
            payable.authorization_origin = origin
            payable.status = financial_status
            payable.save(update_fields=['authorization_status', 'authorization_origin', 'status'])
            before = self._state_before_invalid_decision(payable)
            with self.assertRaises(ValidationError):
                approve_payable(payable_id=payable.pk, actor=self.approver)
            self._assert_unchanged_without_event(payable, before)
            with self.assertRaises(ValidationError):
                reject_payable(payable_id=payable.pk, actor=self.approver, reason='Estado bloqueado')
            self._assert_unchanged_without_event(payable, before)

    def test_pending_or_overdue_financial_statuses_support_formal_decisions(self):
        overdue_to_approve = self._create_pending_payable()
        overdue_to_reject = self._create_pending_payable(descricao='Conta vencida para rejeição')
        ContaPagar.objects.filter(pk__in=[overdue_to_approve.pk, overdue_to_reject.pk]).update(status='VEN')

        approve_payable(payable_id=overdue_to_approve.pk, actor=self.approver)
        reject_payable(
            payable_id=overdue_to_reject.pk,
            actor=self.approver,
            reason='Conta vencida rejeitada formalmente',
        )

        overdue_to_approve.refresh_from_db()
        overdue_to_reject.refresh_from_db()
        self.assertEqual(overdue_to_approve.status, 'VEN')
        self.assertEqual(overdue_to_approve.authorization_status, ContaPagar.AUTHORIZATION_APPROVED)
        self.assertEqual(overdue_to_reject.status, 'VEN')
        self.assertEqual(overdue_to_reject.authorization_status, ContaPagar.AUTHORIZATION_REJECTED)

    def test_policy_false_requires_b3b_reclassification_without_mutation(self):
        payable = self._create_pending_payable()
        self._configure_policy(required=False, version=2)
        before = self._state_before_invalid_decision(payable)

        with self.assertRaises(ValidationError):
            approve_payable(payable_id=payable.pk, actor=self.approver)
        self._assert_unchanged_without_event(payable, before)
        with self.assertRaises(ValidationError):
            reject_payable(payable_id=payable.pk, actor=self.approver, reason='Não reclassifica no B3A')
        self._assert_unchanged_without_event(payable, before)

    def test_level_2_and_level_3_use_the_same_b3a_transition_rules(self):
        payable_level_2 = self._create_pending_payable()
        approve_payable(payable_id=payable_level_2.pk, actor=self.approver)

        self._configure_policy(level=PoliticaFinanceiraIgreja.LEVEL_3_STRONG, version=2)
        payable_level_3 = self._create_pending_payable(descricao='Conta LEVEL 3')
        reject_payable(payable_id=payable_level_3.pk, actor=self.approver, reason='LEVEL 3 usa B3A')

        payable_level_2.refresh_from_db()
        payable_level_3.refresh_from_db()
        self.assertEqual(payable_level_2.authorization_status, ContaPagar.AUTHORIZATION_APPROVED)
        self.assertEqual(payable_level_3.authorization_status, ContaPagar.AUTHORIZATION_REJECTED)

    def test_second_decision_fails_after_first_transition_and_emits_no_second_event(self):
        payable = self._create_pending_payable()

        approve_payable(payable_id=payable.pk, actor=self.approver)
        with self.assertRaises(ValidationError):
            approve_payable(payable_id=payable.pk, actor=self.approver)
        with self.assertRaises(ValidationError):
            reject_payable(payable_id=payable.pk, actor=self.approver, reason='Não pode redecidir')

        payable.refresh_from_db()
        self.assertEqual(payable.authorization_status, ContaPagar.AUTHORIZATION_APPROVED)
        self.assertEqual(
            ContaPagarAutorizacaoEvento.objects.filter(
                conta_pagar=payable,
                event_type=ContaPagarAutorizacaoEvento.EVENT_APPROVED,
            ).count(),
            1,
        )
        self.assertFalse(
            ContaPagarAutorizacaoEvento.objects.filter(
                conta_pagar=payable,
                event_type=ContaPagarAutorizacaoEvento.EVENT_REJECTED,
            ).exists(),
        )

    def test_rejection_blocks_later_approval_and_emits_no_second_event(self):
        payable = self._create_pending_payable()

        reject_payable(payable_id=payable.pk, actor=self.approver, reason='Primeira decisão vence')
        with self.assertRaises(ValidationError):
            approve_payable(payable_id=payable.pk, actor=self.approver)

        payable.refresh_from_db()
        self.assertEqual(payable.authorization_status, ContaPagar.AUTHORIZATION_REJECTED)
        self.assertEqual(
            ContaPagarAutorizacaoEvento.objects.filter(
                conta_pagar=payable,
                event_type=ContaPagarAutorizacaoEvento.EVENT_REJECTED,
            ).count(),
            1,
        )


class ContaPagarAuthorizationEditReclassificationPlannerTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Reclassificação B3B1',
        )
        self.actor = get_user_model().objects.create_user(username='actor-reclassificacao-b3b1')
        self.igreja_b = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja B Reclassificação',
            tipo_igreja='congregacao',
        )

    def _configure_policy(self, igreja, *, required, version):
        policy = PoliticaFinanceiraIgreja.objects.get(igreja=igreja)
        policy.approval_required = required
        policy.segregation_level = (
            PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED
            if required else PoliticaFinanceiraIgreja.LEVEL_1_SIMPLE
        )
        policy.version = version
        policy.save()
        return policy

    def _create_payable(self, *, igreja=None, descricao='Conta para reclassificação'):
        return create_payable(
            ministerio=self.ministerio,
            igreja=igreja or self.igreja,
            fornecedor=self.fornecedor,
            descricao=descricao,
            valor=Decimal('120.00'),
            data_emissao=date(2026, 10, 13),
            data_vencimento=date(2026, 10, 20),
            usuario_criacao=self.actor,
            actor=self.actor,
        )

    def _set_before_authorization(self, payable, status, *, origin=None):
        payable.authorization_status = status
        payable.authorization_origin = origin or (
            ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED
            if status in {
                ContaPagar.AUTHORIZATION_PENDING,
                ContaPagar.AUTHORIZATION_APPROVED,
                ContaPagar.AUTHORIZATION_REJECTED,
            }
            else ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED
        )
        payable.authorization_policy_version = 7
        payable.current_material_fingerprint = 'v1:sha256:' + ('f' * 64)
        payable.approved_material_fingerprint = 'v1:sha256:' + ('a' * 64)
        payable.approved_by = self.actor
        payable.approved_at = timezone.now()
        payable.rejected_by = self.actor
        payable.rejected_at = timezone.now()
        payable.current_rejection_reason = 'Razão anterior'
        return payable

    def _materially_edit(self, payable):
        payable.descricao = f'{payable.descricao} editada'
        return payable

    def _assert_evidence_cleared(self, payable):
        self.assertIsNone(payable.approved_material_fingerprint)
        self.assertIsNone(payable.approved_by)
        self.assertIsNone(payable.approved_at)
        self.assertIsNone(payable.rejected_by)
        self.assertIsNone(payable.rejected_at)
        self.assertIsNone(payable.current_rejection_reason)

    def test_snapshot_is_pure_and_recomputes_material_fingerprint_despite_stale_storage(self):
        policy = self._configure_policy(self.igreja, required=True, version=3)
        payable = self._create_payable()
        payable.current_material_fingerprint = 'v1:sha256:' + ('0' * 64)
        persisted_before = ContaPagar.objects.get(pk=payable.pk)

        before = build_payable_authorization_edit_snapshot(payable)
        self._materially_edit(payable)
        plan = plan_payable_authorization_after_edit(payable=payable, before=before, policy=policy)

        self.assertEqual(
            before.material_fingerprint,
            compute_payable_material_fingerprint_v1(before.material_snapshot),
        )
        self.assertNotEqual(before.material_fingerprint, payable.current_material_fingerprint)
        self.assertTrue(plan.material_changed)
        self.assertNotEqual(plan.after_material_fingerprint, before.material_fingerprint)
        self.assertEqual(ContaPagar.objects.get(pk=payable.pk).pk, persisted_before.pk)
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=payable).count(), 1)

    def test_non_material_edit_is_authorization_noop_and_apply_is_in_memory_only(self):
        policy = self._configure_policy(self.igreja, required=True, version=4)
        payable = self._set_before_authorization(
            self._create_payable(),
            ContaPagar.AUTHORIZATION_APPROVED,
        )
        before = build_payable_authorization_edit_snapshot(payable)
        persisted = ContaPagar.objects.get(pk=payable.pk)
        payable.observacoes = 'Alteração não material'

        plan = plan_payable_authorization_after_edit(payable=payable, before=before, policy=policy)
        apply_payable_authorization_edit_plan(payable, plan)

        self.assertFalse(plan.material_changed)
        self.assertFalse(plan.church_changed)
        self.assertEqual(plan.event_types, ())
        self.assertEqual(payable.authorization_status, ContaPagar.AUTHORIZATION_APPROVED)
        self.assertEqual(payable.approved_by, self.actor)
        self.assertEqual(ContaPagar.objects.get(pk=payable.pk).authorization_status, persisted.authorization_status)
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=payable).count(), 1)

    def test_material_edit_with_null_authorization_fails_closed(self):
        policy = self._configure_policy(self.igreja, required=True, version=5)
        payable = self._create_payable()
        payable.authorization_status = None
        before = build_payable_authorization_edit_snapshot(payable)
        self._materially_edit(payable)

        with self.assertRaises(ValidationError):
            plan_payable_authorization_after_edit(payable=payable, before=before, policy=policy)

    def test_material_edit_policy_false_reclassifies_all_authorization_states_and_clears_evidence(self):
        policy = self._configure_policy(self.igreja, required=False, version=6)
        for status in (
            ContaPagar.AUTHORIZATION_NOT_REQUIRED,
            ContaPagar.AUTHORIZATION_PENDING,
            ContaPagar.AUTHORIZATION_APPROVED,
            ContaPagar.AUTHORIZATION_REJECTED,
        ):
            with self.subTest(status=status):
                payable = self._set_before_authorization(self._create_payable(descricao=f'False {status}'), status)
                before = build_payable_authorization_edit_snapshot(payable)
                self._materially_edit(payable)

                plan = plan_payable_authorization_after_edit(payable=payable, before=before, policy=policy)
                apply_payable_authorization_edit_plan(payable, plan)

                self.assertEqual(plan.target_authorization_status, ContaPagar.AUTHORIZATION_NOT_REQUIRED)
                self.assertEqual(plan.target_authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED)
                self.assertEqual(plan.target_authorization_policy_version, 6)
                self.assertEqual(plan.event_types, (ContaPagarAutorizacaoEvento.EVENT_EDITED,))
                self.assertTrue(plan.clear_approval_evidence)
                self.assertTrue(plan.clear_rejection_evidence)
                self.assertEqual(payable.authorization_status, ContaPagar.AUTHORIZATION_NOT_REQUIRED)
                self._assert_evidence_cleared(payable)

    def test_material_edit_policy_true_reclassifies_matrix_with_deterministic_events(self):
        policy = self._configure_policy(self.igreja, required=True, version=7)
        expected_events = {
            ContaPagar.AUTHORIZATION_NOT_REQUIRED: (
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
            ),
            ContaPagar.AUTHORIZATION_PENDING: (
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
            ),
            ContaPagar.AUTHORIZATION_APPROVED: (
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_INVALIDATED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
            ),
            ContaPagar.AUTHORIZATION_REJECTED: (
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
            ),
        }
        for status, events in expected_events.items():
            with self.subTest(status=status):
                payable = self._set_before_authorization(self._create_payable(descricao=f'True {status}'), status)
                before = build_payable_authorization_edit_snapshot(payable)
                self._materially_edit(payable)

                plan = plan_payable_authorization_after_edit(payable=payable, before=before, policy=policy)
                apply_payable_authorization_edit_plan(payable, plan)

                self.assertEqual(plan.target_authorization_status, ContaPagar.AUTHORIZATION_PENDING)
                self.assertEqual(plan.target_authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED)
                self.assertEqual(plan.target_authorization_policy_version, 7)
                self.assertEqual(plan.event_types, events)
                self.assertTrue(plan.clear_approval_evidence)
                self.assertTrue(plan.clear_rejection_evidence)
                self._assert_evidence_cleared(payable)

    def test_pending_material_edit_with_church_change_plans_new_request(self):
        self._configure_policy(self.igreja, required=True, version=8)
        target_policy = self._configure_policy(self.igreja_b, required=True, version=9)
        payable = self._set_before_authorization(self._create_payable(), ContaPagar.AUTHORIZATION_PENDING)
        before = build_payable_authorization_edit_snapshot(payable)
        payable.igreja = self.igreja_b
        self._materially_edit(payable)

        plan = plan_payable_authorization_after_edit(payable=payable, before=before, policy=target_policy)

        self.assertTrue(plan.material_changed)
        self.assertTrue(plan.church_changed)
        self.assertEqual(
            plan.event_types,
            (
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
            ),
        )

    def test_church_change_policy_matrix(self):
        cases = (
            (False, ContaPagar.AUTHORIZATION_NOT_REQUIRED, False, ContaPagar.AUTHORIZATION_NOT_REQUIRED, (
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
            )),
            (False, ContaPagar.AUTHORIZATION_NOT_REQUIRED, True, ContaPagar.AUTHORIZATION_PENDING, (
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
            )),
            (True, ContaPagar.AUTHORIZATION_APPROVED, False, ContaPagar.AUTHORIZATION_NOT_REQUIRED, (
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
            )),
            (True, ContaPagar.AUTHORIZATION_PENDING, False, ContaPagar.AUTHORIZATION_NOT_REQUIRED, (
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
            )),
            (True, ContaPagar.AUTHORIZATION_REJECTED, False, ContaPagar.AUTHORIZATION_NOT_REQUIRED, (
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
            )),
            (True, ContaPagar.AUTHORIZATION_NOT_REQUIRED, True, ContaPagar.AUTHORIZATION_PENDING, (
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
            )),
            (True, ContaPagar.AUTHORIZATION_PENDING, True, ContaPagar.AUTHORIZATION_PENDING, (
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
            )),
            (True, ContaPagar.AUTHORIZATION_APPROVED, True, ContaPagar.AUTHORIZATION_PENDING, (
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_INVALIDATED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
            )),
            (True, ContaPagar.AUTHORIZATION_REJECTED, True, ContaPagar.AUTHORIZATION_PENDING, (
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
            )),
        )
        for source_required, before_status, target_required, target_status, events in cases:
            with self.subTest(source_required=source_required, target_required=target_required):
                self._configure_policy(self.igreja, required=source_required, version=10)
                target_policy = self._configure_policy(self.igreja_b, required=target_required, version=11)
                payable = self._set_before_authorization(
                    self._create_payable(descricao=f'Church {source_required}-{target_required}'),
                    before_status,
                )
                before = build_payable_authorization_edit_snapshot(payable)
                payable.igreja = self.igreja_b
                self._materially_edit(payable)

                plan = plan_payable_authorization_after_edit(payable=payable, before=before, policy=target_policy)

                self.assertTrue(plan.church_changed)
                self.assertEqual(plan.target_authorization_status, target_status)
                self.assertEqual(plan.target_authorization_policy_version, 11)
                self.assertEqual(plan.event_types, events)

    def test_legacy_not_required_material_edit_uses_current_policy_and_apply_does_not_persist_or_create_events(self):
        policy = self._configure_policy(self.igreja, required=False, version=12)
        payable = self._set_before_authorization(
            self._create_payable(),
            ContaPagar.AUTHORIZATION_NOT_REQUIRED,
            origin=ContaPagar.AUTHORIZATION_ORIGIN_LEGACY_MIGRATION,
        )
        before = build_payable_authorization_edit_snapshot(payable)
        persisted = ContaPagar.objects.get(pk=payable.pk)
        self._materially_edit(payable)

        plan = plan_payable_authorization_after_edit(payable=payable, before=before, policy=policy)
        apply_payable_authorization_edit_plan(payable, plan)

        self.assertEqual(payable.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED)
        self.assertEqual(payable.authorization_policy_version, 12)
        self.assertEqual(ContaPagar.objects.get(pk=payable.pk).descricao, persisted.descricao)
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=payable).count(), 1)

    def test_policy_must_be_valid_and_belong_to_resulting_church(self):
        invalid_policy = PoliticaFinanceiraIgreja.objects.get(igreja=self.igreja)
        invalid_policy.approval_required = True
        invalid_policy.segregation_level = PoliticaFinanceiraIgreja.LEVEL_1_SIMPLE
        payable = self._create_payable()
        before = build_payable_authorization_edit_snapshot(payable)
        self._materially_edit(payable)

        with self.assertRaises(ValidationError):
            plan_payable_authorization_after_edit(payable=payable, before=before, policy=invalid_policy)

        valid_other_policy = self._configure_policy(self.igreja_b, required=True, version=13)
        with self.assertRaises(ValidationError):
            plan_payable_authorization_after_edit(payable=payable, before=before, policy=valid_other_policy)


class ContaPagarAuthorizationEditEventMaterializationTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Materialização B3B2A',
        )
        self.actor = get_user_model().objects.create_user(
            username='actor-materializacao-b3b2a',
            first_name='Editor',
            last_name='B3B2A',
        )
        self.igreja_b = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja B Materialização',
            tipo_igreja='congregacao',
        )

    def _configure_policy(self, igreja, *, required, version):
        policy = PoliticaFinanceiraIgreja.objects.get(igreja=igreja)
        policy.approval_required = required
        policy.segregation_level = (
            PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED
            if required else PoliticaFinanceiraIgreja.LEVEL_1_SIMPLE
        )
        policy.version = version
        policy.save()
        return policy

    def _create_payable(self, *, igreja=None, descricao='Conta para materialização'):
        return create_payable(
            ministerio=self.ministerio,
            igreja=igreja or self.igreja,
            fornecedor=self.fornecedor,
            descricao=descricao,
            valor=Decimal('120.00'),
            data_emissao=date(2026, 10, 13),
            data_vencimento=date(2026, 10, 20),
            usuario_criacao=self.actor,
            actor=self.actor,
        )

    def _set_before_authorization(self, payable, status):
        payable.authorization_status = status
        payable.authorization_origin = (
            ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED
            if status != ContaPagar.AUTHORIZATION_NOT_REQUIRED
            else ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED
        )
        payable.authorization_policy_version = 7
        payable.current_material_fingerprint = 'v1:sha256:' + ('f' * 64)
        payable.approved_material_fingerprint = 'v1:sha256:' + ('a' * 64)
        payable.approved_by = self.actor
        payable.approved_at = timezone.now()
        payable.rejected_by = self.actor
        payable.rejected_at = timezone.now()
        payable.current_rejection_reason = 'Razão anterior'
        return payable

    def _material_plan(self, *, before_status, policy_required, church_changed=False):
        payable = self._set_before_authorization(self._create_payable(), before_status)
        before = build_payable_authorization_edit_snapshot(payable)
        if church_changed:
            payable.igreja = self.igreja_b
            policy = self._configure_policy(self.igreja_b, required=policy_required, version=9)
        else:
            policy = self._configure_policy(self.igreja, required=policy_required, version=8)
        payable.descricao = f'{payable.descricao} editada'
        plan = plan_payable_authorization_after_edit(payable=payable, before=before, policy=policy)
        return payable, before, plan, policy

    def _materialize(self, *, before_status, policy_required, church_changed=False):
        payable, before, plan, policy = self._material_plan(
            before_status=before_status,
            policy_required=policy_required,
            church_changed=church_changed,
        )
        events = _materialize_payable_edit_authorization_events(
            payable=payable,
            before=before,
            plan=plan,
            policy=policy,
            actor=self.actor,
            financial_status_before='PEN',
            financial_status_after='VEN',
        )
        return payable, before, plan, policy, events

    def _assert_common_payload(self, event, *, plan, policy):
        self.assertEqual(event.actor, self.actor)
        self.assertEqual(event.actor_user_id_snapshot, self.actor.pk)
        self.assertEqual(event.actor_display_name_snapshot, 'Editor B3B2A')
        self.assertEqual(event.financial_status_before, 'PEN')
        self.assertEqual(event.financial_status_after, 'VEN')
        self.assertEqual(event.material_fingerprint, plan.after_material_fingerprint)
        self.assertEqual(event.material_snapshot, plan.after_material_snapshot)
        self.assertEqual(event.policy_snapshot, {
            'policy_id': policy.pk,
            'policy_version': policy.version,
            'approval_required': policy.approval_required,
            'segregation_level': policy.segregation_level,
        })
        self.assertIsNone(event.correlation_id)

    def test_generic_helper_persists_explicit_fields_and_snapshots(self):
        payable = self._create_payable()
        policy = self._configure_policy(self.igreja, required=True, version=21)
        snapshot = {'fingerprint_schema_version': 1, 'descricao': 'material explícito'}

        event = _create_payable_authorization_event(
            payable=payable,
            event_type=ContaPagarAutorizacaoEvento.EVENT_EDITED,
            actor=self.actor,
            authorization_status_before=ContaPagar.AUTHORIZATION_REJECTED,
            authorization_status_after=ContaPagar.AUTHORIZATION_PENDING,
            financial_status_before='PEN',
            financial_status_after='VEN',
            material_fingerprint='v1:sha256:' + ('e' * 64),
            material_snapshot=snapshot,
            policy=policy,
            reason='Motivo explícito',
        )

        self.assertEqual(event.authorization_status_before, ContaPagar.AUTHORIZATION_REJECTED)
        self.assertEqual(event.authorization_status_after, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(event.financial_status_before, 'PEN')
        self.assertEqual(event.financial_status_after, 'VEN')
        self.assertEqual(event.material_fingerprint, 'v1:sha256:' + ('e' * 64))
        self.assertEqual(event.material_snapshot, snapshot)
        self.assertEqual(event.reason, 'Motivo explícito')
        self.assertEqual(event.actor, self.actor)
        self.assertEqual(event.actor_user_id_snapshot, self.actor.pk)
        self.assertEqual(event.actor_display_name_snapshot, 'Editor B3B2A')
        self.assertEqual(event.policy_snapshot['policy_id'], policy.pk)
        self.assertIsNone(event.correlation_id)

    def test_generic_helper_preserves_none_actor_and_explicit_correlation_id(self):
        payable = self._create_payable()
        policy = self._configure_policy(self.igreja, required=False, version=22)
        correlation_id = uuid4()

        event = _create_payable_authorization_event(
            payable=payable,
            event_type=ContaPagarAutorizacaoEvento.EVENT_EDITED,
            actor=None,
            authorization_status_before=ContaPagar.AUTHORIZATION_NOT_REQUIRED,
            authorization_status_after=ContaPagar.AUTHORIZATION_NOT_REQUIRED,
            financial_status_before='PEN',
            financial_status_after='PEN',
            material_fingerprint='v1:sha256:' + ('d' * 64),
            material_snapshot={'fingerprint_schema_version': 1},
            policy=policy,
            correlation_id=correlation_id,
        )

        self.assertIsNone(event.actor)
        self.assertIsNone(event.actor_user_id_snapshot)
        self.assertIsNone(event.actor_display_name_snapshot)
        self.assertEqual(event.correlation_id, correlation_id)

    def test_non_material_plan_materializes_zero_events(self):
        payable = self._set_before_authorization(
            self._create_payable(),
            ContaPagar.AUTHORIZATION_APPROVED,
        )
        before = build_payable_authorization_edit_snapshot(payable)
        policy = self._configure_policy(self.igreja, required=True, version=23)
        plan = plan_payable_authorization_after_edit(payable=payable, before=before, policy=policy)

        events = _materialize_payable_edit_authorization_events(
            payable=payable,
            before=before,
            plan=plan,
            policy=policy,
            actor=self.actor,
            financial_status_before='PEN',
            financial_status_after='PEN',
        )

        self.assertEqual(events, ())
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=payable).count(), 1)

    def test_not_required_material_policy_false_materializes_edited_only(self):
        _, before, plan, policy, events = self._materialize(
            before_status=ContaPagar.AUTHORIZATION_NOT_REQUIRED,
            policy_required=False,
        )

        self.assertEqual([event.event_type for event in events], [ContaPagarAutorizacaoEvento.EVENT_EDITED])
        edited = events[0]
        self.assertEqual(edited.authorization_status_before, before.authorization_status)
        self.assertEqual(edited.authorization_status_after, plan.target_authorization_status)
        self.assertIsNone(edited.reason)
        self._assert_common_payload(edited, plan=plan, policy=policy)

    def test_not_required_material_policy_true_materializes_edited_and_requested(self):
        _, before, plan, policy, events = self._materialize(
            before_status=ContaPagar.AUTHORIZATION_NOT_REQUIRED,
            policy_required=True,
        )

        self.assertEqual([event.event_type for event in events], [
            ContaPagarAutorizacaoEvento.EVENT_EDITED,
            ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
        ])
        self.assertEqual(events[0].authorization_status_before, before.authorization_status)
        self.assertEqual(events[0].authorization_status_after, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(events[1].authorization_status_before, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(events[1].authorization_status_after, ContaPagar.AUTHORIZATION_PENDING)
        self._assert_common_payload(events[0], plan=plan, policy=policy)
        self._assert_common_payload(events[1], plan=plan, policy=policy)

    def test_pending_material_same_context_materializes_edited_only(self):
        _, before, plan, policy, events = self._materialize(
            before_status=ContaPagar.AUTHORIZATION_PENDING,
            policy_required=True,
        )

        self.assertEqual([event.event_type for event in events], [ContaPagarAutorizacaoEvento.EVENT_EDITED])
        self.assertEqual(events[0].authorization_status_before, before.authorization_status)
        self.assertEqual(events[0].authorization_status_after, ContaPagar.AUTHORIZATION_PENDING)
        self._assert_common_payload(events[0], plan=plan, policy=policy)

    def test_pending_changed_church_materializes_edited_and_requested(self):
        _, _, plan, policy, events = self._materialize(
            before_status=ContaPagar.AUTHORIZATION_PENDING,
            policy_required=True,
            church_changed=True,
        )

        self.assertEqual([event.event_type for event in events], [
            ContaPagarAutorizacaoEvento.EVENT_EDITED,
            ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
        ])
        self._assert_common_payload(events[0], plan=plan, policy=policy)
        self._assert_common_payload(events[1], plan=plan, policy=policy)

    def test_approved_material_persists_all_events_in_plan_order(self):
        _, before, plan, policy, events = self._materialize(
            before_status=ContaPagar.AUTHORIZATION_APPROVED,
            policy_required=True,
        )

        self.assertEqual([event.event_type for event in events], [
            ContaPagarAutorizacaoEvento.EVENT_EDITED,
            ContaPagarAutorizacaoEvento.EVENT_APPROVAL_INVALIDATED,
            ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
        ])
        self.assertEqual([event.event_type for event in sorted(events, key=lambda event: event.id)], [
            ContaPagarAutorizacaoEvento.EVENT_EDITED,
            ContaPagarAutorizacaoEvento.EVENT_APPROVAL_INVALIDATED,
            ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
        ])
        self.assertEqual(events[0].authorization_status_before, before.authorization_status)
        self.assertEqual(events[0].authorization_status_after, ContaPagar.AUTHORIZATION_PENDING)
        self.assertIsNone(events[0].reason)
        self.assertIsNone(events[0].correlation_id)
        self.assertEqual(events[1].authorization_status_before, ContaPagar.AUTHORIZATION_APPROVED)
        self.assertEqual(events[1].authorization_status_after, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(events[1].reason, 'Aprovação invalidada por alteração material da conta.')
        self.assertIsNone(events[1].correlation_id)
        self.assertEqual(events[2].authorization_status_before, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(events[2].authorization_status_after, ContaPagar.AUTHORIZATION_PENDING)
        self.assertIsNone(events[2].reason)
        self.assertIsNone(events[2].correlation_id)
        for event in events:
            self._assert_common_payload(event, plan=plan, policy=policy)

    def test_rejected_material_materializes_edited_and_requested(self):
        _, before, plan, policy, events = self._materialize(
            before_status=ContaPagar.AUTHORIZATION_REJECTED,
            policy_required=True,
        )

        self.assertEqual([event.event_type for event in events], [
            ContaPagarAutorizacaoEvento.EVENT_EDITED,
            ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
        ])
        self.assertEqual(events[0].authorization_status_before, before.authorization_status)
        self.assertEqual(events[0].authorization_status_after, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(events[1].authorization_status_before, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(events[1].authorization_status_after, ContaPagar.AUTHORIZATION_PENDING)
        self._assert_common_payload(events[0], plan=plan, policy=policy)
        self._assert_common_payload(events[1], plan=plan, policy=policy)

    def test_materializer_does_not_mutate_or_save_payable(self):
        payable, before, plan, policy = self._material_plan(
            before_status=ContaPagar.AUTHORIZATION_APPROVED,
            policy_required=True,
        )
        state_before = {
            'authorization_status': payable.authorization_status,
            'authorization_origin': payable.authorization_origin,
            'authorization_policy_version': payable.authorization_policy_version,
            'current_material_fingerprint': payable.current_material_fingerprint,
            'approved_material_fingerprint': payable.approved_material_fingerprint,
            'approved_by_id': payable.approved_by_id,
            'approved_at': payable.approved_at,
            'rejected_by_id': payable.rejected_by_id,
            'rejected_at': payable.rejected_at,
            'current_rejection_reason': payable.current_rejection_reason,
            'status': payable.status,
            'data_pagamento': payable.data_pagamento,
            'valor_pago': payable.valor_pago,
            'juros_multa': payable.juros_multa,
            'desconto': payable.desconto,
            'conta_debito_id': payable.conta_debito_id,
            'forma_pagamento': payable.forma_pagamento,
            'comprovante': payable.comprovante.name if payable.comprovante else None,
        }
        persisted_description = ContaPagar.objects.get(pk=payable.pk).descricao

        _materialize_payable_edit_authorization_events(
            payable=payable,
            before=before,
            plan=plan,
            policy=policy,
            actor=self.actor,
            financial_status_before='PEN',
            financial_status_after='PEN',
        )

        self.assertEqual(payable.authorization_status, state_before['authorization_status'])
        self.assertEqual(payable.authorization_origin, state_before['authorization_origin'])
        self.assertEqual(payable.authorization_policy_version, state_before['authorization_policy_version'])
        self.assertEqual(payable.current_material_fingerprint, state_before['current_material_fingerprint'])
        self.assertEqual(payable.approved_material_fingerprint, state_before['approved_material_fingerprint'])
        self.assertEqual(payable.approved_by_id, state_before['approved_by_id'])
        self.assertEqual(payable.approved_at, state_before['approved_at'])
        self.assertEqual(payable.rejected_by_id, state_before['rejected_by_id'])
        self.assertEqual(payable.rejected_at, state_before['rejected_at'])
        self.assertEqual(payable.current_rejection_reason, state_before['current_rejection_reason'])
        self.assertEqual(payable.status, state_before['status'])
        self.assertEqual(payable.data_pagamento, state_before['data_pagamento'])
        self.assertEqual(payable.valor_pago, state_before['valor_pago'])
        self.assertEqual(payable.juros_multa, state_before['juros_multa'])
        self.assertEqual(payable.desconto, state_before['desconto'])
        self.assertEqual(payable.conta_debito_id, state_before['conta_debito_id'])
        self.assertEqual(payable.forma_pagamento, state_before['forma_pagamento'])
        self.assertEqual(payable.comprovante.name if payable.comprovante else None, state_before['comprovante'])
        self.assertEqual(ContaPagar.objects.get(pk=payable.pk).descricao, persisted_description)

    def test_materializer_propagates_event_creation_failure(self):
        payable, before, plan, policy = self._material_plan(
            before_status=ContaPagar.AUTHORIZATION_NOT_REQUIRED,
            policy_required=False,
        )

        with patch(
            'financeiro.services.ContaPagarAutorizacaoEvento.objects.create',
            side_effect=RuntimeError('falha de persistência de evento'),
        ):
            with self.assertRaisesRegex(RuntimeError, 'falha de persistência de evento'):
                _materialize_payable_edit_authorization_events(
                    payable=payable,
                    before=before,
                    plan=plan,
                    policy=policy,
                    actor=self.actor,
                    financial_status_before='PEN',
                    financial_status_after='PEN',
                )


@skipUnless(django_settings.MIGRATION_MODULES == {}, 'Requer core.settings_test_migrations.')
class ContaPagarFormalDecisionPermissionMigrationTest(TestCase):
    def test_post_migrate_creates_the_formal_payable_decision_permission(self):
        permission = Permission.objects.get(
            content_type__app_label='financeiro',
            content_type__model='contapagar',
            codename='approve_contapagar',
        )

        self.assertEqual(permission.name, 'Pode aprovar ou rejeitar contas a pagar')


@skipUnless(django_settings.MIGRATION_MODULES == {}, 'Requer core.settings_test_migrations.')
class ContaPagarPrePaymentAuthorizationMigrationTest(TransactionTestCase):
    migrate_from = ('financeiro', '0019_despesas_criado_por')
    migrate_to = ('financeiro', '0020_prepayment_authorization_expansive')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.executor = MigrationExecutor(connection)
        cls.executor.migrate([cls.migrate_from])
        cls.old_apps = cls.executor.loader.project_state([cls.migrate_from]).apps

        User = cls.old_apps.get_model('auth', 'User')
        Ministerio = cls.old_apps.get_model('configuracao', 'Ministerio')
        Igreja = cls.old_apps.get_model('configuracao', 'Igreja')
        Fornecedor = cls.old_apps.get_model('financeiro', 'Fornecedor')
        ContaPagar = cls.old_apps.get_model('financeiro', 'ContaPagar')
        Despesas = cls.old_apps.get_model('financeiro', 'Despesas')

        cls.user = User.objects.create(username='migration-prepayment-user')
        cls.ministerio = CurrentMinisterio.objects.create(
            nome_fantasia='Ministerio Migration Prepayment',
            administrador_principal_id=cls.user.pk,
            ativo=True,
            cnpj='11111111000111',
            is_demo=False,
        )
        cls.igrejas = [
            Igreja.objects.create(ministerio_id=cls.ministerio.pk, nome_igreja=f'Igreja Migration {indice}', tipo_igreja='sede')
            for indice in range(1, 3)
        ]
        cls.fornecedor = Fornecedor.objects.create(ministerio_id=cls.ministerio.pk, nome='Fornecedor Migration')
        cls.pre_migration_despesa_count = Despesas.objects.count()
        cls.legacy_payables = {}
        for indice, status in enumerate(('PEN', 'VEN', 'PAG', 'CAN'), start=1):
            conta = ContaPagar.objects.create(
                ministerio_id=cls.ministerio.pk,
                igreja_id=cls.igrejas[indice % 2].pk,
                fornecedor_id=cls.fornecedor.pk,
                descricao=f'  Conta legado {status}\r\nlinha {indice}  ',
                numero_documento=f'NF-{indice}',
                observacoes=f'Observacao {indice}',
                valor=Decimal(f'{indice * 10}.50'),
                data_emissao=date(2026, 9, indice),
                data_vencimento=date(2026, 10, indice),
                status=status,
            )
            cls.legacy_payables[status] = conta.pk

        cls.executor = MigrationExecutor(connection)
        cls.executor.migrate([cls.migrate_to])
        cls.apps = cls.executor.loader.project_state([cls.migrate_to]).apps

    def test_forward_backfills_policy_payables_events_and_preserves_financial_status(self):
        Politica = self.apps.get_model('financeiro', 'PoliticaFinanceiraIgreja')
        ContaPagar = self.apps.get_model('financeiro', 'ContaPagar')
        Evento = self.apps.get_model('financeiro', 'ContaPagarAutorizacaoEvento')
        Despesas = self.apps.get_model('financeiro', 'Despesas')

        self.assertEqual(Politica.objects.filter(igreja_id__in=[igreja.pk for igreja in self.igrejas]).count(), 2)
        for politica in Politica.objects.filter(igreja_id__in=[igreja.pk for igreja in self.igrejas]):
            self.assertFalse(politica.approval_required)
            self.assertEqual(politica.segregation_level, 'LEVEL_1_SIMPLE')
            self.assertEqual(politica.version, 1)

        for status, payable_id in self.legacy_payables.items():
            conta = ContaPagar.objects.get(pk=payable_id)
            self.assertEqual(conta.status, status)
            self.assertEqual(conta.authorization_status, 'NOT_REQUIRED')
            self.assertEqual(conta.authorization_origin, 'LEGACY_MIGRATION')
            self.assertIsNone(conta.authorization_policy_version)
            self.assertTrue(conta.current_material_fingerprint.startswith('v1:sha256:'))
            self.assertIsNone(conta.approved_by_id)
            self.assertIsNone(conta.approved_at)
            self.assertIsNone(conta.rejected_by_id)
            self.assertIsNone(conta.rejected_at)
            self.assertIsNone(conta.current_rejection_reason)

            eventos = Evento.objects.filter(conta_pagar_id=payable_id, event_type='LEGACY_MIGRATED')
            self.assertEqual(eventos.count(), 1)
            evento = eventos.get()
            self.assertEqual(evento.authorization_status_after, 'NOT_REQUIRED')
            self.assertEqual(evento.financial_status_after, status)
            self.assertEqual(evento.material_fingerprint, conta.current_material_fingerprint)
            self.assertEqual(evento.policy_snapshot['origin'], 'LEGACY_MIGRATION')
            self.assertFalse(evento.policy_snapshot['historical_policy_known'])
            self.assertIsNone(evento.policy_snapshot['policy_id'])
            self.assertIsNone(evento.policy_snapshot['policy_version'])

        self.assertEqual(Despesas.objects.count(), self.pre_migration_despesa_count)

    def test_v1_fingerprint_is_deterministic_and_excludes_non_material_fields(self):
        migration_module = importlib.import_module('financeiro.migrations.0020_prepayment_authorization_expansive')
        conta = SimpleNamespace(
            igreja_id=1,
            fornecedor_id=2,
            valor=Decimal('10.5'),
            data_vencimento=date(2026, 10, 20),
            descricao='  Descricao\r\nLegado  ',
            numero_documento='NF-1',
            observacoes='Observacao 1',
        )
        mesmo_material = SimpleNamespace(**vars(conta))
        numero_documento_alterado = SimpleNamespace(**{**vars(conta), 'numero_documento': 'NF-2'})
        observacoes_alteradas = SimpleNamespace(**{**vars(conta), 'observacoes': 'Outra observacao'})
        valor_alterado = SimpleNamespace(**{**vars(conta), 'valor': Decimal('11.50')})
        descricao_alterada = SimpleNamespace(**{**vars(conta), 'descricao': 'Descricao diferente'})

        fingerprint = migration_module._material_fingerprint(migration_module._material_snapshot(conta))
        self.assertEqual(fingerprint, migration_module._material_fingerprint(migration_module._material_snapshot(mesmo_material)))
        self.assertEqual(fingerprint, migration_module._material_fingerprint(migration_module._material_snapshot(numero_documento_alterado)))
        self.assertEqual(fingerprint, migration_module._material_fingerprint(migration_module._material_snapshot(observacoes_alteradas)))
        self.assertNotEqual(fingerprint, migration_module._material_fingerprint(migration_module._material_snapshot(valor_alterado)))
        self.assertNotEqual(fingerprint, migration_module._material_fingerprint(migration_module._material_snapshot(descricao_alterada)))

    def test_post_migration_state_allows_new_payable_with_null_authorization_fields(self):
        ContaPagar = self.apps.get_model('financeiro', 'ContaPagar')
        Evento = self.apps.get_model('financeiro', 'ContaPagarAutorizacaoEvento')
        user = get_user_model().objects.create(username='post-migration-prepayment-user')
        ministerio = CurrentMinisterio.objects.create(
            nome_fantasia='Ministerio criado apos migration 0020',
            administrador_principal_id=user.pk,
            ativo=True,
            cnpj='22222222000122',
            is_demo=False,
        )
        igreja = Igreja.objects.create(
            ministerio=ministerio,
            nome_igreja='Igreja criada apos migration 0020',
            tipo_igreja='congregacao',
        )
        fornecedor = Fornecedor.objects.create(
            ministerio=ministerio,
            nome='Fornecedor criado apos migration 0020',
        )

        conta = ContaPagar.objects.create(
            ministerio_id=ministerio.pk,
            igreja_id=igreja.pk,
            fornecedor_id=fornecedor.pk,
            descricao='Conta criada apos migration 0020',
            valor=Decimal('99.90'),
            data_emissao=date(2026, 10, 21),
            data_vencimento=date(2026, 10, 31),
        )

        self.assertIsNone(conta.authorization_status)
        self.assertIsNone(conta.authorization_origin)
        self.assertIsNone(conta.authorization_policy_version)
        self.assertIsNone(conta.current_material_fingerprint)
        self.assertFalse(Evento.objects.filter(conta_pagar_id=conta.pk, event_type='LEGACY_MIGRATED').exists())

    def test_legacy_boundary_is_captured_before_policy_backfill(self):
        migration_module = importlib.import_module('financeiro.migrations.0020_prepayment_authorization_expansive')
        with open(migration_module.__file__, encoding='utf-8') as migration_file:
            function = next(
                node
                for node in ast.parse(migration_file.read()).body
                if isinstance(node, ast.FunctionDef) and node.name == 'backfill_prepayment_authorization'
            )

        legacy_max_pk_indexes = [
            index
            for index, statement in enumerate(function.body)
            if isinstance(statement, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == 'legacy_max_pk' for target in statement.targets)
        ]
        policy_backfill_index = next(index for index, statement in enumerate(function.body) if isinstance(statement, ast.For))

        self.assertEqual(len(legacy_max_pk_indexes), 1)
        self.assertLess(legacy_max_pk_indexes[0], policy_backfill_index)


@skipUnless(django_settings.MIGRATION_MODULES == {}, 'Requer core.settings_test_migrations.')
class PoliticaFinanceiraIgrejaReconciliationMigrationTest(TransactionTestCase):
    migrate_from = ('financeiro', '0020_prepayment_authorization_expansive')
    migrate_to = ('financeiro', '0021_reconcile_financial_policies')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.executor = MigrationExecutor(connection)
        cls.executor.migrate([cls.migrate_from])
        cls.old_apps = cls.executor.loader.project_state([cls.migrate_from]).apps

        User = cls.old_apps.get_model('auth', 'User')
        Igreja = cls.old_apps.get_model('configuracao', 'Igreja')
        PoliticaFinanceiraIgreja = cls.old_apps.get_model('financeiro', 'PoliticaFinanceiraIgreja')

        user = User.objects.create(username='policy-reconciliation-migration-user')
        ministerio = CurrentMinisterio.objects.create(
            nome_fantasia='Ministerio Reconciliacao de Politicas',
            administrador_principal_id=user.pk,
            ativo=True,
            cnpj='33333333000133',
            is_demo=False,
        )
        igreja_a = Igreja.objects.create(
            ministerio_id=ministerio.pk,
            nome_igreja='Igreja A Politica Configurada',
            tipo_igreja='sede',
        )
        igreja_b = Igreja.objects.create(
            ministerio_id=ministerio.pk,
            nome_igreja='Igreja B Sem Politica',
            tipo_igreja='congregacao',
        )
        igreja_c = Igreja.objects.create(
            ministerio_id=ministerio.pk,
            nome_igreja='Igreja C Sem Politica',
            tipo_igreja='congregacao',
        )
        PoliticaFinanceiraIgreja.objects.create(
            igreja_id=igreja_a.pk,
            approval_required=True,
            segregation_level='LEVEL_2_CONTROLLED',
            version=9,
        )

        cls.igreja_a_id = igreja_a.pk
        cls.igreja_b_id = igreja_b.pk
        cls.igreja_c_id = igreja_c.pk

        cls.executor = MigrationExecutor(connection)
        cls.executor.migrate([cls.migrate_to])
        cls.apps = cls.executor.loader.project_state([cls.migrate_to]).apps

    def test_forward_reconciles_missing_policies_and_preserves_configured_policy(self):
        PoliticaFinanceiraIgreja = self.apps.get_model('financeiro', 'PoliticaFinanceiraIgreja')

        politica_a = PoliticaFinanceiraIgreja.objects.get(igreja_id=self.igreja_a_id)
        politica_b = PoliticaFinanceiraIgreja.objects.get(igreja_id=self.igreja_b_id)
        politica_c = PoliticaFinanceiraIgreja.objects.get(igreja_id=self.igreja_c_id)

        self.assertTrue(politica_a.approval_required)
        self.assertEqual(politica_a.segregation_level, 'LEVEL_2_CONTROLLED')
        self.assertEqual(politica_a.version, 9)

        for politica in (politica_b, politica_c):
            self.assertFalse(politica.approval_required)
            self.assertEqual(politica.segregation_level, 'LEVEL_1_SIMPLE')
            self.assertEqual(politica.version, 1)

        self.assertEqual(PoliticaFinanceiraIgreja.objects.filter(igreja_id=self.igreja_a_id).count(), 1)
        self.assertEqual(PoliticaFinanceiraIgreja.objects.filter(igreja_id=self.igreja_b_id).count(), 1)
        self.assertEqual(PoliticaFinanceiraIgreja.objects.filter(igreja_id=self.igreja_c_id).count(), 1)

        migration_module = importlib.import_module(
            'financeiro.migrations.0021_reconcile_financial_policies',
        )
        migration_module.reconcile_financial_policies(self.apps, schema_editor=None)

        politica_a = PoliticaFinanceiraIgreja.objects.get(igreja_id=self.igreja_a_id)
        self.assertTrue(politica_a.approval_required)
        self.assertEqual(politica_a.segregation_level, 'LEVEL_2_CONTROLLED')
        self.assertEqual(politica_a.version, 9)
        self.assertEqual(PoliticaFinanceiraIgreja.objects.filter(igreja_id=self.igreja_a_id).count(), 1)
        self.assertEqual(PoliticaFinanceiraIgreja.objects.filter(igreja_id=self.igreja_b_id).count(), 1)
        self.assertEqual(PoliticaFinanceiraIgreja.objects.filter(igreja_id=self.igreja_c_id).count(), 1)


class FechamentoCaixaServiceTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()

        self.conta = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao="Caixa Tesouraria",
            tipo="caixa_fisico",
            saldo_inicial=Decimal("1000.00"),
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome="Operacional Financeiro",
        )

        self.receita_valida = Receitas.objects.create(
            igreja=self.igreja,
            categoria="oferta",
            data=date(2026, 5, 2),
            valor=Decimal("300.00"),
            conta_bancaria=self.conta,
            fechado=False,
        )
        Receitas.objects.create(
            igreja=self.igreja,
            categoria="dizimo",
            data=date(2026, 4, 28),
            valor=Decimal("100.00"),
            conta_bancaria=self.conta,
            fechado=False,
        )
        Receitas.objects.create(
            igreja=self.igreja,
            categoria="dizimo",
            data=date(2026, 5, 3),
            valor=Decimal("50.00"),
            conta_bancaria=self.conta,
            fechado=True,
        )

        self.despesa_valida = Despesas.objects.create(
            igreja=self.igreja,
            data=date(2026, 5, 3),
            descricao="Conta de Agua",
            valor=Decimal("80.00"),
            categoria=self.categoria,
            conta_bancaria=self.conta,
            fechado=False,
        )
        Despesas.objects.create(
            igreja=self.igreja,
            data=date(2026, 5, 4),
            descricao="Conta de Luz",
            valor=Decimal("60.00"),
            categoria=self.categoria,
            conta_bancaria=self.conta,
            fechado=True,
        )

    def test_buscar_dados(self):
        service = FechamentoCaixaService(
            data_inicio=date(2026, 5, 1),
            data_fim=date(2026, 5, 31),
            igreja=self.igreja,
        )

        receitas, despesas = service.buscar_dados()

        self.assertEqual(list(receitas.values_list("id", flat=True)), [self.receita_valida.id])
        self.assertEqual(list(despesas.values_list("id", flat=True)), [self.despesa_valida.id])

    def test_calcular_totais(self):
        service = FechamentoCaixaService(
            data_inicio=date(2026, 5, 1),
            data_fim=date(2026, 5, 31),
            igreja=self.igreja,
        )
        receitas, despesas = service.buscar_dados()

        total_entradas, total_saidas, saldo_final = service.calcular_totais(receitas, despesas)

        self.assertEqual(total_entradas, Decimal("300.00"))
        self.assertEqual(total_saidas, Decimal("80.00"))
        self.assertEqual(saldo_final, Decimal("220.00"))

    def test_fechar_caixa(self):
        service = FechamentoCaixaService(
            data_inicio=date(2026, 5, 1),
            data_fim=date(2026, 5, 31),
            igreja=self.igreja,
            observacoes="Fechamento mensal automatico",
        )
        receitas, despesas = service.buscar_dados()
        total_entradas, total_saidas, saldo_final = service.calcular_totais(receitas, despesas)

        fechamento = service.fechar_caixa(total_entradas, total_saidas, saldo_final)

        self.assertIsInstance(fechamento, FechamentoCaixa)
        self.assertEqual(fechamento.igreja_id, self.igreja.id)
        self.assertEqual(fechamento.total_entradas, Decimal("300.00"))
        self.assertEqual(fechamento.total_saidas, Decimal("80.00"))
        self.assertEqual(fechamento.saldo_final, Decimal("220.00"))
        self.assertEqual(fechamento.status, "fechado")

    def test_fechamento_rejeita_fundo_de_outra_igreja(self):
        ministerio_b = Ministerio.objects.create(
            nome_fantasia="Ministerio Fechamento B",
            administrador_principal=self.user,
            ativo=True,
            cnpj="12345678000155",
        )
        igreja_b = Igreja.objects.create(
            nome_igreja="Igreja Fechamento B",
            ministerio=ministerio_b,
            tipo_igreja="congregacao",
        )
        fundo_outra_igreja = FundoDepartamental.objects.create(
            igreja=igreja_b,
            codigo='PROJETO_TESTE',
            nome_exibicao='Projeto Teste',
            ativo=True,
        )

        fechamento = FechamentoCaixa(
            igreja=self.igreja,
            fundo_departamental=fundo_outra_igreja,
            data_inicio=date(2026, 5, 1),
            data_fim=date(2026, 5, 31),
            total_entradas=Decimal("0.00"),
            total_saidas=Decimal("0.00"),
            saldo_final=Decimal("0.00"),
            status='fechado',
        )

        with self.assertRaises(ValidationError):
            fechamento.full_clean()


class TransferenciaCaixaModelTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.conta_origem = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao="Caixa Origem",
            tipo="caixa_fisico",
            saldo_inicial=Decimal("1000.00"),
        )
        self.conta_destino = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao="Caixa Destino",
            tipo="caixa_fisico",
            saldo_inicial=Decimal("200.00"),
        )

        self.ministerio_b = Ministerio.objects.create(
            nome_fantasia="Ministerio B",
            administrador_principal=self.user,
            ativo=True,
            cnpj="12345678000177",
        )
        self.igreja_b = Igreja.objects.create(
            nome_igreja="Igreja B",
            ministerio=self.ministerio_b,
            tipo_igreja="congregacao",
        )
        self.conta_outra_igreja = ContaBancaria.objects.create(
            igreja=self.igreja_b,
            nome_identificacao="Caixa Outra Igreja",
            tipo="caixa_fisico",
            saldo_inicial=Decimal("300.00"),
        )

    def test_transferencia_atualiza_saldos(self):
        transferencia = TransferenciaCaixa.objects.create(
            caixa_origem=self.conta_origem,
            caixa_destino=self.conta_destino,
            valor=Decimal("150.00"),
            observacao="Repasse mensal",
            usuario=self.user,
        )

        self.conta_origem.refresh_from_db()
        self.conta_destino.refresh_from_db()

        self.assertIsNotNone(transferencia.pk)
        self.assertEqual(self.conta_origem.saldo_atual, Decimal("850.00"))
        self.assertEqual(self.conta_destino.saldo_atual, Decimal("350.00"))

    def test_transferencia_rejeita_mesma_conta(self):
        with self.assertRaises(ValidationError):
            TransferenciaCaixa.objects.create(
                caixa_origem=self.conta_origem,
                caixa_destino=self.conta_origem,
                valor=Decimal("10.00"),
                usuario=self.user,
            )

    def test_transferencia_rejeita_caixas_de_igrejas_diferentes(self):
        with self.assertRaises(ValidationError):
            TransferenciaCaixa.objects.create(
                caixa_origem=self.conta_origem,
                caixa_destino=self.conta_outra_igreja,
                valor=Decimal("10.00"),
                usuario=self.user,
            )

    def test_transferencia_rejeita_saldo_insuficiente(self):
        with self.assertRaises(ValidationError):
            TransferenciaCaixa.objects.create(
                caixa_origem=self.conta_origem,
                caixa_destino=self.conta_destino,
                valor=Decimal("1500.00"),
                usuario=self.user,
            )


class AuditoriaFinanceiraTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.conta = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao="Caixa Auditoria",
            tipo="caixa_fisico",
            saldo_inicial=Decimal("500.00"),
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome="Categoria Auditoria",
        )

    def test_log_gerado_para_receita_criada_atualizada_excluida(self):
        receita = Receitas.objects.create(
            igreja=self.igreja,
            categoria="oferta",
            data=date(2026, 5, 5),
            valor=Decimal("70.00"),
            conta_bancaria=self.conta,
            fechado=False,
        )
        receita.valor = Decimal("90.00")
        receita.save()
        receita_id = receita.id
        receita.delete()

        logs = LogTransacaoFinanceira.objects.filter(
            tipo_lancamento='receita',
            referencia_modelo='Receitas',
            referencia_id=receita_id,
        ).order_by('criado_em')

        self.assertEqual(logs.count(), 3)
        self.assertEqual(list(logs.values_list('acao', flat=True)), ['criado', 'atualizado', 'excluido'])
        self.assertTrue(all(log.igreja_id == self.igreja.id for log in logs))

    def test_log_transferencia_registra_usuario(self):
        destino = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao="Caixa Destino Auditoria",
            tipo="caixa_fisico",
            saldo_inicial=Decimal("100.00"),
        )

        transferencia = TransferenciaCaixa.objects.create(
            caixa_origem=self.conta,
            caixa_destino=destino,
            valor=Decimal("50.00"),
            usuario=self.user,
        )

        log = LogTransacaoFinanceira.objects.filter(
            tipo_lancamento='transferencia',
            referencia_modelo='TransferenciaCaixa',
            referencia_id=transferencia.id,
        ).latest('criado_em')

        self.assertEqual(log.acao, 'criado')
        self.assertEqual(log.usuario_id, self.user.id)

    def test_log_fechamento_usa_saldo_final_como_valor(self):
        fechamento = FechamentoCaixa.objects.create(
            igreja=self.igreja,
            data_inicio=date(2026, 5, 1),
            data_fim=date(2026, 5, 31),
            total_entradas=Decimal("300.00"),
            total_saidas=Decimal("80.00"),
            saldo_final=Decimal("220.00"),
            status='fechado',
            observacoes='Fechamento de auditoria',
        )

        log = LogTransacaoFinanceira.objects.filter(
            tipo_lancamento='fechamento',
            referencia_modelo='FechamentoCaixa',
            referencia_id=fechamento.id,
        ).latest('criado_em')

        self.assertEqual(log.acao, 'criado')
        self.assertEqual(log.valor, Decimal("220.00"))


class OFXImportServiceTest(TestCase):
        def setUp(self):
                self.service = OFXImportService()
                self.ofx_content = """OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX>
    <BANKMSGSRSV1>
        <STMTTRNRS>
            <STMTRS>
                <BANKACCTFROM>
                    <BANKID>341
                    <ACCTID>12345-6
                    <ACCTTYPE>CHECKING
                </BANKACCTFROM>
                <BANKTRANLIST>
                    <DTSTART>20260501000000
                    <DTEND>20260531120000
                    <STMTTRN>
                        <TRNTYPE>CREDIT
                        <DTPOSTED>20260510103000
                        <TRNAMT>150.50
                        <FITID>TXN-001
                        <MEMO>Oferta culto
                    </STMTTRN>
                    <STMTTRN>
                        <TRNTYPE>DEBIT
                        <DTPOSTED>20260511120000
                        <TRNAMT>-45.90
                        <FITID>TXN-002
                        <CHECKNUM>9988
                        <MEMO>Tarifa bancaria
                    </STMTTRN>
                </BANKTRANLIST>
                <LEDGERBAL>
                    <BALAMT>104.60
                    <DTASOF>20260531120000
                </LEDGERBAL>
            </STMTRS>
        </STMTTRNRS>
    </BANKMSGSRSV1>
</OFX>
"""

        def test_parse_ofx_retorna_metadados_e_transacoes(self):
                resultado = self.service.parse(self.ofx_content)

                self.assertEqual(resultado['banco_id'], '341')
                self.assertEqual(resultado['conta_id'], '12345-6')
                self.assertEqual(resultado['tipo_conta'], 'CHECKING')
                self.assertEqual(resultado['saldo_final'], Decimal('104.60'))
                self.assertEqual(len(resultado['transacoes']), 2)

        def test_parse_ofx_classifica_entrada_e_saida(self):
                resultado = self.service.parse(self.ofx_content)

                self.assertEqual(resultado['transacoes'][0]['tipo'], 'entrada')
                self.assertEqual(resultado['transacoes'][0]['valor'], Decimal('150.50'))
                self.assertEqual(resultado['transacoes'][1]['tipo'], 'saida')
                self.assertEqual(resultado['transacoes'][1]['valor'], Decimal('-45.90'))
                self.assertEqual(resultado['transacoes'][1]['documento'], '9988')

        def test_parse_ofx_invalido_dispara_erro(self):
                with self.assertRaises(ValueError):
                        self.service.parse('arquivo invalido')


class RecorrenciaContaPagarServiceTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Recorrencia',
            ativo=True,
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Recorrencia',
        )
        self.conta_principal = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Caixa Principal Recorrencia',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('100.00'),
            is_principal=True,
        )
        self.service = RecorrenciaContaPagarService()

    def test_gerar_competencia_cria_conta_e_ajusta_ultimo_dia_mes(self):
        recorrencia = RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Internet Matriz',
            valor=Decimal('199.90'),
            dia_vencimento=31,
            data_inicio=date(2026, 1, 1),
            conta_debito_padrao=self.conta_principal,
            forma_pagamento_padrao='PIX',
            usuario_criacao=self.user,
        )

        resultado = self.service.gerar_competencia(competencia='2026-02')

        self.assertEqual(resultado['total_geradas'], 1)
        self.assertEqual(resultado['total_existentes'], 0)
        conta = ContaPagar.objects.get(recorrencia_origem=recorrencia, competencia='2026-02')
        self.assertEqual(conta.data_vencimento, date(2026, 2, 28))
        self.assertEqual(conta.data_emissao, date(2026, 2, 1))
        self.assertTrue(conta.criado_automaticamente)
        recorrencia.refresh_from_db()
        self.assertEqual(recorrencia.ultima_competencia_gerada, '2026-02')

    def test_gerar_competencia_e_idempotente(self):
        recorrencia = RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Aluguel templo',
            valor=Decimal('1500.00'),
            dia_vencimento=10,
            data_inicio=date(2026, 1, 1),
            conta_debito_padrao=self.conta_principal,
            usuario_criacao=self.user,
        )

        primeiro = self.service.gerar_competencia(competencia='2026-05')
        segundo = self.service.gerar_competencia(competencia='2026-05')

        self.assertEqual(primeiro['total_geradas'], 1)
        self.assertEqual(segundo['total_geradas'], 0)
        self.assertEqual(segundo['total_existentes'], 1)
        conta = ContaPagar.objects.get(recorrencia_origem=recorrencia, competencia='2026-05')
        self.assertEqual(ContaPagar.objects.filter(recorrencia_origem=recorrencia, competencia='2026-05').count(), 1)
        self.assertEqual(
            ContaPagarAutorizacaoEvento.objects.filter(
                conta_pagar=conta,
                event_type=ContaPagarAutorizacaoEvento.EVENT_CREATED,
            ).count(),
            1,
        )

    def test_gerar_competencia_trata_validation_error_de_duplicidade_como_existente(self):
        recorrencia = RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Duplicidade concorrente por validacao',
            valor=Decimal('1500.00'),
            dia_vencimento=10,
            data_inicio=date(2026, 1, 1),
            conta_debito_padrao=self.conta_principal,
            usuario_criacao=self.user,
        )

        precheck = MagicMock()
        precheck.exists.return_value = False
        postcheck = MagicMock()
        postcheck.exists.return_value = True

        with patch(
            'financeiro.services.ContaPagar.objects.filter',
            side_effect=[precheck, postcheck],
        ) as filter_mock:
            with patch(
                'financeiro.services.create_payable',
                side_effect=ValidationError('Duplicidade concorrente simulada.'),
            ):
                resultado = self.service.gerar_competencia(competencia='2026-05')

        self.assertEqual(filter_mock.call_count, 2)
        filter_mock.assert_has_calls([
            call(recorrencia_origem=recorrencia, competencia='2026-05'),
            call(recorrencia_origem=recorrencia, competencia='2026-05'),
        ])
        self.assertEqual(resultado['total_geradas'], 0)
        self.assertEqual(resultado['total_existentes'], 1)
        self.assertEqual(resultado['total_erros'], 0)
        self.assertEqual(ContaPagar.objects.count(), 0)

    def test_gerar_competencia_propagates_non_duplicate_validation_error(self):
        RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Erro de validacao real',
            valor=Decimal('1500.00'),
            dia_vencimento=10,
            data_inicio=date(2026, 1, 1),
            conta_debito_padrao=self.conta_principal,
            usuario_criacao=self.user,
        )

        with patch(
            'financeiro.services.create_payable',
            side_effect=ValidationError('Erro de validacao real.'),
        ):
            with self.assertRaisesRegex(ValidationError, 'Erro de validacao real'):
                self.service.gerar_competencia(competencia='2026-05')

        self.assertEqual(ContaPagar.objects.count(), 0)

    def test_gerar_competencia_classifica_com_policy_simples_e_evento_sem_ator(self):
        recorrencia = RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Internet classificada simples',
            valor=Decimal('199.90'),
            dia_vencimento=10,
            data_inicio=date(2026, 1, 1),
            conta_debito_padrao=self.conta_principal,
            usuario_criacao=self.user,
        )

        self.service.gerar_competencia(competencia='2026-06')

        conta = ContaPagar.objects.get(recorrencia_origem=recorrencia, competencia='2026-06')
        event = ContaPagarAutorizacaoEvento.objects.get(conta_pagar=conta)
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_NOT_REQUIRED)
        self.assertEqual(conta.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED)
        self.assertTrue(conta.current_material_fingerprint)
        self.assertEqual(event.event_type, ContaPagarAutorizacaoEvento.EVENT_CREATED)
        self.assertIsNone(event.actor)

    def test_gerar_competencia_classifica_com_policy_exigindo_aprovacao(self):
        PoliticaFinanceiraIgreja.objects.filter(igreja=self.igreja).update(
            approval_required=True,
            segregation_level=PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED,
        )
        recorrencia = RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Internet classificada pendente',
            valor=Decimal('199.90'),
            dia_vencimento=10,
            data_inicio=date(2026, 1, 1),
            conta_debito_padrao=self.conta_principal,
            usuario_criacao=self.user,
        )

        self.service.gerar_competencia(competencia='2026-07')

        conta = ContaPagar.objects.get(recorrencia_origem=recorrencia, competencia='2026-07')
        event = ContaPagarAutorizacaoEvento.objects.get(conta_pagar=conta)
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(conta.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED)
        self.assertEqual(event.event_type, ContaPagarAutorizacaoEvento.EVENT_CREATED)
        self.assertIsNone(event.actor)

    def test_gerar_competencia_usa_policy_vigente_sem_reclassificar_competencia_anterior(self):
        recorrencia = RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Internet policy por competencia',
            valor=Decimal('199.90'),
            dia_vencimento=10,
            data_inicio=date(2026, 1, 1),
            conta_debito_padrao=self.conta_principal,
            usuario_criacao=self.user,
        )

        self.service.gerar_competencia(competencia='2026-08')
        primeira = ContaPagar.objects.get(recorrencia_origem=recorrencia, competencia='2026-08')
        PoliticaFinanceiraIgreja.objects.filter(igreja=self.igreja).update(
            approval_required=True,
            segregation_level=PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED,
        )

        self.service.gerar_competencia(competencia='2026-09')

        primeira.refresh_from_db()
        segunda = ContaPagar.objects.get(recorrencia_origem=recorrencia, competencia='2026-09')
        self.assertEqual(primeira.authorization_status, ContaPagar.AUTHORIZATION_NOT_REQUIRED)
        self.assertEqual(segunda.authorization_status, ContaPagar.AUTHORIZATION_PENDING)

    def test_gerar_competencia_respeita_janela_de_inicio_e_fim(self):
        RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Manutencao som',
            valor=Decimal('300.00'),
            dia_vencimento=5,
            data_inicio=date(2026, 6, 1),
            data_fim=date(2026, 6, 30),
            conta_debito_padrao=self.conta_principal,
            usuario_criacao=self.user,
        )

        resultado = self.service.gerar_competencia(competencia='2026-05')

        self.assertEqual(resultado['total_avaliadas'], 1)
        self.assertEqual(resultado['total_ignoradas'], 1)
        self.assertEqual(resultado['total_geradas'], 0)
        self.assertEqual(ContaPagar.objects.count(), 0)

    def test_gerar_competencia_dry_run_nao_persiste(self):
        RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Limpeza templo',
            valor=Decimal('120.00'),
            dia_vencimento=7,
            data_inicio=date(2026, 1, 1),
            conta_debito_padrao=self.conta_principal,
            usuario_criacao=self.user,
        )

        resultado = self.service.gerar_competencia(competencia='2026-05', dry_run=True)

        self.assertTrue(resultado['dry_run'])
        self.assertEqual(resultado['total_geradas'], 1)
        self.assertEqual(ContaPagar.objects.count(), 0)


class ContaPagarMaterialFingerprintRefreshServiceTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Refresh Fingerprint',
        )

    def test_refresh_atribui_fingerprint_sem_persistir_automaticamente(self):
        conta = ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            descricao='Conta para refresh puro',
            valor=Decimal('10.00'),
            data_emissao=date(2026, 10, 10),
            data_vencimento=date(2026, 10, 20),
        )
        expected = compute_payable_material_fingerprint_v1(
            build_payable_material_snapshot_v1(conta),
        )

        fingerprint = refresh_payable_material_fingerprint(conta)

        self.assertEqual(fingerprint, expected)
        self.assertEqual(conta.current_material_fingerprint, expected)
        self.assertIsNone(ContaPagar.objects.get(pk=conta.pk).current_material_fingerprint)
        self.assertFalse(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta).exists())


class ContaPagarAdminCreationIntegrationTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save(update_fields=['is_staff', 'is_superuser'])
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Admin Creation',
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Admin Creation',
        )
        self.client.force_login(self.user)

    def _payload(self, descricao):
        return {
            'ministerio': str(self.ministerio.pk),
            'igreja': str(self.igreja.pk),
            'fornecedor': str(self.fornecedor.pk),
            'categoria': str(self.categoria.pk),
            'descricao': descricao,
            'numero_documento': 'NF-ADMIN-123',
            'valor': '100.00',
            'data_emissao': '2026-10-10',
            'data_vencimento': '2026-10-20',
            'conta_debito': '',
            'forma_pagamento': '',
            'recorrencia_origem': '',
            'competencia': '',
            'criado_automaticamente': '',
            'observacoes': 'Conta criada pelo Admin para teste.',
            'usuario_criacao': '',
        }

    def test_admin_add_classifica_policy_simples_sem_criacao_duplicada(self):
        response = self.client.post(
            reverse('admin:financeiro_contapagar_add'),
            data=self._payload('Conta Admin Simples'),
        )

        self.assertEqual(response.status_code, 302)
        conta = ContaPagar.objects.get(descricao='Conta Admin Simples')
        event = ContaPagarAutorizacaoEvento.objects.get(conta_pagar=conta)
        self.assertEqual(ContaPagar.objects.filter(descricao='Conta Admin Simples').count(), 1)
        self.assertEqual(
            ContaPagarAutorizacaoEvento.objects.filter(
                conta_pagar=conta,
                event_type=ContaPagarAutorizacaoEvento.EVENT_CREATED,
            ).count(),
            1,
        )
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_NOT_REQUIRED)
        self.assertEqual(conta.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED)
        self.assertTrue(conta.current_material_fingerprint)
        self.assertEqual(event.actor, self.user)
        self.assertEqual(conta.usuario_criacao, self.user)

    def test_admin_add_classifica_policy_exigindo_aprovacao(self):
        PoliticaFinanceiraIgreja.objects.filter(igreja=self.igreja).update(
            approval_required=True,
            segregation_level=PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED,
        )

        response = self.client.post(
            reverse('admin:financeiro_contapagar_add'),
            data=self._payload('Conta Admin Pendente'),
        )

        self.assertEqual(response.status_code, 302)
        conta = ContaPagar.objects.get(descricao='Conta Admin Pendente')
        event = ContaPagarAutorizacaoEvento.objects.get(conta_pagar=conta)
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(conta.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED)
        self.assertEqual(event.actor, self.user)

    def test_admin_change_nao_cria_nova_conta_nem_evento_created(self):
        conta = create_payable(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Conta Admin Existente',
            valor=Decimal('100.00'),
            data_emissao=date(2026, 10, 10),
            data_vencimento=date(2026, 10, 20),
            actor=self.user,
        )
        payload = self._payload('Conta Admin Existente')
        payload['numero_documento'] = 'NF-ADMIN-EDITADA'
        payload['usuario_criacao'] = ''
        payload.update({
            'status': conta.status,
            'data_pagamento_0': '',
            'data_pagamento_1': '',
            'valor_pago': '',
            'juros_multa': '0.00',
            'desconto': '0.00',
            'authorization_status': conta.authorization_status,
            'authorization_origin': conta.authorization_origin,
            'authorization_policy_version': str(conta.authorization_policy_version),
            'current_material_fingerprint': 'v1:sha256:' + ('0' * 64),
            'approved_material_fingerprint': '',
            'approved_by': '',
            'approved_at_0': '',
            'approved_at_1': '',
            'rejected_by': '',
            'rejected_at_0': '',
            'rejected_at_1': '',
            'current_rejection_reason': '',
        })

        response = self.client.post(
            reverse('admin:financeiro_contapagar_change', args=[conta.pk]),
            data=payload,
        )

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        self.assertEqual(conta.descricao, 'Conta Admin Existente')
        self.assertEqual(conta.numero_documento, 'NF-ADMIN-EDITADA')
        expected_fingerprint = compute_payable_material_fingerprint_v1(
            build_payable_material_snapshot_v1(conta),
        )
        self.assertEqual(conta.current_material_fingerprint, expected_fingerprint)
        self.assertNotEqual(conta.current_material_fingerprint, 'v1:sha256:' + ('0' * 64))
        self.assertEqual(ContaPagar.objects.count(), 1)
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta).count(), 1)
        self.assertEqual(
            ContaPagarAutorizacaoEvento.objects.filter(
                conta_pagar=conta,
                event_type=ContaPagarAutorizacaoEvento.EVENT_CREATED,
            ).count(),
            1,
        )

    def test_admin_change_heals_null_current_fingerprint_without_new_event(self):
        conta = ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Conta Admin Legada',
            valor=Decimal('100.00'),
            data_emissao=date(2026, 10, 10),
            data_vencimento=date(2026, 10, 20),
            authorization_status=ContaPagar.AUTHORIZATION_PENDING,
            authorization_origin=ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED,
            authorization_policy_version=3,
        )
        payload = self._payload('Conta Admin Legada Editada')
        payload['usuario_criacao'] = ''
        payload.update({
            'status': conta.status,
            'data_pagamento_0': '',
            'data_pagamento_1': '',
            'valor_pago': '',
            'juros_multa': '0.00',
            'desconto': '0.00',
            'authorization_status': conta.authorization_status,
            'authorization_origin': conta.authorization_origin,
            'authorization_policy_version': str(conta.authorization_policy_version),
            'current_material_fingerprint': '',
            'approved_material_fingerprint': '',
            'approved_by': '',
            'approved_at_0': '',
            'approved_at_1': '',
            'rejected_by': '',
            'rejected_at_0': '',
            'rejected_at_1': '',
            'current_rejection_reason': '',
        })

        response = self.client.post(
            reverse('admin:financeiro_contapagar_change', args=[conta.pk]),
            data=payload,
        )

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(conta.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED)
        self.assertEqual(conta.authorization_policy_version, 3)
        self.assertEqual(
            conta.current_material_fingerprint,
            compute_payable_material_fingerprint_v1(build_payable_material_snapshot_v1(conta)),
        )
        self.assertFalse(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta).exists())


class ContaPagarAdminSensitiveFieldsHardeningTest(BaseFinanceiroTestCase):
    authorization_sensitive_fields = (
        'authorization_status',
        'authorization_origin',
        'authorization_policy_version',
        'current_material_fingerprint',
        'approved_material_fingerprint',
        'approved_by',
        'approved_at',
        'rejected_by',
        'rejected_at',
        'current_rejection_reason',
    )
    payment_sensitive_fields = (
        'status',
        'data_pagamento',
        'valor_pago',
        'juros_multa',
        'desconto',
        'comprovante',
        'forma_pagamento',
        'conta_debito',
    )
    provenance_fields = (
        'usuario_criacao',
        'criado_automaticamente',
        'recorrencia_origem',
    )
    change_readonly_fields = (
        'ministerio',
        'igreja',
        'fornecedor',
        'categoria',
        'descricao',
        'valor',
        'data_vencimento',
        'competencia',
    )

    def setUp(self):
        super().setUp()
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save(update_fields=['is_staff', 'is_superuser'])
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Admin Sensitive Fields',
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Admin Sensitive Fields',
        )
        self.conta_debito = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Conta Debito Admin Sensitive Fields',
            tipo='caixa_fisico',
        )
        self.other_user = get_user_model().objects.create_user(
            username='outro_criador_admin_sensitive',
            password='senha123',
        )
        self.other_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministerio Admin Sensitive Fields',
            administrador_principal=self.other_user,
            ativo=True,
            cnpj='98765432000199',
        )
        self.other_igreja = Igreja.objects.create(
            nome_igreja='Outra Igreja Admin Sensitive Fields',
            ministerio=self.other_ministerio,
            tipo_igreja='sede',
        )
        self.other_fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Outro Fornecedor Admin Sensitive Fields',
        )
        self.other_categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Outra Categoria Admin Sensitive Fields',
        )
        self.recorrencia = RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Recorrencia Admin Sensitive Fields',
            valor=Decimal('100.00'),
            dia_vencimento=20,
            usuario_criacao=self.other_user,
        )
        self.other_recorrencia = RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.other_fornecedor,
            categoria=self.other_categoria,
            descricao='Outra Recorrencia Admin Sensitive Fields',
            valor=Decimal('200.00'),
            dia_vencimento=25,
            usuario_criacao=self.other_user,
        )
        self.client.force_login(self.user)

    def _admin(self):
        return admin.site._registry[ContaPagar]

    def _payload(self, descricao):
        return {
            'ministerio': str(self.ministerio.pk),
            'igreja': str(self.igreja.pk),
            'fornecedor': str(self.fornecedor.pk),
            'categoria': str(self.categoria.pk),
            'descricao': descricao,
            'numero_documento': 'NF-ADMIN-SENSITIVE-123',
            'valor': '100.00',
            'data_emissao': '2026-10-10',
            'data_vencimento': '2026-10-20',
            'recorrencia_origem': '',
            'competencia': '',
            'criado_automaticamente': '',
            'observacoes': 'Edicao administrativa normal.',
            'usuario_criacao': '',
        }

    def _malicious_authorization_payload(self):
        return {
            'authorization_status': ContaPagar.AUTHORIZATION_REJECTED,
            'authorization_origin': ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED,
            'authorization_policy_version': '999',
            'current_material_fingerprint': 'v1:sha256:' + ('0' * 64),
            'approved_material_fingerprint': 'v1:sha256:' + ('1' * 64),
            'approved_by': str(self.user.pk),
            'approved_at_0': '2026-10-21',
            'approved_at_1': '10:00:00',
            'rejected_by': str(self.user.pk),
            'rejected_at_0': '2026-10-21',
            'rejected_at_1': '10:00:00',
            'current_rejection_reason': 'Payload administrativo adulterado.',
        }

    def _malicious_payment_payload(self):
        return {
            'status': 'PAG',
            'data_pagamento': '2026-10-21',
            'valor_pago': '999.99',
            'juros_multa': '12.34',
            'desconto': '5.67',
            'comprovante': 'comprovante-adulterado.pdf',
            'forma_pagamento': 'PIX',
            'conta_debito': str(self.conta_debito.pk),
        }

    def _create_payable(self, descricao='Conta Admin Sensitive Fields'):
        return create_payable(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao=descricao,
            valor=Decimal('100.00'),
            data_emissao=date(2026, 10, 10),
            data_vencimento=date(2026, 10, 20),
            actor=self.user,
        )

    def _malicious_provenance_payload(self):
        return {
            'usuario_criacao': str(self.other_user.pk),
            'criado_automaticamente': 'on',
            'recorrencia_origem': str(self.other_recorrencia.pk),
            'competencia': '2026-11',
        }

    def test_admin_forms_differentiate_add_and_change_safe_surfaces(self):
        model_admin = self._admin()
        request = self.factory.get('/admin/financeiro/contapagar/')
        request.user = self.user
        change_fields = model_admin.get_form(request, ContaPagar()).base_fields
        add_fields = model_admin.get_form(request, None).base_fields

        for field_name in self.authorization_sensitive_fields + self.payment_sensitive_fields + self.provenance_fields:
            self.assertNotIn(field_name, change_fields)
            self.assertNotIn(field_name, add_fields)

        for field_name in (
            'ministerio', 'igreja', 'fornecedor', 'categoria', 'descricao', 'numero_documento', 'valor',
            'data_emissao', 'data_vencimento', 'competencia', 'observacoes',
        ):
            self.assertIn(field_name, add_fields)

        for field_name in self.change_readonly_fields:
            self.assertNotIn(field_name, change_fields)

        for field_name in ('numero_documento', 'data_emissao', 'observacoes'):
            self.assertIn(field_name, change_fields)

    def test_admin_change_post_cannot_mutate_authorization_internals(self):
        conta = self._create_payable()
        approved_at = timezone.now()
        rejected_at = approved_at + timedelta(minutes=1)
        ContaPagar.objects.filter(pk=conta.pk).update(
            authorization_status=ContaPagar.AUTHORIZATION_APPROVED,
            authorization_origin=ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED,
            authorization_policy_version=7,
            approved_material_fingerprint='v1:sha256:' + ('a' * 64),
            approved_by=self.user,
            approved_at=approved_at,
            rejected_by=self.user,
            rejected_at=rejected_at,
            current_rejection_reason='Motivo historico preservado.',
        )
        conta.refresh_from_db()
        expected = {
            field_name: getattr(conta, field_name)
            for field_name in self.authorization_sensitive_fields
            if field_name != 'current_material_fingerprint'
        }
        payload = self._payload('Conta Admin Authorization Preservada')
        payload.update(self._malicious_authorization_payload())

        response = self.client.post(
            reverse('admin:financeiro_contapagar_change', args=[conta.pk]),
            data=payload,
        )

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        self.assertEqual(conta.descricao, 'Conta Admin Sensitive Fields')
        for field_name, value in expected.items():
            self.assertEqual(getattr(conta, field_name), value)
        self.assertNotEqual(conta.current_material_fingerprint, payload['current_material_fingerprint'])
        self.assertEqual(
            conta.current_material_fingerprint,
            compute_payable_material_fingerprint_v1(build_payable_material_snapshot_v1(conta)),
        )

    def test_admin_change_post_cannot_mutate_payment_internals_or_create_expense(self):
        conta = self._create_payable()
        expected = {
            'status': conta.status,
            'data_pagamento': conta.data_pagamento,
            'valor_pago': conta.valor_pago,
            'juros_multa': conta.juros_multa,
            'desconto': conta.desconto,
            'comprovante': conta.comprovante.name or '',
            'forma_pagamento': conta.forma_pagamento,
            'conta_debito_id': conta.conta_debito_id,
        }
        payload = self._payload('Conta Admin Payment Preservada')
        payload.update(self._malicious_payment_payload())

        response = self.client.post(
            reverse('admin:financeiro_contapagar_change', args=[conta.pk]),
            data=payload,
        )

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        self.assertEqual(conta.descricao, 'Conta Admin Sensitive Fields')
        self.assertEqual(conta.status, expected['status'])
        self.assertEqual(conta.data_pagamento, expected['data_pagamento'])
        self.assertEqual(conta.valor_pago, expected['valor_pago'])
        self.assertEqual(conta.juros_multa, expected['juros_multa'])
        self.assertEqual(conta.desconto, expected['desconto'])
        self.assertEqual(conta.comprovante.name, expected['comprovante'])
        self.assertEqual(conta.forma_pagamento, expected['forma_pagamento'])
        self.assertEqual(conta.conta_debito_id, expected['conta_debito_id'])
        self.assertNotEqual(conta.status, 'PAG')
        self.assertFalse(Despesas.objects.filter(origem_conta_pagar=conta).exists())

    def test_admin_change_post_cannot_mutate_tenant_provenance_material_or_category_fields(self):
        conta = self._create_payable()
        conta.usuario_criacao = self.user
        conta.recorrencia_origem = self.recorrencia
        conta.competencia = '2026-10'
        conta.criado_automaticamente = True
        conta.save(update_fields=[
            'usuario_criacao', 'recorrencia_origem', 'competencia', 'criado_automaticamente',
        ])
        expected = {
            'ministerio_id': conta.ministerio_id,
            'igreja_id': conta.igreja_id,
            'fornecedor_id': conta.fornecedor_id,
            'categoria_id': conta.categoria_id,
            'descricao': conta.descricao,
            'valor': conta.valor,
            'data_vencimento': conta.data_vencimento,
            'usuario_criacao_id': conta.usuario_criacao_id,
            'criado_automaticamente': conta.criado_automaticamente,
            'recorrencia_origem_id': conta.recorrencia_origem_id,
            'competencia': conta.competencia,
        }
        payload = self._payload('Conta Admin Material Adulterada')
        payload.update({
            'ministerio': str(self.other_ministerio.pk),
            'igreja': str(self.other_igreja.pk),
            'fornecedor': str(self.other_fornecedor.pk),
            'categoria': str(self.other_categoria.pk),
            'valor': '999.99',
            'data_vencimento': '2026-11-20',
        })
        payload.update(self._malicious_provenance_payload())

        response = self.client.post(
            reverse('admin:financeiro_contapagar_change', args=[conta.pk]),
            data=payload,
        )

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        for field_name, value in expected.items():
            self.assertEqual(getattr(conta, field_name), value)

    def test_admin_change_keeps_safe_nonmaterial_edit_working(self):
        conta = self._create_payable()
        payload = self._payload(conta.descricao)
        payload['numero_documento'] = 'NF-ADMIN-SAFE-EDIT-456'

        response = self.client.post(
            reverse('admin:financeiro_contapagar_change', args=[conta.pk]),
            data=payload,
        )

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        self.assertEqual(conta.numero_documento, 'NF-ADMIN-SAFE-EDIT-456')

    def test_admin_add_ignores_sensitive_payload_and_uses_create_payable(self):
        payload = self._payload('Conta Admin Add Protegida')
        payload.update(self._malicious_authorization_payload())
        payload.update(self._malicious_payment_payload())
        payload.update(self._malicious_provenance_payload())

        with patch('financeiro.admin_contas.create_payable', wraps=create_payable) as create_payable_mock:
            response = self.client.post(
                reverse('admin:financeiro_contapagar_add'),
                data=payload,
            )

        self.assertEqual(response.status_code, 302)
        create_payable_mock.assert_called_once()
        self.assertEqual(create_payable_mock.call_args.kwargs['usuario_criacao'], self.user)
        self.assertFalse(create_payable_mock.call_args.kwargs['criado_automaticamente'])
        self.assertIsNone(create_payable_mock.call_args.kwargs['recorrencia_origem'])
        conta = ContaPagar.objects.get(descricao='Conta Admin Add Protegida')
        self.assertNotEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_REJECTED)
        self.assertNotEqual(conta.authorization_policy_version, 999)
        self.assertNotEqual(conta.current_material_fingerprint, payload['current_material_fingerprint'])
        self.assertNotEqual(conta.status, 'PAG')
        self.assertIsNone(conta.data_pagamento)
        self.assertIsNone(conta.valor_pago)
        self.assertEqual(conta.usuario_criacao, self.user)
        self.assertFalse(conta.criado_automaticamente)
        self.assertIsNone(conta.recorrencia_origem)
        self.assertFalse(Despesas.objects.filter(origem_conta_pagar=conta).exists())


class RecorrenciaContaPagarFormTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Form Recorrencia',
            ativo=True,
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Form Recorrencia',
        )
        self.conta_principal = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Caixa Principal Form',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('100.00'),
            is_principal=True,
        )
        self.conta_secundaria = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Conta Secundaria Form',
            tipo='bancaria',
            saldo_inicial=Decimal('50.00'),
        )

    def test_preseleciona_conta_padrao_despesas(self):
        self.igreja.conta_padrao_despesas = self.conta_secundaria
        self.igreja.save(update_fields=['conta_padrao_despesas'])

        form = RecorrenciaContaPagarForm(
            ministerio=self.ministerio,
            user=self.user,
            allowed_churches=Igreja.objects.filter(pk=self.igreja.pk),
            igreja_selecionada_inicial=self.igreja,
        )

        self.assertEqual(form.initial.get('conta_debito_padrao'), self.conta_secundaria)

    def test_fallback_caixa_principal_quando_sem_conta_padrao(self):
        self.igreja.conta_padrao_despesas = None
        self.igreja.conta_padrao_receitas = None
        self.igreja.save(update_fields=['conta_padrao_despesas', 'conta_padrao_receitas'])

        form = RecorrenciaContaPagarForm(
            ministerio=self.ministerio,
            user=self.user,
            allowed_churches=Igreja.objects.filter(pk=self.igreja.pk),
            igreja_selecionada_inicial=self.igreja,
        )

        conta_inicial = form.initial.get('conta_debito_padrao')
        self.assertIsNotNone(conta_inicial)
        self.assertEqual(conta_inicial.igreja_id, self.igreja.id)
        self.assertTrue(conta_inicial.is_principal)

    def test_conta_debito_padrao_fica_restrita_a_igreja_ativa(self):
        outra_igreja = Igreja.objects.create(
            nome_igreja='Igreja Secundaria Form',
            ministerio=self.ministerio,
            tipo_igreja='congregacao',
        )
        conta_outra_igreja = ContaBancaria.objects.create(
            igreja=outra_igreja,
            nome_identificacao='Caixa Outra Igreja',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('10.00'),
        )

        form = RecorrenciaContaPagarForm(
            ministerio=self.ministerio,
            user=self.user,
            allowed_churches=Igreja.objects.filter(pk=self.igreja.pk),
            igreja_selecionada_inicial=self.igreja,
        )

        ids_queryset = set(form.fields['conta_debito_padrao'].queryset.values_list('id', flat=True))
        self.assertIn(self.conta_principal.id, ids_queryset)
        self.assertIn(self.conta_secundaria.id, ids_queryset)
        self.assertNotIn(conta_outra_igreja.id, ids_queryset)


class RecorrenciaFluxoPagamentoIntegracaoTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.perfil, _ = PerfilUsuario.objects.get_or_create(
            user=self.user,
            defaults={'ministerio': self.ministerio},
        )
        if self.perfil.ministerio_id != self.ministerio.id:
            self.perfil.ministerio = self.ministerio
            self.perfil.save(update_fields=['ministerio'])
        self.perfil.igrejas_permitidas.set([self.igreja])

        grupo_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)
        self.user.groups.add(grupo_tesoureiro)

        self.client.force_login(self.user)
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Integracao Recorrencia',
            ativo=True,
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Integracao Recorrencia',
        )
        self.conta = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Conta Integracao Recorrencia',
            tipo='bancaria',
            saldo_inicial=Decimal('1000.00'),
            is_principal=True,
        )
        self.service = RecorrenciaContaPagarService()

    def test_fluxo_gerou_pagou_criou_despesa(self):
        recorrencia = RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Internet Integracao',
            valor=Decimal('200.00'),
            dia_vencimento=10,
            data_inicio=date(2026, 1, 1),
            conta_debito_padrao=self.conta,
            forma_pagamento_padrao='PIX',
            usuario_criacao=self.user,
        )

        self.service.gerar_competencia(competencia='2026-05', igreja_id=self.igreja.id)

        conta_pagar = ContaPagar.objects.get(recorrencia_origem=recorrencia, competencia='2026-05')
        self.assertEqual(conta_pagar.status, 'PEN')
        self.assertTrue(conta_pagar.criado_automaticamente)

        session = self.client.session
        session['igreja_ativa_id'] = self.igreja.pk
        session.save()

        response = self.client.post(
            reverse('financeiro:registrar_pagamento_conta_pagar', args=[conta_pagar.id]),
            data={
                'data_pagamento': '2026-05-10',
                'valor_pago': '200.00',
                'juros_multa': '5.00',
                'desconto': '10.00',
                'conta_debito': str(self.conta.id),
                'forma_pagamento': 'PIX',
            },
        )

        self.assertEqual(response.status_code, 302)

        conta_pagar.refresh_from_db()
        self.assertEqual(conta_pagar.status, 'PAG')
        self.assertEqual(conta_pagar.valor_pago, Decimal('200.00'))

        despesa = Despesas.objects.get(origem_conta_pagar=conta_pagar)
        self.assertEqual(despesa.igreja_id, self.igreja.id)
        self.assertEqual(despesa.categoria_id, self.categoria.id)
        self.assertEqual(despesa.usuario_registro_pagamento, self.user)
        self.assertEqual(despesa.criado_por, self.user)
        self.assertEqual(despesa.conta_bancaria_id, self.conta.id)
        self.assertEqual(despesa.valor, Decimal('195.00'))
        self.assertEqual(despesa.usuario_registro_pagamento_id, self.user.id)


class RecorrenciaPermissoesViewTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.perfil, _ = PerfilUsuario.objects.get_or_create(
            user=self.user,
            defaults={'ministerio': self.ministerio},
        )
        if self.perfil.ministerio_id != self.ministerio.id:
            self.perfil.ministerio = self.ministerio
            self.perfil.save(update_fields=['ministerio'])
        self.perfil.igrejas_permitidas.set([self.igreja])
        self.client.force_login(self.user)
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja.id
        session.save()

        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Permissoes',
            ativo=True,
        )
        self.recorrencia = RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            descricao='Recorrencia Permissao',
            valor=Decimal('100.00'),
            dia_vencimento=5,
            data_inicio=date(2026, 1, 1),
            usuario_criacao=self.user,
        )

    def test_criar_recorrencia_sem_permissao_de_edicao_lanca_erro(self):
        request = self.factory.get(reverse('financeiro:criar_recorrencia_conta_pagar'))
        request.user = self.user
        request.session = {}
        request.igreja_ativa = self.igreja

        with patch('contas.page_permissions.user_can_access_page', return_value=True), patch(
            'financeiro.views.has_finance_edit_permission', return_value=False
        ):
            with self.assertRaises(PermissionDenied):
                criar_recorrencia_conta_pagar(request)

    def test_editar_recorrencia_sem_permissao_de_edicao_lanca_erro(self):
        request = self.factory.get(
            reverse('financeiro:editar_recorrencia_conta_pagar', args=[self.recorrencia.id])
        )
        request.user = self.user
        request.session = {}
        request.igreja_ativa = self.igreja

        with patch('contas.page_permissions.user_can_access_page', return_value=True), patch(
            'financeiro.views.has_finance_edit_permission', return_value=False
        ):
            with self.assertRaises(PermissionDenied):
                editar_recorrencia_conta_pagar(request, self.recorrencia.id)

    def test_gerar_despesas_fixas_sem_permissao_de_edicao_lanca_erro(self):
        request = self.factory.post(reverse('financeiro:gerar_despesas_fixas_mes'))
        request.user = self.user
        request.session = {}
        request.igreja_ativa = self.igreja

        with patch('contas.page_permissions.user_can_access_page', return_value=True), patch(
            'financeiro.views.has_finance_edit_permission', return_value=False
        ):
            with self.assertRaises(PermissionDenied):
                gerar_despesas_fixas_mes(request)

    def test_criar_recorrencia_com_permissao_de_edicao_renderiza_formulario(self):
        with patch('contas.page_permissions.user_can_access_page', return_value=True), patch(
            'financeiro.views.has_finance_edit_permission', return_value=True
        ):
            response = self.client.get(reverse('financeiro:criar_recorrencia_conta_pagar'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'financeiro/recorrencias_contas_pagar/form_recorrencia.html')

    def test_editar_recorrencia_com_permissao_de_edicao_renderiza_formulario(self):
        with patch('contas.page_permissions.user_can_access_page', return_value=True), patch(
            'financeiro.views.has_finance_edit_permission', return_value=True
        ):
            response = self.client.get(
                reverse('financeiro:editar_recorrencia_conta_pagar', args=[self.recorrencia.id])
            )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'financeiro/recorrencias_contas_pagar/form_recorrencia.html')

    def test_gerar_despesas_fixas_com_permissao_de_edicao_redireciona(self):
        with patch('contas.page_permissions.user_can_access_page', return_value=True), patch(
            'financeiro.views.has_finance_edit_permission', return_value=True
        ):
            response = self.client.post(reverse('financeiro:gerar_despesas_fixas_mes'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('financeiro:lista_contas_pagar'))


class PagamentoLoteContasPagarViewTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.perfil, _ = PerfilUsuario.objects.get_or_create(
            user=self.user,
            defaults={'ministerio': self.ministerio},
        )
        if self.perfil.ministerio_id != self.ministerio.id:
            self.perfil.ministerio = self.ministerio
            self.perfil.save(update_fields=['ministerio'])
        self.perfil.igrejas_permitidas.set([self.igreja])

        grupo_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)
        self.user.groups.add(grupo_tesoureiro)

        self.client.force_login(self.user)
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja.id
        session.save()

        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Lote',
            ativo=True,
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Lote',
        )
        self.conta_debito = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Conta Debito Lote',
            tipo='bancaria',
            saldo_inicial=Decimal('1000.00'),
        )
        self.conta_pendente = ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Conta Lote Pendente',
            valor=Decimal('80.00'),
            data_vencimento=date(2026, 6, 10),
            status='PEN',
        )
        self.conta_vencida = ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao='Conta Lote Vencida',
            valor=Decimal('120.00'),
            data_vencimento=date(2026, 6, 5),
            status='VEN',
        )

    def test_pagamento_lote_processa_contas_selecionadas(self):
        response = self.client.post(
            reverse('financeiro:registrar_pagamento_lote_contas_pagar'),
            data={
                'conta_ids': [str(self.conta_pendente.id), str(self.conta_vencida.id)],
                'data_pagamento_lote': '2026-06-12',
                'conta_debito_lote': str(self.conta_debito.id),
                'forma_pagamento_lote': 'PIX',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('financeiro:lista_contas_pagar'))

        self.conta_pendente.refresh_from_db()
        self.conta_vencida.refresh_from_db()
        self.assertEqual(self.conta_pendente.status, 'PAG')
        self.assertEqual(self.conta_vencida.status, 'PAG')
        self.assertEqual(self.conta_pendente.valor_pago, Decimal('80.00'))
        self.assertEqual(self.conta_vencida.valor_pago, Decimal('120.00'))
        self.assertEqual(self.conta_pendente.conta_debito_id, self.conta_debito.id)
        self.assertEqual(self.conta_vencida.conta_debito_id, self.conta_debito.id)

        despesas_lote = Despesas.objects.filter(origem_conta_pagar__in=[self.conta_pendente, self.conta_vencida])
        self.assertEqual(despesas_lote.count(), 2)
        self.assertTrue(all(despesa.usuario_registro_pagamento_id == self.user.id for despesa in despesas_lote))
        self.assertTrue(all(despesa.criado_por_id == self.user.id for despesa in despesas_lote))

    def test_pagamento_lote_sem_contas_selecionadas_nao_processa(self):
        response = self.client.post(
            reverse('financeiro:registrar_pagamento_lote_contas_pagar'),
            data={
                'data_pagamento_lote': '2026-06-12',
                'conta_debito_lote': str(self.conta_debito.id),
                'forma_pagamento_lote': 'PIX',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('financeiro:lista_contas_pagar'))

        self.conta_pendente.refresh_from_db()
        self.conta_vencida.refresh_from_db()
        self.assertEqual(self.conta_pendente.status, 'PEN')
        self.assertEqual(self.conta_vencida.status, 'VEN')
        self.assertEqual(Despesas.objects.filter(origem_conta_pagar__in=[self.conta_pendente, self.conta_vencida]).count(), 0)


class ContaPagarPaymentAuthorizationHardeningTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_principal = User.objects.create_user(
            username='admin-principal-payment-hardening',
            password='senha123',
        )
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Payment Hardening',
            administrador_principal=self.admin_principal,
            ativo=True,
        )
        self.igreja_a = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja A Payment Hardening',
            tipo_igreja='sede',
        )
        self.igreja_b = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja B Payment Hardening',
            tipo_igreja='independente',
        )
        self.igreja_c = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja C Descendente Payment Hardening',
            tipo_igreja='congregacao',
            igreja_superior=self.igreja_b,
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Payment Hardening',
        )
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Payment Hardening',
            ativo=True,
        )
        self.conta_a = ContaBancaria.objects.create(
            igreja=self.igreja_a,
            nome_identificacao='Caixa A Payment Hardening',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('500.00'),
        )
        self.conta_b = ContaBancaria.objects.create(
            igreja=self.igreja_b,
            nome_identificacao='Caixa B Payment Hardening',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('500.00'),
        )
        for group_name in (ADMIN_MINISTERIO, PASTOR_LOCAL, PASTOR_REGIONAL, TESOUREIRO):
            Group.objects.get_or_create(name=group_name)

    def _criar_usuario(self, username, group_name, igrejas=()):
        user = get_user_model().objects.create_user(username=username, password='senha123')
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        perfil = PerfilUsuario.objects.create(user=user, ministerio=self.ministerio)
        perfil.igrejas_permitidas.set(igrejas)
        return user

    def _autenticar_com_igreja_ativa(self, user, igreja):
        self.client.force_login(user)
        session = self.client.session
        session['igreja_ativa_id'] = igreja.pk
        session.save()

    def _criar_conta_pagar(self, igreja, descricao):
        return ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao=descricao,
            valor=Decimal('100.00'),
            data_vencimento=date(2026, 10, 20),
            status='PEN',
        )

    def _payload_individual(self, conta_bancaria):
        return {
            'data_pagamento': '2026-10-16',
            'valor_pago': '100.00',
            'juros_multa': '0.00',
            'desconto': '0.00',
            'conta_debito': str(conta_bancaria.pk),
            'forma_pagamento': 'PIX',
        }

    def _payload_lote(self, conta, conta_bancaria):
        return {
            'conta_ids': [str(conta.pk)],
            'data_pagamento_lote': '2026-10-16',
            'conta_debito_lote': str(conta_bancaria.pk),
            'forma_pagamento_lote': 'PIX',
        }

    def _assert_pagamento_nao_alterado(self, conta, conta_bancaria):
        conta.refresh_from_db()
        conta_bancaria.refresh_from_db()
        self.assertEqual(conta.status, 'PEN')
        self.assertIsNone(conta.data_pagamento)
        self.assertIsNone(conta.valor_pago)
        self.assertFalse(Despesas.objects.filter(origem_conta_pagar=conta).exists())
        self.assertEqual(conta_bancaria.saldo_atual, Decimal('500.00'))

    def test_admin_sem_write_scope_falha_fechado_no_individual_e_lote(self):
        admin = self._criar_usuario(
            'admin-empty-scope-payment-hardening',
            ADMIN_MINISTERIO,
        )
        conta_individual = self._criar_conta_pagar(self.igreja_a, 'Conta Admin Vazio Individual')
        conta_lote = self._criar_conta_pagar(self.igreja_a, 'Conta Admin Vazio Lote')
        self._autenticar_com_igreja_ativa(admin, self.igreja_a)

        response_individual = self.client.post(
            reverse('financeiro:registrar_pagamento_conta_pagar', args=[conta_individual.pk]),
            data=self._payload_individual(self.conta_a),
        )
        response_lote = self.client.post(
            reverse('financeiro:registrar_pagamento_lote_contas_pagar'),
            data=self._payload_lote(conta_lote, self.conta_a),
        )

        self.assertEqual(response_individual.status_code, 404)
        self.assertEqual(response_lote.status_code, 302)
        self._assert_pagamento_nao_alterado(conta_individual, self.conta_a)
        self._assert_pagamento_nao_alterado(conta_lote, self.conta_a)

    def test_admin_com_write_scope_a_nao_paga_conta_da_igreja_b(self):
        admin = self._criar_usuario(
            'admin-scope-a-payment-hardening',
            ADMIN_MINISTERIO,
            [self.igreja_a],
        )
        conta_b = self._criar_conta_pagar(self.igreja_b, 'Conta B Fora do Escopo Admin')
        self._autenticar_com_igreja_ativa(admin, self.igreja_a)

        response = self.client.post(
            reverse('financeiro:registrar_pagamento_conta_pagar', args=[conta_b.pk]),
            data=self._payload_individual(self.conta_b),
        )

        self.assertEqual(response.status_code, 404)
        self._assert_pagamento_nao_alterado(conta_b, self.conta_b)

    def test_regional_write_scope_nao_expande_para_igreja_descendente(self):
        regional = self._criar_usuario(
            'regional-payment-hardening',
            PASTOR_REGIONAL,
            [self.igreja_b],
        )

        scope_ids = set(get_finance_write_scope(regional, self.ministerio).values_list('pk', flat=True))

        self.assertEqual(scope_ids, {self.igreja_b.pk})
        self.assertNotIn(self.igreja_c.pk, scope_ids)

    def test_pastor_local_no_write_scope_paga_conta_individual(self):
        pastor = self._criar_usuario(
            'pastor-local-payment-hardening',
            PASTOR_LOCAL,
            [self.igreja_a],
        )
        conta = self._criar_conta_pagar(self.igreja_a, 'Conta Pastor Local Autorizada')
        self._autenticar_com_igreja_ativa(pastor, self.igreja_a)

        response = self.client.post(
            reverse('financeiro:registrar_pagamento_conta_pagar', args=[conta.pk]),
            data=self._payload_individual(self.conta_a),
        )

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        self.assertEqual(conta.status, 'PAG')
        self.assertTrue(Despesas.objects.filter(origem_conta_pagar=conta).exists())

    def test_tesoureiro_no_write_scope_paga_individual_e_lote(self):
        tesoureiro = self._criar_usuario(
            'tesoureiro-payment-hardening',
            TESOUREIRO,
            [self.igreja_a],
        )
        conta_individual = self._criar_conta_pagar(self.igreja_a, 'Conta Tesoureiro Individual')
        conta_lote = self._criar_conta_pagar(self.igreja_a, 'Conta Tesoureiro Lote')
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response_individual = self.client.post(
            reverse('financeiro:registrar_pagamento_conta_pagar', args=[conta_individual.pk]),
            data=self._payload_individual(self.conta_a),
        )
        response_lote = self.client.post(
            reverse('financeiro:registrar_pagamento_lote_contas_pagar'),
            data=self._payload_lote(conta_lote, self.conta_a),
        )

        self.assertEqual(response_individual.status_code, 302)
        self.assertEqual(response_lote.status_code, 302)
        conta_individual.refresh_from_db()
        conta_lote.refresh_from_db()
        self.assertEqual(conta_individual.status, 'PAG')
        self.assertEqual(conta_lote.status, 'PAG')
        self.assertTrue(Despesas.objects.filter(origem_conta_pagar=conta_individual).exists())
        self.assertTrue(Despesas.objects.filter(origem_conta_pagar=conta_lote).exists())

    def test_tesoureiro_na_igreja_a_nao_paga_conta_da_igreja_b_individual_ou_lote(self):
        tesoureiro = self._criar_usuario(
            'tesoureiro-cross-church-payment-hardening',
            TESOUREIRO,
            [self.igreja_a],
        )
        conta_individual = self._criar_conta_pagar(self.igreja_b, 'Conta B Cross Church Individual')
        conta_lote = self._criar_conta_pagar(self.igreja_b, 'Conta B Cross Church Lote')
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response_individual = self.client.post(
            reverse('financeiro:registrar_pagamento_conta_pagar', args=[conta_individual.pk]),
            data=self._payload_individual(self.conta_b),
        )
        response_lote = self.client.post(
            reverse('financeiro:registrar_pagamento_lote_contas_pagar'),
            data=self._payload_lote(conta_lote, self.conta_a),
        )

        self.assertEqual(response_individual.status_code, 404)
        self.assertEqual(response_lote.status_code, 302)
        self._assert_pagamento_nao_alterado(conta_individual, self.conta_b)
        self._assert_pagamento_nao_alterado(conta_lote, self.conta_b)

    def test_segundo_pagamento_individual_nao_duplica_despesa_ou_debito(self):
        tesoureiro = self._criar_usuario(
            'tesoureiro-segundo-pagamento-bloqueado',
            TESOUREIRO,
            [self.igreja_a],
        )
        conta = self._criar_conta_pagar(self.igreja_a, 'Conta Pagamento Unico')
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response_primeiro_pagamento = self.client.post(
            reverse('financeiro:registrar_pagamento_conta_pagar', args=[conta.pk]),
            data=self._payload_individual(self.conta_a),
        )

        self.assertEqual(response_primeiro_pagamento.status_code, 302)
        conta.refresh_from_db()
        self.conta_a.refresh_from_db()
        self.assertEqual(conta.status, 'PAG')
        self.assertEqual(conta.valor_pago, Decimal('100.00'))
        self.assertEqual(Despesas.objects.filter(origem_conta_pagar=conta).count(), 1)
        self.assertEqual(self.conta_a.saldo_atual, Decimal('400.00'))

        response_segundo_pagamento = self.client.post(
            reverse('financeiro:registrar_pagamento_conta_pagar', args=[conta.pk]),
            data={
                **self._payload_individual(self.conta_a),
                'data_pagamento': '2026-10-17',
                'valor_pago': '99.00',
            },
        )

        self.assertEqual(response_segundo_pagamento.status_code, 404)
        conta.refresh_from_db()
        self.conta_a.refresh_from_db()
        self.assertEqual(conta.status, 'PAG')
        self.assertEqual(conta.data_pagamento, date(2026, 10, 16))
        self.assertEqual(conta.valor_pago, Decimal('100.00'))
        self.assertEqual(Despesas.objects.filter(origem_conta_pagar=conta).count(), 1)
        self.assertEqual(self.conta_a.saldo_atual, Decimal('400.00'))


class ContaPagarFormScopeHardeningTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username='admin-form-scope-payable-management',
            password='senha123',
        )
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Form Scope Payable Management',
            administrador_principal=self.admin,
            ativo=True,
        )
        self.outro_admin = User.objects.create_user(
            username='admin-outro-ministerio-form-scope-payable-management',
            password='senha123',
        )
        self.outro_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministerio Form Scope Payable Management',
            administrador_principal=self.outro_admin,
            ativo=True,
        )
        self.igreja_a = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja A Form Scope Payable Management',
            tipo_igreja='sede',
        )
        self.igreja_b = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja B Form Scope Payable Management',
            tipo_igreja='regional',
        )
        self.igreja_outro_ministerio = Igreja.objects.create(
            ministerio=self.outro_ministerio,
            nome_igreja='Igreja Outro Ministerio Form Scope Payable Management',
            tipo_igreja='sede',
        )
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Form Scope Payable Management',
            ativo=True,
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Form Scope Payable Management',
        )
        Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        self.admin.groups.add(Group.objects.get(name=ADMIN_MINISTERIO))
        self.perfil = PerfilUsuario.objects.create(user=self.admin, ministerio=self.ministerio)
        self.perfil.igrejas_permitidas.set([self.igreja_a])

    def _payload(self, igreja):
        return {
            'igreja': str(igreja.pk),
            'fornecedor': str(self.fornecedor.pk),
            'categoria': str(self.categoria.pk),
            'descricao': 'Conta Form Scope',
            'numero_documento': 'NF-FORM-123',
            'valor': '100.00',
            'data_emissao': '2026-10-10',
            'data_vencimento': '2026-10-20',
            'observacoes': 'Teste direto do escopo explícito do formulário.',
        }

    def _form(self, data=None):
        return ContaPagarForm(
            data=data,
            ministerio=self.ministerio,
            user=self.admin,
            allowed_churches=get_finance_write_scope(self.admin, self.ministerio),
        )

    def test_admin_queryset_respeita_write_scope_explicito(self):
        form = self._form()

        queryset_ids = set(form.fields['igreja'].queryset.values_list('pk', flat=True))

        self.assertIn(self.igreja_a.pk, queryset_ids)
        self.assertNotIn(self.igreja_b.pk, queryset_ids)

    def test_admin_post_igreja_fora_do_write_scope_e_invalido(self):
        form = self._form(self._payload(self.igreja_b))

        self.assertFalse(form.is_valid())
        self.assertIn('igreja', form.errors)
        self.assertEqual(ContaPagar.objects.count(), 0)

    def test_admin_post_igreja_de_outro_ministerio_e_invalido(self):
        form = self._form(self._payload(self.igreja_outro_ministerio))

        self.assertFalse(form.is_valid())
        self.assertIn('igreja', form.errors)
        self.assertEqual(ContaPagar.objects.count(), 0)

    def test_scope_omitido_preserva_fallback_do_ministerio(self):
        form = ContaPagarForm(
            ministerio=self.ministerio,
            user=self.admin,
        )

        queryset_ids = set(form.fields['igreja'].queryset.values_list('pk', flat=True))

        self.assertIn(self.igreja_a.pk, queryset_ids)
        self.assertIn(self.igreja_b.pk, queryset_ids)
        self.assertNotIn(self.igreja_outro_ministerio.pk, queryset_ids)

    def test_scope_explicitamente_vazio_permanece_vazio(self):
        form = ContaPagarForm(
            ministerio=self.ministerio,
            user=self.admin,
            allowed_churches=Igreja.objects.none(),
        )

        self.assertFalse(form.fields['igreja'].queryset.exists())


class ContaPagarManagementAuthorizationHardeningTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_principal = User.objects.create_user(
            username='admin-principal-payable-management',
            password='senha123',
        )
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Payable Management Hardening',
            administrador_principal=self.admin_principal,
            ativo=True,
        )
        self.outro_admin_principal = User.objects.create_user(
            username='admin-principal-outro-ministerio-payable-management',
            password='senha123',
        )
        self.outro_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministerio Payable Management Hardening',
            administrador_principal=self.outro_admin_principal,
            ativo=True,
        )
        self.igreja_a = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja A Payable Management',
            tipo_igreja='sede',
        )
        self.igreja_b = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja B Payable Management',
            tipo_igreja='regional',
        )
        self.igreja_c = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja C Descendente Payable Management',
            tipo_igreja='congregacao',
            igreja_superior=self.igreja_b,
        )
        self.igreja_outro_ministerio = Igreja.objects.create(
            ministerio=self.outro_ministerio,
            nome_igreja='Igreja Outro Ministerio Payable Management',
            tipo_igreja='sede',
        )
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Payable Management',
            ativo=True,
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Payable Management',
        )
        self.fornecedor_outro_ministerio = Fornecedor.objects.create(
            ministerio=self.outro_ministerio,
            nome='Fornecedor Outro Ministerio Payable Management',
            ativo=True,
        )
        self.categoria_outro_ministerio = CategoriaDespesa.objects.create(
            ministerio=self.outro_ministerio,
            nome='Categoria Outro Ministerio Payable Management',
        )
        self.conta_debito = ContaBancaria.objects.create(
            igreja=self.igreja_a,
            nome_identificacao='Conta Debito Payable Management',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('500.00'),
        )
        for group_name in (ADMIN_MINISTERIO, PASTOR_LOCAL, PASTOR_REGIONAL, TESOUREIRO):
            Group.objects.get_or_create(name=group_name)
        Plano.objects.get_or_create(
            nome='pioneiro',
            defaults={
                'codigo_plano': 'pioneiro',
                'permite_modulo_financeiro': True,
                'ativo': True,
            },
        )

    def _criar_usuario(self, username, group_name, igrejas=()):
        user = get_user_model().objects.create_user(username=username, password='senha123')
        user.groups.add(Group.objects.get(name=group_name))
        perfil = PerfilUsuario.objects.create(user=user, ministerio=self.ministerio)
        perfil.igrejas_permitidas.set(igrejas)
        return user, perfil

    def _autenticar_com_igreja_ativa(self, user, igreja):
        self.client.force_login(user)
        session = self.client.session
        session['igreja_ativa_id'] = igreja.pk
        session.save()

    def _payload(self, igreja, descricao, valor='100.00'):
        return {
            'igreja': str(igreja.pk),
            'fornecedor': str(self.fornecedor.pk),
            'categoria': str(self.categoria.pk),
            'descricao': descricao,
            'numero_documento': 'NF-123',
            'valor': valor,
            'data_emissao': '2026-10-10',
            'data_vencimento': '2026-10-20',
            'observacoes': 'Conta criada para teste de autorização.',
        }

    def _criar_conta(self, igreja, descricao='Conta existente', status='PEN', valor='100.00'):
        return ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=igreja,
            fornecedor=self.fornecedor,
            categoria=self.categoria,
            descricao=descricao,
            valor=Decimal(valor),
            data_emissao=date(2026, 10, 10),
            data_vencimento=date(2026, 10, 20),
            status=status,
        )

    def _payload_pagamento(self):
        return {
            'data_pagamento': '2026-10-16',
            'valor_pago': '100.00',
            'juros_multa': '0.00',
            'desconto': '0.00',
            'conta_debito': str(self.conta_debito.pk),
            'forma_pagamento': 'PIX',
        }

    def _assert_conta_inalterada(self, conta, descricao, valor, igreja, status):
        conta.refresh_from_db()
        self.assertEqual(conta.descricao, descricao)
        self.assertEqual(conta.valor, Decimal(valor))
        self.assertEqual(conta.igreja_id, igreja.pk)
        self.assertEqual(conta.status, status)
        self.assertFalse(Despesas.objects.filter(origem_conta_pagar=conta).exists())

    def _editar_conta_manual(self, conta, descricao, valor='100.00', **overrides):
        tesoureiro, _ = self._criar_usuario(
            f'tesoureiro-edicao-fingerprint-{conta.pk}-{descricao}',
            TESOUREIRO,
            [conta.igreja],
        )
        self._autenticar_com_igreja_ativa(tesoureiro, conta.igreja)
        payload = self._payload(conta.igreja, descricao, valor=valor)
        payload.update(overrides)
        return self.client.post(
            reverse('financeiro:editar_conta_pagar', args=[conta.pk]),
            data=payload,
        )

    def _atribuir_fingerprint_atual(self, conta):
        fingerprint = refresh_payable_material_fingerprint(conta)
        conta.save(update_fields=['current_material_fingerprint'])
        return fingerprint

    def _configurar_politica(self, igreja, *, approval_required, version):
        politica = PoliticaFinanceiraIgreja.objects.get(igreja=igreja)
        politica.approval_required = approval_required
        politica.segregation_level = (
            PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED
            if approval_required else PoliticaFinanceiraIgreja.LEVEL_1_SIMPLE
        )
        politica.version = version
        politica.full_clean()
        politica.save()
        return politica

    def _registrar_evento_decisao_historico(self, conta, event_type, politica):
        return _create_payable_authorization_event(
            payable=conta,
            event_type=event_type,
            actor=self.admin_principal,
            authorization_status_before=ContaPagar.AUTHORIZATION_PENDING,
            authorization_status_after=conta.authorization_status,
            financial_status_before=conta.status,
            financial_status_after=conta.status,
            material_fingerprint=conta.current_material_fingerprint,
            material_snapshot=build_payable_material_snapshot_v1(conta),
            policy=politica,
            reason=conta.current_rejection_reason,
        )

    def _assert_edicao_manual_falhou_sem_persistencia(self, conta, *, descricao, valor, fingerprint,
                                                       authorization_status, policy_version,
                                                       event_count=0):
        conta.refresh_from_db()
        self.assertEqual(conta.descricao, descricao)
        self.assertEqual(conta.valor, Decimal(valor))
        self.assertEqual(conta.current_material_fingerprint, fingerprint)
        self.assertEqual(conta.authorization_status, authorization_status)
        self.assertEqual(conta.authorization_policy_version, policy_version)
        self.assertEqual(
            ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta).count(),
            event_count,
        )

    def test_edicao_manual_material_mantem_pending_e_atualiza_politica_vigente(self):
        conta = self._criar_conta(self.igreja_a, 'Conta Pendente Original')
        original_fingerprint = self._atribuir_fingerprint_atual(conta)
        politica = self._configurar_politica(
            self.igreja_a,
            approval_required=True,
            version=8,
        )
        conta.authorization_status = ContaPagar.AUTHORIZATION_PENDING
        conta.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED
        conta.authorization_policy_version = 4
        conta.save(update_fields=['authorization_status', 'authorization_origin', 'authorization_policy_version'])

        response = self._editar_conta_manual(
            conta,
            'Conta Pendente Editada',
            valor='125.00',
            data_vencimento='2026-10-25',
        )

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        self.assertNotEqual(conta.current_material_fingerprint, original_fingerprint)
        self.assertEqual(
            conta.current_material_fingerprint,
            compute_payable_material_fingerprint_v1(build_payable_material_snapshot_v1(conta)),
        )
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_PENDING)
        self.assertIsNone(conta.approved_material_fingerprint)
        self.assertIsNone(conta.approved_by)
        self.assertIsNone(conta.approved_at)
        self.assertEqual(conta.authorization_policy_version, politica.version)
        self.assertEqual(
            list(
                ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta)
                .order_by('id')
                .values_list('event_type', flat=True)
            ),
            [ContaPagarAutorizacaoEvento.EVENT_EDITED],
        )

    def test_edicao_manual_nao_material_repara_fingerprint_sem_reclassificar(self):
        conta = self._criar_conta(self.igreja_a, 'Conta Legada Sem Fingerprint')
        conta.authorization_status = ContaPagar.AUTHORIZATION_PENDING
        conta.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED
        conta.authorization_policy_version = 7
        conta.save(update_fields=['authorization_status', 'authorization_origin', 'authorization_policy_version'])

        response = self._editar_conta_manual(conta, conta.descricao)

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        self.assertTrue(conta.current_material_fingerprint)
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(conta.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED)
        self.assertEqual(conta.authorization_policy_version, 7)
        self.assertFalse(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta).exists())

    def test_edicao_manual_nao_material_repara_fingerprint_nulo_sem_reclassificar(self):
        conta = self._criar_conta(self.igreja_a, 'Conta Legada Fingerprint Nulo')
        conta.authorization_status = ContaPagar.AUTHORIZATION_NOT_REQUIRED
        conta.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED
        conta.authorization_policy_version = 3
        conta.current_material_fingerprint = None
        conta.save(update_fields=[
            'authorization_status',
            'authorization_origin',
            'authorization_policy_version',
            'current_material_fingerprint',
        ])

        response = self._editar_conta_manual(conta, 'Conta Legada Fingerprint Nulo')

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_NOT_REQUIRED)
        self.assertEqual(conta.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED)
        self.assertEqual(conta.authorization_policy_version, 3)
        self.assertTrue(conta.current_material_fingerprint)
        self.assertFalse(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta).exists())

    def test_edicao_manual_material_mantem_not_required_e_atualiza_politica_vigente(self):
        conta = self._criar_conta(self.igreja_a, 'Conta Not Required Original')
        original_fingerprint = self._atribuir_fingerprint_atual(conta)
        politica = self._configurar_politica(
            self.igreja_a,
            approval_required=False,
            version=6,
        )
        conta.authorization_status = ContaPagar.AUTHORIZATION_NOT_REQUIRED
        conta.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED
        conta.authorization_policy_version = 2
        conta.save(update_fields=['authorization_status', 'authorization_origin', 'authorization_policy_version'])

        response = self._editar_conta_manual(
            conta,
            'Conta Not Required Editada Materialmente',
        )

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        self.assertNotEqual(conta.current_material_fingerprint, original_fingerprint)
        self.assertEqual(
            conta.current_material_fingerprint,
            compute_payable_material_fingerprint_v1(build_payable_material_snapshot_v1(conta)),
        )
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_NOT_REQUIRED)
        self.assertEqual(conta.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED)
        self.assertEqual(conta.authorization_policy_version, politica.version)
        self.assertEqual(
            list(
                ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta)
                .order_by('id')
                .values_list('event_type', flat=True)
            ),
            [ContaPagarAutorizacaoEvento.EVENT_EDITED],
        )

    def test_edicao_manual_material_reclassifica_not_required_para_pending_quando_policy_exige_aprovacao(self):
        conta = self._criar_conta(self.igreja_a, 'Conta Sem Aprovacao Original')
        self._atribuir_fingerprint_atual(conta)
        politica = self._configurar_politica(
            self.igreja_a,
            approval_required=True,
            version=12,
        )
        conta.authorization_status = ContaPagar.AUTHORIZATION_NOT_REQUIRED
        conta.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED
        conta.authorization_policy_version = 3
        conta.save(update_fields=['authorization_status', 'authorization_origin', 'authorization_policy_version'])

        response = self._editar_conta_manual(conta, 'Conta Agora Requer Aprovacao', valor='150.00')

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(conta.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED)
        self.assertEqual(conta.authorization_policy_version, politica.version)
        self.assertEqual(
            list(
                ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta)
                .order_by('id')
                .values_list('event_type', flat=True)
            ),
            [
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
            ],
        )

    def test_edicao_manual_pending_troca_igreja_usa_policy_resultante(self):
        tesoureiro, _ = self._criar_usuario(
            'tesoureiro-b3b2b-troca-igreja',
            TESOUREIRO,
            [self.igreja_a, self.igreja_b],
        )
        conta = self._criar_conta(self.igreja_a, 'Conta Pendente Igreja A')
        self._atribuir_fingerprint_atual(conta)
        self._configurar_politica(self.igreja_a, approval_required=False, version=2)
        politica_b = self._configurar_politica(self.igreja_b, approval_required=True, version=13)
        conta.authorization_status = ContaPagar.AUTHORIZATION_PENDING
        conta.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED
        conta.authorization_policy_version = 4
        conta.save(update_fields=['authorization_status', 'authorization_origin', 'authorization_policy_version'])
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response = self.client.post(
            reverse('financeiro:editar_conta_pagar', args=[conta.pk]),
            data=self._payload(self.igreja_b, 'Conta Pendente Igreja B', valor='150.00'),
        )

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        self.assertEqual(conta.igreja_id, self.igreja_b.pk)
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(conta.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED)
        self.assertEqual(conta.authorization_policy_version, politica_b.version)
        self.assertEqual(
            list(
                ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta)
                .order_by('id')
                .values_list('event_type', flat=True)
            ),
            [
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
            ],
        )

    def test_edicao_manual_material_invalida_aprovacao_com_evidencia_historica(self):
        conta = self._criar_conta(self.igreja_a, 'Conta Aprovada Original')
        original_fingerprint = self._atribuir_fingerprint_atual(conta)
        politica = self._configurar_politica(
            self.igreja_a,
            approval_required=True,
            version=5,
        )
        conta.authorization_status = ContaPagar.AUTHORIZATION_APPROVED
        conta.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_USER_APPROVAL
        conta.authorization_policy_version = 4
        conta.approved_material_fingerprint = original_fingerprint
        conta.approved_by = self.admin_principal
        conta.approved_at = timezone.now()
        conta.save(update_fields=[
            'authorization_status',
            'authorization_origin',
            'authorization_policy_version',
            'approved_material_fingerprint',
            'approved_by',
            'approved_at',
        ])
        self._registrar_evento_decisao_historico(
            conta,
            ContaPagarAutorizacaoEvento.EVENT_APPROVED,
            politica,
        )

        response = self._editar_conta_manual(conta, 'Conta Aprovada Editada', valor='130.00')

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(conta.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED)
        self.assertEqual(conta.authorization_policy_version, politica.version)
        self.assertNotEqual(conta.current_material_fingerprint, original_fingerprint)
        self.assertIsNone(conta.approved_material_fingerprint)
        self.assertIsNone(conta.approved_by)
        self.assertIsNone(conta.approved_at)
        self.assertEqual(
            list(
                ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta)
                .order_by('id')
                .values_list('event_type', flat=True)
            ),
            [
                ContaPagarAutorizacaoEvento.EVENT_APPROVED,
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_INVALIDATED,
                ContaPagarAutorizacaoEvento.EVENT_APPROVAL_REQUESTED,
            ],
        )

    def test_edicao_manual_material_falha_fechado_com_evento_aprovado_antigo(self):
        conta = self._criar_conta(self.igreja_a, 'Conta Aprovada Com Evento Antigo')
        original_fingerprint = self._atribuir_fingerprint_atual(conta)
        politica = self._configurar_politica(self.igreja_a, approval_required=True, version=14)
        conta.authorization_status = ContaPagar.AUTHORIZATION_APPROVED
        conta.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_USER_APPROVAL
        conta.approved_material_fingerprint = original_fingerprint
        conta.approved_by = self.admin_principal
        conta.approved_at = timezone.now()
        conta.save()
        evento = self._registrar_evento_decisao_historico(
            conta,
            ContaPagarAutorizacaoEvento.EVENT_APPROVED,
            politica,
        )
        evento.material_fingerprint = 'v1:sha256:fingerprint-antigo'
        evento.save(update_fields=['material_fingerprint'])

        response = self._editar_conta_manual(conta, 'Conta Aprovada Com Evento Antigo Editada')

        self.assertEqual(response.status_code, 200)
        self._assert_edicao_manual_falhou_sem_persistencia(
            conta,
            descricao='Conta Aprovada Com Evento Antigo',
            valor='100.00',
            fingerprint=original_fingerprint,
            authorization_status=ContaPagar.AUTHORIZATION_APPROVED,
            policy_version=None,
            event_count=1,
        )
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta).count(), 1)

    def test_edicao_manual_material_limpa_rejeicao_com_evidencia_historica(self):
        conta = self._criar_conta(self.igreja_a, 'Conta Rejeitada Original')
        self._atribuir_fingerprint_atual(conta)
        politica = self._configurar_politica(
            self.igreja_a,
            approval_required=False,
            version=9,
        )
        conta.authorization_status = ContaPagar.AUTHORIZATION_REJECTED
        conta.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED
        conta.authorization_policy_version = 4
        conta.rejected_by = self.admin_principal
        conta.rejected_at = timezone.now()
        conta.current_rejection_reason = 'Evidencia formal da rejeicao.'
        conta.save(update_fields=[
            'authorization_status',
            'authorization_origin',
            'authorization_policy_version',
            'rejected_by',
            'rejected_at',
            'current_rejection_reason',
        ])
        self._registrar_evento_decisao_historico(
            conta,
            ContaPagarAutorizacaoEvento.EVENT_REJECTED,
            politica,
        )

        response = self._editar_conta_manual(conta, 'Conta Rejeitada Editada', valor='140.00')

        self.assertEqual(response.status_code, 302)
        conta.refresh_from_db()
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_NOT_REQUIRED)
        self.assertEqual(conta.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED)
        self.assertEqual(conta.authorization_policy_version, politica.version)
        self.assertIsNone(conta.rejected_by)
        self.assertIsNone(conta.rejected_at)
        self.assertIsNone(conta.current_rejection_reason)
        self.assertEqual(
            list(
                ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta)
                .order_by('id')
                .values_list('event_type', flat=True)
            ),
            [
                ContaPagarAutorizacaoEvento.EVENT_REJECTED,
                ContaPagarAutorizacaoEvento.EVENT_EDITED,
            ],
        )

    def test_edicao_manual_material_falha_fechado_com_evento_rejeitado_antigo(self):
        conta = self._criar_conta(self.igreja_a, 'Conta Rejeitada Com Evento Antigo')
        original_fingerprint = self._atribuir_fingerprint_atual(conta)
        politica = self._configurar_politica(self.igreja_a, approval_required=True, version=15)
        conta.authorization_status = ContaPagar.AUTHORIZATION_REJECTED
        conta.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED
        conta.authorization_policy_version = 4
        conta.rejected_by = self.admin_principal
        conta.rejected_at = timezone.now()
        conta.current_rejection_reason = 'Motivo atual da rejeicao'
        conta.save()
        evento = self._registrar_evento_decisao_historico(
            conta,
            ContaPagarAutorizacaoEvento.EVENT_REJECTED,
            politica,
        )
        evento.material_fingerprint = 'v1:sha256:fingerprint-antigo'
        evento.save(update_fields=['material_fingerprint'])

        response = self._editar_conta_manual(conta, 'Conta Rejeitada Com Evento Antigo Editada')

        self.assertEqual(response.status_code, 200)
        self._assert_edicao_manual_falhou_sem_persistencia(
            conta,
            descricao='Conta Rejeitada Com Evento Antigo',
            valor='100.00',
            fingerprint=original_fingerprint,
            authorization_status=ContaPagar.AUTHORIZATION_REJECTED,
            policy_version=4,
            event_count=1,
        )
        self.assertEqual(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta).count(), 1)

    def test_edicao_manual_material_falha_fechado_sem_evidencia_historica(self):
        conta = self._criar_conta(self.igreja_a, 'Conta Aprovada Sem Evento')
        original_fingerprint = self._atribuir_fingerprint_atual(conta)
        self._configurar_politica(self.igreja_a, approval_required=True, version=10)
        conta.authorization_status = ContaPagar.AUTHORIZATION_APPROVED
        conta.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_USER_APPROVAL
        conta.approved_material_fingerprint = original_fingerprint
        conta.approved_by = self.admin_principal
        conta.approved_at = timezone.now()
        conta.save()

        response = self._editar_conta_manual(conta, 'Conta Aprovada Sem Evento Editada')

        self.assertEqual(response.status_code, 200)
        conta.refresh_from_db()
        self.assertEqual(conta.descricao, 'Conta Aprovada Sem Evento')
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_APPROVED)
        self.assertEqual(conta.current_material_fingerprint, original_fingerprint)
        self.assertFalse(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta).exists())

    def test_edicao_manual_rejeitada_falha_fechado_sem_evidencia_historica(self):
        conta = self._criar_conta(self.igreja_a, 'Conta Rejeitada Sem Evento')
        original_fingerprint = self._atribuir_fingerprint_atual(conta)
        self._configurar_politica(self.igreja_a, approval_required=True, version=16)
        conta.authorization_status = ContaPagar.AUTHORIZATION_REJECTED
        conta.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED
        conta.authorization_policy_version = 4
        conta.rejected_by = self.admin_principal
        conta.rejected_at = timezone.now()
        conta.current_rejection_reason = 'Motivo sem evidencia formal'
        conta.save()

        response = self._editar_conta_manual(conta, 'Conta Rejeitada Sem Evento Editada')

        self.assertEqual(response.status_code, 200)
        self._assert_edicao_manual_falhou_sem_persistencia(
            conta,
            descricao='Conta Rejeitada Sem Evento',
            valor='100.00',
            fingerprint=original_fingerprint,
            authorization_status=ContaPagar.AUTHORIZATION_REJECTED,
            policy_version=4,
        )

    def test_edicao_manual_material_falha_fechado_sem_status_autorizacao(self):
        conta = self._criar_conta(self.igreja_a, 'Conta Sem Status De Autorizacao')
        original_fingerprint = self._atribuir_fingerprint_atual(conta)
        self._configurar_politica(self.igreja_a, approval_required=True, version=17)
        conta.authorization_status = None
        conta.authorization_origin = None
        conta.authorization_policy_version = None
        conta.save(update_fields=['authorization_status', 'authorization_origin', 'authorization_policy_version'])

        response = self._editar_conta_manual(conta, 'Conta Sem Status Editada')

        self.assertEqual(response.status_code, 200)
        self._assert_edicao_manual_falhou_sem_persistencia(
            conta,
            descricao='Conta Sem Status De Autorizacao',
            valor='100.00',
            fingerprint=original_fingerprint,
            authorization_status=None,
            policy_version=None,
        )

    def test_edicao_manual_formulario_invalido_nao_persiste_nem_cria_evento(self):
        tesoureiro, _ = self._criar_usuario(
            'tesoureiro-b3b2b-formulario-invalido',
            TESOUREIRO,
            [self.igreja_a],
        )
        conta = self._criar_conta(self.igreja_a, 'Conta Com Formulario Invalido')
        original_fingerprint = self._atribuir_fingerprint_atual(conta)
        payload = self._payload(self.igreja_a, 'Conta Com Formulario Invalido Editada')
        payload.pop('fornecedor')
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response = self.client.post(
            reverse('financeiro:editar_conta_pagar', args=[conta.pk]),
            data=payload,
        )

        self.assertEqual(response.status_code, 200)
        self._assert_edicao_manual_falhou_sem_persistencia(
            conta,
            descricao='Conta Com Formulario Invalido',
            valor='100.00',
            fingerprint=original_fingerprint,
            authorization_status=None,
            policy_version=None,
        )

    def test_edicao_manual_categoria_de_outro_ministerio_nao_persiste_nem_cria_evento(self):
        tesoureiro, _ = self._criar_usuario(
            'tesoureiro-b3b2b-categoria-outro-ministerio',
            TESOUREIRO,
            [self.igreja_a],
        )
        conta = self._criar_conta(self.igreja_a, 'Conta Com Categoria De Outro Ministerio')
        original_fingerprint = self._atribuir_fingerprint_atual(conta)
        payload = self._payload(self.igreja_a, 'Conta Com Categoria Indevida', valor='150.00')
        payload['categoria'] = str(self.categoria_outro_ministerio.pk)
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response = self.client.post(
            reverse('financeiro:editar_conta_pagar', args=[conta.pk]),
            data=payload,
        )

        self.assertEqual(response.status_code, 200)
        self._assert_edicao_manual_falhou_sem_persistencia(
            conta,
            descricao='Conta Com Categoria De Outro Ministerio',
            valor='100.00',
            fingerprint=original_fingerprint,
            authorization_status=None,
            policy_version=None,
        )

    def test_edicao_manual_igreja_resultante_fora_do_escopo_nao_persiste_nem_cria_evento(self):
        tesoureiro, _ = self._criar_usuario(
            'tesoureiro-b3b2b-resulting-scope',
            TESOUREIRO,
            [self.igreja_a],
        )
        conta = self._criar_conta(self.igreja_a, 'Conta Com Troca Fora Do Escopo')
        original_fingerprint = self._atribuir_fingerprint_atual(conta)
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response = self.client.post(
            reverse('financeiro:editar_conta_pagar', args=[conta.pk]),
            data=self._payload(self.igreja_b, 'Conta Indevidamente Movida', valor='150.00'),
        )

        self.assertEqual(response.status_code, 200)
        self._assert_edicao_manual_falhou_sem_persistencia(
            conta,
            descricao='Conta Com Troca Fora Do Escopo',
            valor='100.00',
            fingerprint=original_fingerprint,
            authorization_status=None,
            policy_version=None,
        )

    def test_edicao_manual_reverte_tudo_quando_materializacao_de_eventos_falha(self):
        conta = self._criar_conta(self.igreja_a, 'Conta Com Falha De Evento')
        original_fingerprint = self._atribuir_fingerprint_atual(conta)
        self._configurar_politica(self.igreja_a, approval_required=True, version=11)
        conta.authorization_status = ContaPagar.AUTHORIZATION_PENDING
        conta.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED
        conta.authorization_policy_version = 4
        conta.save(update_fields=['authorization_status', 'authorization_origin', 'authorization_policy_version'])

        with patch.object(
            financeiro_views,
            '_materialize_payable_edit_authorization_events',
            side_effect=RuntimeError('falha intencional de materializacao'),
        ):
            response = self._editar_conta_manual(conta, 'Conta Com Falha Editada', valor='150.00')

        self.assertEqual(response.status_code, 200)
        conta.refresh_from_db()
        self.assertEqual(conta.descricao, 'Conta Com Falha De Evento')
        self.assertEqual(conta.valor, Decimal('100.00'))
        self.assertEqual(conta.current_material_fingerprint, original_fingerprint)
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(conta.authorization_policy_version, 4)
        self.assertFalse(ContaPagarAutorizacaoEvento.objects.filter(conta_pagar=conta).exists())

    def test_criacao_falha_fechado_com_escopo_vazio_e_nao_usa_igreja_ativa(self):
        tesoureiro, perfil = self._criar_usuario(
            'tesoureiro-criacao-escopo-vazio-payable-management',
            TESOUREIRO,
        )
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response = self.client.post(
            reverse('financeiro:criar_conta_pagar'),
            data=self._payload(self.igreja_a, 'Conta Escopo Vazio'),
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(ContaPagar.objects.filter(descricao='Conta Escopo Vazio').exists())
        self.assertFalse(get_finance_write_scope(tesoureiro, self.ministerio).exists())
        self.assertEqual(Despesas.objects.count(), 0)
        perfil.refresh_from_db()
        self.assertFalse(perfil.igrejas_permitidas.exists())

    def test_criacao_rejeita_igreja_adulterada_fora_do_escopo_e_de_outro_ministerio(self):
        tesoureiro, _ = self._criar_usuario(
            'tesoureiro-criacao-adulterada-payable-management',
            TESOUREIRO,
            [self.igreja_a],
        )
        self.client.force_login(tesoureiro)

        for igreja, descricao in (
            (self.igreja_b, 'Conta Igreja B Adulterada'),
            (self.igreja_outro_ministerio, 'Conta Outro Ministerio Adulterada'),
        ):
            response = self.client.post(
                reverse('financeiro:criar_conta_pagar'),
                data=self._payload(igreja, descricao),
            )

            self.assertEqual(response.status_code, 302)
            self.assertFalse(
                ContaPagar.objects.filter(
                    igreja=igreja,
                    descricao=descricao,
                ).exists()
            )

        self.assertFalse(ContaPagar.objects.filter(igreja__in=[self.igreja_b, self.igreja_outro_ministerio]).exists())
        self.assertFalse(
            ContaPagarAutorizacaoEvento.objects.filter(
                conta_pagar__igreja__in=[self.igreja_b, self.igreja_outro_ministerio],
                event_type=ContaPagarAutorizacaoEvento.EVENT_CREATED,
            ).exists()
        )
        self.assertEqual(Despesas.objects.count(), 0)

    def test_pastor_local_no_escopo_cria_edita_e_cancela_conta(self):
        pastor, _ = self._criar_usuario(
            'pastor-local-gerencia-payable-management',
            PASTOR_LOCAL,
            [self.igreja_a],
        )
        self._autenticar_com_igreja_ativa(pastor, self.igreja_a)

        response_criacao = self.client.post(
            reverse('financeiro:criar_conta_pagar'),
            data=self._payload(self.igreja_a, 'Conta Pastor Local'),
        )
        self.assertEqual(response_criacao.status_code, 302)
        conta = ContaPagar.objects.get(descricao='Conta Pastor Local')
        self.assertEqual(conta.igreja_id, self.igreja_a.pk)
        self.assertEqual(conta.status, 'PEN')

        response_edicao = self.client.post(
            reverse('financeiro:editar_conta_pagar', args=[conta.pk]),
            data=self._payload(self.igreja_a, 'Conta Pastor Local Editada', valor='125.00'),
        )
        self.assertEqual(response_edicao.status_code, 302)
        conta.refresh_from_db()
        self.assertEqual(conta.descricao, 'Conta Pastor Local Editada')
        self.assertEqual(conta.valor, Decimal('125.00'))

        response_cancelamento = self.client.post(
            reverse('financeiro:cancelar_conta_pagar', args=[conta.pk]),
        )
        self.assertEqual(response_cancelamento.status_code, 302)
        conta.refresh_from_db()
        self.assertEqual(conta.status, 'CAN')
        self.assertFalse(Despesas.objects.filter(origem_conta_pagar=conta).exists())

    def test_tesoureiro_no_escopo_cria_conta(self):
        tesoureiro, _ = self._criar_usuario(
            'tesoureiro-cria-payable-management',
            TESOUREIRO,
            [self.igreja_a],
        )
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response = self.client.post(
            reverse('financeiro:criar_conta_pagar'),
            data=self._payload(self.igreja_a, 'Conta Tesoureiro'),
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(ContaPagar.objects.filter(igreja=self.igreja_a, descricao='Conta Tesoureiro').exists())

    def test_criacao_manual_classifica_policy_simples_e_registra_evento_do_usuario(self):
        tesoureiro, _ = self._criar_usuario(
            'tesoureiro-criacao-manual-simples',
            TESOUREIRO,
            [self.igreja_a],
        )
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response = self.client.post(
            reverse('financeiro:criar_conta_pagar'),
            data=self._payload(self.igreja_a, 'Conta Manual Simples'),
        )

        self.assertEqual(response.status_code, 302)
        conta = ContaPagar.objects.get(descricao='Conta Manual Simples')
        event = ContaPagarAutorizacaoEvento.objects.get(conta_pagar=conta)
        self.assertEqual(ContaPagar.objects.filter(descricao='Conta Manual Simples').count(), 1)
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_NOT_REQUIRED)
        self.assertEqual(conta.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED)
        self.assertTrue(conta.current_material_fingerprint)
        self.assertEqual(event.event_type, ContaPagarAutorizacaoEvento.EVENT_CREATED)
        self.assertEqual(event.actor, tesoureiro)
        self.assertEqual(conta.usuario_criacao, tesoureiro)

    def test_criacao_manual_classifica_policy_exigindo_aprovacao(self):
        PoliticaFinanceiraIgreja.objects.filter(igreja=self.igreja_a).update(
            approval_required=True,
            segregation_level=PoliticaFinanceiraIgreja.LEVEL_2_CONTROLLED,
        )
        tesoureiro, _ = self._criar_usuario(
            'tesoureiro-criacao-manual-pendente',
            TESOUREIRO,
            [self.igreja_a],
        )
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response = self.client.post(
            reverse('financeiro:criar_conta_pagar'),
            data=self._payload(self.igreja_a, 'Conta Manual Pendente'),
        )

        self.assertEqual(response.status_code, 302)
        conta = ContaPagar.objects.get(descricao='Conta Manual Pendente')
        event = ContaPagarAutorizacaoEvento.objects.get(conta_pagar=conta)
        self.assertEqual(conta.authorization_status, ContaPagar.AUTHORIZATION_PENDING)
        self.assertEqual(conta.authorization_origin, ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED)
        self.assertEqual(event.actor, tesoureiro)

    def test_edicao_e_cancelamento_falham_fechado_com_escopo_vazio(self):
        tesoureiro, perfil = self._criar_usuario(
            'tesoureiro-edicao-cancelamento-escopo-vazio-payable-management',
            TESOUREIRO,
        )
        conta = self._criar_conta(self.igreja_a, 'Conta Escopo Vazio Existente')
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response_edicao = self.client.post(
            reverse('financeiro:editar_conta_pagar', args=[conta.pk]),
            data=self._payload(self.igreja_a, 'Conta Não Deve Editar', valor='999.00'),
        )
        response_cancelamento = self.client.post(
            reverse('financeiro:cancelar_conta_pagar', args=[conta.pk]),
        )

        self.assertEqual(response_edicao.status_code, 404)
        self.assertEqual(response_cancelamento.status_code, 404)
        self._assert_conta_inalterada(conta, 'Conta Escopo Vazio Existente', '100.00', self.igreja_a, 'PEN')
        perfil.refresh_from_db()
        self.assertFalse(perfil.igrejas_permitidas.exists())

    def test_edicao_rejeita_objeto_fora_do_escopo_e_troca_adulterada_de_igreja(self):
        tesoureiro, _ = self._criar_usuario(
            'tesoureiro-edicao-fora-escopo-payable-management',
            TESOUREIRO,
            [self.igreja_a],
        )
        conta_a = self._criar_conta(self.igreja_a, 'Conta A Editavel')
        conta_b = self._criar_conta(self.igreja_b, 'Conta B Fora do Escopo')
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response_troca_igreja = self.client.post(
            reverse('financeiro:editar_conta_pagar', args=[conta_a.pk]),
            data=self._payload(self.igreja_b, 'Conta A Indevidamente Movida', valor='999.00'),
        )
        response_fora_escopo = self.client.post(
            reverse('financeiro:editar_conta_pagar', args=[conta_b.pk]),
            data=self._payload(self.igreja_b, 'Conta B Indevidamente Editada', valor='999.00'),
        )

        self.assertEqual(response_troca_igreja.status_code, 200)
        self.assertEqual(response_fora_escopo.status_code, 404)
        self._assert_conta_inalterada(conta_a, 'Conta A Editavel', '100.00', self.igreja_a, 'PEN')
        self._assert_conta_inalterada(conta_b, 'Conta B Fora do Escopo', '100.00', self.igreja_b, 'PEN')

    def test_cancelamento_fora_do_escopo_nao_altera_status(self):
        tesoureiro, _ = self._criar_usuario(
            'tesoureiro-cancelamento-fora-escopo-payable-management',
            TESOUREIRO,
            [self.igreja_a],
        )
        conta_b = self._criar_conta(self.igreja_b, 'Conta B Cancelamento Fora do Escopo', status='VEN')
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response = self.client.post(
            reverse('financeiro:cancelar_conta_pagar', args=[conta_b.pk]),
        )

        self.assertEqual(response.status_code, 404)
        self._assert_conta_inalterada(conta_b, 'Conta B Cancelamento Fora do Escopo', '100.00', self.igreja_b, 'VEN')

    def test_edicao_e_cancelamento_cross_ministry_nao_alteram_conta(self):
        tesoureiro, _ = self._criar_usuario(
            'tesoureiro-cross-ministry-payable-management',
            TESOUREIRO,
            [self.igreja_a],
        )
        conta_outro_ministerio = ContaPagar.objects.create(
            ministerio=self.outro_ministerio,
            igreja=self.igreja_outro_ministerio,
            fornecedor=self.fornecedor_outro_ministerio,
            categoria=self.categoria_outro_ministerio,
            descricao='Conta Outro Ministerio Existente',
            valor=Decimal('100.00'),
            data_emissao=date(2026, 10, 10),
            data_vencimento=date(2026, 10, 20),
            status='PEN',
        )
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response_edicao = self.client.post(
            reverse('financeiro:editar_conta_pagar', args=[conta_outro_ministerio.pk]),
            data=self._payload(self.igreja_a, 'Conta Outro Ministerio Alterada', valor='999.00'),
        )
        response_cancelamento = self.client.post(
            reverse('financeiro:cancelar_conta_pagar', args=[conta_outro_ministerio.pk]),
        )

        self.assertEqual(response_edicao.status_code, 404)
        self.assertEqual(response_cancelamento.status_code, 404)
        conta_outro_ministerio.refresh_from_db()
        self.assertEqual(conta_outro_ministerio.descricao, 'Conta Outro Ministerio Existente')
        self.assertEqual(conta_outro_ministerio.valor, Decimal('100.00'))
        self.assertEqual(conta_outro_ministerio.igreja_id, self.igreja_outro_ministerio.pk)
        self.assertEqual(conta_outro_ministerio.status, 'PEN')
        self.assertFalse(Despesas.objects.filter(origem_conta_pagar=conta_outro_ministerio).exists())

    def test_admin_ministerio_sem_escopo_e_fora_do_escopo_nao_edita_nem_cancela(self):
        admin_sem_escopo, perfil_sem_escopo = self._criar_usuario(
            'admin-sem-escopo-payable-management',
            ADMIN_MINISTERIO,
        )
        conta_a = self._criar_conta(self.igreja_a, 'Conta Admin Sem Escopo')
        self._autenticar_com_igreja_ativa(admin_sem_escopo, self.igreja_a)

        response_edicao_sem_escopo = self.client.post(
            reverse('financeiro:editar_conta_pagar', args=[conta_a.pk]),
            data=self._payload(self.igreja_a, 'Conta Admin Alterada Sem Escopo', valor='999.00'),
        )
        response_cancelamento_sem_escopo = self.client.post(
            reverse('financeiro:cancelar_conta_pagar', args=[conta_a.pk]),
        )
        self.assertEqual(response_edicao_sem_escopo.status_code, 404)
        self.assertEqual(response_cancelamento_sem_escopo.status_code, 404)
        self._assert_conta_inalterada(conta_a, 'Conta Admin Sem Escopo', '100.00', self.igreja_a, 'PEN')
        perfil_sem_escopo.refresh_from_db()
        self.assertFalse(perfil_sem_escopo.igrejas_permitidas.exists())

        admin_escopo_a, _ = self._criar_usuario(
            'admin-escopo-a-payable-management',
            ADMIN_MINISTERIO,
            [self.igreja_a],
        )
        conta_b = self._criar_conta(self.igreja_b, 'Conta Admin Fora do Escopo')
        self._autenticar_com_igreja_ativa(admin_escopo_a, self.igreja_a)

        response_edicao_fora_escopo = self.client.post(
            reverse('financeiro:editar_conta_pagar', args=[conta_b.pk]),
            data=self._payload(self.igreja_b, 'Conta Admin Fora do Escopo Alterada', valor='999.00'),
        )
        response_cancelamento_fora_escopo = self.client.post(
            reverse('financeiro:cancelar_conta_pagar', args=[conta_b.pk]),
        )
        self.assertEqual(response_edicao_fora_escopo.status_code, 404)
        self.assertEqual(response_cancelamento_fora_escopo.status_code, 404)
        self._assert_conta_inalterada(conta_b, 'Conta Admin Fora do Escopo', '100.00', self.igreja_b, 'PEN')

    def test_regional_tem_apenas_escopo_explicito_sem_descendente(self):
        regional, _ = self._criar_usuario(
            'pastor-regional-escopo-payable-management',
            PASTOR_REGIONAL,
            [self.igreja_b],
        )

        scope_ids = set(get_finance_write_scope(regional, self.ministerio).values_list('pk', flat=True))

        self.assertIn(self.igreja_b.pk, scope_ids)
        self.assertNotIn(self.igreja_c.pk, scope_ids)

    def test_edicao_posterior_ao_pagamento_nao_sobrescreve_conta_paga(self):
        tesoureiro, _ = self._criar_usuario(
            'tesoureiro-edicao-apos-pagamento-payable-management',
            TESOUREIRO,
            [self.igreja_a],
        )
        conta = self._criar_conta(self.igreja_a, 'Conta Editar Apos Pagamento')
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response_pagamento = self.client.post(
            reverse('financeiro:registrar_pagamento_conta_pagar', args=[conta.pk]),
            data=self._payload_pagamento(),
        )
        response_edicao = self.client.post(
            reverse('financeiro:editar_conta_pagar', args=[conta.pk]),
            data=self._payload(self.igreja_a, 'Conta Indevidamente Editada', valor='999.00'),
        )

        self.assertEqual(response_pagamento.status_code, 302)
        self.assertEqual(response_edicao.status_code, 404)
        conta.refresh_from_db()
        self.conta_debito.refresh_from_db()
        self.assertEqual(conta.status, 'PAG')
        self.assertEqual(conta.descricao, 'Conta Editar Apos Pagamento')
        self.assertEqual(conta.valor, Decimal('100.00'))
        self.assertEqual(Despesas.objects.filter(origem_conta_pagar=conta).count(), 1)
        self.assertEqual(self.conta_debito.saldo_atual, Decimal('400.00'))

    def test_cancelamento_posterior_ao_pagamento_nao_cancela_conta_paga(self):
        tesoureiro, _ = self._criar_usuario(
            'tesoureiro-cancelamento-apos-pagamento-payable-management',
            TESOUREIRO,
            [self.igreja_a],
        )
        conta = self._criar_conta(self.igreja_a, 'Conta Cancelar Apos Pagamento')
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja_a)

        response_pagamento = self.client.post(
            reverse('financeiro:registrar_pagamento_conta_pagar', args=[conta.pk]),
            data=self._payload_pagamento(),
        )
        response_cancelamento = self.client.post(
            reverse('financeiro:cancelar_conta_pagar', args=[conta.pk]),
        )

        self.assertEqual(response_pagamento.status_code, 302)
        self.assertEqual(response_cancelamento.status_code, 404)
        conta.refresh_from_db()
        self.assertEqual(conta.status, 'PAG')
        self.assertEqual(Despesas.objects.filter(origem_conta_pagar=conta).count(), 1)

    def test_edicao_post_usa_linha_bloqueada_para_validar_e_salvar(self):
        source = textwrap.dedent(inspect.getsource(financeiro_views.editar_conta_pagar))
        function = ast.parse(source).body[0]
        post_branch = next(
            statement
            for statement in function.body
            if isinstance(statement, ast.If)
            and isinstance(statement.test, ast.Compare)
            and isinstance(statement.test.left, ast.Attribute)
            and statement.test.left.attr == 'method'
        )

        calls = [node for node in ast.walk(post_branch) if isinstance(node, ast.Call)]
        self.assertTrue(any(isinstance(node.func, ast.Attribute) and node.func.attr == 'atomic' for node in calls))
        self.assertTrue(any(isinstance(node.func, ast.Attribute) and node.func.attr == 'select_for_update' for node in calls))
        form_call = next(
            node
            for node in calls
            if isinstance(node.func, ast.Name) and node.func.id == 'ContaPagarForm'
        )
        instance_keyword = next(keyword for keyword in form_call.keywords if keyword.arg == 'instance')
        self.assertIsInstance(instance_keyword.value, ast.Name)
        self.assertEqual(instance_keyword.value.id, 'conta')

    def test_cancelamento_post_usa_linha_bloqueada(self):
        source = textwrap.dedent(inspect.getsource(financeiro_views.cancelar_conta_pagar))
        function = ast.parse(source).body[0]
        post_branch = next(
            statement
            for statement in function.body
            if isinstance(statement, ast.If)
            and isinstance(statement.test, ast.Compare)
            and isinstance(statement.test.left, ast.Attribute)
            and statement.test.left.attr == 'method'
        )

        calls = [node for node in ast.walk(post_branch) if isinstance(node, ast.Call)]
        self.assertTrue(any(isinstance(node.func, ast.Attribute) and node.func.attr == 'atomic' for node in calls))
        self.assertTrue(any(isinstance(node.func, ast.Attribute) and node.func.attr == 'select_for_update' for node in calls))


class AlertaVencimentoContaPagarServiceTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Alertas',
            ativo=True,
        )
        self.usuario_financeiro = get_user_model().objects.create_user(
            username='tesoureiro_alerta',
            email='tesoureiro_alerta@example.com',
            password='senha123',
        )
        group_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)
        self.usuario_financeiro.groups.add(group_tesoureiro)

        perfil_fin, _ = PerfilUsuario.objects.get_or_create(
            user=self.usuario_financeiro,
            defaults={'ministerio': self.ministerio},
        )
        if perfil_fin.ministerio_id != self.ministerio.id:
            perfil_fin.ministerio = self.ministerio
            perfil_fin.save(update_fields=['ministerio'])
        perfil_fin.igrejas_permitidas.set([self.igreja])

        self.service = AlertaVencimentoContaPagarService()

    def test_enviar_alertas_cria_notificacao_para_dia_configurado(self):
        conta = ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            descricao='Conta D-3',
            valor=Decimal('90.00'),
            data_vencimento=date(2026, 5, 25),
            status='PEN',
        )

        with patch('financeiro.services.timezone.localdate', return_value=date(2026, 5, 22)):
            resultado = self.service.enviar_alertas(dias_alerta=(7, 3, 1), incluir_vencidas=True)

        self.assertEqual(resultado['total_notificacoes_criadas'], 1)
        notificacao = Notificacao.objects.get(user=self.usuario_financeiro, ministerio=self.ministerio)
        self.assertIn(f'[ALERTA-CP:{conta.id}:D-3]', notificacao.message)
        self.assertEqual(notificacao.notification_type, 'financeiro')

    def test_enviar_alertas_nao_duplica_mesma_notificacao(self):
        ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            descricao='Conta D-1',
            valor=Decimal('70.00'),
            data_vencimento=date(2026, 5, 23),
            status='PEN',
        )

        with patch('financeiro.services.timezone.localdate', return_value=date(2026, 5, 22)):
            primeiro = self.service.enviar_alertas(dias_alerta=(7, 3, 1), incluir_vencidas=True)
            segundo = self.service.enviar_alertas(dias_alerta=(7, 3, 1), incluir_vencidas=True)

        self.assertEqual(primeiro['total_notificacoes_criadas'], 1)
        self.assertEqual(segundo['total_notificacoes_criadas'], 0)
        self.assertGreaterEqual(segundo['total_notificacoes_existentes'], 1)
        self.assertEqual(Notificacao.objects.filter(user=self.usuario_financeiro, ministerio=self.ministerio).count(), 1)

    def test_enviar_alertas_ignora_conta_fora_dos_dias(self):
        ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            descricao='Conta Fora Regra',
            valor=Decimal('110.00'),
            data_vencimento=date(2026, 5, 28),
            status='PEN',
        )

        with patch('financeiro.services.timezone.localdate', return_value=date(2026, 5, 22)):
            resultado = self.service.enviar_alertas(dias_alerta=(7, 3, 1), incluir_vencidas=True)

        self.assertEqual(resultado['total_notificacoes_criadas'], 0)
        self.assertGreaterEqual(resultado['total_contas_fora_regra'], 1)
        self.assertEqual(Notificacao.objects.filter(user=self.usuario_financeiro, ministerio=self.ministerio).count(), 0)


class OFXPersistenciaServiceTest(BaseFinanceiroTestCase):
        def setUp(self):
                super().setUp()
                self.service = OFXImportService()
                self.conta = ContaBancaria.objects.create(
                        igreja=self.igreja,
                        nome_identificacao='Conta Bancaria OFX',
                        tipo='bancaria',
                        saldo_inicial=Decimal('1000.00'),
                )
                self.ofx_content = """OFXHEADER:100
DATA:OFXSGML
VERSION:102

<OFX>
    <BANKMSGSRSV1>
        <STMTTRNRS>
            <STMTRS>
                <BANKACCTFROM>
                    <BANKID>341
                    <ACCTID>12345-6
                    <ACCTTYPE>CHECKING
                </BANKACCTFROM>
                <BANKTRANLIST>
                    <DTSTART>20260501000000
                    <DTEND>20260531120000
                    <STMTTRN>
                        <TRNTYPE>CREDIT
                        <DTPOSTED>20260510103000
                        <TRNAMT>150.50
                        <FITID>TXN-001
                        <MEMO>Oferta culto</MEMO>
                    </STMTTRN>
                    <STMTTRN>
                        <TRNTYPE>DEBIT
                        <DTPOSTED>20260511120000
                        <TRNAMT>-45.90
                        <FITID>TXN-002
                        <CHECKNUM>9988
                        <MEMO>Tarifa bancaria</MEMO>
                    </STMTTRN>
                </BANKTRANLIST>
                <LEDGERBAL>
                    <BALAMT>104.60</BALAMT>
                    <DTASOF>20260531120000</DTASOF>
                </LEDGERBAL>
            </STMTRS>
        </STMTTRNRS>
    </BANKMSGSRSV1>
</OFX>
"""

        def test_importar_para_banco_cria_importacao_e_lancamentos(self):
                importacao = self.service.importar_para_banco(
                        self.ofx_content,
                        conta_bancaria=self.conta,
                        usuario=self.user,
                        arquivo_nome='extrato_maio.ofx',
                )

                self.assertIsInstance(importacao, ImportacaoExtratoOFX)
                self.assertEqual(importacao.conta_bancaria_id, self.conta.id)
                self.assertEqual(importacao.igreja_id, self.igreja.id)
                self.assertEqual(importacao.usuario_id, self.user.id)
                self.assertEqual(importacao.saldo_final, Decimal('104.60'))
                self.assertEqual(importacao.lancamentos.count(), 2)

                lancamento = importacao.lancamentos.order_by('data').first()
                self.assertIsInstance(lancamento, LancamentoExtratoOFX)
                self.assertEqual(lancamento.tipo, 'entrada')
                self.assertEqual(lancamento.fit_id, 'TXN-001')

        def test_importar_para_banco_rejeita_arquivo_duplicado_na_mesma_conta(self):
                self.service.importar_para_banco(
                        self.ofx_content,
                        conta_bancaria=self.conta,
                        usuario=self.user,
                        arquivo_nome='extrato_maio.ofx',
                )

                with self.assertRaises(ValueError):
                        self.service.importar_para_banco(
                                self.ofx_content,
                                conta_bancaria=self.conta,
                                usuario=self.user,
                                arquivo_nome='extrato_maio.ofx',
                        )


class OFXConciliacaoSugestaoServiceTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.service = OFXImportService()
        self.conta = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Conta Conciliacao OFX',
            tipo='bancaria',
            saldo_inicial=Decimal('0.00'),
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Conciliacao',
        )

        self.ofx_content = """OFXHEADER:100
DATA:OFXSGML
VERSION:102

<OFX>
    <BANKMSGSRSV1>
    <STMTTRNRS>
        <STMTRS>
        <BANKACCTFROM>
            <BANKID>341
            <ACCTID>99999-1
            <ACCTTYPE>CHECKING
        </BANKACCTFROM>
        <BANKTRANLIST>
            <DTSTART>20260501000000
            <DTEND>20260531120000
            <STMTTRN>
            <TRNTYPE>CREDIT
            <DTPOSTED>20260510103000
            <TRNAMT>150.50
            <FITID>SUG-ENTRADA-01
            <MEMO>Oferta culto noite
            </STMTTRN>
            <STMTTRN>
            <TRNTYPE>DEBIT
            <DTPOSTED>20260511120000
            <TRNAMT>-45.90
            <FITID>SUG-SAIDA-01
            <MEMO>Conta de agua
            </STMTTRN>
            <STMTTRN>
            <TRNTYPE>DEBIT
            <DTPOSTED>20260512090000
            <TRNAMT>-999.99
            <FITID>SUG-NOMATCH-01
            <MEMO>Sem correspondencia
            </STMTTRN>
        </BANKTRANLIST>
        <LEDGERBAL>
            <BALAMT>-895.39</BALAMT>
            <DTASOF>20260531120000</DTASOF>
        </LEDGERBAL>
        </STMTRS>
    </STMTTRNRS>
    </BANKMSGSRSV1>
</OFX>
"""

    def test_gera_sugestao_para_entrada_e_saida(self):
        importacao = self.service.importar_para_banco(
            self.ofx_content,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='conciliacao.ofx',
        )

        receita = Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 10),
            valor=Decimal('150.50'),
            conta_bancaria=self.conta,
            observacao='Oferta culto noite',
            fechado=False,
        )
        despesa = Despesas.objects.create(
            igreja=self.igreja,
            data=date(2026, 5, 11),
            descricao='Conta de agua central',
            valor=Decimal('45.90'),
            categoria=self.categoria,
            conta_bancaria=self.conta,
            fechado=False,
        )

        resultado = self.service.gerar_sugestoes_conciliacao(importacao)

        sugestao_receita = next(item for item in resultado if item['fit_id'] == 'SUG-ENTRADA-01')
        sugestao_despesa = next(item for item in resultado if item['fit_id'] == 'SUG-SAIDA-01')

        self.assertGreaterEqual(len(sugestao_receita['sugestoes']), 1)
        self.assertEqual(sugestao_receita['sugestoes'][0]['tipo'], 'receita')
        self.assertEqual(sugestao_receita['sugestoes'][0]['id'], receita.id)

        self.assertGreaterEqual(len(sugestao_despesa['sugestoes']), 1)
        self.assertEqual(sugestao_despesa['sugestoes'][0]['tipo'], 'despesa')
        self.assertEqual(sugestao_despesa['sugestoes'][0]['id'], despesa.id)

    def test_retorna_lista_vazia_quando_nao_ha_match(self):
        importacao = self.service.importar_para_banco(
            self.ofx_content,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='conciliacao.ofx',
        )

        resultado = self.service.gerar_sugestoes_conciliacao(importacao)
        sugestao_sem_match = next(item for item in resultado if item['fit_id'] == 'SUG-NOMATCH-01')

        self.assertEqual(sugestao_sem_match['sugestoes'], [])

    def test_confirmar_conciliacao_marca_lancamento_com_referencia(self):
        importacao = self.service.importar_para_banco(
            self.ofx_content,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='conciliacao.ofx',
        )
        receita = Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 10),
            valor=Decimal('150.50'),
            conta_bancaria=self.conta,
            observacao='Oferta culto noite',
            fechado=False,
        )
        lancamento = importacao.lancamentos.get(fit_id='SUG-ENTRADA-01')

        atualizado = self.service.confirmar_conciliacao(
            lancamento_id=lancamento.id,
            tipo='receita',
            referencia_id=receita.id,
            usuario=self.user,
        )

        self.assertTrue(atualizado.conciliado)
        self.assertEqual(atualizado.conciliado_tipo, 'receita')
        self.assertEqual(atualizado.conciliado_referencia_id, receita.id)
        self.assertEqual(atualizado.conciliado_por_id, self.user.id)
        self.assertIsNotNone(atualizado.conciliado_em)

    def test_confirmar_conciliacao_rejeita_valor_diferente(self):
        importacao = self.service.importar_para_banco(
            self.ofx_content,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='conciliacao.ofx',
        )
        despesa = Despesas.objects.create(
            igreja=self.igreja,
            data=date(2026, 5, 11),
            descricao='Conta de agua divergente',
            valor=Decimal('50.00'),
            categoria=self.categoria,
            conta_bancaria=self.conta,
            fechado=False,
        )
        lancamento = importacao.lancamentos.get(fit_id='SUG-SAIDA-01')

        with self.assertRaises(ValueError):
            self.service.confirmar_conciliacao(
                lancamento_id=lancamento.id,
                tipo='despesa',
                referencia_id=despesa.id,
                usuario=self.user,
            )

    def test_desfazer_conciliacao_limpa_metadados(self):
        importacao = self.service.importar_para_banco(
            self.ofx_content,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='conciliacao.ofx',
        )
        receita = Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 10),
            valor=Decimal('150.50'),
            conta_bancaria=self.conta,
            observacao='Oferta culto noite',
            fechado=False,
        )
        lancamento = importacao.lancamentos.get(fit_id='SUG-ENTRADA-01')
        self.service.confirmar_conciliacao(
            lancamento_id=lancamento.id,
            tipo='receita',
            referencia_id=receita.id,
            usuario=self.user,
        )

        atualizado = self.service.desfazer_conciliacao(lancamento_id=lancamento.id)

        self.assertFalse(atualizado.conciliado)
        self.assertEqual(atualizado.conciliado_tipo, '')
        self.assertIsNone(atualizado.conciliado_referencia_id)
        self.assertIsNone(atualizado.conciliado_por_id)
        self.assertIsNone(atualizado.conciliado_em)

    def test_conciliar_melhores_sugestoes_concilia_apenas_top_score(self):
        importacao = self.service.importar_para_banco(
            self.ofx_content,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='conciliacao_lote.ofx',
        )

        receita = Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 10),
            valor=Decimal('150.50'),
            conta_bancaria=self.conta,
            observacao='Oferta culto noite',
            fechado=False,
        )
        despesa = Despesas.objects.create(
            igreja=self.igreja,
            data=date(2026, 5, 11),
            descricao='Conta de agua central',
            valor=Decimal('45.90'),
            categoria=self.categoria,
            conta_bancaria=self.conta,
            fechado=False,
        )

        resumo = self.service.conciliar_melhores_sugestoes(
            importacao=importacao,
            usuario=self.user,
            score_minimo=90,
        )

        self.assertEqual(resumo['total_conciliados'], 2)
        self.assertEqual(resumo['total_ignorados_score'], 0)
        self.assertEqual(resumo['total_erros'], 0)

        lanc_entrada = importacao.lancamentos.get(fit_id='SUG-ENTRADA-01')
        lanc_saida = importacao.lancamentos.get(fit_id='SUG-SAIDA-01')
        lanc_sem_match = importacao.lancamentos.get(fit_id='SUG-NOMATCH-01')

        self.assertTrue(lanc_entrada.conciliado)
        self.assertEqual(lanc_entrada.conciliado_tipo, 'receita')
        self.assertEqual(lanc_entrada.conciliado_referencia_id, receita.id)

        self.assertTrue(lanc_saida.conciliado)
        self.assertEqual(lanc_saida.conciliado_tipo, 'despesa')
        self.assertEqual(lanc_saida.conciliado_referencia_id, despesa.id)

        self.assertFalse(lanc_sem_match.conciliado)

    def test_conciliar_melhores_sugestoes_dry_run_nao_persiste(self):
        importacao = self.service.importar_para_banco(
            self.ofx_content,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='conciliacao_lote_dryrun.ofx',
        )

        Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 10),
            valor=Decimal('150.50'),
            conta_bancaria=self.conta,
            observacao='Oferta culto noite',
            fechado=False,
        )
        Despesas.objects.create(
            igreja=self.igreja,
            data=date(2026, 5, 11),
            descricao='Conta de agua central',
            valor=Decimal('45.90'),
            categoria=self.categoria,
            conta_bancaria=self.conta,
            fechado=False,
        )

        resumo = self.service.conciliar_melhores_sugestoes(
            importacao=importacao,
            usuario=self.user,
            score_minimo=90,
            dry_run=True,
        )

        self.assertEqual(resumo['total_conciliados'], 2)
        self.assertGreaterEqual(len(resumo['itens_selecionados']), 2)
        self.assertEqual(resumo['resumo_impacto']['quantidade_entradas'], 1)
        self.assertEqual(resumo['resumo_impacto']['quantidade_saidas'], 1)
        self.assertEqual(resumo['resumo_impacto']['total_entradas'], Decimal('150.50'))
        self.assertEqual(resumo['resumo_impacto']['total_saidas'], Decimal('45.90'))
        self.assertEqual(resumo['resumo_impacto']['total_movimentado'], Decimal('196.40'))
        self.assertEqual(resumo['resumo_impacto']['saldo_previsto'], Decimal('104.60'))
        self.assertEqual(importacao.lancamentos.filter(conciliado=True).count(), 0)


class OFXConciliacaoViewTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.service = OFXImportService()
        self.conta = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Conta View OFX',
            tipo='bancaria',
            saldo_inicial=Decimal('100.00'),
        )
        self.ofx_content = """OFXHEADER:100
DATA:OFXSGML
VERSION:102

<OFX>
    <BANKMSGSRSV1>
        <STMTTRNRS>
            <STMTRS>
                <BANKACCTFROM>
                    <BANKID>341
                    <ACCTID>11111-1
                    <ACCTTYPE>CHECKING
                </BANKACCTFROM>
                <BANKTRANLIST>
                    <DTSTART>20260501000000
                    <DTEND>20260531120000
                    <STMTTRN>
                        <TRNTYPE>CREDIT
                        <DTPOSTED>20260510103000
                        <TRNAMT>150.50
                        <FITID>VIEW-ENTRADA-01
                        <MEMO>Oferta culto noite
                    </STMTTRN>
                </BANKTRANLIST>
                <LEDGERBAL>
                    <BALAMT>150.50
                    <DTASOF>20260531120000
                </LEDGERBAL>
            </STMTRS>
        </STMTTRNRS>
    </BANKMSGSRSV1>
</OFX>
"""

    def test_view_conciliacao_ofx_renderiza(self):
        response = self.client.get(reverse('financeiro:conciliacao_ofx'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'financeiro/ofx/conciliacao_ofx.html')

    def test_view_conciliacao_ofx_confirma_match(self):
        importacao = self.service.importar_para_banco(
            self.ofx_content,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='view_conciliacao.ofx',
        )
        receita = Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 10),
            valor=Decimal('150.50'),
            conta_bancaria=self.conta,
            observacao='Oferta culto noite',
            fechado=False,
        )
        lancamento = importacao.lancamentos.get(fit_id='VIEW-ENTRADA-01')

        response = self.client.post(
            reverse('financeiro:conciliacao_ofx'),
            data={
                'importacao_id': importacao.id,
                'lancamento_id': lancamento.id,
                'tipo': 'receita',
                'referencia_id': receita.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        lancamento.refresh_from_db()
        self.assertTrue(lancamento.conciliado)
        self.assertEqual(lancamento.conciliado_tipo, 'receita')
        self.assertEqual(lancamento.conciliado_referencia_id, receita.id)

    def test_view_conciliacao_ofx_desfaz_match(self):
        importacao = self.service.importar_para_banco(
            self.ofx_content,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='view_conciliacao.ofx',
        )
        receita = Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 10),
            valor=Decimal('150.50'),
            conta_bancaria=self.conta,
            observacao='Oferta culto noite',
            fechado=False,
        )
        lancamento = importacao.lancamentos.get(fit_id='VIEW-ENTRADA-01')
        self.service.confirmar_conciliacao(
            lancamento_id=lancamento.id,
            tipo='receita',
            referencia_id=receita.id,
            usuario=self.user,
        )

        response = self.client.post(
            reverse('financeiro:conciliacao_ofx'),
            data={
                'acao': 'desfazer',
                'importacao_id': importacao.id,
                'lancamento_id': lancamento.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        lancamento.refresh_from_db()
        self.assertFalse(lancamento.conciliado)
        self.assertEqual(lancamento.conciliado_tipo, '')

    def test_view_conciliacao_ofx_vinculo_manual_despesa(self):
        ofx_saida = """OFXHEADER:100
DATA:OFXSGML
VERSION:102

<OFX>
    <BANKMSGSRSV1>
        <STMTTRNRS>
            <STMTRS>
                <BANKACCTFROM>
                    <BANKID>341
                    <ACCTID>11111-1
                    <ACCTTYPE>CHECKING
                </BANKACCTFROM>
                <BANKTRANLIST>
                    <DTSTART>20260501000000
                    <DTEND>20260531120000
                    <STMTTRN>
                        <TRNTYPE>DEBIT
                        <DTPOSTED>20260512103000
                        <TRNAMT>-70.00
                        <FITID>VIEW-SAIDA-01
                        <MEMO>Pagamento manual
                    </STMTTRN>
                </BANKTRANLIST>
                <LEDGERBAL>
                    <BALAMT>30.00
                    <DTASOF>20260531120000
                </LEDGERBAL>
            </STMTRS>
        </STMTTRNRS>
    </BANKMSGSRSV1>
</OFX>
"""
        importacao = self.service.importar_para_banco(
            ofx_saida,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='view_manual.ofx',
        )
        categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Manual View',
        )
        despesa = Despesas.objects.create(
            igreja=self.igreja,
            data=date(2026, 5, 12),
            descricao='Pagamento manual',
            valor=Decimal('70.00'),
            categoria=categoria,
            conta_bancaria=self.conta,
            fechado=False,
        )
        lancamento = importacao.lancamentos.get(fit_id='VIEW-SAIDA-01')

        response = self.client.post(
            reverse('financeiro:conciliacao_ofx'),
            data={
                'acao': 'confirmar',
                'importacao_id': importacao.id,
                'lancamento_id': lancamento.id,
                'tipo': 'despesa',
                'referencia_id': despesa.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        lancamento.refresh_from_db()
        self.assertTrue(lancamento.conciliado)
        self.assertEqual(lancamento.conciliado_tipo, 'despesa')
        self.assertEqual(lancamento.conciliado_referencia_id, despesa.id)

    def test_view_conciliacao_ofx_concilia_melhores_em_lote(self):
        importacao = self.service.importar_para_banco(
            self.ofx_content,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='view_lote.ofx',
        )
        receita = Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 10),
            valor=Decimal('150.50'),
            conta_bancaria=self.conta,
            observacao='Oferta culto noite',
            fechado=False,
        )
        lancamento = importacao.lancamentos.get(fit_id='VIEW-ENTRADA-01')

        response = self.client.post(
            reverse('financeiro:conciliacao_ofx'),
            data={
                'acao': 'conciliar_melhores',
                'importacao_id': importacao.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        lancamento.refresh_from_db()
        self.assertTrue(lancamento.conciliado)
        self.assertEqual(lancamento.conciliado_tipo, 'receita')
        self.assertEqual(lancamento.conciliado_referencia_id, receita.id)

    def test_view_conciliacao_ofx_previsualiza_melhores_sem_conciliar(self):
        importacao = self.service.importar_para_banco(
            self.ofx_content,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='view_preview_lote.ofx',
        )
        Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 10),
            valor=Decimal('150.50'),
            conta_bancaria=self.conta,
            observacao='Oferta culto noite',
            fechado=False,
        )
        lancamento = importacao.lancamentos.get(fit_id='VIEW-ENTRADA-01')

        response = self.client.post(
            reverse('financeiro:conciliacao_ofx'),
            data={
                'acao': 'previsualizar_melhores',
                'importacao_id': importacao.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pré-visualização do lote')
        self.assertContains(response, 'Saldo previsto')
        self.assertIn('previsao_lote', response.context)
        self.assertGreaterEqual(response.context['previsao_lote']['total_conciliados'], 1)
        lancamento.refresh_from_db()
        self.assertFalse(lancamento.conciliado)

    def test_view_conciliacao_ofx_lote_respeita_score_minimo(self):
        importacao = self.service.importar_para_banco(
            self.ofx_content,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='view_score_minimo.ofx',
        )
        Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 10),
            valor=Decimal('150.50'),
            conta_bancaria=self.conta,
            observacao='Oferta culto noite',
            fechado=False,
        )
        lancamento = importacao.lancamentos.get(fit_id='VIEW-ENTRADA-01')

        response = self.client.post(
            reverse('financeiro:conciliacao_ofx'),
            data={
                'acao': 'conciliar_melhores',
                'importacao_id': importacao.id,
                'score_minimo': '130',
            },
        )

        self.assertEqual(response.status_code, 302)
        lancamento.refresh_from_db()
        self.assertFalse(lancamento.conciliado)

    def test_view_conciliacao_ofx_exporta_previsao_csv(self):
        importacao = self.service.importar_para_banco(
            self.ofx_content,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='view_export_csv.ofx',
        )
        Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 10),
            valor=Decimal('150.50'),
            conta_bancaria=self.conta,
            observacao='Oferta culto noite',
            fechado=False,
        )

        response = self.client.post(
            reverse('financeiro:conciliacao_ofx'),
            data={
                'acao': 'exportar_previsao_csv',
                'importacao_id': importacao.id,
                'score_minimo': '90',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])
        self.assertIn('attachment; filename=', response['Content-Disposition'])

        payload = response.content.decode('utf-8')
        self.assertIn('lancamento_id_ofx,fit_id,tipo_ofx', payload)
        self.assertIn('resumo', payload)
        self.assertIn('saldo_previsto', payload)

    def test_view_conciliacao_ofx_exporta_previsao_xlsx(self):
        importacao = self.service.importar_para_banco(
            self.ofx_content,
            conta_bancaria=self.conta,
            usuario=self.user,
            arquivo_nome='view_export_xlsx.ofx',
        )
        Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 10),
            valor=Decimal('150.50'),
            conta_bancaria=self.conta,
            observacao='Oferta culto noite',
            fechado=False,
        )

        response = self.client.post(
            reverse('financeiro:conciliacao_ofx'),
            data={
                'acao': 'exportar_previsao_xlsx',
                'importacao_id': importacao.id,
                'score_minimo': '90',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            response['Content-Type'],
        )
        self.assertIn('attachment; filename=', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b'PK'))


class ContaBancariaViewTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        grupo_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)
        self.user.groups.add(grupo_tesoureiro)
        perfil, _ = PerfilUsuario.objects.get_or_create(
            user=self.user,
            defaults={'ministerio': self.ministerio},
        )
        if perfil.ministerio_id != self.ministerio.id:
            perfil.ministerio = self.ministerio
            perfil.save(update_fields=['ministerio'])
        perfil.igrejas_permitidas.set([self.igreja])
        self.client.force_login(self.user)
        self.conta_bancaria = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Banco Principal',
            tipo='bancaria',
            instituicao_bancaria='Banco Teste',
            agencia='1234',
            conta='0001-9',
            saldo_inicial=Decimal('1000.00'),
        )
        self.caixa_fisico = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Caixa Tesouraria',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('500.00'),
        )

    def test_lista_contas_bancarias_renderiza_com_resumo(self):
        response = self.client.get(reverse('financeiro:lista_contas_bancarias'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'financeiro/contas_bancarias/lista_contas_bancarias.html')

        contas_contexto = list(response.context['contas_bancarias'])
        self.assertGreaterEqual(response.context['resumo_quantidade'], 2)
        self.assertEqual(response.context['resumo_quantidade'], len(contas_contexto))

        total_bancarias = len([conta for conta in contas_contexto if conta.tipo == 'bancaria'])
        total_caixas = len([conta for conta in contas_contexto if conta.tipo == 'caixa_fisico'])
        self.assertEqual(response.context['resumo_total_bancarias'], total_bancarias)
        self.assertEqual(response.context['resumo_total_caixas'], total_caixas)

    def test_lista_contas_bancarias_filtra_por_tipo(self):
        response = self.client.get(reverse('financeiro:lista_contas_bancarias'), {'tipo': 'caixa_fisico'})

        self.assertEqual(response.status_code, 200)
        contas = list(response.context['contas_bancarias'])
        self.assertGreaterEqual(len(contas), 1)
        self.assertTrue(any(conta.id == self.caixa_fisico.id for conta in contas))
        self.assertTrue(all(conta.tipo == 'caixa_fisico' for conta in contas))

    def test_lista_contas_bancarias_filtra_por_busca(self):
        response = self.client.get(reverse('financeiro:lista_contas_bancarias'), {'q': 'Banco Principal'})

        self.assertEqual(response.status_code, 200)
        contas = list(response.context['contas_bancarias'])
        self.assertGreaterEqual(len(contas), 1)
        self.assertTrue(any(conta.id == self.conta_bancaria.id for conta in contas))


class ContaBancariaEscopoExplicitoTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.grupo_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)
        self.admin_ministerio_1 = User.objects.create_user(username='admin-contas-escopo-1')
        self.admin_ministerio_2 = User.objects.create_user(username='admin-contas-escopo-2')
        self.usuario = User.objects.create_user(
            username='tesoureiro-contas-escopo',
            password='senha123',
        )
        self.usuario.groups.add(self.grupo_tesoureiro)

        self.ministerio_1 = Ministerio.objects.create(
            nome_fantasia='Ministerio Contas Escopo 1',
            administrador_principal=self.admin_ministerio_1,
            ativo=True,
        )
        self.ministerio_2 = Ministerio.objects.create(
            nome_fantasia='Ministerio Contas Escopo 2',
            administrador_principal=self.admin_ministerio_2,
            ativo=True,
        )
        self.igreja_a = Igreja.objects.create(
            ministerio=self.ministerio_1,
            nome_igreja='Igreja A Contas Escopo',
            tipo_igreja='sede',
        )
        self.igreja_b = Igreja.objects.create(
            ministerio=self.ministerio_1,
            nome_igreja='Igreja B Contas Escopo',
            tipo_igreja='regional',
            igreja_superior=self.igreja_a,
        )
        self.igreja_regional_filha = Igreja.objects.create(
            ministerio=self.ministerio_1,
            nome_igreja='Igreja Regional Filha Contas Escopo',
            tipo_igreja='congregacao',
            igreja_superior=self.igreja_b,
        )
        self.igreja_c = Igreja.objects.create(
            ministerio=self.ministerio_2,
            nome_igreja='Igreja C Contas Escopo',
            tipo_igreja='sede',
        )
        self.perfil = PerfilUsuario.objects.create(
            user=self.usuario,
            ministerio=self.ministerio_1,
        )
        self.perfil.igrejas_permitidas.add(self.igreja_a)

        Plano.objects.get_or_create(
            nome='pioneiro',
            defaults={
                'codigo_plano': 'pioneiro',
                'permite_modulo_financeiro': True,
                'ativo': True,
            },
        )
        self.conta_a = ContaBancaria.objects.create(
            igreja=self.igreja_a,
            nome_identificacao='Caixa Igreja A',
            tipo='caixa_fisico',
        )
        self.conta_b = ContaBancaria.objects.create(
            igreja=self.igreja_b,
            nome_identificacao='Caixa Igreja B',
            tipo='caixa_fisico',
        )
        self.conta_c = ContaBancaria.objects.create(
            igreja=self.igreja_c,
            nome_identificacao='Caixa Igreja C',
            tipo='caixa_fisico',
        )
        self.conta_regional_filha = ContaBancaria.objects.create(
            igreja=self.igreja_regional_filha,
            nome_identificacao='Caixa Igreja Regional Filha',
            tipo='caixa_fisico',
        )
        self.client.force_login(self.usuario)

    def _payload_conta(self, igreja, nome):
        return {
            'igreja': str(igreja.pk),
            'nome_identificacao': nome,
            'tipo': 'bancaria',
            'instituicao_bancaria': 'Banco de Teste',
            'agencia': '1234',
            'conta': '0001-9',
            'saldo_inicial': '100.00',
        }

    def test_forms_expoem_somente_o_write_scope_explicito_e_fecham_sem_escopo(self):
        for form_class in (ContaBancariaForm, ReceitaForm, DespesaForm):
            form = form_class(
                ministerio=self.ministerio_1,
                user=self.usuario,
                allowed_churches=Igreja.objects.filter(pk=self.igreja_a.pk),
            )
            self.assertQuerySetEqual(form.fields['igreja'].queryset.order_by('pk'), [self.igreja_a])

            form = form_class(
                ministerio=self.ministerio_1,
                user=self.usuario,
                allowed_churches=Igreja.objects.filter(pk=self.igreja_b.pk),
            )
            self.assertQuerySetEqual(form.fields['igreja'].queryset.order_by('pk'), [self.igreja_b])

            form = form_class(
                ministerio=self.ministerio_1,
                user=self.usuario,
                allowed_churches=Igreja.objects.none(),
            )
            self.assertFalse(form.fields['igreja'].queryset.exists())

    def test_lista_contas_com_escopo_vazio_falha_fechado(self):
        self.perfil.igrejas_permitidas.clear()

        response = self.client.get(reverse('financeiro:lista_contas_bancarias'))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['contas_bancarias'].exists())
        self.assertEqual(response.context['resumo_quantidade'], 0)

    def test_lista_contas_retorna_somente_igreja_expressamente_permitida(self):
        response = self.client.get(reverse('financeiro:lista_contas_bancarias'))

        self.assertEqual(response.status_code, 200)
        contas = response.context['contas_bancarias']
        self.assertIn(self.conta_a, contas)
        self.assertTrue(all(conta.igreja_id == self.igreja_a.pk for conta in contas))
        self.assertNotIn(self.conta_b, contas)
        self.assertNotIn(self.conta_c, contas)

    def test_criar_conta_permite_igreja_expressamente_autorizada(self):
        response = self.client.post(
            reverse('financeiro:criar_conta_bancaria'),
            data=self._payload_conta(self.igreja_a, 'Conta Criada Igreja A'),
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ContaBancaria.objects.filter(
                igreja=self.igreja_a,
                nome_identificacao='Conta Criada Igreja A',
            ).exists()
        )

    def test_criar_conta_bloqueia_tampering_para_igreja_mesmo_ministerio_fora_do_escopo(self):
        response = self.client.post(
            reverse('financeiro:criar_conta_bancaria'),
            data=self._payload_conta(self.igreja_b, 'Conta Tampering Igreja B'),
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            ContaBancaria.objects.filter(
                igreja=self.igreja_b,
                nome_identificacao='Conta Tampering Igreja B',
            ).exists()
        )

    def test_criar_conta_bloqueia_tampering_para_igreja_de_outro_ministerio(self):
        response = self.client.post(
            reverse('financeiro:criar_conta_bancaria'),
            data=self._payload_conta(self.igreja_c, 'Conta Tampering Igreja C'),
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            ContaBancaria.objects.filter(
                igreja=self.igreja_c,
                nome_identificacao='Conta Tampering Igreja C',
            ).exists()
        )

    def test_editar_conta_bloqueia_idor_mesmo_ministerio_e_outro_ministerio(self):
        for conta in (self.conta_b, self.conta_c):
            url = reverse('financeiro:editar_conta_bancaria', args=[conta.pk])
            original = conta.nome_identificacao

            response_get = self.client.get(url)
            response_post = self.client.post(
                url,
                data=self._payload_conta(conta.igreja, f'{original} adulterada'),
            )

            self.assertEqual(response_get.status_code, 404)
            self.assertEqual(response_post.status_code, 404)
            conta.refresh_from_db()
            self.assertEqual(conta.nome_identificacao, original)

    def test_excluir_conta_bloqueia_idor_mesmo_ministerio_e_outro_ministerio(self):
        for conta in (self.conta_b, self.conta_c):
            response = self.client.post(
                reverse('financeiro:excluir_conta_bancaria', args=[conta.pk]),
            )

            self.assertEqual(response.status_code, 404)
            self.assertTrue(ContaBancaria.objects.filter(pk=conta.pk).exists())

    def test_regional_com_escopo_explicito_nao_ganha_acesso_a_igreja_filha(self):
        usuario_regional = get_user_model().objects.create_user(
            username='tesoureiro-regional-contas-escopo',
            password='senha123',
        )
        grupo_regional, _ = Group.objects.get_or_create(name=PASTOR_REGIONAL)
        usuario_regional.groups.add(grupo_regional, self.grupo_tesoureiro)
        perfil_regional = PerfilUsuario.objects.create(
            user=usuario_regional,
            ministerio=self.ministerio_1,
        )
        perfil_regional.igrejas_permitidas.set([self.igreja_b])
        self.client.force_login(usuario_regional)

        response_create = self.client.post(
            reverse('financeiro:criar_conta_bancaria'),
            data=self._payload_conta(
                self.igreja_regional_filha,
                'Conta Regional Filha Bloqueada',
            ),
        )
        response_edit = self.client.post(
            reverse('financeiro:editar_conta_bancaria', args=[self.conta_regional_filha.pk]),
            data=self._payload_conta(
                self.igreja_regional_filha,
                'Conta Regional Filha Alterada',
            ),
        )
        response_delete = self.client.post(
            reverse('financeiro:excluir_conta_bancaria', args=[self.conta_regional_filha.pk]),
        )

        self.assertEqual(response_create.status_code, 302)
        self.assertEqual(response_edit.status_code, 404)
        self.assertEqual(response_delete.status_code, 404)
        self.assertFalse(
            ContaBancaria.objects.filter(
                igreja=self.igreja_regional_filha,
                nome_identificacao='Conta Regional Filha Bloqueada',
            ).exists()
        )
        self.conta_regional_filha.refresh_from_db()
        self.assertEqual(self.conta_regional_filha.nome_identificacao, 'Caixa Igreja Regional Filha')

    def test_crud_conta_falha_fechado_com_escopo_vazio(self):
        self.perfil.igrejas_permitidas.clear()

        response_create = self.client.post(
            reverse('financeiro:criar_conta_bancaria'),
            data=self._payload_conta(self.igreja_a, 'Conta Escopo Vazio'),
        )
        response_edit = self.client.post(
            reverse('financeiro:editar_conta_bancaria', args=[self.conta_a.pk]),
            data=self._payload_conta(self.igreja_a, 'Conta A Alterada Sem Escopo'),
        )
        response_delete = self.client.post(
            reverse('financeiro:excluir_conta_bancaria', args=[self.conta_a.pk]),
        )

        self.assertEqual(response_create.status_code, 302)
        self.assertEqual(response_edit.status_code, 404)
        self.assertEqual(response_delete.status_code, 404)
        self.assertFalse(ContaBancaria.objects.filter(nome_identificacao='Conta Escopo Vazio').exists())
        self.conta_a.refresh_from_db()
        self.assertEqual(self.conta_a.nome_identificacao, 'Caixa Igreja A')

    def test_gerenciar_permissoes_caixa_bloqueia_igreja_do_mesmo_ministerio_fora_do_escopo(self):
        response = self.client.get(
            reverse('financeiro:gerenciar_permissoes_caixa', args=[self.conta_b.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_gerenciar_permissoes_caixa_bloqueia_escopo_vazio(self):
        self.perfil.igrejas_permitidas.clear()

        response = self.client.get(
            reverse('financeiro:gerenciar_permissoes_caixa', args=[self.conta_a.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_gerenciar_permissoes_caixa_permite_igreja_expressamente_autorizada(self):
        response = self.client.get(
            reverse('financeiro:gerenciar_permissoes_caixa', args=[self.conta_a.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['caixa'], self.conta_a)

    def test_gerenciar_permissoes_caixa_bloqueia_caixa_de_outro_ministerio(self):
        response = self.client.get(
            reverse('financeiro:gerenciar_permissoes_caixa', args=[self.conta_c.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_post_permissoes_ignora_usuario_da_igreja_b_do_mesmo_ministerio(self):
        usuario_igreja_b = get_user_model().objects.create_user(
            username='usuario-igreja-b-permissao-caixa',
        )
        perfil_igreja_b = PerfilUsuario.objects.create(
            user=usuario_igreja_b,
            ministerio=self.ministerio_1,
        )
        perfil_igreja_b.igrejas_permitidas.add(self.igreja_b)

        response = self.client.post(
            reverse('financeiro:gerenciar_permissoes_caixa', args=[self.conta_a.pk]),
            data={
                f'user_{usuario_igreja_b.pk}_visualizar': 'on',
                f'user_{usuario_igreja_b.pk}_transferir': 'on',
                f'user_{usuario_igreja_b.pk}_editar': 'on',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            PermissaoCaixa.objects.filter(
                usuario=usuario_igreja_b,
                caixa=self.conta_a,
            ).exists()
        )

    def test_post_permissoes_ignora_usuario_de_outro_ministerio(self):
        usuario_igreja_c = get_user_model().objects.create_user(
            username='usuario-igreja-c-permissao-caixa',
        )
        perfil_igreja_c = PerfilUsuario.objects.create(
            user=usuario_igreja_c,
            ministerio=self.ministerio_2,
        )
        perfil_igreja_c.igrejas_permitidas.add(self.igreja_c)

        response = self.client.post(
            reverse('financeiro:gerenciar_permissoes_caixa', args=[self.conta_a.pk]),
            data={f'user_{usuario_igreja_c.pk}_visualizar': 'on'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            PermissaoCaixa.objects.filter(
                usuario=usuario_igreja_c,
                caixa=self.conta_a,
            ).exists()
        )

    def test_post_permissoes_ignora_usuario_sem_igreja_explicita(self):
        usuario_sem_igreja = get_user_model().objects.create_user(
            username='usuario-sem-igreja-permissao-caixa',
        )
        PerfilUsuario.objects.create(
            user=usuario_sem_igreja,
            ministerio=self.ministerio_1,
        )

        response = self.client.post(
            reverse('financeiro:gerenciar_permissoes_caixa', args=[self.conta_a.pk]),
            data={f'user_{usuario_sem_igreja.pk}_visualizar': 'on'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            PermissaoCaixa.objects.filter(
                usuario=usuario_sem_igreja,
                caixa=self.conta_a,
            ).exists()
        )

    def test_post_permissoes_cria_permissao_para_usuario_da_igreja_autorizada(self):
        usuario_igreja_a = get_user_model().objects.create_user(
            username='usuario-igreja-a-permissao-caixa',
        )
        perfil_igreja_a = PerfilUsuario.objects.create(
            user=usuario_igreja_a,
            ministerio=self.ministerio_1,
        )
        perfil_igreja_a.igrejas_permitidas.add(self.igreja_a)

        response = self.client.post(
            reverse('financeiro:gerenciar_permissoes_caixa', args=[self.conta_a.pk]),
            data={
                f'user_{usuario_igreja_a.pk}_visualizar': 'on',
                f'user_{usuario_igreja_a.pk}_transferir': 'on',
                f'user_{usuario_igreja_a.pk}_editar': 'on',
            },
        )

        self.assertEqual(response.status_code, 302)
        permissao = PermissaoCaixa.objects.get(
            usuario=usuario_igreja_a,
            caixa=self.conta_a,
        )
        self.assertTrue(permissao.pode_visualizar)
        self.assertTrue(permissao.pode_transferir)
        self.assertTrue(permissao.pode_editar)


class ReceitasViewTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        group_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)
        self.user.groups.add(group_tesoureiro)
        self.perfil, _ = PerfilUsuario.objects.get_or_create(
            user=self.user,
            defaults={'ministerio': self.ministerio},
        )
        if self.perfil.ministerio_id != self.ministerio.id:
            self.perfil.ministerio = self.ministerio
            self.perfil.save(update_fields=['ministerio'])
        self.perfil.igrejas_permitidas.set([self.igreja])

        self.client.force_login(self.user)
        self.conta = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Conta Receitas View',
            tipo='bancaria',
            saldo_inicial=Decimal('0.00'),
        )
        self.outra_igreja = Igreja.objects.create(
            nome_igreja='Igreja Financeiro Filial',
            ministerio=self.ministerio,
            tipo_igreja='congregacao',
        )
        self.conta_outra_igreja = ContaBancaria.objects.create(
            igreja=self.outra_igreja,
            nome_identificacao='Conta Receitas Outra Igreja',
            tipo='bancaria',
            saldo_inicial=Decimal('0.00'),
        )
        Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 10),
            valor=Decimal('100.00'),
            conta_bancaria=self.conta,
            fechado=False,
        )
        Receitas.objects.create(
            igreja=self.igreja,
            categoria='dizimo',
            data=date(2026, 5, 11),
            valor=Decimal('50.00'),
            conta_bancaria=self.conta,
            fechado=True,
        )

    def test_lista_receitas_exibe_resumo_financeiro(self):
        response = self.client.get(reverse('financeiro:lista_receitas'), {'fechado': 'todos'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'financeiro/receitas/lista_receitas.html')
        self.assertEqual(response.context['resumo_total_periodo'], Decimal('150.00'))
        self.assertEqual(response.context['resumo_total_aberto'], Decimal('100.00'))
        self.assertEqual(response.context['resumo_ticket_medio'], Decimal('75.00'))
        self.assertEqual(response.context['resumo_quantidade_periodo'], 2)

    def test_lista_receitas_exibe_resumo_dizimos_e_ofertas_por_forma_pagamento(self):
        Receitas.objects.create(
            igreja=self.igreja,
            categoria='dizimo',
            data=date(2026, 5, 12),
            valor=Decimal('30.00'),
            conta_bancaria=self.conta,
            forma_pgto='DIN',
            fechado=False,
        )
        Receitas.objects.create(
            igreja=self.igreja,
            categoria='dizimo',
            data=date(2026, 5, 13),
            valor=Decimal('20.00'),
            conta_bancaria=self.conta,
            forma_pgto='PIX',
            fechado=False,
        )
        Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 14),
            valor=Decimal('40.00'),
            conta_bancaria=self.conta,
            forma_pgto='DIN',
            fechado=False,
        )
        Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 5, 15),
            valor=Decimal('10.00'),
            conta_bancaria=self.conta,
            forma_pgto='PIX',
            fechado=False,
        )

        response = self.client.get(reverse('financeiro:lista_receitas'), {'fechado': 'todos'})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['exibir_cards_dizimos_ofertas'])
        self.assertEqual(response.context['dizimos_dinheiro'], Decimal('30.00'))
        self.assertEqual(response.context['dizimos_pix'], Decimal('20.00'))
        self.assertEqual(response.context['dizimos_total'], Decimal('100.00'))
        self.assertEqual(response.context['ofertas_dinheiro'], Decimal('40.00'))
        self.assertEqual(response.context['ofertas_pix'], Decimal('10.00'))
        self.assertEqual(response.context['ofertas_total'], Decimal('150.00'))

    def test_lista_receitas_exibe_cards_dizimos_ofertas_apenas_para_fundo_local(self):
        fundo_local = FundoDepartamental.objects.get(
            igreja=self.igreja,
            codigo=FundoDepartamental.CODIGO_LOCAL,
        )
        fundo_eventos = FundoDepartamental.objects.get(
            igreja=self.igreja,
            codigo=FundoDepartamental.CODIGO_EVENTOS,
        )

        response_local = self.client.get(
            reverse('financeiro:lista_receitas'),
            {'fechado': 'todos', 'fundo_filtro': str(fundo_local.pk)},
        )
        self.assertEqual(response_local.status_code, 200)
        self.assertTrue(response_local.context['exibir_cards_dizimos_ofertas'])

        response_eventos = self.client.get(
            reverse('financeiro:lista_receitas'),
            {'fechado': 'todos', 'fundo_filtro': str(fundo_eventos.pk)},
        )
        self.assertEqual(response_eventos.status_code, 200)
        self.assertFalse(response_eventos.context['exibir_cards_dizimos_ofertas'])

    def test_lista_receitas_restringe_caixas_e_dados_a_igreja_ativa(self):
        self.perfil.igrejas_permitidas.set([self.igreja, self.outra_igreja])
        Receitas.objects.create(
            igreja=self.outra_igreja,
            categoria='oferta',
            data=date(2026, 5, 16),
            valor=Decimal('200.00'),
            conta_bancaria=self.conta_outra_igreja,
            fechado=False,
        )
        request = self.factory.get(reverse('financeiro:lista_receitas'), {'fechado': 'todos'})
        request.user = self.user
        request.session = {}
        request.igreja_ativa = self.igreja

        def fake_render(_request, _template, context):
            response = HttpResponse(status=200)
            response.context = context
            return response

        with patch('contas.page_permissions.user_can_access_page', return_value=True), patch('financeiro.views.render', side_effect=fake_render):
            response = lista_receitas(request)

        self.assertEqual(response.status_code, 200)
        contas_ids = list(response.context['contas_bancarias_painel'].values_list('id', flat=True))
        self.assertIn(self.conta.id, contas_ids)
        self.assertNotIn(self.conta_outra_igreja.id, contas_ids)
        self.assertTrue(all(conta.igreja_id == self.igreja.id for conta in response.context['contas_bancarias_painel']))
        self.assertTrue(all(receita.igreja_id == self.igreja.id for receita in response.context['receitas']))


class DespesasViewTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        group_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)
        self.user.groups.add(group_tesoureiro)
        self.perfil, _ = PerfilUsuario.objects.get_or_create(
            user=self.user,
            defaults={'ministerio': self.ministerio},
        )
        if self.perfil.ministerio_id != self.ministerio.id:
            self.perfil.ministerio = self.ministerio
            self.perfil.save(update_fields=['ministerio'])
        self.perfil.igrejas_permitidas.set([self.igreja])

        self.client.force_login(self.user)
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Operacional',
        )
        self.conta = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Conta Despesas View',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('500.00'),
        )
        self.outra_igreja = Igreja.objects.create(
            nome_igreja='Igreja Financeiro Apoio',
            ministerio=self.ministerio,
            tipo_igreja='congregacao',
        )
        self.conta_outra_igreja = ContaBancaria.objects.create(
            igreja=self.outra_igreja,
            nome_identificacao='Conta Despesas Outra Igreja',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('500.00'),
        )
        Despesas.objects.create(
            igreja=self.igreja,
            data=date(2026, 5, 10),
            descricao='Conta de Agua',
            valor=Decimal('100.00'),
            categoria=self.categoria,
            conta_bancaria=self.conta,
            fechado=False,
        )
        Despesas.objects.create(
            igreja=self.igreja,
            data=date(2026, 5, 11),
            descricao='Conta de Luz',
            valor=Decimal('50.00'),
            categoria=self.categoria,
            conta_bancaria=self.conta,
            fechado=True,
        )

    def test_lista_despesas_exibe_resumo_financeiro(self):
        response = self.client.get(reverse('financeiro:lista_despesas'), {'fechado': 'todos'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'financeiro/despesas/lista_despesas.html')
        self.assertEqual(response.context['resumo_total_periodo'], Decimal('150.00'))
        self.assertEqual(response.context['resumo_total_aberto'], Decimal('100.00'))
        self.assertEqual(response.context['resumo_ticket_medio'], Decimal('75.00'))
        self.assertEqual(response.context['resumo_quantidade_periodo'], 2)
        self.assertEqual(response.context['resumos_categoria']['Operacional'], Decimal('150.00'))

    def test_lista_despesas_restringe_caixas_e_dados_a_igreja_ativa(self):
        self.perfil.igrejas_permitidas.set([self.igreja, self.outra_igreja])
        Despesas.objects.create(
            igreja=self.outra_igreja,
            data=date(2026, 5, 16),
            descricao='Despesa Outra Igreja',
            valor=Decimal('200.00'),
            categoria=self.categoria,
            conta_bancaria=self.conta_outra_igreja,
            fechado=False,
        )
        request = self.factory.get(reverse('financeiro:lista_despesas'), {'fechado': 'todos'})
        request.user = self.user
        request.session = {}
        request.igreja_ativa = self.igreja

        def fake_render(_request, _template, context):
            response = HttpResponse(status=200)
            response.context = context
            return response

        with patch('contas.page_permissions.user_can_access_page', return_value=True), patch('financeiro.views.render', side_effect=fake_render):
            response = lista_despesas(request)

        self.assertEqual(response.status_code, 200)
        contas_ids = list(response.context['contas_bancarias_painel'].values_list('id', flat=True))
        self.assertIn(self.conta.id, contas_ids)
        self.assertNotIn(self.conta_outra_igreja.id, contas_ids)
        self.assertTrue(all(conta.igreja_id == self.igreja.id for conta in response.context['contas_bancarias_painel']))
        self.assertTrue(all(despesa.igreja_id == self.igreja.id for despesa in response.context['despesas']))

    def test_cadastrar_despesa_persiste_criador_e_ignora_post_adulterado(self):
        outro_usuario = get_user_model().objects.create_user(
            username='outro_usuario_criador_despesa',
            password='senha123',
        )

        response = self.client.post(
            reverse('financeiro:cadastrar_despesa'),
            data={
                'igreja': str(self.igreja.pk),
                'categoria': str(self.categoria.pk),
                'data': '2026-10-15',
                'valor': '25.00',
                'descricao': 'Despesa criada pela view',
                'conta_bancaria': str(self.conta.pk),
                'observacao': '',
                'criado_por': str(outro_usuario.pk),
            },
        )

        self.assertEqual(response.status_code, 302)
        despesa = Despesas.objects.get(descricao='Despesa criada pela view')
        self.assertEqual(despesa.criado_por, self.user)

    def test_cadastro_lote_persiste_criador_para_todas_as_despesas(self):
        session = self.client.session
        session[f'financeiro_batch_despesas_{self.igreja.pk}'] = [
            {
                'id': 'despesa-lote-1',
                'data': '2026-10-15',
                'categoria': str(self.categoria.pk),
                'valor': '11.00',
                'descricao': 'Despesa lote criador 1',
                'evento': '',
                'conta_bancaria': str(self.conta.pk),
                'observacao': '',
            },
            {
                'id': 'despesa-lote-2',
                'data': '2026-10-15',
                'categoria': str(self.categoria.pk),
                'valor': '12.00',
                'descricao': 'Despesa lote criador 2',
                'evento': '',
                'conta_bancaria': str(self.conta.pk),
                'observacao': '',
            },
        ]
        session.save()

        response = self.client.post(
            reverse('financeiro:cadastrar_despesa'),
            data={'action': 'batch_save'},
        )

        self.assertEqual(response.status_code, 302)
        despesas = Despesas.objects.filter(
            descricao__in=['Despesa lote criador 1', 'Despesa lote criador 2'],
        ).order_by('descricao')
        self.assertEqual(despesas.count(), 2)
        self.assertTrue(all(despesa.criado_por_id == self.user.id for despesa in despesas))

    def test_editar_despesa_preserva_criador_e_ignora_post_adulterado(self):
        editor = get_user_model().objects.create_user(
            username='editor_despesa_criador',
            password='senha123',
        )
        perfil_editor = PerfilUsuario.objects.create(user=editor, ministerio=self.ministerio)
        perfil_editor.igrejas_permitidas.set([self.igreja])
        grupo_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)
        editor.groups.add(grupo_tesoureiro)
        despesa = Despesas.objects.create(
            igreja=self.igreja,
            categoria=self.categoria,
            data=date(2026, 10, 15),
            descricao='Despesa com autor original',
            valor=Decimal('15.00'),
            conta_bancaria=self.conta,
            criado_por=self.user,
        )

        self.client.force_login(editor)
        response = self.client.post(
            reverse('financeiro:editar_despesa', args=[despesa.pk]),
            data={
                'igreja': str(self.igreja.pk),
                'evento': '',
                'categoria': str(self.categoria.pk),
                'data': '2026-10-15',
                'valor': '20.00',
                'descricao': 'Despesa editada por U2',
                'conta_bancaria': str(self.conta.pk),
                'observacao': 'edicao valida',
                'criado_por': str(editor.pk),
            },
        )

        self.assertEqual(response.status_code, 302)
        despesa.refresh_from_db()
        self.assertEqual(despesa.descricao, 'Despesa editada por U2')
        self.assertEqual(despesa.criado_por, self.user)


class DespesaAprovacaoHardeningTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        self.grupo_pastor_local, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        self.grupo_pastor_regional, _ = Group.objects.get_or_create(name=PASTOR_REGIONAL)
        self.grupo_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)
        self.igreja_b = Igreja.objects.create(
            nome_igreja='Igreja B Aprovacao',
            ministerio=self.ministerio,
            tipo_igreja='independente',
        )
        self.igreja_c = Igreja.objects.create(
            nome_igreja='Igreja C Descendente Aprovacao',
            ministerio=self.ministerio,
            tipo_igreja='congregacao',
            igreja_superior=self.igreja_b,
        )
        self.admin_m2 = get_user_model().objects.create_user(
            username='admin_m2_aprovacao',
            password='senha123',
        )
        self.ministerio_m2 = Ministerio.objects.create(
            nome_fantasia='Ministerio M2 Aprovacao',
            administrador_principal=self.admin_m2,
            ativo=True,
            cnpj='98765432000177',
        )
        self.igreja_m2 = Igreja.objects.create(
            nome_igreja='Igreja M2 Aprovacao',
            ministerio=self.ministerio_m2,
            tipo_igreja='sede',
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Aprovacao Hardening',
        )
        self.categoria_m2 = CategoriaDespesa.objects.create(
            ministerio=self.ministerio_m2,
            nome='Categoria Aprovacao M2',
        )
        self.conta_a = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Conta A Aprovacao',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('500.00'),
        )
        self.conta_b = ContaBancaria.objects.create(
            igreja=self.igreja_b,
            nome_identificacao='Conta B Aprovacao',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('500.00'),
        )
        self.conta_c = ContaBancaria.objects.create(
            igreja=self.igreja_c,
            nome_identificacao='Conta C Aprovacao',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('500.00'),
        )
        self.conta_m2 = ContaBancaria.objects.create(
            igreja=self.igreja_m2,
            nome_identificacao='Conta M2 Aprovacao',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('500.00'),
        )
        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)
        departamento_local = DepartamentoFinanceiro.objects.get(
            igreja=self.igreja,
            codigo_interno=DepartamentoFinanceiro.CODIGO_LOCAL,
        )
        self.politica_local = PoliticaDepartamentoFinanceiro.objects.get(
            departamento=departamento_local,
        )
        self.politica_local.exige_aprovacao_para_saida = True
        self.politica_local.valor_minimo_para_aprovacao = Decimal('10.00')
        self.politica_local.save(update_fields=['exige_aprovacao_para_saida', 'valor_minimo_para_aprovacao'])

    def _criar_usuario(self, username, grupos, igrejas, ministerio=None):
        user = get_user_model().objects.create_user(username=username, password='senha123')
        user.groups.add(*grupos)
        perfil = PerfilUsuario.objects.create(
            user=user,
            ministerio=ministerio or self.ministerio,
        )
        perfil.igrejas_permitidas.set(igrejas)
        return user

    def _autenticar_com_igreja_ativa(self, user, igreja):
        self.client.force_login(user)
        session = self.client.session
        session['igreja_ativa_id'] = igreja.pk
        session.save()

    def _criar_despesa_pendente(self, igreja, conta, criador=None, categoria=None):
        return Despesas.objects.create(
            igreja=igreja,
            categoria=categoria or self.categoria,
            data=date(2026, 10, 16),
            descricao=f'Despesa pendente {igreja.pk}',
            valor=Decimal('50.00'),
            conta_bancaria=conta,
            criado_por=criador,
            aprovacao_status=Despesas.APROVACAO_PENDENTE,
        )

    def test_tesoureiro_cria_despesa_com_aprovacao_obrigatoria_e_permanece_pendente(self):
        tesoureiro = self._criar_usuario(
            'tesoureiro_criador_aprovacao',
            [self.grupo_tesoureiro],
            [self.igreja],
        )
        self._autenticar_com_igreja_ativa(tesoureiro, self.igreja)

        response = self.client.post(
            reverse('financeiro:cadastrar_despesa'),
            data={
                'data': '2026-10-16',
                'categoria': str(self.categoria.pk),
                'descricao': 'Despesa tesoureiro pendente',
                'valor': '50.00',
                'conta_bancaria': str(self.conta_a.pk),
                'evento': '',
                'observacao': '',
            },
        )

        self.assertEqual(response.status_code, 302)
        despesa = Despesas.objects.get(descricao='Despesa tesoureiro pendente')
        self.assertEqual(despesa.criado_por, tesoureiro)
        self.assertEqual(despesa.aprovacao_status, Despesas.APROVACAO_PENDENTE)
        self.assertIsNone(despesa.aprovado_por)
        self.assertIsNone(despesa.aprovado_em)

    def test_pastor_local_cria_propria_despesa_com_aprovacao_obrigatoria_e_permanece_pendente(self):
        pastor = self._criar_usuario(
            'pastor_criador_aprovacao',
            [self.grupo_pastor_local],
            [self.igreja],
        )
        self._autenticar_com_igreja_ativa(pastor, self.igreja)

        response = self.client.post(
            reverse('financeiro:cadastrar_despesa'),
            data={
                'data': '2026-10-16',
                'categoria': str(self.categoria.pk),
                'descricao': 'Despesa pastor pendente',
                'valor': '50.00',
                'conta_bancaria': str(self.conta_a.pk),
                'evento': '',
                'observacao': '',
            },
        )

        self.assertEqual(response.status_code, 302)
        despesa = Despesas.objects.get(descricao='Despesa pastor pendente')
        self.assertEqual(despesa.criado_por, pastor)
        self.assertEqual(despesa.aprovacao_status, Despesas.APROVACAO_PENDENTE)
        self.assertIsNone(despesa.aprovado_por)
        self.assertIsNone(despesa.aprovado_em)

    def test_pastor_local_nao_pode_aprovar_ou_reprovar_propria_despesa(self):
        pastor = self._criar_usuario(
            'pastor_auto_decisao_bloqueada',
            [self.grupo_pastor_local],
            [self.igreja],
        )
        despesa = self._criar_despesa_pendente(self.igreja, self.conta_a, criador=pastor)
        self._autenticar_com_igreja_ativa(pastor, self.igreja)

        response_aprovacao = self.client.post(
            reverse('financeiro:aprovar_despesa', args=[despesa.pk]),
        )
        response_reprovacao = self.client.post(
            reverse('financeiro:reprovar_despesa', args=[despesa.pk]),
            data={'observacao_aprovacao': 'Tentativa indevida.'},
        )

        self.assertEqual(response_aprovacao.status_code, 403)
        self.assertEqual(response_reprovacao.status_code, 403)
        despesa.refresh_from_db()
        self.assertEqual(despesa.aprovacao_status, Despesas.APROVACAO_PENDENTE)
        self.assertIsNone(despesa.aprovado_por)
        self.assertIsNone(despesa.aprovado_em)

    def test_aprovador_diferente_com_write_scope_pode_aprovar_e_autor_historico_nulo_permanece_nulo(self):
        tesoureiro = self._criar_usuario(
            'tesoureiro_autor_aprovacao',
            [self.grupo_tesoureiro],
            [self.igreja],
        )
        aprovador = self._criar_usuario(
            'pastor_aprovador_aprovacao',
            [self.grupo_pastor_local],
            [self.igreja],
        )
        despesa = self._criar_despesa_pendente(self.igreja, self.conta_a, criador=tesoureiro)
        despesa_historica = self._criar_despesa_pendente(self.igreja, self.conta_a, criador=None)
        self._autenticar_com_igreja_ativa(aprovador, self.igreja)

        response = self.client.post(reverse('financeiro:aprovar_despesa', args=[despesa.pk]))
        response_historica = self.client.post(
            reverse('financeiro:aprovar_despesa', args=[despesa_historica.pk]),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response_historica.status_code, 302)
        despesa.refresh_from_db()
        despesa_historica.refresh_from_db()
        self.assertEqual(despesa.aprovacao_status, Despesas.APROVACAO_APROVADA)
        self.assertEqual(despesa.aprovado_por, aprovador)
        self.assertIsNotNone(despesa.aprovado_em)
        self.assertIsNone(despesa_historica.criado_por)
        self.assertEqual(despesa_historica.aprovado_por, aprovador)

    def test_aprovador_elegivel_sem_write_scope_nao_acessa_despesa_de_outra_igreja(self):
        aprovador = self._criar_usuario(
            'pastor_sem_scope_aprovacao',
            [self.grupo_pastor_local],
            [self.igreja_b],
        )
        despesa = self._criar_despesa_pendente(self.igreja, self.conta_a)
        self._autenticar_com_igreja_ativa(aprovador, self.igreja_b)

        response = self.client.post(reverse('financeiro:aprovar_despesa', args=[despesa.pk]))

        self.assertEqual(response.status_code, 404)
        despesa.refresh_from_db()
        self.assertEqual(despesa.aprovacao_status, Despesas.APROVACAO_PENDENTE)
        self.assertIsNone(despesa.aprovado_por)

    def test_pastor_regional_nao_recebe_descendente_no_write_scope_de_aprovacao(self):
        regional = self._criar_usuario(
            'regional_sem_expansao_aprovacao',
            [self.grupo_pastor_regional],
            [self.igreja_b],
        )
        despesa = self._criar_despesa_pendente(self.igreja_c, self.conta_c)

        allowed_churches = get_finance_write_scope(regional, self.ministerio)

        self.assertFalse(allowed_churches.filter(pk=self.igreja_c.pk).exists())
        self.assertFalse(Despesas.objects.filter(pk=despesa.pk, igreja__in=allowed_churches).exists())

    def test_admin_ministerio_nao_recebe_bypass_para_igreja_fora_do_write_scope(self):
        admin = self._criar_usuario(
            'admin_sem_bypass_aprovacao',
            [self.grupo_admin],
            [self.igreja],
        )
        despesa = self._criar_despesa_pendente(self.igreja_b, self.conta_b)
        self._autenticar_com_igreja_ativa(admin, self.igreja)

        response = self.client.post(reverse('financeiro:aprovar_despesa', args=[despesa.pk]))

        self.assertEqual(response.status_code, 404)
        despesa.refresh_from_db()
        self.assertEqual(despesa.aprovacao_status, Despesas.APROVACAO_PENDENTE)
        self.assertIsNone(despesa.aprovado_por)

    def test_cross_ministry_e_escopo_vazio_falham_fechados_para_aprovacao_e_reprovacao(self):
        aprovador = self._criar_usuario(
            'pastor_cross_ministry_aprovacao',
            [self.grupo_pastor_local],
            [self.igreja],
        )
        sem_escopo = self._criar_usuario(
            'pastor_scope_vazio_aprovacao',
            [self.grupo_pastor_local],
            [],
        )
        despesa_m2 = self._criar_despesa_pendente(
            self.igreja_m2,
            self.conta_m2,
            categoria=self.categoria_m2,
        )
        despesa_a = self._criar_despesa_pendente(self.igreja, self.conta_a)

        self._autenticar_com_igreja_ativa(aprovador, self.igreja)
        response_cross = self.client.post(reverse('financeiro:aprovar_despesa', args=[despesa_m2.pk]))
        self._autenticar_com_igreja_ativa(sem_escopo, self.igreja)
        response_scope_vazio = self.client.post(
            reverse('financeiro:reprovar_despesa', args=[despesa_a.pk]),
            data={'observacao_aprovacao': 'Nao deve acessar.'},
        )

        self.assertEqual(response_cross.status_code, 404)
        self.assertEqual(response_scope_vazio.status_code, 404)
        despesa_m2.refresh_from_db()
        despesa_a.refresh_from_db()
        self.assertEqual(despesa_m2.aprovacao_status, Despesas.APROVACAO_PENDENTE)
        self.assertEqual(despesa_a.aprovacao_status, Despesas.APROVACAO_PENDENTE)
        self.assertIsNone(despesa_m2.aprovado_por)
        self.assertIsNone(despesa_a.aprovado_por)

    def test_politica_sem_aprovacao_obrigatoria_preserva_aprovacao_imediata_do_criador(self):
        pastor = self._criar_usuario(
            'pastor_sem_politica_aprovacao',
            [self.grupo_pastor_local],
            [self.igreja],
        )
        self.politica_local.exige_aprovacao_para_saida = False
        self.politica_local.save(update_fields=['exige_aprovacao_para_saida'])
        self._autenticar_com_igreja_ativa(pastor, self.igreja)

        response = self.client.post(
            reverse('financeiro:cadastrar_despesa'),
            data={
                'data': '2026-10-16',
                'categoria': str(self.categoria.pk),
                'descricao': 'Despesa sem aprovacao obrigatoria',
                'valor': '50.00',
                'conta_bancaria': str(self.conta_a.pk),
                'evento': '',
                'observacao': '',
            },
        )

        self.assertEqual(response.status_code, 302)
        despesa = Despesas.objects.get(descricao='Despesa sem aprovacao obrigatoria')
        self.assertEqual(despesa.criado_por, pastor)
        self.assertEqual(despesa.aprovacao_status, Despesas.APROVACAO_APROVADA)
        self.assertEqual(despesa.aprovado_por, pastor)
        self.assertIsNotNone(despesa.aprovado_em)


class PainelFinanceiroViewTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.perfil, _ = PerfilUsuario.objects.get_or_create(
            user=self.user,
            defaults={'ministerio': self.ministerio},
        )
        if self.perfil.ministerio_id != self.ministerio.id:
            self.perfil.ministerio = self.ministerio
            self.perfil.save(update_fields=['ministerio'])
        self.perfil.igrejas_permitidas.set([self.igreja])

        self.client.force_login(self.user)
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja.id
        session.save()

        self.fornecedor = Fornecedor.objects.create(
            ministerio=self.ministerio,
            nome='Fornecedor Painel Fixo',
            ativo=True,
        )
        self.recorrencia = RecorrenciaContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            descricao='Internet Mensal',
            valor=Decimal('100.00'),
            dia_vencimento=10,
            data_inicio=date(2026, 1, 1),
            usuario_criacao=self.user,
        )
        ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            descricao='Conta Fixa Pendente',
            valor=Decimal('100.00'),
            data_vencimento=date(2026, 5, 25),
            recorrencia_origem=self.recorrencia,
            competencia='2026-05',
            criado_automaticamente=True,
            status='PEN',
        )
        ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            descricao='Conta Fixa Paga',
            valor=Decimal('150.00'),
            data_vencimento=date(2026, 5, 15),
            competencia='2026-05',
            criado_automaticamente=True,
            status='PAG',
        )
        ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            descricao='Conta Fixa Vencida',
            valor=Decimal('80.00'),
            data_vencimento=date(2026, 5, 10),
            competencia='2026-05',
            criado_automaticamente=True,
            status='VEN',
        )
        ContaPagar.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            fornecedor=self.fornecedor,
            descricao='Conta Avulsa',
            valor=Decimal('300.00'),
            data_vencimento=date(2026, 5, 20),
            status='PEN',
        )

    def test_painel_exibe_resumo_de_contas_fixas_do_mes(self):
        with patch('contas.page_permissions.user_can_access_page', return_value=True):
            response = self.client.get(reverse('financeiro:painel_financeiro'), {'periodo_filtro': 'geral'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['qtd_contas_fixas_previstas'], 3)
        self.assertEqual(response.context['qtd_contas_fixas_pagas'], 1)
        self.assertEqual(response.context['qtd_contas_fixas_atrasadas'], 1)
        self.assertEqual(response.context['total_contas_fixas_previstas'], Decimal('330.00'))
        self.assertEqual(response.context['total_contas_fixas_pagas'], Decimal('150.00'))
        self.assertEqual(response.context['total_contas_fixas_atrasadas'], Decimal('80.00'))


class EventoFinanceiroSegregacaoTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.perfil, _ = PerfilUsuario.objects.get_or_create(
            user=self.user,
            defaults={'ministerio': self.ministerio},
        )
        if self.perfil.ministerio_id != self.ministerio.id:
            self.perfil.ministerio = self.ministerio
            self.perfil.save(update_fields=['ministerio'])
        self.perfil.igrejas_permitidas.set([self.igreja])

        group_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)
        self.user.groups.add(group_tesoureiro)

        self.client.force_login(self.user)

        self.caixa_evento = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Caixa Evento Teste',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('100.00'),
        )
        self.caixa_tesouraria = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Caixa Tesouraria Geral',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('200.00'),
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Evento Segregacao',
        )
        self.categoria_evento = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Outros Custos do Evento',
        )
        self.evento = Evento.objects.create(
            igreja=self.igreja,
            titulo='Conferencia Financeira',
            data_inicio=timezone.make_aware(datetime(2026, 8, 10, 9, 0, 0)),
            data_fim=timezone.make_aware(datetime(2026, 8, 11, 18, 0, 0)),
            conta_bancaria_evento=self.caixa_evento,
        )

    def test_receita_model_rejeita_caixa_diferente_do_evento(self):
        receita = Receitas(
            igreja=self.igreja,
            evento=self.evento,
            categoria='oferta',
            data=date(2026, 8, 10),
            valor=Decimal('50.00'),
            conta_bancaria=self.caixa_tesouraria,
        )

        with self.assertRaises(ValidationError):
            receita.full_clean()

    def test_despesa_model_rejeita_caixa_diferente_do_evento(self):
        despesa = Despesas(
            igreja=self.igreja,
            evento=self.evento,
            categoria=self.categoria,
            data=date(2026, 8, 10),
            descricao='Pagamento fornecedor',
            valor=Decimal('30.00'),
            conta_bancaria=self.caixa_tesouraria,
        )

        with self.assertRaises(ValidationError):
            despesa.full_clean()

    def test_receita_form_contexto_evento_trava_evento_e_caixa(self):
        form = ReceitaForm(
            ministerio=self.ministerio,
            allowed_churches=Igreja.objects.filter(pk=self.igreja.pk),
            igreja_selecionada_inicial=self.igreja,
            evento_contexto=self.evento,
            travar_evento=True,
            travar_conta_evento=True,
        )

        self.assertTrue(form.fields['evento'].disabled)
        self.assertTrue(form.fields['conta_bancaria'].disabled)
        self.assertEqual(form.initial['evento'], self.evento.pk)
        self.assertEqual(form.initial['categoria'], 'doacao')
        self.assertEqual(form.initial['conta_bancaria'], self.caixa_evento.pk)

    def test_receita_fluxo_service_post_evento_forca_categoria_e_conta(self):
        post_data, conta_evento_efetiva_id = ReceitaFluxoService.construir_post_data_receita_evento(
            raw_post_data={
                'data': '2026-08-10',
                'categoria': 'oferta',
                'valor': '120.00',
                'conta_bancaria': str(self.caixa_tesouraria.pk),
            },
            evento=self.evento,
        )

        self.assertEqual(post_data['igreja'], str(self.igreja.pk))
        self.assertEqual(post_data['evento'], str(self.evento.pk))
        self.assertEqual(post_data['categoria'], 'doacao')
        self.assertEqual(post_data['conta_bancaria'], str(self.caixa_evento.pk))
        self.assertEqual(conta_evento_efetiva_id, self.caixa_evento.pk)

    def test_receita_fluxo_service_post_caixa_eventos_com_evento_forca_doacao(self):
        post_data, evento, conta_evento_efetiva_id = ReceitaFluxoService.construir_post_data_receita_caixa_eventos(
            raw_post_data={
                'evento': str(self.evento.pk),
                'categoria': 'oferta',
                'valor': '120.00',
                'conta_bancaria': str(self.caixa_tesouraria.pk),
            },
            igreja_padrao_para_form=self.igreja,
            allowed_churches=Igreja.objects.filter(pk=self.igreja.pk),
        )

        self.assertIsNotNone(evento)
        self.assertEqual(post_data['igreja'], str(self.igreja.pk))
        self.assertEqual(post_data['categoria'], 'doacao')
        self.assertEqual(post_data['conta_bancaria'], str(self.caixa_evento.pk))
        self.assertEqual(conta_evento_efetiva_id, self.caixa_evento.pk)

    def test_receita_fluxo_service_initial_caixa_eventos_usa_conta_padrao_eventos(self):
        self.igreja.conta_padrao_eventos = self.caixa_evento
        self.igreja.save(update_fields=['conta_padrao_eventos'])

        initial = ReceitaFluxoService.construir_initial_receita_caixa_eventos(self.igreja)

        self.assertEqual(initial['categoria'], 'doacao')
        self.assertEqual(initial['conta_bancaria'], self.caixa_evento.pk)

    def test_cadastrar_receita_caixa_eventos_get_filtra_categoria_e_preseleciona_conta_eventos(self):
        self.igreja.conta_padrao_eventos = self.caixa_evento
        self.igreja.save(update_fields=['conta_padrao_eventos'])

        response = self.client.get(reverse('financeiro:cadastrar_receita_caixa_eventos'))

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        categorias = [codigo for codigo, _rotulo in form.fields['categoria'].choices]
        self.assertEqual(categorias, ['doacao', 'outro'])
        self.assertEqual(form.initial['categoria'], 'doacao')
        self.assertEqual(form.initial['conta_bancaria'], self.caixa_evento.pk)
        self.assertContains(response, '<select name="categoria"', html=False)
        self.assertNotContains(response, '<select name="conta_bancaria"', html=False)
        self.assertContains(response, f'name="conta_bancaria" value="{self.caixa_evento.pk}"', html=False)

    def test_cadastrar_receita_caixa_eventos_mostra_conta_quando_nao_ha_padrao_eventos(self):
        self.igreja.conta_padrao_eventos = None
        self.igreja.save(update_fields=['conta_padrao_eventos'])

        response = self.client.get(reverse('financeiro:cadastrar_receita_caixa_eventos'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<select name="categoria"', html=False)
        self.assertContains(response, '<select name="conta_bancaria"', html=False)

    def test_cadastrar_receita_caixa_eventos_sem_evento_salva_no_fundo_eventos(self):
        self.igreja.conta_padrao_eventos = self.caixa_evento
        self.igreja.save(update_fields=['conta_padrao_eventos'])

        response = self.client.post(
            reverse('financeiro:cadastrar_receita_caixa_eventos'),
            data={
                'data': '2026-08-10',
                'categoria': 'outro',
                'valor': '120.00',
                'forma_pgto': 'PIX',
                'conta_bancaria': str(self.caixa_evento.pk),
                'membro': '',
                'evento': '',
                'observacao': 'entrada geral de eventos',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        receita = Receitas.objects.order_by('-id').first()
        self.assertIsNotNone(receita)
        self.assertEqual(receita.fundo_departamental.codigo, FundoDepartamental.CODIGO_EVENTOS)
        self.assertEqual(receita.categoria, 'outro')
        self.assertEqual(receita.conta_bancaria_id, self.caixa_evento.pk)

    def test_cadastrar_receita_com_next_eventos_redireciona_para_fluxo_eventos(self):
        response = self.client.get(
            reverse('financeiro:cadastrar_receita'),
            {'next': reverse('eventos:lista_eventos')},
        )

        self.assertRedirects(response, reverse('financeiro:cadastrar_receita_caixa_eventos'))

    def test_cadastrar_despesa_com_next_eventos_redireciona_para_fluxo_eventos(self):
        response = self.client.get(
            reverse('financeiro:cadastrar_despesa'),
            {'next': reverse('eventos:lista_eventos')},
        )

        self.assertRedirects(response, reverse('financeiro:cadastrar_despesa_caixa_eventos'))

    def test_eventos_lista_painel_reflete_receita_caixa_eventos_sem_evento(self):
        self.igreja.conta_padrao_eventos = self.caixa_evento
        self.igreja.save(update_fields=['conta_padrao_eventos'])

        response_post = self.client.post(
            reverse('financeiro:cadastrar_receita_caixa_eventos'),
            data={
                'data': '2026-08-10',
                'categoria': 'doacao',
                'valor': '125.00',
                'forma_pgto': 'PIX',
                'conta_bancaria': str(self.caixa_evento.pk),
                'membro': '',
                'evento': '',
                'observacao': 'entrada sem evento específico',
            },
            follow=True,
        )

        self.assertEqual(response_post.status_code, 200)

        response_lista = self.client.get(
            reverse('eventos:lista_eventos'),
            {
                'periodo_filtro': 'ano_atual',
                'status': 'aguardando',
            },
        )

        self.assertEqual(response_lista.status_code, 200)
        painel = response_lista.context['painel_financeiro_eventos']
        self.assertEqual(painel['total_entradas'], Decimal('125.00'))

    def test_eventos_lista_painel_reflete_despesa_caixa_eventos_sem_evento(self):
        self.igreja.conta_padrao_eventos = self.caixa_evento
        self.igreja.save(update_fields=['conta_padrao_eventos'])
        categoria_evento, _ = CategoriaDespesa.objects.get_or_create(
            ministerio=self.ministerio,
            nome='Outros Custos do Evento',
            defaults={'padrao_global': False},
        )

        response_post = self.client.post(
            reverse('financeiro:cadastrar_despesa_caixa_eventos'),
            data={
                'data': '2026-08-10',
                'categoria': str(categoria_evento.pk),
                'descricao': 'saida sem evento específico',
                'valor': '77.50',
                'conta_bancaria': str(self.caixa_evento.pk),
                'evento': '',
                'observacao': 'teste de saida geral de eventos',
            },
            follow=True,
        )

        self.assertEqual(response_post.status_code, 200)

        response_lista = self.client.get(
            reverse('eventos:lista_eventos'),
            {
                'periodo_filtro': 'ano_atual',
                'status': 'aguardando',
            },
        )

        self.assertEqual(response_lista.status_code, 200)
        painel = response_lista.context['painel_financeiro_eventos']
        self.assertEqual(painel['total_saidas'], Decimal('77.50'))
        despesa = Despesas.objects.get(descricao='saida sem evento específico')
        self.assertEqual(despesa.criado_por, self.user)

    def test_cadastrar_despesa_caixa_eventos_restringe_categorias_para_contexto_eventos(self):
        response = self.client.get(reverse('financeiro:cadastrar_despesa_caixa_eventos'))

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        categorias_renderizadas = list(form.fields['categoria'].queryset.values_list('nome', flat=True))

        for nome_categoria in categorias_despesa_padrao_eventos():
            self.assertIn(nome_categoria, categorias_renderizadas)
        self.assertNotIn(self.categoria.nome, categorias_renderizadas)

    def test_cadastrar_despesa_caixa_eventos_define_criado_por(self):
        self.igreja.conta_padrao_eventos = self.caixa_evento
        self.igreja.save(update_fields=['conta_padrao_eventos'])

        response = self.client.post(
            reverse('financeiro:cadastrar_despesa_caixa_eventos'),
            data={
                'data': '2026-08-10',
                'categoria': str(self.categoria_evento.pk),
                'descricao': 'Despesa caixa eventos com autor',
                'valor': '55.00',
                'conta_bancaria': str(self.caixa_evento.pk),
                'evento': '',
                'observacao': '',
            },
        )

        self.assertEqual(response.status_code, 302)
        despesa = Despesas.objects.get(descricao='Despesa caixa eventos com autor')
        despesa.refresh_from_db()
        self.assertEqual(despesa.criado_por, self.user)
        self.assertEqual(despesa.igreja, self.igreja)
        self.assertEqual(despesa.fundo_departamental.codigo, FundoDepartamental.CODIGO_EVENTOS)
        self.assertEqual(despesa.conta_bancaria, self.caixa_evento)

    def test_cadastrar_receita_evento_forca_caixa_vinculado(self):
        response = self.client.post(
            reverse('financeiro:cadastrar_receita_evento', args=[self.evento.pk]),
            data={
                'data': '2026-08-10',
                'categoria': 'oferta',
                'valor': '120.00',
                'conta_bancaria': str(self.caixa_tesouraria.pk),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        receita = Receitas.objects.filter(evento=self.evento).order_by('-id').first()
        self.assertIsNotNone(receita)
        self.assertEqual(receita.categoria, 'doacao')
        self.assertEqual(receita.conta_bancaria_id, self.caixa_evento.pk)

    def test_cadastrar_despesa_evento_forca_caixa_vinculado(self):
        response = self.client.post(
            reverse('financeiro:cadastrar_despesa_evento', args=[self.evento.pk]),
            data={
                'data': '2026-08-10',
                'categoria': str(self.categoria_evento.pk),
                'descricao': 'Compra de material',
                'valor': '40.00',
                'conta_bancaria': str(self.caixa_tesouraria.pk),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        despesa = Despesas.objects.filter(evento=self.evento).order_by('-id').first()
        self.assertIsNotNone(despesa)
        self.assertEqual(despesa.conta_bancaria_id, self.caixa_evento.pk)
        self.assertEqual(despesa.criado_por, self.user)

    def test_cadastrar_despesa_evento_define_criado_por(self):
        response = self.client.post(
            reverse('financeiro:cadastrar_despesa_evento', args=[self.evento.pk]),
            data={
                'data': '2026-08-10',
                'categoria': str(self.categoria_evento.pk),
                'descricao': 'Despesa evento com autor',
                'valor': '60.00',
                'conta_bancaria': str(self.caixa_tesouraria.pk),
                'observacao': '',
            },
        )

        self.assertEqual(response.status_code, 302)
        despesa = Despesas.objects.get(descricao='Despesa evento com autor')
        despesa.refresh_from_db()
        self.assertEqual(despesa.criado_por, self.user)
        self.assertEqual(despesa.evento, self.evento)
        self.assertEqual(despesa.igreja, self.evento.igreja)
        self.assertEqual(despesa.conta_bancaria, self.caixa_evento)

    def test_evento_sem_caixa_permite_caixa_tesouraria(self):
        evento_sem_caixa = Evento.objects.create(
            igreja=self.igreja,
            titulo='Evento sem caixa vinculado',
            data_inicio=timezone.make_aware(datetime(2026, 8, 20, 9, 0, 0)),
            data_fim=timezone.make_aware(datetime(2026, 8, 20, 18, 0, 0)),
            conta_bancaria_evento=None,
        )

        response = self.client.post(
            reverse('financeiro:cadastrar_receita_evento', args=[evento_sem_caixa.pk]),
            data={
                'data': '2026-08-20',
                'categoria': 'oferta',
                'valor': '55.00',
                'conta_bancaria': str(self.caixa_tesouraria.pk),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        receita = Receitas.objects.filter(evento=evento_sem_caixa).order_by('-id').first()
        self.assertIsNotNone(receita)
        self.assertEqual(receita.categoria, 'doacao')
        self.assertEqual(receita.conta_bancaria_id, self.caixa_tesouraria.pk)

    def test_evento_sem_caixa_usa_conta_padrao_eventos_da_igreja_na_receita(self):
        self.igreja.conta_padrao_eventos = self.caixa_evento
        self.igreja.save(update_fields=['conta_padrao_eventos'])

        evento_sem_caixa = Evento.objects.create(
            igreja=self.igreja,
            titulo='Evento com conta padrao da igreja',
            data_inicio=timezone.make_aware(datetime(2026, 8, 22, 9, 0, 0)),
            data_fim=timezone.make_aware(datetime(2026, 8, 22, 18, 0, 0)),
            conta_bancaria_evento=None,
        )

        response = self.client.post(
            reverse('financeiro:cadastrar_receita_evento', args=[evento_sem_caixa.pk]),
            data={
                'data': '2026-08-22',
                'categoria': 'oferta',
                'valor': '88.00',
                'conta_bancaria': str(self.caixa_tesouraria.pk),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        receita = Receitas.objects.filter(evento=evento_sem_caixa).order_by('-id').first()
        self.assertIsNotNone(receita)
        self.assertEqual(receita.categoria, 'doacao')
        self.assertEqual(receita.conta_bancaria_id, self.caixa_evento.pk)

    def test_form_receita_evento_oculta_seletor_conta_quando_igreja_tem_padrao_eventos(self):
        self.igreja.conta_padrao_eventos = self.caixa_evento
        self.igreja.save(update_fields=['conta_padrao_eventos'])

        evento_sem_caixa = Evento.objects.create(
            igreja=self.igreja,
            titulo='Evento sem caixa com padrao igreja',
            data_inicio=timezone.make_aware(datetime(2026, 8, 23, 9, 0, 0)),
            data_fim=timezone.make_aware(datetime(2026, 8, 23, 18, 0, 0)),
            conta_bancaria_evento=None,
        )

        response = self.client.get(reverse('financeiro:cadastrar_receita_evento', args=[evento_sem_caixa.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<select name="conta_bancaria"')
        self.assertContains(response, f'name="conta_bancaria" value="{self.caixa_evento.pk}"')

    def test_form_receita_evento_renderiza_action_da_rota_de_evento(self):
        response = self.client.get(reverse('financeiro:cadastrar_receita_evento', args=[self.evento.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'action="{reverse("financeiro:cadastrar_receita_evento", args=[self.evento.pk])}"',
        )

    def test_lista_receitas_filtra_por_fundo_eventos(self):
        Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 8, 10),
            valor=Decimal('10.00'),
            conta_bancaria=self.caixa_tesouraria,
        )
        receita_evento = Receitas.objects.create(
            igreja=self.igreja,
            evento=self.evento,
            categoria='doacao',
            data=date(2026, 8, 10),
            valor=Decimal('20.00'),
            conta_bancaria=self.caixa_evento,
        )
        fundo_eventos = FundoDepartamental.objects.get(
            igreja=self.igreja,
            codigo=FundoDepartamental.CODIGO_EVENTOS,
        )

        response = self.client.get(
            reverse('financeiro:lista_receitas'),
            {'fundo_filtro': str(fundo_eventos.pk), 'fechado': 'todos'},
        )

        self.assertEqual(response.status_code, 200)
        receitas_contexto = list(response.context['receitas'])
        self.assertEqual(len(receitas_contexto), 1)
        self.assertEqual(receitas_contexto[0].pk, receita_evento.pk)

    def test_lista_despesas_filtra_por_fundo_eventos(self):
        Despesas.objects.create(
            igreja=self.igreja,
            categoria=self.categoria,
            data=date(2026, 8, 10),
            descricao='Despesa local',
            valor=Decimal('11.00'),
            conta_bancaria=self.caixa_tesouraria,
        )
        despesa_evento = Despesas.objects.create(
            igreja=self.igreja,
            evento=self.evento,
            categoria=self.categoria,
            data=date(2026, 8, 10),
            descricao='Despesa evento',
            valor=Decimal('21.00'),
            conta_bancaria=self.caixa_evento,
        )
        fundo_eventos = FundoDepartamental.objects.get(
            igreja=self.igreja,
            codigo=FundoDepartamental.CODIGO_EVENTOS,
        )

        response = self.client.get(
            reverse('financeiro:lista_despesas'),
            {'fundo_filtro': str(fundo_eventos.pk), 'fechado': 'todos'},
        )

        self.assertEqual(response.status_code, 200)
        despesas_contexto = list(response.context['despesas'])
        self.assertEqual(len(despesas_contexto), 1)
        self.assertEqual(despesas_contexto[0].pk, despesa_evento.pk)

    def test_painel_financeiro_filtra_por_fundo_eventos(self):
        Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 8, 10),
            valor=Decimal('30.00'),
            conta_bancaria=self.caixa_tesouraria,
        )
        Despesas.objects.create(
            igreja=self.igreja,
            categoria=self.categoria,
            data=date(2026, 8, 10),
            descricao='Despesa local painel',
            valor=Decimal('5.00'),
            conta_bancaria=self.caixa_tesouraria,
        )
        Receitas.objects.create(
            igreja=self.igreja,
            evento=self.evento,
            categoria='doacao',
            data=date(2026, 8, 10),
            valor=Decimal('40.00'),
            conta_bancaria=self.caixa_evento,
        )
        Despesas.objects.create(
            igreja=self.igreja,
            evento=self.evento,
            categoria=self.categoria,
            data=date(2026, 8, 10),
            descricao='Despesa evento painel',
            valor=Decimal('7.00'),
            conta_bancaria=self.caixa_evento,
        )
        fundo_eventos = FundoDepartamental.objects.get(
            igreja=self.igreja,
            codigo=FundoDepartamental.CODIGO_EVENTOS,
        )

        with patch('contas.page_permissions.user_can_access_page', return_value=True):
            response = self.client.get(
                reverse('financeiro:painel_financeiro'),
                {'periodo_filtro': 'geral', 'fundo_filtro': str(fundo_eventos.pk)},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_receitas'], Decimal('40.00'))
        self.assertEqual(response.context['total_despesas'], Decimal('7.00'))

    def test_edicao_receita_evento_mantem_regra_de_caixa(self):
        receita = Receitas.objects.create(
            igreja=self.igreja,
            evento=self.evento,
            categoria='oferta',
            data=date(2026, 8, 10),
            valor=Decimal('70.00'),
            conta_bancaria=self.caixa_evento,
        )

        response = self.client.post(
            reverse('financeiro:editar_receita', args=[receita.pk]),
            data={
                'igreja': str(self.igreja.pk),
                'evento': str(self.evento.pk),
                'data': '2026-08-10',
                'categoria': 'oferta',
                'valor': '70.00',
                'conta_bancaria': str(self.caixa_tesouraria.pk),
                'forma_pgto': '',
                'membro': '',
                'observacao': 'tentativa troca caixa',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Use o caixa vinculado ao evento selecionado.')
        receita.refresh_from_db()
        self.assertEqual(receita.conta_bancaria_id, self.caixa_evento.pk)

    def test_evento_sem_caixa_permite_despesa_com_caixa_tesouraria(self):
        evento_sem_caixa = Evento.objects.create(
            igreja=self.igreja,
            titulo='Evento sem caixa para despesa',
            data_inicio=timezone.make_aware(datetime(2026, 8, 21, 9, 0, 0)),
            data_fim=timezone.make_aware(datetime(2026, 8, 21, 18, 0, 0)),
            conta_bancaria_evento=None,
        )

        response = self.client.post(
            reverse('financeiro:cadastrar_despesa_evento', args=[evento_sem_caixa.pk]),
            data={
                'data': '2026-08-21',
                'categoria': str(self.categoria_evento.pk),
                'descricao': 'Despesa sem caixa vinculado',
                'valor': '35.00',
                'conta_bancaria': str(self.caixa_tesouraria.pk),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        despesa = Despesas.objects.filter(evento=evento_sem_caixa).order_by('-id').first()
        self.assertIsNotNone(despesa)
        self.assertEqual(despesa.conta_bancaria_id, self.caixa_tesouraria.pk)

    def test_evento_sem_caixa_usa_conta_padrao_eventos_da_igreja_na_despesa(self):
        self.igreja.conta_padrao_eventos = self.caixa_evento
        self.igreja.save(update_fields=['conta_padrao_eventos'])

        evento_sem_caixa = Evento.objects.create(
            igreja=self.igreja,
            titulo='Evento despesa com conta padrao da igreja',
            data_inicio=timezone.make_aware(datetime(2026, 8, 24, 9, 0, 0)),
            data_fim=timezone.make_aware(datetime(2026, 8, 24, 18, 0, 0)),
            conta_bancaria_evento=None,
        )

        response = self.client.post(
            reverse('financeiro:cadastrar_despesa_evento', args=[evento_sem_caixa.pk]),
            data={
                'data': '2026-08-24',
                'categoria': str(self.categoria_evento.pk),
                'descricao': 'Despesa com padrao da igreja',
                'valor': '42.00',
                'conta_bancaria': str(self.caixa_tesouraria.pk),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        despesa = Despesas.objects.filter(evento=evento_sem_caixa).order_by('-id').first()
        self.assertIsNotNone(despesa)
        self.assertEqual(despesa.conta_bancaria_id, self.caixa_evento.pk)

    def test_form_despesa_evento_renderiza_action_da_rota_de_evento(self):
        response = self.client.get(reverse('financeiro:cadastrar_despesa_evento', args=[self.evento.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'action="{reverse("financeiro:cadastrar_despesa_evento", args=[self.evento.pk])}"',
        )

    def test_cadastrar_despesa_caixa_eventos_oculta_conta_quando_igreja_tem_padrao_eventos(self):
        self.igreja.conta_padrao_eventos = self.caixa_evento
        self.igreja.save(update_fields=['conta_padrao_eventos'])

        response = self.client.get(reverse('financeiro:cadastrar_despesa_caixa_eventos'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<select name="conta_bancaria"')
        self.assertContains(response, f'name="conta_bancaria" value="{self.caixa_evento.pk}"')

    def test_edicao_despesa_evento_mantem_regra_de_caixa(self):
        despesa = Despesas.objects.create(
            igreja=self.igreja,
            evento=self.evento,
            categoria=self.categoria,
            data=date(2026, 8, 10),
            descricao='Despesa original',
            valor=Decimal('45.00'),
            conta_bancaria=self.caixa_evento,
        )

        response = self.client.post(
            reverse('financeiro:editar_despesa', args=[despesa.pk]),
            data={
                'igreja': str(self.igreja.pk),
                'evento': str(self.evento.pk),
                'categoria': str(self.categoria.pk),
                'data': '2026-08-10',
                'valor': '45.00',
                'descricao': 'Despesa editada',
                'conta_bancaria': str(self.caixa_tesouraria.pk),
                'observacao': 'tentativa troca caixa',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Use o caixa vinculado ao evento selecionado.')
        despesa.refresh_from_db()
        self.assertEqual(despesa.conta_bancaria_id, self.caixa_evento.pk)

    def test_cadastrar_despesa_evento_salva_pendente_quando_politica_exige_aprovacao(self):
        user_model = get_user_model()
        tesoureiro_local = user_model.objects.create_user(
            username='tesoureiro_sem_nivel_aprovacao_evento',
            email='tesoureiro_evento@gereigreja.test',
            password='senha123',
        )
        perfil_tesoureiro, _ = PerfilUsuario.objects.get_or_create(
            user=tesoureiro_local,
            defaults={'ministerio': self.ministerio},
        )
        if perfil_tesoureiro.ministerio_id != self.ministerio.id:
            perfil_tesoureiro.ministerio = self.ministerio
            perfil_tesoureiro.save(update_fields=['ministerio'])
        perfil_tesoureiro.igrejas_permitidas.set([self.igreja])
        group_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)
        tesoureiro_local.groups.add(group_tesoureiro)
        self.client.force_login(tesoureiro_local)

        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)
        departamento_eventos = DepartamentoFinanceiro.objects.get(
            igreja=self.igreja,
            codigo_interno=DepartamentoFinanceiro.CODIGO_EVENTOS,
        )
        politica = PoliticaDepartamentoFinanceiro.objects.get(departamento=departamento_eventos)
        politica.exige_aprovacao_para_saida = True
        politica.valor_minimo_para_aprovacao = Decimal('10.00')
        politica.save(update_fields=['exige_aprovacao_para_saida', 'valor_minimo_para_aprovacao'])

        response = self.client.post(
            reverse('financeiro:cadastrar_despesa_evento', args=[self.evento.pk]),
            data={
                'data': '2026-08-10',
                'categoria': str(self.categoria_evento.pk),
                'descricao': 'Despesa bloqueada por aprovacao',
                'valor': '40.00',
                'conta_bancaria': str(self.caixa_evento.pk),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'salvo como pendente para aprovacao')
        despesa = Despesas.objects.get(descricao='Despesa bloqueada por aprovacao')
        self.assertEqual(despesa.aprovacao_status, Despesas.APROVACAO_PENDENTE)
        self.assertIsNone(despesa.aprovado_por)

    def test_cadastrar_despesa_local_salva_pendente_quando_politica_exige_aprovacao(self):
        user_model = get_user_model()
        tesoureiro_local = user_model.objects.create_user(
            username='tesoureiro_sem_nivel_aprovacao_local',
            email='tesoureiro_local@gereigreja.test',
            password='senha123',
        )
        perfil_tesoureiro, _ = PerfilUsuario.objects.get_or_create(
            user=tesoureiro_local,
            defaults={'ministerio': self.ministerio},
        )
        if perfil_tesoureiro.ministerio_id != self.ministerio.id:
            perfil_tesoureiro.ministerio = self.ministerio
            perfil_tesoureiro.save(update_fields=['ministerio'])
        perfil_tesoureiro.igrejas_permitidas.set([self.igreja])
        group_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)
        tesoureiro_local.groups.add(group_tesoureiro)
        self.client.force_login(tesoureiro_local)

        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)
        departamento_local = DepartamentoFinanceiro.objects.get(
            igreja=self.igreja,
            codigo_interno=DepartamentoFinanceiro.CODIGO_LOCAL,
        )
        politica = PoliticaDepartamentoFinanceiro.objects.get(departamento=departamento_local)
        politica.exige_aprovacao_para_saida = True
        politica.valor_minimo_para_aprovacao = Decimal('10.00')
        politica.save(update_fields=['exige_aprovacao_para_saida', 'valor_minimo_para_aprovacao'])

        response = self.client.post(
            reverse('financeiro:cadastrar_despesa'),
            data={
                'data': '2026-08-10',
                'categoria': str(self.categoria.pk),
                'descricao': 'Despesa local bloqueada por aprovacao',
                'valor': '50.00',
                'conta_bancaria': str(self.caixa_tesouraria.pk),
                'evento': '',
                'observacao': 'teste politica aprovacao',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'salvo como pendente para aprovacao')
        despesa = Despesas.objects.get(descricao='Despesa local bloqueada por aprovacao')
        self.assertEqual(despesa.aprovacao_status, Despesas.APROVACAO_PENDENTE)
        self.assertIsNone(despesa.aprovado_por)

    def test_aprovar_despesa_pendente_atualiza_status(self):
        despesa = Despesas.objects.create(
            igreja=self.igreja,
            categoria=self.categoria,
            data=date(2026, 8, 10),
            descricao='Despesa pendente de aprovacao',
            valor=Decimal('77.00'),
            conta_bancaria=self.caixa_tesouraria,
            aprovacao_status=Despesas.APROVACAO_PENDENTE,
        )

        response = self.client.post(
            reverse('financeiro:aprovar_despesa', args=[despesa.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        despesa.refresh_from_db()
        self.assertEqual(despesa.aprovacao_status, Despesas.APROVACAO_APROVADA)
        self.assertEqual(despesa.aprovado_por_id, self.user.id)
        self.assertIsNotNone(despesa.aprovado_em)

    def test_reprovar_despesa_pendente_atualiza_status(self):
        despesa = Despesas.objects.create(
            igreja=self.igreja,
            categoria=self.categoria,
            data=date(2026, 8, 10),
            descricao='Despesa pendente para reprovar',
            valor=Decimal('63.00'),
            conta_bancaria=self.caixa_tesouraria,
            aprovacao_status=Despesas.APROVACAO_PENDENTE,
        )

        response = self.client.post(
            reverse('financeiro:reprovar_despesa', args=[despesa.pk]),
            data={'observacao_aprovacao': 'Documento incompleto.'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        despesa.refresh_from_db()
        self.assertEqual(despesa.aprovacao_status, Despesas.APROVACAO_REJEITADA)
        self.assertEqual(despesa.aprovado_por_id, self.user.id)
        self.assertEqual(despesa.observacao_aprovacao, 'Documento incompleto.')

    def test_reprovar_despesa_sem_motivo_retorna_erro(self):
        despesa = Despesas.objects.create(
            igreja=self.igreja,
            categoria=self.categoria,
            data=date(2026, 8, 10),
            descricao='Despesa pendente sem motivo',
            valor=Decimal('63.00'),
            conta_bancaria=self.caixa_tesouraria,
            aprovacao_status=Despesas.APROVACAO_PENDENTE,
        )

        response = self.client.post(
            reverse('financeiro:reprovar_despesa', args=[despesa.pk]),
            data={'observacao_aprovacao': '   '},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Informe o motivo da reprovação antes de continuar.')
        despesa.refresh_from_db()
        self.assertEqual(despesa.aprovacao_status, Despesas.APROVACAO_PENDENTE)
        self.assertIsNone(despesa.aprovado_por)

    def test_lista_despesas_filtra_por_status_aprovacao(self):
        despesa_pendente = Despesas.objects.create(
            igreja=self.igreja,
            categoria=self.categoria,
            data=date(2026, 8, 10),
            descricao='Despesa pendente filtro',
            valor=Decimal('25.00'),
            conta_bancaria=self.caixa_tesouraria,
            aprovacao_status=Despesas.APROVACAO_PENDENTE,
        )
        despesa_aprovada = Despesas.objects.create(
            igreja=self.igreja,
            categoria=self.categoria,
            data=date(2026, 8, 10),
            descricao='Despesa aprovada filtro',
            valor=Decimal('35.00'),
            conta_bancaria=self.caixa_tesouraria,
            aprovado_por=self.user,
            aprovado_em=timezone.now(),
            aprovacao_status=Despesas.APROVACAO_APROVADA,
        )

        response = self.client.get(
            reverse('financeiro:lista_despesas'),
            {'aprovacao_status': 'PENDENTE', 'fechado': 'todos'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        despesas_contexto = list(response.context['despesas'])
        self.assertIn(despesa_pendente, despesas_contexto)
        self.assertNotIn(despesa_aprovada, despesas_contexto)

    def test_finalizar_fechamento_ignora_despesas_pendentes(self):
        Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 8, 10),
            valor=Decimal('100.00'),
            conta_bancaria=self.caixa_tesouraria,
            fechado=False,
        )
        despesa_aprovada = Despesas.objects.create(
            igreja=self.igreja,
            categoria=self.categoria,
            data=date(2026, 8, 10),
            descricao='Despesa aprovada fechamento',
            valor=Decimal('30.00'),
            conta_bancaria=self.caixa_tesouraria,
            aprovado_por=self.user,
            aprovado_em=timezone.now(),
            aprovacao_status=Despesas.APROVACAO_APROVADA,
            fechado=False,
        )
        despesa_pendente = Despesas.objects.create(
            igreja=self.igreja,
            categoria=self.categoria,
            data=date(2026, 8, 10),
            descricao='Despesa pendente fechamento',
            valor=Decimal('20.00'),
            conta_bancaria=self.caixa_tesouraria,
            aprovacao_status=Despesas.APROVACAO_PENDENTE,
            fechado=False,
        )

        response = self.client.post(
            reverse('financeiro:finalizar_fechamento_caixa'),
            data={
                'igreja_id': str(self.igreja.pk),
                'data_inicio': '2026-08-01',
                'data_fim': '2026-08-31',
                'observacoes': 'teste fechamento aprovacao',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        fechamento = FechamentoCaixa.objects.latest('id')
        self.assertEqual(fechamento.total_entradas, Decimal('100.00'))
        self.assertEqual(fechamento.total_saidas, Decimal('30.00'))
        despesa_aprovada.refresh_from_db()
        despesa_pendente.refresh_from_db()
        self.assertTrue(despesa_aprovada.fechado)
        self.assertFalse(despesa_pendente.fechado)

    def test_prestacao_contas_eventos_fecha_lancamentos_do_periodo(self):
        grupo_pastor_local, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        self.user.groups.add(grupo_pastor_local)
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja.pk
        session.save()

        receita = Receitas.objects.create(
            igreja=self.igreja,
            evento=self.evento,
            categoria='doacao',
            data=date(2026, 8, 10),
            valor=Decimal('110.00'),
            conta_bancaria=self.caixa_evento,
        )
        despesa = Despesas.objects.create(
            igreja=self.igreja,
            evento=self.evento,
            categoria=self.categoria_evento,
            data=date(2026, 8, 10),
            descricao='Despesa para fechamento',
            valor=Decimal('35.00'),
            conta_bancaria=self.caixa_evento,
        )

        response = self.client.post(
            reverse('eventos:prestacao_contas_eventos') + '?periodo_filtro=custom&data_inicio=2026-08-01&data_fim=2026-08-31',
            data={'acao': 'fechar_periodo_eventos'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        receita.refresh_from_db()
        despesa.refresh_from_db()
        self.assertTrue(receita.fechado)
        self.assertTrue(despesa.fechado)

    def test_edicao_receita_fechada_e_bloqueada(self):
        receita = Receitas.objects.create(
            igreja=self.igreja,
            evento=self.evento,
            categoria='doacao',
            data=date(2026, 8, 10),
            valor=Decimal('70.00'),
            conta_bancaria=self.caixa_evento,
            fechado=True,
        )

        response = self.client.post(
            reverse('financeiro:editar_receita', args=[receita.pk]),
            data={
                'igreja': str(self.igreja.pk),
                'evento': str(self.evento.pk),
                'data': '2026-08-10',
                'categoria': 'doacao',
                'valor': '95.00',
                'conta_bancaria': str(self.caixa_evento.pk),
                'forma_pgto': 'PIX',
                'membro': '',
                'observacao': 'tentativa alteracao',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Não é possível editar uma receita fechada.')
        receita.refresh_from_db()
        self.assertEqual(receita.valor, Decimal('70.00'))

    def test_exclusao_despesa_fechada_e_bloqueada(self):
        despesa = Despesas.objects.create(
            igreja=self.igreja,
            evento=self.evento,
            categoria=self.categoria_evento,
            data=date(2026, 8, 10),
            descricao='Despesa fechada',
            valor=Decimal('42.00'),
            conta_bancaria=self.caixa_evento,
            fechado=True,
        )

        response = self.client.post(
            reverse('financeiro:excluir_despesa', args=[despesa.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Não é possível excluir uma despesa fechada.')
        self.assertTrue(Despesas.objects.filter(pk=despesa.pk).exists())


class FundosDepartamentaisFinanceiroTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.conta = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Caixa Fundo Teste',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('100.00'),
        )
        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Fundo Teste',
        )
        self.evento = Evento.objects.create(
            igreja=self.igreja,
            titulo='Evento Fundo Teste',
            data_inicio=timezone.make_aware(datetime(2026, 9, 1, 19, 0, 0)),
            data_fim=timezone.make_aware(datetime(2026, 9, 1, 21, 0, 0)),
        )

    def test_receita_sem_evento_recebe_fundo_local(self):
        receita = Receitas.objects.create(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 9, 2),
            valor=Decimal('50.00'),
            conta_bancaria=self.conta,
        )

        self.assertIsNotNone(receita.fundo_departamental_id)
        self.assertEqual(receita.fundo_departamental.codigo, FundoDepartamental.CODIGO_LOCAL)

    def test_despesa_com_evento_recebe_fundo_eventos(self):
        despesa = Despesas.objects.create(
            igreja=self.igreja,
            evento=self.evento,
            data=date(2026, 9, 2),
            descricao='Despesa de evento',
            valor=Decimal('20.00'),
            categoria=self.categoria,
            conta_bancaria=self.conta,
        )

        self.assertIsNotNone(despesa.fundo_departamental_id)
        self.assertEqual(despesa.fundo_departamental.codigo, FundoDepartamental.CODIGO_EVENTOS)

    def test_receita_evento_com_fundo_local_rejeita_validacao(self):
        fundo_local, _ = FundoDepartamental.objects.get_or_create(
            igreja=self.igreja,
            codigo=FundoDepartamental.CODIGO_LOCAL,
            defaults={'nome_exibicao': 'Tesouraria Local'},
        )
        receita = Receitas(
            igreja=self.igreja,
            evento=self.evento,
            categoria='oferta',
            data=date(2026, 9, 3),
            valor=Decimal('30.00'),
            conta_bancaria=self.conta,
            fundo_departamental=fundo_local,
        )

        with self.assertRaises(ValidationError):
            receita.full_clean()

    def test_receita_fundo_eventos_rejeita_categoria_dizimo(self):
        fundo_eventos, _ = FundoDepartamental.objects.get_or_create(
            igreja=self.igreja,
            codigo=FundoDepartamental.CODIGO_EVENTOS,
            defaults={'nome_exibicao': 'Eventos'},
        )
        receita = Receitas(
            igreja=self.igreja,
            categoria='dizimo',
            data=date(2026, 9, 3),
            valor=Decimal('45.00'),
            conta_bancaria=self.conta,
            fundo_departamental=fundo_eventos,
        )

        with self.assertRaises(ValidationError):
            receita.full_clean()

    def test_receita_fundo_eventos_rejeita_categoria_oferta(self):
        fundo_eventos, _ = FundoDepartamental.objects.get_or_create(
            igreja=self.igreja,
            codigo=FundoDepartamental.CODIGO_EVENTOS,
            defaults={'nome_exibicao': 'Eventos'},
        )
        receita = Receitas(
            igreja=self.igreja,
            categoria='oferta',
            data=date(2026, 9, 3),
            valor=Decimal('45.00'),
            conta_bancaria=self.conta,
            fundo_departamental=fundo_eventos,
        )

        with self.assertRaises(ValidationError):
            receita.full_clean()

    def test_receita_fundo_eventos_aceita_categoria_doacao(self):
        fundo_eventos, _ = FundoDepartamental.objects.get_or_create(
            igreja=self.igreja,
            codigo=FundoDepartamental.CODIGO_EVENTOS,
            defaults={'nome_exibicao': 'Eventos'},
        )
        receita = Receitas(
            igreja=self.igreja,
            categoria='doacao',
            data=date(2026, 9, 3),
            valor=Decimal('45.00'),
            conta_bancaria=self.conta,
            fundo_departamental=fundo_eventos,
        )

        receita.full_clean()

    def test_receita_fundo_eventos_aceita_categoria_outro(self):
        fundo_eventos, _ = FundoDepartamental.objects.get_or_create(
            igreja=self.igreja,
            codigo=FundoDepartamental.CODIGO_EVENTOS,
            defaults={'nome_exibicao': 'Eventos'},
        )
        receita = Receitas(
            igreja=self.igreja,
            categoria='outro',
            data=date(2026, 9, 3),
            valor=Decimal('45.00'),
            conta_bancaria=self.conta,
            fundo_departamental=fundo_eventos,
        )

        receita.full_clean()

    def test_receita_fundo_assistencia_aceita_categoria_doacao(self):
        fundo_assistencia, _ = FundoDepartamental.objects.get_or_create(
            igreja=self.igreja,
            codigo=FundoDepartamental.CODIGO_ASSISTENCIA,
            defaults={'nome_exibicao': 'Assistencia Social'},
        )
        receita = Receitas(
            igreja=self.igreja,
            categoria='doacao',
            data=date(2026, 9, 3),
            valor=Decimal('55.00'),
            conta_bancaria=self.conta,
            fundo_departamental=fundo_assistencia,
        )

        receita.full_clean()

    def test_politica_categoria_padrao_por_fundo(self):
        self.assertEqual(categoria_receita_padrao_por_fundo(FundoDepartamental.CODIGO_EVENTOS), 'doacao')
        self.assertEqual(categoria_receita_padrao_por_fundo(FundoDepartamental.CODIGO_ASSISTENCIA), 'doacao')
        self.assertEqual(categoria_receita_padrao_por_fundo(FundoDepartamental.CODIGO_LOCAL), 'oferta')

    def test_politica_categorias_permitidas_por_fundo(self):
        permitidas_eventos = categorias_receita_permitidas_por_fundo(FundoDepartamental.CODIGO_EVENTOS)
        permitidas_assistencia = categorias_receita_permitidas_por_fundo(FundoDepartamental.CODIGO_ASSISTENCIA)
        permitidas_local = categorias_receita_permitidas_por_fundo(FundoDepartamental.CODIGO_LOCAL)

        self.assertEqual(permitidas_eventos, {'doacao', 'outro'})
        self.assertIn('doacao', permitidas_assistencia)
        self.assertIn('oferta', permitidas_local)

    def test_despesa_evento_com_fundo_local_rejeita_validacao(self):
        fundo_local, _ = FundoDepartamental.objects.get_or_create(
            igreja=self.igreja,
            codigo=FundoDepartamental.CODIGO_LOCAL,
            defaults={'nome_exibicao': 'Tesouraria Local'},
        )
        despesa = Despesas(
            igreja=self.igreja,
            evento=self.evento,
            data=date(2026, 9, 3),
            descricao='Despesa invalida por fundo',
            valor=Decimal('22.00'),
            categoria=self.categoria,
            conta_bancaria=self.conta,
            fundo_departamental=fundo_local,
        )

        with self.assertRaises(ValidationError):
            despesa.full_clean()


class DepartamentoFinanceiroGeradorTest(BaseFinanceiroTestCase):
    def test_service_cria_departamentos_padroes_com_politica(self):
        resumo = DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)

        self.assertIn(resumo['departamentos_criados'], (0, 4))
        self.assertIn(resumo['politicas_criadas'], (0, 4))
        self.assertEqual(
            DepartamentoFinanceiro.objects.filter(igreja=self.igreja, ativo=True).count(),
            4,
        )
        self.assertEqual(Departamento.objects.filter(igreja=self.igreja, ativo=True).count(), 4)

        departamento_eventos = DepartamentoFinanceiro.objects.get(
            igreja=self.igreja,
            codigo_interno=DepartamentoFinanceiro.CODIGO_EVENTOS,
        )
        self.assertEqual(departamento_eventos.tipo_departamento, DepartamentoFinanceiro.TIPO_PADRAO)
        self.assertIsNotNone(departamento_eventos.fundo_departamental_id)
        self.assertIsNotNone(departamento_eventos.departamento_id)

        politica_eventos = PoliticaDepartamentoFinanceiro.objects.get(departamento=departamento_eventos)
        self.assertFalse(politica_eventos.exige_nota_fiscal)
        self.assertTrue(politica_eventos.permite_prestacao_local_simplificada)

    def test_service_e_idempotente(self):
        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)
        resumo = DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)

        self.assertEqual(resumo['departamentos_criados'], 0)
        self.assertEqual(resumo['politicas_criadas'], 0)
        self.assertEqual(DepartamentoFinanceiro.objects.filter(igreja=self.igreja).count(), 4)

    def test_command_sincroniza_igreja_especifica(self):
        igreja_b = Igreja.objects.create(
            nome_igreja='Igreja B - Deptos',
            ministerio=self.ministerio,
            tipo_igreja='congregacao',
        )

        call_command('gerar_departamentos_financeiros', '--igreja-id', str(igreja_b.id))

        self.assertEqual(DepartamentoFinanceiro.objects.filter(igreja=self.igreja).count(), 4)
        self.assertEqual(DepartamentoFinanceiro.objects.filter(igreja=igreja_b).count(), 4)

    def test_vinculo_departamento_caixa_rejeita_igreja_diferente(self):
        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)
        departamento_local = DepartamentoFinanceiro.objects.get(
            igreja=self.igreja,
            codigo_interno=DepartamentoFinanceiro.CODIGO_LOCAL,
        )

        ministerio_b = Ministerio.objects.create(
            nome_fantasia='Ministerio B',
            administrador_principal=self.user,
            ativo=True,
            cnpj='22345678000199',
        )
        igreja_b = Igreja.objects.create(
            nome_igreja='Igreja B',
            ministerio=ministerio_b,
            tipo_igreja='sede',
        )
        caixa_outra_igreja = ContaBancaria.objects.create(
            igreja=igreja_b,
            nome_identificacao='Caixa B',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('0.00'),
        )

        vinculo = DepartamentoCaixa(
            departamento=departamento_local,
            conta_bancaria=caixa_outra_igreja,
        )
        with self.assertRaises(ValidationError):
            vinculo.full_clean()

    def test_fundos_visiveis_ignoram_departamento_inativo_e_mantem_fundos_soltos(self):
        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)

        fundo_local = FundoDepartamental.objects.get(
            igreja=self.igreja,
            codigo=FundoDepartamental.CODIGO_LOCAL,
        )
        fundo_eventos = FundoDepartamental.objects.get(
            igreja=self.igreja,
            codigo=FundoDepartamental.CODIGO_EVENTOS,
        )
        fundo_local.departamento_financeiro.ativo = False
        fundo_local.departamento_financeiro.save(update_fields=['ativo'])

        fundo_solto = FundoDepartamental.objects.create(
            igreja=self.igreja,
            codigo='PROJETO',
            nome_exibicao='Fundo Projeto',
            ativo=True,
        )

        fundos_visiveis = DepartamentoFinanceiroService.fundos_visiveis_para_igrejas([self.igreja])
        fundos_visiveis_ids = set(fundos_visiveis.values_list('id', flat=True))

        self.assertNotIn(fundo_local.id, fundos_visiveis_ids)
        self.assertIn(fundo_eventos.id, fundos_visiveis_ids)
        self.assertIn(fundo_solto.id, fundos_visiveis_ids)


class GestaoDepartamentosViewTest(BaseFinanceiroTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

        self.conta = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Caixa Teste Departamentos',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('0.00'),
        )

        perfil, _ = PerfilUsuario.objects.get_or_create(
            user=self.user,
            defaults={'ministerio': self.ministerio},
        )
        if perfil.ministerio_id != self.ministerio.id:
            perfil.ministerio = self.ministerio
            perfil.save(update_fields=['ministerio'])
        perfil.igrejas_permitidas.set([self.igreja])

        grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        self.user.groups.add(grupo_admin)

    def test_get_renderiza_pagina_departamentos(self):
        response = self.client.get(reverse('configuracao:gestao_departamentos'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'configuracao/departamentos/gestao_departamentos.html')
        self.assertContains(response, 'Gestao de Departamentos')

    def test_post_bloqueia_criacao_local_de_departamento_personalizado(self):
        response = self.client.post(
            reverse('configuracao:gestao_departamentos'),
            data={
                'action': 'criar_departamento',
                'igreja_id': str(self.igreja.id),
                'codigo_interno': 'JOVENS',
                'nome_exibicao': 'Ministerio de Jovens',
                'tipo_departamento': Departamento.TIPO_PERSONALIZADO,
                'ordem_exibicao': '60',
                'ativo': 'on',
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            Departamento.objects.filter(
                igreja=self.igreja,
                codigo_interno='JOVENS',
                nome_exibicao='Ministerio de Jovens',
            ).exists()
        )

    def test_post_habilita_financeiro_departamento_e_salva_politica(self):
        departamento = Departamento.objects.create(
            igreja=self.igreja,
            codigo_interno='KIDS',
            nome_exibicao='Ministerio Kids',
            tipo_departamento=Departamento.TIPO_PERSONALIZADO,
            ativo=True,
            ordem_exibicao=70,
        )

        response = self.client.post(
            reverse('configuracao:gestao_departamentos'),
            data={
                'action': 'salvar_financeiro_departamento',
                'igreja_id': str(self.igreja.id),
                'departamento_id': str(departamento.id),
                'habilitar_financeiro': 'on',
                'exige_nota_fiscal': 'on',
                'exige_envio_contabilidade': 'on',
                'permite_prestacao_local_simplificada': 'on',
            },
        )

        self.assertEqual(response.status_code, 302)

        departamento_financeiro = DepartamentoFinanceiro.objects.get(
            igreja=self.igreja,
            codigo_interno='KIDS',
        )
        politica = PoliticaDepartamentoFinanceiro.objects.get(departamento=departamento_financeiro)

        self.assertTrue(departamento_financeiro.ativo)
        self.assertEqual(departamento_financeiro.departamento_id, departamento.id)
        self.assertTrue(politica.exige_nota_fiscal)
        self.assertTrue(politica.exige_envio_contabilidade)
        self.assertTrue(politica.permite_prestacao_local_simplificada)

    def test_post_salva_caixa_padrao_para_departamento_financeiro(self):
        departamento = Departamento.objects.create(
            igreja=self.igreja,
            codigo_interno='KIDS_CAIXA',
            nome_exibicao='Kids Caixa',
            tipo_departamento=Departamento.TIPO_PERSONALIZADO,
            ativo=True,
            ordem_exibicao=20,
        )

        response = self.client.post(
            reverse('configuracao:gestao_departamentos'),
            data={
                'action': 'salvar_financeiro_departamento',
                'igreja_id': str(self.igreja.id),
                'departamento_id': str(departamento.id),
                'habilitar_financeiro': 'on',
                'caixa_padrao_id': str(self.conta.id),
            },
        )

        self.assertEqual(response.status_code, 302)

        departamento_financeiro = DepartamentoFinanceiro.objects.get(
            igreja=self.igreja,
            codigo_interno='KIDS_CAIXA',
        )
        vinculo_caixa = DepartamentoCaixa.objects.get(
            departamento=departamento_financeiro,
            conta_bancaria=self.conta,
        )

        self.assertTrue(departamento_financeiro.ativo)
        self.assertTrue(vinculo_caixa.ativo)
        self.assertTrue(vinculo_caixa.is_padrao)

    def test_conexoes_exibem_apenas_capacidades_ativas(self):
        departamento = Departamento.objects.create(
            igreja=self.igreja,
            codigo_interno='CONEXOES',
            nome_exibicao='Departamento Conexoes',
            tipo_departamento=Departamento.TIPO_PERSONALIZADO,
            ativo=True,
            ordem_exibicao=80,
        )
        DepartamentoCapacidade.objects.create(
            departamento=departamento,
            capacidade=DepartamentoCapacidade.PESSOAS,
            ativa=True,
        )
        DepartamentoCapacidade.objects.create(
            departamento=departamento,
            capacidade=DepartamentoCapacidade.EVENTOS,
            ativa=True,
        )
        DepartamentoCapacidade.objects.create(
            departamento=departamento,
            capacidade=DepartamentoCapacidade.AGENDA,
            ativa=False,
        )

        response = self.client.get(reverse('configuracao:gestao_departamentos'))

        self.assertEqual(response.status_code, 200)
        detalhes = response.content.decode().split(
            f'id="departamento_detalhes_{departamento.id}"', 1
        )[1].split('<div class="row g-3">', 1)[0]
        self.assertIn(reverse('secretaria:dashboard'), detalhes)
        self.assertIn(reverse('eventos:lista_eventos'), detalhes)
        self.assertNotIn(reverse('agenda:agenda'), detalhes)
        self.assertNotIn(reverse('comunicacao:home'), detalhes)
        self.assertNotIn(reverse('escola_biblica:dashboard'), detalhes)

    def test_confirmacao_de_legado_preserva_vinculos_financeiros(self):
        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)
        departamento = Departamento.objects.get(igreja=self.igreja, codigo_interno='MISSOES')
        financeiro = DepartamentoFinanceiro.objects.get(igreja=self.igreja, codigo_interno='MISSOES')
        DepartamentoCaixa.objects.create(
            departamento=financeiro,
            conta_bancaria=self.conta,
            ativo=True,
            is_padrao=True,
        )
        financeiro_id = financeiro.id
        fundo_id = financeiro.fundo_departamental_id

        response = self.client.post(
            reverse('configuracao:gestao_departamentos'),
            data={
                'action': 'confirmar_legado_departamento',
                'igreja_id': str(self.igreja.id),
                'departamento_id': str(departamento.id),
            },
        )

        self.assertEqual(response.status_code, 302)
        departamento.refresh_from_db()
        financeiro.refresh_from_db()
        self.assertEqual(departamento.classificacao, Departamento.CLASSIFICACAO_ORGANIZACIONAL)
        self.assertEqual(financeiro.id, financeiro_id)
        self.assertEqual(financeiro.departamento_id, departamento.id)
        self.assertEqual(financeiro.fundo_departamental_id, fundo_id)
        self.assertTrue(
            DepartamentoCaixa.objects.filter(
                departamento=financeiro,
                conta_bancaria=self.conta,
                ativo=True,
            ).exists()
        )

    def test_capacidade_financeiro_exibe_grupo_separado(self):
        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)
        departamento = Departamento.objects.get(igreja=self.igreja, codigo_interno='MISSOES')
        financeiro = DepartamentoFinanceiro.objects.get(igreja=self.igreja, codigo_interno='MISSOES')
        DepartamentoCapacidade.objects.create(
            departamento=departamento,
            capacidade=DepartamentoCapacidade.FINANCEIRO,
            ativa=True,
        )

        with patch('configuracao.views.user_can_access_page', return_value=True):
            response = self.client.get(reverse('configuracao:gestao_departamentos'))

        self.assertEqual(response.status_code, 200)
        detalhes = response.content.decode().split(
            f'id="departamento_detalhes_{departamento.id}"', 1
        )[1].split('<div class="row g-3">', 1)[0]
        self.assertIn('Financeiro do departamento', detalhes)
        self.assertIn(
            f'{reverse("financeiro:lista_receitas")}?fundo_filtro={financeiro.fundo_departamental_id}',
            detalhes,
        )
        self.assertIn(
            f'{reverse("financeiro:lista_fechamentos_caixa")}?dept_filtro={financeiro.id}',
            detalhes,
        )
        self.assertNotIn('>Financeiro</span>', detalhes)

    def test_confirmacao_de_legado_nao_altera_departamento_de_outra_igreja(self):
        outra_igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja Fora do Contexto',
        )
        departamento = Departamento.objects.create(
            igreja=outra_igreja,
            codigo_interno='LEGADO_FORA',
            nome_exibicao='Legado Fora do Contexto',
            classificacao=Departamento.CLASSIFICACAO_LEGADO_SUGERIDO,
        )

        response = self.client.post(
            reverse('configuracao:gestao_departamentos'),
            data={
                'action': 'confirmar_legado_departamento',
                'igreja_id': str(self.igreja.id),
                'departamento_id': str(departamento.id),
            },
        )

        self.assertEqual(response.status_code, 302)
        departamento.refresh_from_db()
        self.assertEqual(departamento.classificacao, Departamento.CLASSIFICACAO_LEGADO_SUGERIDO)


class EscopoFinanceiroPastorLocalTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin-escopo-financeiro')
        self.pastor = User.objects.create_user(username='pastor-local-escopo-financeiro')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Escopo Financeiro',
            administrador_principal=self.admin,
            ativo=True,
        )
        self.igreja_a = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Sede Financeiro',
            tipo_igreja='sede',
        )
        self.igreja_b = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Regional Financeiro',
            tipo_igreja='regional',
            igreja_superior=self.igreja_a,
        )
        self.igreja_c = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Congregacao Financeiro',
            tipo_igreja='congregacao',
            igreja_superior=self.igreja_b,
        )
        self.outro_admin = User.objects.create_user(username='admin-outro-ministerio-financeiro')
        self.outro_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministerio Escopo Financeiro',
            administrador_principal=self.outro_admin,
            ativo=True,
        )
        self.igreja_outro_ministerio = Igreja.objects.create(
            ministerio=self.outro_ministerio,
            nome_igreja='Igreja Outro Ministerio',
            tipo_igreja='independente',
        )
        self.perfil = PerfilUsuario.objects.create(user=self.pastor, ministerio=self.ministerio)
        self.perfil.igrejas_permitidas.add(self.igreja_a)
        grupo, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        self.pastor.groups.add(grupo)
        Plano.objects.get_or_create(
            nome='pioneiro',
            defaults={
                'codigo_plano': 'pioneiro',
                'permite_modulo_financeiro': True,
                'ativo': True,
            },
        )
        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja_a)
        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja_b)
        self.departamento_a = DepartamentoFinanceiro.objects.get(
            igreja=self.igreja_a,
            codigo_interno=DepartamentoFinanceiro.CODIGO_MISSOES,
        )
        self.departamento_b = DepartamentoFinanceiro.objects.get(
            igreja=self.igreja_b,
            codigo_interno=DepartamentoFinanceiro.CODIGO_MISSOES,
        )
        self.fundo_a = self.departamento_a.fundo_departamental
        self.fundo_b = self.departamento_b.fundo_departamental
        self.fechamento_a = FechamentoCaixa.objects.create(
            igreja=self.igreja_a,
            fundo_departamental=self.fundo_a,
            data_inicio=date(2026, 7, 1),
            data_fim=date(2026, 7, 31),
            status='fechado',
        )
        self.fechamento_b = FechamentoCaixa.objects.create(
            igreja=self.igreja_b,
            fundo_departamental=self.fundo_b,
            data_inicio=date(2026, 7, 1),
            data_fim=date(2026, 7, 31),
            status='fechado',
        )
        self.client.force_login(self.pastor)

    def test_escopo_canonico_nao_expande_pastor_local_para_subordinadas(self):
        self.assertQuerySetEqual(
            get_allowed_churches_for_user(self.pastor).order_by('pk'),
            [self.igreja_a],
        )

        self.assertNotIn(self.igreja_b, get_allowed_churches_for_user(self.pastor))
        self.assertNotIn(self.igreja_c, get_allowed_churches_for_user(self.pastor))

    def test_sem_igreja_explicitamente_permitida_retorna_escopo_vazio(self):
        self.perfil.igrejas_permitidas.clear()

        self.assertFalse(get_allowed_churches_for_user(self.pastor).exists())

    def test_lista_receitas_com_escopo_vazio_nao_retorna_receitas_do_ministerio(self):
        conta_a = ContaBancaria.objects.create(
            igreja=self.igreja_a,
            nome_identificacao='Caixa Sede',
            tipo='caixa_fisico',
        )
        Receitas.objects.create(
            igreja=self.igreja_a,
            fundo_departamental=self.fundo_a,
            conta_bancaria=conta_a,
            categoria='oferta',
            data=date(2026, 8, 10),
            valor=Decimal('10.00'),
            fechado=False,
        )
        self.perfil.igrejas_permitidas.clear()

        response = self.client.get(reverse('financeiro:lista_receitas'), {'fechado': 'todos'})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['receitas'].exists())
        self.assertFalse(response.context['fundos_departamentais_dropdown'].exists())

    def test_lista_receitas_com_igreja_explicita_retorna_somente_receitas_permitidas(self):
        conta_a = ContaBancaria.objects.create(
            igreja=self.igreja_a,
            nome_identificacao='Caixa Sede',
            tipo='caixa_fisico',
        )
        conta_b = ContaBancaria.objects.create(
            igreja=self.igreja_b,
            nome_identificacao='Caixa Regional',
            tipo='caixa_fisico',
        )
        receita_a = Receitas.objects.create(
            igreja=self.igreja_a,
            fundo_departamental=self.fundo_a,
            conta_bancaria=conta_a,
            categoria='oferta',
            data=date(2026, 8, 10),
            valor=Decimal('10.00'),
            fechado=False,
        )
        Receitas.objects.create(
            igreja=self.igreja_b,
            fundo_departamental=self.fundo_b,
            conta_bancaria=conta_b,
            categoria='oferta',
            data=date(2026, 8, 10),
            valor=Decimal('20.00'),
            fechado=False,
        )

        response = self.client.get(reverse('financeiro:lista_receitas'), {'fechado': 'todos'})

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['receitas'], [receita_a])

    def test_formulario_transferencia_ignora_igreja_presente_apenas_na_sessao(self):
        request = self.factory.get('/')
        request.igreja_ativa = None
        request.session = {'igreja_ativa_id': self.igreja_a.pk}

        form = TransferenciaCaixaForm(request=request)

        self.assertFalse(form.fields['caixa_origem'].queryset.exists())
        self.assertFalse(form.fields['caixa_destino'].queryset.exists())

    def test_formulario_transferencia_restringe_caixas_a_igreja_ativa_validada(self):
        conta_a = ContaBancaria.objects.create(
            igreja=self.igreja_a,
            nome_identificacao='Caixa Sede',
            tipo='caixa_fisico',
        )
        conta_b = ContaBancaria.objects.create(
            igreja=self.igreja_b,
            nome_identificacao='Caixa Regional',
            tipo='caixa_fisico',
        )
        request = self.factory.get('/')
        request.igreja_ativa = self.igreja_a
        request.session = {}

        form = TransferenciaCaixaForm(request=request)

        caixas_origem = form.fields['caixa_origem'].queryset
        caixas_destino = form.fields['caixa_destino'].queryset

        self.assertIn(conta_a, caixas_origem)
        self.assertIn(conta_a, caixas_destino)
        self.assertNotIn(conta_b, caixas_origem)
        self.assertNotIn(conta_b, caixas_destino)
        self.assertTrue(all(caixa.igreja_id == self.igreja_a.pk for caixa in caixas_origem))
        self.assertTrue(all(caixa.igreja_id == self.igreja_a.pk for caixa in caixas_destino))

    def test_api_caixas_retorna_somente_caixas_da_igreja_permitida(self):
        conta_a = ContaBancaria.objects.create(
            igreja=self.igreja_a,
            nome_identificacao='Caixa API Permitida',
            tipo='caixa_fisico',
        )
        conta_b = ContaBancaria.objects.create(
            igreja=self.igreja_b,
            nome_identificacao='Caixa API Não Permitida',
            tipo='caixa_fisico',
        )

        response = self.client.get(
            reverse('financeiro:api_caixas_por_igreja', args=[self.igreja_a.pk])
        )

        self.assertEqual(response.status_code, 200)
        caixas_ids = {caixa['id'] for caixa in response.json()}
        self.assertIn(conta_a.pk, caixas_ids)
        self.assertNotIn(conta_b.pk, caixas_ids)

    def test_api_caixas_nega_igreja_do_mesmo_ministerio_fora_do_escopo(self):
        conta_b = ContaBancaria.objects.create(
            igreja=self.igreja_b,
            nome_identificacao='Caixa API IDOR Mesmo Ministério',
            tipo='caixa_fisico',
        )

        response = self.client.get(
            reverse('financeiro:api_caixas_por_igreja', args=[self.igreja_b.pk])
        )

        self.assertEqual(response.status_code, 404)
        self.assertNotIn(conta_b.pk, {caixa['id'] for caixa in response.json()} if response.headers.get('Content-Type', '').startswith('application/json') else set())

    def test_api_caixas_nega_igreja_de_outro_ministerio(self):
        conta_outro_ministerio = ContaBancaria.objects.create(
            igreja=self.igreja_outro_ministerio,
            nome_identificacao='Caixa API Outro Ministério',
            tipo='caixa_fisico',
        )

        response = self.client.get(
            reverse('financeiro:api_caixas_por_igreja', args=[self.igreja_outro_ministerio.pk])
        )

        self.assertEqual(response.status_code, 404)
        self.assertNotIn(conta_outro_ministerio.pk, {caixa['id'] for caixa in response.json()} if response.headers.get('Content-Type', '').startswith('application/json') else set())

    def _criar_transferencia_para_igreja(self, igreja, prefixo):
        origem = ContaBancaria.objects.create(
            igreja=igreja,
            nome_identificacao=f'{prefixo} Origem',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('100.00'),
        )
        destino = ContaBancaria.objects.create(
            igreja=igreja,
            nome_identificacao=f'{prefixo} Destino',
            tipo='caixa_fisico',
            saldo_inicial=Decimal('0.00'),
        )
        return TransferenciaCaixa.objects.create(
            caixa_origem=origem,
            caixa_destino=destino,
            valor=Decimal('10.00'),
            usuario=self.pastor,
        )

    def test_transferencia_exibe_historico_da_igreja_ativa_validada(self):
        transferencia_a = self._criar_transferencia_para_igreja(self.igreja_a, 'Ativa A')
        transferencia_b = self._criar_transferencia_para_igreja(self.igreja_b, 'Fora Escopo B')
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja_a.pk
        session.save()

        response = self.client.get(reverse('financeiro:nova_transferencia_caixa'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['transferencias'], [transferencia_a])
        self.assertNotIn(transferencia_b, response.context['transferencias'])

    def test_transferencia_sessao_com_igreja_nao_permitida_nao_concede_acesso(self):
        transferencia_a = self._criar_transferencia_para_igreja(self.igreja_a, 'Permitida A')
        transferencia_b = self._criar_transferencia_para_igreja(self.igreja_b, 'Sessão Não Permitida B')
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja_b.pk
        session.save()

        response = self.client.get(reverse('financeiro:nova_transferencia_caixa'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['transferencias'], [transferencia_a])
        self.assertNotIn(transferencia_b, response.context['transferencias'])
        self.assertEqual(response.context['form'].fields['caixa_origem'].queryset.first().igreja_id, self.igreja_a.pk)

    def test_transferencia_sem_igreja_ativa_validada_falha_fechado(self):
        self.perfil.igrejas_permitidas.add(self.igreja_b)
        self._criar_transferencia_para_igreja(self.igreja_a, 'Sem Contexto A')
        self._criar_transferencia_para_igreja(self.igreja_b, 'Sem Contexto B')
        session = self.client.session
        session.pop('igreja_ativa_id', None)
        session.save()

        response = self.client.get(reverse('financeiro:nova_transferencia_caixa'))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['transferencias'].exists())
        self.assertFalse(response.context['form'].fields['caixa_origem'].queryset.exists())
        self.assertFalse(response.context['form'].fields['caixa_destino'].queryset.exists())

    def test_dropdown_e_filtro_de_fechamentos_rejeitam_igreja_b(self):
        response = self.client.get(
            reverse('financeiro:lista_fechamentos_caixa'),
            {'dept_filtro': self.departamento_b.pk},
        )

        self.assertEqual(response.status_code, 200)
        departamentos_ids = set(response.context['departamentos_financeiros_dropdown'].values_list('pk', flat=True))
        fechamentos_ids = set(response.context['fechamentos'].values_list('pk', flat=True))
        self.assertIn(self.departamento_a.pk, departamentos_ids)
        self.assertNotIn(self.departamento_b.pk, departamentos_ids)
        self.assertIn(self.fechamento_a.pk, fechamentos_ids)
        self.assertNotIn(self.fechamento_b.pk, fechamentos_ids)
        self.assertEqual(response.context['departamento_filtro_selecionado'], '')

    def test_filtro_de_fechamentos_aceita_departamento_permitido_e_preserva_isolamento(self):
        response = self.client.get(
            reverse('financeiro:lista_fechamentos_caixa'),
            {'dept_filtro': self.departamento_a.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['departamento_filtro_obj'], self.departamento_a)
        self.assertEqual(
            response.context['departamento_filtro_selecionado'],
            str(self.departamento_a.pk),
        )
        self.assertQuerySetEqual(response.context['fechamentos'], [self.fechamento_a])
        self.assertNotContains(response, self.igreja_b.nome_igreja)

    def test_criacao_e_finalizacao_na_igreja_b_nao_alteram_dados(self):
        quantidade_inicial = FechamentoCaixa.objects.count()
        dados = {
            'igreja': self.igreja_b.pk,
            'fundo_departamental': self.fundo_b.pk,
            'data_inicio': '2026-08-01',
            'data_fim': '2026-08-31',
        }

        response_criacao = self.client.post(reverse('financeiro:criar_fechamento_caixa'), dados)
        response_finalizacao = self.client.post(
            reverse('financeiro:finalizar_fechamento_caixa'),
            {
                'igreja_id': self.igreja_b.pk,
                'fundo_id': self.fundo_b.pk,
                'data_inicio': '2026-08-01',
                'data_fim': '2026-08-31',
            },
        )

        self.assertEqual(response_criacao.status_code, 200)
        self.assertTrue(response_criacao.context['form'].errors)
        self.assertEqual(response_finalizacao.status_code, 302)
        self.assertEqual(FechamentoCaixa.objects.count(), quantidade_inicial)

    def test_detalhe_e_reabertura_da_igreja_b_sao_bloqueados(self):
        detalhe = self.client.get(
            reverse('financeiro:detalhe_fechamento_caixa', args=[self.fechamento_b.pk])
        )
        reabertura = self.client.post(
            reverse('financeiro:reabrir_fechamento_caixa', args=[self.fechamento_b.pk])
        )

        self.assertEqual(detalhe.status_code, 404)
        self.assertEqual(reabertura.status_code, 404)
        self.assertTrue(FechamentoCaixa.objects.filter(pk=self.fechamento_b.pk, status='fechado').exists())

    def test_igreja_ativa_restringe_todas_as_listagens_ao_mesmo_escopo(self):
        self.perfil.igrejas_permitidas.add(self.igreja_b)
        conta_a = ContaBancaria.objects.create(
            igreja=self.igreja_a,
            nome_identificacao='Caixa Ativo A',
            tipo='caixa_fisico',
        )
        conta_b = ContaBancaria.objects.create(
            igreja=self.igreja_b,
            nome_identificacao='Caixa Ativo B',
            tipo='caixa_fisico',
        )
        categoria = CategoriaDespesa.objects.create(ministerio=self.ministerio, nome='Escopo Ativo')
        receita_a = Receitas.objects.create(
            igreja=self.igreja_a,
            fundo_departamental=self.fundo_a,
            conta_bancaria=conta_a,
            categoria='oferta',
            data=date(2026, 8, 10),
            valor=Decimal('10.00'),
            fechado=False,
        )
        Receitas.objects.create(
            igreja=self.igreja_b,
            fundo_departamental=self.fundo_b,
            conta_bancaria=conta_b,
            categoria='oferta',
            data=date(2026, 8, 10),
            valor=Decimal('20.00'),
            fechado=False,
        )
        despesa_a = Despesas.objects.create(
            igreja=self.igreja_a,
            fundo_departamental=self.fundo_a,
            conta_bancaria=conta_a,
            categoria=categoria,
            descricao='Pendente A',
            data=date(2026, 8, 10),
            valor=Decimal('10.00'),
            fechado=False,
            aprovacao_status=Despesas.APROVACAO_PENDENTE,
        )
        Despesas.objects.create(
            igreja=self.igreja_b,
            fundo_departamental=self.fundo_b,
            conta_bancaria=conta_b,
            categoria=categoria,
            descricao='Pendente B',
            data=date(2026, 8, 10),
            valor=Decimal('20.00'),
            fechado=False,
            aprovacao_status=Despesas.APROVACAO_PENDENTE,
        )
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja_a.pk
        session.save()

        receitas = self.client.get(reverse('financeiro:lista_receitas'), {'fechado': 'todos'})
        despesas = self.client.get(
            reverse('financeiro:lista_despesas'),
            {'fechado': 'todos', 'aprovacao_status': Despesas.APROVACAO_PENDENTE},
        )
        fechamentos = self.client.get(reverse('financeiro:lista_fechamentos_caixa'))

        self.assertQuerySetEqual(receitas.context['receitas'], [receita_a])
        self.assertQuerySetEqual(despesas.context['despesas'], [despesa_a])
        self.assertQuerySetEqual(fechamentos.context['fechamentos'], [self.fechamento_a])
        self.assertTrue(all(
            item.igreja_id == self.igreja_a.pk
            for item in fechamentos.context['departamentos_financeiros_dropdown']
        ))
