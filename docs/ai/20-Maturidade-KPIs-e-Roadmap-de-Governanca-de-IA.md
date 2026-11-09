Pasta:

docs/ai/

Arquivo:

20-Maturidade-KPIs-e-Roadmap-de-Governanca-de-IA.md

Documento:

GAI-20

Código:

GAI-AI-MATURITY-KPI-ROADMAP

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

# GAI-20 — Maturidade, KPIs e Roadmap de Governança de Inteligência Artificial

> "Governança de IA madura não é medida pela quantidade de documentos, mas pela capacidade de demonstrar que controles funcionam, riscos são reduzidos e valor é entregue de forma sustentável."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Modelo de Maturidade
6. Nível 0 — Inexistente
7. Nível 1 — Inicial
8. Nível 2 — Gerenciado
9. Nível 3 — Padronizado
10. Nível 4 — Mensurado
11. Nível 5 — Otimizado
12. Dimensões de Maturidade
13. Estratégia e Governança
14. Arquitetura
15. Casos de Uso e Risco
16. Inventário
17. Providers e Modelos
18. Prompts e Configurações
19. Dados e RAG
20. Segurança
21. Privacidade
22. Agentes e Autonomia
23. Qualidade e Avaliação
24. Release e Lifecycle
25. Observabilidade
26. Custos e FinOps
27. Terceiros
28. Incidentes e Continuidade
29. Auditoria e Evidências
30. Descomissionamento
31. Pessoas e Capacitação
32. KPIs
33. Princípios para KPIs
34. KPIs de Governança
35. KPIs de Inventário
36. KPIs de Risco
37. KPIs de Segurança
38. KPIs de Privacidade
39. KPIs de Qualidade
40. KPIs de Agentes
41. KPIs de Operação
42. KPIs de Incidentes
43. KPIs de Custos
44. KPIs de Providers
45. KPIs de Compliance
46. KPIs de Lifecycle
47. KRIs
48. Indicadores Leading
49. Indicadores Lagging
50. Baselines
51. Targets
52. Thresholds
53. SLOs de Governança
54. Scorecards
55. Maturity Score
56. Weighted Score
57. Evidence-Based Scoring
58. Assessment
59. Self-Assessment
60. Independent Review
61. Periodicidade
62. Findings
63. Gaps
64. Prioridade
65. Roadmap
66. Horizonte 0
67. Horizonte 1
68. Horizonte 2
69. Horizonte 3
70. Quick Wins
71. Foundational Controls
72. Automation
73. Scale
74. Optimization
75. Roadmap por Risco
76. Roadmap por Valor
77. Roadmap por Dependência
78. Roadmap por Capacidade
79. Initiatives
80. Owners
81. Milestones
82. Success Criteria
83. Dependencies
84. Budget
85. Capacity
86. Risk Reduction
87. Value Realization
88. Governance Debt
89. Technical Debt
90. Exceptions Debt
91. Evidence Debt
92. Automation Coverage
93. Policy as Code
94. Compliance as Code
95. Continuous Controls
96. Dashboards
97. Executive Reporting
98. Engineering Reporting
99. Product Reporting
100. Audit Reporting
101. Review Cadence
102. Governance Forum
103. Architecture Review
104. Security Review
105. FinOps Review
106. Provider Review
107. Incident Review
108. Annual Review
109. Continuous Improvement
110. Benchmarking
111. Production Readiness
112. Templates
113. Anti-Padrões
114. Arquitetura Consolidada
115. Checklist
116. Documentos Relacionados
117. Princípios Finais
118. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para avaliação de maturidade, definição de indicadores e planejamento evolutivo da governança de Inteligência Artificial no GereIgreja.

Seu objetivo é transformar a família GAI em um sistema mensurável de governança, permitindo identificar lacunas, priorizar investimentos, acompanhar redução de risco e orientar evolução contínua.

---

# 2. Escopo

Aplica-se a:

- governança de IA;
- arquitetura;
- engenharia;
- segurança;
- privacidade;
- qualidade;
- operações;
- FinOps;
- gestão de providers;
- agentes;
- dados;
- auditoria;
- lifecycle;
- processos e controles definidos na família GAI.

---

# 3. Relação com a Família GAI

```text
GAI-01 ... GAI-19
        │
        ▼
Controls / Processes / Evidence
        │
        ▼
GAI-20
Maturity / KPIs / Roadmap
        │
        ▼
Continuous Improvement
```

GAI-20 atua como camada de medição e evolução da família GAI.

---

# 4. Princípios Fundamentais

Aplicar:

