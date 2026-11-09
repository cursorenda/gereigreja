Pasta:

docs/ai/

Arquivo:

15-Gestao-de-Custos-Capacidade-e-FinOps-de-IA.md

Documento:

GAI-15

Código:

GAI-AI-COST-CAPACITY-FINOPS

Família:

GAI — GereIgreja Artificial Intelligence Engineering

Frameworks relacionados:

GEA — GereIgreja Enterprise Architecture
GSF — GereIgreja Security Framework
GQF — GereIgreja Quality Framework
GOC — GereIgreja Operations Center
GDF — GereIgreja Documentation Framework
GAPI — GereIgreja API Engineering
GINF — GereIgreja Infrastructure Engineering
GereIgreja Backend Engineering
GereIgreja Data Engineering

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GAI-15 — Gestão de Custos, Capacidade e FinOps de Inteligência Artificial

> "Custo de IA é uma propriedade arquitetural e operacional; não apenas uma linha na fatura do provider."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Modelo de Custos de IA
6. Unidades de Consumo
7. Tokens de Entrada
8. Tokens de Saída
9. Chamadas
10. Embeddings
11. Retrieval
12. Vector Store
13. Tool Calls
14. Agentes
15. Multimodalidade
16. Armazenamento
17. Filas e Workers
18. Custos de Rede
19. Custos Indiretos
20. Cost Attribution
21. Cost Allocation
22. Dimensões de Custo
23. Tenant
24. Feature
25. Caso de Uso
26. Provider
27. Modelo
28. Ambiente
29. Equipe
30. Request
31. Correlation ID
32. Tags
33. Budgets
34. Budget Global
35. Budget por Tenant
36. Budget por Feature
37. Budget por Agente
38. Budget por Execução
39. Hard Limits
40. Soft Limits
41. Alertas
42. Quotas
43. Rate Limits
44. Token Limits
45. Step Limits
46. Tool Limits
47. Concurrency Limits
48. Capacity Planning
49. Demanda
50. Throughput
51. Latência
52. Burst
53. Rate Limit do Provider
54. Headroom
55. Saturação
56. Backpressure
57. Filas
58. Load Shedding
59. Priorização
60. Degradação
61. Model Routing
62. Model Tiering
63. Fallback
64. Caching
65. Semantic Cache
66. Prompt Optimization
67. Context Optimization
68. RAG Optimization
69. Output Optimization
70. Batch
71. Async Processing
72. Embedding Optimization
73. Vector Optimization
74. Agent Optimization
75. Tool Optimization
76. Unit Economics
77. Cost per Request
78. Cost per Successful Outcome
79. Cost per Tenant
80. Cost per Active User
81. Cost per Feature
82. Marginal Cost
83. Forecast
84. Forecast por Crescimento
85. Forecast por Feature
86. Cenários
87. Provider Pricing Changes
88. Model Migration
89. Cost Anomaly Detection
90. Cost Spikes
91. Abuse
92. Infinite Loops
93. Retry Storms
94. Runaway Agents
95. Observabilidade Financeira
96. Métricas
97. Dashboards
98. Relatórios
99. Showback
100. Chargeback
101. FinOps Review
102. Otimização Contínua
103. Qualidade versus Custo
104. Segurança versus Custo
105. Privacidade versus Custo
106. SLO versus Custo
107. Decisões Arquiteturais
108. Desenvolvimento
109. Staging
110. Produção
111. Testes e Avaliações
112. Custos de Experimentos
113. Custos de Incidentes
114. Procurement
115. Contratos
116. Commitments
117. Multi-Provider
118. Inventário
119. Auditoria
120. Production Readiness
121. Templates
122. Anti-Padrões
123. Arquitetura Consolidada
124. Checklist
125. Documentos Relacionados
126. Princípios Finais
127. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para gestão de custos, capacidade e práticas FinOps aplicadas às capacidades de Inteligência Artificial do GereIgreja.

