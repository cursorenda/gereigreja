# secretaria/admin.py
from django.contrib import admin
from .models import Membro, Pessoa, TipoPessoa, StatusPessoa, StatusHistorico, Contatos, InfoEclesiastica, Familia, Filhos, Observacoes, Cargo, MembroCargo, GrupoCasa, VisitaGrupoCasa, Tag, TransferenciaMembro # Adicionado Tag
# Admin para Tag de Pessoa
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cor', 'descricao')
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)
from django.utils.html import format_html # Para exibir a imagem


# O admin para Tiposstatus (antigo) não é mais necessário.
# Vamos registrar os novos modelos TipoPessoa e StatusPessoa.

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




# --- Admin para Membro (atualizado para mostrar/filtrar pelo flag) ---
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
# Admin para o modelo de acompanhamento de visita
from .models import AcompanhamentoVisita

@admin.register(AcompanhamentoVisita)
class AcompanhamentoVisitaAdmin(admin.ModelAdmin):
    list_display = ('membro', 'data', 'responsavel', 'tipo_contato', 'resultado')
    list_filter = ('tipo_contato', 'responsavel', 'data')
    search_fields = ('membro__nome', 'resultado', 'observacao')
    autocomplete_fields = ['membro', 'responsavel', 'visita_grupo_casa']
    ordering = ('-data',)
    list_per_page = 25 # Define quantos acompanhamentos por página no admin


@admin.register(StatusHistorico)
class StatusHistoricoAdmin(admin.ModelAdmin):
    list_display = ('membro', 'tipo_pessoa_anterior', 'tipo_pessoa_novo', 'status_pessoa_anterior', 'status_pessoa_novo', 'data_transicao', 'registrado_por')
    list_filter = ('data_transicao', 'registrado_por', 'tipo_pessoa_novo', 'status_pessoa_novo')
    search_fields = ('membro__nome', 'registrado_por__username')
    readonly_fields = ('data_transicao',)
    autocomplete_fields = ['membro', 'tipo_pessoa_anterior', 'tipo_pessoa_novo', 'status_pessoa_anterior', 'status_pessoa_novo', 'registrado_por']
    ordering = ('-data_transicao',)



# Admin para o novo modelo Cargo
@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'grupo_permissao')
    search_fields = ('nome',)
    autocomplete_fields = ['grupo_permissao']
    list_filter = ('grupo_permissao',)


# Admin para GrupoCasa
@admin.register(GrupoCasa)
class GrupoCasaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'igreja', 'rua', 'numero', 'cidade', 'cep', 'responsavel', 'qtd_pessoas')
    search_fields = ('nome', 'rua', 'cidade', 'cep')
    list_filter = ('igreja', 'cidade')
    autocomplete_fields = ['responsavel', 'igreja']

    def qtd_pessoas(self, obj):
        return obj.pessoas.count()
    qtd_pessoas.short_description = 'Quantidade de Pessoas'


# Admin para VisitaGrupoCasa
@admin.register(VisitaGrupoCasa)
class VisitaGrupoCasaAdmin(admin.ModelAdmin):
    list_display = ('grupo_casa', 'data', 'responsavel', 'tipo', 'num_membros')
    list_filter = ('tipo', 'responsavel', 'data')
    search_fields = ('grupo_casa__nome', 'grupo_casa__rua')
    autocomplete_fields = ['grupo_casa', 'responsavel']

# Admin para o novo modelo MembroCargo
@admin.register(MembroCargo)
class MembroCargoAdmin(admin.ModelAdmin):
    list_display = ('membro', 'cargo', 'data_inicio', 'data_fim')
    search_fields = ('membro__nome', 'cargo__nome')
    autocomplete_fields = ['membro', 'cargo']
    list_filter = ('cargo',)


@admin.register(TransferenciaMembro)
class TransferenciaMembroAdmin(admin.ModelAdmin):
    list_display = (
        'membro',
        'igreja_origem',
        'igreja_destino',
        'status',
        'data_solicitacao',
        'usuario_solicitante',
        'data_aprovacao',
        'usuario_aprovador',
    )
    list_filter = ('status', 'igreja_origem', 'igreja_destino')
    search_fields = ('membro__nome', 'motivo', 'observacao')
    autocomplete_fields = ['membro', 'igreja_origem', 'igreja_destino', 'usuario_solicitante', 'usuario_aprovador']
    readonly_fields = ('data_solicitacao', 'data_aprovacao')
    ordering = ('-data_solicitacao',)
# admin.site.register(Contatos)
# admin.site.register(Eventos)
# admin.site.register(EventosParticipacao)
# admin.site.register(Familia)
# admin.site.register(Filhos)
# admin.site.register(InfoEclesiastica)
# admin.site.register(Observacoes)
# admin.site.register(OutrosFamiliares)
# StatusHistorico já registrado com @admin.register

