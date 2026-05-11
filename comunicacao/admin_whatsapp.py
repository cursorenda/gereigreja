"""Admin para integracao WhatsApp."""
from django.contrib import admin

from core.admin_mixins import MinisterioFilteredMixin, DateHierarchyMixin

from .models import WhatsAppConfiguracao, WhatsAppConfiguracaoGlobal, WhatsAppMensagemLog


@admin.register(WhatsAppConfiguracaoGlobal)
class WhatsAppConfiguracaoGlobalAdmin(MinisterioFilteredMixin, admin.ModelAdmin):
    list_display = ('ministerio', 'waha_base_url', 'ativo')
    search_fields = ('ministerio__nome_fantasia', 'waha_base_url')


@admin.register(WhatsAppConfiguracao)
class WhatsAppConfiguracaoAdmin(MinisterioFilteredMixin, admin.ModelAdmin):
    list_display = (
        'igreja',
        'ministerio',
        'ativo',
        'numero_envio',
        'session_name',
        'auto_aniversariantes',
        'auto_novos_membros',
    )
    list_filter = ('ativo', 'ministerio', 'auto_aniversariantes', 'auto_novos_membros')
    search_fields = ('igreja__nome_igreja', 'ministerio__nome_fantasia', 'numero_envio', 'session_name')


@admin.register(WhatsAppMensagemLog)
class WhatsAppMensagemLogAdmin(DateHierarchyMixin, admin.ModelAdmin):
    list_display = ('criado_em', 'tipo', 'status', 'igreja', 'telefone_destino', 'membro')
    list_filter = ('tipo', 'status', 'ministerio', 'igreja')
    search_fields = ('telefone_destino', 'mensagem', 'erro', 'membro__nome')
    readonly_fields = (
        'ministerio',
        'igreja',
        'membro',
        'configuracao',
        'tipo',
        'status',
        'telefone_destino',
        'chat_id',
        'mensagem',
        'resposta_waha',
        'erro',
        'criado_em',
    )
    ordering = ('-criado_em',)
