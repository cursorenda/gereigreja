"""Sincronização de calendário e lições da Escola Bíblica."""

from django.utils.dateparse import parse_time
from django.db import transaction

from .models import AnoLetivo, FechamentoPeriodoEBD, Frequencia, Licao, PeriodoEBD, Turma
from .utils import (
    gerar_datas_semana_periodo,
    gerar_domingos_periodo,
    gerar_periodos_ebd,
)


def normalizar_etapa_wizard_cronograma(valor, padrao=1):
    """Retorna uma etapa valida do assistente de cronograma."""
    try:
        etapa = int(valor)
    except (TypeError, ValueError):
        return padrao
    return etapa if etapa in (1, 2, 3, 4) else padrao


def normalizar_inteiro_wizard_cronograma(valor, padrao=0):
    """Converte campos numericos do assistente sem propagar erro de entrada."""
    try:
        return int(str(valor).replace('.', '').replace(' ', ''))
    except (TypeError, ValueError):
        return padrao


def normalizar_ids_turmas_wizard(valores):
    """Retorna IDs de turma positivos, unicos e seguros para consultas."""
    ids = []
    for valor in valores:
        texto = str(valor).strip()
        if not texto.isdigit():
            continue
        turma_id = int(texto)
        if turma_id > 0 and turma_id not in ids:
            ids.append(turma_id)
    return ids


def normalizar_status_licao_wizard(valor):
    """Mantem o status do cronograma dentro das opcoes aceitas pelo modelo."""
    return valor if valor in {'ativa', 'rascunho'} else 'ativa'


def normalizar_horario_wizard(valor):
    """Converte o horario do assistente para HH:MM ou None quando ausente."""
    if not valor:
        return None
    horario = parse_time(str(valor).strip())
    return horario.strftime('%H:%M') if horario else None


def normalizar_material_wizard(valor):
    """Mantem o material dentro do limite aceito pelo modelo de licao."""
    return str(valor or '').strip()[:255]


def normalizar_nome_licao_padrao(valor):
    """Garante um modelo de tema utilizavel pelo assistente de cronograma."""
    nome = ' '.join(str(valor or '').split())
    return nome or 'Lição {n} - {periodo}'


def montar_tema_licao_cronograma(*, nome_licao_padrao, indice, periodo_nome):
    """Monta o tema final dentro do limite do campo Tema da licao."""
    return (
        nome_licao_padrao
        .replace('{n}', str(indice))
        .replace('{periodo}', periodo_nome)
    )[:200]


def selecao_turmas_wizard_valida(*, turmas, turmas_ids):
    """Confirma que todas as turmas selecionadas permanecem no escopo permitido."""
    return bool(turmas_ids) and turmas.count() == len(turmas_ids)


def selecionar_turmas_wizard(*, turmas, turmas_ids, ano_letivo):
    """Restringe a selecao do assistente ao ano letivo e escopo ja aplicado."""
    return turmas.filter(
        id__in=turmas_ids,
        ano_letivo__ano=ano_letivo,
    )


def turmas_wizard_compativeis_com_tipo_periodo(
    *, turmas, tipo_periodo, obter_configuracao_turma=None,
):
    """Impede misturar turmas de calendarios diferentes no mesmo cronograma."""
    from .services_configuracao import (
        obter_configuracao_ebd_turma,
        obter_tipo_periodo_ebd,
    )

    obter_configuracao_turma = obter_configuracao_turma or obter_configuracao_ebd_turma
    return all(
        obter_tipo_periodo_ebd(obter_configuracao_turma(turma)) == tipo_periodo
        for turma in turmas
    )


def obter_periodo_wizard_disponivel(*, ano_letivo, numero, tipo_periodo, hoje):
    """Retorna somente periodos abertos do calendario configurado para a EBD."""
    return PeriodoEBD.objects.filter(
        ano_letivo__ano=ano_letivo,
        numero=numero,
        tipo=tipo_periodo,
        data_fim__gte=hoje,
    ).first()


