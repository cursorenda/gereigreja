Pasta:

docs/ai/

Arquivo:

05-Avaliacao-Observabilidade-Custos-e-Operacao-de-IA.md

Documento:

GAI-05

Código:

GAI-EVALUATION-OBSERVABILITY-COST-OPERATIONS

Família:

GAI — GereIgreja Artificial Intelligence Engineering

Frameworks relacionados:

GEA — GereIgreja Enterprise Architecture
GSF — GereIgreja Security Framework
GOC — GereIgreja Operations Center
GQF — GereIgreja Quality Framework
GDF — GereIgreja Documentation Framework
GAPI — GereIgreja API Engineering
GINF — GereIgreja Infrastructure Engineering
GereIgreja Backend Engineering

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GAI-05 — Avaliação, Observabilidade, Custos e Operação de IA

> "Uma funcionalidade de IA só pode ser operada com segurança quando sua qualidade, custo, comportamento e falhas podem ser medidos."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Operação de IA
6. Arquitetura Operacional
7. Avaliação
8. Tipos de Avaliação
9. Evaluation Datasets
10. Casos de Referência
11. Golden Sets
12. Avaliação Offline
13. Avaliação Online
14. Avaliação Humana
15. Avaliação Automática
16. LLM-as-Judge
17. Métricas de Qualidade
18. Correção
19. Relevância
20. Groundedness
21. Faithfulness
22. Completude
23. Formato
24. Segurança
25. Taxa de Recusa
26. Tool Success
27. Task Completion
28. Avaliação de RAG
29. Avaliação de Agentes
30. Testes Adversariais
31. Regressão
32. Quality Gates
33. Baselines
34. Mudança de Modelo
35. Mudança de Prompt
36. Mudança de Retrieval
37. Mudança de Tool
38. Experimentos
39. A/B Testing
40. Feature Flags
41. Observabilidade
42. Correlation ID
43. Logging
44. Dados em Logs
45. Métricas
46. Latência
47. Erros
48. Tokens
49. Custos
50. Fallback
51. Retrieval
52. Tools
53. Agentes
54. Tracing
55. Auditoria
56. Dashboards
57. Alertas
58. SLOs
59. SLIs
60. Disponibilidade
61. Performance
62. Error Budget
63. Custos de IA
64. Cost Attribution
65. Custo por Feature
66. Custo por Tenant
67. Budgets
68. Quotas
69. Rate Limiting
70. Cost Guardrails
71. Model Routing
72. Caching
73. Batch
74. Otimização
75. Capacidade
76. Limites de Provider
77. Resiliência
78. Timeouts
79. Retries
80. Circuit Breaker
81. Fallback Operacional
82. Degradação Controlada
83. Incident Management
84. Severidade
85. Runbooks
86. Kill Switch
87. Rollback
88. Provider Outage
89. Model Degradation
90. Quality Incident
91. Cost Incident
92. Security Incident
93. Privacy Incident
94. Operação de Prompts
95. Operação de Modelos
96. Operação de Knowledge Bases
97. Operação de Agentes
98. Lifecycle
99. Depreciação
100. Ownership
101. Revisões Periódicas
102. Ambientes
103. Production Readiness
104. Anti-Padrões
105. Arquitetura Consolidada
106. Checklist
107. Documentos Relacionados
108. Princípios Finais
109. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para avaliação, observabilidade, controle de custos e operação de recursos de Inteligência Artificial no GereIgreja.

O objetivo é impedir que funcionalidades de IA sejam tratadas como caixas-pretas impossíveis de medir, comparar, diagnosticar ou controlar.

---

# 2. Escopo

Aplica-se a:

- modelos;
- prompts;
- RAG;
- embeddings;
- ferramentas;
- agentes;
- workflows;
- AI Gateway;
- integrações com providers;
- funcionalidades assistivas;
- automações baseadas em IA.

---

# 3. Relação com a Família GAI

```text
GAI-01
Architecture / Governance
        │
        ▼
GAI-02
Providers / Models / Prompts
        │
        ├───────────────┐
        ▼               ▼
GAI-03                GAI-04
RAG / Knowledge       Tools / Agents
        │               │
        └───────┬───────┘
                ▼
              GAI-05
 Evaluation / Observability
     Cost / Operations
```

O GAI-05 fecha o ciclo operacional da primeira camada normativa da família GAI.

---

# 4. Princípios Fundamentais

Toda capacidade de IA deverá observar:

- measurable quality;
- observable execution;
- explicit ownership;
- bounded cost;
- safe degradation;
- reproducible evaluation;
- regression detection;
- operational readiness;
- incident response;
- continuous improvement.

---

# 5. Operação de IA

Operar IA significa controlar simultaneamente:

```text
Quality
Security
Availability
Latency
Cost
Behavior
```

Uma feature funcional, mas não observável, não deverá ser considerada operacionalmente madura.

---

# 6. Arquitetura Operacional

```text
                    AI FEATURE
                        │
                        ▼
                   AI SERVICE
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Gateway       Retrieval       Tools
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                    TELEMETRY
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
     Logs             Metrics          Traces
       │                │                │
       └────────────────┼────────────────┘
                        ▼
                    DASHBOARDS
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
           Alerts             Evaluation
              │                   │
              └─────────┬─────────┘
                        ▼
                 Engineering Action
```

---

# 7. Avaliação

Toda feature relevante deverá possuir critérios de avaliação proporcionais ao seu risco.

---

# 8. Tipos de Avaliação

Poderão existir:

- offline;
- online;
- humana;
- automática;
- adversarial;
- regressão;
- produção.

---

# 9. Evaluation Datasets

Conjuntos de avaliação deverão representar tarefas reais da plataforma.

Não deverão conter dados de produção sensíveis sem processo formal adequado.

---

# 10. Casos de Referência

Cada caso deverá conter, quando aplicável:

- input;
- contexto;
- tenant fictício ou controlado;
- resultado esperado;
- critérios;
- tags;
- nível de risco.

---

# 11. Golden Sets

Golden sets poderão ser utilizados para casos com expectativa conhecida.

Deverão possuir versionamento.

---

# 12. Avaliação Offline

Executada antes da promoção de mudanças.

Adequada para comparar:

- modelos;
- prompts;
- retrieval;
- routing;
- schemas.

---

# 13. Avaliação Online

Utiliza sinais da operação real.

Deverá respeitar privacidade e governança.

---

# 14. Avaliação Humana

Necessária quando critérios automáticos não capturam adequadamente:

- utilidade;
- clareza;
- adequação;
- risco;
- nuance.

---

# 15. Avaliação Automática

Adequada para critérios determinísticos ou repetíveis.

Exemplos:

- schema válido;
- campo obrigatório;
- classificação;
- tool correta;
- ausência de dado proibido.

---

# 16. LLM-as-Judge

Poderá ser utilizado como sinal auxiliar.

Não deverá ser tratado como verdade absoluta.

Quando relevante:

- versionar judge/model;
- calibrar contra avaliação humana;
- monitorar viés;
- evitar dependência exclusiva.

---

# 17. Métricas de Qualidade

Métricas dependerão do caso de uso.

---

# 18. Correção

Avaliar se a resposta está correta segundo a fonte ou regra aplicável.

---

# 19. Relevância

Avaliar se a resposta atende à pergunta real.

---

# 20. Groundedness

Avaliar se afirmações estão apoiadas no contexto fornecido.

---

# 21. Faithfulness

Avaliar se o modelo não atribui à fonte algo que ela não contém.

---

# 22. Completude

Avaliar se aspectos essenciais foram cobertos.

---

# 23. Formato

Para saídas estruturadas, medir:

- parse success;
- schema compliance;
- campos obrigatórios;
- tipos válidos.

---

# 24. Segurança

Avaliar:

- prompt injection;
- vazamento;
- cross-tenant;
- tool abuse;
- conteúdo proibido;
- bypass de autorização.

---

# 25. Taxa de Recusa

Recusa excessiva também poderá representar degradação de produto.

Medir quando aplicável.

---

# 26. Tool Success

Para tools:

```text
proposed
authorized
executed
successful
failed
rejected
```

---

# 27. Task Completion

Para agentes, avaliar conclusão da tarefa e não apenas qualidade textual.

---

# 28. Avaliação de RAG

Seguir GAI-03.

Incluir:

- precision;
- recall;
- retrieval relevance;
- empty retrieval;
- groundedness.

---

# 29. Avaliação de Agentes

Seguir GAI-04.

Incluir:

- número de passos;
- tool selection;
- execução correta;
- loops;
- confirmações;
- aborts;
- efeitos finais.

---

# 30. Testes Adversariais

Deverão existir casos deliberadamente hostis.

---

# 31. Regressão

Mudanças deverão ser comparadas contra baseline quando o risco justificar.

---