Seu objetivo é permitir que IA seja operada de forma economicamente sustentável, previsível e observável sem comprometer segurança, privacidade ou qualidade.

---

# 2. Escopo

Aplica-se a:

- modelos generativos;
- embeddings;
- RAG;
- vector stores;
- agentes;
- tools;
- avaliações;
- jobs;
- processamento multimodal;
- providers externos;
- infraestrutura própria relacionada à IA.

---

# 3. Relação com a Família GAI

```text
GAI-05
Evaluation / Observability / Cost
        │
        ▼
GAI-11
Use Case Risk
        │
        ▼
GAI-12 / GAI-13 / GAI-14
Assets / Config / Agents
        │
        ▼
GAI-15
Cost / Capacity / FinOps
```

GAI-15 aprofunda a disciplina econômica e de capacidade operacional.

---

# 4. Princípios Fundamentais

Aplicar:

- cost visibility;
- cost attribution;
- bounded consumption;
- quality-aware optimization;
- capacity before saturation;
- tenant-aware controls;
- anomaly detection;
- graceful degradation;
- no unlimited agents;
- economics as architecture.

---

# 5. Modelo de Custos de IA

O custo total poderá ser representado conceitualmente por:

```text
AI Total Cost
=
Model Inference
+ Embeddings
+ Retrieval
+ Storage
+ Tools
+ Compute
+ Network
+ Observability
+ Evaluation
+ Operational Overhead
```

---

# 6. Unidades de Consumo

Cada serviço deverá conhecer sua unidade relevante de consumo.

---

# 7. Tokens de Entrada

Medir quando disponibilizado pelo provider.

---

# 8. Tokens de Saída

Saídas longas podem dominar custo e latência.

---

# 9. Chamadas

Alguns providers ou serviços possuem custo por request.

---

# 10. Embeddings

Medir volume processado e reprocessamento.

---

# 11. Retrieval

Retrieval possui custos de infraestrutura e consulta.

---

# 12. Vector Store

Considerar:

- armazenamento;
- índices;
- queries;
- replicação;
- manutenção.

---

# 13. Tool Calls

Tools podem gerar custos externos adicionais.

---

# 14. Agentes

Custo de agente é multiplicativo.

```text
Agent Cost
≈
Steps
×
Model Calls
+
Tool Calls
```

Por isso agentes exigem limites.

---

# 15. Multimodalidade

Imagem, áudio e outros formatos poderão possuir unidades próprias.

---

# 16. Armazenamento

Considerar:

- arquivos;
- chunks;
- embeddings;
- traces;
- evaluation artifacts.

---

# 17. Filas e Workers

Jobs assíncronos consomem infraestrutura mesmo quando o provider é externo.

---

# 18. Custos de Rede

Avaliar egress e transferência quando material.

---

# 19. Custos Indiretos

Incluem:

- observabilidade;
- engenharia;
- suporte;
- incidentes;
- avaliação;
- compliance.

---

# 20. Cost Attribution

Toda capacidade relevante deverá permitir atribuir custo a uma dimensão funcional.

---

# 21. Cost Allocation

A alocação poderá ser direta ou estimada.

Deverá ser consistente.

---

# 22. Dimensões de Custo

Dimensões recomendadas:

```text
tenant
feature
use_case
provider
model
environment
request
```

---

# 23. Tenant

Sempre que tecnicamente viável, medir consumo por tenant.

---

# 24. Feature

Cada feature de IA deverá possuir identificador estável.

---

# 25. Caso de Uso

Relacionar ao GAI-11.

---

# 26. Provider

Permitir comparação entre providers aprovados.

---

# 27. Modelo

Medir consumo por alias e modelo concreto.

---

# 28. Ambiente

Separar:

```text
development
staging
production
evaluation
```

---

# 29. Equipe

Quando útil, atribuir custos internos por domínio responsável.

