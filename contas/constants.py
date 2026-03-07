"""
Constantes de grupos e permissões do sistema GereIgreja.
Centraliza nomes de grupos para evitar strings hardcoded.

Última atualização: 12/02/2026
Hierarquia: Pastor Presidente → Pastor Regional → Pastor Local → Equipe Administrativa
"""

# ===================================
# GRUPOS DO SISTEMA
# ===================================

# Nível 1: Administrativo (Pastor Presidente)
ADMIN_MINISTERIO = 'Admin Ministerio'

# Nível 2: Liderança Ministerial
LIDERANCA_SECRETARIA = 'Lideranca Secretaria'
LIDERANCA_FINANCEIRA = 'Lideranca Financeira'

# Nível 3: Liderança Regional (supervisiona várias igrejas)
PASTOR_REGIONAL = 'Pastor Regional'

# Nível 4: Liderança Local (pastor de UMA igreja)
PASTOR_LOCAL = 'Pastor Local'

# Nível 5: Operacional Local (equipe administrativa)
SECRETARIO_LOCAL = 'Secretario Local'
TESOUREIRO = 'Tesoureiro'
SUPERINTENDENTE_EBD = 'Superintendente EBD'

# Nível 6: Equipes e Auxiliares
EQUIPE_EVENTOS = 'Equipe de Eventos'
EQUIPE_MIDIA = 'Equipe de Mídia'
EQUIPE_RECEPCAO = 'Equipe de Recepção'
PROFESSOR_EBD = 'Professores EBD'
SECRETARIA_EBD = 'Secretaria EBD'

# Nível 7: Base
MEMBRO_COMUM = 'Membro Comum'

# ===================================
# HIERARQUIAS (para verificações)
# ===================================

GRUPOS_ADMIN = [ADMIN_MINISTERIO]

GRUPOS_LIDERANCA_MINISTERIAL = GRUPOS_ADMIN + [
    LIDERANCA_SECRETARIA,
    LIDERANCA_FINANCEIRA,
]

GRUPOS_LIDERANCA_REGIONAL = GRUPOS_LIDERANCA_MINISTERIAL + [
    PASTOR_REGIONAL,
]

GRUPOS_LIDERANCA_LOCAL = GRUPOS_LIDERANCA_REGIONAL + [
    PASTOR_LOCAL,
]

GRUPOS_OPERACIONAL = GRUPOS_LIDERANCA_LOCAL + [
    SECRETARIO_LOCAL,
    TESOUREIRO,
    SUPERINTENDENTE_EBD,
]

GRUPOS_EQUIPES = [
    EQUIPE_EVENTOS,
    EQUIPE_MIDIA,
    EQUIPE_RECEPCAO,
    PROFESSOR_EBD,
    SECRETARIA_EBD,
]

GRUPOS_TODOS = GRUPOS_OPERACIONAL + GRUPOS_EQUIPES + [MEMBRO_COMUM]

# Alias para compatibilidade
GRUPOS_LIDERANCA = GRUPOS_LIDERANCA_REGIONAL  # Mantém nome antigo por compatibilidade

# ===================================
# HELPER FUNCTIONS
# ===================================

def user_tem_grupo(user, nome_grupo):
    """
    Verifica se usuário pertence a um grupo específico.
    
    Args:
        user: Instância de User
        nome_grupo: Nome exato do grupo (use constantes deste arquivo)
    
    Returns:
        bool: True se usuário pertence ao grupo
    """
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=nome_grupo).exists()


def user_tem_qualquer_grupo(user, lista_grupos):
    """
    Verifica se usuário pertence a qualquer grupo da lista.
    
    Args:
        user: Instância de User
        lista_grupos: Lista de nomes de grupos
    
    Returns:
        bool: True se usuário pertence a pelo menos um dos grupos
    """
    if not user.is_authenticated:
        return False
    return user.groups.filter(name__in=lista_grupos).exists()


# ===================================
# VERIFICAÇÕES DE HIERARQUIA
# ===================================

def user_is_admin(user):
    """Verifica se é Admin Ministerio (nível mais alto)."""
    return user.is_superuser or user_tem_grupo(user, ADMIN_MINISTERIO)


def user_is_lideranca_ministerial(user):
    """Verifica se é Liderança Ministerial (escopo: todas as igrejas)."""
    return user_tem_qualquer_grupo(user, GRUPOS_LIDERANCA_MINISTERIAL)


def user_is_lideranca(user):
    """Verifica se é qualquer nível de liderança (ministerial ou regional)."""
    return user_tem_qualquer_grupo(user, GRUPOS_LIDERANCA)


def user_is_lideranca_secretaria(user):
    """Verifica se é Liderança Secretaria ou superior."""
    return user_tem_qualquer_grupo(user, [ADMIN_MINISTERIO, LIDERANCA_SECRETARIA])


def user_is_lideranca_financeira(user):
    """Verifica se é Liderança Financeira ou superior."""
    return user_tem_qualquer_grupo(user, [ADMIN_MINISTERIO, LIDERANCA_FINANCEIRA])


