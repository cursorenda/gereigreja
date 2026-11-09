Pasta:

docs/ai/

Arquivo:

26-Red-Teaming-Adversarial-Testing-e-Seguranca-Ofensiva-de-IA.md

Documento:

GAI-26

Código:

GAI-AI-RED-TEAMING-ADVERSARIAL-TESTING

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

# GAI-26 — Red Teaming, Adversarial Testing e Segurança Ofensiva de Inteligência Artificial

> "Sistemas de IA devem ser avaliados não apenas pelo comportamento esperado, mas também por como resistem a entradas hostis, contextos manipulados, abuso de ferramentas e tentativas de violação dos seus limites."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Conceito de AI Red Teaming
6. Objetivos
7. Autorização
8. Regras de Engajamento
9. Escopo
10. Ambientes
11. Dados de Teste
12. Segurança dos Testes
13. Threat Modeling
14. Attack Surface
15. Prompt Injection
16. Indirect Prompt Injection
17. Jailbreaks
18. Instruction Hierarchy
19. Context Manipulation
20. RAG Poisoning
21. Retrieval Abuse
22. Data Exfiltration
23. Sensitive Data Leakage
24. Secret Leakage
25. Cross-Tenant Leakage
26. Authorization Bypass
27. Tool Abuse
28. Agent Abuse
29. Excessive Agency
30. Privilege Escalation
31. Confused Deputy
32. Unsafe Actions
33. Destructive Actions
34. Resource Exhaustion
35. Cost Abuse
36. Infinite Loops
37. Denial of Wallet
38. Model Extraction
39. Memorization
40. Regurgitation
41. Output Manipulation
42. Hallucination Exploitation
43. Citation Manipulation
44. Social Engineering
45. Impersonation
46. Provider Boundary
47. Supply Chain
48. Model and Dependency Changes
49. Attack Scenarios
50. Test Cases
51. Test Harness
52. Automation
53. Manual Testing
54. Human Creativity
55. Coverage
56. Severity
57. Exploitability
58. Impact
59. Reproducibility
60. Findings
61. Evidence
62. Sensitive Evidence
63. Finding Lifecycle
64. Triage
65. Remediation
66. Retest
67. Closure
68. Risk Acceptance
69. Exceptions
70. Release Gates
71. R1
72. R2
73. R3
74. Continuous Testing
75. Regression
76. Production Testing
77. Safe Production Validation
78. Incident Linkage
79. Purple Teaming
80. Security Engineering Feedback
81. Detection Engineering
82. Observability
83. Metrics
84. Reporting
85. Executive Reporting
86. Engineering Reporting
87. Audit Reporting
88. Third-Party Testing
89. External Assessments
90. Provider Testing
91. Model Upgrades
92. Agent Changes
93. Tool Changes
94. RAG Changes
95. Fine-Tuning Changes
96. Training Data Changes
97. Change Management
98. Test Data Retention
99. Access Control
100. Legal and Contractual Boundaries
101. Responsible Testing
102. Production Readiness
103. Templates
104. Anti-Padrões
105. Arquitetura Consolidada
106. Checklist
107. Documentos Relacionados
108. Princípios Finais
109. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para red teaming, adversarial testing e testes ofensivos autorizados de capacidades de Inteligência Artificial no GereIgreja.

Seu objetivo é identificar falhas de segurança, autorização, isolamento, guardrails, agentes, tools, RAG e comportamento antes que possam produzir impacto real.

---

# 2. Escopo

Aplica-se a:

- modelos;
- prompts;
- AI Gateway;
- RAG;
- agentes;
- tools;
- APIs;
- workflows;
- guardrails;
- fine-tuned models;
- integrações com providers;
- features de IA expostas a usuários;
- sistemas internos de IA.

---

# 3. Relação com a Família GAI

```text
GAI-04
Agents / Tools
      │
GAI-06
Security / Privacy / Guardrails
      │
GAI-08
Tests / Quality Gates
      │
GAI-11
Risk Classification
      │
GAI-14
Agent Governance
      │
GAI-17
Incident Management
      │
GAI-23
Change Management
      │
GAI-25
Fine-Tuning / Custom Models
      │
      ▼
GAI-26
Red Teaming / Adversarial Testing
```