def resolver_selecao_wizard_cronograma(
    *, turmas, turmas_ids, ano_letivo, numero_periodo, tipo_periodo, hoje,
):
    """Centraliza a selecao segura de periodo e turmas do wizard."""
    periodo = obter_periodo_wizard_disponivel(
        ano_letivo=ano_letivo,
        numero=numero_periodo,
        tipo_periodo=tipo_periodo,
        hoje=hoje,
    )
    turmas_selecionadas = selecionar_turmas_wizard(
        turmas=turmas,
        turmas_ids=turmas_ids,
        ano_letivo=ano_letivo,
    )
    tipo_periodo_compativel = turmas_wizard_compativeis_com_tipo_periodo(
        turmas=turmas_selecionadas,
        tipo_periodo=tipo_periodo,
    )
    selecao_basica_valida = bool(periodo) and selecao_turmas_wizard_valida(
        turmas=turmas_selecionadas,
        turmas_ids=turmas_ids,
    )
    valida = selecao_basica_valida and tipo_periodo_compativel
    return {
        'periodo': periodo,
        'turmas': turmas_selecionadas,
        'valida': valida,
        'mensagem_erro': (
            '' if valida
            else 'Selecione turmas com o mesmo calendario configurado.'
            if selecao_basica_valida
            else 'Selecione turmas validas para o ano letivo e um periodo valido.'
        ),
    }


def validar_ano_letivo(valor):
    """Converte o ano letivo e rejeita valores fora de uma faixa razoavel."""
    ano = normalizar_inteiro_wizard_cronograma(valor, None)
    if ano is None or not 1900 <= ano <= 9999:
        raise ValueError('Ano letivo invalido.')
    return ano


def tipo_periodo_ebd_valido(valor):
    """Informa se o tipo recebido pertence aos calendarios suportados pela EBD."""
    return valor in {'trimestre', 'quadrimestre', 'semestre', 'ano'}


def abrir_proximo_periodo(*, ano_letivo, tipo_periodo):
    """Prepara o proximo periodo disponivel e informa o resultado da operacao."""
    ano_letivo_obj, _ = AnoLetivo.objects.get_or_create(
        ano=ano_letivo,
        defaults={'ativo': True},
    )
    periodos_gerados = gerar_periodos_ebd(ano_letivo, tipo_periodo)
    periodos_existentes = PeriodoEBD.objects.filter(
        ano_letivo=ano_letivo_obj,
        tipo=tipo_periodo,
    ).order_by('numero')
    ultimo_periodo = periodos_existentes.last()

    if ultimo_periodo is None:
        proximo_periodo = periodos_gerados[0]
        ano_destino = ano_letivo
        novo_ano = False
    else:
        proximo_periodo = next(
            (
                periodo for periodo in periodos_gerados
                if periodo['numero'] == ultimo_periodo.numero + 1
            ),
            None,
        )
        ano_destino = ano_letivo
        novo_ano = False
        if proximo_periodo is None:
            ano_destino = ano_letivo + 1
            ano_letivo_obj, _ = AnoLetivo.objects.get_or_create(
                ano=ano_destino,
                defaults={'ativo': True},
            )
            proximo_periodo = gerar_periodos_ebd(ano_destino, tipo_periodo)[0]
            novo_ano = True

    _, criado = PeriodoEBD.objects.get_or_create(
        ano_letivo=ano_letivo_obj,
        numero=proximo_periodo['numero'],
        tipo=tipo_periodo,
        defaults={
            'data_inicio': proximo_periodo['data_inicio'],
            'data_fim': proximo_periodo['data_fim'],
        },
    )
    return {
        'ano_destino': ano_destino,
        'numero_periodo': proximo_periodo['numero'],
        'novo_ano': novo_ano,
        'criado': criado,
    }


def preparar_dados_wizard_cronograma(
    *, parametros, ano_atual, horario_padrao='', usar_horario_padrao=False,
):
    """Extrai os campos compartilhados nas etapas de configuracao do assistente."""
    horario = parametros.get('horario', '')
    if usar_horario_padrao and not horario:
        horario = horario_padrao
    horario = normalizar_horario_wizard(horario)

    return {
        'ano_letivo': normalizar_inteiro_wizard_cronograma(
            parametros.get('ano_letivo'), ano_atual,
        ),
        'periodo': normalizar_inteiro_wizard_cronograma(parametros.get('periodo')),
        'turmas_ids': normalizar_ids_turmas_wizard(parametros.getlist('turmas')),
        'material': normalizar_material_wizard(parametros.get('material', '')),
        'horario': horario,
        'status': normalizar_status_licao_wizard(parametros.get('status', 'ativa')),
        'observacoes': parametros.get('observacoes', ''),
        'nome_licao_padrao': normalizar_nome_licao_padrao(
            parametros.get('nome_licao_padrao'),
        ),
    }


