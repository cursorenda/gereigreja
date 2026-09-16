from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from configuracao.models import (
    Departamento,
    DepartamentoCapacidade,
    DepartamentoMinisterial,
    Igreja,
    Ministerio,
)
from configuracao.services_gestao_departamentos import DepartamentoGestaoService
from financeiro.models import DepartamentoCaixa, DepartamentoFinanceiro, FundoDepartamental


class DepartamentoGestaoServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin-service-departamentos')
        self.outro_admin = User.objects.create_user(username='outro-admin-service-departamentos')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Service Departamentos',
            administrador_principal=self.admin,
            ativo=True,
        )
        self.outro_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministerio Service Departamentos',
            administrador_principal=self.outro_admin,
            ativo=True,
        )
        self.igreja = Igreja.objects.create(ministerio=self.ministerio, nome_igreja='Igreja Service')
        self.outra_igreja = Igreja.objects.create(
            ministerio=self.outro_ministerio,
            nome_igreja='Outra Igreja Service',
        )

    def _dados_definicao(self, codigo='JOVENS', nome='Jovens'):
        return {'codigo': codigo, 'nome': nome, 'ativo': True, 'ordem': 20}

    def test_cria_definicao_normalizada_e_rejeita_duplicidade_no_mesmo_ministerio(self):
        definicao = DepartamentoGestaoService.criar_definicao_ministerial(
            ministerio=self.ministerio,
            dados=self._dados_definicao(codigo=' jovens '),
        )

        self.assertEqual(definicao.codigo, 'JOVENS')
        with self.assertRaises(ValidationError):
            DepartamentoGestaoService.criar_definicao_ministerial(
                ministerio=self.ministerio,
                dados=self._dados_definicao(),
            )
        DepartamentoGestaoService.criar_definicao_ministerial(
            ministerio=self.outro_ministerio,
            dados=self._dados_definicao(),
        )

    def test_atualizacao_rejeita_definicao_de_outro_ministerio(self):
        definicao = DepartamentoGestaoService.criar_definicao_ministerial(
            ministerio=self.ministerio,
            dados=self._dados_definicao(),
        )

        with self.assertRaises(ValidationError):
            DepartamentoGestaoService.atualizar_definicao_ministerial(
                definicao=definicao,
                ministerio=self.outro_ministerio,
                dados=self._dados_definicao(nome='Nome Indevido'),
            )

        definicao.refresh_from_db()
        self.assertEqual(definicao.nome, 'Jovens')

    def test_ativacao_e_idempotente_sem_provisionamento_financeiro(self):
        definicao = DepartamentoGestaoService.criar_definicao_ministerial(
            ministerio=self.ministerio,
            dados=self._dados_definicao(),
        )
        antes = (
            DepartamentoFinanceiro.objects.count(),
            FundoDepartamental.objects.count(),
            DepartamentoCaixa.objects.count(),
            DepartamentoCapacidade.objects.count(),
        )

        departamento, resultado = DepartamentoGestaoService.ativar_na_igreja(
            definicao=definicao,
            igreja=self.igreja,
        )
        repetido, resultado_repetido = DepartamentoGestaoService.ativar_na_igreja(
            definicao=definicao,
            igreja=self.igreja,
        )

        self.assertEqual(resultado, 'criado')
        self.assertEqual(resultado_repetido, 'ja_ativo')
        self.assertEqual(departamento.pk, repetido.pk)
        self.assertEqual(
            (
                DepartamentoFinanceiro.objects.count(),
                FundoDepartamental.objects.count(),
                DepartamentoCaixa.objects.count(),
                DepartamentoCapacidade.objects.count(),
            ),
            antes,
        )

    def test_ativacao_reaproveita_legado_e_rejeita_colisao_personalizada(self):
        definicao = DepartamentoGestaoService.criar_definicao_ministerial(
            ministerio=self.ministerio,
            dados=self._dados_definicao(),
        )
        legado = Departamento.objects.create(
            igreja=self.igreja,
            codigo_interno='JOVENS',
            nome_exibicao='Jovens Legado',
            tipo_departamento=Departamento.TIPO_PADRAO,
            classificacao=Departamento.CLASSIFICACAO_LEGADO_SUGERIDO,
            ativo=False,
        )

        departamento, resultado = DepartamentoGestaoService.ativar_na_igreja(
            definicao=definicao,
            igreja=self.igreja,
        )
        self.assertEqual(resultado, 'reutilizado')
        self.assertEqual(departamento.pk, legado.pk)
        self.assertTrue(departamento.ativo)

        outra_definicao = DepartamentoGestaoService.criar_definicao_ministerial(
            ministerio=self.ministerio,
            dados=self._dados_definicao(codigo='KIDS', nome='Kids'),
        )
        Departamento.objects.create(
            igreja=self.igreja,
            codigo_interno='KIDS',
            nome_exibicao='Kids Local',
            tipo_departamento=Departamento.TIPO_PERSONALIZADO,
        )
        with self.assertRaises(ValidationError):
            DepartamentoGestaoService.ativar_na_igreja(
                definicao=outra_definicao,
                igreja=self.igreja,
            )

    def test_reativacao_preserva_pk_e_desativacao_preserva_capacidades(self):
        definicao = DepartamentoGestaoService.criar_definicao_ministerial(
            ministerio=self.ministerio,
            dados=self._dados_definicao(),
        )
        departamento = Departamento.objects.create(
            igreja=self.igreja,
            departamento_ministerial=definicao,
            codigo_interno='JOVENS',
            nome_exibicao='Jovens',
            ativo=False,
        )
        DepartamentoCapacidade.objects.create(
            departamento=departamento,
            capacidade=DepartamentoCapacidade.PESSOAS,
        )

        reativado, resultado = DepartamentoGestaoService.ativar_na_igreja(
            definicao=definicao,
            igreja=self.igreja,
        )
        DepartamentoGestaoService.desativar_na_igreja(
            departamento=reativado,
            igreja=self.igreja,
        )

        departamento.refresh_from_db()
        self.assertEqual(resultado, 'reativado')
        self.assertEqual(reativado.pk, departamento.pk)
        self.assertFalse(departamento.ativo)
        self.assertTrue(departamento.capacidades.filter(capacidade=DepartamentoCapacidade.PESSOAS).exists())

    def test_confirmacao_e_capacidades_respeitam_igreja_e_departamento(self):
        legado = Departamento.objects.create(
            igreja=self.igreja,
            codigo_interno='LEGADO',
            nome_exibicao='Legado',
            classificacao=Departamento.CLASSIFICACAO_LEGADO_SUGERIDO,
        )
        outro = Departamento.objects.create(
            igreja=self.outra_igreja,
            codigo_interno='OUTRO',
            nome_exibicao='Outro',
        )

        with self.assertRaises(ValidationError):
            DepartamentoGestaoService.confirmar_legado(
                departamento=legado,
                igreja=self.outra_igreja,
            )
        with self.assertRaises(ValidationError):
            DepartamentoGestaoService.atualizar_capacidades(
                departamento=outro,
                igreja=self.igreja,
                capacidades=[DepartamentoCapacidade.PESSOAS],
            )
        with self.assertRaises(ValidationError):
            DepartamentoGestaoService.atualizar_capacidades(
                departamento=legado,
                igreja=self.igreja,
                capacidades=['INVALIDA'],
            )
        self.assertFalse(legado.capacidades.exists())

        DepartamentoGestaoService.confirmar_legado(departamento=legado, igreja=self.igreja)
        DepartamentoGestaoService.atualizar_capacidades(
            departamento=legado,
            igreja=self.igreja,
            capacidades=[DepartamentoCapacidade.PESSOAS, DepartamentoCapacidade.AGENDA],
        )
        legado.refresh_from_db()
        self.assertEqual(legado.classificacao, Departamento.CLASSIFICACAO_ORGANIZACIONAL)
        self.assertSetEqual(
            set(legado.capacidades.filter(ativa=True).values_list('capacidade', flat=True)),
            {DepartamentoCapacidade.PESSOAS, DepartamentoCapacidade.AGENDA},
        )