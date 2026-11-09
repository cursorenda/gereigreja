from datetime import date, datetime
from decimal import Decimal
import logging
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone

from configuracao.models import Igreja, Ministerio
from eventos.models import Evento
from financeiro.models import (
    CategoriaDespesa, ContaBancaria, ContaPagar, ContaPagarAutorizacaoEvento,
    DepartamentoCaixa, DepartamentoFinanceiro, Despesas, FechamentoCaixa,
    Fornecedor, FundoDepartamental, ImportacaoExtratoOFX, LancamentoExtratoOFX,
    LogTransacaoFinanceira, PoliticaFinanceiraIgreja, Receitas,
    RecorrenciaContaPagar, TransferenciaCaixa,
)


logging.disable(logging.CRITICAL)


class ResetDemoCommandTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('reset-demo-user', password='senha')
        self.demo_ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio de Teste', administrador_principal=self.user,
            cnpj='91000000000101', cidade='Demo', estado='SP', is_demo=True,
        )
        self.live_ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Real', administrador_principal=self.user,
            cnpj='91000000000102', cidade='Real', estado='SP', is_demo=False,
        )
        self.demo_church = Igreja.objects.create(ministerio=self.demo_ministerio, nome_igreja='Igreja Estrutural', tipo_igreja='sede')
        self.live_church = Igreja.objects.create(ministerio=self.live_ministerio, nome_igreja='Igreja Real com texto Demo', tipo_igreja='sede')
        self.demo_account = ContaBancaria.objects.create(igreja=self.demo_church, nome_identificacao='Caixa DEMO', tipo='caixa_fisico', saldo_inicial=Decimal('100.00'), is_principal=True)
        self.demo_destination = ContaBancaria.objects.create(igreja=self.demo_church, nome_identificacao='Destino DEMO', tipo='caixa_fisico', saldo_inicial=Decimal('20.00'))
        self.live_account = ContaBancaria.objects.create(igreja=self.live_church, nome_identificacao='Caixa Real', tipo='caixa_fisico', saldo_inicial=Decimal('500.00'), is_principal=True)
        self.category = CategoriaDespesa.objects.create(ministerio=self.demo_ministerio, nome='Categoria reset')
        self.supplier = Fornecedor.objects.create(ministerio=self.demo_ministerio, nome='Fornecedor reset')
        self.fund, _ = FundoDepartamental.objects.get_or_create(
            igreja=self.demo_church,
            codigo=FundoDepartamental.CODIGO_MISSOES,
            defaults={'nome_exibicao': 'Missões'},
        )
        self.department = DepartamentoFinanceiro.objects.create(igreja=self.demo_church, codigo_interno='RESET', nome_exibicao='Departamento reset')
        DepartamentoCaixa.objects.create(departamento=self.department, conta_bancaria=self.demo_account, is_padrao=True)
        PoliticaFinanceiraIgreja.objects.get_or_create(igreja=self.demo_church)

    def _fixture(self):
        revenue = Receitas.objects.create(igreja=self.demo_church, categoria='oferta', data=date(2026, 1, 10), valor=Decimal('30.00'), conta_bancaria=self.demo_account)
        expense = Despesas.objects.create(igreja=self.demo_church, data=date(2026, 1, 11), descricao='Manual', valor=Decimal('10.00'), categoria=self.category, conta_bancaria=self.demo_account)
        payable = ContaPagar.objects.create(ministerio=self.demo_ministerio, igreja=self.demo_church, fornecedor=self.supplier, categoria=self.category, descricao='Obrigação', valor=Decimal('25.00'), data_emissao=date(2026, 1, 1), data_vencimento=date(2026, 1, 15), status='PAG', data_pagamento=date(2026, 1, 15), valor_pago=Decimal('25.00'), conta_debito=self.demo_account, forma_pagamento='PIX')
        event = ContaPagarAutorizacaoEvento.objects.create(conta_pagar=payable, event_type=ContaPagarAutorizacaoEvento.EVENT_PAID, actor=self.user, authorization_status_after=ContaPagar.AUTHORIZATION_NOT_REQUIRED, financial_status_after='PAG')
        mirror = Despesas.objects.create(igreja=self.demo_church, data=date(2026, 1, 15), descricao='Espelho', valor=Decimal('25.00'), categoria=self.category, conta_bancaria=self.demo_account, origem_conta_pagar=payable)
        recurrence = RecorrenciaContaPagar.objects.create(ministerio=self.demo_ministerio, igreja=self.demo_church, fornecedor=self.supplier, categoria=self.category, descricao='Recorrência', valor=Decimal('15.00'), dia_vencimento=10, data_inicio=date(2026, 1, 1), conta_debito_padrao=self.demo_account)
        transfer = TransferenciaCaixa.objects.create(caixa_origem=self.demo_account, caixa_destino=self.demo_destination, valor=Decimal('5.00'), usuario=self.user)
        closing = FechamentoCaixa.objects.create(igreja=self.demo_church, data_inicio=date(2026, 1, 1), data_fim=date(2026, 1, 31), total_entradas=Decimal('30.00'), total_saidas=Decimal('35.00'), saldo_final=Decimal('-5.00'))
        imported = ImportacaoExtratoOFX.objects.create(conta_bancaria=self.demo_account, igreja=self.demo_church, hash_arquivo='a' * 64)
        ofx = LancamentoExtratoOFX.objects.create(importacao=imported, data=timezone.make_aware(datetime(2026, 1, 20, 12)), tipo='entrada', valor=Decimal('10.00'))
        Evento.objects.create(igreja=self.demo_church, titulo='Evento operacional', tipo='culto', data_inicio=timezone.now(), responsavel=self.user)
        return revenue, expense, payable, event, mirror, recurrence, transfer, closing, imported, ofx

    def _live_snapshot(self):
        return (
            tuple(ContaBancaria.objects.filter(igreja=self.live_church).values_list('pk', 'saldo_inicial', 'saldo_atual')),
            tuple(Receitas.objects.filter(igreja=self.live_church).values_list('pk', 'valor', 'conta_bancaria_id')),
            tuple(Despesas.objects.filter(igreja=self.live_church).values_list('pk', 'valor', 'conta_bancaria_id')),
        )

    def test_transfer_model_rejects_cross_tenant_in_both_directions_without_balance_change(self):
        before = (self.demo_account.saldo_atual, self.live_account.saldo_atual)
        for origem, destino in ((self.demo_account, self.live_account), (self.live_account, self.demo_account)):
            with self.assertRaises(ValidationError):
                TransferenciaCaixa.objects.create(caixa_origem=origem, caixa_destino=destino, valor=Decimal('1.00'), usuario=self.user)
        self.demo_account.refresh_from_db(); self.live_account.refresh_from_db()
        self.assertEqual((self.demo_account.saldo_atual, self.live_account.saldo_atual), before)

    def test_cross_tenant_legacy_transfer_fails_closed_before_mutation(self):
        records = self._fixture()
        # Simula dado legado/corrompido criado fora do caminho normal do domínio.
        TransferenciaCaixa.objects.bulk_create([TransferenciaCaixa(caixa_origem=self.demo_account, caixa_destino=self.live_account, valor=Decimal('1.00'), usuario=self.user)])
        with self.assertRaises(CommandError):
            call_command('reset_demo')
        self.assertTrue(Receitas.objects.filter(pk=records[0].pk).exists())
        self.assertTrue(ContaPagar.objects.filter(pk=records[2].pk).exists())

    def test_cross_scope_event_reference_aborts_without_changes(self):
        demo_records = self._fixture()
        demo_event = Evento.objects.get(igreja=self.demo_church)
        revenue = Receitas.objects.create(
            igreja=self.live_church, categoria='oferta', data=date(2026, 1, 1),
            valor=Decimal('20.00'), conta_bancaria=self.live_account,
        )
        expense = Despesas.objects.create(
            igreja=self.live_church, data=date(2026, 1, 2), descricao='Real',
            valor=Decimal('5.00'), conta_bancaria=self.live_account,
        )
        # Reproduce legacy links without the ordinary model validation.
        for record in (revenue, expense):
            type(record).objects.filter(pk=record.pk).update(evento=demo_event)

        records = (*demo_records, demo_event, revenue, expense,
                   self.demo_account, self.demo_destination, self.live_account)
        snapshots = [
            type(record).objects.values().get(pk=record.pk) for record in records
        ]

        with self.assertRaisesMessage(CommandError, 'referências financeiras fora do escopo demo'):
            call_command('reset_demo')

        self.assertEqual(
            [type(record).objects.values().get(pk=record.pk) for record in records],
            snapshots,
        )

    def test_reset_clears_operational_finance_preserves_structure_logs_and_non_demo(self):
        records = self._fixture()
        user_account = ContaBancaria.objects.create(igreja=self.demo_church, nome_identificacao='Criada pelo usuário', saldo_inicial=Decimal('77.00'))
        ContaBancaria.objects.filter(pk=self.demo_account.pk).update(saldo_inicial=Decimal('123.00'), saldo_atual=Decimal('999.00'))
        ContaBancaria.objects.filter(pk=user_account.pk).update(saldo_atual=Decimal('1.00'))
        log = LogTransacaoFinanceira.objects.create(igreja=self.demo_church, tipo_lancamento='receita', acao='criado', referencia_modelo='Teste', referencia_id=1, valor=Decimal('1.00'))
        Receitas.objects.create(igreja=self.live_church, categoria='oferta', data=date(2026, 1, 1), valor=Decimal('20.00'), conta_bancaria=self.live_account, observacao='Texto Demo não é ownership')
        Despesas.objects.create(igreja=self.live_church, data=date(2026, 1, 2), descricao='Real', valor=Decimal('5.00'), conta_bancaria=self.live_account, observacao='Demo')
        live_before = self._live_snapshot()
        call_command('reset_demo')
        self.assertFalse(Receitas.objects.filter(pk=records[0].pk).exists())
        self.assertFalse(Despesas.objects.filter(pk__in=[records[1].pk, records[4].pk]).exists())
        self.assertFalse(ContaPagar.objects.filter(pk=records[2].pk).exists())
        self.assertFalse(ContaPagarAutorizacaoEvento.objects.filter(pk=records[3].pk).exists())
        self.assertFalse(RecorrenciaContaPagar.objects.filter(pk=records[5].pk).exists())
        self.assertFalse(TransferenciaCaixa.objects.filter(pk=records[6].pk).exists())
        self.assertFalse(FechamentoCaixa.objects.filter(pk=records[7].pk).exists())
        self.assertFalse(ImportacaoExtratoOFX.objects.filter(pk=records[8].pk).exists())
        self.assertFalse(LancamentoExtratoOFX.objects.filter(pk=records[9].pk).exists())
        self.assertFalse(Evento.objects.filter(igreja=self.demo_church).exists())
        self.demo_account.refresh_from_db(); user_account.refresh_from_db()
        self.assertEqual((self.demo_account.saldo_inicial, self.demo_account.saldo_atual), (Decimal('123.00'), Decimal('123.00')))
        self.assertEqual((user_account.saldo_inicial, user_account.saldo_atual), (Decimal('77.00'), Decimal('77.00')))
        self.assertTrue(all(
            saldo_inicial == saldo_atual
            for saldo_inicial, saldo_atual in ContaBancaria.objects.filter(
                igreja__ministerio__is_demo=True
            ).values_list('saldo_inicial', 'saldo_atual')
        ))
        self.assertTrue(CategoriaDespesa.objects.filter(pk=self.category.pk).exists())
        self.assertTrue(Fornecedor.objects.filter(pk=self.supplier.pk).exists())
        self.assertTrue(FundoDepartamental.objects.filter(pk=self.fund.pk).exists())
        self.assertTrue(DepartamentoFinanceiro.objects.filter(pk=self.department.pk).exists())
        self.assertTrue(DepartamentoCaixa.objects.filter(departamento=self.department).exists())
        self.assertTrue(PoliticaFinanceiraIgreja.objects.filter(igreja=self.demo_church).exists())
        self.assertTrue(LogTransacaoFinanceira.objects.filter(pk=log.pk).exists())
        self.assertEqual(self._live_snapshot(), live_before)

    def test_late_failure_rolls_back_all_operational_mutations_and_balances(self):
        records = self._fixture()
        self.demo_account.refresh_from_db()
        before = self.demo_account.saldo_atual
        with patch('secretaria.management.commands.reset_demo.ContaBancaria.objects.filter', side_effect=RuntimeError('late normalization failure')):
            with self.assertRaisesRegex(RuntimeError, 'late normalization failure'):
                call_command('reset_demo')
        for model, record in zip((Receitas, Despesas, ContaPagar, ContaPagarAutorizacaoEvento, Despesas, RecorrenciaContaPagar, TransferenciaCaixa, FechamentoCaixa, ImportacaoExtratoOFX, LancamentoExtratoOFX), records):
            self.assertTrue(model.objects.filter(pk=record.pk).exists())
        self.demo_account.refresh_from_db(); self.assertEqual(self.demo_account.saldo_atual, before)


