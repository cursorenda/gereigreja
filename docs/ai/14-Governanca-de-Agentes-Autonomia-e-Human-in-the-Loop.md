Pasta:

docs/ai/

Arquivo:

14-Governanca-de-Agentes-Autonomia-e-Human-in-the-Loop.md

Documento:

GAI-14

Código:

GAI-AI-AGENT-AUTONOMY-HITL-GOVERNANCE

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

# GAI-14 — Governança de Agentes, Autonomia e Human-in-the-Loop

> "Autonomia não é uma propriedade do modelo. É uma permissão concedida pela arquitetura."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Conceito de Agente
6. Agente versus Assistente
7. Autonomia
8. Escala de Autonomia
9. Nível A0 — Informativo
10. Nível A1 — Recomendação
11. Nível A2 — Preparação
12. Nível A3 — Execução Confirmada
13. Nível A4 — Execução Autônoma Limitada
14. Nível A5 — Autonomia Privilegiada
15. Relação entre Autonomia e Risco
16. Agent Policy
17. Agent Identity
18. Agent Owner
19. Finalidade
20. Escopo
21. Tenant Context
22. User Context
23. Authorization Context
24. Tool Registry
25. Tool Allowlist
26. Tool Denylist
27. Tool Schemas
28. Tool Authorization
29. Tool Mutability
30. Tool Risk
31. Tool Results
32. Tool Chaining
33. Max Steps
34. Max Tool Calls
35. Timeout
36. Token Budget
37. Cost Budget
38. Rate Limits
39. Concurrency
40. Loop Detection
41. Stop Conditions
42. Abort
43. Kill Switch
44. Human-in-the-Loop
45. Quando Exigir HITL
46. Preview
47. Confirmation
48. Approval Token
49. Reautorização
50. Expiração da Aprovação
51. Mudança após Aprovação
52. Ações Financeiras
53. Ações Destrutivas
54. Comunicação Externa
55. Alterações de Permissão
56. Operações em Massa
57. Dados Sensíveis
58. Multi-Tenant
59. Delegação
60. Subagentes
61. Agent-to-Agent
62. Memória
63. Estado
64. Sessões
65. Persistência
66. Dados em Memória
67. Retenção
68. Prompt Injection
69. Indirect Prompt Injection
70. Tool Injection
71. Confused Deputy
72. Exfiltração
73. Escalada de Privilégio
74. Cross-Tenant Leakage
75. Idempotência
76. Side Effects
77. Compensação
78. Transactions
79. Jobs Assíncronos
80. Long-Running Agents
81. Resumption
82. Model Failure
83. Tool Failure
84. Partial Failure
85. Fallback
86. Degradação Segura
87. Auditoria
88. Observabilidade
89. Métricas
90. Tracing
91. Evaluation
92. Agent Evaluation
93. Trajectory Evaluation
94. Outcome Evaluation
95. Security Evaluation
96. Simulation
97. Sandbox
98. Red Team
99. Release
100. Canary
101. Feature Flags
102. Rollback
103. Inventário
104. Reclassificação
105. Production Readiness
106. Runbook
107. Incidentes
108. Emergency Disable
109. Templates
110. Anti-Padrões
111. Arquitetura Consolidada
112. Checklist
113. Documentos Relacionados
114. Princípios Finais
115. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para governança de agentes de Inteligência Artificial, níveis de autonomia e mecanismos Human-in-the-Loop no GereIgreja.

Seu objetivo é garantir que agentes possam auxiliar ou executar tarefas somente dentro de limites explicitamente concedidos pela aplicação.

---

# 2. Escopo

Aplica-se a:

- agentes;
- assistentes com tools;
- workflows multi-step;
- automações orientadas por modelos;
- tool calling;
- subagentes;
- ações preparadas;
- ações confirmadas;
- execução autônoma limitada.

---

# 3. Relação com a Família GAI

```text
GAI-04
Tools / Agents / Safe Actions
        │
        ▼
GAI-11
Use Case Risk
        │
        ▼
GAI-12 / GAI-13
Assets / Configurations
        │
        ▼
GAI-14
Agent Autonomy / HITL Governance
```

GAI-04 define os fundamentos técnicos.

GAI-14 formaliza os níveis de autonomia e controles de governança.

---

