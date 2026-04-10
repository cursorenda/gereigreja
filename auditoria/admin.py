from django.contrib import admin

from .models import AccessDeniedLog, AuditSession, PermissionChangeLog


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


@admin.register(AccessDeniedLog)
class AccessDeniedLogAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'usuario', 'tipo_acesso', 'recurso', 'permissao_requerida', 'ministerio')
    list_filter = ('tipo_acesso', 'ministerio', 'data_hora')
    search_fields = ('usuario__username', 'recurso', 'permissao_requerida', 'url_path', 'ip_address')
    autocomplete_fields = ('usuario', 'igreja_tentada', 'ministerio')
    ordering = ('-data_hora',)


@admin.register(AuditSession)
class AuditSessionAdmin(admin.ModelAdmin):
    list_display = ('login_data_hora', 'usuario', 'logout_data_hora', 'ativa', 'ministerio', 'paginas_visitadas')
    list_filter = ('ministerio', 'login_data_hora', 'logout_data_hora')
    search_fields = ('usuario__username', 'ip_address', 'user_agent')
    autocomplete_fields = ('usuario', 'ministerio', 'igreja_ativa')
    ordering = ('-login_data_hora',)
