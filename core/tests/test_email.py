"""Testes isolados para ``core.email_services``."""
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from configuracao.models import Ministerio
from core.email_services import StatusEnvioEmail, enviar_email_seguro


class EmailServicesTests(TestCase):
    def _criar_ministerio(self, *, nome='Ministerio Teste', is_demo=False, username=None):
        usuario = get_user_model().objects.create_user(
            username=username or f'admin_{nome.lower().replace(" ", "_")}',
            password='pass123',
        )
        return Ministerio.objects.create(
            nome_fantasia=nome,
            administrador_principal=usuario,
            ativo=True,
            is_demo=is_demo,
        )

    def _igreja_com_ministerio(self, ministerio):
        igreja = MagicMock()
        igreja.ministerio = ministerio
        return igreja

    def _membro_com_igreja(self, igreja):
        membro = MagicMock()
        membro.igreja = igreja
        return membro

    @patch('core.email_services.send_mail')
    def test_demo_retorna_resultado_neutralizado_sem_chamar_backend(self, mock_send):
        ministerio = self._criar_ministerio(is_demo=True)

        resultado = enviar_email_seguro(
            'Assunto Teste',
            'Corpo da mensagem',
            ['dest@test.com'],
            ministerio=ministerio,
        )

        self.assertEqual(resultado.status, StatusEnvioEmail.NEUTRALIZADO_DEMO)
        self.assertFalse(resultado.backend_chamado)
        self.assertIsNone(resultado.resultado_backend)
        mock_send.assert_not_called()

    @patch('core.email_services.send_mail')
    def test_tenant_real_retorno_um_indica_enviado(self, mock_send):
        ministerio = self._criar_ministerio()
        mock_send.return_value = 1

        resultado = enviar_email_seguro(
            'Assunto Teste',
            'Corpo da mensagem',
            ['dest@test.com'],
            ministerio=ministerio,
        )

        self.assertEqual(resultado.status, StatusEnvioEmail.ENVIADO)
        self.assertTrue(resultado.backend_chamado)
        self.assertEqual(resultado.resultado_backend, 1)
        mock_send.assert_called_once()

    @patch('core.email_services.send_mail')
    def test_tenant_real_retorno_zero_indica_nao_enviado(self, mock_send):
        ministerio = self._criar_ministerio()
        mock_send.return_value = 0

        resultado = enviar_email_seguro(
            'Assunto Teste',
            'Corpo da mensagem',
            ['dest@test.com'],
            ministerio=ministerio,
        )

        self.assertEqual(resultado.status, StatusEnvioEmail.NAO_ENVIADO)
        self.assertTrue(resultado.backend_chamado)
        self.assertEqual(resultado.resultado_backend, 0)
        mock_send.assert_called_once()

    @patch('core.email_services.send_mail')
    def test_propaga_excecao_do_backend_quando_fail_silently_false(self, mock_send):
        ministerio = self._criar_ministerio()
        mock_send.side_effect = RuntimeError('Falha de backend')

        with self.assertRaisesRegex(RuntimeError, 'Falha de backend'):
            enviar_email_seguro(
                'Assunto Teste',
                'Corpo da mensagem',
                ['dest@test.com'],
                ministerio=ministerio,
                fail_silently=False,
            )

    @patch('core.email_services.send_mail')
    def test_preserva_parametros_do_backend(self, mock_send):
        ministerio = self._criar_ministerio()
        mock_send.return_value = 1

        enviar_email_seguro(
            'Assunto',
            'Mensagem texto',
            ['dest1@test.com', 'dest2@test.com'],
            ministerio=ministerio,
            html_message='<p>Mensagem HTML</p>',
            from_email='remetente@test.com',
            fail_silently=True,
        )

        mock_send.assert_called_once_with(
            'Assunto',
            'Mensagem texto',
            'remetente@test.com',
            ['dest1@test.com', 'dest2@test.com'],
            html_message='<p>Mensagem HTML</p>',
            fail_silently=True,
        )

    @patch('core.email_services.send_mail')
    def test_resolve_contexto_por_ministerio(self, mock_send):
        ministerio = self._criar_ministerio()
        mock_send.return_value = 1

        resultado = enviar_email_seguro(
            'Assunto', 'Mensagem', ['dest@test.com'], ministerio=ministerio
        )

        self.assertEqual(resultado.status, StatusEnvioEmail.ENVIADO)
        mock_send.assert_called_once()

    @patch('core.email_services.send_mail')
    def test_resolve_contexto_por_igreja(self, mock_send):
        ministerio = self._criar_ministerio()
        mock_send.return_value = 1

        resultado = enviar_email_seguro(
            'Assunto',
            'Mensagem',
            ['dest@test.com'],
            igreja=self._igreja_com_ministerio(ministerio),
        )

        self.assertEqual(resultado.status, StatusEnvioEmail.ENVIADO)
        mock_send.assert_called_once()

    @patch('core.email_services.send_mail')
    def test_resolve_contexto_por_membro(self, mock_send):
        ministerio = self._criar_ministerio()
        mock_send.return_value = 1
        igreja = self._igreja_com_ministerio(ministerio)

        resultado = enviar_email_seguro(
            'Assunto',
            'Mensagem',
            ['dest@test.com'],
            membro=self._membro_com_igreja(igreja),
        )

        self.assertEqual(resultado.status, StatusEnvioEmail.ENVIADO)
        mock_send.assert_called_once()

    @patch('core.email_services.send_mail')
    def test_ausencia_de_contexto_falha_antes_do_backend(self, mock_send):
        with self.assertRaises(ValueError):
            enviar_email_seguro('Assunto', 'Mensagem', ['dest@test.com'])

        mock_send.assert_not_called()

    @patch('core.email_services.send_mail')
    def test_ministerio_sem_pk_falha_fechado_antes_do_backend(self, mock_send):
        ministerio = MagicMock()
        ministerio.pk = None

        with self.assertRaises(ValueError):
            enviar_email_seguro(
                'Assunto', 'Mensagem', ['dest@test.com'], ministerio=ministerio
            )

        mock_send.assert_not_called()

    @patch('core.email_services.send_mail')
    def test_contexto_cross_tenant_falha_fechado_antes_do_backend(self, mock_send):
        ministerio_a = self._criar_ministerio(nome='Ministerio A')
        ministerio_b = self._criar_ministerio(nome='Ministerio B')

        with self.assertRaises(ValueError):
            enviar_email_seguro(
                'Assunto',
                'Mensagem',
                ['dest@test.com'],
                ministerio=ministerio_a,
                igreja=self._igreja_com_ministerio(ministerio_b),
            )

        mock_send.assert_not_called()

    @patch('core.email_services.send_mail')
    def test_demo_depende_exclusivamente_de_is_demo(self, mock_send):
        ministerio = self._criar_ministerio(
            nome='Demonstracao',
            is_demo=False,
            username='admin_demo_nome',
        )
        mock_send.return_value = 1

        resultado = enviar_email_seguro(
            'Assunto', 'Mensagem', ['demo@test.com'], ministerio=ministerio
        )

        self.assertEqual(resultado.status, StatusEnvioEmail.ENVIADO)
        mock_send.assert_called_once()

    @patch('core.email_services.send_mail')
    @patch('core.email_services.logger')
    def test_log_demo_nao_contem_conteudo_sensivel(self, mock_logger, mock_send):
        ministerio = self._criar_ministerio(is_demo=True)

        enviar_email_seguro(
            'Assunto Secreto',
            'Corpo confidencial com token abc123',
            ['user@email.com'],
            ministerio=ministerio,
        )

        mock_send.assert_not_called()
        mock_logger.info.assert_called_once()
        mensagem_log = mock_logger.info.call_args.args[0]
        self.assertNotIn('Assunto Secreto', mensagem_log)
        self.assertNotIn('Corpo confidencial', mensagem_log)
        self.assertNotIn('token', mensagem_log)
        self.assertNotIn('abc123', mensagem_log)
        self.assertNotIn('user@email.com', mensagem_log)