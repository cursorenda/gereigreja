from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse

class AdminMinisterioSemMembroTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Cria grupo Admin Ministerio
        self.admin_group, _ = Group.objects.get_or_create(name="Admin Ministerio")
        # Cria usuário sem membro vinculado
        self.user = User.objects.create_user(username="testeabril", email="testeabril@gmail.com", password="123456")
        self.user.groups.add(self.admin_group)
        self.user.save()

    def test_admin_ministerio_acessa_portal_sem_membro(self):
        self.client.login(username="testeabril", password="123456")
        # A URL abaixo deve ser ajustada para a view que faz a checagem
        response = self.client.get(reverse("secretaria:portal"))
        # Não deve redirecionar para editar perfil
        self.assertNotIn("cadastro de membro não foi encontrado", response.content.decode().lower())
        self.assertEqual(response.status_code, 200)
        # O usuário deve conseguir acessar normalmente
        self.assertIn("Meu Portal", response.content.decode())
