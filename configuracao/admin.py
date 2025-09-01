# c:\Gereigreja\configuracao\admin.py
from django.contrib import admin
from django.db import models  # Adicione esta linha
# Importar os nomes corretos dos modelos
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Ministerio, Igreja, PerfilUsuario, Plano, AssinaturaMinisterio # Adicionar Plano e AssinaturaMinisterio
from .models import AtualizacaoSistema
from django.shortcuts import render
from django.urls import path, reverse
import boto3
from . import views
from .models import PerfilUsuario, Ministerio  # ...seus outros modelos
import os  # Adicione esta linha no topo

# --- Admin para Ministério ---
@admin.register(Ministerio)
class MinisterioAdmin(admin.ModelAdmin):
    # --- CORREÇÃO AQUI ---
    # Substituir 'nome' por 'nome_fantasia' e/ou 'razao_social'
    list_display = ('nome_fantasia', 'razao_social', 'cnpj', 'ativo', 'administrador_principal')
    # --- FIM CORREÇÃO ---

    list_filter = ('ativo',) # Remover 'estado' se você não o adicionou ao modelo
    # --- CORREÇÃO AQUI ---
    search_fields = ('nome_fantasia', 'razao_social', 'cnpj', 'administrador_principal__username')
    # --- FIM CORREÇÃO ---

    # --- CORREÇÃO AQUI (se estiver usando fieldsets) ---
    fieldsets = (
        (None, {
            # Usar os novos nomes de campo
            'fields': ('nome_fantasia', 'razao_social', 'administrador_principal', 'ativo')
        }),
        ('Documentos e Contato', {
            'fields': ('cnpj', 'telefone', 'email'),
            'classes': ('collapse',)
        }),
        ('Endereço', {
            # Adicionar 'estado' aqui APENAS se você o adicionou ao modelo Ministerio
            'fields': ('cep', 'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado'),
            'classes': ('collapse',)
        }),
    )
    # --- FIM CORREÇÃO ---
    

