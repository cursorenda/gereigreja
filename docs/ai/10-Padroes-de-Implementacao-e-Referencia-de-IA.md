Pasta:

docs/ai/

Arquivo:

10-Padroes-de-Implementacao-e-Referencia-de-IA.md

Documento:

GAI-10

Código:

GAI-AI-IMPLEMENTATION-REFERENCE-PATTERNS

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

# GAI-10 — Padrões de Implementação e Referência de Inteligência Artificial

> "A arquitetura de IA só se torna consistente quando suas regras podem ser traduzidas em padrões de implementação repetíveis."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Arquitetura de Referência
6. Camadas
7. AI Feature
8. Application Service
9. AI Orchestrator
10. AI Gateway
11. Provider Adapter
12. Model Registry
13. Prompt Registry
14. Context Builder
15. RAG Service
16. Tool Registry
17. Agent Runtime
18. Guardrails
19. Evaluation Layer
20. Observability Layer
21. Data Governance
22. Tenant Context
23. Authorization Context
24. Request Context
25. Correlation ID
26. Contratos
27. DTOs
28. Schemas
29. Structured Output
30. Erros
31. Timeouts
32. Retries
33. Fallback
34. Circuit Breaker
35. Rate Limiting
36. Quotas
37. Budgets
38. Caching
39. Idempotência
40. Feature Flags
41. Padrão de Chamada Simples
42. Padrão de Structured Generation
43. Padrão de Classificação
44. Padrão de Resumo
45. Padrão de RAG
46. Padrão de RAG com Citações
47. Padrão de Tool Calling
48. Padrão de Ação Preparada
49. Padrão de Ação Confirmada
50. Padrão de Agente Multi-Step
51. Padrão de Job Assíncrono
52. Padrão de Batch
53. Padrão de Fallback
54. Padrão de Degradação
55. Padrão de Cache
56. Padrão de Auditoria
57. Padrão de Observabilidade
58. Padrão de Avaliação
59. Padrão de Tenant Isolation
60. Padrão de Minimização
61. Padrão de Provider Isolation
62. Padrão de Prompt Versioning
63. Padrão de Model Routing
64. Padrão de Kill Switch
65. Organização de Código
66. Interfaces de Referência
67. AI Gateway Interface
68. Provider Adapter Interface
69. Prompt Interface
70. Retrieval Interface
71. Tool Interface
72. Agent Interface
73. Evaluation Interface
74. Convenções de Nomenclatura
75. Configuração
76. Secrets
77. Persistência
78. Banco Relacional
79. Vector Store
80. Cache
81. Filas
82. Arquivos
83. Segurança
84. Privacidade
85. Logs
86. Métricas
87. Tracing
88. Testes
89. CI/CD
90. Deploy
91. Exemplos de Fluxo
92. Anti-Padrões
93. Decision Matrix
94. Production Readiness
95. Checklist
96. Documentos Relacionados
97. Princípios Finais
98. Status do Documento

---

# 1. Objetivo

Este documento estabelece padrões de implementação e arquiteturas de referência para capacidades de Inteligência Artificial no GereIgreja.

Ele transforma as normas GAI-01 a GAI-09 em estruturas técnicas reutilizáveis.

Não define uma biblioteca específica obrigatória.

Define fronteiras, responsabilidades e fluxos que as implementações deverão preservar.

---

# 2. Escopo

Aplica-se à implementação de:

- chamadas simples a modelos;
- geração estruturada;
- classificação;
- sumarização;
- RAG;
- embeddings;
- tool calling;
- agentes;
- jobs de IA;
- avaliações;
- integrações com providers.

---

# 3. Relação com a Família GAI

```text
GAI-01 ... GAI-09
Normas e Controles
       │
       ▼
     GAI-10
Implementation Patterns
       │
       ▼
Application Code
```

GAI-10 não reduz requisitos anteriores.

Ele demonstra como organizá-los.

---

# 4. Princípios Fundamentais

Aplicar:

- provider isolation;
- explicit contracts;
- deterministic security;
- tenant-aware design;
- reusable services;
- structured outputs;
- bounded execution;
- observability by default;
- testability;
- configuration versioning.

---

# 5. Arquitetura de Referência

