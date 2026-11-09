Pasta:

docs/ai/

Arquivo:

16-Gestao-de-Riscos-de-Terceiros-e-Providers-de-IA.md

Documento:

GAI-16

Código:

GAI-AI-THIRD-PARTY-PROVIDER-RISK

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

# GAI-16 — Gestão de Riscos de Terceiros e Providers de Inteligência Artificial

> "A terceirização do processamento não terceiriza a responsabilidade sobre segurança, privacidade, disponibilidade e governança."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Conceito de Terceiro de IA
6. Categorias de Terceiros
7. Provider Registry
8. Provider ID
9. Owner
10. Finalidade
11. Serviços Utilizados
12. Casos de Uso
13. Classificação de Risco
14. Due Diligence
15. Segurança
16. Privacidade
17. Proteção de Dados
18. LGPD
19. Retenção
20. Uso para Treinamento
21. Residência de Dados
22. Transferência Internacional
23. Subprocessadores
24. Criptografia
25. Identidade e Acesso
26. API Keys
27. Service Accounts
28. Segregação de Ambientes
29. Logging do Provider
30. Auditoria
31. Certificações
32. Vulnerabilidades
33. Gestão de Incidentes
34. Notificação de Incidentes
35. Disponibilidade
36. SLA
37. SLO Interno
38. Rate Limits
39. Quotas
40. Capacity Risk
41. Performance
42. Latência
43. Dependência Externa
44. Vendor Lock-in
45. Portabilidade
46. Provider Adapter
47. Multi-Provider
48. Fallback
49. Failover
50. Data Compatibility
51. Model Compatibility
52. Prompt Compatibility
53. Tool Compatibility
54. Structured Output Compatibility
55. Embeddings
56. Vector Services
57. Hosted Models
58. SaaS de IA
59. Open Source Hospedado
60. Modelos Self-Hosted
61. Marketplace
62. Plugins e Extensões
63. Integrações de Terceiros
64. Supply Chain
65. SDKs
66. Bibliotecas
67. Dependências Transitivas
68. Atualizações
69. Breaking Changes
70. Model Deprecation
71. API Deprecation
72. Provider Policy Changes
73. Pricing Changes
74. Contract Risk
75. Terms of Service
76. DPA
77. Confidentiality
78. Intellectual Property
79. Data Ownership
80. Output Ownership
81. Compliance
82. Geographic Restrictions
83. Business Continuity
84. Exit Strategy
85. Migration Plan
86. Data Deletion
87. Offboarding
88. Evidence
89. Provider Review
90. Continuous Monitoring
91. Risk Signals
92. Risk Acceptance
93. Exceptions
94. Approval
95. Reassessment
96. Incident Response
97. Emergency Disable
98. Provider Kill Switch
99. Cost Exposure
100. Budget Exposure
101. Abuse
102. Fraud
103. Observabilidade
104. Métricas
105. Inventário
106. Production Readiness
107. Templates
108. Anti-Padrões
109. Arquitetura Consolidada
110. Checklist
111. Documentos Relacionados
112. Princípios Finais
113. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para avaliação, aprovação, monitoramento e encerramento de terceiros e providers utilizados por capacidades de Inteligência Artificial no GereIgreja.

O objetivo é controlar riscos introduzidos por serviços externos sem transferir indevidamente a responsabilidade da plataforma.

---

# 2. Escopo

Aplica-se a:

- providers de modelos;
- APIs de IA;
- serviços de embeddings;
- vector databases gerenciados;
- serviços de avaliação;
- plataformas de agentes;
- serviços multimodais;
- SDKs críticos;
- marketplaces;
- integrações externas que processem dados relacionados à IA.

---

# 3. Relação com a Família GAI

```text
GAI-02
Providers / Models / Gateway
        │
        ▼
GAI-06 / GAI-07
Security / Privacy / Data
        │
        ▼
GAI-12 / GAI-13
Inventory / Configuration
        │
        ▼
GAI-15
Cost / Capacity
        │
        ▼
GAI-16
Third-Party / Provider Risk
```

