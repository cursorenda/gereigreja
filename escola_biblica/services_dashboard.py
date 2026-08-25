"""Regras puras de apresentação do painel da Escola Bíblica."""


from datetime import timedelta

from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce
from django.urls import reverse

from configuracao.models import ConfiguracaoSistema
from configuracao.utils import pode_editar_configuracao_org
from secretaria.models import MembroCargo

from .models import Classe, Frequencia, OfertaClasse, PeriodoEBD, TransferenciaAluno
from .services_analiticos import (
    calcular_distribuicao_faixa_etaria,
    calcular_media_frequencia_alunos,
    calcular_percentual_engajamento_alunos,
    construir_ranking_classes,
    construir_ranking_alunos_pontos,
    construir_ranking_ofertas,
    calcular_totais_ofertas_periodos,
    coletar_movimentacao_alunos,
)
from .services_consultas import construir_expr_pontos_frequencia
from .services_permissoes import usuario_pode_gerenciar_ebd
from .services_relatorios import coletar_dados_relatorio_instantaneo
from .utils import build_resumo_semanal_ebd, formatar_resumo_semanal_ebd, get_faixa_semana_anterior


def construir_chave_cache_dashboard(
    *, versao, usuario_id, igreja_id, tipo_periodo, ano_letivo, periodo, data_relatorio,
):
    """Monta a chave do cache incluindo todo recorte que altera o painel."""
    return (
        f"ebd:dashboard:v{versao}:u{usuario_id}:ig{igreja_id or 'all'}"
        f":tp:{tipo_periodo}:a:{ano_letivo}:p:{periodo}:r:{data_relatorio}:summary_scope_v2"
    )


def preparar_contexto_periodo_dashboard(*, periodo_ctx, periodo_tipo_label, hoje):
    """Consolida o recorte temporal e os rotulos exibidos no dashboard."""
    tipo_periodo = periodo_ctx['tipo_periodo']
    periodo_selecionado = periodo_ctx['periodo_selecionado']
    recortes = calcular_recortes_comparativos_dashboard(
        periodo_selecionado=periodo_selecionado,
        tipo_periodo=tipo_periodo,
        hoje=hoje,
    )
    return {
        'tipo_periodo': tipo_periodo,
        'periodo_tipo_label': periodo_tipo_label,
        'anos_letivos': periodo_ctx['anos_letivos'],
        'ano_letivo_selecionado': periodo_ctx['ano_letivo_selecionado'],
        'periodos_disponiveis': periodo_ctx['periodos_disponiveis'],
        'periodo_selecionado': periodo_selecionado,
        'inicio_atual': recortes['inicio_atual'],
        'fim_atual': recortes['fim_atual'],
        'inicio_anterior': recortes['inicio_anterior'],
        'fim_anterior': recortes['fim_anterior'],
        'periodo_anterior_label': (
            f"{recortes['inicio_anterior'].strftime('%d/%m/%Y')} "
            f"a {recortes['fim_anterior'].strftime('%d/%m/%Y')}"
        ),
        'periodo_selecionado_label': (
            f"{recortes['inicio_atual'].strftime('%d/%m/%Y')} "
            f"a {recortes['fim_atual'].strftime('%d/%m/%Y')}"
        ),
    }


def preparar_contexto_relatorio_instantaneo(
    *, turmas, ano_letivo, data_relatorio, hoje, licoes,
):
    """Define a data e as turmas autorizadas do relatorio diario do painel."""
    if data_relatorio:
        from django.utils.dateparse import parse_date

        data = parse_date(data_relatorio) or hoje
    else:
        ultima_licao = licoes.order_by('-data').first()
        data = ultima_licao.data if ultima_licao else hoje

    turmas_relatorio = turmas
    if ano_letivo:
        turmas_relatorio = turmas_relatorio.filter(ano_letivo=ano_letivo)
    turmas_relatorio = turmas_relatorio.select_related('classe').annotate(
        matriculados_ativos=Count('alunos', filter=Q(alunos__ativo=True), distinct=True),
    ).order_by('nome')
    return {'data': data, 'turmas': turmas_relatorio}


def resumir_status_relatorio_instantaneo(relatorio_instantaneo_turmas):
    """Conta os estados apresentados no relatorio instantaneo do painel."""
    return {
        'pendentes': sum(1 for item in relatorio_instantaneo_turmas if item['status_tone'] == 'is-pending'),
        'parciais': sum(1 for item in relatorio_instantaneo_turmas if item['status_tone'] == 'is-partial'),
        'completas': sum(1 for item in relatorio_instantaneo_turmas if item['status_tone'] == 'is-complete'),
    }


def calcular_recortes_comparativos_dashboard(*, periodo_selecionado, tipo_periodo, hoje):
    """Retorna os intervalos atual e anterior usados pelos indicadores do painel."""
    if periodo_selecionado:
        inicio_atual = periodo_selecionado.data_inicio
        fim_atual = periodo_selecionado.data_fim
    else:
        inicio_atual = hoje.replace(day=1)
        fim_atual = hoje

    periodo_anterior = PeriodoEBD.objects.filter(
        tipo=tipo_periodo,
        data_fim__lt=inicio_atual,
    ).order_by('-data_fim').first()
    if periodo_anterior:
        inicio_anterior = periodo_anterior.data_inicio
        fim_anterior = periodo_anterior.data_fim
    else:
        dias_periodo = max((fim_atual - inicio_atual).days + 1, 1)
        fim_anterior = inicio_atual - timedelta(days=1)
        inicio_anterior = fim_anterior - timedelta(days=dias_periodo - 1)

    return {
        'inicio_atual': inicio_atual,
        'fim_atual': fim_atual,
        'inicio_anterior': inicio_anterior,
        'fim_anterior': fim_anterior,
    }


def coletar_indicadores_frequencia_dashboard(
    *, alunos, classes, inicio_atual, fim_atual, inicio_anterior, fim_anterior,
):
    """Calcula indicadores de frequencia apenas para alunos e classes ja autorizados."""
    alunos_ids = list(alunos.values_list('id', flat=True))
    frequencia_atual = calcular_media_frequencia_alunos(
        aluno_ids=alunos_ids,
        data_inicio=inicio_atual,
        data_fim=fim_atual,
    )
    frequencia_anterior = calcular_media_frequencia_alunos(
        aluno_ids=alunos_ids,
        data_inicio=inicio_anterior,
        data_fim=fim_anterior,
    )
    engajamento = calcular_percentual_engajamento_alunos(
        aluno_ids=alunos_ids,
        data_inicio=inicio_atual,
        data_fim=fim_atual,
    )
    resumo_classes = Frequencia.objects.filter(
        aluno_id__in=alunos_ids,
        aluno__turma__classe__in=classes,
        aluno__ativo=True,
        data__gte=inicio_atual,
        data__lte=fim_atual,
    ).values('aluno__turma__classe_id', 'aluno__turma__classe__nome').annotate(
        total=Count('id'),
        presentes=Count('id', filter=Q(presente=True)),
    )
    return {
        'frequencia_atual': frequencia_atual,
        'frequencia_anterior': frequencia_anterior,
        'engajamento': engajamento,
        'ranking_classes': construir_ranking_classes(resumo_classes),
    }