```text
                         USER / API
                             │
                             ▼
                    APPLICATION LAYER
                             │
                             ▼
                      AI ORCHESTRATOR
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
  CONTEXT BUILDER        AI GATEWAY          TOOL REGISTRY
        │                    │                    │
        ▼                    ▼                    ▼
       RAG             PROVIDER ADAPTER      DOMAIN SERVICES
        │                    │                    │
        └────────────────────┼────────────────────┘
                             ▼
                         AI RESULT
                             │
                             ▼
                  VALIDATION / GUARDRAILS
                             │
                             ▼
                       APPLICATION
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
           AUDIT          METRICS         TRACES
```

---

# 6. Camadas

Responsabilidades deverão permanecer separadas.

```text
Presentation
Application
AI Orchestration
AI Infrastructure
Domain
Persistence
```

---

# 7. AI Feature

A feature conhece a necessidade do produto.

Ela não deverá conhecer detalhes específicos de SDK do provider.

---

# 8. Application Service

Coordena regra de negócio e autorização.

---

# 9. AI Orchestrator

Coordena componentes de IA para um caso de uso.

Exemplo:

```text
Build Context
→ Select Prompt
→ Call Gateway
→ Validate
→ Return Result
```

---

# 10. AI Gateway

Centraliza acesso a modelos.

Responsabilidades possíveis:

- provider routing;
- model selection;
- timeout;
- retry;
- telemetry;
- cost metadata;
- error normalization.

---

# 11. Provider Adapter

Isola SDK e API específicos.

```text
Application
→ AI Gateway
→ Adapter
→ Provider
```

---

# 12. Model Registry

Mantém configuração aprovada de modelos.

Exemplo conceitual:

```text
model_alias: fast_text
provider: provider_x
model_id: model-version
risk_class: standard
```

---

# 13. Prompt Registry

Prompts relevantes deverão ser identificáveis por versão.

---

# 14. Context Builder

Responsável por montar contexto autorizado e minimizado.

---

# 15. RAG Service

Responsável por retrieval conforme GAI-03.

---

# 16. Tool Registry

Lista explicitamente tools disponíveis conforme GAI-04.

---

# 17. Agent Runtime

Controla:

- passos;
- budget;
- tools;
- timeout;
- estado;
- abort.

---

# 18. Guardrails

Devem existir fora do modelo quando determinísticos.

---

# 19. Evaluation Layer

Permite executar avaliações independentes do fluxo de produção.

---

# 20. Observability Layer

Deverá atravessar os componentes.

---

# 21. Data Governance

Aplicar GAI-07 em todos os contextos.

---

# 22. Tenant Context

Tenant deverá ser resolvido pela aplicação.

---

# 23. Authorization Context

Permissões deverão ser resolvidas por componentes confiáveis.

---

# 24. Request Context

Objeto interno poderá conter:

```text
request_id
user_id
tenant_id
permissions
feature
environment
```

Nunca confiar nesses valores quando originados diretamente do modelo.

---

# 25. Correlation ID

Propagar entre componentes.

---

# 26. Contratos

Interfaces internas deverão ser pequenas e explícitas.

---

# 27. DTOs

Preferir DTOs específicos para IA.

Evitar enviar modelos ORM completos.

---

# 28. Schemas

Entradas e saídas estruturadas deverão possuir schema.

---

# 29. Structured Output

Preferir para dados consumidos por código.

---

# 30. Erros

Definir categorias internas.

Exemplo:

```text
AIProviderError
AITimeoutError
AIValidationError
AIRateLimitError
AIRetrievalError
AIToolError
```

---

# 31. Timeouts

Definir por camada.

---

# 32. Retries

Retry deverá ocorrer apenas para falhas apropriadas.

---

# 33. Fallback

Fallback deverá ser política do Gateway ou Orchestrator, não improvisação espalhada pelo código.

---

# 34. Circuit Breaker

Poderá proteger providers instáveis.

---

# 35. Rate Limiting

Aplicar antes de operações caras.

---

# 36. Quotas

Quotas poderão ser tenant-aware.

---

# 37. Budgets

Agentes deverão possuir budgets explícitos.

---

# 38. Caching

Cache deverá incluir dimensões de segurança relevantes.

---

# 39. Idempotência

Ações mutáveis originadas por IA deverão preservar idempotência.

---

# 40. Feature Flags

Toda capacidade experimental deverá poder ser controlada.

---

# 41. Padrão de Chamada Simples

```text
User Request
   ↓
Authorization
   ↓
Application Service
   ↓
Prompt Registry
   ↓
AI Gateway
   ↓
Provider Adapter
   ↓
Validation
   ↓
Response
```

