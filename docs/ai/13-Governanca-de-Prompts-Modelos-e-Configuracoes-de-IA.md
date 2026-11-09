Pasta:

docs/ai/

Arquivo:

13-Governanca-de-Prompts-Modelos-e-Configuracoes-de-IA.md

Documento:

GAI-13

Código:

GAI-AI-PROMPT-MODEL-CONFIG-GOVERNANCE

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

# GAI-13 — Governança de Prompts, Modelos e Configurações de Inteligência Artificial

> "Prompts, modelos e configurações são artefatos de produção e devem ser tratados com o mesmo rigor aplicado a código e infraestrutura."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Artefatos Comportamentais de IA
6. Governança de Prompts
7. Prompt ID
8. Prompt Version
9. Prompt Owner
10. Prompt Purpose
11. Prompt Status
12. Prompt Registry
13. Prompt Templates
14. Variáveis
15. System Instructions
16. Developer Instructions
17. User Content
18. Contexto Recuperado
19. Tool Instructions
20. Separação de Instruções e Dados
21. Prompt Composition
22. Prompt Rendering
23. Validação de Variáveis
24. Structured Outputs
25. Prompt Security
26. Prompt Injection
27. Indirect Prompt Injection
28. Dados Sensíveis em Prompts
29. Secrets
30. Prompt Logging
31. Prompt Testing
32. Prompt Evaluation
33. Prompt Regression
34. Prompt Review
35. Prompt Approval
36. Prompt Promotion
37. Prompt Rollback
38. Prompt Deprecation
39. Governança de Modelos
40. Model ID
41. Model Alias
42. Model Registry
43. Model Owner
44. Provider
45. Capabilities
46. Approved Uses
47. Restricted Uses
48. Context Window
49. Structured Output Support
50. Tool Calling Support
51. Multimodalidade
52. Performance
53. Custos
54. Rate Limits
55. Data Handling
56. Retention Profile
57. Training Usage Profile
58. Região e Residência
59. Model Evaluation
60. Model Approval
61. Model Promotion
62. Model Routing
63. Model Fallback
64. Model Upgrade
65. Model Deprecation
66. Model End of Life
67. Governança de Providers
68. Provider Approval
69. Provider Adapter
70. Provider Configuration
71. Provider Failure
72. Governança de Configurações
73. Configuration ID
74. Configuration Version
75. Environment Scope
76. Tenant Scope
77. Feature Scope
78. Runtime Configuration
79. Configuration as Code
80. Remote Configuration
81. Feature Flags
82. Sampling Parameters
83. Temperature
84. Token Limits
85. Stop Conditions
86. Retrieval Configuration
87. Agent Configuration
88. Tool Configuration
89. Guardrail Configuration
90. Timeout Configuration
91. Retry Configuration
92. Fallback Configuration
93. Budget Configuration
94. Configuração Segura
95. Secrets Management
96. Change Management
97. Change Record
98. Impact Analysis
99. Quality Gates
100. Release
101. Rollback
102. Drift
103. Configuration Drift
104. Provider Drift
105. Model Behavior Drift
106. Auditoria
107. Observabilidade
108. Reprodutibilidade
109. Inventário
110. Production Readiness
111. Templates de Registro
112. Anti-Padrões
113. Arquitetura Consolidada
114. Checklist
115. Documentos Relacionados
116. Princípios Finais
117. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial de governança para prompts, modelos, providers e configurações que determinam o comportamento das capacidades de Inteligência Artificial do GereIgreja.

Seu objetivo é impedir alterações comportamentais invisíveis, não versionadas ou impossíveis de reproduzir.

---

# 2. Escopo

Aplica-se a:

- system prompts;
- developer prompts;
- prompt templates;
- model aliases;
- modelos;
- providers;
- routing;
- sampling parameters;
- retrieval configuration;
- agent policies;
- tool policies;
- guardrails;
- timeouts;
- retries;
- fallbacks;
- budgets;
- feature flags relacionados à IA.

---

# 3. Relação com a Família GAI

```text
GAI-01 ... GAI-10
Architecture / Controls / Implementation
             │
             ├── GAI-11 Risk Catalog
             ├── GAI-12 Asset Registry
             │
             ▼
          GAI-13
Prompt / Model / Config Governance
```

