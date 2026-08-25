"""Consultas consolidadas reutilizáveis da Escola Bíblica."""

from collections import defaultdict

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg, Case, Count, IntegerField, OuterRef, Q, Subquery, Value, When
from django.utils import timezone
from django.utils.dateparse import parse_date

from secretaria.models import Membro, MembroCargo

from .models import Avaliacao, Classe, Frequencia, Licao, PeriodoEBD


def construir_expr_pontos_frequencia(pontos_cfg):
    return (
        Case(When(presente=True, then=Value(pontos_cfg['presente'])), default=Value(0), output_field=IntegerField())
        + Case(When(trouxe_biblia=True, then=Value(pontos_cfg['biblia'])), default=Value(0), output_field=IntegerField())
        + Case(When(trouxe_revista=True, then=Value(pontos_cfg['revista'])), default=Value(0), output_field=IntegerField())
        + Case(When(trouxe_oferta=True, then=Value(pontos_cfg['oferta'])), default=Value(0), output_field=IntegerField())
        + Case(When(trouxe_visitante=True, then=Value(pontos_cfg['visitante'])), default=Value(0), output_field=IntegerField())
    )


def paginar_queryset(*, queryset, pagina, por_pagina):
    """Paginação com os mesmos fallbacks usados pelas listagens da EBD."""
    paginator = Paginator(queryset, por_pagina)
    try:
        return paginator.page(pagina)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def filtrar_e_paginar_aulas_geradas(*, aulas, data='', tema='', pagina=None, por_pagina=30):
    """Aplica os filtros da listagem de aulas já restrita à turma autorizada."""
    data_aula = parse_date(data or '')
    if data_aula:
        aulas = aulas.filter(data=data_aula)
    if tema:
        aulas = aulas.filter(tema__icontains=tema)
    return paginar_queryset(queryset=aulas.order_by('-data'), pagina=pagina, por_pagina=por_pagina)


def construir_filtros_listagem_turmas(
    *, turmas_base, periodo=None, turma_filtro='', nome_filtro='', classe_filtro='',
):
    """Aplica filtros de turma e monta as opções auxiliares já no escopo autorizado."""
    try:
        turma_filtro_id = int(turma_filtro) if turma_filtro else None
    except ValueError:
        turma_filtro_id = None
    try:
        classe_filtro_id = int(classe_filtro) if classe_filtro else None
    except ValueError:
        classe_filtro_id = None

    turmas_disponiveis = turmas_base
    if classe_filtro_id:
        turmas_disponiveis = turmas_disponiveis.filter(classe_id=classe_filtro_id)
    turmas_disponiveis = turmas_disponiveis.order_by('nome')

    classes_disponiveis = Classe.objects.filter(
        id__in=turmas_base.values_list('classe_id', flat=True),
    )
    if turma_filtro_id:
        classes_disponiveis = classes_disponiveis.filter(
            id__in=turmas_base.filter(id=turma_filtro_id).values_list('classe_id', flat=True),
        )
    classes_disponiveis = classes_disponiveis.distinct().order_by('nome')

    turmas_list = turmas_base
    if turma_filtro_id:
        turmas_list = turmas_list.filter(id=turma_filtro_id)
    elif turma_filtro:
        turmas_list = turmas_list.filter(nome__icontains=turma_filtro)
    elif nome_filtro:
        turmas_list = turmas_list.filter(nome__icontains=nome_filtro)

    if classe_filtro_id:
        turmas_list = turmas_list.filter(classe_id=classe_filtro_id)
    elif classe_filtro:
        turmas_list = turmas_list.filter(classe__nome__icontains=classe_filtro)

    if periodo:
        turmas_list = turmas_list.filter(
            licao__data__gte=periodo.data_inicio,
            licao__data__lte=periodo.data_fim,
        )
    turmas_list = turmas_list.distinct().order_by('nome')
    return {
        'turmas_disponiveis': turmas_disponiveis,
        'classes_disponiveis': classes_disponiveis,
        'turmas_list': turmas_list,
    }


