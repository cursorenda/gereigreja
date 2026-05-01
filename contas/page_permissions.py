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
    ]),
    'secretaria_pessoas': user_pode_gerenciar_secretaria,
    'secretaria_transferencias': user_pode_gerenciar_secretaria,
    'secretaria_cargos': user_pode_gerenciar_cargos,
    'secretaria_grupos_casa': user_pode_gerenciar_secretaria,
    'secretaria_acompanhamentos': user_pode_gerenciar_secretaria,
    'secretaria_tags': user_pode_gerenciar_secretaria,
    'secretaria_relatorios': user_pode_gerenciar_secretaria,
    'recepcao_visitantes': _can_manage_reception,
    'agenda': user_pode_gerenciar_eventos,
    'eventos': user_pode_gerenciar_eventos,
    'escola_biblica': lambda user: user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        PASTOR_LOCAL,
        SECRETARIA_EBD,
        SUPERINTENDENTE_EBD,
    ]),
    'escola_biblica_professor': lambda user: user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        PASTOR_LOCAL,
        SECRETARIA_EBD,
        SUPERINTENDENTE_EBD,
        PROFESSOR_EBD,
    ]) or _is_active_ebd_professor(user),
    'financeiro': user_pode_ver_financeiro,
    'lideranca_secretaria': user_is_lideranca_secretaria,
    'lideranca_financeira': user_is_lideranca_financeira,
    'comunicacao': user_pode_gerenciar_comunicacao,
    'comunicacao_massa': user_pode_enviar_comunicacao_massa,
    'mural_avisos': _is_authenticated,
    'suporte': _can_view_internal_menu,
    'dashboard_sistema': lambda user: user_tem_grupo(user, ADMIN_MINISTERIO),
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