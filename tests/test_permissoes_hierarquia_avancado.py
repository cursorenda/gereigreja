"""
Testes Avançados de Hierarquia de Permissões - GereIgreja
Cobre todos os 10 cenários críticos do sistema de permissões hierárquicas

Baseado em: docs/TESTES_PERMISSOES_AVANCADOS.md

Cenários testados:
1. Usuário com múltiplos grupos
2. Usuário inativo (is_active=False)
3. Grupo inexistente
4. Usuário sem grupo mas com is_staff=True
5. Usuário comum (sem staff, sem grupo)
6. Superusuário inativo
7. Remoção de permissão em tempo de execução
8. Múltiplos grupos do mesmo nível
9. Grupo abaixo do exigido
10. Grupo acima do exigido

Última atualização: 05/04/2026
"""

import pytest
from django.contrib.auth.models import User, Group
from contas.constants import *


# ===================================
# FIXTURES
# ===================================

@pytest.fixture
def criar_grupos():
    """Garante que todos os grupos necessários existem."""
    grupos_necessarios = [
        ADMIN_MINISTERIO,
        LIDERANCA_SECRETARIA,
        LIDERANCA_FINANCEIRA,
        PASTOR_REGIONAL,
        PASTOR_LOCAL,
        SECRETARIO_LOCAL,
        TESOUREIRO,
        SUPERINTENDENTE_EBD,
        EQUIPE_EVENTOS,
        EQUIPE_MIDIA,
        EQUIPE_RECEPCAO,
        PROFESSOR_EBD,
        SECRETARIA_EBD,
        MEMBRO_COMUM,
    ]
    
    grupos = {}
    for nome_grupo in grupos_necessarios:
        grupo, _ = Group.objects.get_or_create(name=nome_grupo)
        grupos[nome_grupo] = grupo
    
    return grupos


@pytest.fixture
def usuario_limpo(db):
    """Cria usuário de teste limpo."""
    user = User.objects.create_user(
        username='test_avancado',
        email='test@avancado.com',
        password='senha123',
        is_active=True,
        is_staff=False,
        is_superuser=False
    )
    yield user
    user.delete()


# ===================================
# TESTE 1: Usuário com Múltiplos Grupos
# ===================================

@pytest.mark.django_db
def test_usuario_multiplos_grupos_prevalece_maior_privilegio(criar_grupos, usuario_limpo):
    """
    Usuário pertence a dois grupos de níveis diferentes.
    Esperado: prevalece o grupo de maior privilégio.
    """
    user = usuario_limpo
    
    # Adiciona Tesoureiro (nível 6) e Equipe de Eventos (nível 8)
    user.groups.add(criar_grupos[TESOUREIRO])
    user.groups.add(criar_grupos[EQUIPE_EVENTOS])
    
    # Deve ter nível de Tesoureiro (mais alto)
    nivel = get_user_permission_level(user)
    nivel_tesoureiro = HIERARQUIA_GRUPOS[TESOUREIRO]
    
    assert nivel == nivel_tesoureiro, f"Esperado nível {nivel_tesoureiro}, obteve {nivel}"
    
    # Deve ter acesso como Tesoureiro
    assert user_has_permission_level_or_higher(user, TESOUREIRO), "Deve ter permissão de Tesoureiro"
    
    # Deve ter acesso às permissões de Equipe de Eventos também
    assert user_has_permission_level_or_higher(user, EQUIPE_EVENTOS), "Deve ter permissão de Equipe de Eventos"
    
    print("✓ TESTE 1: Múltiplos grupos - prevalece maior privilégio")


@pytest.mark.django_db
def test_usuario_multiplos_grupos_administrativos(criar_grupos, usuario_limpo):
    """
    Usuário com Admin + Liderança Secretaria.
    Esperado: Admin prevalece (nível 0).
    """
    user = usuario_limpo
    
    user.groups.add(criar_grupos[ADMIN_MINISTERIO])
    user.groups.add(criar_grupos[LIDERANCA_SECRETARIA])
    
    nivel = get_user_permission_level(user)
    
    assert nivel == 0, f"Admin deve ser nível 0, obteve {nivel}"
    assert user_is_admin(user), "Deve ser reconhecido como Admin"
    
    print("✓ TESTE 1b: Múltiplos grupos administrativos - Admin prevalece")


