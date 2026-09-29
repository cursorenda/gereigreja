from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase


class EnviarEmailAutomaticoCommandTests(SimpleTestCase):
    @patch('comunicacao.management.commands.enviar_email_automatico.executar_automacao_aniversario_email')
    @patch('comunicacao.management.commands.enviar_email_automatico.AutomacaoAniversariantes.objects.filter')
    def test_resumo_distingue_status_de_dispatch(self, mock_automacoes, mock_executar):
        mock_automacoes.return_value.select_related.return_value = [
            SimpleNamespace(ministerio=SimpleNamespace(pk=1)),
        ]
        mock_executar.return_value = {
            'enviados': 1,
            'neutralizados_demo': 2,
            'nao_enviados': 3,
            'falhas': 4,
            'ignorado': False,
        }
        output = StringIO()

        call_command('enviar_email_automatico', stdout=output)

        texto = output.getvalue()
        self.assertIn('Enviados externamente: 1', texto)
        self.assertIn('Neutralizados em Demo: 2', texto)
        self.assertIn('Não enviados: 3', texto)
        self.assertIn('Falhas de envio: 4', texto)