Pasta:

docs/ai/

Arquivo:

25-Governanca-de-Datasets-Sinteticos-Fine-Tuning-e-Customizacao-de-Modelos.md

Documento:

GAI-25

Código:

GAI-AI-SYNTHETIC-DATA-FINETUNING-MODEL-CUSTOMIZATION

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

# GAI-25 — Governança de Datasets Sintéticos, Fine-Tuning e Customização de Modelos

> "Customizar um modelo transforma dados, parâmetros e decisões de treinamento em parte do comportamento de produção. Tudo o que influencia esse comportamento precisa de proveniência, avaliação, ownership e lifecycle."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Tipos de Customização
6. Prompting versus Customização
7. RAG versus Fine-Tuning
8. Fine-Tuning
9. Continued Pretraining
10. Adapters
11. LoRA e PEFT
12. Distillation
13. Custom Models
14. Datasets de Treinamento
15. Datasets de Validação
16. Datasets de Teste
17. Datasets Sintéticos
18. Finalidade
19. Proveniência
20. Data Lineage
21. Data Ownership
22. Classificação
23. Dados Pessoais
24. Dados Sensíveis
25. Dados de Tenant
26. Segregação entre Tenants
27. Consentimento e Base Autorizada
28. Direitos de Uso
29. Propriedade Intelectual
30. Conteúdo de Terceiros
31. Licenciamento
32. Minimização
33. Retenção
34. Exclusão
35. Deduplicação
36. Qualidade
37. Representatividade
38. Bias
39. Contaminação
40. Data Leakage
41. Test Set Leakage
42. Memorization
43. Regurgitation
44. Secrets
45. PII Leakage
46. Synthetic Data Generation
47. Synthetic Data Labeling
48. Synthetic Data Quality
49. Synthetic Data Risks
50. Human Review
51. Dataset Versioning
52. Dataset Registry
53. Dataset Card
54. Model Registry
55. Model Card
56. Training Run
57. Training Run ID
58. Reprodutibilidade
59. Hyperparameters
60. Base Model
61. Provider
62. Training Infrastructure
63. Security
64. Access Control
65. Encryption
66. Environment Isolation
67. Artifact Integrity
68. Supply Chain
69. Training Approval
70. Risk Classification
71. Evaluation Plan
72. Baseline
73. Holdout
74. Golden Dataset
75. Regression Evaluation
76. Safety Evaluation
77. Security Evaluation
78. Privacy Evaluation
79. Bias Evaluation
80. Performance Evaluation
81. Cost Evaluation
82. Acceptance Criteria
83. Quality Gates
84. Promotion
85. Model Alias
86. Deployment
87. Canary
88. Shadow
89. Rollback
90. Observability
91. Drift
92. Model Decay
93. Retraining
94. Retraining Triggers
95. Continuous Training
96. Human Approval
97. Change Management
98. Exceptions
99. Provider-Hosted Fine-Tuning
100. Data Retention by Provider
101. Training Data Use by Provider
102. Model Ownership
103. Portability
104. Exportability
105. Vendor Lock-In
106. Deletion
107. Decommission
108. Audit
109. Evidence
110. Compliance
111. Métricas
112. Production Readiness
113. Templates
114. Anti-Padrões
115. Arquitetura Consolidada
116. Checklist
117. Documentos Relacionados
118. Princípios Finais
119. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para governança de datasets sintéticos, fine-tuning e outras formas de customização de modelos de Inteligência Artificial no GereIgreja.

Seu objetivo é assegurar que customizações sejam justificadas, reproduzíveis, avaliadas, seguras, rastreáveis e compatíveis com requisitos de dados, privacidade, propriedade intelectual, qualidade e lifecycle.

---

# 2. Escopo

Aplica-se a:

- fine-tuning;
- continued pretraining;
- adapters;
- LoRA;
- PEFT;
- distillation;
- modelos customizados;
- datasets de treinamento;
- datasets sintéticos;
- datasets de validação;
- datasets de teste;
- pipelines de treinamento e retraining.

---

# 3. Relação com a Família GAI

```text
GAI-07
Data Governance
      │
GAI-08
Testing / Quality Gates
      │
GAI-11
Risk Classification
      │
GAI-12
Asset Registry
      │
GAI-13
Model Governance
      │
GAI-16
Provider Governance
      │
GAI-23
Change Management
      │
      ▼
GAI-25
Training / Synthetic Data / Custom Models
```

