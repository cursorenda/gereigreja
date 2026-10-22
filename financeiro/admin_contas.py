"""Admin para modelos de contas bancarias e permissoes."""
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.forms import ModelForm
from django.http import HttpResponseRedirect

from .authorization import get_finance_write_scope
from .services import (
    _materialize_payable_edit_authorization_events,
    _resolve_locked_payable_policy,
    _validate_payable_domain_integrity,
    _validate_payable_historical_decision_evidence_before_edit,
    apply_payable_authorization_edit_plan,
    build_payable_authorization_edit_snapshot,
    build_payable_material_snapshot_v1,
    compute_payable_material_fingerprint_v1,
    create_payable,
    plan_payable_authorization_after_edit,
    refresh_payable_material_fingerprint,
)
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


class ContaPagarAdminForm(ModelForm):
    class Meta:
        model = ContaPagar
        exclude = (
            'status',
            'data_pagamento',
            'valor_pago',
            'juros_multa',
            'desconto',
            'comprovante',
            'forma_pagamento',
            'conta_debito',
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
            'usuario_criacao',
            'criado_automaticamente',
            'recorrencia_origem',
        )


class ContaPagarAdminEditValidationError(ValidationError):
    """Falha esperada do workflow bloqueado de edição no Django Admin."""


@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ('nome_identificacao', 'igreja', 'tipo', 'saldo_atual', 'padrao_global')
    list_filter = ('igreja__ministerio', 'igreja', 'tipo', 'padrao_global')
    search_fields = ('nome_identificacao', 'igreja__nome_igreja')
    readonly_fields = ('saldo_atual',)
    autocomplete_fields = ['igreja']


@admin.register(ContaPagar)
class ContaPagarAdmin(admin.ModelAdmin):
    change_readonly_fields = (
        'ministerio',
        'competencia',
    )
    change_mutable_fields = (
        'igreja',
        'fornecedor',
        'categoria',
        'descricao',
        'valor',
        'data_vencimento',
        'numero_documento',
        'data_emissao',
        'observacoes',
    )
    form = ContaPagarAdminForm
    list_display = ('descricao', 'fornecedor', 'igreja', 'valor', 'data_vencimento', 'status')
    list_filter = ('status', 'igreja__ministerio', 'igreja', 'data_vencimento')
    search_fields = ('descricao', 'fornecedor__nome', 'igreja__nome_igreja')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    autocomplete_fields = ['ministerio', 'igreja', 'fornecedor', 'categoria', 'conta_debito']
    date_hierarchy = 'data_vencimento'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + self.change_readonly_fields
        return self.readonly_fields

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        try:
            return super().changeform_view(request, object_id, form_url, extra_context)
        except ContaPagarAdminEditValidationError as exc:
            self.message_user(
                request,
                f'Não foi possível salvar a conta: {" ".join(exc.messages)}',
                level=messages.ERROR,
            )
            return HttpResponseRedirect(request.get_full_path())

    def save_model(self, request, obj, form, change):
        if change:
            try:
                with transaction.atomic():
                    locked_payable = (
                        ContaPagar.objects
                        .select_for_update()
                        .select_related(
                            'igreja__ministerio',
                            'fornecedor',
                            'categoria',
                            'conta_debito',
                            'recorrencia_origem',
                            'recorrencia_origem__igreja',
                            'recorrencia_origem__ministerio',
                        )
                        .get(pk=obj.pk)
                    )
                    if locked_payable.status not in {'PEN', 'VEN'}:
                        raise ValidationError(
                            'A edição administrativa só é permitida para contas pendentes ou vencidas.'
                        )

                    allowed_churches = get_finance_write_scope(request.user, locked_payable.ministerio)
                    if not allowed_churches.filter(pk=locked_payable.igreja_id).exists():
                        raise PermissionDenied(
                            'O usuário não possui escopo local explícito para editar esta conta a pagar.'
                        )

                    before = build_payable_authorization_edit_snapshot(locked_payable)
                    financial_status_before = locked_payable.status
                    for field_name in self.change_mutable_fields:
                        setattr(locked_payable, field_name, getattr(obj, field_name))

                    if not allowed_churches.filter(pk=locked_payable.igreja_id).exists():
                        raise PermissionDenied(
                            'O usuário não possui escopo local explícito para a igreja resultante da conta a pagar.'
                        )

                    _validate_payable_domain_integrity(locked_payable)
                    after_material_fingerprint = compute_payable_material_fingerprint_v1(
                        build_payable_material_snapshot_v1(locked_payable),
                    )
                    if before.material_fingerprint != after_material_fingerprint:
                        policy = _resolve_locked_payable_policy(locked_payable.igreja)
                        plan = plan_payable_authorization_after_edit(
                            payable=locked_payable,
                            before=before,
                            policy=policy,
                        )
                        _validate_payable_historical_decision_evidence_before_edit(
                            payable=locked_payable,
                            before=before,
                            plan=plan,
                        )
                        apply_payable_authorization_edit_plan(locked_payable, plan)
                    else:
                        policy = None
                        plan = plan_payable_authorization_after_edit(
                            payable=locked_payable,
                            before=before,
                            policy=None,
                        )
                        refresh_payable_material_fingerprint(locked_payable)

                    locked_payable.full_clean()
                    locked_payable.save()
                    if plan.material_changed:
                        _materialize_payable_edit_authorization_events(
                            payable=locked_payable,
                            before=before,
                            plan=plan,
                            policy=policy,
                            actor=request.user,
                            financial_status_before=financial_status_before,
                            financial_status_after=locked_payable.status,
                        )

                    for field in obj._meta.concrete_fields:
                        setattr(obj, field.attname, getattr(locked_payable, field.attname))
                    obj._state.adding = False
                    obj._state.db = locked_payable._state.db
            except ValidationError as exc:
                raise ContaPagarAdminEditValidationError(exc.messages) from exc
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
            recorrencia_origem=None,
            competencia=obj.competencia,
            criado_automaticamente=False,
            observacoes=obj.observacoes,
            usuario_criacao=request.user,
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
