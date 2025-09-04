from django.contrib import admin
from .models import (
    Receitas, Despesas, CategoriaDespesa, FechamentoCaixa, ContaBancaria,
    Fornecedor, ContaPagar
)

@admin.register(CategoriaDespesa)
class CategoriaDespesaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ministerio', 'padrao_global')
    list_filter = ('ministerio', 'padrao_global')
    search_fields = ('nome', 'ministerio__nome_fantasia')
    autocomplete_fields = ['ministerio']

@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ('nome_identificacao', 'igreja', 'tipo', 'saldo_atual', 'padrao_global')
    list_filter = ('igreja__ministerio', 'igreja', 'tipo', 'padrao_global')
    search_fields = ('nome_identificacao', 'igreja__nome_igreja')
    readonly_fields = ('saldo_atual',)
    autocomplete_fields = ['igreja']

@admin.register(Receitas)
class ReceitasAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'igreja', 'data', 'valor', 'categoria', 'fechado')
    list_filter = ('igreja__ministerio', 'igreja', 'categoria', 'fechado', 'data')
    search_fields = ('observacao', 'membro__nome', 'igreja__nome_igreja')
    autocomplete_fields = ['igreja', 'membro', 'conta_bancaria']
    date_hierarchy = 'data'

@admin.register(Despesas)
class DespesasAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'igreja', 'data', 'valor', 'categoria', 'fechado')
    list_filter = ('igreja__ministerio', 'igreja', 'categoria', 'fechado', 'data')
    search_fields = ('descricao', 'observacao', 'igreja__nome_igreja')
    autocomplete_fields = ['igreja', 'categoria', 'conta_bancaria', 'origem_conta_pagar']
    date_hierarchy = 'data'

@admin.register(FechamentoCaixa)
class FechamentoCaixaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'igreja', 'data_inicio', 'data_fim', 'saldo_final', 'status')
    list_filter = ('igreja__ministerio', 'igreja', 'status')
    search_fields = ('igreja__nome_igreja', 'observacoes')
    readonly_fields = ('total_entradas', 'total_saidas', 'saldo_final')
    autocomplete_fields = ['igreja']

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ministerio', 'cnpj_cpf', 'ativo', 'padrao_global')
    list_filter = ('ministerio', 'ativo', 'padrao_global')
    search_fields = ('nome', 'cnpj_cpf', 'ministerio__nome_fantasia')
    autocomplete_fields = ['ministerio']

@admin.register(ContaPagar)
class ContaPagarAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'fornecedor', 'igreja', 'valor', 'data_vencimento', 'status')
    list_filter = ('status', 'igreja__ministerio', 'igreja', 'data_vencimento')
    search_fields = ('descricao', 'fornecedor__nome', 'igreja__nome_igreja')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    autocomplete_fields = ['ministerio', 'igreja', 'fornecedor', 'categoria', 'conta_debito']
    date_hierarchy = 'data_vencimento'