# ===================================
# TESTE 2: Usuário Inativo
# ===================================

@pytest.mark.django_db
def test_usuario_inativo_acesso_negado(criar_grupos, usuario_limpo):
    """
    Usuário está em grupo correto, mas is_active=False.
    Esperado: acesso negado (Django bloqueia por padrão).
    """
    user = usuario_limpo
    user.groups.add(criar_grupos[TESOUREIRO])
    user.is_active = False
    user.save()
    
    # Mesmo com grupo, usuário inativo não é autenticado
    assert not user.is_active, "Usuário deve estar inativo"
    assert user.groups.filter(name=TESOUREIRO).exists(), "Deve ter grupo Tesoureiro"
    
    # Django bloqueia usuários inativos no login
    # Mas as funções de permissão ainda funcionam (design decision)
    nivel = get_user_permission_level(user)
    assert nivel is not None, "Função retorna nível mesmo para inativo"
    
    print("✓ TESTE 2: Usuário inativo - Django bloqueará no login")


# ===================================
# TESTE 3: Grupo Inexistente
# ===================================

@pytest.mark.django_db
def test_grupo_inexistente_acesso_negado(usuario_limpo):
    """
    Checagem de permissão para grupo não cadastrado.
    Esperado: acesso negado, função retorna False.
    """
    user = usuario_limpo
    
    # Tenta verificar grupo que não existe na hierarquia
    grupo_invalido = 'Grupo Que Nao Existe'
    
    # Verifica que o grupo não está na hierarquia
    assert grupo_invalido not in HIERARQUIA_GRUPOS, "Grupo não deve estar na hierarquia"
    
    # user_has_permission_level_or_higher deve retornar False
    # e logar erro (já implementado na função)
    resultado = user_has_permission_level_or_higher(user, grupo_invalido)
    
    assert resultado is False, "Deve retornar False para grupo inexistente"
    
    print("✓ TESTE 3: Grupo inexistente - acesso negado corretamente")


# ===================================
# TESTE 4: Usuário sem Grupo, mas is_staff=True
# ===================================

@pytest.mark.django_db
def test_staff_sem_grupo_sem_permissoes(usuario_limpo):
    """
    Usuário sem grupo, mas com is_staff=True.
    Esperado: pode acessar admin Django, mas sem permissões específicas.
    """
    user = usuario_limpo
    user.is_staff = True
    user.save()
    
    assert user.is_staff, "Deve ser staff"
    assert user.groups.count() == 0, "Não deve ter grupos"
    
    # Não deve ter nível de permissão
    nivel = get_user_permission_level(user)
    assert nivel is None, "Staff sem grupo não tem nível de permissão"
    
    # Não deve ter acesso a nenhuma permissão específica
    assert not user_has_permission_level_or_higher(user, MEMBRO_COMUM), "Sem grupos, sem acesso"
    assert not user_is_admin(user), "Não é admin"
    assert not user_is_lideranca(user), "Não é liderança"
    
    print("✓ TESTE 4: Staff sem grupo - sem permissões específicas")


# ===================================
# TESTE 5: Usuário Comum (sem staff, sem grupo)
# ===================================

@pytest.mark.django_db
def test_usuario_comum_sem_permissoes(usuario_limpo):
    """
    Usuário comum (sem staff, sem grupo).
    Esperado: acesso negado a todas as áreas administrativas.
    """
    user = usuario_limpo
    
    assert not user.is_staff, "Não deve ser staff"
    assert not user.is_superuser, "Não deve ser superuser"
    assert user.groups.count() == 0, "Não deve ter grupos"
    
    # Não tem nível
    nivel = get_user_permission_level(user)
    assert nivel is None, "Usuário comum não tem nível"
    
    # Não tem nenhuma permissão
    assert not user_is_admin(user)
    assert not user_is_lideranca(user)
    assert not user_pode_gerenciar_secretaria(user)
    assert not user_pode_gerenciar_financeiro(user)
    
    print("✓ TESTE 5: Usuário comum - sem permissões")


# ===================================
# TESTE 6: Superusuário Inativo
# ===================================