- measure what matters;
- evidence before score;
- risk-based maturity;
- outcomes over activity;
- actionable metrics;
- explicit targets;
- accountable roadmap;
- automation where valuable;
- continuous improvement;
- maturity is not bureaucracy.

---

# 5. Modelo de Maturidade

Escala oficial sugerida:

```text
0 — INEXISTENTE
1 — INICIAL
2 — GERENCIADO
3 — PADRONIZADO
4 — MENSURADO
5 — OTIMIZADO
```

---

# 6. Nível 0 — Inexistente

Características:

- ausência de processo;
- ausência de owner;
- controles inexistentes;
- dependência de ações informais.

---

# 7. Nível 1 — Inicial

Características:

- práticas pontuais;
- conhecimento concentrado;
- execução inconsistente;
- documentação parcial.

---

# 8. Nível 2 — Gerenciado

Características:

- owners definidos;
- processos básicos;
- controles principais implementados;
- registros mínimos disponíveis.

---

# 9. Nível 3 — Padronizado

Características:

- padrões organizacionais;
- templates;
- gates;
- inventário;
- processos repetíveis;
- evidências consistentes.

---

# 10. Nível 4 — Mensurado

Características:

- KPIs;
- KRIs;
- dashboards;
- thresholds;
- avaliação de efetividade;
- decisões orientadas por dados.

---

# 11. Nível 5 — Otimizado

Características:

- automação ampla;
- controles contínuos;
- prevenção;
- otimização sistemática;
- melhoria baseada em evidências.

---

# 12. Dimensões de Maturidade

A maturidade deverá ser avaliada por dimensão, evitando um único número sem contexto.

---

# 13. Estratégia e Governança

Avaliar:

- princípios;
- ownership;
- fóruns;
- políticas;
- decisões;
- accountability.

---

# 14. Arquitetura

Avaliar:

- AI Gateway;
- abstrações;
- isolamento;
- padrões;
- ADRs;
- resiliency.

---

# 15. Casos de Uso e Risco

Avaliar aderência ao GAI-11.

---

# 16. Inventário

Avaliar cobertura e atualização do GAI-12.

---

# 17. Providers e Modelos

Avaliar governança conforme GAI-02, GAI-13 e GAI-16.

---

# 18. Prompts e Configurações

Avaliar versionamento, promoção, rollback e ownership.

---

# 19. Dados e RAG

Avaliar:

- proveniência;
- isolamento;
- retenção;
- qualidade;
- lifecycle.

---

# 20. Segurança

Avaliar controles do GAI-06 e integração ao GSF.

---

# 21. Privacidade

Avaliar minimização, classificação e tratamento de dados.

---

# 22. Agentes e Autonomia

Avaliar GAI-14:

- autonomy levels;
- tool policies;
- HITL;
- budgets;
- kill switches.

---

# 23. Qualidade e Avaliação

Avaliar GAI-05 e GAI-08.

---

# 24. Release e Lifecycle

Avaliar GAI-09.

---

# 25. Observabilidade

Avaliar métricas, logs, traces, alertas e dashboards.

---

# 26. Custos e FinOps

Avaliar GAI-15.

---

# 27. Terceiros

Avaliar GAI-16.

---

# 28. Incidentes e Continuidade

Avaliar GAI-17.

---

# 29. Auditoria e Evidências

Avaliar GAI-18.

---

# 30. Descomissionamento

Avaliar GAI-19.

---

# 31. Pessoas e Capacitação

Avaliar se os papéis relevantes compreendem:

- riscos;
- padrões;
- processos;
- responsabilidades;
- procedimentos de incidente.

---

# 32. KPIs

KPIs deverão demonstrar desempenho ou resultado relevante da governança.

---

# 33. Princípios para KPIs

Um KPI deverá ser:

```text
defined
measurable
owned
actionable
time-bounded
comparable
```

---

# 34. KPIs de Governança

Exemplos:

```text
% AI use cases with owner
% AI use cases risk-classified
% high-risk use cases approved
% governance reviews completed on time
```

---

# 35. KPIs de Inventário

Exemplos:

```text
% production AI assets registered
% assets with current owner
% assets reviewed within required period
orphan assets count
```

---

# 36. KPIs de Risco

Exemplos:

```text
open high-risk findings
overdue risk treatments
expired risk acceptances
risk reduction delivered
```

---

# 37. KPIs de Segurança

Exemplos:

```text
% high-risk features security-reviewed
% mutable tools with authorization tests
% tenant-aware AI features with isolation tests
critical AI vulnerabilities open
```

---

# 38. KPIs de Privacidade

