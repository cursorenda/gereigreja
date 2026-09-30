import pytest
from django.contrib.auth.models import Group, User
from django.contrib.messages import get_messages
from django.conf import settings
from django.core import mail
from django.test import Client
from django.urls import reverse
from unittest.mock import patch

from configuracao.models import Igreja, Ministerio, PerfilUsuario
from contas.constants import MEMBRO_COMUM, PASTOR_LOCAL, SECRETARIO_LOCAL
from contas.models import Convite
from core.email_services import ResultadoEnvioEmail, StatusEnvioEmail


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


def _resultado_email(status, backend_chamado, resultado_backend):
    return ResultadoEnvioEmail(
        status=status,
        backend_chamado=backend_chamado,
        resultado_backend=resultado_backend,
    )


def _mensagens(response):
    return [str(message) for message in get_messages(response.wsgi_request)]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('resultado', 'mensagem_esperada', 'classe_mensagem'),
    [
        (
            _resultado_email(StatusEnvioEmail.ENVIADO, True, 1),
            'Convite enviado com sucesso para convidado@teste.com!',
            'success',
        ),
        (
            _resultado_email(StatusEnvioEmail.NEUTRALIZADO_DEMO, False, None),
            'Convite criado para convidado@teste.com, mas o envio externo está desabilitado no ambiente Demo.',
            'warning',
        ),
        (
            _resultado_email(StatusEnvioEmail.NAO_ENVIADO, True, 0),
            'Convite criado para convidado@teste.com, mas o e-mail não foi enviado.',
            'warning',
        ),
    ],
)
def test_enviar_convite_trata_resultado_do_wrapper_sem_expor_token(
    client,
    cenario_usuarios_local,
    resultado,
    mensagem_esperada,
    classe_mensagem,
):
    ministerio = cenario_usuarios_local['ministerio']
    secretario_local = cenario_usuarios_local['secretario_local']
    client.force_login(secretario_local)

    with patch('contas.views.enviar_email_seguro', return_value=resultado) as enviar_email:
        response = client.post(reverse('contas:enviar_convite'), {'email_convidado': 'convidado@teste.com'})

    convite = Convite.objects.get(email_convidado='convidado@teste.com', ministerio=ministerio)
    mensagens = _mensagens(response)

    assert response.status_code == 302
    assert convite.status == 'pendente'
    assert mensagem_esperada in mensagens
    assert str(convite.token) not in ' '.join(mensagens)
    assert ('success' if resultado.status == StatusEnvioEmail.ENVIADO else 'warning') == classe_mensagem
    enviar_email.assert_called_once_with(
        'Convite para se juntar à ministério Ministerio Teste',
        enviar_email.call_args.args[1],
        ['convidado@teste.com'],
        ministerio=ministerio,
        html_message=enviar_email.call_args.args[1],
        from_email=settings.DEFAULT_FROM_EMAIL,
        fail_silently=False,
    )