def coletar_evolucao_mensal_alunos_dashboard(*, alunos_escopo, hoje):
    """Monta a serie mensal de alunos ativos a partir de um escopo ja autorizado."""
    meses = [
        (hoje.replace(day=1) - timedelta(days=30 * indice)).replace(day=1)
        for indice in range(11, -1, -1)
    ]
    departamentos = [chave for chave, _nome in Classe.DEPARTAMENTO_CHOICES]
    totais = []
    for mes in meses:
        proximo_mes = (mes + timedelta(days=32)).replace(day=1)
        totais.append(alunos_escopo.filter(
            turma__isnull=False,
            ativo=True,
            turma__ano_letivo__ativo=True,
            turma__ano_letivo__ano__contains=str(mes.year),
            turma__classe__isnull=False,
            turma__classe__departamento__in=departamentos,
            data_nascimento__isnull=False,
            data_nascimento__lte=proximo_mes,
        ).count())
    return {'meses': meses, 'totais': totais}


def coletar_ranking_pontos_dashboard(
    *, turmas, alunos_escopo, ano_letivo, inicio, fim, pontos_config,
):
    """Consolida o ranking por cadastro a partir de turmas e alunos ja autorizados."""
    frequencias = Frequencia.objects.filter(
        aluno__turma__in=turmas,
        data__gte=inicio,
        data__lte=fim,
    )
    if ano_letivo:
        frequencias = frequencias.filter(aluno__turma__ano_letivo=ano_letivo)
    pontos_por_cadastro = list(
        frequencias.values('aluno__cadastro_id').annotate(
            total_pontos=Sum(
                Coalesce('pontos_total', construir_expr_pontos_frequencia(pontos_config)),
            ),
            presencas=Count('id', filter=Q(presente=True)),
        ),
    )
    cadastro_ids = [item['aluno__cadastro_id'] for item in pontos_por_cadastro if item['aluno__cadastro_id']]
    referencias = {}
    if cadastro_ids:
        alunos_referencia = alunos_escopo.filter(
            cadastro_id__in=cadastro_ids,
        ).select_related('cadastro', 'turma', 'turma__classe', 'turma__ano_letivo')
        if ano_letivo:
            alunos_referencia = alunos_referencia.filter(turma__ano_letivo=ano_letivo)
        for aluno in alunos_referencia.order_by('cadastro_id', '-ativo', '-updated_at', '-id'):
            referencias.setdefault(aluno.cadastro_id, aluno)
    return construir_ranking_alunos_pontos(
        pontos_por_cadastro=pontos_por_cadastro,
        referencias_por_cadastro=referencias,
    )


def coletar_indicadores_ofertas_dashboard(
    *, classes, ofertas_escopo, ano, inicio_atual, fim_atual, inicio_anterior, fim_anterior,
):
    """Consolida os indicadores de oferta para classes e ofertas ja autorizadas."""
    total_geral = ofertas_escopo.aggregate(total=Sum('valor'))['total'] or 0
    totais_periodo = calcular_totais_ofertas_periodos(
        ofertas_escopo=ofertas_escopo,
        inicio_atual=inicio_atual,
        fim_atual=fim_atual,
        inicio_anterior=inicio_anterior,
        fim_anterior=fim_anterior,
    )
    return {
        'total_geral': total_geral,
        'total_atual': totais_periodo['atual'],
        'total_anterior': totais_periodo['anterior'],
        'ranking_classes': construir_ranking_ofertas(
            classes=classes,
            ofertas_escopo=ofertas_escopo,
            ano=ano,
        ),
    }


def coletar_indicadores_movimentacao_dashboard(
    *, turmas, alunos_escopo, inicio_atual, fim_atual, inicio_anterior, fim_anterior,
):
    """Apura novas matriculas e transferencias para turmas ja autorizadas."""
    transferencias = TransferenciaAluno.objects.filter(
        Q(turma_origem__in=turmas) | Q(turma_destino__in=turmas),
    )
    return coletar_movimentacao_alunos(
        alunos_escopo=alunos_escopo,
        transferencias_escopo=transferencias,
        inicio_atual=inicio_atual,
        fim_atual=fim_atual,
        inicio_anterior=inicio_anterior,
        fim_anterior=fim_anterior,
    )


def construir_contexto_escopo_dashboard(*, igreja, igrejas_escopo, ano_letivo, ano_atual):
    """Monta os textos e a referencia anual usados no cabecalho operacional."""
    if igreja:
        scope_label = f'Igreja: {igreja.nome_igreja}'
    else:
        scope_label = f'Consolidado EBD ({igrejas_escopo.count()} igrejas)'
    ano_destino_preparo = (
        ano_letivo.ano + 1
        if ano_letivo is not None
        else ano_atual + 1
    )
    return {
        'scope_label': scope_label,
        'ano_destino_preparo': ano_destino_preparo,
    }


def preparar_resumo_semanal_dashboard(*, ministerio, hoje, igrejas_escopo, ano_letivo):
    """Monta o resumo semanal apenas quando ha ministerio no contexto da EBD."""
    if not ministerio:
        return {'resumo': None, 'formatado': ''}
    inicio, fim = get_faixa_semana_anterior(hoje)
    resumo = build_resumo_semanal_ebd(
        ministerio,
        inicio,
        fim,
        igrejas=igrejas_escopo,
        ano_letivo=ano_letivo,
    )
    return {
        'resumo': resumo,
        'formatado': formatar_resumo_semanal_ebd(resumo),
    }


