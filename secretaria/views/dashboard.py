"""
secretaria/views/dashboard.py
Views de dashboard principal (index) e salvar nota do usuário.
"""
import json
import locale
import logging
import csv
from calendar import monthrange
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import (
    BooleanField, Case, Count, Q, Sum, Value, When,
)
from django.db.models.functions import Extract
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from configuracao.models import Igreja, PerfilUsuario
from contas.models import NotaUsuario
from core.decorators import page_access_required
from core.utils import get_ministerio_or_error
from eventos.models import Evento, ParticipacaoEvento
from financeiro.models import ContaPagar
from secretaria.models import (
    AcompanhamentoVisita, Cargo, GrupoCasa, Membro, Tag, TimelineEvent, TipoPessoa,
)
from secretaria.utils import get_allowed_churches_for_membros, is_admin_org

from secretaria.views._helpers import (
    _user_has_permission_level_or_higher,
    get_request_scoped_churches,
    is_admin_or_pastor,
)
from secretaria.views.visitacao_metrics import build_visitacao_metrics

logger = logging.getLogger(__name__)

PERIODO_PRESETS_DIAS = {
    '30d': 30,
    '90d': 90,
}

PERIODO_PRESETS_MESES = {
    '6m': 6,
    '12m': 12,
}


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _calcular_faixas_etarias(membros_para_relatorios, idades):
    faixas = {
        '0-5 anos': 0,
        '6-10 anos': 0,
        '11-14 anos': 0,
        '15-17 anos': 0,
        '18-30 anos': 0,
        '31-50 anos': 0,
        '51-65 anos': 0,
        'Mais de 65 anos': 0,
        'Não Informado': membros_para_relatorios.filter(nascimento__isnull=True).count(),
    }
    for idade_val in idades:
        if 0 <= idade_val <= 5:
            faixas['0-5 anos'] += 1
        elif 6 <= idade_val <= 10:
            faixas['6-10 anos'] += 1
        elif 11 <= idade_val <= 14:
            faixas['11-14 anos'] += 1
        elif 15 <= idade_val <= 17:
            faixas['15-17 anos'] += 1
        elif 18 <= idade_val <= 30:
            faixas['18-30 anos'] += 1
        elif 31 <= idade_val <= 50:
            faixas['31-50 anos'] += 1
        elif 51 <= idade_val <= 65:
            faixas['51-65 anos'] += 1
        elif idade_val > 65:
            faixas['Mais de 65 anos'] += 1
    return [{'faixa_etaria': k, 'total': v} for k, v in faixas.items()]


def _idades_lista(membros_para_relatorios, hoje_data):
    idades = []
    for nascimento in membros_para_relatorios.filter(nascimento__isnull=False).values_list('nascimento', flat=True):
        if nascimento:
            try:
                idade = hoje_data.year - nascimento.year - (
                    (hoje_data.month, hoje_data.day) < (nascimento.month, nascimento.day)
                )
                idades.append(idade)
            except AttributeError:
                logger.warning('Valor inesperado para data de nascimento: %s', nascimento)
    return idades


def _assinatura_alerta(ministerio, hoje):
    if not (hasattr(ministerio, 'assinatura') and ministerio.assinatura):
        return None
    data_fim_raw = ministerio.assinatura.data_fim
    if data_fim_raw and hasattr(data_fim_raw, 'date'):
        data_fim_raw = data_fim_raw.date()
    dias_restantes = (data_fim_raw - hoje).days if data_fim_raw else None
    if dias_restantes is not None and dias_restantes <= 10 and ministerio.assinatura.status != 'ATIVA':
        return {'dias_restantes': dias_restantes, 'status': ministerio.assinatura.get_status_display()}
    return None


def _dashboard_visibility_flags(request):
    """Centraliza a visibilidade dos blocos do dashboard por perfil."""
    from contas.constants import (
        ADMIN_MINISTERIO,
        LIDERANCA_FINANCEIRA,
        TESOUREIRO,
        user_tem_grupo,
    )
    from contas.page_permissions import user_can_access_page

    user = request.user
    can_manage_secretaria = user_can_access_page(user, 'secretaria_pessoas', request=request)
    can_manage_cargos = user_can_access_page(user, 'secretaria_cargos', request=request)
    can_manage_reception = user_can_access_page(user, 'recepcao_visitantes', request=request)
    can_manage_grupos = user_can_access_page(user, 'secretaria_grupos_casa', request=request)
    can_manage_acompanhamentos = user_can_access_page(user, 'secretaria_acompanhamentos', request=request)
    can_manage_tags = user_can_access_page(user, 'secretaria_tags', request=request)
    can_view_relatorios = user_can_access_page(user, 'secretaria_relatorios', request=request)
    can_view_financial_alert = user_tem_grupo(user, TESOUREIRO)
    can_view_signature_alert = (
        user_tem_grupo(user, ADMIN_MINISTERIO)
        or user_tem_grupo(user, LIDERANCA_FINANCEIRA)
    )

    cards = {
        'pessoas': can_manage_secretaria,
        'recepcao': can_manage_reception,
        'cargos': can_manage_cargos,
        'grupos': can_manage_grupos,
        'relatorios': can_view_relatorios,
        'acompanhamentos': can_manage_acompanhamentos,
        'tags': can_manage_tags,
        'associacoes': can_manage_secretaria,
    }

    quick_actions = {
        'cadastrar_pessoa': can_manage_secretaria,
        'registrar_visitante': can_manage_reception,
        'iniciar_acompanhamento': can_manage_acompanhamentos,
    }

    return {
        'alertas': {
            'financeiro': can_view_financial_alert,
            'assinatura': can_view_signature_alert,
            'exibir_algum': can_view_financial_alert or can_view_signature_alert,
        },
        'cards': cards,
        'quick_actions': quick_actions,
        'secoes': {
            'operacao': any(cards.values()),
            'acoes_rapidas': any(quick_actions.values()),
        },
    }