---

# 4. Princípios Fundamentais

Aplicar:

- approved providers only;
- risk-based due diligence;
- minimum necessary data;
- contractual clarity;
- provider isolation;
- continuous monitoring;
- exit readiness;
- no implicit fallback;
- auditable decisions;
- shared responsibility awareness.

---

# 5. Conceito de Terceiro de IA

É qualquer organização, serviço ou componente externo que processe, armazene, transporte ou influencie materialmente workloads de IA.

---

# 6. Categorias de Terceiros

Exemplos:

```text
MODEL_PROVIDER
EMBEDDING_PROVIDER
VECTOR_SERVICE
AI_SAAS
EVALUATION_SERVICE
OBSERVABILITY_SERVICE
TOOL_PROVIDER
SDK_VENDOR
MARKETPLACE
```

---

# 7. Provider Registry

Todo provider de produção deverá estar registrado conforme GAI-12.

---

# 8. Provider ID

Formato sugerido:

```text
AI-PROVIDER-###
```

---

# 9. Owner

Todo relacionamento deverá possuir owner interno.

---

# 10. Finalidade

Registrar por que o terceiro é necessário.

---

# 11. Serviços Utilizados

Não aprovar genericamente toda a oferta de um fornecedor.

Registrar serviços efetivamente autorizados.

---

# 12. Casos de Uso

Relacionar providers aos casos de uso do GAI-11.

---

# 13. Classificação de Risco

Considerar:

- sensibilidade dos dados;
- criticidade;
- autonomia;
- dependência;
- alcance;
- substituibilidade.

---

# 14. Due Diligence

Antes de production, realizar avaliação proporcional ao risco.

---

# 15. Segurança

Avaliar práticas de segurança relevantes ao serviço contratado.

---

# 16. Privacidade

Avaliar tratamento de dados pessoais.

---

# 17. Proteção de Dados

Identificar:

```text
data sent
data stored
data logged
data derived
data retained
```

---

# 18. LGPD

O uso deverá ser compatível com requisitos jurídicos e políticas internas aplicáveis.

---

# 19. Retenção

Conhecer prazos e opções de retenção.

---

# 20. Uso para Treinamento

Determinar se inputs, outputs ou metadados poderão ser utilizados pelo provider para treinamento ou melhoria.

Configurações contratuais e técnicas deverão ser verificadas.

---

# 21. Residência de Dados

Registrar regiões de processamento ou armazenamento quando relevantes.

---

# 22. Transferência Internacional

Avaliar quando dados forem processados fora da jurisdição aplicável.

---

# 23. Subprocessadores

Conhecer subprocessadores relevantes quando exigido por risco ou contrato.

---

# 24. Criptografia

Avaliar proteção:

- in transit;
- at rest;
- key management quando aplicável.

---

# 25. Identidade e Acesso

Preferir mecanismos corporativos e controlados.

---

# 26. API Keys

Chaves deverão:

- permanecer em secret management;
- possuir owner;
- ser rotacionáveis;
- possuir escopo mínimo.

---

# 27. Service Accounts

Usar identidades dedicadas quando suportado.

---

# 28. Segregação de Ambientes

Separar credenciais e projetos de development, staging e production quando apropriado.

---

# 29. Logging do Provider

Conhecer quais dados podem aparecer em logs externos.

---

# 30. Auditoria

Avaliar evidências disponíveis para atividades administrativas e acessos.

---

# 31. Certificações

Certificações podem apoiar due diligence, mas não substituem análise do serviço e configuração utilizados.

---

# 32. Vulnerabilidades

Avaliar processo do fornecedor para vulnerabilidades e correções.

---

# 33. Gestão de Incidentes

Conhecer processo de resposta do terceiro.

---

# 34. Notificação de Incidentes

Contratos de maior risco deverão definir expectativas de notificação quando aplicável.

---

# 35. Disponibilidade

Avaliar histórico e arquitetura de disponibilidade.

---

