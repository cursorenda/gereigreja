Pasta:

docs/ai/

Arquivo:

32-Governanca-de-Evaluations-Benchmarks-Golden-Datasets-e-Regressao-de-IA.md

Documento:

GAI-32

Código:

GAI-AI-EVALUATIONS-BENCHMARKS-GOLDEN-DATASETS-REGRESSION

Família:

GAI — GereIgreja Artificial Intelligence Engineering

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GAI-32 — Governança de Evaluations, Benchmarks, Golden Datasets e Regressão de Inteligência Artificial

> "Nenhuma mudança de IA deve ser considerada melhor apenas porque parece melhor. Ela precisa ser comparada contra critérios, datasets, baselines e thresholds definidos."

---

# Sumário

1. Objetivo
2. Escopo
3. Princípios Fundamentais
4. Sistema de Evaluations
5. Evaluation Registry
6. Evaluation Suite
7. Golden Datasets
8. Benchmarks
9. Baselines
10. Candidate Evaluation
11. Offline Evaluation
12. Online Evaluation
13. Human Evaluation
14. Deterministic Graders
15. Model-Based Graders
16. Pairwise Evaluation
17. Task Success
18. Groundedness
19. Relevance
20. Factuality
21. Safety
22. Security
23. Privacy
24. Bias e Fairness
25. Agent Evaluation
26. Tool Evaluation
27. RAG Evaluation
28. Retrieval Evaluation
29. Structured Output Evaluation
30. Latency Evaluation
31. Cost Evaluation
32. Regression
33. Acceptance Criteria
34. Quality Gates
35. Statistical Confidence
36. Dataset Contamination
37. Evaluation Drift
38. Versionamento
39. Evidence
40. Release Integration
41. Production Monitoring
42. Incident Integration
43. Change Management
44. Templates
45. Anti-Padrões
46. Checklist
47. Documentos Relacionados
48. Princípios Finais
49. Status do Documento

---

# 1. Objetivo

Estabelecer o padrão oficial para evaluations, benchmarks, golden datasets, regressão e critérios de aceitação de sistemas de Inteligência Artificial do GereIgreja.

---

# 2. Escopo

Aplica-se a:

- modelos;
- prompts;
- RAG;
- agentes;
- tools;
- embeddings;
- rerankers;
- routing;
- fallback;
- modelos customizados;
- mudanças de configuração;
- features de IA.

---

# 3. Princípios Fundamentais

Aplicar:

- evaluate before production;
- compare against baseline;
- version datasets;
- define thresholds before promotion;
- separate train and evaluation data;
- use task-specific metrics;
- preserve evidence;
- regression must be repeatable;
- human judgment where automation is insufficient;
- no single metric decides every use case.

---

# 4. Sistema de Evaluations

Fluxo:

```text
Use Case
   ↓
Risk Level
   ↓
Evaluation Suite
   ↓
Golden Dataset
   ↓
Baseline
   ↓
Candidate
   ↓
Metrics / Graders
   ↓
Acceptance Criteria
   ↓
PASS / FAIL
```

---

# 5. Evaluation Registry

Cada evaluation relevante deverá possuir:

```text
evaluation_id
owner
use_case_id
risk_level
dataset_version
baseline_version
candidate_version
metrics
thresholds
result
evidence
```

---

# 6. Evaluation Suite

Uma suite deverá agrupar os testes necessários para um caso de uso.

---

# 7. Golden Datasets

Golden datasets são conjuntos versionados e representativos usados para regressão e comparação.

Devem possuir owner, finalidade, proveniência e proteção contra contaminação.

---

# 8. Benchmarks

Benchmarks externos podem ser usados como referência, mas não substituem datasets reais do domínio.

---

# 9. Baselines

Toda mudança material deverá ser comparada a um baseline conhecido.

---

# 10. Candidate Evaluation

O candidato deverá ser avaliado com a mesma suite sempre que possível.

---

# 11. Offline Evaluation

Executada antes do rollout usando datasets controlados.

---

# 12. Online Evaluation

Executada em produção ou canary com sinais reais, sem substituir gates anteriores.

---

# 13. Human Evaluation

Utilizar quando qualidade depende de julgamento contextual.

---

# 14. Deterministic Graders

Preferir graders determinísticos quando o critério puder ser verificado objetivamente.

---

# 15. Model-Based Graders

Podem complementar avaliação, mas devem ser calibrados e versionados.

---

# 16. Pairwise Evaluation

Comparar baseline e candidato lado a lado quando métricas absolutas forem insuficientes.

---

# 17. Task Success

Medir se a tarefa foi realmente concluída.

---

# 18. Groundedness

Avaliar aderência às fontes quando houver RAG.

---

# 19. Relevance

