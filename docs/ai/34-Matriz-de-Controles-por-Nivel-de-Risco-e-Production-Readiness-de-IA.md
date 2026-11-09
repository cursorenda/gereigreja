Pasta:

docs/ai/

Arquivo:

34-Matriz-de-Controles-por-Nivel-de-Risco-e-Production-Readiness-de-IA.md

Documento:

GAI-34

Código:

GAI-AI-RISK-CONTROL-MATRIX-PRODUCTION-READINESS

Família:

GAI — GereIgreja Artificial Intelligence Engineering

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GAI-34 — Matriz de Controles por Nível de Risco e Production Readiness de Inteligência Artificial

> "O objetivo da governança não é obrigar cada equipe a ler todos os documentos antes de agir. É transformar o nível de risco em um conjunto claro, verificável e proporcional de controles."

---

# 1. Objetivo

Consolidar em uma única matriz os controles mínimos exigidos por nível de risco e definir o checklist oficial de Production Readiness da família GAI.

---

# 2. Níveis de Risco

Referência principal: GAI-11.

```text
R0 — Residual / Informativo
R1 — Baixo
R2 — Moderado
R3 — Alto
R4 — Crítico / Excepcional
```

---

# 3. Convenções

```text
REQ   = obrigatório
COND  = obrigatório quando aplicável
REC   = recomendado
N/A   = normalmente não aplicável
```

---

# 4. Matriz Mestra de Controles

| Controle | R0 | R1 | R2 | R3 | R4 |
|---|:---:|:---:|:---:|:---:|:---:|
| Use Case ID | REQ | REQ | REQ | REQ | REQ |
| Owner | REQ | REQ | REQ | REQ | REQ |
| Risk Classification | REQ | REQ | REQ | REQ | REQ |
| Asset Registry | REC | REQ | REQ | REQ | REQ |
| Provider aprovado | COND | REQ | REQ | REQ | REQ |
| Model aprovado | COND | REQ | REQ | REQ | REQ |
| Prompt versionado | COND | REQ | REQ | REQ | REQ |
| Data Classification | COND | REQ | REQ | REQ | REQ |
| Privacy Review | N/A | COND | COND | REQ | REQ |
| Security Review | N/A | COND | REQ | REQ | REQ |
| Evaluation Suite | REC | REQ | REQ | REQ | REQ |
| Golden Dataset | N/A | REC | REQ | REQ | REQ |
| Regression Tests | REC | REQ | REQ | REQ | REQ |
| Threat Model | N/A | REC | COND | REQ | REQ |
| Red Teaming | N/A | N/A | COND | REQ | REQ |
| Tenant Isolation Tests | COND | COND | REQ | REQ | REQ |
| Observability | REC | REQ | REQ | REQ | REQ |
| Cost Controls | REC | REQ | REQ | REQ | REQ |
| Incident Runbook | N/A | REC | REQ | REQ | REQ |
| Kill Switch | N/A | N/A | COND | REQ | REQ |
| Human-in-the-Loop | N/A | N/A | COND | REQ | REQ |
| AI Impact Assessment | N/A | N/A | COND | REQ | REQ |
| Provider Risk Review | N/A | COND | REQ | REQ | REQ |
| Audit Trail | REC | REQ | REQ | REQ | REQ |
| Evidence Package | N/A | REC | REQ | REQ | REQ |
| Formal Approval | N/A | REC | REQ | REQ | REQ |
| Periodic Review | REC | REQ | REQ | REQ | REQ |
| Decommission Plan | N/A | REC | COND | REQ | REQ |

---

# 5. Production Readiness — Identidade e Governança

Antes de produção:

```text
[ ] Use Case ID
[ ] Owner
[ ] Risk Level
[ ] Assets registered
[ ] Roles and approvers defined
[ ] Exceptions documented
```

---

# 6. Providers, Modelos e Prompts

```text
[ ] Provider approved
[ ] Model approved
[ ] Model alias defined
[ ] Prompt versioned
[ ] Configuration versioned
[ ] Routing policy approved
[ ] Fallback approved
```

