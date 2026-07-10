from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q

from configuracao.models import Ministerio
from secretaria.models import Igreja

from .managers import (
    HinoGlobalManager,
    HinoDaIgrejaManager,
    HinoAuditLogManager,
    SoftDeleteQuerySet,
)


class HinoTema(models.Model):
    """Taxonomia de temas para facilitar filtros de culto e liturgia."""

    nome = models.CharField(
        max_length=80,
        unique=True,
        verbose_name='Nome do tema',
    )
    slug = models.SlugField(
        max_length=80,
        unique=True,
        verbose_name='Slug',
        help_text='Identificador curto para filtros e URLs.',
    )
    descricao = models.CharField(
        max_length=180,
        blank=True,
        null=True,
        verbose_name='Descrição',
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo?',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
    )

    class Meta:
        verbose_name = 'Tema de Hino'
        verbose_name_plural = 'Temas de Hino'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['ativo']),
        ]

    def __str__(self):
        return self.nome


class HinoGlobal(models.Model):
    """
    Catálogo global de hinos.

    Funciona como base compartilhada entre todas as igrejas.
    Oferece suporte a compliance jurídico com bloqueio de conteúdo protegido por padrão.
    """

    # Metadados de conteúdo
    colecao = models.CharField(
        max_length=100,
        default='Harpa Cristã',
        verbose_name='Coleção',
        help_text='Ex.: Harpa Cristã, Corinhos, Cantor Cristão',
    )
    numero = models.PositiveIntegerField(
        verbose_name='Número do hino',
    )
    titulo = models.CharField(
        max_length=255,
        verbose_name='Título',
    )
    letra = models.TextField(
        verbose_name='Letra completa',
    )
    cifra = models.TextField(
        null=True,
        blank=True,
        verbose_name='Cifra/Tablaturas',
        help_text='Opcional. Cifra para guitarra ou arranjo musical.',
    )
    corinho = models.BooleanField(
        default=False,
        verbose_name='É corinho?',
        help_text='Se marcado, indica que é um corinho em vez de hino completo.',
    )
    idioma = models.CharField(
        max_length=10,
        default='pt-BR',
        verbose_name='Idioma',
    )
    temas = models.ManyToManyField(
        HinoTema,
        blank=True,
        related_name='hinos_globais',
        verbose_name='Temas',
        help_text='Classificação por tema: Adoração, Santa Ceia, Céu, etc.',
    )

    # Estado operacional
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo?',
    )

    # Soft delete
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Deletado em',
        editable=False,
    )

    # Compliance e direitos autorais
    is_public_domain = models.BooleanField(
        default=False,
        verbose_name='Domínio público?',
        help_text='Marca se o conteúdo está em domínio público comprovado.',
    )

    LICENSE_STATUS_CHOICES = [
        ('public_domain', 'Domínio público'),
        ('licensed', 'Licenciado'),
        ('restricted', 'Restrito'),
        ('unknown', 'Desconhecido'),
        ('pending_review', 'Pendente de revisão'),
    ]

    license_status = models.CharField(
        max_length=20,
        choices=LICENSE_STATUS_CHOICES,
        default='pending_review',
        verbose_name='Status de licença',
    )

    rights_holder = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Detentor de direitos',
        help_text='Autor/editora que detém direitos.',
    )

    license_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Referência de licença',
        help_text='URL ou ID de documento que comprove a licença.',
    )

    license_expires_at = models.DateField(
        null=True,
        blank=True,
        verbose_name='Licença expira em',
    )

    legal_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name='Notas legais',
        help_text='Observações sobre restrições, permissões especiais, etc.',
    )

    blocked_for_public_use = models.BooleanField(
        default=True,
        verbose_name='Bloqueado para uso público?',
        help_text='Se marcado, a letra/cifra não será exibida até revisão.',
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hino_global_reviews',
        verbose_name='Revisado por',
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Revisado em',
    )

    # Rastreabilidade de origem
    source_origin = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Origem da fonte',
        help_text='Ex.: DanielLiberato, API externa, etc.',
    )

    source_hash = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        unique=False,
        verbose_name='Hash da origem',
        help_text='Hash para detecção de duplicatas e reprocessamento.',
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
    )

    objects = HinoGlobalManager()

    class Meta:
        verbose_name = 'Hino Global'
        verbose_name_plural = 'Hinos Globais'
        ordering = ['colecao', 'numero']
        constraints = [
            models.UniqueConstraint(
                fields=['colecao', 'numero'],
                condition=Q(deleted_at__isnull=True),
                name='unique_hino_global_colecao_numero',
            ),
        ]
        indexes = [
            models.Index(fields=['colecao', 'numero']),
            models.Index(fields=['ativo', 'blocked_for_public_use']),
            models.Index(fields=['license_status']),
            models.Index(fields=['titulo']),
            models.Index(fields=['deleted_at']),
        ]

    def __str__(self):
        return f"{self.colecao} #{self.numero} - {self.titulo}"

    def clean(self):
        """Validações de negócio."""
        if self.license_status in ['unknown', 'pending_review']:
            if not self.blocked_for_public_use:
                raise ValidationError(
                    'Hinos unknown ou pending_review devem estar bloqueados para uso público.'
                )

    def is_license_expired(self):
        """Retorna True se a licença expirou."""
        if self.license_expires_at is None:
            return False
        return timezone.now().date() > self.license_expires_at

    def can_render_public_text(self):
        """
        Decide se a letra/cifra pode ser exibida publicamente.

        Retorna False se bloqueado, licença expirada ou status unsafe.
        """
        if self.blocked_for_public_use:
            return False
        if self.is_license_expired():
            return False
        if self.license_status in ['unknown', 'pending_review', 'restricted']:
            return False
        return True


