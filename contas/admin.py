# c:\Gereigreja\contas\admin.py
from django.contrib import admin
from .models import Convite # Importe o modelo Convite

@admin.register(Convite)
class ConviteAdmin(admin.ModelAdmin):
    """ Configuração do Admin para o modelo Convite """
    list_display = (
        'email_convidado',
        'organizacao',
        'status',
        'remetente',
        'data_criacao',
        'data_aceite',
        'token' # Mostrar o token pode ser útil para debug
    )
    list_filter = ('status', 'organizacao', 'data_criacao')
    search_fields = (
        'email_convidado',
        'organizacao__nome_fantasia',
        'remetente__username',
        'remetente__email'
    )
    # Campos que não devem ser editáveis diretamente no admin
    readonly_fields = ('token', 'data_criacao', 'data_aceite')
    # Ordenação padrão
    ordering = ('-data_criacao',)

    # Opcional: Filtrar organização por autocomplete se houver muitas
    # autocomplete_fields = ['organizacao', 'remetente']

    # Opcional: Ações administrativas (ex: marcar como expirado)
    # actions = [...]

# Se você tiver outros modelos no app 'contas' para registrar, adicione-os aqui.
