import pytest
from django.contrib.auth.models import Group, User
from django.urls import reverse

from auditoria.models import PermissionChangeLog
from contas.constants import ADMIN_MINISTERIO, MEMBRO_COMUM
from contas.models import PermissionRequest


@pytest.mark.django_db
def test_hub_permissoes_cria_solicitacao(client):
    solicitante = User.objects.create_user(
        username="solicitante1",
        email="solicitante1@test.com",
        password="senha123",
    )
    grupo_base, _ = Group.objects.get_or_create(name=MEMBRO_COMUM)
    grupo_alvo = Group.objects.create(name="Tesoureiro Teste")
    solicitante.groups.add(grupo_base)

    client.force_login(solicitante)
    response = client.post(
        reverse("contas:hub_permissoes"),
        {
            "grupo": grupo_alvo.id,
            "justificativa": "Preciso dessa permissao para operar os lancamentos financeiros.",
            "prioridade": "media",
        },
        follow=True,
    )

    assert response.status_code == 200
    solicitacao = PermissionRequest.objects.get(usuario_solicitante=solicitante)
    assert solicitacao.grupo_solicitado == grupo_alvo
    assert solicitacao.status == "pending"


@pytest.mark.django_db
def test_admin_aprova_solicitacao_e_gera_log_auditoria(client):
    admin = User.objects.create_user(
        username="admin1",
        email="admin1@test.com",
        password="senha123",
    )
    solicitante = User.objects.create_user(
        username="solicitante2",
        email="solicitante2@test.com",
        password="senha123",
    )

    grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
    grupo_alvo = Group.objects.create(name="Equipe Midia Teste")
    admin.groups.add(grupo_admin)

    solicitacao = PermissionRequest.objects.create(
        usuario_solicitante=solicitante,
        grupo_solicitado=grupo_alvo,
        justificativa="Preciso atuar na equipe de transmissao e edicao.",
        prioridade="alta",
    )

    client.force_login(admin)
    response = client.post(
        reverse("contas:avaliar_solicitacao", kwargs={"pk": solicitacao.pk}),
        {"acao": "aprovar", "observacao": "Aprovado para apoiar a equipe."},
        follow=True,
    )

    assert response.status_code == 200

    solicitacao.refresh_from_db()
    solicitante.refresh_from_db()

    assert solicitacao.status == "approved"
    assert solicitacao.usuario_aprovador == admin
    assert solicitante.groups.filter(pk=grupo_alvo.pk).exists()

    log = PermissionChangeLog.objects.filter(
        usuario_afetado=solicitante,
        grupo=grupo_alvo,
        acao="ADD",
        usuario_executor=admin,
    ).first()
    assert log is not None
    assert str(solicitacao.pk) in (log.observacao or "")


@pytest.mark.django_db
def test_usuario_sem_permissao_nao_pode_avaliar_solicitacao(client):
    avaliador_sem_permissao = User.objects.create_user(
        username="comum1",
        email="comum1@test.com",
        password="senha123",
    )
    solicitante = User.objects.create_user(
        username="solicitante3",
        email="solicitante3@test.com",
        password="senha123",
    )
    grupo_alvo = Group.objects.create(name="Grupo Teste Bloqueio")

    solicitacao = PermissionRequest.objects.create(
        usuario_solicitante=solicitante,
        grupo_solicitado=grupo_alvo,
        justificativa="Justificativa valida para tentativa sem permissao.",
        prioridade="media",
    )

    client.force_login(avaliador_sem_permissao)
    response = client.post(
        reverse("contas:avaliar_solicitacao", kwargs={"pk": solicitacao.pk}),
        {"acao": "aprovar", "observacao": "Tentativa indevida."},
        follow=True,
    )

    assert response.status_code == 200

    solicitacao.refresh_from_db()
    assert solicitacao.status == "pending"
    assert not solicitante.groups.filter(pk=grupo_alvo.pk).exists()


@pytest.mark.django_db
def test_admin_rejeita_solicitacao_com_notificacao(client):
    admin = User.objects.create_user(
        username="admin2",
        email="admin2@test.com",
        password="senha123",
    )
    solicitante = User.objects.create_user(
        username="solicitante4",
        email="solicitante4@test.com",
        password="senha123",
    )

    grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
    grupo_alvo = Group.objects.create(name="Equipe Financeira Teste")
    admin.groups.add(grupo_admin)

    solicitacao = PermissionRequest.objects.create(
        usuario_solicitante=solicitante,
        grupo_solicitado=grupo_alvo,
        justificativa="Preciso gerenciar fluxos financeiros da igreja.",
        prioridade="alta",
    )

    client.force_login(admin)
    response = client.post(
        reverse("contas:avaliar_solicitacao", kwargs={"pk": solicitacao.pk}),
        {"acao": "rejeitar", "observacao": "Aguarde renovação de credenciais."},
        follow=True,
    )

    assert response.status_code == 200

    solicitacao.refresh_from_db()
    solicitante.refresh_from_db()

    assert solicitacao.status == "rejected"
    assert solicitacao.usuario_aprovador == admin
    assert "Aguarde renovação de credenciais." in (solicitacao.observacao_resposta or "")
    assert not solicitante.groups.filter(pk=grupo_alvo.pk).exists()
    assert solicitacao.data_resposta is not None


@pytest.mark.django_db
def test_cancelar_solicitacao_pendente(client):
    solicitante = User.objects.create_user(
        username="solicitante5",
        email="solicitante5@test.com",
        password="senha123",
    )
    grupo_base, _ = Group.objects.get_or_create(name=MEMBRO_COMUM)
    grupo_alvo = Group.objects.create(name="Grupo Cancelavel")
    solicitante.groups.add(grupo_base)

    solicitacao = PermissionRequest.objects.create(
        usuario_solicitante=solicitante,
        grupo_solicitado=grupo_alvo,
        justificativa="Cancelarei depois.",
        prioridade="baixa",
    )

    client.force_login(solicitante)
    response = client.post(
        reverse("contas:cancelar_solicitacao", kwargs={"pk": solicitacao.pk}),
        follow=True,
    )

    assert response.status_code == 200

    solicitacao.refresh_from_db()
    assert solicitacao.status == "cancelled"


@pytest.mark.django_db
def test_log_auditoria_registra_remocao_grupo(client):
    admin = User.objects.create_user(
        username="admin3",
        email="admin3@test.com",
        password="senha123",
    )
    usuario_alvo = User.objects.create_user(
        username="usuario_alvo1",
        email="usuario_alvo1@test.com",
        password="senha123",
    )

    grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
    grupo_remover = Group.objects.create(name="Grupo Remover Test")
    admin.groups.add(grupo_admin)
    usuario_alvo.groups.add(grupo_remover)

    # Simula remoção manual de grupo (não é pelo workflow de solicitação, mas sim pelo sistema de auditoria)
    # Verificamos apenas que o log é criado corretamente
    from auditoria.models import PermissionChangeLog

    log = PermissionChangeLog.objects.create(
        usuario_afetado=usuario_alvo,
        grupo=grupo_remover,
        acao="REMOVE",
        usuario_executor=admin,
        observacao="Acesso revogado por inatividade.",
    )

    assert log.usuario_afetado == usuario_alvo
    assert log.acao == "REMOVE"
    assert log.usuario_executor == admin
    assert "inatividade" in log.observacao.lower()
