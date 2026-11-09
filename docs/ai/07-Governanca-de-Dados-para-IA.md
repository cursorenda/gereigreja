Pasta:

docs/ai/

Arquivo:

07-Governanca-de-Dados-para-IA.md

Documento:

GAI-07

Código:

GAI-AI-DATA-GOVERNANCE

Família:

GAI — GereIgreja Artificial Intelligence Engineering

Frameworks relacionados:

GEA — GereIgreja Enterprise Architecture
GSF — GereIgreja Security Framework
GQF — GereIgreja Quality Framework
GOC — GereIgreja Operations Center
GDF — GereIgreja Documentation Framework
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

# GAI-07 — Governança de Dados para Inteligência Artificial

> "A IA só pode utilizar dados que a plataforma tenha autoridade, finalidade e controles para utilizar."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Dados como Ativo Governado
6. Categorias de Dados para IA
7. Fontes de Dados
8. Fonte de Verdade
9. Data Ownership
10. Data Stewardship
11. Tenant Ownership
12. Classificação
13. Dados Públicos
14. Dados Internos
15. Dados Restritos
16. Dados Confidenciais
17. Dados Pessoais
18. Dados Sensíveis
19. Dados Financeiros
20. Dados Ministeriais e Pastorais
21. Secrets e Credenciais
22. Finalidade
23. Necessidade
24. Base de Uso
25. Minimização
26. Seleção de Campos
27. Transformação
28. Mascaramento
29. Pseudonimização
30. Anonimização
31. Agregação
32. Proveniência
33. Linhagem
34. Metadados
35. Qualidade dos Dados
36. Completude
37. Atualidade
38. Consistência
39. Validade
40. Duplicidade
41. Data Contracts
42. Contexto para IA
43. Dados em Prompts
44. Dados em RAG
45. Dados em Embeddings
46. Dados em Vector Stores
47. Dados em Memória de Agentes
48. Dados em Tools
49. Dados em Outputs
50. Dados em Logs
51. Dados em Avaliações
52. Dados Sintéticos
53. Dados de Produção em Testes
54. Training e Fine-Tuning
55. Datasets
56. Dataset Registry
57. Versionamento de Datasets
58. Providers Externos
59. Transferência de Dados
60. Residência
61. Retenção
62. Expiração
63. Exclusão
64. Propagação de Exclusão
65. Correção
66. Reindexação
67. Cache
68. Backups
69. Exportações
70. Portabilidade
71. Controle de Acesso
72. Isolamento Multi-Tenant
73. Cross-Tenant Analytics
74. Compartilhamento
75. Consentimento e Expectativa
76. LGPD
77. Direitos dos Titulares
78. Auditoria
79. Observabilidade
80. Incidentes
81. Data Leakage
82. Data Poisoning
83. Qualidade e Poisoning
84. Revisões
85. Data Lifecycle
86. Governança de Novos Casos de Uso
87. Production Readiness
88. Anti-Padrões
89. Arquitetura Consolidada
90. Checklist
91. Documentos Relacionados
92. Princípios Finais
93. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial de governança dos dados utilizados por capacidades de Inteligência Artificial no GereIgreja.

Seu objetivo é garantir que qualquer dado utilizado em prompts, RAG, embeddings, agentes, tools, avaliações ou outras capacidades de IA possua:

- origem conhecida;
- finalidade definida;
- classificação;
- owner;
- escopo de tenant;
- controles de acesso;
- lifecycle;
- retenção;
- rastreabilidade.

---

# 2. Escopo

Aplica-se a dados utilizados em:

- prompts;
- context builders;
- RAG;
- embeddings;
- vector stores;
- memória de agentes;
- tools;
- outputs persistidos;
- logs;
- telemetria;
- datasets de avaliação;
- fine-tuning quando existir;
- integrações com providers de IA.

---

# 3. Relação com a Família GAI

```text
GAI-01
Architecture / Governance
       │
       ├── GAI-02 Models / Prompts
       ├── GAI-03 RAG / Knowledge
       ├── GAI-04 Tools / Agents
       ├── GAI-05 Operations
       ├── GAI-06 Security / Privacy
       │
       ▼
GAI-07
AI Data Governance
```

O GAI-07 não substitui a governança geral de dados da plataforma.

Ele estabelece os controles adicionais necessários quando dados são utilizados por sistemas de IA.

---

# 4. Princípios Fundamentais

Aplicar:

- purpose limitation;
- data minimization;
- tenant isolation;
- provenance;
- ownership;
- quality;
- least access;
- lifecycle management;
- deletion propagation;
- traceability;
- privacy by design.

---

# 5. Dados como Ativo Governado

Dados não deverão ser enviados a um modelo apenas porque estão tecnicamente disponíveis.

