"""Admin para modelos de movimentacao financeira."""
from django.contrib import admin

from core.admin_mixins import MinisterioFilteredMixin, DataHierarchyMixin

from .models import Receitas, Despesas, FechamentoCaixa, LogTransacaoFinanceira


@admin.register(Receitas)
class ReceitasAdmin(MinisterioFilteredMixin, DataHierarchyMixin, admin.ModelAdmin):
    list_display = ('__str__', 'igreja', 'data', 'valor', 'categoria', 'fechado')
    list_filter = ('igreja__ministerio', 'igreja', 'categoria', 'fechado', 'data')
    search_fields = ('observacao', 'membro__nome', 'igreja__nome_igreja')
    autocomplete_fields = ['igreja', 'membro', 'conta_bancaria']
    ordering = ('-data',)


@admin.register(Despesas)
class DespesasAdmin(MinisterioFilteredMixin, DataHierarchyMixin, admin.ModelAdmin):
    list_display = ('descricao', 'igreja', 'data', 'valor', 'categoria', 'fechado')
    list_filter = ('igreja__ministerio', 'igreja', 'categoria', 'fechado', 'data')
    search_fields = ('descricao', 'observacao', 'igreja__nome_igreja')
    autocomplete_fields = ['igreja', 'categoria', 'conta_bancaria', 'origem_conta_pagar']
    ordering = ('-data',)


@admin.register(FechamentoCaixa)
class FechamentoCaixaAdmin(MinisterioFilteredMixin, admin.ModelAdmin):
    list_display = ('__str__', 'igreja', 'data_inicio', 'data_fim', 'saldo_final', 'status')
    list_filter = ('igreja__ministerio', 'igreja', 'status')
    search_fields = ('igreja__nome_igreja', 'observacoes')
    readonly_fields = ('total_entradas', 'total_saidas', 'saldo_final')
    autocomplete_fields = ['igreja']
    date_hierarchy = 'data_inicio'
    ordering = ('-data_inicio',)


@admin.register(LogTransacaoFinanceira)
class LogTransacaoFinanceiraAdmin(MinisterioFilteredMixin, DataHierarchyMixin, admin.ModelAdmin):
    date_hierarchy = 'criado_em'
    list_display = ('criado_em', 'igreja', 'tipo_lancamento', 'acao', 'referencia_modelo', 'referencia_id', 'valor', 'usuario')
    list_filter = ('igreja__ministerio', 'igreja', 'tipo_lancamento', 'acao', 'criado_em')
    search_fields = ('referencia_modelo', 'detalhes', 'usuario__username', 'igreja__nome_igreja')
    readonly_fields = (
        'igreja',
        'usuario',
        'tipo_lancamento',
        'acao',
        'referencia_modelo',
        'referencia_id',
        'valor',
        'detalhes',
        'criado_em',
    )
    autocomplete_fields = ['igreja', 'usuario']

    def has_add_permission(self, request):
        return False
