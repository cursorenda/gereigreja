Pasta:

docs/ai/

Arquivo:

12-Registro-Inventario-e-Governanca-de-Ativos-de-IA.md

Documento:

GAI-12

Código:

GAI-AI-ASSET-REGISTRY-INVENTORY-GOVERNANCE

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

# GAI-12 — Registro, Inventário e Governança de Ativos de Inteligência Artificial

> "Nenhum ativo de IA deve existir em produção sem identidade, owner, finalidade, versão, risco e lifecycle conhecidos."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Conceito de Ativo de IA
6. Objetivos do Inventário
7. Categorias de Ativos
8. Casos de Uso
9. Features
10. Providers
11. Modelos
12. Model Aliases
13. Prompts
14. Prompt Templates
15. Datasets
16. Evaluation Datasets
17. Knowledge Bases
18. Fontes de Conhecimento
19. Embeddings
20. Vector Stores
21. Retrieval Configurations
22. Tools
23. Agentes
24. Agent Policies
25. Guardrails
26. Integrações
27. AI Gateways
28. Pipelines
29. Jobs
30. Caches
31. Artefatos Derivados
32. Identidade do Ativo
33. Asset ID
34. Nome
35. Descrição
36. Owner
37. Technical Owner
38. Business Owner
39. Status
40. Ambiente
41. Tenant Scope
42. Classificação de Risco
43. Classificação de Dados
44. Finalidade
45. Dependências
46. Dependentes
47. Versionamento
48. Proveniência
49. Localização
50. Configuração
51. Secrets
52. Data de Criação
53. Última Revisão
54. Próxima Revisão
55. Lifecycle
56. Experimental
57. Beta
58. Production
59. Deprecated
60. Disabled
61. End of Life
62. Processo de Registro
63. Registro Antes de Produção
64. Descoberta Automática
65. Reconciliação
66. Shadow AI
67. Ativos Não Registrados
68. Inventário Central
69. Source of Truth
70. Relações entre Ativos
71. Dependency Graph
72. Impact Analysis
73. Mudança de Provider
74. Mudança de Modelo
75. Mudança de Prompt
76. Mudança de Dataset
77. Mudança de Knowledge Base
78. Mudança de Tool
79. Mudança de Agente
80. Mudança de Guardrail
81. Reclassificação de Risco
82. Aprovação
83. Revisões Periódicas
84. Evidências
85. Auditoria
86. Observabilidade
87. Custos
88. Segurança
89. Privacidade
90. Vulnerabilidades
91. Incidentes
92. Depreciação
93. Remoção
94. Registro Histórico
95. Retenção de Metadados
96. Templates
97. Registro de Caso de Uso
98. Registro de Modelo
99. Registro de Prompt
100. Registro de Dataset
101. Registro de Knowledge Base
102. Registro de Tool
103. Registro de Agente
104. Registro de Provider
105. Production Readiness
106. Métricas de Governança
107. Anti-Padrões
108. Arquitetura Consolidada
109. Checklist
110. Documentos Relacionados
111. Princípios Finais
112. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para registro, inventário e governança de ativos relacionados à Inteligência Artificial no GereIgreja.

Seu objetivo é garantir visibilidade sobre quais capacidades de IA existem, onde estão, quem responde por elas, quais dados utilizam, quais dependências possuem e qual é seu estado operacional.

---

# 2. Escopo

Aplica-se a ativos de IA utilizados em:

- development;
- staging;
- production;
- avaliações;
- pipelines;
- automações;
- integrações;
- ferramentas internas.

O rigor de registro deverá ser proporcional ao ambiente e ao risco.

---

# 3. Relação com a Família GAI

```text
GAI-01 ... GAI-10
Architecture / Controls / Implementation
             │
             ▼
          GAI-11
       Use Case Risk
             │
             ▼
          GAI-12
 AI Asset Registry / Inventory
```

GAI-11 classifica o risco do caso de uso.

