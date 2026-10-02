# RELEASE v1.13.14 - RESUMO EXECUTIVO

Data: 04/06/2026
Tipo: PATCH
Escopo: Escola Dominical (EBD)

## Resumo
A versao v1.13.14 conclui o ciclo premium de operacao da EBD com foco em execucao semanal: fila priorizada de tarefas no dashboard, KPIs mensais por turma/professor, publicacao de resumo semanal e rebaixamento visual de classe para contexto secundario.

## Principais Entregas
- Centro de Acoes Operacionais no dashboard EBD com fila priorizada:
  - fechamento de chamadas da semana;
  - pendencias e registros parciais do relatorio do dia;
  - acompanhamento de evasao;
  - atalho para publicacao do resumo semanal.
- KPIs por Turma e Professor com tendencia mensal:
  - frequencia atual vs periodo anterior (delta em pontos percentuais);
  - oferta atual vs periodo anterior;
  - indicador visual de tendencia.
- Dashboard operacional premium:
  - resumo semanal com acao de publicar em Avisos;
  - checklist mobile de domingo para secretaria/lideranca.
- UX final orientada por operacao:
  - classe mantida como contexto de apoio;
  - cards e rotulos de classe rebaixados visualmente.
- Roadmap premium atualizado com itens concluidos.

## Migracoes
- Nenhuma.

## Impacto para o Usuario
- Secretaria e lideranca passam a ter uma fila objetiva de execucao para fechar a semana sem retrabalho.
- Decisoes ficam mais rapidas com leitura de tendencia por turma/professor no proprio dashboard.
- Navegacao mais clara: foco em turma e acao, com classe apenas como referencia estrutural.

## Impacto Tecnico
- Sem alteracao de schema e sem migracoes.
- Sem breaking changes de API publica.
- Mantem padrao de confiabilidade com testes focados da EBD.

## Check de Qualidade
- `manage.py test escola_biblica.tests.test_resumo_semanal_ebd escola_biblica.tests.test_pontos_ebd escola_biblica.tests.test_chamada_fluxo --settings=core.settings_test -v 1` executado com sucesso (19 testes).
- `manage.py check` sem issues no contexto de testes.
