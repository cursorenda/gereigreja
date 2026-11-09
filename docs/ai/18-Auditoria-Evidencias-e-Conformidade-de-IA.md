Pasta:

docs/ai/

Arquivo:

18-Auditoria-Evidencias-e-Conformidade-de-IA.md

Documento:

GAI-18

Código:

GAI-AI-AUDIT-EVIDENCE-COMPLIANCE

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

# GAI-18 — Auditoria, Evidências e Conformidade de Inteligência Artificial

> "Governança só é demonstrável quando decisões, controles, versões e evidências podem ser reconstruídos de forma objetiva."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Auditabilidade de IA
6. Evidência
7. Evidência Técnica
8. Evidência Operacional
9. Evidência de Segurança
10. Evidência de Privacidade
11. Evidência de Qualidade
12. Evidência de Governança
13. Evidência de Terceiros
14. Evidence Registry
15. Evidence ID
16. Owner
17. Proveniência
18. Integridade
19. Timestamp
20. Retenção
21. Classificação
22. Controle de Acesso
23. Imutabilidade
24. Cadeia de Custódia
25. Audit Trail
26. Eventos Auditáveis
27. Identidade
28. Tenant
29. Caso de Uso
30. Asset ID
31. Prompt Version
32. Model Alias
33. Model ID
34. Provider
35. Configuration Version
36. Agent Policy
37. Tool Execution
38. Human Approval
39. Data Sources
40. Retrieval
41. Release
42. Rollback
43. Incident
44. Exception
45. Risk Acceptance
46. Change Record
47. Decisões Automatizadas
48. Explicabilidade Operacional
49. Reprodutibilidade
50. Limites da Reprodutibilidade
51. Logging
52. Logging Seguro
53. Redação
54. Hashing
55. Correlation ID
56. Trace ID
57. Request ID
58. Audit ID
59. Segregação de Logs
60. Acesso a Logs
61. Exportação
62. Consultas de Auditoria
63. Evidências de Testes
64. Evaluation Reports
65. Quality Gates
66. Security Tests
67. Privacy Tests
68. Cross-Tenant Tests
69. Red Team
70. Evidência de Aprovação
71. Evidência de Deploy
72. Evidência de Provider Review
73. Evidência de Incidente
74. Evidência de Recuperação
75. Compliance Mapping
76. LGPD
77. Políticas Internas
78. Obrigações Contratuais
79. Requisitos de Clientes
80. Normas e Frameworks
81. Control Mapping
82. Control Owner
83. Control Status
84. Control Effectiveness
85. Control Testing
86. Deficiências
87. Findings
88. Severity
89. Remediation
90. Compensating Controls
91. Exceptions
92. Expiration
93. Periodic Review
94. Internal Audit
95. External Audit
96. Audit Request
97. Evidence Package
98. Scope Control
99. Data Minimization
100. Auditor Access
101. Production Access
102. Sampling
103. Continuous Compliance
104. Compliance as Code
105. Automated Evidence
106. Manual Evidence
107. Evidence Freshness
108. Evidence Quality
109. Evidence Gaps
110. Dashboard
111. Métricas
112. Auditoria de Agentes
113. Auditoria de RAG
114. Auditoria de Providers
115. Auditoria de Custos
116. Auditoria de Incidentes
117. Inventário
118. Production Readiness
119. Templates
120. Anti-Padrões
121. Arquitetura Consolidada
122. Checklist
123. Documentos Relacionados
124. Princípios Finais
125. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para auditabilidade, gestão de evidências e demonstração de conformidade das capacidades de Inteligência Artificial do GereIgreja.

Seu objetivo é permitir que decisões técnicas e operacionais relacionadas à IA possam ser verificadas posteriormente sem depender apenas de memória humana, documentação informal ou comportamento atual do sistema.

---

# 2. Escopo

Aplica-se a:

- casos de uso de IA;
- modelos;
- prompts;
- providers;
- configurações;
- RAG;
- agentes;
- tools;
- datasets;
- avaliações;
- releases;
- incidentes;
- exceções;
- controles;
- decisões e aprovações relevantes.

---

# 3. Relação com a Família GAI

```text
GAI-11
Risk Classification
        │
GAI-12
Asset Registry
        │
GAI-13
Prompt / Model / Config
        │
GAI-14
Agents / HITL
        │
GAI-16
Provider Risk
        │
GAI-17
Incident / Recovery
        │
        ▼
GAI-18
Audit / Evidence / Compliance
```

