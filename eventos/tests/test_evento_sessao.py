from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from configuracao.models import Igreja, Ministerio, PerfilUsuario
from secretaria.models import TipoPessoa, StatusPessoa, Membro
from django.contrib.auth import get_user_model

from eventos.models import Evento, EventoSessao, ParticipacaoEvento


class EventoSessaoPresenceTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pass')
        # Create a Ministerio required by Igreja (ministerio is non-nullable)
        # Ministerio expects 'nome_fantasia' and a required administrador_principal
        self.ministerio = Ministerio.objects.create(nome_fantasia='Ministerio Teste', administrador_principal=self.user)
        self.igreja = Igreja.objects.create(nome_igreja='Igreja Teste', ministerio=self.ministerio)

        # Cria perfil do usuário
        PerfilUsuario.objects.create(user=self.user, ministerio=self.ministerio)

        # Tipo e status necessários
        self.tipo_membro = TipoPessoa.objects.create(nome='Membro')
        self.status_ativo = StatusPessoa.objects.create(nome='Ativo')

        # Create a member
        self.membro = Membro.objects.create(nome='Fulano', igreja=self.igreja, tipo_pessoa=self.tipo_membro, status_pessoa=self.status_ativo)

        # Adiciona o usuário ao grupo Tesoureiro
        from django.contrib.auth.models import Group
        grupo, _ = Group.objects.get_or_create(name='Tesoureiro')
        self.user.groups.add(grupo)

        self.client = Client()
        self.client.login(username='tester', password='pass')

    def test_evento_with_three_days_creates_sessions_and_marks_presence_per_session(self):
        start = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
        evento = Evento.objects.create(
            igreja=self.igreja,
            titulo='Retiro Teste',
            data_inicio=start,
            quantidade_dias=3,
        )

        # Post-save signal should create 3 sessions
        sessoes = list(EventoSessao.objects.filter(evento=evento).order_by('numero'))
        self.assertEqual(len(sessoes), 3)

        # Access marcar_presenca (GET) -> should return first session by default
        url = reverse('eventos:marcar_presenca', args=[evento.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('sessoes', resp.context)
        sessao_default = resp.context['sessao']
        self.assertEqual(sessao_default.numero, 1)

        # Now POST marking the member present for session 2
        sessao2 = sessoes[1]
        # First, GET partecipacoes for session2 to trigger creation
        resp2 = self.client.get(f"{url}?sessao={sessao2.pk}")
        self.assertEqual(resp2.status_code, 200)

        # Find the participacao created
        pe_qs = ParticipacaoEvento.objects.filter(evento=evento, sessao=sessao2, membro=self.membro)
        self.assertTrue(pe_qs.exists(), 'Participacao should have been created for session 2')
        pe = pe_qs.first()

        post_data = {
            'sessao': str(sessao2.pk),
            'presentes': [str(self.membro.chave)],
        }
        resp_post = self.client.post(url, post_data, follow=True)
        self.assertEqual(resp_post.status_code, 200)

        pe.refresh_from_db()
        self.assertEqual(pe.status, 'PRESENTE')
        self.assertEqual(pe.sessao, sessao2)