def preparar_contexto_operacional_dashboard(
    *, igreja, igrejas_escopo, ano_letivo, ano_atual, ministerio, hoje,
    pode_gerenciar_ebd, alunos_novos, alunos_novos_anterior,
    frequencia_atual, frequencia_anterior, ofertas_atual, ofertas_anterior,
    evasao, turmas_previstas_semana, turmas_sem_chamada_semana,
    houve_janela_operacional, turmas_pendentes_relatorio,
    turmas_parciais_relatorio, relatorio_instantaneo_turmas,
):
    """Reune os elementos operacionais do dashboard sem depender da view."""
    contexto_escopo = construir_contexto_escopo_dashboard(
        igreja=igreja,
        igrejas_escopo=igrejas_escopo,
        ano_letivo=ano_letivo,
        ano_atual=ano_atual,
    )
    contexto_resumo = preparar_resumo_semanal_dashboard(
        ministerio=ministerio,
        hoje=hoje,
        igrejas_escopo=igrejas_escopo,
        ano_letivo=ano_letivo,
    )
    pode_publicar_resumo_semanal = bool(ministerio and pode_gerenciar_ebd)
    bloco_decisao = construir_bloco_decisao_dashboard(
        alunos_novos=alunos_novos,
        alunos_novos_anterior=alunos_novos_anterior,
        frequencia_atual=frequencia_atual,
        frequencia_anterior=frequencia_anterior,
        ofertas_atual=ofertas_atual,
        ofertas_anterior=ofertas_anterior,
        evasao=evasao,
        turmas_previstas_semana=turmas_previstas_semana,
        turmas_sem_chamada_semana=turmas_sem_chamada_semana,
        houve_janela_operacional=houve_janela_operacional,
        turmas_pendentes_relatorio=turmas_pendentes_relatorio,
        turmas_parciais_relatorio=turmas_parciais_relatorio,
        resumo_semanal=contexto_resumo['resumo'],
        pode_publicar_resumo_semanal=pode_publicar_resumo_semanal,
        relatorio_instantaneo_turmas=relatorio_instantaneo_turmas,
    )
    return {
        'scope_label': contexto_escopo['scope_label'],
        'ano_destino_preparo': contexto_escopo['ano_destino_preparo'],
        'resumo_semanal': contexto_resumo['resumo'],
        'resumo_semanal_formatado': contexto_resumo['formatado'],
        'pode_publicar_resumo_semanal': pode_publicar_resumo_semanal,
        'bloco_decisao': bloco_decisao,
    }


def construir_contexto_template_dashboard(
    *, turmas, alunos, classes, licoes, avaliacoes, total_oferta,
    total_ofertas_mes, total_ofertas_mes_anterior, alunos_evolucao,
    engajamento_percent, evasao, ranking_classes, ranking_alunos_pontos,
    frequencia_atual, frequencia_anterior, ranking_ofertas,
    kpis_turma_professor, alunos_novos, alunos_novos_anterior,
    transferidos_mes, meses, faixas_etarias_labels, faixas_etarias_counts,
    operacao_diaria, contexto_operacional, pode_gerenciar_ebd,
    contexto_periodo, ebd_config_igreja_link, ebd_config_source_info,
    ebd_pontos_config,
):
    """Monta o contrato completo consumido pelo template do dashboard."""
    bloco_decisao = contexto_operacional['bloco_decisao']
    return {
        'turmas': turmas,
        'alunos': alunos,
        'classes': classes,
        'licoes': licoes,
        'avaliacoes': avaliacoes,
        'total_turmas': turmas.count(),
        'total_alunos': alunos.count(),
        'total_classes': classes.count(),
        'total_licoes': licoes.count(),
        'total_oferta': total_oferta,
        'total_ofertas_mes': total_ofertas_mes,
        'total_ofertas_mes_anterior': total_ofertas_mes_anterior,
        'alunos_evolucao': alunos_evolucao,
        'engajamento_percent': engajamento_percent,
        'evasao': evasao,
        'ranking_classes': ranking_classes,
        'ranking_alunos_pontos': ranking_alunos_pontos,
        'freq_geral': frequencia_atual,
        'freq_mes_anterior': frequencia_anterior,
        'ranking_ofertas': ranking_ofertas,
        'kpis_turma_professor': kpis_turma_professor[:6],
        'alunos_novos': alunos_novos,
        'alunos_novos_mes_anterior': alunos_novos_anterior,
        'transferidos_mes': transferidos_mes,
        'meses': [mes.strftime('%m/%Y') for mes in meses],
        'faixas_etarias_labels': faixas_etarias_labels,
        'faixas_etarias_counts': faixas_etarias_counts,
        'comparativo_periodo_cards': bloco_decisao['comparativos'],
        'data_relatorio_dia': operacao_diaria['data_relatorio'],
        'relatorio_instantaneo_turmas': operacao_diaria['relatorio_turmas'],
        'turmas_pendentes_relatorio': operacao_diaria['pendentes_relatorio'],
        'turmas_parciais_relatorio': operacao_diaria['parciais_relatorio'],
        'turmas_completas_relatorio': operacao_diaria['completas_relatorio'],
        'turmas_previstas_semana': operacao_diaria['turmas_previstas_semana'],
        'turmas_com_chamada_semana': operacao_diaria['turmas_com_chamada_semana'],
        'turmas_sem_chamada_semana': operacao_diaria['turmas_sem_chamada_semana'],
        'houve_janela_operacional': operacao_diaria['houve_janela'],
        'insights_dashboard': bloco_decisao['insights'][:3],
        'painel_executivo': bloco_decisao['painel_executivo'],
        'resumo_semanal': contexto_operacional['resumo_semanal'],
        'resumo_semanal_formatado': contexto_operacional['resumo_semanal_formatado'],
        'centro_acoes_operacionais': bloco_decisao['centro_acoes'],
        'checklist_operacional_domingo': bloco_decisao['checklist'],
        'pode_publicar_resumo_semanal': contexto_operacional['pode_publicar_resumo_semanal'],
        'pode_preparar_ano_letivo': pode_gerenciar_ebd,
        'ano_destino_preparo': contexto_operacional['ano_destino_preparo'],
        'periodo_anterior_label': contexto_periodo['periodo_anterior_label'],
        'periodo_selecionado_label': contexto_periodo['periodo_selecionado_label'],
        'periodo_tipo_label': contexto_periodo['periodo_tipo_label'],
        'tipo_periodo': contexto_periodo['tipo_periodo'],
        'anos_letivos': contexto_periodo['anos_letivos'],
        'ano_letivo_selecionado': contexto_periodo['ano_letivo_selecionado'],
        'periodos_disponiveis': contexto_periodo['periodos_disponiveis'],
        'periodo_selecionado': contexto_periodo['periodo_selecionado'],
        'scope_label': contexto_operacional['scope_label'],
        'ebd_config_igreja_link': ebd_config_igreja_link,
        'ebd_config_source': ebd_config_source_info['ebd_config_source'],
        'ebd_config_source_label': ebd_config_source_info['ebd_config_source_label'],
        'ebd_config_source_hint': ebd_config_source_info['ebd_config_source_hint'],
        'ebd_pontos_config': ebd_pontos_config,
    }


