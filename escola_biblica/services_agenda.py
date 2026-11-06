from datetime import datetime, time, timedelta

from django.db import router, transaction
from django.utils import timezone

from configuracao.models import ConfiguracaoSistema, Igreja
from eventos.models import Evento

from .models import Licao

TITULO_EVENTO_EBD = 'Escola Dominical'
DESCRICAO_EVENTO_EBD = (
    'Evento consolidado da Escola Dominical gerado automaticamente pela EBD. '
    'As turmas e licoes continuam detalhadas no modulo Escola Biblica.'
)


def _get_dia_semana_ebd(igreja):
    """Resolve dia da semana da EBD com fallback igreja -> ministerio -> domingo."""
    if igreja is not None and getattr(igreja, 'ebd_dia_semana', None) is not None:
        return igreja.ebd_dia_semana

    if igreja is not None and getattr(igreja, 'ministerio', None) is not None:
        config = ConfiguracaoSistema.objects.filter(ministerio=igreja.ministerio).only('ebd_dia_semana').first()
        if config is not None and config.ebd_dia_semana is not None:
            return config.ebd_dia_semana

    return 6


def _proxima_data_para_dia_semana(dia_semana):
    """Retorna a próxima data para um weekday Python (0=seg, 6=dom), incluindo hoje."""
    hoje = timezone.localdate()
    delta = (dia_semana - hoje.weekday()) % 7
    return hoje + timedelta(days=delta)


def _igreja_tem_estrutura_ebd(igreja):
    """Evita poluir agenda em igrejas sem estrutura EBD."""
    from .models import Turma

    return Turma.objects.filter(igreja=igreja).exists() or Turma.objects.filter(classe__igreja=igreja).exists()


def sync_evento_padrao_ebd_por_igreja(igreja):
    """
    Garante ao menos a próxima ocorrência da EBD na agenda para a igreja,
    mesmo quando ainda não existem lições cadastradas.
    """
    if igreja is None or not _igreja_tem_estrutura_ebd(igreja):
        return

    dia_semana = _get_dia_semana_ebd(igreja)
    proxima_data = _proxima_data_para_dia_semana(dia_semana)
    _upsert_evento_escola_dominical(igreja=igreja, data_aula=proxima_data)


def _resolver_igreja_turma(turma):
    igreja = getattr(turma, 'igreja', None)
    if igreja is not None:
        return igreja

    classe = getattr(turma, 'classe', None)
    if classe is not None and getattr(classe, 'igreja', None) is not None:
        return classe.igreja

    membro = turma.membros.exclude(igreja__isnull=True).select_related('igreja').first()
    if membro is not None:
        return membro.igreja

    return None


def _get_faixa_horario_evento(data_aula, igreja):
    hora_inicio = time(hour=9, minute=0)
    if igreja is not None:
        if getattr(igreja, 'ebd_horario', None) is not None:
            hora_inicio = igreja.ebd_horario
        elif getattr(igreja, 'ministerio', None) is not None:
            config = ConfiguracaoSistema.objects.filter(ministerio=igreja.ministerio).only('ebd_horario').first()
            if config is not None and config.ebd_horario is not None:
                hora_inicio = config.ebd_horario

    tz = timezone.get_current_timezone()
    inicio = timezone.make_aware(datetime.combine(data_aula, hora_inicio), tz)
    fim = inicio + timedelta(hours=1, minutes=30)
    return inicio, fim


def set_licao_evento_agenda(licoes, *, evento_id, using):
    """Set or clear the link for a scoped Licao queryset on its write alias."""
    # QuerySet.db may resolve through a router; _db records an explicit .using() binding.
    queryset_alias = licoes._db
    if queryset_alias is not None and queryset_alias != using:
        raise ValueError(f"Queryset alias {queryset_alias!r} conflicts with write alias {using!r}.")
    with transaction.atomic(using=using):
        return (
            licoes.using(using)
            .exclude(evento_agenda_id=evento_id)
            .update(evento_agenda_id=evento_id)
        )


