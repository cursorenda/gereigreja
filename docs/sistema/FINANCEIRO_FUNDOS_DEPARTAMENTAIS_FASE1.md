# Financeiro - Fundos Departamentais (Fase 1)

## Objetivo
Preparar o financeiro para separacao segura por departamento (Local, Eventos, Missoes, Assistencia Social) sem quebrar o fluxo atual.

## Escopo da Fase 1
- Criacao do modelo `FundoDepartamental` por igreja.
- Inclusao do campo opcional `fundo_departamental` em `Receitas` e `Despesas`.
- Backfill automatico para dados existentes:
  - lancamento com `evento` -> fundo `EVENTOS`
  - lancamento sem `evento` -> fundo `LOCAL`
- Autopreenchimento em novos salvamentos quando o fundo nao for informado.

## O que NAO muda nesta fase
- Nao altera telas, menus, fluxo operacional ou permissao atual.
- Nao altera regra de caixa por evento ja existente.
- Nao muda relatorios atuais do painel financeiro.

## Seguranca e compatibilidade
- Campo novo e opcional para evitar ruptura.
- Backfill executado na migration para evitar registros antigos sem fundo.
- Regras de validacao garantem que o fundo pertence a mesma igreja do lancamento.

## Modelo introduzido
- `FundoDepartamental`
  - `igreja`
  - `codigo` (`LOCAL`, `EVENTOS`, `MISSOES`, `ASSISTENCIA`)
  - `nome_exibicao`
  - `ativo`

## Proximas fases
- Fase 2: regras por fundo (categorias permitidas, conta padrao por fundo, restricoes por departamento).
- Fase 3: selectors/services para reduzir acoplamento de views.
- Fase 4: UX premium com cockpit por fundo.
- Fase 5: performance (indices compostos e cache de KPI).