Avaliar relevância para a solicitação e o contexto.

---

# 20. Factuality

Avaliar factualidade quando o domínio permitir verificação.

---

# 21. Safety

Medir aderência a controles e políticas de segurança.

---

# 22. Security

Incluir cenários adversariais conforme GAI-26.

---

# 23. Privacy

Avaliar leakage, minimização e uso correto de dados.

---

# 24. Bias e Fairness

Integrar com GAI-33 quando aplicável.

---

# 25. Agent Evaluation

Avaliar:

```text
trajectory
tool selection
authorization
step count
outcome
cost
safety
```

---

# 26. Tool Evaluation

Verificar schema, autorização, side effects e idempotência.

---

# 27. RAG Evaluation

Avaliar retrieval e geração separadamente.

---

# 28. Retrieval Evaluation

Métricas possíveis:

```text
precision
recall
MRR
NDCG
empty_retrieval_rate
source_coverage
```

---

# 29. Structured Output Evaluation

Validar schemas e semântica de campos.

---

# 30. Latency Evaluation

Comparar latência contra SLOs.

---

# 31. Cost Evaluation

Comparar custo por request e por resultado útil.

---

# 32. Regression

Toda correção de finding relevante deverá gerar teste de regressão.

---

# 33. Acceptance Criteria

Critérios devem existir antes da avaliação.

Exemplo:

```text
task_success >= 0.92
groundedness >= 0.95
critical_safety_failures = 0
cost_increase <= 15%
p95_latency <= target
```

---

# 34. Quality Gates

Resultados deverão integrar GAI-08 e GAI-09.

---

# 35. Statistical Confidence

Para amostras grandes ou métricas sensíveis, considerar intervalos de confiança e tamanho de amostra.

---

# 36. Dataset Contamination

Evitar uso de golden datasets durante tuning ou treinamento.

---

# 37. Evaluation Drift

Monitorar se datasets e critérios deixam de representar produção.

---

# 38. Versionamento

Versionar:

```text
dataset
grader
prompt
model
configuration
evaluation suite
thresholds
```

---

# 39. Evidence

Preservar relatórios e artefatos conforme GAI-18.

---

# 40. Release Integration

Mudanças sem evidência suficiente não deverão ser promovidas.

---

# 41. Production Monitoring

Conectar resultados offline a sinais observados em produção.

---

# 42. Incident Integration

Incidentes de qualidade devem gerar novos casos de teste.

---

# 43. Change Management

Aplicar GAI-23.

---

# 44. Templates

## Evaluation Suite Record

```text
Evaluation ID:
Owner:
Use Case ID:
Risk Level:

Dataset:
Dataset Version:
Baseline:
Candidate:

Metrics:
Graders:
Thresholds:

Human Review:
Security Tests:
Privacy Tests:
Fairness Tests:

Result:
Evidence:
Approval:
```

## Golden Dataset Card

```text
Dataset ID:
Name:
Version:
Owner:

Purpose:
Source:
Provenance:
Sampling Strategy:

Train Contamination Check:
Sensitive Data:
Tenant Data:

Coverage:
Known Gaps:
Last Review:
Status:
```

---

# 45. Anti-Padrões

Evitar:

```text
looks better
=
approved
```

```text
benchmark score
=
production quality
```

```text
same dataset
for tuning and final evaluation
```

```text
LLM judge
without calibration
```

```text
one metric
for every use case
```

---

# 46. Checklist

- [ ] evaluation suite;
- [ ] golden dataset;
- [ ] baseline;
- [ ] candidate;
- [ ] thresholds;
- [ ] regression;
- [ ] safety;
- [ ] security;
- [ ] privacy;
- [ ] fairness quando aplicável;
- [ ] latency;
- [ ] cost;
- [ ] evidence;
- [ ] release gate.

---

# 47. Documentos Relacionados

- GAI-05 — Avaliação, Observabilidade, Custos e Operação de IA
- GAI-08 — Testes e Quality Gates para IA
- GAI-11 — Catálogo de Casos de Uso e Níveis de Risco de IA
- GAI-13 — Governança de Prompts, Modelos e Configurações de IA
- GAI-25 — Datasets Sintéticos, Fine-Tuning e Customização
- GAI-26 — Red Teaming e Adversarial Testing
- GAI-31 — Observabilidade e Telemetria Avançada

---

# 48. Princípios Finais

```text
Baseline
→ Candidate
→ Evaluate
→ Compare
→ Gate
→ Release
→ Observe
→ Regress
```

---

# 49. Status do Documento

**Arquivo**

`32-Governanca-de-Evaluations-Benchmarks-Golden-Datasets-e-Regressao-de-IA.md`

**Documento**

`GAI-32`

**Versão**

`1.0`

**Status**

`OFICIAL`
