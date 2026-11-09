Pasta:

docs/ai/

Arquivo:

17-Gestao-de-Incidentes-Continuidade-e-Recuperacao-de-IA.md

Documento:

GAI-17

Código:

GAI-AI-INCIDENT-CONTINUITY-RECOVERY

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

# GAI-17 — Gestão de Incidentes, Continuidade e Recuperação de Inteligência Artificial

> "Uma capacidade de IA só está pronta para produção quando a organização sabe como detectar sua falha, conter seus efeitos, operar sem ela e recuperá-la com segurança."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Conceito de Incidente de IA
6. Categorias de Incidentes
7. Incidentes de Segurança
8. Incidentes de Privacidade
9. Incidentes de Isolamento de Tenant
10. Incidentes de Provider
11. Incidentes de Modelo
12. Incidentes de Prompt
13. Incidentes de RAG
14. Incidentes de Tool
15. Incidentes de Agente
16. Incidentes de Dados
17. Incidentes de Custo
18. Incidentes de Qualidade
19. Incidentes de Disponibilidade
20. Incidentes de Compliance
21. Severidade
22. SEV-1
23. SEV-2
24. SEV-3
25. SEV-4
26. Critérios de Elevação
27. Detecção
28. Alertas
29. Observabilidade
30. Sinais de Incidente
31. Triagem
32. Incident Commander
33. Technical Lead
34. Security Lead
35. Privacy / Compliance
36. Communications
37. Owner da Feature
38. Contenção
39. Kill Switch
40. Feature Flag
41. Desativação de Agente
42. Desativação de Tool
43. Desativação de Provider
44. Desativação de Modelo
45. Desativação de Prompt
46. Bloqueio de Tenant
47. Revogação de Credenciais
48. Rate Limiting Emergencial
49. Quotas Emergenciais
50. Preservação de Evidências
51. Logs
52. Traces
53. Audit Events
54. Configuração Ativa
55. Prompt Version
56. Model Version
57. Provider
58. Dados Afetados
59. Timeline
60. Investigação
61. Root Cause Analysis
62. Blast Radius
63. Impact Analysis
64. Cross-Tenant Analysis
65. Data Exposure Analysis
66. Cost Exposure Analysis
67. Recovery
68. Recovery Criteria
69. Validation
70. Safe Re-enable
71. Canary Recovery
72. Rollback
73. Fallback
74. Degradação
75. Continuidade
76. Business Continuity
77. AI Dependency Mapping
78. Criticality
79. RTO
80. RPO
81. Operação sem IA
82. Manual Fallback
83. Deterministic Fallback
84. Provider Outage
85. Model Retirement
86. Vector Store Failure
87. Knowledge Base Failure
88. Queue Failure
89. Agent Runtime Failure
90. Tool Dependency Failure
91. Disaster Recovery
92. Backup
93. Restore
94. Reindexação
95. Re-embedding
96. Rebuild
97. Recovery Testing
98. Game Days
99. Tabletop Exercises
100. Chaos Testing
101. Comunicação de Incidentes
102. Comunicação Interna
103. Comunicação Externa
104. Notificação
105. LGPD e Obrigações
106. Provider Notification
107. Customer Impact
108. Post-Incident Review
109. Corrective Actions
110. Preventive Actions
111. Follow-up
112. Lessons Learned
113. Runbooks
114. Playbooks
115. Inventário
116. Auditoria
117. Métricas
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

Este documento estabelece o padrão oficial para identificação, resposta, contenção, recuperação e continuidade diante de incidentes envolvendo capacidades de Inteligência Artificial no GereIgreja.

O objetivo é integrar workloads de IA aos processos operacionais e de segurança da plataforma, considerando riscos específicos de modelos, providers, RAG, tools e agentes.

---

# 2. Escopo

Aplica-se a incidentes relacionados a:

- modelos;
- providers;
- prompts;
- RAG;
- embeddings;
- vector stores;
- tools;
- agentes;
- dados;
- privacidade;
- segurança;
- qualidade;
- custos;
- disponibilidade;
- integrações de IA.

---

# 3. Relação com a Família GAI

```text
GAI-05
Observability / Operations
        │
GAI-06
Security / Privacy
        │
GAI-09
Release / Lifecycle
        │
GAI-12
Asset Registry
        │
GAI-14
Agents / Kill Switch
        │
GAI-16
Provider Risk
        │
        ▼
GAI-17
Incident / Continuity / Recovery
```

---

# 4. Princípios Fundamentais

Aplicar:

- detect early;
- contain first;
- preserve evidence;
- know the blast radius;
- degrade safely;
- recover deliberately;
- validate before re-enable;
- maintain non-AI continuity where critical;
- learn from incidents;
- prevent recurrence.

---

# 5. Conceito de Incidente de IA

Incidente de IA é evento que comprometa ou ameace:

- confidencialidade;
- integridade;
- disponibilidade;
- privacidade;
- isolamento;
- qualidade;
- custo;
- conformidade;
- controle de ações.

---

# 6. Categorias de Incidentes

Categorias sugeridas:

```text
AI-SEC
AI-PRIV
AI-TENANT
AI-PROVIDER
AI-MODEL
AI-PROMPT
AI-RAG
AI-TOOL
AI-AGENT
AI-DATA
AI-COST
AI-QUALITY
AI-AVAILABILITY
AI-COMPLIANCE
```

---

# 7. Incidentes de Segurança

Exemplos:

- uso indevido de tools;
- credencial comprometida;
- exfiltração;
- escalada de privilégio;
- prompt injection com efeito real.

---

# 8. Incidentes de Privacidade

Exemplos:

- envio indevido de dados pessoais;
- retenção incompatível;
- exposição de informação protegida.

---

# 9. Incidentes de Isolamento de Tenant

Qualquer possibilidade material de cross-tenant leakage deverá receber prioridade elevada.

---

# 10. Incidentes de Provider

Exemplos:

- indisponibilidade;
- degradação;
- incidente de segurança externo;
- alteração inesperada de política.

---

# 11. Incidentes de Modelo

Exemplos:

- regressão severa;
- mudança inesperada de comportamento;
- indisponibilidade;
- retirada de versão.

---

# 12. Incidentes de Prompt

Exemplos:

- versão incorreta;
- instrução insegura;
- regressão em produção.

---

# 13. Incidentes de RAG

Exemplos:

- retrieval cross-tenant;
- fonte incorreta;
- índice desatualizado;
- perda de proveniência.

---

# 14. Incidentes de Tool

Exemplos:

- execução não autorizada;
- parâmetros incorretos;
- side effect inesperado.

---

# 15. Incidentes de Agente

Exemplos:

- loop;
- runaway cost;
- tool chaining inseguro;
- execução além da autonomia concedida.

---

# 16. Incidentes de Dados

Exemplos:

- dataset incorreto;
- ingestão indevida;
- corrupção de embeddings;
- retenção excedida.

---

# 17. Incidentes de Custo

Exemplos:

- spike anormal;
- retry storm;
- agent loop;
- abuso de quota.

---

# 18. Incidentes de Qualidade

Qualidade torna-se incidente quando produz impacto operacional ou material relevante.

---

# 19. Incidentes de Disponibilidade

Falha de IA não deverá necessariamente derrubar funcionalidades centrais não dependentes dela.

---

# 20. Incidentes de Compliance

Qualquer possível descumprimento relevante deverá ser escalado conforme processos oficiais.

---

# 21. Severidade

Classificação sugerida:

```text
SEV-1 — Crítico
SEV-2 — Alto
SEV-3 — Moderado
SEV-4 — Baixo
```

---

# 22. SEV-1

Exemplos:

- cross-tenant exposure confirmado em escala;
- ação privilegiada indevida com impacto crítico;
- exposição significativa de dados sensíveis;
- comprometimento amplo de provider/credenciais.

Exige contenção imediata.

---

# 23. SEV-2

Exemplos:

- indisponibilidade relevante;
- tool mutável executando incorretamente;
- degradação severa com impacto material;
- risco de privacidade limitado mas relevante.

---

# 24. SEV-3

Impacto limitado, controlável e sem exposição crítica.

---

# 25. SEV-4

Falha menor sem impacto significativo.

---

# 26. Critérios de Elevação

Elevar severidade quando houver:

- dados sensíveis;
- múltiplos tenants;
- ação irreversível;
- privilégio;
- alcance elevado;
- obrigação legal;
- ausência de contenção.

---

# 27. Detecção

Incidentes poderão ser detectados por:

- métricas;
- alertas;
- logs;
- auditoria;
- usuários;
- suporte;
- providers;
- avaliações contínuas.

---

# 28. Alertas

Alertas deverão ser acionáveis.

---

# 29. Observabilidade

Aplicar GAI-05.

---

# 30. Sinais de Incidente

Exemplos:

```text
cross_tenant_denial spike
tool_denied spike
provider_errors spike
agent_steps anomaly
cost anomaly
quality regression
unexpected model change
```

---

