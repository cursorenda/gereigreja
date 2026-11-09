Pasta:

docs/ai/

Arquivo:

08-Testes-e-Quality-Gates-para-IA.md

Documento:

GAI-08

Código:

GAI-AI-TESTING-QUALITY-GATES

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

# GAI-08 — Testes e Quality Gates para Inteligência Artificial

> "Uma mudança de IA não deve chegar à produção apenas porque compila, responde ou parece funcionar."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Estratégia de Testes
6. Pirâmide de Testes para IA
7. Testes Determinísticos
8. Testes Não Determinísticos
9. Unit Tests
10. Contract Tests
11. Integration Tests
12. End-to-End Tests
13. Evaluation Tests
14. Regression Tests
15. Security Tests
16. Privacy Tests
17. Performance Tests
18. Cost Tests
19. Resilience Tests
20. Testes de Prompts
21. Testes de Modelos
22. Testes do AI Gateway
23. Testes de Structured Output
24. Testes de Parsing
25. Testes de RAG
26. Retrieval Precision
27. Retrieval Recall
28. Groundedness
29. Faithfulness
30. Empty Retrieval
31. Testes de Embeddings
32. Testes de Vector Store
33. Testes de Tools
34. Testes de Agentes
35. Task Completion
36. Tool Selection
37. Número de Passos
38. Loops
39. Confirmações
40. Idempotência
41. Testes Cross-Tenant
42. Testes de Autorização
43. Prompt Injection
44. Indirect Prompt Injection
45. Exfiltração
46. Tool Abuse
47. Dados Sensíveis
48. Testes de Guardrails
49. Datasets de Avaliação
50. Golden Sets
51. Casos Adversariais
52. Dados Sintéticos
53. Dados de Produção
54. Versionamento
55. Reprodutibilidade
56. Baseline
57. Métricas
58. Thresholds
59. Quality Gates
60. Gate de Pull Request
61. Gate de Staging
62. Gate de Produção
63. Mudança de Prompt
64. Mudança de Modelo
65. Mudança de Provider
66. Mudança de RAG
67. Mudança de Tool
68. Mudança de Agent Policy
69. CI/CD
70. Testes com Providers Reais
71. Mocks
72. Fakes
73. Fixtures
74. Flakiness
75. Repetição Estatística
76. LLM-as-Judge
77. Avaliação Humana
78. A/B Testing
79. Canary
80. Feature Flags
81. Shadow Testing
82. Performance
83. Latência
84. Concorrência
85. Tokens
86. Custos
87. Rate Limits
88. Timeouts
89. Retries
90. Fallback
91. Chaos e Falhas
92. Observabilidade dos Testes
93. Evidências
94. Relatórios
95. Defeitos e Regressões
96. Severidade
97. Waivers
98. Ownership
99. Production Readiness
100. Revisões Periódicas
101. Anti-Padrões
102. Arquitetura Consolidada
103. Checklist
104. Documentos Relacionados
105. Princípios Finais
106. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial de testes e Quality Gates para capacidades de Inteligência Artificial no GereIgreja.

O objetivo é garantir que mudanças em modelos, prompts, RAG, tools, agentes, providers e políticas sejam avaliadas antes e depois de chegar à produção.

---

# 2. Escopo

Aplica-se a:

- AI Gateway;
- providers;
- modelos;
- prompts;
- structured outputs;
- RAG;
- embeddings;
- vector stores;
- tools;
- agentes;
- guardrails;
- pipelines de dados para IA;
- funcionalidades completas de IA.

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
             │
             ▼
GAI-08
Testing / Quality Gates
```

O GAI-08 transforma os requisitos dos documentos anteriores em verificações repetíveis.

---

# 4. Princípios Fundamentais

Aplicar:

- test before production;
- deterministic controls first;
- representative evaluations;
- security as a gate;
- tenant isolation as a gate;
- regression detection;
- reproducibility;
- measurable thresholds;
- risk-based testing;
- evidence-based promotion.

---

# 5. Estratégia de Testes

Uma feature de IA deverá possuir estratégia proporcional ao risco.

Não existe um único teste suficiente.

---

# 6. Pirâmide de Testes para IA

```text
              E2E / HUMAN
             /           \
        EVALUATIONS / SECURITY
          /                 \
     INTEGRATION / CONTRACT
        /                 \
      UNIT / DETERMINISTIC
