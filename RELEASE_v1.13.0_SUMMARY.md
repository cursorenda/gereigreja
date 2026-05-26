# v1.13.0 Release — Dashboard Financeiro (Consolidacao Completa)

## Objetivo

Consolidar e registrar oficialmente todas as melhorias recentes do dashboard financeiro (incluindo pendencias retroativas sem changelog), com foco em UX, confiabilidade analitica, acessibilidade e navegacao contextual.

---

## Entregas Principais

### 1) Consistencia de Filtros e Contexto
- Filtro de caixa aplicado em KPIs, graficos, alertas e visoes relacionadas.
- Preservacao de contexto nos links de drill-down (igreja, caixa, periodo e datas quando aplicavel).
- Chips de escopo ativo no topo (Igreja, Caixa e Periodo).

### 2) UX do Dashboard
- Estados vazios com CTA para recuperar contexto rapido:
  - Limpar filtro
  - Voltar para visao geral
- Microcopy mais acionavel para risco financeiro imediato.
- Resumo executivo fixo com:
  - Caixa em foco
  - Risco de vencidas
  - Tendencia mensal

### 3) Graficos (Percepcao de Performance e Robustez)
- Skeleton/loading nos blocos de grafico.
- Fallback visual elegante para erro de renderizacao.
- Empty state com acao para recuperar filtros.

### 4) Leitura Analitica
- Tendencias de receitas/despesas com base comparativa explicita:
  - Atual x mes anterior
  - Periodo de referencia no tooltip

### 5) Acessibilidade
- Cards clicaveis acionaveis via teclado (Enter/Espaco).
- Foco visivel melhorado.
- Controle de zoom simplificado na topbar:
  - Botao "A" com ciclo de niveis
  - Persistencia em localStorage
  - Tooltip de status por clique/hover/foco

### 6) Navegacao e Marca
- Correcao da estabilidade do toggle de menu no dashboard financeiro.
- Marca Gereigreja reposicionada na topbar.
- Logo dinamica por helper do sistema com fallback.

---

## Arquivos com Maior Impacto

- financeiro/views.py
- financeiro/templates/financeiro/painel_financeiro.html
- static/css/financeiro-painel.css
- static/js/dashboard-sidebar.js
- templates/base_com_menu.html
- static/js/layout_custom.js
- static/css/design_system.css

---

## Impacto de Negocio

- Menor risco de interpretacao incorreta de dados financeiros.
- Melhor velocidade de decisao para tesouraria e lideranca.
- Experiencia mais estavel e consistente em desktop e mobile.

---

## Compatibilidade

- Sem migracoes de banco.
- Sem breaking changes de API publica.
- Mudancas concentradas em view/template/CSS/JS.

---

## Checklist de Publicacao

- [x] CHANGELOG atualizado com v1.13.0
- [x] Sumario tecnico de release (este arquivo)
- [ ] Revisao final visual em desktop/mobile
- [ ] Validacao funcional em ambiente de homologacao
- [ ] Publicacao da tag/release no repositorio

