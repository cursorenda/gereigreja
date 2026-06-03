from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.test import TestCase
from django.utils import timezone

from configuracao.models import Igreja, Ministerio
from escola_biblica.models import Aluno, AnoLetivo, Classe, Frequencia, PeriodoEBD, Turma
from escola_biblica.views import _get_expr_pontos_frequencia, calcular_pontos_frequencia_flags


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
