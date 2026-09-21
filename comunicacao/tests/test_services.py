from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import TestCase

from configuracao.models import Igreja, Ministerio
from comunicacao.services import (
    executar_automacao_aniversario_email,
    executar_automacao_novos_membros_whatsapp,
    executar_automacao_followup_visitantes_whatsapp,
    executar_automacao_lembrete_eventos_whatsapp,
    executar_automacao_aniversario_whatsapp,
    personalizar_template_comunicacao,
)
from comunicacao.models import AutomacaoAniversariantes
from comunicacao.services_whatsapp import WhatsAppSendError
from secretaria.models import Pessoa, StatusPessoa, TipoPessoa


class _ChainResult:
    def __init__(self, items):
        self._items = items

    def exclude(self, **kwargs):
        return self

    def select_related(self, *args, **kwargs):
        return self._items

    def __iter__(self):
        return iter(self._items)


class _FilterResult:
    def __init__(self, items):
        self._items = items

    def select_related(self, *args, **kwargs):
        return self._items


class _OrderableResult:
    def __init__(self, items):
        self._items = items

    def order_by(self, *args, **kwargs):
        return self

    def exists(self):
        return bool(self._items)

    def __iter__(self):
        return iter(self._items)


class ComunicacaoServicesTests(TestCase):
    def test_personalizar_template_comunicacao_substitui_variaveis(self):
        membro = SimpleNamespace(
            nome='Maria de Souza',
            nascimento=date(1994, 7, 13),
            igreja=SimpleNamespace(nome_igreja='Sede Central'),
        )
        ministerio = SimpleNamespace(nome_fantasia='AD Ministerio dos Vales')

        template = 'Ola {primeiro_nome} ({nome}) da {igreja} - {ministerio} - {data_aniversario}'
        texto = personalizar_template_comunicacao(template, membro, ministerio)

        self.assertIn('Maria', texto)
        self.assertIn('Maria de Souza', texto)
        self.assertIn('Sede Central', texto)
        self.assertIn('AD Ministerio dos Vales', texto)
        self.assertIn('13/07', texto)

    @patch('comunicacao.services.AutomacaoAniversariantes.objects')
    @patch('comunicacao.services.timezone.localdate')
    def test_automacao_whatsapp_ignora_quando_ja_executou_no_dia(self, mock_localdate, mock_automacao_objects):
        hoje = date(2026, 7, 13)
        mock_localdate.return_value = hoje
        mock_automacao_objects.get.return_value = SimpleNamespace(
            pk=10,
            ultima_execucao_whatsapp=hoje,
            whatsapp_template='Feliz aniversario {primeiro_nome}',
        )

        resumo = executar_automacao_aniversario_whatsapp(ministerio=SimpleNamespace(id=1), force=False)

        self.assertEqual(resumo, {'enviados': 0, 'falhas': 0, 'ignorado': True})

    @patch('comunicacao.services.send_whatsapp_text')
    @patch('comunicacao.services.Membro.objects.filter')
    @patch('comunicacao.services.WhatsAppConfiguracao.objects.filter')
    @patch('comunicacao.services.AutomacaoAniversariantes.objects')
    @patch('comunicacao.services.timezone.localdate')
    def test_automacao_whatsapp_processa_envios_e_falhas(self, mock_localdate, mock_automacao_objects, mock_cfg_filter, mock_membro_filter, mock_send):
        hoje = date(2026, 7, 13)
        ministerio = SimpleNamespace(id=1, nome_fantasia='AD Teste')
        igreja = SimpleNamespace(nome_igreja='Sede')
        config = SimpleNamespace(igreja=igreja)
        pessoa_ok = SimpleNamespace(nome='Ana Clara', nascimento=hoje, celular='11999999999', igreja=igreja)
        pessoa_erro = SimpleNamespace(nome='Bruno Lima', nascimento=hoje, celular='11888888888', igreja=igreja)

        mock_localdate.return_value = hoje
        mock_automacao_objects.get.return_value = SimpleNamespace(
            pk=10,
            ultima_execucao_whatsapp=None,
            whatsapp_template='Feliz aniversario {primeiro_nome}',
        )
        mock_cfg_filter.return_value = _FilterResult([config])
        mock_membro_filter.return_value = _ChainResult([pessoa_ok, pessoa_erro])
        mock_send.side_effect = [None, WhatsAppSendError('falha simulada')]

        resumo = executar_automacao_aniversario_whatsapp(ministerio=ministerio, force=False)

        self.assertEqual(resumo['enviados'], 1)
        self.assertEqual(resumo['falhas'], 1)
        self.assertFalse(resumo['ignorado'])
        mock_automacao_objects.filter.return_value.update.assert_called_once_with(ultima_execucao_whatsapp=hoje)

    @patch('comunicacao.services.enviar_email_personalizado')
    @patch('comunicacao.services.Membro.objects.filter')
    @patch('comunicacao.services.Igreja.objects.filter')
    @patch('comunicacao.services.AutomacaoAniversariantes.objects')
    @patch('comunicacao.services.timezone.localdate')
    def test_automacao_email_processa_envios(
        self,
        mock_localdate,
        mock_automacao_objects,
        mock_igreja_filter,
        mock_membro_filter,
        mock_email,
    ):
        hoje = date(2026, 7, 13)
        ministerio = SimpleNamespace(id=2, nome_fantasia='AD QA')
        igreja = SimpleNamespace(nome_igreja='Congregacao Norte')
        pessoa = SimpleNamespace(nome='Carlos Melo', nascimento=hoje, email='carlos@teste.com', igreja=igreja)

        mock_localdate.return_value = hoje
        mock_automacao_objects.get.return_value = SimpleNamespace(
            pk=20,
            ultima_execucao_email=None,
            email_assunto_template='Feliz aniversario {primeiro_nome}',
            email_mensagem_template='Parabens {nome}',
        )
        mock_igreja_filter.return_value = [igreja]
        mock_membro_filter.return_value = _ChainResult([pessoa])

        resumo = executar_automacao_aniversario_email(ministerio=ministerio, force=False)

        self.assertEqual(resumo['enviados'], 1)
        self.assertEqual(resumo['falhas'], 0)
        self.assertFalse(resumo['ignorado'])
        mock_email.assert_called_once()
        mock_automacao_objects.filter.return_value.update.assert_called_once_with(ultima_execucao_email=hoje)

    @patch('comunicacao.services.enviar_email_personalizado')
    def test_automacao_email_restringe_aniversariantes_ao_ministerio_informado(self, mock_email):
        from django.contrib.auth import get_user_model

        hoje = date(2026, 7, 13)
        User = get_user_model()
        admin_a = User.objects.create_user(username='admin-email-a')
        admin_b = User.objects.create_user(username='admin-email-b')
        ministerio_a = Ministerio.objects.create(
            nome_fantasia='Ministerio A',
            administrador_principal=admin_a,
        )
        ministerio_b = Ministerio.objects.create(
            nome_fantasia='Ministerio B',
            administrador_principal=admin_b,
        )
        igreja_a = Igreja.objects.create(ministerio=ministerio_a, nome_igreja='Igreja A')
        igreja_b = Igreja.objects.create(ministerio=ministerio_b, nome_igreja='Igreja B')
        tipo = TipoPessoa.objects.create(nome='Membro Email Scope')
        status = StatusPessoa.objects.create(nome='Ativo Email Scope')
        pessoa_a = Pessoa.objects.create(
            igreja=igreja_a,
            nome='Aniversariante A',
            nascimento=hoje,
            email='a@example.com',
            tipo_pessoa=tipo,
            status_pessoa=status,
        )
        Pessoa.objects.create(
            igreja=igreja_b,
            nome='Aniversariante B',
            nascimento=hoje,
            email='b@example.com',
            tipo_pessoa=tipo,
            status_pessoa=status,
        )
        AutomacaoAniversariantes.objects.create(
            ministerio=ministerio_a,
            email_ativo=True,
        )

        resumo = executar_automacao_aniversario_email(
            ministerio=ministerio_a,
            referencia=hoje,
        )

        self.assertEqual(resumo['enviados'], 1)
        self.assertEqual(resumo['falhas'], 0)
        mock_email.assert_called_once()
        self.assertEqual(mock_email.call_args.kwargs['ministerio'], ministerio_a)
        self.assertEqual(mock_email.call_args.kwargs['membro'], pessoa_a)

    @patch('comunicacao.services.WhatsAppMensagemLog.objects.filter')
    @patch('comunicacao.services.send_whatsapp_text')
    @patch('comunicacao.services.Membro.objects.filter')
    @patch('comunicacao.services.WhatsAppConfiguracao.objects.filter')
    @patch('comunicacao.services.timezone.localdate')
    def test_automacao_novos_membros_whatsapp_envia_apenas_nao_enviados(
        self,
        mock_localdate,
        mock_cfg_filter,
        mock_membro_filter,
        mock_send,
        mock_log_filter,
    ):
        hoje = date(2026, 7, 13)
        ministerio = SimpleNamespace(id=1, nome_fantasia='AD Teste')
        igreja = SimpleNamespace(nome_igreja='Sede')
        config = SimpleNamespace(igreja=igreja)
        novo_1 = SimpleNamespace(nome='Ana Clara', celular='11999999999', igreja=igreja)
        novo_2 = SimpleNamespace(nome='Bruno Lima', celular='11888888888', igreja=igreja)

        mock_localdate.return_value = hoje
        mock_cfg_filter.return_value = _FilterResult([config])
        mock_membro_filter.return_value = _ChainResult([novo_1, novo_2])
        mock_log_filter.return_value.exists.side_effect = [False, True]

        resumo = executar_automacao_novos_membros_whatsapp(
            ministerio=ministerio,
            referencia=hoje,
            dias=7,
            force=False,
        )

        self.assertEqual(resumo['enviados'], 1)
        self.assertEqual(resumo['falhas'], 0)
        self.assertEqual(resumo['ignorados'], 1)
        mock_send.assert_called_once()

    @patch('comunicacao.services.WhatsAppMensagemLog.objects.filter')
    @patch('comunicacao.services.send_whatsapp_text')
    @patch('comunicacao.services.Pessoa.objects.filter')
    @patch('comunicacao.services.WhatsAppConfiguracao.objects.filter')
    @patch('comunicacao.services.AutomacaoAniversariantes.objects.get_or_create')
    @patch('comunicacao.services.timezone.localdate')
    def test_automacao_followup_visitantes_whatsapp_dedup_no_dia(
        self,
        mock_localdate,
        mock_get_or_create,
        mock_cfg_filter,
        mock_pessoa_filter,
        mock_send,
        mock_log_filter,
    ):
        hoje = date(2026, 7, 13)
        ministerio = SimpleNamespace(id=1, nome_fantasia='AD Teste')
        igreja = SimpleNamespace(nome_igreja='Sede')
        config = SimpleNamespace(igreja=igreja)
        visitante_1 = SimpleNamespace(nome='Visitante A', celular='11999999999', igreja=igreja)
        visitante_2 = SimpleNamespace(nome='Visitante B', celular='11888888888', igreja=igreja)

        mock_localdate.return_value = hoje
        mock_get_or_create.return_value = (
            SimpleNamespace(
                followup_visitantes_ativo=True,
                followup_visitantes_dias_apos=1,
                followup_visitantes_template='Ola {primeiro_nome} da {igreja} - {ministerio}',
            ),
            False,
        )
        mock_cfg_filter.return_value = _FilterResult([config])
        mock_pessoa_filter.return_value = _ChainResult([visitante_1, visitante_2])
        mock_log_filter.return_value.exists.side_effect = [False, True]

        resumo = executar_automacao_followup_visitantes_whatsapp(
            ministerio=ministerio,
            referencia=hoje,
            dias_apos=1,
            force=False,
        )

        self.assertEqual(resumo['enviados'], 1)
        self.assertEqual(resumo['falhas'], 0)
        self.assertEqual(resumo['ignorados'], 1)
        mock_send.assert_called_once()

    @patch('comunicacao.services.WhatsAppMensagemLog.objects.filter')
    @patch('comunicacao.services.send_whatsapp_text')
    @patch('comunicacao.services.Pessoa.objects.filter')
    @patch('comunicacao.services.Evento.objects.filter')
    @patch('comunicacao.services.WhatsAppConfiguracao.objects.filter')
    @patch('comunicacao.services.AutomacaoAniversariantes.objects.get_or_create')
    @patch('comunicacao.services.timezone.localtime')
    def test_automacao_lembrete_eventos_whatsapp_dedup_no_dia(
        self,
        mock_localtime,
        mock_get_or_create,
        mock_cfg_filter,
        mock_evento_filter,
        mock_pessoa_filter,
        mock_send,
        mock_log_filter,
    ):
        from datetime import datetime

        ministerio = SimpleNamespace(id=1, nome_fantasia='AD Teste')
        igreja = SimpleNamespace(nome_igreja='Sede')
        config = SimpleNamespace(igreja=igreja)
        pessoa_1 = SimpleNamespace(nome='Ana', celular='11999999999', igreja=igreja)
        pessoa_2 = SimpleNamespace(nome='Bruno', celular='11888888888', igreja=igreja)
        evento = SimpleNamespace(titulo='Culto de Jovens', data_inicio=datetime(2026, 7, 13, 20, 0, 0))
        agora = datetime(2026, 7, 13, 10, 0, 0)

        mock_get_or_create.return_value = (
            SimpleNamespace(
                lembrete_eventos_ativo=True,
                lembrete_eventos_template='{quando} "{evento}" {hora} {igreja} {ministerio}',
            ),
            False,
        )
        mock_localtime.return_value = evento.data_inicio
        mock_cfg_filter.return_value = _FilterResult([config])
        mock_evento_filter.return_value = _OrderableResult([evento])
        mock_pessoa_filter.return_value = _ChainResult([pessoa_1, pessoa_2])
        mock_log_filter.return_value.exists.side_effect = [False, True]

        resumo = executar_automacao_lembrete_eventos_whatsapp(
            ministerio=ministerio,
            referencia=agora,
            force=False,
        )

        self.assertEqual(resumo['eventos_processados'], 1)
        self.assertEqual(resumo['enviados'], 1)
        self.assertEqual(resumo['falhas'], 0)
        self.assertEqual(resumo['ignorados'], 1)
        mock_send.assert_called_once()