A pergunta obrigatória é:

```text
Este dado é necessário,
autorizado
e adequado
para esta finalidade?
```

---

# 6. Categorias de Dados para IA

Distinguir:

```text
Source Data
Derived Data
Retrieved Data
Prompt Data
Generated Data
Operational Data
Evaluation Data
```

---

# 7. Fontes de Dados

Fontes poderão incluir:

- banco transacional;
- documentos;
- APIs;
- arquivos;
- integrações;
- knowledge bases;
- conteúdo público;
- conteúdo gerado.

---

# 8. Fonte de Verdade

IA não deverá transformar cópias derivadas em fonte autoritativa.

```text
System of Record
→ authoritative

AI output
→ derived
```

---

# 9. Data Ownership

Toda categoria relevante deverá possuir owner.

---

# 10. Data Stewardship

Responsabilidades poderão incluir:

- classificação;
- qualidade;
- lifecycle;
- acesso;
- revisão.

---

# 11. Tenant Ownership

Dados de uma igreja permanecem no escopo daquela organização conforme regras da plataforma.

---

# 12. Classificação

Aplicar classificação oficial de segurança.

---

# 13. Dados Públicos

Ainda deverão possuir origem e licença/condição de uso conhecidas quando externas.

---

# 14. Dados Internos

Não deverão ser enviados externamente sem finalidade e provider aprovados.

---

# 15. Dados Restritos

Exigem controles adicionais de acesso.

---

# 16. Dados Confidenciais

Devem ser minimizados e enviados somente quando estritamente necessário e permitido.

---

# 17. Dados Pessoais

Aplicar requisitos de privacidade e LGPD.

---

# 18. Dados Sensíveis

Exigem avaliação reforçada.

---

# 19. Dados Financeiros

Preferir valores agregados ou campos estritamente necessários.

---

# 20. Dados Ministeriais e Pastorais

Informações que revelem contexto pastoral, aconselhamento ou situações pessoais deverão receber tratamento altamente restritivo.

---

# 21. Secrets e Credenciais

Nunca utilizar como contexto de IA:

- passwords;
- API keys;
- session tokens;
- private keys;
- database credentials;
- integration secrets.

---

# 22. Finalidade

Todo uso de dados por IA deverá possuir finalidade funcional identificável.

---

# 23. Necessidade

A disponibilidade do dado não prova necessidade.

---

# 24. Base de Uso

Antes de novos casos de uso envolvendo dados pessoais ou sensíveis, avaliar os requisitos legais e internos aplicáveis.

---

# 25. Minimização

Enviar apenas o subconjunto necessário.

---

# 26. Seleção de Campos

Preferir:

```text
name
status
summary
```

quando a tarefa não necessita do objeto completo.

---

# 27. Transformação

Transformações deverão preservar rastreabilidade quando necessária.

---

# 28. Mascaramento

Exemplo:

```text
email completo
→ parcialmente mascarado
```

quando o valor integral não for necessário.

---

# 29. Pseudonimização

Identificadores poderão ser substituídos por referências internas controladas.

---

# 30. Anonimização

Quando utilizada, deverá buscar impedir reidentificação de forma compatível com a finalidade.

---

# 31. Agregação

Preferir dados agregados quando detalhes individuais não forem necessários.

---

# 32. Proveniência

Deverá ser possível conhecer a origem do dado.

---

# 33. Linhagem

Para pipelines relevantes:

```text
Source
→ Transform
→ Chunk
→ Embedding
→ Retrieval
→ AI Output
```

---

# 34. Metadados

Metadados recomendados:

- source;
- tenant;
- classification;
- owner;
- version;
- timestamp;
- lifecycle status.

---

# 35. Qualidade dos Dados

IA não corrige automaticamente dados ruins.

```text
Poor Data
→ Poor Context
→ Poor AI Result
```

---

# 36. Completude

Avaliar se os campos necessários estão disponíveis.

---

# 37. Atualidade

Dados temporais deverão possuir freshness conhecida.

---

# 38. Consistência

Conflitos entre fontes deverão possuir política.

---

# 39. Validade

Dados deverão respeitar regras do domínio.

---

# 40. Duplicidade

Duplicidades poderão distorcer retrieval e análise.

---

# 41. Data Contracts

Pipelines importantes deverão possuir contratos de dados explícitos.

---

# 42. Contexto para IA

Context Builder deverá receber somente dados previamente autorizados.

---

# 43. Dados em Prompts

Prompts deverão aplicar minimização e classificação.

---

# 44. Dados em RAG

Seguir GAI-03.

---

# 45. Dados em Embeddings

Embeddings são dados derivados e deverão manter vínculo de governança com a fonte.

---