Uso:

- reformulação;
- explicação;
- geração simples sem dados sensíveis adicionais.

---

# 42. Padrão de Structured Generation

```text
Input DTO
   ↓
Prompt
   ↓
Model + Output Schema
   ↓
Parse
   ↓
Validate
   ↓
Typed DTO
```

Nunca utilizar texto livre como estrutura confiável quando schema for necessário.

---

# 43. Padrão de Classificação

```text
Authorized Input
   ↓
Classifier Prompt
   ↓
Enum Schema
   ↓
Validation
   ↓
Business Decision
```

Decisões críticas poderão exigir regra determinística adicional.

---

# 44. Padrão de Resumo

```text
Source
   ↓
Minimize
   ↓
Summarize
   ↓
Validate
   ↓
Return
```

O resumo não substitui a fonte de verdade.

---

# 45. Padrão de RAG

```text
Question
   ↓
Authorization
   ↓
Tenant Scope
   ↓
Retrieval
   ↓
Context Builder
   ↓
Prompt
   ↓
Model
   ↓
Grounded Answer
```

---

# 46. Padrão de RAG com Citações

```text
Retrieved Chunks
   │
   ├── source_id
   ├── title
   └── location
        │
        ▼
      Model
        │
        ▼
Answer + Source References
```

Citações deverão ser vinculadas a fontes realmente recuperadas.

---

# 47. Padrão de Tool Calling

```text
Model
   ↓
Tool Proposal
   ↓
Schema Validation
   ↓
Authorization
   ↓
Tool Service
   ↓
Result
   ↓
Model / Application
```

---

# 48. Padrão de Ação Preparada

Preferido para operações sensíveis.

```text
User Intent
   ↓
AI Generates Proposal
   ↓
Application Validates
   ↓
Preview
   ↓
User Reviews
```

Nenhuma alteração ainda ocorreu.

---

# 49. Padrão de Ação Confirmada

```text
Prepared Action
   ↓
User Confirmation
   ↓
Approval Token
   ↓
Authorization Recheck
   ↓
Domain Service
   ↓
Audit
```

---

# 50. Padrão de Agente Multi-Step

```text
Goal
  ↓
Policy
  ↓
Agent Runtime
  ↓
Plan / Next Step
  ↓
Allowed Tool
  ↓
Observe Result
  ↓
Repeat within limits
  ↓
Final Result / Abort
```

---

# 51. Padrão de Job Assíncrono

```text
Request
  ↓
Validate
  ↓
Queue
  ↓
AI Worker
  ↓
Persist Result
  ↓
Notify / Poll
```

O job deverá carregar contexto seguro de tenant e autorização.

---

# 52. Padrão de Batch

Adequado para tarefas não interativas.

Aplicar limites de volume e custo.

---

# 53. Padrão de Fallback

```text
Primary Model
   │
   ├── success → return
   │
   └── eligible failure
          ↓
     Fallback Model
```

Não utilizar fallback para esconder erros de autorização ou validação.

---

# 54. Padrão de Degradação

```text
AI Advanced
   ↓ failure
AI Basic
   ↓ failure
Feature Unavailable

Core Platform
remains available
```

---

# 55. Padrão de Cache

Chave deverá considerar, conforme caso:

```text
tenant
user/permission scope
feature
prompt version
model/config version
input hash
```

---

# 56. Padrão de Auditoria

```text
AI Proposal
   ↓
Validated Action
   ↓
Domain Mutation
   ↓
Audit Event
```

Auditar efeito de negócio, não raciocínio interno.

---

# 57. Padrão de Observabilidade

Cada execução relevante deverá produzir:

```text
request_id
feature
provider
model
duration
status
token_usage
cost_estimate
fallback
```

sem conteúdo sensível desnecessário.

---

# 58. Padrão de Avaliação

```text
Versioned Dataset
   ↓
Evaluation Runner
   ↓
Candidate Configuration
   ↓
Metrics
   ↓
Thresholds
   ↓
PASS / FAIL
```

---

# 59. Padrão de Tenant Isolation

```text
Authenticated User
      ↓
Trusted Tenant Context
      ↓
Authorized Query
      ↓
Tenant-Scoped Data
      ↓
AI Context
```

Nunca:

```text
Model
→ chooses tenant
```

---

# 60. Padrão de Minimização

```text
Domain Object
   ↓
Purpose
   ↓
Field Selection
   ↓
Redaction
   ↓
AI DTO
```

