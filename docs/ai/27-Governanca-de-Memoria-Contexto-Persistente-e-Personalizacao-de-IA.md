Pasta:

docs/ai/

Arquivo:

27-Governanca-de-Memoria-Contexto-Persistente-e-Personalizacao-de-IA.md

Documento:

GAI-27

Código:

GAI-AI-MEMORY-PERSISTENT-CONTEXT-PERSONALIZATION

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

# GAI-27 — Governança de Memória, Contexto Persistente e Personalização de Inteligência Artificial

> "Memória em IA não é apenas conveniência de produto. É persistência de contexto, dados e inferências que precisam de finalidade, isolamento, controle de acesso, retenção, correção e exclusão."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Conceito de Memória de IA
6. Memória de Sessão
7. Memória Persistente
8. Memória de Usuário
9. Memória de Tenant
10. Memória Organizacional
11. Contexto Efêmero
12. Contexto Persistente
13. Personalização
14. Preferências Explícitas
15. Preferências Inferidas
16. Perfil
17. Histórico
18. Finalidade
19. Necessidade
20. Minimização
21. Consentimento e Base Autorizada
22. Transparência
23. Controle do Usuário
24. Visualização
25. Correção
26. Exclusão
27. Desativação
28. Expiração
29. Retenção
30. TTL
31. Data Classification
32. Dados Pessoais
33. Dados Sensíveis
34. Secrets
35. Credenciais
36. Dados de Tenant
37. Tenant Isolation
38. Cross-Tenant Prevention
39. User Isolation
40. Shared Context
41. Context Assembly
42. Context Sources
43. Source Trust
44. Proveniência
45. Context Priority
46. Instruction Hierarchy
47. Prompt Injection
48. Memory Poisoning
49. Context Poisoning
50. Retrieval
51. Relevance
52. Staleness
53. Conflicts
54. Canonical Data
55. Derived Memory
56. Inferences
57. Confidence
58. Sensitive Inferences
59. Memory Write
60. Memory Read
61. Memory Update
62. Memory Delete
63. Authorization
64. Least Privilege
65. Service Accounts
66. Agents
67. Tools
68. Autonomous Memory Writes
69. Human Review
70. Audit Trail
71. Logging
72. Redaction
73. Encryption
74. Storage
75. Indexes
76. Vector Stores
77. Cache
78. Backups
79. Replication
80. Data Residency
81. Provider Boundaries
82. Third Parties
83. Model Context
84. Training versus Memory
85. Fine-Tuning versus Personalization
86. RAG versus Memory
87. Personalization Rules
88. User Experience
89. Recommendations
90. High-Impact Decisions
91. Bias
92. Discrimination
93. Manipulation
94. Over-Personalization
95. Filter Bubbles
96. Safety
97. Security Testing
98. Privacy Testing
99. Quality Testing
100. Memory Evaluation
101. Drift
102. Change Management
103. Incidents
104. Recovery
105. Decommission
106. Portability
107. Export
108. Audit
109. Evidence
110. Metrics
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

Este documento estabelece o padrão oficial para governança de memória, contexto persistente e personalização de capacidades de Inteligência Artificial no GereIgreja.

Seu objetivo é garantir que informações persistidas para melhorar continuidade, relevância ou personalização sejam tratadas como dados governados, com finalidade explícita, isolamento, autorização, transparência, retenção, correção e exclusão.

---

# 2. Escopo

Aplica-se a:

- memória de conversação;
- preferências persistentes;
- perfis de usuário;
- contexto por tenant;
- contexto organizacional;
- históricos resumidos;
- fatos derivados;
- personalização;
- stores de memória;
- índices vetoriais;
- caches persistentes;
- agentes com memória.

---

# 3. Relação com a Família GAI

```text
GAI-03
RAG / Context / Knowledge
        │
GAI-06
Security / Privacy
        │
GAI-07
Data Governance
        │
GAI-11
Risk Classification
        │
GAI-14
Agents / Autonomy
        │
GAI-18
Audit / Evidence
        │
GAI-24
Transparency
        │
        ▼
GAI-27
Memory / Persistent Context / Personalization
```

---

# 4. Princípios Fundamentais

Aplicar:

