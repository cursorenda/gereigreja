from django.contrib import admin

from .models import PermissionChangeLog


@admin.register(PermissionChangeLog)
class PermissionChangeLogAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'usuario_afetado', 'grupo', 'acao', 'usuario_executor', 'ministerio')
    list_filter = ('acao', 'ministerio', 'grupo', 'data_hora')
    search_fields = (
        'usuario_afetado__username',
        'usuario_afetado__first_name',
        'usuario_afetado__last_name',
        'usuario_executor__username',
        'grupo__name',
        'observacao',
    )
    autocomplete_fields = ('usuario_afetado', 'usuario_executor', 'grupo', 'ministerio')
    ordering = ('-data_hora',)