GAI-18 consolida a capacidade de demonstrar que os controles definidos nos demais documentos foram realmente aplicados.

---

# 4. Princípios Fundamentais

Aplicar:

- evidence over assertion;
- traceability;
- minimum necessary logging;
- integrity;
- explicit ownership;
- reproducible governance;
- controlled auditor access;
- evidence retention;
- continuous compliance where useful;
- no secret or sensitive-data overlogging.

---

# 5. Auditabilidade de IA

Um sistema auditável deverá conseguir responder, quando aplicável:

```text
What happened?
When?
For whom?
Under which tenant?
Which AI asset?
Which prompt?
Which model?
Which provider?
Which configuration?
Which data source?
Which tool?
Who approved?
What was the result?
```

---

# 6. Evidência

Evidência é artefato verificável que demonstra a existência, execução ou resultado de um controle, decisão ou evento.

---

# 7. Evidência Técnica

Exemplos:

- commit;
- configuration version;
- test report;
- evaluation report;
- deployment record;
- audit event.

---

# 8. Evidência Operacional

Exemplos:

- dashboard;
- alert;
- incident record;
- runbook execution;
- recovery test.

---

# 9. Evidência de Segurança

Exemplos:

- security review;
- access review;
- vulnerability result;
- red-team result;
- authorization test.

---

# 10. Evidência de Privacidade

Exemplos:

- data mapping;
- retention configuration;
- provider data profile;
- privacy review.

---

# 11. Evidência de Qualidade

Exemplos:

- evaluation dataset;
- regression report;
- quality gate result.

---

# 12. Evidência de Governança

Exemplos:

- risk classification;
- approval;
- exception;
- risk acceptance;
- periodic review.

---

# 13. Evidência de Terceiros

Exemplos:

- provider assessment;
- contractual review;
- security documentation;
- incident notification;
- deprecation notice.

---

# 14. Evidence Registry

Evidências relevantes poderão ser registradas de forma centralizada ou referenciadas a partir do ativo correspondente.

---

# 15. Evidence ID

Formato sugerido:

```text
AI-EVID-YYYY-####
```

---

# 16. Owner

Toda evidência material deverá possuir owner ou fonte responsável.

---

# 17. Proveniência

Registrar origem da evidência.

---

# 18. Integridade

Evidência não deverá ser alterável silenciosamente.

---

# 19. Timestamp

Registrar data e hora confiáveis.

---

# 20. Retenção

Definir retenção conforme:

- finalidade;
- risco;
- política;
- contrato;
- obrigação aplicável.

---

# 21. Classificação

Evidências também poderão conter informação sensível e deverão ser classificadas.

---

# 22. Controle de Acesso

Acesso deverá seguir least privilege.

---

# 23. Imutabilidade

Para eventos críticos, preferir mecanismos append-only ou equivalentes.

---

# 24. Cadeia de Custódia

Quando necessário, registrar quem coletou, transferiu ou acessou determinada evidência.

---

# 25. Audit Trail

Audit trail deverá representar eventos relevantes em sequência temporal.

---

# 26. Eventos Auditáveis

Exemplos:

```text
AI_USE_CASE_APPROVED
AI_PROMPT_PROMOTED
AI_MODEL_ALIAS_CHANGED
AI_PROVIDER_CHANGED
AI_AGENT_ENABLED
AI_TOOL_EXECUTED
AI_HUMAN_APPROVAL_GRANTED
AI_RISK_ACCEPTED
AI_EXCEPTION_CREATED
AI_RELEASE_DEPLOYED
AI_ROLLBACK_EXECUTED
AI_KILL_SWITCH_ACTIVATED
```

---

# 27. Identidade

Eventos mutáveis deverão registrar identidade confiável do ator quando aplicável.

---

# 28. Tenant

Registrar tenant em operações tenant-aware.

---

# 29. Caso de Uso

Relacionar evento ao Use Case ID do GAI-11.

---

# 30. Asset ID

Relacionar ao ativo do GAI-12.

---

# 31. Prompt Version

Registrar identificador e versão, não necessariamente o prompt renderizado completo.

---

# 32. Model Alias

Registrar alias controlado.

---

# 33. Model ID

Registrar modelo concreto quando necessário à investigação.

---

# 34. Provider

Registrar provider utilizado.

---

# 35. Configuration Version

Registrar versão da configuração comportamental.

---

# 36. Agent Policy

Registrar versão da policy.

---

# 37. Tool Execution

Para tools mutáveis, registrar:

```text
tool
actor
tenant
authorization result
effect
status
```

