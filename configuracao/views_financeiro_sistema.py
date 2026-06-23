import json
from datetime import date
from decimal import Decimal

from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .dev_access import user_is_dev_finance
from .models import CategoriaGastoSistema, GastoSistema, HistoricoAssinatura


CATEGORIAS_PADRAO = [
    ('hospedagens', 'Hospedagens', 10),
    ('dominios', 'Dominios', 20),
    ('ia', 'IA', 30),
    ('outros', 'Outros', 90),
]


def _month_bounds(year, month):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end


def _shift_month(base_date, offset):
    year = base_date.year
    month = base_date.month + offset
    while month > 12:
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1
    return date(year, month, 1)


def _garantir_categorias_padrao():
    for slug, nome, ordem in CATEGORIAS_PADRAO:
        CategoriaGastoSistema.objects.get_or_create(
            slug=slug,
            defaults={
                'nome': nome,
                'ordem': ordem,
                'ativo': True,
            },
        )


class GastoSistemaForm(forms.ModelForm):
    class Meta:
        model = GastoSistema
        fields = ['categoria', 'descricao', 'valor', 'data_competencia', 'data_pagamento', 'observacao']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: VPS produção'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'data_competencia': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_pagamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = CategoriaGastoSistema.objects.filter(ativo=True).order_by('ordem', 'nome')
        self.fields['categoria'].empty_label = 'Selecione a categoria'


@staff_member_required
def financeiro_sistema_admin(request):
    if not user_is_dev_finance(request.user):
        raise PermissionDenied('Acesso restrito ao desenvolvedor.')

    _garantir_categorias_padrao()

    hoje = timezone.localdate()
    mes_param = (request.GET.get('mes') or '').strip()
    try:
        ano, mes = map(int, mes_param.split('-'))
        data_referencia = date(ano, mes, 1)
    except Exception:
        data_referencia = date(hoje.year, hoje.month, 1)

    mes_inicio, mes_fim = _month_bounds(data_referencia.year, data_referencia.month)

    if request.method == 'POST':
        form = GastoSistemaForm(request.POST)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.criado_por = request.user
            gasto.save()
            messages.success(request, 'Gasto registrado com sucesso.')
            return redirect(f"{reverse('admin_financeiro_sistema')}?mes={data_referencia:%Y-%m}")
        messages.error(request, 'Nao foi possivel salvar o gasto. Verifique os campos.')
    else:
        form = GastoSistemaForm(initial={'data_competencia': data_referencia})

    recebimentos_qs = HistoricoAssinatura.objects.filter(tipo='mensalidade', status='paga')
    gastos_qs = GastoSistema.objects.select_related('categoria')

    recebimentos_mes_qs = recebimentos_qs.filter(data_inicio__date__gte=mes_inicio, data_inicio__date__lt=mes_fim)
    gastos_mes_qs = gastos_qs.filter(data_competencia__gte=mes_inicio, data_competencia__lt=mes_fim)

    total_receitas_mes = recebimentos_mes_qs.aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
    total_gastos_mes = gastos_mes_qs.aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
    liquido_mes = total_receitas_mes - total_gastos_mes

    total_receitas_geral = recebimentos_qs.aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
    total_gastos_geral = gastos_qs.aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
    acumulado = total_receitas_geral - total_gastos_geral

    recebimentos_por_mes = {
        row['mes'].date(): row['total']
        for row in recebimentos_qs.annotate(mes=TruncMonth('data_inicio')).values('mes').annotate(total=Sum('valor'))
    }
    gastos_por_mes = {
        row['mes'].date(): row['total']
        for row in gastos_qs.annotate(mes=TruncMonth('data_competencia')).values('mes').annotate(total=Sum('valor'))
    }

    meses_series = [_shift_month(data_referencia, offset) for offset in range(-11, 1)]
    labels = [m.strftime('%m/%Y') for m in meses_series]
    receitas_series = [float(recebimentos_por_mes.get(m, Decimal('0.00'))) for m in meses_series]
    gastos_series = [float(gastos_por_mes.get(m, Decimal('0.00'))) for m in meses_series]
    liquido_series = [round(receitas_series[i] - gastos_series[i], 2) for i in range(len(labels))]

    categorias_breakdown = list(
        gastos_mes_qs.values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')
    )

    context = {
        'title': 'Financeiro do Sistema',
        'mes_referencia': data_referencia,
        'mes_referencia_str': data_referencia.strftime('%Y-%m'),
        'mes_anterior_str': _shift_month(data_referencia, -1).strftime('%Y-%m'),
        'mes_posterior_str': _shift_month(data_referencia, 1).strftime('%Y-%m'),
        'form_gasto': form,
        'total_receitas_mes': total_receitas_mes,
        'total_gastos_mes': total_gastos_mes,
        'liquido_mes': liquido_mes,
        'acumulado': acumulado,
        'total_receitas_geral': total_receitas_geral,
        'total_gastos_geral': total_gastos_geral,
        'recebimentos_recentes': recebimentos_qs.select_related('ministerio', 'plano').order_by('-data_inicio')[:12],
        'gastos_recentes': gastos_qs.order_by('-data_competencia', '-id')[:12],
        'categorias_breakdown': categorias_breakdown,
        'chart_labels_json': json.dumps(labels),
        'chart_receitas_json': json.dumps(receitas_series),
        'chart_gastos_json': json.dumps(gastos_series),
        'chart_liquido_json': json.dumps(liquido_series),
    }
    return render(request, 'admin/financeiro_sistema.html', context)