---

# 4. Princípios Fundamentais

Aplicar:

- authorized testing only;
- risk-based depth;
- assume hostile input;
- test controls, not promises;
- isolate dangerous tests;
- preserve tenant boundaries;
- evidence every material finding;
- retest remediation;
- prevent uncontrolled side effects;
- feed findings back into engineering.

---

# 5. Conceito de AI Red Teaming

AI Red Teaming é avaliação adversarial autorizada destinada a descobrir como uma capacidade de IA pode falhar ou ser abusada diante de entradas e contextos hostis.

---

# 6. Objetivos

Avaliar se o sistema:

```text
protects data
enforces authorization
resists manipulation
limits autonomy
controls tools
preserves isolation
fails safely
produces evidence
```

---

# 7. Autorização

Nenhum teste ofensivo deverá ocorrer fora de autorização explícita e escopo definido.

---

# 8. Regras de Engajamento

Definir antes do teste:

- sistemas permitidos;
- ambientes;
- horários;
- dados;
- técnicas;
- limites;
- contatos;
- stop conditions.

---

# 9. Escopo

O escopo deverá identificar claramente ativos e interfaces autorizados.

---

# 10. Ambientes

Preferir ambientes isolados e representativos.

Produção somente deverá ser testada quando necessário, autorizado e seguro.

---

# 11. Dados de Teste

Preferir dados sintéticos ou controlados.

---

# 12. Segurança dos Testes

Testes não deverão criar risco desnecessário para clientes, tenants ou infraestrutura.

---

# 13. Threat Modeling

O plano de red team deverá derivar de ameaças relevantes ao sistema.

---

# 14. Attack Surface

Mapear:

```text
user input
system instructions
retrieved content
files
APIs
tools
agents
providers
memory/context
outputs
logs
```

---

# 15. Prompt Injection

Testar tentativas de fazer conteúdo não confiável alterar comportamento autorizado.

---

# 16. Indirect Prompt Injection

Testar instruções maliciosas presentes em documentos, páginas ou dados recuperados.

---

# 17. Jailbreaks

Avaliar resistência a tentativas de contornar políticas e guardrails aplicáveis.

---

# 18. Instruction Hierarchy

Verificar se entradas de menor confiança conseguem sobrescrever controles de maior autoridade.

---

# 19. Context Manipulation

Testar manipulação do contexto disponível ao modelo.

---

# 20. RAG Poisoning

Avaliar impacto de conteúdo malicioso ou comprometido na base de conhecimento.

---

# 21. Retrieval Abuse

Testar consultas destinadas a recuperar conteúdo fora do escopo autorizado.

---

# 22. Data Exfiltration

Testar se entradas hostis conseguem induzir divulgação indevida de dados.

---

# 23. Sensitive Data Leakage

Avaliar exposição de dados pessoais, sensíveis ou confidenciais.

---

# 24. Secret Leakage

Verificar se secrets podem aparecer em prompts, contexto, tools, logs ou outputs.

---

# 25. Cross-Tenant Leakage

Testar isolamento entre tenants como controle técnico.

---

# 26. Authorization Bypass

Verificar se IA consegue executar ações além da autorização do usuário.

---

# 27. Tool Abuse

Testar parâmetros, escopo e efeitos de tools de forma controlada.

---

# 28. Agent Abuse

Avaliar como agentes se comportam diante de objetivos manipulados ou contexto hostil.

---

# 29. Excessive Agency

Testar se o agente executa mais ações do que o necessário ou autorizado.

---

# 30. Privilege Escalation

Avaliar se ferramentas ou integrações permitem ampliar privilégios indevidamente.

---

# 31. Confused Deputy

Testar se o sistema usa sua própria autoridade para executar ação que o solicitante não poderia executar diretamente.

---

# 32. Unsafe Actions

Validar bloqueios para ações incompatíveis com políticas.

---

# 33. Destructive Actions

Testes de ações destrutivas deverão utilizar mocks, sandboxes ou recursos descartáveis sempre que possível.

---

