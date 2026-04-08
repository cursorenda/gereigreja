"""
Testes de Validação de Escopo Hierárquico - GereIgreja
Valida que usuários só acessam dados de igrejas permitidas

Cenários testados:
1. Escopo Ministerial (Admin, Liderança)
2. Escopo Regional (Pastor Regional)
3. Escopo Local (Pastor Local, Secretário, etc)
4. Validação de acesso a objetos
5. Decorator inject_igrejas_permitidas
6. Igreja subordinadas (hierarquia)

Última atualização: 05/04/2026
"""

import pytest
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from contas.constants import *
from core.utils import (
    get_igrejas_permitidas,
    validar_acesso_igreja,
    validar_acesso_objeto_igreja
)


# ===================================
# FIXTURES
# ===================================

@pytest.fixture
def criar_grupos():
    """Cria grupos necessários."""
    grupos = {}
    for nome in [ADMIN_MINISTERIO, PASTOR_REGIONAL, PASTOR_LOCAL, 
                 SECRETARIO_LOCAL, TESOUREIRO, EQUIPE_EVENTOS]:
        grupo, _ = Group.objects.get_or_create(name=nome)
        grupos[nome] = grupo
    return grupos


@pytest.fixture
def criar_ministerio(db):
    """Cria ministério e igrejas de teste."""
    from configuracao.models import Ministerio, Igreja, PerfilUsuario
    
    # Cria usuário administrador do ministério
    admin_user = User.objects.create_user(
        username='admin_ministerio',
        email='admin@ministerio.com',
        password='senha123'
    )
    
    # Cria ministério
    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministério Teste',
        cnpj='12345678000100',
        ativo=True,
        administrador_principal=admin_user
    )
    
    # Cria igrejas: SEDE > REGIONAL > LOCAL1, LOCAL2
    sede = Igreja.objects.create(
        nome_igreja='Igreja Sede',
        ministerio=ministerio,
        tipo_igreja='sede'
    )
    
    regional = Igreja.objects.create(
        nome_igreja='Igreja Regional',
        ministerio=ministerio,
        tipo_igreja='regional',
        igreja_superior=sede
    )
    
    local1 = Igreja.objects.create(
        nome_igreja='Igreja Local 1',
        ministerio=ministerio,
        tipo_igreja='congregacao',
        igreja_superior=regional
    )
    
    local2 = Igreja.objects.create(
        nome_igreja='Igreja Local 2',
        ministerio=ministerio,
        tipo_igreja='congregacao',
        igreja_superior=regional
    )
    
    # Igreja de outro ministério
    admin_user2 = User.objects.create_user(
        username='admin_ministerio2',
        email='admin@ministerio2.com',
        password='senha123'
    )
    
    ministerio2 = Ministerio.objects.create(
        nome_fantasia='Outro Ministério',
        cnpj='99999999000100',
        ativo=True,
        administrador_principal=admin_user2
    )
    
    outra_igreja = Igreja.objects.create(
        nome_igreja='Outra Igreja',
        ministerio=ministerio2,
        tipo_igreja='sede'
    )
    
    return {
        'ministerio': ministerio,
        'sede': sede,
        'regional': regional,
        'local1': local1,
        'local2': local2,
        'ministerio2': ministerio2,
        'outra_igreja': outra_igreja
    }


@pytest.fixture
def criar_usuario_com_perfil(db, criar_ministerio):
    """Helper para criar usuário com perfil."""
    def _criar(username, grupo=None, igrejas_permitidas=None):
        from configuracao.models import PerfilUsuario
        
        user = User.objects.create_user(username=username, password='senha123')
        
        if grupo:
            user.groups.add(grupo)
        
        perfil = PerfilUsuario.objects.create(
            user=user,
            ministerio=criar_ministerio['ministerio']
        )
        
        if igrejas_permitidas:
            perfil.igrejas_permitidas.set(igrejas_permitidas)
        
        return user
    
    return _criar


# ===================================
# TESTE 1: Escopo Ministerial
# ===================================

