from decimal import Decimal
from django.db.models import Sum

from .models import Receitas, Despesas, FechamentoCaixa


class FechamentoCaixaService:
    def __init__(self, data_inicio, data_fim, igreja=None, observacoes=''):
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.igreja = igreja
        self.observacoes = observacoes

    def buscar_dados(self):
        receitas = Receitas.objects.filter(
            data__gte=self.data_inicio,
            data__lte=self.data_fim,
            fechado=False,
        )
        despesas = Despesas.objects.filter(
            data__gte=self.data_inicio,
            data__lte=self.data_fim,
            fechado=False,
        )
        return receitas, despesas

    def calcular_totais(self, receitas_queryset, despesas_queryset):
        total_entradas = receitas_queryset.aggregate(Sum('valor')).get('valor__sum') or Decimal('0')
        total_saidas = despesas_queryset.aggregate(Sum('valor')).get('valor__sum') or Decimal('0')
        saldo_final = total_entradas - total_saidas
        return total_entradas, total_saidas, saldo_final

    def fechar_caixa(self, total_entradas, total_saidas, saldo_final):
        return FechamentoCaixa.objects.create(
            igreja=self.igreja,
            data_inicio=self.data_inicio,
            data_fim=self.data_fim,
            total_entradas=total_entradas,
            total_saidas=total_saidas,
            saldo_final=saldo_final,
            observacoes=self.observacoes,
            status='fechado',
        )