GAI-12 registra os ativos que implementam e suportam esse caso de uso.

---

# 4. Princípios Fundamentais

Aplicar:

- every production asset has an identity;
- every asset has an owner;
- every asset has a purpose;
- every asset has a lifecycle;
- every dependency is traceable;
- risk is visible;
- data classification is visible;
- changes are auditable;
- deprecated assets are removed deliberately;
- unknown AI is treated as governance debt.

---

# 5. Conceito de Ativo de IA

Ativo de IA é qualquer componente, configuração, dataset ou recurso que participe materialmente do comportamento de uma capacidade de Inteligência Artificial.

---

# 6. Objetivos do Inventário

O inventário deverá permitir responder:

```text
Quais recursos de IA existem?
Quem é responsável?
Onde estão em produção?
Quais modelos utilizam?
Quais dados processam?
Quais tools podem executar?
Qual o risco?
Quanto custam?
Quando foram revisados?
O que depende deles?
```

---

# 7. Categorias de Ativos

Categorias recomendadas:

```text
USE_CASE
FEATURE
PROVIDER
MODEL
PROMPT
DATASET
KNOWLEDGE_BASE
EMBEDDING
VECTOR_STORE
RETRIEVAL_CONFIG
TOOL
AGENT
GUARDRAIL
INTEGRATION
PIPELINE
```

---

# 8. Casos de Uso

Casos de uso deverão referenciar o registro definido no GAI-11.

---

# 9. Features

Uma feature poderá implementar um ou mais casos de uso.

---

# 10. Providers

Registrar providers externos e internos utilizados.

---

# 11. Modelos

Registrar modelos aprovados e efetivamente utilizados.

---

# 12. Model Aliases

Aliases deverão mapear para modelos concretos por configuração.

Exemplo:

```text
fast_text
→ provider_x/model_a
```

---

# 13. Prompts

Prompts relevantes deverão possuir identidade e versão.

---

# 14. Prompt Templates

Templates compartilhados também deverão ser governados.

---

# 15. Datasets

Datasets utilizados em IA deverão seguir GAI-07.

---

# 16. Evaluation Datasets

Registrar datasets usados como gates ou benchmarks.

---

# 17. Knowledge Bases

Registrar bases de conhecimento utilizadas por RAG.

---

# 18. Fontes de Conhecimento

Bases deverão apontar para suas fontes principais.

---

# 19. Embeddings

Registrar modelo/versão de embedding quando relevante.

---

# 20. Vector Stores

Registrar infraestrutura e escopo de índices vetoriais.

---

# 21. Retrieval Configurations

Configurações relevantes deverão possuir versão.

Exemplos:

- chunking;
- top-k;
- thresholds;
- filters;
- reranking.

---

# 22. Tools

Toda tool disponível para agentes deverá possuir registro.

---

# 23. Agentes

Agentes deverão possuir identidade própria.

---

# 24. Agent Policies

Políticas de tools, budgets e limites deverão ser versionadas quando relevantes.

---

# 25. Guardrails

Guardrails críticos deverão ser identificáveis.

---

# 26. Integrações

Registrar integrações externas materialmente utilizadas por IA.

---

# 27. AI Gateways

Gateways e adapters relevantes deverão estar associados às features que atendem.

---

# 28. Pipelines

Pipelines de ingestão, indexação e avaliação poderão ser registrados.

---

# 29. Jobs

Jobs permanentes ou recorrentes de IA poderão ser inventariados como componentes operacionais.

---

# 30. Caches

Caches relevantes para comportamento, privacidade ou custo deverão possuir ownership conhecido.

---

# 31. Artefatos Derivados

Chunks, embeddings e índices são derivados e deverão manter vínculo com a fonte.

---

# 32. Identidade do Ativo

Cada ativo governado deverá possuir identificador estável.

---

# 33. Asset ID

Formato sugerido:

```text
AI-ASSET-<TYPE>-###
```

Exemplos:

