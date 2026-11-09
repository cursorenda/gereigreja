Pasta:

docs/ai/

Arquivo:

24-Transparencia-Explicabilidade-e-Comunicacao-de-IA.md

Documento:

GAI-24

Código:

GAI-AI-TRANSPARENCY-EXPLAINABILITY-COMMUNICATION

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

# GAI-24 — Transparência, Explicabilidade e Comunicação de Inteligência Artificial

> "Transparência útil não significa revelar tudo. Significa fornecer às pessoas certas informação suficiente para compreender o papel da IA, seus limites, suas fontes, seus efeitos e os caminhos de revisão."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Transparência de IA
6. Públicos
7. Transparência para Usuários
8. Transparência para Clientes
9. Transparência Interna
10. Transparência para Engenharia
11. Transparência para Auditoria
12. Transparência para Incidentes
13. Divulgação do Uso de IA
14. Quando Informar
15. Como Informar
16. Linguagem
17. Proporcionalidade
18. Limitações
19. Incerteza
20. Conteúdo Gerado por IA
21. Assistência versus Automação
22. Recomendações
23. Decisões
24. Ações Automatizadas
25. Explicabilidade
26. Explicabilidade Operacional
27. Explicabilidade Funcional
28. Explicabilidade de Dados
29. Explicabilidade de RAG
30. Explicabilidade de Agentes
31. Explicabilidade de Tools
32. Explicabilidade de Decisões
33. Proveniência
34. Fontes
35. Citações
36. Confidence
37. Limites de Confidence
38. Chain-of-Thought
39. Rationale Seguro
40. Decision Record
41. Model Identity
42. Provider Identity
43. Prompt Identity
44. Configuration Identity
45. Versionamento
46. User-Facing Explanations
47. Internal Explanations
48. Audit Explanations
49. High-Impact Use Cases
50. Human Review
51. Contestação
52. Correção
53. Feedback
54. Escalation
55. Comunicação de Erros
56. Comunicação de Incidentes
57. Comunicação de Indisponibilidade
58. Comunicação de Degradação
59. Comunicação de Mudança
60. Comunicação de Modelo
61. Comunicação de Provider
62. Comunicação de Depreciação
63. Comunicação de Dados
64. Comunicação de Privacidade
65. Comunicação de Limites
66. UX
67. Labels
68. Notices
69. Disclaimers
70. Help Content
71. Documentation
72. API Consumers
73. Developer Communication
74. Changelog
75. Release Notes
76. Status Communication
77. Support
78. Training
79. Marketing
80. Claims sobre IA
81. Proibições de Comunicação
82. Falsa Precisão
83. Falsa Garantia
84. Anthropomorphism
85. Ocultação de Limitações
86. Dark Patterns
87. Manipulação
88. Segurança da Informação
89. Secrets
90. Dados Sensíveis
91. Prompt Disclosure
92. System Instructions
93. Security Controls
94. Auditoria
95. Evidências
96. Retenção
97. Métricas
98. Quality Gates
99. Production Readiness
100. Templates
101. Anti-Padrões
102. Arquitetura Consolidada
103. Checklist
104. Documentos Relacionados
105. Princípios Finais
106. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para transparência, explicabilidade e comunicação relacionadas às capacidades de Inteligência Artificial no GereIgreja.

Seu objetivo é garantir que usuários, equipes internas, clientes, operadores e auditores recebam informação apropriada ao contexto sobre o papel da IA, suas limitações, fontes, ações, mudanças e mecanismos de revisão.

---

# 2. Escopo

Aplica-se a:

- interfaces com IA;
- conteúdo gerado;
- recomendações;
- decisões assistidas;
- agentes;
- tools;
- RAG;
- APIs;
- documentação;
- suporte;
- incidentes;
- releases;
- comunicações internas e externas.

---

# 3. Relação com a Família GAI

```text
GAI-03
RAG / Provenance
        │
GAI-05
Quality / Observability
        │
GAI-11
Use Cases / Risk
        │
GAI-14
Agents / HITL
        │
GAI-18
Audit / Evidence
        │
GAI-22
Acceptable Use
        │
GAI-23
Change Management
        │
        ▼
GAI-24
Transparency / Explainability / Communication
```

