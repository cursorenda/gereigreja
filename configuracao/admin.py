# c:\Gereigreja\configuracao\admin.py
from django.contrib import admin
from django.db import models  # Adicione esta linha
# Importar os nomes corretos dos modelos
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Ministerio, Igreja, PerfilUsuario, Plano, AssinaturaMinisterio, ConfiguracaoSistema, LiberacaoPlanoMinisterio, EventoFunil, CodigoPromocional # Adicionar ConfiguracaoSistema
from .models import AtualizacaoSistema
# Admin para ConfiguracaoSistema
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
from django.shortcuts import render
from django.urls import path, reverse
import boto3
from . import views
from .models import PerfilUsuario, Ministerio  # ...seus outros modelos
import os  # Adicione esta linha no topo

# --- Admin para Ministério ---

@admin.register(Ministerio)
class MinisterioAdmin(admin.ModelAdmin):
    # Exibe informações extras para desenvolvedor
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
        # Soma membros de todas as igrejas do ministério
        return sum(igreja.membros.count() for igreja in obj.igrejas.all())

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
         # Filtrar igrejas permitidas para mostrar apenas as do ministério selecionada
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
    list_display = ('get_nome_display', 'codigo_plano', 'preco_mensal', 'preco_anual', 'limite_membros', 'permite_modulo_secretaria', 'permite_modulo_comunicacao', 'permite_suporte_tickets', 'suporte_prioritario', 'is_visible', 'liberado_publicamente', 'contratacao_publica_liberada', 'ativo')
    list_filter = ('ativo', 'is_visible', 'liberado_publicamente', 'contratacao_publica_liberada')
    search_fields = ('nome', 'codigo_plano', 'descricao')
    list_editable = ('preco_mensal', 'preco_anual', 'limite_membros', 'is_visible', 'liberado_publicamente', 'contratacao_publica_liberada', 'ativo')
    fieldsets = (
        ('Identificação', {'fields': ('nome', 'codigo_plano', 'descricao')}),
        ('Preços e Visibilidade', {'fields': ('preco_mensal', 'preco_de_mensal', 'preco_anual', 'preco_de_anual', 'is_visible', 'liberado_publicamente', 'contratacao_publica_liberada', 'ordem_liberacao', 'ativo')}),
        ('Limites e Recursos', {'fields': ('limite_membros', 'limite_igrejas')}),
        ('Módulos e Suporte', {'fields': ('permite_modulo_secretaria', 'permite_modulo_agenda', 'permite_modulo_eventos', 'permite_modulo_escola_biblica', 'permite_modulo_financeiro', 'permite_modulo_comunicacao', 'permite_suporte_tickets', 'suporte_prioritario')}),
        ('Integração (Stripe)', {'fields': ('stripe_product_id', 'stripe_price_id_mensal', 'stripe_price_id_anual'), 'classes': ('collapse',)}),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard-sistema/', self.admin_site.admin_view(self._dashboard_sistema_view), name='configuracao_dashboard_sistema'),
            path('dashboard-funil/', self.admin_site.admin_view(self._dashboard_funil_view), name='configuracao_dashboard_funil'),
        ]
        return custom_urls + urls

    def _dashboard_sistema_view(self, request):
        if not request.user.is_superuser:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Acesso restrito.")
        context = {
            **self.admin_site.each_context(request),
            'title': 'Dashboard do Sistema',
            'opts': self.model._meta,
        }
        return render(request, 'configuracao/dashboard_sistema.html', context)

    def _dashboard_funil_view(self, request):
        if not request.user.is_superuser:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Acesso restrito.")
        from datetime import datetime, timedelta
        from collections import defaultdict
        from django.db.models import Count, Sum, Exists, OuterRef
        from django.db.models.functions import TruncMonth
        from .models import EventoFunil
        try:
            dias = int(request.GET.get('dias', 30))
        except (TypeError, ValueError):
            dias = 30
        if dias not in (7, 30, 90):
            dias = 30
        data_inicio = datetime.now() - timedelta(days=dias)
        eventos = EventoFunil.objects.filter(criado_em__gte=data_inicio)

        # --- KPIs básicos ---
        contagem = {
            'visita_landing': eventos.filter(tipo='visita_landing').count(),
            'clique_cta': eventos.filter(tipo='clique_cta').count(),
            'cadastro': eventos.filter(tipo='cadastro').count(),
            'checkout_iniciado': eventos.filter(tipo='checkout_iniciado').count(),
            'checkout_completo': eventos.filter(tipo='checkout_completo').count(),
        }
        visitas = contagem['visita_landing']
        def _pct(base, alvo):
            return round((alvo / base) * 100, 2) if base else 0
        taxas = {
            'visitas_para_cliques': _pct(visitas, contagem['clique_cta']),
            'cliques_para_cadastros': _pct(contagem['clique_cta'], contagem['cadastro']),
            'cadastros_para_checkout': _pct(contagem['cadastro'], contagem['checkout_iniciado']),
            'checkout_para_pago': _pct(contagem['checkout_iniciado'], contagem['checkout_completo']),
            'visita_para_pago': _pct(visitas, contagem['checkout_completo']),
        }

        # --- Conversões por plano ---
        por_plano = list(
            eventos.filter(tipo='checkout_completo', plano__isnull=False)
            .values('plano__nome')
            .annotate(total=Count('id'), receita=Sum('valor'))
            .order_by('-total')
        )
        receita_total = (
            eventos.filter(tipo='checkout_completo').aggregate(total=Sum('valor')).get('total') or 0
        )
        ticket_medio = (
            round(float(receita_total) / contagem['checkout_completo'], 2)
            if contagem['checkout_completo'] else 0
        )

        # --- Conversão por origem (campo extra->>'origem') ---
        cliques_map = dict(
            eventos.filter(tipo='clique_cta')
            .values('extra__origem')
            .annotate(n=Count('id'))
            .values_list('extra__origem', 'n')
        )
        cadastros_map = dict(
            eventos.filter(tipo='cadastro')
            .values('extra__origem')
            .annotate(n=Count('id'))
            .values_list('extra__origem', 'n')
        )
        origens_keys = sorted(set(list(cliques_map.keys()) + list(cadastros_map.keys())))
        por_origem = []
        for o in origens_keys:
            cl = cliques_map.get(o, 0)
            ca = cadastros_map.get(o, 0)
            por_origem.append({
                'origem': o or '(direto)',
                'cliques': cl,
                'cadastros': ca,
                'taxa': round((ca / cl) * 100, 1) if cl else 0,
            })
        por_origem.sort(key=lambda x: x['cliques'], reverse=True)

        # --- Cohort por mês de cadastro (all-time, sem filtro de dias) ---
        pagou_subq = EventoFunil.objects.filter(
            tipo='checkout_completo',
            ministerio=OuterRef('ministerio'),
        )
        cohort_raw = (
            EventoFunil.objects
            .filter(tipo='cadastro', ministerio__isnull=False)
            .annotate(mes=TruncMonth('criado_em'))
            .annotate(converteu=Exists(pagou_subq))
            .values('mes', 'converteu')
            .annotate(total=Count('id'))
            .order_by('mes', 'converteu')
        )
        cohort_by_month = defaultdict(lambda: {'cadastros': 0, 'convertidos': 0})
        for row in cohort_raw:
            mes = row['mes']
            if row['converteu']:
                cohort_by_month[mes]['convertidos'] += row['total']
            else:
                cohort_by_month[mes]['cadastros'] += row['total']
        cohort = []
        for mes, data in sorted(cohort_by_month.items(), reverse=True):
            total = data['cadastros'] + data['convertidos']
            conv = data['convertidos']
            cohort.append({
                'mes': mes,
                'total': total,
                'convertidos': conv,
                'taxa': round((conv / total) * 100, 1) if total else 0,
            })

        # --- Últimos eventos ---
        ultimos_eventos = eventos.select_related('ministerio', 'plano')[:20]

        context = {
            **self.admin_site.each_context(request),
            'title': 'Funil de Conversão',
            'opts': self.model._meta,
            'dias': dias,
            'contagem': contagem,
            'taxas': taxas,
            'por_plano': por_plano,
            'receita_total': receita_total,
            'ticket_medio': ticket_medio,
            'por_origem': por_origem,
            'cohort': cohort,
            'ultimos_eventos': ultimos_eventos,
        }
        return render(request, 'configuracao/dashboard_funil.html', context)


