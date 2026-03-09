# c:\Gereigreja\contas\admin.py
from django.contrib import admin
from .models import Convite, NotaUsuario, ConsentimentoLGPD # Importe o modelo Convite

@admin.register(Convite)
class ConviteAdmin(admin.ModelAdmin):
    """ Configuração do Admin para o modelo Convite """
    list_display = (
        'email_convidado',
        'ministerio',
        'status',
        'remetente',
        'data_criacao',
        'data_aceite',
        'token' # Mostrar o token pode ser útil para debug
    )
    list_filter = ('status', 'ministerio', 'data_criacao')
    search_fields = (
        'email_convidado',
        'ministerio__nome_fantasia',
        'remetente__username',
        'remetente__email'
    )
    # Campos que não devem ser editáveis diretamente no admin
    readonly_fields = ('token', 'data_criacao', 'data_aceite')
    # Ordenação padrão
    ordering = ('-data_criacao',)

    # Opcional: Filtrar ministério por autocomplete se houver muitas
    # autocomplete_fields = ['ministerio', 'remetente']

    # Opcional: Ações administrativas (ex: marcar como expirado)
    # actions = [...]


@admin.register(NotaUsuario)
class NotaUsuarioAdmin(admin.ModelAdmin):
    """ Configuração do Admin para o modelo NotaUsuario """
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
        """Retorna o nome completo do usuário"""
        return obj.usuario.get_full_name() or obj.usuario.username
    get_nome_completo.short_description = 'Nome Completo'
    
    def preview_conteudo(self, obj):
        """Retorna um preview do conteúdo da nota"""
        if obj.conteudo:
            return obj.conteudo[:50] + '...' if len(obj.conteudo) > 50 else obj.conteudo
        return '(vazio)'
    preview_conteudo.short_description = 'Preview'


@admin.register(ConsentimentoLGPD)
class ConsentimentoLGPDAdmin(admin.ModelAdmin):
    """ Configuração do Admin para o modelo ConsentimentoLGPD """
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
    ordering = ('-data_consentimento',)
    
    def get_nome_usuario(self, obj):
        """Retorna o nome completo do usuário"""
        return obj.usuario.get_full_name() or obj.usuario.username
    get_nome_usuario.short_description = 'Nome'
    
    def has_add_permission(self, request):
        """Desabilita a criação manual de consentimentos pelo admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Desabilita a exclusão de consentimentos (auditoria)"""
        return False


# Se você tiver outros modelos no app 'contas' para registrar, adicione-os aqui.