# 31. Triagem

Fluxo:

```text
Detect
  ↓
Validate Signal
  ↓
Classify
  ↓
Assign Severity
  ↓
Contain
  ↓
Investigate
```

---

# 32. Incident Commander

Incidentes relevantes deverão possuir responsável pela coordenação.

---

# 33. Technical Lead

Coordena investigação técnica.

---

# 34. Security Lead

Participa quando houver risco de segurança.

---

# 35. Privacy / Compliance

Participa quando houver dados pessoais ou obrigações regulatórias.

---

# 36. Communications

Coordena comunicação quando necessária.

---

# 37. Owner da Feature

Deverá participar da análise do comportamento esperado.

---

# 38. Contenção

A prioridade inicial é impedir expansão do impacto.

---

# 39. Kill Switch

Mecanismos de kill switch deverão ser conhecidos previamente.

---

# 40. Feature Flag

Pode desativar capacidade afetada.

---

# 41. Desativação de Agente

Agentes deverão poder ser interrompidos.

---

# 42. Desativação de Tool

Uma tool comprometida poderá ser removida da allowlist sem desligar todo o sistema.

---

# 43. Desativação de Provider

AI Gateway deverá permitir bloquear provider quando necessário.

---

# 44. Desativação de Modelo

Model alias poderá ser redirecionado ou desabilitado conforme política aprovada.

---

# 45. Desativação de Prompt

Versão insegura deverá poder sofrer rollback.

---

# 46. Bloqueio de Tenant

Poderá ser necessário conter apenas tenant afetado.

---

# 47. Revogação de Credenciais

Credenciais comprometidas deverão ser revogadas imediatamente.

---

# 48. Rate Limiting Emergencial

Poderá reduzir blast radius.

---

# 49. Quotas Emergenciais

Poderão conter custos ou abuso.

---

# 50. Preservação de Evidências

Antes de apagar dados relevantes, preservar evidências necessárias conforme política.

---

# 51. Logs

Preservar logs operacionais relevantes.

---

# 52. Traces

Traces poderão ajudar a reconstruir fluxos multi-step.

---

# 53. Audit Events

Ações mutáveis deverão possuir eventos de auditoria.

---

# 54. Configuração Ativa

Registrar configuração vigente durante o incidente.

---

# 55. Prompt Version

Identificar versão exata.

---

# 56. Model Version

Identificar alias e modelo concreto.

---

# 57. Provider

Identificar provider e região quando aplicável.

---

# 58. Dados Afetados

Classificar dados potencialmente envolvidos.

---

# 59. Timeline

Construir linha do tempo.

---

# 60. Investigação

Separar fatos, hipóteses e conclusões.

---

# 61. Root Cause Analysis

Buscar causa sistêmica, não apenas erro imediato.

---

# 62. Blast Radius

Determinar:

```text
users
tenants
records
requests
providers
agents
tools
time window
```

---

# 63. Impact Analysis

Avaliar efeitos técnicos e de negócio.

---

# 64. Cross-Tenant Analysis

Sempre executar quando houver suspeita de falha de isolamento.

---

# 65. Data Exposure Analysis

Determinar categorias e volume de dados.

---

# 66. Cost Exposure Analysis

Determinar consumo financeiro anormal.

---

# 67. Recovery

Recuperação deverá ocorrer somente após contenção suficiente.

---

# 68. Recovery Criteria

Definir critérios objetivos.

---

# 69. Validation

Antes de reativar:

- testes;
- avaliações;
- security checks;
- configuração;
- monitoramento.

---

# 70. Safe Re-enable

Preferir reativação gradual.

---

# 71. Canary Recovery

Reativar inicialmente para pequena parcela quando possível.

---

# 72. Rollback

Utilizar versão previamente conhecida como segura.

---

# 73. Fallback

Fallback deverá estar aprovado.

---

# 74. Degradação

Se necessário, operar com menor capacidade de IA.

---

# 75. Continuidade

Capacidades críticas deverão possuir estratégia para indisponibilidade de IA.

---

# 76. Business Continuity

IA deverá integrar planejamento geral de continuidade.

---

# 77. AI Dependency Mapping

Utilizar GAI-12 para identificar dependências.

---

# 78. Criticality

Classificar quais features realmente dependem de IA para operar.

---

# 79. RTO

Definir Recovery Time Objective quando aplicável.

---

# 80. RPO

Definir Recovery Point Objective para dados persistidos relacionados à IA quando aplicável.

---

# 81. Operação sem IA

Quando possível, funcionalidades essenciais deverão possuir modo não-IA.

