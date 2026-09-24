"""Regressões de autorização backend para a raiz da Secretaria."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from contas.constants import (
    ADMIN_MINISTERIO,
    MEMBRO_COMUM,
    PASTOR_LOCAL,
    SECRETARIO_LOCAL,
    TESOUREIRO,
)
from configuracao.models import (
    AssinaturaMinisterio,
    Departamento,
    DepartamentoVinculo,
    Igreja,
    Ministerio,
    PerfilUsuario,
)
from secretaria.models import Pessoa, StatusPessoa, TipoPessoa


User = get_user_model()


class SecretariaRootAuthorizationTests(TestCase):
    def setUp(self):
        self.groups = {
            name: Group.objects.get_or_create(name=name)[0]
            for name in (
                ADMIN_MINISTERIO,
                MEMBRO_COMUM,
                PASTOR_LOCAL,
                SECRETARIO_LOCAL,
                TESOUREIRO,
            )
        }
        self.owner = User.objects.create_user(username='owner-secretaria-root')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Secretaria Root',
            administrador_principal=self.owner,
            ativo=True,
        )
        AssinaturaMinisterio.objects.get_or_create(
            ministerio=self.ministerio,
            defaults={
                'data_inicio': timezone.now(),
                'data_fim': timezone.now() + timedelta(days=3650),
                'status': 'gratuita',
            },
        )
        self.sede = Igreja.objects.create(
            ministerio=self.ministerio, nome_igreja='Sede Root', tipo_igreja='sede'
        )
        self.independente = Igreja.objects.create(
            ministerio=self.ministerio, nome_igreja='Independente Root', tipo_igreja='independente'
        )
        self.regional = Igreja.objects.create(
            ministerio=self.ministerio, nome_igreja='Regional Root', tipo_igreja='regional'
        )
        self.congregacao = Igreja.objects.create(
            ministerio=self.ministerio, nome_igreja='Congregacao Root', tipo_igreja='congregacao'
        )
        self.url_secretaria = reverse('secretaria:index')
        self.url_pessoas = reverse('secretaria:lista_pessoas')

    def _user(self, username, *groups, churches=()):
        user = User.objects.create_user(username=username, password='senha123')
        user.groups.add(*(self.groups[group] for group in groups))
        perfil = PerfilUsuario.objects.create(user=user, ministerio=self.ministerio)
        perfil.igrejas_permitidas.set(churches)
        return user

    def _get_secretaria(self, user, igreja=None):
        self.client.force_login(user)
        session = self.client.session
        if igreja is None:
            session.pop('igreja_ativa_id', None)
        else:
            session['igreja_ativa_id'] = igreja.pk
        session.save()
        return self.client.get(self.url_secretaria)

    def test_tesoureiro_e_multifuncao_departamental_nao_acessam_secretaria(self):
        tesoureiro = self._user('tesoureiro-secretaria-root', TESOUREIRO, churches=[self.sede])
        self.assertEqual(self._get_secretaria(tesoureiro, self.sede).status_code, 403)
        self.assertEqual(self.client.get(self.url_pessoas).status_code, 403)

        multi = self._user('multi-secretaria-root', TESOUREIRO, churches=[self.sede])
        tipo = TipoPessoa.objects.create(nome='Membro Multi Secretaria Root')
        status = StatusPessoa.objects.create(nome='Ativo Multi Secretaria Root')
        pessoa = Pessoa.objects.create(
            usuario=multi,
            igreja=self.sede,
            nome='Pessoa Multi Secretaria Root',
            tipo_pessoa=tipo,
            status_pessoa=status,
        )
        departamento = Departamento.objects.get(igreja=self.sede, codigo_interno='MISSOES')
        DepartamentoVinculo.objects.create(departamento=departamento, membro=pessoa, criado_por=self.owner)
        self.assertEqual(self._get_secretaria(multi, self.sede).status_code, 403)

    def test_pastor_e_secretario_locais_vinculados_acessam_secretaria(self):
        pastor = self._user('pastor-secretaria-root', PASTOR_LOCAL, churches=[self.sede])
        secretario = self._user('secretario-secretaria-root', SECRETARIO_LOCAL, churches=[self.independente])

        self.assertEqual(self._get_secretaria(pastor, self.sede).status_code, 200)
        self.assertEqual(self._get_secretaria(secretario, self.independente).status_code, 200)

    def test_admin_tem_acesso_somente_em_sede_ou_independente_com_contexto(self):
        admin = self._user(
            'admin-secretaria-root',
            ADMIN_MINISTERIO,
            churches=[self.sede, self.independente, self.regional, self.congregacao],
        )

        self.assertEqual(self._get_secretaria(admin, self.sede).status_code, 200)
        self.assertEqual(self._get_secretaria(admin, self.independente).status_code, 200)
        self.assertEqual(self._get_secretaria(admin, self.regional).status_code, 403)
        self.assertEqual(self._get_secretaria(admin, self.congregacao).status_code, 403)
        self.assertEqual(self._get_secretaria(admin).status_code, 403)

    def test_membro_e_departamento_vinculo_sem_papel_operacional_nao_ganham_secretaria(self):
        membro = self._user('membro-secretaria-root', MEMBRO_COMUM, churches=[self.sede])
        response = self._get_secretaria(membro, self.sede)
        self.assertRedirects(response, reverse('secretaria:portal_membro'), fetch_redirect_response=False)

        departamento_vinculo = self._user('departamento-secretaria-root', churches=[self.sede])
        tipo = TipoPessoa.objects.create(nome='Membro Departamento Secretaria Root')
        status = StatusPessoa.objects.create(nome='Ativo Departamento Secretaria Root')
        pessoa = Pessoa.objects.create(
            usuario=departamento_vinculo,
            igreja=self.sede,
            nome='Pessoa Departamento Secretaria Root',
            tipo_pessoa=tipo,
            status_pessoa=status,
        )
        departamento = Departamento.objects.get(igreja=self.sede, codigo_interno='MISSOES')
        DepartamentoVinculo.objects.create(departamento=departamento, membro=pessoa, criado_por=self.owner)
        response = self._get_secretaria(departamento_vinculo, self.sede)
        self.assertRedirects(response, reverse('contas:aguardando_acesso'), fetch_redirect_response=False)

    def test_membro_com_papel_local_autorizado_nao_e_redirecionado_para_portal(self):
        pastor = self._user(
            'membro-pastor-secretaria-root',
            MEMBRO_COMUM,
            PASTOR_LOCAL,
            churches=[self.sede],
        )
        secretario = self._user(
            'membro-secretario-secretaria-root',
            MEMBRO_COMUM,
            SECRETARIO_LOCAL,
            churches=[self.sede],
        )
        admin = self._user(
            'membro-admin-secretaria-root',
            MEMBRO_COMUM,
            ADMIN_MINISTERIO,
            churches=[self.sede],
        )

        for user in (pastor, secretario, admin):
            response = self._get_secretaria(user, self.sede)
            self.assertEqual(response.status_code, 200)
            self.assertNotEqual(response.get('Location'), reverse('secretaria:portal_membro'))