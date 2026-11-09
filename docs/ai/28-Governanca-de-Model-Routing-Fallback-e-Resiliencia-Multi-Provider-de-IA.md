Pasta:

docs/ai/

Arquivo:

28-Governanca-de-Model-Routing-Fallback-e-Resiliencia-Multi-Provider-de-IA.md

Documento:

GAI-28

Código:

GAI-AI-MODEL-ROUTING-FALLBACK-MULTI-PROVIDER-RESILIENCE

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

# GAI-28 — Governança de Model Routing, Fallback e Resiliência Multi-Provider de Inteligência Artificial

> "Resiliência em IA não é trocar de modelo a qualquer custo. É preservar segurança, qualidade, privacidade, isolamento e previsibilidade quando o caminho principal deixa de ser adequado ou disponível."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Model Routing
6. Objetivos do Routing
7. Routing Estático
8. Routing Dinâmico
9. Routing por Caso de Uso
10. Routing por Risco
11. Routing por Capacidade
12. Routing por Custo
13. Routing por Latência
14. Routing por Região
15. Routing por Disponibilidade
16. Routing por Classificação de Dados
17. Model Alias
18. Provider Alias
19. Routing Policy
20. Routing Decision
21. Determinismo
22. Explainability
23. Policy Enforcement
24. AI Gateway
25. Provider Abstraction
26. Capability Matrix
27. Model Compatibility
28. Prompt Compatibility
29. Tool Compatibility
30. Structured Output Compatibility
31. Context Window
32. Multimodality
33. Safety Compatibility
34. Data Policy Compatibility
35. Tenant Policy
36. Fallback
37. Fallback Hierarchy
38. Same-Provider Fallback
39. Cross-Provider Fallback
40. Degraded Mode
41. No-AI Fallback
42. Deterministic Fallback
43. Human Fallback
44. Failure Classification
45. Timeout
46. Rate Limit
47. Provider Outage
48. Model Unavailability
49. Invalid Output
50. Quality Failure
51. Safety Failure
52. Policy Failure
53. Cost Threshold
54. Context Overflow
55. Retry
56. Retry Budget
57. Backoff
58. Circuit Breaker
59. Bulkhead
60. Queueing
61. Load Shedding
62. Concurrency
63. Quotas
64. Failover
65. Multi-Provider
66. Provider Independence
67. Provider Concentration Risk
68. Vendor Lock-In
69. Data Residency
70. Privacy
71. Security
72. Secrets
73. Tenant Isolation
74. Authorization
75. RAG
76. Agents
77. Tools
78. Memory
79. Fine-Tuned Models
80. Provider-Specific Features
81. Quality Baselines
82. Equivalence
83. Non-Equivalent Fallback
84. Evaluation
85. Golden Datasets
86. Regression
87. Shadow Testing
88. Chaos Testing
89. Resilience Testing
90. Provider Failure Simulation
91. Disaster Recovery
92. Business Continuity
93. Observability
94. Routing Logs
95. Metrics
96. Alerts
97. SLO
98. Error Budget
99. Cost Observability
100. Quality Observability
101. Routing Drift
102. Configuration Drift
103. Change Management
104. Emergency Routing
105. Kill Switch
106. Manual Override
107. Approval
108. Audit
109. Evidence
110. Incidents
111. Post-Incident Review
112. Provider Recovery
113. Failback
114. Production Readiness
115. Templates
116. Anti-Padrões
117. Arquitetura Consolidada
118. Checklist
119. Documentos Relacionados
120. Princípios Finais
121. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para model routing, fallback e resiliência multi-provider das capacidades de Inteligência Artificial no GereIgreja.

Seu objetivo é garantir continuidade operacional sem permitir que mecanismos de failover reduzam silenciosamente controles de segurança, privacidade, qualidade, tenant isolation ou governança.

---

# 2. Escopo

Aplica-se a:

- AI Gateway;
- modelos;
- providers;
- aliases;
- roteadores;
- fallback chains;
- retries;
- circuit breakers;
- agentes;
- RAG;
- tools;
- memória;
- serviços que dependam de inferência de IA.

---

# 3. Relação com a Família GAI

```text
GAI-02
Providers / Models / AI Gateway
        │
GAI-05
Observability / Cost / Operations
        │
GAI-06
Security / Privacy
        │
GAI-09
Deploy / Lifecycle
        │
GAI-15
FinOps
        │
GAI-16
Third-Party / Provider Risk
        │
GAI-17
Continuity / Recovery
        │
GAI-23
Change Management
        │
        ▼
GAI-28
Routing / Fallback / Multi-Provider Resilience
```

---

