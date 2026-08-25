"""Regras reutilizaveis do fluxo de chamada da EBD."""

import hashlib
import json
from decimal import Decimal, InvalidOperation

from django.db import transaction

from .models import Frequencia, Licao, OfertaClasse, PeriodoEBD


EBD_PONTOS_DEFAULT = {
    'presente': 10,
    'biblia': 2,
    'revista': 2,
    'oferta': 3,
    'visitante': 5,
}


def construir_chave_idempotencia_chamada(request, turma_id, data_selecionada):
    total_forms = int(request.POST.get('form-TOTAL_FORMS') or 0)
    alunos_payload = [
        (
            request.POST.get(f'form-{indice}-aluno_id', ''),
            1 if request.POST.get(f'form-{indice}-presente') else 0,
            1 if request.POST.get(f'form-{indice}-trouxe_biblia') else 0,
            1 if request.POST.get(f'form-{indice}-trouxe_revista') else 0,
            1 if request.POST.get(f'form-{indice}-trouxe_visitante') else 0,
            1 if request.POST.get(f'form-{indice}-trouxe_oferta') else 0,
        )
        for indice in range(total_forms)
    ]
    raw = json.dumps(
        {
            'user_id': request.user.pk,
            'turma_id': turma_id,
            'data': data_selecionada.isoformat() if data_selecionada else '',
            'valor_oferta': request.POST.get('valor_oferta', ''),
            'alunos': alunos_payload,
        },
        sort_keys=True,
        ensure_ascii=True,
    )
    return f"ebd:chamada:idempotency:{hashlib.sha256(raw.encode('utf-8')).hexdigest()}"


def construir_chave_bloqueio_chamada(turma_id, data_selecionada):
    data_ref = data_selecionada.isoformat() if data_selecionada else 'sem-data'
    return f'ebd:chamada:processing:{turma_id}:{data_ref}'


class ValorOfertaInvalido(ValueError):
    """Indica que o valor informado para a oferta nao pode ser convertido."""


def calcular_pontos_frequencia_flags(
    *,
    presente=False,
    trouxe_biblia=False,
    trouxe_revista=False,
    trouxe_oferta=False,
    trouxe_visitante=False,
    pontos_cfg=None,
):
    """Calcula o snapshot de pontos da frequencia a partir das flags informadas."""
    cfg = pontos_cfg or EBD_PONTOS_DEFAULT
    total = 0
    if presente:
        total += cfg['presente']
    if trouxe_biblia:
        total += cfg['biblia']
    if trouxe_revista:
        total += cfg['revista']
    if trouxe_oferta:
        total += cfg['oferta']
    if trouxe_visitante:
        total += cfg['visitante']
    return total


def formulario_chamada_corresponde_a_turma(formset, alunos):
    """Garante que o POST contenha uma vez cada aluno ativo da turma."""
    alunos_formulario = [form.cleaned_data['aluno_id'] for form in formset]
    alunos_permitidos = set(alunos.values_list('pk', flat=True))
    return (
        len(alunos_formulario) == len(alunos_permitidos)
        and len(set(alunos_formulario)) == len(alunos_formulario)
        and set(alunos_formulario) == alunos_permitidos
    )


def preparar_formset_inicial_chamada(*, alunos, data, formset_class):
    """Monta o formset inicial com os registros ja salvos para a data."""
    frequencias_por_aluno = {
        frequencia.aluno_id: frequencia
        for frequencia in Frequencia.objects.filter(aluno__in=alunos, data=data)
    }
    inicial = [
        {
            'aluno_id': aluno.id,
            'nome': aluno.nome,
            'presente': bool(
                frequencias_por_aluno.get(aluno.id)
                and frequencias_por_aluno[aluno.id].presente
            ),
            'trouxe_biblia': bool(
                frequencias_por_aluno.get(aluno.id)
                and frequencias_por_aluno[aluno.id].trouxe_biblia
            ),
            'trouxe_revista': bool(
                frequencias_por_aluno.get(aluno.id)
                and frequencias_por_aluno[aluno.id].trouxe_revista
            ),
            'trouxe_visitante': bool(
                frequencias_por_aluno.get(aluno.id)
                and frequencias_por_aluno[aluno.id].trouxe_visitante
            ),
            'trouxe_oferta': bool(
                frequencias_por_aluno.get(aluno.id)
                and frequencias_por_aluno[aluno.id].trouxe_oferta
            ),
        }
        for aluno in alunos
    ]
    return formset_class(initial=inicial)


