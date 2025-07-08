from django.contrib import admin
from .models import Ticket, RespostaTicket

class RespostaTicketInline(admin.TabularInline):
    """
    Permite adicionar e editar respostas diretamente na página de detalhes do Ticket.
    """
    model = RespostaTicket
    extra = 1 # Mostra um campo de resposta em branco por padrão.
    fields = ('autor', 'mensagem')
    readonly_fields = ('data_criacao',)
    # Define o autor da resposta como o usuário logado por padrão
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "autor":
            kwargs["initial"] = request.user.id
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo Ticket.
    """
    list_display = ('id', 'assunto', 'organizacao', 'user', 'area', 'status', 'data_criacao', 'data_atualizacao')
    list_filter = ('status', 'area', 'organizacao')
    search_fields = ('assunto', 'mensagem', 'user__username', 'organizacao__nome_fantasia')
    list_editable = ('status',) # Permite editar o status diretamente na lista!
    readonly_fields = ('user', 'organizacao', 'data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações do Ticket', {
            'fields': ('assunto', 'area', 'status', ('user', 'organizacao'))
        }),
        ('Mensagem Original', {
            'fields': ('mensagem',),
        }),
    )
    
    inlines = [RespostaTicketInline] # Adiciona o formulário de respostas na página do ticket.