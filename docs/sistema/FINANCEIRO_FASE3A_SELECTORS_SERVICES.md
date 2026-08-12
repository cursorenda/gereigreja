# Financeiro - Fase 3A (Selectors/Services)

## Objetivo
Reduzir acoplamento das views de receita com evento, centralizando regras de consulta e decisao em selectors, sem alterar comportamento funcional.

## Escopo implementado
- Novo modulo [financeiro/selectors.py](financeiro/selectors.py) com funcoes:
  - `categoria_receita_por_evento(evento)`
  - `obter_conta_evento_efetiva_id(evento)`
  - `obter_evento_no_escopo(allowed_churches, evento_id)`
- Integracao dos selectors em:
  - [financeiro/views.py](financeiro/views.py) (fluxos `cadastrar_receita_evento` e `cadastrar_receita_caixa_eventos`)
  - [financeiro/forms.py](financeiro/forms.py) (default/lock de categoria e conta em contexto de evento)

## Beneficios
- Menos duplicacao de logica em views/forms.
- Regra de categoria por evento consolidada em um unico ponto.
- Melhor base para Fase 3B (padronizacao de fluxo e defaults por fundo).

## Compatibilidade
- Sem alteracao de URLs.
- Sem alteracao de schema.
- Sem alteracao de layout.
- Sem mudanca de permissao.
