import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from decimal import Decimal
from financeiro.models import Receitas, Despesas, FechamentoCaixa, CategoriaDespesa
from financeiro.services import FechamentoCaixaService

class FechamentoCaixaServiceTest(TestCase):
    def setUp(self):
        # Criar mocks para Receitas e Despesas, incluindo campos relevantes
        self.mock_receita1 = MagicMock(spec=Receitas)
        self.mock_receita1.valor = Decimal(1000)
        self.mock_receita1.fechado = False
        self.mock_receita1.data = '2024-01-15' 
        self.mock_receita1.categoria = 'dizimo' 

        self.mock_receita2 = MagicMock(spec=Receitas)
        self.mock_receita2.valor = Decimal(500)
        self.mock_receita2.fechado = False
        self.mock_receita2.data = '2024-01-20' 
        self.mock_receita2.categoria = 'oferta' 

        self.mock_despesa1 = MagicMock(spec=Despesas)
        self.mock_despesa1.valor = Decimal(200)
        self.mock_despesa1.fechado = False
        self.mock_despesa1.data = '2024-01-10' 
        self.mock_categoria_despesa = MagicMock(spec=CategoriaDespesa)
        self.mock_categoria_despesa.nome = "Aluguel" 
        self.mock_despesa1.categoria = self.mock_categoria_despesa 


    def test_buscar_dados(self):
        with patch('financeiro.services.Receitas.objects.filter', return_value=[self.mock_receita1, self.mock_receita2]):
            with patch('financeiro.services.Despesas.objects.filter', return_value=[self.mock_despesa1]):
                service = FechamentoCaixaService(data_inicio='2024-01-01', data_fim='2024-01-31')
                receitas, despesas = service.buscar_dados()
                self.assertEqual(len(receitas), 2)
                self.assertEqual(len(despesas), 1)


    def test_calcular_totais(self):
        mock_receitas_queryset = MagicMock()
        mock_receitas_queryset.aggregate.return_value = {'valor__sum': Decimal(1500)}
        mock_despesas_queryset = MagicMock()
        mock_despesas_queryset.aggregate.return_value = {'valor__sum': Decimal(200)}

        service = FechamentoCaixaService(data_inicio='2024-01-01', data_fim='2024-01-31')
        total_entradas, total_saidas, saldo_final = service.calcular_totais(mock_receitas_queryset, mock_despesas_queryset)
        self.assertEqual(total_entradas, Decimal(1500))
        self.assertEqual(total_saidas, Decimal(200))
        self.assertEqual(saldo_final, Decimal(1300))

    @patch('financeiro.services.FechamentoCaixa.objects.create', return_value=MagicMock(spec=FechamentoCaixa))
    def test_fechar_caixa(self, mock_fechamento_create):
        mock_receitas_queryset = MagicMock()
        mock_receitas_queryset.aggregate.return_value = {'valor__sum': Decimal(1500)}
        mock_despesas_queryset = MagicMock()
        mock_despesas_queryset.aggregate.return_value = {'valor__sum': Decimal(200)}

        service = FechamentoCaixaService(data_inicio='2024-01-01', data_fim='2024-01-31')
        total_entradas, total_saidas, saldo_final = service.calcular_totais(mock_receitas_queryset, mock_despesas_queryset)
        fechamento = service.fechar_caixa(total_entradas, total_saidas, saldo_final)
        self.assertIsNotNone(fechamento)
        mock_fechamento_create.assert_called_once()


    def tearDown(self):
        pass

