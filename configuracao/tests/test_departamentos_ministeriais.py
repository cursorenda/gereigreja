import importlib
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from contas.constants import ADMIN_MINISTERIO, PASTOR_LOCAL, SECRETARIO_LOCAL
from configuracao.models import Departamento, DepartamentoCapacidade, DepartamentoMinisterial, Igreja, Ministerio, PerfilUsuario
from financeiro.models import DepartamentoCaixa, DepartamentoFinanceiro, FundoDepartamental
from financeiro.services import DepartamentoFinanceiroService


class DepartamentoMinisterialTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(username='admin-departamentos-ministeriais')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministério Departamentos Ministeriais',
            administrador_principal=self.admin,
        )
        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja Departamentos Ministeriais',
        )
        perfil = PerfilUsuario.objects.create(user=self.admin, ministerio=self.ministerio)
        perfil.igrejas_permitidas.add(self.igreja)
        grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        self.admin.groups.add(grupo_admin)
        self.admin.refresh_from_db()
        self.client.force_login(self.admin)

    def test_codigo_e_unico_por_ministerio_mas_repetivel_em_outro(self):
        DepartamentoMinisterial.objects.create(
            ministerio=self.ministerio,
            codigo='MISSOES',
            nome='Missões',
        )
        outro_admin = get_user_model().objects.create_user(username='admin-outro-ministerio')
        outro_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministério',
            administrador_principal=outro_admin,
        )
        DepartamentoMinisterial.objects.create(
            ministerio=outro_ministerio,
            codigo='MISSOES',
            nome='Missões',
        )

        with self.assertRaises(IntegrityError):
            DepartamentoMinisterial.objects.create(
                ministerio=self.ministerio,
                codigo='MISSOES',
                nome='Missões duplicada',
            )

    def test_associacao_local_preserva_vinculos_financeiros(self):
        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)
        departamento = Departamento.objects.get(igreja=self.igreja, codigo_interno='MISSOES')
        financeiro = DepartamentoFinanceiro.objects.get(igreja=self.igreja, codigo_interno='MISSOES')
        definicao = DepartamentoMinisterial.objects.create(
            ministerio=self.ministerio,
            codigo='MISSOES',
            nome='Missões',
        )
        departamento_id = departamento.id
        financeiro_id = financeiro.id
        fundo_id = financeiro.fundo_departamental_id

        departamento.departamento_ministerial = definicao
        departamento.full_clean()
        departamento.save(update_fields=['departamento_ministerial'])

        departamento.refresh_from_db()
        financeiro.refresh_from_db()
        self.assertEqual(departamento.id, departamento_id)
        self.assertEqual(departamento.departamento_ministerial_id, definicao.id)
        self.assertEqual(financeiro.id, financeiro_id)
        self.assertEqual(financeiro.departamento_id, departamento.id)
        self.assertEqual(financeiro.fundo_departamental_id, fundo_id)

    def test_validacao_impede_definicao_de_outro_ministerio(self):
        outro_admin = get_user_model().objects.create_user(username='admin-validacao-outro-ministerio')
        outro_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministério',
            administrador_principal=outro_admin,
        )
        definicao = DepartamentoMinisterial.objects.create(
            ministerio=outro_ministerio,
            codigo='JOVENS',
            nome='Jovens',
        )
        departamento = Departamento.objects.create(
            igreja=self.igreja,
            codigo_interno='JOVENS',
            nome_exibicao='Jovens',
        )
        departamento.departamento_ministerial = definicao

        with self.assertRaises(ValidationError):
            departamento.full_clean()

    def test_migracao_inicial_so_associa_codigos_canonicos(self):
        DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(self.igreja)
        missoes = Departamento.objects.get(igreja=self.igreja, codigo_interno='MISSOES')
        local = Departamento.objects.get(igreja=self.igreja, codigo_interno='LOCAL')
        eventos = Departamento.objects.get(igreja=self.igreja, codigo_interno='EVENTOS')
        personalizado, _ = Departamento.objects.get_or_create(
            igreja=self.igreja,
            codigo_interno='JOVENS_LOCAIS',
            defaults={
                'nome_exibicao': 'Jovens Locais',
                'tipo_departamento': Departamento.TIPO_PERSONALIZADO,
                'classificacao': Departamento.CLASSIFICACAO_ORGANIZACIONAL,
            },
        )
        migration = importlib.import_module(
            'configuracao.migrations.0041_departamentoministerial_departamento_departamento_ministerial'
        )

        migration.criar_definicoes_ministeriais_iniciais(
            type('Apps', (), {'get_model': staticmethod(lambda app, model: {
                ('configuracao', 'Departamento'): Departamento,
                ('configuracao', 'DepartamentoMinisterial'): DepartamentoMinisterial,
            }[(app, model)])})(),
            None,
        )

        missoes.refresh_from_db()
        local.refresh_from_db()
        eventos.refresh_from_db()
        personalizado.refresh_from_db()
        self.assertIsNotNone(missoes.departamento_ministerial_id)
        self.assertIsNone(local.departamento_ministerial_id)
        self.assertIsNone(eventos.departamento_ministerial_id)
        self.assertIsNone(personalizado.departamento_ministerial_id)
        self.assertSetEqual(
            set(DepartamentoMinisterial.objects.values_list('codigo', flat=True)),
            {'MISSOES', 'ASSISTENCIA'},
        )

    def test_usuario_local_nao_altera_definicao_ministerial(self):
        usuario_local = get_user_model().objects.create_user(username='usuario-local-departamentos')
        perfil = PerfilUsuario.objects.create(user=usuario_local, ministerio=self.ministerio)
        perfil.igrejas_permitidas.add(self.igreja)
        self.client.force_login(usuario_local)

        response = self.client.post(
            reverse('configuracao:gestao_departamentos_ministeriais'),
            data={
                'action': 'criar_departamento_ministerial',
                'codigo': 'JOVENS',
                'nome': 'Jovens',
                'ordem': '10',
                'ativo': 'on',
            },
        )

        self.assertIn(response.status_code, {302, 403})
        self.assertFalse(DepartamentoMinisterial.objects.filter(codigo='JOVENS').exists())


