Pasta:

docs/ai/

Arquivo:

21-Responsabilidades-Papeis-e-Modelo-Operacional-de-IA.md

Documento:

GAI-21

Código:

GAI-AI-ROLES-RESPONSIBILITIES-OPERATING-MODEL

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

# GAI-21 — Responsabilidades, Papéis e Modelo Operacional de Inteligência Artificial

> "Governança sem responsabilidade explícita transforma controles em recomendações. Cada decisão relevante de IA precisa de owner, autoridade e accountability."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Modelo Operacional
6. Accountability
7. Ownership
8. Segregação de Funções
9. Papéis Fundamentais
10. AI Governance Owner
11. AI Platform Owner
12. AI Use Case Owner
13. Product Owner
14. Engineering Owner
15. Model Owner
16. Prompt Owner
17. Agent Owner
18. Tool Owner
19. Data Owner
20. Knowledge Base Owner
21. Provider Owner
22. Security Owner
23. Privacy Owner
24. Quality Owner
25. Operations Owner
26. FinOps Owner
27. Compliance Owner
28. Incident Commander
29. Human Approver
30. Auditor
31. Developer
32. Reviewer
33. RACI
34. Arquitetura
35. Caso de Uso
36. Classificação de Risco
37. Provider Approval
38. Model Approval
39. Prompt Promotion
40. Agent Approval
41. Tool Approval
42. Data Approval
43. Production Release
44. Exception Approval
45. Risk Acceptance
46. Incident Response
47. Recovery
48. Decommission
49. Fóruns de Governança
50. AI Governance Forum
51. Architecture Review
52. Security Review
53. Privacy Review
54. Quality Review
55. FinOps Review
56. Provider Review
57. Incident Review
58. Cadência
59. Quorum
60. Decision Rights
61. Escalation
62. High-Risk Decisions
63. Emergency Authority
64. Delegation
65. Conflict of Interest
66. Evidence
67. Decision Record
68. Approvals
69. Expiration
70. Exceptions
71. Operational Workflow
72. Intake
73. Triage
74. Design
75. Review
76. Build
77. Evaluate
78. Approve
79. Release
80. Operate
81. Monitor
82. Improve
83. Retire
84. Handoffs
85. On-Call
86. Support
87. Incident Escalation
88. Knowledge Transfer
89. Joiners
90. Movers
91. Leavers
92. Access Governance
93. Training
94. Competency
95. Awareness
96. Third Parties
97. Documentation
98. Metrics
99. Maturity
100. Production Readiness
101. Templates
102. Anti-Padrões
103. Arquitetura Consolidada
104. Checklist
105. Documentos Relacionados
106. Princípios Finais
107. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial de papéis, responsabilidades, direitos de decisão e modelo operacional para Inteligência Artificial no GereIgreja.

Seu objetivo é garantir que cada capacidade, risco, ativo, aprovação e decisão relevante possua responsabilidade explícita durante todo o lifecycle.

---

# 2. Escopo

Aplica-se a:

- governança de IA;
- arquitetura;
- produto;
- engenharia;
- segurança;
- privacidade;
- dados;
- qualidade;
- operações;
- FinOps;
- compliance;
- providers;
- agentes;
- tools;
- incidentes;
- lifecycle.

---

# 3. Relação com a Família GAI

```text
GAI-01 ... GAI-20
        │
        ▼
Policies / Controls / Processes
        │
        ▼
GAI-21
Roles / Accountability / Operating Model
        │
        ▼
Execution with Ownership
```

GAI-21 define quem responde pela execução dos controles estabelecidos pela família GAI.

---

# 4. Princípios Fundamentais

Aplicar:

- one accountable owner;
- explicit decision rights;
- least privilege;
- segregation of duties;
- risk-based approvals;
- evidence-based decisions;
- no orphan assets;
- no implicit authority;
- escalation paths;
- ownership through lifecycle.

---

# 5. Modelo Operacional

