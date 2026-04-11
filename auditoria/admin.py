from django.contrib import admin
from django.contrib.auth.models import User

from .models import AccessDeniedLog, AuditSession, PermissionChangeLog


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class UserAuditAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_staff', 'is_superuser', 'list_groups')
    search_fields = ('username',)
    list_filter = ('is_staff', 'is_superuser')

    def list_groups(self, obj):
        return ', '.join(g.name for g in obj.groups.all())

    list_groups.short_description = 'Grupos'


@admin.register(PermissionChangeLog)
class PermissionChangeLogAdmin(admin.ModelAdmin):
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
    date_hierarchy = 'data_hora'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(AccessDeniedLog)
class AccessDeniedLogAdmin(admin.ModelAdmin):
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
    date_hierarchy = 'data_hora'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(AuditSession)
class AuditSessionAdmin(admin.ModelAdmin):
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
    date_hierarchy = 'login_data_hora'

    def duracao_display(self, obj):
        return str(obj.duracao)

    duracao_display.short_description = 'Duracao'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