# 34. Resource Exhaustion

Avaliar loops, fan-out, chamadas excessivas e consumo de recursos.

---

# 35. Cost Abuse

Testar se usuários ou agentes podem provocar consumo financeiro desproporcional.

---

# 36. Infinite Loops

Agentes deverão ser testados contra ciclos não terminantes.

---

# 37. Denial of Wallet

Avaliar cenários de consumo econômico abusivo que possam esgotar quotas ou orçamento.

---

# 38. Model Extraction

Quando relevante, avaliar exposição indevida de comportamento proprietário ou artefatos.

---

# 39. Memorization

Avaliar risco de memorização em modelos customizados.

---

# 40. Regurgitation

Testar reprodução indevida de conteúdo sensível ou protegido quando aplicável.

---

# 41. Output Manipulation

Verificar se outputs podem induzir downstream systems a executar comportamento não autorizado.

---

# 42. Hallucination Exploitation

Avaliar cenários em que respostas incorretas possam gerar ação ou impacto.

---

# 43. Citation Manipulation

Testar fabricação, troca ou atribuição incorreta de fontes.

---

# 44. Social Engineering

Avaliar se o sistema pode ser manipulado para facilitar engano dentro do contexto de risco autorizado.

---

# 45. Impersonation

Testar controles contra representação indevida de identidade quando aplicável.

---

# 46. Provider Boundary

Avaliar controles nas fronteiras entre GereIgreja e providers.

---

# 47. Supply Chain

Considerar dependências, SDKs, modelos, datasets e integrações.

---

# 48. Model and Dependency Changes

Mudanças relevantes deverão disparar regressões adversariais proporcionais.

---

# 49. Attack Scenarios

Cada cenário deverá possuir:

```text
scenario ID
threat
preconditions
target
expected control
test method
success criteria
evidence
```

---

# 50. Test Cases

Casos de teste deverão ser reproduzíveis quando possível.

---

# 51. Test Harness

Preferir harness controlado para execução repetível.

---

# 52. Automation

Automatizar cenários estáveis de regressão.

---

# 53. Manual Testing

Testes manuais continuam necessários para exploração criativa.

---

# 54. Human Creativity

Adversarial testing não deverá depender exclusivamente de listas estáticas.

---

# 55. Coverage

Cobertura deverá considerar superfície e risco, não apenas quantidade de prompts.

---

# 56. Severity

Classificação sugerida:

```text
CRITICAL
HIGH
MEDIUM
LOW
INFORMATIONAL
```

---

# 57. Exploitability

Considerar dificuldade, pré-condições e repetibilidade.

---

# 58. Impact

Considerar:

- tenants;
- dados;
- autorização;
- disponibilidade;
- custo;
- reputação;
- compliance.

---

# 59. Reproducibility

Registrar condições necessárias para reproduzir o finding.

---

# 60. Findings

Todo finding material deverá possuir owner e lifecycle.

---

# 61. Evidence

Preservar evidência suficiente sem ampliar exposição de dados.

---

# 62. Sensitive Evidence

PoCs e evidências perigosas deverão possuir acesso restrito.

---

# 63. Finding Lifecycle

```text
OPEN
  ↓
TRIAGED
  ↓
ASSIGNED
  ↓
REMEDIATING
  ↓
RETEST
  ↓
CLOSED
```

---

# 64. Triage

Confirmar validade, impacto e prioridade.

---

# 65. Remediation

Correções deverão atacar causa e não apenas um prompt específico quando o problema for sistêmico.

---

# 66. Retest

Findings críticos e altos deverão ser retestados após correção.

---

# 67. Closure

Closure exige evidência de correção ou aceite formal de risco.

---

# 68. Risk Acceptance

Aplicar GAI-21 e GAI-23.

---

# 69. Exceptions

Exceções deverão possuir prazo e controles compensatórios.

---

# 70. Release Gates

Findings acima do risco aceito deverão bloquear promoção.

---

# 71. R1

Casos de baixo risco poderão possuir conjunto adversarial básico.

---

# 72. R2

Exigir cobertura ampliada das superfícies relevantes.

---

# 73. R3

