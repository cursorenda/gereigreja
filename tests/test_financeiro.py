from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from contas.constants import TESOUREIRO
from configuracao.models import Igreja, Ministerio, PerfilUsuario
from financeiro.models import (
    CategoriaDespesa,
    ContaBancaria,
    ContaPagar,
    Despesas,
    FechamentoCaixa,
    Fornecedor,
    ImportacaoExtratoOFX,
    LancamentoExtratoOFX,
    LogTransacaoFinanceira,
    RecorrenciaContaPagar,
    Receitas,
    TransferenciaCaixa,
)
from financeiro.forms import RecorrenciaContaPagarForm
from financeiro.services import (
    AlertaVencimentoContaPagarService,
    FechamentoCaixaService,
    OFXImportService,
    RecorrenciaContaPagarService,
)
from notificacoes.models import Notificacao
from financeiro.views import (
    criar_recorrencia_conta_pagar,
    editar_recorrencia_conta_pagar,
    gerar_despesas_fixas_mes,
    lista_despesas,
    lista_receitas,
)


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
        self.assertEqual(ContaPagar.objects.filter(recorrencia_origem=recorrencia, competencia='2026-05').count(), 1)

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
        with patch('contas.page_permissions.user_can_access_page', return_value=True), patch(
            'financeiro.views.has_finance_edit_permission', return_value=True
        ):
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

    def test_pagamento_lote_sem_contas_selecionadas_nao_processa(self):
        with patch('contas.page_permissions.user_can_access_page', return_value=True), patch(
            'financeiro.views.has_finance_edit_permission', return_value=True
        ):
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


class ReceitasViewTest(BaseFinanceiroTestCase):
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
        self.assertEqual(response.context['dizimos_dinheiro'], Decimal('30.00'))
        self.assertEqual(response.context['dizimos_pix'], Decimal('20.00'))
        self.assertEqual(response.context['dizimos_total'], Decimal('100.00'))
        self.assertEqual(response.context['ofertas_dinheiro'], Decimal('40.00'))
        self.assertEqual(response.context['ofertas_pix'], Decimal('10.00'))
        self.assertEqual(response.context['ofertas_total'], Decimal('150.00'))

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

