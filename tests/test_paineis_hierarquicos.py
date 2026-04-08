import pytest
from django.contrib.auth.models import Group, User
from django.urls import reverse

from contas.constants import ADMIN_MINISTERIO, PASTOR_LOCAL
from contas.models import HierarquiaPermissoes
from configuracao.models import Igreja, Ministerio, PerfilUsuario


@pytest.fixture
def base_hierarquia_data(db):
    admin_principal = User.objects.create_user(username="admin_principal", password="senha123")
    ministerio = Ministerio.objects.create(
        nome_fantasia="Ministerio Teste",
        administrador_principal=admin_principal,
        ativo=True,
    )

    igreja_a = Igreja.objects.create(ministerio=ministerio, nome_igreja="Igreja A", tipo_igreja="congregacao")
    igreja_b = Igreja.objects.create(ministerio=ministerio, nome_igreja="Igreja B", tipo_igreja="congregacao")

    pastor_local = User.objects.create_user(username="pastor_local", password="senha123")
    alvo_mesma_igreja = User.objects.create_user(username="alvo_a", password="senha123")
    alvo_outra_igreja = User.objects.create_user(username="alvo_b", password="senha123")

    PerfilUsuario.objects.create(user=admin_principal, ministerio=ministerio)

    perfil_pastor = PerfilUsuario.objects.create(user=pastor_local, ministerio=ministerio)
    perfil_pastor.igrejas_permitidas.add(igreja_a)

    perfil_alvo_a = PerfilUsuario.objects.create(user=alvo_mesma_igreja, ministerio=ministerio)
    perfil_alvo_a.igrejas_permitidas.add(igreja_a)

    perfil_alvo_b = PerfilUsuario.objects.create(user=alvo_outra_igreja, ministerio=ministerio)
    perfil_alvo_b.igrejas_permitidas.add(igreja_b)

    grupo_pastor_local, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
    pastor_local.groups.add(grupo_pastor_local)

    return {
        "pastor_local": pastor_local,
        "alvo_mesma_igreja": alvo_mesma_igreja,
        "alvo_outra_igreja": alvo_outra_igreja,
        "igreja_a": igreja_a,
    }


@pytest.mark.django_db
def test_pastor_local_altera_todos_grupos_na_propria_igreja(client, base_hierarquia_data):
    pastor_local = base_hierarquia_data["pastor_local"]
    alvo = base_hierarquia_data["alvo_mesma_igreja"]

    grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)

    client.force_login(pastor_local)
    response = client.post(
        reverse("contas:editar_permissoes_usuario", kwargs={"user_id": alvo.id}),
        {"grupos": [str(grupo_admin.id)]},
        follow=True,
    )

    assert response.status_code == 200
    alvo.refresh_from_db()
    assert alvo.groups.filter(name=ADMIN_MINISTERIO).exists()


@pytest.mark.django_db
def test_pastor_local_nao_altera_usuario_de_outra_igreja(client, base_hierarquia_data):
    pastor_local = base_hierarquia_data["pastor_local"]
    alvo_outra_igreja = base_hierarquia_data["alvo_outra_igreja"]
    grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)

    client.force_login(pastor_local)
    response = client.post(
        reverse("contas:editar_permissoes_usuario", kwargs={"user_id": alvo_outra_igreja.id}),
        {"grupos": [str(grupo_admin.id)]},
        follow=True,
    )

    assert response.status_code == 200
    alvo_outra_igreja.refresh_from_db()
    assert not alvo_outra_igreja.groups.filter(name=ADMIN_MINISTERIO).exists()


@pytest.mark.django_db
def test_gestao_vinculos_cria_vinculo_para_pastor_local(client, base_hierarquia_data):
    pastor_local = base_hierarquia_data["pastor_local"]
    alvo = base_hierarquia_data["alvo_mesma_igreja"]
    igreja = base_hierarquia_data["igreja_a"]

    client.force_login(pastor_local)
    response = client.post(
        reverse("contas:gestao_vinculos_hierarquicos"),
        {
            "usuario_subordinado": str(alvo.id),
            "nivel_superior": PASTOR_LOCAL,
            "igreja": str(igreja.id),
            "ativo": "on",
        },
        follow=True,
    )

    assert response.status_code == 200
    assert HierarquiaPermissoes.objects.filter(
        usuario_superior=pastor_local,
        usuario_subordinado=alvo,
        nivel_superior=PASTOR_LOCAL,
        ativo=True,
    ).exists()
