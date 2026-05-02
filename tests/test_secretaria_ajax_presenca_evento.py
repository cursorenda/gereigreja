from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from django.contrib.auth import get_user_model

from configuracao.models import Ministerio, Igreja
from secretaria.models import TipoPessoa, StatusPessoa, Membro, PresencaVisitanteEvento
from eventos.models import Evento


class AjaxRegistrarPresencaEventoTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pw')
        # criar ministerio e igreja
        self.ministerio = Ministerio.objects.create(nome_fantasia='MinTest', administrador_principal=self.user)
        self.igreja = Igreja.objects.create(ministerio=self.ministerio, nome_igreja='Igreja Teste')

        # tipos e status necessários
        self.tipo_visitante = TipoPessoa.objects.create(nome='Visitante')
        self.status_ativo = StatusPessoa.objects.create(nome='Ativo')

        # criar evento
        self.evento = Evento.objects.create(
            igreja=self.igreja,
            titulo='Culto Teste',
            data_inicio=timezone.now(),
            criado_por=self.user,
        )

        # criar membro (visitante)
        self.membro = Membro.objects.create(
            igreja=self.igreja,
            nome='Fulano de Teste',
            tipo_pessoa=self.tipo_visitante,
            status_pessoa=self.status_ativo,
        )

    def test_ajax_registrar_presenca_evento_creates_presence_and_returns_json(self):
        self.client.force_login(self.user)
        url = reverse('secretaria:ajax_registrar_presenca_evento')
        resp = self.client.post(url, {'evento': self.evento.pk, 'membro': self.membro.pk})
        self.assertEqual(resp.status_code, 200, msg=f'Response content: {resp.content!r}')
        data = resp.json()
        # Response should include presenca and presenca_html
        self.assertIn('presenca', data)
        self.assertIn('presenca_html', data)
        pres = data['presenca']
        self.assertEqual(pres.get('nome'), self.membro.nome)
        # apelido may be empty string
        self.assertIn('apelido', pres)

        # Check DB record
        exists = PresencaVisitanteEvento.objects.filter(membro=self.membro, evento=self.evento).exists()
        self.assertTrue(exists, msg='Presença não foi criada no banco de dados')
