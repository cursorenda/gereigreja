"""Agregações usadas nos relatórios operacionais da Escola Bíblica."""

from decimal import Decimal

from django.db.models import Count, Q, Sum

from .models import Frequencia, OfertaClasse


def ofertas_da_turma_na_data(turma, data):
    return OfertaClasse.objects.filter(
        Q(turma=turma) | Q(turma__isnull=True, classe=turma.classe),
        data=data,
    )


def _novo_total():
    return {
        'matriculados': 0,
        'presentes': 0,
        'ausentes': 0,
        'visitantes': 0,
        'biblias': 0,
        'revistas': 0,
        'oferta': Decimal('0.0'),
    }


def _consolidar_turma(turma, data):
    alunos = turma.alunos.filter(ativo=True)
    matriculados = alunos.count()
    frequencias = Frequencia.objects.filter(aluno__in=alunos, data=data)
    presentes = frequencias.filter(presente=True).count()
    return {
        'nome': turma.nome,
        'matriculados': matriculados,
        'presentes': presentes,
        'ausentes': matriculados - presentes,
        'visitantes': frequencias.filter(trouxe_visitante=True).count(),
        'biblias': frequencias.filter(trouxe_biblia=True).count(),
        'revistas': frequencias.filter(trouxe_revista=True).count(),
        'oferta': ofertas_da_turma_na_data(turma, data).aggregate(s=Sum('valor'))['s'] or Decimal('0.0'),
    }


def _somar_total(total, dados_turma):
    for campo in total:
        total[campo] += dados_turma[campo]


def construir_resumo_relatorio_diario(*, turmas, turmas_escopo, licoes_escopo, ano_letivo, data, datas_com_licoes):
    relatorio_turmas = [_consolidar_turma(turma, data) for turma in turmas]
    total_geral = _novo_total()
    for dados_turma in relatorio_turmas:
        _somar_total(total_geral, dados_turma)

    data_anterior = None
    datas_lista = list(datas_com_licoes)
    try:
        indice_atual = datas_lista.index(data)
        if indice_atual + 1 < len(datas_lista):
            data_anterior = datas_lista[indice_atual + 1]
    except ValueError:
        pass

    total_anterior = None
    if data_anterior and ano_letivo:
        turmas_anterior = licoes_escopo.filter(data=data_anterior).values_list('turma_id', flat=True)
        total_anterior = _novo_total()
        for turma in turmas_escopo.filter(ano_letivo=ano_letivo, id__in=turmas_anterior):
            _somar_total(total_anterior, _consolidar_turma(turma, data_anterior))

    return {
        'relatorio_turmas': relatorio_turmas,
        'total_geral': total_geral,
        'total_anterior': total_anterior,
        'data_anterior': data_anterior,
    }


def coletar_dados_relatorio_instantaneo(*, turmas, data):
    """Consolida chamadas e ofertas do dia para turmas já autorizadas."""
    turmas = list(turmas)
    turma_ids = [turma.id for turma in turmas]
    classe_ids = list({turma.classe_id for turma in turmas if turma.classe_id})
    frequencias_por_turma = {
        item['aluno__turma_id']: item
        for item in Frequencia.objects.filter(
            aluno__turma_id__in=turma_ids,
            data=data,
        ).values('aluno__turma_id').annotate(
            chamadas=Count('id'),
            presentes=Count('id', filter=Q(presente=True)),
            biblias=Count('id', filter=Q(trouxe_biblia=True)),
            ofertas_individuais=Count('id', filter=Q(trouxe_oferta=True)),
        )
    }
    ofertas_por_turma = {
        item['turma_id']: item['total'] or 0
        for item in OfertaClasse.objects.filter(
            turma_id__in=turma_ids,
            data=data,
        ).values('turma_id').annotate(total=Sum('valor'))
    }
    ofertas_por_classe = {
        item['classe_id']: item['total'] or 0
        for item in OfertaClasse.objects.filter(
            turma__isnull=True,
            classe_id__in=classe_ids,
            data=data,
        ).values('classe_id').annotate(total=Sum('valor'))
    }
    return {
        'turmas': turmas,
        'frequencias_por_turma': frequencias_por_turma,
        'ofertas_por_turma': ofertas_por_turma,
        'ofertas_por_classe': ofertas_por_classe,
    }
