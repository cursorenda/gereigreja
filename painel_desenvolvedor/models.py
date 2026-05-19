"""
Modelos para gerenciamento de ativos do sistema (imagens, logos, ícones).

Este módulo contém o modelo SistemaImagem que centraliza e gerencia
todas as imagens do sistema, permitindo fácil upload, preview e troca
de versões.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator


class SistemaImagem(models.Model):
    """
    Modelo centralizado para gerenciar imagens do sistema.
    
    Permite upload, preview e versionamento de logos, favicons e outros
    ativos visuais. Cada imagem pode ter múltiplos tamanhos/versões.
    
    Atributos:
        tipo: Categoria da imagem (logo, favicon, icone, banner, etc)
        variacao: Variação específica (ex: grande, médio, pequeno)
        descricao: Descrição legível da imagem
        imagem: Arquivo de imagem (jpg, png, svg, ico)
        largura: Largura esperada em pixels
        altura: Altura esperada em pixels
        ativo: Flag indicando se esta é a versão atual em uso
        data_upload: Timestamp do upload
        notas: Observações técnicas ou de design
    """
    
    # Tipos de imagem disponíveis — somente ativos do próprio sistema/plataforma.
    # Logos e imagens de igrejas/ministérios de clientes são gerenciadas em Configuração.
    TIPO_CHOICES = [
        # Identidade da plataforma
        ('logo', _('Logo do Gereigreja')),
        ('favicon', _('Favicon')),
        ('icone_app', _('Ícone da Aplicação')),
        ('padrao_ministerio', _('Imagem Padrão de Ministério')),
        ('padrao_igreja', _('Imagem Padrão de Igreja')),
        # Layout e interface
        ('hero_bg', _('Imagem de Fundo (Hero)')),
        ('icone_menu', _('Ícone de Menu')),
        ('avatar_padrao', _('Avatar Padrão de Usuário')),
        ('placeholder', _('Imagem Placeholder')),
        # Marketing / público
        ('og_image', _('Imagem Open Graph / Social')),
        ('banner_marketing', _('Banner Marketing')),
        ('dashboard_preview', _('Preview do Dashboard')),
        # Outros
        ('outro', _('Outro')),
    ]
    
    # Variações de tamanho padrão
    VARIACAO_CHOICES = [
        ('grande', _('Grande (300x100px ou superior)')),
        ('medio', _('Médio (200x70px)')),
        ('pequeno', _('Pequeno (150x50px ou inferior)')),
        ('1200x630', _('1200x630 (Open Graph)')),
        ('16x16', _('16x16 (favicon)')),
        ('32x32', _('32x32 (favicon alt)')),
        ('64x64', _('64x64 (ícone)')),
        ('128x128', _('128x128 (ícone)')),
        ('256x256', _('256x256 (ícone)')),
        ('original', _('Tamanho Original')),
    ]
    
    # ═══════════════════════════════════════════════════════════════════
    # Campos principais
    # ═══════════════════════════════════════════════════════════════════
    tipo = models.CharField(
        _('Tipo de Imagem'),
        max_length=20,
        choices=TIPO_CHOICES,
        help_text=_('Categoria da imagem no sistema')
    )
    
    variacao = models.CharField(
        _('Variação/Tamanho'),
        max_length=20,
        choices=VARIACAO_CHOICES,
        default='original',
        help_text=_('Tamanho ou variação específica desta imagem')
    )
    
    descricao = models.CharField(
        _('Descrição'),
        max_length=255,
        help_text=_('Ex: "Logo horizontal colorido", "Favicon 32x32 branco"')
    )
    
    imagem = models.FileField(
        _('Arquivo de Imagem'),
        upload_to='sistema/imagens/%Y/%m/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'svg', 'ico', 'gif', 'webp']
            )
        ],
        help_text=_('Formato: JPG, PNG, SVG, ICO, GIF ou WebP')
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # Metadados de dimensões
    # ═══════════════════════════════════════════════════════════════════
    largura = models.PositiveIntegerField(
        _('Largura (px)'),
        null=True,
        blank=True,
        help_text=_('Largura esperada em pixels')
    )
    
    altura = models.PositiveIntegerField(
        _('Altura (px)'),
        null=True,
        blank=True,
        help_text=_('Altura esperada em pixels')
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # Status e controle
    # ═══════════════════════════════════════════════════════════════════
    ativo = models.BooleanField(
        _('Ativo'),
        default=False,
        help_text=_('Marca esta versão como a atual em uso no sistema')
    )
    
    data_upload = models.DateTimeField(
        _('Data de Upload'),
        auto_now_add=True
    )
    
    data_atualizacao = models.DateTimeField(
        _('Data de Atualização'),
        auto_now=True
    )
    
    notas = models.TextField(
        _('Notas Técnicas'),
        blank=True,
        help_text=_('Observações sobre dimensões, formato, ou qualidade')
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # Meta
    # ═══════════════════════════════════════════════════════════════════
    class Meta:
        verbose_name = _('Imagem do Sistema')
        verbose_name_plural = _('Imagens do Sistema')
        ordering = ['-ativo', '-tipo', 'variacao', '-data_upload']
        constraints = [
            models.UniqueConstraint(
                fields=['tipo', 'variacao'],
                condition=models.Q(ativo=True),
                name='uniq_imagem_ativa_por_tipo_variacao',
            ),
        ]
        indexes = [
            models.Index(fields=['tipo', 'ativo']),
            models.Index(fields=['data_upload']),
        ]
    
    def __str__(self) -> str:
        """Representação em string do objeto."""
        label_tipo = self.get_tipo_display()
        label_var = self.get_variacao_display() if self.variacao != 'original' else ''
        ativo_icon = '✓' if self.ativo else ' '
        
        partes = [f'[{ativo_icon}]', label_tipo]
        if label_var:
            partes.append(f'({label_var})')
        
        return ' '.join(filter(None, partes))
    
    def get_dimensoes_display(self) -> str:
        """
        Retorna as dimensões em formato legível.
        
        Returns:
            str: "250x100px" ou "Não informado"
        """
        if self.largura and self.altura:
            return f'{self.largura}x{self.altura}px'
        return _('Não informado')
    
    def get_tamanho_arquivo_kb(self) -> float:
        """
        Retorna o tamanho do arquivo em KB.
        
        Returns:
            float: Tamanho em KB, arredondado a 2 casas decimais
        """
        try:
            if self.imagem:
                return round(self.imagem.size / 1024, 2)
        except Exception:
            # Storages remotos (ex: Cloudinary) podem não expor Content-Length
            pass
        return 0.0
    
    def desativar_outras_versoes(self) -> int:
        """
        Desativa todas as outras versões do mesmo tipo/variação.
        
        Returns:
            int: Número de imagens desativadas
        """
        if not self.ativo:
            return 0
        
        outras = SistemaImagem.objects.filter(
            tipo=self.tipo,
            variacao=self.variacao,
            ativo=True
        ).exclude(pk=self.pk)
        
        quantidade = outras.count()
        outras.update(ativo=False)
        return quantidade
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve save para garantir consistência.
        
        Se marcar como ativo, desativa outras versões do mesmo tipo/variação.
        """
        if self.ativo:
            self.desativar_outras_versoes()
        
        super().save(*args, **kwargs)
    
    @classmethod
    def obter_ativa(cls, tipo: str, variacao: str = 'original') -> 'SistemaImagem | None':
        """
        Obtém a versão ativa de uma imagem específica.
        
        Args:
            tipo (str): Tipo de imagem
            variacao (str): Variação/tamanho (padrão: 'original')
        
        Returns:
            SistemaImagem | None: A imagem ativa ou None
        """
        return cls.objects.filter(
            tipo=tipo,
            variacao=variacao,
            ativo=True
        ).first()
    
    @classmethod
    def obter_todas_por_tipo(cls, tipo: str) -> models.QuerySet:
        """
        Obtém todas as versões de um tipo de imagem.
        
        Args:
            tipo (str): Tipo de imagem
        
        Returns:
            QuerySet: Todas as variações deste tipo, ordenadas por ativo/data
        """
        return cls.objects.filter(tipo=tipo).order_by('-ativo', '-data_upload')
