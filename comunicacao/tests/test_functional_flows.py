from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from django.core.mail import BadHeaderError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from comunicacao.models import Aviso, WhatsAppConfiguracaoGlobal
from comunicacao.services import ResultadoEnvioEmailMassa
from configuracao.models import AssinaturaMinisterio, Ministerio, PerfilUsuario, Plano
from contas.constants import ADMIN_MINISTERIO
from core.email_services import ResultadoEnvioEmail, StatusEnvioEmail


class ComunicacaoFunctionalFlowsTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='admin_comunicacao',
            password='senha123',
        )
        self.admin_group, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        self.user.groups.add(self.admin_group)

        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Comunicacao Teste',
            administrador_principal=self.user,
            ativo=True,
        )
        PerfilUsuario.objects.create(user=self.user, ministerio=self.ministerio)

        self.plano = Plano.objects.create(
            nome='pioneiro',
            codigo_plano='plano_comunicacao_teste',
            preco_mensal=0,
            preco_anual=0,
            limite_membros=100,
            limite_igrejas=5,
            permite_modulo_secretaria=True,
            permite_modulo_agenda=True,
            permite_modulo_eventos=True,
            permite_modulo_escola_biblica=True,
            permite_modulo_financeiro=True,
            permite_modulo_comunicacao=True,
            permite_suporte_tickets=True,
            suporte_prioritario=False,
            ativo=True,
            is_visible=True,
            liberado_publicamente=True,
            contratacao_publica_liberada=True,
            ordem_liberacao=1,
            stripe_product_id='prod_comunicacao_teste',
        )
        AssinaturaMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=self.plano,
            data_inicio=timezone.now() - timedelta(days=1),
            data_fim=timezone.now() + timedelta(days=365),
            status='ativa',
            ciclo_pagamento='mensal',
        )

        self.client.force_login(self.user)

    def test_home_da_comunicacao_abre(self):
        response = self.client.get(reverse('comunicacao:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Comunicação')

    def test_criar_aviso_persiste_registro(self):
        response = self.client.post(
            reverse('comunicacao:criar_aviso'),
            data={
                'ministerio': self.ministerio.pk,
                'titulo': 'Aviso funcional',
                'conteudo': 'Conteúdo do aviso funcional',
                'igrejas_destino': [],
                'data_expiracao': '',
                'publicado': 'on',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('comunicacao:lista_avisos'))
        self.assertTrue(Aviso.objects.filter(ministerio=self.ministerio, titulo='Aviso funcional').exists())

    def _post_email_massa(self):
        return self.client.post(
            reverse('comunicacao:enviar_email_massa'),
            data={
                'assunto': 'Assunto funcional',
                'mensagem': 'Corpo da mensagem',
                'igrejas_destino': [],
                'tipos_pessoa': [],
                'status_pessoa': [],
                'aniversariantes_do_mes': False,
            },
        )

    @patch('comunicacao.views.email.filtrar_membros_email_destino')
    @patch('comunicacao.views.email.listar_destinatarios_email')
    @patch('comunicacao.views.email.enviar_email_massa_service')
    def test_enviar_email_massa_chama_service_e_exibe_sucesso_para_envio_real(
        self,
        mock_service,
        mock_listar_destinatarios,
        mock_filtrar_membros,
    ):
        mock_filtrar_membros.return_value = object()
        mock_listar_destinatarios.return_value = ['destino@teste.com']
        mock_service.return_value = ResultadoEnvioEmailMassa(
            quantidade_destinatarios=1,
            resultado_dispatch=ResultadoEnvioEmail(
                status=StatusEnvioEmail.ENVIADO,
                backend_chamado=True,
                resultado_backend=1,
            ),
        )

        response = self._post_email_massa()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('comunicacao:enviar_email_massa'))
        mock_filtrar_membros.assert_called_once()
        mock_listar_destinatarios.assert_called_once()
        mock_service.assert_called_once()
        mensagens = [str(mensagem) for mensagem in get_messages(response.wsgi_request)]
        self.assertIn('E-mail enviado com sucesso para 1 destinatário(s)!', mensagens)

    @patch('comunicacao.views.email.filtrar_membros_email_destino')
    @patch('comunicacao.views.email.listar_destinatarios_email')
    @patch('comunicacao.views.email.enviar_email_massa_service')
    def test_enviar_email_massa_exibe_neutralizacao_demo(self, mock_service, mock_listar_destinatarios, mock_filtrar_membros):
        mock_filtrar_membros.return_value = object()
        mock_listar_destinatarios.return_value = ['destino@teste.com']
        mock_service.return_value = ResultadoEnvioEmailMassa(
            quantidade_destinatarios=1,
            resultado_dispatch=ResultadoEnvioEmail(
                status=StatusEnvioEmail.NEUTRALIZADO_DEMO,
                backend_chamado=False,
                resultado_backend=None,
            ),
        )

        response = self._post_email_massa()
        mensagens = [str(mensagem) for mensagem in get_messages(response.wsgi_request)]

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('comunicacao:enviar_email_massa'))
        self.assertIn('Envio externo de e-mail foi neutralizado neste ambiente de demonstração.', mensagens)
        self.assertNotIn('E-mail enviado com sucesso para 1 destinatário(s)!', mensagens)

    @patch('comunicacao.views.email.filtrar_membros_email_destino')
    @patch('comunicacao.views.email.listar_destinatarios_email')
    @patch('comunicacao.views.email.enviar_email_massa_service')
    def test_enviar_email_massa_nao_afirma_sucesso_quando_nao_enviado(
        self,
        mock_service,
        mock_listar_destinatarios,
        mock_filtrar_membros,
    ):
        mock_filtrar_membros.return_value = object()
        mock_listar_destinatarios.return_value = ['destino@teste.com']
        mock_service.return_value = ResultadoEnvioEmailMassa(
            quantidade_destinatarios=1,
            resultado_dispatch=ResultadoEnvioEmail(
                status=StatusEnvioEmail.NAO_ENVIADO,
                backend_chamado=True,
                resultado_backend=0,
            ),
        )

        response = self._post_email_massa()
        mensagens = [str(mensagem) for mensagem in get_messages(response.wsgi_request)]

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('comunicacao:enviar_email_massa'))
        self.assertIn('Não foi possível concluir o envio externo de e-mail.', mensagens)
        self.assertNotIn('E-mail enviado com sucesso para 1 destinatário(s)!', mensagens)

    @patch('comunicacao.views.email.filtrar_membros_email_destino')
    @patch('comunicacao.views.email.listar_destinatarios_email')
    @patch('comunicacao.views.email.enviar_email_massa_service')
    def test_enviar_email_massa_preserva_tratamento_de_bad_header(
        self,
        mock_service,
        mock_listar_destinatarios,
        mock_filtrar_membros,
    ):
        mock_filtrar_membros.return_value = object()
        mock_listar_destinatarios.return_value = ['destino@teste.com']
        mock_service.side_effect = BadHeaderError('Assunto inválido')

        response = self._post_email_massa()
        mensagens = [str(mensagem) for mensagem in get_messages(response.wsgi_request)]

        self.assertEqual(response.status_code, 200)
        self.assertIn('Assunto inválido.', mensagens)

    def test_configurar_whatsapp_global_persiste_ativo(self):
        response = self.client.post(
            reverse('comunicacao:configurar_whatsapp_global'),
            data={'ativo': 'on'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('comunicacao:configurar_whatsapp_global'))
        config = WhatsAppConfiguracaoGlobal.objects.get(ministerio=self.ministerio)
        self.assertTrue(config.ativo)
