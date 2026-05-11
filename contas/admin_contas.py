"""Admin para contas, convites e auditoria de consentimento."""
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from core.admin_mixins import DateHierarchyMixin, ReadOnlyAdminMixin
from contas.constants import GRUPOS_TODOS

from .models import ConsentimentoLGPD, Convite, NotaUsuario


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdminProtegido(GroupAdmin):
    """Permite editar permissoes, mas protege nomes de grupos centralizados."""

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj and obj.name in GRUPOS_TODOS and 'name' not in readonly:
            readonly.append('name')
        return readonly

    def has_delete_permission(self, request, obj=None):
        # Impede exclusao de grupos padrao do sistema.
        if obj and obj.name in GRUPOS_TODOS:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Convite)
class ConviteAdmin(admin.ModelAdmin):
    """Configuracao do Admin para o modelo Convite"""
    list_display = (
        'email_convidado',
        'ministerio',
        'status',
        'remetente',
        'data_criacao',
        'data_aceite',
        'token'
    )
    list_filter = ('status', 'ministerio', 'data_criacao')
    search_fields = (
        'email_convidado',
        'ministerio__nome_fantasia',
        'remetente__username',
        'remetente__email'
    )
    readonly_fields = ('token', 'data_criacao', 'data_aceite')
    ordering = ('-data_criacao',)


@admin.register(NotaUsuario)
class NotaUsuarioAdmin(DateHierarchyMixin, admin.ModelAdmin):
    """Configuracao do Admin para o modelo NotaUsuario"""
    list_display = (
        'usuario',
        'get_nome_completo',
        'atualizado_em',
        'criado_em',
        'preview_conteudo'
    )
    list_filter = ('atualizado_em', 'criado_em')
    search_fields = (
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'conteudo'
    )
    readonly_fields = ('criado_em', 'atualizado_em')
    ordering = ('-atualizado_em',)

    def get_nome_completo(self, obj):
        """Retorna o nome completo do usuario"""
        return obj.usuario.get_full_name() or obj.usuario.username
    get_nome_completo.short_description = 'Nome Completo'

    def preview_conteudo(self, obj):
        """Retorna um preview do conteudo da nota"""
        if obj.conteudo:
            return obj.conteudo[:50] + '...' if len(obj.conteudo) > 50 else obj.conteudo
        return '(vazio)'
    preview_conteudo.short_description = 'Preview'


@admin.register(ConsentimentoLGPD)
class ConsentimentoLGPDAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Configuracao do Admin para o modelo ConsentimentoLGPD"""
    list_display = (
        'usuario',
        'get_nome_usuario',
        'aceite_termos',
        'aceite_privacidade',
        'data_consentimento',
        'ip_consentimento',
        'versao_termos',
        'versao_privacidade'
    )
    list_filter = (
        'aceite_termos',
        'aceite_privacidade',
        'data_consentimento',
        'versao_termos',
        'versao_privacidade'
    )
    search_fields = (
        'usuario__username',
        'usuario__email',
        'usuario__first_name',
        'usuario__last_name',
        'ip_consentimento'
    )
    readonly_fields = (
        'usuario',
        'aceite_termos',
        'aceite_privacidade',
        'data_consentimento',
        'ip_consentimento',
        'versao_termos',
        'versao_privacidade',
        'user_agent'
    )
    date_hierarchy = 'data_consentimento'
    ordering = ('-data_consentimento',)

    def get_nome_usuario(self, obj):
        """Retorna o nome completo do usuario"""
        return obj.usuario.get_full_name() or obj.usuario.username
    get_nome_usuario.short_description = 'Nome'