```text
AI-ASSET-MODEL-001
AI-ASSET-PROMPT-014
AI-ASSET-TOOL-008
```

---

# 34. Nome

Nome deverá expressar finalidade.

---

# 35. Descrição

Descrição curta e objetiva.

---

# 36. Owner

Todo ativo deverá possuir owner.

---

# 37. Technical Owner

Responsável pela implementação e operação técnica.

---

# 38. Business Owner

Quando aplicável, responsável pelo uso funcional e impacto de negócio.

---

# 39. Status

Status deverá refletir lifecycle real.

---

# 40. Ambiente

Registrar:

```text
development
staging
production
```

quando aplicável.

---

# 41. Tenant Scope

Registrar se o ativo é:

- global;
- tenant-scoped;
- tenant-configurable;
- internal-only.

---

# 42. Classificação de Risco

Relacionar ao GAI-11.

---

# 43. Classificação de Dados

Relacionar ao GAI-07 e GSF.

---

# 44. Finalidade

Ativo sem finalidade conhecida deverá ser revisado.

---

# 45. Dependências

Exemplos:

```text
Agent
→ Prompt
→ Model Alias
→ Provider
```

---

# 46. Dependentes

Também deverá ser possível identificar quem utiliza o ativo.

---

# 47. Versionamento

Registrar versão ativa e, quando necessário, histórico.

---

# 48. Proveniência

Datasets e knowledge assets deverão possuir origem conhecida.

---

# 49. Localização

Registrar localização lógica:

- repositório;
- serviço;
- registry;
- storage;
- infraestrutura.

Não registrar secrets.

---

# 50. Configuração

Configurações críticas deverão apontar para fonte versionada quando possível.

---

# 51. Secrets

O inventário poderá registrar que um ativo depende de determinada categoria de secret.

Nunca armazenar o valor do secret no inventário.

---

# 52. Data de Criação

Registrar quando relevante.

---

# 53. Última Revisão

Obrigatória para ativos críticos.

---

# 54. Próxima Revisão

Definir conforme risco.

---

# 55. Lifecycle

Todo ativo deverá possuir lifecycle explícito.

---

# 56. Experimental

Ainda em experimentação.

---

# 57. Beta

Disponível de forma limitada.

---

# 58. Production

Aprovado para uso regular.

---

# 59. Deprecated

Possui substituição ou remoção planejada.

---

# 60. Disabled

Desativado, mas ainda existente tecnicamente.

---

# 61. End of Life

Removido do uso operacional.

---

# 62. Processo de Registro

Fluxo:

```text
Create Asset
   ↓
Assign ID
   ↓
Assign Owner
   ↓
Classify
   ↓
Link Dependencies
   ↓
Review
   ↓
Approve
   ↓
Activate
```

---

# 63. Registro Antes de Produção

Ativos materiais deverão estar registrados antes da ativação em production.

---

# 64. Descoberta Automática

Quando viável, automação poderá identificar:

- modelos configurados;
- prompts;
- tools;
- agents;
- providers.

---

# 65. Reconciliação

Comparar periodicamente:

```text
Declared Inventory
vs
Observed Production
```

---

# 66. Shadow AI

Shadow AI é o uso de recursos de IA não registrados ou não aprovados dentro dos processos da organização.

Deverá ser identificado e regularizado ou removido.

---

# 67. Ativos Não Registrados

Ativo de produção não registrado deverá gerar ação de governança.

---

# 68. Inventário Central

Deverá existir uma fonte central de consulta dos ativos governados.

A implementação poderá evoluir de arquivos versionados para registry dedicado conforme escala.

---

# 69. Source of Truth

Definir claramente qual repositório ou sistema é autoritativo para metadados do inventário.

---

# 70. Relações entre Ativos

Relações são essenciais para análise de impacto.

---

# 71. Dependency Graph

Exemplo:

