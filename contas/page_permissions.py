import inspect

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


def _normalizar_tipo_igreja(tipo_igreja):
    """Normaliza códigos/tipos de igreja para validação de acesso."""
    if not tipo_igreja:
        return None

    valor = str(tipo_igreja).strip().lower()
    mapa = {
        's': 'sede',
        'd': 'independente',
        'r': 'regional',
        'c': 'congregacao',
    }
    return mapa.get(valor, valor)


def _resolver_igreja_contexto(request=None, igreja=None):
    if igreja is not None:
        return igreja
    if request is not None:
        return getattr(request, 'igreja_ativa', None)
    return None


def pode_acessar_secretaria(user, request=None, igreja=None):
    """
    Regra central de acesso à Secretaria.

    Segurança:
    - Secretário Local sempre acessa.
    - Admin/Presidente acessa somente em contexto de igreja Sede/Independente.
    - Admin/Presidente não acessa em Regional/Congregação.
    - Demais usuários não acessam.
    """
    if not _is_authenticated(user):
        return False

    if user_tem_grupo(user, SECRETARIO_LOCAL):
        return True

    if not user_tem_grupo(user, ADMIN_MINISTERIO):
        return False

    igreja_contexto = _resolver_igreja_contexto(request=request, igreja=igreja)
    tipo_normalizado = _normalizar_tipo_igreja(getattr(igreja_contexto, 'tipo_igreja', None))
    return tipo_normalizado in {'sede', 'independente'}


def _is_authenticated(user):
    return bool(getattr(user, 'is_authenticated', False))


def _can_view_internal_menu(user):
    return _is_authenticated(user) and not user_tem_grupo(user, MEMBRO_COMUM)


def _can_manage_reception(user):
    return pode_acessar_secretaria(user)


def _can_manage_secretaria_base(user):
    """Base única para telas da Secretaria com regra por perfil+tipo de igreja."""
    return pode_acessar_secretaria(user)


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
    'dashboard_secretaria': lambda user, **ctx: pode_acessar_secretaria(user, request=ctx.get('request'), igreja=ctx.get('igreja')) and usuario_pode_usar_modulo(user, 'secretaria'),
    'secretaria_pessoas': lambda user, **ctx: pode_acessar_secretaria(user, request=ctx.get('request'), igreja=ctx.get('igreja')) and usuario_pode_usar_modulo(user, 'secretaria'),
    'secretaria_transferencias': lambda user, **ctx: pode_acessar_secretaria(user, request=ctx.get('request'), igreja=ctx.get('igreja')) and usuario_pode_usar_modulo(user, 'secretaria'),
    'secretaria_cargos': lambda user, **ctx: pode_acessar_secretaria(user, request=ctx.get('request'), igreja=ctx.get('igreja')) and usuario_pode_usar_modulo(user, 'secretaria'),
    'secretaria_grupos_casa': lambda user, **ctx: pode_acessar_secretaria(user, request=ctx.get('request'), igreja=ctx.get('igreja')) and usuario_pode_usar_modulo(user, 'secretaria'),
    'secretaria_acompanhamentos': lambda user, **ctx: pode_acessar_secretaria(user, request=ctx.get('request'), igreja=ctx.get('igreja')) and usuario_pode_usar_modulo(user, 'secretaria'),
    'secretaria_tags': lambda user, **ctx: pode_acessar_secretaria(user, request=ctx.get('request'), igreja=ctx.get('igreja')) and usuario_pode_usar_modulo(user, 'secretaria'),
    'secretaria_relatorios': lambda user, **ctx: pode_acessar_secretaria(user, request=ctx.get('request'), igreja=ctx.get('igreja')) and usuario_pode_usar_modulo(user, 'secretaria'),
    'recepcao_visitantes': lambda user, **ctx: pode_acessar_secretaria(user, request=ctx.get('request'), igreja=ctx.get('igreja')) and usuario_pode_usar_modulo(user, 'secretaria'),
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
    'financeiro': lambda user: user_tem_qualquer_grupo(user, [
        PASTOR_LOCAL,
        TESOUREIRO,
    ]) and usuario_pode_usar_modulo(user, 'financeiro'),
    'lideranca_secretaria': user_is_lideranca_secretaria,
    'lideranca_financeira': user_is_lideranca_financeira,
    'comunicacao': lambda user: user_pode_gerenciar_comunicacao(user) and usuario_pode_usar_modulo(user, 'comunicacao'),
    'comunicacao_massa': lambda user: user_pode_enviar_comunicacao_massa(user) and usuario_pode_usar_modulo(user, 'comunicacao'),
    'mural_avisos': _is_authenticated,
    'suporte': _can_view_internal_menu,
    'novidades_sistema': _is_authenticated,
    'configuracoes_sistema': lambda user: user_tem_grupo(user, ADMIN_MINISTERIO),
}


def user_can_access_page(user, page_key, request=None, igreja=None):
    rule = PAGE_ACCESS_RULES.get(page_key)
    if rule is None:
        return False

    signature = inspect.signature(rule)
    params = signature.parameters
    aceita_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())

    if aceita_kwargs or 'request' in params or 'igreja' in params:
        kwargs = {}
        if aceita_kwargs or 'request' in params:
            kwargs['request'] = request
        if aceita_kwargs or 'igreja' in params:
            kwargs['igreja'] = igreja
        return bool(rule(user, **kwargs))

    return bool(rule(user))


def user_can_access_any(user, *page_keys, request=None, igreja=None):
    return any(user_can_access_page(user, page_key, request=request, igreja=igreja) for page_key in page_keys)