```

A maior quantidade possível de regras controláveis deverá permanecer em testes determinísticos.

---

# 7. Testes Determinísticos

Adequados para:

- autorização;
- tenant;
- schemas;
- parsing;
- filtros;
- limites;
- routing;
- tool policies;
- idempotência.

---

# 8. Testes Não Determinísticos

Utilizados para comportamento probabilístico.

Devem usar:

- datasets;
- métricas;
- thresholds;
- múltiplas execuções quando necessário.

---

# 9. Unit Tests

Testar componentes isolados sem provider real sempre que possível.

---

# 10. Contract Tests

Validar contratos entre:

- AI Service e Gateway;
- Gateway e adapters;
- tools e services;
- retrieval e Context Builder.

---

# 11. Integration Tests

Validar interação entre componentes reais controlados.

---

# 12. End-to-End Tests

Validar fluxos críticos completos.

Não deverão ser a única camada de testes.

---

# 13. Evaluation Tests

Avaliam qualidade comportamental sobre datasets definidos.

---

# 14. Regression Tests

Comparam mudança contra baseline anterior.

---

# 15. Security Tests

Aplicar GAI-06 e GSF.

---

# 16. Privacy Tests

Verificar:

- minimização;
- retenção;
- logging;
- isolamento;
- exposição a provider.

---

# 17. Performance Tests

Avaliar latência e throughput.

---

# 18. Cost Tests

Mudanças poderão ser bloqueadas quando custo exceder limites definidos sem justificativa.

---

# 19. Resilience Tests

Simular falhas previsíveis.

---

# 20. Testes de Prompts

Cobrir:

- caso normal;
- ambiguidade;
- falta de contexto;
- input hostil;
- formato inesperado;
- recusa adequada.

---

# 21. Testes de Modelos

Uma troca de modelo deverá avaliar comportamento, não apenas compatibilidade de API.

---

# 22. Testes do AI Gateway

Testar:

- routing;
- timeout;
- retry;
- fallback;
- erros;
- métricas;
- normalização.

---

# 23. Testes de Structured Output

Verificar schema compliance.

---

# 24. Testes de Parsing

Parsing inválido deverá falhar de forma segura.

---

# 25. Testes de RAG

Aplicar GAI-03.

---

# 26. Retrieval Precision

Medir proporção de resultados recuperados que são relevantes.

---

# 27. Retrieval Recall

Medir capacidade de recuperar conhecimento relevante existente.

---

# 28. Groundedness

Avaliar se a resposta está apoiada no contexto.

---

# 29. Faithfulness

Avaliar se a resposta representa corretamente as fontes.

---

# 30. Empty Retrieval

Testar comportamento quando nenhuma evidência adequada é encontrada.

---

# 31. Testes de Embeddings

Mudanças de embedding deverão avaliar impacto no retrieval.

---

# 32. Testes de Vector Store

Testar:

- filtros;
- tenant;
- metadata;
- exclusão;
- atualização.

---

# 33. Testes de Tools

Testar cada tool independentemente do modelo.

---

# 34. Testes de Agentes

Avaliar trajetória e efeito final.

---

# 35. Task Completion

O agente deverá concluir corretamente a tarefa permitida.

---

# 36. Tool Selection

Avaliar se ferramentas adequadas são escolhidas.

---

# 37. Número de Passos

Detectar aumento injustificado de passos.

---

# 38. Loops

Testar interrupção de loops.

---

# 39. Confirmações

Ações que exigem aprovação não deverão executar antes da confirmação válida.

---

# 40. Idempotência

Testar retry e duplicidade em ações mutáveis.

---

# 41. Testes Cross-Tenant

São obrigatórios para funcionalidades tenant-scoped.

Exemplo mínimo:

```text
User A / Tenant A
asks for resource B / Tenant B
→ DENIED
```

---

# 42. Testes de Autorização

Cobrir permissões positivas e negativas.

---

# 43. Prompt Injection

Incluir casos explícitos de tentativa de sobrescrever instruções.

---

# 44. Indirect Prompt Injection

Inserir instruções adversariais em documentos e conteúdo recuperado.

---

# 45. Exfiltração

Testar tentativas de enviar dados para destinos não autorizados.

---

# 46. Tool Abuse

Testar uso de ferramenta fora do escopo.

---

# 47. Dados Sensíveis

Verificar que secrets e campos proibidos não chegam ao modelo.

---

# 48. Testes de Guardrails

Cada guardrail relevante deverá possuir casos positivos e negativos.

---

# 49. Datasets de Avaliação

Datasets deverão representar uso real e riscos conhecidos.

---

# 50. Golden Sets

Golden sets deverão possuir respostas ou critérios esperados controlados.

---

# 51. Casos Adversariais

Manter conjunto específico de ataques e edge cases.

---

# 52. Dados Sintéticos

Preferir dados sintéticos ou anonimizados quando possível.

---

# 53. Dados de Produção

Não copiar dados de produção para testes sem processo aprovado.

---

# 54. Versionamento

Versionar:

- dataset;
- prompt;
- modelo;
- retrieval configuration;
- evaluator.

---

# 55. Reprodutibilidade

Uma avaliação deverá registrar configuração suficiente para repetição.

---

# 56. Baseline

Toda mudança relevante deverá ser comparável com uma baseline.

---

# 57. Métricas

Exemplos:

```text
task_success_rate
schema_valid_rate
groundedness_score
retrieval_precision
retrieval_recall
tool_success_rate
security_failure_rate
p95_latency
estimated_cost_per_request
```

---

# 58. Thresholds

Thresholds deverão ser explícitos e proporcionais ao risco.

---

# 59. Quality Gates

Um Quality Gate decide se a mudança pode avançar.

```text
Change
  ↓
