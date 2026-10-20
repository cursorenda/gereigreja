"""Admin para modelos de contas bancarias e permissoes."""
from django.contrib import admin

from .services import create_payable, refresh_payable_material_fingerprint
from .models import (
    ContaBancaria,
    ContaPagar,
    DepartamentoCaixa,
    DepartamentoFinanceiro,
    ImportacaoExtratoOFX,
    LancamentoExtratoOFX,
    PermissaoCaixa,
    PoliticaDepartamentoFinanceiro,
)


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
    add_exclude = (
        'status',
        'data_pagamento',
        'valor_pago',
        'juros_multa',
        'desconto',
        'comprovante',
        'authorization_status',
        'authorization_origin',
        'authorization_policy_version',
        'current_material_fingerprint',
        'approved_material_fingerprint',
        'approved_by',
        'approved_at',
        'rejected_by',
        'rejected_at',
        'current_rejection_reason',
    )

    def get_exclude(self, request, obj=None):
        if obj is None:
            return self.add_exclude
        return super().get_exclude(request, obj)

    def save_model(self, request, obj, form, change):
        if change:
            refresh_payable_material_fingerprint(obj)
            super().save_model(request, obj, form, change)
            return

        payable = create_payable(
            ministerio=obj.ministerio,
            igreja=obj.igreja,
            fornecedor=obj.fornecedor,
            categoria=obj.categoria,
            descricao=obj.descricao,
            numero_documento=obj.numero_documento,
            valor=obj.valor,
            data_emissao=obj.data_emissao,
            data_vencimento=obj.data_vencimento,
            conta_debito=obj.conta_debito,
            forma_pagamento=obj.forma_pagamento,
            recorrencia_origem=obj.recorrencia_origem,
            competencia=obj.competencia,
            criado_automaticamente=obj.criado_automaticamente,
            observacoes=obj.observacoes,
            usuario_criacao=obj.usuario_criacao,
            actor=request.user,
        )
        for field in obj._meta.concrete_fields:
            setattr(obj, field.attname, getattr(payable, field.attname))
        obj._state.adding = False
        obj._state.db = payable._state.db


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


@admin.register(DepartamentoFinanceiro)
class DepartamentoFinanceiroAdmin(admin.ModelAdmin):
    list_display = ('nome_exibicao', 'codigo_interno', 'igreja', 'departamento', 'tipo_departamento', 'ativo', 'ordem_exibicao')
    list_filter = ('igreja__ministerio', 'igreja', 'tipo_departamento', 'ativo')
    search_fields = ('nome_exibicao', 'codigo_interno', 'igreja__nome_igreja')
    autocomplete_fields = ['igreja']


@admin.register(DepartamentoCaixa)
class DepartamentoCaixaAdmin(admin.ModelAdmin):
    list_display = ('departamento', 'conta_bancaria', 'is_padrao', 'ativo', 'created_at')
    list_filter = ('departamento__igreja__ministerio', 'departamento__igreja', 'is_padrao', 'ativo')
    search_fields = ('departamento__nome_exibicao', 'conta_bancaria__nome_identificacao')
    autocomplete_fields = ['departamento', 'conta_bancaria']


@admin.register(PoliticaDepartamentoFinanceiro)
class PoliticaDepartamentoFinanceiroAdmin(admin.ModelAdmin):
    list_display = (
        'departamento',
        'exige_nota_fiscal',
        'exige_envio_contabilidade',
        'permite_prestacao_local_simplificada',
        'exige_aprovacao_para_saida',
    )
    list_filter = (
        'departamento__igreja__ministerio',
        'departamento__igreja',
        'exige_nota_fiscal',
        'exige_envio_contabilidade',
        'exige_aprovacao_para_saida',
    )
    search_fields = ('departamento__nome_exibicao', 'departamento__igreja__nome_igreja')
    autocomplete_fields = ['departamento']