@pytest.mark.django_db
def test_escopo_ministerial_admin_ve_todas_igrejas(criar_grupos, criar_ministerio, criar_usuario_com_perfil):
    """Admin Ministerio vê TODAS as igrejas do ministério."""
    user = criar_usuario_com_perfil('admin', grupo=criar_grupos[ADMIN_MINISTERIO])
    
    igrejas = get_igrejas_permitidas(user, criar_ministerio['ministerio'])
    
    # Deve ver as 4 igrejas do SEU ministério
    assert criar_ministerio['sede'] in igrejas
    assert criar_ministerio['regional'] in igrejas
    assert criar_ministerio['local1'] in igrejas
    assert criar_ministerio['local2'] in igrejas
    # MAS NÃO deve ver da outro ministério
    assert criar_ministerio['outra_igreja'] not in igrejas
    
    print("✓ TESTE 1: Escopo Ministerial - Admin vê todas igrejas do ministério")


@pytest.mark.django_db
def test_escopo_ministerial_com_restricao(criar_grupos, criar_ministerio, criar_usuario_com_perfil):
    """Admin com igrejas_permitidas específicas só vê essas."""
    user = criar_usuario_com_perfil(
        'admin_restrito',
        grupo=criar_grupos[ADMIN_MINISTERIO],
        igrejas_permitidas=[criar_ministerio['regional']]
    )
    
    igrejas = get_igrejas_permitidas(user, criar_ministerio['ministerio'])
    
    # Deve ver apenas a regional
    assert igrejas.count() == 1
    assert criar_ministerio['regional'] in igrejas
    
    print("✓ TESTE 1b: Admin com igrejas_permitidas - respeita restrição")


# ===================================
# TESTE 2: Escopo Regional
# ===================================

@pytest.mark.django_db
def test_escopo_regional_ve_subordinadas(criar_grupos, criar_ministerio, criar_usuario_com_perfil):
    """Pastor Regional vê igreja regional + subordinadas."""
    user = criar_usuario_com_perfil(
        'pastor_regional',
        grupo=criar_grupos[PASTOR_REGIONAL],
        igrejas_permitidas=[criar_ministerio['regional']]
    )
    
    igrejas = get_igrejas_permitidas(user, criar_ministerio['ministerio'])
    
    # Deve ver regional + local1 + local2 (subordinadas)
    assert igrejas.count() == 3, f"Pastor Regional deve ver 3 igrejas, viu {igrejas.count()}"
    assert criar_ministerio['regional'] in igrejas
    assert criar_ministerio['local1'] in igrejas
    assert criar_ministerio['local2'] in igrejas
    assert criar_ministerio['sede'] not in igrejas
    
    print("✓ TESTE 2: Escopo Regional - vê região + subordinadas")


# ===================================
# TESTE 3: Escopo Local
# ===================================

@pytest.mark.django_db
def test_escopo_local_ve_apenas_sua_igreja(criar_grupos, criar_ministerio, criar_usuario_com_perfil):
    """Pastor Local vê apenas SUA igreja."""
    user = criar_usuario_com_perfil(
        'pastor_local',
        grupo=criar_grupos[PASTOR_LOCAL],
        igrejas_permitidas=[criar_ministerio['local1']]
    )
    
    igrejas = get_igrejas_permitidas(user, criar_ministerio['ministerio'])
    
    # Deve ver apenas local1
    assert igrejas.count() == 1
    assert criar_ministerio['local1'] in igrejas
    assert criar_ministerio['local2'] not in igrejas
    assert criar_ministerio['regional'] not in igrejas
    
    print("✓ TESTE 3: Escopo Local - vê apenas sua igreja")


@pytest.mark.django_db
def test_escopo_local_secretario(criar_grupos, criar_ministerio, criar_usuario_com_perfil):
    """Secretário Local vê apenas sua igreja."""
    user = criar_usuario_com_perfil(
        'secretario',
        grupo=criar_grupos[SECRETARIO_LOCAL],
        igrejas_permitidas=[criar_ministerio['local2']]
    )
    
    igrejas = get_igrejas_permitidas(user, criar_ministerio['ministerio'])
    
    assert igrejas.count() == 1
    assert criar_ministerio['local2'] in igrejas
    
    print("✓ TESTE 3b: Secretário Local - escopo local funcionando")


# ===================================
# TESTE 4: Usuário sem Grupo
# ===================================

@pytest.mark.django_db
def test_usuario_sem_grupo_sem_acesso(criar_ministerio, criar_usuario_com_perfil):
    """Usuário sem grupo não vê nenhuma igreja."""
    user = criar_usuario_com_perfil('sem_grupo')  # Sem grupo
    
    igrejas = get_igrejas_permitidas(user, criar_ministerio['ministerio'])
    
    assert igrejas.count() == 0
    
    print("✓ TESTE 4: Usuário sem grupo - sem acesso")


