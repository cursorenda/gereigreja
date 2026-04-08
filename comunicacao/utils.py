# c:\Gereigreja\comunicacao\utils.py
from configuracao.models import PerfilUsuario
from contas.constants import ADMIN_MINISTERIO

def can_manage_avisos(user):
    """
    Verifica se o usuário pode gerenciar (criar, editar, excluir) avisos.
    Exemplo: Superusuários ou usuários com um papel específico na ministério.
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    
    # Verifica se o usuário tem um perfil e uma ministério associada
    if hasattr(user, 'perfil') and user.perfil and user.perfil.ministerio:
        # Permite se for staff (acesso ao admin) ou pertencer a grupos específicos
        # ou se for o administrador principal do ministério.
        is_admin_org = user.perfil.ministerio.administrador_principal == user
        try:
            from contas.constants import COMUNICACAO_MANAGER, user_has_permission_level_or_higher
            return user.is_staff or user_has_permission_level_or_higher(user, COMUNICACAO_MANAGER) or is_admin_org
        except ImportError:
            from contas.constants import user_has_permission_level_or_higher
            return user.is_staff or user_has_permission_level_or_higher(user, ADMIN_MINISTERIO) or is_admin_org
    return False

def can_view_avisos(user):
    """
    Verifica se o usuário pode visualizar avisos.
    Por padrão, todos os usuários autenticados do ministério podem ver.
    """
    if not user.is_authenticated:
        return False
    # Todos os usuários autenticados com perfil e ministério podem ver
    return hasattr(user, 'perfil') and user.perfil and user.perfil.ministerio is not None