---

# 38. Human Approval

Registrar aprovação vinculada à ação específica conforme GAI-14.

---

# 39. Data Sources

Registrar IDs ou referências de fontes relevantes.

---

# 40. Retrieval

Para casos de maior risco, preservar metadados suficientes para entender quais fontes fundamentaram a execução.

---

# 41. Release

Registrar versão liberada e gates satisfeitos.

---

# 42. Rollback

Registrar motivo e versão de destino.

---

# 43. Incident

Relacionar evidências ao Incident ID.

---

# 44. Exception

Exceções deverão possuir registro próprio.

---

# 45. Risk Acceptance

Aceite de risco deverá registrar:

- risco;
- owner;
- justificativa;
- validade;
- controles compensatórios.

---

# 46. Change Record

Mudanças comportamentais deverão ser rastreáveis.

---

# 47. Decisões Automatizadas

Quando aplicável, registrar informações suficientes para explicar operacionalmente a decisão ou recomendação.

---

# 48. Explicabilidade Operacional

Explicabilidade operacional significa conhecer:

- inputs autorizados;
- fontes;
- configuração;
- modelo;
- regras determinísticas;
- ações;
- resultado.

Não exige exposição de chain-of-thought interno.

---

# 49. Reprodutibilidade

Preservar artefatos que permitam reconstruir condições da execução.

---

# 50. Limites da Reprodutibilidade

Modelos probabilísticos poderão não reproduzir saída idêntica.

O objetivo é reproduzir contexto técnico e configuração, não garantir texto idêntico.

---

# 51. Logging

Logs deverão ser projetados com finalidade clara.

---

# 52. Logging Seguro

Nunca registrar indiscriminadamente:

- prompts completos;
- documentos completos;
- secrets;
- tokens;
- dados sensíveis.

---

# 53. Redação

Aplicar masking ou redaction quando necessário.

---

# 54. Hashing

Hashes poderão comprovar identidade de parâmetros ou conteúdo sem armazenar o valor completo.

---

# 55. Correlation ID

Utilizar para fluxos distribuídos.

---

# 56. Trace ID

Relacionar chamadas técnicas.

---

# 57. Request ID

Identificar request individual.

---

# 58. Audit ID

Identificar evento de auditoria.

---

# 59. Segregação de Logs

Logs de segurança e auditoria poderão exigir armazenamento ou acesso diferenciado.

---

# 60. Acesso a Logs

Acesso administrativo deverá ser auditável.

---

# 61. Exportação

Exportações de evidências deverão preservar integridade e classificação.

---

# 62. Consultas de Auditoria

O sistema deverá permitir localizar evidências por dimensões relevantes.

---

# 63. Evidências de Testes

Resultados de testes relevantes deverão estar associados à versão avaliada.

---

# 64. Evaluation Reports

Relatórios deverão incluir:

```text
dataset
version
model
prompt
configuration
metrics
thresholds
result
```

---

# 65. Quality Gates

Registrar gate e resultado conforme GAI-08.

---

# 66. Security Tests

Preservar evidências de testes exigidos pelo risco.

---

# 67. Privacy Tests

Preservar evidências quando aplicável.

---

# 68. Cross-Tenant Tests

Obrigatórios para features tenant-aware de maior risco.

---

# 69. Red Team

Registrar escopo, versão testada, findings e remediações.

---

# 70. Evidência de Aprovação

Aprovações deverão ser atribuíveis a ator autorizado.

---

# 71. Evidência de Deploy

Registrar:

- release;
- environment;
- time;
- artifacts;
- approver quando exigido.

---

# 72. Evidência de Provider Review

Relacionar ao GAI-16.

---

# 73. Evidência de Incidente

Relacionar ao GAI-17.

---

# 74. Evidência de Recuperação

Registrar testes e validações após recuperação.

---

# 75. Compliance Mapping

Controles poderão ser mapeados a requisitos externos ou internos.

---

# 76. LGPD

Mapeamentos de conformidade deverão considerar obrigações aplicáveis ao tratamento de dados pessoais.

Este documento não substitui avaliação jurídica.

---

# 77. Políticas Internas

Cada controle deverá poder referenciar política interna relevante.

---

# 78. Obrigações Contratuais

Requisitos de clientes ou providers poderão exigir evidências específicas.

---

# 79. Requisitos de Clientes

Evidências compartilhadas deverão respeitar confidencialidade e escopo.

---

# 80. Normas e Frameworks