def construir_contexto_completo_dashboard(
    *, request, turmas, alunos, classes, licoes, avaliacoes, ofertas_escopo,
    igrejas_escopo, igreja, ministerio, hoje, ano_atual, periodo_ctx,
    ebd_config_source_info, ebd_pontos_config, dia_ebd,
):
    """Orquestra todos os indicadores e o contexto do dashboard em um unico dict.

    Recebe querysets ja restritos ao escopo/permissao e devolve o contexto
    completo consumido pelo template, sem depender da view.
    """
    tipo_periodo_inicial = periodo_ctx['tipo_periodo']
    contexto_periodo_dashboard = preparar_contexto_periodo_dashboard(
        periodo_ctx=periodo_ctx,
        periodo_tipo_label=dict(ConfiguracaoSistema.EBD_PERIODO_CHOICES).get(
            tipo_periodo_inicial,
            tipo_periodo_inicial.title(),
        ),
        hoje=hoje,
    )
    tipo_periodo = contexto_periodo_dashboard['tipo_periodo']
    ano_letivo_selecionado = contexto_periodo_dashboard['ano_letivo_selecionado']
    data_inicio_periodo = contexto_periodo_dashboard['inicio_atual']
    data_fim_periodo = contexto_periodo_dashboard['fim_atual']
    data_inicio_periodo_anterior = contexto_periodo_dashboard['inicio_anterior']
    data_fim_periodo_anterior = contexto_periodo_dashboard['fim_anterior']

    ebd_config_igreja_link = obter_link_configuracao_dashboard(
        usuario=request.user,
        igreja=igreja,
    )

    evolucao_alunos = coletar_evolucao_mensal_alunos_dashboard(
        alunos_escopo=alunos,
        hoje=hoje,
    )
    meses = evolucao_alunos['meses']
    alunos_evolucao = evolucao_alunos['totais']

    indicadores_frequencia = coletar_indicadores_frequencia_dashboard(
        alunos=alunos,
        classes=classes,
        inicio_atual=data_inicio_periodo,
        fim_atual=data_fim_periodo,
        inicio_anterior=data_inicio_periodo_anterior,
        fim_anterior=data_fim_periodo_anterior,
    )
    freq_geral = indicadores_frequencia['frequencia_atual']
    freq_mes_anterior = indicadores_frequencia['frequencia_anterior']
    engajamento_percent = indicadores_frequencia['engajamento']

    evasao = contar_evasao_dashboard(alunos_escopo=alunos, ano=ano_atual)

    ranking_classes = indicadores_frequencia['ranking_classes']

    ranking_alunos_pontos = coletar_ranking_pontos_dashboard(
        turmas=turmas,
        alunos_escopo=alunos,
        ano_letivo=ano_letivo_selecionado,
        inicio=data_inicio_periodo,
        fim=data_fim_periodo,
        pontos_config=ebd_pontos_config,
    )

    indicadores_ofertas = coletar_indicadores_ofertas_dashboard(
        classes=classes,
        ofertas_escopo=ofertas_escopo,
        ano=ano_atual,
        inicio_atual=data_inicio_periodo,
        fim_atual=data_fim_periodo,
        inicio_anterior=data_inicio_periodo_anterior,
        fim_anterior=data_fim_periodo_anterior,
    )
    total_oferta = indicadores_ofertas['total_geral']
    ranking_ofertas = indicadores_ofertas['ranking_classes']

    dados_kpis_turma = coletar_dados_kpis_turma_professor(
        turmas_escopo=turmas,
        ano_letivo=ano_letivo_selecionado,
        inicio_atual=data_inicio_periodo,
        fim_atual=data_fim_periodo,
        inicio_anterior=data_inicio_periodo_anterior,
        fim_anterior=data_fim_periodo_anterior,
    )

    kpis_turma_professor = construir_kpis_turma_professor(
        turmas=dados_kpis_turma['turmas'],
        freq_atual_map=dados_kpis_turma['freq_atual_map'],
        freq_anterior_map=dados_kpis_turma['freq_anterior_map'],
        ofertas_atual_map=dados_kpis_turma['ofertas_atual_map'],
        ofertas_anterior_map=dados_kpis_turma['ofertas_anterior_map'],
        professor_por_turma=dados_kpis_turma['professor_por_turma'],
    )

    movimentacao_alunos = coletar_indicadores_movimentacao_dashboard(
        turmas=turmas,
        alunos_escopo=alunos,
        inicio_atual=data_inicio_periodo,
        fim_atual=data_fim_periodo,
        inicio_anterior=data_inicio_periodo_anterior,
        fim_anterior=data_fim_periodo_anterior,
    )
    alunos_novos = movimentacao_alunos['alunos_novos']
    alunos_novos_mes_anterior = movimentacao_alunos['alunos_novos_anterior']
    transferidos_mes = movimentacao_alunos['transferidos']

    total_ofertas_mes = indicadores_ofertas['total_atual']
    total_ofertas_mes_anterior = indicadores_ofertas['total_anterior']

    faixas_etarias_labels, faixas_etarias_counts = calcular_distribuicao_faixa_etaria(
        alunos=alunos,
        hoje=hoje,
    )

    operacao_diaria = coletar_operacao_diaria_dashboard(
        turmas=turmas,
        licoes=licoes,
        ano_letivo=ano_letivo_selecionado,
        data_relatorio=request.GET.get('data_relatorio'),
        hoje=hoje,
        inicio_periodo=data_inicio_periodo,
        fim_periodo=data_fim_periodo,
        dia_ebd=dia_ebd,
    )
    pode_gerenciar_ebd = usuario_pode_gerenciar_ebd(request.user)
    contexto_operacional_dashboard = preparar_contexto_operacional_dashboard(
        igreja=igreja,
        igrejas_escopo=igrejas_escopo,
        ano_letivo=ano_letivo_selecionado,
        ano_atual=ano_atual,
        ministerio=ministerio,
        hoje=hoje,
        pode_gerenciar_ebd=pode_gerenciar_ebd,
        alunos_novos=alunos_novos,
        alunos_novos_anterior=alunos_novos_mes_anterior,
        frequencia_atual=freq_geral,
        frequencia_anterior=freq_mes_anterior,
        ofertas_atual=total_ofertas_mes,
        ofertas_anterior=total_ofertas_mes_anterior,
        evasao=evasao,
        turmas_previstas_semana=operacao_diaria['turmas_previstas_semana'],
        turmas_sem_chamada_semana=operacao_diaria['turmas_sem_chamada_semana'],
        houve_janela_operacional=operacao_diaria['houve_janela'],
        turmas_pendentes_relatorio=operacao_diaria['pendentes_relatorio'],
        turmas_parciais_relatorio=operacao_diaria['parciais_relatorio'],
        relatorio_instantaneo_turmas=operacao_diaria['relatorio_turmas'],
    )

    return construir_contexto_template_dashboard(
        turmas=turmas,
        alunos=alunos,
        classes=classes,
        licoes=licoes,
        avaliacoes=avaliacoes,
        total_oferta=total_oferta,
        total_ofertas_mes=total_ofertas_mes,
        total_ofertas_mes_anterior=total_ofertas_mes_anterior,
        alunos_evolucao=alunos_evolucao,
        engajamento_percent=engajamento_percent,
        evasao=evasao,
        ranking_classes=ranking_classes,
        ranking_alunos_pontos=ranking_alunos_pontos,
        frequencia_atual=freq_geral,
        frequencia_anterior=freq_mes_anterior,
        ranking_ofertas=ranking_ofertas,
        kpis_turma_professor=kpis_turma_professor,
        alunos_novos=alunos_novos,
        alunos_novos_anterior=alunos_novos_mes_anterior,
        transferidos_mes=transferidos_mes,
        meses=meses,
        faixas_etarias_labels=faixas_etarias_labels,
        faixas_etarias_counts=faixas_etarias_counts,
        operacao_diaria=operacao_diaria,
        contexto_operacional=contexto_operacional_dashboard,
        pode_gerenciar_ebd=pode_gerenciar_ebd,
        contexto_periodo=contexto_periodo_dashboard,
        ebd_config_igreja_link=ebd_config_igreja_link,
        ebd_config_source_info=ebd_config_source_info,
        ebd_pontos_config=ebd_pontos_config,
    )