---

# 4. Princípios Fundamentais

Aplicar:

- customize only with clear purpose;
- provenance before training;
- separate train, validation and test;
- no secrets in datasets;
- tenant boundaries remain enforceable;
- evaluate against baseline;
- version every material artifact;
- reproducibility where practical;
- promote only through gates;
- custom models have full lifecycle.

---

# 5. Tipos de Customização

Customização poderá ocorrer por:

```text
prompt
configuration
RAG
fine-tuning
adapter
continued pretraining
distillation
custom training
```

Cada opção possui custo e risco diferentes.

---

# 6. Prompting versus Customização

Antes de treinar, avaliar se o objetivo pode ser atendido com prompting ou configuração controlada.

---

# 7. RAG versus Fine-Tuning

Conhecimento frequentemente mutável tende a ser melhor tratado por mecanismos recuperáveis e atualizáveis.

Fine-tuning não deverá ser utilizado como substituto automático para governança de conhecimento.

---

# 8. Fine-Tuning

Fine-tuning deverá possuir:

- finalidade;
- dataset aprovado;
- base model identificada;
- owner;
- avaliação;
- versionamento;
- rollback.

---

# 9. Continued Pretraining

Exige governança reforçada devido ao volume e impacto potencial dos dados.

---

# 10. Adapters

Adapters deverão ser tratados como artefatos versionados.

---

# 11. LoRA e PEFT

Pesos ou adapters resultantes deverão possuir identidade e lifecycle próprios.

---

# 12. Distillation

Distillation deverá avaliar:

- perda de qualidade;
- transferência de comportamento;
- segurança;
- direitos sobre outputs utilizados.

---

# 13. Custom Models

Modelos treinados ou fortemente customizados deverão ser registrados como ativos independentes.

---

# 14. Datasets de Treinamento

Todo dataset de treinamento deverá possuir owner e proveniência.

---

# 15. Datasets de Validação

Não deverão ser usados indiscriminadamente para otimização até perderem independência.

---

# 16. Datasets de Teste

Test sets críticos deverão ser protegidos contra contaminação.

---

# 17. Datasets Sintéticos

Dados sintéticos continuam sendo ativos de dados e exigem governança.

---

# 18. Finalidade

Cada dataset deverá possuir finalidade explícita.

---

# 19. Proveniência

Registrar origem dos dados e transformações relevantes.

---

# 20. Data Lineage

Fluxo conceitual:

```text
Source
  ↓
Extraction
  ↓
Filtering
  ↓
Transformation
  ↓
Labeling
  ↓
Dataset Version
  ↓
Training Run
  ↓
Model Version
```

---

# 21. Data Ownership

Todo dataset deverá possuir owner.

---

# 22. Classificação

Aplicar classificação de dados existente.

---

# 23. Dados Pessoais

Uso em treinamento deverá ser avaliado especificamente.

---

# 24. Dados Sensíveis

Exigem controles reforçados e necessidade demonstrável.

---

# 25. Dados de Tenant

Dados de tenants não deverão ser combinados para treinamento sem autorização e desenho de isolamento apropriados.

---

# 26. Segregação entre Tenants

Customização não deverá criar canal indireto de vazamento entre tenants.

---

# 27. Consentimento e Base Autorizada

Quando aplicável, confirmar base legítima para o uso de dados.

---

# 28. Direitos de Uso

Acesso ao dado não implica direito de utilizá-lo para treinamento.

---

# 29. Propriedade Intelectual

Avaliar direitos sobre conteúdo utilizado.

---

# 30. Conteúdo de Terceiros

Conteúdo externo deverá possuir origem e direitos compatíveis com a finalidade.

---

# 31. Licenciamento

Licenças incompatíveis deverão impedir inclusão no dataset.

---

# 32. Minimização

Utilizar apenas os dados necessários.

---

# 33. Retenção

Definir retenção para datasets intermediários e finais.

---

# 34. Exclusão

Deverá existir processo para remoção quando exigida.

---

# 35. Deduplicação

Reduzir duplicação quando ela aumentar memorization ou distorção.

---

# 36. Qualidade