# 4. Princípios Fundamentais

Aplicar:

- least autonomy;
- least privilege;
- explicit tool access;
- deterministic authorization;
- bounded execution;
- human control for consequential actions;
- reversible operations when possible;
- tenant isolation;
- auditable effects;
- immediate containment capability.

---

# 5. Conceito de Agente

Agente é um runtime no qual um modelo pode selecionar ou coordenar múltiplas etapas para alcançar um objetivo dentro de uma policy definida.

```text
Goal
 ↓
Agent Runtime
 ↓
Reason / Select
 ↓
Tool
 ↓
Observe
 ↓
Continue or Stop
```

---

# 6. Agente versus Assistente

Um assistente poderá apenas gerar informação.

Um agente poderá interagir com ferramentas e produzir efeitos.

Quanto maior a capacidade de produzir efeitos, maior o rigor.

---

# 7. Autonomia

Autonomia deverá ser concedida explicitamente.

Nunca inferida apenas porque o modelo suporta tool calling.

---

# 8. Escala de Autonomia

O GereIgreja adota:

```text
A0 — Informativo
A1 — Recomendação
A2 — Preparação
A3 — Execução Confirmada
A4 — Execução Autônoma Limitada
A5 — Autonomia Privilegiada
```

---

# 9. Nível A0 — Informativo

O sistema apenas responde ou explica.

Sem tools mutáveis.

---

# 10. Nível A1 — Recomendação

O sistema recomenda ações, mas não as prepara nem executa.

---

# 11. Nível A2 — Preparação

O sistema prepara uma ação para revisão humana.

Exemplo:

```text
AI
→ draft
→ preview
→ user decides
```

---

# 12. Nível A3 — Execução Confirmada

O sistema poderá executar somente após confirmação explícita.

```text
AI Proposal
   ↓
Preview
   ↓
User Confirmation
   ↓
Authorization Recheck
   ↓
Execution
```

---

# 13. Nível A4 — Execução Autônoma Limitada

O agente poderá executar ações previamente aprovadas dentro de limites estritos.

Exige controles reforçados.

---

# 14. Nível A5 — Autonomia Privilegiada

Representa autonomia ampla sobre operações privilegiadas ou de alto impacto.

A5 é proibido por padrão.

Qualquer exceção exige aprovação arquitetural, de segurança e governança específica.

---

# 15. Relação entre Autonomia e Risco

Autonomia e risco são dimensões relacionadas.

```text
Higher Autonomy
+
Higher Impact
=
Stronger Controls
```

A classificação final deverá seguir GAI-11.

---

# 16. Agent Policy

Todo agente deverá possuir policy explícita.

Campos recomendados:

```text
agent_id
risk_level
autonomy_level
allowed_tools
max_steps
timeout
token_budget
cost_budget
confirmation_policy
kill_switch
```

---

# 17. Agent Identity

Cada agente deverá possuir ID estável conforme GAI-12.

---

# 18. Agent Owner

Todo agente deverá possuir owner.

---

# 19. Finalidade

Um agente deverá possuir objetivo funcional limitado.

Evitar agentes genéricos com acesso amplo.

---

# 20. Escopo

Definir claramente quais operações são permitidas.

---

# 21. Tenant Context

Tenant deverá ser fornecido pela aplicação.

Nunca selecionado livremente pelo modelo.

---

# 22. User Context

Identidade do usuário deverá vir do sistema confiável de autenticação.

---

# 23. Authorization Context

Permissões deverão ser calculadas deterministicamente.

---

# 24. Tool Registry

Agentes somente poderão acessar tools registradas.

---

# 25. Tool Allowlist

Preferir allowlist explícita.

---

# 26. Tool Denylist

Denylist poderá complementar, mas não substituir allowlist.

---

# 27. Tool Schemas

Entradas e saídas deverão possuir schemas.

---

# 28. Tool Authorization

Fluxo obrigatório:

```text
Model Requests Tool
       ↓
Validate Schema
       ↓
Resolve Trusted Context
       ↓
Authorize
       ↓
Execute
```

---

# 29. Tool Mutability

Classificar tools:

```text
READ_ONLY
PREPARE
MUTATE
DESTRUCTIVE
PRIVILEGED
```

---

# 30. Tool Risk

