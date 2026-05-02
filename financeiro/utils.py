# c:\Gereigreja\financeiro\utils.py
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, Group
from configuracao.models import Igreja, PerfilUsuario # Importar PerfilUsuario
from django.db.models import Q # Importar Q para consultas complexas
from contas.constants import (
    ADMIN_MINISTERIO, TESOUREIRO, PASTOR_REGIONAL, LIDERANCA_FINANCEIRA,
    user_is_admin, user_is_lideranca_financeira, user_has_permission_level_or_higher,
    PASTOR_LOCAL
)



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
    return user_is_admin(user)

def is_tesoureiro(user):
    """Verifica se o usuário é Tesoureiro."""
    return _user_in_group(user, TESOUREIRO)

def is_lider_igreja(user):
    """Verifica se o usuário é Pastor Local ou superior na hierarquia."""
    return user_has_permission_level_or_higher(user, PASTOR_LOCAL)

# --- Funções de Verificação de Permissão Financeira ---

def has_finance_view_permission(user):
    """Verifica se o usuário tem permissão para VER dados financeiros.
    Aceita: Admin, Liderança Financeira, Pastor Regional, Pastor Local e Tesoureiro.
    """
    return user_has_permission_level_or_higher(user, TESOUREIRO)

def has_finance_edit_permission(user):
    """Verifica se o usuário tem permissão para EDITAR/ADICIONAR/EXCLUIR dados financeiros.
    Aceita: Admin, Liderança Financeira, Pastor Regional, Pastor Local e Tesoureiro.
    """
    return user_has_permission_level_or_higher(user, TESOUREIRO)


def is_finance_leader(user):
    """ Verifica se o usuário é Admin da Ministério, Liderança Financeira, ou Pastor Regional/Local (papéis com acesso hierárquico). """
    from contas.constants import ADMIN_MINISTERIO, LIDERANCA_FINANCEIRA, PASTOR_REGIONAL, PASTOR_LOCAL, user_tem_qualquer_grupo
    return user_tem_qualquer_grupo(user, [ADMIN_MINISTERIO, LIDERANCA_FINANCEIRA, PASTOR_REGIONAL, PASTOR_LOCAL])


# --- Função para Obter Igrejas Permitidas ---

def get_allowed_churches_for_user(user):
    """
    Retorna um QuerySet das Igrejas que o usuário tem permissão para acessar.
    
    Esta função é usada globalmente no sistema para:
    1. Popular o seletor de igreja no topo da interface
    2. Determinar o escopo de dados que o usuário pode ver
    3. Validar se uma igreja selecionada é permitida
    
    HIERARQUIA DE PERMISSÕES (ordem de verificação):
    
    1. Admin Org (is_admin_org):
       → Retorna: TODAS as igrejas do ministério
       → Use case: Administrador principal do sistema
    
    2. Permissões Financeiras (has_finance_view_permission):
       a) Líder Financeiro (is_finance_leader):
          → Retorna: Igrejas configuradas no perfil + subordinadas (recursivo)
          → Use case: Tesoureiro geral, líder financeiro de região
       
       b) Outros papéis financeiros:
          → Retorna: Igrejas explicitamente permitidas (perfil.igrejas_permitidas)
          → Use case: Tesoureiro local, líder de uma igreja específica
    
    3. Membros sem permissão financeira (Pessoa.usuario = user):
       → Retorna: Igreja onde é cadastrado como membro (Pessoa.igreja)
       → Use case: Professores EBD, pastores locais, diáconos, membros comuns
       → Nota: Assume que pessoa tem cargo apenas na igreja onde é membro
    
    4. Sem vínculo:
       → Retorna: QuerySet vazio (Igreja.objects.none())
       → Use case: Usuário sem perfil ou sem cadastro como pessoa
    
    REGRAS DE NEGÓCIO:
    - Uma pessoa é MEMBRO de uma única igreja (Pessoa.igreja)
    - Pode LECIONAR/ATUAR em múltiplas turmas, mas todas da mesma igreja
    - Cargos (MembroCargo) não têm campo igreja (inferido da pessoa)
    - Se no futuro precisar de múltiplas igrejas: adicionar campo igreja em MembroCargo
    
    PERFORMANCE:
    - Usa select_related/prefetch_related para evitar N+1 queries
    - Recursão em subordinadas pode ser cara (considerar cache)
    
    EXEMPLOS DE USO:
    
    # No middleware (core/middleware.py):
    allowed = get_allowed_churches_for_user(request.user)
    if igreja_ativa_id in allowed.values_list('pk', flat=True):
        request.igreja_ativa = allowed.get(pk=igreja_ativa_id)
    
    # Em views:
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        membros = Membro.objects.filter(igreja=request.igreja_ativa)
    
    # Para relatórios consolidados:
    todas_igrejas = get_allowed_churches_for_user(request.user)
    for igreja in todas_igrejas:
        # ... agregar dados de cada igreja
    
    TESTES:
    Ver: escola_biblica/tests/test_professor_permissions.py
    
    Args:
        user (User): Usuário autenticado do Django
    
    Returns:
        QuerySet[Igreja]: Igrejas que o usuário pode acessar, filtradas por ministério
        
    Raises:
        Nenhuma exceção. Retorna QuerySet vazio se usuário não tem acesso.
    
    See Also:
        - docs/SELETOR_IGREJA.md: Documentação completa
        - core/middleware.py: ActiveChurchMiddleware
        - escola_biblica/views.py: Exemplos de uso com permissões granulares
    """
    if not user.is_authenticated or not hasattr(user, 'perfil') or not user.perfil.ministerio:
        return Igreja.objects.none() # Retorna queryset vazio por segurança

    ministerio = user.perfil.ministerio

    # Verifica se o usuário tem permissão de visualização financeira
    if has_finance_view_permission(user):
        # LÓGICA FINANCEIRA (mantém código original)
        
        # Se o usuário é Admin da Ministério ou Líder Financeiro, expandir permissões
        if is_finance_leader(user):
            # Começa com as igrejas diretamente permitidas no perfil
            igrejas_base_permitidas = user.perfil.igrejas_permitidas.filter(ministerio=ministerio)
            
            # Se o usuário não tem nenhuma igreja explicitamente permitida, mas é líder,
            # e é Admin Org, ele vê TUDO. Se for apenas Líder Financeiro sem igrejas permitidas,
            # talvez a regra seja ver apenas as Sede/Regionais? Vamos assumir que Admin Org vê tudo
            # e Líder Financeiro vê as permitidas + subordinadas.
            if is_admin_org(user) and not igrejas_base_permitidas.exists():
                 # Admin Org sem igrejas permitidas explicitamente vê todas do ministério
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
            # Para outros papéis financeiros, usa apenas as igrejas explicitamente permitidas no perfil
            # Garante que as igrejas retornadas pertencem à ministério do usuário e ao seu perfil.
            igrejas_diretamente_permitidas = user.perfil.igrejas_permitidas.filter(ministerio=ministerio)
            return igrejas_diretamente_permitidas
    
    # NOVO: Usuário NÃO tem permissão financeira, mas pode ser membro (professor, pastor, etc)
    # Retorna a igreja onde é cadastrado como membro
    if hasattr(user, 'membro_secretaria') and user.membro_secretaria:
        membro = user.membro_secretaria
        if membro.igreja:
            # Retorna apenas a igreja onde é membro
            return Igreja.objects.filter(pk=membro.igreja.pk, ministerio=ministerio)
    
    # Sem permissão financeira e sem cadastro como membro: retorna vazio
    return Igreja.objects.none()



