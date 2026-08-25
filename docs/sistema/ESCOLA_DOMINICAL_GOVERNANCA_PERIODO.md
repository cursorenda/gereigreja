# Escola Dominical - Governanca de Periodo e Automacao

Data: 28/05/2026  
Escopo: app `escola_biblica`

## Objetivo

Garantir que toda operacao da EBD (licoes, chamada, ofertas, relatorios e graficos) rode dentro do periodo oficial configurado no ministerio, sem depender de clique manual para gerar calendario.

## Fonte de verdade

- Configuracao do ministerio em `ConfiguracaoSistema`:
  - `ebd_periodo` (trimestre, quadrimestre, semestre, ano)
  - `ebd_dia_semana` (0 a 6)
- Periodos fisicos em `PeriodoEBD` por `AnoLetivo`.

## O que esta automatizado (Fase 1)

### 1) Auto-sync de periodos e licoes

Servico: `auto_sync_ebd_periodos_e_licoes(request)`.

Comportamento:
- Garante periodos do ano atual e proximo ano, conforme `ebd_periodo`.
- Gera licoes do periodo vigente (ou proximo), para turmas no escopo do usuario.
- Operacao idempotente (nao duplica dados existentes).
- Execucao limitada por sessao/dia para reduzir custo.

### 2) Pontos de entrada que disparam auto-sync

- Dashboard EBD
- Chamada por turma
- Lista de turmas

Resultado esperado:
- Usuario nao precisa mais clicar em "gerar periodo" para o modulo funcionar no uso diario.

### 3) Dia da semana configuravel

Utilitario novo:
- `gerar_datas_semana_periodo(inicio, fim, dia_semana)`

Observacao:
- `gerar_domingos_periodo` foi mantido como wrapper para compatibilidade.

## Governanca de dados (Fase 2)

### 1) Licao

Regras:
- Licao so pode ser salva se a data estiver dentro de um `PeriodoEBD` valido para a turma.
- Constraint de unicidade por `turma + data`.

Migration:
- `escola_biblica/migrations/0023_licao_uq_licao_turma_data.py`

### 2) Frequencia

Regras:
- Nao permite data futura.
- Data precisa estar dentro de periodo valido da turma.
- Data precisa bater com `ebd_dia_semana` configurado no ministerio.

### 3) Oferta por turma

Regras:
- Oferta vinculada a turma precisa cair dentro de periodo valido da turma.
- Classe da oferta precisa ser a classe da turma.

## Beneficios

- Menos friccao operacional na secretaria/superintendencia EBD.
- Relatorios e graficos mais confiaveis por respeitar periodo oficial.
- Menor chance de inconsistencias de calendario.

## Integridade adicional de dados

### Copia de turmas entre anos

- A turma de destino e identificada por `nome + igreja + ano_letivo`.
- Classes e alunos copiados permanecem no escopo da mesma igreja.
- A operacao e transacional e impede duplicar o mesmo aluno na turma de destino.
- Cada copia anual gera evento de auditoria com usuario, igreja em escopo, anos envolvidos e totais processados.

### Preparacao do ano letivo

- A secretaria seleciona explicitamente as classes, turmas e alunos que continuarao no novo ano.
- Professores e colaboradores vinculados as turmas selecionadas tambem sao copiados.
- Ao concluir a copia, o sistema cria os periodos necessarios e gera as licoes do novo ano.
- O calendario de cada turma usa a configuracao da sua igreja: periodo, dia da semana e horario.
- A geracao e idempotente: uma nova execucao nao duplica turmas, matriculas ou licoes.

### Avaliacoes

- O aluno avaliado deve pertencer a mesma turma da licao.
- A matricula precisa estar vigente na data da licao, inclusive em consultas historicas.
- A regra e validada tanto no formulario quanto no modelo, protegendo interfaces e integracoes.

### Chamada de presenca

- O POST da chamada aceita somente a lista completa, sem duplicatas, dos alunos ativos da turma acessada.
- Identificadores manipulados de alunos de outra turma sao recusados sem gravar frequencia.
- A chamada continua protegida por idempotencia e bloqueio de concorrencia.

### Desempenho da chamada

- A pagina reutiliza na propria requisicao as verificacoes de grupos, ministerio e modulos permitidos.
- O fluxo possui testes de orcamento de consultas e de regressao N+1.

## Riscos e mitigacoes

Risco: mudar `ebd_periodo` no meio do ano pode alterar a janela esperada.  
Mitigacao: auto-sync usa configuracao atual, mas valida gravacao por periodo existente; manter politica ministerial de mudanca com comunicacao.

Risco: dados legados fora da regra.  
Mitigacao: validacoes bloqueiam novos registros inconsistentes; tratar legados em rotina de saneamento quando necessario.

## Operacao recomendada

1. Definir `ebd_periodo`, `ebd_dia_semana` e horario na igreja; na ausencia de override local, usar a configuracao do ministerio.
2. Acessar dashboard/chamada/turmas para disparar auto-sync inicial.
3. Verificar se periodos e licoes foram gerados no ano vigente.
4. Na virada anual, abrir "Preparar Ano Letivo", selecionar os dados que continuarao e confirmar a copia.
5. Monitorar mensagens de validacao em caso de tentativa fora de periodo.

## Checklist tecnico

- [x] Auto-sync implementado no backend EBD
- [x] Utilitario por dia da semana configurado
- [x] Validacoes de dominio em Licao/Frequencia/Oferta
- [x] Constraint `turma + data` para licoes
- [x] Copia anual isolada por igreja e sem duplicacao de alunos
- [x] Preparacao anual seletiva com geracao automatica de licoes por configuracao da igreja
- [x] Avaliacao vinculada a turma e matricula historica corretas
- [x] Chamada protegida contra aluno de outra turma no POST
- [x] Orcamento de consultas para a chamada
- [x] `manage.py check` sem erros