GAI-12 registra os ativos.

GAI-13 define como os principais artefatos comportamentais são controlados ao longo do tempo.

---

# 4. Princípios Fundamentais

Aplicar:

- version everything that changes behavior;
- explicit ownership;
- approved providers and models;
- prompts as governed artifacts;
- configuration as controlled change;
- reproducibility;
- evaluation before promotion;
- rollback readiness;
- least privilege;
- secure defaults.

---

# 5. Artefatos Comportamentais de IA

Uma alteração de comportamento pode ocorrer sem mudança no código.

```text
Prompt
Model
Provider
Temperature
Retrieval
Tool Policy
Agent Limits
Guardrail
Fallback
```

Todos poderão constituir artefatos governados.

---

# 6. Governança de Prompts

Prompts de produção relevantes deverão possuir identidade, owner e versão.

---

# 7. Prompt ID

Formato sugerido:

```text
AI-PROMPT-###
```

---

# 8. Prompt Version

Cada alteração material deverá gerar versão identificável.

---

# 9. Prompt Owner

Todo prompt de produção deverá possuir owner técnico.

---

# 10. Prompt Purpose

Registrar finalidade específica.

---

# 11. Prompt Status

Estados recomendados:

```text
DRAFT
EXPERIMENTAL
APPROVED
PRODUCTION
DEPRECATED
DISABLED
```

---

# 12. Prompt Registry

Prompts deverão estar em registry ou fonte versionada oficial.

---

# 13. Prompt Templates

Templates reutilizáveis deverão possuir contrato de variáveis.

---

# 14. Variáveis

Exemplo:

```text
{{tenant_name}}
{{document_context}}
{{user_question}}
```

Variáveis deverão ser validadas antes do rendering.

---

# 15. System Instructions

Devem conter regras estáveis do comportamento esperado.

Não utilizar para transportar dados dinâmicos desnecessariamente.

---

# 16. Developer Instructions

Devem expressar políticas e objetivos controlados pela aplicação.

---

# 17. User Content

Conteúdo do usuário deverá ser tratado como dado não confiável.

---

# 18. Contexto Recuperado

Conteúdo de RAG também deverá ser tratado como dado, não como instrução autoritativa.

---

# 19. Tool Instructions

Descrições de tools deverão ser claras, limitadas e compatíveis com a autorização real.

---

# 20. Separação de Instruções e Dados

Padrão conceitual:

```text
Trusted Instructions
       │
       ▼
Structured Context
       │
       ▼
Untrusted User / Retrieved Data
```

Não concatenar indiscriminadamente todos os elementos como texto equivalente.

---

# 21. Prompt Composition

Composição deverá ser centralizada quando possível.

---

# 22. Prompt Rendering

Rendering deverá escapar, delimitar ou estruturar conteúdo quando necessário.

---

# 23. Validação de Variáveis

Campos obrigatórios ausentes deverão falhar de forma previsível.

---

# 24. Structured Outputs

Quando código consome resultado, preferir schema explícito.

---

# 25. Prompt Security

Prompts não substituem autorização, validação ou isolamento.

---

# 26. Prompt Injection

Testar instruções adversariais em inputs.

---

# 27. Indirect Prompt Injection

Testar instruções adversariais em documentos, páginas ou conteúdo recuperado.

---

# 28. Dados Sensíveis em Prompts

Aplicar minimização antes da composição.

---

# 29. Secrets

Nunca inserir secrets em prompts.

---

# 30. Prompt Logging

Evitar persistir prompts renderizados completos quando contiverem dados protegidos.

Preferir:

```text
prompt_id
prompt_version
```

---

# 31. Prompt Testing

Cada prompt relevante deverá possuir casos de teste.

---

# 32. Prompt Evaluation

Prompts de maior impacto deverão passar por datasets de avaliação.

---

# 33. Prompt Regression

Comparar versão candidata com baseline.

---

# 34. Prompt Review

Mudanças relevantes deverão passar por revisão técnica proporcional ao risco.

---

# 35. Prompt Approval

Prompts R3/R4 deverão seguir aprovação reforçada conforme GAI-11.

---

# 36. Prompt Promotion

