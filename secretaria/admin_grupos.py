"""Admin para modelos de estrutura: grupos de casa e visitas."""
from django.contrib import admin

from .models import GrupoCasa, VisitaGrupoCasa


@admin.register(GrupoCasa)
class GrupoCasaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'igreja', 'rua', 'numero', 'cidade', 'cep', 'responsavel', 'qtd_pessoas')
    search_fields = ('nome', 'rua', 'cidade', 'cep')
    list_filter = ('igreja', 'cidade')
    autocomplete_fields = ['responsavel', 'igreja']

    def qtd_pessoas(self, obj):
        return obj.pessoas.count()
    qtd_pessoas.short_description = 'Quantidade de Pessoas'


@admin.register(VisitaGrupoCasa)
class VisitaGrupoCasaAdmin(admin.ModelAdmin):
    list_display = ('grupo_casa', 'data', 'responsavel', 'tipo', 'num_membros')
    list_filter = ('tipo', 'responsavel', 'data')
    search_fields = ('grupo_casa__nome', 'grupo_casa__rua')
    autocomplete_fields = ['grupo_casa', 'responsavel']