Avaliar:

- completude;
- consistência;
- precisão;
- relevância;
- labeling quality.

---

# 37. Representatividade

Verificar se dataset representa adequadamente os cenários de uso.

---

# 38. Bias

Avaliar vieses relevantes ao contexto.

---

# 39. Contaminação

Evitar mistura indevida entre conjuntos de treinamento e avaliação.

---

# 40. Data Leakage

Controlar vazamento de informação entre splits.

---

# 41. Test Set Leakage

Test set não deverá ser incorporado ao treinamento.

---

# 42. Memorization

Avaliar risco de memorização de conteúdo protegido ou sensível.

---

# 43. Regurgitation

Testar reprodução indevida quando o risco justificar.

---

# 44. Secrets

Secrets são proibidos em datasets de treinamento.

---

# 45. PII Leakage

Executar testes de leakage quando houver risco de dados pessoais.

---

# 46. Synthetic Data Generation

Geração deverá registrar:

```text
generator model
prompt/config
source context
generation date
filters
review method
```

---

# 47. Synthetic Data Labeling

Dados sintéticos deverão ser identificáveis como sintéticos.

---

# 48. Synthetic Data Quality

Não assumir que geração sintética produz automaticamente dados corretos.

---

# 49. Synthetic Data Risks

Riscos incluem:

- amplificação de bias;
- baixa diversidade;
- erros replicados;
- synthetic collapse;
- falsa representatividade.

---

# 50. Human Review

Amostragem humana poderá ser necessária para validar qualidade.

---

# 51. Dataset Versioning

Datasets materiais deverão ser versionados.

Exemplo:

```text
ai-dataset://support-intent/v3
```

---

# 52. Dataset Registry

Registrar datasets relevantes no inventário.

---

# 53. Dataset Card

Deverá documentar finalidade, origem, limitações e composição.

---

# 54. Model Registry

Modelos customizados deverão constar no registro de ativos.

---

# 55. Model Card

Documentar:

- base model;
- treinamento;
- finalidade;
- avaliações;
- limitações;
- owner.

---

# 56. Training Run

Cada treinamento material deverá possuir registro.

---

# 57. Training Run ID

Formato sugerido:

```text
AI-TRAIN-YYYY-####
```

---

# 58. Reprodutibilidade

Preservar informação suficiente para reproduzir ou explicar o treinamento quando praticável.

---

# 59. Hyperparameters

Registrar parâmetros materiais.

---

# 60. Base Model

Registrar versão exata ou identificador disponível.

---

# 61. Provider

Registrar provider e ambiente de treinamento.

---

# 62. Training Infrastructure

Infraestrutura deverá seguir padrões de segurança e acesso.

---

# 63. Security

Aplicar GSF e GAI-06.

---

# 64. Access Control

Acesso a datasets e artefatos deverá seguir least privilege.

---

# 65. Encryption

Aplicar criptografia conforme classificação.

---

# 66. Environment Isolation

Separar ambientes conforme criticidade.

---

# 67. Artifact Integrity

Preservar integridade de datasets, adapters e modelos.

---

# 68. Supply Chain

Dependências de treinamento deverão ser controladas.

---

# 69. Training Approval

Treinamentos de maior risco deverão ser aprovados antes da execução.

---

# 70. Risk Classification

Aplicar GAI-11.

---

# 71. Evaluation Plan

Definir antes da promoção.

---

# 72. Baseline

Comparar modelo customizado com baseline apropriado.

---

# 73. Holdout

Preservar conjunto independente quando necessário.

---

# 74. Golden Dataset

Utilizar golden datasets versionados para cenários críticos.

---

# 75. Regression Evaluation

Customização não deverá degradar capacidades críticas sem decisão explícita.

---

# 76. Safety Evaluation

Avaliar comportamento inseguro relevante.

---

# 77. Security Evaluation

Testar riscos como leakage e prompt injection quando aplicável.

---

# 78. Privacy Evaluation

Avaliar exposição de dados e memorization.

---

# 79. Bias Evaluation

Aplicar métricas adequadas ao domínio.

---

# 80. Performance Evaluation

Avaliar latência, throughput e recursos quando relevante.

---

# 81. Cost Evaluation

Comparar custo total com alternativas.

---

# 82. Acceptance Criteria

