from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.auth.models import User
from django.urls import path

from . import views
from .admin import AccessDeniedLogAdmin, AuditSessionAdmin, PermissionChangeLogAdmin, UserAuditAdmin
from .models import AccessDeniedLog, AuditSession, PermissionChangeLog


class AuditoriaAdminSite(admin.AdminSite):
    site_header = 'Auditoria de Permissoes'
    site_title = 'Auditoria de Permissoes'
    index_title = 'Auditoria de Permissoes'
    index_template = 'admin/auditoria_index.html'
    enable_nav_sidebar = False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('auditar/', self.admin_view(views.auditar_permissoes_view), name='auditar_permissoes'),
        ]
        return custom_urls + urls


auditoria_admin_site = AuditoriaAdminSite(name='auditoria_admin')


for model, model_admin in [
    (User, UserAuditAdmin),
    (PermissionChangeLog, PermissionChangeLogAdmin),
    (AccessDeniedLog, AccessDeniedLogAdmin),
    (AuditSession, AuditSessionAdmin),
]:
    try:
        auditoria_admin_site.register(model, model_admin)
    except AlreadyRegistered:
        pass