def preparar_transicao_wizard_cronograma(
    *, parametros, ano_atual, turmas, tipo_periodo, hoje,
    horario_padrao='', usar_horario_padrao=False,
):
    """Reune os dados normalizados e a selecao segura usados entre etapas."""
    dados = preparar_dados_wizard_cronograma(
        parametros=parametros,
        ano_atual=ano_atual,
        horario_padrao=horario_padrao,
        usar_horario_padrao=usar_horario_padrao,
    )
    selecao = resolver_selecao_wizard_cronograma(
        turmas=turmas,
        turmas_ids=dados['turmas_ids'],
        ano_letivo=dados['ano_letivo'],
        numero_periodo=dados['periodo'],
        tipo_periodo=tipo_periodo,
        hoje=hoje,
    )
    periodo = selecao['periodo']
    periodo_nome = (
        f"{periodo.get_tipo_display()} {periodo.numero}"
        if periodo else 'Periodo'
    )
    return {
        'dados': dados,
        'selecao': selecao,
        'periodo_nome': periodo_nome,
    }


def construir_contexto_formulario_wizard_cronograma(*, dados, horario=None, etapa=None):
    """Mantem os campos do formulario consistentes entre as etapas do wizard."""
    contexto = {
        'ano_letivo': dados['ano_letivo'],
        'periodo': dados['periodo'],
        'turmas': dados['turmas_ids'],
        'material': dados['material'],
        'horario': dados['horario'] if horario is None else horario,
        'status': dados['status'],
        'observacoes': dados['observacoes'],
        'nome_licao_padrao': dados['nome_licao_padrao'],
    }
    if etapa is not None:
        contexto['etapa'] = etapa
    return contexto


def preparar_contexto_periodos_listagem_turmas(
    *, ano_letivo_raw, periodo_raw, tipo_periodo, hoje,
):
    """Seleciona o ano e periodo usados na listagem de turmas."""
    ano_atual = hoje.year
    if ano_letivo_raw:
        try:
            ano_letivo_int = int(str(ano_letivo_raw).replace('.', '').replace(',', '').strip())
            ano_letivo = AnoLetivo.objects.get(ano=ano_letivo_int)
        except (AnoLetivo.DoesNotExist, ValueError):
            ano_letivo, _ = AnoLetivo.objects.get_or_create(
                ano=ano_atual,
                defaults={'ativo': True},
            )
    else:
        ano_letivo, _ = AnoLetivo.objects.get_or_create(
            ano=ano_atual,
            defaults={'ativo': True},
        )

    periodos = PeriodoEBD.objects.filter(
        ano_letivo=ano_letivo,
        tipo=tipo_periodo,
    ).order_by('numero')
    periodo_atual = periodos.filter(data_inicio__lte=hoje, data_fim__gte=hoje).first()
    if periodo_raw:
        try:
            periodo_selecionado = periodos.get(numero=periodo_raw)
        except PeriodoEBD.DoesNotExist:
            periodo_selecionado = periodo_atual or periodos.first()
    else:
        periodo_selecionado = periodo_atual or periodos.first()

    ano_anterior = ano_letivo.ano - 1
    sugerir_copiar = (
        not Turma.objects.filter(ano_letivo=ano_letivo).exists()
        and Turma.objects.filter(ano_letivo__ano=ano_anterior).exists()
    )
    return {
        'anos_letivos': AnoLetivo.objects.order_by('-ano'),
        'ano_letivo_selecionado': ano_letivo,
        'periodos': periodos,
        'periodo_atual': periodo_atual,
        'periodo_selecionado': periodo_selecionado,
        'periodo_filtro_chip': (
            periodo_selecionado
            if periodo_selecionado and periodo_atual and periodo_selecionado.id != periodo_atual.id
            else None
        ),
        'sugerir_copiar': sugerir_copiar,
        'mostrar_banner_abrir_periodo': (
            ano_letivo.ano == ano_atual and (not periodos or not periodo_selecionado)
        ),
    }


def obter_ano_letivo_para_criacao_turma(*, ano_letivo_raw, ano_atual):
    """Retorna o ano letivo informado ou cria o ano corrente como padrao."""
    if ano_letivo_raw:
        try:
            ano = int(str(ano_letivo_raw).replace('.', '').replace(',', '').strip())
            ano_letivo = AnoLetivo.objects.filter(ano=ano).first()
            if ano_letivo is not None:
                return ano_letivo
        except (TypeError, ValueError):
            pass
    return AnoLetivo.objects.get_or_create(
        ano=ano_atual,
        defaults={'ativo': True},
    )[0]


