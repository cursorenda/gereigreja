# secretaria/admin.py
from django.contrib import admin
from .models import Membro, TipoPessoa, StatusPessoa, StatusHistorico, Contatos, InfoEclesiastica, Familia, Filhos, Observacoes, MembrosCargos, Cargos # Adicionado StatusHistorico
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
        'nome', 'igreja', 
        'tipo_pessoa', # Novo campo
        'status_pessoa', # Novo campo       
         'is_ativo_para_relatorios', # Mostra o resultado da propriedade
        'genero', 'nascimento', 'telefone' # Adicionei telefone como exemplo
    )
    list_filter = (
        'igreja',
        'tipo_pessoa', # Novo campo
        'status_pessoa', # Novo campo
        'status_pessoa__considerar_ativo_relatorios', # Filtra pelo flag DENTRO do novo StatusPessoa
        'genero',
        'estado_civil',
        'nascimento' # <-- Adicionado aqui

    )
    search_fields = ('nome', 'apelido', 'cpf', 'rg')
    raw_id_fields = ('igreja', 'tipo_pessoa', 'status_pessoa') # Atualizado para novos campos
    #date_hierarchy = 'nascimento' # Navegação por data
    readonly_fields = ('is_ativo_para_relatorios',) # A propriedade não é editável aqui
    ordering = ('nome',)
    list_per_page = 25 # Define quantos membros por página no admin


@admin.register(StatusHistorico)
class StatusHistoricoAdmin(admin.ModelAdmin):
    list_display = ('membro', 'tipo_pessoa_anterior', 'tipo_pessoa_novo', 'status_pessoa_anterior', 'status_pessoa_novo', 'data_transicao', 'registrado_por')
    list_filter = ('data_transicao', 'registrado_por', 'tipo_pessoa_novo', 'status_pessoa_novo')
    search_fields = ('membro__nome', 'registrado_por__username')
    readonly_fields = ('data_transicao',)
    autocomplete_fields = ['membro', 'tipo_pessoa_anterior', 'tipo_pessoa_novo', 'status_pessoa_anterior', 'status_pessoa_novo', 'registrado_por']
    ordering = ('-data_transicao',)

# --- Registre os outros modelos se desejar (descomente/adicione conforme necessário) ---

@admin.register(Cargos)
class CargosAdmin(admin.ModelAdmin):
    list_display = ('cargo', 'grupo_permissao')
    search_fields = ('cargo',)
    autocomplete_fields = ['grupo_permissao']
    list_filter = ('grupo_permissao',)
# admin.site.register(Contatos)
# admin.site.register(Eventos)
# admin.site.register(EventosParticipacao)
# admin.site.register(Familia)
# admin.site.register(Filhos)
# admin.site.register(InfoEclesiastica)
# admin.site.register(MembrosCargos)
# admin.site.register(Observacoes)
# admin.site.register(OutrosFamiliares)
# StatusHistorico já registrado com @admin.register

