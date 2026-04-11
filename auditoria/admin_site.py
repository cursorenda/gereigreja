from django.contrib import admin
from django.urls import path

from . import views


class AuditoriaAdminSite(admin.AdminSite):
    site_header = 'Auditoria de Permissoes'
    site_title = 'Auditoria de Permissoes'
    index_title = 'Auditoria de Permissoes'
    index_template = 'admin/auditoria_index.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('auditar/', self.admin_view(views.auditar_permissoes_view), name='auditar_permissoes'),
        ]
        return custom_urls + urls


auditoria_admin_site = AuditoriaAdminSite(name='auditoria_admin')