# 36. SLA

SLA externo não substitui SLO interno.

---

# 37. SLO Interno

A plataforma deverá definir objetivo compatível com dependências reais.

---

# 38. Rate Limits

Registrar limites conhecidos.

---

# 39. Quotas

Quotas externas deverão entrar no capacity planning.

---

# 40. Capacity Risk

Provider poderá ser gargalo da plataforma.

---

# 41. Performance

Avaliar performance no workload real.

---

# 42. Latência

Considerar regiões, rede e processamento.

---

# 43. Dependência Externa

Quanto maior a criticidade, maior a necessidade de estratégia de contingência.

---

# 44. Vendor Lock-in

Avaliar lock-in em:

- APIs;
- prompts;
- formatos;
- embeddings;
- tools;
- datasets;
- modelos proprietários.

---

# 45. Portabilidade

Projetar abstrações apenas onde houver benefício real.

---

# 46. Provider Adapter

Utilizar adapter conforme GAI-10.

---

# 47. Multi-Provider

Multi-provider deverá ser decisão arquitetural, não requisito automático.

---

# 48. Fallback

Provider alternativo deverá ser previamente aprovado para a mesma classe de dados e caso de uso.

---

# 49. Failover

Failover automático exige compatibilidade previamente validada.

---

# 50. Data Compatibility

Confirmar que o provider alternativo pode receber os mesmos dados.

---

# 51. Model Compatibility

Modelos podem produzir comportamento diferente.

---

# 52. Prompt Compatibility

Prompts deverão ser avaliados ao migrar modelos.

---

# 53. Tool Compatibility

Tool calling poderá possuir diferenças de schema e semântica.

---

# 54. Structured Output Compatibility

Validar comportamento real.

---

# 55. Embeddings

Mudança de embedding poderá exigir reindexação.

---

# 56. Vector Services

Avaliar isolamento, backup, exportação e exclusão.

---

# 57. Hosted Models

Aplicar due diligence ao host e ao modelo.

---

# 58. SaaS de IA

SaaS poderá possuir menos controle sobre pipeline interno.

Isso deverá ser refletido no risco.

---

# 59. Open Source Hospedado

Código aberto não elimina risco operacional do host.

---

# 60. Modelos Self-Hosted

Reduzem algumas dependências externas, mas transferem responsabilidades de:

- infraestrutura;
- patching;
- capacity;
- segurança;
- operação.

---

# 61. Marketplace

Artefatos de marketplace deverão ser avaliados antes do uso.

---

# 62. Plugins e Extensões

Não permitir extensões arbitrárias em agentes de produção.

---

# 63. Integrações de Terceiros

Toda integração com efeitos deverá seguir autorização determinística.

---

# 64. Supply Chain

Providers fazem parte da cadeia de fornecimento da plataforma.

---

# 65. SDKs

SDK oficial também é dependência de software e deverá seguir gestão de vulnerabilidades.

---

# 66. Bibliotecas

Evitar bibliotecas não mantidas para integrações críticas.

---

# 67. Dependências Transitivas

Avaliar por processos normais de supply chain.

---

# 68. Atualizações

Atualizações de SDK não deverão mudar comportamento crítico sem testes.

---

# 69. Breaking Changes

Monitorar changelogs e avisos do provider.

---

# 70. Model Deprecation

Registrar datas de depreciação conhecidas.

---

# 71. API Deprecation

Planejar migração antes de EOL.

---

# 72. Provider Policy Changes

Mudanças em políticas de dados ou uso deverão disparar revisão.

---

# 73. Pricing Changes

Relacionar ao GAI-15.

---

# 74. Contract Risk

Contratos deverão ser proporcionais à criticidade.

---

# 75. Terms of Service

Uso técnico deverá ser compatível com termos aplicáveis.

---

# 76. DPA

Data Processing Agreement deverá ser avaliado quando aplicável.

---

# 77. Confidentiality

Verificar proteção de informações confidenciais.

---

# 78. Intellectual Property

Avaliar direitos e restrições relevantes.

