# Escola Dominical - Configuracao Local por Igreja (Fase 1)

Data: 01/06/2026  
Escopo: apps `configuracao` e `escola_biblica`

## Objetivo

- Mudar a fonte de configuracao EBD para nivel de igreja, com fallback seguro para configuracao ministerial.
- Evitar regressao durante rollout: ministerio continua valido enquanto as igrejas recebem override local.

## O que foi implementado nesta fase

### 1) Modelo de dados

- `Igreja` ganhou campos opcionais de override EBD:
  - `ebd_periodo`
  - `ebd_dia_semana`
  - `ebd_horario`
- Migration: `configuracao/migrations/0027_igreja_ebd_config_local.py`
  - adiciona os campos
  - faz backfill inicial copiando valores de `ConfiguracaoSistema` por ministerio

### 2) Interface de configuracao

- `IgrejaForm` e `IgrejaEditForm` agora expoem os campos EBD locais.
- Tela de edicao da igreja (`editar_igreja_config.html`) recebeu secao dedicada:
  - "Configuracoes EBD da Igreja"
  - texto de apoio deixando claro o comportamento de override

### 3) Regras de resolucao (church-first)

- Em `escola_biblica/views.py`, a resolucao EBD passou a seguir:
  1. igreja ativa/unica no escopo
  2. se igreja tiver override preenchido, usa igreja
  3. senao, fallback para `ConfiguracaoSistema` do ministerio
- Funcoes afetadas:
  - `get_ebd_tipo_periodo`
  - `get_ebd_dia_semana`
  - wizard de cronograma (`gerar_cronograma_wizard`) para horario padrao
- Chave de cache de auto-sync agora considera igreja ativa para evitar colisao entre igrejas com configuracoes diferentes.

### 4) Agenda macro EBD

- Em `escola_biblica/services_agenda.py`, o horario do evento consolidado passa a priorizar `igreja.ebd_horario`.
- Se nao existir override local, usa horario do ministerio (comportamento legado).

### 5) Dominio de turma

- Em `escola_biblica/models.py`, `_get_config_ebd_turma` agora prioriza override local da igreja da turma/classe.
- Sem override local, permanece fallback ministerial.

### 6) Auto-sync por sinal

- `configuracao/signals.py` agora dispara auto-sync EBD tambem quando campos EBD da `Igreja` mudam.
- Mantem disparo anterior para alteracoes em `ConfiguracaoSistema`.

### 7) UX operacional

- Dashboard EBD ganhou atalho rapido para configuracao local da igreja quando houver igreja em escopo e permissao para editar.

## Compatibilidade e rollout

- Estrategia atual: **dual-source com prioridade local**.
- Nao remove a aba/configuracao ministerial nesta fase.
- Permite migracao gradual por igreja sem downtime.

## Proximos passos recomendados (Fase 2)

- Revisar pagina ministerial para retirar destaque da aba EBD (ou marcar como legado).
- Adicionar indicador visual de origem da configuracao (local x herdada) nas telas de EBD.
- Criar checklist de migracao para equipes multi-igreja.