Quando adotados, deverão ser mapeados de forma explícita e versionada.

---

# 81. Control Mapping

Formato conceitual:

```text
Requirement
    ↓
Control
    ↓
Implementation
    ↓
Evidence
    ↓
Test Result
```

---

# 82. Control Owner

Todo controle deverá possuir owner.

---

# 83. Control Status

Estados sugeridos:

```text
PLANNED
IMPLEMENTED
OPERATING
DEFICIENT
EXCEPTION
RETIRED
```

---

# 84. Control Effectiveness

Implementado não significa efetivo.

Efetividade deverá ser validada quando necessário.

---

# 85. Control Testing

Definir periodicidade proporcional ao risco.

---

# 86. Deficiências

Deficiências deverão ser registradas.

---

# 87. Findings

Finding deverá possuir:

- descrição;
- impacto;
- evidência;
- owner;
- prazo.

---

# 88. Severity

Classificar findings de forma consistente.

---

# 89. Remediation

A remediação deverá ser verificável.

---

# 90. Compensating Controls

Quando controle principal não puder ser implementado, documentar controle compensatório.

---

# 91. Exceptions

Exceções não deverão ser permanentes por omissão.

---

# 92. Expiration

Toda exceção relevante deverá possuir data de expiração ou revisão.

---

# 93. Periodic Review

Revisões periódicas deverão verificar se evidências permanecem atuais.

---

# 94. Internal Audit

Auditoria interna poderá revisar amostras de casos de uso e controles.

---

# 95. External Audit

Auditoria externa deverá receber somente evidências necessárias ao escopo.

---

# 96. Audit Request

Toda solicitação deverá definir:

- escopo;
- período;
- controles;
- evidências;
- destinatário.

---

# 97. Evidence Package

Pacote de evidências poderá conter:

```text
scope
control mapping
asset inventory
risk classification
approvals
test reports
release evidence
incident evidence
exceptions
```

---

# 98. Scope Control

Não fornecer dados fora do escopo apenas por conveniência.

---

# 99. Data Minimization

Pacotes de auditoria deverão aplicar minimização.

---

# 100. Auditor Access

Preferir acesso read-only e temporário quando acesso direto for necessário.

---

# 101. Production Access

Não conceder acesso amplo à produção para coleta de evidências quando exportação controlada for suficiente.

---

# 102. Sampling

Auditorias poderão utilizar amostragem proporcional ao risco.

---

# 103. Continuous Compliance

Controles automatizáveis poderão ser monitorados continuamente.

---

# 104. Compliance as Code

Quando adequado, expressar controles verificáveis como código.

Exemplos:

```text
provider must be approved
agent max_steps must be set
R3 feature must have kill switch
production prompt must be versioned
```

---

# 105. Automated Evidence

CI/CD e runtime poderão gerar evidências automaticamente.

---

# 106. Manual Evidence

Algumas decisões continuarão exigindo evidência humana ou documental.

---

# 107. Evidence Freshness

Evidência antiga poderá não representar o estado atual.

---

# 108. Evidence Quality

Boa evidência deverá ser:

```text
relevant
reliable
traceable
dated
scoped
accessible
```

---

# 109. Evidence Gaps

Gaps deverão gerar ação corretiva.

---

# 110. Dashboard

Governança poderá possuir dashboard de controles e evidências.

---

# 111. Métricas

Exemplos:

```text
ai_controls_total
ai_controls_operating
ai_controls_deficient
ai_evidence_missing
ai_evidence_expired
ai_exceptions_open
ai_findings_open
ai_findings_overdue
ai_audit_events_total
```

---

# 112. Auditoria de Agentes

Verificar:

- autonomia;
- tools;
- approvals;
- limits;
- audit events;
- kill switch.

---

# 113. Auditoria de RAG

Verificar:

- fontes;
- tenant isolation;
- provenance;
- index version;
- retention.

---

# 114. Auditoria de Providers

Verificar:

- approval;
- data profile;
- review;
- contract;
- exit strategy.

---

# 115. Auditoria de Custos

Verificar:

- attribution;
- budgets;
- quotas;
- anomalies;
- owner.

---

# 116. Auditoria de Incidentes

Verificar:

- timeline;
- containment;
- evidence;
- root cause;
- remediation;
- follow-up.

---

# 117. Inventário

GAI-12 deverá servir como ponto de partida para o escopo auditável.

---

# 118. Production Readiness

Antes de produção:

```text
risk recorded?
assets registered?
controls mapped?
tests evidenced?
approvals recorded?
audit events defined?
logging minimized?
retention defined?
exceptions documented?
owner assigned?
```

