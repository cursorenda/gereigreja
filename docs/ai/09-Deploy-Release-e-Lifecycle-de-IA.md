Pasta:

docs/ai/

Arquivo:

09-Deploy-Release-e-Lifecycle-de-IA.md

Documento:

GAI-09

Código:

GAI-AI-DEPLOY-RELEASE-LIFECYCLE

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

# GAI-09 — Deploy, Release e Lifecycle de Inteligência Artificial

> "Uma capacidade de IA em produção precisa ser versionável, promovível, reversível, observável e desativável."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. O que Constitui uma Release de IA
6. Artefatos de Release
7. Versionamento
8. Identidade de Configuração
9. Ambientes
10. Development
11. Staging
12. Production
13. Paridade entre Ambientes
14. Configuração por Ambiente
15. Secrets
16. Providers por Ambiente
17. Modelos por Ambiente
18. Prompts por Ambiente
19. Knowledge Bases por Ambiente
20. Tools por Ambiente
21. Agentes por Ambiente
22. Pipeline de Promoção
23. Quality Gates
24. Aprovação
25. Release Candidate
26. Deploy
27. Release
28. Configuração sem Deploy
29. Mudanças de Prompt
30. Mudanças de Modelo
31. Mudanças de Provider
32. Mudanças de Routing
33. Mudanças de RAG
34. Mudanças de Embeddings
35. Mudanças de Vector Store
36. Mudanças de Tools
37. Mudanças de Agentes
38. Mudanças de Guardrails
39. Feature Flags
40. Canary Release
41. Progressive Delivery
42. Shadow Mode
43. Dark Launch
44. A/B Testing
45. Tenant-Based Rollout
46. Internal Rollout
47. Rollback
48. Rollback de Prompt
49. Rollback de Modelo
50. Rollback de RAG
51. Rollback de Agent Policy
52. Kill Switch
53. Safe Defaults
54. Compatibilidade
55. Migrações
56. Reindexação
57. Estado Persistido
58. Sessões
59. Memória de Agentes
60. Jobs em Execução
61. Backward Compatibility
62. Depreciação
63. Model Deprecation
64. Provider Deprecation
65. Prompt Deprecation
66. Tool Deprecation
67. Knowledge Base Deprecation
68. Lifecycle States
69. Experimental
70. Beta
71. Production
72. Deprecated
73. Disabled
74. End of Life
75. Ownership
76. Change Management
77. Change Record
78. Release Notes
79. Auditoria
80. Observabilidade
81. Métricas de Release
82. Comparação Pré/Pós-Release
83. Quality Regression
84. Cost Regression
85. Latency Regression
86. Security Regression
87. Incident Response
88. Automatic Rollback
89. Manual Rollback
90. Provider Outage
91. Emergency Change
92. CI/CD
93. Infrastructure as Code
94. Configuration as Code
95. Prompt as Code
96. Evaluation as Code
97. Reprodutibilidade
98. Supply Chain
99. Production Readiness
100. Post-Release Review
101. Revisões Periódicas
102. Anti-Padrões
103. Arquitetura Consolidada
104. Checklist
105. Documentos Relacionados
106. Princípios Finais
107. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para deploy, release, promoção, rollback, depreciação e lifecycle das capacidades de Inteligência Artificial do GereIgreja.

O objetivo é garantir que mudanças comportamentais de IA sejam tratadas como mudanças de produção mesmo quando não exigem alteração tradicional de código.

---

# 2. Escopo

Aplica-se a mudanças em:

- providers;
- modelos;
- prompts;
- routing;
- RAG;
- embeddings;
- vector stores;
- datasets operacionais;
- tools;
- agentes;
- guardrails;
- políticas;
- configurações;
- AI Gateway.

---

# 3. Relação com a Família GAI

```text
GAI-01  Architecture / Governance
GAI-02  Providers / Models / Prompts
GAI-03  RAG / Knowledge
GAI-04  Tools / Agents
GAI-05  Evaluation / Operations
GAI-06  Security / Privacy
GAI-07  Data Governance
GAI-08  Testing / Quality Gates
             │
             ▼
GAI-09
Deploy / Release / Lifecycle
```

