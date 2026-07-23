from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from comunicacao.models import Aviso, WhatsAppConfiguracaoGlobal
from configuracao.models import AssinaturaMinisterio, Ministerio, PerfilUsuario, Plano
from contas.constants import ADMIN_MINISTERIO


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

    @patch('comunicacao.views.email.filtrar_membros_email_destino')
    @patch('comunicacao.views.email.listar_destinatarios_email')
    @patch('comunicacao.views.email.enviar_email_massa_service')
    def test_enviar_email_massa_chama_service(self, mock_service, mock_listar_destinatarios, mock_filtrar_membros):
        mock_filtrar_membros.return_value = object()
        mock_listar_destinatarios.return_value = ['destino@teste.com']
        mock_service.return_value = 1

        response = self.client.post(
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

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('comunicacao:enviar_email_massa'))
        mock_filtrar_membros.assert_called_once()
        mock_listar_destinatarios.assert_called_once()
        mock_service.assert_called_once()

    def test_configurar_whatsapp_global_persiste_ativo(self):
        response = self.client.post(
            reverse('comunicacao:configurar_whatsapp_global'),
            data={'ativo': 'on'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('comunicacao:configurar_whatsapp_global'))
        config = WhatsAppConfiguracaoGlobal.objects.get(ministerio=self.ministerio)
        self.assertTrue(config.ativo)
