"""Resolução das configurações da Escola Bíblica por escopo."""

from configuracao.models import ConfiguracaoSistema


PONTOS_EBD_PADRAO = {
    'presente': 10,
    'biblia': 2,
    'revista': 2,
    'oferta': 3,
    'visitante': 5,
}


def obter_configuracao_ministerio_ebd(request):
    perfil = getattr(request.user, 'perfil', None) or getattr(request.user, 'perfil_usuario', None)
    ministerio = getattr(perfil, 'ministerio', None)
    if not ministerio:
        return None
    return ConfiguracaoSistema.objects.filter(ministerio=ministerio).first()


def igreja_tem_override_ebd(igreja):
    return bool(
        igreja
        and (
            igreja.ebd_periodo
            or igreja.ebd_dia_semana is not None
            or igreja.ebd_horario is not None
        )
    )


def obter_igreja_configuracao_ebd(request, igrejas_escopo):
    if hasattr(request, '_ebd_igreja_config_cache'):
        return request._ebd_igreja_config_cache

    igreja_ativa = getattr(request, 'igreja_ativa', None)
    if igreja_ativa:
        request._ebd_igreja_config_cache = igreja_ativa
        return igreja_ativa

    if igrejas_escopo.count() == 1:
        request._ebd_igreja_config_cache = igrejas_escopo.first()
        return request._ebd_igreja_config_cache

    request._ebd_igreja_config_cache = None
    return None


def obter_configuracao_ebd(request, igreja):
    if hasattr(request, '_ebd_config_cache'):
        return request._ebd_config_cache

    if igreja_tem_override_ebd(igreja):
        request._ebd_config_cache = igreja
    else:
        request._ebd_config_cache = obter_configuracao_ministerio_ebd(request)
    return request._ebd_config_cache


def obter_configuracao_ebd_turma(turma):
    """Resolve a configuração EBD aplicável à turma, priorizando a igreja local."""
    igreja = getattr(turma, 'igreja', None)
    if igreja is None:
        classe = getattr(turma, 'classe', None)
        igreja = getattr(classe, 'igreja', None)

    if igreja_tem_override_ebd(igreja):
        return igreja
    if igreja is None or not getattr(igreja, 'ministerio_id', None):
        return None
    return ConfiguracaoSistema.objects.filter(ministerio_id=igreja.ministerio_id).first()


def obter_info_origem_configuracao_ebd(igreja):
    if igreja_tem_override_ebd(igreja):
        return {
            'ebd_config_source': 'igreja',
            'ebd_config_source_label': f'Origem: configuração local ({igreja.nome_igreja})',
            'ebd_config_source_hint': 'Período, dia e horário definidos na igreja em escopo.',
        }

    return {
        'ebd_config_source': 'ministerio',
        'ebd_config_source_label': 'Origem: configuração herdada do ministério',
        'ebd_config_source_hint': 'Sem override local nesta igreja. A EBD segue os parâmetros ministeriais.',
    }


def obter_tipo_periodo_ebd(configuracao):
    return configuracao.ebd_periodo if configuracao and configuracao.ebd_periodo else 'trimestre'


def obter_dia_semana_ebd(configuracao):
    return configuracao.ebd_dia_semana if configuracao and configuracao.ebd_dia_semana is not None else 6


def obter_horario_ebd_formatado(configuracao):
    """Retorna o horario da EBD no formato esperado pelos formularios."""
    horario = getattr(configuracao, 'ebd_horario', None)
    if not horario:
        return ''
    if isinstance(horario, str):
        return horario[:5]
    return horario.strftime('%H:%M')


def obter_pontos_ebd(configuracao):
    return {
        'presente': getattr(configuracao, 'ebd_pontos_presente', None) if configuracao else None,
        'biblia': getattr(configuracao, 'ebd_pontos_biblia', None) if configuracao else None,
        'revista': getattr(configuracao, 'ebd_pontos_revista', None) if configuracao else None,
        'oferta': getattr(configuracao, 'ebd_pontos_oferta', None) if configuracao else None,
        'visitante': getattr(configuracao, 'ebd_pontos_visitante', None) if configuracao else None,
    }


def aplicar_fallback_pontos_ebd(pontos):
    return {
        chave: PONTOS_EBD_PADRAO[chave] if valor is None else int(valor)
        for chave, valor in pontos.items()
    }
