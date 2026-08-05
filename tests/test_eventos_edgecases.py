from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from configuracao.models import Igreja, Ministerio, PerfilUsuario
from secretaria.models import TipoPessoa, StatusPessoa, Membro
from django.contrib.auth import get_user_model

from eventos.models import Evento, EventoSessao, ParticipacaoEvento


class EventoEdgeCasesTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tester2', password='pass')
        self.ministerio = Ministerio.objects.create(nome_fantasia='Min Teste 2', administrador_principal=self.user)
        self.igreja = Igreja.objects.create(nome_igreja='Igreja Teste 2', ministerio=self.ministerio)

        # Cria perfil do usuário
        PerfilUsuario.objects.create(user=self.user, ministerio=self.ministerio)

        self.tipo_membro = TipoPessoa.objects.create(nome='Membro')
        self.status_ativo = StatusPessoa.objects.create(nome='Ativo')

        self.membro = Membro.objects.create(nome='Beltrano', igreja=self.igreja, tipo_pessoa=self.tipo_membro, status_pessoa=self.status_ativo)

        # Adiciona o usuário ao grupo Tesoureiro
        from django.contrib.auth.models import Group
        grupo, _ = Group.objects.get_or_create(name='Tesoureiro')
        self.user.groups.add(grupo)

        self.client = Client()
        self.client.login(username='tester2', password='pass')

    def test_single_day_event_behaviour(self):
        """Evento com quantidade_dias=1 deve criar exatamente 1 sessao e permitir marcar presença."""
        start = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
        evento = Evento.objects.create(igreja=self.igreja, titulo='Evento 1 dia', data_inicio=start, quantidade_dias=1)

        sessoes = list(EventoSessao.objects.filter(evento=evento))
        self.assertEqual(len(sessoes), 1)

        url = reverse('eventos:marcar_presenca', args=[evento.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_event_with_only_email_guests(self):
        """Evento sem membros cadastrados, apenas convidados por email devem permitir participacao por email."""
        start = timezone.now()
        evento = Evento.objects.create(igreja=self.igreja, titulo='Evento convidados email', data_inicio=start, quantidade_dias=1)
        # Simule convidados via campo 'convidados_emails' se existente no model ou use criação direta de ParticipacaoEvento com convidado_email
        pe = ParticipacaoEvento.objects.create(evento=evento, convidado_email='visitante@example.com')
        self.assertEqual(pe.convidado_email, 'visitante@example.com')

    def test_mark_presence_for_email_guest(self):
        """Marcar presença para convidado via email deve criar/atualizar participacao com status PRESENTE."""
        start = timezone.now()
        evento = Evento.objects.create(igreja=self.igreja, titulo='Evento convidados email 2', data_inicio=start, quantidade_dias=2)
        sessoes = list(EventoSessao.objects.filter(evento=evento))
        sessao1 = sessoes[0]

        # Cria participacao por email para sessao1
        pe = ParticipacaoEvento.objects.create(evento=evento, sessao=sessao1, convidado_email='guest2@example.com')
        self.assertEqual(pe.sessao, sessao1)
        self.assertEqual(pe.convidado_email, 'guest2@example.com')

        url = reverse('eventos:marcar_presenca', args=[evento.pk])
        post_data = {
            'sessao': str(sessao1.pk),
            'presentes': [str(pe.pk)],
        }
        resp = self.client.post(url, post_data, follow=True)
        self.assertEqual(resp.status_code, 200)

        pe.refresh_from_db()
        self.assertEqual(pe.status, 'PRESENTE')

    def test_marking_session_does_not_affect_other_sessions(self):
        """Marcar presente em sessão A não deve mudar presença em sessão B."""
        start = timezone.now()
        evento = Evento.objects.create(igreja=self.igreja, titulo='Evento 3 dias', data_inicio=start, quantidade_dias=3)
        sessoes = list(EventoSessao.objects.filter(evento=evento).order_by('numero'))
        s1, s2, s3 = sessoes

        # Garantir participacoes criadas para os membros
        url = reverse('eventos:marcar_presenca', args=[evento.pk])
        # Gera participacoes para sessao 1 e 2 via GET
        self.client.get(f"{url}?sessao={s1.pk}")
        self.client.get(f"{url}?sessao={s2.pk}")

        pe_s1 = ParticipacaoEvento.objects.filter(evento=evento, sessao=s1, membro=self.membro).first()
        pe_s2 = ParticipacaoEvento.objects.filter(evento=evento, sessao=s2, membro=self.membro).first()
        self.assertIsNotNone(pe_s1)
        self.assertIsNotNone(pe_s2)

        # Marca presente apenas na sessao 1
        post_data = {'sessao': str(s1.pk), 'presentes': [str(pe_s1.pk)]}
        resp = self.client.post(url, post_data, follow=True)
        self.assertEqual(resp.status_code, 200)

        pe_s1.refresh_from_db()
        pe_s2.refresh_from_db()
        self.assertEqual(pe_s1.status, 'PRESENTE')
        # pe_s2 deve continuar com status padrão (não presente)
        self.assertNotEqual(pe_s2.status, 'PRESENTE')
