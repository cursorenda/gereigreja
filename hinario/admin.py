from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone

from .models import HinoGlobal, HinoDaIgreja, HinoAuditLog, HinoTema


@admin.register(HinoTema)
class HinoTemaAdmin(admin.ModelAdmin):
    """Admin da taxonomia de temas do hinário."""

    list_display = ('nome', 'slug', 'ativo', 'created_at')
    list_filter = ('ativo', 'created_at')
    search_fields = ('nome', 'slug', 'descricao')
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('nome',)}


@admin.register(HinoGlobal)
class HinoGlobalAdmin(admin.ModelAdmin):
    """Admin para HinoGlobal com filtros de compliance."""

    list_display = (
        'numero',
        'titulo',
        'colecao',
        'license_status_display',
        'blocked_badge',
        'reviewed_badge',
        'ativo',
    )
    list_filter = (
        'colecao',
        'ativo',
        'temas',
        'license_status',
        'blocked_for_public_use',
        'created_at',
    )
    search_fields = ('numero', 'titulo', 'letra')
    readonly_fields = (
        'created_at',
        'updated_at',
        'deleted_at',
        'source_hash',
        'audit_link',
    )
    fieldsets = (
        ('Conteúdo', {
            'fields': (
                'colecao',
                'numero',
                'titulo',
                'letra',
                'cifra',
                'corinho',
                'idioma',
                'temas',
            )
        }),
        ('Estado', {
            'fields': ('ativo', 'deleted_at')
        }),
        ('Compliance e Direitos Autorais', {
            'fields': (
                'license_status',
                'is_public_domain',
                'rights_holder',
                'license_reference',
                'license_expires_at',
                'legal_notes',
                'blocked_for_public_use',
            ),
            'classes': ('collapse',),
        }),
        ('Revisão', {
            'fields': (
                'reviewed_by',
                'reviewed_at',
            ),
        }),
        ('Origem', {
            'fields': (
                'source_origin',
                'source_hash',
            ),
            'classes': ('collapse',),
        }),
        ('Auditoria', {
            'fields': (
                'created_at',
                'updated_at',
                'audit_link',
            ),
            'classes': ('collapse',),
        }),
    )

    actions = ['bloquear_selecionados', 'desbloquear_selecionados']

    def license_status_display(self, obj):
        colors = {
            'public_domain': '#28a745',
            'licensed': '#17a2b8',
            'restricted': '#ffc107',
            'unknown': '#6c757d',
            'pending_review': '#dc3545',
        }
        color = colors.get(obj.license_status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_license_status_display(),
        )
    license_status_display.short_description = 'Status de Licença'

    def blocked_badge(self, obj):
        if obj.blocked_for_public_use:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Bloqueado</span>'
            )
        return format_html(
            '<span style="background: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Público</span>'
        )
    blocked_badge.short_description = 'Acesso'

    def reviewed_badge(self, obj):
        if obj.reviewed_at:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Revisado</span>'
            )
        return format_html(
            '<span style="background: #ffc107; color: black; padding: 3px 10px; border-radius: 3px;">Pendente</span>'
        )
    reviewed_badge.short_description = 'Revisão'

    def audit_link(self, obj):
        """Link para auditoria de compliance."""
        url = reverse('admin:hinario_hinoauditlog_changelist')
        return format_html(
            '<a href="{}?target_type=global&target_id={}" target="_blank">Ver auditoria →</a>',
            url,
            obj.id,
        )
    audit_link.short_description = 'Auditoria'

    def bloquear_selecionados(self, request, queryset):
        """Ação para bloquear hinos selecionados."""
        updated = queryset.update(blocked_for_public_use=True)
        self.message_user(request, f'{updated} hino(s) bloqueado(s) com sucesso.')
    bloquear_selecionados.short_description = 'Bloquear para uso público'

    def desbloquear_selecionados(self, request, queryset):
        """Ação para desbloquear hinos com validação."""
        # Apenas desbloquear se revisado e com licença válida
        today = timezone.now().date()
        validos = queryset.filter(
            reviewed_at__isnull=False,
            license_status__in=['public_domain', 'licensed'],
        ).filter(
            Q(license_expires_at__isnull=True) | Q(license_expires_at__gte=today)
        )
        updated = validos.update(blocked_for_public_use=False)
        self.message_user(request, f'{updated} hino(s) desbloqueado(s).')
    desbloquear_selecionados.short_description = 'Desbloquear (com validação)'


