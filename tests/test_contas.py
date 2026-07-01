from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from configuracao.models import Igreja, Ministerio, Plano


class RegistroUsuarioOrganizacaoTest(TestCase):
	def setUp(self):
		self.plano_pioneiro = Plano.objects.create(
			nome='pioneiro',
			codigo_plano='pioneiro',
			ativo=True,
			limite_membros=50,
			limite_igrejas=1,
		)

	def test_registro_redireciona_para_edicao_da_igreja_auto_criada(self):
		response = self.client.post(
			reverse('contas:registrar'),
			{
				'primeiro_nome': 'Joao',
				'ultimo_nome': 'Silva',
				'email': 'joao@example.com',
				'senha': 'Senha123!@#',
				'confirmar_senha': 'Senha123!@#',
				'nome_fantasia_org': 'Ministério Teste',
				'aceito_termos': 'on',
			},
		)

		self.assertEqual(response.status_code, 302)

		usuario = User.objects.get(username='joao@example.com')
		ministerio = Ministerio.objects.get(administrador_principal=usuario)
		igreja = Igreja.objects.filter(ministerio=ministerio).order_by('id').first()

		self.assertIsNotNone(igreja)
		self.assertEqual(response.url, reverse('configuracao:editar_igreja_config', args=[igreja.id]))