# 46. Dados em Vector Stores

Vector stores deverão possuir:

- tenant;
- source ID;
- lifecycle;
- exclusão;
- acesso restrito.

---

# 47. Dados em Memória de Agentes

Memória deverá possuir finalidade, escopo e retenção explícitos.

Não criar memória permanente por padrão.

---

# 48. Dados em Tools

Tools deverão retornar somente campos necessários.

---

# 49. Dados em Outputs

Outputs persistidos deverão possuir classificação adequada.

---

# 50. Dados em Logs

Logs deverão evitar payloads completos.

---

# 51. Dados em Avaliações

Evaluation datasets deverão ser governados.

---

# 52. Dados Sintéticos

Preferir dados sintéticos para testes quando representativos.

---

# 53. Dados de Produção em Testes

Uso deverá ser excepcional e controlado.

Preferir anonimização ou ambientes apropriados.

---

# 54. Training e Fine-Tuning

Nenhum dado do GereIgreja deverá ser utilizado para treinamento/fine-tuning sem processo explícito de aprovação, finalidade, segurança e privacidade.

---

# 55. Datasets

Datasets deverão possuir:

- owner;
- finalidade;
- origem;
- classificação;
- versão;
- retenção.

---

# 56. Dataset Registry

Quando houver volume suficiente, manter registry de datasets utilizados por IA.

---

# 57. Versionamento de Datasets

Avaliações reproduzíveis exigem versão identificável.

---

# 58. Providers Externos

Enviar somente dados compatíveis com a política do provider aprovado.

---

# 59. Transferência de Dados

Transferências deverão seguir requisitos legais, contratuais e de segurança.

---

# 60. Residência

Avaliar requisitos de residência quando aplicáveis.

---

# 61. Retenção

Definir período compatível com finalidade.

---

# 62. Expiração

Dados temporários deverão expirar.

---

# 63. Exclusão

A exclusão da fonte deverá disparar avaliação dos derivados.

---

# 64. Propagação de Exclusão

Fluxo conceitual:

```text
Source Deleted
      │
      ▼
Chunks
      │
      ▼
Embeddings
      │
      ▼
Vector Index
      │
      ▼
Caches
      │
      ▼
Derived Artifacts
```

---

# 65. Correção

Correção na fonte deverá refletir nos índices derivados conforme política de consistência.

---

# 66. Reindexação

Reindexação deverá preservar isolamento e metadados.

---

# 67. Cache

Cache deverá respeitar:

- tenant;
- authorization;
- version;
- expiration.

---

# 68. Backups

Dados derivados persistentes deverão seguir estratégia de backup quando necessários para recuperação.

Exclusões legais deverão considerar políticas de backup aplicáveis.

---

# 69. Exportações

IA não deverá criar caminho alternativo para exportação irrestrita.

---

# 70. Portabilidade

Dados gerados ou enriquecidos deverão ser classificados quanto à sua relação com os dados originais.

---

# 71. Controle de Acesso

Aplicar autorização antes de acesso aos dados.

---

# 72. Isolamento Multi-Tenant

Obrigatório.

```text
Tenant A data
X
Tenant B AI context
```

---

# 73. Cross-Tenant Analytics

Qualquer análise entre tenants deverá possuir finalidade, arquitetura e governança próprias.

Não poderá surgir acidentalmente por compartilhamento de índice.

---

# 74. Compartilhamento

Dados não deverão ser compartilhados entre organizações por inferência do modelo.

---

# 75. Consentimento e Expectativa

Quando aplicável, considerar se o uso por IA é compatível com a expectativa e finalidade comunicada ao usuário.

---

# 76. LGPD

O uso de IA deverá preservar princípios e obrigações aplicáveis da LGPD.

---

# 77. Direitos dos Titulares

A arquitetura deverá permitir localizar, corrigir e excluir dados relevantes conforme processos oficiais.

---

# 78. Auditoria

Usos de dados de maior sensibilidade poderão exigir trilha específica.

---

# 79. Observabilidade

Monitorar pipelines de dados sem expor conteúdo indevido.

---

# 80. Incidentes

Incidentes envolvendo dados deverão integrar GSF e GAI-06.

---

# 81. Data Leakage

Vazamento deverá ser tratado como incidente de segurança e privacidade.

---

# 82. Data Poisoning

Entradas maliciosas poderão degradar conhecimento e comportamento.

---

# 83. Qualidade e Poisoning

Controles de qualidade também são controles de segurança em pipelines de IA.

---

# 84. Revisões

Revisar quando houver:

- nova fonte;
- novo provider;
- novo tipo de dado;
- nova finalidade;
- nova integração;
- alteração de retenção.

---

# 85. Data Lifecycle

