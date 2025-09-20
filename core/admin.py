from django.contrib import admin
from .models import NotificacaoEnviada

@admin.register(NotificacaoEnviada)
class NotificacaoEnviadaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'titulo', 'destinatario', 'data_envio')
    list_filter = ('tipo', 'data_envio')
    search_fields = ('titulo', 'mensagem', 'destinatario')
    date_hierarchy = 'data_envio'