Exemplos:

```text
% use cases with data classification
% providers with retention profile
% personal-data workloads with privacy review
privacy findings overdue
```

---

# 39. KPIs de Qualidade

Exemplos:

```text
evaluation pass rate
regression escape rate
quality gate failure rate
production quality incidents
```

---

# 40. KPIs de Agentes

Exemplos:

```text
% production agents with max_steps
% agents with kill switch
% high-impact actions requiring approval
agent runaway incidents
```

---

# 41. KPIs de Operação

Exemplos:

```text
AI request success rate
AI latency SLO attainment
provider throttle rate
fallback activation rate
```

---

# 42. KPIs de Incidentes

Exemplos:

```text
MTTD
MTTR
incident recurrence rate
% post-incident actions completed on time
```

---

# 43. KPIs de Custos

Exemplos:

```text
cost per request
cost per successful outcome
budget variance
cost anomaly rate
optimization savings
```

---

# 44. KPIs de Providers

Exemplos:

```text
% critical providers reviewed
provider SLA attainment
provider incidents
days to provider/model EOL
```

---

# 45. KPIs de Compliance

Exemplos:

```text
% required controls operating
evidence freshness rate
open audit findings
overdue remediation
```

---

# 46. KPIs de Lifecycle

Exemplos:

```text
deprecated assets overdue
orphan resources
stale credentials
average retirement duration
verified decommission rate
```

---

# 47. KRIs

Key Risk Indicators sinalizam aumento de exposição.

Exemplos:

```text
unapproved provider usage
high-risk agents without HITL
cross-tenant test failures
cost spikes
expired exceptions
```

---

# 48. Indicadores Leading

Antecipam problemas.

Exemplos:

- provider EOL approaching;
- exception expiration;
- budget consumption acceleration;
- evaluation degradation.

---

# 49. Indicadores Lagging

Demonstram resultado após evento.

Exemplos:

- incidentes;
- outages;
- data exposure;
- cost overrun.

---

# 50. Baselines

Antes de definir target, medir baseline quando possível.

---

# 51. Targets

Targets deverão possuir prazo.

Exemplo:

```text
95% of production AI assets
registered with owner
by Q4
```

---

# 52. Thresholds

Definir limites que exigem ação.

---

# 53. SLOs de Governança

Exemplos:

```text
100% R3 use cases reviewed before production
95% critical evidence current
100% critical providers reviewed on schedule
```

---

# 54. Scorecards

Scorecards deverão mostrar dimensões, gaps e tendências.

---

# 55. Maturity Score

Score poderá ser utilizado como resumo, nunca como substituto da análise.

---

# 56. Weighted Score

Dimensões de maior risco poderão receber peso maior.

Exemplo:

```text
Security       20%
Privacy        15%
Risk           15%
Quality        15%
Operations     10%
Providers      10%
Audit          10%
FinOps          5%
```

Pesos deverão ser aprovados e revisáveis.

---

# 57. Evidence-Based Scoring

Nenhum nível de maturidade deverá ser atribuído apenas por declaração.

Exigir evidência compatível.

---

# 58. Assessment

Assessment deverá avaliar desenho e operação dos controles.

---

# 59. Self-Assessment

Pode ser conduzido pelos owners das dimensões.

---

# 60. Independent Review

Dimensões críticas poderão receber revisão independente.

---

# 61. Periodicidade

Sugestão:

```text
operational KPIs → continuous/monthly
maturity review  → quarterly/semiannual
full assessment  → annual
```

A periodicidade real deverá refletir risco e escala.

---

# 62. Findings

Gaps identificados deverão gerar findings rastreáveis.

---

# 63. Gaps

Classificar:

```text
critical
high
medium
low
```

---

# 64. Prioridade

Priorização recomendada:

```text
Risk
×
Impact
×
Exposure
×
Urgency
```

---

# 65. Roadmap

Roadmap deverá transformar gaps em iniciativas executáveis.

---

# 66. Horizonte 0

Correções imediatas.

Exemplos:

- bloquear provider não aprovado;
- adicionar kill switch;
- corrigir isolamento.

---

# 67. Horizonte 1

Fundação.

Exemplos:

- inventário;
- risk classification;
- owners;
- templates;
- gates.

---

# 68. Horizonte 2

Padronização e escala.

Exemplos:

- AI Gateway;
- evaluation pipeline;
- centralized observability;
- provider governance.

---

# 69. Horizonte 3

Automação e otimização.

Exemplos:

- policy as code;
- continuous compliance;
- automated evidence;
- anomaly detection;
- advanced FinOps.

---

