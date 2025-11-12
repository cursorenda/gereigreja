from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

from configuracao.models import Ministerio, Igreja, PerfilUsuario
from secretaria.models import TipoPessoa, StatusPessoa, Membro, PresencaVisitanteEvento
from eventos.models import Evento


class VisitantePresencaFlowTest(TestCase):
    def setUp(self):
        User = get_user_model()
        # Create two users: one admin owner for the ministerio and one operator
        self.admin_user = User.objects.create_user(username='min_admin', email='admin@example.com', password='pass')
        self.test_user = User.objects.create_user(username='operator', email='op@example.com', password='pass')

        # Create Ministerio and Igreja
        self.ministerio = Ministerio.objects.create(nome_fantasia='TestMin', administrador_principal=self.admin_user, ativo=True)
        self.igreja = Igreja.objects.create(ministerio=self.ministerio, nome_igreja='Igreja Test', tipo_igreja='congregacao')

        # Create PerfilUsuario for test_user and allow access to igreja
        perfil = PerfilUsuario.objects.create(user=self.test_user, ministerio=self.ministerio)
        perfil.igrejas_permitidas.add(self.igreja)

        # Ensure test_user has a group that grants permission (Admin Ministerio)
        group, _ = Group.objects.get_or_create(name='Admin Ministerio')
        self.test_user.groups.add(group)

        # Create TipoPessoa 'Visitante' and StatusPessoa 'Ativo'
        self.tipo_visitante, _ = TipoPessoa.objects.get_or_create(nome='Visitante')
        self.status_ativo, _ = StatusPessoa.objects.get_or_create(nome='Ativo')

        # Create an Evento in the igreja
        now = timezone.now()
        self.evento = Evento.objects.create(igreja=self.igreja, titulo='Culto Teste', data_inicio=now, data_fim=now, criado_por=self.test_user)

        self.client = Client()
        self.client.login(username='operator', password='pass')

    def test_criar_visitante_e_registrar_presenca(self):
        # Create visitante via AJAX POST
        payload = {'nome': 'Teste Visitante TC', 'apelido': 'TCT'}
        response = self.client.post('/sistema/visitantes/criar-parcial/', payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200, msg=f'Create visitante status unexpected: {response.content[:200]}')
        data = response.json()
        self.assertIn('visitante', data)
        visitante = data['visitante']
        visitante_id = visitante.get('id') or visitante.get('chave')

        # Now register presence via AJAX
        pres_payload = {'evento': str(self.evento.pk), 'membro': str(visitante_id)}
        resp2 = self.client.post('/sistema/visitantes/ajax-registrar-presenca-evento/', pres_payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp2.status_code, 200, msg=f'Presença status unexpected: {resp2.content[:200]}')
        data2 = resp2.json()
        self.assertIn('presenca', data2)

        # Verify presence exists in DB
        presencas = PresencaVisitanteEvento.objects.filter(evento=self.evento, membro__pk=visitante_id)
        self.assertTrue(presencas.exists())