# 32. Quality Gates

Exemplo conceitual:

```text
Evaluation
    │
    ├── PASS → candidate
    │
    └── FAIL → block
```

Thresholds deverão ser definidos por feature.

---

# 33. Baselines

Registrar baseline antes de alterações significativas.

---

# 34. Mudança de Modelo

Troca de modelo poderá alterar comportamento mesmo sem mudança de código.

Exige avaliação proporcional ao risco.

---

# 35. Mudança de Prompt

Prompt é componente comportamental.

Mudança relevante deverá passar por regressão.

---

# 36. Mudança de Retrieval

Mudanças em:

- chunking;
- embeddings;
- ranking;
- reranking;
- threshold;

podem modificar respostas e deverão ser avaliadas.

---

# 37. Mudança de Tool

Alterações em contratos de tools deverão possuir testes.

---

# 38. Experimentos

Experimentos deverão possuir:

- hipótese;
- métrica;
- população;
- duração;
- owner;
- critério de encerramento.

---

# 39. A/B Testing

Poderá ser utilizado quando apropriado.

Não utilizar para contornar requisitos de segurança.

---

# 40. Feature Flags

Mudanças de IA poderão utilizar rollout gradual.

---

# 41. Observabilidade

Observabilidade deverá permitir responder:

```text
o que aconteceu?
quando?
para qual feature?
com qual modelo?
quanto custou?
quanto demorou?
falhou onde?
houve fallback?
```

---

# 42. Correlation ID

Uma execução deverá possuir identificador correlacionável entre componentes.

---

# 43. Logging

Logs deverão registrar eventos técnicos úteis sem copiar indiscriminadamente dados sensíveis.

---

# 44. Dados em Logs

Evitar:

- prompts completos;
- documentos completos;
- secrets;
- tokens;
- dados pessoais desnecessários.

Preferir metadados.

---

# 45. Métricas

Métricas recomendadas incluem:

```text
ai_requests_total
ai_request_duration
ai_errors_total
ai_tokens_input
ai_tokens_output
ai_fallback_total
ai_estimated_cost
ai_tool_calls_total
rag_retrieval_latency
```

Os nomes definitivos deverão seguir o padrão de observabilidade da plataforma.

---

# 46. Latência

Medir percentis quando possível.

Exemplo:

```text
p50
p95
p99
```

---

# 47. Erros

Separar categorias:

- aplicação;
- provider;
- timeout;
- rate limit;
- parsing;
- validation;
- retrieval;
- tool.

---

# 48. Tokens

Registrar consumo quando disponível.

---

# 49. Custos

Custos deverão ser estimáveis por operação.

---

# 50. Fallback

Fallback deverá possuir métrica própria.

Aumento de fallback pode indicar degradação do provider principal.

---

# 51. Retrieval

Medir:

- latência;
- resultados;
- empty results;
- filtros;
- falhas.

---

# 52. Tools

Medir:

- chamadas;
- sucesso;
- erro;
- rejeição;
- confirmação.

---

# 53. Agentes

Medir:

- passos;
- duração;
- custo;
- aborts;
- loops interrompidos;
- task completion.

---

# 54. Tracing

Tracing deverá conectar operações distribuídas quando necessário.

---

# 55. Auditoria

Auditoria é diferente de logging operacional.

Eventos de negócio deverão seguir os frameworks oficiais de auditoria.

---

# 56. Dashboards

Dashboards deverão priorizar sinais acionáveis.

Possíveis painéis:

- saúde geral;
- qualidade;
- custos;
- providers;
- RAG;
- agentes.

---

# 57. Alertas

Alertas deverão indicar situações que exigem ação.

Evitar alert fatigue.

---

# 58. SLOs

Features maduras poderão possuir Service Level Objectives.

---

# 59. SLIs

Indicadores poderão incluir:

- availability;
- latency;
- success rate;
- valid output rate.

---

# 60. Disponibilidade

A disponibilidade de IA deverá ser separada da disponibilidade do core quando possível.

---

# 61. Performance

Performance deverá considerar experiência total e não apenas tempo do modelo.

---

# 62. Error Budget

Features críticas poderão adotar error budget.

---

# 63. Custos de IA

Custo é dimensão operacional de primeira classe.

---

# 64. Cost Attribution

Deverá ser possível atribuir custo pelo menos à feature quando relevante.

---

# 65. Custo por Feature

Exemplos:

```text
assistant
summary
classification
rag_search
agent
```

---

