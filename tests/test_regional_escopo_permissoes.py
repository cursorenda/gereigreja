import pytest
from django.contrib.auth.models import Group, User

from contas.constants import PASTOR_LOCAL, PASTOR_REGIONAL
from contas.views_paineis_permissoes import _grupos_alteraveis_por_usuario, _igrejas_visiveis_regional
from configuracao.models import Igreja, Ministerio, PerfilUsuario


@pytest.mark.django_db
def test_regional_escopo_usa_subsede_e_descendentes():
    admin = User.objects.create_user(username="admin_t", password="123")
    regional = User.objects.create_user(username="regional_t", password="123")

    ministerio = Ministerio.objects.create(nome_fantasia="Min T", administrador_principal=admin, ativo=True)

    sede = Igreja.objects.create(ministerio=ministerio, nome_igreja="Sede", tipo_igreja="sede")
    subsede = Igreja.objects.create(ministerio=ministerio, nome_igreja="Subsede", tipo_igreja="regional", igreja_superior=sede)
    local = Igreja.objects.create(ministerio=ministerio, nome_igreja="Local", tipo_igreja="congregacao", igreja_superior=subsede)

    perfil_admin = PerfilUsuario.objects.create(user=admin, ministerio=ministerio)
    perfil_admin.igrejas_permitidas.add(sede)

    perfil_regional = PerfilUsuario.objects.create(user=regional, ministerio=ministerio)
    perfil_regional.igrejas_permitidas.add(subsede)

    igrejas = _igrejas_visiveis_regional(regional)
    nomes = {i.nome_igreja for i in igrejas}

    assert "Subsede" in nomes
    assert "Local" in nomes


@pytest.mark.django_db
def test_regional_so_pode_atribuir_ate_pastor_local():
    regional = User.objects.create_user(username="regional_perm", password="123")
    g_regional, _ = Group.objects.get_or_create(name=PASTOR_REGIONAL)
    g_local, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
    regional.groups.add(g_regional)

    grupos = _grupos_alteraveis_por_usuario(regional)
    nomes = set(grupos.values_list("name", flat=True))

    assert PASTOR_LOCAL in nomes
    assert PASTOR_REGIONAL not in nomes
