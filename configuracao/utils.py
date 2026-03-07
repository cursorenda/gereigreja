# c:\Gereigreja\configuracao\utils.py
from django.contrib.auth.models import Group
from contas.constants import user_is_admin

def pode_editar_configuracao_org(user):
    """
    Verifica se o usuário tem permissão para editar configurações do ministério.
    Exemplo: Ser do grupo 'Admin Ministerio'.
    """
    if not user.is_authenticated:
        return False
    # Verifica se o usuário pertence ao grupo 'Admin Ministerio'
    # Você pode adicionar outras lógicas de permissão aqui, se necessário
    # Por exemplo, verificar se é superusuário ou tem uma permissão específica.
    return user_is_admin(user)

# Você pode adicionar outras funções de utilidade específicas do app configuracao aqui.
