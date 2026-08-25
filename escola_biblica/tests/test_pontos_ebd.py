from datetime import timedelta
from inspect import unwrap
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.test import RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from configuracao.models import Igreja, Ministerio
from secretaria.models import Membro, StatusPessoa, TipoPessoa
from escola_biblica.forms import AlunoForm, AvaliacaoForm, GerarCronogramaForm, LicaoForm, OfertaClasseForm, TransferenciaAlunoForm
from escola_biblica.models import Aluno, AnoLetivo, Avaliacao, Classe, Frequencia, Licao, OfertaClasse, PeriodoEBD, TransferenciaAluno, Turma
from escola_biblica.services_chamada import (
    calcular_pontos_frequencia_flags,
    formulario_chamada_corresponde_a_turma,
    preparar_calendario_chamada,
    preparar_contexto_exibicao_chamada,
    preparar_formset_inicial_chamada,
)
from escola_biblica.services_copia import (
    consolidar_resultado_copia_seletiva,
    copiar_aluno_para_turma,
    copiar_ano_anterior_completo,
    copiar_dados_selecionados_para_ano,
    copiar_turmas_para_ano,
    obter_ou_criar_classe_destino,
    obter_ou_criar_turma_destino,
)
from escola_biblica.services_consultas import (
    construir_contexto_relatorio_alunos,
    construir_contexto_listagem_alunos,
    construir_contexto_template_listagem_alunos,
    construir_contexto_template_listagem_turmas,
    construir_expr_pontos_frequencia,
    construir_listagem_licoes,
    filtrar_e_paginar_aulas_geradas,
    paginar_queryset,
    preparar_listagem_alunos,
)
from escola_biblica.services_dashboard import (
    calcular_status_chamadas_semanais,
    coletar_dados_kpis_turma_professor,
    calcular_janela_operacional_semana,
    construir_bloco_decisao_dashboard,
    construir_chave_cache_dashboard,
    construir_comparativo_card,
    construir_painel_executivo_ebd,
    construir_relatorio_instantaneo_turmas,
    construir_contexto_template_dashboard,
    preparar_contexto_operacional_dashboard,
    preparar_contexto_periodo_dashboard,
)
from escola_biblica.services_configuracao import (
    obter_configuracao_ebd_turma,
    obter_horario_ebd_formatado,
)
from escola_biblica.services_escopo import aplicar_igreja_filtro_inicial
from escola_biblica.services_permissoes import filtrar_queryset_por_turmas_do_usuario
from escola_biblica.services_periodos import (
    agrupar_turmas_por_calendario,
    abrir_proximo_periodo,
    criar_licoes_cronograma,
    construir_previa_cronograma,
    construir_contexto_formulario_wizard_cronograma,
    construir_status_periodo,
    avaliar_prontidao_fechamento_periodo,
    diagnosticar_fechamento_periodo,
    gerar_cronograma_para_turma,
    gerar_e_persistir_licoes_periodos,
    normalizar_etapa_wizard_cronograma,
    normalizar_inteiro_wizard_cronograma,
    normalizar_horario_wizard,
    normalizar_material_wizard,
    normalizar_nome_licao_padrao,
    normalizar_status_licao_wizard,
    obter_ano_letivo_para_criacao_turma,
    obter_datas_aula_wizard_cronograma,
    obter_periodo_wizard_disponivel,
    obter_periodo_filtro,
    preparar_dados_wizard_cronograma,
    preparar_transicao_wizard_cronograma,
    resolver_selecao_wizard_cronograma,
    selecao_turmas_wizard_valida,
    selecionar_turmas_wizard,
    turmas_wizard_compativeis_com_tipo_periodo,
    montar_tema_licao_cronograma,
    preparar_contexto_periodos_listagem_turmas,
    tipo_periodo_ebd_valido,
    validar_ano_letivo,
    persistir_licoes_geradas,
)
from escola_biblica.services_analiticos import (
    calcular_distribuicao_faixa_etaria,
    calcular_media_frequencia_alunos,
    calcular_percentual_engajamento_alunos,
    construir_meses_evolucao,
    construir_ofertas_evolucao,
    construir_ranking_alunos_pontos,
    construir_ranking_classes,
    construir_ranking_ofertas,
    coletar_movimentacao_alunos,
    calcular_totais_ofertas_periodos,
)
from escola_biblica.services_configuracao import aplicar_fallback_pontos_ebd
from escola_biblica.services_relatorios import coletar_dados_relatorio_instantaneo
from escola_biblica.services_vinculos import (
    aplicar_vinculos_selecionados_em_lote,
    tentar_vinculos_em_lote,
)
from escola_biblica.utils import gerar_periodos_ebd
from escola_biblica.utils import gerar_licoes_periodos