Exigir avaliação adversarial reforçada antes de produção e após mudanças materiais.

---

# 74. Continuous Testing

Cenários críticos deverão entrar em regressão contínua quando possível.

---

# 75. Regression

Um finding corrigido deverá gerar teste de regressão apropriado.

---

# 76. Production Testing

Somente com autorização, limites e observabilidade adequados.

---

# 77. Safe Production Validation

Preferir verificações sem efeitos destrutivos.

---

# 78. Incident Linkage

Findings relacionados a incidentes deverão ser vinculados ao registro correspondente.

---

# 79. Purple Teaming

Red team e defesa deverão colaborar para transformar descobertas em controles e detecções.

---

# 80. Security Engineering Feedback

Findings deverão alimentar padrões de arquitetura e desenvolvimento.

---

# 81. Detection Engineering

Criar sinais detectivos para padrões de ataque relevantes quando possível.

---

# 82. Observability

Monitorar:

- denied actions;
- guardrail triggers;
- unusual tool usage;
- abnormal agent loops;
- retrieval anomalies;
- cost spikes.

---

# 83. Metrics

Exemplos:

```text
ai_red_team_findings
ai_critical_findings_open
ai_high_findings_open
ai_mean_time_to_remediate
ai_retest_failure_rate
ai_adversarial_regression_coverage
ai_cross_tenant_test_failures
ai_tool_abuse_test_failures
```

---

# 84. Reporting

Relatórios deverão separar risco técnico de detalhes sensíveis de exploração.

---

# 85. Executive Reporting

Foco:

- exposição;
- findings críticos;
- tendência;
- tempo de correção;
- risco residual.

---

# 86. Engineering Reporting

Foco:

- reprodução;
- causa;
- controle esperado;
- correção;
- regressão.

---

# 87. Audit Reporting

Foco:

- escopo;
- metodologia;
- evidências;
- findings;
- remediation;
- closure.

---

# 88. Third-Party Testing

Avaliações externas deverão possuir autorização e regras de engajamento.

---

# 89. External Assessments

Podem complementar, não substituir, testes internos contínuos.

---

# 90. Provider Testing

Respeitar limites contratuais e políticas aplicáveis ao provider.

---

# 91. Model Upgrades

Mudança de modelo poderá alterar resistência adversarial.

---

# 92. Agent Changes

Mudanças de autonomia, tools ou workflow exigem regressão relevante.

---

# 93. Tool Changes

Nova tool deverá ampliar o plano de testes.

---

# 94. RAG Changes

Novas fontes ou mecanismos de retrieval deverão ser avaliados contra poisoning e leakage.

---

# 95. Fine-Tuning Changes

Aplicar testes de memorization, leakage e regressão conforme GAI-25.

---

# 96. Training Data Changes

Mudanças de dataset poderão introduzir novos comportamentos adversariais.

---

# 97. Change Management

Aplicar GAI-23.

---

# 98. Test Data Retention

Dados e resultados de teste deverão seguir retenção definida.

---

# 99. Access Control

Resultados ofensivos sensíveis deverão seguir least privilege.

---

# 100. Legal and Contractual Boundaries

Nenhum teste deverá ultrapassar autorização legal, contratual ou operacional.

---

# 101. Responsible Testing

A equipe deverá minimizar efeitos reais e interromper testes diante de risco inesperado.

---

# 102. Production Readiness

Antes de produção de R2/R3:

```text
threat model?
attack surface mapped?
prompt injection tested?
RAG abuse tested?
authorization tested?
tenant isolation tested?
tools tested?
agent limits tested?
cost abuse tested?
findings triaged?
critical findings closed?
regressions created?
evidence preserved?
```

---

# 103. Templates

## AI Red Team Plan

```text
Assessment ID:
Owner:
Date:
Use Case:
Risk Level:

Scope:
In-Scope Assets:
Out-of-Scope Assets:
Environment:

Rules of Engagement:
Allowed Techniques:
Prohibited Techniques:
Stop Conditions:

Threat Model:
Attack Surfaces:

Test Categories:
Success Criteria:

Contacts:
Emergency Contact:
Evidence Location:
Approval:
```

