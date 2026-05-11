"""Admin para avisos e notificacoes."""
from django.contrib import admin

from core.admin_mixins import MinisterioFilteredMixin, TimestampReadOnlyMixin

from .models import Aviso


@admin.register(Aviso)
class AvisoAdmin(MinisterioFilteredMixin, TimestampReadOnlyMixin, admin.ModelAdmin):
    list_display = ('titulo', 'ministerio', 'autor_username', 'data_publicacao', 'publicado', 'data_expiracao', 'destino_display')
    list_filter = ('publicado', 'ministerio', 'data_publicacao', 'data_expiracao')
    search_fields = ('titulo', 'conteudo', 'autor__username', 'ministerio__nome_fantasia')
    autocomplete_fields = ['ministerio', 'autor']
    filter_horizontal = ('igrejas_destino',)
    readonly_fields = ('data_publicacao',)

    fieldsets = (
        (None, {'fields': ('ministerio', 'titulo', 'conteudo', 'autor')}),
        ('Publicacao e Visibilidade', {'fields': ('publicado', 'igrejas_destino', 'data_expiracao')}),
        ('Datas', {'fields': ('data_publicacao',)}),
    )

    def autor_username(self, obj):
        return obj.autor.username if obj.autor else '-'
    autor_username.short_description = 'Autor'

    def destino_display(self, obj):
        return ", ".join([igreja.nome_igreja for igreja in obj.igrejas_destino.all()]) or "Toda Ministerio"
    destino_display.short_description = 'Destino'
