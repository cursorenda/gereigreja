"""
secretaria/views/relatorios.py
Views de relatórios: linha do tempo e relatório de reunião de membros.
"""
import json
import logging
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta

from django import forms as _forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET

from core.decorators import page_access_required, verificar_assinatura_valida
from core.utils import get_ministerio_or_error
from secretaria.views._helpers import _membros_queryset_por_escopo
from secretaria.models import (
    Membro, StatusHistorico, StatusPessoa, TimelineEvent, TipoPessoa,
)
from secretaria.utils import get_allowed_churches_for_membros

logger = logging.getLogger(__name__)


@login_required
@page_access_required('secretaria_acompanhamentos')
@verificar_assinatura_valida
def linha_do_tempo(request):
    periodo_predefinido = request.GET.get('periodo_predefinido')
    if not periodo_predefinido and not request.GET:
        from django.urls import reverse
        return redirect(f"{reverse('secretaria:linha_do_tempo')}?periodo_predefinido=mes_atual")

    TIPO_COLORS = {
        'membro': 'bg-primary',
        'visitante': 'bg-info',
        'obreiro': 'bg-success',
        'congregado': 'bg-warning',
        'novo convertido': 'bg-secondary',
    }
    STATUS_COLORS = {
        'ativo': 'bg-success',
        'inativo': 'bg-secondary',
        'em disciplina': 'bg-warning',
        'desligado': 'bg-danger',
        'transferido': 'bg-info',
        'falecido': 'bg-dark',
    }

    class TimelineFilterForm(_forms.Form):
        tipo_evento = _forms.MultipleChoiceField(required=False, choices=getattr(TimelineEvent, 'TIPO_EVENTO_CHOICES', []))
        data_inicio = _forms.DateField(required=False)
        data_fim = _forms.DateField(required=False)
        tipo_pessoa_novo = _forms.ModelMultipleChoiceField(required=False, queryset=TipoPessoa.objects.all())
        status_pessoa_novo = _forms.ModelMultipleChoiceField(required=False, queryset=StatusPessoa.objects.all())

    form = TimelineFilterForm(request.GET or None)

    eventos_timeline = []
    tipos_evento = form.cleaned_data.get('tipo_evento') if form.is_valid() else []
    data_inicio = form.cleaned_data.get('data_inicio') if form.is_valid() else None
    data_fim = form.cleaned_data.get('data_fim') if form.is_valid() else None

    if periodo_predefinido == 'mes_atual' and not data_inicio and not data_fim:
        hoje = datetime.today()
        data_inicio = hoje.replace(day=1)
        if hoje.month == 12:
            data_fim = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            data_fim = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
        data_inicio = timezone.make_aware(datetime.combine(data_inicio, datetime.min.time()))
        data_fim = timezone.make_aware(datetime.combine(data_fim, datetime.max.time()))

    tipos_pessoa_novo = form.cleaned_data.get('tipo_pessoa_novo') if form.is_valid() else None
    status_pessoa_novo = form.cleaned_data.get('status_pessoa_novo') if form.is_valid() else None

    if data_inicio:
        if isinstance(data_inicio, datetime):
            if timezone.is_naive(data_inicio):
                data_inicio = timezone.make_aware(data_inicio)
        else:
            data_inicio = timezone.make_aware(datetime.combine(data_inicio, datetime.min.time()))
    if data_fim:
        if isinstance(data_fim, datetime):
            if timezone.is_naive(data_fim):
                data_fim = timezone.make_aware(data_fim)
        else:
            data_fim = timezone.make_aware(datetime.combine(data_fim, datetime.max.time()))

    # Restringe eventos ao escopo efetivo do request (igreja ativa ou permitidas).
    membros_escopo_ids = _membros_queryset_por_escopo(request).values('pk')

    entrada_qs = TimelineEvent.objects.select_related('membro').filter(
        membro_id__in=membros_escopo_ids
    )
    if tipos_evento:
        entrada_qs = entrada_qs.filter(tipo_evento__in=tipos_evento)
    if data_inicio:
        entrada_qs = entrada_qs.filter(data__gte=data_inicio)
    if data_fim:
        entrada_qs = entrada_qs.filter(data__lte=data_fim)
    for evento in entrada_qs:
        evento.data_evento = getattr(evento, 'data', None)
        if hasattr(evento, 'tipo_pessoa_novo') and evento.tipo_evento == 'entrada':
            evento.valor_anterior = '-'
            evento.novo_valor = getattr(evento, 'tipo_pessoa_novo', None)
            nome = evento.membro.nome if hasattr(evento, 'membro') and evento.membro else 'Alguém'
            tipo = evento.novo_valor if evento.novo_valor else 'membro'
            evento.descricao_evento = f"{nome} entrou como {tipo}" if tipo else f"{nome} entrou"
        else:
            evento.valor_anterior = getattr(evento, 'valor_anterior', '-')
            evento.novo_valor = getattr(evento, 'novo_valor', '-')
            nome = evento.membro.nome if hasattr(evento, 'membro') and evento.membro else 'Alguém'
            tipo = evento.novo_valor if evento.novo_valor else 'membro'
            evento.descricao_evento = f"{nome} mudou para {tipo}" if tipo else f"{nome} teve uma mudança"
        if (
            hasattr(evento, 'membro') and evento.membro and getattr(evento.membro, 'nome', None)
            and (
                (hasattr(evento, 'valor_anterior') and evento.valor_anterior and evento.valor_anterior != '-') or
                (hasattr(evento, 'novo_valor') and evento.novo_valor and evento.novo_valor != '-')
            )
        ):
            eventos_timeline.append(evento)

    transicao_qs = StatusHistorico.objects.select_related(
        'membro', 'status_pessoa_anterior', 'status_pessoa_novo',
        'tipo_pessoa_anterior', 'tipo_pessoa_novo',
    ).filter(membro_id__in=membros_escopo_ids)
    if data_inicio:
        transicao_qs = transicao_qs.filter(data_transicao__gte=data_inicio)
    if data_fim:
        transicao_qs = transicao_qs.filter(data_transicao__lte=data_fim)
    if tipos_pessoa_novo:
        transicao_qs = transicao_qs.filter(tipo_pessoa_novo__in=tipos_pessoa_novo)
    if status_pessoa_novo:
        transicao_qs = transicao_qs.filter(status_pessoa_novo__in=status_pessoa_novo)
    for transicao in transicao_qs:
        transicao.data_evento = getattr(transicao, 'data_transicao', None)
        if hasattr(transicao, 'tipo_pessoa_anterior') and hasattr(transicao, 'tipo_pessoa_novo') and transicao.tipo_pessoa_anterior != transicao.tipo_pessoa_novo:
            transicao.get_tipo_evento_display = lambda: "Mudança de Tipo"
            transicao.tipo_evento = 'mudanca_tipo'
            transicao.valor_anterior = transicao.tipo_pessoa_anterior.nome if transicao.tipo_pessoa_anterior else '-'
            transicao.novo_valor = transicao.tipo_pessoa_novo.nome if transicao.tipo_pessoa_novo else '-'
            nome = transicao.membro.nome if hasattr(transicao, 'membro') and transicao.membro else 'Alguém'
            tipo = transicao.novo_valor if transicao.novo_valor else 'membro'
            transicao.descricao_evento = f"{nome} virou {tipo}"
        elif hasattr(transicao, 'status_pessoa_anterior') and hasattr(transicao, 'status_pessoa_novo') and transicao.status_pessoa_anterior != transicao.status_pessoa_novo:
            transicao.get_tipo_evento_display = lambda: "Mudança de Status"
            transicao.tipo_evento = 'mudanca_status'
            transicao.valor_anterior = transicao.status_pessoa_anterior.nome if transicao.status_pessoa_anterior else '-'
            transicao.novo_valor = transicao.status_pessoa_novo.nome if transicao.status_pessoa_novo else '-'
            nome = transicao.membro.nome if hasattr(transicao, 'membro') and transicao.membro else 'Alguém'
            status = transicao.novo_valor if transicao.novo_valor else 'ativo'
            transicao.descricao_evento = f"{nome} ficou {status}"
        else:
            transicao.get_tipo_evento_display = lambda: "Mudança de Tipo/Status"
            transicao.tipo_evento = 'mudanca_tipo_status'
            transicao.valor_anterior = '-'
            transicao.novo_valor = '-'
            nome = transicao.membro.nome if hasattr(transicao, 'membro') and transicao.membro else 'Alguém'
            transicao.descricao_evento = f"{nome} teve uma mudança"
        if (
            hasattr(transicao, 'membro') and transicao.membro and getattr(transicao.membro, 'nome', None)
            and (
                (hasattr(transicao, 'valor_anterior') and transicao.valor_anterior and transicao.valor_anterior != '-') or
                (hasattr(transicao, 'novo_valor') and transicao.novo_valor and transicao.novo_valor != '-')
            )
        ):
            eventos_timeline.append(transicao)

    eventos_timeline = sorted(eventos_timeline, key=lambda e: e.data_evento, reverse=True)
    eventos_por_data = OrderedDict()
    for evento in eventos_timeline:
        data_str = evento.data_evento.strftime('%Y-%m-%d')
        if data_str not in eventos_por_data:
            eventos_por_data[data_str] = []
        eventos_por_data[data_str].append(evento)

    eventos_por_mes_tipo = defaultdict(lambda: defaultdict(int))
    for evento in eventos_timeline:
        mes = evento.data_evento.strftime('%Y-%m') if evento.data_evento else ''
        eventos_por_mes_tipo[mes][evento.get_tipo_evento_display()] += 1
    meses = sorted(eventos_por_mes_tipo.keys())
    tipos_set = set()
    for tipo_dict in eventos_por_mes_tipo.values():
        tipos_set.update(tipo_dict.keys())
    tipos_list = sorted(tipos_set)
    chart_labels = meses
    chart_datasets = []
    for tipo in tipos_list:
        data = [eventos_por_mes_tipo[mes].get(tipo, 0) for mes in meses]
        chart_datasets.append({'label': tipo, 'data': data})
    chart_data = {'labels': chart_labels, 'datasets': chart_datasets}

    status_pessoa_list = StatusPessoa.objects.all().order_by('nome')
    context = {
        'eventos_por_data': eventos_por_data,
        'form': form,
        'chart_data_json': json.dumps(chart_data),
        'mostrar_anterior': request.GET.get('mostrar_anterior'),
        'status_pessoa_list': status_pessoa_list,
        'periodo_predefinido': request.GET.get('periodo_predefinido', 'mes_atual'),
    }
    logger.warning(
        'linha_do_tempo: eventos_timeline=%d, eventos_por_data=%d',
        len(eventos_timeline), len(eventos_por_data),
    )
    return render(request, 'secretaria/linha_do_tempo.html', context)