# 70. Quick Wins

Quick wins devem reduzir risco ou esforço de forma mensurável.

---

# 71. Foundational Controls

Priorizar controles sem os quais outros não funcionam.

Exemplos:

```text
inventory
ownership
risk classification
versioning
logging
```

---

# 72. Automation

Automatizar processos repetitivos e verificáveis.

---

# 73. Scale

Processos manuais que funcionam para poucos casos podem falhar em escala.

---

# 74. Optimization

Nível avançado deverá reduzir custo operacional sem reduzir controle.

---

# 75. Roadmap por Risco

Riscos críticos têm prioridade sobre conveniência.

---

# 76. Roadmap por Valor

Dentro do mesmo risco, priorizar iniciativas de maior impacto.

---

# 77. Roadmap por Dependência

Respeitar dependências técnicas.

Exemplo:

```text
Inventory
→ Ownership
→ Policy
→ Automation
→ Continuous Control
```

---

# 78. Roadmap por Capacidade

Não planejar mais iniciativas do que a organização consegue executar.

---

# 79. Initiatives

Cada iniciativa deverá ser concreta.

---

# 80. Owners

Toda iniciativa deverá possuir owner.

---

# 81. Milestones

Definir marcos verificáveis.

---

# 82. Success Criteria

Exemplo:

```text
"AI inventory implemented"
```

não é suficiente.

Preferir:

```text
>= 98% of production AI assets
automatically registered
with owner and lifecycle status
```

---

# 83. Dependencies

Registrar dependências.

---

# 84. Budget

Relacionar recursos necessários.

---

# 85. Capacity

Considerar disponibilidade das equipes.

---

# 86. Risk Reduction

Estimar qual exposição a iniciativa reduz.

---

# 87. Value Realization

Medir benefício obtido após implementação.

---

# 88. Governance Debt

Governance debt representa controles necessários ainda não implementados.

---

# 89. Technical Debt

Dívida técnica poderá impedir maturidade.

---

# 90. Exceptions Debt

Muitas exceções abertas indicam fragilidade do padrão.

---

# 91. Evidence Debt

Controles sem evidência confiável possuem maturidade limitada.

---

# 92. Automation Coverage

Medir percentual de controles automatizados quando relevante.

---

# 93. Policy as Code

Transformar políticas objetivas em verificações automáticas.

---

# 94. Compliance as Code

Aplicar GAI-18.

---

# 95. Continuous Controls

Exemplos:

```text
deny unapproved provider
deny production agent without max_steps
alert expired exception
alert missing owner
block unversioned prompt promotion
```

---

# 96. Dashboards

Dashboards deverão mostrar tendência, não apenas estado atual.

---

# 97. Executive Reporting

Foco:

- exposição;
- tendência;
- incidentes;
- investimento;
- valor;
- principais gaps.

---

# 98. Engineering Reporting

Foco:

- gates;
- regressões;
- incidents;
- provider performance;
- technical debt;
- automation.

---

# 99. Product Reporting

Foco:

- valor;
- qualidade;
- adoção;
- custo;
- risco por feature.

---

# 100. Audit Reporting

Foco:

- controles;
- evidências;
- findings;
- exceptions;
- remediation.

---

# 101. Review Cadence

Definir calendário de revisão.

---

# 102. Governance Forum

Fórum de governança deverá tratar decisões cross-domain.

---

# 103. Architecture Review

Avaliar mudanças arquiteturais materiais.

---

# 104. Security Review

Priorizar R2/R3 conforme classificação adotada.

---

# 105. FinOps Review

Avaliar custo, forecast e otimizações.

---

# 106. Provider Review

Avaliar terceiros críticos periodicamente.

---

# 107. Incident Review

Revisar padrões de incidentes e recorrência.

---

# 108. Annual Review

A família GAI deverá ser revisada periodicamente como conjunto.

---

# 109. Continuous Improvement

Ciclo:

```text
Assess
  ↓
Measure
  ↓
Identify Gaps
  ↓
Prioritize
  ↓
Implement
  ↓
Verify
  ↓
Reassess
```

---

# 110. Benchmarking

Benchmarks externos poderão apoiar evolução, mas não substituir análise do contexto GereIgreja.

---

# 111. Production Readiness

Uma organização madura deverá conseguir responder:

```text
What AI do we run?
Who owns it?
What is the risk?
Which controls apply?
Are they operating?
How do we know?
What is failing?
What costs too much?
What should improve next?
```

---

# 112. Templates

## AI Maturity Assessment