---

# 30. Request

Operações relevantes deverão possuir request ID.

---

# 31. Correlation ID

Propagar para fluxos multi-step.

---

# 32. Tags

Tags deverão ser controladas e possuir cardinalidade adequada.

---

# 33. Budgets

Budget é limite de consumo esperado ou permitido.

---

# 34. Budget Global

Definir envelope operacional global quando necessário.

---

# 35. Budget por Tenant

Útil para planos, proteção contra abuso e previsibilidade.

---

# 36. Budget por Feature

Evita que uma feature degrade economia da plataforma inteira.

---

# 37. Budget por Agente

Obrigatório para agentes multi-step relevantes.

---

# 38. Budget por Execução

Exemplo:

```text
max_tokens
max_model_calls
max_tool_calls
max_steps
max_estimated_cost
```

---

# 39. Hard Limits

Interrompem execução.

Usar quando exceder o limite representa risco material.

---

# 40. Soft Limits

Geram alerta ou degradação.

---

# 41. Alertas

Alertas deverão considerar baseline e contexto.

---

# 42. Quotas

Quotas poderão ser:

- diárias;
- mensais;
- por usuário;
- por tenant;
- por feature.

---

# 43. Rate Limits

Protegem custo e capacidade.

---

# 44. Token Limits

Definir limites de input e output.

---

# 45. Step Limits

Agentes deverão possuir máximo de passos.

---

# 46. Tool Limits

Tools caras poderão possuir quota própria.

---

# 47. Concurrency Limits

Controlar workloads simultâneos.

---

# 48. Capacity Planning

Planejar capacidade antes de crescimento significativo.

---

# 49. Demanda

Medir:

```text
requests/time
tokens/time
jobs/time
concurrent agents
```

---

# 50. Throughput

Definir capacidade necessária para SLO.

---

# 51. Latência

Capacidade insuficiente tende a elevar latência.

---

# 52. Burst

Planejar picos de uso.

---

# 53. Rate Limit do Provider

Rate limits externos são dependência operacional.

---

# 54. Headroom

Manter margem para picos e falhas.

---

# 55. Saturação

Sinais:

- filas crescentes;
- throttling;
- timeouts;
- aumento de retry;
- latência elevada.

---

# 56. Backpressure

Aplicar quando downstream não suporta a demanda.

---

# 57. Filas

Workloads não interativos deverão utilizar filas quando apropriado.

---

# 58. Load Shedding

Sob saturação, rejeitar ou adiar trabalho de menor prioridade.

---

# 59. Priorização

Exemplo:

```text
critical interactive
>
standard interactive
>
background
>
experiments
```

---

# 60. Degradação

Alternativas:

- modelo menor;
- resposta menor;
- sem enriquecimento;
- processamento assíncrono;
- feature temporariamente indisponível.

---

# 61. Model Routing

Routing poderá considerar custo, mas nunca ignorar requisitos de qualidade e segurança.

---

# 62. Model Tiering

Exemplo:

```text
FAST
STANDARD
ADVANCED
```

Cada caso de uso deverá utilizar o menor tier que satisfaça os requisitos.

---

# 63. Fallback

Fallback deverá possuir perfil econômico conhecido.

---

# 64. Caching

Cache poderá reduzir chamadas repetidas.

---

# 65. Semantic Cache

Utilizar somente quando isolamento e semântica permitirem.

Não compartilhar resultados entre tenants sem garantia explícita de segurança.

---

# 66. Prompt Optimization

Remover conteúdo redundante.

Não reduzir instruções de segurança para economizar tokens.

---

# 67. Context Optimization

Enviar somente contexto necessário.

---

# 68. RAG Optimization

Otimizar:

- chunk size;
- top-k;
- reranking;
- filtros;
- deduplicação.

---

# 69. Output Optimization

Definir saídas proporcionais à necessidade.

---

# 70. Batch