- memory by explicit purpose;
- minimum necessary persistence;
- tenant and user isolation;
- no secrets as memory;
- user control where applicable;
- provenance for derived context;
- expiration by design;
- authorization on read and write;
- safe personalization;
- deletion must propagate.

---

# 5. Conceito de Memória de IA

Memória de IA é informação preservada além da necessidade imediata de uma única inferência e reutilizada para influenciar interações ou ações futuras.

---

# 6. Memória de Sessão

Existe apenas durante o contexto operacional da sessão definida.

---

# 7. Memória Persistente

Sobrevive ao encerramento da sessão e exige governança de lifecycle.

---

# 8. Memória de Usuário

Informação associada a uma identidade de usuário específica.

---

# 9. Memória de Tenant

Informação persistida dentro do boundary de um tenant.

---

# 10. Memória Organizacional

Conhecimento persistente compartilhado deverá possuir regras de acesso próprias.

---

# 11. Contexto Efêmero

Contexto temporário não deverá ser persistido automaticamente.

---

# 12. Contexto Persistente

Persistência deverá ser uma decisão explícita.

---

# 13. Personalização

Personalização é adaptação do comportamento com base em preferências, histórico ou contexto autorizado.

---

# 14. Preferências Explícitas

Preferências fornecidas diretamente pelo usuário são preferíveis a inferências quando disponíveis.

---

# 15. Preferências Inferidas

Inferências deverão possuir finalidade e risco avaliados.

---

# 16. Perfil

Perfis não deverão acumular informação indefinidamente sem necessidade.

---

# 17. Histórico

Histórico bruto e memória útil são conceitos diferentes.

Preferir armazenar apenas o necessário.

---

# 18. Finalidade

Toda categoria de memória deverá possuir finalidade documentada.

---

# 19. Necessidade

Antes de persistir:

```text
Is persistence necessary?
Can session context solve it?
Can canonical data be queried instead?
What happens if this memory is wrong?
```

---

# 20. Minimização

Persistir o mínimo necessário para a finalidade.

---

# 21. Consentimento e Base Autorizada

Quando aplicável, persistência deverá possuir base adequada e comunicação compatível.

---

# 22. Transparência

Usuários deverão compreender personalização material quando relevante.

---

# 23. Controle do Usuário

Quando aplicável, permitir gerenciamento de memória ou personalização.

---

# 24. Visualização

Memórias relevantes poderão possuir interface ou mecanismo de consulta apropriado.

---

# 25. Correção

Informação incorreta deverá ser corrigível quando material.

---

# 26. Exclusão

Exclusão deverá remover ou tornar inacessível a memória conforme política aplicável.

---

# 27. Desativação

Usuários ou administradores poderão possuir opção de desativar personalização quando aplicável.

---

# 28. Expiração

Memórias deverão expirar quando deixarem de ser necessárias.

---

# 29. Retenção

Definir períodos por categoria.

---

# 30. TTL

Preferir TTL explícito para memória temporária.

Exemplo:

```text
session_summary_ttl = 30d
temporary_preference_ttl = 90d
```

---

# 31. Data Classification

Memória herda ou eleva a classificação dos dados que contém.

---

# 32. Dados Pessoais

Aplicar requisitos de privacidade.

---

# 33. Dados Sensíveis

Evitar persistência salvo necessidade demonstrável e controles reforçados.

---

# 34. Secrets

Secrets não deverão ser armazenados como memória de IA.

---

# 35. Credenciais

Credenciais deverão permanecer em sistemas próprios de secrets/IAM.

---

# 36. Dados de Tenant

Memória deverá preservar tenant_id ou boundary equivalente de forma estrutural.

---

# 37. Tenant Isolation

O isolamento deverá ser imposto no storage e na autorização.

---

# 38. Cross-Tenant Prevention

Nunca depender apenas do prompt:

```text
"Only use data from the current tenant."
```

---

# 39. User Isolation

Memória pessoal deverá respeitar identidade e autorização do usuário.

---

# 40. Shared Context

Contexto compartilhado deverá possuir escopo explícito.

---

# 41. Context Assembly

A composição do contexto deverá aplicar filtros antes de enviar dados ao modelo.

---

# 42. Context Sources

Exemplos:

- session;
- user memory;
- tenant memory;
- canonical database;
- RAG;
- system configuration.

---

# 43. Source Trust