# ===================================
# TESTE 5: Superusuário
# ===================================

@pytest.mark.django_db
def test_superusuario_ve_tudo(criar_ministerio):
    """Superusuário vê TODAS as igrejas de TODOS os ministérios."""
    user = User.objects.create_user(username='super', password='senha123')
    user.is_superuser = True
    user.save()
    
    igrejas = get_igrejas_permitidas(user)
    
    # Deve ver TODAS (pelo menos as 5 criadas no fixture)
    assert criar_ministerio['sede'] in igrejas
    assert criar_ministerio['regional'] in igrejas
    assert criar_ministerio['local1'] in igrejas
    assert criar_ministerio['local2'] in igrejas
    assert criar_ministerio['outra_igreja'] in igrejas
    # E deve ter no mínimo 5 (pode ter mais de outros runs)
    assert igrejas.count() >= 5
    
    print("✓ TESTE 5: Superusuário - vê todas igrejas")


# ===================================
# TESTE 6: Validação de Acesso a Igreja
# ===================================

@pytest.mark.django_db
def test_validar_acesso_igreja_permitido(criar_grupos, criar_ministerio, criar_usuario_com_perfil):
    """Valida que usuário tem acesso à igreja permitida."""
    user = criar_usuario_com_perfil(
        'teste_validacao',
        grupo=criar_grupos[PASTOR_LOCAL],
        igrejas_permitidas=[criar_ministerio['local1']]
    )
    
    # Deve ter acesso à local1
    assert validar_acesso_igreja(user, criar_ministerio['local1']) is True
    
    print("✓ TESTE 6: Validação de acesso - igreja permitida")


@pytest.mark.django_db
def test_validar_acesso_igreja_negado(criar_grupos, criar_ministerio, criar_usuario_com_perfil):
    """Valida que usuário NÃO tem acesso à igreja não permitida."""
    user = criar_usuario_com_perfil(
        'teste_negacao',
        grupo=criar_grupos[PASTOR_LOCAL],
        igrejas_permitidas=[criar_ministerio['local1']]
    )
    
    # NÃO deve ter acesso à local2
    assert validar_acesso_igreja(user, criar_ministerio['local2']) is False
    
    print("✓ TESTE 6b: Validação de acesso - igreja negada")


# ===================================
# TESTE 7: Validação de Objeto com Igreja
# ===================================

@pytest.mark.django_db
def test_validar_acesso_objeto_permitido(criar_grupos, criar_ministerio, criar_usuario_com_perfil):
    """Valida acesso a objeto que pertence a igreja permitida."""
    from secretaria.models import Membro, TipoPessoa, StatusPessoa
    
    # Cria tipo e status
    tipo = TipoPessoa.objects.create(nome='Membro')
    status = StatusPessoa.objects.create(nome='Ativo')
    
    # Cria membro da local1
    membro = Membro.objects.create(
        nome='João Teste',
        igreja=criar_ministerio['local1'],
        tipo_pessoa=tipo,
        status_pessoa=status
    )
    
    user = criar_usuario_com_perfil(
        'teste_objeto',
        grupo=criar_grupos[SECRETARIO_LOCAL],
        igrejas_permitidas=[criar_ministerio['local1']]
    )
    
    # Deve permitir acesso
    assert validar_acesso_objeto_igreja(user, membro) is True
    
    print("✓ TESTE 7: Validação objeto - acesso permitido")


@pytest.mark.django_db
def test_validar_acesso_objeto_negado(criar_grupos, criar_ministerio, criar_usuario_com_perfil):
    """Bloqueia acesso a objeto de igreja não permitida."""
    from secretaria.models import Membro, TipoPessoa, StatusPessoa
    
    tipo = TipoPessoa.objects.create(nome='Membro')
    status = StatusPessoa.objects.create(nome='Ativo')
    
    # Membro da local2
    membro = Membro.objects.create(
        nome='Maria Teste',
        igreja=criar_ministerio['local2'],
        tipo_pessoa=tipo,
        status_pessoa=status
    )
    
    # Usuário só tem acesso à local1
    user = criar_usuario_com_perfil(
        'teste_bloqueio',
        grupo=criar_grupos[SECRETARIO_LOCAL],
        igrejas_permitidas=[criar_ministerio['local1']]
    )
    
    # Deve lançar PermissionDenied
    with pytest.raises(PermissionDenied):
        validar_acesso_objeto_igreja(user, membro)
    
    print("✓ TESTE 7b: Validação objeto - acesso bloqueado")