Agrupar operações quando provider e caso de uso permitirem.

---

# 71. Async Processing

Mover workloads não interativos para execução assíncrona.

---

# 72. Embedding Optimization

Evitar re-embedding sem mudança de conteúdo ou versão necessária.

---

# 73. Vector Optimization

Remover índices órfãos e dados expirados.

---

# 74. Agent Optimization

Reduzir passos desnecessários e tool calls redundantes.

---

# 75. Tool Optimization

Evitar chamar modelo quando regra determinística resolve a tarefa.

---

# 76. Unit Economics

Toda feature relevante deverá conhecer sua economia unitária.

---

# 77. Cost per Request

```text
total_feature_cost
/
requests
```

---

# 78. Cost per Successful Outcome

Mais útil para agentes e automações.

```text
total_cost
/
successful_outcomes
```

---

# 79. Cost per Tenant

Permite identificar tenants fora do perfil esperado.

---

# 80. Cost per Active User

Útil para planejamento de produto.

---

# 81. Cost per Feature

Permite comparar valor e consumo.

---

# 82. Marginal Cost

Avaliar custo incremental de novos usuários, tenants ou workloads.

---

# 83. Forecast

Forecast deverá utilizar dados observados sempre que possível.

---

# 84. Forecast por Crescimento

Modelar:

```text
users
×
requests/user
×
cost/request
```

---

# 85. Forecast por Feature

Novas features deverão estimar custo antes de rollout amplo.

---

# 86. Cenários

Manter cenários:

```text
baseline
growth
peak
provider price increase
fallback activation
```

---

# 87. Provider Pricing Changes

Mudanças relevantes deverão gerar revisão de impacto.

---

# 88. Model Migration

Avaliar:

```text
quality
cost
latency
capacity
risk
```

---

# 89. Cost Anomaly Detection

Detectar desvios inesperados.

---

# 90. Cost Spikes

Investigar rapidamente.

---

# 91. Abuse

Abuso poderá aparecer primeiro como anomalia financeira.

---

# 92. Infinite Loops

Agentes sem limites podem gerar custos descontrolados.

---

# 93. Retry Storms

Retries devem possuir backoff e limite.

---

# 94. Runaway Agents

Mecanismos obrigatórios:

```text
max_steps
timeout
budget
kill_switch
```

---

# 95. Observabilidade Financeira

FinOps deverá utilizar telemetria operacional, não apenas fatura mensal.

---

# 96. Métricas

Exemplos:

```text
ai_cost_estimated_total
ai_tokens_input_total
ai_tokens_output_total
ai_requests_total
ai_cost_per_request
ai_cost_per_tenant
ai_cost_per_feature
ai_agent_steps_total
ai_budget_exceeded_total
ai_provider_throttle_total
```

---

# 97. Dashboards

Dashboards deverão permitir análise por dimensões relevantes.

---

# 98. Relatórios

Relatórios periódicos deverão destacar:

- tendência;
- maiores consumidores;
- anomalias;
- forecast;
- oportunidades de otimização.

---

# 99. Showback

Mostrar consumo para owners e equipes.

---

# 100. Chargeback

Chargeback poderá ser adotado quando houver necessidade organizacional.

---

# 101. FinOps Review

Revisões deverão envolver engenharia, produto e operação conforme escala.

---

# 102. Otimização Contínua

Ciclo:

```text
Measure
  ↓
Attribute
  ↓
Analyze
  ↓
Optimize
  ↓
Validate Quality
  ↓
Measure Again
```

---

# 103. Qualidade versus Custo

Nunca otimizar somente custo.

Uma solução barata que falha no objetivo possui economia falsa.

---

# 104. Segurança versus Custo

Não remover controles de segurança para reduzir consumo.

---

# 105. Privacidade versus Custo

Não ampliar compartilhamento de cache ou contexto para economizar recursos sem análise de privacidade.

---