def publicar_resumo_semanal_dashboard(*, ministerio, autor, igrejas_escopo, hoje):
    """Gera e publica o resumo semanal da EBD para a lideranca autorizada."""
    from comunicacao.models import Aviso

    inicio, fim = get_faixa_semana_anterior(hoje)
    resumo = build_resumo_semanal_ebd(
        ministerio,
        inicio,
        fim,
        igrejas=igrejas_escopo,
    )
    titulo = f"Resumo semanal EBD - {inicio.strftime('%d/%m')} a {fim.strftime('%d/%m')}"
    Aviso.objects.create(
        ministerio=ministerio,
        titulo=titulo,
        conteudo=formatar_resumo_semanal_ebd(resumo),
        autor=autor,
        publicado=True,
    )
    return {'inicio': inicio, 'fim': fim}


def coletar_operacao_diaria_dashboard(
    *, turmas, licoes, ano_letivo, data_relatorio, hoje, inicio_periodo, fim_periodo, dia_ebd,
):
    """Consolida o relatorio diario e o fechamento semanal para turmas autorizadas."""
    contexto_relatorio = preparar_contexto_relatorio_instantaneo(
        turmas=turmas,
        ano_letivo=ano_letivo,
        data_relatorio=data_relatorio,
        hoje=hoje,
        licoes=licoes,
    )
    dados_relatorio = coletar_dados_relatorio_instantaneo(
        turmas=contexto_relatorio['turmas'],
        data=contexto_relatorio['data'],
    )
    relatorio_turmas = construir_relatorio_instantaneo_turmas(
        turmas=dados_relatorio['turmas'],
        frequencias_por_turma=dados_relatorio['frequencias_por_turma'],
        ofertas_por_turma=dados_relatorio['ofertas_por_turma'],
        ofertas_por_classe=dados_relatorio['ofertas_por_classe'],
    )
    status_relatorio = resumir_status_relatorio_instantaneo(relatorio_turmas)
    janela = calcular_janela_operacional_semana(
        hoje=hoje,
        inicio_periodo=inicio_periodo,
        fim_periodo=fim_periodo,
        dia_ebd=dia_ebd,
    )
    status_chamadas = calcular_status_chamadas_semanais(
        turmas=turmas,
        inicio=janela['inicio'],
        fim=janela['fim'],
        houve_janela=janela['houve_janela'],
    )
    return {
        'data_relatorio': contexto_relatorio['data'],
        'relatorio_turmas': relatorio_turmas,
        'pendentes_relatorio': status_relatorio['pendentes'],
        'parciais_relatorio': status_relatorio['parciais'],
        'completas_relatorio': status_relatorio['completas'],
        'houve_janela': janela['houve_janela'],
        'turmas_previstas_semana': status_chamadas['previstas'],
        'turmas_com_chamada_semana': status_chamadas['realizadas'],
        'turmas_sem_chamada_semana': status_chamadas['pendentes'],
    }


def contar_evasao_dashboard(*, alunos_escopo, ano):
    """Conta alunos inativos do ano dentro de um escopo ja autorizado."""
    return alunos_escopo.filter(
        ativo=False,
        turma__ano_letivo__ano__contains=str(ano),
    ).count()


def obter_link_configuracao_dashboard(*, usuario, igreja):
    """Retorna somente o link de configuracao permitido ao usuario do painel."""
    if not pode_editar_configuracao_org(usuario):
        return None
    if igreja is not None:
        return reverse('configuracao:editar_igreja_config', args=[igreja.pk])
    return reverse('configuracao:lista_igrejas')


def construir_insights_dashboard(*, frequencia, evasao, ofertas_atual, ofertas_anterior):
    insights = []
    if frequencia >= 80:
        insights.append({'tone': 'is-positive', 'icon': 'fas fa-circle-check', 'title': 'Frequência saudável', 'message': f'Frequência média do período em {frequencia:.1f}%. Mantenha o ritmo das turmas com melhor presença.', 'cta_label': 'Ver frequência', 'cta_url': reverse('escola_biblica:frequencia_list')})
    elif frequencia < 65:
        insights.append({'tone': 'is-warning', 'icon': 'fas fa-triangle-exclamation', 'title': 'Atenção na presença', 'message': f'Frequência média do período em {frequencia:.1f}%. Vale reforçar contato com responsáveis e líderes de turma.', 'cta_label': 'Abrir turmas', 'cta_url': reverse('escola_biblica:turma_list')})
    if evasao > 0:
        insights.append({'tone': 'is-danger', 'icon': 'fas fa-user-minus', 'title': 'Evasão no ano letivo', 'message': f'Há {evasao} aluno(s) inativos no ano. Priorize o acompanhamento das turmas com maior queda.', 'cta_label': 'Ver alunos', 'cta_url': reverse('escola_biblica:aluno_list')})
    if ofertas_atual > ofertas_anterior:
        insights.append({'tone': 'is-info', 'icon': 'fas fa-hand-holding-dollar', 'title': 'Evolução nas ofertas', 'message': 'As ofertas cresceram em relação ao período anterior. Bom sinal de participação comunitária.', 'cta_label': 'Abrir ofertas', 'cta_url': reverse('escola_biblica:oferta_classe_list')})
    if not insights:
        insights.append({'tone': 'is-neutral', 'icon': 'fas fa-circle-info', 'title': 'Painel estável no período', 'message': 'Sem alertas críticos neste recorte. Mantenha a rotina de chamada, ensino e acompanhamento.', 'cta_label': 'Ver turmas', 'cta_url': reverse('escola_biblica:turma_list')})
    return insights


