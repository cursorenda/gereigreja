from django.contrib import admin

from .models import (
    CidadeCatalogo,
    CidadeTraducao,
    Pais,
    PaisTraducao,
    SubdivisaoAdministrativa,
    SubdivisaoTraducao,
)


class PaisTraducaoInline(admin.TabularInline):
    model = PaisTraducao
    extra = 0


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ('codigo_iso2', 'codigo_iso3', 'nome_oficial', 'idioma_padrao', 'ativo')
    search_fields = ('codigo_iso2', 'codigo_iso3', 'nome_oficial', 'nome_curto')
    list_filter = ('ativo', 'idioma_padrao')
    inlines = [PaisTraducaoInline]


class SubdivisaoTraducaoInline(admin.TabularInline):
    model = SubdivisaoTraducao
    extra = 0


@admin.register(SubdivisaoAdministrativa)
class SubdivisaoAdministrativaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'pais', 'nivel', 'ativo')
    search_fields = ('codigo', 'nome', 'pais__nome_oficial')
    list_filter = ('pais', 'nivel', 'ativo')
    autocomplete_fields = ('pais',)
    inlines = [SubdivisaoTraducaoInline]


class CidadeTraducaoInline(admin.TabularInline):
    model = CidadeTraducao
    extra = 0


@admin.register(CidadeCatalogo)
class CidadeCatalogoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'subdivisao', 'pais', 'ativo')
    search_fields = ('nome', 'subdivisao__nome', 'pais__nome_oficial')
    list_filter = ('pais', 'subdivisao', 'ativo')
    autocomplete_fields = ('pais', 'subdivisao')
    inlines = [CidadeTraducaoInline]