---

# 61. Padrão de Provider Isolation

Código de feature não deverá importar diretamente SDK de provider.

Preferir:

```text
Feature
→ AI Gateway Interface
→ Provider Adapter
```

---

# 62. Padrão de Prompt Versioning

Prompt deverá possuir:

```text
prompt_id
version
purpose
owner
status
```

---

# 63. Padrão de Model Routing

```text
Feature Policy
   ↓
Model Alias
   ↓
Registry
   ↓
Provider + Model
```

Evitar model IDs espalhados pelo código.

---

# 64. Padrão de Kill Switch

```text
Feature Request
   ↓
Feature Flag / Policy
   │
   ├── enabled → continue
   └── disabled → safe response
```

---

# 65. Organização de Código

Estrutura ilustrativa:

```text
ai/
├── gateway/
├── providers/
├── prompts/
├── models/
├── retrieval/
├── tools/
├── agents/
├── guardrails/
├── evaluations/
├── telemetry/
└── policies/
```

A estrutura real deverá respeitar a arquitetura oficial do repositório.

---

# 66. Interfaces de Referência

Interfaces deverão ocultar detalhes de infraestrutura.

---

# 67. AI Gateway Interface

Exemplo conceitual:

```text
generate(request) -> AIResponse
generate_structured(request, schema) -> TypedResult
```

---

# 68. Provider Adapter Interface

```text
invoke(model, messages, options)
```

Provider adapter não deverá conter regra de negócio.

---

# 69. Prompt Interface

```text
get_prompt(prompt_id, version)
render_prompt(prompt, variables)
```

---

# 70. Retrieval Interface

```text
retrieve(
    tenant_context,
    query,
    filters,
    limit
)
```

---

# 71. Tool Interface

```text
validate(args)
authorize(context, args)
execute(context, args)
```

---

# 72. Agent Interface

```text
run(goal, context, policy)
```

Policy deverá definir limites.

---

# 73. Evaluation Interface

```text
evaluate(candidate, dataset, metrics)
```

---

# 74. Convenções de Nomenclatura

Nomes deverão expressar finalidade.

Preferir:

```text
summarize_meeting_notes
```

a:

```text
ai_process_v2
```

---

# 75. Configuração

Configuração deverá ser centralizada quando apropriado.

---

# 76. Secrets

Somente secret management oficial.

---

# 77. Persistência

Persistir apenas dados necessários.

---

# 78. Banco Relacional

Usar para metadados, estados e referências quando apropriado.

---

# 79. Vector Store

Usar somente para necessidades vetoriais reais.

Não transformar vector store em banco principal da aplicação.

---

# 80. Cache

Cache é otimização, não fonte de verdade.

---

# 81. Filas

Usar para workloads assíncronos e controláveis.

---

# 82. Arquivos

Artefatos temporários deverão possuir lifecycle.

---

# 83. Segurança

Aplicar GAI-06 e GSF.

---

# 84. Privacidade

Aplicar GAI-07 e políticas de LGPD.

---

# 85. Logs

Não registrar payload completo por conveniência.

---

# 86. Métricas

Instrumentar desde a primeira versão de production.

---

# 87. Tracing

Usar em fluxos distribuídos ou multi-step quando útil.

---

# 88. Testes

Aplicar GAI-08.

---

# 89. CI/CD

Aplicar GAI-09.

---

# 90. Deploy

Separar deploy técnico de ativação funcional quando possível.

---

# 91. Exemplos de Fluxo

## Assistente com RAG

```text
API
 ↓
Auth
 ↓
Tenant
 ↓
Assistant Service
 ↓
Retrieval
 ↓
Context Builder
 ↓
AI Gateway
 ↓
Validation
 ↓
Response + Sources
```

## Ação assistida

```text
User
 ↓
AI Proposal
 ↓
Preview
 ↓
Confirmation
 ↓
Authorization Recheck
 ↓
Domain Service
 ↓
Audit
```

## Agente

```text
Goal
 ↓
Agent Policy
 ↓
Agent Runtime
 ↓
Allowed Tools
 ↓
Domain Services
 ↓
Audit / Metrics
```

---

# 92. Anti-Padrões

Evitar:

```text
controller
→ provider SDK
```

---

```text
provider SDK
inside domain service
```

---

```text
ORM object
→ full prompt
```

---

```text
model output
→ database write
```

sem validação e autorização.