# 4. Princípios Fundamentais

Aplicar:

- policy before routing;
- no unsafe fallback;
- explicit fallback hierarchy;
- equivalent controls across providers;
- bounded retries;
- fail closed when required;
- observable routing decisions;
- provider failure must not become data-policy failure;
- test failover before depending on it;
- recover deliberately.

---

# 5. Model Routing

Model routing seleciona o modelo ou provider apropriado para uma requisição segundo regras governadas.

---

# 6. Objetivos do Routing

Routing poderá otimizar:

```text
quality
risk
latency
availability
cost
capability
region
capacity
```

Segurança e política prevalecem sobre otimizações.

---

# 7. Routing Estático

Uma capacidade utiliza alias fixo controlado.

---

# 8. Routing Dinâmico

A seleção ocorre em runtime segundo regras previamente aprovadas.

---

# 9. Routing por Caso de Uso

Cada use case poderá possuir conjunto próprio de modelos elegíveis.

---

# 10. Routing por Risco

Casos R3 não deverão ser enviados automaticamente para modelos aprovados apenas para R1.

---

# 11. Routing por Capacidade

Selecionar somente modelos capazes de atender requisitos funcionais.

---

# 12. Routing por Custo

Custo poderá influenciar seleção após requisitos obrigatórios.

---

# 13. Routing por Latência

Latência poderá ser otimizada dentro do conjunto permitido.

---

# 14. Routing por Região

Requisitos de região e residência deverão ser respeitados.

---

# 15. Routing por Disponibilidade

Health signals poderão remover temporariamente destinos indisponíveis.

---

# 16. Routing por Classificação de Dados

A classificação dos dados deverá limitar providers e modelos elegíveis.

---

# 17. Model Alias

Produção deverá preferir aliases.

Exemplo:

```text
ai-model://assistant-general/prod
ai-model://document-extraction/prod
```

---

# 18. Provider Alias

Abstrações de provider poderão reduzir acoplamento quando tecnicamente apropriado.

---

# 19. Routing Policy

Uma policy deverá definir:

```text
use_case
risk_level
data_class
region
required_capabilities
allowed_models
allowed_providers
fallback_chain
cost_limit
latency_limit
```

---

# 20. Routing Decision

Decisões materiais deverão ser rastreáveis.

---

# 21. Determinismo

Quando necessário, regras deverão produzir decisões previsíveis sob as mesmas condições.

---

# 22. Explainability

Operação deverá conseguir explicar por que determinado destino foi escolhido sem expor detalhes sensíveis desnecessários.

---

# 23. Policy Enforcement

Routing não deverá permitir bypass de políticas de dados ou segurança.

---

# 24. AI Gateway

O AI Gateway deverá centralizar, quando aplicável:

- routing;
- aliases;
- provider policy;
- retries;
- fallback;
- observability;
- quotas;
- cost controls.

---

# 25. Provider Abstraction

Abstração não deverá esconder diferenças materiais entre providers.

---

# 26. Capability Matrix

Manter matriz de capacidades.

Exemplo:

```text
Model A:
structured_output = true
tools = true
vision = false
region = approved

Model B:
structured_output = true
tools = false
vision = true
region = approved
```

---

# 27. Model Compatibility

Fallback somente deverá ocorrer para modelo compatível com requisitos mínimos.

---

# 28. Prompt Compatibility

Prompts poderão precisar de variantes por família de modelo.

---

# 29. Tool Compatibility

Nem todos os modelos suportam tools da mesma forma.

---

# 30. Structured Output Compatibility

Validar schema e comportamento antes de permitir fallback.

---

# 31. Context Window

Fallback deverá considerar tamanho de contexto suportado.

---

# 32. Multimodality

Inputs multimodais deverão ser roteados apenas para destinos compatíveis.

---

# 33. Safety Compatibility

Fallback não deverá reduzir controles obrigatórios.

---

# 34. Data Policy Compatibility

O destino deverá ser autorizado para as classes de dados presentes.

---

# 35. Tenant Policy

Tenants poderão possuir restrições adicionais de provider, região ou capacidade.

---

# 36. Fallback

Fallback é a seleção de caminho alternativo após indisponibilidade ou inadequação do caminho preferencial.

---

# 37. Fallback Hierarchy

Exemplo:

```text
Primary Model
   ↓
Equivalent Model / Same Provider
   ↓
Equivalent Model / Approved Provider
   ↓
Degraded Capability
   ↓
Deterministic / Human Path
   ↓
Fail Safely
```

---

# 38. Same-Provider Fallback

Pode reduzir complexidade, mas não resolve outage total do provider.

---