O GAI-09 define como uma mudança aprovada chega à produção e como pode ser revertida ou encerrada.

---

# 4. Princípios Fundamentais

Aplicar:

- explicit versioning;
- controlled promotion;
- immutable release identity;
- progressive rollout;
- rollback readiness;
- observable change;
- lifecycle ownership;
- secure configuration;
- reproducibility;
- fail-safe deployment.

---

# 5. O que Constitui uma Release de IA

Uma release de IA não é apenas novo código.

Podem alterar comportamento:

```text
Prompt
Model
Provider
Routing
Retrieval
Embedding
Tool
Agent Policy
Guardrail
Configuration
```

Qualquer uma dessas mudanças poderá exigir processo de release.

---

# 6. Artefatos de Release

Uma release deverá identificar os artefatos relevantes.

Exemplo conceitual:

```text
application_commit
prompt_version
model_id
provider
routing_version
retrieval_config
tool_registry_version
agent_policy_version
evaluation_version
```

---

# 7. Versionamento

Componentes comportamentais relevantes deverão possuir versão ou identificador reproduzível.

---

# 8. Identidade de Configuração

Deverá ser possível determinar qual configuração estava ativa em uma execução.

---

# 9. Ambientes

Manter separação entre ambientes.

---

# 10. Development

Adequado para experimentação controlada.

---

# 11. Staging

Deverá representar o comportamento de produção o suficiente para validação.

---

# 12. Production

Somente artefatos aprovados deverão ser ativados.

---

# 13. Paridade entre Ambientes

Diferenças inevitáveis deverão ser documentadas.

---

# 14. Configuração por Ambiente

Configuração deverá ser explícita e rastreável.

---

# 15. Secrets

Secrets não deverão fazer parte do artefato versionado.

---

# 16. Providers por Ambiente

Providers diferentes poderão ser utilizados, desde que diferenças sejam conhecidas e testadas.

---

# 17. Modelos por Ambiente

Quando staging utiliza modelo diferente de production, o risco de divergência deverá ser considerado.

---

# 18. Prompts por Ambiente

Prompts candidatos deverão possuir versão.

---

# 19. Knowledge Bases por Ambiente

Dados de production não deverão ser copiados indiscriminadamente para ambientes inferiores.

---

# 20. Tools por Ambiente

Tools destrutivas poderão ser substituídas por fakes ou ambientes seguros fora de production.

---

# 21. Agentes por Ambiente

Limites de agentes deverão permanecer explícitos em cada ambiente.

---

# 22. Pipeline de Promoção

Fluxo recomendado:

```text
Change
  ↓
Development
  ↓
Tests
  ↓
Evaluation
  ↓
Security
  ↓
Staging
  ↓
Quality Gate
  ↓
Release Candidate
  ↓
Controlled Production Rollout
```

---

# 23. Quality Gates

Aplicar GAI-08.

Nenhuma promoção deverá contornar gates críticos sem waiver formal.

---

# 24. Aprovação

Mudanças de maior risco deverão possuir aprovação proporcional.

---

# 25. Release Candidate

Uma release candidate deverá possuir identidade congelada suficiente para avaliação.

---

# 26. Deploy

Deploy é disponibilização técnica do artefato.

---

# 27. Release

Release é ativação do comportamento para usuários ou tenants.

Deploy e release poderão ocorrer em momentos diferentes.

---

# 28. Configuração sem Deploy

Alterações remotas de configuração ainda podem constituir release.

---

# 29. Mudanças de Prompt

Deverão possuir:

- versão;
- avaliação;
- rollback;
- owner.

---

# 30. Mudanças de Modelo

Deverão considerar:

- qualidade;
- custo;
- latência;
- contexto;
- tool support;
- structured output;
- segurança.

---

# 31. Mudanças de Provider

Exigem avaliação operacional, de segurança e privacidade.

---

