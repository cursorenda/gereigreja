"""
Testes de integração para fluxo WAHA WhatsApp.
Executa: manage.py test comunicacao.tests.test_waha_integration --settings=core.settings_test -v 1
"""
import os
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError

from django.test import TestCase
from django.contrib.auth.models import User

from configuracao.models import Ministerio, Igreja
from secretaria.models import Pessoa
from comunicacao.models import WhatsAppConfiguracao, WhatsAppMensagemLog
from comunicacao.services_whatsapp import (
    send_whatsapp_text,
    get_waha_session_status,
    get_waha_qr_code,
    WhatsAppSendError,
    normalize_phone_to_chat_id,
    _resolve_chat_id_for_send,
)


class WhatsAppIntegrationTest(TestCase):
    """Testes de integração com WAHA."""

    def setUp(self):
        """Criar fixtures de teste."""
        # Criar usuário administrador
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123'
        )
        
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Teste Ministerio',
            administrador_principal=self.admin,
        )
        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja Teste',
        )
        self.config = WhatsAppConfiguracao.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            ativo=True,
            numero_envio='5533988507660',
            remetente_nome='Teste',
            session_name='test-session',
        )

    def test_normalize_phone_to_chat_id(self):
        """Testar normalização de telefone."""
        # Telefone com DDD
        phone, chat_id = normalize_phone_to_chat_id('(33) 98850-7660')
        self.assertEqual(phone, '5533988507660')
        self.assertIn('@c.us', chat_id)

        # Telefone vazio
        phone, chat_id = normalize_phone_to_chat_id('')
        self.assertIsNone(phone)
        self.assertIsNone(chat_id)

        # Telefone sem country code
        phone, chat_id = normalize_phone_to_chat_id('33988507660')
        self.assertEqual(phone, '5533988507660')
        self.assertIn('@c.us', chat_id)

    @patch('comunicacao.services_whatsapp.requests.get')
    def test_resolve_chat_id_for_send_valid_number(self, mock_get):
        """Testar resolução de chatId para número válido."""
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {'numberExists': True, 'chatId': '279825742827600@lid'},
        )

        chat_id, error = _resolve_chat_id_for_send(
            'https://test.waha.app',
            {'X-Api-Key': 'test-key'},
            'test-session',
            '5533988507660',
        )

        self.assertEqual(chat_id, '279825742827600@lid')
        self.assertIsNone(error)
        mock_get.assert_called_once()

    @patch('comunicacao.services_whatsapp.requests.get')
    def test_resolve_chat_id_for_send_invalid_number(self, mock_get):
        """Testar resolução de chatId para número inválido."""
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {'numberExists': False},
        )

        chat_id, error = _resolve_chat_id_for_send(
            'https://test.waha.app',
            {'X-Api-Key': 'test-key'},
            'test-session',
            '5533988507660',
        )

        self.assertIsNone(chat_id)
        self.assertIn('sem conta WhatsApp', error)

    @patch('comunicacao.services_whatsapp.requests.post')
    @patch('comunicacao.services_whatsapp.requests.get')
    def test_send_whatsapp_text_success(self, mock_get, mock_post):
        """Testar envio bem-sucedido."""
        # Mock check-exists
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {'numberExists': True, 'chatId': '279825742827600@lid'},
        )
        # Mock sendText
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {'ok': True},
            content=b'{"ok": true}',
        )

        result = send_whatsapp_text(
            self.config,
            '5533988507660',
            'Teste mensagem',
            tipo='manual',
            ministerio=self.ministerio,
            igreja=self.igreja,
        )

        self.assertEqual(result['ok'], True)

        # Verificar que log foi criado como sucesso
        log = WhatsAppMensagemLog.objects.filter(
            status='sucesso',
        ).last()
        self.assertIsNotNone(log)

    @patch('comunicacao.services_whatsapp.requests.get')
    def test_get_waha_session_status_working(self, mock_get):
        """Testar status da sessão WORKING."""
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {'status': 'WORKING'},
        )

        status = get_waha_session_status(self.config)
        self.assertEqual(status, 'WORKING')

    @patch('comunicacao.services_whatsapp.requests.get')
    def test_get_waha_session_status_stopped(self, mock_get):
        """Testar status da sessão STOPPED (404)."""
        mock_get.return_value = MagicMock(status_code=404)

        status = get_waha_session_status(self.config)
        self.assertEqual(status, 'STOPPED')

    @patch('comunicacao.services_whatsapp.requests.post')
    @patch('comunicacao.services_whatsapp.requests.get')
    def test_get_waha_qr_code_recovery_from_failed(self, mock_get, mock_post):
        """Testar recuperação automática de sessão FAILED."""
        # Primeira chamada: status FAILED
        # Chamadas POST: stop/start
        # Segunda chamada GET: retorna imagem
        call_count = [0]

        def get_side_effect(*args, **kwargs):
            call_count[0] += 1
            if '/sessions/' in args[0] and 'auth/qr' not in args[0]:
                # GET /api/sessions/...
                if call_count[0] == 1:
                    return MagicMock(
                        status_code=200,
                        json=lambda: {'status': 'FAILED'},
                    )
            # GET /api/.../auth/qr
            return MagicMock(
                status_code=200,
                content=b'fake-png-data',
                headers={'content-type': 'image/png'},
            )

        mock_get.side_effect = get_side_effect
        mock_post.return_value = MagicMock(status_code=201)

        qr = get_waha_qr_code(self.config)
        self.assertIsNotNone(qr)
        self.assertIn('data:image/png', qr)
