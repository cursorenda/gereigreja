"""Admin para modelos de aulas e avaliacoes."""
from django.contrib import admin

from core.admin_mixins import DataHierarchyMixin

from .models import Avaliacao, Licao


@admin.register(Licao)
class LicaoAdmin(DataHierarchyMixin, admin.ModelAdmin):
    list_display = ("tema", "turma", "data")
    list_filter = ("turma", "data")


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("aluno", "licao", "nota", "participacao")
    list_filter = ("licao", "participacao")
