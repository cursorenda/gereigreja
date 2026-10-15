"""Políticas de escopo local para operações financeiras."""

from configuracao.models import Igreja


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