# Opção 1: Inline dentro do UserAdmin (preferível)
class PerfilUsuarioInline(admin.StackedInline): # Ou admin.TabularInline
    model = PerfilUsuario
    can_delete = False # Não permitir deletar perfil a partir do User
    verbose_name_plural = 'Perfil e Ministério'
    fk_name = 'user'
    # Campos a exibir no inline
    fields = ('ministerio', 'telefone_contato', 'whatsapp_contato', 'foto_perfil', 'igrejas_permitidas') # Adicionando os novos campos
    # Usar filter_horizontal para ManyToManyField fica melhor
    filter_horizontal = ('igrejas_permitidas',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Filtrar ministério no dropdown (opcional, mas útil)
        # if db_field.name == "ministerio":
        #     kwargs["queryset"] = Ministerio.objects.order_by('nome_fantasia')
        # Se quiser raw_id_fields para ministério no inline:

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
         # Filtrar igrejas permitidas para mostrar apenas as da ministério selecionada
         # Isso requer um pouco de Javascript no admin ou uma abordagem mais complexa.
         # Por enquanto, mostra todas as igrejas. O admin precisa ter cuidado.
         if db_field.name == "igrejas_permitidas":
             kwargs["queryset"] = Igreja.objects.order_by('ministerio__nome_fantasia', 'nome_igreja')
         return super().formfield_for_manytomany(db_field, request, **kwargs)
         raw_id_fields = ('ministerio',) # Adicionado para consistência


# Define um novo User admin que inclui o PerfilUsuario inline
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_ministerio') # Adicionar coluna ministério
    list_select_related = ('perfil', 'perfil__ministerio') # Otimizar query

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


# --- Admin para Igreja (Atualizado e CORRIGIDO) ---
# REMOVIDO o @admin.register(Igreja) solto e o bloco de comentários duplicado daqui

@admin.register(Igreja)
class IgrejaAdmin(admin.ModelAdmin):
    # Verificar se 'responsavel' existe ou se é 'pastor_local' no seu modelo Igreja
    list_display = ('nome_igreja', 'ministerio', 'cidade', 'estado', 'pastor_local') # Ajustado para 'pastor_local' (verifique seu modelo)
    list_filter = ('ministerio', 'estado', 'cidade')
    search_fields = ('nome_igreja', 'pastor_local', 'cidade') # Ajustado para 'pastor_local'
    list_select_related = ('ministerio',)


    # Método para controlar campos readonly (correto como estava)
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('ministerio',)
        else:
            return ()

    # Método para filtrar 'igreja_superior' (correto como estava)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "igreja_superior":
            ministerio_id = request.POST.get('ministerio')
            obj_id = request.resolver_match.kwargs.get('object_id')

            if obj_id: # Editando
                try:
                    igreja_atual = self.get_object(request, obj_id)
                    if igreja_atual and igreja_atual.ministerio:
                        kwargs["queryset"] = Igreja.objects.filter(ministerio=igreja_atual.ministerio).exclude(pk=obj_id)
                    else:
                         kwargs["queryset"] = Igreja.objects.none()
                except Igreja.DoesNotExist:
                     kwargs["queryset"] = Igreja.objects.none()
            elif ministerio_id: # Adicionando (tentativa de pegar do POST)
                 kwargs["queryset"] = Igreja.objects.filter(ministerio_id=ministerio_id)
            else: # Adicionando, sem ministério selecionada ainda
                kwargs["queryset"] = Igreja.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# --- NOVAS CLASSES ADMIN PARA PLANOS E ASSINATURAS ---
@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ('get_nome_display', 'codigo_plano', 'preco_mensal', 'preco_anual', 'limite_membros', 'is_visible', 'ativo')
    list_filter = ('ativo', 'is_visible')
    search_fields = ('nome', 'codigo_plano', 'descricao')
    list_editable = ('preco_mensal', 'preco_anual', 'limite_membros', 'is_visible', 'ativo')
    fieldsets = (
        ('Identificação', {'fields': ('nome', 'codigo_plano', 'descricao')}),
        ('Preços e Visibilidade', {'fields': ('preco_mensal', 'preco_anual', 'is_visible', 'ativo')}),
        ('Limites e Recursos', {'fields': ('limite_membros', 'limite_igrejas', 'permite_modulo_comunicacao', 'suporte_prioritario')}),
        ('Integração (Stripe)', {'fields': ('stripe_price_id_mensal', 'stripe_price_id_anual'), 'classes': ('collapse',)}),
    )
@admin.register(AssinaturaMinisterio)
class AssinaturaMinisterioAdmin(admin.ModelAdmin):
    list_display = ('ministerio', 'plano', 'status', 'ciclo_pagamento', 'data_inicio', 'data_fim')
    list_filter = ('status', 'plano', 'data_inicio', 'data_fim')
    search_fields = ('ministerio__nome_fantasia', 'plano__nome', 'id_transacao_gateway')
    autocomplete_fields = ['ministerio', 'plano']
    readonly_fields = ('data_criacao', 'data_atualizacao')
    fieldsets = (
        (None, {
            'fields': ('ministerio', 'plano', 'status', 'ciclo_pagamento')
        }),
        ('Período da Assinatura', {
            'fields': ('data_inicio', 'data_fim')
        }),
        ('Detalhes do Gateway (Opcional)', {
            'fields': ('id_transacao_gateway',),
            'classes': ('collapse',)
        }),
        ('Datas de Sistema', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AtualizacaoSistema)
class AtualizacaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'versao', 'data_publicacao', 'publicado')
    list_filter = ('publicado', 'data_publicacao')
    search_fields = ('titulo', 'conteudo', 'versao')    

# Modificar a classe ValidacaoImagens
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
                # Suas verificações de imagem aqui
                pass
            resultados.append({
                'usuario': perfil.user.get_full_name() or perfil.user.username,
                'ministerio': perfil.ministerio.nome_fantasia,
                'imagem': perfil.foto_perfil,
                'status': status
            })
        return resultados

# Registrar no admin (mova este registro para o final do arquivo)
admin.site.register(ValidacaoImagens, ValidacaoImagensAdmin)