@pytest.mark.django_db
def test_enviar_convite_preserva_convite_pendente_quando_wrapper_falha(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    secretario_local = cenario_usuarios_local['secretario_local']
    client.force_login(secretario_local)

    with patch('contas.views.enviar_email_seguro', side_effect=RuntimeError('falha de transporte')):
        response = client.post(reverse('contas:enviar_convite'), {'email_convidado': 'falha@teste.com'})

    convite = Convite.objects.get(email_convidado='falha@teste.com', ministerio=ministerio)
    mensagens = _mensagens(response)

    assert response.status_code == 302
    assert convite.status == 'pendente'
    assert 'Convite criado para falha@teste.com, mas ocorreu um erro ao enviar o e-mail.' in mensagens
    assert str(convite.token) not in ' '.join(mensagens)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('resultado', 'mensagem_esperada'),
    [
        (
            _resultado_email(StatusEnvioEmail.ENVIADO, True, 1),
            'Convite reenviado com sucesso para convidado@teste.com!',
        ),
        (
            _resultado_email(StatusEnvioEmail.NEUTRALIZADO_DEMO, False, None),
            'Convite permanece pendente, mas o reenvio externo está desabilitado no ambiente Demo.',
        ),
        (
            _resultado_email(StatusEnvioEmail.NAO_ENVIADO, True, 0),
            'Convite permanece pendente, mas o e-mail não foi enviado.',
        ),
    ],
)
def test_reenviar_convite_trata_resultado_do_wrapper_sem_mutar_estado(
    client,
    cenario_usuarios_local,
    resultado,
    mensagem_esperada,
):
    ministerio = cenario_usuarios_local['ministerio']
    secretario_local = cenario_usuarios_local['secretario_local']
    convite = Convite.objects.create(
        email_convidado='convidado@teste.com',
        remetente=secretario_local,
        ministerio=ministerio,
        status='pendente',
    )
    token_original = convite.token
    client.force_login(secretario_local)

    with patch('contas.views.enviar_email_seguro', return_value=resultado) as enviar_email:
        response = client.post(reverse('contas:reenviar_convite', args=[convite.pk]))

    convite.refresh_from_db()
    mensagens = _mensagens(response)

    assert response.status_code == 302
    assert convite.status == 'pendente'
    assert convite.token == token_original
    assert mensagem_esperada in mensagens
    assert str(convite.token) not in ' '.join(mensagens)
    enviar_email.assert_called_once_with(
        'Convite para se juntar à ministério Ministerio Teste',
        enviar_email.call_args.args[1],
        ['convidado@teste.com'],
        ministerio=ministerio,
        html_message=enviar_email.call_args.args[1],
        from_email=settings.DEFAULT_FROM_EMAIL,
        fail_silently=False,
    )