def obter_datas_aula_wizard_cronograma(*, turma, periodo):
    """Retorna as datas de aula no dia configurado para a turma."""
    from .services_configuracao import (
        obter_configuracao_ebd_turma,
        obter_dia_semana_ebd,
    )

    configuracao = obter_configuracao_ebd_turma(turma)
    return gerar_datas_semana_periodo(
        periodo.data_inicio,
        periodo.data_fim,
        dia_semana=obter_dia_semana_ebd(configuracao),
    )


def construir_previa_cronograma(*, turmas, periodo, periodo_nome, nome_licao_padrao, status):
    """Monta as lições que serão criadas pelo assistente de cronograma."""
    if periodo is None:
        return []

    previa = []
    for turma in turmas:
        for indice, domingo in enumerate(
            obter_datas_aula_wizard_cronograma(turma=turma, periodo=periodo), start=1,
        ):
            tema = montar_tema_licao_cronograma(
                nome_licao_padrao=nome_licao_padrao,
                indice=indice,
                periodo_nome=periodo_nome,
            )
            previa.append({
                'turma_nome': turma.nome,
                'data': domingo,
                'tema': tema,
                'professor': turma.get_professor_nome(),
                'status': status,
            })
    return previa


def criar_licoes_cronograma(
    *, turmas, periodo, periodo_nome, nome_licao_padrao, material, observacoes, horario, status,
):
    """Cria as lições ainda inexistentes para as turmas e o período informados."""
    if periodo is None:
        return 0

    total_criadas = 0
    for turma in turmas:
        professor = turma.get_professor_ebd()
        for indice, domingo in enumerate(
            obter_datas_aula_wizard_cronograma(turma=turma, periodo=periodo), start=1,
        ):
            tema = montar_tema_licao_cronograma(
                nome_licao_padrao=nome_licao_padrao,
                indice=indice,
                periodo_nome=periodo_nome,
            )
            _, criada = Licao.objects.get_or_create(
                turma=turma,
                data=domingo,
                defaults={
                    'tema': tema,
                    'material': material,
                    'observacoes': observacoes,
                    'horario': horario,
                    'status': status,
                    'professor': professor,
                    'periodo': periodo,
                },
            )
            total_criadas += int(criada)
    return total_criadas


def persistir_licoes_geradas(*, licoes):
    """Persiste lições geradas, sem duplicar uma mesma turma e data."""
    total_criadas = 0
    for licao_data in licoes:
        _, criada = Licao.objects.get_or_create(
            turma=licao_data['turma'],
            data=licao_data['data'],
            defaults={
                'tema': licao_data['tema'],
                'material': licao_data['material'],
                'observacoes': licao_data['observacoes'],
                'horario': licao_data['horario'],
                'status': licao_data['status'],
                'professor': licao_data['professor'],
            },
        )
        total_criadas += int(criada)
    return total_criadas


def gerar_e_persistir_licoes_periodos(
    *, ano, tipo_periodo, turmas, material='', observacoes='', horario=None, status='ativa', dia_semana=6,
):
    """Gera lições nos períodos configurados e persiste somente as inexistentes."""
    turmas = list(turmas)
    ano_letivo, _ = AnoLetivo.objects.get_or_create(ano=ano, defaults={'ativo': False})
    for periodo in gerar_periodos_ebd(ano, tipo_periodo):
        PeriodoEBD.objects.get_or_create(
            ano_letivo=ano_letivo,
            tipo=tipo_periodo,
            numero=periodo['numero'],
            defaults={
                'data_inicio': periodo['data_inicio'],
                'data_fim': periodo['data_fim'],
            },
        )
    licoes = []
    periodos = PeriodoEBD.objects.filter(
        ano_letivo=ano_letivo, tipo=tipo_periodo,
    ).order_by('numero')
    for periodo in periodos:
        for turma in turmas:
            professor = turma.get_professor_ebd()
            for indice, data_aula in enumerate(
                gerar_datas_semana_periodo(
                    periodo.data_inicio, periodo.data_fim, dia_semana=dia_semana,
                ), start=1,
            ):
                licoes.append({
                    'turma': turma,
                    'data': data_aula,
                    'tema': f'Lição {indice} - {periodo.numero}º {tipo_periodo.capitalize()} {ano}',
                    'material': material,
                    'observacoes': observacoes,
                    'horario': horario,
                    'status': status,
                    'professor': professor,
                })
    return persistir_licoes_geradas(licoes=licoes)


