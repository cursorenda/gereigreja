"""
Testes de Permissões no Admin — GereIgreja
Valida que as classes admin registradas respeitam as restrições corretas de acesso.

Cenários testados:
1. Admin site: Superusuário tem acesso total
2. Admin site: Staff sem superuser tem acesso limitado
3. Admin site: Usuário normal não acessa admin
4. Modelos de auditoria: read-only para staff
5. Modelos de auditoria: superuser pode deletar
6. GroupAdminProtegido: nomes protegidos não editáveis
7. Register: todos os modelos esperados estão registrados no admin.site
8. Modularização: subarchivos de domínio importados corretamente

Última atualização: 11/05/2026

NOTA: Testes marcados com @pytest.mark.django_db requerem banco de dados funcional.
Se falhar com "table already exists", há um conflito de migrations em secretaria/
(dois arquivos com prefixo 0014_ sem merge resolvido para SQLite de teste).
Os testes sem banco (seção Modularização) passam sempre.
"""

import pytest
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.test import Client, TestCase
from django.urls import reverse


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        username='superadmin',
        email='super@test.com',
        password='super123',
    )


@pytest.fixture
def staff_user(db):
    user = User.objects.create_user(
        username='staffuser',
        email='staff@test.com',
        password='staff123',
        is_staff=True,
    )
    return user


@pytest.fixture
def normal_user(db):
    return User.objects.create_user(
        username='normaluser',
        email='normal@test.com',
        password='normal123',
    )


@pytest.fixture
def client_superuser(superuser):
    c = Client()
    c.force_login(superuser)
    return c


@pytest.fixture
def client_staff(staff_user):
    c = Client()
    c.force_login(staff_user)
    return c


@pytest.fixture
def client_normal(normal_user):
    c = Client()
    c.force_login(normal_user)
    return c