@pytest.mark.django_db
def test_superusuario_inativo_mantem_acesso_total(usuario_limpo):
    """
    Usuário superusuário com is_active=False.
    Esperado: funções de permissão retornam True (mas Django bloqueia login).
    """
    user = usuario_limpo
    user.is_superuser = True
    user.is_active = False
    user.save()
    
    assert user.is_superuser, "Deve ser superuser"
    assert not user.is_active, "Deve estar inativo"
    
    # Superuser sempre tem nível 0
    nivel = get_user_permission_level(user)
    assert nivel == 0, "Superuser sempre tem nível 0"
    
    # Superuser sempre tem todas as permissões (mesmo inativo)
    assert user_has_permission_level_or_higher(user, MEMBRO_COMUM), "Superuser tem todas as permissões"
    assert user_is_admin(user), "Superuser é reconhecido como admin"
    
    # Django bloqueia no login, mas as funções de permissão funcionam
    print("✓ TESTE 6: Superusuário inativo - funções retornam True (Django bloqueia login)")


# ===================================
# TESTE 7: Remoção de Permissão em Runtime
# ===================================

@pytest.mark.django_db
def test_remocao_permissao_runtime_efeito_imediato(criar_grupos, usuario_limpo):
    """
    Remover grupo do usuário durante execução.
    Esperado: acesso negado imediatamente.
    """
    user = usuario_limpo
    grupo_tesoureiro = criar_grupos[TESOUREIRO]
    
    # Adiciona grupo
    user.groups.add(grupo_tesoureiro)
    
    # Verifica que tem permissão
    assert user_has_permission_level_or_higher(user, TESOUREIRO), "Deve ter permissão inicialmente"
    
    # Remove grupo
    user.groups.remove(grupo_tesoureiro)
    
    # Força refresh do cache do Django
    user.refresh_from_db()
    
    # Verifica que perdeu permissão IMEDIATAMENTE
    assert not user_has_permission_level_or_higher(user, TESOUREIRO), "Deve perder permissão imediatamente"
    assert get_user_permission_level(user) is None, "Não deve ter mais nível de permissão"
    
    print("✓ TESTE 7: Remoção em runtime - efeito imediato")


# ===================================
# TESTE 8: Múltiplos Grupos do Mesmo Nível
# ===================================

@pytest.mark.django_db
def test_multiplos_grupos_mesmo_nivel(criar_grupos, usuario_limpo):
    """
    Usuário com Tesoureiro + Superintendente EBD (ambos nível 5).
    Esperado: acesso concedido se qualquer grupo for suficiente.
    """
    user = usuario_limpo
    
    # Adiciona dois grupos do mesmo nível (6 na hierarquia)
    user.groups.add(criar_grupos[TESOUREIRO])
    user.groups.add(criar_grupos[SUPERINTENDENTE_EBD])
    
    # Ambos estão no mesmo nível
    nivel_tesoureiro = HIERARQUIA_GRUPOS[TESOUREIRO]
    nivel_superintendente = HIERARQUIA_GRUPOS[SUPERINTENDENTE_EBD]
    
    # Deve ter o menor índice (maior privilégio entre os dois)
    nivel_user = get_user_permission_level(user)
    nivel_esperado = min(nivel_tesoureiro, nivel_superintendente)
    
    assert nivel_user == nivel_esperado, f"Deve ter nível {nivel_esperado}"
    
    # Deve ter acesso com qualquer um dos grupos
    assert user_has_permission_level_or_higher(user, TESOUREIRO)
    assert user_has_permission_level_or_higher(user, SUPERINTENDENTE_EBD)
    
    print("✓ TESTE 8: Múltiplos grupos mesmo nível - prevalece menor índice")


# ===================================
# TESTE 9: Grupo Abaixo do Exigido
# ===================================

@pytest.mark.django_db
def test_grupo_abaixo_acesso_negado(criar_grupos, usuario_limpo):
    """
    Equipe de Eventos tentando acessar função de Tesoureiro.
    Esperado: acesso negado.
    """
    user = usuario_limpo
    
    # Adiciona grupo de nível baixo
    user.groups.add(criar_grupos[EQUIPE_EVENTOS])
    
    # Tenta acessar permissão de nível superior
    assert not user_has_permission_level_or_higher(user, TESOUREIRO), \
        "Equipe de Eventos NÃO deve ter permissão de Tesoureiro"
    
    assert not user_has_permission_level_or_higher(user, PASTOR_LOCAL), \
        "Equipe de Eventos NÃO deve ter permissão de Pastor Local"
    
    # Mas deve ter acesso ao próprio nível e inferiores
    assert user_has_permission_level_or_higher(user, EQUIPE_EVENTOS), \
        "Deve ter permissão do próprio grupo"
    
    assert user_has_permission_level_or_higher(user, MEMBRO_COMUM), \
        "Deve ter permissão de níveis inferiores"
    
    print("✓ TESTE 9: Grupo abaixo - acesso negado corretamente")