```text
Use Case
   ↓
Feature
   ↓
Agent
   ├── Prompt
   ├── Tools
   ├── Model Alias
   └── Knowledge Base
            ↓
       Embedding Model
            ↓
        Vector Store
```

---

# 72. Impact Analysis

Antes de alterar ativo compartilhado, identificar dependentes.

---

# 73. Mudança de Provider

Identificar todos os modelos/features afetados.

---

# 74. Mudança de Modelo

Identificar prompts, evaluations e casos de uso dependentes.

---

# 75. Mudança de Prompt

Identificar features e agentes consumidores.

---

# 76. Mudança de Dataset

Avaliar impacto em baselines e comparabilidade.

---

# 77. Mudança de Knowledge Base

Avaliar retrieval e casos de uso afetados.

---

# 78. Mudança de Tool

Identificar agentes que possuem acesso.

---

# 79. Mudança de Agente

Reavaliar risco e dependências.

---

# 80. Mudança de Guardrail

Redução de proteção deverá disparar revisão.

---

# 81. Reclassificação de Risco

Mudanças relevantes deverão atualizar o risco do caso de uso e ativos relacionados.

---

# 82. Aprovação

Ativos R3/R4 ou equivalentes deverão seguir aprovação reforçada.

---

# 83. Revisões Periódicas

Periodicidade deverá considerar:

- risco;
- criticidade;
- mudanças externas;
- depreciação;
- incidentes.

---

# 84. Evidências

O inventário deverá apontar para evidências relevantes, quando aplicável:

- evaluation;
- security review;
- approval;
- release;
- runbook.

---

# 85. Auditoria

Mudanças de metadados críticos deverão ser rastreáveis.

---

# 86. Observabilidade

Relacionar ativos com métricas e dashboards quando possível.

---

# 87. Custos

Relacionar providers, modelos e features com dados de custo quando relevante.

---

# 88. Segurança

Inventário deverá apoiar:

- threat modeling;
- incident response;
- access review;
- vulnerability response.

---

# 89. Privacidade

Deverá ser possível localizar ativos que processam determinadas classes de dados.

---

# 90. Vulnerabilidades

Dependências vulneráveis deverão poder ser relacionadas aos ativos afetados.

---

# 91. Incidentes

Durante incidente, o inventário deverá ajudar a responder:

```text
o que usa este provider?
quais agentes têm esta tool?
quais features usam este modelo?
quais dados passam por este pipeline?
```

---

# 92. Depreciação

Ativos deprecated deverão possuir:

- substituto;
- owner;
- prazo;
- dependentes;
- plano de remoção.

---

# 93. Remoção

Antes de remover, validar dependentes.

---

# 94. Registro Histórico

Manter histórico suficiente para auditoria e investigação.

---

# 95. Retenção de Metadados

Metadados de ativos poderão ter retenção superior ao próprio ativo quando necessários para auditoria.

---

# 96. Templates

O inventário deverá utilizar templates consistentes.

---

# 97. Registro de Caso de Uso

Campos mínimos:

```text
use_case_id
name
owner
purpose
risk_level
data_classes
status
```

---

# 98. Registro de Modelo

Campos mínimos:

```text
asset_id
provider
model_id
alias
owner
approved_use
status
risk_notes
```

---

# 99. Registro de Prompt

Campos mínimos:

```text
asset_id
prompt_id
version
owner
purpose
model_alias
status
```

---

# 100. Registro de Dataset

Campos mínimos:

```text
asset_id
dataset_id
version
owner
purpose
source
data_classification
retention
status
```

---

# 101. Registro de Knowledge Base

Campos mínimos:

```text
asset_id
knowledge_base_id
owner
tenant_scope
sources
embedding_model
vector_store
retention
status
```

---

# 102. Registro de Tool

Campos mínimos:

```text
asset_id
tool_id
owner
risk_level
required_permission
mutability
confirmation_policy
status
```

---

# 103. Registro de Agente

Campos mínimos:

```text
asset_id
agent_id
owner
purpose
risk_level
allowed_tools
model_alias
max_steps
budget
kill_switch
status
```

---

# 104. Registro de Provider

Campos mínimos:

```text
asset_id
provider_id
owner
approved_data_classes
retention_profile
training_usage_profile
regions
status
```

---

# 105. Production Readiness

Antes de production, verificar:

```text
registered?
owner?
risk?
data?
dependencies?
version?
evaluation?
security?
rollback?
lifecycle?
```

---

# 106. Métricas de Governança

Exemplos:

```text
ai_assets_total
ai_assets_without_owner
ai_assets_without_review
ai_assets_deprecated
ai_assets_unregistered_detected
ai_high_risk_assets
ai_assets_past_review_date
```

---

# 107. Anti-Padrões

Evitar:

```text
production model
unknown to inventory
```

---

```text
prompt
without owner
```

---

```text
agent
without dependency list
```

---

```text
provider
used because developer had API key
```

---

```text
deprecated model
with unknown consumers
```

---

```text
inventory spreadsheet
never reconciled with production
```

---

```text
asset registry
containing secrets
```

---

```text
one generic entry:
"OpenAI"
for every model, prompt and feature
```

---

# 108. Arquitetura Consolidada

```text
                       AI USE CASE
                           │
                           ▼
                        FEATURE
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
       PROMPT            AGENT             RAG
          │                │                │
          ▼                ▼                ▼
        MODEL            TOOLS        KNOWLEDGE BASE
          │                                 │
          ▼                                 ▼
       PROVIDER                         EMBEDDINGS
                                            │
                                            ▼
                                       VECTOR STORE

                 ALL REGISTERED IN
                         │
                         ▼
                   AI ASSET REGISTRY
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
     RISK              OWNER            LIFECYCLE
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
                 GOVERNANCE / AUDIT
```

---

# 109. Checklist

## Identidade

- [ ] Asset ID;
- [ ] nome;
- [ ] categoria;
- [ ] descrição;
- [ ] owner.

## Classificação

- [ ] risco;
- [ ] dados;
- [ ] tenant scope;
- [ ] finalidade;
- [ ] ambiente.

## Dependências

- [ ] providers;
- [ ] modelos;
- [ ] prompts;
- [ ] datasets;
- [ ] knowledge bases;
- [ ] tools;
- [ ] agents;
- [ ] guardrails.

## Lifecycle

- [ ] status;
- [ ] versão;
- [ ] data de criação;
- [ ] última revisão;
- [ ] próxima revisão;
- [ ] depreciação;
- [ ] EOL.

## Governança

- [ ] avaliação;
- [ ] security review;
- [ ] aprovação;
- [ ] auditoria;
- [ ] evidências;
- [ ] incident linkage.

## Produção

- [ ] registrado antes da ativação;
- [ ] reconciliado;
- [ ] observável;
- [ ] rollback conhecido;
- [ ] kill switch quando necessário.

---

# 110. Documentos Relacionados

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
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 111. Princípios Finais

Governança de IA exige inventário real, não conhecimento informal da equipe.

```text
Unknown Asset
=
Unknown Risk
```

O princípio central é:

```text
Register it.
Classify it.
Own it.
Version it.
Connect it.
Review it.
Retire it.
```

O GereIgreja deverá ser capaz de identificar rapidamente quais ativos de IA estão ativos, quais casos de uso suportam, quais dados processam, quais dependências possuem e quem responde por eles.

---

# 112. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`12-Registro-Inventario-e-Governanca-de-Ativos-de-IA.md`

**Documento**

`GAI-12`

**Código**

`GAI-AI-ASSET-REGISTRY-INVENTORY-GOVERNANCE`

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

`GAI-11 — Catálogo de Casos de Uso e Níveis de Risco de Inteligência Artificial`

**Próximo documento candidato**

`13-Governanca-de-Prompts-Modelos-e-Configuracoes-de-IA.md`
