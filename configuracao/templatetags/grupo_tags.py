from django import template
from contas.constants import (
    ADMIN_MINISTERIO,
    GRUPOS_TODOS,
    HIERARQUIA_GRUPOS,
    MEMBRO_COMUM,
)

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    from contas.constants import user_tem_grupo
    return user_tem_grupo(user, group_name)


@register.simple_tag
def user_is_admin_ministerio(user):
    """Verifica se o usuário é Admin Ministerio"""
    if not user.is_authenticated:
        return False
    from contas.constants import user_tem_grupo
    return user.is_superuser or user_tem_grupo(user, ADMIN_MINISTERIO)


_ROTULOS_ATUACAO = {
    ADMIN_MINISTERIO: 'Administrador do Ministério',
    'Secretaria Ministerial': 'Secretaria Ministerial',
    'Tesouraria Ministerial': 'Tesouraria Ministerial',
    'Pastor Regional': 'Pastor Regional',
    'Pastor Local': 'Pastor Local',
    'Secretario Local': 'Secretário Local',
    'Tesoureiro': 'Tesoureiro Local',
    'Superintendente EBD': 'Superintendente EBD',
    'Equipe de Eventos': 'Equipe de Eventos',
    'Equipe de Mídia': 'Equipe de Mídia',
    'Equipe de Recepção': 'Equipe de Recepção',
    'Professores EBD': 'Professor EBD',
    'Secretaria EBD': 'Secretaria EBD',
    MEMBRO_COMUM: 'Membro',
}


def _usuario_e_presidente_ministerial(user):
    """Identifica o administrador principal sem depender da exibição do menu."""
    try:
        perfil = user.perfil
        return bool(perfil.ministerio_id and perfil.ministerio.administrador_principal_id == user.id)
    except Exception:
        return False


@register.simple_tag
def resumo_atuacao_usuario(user):
    """Resumo visual de atuação; não participa de nenhuma decisão de autorização."""
    vazio = {'principal': '', 'adicionais': 0, 'titulo': '', 'atuacoes': []}
    if not getattr(user, 'is_authenticated', False):
        return vazio

    if user.is_superuser:
        return {
            'principal': 'Administrador do Sistema',
            'adicionais': 0,
            'titulo': 'Atuação: Administrador do Sistema',
            'atuacoes': ['Administrador do Sistema'],
        }

    grupos_ativos = set(user.groups.values_list('name', flat=True)) & set(GRUPOS_TODOS)
    if len(grupos_ativos) > 1:
        grupos_ativos.discard(MEMBRO_COMUM)
    if not grupos_ativos:
        return vazio

    grupos_ordenados = sorted(
        grupos_ativos,
        key=lambda grupo: (HIERARQUIA_GRUPOS.get(grupo, 99), _ROTULOS_ATUACAO[grupo]),
    )
    rotulos = [_ROTULOS_ATUACAO[grupo] for grupo in grupos_ordenados]
    if grupos_ordenados[0] == ADMIN_MINISTERIO and _usuario_e_presidente_ministerial(user):
        rotulos[0] = 'Presidente do Ministério'

    return {
        'principal': rotulos[0],
        'adicionais': len(rotulos) - 1,
        'titulo': 'Atuações: ' + ', '.join(rotulos),
        'atuacoes': rotulos,
    }
