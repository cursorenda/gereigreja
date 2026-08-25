"""Filtros reutilizáveis de isolamento de dados da Escola Bíblica."""

from django.db.models import Q


def aplicar_igreja_filtro_inicial(*, form, igreja_id):
    """Pré-seleciona uma igreja somente quando ela estiver disponível no formulário."""
    if not igreja_id or 'igreja' not in form.fields:
        return
    try:
        igreja_id = int(igreja_id)
    except (TypeError, ValueError):
        return
    if form.fields['igreja'].queryset.filter(pk=igreja_id).exists():
        form.fields['igreja'].initial = igreja_id


def filtrar_turmas_por_igrejas(queryset, igrejas):
    return queryset.filter(
        Q(igreja__in=igrejas)
        | Q(igreja__isnull=True, membros__igreja__in=igrejas),
    ).distinct()


def filtrar_classes_por_igrejas(queryset, igrejas):
    return queryset.filter(
        Q(igreja__in=igrejas)
        | Q(igreja__isnull=True, turma__membros__igreja__in=igrejas),
    ).distinct()


def filtrar_alunos_por_igrejas(queryset, igrejas):
    return queryset.filter(
        Q(turma__igreja__in=igrejas)
        | Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas),
    ).distinct()


def filtrar_ofertas_por_igrejas(queryset, igrejas):
    return queryset.filter(
        Q(turma__igreja__in=igrejas)
        | Q(turma__igreja__isnull=True, turma__membros__igreja__in=igrejas)
        | Q(turma__isnull=True, classe__igreja__in=igrejas)
        | Q(
            turma__isnull=True,
            classe__igreja__isnull=True,
            classe__turma__membros__igreja__in=igrejas,
        )
    ).distinct()
