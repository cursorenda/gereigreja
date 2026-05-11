from django.contrib import admin
from django.contrib.auth.models import User

from core.admin_mixins import ReadOnlyAdminMixin, DateHierarchyMixin
from .models import AccessDeniedLog, AuditSession, PermissionChangeLog


# NOTE: Estas classes são usadas por auditoria_admin_site (admin_site.py).
# Não são registradas no admin.site global — User é registrado em configuracao/admin.py.
class UserAuditAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_staff', 'is_superuser', 'list_groups')
    search_fields = ('username',)
    list_filter = ('is_staff', 'is_superuser')

    def list_groups(self, obj):
        return ', '.join(g.name for g in obj.groups.all())

    list_groups.short_description = 'Grupos'


class PermissionChangeLogAdmin(ReadOnlyAdminMixin, DateHierarchyMixin, admin.ModelAdmin):
    date_hierarchy = 'data_hora'  # Override mixin default
    list_display = ('data_hora', 'usuario_afetado', 'acao', 'grupo', 'usuario_executor', 'ip_address')
    list_filter = ('acao', 'data_hora', 'ministerio')
    search_fields = ('usuario_afetado__username', 'usuario_executor__username', 'grupo__name', 'observacao')
    readonly_fields = (
        'data_hora',
        'usuario_afetado',
        'grupo',
        'acao',
        'usuario_executor',
        'ip_address',
        'observacao',
        'ministerio',
    )

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class AccessDeniedLogAdmin(ReadOnlyAdminMixin, DateHierarchyMixin, admin.ModelAdmin):
    date_hierarchy = 'data_hora'  # Override mixin default
    list_display = ('data_hora', 'usuario', 'tipo_acesso', 'recurso', 'permissao_requerida', 'ip_address')
    list_filter = ('tipo_acesso', 'data_hora', 'ministerio')
    search_fields = ('usuario__username', 'recurso', 'permissao_requerida', 'url_path')
    readonly_fields = (
        'data_hora',
        'usuario',
        'tipo_acesso',
        'recurso',
        'permissao_requerida',
        'igreja_tentada',
        'ip_address',
        'user_agent',
        'url_path',
        'metodo_http',
        'ministerio',
    )

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class AuditSessionAdmin(ReadOnlyAdminMixin, DateHierarchyMixin, admin.ModelAdmin):
    date_hierarchy = 'login_data_hora'  # Override mixin default
    list_display = ('login_data_hora', 'usuario', 'logout_data_hora', 'duracao_display', 'ativa', 'ip_address', 'paginas_visitadas')
    list_filter = ('login_data_hora', 'ministerio')
    search_fields = ('usuario__username', 'ip_address')
    readonly_fields = (
        'login_data_hora',
        'usuario',
        'logout_data_hora',
        'ip_address',
        'user_agent',
        'ministerio',
        'igreja_ativa',
        'paginas_visitadas',
        'duracao_display',
    )

    def duracao_display(self, obj):
        return str(obj.duracao)

    duracao_display.short_description = 'Duracao'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