def _upsert_evento_escola_dominical(igreja, data_aula, *, using=None):
    using = using or router.db_for_write(Evento, instance=igreja)
    eventos = Evento.objects.using(using)
    candidatos = list(
        eventos.filter(
            igreja=igreja,
            tipo='escola_dominical',
            data_inicio__date=data_aula,
        ).order_by('id')
    )

    inicio, fim = _get_faixa_horario_evento(data_aula, igreja)

    if candidatos:
        principal = candidatos[0]
        if principal.status_evento == 'cancelado':
            duplicados = candidatos[1:]
            if duplicados:
                duplicados_ids = [evento.id for evento in duplicados]
                set_licao_evento_agenda(
                    Licao.objects.filter(evento_agenda_id__in=duplicados_ids),
                    evento_id=principal.pk, using=using,
                )
                eventos.filter(id__in=duplicados_ids).delete()
            return principal

        update_fields = []
        if principal.titulo != TITULO_EVENTO_EBD:
            principal.titulo = TITULO_EVENTO_EBD
            update_fields.append('titulo')
        if principal.descricao != DESCRICAO_EVENTO_EBD:
            principal.descricao = DESCRICAO_EVENTO_EBD
            update_fields.append('descricao')
        if principal.data_inicio != inicio:
            principal.data_inicio = inicio
            update_fields.append('data_inicio')
        if principal.data_fim != fim:
            principal.data_fim = fim
            update_fields.append('data_fim')
        if principal.frequencia != 'nenhuma':
            principal.frequencia = 'nenhuma'
            update_fields.append('frequencia')
        if principal.recorrente:
            principal.recorrente = False
            update_fields.append('recorrente')
        if principal.quantidade_dias != 1:
            principal.quantidade_dias = 1
            update_fields.append('quantidade_dias')

        if update_fields:
            principal.save(update_fields=update_fields)

        duplicados = candidatos[1:]
        if duplicados:
            duplicados_ids = [evento.id for evento in duplicados]
            set_licao_evento_agenda(
                Licao.objects.filter(evento_agenda_id__in=duplicados_ids),
                evento_id=principal.pk, using=using,
            )
            eventos.filter(id__in=duplicados_ids).delete()

        return principal

    return eventos.create(
        igreja=igreja,
        titulo=TITULO_EVENTO_EBD,
        descricao=DESCRICAO_EVENTO_EBD,
        tipo='escola_dominical',
        data_inicio=inicio,
        data_fim=fim,
        quantidade_dias=1,
        recorrente=False,
        frequencia='nenhuma',
        intervalo=1,
    )


def sync_licao_evento_agenda(licao):
    turma = getattr(licao, 'turma', None)
    if turma is None:
        return

    igreja = _resolver_igreja_turma(turma)
    if igreja is None:
        return

    using = router.db_for_write(Licao, instance=licao)
    evento = _upsert_evento_escola_dominical(igreja=igreja, data_aula=licao.data, using=using)
    set_licao_evento_agenda(Licao.objects.filter(pk=licao.pk), evento_id=evento.pk, using=using)


@transaction.atomic
def sync_eventos_ebd_por_ministerio(ministerio):
    if ministerio is None:
        return

    igrejas_ids = list(Igreja.objects.filter(ministerio=ministerio).values_list('id', flat=True))
    if not igrejas_ids:
        return

    licoes = (
        Licao.objects.select_related('turma', 'turma__igreja', 'turma__classe__igreja')
        .filter(
            turma__isnull=False,
            turma__ano_letivo__ano__gte=timezone.now().date().year,
        )
        .filter(
            turma__igreja_id__in=igrejas_ids,
        )
        .order_by('data', 'id')
    )

    # Inclui turmas sem turma.igreja mas com classe.igreja do ministerio.
    licoes_sem_igreja_turma = (
        Licao.objects.select_related('turma', 'turma__igreja', 'turma__classe__igreja')
        .filter(
            turma__isnull=False,
            turma__ano_letivo__ano__gte=timezone.now().date().year,
            turma__igreja__isnull=True,
            turma__classe__igreja_id__in=igrejas_ids,
        )
        .order_by('data', 'id')
    )

    for licao in licoes:
        sync_licao_evento_agenda(licao)
    for licao in licoes_sem_igreja_turma:
        sync_licao_evento_agenda(licao)

    # Garante visibilidade mínima da EBD na agenda após configuração
    # mesmo sem lições já cadastradas para a igreja.
    for igreja_id in igrejas_ids:
        igreja = Igreja.objects.filter(pk=igreja_id).first()
        sync_evento_padrao_ebd_por_igreja(igreja)

    eventos = Evento.objects.filter(igreja_id__in=igrejas_ids, tipo='escola_dominical').order_by('id')
    for evento in eventos:
        if evento.status_evento == 'cancelado':
            continue

        inicio, fim = _get_faixa_horario_evento(evento.data_inicio.date(), evento.igreja)
        update_fields = []
        if evento.titulo != TITULO_EVENTO_EBD:
            evento.titulo = TITULO_EVENTO_EBD
            update_fields.append('titulo')
        if evento.descricao != DESCRICAO_EVENTO_EBD:
            evento.descricao = DESCRICAO_EVENTO_EBD
            update_fields.append('descricao')
        if evento.data_inicio != inicio:
            evento.data_inicio = inicio
            update_fields.append('data_inicio')
        if evento.data_fim != fim:
            evento.data_fim = fim
            update_fields.append('data_fim')
        if update_fields:
            evento.save(update_fields=update_fields)