class AtivacaoLocalDepartamentoMinisterialTests(TestCase):
    def setUp(self):
        administrador = get_user_model().objects.create_user(username='admin-ministerio-local')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministério Local',
            administrador_principal=administrador,
            ativo=True,
        )
        PerfilUsuario.objects.create(user=administrador, ministerio=self.ministerio)
        self.igreja = Igreja.objects.create(ministerio=self.ministerio, nome_igreja='Igreja Local')
        self.outra_igreja = Igreja.objects.create(ministerio=self.ministerio, nome_igreja='Outra Igreja')
        self.definicao = DepartamentoMinisterial.objects.create(
            ministerio=self.ministerio,
            codigo='JOVENS',
            nome='Jovens',
            ordem=20,
        )
        self.usuario_local = get_user_model().objects.create_user(username='secretario-local-departamentos')
        perfil = PerfilUsuario.objects.create(user=self.usuario_local, ministerio=self.ministerio)
        perfil.igrejas_permitidas.add(self.igreja)
        grupo, _ = Group.objects.get_or_create(name=SECRETARIO_LOCAL)
        self.usuario_local.groups.add(grupo)
        self.usuario_local.refresh_from_db()
        self.assertTrue(self.usuario_local.groups.filter(name=SECRETARIO_LOCAL).exists())
        self.url = reverse('configuracao:gestao_departamentos')
        self.client.force_login(self.usuario_local)

    def _ativar(self, definicao=None, igreja=None):
        return self.client.post(
            self.url,
            {
                'action': 'ativar_departamento_ministerial',
                'departamento_ministerial_id': (definicao or self.definicao).id,
                'igreja_id': (igreja or self.igreja).id,
            },
        )

    def test_definicao_de_outro_ministerio_nao_aparece_nem_pode_ser_ativada(self):
        outro_admin = get_user_model().objects.create_user(username='admin-outro-ministerio-local')
        outro_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministério',
            administrador_principal=outro_admin,
            ativo=True,
        )
        externa = DepartamentoMinisterial.objects.create(
            ministerio=outro_ministerio,
            codigo='MULHERES',
            nome='Mulheres externas',
        )

        response = self.client.get(self.url)

        self.assertContains(response, 'Jovens')
        self.assertNotContains(response, 'Mulheres externas')
        response = self._ativar(externa)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Departamento.objects.filter(igreja=self.igreja, codigo_interno='MULHERES').exists())

    def test_secretario_local_ativa_uma_unica_instancia_sem_recursos_financeiros(self):
        antes = {
            'financeiros': DepartamentoFinanceiro.objects.count(),
            'fundos': FundoDepartamental.objects.count(),
            'caixas': DepartamentoCaixa.objects.count(),
            'capacidades': DepartamentoCapacidade.objects.count(),
        }

        response = self._ativar()

        self.assertEqual(response.status_code, 302)
        departamento = Departamento.objects.get(igreja=self.igreja, departamento_ministerial=self.definicao)
        self.assertTrue(departamento.ativo)
        self.assertEqual(departamento.codigo_interno, 'JOVENS')
        self.assertEqual(departamento.classificacao, Departamento.CLASSIFICACAO_ORGANIZACIONAL)
        self.assertEqual(
            {
                'financeiros': DepartamentoFinanceiro.objects.count(),
                'fundos': FundoDepartamental.objects.count(),
                'caixas': DepartamentoCaixa.objects.count(),
                'capacidades': DepartamentoCapacidade.objects.count(),
            },
            antes,
        )

    def test_gestao_local_nao_exibe_nem_aceita_criacao_local(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Novo Departamento')

        response = self.client.post(
            self.url,
            {
                'action': 'criar_departamento',
                'igreja_id': self.igreja.id,
                'codigo_interno': 'NOVO_LOCAL',
                'nome_exibicao': 'Novo Local',
                'tipo_departamento': Departamento.TIPO_PERSONALIZADO,
                'ordem_exibicao': 10,
                'ativo': 'on',
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Departamento.objects.filter(igreja=self.igreja, codigo_interno='NOVO_LOCAL').exists())

    def test_admin_tambem_nao_cria_departamento_pela_gestao_local(self):
        self.client.force_login(self.ministerio.administrador_principal)

        response = self.client.post(
            self.url,
            {
                'action': 'criar_departamento',
                'igreja_id': self.igreja.id,
                'codigo_interno': 'NOVO_ADMIN_LOCAL',
                'nome_exibicao': 'Novo Admin Local',
                'tipo_departamento': Departamento.TIPO_PERSONALIZADO,
                'ordem_exibicao': 10,
                'ativo': 'on',
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Departamento.objects.filter(igreja=self.igreja, codigo_interno='NOVO_ADMIN_LOCAL').exists())

    def test_vinculo_ministerial_prevalece_sobre_estado_legado_na_ux(self):
        departamento = Departamento.objects.create(
            igreja=self.igreja,
            departamento_ministerial=self.definicao,
            codigo_interno='JOVENS',
            nome_exibicao='Jovens',
            classificacao=Departamento.CLASSIFICACAO_LEGADO_SUGERIDO,
        )

        response = self.client.get(self.url)

        self.assertContains(response, 'Origem ministerial')
        self.assertNotContains(response, 'Legado sugerido')
        self.assertNotContains(response, 'Confirmar como departamento da igreja')
        departamento.refresh_from_db()
        self.assertEqual(departamento.classificacao, Departamento.CLASSIFICACAO_LEGADO_SUGERIDO)

    def test_edicao_de_vinculado_altera_so_capacidades_locais(self):
        departamento = Departamento.objects.create(
            igreja=self.igreja,
            departamento_ministerial=self.definicao,
            codigo_interno='JOVENS',
            nome_exibicao='Jovens',
            tipo_departamento=Departamento.TIPO_PADRAO,
            ordem_exibicao=20,
        )

        response = self.client.post(
            self.url,
            {
                'action': 'editar_departamento',
                'igreja_id': self.igreja.id,
                'departamento_id': departamento.id,
                'codigo_interno': 'ALTERADO',
                'nome_exibicao': 'Nome alterado',
                'tipo_departamento': Departamento.TIPO_PERSONALIZADO,
                'ordem_exibicao': 999,
                'capacidades': [DepartamentoCapacidade.PESSOAS],
            },
        )

        self.assertEqual(response.status_code, 302)
        departamento.refresh_from_db()
        self.assertEqual(departamento.codigo_interno, 'JOVENS')
        self.assertEqual(departamento.nome_exibicao, 'Jovens')
        self.assertEqual(departamento.tipo_departamento, Departamento.TIPO_PADRAO)
        self.assertEqual(departamento.ordem_exibicao, 20)
        self.assertTrue(departamento.capacidades.get(capacidade=DepartamentoCapacidade.PESSOAS).ativa)

    def test_links_de_capacidade_dependem_da_politica_central(self):
        departamento = Departamento.objects.create(
            igreja=self.igreja,
            departamento_ministerial=self.definicao,
            codigo_interno='JOVENS',
            nome_exibicao='Jovens',
        )
        DepartamentoCapacidade.objects.create(
            departamento=departamento,
            capacidade=DepartamentoCapacidade.FINANCEIRO,
        )

        with patch('configuracao.views.user_can_access_page', side_effect=lambda user, chave, **kwargs: chave == 'financeiro'):
            response = self.client.get(self.url)
        self.assertContains(response, 'dp-financeiro-capacidade')

        with patch('configuracao.views.user_can_access_page', return_value=False):
            response = self.client.get(self.url)
        self.assertNotContains(response, 'dp-financeiro-capacidade')

        self.client.force_login(self.ministerio.administrador_principal)
        with patch('configuracao.views.user_can_access_page', return_value=False):
            response = self.client.get(self.url)
        self.assertNotContains(response, 'dp-financeiro-capacidade')

        pastor = get_user_model().objects.create_user(username='pastor-local-links-departamentos')
        perfil = PerfilUsuario.objects.create(user=pastor, ministerio=self.ministerio)
        perfil.igrejas_permitidas.add(self.igreja)
        grupo, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        pastor.groups.add(grupo)
        self.client.force_login(pastor)
        with patch('configuracao.views.user_can_access_page', side_effect=lambda user, chave, **kwargs: chave == 'financeiro'):
            response = self.client.get(self.url)
        self.assertContains(response, 'dp-financeiro-capacidade')

    def test_ativacao_por_administracao_tambem_nao_sincroniza_financeiro(self):
        antes = (
            DepartamentoFinanceiro.objects.count(),
            FundoDepartamental.objects.count(),
            DepartamentoCaixa.objects.count(),
            DepartamentoCapacidade.objects.count(),
        )
        administrador = self.ministerio.administrador_principal
        self.client.force_login(administrador)

        response = self._ativar()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Departamento.objects.filter(igreja=self.igreja, departamento_ministerial=self.definicao).exists()
        )
        self.assertEqual(
            (
                DepartamentoFinanceiro.objects.count(),
                FundoDepartamental.objects.count(),
                DepartamentoCaixa.objects.count(),
                DepartamentoCapacidade.objects.count(),
            ),
            antes,
        )

    def test_usuario_sem_autorizacao_local_e_bloqueado(self):
        usuario = get_user_model().objects.create_user(username='membro-sem-gestao-departamentos')
        usuario.groups.clear()
        perfil = PerfilUsuario.objects.create(user=usuario, ministerio=self.ministerio)
        perfil.igrejas_permitidas.add(self.igreja)
        self.client.logout()
        self.client.force_login(usuario)

        response = self._ativar()

        self.assertIn(response.status_code, {302, 403})
        self.assertFalse(Departamento.objects.filter(departamento_ministerial=self.definicao).exists())

    def test_ativacao_repetida_nao_duplica(self):
        self._ativar()
        self._ativar()

        self.assertEqual(
            Departamento.objects.filter(igreja=self.igreja, departamento_ministerial=self.definicao).count(),
            1,
        )

    def test_ativacao_reutiliza_departamento_padrao_compativel(self):
        departamento = Departamento.objects.create(
            igreja=self.igreja,
            codigo_interno='JOVENS',
            nome_exibicao='Juventude local',
            tipo_departamento=Departamento.TIPO_PADRAO,
            classificacao=Departamento.CLASSIFICACAO_LEGADO_SUGERIDO,
            ativo=False,
        )

        response = self._ativar()

        self.assertEqual(response.status_code, 302)
        departamento.refresh_from_db()
        self.assertEqual(departamento.departamento_ministerial_id, self.definicao.id)
        self.assertTrue(departamento.ativo)
        self.assertEqual(
            Departamento.objects.filter(igreja=self.igreja, departamento_ministerial=self.definicao).count(),
            1,
        )

    def test_departamento_vinculado_desativado_e_reativado_sem_mudar_id(self):
        departamento = Departamento.objects.create(
            igreja=self.igreja,
            departamento_ministerial=self.definicao,
            codigo_interno='JOVENS',
            nome_exibicao='Jovens',
            ativo=False,
        )

        response = self._ativar()

        self.assertEqual(response.status_code, 302)
        departamento.refresh_from_db()
        self.assertTrue(departamento.ativo)
        self.assertEqual(departamento.departamento_ministerial_id, self.definicao.id)
        self.assertEqual(
            Departamento.objects.filter(igreja=self.igreja, departamento_ministerial=self.definicao).count(),
            1,
        )

    def test_desativacao_preserva_vinculo_e_capacidades(self):
        departamento = Departamento.objects.create(
            igreja=self.igreja,
            departamento_ministerial=self.definicao,
            codigo_interno='JOVENS',
            nome_exibicao='Jovens',
        )
        DepartamentoCapacidade.objects.create(
            departamento=departamento,
            capacidade=DepartamentoCapacidade.PESSOAS,
        )

        response = self.client.post(
            self.url,
            {
                'action': 'desativar_departamento_ministerial',
                'departamento_id': departamento.id,
                'igreja_id': self.igreja.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        departamento.refresh_from_db()
        self.assertFalse(departamento.ativo)
        self.assertEqual(departamento.departamento_ministerial_id, self.definicao.id)
        self.assertTrue(departamento.capacidades.filter(capacidade=DepartamentoCapacidade.PESSOAS).exists())

    def test_colisao_personalizada_nao_e_sobrescrita(self):
        personalizado = Departamento.objects.create(
            igreja=self.igreja,
            codigo_interno='JOVENS',
            nome_exibicao='Jovens da Igreja',
            tipo_departamento=Departamento.TIPO_PERSONALIZADO,
        )

        response = self._ativar()

        self.assertEqual(response.status_code, 302)
        personalizado.refresh_from_db()
        self.assertIsNone(personalizado.departamento_ministerial_id)
        self.assertEqual(Departamento.objects.filter(igreja=self.igreja, codigo_interno='JOVENS').count(), 1)

    def test_contextos_tecnicos_nunca_entram_no_fluxo_local(self):
        local = DepartamentoMinisterial.objects.create(
            ministerio=self.ministerio,
            codigo='LOCAL',
            nome='Tesouraria Local',
        )
        eventos = DepartamentoMinisterial.objects.create(
            ministerio=self.ministerio,
            codigo='EVENTOS',
            nome='Eventos',
        )

        response = self.client.get(self.url)

        self.assertNotIn(local.id, [item.id for item in response.context['departamentos_ministeriais_disponiveis']])
        self.assertNotIn(eventos.id, [item.id for item in response.context['departamentos_ministeriais_disponiveis']])
        self.assertEqual(self._ativar(local).status_code, 404)
        self.assertEqual(self._ativar(eventos).status_code, 404)
        self.assertFalse(
            Departamento.objects.filter(
                igreja=self.igreja,
                codigo_interno__in=['LOCAL', 'EVENTOS'],
                departamento_ministerial__in=[local, eventos],
            ).exists()
        )

    def test_isolamento_entre_igrejas(self):
        response = self._ativar(igreja=self.outra_igreja)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            Departamento.objects.filter(
                igreja=self.outra_igreja,
                departamento_ministerial=self.definicao,
            ).exists()
        )
