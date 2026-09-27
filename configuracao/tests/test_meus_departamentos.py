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

from contas.constants import ADMIN_MINISTERIO, PASTOR_LOCAL, SECRETARIO_LOCAL, TESOUREIRO
from configuracao.models import (
    Departamento,
    DepartamentoCapacidade,
    DepartamentoVinculo,
    Igreja,
    Ministerio,
    PerfilUsuario,
)
from configuracao.views import meus_departamentos
from secretaria.models import Cargo, MembroCargo, Pessoa, StatusPessoa, TipoPessoa


class MeusDepartamentosTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_a = User.objects.create_user(username='admin-meus-deps-a')
        self.admin_b = User.objects.create_user(username='admin-meus-deps-b')
        self.user = User.objects.create_user(username='usuario-meus-deps')
        self.outro_user = User.objects.create_user(username='outro-meus-deps')
        self.sem_pessoa = User.objects.create_user(username='sem-pessoa-meus-deps')
        self.ministerio_a = Ministerio.objects.create(
            nome_fantasia='Ministerio Teste Meus Departamentos',
            administrador_principal=self.admin_a,
            ativo=True,
            is_demo=False,
        )
        self.ministerio_b = Ministerio.objects.create(
            nome_fantasia='Outro Ministerio Meus Departamentos',
            administrador_principal=self.admin_b,
            ativo=True,
        )
        self.igreja_a = Igreja.objects.create(ministerio=self.ministerio_a, nome_igreja='Igreja A')
        self.igreja_b = Igreja.objects.create(ministerio=self.ministerio_a, nome_igreja='Igreja B')
        self.igreja_outro_ministerio = Igreja.objects.create(
            ministerio=self.ministerio_b,
            nome_igreja='Igreja Outro Ministerio',
        )
        self.perfil = PerfilUsuario.objects.create(user=self.user, ministerio=self.ministerio_a)
        self.perfil.igrejas_permitidas.add(self.igreja_a)
        PerfilUsuario.objects.create(user=self.outro_user, ministerio=self.ministerio_a)
        PerfilUsuario.objects.create(user=self.sem_pessoa, ministerio=self.ministerio_a)
        grupo_secretario, _ = Group.objects.get_or_create(name=SECRETARIO_LOCAL)
        self.user.groups.add(grupo_secretario)
        self.sem_pessoa.groups.add(grupo_secretario)

        tipo = TipoPessoa.objects.create(nome='Membro Meus Departamentos')
        status = StatusPessoa.objects.create(nome='Ativo Meus Departamentos')
        self.pessoa, self.outra_pessoa = Pessoa.objects.bulk_create(
            [
                Pessoa(
                    usuario=self.user,
                    igreja=self.igreja_a,
                    nome='Pessoa Autenticada',
                    tipo_pessoa=tipo,
                    status_pessoa=status,
                ),
                Pessoa(
                    usuario=self.outro_user,
                    igreja=self.igreja_b,
                    nome='Outra Pessoa',
                    tipo_pessoa=tipo,
                    status_pessoa=status,
                ),
            ]
        )
        self.departamento_a = Departamento.objects.get(igreja=self.igreja_a, codigo_interno='MISSOES')
        self.departamento_b = Departamento.objects.get(igreja=self.igreja_b, codigo_interno='MISSOES')
        self.departamento_outro_ministerio = Departamento.objects.get(
            igreja=self.igreja_outro_ministerio,
            codigo_interno='MISSOES',
        )
        self.cargo = Cargo.objects.create(nome='Funcao Departamental de Teste')
        self.url = reverse('configuracao:meus_departamentos')

    def _vincular(self, pessoa=None, departamento=None, **kwargs):
        return DepartamentoVinculo.objects.create(
            membro=pessoa or self.pessoa,
            departamento=departamento or self.departamento_a,
            criado_por=self.user,
            **kwargs,
        )

    def test_exibe_somente_vinculos_ativos_da_pessoa_autenticada(self):
        ativo = self._vincular(cargo=self.cargo)
        encerrado = self._vincular(
            departamento=Departamento.objects.get(igreja=self.igreja_a, codigo_interno='ASSISTENCIA'),
            data_fim=date.today(),
        )
        outro = self._vincular(pessoa=self.outra_pessoa, departamento=self.departamento_b)
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ativo.departamento.nome_exibicao)
        self.assertContains(response, self.cargo.nome)
        self.assertNotContains(response, encerrado.departamento.nome_exibicao)
        self.assertNotContains(response, outro.membro.nome)

    def test_usuario_sem_pessoa_recebe_estado_vazio(self):
        self.client.force_login(self.sem_pessoa)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Você ainda não possui departamentos ativos')

    def test_isolamento_igreja_ministerio_e_parametros_idor_ignorados(self):
        vinculo_b = self._vincular(pessoa=self.outra_pessoa, departamento=self.departamento_b)
        pessoa_outro_ministerio = Pessoa.objects.bulk_create(
            [
                Pessoa(
                    igreja=self.igreja_outro_ministerio,
                    nome='Pessoa Outro Ministerio',
                    tipo_pessoa=self.pessoa.tipo_pessoa,
                    status_pessoa=self.pessoa.status_pessoa,
                )
            ]
        )[0]
        vinculo_outro_ministerio = self._vincular(
            pessoa=pessoa_outro_ministerio,
            departamento=self.departamento_outro_ministerio,
        )
        self.client.force_login(self.user)

        response = self.client.get(
            self.url,
            {
                'membro_id': vinculo_b.membro_id,
                'pessoa_id': vinculo_outro_ministerio.membro_id,
                'departamento_id': self.departamento_b.pk,
                'igreja_id': self.igreja_b.pk,
            },
        )

        self.assertNotContains(response, self.departamento_b.igreja.nome_igreja)
        self.assertNotContains(response, self.departamento_outro_ministerio.igreja.nome_igreja)
        self.assertContains(response, 'Você ainda não possui departamentos ativos')

    def test_cargo_e_capacidade_nao_concedem_financeiro(self):
        grupo_financeiro, _ = Group.objects.get_or_create(name=TESOUREIRO)
        self.cargo.grupo_permissao = grupo_financeiro
        self.cargo.save(update_fields=['grupo_permissao'])
        self._vincular(cargo=self.cargo)
        DepartamentoCapacidade.objects.update_or_create(
            departamento=self.departamento_a,
            capacidade=DepartamentoCapacidade.FINANCEIRO,
            defaults={'ativa': True},
        )
        self.client.force_login(self.user)
        financeiro_url = reverse('financeiro:painel_financeiro')

        response = self.client.get(self.url)

        self.assertContains(response, 'Financeiro')
        self.assertNotContains(response, f'href="{financeiro_url}?igreja_filtro={self.igreja_a.pk}"')
        self.assertFalse(self.user.groups.filter(pk=grupo_financeiro.pk).exists())

    def test_financeiro_aparece_somente_com_politica_real_na_igreja(self):
        grupo_pastor, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        self.user.groups.add(grupo_pastor)
        self._vincular()
        DepartamentoCapacidade.objects.update_or_create(
            departamento=self.departamento_a,
            capacidade=DepartamentoCapacidade.FINANCEIRO,
            defaults={'ativa': True},
        )
        self.client.force_login(self.user)
        url_esperada = f'{reverse("financeiro:painel_financeiro")}?igreja_filtro={self.igreja_a.pk}'

        response = self.client.get(self.url)

        self.assertContains(response, f'href="{url_esperada}"')

    def test_autorizacao_em_uma_igreja_nao_cria_atalho_para_outra(self):
        grupo_pastor, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        self.user.groups.add(grupo_pastor)
        self._vincular()
        # Registro inconsistente simula dado legado; a pagina ainda deve negar o atalho fora do escopo.
        self._vincular(departamento=self.departamento_b)
        for departamento in (self.departamento_a, self.departamento_b):
            DepartamentoCapacidade.objects.update_or_create(
                departamento=departamento,
                capacidade=DepartamentoCapacidade.AGENDA,
                defaults={'ativa': True},
            )
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        itens = response.context['departamentos_itens']
        atalhos_por_igreja = {
            item['vinculo'].departamento.igreja_id: [atalho['rotulo'] for atalho in item['atalhos']]
            for item in itens
        }
        self.assertIn('Agenda', atalhos_por_igreja[self.igreja_a.pk])
        self.assertNotIn('Agenda', atalhos_por_igreja[self.igreja_b.pk])

    def test_pagina_readonly_nao_altera_vinculos_grupos_ou_membrocargo(self):
        vinculo = self._vincular()
        grupos_antes = set(self.user.groups.values_list('pk', flat=True))
        membro_cargo_antes = MembroCargo.objects.count()
        estado_antes = list(DepartamentoVinculo.objects.values_list('pk', 'data_inicio', 'data_fim'))
        self.client.force_login(self.user)

        get_response = self.client.get(self.url)
        post_response = self.client.post(self.url, {'vinculo_id': vinculo.pk, 'data_fim': '2026-08-28'})

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(post_response.status_code, 405)
        self.assertEqual(set(self.user.groups.values_list('pk', flat=True)), grupos_antes)
        self.assertEqual(MembroCargo.objects.count(), membro_cargo_antes)
        self.assertEqual(
            list(DepartamentoVinculo.objects.values_list('pk', 'data_inicio', 'data_fim')),
            estado_antes,
        )

    def test_quantidade_de_queries_nao_cresce_por_departamento(self):
        grupo_pastor, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        self.user.groups.add(grupo_pastor)
        self._vincular()
        self.client.force_login(self.user)
        with CaptureQueriesContext(connection) as contexto_um:
            self.client.get(self.url)

        for indice in range(5):
            departamento = Departamento.objects.create(
                igreja=self.igreja_a,
                codigo_interno=f'PESSOAL_{indice}',
                nome_exibicao=f'Departamento Pessoal {indice}',
                ativo=True,
            )
            self._vincular(departamento=departamento)
            DepartamentoCapacidade.objects.create(
                departamento=departamento,
                capacidade=DepartamentoCapacidade.AGENDA,
                ativa=True,
            )

        with CaptureQueriesContext(connection) as contexto_seis:
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(contexto_seis), len(contexto_um) + 2)

    def test_view_isolada_usa_escopo_operacional_local_e_mantem_orcamento_de_queries(self):
        grupo_pastor, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        self.user.groups.add(grupo_pastor)
        self._vincular()
        DepartamentoCapacidade.objects.update_or_create(
            departamento=self.departamento_a,
            capacidade=DepartamentoCapacidade.FINANCEIRO,
            defaults={'ativa': True},
        )
        usuario_request = get_user_model().objects.get(pk=self.user.pk)
        request = RequestFactory().get(self.url)
        request.user = usuario_request
        SessionMiddleware(lambda req: None).process_request(request)
        request.igreja_ativa = self.igreja_a

        with patch('configuracao.views.get_igrejas_selecionaveis') as seletor_generico:
            with patch('configuracao.views.render', return_value=HttpResponse()):
                with CaptureQueriesContext(connection) as queries:
                    response = meus_departamentos(request)

        self.assertEqual(response.status_code, 200)
        seletor_generico.assert_not_called()
        # Escopo local, policy financeira e entitlement real mantêm custo
        # constante por request, sem N+1 por vínculo departamental.
        self.assertLessEqual(len(queries), 16)

    def test_igreja_subordinada_nao_explicitamente_permitida_exibe_vinculo_sem_atalhos(self):
        self._vincular()
        regional = Igreja.objects.create(
            ministerio=self.ministerio_a,
            nome_igreja='Regional Sem Escopo Explicito',
            tipo_igreja='regional',
            igreja_superior=self.igreja_a,
        )
        congregacao = Igreja.objects.create(
            ministerio=self.ministerio_a,
            nome_igreja='Congregacao Subordinada Sem Escopo Explicito',
            tipo_igreja='congregacao',
            igreja_superior=regional,
        )
        departamento_congregacao = Departamento.objects.get(
            igreja=congregacao,
            codigo_interno='MISSOES',
        )
        self._vincular(departamento=departamento_congregacao)
        DepartamentoCapacidade.objects.update_or_create(
            departamento=departamento_congregacao,
            capacidade=DepartamentoCapacidade.AGENDA,
            defaults={'ativa': True},
        )
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        itens_por_igreja = {
            item['vinculo'].departamento.igreja_id: item
            for item in response.context['departamentos_itens']
        }
        self.assertIn(congregacao.pk, itens_por_igreja)
        self.assertEqual(itens_por_igreja[congregacao.pk]['atalhos'], [])

    def test_pastor_local_com_regional_explicita_recebe_atalho_sem_expandir_congregacao(self):
        grupo_pastor, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        self.user.groups.add(grupo_pastor)
        regional = Igreja.objects.create(
            ministerio=self.ministerio_a,
            nome_igreja='Regional Explicita',
            tipo_igreja='regional',
        )
        congregacao = Igreja.objects.create(
            ministerio=self.ministerio_a,
            nome_igreja='Congregacao Subordinada',
            tipo_igreja='congregacao',
            igreja_superior=regional,
        )
        self.perfil.igrejas_permitidas.add(regional)
        departamento_regional = Departamento.objects.get(igreja=regional, codigo_interno='MISSOES')
        departamento_congregacao = Departamento.objects.get(igreja=congregacao, codigo_interno='MISSOES')
        self._vincular(departamento=departamento_regional)
        self._vincular(departamento=departamento_congregacao)
        for departamento in (departamento_regional, departamento_congregacao):
            DepartamentoCapacidade.objects.update_or_create(
                departamento=departamento,
                capacidade=DepartamentoCapacidade.AGENDA,
                defaults={'ativa': True},
            )

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        atalhos_por_igreja = {
            item['vinculo'].departamento.igreja_id: [atalho['rotulo'] for atalho in item['atalhos']]
            for item in response.context['departamentos_itens']
        }
        self.assertIn('Agenda', atalhos_por_igreja[regional.pk])
        self.assertNotIn('Agenda', atalhos_por_igreja[congregacao.pk])

    def test_admin_tem_atalhos_apenas_em_sede_independente_ou_escopo_local_explicito(self):
        admin = get_user_model().objects.create_user(username='admin-operacional-meus-deps')
        perfil_admin = PerfilUsuario.objects.create(user=admin, ministerio=self.ministerio_a)
        grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        grupo_pastor, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        admin.groups.add(grupo_admin)
        tipo = TipoPessoa.objects.create(nome='Membro Admin Meus Departamentos')
        status = StatusPessoa.objects.create(nome='Ativo Admin Meus Departamentos')
        sede = Igreja.objects.create(
            ministerio=self.ministerio_a,
            nome_igreja='Sede Operacional',
            tipo_igreja='sede',
        )
        independente = Igreja.objects.create(
            ministerio=self.ministerio_a,
            nome_igreja='Independente Operacional',
            tipo_igreja='independente',
        )
        regional = Igreja.objects.create(
            ministerio=self.ministerio_a,
            nome_igreja='Regional Admin',
            tipo_igreja='regional',
        )
        congregacao = Igreja.objects.create(
            ministerio=self.ministerio_a,
            nome_igreja='Congregacao Admin',
            tipo_igreja='congregacao',
            igreja_superior=regional,
        )
        pessoa_admin = Pessoa.objects.create(
            usuario=admin,
            igreja=sede,
            nome='Pessoa Admin Operacional',
            tipo_pessoa=tipo,
            status_pessoa=status,
        )
        departamentos = [
            Departamento.objects.get(igreja=igreja, codigo_interno='MISSOES')
            for igreja in (sede, independente, regional, congregacao)
        ]
        for departamento in departamentos:
            DepartamentoVinculo.objects.create(
                membro=pessoa_admin,
                departamento=departamento,
                criado_por=admin,
            )
            DepartamentoCapacidade.objects.update_or_create(
                departamento=departamento,
                capacidade=DepartamentoCapacidade.FINANCEIRO,
                defaults={'ativa': True},
            )

        self.client.force_login(admin)
        with patch('configuracao.views.user_can_access_page', return_value=True):
            response = self.client.get(self.url)

        atalhos_por_igreja = {
            item['vinculo'].departamento.igreja_id: [atalho['rotulo'] for atalho in item['atalhos']]
            for item in response.context['departamentos_itens']
        }
        self.assertIn('Financeiro', atalhos_por_igreja[sede.pk])
        self.assertIn('Financeiro', atalhos_por_igreja[independente.pk])
        self.assertNotIn('Financeiro', atalhos_por_igreja[regional.pk])
        self.assertNotIn('Financeiro', atalhos_por_igreja[congregacao.pk])

        admin.groups.add(grupo_pastor)
        perfil_admin.igrejas_permitidas.add(congregacao)
        response = self.client.get(self.url)
        atalhos_por_igreja = {
            item['vinculo'].departamento.igreja_id: [atalho['rotulo'] for atalho in item['atalhos']]
            for item in response.context['departamentos_itens']
        }
        self.assertIn('Financeiro', atalhos_por_igreja[congregacao.pk])

    def test_autorizacao_equivalente_e_avaliada_uma_vez_por_igreja(self):
        self._vincular()
        outro_departamento = Departamento.objects.create(
            igreja=self.igreja_a,
            codigo_interno='OUTRO_AGENDA',
            nome_exibicao='Outro Departamento Agenda',
            ativo=True,
        )
        self._vincular(departamento=outro_departamento)
        for departamento in (self.departamento_a, outro_departamento):
            DepartamentoCapacidade.objects.update_or_create(
                departamento=departamento,
                capacidade=DepartamentoCapacidade.AGENDA,
                defaults={'ativa': True},
            )
        request = RequestFactory().get(self.url)
        request.user = get_user_model().objects.get(pk=self.user.pk)
        SessionMiddleware(lambda req: None).process_request(request)
        request.igreja_ativa = self.igreja_a
        request.igrejas_permitidas = Igreja.objects.filter(pk=self.igreja_a.pk)

        with patch('configuracao.views.user_can_access_page', return_value=True) as autorizar:
            with patch('configuracao.views.render', return_value=HttpResponse()):
                response = meus_departamentos(request)

        self.assertEqual(response.status_code, 200)
        autorizar.assert_called_once_with(
            request.user,
            'agenda',
            request=request,
            igreja=self.igreja_a,
        )