Modelo conceitual:

```text
GOVERN
   │
   ▼
DESIGN
   │
   ▼
BUILD
   │
   ▼
EVALUATE
   │
   ▼
APPROVE
   │
   ▼
RELEASE
   │
   ▼
OPERATE
   │
   ▼
IMPROVE / RETIRE
```

Cada etapa deverá possuir responsáveis definidos.

---

# 6. Accountability

Accountability representa responsabilidade final pelo resultado.

Pode haver múltiplos executores, mas deverá existir clareza sobre quem responde pela decisão.

---

# 7. Ownership

Todo ativo de produção deverá possuir owner ativo e identificável.

---

# 8. Segregação de Funções

Em operações de maior risco, evitar que a mesma pessoa:

```text
creates
+
approves
+
deploys
+
audits
```

sem controles compensatórios.

---

# 9. Papéis Fundamentais

Os papéis são funções de responsabilidade.

Uma pessoa poderá exercer múltiplos papéis quando o risco e a estrutura organizacional permitirem.

---

# 10. AI Governance Owner

Responsável por:

- família GAI;
- modelo de governança;
- evolução dos controles;
- fóruns;
- maturidade;
- exceções estruturais.

---

# 11. AI Platform Owner

Responsável pela plataforma compartilhada de IA.

Inclui:

- AI Gateway;
- abstrações;
- runtime;
- integração com providers;
- padrões técnicos compartilhados.

---

# 12. AI Use Case Owner

Responsável pelo caso de uso durante seu lifecycle.

Deverá garantir:

- finalidade;
- classificação;
- owner técnico;
- avaliação;
- aprovação;
- revisão;
- retirement.

---

# 13. Product Owner

Responsável por valor, comportamento esperado e impacto funcional.

---

# 14. Engineering Owner

Responsável pela implementação técnica e operação de engenharia.

---

# 15. Model Owner

Responsável por uso e lifecycle do modelo ou alias sob sua governança.

---

# 16. Prompt Owner

Responsável por:

- finalidade;
- versionamento;
- testes;
- promoção;
- rollback.

---

# 17. Agent Owner

Responsável por:

- autonomia;
- tools;
- budgets;
- HITL;
- kill switch;
- observabilidade.

---

# 18. Tool Owner

Responsável por:

- contrato;
- autorização;
- side effects;
- idempotência;
- auditoria.

---

# 19. Data Owner

Responsável pela governança do conjunto de dados sob sua autoridade.

---

# 20. Knowledge Base Owner

Responsável por:

- fontes;
- atualização;
- proveniência;
- acesso;
- lifecycle.

---

# 21. Provider Owner

Responsável pelo relacionamento técnico-operacional com provider aprovado.

---

# 22. Security Owner

Responsável por controles e avaliações de segurança aplicáveis.

---

# 23. Privacy Owner

Responsável por revisão de privacidade e requisitos relacionados a dados pessoais.

---

# 24. Quality Owner

Responsável por estratégia de testes, avaliações e quality gates.

---

# 25. Operations Owner

Responsável por:

- observabilidade;
- runbooks;
- SLOs;
- incident readiness;
- continuidade.

---

# 26. FinOps Owner

Responsável por:

- cost attribution;
- budgets;
- forecasts;
- otimização;
- anomalias financeiras.

---

# 27. Compliance Owner

Responsável pelo mapeamento e acompanhamento de requisitos de conformidade aplicáveis.

---

# 28. Incident Commander

Coordena resposta a incidente conforme GAI-17.

---

# 29. Human Approver

Pessoa autorizada a aprovar ação específica de agente ou workflow.

A aprovação deverá estar vinculada ao contexto exato da ação.

---

# 30. Auditor

Avalia controles e evidências com independência proporcional ao risco.

---

# 31. Developer

Implementa capacidades conforme padrões aprovados.

---

# 32. Reviewer

Executa revisão técnica, funcional ou de controle conforme contexto.