---

# 79. Data Ownership

A propriedade e controle dos dados deverão permanecer claros.

---

# 80. Output Ownership

Avaliar condições aplicáveis ao uso dos outputs.

---

# 81. Compliance

Mapear requisitos regulatórios e contratuais relevantes.

---

# 82. Geographic Restrictions

Alguns serviços ou modelos poderão possuir restrições geográficas.

---

# 83. Business Continuity

Providers críticos deverão entrar no planejamento de continuidade.

---

# 84. Exit Strategy

Todo provider crítico deverá possuir estratégia de saída.

---

# 85. Migration Plan

Definir:

```text
replacement
data export
configuration migration
prompt validation
evaluation
cutover
rollback
```

---

# 86. Data Deletion

Conhecer mecanismo de exclusão de dados externos.

---

# 87. Offboarding

Ao encerrar relacionamento:

- revogar credenciais;
- desativar integrações;
- excluir dados quando aplicável;
- atualizar inventário;
- remover dependências.

---

# 88. Evidence

Manter evidências proporcionais ao risco.

Exemplos:

- security review;
- privacy review;
- contract review;
- architecture decision;
- evaluation;
- approval.

---

# 89. Provider Review

Providers críticos deverão ser revisados periodicamente.

---

# 90. Continuous Monitoring

Monitorar mudanças relevantes em:

- segurança;
- disponibilidade;
- modelos;
- políticas;
- preços;
- APIs.

---

# 91. Risk Signals

Exemplos:

```text
security incident
major outage
policy change
unexpected retention
model retirement
pricing spike
support degradation
```

---

# 92. Risk Acceptance

Risco residual deverá possuir owner e aprovação quando necessário.

---

# 93. Exceptions

Exceções deverão possuir prazo e justificativa.

---

# 94. Approval

Aprovação deverá considerar risco do provider e dos casos de uso.

---

# 95. Reassessment

Reavaliar quando ocorrer:

- novo serviço;
- nova classe de dados;
- novo contrato;
- incidente;
- mudança material de política;
- aumento de criticidade.

---

# 96. Incident Response

Incidentes do provider deverão ser tratados como incidentes de dependência externa.

---

# 97. Emergency Disable

Deverá existir caminho operacional para interromper o uso quando necessário.

---

# 98. Provider Kill Switch

Poderá atuar no AI Gateway ou configuração central.

---

# 99. Cost Exposure

Provider comprometido ou mal configurado pode gerar custo anormal.

---

# 100. Budget Exposure

Aplicar budgets e quotas conforme GAI-15.

---

# 101. Abuse

Credenciais comprometidas deverão poder ser revogadas rapidamente.

---

# 102. Fraud

Monitorar padrões incompatíveis com uso esperado.

---

# 103. Observabilidade

Telemetria deverá identificar provider e modelo sem expor secrets.

---

# 104. Métricas

Exemplos:

```text
ai_provider_requests_total
ai_provider_errors_total
ai_provider_latency
ai_provider_throttle_total
ai_provider_fallback_total
ai_provider_cost
ai_provider_incidents
ai_provider_deprecation_days
```

---

# 105. Inventário

Todos os providers aprovados deverão estar no GAI-12.

---

# 106. Production Readiness

Antes de utilizar terceiro em production:

```text
registered?
owner?
risk classified?
security reviewed?
privacy reviewed?
data profile known?
retention known?
training usage known?
regions known?
contract adequate?
limits known?
fallback policy?
exit strategy?
```

---

# 107. Templates

## Provider Risk Record

```text
Provider ID:
Provider:
Owner:
Service:

Use Cases:
Risk Level:

Data Classes:
Personal Data:
Sensitive Data:

Retention:
Training Usage:
Processing Regions:
Subprocessors:

Security Review:
Privacy Review:
Contract Review:

SLA:
Rate Limits:
Quotas:

Model/API Deprecation Policy:
Fallback Provider:
Exit Strategy:

Evidence:
Approval:
Last Review:
Next Review:
Status:
```