@admin.register(HinoDaIgreja)
class HinoDaIgrejaAdmin(admin.ModelAdmin):
    """Admin para HinoDaIgreja com isolamento tenant."""

    list_display = (
        'numero',
        'titulo',
        'igreja',
        'colecao',
        'override_badge',
        'blocked_badge',
        'ativo',
    )
    list_filter = (
        'igreja',
        'colecao',
        'ativo',
        'temas',
        'override_global',
        'license_status',
        'blocked_for_public_use',
    )
    search_fields = ('numero', 'titulo', 'letra')
    readonly_fields = (
        'created_at',
        'updated_at',
        'deleted_at',
        'created_by',
        'updated_by',
    )

    fieldsets = (
        ('Tenant', {
            'fields': ('igreja',)
        }),
        ('Conteúdo', {
            'fields': (
                'colecao',
                'numero',
                'titulo',
                'letra',
                'cifra',
                'temas',
                'observacoes',
            )
        }),
        ('Estado', {
            'fields': (
                'ativo',
                'override_global',
                'deleted_at',
            )
        }),
        ('Compliance', {
            'fields': (
                'license_status',
                'rights_holder',
                'license_reference',
                'license_expires_at',
                'legal_notes',
                'blocked_for_public_use',
            ),
            'classes': ('collapse',),
        }),
        ('Revisão', {
            'fields': (
                'reviewed_by',
                'reviewed_at',
            ),
        }),
        ('Auditoria', {
            'fields': (
                'created_by',
                'updated_by',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    def override_badge(self, obj):
        if obj.override_global:
            return format_html(
                '<span style="background: #007bff; color: white; padding: 3px 10px; border-radius: 3px;">Override</span>'
            )
        return '-'
    override_badge.short_description = 'Override'

    def blocked_badge(self, obj):
        if obj.blocked_for_public_use:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Bloqueado</span>'
            )
        return format_html(
            '<span style="background: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Público</span>'
        )
    blocked_badge.short_description = 'Acesso'


@admin.register(HinoAuditLog)
class HinoAuditLogAdmin(admin.ModelAdmin):
    """Admin para auditoria de hinos."""

    list_display = (
        'created_at',
        'action',
        'target_type',
        'target_id',
        'tenant_igreja',
        'actor_user',
    )
    list_filter = (
        'action',
        'target_type',
        'tenant_igreja',
        'created_at',
    )
    search_fields = ('target_id', 'reason', 'actor_user__username')
    readonly_fields = (
        'created_at',
        'before_json_pretty',
        'after_json_pretty',
    )

    fieldsets = (
        ('Evento', {
            'fields': (
                'action',
                'target_type',
                'target_id',
                'created_at',
            )
        }),
        ('Tenant', {
            'fields': ('tenant_igreja',)
        }),
        ('Dados', {
            'fields': (
                'before_json_pretty',
                'after_json_pretty',
            )
        }),
        ('Rastreabilidade', {
            'fields': (
                'actor_user',
                'reason',
            ),
        }),
    )

    def before_json_pretty(self, obj):
        import json
        if obj.before_json:
            return format_html(
                '<pre>{}</pre>',
                json.dumps(obj.before_json, indent=2, ensure_ascii=False),
            )
        return '-'
    before_json_pretty.short_description = 'Dados antes'

    def after_json_pretty(self, obj):
        import json
        if obj.after_json:
            return format_html(
                '<pre>{}</pre>',
                json.dumps(obj.after_json, indent=2, ensure_ascii=False),
            )
        return '-'
    after_json_pretty.short_description = 'Dados depois'