class ResetDemoPopularCycleTests(TestCase):
    def test_reset_popular_cycle_preserves_demo_churches_and_does_not_accumulate_events(self):
        user = get_user_model().objects.create_user('reset-cycle-live', password='senha')
        live = Ministerio.objects.create(nome_fantasia='Real', administrador_principal=user, cnpj='91000000000103', cidade='Real', estado='SP', is_demo=False)
        live_church = Igreja.objects.create(ministerio=live, nome_igreja='Real com Demo', tipo_igreja='sede')
        live_account = ContaBancaria.objects.create(igreja=live_church, nome_identificacao='Real', saldo_inicial=Decimal('10.00'), is_principal=True)
        Receitas.objects.create(igreja=live_church, categoria='oferta', data=date(2026, 1, 1), valor=Decimal('2.00'), conta_bancaria=live_account, observacao='Demo')
        live_before = (
            tuple(ContaBancaria.objects.filter(igreja=live_church).values_list('pk', 'saldo_inicial', 'saldo_atual')),
            tuple(Receitas.objects.filter(igreja=live_church).values_list('pk', 'valor')),
        )
        call_command('popular_demo')
        demo = Ministerio.objects.get(is_demo=True)
        church_ids = tuple(Igreja.objects.filter(ministerio=demo).order_by('pk').values_list('pk', flat=True))
        call_command('reset_demo'); call_command('popular_demo'); call_command('reset_demo'); call_command('popular_demo')
        self.assertEqual(Ministerio.objects.filter(is_demo=True).count(), 1)
        self.assertEqual(tuple(Igreja.objects.filter(ministerio=demo).order_by('pk').values_list('pk', flat=True)), church_ids)
        self.assertEqual(Evento.objects.filter(igreja__ministerio__is_demo=True).count(), 3)
        self.assertEqual(ContaPagar.objects.filter(igreja__ministerio__is_demo=True).count(), 0)
        self.assertEqual(RecorrenciaContaPagar.objects.filter(igreja__ministerio__is_demo=True).count(), 0)
        self.assertEqual(TransferenciaCaixa.objects.filter(caixa_origem__igreja__ministerio__is_demo=True).count(), 0)
        self.assertTrue(Receitas.objects.filter(igreja__ministerio__is_demo=True).exists())
        self.assertEqual(
            (
                tuple(ContaBancaria.objects.filter(igreja=live_church).values_list('pk', 'saldo_inicial', 'saldo_atual')),
                tuple(Receitas.objects.filter(igreja=live_church).values_list('pk', 'valor')),
            ),
            live_before,
        )