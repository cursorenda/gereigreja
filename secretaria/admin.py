# secretaria/admin.py
from django.contrib import admin
from .models import Membro, TipoPessoa, StatusPessoa, StatusHistorico, Contatos, InfoEclesiastica, Familia, Filhos, Observacoes, Cargo, MembroCargo # Adicionado StatusHistorico
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
    list_display = ('nome', 'considerar_ativo_relatorios', 'cor_associada', 'descricao')
    list_filter = ('considerar_ativo_relatorios',)
    search_fields = ('nome',)
    ordering = ('nome',)




# --- Admin para Membro (atualizado para mostrar/filtrar pelo flag) ---
@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'igreja', 'tipo_pessoa', 'status_pessoa', 'is_ativo_para_relatorios',
        'genero', 'nascimento', 'telefone',
        'data_primeira_visita', 'origem_visita', 'responsavel_acompanhamento', 'status_acompanhamento'
    )
    list_filter = (
        'igreja', 'tipo_pessoa', 'status_pessoa', 'status_acompanhamento',
        'status_pessoa__considerar_ativo_relatorios', 'genero', 'estado_civil', 'nascimento'
    )
    search_fields = ('nome', 'apelido', 'cpf', 'rg', 'origem_visita', 'observacoes_visita')
# Admin para o modelo de acompanhamento de visita
from .models import AcompanhamentoVisita

@admin.register(AcompanhamentoVisita)
class AcompanhamentoVisitaAdmin(admin.ModelAdmin):
    list_display = ('membro', 'data', 'responsavel', 'tipo_contato', 'resultado')
    list_filter = ('tipo_contato', 'responsavel', 'data')
    search_fields = ('membro__nome', 'resultado', 'observacao')
    autocomplete_fields = ['membro', 'responsavel']
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

# Admin para o novo modelo MembroCargo
@admin.register(MembroCargo)
class MembroCargoAdmin(admin.ModelAdmin):
    list_display = ('membro', 'cargo', 'data_inicio', 'data_fim')
    search_fields = ('membro__nome', 'cargo__nome')
    autocomplete_fields = ['membro', 'cargo']
    list_filter = ('cargo',)
# admin.site.register(Contatos)
# admin.site.register(Eventos)
# admin.site.register(EventosParticipacao)
# admin.site.register(Familia)
# admin.site.register(Filhos)
# admin.site.register(InfoEclesiastica)
# admin.site.register(Observacoes)
# admin.site.register(OutrosFamiliares)
# StatusHistorico já registrado com @admin.register

