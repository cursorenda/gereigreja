"""Indicadores analíticos da Escola Bíblica para painéis e gráficos."""

from collections import defaultdict
from datetime import date, timedelta

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth

from .models import Frequencia


def _filtrar_periodo(queryset, periodo, ano_letivo):
    if periodo:
        return queryset.filter(data__gte=periodo.data_inicio, data__lte=periodo.data_fim)
    if ano_letivo:
        return queryset.filter(data__year=ano_letivo.ano)
    return queryset


def construir_dados_dashboard_graficos(*, classes, alunos_escopo, ofertas_escopo, departamentos, periodo, ano_letivo):
    classes = list(classes)
    alunos_por_departamento = {nome: 0 for nome in departamentos.values()}
    ofertas_por_departamento = {nome: 0 for nome in departamentos.values()}

    for chave, nome in departamentos.items():
        alunos = alunos_escopo.filter(turma__classe__departamento=chave)
        if ano_letivo:
            alunos = alunos.filter(turma__ano_letivo=ano_letivo)
        alunos_por_departamento[nome] = alunos.count()

        ofertas = ofertas_escopo.filter(
            Q(turma__classe__departamento=chave)
            | Q(turma__isnull=True, classe__departamento=chave)
        )
        ofertas_por_departamento[nome] = _filtrar_periodo(ofertas, periodo, ano_letivo).aggregate(
            total=Sum('valor'),
        )['total'] or 0

    alunos_por_classe = {}
    ofertas_por_classe = {}
    for classe in classes:
        alunos = alunos_escopo.filter(turma__classe=classe)
        if ano_letivo:
            alunos = alunos.filter(turma__ano_letivo=ano_letivo)
        alunos_por_classe[classe.nome] = alunos.count()

        ofertas = ofertas_escopo.filter(
            Q(turma__classe=classe) | Q(turma__isnull=True, classe=classe),
        )
        ofertas_por_classe[classe.nome] = _filtrar_periodo(ofertas, periodo, ano_letivo).aggregate(
            total=Sum('valor'),
        )['total'] or 0

    return {
        'alunos_por_departamento': alunos_por_departamento,
        'ofertas_por_departamento': ofertas_por_departamento,
        'ofertas_por_classe': ofertas_por_classe,
        'alunos_por_classe': alunos_por_classe,
    }


def construir_meses_evolucao(*, periodo, ano_letivo, hoje):
    if periodo:
        mes_atual = periodo.data_inicio.replace(day=1)
        limite = periodo.data_fim.replace(day=1)
        meses = []
        while mes_atual <= limite:
            meses.append(mes_atual)
            mes_atual = (mes_atual + timedelta(days=32)).replace(day=1)
        return meses
    if ano_letivo:
        return [date(ano_letivo.ano, mes, 1) for mes in range(1, 13)]
    return [(hoje.replace(day=1) - timedelta(days=30 * indice)).replace(day=1) for indice in range(11, -1, -1)]