---

# 4. Princípios Fundamentais

Aplicar:

- disclose when material;
- explain for the audience;
- state limitations;
- preserve provenance;
- distinguish fact from generation;
- avoid false certainty;
- enable review;
- protect sensitive implementation details;
- communicate material changes;
- never use transparency as a substitute for control.

---

# 5. Transparência de IA

Transparência deverá responder, quando relevante:

```text
Is AI involved?
What role does it play?
What information was used?
What can it get wrong?
Did it take an action?
Can a human review it?
How can an error be corrected?
```

---

# 6. Públicos

A quantidade e profundidade de informação dependerão do público.

---

# 7. Transparência para Usuários

Usuários deverão receber informação útil para utilizar a capacidade de forma adequada.

---

# 8. Transparência para Clientes

Clientes deverão compreender capacidades e limitações materiais que afetem seu uso.

---

# 9. Transparência Interna

Owners e equipes operacionais deverão possuir contexto técnico suficiente para operar e governar a capacidade.

---

# 10. Transparência para Engenharia

Engenharia deverá conhecer:

- modelo/alias;
- provider;
- prompt/configuração;
- fontes;
- tools;
- limites;
- observabilidade.

---

# 11. Transparência para Auditoria

Auditoria deverá receber evidências necessárias ao escopo, aplicando minimização.

---

# 12. Transparência para Incidentes

Durante investigação, preservar informação suficiente para reconstruir o comportamento.

---

# 13. Divulgação do Uso de IA

O uso de IA deverá ser informado quando sua participação for material para a expectativa ou decisão do usuário.

---

# 14. Quando Informar

Considerar divulgação especialmente quando IA:

- gera conteúdo em nome do sistema;
- recomenda ações;
- resume informação crítica;
- executa ações;
- influencia decisões relevantes;
- interage diretamente com pessoas.

---

# 15. Como Informar

A informação deverá aparecer no ponto em que seja útil, não escondida em documentação distante.

---

# 16. Linguagem

Preferir linguagem clara e não técnica para usuários finais.

---

# 17. Proporcionalidade

Não sobrecarregar interfaces com avisos irrelevantes.

---

# 18. Limitações

Limitações materiais deverão ser comunicadas.

---

# 19. Incerteza

Não apresentar resultado probabilístico como certeza quando a incerteza for relevante.

---

# 20. Conteúdo Gerado por IA

Quando material, distinguir conteúdo gerado ou assistido por IA de conteúdo humano verificado.

---

# 21. Assistência versus Automação

Diferenciar:

```text
AI-assisted
AI-generated
AI-recommended
AI-executed
```

---

# 22. Recomendações

Recomendações deverão ser apresentadas como recomendações quando não forem decisões determinísticas.

---

# 23. Decisões

Quando IA influenciar decisão de maior impacto, fornecer mecanismo de revisão conforme política aplicável.

---

# 24. Ações Automatizadas

Usuário deverá compreender efeitos relevantes antes de ações mutáveis de alto impacto quando aplicável.

---

# 25. Explicabilidade

Explicabilidade é a capacidade de fornecer informação útil sobre como um resultado foi produzido dentro dos limites técnicos e de segurança.

---

# 26. Explicabilidade Operacional

Deverá permitir reconstruir:

```text
input class
authorized context
retrieved sources
model
provider
configuration
tools
deterministic rules
output/action
```

---

# 27. Explicabilidade Funcional

Explicar em linguagem de produto o que a capacidade faz e não faz.

---

# 28. Explicabilidade de Dados

Quando relevante, indicar quais categorias de dados influenciaram o resultado.

---

# 29. Explicabilidade de RAG

Para respostas fundamentadas em conhecimento, preservar proveniência das fontes conforme GAI-03.

---

# 30. Explicabilidade de Agentes

Registrar ações, tools, aprovações e resultados relevantes.

---

# 31. Explicabilidade de Tools

A execução deverá permitir identificar qual tool produziu determinado efeito.

---

# 32. Explicabilidade de Decisões