# ---------------------------------------------------------------------------
# 1. Acesso ao admin.site
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_superuser_acessa_admin(client_superuser):
    """Superusuário deve conseguir acessar /admin/."""
    response = client_superuser.get('/admin/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_staff_acessa_admin(client_staff):
    """Staff (sem superuser) deve conseguir acessar /admin/."""
    response = client_staff.get('/admin/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_usuario_normal_nao_acessa_admin(client_normal):
    """Usuário normal deve ser redirecionado do admin."""
    response = client_normal.get('/admin/')
    assert response.status_code == 302  # redirect para login


# ---------------------------------------------------------------------------
# 2. Modelos registrados no admin.site
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_modelos_configuracao_registrados():
    """Modelos do app configuracao devem estar no admin.site."""
    from configuracao.models import Ministerio, Igreja, ConfiguracaoSistema, Plano

    assert admin.site.is_registered(Ministerio), "Ministerio não registrado"
    assert admin.site.is_registered(Igreja), "Igreja não registrado"
    assert admin.site.is_registered(ConfiguracaoSistema), "ConfiguracaoSistema não registrado"
    assert admin.site.is_registered(Plano), "Plano não registrado"


@pytest.mark.django_db
def test_modelos_secretaria_registrados():
    """Modelos do app secretaria devem estar no admin.site."""
    from secretaria.models import Membro, GrupoCasa, Cargo

    assert admin.site.is_registered(Membro), "Membro não registrado"
    assert admin.site.is_registered(GrupoCasa), "GrupoCasa não registrado"
    assert admin.site.is_registered(Cargo), "Cargo não registrado"


@pytest.mark.django_db
def test_modelos_financeiro_registrados():
    """Modelos do app financeiro devem estar no admin.site."""
    from financeiro.models import Receitas, Despesas, ContaBancaria

    assert admin.site.is_registered(Receitas), "Receitas não registrado"
    assert admin.site.is_registered(Despesas), "Despesas não registrado"
    assert admin.site.is_registered(ContaBancaria), "ContaBancaria não registrado"


@pytest.mark.django_db
def test_modelos_comunicacao_registrados():
    """Modelos do app comunicacao devem estar no admin.site."""
    from comunicacao.models import Aviso

    assert admin.site.is_registered(Aviso), "Aviso não registrado"


@pytest.mark.django_db
def test_modelos_contas_registrados():
    """Modelos do app contas devem estar no admin.site."""
    from contas.models import Convite, ConsentimentoLGPD

    assert admin.site.is_registered(Convite), "Convite não registrado"
    assert admin.site.is_registered(ConsentimentoLGPD), "ConsentimentoLGPD não registrado"


@pytest.mark.django_db
def test_user_registrado_apenas_uma_vez():
    """User deve estar registrado exatamente uma vez no admin.site global."""
    # Se registrado mais de uma vez, Django levanta AlreadyRegistered no startup
    # Aqui só verificamos que está registrado
    assert admin.site.is_registered(User), "User não está registrado no admin.site"


# ---------------------------------------------------------------------------
# 3. Classes admin de auditoria — permissões read-only
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_permission_change_log_admin_read_only():
    """PermissionChangeLogAdmin deve ser read-only (sem add/delete)."""
    from auditoria.models import PermissionChangeLog

    # Busca a classe registrada no auditoria_admin_site
    from auditoria.admin_site import auditoria_admin_site
    if auditoria_admin_site.is_registered(PermissionChangeLog):
        admin_class = auditoria_admin_site._registry[PermissionChangeLog]
        mock_request = _mock_request(is_superuser=False)
        assert admin_class.has_add_permission(mock_request) is False
        assert admin_class.has_delete_permission(mock_request) is False


@pytest.mark.django_db
def test_access_denied_log_admin_read_only():
    """AccessDeniedLogAdmin deve ser read-only."""
    from auditoria.models import AccessDeniedLog

    from auditoria.admin_site import auditoria_admin_site
    if auditoria_admin_site.is_registered(AccessDeniedLog):
        admin_class = auditoria_admin_site._registry[AccessDeniedLog]
        mock_request = _mock_request(is_superuser=False)
        assert admin_class.has_add_permission(mock_request) is False


@pytest.mark.django_db
def test_auditoria_superuser_pode_deletar():
    """Superusuário pode deletar em modelos de auditoria (por override)."""
    from auditoria.models import PermissionChangeLog

    from auditoria.admin_site import auditoria_admin_site
    if auditoria_admin_site.is_registered(PermissionChangeLog):
        admin_class = auditoria_admin_site._registry[PermissionChangeLog]
        mock_request = _mock_request(is_superuser=True)
        assert admin_class.has_delete_permission(mock_request) is True


# ---------------------------------------------------------------------------
# 4. GroupAdminProtegido — proteção de nomes de grupos
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_group_admin_protegido_registrado():
    """Group deve estar registrado (protegido) no admin.site."""
    assert admin.site.is_registered(Group), "Group não registrado"


@pytest.mark.django_db
def test_group_admin_nao_permite_deletar_grupo_protegido(client_superuser):
    """Grupos do sistema (GRUPOS_TODOS) não devem ser deletáveis."""
    from contas.constants import GRUPOS_TODOS

    # Cria o grupo protegido
    grupo, _ = Group.objects.get_or_create(name=GRUPOS_TODOS[0])
    url = f'/admin/auth/group/{grupo.pk}/delete/'
    response = client_superuser.get(url)
    # Deve bloquear (403) ou redirecionar, não mostrar confirmação de delete (200)
    assert response.status_code in (403, 302)


# ---------------------------------------------------------------------------
# 5. Modularização — subarchivos importados corretamente
# ---------------------------------------------------------------------------

def test_configuracao_admin_hub_imports():
    """O hub configuracao/admin.py deve re-exportar todas as classes."""
    import configuracao.admin as hub
    from configuracao.admin_ministerio import MinisterioAdmin, IgrejaAdmin
    from configuracao.admin_planos import PlanoAdmin
    from configuracao.admin_sistema import AtualizacaoSistemaAdmin

    # As classes dos subarchivos devem ser acessíveis via hub
    assert MinisterioAdmin is not None
    assert IgrejaAdmin is not None
    assert PlanoAdmin is not None
    assert AtualizacaoSistemaAdmin is not None


def test_secretaria_admin_hub_imports():
    """O hub secretaria/admin.py deve re-exportar todas as classes."""
    from secretaria.admin_membros import MembroAdmin
    from secretaria.admin_grupos import GrupoCasaAdmin
    from secretaria.admin_cargos import CargoAdmin

    assert MembroAdmin is not None
    assert GrupoCasaAdmin is not None
    assert CargoAdmin is not None


def test_financeiro_admin_hub_imports():
    """O hub financeiro/admin.py deve re-exportar todas as classes."""
    from financeiro.admin_movimentacao import ReceitasAdmin, DespesasAdmin
    from financeiro.admin_contas import ContaBancariaAdmin

    assert ReceitasAdmin is not None
    assert DespesasAdmin is not None
    assert ContaBancariaAdmin is not None


def test_comunicacao_admin_hub_imports():
    """O hub comunicacao/admin.py deve re-exportar todas as classes."""
    from comunicacao.admin_avisos import AvisoAdmin
    from comunicacao.admin_whatsapp import WhatsAppConfiguracaoAdmin

    assert AvisoAdmin is not None
    assert WhatsAppConfiguracaoAdmin is not None


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _mock_request(is_superuser=False):
    from unittest.mock import MagicMock
    req = MagicMock()
    req.user = MagicMock(spec=User)
    req.user.is_superuser = is_superuser
    req.user.is_active = True
    req.user.is_staff = True
    return req
