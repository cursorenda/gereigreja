from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import TestCase

from configuracao.models import Igreja, Ministerio
from core.email_services import ResultadoEnvioEmail, StatusEnvioEmail
from comunicacao.services import (
    ResultadoEnvioEmailMassa,
    executar_automacao_aniversario_email,
    executar_automacao_followup_visitantes_whatsapp,
    executar_automacao_lembrete_eventos_whatsapp,
    executar_automacao_aniversario_whatsapp,
    executar_automacao_novos_membros_whatsapp,
    enviar_email_personalizado,
    enviar_email_massa,
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
    def _resultado_email(self, status, resultado_backend=None):
        return ResultadoEnvioEmail(
            status=status,
            backend_chamado=status != StatusEnvioEmail.NEUTRALIZADO_DEMO,
            resultado_backend=resultado_backend,
        )

    @patch('comunicacao.services.enviar_email_seguro')
    @patch('comunicacao.services.render_to_string')
    def test_enviar_email_massa_preserva_dispatch_e_parametros(self, mock_render, mock_enviar_email_seguro):
        ministerio = SimpleNamespace(nome_fantasia='Ministerio Teste')
        destinatarios = ['ana@example.com', 'bruno@example.com']
        resultado_dispatch = ResultadoEnvioEmail(
            status=StatusEnvioEmail.ENVIADO,
            backend_chamado=True,
            resultado_backend=1,
        )
        mock_render.return_value = '<html>Mensagem</html>'
        mock_enviar_email_seguro.return_value = resultado_dispatch

        resultado = enviar_email_massa(
            ministerio=ministerio,
            assunto='Assunto de teste',
            mensagem='Mensagem de teste',
            destinatarios_emails=destinatarios,
            igrejas_destino=MagicMock(count=MagicMock(return_value=0)),
        )

        self.assertEqual(
            resultado,
            ResultadoEnvioEmailMassa(
                quantidade_destinatarios=2,
                resultado_dispatch=resultado_dispatch,
            ),
        )
        mock_render.assert_called_once_with(
            'comunicacao/email/email_massa_template.html',
            {
                'assunto': 'Assunto de teste',
                'mensagem': 'Mensagem de teste',
                'ministerio_nome': 'Ministerio Teste',
                'igreja_nome': None,
                'remetente_email': settings.DEFAULT_FROM_EMAIL,
            },
        )
        mock_enviar_email_seguro.assert_called_once_with(
            'Assunto de teste',
            'Mensagem de teste',
            destinatarios,
            ministerio=ministerio,
            html_message='<html>Mensagem</html>',
            from_email=settings.DEFAULT_FROM_EMAIL,
            fail_silently=False,
        )

    @patch('comunicacao.services.enviar_email_seguro')
    @patch('comunicacao.services.render_to_string')
    def test_enviar_email_massa_preserva_neutralizacao_demo(self, mock_render, mock_enviar_email_seguro):
        resultado_dispatch = ResultadoEnvioEmail(
            status=StatusEnvioEmail.NEUTRALIZADO_DEMO,
            backend_chamado=False,
            resultado_backend=None,
        )
        mock_enviar_email_seguro.return_value = resultado_dispatch

        resultado = enviar_email_massa(
            ministerio=SimpleNamespace(nome_fantasia='Ministerio Demo'),
            assunto='Assunto',
            mensagem='Mensagem',
            destinatarios_emails=['demo@example.com'],
            igrejas_destino=MagicMock(count=MagicMock(return_value=0)),
        )

        self.assertEqual(resultado.quantidade_destinatarios, 1)
        self.assertIs(resultado.resultado_dispatch, resultado_dispatch)
        self.assertEqual(resultado.resultado_dispatch.status, StatusEnvioEmail.NEUTRALIZADO_DEMO)

    @patch('comunicacao.services.enviar_email_seguro')
    @patch('comunicacao.services.render_to_string')
    def test_enviar_email_massa_preserva_contagem_quando_backend_retorna_zero(
        self,
        mock_render,
        mock_enviar_email_seguro,
    ):
        resultado_dispatch = ResultadoEnvioEmail(
            status=StatusEnvioEmail.NAO_ENVIADO,
            backend_chamado=True,
            resultado_backend=0,
        )
        mock_enviar_email_seguro.return_value = resultado_dispatch

        resultado = enviar_email_massa(
            ministerio=SimpleNamespace(nome_fantasia='Ministerio Teste'),
            assunto='Assunto',
            mensagem='Mensagem',
            destinatarios_emails=['um@example.com', 'dois@example.com', 'tres@example.com'],
            igrejas_destino=MagicMock(count=MagicMock(return_value=0)),
        )

        self.assertEqual(resultado.quantidade_destinatarios, 3)
        self.assertIs(resultado.resultado_dispatch, resultado_dispatch)
        self.assertEqual(resultado.resultado_dispatch.resultado_backend, 0)
        self.assertEqual(resultado.resultado_dispatch.status, StatusEnvioEmail.NAO_ENVIADO)

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
        mock_email.return_value = self._resultado_email(StatusEnvioEmail.ENVIADO, 1)

        resumo = executar_automacao_aniversario_email(ministerio=ministerio, force=False)

        self.assertEqual(resumo['enviados'], 1)
        self.assertEqual(resumo['neutralizados_demo'], 0)
        self.assertEqual(resumo['nao_enviados'], 0)
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
        mock_email.return_value = self._resultado_email(StatusEnvioEmail.ENVIADO, 1)

        resumo = executar_automacao_aniversario_email(
            ministerio=ministerio_a,
            referencia=hoje,
        )

        self.assertEqual(resumo['enviados'], 1)
        self.assertEqual(resumo['neutralizados_demo'], 0)
        self.assertEqual(resumo['nao_enviados'], 0)
        self.assertEqual(resumo['falhas'], 0)
        mock_email.assert_called_once()
        self.assertEqual(mock_email.call_args.kwargs['ministerio'], ministerio_a)
        self.assertEqual(mock_email.call_args.kwargs['membro'], pessoa_a)

    @patch('comunicacao.services.enviar_email_seguro')
    @patch('comunicacao.services.render_to_string')
    def test_enviar_email_personalizado_retorna_resultado_do_wrapper(self, mock_render, mock_enviar_email_seguro):
        ministerio = SimpleNamespace(nome_fantasia='Ministerio Teste')
        membro = SimpleNamespace(
            nome='Ana Silva',
            nascimento=date(1990, 7, 13),
            email='ana@example.com',
            igreja=SimpleNamespace(nome_igreja='Igreja Central', email='contato@igreja.com'),
        )
        resultado_dispatch = self._resultado_email(StatusEnvioEmail.ENVIADO, 1)
        mock_render.return_value = '<html>Mensagem</html>'
        mock_enviar_email_seguro.return_value = resultado_dispatch

        resultado = enviar_email_personalizado(
            ministerio=ministerio,
            membro=membro,
            assunto_template='Feliz aniversario, {primeiro_nome}',
            mensagem_template='Parabens, {nome}',
        )

        self.assertIs(resultado, resultado_dispatch)
        mock_render.assert_called_once_with(
            'comunicacao/email/email_massa_template.html',
            {
                'assunto': 'Feliz aniversario, Ana',
                'mensagem': 'Parabens, Ana Silva',
                'ministerio_nome': 'Ministerio Teste',
                'igreja_nome': 'Igreja Central',
                'remetente_email': 'contato@igreja.com',
            },
        )
        mock_enviar_email_seguro.assert_called_once_with(
            'Feliz aniversario, Ana',
            'Parabens, Ana Silva',
            ['ana@example.com'],
            ministerio=ministerio,
            membro=membro,
            html_message='<html>Mensagem</html>',
            from_email=settings.DEFAULT_FROM_EMAIL,
            fail_silently=False,
        )

    @patch('comunicacao.services.enviar_email_personalizado')
    @patch('comunicacao.services.Membro.objects.filter')
    @patch('comunicacao.services.Igreja.objects.filter')
    @patch('comunicacao.services.AutomacaoAniversariantes.objects')
    def test_automacao_email_contabiliza_neutralizacao_demo(self, mock_automacao_objects, mock_igreja_filter, mock_membro_filter, mock_email):
        hoje = date(2026, 7, 13)
        ministerio = SimpleNamespace(id=2, nome_fantasia='Demo')
        igreja = SimpleNamespace(nome_igreja='Congregacao Demo')
        pessoa = SimpleNamespace(nome='Ana', email='ana@example.com', igreja=igreja)
        mock_automacao_objects.get.return_value = SimpleNamespace(
            pk=20,
            ultima_execucao_email=None,
            email_assunto_template='Assunto',
            email_mensagem_template='Mensagem',
        )
        mock_igreja_filter.return_value = [igreja]
        mock_membro_filter.return_value = _ChainResult([pessoa])
        mock_email.return_value = self._resultado_email(StatusEnvioEmail.NEUTRALIZADO_DEMO)

        resumo = executar_automacao_aniversario_email(ministerio=ministerio, referencia=hoje)

        self.assertEqual(
            resumo,
            {'enviados': 0, 'neutralizados_demo': 1, 'nao_enviados': 0, 'falhas': 0, 'ignorado': False},
        )
        mock_automacao_objects.filter.return_value.update.assert_called_once_with(ultima_execucao_email=hoje)

    @patch('comunicacao.services.enviar_email_personalizado')
    @patch('comunicacao.services.Membro.objects.filter')
    @patch('comunicacao.services.Igreja.objects.filter')
    @patch('comunicacao.services.AutomacaoAniversariantes.objects')
    def test_automacao_email_contabiliza_backend_zero(self, mock_automacao_objects, mock_igreja_filter, mock_membro_filter, mock_email):
        hoje = date(2026, 7, 13)
        ministerio = SimpleNamespace(id=2, nome_fantasia='Teste')
        igreja = SimpleNamespace(nome_igreja='Congregacao')
        pessoa = SimpleNamespace(nome='Ana', email='ana@example.com', igreja=igreja)
        mock_automacao_objects.get.return_value = SimpleNamespace(
            pk=20,
            ultima_execucao_email=None,
            email_assunto_template='Assunto',
            email_mensagem_template='Mensagem',
        )
        mock_igreja_filter.return_value = [igreja]
        mock_membro_filter.return_value = _ChainResult([pessoa])
        mock_email.return_value = self._resultado_email(StatusEnvioEmail.NAO_ENVIADO, 0)

        resumo = executar_automacao_aniversario_email(ministerio=ministerio, referencia=hoje)

        self.assertEqual(
            resumo,
            {'enviados': 0, 'neutralizados_demo': 0, 'nao_enviados': 1, 'falhas': 0, 'ignorado': False},
        )
        mock_automacao_objects.filter.return_value.update.assert_called_once_with(ultima_execucao_email=hoje)

    @patch('comunicacao.services.enviar_email_personalizado')
    @patch('comunicacao.services.Membro.objects.filter')
    @patch('comunicacao.services.Igreja.objects.filter')
    @patch('comunicacao.services.AutomacaoAniversariantes.objects')
    def test_automacao_email_continua_apos_falha_parcial(self, mock_automacao_objects, mock_igreja_filter, mock_membro_filter, mock_email):
        hoje = date(2026, 7, 13)
        ministerio = SimpleNamespace(id=2, nome_fantasia='Teste')
        igreja = SimpleNamespace(nome_igreja='Congregacao')
        pessoa_ok = SimpleNamespace(nome='Ana', email='ana@example.com', igreja=igreja)
        pessoa_falha = SimpleNamespace(nome='Bruno', email='bruno@example.com', igreja=igreja)
        mock_automacao_objects.get.return_value = SimpleNamespace(
            pk=20,
            ultima_execucao_email=None,
            email_assunto_template='Assunto',
            email_mensagem_template='Mensagem',
        )
        mock_igreja_filter.return_value = [igreja]
        mock_membro_filter.return_value = _ChainResult([pessoa_ok, pessoa_falha])
        mock_email.side_effect = [self._resultado_email(StatusEnvioEmail.ENVIADO, 1), Exception('falha simulada')]

        resumo = executar_automacao_aniversario_email(ministerio=ministerio, referencia=hoje)

        self.assertEqual(
            resumo,
            {'enviados': 1, 'neutralizados_demo': 0, 'nao_enviados': 0, 'falhas': 1, 'ignorado': False},
        )
        self.assertEqual(mock_email.call_count, 2)
        mock_automacao_objects.filter.return_value.update.assert_called_once_with(ultima_execucao_email=hoje)

    @patch('comunicacao.services.enviar_email_personalizado')
    @patch('comunicacao.services.Membro.objects.filter')
    @patch('comunicacao.services.Igreja.objects.filter')
    @patch('comunicacao.services.AutomacaoAniversariantes.objects')
    def test_automacao_email_atualiza_lote_apos_falha_total_individual(self, mock_automacao_objects, mock_igreja_filter, mock_membro_filter, mock_email):
        hoje = date(2026, 7, 13)
        ministerio = SimpleNamespace(id=2, nome_fantasia='Teste')
        igreja = SimpleNamespace(nome_igreja='Congregacao')
        pessoas = [
            SimpleNamespace(nome='Ana', email='ana@example.com', igreja=igreja),
            SimpleNamespace(nome='Bruno', email='bruno@example.com', igreja=igreja),
        ]
        mock_automacao_objects.get.return_value = SimpleNamespace(
            pk=20,
            ultima_execucao_email=None,
            email_assunto_template='Assunto',
            email_mensagem_template='Mensagem',
        )
        mock_igreja_filter.return_value = [igreja]
        mock_membro_filter.return_value = _ChainResult(pessoas)
        mock_email.side_effect = [Exception('falha 1'), Exception('falha 2')]

        resumo = executar_automacao_aniversario_email(ministerio=ministerio, referencia=hoje)

        self.assertEqual(
            resumo,
            {'enviados': 0, 'neutralizados_demo': 0, 'nao_enviados': 0, 'falhas': 2, 'ignorado': False},
        )
        mock_automacao_objects.filter.return_value.update.assert_called_once_with(ultima_execucao_email=hoje)

    @patch('comunicacao.services.enviar_email_personalizado')
    @patch('comunicacao.services.Igreja.objects.filter')
    @patch('comunicacao.services.AutomacaoAniversariantes.objects')
    def test_automacao_email_ignora_mesmo_dia_sem_force(self, mock_automacao_objects, mock_igreja_filter, mock_email):
        hoje = date(2026, 7, 13)
        ministerio = SimpleNamespace(id=2, nome_fantasia='Teste')
        mock_automacao_objects.get.return_value = SimpleNamespace(pk=20, ultima_execucao_email=hoje)

        resumo = executar_automacao_aniversario_email(ministerio=ministerio, referencia=hoje, force=False)

        self.assertEqual(
            resumo,
            {'enviados': 0, 'neutralizados_demo': 0, 'nao_enviados': 0, 'falhas': 0, 'ignorado': True},
        )
        mock_igreja_filter.assert_not_called()
        mock_email.assert_not_called()

    @patch('comunicacao.services.enviar_email_personalizado')
    @patch('comunicacao.services.Membro.objects.filter')
    @patch('comunicacao.services.Igreja.objects.filter')
    @patch('comunicacao.services.AutomacaoAniversariantes.objects')
    def test_automacao_email_force_reprocessa_aniversariantes_do_dia(self, mock_automacao_objects, mock_igreja_filter, mock_membro_filter, mock_email):
        hoje = date(2026, 7, 13)
        ministerio = SimpleNamespace(id=2, nome_fantasia='Teste')
        igreja = SimpleNamespace(nome_igreja='Congregacao')
        pessoa = SimpleNamespace(nome='Ana', email='ana@example.com', igreja=igreja)
        mock_automacao_objects.get.return_value = SimpleNamespace(
            pk=20,
            ultima_execucao_email=hoje,
            email_assunto_template='Assunto',
            email_mensagem_template='Mensagem',
        )
        mock_igreja_filter.return_value = [igreja]
        mock_membro_filter.return_value = _ChainResult([pessoa])
        mock_email.return_value = self._resultado_email(StatusEnvioEmail.ENVIADO, 1)

        resumo = executar_automacao_aniversario_email(ministerio=ministerio, referencia=hoje, force=True)

        self.assertFalse(resumo['ignorado'])
        self.assertEqual(resumo['enviados'], 1)
        mock_email.assert_called_once()

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