# 32. Mudanças de Routing

Routing deverá possuir configuração rastreável.

---

# 33. Mudanças de RAG

Mudanças de retrieval podem modificar respostas sem alterar modelo.

---

# 34. Mudanças de Embeddings

Podem exigir reindexação e avaliação de compatibilidade.

---

# 35. Mudanças de Vector Store

Deverão preservar isolamento, metadata e lifecycle.

---

# 36. Mudanças de Tools

Mudanças de contrato ou efeito exigem compatibilidade e testes.

---

# 37. Mudanças de Agentes

Alterações em tools, limites ou autonomia deverão ser consideradas mudanças de risco.

---

# 38. Mudanças de Guardrails

Redução de proteção deverá receber revisão explícita.

---

# 39. Feature Flags

Feature flags são mecanismo preferencial para separar deploy de release quando apropriado.

---

# 40. Canary Release

Liberar inicialmente para pequena população.

---

# 41. Progressive Delivery

Expandir rollout conforme sinais permanecem saudáveis.

```text
1%
→ 5%
→ 25%
→ 50%
→ 100%
```

Percentuais são ilustrativos e deverão ser definidos por risco.

---

# 42. Shadow Mode

Nova configuração poderá receber tráfego de comparação sem controlar a resposta final.

Deverá respeitar privacidade e custos.

---

# 43. Dark Launch

Infraestrutura poderá ser implantada antes da exposição funcional.

---

# 44. A/B Testing

Utilizar somente depois de requisitos mínimos de segurança terem sido aprovados.

---

# 45. Tenant-Based Rollout

Em arquitetura multi-tenant, rollout poderá ocorrer por tenant ou grupo controlado de tenants.

---

# 46. Internal Rollout

Preferir validação interna antes de exposição ampla para recursos de maior risco.

---

# 47. Rollback

Toda mudança relevante deverá possuir estratégia de reversão quando tecnicamente possível.

---

# 48. Rollback de Prompt

Manter versão anterior disponível durante janela adequada.

---

# 49. Rollback de Modelo

Considerar disponibilidade do modelo anterior e compatibilidade.

---

# 50. Rollback de RAG

Pode exigir restauração de:

- embedding model;
- index;
- retrieval configuration;
- reranker.

---

# 51. Rollback de Agent Policy

Deverá permitir restaurar tools e limites anteriores.

---

# 52. Kill Switch

Recursos de risco elevado deverão possuir caminho rápido de desativação.

---

# 53. Safe Defaults

Quando configuração estiver ausente ou inválida, preferir comportamento seguro.

---

# 54. Compatibilidade

Mudanças deverão considerar compatibilidade entre componentes.

---

# 55. Migrações

Mudanças estruturais poderão exigir migração controlada.

---

# 56. Reindexação

Reindexação deverá ser planejada como operação de release quando alterar comportamento.

---

# 57. Estado Persistido

Mudanças deverão considerar dados persistidos por versões anteriores.

---

# 58. Sessões

Sessões iniciadas antes de uma release poderão carregar configuração antiga.

Definir política quando relevante.

---

# 59. Memória de Agentes

Mudanças de formato ou política deverão considerar memória existente.

---

# 60. Jobs em Execução

Long-running jobs deverão possuir política para mudanças durante execução.

---

# 61. Backward Compatibility

Contratos internos deverão preservar compatibilidade quando necessário.

---

# 62. Depreciação

Todo componente removido deverá possuir plano quando houver dependentes.

---

# 63. Model Deprecation

Monitorar anúncios e lifecycle dos providers.

---

# 64. Provider Deprecation

Planejar migração antes de encerramento do serviço.

---

# 65. Prompt Deprecation

Prompts antigos deverão ser removidos após janela segura.

---

# 66. Tool Deprecation

Tool deprecated não deverá permanecer indefinidamente exposta a agentes.

---

# 67. Knowledge Base Deprecation

Bases antigas deverão ser retiradas do retrieval ativo.

---

# 68. Lifecycle States

Estados recomendados:

```text
EXPERIMENTAL
BETA
PRODUCTION
DEPRECATED
DISABLED
END_OF_LIFE
```

---

# 69. Experimental

Uso restrito e sem garantia de estabilidade.

---

# 70. Beta

Uso controlado com observação reforçada.

---

# 71. Production

Aprovado para operação regular.

---

# 72. Deprecated

Ainda disponível temporariamente, mas com substituição planejada.

---

# 73. Disabled

Não disponível para execução.

---

# 74. End of Life

Componente removido do ciclo operacional.

---

# 75. Ownership

Cada componente deverá possuir owner responsável pelo lifecycle.

---

# 76. Change Management

Mudanças relevantes deverão ser rastreáveis.

---

# 77. Change Record

Registrar quando necessário:

- motivo;
- owner;
- artefatos;
- avaliação;
- risco;
- rollout;
- rollback.

---

# 78. Release Notes

Mudanças relevantes deverão possuir resumo técnico adequado.

---

# 79. Auditoria

Deverá ser possível identificar quando uma configuração entrou ou saiu de produção.

---

# 80. Observabilidade

Release deverá gerar marcador ou dimensão de versão na telemetria quando possível.

---

# 81. Métricas de Release

Comparar antes e depois:

- success rate;
- quality;
- latency;
- errors;
- fallback;
- tokens;
- cost.

---

# 82. Comparação Pré/Pós-Release

Uma release deverá possuir janela de observação proporcional ao risco.

---

# 83. Quality Regression

Queda de qualidade poderá exigir rollback mesmo sem erro técnico.

---

# 84. Cost Regression

Aumento inesperado de custo poderá exigir contenção.

---

# 85. Latency Regression

Monitorar impacto na experiência.

---

# 86. Security Regression

Qualquer regressão de autorização, tenant ou guardrail crítico deverá bloquear ou reverter a release.

---

# 87. Incident Response

Releases deverão integrar o processo de incidentes.

---

# 88. Automatic Rollback

Poderá ser utilizado quando sinais forem suficientemente confiáveis.

---

# 89. Manual Rollback

Deverá permanecer documentado e acessível à equipe responsável.

---

# 90. Provider Outage

Mudanças emergenciais de provider ainda deverão preservar segurança e observabilidade.

---

# 91. Emergency Change

Mudanças emergenciais deverão ser registradas e revisadas posteriormente.

---

# 92. CI/CD

Automatizar:

- testes;
- evaluations;
- packaging;
- gates;
- promoção;

quando viável.

---

# 93. Infrastructure as Code

Infraestrutura de IA deverá seguir GINF.

---

# 94. Configuration as Code

Configurações críticas deverão ser versionadas quando apropriado.

---

# 95. Prompt as Code

Prompts relevantes deverão ser revisáveis, versionáveis e testáveis.

---

# 96. Evaluation as Code

Datasets, runners e thresholds deverão ser automatizáveis quando possível.

---

# 97. Reprodutibilidade

Uma release deverá ser reconstruível a partir dos artefatos registrados, dentro das limitações de providers externos.

---

# 98. Supply Chain

Release deverá considerar versões de:

- SDKs;
- adapters;
- libraries;
- models;
- providers.

---

# 99. Production Readiness

Antes da primeira release de uma feature:

- owner;
- avaliação;
- segurança;
- dados;
- observabilidade;
- custos;
- rollout;
- rollback;
- kill switch quando necessário;
- runbook.

---

# 100. Post-Release Review

Mudanças de maior risco poderão exigir revisão pós-release.

---

# 101. Revisões Periódicas

Revisar componentes em production para identificar:

- depreciação;
- custo;
- baixa utilização;
- qualidade;
- riscos;
- substituições.

---

# 102. Anti-Padrões

Evitar:

```text
prompt changed in production
without version
```

---

```text
latest model
=
automatic production upgrade
```

---

```text
deploy
=
release to everyone
```

---

```text
new embedding
→ overwrite old index
without rollback
```

---

```text
agent autonomy increased
without security review
```

