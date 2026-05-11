"""Admin para modelos de estrutura: anos letivos, classes e turmas."""
from django.contrib import admin

from .models import AnoLetivo, Classe, Turma


@admin.register(AnoLetivo)
class AnoLetivoAdmin(admin.ModelAdmin):
    list_display = ("ano", "ativo")
    list_filter = ("ativo",)


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ("nome", "faixa_etaria")


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ("nome", "classe", "ano_letivo")
    list_filter = ("ano_letivo", "classe")