def construir_contexto_template_listagem_turmas(
    *, turmas, turmas_total, contexto_periodos, filtros_listagem,
    turma_filtro, classe_filtro, tipo_periodo, now, request, status_periodo, ebd_periodo_atual,
    ebd_config_source_info, querystring,
):
    """Monta o contrato do template da listagem de turmas."""
    return {
        'turmas': turmas,
        'turmas_total': turmas_total,
        'anos_letivos': contexto_periodos['anos_letivos'],
        'ano_letivo_selecionado': contexto_periodos['ano_letivo_selecionado'],
        'turmas_disponiveis': filtros_listagem['turmas_disponiveis'],
        'classes_disponiveis': filtros_listagem['classes_disponiveis'],
        'turma_filtro': turma_filtro,
        'classe_filtro': classe_filtro,
        'periodos': contexto_periodos['periodos'],
        'periodo_selecionado': contexto_periodos['periodo_selecionado'],
        'periodo_filtro_chip': contexto_periodos['periodo_filtro_chip'],
        'tipo_periodo': tipo_periodo,
        'now': now,
        'request': request,
        'mostrar_banner_abrir_periodo': contexto_periodos['mostrar_banner_abrir_periodo'],
        'sugerir_copiar': contexto_periodos['sugerir_copiar'],
        'ebd_periodo_atual': ebd_periodo_atual,
        **status_periodo,
        'ebd_config_source': ebd_config_source_info['ebd_config_source'],
        'ebd_config_source_label': ebd_config_source_info['ebd_config_source_label'],
        'ebd_config_source_hint': ebd_config_source_info['ebd_config_source_hint'],
        'querystring': querystring,
    }


def colapsar_alunos_por_cadastro(queryset):
    ultimo_aluno_por_cadastro = queryset.filter(cadastro_id=OuterRef('cadastro_id')).order_by(
        '-ativo', '-turma__ano_letivo__ano', '-updated_at', '-id'
    ).values('id')[:1]
    return queryset.filter(id=Subquery(ultimo_aluno_por_cadastro))


def consolidar_alunos_por_cadastro_periodo(
    queryset, inicio=None, fim=None, turma_id=None, classe_id=None, periodo=None,
):
    if periodo is not None:
        inicio, fim = periodo.data_inicio, periodo.data_fim
    data_referencia = fim or inicio or timezone.now().date()
    matriculas = list(queryset.select_related('cadastro', 'turma', 'turma__classe', 'turma__ano_letivo'))
    if not matriculas:
        return []

    matriculas_por_cadastro = defaultdict(list)
    for matricula in matriculas:
        matriculas_por_cadastro[matricula.cadastro_id].append(matricula)
    alunos_referencia = []
    for matriculas_cadastro in matriculas_por_cadastro.values():
        cadastro = matriculas_cadastro[0].cadastro
        matricula_referencia = cadastro.get_matricula_referencia(
            data_referencia=data_referencia, matriculas=matriculas_cadastro,
        )
        if matricula_referencia is None:
            continue
        if turma_id and str(matricula_referencia.turma_id) != str(turma_id):
            continue
        if classe_id and str(matricula_referencia.turma.classe_id) != str(classe_id):
            continue
        alunos_referencia.append(matricula_referencia)
    if not alunos_referencia:
        return []

    cadastro_ids = [aluno.cadastro_id for aluno in alunos_referencia]
    frequencias = Frequencia.objects.filter(aluno__cadastro_id__in=cadastro_ids)
    if inicio:
        frequencias = frequencias.filter(data__gte=inicio)
    if fim:
        frequencias = frequencias.filter(data__lte=fim)
    frequencias_por_cadastro = {
        item['aluno__cadastro_id']: item
        for item in frequencias.values('aluno__cadastro_id').annotate(
            total_freq=Count('id'), presencas=Count('id', filter=Q(presente=True)),
        )
    }

    avaliacoes = Avaliacao.objects.filter(aluno__cadastro_id__in=cadastro_ids)
    if periodo is not None:
        avaliacoes = avaliacoes.filter(licao__periodo=periodo)
    else:
        if inicio:
            avaliacoes = avaliacoes.filter(licao__data__gte=inicio)
        if fim:
            avaliacoes = avaliacoes.filter(licao__data__lte=fim)
    avaliacoes_por_cadastro = {
        item['aluno__cadastro_id']: item
        for item in avaliacoes.values('aluno__cadastro_id').annotate(
            media_nota=Avg('nota'), participacao=Count('id', filter=Q(participacao=True)),
        )
    }
    for aluno in alunos_referencia:
        aluno.nome_exibicao = aluno.cadastro.nome
        freq_info = frequencias_por_cadastro.get(aluno.cadastro_id, {})
        total_freq, presencas = freq_info.get('total_freq', 0), freq_info.get('presencas', 0)
        aluno.total_freq, aluno.presencas = total_freq, presencas
        aluno.freq_percent = round((presencas / total_freq) * 100, 1) if total_freq else None
        aval_info = avaliacoes_por_cadastro.get(aluno.cadastro_id, {})
        media_nota = aval_info.get('media_nota')
        aluno.media_nota = round(media_nota, 2) if media_nota is not None else None
        aluno.participacao = aval_info.get('participacao', 0)
    return sorted(alunos_referencia, key=lambda item: (item.nome_exibicao.lower(), item.turma.nome.lower()))


