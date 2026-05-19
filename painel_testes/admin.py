"""Ponto de entrada do admin do app painel_testes."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import SistemaImagem
from .admin_tools import painel_pytest_view  # noqa: F401


@admin.register(SistemaImagem)
class SistemaImagemAdmin(admin.ModelAdmin):
    """
    Admin para gerenciamento de imagens do sistema.
    
    Fornece preview em miniatura, filtros por tipo, busca e edição
    direta dos metadados.
    """
    
    list_display = [
        'thumbnail_preview',
        'descricao',
        'tipo',
        'variacao',
        'ativo_badge',
        'tamanho_arquivo',
        'data_upload',
    ]
    
    list_filter = [
        'tipo',
        'variacao',
        'ativo',
        'data_upload',
    ]
    
    search_fields = [
        'descricao',
        'notas',
    ]
    
    readonly_fields = [
        'data_upload',
        'data_atualizacao',
        'thumbnail_grande',
        'info_tecnica',
    ]
    
    fieldsets = (
        (_('Identificação'), {
            'fields': ('tipo', 'variacao', 'descricao'),
        }),
        (_('Imagem'), {
            'fields': ('imagem', 'thumbnail_grande'),
            'classes': ('wide',),
        }),
        (_('Dimensões'), {
            'fields': ('largura', 'altura'),
            'classes': ('collapse',),
        }),
        (_('Status'), {
            'fields': ('ativo',),
            'description': _('Marque como ativo para usar esta versão no sistema.')
        }),
        (_('Notas'), {
            'fields': ('notas',),
            'classes': ('collapse',),
        }),
        (_('Informações Técnicas'), {
            'fields': ('info_tecnica', 'data_upload', 'data_atualizacao'),
            'classes': ('collapse', 'read-only'),
        }),
    )
    
    actions = ['marcar_como_ativo']
    
    def thumbnail_preview(self, obj: SistemaImagem) -> str:
        """Exibe thumbnail na listagem."""
        if obj.imagem:
            return format_html(
                '<img src="{}" width="60" height="40" style="object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                obj.imagem.url
            )
        return '-'
    thumbnail_preview.short_description = _('Preview')
    
    def thumbnail_grande(self, obj: SistemaImagem) -> str:
        """Exibe thumbnail grande nos detalhes."""
        if obj.imagem:
            return format_html(
                '<div style="text-align: center; margin: 20px 0;">'
                '<img src="{}" style="max-width: 100%; max-height: 300px; border: 1px solid #ddd; border-radius: 8px;" />'
                '</div>',
                obj.imagem.url
            )
        return format_html('<p style="color: #999;">Nenhuma imagem</p>')
    thumbnail_grande.short_description = _('Preview Grande')
    
    def ativo_badge(self, obj: SistemaImagem) -> str:
        """Exibe badge indicando se está ativo."""
        if obj.ativo:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">✓ Ativo</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 3px;">Inativo</span>'
        )
    ativo_badge.short_description = _('Status')
    
    def tamanho_arquivo(self, obj: SistemaImagem) -> str:
        """Exibe tamanho do arquivo em KB."""
        kb = obj.get_tamanho_arquivo_kb()
        return f'{kb} KB'
    tamanho_arquivo.short_description = _('Tamanho')
    
    def info_tecnica(self, obj: SistemaImagem) -> str:
        """Exibe informações técnicas da imagem."""
        dimensoes = obj.get_dimensoes_display()
        tamanho = obj.get_tamanho_arquivo_kb()
        
        return format_html(
            '<div style="background: #f8f9fa; padding: 12px; border-radius: 4px; border-left: 4px solid #007bff;">'
            '<strong>Dimensões:</strong> {}<br />'
            '<strong>Tamanho:</strong> {} KB<br />'
            '<strong>Extensão:</strong> {}<br />'
            '</div>',
            dimensoes,
            tamanho,
            obj.imagem.name.split('.')[-1].upper() if obj.imagem else '-'
        )
    info_tecnica.short_description = _('Informações Técnicas')
    
    def marcar_como_ativo(self, request, queryset):
        """Action para marcar múltiplas imagens como ativas."""
        for imagem in queryset:
            imagem.ativo = True
            imagem.save()
        
        self.message_user(
            request,
            _('✓ Imagens marcadas como ativas. Outras versões foram desativadas.')
        )
    marcar_como_ativo.short_description = _('Marcar selecionadas como ativas')
    
    def save_model(self, request, obj: SistemaImagem, form, change):
        """Sobrescreve save para garantir que apenas uma versão fica ativa."""
        if obj.ativo:
            # Desativar outras versões do mesmo tipo/variação
            SistemaImagem.objects.filter(
                tipo=obj.tipo,
                variacao=obj.variacao,
                ativo=True
            ).exclude(pk=obj.pk if change else None).update(ativo=False)
        
        super().save_model(request, obj, form, change)