---

# 7. Dados e Privacidade

```text
[ ] Data classes known
[ ] Tenant boundaries enforced
[ ] Personal data reviewed
[ ] Sensitive data reviewed
[ ] Retention defined
[ ] Deletion path defined
[ ] RAG sources authorized
[ ] Memory policy defined
```

---

# 8. Segurança

```text
[ ] Threat model
[ ] Authorization enforced outside model
[ ] Tool allowlist
[ ] Cross-tenant tests
[ ] Prompt injection tests
[ ] Secret handling validated
[ ] Red team complete when required
[ ] Kill switch available when required
```

---

# 9. Qualidade

```text
[ ] Evaluation suite
[ ] Golden dataset
[ ] Baseline
[ ] Candidate comparison
[ ] Acceptance thresholds
[ ] Regression tests
[ ] Structured output validation
[ ] Human evaluation when needed
```

---

# 10. Impacto e Fairness

```text
[ ] Impact Assessment when required
[ ] Affected groups identified
[ ] Bias review
[ ] Fairness metrics
[ ] Human review path
[ ] Contestation/correction path
```

---

# 11. Agentes e Tools

```text
[ ] Autonomy level
[ ] Allowed tools
[ ] Max steps
[ ] Timeout
[ ] Token budget
[ ] Cost budget
[ ] Approval policy
[ ] Idempotency
[ ] Abort / kill switch
```

---

# 12. Observabilidade e Operação

```text
[ ] Request ID
[ ] Trace ID
[ ] Model/provider identity
[ ] Prompt/config version
[ ] Token metrics
[ ] Latency metrics
[ ] Cost metrics
[ ] Quality signals
[ ] Security signals
[ ] Alerts
[ ] Dashboard
[ ] Runbook
```

---

# 13. Release

```text
[ ] Quality gates passed
[ ] Security gates passed
[ ] Privacy gates passed
[ ] FinOps gates passed
[ ] Canary or progressive rollout when needed
[ ] Rollback ready
[ ] Abort criteria
```

---

# 14. Evidências

```text
[ ] Evaluation evidence
[ ] Security evidence
[ ] Privacy evidence
[ ] Approval evidence
[ ] Release evidence
[ ] Provider evidence
[ ] Exception evidence
```

---

# 15. Production Readiness Decision

Estados:

```text
READY
READY_WITH_CONDITIONS
BLOCKED
EXCEPTION_REQUIRED
```

---

# 16. Approval Matrix

| Risco | Aprovação mínima |
|---|---|
| R0 | Owner |
| R1 | Owner + gates automatizados |
| R2 | Owner + Engineering/Quality + Security/Privacy quando aplicável |
| R3 | Owner + Engineering + Security + Privacy + Governance + Operations conforme escopo |
| R4 | Aprovação executiva/arquitetural excepcional + controles reforçados |

---

# 17. Template

## AI Production Readiness Record

```text
Readiness ID:
Use Case ID:
Owner:
Risk Level:

Governance:
Providers:
Models:
Prompts:
Data:
Security:
Privacy:
Quality:
Impact:
Agents:
Tools:
Observability:
FinOps:
Incidents:
Evidence:

Exceptions:
Residual Risks:

Decision:
Approvers:
Approved At:
Next Review:
```

---

# 18. Regra de Bloqueio

Nenhum controle marcado como `REQ` poderá ser ignorado sem exceção formal válida.

---

# 19. Documentos Relacionados

Este documento referencia toda a família GAI-01 a GAI-33.

---

# 20. Princípios Finais

```text
Risk Level
→ Required Controls
→ Evidence
→ Approval
→ Production
```

O GAI-34 é o ponto de entrada operacional para equipes que precisam saber o que é obrigatório antes de colocar IA em produção.

---

# 21. Status do Documento

**Arquivo**

`34-Matriz-de-Controles-por-Nivel-de-Risco-e-Production-Readiness-de-IA.md`

**Documento**

`GAI-34`

**Versão**

`1.0`

**Status**

`OFICIAL`