def construir_cards_comparativos_dashboard(itens):
    return [construir_comparativo_card(*item) for item in itens]


def construir_bloco_decisao_dashboard(
    *, alunos_novos, alunos_novos_anterior, frequencia_atual, frequencia_anterior,
    ofertas_atual, ofertas_anterior, evasao, turmas_previstas_semana,
    turmas_sem_chamada_semana, houve_janela_operacional,
    turmas_pendentes_relatorio, turmas_parciais_relatorio, resumo_semanal,
    pode_publicar_resumo_semanal, relatorio_instantaneo_turmas,
):
    """Reune os elementos de decisao exibidos no dashboard, sem consultar dados."""
    comparativos = construir_cards_comparativos_dashboard([
        ('Novos alunos', alunos_novos, alunos_novos_anterior, 'up', 'int'),
        ('Frequência média (%)', frequencia_atual, frequencia_anterior, 'up', 'percent'),
        ('Ofertas do período (R$)', ofertas_atual, ofertas_anterior, 'up', 'currency'),
    ])
    insights = construir_insights_dashboard(
        frequencia=frequencia_atual,
        evasao=evasao,
        ofertas_atual=ofertas_atual,
        ofertas_anterior=ofertas_anterior,
    )
    painel_executivo = construir_painel_executivo_ebd(
        freq_atual=frequencia_atual,
        freq_anterior=frequencia_anterior,
        ofertas_atual=ofertas_atual,
        ofertas_anterior=ofertas_anterior,
        turmas_previstas_semana=turmas_previstas_semana,
        turmas_sem_chamada_semana=turmas_sem_chamada_semana,
        evasao=evasao,
    )
    checklist = construir_checklist_operacional_domingo(
        houve_janela_operacional=houve_janela_operacional,
        turmas_sem_chamada_semana=turmas_sem_chamada_semana,
        turmas_parciais_relatorio=turmas_parciais_relatorio,
        turmas_pendentes_relatorio=turmas_pendentes_relatorio,
    )
    centro_acoes = construir_centro_acoes_operacionais(
        houve_janela_operacional=houve_janela_operacional,
        turmas_sem_chamada_semana=turmas_sem_chamada_semana,
        turmas_pendentes_relatorio=turmas_pendentes_relatorio,
        turmas_parciais_relatorio=turmas_parciais_relatorio,
        evasao=evasao,
        resumo_semanal=resumo_semanal,
        pode_publicar_resumo_semanal=pode_publicar_resumo_semanal,
        relatorio_instantaneo_turmas=relatorio_instantaneo_turmas,
    )
    return {
        'comparativos': comparativos,
        'insights': insights,
        'painel_executivo': painel_executivo,
        'checklist': checklist,
        'centro_acoes': centro_acoes,
    }


def construir_comparativo_card(label, atual, anterior, melhora_quando='up', formato='int'):
    diferenca = atual - anterior
    subiu = diferenca > 0
    melhorou = subiu if melhora_quando == 'up' else not subiu
    if diferenca == 0:
        tone = 'is-neutral'
        icon = 'fas fa-minus'
    else:
        tone = 'is-positive' if melhorou else 'is-warning'
        icon = 'fas fa-arrow-up' if subiu else 'fas fa-arrow-down'
    if formato == 'currency':
        diferenca_label = f"{diferenca:+.2f}"
    elif formato == 'percent':
        diferenca_label = f"{diferenca:+.1f}"
    else:
        diferenca_label = f"{int(diferenca):+d}"
    return {
        'label': label,
        'atual': atual,
        'anterior': anterior,
        'diferenca': diferenca,
        'diferenca_label': diferenca_label,
        'tone': tone,
        'icon': icon,
        'format': formato,
    }


def construir_kpis_turma_professor(
    *, turmas, freq_atual_map, freq_anterior_map, ofertas_atual_map,
    ofertas_anterior_map, professor_por_turma,
):
    itens = []
    for turma in turmas:
        freq_atual_item = freq_atual_map.get(turma.id, {})
        freq_anterior_item = freq_anterior_map.get(turma.id, {})
        total_atual = int(freq_atual_item.get('total') or 0)
        presentes_atual = int(freq_atual_item.get('presentes') or 0)
        total_anterior = int(freq_anterior_item.get('total') or 0)
        presentes_anterior = int(freq_anterior_item.get('presentes') or 0)
        freq_atual = round((presentes_atual / total_atual) * 100, 1) if total_atual else 0.0
        freq_anterior = round((presentes_anterior / total_anterior) * 100, 1) if total_anterior else 0.0
        delta_freq = round(freq_atual - freq_anterior, 1)
        oferta_atual = float(ofertas_atual_map.get(turma.id) or 0)
        oferta_anterior = float(ofertas_anterior_map.get(turma.id) or 0)
        delta_oferta = round(oferta_atual - oferta_anterior, 2)
        if delta_freq > 0:
            tendencia_tone, tendencia_icon = 'is-positive', 'fas fa-arrow-trend-up'
        elif delta_freq < 0:
            tendencia_tone, tendencia_icon = 'is-warning', 'fas fa-arrow-trend-down'
        else:
            tendencia_tone, tendencia_icon = 'is-neutral', 'fas fa-minus'
        itens.append({
            'turma_id': turma.id,
            'turma_nome': turma.nome,
            'classe_nome': turma.classe.nome if getattr(turma, 'classe_id', None) else '-',
            'professor_nome': professor_por_turma.get(turma.id) or 'Sem professor vinculado',
            'frequencia_atual': freq_atual,
            'frequencia_anterior': freq_anterior,
            'delta_frequencia': delta_freq,
            'oferta_atual': oferta_atual,
            'delta_oferta': delta_oferta,
            'tendencia_tone': tendencia_tone,
            'tendencia_icon': tendencia_icon,
        })
    itens.sort(key=lambda item: (-item['frequencia_atual'], -item['oferta_atual'], item['turma_nome'].casefold()))
    return itens