---

# 33. RACI

RACI poderá ser utilizado para processos relevantes:

```text
R = Responsible
A = Accountable
C = Consulted
I = Informed
```

Sempre deverá existir exatamente um accountable principal quando a decisão exigir ownership inequívoco.

---

# 34. Arquitetura

Mudanças arquiteturais materiais:

```text
A: Architecture / Platform Owner
R: Engineering
C: Security, Operations, Data
I: Product
```

A composição poderá variar conforme risco.

---

# 35. Caso de Uso

Criação e manutenção:

```text
A: AI Use Case Owner
R: Product / Engineering
C: Security, Privacy, Data
I: Governance
```

---

# 36. Classificação de Risco

```text
A: AI Use Case Owner
R: Use Case Team
C: Security / Privacy / Governance
```

R3 ou equivalente poderá exigir aprovação adicional.

---

# 37. Provider Approval

```text
A: Provider Owner / Governance
R: Engineering
C: Security / Privacy / Compliance / FinOps
```

---

# 38. Model Approval

Considerar:

- qualidade;
- risco;
- provider;
- custo;
- compatibilidade.

---

# 39. Prompt Promotion

Não permitir promoção material sem owner e evidência de avaliação.

---

# 40. Agent Approval

Agentes de maior autonomia deverão possuir aprovação proporcional ao impacto.

---

# 41. Tool Approval

Tools mutáveis exigem revisão de autorização e efeitos.

---

# 42. Data Approval

Uso de novas classes ou fontes de dados deverá envolver owner apropriado.

---

# 43. Production Release

Release deverá seguir GAI-09 e GAI-08.

---

# 44. Exception Approval

A autoridade deverá ser proporcional ao risco do controle dispensado.

---

# 45. Risk Acceptance

Quem aceita o risco deverá possuir autoridade real sobre o impacto correspondente.

---

# 46. Incident Response

Papéis deverão ser definidos previamente.

---

# 47. Recovery

A decisão de reativação deverá possuir owner e critérios objetivos.

---

# 48. Decommission

O owner permanece responsável até closure conforme GAI-19.

---

# 49. Fóruns de Governança

Fóruns existem para decisões cross-domain, não para substituir ownership.

---

# 50. AI Governance Forum

Responsabilidades:

- políticas;
- riscos sistêmicos;
- exceções relevantes;
- maturidade;
- roadmap;
- decisões cross-domain.

---

# 51. Architecture Review

Analisa mudanças estruturais relevantes.

---

# 52. Security Review

Analisa riscos e controles de segurança.

---

# 53. Privacy Review

Analisa tratamento de dados pessoais e requisitos aplicáveis.

---

# 54. Quality Review

Analisa evidências de avaliação quando necessário.

---

# 55. FinOps Review

Analisa custo, capacidade e eficiência.

---

# 56. Provider Review

Analisa terceiros críticos.

---

# 57. Incident Review

Analisa incidentes relevantes e ações de prevenção.

---

# 58. Cadência

Cadência deverá refletir volume e risco.

---

# 59. Quorum

Decisões críticas poderão exigir participantes mínimos.

---

# 60. Decision Rights

Definir explicitamente quem pode:

```text
approve
reject
disable
rollback
accept risk
grant exception
re-enable
retire
```

---

# 61. Escalation

Todo processo crítico deverá possuir caminho de escalonamento.

---

# 62. High-Risk Decisions

Decisões de alto risco não deverão depender de aprovação informal.

---

# 63. Emergency Authority

Durante incidente, autoridade emergencial poderá permitir contenção imediata.

A ação deverá ser auditada e revisada posteriormente.

---

# 64. Delegation

Delegação deverá ser explícita, limitada e revogável.

---

# 65. Conflict of Interest

Evitar autoaprovação em decisões de maior risco.

---

# 66. Evidence

Decisões materiais deverão produzir evidência conforme GAI-18.

---

# 67. Decision Record

