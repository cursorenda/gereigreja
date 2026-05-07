from django.contrib import admin
from .models import Aviso, WhatsAppConfiguracao, WhatsAppMensagemLog

# Register your models here.

@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ministerio', 'autor_username', 'data_publicacao', 'publicado', 'data_expiracao', 'destino_display')
    list_filter = ('publicado', 'ministerio', 'data_publicacao', 'data_expiracao')
    search_fields = ('titulo', 'conteudo', 'autor__username', 'ministerio__nome_fantasia')
    autocomplete_fields = ['ministerio', 'autor']
    filter_horizontal = ('igrejas_destino',) # Melhor interface para ManyToMany
    readonly_fields = ('data_publicacao',)

    fieldsets = (
        (None, {'fields': ('ministerio', 'titulo', 'conteudo', 'autor')}),
        ('Publicação e Visibilidade', {'fields': ('publicado', 'igrejas_destino', 'data_expiracao')}),
        ('Datas', {'fields': ('data_publicacao',)}),
    )

    def autor_username(self, obj):
        return obj.autor.username if obj.autor else '-'
    autor_username.short_description = 'Autor'

    def destino_display(self, obj):
        return ", ".join([igreja.nome_igreja for igreja in obj.igrejas_destino.all()]) or "Toda Ministério"
    destino_display.short_description = 'Destino'


@admin.register(WhatsAppConfiguracao)
class WhatsAppConfiguracaoAdmin(admin.ModelAdmin):
    list_display = (
        'igreja',
        'ministerio',
        'ativo',
        'numero_envio',
        'session_name',
        'auto_aniversariantes',
        'auto_novos_membros',
    )
    list_filter = ('ativo', 'ministerio', 'auto_aniversariantes', 'auto_novos_membros')
    search_fields = ('igreja__nome_igreja', 'ministerio__nome_fantasia', 'numero_envio', 'session_name')


@admin.register(WhatsAppMensagemLog)
class WhatsAppMensagemLogAdmin(admin.ModelAdmin):
    list_display = ('criado_em', 'tipo', 'status', 'igreja', 'telefone_destino', 'membro')
    list_filter = ('tipo', 'status', 'ministerio', 'igreja')
    search_fields = ('telefone_destino', 'mensagem', 'erro', 'membro__nome')
    readonly_fields = (
        'ministerio',
        'igreja',
        'membro',
        'configuracao',
        'tipo',
        'status',
        'telefone_destino',
        'chat_id',
        'mensagem',
        'resposta_waha',
        'erro',
        'criado_em',
    )
