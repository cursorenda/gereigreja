from importlib import import_module

from django.test import SimpleTestCase


class ComunicacaoViewsImportsTests(SimpleTestCase):
    def test_modulos_de_views_importam(self):
        modulos = [
            'comunicacao.views',
            'comunicacao.views.home',
            'comunicacao.views.email',
            'comunicacao.views.logs',
            'comunicacao.views.mural',
            'comunicacao.views.whatsapp',
        ]

        for modulo in modulos:
            with self.subTest(module=modulo):
                self.assertIsNotNone(import_module(modulo))
