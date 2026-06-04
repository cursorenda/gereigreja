from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from comunicacao.models import Aviso
from configuracao.models import ConfiguracaoSistema, Igreja, Ministerio
from escola_biblica.models import Aluno, AnoLetivo, Classe, Frequencia, OfertaClasse, PeriodoEBD, Turma
from escola_biblica.utils import build_resumo_semanal_ebd, formatar_resumo_semanal_ebd


class EBDResumoSemanalTest(TestCase):
    def _ultimo_domingo(self, data_base):
        deslocamento = (data_base.weekday() - 6) % 7
        return data_base - timedelta(days=deslocamento)

    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(username='admin_resumo_ebd', password='senha123')

        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Resumo EBD',
            administrador_principal=self.admin,
            ativo=True,
        )
        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja Resumo EBD',
            tipo_igreja='congregacao',
            ebd_periodo='trimestre',
            ebd_dia_semana=6,
        )
        ConfiguracaoSistema.objects.create(ministerio=self.ministerio)

        ano = timezone.localdate().year
        self.ano_letivo = AnoLetivo.objects.create(ano=ano, ativo=True)
        hoje = timezone.localdate()
        PeriodoEBD.objects.create(
            ano_letivo=self.ano_letivo,
            numero=1,
            tipo='trimestre',
            data_inicio=hoje - timedelta(days=30),
            data_fim=hoje + timedelta(days=30),
        )
        classe = Classe.objects.create(igreja=self.igreja, nome='Classe Resumo')
        self.turma = Turma.objects.create(
            nome='Turma Resumo',
            igreja=self.igreja,
            classe=classe,
            ano_letivo=self.ano_letivo,
        )

        self.aluno_1 = Aluno.objects.create(nome='Aluno Um', turma=self.turma)
        self.aluno_2 = Aluno.objects.create(nome='Aluno Dois', turma=self.turma)

    def test_build_resumo_semanal_ebd_calcula_metricas(self):
        hoje = timezone.localdate()
        inicio = hoje - timedelta(days=7)
        fim = hoje
        data_ebd = self._ultimo_domingo(hoje)

        Frequencia.objects.create(aluno=self.aluno_1, data=data_ebd, presente=True, pontos_total=10)
        Frequencia.objects.create(aluno=self.aluno_2, data=data_ebd, presente=False, pontos_total=0)
        OfertaClasse.objects.create(turma=self.turma, classe=self.turma.classe, data=data_ebd, valor=50)

        resumo = build_resumo_semanal_ebd(self.ministerio, inicio, fim)

        self.assertEqual(resumo['turmas_previstas'], 1)
        self.assertEqual(resumo['turmas_com_chamada'], 1)
        self.assertEqual(resumo['turmas_sem_chamada'], 0)
        self.assertEqual(resumo['chamadas_total'], 2)
        self.assertEqual(resumo['presencas_total'], 1)
        self.assertEqual(resumo['frequencia_media'], 50.0)
        self.assertEqual(resumo['total_ofertas'], 50.0)

    def test_formatar_resumo_semanal_ebd_retorna_texto_operacional(self):
        hoje = timezone.localdate()
        resumo = {
            'inicio': hoje - timedelta(days=7),
            'fim': hoje,
            'turmas_previstas': 2,
            'turmas_com_chamada': 1,
            'turmas_sem_chamada': 1,
            'frequencia_media': 72.5,
            'total_ofertas': 120.0,
            'alunos_novos': 3,
            'recomendacoes': ['Priorizar fechamento de chamada.'],
        }

        texto = formatar_resumo_semanal_ebd(resumo)

        self.assertIn('Turmas pendentes: 1', texto)
        self.assertIn('Frequência média: 72.5%', texto)
        self.assertIn('Recomendações da semana', texto)

    def test_management_command_publica_aviso(self):
        hoje = timezone.localdate()
        inicio = (hoje - timedelta(days=7)).strftime('%Y-%m-%d')
        fim = hoje.strftime('%Y-%m-%d')

        call_command(
            'gerar_resumo_semanal_ebd',
            ministerio_id=self.ministerio.id,
            inicio=inicio,
            fim=fim,
            publicar_aviso=True,
        )

        self.assertEqual(Aviso.objects.filter(ministerio=self.ministerio).count(), 1)
        aviso = Aviso.objects.get(ministerio=self.ministerio)
        self.assertIn('Resumo semanal EBD', aviso.titulo)
        self.assertIn('Recomendações da semana', aviso.conteudo)