class HinoDaIgreja(models.Model):
    """
    Customização de hino por Igreja.

    Permite que cada Igreja customize, mantenha versões próprias e override hinos globais.
    Multi-tenant estrito: Igreja A não pode acessar dados de Igreja B.
    """

    # Tenant
    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.CASCADE,
        related_name='hinos_customizados',
        verbose_name='Igreja',
    )

    # Conteúdo (similar ao HinoGlobal, mas específico da Igreja)
    colecao = models.CharField(
        max_length=100,
        default='Harpa Cristã',
        verbose_name='Coleção',
    )
    numero = models.PositiveIntegerField(
        verbose_name='Número do hino',
    )
    titulo = models.CharField(
        max_length=255,
        verbose_name='Título',
    )
    letra = models.TextField(
        verbose_name='Letra completa',
    )
    cifra = models.TextField(
        null=True,
        blank=True,
        verbose_name='Cifra/Tablaturas',
        help_text='Versão customizada de cifra para esta Igreja.',
    )
    observacoes = models.TextField(
        null=True,
        blank=True,
        verbose_name='Observações',
        help_text='Contexto local, arranjo utilizado, motivos de customização, etc.',
    )
    temas = models.ManyToManyField(
        HinoTema,
        blank=True,
        related_name='hinos_igreja',
        verbose_name='Temas',
        help_text='Classificação por tema: Adoração, Santa Ceia, Céu, etc.',
    )

    # Estado operacional
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo?',
    )
    override_global = models.BooleanField(
        default=True,
        verbose_name='Sobrepõe hino global?',
        help_text='Se marcado, este hino será usado em vez da versão global.',
    )

    # Soft delete
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Deletado em',
        editable=False,
    )

    # Compliance
    license_status = models.CharField(
        max_length=20,
        choices=HinoGlobal.LICENSE_STATUS_CHOICES,
        default='pending_review',
        verbose_name='Status de licença',
    )
    rights_holder = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Detentor de direitos',
    )
    license_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Referência de licença',
    )
    license_expires_at = models.DateField(
        null=True,
        blank=True,
        verbose_name='Licença expira em',
    )
    legal_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name='Notas legais',
    )
    blocked_for_public_use = models.BooleanField(
        default=True,
        verbose_name='Bloqueado para uso público?',
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hino_igreja_reviews',
        verbose_name='Revisado por',
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Revisado em',
    )

    # Auditoria de autoria
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hino_igreja_criados',
        verbose_name='Criado por',
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hino_igreja_alterados',
        verbose_name='Alterado por',
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
    )

    objects = HinoDaIgrejaManager()

    class Meta:
        verbose_name = 'Hino da Igreja'
        verbose_name_plural = 'Hinos da Igreja'
        ordering = ['colecao', 'numero']
        constraints = [
            models.UniqueConstraint(
                fields=['igreja', 'colecao', 'numero'],
                condition=Q(deleted_at__isnull=True),
                name='unique_hino_igreja_tenant_colecao_numero',
            ),
        ]
        indexes = [
            models.Index(fields=['igreja', 'colecao', 'numero']),
            models.Index(fields=['igreja', 'ativo']),
            models.Index(fields=['igreja', 'blocked_for_public_use']),
            models.Index(fields=['deleted_at']),
        ]

    def __str__(self):
        return f"{self.igreja.nome} - {self.colecao} #{self.numero}"

    def clean(self):
        """Validações de negócio."""
        if self.license_status in ['unknown', 'pending_review']:
            if not self.blocked_for_public_use:
                raise ValidationError(
                    'Hinos unknown ou pending_review devem estar bloqueados.'
                )

    def is_license_expired(self):
        """Retorna True se a licença expirou."""
        if self.license_expires_at is None:
            return False
        return timezone.now().date() > self.license_expires_at

    def can_render_public_text(self):
        """Decide se a letra/cifra pode ser exibida publicamente."""
        if self.blocked_for_public_use:
            return False
        if self.is_license_expired():
            return False
        if self.license_status in ['unknown', 'pending_review', 'restricted']:
            return False
        return True


