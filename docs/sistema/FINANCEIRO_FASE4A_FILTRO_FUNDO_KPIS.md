# Financeiro - Fase 4A (Filtro por Fundo + KPIs)

## Objetivo
Iniciar o cockpit por fundo com o menor risco possivel: filtro por fundo nos principais fluxos de leitura e indicadores resumidos por fundo no painel.

## Escopo implementado
- Painel financeiro com filtro `fundo_filtro`:
  - [financeiro/views.py](financeiro/views.py)
  - [financeiro/templates/financeiro/painel_financeiro.html](financeiro/templates/financeiro/painel_financeiro.html)
- Lista de receitas com filtro por fundo:
  - [financeiro/views.py](financeiro/views.py)
  - [financeiro/templates/financeiro/receitas/lista_receitas.html](financeiro/templates/financeiro/receitas/lista_receitas.html)
- Lista de despesas com filtro por fundo:
  - [financeiro/views.py](financeiro/views.py)
  - [financeiro/templates/financeiro/despesas/lista_despesas.html](financeiro/templates/financeiro/despesas/lista_despesas.html)

## Entregas
- Novo seletor "Fundo" nos filtros de painel, receitas e despesas.
- Validacao de escopo do fundo selecionado para evitar filtro invalido.
- KPI resumido por fundo no painel (Receitas/Despesas):
  - LOCAL
  - EVENTOS
  - MISSOES
  - ASSISTENCIA
- Chip de escopo do fundo ativo no painel.

## Compatibilidade
- Sem mudanca de schema.
- Sem novas rotas.
- Sem alteracao de regras de dominio.

## Validacao
- `manage.py check`
- `manage.py makemigrations --check --dry-run`
- Testes focados financeiros com cobertura de filtro por fundo.