@admin.register(LiberacaoPlanoMinisterio)
class LiberacaoPlanoMinisterioAdmin(admin.ModelAdmin):
    list_display = ('ministerio', 'plano', 'pode_visualizar', 'pode_contratar', 'acesso_beta', 'ativo')
    list_filter = ('plano', 'pode_visualizar', 'pode_contratar', 'acesso_beta', 'ativo')
    search_fields = ('ministerio__nome_fantasia', 'plano__nome', 'plano__codigo_plano')
    autocomplete_fields = ('ministerio', 'plano')
    list_editable = ('pode_visualizar', 'pode_contratar', 'acesso_beta', 'ativo')
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


@admin.register(EventoFunil)
class EventoFunilAdmin(admin.ModelAdmin):
    """Admin técnico de métricas de funil, somente leitura e restrito a superusuário."""
    list_display = ('tipo', 'ministerio', 'plano', 'ciclo_pagamento', 'valor', 'criado_em')
    list_filter = ('tipo', 'ciclo_pagamento', 'criado_em')
    search_fields = (
        'ministerio__nome_fantasia',
        'plano__nome',
        'plano__codigo_plano',
    )
    readonly_fields = ('tipo', 'ministerio', 'plano', 'ciclo_pagamento', 'valor', 'extra', 'criado_em')
    date_hierarchy = 'criado_em'

    def has_module_permission(self, request):
        # Oculta do menu lateral do admin — acesso direto via dashboard de funil
        return False

    def has_view_permission(self, request, obj=None):
        return bool(request.user and request.user.is_active and request.user.is_superuser)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

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

admin.site.register(ValidacaoImagens, ValidacaoImagensAdmin)


class CodigoPromocionalAdmin(admin.ModelAdmin):
    """Admin para gerenciar cupons/códigos promocionais."""
    list_display = ('codigo_stripe', 'descricao', 'status', 'percentual_desconto', 'data_termino', 'vezes_usado', 'usos_restantes')
    list_filter = ('status', 'data_inicio', 'data_termino')
    search_fields = ('codigo_stripe', 'descricao')
    readonly_fields = ('vezes_usado', 'criado_em', 'atualizado_em')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('codigo_stripe', 'descricao', 'status')
        }),
        ('Desconto', {
            'fields': ('percentual_desconto',),
            'description': 'Apenas informativo — o desconto real é definido no Stripe.'
        }),
        ('Validade', {
            'fields': ('data_inicio', 'data_termino', 'usos_restantes'),
            'description': 'Deixe em branco para ilimitado.'
        }),
        ('Rastreamento', {
            'fields': ('vezes_usado', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make codigo_stripe read-only after creation."""
        if obj:  # Editing an existing object
            return self.readonly_fields + ('codigo_stripe',)
        return self.readonly_fields


admin.site.register(CodigoPromocional, CodigoPromocionalAdmin)