def _add_months(base_date, months_delta):
    """Retorna o primeiro dia do mês deslocado em months_delta."""
    month_index = (base_date.month - 1) + months_delta
    year = base_date.year + (month_index // 12)
    month = (month_index % 12) + 1
    return date(year, month, 1)


def _last_month_starts(reference_date, total_months=12):
    """Lista meses (primeiro dia), do mais antigo ao atual."""
    anchor = reference_date.replace(day=1)
    return [_add_months(anchor, -offset) for offset in range(total_months - 1, -1, -1)]


def _month_end(month_start):
    """Retorna o último dia do mês do month_start."""
    return month_start.replace(day=monthrange(month_start.year, month_start.month)[1])


def _month_starts_between(start_date, end_date):
    """Retorna o primeiro dia de cada mês entre start_date e end_date (inclusive)."""
    cursor = start_date.replace(day=1)
    limit = end_date.replace(day=1)
    months = []
    while cursor <= limit:
        months.append(cursor)
        cursor = _add_months(cursor, 1)
    return months


def _parse_periodo_dashboard(request, hoje_data):
    """Normaliza o período selecionado no dashboard (presets + custom)."""
    periodo = (request.GET.get('periodo') or '12m').strip().lower()
    data_inicio_raw = (request.GET.get('data_inicio') or '').strip()
    data_fim_raw = (request.GET.get('data_fim') or '').strip()

    if periodo in PERIODO_PRESETS_DIAS:
        dias = PERIODO_PRESETS_DIAS[periodo]
        data_inicio = hoje_data - timedelta(days=dias - 1)
        return {
            'periodo': periodo,
            'data_inicio': data_inicio,
            'data_fim': hoje_data,
            'periodo_label': f'Últimos {dias} dias',
        }

    if periodo in PERIODO_PRESETS_MESES:
        meses = PERIODO_PRESETS_MESES[periodo]
        data_inicio = _add_months(hoje_data.replace(day=1), -(meses - 1))
        return {
            'periodo': periodo,
            'data_inicio': data_inicio,
            'data_fim': hoje_data,
            'periodo_label': f'Últimos {meses} meses',
        }

    if periodo == 'custom':
        try:
            data_inicio = datetime.strptime(data_inicio_raw, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_raw, '%Y-%m-%d').date()
            if data_inicio > data_fim:
                data_inicio, data_fim = data_fim, data_inicio
            return {
                'periodo': 'custom',
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'periodo_label': f'{data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}',
            }
        except ValueError:
            pass

    # Fallback seguro para manter o comportamento padrão
    data_inicio = _add_months(hoje_data.replace(day=1), -11)
    return {
        'periodo': '12m',
        'data_inicio': data_inicio,
        'data_fim': hoje_data,
        'periodo_label': 'Últimos 12 meses',
    }


def _series_evolucao_por_tipo(membros_base_para_grafico_status, data_inicio, data_fim):
    month_starts = _month_starts_between(data_inicio, data_fim)
    month_ends = [_month_end(month_start) for month_start in month_starts]
    meses_labels = [month_start.strftime('%b/%Y') for month_start in month_starts]
    evolucao_por_tipo = defaultdict(list)
    tipos_para_grafico = ['Membro', 'Congregado', 'Novo Convertido', 'Visitante']

    entradas = defaultdict(list)
    registros = membros_base_para_grafico_status.filter(
        tipo_pessoa__nome__in=tipos_para_grafico,
        data_entrada__isnull=False,
        data_entrada__gte=data_inicio,
        data_entrada__lte=data_fim,
    ).values_list('tipo_pessoa__nome', 'data_entrada')
    for tipo_nome, data_entrada in registros:
        if data_entrada:
            entradas[tipo_nome].append(data_entrada)
    for tipo_nome in tipos_para_grafico:
        entradas[tipo_nome].sort()

    for tipo_nome in tipos_para_grafico:
        datas = entradas[tipo_nome]
        idx = 0
        acumulado = []
        for month_end in month_ends:
            while idx < len(datas) and datas[idx] <= month_end:
                idx += 1
            acumulado.append(idx)
        evolucao_por_tipo[tipo_nome] = acumulado

    return meses_labels, evolucao_por_tipo


def _series_mensal_membros(membros_para_relatorios, hoje):
    month_starts = _last_month_starts(hoje, 12)
    month_ends = [_month_end(month_start) for month_start in month_starts]
    meses_evolucao = [month_start.strftime('%Y-%m') for month_start in month_starts]
    membros_evolucao = []
    novos_membros_por_mes = []

    datas_entrada = sorted(
        d for d in membros_para_relatorios.exclude(data_entrada__isnull=True).values_list('data_entrada', flat=True)
        if d
    )
    novos_por_mes = Counter((d.year, d.month) for d in datas_entrada)

    idx = 0
    for month_start, month_end in zip(month_starts, month_ends):
        while idx < len(datas_entrada) and datas_entrada[idx] <= month_end:
            idx += 1
        membros_evolucao.append(idx)
        novos_membros_por_mes.append(novos_por_mes.get((month_start.year, month_start.month), 0))

    return meses_evolucao, membros_evolucao, novos_membros_por_mes


def _aniversariantes_janela(membros_para_relatorios, hoje):
    ontem = hoje - timedelta(days=1)
    amanha = hoje + timedelta(days=1)
    aniversariantes_hoje = membros_para_relatorios.filter(nascimento__month=hoje.month, nascimento__day=hoje.day)
    aniversariantes_ontem = membros_para_relatorios.filter(nascimento__month=ontem.month, nascimento__day=ontem.day)
    aniversariantes_amanha = membros_para_relatorios.filter(nascimento__month=amanha.month, nascimento__day=amanha.day)
    return aniversariantes_ontem, aniversariantes_hoje, aniversariantes_amanha


def _pie_tipos_pessoa(membros_para_grafico_tipo):
    tipos_pessoa_qs = TipoPessoa.objects.all().order_by('nome')
    membros_por_tipo = (
        membros_para_grafico_tipo.values('tipo_pessoa__nome')
        .annotate(total=Count('chave'))
        .order_by('tipo_pessoa__nome')
    )

    pie_labels = []
    pie_values = []
    for tipo in tipos_pessoa_qs:
        found = next((item for item in membros_por_tipo if item['tipo_pessoa__nome'] == tipo.nome), None)
        pie_labels.append(tipo.nome)
        pie_values.append(found['total'] if found else 0)

    return pie_labels, pie_values


def _categoria_evento_data(igrejas_filtro, data_inicio=None, data_fim=None):
    eventos_ids = list(Evento.objects.filter(igreja__in=igrejas_filtro).values_list('id', flat=True))
    participacoes_qs = ParticipacaoEvento.objects.filter(
        status__in=['CONFIRMADO', 'PRESENTE', 'AUSENTE'],
        evento_id__in=eventos_ids,
    )
    if data_inicio and data_fim:
        participacoes_qs = participacoes_qs.filter(evento__data_inicio__date__range=(data_inicio, data_fim))
    participacoes_por_categoria = (
        participacoes_qs.values('evento__tipo').annotate(total=Count('id')).order_by('evento__tipo')
    )
    tipo_dict = dict(Evento.TIPO_EVENTO_CHOICES)

    categoria_labels = []
    categoria_values = []
    for item in participacoes_por_categoria:
        tipo = item['evento__tipo']
        categoria_labels.append(tipo_dict.get(tipo, tipo.title()))
        categoria_values.append(item['total'])

    return categoria_labels, categoria_values


def _gerar_insights_dashboard(
    membros_para_relatorios,
    membros_base_periodo,
    data_inicio_periodo,
    data_fim_periodo,
    novos_membros_periodo,
    total_pendencias_cadastro,
):
    """Gera insights determinísticos para orientar ação no dashboard."""
    insights = []
    dias_periodo = max((data_fim_periodo - data_inicio_periodo).days + 1, 1)

    # 1) Tendencia de entrada de membros versus janela anterior equivalente.
    periodo_anterior_fim = data_inicio_periodo - timedelta(days=1)
    periodo_anterior_inicio = periodo_anterior_fim - timedelta(days=dias_periodo - 1)
    novos_membros_periodo_anterior = membros_para_relatorios.filter(
        data_entrada__isnull=False,
        data_entrada__range=(periodo_anterior_inicio, periodo_anterior_fim),
    ).count()

    diferenca_absoluta = novos_membros_periodo - novos_membros_periodo_anterior
    if novos_membros_periodo_anterior >= 3:
        variacao = ((novos_membros_periodo - novos_membros_periodo_anterior) / novos_membros_periodo_anterior) * 100
        if variacao >= 15 and diferenca_absoluta >= 3:
            insights.append({
                'tone': 'is-positive',
                'icon': 'fas fa-arrow-trend-up',
                'title': 'Tendencia positiva de entrada',
                'message': (
                    f'Novos membros cresceram {variacao:.1f}% em relacao ao periodo anterior equivalente.'
                ),
                'cta_label': 'Ver lista de pessoas',
                'cta_url': reverse('secretaria:lista_pessoas'),
            })
        elif variacao <= -15 and abs(diferenca_absoluta) >= 3:
            insights.append({
                'tone': 'is-warning',
                'icon': 'fas fa-arrow-trend-down',
                'title': 'Queda na entrada de membros',
                'message': (
                    f'Novos membros cairam {abs(variacao):.1f}% versus o periodo anterior. Vale revisar a recepcao.'
                ),
                'cta_label': 'Abrir visitantes',
                'cta_url': reverse('secretaria:lista_visitantes'),
            })
    elif novos_membros_periodo > 0:
        insights.append({
            'tone': 'is-positive',
            'icon': 'fas fa-seedling',
            'title': 'Primeiras entradas no comparativo',
            'message': 'Nao havia base no periodo anterior e agora ha novos membros registrados.',
            'cta_label': 'Ver lista de pessoas',
            'cta_url': reverse('secretaria:lista_pessoas'),
        })

    # 2) Qualidade cadastral no periodo.
    total_cadastros_periodo = max(membros_base_periodo.count(), 1)
    taxa_pendencias = total_pendencias_cadastro / total_cadastros_periodo
    if (
        total_pendencias_cadastro >= 8
        and total_cadastros_periodo >= 20
        and taxa_pendencias >= 0.25
    ):
        insights.append({
            'tone': 'is-danger',
            'icon': 'fas fa-triangle-exclamation',
            'title': 'Risco cadastral elevado',
            'message': (
                f'{total_pendencias_cadastro} registros com pendencias no periodo '
                f'({taxa_pendencias * 100:.0f}% dos cadastros do periodo).'
            ),
            'cta_label': 'Tratar pendencias',
            'cta_url': reverse('secretaria:lista_pessoas'),
        })
    elif (
        total_pendencias_cadastro >= 4
        and total_cadastros_periodo >= 10
        and taxa_pendencias >= 0.15
    ):
        insights.append({
            'tone': 'is-warning',
            'icon': 'fas fa-circle-exclamation',
            'title': 'Atencao em qualidade cadastral',
            'message': (
                f'Pendencias cadastrais em {taxa_pendencias * 100:.0f}% dos registros do periodo.'
            ),
            'cta_label': 'Revisar cadastros',
            'cta_url': reverse('secretaria:lista_pessoas'),
        })

    # 3) Sinal operacional de recepcao e conversao no periodo.
    total_visitantes_periodo = membros_base_periodo.filter(tipo_pessoa__nome__iexact='Visitante').count()
    total_convertidos_periodo = membros_base_periodo.filter(tipo_pessoa__nome__iexact='Novo Convertido').count()
    limiar_visitantes = max(6, dias_periodo // 8)
    limiar_convertidos = max(3, dias_periodo // 20)
    if total_visitantes_periodo >= limiar_visitantes:
        insights.append({
            'tone': 'is-info',
            'icon': 'fas fa-handshake-angle',
            'title': 'Recepcao aquecida no periodo',
            'message': (
                f'Foram registrados {total_visitantes_periodo} visitantes. Boa oportunidade de acompanhamento ativo.'
            ),
            'cta_label': 'Abrir visitantes',
            'cta_url': reverse('secretaria:lista_visitantes'),
        })
    elif total_convertidos_periodo >= limiar_convertidos:
        insights.append({
            'tone': 'is-positive',
            'icon': 'fas fa-user-check',
            'title': 'Movimento de conversao relevante',
            'message': (
                f'Ha {total_convertidos_periodo} novos convertidos no periodo. Planeje o proximo ciclo de integracao.'
            ),
            'cta_label': 'Ver acompanhamentos',
            'cta_url': reverse('secretaria:acompanhamentos_visita'),
        })

    if not insights:
        insights.append({
            'tone': 'is-neutral',
            'icon': 'fas fa-circle-check',
            'title': 'Painel estavel no periodo',
            'message': 'Sem alertas criticos no recorte atual. Mantenha o monitoramento semanal.',
            'cta_label': '',
            'cta_url': '',
        })

    return insights[:3]


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------

@login_required
def index(request):
    from contas.constants import MEMBRO_COMUM, ADMIN_MINISTERIO, user_tem_grupo
    if (user_tem_grupo(request.user, MEMBRO_COMUM)
            and not user_tem_grupo(request.user, ADMIN_MINISTERIO)
            and not request.user.is_staff):
        return redirect('secretaria:portal_membro')

    ministerio = get_ministerio_or_error(request)
    if not ministerio:
        messages.error(request, "Seu perfil não está associado a nenhum ministério. Entre em contato com o administrador.")
        return redirect('core:index')

    allowed_churches_secretaria = get_allowed_churches_for_membros(request.user, ministerio)
    igrejas_filtro = get_request_scoped_churches(request, allowed_churches_secretaria)

    if request.igreja_ativa and allowed_churches_secretaria.filter(pk=request.igreja_ativa.pk).exists():
        titulo_contextual = f"Visão Geral - Igreja: {request.igreja_ativa.nome_igreja}"
    elif igrejas_filtro.exists():
        titulo_contextual = f"Visão Geral - {ministerio.nome_fantasia} (Consolidado)"
    else:
        titulo_contextual = f"Visão Geral - {ministerio.nome_fantasia}"

    total_pessoas_igreja = 0
    membros_para_relatorios = Membro.objects.none()
    if igrejas_filtro.exists():
        total_pessoas_igreja = Membro.objects.filter(igreja__in=igrejas_filtro).count()
        membros_para_relatorios = Membro.objects.filter(
            igreja__in=igrejas_filtro,
            tipo_pessoa__nome__iexact='Membro',
            status_pessoa__nome__iexact='Ativo',
        )
    elif is_admin_org(request.user):
        total_pessoas_igreja = Membro.objects.filter(igreja__ministerio=ministerio).count()
        membros_para_relatorios = Membro.objects.filter(
            igreja__ministerio=ministerio,
            tipo_pessoa__nome__iexact='Membro',
            status_pessoa__nome__iexact='Ativo',
        )
        titulo_contextual += ' (Ministério)'

    membros_base_para_grafico_status = (
        Membro.objects.filter(igreja__in=igrejas_filtro)
        if igrejas_filtro.exists()
        else Membro.objects.filter(igreja__ministerio=ministerio) if is_admin_org(request.user)
        else Membro.objects.none()
    )

    status_data_qs = membros_base_para_grafico_status.values('status_pessoa__nome').annotate(
        total=Count('chave')
    ).order_by('status_pessoa__nome')
    status_data_list = [
        {'status': item['status_pessoa__nome'], 'total': item['total']}
        for item in status_data_qs if item['status_pessoa__nome']
    ]

    genero_data_qs = membros_para_relatorios.values('genero').annotate(total=Count('chave'))
    genero_map = {'F': 'Feminino', 'M': 'Masculino', '': 'Não Informado', None: 'Não Informado'}
    aggregated_genero = {}
    for item in genero_data_qs:
        gd = genero_map.get(item['genero'], 'Não Informado')
        aggregated_genero[gd] = aggregated_genero.get(gd, 0) + item['total']
    genero_data_normalized = [{'genero': k, 'total': v} for k, v in aggregated_genero.items()]

    hoje_data = date.today()
    data_inicio_periodo = _add_months(hoje_data.replace(day=1), -11)
    data_fim_periodo = hoje_data
    idades = _idades_lista(membros_para_relatorios, hoje_data)
    faixa_etaria_data = _calcular_faixas_etarias(membros_para_relatorios, idades)

    trinta_dias_atras = hoje_data - timedelta(days=30)
    novos_membros_30_dias = membros_para_relatorios.filter(data_entrada__gte=trinta_dias_atras).count()
    aniversariantes_mes_atual_count = membros_para_relatorios.filter(nascimento__month=hoje_data.month).count()

    idades_para_media = _idades_lista(membros_para_relatorios, hoje_data)
    media_idade_membros = round(sum(idades_para_media) / len(idades_para_media)) if idades_para_media else 0

    mes_atual = hoje_data.month
    dia_atual = hoje_data.day
    aniversariantes_qs = membros_para_relatorios.filter(nascimento__isnull=False).annotate(
        nascimento_month=Extract('nascimento', 'month'),
        nascimento_day=Extract('nascimento', 'day'),
        passed_this_year=Case(
            When(nascimento_month__lt=mes_atual, then=Value(True)),
            When(nascimento_month=mes_atual, nascimento_day__lt=dia_atual, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ),
    ).order_by('passed_this_year', 'nascimento_month', 'nascimento_day')
    aniversariantes_proximos = list(aniversariantes_qs[:10])

    pendencias_cadastro = membros_para_relatorios.filter(Q(nascimento__isnull=True) | Q(email__isnull=True) | Q(email=''))
    total_pendencias_cadastro = pendencias_cadastro.count()

    igrejas_ids = membros_para_relatorios.values_list('igreja_id', flat=True).distinct()
    contas_vencidas = ContaPagar.objects.filter(igreja_id__in=igrejas_ids, status='VEN')
    total_contas_vencidas = contas_vencidas.count()
    valor_total_contas_vencidas = contas_vencidas.aggregate(total=Sum('valor'))['total'] or 0

    hoje = hoje_data
    assinatura = _assinatura_alerta(ministerio, hoje)

    meses_labels, evolucao_por_tipo = _series_evolucao_por_tipo(
        membros_base_para_grafico_status,
        data_inicio_periodo,
        data_fim_periodo,
    )
    meses_evolucao, membros_evolucao, novos_membros_por_mes = _series_mensal_membros(membros_para_relatorios, hoje)
    aniversariantes_ontem, aniversariantes_hoje, aniversariantes_amanha = _aniversariantes_janela(
        membros_para_relatorios,
        hoje,
    )
    membros_para_grafico_tipo = Membro.objects.filter(igreja__in=igrejas_filtro)
    pie_labels, pie_values = _pie_tipos_pessoa(membros_para_grafico_tipo)
    categoria_labels, categoria_values = _categoria_evento_data(
        igrejas_filtro,
        data_inicio_periodo,
        data_fim_periodo,
    )

    # Foto do usuário
    usuario_foto_url = None
    try:
        perfil_usuario = PerfilUsuario.objects.get(user=request.user)
        if perfil_usuario.foto_perfil:
            usuario_foto_url = perfil_usuario.foto_perfil.url
    except PerfilUsuario.DoesNotExist:
        pass

    atividades_recentes = TimelineEvent.objects.filter(
        membro__in=membros_para_relatorios
    ).select_related('membro').order_by('-data')[:10]

    alertas = []
    if total_contas_vencidas > 0:
        alertas.append({
            'tipo': 'danger', 'titulo': 'Contas Vencidas',
            'mensagem': f'{total_contas_vencidas} conta(s) vencida(s) - R$ {valor_total_contas_vencidas:.2f}',
            'icone': 'fas fa-exclamation-circle',
        })
    if aniversariantes_hoje.exists():
        alertas.append({
            'tipo': 'info', 'titulo': 'Aniversariantes Hoje',
            'mensagem': f'{aniversariantes_hoje.count()} pessoa(s) fazendo aniversário hoje!',
            'icone': 'fas fa-birthday-cake',
        })
    if assinatura:
        alertas.append({
            'tipo': 'warning', 'titulo': 'Assinatura Vencendo',
            'mensagem': f'Sua assinatura vence em {assinatura["dias_restantes"]} dias',
            'icone': 'fas fa-calendar-times',
        })

    hoje_agora = timezone.now()
    if igrejas_filtro.exists():
        eventos_qs = Evento.objects.filter(igreja__in=igrejas_filtro, data_inicio__gte=hoje_agora)
    elif is_admin_org(request.user):
        eventos_qs = Evento.objects.filter(igreja__ministerio=ministerio, data_inicio__gte=hoje_agora)
    else:
        eventos_qs = Evento.objects.none()
    eventos_qs = eventos_qs.order_by('data_inicio')[:8]

    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except locale.Error:
        pass

    proximos_eventos = []
    for evento in eventos_qs:
        data = evento.data_inicio
        dia = data.day
        try:
            dia_semana = data.strftime('%a').upper()
        except Exception:
            dia_semana = ''
        data_evento = data.date()
        if data_evento == hoje:
            data_texto = 'hoje'
        elif data_evento == (hoje + timedelta(days=1)):
            data_texto = 'amanhã'
        else:
            data_texto = data.strftime('%d/%m')
        hora_inicio = evento.data_inicio.strftime('%H:%M') if evento.data_inicio else ''
        hora_fim = evento.data_fim.strftime('%H:%M') if evento.data_fim else ''
        if hora_inicio and hora_fim:
            horario = f'de {hora_inicio} até {hora_fim}'
        elif hora_inicio:
            horario = f'às {hora_inicio}'
        else:
            horario = ''
        proximos_eventos.append({
            'dia': f'{dia:02d}',
            'dia_semana': dia_semana,
            'titulo': evento.titulo,
            'descricao': evento.descricao or '',
            'linha_info': f'{data_texto}, {horario}' if horario else data_texto,
        })

    nota_usuario, _ = NotaUsuario.objects.get_or_create(usuario=request.user)

    context = {
        'status_data_json': json.dumps(status_data_list),
        'status_labels_json': json.dumps([item['status'] for item in status_data_list]),
        'status_values_json': json.dumps([item['total'] for item in status_data_list]),
        'genero_data_json': json.dumps(genero_data_normalized),
        'genero_labels_json': json.dumps([item['genero'] for item in genero_data_normalized]),
        'genero_values_json': json.dumps([item['total'] for item in genero_data_normalized]),
        'faixa_etaria_data_json': json.dumps(faixa_etaria_data),
        'faixa_labels_json': json.dumps([item['faixa_etaria'] for item in faixa_etaria_data]),
        'faixa_values_json': json.dumps([item['total'] for item in faixa_etaria_data]),
        'novos_membros_30_dias': novos_membros_30_dias,
        'aniversariantes_mes_atual_count': aniversariantes_mes_atual_count,
        'media_idade_membros': media_idade_membros,
        'ministerio': ministerio,
        'aniversariantes_proximos': aniversariantes_proximos,
        'titulo_pagina': titulo_contextual,
        'igreja_ativa_atual': request.igreja_ativa,
        'total_membros_ativos': membros_para_relatorios.count(),
        'total_pessoas_igreja': total_pessoas_igreja,
        'novos_membros_ultimo_mes': novos_membros_30_dias,
        'total_pendencias_cadastro': total_pendencias_cadastro,
        'total_contas_vencidas': total_contas_vencidas,
        'valor_total_contas_vencidas': valor_total_contas_vencidas,
        'assinatura_alerta': assinatura,
        'evolucao_meses': meses_evolucao,
        'evolucao_membros': membros_evolucao,
        'novos_membros_por_mes': novos_membros_por_mes,
        'aniversariantes_ontem': aniversariantes_ontem,
        'aniversariantes_hoje': aniversariantes_hoje,
        'aniversariantes_amanha': aniversariantes_amanha,
        'usuario_foto_url': usuario_foto_url,
        'atividades_recentes': atividades_recentes,
        'alertas': alertas,
        'proximos_eventos': proximos_eventos,
        'nota_usuario': nota_usuario,
        # Pie chart
        'pie_labels_json': json.dumps(pie_labels),
        'pie_values_json': json.dumps(pie_values),
        # Categoria evento
        'categoria_evento_labels_json': json.dumps(categoria_labels),
        'categoria_evento_values_json': json.dumps(categoria_values),
        # Evolução
        'evolucao_meses_labels_json': json.dumps(meses_labels),
        'evolucao_membros_json': json.dumps(evolucao_por_tipo['Membro']),
        'evolucao_congregados_json': json.dumps(evolucao_por_tipo['Congregado']),
        'evolucao_novos_convertidos_json': json.dumps(evolucao_por_tipo['Novo Convertido']),
        'evolucao_visitantes_json': json.dumps(evolucao_por_tipo['Visitante']),
    }

    from contas.constants import SECRETARIO_LOCAL
    link_cadastro = None
    pendentes_count = None
    igreja_selecionada = getattr(request, 'igreja_ativa', None)
    pode_ver_link = False
    if _user_has_permission_level_or_higher(request.user, SECRETARIO_LOCAL):
        pode_ver_link = True
        if igreja_selecionada:
            link_cadastro = f'/secretaria/cadastro/igreja/{igreja_selecionada.pk}/'
            from secretaria.models import StatusPessoa
            status_pendentes = (
                StatusPessoa.objects.filter(nome__iexact='Pendente')
                | StatusPessoa.objects.filter(nome__iexact='Aguardando aprovação')
            )
            pendentes_count = 0
            if status_pendentes.exists():
                pendentes_count = Membro.objects.filter(
                    igreja=igreja_selecionada, status_pessoa__in=status_pendentes
                ).count()
    context['link_cadastro'] = link_cadastro
    context['pendentes_count'] = pendentes_count
    context['pode_ver_link'] = pode_ver_link

    if request.igreja_ativa and allowed_churches_secretaria.filter(pk=request.igreja_ativa.pk).exists():
        context['scope_label'] = f'Igreja: {request.igreja_ativa.nome_igreja}'
    elif igrejas_filtro.exists():
        _n = igrejas_filtro.count()
        context['scope_label'] = f"Consolidado — {ministerio.nome_fantasia} ({_n} {'igrejas' if _n != 1 else 'igreja'})"
    else:
        context['scope_label'] = None

    return render(request, 'secretaria/index.html', context)


# ---------------------------------------------------------------------------
# salvar_nota_usuario (AJAX POST)
# ---------------------------------------------------------------------------

@require_POST
@login_required
def salvar_nota_usuario(request):
    try:
        conteudo = request.POST.get('conteudo', '')
        nota_usuario, created = NotaUsuario.objects.get_or_create(usuario=request.user)
        nota_usuario.conteudo = conteudo
        nota_usuario.save()
        return JsonResponse({
            'success': True,
            'message': 'Nota salva com sucesso!',
            'atualizado_em': nota_usuario.atualizado_em.strftime('%d/%m/%Y %H:%M'),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro ao salvar nota: {e}'}, status=500)


# ---------------------------------------------------------------------------
# dashboard
# ---------------------------------------------------------------------------

@login_required
@page_access_required('dashboard_secretaria')
def dashboard(request):
    from contas.constants import MEMBRO_COMUM, ADMIN_MINISTERIO, PASTOR_LOCAL, user_tem_grupo
    if request.user.is_superuser:
        return redirect('admin:index')
    if (user_tem_grupo(request.user, MEMBRO_COMUM)
            and not user_tem_grupo(request.user, ADMIN_MINISTERIO)
            and not request.user.is_staff):
        return redirect('secretaria:portal_membro')

    ministerio = get_ministerio_or_error(request)
    igrejas_permitidas = getattr(request, 'igrejas_permitidas', None)
    if igrejas_permitidas is None:
        igrejas_permitidas = get_allowed_churches_for_membros(request.user, ministerio)
    igrejas_filtro = get_request_scoped_churches(request, igrejas_permitidas)

    if request.igreja_ativa and igrejas_permitidas.filter(pk=request.igreja_ativa.pk).exists():
        titulo_contextual = f'Visão Geral - Igreja: {request.igreja_ativa.nome_igreja}'
    else:
        total_igrejas = igrejas_filtro.count()
        titulo_contextual = f'Visão Geral - {ministerio.nome_fantasia} ({total_igrejas} igrejas)'

    hoje_data = date.today()
    hoje = hoje_data
    periodo_info = _parse_periodo_dashboard(request, hoje_data)
    data_inicio_periodo = periodo_info['data_inicio']
    data_fim_periodo = periodo_info['data_fim']
    dias_periodo = max((data_fim_periodo - data_inicio_periodo).days + 1, 1)
    periodo_anterior_fim = data_inicio_periodo - timedelta(days=1)
    periodo_anterior_inicio = periodo_anterior_fim - timedelta(days=dias_periodo - 1)

    total_pessoas_igreja = Membro.objects.filter(igreja__in=igrejas_filtro).count()
    membros_para_relatorios = Membro.objects.filter(
        igreja__in=igrejas_filtro,
        tipo_pessoa__nome__iexact='Membro',
        status_pessoa__nome__iexact='Ativo',
    )

    membros_base_para_grafico_status = Membro.objects.filter(igreja__in=igrejas_filtro)
    membros_para_relatorios_periodo = membros_para_relatorios.filter(
        data_entrada__isnull=False,
        data_entrada__range=(data_inicio_periodo, data_fim_periodo),
    )
    membros_base_periodo = membros_base_para_grafico_status.filter(
        data_entrada__isnull=False,
        data_entrada__range=(data_inicio_periodo, data_fim_periodo),
    )
    membros_base_periodo_anterior = membros_base_para_grafico_status.filter(
        data_entrada__isnull=False,
        data_entrada__range=(periodo_anterior_inicio, periodo_anterior_fim),
    )

    status_data_qs = membros_base_periodo.values('status_pessoa__nome').annotate(
        total=Count('chave')
    ).order_by('status_pessoa__nome')
    status_data_list = [
        {'status': item['status_pessoa__nome'], 'total': item['total']}
        for item in status_data_qs if item['status_pessoa__nome']
    ]

    meses_labels, evolucao_por_tipo = _series_evolucao_por_tipo(
        membros_base_para_grafico_status,
        data_inicio_periodo,
        data_fim_periodo,
    )

    genero_data_qs = membros_para_relatorios_periodo.values('genero').annotate(total=Count('chave'))
    genero_map = {'F': 'Feminino', 'M': 'Masculino', '': 'Não Informado', None: 'Não Informado'}
    aggregated_genero = {}
    for item in genero_data_qs:
        gd = genero_map.get(item['genero'], 'Não Informado')
        aggregated_genero[gd] = aggregated_genero.get(gd, 0) + item['total']
    genero_data_normalized = [{'genero': k, 'total': v} for k, v in aggregated_genero.items()]

    idades = _idades_lista(membros_para_relatorios_periodo, hoje_data)
    faixa_etaria_data = _calcular_faixas_etarias(membros_para_relatorios_periodo, idades)

    novos_membros_periodo = membros_para_relatorios_periodo.count()
    novos_membros_periodo_anterior = membros_para_relatorios.filter(
        data_entrada__isnull=False,
        data_entrada__range=(periodo_anterior_inicio, periodo_anterior_fim),
    ).count()
    aniversariantes_mes_atual_count = membros_para_relatorios.filter(nascimento__month=hoje_data.month).count()

    idades_para_media = _idades_lista(membros_para_relatorios, hoje_data)
    media_idade_membros = round(sum(idades_para_media) / len(idades_para_media)) if idades_para_media else 0

    mes_atual = hoje_data.month
    dia_atual = hoje_data.day
    aniversariantes_qs = membros_para_relatorios.filter(nascimento__isnull=False).annotate(
        nascimento_month=Extract('nascimento', 'month'),
        nascimento_day=Extract('nascimento', 'day'),
        passed_this_year=Case(
            When(nascimento_month__lt=mes_atual, then=Value(True)),
            When(nascimento_month=mes_atual, nascimento_day__lt=dia_atual, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ),
    ).order_by('passed_this_year', 'nascimento_month', 'nascimento_day')
    aniversariantes_proximos = list(aniversariantes_qs[:10])

    pendencias_cadastro_base = membros_para_relatorios.filter(
        Q(nascimento__isnull=True) | Q(email__isnull=True) | Q(email='')
    )
    total_pendencias_cadastro = pendencias_cadastro_base.count()

    pendencias_cadastro_periodo = membros_para_relatorios_periodo.filter(
        Q(nascimento__isnull=True) | Q(email__isnull=True) | Q(email='')
    )
    total_pendencias_cadastro_periodo = pendencias_cadastro_periodo.count()
    total_pendencias_cadastro_periodo_anterior = membros_para_relatorios.filter(
        data_entrada__isnull=False,
        data_entrada__range=(periodo_anterior_inicio, periodo_anterior_fim),
    ).filter(
        Q(nascimento__isnull=True) | Q(email__isnull=True) | Q(email='')
    ).count()

    total_visitantes_periodo = membros_base_periodo.filter(tipo_pessoa__nome__iexact='Visitante').count()
    total_visitantes_periodo_anterior = membros_base_periodo_anterior.filter(
        tipo_pessoa__nome__iexact='Visitante'
    ).count()

    def _comparativo_card(label, atual, anterior, melhora_quando='up'):
        diferenca = atual - anterior
        if diferenca == 0:
            tone = 'is-neutral'
            icon = 'fas fa-minus'
        else:
            subiu = diferenca > 0
            melhorou = subiu if melhora_quando == 'up' else not subiu
            tone = 'is-positive' if melhorou else 'is-warning'
            icon = 'fas fa-arrow-up' if subiu else 'fas fa-arrow-down'

        return {
            'label': label,
            'atual': atual,
            'anterior': anterior,
            'diferenca': diferenca,
            'diferenca_label': f"{diferenca:+d}",
            'tone': tone,
            'icon': icon,
        }

    comparativo_periodo_cards = [
        _comparativo_card('Entradas de membros', novos_membros_periodo, novos_membros_periodo_anterior, 'up'),
        _comparativo_card('Pendencias cadastrais', total_pendencias_cadastro_periodo, total_pendencias_cadastro_periodo_anterior, 'down'),
        _comparativo_card('Visitantes registrados', total_visitantes_periodo, total_visitantes_periodo_anterior, 'up'),
    ]

    igrejas_ids = membros_para_relatorios.values_list('igreja_id', flat=True).distinct()
    contas_vencidas = ContaPagar.objects.filter(
        igreja_id__in=igrejas_ids,
        status='VEN',
        data_vencimento__range=(data_inicio_periodo, data_fim_periodo),
    )
    total_contas_vencidas = contas_vencidas.count()
    valor_total_contas_vencidas = contas_vencidas.aggregate(total=Sum('valor'))['total'] or 0

    assinatura = _assinatura_alerta(ministerio, hoje)

    _meses_ignorado, membros_evolucao, novos_membros_por_mes = _series_mensal_membros(membros_para_relatorios, hoje)
    aniversariantes_ontem, aniversariantes_hoje, aniversariantes_amanha = _aniversariantes_janela(
        membros_para_relatorios,
        hoje,
    )
    membros_para_grafico_tipo = Membro.objects.filter(igreja__in=igrejas_filtro)
    membros_para_grafico_tipo_periodo = membros_para_grafico_tipo.filter(
        data_entrada__isnull=False,
        data_entrada__range=(data_inicio_periodo, data_fim_periodo),
    )
    pie_labels, pie_values = _pie_tipos_pessoa(membros_para_grafico_tipo_periodo)
    categoria_labels, categoria_values = _categoria_evento_data(igrejas_filtro)

    total_membros = total_pessoas_igreja
    total_visitantes = membros_base_para_grafico_status.filter(tipo_pessoa__nome__iexact='Visitante').count()
    total_cargos = Cargo.objects.filter(membrocargo__membro__igreja__in=igrejas_filtro).distinct().count()
    total_grupos_casa = GrupoCasa.objects.filter(igreja__in=igrejas_filtro).count()
    total_acompanhamentos = AcompanhamentoVisita.objects.filter(membro__igreja__in=igrejas_filtro).count()
    total_tags = Tag.objects.filter(pessoas__igreja__in=igrejas_filtro).distinct().count()
    total_associacoes = Membro.objects.filter(usuario__isnull=False, igreja__in=igrejas_filtro).count()
    total_relatorios = membros_base_para_grafico_status.filter(
        tipo_pessoa__nome__in=['Membro', 'Obreiro'],
        status_pessoa__nome__in=['Ativo', 'Em Disciplina'],
    ).count()

    insights_dashboard = _gerar_insights_dashboard(
        membros_para_relatorios,
        membros_base_periodo,
        data_inicio_periodo,
        data_fim_periodo,
        novos_membros_periodo,
        total_pendencias_cadastro_periodo,
    )

    dashboard_visibility = _dashboard_visibility_flags(request)
    is_pastor_dashboard = _user_has_permission_level_or_higher(request.user, PASTOR_LOCAL)

    periodo_visitacao_dashboard = (request.GET.get('periodo_visitacao_dashboard') or '3m').strip().lower()
    try:
        familias_sem_visita_dashboard_meses = int(request.GET.get('familias_sem_visita_dashboard_meses', 3))
    except (TypeError, ValueError):
        familias_sem_visita_dashboard_meses = 3

    visitacao_metrics_dashboard = build_visitacao_metrics(
        igrejas_filtro,
        periodo_key=periodo_visitacao_dashboard,
        familias_sem_visita_meses=familias_sem_visita_dashboard_meses,
        limite_familias=12,
    )

    context = {
        'status_data_json': json.dumps(status_data_list),
        'status_labels_json': json.dumps([item['status'] for item in status_data_list]),
        'status_values_json': json.dumps([item['total'] for item in status_data_list]),
        'genero_data_json': json.dumps(genero_data_normalized),
        'genero_labels_json': json.dumps([item['genero'] for item in genero_data_normalized]),
        'genero_values_json': json.dumps([item['total'] for item in genero_data_normalized]),
        'faixa_etaria_data_json': json.dumps(faixa_etaria_data),
        'faixa_labels_json': json.dumps([item['faixa_etaria'] for item in faixa_etaria_data]),
        'faixa_values_json': json.dumps([item['total'] for item in faixa_etaria_data]),
        'novos_membros_periodo': novos_membros_periodo,
        'aniversariantes_mes_atual_count': aniversariantes_mes_atual_count,
        'media_idade_membros': media_idade_membros,
        'ministerio': ministerio,
        'aniversariantes_proximos': aniversariantes_proximos,
        'titulo_pagina': titulo_contextual,
        'igreja_ativa_atual': request.igreja_ativa,
        'total_membros_ativos': membros_para_relatorios.count(),
        'total_pessoas_igreja': total_pessoas_igreja,
        'novos_membros_ultimo_mes': novos_membros_periodo,
        'total_pendencias_cadastro': total_pendencias_cadastro,
        'total_pendencias_cadastro_periodo': total_pendencias_cadastro_periodo,
        'total_contas_vencidas': total_contas_vencidas,
        'valor_total_contas_vencidas': valor_total_contas_vencidas,
        'assinatura_alerta': assinatura,
        'periodo_filtro': periodo_info['periodo'],
        'periodo_label': periodo_info['periodo_label'],
        'periodo_data_inicio': data_inicio_periodo.strftime('%Y-%m-%d'),
        'periodo_data_fim': data_fim_periodo.strftime('%Y-%m-%d'),
        'evolucao_meses_labels_json': json.dumps(meses_labels),
        'evolucao_membros_json': json.dumps(evolucao_por_tipo['Membro']),
        'evolucao_congregados_json': json.dumps(evolucao_por_tipo['Congregado']),
        'evolucao_novos_convertidos_json': json.dumps(evolucao_por_tipo['Novo Convertido']),
        'evolucao_visitantes_json': json.dumps(evolucao_por_tipo['Visitante']),
        'pie_labels_json': json.dumps(pie_labels),
        'pie_values_json': json.dumps(pie_values),
        'categoria_evento_labels_json': json.dumps(categoria_labels),
        'categoria_evento_values_json': json.dumps(categoria_values),
        'total_membros': total_membros,
        'total_visitantes': total_visitantes,
        'total_cargos': total_cargos,
        'total_grupos_casa': total_grupos_casa,
        'total_relatorios': total_relatorios,
        'total_acompanhamentos': total_acompanhamentos,
        'total_tags': total_tags,
        'total_associacoes': total_associacoes,
        'insights_dashboard': insights_dashboard,
        'comparativo_periodo_cards': comparativo_periodo_cards,
        'periodo_anterior_label': f"{periodo_anterior_inicio.strftime('%d/%m/%Y')} a {periodo_anterior_fim.strftime('%d/%m/%Y')}",
        'dashboard_visibility': dashboard_visibility,
        'is_pastor_dashboard': is_pastor_dashboard,
        'visitacao_metrics_dashboard': visitacao_metrics_dashboard,
        # Compatibilidade temporaria para evitar quebra em templates/partials legados.
        'pode_ver_alerta_financeiro': dashboard_visibility['alertas']['financeiro'],
        'pode_ver_alerta_assinatura': dashboard_visibility['alertas']['assinatura'],
    }

    igrejas_permitidas_ctx = getattr(request, 'igrejas_permitidas', Igreja.objects.none())
    if request.igreja_ativa and igrejas_permitidas_ctx.filter(pk=request.igreja_ativa.pk).exists():
        context['scope_label'] = f'Igreja: {request.igreja_ativa.nome_igreja}'
    elif igrejas_filtro.exists():
        _n = igrejas_filtro.count()
        context['scope_label'] = f"Consolidado — {ministerio.nome_fantasia} ({_n} {'igrejas' if _n != 1 else 'igreja'})"
    else:
        context['scope_label'] = None

    return render(request, 'secretaria/dashboard.html', context)


@login_required
@page_access_required('dashboard_secretaria')
def exportar_dashboard_csv(request):
    ministerio = get_ministerio_or_error(request)
    igrejas_permitidas = getattr(request, 'igrejas_permitidas', None)
    if igrejas_permitidas is None:
        igrejas_permitidas = get_allowed_churches_for_membros(request.user, ministerio)
    igrejas_filtro = get_request_scoped_churches(request, igrejas_permitidas)

    hoje_data = date.today()
    periodo_info = _parse_periodo_dashboard(request, hoje_data)
    data_inicio_periodo = periodo_info['data_inicio']
    data_fim_periodo = periodo_info['data_fim']

    dataset = (request.GET.get('dataset') or 'resumo').strip().lower()
    datasets_validos = {'resumo', 'evolucao', 'status', 'genero', 'faixa', 'tipo', 'categoria'}
    if dataset not in datasets_validos:
        dataset = 'resumo'

    membros_para_relatorios = Membro.objects.filter(
        igreja__in=igrejas_filtro,
        tipo_pessoa__nome__iexact='Membro',
        status_pessoa__nome__iexact='Ativo',
    )
    membros_base_para_grafico_status = Membro.objects.filter(igreja__in=igrejas_filtro)
    membros_para_relatorios_periodo = membros_para_relatorios.filter(
        data_entrada__isnull=False,
        data_entrada__range=(data_inicio_periodo, data_fim_periodo),
    )
    membros_base_periodo = membros_base_para_grafico_status.filter(
        data_entrada__isnull=False,
        data_entrada__range=(data_inicio_periodo, data_fim_periodo),
    )

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = (
        f'attachment; filename="dashboard_secretaria_{dataset}_{hoje_data.strftime("%Y%m%d")}.csv"'
    )
    writer = csv.writer(response)

    writer.writerow(['dataset', dataset])
    writer.writerow(['periodo', periodo_info['periodo_label']])
    writer.writerow(['data_inicio', data_inicio_periodo.strftime('%Y-%m-%d')])
    writer.writerow(['data_fim', data_fim_periodo.strftime('%Y-%m-%d')])
    writer.writerow([])

    if dataset == 'resumo':
        pendencias_cadastro_base = membros_para_relatorios.filter(
            Q(nascimento__isnull=True) | Q(email__isnull=True) | Q(email='')
        ).count()
        pendencias_cadastro_periodo = membros_para_relatorios_periodo.filter(
            Q(nascimento__isnull=True) | Q(email__isnull=True) | Q(email='')
        ).count()
        igrejas_ids = membros_para_relatorios.values_list('igreja_id', flat=True).distinct()
        contas_vencidas = ContaPagar.objects.filter(
            igreja_id__in=igrejas_ids,
            status='VEN',
            data_vencimento__range=(data_inicio_periodo, data_fim_periodo),
        )
        writer.writerow(['indicador', 'valor'])
        writer.writerow(['novos_membros_periodo', membros_para_relatorios_periodo.count()])
        writer.writerow(['membros_ativos_total_escopo', membros_para_relatorios.count()])
        writer.writerow(['pendencias_cadastro_base_ativa', pendencias_cadastro_base])
        writer.writerow(['pendencias_cadastro_periodo', pendencias_cadastro_periodo])
        writer.writerow(['contas_vencidas_periodo', contas_vencidas.count()])
        writer.writerow(['valor_total_contas_vencidas_periodo', contas_vencidas.aggregate(total=Sum('valor'))['total'] or 0])
        return response

    if dataset == 'evolucao':
        meses_labels, evolucao_por_tipo = _series_evolucao_por_tipo(
            membros_base_para_grafico_status,
            data_inicio_periodo,
            data_fim_periodo,
        )
        writer.writerow(['mes', 'membro', 'congregado', 'novo_convertido', 'visitante'])
        for idx, mes in enumerate(meses_labels):
            writer.writerow([
                mes,
                evolucao_por_tipo['Membro'][idx],
                evolucao_por_tipo['Congregado'][idx],
                evolucao_por_tipo['Novo Convertido'][idx],
                evolucao_por_tipo['Visitante'][idx],
            ])
        return response

    if dataset == 'status':
        status_data_qs = membros_base_periodo.values('status_pessoa__nome').annotate(total=Count('chave')).order_by('status_pessoa__nome')
        writer.writerow(['status', 'total'])
        for item in status_data_qs:
            if item['status_pessoa__nome']:
                writer.writerow([item['status_pessoa__nome'], item['total']])
        return response

    if dataset == 'genero':
        genero_data_qs = membros_para_relatorios_periodo.values('genero').annotate(total=Count('chave'))
        genero_map = {'F': 'Feminino', 'M': 'Masculino', '': 'Não Informado', None: 'Não Informado'}
        acumulado = defaultdict(int)
        for item in genero_data_qs:
            acumulado[genero_map.get(item['genero'], 'Não Informado')] += item['total']
        writer.writerow(['genero', 'total'])
        for genero, total in acumulado.items():
            writer.writerow([genero, total])
        return response

    if dataset == 'faixa':
        idades = _idades_lista(membros_para_relatorios_periodo, hoje_data)
        faixa_etaria_data = _calcular_faixas_etarias(membros_para_relatorios_periodo, idades)
        writer.writerow(['faixa_etaria', 'total'])
        for item in faixa_etaria_data:
            writer.writerow([item['faixa_etaria'], item['total']])
        return response

    if dataset == 'tipo':
        membros_para_grafico_tipo_periodo = Membro.objects.filter(
            igreja__in=igrejas_filtro,
            data_entrada__isnull=False,
            data_entrada__range=(data_inicio_periodo, data_fim_periodo),
        )
        pie_labels, pie_values = _pie_tipos_pessoa(membros_para_grafico_tipo_periodo)
        writer.writerow(['tipo', 'total'])
        for label, value in zip(pie_labels, pie_values):
            writer.writerow([label, value])
        return response

    categoria_labels, categoria_values = _categoria_evento_data(
        igrejas_filtro,
        data_inicio_periodo,
        data_fim_periodo,
    )
    writer.writerow(['categoria_evento', 'participacoes'])
    for label, value in zip(categoria_labels, categoria_values):
        writer.writerow([label, value])
    return response