## AI Adversarial Test Case

```text
Test ID:
Assessment ID:
Threat:
Target:

Preconditions:
Input / Scenario:
Expected Control:

Observed Result:
Pass / Fail:

Severity:
Impact:
Exploitability:
Reproducibility:

Evidence:
Finding ID:
```

## AI Security Finding

```text
Finding ID:
Title:
Severity:
Owner:

Affected Assets:
Risk Level:

Description:
Preconditions:
Impact:
Expected Control:

Evidence:
Root Cause:

Remediation:
Compensating Controls:
Target Date:

Retest:
Retest Result:
Risk Acceptance:

Status:
Closed At:
```

---

# 104. Anti-Padrões

Evitar:

```text
red team
=
random jailbreak prompts
```

---

```text
production attack testing
without authorization
```

---

```text
cross-tenant test
using real customer data
```

---

```text
finding closed
without retest
```

---

```text
prompt patch
for systemic authorization flaw
```

---

```text
agent red team
without testing tools
```

---

```text
security test
that causes real destructive action
when sandbox was available
```

---

```text
critical PoC
stored in public documentation
```

---

```text
model upgrade
without adversarial regression
```

---

# 105. Arquitetura Consolidada

```text
                       THREAT MODEL
                            │
                            ▼
                      ATTACK SURFACE
                            │
                            ▼
                       TEST PLAN
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          AUTOMATED       MANUAL       RED TEAM
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                         FINDINGS
                            │
                            ▼
                          TRIAGE
                            │
                            ▼
                       REMEDIATION
                            │
                            ▼
                          RETEST
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
               PASS                   FAIL
                 │                     │
                 ▼                     └──────► REMEDIATION
              REGRESSION
                 │
                 ▼
           CONTINUOUS TESTING
```

---

# 106. Checklist

## Planejamento

- [ ] autorização;
- [ ] scope;
- [ ] environment;
- [ ] rules of engagement;
- [ ] stop conditions;
- [ ] threat model;
- [ ] attack surface.

## Testes

- [ ] prompt injection;
- [ ] indirect injection;
- [ ] RAG poisoning;
- [ ] retrieval abuse;
- [ ] data leakage;
- [ ] secrets;
- [ ] cross-tenant;
- [ ] authorization;
- [ ] tools;
- [ ] agents;
- [ ] cost abuse;
- [ ] resource exhaustion.

## Findings

- [ ] severity;
- [ ] impact;
- [ ] exploitability;
- [ ] reproducibility;
- [ ] evidence;
- [ ] owner;
- [ ] remediation;
- [ ] retest.

## Governança

- [ ] risk acceptance;
- [ ] exceptions;
- [ ] release gates;
- [ ] change linkage;
- [ ] incident linkage;
- [ ] audit trail.

## Continuidade

- [ ] regression tests;
- [ ] continuous testing;
- [ ] model upgrade tests;
- [ ] agent/tool change tests;
- [ ] RAG change tests;
- [ ] fine-tuning tests.

---

# 107. Documentos Relacionados

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
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 108. Princípios Finais

Segurança de IA não pode ser demonstrada apenas testando caminhos felizes.

```text
Expected Input
is only part of reality.

Hostile Input
must also be part of testing.
```

O princípio central é:

```text
Threat model first.

Test real controls.

Assume hostile context.

Limit test blast radius.

Record findings.

Fix root causes.

Retest.

Turn every important finding into regression.
```

No GereIgreja, red teaming deverá funcionar como mecanismo contínuo de aprendizagem de segurança, fortalecendo arquitetura, guardrails, agentes, tools e processos de release.

---

# 109. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`26-Red-Teaming-Adversarial-Testing-e-Seguranca-Ofensiva-de-IA.md`

**Documento**

`GAI-26`

**Código**

`GAI-AI-RED-TEAMING-ADVERSARIAL-TESTING`

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

`GAI-25 — Governança de Datasets Sintéticos, Fine-Tuning e Customização de Modelos`

**Próximo documento candidato**

`27-Governanca-de-Memoria-Contexto-Persistente-e-Personalizacao-de-IA.md`