def user_is_pastor_regional(user):
    """Verifica se é Pastor Regional ou superior."""
    return user_tem_qualquer_grupo(user, [ADMIN_MINISTERIO, LIDERANCA_SECRETARIA, LIDERANCA_FINANCEIRA, PASTOR_REGIONAL])


def user_is_pastor_local(user):
    """Verifica se é Pastor Local ou superior."""
    return user_tem_qualquer_grupo(user, GRUPOS_LIDERANCA_LOCAL)


# ===================================
# PERMISSÕES POR MÓDULO
# ===================================

def user_pode_gerenciar_secretaria(user):
    """
    Verifica se pode gerenciar secretaria (CRUD de pessoas).
    Inclui: Admin, Liderança Secretaria, Pastor Regional, Pastor Local, Secretário Local
    """
    return user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        LIDERANCA_SECRETARIA,
        PASTOR_REGIONAL,
        PASTOR_LOCAL,
        SECRETARIO_LOCAL,
    ])


def user_pode_gerenciar_cargos(user):
    """
    Verifica se pode gerenciar cargos (criar/editar/deletar).
    Cargos são LOCAIS - apenas Admin, Pastor Local e Secretário Local da igreja.
    """
    return user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        PASTOR_LOCAL,
        SECRETARIO_LOCAL,
    ])


def user_pode_gerenciar_financeiro(user):
    """
    Verifica se pode gerenciar financeiro (criar transações).
    Inclui: Admin, Tesoureiro Local
    Liderança Financeira apenas visualiza, não lança.
    """
    return user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        TESOUREIRO,
    ])


def user_pode_ver_financeiro(user):
    """
    Verifica se pode VER finanças (inclui quem apenas audita).
    Inclui: Admin, Liderança Financeira, Pastor Regional, Pastor Local, Tesoureiro Local
    """
    return user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        LIDERANCA_FINANCEIRA,
        PASTOR_REGIONAL,
        PASTOR_LOCAL,
        TESOUREIRO,
    ])


def user_pode_gerenciar_categorias_financeiras(user):
    """
    Verifica se pode criar/editar categorias financeiras globais.
    Apenas: Admin e Liderança Financeira
    """
    return user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        LIDERANCA_FINANCEIRA,
    ])


def user_pode_gerenciar_ebd(user):
    """
    Verifica se pode gerenciar EBD (turmas, alunos, aulas).
    Inclui: Admin, Liderança Secretaria, Superintendente EBD
    """
    return user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        LIDERANCA_SECRETARIA,
        SUPERINTENDENTE_EBD,
    ])


def user_pode_gerenciar_eventos(user):
    """
    Verifica se pode gerenciar eventos.
    Inclui: Admin, Liderança, Pastor Regional, Pastor Local, Equipe de Eventos
    """
    return user_tem_qualquer_grupo(user, [
        ADMIN_MINISTERIO,
        LIDERANCA_SECRETARIA,
        LIDERANCA_FINANCEIRA,
        PASTOR_REGIONAL,
        PASTOR_LOCAL,
        EQUIPE_EVENTOS,
    ])


def user_pode_enviar_comunicacao_massa(user):
    """
    Verifica se pode enviar comunicação em massa (e-mails/SMS).
    Inclui: Admin, Lideranças
    """
    return user_tem_qualquer_grupo(user, GRUPOS_LIDERANCA)


# ===================================
# ESCOPO (Ministerial vs Local)
# ===================================

def user_escopo_ministerial(user):
    """
    Retorna True se usuário tem escopo ministerial (todas as igrejas).
    False se é local (precisa filtrar por igreja_ativa).
    
    Escopo Ministerial: Admin, Liderança Secretaria, Liderança Financeira
    Escopo Regional: Pastor Regional (filtra por região)
    Escopo Local: Demais grupos (filtra por igreja_ativa)
    """
    return user_tem_qualquer_grupo(user, GRUPOS_LIDERANCA_MINISTERIAL)


def user_escopo_regional(user):
    """
    Retorna True se usuário tem escopo regional (várias igrejas da região).
    
    Escopo Regional: Pastor Regional
    """
    return user_tem_grupo(user, PASTOR_REGIONAL)


def user_escopo_local(user):
    """
    Retorna True se usuário tem escopo local (apenas sua igreja_ativa).
    
    Escopo Local: Todos exceto Liderança Ministerial e Pastor Regional
    """
    return not (user_escopo_ministerial(user) or user_escopo_regional(user))


# ===================================
# COMPATIBILIDADE (ANTIGOS NOMES)
# ===================================
# TODO: Remover após migração completa do código

def is_admin_org(user):
    """DEPRECATED: Use user_is_admin()"""
    return user_is_admin(user)


def is_tesoureiro(user):
    """DEPRECATED: Use user_tem_grupo(user, TESOUREIRO)"""
    return user_tem_grupo(user, TESOUREIRO)


def is_lider_igreja(user):
    """DEPRECATED: Use user_is_pastor_regional() ou renomear grupo"""
    # Grupo antigo 'Lider Igreja' será renomeado para 'Pastor Regional'
    return user_tem_grupo(user, 'Lider Igreja') or user_is_pastor_regional(user)


def is_finance_leader(user):
    """DEPRECATED: Use user_is_lideranca_financeira()"""
    return user_is_lideranca_financeira(user)
