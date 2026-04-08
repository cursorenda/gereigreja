from django.contrib import admin
from django.urls import path
from . import views

class AuditoriaAdminSite(admin.AdminSite):
    site_header = 'Auditoria de Permissões'
    site_title = 'Auditoria de Permissões'
    index_title = 'Auditoria de Permissões'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('auditar/', self.admin_view(views.auditar_permissoes_view), name='auditar_permissoes'),
        ]
        return custom_urls + urls

auditoria_admin_site = AuditoriaAdminSite(name='auditoria_admin')
