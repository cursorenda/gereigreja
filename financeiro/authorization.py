"""Políticas de escopo local para operações financeiras."""

from configuracao.models import Igreja


FORMAL_PAYABLE_DECISION_PERMISSION = 'financeiro.approve_contapagar'


def _get_explicit_finance_scope(user, ministerio):
    """Retorna somente igrejas explicitamente autorizadas no perfil do usuário."""
    if not getattr(user, 'is_authenticated', False) or not getattr(ministerio, 'pk', None):
        return Igreja.objects.none()

    perfil = getattr(user, 'perfil', None)
    if not perfil or perfil.ministerio_id != ministerio.pk:
        return Igreja.objects.none()

    return perfil.igrejas_permitidas.filter(ministerio_id=ministerio.pk)


def get_finance_read_scope(user, ministerio):
    """Retorna o escopo local explícito de leitura financeira do usuário."""
    return _get_explicit_finance_scope(user, ministerio)


def get_finance_write_scope(user, ministerio):
    """Retorna o escopo local explícito de escrita financeira do usuário."""
    return _get_explicit_finance_scope(user, ministerio)


def can_approve_payable(user):
    """Retorna se o usuário possui a capability formal de decisão de contas a pagar."""
    return bool(
        user
        and getattr(user, 'is_authenticated', False)
        and user.has_perm(FORMAL_PAYABLE_DECISION_PERMISSION)
    )


def get_finance_approval_scope(user, ministerio):
    """Retorna o escopo local explícito para decisões formais de contas a pagar."""
    return _get_explicit_finance_scope(user, ministerio)
