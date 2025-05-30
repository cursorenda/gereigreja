# c:\Gereigreja\secretaria\utils.py
from django.contrib.auth.models import User, Group
from configuracao.models import Igreja, PerfilUsuario # Importar PerfilUsuario e Igreja
from django.db.models import Q # Importar Q para consultas complexas

# --- Funções de Verificação de Grupo (Reutilizáveis) ---

def _user_in_group(user, group_name):
    """Verifica se o usuário pertence a um grupo específico."""
    if not user.is_authenticated:
        return False
    # Otimização: Verificar se o usuário já tem os grupos pré-carregados
    if hasattr(user, '_prefetched_objects_cache') and 'groups' in user._prefetched_objects_cache:
        return any(group.name == group_name for group in user.groups.all())
    # Fallback: Consultar o banco de dados
    return user.groups.filter(name=group_name).exists()

def is_admin_org(user):
    """Verifica se o usuário é Admin da Organização."""
    return _user_in_group(user, 'Admin Organizacao')

def is_secretario(user):
    """Verifica se o usuário é Secretário."""
    return _user_in_group(user, 'Secretario')

def is_lider_igreja(user):
    """Verifica se o usuário é Lider Igreja."""
    return _user_in_group(user, 'Lider Igreja')

def is_tesoureiro(user):
    """Verifica se o usuário é Tesoureiro."""
    return _user_in_group(user, 'Tesoureiro')


# Nova função para líder da secretaria
def is_secretaria_leader(user):
    """ Verifica se o usuário é Admin da Organização ou pertence ao grupo 'Lideranca Secretaria'. """
    if is_admin_org(user): # Admin da Org também é considerado líder da secretaria
        return True
    return _user_in_group(user, 'Lideranca Secretaria')

# --- Funções de Verificação de Permissão para secretaria de Membros ---

def has_membro_view_permission(user):
    """Verifica se o usuário tem permissão para VER dados de membros.""" # Adicionado is_secretaria_leader
    return is_admin_org(user) or is_secretario(user) or is_lider_igreja(user) or is_tesoureiro(user) or is_secretaria_leader(user)

def has_membro_edit_permission(user):
    """Verifica se o usuário tem permissão para EDITAR/ADICIONAR/INATIVAR dados de membros."""
    return is_admin_org(user) or is_secretario(user)

# --- Função para Obter Igrejas Permitidas para secretaria de Membros ---

def get_allowed_churches_for_membros(user, organizacao_param=None): # Adicionado organizacao_param
    # ... lógica existente ...
    # Agora você pode usar 'organizacao_param' dentro da função se necessário
    # Por exemplo, para filtrar igrejas pela organização do líder.
    # Se a lógica já usa user.perfil.organizacao, pode não precisar de grandes mudanças internas,
    # mas a assinatura da função precisa aceitar o argumento.
    """
    Retorna um QuerySet das Igrejas que o usuário tem permissão para acessar no contexto de membros.
    - Admin Org ou Líder Secretaria: Todas as igrejas da organização ou as permitidas no perfil + subordinadas.
    - Secretário, Líder Igreja, Tesoureiro (não líderes): Igrejas associadas no PerfilUsuario.
    - Outros: Nenhuma igreja.
    - Retorna QuerySet vazio se o usuário não tiver perfil/organização ou permissão de visualização.
    """
    if not user.is_authenticated or not hasattr(user, 'perfil') or not user.perfil.organizacao:
        return Igreja.objects.none()

    # Verifica se o usuário tem PELO MENOS permissão de visualização de membros
    if not has_membro_view_permission(user):
        return Igreja.objects.none()

    organizacao = user.perfil.organizacao

    # Se o usuário é Admin da Organização ou Líder da Secretaria, expandir permissões
    if is_secretaria_leader(user):
        igrejas_base_permitidas = user.perfil.igrejas_permitidas.filter(organizacao=organizacao)

        
        # Se for Admin da Org e não tiver igrejas específicas no perfil, vê todas da organização
        if is_admin_org(user) and not igrejas_base_permitidas.exists():
            return Igreja.objects.filter(organizacao=organizacao)

        todas_igrejas_permitidas_ids = set()

        def get_subordinadas_recursivamente(igreja_obj):
            sub_ids = set()
            sub_ids.add(igreja_obj.pk) # Adiciona a própria igreja
            # Busca subordinadas que pertencem à mesma organização (segurança)
            # Assumindo que o related_name no modelo Igreja para igreja_superior é 'igrejas_subordinadas'
            for sub_igreja in igreja_obj.igrejas_subordinadas.filter(organizacao=organizacao):
                sub_ids.update(get_subordinadas_recursivamente(sub_igreja))
            return sub_ids

        for igreja_permitida in igrejas_base_permitidas:
            todas_igrejas_permitidas_ids.update(get_subordinadas_recursivamente(igreja_permitida))
            
        if todas_igrejas_permitidas_ids:
            return Igreja.objects.filter(pk__in=list(todas_igrejas_permitidas_ids), organizacao=organizacao)
        else:
            # Se o líder não tem igrejas no perfil ou elas não existem na organização, retorna vazio.
            return Igreja.objects.none()



    elif is_secretario(user) or is_lider_igreja(user) or is_tesoureiro(user):
        # Secretário, Líder e Tesoureiro têm acesso às igrejas explicitamente permitidas no perfil
        # Garante que as igrejas retornadas pertencem à organização do usuário (segurança extra)
        return user.perfil.igrejas_permitidas.filter(organizacao=organizacao)
    else:
        # Por segurança, retorna vazio.
        return Igreja.objects.none()