---

# 82. Manual Fallback

Alguns processos poderão retornar temporariamente a operação humana.

---

# 83. Deterministic Fallback

Preferir regras determinísticas para funções essenciais quando adequadas.

---

# 84. Provider Outage

Estratégias:

```text
retry bounded
approved fallback
queue
degrade
disable
```

---

# 85. Model Retirement

Manter plano de migração conforme GAI-16.

---

# 86. Vector Store Failure

Definir:

- restore;
- rebuild;
- reindex;
- fallback sem RAG.

---

# 87. Knowledge Base Failure

Evitar responder com falsa confiança quando contexto autorizado não estiver disponível.

---

# 88. Queue Failure

Jobs deverão possuir políticas de retry, dead-letter e recuperação.

---

# 89. Agent Runtime Failure

Deverá preservar estado suficiente para auditoria sem executar efeitos duplicados.

---

# 90. Tool Dependency Failure

Falha de tool deverá terminar ou degradar o fluxo com segurança.

---

# 91. Disaster Recovery

Workloads críticos de IA deverão estar incluídos no DR da plataforma.

---

# 92. Backup

Aplicar backup aos dados que realmente precisam ser persistidos.

---

# 93. Restore

Restore deverá ser testado.

---

# 94. Reindexação

Bases RAG deverão possuir processo documentado de reindexação.

---

# 95. Re-embedding

Mudança ou corrupção de embeddings poderá exigir regeneração controlada.

---

# 96. Rebuild

Artefatos derivados deverão ser reconstruíveis a partir da fonte quando possível.

---

# 97. Recovery Testing

Não confiar em plano nunca testado.

---

# 98. Game Days

Simular falhas de providers e componentes críticos.

---

# 99. Tabletop Exercises

Simular cenários de:

- cross-tenant leak;
- provider breach;
- runaway agent;
- cost spike;
- destructive tool misuse.

---

# 100. Chaos Testing

Aplicar de forma controlada quando maturidade permitir.

---

# 101. Comunicação de Incidentes

Comunicação deverá ser factual, proporcional e coordenada.

---

# 102. Comunicação Interna

Informar equipes necessárias sem espalhar dados sensíveis.

---

# 103. Comunicação Externa

Somente quando necessária e por processo autorizado.

---

# 104. Notificação

Obrigações de notificação deverão seguir requisitos jurídicos e contratuais aplicáveis.

---

# 105. LGPD e Obrigações

Incidentes envolvendo dados pessoais deverão acionar o processo oficial de privacidade e segurança.

---

# 106. Provider Notification

Notificar provider quando necessário para investigação ou contenção.

---

# 107. Customer Impact

Determinar impacto real antes de conclusões públicas.

---

# 108. Post-Incident Review

Incidentes relevantes deverão possuir revisão pós-incidente.

---

# 109. Corrective Actions

Ações corretivas resolvem a causa ou efeito identificado.

---

# 110. Preventive Actions

Ações preventivas reduzem recorrência.

---

# 111. Follow-up

Toda ação deverá possuir owner e prazo.

---

# 112. Lessons Learned

Lições deverão atualizar:

- código;
- arquitetura;
- prompts;
- policies;
- tests;
- runbooks;
- documentação.

---

# 113. Runbooks

Runbooks deverão existir para cenários previsíveis.

---

# 114. Playbooks

Playbooks recomendados:

```text
provider outage
model regression
prompt rollback
RAG isolation incident
agent runaway
tool misuse
cost spike
credential compromise
```

---

# 115. Inventário

GAI-12 deverá permitir localizar rapidamente ativos afetados.

---

# 116. Auditoria

Preservar rastreabilidade de decisões e ações de resposta.

---

# 117. Métricas

Exemplos:

```text
ai_incidents_total
ai_incidents_by_severity
ai_incident_mttd
ai_incident_mttr
ai_kill_switch_activations
ai_provider_incidents
ai_agent_incidents
ai_cross_tenant_incidents
ai_recovery_failures
```

---

# 118. Production Readiness

Antes de production:

```text
alerts?
owner?
runbook?
kill switch?
fallback?
degradation?
dependency map?
RTO/RPO if needed?
recovery tested?
incident contacts?
```

---

# 119. Templates

## AI Incident Record

