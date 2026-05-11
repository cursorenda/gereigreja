"""Admin para modelos de planos, assinaturas e códigos promocionais."""
from collections import defaultdict
from datetime import datetime, timedelta

from django.contrib import admin
from django.db.models import Count, Exists, OuterRef, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.urls import path

from .models import AssinaturaMinisterio, CodigoPromocional, EventoFunil, LiberacaoPlanoMinisterio, Plano


@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = (
        'get_nome_display', 'codigo_plano', 'preco_mensal', 'preco_anual',
        'limite_membros', 'permite_modulo_secretaria', 'permite_modulo_comunicacao',
        'permite_suporte_tickets', 'suporte_prioritario', 'is_visible',
        'liberado_publicamente', 'contratacao_publica_liberada', 'ativo',
    )
    list_filter = ('ativo', 'is_visible', 'liberado_publicamente', 'contratacao_publica_liberada')
    search_fields = ('nome', 'codigo_plano', 'descricao')
    list_editable = (
        'preco_mensal', 'preco_anual', 'limite_membros', 'is_visible',
        'liberado_publicamente', 'contratacao_publica_liberada', 'ativo',
    )
    fieldsets = (
        ('Identificação', {'fields': ('nome', 'codigo_plano', 'descricao')}),
        ('Preços e Visibilidade', {'fields': (
            'preco_mensal', 'preco_de_mensal', 'preco_anual', 'preco_de_anual',
            'is_visible', 'liberado_publicamente', 'contratacao_publica_liberada',
            'ordem_liberacao', 'ativo',
        )}),
        ('Limites e Recursos', {'fields': ('limite_membros', 'limite_igrejas')}),
        ('Módulos e Suporte', {'fields': (
            'permite_modulo_secretaria', 'permite_modulo_agenda', 'permite_modulo_eventos',
            'permite_modulo_escola_biblica', 'permite_modulo_financeiro',
            'permite_modulo_comunicacao', 'permite_suporte_tickets', 'suporte_prioritario',
        )}),
        ('Integração (Stripe)', {
            'fields': ('stripe_product_id', 'stripe_price_id_mensal', 'stripe_price_id_anual'),
            'classes': ('collapse',),
        }),
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

        try:
            dias = int(request.GET.get('dias', 30))
        except (TypeError, ValueError):
            dias = 30
        if dias not in (7, 30, 90):
            dias = 30
        data_inicio = datetime.now() - timedelta(days=dias)
        eventos = EventoFunil.objects.filter(criado_em__gte=data_inicio)

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


class CodigoPromocionalAdmin(admin.ModelAdmin):
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
        if obj:
            return self.readonly_fields + ('codigo_stripe',)
        return self.readonly_fields


admin.site.register(CodigoPromocional, CodigoPromocionalAdmin)