Formato mínimo:

```text
decision
actor
authority
scope
reason
evidence
timestamp
expiration
```

---

# 68. Approvals

Aprovação deverá ser específica ao escopo avaliado.

---

# 69. Expiration

Aprovações temporárias e exceções deverão expirar.

---

# 70. Exceptions

Toda exceção deverá possuir owner, justificativa e prazo.

---

# 71. Operational Workflow

Fluxo recomendado:

```text
INTAKE
  ↓
TRIAGE
  ↓
DESIGN
  ↓
REVIEW
  ↓
BUILD
  ↓
EVALUATE
  ↓
APPROVE
  ↓
RELEASE
  ↓
OPERATE
  ↓
IMPROVE / RETIRE
```

---

# 72. Intake

Registrar nova iniciativa e owner.

---

# 73. Triage

Determinar:

- caso de uso;
- risco;
- dados;
- criticidade;
- stakeholders.

---

# 74. Design

Definir arquitetura e controles.

---

# 75. Review

Executar revisões necessárias antes da implementação ou release.

---

# 76. Build

Implementar segundo padrões.

---

# 77. Evaluate

Executar testes e avaliações.

---

# 78. Approve

Aprovar somente com evidência suficiente.

---

# 79. Release

Promover por processo controlado.

---

# 80. Operate

Monitorar qualidade, custo, segurança e disponibilidade.

---

# 81. Monitor

Acompanhar KPIs e KRIs.

---

# 82. Improve

Corrigir gaps e otimizar.

---

# 83. Retire

Aplicar GAI-19.

---

# 84. Handoffs

Transferências entre equipes deverão preservar contexto, owner e pendências.

---

# 85. On-Call

Capacidades críticas deverão possuir cobertura operacional adequada.

---

# 86. Support

Definir caminhos de suporte para falhas e dúvidas.

---

# 87. Incident Escalation

Escalonamento deverá seguir severidade e impacto.

---

# 88. Knowledge Transfer

Mudança de owner deverá incluir transferência documentada.

---

# 89. Joiners

Novos membros deverão receber acessos compatíveis com o papel.

---

# 90. Movers

Mudanças de função deverão disparar revisão de acesso e ownership.

---

# 91. Leavers

Saída de pessoas deverá remover acessos e transferir responsabilidades.

---

# 92. Access Governance

Papéis não substituem controles técnicos de autorização.

---

# 93. Training

Pessoas em funções relevantes deverão conhecer os padrões aplicáveis.

---

# 94. Competency

Papéis de aprovação deverão possuir competência adequada ao domínio avaliado.

---

# 95. Awareness

Equipes consumidoras de IA deverão conhecer limitações e canais de incidente.

---

# 96. Third Parties

Terceiros não deverão receber autoridade implícita sobre decisões internas de governança.

---

# 97. Documentation

Papéis e fluxos deverão permanecer documentados e acessíveis.

---

# 98. Metrics

Exemplos:

```text
ai_assets_without_owner
ai_use_cases_without_owner
ai_approvals_overdue
ai_exceptions_without_owner
ai_owner_transfers_pending
ai_governance_reviews_overdue
ai_training_coverage
ai_segregation_violations
```

---

# 99. Maturity

A clareza de ownership deverá compor avaliação do GAI-20.

---

# 100. Production Readiness

Antes de produção:

```text
use case owner?
engineering owner?
data owner?
provider owner?
operations owner?
risk approver?
incident owner?
decommission owner?
decision rights known?
escalation path?
```

---

# 101. Templates

## AI Responsibility Record

```text
Use Case ID:
Feature:
Risk Level:

AI Use Case Owner:
Product Owner:
Engineering Owner:

Model Owner:
Prompt Owner:
Agent Owner:
Tool Owner:

Data Owner:
Knowledge Base Owner:
Provider Owner:

Security Owner:
Privacy Owner:
Quality Owner:
Operations Owner:
FinOps Owner:
Compliance Owner:

Incident Escalation:
Emergency Authority:
Last Review:
Next Review:
```