@login_required
def relatorio_reuniao_membros(request):
    """Gera relatório HTML para impressão da reunião de membros."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    igreja = None
    if request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
        igreja = request.igreja_ativa
    elif allowed_churches.exists():
        igreja = allowed_churches.first()
    else:
        messages.error(request, "Nenhuma igreja selecionada ou permitida para gerar relatório.")
        return redirect('secretaria:dashboard')

    membros = Membro.objects.filter(
        igreja=igreja,
        tipo_pessoa__nome__in=['Membro', 'Obreiro'],
        status_pessoa__nome__in=['Ativo', 'Em Disciplina'],
    ).order_by('nome')

    nome_igreja = igreja.nome_igreja if hasattr(igreja, 'nome_igreja') else str(igreja)
    rua = getattr(igreja, 'rua', '')
    numero = getattr(igreja, 'numero_casa', '')
    bairro = getattr(igreja, 'bairro', '')
    cidade = getattr(igreja, 'cidade', '')
    estado = getattr(igreja, 'estado', '')
    endereco_completo = f"{rua}, {numero} - {bairro}, {cidade} - {estado}".strip(', -')
    razao_social = getattr(ministerio, 'razao_social', '')
    nome_fantasia = getattr(ministerio, 'nome_fantasia', '')
    nome_ministerio = razao_social or nome_fantasia or str(ministerio)
    pastor_local = getattr(igreja, 'pastor_local', '')
    pastor_regional = getattr(igreja, 'pastor_regional', '')
    data_reuniao = timezone.now().strftime('%d de %B de %Y')

    logo_igreja_url = igreja.logo1_url
    logo_ministerio_url = ministerio.logo_url

    context = {
        'membros': membros,
        'nome_igreja': nome_igreja,
        'bairro': bairro,
        'cidade': cidade,
        'estado': estado,
        'rua': rua,
        'numero': numero,
        'endereco_completo': endereco_completo,
        'nome_ministerio': nome_ministerio,
        'pastor_local': pastor_local,
        'pastor_regional': pastor_regional,
        'data_reuniao': data_reuniao,
        'logo_igreja_url': logo_igreja_url,
        'logo_ministerio_url': logo_ministerio_url,
    }
    return render(request, 'secretaria/relatorio_reuniao_membros.html', context)