Critérios deverão ser definidos antes da promoção.

---

# 83. Quality Gates

Aplicar GAI-08.

---

# 84. Promotion

Nenhum modelo customizado deverá ser promovido apenas porque o training loss melhorou.

---

# 85. Model Alias

Produção deverá preferir aliases controlados.

---

# 86. Deployment

Aplicar GAI-09.

---

# 87. Canary

Utilizar rollout progressivo quando apropriado.

---

# 88. Shadow

Comparar comportamento sem efeito real quando útil.

---

# 89. Rollback

Manter versão anterior disponível conforme criticidade.

---

# 90. Observability

Monitorar qualidade, segurança, custo e drift.

---

# 91. Drift

Detectar alterações de distribuição ou desempenho.

---

# 92. Model Decay

Desempenho poderá degradar com mudança do domínio.

---

# 93. Retraining

Retraining é uma nova mudança governada, não operação invisível.

---

# 94. Retraining Triggers

Exemplos:

```text
quality degradation
data distribution shift
new approved dataset
model/provider change
material incident
```

---

# 95. Continuous Training

Somente adotar com controles fortes de dataset, avaliação e promoção.

---

# 96. Human Approval

Automação de treinamento não implica automação irrestrita de promoção.

---

# 97. Change Management

Aplicar GAI-23.

---

# 98. Exceptions

Exceções deverão ser temporárias e evidenciadas.

---

# 99. Provider-Hosted Fine-Tuning

Avaliar termos específicos do serviço.

---

# 100. Data Retention by Provider

Confirmar retenção e exclusão.

---

# 101. Training Data Use by Provider

Confirmar se dados enviados poderão ser utilizados pelo provider para outros fins.

---

# 102. Model Ownership

Definir direitos sobre o artefato customizado.

---

# 103. Portability

Avaliar capacidade de migração.

---

# 104. Exportability

Registrar se pesos/adapters podem ser exportados.

---

# 105. Vendor Lock-In

Considerar dependência operacional e econômica.

---

# 106. Deletion

Definir processo para excluir datasets e artefatos quando necessário.

---

# 107. Decommission

Aplicar GAI-19.

---

# 108. Audit

Treinamentos e promoções materiais deverão ser auditáveis.

---

# 109. Evidence

Preservar conforme GAI-18.

---

# 110. Compliance

Mapear requisitos legais, contratuais e internos aplicáveis.

---

# 111. Métricas

Exemplos:

```text
ai_custom_models_total
ai_training_runs
ai_training_runs_failed
ai_datasets_without_owner
ai_datasets_without_provenance
ai_synthetic_dataset_ratio
ai_test_contamination_findings
ai_privacy_leakage_findings
ai_custom_model_regressions
ai_retraining_frequency
```

---

# 112. Production Readiness

Antes de promover modelo customizado:

```text
purpose?
owner?
base model?
dataset provenance?
data rights?
tenant isolation?
no secrets?
versioned dataset?
training run recorded?
baseline comparison?
safety evaluation?
privacy evaluation?
quality gates?
rollback?
observability?
```

---

# 113. Templates

## AI Dataset Card

```text
Dataset ID:
Name:
Version:
Owner:

Purpose:
Type:
- Training
- Validation
- Test
- Synthetic

Sources:
Provenance:
License / Rights:

Data Classes:
Personal Data:
Sensitive Data:
Tenant Data:

Generation Method:
Synthetic Generator:
Labeling Method:

Filtering:
Deduplication:
Quality Checks:
Bias Review:

Retention:
Deletion Procedure:

Known Limitations:
Approved Uses:
Prohibited Uses:

Created At:
Last Review:
Status:
```

## AI Training Run Record

```text
Training Run ID:
Owner:
Date:

Purpose:
Risk Level:

Base Model:
Provider:
Training Method:

Dataset Versions:
Validation Dataset:
Test Dataset:

Hyperparameters:
Infrastructure:
Code / Pipeline Version:

Evaluation Plan:
Baseline:
Results:

Safety Results:
Security Results:
Privacy Results:
Bias Results:
Cost Results:

Acceptance Criteria:
Approval:
Produced Model ID:
Evidence:
```

## AI Custom Model Card

