from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group

class EBDFlowTest(TestCase):
    def setUp(self):
        # Importações locais para evitar problemas de import circular
        from configuracao.models import Ministerio, Igreja, AssinaturaMinisterio, Plano
        from django.utils import timezone
        from secretaria.models import Pessoa

        # Cria grupos necessários
        super_group, _ = Group.objects.get_or_create(name='Superintendentes')
        secretaria_group, _ = Group.objects.get_or_create(name='Secretaria EBD')
        superintendente_ebd_group, _ = Group.objects.get_or_create(name='Superintendente EBD')

        # Cria usuários de teste
        self.super_user = User.objects.create_user(username='superintendente', password='senha123')
        self.super_user.groups.add(super_group)
        self.super_user.groups.add(secretaria_group)  # Garante permissão de acesso
        self.super_user.groups.add(superintendente_ebd_group)  # Garante acesso como Superintendente EBD
        self.secretaria_user = User.objects.create_user(username='secretaria', password='senha123')
        self.secretaria_user.groups.add(secretaria_group)
        self.normal_user = User.objects.create_user(username='normal', password='senha123')

        # Cria um plano dummy se não existir
        plano, _ = Plano.objects.get_or_create(codigo_plano='pioneiro', defaults={
            'nome': 'pioneiro',
            'limite_membros': 50,
            'preco_mensal': 0,
            'preco_anual': 0,
        })

        # Cria um ministério ativo e vincula ao super_user
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministério Teste',
            administrador_principal=self.super_user,
            ativo=True
        )

        # Cria uma igreja vinculada ao ministério
        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja Teste',
            tipo_igreja='sede',
            cidade='Cidade Teste',
            estado='SP'
        )

        # Cria assinatura ativa para o ministério
        AssinaturaMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=plano,
            data_inicio=timezone.now(),
            data_fim=timezone.now() + timezone.timedelta(days=30),
            status='ativa',
            ciclo_pagamento='mensal'
        )

        # Cria TipoPessoa padrão para uso obrigatório
        from secretaria.models import TipoPessoa
        tipo_membro, _ = TipoPessoa.objects.get_or_create(nome='Membro', defaults={'descricao': 'Membro padrão'})
        from secretaria.models import StatusPessoa
        status_ativo, _ = StatusPessoa.objects.get_or_create(nome='Ativo', defaults={'descricao': 'Ativo'})

        # Cria Pessoa e vincula ao usuário super_user e à igreja
        self.pessoa_super = Pessoa.objects.create(
            usuario=self.super_user,
            igreja=self.igreja,
            nome='Superintendente Teste',
            tipo_pessoa=tipo_membro,
            status_pessoa=status_ativo,
        )
        self.pessoa_secretaria = Pessoa.objects.create(
            usuario=self.secretaria_user,
            igreja=self.igreja,
            nome='Secretaria Teste',
            tipo_pessoa=tipo_membro,
            status_pessoa=status_ativo,
        )

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
