"""Admin para modelos de ministério, igrejas, usuários e perfis."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils.html import format_html
from django.urls import path, reverse

from .models import ConfiguracaoSistema, Igreja, Ministerio, PerfilUsuario, ModeloCartaRecomendacao


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


@admin.register(ModeloCartaRecomendacao)
class ModeloCartaRecomendacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'escopo', 'tipo', 'ministerio', 'ativo', 'ordem')
    list_filter = ('tipo', 'ativo', 'ministerio')
    search_fields = ('nome', 'codigo', 'template_include', 'ministerio__nome_fantasia')
    ordering = ('ordem', 'nome')
    readonly_fields = ('preview_template_include',)
    fieldsets = (
        (None, {
            'description': (
                'Regras: modelo Padrao deve ficar sem ministerio. '
                'Modelo Exclusivo deve ter ministerio dono definido.'
            ),
            'fields': ('nome', 'codigo', 'template_include', 'tipo', 'ministerio', 'ativo', 'ordem')
        }),
        ('Previa', {
            'fields': ('preview_template_include',),
        }),
    )

    @admin.display(description='Escopo')
    def escopo(self, obj):
        if obj.tipo == ModeloCartaRecomendacao.TIPO_PADRAO:
            return 'Global'
        if obj.ministerio_id:
            return f'Exclusivo de {obj.ministerio.nome_fantasia}'
        return 'Exclusivo (sem ministerio)'

    @admin.display(description='Previa do Template Include')
    def preview_template_include(self, obj):
        if not obj:
            return 'Salve o modelo para habilitar a previa.'

        if not obj.template_include:
            return 'Informe o caminho em Template include para gerar a previa.'

        dados_exemplo = {
            'destino': 'Assembleia de Deus - Cidade Exemplo',
            'nome_irmao': 'Joao da Silva',
            'congregacao': 'Congregacao Central',
            'sub_sede': 'Sub-sede Exemplo',
            'data_emissao': None,
        }

        contexto_previa = {
            'dados': dados_exemplo,
            'nome_igreja': 'Igreja Exemplo',
            'cnpj_igreja': '00.000.000/0001-00',
            'email_igreja': 'contato@exemplo.org',
            'logo_url_1': '',
            'logo_url_2': '',
            'pastor_nome': 'Pr. Nome Exemplo',
            'congregacao_nome': 'Congregacao Central',
            'ministerio_nome': obj.ministerio.nome_fantasia if obj.ministerio_id else 'Ministerio Exemplo',
            'ministerio_email': 'secretaria@ministerio.org',
            'ministerio_telefone': '(00) 00000-0000',
            'ministerio_cnpj': '00.000.000/0001-00',
            'ministerio_endereco': 'Rua Exemplo, 100, Centro, Cidade - UF, 00000-000',
        }

        try:
            html_carta = render_to_string(obj.template_include, contexto_previa)
        except Exception as exc:
            return format_html('<span style="color:#b42318;font-weight:600;">Erro ao renderizar prévia: {}</span>', exc)

        css_url = static('css/documentos/carta_recomendacao.css')
        preview_url = reverse(
            f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_preview',
            args=[obj.pk],
        )
        return format_html(
            '<div style="border:1px solid #d0d5dd;border-radius:10px;overflow:auto;max-height:540px;background:#fff;padding:10px;">'
            '<style>@import url("{}"); .carta-preview-wrap{{max-width:460px;margin:0 auto;}}</style>'
            '<div class="carta-preview-wrap">{}</div>'
            '</div>'
            '<div style="margin-top:10px;">'
            '<a href="{}" target="_blank" style="display:inline-block;padding:8px 12px;border-radius:8px;'
            'text-decoration:none;background:#0d6efd;color:#fff;font-weight:600;">Abrir previa em nova aba</a>'
            '</div>',
            css_url,
            html_carta,
            preview_url,
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:object_id>/preview/',
                self.admin_site.admin_view(self.preview_em_tela_cheia),
                name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_preview',
            ),
        ]
        return custom_urls + urls

    def preview_em_tela_cheia(self, request, object_id):
        obj = get_object_or_404(ModeloCartaRecomendacao, pk=object_id)

        dados_exemplo = {
            'destino': 'Assembleia de Deus - Cidade Exemplo',
            'nome_irmao': 'Joao da Silva',
            'congregacao': 'Congregacao Central',
            'sub_sede': 'Sub-sede Exemplo',
            'data_emissao': None,
        }

        contexto_previa = {
            'dados': dados_exemplo,
            'nome_igreja': 'Igreja Exemplo',
            'cnpj_igreja': '00.000.000/0001-00',
            'email_igreja': 'contato@exemplo.org',
            'logo_url_1': '',
            'logo_url_2': '',
            'pastor_nome': 'Pr. Nome Exemplo',
            'congregacao_nome': 'Congregacao Central',
            'ministerio_nome': obj.ministerio.nome_fantasia if obj.ministerio_id else 'Ministerio Exemplo',
            'ministerio_email': 'secretaria@ministerio.org',
            'ministerio_telefone': '(00) 00000-0000',
            'ministerio_cnpj': '00.000.000/0001-00',
            'ministerio_endereco': 'Rua Exemplo, 100, Centro, Cidade - UF, 00000-000',
        }

        try:
            html_carta = render_to_string(obj.template_include, contexto_previa)
        except Exception as exc:
            return HttpResponse(
                f'<h2>Erro ao renderizar template</h2><pre>{exc}</pre>',
                status=400,
            )

        css_url = static('css/documentos/carta_recomendacao.css')
        page = f'''
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <title>Previa - {obj.nome}</title>
  <style>@import url("{css_url}"); body {{ margin: 0; padding: 18px; background: #f4f6fb; }}</style>
</head>
<body>
  <div class="carta-preview-wrap">{html_carta}</div>
</body>
</html>
'''
        return HttpResponse(page)


@admin.register(Ministerio)
class MinisterioAdmin(admin.ModelAdmin):
    list_display = (
        'nome_fantasia',
        'razao_social',
        'cnpj',
        'modelo_carta_recomendacao',
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
            'fields': ('cnpj', 'telefone', 'email', 'modelo_carta_recomendacao'),
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