```text
Discover
   ↓
Classify
   ↓
Authorize
   ↓
Use
   ↓
Observe
   ↓
Retain
   ↓
Archive/Delete
```

---

# 86. Governança de Novos Casos de Uso

Antes de nova feature, responder:

```text
Quais dados?
De qual tenant?
Para qual finalidade?
Qual classificação?
Qual provider?
Quanto tempo?
Onde serão persistidos?
Como serão excluídos?
Quem é o owner?
```

---

# 87. Production Readiness

Nenhum novo fluxo de dados para IA deverá chegar a produção sem respostas para as perguntas essenciais de governança.

---

# 88. Anti-Padrões

Evitar:

```text
"já está no banco"
=
pode mandar para IA
```

---

```text
full database row
→ prompt
```

---

```text
production dump
→ evaluation dataset
```

---

```text
deleted source
→ permanent embedding
```

---

```text
shared vector index
without tenant controls
```

---

```text
AI logs
as permanent data lake
```

---

```text
unknown provider retention
+
confidential data
```

---

```text
agent memory
without expiration
```

---

```text
AI output
becomes source of truth
without validation
```

---

# 89. Arquitetura Consolidada

```text
                       DATA SOURCES
                            │
                            ▼
                     CLASSIFICATION
                            │
                            ▼
                    PURPOSE / POLICY
                            │
                            ▼
                  AUTHORIZATION / TENANT
                            │
                            ▼
                      MINIMIZATION
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
            Prompt         RAG           Tool
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                           AI
                            │
                            ▼
                    VALIDATED OUTPUT
                            │
                            ▼
                   GOVERNED PERSISTENCE
                            │
                            ▼
                 RETENTION / CORRECTION
                            │
                            ▼
                         DELETION
```

---

# 90. Checklist

## Origem

- [ ] fonte conhecida;
- [ ] owner;
- [ ] tenant;
- [ ] classificação;
- [ ] finalidade.

## Minimização

- [ ] somente campos necessários;
- [ ] masking quando aplicável;
- [ ] pseudonimização quando aplicável;
- [ ] sem secrets.

## IA

- [ ] prompt governado;
- [ ] RAG autorizado;
- [ ] embeddings governados;
- [ ] memory com lifecycle;
- [ ] tools minimizadas;
- [ ] output classificado.

## Providers

- [ ] provider aprovado;
- [ ] retenção conhecida;
- [ ] uso para treinamento conhecido;
- [ ] residência avaliada quando necessário;
- [ ] transferência compatível.

## Lifecycle

- [ ] freshness;
- [ ] retenção;
- [ ] expiração;
- [ ] correção;
- [ ] exclusão;
- [ ] propagação para derivados.

## Tenant

- [ ] isolamento;
- [ ] filtros;
- [ ] testes cross-tenant;
- [ ] cache segregado;
- [ ] índices protegidos.

## Qualidade

- [ ] completude;
- [ ] consistência;
- [ ] validade;
- [ ] duplicidade;
- [ ] provenance.

## Governança

- [ ] auditoria quando necessária;
- [ ] LGPD;
- [ ] revisão;
- [ ] incident response;
- [ ] production readiness.

---

# 91. Documentos Relacionados

- GAI-01 — Arquitetura e Governança de Inteligência Artificial
- GAI-02 — Providers, Modelos, Prompts e AI Gateway
- GAI-03 — RAG, Contexto e Conhecimento
- GAI-04 — Ferramentas, Agentes e Ações Seguras
- GAI-05 — Avaliação, Observabilidade, Custos e Operação de IA
- GAI-06 — Segurança, Privacidade e Guardrails de IA
- GSF — GereIgreja Security Framework
- GINF — GereIgreja Infrastructure Engineering
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GDF — GereIgreja Documentation Framework
- GereIgreja Backend Engineering
- GereIgreja Data Engineering

---

# 92. Princípios Finais

A governança de dados para IA começa antes da chamada ao modelo.

```text
Data Available
≠
Data Authorized for AI
```

O princípio central é:

```text
Know the source.
Know the owner.
Know the tenant.
Know the purpose.
Know the classification.
Know the lifecycle.

Only then
use the data.
```

O GereIgreja deverá ser capaz de explicar de onde vieram os dados utilizados por uma capacidade de IA, por que foram utilizados, quem podia acessá-los, onde foram processados e como serão corrigidos ou removidos.

---

# 93. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`07-Governanca-de-Dados-para-IA.md`

**Documento**

`GAI-07`

**Código**

`GAI-AI-DATA-GOVERNANCE`

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

`GAI-06 — Segurança, Privacidade e Guardrails de IA`

**Próximo documento candidato**

`08-Testes-e-Quality-Gates-para-IA.md`
