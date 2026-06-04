from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from comunicacao.models import Aviso
from configuracao.models import Igreja, Ministerio, PerfilUsuario
from contas.constants import ADMIN_MINISTERIO
from escola_biblica.models import Aluno, AnoLetivo, Classe, Frequencia, Licao, PeriodoEBD, Turma
from escola_biblica.views import _build_chamada_processing_lock_key


class ChamadaPresencaFluxoTest(TestCase):
    QUERY_BUDGET_CHAMADA_GET = 140
    QUERY_BUDGET_DASHBOARD_GET = 140
    QUERY_BUDGET_CHAMADA_CARGA_GET = 180
    QUERY_BUDGET_DASHBOARD_CARGA_GET = 220

    def setUp(self):
        cache.clear()

        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='admin_chamada', password='senha123')

        group, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        self.user.groups.add(group)

        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Chamada EBD',
            administrador_principal=self.user,
            ativo=True,
        )
        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja Chamada EBD',
            tipo_igreja='congregacao',
            ebd_periodo='trimestre',
            ebd_dia_semana=timezone.localdate().weekday(),
        )

        perfil = PerfilUsuario.objects.create(user=self.user, ministerio=self.ministerio)
        perfil.igrejas_permitidas.add(self.igreja)

        self.ano_letivo = AnoLetivo.objects.create(ano=timezone.localdate().year, ativo=True)
        PeriodoEBD.objects.create(
            ano_letivo=self.ano_letivo,
            numero=1,
            tipo='trimestre',
            data_inicio=timezone.localdate() - timedelta(days=30),
            data_fim=timezone.localdate() + timedelta(days=30),
        )

        self.client.force_login(self.user)

    def _assert_query_budget_get(self, url, max_queries):
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(
            len(ctx),
            max_queries,
            f'Orçamento de queries excedido para {url}: {len(ctx)} > {max_queries}',
        )
        return response

    def _criar_turma(self, nome, qtd_alunos=1, criar_licao=True):
        classe = Classe.objects.create(igreja=self.igreja, nome=f'Classe {nome}')
        turma = Turma.objects.create(
            nome=f'Turma {nome}',
            igreja=self.igreja,
            classe=classe,
            ano_letivo=self.ano_letivo,
        )

        for i in range(qtd_alunos):
            Aluno.objects.create(nome=f'Aluno {nome} {i}', turma=turma)

        if criar_licao:
            Licao.objects.create(
                turma=turma,
                data=timezone.localdate(),
                tema=f'Licao {nome}',
                status='ativa',
            )

        return turma

    def _seed_frequencias_turma(self, turma, semanas=8):
        alunos = list(turma.alunos.all())
        base = timezone.localdate()
        datas = [base - timedelta(days=7 * idx) for idx in range(semanas)]

        licoes = [
            Licao(
                turma=turma,
                data=data,
                tema=f'Licao carga {idx}',
                status='ativa',
            )
            for idx, data in enumerate(datas, start=1)
        ]
        Licao.objects.bulk_create(licoes, ignore_conflicts=True)

        frequencias = []
        for aluno in alunos:
            for idx, data in enumerate(datas):
                presente = (idx % 4) != 0
                frequencias.append(
                    Frequencia(
                        aluno=aluno,
                        data=data,
                        presente=presente,
                        trouxe_biblia=presente,
                        trouxe_revista=False,
                        trouxe_visitante=False,
                        trouxe_oferta=False,
                        pontos_total=12 if presente else 0,
                    )
                )

        Frequencia.objects.bulk_create(frequencias, ignore_conflicts=True)

    def test_chamada_post_salva_frequencia_com_snapshot_pontos(self):
        turma = self._criar_turma('post', qtd_alunos=1, criar_licao=True)
        aluno = turma.alunos.first()

        url = reverse('escola_biblica:chamada_presenca', args=[turma.id])
        response = self.client.post(
            url,
            {
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MIN_NUM_FORMS': '0',
                'form-MAX_NUM_FORMS': '1000',
                'form-0-aluno_id': str(aluno.id),
                'form-0-nome': aluno.nome,
                'form-0-presente': 'on',
                'form-0-trouxe_biblia': 'on',
                'valor_oferta': '0',
            },
        )

        self.assertEqual(response.status_code, 302)
        freq = Frequencia.objects.get(aluno=aluno, data=timezone.localdate())
        self.assertEqual(freq.pontos_total, 12)

    def test_chamada_sem_permissao_retorna_403(self):
        turma = self._criar_turma('sem-permissao', qtd_alunos=2, criar_licao=True)

        user_model = get_user_model()
        user_sem_permissao = user_model.objects.create_user(username='sem_perm_ebd', password='senha123')
        PerfilUsuario.objects.create(user=user_sem_permissao, ministerio=self.ministerio)

        self.client.force_login(user_sem_permissao)
        url = reverse('escola_biblica:chamada_presenca', args=[turma.id])
        response = self.client.get(url)

        self.assertIn(response.status_code, [302, 403])
        self.assertNotEqual(response.status_code, 200)

    def test_get_chamada_sem_regressao_nmais1(self):
        turma_pequena = self._criar_turma('qsmall', qtd_alunos=1, criar_licao=True)
        turma_grande = self._criar_turma('qbig', qtd_alunos=15, criar_licao=True)

        url_pequena = reverse('escola_biblica:chamada_presenca', args=[turma_pequena.id])
        url_grande = reverse('escola_biblica:chamada_presenca', args=[turma_grande.id])

        # Warm-up para estabilizar queries de sessão/permissão.
        self.client.get(url_pequena)

        with CaptureQueriesContext(connection) as ctx_pequena:
            resp_pequena = self.client.get(url_pequena)
        with CaptureQueriesContext(connection) as ctx_grande:
            resp_grande = self.client.get(url_grande)

        self.assertEqual(resp_pequena.status_code, 200)
        self.assertEqual(resp_grande.status_code, 200)
        self.assertLessEqual(len(ctx_grande), len(ctx_pequena) + 15)

    def test_get_chamada_respeita_orcamento_queries(self):
        turma = self._criar_turma('budget-chamada', qtd_alunos=15, criar_licao=True)
        url = reverse('escola_biblica:chamada_presenca', args=[turma.id])

        # Warm-up para evitar ruído de primeira requisição.
        self.client.get(url)

        self._assert_query_budget_get(url, self.QUERY_BUDGET_CHAMADA_GET)

    def test_get_dashboard_respeita_orcamento_queries(self):
        turma = self._criar_turma('budget-dashboard', qtd_alunos=15, criar_licao=True)
        alunos = list(turma.alunos.all()[:5])
        for aluno in alunos:
            Frequencia.objects.create(
                aluno=aluno,
                data=timezone.localdate(),
                presente=True,
                trouxe_biblia=True,
                trouxe_revista=False,
                trouxe_visitante=False,
                trouxe_oferta=False,
                pontos_total=12,
            )

        url = reverse('escola_biblica:dashboard')

        # Warm-up para evitar ruído de primeira requisição.
        self.client.get(url)

        self._assert_query_budget_get(url, self.QUERY_BUDGET_DASHBOARD_GET)

    def test_dashboard_exibe_resumo_semanal_e_checklist_mobile(self):
        self._criar_turma('dash-ui', qtd_alunos=3, criar_licao=True)

        url = reverse('escola_biblica:dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resumo Semanal da EBD')
        self.assertContains(response, 'Checklist Mobile de Domingo')
        self.assertContains(response, 'Publicar em Avisos')

    def test_dashboard_post_publica_resumo_semanal_em_avisos(self):
        self._criar_turma('dash-post', qtd_alunos=2, criar_licao=True)

        url = reverse('escola_biblica:dashboard')
        response = self.client.post(url, {'acao': 'publicar_resumo_semanal'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Aviso.objects.filter(ministerio=self.ministerio).count(), 1)
        self.assertContains(response, 'Resumo semanal da EBD publicado em Avisos')

    def test_chamada_post_duplicado_e_ignorado_por_idempotencia(self):
        turma = self._criar_turma('idem', qtd_alunos=1, criar_licao=True)
        aluno = turma.alunos.first()

        url = reverse('escola_biblica:chamada_presenca', args=[turma.id])
        payload = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-aluno_id': str(aluno.id),
            'form-0-nome': aluno.nome,
            'form-0-presente': 'on',
            'form-0-trouxe_biblia': 'on',
            'valor_oferta': '0',
        }

        primeira = self.client.post(url, payload)
        segunda = self.client.post(url, payload, follow=True)

        self.assertEqual(primeira.status_code, 302)
        self.assertEqual(segunda.status_code, 200)
        self.assertEqual(Frequencia.objects.filter(aluno=aluno, data=timezone.localdate()).count(), 1)
        self.assertContains(segunda, 'já foi processada recentemente')

    def test_chamada_post_concorrente_e_ignorado_por_processing_lock(self):
        turma = self._criar_turma('lock', qtd_alunos=1, criar_licao=True)
        aluno = turma.alunos.first()

        url = reverse('escola_biblica:chamada_presenca', args=[turma.id])
        payload = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-aluno_id': str(aluno.id),
            'form-0-nome': aluno.nome,
            'form-0-presente': 'on',
            'form-0-trouxe_biblia': 'on',
            'valor_oferta': '0',
        }

        lock_key = _build_chamada_processing_lock_key(turma.id, timezone.localdate())
        cache.add(lock_key, self.user.pk, timeout=30)

        response = self.client.post(url, payload, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Frequencia.objects.filter(aluno=aluno, data=timezone.localdate()).count(), 0)
        self.assertContains(response, 'está sendo processada no momento')

    def test_carga_get_chamada_turma_grande_periodo_extenso(self):
        turma = self._criar_turma('carga-chamada', qtd_alunos=120, criar_licao=True)
        self._seed_frequencias_turma(turma, semanas=10)
        url = reverse('escola_biblica:chamada_presenca', args=[turma.id])

        # Warm-up para reduzir ruído de cache/sessão.
        self.client.get(url)

        response = self._assert_query_budget_get(url, self.QUERY_BUDGET_CHAMADA_CARGA_GET)
        self.assertContains(response, 'Chamada de Presença')

    def test_carga_get_dashboard_periodo_extenso(self):
        turmas = [
            self._criar_turma('carga-dash-a', qtd_alunos=60, criar_licao=True),
            self._criar_turma('carga-dash-b', qtd_alunos=60, criar_licao=True),
        ]
        for turma in turmas:
            self._seed_frequencias_turma(turma, semanas=12)

        url = reverse('escola_biblica:dashboard')

        # Warm-up para reduzir ruído de cache/sessão.
        self.client.get(url)

        response = self._assert_query_budget_get(url, self.QUERY_BUDGET_DASHBOARD_CARGA_GET)
        self.assertContains(response, 'Dashboard EBD')
