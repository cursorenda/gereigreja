"""
Testes de regressao para os signals de comunicacao.

Cobre a remocao do handler legado enviar_whatsapp_novo_membro:
a criacao de uma Pessoa nao deve mais disparar envio de WhatsApp em tempo real
e nao deve gerar excecao de signal (NameError ou outra).
"""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from configuracao.models import Igreja, Ministerio
from secretaria.models import Pessoa, StatusPessoa, TipoPessoa


class PessoaPostSaveSignalRegressaoTest(TestCase):
    """Garante que o post_save de secretaria.Pessoa nao envia WhatsApp em tempo real."""

    def setUp(self):
        self.user_model = get_user_model()
        self.admin = self.user_model.objects.create_user(
            username='admin_sinal_regressao',
            password='senha123',
        )
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Sinal Regressao',
            administrador_principal=self.admin,
            ativo=True,
        )
        self.igreja = Igreja.objects.create(
            nome_igreja='Igreja Sinal Regressao',
            ministerio=self.ministerio,
        )
        self.tipo_membro = TipoPessoa.objects.create(nome='Membro')
        self.status_ativo = StatusPessoa.objects.create(nome='Ativo')

    def test_criar_pessoa_sem_whatsapp_config_nao_envia_whatsapp(self):
        """Criar Pessoa sem WhatsAppConfiguracao nao deve tentar enviar WhatsApp."""
        with patch('comunicacao.services.send_whatsapp_text') as mock_send:
            pessoa = Pessoa.objects.create(
                nome='Carlos Regressao',
                igreja=self.igreja,
                tipo_pessoa=self.tipo_membro,
                status_pessoa=self.status_ativo,
                celular='5533988507660',
            )

        self.assertIsNotNone(pessoa.pk)
        mock_send.assert_not_called()

    def test_criar_pessoa_com_whatsapp_config_ativo_nao_envia_em_tempo_real(self):
        """Mesmo com WhatsAppConfiguracao ativa, o envio em tempo real foi removido."""
        from comunicacao.models import WhatsAppConfiguracao

        WhatsAppConfiguracao.objects.create(
            ministerio=self.ministerio,
            igreja=self.igreja,
            ativo=True,
            numero_envio='5533988507660',
            remetente_nome='Teste',
            auto_novos_membros=True,
        )

        with patch('comunicacao.services_whatsapp.requests.post') as mock_post:
            pessoa = Pessoa.objects.create(
                nome='Maria Regressao',
                igreja=self.igreja,
                tipo_pessoa=self.tipo_membro,
                status_pessoa=self.status_ativo,
                celular='5533988507661',
            )

        self.assertIsNotNone(pessoa.pk)
        mock_post.assert_not_called()

    def test_criar_pessoa_sem_celular_nao_gera_excecao(self):
        """Criar Pessoa sem celular nao deve gerar excecao de signal."""
        with patch('comunicacao.services.send_whatsapp_text') as mock_send:
            pessoa = Pessoa.objects.create(
                nome='Sem Celular Regressao',
                igreja=self.igreja,
                tipo_pessoa=self.tipo_membro,
                status_pessoa=self.status_ativo,
                celular='',
            )

        self.assertIsNotNone(pessoa.pk)
        mock_send.assert_not_called()

    def test_criar_pessoa_sem_igreja_nao_gera_excecao(self):
        """Pessoa sem igreja (igreja_id NULL) nao deve gerar excecao de signal."""
        # Igreja e obrigatoria no model Pessoa (PROTECT), entao o teste cobre
        # o caminho em que a pessoa tem igreja mas nao ha config WhatsApp.
        with patch('comunicacao.services.send_whatsapp_text') as mock_send:
            pessoa = Pessoa.objects.create(
                nome='Sem Config Regressao',
                igreja=self.igreja,
                tipo_pessoa=self.tipo_membro,
                status_pessoa=self.status_ativo,
            )

        self.assertIsNotNone(pessoa.pk)
        mock_send.assert_not_called()