# 106. SLO versus Custo

SLOs mais rigorosos podem exigir capacidade e providers mais caros.

A decisão deverá ser explícita.

---

# 107. Decisões Arquiteturais

Mudanças materiais de custo poderão exigir ADR conforme GEA.

---

# 108. Desenvolvimento

Ambientes de desenvolvimento deverão possuir limites próprios.

---

# 109. Staging

Evitar reproduzir carga completa sem necessidade.

---

# 110. Produção

Produção recebe prioridade de capacidade.

---

# 111. Testes e Avaliações

Datasets grandes poderão consumir significativamente.

Planejar orçamento de avaliação.

---

# 112. Custos de Experimentos

Experimentos deverão possuir budget e owner.

---

# 113. Custos de Incidentes

Incidentes podem gerar consumo anormal por retries, fallback ou reprocessamento.

---

# 114. Procurement

Escala significativa poderá exigir negociação centralizada.

---

# 115. Contratos

Avaliar:

- preço;
- tiers;
- quotas;
- commitments;
- suporte;
- limites.

---

# 116. Commitments

Compromissos de consumo deverão ser baseados em demanda previsível.

---

# 117. Multi-Provider

Multi-provider não é automaticamente mais barato.

Considerar complexidade operacional e de governança.

---

# 118. Inventário

Relacionar custos aos ativos do GAI-12.

---

# 119. Auditoria

Deverá ser possível demonstrar critérios de budget e alterações relevantes.

---

# 120. Production Readiness

Antes de liberar uma feature relevante:

```text
cost model known?
budget defined?
limits defined?
capacity known?
provider quota known?
metrics available?
alerts configured?
degradation path?
owner?
forecast?
```

---

# 121. Templates

## Cost Profile

```text
Feature:
Use Case ID:
Owner:
Risk Level:

Provider:
Model Alias:

Expected Requests / Day:
Expected Input Tokens / Request:
Expected Output Tokens / Request:

Expected Cost / Request:
Expected Monthly Cost:

Tenant Attribution:
Budget:
Quota:
Rate Limit:

Peak Demand:
Concurrency:
Provider Limits:

Fallback:
Degradation:

Metrics:
Alerts:
Review Date:
```

## Agent Budget

```text
Agent ID:
Owner:

Max Steps:
Max Model Calls:
Max Tool Calls:
Max Input Tokens:
Max Output Tokens:
Max Estimated Cost:
Timeout:

Daily Quota:
Tenant Quota:

On Budget Exceeded:
Kill Switch:
```

---

# 122. Anti-Padrões

Evitar:

```text
"we will check the bill later"
```

---

```text
unlimited tokens
```

---

```text
unlimited agent steps
```

---

```text
same expensive model
for every task
```

---

```text
retry until success
```

---

```text
cache across tenants
without isolation
```

---

```text
cost optimization
by removing security checks
```

---

```text
production and experiments
sharing unlimited quota
```

---

```text
provider price
hardcoded forever
```

---

# 123. Arquitetura Consolidada

```text
                         AI REQUEST
                             │
                             ▼
                      COST / POLICY GATE
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
          QUOTAS          BUDGETS        RATE LIMITS
             │               │               │
             └───────────────┼───────────────┘
                             ▼
                        MODEL ROUTER
                             │
                 ┌───────────┼───────────┐
                 ▼           ▼           ▼
               FAST       STANDARD    ADVANCED
                 │           │           │
                 └───────────┼───────────┘
                             ▼
                         EXECUTION
                             │
                 ┌───────────┼───────────┐
                 ▼           ▼           ▼
              TOKENS       TOOLS       STORAGE
                 │           │           │
                 └───────────┼───────────┘
                             ▼
                      COST TELEMETRY
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
          TENANT          FEATURE         PROVIDER
             │               │               │
             └───────────────┼───────────────┘
                             ▼
                       FINOPS REVIEW
                             │
                             ▼
                         OPTIMIZE
```