# 39. Cross-Provider Fallback

Exige compatibilidade de dados, contrato, segurança e comportamento.

---

# 40. Degraded Mode

Modo degradado deverá possuir comportamento conhecido.

---

# 41. No-AI Fallback

Algumas funções deverão continuar por fluxo determinístico sem IA.

---

# 42. Deterministic Fallback

Regras tradicionais poderão ser preferíveis a fallback de IA inadequado.

---

# 43. Human Fallback

Processos críticos poderão escalar para revisão humana.

---

# 44. Failure Classification

Classificar falha antes de aplicar resposta quando possível.

---

# 45. Timeout

Timeout deverá possuir limite por operação.

---

# 46. Rate Limit

Rate limit poderá acionar queue, retry ou fallback conforme policy.

---

# 47. Provider Outage

Outage deverá acionar circuit breaker ou failover apropriado.

---

# 48. Model Unavailability

Modelo indisponível não autoriza automaticamente uso de qualquer alternativa.

---

# 49. Invalid Output

Output inválido poderá permitir retry limitado ou fallback compatível.

---

# 50. Quality Failure

Falha de qualidade não deverá ser confundida com falha de disponibilidade.

---

# 51. Safety Failure

Safety failure poderá exigir fail closed.

---

# 52. Policy Failure

Policy denial não deverá acionar fallback destinado a contornar a própria policy.

---

# 53. Cost Threshold

Limites de custo poderão alterar routing, desde que requisitos obrigatórios permaneçam satisfeitos.

---

# 54. Context Overflow

Poderá exigir redução segura de contexto, modelo compatível ou falha controlada.

---

# 55. Retry

Retries deverão ser limitados e idempotentes quando aplicável.

---

# 56. Retry Budget

Definir orçamento máximo de tentativas.

---

# 57. Backoff

Utilizar backoff apropriado para falhas transitórias.

---

# 58. Circuit Breaker

Impedir chamadas repetidas para destino degradado.

---

# 59. Bulkhead

Isolar falhas entre workloads.

---

# 60. Queueing

Filas poderão absorver picos quando latência permitir.

---

# 61. Load Shedding

Sob sobrecarga, reduzir trabalho não crítico de forma controlada.

---

# 62. Concurrency

Limites deverão evitar saturação de provider e infraestrutura.

---

# 63. Quotas

Quotas deverão existir por dimensão relevante.

---

# 64. Failover

Failover deverá ser testado antes de ser considerado mecanismo confiável.

---

# 65. Multi-Provider

Multi-provider deverá existir por necessidade arquitetural, não apenas por quantidade de integrações.

---

# 66. Provider Independence

Identificar componentes realmente portáveis e componentes específicos.

---

# 67. Provider Concentration Risk

Monitorar dependência excessiva de um único provider.

---

# 68. Vendor Lock-In

Avaliar custo e complexidade de migração.

---

# 69. Data Residency

Fallback não deverá transferir dados para região incompatível.

---

# 70. Privacy

Fallback deverá preservar obrigações de privacidade.

---

# 71. Security

Aplicar GAI-06 e GSF.

---

# 72. Secrets

Credenciais de cada provider deverão ser segregadas.

---

# 73. Tenant Isolation

Routing deverá preservar tenant context sem exposição cruzada.

---

# 74. Authorization

Fallback não deverá alterar permissões.

---

# 75. RAG

Retrieval e geração deverão preservar políticas mesmo quando o modelo mudar.

---

# 76. Agents

Agentes deverão conhecer apenas capacidades abstratas necessárias, quando possível.

---

# 77. Tools

Fallback de modelo não deverá ampliar conjunto de tools autorizado.

---

# 78. Memory

Contexto persistente deverá seguir GAI-27 em todos os destinos.

---

# 79. Fine-Tuned Models

Modelos customizados poderão não possuir substituto equivalente.

---

# 80. Provider-Specific Features

Features proprietárias deverão ser explicitamente identificadas.

---

# 81. Quality Baselines

Cada destino elegível deverá possuir baseline.

---

# 82. Equivalence

Equivalência deverá ser demonstrada para requisitos materiais.

---

# 83. Non-Equivalent Fallback

Quando alternativa for inferior, o sistema deverá entrar em modo degradado explícito.

---

# 84. Evaluation

Aplicar GAI-08.

---

# 85. Golden Datasets

Comparar destinos com datasets representativos.

---

# 86. Regression

Mudanças de routing deverão executar regressões apropriadas.

---

# 87. Shadow Testing

Novos destinos poderão receber shadow traffic devidamente controlado.

---

# 88. Chaos Testing