Cada fonte deverá possuir nível de confiança apropriado.

---

# 44. Proveniência

Memórias derivadas deverão registrar origem quando material.

---

# 45. Context Priority

Conflitos deverão seguir regras determinísticas quando possível.

---

# 46. Instruction Hierarchy

Memória nunca deverá possuir autoridade superior a políticas e instruções de sistema.

---

# 47. Prompt Injection

Conteúdo armazenado deverá ser tratado como potencialmente não confiável.

---

# 48. Memory Poisoning

Testar tentativas de persistir instruções maliciosas como memória.

---

# 49. Context Poisoning

Evitar que dados não confiáveis alterem permanentemente comportamento.

---

# 50. Retrieval

Recuperação deverá respeitar escopo, identidade e finalidade.

---

# 51. Relevance

Não inserir toda memória disponível no contexto.

---

# 52. Staleness

Memórias antigas poderão se tornar incorretas.

---

# 53. Conflicts

Quando memória conflitar com dado canônico, preferir fonte definida como autoritativa.

---

# 54. Canonical Data

Dados transacionais críticos deverão permanecer em sistemas canônicos, não apenas na memória de IA.

---

# 55. Derived Memory

Informações resumidas ou inferidas deverão ser identificadas como derivadas.

---

# 56. Inferences

Inferências não deverão ser representadas como fatos confirmados.

---

# 57. Confidence

Quando utilizado, confidence deverá possuir significado validado.

---

# 58. Sensitive Inferences

Inferências sensíveis exigem controles reforçados e poderão ser proibidas conforme finalidade e política.

---

# 59. Memory Write

Toda gravação deverá passar por regras de elegibilidade.

---

# 60. Memory Read

Toda leitura deverá aplicar autorização e boundary.

---

# 61. Memory Update

Atualizações deverão preservar histórico quando necessário para auditoria sem manter dados além da retenção permitida.

---

# 62. Memory Delete

Deleção deverá possuir semântica clara e propagação adequada.

---

# 63. Authorization

Aplicar autorização no backend antes de recuperar memória.

---

# 64. Least Privilege

Serviços deverão acessar apenas stores necessários.

---

# 65. Service Accounts

Identidades técnicas deverão possuir escopo limitado.

---

# 66. Agents

Agentes com memória ampliam persistência e superfície de ataque.

---

# 67. Tools

Tools de memória deverão possuir contratos explícitos.

Exemplos:

```text
memory.read
memory.write
memory.update
memory.delete
```

---

# 68. Autonomous Memory Writes

Agentes não deverão persistir indiscriminadamente tudo que observam.

---

# 69. Human Review

Memórias de alto impacto poderão exigir confirmação antes de persistência.

---

# 70. Audit Trail

Registrar eventos relevantes de criação, alteração e exclusão.

---

# 71. Logging

Logs não deverão se transformar em memória paralela sem governança.

---

# 72. Redaction

Aplicar redaction antes de persistir conteúdo quando necessário.

---

# 73. Encryption

Aplicar criptografia conforme classificação.

---

# 74. Storage

Stores deverão ser aprovados para a classe de dados correspondente.

---

# 75. Indexes

Índices deverão preservar isolamento e lifecycle.

---

# 76. Vector Stores

Vetores e embeddings também podem representar informação sensível e deverão ser governados.

---

# 77. Cache

Caches persistentes deverão possuir TTL e invalidação.

---

# 78. Backups

Exclusão e retenção deverão considerar backups conforme política aplicável.

---

# 79. Replication

Replicação não deverá criar regiões ou cópias não autorizadas.

---

# 80. Data Residency

Aplicar requisitos de localização quando existentes.

---

# 81. Provider Boundaries

Memória enviada a providers deverá seguir GAI-16.

---

# 82. Third Parties

Terceiros não deverão receber contexto persistente além do necessário.

---

# 83. Model Context

Contexto enviado ao modelo deverá ser minimizado.

---

# 84. Training versus Memory

Memória não deverá ser reutilizada para treinamento automaticamente.

```text
Memory authorization
≠
Training authorization
```

---

# 85. Fine-Tuning versus Personalização

Fine-tuning altera artefato/modelo; personalização altera contexto ou comportamento por identidade.

---

# 86. RAG versus Memory

