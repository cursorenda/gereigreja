"""Admin para modelos de contas bancarias e permissoes."""
from django.contrib import admin

from .models import ContaBancaria, ContaPagar, ImportacaoExtratoOFX, LancamentoExtratoOFX, PermissaoCaixa


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


@admin.register(ImportacaoExtratoOFX)
class ImportacaoExtratoOFXAdmin(admin.ModelAdmin):
    list_display = ('importado_em', 'conta_bancaria', 'arquivo_nome', 'data_inicio', 'data_fim', 'saldo_final', 'usuario')
    list_filter = ('igreja__ministerio', 'igreja', 'conta_bancaria', 'importado_em')
    search_fields = ('arquivo_nome', 'conta_bancaria__nome_identificacao', 'hash_arquivo', 'conta_id')
    readonly_fields = ('hash_arquivo', 'importado_em', 'saldo_final')
    autocomplete_fields = ['conta_bancaria', 'igreja', 'usuario']
    date_hierarchy = 'importado_em'


@admin.register(LancamentoExtratoOFX)
class LancamentoExtratoOFXAdmin(admin.ModelAdmin):
    list_display = ('data', 'importacao', 'tipo', 'valor', 'fit_id', 'conciliado', 'conciliado_tipo', 'conciliado_referencia_id')
    list_filter = ('tipo', 'conciliado', 'importacao__igreja', 'importacao__conta_bancaria')
    search_fields = ('fit_id', 'memo', 'documento', 'importacao__arquivo_nome')
    readonly_fields = (
        'data',
        'tipo',
        'trn_type',
        'valor',
        'fit_id',
        'memo',
        'documento',
        'conciliado',
        'conciliado_tipo',
        'conciliado_referencia_id',
        'conciliado_por',
        'conciliado_em',
    )
    autocomplete_fields = ['importacao']
    date_hierarchy = 'data'