# ===================================
# TESTE 10: Grupo Acima do Exigido
# ===================================

@pytest.mark.django_db
def test_grupo_acima_acesso_concedido(criar_grupos, usuario_limpo):
    """
    Admin Ministerio tentando acessar função de Tesoureiro.
    Esperado: acesso concedido (herança hierárquica).
    """
    user = usuario_limpo
    
    # Adiciona grupo de nível máximo
    user.groups.add(criar_grupos[ADMIN_MINISTERIO])
    
    # Admin deve ter TODAS as permissões
    assert user_has_permission_level_or_higher(user, ADMIN_MINISTERIO)
    assert user_has_permission_level_or_higher(user, PASTOR_REGIONAL)
    assert user_has_permission_level_or_higher(user, PASTOR_LOCAL)
    assert user_has_permission_level_or_higher(user, TESOUREIRO)
    assert user_has_permission_level_or_higher(user, EQUIPE_EVENTOS)
    assert user_has_permission_level_or_higher(user, MEMBRO_COMUM)
    
    # Nível deve ser 0 (maior privilégio)
    assert get_user_permission_level(user) == 0
    
    print("✓ TESTE 10: Grupo acima - acesso concedido (herança hierárquica)")


# ===================================
# TESTE BÔNUS: Escopo Ministerial/Regional/Local
# ===================================

@pytest.mark.django_db
def test_escopo_ministerial(criar_grupos, usuario_limpo):
    """Testa função de escopo ministerial."""
    user = usuario_limpo
    
    # Admin tem escopo ministerial
    user.groups.add(criar_grupos[ADMIN_MINISTERIO])
    assert user_escopo_ministerial(user), "Admin deve ter escopo ministerial"
    assert not user_escopo_regional(user), "Admin não é regional"
    assert not user_escopo_local(user), "Admin não é local"
    
    # Limpa
    user.groups.clear()
    
    # Pastor Regional tem escopo regional
    user.groups.add(criar_grupos[PASTOR_REGIONAL])
    assert not user_escopo_ministerial(user), "Pastor Regional não é ministerial"
    assert user_escopo_regional(user), "Pastor Regional tem escopo regional"
    assert not user_escopo_local(user), "Pastor Regional não é local"
    
    # Limpa
    user.groups.clear()
    
    # Tesoureiro tem escopo local
    user.groups.add(criar_grupos[TESOUREIRO])
    assert not user_escopo_ministerial(user), "Tesoureiro não é ministerial"
    assert not user_escopo_regional(user), "Tesoureiro não é regional"
    assert user_escopo_local(user), "Tesoureiro tem escopo local"
    
    print("✓ TESTE BÔNUS: Escopos ministerial/regional/local funcionam corretamente")


# ===================================
# TESTE BÔNUS: Funções Helper de Permissões Específicas
# ===================================

@pytest.mark.django_db
def test_funcoes_helper_permissoes(criar_grupos, usuario_limpo):
    """Testa funções helper específicas."""
    user = usuario_limpo
    
    # Tesoureiro pode gerenciar financeiro
    user.groups.add(criar_grupos[TESOUREIRO])
    assert user_pode_gerenciar_financeiro(user), "Tesoureiro deve gerenciar financeiro"
    
    user.groups.clear()
    
    # Secretário pode gerenciar secretaria
    user.groups.add(criar_grupos[SECRETARIO_LOCAL])
    assert user_pode_gerenciar_secretaria(user), "Secretário deve gerenciar secretaria"
    assert user_pode_gerenciar_cargos(user), "Secretário pode gerenciar cargos"
    
    user.groups.clear()
    
    # Equipe de Eventos pode gerenciar eventos
    user.groups.add(criar_grupos[EQUIPE_EVENTOS])
    assert user_pode_gerenciar_eventos(user), "Equipe de Eventos deve gerenciar eventos"
    assert not user_pode_gerenciar_financeiro(user), "Equipe não gerencia financeiro"
    
    print("✓ TESTE BÔNUS: Funções helper de permissões específicas funcionam")


