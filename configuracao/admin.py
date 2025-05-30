# c:\Gereigreja\configuracao\admin.py
from django.contrib import admin
# Importar os nomes corretos dos modelos
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Organizacao, Igreja, PerfilUsuario, Plano, AssinaturaOrganizacao # Adicionar Plano e AssinaturaOrganizacao
from .models import AtualizacaoSistema

# --- Admin para Organização ---
@admin.register(Organizacao)
class OrganizacaoAdmin(admin.ModelAdmin):
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
            # Adicionar 'estado' aqui APENAS se você o adicionou ao modelo Organizacao
            'fields': ('cep', 'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado'),
            'classes': ('collapse',)
        }),
    )
    # --- FIM CORREÇÃO ---

# Opção 1: Inline dentro do UserAdmin (preferível)
class PerfilUsuarioInline(admin.StackedInline): # Ou admin.TabularInline
    model = PerfilUsuario
    can_delete = False # Não permitir deletar perfil a partir do User
    verbose_name_plural = 'Perfil e Organização'
    fk_name = 'user'
    # Campos a exibir no inline
    fields = ('organizacao', 'telefone_contato', 'whatsapp_contato', 'foto_perfil', 'igrejas_permitidas') # Adicionando os novos campos
    # Usar filter_horizontal para ManyToManyField fica melhor
    filter_horizontal = ('igrejas_permitidas',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Filtrar organização no dropdown (opcional, mas útil)
        # if db_field.name == "organizacao":
        #     kwargs["queryset"] = Organizacao.objects.order_by('nome_fantasia')
        # Se quiser raw_id_fields para organização no inline:

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
         # Filtrar igrejas permitidas para mostrar apenas as da organização selecionada
         # Isso requer um pouco de Javascript no admin ou uma abordagem mais complexa.
         # Por enquanto, mostra todas as igrejas. O admin precisa ter cuidado.
         if db_field.name == "igrejas_permitidas":
             kwargs["queryset"] = Igreja.objects.order_by('organizacao__nome_fantasia', 'nome_igreja')
         return super().formfield_for_manytomany(db_field, request, **kwargs)
         raw_id_fields = ('organizacao',) # Adicionado para consistência


# Define um novo User admin que inclui o PerfilUsuario inline
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_organizacao') # Adicionar coluna organização
    list_select_related = ('perfil', 'perfil__organizacao') # Otimizar query

    @admin.display(description='Organização', ordering='perfil__organizacao__nome_fantasia')
    def get_organizacao(self, instance):
        if hasattr(instance, 'perfil') and instance.perfil.organizacao:
            return instance.perfil.organizacao.nome_fantasia
        return None

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user_display_name', 'organizacao_nome', 'telefone_contato', 'whatsapp_contato')
    list_filter = ('organizacao__nome_fantasia',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'organizacao__nome_fantasia')
    raw_id_fields = ('user', 'organizacao') # Facilita a seleção de User e Organização
    filter_horizontal = ('igrejas_permitidas',) # Melhor interface para ManyToManyField

    def user_display_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_display_name.short_description = "Usuário"

    def organizacao_nome(self, obj):
        return obj.organizacao.nome_fantasia
    organizacao_nome.short_description = "Organização"



# --- Admin para Igreja (Atualizado e CORRIGIDO) ---
# REMOVIDO o @admin.register(Igreja) solto e o bloco de comentários duplicado daqui

@admin.register(Igreja)
class IgrejaAdmin(admin.ModelAdmin):
    # Verificar se 'responsavel' existe ou se é 'pastor_local' no seu modelo Igreja
    list_display = ('nome_igreja', 'organizacao', 'cidade', 'estado', 'pastor_local') # Ajustado para 'pastor_local' (verifique seu modelo)
    list_filter = ('organizacao', 'estado', 'cidade')
    search_fields = ('nome_igreja', 'pastor_local', 'cidade') # Ajustado para 'pastor_local'
    list_select_related = ('organizacao',)


    # Método para controlar campos readonly (correto como estava)
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('organizacao',)
        else:
            return ()

    # Método para filtrar 'igreja_superior' (correto como estava)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "igreja_superior":
            organizacao_id = request.POST.get('organizacao')
            obj_id = request.resolver_match.kwargs.get('object_id')

            if obj_id: # Editando
                try:
                    igreja_atual = self.get_object(request, obj_id)
                    if igreja_atual and igreja_atual.organizacao:
                        kwargs["queryset"] = Igreja.objects.filter(organizacao=igreja_atual.organizacao).exclude(pk=obj_id)
                    else:
                         kwargs["queryset"] = Igreja.objects.none()
                except Igreja.DoesNotExist:
                     kwargs["queryset"] = Igreja.objects.none()
            elif organizacao_id: # Adicionando (tentativa de pegar do POST)
                 kwargs["queryset"] = Igreja.objects.filter(organizacao_id=organizacao_id)
            else: # Adicionando, sem organização selecionada ainda
                kwargs["queryset"] = Igreja.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# --- NOVAS CLASSES ADMIN PARA PLANOS E ASSINATURAS ---
@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'get_nome_display', 'preco', 'duracao_dias', 'ativo', 'codigo_referencia_gateway')
    list_filter = ('ativo', 'nome')
    search_fields = ('nome', 'descricao', 'codigo_referencia_gateway')
    list_editable = ('preco', 'duracao_dias', 'ativo') # Cuidado ao usar list_editable com muitos dados

@admin.register(AssinaturaOrganizacao)
class AssinaturaOrganizacaoAdmin(admin.ModelAdmin):
    list_display = ('organizacao', 'plano', 'status', 'data_inicio', 'data_fim', 'id_transacao_gateway')
    list_filter = ('status', 'plano', 'data_inicio', 'data_fim')
    search_fields = ('organizacao__nome_fantasia', 'plano__nome', 'id_transacao_gateway')
    autocomplete_fields = ['organizacao', 'plano']
    readonly_fields = ('data_criacao', 'data_atualizacao')
    fieldsets = (
        (None, {
            'fields': ('organizacao', 'plano', 'status')
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
# --- FIM NOVAS CLASSES ADMIN ---