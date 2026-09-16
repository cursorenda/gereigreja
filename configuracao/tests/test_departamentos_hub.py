from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from configuracao.models import Departamento, DepartamentoCapacidade, Igreja, Ministerio
from financeiro.models import DepartamentoFinanceiro, FundoDepartamental
from financeiro.services import DepartamentoFinanceiroService


class DepartamentoHubTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='admin-departamentos')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministério Departamentos',
            administrador_principal=user,
        )
        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja Departamentos',
        )

    def test_sincronizador_mantem_contextos_tecnicos_e_vinculos_financeiros(self):
        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)

        for codigo in ('LOCAL', 'EVENTOS', 'MISSOES', 'ASSISTENCIA'):
            departamento = Departamento.objects.get(igreja=self.igreja, codigo_interno=codigo)
            financeiro = DepartamentoFinanceiro.objects.get(igreja=self.igreja, codigo_interno=codigo)
            self.assertEqual(financeiro.departamento_id, departamento.id)
            self.assertTrue(FundoDepartamental.objects.filter(igreja=self.igreja, codigo=codigo).exists())

        self.assertEqual(
            Departamento.objects.get(igreja=self.igreja, codigo_interno='LOCAL').classificacao,
            Departamento.CLASSIFICACAO_CONTEXTO_FINANCEIRO_SISTEMA,
        )
        self.assertEqual(
            Departamento.objects.get(igreja=self.igreja, codigo_interno='EVENTOS').classificacao,
            Departamento.CLASSIFICACAO_CONTEXTO_FINANCEIRO_SISTEMA,
        )
        self.assertEqual(
            Departamento.objects.get(igreja=self.igreja, codigo_interno='MISSOES').classificacao,
            Departamento.CLASSIFICACAO_LEGADO_SUGERIDO,
        )
        self.assertEqual(
            Departamento.objects.get(igreja=self.igreja, codigo_interno='ASSISTENCIA').classificacao,
            Departamento.CLASSIFICACAO_LEGADO_SUGERIDO,
        )

    def test_sincronizador_preserva_confirmacao_futura_de_legado(self):
        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)
        missoes = Departamento.objects.get(igreja=self.igreja, codigo_interno='MISSOES')
        missoes.classificacao = Departamento.CLASSIFICACAO_ORGANIZACIONAL
        missoes.save(update_fields=['classificacao'])

        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)

        missoes.refresh_from_db()
        self.assertEqual(missoes.classificacao, Departamento.CLASSIFICACAO_ORGANIZACIONAL)

    def test_hub_exclui_somente_contextos_financeiros_do_sistema(self):
        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)
        Departamento.objects.create(
            igreja=self.igreja,
            codigo_interno='JOVENS',
            nome_exibicao='Jovens',
        )

        visiveis = Departamento.objects.filter(igreja=self.igreja).exclude(
            classificacao=Departamento.CLASSIFICACAO_CONTEXTO_FINANCEIRO_SISTEMA
        )
        self.assertSetEqual(
            set(visiveis.values_list('codigo_interno', flat=True)),
            {'MISSOES', 'ASSISTENCIA', 'JOVENS'},
        )

    def test_capacidades_sao_controladas_e_unicas_por_departamento(self):
        departamento = Departamento.objects.create(
            igreja=self.igreja,
            codigo_interno='JOVENS',
            nome_exibicao='Jovens',
        )
        DepartamentoCapacidade.objects.create(
            departamento=departamento,
            capacidade=DepartamentoCapacidade.PESSOAS,
            ativa=True,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DepartamentoCapacidade.objects.create(
                    departamento=departamento,
                    capacidade=DepartamentoCapacidade.PESSOAS,
                    ativa=True,
                )

        self.assertEqual(departamento.capacidades.count(), 1)
