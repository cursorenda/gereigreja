"""Admin para modelos de membros, tipos, status, acompanhamento e histórico."""
from django.contrib import admin

from core.admin_mixins import DataTransicaoHierarchyMixin

from .models import AcompanhamentoVisita, Membro, StatusHistorico, StatusPessoa, Tag, TipoPessoa


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cor', 'descricao')
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)


@admin.register(TipoPessoa)
class TipoPessoaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)
    ordering = ('nome',)


@admin.register(StatusPessoa)
class StatusPessoaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cor_associada', 'descricao')
    list_filter = ()
    search_fields = ('nome',)
    ordering = ('nome',)


@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'igreja', 'tipo_pessoa', 'status_pessoa',
        'genero', 'nascimento', 'telefone',
        'data_primeira_visita', 'origem_visita', 'responsavel_acompanhamento', 'status_acompanhamento'
    )
    list_filter = (
        'igreja', 'tipo_pessoa', 'status_pessoa', 'status_acompanhamento',
        'genero', 'estado_civil', 'nascimento', 'tags'
    )
    search_fields = ('nome', 'apelido', 'cpf', 'rg', 'origem_visita', 'observacoes_visita')
    filter_horizontal = ('tags',)


@admin.register(AcompanhamentoVisita)
class AcompanhamentoVisitaAdmin(admin.ModelAdmin):
    list_display = ('membro', 'data', 'responsavel', 'tipo_contato', 'resultado')
    list_filter = ('tipo_contato', 'responsavel', 'data')
    search_fields = ('membro__nome', 'resultado', 'observacao')
    autocomplete_fields = ['membro', 'responsavel', 'visita_grupo_casa']
    ordering = ('-data',)
    list_per_page = 25


@admin.register(StatusHistorico)
class StatusHistoricoAdmin(DataTransicaoHierarchyMixin, admin.ModelAdmin):
    list_display = (
        'membro', 'tipo_pessoa_anterior', 'tipo_pessoa_novo',
        'status_pessoa_anterior', 'status_pessoa_novo',
        'data_transicao', 'registrado_por'
    )
    list_filter = ('data_transicao', 'registrado_por', 'tipo_pessoa_novo', 'status_pessoa_novo')
    search_fields = ('membro__nome', 'registrado_por__username')
    readonly_fields = ('data_transicao',)
    autocomplete_fields = [
        'membro', 'tipo_pessoa_anterior', 'tipo_pessoa_novo',
        'status_pessoa_anterior', 'status_pessoa_novo', 'registrado_por'
    ]
    ordering = ('-data_transicao',)
