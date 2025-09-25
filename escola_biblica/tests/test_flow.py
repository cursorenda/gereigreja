from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group

class EBDFlowTest(TestCase):
    def setUp(self):
        # Cria grupos necessários
        super_group, _ = Group.objects.get_or_create(name='Superintendentes')
        secretaria_group, _ = Group.objects.get_or_create(name='Secretaria EBD')
        
        # Cria usuários de teste
        self.super_user = User.objects.create_user(username='superintendente', password='senha123')
        self.super_user.groups.add(super_group)
        self.secretaria_user = User.objects.create_user(username='secretaria', password='senha123')
        self.secretaria_user.groups.add(secretaria_group)
        self.normal_user = User.objects.create_user(username='normal', password='senha123')

    def test_dashboard_access_superintendente(self):
        self.client.login(username='superintendente', password='senha123')
        url = reverse('escola_biblica:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_access_secretaria(self):
        self.client.login(username='secretaria', password='senha123')
        url = reverse('escola_biblica:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_access_denied_for_normal_user(self):
        self.client.login(username='normal', password='senha123')
        url = reverse('escola_biblica:dashboard')
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 403])  # Redireciona ou Forbidden

    def test_aluno_list_access(self):
        self.client.login(username='superintendente', password='senha123')
        url = reverse('escola_biblica:aluno_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cadastros_menu(self):
        self.client.login(username='superintendente', password='senha123')
        url = reverse('escola_biblica:dashboard')
        response = self.client.get(url)
        self.assertContains(response, 'Escola Bíblica Dominical')
        self.assertContains(response, 'Cadastros')
        self.assertContains(response, 'Relatórios')

    # Adicione mais testes para views de cadastro, chamada, transferência, relatórios, etc.
