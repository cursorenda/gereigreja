from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from contas.constants import ADMIN_MINISTERIO, TESOUREIRO
from configuracao.models import Departamento, DepartamentoCapacidade, Igreja, Ministerio, PerfilUsuario
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
    PoliticaDepartamentoFinanceiro,
    RecorrenciaContaPagar,
    Receitas,
    TransferenciaCaixa,
)
from financeiro.forms import RecorrenciaContaPagarForm
from financeiro.forms import ReceitaForm, DespesaForm
from financeiro.services import (
    AlertaVencimentoContaPagarService,
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

    def test_cadastrar_despesa_caixa_eventos_restringe_categorias_para_contexto_eventos(self):
        response = self.client.get(reverse('financeiro:cadastrar_despesa_caixa_eventos'))

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        categorias_renderizadas = list(form.fields['categoria'].queryset.values_list('nome', flat=True))

        for nome_categoria in categorias_despesa_padrao_eventos():
            self.assertIn(nome_categoria, categorias_renderizadas)
        self.assertNotIn(self.categoria.nome, categorias_renderizadas)

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
