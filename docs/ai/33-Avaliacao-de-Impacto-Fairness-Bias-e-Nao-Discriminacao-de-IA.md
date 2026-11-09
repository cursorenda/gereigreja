Pasta:

docs/ai/

Arquivo:

33-Avaliacao-de-Impacto-Fairness-Bias-e-Nao-Discriminacao-de-IA.md

Documento:

GAI-33

Código:

GAI-AI-IMPACT-FAIRNESS-BIAS-NON-DISCRIMINATION

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

# GAI-33 — Avaliação de Impacto, Fairness, Bias e Não Discriminação de Inteligência Artificial

> "Um sistema pode ser tecnicamente correto e ainda produzir impacto inadequado. Avaliar IA exige considerar quem é afetado, como é afetado e quais riscos permanecem após os controles."

---

# Sumário

1. Objetivo
2. Escopo
3. Princípios Fundamentais
4. AI Impact Assessment
5. Pessoas Afetadas
6. Impacto Direto
7. Impacto Indireto
8. Materialidade
9. Vulnerabilidade
10. Fairness
11. Bias
12. Discriminação
13. Representatividade
14. Proxy Variables
15. Protected/Sensitive Attributes
16. Dataset Bias
17. Measurement Bias
18. Label Bias
19. Selection Bias
20. Model Bias
21. Automation Bias
22. Feedback Loops
23. Disparate Impact
24. Error Distribution
25. False Positives
26. False Negatives
27. Human Oversight
28. Contestação
29. Mitigação
30. Residual Impact
31. Approval
32. Reassessment
33. Evidence
34. Metrics
35. Templates
36. Anti-Padrões
37. Checklist
38. Documentos Relacionados
39. Princípios Finais
40. Status do Documento

---

# 1. Objetivo

Estabelecer o processo oficial de avaliação de impacto de IA, fairness, bias e não discriminação no GereIgreja.

---

# 2. Escopo

Aplica-se especialmente a sistemas que:

- recomendam;
- classificam;
- priorizam;
- personalizam;
- influenciam decisões;
- automatizam ações;
- afetam acesso a funcionalidades ou tratamento de pessoas.

---

# 3. Princípios Fundamentais

Aplicar:

- assess impact before scale;
- identify affected groups;
- measure error distribution;
- distinguish bias from lawful differentiation;
- use representative data;
- avoid proxy discrimination;
- preserve human review where needed;
- enable contest and correction;
- document residual impact;
- reassess after material change.

---

# 4. AI Impact Assessment

Todo caso de uso R3 e outros casos materialmente impactantes deverão possuir AI Impact Assessment.

Fluxo:

```text
Purpose
  ↓
Affected Persons
  ↓
Potential Impacts
  ↓
Bias / Fairness Risks
  ↓
Controls
  ↓
Evaluation
  ↓
Residual Impact
  ↓
Approval
```

---

# 5. Pessoas Afetadas

Identificar usuários, membros, operadores, terceiros ou grupos impactados.

---

# 6. Impacto Direto

Impacto produzido diretamente por recomendação, classificação, decisão ou ação.

---

# 7. Impacto Indireto

Impactos secundários ou cumulativos também deverão ser considerados.

---

# 8. Materialidade

Avaliar severidade, escala, duração e reversibilidade.

---

# 9. Vulnerabilidade

Considerar grupos em maior risco de dano ou exclusão.

---

# 10. Fairness

Fairness deverá ser definida conforme o contexto do caso de uso.

Não existe uma única métrica universal.

---

# 11. Bias

Bias poderá surgir em dados, labels, amostragem, arquitetura, interação humana ou feedback.

---

# 12. Discriminação

Resultados incompatíveis com políticas, direitos ou requisitos aplicáveis deverão ser bloqueados ou mitigados.

---

# 13. Representatividade

Datasets deverão representar a população e cenários relevantes.

---

# 14. Proxy Variables

Atributos aparentemente neutros podem atuar como proxies de atributos sensíveis.

---

# 15. Protected/Sensitive Attributes

O uso de atributos sensíveis deverá possuir finalidade, autorização e controles adequados.