def agrupar_turmas_por_calendario(*, turmas, obter_configuracao_turma=None):
    """Agrupa turmas pela configuracao efetiva usada para gerar suas licoes."""
    from .services_configuracao import (
        obter_configuracao_ebd_turma,
        obter_dia_semana_ebd,
        obter_tipo_periodo_ebd,
    )

    obter_configuracao_turma = obter_configuracao_turma or obter_configuracao_ebd_turma
    grupos = {}
    for turma in turmas:
        configuracao = obter_configuracao_turma(turma)
        chave_calendario = (
            obter_tipo_periodo_ebd(configuracao),
            obter_dia_semana_ebd(configuracao),
            getattr(configuracao, 'ebd_horario', None),
        )
        grupos.setdefault(chave_calendario, []).append(turma)
    return grupos


def gerar_cronograma_para_turma(
    *, ano, turma_selecionada, turmas_escopo, material='', observacoes='', status='ativa',
):
    """Gera aulas usando a configuracao efetiva da turma selecionada."""
    from .services_configuracao import (
        obter_configuracao_ebd_turma,
        obter_dia_semana_ebd,
        obter_tipo_periodo_ebd,
    )

    configuracao_turma = obter_configuracao_ebd_turma(turma_selecionada)
    tipo_periodo = obter_tipo_periodo_ebd(configuracao_turma)
    criadas = gerar_e_persistir_licoes_periodos(
        ano=ano,
        tipo_periodo=tipo_periodo,
        turmas=[turma_selecionada] if turma_selecionada else turmas_escopo,
        material=material,
        observacoes=observacoes,
        horario=getattr(configuracao_turma, 'ebd_horario', None),
        status=status,
        dia_semana=obter_dia_semana_ebd(configuracao_turma),
    )
    return {'criadas': criadas, 'tipo_periodo': tipo_periodo}


def sincronizar_periodos_e_licoes(*, turmas, hoje, tipo_periodo, dia_semana):
    """Cria períodos e lições do período vigente/próximo para as turmas informadas."""
    anos_letivos = []
    for ano in (hoje.year, hoje.year + 1):
        ano_letivo, _ = AnoLetivo.objects.get_or_create(
            ano=ano, defaults={'ativo': ano == hoje.year},
        )
        anos_letivos.append(ano_letivo)
        for periodo in gerar_periodos_ebd(ano, tipo_periodo):
            PeriodoEBD.objects.get_or_create(
                ano_letivo=ano_letivo,
                tipo=tipo_periodo,
                numero=periodo['numero'],
                defaults={
                    'data_inicio': periodo['data_inicio'],
                    'data_fim': periodo['data_fim'],
                },
            )

    periodo_referencia = PeriodoEBD.objects.filter(
        ano_letivo__in=anos_letivos,
        tipo=tipo_periodo,
        data_inicio__lte=hoje,
        data_fim__gte=hoje,
    ).order_by('ano_letivo__ano', 'numero').first()
    if periodo_referencia is None:
        periodo_referencia = PeriodoEBD.objects.filter(
            ano_letivo__in=anos_letivos, tipo=tipo_periodo, data_inicio__gte=hoje,
        ).order_by('data_inicio').first()
    if periodo_referencia is None:
        return 0, None

    datas_aula = gerar_datas_semana_periodo(
        periodo_referencia.data_inicio, periodo_referencia.data_fim, dia_semana=dia_semana,
    )
    periodo_nome = (
        f"{periodo_referencia.get_tipo_display()} "
        f"{periodo_referencia.numero}/{periodo_referencia.ano_letivo.ano}"
    )
    total_criadas = 0
    for turma in turmas.filter(ano_letivo=periodo_referencia.ano_letivo).order_by('id'):
        for indice, data_aula in enumerate(datas_aula, start=1):
            _, criada = Licao.objects.get_or_create(
                turma=turma,
                data=data_aula,
                defaults={
                    'tema': f'Lição {indice} - {periodo_nome}',
                    'status': 'ativa',
                    'periodo': periodo_referencia,
                },
            )
            total_criadas += int(criada)
    return total_criadas, periodo_nome


