import datetime
from dateutil.rrule import rrule, WEEKLY, MONTHLY, YEARLY, DAILY

def gerar_datas_recorrencia(evento):
    """
    Gera uma lista de datas de início para cada ocorrência do evento recorrente,
    baseado nos campos do modelo Evento.
    """
    datas = []
    if not evento.recorrente or evento.frequencia == 'nenhuma':
        return [evento.data_inicio]


    from django.utils import timezone
    dt_inicio = evento.data_inicio
    intervalo = evento.intervalo or 1
    dt_fim = evento.data_fim_recorrencia

    # Corrige dt_fim para datetime com mesmo timezone de dt_inicio
    if dt_fim:
        if isinstance(dt_fim, datetime.date) and not isinstance(dt_fim, datetime.datetime):
            # Usa o final do dia para garantir inclusão
            dt_fim = datetime.datetime.combine(dt_fim, datetime.time(23, 59, 59))
        # Se dt_inicio tem tzinfo, aplica o mesmo em dt_fim
        if timezone.is_aware(dt_inicio):
            if timezone.is_naive(dt_fim):
                dt_fim = timezone.make_aware(dt_fim, dt_inicio.tzinfo)
            else:
                dt_fim = dt_fim.astimezone(dt_inicio.tzinfo)
        else:
            if timezone.is_aware(dt_fim):
                dt_fim = timezone.make_naive(dt_fim)
    else:
        return [dt_inicio]

    # Frequência semanal
    if evento.frequencia == 'semanal':
        # Exemplo: MO,TU
        dias = (evento.dia_semana or '').split(',')
        dias_map = {
            'MO': 0, 'TU': 1, 'WE': 2, 'TH': 3, 'FR': 4, 'SA': 5, 'SU': 6
        }
        byweekday = [dias_map[d] for d in dias if d in dias_map]
        rule = rrule(
            freq=WEEKLY,
            interval=intervalo,
            dtstart=dt_inicio,
            until=dt_fim,
            byweekday=byweekday or None
        )
        datas = list(rule)
    elif evento.frequencia == 'mensal':
        # Exemplo: semana_mes = 1,2,-1; dia_semana = MO,TU
        semanas = [int(s) for s in (evento.semana_mes or '').split(',') if s]
        dias = (evento.dia_semana or '').split(',')
        dias_map = {
            'MO': 0, 'TU': 1, 'WE': 2, 'TH': 3, 'FR': 4, 'SA': 5, 'SU': 6
        }
        byweekday = []
        for semana in semanas:
            for d in dias:
                if d in dias_map:
                    byweekday.append(dias_map[d] + 7 * (semana-1) if semana > 0 else dias_map[d] + 7 * semana)
        # Fallback: se não houver semana/dia, gera no mesmo dia do mês
        rule = rrule(
            freq=MONTHLY,
            interval=intervalo,
            dtstart=dt_inicio,
            until=dt_fim
        )
        datas = list(rule)
    elif evento.frequencia == 'anual':
        # Exemplo: mes_ano = 1,6,12
        meses = [int(m) for m in (evento.mes_ano or '').split(',') if m]
        rule = rrule(
            freq=YEARLY,
            interval=intervalo,
            dtstart=dt_inicio,
            until=dt_fim,
            bymonth=meses or None
        )
        datas = list(rule)
    elif evento.frequencia == 'diaria':
        rule = rrule(
            freq=DAILY,
            interval=intervalo,
            dtstart=dt_inicio,
            until=dt_fim
        )
        datas = list(rule)
    else:
        datas = [dt_inicio]
    return datas