def coletar_dados_kpis_turma_professor(
    *, turmas_escopo, ano_letivo, inicio_atual, fim_atual, inicio_anterior, fim_anterior,
):
    """Busca os indicadores por turma a partir de uma queryset já restrita ao escopo."""
    turmas_qs = turmas_escopo.select_related('classe').order_by('nome')
    if ano_letivo:
        turmas_qs = turmas_qs.filter(ano_letivo=ano_letivo)
    turmas = list(turmas_qs)
    turma_ids = [turma.id for turma in turmas]

    def frequencias_por_periodo(inicio, fim):
        return {
            item['aluno__turma_id']: item
            for item in Frequencia.objects.filter(
                aluno__turma_id__in=turma_ids, data__gte=inicio, data__lte=fim,
            ).values('aluno__turma_id').annotate(
                total=Count('id'), presentes=Count('id', filter=Q(presente=True)),
            )
        }

    def ofertas_por_periodo(inicio, fim):
        return {
            item['turma_id']: item['total'] or 0
            for item in OfertaClasse.objects.filter(
                turma_id__in=turma_ids, data__gte=inicio, data__lte=fim,
            ).values('turma_id').annotate(total=Sum('valor'))
        }

    professor_por_turma = {}
    for item in MembroCargo.objects.filter(
        membro__turmas_ebd__in=turmas,
        cargo__is_ebd=True,
        cargo__nome__icontains='professor',
        data_fim__isnull=True,
    ).values('membro__turmas_ebd', 'membro__nome').order_by('membro__nome'):
        professor_por_turma.setdefault(item['membro__turmas_ebd'], item['membro__nome'])

    return {
        'turmas': turmas,
        'freq_atual_map': frequencias_por_periodo(inicio_atual, fim_atual),
        'freq_anterior_map': frequencias_por_periodo(inicio_anterior, fim_anterior),
        'ofertas_atual_map': ofertas_por_periodo(inicio_atual, fim_atual),
        'ofertas_anterior_map': ofertas_por_periodo(inicio_anterior, fim_anterior),
        'professor_por_turma': professor_por_turma,
    }


def construir_relatorio_instantaneo_turmas(
    *, turmas, frequencias_por_turma, ofertas_por_turma, ofertas_por_classe,
):
    """Monta o status diário das turmas a partir de dados já filtrados."""
    relatorio = []
    for turma in turmas:
        resumo_frequencia = frequencias_por_turma.get(turma.id, {})
        matriculados = turma.matriculados_ativos or 0
        presentes = resumo_frequencia.get('presentes', 0)
        oferta_total = (
            (ofertas_por_turma.get(turma.id, 0) or 0)
            + (ofertas_por_classe.get(turma.classe_id, 0) or 0)
        )
        chamada_realizada = (resumo_frequencia.get('chamadas', 0) or 0) > 0

        if not chamada_realizada:
            status_label, status_tone = 'Pendente', 'is-pending'
        elif oferta_total > 0:
            status_label, status_tone = 'Completo', 'is-complete'
        else:
            status_label, status_tone = 'Parcial', 'is-partial'

        relatorio.append({
            'turma_id': turma.id,
            'turma_nome': turma.nome,
            'segmento_nome': turma.classe.nome if turma.classe_id else '-',
            'matriculados': matriculados,
            'presentes': presentes,
            'ausentes': max(matriculados - presentes, 0),
            'biblias': resumo_frequencia.get('biblias', 0),
            'alunos_ofertantes': resumo_frequencia.get('ofertas_individuais', 0),
            'oferta_total': oferta_total,
            'chamada_realizada': chamada_realizada,
            'status_label': status_label,
            'status_tone': status_tone,
        })

    status_prioridade = {'is-pending': 0, 'is-partial': 1, 'is-complete': 2}
    return sorted(
        relatorio,
        key=lambda item: (status_prioridade.get(item['status_tone'], 9), item['turma_nome'].casefold()),
    )


def calcular_janela_operacional_semana(*, hoje, inicio_periodo, fim_periodo, dia_ebd):
    """Determina a parcela da semana atual válida para a operação da EBD."""
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    inicio_janela = max(inicio_semana, inicio_periodo)
    fim_janela = min(hoje, fim_semana, fim_periodo)
    houve_janela = hoje.weekday() >= dia_ebd and inicio_janela <= fim_janela
    return {
        'inicio': inicio_janela,
        'fim': fim_janela,
        'houve_janela': houve_janela,
    }


def calcular_status_chamadas_semanais(*, turmas, inicio, fim, houve_janela):
    """Apura chamadas da semana para turmas previamente autorizadas."""
    turma_ids = list(turmas.values_list('id', flat=True))
    previstas = len(turma_ids) if houve_janela else 0
    realizadas = 0
    if previstas:
        realizadas = Frequencia.objects.filter(
            aluno__turma_id__in=turma_ids,
            data__gte=inicio,
            data__lte=fim,
        ).values_list('aluno__turma_id', flat=True).distinct().count()
    return {
        'previstas': previstas,
        'realizadas': realizadas,
        'pendentes': max(previstas - realizadas, 0),
    }


def construir_checklist_operacional_domingo(
    *, houve_janela_operacional, turmas_sem_chamada_semana,
    turmas_parciais_relatorio, turmas_pendentes_relatorio,
):
    return [
        {
            'titulo': 'Abrir dashboard pelo celular',
            'descricao': 'Validar filtros de ano/período e confirmar se a igreja ativa está correta.',
            'status': 'done' if houve_janela_operacional else 'pending',
        },
        {
            'titulo': 'Fechar chamadas pendentes',
            'descricao': f'{turmas_sem_chamada_semana} turma(s) sem chamada registrada na janela operacional.',
            'status': 'done' if turmas_sem_chamada_semana == 0 else 'pending',
        },
        {
            'titulo': 'Conferir turmas parciais do dia',
            'descricao': f'{turmas_parciais_relatorio} turma(s) com chamada sem fechamento completo de oferta/status.',
            'status': 'done' if turmas_parciais_relatorio == 0 else 'warning',
        },
        {
            'titulo': 'Revisar pendências do relatório instantâneo',
            'descricao': f'{turmas_pendentes_relatorio} turma(s) ainda pendente(s) no recorte do dia.',
            'status': 'done' if turmas_pendentes_relatorio == 0 else 'warning',
        },
    ]


