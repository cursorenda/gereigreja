from datetime import timedelta
from collections import Counter
import re
from unittest.mock import patch

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
from contas.constants import ADMIN_MINISTERIO, PROFESSOR_EBD
from secretaria.models import Cargo, Membro, MembroCargo, StatusPessoa, TipoPessoa
from escola_biblica.models import Aluno, AnoLetivo, Avaliacao, Classe, Frequencia, Licao, OfertaClasse, PeriodoEBD, TransferenciaAluno, Turma
from escola_biblica.services_chamada import construir_chave_bloqueio_chamada


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
        tabelas = Counter()
        for query in ctx.captured_queries:
            tabelas.update(re.findall(r'(?:FROM|JOIN|INTO|UPDATE) "([^"]+)"', query['sql']))
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(
            len(ctx),
            max_queries,
            f'Orçamento de queries excedido para {url}: {len(ctx)} > {max_queries}; {tabelas.most_common(10)}',
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
                'valor_oferta': '12,34',
            },
        )

        self.assertEqual(response.status_code, 302)
        freq = Frequencia.objects.get(aluno=aluno, data=timezone.localdate())
        self.assertEqual(freq.pontos_total, 12)
        oferta = OfertaClasse.objects.get(turma=turma, data=timezone.localdate())
        self.assertEqual(str(oferta.valor), '12.34')

    def test_chamada_post_invalida_desfaz_frequencias_e_oferta(self):
        turma = self._criar_turma('post-invalido', qtd_alunos=1, criar_licao=True)
        aluno = turma.alunos.first()

        response = self.client.post(
            reverse('escola_biblica:chamada_presenca', args=[turma.id]),
            {
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MIN_NUM_FORMS': '0',
                'form-MAX_NUM_FORMS': '1000',
                'form-0-aluno_id': str(aluno.id),
                'form-0-nome': aluno.nome,
                'form-0-presente': 'on',
                'valor_oferta': 'valor-invalido',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Informe um valor de oferta valido.')
        self.assertFalse(Frequencia.objects.filter(aluno=aluno, data=timezone.localdate()).exists())
        self.assertFalse(OfertaClasse.objects.filter(turma=turma, data=timezone.localdate()).exists())

    def test_chamada_post_rejeita_aluno_de_outra_turma(self):
        turma = self._criar_turma('turma-origem', qtd_alunos=1, criar_licao=True)
        outra_turma = self._criar_turma('turma-estranha', qtd_alunos=1, criar_licao=True)
        aluno_estranho = outra_turma.alunos.first()

        response = self.client.post(
            reverse('escola_biblica:chamada_presenca', args=[turma.id]),
            {
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MIN_NUM_FORMS': '0',
                'form-MAX_NUM_FORMS': '1000',
                'form-0-aluno_id': str(aluno_estranho.id),
                'form-0-nome': aluno_estranho.nome,
                'form-0-presente': 'on',
                'valor_oferta': '0',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A chamada foi recusada')
        self.assertFalse(Frequencia.objects.filter(aluno=aluno_estranho, data=timezone.localdate()).exists())

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

    def test_professor_acessa_apenas_a_propria_turma(self):
        turma_do_professor = self._criar_turma('professor', criar_licao=True)
        outra_turma = self._criar_turma('outra-professor', criar_licao=True)
        user_model = get_user_model()
        professor_user = user_model.objects.create_user(username='professor_ebd', password='senha123')
        grupo_professor, _ = Group.objects.get_or_create(name=PROFESSOR_EBD)
        professor_user.groups.add(grupo_professor)
        PerfilUsuario.objects.create(user=professor_user, ministerio=self.ministerio)
        tipo, _ = TipoPessoa.objects.get_or_create(nome='Membro')
        status, _ = StatusPessoa.objects.get_or_create(nome='Ativo')
        with patch('secretaria.models.StatusHistorico.objects.create'):
            membro = Membro.objects.create(
                nome='Professor EBD', igreja=self.igreja, usuario=professor_user,
                tipo_pessoa=tipo, status_pessoa=status,
            )
        cargo = Cargo.objects.create(nome='Professor EBD Teste', is_ebd=True)
        MembroCargo.objects.create(membro=membro, cargo=cargo, data_inicio=timezone.localdate())
        turma_do_professor.membros.add(membro)

        self.client.force_login(professor_user)
        permitida = self.client.get(reverse('escola_biblica:chamada_presenca', args=[turma_do_professor.id]))
        bloqueada = self.client.get(reverse('escola_biblica:chamada_presenca', args=[outra_turma.id]))

        self.assertEqual(permitida.status_code, 200)
        self.assertEqual(bloqueada.status_code, 403)
        self.assertFalse(Frequencia.objects.filter(aluno__turma=outra_turma).exists())

    def test_get_exclusao_licao_exibe_confirmacao(self):
        turma = self._criar_turma('excluir-licao', criar_licao=True)
        licao = turma.licao_set.get()

        response = self.client.get(reverse('escola_biblica:licao_delete', args=[licao.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'escola_biblica/licao_confirm_delete.html')
        self.assertContains(response, licao.tema)

    def test_exclusao_licao_com_avaliacoes_e_bloqueada(self):
        turma = self._criar_turma('licao-com-avaliacao', criar_licao=True)
        licao = turma.licao_set.get()
        avaliacao = Avaliacao.objects.create(aluno=turma.alunos.get(), licao=licao)

        response = self.client.post(
            reverse('escola_biblica:licao_delete', args=[licao.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Licao.objects.filter(pk=licao.id).exists())
        self.assertTrue(Avaliacao.objects.filter(pk=avaliacao.id).exists())
        self.assertContains(response, 'Esta lição possui avaliações registradas.')

    def test_lista_licoes_inclui_turma_da_igreja_sem_colaboradores(self):
        turma = self._criar_turma('listar-licoes-sem-colaboradores', criar_licao=True)
        licao = turma.licao_set.get()

        response = self.client.get(reverse('escola_biblica:licao_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, licao.tema)

    def test_relatorio_diario_inclui_turma_da_igreja_sem_colaboradores(self):
        turma = self._criar_turma('relatorio-sem-colaboradores', criar_licao=True)

        response = self.client.get(
            reverse('escola_biblica:relatorio_ebd_dia'),
            {'data': timezone.localdate().isoformat()},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, turma.nome)

    def test_wizard_cronograma_inclui_turma_da_igreja_sem_colaboradores(self):
        turma = self._criar_turma('cronograma-sem-colaboradores', criar_licao=False)

        response = self.client.get(reverse('escola_biblica:gerar_cronograma_wizard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, turma.nome)

    def test_wizard_cronograma_avanca_da_selecao_para_configuracao(self):
        turma = self._criar_turma('wizard-selecao', criar_licao=False)
        periodo = self.ano_letivo.periodos.first()

        response = self.client.post(
            reverse('escola_biblica:gerar_cronograma_wizard'),
            {
                'etapa': '1',
                'wizard_next': '1',
                'ano_letivo': self.ano_letivo.ano,
                'periodo': periodo.numero,
                'turmas': [turma.id],
                'material': 'Revista da EBD',
                'status': 'ativa',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['etapa'], 2)
        self.assertEqual(response.context['ano_letivo'], self.ano_letivo.ano)
        self.assertEqual(response.context['periodo'], periodo.numero)
        self.assertEqual(response.context['material'], 'Revista da EBD')

    def test_wizard_cronograma_recusa_selecao_inicial_com_turma_de_outro_ano(self):
        ano_futuro = AnoLetivo.objects.create(ano=self.ano_letivo.ano + 1)
        turma_futura = Turma.objects.create(
            nome='Turma futura na selecao',
            igreja=self.igreja,
            classe=Classe.objects.create(igreja=self.igreja, nome='Classe futura'),
            ano_letivo=ano_futuro,
        )
        periodo = self.ano_letivo.periodos.first()

        response = self.client.post(
            reverse('escola_biblica:gerar_cronograma_wizard'),
            {
                'etapa': '1',
                'wizard_next': '1',
                'ano_letivo': self.ano_letivo.ano,
                'periodo': periodo.numero,
                'turmas': [turma_futura.id],
                'status': 'ativa',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['etapa'], 1)
        self.assertIn('erro_wizard', response.context)
        self.assertEqual(response.context['ano_letivo_selecionado'], self.ano_letivo.ano)
        self.assertEqual(response.context['periodo_selecionado'], periodo.numero)
        self.assertEqual(response.context['turmas_selecionadas'], [turma_futura.id])

    def test_wizard_cronograma_monta_previa_para_turmas_autorizadas(self):
        turma = self._criar_turma('wizard-previa', criar_licao=False)
        periodo = self.ano_letivo.periodos.first()

        response = self.client.post(
            reverse('escola_biblica:gerar_cronograma_wizard'),
            {
                'etapa': '2',
                'wizard_next': '1',
                'ano_letivo': self.ano_letivo.ano,
                'periodo': periodo.numero,
                'turmas': [turma.id],
                'nome_licao_padrao': 'Licao {n} - {periodo}',
                'status': 'ativa',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['etapa'], 3)
        self.assertTrue(response.context['licoes_preview'])
        self.assertEqual(response.context['licoes_preview'][0]['turma_nome'], turma.nome)

    def test_wizard_cronograma_recusa_confirmacao_com_turma_de_outro_ano(self):
        ano_futuro = AnoLetivo.objects.create(ano=self.ano_letivo.ano + 1)
        turma_futura = Turma.objects.create(
            nome='Turma de outro ano',
            igreja=self.igreja,
            classe=Classe.objects.create(igreja=self.igreja, nome='Classe outro ano'),
            ano_letivo=ano_futuro,
        )
        periodo = self.ano_letivo.periodos.first()

        response = self.client.post(
            reverse('escola_biblica:gerar_cronograma_wizard'),
            {
                'etapa': '3',
                'wizard_confirm': '1',
                'ano_letivo': self.ano_letivo.ano,
                'periodo': periodo.numero,
                'turmas': [turma_futura.id],
                'nome_licao_padrao': 'Licao {n} - {periodo}',
                'status': 'ativa',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['etapa'], 2)
        self.assertIn('erro_wizard', response.context)
        self.assertFalse(Licao.objects.filter(turma=turma_futura).exists())

    def test_wizard_cronograma_registra_auditoria_ao_confirmar(self):
        turma = self._criar_turma('wizard-auditoria', criar_licao=False)
        periodo = self.ano_letivo.periodos.first()

        with patch('escola_biblica.views.log_ebd_audit_event') as auditoria:
            response = self.client.post(
                reverse('escola_biblica:gerar_cronograma_wizard'),
                {
                    'etapa': '3',
                    'wizard_confirm': '1',
                    'ano_letivo': self.ano_letivo.ano,
                    'periodo': periodo.numero,
                    'turmas': [turma.id],
                    'nome_licao_padrao': 'Licao {n} - {periodo}',
                    'status': 'ativa',
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['etapa'], 4)
        auditoria.assert_called_once()
        self.assertEqual(auditoria.call_args.args[1], 'cronograma_wizard_gerado')
        self.assertEqual(auditoria.call_args.kwargs['periodo_id'], periodo.id)
        self.assertEqual(auditoria.call_args.kwargs['turmas_ids'], str(turma.id))

    def test_dashboard_inclui_turma_da_igreja_sem_colaboradores(self):
        turma = self._criar_turma('dashboard-sem-colaboradores', criar_licao=True)

        response = self.client.get(reverse('escola_biblica:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, turma.nome)

    def test_dashboard_conta_transferencia_com_turma_origem_no_escopo(self):
        turma_origem = self._criar_turma('transferencia-origem', criar_licao=False)
        outra_igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja Destino Transferencia',
            tipo_igreja='congregacao',
        )
        classe_destino = Classe.objects.create(igreja=outra_igreja, nome='Classe Destino Transferencia')
        turma_destino = Turma.objects.create(
            nome='Turma Destino Transferencia',
            igreja=outra_igreja,
            classe=classe_destino,
            ano_letivo=self.ano_letivo,
        )
        TransferenciaAluno.objects.create(
            aluno=turma_origem.alunos.get(),
            turma_origem=turma_origem,
            turma_destino=turma_destino,
        )

        response = self.client.get(reverse('escola_biblica:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['transferidos_mes'], 1)

    def test_historico_consolidado_exibe_apenas_matriculas_do_escopo(self):
        turma = self._criar_turma('historico-escopo', criar_licao=True)
        aluno = turma.alunos.get()

        response = self.client.get(
            reverse('escola_biblica:aluno_historico_consolidado', args=[aluno.id]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_matriculas'], 1)
        self.assertEqual(response.context['total_frequencias'], 0)

    def test_exclusao_classe_com_turmas_exibe_mensagem_amigavel(self):
        turma = self._criar_turma('classe-com-turmas', criar_licao=False)

        response = self.client.post(
            reverse('escola_biblica:classe_delete', args=[turma.classe_id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Classe.objects.filter(pk=turma.classe_id).exists())
        self.assertContains(response, 'Esta classe possui turmas vinculadas e não pode ser excluída.')

    def test_exclusao_turma_sem_colaboradores_respeita_igreja_da_turma(self):
        turma = self._criar_turma(
            'excluir-turma-sem-colaboradores',
            qtd_alunos=0,
            criar_licao=False,
        )

        response = self.client.post(reverse('escola_biblica:turma_delete', args=[turma.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Turma.objects.filter(pk=turma.id).exists())

    def test_exclusao_turma_com_alunos_exibe_mensagem_amigavel(self):
        turma = self._criar_turma('excluir-turma-com-alunos', criar_licao=False)

        response = self.client.post(
            reverse('escola_biblica:turma_delete', args=[turma.id]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Turma.objects.filter(pk=turma.id).exists())
        self.assertContains(response, 'Esta turma possui dados vinculados e não pode ser excluída.')

    def test_exclusao_avaliacao_respeita_escopo_e_remove_registro(self):
        turma = self._criar_turma('excluir-avaliacao', criar_licao=True)
        avaliacao = Avaliacao.objects.create(
            aluno=turma.alunos.get(),
            licao=turma.licao_set.get(),
        )

        response = self.client.post(reverse('escola_biblica:avaliacao_delete', args=[avaliacao.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Avaliacao.objects.filter(pk=avaliacao.id).exists())

    def test_exclusao_oferta_respeita_escopo_e_remove_registro(self):
        turma = self._criar_turma('excluir-oferta', criar_licao=False)
        oferta = OfertaClasse.objects.create(
            turma=turma,
            classe=turma.classe,
            data=timezone.localdate(),
            valor=10,
        )

        response = self.client.post(reverse('escola_biblica:oferta_classe_delete', args=[oferta.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(OfertaClasse.objects.filter(pk=oferta.id).exists())

    def test_lista_ofertas_inclui_oferta_legada_vinculada_a_classe_da_igreja(self):
        turma = self._criar_turma('oferta-legada-classe', criar_licao=False)
        OfertaClasse.objects.create(
            classe=turma.classe,
            data=timezone.localdate(),
            valor=10,
        )

        response = self.client.get(reverse('escola_biblica:oferta_classe_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, turma.classe.nome)

    def test_copia_seletiva_isola_turmas_com_mesmo_nome_por_igreja(self):
        ano_destino = self.ano_letivo.ano + 1
        classe_origem = Classe.objects.create(igreja=self.igreja, nome='Classe Adultos Copia')
        turma_origem = Turma.objects.create(
            nome='Turma Adultos Copia',
            igreja=self.igreja,
            classe=classe_origem,
            ano_letivo=self.ano_letivo,
        )
        aluno_origem = Aluno.objects.create(nome='Aluno Copia', turma=turma_origem)

        outra_igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Outra Igreja Copia',
            tipo_igreja='congregacao',
        )
        classe_outra_igreja = Classe.objects.create(igreja=outra_igreja, nome='Classe Adultos Copia')
        ano_destino_obj = AnoLetivo.objects.create(ano=ano_destino, ativo=True)
        turma_outra_igreja = Turma.objects.create(
            nome='Turma Adultos Copia',
            igreja=outra_igreja,
            classe=classe_outra_igreja,
            ano_letivo=ano_destino_obj,
        )

        url = reverse('escola_biblica:copiar_periodo_selecao')
        payload = {
            'ano_destino': str(ano_destino),
            'turmas_selecionadas': [str(turma_origem.id)],
            'classes_selecionadas': [str(classe_origem.id)],
            'alunos_selecionados': [str(aluno_origem.id)],
        }
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, 302)
        turma_destino = Turma.objects.get(
            nome=turma_origem.nome,
            igreja=self.igreja,
            ano_letivo=ano_destino_obj,
        )
        self.assertNotEqual(turma_destino.pk, turma_outra_igreja.pk)
        self.assertTrue(Aluno.objects.filter(cadastro=aluno_origem.cadastro, turma=turma_destino).exists())
        self.assertFalse(Aluno.objects.filter(cadastro=aluno_origem.cadastro, turma=turma_outra_igreja).exists())
        licoes_destino = Licao.objects.filter(turma=turma_destino)
        total_licoes_destino = licoes_destino.count()
        self.assertGreater(total_licoes_destino, 0)
        self.assertTrue(all(
            licao.data.weekday() == self.igreja.ebd_dia_semana
            for licao in licoes_destino
        ))

        self.client.post(url, payload)
        self.assertEqual(Aluno.objects.filter(cadastro=aluno_origem.cadastro, turma=turma_destino).count(), 1)
        self.assertEqual(Licao.objects.filter(turma=turma_destino).count(), total_licoes_destino)

        response = self.client.post(
            reverse('escola_biblica:copiar_turmas_ano_anterior'),
            {'ano_destino': str(ano_destino)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Aluno.objects.filter(cadastro=aluno_origem.cadastro, turma=turma_destino).count(), 1)
        self.assertFalse(Aluno.objects.filter(cadastro=aluno_origem.cadastro, turma=turma_outra_igreja).exists())

    def test_copia_seletiva_permite_copiar_apenas_aluno_para_turma_destino_existente(self):
        ano_destino = self.ano_letivo.ano + 1
        classe = Classe.objects.create(igreja=self.igreja, nome='Classe Copia Apenas Aluno')
        turma_origem = Turma.objects.create(
            nome='Turma Copia Apenas Aluno',
            igreja=self.igreja,
            classe=classe,
            ano_letivo=self.ano_letivo,
        )
        aluno_origem = Aluno.objects.create(nome='Aluno Copia Apenas Aluno', turma=turma_origem)
        ano_destino_obj = AnoLetivo.objects.create(ano=ano_destino, ativo=True)
        turma_destino = Turma.objects.create(
            nome=turma_origem.nome,
            igreja=self.igreja,
            classe=classe,
            ano_letivo=ano_destino_obj,
        )

        response = self.client.post(reverse('escola_biblica:copiar_periodo_selecao'), {
            'ano_destino': str(ano_destino),
            'alunos_selecionados': [str(aluno_origem.id)],
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Aluno.objects.filter(cadastro=aluno_origem.cadastro, turma=turma_destino).exists(),
        )

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
        self.assertContains(response, 'KPIs por Turma e Professor')
        self.assertContains(response, 'Centro de Ações Operacionais')
        self.assertContains(response, 'Fechar pendências do relatório do dia')
        self.assertContains(response, 'Contexto de Classe (apoio)')

    def test_dashboard_exibe_atalho_para_preparar_proximo_ano_letivo(self):
        response = self.client.get(reverse('escola_biblica:dashboard'))

        proximo_ano = self.ano_letivo.ano + 1
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'Preparar ano letivo {proximo_ano}')
        self.assertContains(response, f'copiar_periodo_selecao/?ano_destino={proximo_ano}')

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

        lock_key = construir_chave_bloqueio_chamada(turma.id, timezone.localdate())
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
