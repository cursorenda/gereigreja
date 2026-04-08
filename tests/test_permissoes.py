import pytest
from django.contrib.auth.models import User, Group
from contas.constants import (
    user_tem_grupo, user_tem_qualquer_grupo, ADMIN_MINISTERIO, PASTOR_LOCAL, MEMBRO_COMUM
)

@pytest.mark.django_db
def test_user_tem_grupo_true():
    user = User.objects.create_user('teste')
    grupo = Group.objects.create(name=ADMIN_MINISTERIO)
    user.groups.add(grupo)
    assert user_tem_grupo(user, ADMIN_MINISTERIO) is True

@pytest.mark.django_db
def test_user_tem_grupo_false():
    user = User.objects.create_user('teste2')
    assert user_tem_grupo(user, ADMIN_MINISTERIO) is False

@pytest.mark.django_db
def test_user_tem_qualquer_grupo_true():
    user = User.objects.create_user('teste3')
    grupo1 = Group.objects.create(name=PASTOR_LOCAL)
    grupo2 = Group.objects.create(name=MEMBRO_COMUM)
    user.groups.add(grupo2)
    assert user_tem_qualquer_grupo(user, [PASTOR_LOCAL, MEMBRO_COMUM]) is True

@pytest.mark.django_db
def test_user_tem_qualquer_grupo_false():
    user = User.objects.create_user('teste4')
    grupo1 = Group.objects.create(name=PASTOR_LOCAL)
    assert user_tem_qualquer_grupo(user, [PASTOR_LOCAL, MEMBRO_COMUM]) is False