RAG recupera conhecimento; memória preserva contexto ou preferências. Um sistema poderá utilizar ambos, mas com governança distinta.

---

# 87. Personalization Rules

Regras deverão especificar quais atributos podem influenciar comportamento.

---

# 88. User Experience

Personalização deverá melhorar relevância sem criar surpresa indevida.

---

# 89. Recommendations

Recomendações personalizadas deverão preservar limites e transparência aplicáveis.

---

# 90. High-Impact Decisions

Memória ou perfil não deverá produzir automaticamente decisão de alto impacto sem governança proporcional.

---

# 91. Bias

Avaliar se personalização reforça vieses indesejados.

---

# 92. Discrimination

Não utilizar atributos ou inferências de forma incompatível com políticas e requisitos aplicáveis.

---

# 93. Manipulação

Personalização não deverá explorar vulnerabilidades do usuário.

---

# 94. Over-Personalization

Evitar adaptação excessiva que reduza previsibilidade ou controle.

---

# 95. Filter Bubbles

Quando relevante, avaliar efeitos de repetição e estreitamento de recomendações.

---

# 96. Safety

Aplicar GAI-06 e GAI-22.

---

# 97. Security Testing

Aplicar GAI-26 para poisoning, leakage, authorization e cross-tenant.

---

# 98. Privacy Testing

Validar exclusão, minimização, isolamento e retenção.

---

# 99. Quality Testing

Testar relevância, correção e staleness.

---

# 100. Memory Evaluation

Métricas possíveis:

```text
memory_precision
memory_relevance
memory_staleness_rate
memory_correction_rate
memory_delete_success_rate
```

---

# 101. Drift

Mudanças de comportamento de personalização deverão ser monitoradas.

---

# 102. Change Management

Mudanças materiais deverão seguir GAI-23.

---

# 103. Incidents

Vazamento, poisoning ou persistência indevida deverão seguir GAI-17.

---

# 104. Recovery

Planos deverão considerar corrupção ou indisponibilidade do store de memória.

---

# 105. Decommission

Aplicar GAI-19.

---

# 106. Portability

Quando aplicável, definir como preferências ou memórias podem ser exportadas.

---

# 107. Export

Exportações deverão aplicar autorização e minimização.

---

# 108. Audit

Controles de memória deverão ser auditáveis.

---

# 109. Evidence

Preservar evidências conforme GAI-18.

---

# 110. Metrics

Exemplos:

```text
ai_memory_records
ai_memory_writes
ai_memory_deletes
ai_memory_expired
ai_memory_stale_findings
ai_memory_poisoning_attempts
ai_cross_tenant_memory_denials
ai_memory_privacy_findings
ai_personalization_opt_out_rate
```

---

# 111. Production Readiness

Antes de habilitar memória persistente:

```text
purpose?
owner?
data classes?
tenant isolation?
user isolation?
write authorization?
read authorization?
TTL?
retention?
delete path?
correction path?
poisoning protection?
audit trail?
provider boundary?
incident response?
```

---

# 112. Templates

## AI Memory Store Record

```text
Memory Store ID:
Name:
Owner:

Purpose:
Scope:
- Session
- User
- Tenant
- Organization

Storage:
Region:
Provider:

Data Classes:
Personal Data:
Sensitive Data:
Tenant Data:

Write Rules:
Read Rules:
Update Rules:
Delete Rules:

TTL:
Retention:
Backup Policy:

Encryption:
Access Control:
Audit Logging:

Poisoning Controls:
Redaction:
Review Date:
Status:
```

## AI Memory Item Schema

```text
Memory ID:
Tenant ID:
User ID:
Scope:

Type:
Value / Reference:
Source:
Source Timestamp:

Derived:
Confidence:
Sensitivity:

Created At:
Updated At:
Expires At:

Created By:
Last Updated By:

Status:
```

## AI Personalization Assessment

```text
Use Case:
Owner:
Risk Level:

Personalization Purpose:
Attributes Used:
Explicit Preferences:
Inferred Preferences:

Memory Sources:
Canonical Sources:

User Disclosure:
User Controls:
Opt-Out:
Correction:
Deletion:

Bias Review:
Manipulation Review:
Privacy Review:
Security Review:

Approval:
Last Review:
```

---

# 113. Anti-Padrões

Evitar:

```text
store every conversation forever
just in case
```

