"""Regressões HTTP do dispatcher de destino pós-login."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from contas.constants import ADMIN_MINISTERIO, MEMBRO_COMUM, PASTOR_LOCAL, SECRETARIO_LOCAL, TESOUREIRO
from configuracao.models import Departamento, DepartamentoVinculo, Igreja, Ministerio, PerfilUsuario
from secretaria.models import Pessoa, StatusPessoa, TipoPessoa


User = get_user_model()


class LoginRedirectPorPapelTests(TestCase):
    def setUp(self):
        self.groups = {
            name: Group.objects.get_or_create(name=name)[0]
            for name in (ADMIN_MINISTERIO, MEMBRO_COMUM, PASTOR_LOCAL, SECRETARIO_LOCAL, TESOUREIRO)
        }
        self.owner = User.objects.create_user(username='owner-login-redirect')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Login Redirect',
            administrador_principal=self.owner,
            ativo=True,
        )
        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja Login Redirect',
            tipo_igreja='sede',
        )
        self.login_url = reverse('login')

    def _user(self, username, *groups, churches=()):
        user = User.objects.create_user(username=username, password='senha123')
        user.groups.add(*(self.groups[group] for group in groups))
        perfil = PerfilUsuario.objects.create(user=user, ministerio=self.ministerio)
        perfil.igrejas_permitidas.set(churches)
        return user

    def _login(self, user):
        return self.client.post(
            self.login_url,
            {'username': user.username, 'password': 'senha123'},
        )

    def test_admin_ministerio_redireciona_para_centro_ministerial(self):
        admin = self._user('admin-login-redirect', ADMIN_MINISTERIO, churches=[self.igreja])

        self.assertRedirects(self._login(admin), reverse('configuracao:centro_ministerial'), fetch_redirect_response=False)

    def test_pastor_local_redireciona_para_secretaria(self):
        pastor = self._user('pastor-login-redirect', PASTOR_LOCAL, churches=[self.igreja])

        self.assertRedirects(self._login(pastor), reverse('secretaria:index'), fetch_redirect_response=False)

    def test_secretario_local_redireciona_para_secretaria(self):
        secretario = self._user('secretario-login-redirect', SECRETARIO_LOCAL, churches=[self.igreja])

        self.assertRedirects(self._login(secretario), reverse('secretaria:index'), fetch_redirect_response=False)

    def test_tesoureiro_redireciona_para_financeiro(self):
        tesoureiro = self._user('tesoureiro-login-redirect', TESOUREIRO, churches=[self.igreja])

        self.assertRedirects(self._login(tesoureiro), reverse('financeiro:painel_financeiro'), fetch_redirect_response=False)

    def test_membro_comum_redireciona_para_portal_do_membro(self):
        membro = self._user('membro-login-redirect', MEMBRO_COMUM, churches=[self.igreja])

        self.assertRedirects(self._login(membro), reverse('secretaria:portal_membro'), fetch_redirect_response=False)

    def test_membro_com_pastor_local_redireciona_para_secretaria(self):
        membro_pastor = self._user(
            'membro-pastor-login-redirect',
            MEMBRO_COMUM,
            PASTOR_LOCAL,
            churches=[self.igreja],
        )

        self.assertRedirects(self._login(membro_pastor), reverse('secretaria:index'), fetch_redirect_response=False)

    def test_membro_com_tesoureiro_redireciona_para_financeiro(self):
        membro_tesoureiro = self._user(
            'membro-tesoureiro-login-redirect',
            MEMBRO_COMUM,
            TESOUREIRO,
            churches=[self.igreja],
        )

        self.assertRedirects(self._login(membro_tesoureiro), reverse('financeiro:painel_financeiro'), fetch_redirect_response=False)

    def test_multifuncao_tesoureiro_com_departamento_redireciona_para_financeiro(self):
        multi = self._user('multi-login-redirect', TESOUREIRO, churches=[self.igreja])
        tipo = TipoPessoa.objects.create(nome='Membro Multi Login Redirect')
        status = StatusPessoa.objects.create(nome='Ativo Multi Login Redirect')
        pessoa = Pessoa.objects.create(
            usuario=multi,
            igreja=self.igreja,
            nome='Pessoa Multi Login Redirect',
            tipo_pessoa=tipo,
            status_pessoa=status,
        )
        departamento = Departamento.objects.get(igreja=self.igreja, codigo_interno='MISSOES')
        DepartamentoVinculo.objects.create(departamento=departamento, membro=pessoa, criado_por=self.owner)

        self.assertRedirects(self._login(multi), reverse('financeiro:painel_financeiro'), fetch_redirect_response=False)

    def test_superuser_tecnico_vai_para_destino_tecnico(self):
        superuser = User.objects.create_superuser(
            username='superuser-login-redirect',
            password='senha123',
            email='superuser@example.test',
        )
        PerfilUsuario.objects.create(user=superuser, ministerio=self.ministerio)

        self.assertRedirects(self._login(superuser), reverse('admin:index'), fetch_redirect_response=False)