def obter_periodo_filtro(*, ano_letivo_filtro, periodo_filtro, tipo_periodo, hoje):
    anos_letivos = AnoLetivo.objects.order_by('-ano')
    try:
        ano_letivo_selecionado = (
            anos_letivos.get(ano=int(str(ano_letivo_filtro).strip()))
            if ano_letivo_filtro else anos_letivos.filter(ano=hoje.year).first() or anos_letivos.first()
        )
    except (AnoLetivo.DoesNotExist, ValueError):
        ano_letivo_selecionado = anos_letivos.filter(ano=hoje.year).first() or anos_letivos.first()
    periodos_disponiveis = PeriodoEBD.objects.none()
    if ano_letivo_selecionado:
        periodos_disponiveis = PeriodoEBD.objects.filter(
            ano_letivo=ano_letivo_selecionado, tipo=tipo_periodo,
        ).order_by('numero')
    periodo_selecionado = None
    if periodos_disponiveis.exists():
        try:
            periodo_selecionado = (
                periodos_disponiveis.get(numero=int(periodo_filtro))
                if periodo_filtro else None
            )
        except (PeriodoEBD.DoesNotExist, ValueError):
            periodo_selecionado = None
        periodo_selecionado = periodo_selecionado or (
            periodos_disponiveis.filter(data_inicio__lte=hoje, data_fim__gte=hoje).first()
            or periodos_disponiveis.first()
        )
    return {
        'tipo_periodo': tipo_periodo,
        'anos_letivos': anos_letivos,
        'ano_letivo_selecionado': ano_letivo_selecionado,
        'periodos_disponiveis': periodos_disponiveis,
        'periodo_selecionado': periodo_selecionado,
    }


def construir_status_periodo(*, periodo, hoje):
    """Monta os indicadores de andamento exibidos na listagem de turmas."""
    status = {
        'ebd_aulas_total': None,
        'ebd_aulas_realizadas': None,
        'ebd_percentual': None,
        'ebd_status_label': 'Em andamento',
        'ebd_status_bg': '#0d8281',
        'ebd_status_color': '#fff',
        'ebd_status_tone': 'is-active',
    }
    if periodo is None:
        return status

    datas_aula = gerar_domingos_periodo(periodo.data_inicio, periodo.data_fim)
    status['ebd_aulas_total'] = len(datas_aula)
    status['ebd_aulas_realizadas'] = sum(1 for data_aula in datas_aula if data_aula <= hoje)
    status['ebd_percentual'] = (
        int((status['ebd_aulas_realizadas'] / status['ebd_aulas_total']) * 100)
        if status['ebd_aulas_total'] else 0
    )
    if hoje > periodo.data_fim:
        status.update({
            'ebd_status_label': 'Encerrado',
            'ebd_status_bg': '#6c757d',
            'ebd_status_tone': 'is-closed',
            'ebd_aulas_realizadas': status['ebd_aulas_total'],
            'ebd_percentual': 100,
        })
    elif hoje < periodo.data_inicio:
        status.update({
            'ebd_status_label': 'Programado',
            'ebd_status_bg': '#0d6efd',
            'ebd_status_tone': 'is-planned',
            'ebd_aulas_realizadas': 0,
            'ebd_percentual': 0,
        })
    return status


def avaliar_prontidao_fechamento_periodo(
    *, periodo, hoje, aulas_previstas, chamadas_realizadas, motivo_excecao='',
):
    """Informa se um período pode ser formalmente fechado.

    A regra deliberadamente trata somente chamadas de aulas previstas como
    pendência crítica. Oferta pode não fazer parte da rotina de uma igreja e,
    portanto, permanece como alerta operacional, não como bloqueio.
    """
    if hoje <= periodo.data_fim:
        return {
            'pode_fechar': False,
            'tipo_fechamento': None,
            'permite_excecao': False,
            'motivo': 'O período só pode ser fechado após sua data final.',
            'aulas_pendentes': [],
        }

    chamadas = set(chamadas_realizadas)
    pendentes = sorted(set(aulas_previstas) - chamadas, key=lambda item: (item[1], item[0]))
    if pendentes:
        motivo_excecao = str(motivo_excecao or '').strip()
        return {
            'pode_fechar': bool(motivo_excecao),
            'tipo_fechamento': 'excecao' if motivo_excecao else None,
            'permite_excecao': True,
            'motivo': (
                'Fechamento com exceção autorizado e registrado.'
                if motivo_excecao else
                'Existem chamadas pendentes. Informe o motivo para fechar com exceção.'
            ),
            'aulas_pendentes': pendentes,
        }
    return {
        'pode_fechar': True,
        'tipo_fechamento': 'normal',
        'permite_excecao': False,
        'motivo': '',
        'aulas_pendentes': [],
    }


