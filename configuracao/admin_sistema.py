"""Admin para modelos de sistema: atualizações, funil e validação de imagens."""
from django.contrib import admin
from django.shortcuts import render
from django.urls import path

from .models import AtualizacaoSistema, EventoFunil, PerfilUsuario


@admin.register(AtualizacaoSistema)
class AtualizacaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'versao', 'data_publicacao', 'publicado')
    list_filter = ('publicado', 'data_publicacao')
    search_fields = ('titulo', 'conteudo', 'versao')


@admin.register(EventoFunil)
class EventoFunilAdmin(admin.ModelAdmin):
    """Admin técnico de métricas de funil, somente leitura e restrito a superusuário."""
    list_display = ('tipo', 'ministerio', 'plano', 'ciclo_pagamento', 'valor', 'criado_em')
    list_filter = ('tipo', 'ciclo_pagamento', 'criado_em')
    search_fields = (
        'ministerio__nome_fantasia',
        'plano__nome',
        'plano__codigo_plano',
    )
    readonly_fields = ('tipo', 'ministerio', 'plano', 'ciclo_pagamento', 'valor', 'extra', 'criado_em')
    date_hierarchy = 'criado_em'

    def has_module_permission(self, request):
        # Oculta do menu lateral — acesso via dashboard de funil
        return False

    def has_view_permission(self, request, obj=None):
        return bool(request.user and request.user.is_active and request.user.is_superuser)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ValidacaoImagens(PerfilUsuario):
    class Meta:
        proxy = True
        verbose_name = 'Validação de Imagens'
        verbose_name_plural = 'Validações de Imagens'
        app_label = 'configuracao'


class ValidacaoImagensAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.validar_imagens_view), name='configuracao_validacaoimagens_changelist'),
        ]
        return custom_urls + urls

    def validar_imagens_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            'title': 'Validação de Imagens de Perfil',
            'resultados': self.get_imagens_para_validar(),
            'opts': self.model._meta,
        }
        return render(request, 'admin/configuracao/validar_imagens.html', context)

    def get_imagens_para_validar(self):
        resultados = []
        for perfil in PerfilUsuario.objects.filter(foto_perfil__isnull=False):
            status = '✅ OK'
            if perfil.foto_perfil:
                pass
            resultados.append({
                'usuario': perfil.user.get_full_name() or perfil.user.username,
                'ministerio': perfil.ministerio.nome_fantasia,
                'imagem': perfil.foto_perfil,
                'status': status,
            })
        return resultados


admin.site.register(ValidacaoImagens, ValidacaoImagensAdmin)
