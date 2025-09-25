from django.contrib import admin
from .models import AnoLetivo, Classe, Turma, Aluno, Frequencia, Licao, Avaliacao


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

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("nome", "turma", "ativo")
    list_filter = ("turma", "ativo")
    search_fields = ("nome",)

@admin.register(Frequencia)
class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ("aluno", "data", "presente")
    list_filter = ("data", "presente")

@admin.register(Licao)
class LicaoAdmin(admin.ModelAdmin):
    list_display = ("tema", "turma", "data")
    list_filter = ("turma", "data")

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("aluno", "licao", "nota", "participacao")
    list_filter = ("licao", "participacao")