Fluxo recomendado:

```text
DRAFT
  ↓
TEST
  ↓
EVALUATE
  ↓
REVIEW
  ↓
APPROVE
  ↓
PRODUCTION
```

---

# 37. Prompt Rollback

Manter versão anterior recuperável durante janela apropriada.

---

# 38. Prompt Deprecation

Prompts sem consumidores deverão ser removidos de forma controlada.

---

# 39. Governança de Modelos

Modelos não deverão ser referenciados arbitrariamente por cada feature.

---

# 40. Model ID

Registrar identificador concreto fornecido pelo provider.

---

# 41. Model Alias

Features deverão preferir aliases controlados.

Exemplo:

```text
ai.fast_text
ai.reasoning_standard
ai.embedding_default
```

---

# 42. Model Registry

Registry deverá mapear:

```text
alias
→ provider
→ model_id
→ approved configuration
```

---

# 43. Model Owner

Cada alias ou configuração de produção deverá possuir owner.

---

# 44. Provider

Somente providers aprovados.

---

# 45. Capabilities

Registrar capacidades necessárias:

- text;
- structured output;
- tool calling;
- vision;
- embeddings;
- outras quando aplicáveis.

---

# 46. Approved Uses

Definir usos permitidos.

---

# 47. Restricted Uses

Definir restrições quando necessário.

---

# 48. Context Window

Registrar limites relevantes para design e custos.

---

# 49. Structured Output Support

Validar suporte antes de utilizar como dependência arquitetural.

---

# 50. Tool Calling Support

Suporte técnico não implica autorização para executar tools.

---

# 51. Multimodalidade

Uso de imagem, áudio ou outros formatos deverá considerar classificação de dados.

---

# 52. Performance

Avaliar latência e throughput.

---

# 53. Custos

Registrar perfil de custo quando relevante.

---

# 54. Rate Limits

Conhecer limites operacionais do provider.

---

# 55. Data Handling

Registrar condições de processamento de dados.

---

# 56. Retention Profile

Conhecer retenção aplicável pelo provider.

---

# 57. Training Usage Profile

Conhecer se e como dados podem ser utilizados pelo provider para melhoria ou treinamento, conforme contrato e configuração aplicáveis.

---

# 58. Região e Residência

Registrar regiões disponíveis e requisitos aplicáveis.

---

# 59. Model Evaluation

Modelo candidato deverá ser avaliado no contexto real dos casos de uso.

---

# 60. Model Approval

Aprovação deverá considerar:

- qualidade;
- segurança;
- privacidade;
- custo;
- performance;
- compatibilidade.

---

# 61. Model Promotion

Promover via alias ou configuração controlada.

---

# 62. Model Routing

Routing deverá ser explícito.

```text
Use Case
   ↓
Model Alias
   ↓
Routing Policy
   ↓
Provider / Model
```

---

# 63. Model Fallback

Fallback deverá ser previamente aprovado.

Não enviar dados a provider alternativo não aprovado apenas porque o principal falhou.

---

# 64. Model Upgrade

Nova versão deverá passar por regression evaluation.

---

# 65. Model Deprecation

Monitorar lifecycle externo.

---

# 66. Model End of Life

Planejar substituição antes da indisponibilidade definitiva.

---

# 67. Governança de Providers

Providers são dependências críticas de terceiros.

---

# 68. Provider Approval

Avaliar:

- segurança;
- privacidade;
- contrato;
- disponibilidade;
- regiões;
- retenção;
- custos;
- observabilidade.

---

# 69. Provider Adapter

Isolar detalhes técnicos conforme GAI-10.

---

# 70. Provider Configuration

Configuração deverá ser centralizada.

---

# 71. Provider Failure

Falhas deverão seguir políticas de timeout, retry e fallback.

---

# 72. Governança de Configurações

Configuração que muda comportamento deverá ser tratada como mudança controlada.

---

# 73. Configuration ID

Configurações compartilhadas deverão possuir identificador quando necessário.

---

# 74. Configuration Version

Alterações relevantes deverão possuir versão ou change record.

---

# 75. Environment Scope

Configuração deverá declarar ambiente.

---

# 76. Tenant Scope

Configurações específicas por tenant deverão possuir isolamento.

