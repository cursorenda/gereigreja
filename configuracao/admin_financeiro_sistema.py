from django.contrib import admin

from .dev_access import user_is_dev_finance
from .models import CategoriaGastoSistema, GastoSistema


class DevOnlyAdminMixin:
    def has_module_permission(self, request):
        return user_is_dev_finance(request.user)

    def has_view_permission(self, request, obj=None):
        return user_is_dev_finance(request.user)

    def has_add_permission(self, request):
        return user_is_dev_finance(request.user)

    def has_change_permission(self, request, obj=None):
        return user_is_dev_finance(request.user)

    def has_delete_permission(self, request, obj=None):
        return user_is_dev_finance(request.user)


@admin.register(CategoriaGastoSistema)
class CategoriaGastoSistemaAdmin(DevOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('nome', 'slug', 'ordem', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'slug')
    list_editable = ('ordem', 'ativo')


@admin.register(GastoSistema)
class GastoSistemaAdmin(DevOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('data_competencia', 'descricao', 'categoria', 'valor', 'data_pagamento', 'criado_por')
    list_filter = ('categoria', 'data_competencia')
    search_fields = ('descricao', 'observacao')
    autocomplete_fields = ('categoria', 'criado_por')
    readonly_fields = ('criado_em', 'atualizado_em')
