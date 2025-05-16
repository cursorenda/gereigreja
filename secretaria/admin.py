# secretaria/admin.py
from django.contrib import admin
from .models import ( # Importe todos os modelos que você gerencia aqui
    Membro, Tiposstatus, Cargos, Contatos, Eventos, EventosParticipacao,
    Familia, Filhos, InfoEclesiastica, MembrosCargos, Observacoes,
    OutrosFamiliares, StatusHistorico
)

# --- Admin para Tiposstatus ---
@admin.register(Tiposstatus)
class TiposstatusAdmin(admin.ModelAdmin):
    list_display = ('status', 'considerar_ativo_relatorios') # Mostra o status e o novo campo
    list_editable = ('considerar_ativo_relatorios',) # Permite editar o flag direto na lista
    search_fields = ('status',)
    list_filter = ('considerar_ativo_relatorios',) # Permite filtrar por este campo
    ordering = ('status',) # Mantém a ordem

# --- Admin para Membro (atualizado para mostrar/filtrar pelo flag) ---
@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'igreja', 'status',
        'is_ativo_para_relatorios', # Mostra o resultado da propriedade
        'genero', 'nascimento', 'telefone' # Adicionei telefone como exemplo
    )
    list_filter = (
        'igreja',
        'status', # Filtra pelo objeto Status
        'status__considerar_ativo_relatorios', # Filtra pelo flag DENTRO do Status
        'genero',
        'estado_civil',
        'nascimento' # <-- Adicionado aqui

    )
    search_fields = ('nome', 'apelido', 'cpf', 'rg')
    raw_id_fields = ('igreja', 'status') # Bom para performance com muitos itens
    #date_hierarchy = 'nascimento' # Navegação por data
    readonly_fields = ('is_ativo_para_relatorios',) # A propriedade não é editável aqui
    ordering = ('nome',)
    list_per_page = 25 # Define quantos membros por página no admin

# --- Registre os outros modelos se desejar (descomente/adicione conforme necessário) ---
# admin.site.register(Cargos)
# admin.site.register(Contatos)
# admin.site.register(Eventos)
# admin.site.register(EventosParticipacao)
# admin.site.register(Familia)
# admin.site.register(Filhos)
# admin.site.register(InfoEclesiastica)
# admin.site.register(MembrosCargos)
# admin.site.register(Observacoes)
# admin.site.register(OutrosFamiliares)
# admin.site.register(StatusHistorico)

