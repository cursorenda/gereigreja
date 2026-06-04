from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.test import TestCase
from django.utils import timezone

from configuracao.models import Igreja, Ministerio
from escola_biblica.models import Aluno, AnoLetivo, Classe, Frequencia, PeriodoEBD, Turma
from escola_biblica.views import _get_expr_pontos_frequencia, build_painel_executivo_ebd, calcular_pontos_frequencia_flags


class EBDPontosHelpersTest(TestCase):
    def test_calcular_pontos_frequencia_flags_soma_campos_ativos(self):
        pontos = calcular_pontos_frequencia_flags(
            presente=True,
            trouxe_biblia=True,
            trouxe_revista=False,
            trouxe_oferta=True,
            trouxe_visitante=True,
            pontos_cfg={
                'presente': 10,
                'biblia': 2,
                'revista': 2,
                'oferta': 3,
                'visitante': 5,
            },
        )

        self.assertEqual(pontos, 20)

    def test_build_painel_executivo_detecta_anomalias_criticas(self):
        painel = build_painel_executivo_ebd(
            freq_atual=58,
            freq_anterior=71,
            ofertas_atual=800,
            ofertas_anterior=1500,
            turmas_previstas_semana=10,
            turmas_sem_chamada_semana=4,
            evasao=3,
        )

        self.assertIn('frequencia_baixa', painel['anomalias'])
        self.assertIn('queda_frequencia_acelerada', painel['anomalias'])
        self.assertIn('chamadas_pendentes_semana', painel['anomalias'])
        self.assertIn('queda_ofertas_relevante', painel['anomalias'])
        self.assertIn('evasao_detectada', painel['anomalias'])
        self.assertGreaterEqual(len(painel['recomendacoes']), 1)

    def test_build_painel_executivo_retorna_recomendacao_estavel(self):
        painel = build_painel_executivo_ebd(
            freq_atual=84,
            freq_anterior=82,
            ofertas_atual=1200,
            ofertas_anterior=1150,
            turmas_previstas_semana=8,
            turmas_sem_chamada_semana=0,
            evasao=0,
        )

        self.assertEqual(painel['anomalias'], [])
        self.assertEqual(len(painel['recomendacoes']), 1)
        self.assertEqual(painel['recomendacoes'][0]['titulo'], 'Operação estável no período')


class EBDPontosRankingSnapshotTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(username='admin_ebd_pontos', password='senha123')

        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio EBD Pontos',
            administrador_principal=self.admin,
            ativo=True,
        )
        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja EBD Pontos',
            tipo_igreja='congregacao',
        )

        hoje = timezone.localdate()
        self.ano_letivo = AnoLetivo.objects.create(ano=hoje.year, ativo=True)
        PeriodoEBD.objects.create(
            ano_letivo=self.ano_letivo,
            numero=1,
            tipo='trimestre',
            data_inicio=hoje - timedelta(days=30),
            data_fim=hoje + timedelta(days=30),
        )
        classe = Classe.objects.create(igreja=self.igreja, nome='Classe Teste')
        turma = Turma.objects.create(nome='Turma Teste', igreja=self.igreja, classe=classe, ano_letivo=self.ano_letivo)

        self.aluno = Aluno.objects.create(nome='Aluno Teste', turma=turma)

    def test_ranking_usa_snapshot_pontos_total_com_fallback_por_flags(self):
        hoje = timezone.localdate()
        cfg = {
            'presente': 10,
            'biblia': 2,
            'revista': 2,
            'oferta': 3,
            'visitante': 5,
        }

        Frequencia.objects.create(
            aluno=self.aluno,
            data=hoje - timedelta(days=7),
            presente=True,
            trouxe_biblia=True,
            pontos_total=99,
        )
        Frequencia.objects.create(
            aluno=self.aluno,
            data=hoje,
            presente=True,
            trouxe_oferta=True,
            pontos_total=None,
        )

        total = Frequencia.objects.aggregate(
            total=Sum(Coalesce('pontos_total', _get_expr_pontos_frequencia(cfg)))
        )['total']

        self.assertEqual(total, 112)

    def test_ordenacao_empate_por_nome_casefold(self):
        ranking = [
            {'nome': 'joao', 'total_pontos': 20, 'presencas': 2},
            {'nome': 'Ana', 'total_pontos': 20, 'presencas': 2},
            {'nome': 'bia', 'total_pontos': 30, 'presencas': 1},
        ]

        ranking.sort(key=lambda r: (-r['total_pontos'], -r['presencas'], r['nome'].casefold()))

        self.assertEqual([item['nome'] for item in ranking], ['bia', 'Ana', 'joao'])
