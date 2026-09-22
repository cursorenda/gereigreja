"""
Testes para as views do demo, com foco no tratamento de excecoes
de provisionamento em _authenticate_demo_user() e na landing page
pos-login definida por _demo_redirect_home().
"""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from contas.constants import (
    ADMIN_MINISTERIO,
    LIDERANCA_FINANCEIRA,
    LIDERANCA_SECRETARIA,
    MEMBRO_COMUM,
    PASTOR_LOCAL,
    TESOUREIRO,
)
from demo.views import _authenticate_demo_user, _demo_redirect_home


User = get_user_model()


class AuthenticateDemoUserTests(TestCase):
    """Testa _authenticate_demo_user() diretamente."""

    def _make_request(self):
        from django.test import RequestFactory
        return RequestFactory().post('/demo/login/')

    def test_usuario_demo_existente_autentica_sem_provisionamento(self):
        """Usuario demo que ja existe autentica sem chamar popular_demo."""
        User.objects.create_user(username='demo_admin', password='demo123')
        request = self._make_request()

        with patch('demo.views.call_command') as mock_call:
            user = _authenticate_demo_user(request, 'demo_admin')

        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'demo_admin')
        mock_call.assert_not_called()

    def test_provisionamento_falha_logga_excecao(self):
        """Quando popular_demo levanta excecao, ela deve ser loggada."""
        request = self._make_request()

        with patch(
            'demo.views.call_command',
            side_effect=Exception('erro interno simulado'),
        ), self.assertLogs('demo.views', level='ERROR') as log_ctx:
            result = _authenticate_demo_user(request, 'demo_admin')

        self.assertIsNone(result)
        log_output = '\n'.join(log_ctx.output)
        self.assertIn('demo_admin', log_output)
        self.assertIn('provisionar dados demo', log_output)
        self.assertIn('Exception', log_output)

    def test_provisionamento_falha_retorna_none(self):
        """Falha no provisionamento retorna None (usuario inexistente)."""
        request = self._make_request()

        with patch(
            'demo.views.call_command',
            side_effect=RuntimeError('falha no provisionamento'),
        ):
            result = _authenticate_demo_user(request, 'demo_membro')

        self.assertIsNone(result)

    def test_usuario_nao_demo_retorna_none_sem_provisionar(self):
        """Usuario que nao comeca com demo_ retorna None sem provisionar."""
        request = self._make_request()

        with patch('demo.views.call_command') as mock_call:
            result = _authenticate_demo_user(request, 'usuario_qualquer')

        self.assertIsNone(result)
        mock_call.assert_not_called()

    def test_provisionamento_executado_no_maximo_uma_vez(self):
        """O provisionamento e executado no maximo uma vez (sem loop)."""
        request = self._make_request()

        with patch(
            'demo.views.call_command',
            side_effect=Exception('falha persistente'),
        ) as mock_call:
            _authenticate_demo_user(request, 'demo_admin')

        self.assertEqual(mock_call.call_count, 1)

    def test_provisionamento_sucesso_autentica_apos_repopulacao(self):
        """Quando provisionamento sucede, autentica o usuario apos repopular."""
        request = self._make_request()

        def fake_provision(*args, **kwargs):
            User.objects.create_user(username='demo_novo', password='demo123')

        with patch('demo.views.call_command', side_effect=fake_provision):
            user = _authenticate_demo_user(request, 'demo_novo')

        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'demo_novo')