# 66. Custo por Tenant

Poderá ser necessário para:

- quotas;
- billing futuro;
- abuse detection;
- capacity planning.

---

# 67. Budgets

Definir budgets quando o risco financeiro justificar.

---

# 68. Quotas

Quotas poderão limitar consumo por período.

---

# 69. Rate Limiting

Aplicar conforme GAI-02 e GAI-04.

---

# 70. Cost Guardrails

Exemplos:

- max tokens;
- max steps;
- max tool calls;
- cheaper model routing;
- hard quota;
- alert threshold.

---

# 71. Model Routing

Routing poderá otimizar custo, desde que preserve qualidade mínima e segurança.

---

# 72. Caching

Caching poderá reduzir custo.

Cache deverá respeitar:

- tenant;
- autorização;
- freshness;
- privacidade.

---

# 73. Batch

Operações não interativas poderão utilizar batch quando apropriado.

---

# 74. Otimização

Otimização não deverá sacrificar segurança ou qualidade silenciosamente.

---

# 75. Capacidade

Planejar capacidade considerando:

- volume;
- concorrência;
- rate limits;
- latência;
- budgets.

---

# 76. Limites de Provider

Limites externos deverão ser conhecidos e monitorados.

---

# 77. Resiliência

Falhas deverão permanecer confinadas.

---

# 78. Timeouts

Timeouts são obrigatórios em dependências externas.

---

# 79. Retries

Retries deverão ser limitados e observáveis.

---

# 80. Circuit Breaker

Poderá proteger a plataforma durante falhas persistentes.

---

# 81. Fallback Operacional

Fallback deverá possuir política conhecida.

---

# 82. Degradação Controlada

Exemplo:

```text
advanced AI unavailable
→ simpler AI fallback

all AI unavailable
→ assisted feature unavailable

core GereIgreja
→ remains operational
```

quando possível.

---

# 83. Incident Management

Incidentes relacionados a IA deverão seguir GSF, GOC e processos oficiais.

---

# 84. Severidade

Classificar impacto considerando:

- indisponibilidade;
- segurança;
- privacidade;
- custo;
- qualidade;
- número de tenants.

---

# 85. Runbooks

Features relevantes deverão possuir procedimentos para falhas previsíveis.

---

# 86. Kill Switch

Deverá existir para capacidades de maior risco.

---

# 87. Rollback

Mudanças de prompt, modelo, routing ou configuração deverão poder ser revertidas quando tecnicamente possível.

---

# 88. Provider Outage

Plano poderá incluir:

```text
detect
→ circuit break
→ fallback
→ degrade
→ recover
```

---

# 89. Model Degradation

Um modelo pode permanecer disponível e ainda assim degradar qualidade.

Avaliação e métricas deverão detectar esse cenário.

---

# 90. Quality Incident

Exemplos:

- respostas sistematicamente incorretas;
- formato inválido em escala;
- perda de groundedness;
- tool selection inadequada.

---

# 91. Cost Incident

Exemplos:

- loop de agente;
- retry excessivo;
- aumento inesperado de tokens;
- abuso;
- configuração incorreta.

---

# 92. Security Incident

Seguir GSF.

Exemplos:

- prompt injection com impacto;
- tool abuse;
- bypass de autorização;
- exfiltração.

---

# 93. Privacy Incident

Exemplos:

- envio indevido de dados;
- vazamento cross-tenant;
- logging excessivo;
- provider incompatível com política.

---

# 94. Operação de Prompts

Prompts em produção deverão possuir versão identificável.

---

# 95. Operação de Modelos

Deverá ser possível identificar qual modelo atendeu uma execução.

---

# 96. Operação de Knowledge Bases

Monitorar:

- ingestão;
- freshness;
- falhas;
- volume;
- reindexação.

---

# 97. Operação de Agentes

Monitorar:

- tools;
- passos;
- duração;
- aborts;
- custos;
- confirmações.

---

# 98. Lifecycle

Componentes poderão possuir estados:

```text
EXPERIMENTAL
BETA
PRODUCTION
DEPRECATED
DISABLED
```

---

# 99. Depreciação

Depreciação deverá possuir:

- owner;
- prazo;
- substituto;
- impacto;
- remoção planejada.

---

# 100. Ownership

Toda feature de IA deverá possuir owner técnico.

Features críticas também deverão possuir owner operacional claramente definido.

---

# 101. Revisões Periódicas

Revisar periodicamente:

- providers;
- modelos;
- prompts;
- custos;
- qualidade;
- permissões;
- retention;
- incidents.

---

# 102. Ambientes

Development, staging e production deverão ser distinguíveis na telemetria.

---

# 103. Production Readiness

Antes de produção verificar:

- avaliação;
- baseline;
- owner;
- métricas;
- logs;
- alertas quando necessários;
- limites;
- custos;
- fallback;
- kill switch proporcional ao risco;
- documentação.

---

# 104. Anti-Padrões

Evitar:

```text
"parece funcionar"
=
evaluation
```

---

```text
produção
sem baseline
```

---

```text
modelo alterado
sem regressão
```

---

```text
prompt completo sensível
em log
```

---

```text
custo
descoberto apenas
na fatura
```

---

```text
agente
sem max steps
```

---

```text
fallback
sem métrica
```

---

```text
alerta
para todo erro individual
```

---

```text
provider outage
derruba core platform
```

---

```text
qualidade
medida apenas
por latência
```

---

# 105. Arquitetura Consolidada

```text
                         AI FEATURE
                             │
                             ▼
                        AI SERVICE
                             │
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
       AI GATEWAY            RAG              TOOLS
           │                 │                 │
           └─────────────────┼─────────────────┘
                             ▼
                         TELEMETRY
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
        LOGS               METRICS            TRACES
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                         DASHBOARDS
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
             ALERTS      EVALUATION      COST
                │            │            │
                └────────────┼────────────┘
                             ▼
                     OPERATIONAL CONTROL
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
       FALLBACK          KILL SWITCH         ROLLBACK
```

---

# 106. Checklist

## Avaliação

- [ ] dataset;
- [ ] casos reais representativos;
- [ ] baseline;
- [ ] métricas;
- [ ] adversarial;
- [ ] regressão;
- [ ] quality gate proporcional ao risco.

## Observabilidade

- [ ] correlation ID;
- [ ] logs minimizados;
- [ ] métricas;
- [ ] latência;
- [ ] erros;
- [ ] tokens;
- [ ] fallback;
- [ ] tracing quando necessário.

## Custos

- [ ] custo mensurável;
- [ ] attribution;
- [ ] budget quando necessário;
- [ ] quota quando necessária;
- [ ] rate limiting;
- [ ] guardrails.

## Operação

- [ ] owner;
- [ ] SLI/SLO quando necessário;
- [ ] dashboard;
- [ ] alertas;
- [ ] runbook;
- [ ] fallback;
- [ ] kill switch;
- [ ] rollback.

## Incidentes

- [ ] provider outage;
- [ ] quality incident;
- [ ] cost incident;
- [ ] security incident;
- [ ] privacy incident.

## Lifecycle

- [ ] estado;
- [ ] versão de prompt;
- [ ] modelo identificável;
- [ ] feature flag;
- [ ] depreciação;
- [ ] revisão periódica.

---

# 107. Documentos Relacionados

- GAI-01 — Arquitetura e Governança de Inteligência Artificial
- GAI-02 — Providers, Modelos, Prompts e AI Gateway
- GAI-03 — RAG, Contexto e Conhecimento
- GAI-04 — Ferramentas, Agentes e Ações Seguras
- GSF — GereIgreja Security Framework
- GAPI — GereIgreja API Engineering
- GINF — GereIgreja Infrastructure Engineering
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GDF — GereIgreja Documentation Framework
- GereIgreja Backend Engineering

---

# 108. Princípios Finais

Uma capacidade de IA em produção deverá ser tratada como sistema operacionalmente mensurável.

```text
Quality
+
Observability
+
Cost Control
+
Resilience
+
Ownership
=
Operable AI
```

O princípio central é:

```text
Não basta saber
que a IA respondeu.

Precisamos saber:

se respondeu bem,
quanto demorou,
quanto custou,
qual componente falhou,
qual modelo foi utilizado
e como desligar ou reverter
quando necessário.
```

A evolução de IA no GereIgreja deverá ser orientada por evidências e não apenas por percepção subjetiva de qualidade.

---

# 109. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`05-Avaliacao-Observabilidade-Custos-e-Operacao-de-IA.md`

**Documento**

`GAI-05`

**Código**

`GAI-EVALUATION-OBSERVABILITY-COST-OPERATIONS`

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

`GAI-04 — Ferramentas, Agentes e Ações Seguras`

**Próxima etapa recomendada**

`Auditoria da família GAI-01 a GAI-05 antes da criação de GAI-06`