Tool de maior risco poderá elevar o risco do agente inteiro.

---

# 31. Tool Results

Resultados deverão ser minimizados antes de retornar ao modelo.

---

# 32. Tool Chaining

Combinações de tools podem criar capacidade maior que cada tool isoladamente.

Avaliar riscos compostos.

---

# 33. Max Steps

Todo agente multi-step deverá possuir limite.

---

# 34. Max Tool Calls

Definir limite quando necessário.

---

# 35. Timeout

Toda execução deverá possuir timeout.

---

# 36. Token Budget

Definir teto de tokens quando aplicável.

---

# 37. Cost Budget

Agentes recorrentes ou multi-step deverão possuir budget.

---

# 38. Rate Limits

Aplicar limites por usuário, tenant ou feature conforme risco.

---

# 39. Concurrency

Limitar concorrência em ações caras ou mutáveis.

---

# 40. Loop Detection

Detectar repetição improdutiva.

---

# 41. Stop Conditions

Definir condições de sucesso, falha e interrupção.

---

# 42. Abort

O runtime deverá conseguir abortar execução.

---

# 43. Kill Switch

Agentes R3+ deverão possuir mecanismo rápido de desativação quando tecnicamente aplicável.

---

# 44. Human-in-the-Loop

HITL é controle arquitetural, não simples mensagem de confirmação.

---

# 45. Quando Exigir HITL

Exigir ou avaliar fortemente para:

- ações financeiras;
- destruição;
- alteração de permissões;
- comunicação externa;
- operações em massa;
- dados sensíveis;
- baixa reversibilidade.

---

# 46. Preview

Antes da confirmação, apresentar claramente o efeito pretendido.

---

# 47. Confirmation

Confirmação deverá estar vinculada à ação específica.

---

# 48. Approval Token

A aplicação poderá gerar token ou registro de aprovação contendo:

```text
user
tenant
action
parameters_hash
expires_at
```

---

# 49. Reautorização

A autorização deverá ser revalidada imediatamente antes da execução quando necessário.

---

# 50. Expiração da Aprovação

Aprovação deverá expirar após janela apropriada.

---

# 51. Mudança após Aprovação

Se parâmetros materiais mudarem, exigir nova confirmação.

---

# 52. Ações Financeiras

Deverão possuir controles reforçados e confirmação adequada.

---

# 53. Ações Destrutivas

Preferir:

```text
preview
→ confirm
→ execute
→ audit
```

---

# 54. Comunicação Externa

Distinguir:

```text
draft
send one
bulk send
autonomous campaign
```

Cada nível possui risco diferente.

---

# 55. Alterações de Permissão

Não permitir decisão autônoma do modelo sobre concessão de privilégios.

---

# 56. Operações em Massa

Exigem limites e preview do alcance.

---

# 57. Dados Sensíveis

Minimizar exposição em cada passo.

---

# 58. Multi-Tenant

Agente não deverá possuir capacidade de atravessar tenants fora de casos explicitamente aprovados.

---

# 59. Delegação

Permissões do usuário não deverão ser ampliadas pela presença do agente.

---

# 60. Subagentes

Subagentes herdam limites máximos do agente pai e poderão receber subconjunto menor.

Nunca ampliar privilégios por delegação.

---

# 61. Agent-to-Agent

Comunicação entre agentes deverá preservar:

- identidade;
- tenant;
- policy;
- provenance;
- limites.

---

# 62. Memória

Memória não deverá ser ativada por padrão.

---

# 63. Estado

Estado operacional deverá ser separado de conhecimento permanente.

---

# 64. Sessões

Sessões deverão possuir escopo e expiração.

---

# 65. Persistência

Persistir somente o necessário para a finalidade.

---

# 66. Dados em Memória

Não armazenar secrets ou dados sensíveis sem necessidade e governança explícita.

---

# 67. Retenção

Definir lifecycle conforme GAI-07.

---

# 68. Prompt Injection

Inputs adversariais não deverão alterar policy de autorização.

---

# 69. Indirect Prompt Injection

Conteúdo recuperado ou retornado por tools é não confiável.

---

# 70. Tool Injection

Uma tool não deverá poder instruir o agente a ignorar políticas superiores.

---

# 71. Confused Deputy