class HinoAuditLog(models.Model):
    """
    Trilha de auditoria para eventos de compliance e alterações de conteúdo.

    Registra mudanças em status jurídico, conteúdo e revisões.
    """

    ACTION_CHOICES = [
        ('created', 'Criado'),
        ('updated', 'Atualizado'),
        ('reviewed', 'Revisado'),
        ('blocked', 'Bloqueado'),
        ('unblocked', 'Desbloqueado'),
        ('imported', 'Importado'),
        ('soft_deleted', 'Deletado (soft)'),
        ('restored', 'Restaurado'),
    ]

    # Tenant
    tenant_igreja = models.ForeignKey(
        Igreja,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hino_audit_logs',
        verbose_name='Igreja (tenant)',
        help_text='None para eventos de HinoGlobal.',
    )

    # Alvo
    target_type = models.CharField(
        max_length=20,
        choices=[('global', 'Global'), ('igreja', 'Igreja')],
        verbose_name='Tipo de alvo',
    )
    target_id = models.PositiveIntegerField(
        verbose_name='ID do alvo',
    )

    # Ação
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Ação',
    )

    # Histórico de mudança
    before_json = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Dados antes',
        help_text='Snapshot em JSON dos dados antes da mudança.',
    )
    after_json = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Dados depois',
        help_text='Snapshot em JSON dos dados depois da mudança.',
    )

    # Rastreabilidade
    actor_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hino_audit_actions',
        verbose_name='Usuário que agiu',
    )
    reason = models.TextField(
        null=True,
        blank=True,
        verbose_name='Motivo',
        help_text='Razão da ação (revisão, bloqueio, etc.).',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ocorrido em',
    )

    objects = HinoAuditLogManager()

    class Meta:
        verbose_name = 'Auditoria de Hino'
        verbose_name_plural = 'Auditorias de Hino'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant_igreja', 'created_at']),
            models.Index(fields=['target_type', 'target_id']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.target_type}#{self.target_id} by {self.actor_user}"