```text
Assessment ID:
Date:
Scope:
Reviewer:

Dimension:
Current Level:
Target Level:

Controls Reviewed:
Evidence:
KPIs:
KRIs:

Strengths:
Gaps:
Findings:

Priority:
Recommended Initiatives:
Owner:
Target Date:
```

## AI Governance KPI

```text
KPI ID:
Name:
Owner:
Purpose:

Definition:
Formula:
Source:
Frequency:

Baseline:
Target:
Warning Threshold:
Critical Threshold:

Dimensions:
Trend:

Actions on Breach:
Last Review:
```

## AI Governance Roadmap Initiative

```text
Initiative ID:
Title:
Owner:

Problem:
Risk Addressed:
Expected Value:

Current Maturity:
Target Maturity:

Scope:
Dependencies:
Milestones:

Success Criteria:
KPIs:

Budget:
Capacity:

Target Start:
Target Completion:
Status:

Evidence of Completion:
```

---

# 113. Anti-Padrões

Evitar:

```text
number of policies
=
maturity
```

---

```text
maturity score
without evidence
```

---

```text
100 KPIs
that nobody acts on
```

---

```text
target
without owner
```

---

```text
roadmap
without capacity
```

---

```text
all dimensions
must reach level 5
```

---

```text
automation
before process definition
```

---

```text
green dashboard
while critical exceptions are hidden
```

---

```text
maturity assessment
performed once
and forgotten
```

---

# 114. Arquitetura Consolidada

```text
                    GAI CONTROL SYSTEM
                           │
                           ▼
                     ASSET INVENTORY
                           │
                           ▼
                    RISK CLASSIFICATION
                           │
                           ▼
                        CONTROLS
                           │
                           ▼
                        EVIDENCE
                           │
                           ▼
                    KPI / KRI LAYER
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          SECURITY       QUALITY       FINOPS
              │            │            │
              └────────────┼────────────┘
                           ▼
                    MATURITY ASSESSMENT
                           │
                           ▼
                          GAPS
                           │
                           ▼
                      PRIORITIZATION
                           │
                           ▼
                        ROADMAP
                           │
                           ▼
                     IMPLEMENTATION
                           │
                           ▼
                       VALIDATION
                           │
                           └──────────────┐
                                          │
                                          ▼
                                      REASSESS
```

---

# 115. Checklist

## Maturidade

- [ ] dimensões definidas;
- [ ] níveis definidos;
- [ ] evidências exigidas;
- [ ] baseline;
- [ ] target maturity;
- [ ] periodicidade.

## KPIs

- [ ] owner;
- [ ] definição;
- [ ] fórmula;
- [ ] fonte;
- [ ] baseline;
- [ ] target;
- [ ] thresholds;
- [ ] ação em caso de desvio.

## KRIs

- [ ] riscos materiais cobertos;
- [ ] leading indicators;
- [ ] thresholds;
- [ ] escalation.

## Roadmap

- [ ] gaps priorizados;
- [ ] iniciativas;
- [ ] owners;
- [ ] dependencies;
- [ ] milestones;
- [ ] success criteria;
- [ ] budget;
- [ ] capacity.

## Reporting

- [ ] dashboards;
- [ ] executive view;
- [ ] engineering view;
- [ ] product view;
- [ ] audit view;
- [ ] trends.

## Melhoria Contínua

- [ ] review cadence;
- [ ] governance forum;
- [ ] architecture review;
- [ ] security review;
- [ ] FinOps review;
- [ ] provider review;
- [ ] incident review;
- [ ] annual GAI review.

---

# 116. Documentos Relacionados

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
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 117. Princípios Finais

Maturidade não significa maximizar controles indiscriminadamente.

Significa aplicar os controles corretos, no risco correto, com evidência de que funcionam.

```text
Govern
→ Measure
→ Learn
→ Improve
```

O princípio central é:

```text
Know the current state.

Measure what matters.

Expose real gaps.

Prioritize by risk and value.

Assign owners.

Verify outcomes.

Improve continuously.
```

No GereIgreja, a governança de Inteligência Artificial deverá evoluir como um sistema operacional de engenharia: mensurável, verificável, adaptável e orientado à redução de risco e geração sustentável de valor.

---

# 118. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`20-Maturidade-KPIs-e-Roadmap-de-Governanca-de-IA.md`

**Documento**

`GAI-20`

**Código**

`GAI-AI-MATURITY-KPI-ROADMAP`

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

`GAI-19 — Lifecycle, Desativação e Descomissionamento de Inteligência Artificial`

**Próximo documento candidato**

`21-Responsabilidades-Papeis-e-Modelo-Operacional-de-IA.md`
