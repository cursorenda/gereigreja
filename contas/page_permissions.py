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
    Regra central de operação local da Secretaria.

    Distinções:
    - Liderança ministerial/regional usa painéis próprios de supervisão
      (`lideranca_secretaria`) e não recebe operação local automática.
    - Perfis locais usam exclusivamente as igrejas explicitamente vinculadas
      em `PerfilUsuario.igrejas_permitidas`, sem expansão hierárquica.
    - Admin Ministério segue política própria: igreja concreta selecionável,
      limitada a Sede ou Independente.
    """
    if not _is_authenticated(user):
        return False

    igreja_contexto = _resolver_igreja_contexto(request=request, igreja=igreja)
    local_access = False

    if user_tem_grupo(user, SECRETARIO_LOCAL) or user_tem_grupo(user, PASTOR_LOCAL):
        perfil = getattr(user, 'perfil', None) or getattr(user, 'perfil_usuario', None)
        if perfil and perfil.ministerio:
            igrejas_autorizadas = perfil.igrejas_permitidas.filter(
                ministerio=perfil.ministerio,
            )
            if igreja_contexto is None:
                local_access = igrejas_autorizadas.exists()
            else:
                local_access = igrejas_autorizadas.filter(pk=igreja_contexto.pk).exists()

    admin_access = False
    if user_tem_grupo(user, ADMIN_MINISTERIO) and igreja_contexto is not None:
        tipo_normalizado = _normalizar_tipo_igreja(getattr(igreja_contexto, 'tipo_igreja', None))
        if tipo_normalizado in {'sede', 'independente'}:
            from core.utils import get_igrejas_selecionaveis

            igrejas_autorizadas = get_igrejas_selecionaveis(user)
            admin_access = igrejas_autorizadas.filter(pk=igreja_contexto.pk).exists()

    return local_access or admin_access


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


def pode_acessar_financeiro(user, request=None, igreja=None):
    """Regra de entrada no modulo Financeiro.

    Pastor Local e Tesoureiro: preservam comportamento atual.
    Admin Ministerio: permitido somente quando a igreja ativa for Sede ou Independente
    e estiver dentro do escopo canônico (get_igrejas_selecionaveis).

    A entrada no modulo NAO concede poderes internos de Tesoureiro.
    """
    if not user or not user.is_authenticated:
        return False

    if not usuario_pode_usar_modulo(user, 'financeiro'):
        return False

    igreja_contexto = igreja
    if igreja_contexto is None and request is not None:
        igreja_contexto = getattr(request, 'igreja_ativa', None)

    papel_local_financeiro = user_tem_qualquer_grupo(user, [PASTOR_LOCAL, TESOUREIRO])
    if igreja_contexto is None:
        return papel_local_financeiro

    from core.utils import get_igrejas_selecionaveis

    igrejas_autorizadas = get_igrejas_selecionaveis(
        user,
        ministerio=igreja_contexto.ministerio,
    )
    if not igrejas_autorizadas.filter(pk=igreja_contexto.pk).exists():
        return False

    if papel_local_financeiro:
        return True

    if not user_tem_grupo(user, ADMIN_MINISTERIO):
        return False

    tipo_normalizado = _normalizar_tipo_igreja(getattr(igreja_contexto, 'tipo_igreja', None))
    return tipo_normalizado in {'sede', 'independente'}


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
    'financeiro': lambda user, **ctx: pode_acessar_financeiro(user, request=ctx.get('request'), igreja=ctx.get('igreja')),
    'lideranca_secretaria': user_is_lideranca_secretaria,
    'lideranca_financeira': user_is_lideranca_financeira,
    'comunicacao': lambda user: user_pode_gerenciar_comunicacao(user) and usuario_pode_usar_modulo(user, 'comunicacao'),
    'comunicacao_massa': lambda user: user_pode_enviar_comunicacao_massa(user) and usuario_pode_usar_modulo(user, 'comunicacao'),
    'mural_avisos': _is_authenticated,
    'suporte': _can_view_internal_menu,
    'novidades_sistema': _is_authenticated,
    'configuracoes_sistema': lambda user: user_tem_grupo(user, ADMIN_MINISTERIO),
}


PAGE_ACCESS_RULES_WITH_CONTEXT = frozenset({
    'dashboard_secretaria',
    'secretaria_pessoas',
    'secretaria_transferencias',
    'secretaria_cargos',
    'secretaria_grupos_casa',
    'secretaria_acompanhamentos',
    'secretaria_tags',
    'secretaria_relatorios',
    'recepcao_visitantes',
    'financeiro',
})


def user_can_access_page(user, page_key, request=None, igreja=None):
    rule = PAGE_ACCESS_RULES.get(page_key)
    if rule is None:
        return False

    if page_key in PAGE_ACCESS_RULES_WITH_CONTEXT:
        return bool(
            rule(
                user,
                request=request,
                igreja=igreja,
            )
        )

    return bool(rule(user))


def user_can_access_any(user, *page_keys, request=None, igreja=None):
    return any(user_can_access_page(user, page_key, request=request, igreja=igreja) for page_key in page_keys)