class EBDPontosHelpersTest(TestCase):
    def test_normalizacao_da_etapa_do_wizard_de_cronograma(self):
        self.assertEqual(normalizar_etapa_wizard_cronograma('3'), 3)
        self.assertEqual(normalizar_etapa_wizard_cronograma('invalida'), 1)
        self.assertEqual(normalizar_etapa_wizard_cronograma('99'), 1)

    def test_normalizacao_dos_campos_numericos_do_wizard_de_cronograma(self):
        self.assertEqual(normalizar_inteiro_wizard_cronograma('2026'), 2026)
        self.assertEqual(normalizar_inteiro_wizard_cronograma('invalido', 2026), 2026)
        self.assertEqual(normalizar_inteiro_wizard_cronograma(None), 0)

    def test_validacao_do_ano_letivo_rejeita_valores_fora_da_faixa(self):
        self.assertEqual(validar_ano_letivo('2.026'), 2026)
        with self.assertRaises(ValueError):
            validar_ano_letivo('2026.5')
        with self.assertRaises(ValueError):
            validar_ano_letivo('invalido')

    def test_validacao_do_tipo_de_periodo_da_ebd(self):
        self.assertTrue(tipo_periodo_ebd_valido('trimestre'))
        self.assertTrue(tipo_periodo_ebd_valido('semestre'))
        self.assertFalse(tipo_periodo_ebd_valido('mensal'))
        self.assertFalse(tipo_periodo_ebd_valido(None))

    def test_ano_letivo_da_criacao_de_turma_respeita_parametro_ou_usa_atual(self):
        ano_futuro = AnoLetivo.objects.create(ano=2098, ativo=True)

        self.assertEqual(
            obter_ano_letivo_para_criacao_turma(
                ano_letivo_raw='2.098',
                ano_atual=2026,
            ),
            ano_futuro,
        )
        ano_padrao = obter_ano_letivo_para_criacao_turma(
            ano_letivo_raw='invalido',
            ano_atual=2099,
        )
        self.assertEqual(ano_padrao.ano, 2099)
        self.assertTrue(ano_padrao.ativo)

    def test_horario_ebd_formatado_para_o_wizard(self):
        self.assertEqual(
            obter_horario_ebd_formatado(SimpleNamespace(ebd_horario='09:30:00')),
            '09:30',
        )
        self.assertEqual(
            obter_horario_ebd_formatado(SimpleNamespace(ebd_horario=timezone.datetime(2026, 1, 1, 18, 45).time())),
            '18:45',
        )
        self.assertEqual(obter_horario_ebd_formatado(None), '')

    def test_dados_do_wizard_aplicam_horario_padrao_quando_solicitado(self):
        parametros = RequestFactory().post(
            '/',
            {'ano_letivo': '2026', 'periodo': '3', 'turmas': ['1', '2'], 'material': 'Revista'},
        ).POST

        dados = preparar_dados_wizard_cronograma(
            parametros=parametros,
            ano_atual=2026,
            horario_padrao='09:00',
            usar_horario_padrao=True,
        )

        self.assertEqual(dados['ano_letivo'], 2026)
        self.assertEqual(dados['periodo'], 3)
        self.assertEqual(dados['turmas_ids'], [1, 2])
        self.assertEqual(dados['horario'], '09:00')

    def test_transicao_do_wizard_reune_dados_selecao_e_nome_do_periodo(self):
        periodo = SimpleNamespace(numero=2, get_tipo_display=lambda: 'Trimestre')
        turmas = SimpleNamespace()
        dados = {
            'ano_letivo': 2026,
            'periodo': 2,
            'turmas_ids': [10],
        }
        selecao = {'periodo': periodo, 'turmas': [], 'valida': True, 'mensagem_erro': ''}

        with patch(
            'escola_biblica.services_periodos.preparar_dados_wizard_cronograma',
            return_value=dados,
        ) as preparar_dados, patch(
            'escola_biblica.services_periodos.resolver_selecao_wizard_cronograma',
            return_value=selecao,
        ) as resolver_selecao:
            transicao = preparar_transicao_wizard_cronograma(
                parametros=SimpleNamespace(),
                ano_atual=2026,
                turmas=turmas,
                tipo_periodo='trimestre',
                hoje=timezone.datetime(2026, 8, 20).date(),
                horario_padrao='09:00',
                usar_horario_padrao=True,
            )

        self.assertEqual(transicao['dados'], dados)
        self.assertEqual(transicao['selecao'], selecao)
        self.assertEqual(transicao['periodo_nome'], 'Trimestre 2')
        preparar_dados.assert_called_once()
        resolver_selecao.assert_called_once_with(
            turmas=turmas,
            turmas_ids=[10],
            ano_letivo=2026,
            numero_periodo=2,
            tipo_periodo='trimestre',
            hoje=timezone.datetime(2026, 8, 20).date(),
        )

    def test_contexto_do_formulario_wizard_preserva_campos_entre_etapas(self):
        dados = {
            'ano_letivo': 2026,
            'periodo': 3,
            'turmas_ids': [1, 2],
            'material': 'Revista',
            'horario': '09:00',
            'status': 'ativa',
            'observacoes': 'Observacao',
            'nome_licao_padrao': 'Licao {n}',
        }

        contexto = construir_contexto_formulario_wizard_cronograma(
            dados=dados,
            horario='10:00',
            etapa=2,
        )

        self.assertEqual(contexto['turmas'], [1, 2])
        self.assertEqual(contexto['horario'], '10:00')
        self.assertEqual(contexto['nome_licao_padrao'], 'Licao {n}')
        self.assertEqual(contexto['etapa'], 2)

    def test_dados_do_wizard_ignoram_ids_de_turma_invalidos_e_duplicados(self):
        parametros = RequestFactory().post(
            '/',
            {'turmas': ['1', 'invalido', '-2', '1', '3.0']},
        ).POST

        dados = preparar_dados_wizard_cronograma(
            parametros=parametros,
            ano_atual=2026,
        )

        self.assertEqual(dados['turmas_ids'], [1])

    def test_status_do_wizard_usa_apenas_opcoes_validas_de_licao(self):
        self.assertEqual(normalizar_status_licao_wizard('rascunho'), 'rascunho')
        self.assertEqual(normalizar_status_licao_wizard('valor-invalido'), 'ativa')

        dados = preparar_dados_wizard_cronograma(
            parametros=RequestFactory().post('/', {'status': 'valor-invalido'}).POST,
            ano_atual=2026,
        )

        self.assertEqual(dados['status'], 'ativa')

    def test_horario_do_wizard_e_normalizado_sem_aceitar_valores_invalidos(self):
        self.assertEqual(normalizar_horario_wizard('09:30:00'), '09:30')
        self.assertEqual(normalizar_horario_wizard('horario-invalido'), '')

        dados = preparar_dados_wizard_cronograma(
            parametros=RequestFactory().post('/', {'horario': 'horario-invalido'}).POST,
            ano_atual=2026,
        )

        self.assertEqual(dados['horario'], '')

    def test_nome_da_licao_do_wizard_e_normalizado_e_respeita_limite_do_modelo(self):
        self.assertEqual(normalizar_nome_licao_padrao('   '), 'Lição {n} - {periodo}')
        tema = montar_tema_licao_cronograma(
            nome_licao_padrao='X' * 250,
            indice=1,
            periodo_nome='Trimestre 1',
        )

        self.assertEqual(len(tema), 200)

    def test_material_do_wizard_respeita_limite_do_modelo(self):
        self.assertEqual(normalizar_material_wizard('  Revista  '), 'Revista')
        self.assertEqual(len(normalizar_material_wizard('X' * 300)), 255)

        dados = preparar_dados_wizard_cronograma(
            parametros=RequestFactory().post('/', {'material': 'X' * 300}).POST,
            ano_atual=2026,
        )

        self.assertEqual(len(dados['material']), 255)

    def test_validacao_da_selecao_do_wizard_exige_todas_as_turmas(self):
        turmas = SimpleNamespace(count=lambda: 1)

        self.assertTrue(selecao_turmas_wizard_valida(turmas=turmas, turmas_ids=[1]))
        self.assertFalse(selecao_turmas_wizard_valida(turmas=turmas, turmas_ids=[1, 2]))

    def test_selecao_do_wizard_restringe_turmas_ao_ano_informado(self):
        ano_2026 = AnoLetivo.objects.create(ano=2026)
        ano_2027 = AnoLetivo.objects.create(ano=2027)
        administrador = get_user_model().objects.create_user(
            username='admin_teste_wizard',
            password='senha123',
        )
        ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio teste wizard',
            administrador_principal=administrador,
        )
        igreja = Igreja.objects.create(
            ministerio=ministerio,
            nome_igreja='Igreja teste wizard',
        )
        classe = Classe.objects.create(igreja=igreja, nome='Classe teste wizard')
        turma_2026 = Turma.objects.create(
            nome='Turma 2026', igreja=igreja, classe=classe, ano_letivo=ano_2026,
        )
        turma_2027 = Turma.objects.create(
            nome='Turma 2027', igreja=igreja, classe=classe, ano_letivo=ano_2027,
        )

        turmas = selecionar_turmas_wizard(
            turmas=Turma.objects.all(),
            turmas_ids=[turma_2026.id, turma_2027.id],
            ano_letivo=2026,
        )

        self.assertEqual(list(turmas), [turma_2026])

        periodo = PeriodoEBD.objects.create(
            ano_letivo=ano_2026,
            numero=1,
            tipo='trimestre',
            data_inicio=timezone.datetime(2026, 1, 1).date(),
            data_fim=timezone.datetime(2026, 3, 31).date(),
        )
        selecao = resolver_selecao_wizard_cronograma(
            turmas=Turma.objects.all(),
            turmas_ids=[turma_2026.id],
            ano_letivo=2026,
            numero_periodo=periodo.numero,
            tipo_periodo='trimestre',
            hoje=timezone.datetime(2026, 2, 1).date(),
        )

        self.assertTrue(selecao['valida'])
        self.assertEqual(selecao['periodo'], periodo)
        self.assertEqual(list(selecao['turmas']), [turma_2026])

    def test_periodo_do_wizard_precisa_estar_aberto(self):
        ano = AnoLetivo.objects.create(ano=2026)
        encerrado = PeriodoEBD.objects.create(
            ano_letivo=ano,
            numero=1,
            tipo='trimestre',
            data_inicio=timezone.datetime(2026, 1, 1).date(),
            data_fim=timezone.datetime(2026, 3, 31).date(),
        )
        aberto = PeriodoEBD.objects.create(
            ano_letivo=ano,
            numero=2,
            tipo='trimestre',
            data_inicio=timezone.datetime(2026, 4, 1).date(),
            data_fim=timezone.datetime(2026, 6, 30).date(),
        )
        PeriodoEBD.objects.create(
            ano_letivo=ano,
            numero=2,
            tipo='semestre',
            data_inicio=timezone.datetime(2026, 1, 1).date(),
            data_fim=timezone.datetime(2026, 6, 30).date(),
        )
        hoje = timezone.datetime(2026, 5, 1).date()

        self.assertIsNone(obter_periodo_wizard_disponivel(
            ano_letivo=2026, numero=encerrado.numero, tipo_periodo='trimestre', hoje=hoje,
        ))
        self.assertEqual(
            obter_periodo_wizard_disponivel(
                ano_letivo=2026, numero=aberto.numero, tipo_periodo='trimestre', hoje=hoje,
            ),
            aberto,
        )

    def test_agrupamento_de_turmas_usa_a_configuracao_efetiva_do_calendario(self):
        configuracao_comum = SimpleNamespace(
            ebd_periodo='trimestre', ebd_dia_semana=6, ebd_horario='09:00',
        )
        primeira = SimpleNamespace(configuracao=configuracao_comum)
        segunda = SimpleNamespace(configuracao=configuracao_comum)
        terceira = SimpleNamespace(
            configuracao=SimpleNamespace(
                ebd_periodo='semestre', ebd_dia_semana=2, ebd_horario='18:00',
            ),
        )

        grupos = agrupar_turmas_por_calendario(
            turmas=[primeira, segunda, terceira],
            obter_configuracao_turma=lambda turma: turma.configuracao,
        )

        self.assertEqual(len(grupos), 2)
        self.assertEqual(grupos[('trimestre', 6, '09:00')], [primeira, segunda])
        self.assertEqual(grupos[('semestre', 2, '18:00')], [terceira])

    def test_wizard_nao_mistura_turmas_de_tipos_de_periodo_diferentes(self):
        turmas = [SimpleNamespace(tipo='trimestre'), SimpleNamespace(tipo='semestre')]

        compativeis = turmas_wizard_compativeis_com_tipo_periodo(
            turmas=turmas,
            tipo_periodo='trimestre',
            obter_configuracao_turma=lambda turma: SimpleNamespace(ebd_periodo=turma.tipo),
        )

        self.assertFalse(compativeis)

    def test_servico_de_paginacao_aplica_fallbacks(self):
        primeira_pagina = paginar_queryset(
            queryset=[1, 2, 3], pagina='invalida', por_pagina=1,
        )
        ultima_pagina = paginar_queryset(
            queryset=[1, 2, 3], pagina='99', por_pagina=1,
        )

        self.assertEqual(list(primeira_pagina.object_list), [1])
        self.assertEqual(list(ultima_pagina.object_list), [3])

    def test_servico_monta_status_de_periodo_programado_e_encerrado(self):
        periodo = SimpleNamespace(
            data_inicio=timezone.datetime(2026, 8, 2).date(),
            data_fim=timezone.datetime(2026, 8, 30).date(),
        )

        programado = construir_status_periodo(
            periodo=periodo,
            hoje=timezone.datetime(2026, 8, 1).date(),
        )
        encerrado = construir_status_periodo(
            periodo=periodo,
            hoje=timezone.datetime(2026, 9, 1).date(),
        )

        self.assertEqual(programado['ebd_status_label'], 'Programado')
        self.assertEqual(programado['ebd_aulas_realizadas'], 0)
        self.assertEqual(encerrado['ebd_status_label'], 'Encerrado')
        self.assertEqual(encerrado['ebd_aulas_total'], 5)
        self.assertEqual(encerrado['ebd_aulas_realizadas'], 5)
        self.assertEqual(encerrado['ebd_percentual'], 100)

    def test_fechamento_de_periodo_exige_fim_e_chamadas_de_aulas_previstas(self):
        periodo = SimpleNamespace(
            data_fim=timezone.datetime(2026, 8, 30).date(),
        )
        aula_1 = (10, timezone.datetime(2026, 8, 9).date())
        aula_2 = (10, timezone.datetime(2026, 8, 16).date())

        antes_do_fim = avaliar_prontidao_fechamento_periodo(
            periodo=periodo,
            hoje=timezone.datetime(2026, 8, 30).date(),
            aulas_previstas=[aula_1],
            chamadas_realizadas=[aula_1],
        )
        com_pendencia = avaliar_prontidao_fechamento_periodo(
            periodo=periodo,
            hoje=timezone.datetime(2026, 8, 31).date(),
            aulas_previstas=[aula_1, aula_2],
            chamadas_realizadas=[aula_1],
        )
        pronto = avaliar_prontidao_fechamento_periodo(
            periodo=periodo,
            hoje=timezone.datetime(2026, 8, 31).date(),
            aulas_previstas=[aula_1, aula_2],
            chamadas_realizadas=[aula_1, aula_2],
        )
        com_excecao = avaliar_prontidao_fechamento_periodo(
            periodo=periodo,
            hoje=timezone.datetime(2026, 8, 31).date(),
            aulas_previstas=[aula_1, aula_2],
            chamadas_realizadas=[aula_1],
            motivo_excecao='Congresso regional da igreja.',
        )

        self.assertFalse(antes_do_fim['pode_fechar'])
        self.assertFalse(com_pendencia['pode_fechar'])
        self.assertEqual(com_pendencia['aulas_pendentes'], [aula_2])
        self.assertTrue(pronto['pode_fechar'])
        self.assertEqual(pronto['tipo_fechamento'], 'normal')
        self.assertTrue(com_excecao['pode_fechar'])
        self.assertEqual(com_excecao['tipo_fechamento'], 'excecao')

    def test_diagnostico_de_fechamento_inclui_nome_da_turma_pendente(self):
        periodo = SimpleNamespace(
            data_inicio=timezone.datetime(2026, 8, 1).date(),
            data_fim=timezone.datetime(2026, 8, 30).date(),
        )
        turma = SimpleNamespace(id=10, nome='Jovens')
        turmas = SimpleNamespace(
            filter=lambda **kwargs: turmas,
            distinct=lambda: turmas,
            values_list=lambda *args: [(10, 'Jovens')],
        )
        with patch('escola_biblica.services_periodos.Licao.objects.filter') as licoes, patch(
            'escola_biblica.services_periodos.Frequencia.objects.filter',
        ) as frequencias:
            licoes.return_value.values_list.return_value.distinct.return_value = [(10, timezone.datetime(2026, 8, 9).date())]
            frequencias.return_value.values_list.return_value.distinct.return_value = []
            resultado = diagnosticar_fechamento_periodo(
                turmas=turmas, periodo=periodo, hoje=timezone.datetime(2026, 8, 31).date(),
            )
        self.assertFalse(resultado['pode_fechar'])
        self.assertEqual(resultado['pendencias'][0]['turma_nome'], 'Jovens')

    def test_contexto_do_periodo_do_dashboard_reune_recortes_e_rotulos(self):
        hoje = timezone.datetime(2026, 8, 20).date()
        contexto = preparar_contexto_periodo_dashboard(
            periodo_ctx={
                'tipo_periodo': 'trimestre',
                'anos_letivos': [],
                'ano_letivo_selecionado': None,
                'periodos_disponiveis': [],
                'periodo_selecionado': None,
            },
            periodo_tipo_label='Trimestre',
            hoje=hoje,
        )

        self.assertEqual(contexto['inicio_atual'], hoje.replace(day=1))
        self.assertEqual(contexto['fim_atual'], hoje)
        self.assertEqual(contexto['periodo_selecionado_label'], '01/08/2026 a 20/08/2026')
        self.assertEqual(contexto['periodo_tipo_label'], 'Trimestre')

    def test_contexto_operacional_do_dashboard_reune_escopo_resumo_e_decisao(self):
        contexto = preparar_contexto_operacional_dashboard(
            igreja=SimpleNamespace(nome_igreja='Igreja Teste'),
            igrejas_escopo=SimpleNamespace(count=lambda: 1),
            ano_letivo=None,
            ano_atual=2026,
            ministerio=None,
            hoje=timezone.datetime(2026, 8, 20).date(),
            pode_gerenciar_ebd=True,
            alunos_novos=2,
            alunos_novos_anterior=1,
            frequencia_atual=75,
            frequencia_anterior=70,
            ofertas_atual=20,
            ofertas_anterior=10,
            evasao=0,
            turmas_previstas_semana=1,
            turmas_sem_chamada_semana=0,
            houve_janela_operacional=True,
            turmas_pendentes_relatorio=0,
            turmas_parciais_relatorio=0,
            relatorio_instantaneo_turmas=[],
        )

        self.assertEqual(contexto['scope_label'], 'Igreja: Igreja Teste')
        self.assertEqual(contexto['ano_destino_preparo'], 2027)
        self.assertFalse(contexto['pode_publicar_resumo_semanal'])
        self.assertEqual(contexto['bloco_decisao']['comparativos'][0]['atual'], 2)

    def test_contexto_template_dashboard_mantem_contrato_dos_cards(self):
        colecao = SimpleNamespace(count=lambda: 2)
        contexto = construir_contexto_template_dashboard(
            turmas=colecao, alunos=colecao, classes=colecao, licoes=colecao, avaliacoes=colecao,
            total_oferta=100, total_ofertas_mes=20, total_ofertas_mes_anterior=10,
            alunos_evolucao=[1], engajamento_percent=80, evasao=0,
            ranking_classes=[], ranking_alunos_pontos=[], frequencia_atual=80,
            frequencia_anterior=70, ranking_ofertas=[], kpis_turma_professor=list(range(8)),
            alunos_novos=2, alunos_novos_anterior=1, transferidos_mes=0,
            meses=[timezone.datetime(2026, 8, 1).date()], faixas_etarias_labels=['Adultos'],
            faixas_etarias_counts=[2],
            operacao_diaria={
                'data_relatorio': timezone.datetime(2026, 8, 20).date(), 'relatorio_turmas': [],
                'pendentes_relatorio': 1, 'parciais_relatorio': 0, 'completas_relatorio': 0,
                'turmas_previstas_semana': 1, 'turmas_com_chamada_semana': 0,
                'turmas_sem_chamada_semana': 1, 'houve_janela': True,
            },
            contexto_operacional={
                'bloco_decisao': {
                    'comparativos': [], 'insights': ['a', 'b', 'c', 'd'], 'painel_executivo': {},
                    'centro_acoes': [], 'checklist': [],
                },
                'resumo_semanal': None, 'resumo_semanal_formatado': '',
                'pode_publicar_resumo_semanal': True, 'ano_destino_preparo': 2027,
                'scope_label': 'Igreja: Teste',
            },
            pode_gerenciar_ebd=True,
            contexto_periodo={
                'periodo_anterior_label': '01/07/2026 a 31/07/2026',
                'periodo_selecionado_label': '01/08/2026 a 20/08/2026',
                'periodo_tipo_label': 'Trimestre', 'tipo_periodo': 'trimestre',
                'anos_letivos': [], 'ano_letivo_selecionado': None,
                'periodos_disponiveis': [], 'periodo_selecionado': None,
            },
            ebd_config_igreja_link='/configuracao/',
            ebd_config_source_info={
                'ebd_config_source': 'igreja', 'ebd_config_source_label': 'Igreja',
                'ebd_config_source_hint': 'Configuracao local',
            },
            ebd_pontos_config={},
        )

        self.assertEqual(contexto['total_turmas'], 2)
        self.assertEqual(contexto['meses'], ['08/2026'])
        self.assertEqual(contexto['kpis_turma_professor'], list(range(6)))
        self.assertEqual(contexto['insights_dashboard'], ['a', 'b', 'c'])
        self.assertEqual(contexto['turmas_pendentes_relatorio'], 1)

    def test_contexto_template_de_alunos_mantem_filtros_e_paginacao(self):
        contexto = construir_contexto_template_listagem_alunos(
            contexto_listagem={'turmas': ['turma'], 'ano_filtro': 2026},
            alunos_paginados=['aluno'],
            total_alunos=1,
            usuario_pode_vincular=True,
        )

        self.assertEqual(contexto['turmas'], ['turma'])
        self.assertEqual(contexto['alunos'], ['aluno'])
        self.assertEqual(contexto['total_alunos'], 1)
        self.assertTrue(contexto['usuario_pode_vincular'])

    def test_contexto_template_de_turmas_mantem_contrato_de_filtros_e_status(self):
        request = SimpleNamespace()
        contexto = construir_contexto_template_listagem_turmas(
            turmas=['turma'],
            turmas_total=1,
            contexto_periodos={
                'anos_letivos': ['2026'], 'ano_letivo_selecionado': '2026',
                'periodos': ['3'], 'periodo_selecionado': '3',
                'periodo_filtro_chip': 'Trimestre 3',
                'mostrar_banner_abrir_periodo': False, 'sugerir_copiar': True,
            },
            filtros_listagem={
                'turmas_disponiveis': ['turma'], 'classes_disponiveis': ['classe'],
            },
            turma_filtro='turma',
            classe_filtro='classe',
            tipo_periodo='trimestre',
            now=timezone.datetime(2026, 8, 20).date(),
            request=request,
            status_periodo={'ebd_status_label': 'Em andamento'},
            ebd_periodo_atual='periodo',
            ebd_config_source_info={
                'ebd_config_source': 'igreja', 'ebd_config_source_label': 'Igreja',
                'ebd_config_source_hint': 'Configuracao local',
            },
            querystring='ano_letivo=2026',
        )

        self.assertEqual(contexto['turmas_total'], 1)
        self.assertEqual(contexto['ebd_status_label'], 'Em andamento')
        self.assertEqual(contexto['classe_filtro'], 'classe')
        self.assertIs(contexto['request'], request)

    def test_contexto_de_periodos_mantem_fallback_e_selecao_atual(self):
        ano = AnoLetivo.objects.create(ano=2026, ativo=True)
        periodo = PeriodoEBD.objects.create(
            ano_letivo=ano,
            tipo='trimestre',
            numero=3,
            data_inicio=timezone.datetime(2026, 7, 1).date(),
            data_fim=timezone.datetime(2026, 9, 30).date(),
        )

        contexto = preparar_contexto_periodos_listagem_turmas(
            ano_letivo_raw='2026',
            periodo_raw='3',
            tipo_periodo='trimestre',
            hoje=timezone.datetime(2026, 8, 19).date(),
        )
        fallback = preparar_contexto_periodos_listagem_turmas(
            ano_letivo_raw='2030',
            periodo_raw='',
            tipo_periodo='trimestre',
            hoje=timezone.datetime(2026, 8, 19).date(),
        )

        self.assertEqual(contexto['ano_letivo_selecionado'], ano)
        self.assertEqual(contexto['periodo_selecionado'], periodo)
        self.assertEqual(fallback['ano_letivo_selecionado'], ano)

    def test_geracao_de_cronograma_usa_configuracao_da_turma(self):
        turma = SimpleNamespace()
        configuracao = SimpleNamespace(ebd_horario='09:00')

        with patch(
            'escola_biblica.services_configuracao.obter_configuracao_ebd_turma',
            return_value=configuracao,
        ), patch(
            'escola_biblica.services_configuracao.obter_tipo_periodo_ebd',
            return_value='trimestre',
        ), patch(
            'escola_biblica.services_configuracao.obter_dia_semana_ebd',
            return_value=6,
        ), patch(
            'escola_biblica.services_periodos.gerar_e_persistir_licoes_periodos',
            return_value=3,
        ) as gerar_licoes:
            resultado = gerar_cronograma_para_turma(
                ano=2026,
                turma_selecionada=turma,
                turmas_escopo=[turma],
                material='Revista',
                observacoes='Planejamento inicial',
            )

        self.assertEqual(resultado, {'criadas': 3, 'tipo_periodo': 'trimestre'})
        gerar_licoes.assert_called_once_with(
            ano=2026,
            tipo_periodo='trimestre',
            turmas=[turma],
            material='Revista',
            observacoes='Planejamento inicial',
            horario='09:00',
            status='ativa',
            dia_semana=6,
        )

    def test_servico_monta_previa_de_cronograma(self):
        class TurmaTeste:
            nome = 'Turma Adultos'

            def get_professor_nome(self):
                return 'Professora Ana'

        periodo = SimpleNamespace(
            data_inicio=timezone.datetime(2026, 8, 2).date(),
            data_fim=timezone.datetime(2026, 8, 9).date(),
        )

        previa = construir_previa_cronograma(
            turmas=[TurmaTeste()],
            periodo=periodo,
            periodo_nome='Trimestre 3',
            nome_licao_padrao='Licao {n} - {periodo}',
            status='ativa',
        )

        self.assertEqual(len(previa), 2)
        self.assertEqual(previa[0]['tema'], 'Licao 1 - Trimestre 3')
        self.assertEqual(previa[1]['professor'], 'Professora Ana')

    def test_wizard_usa_o_dia_configurado_para_a_turma(self):
        periodo = SimpleNamespace(
            data_inicio=timezone.datetime(2026, 8, 1).date(),
            data_fim=timezone.datetime(2026, 8, 15).date(),
        )

        with patch(
            'escola_biblica.services_configuracao.obter_configuracao_ebd_turma',
            return_value=SimpleNamespace(ebd_dia_semana=5),
        ):
            datas = obter_datas_aula_wizard_cronograma(
                turma=SimpleNamespace(),
                periodo=periodo,
            )

        self.assertEqual(
            datas,
            [timezone.datetime(2026, 8, 1).date(), timezone.datetime(2026, 8, 8).date(), timezone.datetime(2026, 8, 15).date()],
        )

    def test_gerador_de_cronograma_mantem_objeto_do_professor(self):
        professor = SimpleNamespace(nome='Professora Ana')

        class TurmaTeste:
            def get_professor_ebd(self):
                return professor

        licoes = gerar_licoes_periodos(
            ano=2026,
            tipo_periodo='ano',
            turmas=[TurmaTeste()],
        )

        self.assertTrue(licoes)
        self.assertIs(licoes[0]['professor'], professor)

    def test_servico_aplica_vinculos_selecionados_com_escopo_de_igreja(self):
        class CadastroTeste:
            def __init__(self, cadastro_id, nome, igreja_id):
                self.id = cadastro_id
                self.nome = nome
                self.igreja_id = igreja_id
                self.pessoa = None
                self.salvo = False

            def save(self):
                self.salvo = True

        cadastro = CadastroTeste(1, 'Ana', 10)
        pessoa = SimpleNamespace(nome='Ana Pessoa')
        chamadas_busca = []

        resultado = aplicar_vinculos_selecionados_em_lote(
            cadastros=[cadastro],
            pessoa_ids_por_cadastro={1: '20'},
            buscar_pessoa=lambda pessoa_id, igreja_id: (
                chamadas_busca.append((pessoa_id, igreja_id)) or pessoa
            ),
        )

        self.assertTrue(cadastro.salvo)
        self.assertIs(cadastro.pessoa, pessoa)
        self.assertEqual(chamadas_busca, [('20', 10)])
        self.assertEqual(resultado, {
            'vinculos_realizados': ['Ana -> Ana Pessoa'],
            'total_vinculos': 1,
        })

    def test_servico_tenta_vinculos_em_lote_e_resume_resultado(self):
        class CadastroTeste:
            def __init__(self, nome, pessoa):
                self.nome = nome
                self.pessoa = pessoa
                self.salvo = False

            def tentar_vincular_pessoa(self, force=False):
                self.assert_force = force
                return self.pessoa

            def save(self):
                self.salvo = True

        cadastro_vinculado = CadastroTeste('Ana', SimpleNamespace(nome='Ana Secretaria'))
        cadastro_sem_correspondencia = CadastroTeste('Bia', None)

        resultado = tentar_vinculos_em_lote([cadastro_vinculado, cadastro_sem_correspondencia])

        self.assertEqual(resultado, {
            'vinculados': 1,
            'sem_correspondencia': 1,
            'detalhes': ['Ana -> Ana Secretaria'],
        })
        self.assertTrue(cadastro_vinculado.salvo)

    def test_servico_formata_cartao_comparativo_de_frequencia(self):
        card = construir_comparativo_card(
            'Frequência média',
            72.5,
            68.0,
            formato='percent',
        )

        self.assertEqual(card['diferenca_label'], '+4.5')
        self.assertEqual(card['tone'], 'is-positive')
        self.assertEqual(card['icon'], 'fas fa-arrow-up')

    def test_chave_de_cache_do_dashboard_separa_os_recortes(self):
        chave = construir_chave_cache_dashboard(
            versao=2,
            usuario_id=10,
            igreja_id=4,
            tipo_periodo='trimestre',
            ano_letivo='2026',
            periodo='3',
            data_relatorio='2026-08-20',
        )

        self.assertEqual(
            chave,
            'ebd:dashboard:v2:u10:ig4:tp:trimestre:a:2026:p:3:r:2026-08-20:summary_scope_v2',
        )

    def test_servico_distribui_alunos_por_faixa_etaria(self):
        hoje = timezone.datetime(2026, 8, 18).date()
        labels, contagens = calcular_distribuicao_faixa_etaria(
            alunos=[
                SimpleNamespace(data_nascimento=timezone.datetime(2023, 8, 18).date()),
                SimpleNamespace(data_nascimento=timezone.datetime(2016, 8, 18).date()),
                SimpleNamespace(data_nascimento=timezone.datetime(1960, 8, 18).date()),
                SimpleNamespace(data_nascimento=None),
            ],
            hoje=hoje,
        )

        self.assertEqual(labels, ['0-5', '6-12', '13-17', '18-29', '30-59', '60+'])
        self.assertEqual(contagens, [1, 1, 0, 0, 0, 1])

    def test_servico_monta_meses_do_periodo_inclusive(self):
        periodo = SimpleNamespace(
            data_inicio=timezone.datetime(2026, 2, 18).date(),
            data_fim=timezone.datetime(2026, 4, 3).date(),
        )

        meses = construir_meses_evolucao(
            periodo=periodo,
            ano_letivo=None,
            hoje=timezone.datetime(2026, 8, 18).date(),
        )

        self.assertEqual(meses, [
            timezone.datetime(2026, 2, 1).date(),
            timezone.datetime(2026, 3, 1).date(),
            timezone.datetime(2026, 4, 1).date(),
        ])

    def test_servico_pontos_aplica_padrao_sem_sobrescrever_configurado(self):
        pontos = aplicar_fallback_pontos_ebd({
            'presente': None,
            'biblia': '4',
            'revista': None,
            'oferta': 7,
            'visitante': None,
        })

        self.assertEqual(pontos, {
            'presente': 10,
            'biblia': 4,
            'revista': 2,
            'oferta': 7,
            'visitante': 5,
        })

    def test_contexto_de_exibicao_da_chamada_mantem_periodo_oferta_e_bloqueio(self):
        data = timezone.datetime(2026, 8, 16).date()
        periodo = SimpleNamespace(
            numero=3,
            data_inicio=timezone.datetime(2026, 7, 1).date(),
            data_fim=timezone.datetime(2026, 9, 30).date(),
            get_tipo_display=lambda: 'Trimestre',
        )
        calendario = {
            'periodo': periodo,
            'data_selecionada': data,
            'datas_com_licao': [data],
            'opcoes_aula': [{'value': data.isoformat()}],
            'licao_do_dia': SimpleNamespace(),
            'status_aula_selecionada': 'passada',
        }

        contexto = preparar_contexto_exibicao_chamada(
            calendario=calendario,
            oferta_atual=SimpleNamespace(valor=12.5),
            bloqueio_chamada_msg=None,
        )

        self.assertEqual(contexto['data'], '2026-08-16')
        self.assertEqual(contexto['periodo_label'], 'Trimestre 3 (01/07/2026 - 30/09/2026)')
        self.assertEqual(contexto['valor_oferta_atual'], '12.50')
        self.assertIsNone(contexto['bloqueio_chamada_msg'])

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
        painel = construir_painel_executivo_ebd(
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
        painel = construir_painel_executivo_ebd(
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

    def test_bloco_decisao_reune_os_componentes_do_dashboard(self):
        bloco = construir_bloco_decisao_dashboard(
            alunos_novos=4,
            alunos_novos_anterior=2,
            frequencia_atual=82,
            frequencia_anterior=75,
            ofertas_atual=120,
            ofertas_anterior=100,
            evasao=0,
            turmas_previstas_semana=3,
            turmas_sem_chamada_semana=0,
            houve_janela_operacional=True,
            turmas_pendentes_relatorio=0,
            turmas_parciais_relatorio=0,
            resumo_semanal={'turmas_pendentes': 0},
            pode_publicar_resumo_semanal=True,
            relatorio_instantaneo_turmas=[],
        )

        self.assertEqual(len(bloco['comparativos']), 3)
        self.assertEqual(bloco['comparativos'][0]['diferenca_label'], '+2')
        self.assertTrue(bloco['insights'])
        self.assertIn('recomendacoes', bloco['painel_executivo'])
        self.assertEqual(len(bloco['checklist']), 4)
        self.assertIn('fila', bloco['centro_acoes'])


class EBDRelatorioInstantaneoServiceTest(TestCase):
    def test_servicos_constroem_rankings_ordenados(self):
        ranking_classes = construir_ranking_classes([
            {'aluno__turma__classe__nome': 'Jovens', 'total': 4, 'presentes': 2},
            {'aluno__turma__classe__nome': 'Adultos', 'total': 5, 'presentes': 5},
        ])
        aluno = SimpleNamespace(
            cadastro=SimpleNamespace(nome='Ana'),
            turma_id=2,
            turma=SimpleNamespace(nome='Turma A', classe_id=3, classe=SimpleNamespace(nome='Adultos')),
        )
        ranking_alunos = construir_ranking_alunos_pontos(
            pontos_por_cadastro=[
                {'aluno__cadastro_id': 1, 'total_pontos': 15, 'presencas': 2},
            ],
            referencias_por_cadastro={1: aluno},
        )

        self.assertEqual(ranking_classes[0]['classe'], 'Adultos')
        self.assertEqual(ranking_alunos[0]['nome'], 'Ana')
        self.assertEqual(ranking_alunos[0]['posicao'], 1)

    def test_calcula_janela_operacional_limitada_ao_periodo(self):
        janela = calcular_janela_operacional_semana(
            hoje=timezone.datetime(2026, 8, 18).date(),
            inicio_periodo=timezone.datetime(2026, 8, 17).date(),
            fim_periodo=timezone.datetime(2026, 8, 19).date(),
            dia_ebd=6,
        )

        self.assertEqual(janela['inicio'], timezone.datetime(2026, 8, 17).date())
        self.assertEqual(janela['fim'], timezone.datetime(2026, 8, 18).date())
        self.assertFalse(janela['houve_janela'])

    def test_servico_monta_e_prioriza_relatorio_instantaneo(self):
        classe = SimpleNamespace(id=7, nome='Adultos')
        turmas = [
            SimpleNamespace(id=2, nome='Betel', classe_id=7, classe=classe, matriculados_ativos=10),
            SimpleNamespace(id=1, nome='Ágape', classe_id=7, classe=classe, matriculados_ativos=8),
        ]

        relatorio = construir_relatorio_instantaneo_turmas(
            turmas=turmas,
            frequencias_por_turma={
                2: {'chamadas': 1, 'presentes': 7, 'biblias': 4, 'ofertas_individuais': 2},
            },
            ofertas_por_turma={2: 15},
            ofertas_por_classe={7: 5},
        )

        self.assertEqual([item['turma_nome'] for item in relatorio], ['Ágape', 'Betel'])
        self.assertEqual(relatorio[0]['status_tone'], 'is-pending')
        self.assertEqual(relatorio[1]['status_tone'], 'is-complete')
        self.assertEqual(relatorio[1]['ausentes'], 3)
        self.assertEqual(relatorio[1]['oferta_total'], 20)


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
        self.turma = Turma.objects.create(nome='Turma Teste', igreja=self.igreja, classe=classe, ano_letivo=self.ano_letivo)

        self.aluno = Aluno.objects.create(nome='Aluno Teste', turma=self.turma)

    def test_servico_prepara_calendario_e_seleciona_licao_de_hoje(self):
        hoje = timezone.localdate()
        licao = Licao.objects.create(turma=self.turma, data=hoje, tema='Licao atual')

        calendario = preparar_calendario_chamada(
            turma=self.turma,
            tipo_periodo='trimestre',
            dia_ebd=hoje.weekday(),
            hoje=hoje,
        )

        self.assertEqual(calendario['periodo'].ano_letivo, self.ano_letivo)
        self.assertEqual(calendario['data_selecionada'], hoje)
        self.assertEqual(calendario['licao_do_dia'], licao)
        self.assertEqual(calendario['opcoes_aula'][0]['tema'], 'Licao atual')

    def test_servico_prepara_formset_com_frequencia_existente(self):
        hoje = timezone.localdate()
        Frequencia.objects.create(
            aluno=self.aluno,
            data=hoje,
            presente=True,
            trouxe_biblia=True,
            trouxe_revista=False,
            trouxe_visitante=True,
            trouxe_oferta=False,
        )

        inicial = preparar_formset_inicial_chamada(
            alunos=self.turma.alunos.filter(ativo=True),
            data=hoje,
            formset_class=lambda *, initial: initial,
        )

        self.assertEqual(len(inicial), 1)
        self.assertTrue(inicial[0]['presente'])
        self.assertTrue(inicial[0]['trouxe_biblia'])
        self.assertFalse(inicial[0]['trouxe_revista'])
        self.assertTrue(inicial[0]['trouxe_visitante'])
        self.assertFalse(inicial[0]['trouxe_oferta'])

    def test_configuracao_da_igreja_tem_prioridade_na_geracao_da_turma(self):
        self.igreja.ebd_periodo = 'semestre'
        self.igreja.ebd_dia_semana = 2
        self.igreja.save(update_fields=['ebd_periodo', 'ebd_dia_semana'])

        configuracao = obter_configuracao_ebd_turma(self.turma)

        self.assertEqual(configuracao, self.igreja)
        self.assertEqual(configuracao.ebd_periodo, 'semestre')
        self.assertEqual(configuracao.ebd_dia_semana, 2)

    def test_ajax_professor_retorna_vazio_para_identificador_invalido(self):
        request = RequestFactory().get('/escola_biblica/professor-nome/', {'turma_id': 'invalida'})
        request.user = self.admin

        with patch('escola_biblica.views.filtrar_turmas_ebd', return_value=Turma.objects.all()):
            response = unwrap(
                __import__('escola_biblica.views', fromlist=['get_professor_nome']).get_professor_nome,
            )(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"professor": ""}')

    def test_copia_seletiva_rejeita_ano_destino_invalido(self):
        request = RequestFactory().get(
            '/escola_biblica/copiar_periodo_selecao/',
            {'ano_destino': 'ano-invalido'},
        )
        request.user = self.admin

        with patch('escola_biblica.views.messages.error') as erro:
            response = unwrap(
                __import__('escola_biblica.views', fromlist=['copiar_periodo_selecao']).copiar_periodo_selecao,
            )(request)

        self.assertEqual(response.status_code, 302)
        erro.assert_called_once()

    def test_resultado_da_copia_seletiva_consolida_contagens_e_novidades(self):
        resultado = consolidar_resultado_copia_seletiva(
            resultado_copia={
                'classes_criadas': 1,
                'turmas_criadas': 0,
                'membros_copiados': 2,
                'alunos_copiados': 0,
            },
            licoes_geradas=3,
        )

        self.assertTrue(resultado['tem_novidades'])
        self.assertEqual(resultado['classes_criadas'], 1)
        self.assertEqual(resultado['membros_copiados'], 2)
        self.assertEqual(resultado['licoes_geradas'], 3)

        vazio = consolidar_resultado_copia_seletiva(
            resultado_copia={
                'classes_criadas': 0,
                'turmas_criadas': 0,
                'membros_copiados': 0,
                'alunos_copiados': 0,
            },
            licoes_geradas=0,
        )
        self.assertFalse(vazio['tem_novidades'])

    def test_servico_copia_anual_completa_nao_duplica_turmas_ou_alunos(self):
        ano_destino = AnoLetivo.objects.create(ano=self.ano_letivo.ano + 1, ativo=True)
        turmas_origem = Turma.objects.filter(pk=self.turma.pk)

        primeira_copia = copiar_ano_anterior_completo(
            turmas_origem=turmas_origem,
            ano_letivo_destino=ano_destino,
        )
        segunda_copia = copiar_ano_anterior_completo(
            turmas_origem=turmas_origem,
            ano_letivo_destino=ano_destino,
        )
        turma_destino = Turma.objects.get(
            nome=self.turma.nome,
            igreja=self.igreja,
            ano_letivo=ano_destino,
        )

        self.assertEqual(primeira_copia, {'turmas_criadas': 1, 'alunos_copiados': 1})
        self.assertEqual(segunda_copia, {'turmas_criadas': 0, 'alunos_copiados': 0})
        self.assertEqual(Aluno.objects.filter(turma=turma_destino).count(), 1)

    def test_servico_copia_seletiva_retorna_turmas_destino_sem_duplicar_alunos(self):
        ano_destino = AnoLetivo.objects.create(ano=self.ano_letivo.ano + 1, ativo=True)
        turmas_origem = Turma.objects.filter(pk=self.turma.pk)
        classes_origem = Classe.objects.filter(pk=self.turma.classe_id)
        alunos_origem = Aluno.objects.filter(pk=self.aluno.pk)
        parametros = {
            'turmas_ids': [str(self.turma.id)],
            'classes_ids': [str(self.turma.classe_id)],
            'alunos_ids': [str(self.aluno.id)],
        }

        primeira_copia = copiar_dados_selecionados_para_ano(
            turmas_origem=turmas_origem,
            classes_origem=classes_origem,
            alunos_origem=alunos_origem,
            ano_letivo_destino=ano_destino,
            **parametros,
        )
        segunda_copia = copiar_dados_selecionados_para_ano(
            turmas_origem=turmas_origem,
            classes_origem=classes_origem,
            alunos_origem=alunos_origem,
            ano_letivo_destino=ano_destino,
            **parametros,
        )

        self.assertEqual(primeira_copia['turmas_criadas'], 1)
        self.assertEqual(primeira_copia['alunos_copiados'], 1)
        self.assertEqual(len(primeira_copia['turmas_destino']), 1)
        self.assertEqual(segunda_copia['turmas_criadas'], 0)
        self.assertEqual(segunda_copia['alunos_copiados'], 0)

    def test_servico_abre_proximo_periodo_do_mesmo_ano(self):
        resultado = abrir_proximo_periodo(
            ano_letivo=self.ano_letivo.ano,
            tipo_periodo='trimestre',
        )

        self.assertEqual(resultado, {
            'ano_destino': self.ano_letivo.ano,
            'numero_periodo': 2,
            'novo_ano': False,
            'criado': True,
        })
        self.assertTrue(PeriodoEBD.objects.filter(
            ano_letivo=self.ano_letivo,
            tipo='trimestre',
            numero=2,
        ).exists())

    def test_abrir_periodo_nao_duplica_primeiro_periodo_do_proximo_ano(self):
        for periodo in gerar_periodos_ebd(self.ano_letivo.ano, 'trimestre'):
            PeriodoEBD.objects.get_or_create(
                ano_letivo=self.ano_letivo,
                numero=periodo['numero'],
                tipo='trimestre',
                defaults={
                    'data_inicio': periodo['data_inicio'],
                    'data_fim': periodo['data_fim'],
                },
            )
        proximo_ano = AnoLetivo.objects.create(ano=self.ano_letivo.ano + 1, ativo=True)
        primeiro_proximo_ano = gerar_periodos_ebd(proximo_ano.ano, 'trimestre')[0]
        PeriodoEBD.objects.create(
            ano_letivo=proximo_ano,
            numero=primeiro_proximo_ano['numero'],
            tipo='trimestre',
            data_inicio=primeiro_proximo_ano['data_inicio'],
            data_fim=primeiro_proximo_ano['data_fim'],
        )
        request = RequestFactory().post(
            '/escola_biblica/abrir-novo-periodo/',
            {'ano_letivo': self.ano_letivo.ano, 'tipo_periodo': 'trimestre'},
        )
        request.user = self.admin

        with patch('escola_biblica.views.messages.info') as info:
            response = unwrap(
                __import__('escola_biblica.views', fromlist=['abrir_novo_periodo']).abrir_novo_periodo,
            )(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            PeriodoEBD.objects.filter(ano_letivo=proximo_ano, tipo='trimestre', numero=1).count(),
            1,
        )
        info.assert_called_once()

    def test_nova_turma_preserva_o_ano_letivo_selecionado_na_listagem(self):
        ano_futuro = AnoLetivo.objects.create(ano=self.ano_letivo.ano + 1, ativo=True)
        request = RequestFactory().get(f'/escola-biblica/turmas/nova/?ano_letivo={ano_futuro.ano}')
        request.user = self.admin

        form = SimpleNamespace(fields={})
        with patch('escola_biblica.views.TurmaForm', return_value=form) as turma_form, patch(
            'escola_biblica.views.render',
        ):
            unwrap(__import__('escola_biblica.views', fromlist=['turma_create']).turma_create)(request)

        self.assertEqual(turma_form.call_args.kwargs['initial']['ano_letivo'], ano_futuro.pk)

    def test_salvar_nova_turma_retorna_para_o_mesmo_ano_letivo(self):
        ano_futuro = AnoLetivo.objects.create(ano=self.ano_letivo.ano + 1, ativo=True)
        request = RequestFactory().post('/escola-biblica/turmas/nova/')
        request.user = self.admin
        form = SimpleNamespace(
            instance=SimpleNamespace(ano_letivo=ano_futuro),
            is_valid=lambda: True,
            save=lambda: None,
        )

        with patch('escola_biblica.views.TurmaForm', return_value=form), patch(
            'escola_biblica.views.messages.success',
        ):
            response = unwrap(__import__('escola_biblica.views', fromlist=['turma_create']).turma_create)(request)

        self.assertRedirects(
            response,
            f'/escola_biblica/turmas/?ano_letivo={ano_futuro.ano}',
            fetch_redirect_response=False,
        )

    def test_servico_cria_licoes_do_cronograma_sem_duplicar(self):
        periodo = PeriodoEBD.objects.get(ano_letivo=self.ano_letivo, numero=1)

        criadas = criar_licoes_cronograma(
            turmas=[self.turma],
            periodo=periodo,
            periodo_nome='Trimestre 1',
            nome_licao_padrao='Licao {n} - {periodo}',
            material='Revista',
            observacoes='Planejamento',
            horario=None,
            status='ativa',
        )
        repetidas = criar_licoes_cronograma(
            turmas=[self.turma],
            periodo=periodo,
            periodo_nome='Trimestre 1',
            nome_licao_padrao='Licao {n} - {periodo}',
            material='Revista',
            observacoes='Planejamento',
            horario=None,
            status='ativa',
        )

        self.assertGreater(criadas, 0)
        self.assertEqual(repetidas, 0)
        self.assertEqual(Licao.objects.filter(turma=self.turma).count(), criadas)

    def test_servico_persiste_licoes_geradas_sem_duplicar_turma_e_data(self):
        dados_licao = {
            'turma': self.turma,
            'data': timezone.localdate(),
            'tema': 'Licao gerada',
            'material': 'Revista',
            'observacoes': 'Planejamento',
            'horario': None,
            'status': 'ativa',
            'professor': None,
        }

        criadas = persistir_licoes_geradas(licoes=[dados_licao])
        repetidas = persistir_licoes_geradas(licoes=[dados_licao])

        self.assertEqual(criadas, 1)
        self.assertEqual(repetidas, 0)
        self.assertEqual(Licao.objects.filter(turma=self.turma, data=dados_licao['data']).count(), 1)

    def test_servico_gera_e_persiste_licoes_anuais_sem_duplicar(self):
        criadas = gerar_e_persistir_licoes_periodos(
            ano=self.ano_letivo.ano,
            tipo_periodo='trimestre',
            turmas=[self.turma],
            material='Revista',
            observacoes='Planejamento anual',
            status='ativa',
            dia_semana=0,
        )
        repetidas = gerar_e_persistir_licoes_periodos(
            ano=self.ano_letivo.ano,
            tipo_periodo='trimestre',
            turmas=[self.turma],
            material='Revista',
            observacoes='Planejamento anual',
            status='ativa',
            dia_semana=0,
        )

        self.assertGreater(criadas, 0)
        self.assertEqual(repetidas, 0)
        self.assertEqual(
            PeriodoEBD.objects.filter(ano_letivo=self.ano_letivo, tipo='trimestre').count(), 4,
        )
        self.assertTrue(all(
            data_aula.weekday() == 0
            for data_aula in Licao.objects.filter(turma=self.turma).values_list('data', flat=True)
        ))

    def test_servico_lista_licoes_apenas_das_turmas_autorizadas(self):
        periodo = PeriodoEBD.objects.get(ano_letivo=self.ano_letivo, numero=1)
        licao_autorizada = Licao.objects.create(
            turma=self.turma,
            data=timezone.localdate(),
            tema='Licao autorizada',
            periodo=periodo,
        )
        outra_igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja de Licoes Externas',
            tipo_igreja='congregacao',
        )
        classe_externa = Classe.objects.create(igreja=outra_igreja, nome='Classe Externa')
        turma_externa = Turma.objects.create(
            nome='Turma Externa', igreja=outra_igreja, classe=classe_externa,
            ano_letivo=self.ano_letivo,
        )
        Licao.objects.create(
            turma=turma_externa,
            data=timezone.localdate(),
            tema='Licao externa',
            periodo=periodo,
        )

        contexto = construir_listagem_licoes(
            turmas_escopo=Turma.objects.filter(id=self.turma.id),
            igrejas_escopo=Igreja.objects.filter(id=self.igreja.id),
            parametros={'turma': self.turma.nome},
            hoje=timezone.localdate(),
        )

        self.assertEqual(list(contexto['licoes']), [licao_autorizada])
        self.assertEqual(list(contexto['turma_nomes']), [self.turma.nome])

    def test_servico_filtra_e_pagina_aulas_geradas(self):
        hoje = timezone.localdate()
        licao_correspondente = Licao.objects.create(
            turma=self.turma, data=hoje, tema='Estudo de Romanos',
        )
        Licao.objects.create(
            turma=self.turma, data=hoje - timedelta(days=7), tema='Estudo de Genesis',
        )

        aulas = filtrar_e_paginar_aulas_geradas(
            aulas=Licao.objects.filter(turma=self.turma),
            data=hoje.isoformat(),
            tema='romanos',
            pagina='1',
        )

        self.assertEqual(list(aulas.object_list), [licao_correspondente])
        self.assertEqual(aulas.paginator.count, 1)

    def test_servico_monta_contexto_compartilhado_dos_relatorios(self):
        periodo = PeriodoEBD.objects.get(ano_letivo=self.ano_letivo, numero=1)
        contexto = construir_contexto_relatorio_alunos(
            turmas=Turma.objects.filter(id=self.turma.id),
            classes=Classe.objects.filter(id=self.turma.classe_id),
            alunos_escopo=Aluno.objects.filter(id=self.aluno.id),
            parametros={},
            periodo_ctx={'periodo_selecionado': periodo, 'periodos_disponiveis': [periodo]},
        )

        self.assertEqual(list(contexto['turmas']), [self.turma])
        self.assertEqual(list(contexto['classes']), [self.turma.classe])
        self.assertEqual(contexto['alunos'][0], self.aluno)
        self.assertEqual(contexto['periodo_selecionado'], periodo)

    def test_formulario_de_cronograma_respeita_turmas_do_ano_filtrado(self):
        ano_anterior, _ = AnoLetivo.objects.get_or_create(ano=self.ano_letivo.ano - 1)
        turma_anterior = Turma.objects.create(
            nome='Turma do Ano Anterior',
            igreja=self.igreja,
            classe=self.turma.classe,
            ano_letivo=ano_anterior,
        )

        form = GerarCronogramaForm(
            request=SimpleNamespace(igrejas_permitidas=Igreja.objects.filter(id=self.igreja.id)),
            turmas=Turma.objects.filter(id=self.turma.id),
        )

        self.assertEqual(list(form.fields['turma'].queryset), [self.turma])
        self.assertNotIn(turma_anterior, form.fields['turma'].queryset)
        for campo_removido in ('data_inicial', 'periodicidade', 'horario', 'professor'):
            self.assertNotIn(campo_removido, form.fields)

        form_valido = GerarCronogramaForm(
            {'turma': self.turma.id, 'status': 'ativa'},
            turmas=Turma.objects.filter(id=self.turma.id),
        )
        self.assertTrue(form_valido.is_valid())

        form_invalido = GerarCronogramaForm(
            {
                'turma': turma_anterior.id,
                'status': 'ativa',
            },
            turmas=Turma.objects.filter(id=self.turma.id),
        )
        self.assertFalse(form_invalido.is_valid())
        self.assertIn('turma', form_invalido.errors)

    def test_pre_selecao_de_igreja_respeita_queryset_do_formulario(self):
        outra_igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja fora do formulario',
            tipo_igreja='congregacao',
        )
        form = SimpleNamespace(fields={
            'igreja': SimpleNamespace(
                queryset=Igreja.objects.filter(id=self.igreja.id),
                initial=None,
            ),
        })

        aplicar_igreja_filtro_inicial(form=form, igreja_id=outra_igreja.id)
        self.assertNotEqual(form.fields['igreja'].initial, outra_igreja.id)

        aplicar_igreja_filtro_inicial(form=form, igreja_id=self.igreja.id)
        self.assertEqual(form.fields['igreja'].initial, self.igreja.id)

    def test_listagem_de_turmas_nao_expoe_opcoes_fora_do_escopo(self):
        outra_igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja Fora do Escopo',
            tipo_igreja='congregacao',
        )
        classe_externa = Classe.objects.create(igreja=outra_igreja, nome='Classe Externa')
        turma_externa = Turma.objects.create(
            nome='Turma Externa', igreja=outra_igreja, classe=classe_externa,
            ano_letivo=self.ano_letivo,
        )
        Licao.objects.create(
            turma=self.turma, data=timezone.localdate(), tema='Lição no escopo',
        )
        request = RequestFactory().get('/escola-biblica/turmas/')
        request.user = self.admin
        request.session = {}
        request.igrejas_permitidas = Igreja.objects.filter(id=self.igreja.id)
        request_externo = RequestFactory().get(
            f'/escola-biblica/turmas/?igreja_id={outra_igreja.id}',
        )
        request_externo.user = self.admin
        request_externo.session = {}
        request_externo.igrejas_permitidas = Igreja.objects.filter(id=self.igreja.id)

        with patch('escola_biblica.views.auto_sync_ebd_periodos_e_licoes'), patch(
            'escola_biblica.views.get_ebd_config_source_info',
            return_value={
                'ebd_config_source': 'ministerio',
                'ebd_config_source_label': 'Ministério',
                'ebd_config_source_hint': '',
            },
        ), patch('escola_biblica.views.get_ebd_tipo_periodo', return_value='trimestre'), patch(
            'escola_biblica.views.usuario_pode_gerenciar_ebd', return_value=True,
        ), patch('escola_biblica.views.render') as render:
            unwrap(__import__('escola_biblica.views', fromlist=['turma_list']).turma_list)(request)
            unwrap(__import__('escola_biblica.views', fromlist=['turma_list']).turma_list)(request_externo)

        contexto, contexto_externo = [chamada.args[2] for chamada in render.call_args_list]
        self.assertEqual(
            list(contexto['turmas'].object_list.values_list('id', flat=True)), [self.turma.id],
        )
        self.assertNotIn(
            turma_externa.id,
            list(contexto['turmas_disponiveis'].values_list('id', flat=True)),
        )
        self.assertNotIn(
            classe_externa.id,
            list(contexto['classes_disponiveis'].values_list('id', flat=True)),
        )
        self.assertFalse(contexto_externo['turmas'].object_list)
        self.assertFalse(contexto_externo['turmas_disponiveis'].exists())
        self.assertFalse(contexto_externo['classes_disponiveis'].exists())

    def test_listagem_de_alunos_limita_filtro_as_turmas_do_professor(self):
        outra_classe = Classe.objects.create(igreja=self.igreja, nome='Outra Classe')
        outra_turma = Turma.objects.create(
            nome='Turma de Outro Professor', igreja=self.igreja, classe=outra_classe,
            ano_letivo=self.ano_letivo,
        )
        Aluno.objects.create(nome='Aluno de Outra Turma', turma=outra_turma)
        request = RequestFactory().get('/escola-biblica/alunos/')
        request.user = self.admin
        request.session = {}
        request.igrejas_permitidas = Igreja.objects.filter(id=self.igreja.id)

        with patch(
            'escola_biblica.views.get_turmas_professor',
            return_value=Turma.objects.filter(id=self.turma.id),
        ), patch('escola_biblica.views.render') as render:
            unwrap(__import__('escola_biblica.views', fromlist=['aluno_list']).aluno_list)(request)

        contexto = render.call_args.args[2]
        self.assertEqual(
            list(contexto['alunos'].object_list.values_list('id', flat=True)), [self.aluno.id],
        )
        self.assertEqual(
            list(contexto['turmas'].values_list('id', flat=True)), [self.turma.id],
        )

    def test_formulario_de_licao_limita_turmas_do_professor(self):
        outra_classe = Classe.objects.create(igreja=self.igreja, nome='Classe de Licoes')
        outra_turma = Turma.objects.create(
            nome='Turma Nao Atribuida', igreja=self.igreja, classe=outra_classe,
            ano_letivo=self.ano_letivo,
        )
        request = SimpleNamespace(
            user=self.admin,
            igrejas_permitidas=Igreja.objects.filter(id=self.igreja.id),
        )

        with patch('escola_biblica.services_permissoes.usuario_pode_gerenciar_ebd', return_value=False), patch(
            'escola_biblica.services_permissoes.get_turmas_professor',
            return_value=Turma.objects.filter(id=self.turma.id),
        ):
            form = LicaoForm(request=request)

        self.assertEqual(list(form.fields['turma'].queryset), [self.turma])
        self.assertNotIn(outra_turma, form.fields['turma'].queryset)

    def test_formulario_de_aluno_limita_turmas_do_professor(self):
        outra_classe = Classe.objects.create(igreja=self.igreja, nome='Classe de Alunos')
        outra_turma = Turma.objects.create(
            nome='Turma de Alunos Nao Atribuida', igreja=self.igreja, classe=outra_classe,
            ano_letivo=self.ano_letivo,
        )
        request = SimpleNamespace(
            user=self.admin,
            igrejas_permitidas=Igreja.objects.filter(id=self.igreja.id),
        )

        with patch('escola_biblica.services_permissoes.usuario_pode_gerenciar_ebd', return_value=False), patch(
            'escola_biblica.services_permissoes.get_turmas_professor',
            return_value=Turma.objects.filter(id=self.turma.id),
        ):
            form = AlunoForm(request=request)

        self.assertEqual(list(form.fields['turma'].queryset), [self.turma])
        self.assertNotIn(outra_turma, form.fields['turma'].queryset)

    def test_formulario_de_avaliacao_limita_aluno_e_licao_do_professor(self):
        outra_classe = Classe.objects.create(igreja=self.igreja, nome='Classe de Avaliacoes')
        outra_turma = Turma.objects.create(
            nome='Turma de Avaliacao Nao Atribuida', igreja=self.igreja, classe=outra_classe,
            ano_letivo=self.ano_letivo,
        )
        aluno_externo = Aluno.objects.create(nome='Aluno Nao Atribuido', turma=outra_turma)
        licao_externa = Licao.objects.create(
            turma=outra_turma, data=timezone.localdate(), tema='Licao Nao Atribuida',
        )
        request = SimpleNamespace(
            user=self.admin,
            igrejas_permitidas=Igreja.objects.filter(id=self.igreja.id),
        )

        with patch('escola_biblica.services_permissoes.usuario_pode_gerenciar_ebd', return_value=False), patch(
            'escola_biblica.services_permissoes.get_turmas_professor',
            return_value=Turma.objects.filter(id=self.turma.id),
        ):
            form = AvaliacaoForm(request=request)

        self.assertIn(self.aluno, form.fields['aluno'].queryset)
        self.assertNotIn(aluno_externo, form.fields['aluno'].queryset)
        self.assertNotIn(licao_externa, form.fields['licao'].queryset)

    def test_formulario_de_oferta_limita_turmas_do_professor(self):
        outra_classe = Classe.objects.create(igreja=self.igreja, nome='Classe de Ofertas')
        outra_turma = Turma.objects.create(
            nome='Turma de Oferta Nao Atribuida', igreja=self.igreja, classe=outra_classe,
            ano_letivo=self.ano_letivo,
        )
        request = SimpleNamespace(
            user=self.admin,
            igrejas_permitidas=Igreja.objects.filter(id=self.igreja.id),
        )

        with patch('escola_biblica.services_permissoes.usuario_pode_gerenciar_ebd', return_value=False), patch(
            'escola_biblica.services_permissoes.get_turmas_professor',
            return_value=Turma.objects.filter(id=self.turma.id),
        ):
            form = OfertaClasseForm(request=request)

        self.assertEqual(list(form.fields['turma'].queryset), [self.turma])
        self.assertNotIn(outra_turma, form.fields['turma'].queryset)

    def test_formulario_de_transferencia_limita_destino_as_turmas_do_professor(self):
        outra_classe = Classe.objects.create(igreja=self.igreja, nome='Classe de Transferencias')
        outra_turma = Turma.objects.create(
            nome='Turma de Destino Nao Atribuida', igreja=self.igreja, classe=outra_classe,
            ano_letivo=self.ano_letivo,
        )
        request = SimpleNamespace(
            user=self.admin,
            igrejas_permitidas=Igreja.objects.filter(id=self.igreja.id),
        )

        with patch('escola_biblica.services_permissoes.usuario_pode_gerenciar_ebd', return_value=False), patch(
            'escola_biblica.services_permissoes.get_turmas_professor',
            return_value=Turma.objects.filter(id=self.turma.id),
        ):
            form = TransferenciaAlunoForm(request=request)

        self.assertEqual(list(form.fields['turma_destino'].queryset), [self.turma])
        self.assertNotIn(outra_turma, form.fields['turma_destino'].queryset)

    def test_servico_calcula_media_de_frequencia_por_aluno(self):
        hoje = timezone.localdate()
        outro_aluno = Aluno.objects.create(nome='Aluno Media', turma=self.turma)
        Frequencia.objects.create(aluno=self.aluno, data=hoje, presente=True)
        Frequencia.objects.create(aluno=self.aluno, data=hoje - timedelta(days=1), presente=False)
        Frequencia.objects.create(aluno=outro_aluno, data=hoje, presente=True)

        media = calcular_media_frequencia_alunos(
            aluno_ids=[self.aluno.id, outro_aluno.id],
            data_inicio=hoje - timedelta(days=1),
            data_fim=hoje,
        )

        self.assertEqual(media, 75.0)

    def test_servico_calcula_engajamento_sem_consultas_por_aluno(self):
        hoje = timezone.localdate()
        outro_aluno = Aluno.objects.create(nome='Aluno Engajado', turma=self.turma)
        Frequencia.objects.create(aluno=self.aluno, data=hoje, presente=True)
        Frequencia.objects.create(aluno=self.aluno, data=hoje - timedelta(days=1), presente=False)
        Frequencia.objects.create(aluno=outro_aluno, data=hoje, presente=True)

        percentual = calcular_percentual_engajamento_alunos(
            aluno_ids=[self.aluno.id, outro_aluno.id],
            data_inicio=hoje - timedelta(days=1),
            data_fim=hoje,
        )

        self.assertEqual(percentual, 50.0)

    def test_servico_consolida_ofertas_por_classe_e_mes(self):
        meses = [
            timezone.datetime(self.ano_letivo.ano, 1, 1).date(),
            timezone.datetime(self.ano_letivo.ano, 2, 1).date(),
        ]
        OfertaClasse.objects.create(classe=self.turma.classe, data=meses[0], valor='12.50')
        OfertaClasse.objects.create(classe=self.turma.classe, data=meses[1], valor='7.25')

        evolucao = construir_ofertas_evolucao(
            classes=[self.turma.classe],
            ofertas_escopo=OfertaClasse.objects.all(),
            meses=meses,
        )

        self.assertEqual(evolucao, {self.turma.classe.nome: [12.5, 7.25]})

    def test_servico_consolida_ranking_de_ofertas_em_uma_consulta(self):
        hoje = timezone.localdate()
        outra_classe = Classe.objects.create(igreja=self.igreja, nome='Classe Ranking')
        OfertaClasse.objects.create(classe=self.turma.classe, data=hoje, valor='12.50')
        OfertaClasse.objects.create(classe=outra_classe, data=hoje, valor='20.00')

        with CaptureQueriesContext(connection) as consultas:
            ranking = construir_ranking_ofertas(
                classes=[self.turma.classe, outra_classe],
                ofertas_escopo=OfertaClasse.objects.all(),
                ano=hoje.year,
            )

        self.assertEqual(len(consultas), 1)
        self.assertEqual(ranking[0], {'classe': 'Classe Ranking', 'total_oferta': 20.0})

    def test_servico_coleta_indicadores_de_turma_do_escopo(self):
        hoje = timezone.localdate()
        Frequencia.objects.create(aluno=self.aluno, data=hoje, presente=True)
        OfertaClasse.objects.create(turma=self.turma, classe=self.turma.classe, data=hoje, valor='8.00')

        dados = coletar_dados_kpis_turma_professor(
            turmas_escopo=Turma.objects.filter(id=self.turma.id),
            ano_letivo=self.ano_letivo,
            inicio_atual=hoje,
            fim_atual=hoje,
            inicio_anterior=hoje - timedelta(days=7),
            fim_anterior=hoje - timedelta(days=1),
        )

        self.assertEqual([turma.id for turma in dados['turmas']], [self.turma.id])
        self.assertEqual(dados['freq_atual_map'][self.turma.id]['presentes'], 1)
        self.assertEqual(dados['ofertas_atual_map'][self.turma.id], 8)

    def test_servico_coleta_movimentacao_do_periodo(self):
        hoje = timezone.localdate()
        TransferenciaAluno.objects.create(
            aluno=self.aluno,
            turma_origem=self.turma,
            turma_destino=self.turma,
        )

        movimentacao = coletar_movimentacao_alunos(
            alunos_escopo=Aluno.objects.all(),
            transferencias_escopo=TransferenciaAluno.objects.filter(turma_destino=self.turma),
            inicio_atual=hoje - timedelta(days=1),
            fim_atual=hoje,
            inicio_anterior=hoje - timedelta(days=8),
            fim_anterior=hoje - timedelta(days=2),
        )

        self.assertEqual(movimentacao['alunos_novos'], 1)
        self.assertEqual(movimentacao['alunos_novos_anterior'], 0)
        self.assertEqual(movimentacao['transferidos'], 1)

    def test_servico_coleta_dados_do_relatorio_instantaneo(self):
        hoje = timezone.localdate()
        Frequencia.objects.create(
            aluno=self.aluno,
            data=hoje,
            presente=True,
            trouxe_biblia=True,
            trouxe_oferta=True,
        )
        OfertaClasse.objects.create(turma=self.turma, classe=self.turma.classe, data=hoje, valor='9.50')

        dados = coletar_dados_relatorio_instantaneo(turmas=[self.turma], data=hoje)

        self.assertEqual(dados['frequencias_por_turma'][self.turma.id]['presentes'], 1)
        self.assertEqual(dados['frequencias_por_turma'][self.turma.id]['biblias'], 1)
        self.assertEqual(dados['ofertas_por_turma'][self.turma.id], 9.5)

    def test_servico_calcula_chamadas_semanais_do_escopo(self):
        hoje = timezone.localdate()
        Frequencia.objects.create(aluno=self.aluno, data=hoje, presente=True)

        status = calcular_status_chamadas_semanais(
            turmas=Turma.objects.filter(id=self.turma.id),
            inicio=hoje - timedelta(days=1),
            fim=hoje,
            houve_janela=True,
        )

        self.assertEqual(status, {'previstas': 1, 'realizadas': 1, 'pendentes': 0})

    def test_servico_calcula_totais_de_ofertas_em_periodos(self):
        hoje = timezone.localdate()
        OfertaClasse.objects.create(classe=self.turma.classe, data=hoje, valor='14.00')
        OfertaClasse.objects.create(classe=self.turma.classe, data=hoje - timedelta(days=7), valor='6.50')

        totais = calcular_totais_ofertas_periodos(
            ofertas_escopo=OfertaClasse.objects.all(),
            inicio_atual=hoje,
            fim_atual=hoje,
            inicio_anterior=hoje - timedelta(days=7),
            fim_anterior=hoje - timedelta(days=7),
        )

        self.assertEqual(totais, {'atual': 14.0, 'anterior': 6.5})

    def test_servico_aplica_filtros_da_listagem_de_alunos(self):
        alunos = preparar_listagem_alunos(
            alunos_escopo=Aluno.objects.all(),
            ano=self.ano_letivo.ano,
            historico=False,
            nome='Teste',
            ativo='True',
        )

        self.assertEqual(list(alunos.values_list('id', flat=True)), [self.aluno.id])

    def test_servico_limita_queryset_as_turmas_do_professor(self):
        outra_turma = Turma.objects.create(
            nome='Turma sem acesso', igreja=self.igreja, classe=self.turma.classe,
            ano_letivo=self.ano_letivo,
        )
        oferta_autorizada = OfertaClasse.objects.create(
            turma=self.turma, classe=self.turma.classe,
            data=timezone.localdate(), valor='10.00',
        )
        OfertaClasse.objects.create(
            turma=outra_turma, classe=self.turma.classe,
            data=timezone.localdate(), valor='15.00',
        )

        with patch(
            'escola_biblica.services_permissoes.usuario_pode_gerenciar_ebd',
            return_value=False,
        ), patch(
            'escola_biblica.services_permissoes.get_turmas_professor',
            return_value=Turma.objects.filter(id=self.turma.id),
        ):
            ofertas = filtrar_queryset_por_turmas_do_usuario(
                queryset=OfertaClasse.objects.all(),
                user=self.admin,
                campo_turma='turma',
            )

        self.assertEqual(list(ofertas.values_list('id', flat=True)), [oferta_autorizada.id])

    def test_contexto_da_listagem_de_alunos_preserva_filtros_e_querystrings(self):
        parametros = RequestFactory().get(
            f'/escola-biblica/alunos/?ano={self.ano_letivo.ano}&nome=Teste&'
            'vinculo=sem_vinculo&page=2',
        ).GET

        contexto = construir_contexto_listagem_alunos(
            alunos_escopo=Aluno.objects.all(),
            turmas_escopo=Turma.objects.all(),
            anos_letivos=AnoLetivo.objects.order_by('-ano'),
            parametros=parametros,
            ano_atual=timezone.localdate().year,
        )

        self.assertEqual(
            list(contexto['alunos'].values_list('id', flat=True)), [self.aluno.id],
        )
        self.assertEqual(
            list(contexto['turmas'].values_list('id', flat=True)), [self.turma.id],
        )
        self.assertNotIn('page=', contexto['querystring'])
        self.assertNotIn('vinculo=', contexto['querystring_sem_vinculo'])

    def test_servico_resolve_periodo_atual_e_recupera_filtro_invalido(self):
        hoje = timezone.localdate()
        contexto = obter_periodo_filtro(
            ano_letivo_filtro=str(self.ano_letivo.ano),
            periodo_filtro='invalido',
            tipo_periodo='trimestre',
            hoje=hoje,
        )

        self.assertEqual(contexto['ano_letivo_selecionado'], self.ano_letivo)
        self.assertEqual(contexto['periodo_selecionado'].numero, 1)

    def test_servico_rejeita_formulario_incompleto_ou_duplicado(self):
        outro_aluno = Aluno.objects.create(nome='Outro Aluno', turma=self.turma)
        alunos_ativos = self.turma.alunos.filter(ativo=True)

        formulario_incompleto = [SimpleNamespace(cleaned_data={'aluno_id': self.aluno.id})]
        formulario_duplicado = [
            SimpleNamespace(cleaned_data={'aluno_id': self.aluno.id}),
            SimpleNamespace(cleaned_data={'aluno_id': self.aluno.id}),
        ]
        formulario_correto = [
            SimpleNamespace(cleaned_data={'aluno_id': self.aluno.id}),
            SimpleNamespace(cleaned_data={'aluno_id': outro_aluno.id}),
        ]

        self.assertFalse(formulario_chamada_corresponde_a_turma(formulario_incompleto, alunos_ativos))
        self.assertFalse(formulario_chamada_corresponde_a_turma(formulario_duplicado, alunos_ativos))
        self.assertTrue(formulario_chamada_corresponde_a_turma(formulario_correto, alunos_ativos))

    def test_servico_copia_aluno_uma_vez_por_turma_destino(self):
        ano_destino = AnoLetivo.objects.create(ano=self.ano_letivo.ano + 1, ativo=True)
        turma_destino = Turma.objects.create(
            nome='Turma Destino',
            igreja=self.igreja,
            classe=self.turma.classe,
            ano_letivo=ano_destino,
        )

        self.assertTrue(copiar_aluno_para_turma(aluno=self.aluno, turma_destino=turma_destino))
        self.assertFalse(copiar_aluno_para_turma(aluno=self.aluno, turma_destino=turma_destino))
        self.assertEqual(Aluno.objects.filter(cadastro=self.aluno.cadastro, turma=turma_destino).count(), 1)


    def test_servico_reutiliza_classe_e_turma_da_mesma_igreja_no_ano_destino(self):
        ano_destino = AnoLetivo.objects.create(ano=self.ano_letivo.ano + 1, ativo=True)

        classe_destino, classe_criada = obter_ou_criar_classe_destino(
            classe_origem=self.turma.classe,
        )
        turma_destino, turma_criada = obter_ou_criar_turma_destino(
            turma_origem=self.turma,
            ano_letivo_destino=ano_destino,
        )
        turma_reutilizada, turma_criada_novamente = obter_ou_criar_turma_destino(
            turma_origem=self.turma,
            ano_letivo_destino=ano_destino,
        )

        self.assertFalse(classe_criada)
        self.assertEqual(classe_destino, self.turma.classe)
        self.assertTrue(turma_criada)
        self.assertFalse(turma_criada_novamente)
        self.assertEqual(turma_destino, turma_reutilizada)
        self.assertEqual(turma_destino.igreja, self.igreja)
        self.assertEqual(turma_destino.classe, self.turma.classe)

    def test_servico_copia_turmas_e_reutiliza_o_resultado_sem_duplicar(self):
        ano_destino = AnoLetivo.objects.create(ano=self.ano_letivo.ano + 1, ativo=True)

        primeira_copia = copiar_turmas_para_ano(
            turmas_origem=[self.turma],
            ano_letivo_destino=ano_destino,
        )
        segunda_copia = copiar_turmas_para_ano(
            turmas_origem=[self.turma],
            ano_letivo_destino=ano_destino,
        )

        self.assertEqual(primeira_copia['turmas_criadas'], 1)
        self.assertEqual(segunda_copia['turmas_criadas'], 0)
        self.assertEqual(
            primeira_copia['turmas_destino_por_origem_id'][self.turma.id],
            segunda_copia['turmas_destino_por_origem_id'][self.turma.id],
        )

    def test_servico_copia_turmas_nao_cria_nmais1_para_relacoes_de_origem(self):
        ano_destino = AnoLetivo.objects.create(ano=self.ano_letivo.ano + 1, ativo=True)
        for indice in range(8):
            classe = Classe.objects.create(igreja=self.igreja, nome=f'Classe lote {indice}')
            Turma.objects.create(
                nome=f'Turma lote {indice}',
                igreja=self.igreja,
                classe=classe,
                ano_letivo=self.ano_letivo,
            )

        with CaptureQueriesContext(connection) as consultas:
            resultado = copiar_turmas_para_ano(
                turmas_origem=Turma.objects.filter(ano_letivo=self.ano_letivo),
                ano_letivo_destino=ano_destino,
            )

        self.assertEqual(resultado['turmas_criadas'], 9)
        self.assertLessEqual(len(consultas), 40)

    def test_servico_copia_colaboradores_sem_repetir_vinculo(self):
        ano_destino = AnoLetivo.objects.create(ano=self.ano_letivo.ano + 1, ativo=True)
        tipo_pessoa = TipoPessoa.objects.create(nome='Membro para copia')
        status_pessoa = StatusPessoa.objects.create(nome='Ativo para copia')
        Membro.objects.bulk_create([
            Membro(
                nome='Professor de copia',
                igreja=self.igreja,
                tipo_pessoa=tipo_pessoa,
                status_pessoa=status_pessoa,
            ),
        ])
        colaborador = Membro.objects.get(nome='Professor de copia', igreja=self.igreja)
        self.turma.membros.add(colaborador)

        primeira_copia = copiar_turmas_para_ano(
            turmas_origem=[self.turma],
            ano_letivo_destino=ano_destino,
            incluir_membros=True,
        )
        segunda_copia = copiar_turmas_para_ano(
            turmas_origem=[self.turma],
            ano_letivo_destino=ano_destino,
            incluir_membros=True,
        )
        turma_destino = primeira_copia['turmas_destino_por_origem_id'][self.turma.id]

        self.assertEqual(primeira_copia['membros_copiados'], 1)
        self.assertEqual(segunda_copia['membros_copiados'], 0)
        self.assertTrue(turma_destino.membros.filter(pk=colaborador.pk).exists())

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
            total=Sum(Coalesce('pontos_total', construir_expr_pontos_frequencia(cfg)))
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

    def test_avaliacao_bloqueia_aluno_de_outra_turma(self):
        outra_classe = Classe.objects.create(igreja=self.igreja, nome='Outra Classe')
        outra_turma = Turma.objects.create(
            nome='Outra Turma',
            igreja=self.igreja,
            classe=outra_classe,
            ano_letivo=self.ano_letivo,
        )
        licao = Licao.objects.create(
            turma=outra_turma,
            data=timezone.localdate(),
            tema='Licao de outra turma',
        )

        with self.assertRaises(ValidationError):
            Avaliacao.objects.create(aluno=self.aluno, licao=licao)

        form = AvaliacaoForm(data={'aluno': self.aluno.id, 'licao': licao.id})
        self.assertFalse(form.is_valid())
        self.assertIn('Selecione um aluno matriculado na turma da licao.', form.non_field_errors())