class DemoLoginViewTests(TestCase):
    """Testa demo_login_view() end-to-end via cliente de teste."""

    def setUp(self):
        self.login_url = reverse('demo:demo_login')

    def test_usuario_demo_existente_faz_login(self):
        """Usuario demo existente seleciona perfil e faz login com sucesso."""
        User.objects.create_user(username='demo_admin', password='demo123')

        response = self.client.post(self.login_url, {'perfil': 'Administrador'})

        # Login bem-sucedido redireciona (302)
        self.assertEqual(response.status_code, 302)
        # Usuario esta autenticado
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_provisionamento_falha_responde_mensagem_controlada(self):
        """Falha no provisionamento exibe mensagem generica sem traceback."""
        # Mocka call_command para simular falha no provisionamento
        with patch(
            'demo.views.call_command',
            side_effect=Exception('erro interno simulado'),
        ):
            response = self.client.post(self.login_url, {'perfil': 'Membro'})

        # Nao autenticado -> renderiza a pagina de login novamente (200)
        self.assertEqual(response.status_code, 200)

        # Mensagem de erro controlada aparece (via storage de messages)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages_list) > 0)
        self.assertIn('não encontrado', str(messages_list[0]).lower())

        # Nao expoe detalhes tecnicos no HTML
        content = response.content.decode('utf-8')
        self.assertNotIn('Traceback', content)
        self.assertNotIn('Exception', content)
        self.assertNotIn('erro interno', content)
        self.assertNotIn('popular_demo', content)

    def test_provisionamento_falha_nao_expoe_credenciais(self):
        """Falha no provisionamento nao expoe senhas ou caminhos internos."""
        with patch(
            'demo.views.call_command',
            side_effect=Exception('falha simulada'),
        ):
            response = self.client.post(self.login_url, {'perfil': 'Administrador'})

        content = response.content.decode('utf-8')
        # Senha demo nunca deve aparecer no HTML
        self.assertNotIn('demo123', content)
        # Nenhum caminho de arquivo ou stack trace
        self.assertNotIn('File "', content)
        self.assertNotIn('.py", line', content)

    def test_perfil_invalido_redireciona_com_erro(self):
        """Perfil invalido redireciona com mensagem de erro."""
        response = self.client.post(self.login_url, {'perfil': 'Perfil Inexistente'})

        # Redireciona para a pagina de login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.login_url)

    def test_get_rendera_formulario(self):
        """GET renderiza o formulario de selecao de perfil."""
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Entrar como demonstração', content)


class DemoRedirectHomeTests(TestCase):
    """Testa o redirecionamento pos-login definido por _demo_redirect_home()."""

    def setUp(self):
        from django.test import RequestFactory

        self.factory = RequestFactory()
        self._criar_grupos()

    def _criar_grupos(self):
        """Cria os grupos Django usados nos testes."""
        for nome in (
            ADMIN_MINISTERIO,
            LIDERANCA_FINANCEIRA,
            LIDERANCA_SECRETARIA,
            PASTOR_LOCAL,
            TESOUREIRO,
            MEMBRO_COMUM,
        ):
            Group.objects.get_or_create(name=nome)

    def _criar_usuario(self, username, grupo):
        user = User.objects.create_user(username=username, password='demo123')
        user.groups.add(Group.objects.get(name=grupo))
        return user

    def test_admin_ministerio_vai_para_centro_ministerial(self):
        """Admin Ministerio deve cair no Centro Ministerial, nao no portal do membro."""
        user = self._criar_usuario('demo_admin', ADMIN_MINISTERIO)
        request = self.factory.get('/')
        request.user = user

        response = _demo_redirect_home(request, user)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('configuracao:centro_ministerial'))

    def test_membro_comum_vai_para_portal(self):
        """Membro Comum deve continuar caindo no portal do membro."""
        user = self._criar_usuario('demo_membro', MEMBRO_COMUM)
        request = self.factory.get('/')
        request.user = user

        response = _demo_redirect_home(request, user)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('secretaria:portal_membro'))

    def test_lideranca_financeira_preserva_destino(self):
        """Lideranca Financeira deve continuar indo para painel_lideranca_financeiro."""
        user = self._criar_usuario('demo_fin', LIDERANCA_FINANCEIRA)
        request = self.factory.get('/')
        request.user = user

        response = _demo_redirect_home(request, user)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('financeiro:painel_lideranca_financeiro'))

    def test_lideranca_secretaria_preserva_destino(self):
        """Lideranca Secretaria deve continuar indo para painel_lideranca_secretaria."""
        user = self._criar_usuario('demo_sec', LIDERANCA_SECRETARIA)
        request = self.factory.get('/')
        request.user = user

        response = _demo_redirect_home(request, user)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('secretaria:painel_lideranca_secretaria'))