O agente não deverá utilizar seus privilégios para realizar ação que o usuário não poderia realizar.

---

# 72. Exfiltração

Bloquear caminhos que permitam enviar dados para destinos não autorizados.

---

# 73. Escalada de Privilégio

Permissões são definidas fora do modelo.

---

# 74. Cross-Tenant Leakage

Testes cross-tenant são obrigatórios para agentes tenant-aware.

---

# 75. Idempotência

Tools mutáveis deverão utilizar idempotency keys quando apropriado.

---

# 76. Side Effects

Todo efeito deverá ser conhecido antes de liberar a tool.

---

# 77. Compensação

Quando possível, definir ação compensatória.

---

# 78. Transactions

Operações compostas deverão considerar consistência transacional.

---

# 79. Jobs Assíncronos

Agentes assíncronos deverão carregar contexto seguro e limitado.

---

# 80. Long-Running Agents

Devem possuir:

- checkpoint;
- timeout;
- cancellation;
- budget;
- version pinning quando necessário.

---

# 81. Resumption

Ao retomar, revalidar contexto e autorização quando aplicável.

---

# 82. Model Failure

Falha do modelo deverá terminar ou degradar com segurança.

---

# 83. Tool Failure

Erro de tool não deverá gerar repetição ilimitada.

---

# 84. Partial Failure

Definir comportamento para execução parcialmente concluída.

---

# 85. Fallback

Fallback de modelo não poderá ampliar permissões.

---

# 86. Degradação Segura

Quando autonomia não puder operar com segurança, reduzir capacidade.

```text
A4
↓ failure/risk
A2 or A1
```

---

# 87. Auditoria

Auditar:

- ação solicitada;
- usuário;
- tenant;
- tool;
- resultado;
- aprovação;
- efeito.

Não auditar chain-of-thought interno.

---

# 88. Observabilidade

Registrar metadados operacionais.

---

# 89. Métricas

Exemplos:

```text
agent_runs_total
agent_success_rate
agent_abort_rate
agent_tool_calls
agent_confirmation_rate
agent_denied_actions
agent_loop_terminations
agent_cost
```

---

# 90. Tracing

Traçar etapas sem registrar dados sensíveis desnecessariamente.

---

# 91. Evaluation

Aplicar GAI-08.

---

# 92. Agent Evaluation

Avaliar casos completos.

---

# 93. Trajectory Evaluation

Verificar sequência de tools e decisões observáveis.

---

# 94. Outcome Evaluation

Verificar resultado final e efeitos.

---

# 95. Security Evaluation

Incluir ataques adversariais.

---

# 96. Simulation

Preferir ambientes simulados para agentes mutáveis durante testes.

---

# 97. Sandbox

Ferramentas de engenharia ou operações deverão usar sandbox quando apropriado.

---

# 98. Red Team

Agentes R3+ deverão receber testes adversariais reforçados.

---

# 99. Release

Aplicar GAI-09.

---

# 100. Canary

Liberar autonomia progressivamente.

---

# 101. Feature Flags

Separar ativação da capacidade e nível de autonomia quando necessário.

---

# 102. Rollback

Deverá permitir reduzir ou remover autonomia rapidamente.

---

# 103. Inventário

Registrar agente, tools, policy e dependências conforme GAI-12.

---

# 104. Reclassificação

Nova tool ou maior autonomia exige reavaliação de risco.

---

# 105. Production Readiness

Antes de produção:

```text
agent registered?
owner?
risk?
autonomy?
tools?
permissions?
limits?
HITL?
tests?
kill switch?
runbook?
```

---

# 106. Runbook

Agentes de maior risco deverão possuir runbook operacional.

---

# 107. Incidentes

Incidentes envolvendo agentes deverão seguir processos oficiais de segurança e operação.

---

# 108. Emergency Disable

Deverá existir caminho para desabilitar:

- agente;
- tool;
- provider;
- feature;

conforme natureza do incidente.

---

# 109. Templates

## Registro de Agent Policy

```text
Agent ID:
Owner:
Purpose:
Risk Level:
Autonomy Level:

Tenant Scope:
User Scope:

Model Alias:
Prompt Version:

Allowed Tools:
Denied Tools:

Max Steps:
Max Tool Calls:
Timeout:
Token Budget:
Cost Budget:

Confirmation Policy:
Destructive Actions:
Bulk Actions:

Memory:
Retention:

Feature Flag:
Kill Switch:

Evaluation:
Security Review:
Last Review:
```

