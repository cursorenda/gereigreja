from django.test import SimpleTestCase
from django.urls import reverse


class ComunicacaoAccessFlowTests(SimpleTestCase):
    def test_rotas_protegidas_redirecionam_para_login(self):
        rotas = [
            reverse('comunicacao:home'),
            reverse('comunicacao:enviar_email_massa'),
            reverse('comunicacao:preview_email_destinatarios'),
            reverse('comunicacao:configurar_automacao_aniversariantes'),
            reverse('comunicacao:templates_email'),
            reverse('comunicacao:visualizar_template_email_aniversario'),
            reverse('comunicacao:visualizar_template_email_massa'),
            reverse('comunicacao:visualizar_template_password_reset'),
            reverse('comunicacao:configurar_whatsapp'),
            reverse('comunicacao:enviar_whatsapp_massa'),
            reverse('comunicacao:preview_whatsapp_destinatarios'),
            reverse('comunicacao:editar_celulares_whatsapp_massa'),
            reverse('comunicacao:test_waha_health'),
            reverse('comunicacao:logs_whatsapp'),
            reverse('comunicacao:lista_avisos'),
            reverse('comunicacao:criar_aviso'),
            reverse('comunicacao:detalhe_aviso', kwargs={'pk': 1}),
            reverse('comunicacao:editar_aviso', kwargs={'pk': 1}),
            reverse('comunicacao:excluir_aviso', kwargs={'pk': 1}),
            reverse('comunicacao:configurar_whatsapp_global'),
            reverse('comunicacao:qr_code_whatsapp', kwargs={'pk': 1}),
        ]

        for rota in rotas:
            with self.subTest(url=rota):
                response = self.client.get(rota)
                self.assertEqual(response.status_code, 302)
                self.assertIn('/accounts/login/', response['Location'])

    def test_webhook_get_rejeitado(self):
        response = self.client.get(reverse('comunicacao:waha_webhook'))
        self.assertEqual(response.status_code, 405)