Tests
  ↓
Evaluation
  ↓
Security
  ↓
Cost / Performance
  ↓
PASS or BLOCK
```

---

# 60. Gate de Pull Request

Poderá exigir:

- unit tests;
- contract tests;
- lint/type checks;
- deterministic security tests;
- evaluation subset.

---

# 61. Gate de Staging

Poderá exigir:

- integration;
- provider tests;
- full evaluation;
- adversarial tests;
- latency;
- cost.

---

# 62. Gate de Produção

Antes de promoção:

- baseline aceita;
- regressões analisadas;
- segurança aprovada;
- owner identificado;
- observabilidade pronta;
- rollback/kill path conhecido.

---

# 63. Mudança de Prompt

Prompt relevante alterado deverá disparar avaliação.

---

# 64. Mudança de Modelo

Modelo alterado deverá disparar regressão.

---

# 65. Mudança de Provider

Avaliar comportamento, erros, privacidade e performance.

---

# 66. Mudança de RAG

Alterações em chunking, embedding, ranking ou threshold exigem avaliação de retrieval.

---

# 67. Mudança de Tool

Exige contract, authorization e effect tests.

---

# 68. Mudança de Agent Policy

Mudanças de autonomia, tools ou limites exigem testes adversariais.

---

# 69. CI/CD

Quality Gates deverão ser automatizados quando tecnicamente viável.

---

# 70. Testes com Providers Reais

Deverão ser limitados e controlados.

Separar testes rápidos de testes externos mais caros.

---

# 71. Mocks

Mocks são adequados para interfaces específicas, mas não devem mascarar incompatibilidades importantes.

---

# 72. Fakes

Preferir fakes de contratos internos para grande parte dos testes.

---

# 73. Fixtures

Fixtures deverão ser legíveis e representar cenários reais.

---

# 74. Flakiness

Testes probabilísticos instáveis deverão ser identificados.

Não resolver flakiness simplesmente ignorando falhas.

---

# 75. Repetição Estatística

Alguns testes poderão exigir múltiplas execuções para medir taxa de sucesso.

---

# 76. LLM-as-Judge

Pode complementar avaliação, conforme GAI-05.

Não deverá ser o único gate para requisitos críticos de segurança.

---

# 77. Avaliação Humana

Utilizar para critérios subjetivos ou de alto impacto quando necessário.

---

# 78. A/B Testing

Somente após requisitos mínimos de segurança e qualidade terem sido satisfeitos.

---

# 79. Canary

Mudanças relevantes poderão ser liberadas para pequena parcela antes do rollout completo.

---

# 80. Feature Flags

Permitem desativação e comparação controlada.

---

# 81. Shadow Testing

Quando apropriado, executar nova configuração sem impactar a resposta ao usuário para comparação.

Deverá respeitar privacidade e custos.

---

# 82. Performance

Testar experiência end-to-end.

---

# 83. Latência

Avaliar percentis relevantes.

---

# 84. Concorrência

Simular volume esperado quando necessário.

---

# 85. Tokens

Mudanças deverão monitorar impacto no consumo.

---

# 86. Custos

Avaliações deverão permitir detectar regressões financeiras relevantes.

---

# 87. Rate Limits

Testar comportamento ao atingir limites.

---

# 88. Timeouts

Testar provider e tool timeouts.

---

# 89. Retries

Validar política de retry.

---

# 90. Fallback

Testar explicitamente caminho de fallback.

---

# 91. Chaos e Falhas

Cenários úteis:

```text
provider unavailable
retrieval unavailable
vector store slow
tool timeout
malformed model output
rate limit
partial workflow failure
```

---

# 92. Observabilidade dos Testes

Resultados de avaliações automatizadas deverão ser rastreáveis.

---

# 93. Evidências

Guardar quando apropriado:

- versão;
- commit;
- dataset;
- configuração;
- métricas;
- resultado do gate.

Evitar persistir conteúdo sensível desnecessariamente.

---

# 94. Relatórios

Relatórios deverão destacar regressões e não apenas médias globais.

---

# 95. Defeitos e Regressões

Falhas relevantes deverão gerar item rastreável conforme processo de engenharia.

---

# 96. Severidade

Classificar falhas por impacto.

Segurança e cross-tenant possuem prioridade superior a pequenas diferenças estilísticas.

---

# 97. Waivers

Exceções a gates deverão ser raras, temporárias e registradas.

Devem possuir:

- justificativa;
- owner;
- risco;
- prazo;
- aprovação adequada.

---

# 98. Ownership

Cada suíte relevante deverá possuir owner.

---

# 99. Production Readiness

Nenhuma feature de IA relevante deverá entrar em produção apenas com testes manuais informais.

---

# 100. Revisões Periódicas

Datasets e thresholds deverão ser revisados conforme o produto evolui.

---

# 101. Anti-Padrões

Evitar:

```text
one prompt
tested manually once
→ production
```

---

```text
model upgrade
without regression suite
```

---

```text
cross-tenant
tested only by happy path
```

---

```text
LLM-as-Judge
=
security authority
```

---

```text
flaky evaluation
→ ignored forever
```

---

```text
cost regression
→ discovered on invoice
```

---

```text
provider mock
as only integration test
```

---

```text
quality gate
without threshold
```

---

```text
production data
copied freely
into test fixtures
```

---

# 102. Arquitetura Consolidada

```text
                         CHANGE
                           │
                           ▼
                    DETERMINISTIC TESTS
                           │
                           ▼
                     CONTRACT TESTS
                           │
                           ▼
                     AI EVALUATIONS
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
            QUALITY      SECURITY      COST
              │            │            │
              └────────────┼────────────┘
                           ▼
                     QUALITY GATE
                           │
                  ┌────────┴────────┐
                  ▼                 ▼
                BLOCK             PASS
                                    │
                                    ▼
                                 STAGING
                                    │
                                    ▼
                              CANARY / FLAG
                                    │
                                    ▼
                                PRODUCTION
                                    │
                                    ▼
                           ONLINE MONITORING
