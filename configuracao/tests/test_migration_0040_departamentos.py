from importlib import import_module

from django.contrib.auth import get_user_model
from django.test import TestCase

from configuracao.models import Departamento, DepartamentoCapacidade, Igreja, Ministerio
from financeiro.models import ContaBancaria, DepartamentoCaixa, DepartamentoFinanceiro, FundoDepartamental


class _CurrentAppsRegistry:
    """Registry controlado para exercitar somente o RunPython da migration 0040."""

    models = {
        ('configuracao', 'Departamento'): Departamento,
        ('configuracao', 'DepartamentoCapacidade'): DepartamentoCapacidade,
        ('financeiro', 'DepartamentoFinanceiro'): DepartamentoFinanceiro,
    }

    def get_model(self, app_label, model_name):
        return self.models[(app_label, model_name)]


class Migration0040DepartamentosTests(TestCase):
    """Valida a transformação de dados da 0040 sem depender da cadeia histórica."""

    def setUp(self):
        user = get_user_model().objects.create_user(username='migration-0040-admin')
        ministerio = Ministerio.objects.create(
            nome_fantasia='Ministério Migration 0040',
            administrador_principal=user,
        )
        self.igreja = Igreja.objects.create(
            ministerio=ministerio,
            nome_igreja='Igreja Migration 0040',
            tipo_igreja='congregacao',
        )
        self.caixa = ContaBancaria.objects.create(
            igreja=self.igreja,
            nome_identificacao='Caixa Migration 0040',
            tipo='caixa_fisico',
            saldo_inicial='0.00',
        )
        self.departamentos = {}
        self.financeiros = {}
        self.fundos = {}

        for codigo, nome in (
            ('LOCAL', 'Tesouraria Local'),
            ('EVENTOS', 'Eventos'),
            ('MISSOES', 'Missões'),
            ('ASSISTENCIA', 'Assistência Social'),
        ):
            departamento, _ = Departamento.objects.get_or_create(
                igreja=self.igreja,
                codigo_interno=codigo,
                defaults={
                    'nome_exibicao': nome,
                    'tipo_departamento': Departamento.TIPO_PADRAO,
                    'ativo': True,
                },
            )
            departamento.nome_exibicao = nome
            departamento.tipo_departamento = Departamento.TIPO_PADRAO
            departamento.ativo = True
            departamento.classificacao = Departamento.CLASSIFICACAO_ORGANIZACIONAL
            departamento.save()

            fundo, _ = FundoDepartamental.objects.get_or_create(
                igreja=self.igreja,
                codigo=codigo,
                defaults={'nome_exibicao': nome, 'ativo': True},
            )
            fundo.nome_exibicao = nome
            fundo.ativo = True
            fundo.save()

            financeiro, _ = DepartamentoFinanceiro.objects.get_or_create(
                igreja=self.igreja,
                codigo_interno=codigo,
                defaults={
                    'nome_exibicao': nome,
                    'tipo_departamento': DepartamentoFinanceiro.TIPO_PADRAO,
                    'ativo': True,
                    'departamento': departamento,
                    'fundo_departamental': fundo,
                },
            )
            financeiro.nome_exibicao = nome
            financeiro.tipo_departamento = DepartamentoFinanceiro.TIPO_PADRAO
            financeiro.ativo = True
            financeiro.departamento = departamento
            financeiro.fundo_departamental = fundo
            financeiro.save()
            self.departamentos[codigo] = departamento.id
            self.financeiros[codigo] = financeiro.id
            self.fundos[codigo] = fundo.id

        self.personalizado = Departamento.objects.create(
            igreja=self.igreja,
            codigo_interno='JOVENS',
            nome_exibicao='Ministério de Jovens',
            tipo_departamento=Departamento.TIPO_PERSONALIZADO,
            ativo=True,
        )
        self.vinculo_caixa = DepartamentoCaixa.objects.create(
            departamento_id=self.financeiros['LOCAL'],
            conta_bancaria=self.caixa,
            ativo=True,
            is_padrao=True,
        )

    def test_runpython_classifica_e_preserva_registros_existentes(self):
        migration = import_module('configuracao.migrations.0040_departamento_capacidades_e_classificacao')
        registry = _CurrentAppsRegistry()
        quantidade_departamentos_antes = Departamento.objects.filter(igreja=self.igreja).count()

        migration.classificar_departamentos_existentes(registry, schema_editor=None)
        migration.classificar_departamentos_existentes(registry, schema_editor=None)

        classificacoes_esperadas = {
            'LOCAL': Departamento.CLASSIFICACAO_CONTEXTO_FINANCEIRO_SISTEMA,
            'EVENTOS': Departamento.CLASSIFICACAO_CONTEXTO_FINANCEIRO_SISTEMA,
            'MISSOES': Departamento.CLASSIFICACAO_LEGADO_SUGERIDO,
            'ASSISTENCIA': Departamento.CLASSIFICACAO_LEGADO_SUGERIDO,
        }
        self.assertEqual(Departamento.objects.filter(igreja=self.igreja).count(), quantidade_departamentos_antes)

        for codigo, classificacao in classificacoes_esperadas.items():
            departamento = Departamento.objects.get(pk=self.departamentos[codigo])
            financeiro = DepartamentoFinanceiro.objects.get(pk=self.financeiros[codigo])
            fundo = FundoDepartamental.objects.get(pk=self.fundos[codigo])

            self.assertEqual(departamento.classificacao, classificacao)
            self.assertEqual(financeiro.departamento_id, departamento.id)
            self.assertEqual(financeiro.fundo_departamental_id, fundo.id)
            self.assertEqual(fundo.igreja_id, self.igreja.id)
            self.assertEqual(
                DepartamentoCapacidade.objects.filter(
                    departamento=departamento,
                    capacidade=DepartamentoCapacidade.FINANCEIRO,
                    ativa=True,
                ).count(),
                1,
            )

        self.personalizado.refresh_from_db()
        self.assertEqual(self.personalizado.classificacao, Departamento.CLASSIFICACAO_ORGANIZACIONAL)
        self.assertFalse(DepartamentoCapacidade.objects.filter(departamento=self.personalizado).exists())

        vinculo_caixa = DepartamentoCaixa.objects.get(pk=self.vinculo_caixa.id)
        self.assertEqual(vinculo_caixa.departamento_id, self.financeiros['LOCAL'])
        self.assertEqual(vinculo_caixa.conta_bancaria_id, self.caixa.id)
