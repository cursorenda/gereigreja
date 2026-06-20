from datetime import datetime, timedelta

from django.utils import timezone

from eventos.models import Evento

from .models import ProgramacaoPadraoIgreja


def _datas_por_weekday(dia_semana, inicio, fim):
    atual = inicio
    delta = (dia_semana - atual.weekday()) % 7
    atual = atual + timedelta(days=delta)
    while atual <= fim:
        yield atual
        atual += timedelta(days=7)


def _datas_por_weekday_intervalo(dia_semana, inicio, fim, intervalo_semanas):
    atual = inicio
    delta = (dia_semana - atual.weekday()) % 7
    atual = atual + timedelta(days=delta)
    salto = max(1, int(intervalo_semanas or 1)) * 7
    while atual <= fim:
        yield atual
        atual += timedelta(days=salto)


def _nth_weekday_of_month(ano, mes, weekday, nth):
    """Retorna a data da N-ésima ocorrência do weekday no mês. nth=-1 representa última."""
    primeiro_dia = timezone.datetime(ano, mes, 1).date()
    deslocamento = (weekday - primeiro_dia.weekday()) % 7
    primeira_ocorrencia = primeiro_dia + timedelta(days=deslocamento)

    if nth == -1:
        if mes == 12:
            proximo_mes = timezone.datetime(ano + 1, 1, 1).date()
        else:
            proximo_mes = timezone.datetime(ano, mes + 1, 1).date()
        ultimo_dia_mes = proximo_mes - timedelta(days=1)
        deslocamento_volta = (ultimo_dia_mes.weekday() - weekday) % 7
        return ultimo_dia_mes - timedelta(days=deslocamento_volta)

    data = primeira_ocorrencia + timedelta(days=7 * (nth - 1))
    if data.month != mes:
        return None
    return data


def _datas_mensais_por_ocorrencia(dia_semana, ocorrencia_mensal, inicio, fim):
    ano = inicio.year
    mes = inicio.month

    while True:
        candidata = _nth_weekday_of_month(ano, mes, dia_semana, ocorrencia_mensal)
        if candidata and inicio <= candidata <= fim:
            yield candidata

        if ano > fim.year or (ano == fim.year and mes >= fim.month):
            break

        if mes == 12:
            mes = 1
            ano += 1
        else:
            mes += 1


def _datas_anuais_por_ocorrencia(dia_semana, ocorrencia_mensal, mes_ano, inicio, fim):
    for ano in range(inicio.year, fim.year + 1):
        candidata = _nth_weekday_of_month(ano, mes_ano, dia_semana, ocorrencia_mensal)
        if candidata and inicio <= candidata <= fim:
            yield candidata


def _montar_faixa_horario(data_evento, hora_inicio, duracao_minutos):
    tz = timezone.get_current_timezone()
    inicio = timezone.make_aware(datetime.combine(data_evento, hora_inicio), tz)
    fim = inicio + timedelta(minutes=duracao_minutos)
    return inicio, fim


def _resolver_duracao_minutos(programacao):
    if getattr(programacao, 'hora_termino', None):
        dt_inicio = datetime.combine(datetime.today().date(), programacao.hora_inicio)
        dt_fim = datetime.combine(datetime.today().date(), programacao.hora_termino)
        if dt_fim > dt_inicio:
            return int((dt_fim - dt_inicio).total_seconds() // 60)
    return programacao.duracao_minutos or 90


def sync_programacao_padrao(programacao, horizonte_dias=120):
    """Sincroniza uma programação padrão com eventos concretos no horizonte futuro."""
    if programacao is None:
        return

    hoje = timezone.localdate()
    limite = hoje + timedelta(days=horizonte_dias)

    if not programacao.ativo:
        Evento.objects.filter(
            igreja=programacao.igreja,
            programacao_padrao=programacao,
            data_inicio__date__gte=hoje,
            status_evento='ativo',
        ).delete()
        return

    excecoes = programacao.get_datas_excecao_set()

    if programacao.frequencia == 'mensal_por_ocorrencia' and programacao.ocorrencia_mensal:
        datas = _datas_mensais_por_ocorrencia(programacao.dia_semana, programacao.ocorrencia_mensal, hoje, limite)
    elif programacao.frequencia == 'anual_por_ocorrencia' and programacao.ocorrencia_mensal and programacao.mes_ano:
        datas = _datas_anuais_por_ocorrencia(programacao.dia_semana, programacao.ocorrencia_mensal, programacao.mes_ano, hoje, limite)
    else:
        datas = _datas_por_weekday_intervalo(programacao.dia_semana, hoje, limite, programacao.intervalo_semanas)

    for data_evento in datas:
        if data_evento in excecoes:
            continue
        duracao_minutos = _resolver_duracao_minutos(programacao)
        inicio, fim = _montar_faixa_horario(data_evento, programacao.hora_inicio, duracao_minutos)

        evento = Evento.objects.filter(
            igreja=programacao.igreja,
            programacao_padrao=programacao,
            data_inicio__date=data_evento,
        ).first()

        if evento is None:
            Evento.objects.create(
                igreja=programacao.igreja,
                titulo=programacao.nome,
                descricao=programacao.descricao,
                tipo=programacao.tipo_evento,
                local=programacao.local,
                data_inicio=inicio,
                data_fim=fim,
                quantidade_dias=1,
                recorrente=False,
                frequencia='nenhuma',
                intervalo=1,
                status_evento='ativo',
                programacao_padrao=programacao,
            )
            continue

        update_fields = []
        if evento.titulo != programacao.nome:
            evento.titulo = programacao.nome
            update_fields.append('titulo')
        if evento.descricao != programacao.descricao:
            evento.descricao = programacao.descricao
            update_fields.append('descricao')
        if evento.tipo != programacao.tipo_evento:
            evento.tipo = programacao.tipo_evento
            update_fields.append('tipo')
        if evento.local != programacao.local:
            evento.local = programacao.local
            update_fields.append('local')
        if evento.data_inicio != inicio:
            evento.data_inicio = inicio
            update_fields.append('data_inicio')
        if evento.data_fim != fim:
            evento.data_fim = fim
            update_fields.append('data_fim')
        if evento.programacao_padrao_id != programacao.id:
            evento.programacao_padrao = programacao
            update_fields.append('programacao_padrao')

        if update_fields:
            evento.save(update_fields=update_fields)


def sync_programacoes_igreja(igreja, horizonte_dias=120):
    if igreja is None:
        return 0

    programacoes = ProgramacaoPadraoIgreja.objects.filter(igreja=igreja)
    for programacao in programacoes:
        sync_programacao_padrao(programacao, horizonte_dias=horizonte_dias)

    return programacoes.count()