```

---

# 103. Checklist

## Estratégia

- [ ] risco classificado;
- [ ] unit tests;
- [ ] contract tests;
- [ ] integration tests;
- [ ] evaluations;
- [ ] adversarial tests.

## IA

- [ ] prompt;
- [ ] modelo;
- [ ] structured output;
- [ ] gateway;
- [ ] fallback.

## RAG

- [ ] precision;
- [ ] recall;
- [ ] groundedness;
- [ ] empty retrieval;
- [ ] tenant filters;
- [ ] exclusão.

## Tools e Agentes

- [ ] tool contracts;
- [ ] autorização;
- [ ] confirmações;
- [ ] idempotência;
- [ ] max steps;
- [ ] loops;
- [ ] task completion.

## Segurança

- [ ] cross-tenant;
- [ ] prompt injection;
- [ ] indirect injection;
- [ ] exfiltração;
- [ ] tool abuse;
- [ ] sensitive data.

## Qualidade

- [ ] dataset versionado;
- [ ] baseline;
- [ ] métricas;
- [ ] thresholds;
- [ ] regressão;
- [ ] evidências.

## Operação

- [ ] performance;
- [ ] custos;
- [ ] rate limits;
- [ ] timeout;
- [ ] retry;
- [ ] fallback;
- [ ] feature flag;
- [ ] rollback/kill path.

## Governança

- [ ] owner;
- [ ] CI/CD;
- [ ] waivers controlados;
- [ ] production readiness;
- [ ] revisão periódica.

---

# 104. Documentos Relacionados

- GAI-01 — Arquitetura e Governança de Inteligência Artificial
- GAI-02 — Providers, Modelos, Prompts e AI Gateway
- GAI-03 — RAG, Contexto e Conhecimento
- GAI-04 — Ferramentas, Agentes e Ações Seguras
- GAI-05 — Avaliação, Observabilidade, Custos e Operação de IA
- GAI-06 — Segurança, Privacidade e Guardrails de IA
- GAI-07 — Governança de Dados para Inteligência Artificial
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework
- GereIgreja Backend Engineering
- GereIgreja Data Engineering

---

# 105. Princípios Finais

Sistemas probabilísticos exigem engenharia de qualidade explícita.

```text
Works once
≠
Ready for production
```

O princípio central é:

```text
Every relevant AI change
must produce evidence.

Evidence of quality.
Evidence of security.
Evidence of isolation.
Evidence of performance.
Evidence of acceptable cost.
```

O GereIgreja deverá promover mudanças de IA com base em testes, avaliações e Quality Gates reproduzíveis, e não apenas em demonstrações manuais bem-sucedidas.

---

# 106. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`08-Testes-e-Quality-Gates-para-IA.md`

**Documento**

`GAI-08`

**Código**

`GAI-AI-TESTING-QUALITY-GATES`

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

`GAI-07 — Governança de Dados para Inteligência Artificial`

**Próximo documento candidato**

`09-Deploy-Release-e-Lifecycle-de-IA.md`
