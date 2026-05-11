"""Admin para modelos de ministério, igrejas, usuários e perfis."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import ConfiguracaoSistema, Igreja, Ministerio, PerfilUsuario


@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('ministerio', 'ebd_periodo', 'ebd_dia_semana', 'atualizado_em')
    list_filter = ('ebd_periodo', 'ebd_dia_semana')
    search_fields = ('ministerio__nome_fantasia',)
    fieldsets = (
        (None, {
            'fields': ('ministerio', 'ebd_periodo', 'ebd_dia_semana')
        }),
        ('Notificações', {
            'fields': (
                'notificar_eventos',
                'notificar_aniversarios',
                'notificar_pre_cadastro_secretario_pastor',
                'notificar_pre_cadastro_admin',
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(Ministerio)
class MinisterioAdmin(admin.ModelAdmin):
    list_display = (
        'nome_fantasia',
        'razao_social',
        'cnpj',
        'ativo',
        'administrador_principal',
        'ultimo_login_admin',
        'quantidade_membros',
    )
    list_filter = ('ativo',)
    search_fields = ('nome_fantasia', 'razao_social', 'cnpj', 'administrador_principal__username')
    fieldsets = (
        (None, {
            'fields': ('nome_fantasia', 'razao_social', 'administrador_principal', 'ativo')
        }),
        ('Documentos e Contato', {
            'fields': ('cnpj', 'telefone', 'email'),
            'classes': ('collapse',)
        }),
        ('Endereço', {
            'fields': ('cep', 'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Último login do admin', ordering='administrador_principal__last_login')
    def ultimo_login_admin(self, obj):
        if obj.administrador_principal and hasattr(obj.administrador_principal, 'last_login'):
            return obj.administrador_principal.last_login
        return '-'

    @admin.display(description='Qtd. membros')
    def quantidade_membros(self, obj):
        return sum(igreja.membros.count() for igreja in obj.igrejas.all())


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil e Ministério'
    fk_name = 'user'
    fields = ('ministerio', 'telefone_contato', 'whatsapp_contato', 'foto_perfil', 'igrejas_permitidas')
    filter_horizontal = ('igrejas_permitidas',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "igrejas_permitidas":
            kwargs["queryset"] = Igreja.objects.order_by('ministerio__nome_fantasia', 'nome_igreja')
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_ministerio')
    list_select_related = ('perfil', 'perfil__ministerio')

    @admin.display(description='Ministério', ordering='perfil__ministerio__nome_fantasia')
    def get_ministerio(self, instance):
        if hasattr(instance, 'perfil') and instance.perfil.ministerio:
            return instance.perfil.ministerio.nome_fantasia
        return None


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user_display_name', 'ministerio_nome', 'telefone_contato', 'whatsapp_contato')
    list_filter = ('ministerio__nome_fantasia',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'ministerio__nome_fantasia')
    raw_id_fields = ('user', 'ministerio')
    filter_horizontal = ('igrejas_permitidas',)

    def user_display_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_display_name.short_description = "Usuário"

    def ministerio_nome(self, obj):
        return obj.ministerio.nome_fantasia
    ministerio_nome.short_description = "Ministério"


@admin.register(Igreja)
class IgrejaAdmin(admin.ModelAdmin):
    list_display = ('nome_igreja', 'ministerio', 'cidade', 'estado', 'pastor_local')
    list_filter = ('ministerio', 'estado', 'cidade')
    search_fields = ('nome_igreja', 'pastor_local', 'cidade')
    list_select_related = ('ministerio',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('ministerio',)
        return ()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "igreja_superior":
            ministerio_id = request.POST.get('ministerio')
            obj_id = request.resolver_match.kwargs.get('object_id')

            if obj_id:
                try:
                    igreja_atual = self.get_object(request, obj_id)
                    if igreja_atual and igreja_atual.ministerio:
                        kwargs["queryset"] = Igreja.objects.filter(ministerio=igreja_atual.ministerio).exclude(pk=obj_id)
                    else:
                        kwargs["queryset"] = Igreja.objects.none()
                except Igreja.DoesNotExist:
                    kwargs["queryset"] = Igreja.objects.none()
            elif ministerio_id:
                kwargs["queryset"] = Igreja.objects.filter(ministerio_id=ministerio_id)
            else:
                kwargs["queryset"] = Igreja.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Registrar UserAdmin com PerfilUsuarioInline no admin global.
# auditoria/admin.py não registra mais User no admin.site.
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, UserAdmin)