Para casos de maior impacto, registrar fatores operacionais e regras relevantes.

---

# 33. Proveniência

Resultados baseados em fontes deverão preservar referências quando possível e apropriado.

---

# 34. Fontes

Fontes apresentadas ao usuário deverão corresponder às fontes realmente utilizadas.

---

# 35. Citações

Não fabricar citações ou referências.

---

# 36. Confidence

Scores de confidence somente deverão ser apresentados quando possuírem significado validado.

---

# 37. Limites de Confidence

Probabilidade de token ou heurística interna não deverá ser apresentada automaticamente como probabilidade de verdade.

---

# 38. Chain-of-Thought

Chain-of-thought interno não deverá ser exigido, armazenado ou exposto como mecanismo padrão de explicabilidade.

---

# 39. Rationale Seguro

Preferir justificativas resumidas baseadas em:

- fontes;
- regras;
- critérios;
- ações observáveis;
- dados autorizados.

---

# 40. Decision Record

Decisões materiais poderão possuir registro conforme GAI-18 e GAI-21.

---

# 41. Model Identity

Identidade técnica do modelo deverá estar disponível internamente quando necessária.

---

# 42. Provider Identity

Provider deverá ser conhecido pelos sistemas de governança.

---

# 43. Prompt Identity

Registrar versão, sem necessidade de expor system prompt ao usuário.

---

# 44. Configuration Identity

Preservar versão da configuração comportamental.

---

# 45. Versionamento

Explicações operacionais deverão ser relacionáveis à versão executada.

---

# 46. User-Facing Explanations

Devem ser:

```text
clear
short
relevant
actionable
non-deceptive
```

---

# 47. Internal Explanations

Podem conter maior profundidade técnica.

---

# 48. Audit Explanations

Devem ser baseadas em evidência, não em narrativa criada posteriormente.

---

# 49. High-Impact Use Cases

Casos de maior impacto exigem transparência e revisão proporcionais.

---

# 50. Human Review

Quando aplicável, disponibilizar caminho para revisão humana.

---

# 51. Contestação

Resultados contestáveis deverão possuir processo adequado para questionamento quando necessário.

---

# 52. Correção

Deverá existir forma de corrigir dados ou resultados materialmente incorretos quando aplicável.

---

# 53. Feedback

Feedback de usuários poderá alimentar avaliação e melhoria.

---

# 54. Escalation

Erros de maior impacto deverão possuir canal de escalonamento.

---

# 55. Comunicação de Erros

Não ocultar falhas materiais com mensagens genéricas de sucesso.

---

# 56. Comunicação de Incidentes

Aplicar GAI-17.

---

# 57. Comunicação de Indisponibilidade

Informar indisponibilidade quando afetar experiência ou operação de forma relevante.

---

# 58. Comunicação de Degradação

Se fallback reduzir capacidade, comunicar quando isso alterar expectativa do usuário.

---

# 59. Comunicação de Mudança

Mudanças materiais deverão seguir GAI-23.

---

# 60. Comunicação de Modelo

Não é necessário expor toda troca interna de modelo ao usuário, salvo quando material para o serviço ou obrigação aplicável.

---

# 61. Comunicação de Provider

Mudanças de provider deverão ser comunicadas aos públicos que precisem dessa informação por contrato, privacidade, operação ou governança.

---

# 62. Comunicação de Depreciação

Consumers deverão receber prazo e alternativa quando aplicável.

---

# 63. Comunicação de Dados

Explicar categorias de dados processadas quando necessário.

---

# 64. Comunicação de Privacidade

Informações de privacidade deverão ser consistentes com o processamento real.

---

# 65. Comunicação de Limites

Exemplos:

- pode produzir erros;
- depende das fontes disponíveis;
- não substitui revisão humana em contexto crítico;
- pode estar temporariamente degradado.

---

# 66. UX

Transparência deverá fazer parte do design da experiência.

---

# 67. Labels

Labels poderão identificar conteúdo ou ações de IA quando úteis.

---

# 68. Notices

Notices deverão aparecer no contexto correto.

---

# 69. Disclaimers

Disclaimers não substituem controles técnicos nem corrigem design inseguro.