def preparar_alunos_para_relatorio(*, queryset, parametros, periodo):
    return consolidar_alunos_por_cadastro_periodo(
        queryset,
        inicio=parse_date(parametros.get('inicio') or ''),
        fim=parse_date(parametros.get('fim') or ''),
        turma_id=parametros.get('turma'),
        classe_id=parametros.get('classe'),
        periodo=periodo,
    )


def construir_contexto_relatorio_alunos(*, turmas, classes, alunos_escopo, parametros, periodo_ctx):
    """Prepara o contexto comum dos relatórios de frequência e de alunos."""
    alunos = preparar_alunos_para_relatorio(
        queryset=alunos_escopo,
        parametros=parametros,
        periodo=periodo_ctx['periodo_selecionado'],
    )
    return {
        'turmas': turmas,
        'classes': classes,
        'alunos': alunos,
        **periodo_ctx,
    }


def preparar_listagem_alunos(
    *, alunos_escopo, ano, historico, nome='', turma_id='', ativo='', vinculo='', consolidar=True,
):
    """Aplica filtros de listagem sobre uma queryset de alunos já autorizada."""
    alunos = alunos_escopo
    if not historico:
        alunos = alunos.filter(turma__ano_letivo__ano=ano)
    if nome:
        alunos = alunos.filter(nome__icontains=nome)
    if turma_id:
        alunos = alunos.filter(turma_id=turma_id)
    if ativo in ('True', 'False'):
        alunos = alunos.filter(ativo=(ativo == 'True'))
    if vinculo == 'vinculado':
        alunos = alunos.filter(cadastro__pessoa__isnull=False)
    elif vinculo == 'sem_vinculo':
        alunos = alunos.filter(cadastro__pessoa__isnull=True)
    if not historico and consolidar:
        alunos = colapsar_alunos_por_cadastro(alunos)
    return alunos.select_related(
        'cadastro', 'cadastro__pessoa', 'turma', 'turma__ano_letivo',
    ).order_by('nome', '-turma__ano_letivo__ano')


def construir_contexto_listagem_alunos(
    *, alunos_escopo, turmas_escopo, anos_letivos, parametros, ano_atual,
):
    """Monta filtros, resultados e parametros auxiliares da listagem de alunos."""
    nome_filtro = parametros.get('nome', '').strip()
    turma_filtro = parametros.get('turma', '').strip()
    ativo_filtro = parametros.get('ativo', '').strip()
    vinculo_filtro = parametros.get('vinculo', '').strip()
    historico = parametros.get('historico') == '1'
    ano_filtro_raw = parametros.get('ano', '').strip()
    try:
        ano_filtro = int(ano_filtro_raw) if ano_filtro_raw else ano_atual
    except ValueError:
        ano_filtro = ano_atual

    alunos = preparar_listagem_alunos(
        alunos_escopo=alunos_escopo,
        ano=ano_filtro,
        historico=historico,
        nome=nome_filtro,
        turma_id=turma_filtro,
        ativo=ativo_filtro,
        vinculo=vinculo_filtro,
        consolidar=False,
    )
    if not historico:
        alunos = colapsar_alunos_por_cadastro(alunos)
        turmas_escopo = turmas_escopo.filter(ano_letivo__ano=ano_filtro)

    query_params = parametros.copy()
    query_params.pop('page', None)
    query_params_sem_vinculo = query_params.copy()
    query_params_sem_vinculo.pop('vinculo', None)

    return {
        'alunos': alunos,
        'turmas': turmas_escopo,
        'anos_letivos': anos_letivos,
        'ano_filtro': ano_filtro,
        'historico': historico,
        'vinculo_filtro': vinculo_filtro,
        'querystring': query_params.urlencode(),
        'querystring_sem_vinculo': query_params_sem_vinculo.urlencode(),
    }


