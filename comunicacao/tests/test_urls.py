from django.test import SimpleTestCase
from django.urls import reverse


class ComunicacaoUrlsTests(SimpleTestCase):
    def test_rotas_sem_parametros(self):
        esperadas = {
            'comunicacao:home': '/comunicacao/home/',
            'comunicacao:enviar_email_massa': '/comunicacao/email-massa/',
            'comunicacao:templates_email': '/comunicacao/templates-email/',
            'comunicacao:configurar_whatsapp': '/comunicacao/whatsapp/configuracao/',
            'comunicacao:enviar_whatsapp_massa': '/comunicacao/whatsapp/massa/',
            'comunicacao:preview_whatsapp_destinatarios': '/comunicacao/whatsapp/massa/preview/',
            'comunicacao:editar_celulares_whatsapp_massa': '/comunicacao/whatsapp/massa/editar-celulares/',
            'comunicacao:test_waha_health': '/comunicacao/whatsapp/massa/test-health/',
            'comunicacao:logs_whatsapp': '/comunicacao/whatsapp/logs/',
            'comunicacao:waha_webhook': '/comunicacao/whatsapp/webhook/',
            'comunicacao:lista_avisos': '/comunicacao/mural/',
            'comunicacao:criar_aviso': '/comunicacao/mural/novo/',
        }

        for nome, caminho in esperadas.items():
            with self.subTest(route_name=nome):
                self.assertEqual(reverse(nome), caminho)

    def test_rotas_com_parametros(self):
        self.assertEqual(reverse('comunicacao:detalhe_aviso', kwargs={'pk': 1}), '/comunicacao/mural/1/')
        self.assertEqual(reverse('comunicacao:editar_aviso', kwargs={'pk': 1}), '/comunicacao/mural/1/editar/')
        self.assertEqual(reverse('comunicacao:excluir_aviso', kwargs={'pk': 1}), '/comunicacao/mural/1/excluir/')
        self.assertEqual(reverse('comunicacao:qr_code_whatsapp', kwargs={'pk': 1}), '/comunicacao/whatsapp/qr/1/')