---

# 77. Feature Scope

Configurações deverão indicar quais features afetam.

---

# 78. Runtime Configuration

Configuração em runtime deverá ser validada antes do uso.

---

# 79. Configuration as Code

Preferir configuração versionada para parâmetros críticos.

---

# 80. Remote Configuration

Quando utilizada, deverá possuir:

- controle de acesso;
- histórico;
- validação;
- rollback;
- auditoria.

---

# 81. Feature Flags

Flags deverão possuir owner e lifecycle.

---

# 82. Sampling Parameters

Parâmetros de geração deverão ser explícitos quando relevantes.

---

# 83. Temperature

Não alterar arbitrariamente em production.

Mudança poderá afetar avaliações e reprodutibilidade.

---

# 84. Token Limits

Definir limites máximos.

---

# 85. Stop Conditions

Configurar quando necessárias.

---

# 86. Retrieval Configuration

Versionar parâmetros materiais:

```text
embedding_model
chunking
top_k
threshold
reranker
filters
```

---

# 87. Agent Configuration

Versionar:

```text
model_alias
allowed_tools
max_steps
timeout
budget
confirmation_policy
```

---

# 88. Tool Configuration

Definir:

- enablement;
- permissions;
- schemas;
- confirmation requirements.

---

# 89. Guardrail Configuration

Mudanças que reduzem proteção exigem revisão.

---

# 90. Timeout Configuration

Timeout deverá ser explícito por operação relevante.

---

# 91. Retry Configuration

Definir:

- retryable errors;
- attempts;
- backoff.

---

# 92. Fallback Configuration

Fallback deverá preservar requisitos de segurança e privacidade.

---

# 93. Budget Configuration

Definir limites de:

- tokens;
- chamadas;
- passos;
- custo estimado.

---

# 94. Configuração Segura

Configuração inválida deverá falhar para um estado seguro.

---

# 95. Secrets Management

Valores secretos deverão permanecer no sistema oficial de secrets.

---

# 96. Change Management

Toda mudança material deverá possuir rastreabilidade.

---

# 97. Change Record

Registrar, quando aplicável:

```text
artifact
old_version
new_version
reason
owner
evaluation
approval
release
rollback
```

---

# 98. Impact Analysis

Antes de alterar ativo compartilhado, consultar dependências do GAI-12.

---

# 99. Quality Gates

Aplicar GAI-08.

---

# 100. Release

Aplicar GAI-09.

---

# 101. Rollback

Mudanças relevantes deverão possuir versão anterior ou caminho de desativação.

---

# 102. Drift

Drift é divergência entre estado esperado e comportamento/configuração observada.

---

# 103. Configuration Drift

Detectar diferenças entre configuração declarada e runtime.

---

# 104. Provider Drift

Providers poderão alterar comportamento, limites ou políticas externas.

Mudanças relevantes deverão ser reavaliadas.

---

# 105. Model Behavior Drift

Mesmo identificadores estáveis poderão exigir monitoramento contínuo de comportamento quando o provider não garante imutabilidade completa.

---

# 106. Auditoria

Deverá ser possível responder:

```text
qual prompt estava ativo?
qual modelo?
qual provider?
qual configuração?
quando mudou?
quem aprovou?
```

---

# 107. Observabilidade

Telemetria deverá incluir identificadores de configuração relevantes, evitando conteúdo sensível.

Exemplo:

```text
prompt_id
prompt_version
model_alias
provider
model_id
retrieval_version
agent_policy_version
```

---

# 108. Reprodutibilidade

Uma execução relevante deverá ser reproduzível na medida permitida por:

- artefatos versionados;
- configuração registrada;
- provider/model identificados;
- datasets conhecidos.

Não assumir determinismo absoluto do modelo.

---

# 109. Inventário

Todos os artefatos materiais deverão estar relacionados ao GAI-12.

---

# 110. Production Readiness

Antes de ativar configuração:

```text
versioned?
owned?
tested?
evaluated?
approved?
observable?
rollbackable?
registered?
```

---

# 111. Templates de Registro

## Prompt

```text
Prompt ID:
Version:
Owner:
Purpose:
Risk Level:
Model Alias:
Input Variables:
Output Schema:
Status:
Evaluation:
Last Review:
```

