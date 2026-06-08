import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from configuracao.models import Igreja, Ministerio
from contas.constants import ADMIN_MINISTERIO, MEMBRO_COMUM, SECRETARIO_LOCAL
from contas.page_permissions import pode_acessar_secretaria


@pytest.mark.django_db
def test_admin_acessa_secretaria_na_sede():
    User = get_user_model()
    admin = User.objects.create_user(username='admin_sede', password='senha123')
    Group.objects.get_or_create(name=ADMIN_MINISTERIO)
    admin.groups.add(Group.objects.get(name=ADMIN_MINISTERIO))

    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Sede',
        administrador_principal=admin,
        ativo=True,
        cnpj='11111111000111',
    )
    igreja = Igreja.objects.create(nome_igreja='Igreja Sede', ministerio=ministerio, tipo_igreja='sede')

    assert pode_acessar_secretaria(admin, igreja=igreja)


@pytest.mark.django_db
def test_admin_acessa_secretaria_na_independente():
    User = get_user_model()
    admin = User.objects.create_user(username='admin_independente', password='senha123')
    Group.objects.get_or_create(name=ADMIN_MINISTERIO)
    admin.groups.add(Group.objects.get(name=ADMIN_MINISTERIO))

    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Independente',
        administrador_principal=admin,
        ativo=True,
        cnpj='22222222000122',
    )
    igreja = Igreja.objects.create(nome_igreja='Igreja Independente', ministerio=ministerio, tipo_igreja='independente')

    assert pode_acessar_secretaria(admin, igreja=igreja)


@pytest.mark.django_db
def test_admin_nao_acessa_secretaria_na_regional():
    User = get_user_model()
    admin = User.objects.create_user(username='admin_regional', password='senha123')
    Group.objects.get_or_create(name=ADMIN_MINISTERIO)
    admin.groups.add(Group.objects.get(name=ADMIN_MINISTERIO))

    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Regional',
        administrador_principal=admin,
        ativo=True,
        cnpj='33333333000133',
    )
    igreja = Igreja.objects.create(nome_igreja='Igreja Regional', ministerio=ministerio, tipo_igreja='regional')

    assert not pode_acessar_secretaria(admin, igreja=igreja)


@pytest.mark.django_db
def test_admin_nao_acessa_secretaria_na_congregacao():
    User = get_user_model()
    admin = User.objects.create_user(username='admin_congregacao', password='senha123')
    Group.objects.get_or_create(name=ADMIN_MINISTERIO)
    admin.groups.add(Group.objects.get(name=ADMIN_MINISTERIO))

    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Congregacao',
        administrador_principal=admin,
        ativo=True,
        cnpj='44444444000144',
    )
    igreja = Igreja.objects.create(nome_igreja='Igreja Congregacao', ministerio=ministerio, tipo_igreja='congregacao')

    assert not pode_acessar_secretaria(admin, igreja=igreja)


@pytest.mark.django_db
def test_secretario_local_sempre_acessa_secretaria():
    User = get_user_model()
    secretario = User.objects.create_user(username='secretario_local', password='senha123')
    Group.objects.get_or_create(name=SECRETARIO_LOCAL)
    secretario.groups.add(Group.objects.get(name=SECRETARIO_LOCAL))

    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Secretario',
        administrador_principal=secretario,
        ativo=True,
        cnpj='55555555000155',
    )
    igreja = Igreja.objects.create(nome_igreja='Igreja Regional Secretario', ministerio=ministerio, tipo_igreja='regional')

    assert pode_acessar_secretaria(secretario)
    assert pode_acessar_secretaria(secretario, igreja=igreja)


@pytest.mark.django_db
def test_usuario_comum_nunca_acessa_secretaria():
    User = get_user_model()
    dono_ministerio = User.objects.create_user(username='dono_ministerio_comum', password='senha123')
    comum = User.objects.create_user(username='usuario_comum_secretaria', password='senha123')
    Group.objects.get_or_create(name=MEMBRO_COMUM)
    comum.groups.add(Group.objects.get(name=MEMBRO_COMUM))

    ministerio = Ministerio.objects.create(
        nome_fantasia='Ministerio Comum',
        administrador_principal=dono_ministerio,
        ativo=True,
        cnpj='66666666000166',
    )
    igreja = Igreja.objects.create(nome_igreja='Igreja Sede Comum', ministerio=ministerio, tipo_igreja='sede')

    assert not pode_acessar_secretaria(comum)
    assert not pode_acessar_secretaria(comum, igreja=igreja)