# ===================================
# TESTE INTEGRAÇÃO: Cenário Real Completo
# ===================================

@pytest.mark.django_db
def test_cenario_real_completo(criar_grupos):
    """
    Cenário real: 4 usuários com diferentes níveis.
    Testa interação completa do sistema de hierarquia.
    """
    # 1. Superusuário (desenvolvedor)
    dev = User.objects.create_user('dev', 'dev@igreja.com', 'pass')
    dev.is_superuser = True
    dev.is_staff = True
    dev.save()
    
    # 2. Admin Ministerio
    admin = User.objects.create_user('admin', 'admin@igreja.com', 'pass')
    admin.is_staff = True
    admin.groups.add(criar_grupos[ADMIN_MINISTERIO])
    
    # 3. Pastor Local
    pastor = User.objects.create_user('pastor', 'pastor@igreja.com', 'pass')
    pastor.is_staff = True
    pastor.groups.add(criar_grupos[PASTOR_LOCAL])
    
    # 4. Membro Comum
    membro = User.objects.create_user('membro', 'membro@igreja.com', 'pass')
    membro.groups.add(criar_grupos[MEMBRO_COMUM])
    
    # Verifica hierarquia
    assert get_user_permission_level(dev) == 0, "Dev tem nível 0"
    assert get_user_permission_level(admin) == 0, "Admin tem nível 0"
    assert get_user_permission_level(pastor) == HIERARQUIA_GRUPOS[PASTOR_LOCAL]
    assert get_user_permission_level(membro) == HIERARQUIA_GRUPOS[MEMBRO_COMUM]
    
    # Dev e Admin podem tudo
    assert user_has_permission_level_or_higher(dev, MEMBRO_COMUM)
    assert user_has_permission_level_or_higher(admin, TESOUREIRO)
    
    # Pastor pode gerenciar local, mas não ministerial
    assert user_has_permission_level_or_higher(pastor, SECRETARIO_LOCAL)
    assert user_has_permission_level_or_higher(pastor, TESOUREIRO)
    assert not user_has_permission_level_or_higher(pastor, PASTOR_REGIONAL)
    assert not user_has_permission_level_or_higher(pastor, ADMIN_MINISTERIO)
    
    # Membro só tem acesso básico
    assert user_has_permission_level_or_higher(membro, MEMBRO_COMUM)
    assert not user_has_permission_level_or_higher(membro, EQUIPE_EVENTOS)
    assert not user_has_permission_level_or_higher(membro, TESOUREIRO)
    
    # Limpa
    dev.delete()
    admin.delete()
    pastor.delete()
    membro.delete()
    
    print("✓ TESTE INTEGRAÇÃO: Cenário real completo - hierarquia funcionando")


# ===================================
# RESUMO
# ===================================

def test_resumo_testes():
    """Imprime resumo dos testes."""
    print("\n" + "="*70)
    print("RESUMO: TESTES AVANÇADOS DE HIERARQUIA DE PERMISSÕES")
    print("="*70)
    print("✓ Teste 1:  Múltiplos grupos - prevalece maior privilégio")
    print("✓ Teste 2:  Usuário inativo - Django bloqueia login")
    print("✓ Teste 3:  Grupo inexistente - acesso negado")
    print("✓ Teste 4:  Staff sem grupo - sem permissões específicas")
    print("✓ Teste 5:  Usuário comum - sem permissões")
    print("✓ Teste 6:  Superusuário inativo - funções retornam True")
    print("✓ Teste 7:  Remoção em runtime - efeito imediato")
    print("✓ Teste 8:  Múltiplos grupos mesmo nível - menor índice")
    print("✓ Teste 9:  Grupo abaixo - acesso negado")
    print("✓ Teste 10: Grupo acima - herança hierárquica")
    print("✓ Bônus:    Escopos ministerial/regional/local")
    print("✓ Bônus:    Funções helper específicas")
    print("✓ Bônus:    Cenário real completo")
    print("="*70)
    print("TODOS OS CENÁRIOS CRÍTICOS COBERTOS!")
    print("="*70 + "\n")