## Model Alias

```text
Alias:
Owner:
Provider:
Model ID:
Approved Uses:
Restricted Uses:
Data Profile:
Fallback:
Status:
Last Evaluation:
```

## AI Configuration

```text
Configuration ID:
Version:
Owner:
Environment:
Feature:
Tenant Scope:
Model Alias:
Prompt Version:
Retrieval Version:
Tool Policy:
Agent Policy:
Timeout:
Retry:
Fallback:
Budget:
Feature Flag:
Status:
```

---

# 112. Anti-Padrões

Evitar:

```text
prompt string
hardcoded in controller
```

---

```text
model = "latest"
```

em produção sem controle de versão ou política explícita.

---

```text
temperature changed
directly in production
```

---

```text
fallback
to any available provider
```

---

```text
remote config
without audit history
```

---

```text
prompt edited
without evaluation
```

---

```text
provider SDK defaults
as production policy
```

---

```text
agent tools
configured by user input
```

---

```text
secrets
inside prompt registry
```

---

# 113. Arquitetura Consolidada

```text
                     AI FEATURE
                         │
                         ▼
                   CONFIGURATION
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
       PROMPT         MODEL ALIAS     POLICIES
          │              │              │
          │              ▼              ├── Tools
          │          MODEL REGISTRY     ├── Agent
          │              │              ├── Guardrails
          │              ▼              └── Budgets
          │           PROVIDER
          │              │
          └──────────────┼──────────────┘
                         ▼
                      AI GATEWAY
                         │
                         ▼
                      EXECUTION
                         │
                         ▼
                    OBSERVABILITY
                         │
                         ▼
                  ASSET REGISTRY
```

---

# 114. Checklist

## Prompts

- [ ] Prompt ID;
- [ ] versão;
- [ ] owner;
- [ ] finalidade;
- [ ] variáveis;
- [ ] schema;
- [ ] security tests;
- [ ] evaluation;
- [ ] rollback.

## Modelos

- [ ] alias;
- [ ] provider;
- [ ] model ID;
- [ ] approved uses;
- [ ] data profile;
- [ ] performance;
- [ ] custo;
- [ ] fallback;
- [ ] lifecycle.

## Providers

- [ ] aprovado;
- [ ] retenção conhecida;
- [ ] training usage conhecido;
- [ ] regiões avaliadas;
- [ ] adapter;
- [ ] outage policy.

## Configuração

- [ ] versionada;
- [ ] environment scope;
- [ ] tenant scope;
- [ ] feature scope;
- [ ] validated runtime config;
- [ ] secure defaults;
- [ ] history;
- [ ] rollback.

## Agents e Tools

- [ ] allowed tools;
- [ ] permissions;
- [ ] max steps;
- [ ] timeout;
- [ ] budget;
- [ ] confirmation policy;
- [ ] guardrails.

## Governança

- [ ] GAI-11 risk;
- [ ] GAI-12 inventory;
- [ ] GAI-08 gates;
- [ ] GAI-09 release;
- [ ] audit;
- [ ] observability;
- [ ] periodic review.

---

# 115. Documentos Relacionados

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
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 116. Princípios Finais

Prompts e configurações não são detalhes temporários de implementação.

Eles fazem parte do comportamento entregue ao usuário.

```text
Code Version
alone
does not identify
AI Behavior
```

O princípio central é:

```text
Version the prompt.
Pin or govern the model.
Control the provider.
Validate the configuration.
Evaluate the change.
Observe the runtime.
Keep a rollback path.
```

O GereIgreja deverá conseguir determinar quais artefatos comportamentais estavam ativos em uma execução e controlar sua evolução de forma segura, auditável e reproduzível.

---

# 117. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`13-Governanca-de-Prompts-Modelos-e-Configuracoes-de-IA.md`

**Documento**

`GAI-13`

**Código**

`GAI-AI-PROMPT-MODEL-CONFIG-GOVERNANCE`

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

`GAI-12 — Registro, Inventário e Governança de Ativos de Inteligência Artificial`

**Próximo documento candidato**

`14-Governanca-de-Agentes-Autonomia-e-Human-in-the-Loop.md`