---

# 16. Dataset Bias

Avaliar distribuição e cobertura.

---

# 17. Measurement Bias

Verificar se variáveis realmente medem o fenômeno pretendido.

---

# 18. Label Bias

Labels humanas ou históricas podem carregar distorções.

---

# 19. Selection Bias

Amostras não representativas podem comprometer conclusões.

---

# 20. Model Bias

Avaliar desempenho por segmentos relevantes.

---

# 21. Automation Bias

Usuários podem confiar excessivamente em resultados automatizados.

---

# 22. Feedback Loops

Recomendações podem alterar os próprios dados futuros.

---

# 23. Disparate Impact

Avaliar diferença de impacto entre grupos quando aplicável.

---

# 24. Error Distribution

Não analisar apenas média global.

---

# 25. False Positives

Avaliar impacto de falsos positivos por grupo.

---

# 26. False Negatives

Avaliar impacto de falsos negativos por grupo.

---

# 27. Human Oversight

Casos de alto impacto deverão possuir revisão humana proporcional.

---

# 28. Contestação

Quando aplicável, permitir revisão e correção.

---

# 29. Mitigação

Exemplos:

- rebalancing;
- data improvement;
- threshold adjustment;
- process redesign;
- human review;
- scope reduction;
- feature restriction.

---

# 30. Residual Impact

Risco residual deverá ser documentado.

---

# 31. Approval

R3 ou equivalente deverá possuir aprovação formal.

---

# 32. Reassessment

Reavaliar após:

- mudança de modelo;
- mudança de dataset;
- mudança de população;
- incidente;
- alteração de finalidade;
- aumento de autonomia.

---

# 33. Evidence

Preservar datasets, métricas, decisões e controles conforme GAI-18.

---

# 34. Metrics

Exemplos:

```text
impact_assessments_completed
fairness_findings_open
segment_error_gap
false_positive_gap
false_negative_gap
human_override_rate
contest_rate
correction_rate
```

---

# 35. Templates

## AI Impact Assessment

```text
Assessment ID:
Use Case ID:
Owner:
Risk Level:

Purpose:
Affected Persons:
Affected Groups:

Direct Impact:
Indirect Impact:
Severity:
Scale:
Reversibility:

Sensitive Attributes:
Proxy Risks:

Dataset Representation:
Bias Risks:
Fairness Definition:
Metrics:

Human Oversight:
Contest Path:
Correction Path:

Mitigations:
Residual Impact:

Approval:
Review Date:
```

---

# 36. Anti-Padrões

Evitar:

```text
overall accuracy = 95%
therefore fairness is acceptable
```

```text
historical data
=
neutral data
```

```text
remove protected attribute
=
no discrimination
```

```text
human in the loop
=
risk solved
```

---

# 37. Checklist

- [ ] affected persons;
- [ ] material impacts;
- [ ] sensitive attributes;
- [ ] proxy analysis;
- [ ] representativity;
- [ ] subgroup metrics;
- [ ] false positives/negatives;
- [ ] human oversight;
- [ ] contestation;
- [ ] mitigation;
- [ ] residual impact;
- [ ] approval;
- [ ] reassessment.

---

# 38. Documentos Relacionados

- GAI-06 — Segurança, Privacidade e Guardrails de IA
- GAI-07 — Governança de Dados para IA
- GAI-11 — Catálogo de Casos de Uso e Níveis de Risco
- GAI-22 — Política de Uso Aceitável e Práticas Proibidas
- GAI-24 — Transparência, Explicabilidade e Comunicação
- GAI-25 — Datasets Sintéticos, Fine-Tuning e Customização
- GAI-32 — Evaluations, Benchmarks, Golden Datasets e Regressão

---

# 39. Princípios Finais

```text
Measure not only
"Did the model work?"

Also measure
"For whom did it work?"
"And who bears the error?"
```

---

# 40. Status do Documento

**Arquivo**

`33-Avaliacao-de-Impacto-Fairness-Bias-e-Nao-Discriminacao-de-IA.md`

**Documento**

`GAI-33`

**Versão**

`1.0`

**Status**

`OFICIAL`