def diagnosticar_fechamento_periodo(*, turmas, periodo, hoje, motivo_excecao=''):
    """Aplica a política de fechamento aos registros reais já autorizados.

    Só considera turmas com alunos ativos. Uma chamada é considerada concluída
    quando existe ao menos uma frequência para a turma e data da aula prevista.
    """
    turmas_com_alunos = turmas.filter(alunos__ativo=True).distinct()
    aulas_previstas = list(
        Licao.objects.filter(
            turma__in=turmas_com_alunos,
            periodo=periodo,
            data__lte=periodo.data_fim,
        ).values_list('turma_id', 'data').distinct()
    )
    chamadas_realizadas = list(
        Frequencia.objects.filter(
            aluno__turma__in=turmas_com_alunos,
            data__gte=periodo.data_inicio,
            data__lte=periodo.data_fim,
        ).values_list('aluno__turma_id', 'data').distinct()
    )
    diagnostico = avaliar_prontidao_fechamento_periodo(
        periodo=periodo,
        hoje=hoje,
        aulas_previstas=aulas_previstas,
        chamadas_realizadas=chamadas_realizadas,
        motivo_excecao=motivo_excecao,
    )
    nomes_turmas = dict(turmas_com_alunos.values_list('id', 'nome'))
    diagnostico['pendencias'] = [
        {'turma_id': turma_id, 'turma_nome': nomes_turmas.get(turma_id, 'Turma'), 'data': data}
        for turma_id, data in diagnostico['aulas_pendentes']
    ]
    return diagnostico


@transaction.atomic
def registrar_fechamento_periodo(*, turmas, periodo, igreja, usuario, hoje, motivo_excecao=''):
    """Registra apenas fechamentos autorizados pela política operacional."""
    diagnostico = diagnosticar_fechamento_periodo(
        turmas=turmas, periodo=periodo, hoje=hoje, motivo_excecao=motivo_excecao,
    )
    if not diagnostico['pode_fechar']:
        return {'fechado': False, 'diagnostico': diagnostico, 'fechamento': None}

    fechamento, criado = FechamentoPeriodoEBD.objects.update_or_create(
        periodo=periodo,
        igreja=igreja,
        defaults={
            'fechado_por': usuario,
            'tipo': diagnostico['tipo_fechamento'],
            'motivo_excecao': str(motivo_excecao or '').strip() if diagnostico['tipo_fechamento'] == 'excecao' else '',
        },
    )
    return {'fechado': True, 'criado': criado, 'diagnostico': diagnostico, 'fechamento': fechamento}


def executar_fluxo_fechamento_periodo(*, turmas, periodo, igreja, usuario, hoje, confirmar, motivo_excecao=''):
    """Centraliza diagnóstico e confirmação para manter a view apenas HTTP."""
    if confirmar:
        return registrar_fechamento_periodo(
            turmas=turmas, periodo=periodo, igreja=igreja, usuario=usuario,
            hoje=hoje, motivo_excecao=motivo_excecao,
        )
    return {
        'fechado': False,
        'fechamento': None,
        'diagnostico': diagnosticar_fechamento_periodo(
            turmas=turmas, periodo=periodo, hoje=hoje,
        ),
    }


def preparar_contexto_fechamento_periodo(*, periodo, igrejas, igreja_ativa, turmas):
    """Resolve a igreja efetiva e restringe turmas ao ano do período."""
    igreja = igreja_ativa or (igrejas.first() if igrejas.count() == 1 else None)
    if igreja is None or not igrejas.filter(pk=igreja.pk).exists():
        return {'valido': False, 'igreja': None, 'turmas': None}
    return {
        'valido': True,
        'igreja': igreja,
        'turmas': turmas.filter(igreja=igreja, ano_letivo=periodo.ano_letivo),
    }


def construir_contexto_template_fechamento_periodo(*, periodo, igreja, diagnostico, motivo_excecao):
    """Entrega ao template apenas os dados de apresentação do fechamento."""
    return {
        'periodo': periodo,
        'igreja': igreja,
        'diagnostico': diagnostico,
        'motivo_excecao': motivo_excecao,
    }
