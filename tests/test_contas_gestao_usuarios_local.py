import pytest
from django.contrib.auth.models import Group, User
from django.core import mail
from django.urls import reverse

from configuracao.models import Igreja, Ministerio, PerfilUsuario
from contas.constants import PASTOR_LOCAL, SECRETARIO_LOCAL


@pytest.fixture
def cenario_usuarios_local(db):
    admin = User.objects.create_user(username='admin_min', password='123456')
    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Teste',
        administrador_principal=admin,
        ativo=True,
    )

    PerfilUsuario.objects.create(user=admin, ministerio=ministerio)

    igreja_local = Igreja.objects.create(
        ministerio=ministerio,
        nome_igreja='Igreja Local A',
        tipo_igreja='congregacao',
    )
    igreja_outra = Igreja.objects.create(
        ministerio=ministerio,
        nome_igreja='Igreja Local B',
        tipo_igreja='congregacao',
    )

    secretario_local = User.objects.create_user(username='secretario_local', password='123456')
    perfil_secretario = PerfilUsuario.objects.create(user=secretario_local, ministerio=ministerio)
    perfil_secretario.igrejas_permitidas.add(igreja_local)

    grupo_secretario, _ = Group.objects.get_or_create(name=SECRETARIO_LOCAL)
    secretario_local.groups.add(grupo_secretario)

    return {
        'ministerio': ministerio,
        'igreja_local': igreja_local,
        'igreja_outra': igreja_outra,
        'secretario_local': secretario_local,
    }


def _criar_usuario_com_perfil(ministerio, igreja, username):
    usuario = User.objects.create_user(username=username, password='123456', email=f'{username}@teste.com')
    perfil = PerfilUsuario.objects.create(user=usuario, ministerio=ministerio)
    perfil.igrejas_permitidas.add(igreja)
    return usuario


@pytest.mark.django_db
def test_lista_usuarios_org_filtra_por_igreja_do_operador(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    igreja_local = cenario_usuarios_local['igreja_local']
    igreja_outra = cenario_usuarios_local['igreja_outra']
    secretario_local = cenario_usuarios_local['secretario_local']

    usuario_mesma_igreja = _criar_usuario_com_perfil(ministerio, igreja_local, 'usuario_local')
    usuario_outra_igreja = _criar_usuario_com_perfil(ministerio, igreja_outra, 'usuario_outra')

    client.force_login(secretario_local)
    response = client.get(reverse('contas:lista_usuarios'))

    assert response.status_code == 200
    html = response.content.decode('utf-8')
    assert usuario_mesma_igreja.username in html
    assert usuario_outra_igreja.username not in html


@pytest.mark.django_db
def test_secretario_local_nao_edita_usuario_superior(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    igreja_local = cenario_usuarios_local['igreja_local']
    secretario_local = cenario_usuarios_local['secretario_local']

    pastor_local = _criar_usuario_com_perfil(ministerio, igreja_local, 'pastor_local_alvo')
    grupo_pastor, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
    pastor_local.groups.add(grupo_pastor)

    client.force_login(secretario_local)
    response = client.post(
        reverse('contas:editar_papeis_usuario', args=[pastor_local.pk]),
        {'grupos': [], 'igrejas_permitidas': [igreja_local.pk]},
        follow=True,
    )

    pastor_local.refresh_from_db()
    assert response.status_code == 200
    assert pastor_local.groups.filter(name=PASTOR_LOCAL).exists()


@pytest.mark.django_db
def test_secretario_local_envia_reset_apenas_para_usuario_no_seu_escopo(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    igreja_local = cenario_usuarios_local['igreja_local']
    igreja_outra = cenario_usuarios_local['igreja_outra']
    secretario_local = cenario_usuarios_local['secretario_local']

    usuario_local = _criar_usuario_com_perfil(ministerio, igreja_local, 'alvo_reset_local')
    usuario_fora_escopo = _criar_usuario_com_perfil(ministerio, igreja_outra, 'alvo_reset_fora')

    client.force_login(secretario_local)

    response_ok = client.get(reverse('contas:enviar_link_reset_senha', args=[usuario_local.pk]))
    assert response_ok.status_code == 302
    assert len(mail.outbox) == 1
    assert usuario_local.email in mail.outbox[0].to

    response_fora = client.get(reverse('contas:enviar_link_reset_senha', args=[usuario_fora_escopo.pk]))
    assert response_fora.status_code == 404


@pytest.mark.django_db
def test_secretario_local_alterna_status_no_seu_escopo(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    igreja_local = cenario_usuarios_local['igreja_local']
    secretario_local = cenario_usuarios_local['secretario_local']

    usuario_local = _criar_usuario_com_perfil(ministerio, igreja_local, 'alvo_status_local')
    assert usuario_local.is_active is True

    client.force_login(secretario_local)
    response = client.post(reverse('contas:alternar_status_usuario', args=[usuario_local.pk]), follow=True)

    usuario_local.refresh_from_db()
    assert response.status_code == 200
    assert usuario_local.is_active is False


@pytest.mark.django_db
def test_secretario_local_nao_altera_status_fora_do_escopo(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    igreja_outra = cenario_usuarios_local['igreja_outra']
    secretario_local = cenario_usuarios_local['secretario_local']

    usuario_fora_escopo = _criar_usuario_com_perfil(ministerio, igreja_outra, 'alvo_status_fora')
    assert usuario_fora_escopo.is_active is True

    client.force_login(secretario_local)
    response = client.post(reverse('contas:alternar_status_usuario', args=[usuario_fora_escopo.pk]))

    usuario_fora_escopo.refresh_from_db()
    assert response.status_code == 404
    assert usuario_fora_escopo.is_active is True