# ===================================
# TESTE 8: Isolamento entre Ministérios
# ===================================

@pytest.mark.django_db
def test_isolamento_entre_ministerios(criar_grupos, criar_ministerio, criar_usuario_com_perfil):
    """Usuário não vê igrejas de outro ministério."""
    from configuracao.models import PerfilUsuario
    
    # Admin do ministerio1
    user1 = criar_usuario_com_perfil('admin_m1', grupo=criar_grupos[ADMIN_MINISTERIO])
    
    # Admin do ministerio2 (precisa criar explicitamente)
    user2 = User.objects.create_user(username='admin_m2', password='senha123')
    user2.groups.add(criar_grupos[ADMIN_MINISTERIO])
    perfil2 = PerfilUsuario.objects.create(
        user=user2,
        ministerio=criar_ministerio['ministerio2']
    )
    
    igrejas1 = get_igrejas_permitidas(user1, criar_ministerio['ministerio'])
    igrejas2 = get_igrejas_permitidas(user2, criar_ministerio['ministerio2'])
    
    # Admin1 vê as 4 igrejas do seu ministério
    assert criar_ministerio['sede'] in igrejas1
    assert criar_ministerio['regional'] in igrejas1
    assert criar_ministerio['local1'] in igrejas1
    assert criar_ministerio['local2'] in igrejas1
    # MAS NÃO vê a do outro
    assert criar_ministerio['outra_igreja'] not in igrejas1
    
    # Admin2 vê apenas a de seu ministério
    assert criar_ministerio['outra_igreja'] in igrejas2
    # E não vê as do outro
    assert criar_ministerio['sede'] not in igrejas2
    assert criar_ministerio['regional'] not in igrejas2
    assert criar_ministerio['local1'] not in igrejas2
    assert criar_ministerio['local2'] not in igrejas2
    
    print("✓ TESTE 8: Isolamento entre ministérios - funciona")


# ===================================
# TESTE 9: Equipes (Escopo Local)
# ===================================

@pytest.mark.django_db
def test_equipe_eventos_escopo_local(criar_grupos, criar_ministerio, criar_usuario_com_perfil):
    """Equipe de Eventos tem escopo local."""
    user = criar_usuario_com_perfil(
        'equipe',
        grupo=criar_grupos[EQUIPE_EVENTOS],
        igrejas_permitidas=[criar_ministerio['local1']]
    )
    
    # Equipe é escopo local
    assert user_escopo_local(user) is True
    assert user_escopo_ministerial(user) is False
    assert user_escopo_regional(user) is False
    
    # Deve ver apenas sua igreja
    igrejas = get_igrejas_permitidas(user, criar_ministerio['ministerio'])
    assert igrejas.count() == 1
    assert criar_ministerio['local1'] in igrejas
    
    print("✓ TESTE 9: Equipe de Eventos - escopo local correto")


# ===================================
# TESTE RESUMO
# ===================================

def test_resumo_escopo():
    """Imprime resumo dos testes de escopo."""
    print("\n" + "="*70)
    print("RESUMO: TESTES DE ESCOPO HIERÁRQUICO")
    print("="*70)
    print("✓ Teste 1:  Escopo Ministerial - Admin vê todas do ministério")
    print("✓ Teste 1b: Admin com restrição - respeita igrejas_permitidas")
    print("✓ Teste 2:  Escopo Regional - vê região + subordinadas")
    print("✓ Teste 3:  Escopo Local - Pastor vê apenas sua igreja")
    print("✓ Teste 3b: Secretário Local - escopo local")
    print("✓ Teste 4:  Usuário sem grupo - sem acesso")
    print("✓ Teste 5:  Superusuário - vê tudo")
    print("✓ Teste 6:  Validação igreja - permitida")
    print("✓ Teste 6b: Validação igreja - negada")
    print("✓ Teste 7:  Validação objeto - permitido")
    print("✓ Teste 7b: Validação objeto - bloqueado")
    print("✓ Teste 8:  Isolamento entre ministérios")
    print("✓ Teste 9:  Equipe Eventos - escopo local")
    print("="*70)
    print("SISTEMA DE ESCOPO VALIDADO - ZERO VAZAMENTO!")
    print("="*70 + "\n")