def construir_alunos_evolucao(*, cadastros, transferencias, meses, ano_letivo):
    matriculas_por_cadastro = defaultdict(list)
    for cadastro in cadastros:
        matriculas_por_cadastro[cadastro.id].extend(cadastro.matriculas.all())

    transferencias_por_cadastro = defaultdict(list)
    for transferencia in transferencias:
        transferencias_por_cadastro[transferencia.aluno.cadastro_id].append(transferencia)

    def matricula_referencia(cadastro_id, data_referencia):
        matriculas = matriculas_por_cadastro.get(cadastro_id, [])
        if not matriculas:
            return None

        matriculas_por_turma = defaultdict(list)
        for matricula in matriculas:
            matriculas_por_turma[matricula.turma_id].append(matricula)
        for candidatas in matriculas_por_turma.values():
            candidatas.sort(key=lambda item: (item.ativo, item.updated_at, item.id), reverse=True)

        transferencia_passada = None
        transferencia_futura = None
        for transferencia in transferencias_por_cadastro.get(cadastro_id, []):
            if transferencia.data_transferencia and transferencia.data_transferencia <= data_referencia:
                transferencia_passada = transferencia
            elif transferencia_futura is None:
                transferencia_futura = transferencia
                break
        if transferencia_passada:
            candidatas = matriculas_por_turma.get(transferencia_passada.turma_destino_id)
            if candidatas:
                return candidatas[0]
        if transferencia_futura:
            candidatas = matriculas_por_turma.get(transferencia_futura.turma_origem_id)
            if candidatas:
                return candidatas[0]

        matriculas_ordenadas = sorted(matriculas, key=lambda item: (item.ativo, item.updated_at, item.id), reverse=True)
        return next((matricula for matricula in matriculas_ordenadas if matricula.ativo), matriculas_ordenadas[0])

    alunos_evolucao = defaultdict(lambda: [0] * len(meses))
    for indice, mes in enumerate(meses):
        referencia = (mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        for cadastro in cadastros:
            matricula = matricula_referencia(cadastro.id, referencia)
            if not matricula or not matricula.turma_id or not matricula.turma.classe_id:
                continue
            if ano_letivo and matricula.turma.ano_letivo_id != ano_letivo.id:
                continue
            alunos_evolucao[matricula.turma.classe.nome][indice] += 1
    return dict(alunos_evolucao)


def calcular_media_frequencia_alunos(*, aluno_ids, data_inicio, data_fim):
    if not aluno_ids:
        return 0
    resumo = Frequencia.objects.filter(
        aluno_id__in=aluno_ids,
        data__gte=data_inicio,
        data__lte=data_fim,
    ).values('aluno_id').annotate(
        total=Count('id'),
        presencas=Count('id', filter=Q(presente=True)),
    )
    soma_percentuais = 0
    qtd_alunos = 0
    for item in resumo:
        total = item['total'] or 0
        if total:
            soma_percentuais += item['presencas'] / total
            qtd_alunos += 1
    return round((soma_percentuais / qtd_alunos) * 100, 1) if qtd_alunos else 0


def calcular_percentual_engajamento_alunos(*, aluno_ids, data_inicio, data_fim, minimo_presenca=0.75):
    if not aluno_ids:
        return 0
    resumo = Frequencia.objects.filter(
        aluno_id__in=aluno_ids,
        data__gte=data_inicio,
        data__lte=data_fim,
    ).values('aluno_id').annotate(
        total=Count('id'),
        presencas=Count('id', filter=Q(presente=True)),
    )
    engajados = sum(
        1
        for item in resumo
        if item['total'] and (item['presencas'] / item['total']) >= minimo_presenca
    )
    return round((engajados / len(aluno_ids)) * 100, 1)


def construir_ofertas_evolucao(*, classes, ofertas_escopo, meses):
    classes = list(classes)
    if not classes or not meses:
        return {}
    proximo_mes = (meses[-1] + timedelta(days=32)).replace(day=1)
    totais = ofertas_escopo.filter(
        classe__in=classes,
        data__gte=meses[0],
        data__lt=proximo_mes,
    ).annotate(
        mes=TruncMonth('data'),
    ).values('classe_id', 'mes').annotate(total=Sum('valor'))
    total_por_classe_mes = {
        (item['classe_id'], item['mes']): float(item['total'] or 0)
        for item in totais
    }
    return {
        classe.nome: [total_por_classe_mes.get((classe.id, mes), 0) for mes in meses]
        for classe in classes
    }


def calcular_distribuicao_faixa_etaria(*, alunos, hoje):
    faixas = [
        ('0-5', 0, 5),
        ('6-12', 6, 12),
        ('13-17', 13, 17),
        ('18-29', 18, 29),
        ('30-59', 30, 59),
        ('60+', 60, 200),
    ]
    contagens = [0] * len(faixas)
    for aluno in alunos:
        nascimento = getattr(aluno, 'data_nascimento', None)
        if not nascimento:
            continue
        idade = (hoje - nascimento).days // 365
        for indice, (_label, min_idade, max_idade) in enumerate(faixas):
            if min_idade <= idade <= max_idade:
                contagens[indice] += 1
                break
    return [faixa[0] for faixa in faixas], contagens


def construir_ranking_classes(resumo_classes):
    ranking = []
    for item in resumo_classes:
        total = int(item.get('total') or 0)
        presentes = int(item.get('presentes') or 0)
        ranking.append({
            'classe': item['aluno__turma__classe__nome'],
            'frequencia_media': round((presentes / total) * 100, 1) if total else 0,
        })
    return sorted(ranking, key=lambda item: item['frequencia_media'], reverse=True)


def construir_ranking_alunos_pontos(*, pontos_por_cadastro, referencias_por_cadastro):
    ranking = []
    for item in pontos_por_cadastro:
        cadastro_id = item['aluno__cadastro_id']
        if not cadastro_id:
            continue
        aluno = referencias_por_cadastro.get(cadastro_id)
        if aluno is None:
            continue
        ranking.append({
            'nome': aluno.cadastro.nome,
            'turma': aluno.turma.nome if aluno.turma_id else '-',
            'classe': aluno.turma.classe.nome if aluno.turma_id and aluno.turma.classe_id else '-',
            'total_pontos': int(item.get('total_pontos') or 0),
            'presencas': int(item.get('presencas') or 0),
        })
    ranking.sort(key=lambda item: (-item['total_pontos'], -item['presencas'], item['nome'].casefold()))
    for posicao, item in enumerate(ranking, start=1):
        item['posicao'] = posicao
    return ranking


def construir_ranking_ofertas(*, classes, ofertas_escopo, ano):
    """Consolida em uma consulta as ofertas anuais de cada classe do escopo."""
    classes = list(classes)
    totais_por_classe = {
        item['classe_id']: float(item['total'] or 0)
        for item in ofertas_escopo.filter(
            classe__in=classes,
            data__year=ano,
        ).values('classe_id').annotate(total=Sum('valor'))
    }
    ranking = [
        {'classe': classe.nome, 'total_oferta': totais_por_classe.get(classe.id, 0)}
        for classe in classes
    ]
    return sorted(ranking, key=lambda item: item['total_oferta'], reverse=True)


def coletar_movimentacao_alunos(
    *, alunos_escopo, transferencias_escopo, inicio_atual, fim_atual, inicio_anterior, fim_anterior,
):
    """Apura admissões e transferências a partir de querysets já autorizadas."""
    alunos_base = alunos_escopo.filter(
        turma__isnull=False,
        ativo=True,
        turma__ano_letivo__ativo=True,
    )
    return {
        'alunos_novos': alunos_base.filter(
            created_at__date__gte=inicio_atual,
            created_at__date__lte=fim_atual,
        ).count(),
        'alunos_novos_anterior': alunos_base.filter(
            created_at__date__gte=inicio_anterior,
            created_at__date__lte=fim_anterior,
        ).count(),
        'transferidos': transferencias_escopo.filter(
            data_transferencia__gte=inicio_atual,
            data_transferencia__lte=fim_atual,
        ).distinct().count(),
    }


def calcular_totais_ofertas_periodos(*, ofertas_escopo, inicio_atual, fim_atual, inicio_anterior, fim_anterior):
    """Calcula os totais de ofertas de dois períodos em uma queryset autorizada."""
    def total(inicio, fim):
        return float(ofertas_escopo.filter(
            data__gte=inicio,
            data__lte=fim,
        ).aggregate(total=Sum('valor'))['total'] or 0)

    return {
        'atual': total(inicio_atual, fim_atual),
        'anterior': total(inicio_anterior, fim_anterior),
    }