---

```text
tenant_id
from LLM arguments
```

---

```text
model ID
hardcoded everywhere
```

---

```text
prompt
copied across controllers
```

---

```text
agent
with direct database access
```

---

```text
AI feature
without telemetry
```

---

# 93. Decision Matrix

```text
Need knowledge?
→ RAG

Need deterministic data?
→ Selector / Service first

Need structured result?
→ Structured Output

Need business mutation?
→ Tool + Domain Service

Need user approval?
→ Prepared Action + Confirmation

Need multiple bounded steps?
→ Agent Runtime

Need background processing?
→ Async Job

Need provider flexibility?
→ AI Gateway + Adapter
```

---

# 94. Production Readiness

Uma implementação deverá responder:

```text
Onde está a autorização?
Onde está o tenant?
Qual é o contrato?
Qual prompt?
Qual modelo?
Qual provider?
Como valida output?
Como limita custo?
Como observa?
Como testa?
Como desliga?
```

Se essas respostas não forem claras, a implementação ainda não está pronta.

---

# 95. Checklist

## Arquitetura

- [ ] feature isolada do provider;
- [ ] Application Service;
- [ ] AI Orchestrator quando necessário;
- [ ] AI Gateway;
- [ ] adapters;
- [ ] contracts.

## Segurança

- [ ] autenticação;
- [ ] tenant;
- [ ] autorização;
- [ ] minimização;
- [ ] guardrails;
- [ ] sem secrets;
- [ ] structured validation.

## RAG

- [ ] authorized retrieval;
- [ ] metadata;
- [ ] source references;
- [ ] lifecycle;
- [ ] cross-tenant tests.

## Tools/Agents

- [ ] registry;
- [ ] schemas;
- [ ] policy;
- [ ] limits;
- [ ] confirmations;
- [ ] idempotência;
- [ ] audit.

## Operação

- [ ] timeout;
- [ ] retry;
- [ ] fallback;
- [ ] rate limit;
- [ ] quotas;
- [ ] budget;
- [ ] cache seguro.

## Observabilidade

- [ ] correlation ID;
- [ ] logs;
- [ ] metrics;
- [ ] traces quando necessários;
- [ ] cost metadata.

## Qualidade

- [ ] unit tests;
- [ ] integration tests;
- [ ] evaluations;
- [ ] quality gates;
- [ ] regression baseline.

## Release

- [ ] versionamento;
- [ ] feature flag;
- [ ] rollout;
- [ ] rollback;
- [ ] kill switch quando necessário.

---

# 96. Documentos Relacionados

- GAI-01 — Arquitetura e Governança de Inteligência Artificial
- GAI-02 — Providers, Modelos, Prompts e AI Gateway
- GAI-03 — RAG, Contexto e Conhecimento
- GAI-04 — Ferramentas, Agentes e Ações Seguras
- GAI-05 — Avaliação, Observabilidade, Custos e Operação de IA
- GAI-06 — Segurança, Privacidade e Guardrails de IA
- GAI-07 — Governança de Dados para Inteligência Artificial
- GAI-08 — Testes e Quality Gates para Inteligência Artificial
- GAI-09 — Deploy, Release e Lifecycle de Inteligência Artificial
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework
- GereIgreja Backend Engineering
- GereIgreja Data Engineering

---

# 97. Princípios Finais

Uma boa implementação de IA não espalha chamadas de modelo pela aplicação.

Ela cria fronteiras.

```text
Business Need
    ↓
Application Contract
    ↓
AI Orchestration
    ↓
Controlled Infrastructure
    ↓
Validated Result
```

O princípio central é:

```text
Models are replaceable.

Providers are replaceable.

Prompts are versioned.

Data is governed.

Permissions are deterministic.

Tools are bounded.

Behavior is observable.

Architecture remains stable.
```

A implementação de IA no GereIgreja deverá fortalecer a arquitetura da plataforma, e não criar uma segunda arquitetura paralela sem controles.

---

# 98. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`10-Padroes-de-Implementacao-e-Referencia-de-IA.md`

**Documento**

`GAI-10`

**Código**

`GAI-AI-IMPLEMENTATION-REFERENCE-PATTERNS`

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

`GAI-09 — Deploy, Release e Lifecycle de Inteligência Artificial`

**Próxima etapa recomendada**

`11-Catalogo-de-Casos-de-Uso-e-Niveis-de-Risco-de-IA.md`