Testar falhas de provider e componentes sem causar impacto indevido.

---

# 89. Resilience Testing

Validar comportamento sob:

```text
timeouts
429
5xx
latency spikes
partial outages
invalid responses
quota exhaustion
```

---

# 90. Provider Failure Simulation

Simular indisponibilidade para validar circuit breaker e fallback.

---

# 91. Disaster Recovery

Integrar com GAI-17 e GINF.

---

# 92. Business Continuity

Definir capacidades mínimas que devem permanecer disponíveis.

---

# 93. Observability

Routing deverá produzir telemetria suficiente.

---

# 94. Routing Logs

Registrar, conforme minimização:

```text
request_id
tenant_scope
use_case
policy_version
selected_alias
provider
fallback_reason
latency
cost
result
```

---

# 95. Metrics

Exemplos:

```text
ai_routing_requests
ai_primary_route_rate
ai_fallback_rate
ai_cross_provider_fallback_rate
ai_provider_error_rate
ai_circuit_breaker_open
ai_degraded_mode_rate
ai_fail_closed_rate
```

---

# 96. Alerts

Alertar para mudanças anormais de routing ou fallback.

---

# 97. SLO

Definir SLO por capacidade quando aplicável.

---

# 98. Error Budget

Utilizar error budget para orientar decisões operacionais.

---

# 99. Cost Observability

Comparar custo por rota e fallback.

---

# 100. Quality Observability

Fallback deverá ser monitorado também por qualidade.

---

# 101. Routing Drift

Detectar mudança não planejada na distribuição de destinos.

---

# 102. Configuration Drift

Estado produtivo deverá corresponder à policy aprovada.

---

# 103. Change Management

Aplicar GAI-23 para alterações materiais.

---

# 104. Emergency Routing

Mudanças emergenciais deverão ser registradas e revisadas posteriormente.

---

# 105. Kill Switch

Permitir desativar destinos, providers ou capacidades quando necessário.

---

# 106. Manual Override

Override deverá possuir autorização, prazo e evidência.

---

# 107. Approval

Rotas de maior risco deverão possuir aprovação proporcional.

---

# 108. Audit

Decisões e configurações materiais deverão ser auditáveis.

---

# 109. Evidence

Aplicar GAI-18.

---

# 110. Incidents

Falhas materiais deverão seguir GAI-17.

---

# 111. Post-Incident Review

Avaliar se routing, fallback ou retries ampliaram o incidente.

---

# 112. Provider Recovery

Não retornar automaticamente ao primary sem critérios quando isso puder causar instabilidade.

---

# 113. Failback

Failback deverá considerar:

- health stability;
- quality;
- backlog;
- error rate;
- cost;
- observability.

---

# 114. Production Readiness

Antes de habilitar routing/fallback:

```text
owner?
routing policy?
allowed models?
allowed providers?
data policy?
tenant policy?
capability matrix?
fallback chain?
retry budget?
circuit breaker?
degraded mode?
quality baseline?
resilience tests?
observability?
kill switch?
```

---

# 115. Templates

## AI Routing Policy

```text
Routing Policy ID:
Version:
Owner:

Use Case:
Risk Level:
Environment:

Data Classes:
Allowed Regions:
Tenant Restrictions:

Required Capabilities:
Allowed Model Aliases:
Allowed Providers:

Primary Route:
Fallback 1:
Fallback 2:
Degraded Mode:
Fail-Closed Conditions:

Timeout:
Retry Budget:
Circuit Breaker:

Cost Limit:
Latency Target:

Quality Baseline:
Evaluation Evidence:

Approval:
Effective Date:
Review Date:
```

## AI Provider Capability Matrix

```text
Provider:
Model / Alias:

Regions:
Data Classes Allowed:

Text:
Vision:
Audio:
Tools:
Structured Output:
Embeddings:

Context Window:
Latency Class:
Cost Class:

Safety Controls:
Retention:
Known Limitations:

Approved Risk Levels:
Status:
Last Evaluated:
```

## AI Failover Test Record

```text
Test ID:
Owner:
Date:

Use Case:
Primary Route:
Fallback Route:

Failure Injected:
Expected Behavior:
Observed Behavior:

Tenant Isolation Preserved:
Authorization Preserved:
Data Policy Preserved:
Quality Acceptable:
Degraded Mode Correct:

Recovery:
Failback:

Result:
Findings:
Evidence:
```

---

# 116. Anti-Padrões

Evitar:

```text
provider down
→ send request anywhere
```

---

```text
fallback model
not evaluated
```

---

```text
policy denial
→ retry another provider
```

---

```text
unbounded retries
during outage
```

---

