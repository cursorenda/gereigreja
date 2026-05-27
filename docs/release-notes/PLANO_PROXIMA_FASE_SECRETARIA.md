# Plano da Proxima Fase — Dashboard da Secretaria

Data: 27/05/2026

## Objetivo

Definir a proxima fase de evolucao do dashboard da Secretaria com foco em produtividade operacional, consistencia de escopo e melhoria da tomada de decisao.

---

## Resumo Executivo

A recomendacao e iniciar uma **Fase 4** em tres blocos curtos, priorizando primeiro o que melhora decisao diaria sem alto risco de regressao:

1. **Filtro de periodo + consistencia de escopo (prioridade maxima)**
2. **Exportacao de dados dos graficos/KPIs (prioridade alta)**
3. **Insights automaticos no topo do painel (prioridade media-alta)**

---

## Priorizacao (Impacto x Esforco)

## 1) Filtro de Periodo + Escopo Unificado

Prioridade: P1 (imediata)

### Problema
- O dashboard exibe series de 12 meses e KPIs fixos sem um controle de periodo explicito para o usuario.
- O backlog geral ja aponta necessidade de periodos personalizados e consistencia de escopo entre paineis.

### Entrega sugerida
- Adicionar seletor de periodo no dashboard da Secretaria (ex.: 30d, 90d, 6m, 12m, personalizado).
- Aplicar o mesmo periodo a KPIs, cards de prioridade e graficos.
- Preservar contexto em querystring para links de drill-down.

### Arquivos-alvo
- `secretaria/templates/secretaria/dashboard.html`
- `secretaria/views/dashboard.py`
- `static/js/secretaria_dashboard_premium.js`

### Resultado esperado
- Menos ambiguidade de leitura.
- Comparacoes mais justas em reunioes e planejamento.

---

## 2) Exportacao CSV/Excel de KPIs e Graficos

Prioridade: P2

### Problema
- A leitura existe, mas nao ha saida operacional rapida para reunioes e prestacao de contas.

### Entrega sugerida
- Botao de exportacao na secao "Inteligencia de Pessoas".
- Gerar CSV para:
  - Evolucao de pessoas por tipo
  - Distribuicao por tipo
  - Pessoas por status/genero/faixa etaria
- Opcional: endpoint unico com parametro `dataset=` para reaproveitar infraestrutura.

### Arquivos-alvo
- `secretaria/urls.py`
- `secretaria/views/dashboard.py` (ou modulo dedicado de export)
- `secretaria/templates/secretaria/dashboard.html`

### Resultado esperado
- Dashboard vira fonte imediata de material para reunioes.

---

## 3) Insights Automaticos no Topo (Resumo Acionavel)

Prioridade: P3

### Problema
- O usuario ve numeros, mas ainda precisa interpretar manualmente tendencia e risco.

### Entrega sugerida
- Inserir bloco "Leituras da Semana" com ate 3 insights simples:
  - Tendencia de crescimento/queda de membros ativos no periodo
  - Alerta de pendencias cadastrais acima de limiar
  - Destaque de concentracao de visitantes/novos convertidos
- Regras deterministicas (sem IA generativa), com mensagens curtas e CTAs.

### Arquivos-alvo
- `secretaria/views/dashboard.py`
- `secretaria/templates/secretaria/dashboard.html`
- `static/css/secretaria-dashboard.css`

### Resultado esperado
- Menor tempo para sair de "visualizar" para "agir".

---

## Itens que ficam para depois

- Dashboard totalmente personalizavel por usuario.
- Cache agressivo por perfil para paineis e relatorios.
- Centralizacao completa de notificacoes multi-modulo.

Motivo: maior complexidade arquitetural e dependencia de decisoes globais do sistema.

---

## Proposta de Sequencia de Implementacao

1. Sprint curta A (P1): filtro de periodo + propagacao de escopo
2. Sprint curta B (P2): exportacao CSV dos datasets principais
3. Sprint curta C (P3): insights automaticos acionaveis

---

## Criterios de Aceite da Fase 4

1. Usuario consegue alterar periodo e ver impacto consistente em KPIs e graficos.
2. Exportacoes refletem exatamente os dados exibidos na tela.
3. Bloco de insights exibe mensagens coerentes e nunca quebra quando nao houver dados.
4. Permissoes atuais (especialmente financeiro para Secretario Local) permanecem intactas.