---

```text
feature flag
without owner
```

---

```text
deprecated tool
available forever
```

---

```text
release
without telemetry marker
```

---

```text
production issue
→ no known previous version
```

---

# 103. Arquitetura Consolidada

```text
                         CHANGE
                           │
                           ▼
                       VERSION
                           │
                           ▼
                   TEST / EVALUATE
                           │
                           ▼
                     QUALITY GATE
                           │
                           ▼
                        STAGING
                           │
                           ▼
                  RELEASE CANDIDATE
                           │
                           ▼
                    FEATURE FLAG
                           │
                           ▼
                    CANARY / TENANT
                           │
                           ▼
                 PROGRESSIVE ROLLOUT
                           │
                           ▼
                       PRODUCTION
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           QUALITY       COST        SECURITY
              │            │            │
              └────────────┼────────────┘
                           ▼
                     RELEASE DECISION
                      │            │
                      ▼            ▼
                   CONTINUE     ROLLBACK
                                   │
                                   ▼
                               KILL SWITCH
                          when required
```

---

# 104. Checklist

## Versionamento

- [ ] prompt version;
- [ ] model ID;
- [ ] provider;
- [ ] routing;
- [ ] RAG config;
- [ ] tools;
- [ ] agent policy;
- [ ] evaluation version.

## Ambientes

- [ ] development;
- [ ] staging;
- [ ] production;
- [ ] diferenças conhecidas;
- [ ] secrets separados;
- [ ] dados protegidos.

## Gates

- [ ] testes;
- [ ] evaluation;
- [ ] security;
- [ ] privacy;
- [ ] cost;
- [ ] performance.

## Release

- [ ] release candidate;
- [ ] owner;
- [ ] feature flag;
- [ ] canary quando necessário;
- [ ] rollout controlado;
- [ ] telemetria.

## Rollback

- [ ] versão anterior;
- [ ] procedimento;
- [ ] compatibilidade;
- [ ] kill switch;
- [ ] incident path.

## Lifecycle

- [ ] estado;
- [ ] owner;
- [ ] depreciação;
- [ ] end of life;
- [ ] dependentes identificados.

## Operação

- [ ] comparação pré/pós;
- [ ] quality regression;
- [ ] cost regression;
- [ ] latency regression;
- [ ] security regression;
- [ ] post-release review quando necessário.

---

# 105. Documentos Relacionados

- GAI-01 — Arquitetura e Governança de Inteligência Artificial
- GAI-02 — Providers, Modelos, Prompts e AI Gateway
- GAI-03 — RAG, Contexto e Conhecimento
- GAI-04 — Ferramentas, Agentes e Ações Seguras
- GAI-05 — Avaliação, Observabilidade, Custos e Operação de IA
- GAI-06 — Segurança, Privacidade e Guardrails de IA
- GAI-07 — Governança de Dados para Inteligência Artificial
- GAI-08 — Testes e Quality Gates para Inteligência Artificial
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework
- GereIgreja Backend Engineering
- GereIgreja Data Engineering

---

# 106. Princípios Finais

Em sistemas de IA, comportamento pode mudar sem alteração no código da aplicação.

Por isso:

```text
Configuration Change
can be
Production Change
```

O princípio central é:

```text
Version it.
Test it.
Evaluate it.
Release it gradually.
Observe it.
Rollback it when needed.
Retire it deliberately.
```

Nenhum provider, modelo, prompt, índice, tool ou agente deverá se tornar uma dependência permanente apenas porque entrou em produção.

Toda capacidade de IA do GereIgreja deverá possuir lifecycle explícito.

---

# 107. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`09-Deploy-Release-e-Lifecycle-de-IA.md`

**Documento**

`GAI-09`

**Código**

`GAI-AI-DEPLOY-RELEASE-LIFECYCLE`

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

`GAI-08 — Testes e Quality Gates para Inteligência Artificial`

**Próximo documento candidato**

`10-Padroes-de-Implementacao-e-Referencia-de-IA.md`
