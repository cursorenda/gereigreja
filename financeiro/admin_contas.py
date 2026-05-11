"""Admin para modelos de contas bancarias e permissoes."""
from django.contrib import admin

from .models import ContaBancaria, ContaPagar, PermissaoCaixa


@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ('nome_identificacao', 'igreja', 'tipo', 'saldo_atual', 'padrao_global')
    list_filter = ('igreja__ministerio', 'igreja', 'tipo', 'padrao_global')
    search_fields = ('nome_identificacao', 'igreja__nome_igreja')
    readonly_fields = ('saldo_atual',)
    autocomplete_fields = ['igreja']


@admin.register(ContaPagar)
class ContaPagarAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'fornecedor', 'igreja', 'valor', 'data_vencimento', 'status')
    list_filter = ('status', 'igreja__ministerio', 'igreja', 'data_vencimento')
    search_fields = ('descricao', 'fornecedor__nome', 'igreja__nome_igreja')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    autocomplete_fields = ['ministerio', 'igreja', 'fornecedor', 'categoria', 'conta_debito']
    date_hierarchy = 'data_vencimento'


@admin.register(PermissaoCaixa)
class PermissaoCaixaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'caixa', 'pode_visualizar', 'pode_transferir', 'pode_editar', 'criado_em')
    list_filter = ('caixa', 'pode_transferir', 'pode_editar')
    search_fields = ('usuario__username', 'caixa__nome_identificacao')