## AI Decision Record

```text
Decision ID:
Date:
Decision:

Scope:
Use Case:
Assets:

Requested By:
Decision Owner:
Approver:

Risk Level:
Evidence:
Alternatives:

Decision:
Conditions:
Expiration:

Follow-up:
Status:
```

## RACI Record

```text
Process:
Scope:

Responsible:
Accountable:
Consulted:
Informed:

Decision Rights:
Escalation:
Evidence Required:
Review Frequency:
```

---

# 102. Anti-Padrões

Evitar:

```text
everyone owns AI
=
nobody owns AI
```

---

```text
developer
creates + approves + deploys
high-risk change
```

---

```text
committee approval
without accountable owner
```

---

```text
former employee
still listed as asset owner
```

---

```text
exception
without authority or expiration
```

---

```text
human approval
by person without context
```

---

```text
incident
with no predefined escalation
```

---

```text
decommission
after owner already left
```

---

# 103. Arquitetura Consolidada

```text
                       AI GOVERNANCE
                            │
                            ▼
                       DECISION RIGHTS
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
           PRODUCT       ENGINEERING     RISK
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                         OWNERS
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          USE CASE        ASSETS       OPERATIONS
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                       RACI / REVIEWS
                            │
                            ▼
                         EVIDENCE
                            │
                            ▼
                         RELEASE
                            │
                            ▼
                         OPERATE
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
                INCIDENT          IMPROVE
                   │                 │
                   └────────┬────────┘
                            ▼
                          RETIRE
```

---

# 104. Checklist

## Ownership

- [ ] AI Governance Owner;
- [ ] AI Platform Owner;
- [ ] Use Case Owner;
- [ ] Product Owner;
- [ ] Engineering Owner;
- [ ] asset owners;
- [ ] Operations Owner.

## Domínios

- [ ] Security;
- [ ] Privacy;
- [ ] Quality;
- [ ] Data;
- [ ] Provider;
- [ ] FinOps;
- [ ] Compliance.

## Decisões

- [ ] decision rights;
- [ ] approvers;
- [ ] risk acceptance;
- [ ] exceptions;
- [ ] emergency authority;
- [ ] escalation.

## Operação

- [ ] on-call;
- [ ] support;
- [ ] incident roles;
- [ ] recovery authority;
- [ ] knowledge transfer;
- [ ] ownership continuity.

## Governança

- [ ] RACI;
- [ ] segregation of duties;
- [ ] evidence;
- [ ] periodic reviews;
- [ ] forums;
- [ ] maturity metrics.

## Lifecycle

- [ ] ownership from intake;
- [ ] ownership at release;
- [ ] ownership during incidents;
- [ ] ownership during migration;
- [ ] ownership until decommission.

---

# 105. Documentos Relacionados

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
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 106. Princípios Finais

Processos, controles e ferramentas não substituem accountability.

```text
No Owner
→ No Accountability
→ No Reliable Governance
```

O princípio central é:

```text
Assign ownership early.

Define decision rights.

Separate critical duties.

Require evidence.

Escalate by risk.

Preserve ownership through lifecycle.

Never leave an AI asset orphaned.
```

No GereIgreja, toda capacidade relevante de Inteligência Artificial deverá possuir pessoas ou funções claramente responsáveis por sua finalidade, risco, implementação, operação e encerramento.

---

# 107. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`21-Responsabilidades-Papeis-e-Modelo-Operacional-de-IA.md`

**Documento**

`GAI-21`

**Código**

`GAI-AI-ROLES-RESPONSIBILITIES-OPERATING-MODEL`

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

`GAI-20 — Maturidade, KPIs e Roadmap de Governança de Inteligência Artificial`

**Próximo documento candidato**

`22-Politica-de-Uso-Aceitavel-e-Praticas-Proibidas-de-IA.md`