```text
Incident ID:
Title:
Category:
Severity:
Status:

Detected At:
Contained At:
Recovered At:

Incident Commander:
Technical Lead:
Feature Owner:

Affected Use Cases:
Affected Assets:
Affected Tenants:
Affected Users:

Provider:
Model:
Prompt Version:
Agent:
Tools:

Data Classes:
Potential Exposure:

Impact:
Blast Radius:

Containment:
Root Cause:
Recovery:

Corrective Actions:
Preventive Actions:

Notifications:
Evidence:
Post-Incident Review:
```

## AI Continuity Record

```text
Feature:
Owner:
Criticality:

AI Dependencies:
Provider:
Model:
RAG:
Vector Store:
Agent:
Tools:

RTO:
RPO:

Non-AI Mode:
Fallback:
Manual Procedure:

Kill Switch:
Recovery Procedure:
Validation Procedure:

Last Test:
Next Test:
```

---

# 120. Anti-Padrões

Evitar:

```text
AI failure
→ entire platform unavailable
```

---

```text
incident response
starts by deleting logs
```

---

```text
provider outage
→ infinite retries
```

---

```text
unsafe agent
without kill switch
```

---

```text
cross-tenant suspicion
treated as normal bug
```

---

```text
re-enable
without validation
```

---

```text
fallback provider
never evaluated
```

---

```text
DR plan
without restore test
```

---

```text
postmortem
without owners for actions
```

---

# 121. Arquitetura Consolidada

```text
                      AI PRODUCTION
                           │
                           ▼
                     OBSERVABILITY
                           │
                           ▼
                        DETECTION
                           │
                           ▼
                         TRIAGE
                           │
                           ▼
                       SEVERITY
                           │
                           ▼
                      CONTAINMENT
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
     KILL SWITCH        ROLLBACK         REVOKE
         │                 │                 │
         └─────────────────┼─────────────────┘
                           ▼
                     INVESTIGATION
                           │
                           ▼
                     BLAST RADIUS
                           │
                           ▼
                       RECOVERY
                           │
                           ▼
                       VALIDATION
                           │
                           ▼
                    SAFE RE-ENABLE
                           │
                           ▼
                 POST-INCIDENT REVIEW
                           │
                           ▼
                  PREVENT RECURRENCE
```

---

# 122. Checklist

## Preparação

- [ ] owner;
- [ ] contatos;
- [ ] dependency map;
- [ ] runbooks;
- [ ] playbooks;
- [ ] kill switches;
- [ ] fallback;
- [ ] RTO/RPO quando aplicável.

## Detecção

- [ ] logs;
- [ ] metrics;
- [ ] alerts;
- [ ] traces;
- [ ] audit events;
- [ ] anomaly detection.

## Contenção

- [ ] feature disable;
- [ ] agent disable;
- [ ] tool disable;
- [ ] provider disable;
- [ ] credential revoke;
- [ ] emergency rate limits.

## Investigação

- [ ] evidence preserved;
- [ ] timeline;
- [ ] configuration;
- [ ] prompt version;
- [ ] model;
- [ ] provider;
- [ ] blast radius;
- [ ] data exposure;
- [ ] cross-tenant analysis.

## Recuperação

- [ ] root cause understood;
- [ ] fix validated;
- [ ] rollback/fallback;
- [ ] canary;
- [ ] monitoring reinforced;
- [ ] safe re-enable.

## Continuidade

- [ ] non-AI mode;
- [ ] manual fallback;
- [ ] approved provider fallback;
- [ ] backup;
- [ ] restore;
- [ ] reindex/rebuild;
- [ ] recovery tests.

## Pós-Incidente

- [ ] review;
- [ ] corrective actions;
- [ ] preventive actions;
- [ ] owners;
- [ ] deadlines;
- [ ] documentation updated;
- [ ] tests updated.

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
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 124. Princípios Finais

Incidentes de IA deverão ser tratados como problemas operacionais reais, não como simples respostas ruins de um modelo.

```text
Detect
→ Contain
→ Investigate
→ Recover
→ Validate
→ Learn
```

O princípio central é:

```text
Know how to stop it.

Know how to operate without it.

Know how to recover it.

Know how to prove it is safe again.
```

No GereIgreja, nenhuma capacidade crítica de IA deverá ser uma dependência sem mecanismo de contenção, continuidade e recuperação.

---

# 125. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`17-Gestao-de-Incidentes-Continuidade-e-Recuperacao-de-IA.md`

**Documento**

`GAI-17`

**Código**

`GAI-AI-INCIDENT-CONTINUITY-RECOVERY`

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

`GAI-16 — Gestão de Riscos de Terceiros e Providers de Inteligência Artificial`

**Próximo documento candidato**

`18-Auditoria-Evidencias-e-Conformidade-de-IA.md`