## Provider Exit Plan

```text
Provider:
Owner:
Reason:

Replacement:
Affected Use Cases:
Affected Assets:

Data Export:
Data Deletion:
Credential Revocation:

Prompt Migration:
Model Migration:
Embedding Migration:
Evaluation Plan:

Cutover:
Rollback:
Completion Criteria:
```

---

# 108. Anti-Padrões

Evitar:

```text
developer API key
→ production
```

---

```text
fallback
→ unknown provider
```

---

```text
provider approved
for every possible data class
```

---

```text
Terms of Service accepted
=
security review complete
```

---

```text
certification badge
=
zero risk
```

---

```text
provider outage
→ unlimited retries
```

---

```text
critical provider
without exit plan
```

---

```text
new model
automatically enabled
```

---

```text
provider policy changes
never reviewed
```

---

# 109. Arquitetura Consolidada

```text
                      AI USE CASE
                          │
                          ▼
                    RISK CLASSIFICATION
                          │
                          ▼
                    PROVIDER SELECTION
                          │
                          ▼
                      DUE DILIGENCE
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
       SECURITY        PRIVACY         CONTRACT
          │               │               │
          └───────────────┼───────────────┘
                          ▼
                       APPROVAL
                          │
                          ▼
                     AI GATEWAY
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
             PRIMARY            APPROVED
             PROVIDER           FALLBACK
                │                   │
                └─────────┬─────────┘
                          ▼
                     OBSERVABILITY
                          │
                          ▼
                  CONTINUOUS REVIEW
                          │
                          ▼
                    EXIT READINESS
```

---

# 110. Checklist

## Registro

- [ ] Provider ID;
- [ ] owner;
- [ ] serviço;
- [ ] casos de uso;
- [ ] risco;
- [ ] status.

## Segurança

- [ ] due diligence;
- [ ] encryption;
- [ ] access controls;
- [ ] API key governance;
- [ ] incident process;
- [ ] vulnerability process.

## Privacidade

- [ ] data classes;
- [ ] retenção;
- [ ] training usage;
- [ ] regiões;
- [ ] subprocessadores;
- [ ] exclusão.

## Operação

- [ ] SLA;
- [ ] rate limits;
- [ ] quotas;
- [ ] capacity;
- [ ] latency;
- [ ] fallback;
- [ ] failover.

## Supply Chain

- [ ] SDKs;
- [ ] dependencies;
- [ ] updates;
- [ ] breaking changes;
- [ ] deprecation monitoring.

## Contratos

- [ ] terms;
- [ ] DPA quando aplicável;
- [ ] confidentiality;
- [ ] IP;
- [ ] ownership;
- [ ] compliance.

## Continuidade

- [ ] exit strategy;
- [ ] migration plan;
- [ ] data export;
- [ ] data deletion;
- [ ] credential revocation;
- [ ] provider kill switch.

## Governança

- [ ] evidence;
- [ ] approval;
- [ ] periodic review;
- [ ] risk acceptance;
- [ ] exceptions;
- [ ] inventory updated.

---

# 111. Documentos Relacionados

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
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 112. Princípios Finais

A integração com um provider cria uma extensão da superfície operacional da plataforma.

```text
External Service
≠
External Responsibility
```

O princípio central é:

```text
Know the provider.

Know the data.

Know the contract.

Know the dependency.

Know the fallback.

Know the exit.
```

No GereIgreja, nenhum terceiro de IA deverá se tornar uma dependência crítica invisível, irreversível ou sem owner.

---

# 113. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`16-Gestao-de-Riscos-de-Terceiros-e-Providers-de-IA.md`

**Documento**

`GAI-16`

**Código**

`GAI-AI-THIRD-PARTY-PROVIDER-RISK`

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

`GAI-15 — Gestão de Custos, Capacidade e FinOps de Inteligência Artificial`

**Próximo documento candidato**

`17-Gestao-de-Incidentes-Continuidade-e-Recuperacao-de-IA.md`
