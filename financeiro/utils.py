# c:\Gereigreja\financeiro\utils.py
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, Group
from configuracao.models import Igreja, PerfilUsuario # Importar PerfilUsuario
from django.db.models import Q # Importar Q para consultas complexas



# --- Funções de Verificação de Grupo ---

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
    """Verifica se o usuário é Admin da Ministério."""
    return _user_in_group(user, 'Admin Ministerio')

def is_tesoureiro(user):
    """Verifica se o usuário é Tesoureiro."""
    # IMPORTANTE: Ajuste o nome do grupo se for diferente de 'Tesoureiro'
    return _user_in_group(user, 'Tesoureiro')

def is_lider_igreja(user):
    """Verifica se o usuário é Lider Igreja."""
    # IMPORTANTE: Ajuste o nome do grupo se for diferente de 'Lider Igreja'
    return _user_in_group(user, 'Lider Igreja')

# --- Funções de Verificação de Permissão Financeira ---

def has_finance_view_permission(user):
    """Verifica se o usuário tem permissão para VER dados financeiros."""
    return is_admin_org(user) or is_tesoureiro(user) or is_lider_igreja(user)

def has_finance_edit_permission(user):
    """Verifica se o usuário tem permissão para EDITAR/ADICIONAR/EXCLUIR dados financeiros."""
    # Lider Igreja NÃO tem permissão de edição por padrão aqui.
    return is_admin_org(user) or is_tesoureiro(user)


def is_finance_leader(user):
    """ Verifica se o usuário é Admin da Ministério ou pertence ao grupo 'Lideranca Financeira'. """
    if is_admin_org(user):
        return True
    # Verifica se o usuário pertence ao grupo 'Lideranca Financeira'
    return user.groups.filter(name='Lideranca Financeira').exists()


# --- Função para Obter Igrejas Permitidas ---

def get_allowed_churches_for_user(user):
    """
    Retorna um QuerySet das Igrejas que o usuário tem permissão para acessar financeiramente.
    - Admin Org: Todas as igrejas da ministério.
    - Tesoureiro, Líder: Igrejas associadas no PerfilUsuario.
    - Outros: Nenhuma igreja.
    - Retorna QuerySet vazio se o usuário não tiver perfil/ministério ou permissão de visualização.
    """
    if not user.is_authenticated or not hasattr(user, 'perfil') or not user.perfil.ministerio:
        return Igreja.objects.none() # Retorna queryset vazio por segurança

    # Verifica se o usuário tem PELO MENOS permissão de visualização financeira
    if not has_finance_view_permission(user):
        return Igreja.objects.none()

    ministerio = user.perfil.ministerio

    # Se o usuário é Admin da Ministério ou Líder Financeiro, expandir permissões
    if is_finance_leader(user):
        # Começa com as igrejas diretamente permitidas no perfil
        igrejas_base_permitidas = user.perfil.igrejas_permitidas.filter(ministerio=ministerio)
        
        # Se o usuário não tem nenhuma igreja explicitamente permitida, mas é líder,
        # e é Admin Org, ele vê TUDO. Se for apenas Líder Financeiro sem igrejas permitidas,
        # talvez a regra seja ver apenas as Sede/Regionais? Vamos assumir que Admin Org vê tudo
        # e Líder Financeiro vê as permitidas + subordinadas.
        if is_admin_org(user) and not igrejas_base_permitidas.exists():
             # Admin Org sem igrejas permitidas explicitamente vê todas da ministério
             return Igreja.objects.filter(ministerio=ministerio)

        # Coletar todas as igrejas permitidas, incluindo subordinadas recursivamente
        todas_igrejas_permitidas_ids = set()

        def get_subordinadas_recursivamente(igreja_obj):
            sub_ids = set()
            sub_ids.add(igreja_obj.pk) # Adiciona a própria igreja
            # Busca subordinadas que pertencem à mesma ministério (segurança)
            for sub_igreja in igreja_obj.igrejas_subordinadas.filter(ministerio=ministerio):
                sub_ids.update(get_subordinadas_recursivamente(sub_igreja))
            return sub_ids

        for igreja_permitida in igrejas_base_permitidas:
             # Para líderes, se a igreja permitida for Sede ou Regional, inclui ela e suas subordinadas
             # Se for Congregação ou Independente, inclui apenas ela.
             # A função recursiva já trata isso adicionando a própria igreja.
             todas_igrejas_permitidas_ids.update(get_subordinadas_recursivamente(igreja_permitida))
             
        if todas_igrejas_permitidas_ids:
            # Retorna um QuerySet das igrejas coletadas, garantindo que pertencem à ministério
            return Igreja.objects.filter(pk__in=list(todas_igrejas_permitidas_ids), ministerio=ministerio)
        else:
             # Se o líder não tem nenhuma igreja explicitamente permitida e não é Admin Org,
             # ou se as igrejas permitidas não existem na ministério, retorna vazio.
             return Igreja.objects.none()

    else: # Usuário não é líder financeiro nem Admin Org
        # Para outros papéis, usa apenas as igrejas explicitamente permitidas no perfil
        # Garante que as igrejas retornadas pertencem à ministério do usuário e ao seu perfil.

        igrejas_diretamente_permitidas = user.perfil.igrejas_permitidas.filter(ministerio=ministerio)
        return igrejas_diretamente_permitidas