def persistir_chamada(*, formset, turma, data, classe, pontos_cfg, valor_oferta):
    """Grava frequencias e oferta como uma unica operacao atomica."""
    pontos_totais_aula = 0
    valor_oferta_registrada = None

    with transaction.atomic():
        for form in formset:
            aluno_id = form.cleaned_data['aluno_id']
            presente = form.cleaned_data.get('presente', False)
            trouxe_biblia = form.cleaned_data.get('trouxe_biblia', False)
            trouxe_revista = form.cleaned_data.get('trouxe_revista', False)
            trouxe_visitante = form.cleaned_data.get('trouxe_visitante', False)
            trouxe_oferta = form.cleaned_data.get('trouxe_oferta', False)
            pontos_total = calcular_pontos_frequencia_flags(
                presente=presente,
                trouxe_biblia=trouxe_biblia,
                trouxe_revista=trouxe_revista,
                trouxe_oferta=trouxe_oferta,
                trouxe_visitante=trouxe_visitante,
                pontos_cfg=pontos_cfg,
            )
            Frequencia.objects.update_or_create(
                aluno_id=aluno_id,
                data=data,
                defaults={
                    'presente': presente,
                    'trouxe_biblia': trouxe_biblia,
                    'trouxe_revista': trouxe_revista,
                    'trouxe_visitante': trouxe_visitante,
                    'trouxe_oferta': trouxe_oferta,
                    'pontos_total': pontos_total,
                },
            )
            pontos_totais_aula += pontos_total

        if valor_oferta is not None and classe:
            valor_str = str(valor_oferta).replace(',', '.').strip()
            try:
                valor_oferta_registrada = Decimal(valor_str) if valor_str else Decimal('0')
            except InvalidOperation as exc:
                raise ValorOfertaInvalido('Informe um valor de oferta valido.') from exc
            oferta_obj = OfertaClasse.objects.select_for_update().filter(
                turma=turma,
                data=data,
            ).first()
            if oferta_obj:
                oferta_obj.valor = valor_oferta_registrada
                oferta_obj.save(update_fields=['valor'])
            else:
                OfertaClasse.objects.create(
                    turma=turma,
                    classe=classe,
                    data=data,
                    valor=valor_oferta_registrada,
                )

    return pontos_totais_aula, valor_oferta_registrada


def preparar_calendario_chamada(*, turma, tipo_periodo, dia_ebd, hoje, data_solicitada=None):
    """Monta o calendario e a licao selecionada para a chamada da turma."""
    periodos_qs = PeriodoEBD.objects.filter(
        ano_letivo=turma.ano_letivo,
        tipo=tipo_periodo,
    ).order_by('data_inicio')
    periodo = periodos_qs.filter(data_inicio__lte=hoje, data_fim__gte=hoje).first()
    if periodo is None:
        periodo = periodos_qs.filter(data_inicio__gte=hoje).first() or periodos_qs.last()

    datas_esperadas = []
    licoes_qs = Licao.objects.none()
    if periodo is not None:
        from .utils import gerar_datas_semana_periodo

        datas_esperadas = gerar_datas_semana_periodo(
            periodo.data_inicio,
            periodo.data_fim,
            dia_semana=dia_ebd,
        )
        licoes_qs = Licao.objects.filter(
            turma=turma,
            data__gte=periodo.data_inicio,
            data__lte=periodo.data_fim,
        ).select_related('professor').order_by('data', 'id')

    datas_com_licao = []
    licao_por_data = {}
    for licao in licoes_qs:
        if licao.data not in licao_por_data:
            licao_por_data[licao.data] = licao
            datas_com_licao.append(licao.data)

    datas_validas = set(datas_com_licao)
    data_selecionada = data_solicitada
    if data_selecionada not in datas_validas:
        if hoje in datas_validas:
            data_selecionada = hoje
        else:
            datas_passadas = [data for data in datas_com_licao if data <= hoje]
            data_selecionada = (
                max(datas_passadas)
                if datas_passadas
                else (datas_com_licao[0] if datas_com_licao else None)
            )

    opcoes_aula = []
    for indice, data in enumerate(datas_com_licao, start=1):
        licao = licao_por_data[data]
        status = 'hoje' if data == hoje else ('passada' if data < hoje else 'futura')
        opcoes_aula.append({
            'value': data.isoformat(),
            'label': f'{indice}ª aula - {data.strftime("%d/%m/%Y")}',
            'tema': getattr(licao, 'tema', ''),
            'status': status,
        })

    if data_selecionada is None:
        status_aula_selecionada = None
    elif data_selecionada == hoje:
        status_aula_selecionada = 'hoje'
    elif data_selecionada < hoje:
        status_aula_selecionada = 'passada'
    else:
        status_aula_selecionada = 'futura'

    return {
        'periodo': periodo,
        'datas_com_licao': datas_com_licao,
        'licoes_faltantes': [data for data in datas_esperadas if data not in licao_por_data],
        'data_selecionada': data_selecionada,
        'licao_do_dia': licao_por_data.get(data_selecionada),
        'opcoes_aula': opcoes_aula,
        'status_aula_selecionada': status_aula_selecionada,
    }


def preparar_contexto_exibicao_chamada(
    *, calendario, oferta_atual=None, bloqueio_chamada_msg=None,
):
    """Consolida os valores exibidos no formulario de chamada."""
    periodo = calendario['periodo']
    data_selecionada = calendario['data_selecionada']
    valor_oferta_atual = ''
    if oferta_atual is not None and oferta_atual.valor is not None:
        valor_oferta_atual = f'{oferta_atual.valor:.2f}'

    periodo_label = ''
    if periodo is not None:
        periodo_label = (
            f'{periodo.get_tipo_display()} {periodo.numero} '
            f'({periodo.data_inicio.strftime("%d/%m/%Y")} - '
            f'{periodo.data_fim.strftime("%d/%m/%Y")})'
        )

    return {
        'data': data_selecionada.isoformat() if data_selecionada else '',
        'datas_validas': calendario['datas_com_licao'],
        'opcoes_aula': calendario['opcoes_aula'],
        'periodo': periodo,
        'periodo_label': periodo_label,
        'valor_oferta_atual': valor_oferta_atual,
        'licao_do_dia': calendario['licao_do_dia'],
        'bloqueio_chamada_msg': bloqueio_chamada_msg,
        'status_aula_selecionada': calendario['status_aula_selecionada'],
    }
