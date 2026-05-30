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

## Riscos e mitigacoes

Risco: mudar `ebd_periodo` no meio do ano pode alterar a janela esperada.  
Mitigacao: auto-sync usa configuracao atual, mas valida gravacao por periodo existente; manter politica ministerial de mudanca com comunicacao.

Risco: dados legados fora da regra.  
Mitigacao: validacoes bloqueiam novos registros inconsistentes; tratar legados em rotina de saneamento quando necessario.

## Operacao recomendada

1. Definir `ebd_periodo` e `ebd_dia_semana` no ministerio.
2. Acessar dashboard/chamada/turmas para disparar auto-sync inicial.
3. Verificar se periodos e licoes foram gerados no ano vigente.
4. Monitorar mensagens de validacao em caso de tentativa fora de periodo.

## Checklist tecnico

- [x] Auto-sync implementado no backend EBD
- [x] Utilitario por dia da semana configurado
- [x] Validacoes de dominio em Licao/Frequencia/Oferta
- [x] Constraint `turma + data` para licoes
- [x] `manage.py check` sem erros