---

# 124. Checklist

## Visibilidade

- [ ] custos medidos;
- [ ] tokens medidos;
- [ ] requests medidos;
- [ ] provider identificado;
- [ ] modelo identificado;
- [ ] feature identificada;
- [ ] tenant quando aplicável.

## Limites

- [ ] budget global;
- [ ] budget por feature;
- [ ] budget por agente;
- [ ] quotas;
- [ ] rate limits;
- [ ] token limits;
- [ ] step limits;
- [ ] concurrency limits.

## Capacidade

- [ ] demanda conhecida;
- [ ] throughput;
- [ ] peak;
- [ ] provider limits;
- [ ] headroom;
- [ ] backpressure;
- [ ] load shedding.

## Otimização

- [ ] model tiering;
- [ ] cache seguro;
- [ ] contexto minimizado;
- [ ] RAG otimizado;
- [ ] outputs limitados;
- [ ] batch/async quando aplicável;
- [ ] agentes limitados.

## Economia

- [ ] cost/request;
- [ ] cost/outcome;
- [ ] cost/tenant;
- [ ] cost/feature;
- [ ] forecast;
- [ ] anomaly detection.

## Operação

- [ ] dashboards;
- [ ] alerts;
- [ ] showback;
- [ ] review;
- [ ] degradation;
- [ ] kill switch.

## Governança

- [ ] owner;
- [ ] risk level;
- [ ] asset registry;
- [ ] configuration version;
- [ ] audit;
- [ ] periodic review.

---

# 125. Documentos Relacionados

- GAI-01 — Arquitetura e Governança de Inteligência Artificial
- GAI-02 — Providers, Modelos, Prompts e AI Gateway
- GAI-03 — RAG, Contexto e Conhecimento
- GAI-04 — Ferramentas, Agentes e Ações Seguras
- GAI-05 — Avaliação, Observabilidade, Custos e Operação de IA
- GAI-06 — Segurança, Privacidade e Guardrails de IA
- GAI-07 — Governança de Dados para Inteligência Artificial
- GAI-08 — Testes e Quality Gates para Inteligência Artificial
- GAI-09 — Deploy, Release e Lifecycle de Inteligência Artificial
- GAI-10 — Padrões de Implementação e Referência de Inteligência Artificial
- GAI-11 — Catálogo de Casos de Uso e Níveis de Risco de Inteligência Artificial
- GAI-12 — Registro, Inventário e Governança de Ativos de Inteligência Artificial
- GAI-13 — Governança de Prompts, Modelos e Configurações de Inteligência Artificial
- GAI-14 — Governança de Agentes, Autonomia e Human-in-the-Loop
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 126. Princípios Finais

IA economicamente sustentável exige limites antes do problema aparecer.

```text
No Visibility
→ No Attribution
→ No Control
→ No Predictability
```

O princípio central é:

```text
Measure consumption.

Attribute cost.

Bound execution.

Plan capacity.

Detect anomalies.

Optimize with quality.

Scale deliberately.
```

No GereIgreja, custo, qualidade, segurança e capacidade deverão ser tratados como dimensões simultâneas da arquitetura de IA.

---

# 127. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`15-Gestao-de-Custos-Capacidade-e-FinOps-de-IA.md`

**Documento**

`GAI-15`

**Código**

`GAI-AI-COST-CAPACITY-FINOPS`

**Família**

`GAI — GereIgreja Artificial Intelligence Engineering`

**Versão**

`1.0`

**Status**

`OFICIAL`

**Responsável**

`Equipe de Engenharia`

**Última atualização**

`Agosto de 2026`

**Documento anterior**

`GAI-14 — Governança de Agentes, Autonomia e Human-in-the-Loop`

**Próximo documento candidato**

`16-Gestao-de-Riscos-de-Terceiros-e-Providers-de-IA.md`
