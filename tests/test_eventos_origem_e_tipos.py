from datetime import datetime, time

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from configuracao.models import Igreja, Ministerio, PerfilUsuario, ProgramacaoPadraoIgreja
from eventos.models import Evento


class EventosOrigemETiposTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='eventos_teste', password='pass123')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Eventos Teste',
            administrador_principal=self.user,
            ativo=True,
        )
        self.igreja = Igreja.objects.create(
            nome_igreja='Igreja Eventos Teste',
            ministerio=self.ministerio,
        )

        self.perfil = PerfilUsuario.objects.create(user=self.user, ministerio=self.ministerio)
        self.perfil.igrejas_permitidas.add(self.igreja)

        grupo, _ = Group.objects.get_or_create(name='Tesoureiro')
        self.user.groups.add(grupo)

        self.client.force_login(self.user)
        session = self.client.session
        session['igreja_ativa_id'] = self.igreja.pk
        session.save()

    def test_criar_evento_form_restringe_tipos_nao_corriqueiros(self):
        response = self.client.get(reverse('eventos:criar_evento'))

        self.assertEqual(response.status_code, 200)
        tipo_choices = [valor for valor, _ in response.context['form'].fields['tipo'].choices]
        self.assertEqual(set(tipo_choices), {'festa', 'cruzada', 'encontro'})
        self.assertContains(response, 'eventos são individuais e não recorrentes')

    def test_criar_evento_rejeita_tipo_padrao_igreja(self):
        response = self.client.post(
            reverse('eventos:criar_evento'),
            {
                'igreja': str(self.igreja.pk),
                'titulo': 'Culto de Rotina',
                'tipo': 'culto',
                'status_operacional': 'planejamento',
                'data_inicio': '2026-08-10T19:00',
                'quantidade_dias': '1',
                'hora_termino': '21:00',
                'frequencia': 'nenhuma',
                'intervalo': '1',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Evento.objects.filter(titulo='Culto de Rotina').exists())
        self.assertIn('form', response.context)
        self.assertIn('tipo', response.context['form'].errors)

    def test_lista_eventos_marca_origem_e_filtra_por_origem(self):
        programacao = ProgramacaoPadraoIgreja.objects.create(
            igreja=self.igreja,
            nome='Culto de Ensino',
            tipo_evento='culto',
            frequencia='semanal',
            dia_semana=2,
            hora_inicio=time(19, 0),
            hora_termino=time(21, 0),
            intervalo_semanas=1,
            duracao_minutos=120,
            ativo=True,
        )

        agora = timezone.now()
        evento_padrao = Evento.objects.create(
            igreja=self.igreja,
            titulo='Evento Programação',
            tipo='culto',
            data_inicio=agora,
            data_fim=agora,
            programacao_padrao=programacao,
        )
        evento_manual = Evento.objects.create(
            igreja=self.igreja,
            titulo='Evento Manual',
            tipo='festa',
            data_inicio=agora,
            data_fim=agora,
            criado_por=self.user,
        )

        response_lista = self.client.get(
            reverse('eventos:lista_eventos'),
            {
                'status': 'aguardando',
                'data_inicio': '2020-01-01',
                'data_fim': '2100-12-31',
            },
        )

        self.assertEqual(response_lista.status_code, 200)
        self.assertContains(response_lista, 'Configuração da Igreja')
        self.assertContains(response_lista, 'Novo Evento')
        self.assertContains(response_lista, evento_padrao.titulo)
        self.assertContains(response_lista, evento_manual.titulo)

        response_padrao = self.client.get(
            reverse('eventos:lista_eventos'),
            {
                'status': 'aguardando',
                'origem': 'padrao',
                'data_inicio': '2020-01-01',
                'data_fim': '2100-12-31',
            },
        )

        self.assertEqual(response_padrao.status_code, 200)
        self.assertContains(response_padrao, evento_padrao.titulo)
        self.assertNotContains(response_padrao, evento_manual.titulo)

    def test_lista_eventos_multidias_renderiza_grupo_diario_sem_coluna_data_fim(self):
        inicio = timezone.now().replace(hour=18, minute=0, second=0, microsecond=0)
        Evento.objects.create(
            igreja=self.igreja,
            titulo='Festividade 2026',
            tipo='festa',
            data_inicio=inicio,
            data_fim=inicio + timezone.timedelta(days=2, hours=3),
            quantidade_dias=3,
            criado_por=self.user,
        )

        response = self.client.get(
            reverse('eventos:lista_eventos'),
            {
                'status': 'aguardando',
                'data_inicio': '2020-01-01',
                'data_fim': '2100-12-31',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Festividade 2026 - Dia 1')
        self.assertContains(response, 'Festividade 2026 - Dia 2')
        self.assertContains(response, 'Festividade 2026 - Dia 3')
        self.assertContains(response, '3 dias')
        self.assertContains(response, '<th>Dia</th>', html=True)
        self.assertContains(response, 'Presença do dia')
        self.assertContains(response, '?sessao=')
        self.assertContains(response, 'js-toggle-dias')
        self.assertContains(response, 'js-dia-row-')
        self.assertNotContains(response, '<th>Data Fim</th>', html=True)

    def test_lista_eventos_ordenacao_por_dia_da_semana_e_data(self):
        tz = timezone.get_current_timezone()
        Evento.objects.create(
            igreja=self.igreja,
            titulo='Evento Domingo',
            tipo='festa',
            data_inicio=timezone.make_aware(datetime(2026, 8, 9, 19, 0), tz),
            data_fim=timezone.make_aware(datetime(2026, 8, 9, 21, 0), tz),
            criado_por=self.user,
        )
        Evento.objects.create(
            igreja=self.igreja,
            titulo='Evento Segunda',
            tipo='festa',
            data_inicio=timezone.make_aware(datetime(2026, 8, 10, 19, 0), tz),
            data_fim=timezone.make_aware(datetime(2026, 8, 10, 21, 0), tz),
            criado_por=self.user,
        )
        Evento.objects.create(
            igreja=self.igreja,
            titulo='Evento Terca',
            tipo='festa',
            data_inicio=timezone.make_aware(datetime(2026, 8, 11, 19, 0), tz),
            data_fim=timezone.make_aware(datetime(2026, 8, 11, 21, 0), tz),
            criado_por=self.user,
        )

        response = self.client.get(
            reverse('eventos:lista_eventos'),
            {
                'status': 'aguardando',
                'ordenacao': 'dia_data',
                'data_inicio': '2020-01-01',
                'data_fim': '2100-12-31',
            },
        )

        self.assertEqual(response.status_code, 200)
        titulos = [evento.titulo for evento in response.context['page_obj'].object_list]
        self.assertEqual(titulos, ['Evento Segunda', 'Evento Terca', 'Evento Domingo'])

    def test_lista_eventos_periodo_compacto_ultimos_7_dias(self):
        agora = timezone.now()
        Evento.objects.create(
            igreja=self.igreja,
            titulo='Evento Recente',
            tipo='festa',
            data_inicio=agora - timezone.timedelta(days=3),
            data_fim=agora - timezone.timedelta(days=3, hours=-2),
            criado_por=self.user,
        )
        Evento.objects.create(
            igreja=self.igreja,
            titulo='Evento Antigo',
            tipo='festa',
            data_inicio=agora - timezone.timedelta(days=25),
            data_fim=agora - timezone.timedelta(days=25, hours=-2),
            criado_por=self.user,
        )

        response = self.client.get(
            reverse('eventos:lista_eventos'),
            {
                'status': 'aguardando',
                'periodo_filtro': '7d',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Evento Recente')
        self.assertNotContains(response, 'Evento Antigo')

    def test_lista_eventos_periodo_compacto_custom_renderiza_bloco(self):
        response = self.client.get(
            reverse('eventos:lista_eventos'),
            {
                'status': 'aguardando',
                'periodo_filtro': 'custom',
                'data_inicio': '2026-08-01',
                'data_fim': '2026-08-31',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'eventos-periodo-custom')
        self.assertEqual(response.context['periodo_filtro_selecionado'], 'custom')

    def test_lista_eventos_exibe_link_para_lista_de_doacoes_eventos(self):
        response = self.client.get(
            reverse('eventos:lista_eventos'),
            {
                'status': 'aguardando',
                'periodo_filtro': '30d',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ver Doações')
        self.assertContains(response, reverse('financeiro:lista_receitas'))
        self.assertContains(response, 'categoria=doacao')

    def test_lista_eventos_exibe_link_para_lista_de_saidas_eventos(self):
        response = self.client.get(
            reverse('eventos:lista_eventos'),
            {
                'status': 'aguardando',
                'periodo_filtro': '30d',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ver Saídas')
        self.assertContains(response, reverse('financeiro:lista_despesas'))
        self.assertContains(response, 'fechado=todos')

    def test_lista_eventos_exibe_link_de_prestacao_de_contas_eventos(self):
        response = self.client.get(
            reverse('eventos:lista_eventos'),
            {
                'status': 'aguardando',
                'periodo_filtro': '30d',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prestação de Contas')
        self.assertContains(response, reverse('eventos:prestacao_contas_eventos'))
        self.assertContains(response, 'periodo_filtro=custom')
