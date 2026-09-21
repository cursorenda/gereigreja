from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from comunicacao.forms import WhatsAppConfiguracaoForm
from comunicacao.models import AutomacaoAniversariantes, WhatsAppConfiguracao
from comunicacao.services import (
    executar_automacao_aniversario_whatsapp,
    executar_automacao_followup_visitantes_whatsapp,
    executar_automacao_lembrete_eventos_whatsapp,
    executar_automacao_novos_membros_whatsapp,
)
from comunicacao.services_whatsapp import WhatsAppSendError, send_whatsapp_text
from configuracao.models import Igreja, Ministerio
from eventos.models import Evento
from secretaria.models import Membro, Pessoa, StatusPessoa, TipoPessoa


class WhatsAppConfiguracaoTenantTests(TestCase):
    def setUp(self):
        self.admin_a = User.objects.create_user(username='admin-tenant-a')
        self.admin_b = User.objects.create_user(username='admin-tenant-b')
        self.ministerio_a = Ministerio.objects.create(
            nome_fantasia='Ministerio A', administrador_principal=self.admin_a,
        )
        self.ministerio_b = Ministerio.objects.create(
            nome_fantasia='Ministerio B', administrador_principal=self.admin_b,
        )
        self.igreja_a = Igreja.objects.create(ministerio=self.ministerio_a, nome_igreja='Igreja A')
        self.igreja_b = Igreja.objects.create(ministerio=self.ministerio_b, nome_igreja='Igreja B')
        self.tipo = TipoPessoa.objects.create(nome='Membro Tenant WhatsApp')
        self.status = StatusPessoa.objects.create(nome='Ativo Tenant WhatsApp')

    def _dados_pessoa(self):
        return {'tipo_pessoa': self.tipo, 'status_pessoa': self.status}

    def _criar_config_valida(self, **overrides):
        dados = {
            'ministerio': self.ministerio_a,
            'igreja': self.igreja_a,
            'ativo': True,
            'numero_envio': '11999999999',
        }
        dados.update(overrides)
        return WhatsAppConfiguracao.objects.create(**dados)

    def _criar_config_historica_invalida(self, **overrides):
        agora = timezone.now()
        dados = {
            'ministerio_id': self.ministerio_a.id,
            'igreja_id': self.igreja_b.id,
            'ativo': True,
            'numero_envio': '11999999999',
            'criado_em': agora,
            'atualizado_em': agora,
        }
        dados.update(overrides)
        # Bypass deliberado apenas no teste: simula linha histórica criada antes
        # da invariável de tenant, sem chamar save()/full_clean().
        WhatsAppConfiguracao.objects.filter()._insert(
            [WhatsAppConfiguracao(**dados)], fields=[
                field for field in WhatsAppConfiguracao._meta.local_concrete_fields if not field.primary_key
            ], raw=True,
        )
        return WhatsAppConfiguracao.objects.get(igreja_id=self.igreja_b.id)

    def test_model_rejeita_configuracao_cross_tenant_e_aceita_mesmo_tenant(self):
        with self.assertRaises(ValidationError):
            self._criar_config_valida(igreja=self.igreja_b)

        config = self._criar_config_valida()
        self.assertEqual(config.igreja_id, self.igreja_a.id)

    def test_form_rejeita_post_adulterado_cross_tenant(self):
        form = WhatsAppConfiguracaoForm(
            data={'igreja': self.igreja_b.id, 'numero_envio': '11999999999'},
            ministerio=self.ministerio_a,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('igreja', form.errors)

    @patch('comunicacao.services.send_whatsapp_text')
    def test_config_historica_invalida_nao_envia_e_nao_bloqueia_config_valida(self, mock_send):
        self._criar_config_historica_invalida(auto_aniversariantes=True)
        self._criar_config_valida(auto_aniversariantes=True)
        Membro.objects.create(igreja=self.igreja_a, nome='Pessoa A', celular='11999999999', nascimento=timezone.localdate(), **self._dados_pessoa())
        Membro.objects.create(igreja=self.igreja_b, nome='Pessoa B', celular='11888888888', nascimento=timezone.localdate(), **self._dados_pessoa())
        AutomacaoAniversariantes.objects.create(
            ministerio=self.ministerio_a,
            whatsapp_template='Ola {primeiro_nome}',
        )

        resumo = executar_automacao_aniversario_whatsapp(ministerio=self.ministerio_a, force=True)

        self.assertEqual(resumo['enviados'], 1)
        self.assertEqual(mock_send.call_count, 1)
        self.assertEqual(mock_send.call_args.kwargs['igreja'], self.igreja_a)

    @patch('comunicacao.services.send_whatsapp_text')
    def test_todas_automacoes_ignoram_config_historica_invalida(self, mock_send):
        hoje = timezone.localdate()
        self._criar_config_historica_invalida(
            auto_aniversariantes=True,
            auto_novos_membros=True,
            auto_lembrete_eventos=True,
        )
        Membro.objects.create(igreja=self.igreja_b, nome='Aniversariante B', celular='11888888888', nascimento=hoje, **self._dados_pessoa())
        Pessoa.objects.create(igreja=self.igreja_b, nome='Visitante B', celular='11888888888', data_primeira_visita=hoje - timedelta(days=1), **self._dados_pessoa())
        Evento.objects.create(igreja=self.igreja_b, titulo='Evento B', data_inicio=timezone.now() + timedelta(hours=2))
        AutomacaoAniversariantes.objects.create(
            ministerio=self.ministerio_a,
            whatsapp_template='Ola {primeiro_nome}',
            followup_visitantes_ativo=True,
            followup_visitantes_dias_apos=1,
            lembrete_eventos_ativo=True,
        )

        executar_automacao_aniversario_whatsapp(ministerio=self.ministerio_a, force=True)
        executar_automacao_novos_membros_whatsapp(ministerio=self.ministerio_a, referencia=hoje, force=True)
        executar_automacao_followup_visitantes_whatsapp(ministerio=self.ministerio_a, referencia=hoje, force=True)
        executar_automacao_lembrete_eventos_whatsapp(ministerio=self.ministerio_a, referencia=timezone.now(), force=True)

        self.assertEqual(mock_send.call_count, 0)

    @patch('comunicacao.services_whatsapp.requests.post')
    @patch('comunicacao.services_whatsapp.requests.get')
    def test_transporte_bloqueia_config_historica_antes_da_rede(self, mock_get, mock_post):
        config = self._criar_config_historica_invalida()

        with self.assertRaises(WhatsAppSendError):
            send_whatsapp_text(
                config,
                '11999999999',
                'Mensagem de teste',
                ministerio=self.ministerio_a,
                igreja=self.igreja_b,
            )

        mock_get.assert_not_called()
        mock_post.assert_not_called()