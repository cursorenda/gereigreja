"""Admin para modelos de catalogo: categorias e fornecedores."""
from django.contrib import admin

from .models import CategoriaDespesa, Fornecedor


@admin.register(CategoriaDespesa)
class CategoriaDespesaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ministerio', 'padrao_global')
    list_filter = ('ministerio', 'padrao_global')
    search_fields = ('nome', 'ministerio__nome_fantasia')
    autocomplete_fields = ['ministerio']


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ministerio', 'cnpj_cpf', 'ativo', 'padrao_global')
    list_filter = ('ministerio', 'ativo', 'padrao_global')
    search_fields = ('nome', 'cnpj_cpf', 'ministerio__nome_fantasia')
    autocomplete_fields = ['ministerio']
