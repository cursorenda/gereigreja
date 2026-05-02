import pytest
from django.urls import reverse
from django.contrib.auth.models import User, Group
from contas.constants import TESOUREIRO, EQUIPE_EVENTOS

@pytest.mark.django_db
def test_usuario_multiplos_grupos(client):
    """
    Testa se um usuário com múltiplos grupos acessa views do grupo de maior privilégio.
    """
    user = User.objects.create_user('multi@teste.com', password='123')
    group1 = Group.objects.get(name=TESOUREIRO)
    group2 = Group.objects.get(name=EQUIPE_EVENTOS)
    user.groups.add(group1, group2)
    user.is_staff = True
    user.save()
    client.login(username='multi@teste.com', password='123')
    url = reverse('financeiro:alguma_view_restrita')
    resp = client.get(url)
    assert resp.status_code == 200  # Deve acessar pois é Tesoureiro
