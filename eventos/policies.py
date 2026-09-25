"""Policies explícitas para ações sensíveis do módulo de Eventos."""

from contas.constants import ADMIN_MINISTERIO, PASTOR_LOCAL, user_tem_grupo


def can_close_event_financial_period(user, igreja):
    """Retorna se ``user`` pode fechar o período financeiro de ``igreja``.

    Esta regra é intencionalmente independente do acesso ao módulo Eventos e
    não usa a hierarquia genérica de grupos. Na ausência de contexto completo,
    nega a operação.
    """
    if not getattr(user, 'is_authenticated', False) or igreja is None:
        return False

    try:
        perfil = user.perfil
    except Exception:
        return False

    if perfil.ministerio_id != igreja.ministerio_id:
        return False

    igrejas_permitidas = perfil.igrejas_permitidas
    igreja_foi_explicitamente_permitida = igrejas_permitidas.filter(pk=igreja.pk).exists()

    if user_tem_grupo(user, PASTOR_LOCAL):
        return igreja_foi_explicitamente_permitida

    if user_tem_grupo(user, ADMIN_MINISTERIO):
        if igreja.tipo_igreja not in ('sede', 'independente'):
            return False
        return not igrejas_permitidas.exists() or igreja_foi_explicitamente_permitida

    return False