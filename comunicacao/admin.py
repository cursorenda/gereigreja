from django.contrib import admin
from .models import Aviso, Notificacao

# Register your models here.

@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'organizacao', 'autor_username', 'data_publicacao', 'publicado', 'data_expiracao', 'destino_display')
    list_filter = ('publicado', 'organizacao', 'data_publicacao', 'data_expiracao')
    search_fields = ('titulo', 'conteudo', 'autor__username', 'organizacao__nome_fantasia')
    autocomplete_fields = ['organizacao', 'autor']
    filter_horizontal = ('igrejas_destino',) # Melhor interface para ManyToMany
    readonly_fields = ('data_publicacao',)

    fieldsets = (
        (None, {'fields': ('organizacao', 'titulo', 'conteudo', 'autor')}),
        ('Publicação e Visibilidade', {'fields': ('publicado', 'igrejas_destino', 'data_expiracao')}),
        ('Datas', {'fields': ('data_publicacao',)}),
    )

    def autor_username(self, obj):
        return obj.autor.username if obj.autor else '-'
    autor_username.short_description = 'Autor'

    def destino_display(self, obj):
        return ", ".join([igreja.nome_igreja for igreja in obj.igrejas_destino.all()]) or "Toda Organização"
    destino_display.short_description = 'Destino'


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('user', 'organizacao', 'message', 'notification_type', 'is_read', 'created_at', 'url')
    list_filter = ('is_read', 'notification_type', 'organizacao', 'created_at')
    search_fields = ('user__username', 'message', 'organizacao__nome_fantasia')
    autocomplete_fields = ['user', 'organizacao']
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('user', 'organizacao', 'message', 'notification_type', 'url')}),
        ('Status', {'fields': ('is_read', 'created_at', 'content_type', 'object_id')}),
    )