---

```text
memory
=
full raw chat history
```

---

```text
tenant isolation
implemented only in prompt
```

---

```text
API key
saved as useful memory
```

---

```text
model inference
stored as confirmed fact
```

---

```text
deleted memory
still present in active vector index
```

---

```text
agent decides
what to remember forever
without policy
```

---

```text
user preference
silently reused for unrelated purpose
```

---

```text
memory data
automatically reused for training
```

---

# 114. Arquitetura Consolidada

```text
                       USER / TENANT
                            │
                            ▼
                       AUTHORIZATION
                            │
                            ▼
                     CONTEXT ASSEMBLER
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
           SESSION         MEMORY         RAG
              │             │             │
              │      ┌──────┴──────┐      │
              │      ▼             ▼      │
              │    USER          TENANT   │
              │      │             │      │
              └──────┴──────┬──────┴──────┘
                            ▼
                      POLICY FILTER
                            │
                            ▼
                          MODEL
                            │
                            ▼
                         OUTPUT
                            │
                            ▼
                    MEMORY WRITE GATE
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
                ALLOW                DENY
                  │
                  ▼
              VERSION / TTL
                  │
                  ▼
                 AUDIT
```

---

# 115. Checklist

## Finalidade

- [ ] owner;
- [ ] purpose;
- [ ] scope;
- [ ] risk classification;
- [ ] persistence necessary.

## Dados

- [ ] classification;
- [ ] minimization;
- [ ] personal data review;
- [ ] sensitive data review;
- [ ] no secrets;
- [ ] provenance.

## Isolamento

- [ ] tenant boundary;
- [ ] user boundary;
- [ ] shared context rules;
- [ ] authorization on read;
- [ ] authorization on write.

## Lifecycle

- [ ] TTL;
- [ ] retention;
- [ ] correction;
- [ ] deletion;
- [ ] backup behavior;
- [ ] decommission.

## Segurança

- [ ] prompt injection;
- [ ] memory poisoning;
- [ ] context poisoning;
- [ ] cross-tenant tests;
- [ ] encryption;
- [ ] least privilege.

## Personalização

- [ ] explicit versus inferred;
- [ ] transparency;
- [ ] user control;
- [ ] opt-out when applicable;
- [ ] bias review;
- [ ] manipulation review.

## Operação

- [ ] logging;
- [ ] audit trail;
- [ ] metrics;
- [ ] incident response;
- [ ] recovery;
- [ ] periodic review.

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
- GAI-20 — Maturidade, KPIs e Roadmap de Governança de Inteligência Artificial
- GAI-21 — Responsabilidades, Papéis e Modelo Operacional de Inteligência Artificial
- GAI-22 — Política de Uso Aceitável e Práticas Proibidas de Inteligência Artificial
- GAI-23 — Gestão de Mudanças e Exceções de Inteligência Artificial
- GAI-24 — Transparência, Explicabilidade e Comunicação de Inteligência Artificial
- GAI-25 — Governança de Datasets Sintéticos, Fine-Tuning e Customização de Modelos
- GAI-26 — Red Teaming, Adversarial Testing e Segurança Ofensiva de Inteligência Artificial
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 117. Princípios Finais

Memória torna a IA mais útil, mas também torna seus efeitos mais persistentes.

```text
Useful Context
+
Persistence
=
Governed Data
```

O princípio central é:

```text
Remember only with purpose.

Store only what is necessary.

Isolate by tenant and user.

Treat memory as untrusted context.

Allow correction and deletion.

Expire what is no longer needed.

Never turn memory into training data implicitly.
```

No GereIgreja, memória e personalização deverão aumentar continuidade e relevância sem reduzir privacidade, segurança, isolamento, previsibilidade ou controle dos usuários.

---

# 118. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`27-Governanca-de-Memoria-Contexto-Persistente-e-Personalizacao-de-IA.md`

**Documento**

`GAI-27`

**Código**

`GAI-AI-MEMORY-PERSISTENT-CONTEXT-PERSONALIZATION`

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

`GAI-26 — Red Teaming, Adversarial Testing e Segurança Ofensiva de Inteligência Artificial`

**Próximo documento candidato**

`28-Governanca-de-Model-Routing-Fallback-e-Resiliencia-Multi-Provider-de-IA.md`
