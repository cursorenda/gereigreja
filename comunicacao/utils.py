# c:\Gereigreja\comunicacao\utils.py
from configuracao.models import PerfilUsuario
from contas.constants import user_pode_gerenciar_comunicacao

def can_manage_avisos(user):
    """
    Verifica se o usuário pode gerenciar (criar, editar, excluir) avisos.
    """
    if not user.is_authenticated:
        return False
    return user_pode_gerenciar_comunicacao(user)

def can_view_avisos(user):
    """
    Verifica se o usuário pode visualizar avisos.
    Por padrão, todos os usuários autenticados do ministério podem ver.
    """
    if not user.is_authenticated:
        return False
    # Todos os usuários autenticados com perfil e ministério podem ver
    return hasattr(user, 'perfil') and user.perfil and user.perfil.ministerio is not None