```text
Model ID:
Alias:
Version:
Owner:

Base Model:
Training Run ID:
Training Method:

Intended Use:
Prohibited Use:

Data Summary:
Evaluation Summary:
Safety Summary:
Privacy Summary:

Known Limitations:
Rollback Version:
Provider:
Deployment Environment:

Created At:
Last Review:
Status:
```

---

# 114. Anti-Padrões

Evitar:

```text
customer data
+
fine-tuning
+
no provenance
```

---

```text
test dataset
included in training
```

---

```text
synthetic data
=
automatically safe data
```

---

```text
training loss improved
=
production approved
```

---

```text
API keys
inside training examples
```

---

```text
one tenant's data
used to improve another tenant's model
without authorization
```

---

```text
retraining automatically
promotes itself
```

---

```text
custom model
with no rollback version
```

---

```text
dataset copied
with no owner or retention
```

---

# 115. Arquitetura Consolidada

```text
                         DATA SOURCES
                              │
                              ▼
                         PROVENANCE
                              │
                              ▼
                     DATA GOVERNANCE
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
              TRAIN        VALIDATION      TEST
                 │            │            │
                 └────────────┼────────────┘
                              ▼
                       TRAINING RUN
                              │
                              ▼
                       CUSTOM MODEL
                              │
                              ▼
                         EVALUATION
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
            QUALITY         SAFETY         PRIVACY
               │              │              │
               └──────────────┼──────────────┘
                              ▼
                           GATES
                              │
                              ▼
                          REGISTRY
                              │
                              ▼
                          RELEASE
                              │
                              ▼
                        OBSERVABILITY
                              │
                     ┌────────┴────────┐
                     ▼                 ▼
                 RETRAIN            RETIRE
```

---

# 116. Checklist

## Dataset

- [ ] owner;
- [ ] purpose;
- [ ] provenance;
- [ ] lineage;
- [ ] rights/license;
- [ ] classification;
- [ ] tenant review;
- [ ] privacy review;
- [ ] no secrets;
- [ ] versioning;
- [ ] retention.

## Synthetic Data

- [ ] generator identified;
- [ ] generation config recorded;
- [ ] synthetic label;
- [ ] quality validation;
- [ ] bias review;
- [ ] diversity review;
- [ ] human sampling when needed.

## Training

- [ ] Training Run ID;
- [ ] base model;
- [ ] provider;
- [ ] dataset versions;
- [ ] hyperparameters;
- [ ] infrastructure;
- [ ] access control;
- [ ] artifact integrity.

## Evaluation

- [ ] baseline;
- [ ] holdout;
- [ ] regression;
- [ ] safety;
- [ ] security;
- [ ] privacy;
- [ ] bias;
- [ ] performance;
- [ ] cost.

## Release

- [ ] acceptance criteria;
- [ ] approval;
- [ ] model registry;
- [ ] model card;
- [ ] alias;
- [ ] canary/shadow when applicable;
- [ ] rollback;
- [ ] observability.

## Lifecycle

- [ ] drift monitoring;
- [ ] retraining triggers;
- [ ] change management;
- [ ] evidence;
- [ ] deletion;
- [ ] decommission.

---

# 117. Documentos Relacionados

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
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 118. Princípios Finais

Fine-tuning não é apenas uma configuração avançada.

Ele cria um novo artefato comportamental que precisa ser governado.

```text
Data
→ Training
→ Model Behavior
→ Production Impact
```

O princípio central é:

```text
Know the data.

Know the rights.

Know the lineage.

Separate evaluation data.

Version every artifact.

Evaluate against baseline.

Promote through gates.

Monitor after release.

Retire deliberately.
```

No GereIgreja, datasets e modelos customizados deverão ser tratados como ativos de engenharia governados durante todo o lifecycle.

---

# 119. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`25-Governanca-de-Datasets-Sinteticos-Fine-Tuning-e-Customizacao-de-Modelos.md`

**Documento**

`GAI-25`

**Código**

`GAI-AI-SYNTHETIC-DATA-FINETUNING-MODEL-CUSTOMIZATION`

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

`GAI-24 — Transparência, Explicabilidade e Comunicação de Inteligência Artificial`

**Próximo documento candidato**

`26-Red-Teaming-Adversarial-Testing-e-Seguranca-Ofensiva-de-IA.md`