def construir_contexto_template_listagem_alunos(
    *, contexto_listagem, alunos_paginados, total_alunos, usuario_pode_vincular,
):
    """Completa o contexto do template sem alterar o recorte autorizado."""
    return {
        **contexto_listagem,
        'alunos': alunos_paginados,
        'total_alunos': total_alunos,
        'usuario_pode_vincular': usuario_pode_vincular,
    }


def construir_listagem_licoes(*, turmas_escopo, igrejas_escopo, parametros, hoje):
    """Monta a listagem de lições a partir de turmas e igrejas já autorizadas."""
    licoes_escopo = Licao.objects.filter(turma__in=turmas_escopo).distinct()
    anos_com_licoes = licoes_escopo.values_list('data__year', flat=True).distinct()
    periodos = PeriodoEBD.objects.select_related('ano_letivo').filter(
        data_inicio__year__in=anos_com_licoes,
    ).order_by('-ano_letivo__ano', '-numero')

    periodo_atual = periodos.filter(data_inicio__lte=hoje, data_fim__gte=hoje).first()
    periodo_id = parametros.get('periodo')
    periodo_selecionado = periodos.filter(id=periodo_id).first() if periodo_id else periodo_atual

    licoes = licoes_escopo
    if periodo_selecionado:
        licoes = licoes.filter(periodo=periodo_selecionado)

    turma_nomes = turmas_escopo.values_list('nome', flat=True).distinct().order_by('nome')
    turma_nome = parametros.get('turma')
    if turma_nome:
        licoes = licoes.filter(turma__nome=turma_nome)

    membros_professor_ids = MembroCargo.objects.filter(
        cargo__is_ebd=True,
        cargo__nome__icontains='professor',
        data_fim__isnull=True,
        membro__igreja__in=igrejas_escopo,
    ).values_list('membro_id', flat=True)
    professores = Membro.objects.filter(
        chave__in=membros_professor_ids,
        igreja__in=igrejas_escopo,
    ).order_by('nome')
    professor_id = parametros.get('professor')
    if professor_id:
        licoes = licoes.filter(professor_id=professor_id)

    return {
        'licoes': licoes,
        'periodos': periodos,
        'periodo_selecionado': periodo_selecionado,
        'turma_nomes': turma_nomes,
        'turma_nome': turma_nome,
        'professores': professores,
        'professor_id': professor_id,
    }


def construir_historico_anual_aluno(*, matriculas, transferencias, frequencias, avaliacoes):
    por_ano = {}

    def obter_ano(ano):
        return por_ano.setdefault(
            ano,
            {
                'ano': ano,
                'matriculas': [],
                'transferencias': [],
                'total_frequencias': 0,
                'presencas': 0,
                'percentual_frequencia': None,
                'total_avaliacoes': 0,
                'media_notas': None,
                'participacoes': 0,
            },
        )

    for matricula in matriculas:
        ano = getattr(getattr(matricula.turma, 'ano_letivo', None), 'ano', None) or 'Sem ano'
        obter_ano(ano)['matriculas'].append(matricula)

    for transferencia in transferencias:
        ano = transferencia.data_transferencia.year if transferencia.data_transferencia else 'Sem ano'
        obter_ano(ano)['transferencias'].append(transferencia)

    notas_por_ano = defaultdict(list)
    for frequencia in frequencias:
        ano = frequencia.data.year if frequencia.data else 'Sem ano'
        resumo = obter_ano(ano)
        resumo['total_frequencias'] += 1
        if frequencia.presente:
            resumo['presencas'] += 1

    for avaliacao in avaliacoes:
        data_licao = getattr(avaliacao.licao, 'data', None)
        ano = data_licao.year if data_licao else 'Sem ano'
        resumo = obter_ano(ano)
        resumo['total_avaliacoes'] += 1
        if avaliacao.participacao:
            resumo['participacoes'] += 1
        if avaliacao.nota is not None:
            notas_por_ano[ano].append(float(avaliacao.nota))

    for ano, resumo in por_ano.items():
        if resumo['total_frequencias']:
            resumo['percentual_frequencia'] = round(
                (resumo['presencas'] / resumo['total_frequencias']) * 100,
                1,
            )
        if notas_por_ano.get(ano):
            notas = notas_por_ano[ano]
            resumo['media_notas'] = round(sum(notas) / len(notas), 2)

    return sorted(
        por_ano.values(),
        key=lambda item: item['ano'] if isinstance(item['ano'], int) else -1,
        reverse=True,
    )