def construir_painel_executivo_ebd(
    *, freq_atual, freq_anterior, ofertas_atual, ofertas_anterior,
    turmas_previstas_semana, turmas_sem_chamada_semana, evasao,
):
    anomalia_labels = {
        'frequencia_baixa': 'Frequência baixa',
        'queda_frequencia_acelerada': 'Queda acelerada de frequência',
        'chamadas_pendentes_semana': 'Chamadas pendentes na semana',
        'queda_ofertas_relevante': 'Queda relevante de ofertas',
        'evasao_detectada': 'Evasão detectada',
    }
    delta_freq = round(float(freq_atual) - float(freq_anterior), 1)
    delta_ofertas = round(float(ofertas_atual) - float(ofertas_anterior), 2)
    pendencia_pct = round((turmas_sem_chamada_semana / turmas_previstas_semana) * 100, 1) if turmas_previstas_semana > 0 else 0.0
    tendencia = {'freq_delta': delta_freq, 'ofertas_delta': delta_ofertas, 'pendencia_semana_pct': pendencia_pct}
    anomalias = []
    if float(freq_atual) < 65:
        anomalias.append('frequencia_baixa')
    if delta_freq <= -5:
        anomalias.append('queda_frequencia_acelerada')
    if pendencia_pct >= 30:
        anomalias.append('chamadas_pendentes_semana')
    if float(ofertas_anterior) > 0 and float(ofertas_atual) <= float(ofertas_anterior) * 0.8:
        anomalias.append('queda_ofertas_relevante')
    if int(evasao or 0) > 0:
        anomalias.append('evasao_detectada')
    recomendacoes = []
    if 'chamadas_pendentes_semana' in anomalias:
        recomendacoes.append({'titulo': 'Priorizar fechamento de chamadas pendentes', 'descricao': 'Concentre o acompanhamento das turmas sem chamada registrada nesta semana operacional.', 'cta_label': 'Abrir turmas', 'cta_url': reverse('escola_biblica:turma_list')})
    if 'frequencia_baixa' in anomalias or 'queda_frequencia_acelerada' in anomalias:
        recomendacoes.append({'titulo': 'Executar plano de recuperação de presença', 'descricao': 'Acione professores e responsáveis das classes mais críticas para retomada de frequência.', 'cta_label': 'Ver frequência', 'cta_url': reverse('escola_biblica:frequencia_list')})
    if 'queda_ofertas_relevante' in anomalias:
        recomendacoes.append({'titulo': 'Revisar engajamento de ofertas por classe', 'descricao': 'Analise as classes com maior queda e alinhe ações de orientação e prestação de contas.', 'cta_label': 'Abrir ofertas', 'cta_url': reverse('escola_biblica:oferta_classe_list')})
    if 'evasao_detectada' in anomalias:
        recomendacoes.append({'titulo': 'Iniciar contato de retenção de alunos', 'descricao': 'Mapeie motivos de inatividade e ative um plano de acompanhamento por turma.', 'cta_label': 'Ver alunos', 'cta_url': reverse('escola_biblica:aluno_list')})
    if not recomendacoes:
        recomendacoes.append({'titulo': 'Operação estável no período', 'descricao': 'Sem anomalias críticas detectadas. Mantenha rotina semanal e monitoramento dos indicadores.', 'cta_label': 'Abrir dashboard gráfico', 'cta_url': reverse('escola_biblica:dashboard_graficos')})
    return {
        'tendencia': tendencia,
        'anomalias': anomalias,
        'anomalias_detalhes': [{'chave': chave, 'label': anomalia_labels.get(chave, chave)} for chave in anomalias],
        'recomendacoes': recomendacoes[:3],
    }


def construir_centro_acoes_operacionais(
    *, houve_janela_operacional, turmas_sem_chamada_semana,
    turmas_pendentes_relatorio, turmas_parciais_relatorio, evasao,
    resumo_semanal, pode_publicar_resumo_semanal, relatorio_instantaneo_turmas,
):
    fila = []
    turmas_pendentes = [item['turma_nome'] for item in relatorio_instantaneo_turmas if item['status_tone'] == 'is-pending'][:3]
    turmas_parciais = [item['turma_nome'] for item in relatorio_instantaneo_turmas if item['status_tone'] == 'is-partial'][:3]
    if houve_janela_operacional and turmas_sem_chamada_semana > 0:
        detalhe = f'{turmas_sem_chamada_semana} turma(s) sem chamada na janela operacional.'
        if turmas_pendentes:
            detalhe += f" Priorize: {', '.join(turmas_pendentes)}."
        fila.append({'prioridade': 0, 'tone': 'is-danger', 'icone': 'fas fa-siren-on', 'titulo': 'Fechar chamadas da semana', 'descricao': detalhe, 'contador': turmas_sem_chamada_semana, 'contador_label': 'pendências críticas', 'cta_label': 'Abrir painel de turmas', 'cta_url': reverse('escola_biblica:turma_list')})
    if turmas_pendentes_relatorio > 0:
        detalhe = f'{turmas_pendentes_relatorio} turma(s) ainda sem fechamento no relatório do dia.'
        if turmas_pendentes:
            detalhe += f" Turmas: {', '.join(turmas_pendentes)}."
        fila.append({'prioridade': 1, 'tone': 'is-warning', 'icone': 'fas fa-hourglass-half', 'titulo': 'Fechar pendências do relatório do dia', 'descricao': detalhe, 'contador': turmas_pendentes_relatorio, 'contador_label': 'turmas pendentes', 'cta_label': 'Abrir relatório instantâneo', 'cta_url': reverse('escola_biblica:relatorio_ebd_dia')})
    if turmas_parciais_relatorio > 0:
        detalhe = f'{turmas_parciais_relatorio} turma(s) com chamada feita, mas sem oferta ou fechamento completo.'
        if turmas_parciais:
            detalhe += f" Revisar: {', '.join(turmas_parciais)}."
        fila.append({'prioridade': 2, 'tone': 'is-info', 'icone': 'fas fa-list-check', 'titulo': 'Completar registros parciais', 'descricao': detalhe, 'contador': turmas_parciais_relatorio, 'contador_label': 'registros parciais', 'cta_label': 'Revisar chamadas', 'cta_url': reverse('escola_biblica:turma_list')})
    if evasao > 0:
        fila.append({'prioridade': 3, 'tone': 'is-warning', 'icone': 'fas fa-user-minus', 'titulo': 'Acompanhar evasão do período', 'descricao': f'{evasao} aluno(s) inativos no ano letivo atual. Acione professores e secretaria para retenção.', 'contador': evasao, 'contador_label': 'alunos em risco', 'cta_label': 'Abrir alunos', 'cta_url': reverse('escola_biblica:aluno_list')})
    if pode_publicar_resumo_semanal and resumo_semanal:
        fila.append({'prioridade': 4, 'tone': 'is-neutral', 'icone': 'fas fa-bullhorn', 'titulo': 'Publicar resumo semanal para liderança', 'descricao': f"Resumo pronto com {resumo_semanal.get('turmas_com_chamada', 0)}/{resumo_semanal.get('turmas_previstas', 0)} turmas fechadas e frequência média de {float(resumo_semanal.get('frequencia_media', 0) or 0):.1f}%", 'contador': None, 'contador_label': '', 'cta_label': 'Ir ao bloco de resumo', 'cta_url': '#centro-resumo-semanal'})
    fila.sort(key=lambda item: item['prioridade'])
    if not fila:
        fila.append({'prioridade': 9, 'tone': 'is-positive', 'icone': 'fas fa-circle-check', 'titulo': 'Fila operacional zerada', 'descricao': 'Sem pendências críticas neste recorte. Mantenha a rotina semanal e acompanhe apenas a execução normal.', 'contador': 0, 'contador_label': 'pendências abertas', 'cta_label': 'Ver turmas', 'cta_url': reverse('escola_biblica:turma_list')})
    return {'fila': fila[:5], 'pendencias_abertas': sum(1 for item in fila if item['prioridade'] < 9)}