---

# 70. Help Content

Documentação de ajuda deverá explicar uso adequado e limitações.

---

# 71. Documentation

Documentação técnica deverá refletir arquitetura e comportamento atuais.

---

# 72. API Consumers

APIs com comportamento de IA deverão documentar:

- semântica;
- limites;
- erros;
- versionamento;
- comportamento de fallback quando relevante.

---

# 73. Developer Communication

Mudanças técnicas materiais deverão possuir comunicação apropriada aos consumidores.

---

# 74. Changelog

Manter changelog quando útil para rastrear alterações comportamentais.

---

# 75. Release Notes

Releases relevantes deverão descrever mudanças que afetem consumidores.

---

# 76. Status Communication

Status operacional deverá distinguir indisponibilidade de degradação quando possível.

---

# 77. Support

Suporte deverá possuir contexto suficiente para explicar limitações conhecidas sem inventar causas.

---

# 78. Training

Equipes deverão saber comunicar capacidades de IA com precisão.

---

# 79. Marketing

Comunicação comercial deverá ser consistente com capacidades reais.

---

# 80. Claims sobre IA

Claims deverão ser verificáveis.

Evitar termos absolutos sem evidência.

---

# 81. Proibições de Comunicação

É proibido comunicar de forma deliberadamente enganosa o papel ou capacidade da IA.

---

# 82. Falsa Precisão

Evitar números de confiança sem base validada.

---

# 83. Falsa Garantia

Não prometer:

```text
100% accurate
never wrong
fully autonomous and safe
zero hallucinations
```

sem fundamento verificável.

---

# 84. Anthropomorphism

Evitar linguagem que atribua intenção, consciência ou autoridade humana ao sistema quando isso puder induzir erro.

---

# 85. Ocultação de Limitações

Limitações materiais não deverão ser omitidas quando relevantes à decisão do usuário.

---

# 86. Dark Patterns

Não utilizar design para induzir aceitação de decisões ou ações de IA contra interesse ou expectativa legítima do usuário.

---

# 87. Manipulação

IA não deverá ser apresentada de forma destinada a explorar vulnerabilidades ou induzir comportamento indevido.

---

# 88. Segurança da Informação

Transparência não exige revelar detalhes que aumentem risco de segurança.

---

# 89. Secrets

Nunca expor secrets em explicações.

---

# 90. Dados Sensíveis

Explicações deverão aplicar minimização.

---

# 91. Prompt Disclosure

System prompts e instruções internas não precisam ser divulgados integralmente.

---

# 92. System Instructions

Podem conter controles, políticas e detalhes internos que devem permanecer protegidos.

---

# 93. Security Controls

Não divulgar detalhes operacionais que facilitem bypass de guardrails.

---

# 94. Auditoria

Comunicações e explicações materiais deverão ser rastreáveis quando necessário.

---

# 95. Evidências

Preservar evidências conforme GAI-18.

---

# 96. Retenção

Logs de explicabilidade deverão seguir políticas de retenção e privacidade.

---

# 97. Métricas

Exemplos:

```text
ai_user_explanations_shown
ai_source_citation_coverage
ai_invalid_citation_rate
ai_human_review_requests
ai_user_contestations
ai_corrections
ai_transparency_findings
ai_misleading_claim_findings
```

---

# 98. Quality Gates

Verificar, quando aplicável:

- disclosure;
- source accuracy;
- limitation text;
- review path;
- correction path;
- no sensitive leakage.

---

# 99. Production Readiness

Antes de produção:

```text
does user need AI disclosure?
limitations documented?
sources traceable?
human review needed?
contest path?
correction path?
communication for failure?
communication for degradation?
sensitive implementation protected?
```

---

# 100. Templates

## AI Transparency Record

```text
Use Case ID:
Owner:
Risk Level:

AI Role:
AI-Assisted:
AI-Generated:
AI-Recommended:
AI-Executed:

User Disclosure Required:
Disclosure Text:
Disclosure Location:

Known Limitations:
Human Review:
Contest Path:
Correction Path:

Sources Available:
Citation Strategy:
Confidence Strategy:

Sensitive Details Protected:
Approval:
Last Review:
```