## Registro de Aprovação

```text
Approval ID:
User:
Tenant:
Agent:
Action:
Parameters Hash:
Created At:
Expires At:
Status:
Execution ID:
```

---

# 110. Anti-Padrões

Evitar:

```text
agent
→ all tools
```

---

```text
model arguments
→ trusted tenant_id
```

---

```text
"Are you sure?"
without binding confirmation to action
```

---

```text
subagent
with more privilege than parent
```

---

```text
infinite agent loop
```

---

```text
retry destructive tool
without idempotency
```

---

```text
agent memory
as permanent unrestricted database
```

---

```text
prompt says "do not access other tenants"
instead of enforcing tenant isolation
```

---

```text
A5 autonomy
because model benchmark improved
```

---

# 111. Arquitetura Consolidada

```text
                        USER GOAL
                            │
                            ▼
                     TRUSTED CONTEXT
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
               TENANT             PERMISSIONS
                  │                   │
                  └─────────┬─────────┘
                            ▼
                       AGENT POLICY
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          AUTONOMY       LIMITS         TOOLS
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                       AGENT RUNTIME
                            │
                            ▼
                      TOOL PROPOSAL
                            │
                            ▼
                 DETERMINISTIC CHECKS
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
         AUTHORIZE        HITL          VALIDATE
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                         EXECUTE
                            │
                            ▼
                    DOMAIN / SERVICE
                            │
                            ▼
                  AUDIT / OBSERVABILITY
```

---

# 112. Checklist

## Identidade

- [ ] Agent ID;
- [ ] owner;
- [ ] finalidade;
- [ ] risco;
- [ ] autonomia.

## Contexto

- [ ] user confiável;
- [ ] tenant confiável;
- [ ] autorização determinística;
- [ ] dados minimizados.

## Tools

- [ ] registry;
- [ ] allowlist;
- [ ] schemas;
- [ ] autorização;
- [ ] mutability class;
- [ ] risk class;
- [ ] idempotência.

## Limites

- [ ] max steps;
- [ ] max tool calls;
- [ ] timeout;
- [ ] token budget;
- [ ] cost budget;
- [ ] rate limits;
- [ ] loop detection.

## HITL

- [ ] preview;
- [ ] confirmation;
- [ ] approval binding;
- [ ] expiration;
- [ ] reauthorization;
- [ ] new approval after material change.

## Segurança

- [ ] prompt injection;
- [ ] indirect injection;
- [ ] confused deputy;
- [ ] exfiltration;
- [ ] privilege escalation;
- [ ] cross-tenant tests.

## Operação

- [ ] audit;
- [ ] metrics;
- [ ] tracing;
- [ ] feature flag;
- [ ] kill switch;
- [ ] rollback;
- [ ] runbook.

## Qualidade

- [ ] trajectory tests;
- [ ] outcome tests;
- [ ] security tests;
- [ ] simulation;
- [ ] adversarial evaluation.

## Lifecycle

- [ ] inventário;
- [ ] versionamento;
- [ ] release;
- [ ] revisão;
- [ ] reclassificação.

---

# 113. Documentos Relacionados

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
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 114. Princípios Finais

Agentes não devem receber autonomia apenas porque conseguem executar uma tarefa.

```text
Capability
≠
Permission
```

O princípio central é:

```text
Start with the least autonomy.

Grant explicit tools.

Enforce deterministic permissions.

Require humans for consequential actions.

Bound every execution.

Observe every effect.

Keep a kill switch.
```

No GereIgreja, a arquitetura — e não o modelo — deverá decidir o que um agente pode acessar, alterar, enviar, excluir ou executar.

---

# 115. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`14-Governanca-de-Agentes-Autonomia-e-Human-in-the-Loop.md`

**Documento**

`GAI-14`

**Código**

`GAI-AI-AGENT-AUTONOMY-HITL-GOVERNANCE`

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

`GAI-13 — Governança de Prompts, Modelos e Configurações de Inteligência Artificial`

**Próximo documento candidato**

`15-Gestao-de-Custos-Capacidade-e-FinOps-de-IA.md`
