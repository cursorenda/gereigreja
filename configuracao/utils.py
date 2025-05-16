# c:\Gereigreja\configuracao\utils.py
from django.contrib.auth.models import Group

def pode_editar_configuracao_org(user):
    """
    Verifica se o usuário tem permissão para editar configurações da organização.
    Exemplo: Ser do grupo 'Admin Organizacao'.
    """
    if not user.is_authenticated:
        return False
    # Verifica se o usuário pertence ao grupo 'Admin Organizacao'
    # Você pode adicionar outras lógicas de permissão aqui, se necessário
    # Por exemplo, verificar se é superusuário ou tem uma permissão específica.
    return user.groups.filter(name='Admin Organizacao').exists()

# Você pode adicionar outras funções de utilidade específicas do app configuracao aqui.