---

# 119. Templates

## Evidence Record

```text
Evidence ID:
Title:
Owner:
Type:
Control:
Use Case:
Asset:

Source:
Location:
Created At:
Valid Until:

Classification:
Retention:
Integrity Mechanism:

Description:
Scope:
Related Version:
Related Release:
Related Incident:

Status:
```

## Control Record

```text
Control ID:
Title:
Owner:
Requirement:

Applicable Risk Levels:
Applicable Assets:

Implementation:
Evidence:
Test Method:
Test Frequency:

Status:
Effectiveness:

Exceptions:
Findings:
Last Review:
Next Review:
```

## Audit Request

```text
Audit ID:
Requester:
Purpose:
Scope:
Period:

Use Cases:
Assets:
Controls:

Evidence Requested:
Data Restrictions:
Access Method:

Owner:
Due Date:
Status:
```

---

# 120. Anti-Padrões

Evitar:

```text
"we comply"
without evidence
```

---

```text
log everything
just in case
```

---

```text
audit trail
stored only in mutable application logs
```

---

```text
approval
without actor or timestamp
```

---

```text
test report
without artifact version
```

---

```text
exception
without expiration
```

---

```text
audit access
=
production admin access
```

---

```text
chain-of-thought logging
as compliance evidence
```

---

```text
evidence package
containing unnecessary customer data
```

---

# 121. Arquitetura Consolidada

```text
                     AI GOVERNANCE
                          │
                          ▼
                       CONTROLS
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
         TECHNICAL    OPERATIONAL   GOVERNANCE
             │            │            │
             └────────────┼────────────┘
                          ▼
                    IMPLEMENTATION
                          │
                          ▼
                       EVIDENCE
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          TESTS        AUDIT LOGS    APPROVALS
             │            │            │
             └────────────┼────────────┘
                          ▼
                    EVIDENCE REGISTRY
                          │
                          ▼
                   CONTROL MAPPING
                          │
                          ▼
                       AUDIT
                          │
                          ▼
                    REMEDIATION
                          │
                          ▼
                CONTINUOUS COMPLIANCE
```

---

# 122. Checklist

## Auditabilidade

- [ ] use case ID;
- [ ] asset ID;
- [ ] tenant;
- [ ] prompt version;
- [ ] model alias;
- [ ] provider;
- [ ] configuration;
- [ ] agent policy;
- [ ] tool events;
- [ ] approvals.

## Evidências

- [ ] owner;
- [ ] source;
- [ ] timestamp;
- [ ] integrity;
- [ ] classification;
- [ ] retention;
- [ ] access control;
- [ ] freshness.

## Testes

- [ ] evaluation report;
- [ ] quality gates;
- [ ] security tests;
- [ ] privacy tests;
- [ ] cross-tenant tests;
- [ ] red-team evidence quando exigido.

## Governança

- [ ] risk classification;
- [ ] approvals;
- [ ] exceptions;
- [ ] risk acceptance;
- [ ] provider review;
- [ ] periodic review.

## Auditoria

- [ ] scope;
- [ ] evidence package;
- [ ] minimization;
- [ ] auditor access;
- [ ] findings;
- [ ] remediation;
- [ ] follow-up.

## Compliance

- [ ] requirements mapped;
- [ ] controls mapped;
- [ ] control owners;
- [ ] effectiveness;
- [ ] automated evidence quando possível;
- [ ] gaps tracked.

---

# 123. Documentos Relacionados

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
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 124. Princípios Finais

Conformidade não deverá depender de declarações sem rastreabilidade.

```text
Requirement
→ Control
→ Implementation
→ Evidence
→ Verification
```

O princípio central é:

```text
Record what matters.

Preserve trustworthy evidence.

Minimize sensitive data.

Link evidence to versions.

Test control effectiveness.

Make governance auditable.
```

No GereIgreja, a governança de Inteligência Artificial deverá ser tecnicamente demonstrável, operacionalmente verificável e documentalmente rastreável.

---

# 125. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`18-Auditoria-Evidencias-e-Conformidade-de-IA.md`

**Documento**

`GAI-18`

**Código**

`GAI-AI-AUDIT-EVIDENCE-COMPLIANCE`

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

`GAI-17 — Gestão de Incidentes, Continuidade e Recuperação de Inteligência Artificial`

**Próximo documento candidato**

`19-Lifecycle-Desativacao-e-Descomissionamento-de-IA.md`
