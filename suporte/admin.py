"""Admin para modelo de suporte (tickets)."""
from django.contrib import admin

from core.admin_mixins import DateHierarchyMixin

from .models import RespostaTicket, Ticket


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
class TicketAdmin(DateHierarchyMixin, admin.ModelAdmin):
    """
    Configuração do Admin para o modelo Ticket.
    """
    list_display = ('id', 'assunto', 'ministerio', 'user', 'area', 'status', 'data_criacao', 'data_atualizacao')
    list_filter = ('status', 'area', 'ministerio')
    search_fields = ('assunto', 'mensagem', 'user__username', 'ministerio__nome_fantasia')
    list_editable = ('status',) # Permite editar o status diretamente na lista!
    readonly_fields = ('user', 'ministerio', 'data_criacao', 'data_atualizacao')
    date_hierarchy = 'data_criacao'  # Override mixin default
    
    fieldsets = (
        ('Informações do Ticket', {
            'fields': ('assunto', 'area', 'status', ('user', 'ministerio'))
        }),
        ('Mensagem Original', {
            'fields': ('mensagem',),
        }),
    )
    
    inlines = [RespostaTicketInline] # Adiciona o formulário de respostas na página do ticket.