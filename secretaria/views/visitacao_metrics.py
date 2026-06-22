"""Métricas de visitação para visões operacionais e pastorais."""

from calendar import monthrange
from datetime import date, datetime, time, timedelta

from django.db.models import Max, Q
from django.utils import timezone

from secretaria.models import AcompanhamentoVisita, GrupoCasa, Membro, VisitaGrupoCasa


def _subtrair_meses(base: date, meses: int) -> date:
    """Subtrai meses preservando o dia quando possível."""
    meses = max(1, int(meses or 1))
    month_index = (base.month - 1) - meses
    year = base.year + (month_index // 12)
    month = (month_index % 12) + 1
    day = min(base.day, monthrange(year, month)[1])
    return date(year, month, day)


def _resolver_periodo(periodo_key: str):
    periodo_key = (periodo_key or '3m').strip().lower()
    hoje = timezone.localdate()

    if periodo_key in {'7d', '30d', '90d', '180d'}:
        dias = int(periodo_key.replace('d', ''))
        inicio = hoje - timedelta(days=dias - 1)
        return periodo_key, inicio, hoje, f'Últimos {dias} dias'

    if periodo_key.endswith('m') and periodo_key[:-1].isdigit():
        meses = max(1, min(24, int(periodo_key[:-1])))
        inicio = _subtrair_meses(hoje, meses)
        return f'{meses}m', inicio, hoje, f'Últimos {meses} meses'

    # Fallback seguro
    inicio = _subtrair_meses(hoje, 3)
    return '3m', inicio, hoje, 'Últimos 3 meses'


def build_visitacao_metrics(igrejas_qs, periodo_key='3m', familias_sem_visita_meses=3, limite_familias=20):
    """Retorna métricas de visitação por pessoa e por família/casa no escopo informado."""
    periodo_norm, data_inicio, data_fim, periodo_label = _resolver_periodo(periodo_key)
    familias_sem_visita_meses = max(1, min(24, int(familias_sem_visita_meses or 3)))

    inicio_dt = timezone.make_aware(datetime.combine(data_inicio, time.min), timezone.get_current_timezone())
    corte_sem_visita_date = _subtrair_meses(timezone.localdate(), familias_sem_visita_meses)
    corte_sem_visita_dt = timezone.make_aware(
        datetime.combine(corte_sem_visita_date, time.min),
        timezone.get_current_timezone(),
    )

    pessoas_base_qs = Membro.objects.filter(
        igreja__in=igrejas_qs,
        status_pessoa__nome__in=['Ativo', 'Desligado', 'Em Disciplina'],
    )
    total_pessoas_base = pessoas_base_qs.count()

    pessoas_visitadas = AcompanhamentoVisita.objects.filter(
        membro__igreja__in=igrejas_qs,
        data__gte=inicio_dt,
    ).filter(
        Q(tipo_contato='visita') | Q(visita_grupo_casa__isnull=False)
    ).values('membro_id').distinct().count()
    pessoas_nao_visitadas = max(total_pessoas_base - pessoas_visitadas, 0)

    percentual_visitadas = round((pessoas_visitadas / total_pessoas_base) * 100, 1) if total_pessoas_base else 0
    percentual_nao_visitadas = round(100 - percentual_visitadas, 1) if total_pessoas_base else 0

    familias_base_qs = GrupoCasa.objects.filter(igreja__in=igrejas_qs)
    total_familias = familias_base_qs.count()

    familias_visitadas_periodo = VisitaGrupoCasa.objects.filter(
        grupo_casa__igreja__in=igrejas_qs,
        data__gte=inicio_dt,
    ).values('grupo_casa_id').distinct().count()

    familias_sem_visita_qs = familias_base_qs.annotate(
        ultima_visita=Max('visitas__data')
    ).filter(
        Q(ultima_visita__isnull=True) | Q(ultima_visita__lt=corte_sem_visita_dt)
    ).select_related('igreja').order_by('ultima_visita', 'nome', 'rua')

    familias_sem_visita_lista = []
    for grupo in familias_sem_visita_qs[:limite_familias]:
        familias_sem_visita_lista.append({
            'id': grupo.id,
            'nome': grupo.nome or 'Grupo sem nome',
            'endereco_curto': ', '.join(
                [part for part in [grupo.rua, grupo.numero, grupo.bairro] if part]
            ) or 'Endereço não informado',
            'igreja_nome': grupo.igreja.nome_igreja if grupo.igreja_id else '',
            'ultima_visita': grupo.ultima_visita,
        })

    return {
        'periodo_key': periodo_norm,
        'periodo_label': periodo_label,
        'periodo_data_inicio': data_inicio,
        'periodo_data_fim': data_fim,
        'familias_sem_visita_meses': familias_sem_visita_meses,
        'total_pessoas_base': total_pessoas_base,
        'pessoas_visitadas': pessoas_visitadas,
        'pessoas_nao_visitadas': pessoas_nao_visitadas,
        'percentual_visitadas': percentual_visitadas,
        'percentual_nao_visitadas': percentual_nao_visitadas,
        'visitacao_pizza_labels': ['Visitadas', 'Não visitadas'],
        'visitacao_pizza_values': [pessoas_visitadas, pessoas_nao_visitadas],
        'total_familias': total_familias,
        'familias_visitadas_periodo': familias_visitadas_periodo,
        'familias_sem_visita_total': familias_sem_visita_qs.count(),
        'familias_sem_visita_lista': familias_sem_visita_lista,
    }
