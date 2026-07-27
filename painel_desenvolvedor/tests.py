from __future__ import annotations

import io
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import SimpleTestCase
from django.test.client import RequestFactory
from django.urls import reverse

from .forms import SistemaImagemForm
from .models import SistemaImagem
from .services_custo_risco import railway_status
from .views import calcular_risco_custo_whatsapp, galeria_imagens


def gerar_png_upload(nome: str = 'logo.png', tamanho: tuple[int, int] = (32, 32)) -> SimpleUploadedFile:
    """Gera uma imagem PNG válida em memória para testes."""
    buffer = io.BytesIO()
    imagem = Image.new('RGB', tamanho, color=(255, 255, 255))
    imagem.save(buffer, format='PNG')
    return SimpleUploadedFile(nome, buffer.getvalue(), content_type='image/png')


class DummyPaginatorPage:
    def __init__(self, items):
        self.object_list = items


class DummyPaginator:
    def __init__(self, items, per_page):
        self.items = list(items)
        self.per_page = per_page

    def get_page(self, page_number):
        return DummyPaginatorPage(self.items)


class DummyQuerySet(list):
    def count(self):
        return len(self)

    def filter(self, *args, **kwargs):
        return self

    def exclude(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def values(self, *args, **kwargs):
        return self

    def distinct(self):
        return self


class DashboardCustoRiscoTests(SimpleTestCase):
    def test_calcular_risco_custo_whatsapp_classifica_alto(self):
        risco = calcular_risco_custo_whatsapp(
            custo_mensal=Decimal('150.00'),
            receita_mensal=Decimal('500.00'),
            margem=Decimal('0.35'),
        )

        self.assertEqual(risco['nivel'], 'alto')
        self.assertGreater(risco['percentual_custo_receita'], Decimal('0.25'))

    def test_share_custo_receita_calculado_corretamente(self):
        risco = calcular_risco_custo_whatsapp(
            custo_mensal=Decimal('25.00'),
            receita_mensal=Decimal('100.00'),
            margem=Decimal('0.75'),
        )

        self.assertEqual(risco['percentual_custo_receita'], Decimal('0.25'))
        self.assertEqual(risco['nivel'], 'alto')

    def test_receita_zero_e_custo_zero_retorna_indefinido(self):
        risco = calcular_risco_custo_whatsapp(
            custo_mensal=Decimal('0.00'),
            receita_mensal=Decimal('0.00'),
            margem=Decimal('0.00'),
        )

        self.assertEqual(risco['percentual_custo_receita'], Decimal('0.00'))
        self.assertEqual(risco['nivel'], 'indefinido')

    def test_receita_zero_com_custo_retorna_alto(self):
        risco = calcular_risco_custo_whatsapp(
            custo_mensal=Decimal('10.00'),
            receita_mensal=Decimal('0.00'),
            margem=Decimal('0.00'),
        )

        self.assertEqual(risco['percentual_custo_receita'], Decimal('1.00'))
        self.assertEqual(risco['nivel'], 'alto')


class RailwayStatusTests(SimpleTestCase):
    def test_status_railway_mostra_custo_real_quando_houver_valor(self):
        status = railway_status(Decimal('12.50'), [])
        self.assertEqual(status['nivel'], 'ok')
        self.assertEqual(status['label'], 'Custo real')

    def test_status_railway_mostra_uso_estimado_quando_nao_houver_custo(self):
        status = railway_status(None, [{'measurement': 'CPU_USAGE', 'estimatedValue': 10}])
        self.assertEqual(status['nivel'], 'info')
        self.assertEqual(status['label'], 'Uso estimado')


class SistemaImagemTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_str_reflete_tipo_variacao_e_status(self):
        imagem = SistemaImagem(
            tipo='logo',
            variacao='original',
            descricao='Logo principal',
            imagem=gerar_png_upload(),
            ativo=True,
        )

        self.assertIn('Logo do Gereigreja', str(imagem))
        self.assertIn('✓', str(imagem))

    def test_save_ativa_chama_desativacao(self):
        imagem = SistemaImagem(
            tipo='logo',
            variacao='original',
            descricao='Logo principal',
            imagem=gerar_png_upload(),
            ativo=True,
        )

        with patch.object(SistemaImagem, 'desativar_outras_versoes') as desativar_mock, \
             patch('django.db.models.Model.save') as model_save_mock:
            imagem.save()

        desativar_mock.assert_called_once()
        model_save_mock.assert_called_once()

    def test_formulario_aceita_png_valido(self):
        form = SistemaImagemForm(
            data={
                'tipo': 'logo',
                'variacao': 'original',
                'descricao': 'Logo válida',
                'largura': '',
                'altura': '',
                'notas': 'Teste',
            },
            files={'imagem': gerar_png_upload()},
        )

        self.assertTrue(form.is_valid(), form.errors.as_text())

    def test_galeria_requer_login(self):
        request = self.factory.get(reverse('painel_desenvolvedor:galeria_imagens'))
        request.user = SimpleNamespace(is_authenticated=False)

        response = galeria_imagens(request)

        self.assertEqual(response.status_code, 302)

    def test_galeria_permite_staff_autenticado(self):
        request = self.factory.get(reverse('painel_desenvolvedor:galeria_imagens'))
        request.user = SimpleNamespace(is_authenticated=True, is_staff=True, is_superuser=False)

        dummy_items = DummyQuerySet([
            SistemaImagem(
                tipo='logo',
                variacao='original',
                descricao='Logo principal',
                imagem=gerar_png_upload(),
                ativo=True,
            )
        ])

        with patch('painel_desenvolvedor.views.SistemaImagem.objects.all', return_value=dummy_items), \
             patch('painel_desenvolvedor.views.Paginator', DummyPaginator), \
             patch('painel_desenvolvedor.views.render', return_value=HttpResponse('Galeria de Imagens')):
            response = galeria_imagens(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Galeria de Imagens')