## AI Explanation Record

```text
Explanation ID:
Use Case:
Request / Decision ID:

Audience:
Purpose:

Model Alias:
Provider:
Prompt Version:
Configuration Version:

Authorized Context:
Source References:
Rules Applied:
Tools Used:
Human Approval:

Outcome:
Explanation Summary:

Sensitive Data Redacted:
Created At:
```

## AI Communication Change Record

```text
Change ID:
Feature:
Owner:

Change Type:
Audience:
Materiality:

Previous Behavior:
New Behavior:
Known Limitations:

Communication Required:
Channels:
Effective Date:

Approval:
Evidence:
```

---

# 101. Anti-Padrões

Evitar:

```text
"AI powered"
without explaining material limitations
```

---

```text
fake citation
to make output look trustworthy
```

---

```text
confidence = 97%
without validated meaning
```

---

```text
"the AI decided"
when humans remain accountable
```

---

```text
full system prompt
published as transparency
```

---

```text
disclaimer
used instead of authorization control
```

---

```text
silent fallback
that materially changes behavior
```

---

```text
marketing claim
stronger than evaluation evidence
```

---

```text
human review
with no way for user to request it
```

---

# 102. Arquitetura Consolidada

```text
                        AI EXECUTION
                             │
                             ▼
                         OUTCOME
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
          SOURCES          ACTIONS         LIMITS
             │               │               │
             └───────────────┼───────────────┘
                             ▼
                    EXPLANATION LAYER
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
           USER           INTERNAL        AUDIT
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                       COMMUNICATION
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
          DISCLOSE         REVIEW          CORRECT
                             │
                             ▼
                          FEEDBACK
                             │
                             ▼
                         IMPROVEMENT
```

---

# 103. Checklist

## Transparência

- [ ] papel da IA identificado;
- [ ] disclosure quando material;
- [ ] linguagem adequada;
- [ ] limitações relevantes;
- [ ] distinção entre assistência, geração, recomendação e execução.

## Explicabilidade

- [ ] modelo/alias rastreável;
- [ ] provider rastreável;
- [ ] prompt version;
- [ ] configuration version;
- [ ] fontes;
- [ ] tools;
- [ ] regras determinísticas;
- [ ] human approval quando aplicável.

## Usuário

- [ ] human review;
- [ ] contestação;
- [ ] correção;
- [ ] feedback;
- [ ] escalation.

## Comunicação

- [ ] erros;
- [ ] indisponibilidade;
- [ ] degradação;
- [ ] mudanças;
- [ ] depreciação;
- [ ] privacidade;
- [ ] limitações.

## Segurança

- [ ] no secrets;
- [ ] no sensitive overexposure;
- [ ] no unnecessary prompt disclosure;
- [ ] no guardrail bypass details.

## Governança

- [ ] owner;
- [ ] evidence;
- [ ] auditability;
- [ ] quality gates;
- [ ] metrics;
- [ ] periodic review.

---

# 104. Documentos Relacionados

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
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 105. Princípios Finais

Transparência não significa despejar detalhes técnicos sobre o usuário.

Significa fornecer informação útil, verdadeira e proporcional.

```text
Explain what matters.

Show relevant sources.

State material limitations.

Preserve human accountability.

Enable review and correction.

Protect sensitive internals.
```

O princípio central é:

```text
Do not make AI look more certain,
more autonomous,
more authoritative,
or more reliable
than it actually is.
```

No GereIgreja, toda comunicação sobre Inteligência Artificial deverá representar com precisão o papel real da tecnologia, preservar a confiança dos usuários e permitir revisão quando o impacto justificar.

---

# 106. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`24-Transparencia-Explicabilidade-e-Comunicacao-de-IA.md`

**Documento**

`GAI-24`

**Código**

`GAI-AI-TRANSPARENCY-EXPLAINABILITY-COMMUNICATION`

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

`GAI-23 — Gestão de Mudanças e Exceções de Inteligência Artificial`

**Próximo documento candidato**

`25-Governanca-de-Datasets-Sinteticos-Fine-Tuning-e-Customizacao-de-Modelos.md`
