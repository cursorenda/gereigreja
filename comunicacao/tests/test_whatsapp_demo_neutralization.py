"""
Testes de neutralizacao de WhatsApp para tenant de demonstracao.

Comprova que:
- Tenant Demo NAO chama WAHA/requests/API externa
- Tenant Demo registra log com status='neutralizado_demo'
- Tenant Demo NAO e contado como entrega externa real
- Tenant real preserva comportamento existente
- Nenhum bloqueio depende de username demo_*
"""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from configuracao.models import Igreja, Ministerio
from comunicacao.models import WhatsAppConfiguracao, WhatsAppMensagemLog
from comunicacao.services_whatsapp import WhatsAppSendError, send_whatsapp_text

User = get_user_model()


class WhatsAppDemoNeutralizationTests(TestCase):
    """Testa que o tenant Demo neutraliza envios WhatsApp sem chamada externa."""

    def _create_ministerio(
        self,
        is_demo=False,
        nome='Ministerio Teste',
        cnpj='11.222.333/0001-44',
    ):
        """Cria ministerio com igreja e configuracao WhatsApp."""
        admin, _ = User.objects.get_or_create(
            username='admin_test_wa',
            defaults={'email': 'admin_wa@test.com', 'is_staff': True}
        )
        ministerio = Ministerio.objects.create(
            nome_fantasia=nome,
            cnpj=cnpj,
            ativo=True,
            is_demo=is_demo,
            administrador_principal=admin,
        )
        igreja = Igreja.objects.create(
            ministerio=ministerio,
            nome_igreja='Igreja Teste',
            tipo_igreja='sede',
        )
        config = WhatsAppConfiguracao.objects.create(
            ministerio=ministerio,
            igreja=igreja,
            ativo=True,
            numero_envio='5533988507660',
            remetente_nome='Teste',
        )
        return ministerio, igreja, config

    def test_tem_demo_nao_faz_chamada_externa(self):
        """Tenant Demo NAO deve chamar requests.post()."""
        ministerio, igreja, config = self._create_ministerio(is_demo=True)

        with patch('comunicacao.services_whatsapp.requests.post') as mock_post:
            send_whatsapp_text(config, '5533988507660', 'Mensagem teste')

        mock_post.assert_not_called()

    def test_demo_cria_log_neutralizado_demo(self):
        """Tenant Demo deve criar WhatsAppMensagemLog com status='neutralizado_demo'."""
        ministerio, igreja, config = self._create_ministerio(is_demo=True)

        send_whatsapp_text(config, '5533988507660', 'Mensagem teste')

        log = WhatsAppMensagemLog.objects.filter(ministerio=ministerio).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, 'neutralizado_demo')
        self.assertIn('demonstração', log.erro)

    def test_demo_retorna_contrato_compativel_sucesso(self):
        """Tenant Demo deve retornar dict compativel com sucesso."""
        ministerio, igreja, config = self._create_ministerio(is_demo=True)

        result = send_whatsapp_text(config, '5533988507660', 'Mensagem teste')

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('ok'))
        self.assertTrue(result.get('demo'))


    def test_demo_nao_contado_como_entrega_real(self):
        """neutralizado_demo NAO deve ser contado como entrega real (status='sucesso')."""
        ministerio, igreja, config = self._create_ministerio(is_demo=True)

        # Cria 2 envios demo neutralizados
        send_whatsapp_text(config, '5533988507660', 'Msg 1')
        send_whatsapp_text(config, '5533988507661', 'Msg 2')

        # Nao deve haver nenhum log com status='sucesso'
        sucesso_count = WhatsAppMensagemLog.objects.filter(
            ministerio=ministerio, status='sucesso'
        ).count()
        self.assertEqual(sucesso_count, 0)

        # Deve haver 2 logs neutralizados
        neutralizado_count = WhatsAppMensagemLog.objects.filter(
            ministerio=ministerio, status='neutralizado_demo'
        ).count()
        self.assertEqual(neutralizado_count, 2)

    def test_tenant_real_preserva_comportamento(self):
        """Tenant real (is_demo=False) deve tentar enviar normalmente."""
        ministerio, igreja, config = self._create_ministerio(is_demo=False)

        with patch('comunicacao.services_whatsapp.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.content = b'{"ok": true}'
            mock_post.return_value.json.return_value = {'ok': True}
            mock_post.return_value.raise_for_status = lambda: None

            send_whatsapp_text(config, '5533988507660', 'Mensagem teste')

        # Deve ter chamado requests.post
        mock_post.assert_called_once()

        # Deve ter criado log com status='sucesso'
        log = WhatsAppMensagemLog.objects.filter(ministerio=ministerio).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, 'sucesso')

    def test_neutralizacao_nao_depende_username(self):
        """A neutralizacao deve depender exclusivamente de is_demo, nao de username."""
        # Cria ministerio demo com nome diferente (nao "Demonstracao")
        ministerio, igreja, config = self._create_ministerio(
            is_demo=True, nome='Igreja Qualquer Nome'
        )

        with patch('comunicacao.services_whatsapp.requests.post') as mock_post:
            send_whatsapp_text(config, '5533988507660', 'Mensagem teste')

        # Mesmo com nome diferente, deve neutralizar
        mock_post.assert_not_called()
        log = WhatsAppMensagemLog.objects.filter(ministerio=ministerio).first()
        self.assertEqual(log.status, 'neutralizado_demo')

    def test_demo_com_ministerio_param_explicito(self):
        """Neutralizar tambem quando ministerio e passado explicitamente como param."""
        ministerio_demo, igreja_demo, config_demo = self._create_ministerio(
            is_demo=True,
            nome='Demo',
        )

        with (
            patch('comunicacao.services_whatsapp.requests.get') as mock_get,
            patch('comunicacao.services_whatsapp.requests.post') as mock_post,
        ):
            result = send_whatsapp_text(
                config_demo,
                '5533988507660',
                'Teste',
                ministerio=ministerio_demo,
                igreja=igreja_demo,
            )

        mock_get.assert_not_called()
        mock_post.assert_not_called()
        self.assertTrue(result.get('demo'))
        self.assertTrue(
            WhatsAppMensagemLog.objects.filter(
                ministerio=ministerio_demo,
                igreja=igreja_demo,
                configuracao=config_demo,
                status='neutralizado_demo',
            ).exists()
        )

    def test_ministerio_explicito_cross_tenant_e_bloqueado_antes_da_rede(self):
        """Configuracao real nao pode ser usada com Ministerio Demo de outro tenant."""
        ministerio_real, igreja_real, config_real = self._create_ministerio(
            is_demo=False,
            nome='Real A',
        )
        ministerio_demo, _, _ = self._create_ministerio(
            is_demo=True,
            nome='Demo B',
            cnpj='22.333.444/0001-55',
        )

        with (
            patch('comunicacao.services_whatsapp.requests.get') as mock_get,
            patch('comunicacao.services_whatsapp.requests.post') as mock_post,
        ):
            with self.assertRaises(WhatsAppSendError):
                send_whatsapp_text(
                    config_real,
                    '5533988507660',
                    'Teste cross-tenant',
                    ministerio=ministerio_demo,
                    igreja=igreja_real,
                )

        mock_get.assert_not_called()
        mock_post.assert_not_called()
        self.assertFalse(
            WhatsAppMensagemLog.objects.filter(
                ministerio=ministerio_real,
                igreja=igreja_real,
            ).exists()
        )
