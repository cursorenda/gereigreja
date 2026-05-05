from contas.constants import (
    ADMIN_MINISTERIO,
    EQUIPE_RECEPCAO,
    LIDERANCA_SECRETARIA,
    MEMBRO_COMUM,
    PASTOR_LOCAL,
    PASTOR_REGIONAL,
    PROFESSOR_EBD,
    SECRETARIA_EBD,
    SECRETARIO_LOCAL,
    SUPERINTENDENTE_EBD,
    TESOUREIRO,
    user_has_permission_level_or_higher,
    user_is_lideranca_financeira,
    user_is_lideranca_secretaria,
    user_pode_enviar_comunicacao_massa,
    user_pode_gerenciar_comunicacao,
    user_pode_gerenciar_cargos,
    user_pode_gerenciar_eventos,
    user_pode_gerenciar_secretaria,
    user_pode_ver_financeiro,
    user_tem_grupo,
    user_tem_qualquer_grupo,
)
from configuracao.services_assinatura import usuario_pode_usar_modulo


def _is_authenticated(user):
    return bool(getattr(user, 'is_authenticated', False))


def _can_view_internal_menu(user):
    return _is_authenticated(user) and not user_tem_grupo(user, MEMBRO_COMUM)


def _can_manage_reception(user):
    from configuracao.models import Ministerio

    return user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        SECRETARIO_LOCAL,
        EQUIPE_RECEPCAO,
    ]) or Ministerio.objects.filter(administrador_principal=user).exists()


def _is_active_ebd_professor(user):
    membro = getattr(user, 'membro_secretaria', None)
    if not membro:
        return False

    from secretaria.models import MembroCargo

    return MembroCargo.objects.filter(
        membro=membro,
        cargo__is_ebd=True,
        cargo__nome__icontains='professor',
        data_fim__isnull=True,
    ).exists()


PAGE_ACCESS_RULES = {
    'menu_interno': _can_view_internal_menu,
    'dashboard_secretaria': lambda user: user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        LIDERANCA_SECRETARIA,
        PASTOR_REGIONAL,
        PASTOR_LOCAL,
        SECRETARIO_LOCAL,
    ]) and usuario_pode_usar_modulo(user, 'secretaria'),
    'secretaria_pessoas': lambda user: user_pode_gerenciar_secretaria(user) and usuario_pode_usar_modulo(user, 'secretaria'),
    'secretaria_transferencias': lambda user: user_pode_gerenciar_secretaria(user) and usuario_pode_usar_modulo(user, 'secretaria'),
    'secretaria_cargos': lambda user: user_pode_gerenciar_cargos(user) and usuario_pode_usar_modulo(user, 'secretaria'),
    'secretaria_grupos_casa': lambda user: user_pode_gerenciar_secretaria(user) and usuario_pode_usar_modulo(user, 'secretaria'),
    'secretaria_acompanhamentos': lambda user: user_pode_gerenciar_secretaria(user) and usuario_pode_usar_modulo(user, 'secretaria'),
    'secretaria_tags': lambda user: user_pode_gerenciar_secretaria(user) and usuario_pode_usar_modulo(user, 'secretaria'),
    'secretaria_relatorios': lambda user: user_pode_gerenciar_secretaria(user) and usuario_pode_usar_modulo(user, 'secretaria'),
    'recepcao_visitantes': _can_manage_reception,
    'agenda': lambda user: user_pode_gerenciar_eventos(user) and usuario_pode_usar_modulo(user, 'agenda'),
    'eventos': lambda user: user_pode_gerenciar_eventos(user) and usuario_pode_usar_modulo(user, 'eventos'),
    'escola_biblica': lambda user: user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        PASTOR_LOCAL,
        SECRETARIA_EBD,
        SUPERINTENDENTE_EBD,
    ]) and usuario_pode_usar_modulo(user, 'escola_biblica'),
    'escola_biblica_professor': lambda user: (
        user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        PASTOR_LOCAL,
        SECRETARIA_EBD,
        SUPERINTENDENTE_EBD,
        PROFESSOR_EBD,
        ]) or _is_active_ebd_professor(user)
    ) and usuario_pode_usar_modulo(user, 'escola_biblica'),
    'financeiro': lambda user: user_pode_ver_financeiro(user) and usuario_pode_usar_modulo(user, 'financeiro'),
    'lideranca_secretaria': user_is_lideranca_secretaria,
    'lideranca_financeira': user_is_lideranca_financeira,
    'comunicacao': lambda user: user_pode_gerenciar_comunicacao(user) and usuario_pode_usar_modulo(user, 'comunicacao'),
    'comunicacao_massa': lambda user: user_pode_enviar_comunicacao_massa(user) and usuario_pode_usar_modulo(user, 'comunicacao'),
    'mural_avisos': _is_authenticated,
    'suporte': _can_view_internal_menu,
    'novidades_sistema': _is_authenticated,
    'configuracoes_sistema': lambda user: user_tem_grupo(user, ADMIN_MINISTERIO),
}


def user_can_access_page(user, page_key):
    rule = PAGE_ACCESS_RULES.get(page_key)
    if rule is None:
        return False
    return bool(rule(user))


def user_can_access_any(user, *page_keys):
    return any(user_can_access_page(user, page_key) for page_key in page_keys)