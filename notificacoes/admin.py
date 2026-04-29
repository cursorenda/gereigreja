from django.contrib import admin
from .models import Notificacao, NotificacaoEnviada

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
	list_display = ('user', 'ministerio', 'message', 'notification_type', 'is_read', 'created_at', 'url')
	list_filter = ('is_read', 'notification_type', 'ministerio', 'created_at')
	search_fields = ('user__username', 'message', 'ministerio__nome_fantasia')
	autocomplete_fields = ['user', 'ministerio']
	readonly_fields = ('created_at',)
	fieldsets = (
		(None, {'fields': ('user', 'ministerio', 'message', 'notification_type', 'url')}),
		('Status', {'fields': ('is_read', 'created_at', 'content_type', 'object_id')}),
	)

@admin.register(NotificacaoEnviada)
class NotificacaoEnviadaAdmin(admin.ModelAdmin):
	list_display = ('tipo', 'titulo', 'destinatario', 'data_envio')
	list_filter = ('tipo', 'data_envio')
	search_fields = ('titulo', 'mensagem', 'destinatario')
	date_hierarchy = 'data_envio'
