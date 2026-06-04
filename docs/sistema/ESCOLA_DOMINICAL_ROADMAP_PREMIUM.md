# Escola Dominical - Roadmap Premium (Operacao e UX)

Data: 01/06/2026  
Escopo: app `escola_biblica`

## Diretriz de produto

- Tornar o modulo EBD orientado a operacao semanal (acao) e nao a cadastro estrutural (configuracao).
- Classe deixa de ser protagonista no dia a dia e passa para contexto de configuracao/reestruturacao.

## Benchmark de fluxo (mercado)

- Sistemas maduros no Brasil priorizam: Planejamento -> Operacao semanal -> Engajamento -> Governanca.
- Padrao premium observado: dashboard com foco em pendencias criticas, atalhos de execucao e alertas automaticos.

## Fluxo-alvo para o Gereigreja (EBD)

### 1) Planejamento do periodo

- Abrir/gerar periodo automaticamente (ja existente).
- Garantir vinculo de licoes/aulas por periodo e agenda macro (ja existente).

### 2) Operacao semanal

- Pendencias da semana: turmas sem chamada, ausencia alta, aula nao registrada.
- Botoes diretos por turma para resolver pendencia em 1 clique.

### 3) Engajamento

- Lembretes automaticos para professores (chamada/aula pendente).
- Resumo semanal para secretaria e lideranca.

### 4) Governanca

- Painel com comparacao periodo atual x anterior.
- Destaque de risco (evasao, queda de frequencia, turmas sem responsavel ativo).

## Decisao de UX (Classe)

- Remover Classe dos elementos de destaque no dashboard EBD.
- Manter Classe como:
  - filtro secundario em listagens quando necessario;
  - item principal apenas em Configuracoes EBD.
- Mensagem de produto: Turma e presenca sao operacao; Classe e estrutura.

## Plano de implementacao (sprints)

### Sprint 1 (rapido)

- [x] Reorganizar dashboard EBD em 3 blocos: Operacao da Semana, Saude das Turmas, Governanca do Periodo.
- [x] Criar card "Pendencias da Semana" com links de acao.
- [ ] Rebaixar visual de Classe no dashboard para contexto secundario.

### Sprint 2 (premium operacional)

- [x] Alertas automaticos por regra (falta de chamada, queda de frequencia, evasao).
- [x] Resumo semanal automatico para secretaria/lideranca.
- [x] Estado vazio guiado por acao nas visoes operacionais centrais da EBD.

### Sprint 3 (escala e excelencia)

- [ ] KPIs de professor/turma com tendencia mensal.
- [ ] Centro de acoes com fila de tarefas operacionais.
- [x] Checklist de usabilidade mobile para rotina de domingo.

## Metricas de sucesso

- Reduzir turmas sem chamada semanal.
- Aumentar % de presenca media por periodo.
- Reduzir tempo medio de fechamento operacional da semana.
- Reduzir evasao no periodo letivo.
