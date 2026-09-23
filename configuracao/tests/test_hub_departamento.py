from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sessions.middleware import SessionMiddleware
from django.db import connection
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from contas.constants import ADMIN_MINISTERIO, PASTOR_LOCAL, SECRETARIO_LOCAL
from configuracao.models import (
    Departamento,
    DepartamentoCapacidade,
    DepartamentoVinculo,
    Igreja,
    Ministerio,
    PerfilUsuario,
)
from configuracao.views import hub_departamento
from financeiro.models import DepartamentoFinanceiro
from secretaria.models import Cargo, MembroCargo, Pessoa, StatusPessoa, TipoPessoa


class HubDepartamentoTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_a = User.objects.create_user(username='admin-hub-dep-a')
        self.admin_b = User.objects.create_user(username='admin-hub-dep-b')
        self.user = User.objects.create_user(username='usuario-hub-dep')
        self.outro_user = User.objects.create_user(username='outro-hub-dep')
        self.sem_pessoa = User.objects.create_user(username='sem-pessoa-hub-dep')
        self.ministerio_a = Ministerio.objects.create(
            nome_fantasia='Ministerio Hub A', administrador_principal=self.admin_a, ativo=True
        )
        self.ministerio_b = Ministerio.objects.create(
            nome_fantasia='Ministerio Hub B', administrador_principal=self.admin_b, ativo=True
        )
        self.igreja_a = Igreja.objects.create(ministerio=self.ministerio_a, nome_igreja='Igreja Hub A')
        self.igreja_b = Igreja.objects.create(ministerio=self.ministerio_a, nome_igreja='Igreja Hub B')
        self.igreja_c = Igreja.objects.create(ministerio=self.ministerio_b, nome_igreja='Igreja Hub C')
        self.perfil = PerfilUsuario.objects.create(user=self.user, ministerio=self.ministerio_a)
        self.perfil.igrejas_permitidas.add(self.igreja_a)
        PerfilUsuario.objects.create(user=self.outro_user, ministerio=self.ministerio_a)
        PerfilUsuario.objects.create(user=self.sem_pessoa, ministerio=self.ministerio_a)
        grupo, _ = Group.objects.get_or_create(name=SECRETARIO_LOCAL)
        self.user.groups.add(grupo)
        self.outro_user.groups.add(grupo)
        self.sem_pessoa.groups.add(grupo)
        tipo = TipoPessoa.objects.create(nome='Membro Hub Departamento')
        status = StatusPessoa.objects.create(nome='Ativo Hub Departamento')
        self.pessoa, self.outra_pessoa = Pessoa.objects.bulk_create(
            [
                Pessoa(
                    usuario=self.user,
                    igreja=self.igreja_a,
                    nome='Pessoa Hub',
                    tipo_pessoa=tipo,
                    status_pessoa=status,
                ),
                Pessoa(
                    usuario=self.outro_user,
                    igreja=self.igreja_b,
                    nome='Outra Pessoa Hub',
                    tipo_pessoa=tipo,
                    status_pessoa=status,
                ),
            ]
        )
        self.departamento = Departamento.objects.get(igreja=self.igreja_a, codigo_interno='MISSOES')
        self.departamento_b = Departamento.objects.get(igreja=self.igreja_b, codigo_interno='MISSOES')
        self.departamento_c = Departamento.objects.get(igreja=self.igreja_c, codigo_interno='MISSOES')
        self.cargo = Cargo.objects.create(nome='Funcao Hub')
        self.vinculo = DepartamentoVinculo.objects.create(
            departamento=self.departamento,
            membro=self.pessoa,
            cargo=self.cargo,
            criado_por=self.user,
        )
        self.url = reverse('configuracao:hub_departamento', args=[self.departamento.pk])

    def _ativar_capacidade(self, capacidade, departamento=None):
        DepartamentoCapacidade.objects.update_or_create(
            departamento=departamento or self.departamento,
            capacidade=capacidade,
            defaults={'ativa': True},
        )

    def test_vinculo_proprio_ativo_abre_hub_readonly(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.departamento.nome_exibicao)
        self.assertContains(response, self.igreja_a.nome_igreja)
        self.assertContains(response, self.cargo.nome)
        self.assertContains(response, 'não representam permissões pessoais')
        self.assertNotContains(response, 'Equipe do departamento')
        self.assertEqual(self.client.post(self.url).status_code, 405)

    def test_vinculo_encerrado_e_usuario_sem_pessoa_retornam_404(self):
        self.vinculo.data_fim = date.today()
        self.vinculo.save(update_fields=['data_fim'])
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.client.force_login(self.sem_pessoa)
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_id_de_vinculo_alheio_ou_outro_tenant_retorna_mesmo_404(self):
        vinculo_alheio = DepartamentoVinculo.objects.create(
            departamento=self.departamento_b,
            membro=self.outra_pessoa,
            criado_por=self.outro_user,
        )
        self.client.force_login(self.user)
        for departamento in (self.departamento_b, self.departamento_c):
            response = self.client.get(reverse('configuracao:hub_departamento', args=[departamento.pk]))
            self.assertEqual(response.status_code, 404)
            self.assertNotContains(response, departamento.nome_exibicao, status_code=404)
        self.assertEqual(vinculo_alheio.data_fim, None)

    def test_cargo_capacidade_e_capacidades_futuras_nao_concedem_atalhos(self):
        grupo = Group.objects.create(name='Grupo Inerte Hub')
        self.cargo.grupo_permissao = grupo
        self.cargo.save(update_fields=['grupo_permissao'])
        for capacidade in (
            DepartamentoCapacidade.AGENDA,
            DepartamentoCapacidade.FINANCEIRO,
            DepartamentoCapacidade.ESCALAS,
            DepartamentoCapacidade.TAREFAS,
            DepartamentoCapacidade.ALMOXARIFADO,
        ):
            self._ativar_capacidade(capacidade)
        self.client.force_login(self.user)
        with patch('configuracao.views.user_can_access_page', return_value=False):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Escalas')
        self.assertContains(response, 'Tarefas')
        self.assertContains(response, 'Almoxarifado')
        self.assertEqual(response.context['atalhos_igreja'], [])
        self.assertEqual(response.context['atalhos_financeiros'], [])
        self.assertFalse(self.user.groups.filter(pk=grupo.pk).exists())

    def test_financeiro_exige_politica_e_escopo_da_igreja(self):
        self._ativar_capacidade(DepartamentoCapacidade.FINANCEIRO)
        self.client.force_login(self.user)
        with patch('configuracao.views.user_can_access_page', return_value=False):
            negado_politica = self.client.get(self.url)
        self.assertEqual(negado_politica.context['atalhos_financeiros'], [])

    def test_financeiro_autorizado_usa_somente_contexto_resolvido_do_departamento(self):
        self._ativar_capacidade(DepartamentoCapacidade.FINANCEIRO)
        financeiro = DepartamentoFinanceiro.objects.get(departamento=self.departamento)
        financeiro_alheio = DepartamentoFinanceiro.objects.get(departamento=self.departamento_b)
        self.client.force_login(self.user)
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja_a.pk
        session.save()
        with patch('configuracao.views.user_can_access_page', return_value=True):
            response = self.client.get(self.url)
        fundo_id = financeiro.fundo_departamental_id
        self.assertContains(response, f'{reverse("financeiro:lista_receitas")}?fundo_filtro={fundo_id}')
        self.assertContains(response, f'{reverse("financeiro:lista_despesas")}?fundo_filtro={fundo_id}')
        self.assertContains(response, f'dept_filtro={financeiro.pk}')
        self.assertNotContains(response, f'dept_filtro={financeiro_alheio.pk}')

    def test_financeiro_nao_aparece_fora_do_contexto_ativo(self):
        self._ativar_capacidade(DepartamentoCapacidade.FINANCEIRO)
        self.perfil.igrejas_permitidas.add(self.igreja_b)
        self.client.force_login(self.user)
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja_b.pk
        session.save()

        with patch('configuracao.views.user_can_access_page', return_value=True):
            response = self.client.get(self.url)

        self.assertEqual(response.context['atalhos_financeiros'], [])

    def test_atalhos_da_igreja_exigem_politica_escopo_e_igreja_ativa_igual(self):
        for capacidade in (
            DepartamentoCapacidade.PESSOAS,
            DepartamentoCapacidade.AGENDA,
            DepartamentoCapacidade.EVENTOS,
            DepartamentoCapacidade.COMUNICACAO,
        ):
            self._ativar_capacidade(capacidade)
        request = RequestFactory().get(self.url)
        request.user = get_user_model().objects.get(pk=self.user.pk)
        SessionMiddleware(lambda req: None).process_request(request)
        request.igrejas_permitidas = Igreja.objects.filter(pk=self.igreja_a.pk)
        request.igreja_ativa = self.igreja_a
        with patch('configuracao.views.user_can_access_page', return_value=True), patch(
            'configuracao.views.render', return_value=HttpResponse()
        ) as renderizar:
            hub_departamento(request, self.departamento.pk)
        atalhos = renderizar.call_args.args[2]['atalhos_igreja']
        self.assertEqual({item['rotulo'] for item in atalhos}, {'Pessoas', 'Agenda', 'Eventos', 'Comunicacao'})

        request.igreja_ativa = self.igreja_b
        with patch('configuracao.views.user_can_access_page', return_value=True), patch(
            'configuracao.views.render', return_value=HttpResponse()
        ) as renderizar:
            hub_departamento(request, self.departamento.pk)
        self.assertEqual(renderizar.call_args.args[2]['atalhos_igreja'], [])

    def test_outra_igreja_selecionavel_exibe_acao_post_de_troca(self):
        self.perfil.igrejas_permitidas.add(self.igreja_b)
        self.client.force_login(self.user)
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja_b.pk
        session.save()

        response = self.client.get(self.url)

        self.assertContains(response, f'Acessar recursos na Igreja {self.igreja_a.nome_igreja}')
        self.assertContains(response, f'action="{reverse("configuracao:set_active_church")}"')
        self.assertContains(response, f'name="igreja_id_selector" value="{self.igreja_a.pk}"')
        self.assertContains(response, f'name="next" value="{self.url}"')

    def test_mesma_igreja_mantem_atalhos_e_nao_exibe_acao_de_troca(self):
        self._ativar_capacidade(DepartamentoCapacidade.AGENDA)
        self.client.force_login(self.user)
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja_a.pk
        session.save()
        with patch('configuracao.views.user_can_access_page', return_value=True):
            response = self.client.get(self.url)
        self.assertContains(response, 'Recursos autorizados da igreja')
        self.assertNotContains(response, 'Acessar recursos na Igreja')

    def test_outra_igreja_nao_selecionavel_e_vinculo_sozinho_nao_oferecem_troca(self):
        self.perfil.igrejas_permitidas.clear()
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Acessar recursos na Igreja')

    def test_post_canonico_troca_contexto_e_retorna_ao_hub(self):
        self.perfil.igrejas_permitidas.add(self.igreja_b)
        self.client.force_login(self.user)
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja_b.pk
        session.save()
        grupos_antes = set(self.user.groups.values_list('pk', flat=True))
        cargos_antes = MembroCargo.objects.count()
        vinculos_antes = list(DepartamentoVinculo.objects.values_list('pk', 'data_fim'))

        response = self.client.post(
            reverse('configuracao:set_active_church'),
            {'igreja_id_selector': self.igreja_a.pk, 'next': self.url},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url)
        self.assertEqual(self.client.session['igreja_ativa_id'], self.igreja_a.pk)
        self.assertEqual(set(self.user.groups.values_list('pk', flat=True)), grupos_antes)
        self.assertEqual(MembroCargo.objects.count(), cargos_antes)
        self.assertEqual(list(DepartamentoVinculo.objects.values_list('pk', 'data_fim')), vinculos_antes)

    def test_get_e_id_manipulado_continuam_bloqueados_pelo_endpoint(self):
        self.perfil.igrejas_permitidas.add(self.igreja_b)
        self.client.force_login(self.user)
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja_a.pk
        session.save()
        endpoint = reverse('configuracao:set_active_church')

        self.assertEqual(self.client.get(endpoint, {'igreja_id_selector': self.igreja_b.pk}).status_code, 405)
        self.client.post(
            endpoint,
            {'igreja_id_selector': self.igreja_c.pk, 'next': self.url},
        )
        self.assertEqual(self.client.session['igreja_ativa_id'], self.igreja_a.pk)

    def test_hub_nao_troca_igreja_ativa_nem_altera_dados_autorizativos(self):
        self._ativar_capacidade(DepartamentoCapacidade.AGENDA)
        grupos_antes = set(self.user.groups.values_list('pk', flat=True))
        membro_cargo_antes = MembroCargo.objects.count()
        vinculos_antes = list(DepartamentoVinculo.objects.values_list('pk', 'data_fim'))
        self.client.force_login(self.user)
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja_a.pk
        session.save()
        self.client.get(self.url)
        self.assertEqual(self.client.session['igreja_ativa_id'], self.igreja_a.pk)
        self.assertEqual(set(self.user.groups.values_list('pk', flat=True)), grupos_antes)
        self.assertEqual(MembroCargo.objects.count(), membro_cargo_antes)
        self.assertEqual(list(DepartamentoVinculo.objects.values_list('pk', 'data_fim')), vinculos_antes)

    def test_admin_usa_escopo_aditivo_por_tipo_de_igreja_e_papel_local(self):
        admin = get_user_model().objects.create_user(username='admin-tipos-hub')
        perfil_admin = PerfilUsuario.objects.create(user=admin, ministerio=self.ministerio_a)
        grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        grupo_pastor, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        admin.groups.add(grupo_admin)
        tipo = TipoPessoa.objects.create(nome='Membro Admin Hub')
        status = StatusPessoa.objects.create(nome='Ativo Admin Hub')
        sede = Igreja.objects.create(ministerio=self.ministerio_a, nome_igreja='Sede Admin Hub', tipo_igreja='sede')
        independente = Igreja.objects.create(
            ministerio=self.ministerio_a,
            nome_igreja='Independente Admin Hub',
            tipo_igreja='independente',
        )
        regional = Igreja.objects.create(ministerio=self.ministerio_a, nome_igreja='Regional Admin Hub', tipo_igreja='regional')
        congregacao = Igreja.objects.create(
            ministerio=self.ministerio_a,
            nome_igreja='Congregacao Admin Hub',
            tipo_igreja='congregacao',
            igreja_superior=regional,
        )
        pessoa_admin = Pessoa.objects.create(
            usuario=admin,
            igreja=sede,
            nome='Pessoa Admin Hub',
            tipo_pessoa=tipo,
            status_pessoa=status,
        )
        departamentos = {
            igreja.tipo_igreja: Departamento.objects.get(igreja=igreja, codigo_interno='MISSOES')
            for igreja in (sede, independente, regional, congregacao)
        }
        for departamento in departamentos.values():
            DepartamentoVinculo.objects.create(membro=pessoa_admin, departamento=departamento, criado_por=admin)
            self._ativar_capacidade(DepartamentoCapacidade.AGENDA, departamento)

        self.client.force_login(admin)
        with patch('configuracao.views.user_can_access_page', return_value=True):
            for tipo_igreja, esperado in {
                'sede': True,
                'independente': True,
                'regional': False,
                'congregacao': False,
            }.items():
                departamento = departamentos[tipo_igreja]
                session = self.client.session
                session['igreja_ativa_id'] = departamento.igreja_id
                session.save()
                response = self.client.get(reverse('configuracao:hub_departamento', args=[departamento.pk]))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(bool(response.context['atalhos_igreja']), esperado)

        admin.groups.add(grupo_pastor)
        perfil_admin.igrejas_permitidas.add(congregacao)
        session = self.client.session
        session['igreja_ativa_id'] = congregacao.pk
        session.save()
        with patch('configuracao.views.user_can_access_page', return_value=True):
            response = self.client.get(reverse('configuracao:hub_departamento', args=[departamentos['congregacao'].pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['atalhos_igreja'])

    def test_botao_troca_contexto_admin_exige_escopo_operacional_local(self):
        admin = get_user_model().objects.create_user(username='admin-troca-contexto-hub')
        perfil_admin = PerfilUsuario.objects.create(user=admin, ministerio=self.ministerio_a)
        grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        grupo_pastor, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        admin.groups.add(grupo_admin)
        tipo = TipoPessoa.objects.create(nome='Membro Troca Contexto Hub')
        status = StatusPessoa.objects.create(nome='Ativo Troca Contexto Hub')
        sede = Igreja.objects.create(
            ministerio=self.ministerio_a,
            nome_igreja='Sede Troca Contexto Hub',
            tipo_igreja='sede',
        )
        regional = Igreja.objects.create(
            ministerio=self.ministerio_a,
            nome_igreja='Regional Troca Contexto Hub',
            tipo_igreja='regional',
            igreja_superior=sede,
        )
        congregacao = Igreja.objects.create(
            ministerio=self.ministerio_a,
            nome_igreja='Congregacao Troca Contexto Hub',
            tipo_igreja='congregacao',
            igreja_superior=regional,
        )
        pessoa_admin = Pessoa.objects.create(
            usuario=admin,
            igreja=sede,
            nome='Pessoa Troca Contexto Hub',
            tipo_pessoa=tipo,
            status_pessoa=status,
        )
        departamentos = {
            igreja.tipo_igreja: Departamento.objects.get(igreja=igreja, codigo_interno='MISSOES')
            for igreja in (sede, regional, congregacao)
        }
        for departamento in departamentos.values():
            DepartamentoVinculo.objects.create(
                membro=pessoa_admin,
                departamento=departamento,
                criado_por=admin,
            )

        self.client.force_login(admin)
        session = self.client.session
        session['igreja_ativa_id'] = sede.pk
        session.save()

        for tipo_igreja in ('regional', 'congregacao'):
            response = self.client.get(
                reverse('configuracao:hub_departamento', args=[departamentos[tipo_igreja].pk])
            )
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.context['pode_trocar_contexto_igreja'])

        admin.groups.add(grupo_pastor)
        perfil_admin.igrejas_permitidas.add(congregacao)
        response = self.client.get(
            reverse('configuracao:hub_departamento', args=[departamentos['congregacao'].pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['pode_trocar_contexto_igreja'])

    def test_queries_da_view_isolada_nao_crescem_com_capacidades(self):
        request = RequestFactory().get(self.url)
        request.user = get_user_model().objects.get(pk=self.user.pk)
        SessionMiddleware(lambda req: None).process_request(request)
        request.igreja_ativa = self.igreja_a
        request.igrejas_permitidas = Igreja.objects.filter(pk=self.igreja_a.pk)
        with patch('configuracao.views.render', return_value=HttpResponse()), CaptureQueriesContext(connection) as base:
            hub_departamento(request, self.departamento.pk)
        for capacidade in (
            DepartamentoCapacidade.PESSOAS,
            DepartamentoCapacidade.AGENDA,
            DepartamentoCapacidade.EVENTOS,
            DepartamentoCapacidade.COMUNICACAO,
            DepartamentoCapacidade.ESCALAS,
            DepartamentoCapacidade.TAREFAS,
            DepartamentoCapacidade.ALMOXARIFADO,
        ):
            self._ativar_capacidade(capacidade)
        with patch('configuracao.views.user_can_access_page', return_value=False), patch(
            'configuracao.views.render', return_value=HttpResponse()
        ), CaptureQueriesContext(connection) as completo:
            hub_departamento(request, self.departamento.pk)
        self.assertLessEqual(len(completo), len(base) + 1)
        self.assertLessEqual(len(completo), 8)