```text
multi-provider
with one shared unrestricted credential
```

---

```text
fallback
changes tenant region silently
```

---

```text
cheapest model
selected before security policy
```

---

```text
degraded model
presented as equivalent
```

---

```text
failover exists
but was never tested
```

---

# 117. Arquitetura Consolidada

```text
                         AI REQUEST
                              │
                              ▼
                         POLICY GATE
                              │
                              ▼
                       ROUTING ENGINE
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
          PRIMARY         SECONDARY        DEGRADED
             │                │                │
             ▼                ▼                ▼
         PROVIDER A       PROVIDER B      SAFE FALLBACK
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                       OUTPUT VALIDATION
                              │
                              ▼
                         OBSERVABILITY
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
            QUALITY          COST          HEALTH
                              │
                              ▼
                     CIRCUIT / FAILBACK
```

---

# 118. Checklist

## Routing

- [ ] owner;
- [ ] use case;
- [ ] risk level;
- [ ] policy version;
- [ ] required capabilities;
- [ ] model allowlist;
- [ ] provider allowlist.

## Dados e Segurança

- [ ] data classification;
- [ ] region;
- [ ] privacy;
- [ ] tenant isolation;
- [ ] authorization;
- [ ] secrets segregation;
- [ ] provider policy.

## Fallback

- [ ] explicit hierarchy;
- [ ] compatibility;
- [ ] quality baseline;
- [ ] degraded mode;
- [ ] no-AI/human fallback;
- [ ] fail-closed conditions.

## Resiliência

- [ ] timeout;
- [ ] retry budget;
- [ ] backoff;
- [ ] circuit breaker;
- [ ] concurrency;
- [ ] quotas;
- [ ] load shedding.

## Testes

- [ ] golden dataset;
- [ ] regression;
- [ ] shadow;
- [ ] provider failure simulation;
- [ ] resilience testing;
- [ ] recovery;
- [ ] failback.

## Operação

- [ ] routing logs;
- [ ] metrics;
- [ ] alerts;
- [ ] SLO;
- [ ] cost monitoring;
- [ ] quality monitoring;
- [ ] drift detection;
- [ ] kill switch.

---

# 119. Documentos Relacionados

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
- GAI-15 — Gestão de Custos, Capacidade e FinOps de Inteligência Artificial
- GAI-16 — Gestão de Riscos de Terceiros e Providers de Inteligência Artificial
- GAI-17 — Gestão de Incidentes, Continuidade e Recuperação de Inteligência Artificial
- GAI-18 — Auditoria, Evidências e Conformidade de Inteligência Artificial
- GAI-19 — Lifecycle, Desativação e Descomissionamento de Inteligência Artificial
- GAI-20 — Maturidade, KPIs e Roadmap de Governança de Inteligência Artificial
- GAI-21 — Responsabilidades, Papéis e Modelo Operacional de Inteligência Artificial
- GAI-22 — Política de Uso Aceitável e Práticas Proibidas de Inteligência Artificial
- GAI-23 — Gestão de Mudanças e Exceções de Inteligência Artificial
- GAI-24 — Transparência, Explicabilidade e Comunicação de Inteligência Artificial
- GAI-25 — Governança de Datasets Sintéticos, Fine-Tuning e Customização de Modelos
- GAI-26 — Red Teaming, Adversarial Testing e Segurança Ofensiva de Inteligência Artificial
- GAI-27 — Governança de Memória, Contexto Persistente e Personalização de Inteligência Artificial
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 120. Princípios Finais

Multi-provider não é sinônimo de resiliência.

Resiliência existe quando os caminhos alternativos são seguros, compatíveis, avaliados e operacionalmente testados.

```text
Fallback
must preserve
Policy + Security + Privacy + Quality
```

O princípio central é:

```text
Route by policy first.

Optimize second.

Fallback only to approved destinations.

Bound retries.

Fail safely.

Observe every route.

Test provider failure.

Recover deliberately.
```

No GereIgreja, indisponibilidade de um modelo ou provider nunca deverá justificar perda silenciosa de controles essenciais.

---

# 121. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`28-Governanca-de-Model-Routing-Fallback-e-Resiliencia-Multi-Provider-de-IA.md`

**Documento**

`GAI-28`

**Código**

`GAI-AI-MODEL-ROUTING-FALLBACK-MULTI-PROVIDER-RESILIENCE`

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

`GAI-27 — Governança de Memória, Contexto Persistente e Personalização de Inteligência Artificial`

**Próximo documento candidato**

`29-Governanca-de-AI-Gateway-Policy-Enforcement-e-Controle-Centralizado-de-IA.md`
