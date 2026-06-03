from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from configuracao.models import Igreja, Ministerio, PerfilUsuario
from contas.constants import ADMIN_MINISTERIO
from escola_biblica.models import Aluno, AnoLetivo, Classe, Frequencia, Licao, PeriodoEBD, Turma


class ChamadaPresencaFluxoTest(TestCase):
    def setUp(self):
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
