from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from configuracao.models import Igreja, Ministerio
from secretaria.models import TipoPessoa, StatusPessoa, Membro
from django.utils import timezone

class EventoTemplateLayoutTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='layouttester', password='pass')
        self.ministerio = Ministerio.objects.create(nome_fantasia='Min', administrador_principal=self.user)
        self.igreja = Igreja.objects.create(nome_igreja='Igreja X', ministerio=self.ministerio)
        self.client = Client()
        self.client.login(username='layouttester', password='pass')

        self.tipo = TipoPessoa.objects.create(nome='Membro')
        self.status = StatusPessoa.objects.create(nome='Ativo', considerar_ativo_relatorios=True)
        self.membro = Membro.objects.create(nome='Fulano', igreja=self.igreja, tipo_pessoa=self.tipo, status_pessoa=self.status)

    def test_criar_evento_layout(self):
        url = reverse('eventos:criar_evento')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        # Check the compact row exists: tipo (col-md-3), local (col-md-6), responsavel (col-md-3)
        self.assertIn('col-md-3', content)
        self.assertIn('col-md-6', content)
        self.assertIn('col-md-3', content)
        # Check convidados block present
        self.assertIn('Seleção de convidados', content)

    def test_editar_evento_layout(self):
        # create an event to edit
        from ..models import Evento
        start = timezone.now()
        evento = Evento.objects.create(igreja=self.igreja, titulo='E', data_inicio=start, quantidade_dias=1)
        url = reverse('eventos:editar_evento', args=[evento.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        self.assertIn('col-md-3', content)
        self.assertIn('col-md-6', content)
        self.assertIn('Seleção de convidados', content)