@pytest.mark.django_db
def test_reenviar_convite_preserva_estado_quando_wrapper_falha(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    secretario_local = cenario_usuarios_local['secretario_local']
    convite = Convite.objects.create(
        email_convidado='falha@teste.com',
        remetente=secretario_local,
        ministerio=ministerio,
        status='pendente',
    )
    token_original = convite.token
    client.force_login(secretario_local)

    with patch('contas.views.enviar_email_seguro', side_effect=RuntimeError('falha de transporte')):
        response = client.post(reverse('contas:reenviar_convite', args=[convite.pk]))

    convite.refresh_from_db()
    mensagens = _mensagens(response)

    assert response.status_code == 302
    assert convite.status == 'pendente'
    assert convite.token == token_original
    assert 'Não foi possível reenviar o convite. O convite permanece pendente.' in mensagens
    assert str(convite.token) not in ' '.join(mensagens)


@pytest.mark.django_db
def test_reenviar_convite_de_outro_ministerio_retorna_404(client, cenario_usuarios_local):
    secretario_local = cenario_usuarios_local['secretario_local']
    outro_admin = User.objects.create_user(username='admin_outro', password='123456')
    outro_ministerio = Ministerio.objects.create(
        nome_fantasia='Outro Ministério',
        administrador_principal=outro_admin,
        ativo=True,
    )
    convite_outro_ministerio = Convite.objects.create(
        email_convidado='outro@teste.com',
        remetente=outro_admin,
        ministerio=outro_ministerio,
        status='pendente',
    )
    client.force_login(secretario_local)

    response = client.post(reverse('contas:reenviar_convite', args=[convite_outro_ministerio.pk]))

    assert response.status_code == 404


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
def test_reset_senha_get_retorna_405_sem_gerar_token_ou_dispatch(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    igreja_local = cenario_usuarios_local['igreja_local']
    secretario_local = cenario_usuarios_local['secretario_local']
    usuario_local = _criar_usuario_com_perfil(ministerio, igreja_local, 'alvo_reset_local')

    client.force_login(secretario_local)

    with patch('contas.views.default_token_generator.make_token') as make_token, patch(
        'contas.views.enviar_email_seguro'
    ) as enviar_email:
        response = client.get(reverse('contas:enviar_link_reset_senha', args=[usuario_local.pk]))

    assert response.status_code == 405
    assert len(mail.outbox) == 0
    make_token.assert_not_called()
    enviar_email.assert_not_called()


@pytest.mark.django_db
def test_reset_senha_post_enviado_com_ministerio_explicito(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    igreja_local = cenario_usuarios_local['igreja_local']
    secretario_local = cenario_usuarios_local['secretario_local']
    usuario_local = _criar_usuario_com_perfil(ministerio, igreja_local, 'alvo_reset_enviado')
    client.force_login(secretario_local)

    with patch(
        'contas.views.enviar_email_seguro',
        return_value=_resultado_email(StatusEnvioEmail.ENVIADO, True, 1),
    ) as enviar_email:
        response = client.post(reverse('contas:enviar_link_reset_senha', args=[usuario_local.pk]))

    mensagens = _mensagens(response)
    assert response.status_code == 302
    assert f'Link de redefinição de senha enviado com sucesso para {usuario_local.email}.' in mensagens
    enviar_email.assert_called_once_with(
        enviar_email.call_args.args[0],
        enviar_email.call_args.args[1],
        [usuario_local.email],
        ministerio=ministerio,
        from_email=settings.DEFAULT_FROM_EMAIL,
        fail_silently=False,
    )


@pytest.mark.django_db
def test_reset_senha_demo_bloqueia_antes_de_gerar_token_ou_chamar_wrapper(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    igreja_local = cenario_usuarios_local['igreja_local']
    secretario_local = cenario_usuarios_local['secretario_local']
    usuario_local = _criar_usuario_com_perfil(ministerio, igreja_local, 'alvo_reset_demo')
    ministerio.is_demo = True
    ministerio.save(update_fields=['is_demo'])
    client.force_login(secretario_local)

    with patch('contas.views.default_token_generator.make_token') as make_token, patch(
        'contas.views.enviar_email_seguro'
    ) as enviar_email:
        response = client.post(reverse('contas:enviar_link_reset_senha', args=[usuario_local.pk]))

    assert response.status_code == 302
    assert 'O envio de link de redefinição de senha está desabilitado no ambiente Demo.' in _mensagens(response)
    make_token.assert_not_called()
    enviar_email.assert_not_called()


@pytest.mark.django_db
def test_reset_senha_nao_enviado_nao_exibe_sucesso(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    igreja_local = cenario_usuarios_local['igreja_local']
    secretario_local = cenario_usuarios_local['secretario_local']
    usuario_local = _criar_usuario_com_perfil(ministerio, igreja_local, 'alvo_reset_nao_enviado')
    client.force_login(secretario_local)

    with patch(
        'contas.views.enviar_email_seguro',
        return_value=_resultado_email(StatusEnvioEmail.NAO_ENVIADO, True, 0),
    ):
        response = client.post(reverse('contas:enviar_link_reset_senha', args=[usuario_local.pk]))

    mensagens = _mensagens(response)
    assert response.status_code == 302
    assert 'O link de redefinição de senha não foi enviado.' in mensagens
    assert not any('enviado com sucesso' in mensagem for mensagem in mensagens)


@pytest.mark.django_db
def test_reset_senha_excecao_nao_expoe_detalhe_tecnico(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    igreja_local = cenario_usuarios_local['igreja_local']
    secretario_local = cenario_usuarios_local['secretario_local']
    usuario_local = _criar_usuario_com_perfil(ministerio, igreja_local, 'alvo_reset_excecao')
    client.force_login(secretario_local)

    with patch('contas.views.enviar_email_seguro', side_effect=RuntimeError('SEGREDO_TECNICO_TESTE')):
        response = client.post(reverse('contas:enviar_link_reset_senha', args=[usuario_local.pk]))

    mensagens = _mensagens(response)
    assert response.status_code == 302
    assert 'Não foi possível enviar o link de redefinição de senha.' in mensagens
    assert 'SEGREDO_TECNICO_TESTE' not in ' '.join(mensagens)


@pytest.mark.django_db
def test_reset_senha_retorna_404_para_usuario_de_outro_ministerio(client, cenario_usuarios_local):
    secretario_local = cenario_usuarios_local['secretario_local']
    outro_admin = User.objects.create_user(username='admin_reset_outro', password='123456')
    outro_ministerio = Ministerio.objects.create(
        nome_fantasia='Outro Ministério Reset',
        administrador_principal=outro_admin,
        ativo=True,
    )
    PerfilUsuario.objects.create(user=outro_admin, ministerio=outro_ministerio)
    outra_igreja = Igreja.objects.create(
        ministerio=outro_ministerio,
        nome_igreja='Igreja Outro Ministério',
        tipo_igreja='congregacao',
    )
    usuario_outro_ministerio = _criar_usuario_com_perfil(outro_ministerio, outra_igreja, 'alvo_reset_outro')
    client.force_login(secretario_local)

    with patch('contas.views.enviar_email_seguro') as enviar_email:
        response = client.post(reverse('contas:enviar_link_reset_senha', args=[usuario_outro_ministerio.pk]))

    assert response.status_code == 404
    enviar_email.assert_not_called()


@pytest.mark.django_db
def test_reset_senha_bloqueia_usuario_hierarquicamente_superior(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    igreja_local = cenario_usuarios_local['igreja_local']
    secretario_local = cenario_usuarios_local['secretario_local']
    pastor_local = _criar_usuario_com_perfil(ministerio, igreja_local, 'alvo_reset_pastor')
    grupo_pastor, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
    pastor_local.groups.add(grupo_pastor)
    client.force_login(secretario_local)

    with patch('contas.views.enviar_email_seguro') as enviar_email:
        response = client.post(reverse('contas:enviar_link_reset_senha', args=[pastor_local.pk]))

    assert response.status_code == 302
    assert 'Você não pode enviar reset para um usuário com nível hierárquico superior ao seu.' in _mensagens(response)
    enviar_email.assert_not_called()


@pytest.mark.django_db
def test_reset_senha_exige_permissao_de_gerenciamento(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    igreja_local = cenario_usuarios_local['igreja_local']
    usuario_sem_permissao = _criar_usuario_com_perfil(ministerio, igreja_local, 'operador_sem_permissao_reset')
    usuario_alvo = _criar_usuario_com_perfil(ministerio, igreja_local, 'alvo_reset_sem_permissao')
    grupo_membro_comum, _ = Group.objects.get_or_create(name=MEMBRO_COMUM)
    usuario_sem_permissao.groups.add(grupo_membro_comum)
    client.force_login(usuario_sem_permissao)

    with patch('contas.views.enviar_email_seguro') as enviar_email:
        response = client.post(reverse('contas:enviar_link_reset_senha', args=[usuario_alvo.pk]))

    assert response.status_code == 403
    enviar_email.assert_not_called()


@pytest.mark.django_db
def test_reset_senha_post_anonimo_redireciona_para_login(client, cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    igreja_local = cenario_usuarios_local['igreja_local']
    usuario_alvo = _criar_usuario_com_perfil(ministerio, igreja_local, 'alvo_reset_anonimo')

    with patch('contas.views.enviar_email_seguro') as enviar_email:
        response = client.post(reverse('contas:enviar_link_reset_senha', args=[usuario_alvo.pk]))

    assert response.status_code == 302
    assert response.url.startswith(settings.LOGIN_URL)
    enviar_email.assert_not_called()


@pytest.mark.django_db
def test_reset_senha_post_sem_csrf_retorna_403(cenario_usuarios_local):
    ministerio = cenario_usuarios_local['ministerio']
    igreja_local = cenario_usuarios_local['igreja_local']
    secretario_local = cenario_usuarios_local['secretario_local']
    usuario_alvo = _criar_usuario_com_perfil(ministerio, igreja_local, 'alvo_reset_csrf')
    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.force_login(secretario_local)

    with patch('contas.views.enviar_email_seguro') as enviar_email:
        response = csrf_client.post(reverse('contas:enviar_link_reset_senha', args=[usuario_alvo.pk]))

    assert response.status_code == 403
    enviar_email.assert_not_called()


def test_template_reset_senha_usa_botao_post_sem_ancora():
    from pathlib import Path

    template = Path('secretaria/templates/partials/_aba_acesso_sistema.html').read_text(encoding='utf-8-sig')

    assert '<button type="submit" class="btn btn-outline-secondary ms-2"' in template
    assert 'formaction="{% url \'contas:enviar_link_reset_senha\' user_pk=user_associado.pk %}"' in template
    assert 'formmethod="post"' in template
    assert '<a href="{% url \'contas:enviar_link_reset_senha\'' not in template


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
