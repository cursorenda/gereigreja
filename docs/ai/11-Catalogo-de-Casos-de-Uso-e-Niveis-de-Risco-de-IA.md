Pasta:

docs/ai/

Arquivo:

11-Catalogo-de-Casos-de-Uso-e-Niveis-de-Risco-de-IA.md

Documento:

GAI-11

Código:

GAI-AI-USE-CASE-RISK-CATALOG

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

# GAI-11 — Catálogo de Casos de Uso e Níveis de Risco de Inteligência Artificial

> "O nível de controle de uma capacidade de IA deve ser proporcional ao impacto que ela pode produzir."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Por que Classificar Casos de Uso
6. Unidade de Classificação
7. Dimensões de Risco
8. Impacto sobre Pessoas
9. Impacto Financeiro
10. Impacto Operacional
11. Impacto de Segurança
12. Impacto de Privacidade
13. Sensibilidade dos Dados
14. Autonomia
15. Reversibilidade
16. Alcance
17. Dependência da IA
18. Exposição Externa
19. Níveis de Risco
20. Risco R0 — Mínimo
21. Risco R1 — Baixo
22. Risco R2 — Moderado
23. Risco R3 — Alto
24. Risco R4 — Crítico
25. Matriz de Classificação
26. Regras de Elevação de Risco
27. Casos Proibidos por Padrão
28. Casos que Exigem Revisão
29. Casos Assistivos
30. Geração de Texto
31. Resumos
32. Classificação
33. Extração Estruturada
34. Recomendações
35. Pesquisa e RAG
36. Comunicação
37. Dados de Membros
38. Dados Ministeriais
39. Dados Financeiros
40. Dados Sensíveis
41. Automação
42. Tools
43. Agentes
44. Ações Mutáveis
45. Ações Destrutivas
46. Decisões Automatizadas
47. Conteúdo Público
48. Integrações Externas
49. Casos Internos de Engenharia
50. Desenvolvimento Assistido
51. Operações e Suporte
52. Segurança
53. Avaliação de Risco
54. Registro do Caso de Uso
55. Use Case ID
56. Owner
57. Finalidade
58. Usuários
59. Dados
60. Provider
61. Modelo
62. Tools
63. Autonomia
64. Guardrails
65. Human-in-the-Loop
66. Avaliação
67. Observabilidade
68. Retenção
69. Rollout
70. Kill Switch
71. Aprovação
72. Reavaliação
73. Mudanças que Exigem Reclassificação
74. Exceções
75. Catálogo Inicial
76. Template de Registro
77. Production Readiness
78. Auditoria
79. Anti-Padrões
80. Arquitetura Consolidada
81. Checklist
82. Documentos Relacionados
83. Princípios Finais
84. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para catalogar, classificar e governar casos de uso de Inteligência Artificial no GereIgreja conforme seu nível de risco.

O objetivo é evitar que funcionalidades com impactos radicalmente diferentes recebam os mesmos controles.

---

# 2. Escopo

Aplica-se a qualquer funcionalidade que utilize IA, incluindo:

- assistentes;
- geração de texto;
- classificação;
- sumarização;
- RAG;
- recomendações;
- extração;
- tools;
- agentes;
- automações;
- integrações;
- recursos internos de engenharia.

---

# 3. Relação com a Família GAI

```text
GAI-01 ... GAI-10
Architecture / Controls / Implementation
            │
            ▼
          GAI-11
   Use Case Risk Catalog
            │
            ▼
Required Controls
```

O GAI-11 determina quais controles dos demais documentos deverão receber maior rigor em cada caso de uso.

---

# 4. Princípios Fundamentais

Aplicar:

- risk proportionality;
- explicit ownership;
- documented purpose;
- data awareness;
- bounded autonomy;
- human control;
- traceability;
- reclassification on change;
- safe defaults;
- no silent high-risk AI.

---

# 5. Por que Classificar Casos de Uso

Não possuem o mesmo risco:

```text
reformular um título
```

e:

```text
executar uma operação financeira
```

Portanto, o processo de engenharia deverá distinguir essas categorias antes da implementação.

---

# 6. Unidade de Classificação

A classificação deverá ocorrer por caso de uso ou feature suficientemente específica.

Evitar classificar genericamente:

```text
"IA do GereIgreja"
```

Preferir:

```text
"resumo de ata"
"assistente RAG de documentação"
"preparação de comunicado"
"agente de operação X"
```

---

# 7. Dimensões de Risco

Avaliar pelo menos:

- impacto;
- dados;
- autonomia;
- reversibilidade;
- alcance;
- exposição;
- dependência.

---

# 8. Impacto sobre Pessoas

Considerar se a saída poderá afetar significativamente uma pessoa.

---

# 9. Impacto Financeiro

Operações financeiras elevam o risco.

---

# 10. Impacto Operacional

Considerar capacidade de alterar recursos ou processos da plataforma.

---

# 11. Impacto de Segurança

Considerar acesso a:

- permissões;
- credenciais;
- configurações;
- infraestrutura;
- dados protegidos.

---

# 12. Impacto de Privacidade

Considerar exposição, inferência ou processamento de dados pessoais.

---

# 13. Sensibilidade dos Dados

Quanto maior a sensibilidade, maior o rigor necessário.

---

# 14. Autonomia

Escala conceitual:

```text
inform
→ recommend
→ prepare
→ execute with confirmation
→ execute autonomously
```

O risco cresce com autonomia.

---

# 15. Reversibilidade

Ações irreversíveis ou difíceis de desfazer elevam o risco.

---

# 16. Alcance

Considerar quantas pessoas, registros, tenants ou sistemas podem ser afetados.

---

# 17. Dependência da IA

Quanto mais uma decisão depender exclusivamente da IA, maior deverá ser a cautela.

---

# 18. Exposição Externa

Ações que publicam ou enviam conteúdo externamente possuem risco adicional.

---

# 19. Níveis de Risco

O GereIgreja adota cinco níveis:

```text
R0 — Mínimo
R1 — Baixo
R2 — Moderado
R3 — Alto
R4 — Crítico
```

---

# 20. Risco R0 — Mínimo

Características típicas:

- conteúdo não sensível;
- sem mutação;
- sem impacto relevante;
- usuário revisa naturalmente a saída.

Exemplos:

- reformulação de texto genérico;
- geração de título;
- explicação de documentação pública.

Controles mínimos:

- provider aprovado;
- logging básico;
- limites de uso;
- testes funcionais.

---

# 21. Risco R1 — Baixo

Características:

- assistência de produtividade;
- dados internos de baixa sensibilidade;
- sem ação autônoma;
- impacto facilmente reversível.

Exemplos:

- resumo de documento interno autorizado;
- geração de rascunho;
- classificação não crítica.

Controles adicionais:

- tenant;
- autorização;
- minimização;
- avaliação básica;
- observabilidade.

---

# 22. Risco R2 — Moderado

Características:

- dados pessoais;
- RAG interno;
- recomendações relevantes;
- preparação de ações;
- integração com dados operacionais.

Exemplos:

- assistente de conhecimento interno;
- resumo de dados autorizados de membros;
- preparação de comunicado;
- extração estruturada para revisão.

Controles:

- avaliação versionada;
- testes cross-tenant;
- guardrails;
- data governance;
- feature flag;
- owner;
- quality gates.

---

# 23. Risco R3 — Alto

Características:

- dados sensíveis;
- tools mutáveis;
- comunicação externa em escala;
- impacto financeiro;
- agente multi-step;
- ações operacionais relevantes.

Exemplos:

- agente que prepara e executa ações após confirmação;
- automação financeira assistida;
- envio amplo de comunicação;
- operações com dados altamente restritos.

Controles reforçados:

- threat model;
- revisão de segurança;
- human-in-the-loop;
- audit trail;
- kill switch;
- canary;
- adversarial tests;
- runbook;
- monitoramento reforçado.

---

# 24. Risco R4 — Crítico

Características:

- ação autônoma de alto impacto;
- alteração irreversível;
- capacidade ampla sobre múltiplos tenants;
- decisões altamente sensíveis;
- acesso privilegiado crítico.

R4 deverá ser proibido por padrão até aprovação arquitetural e de segurança específica.

Exemplos conceituais:

- agente autônomo com acesso administrativo amplo;
- exclusão massiva autônoma;
- alteração autônoma de permissões privilegiadas;
- movimentação financeira autônoma.

---

# 25. Matriz de Classificação

| Dimensão | Menor risco | Maior risco |
|---|---|---|
| Dados | públicos | sensíveis/restritos |
| Ação | leitura | mutação destrutiva |
| Autonomia | sugestão | execução autônoma |
| Alcance | registro único | escala ampla |
| Reversibilidade | simples | irreversível |
| Exposição | interna | externa |
| Tenant | isolado | multi-tenant privilegiado |
| Decisão | assistiva | determinante |

A classificação final deverá refletir o maior risco material, não apenas uma média matemática.

---

# 26. Regras de Elevação de Risco

Elevar classificação quando houver:

- dados sensíveis;
- ação financeira;
- alteração de permissões;
- ação destrutiva;
- execução sem confirmação;
- comunicação externa em escala;
- múltiplos tenants;
- baixa reversibilidade.

---

# 27. Casos Proibidos por Padrão

Sem aprovação específica, não implementar:

```text
LLM
→ arbitrary SQL
```

```text
LLM
→ unrestricted shell
```

```text
autonomous privileged permission changes
```

```text
cross-tenant unrestricted agent
```

```text
autonomous destructive bulk action
```

---

# 28. Casos que Exigem Revisão

R3 e R4 deverão receber revisão formal proporcional ao impacto.

---

# 29. Casos Assistivos

Preferir IA assistiva quando o benefício não exige autonomia.

---

# 30. Geração de Texto

Normalmente R0–R2, dependendo dos dados e destino.

---

# 31. Resumos

Risco depende da sensibilidade da fonte.

---

# 32. Classificação

Classificações que controlam decisões críticas deverão receber nível superior.

---

# 33. Extração Estruturada

Quando alimenta lógica automática, exigir validação rigorosa.

---

# 34. Recomendações

Recomendação poderá ter risco maior quando influencia decisões relevantes.

---

# 35. Pesquisa e RAG

RAG interno tenant-scoped deverá ser no mínimo avaliado quanto a isolamento e autorização.

---

# 36. Comunicação

Rascunho é menos arriscado que envio automático.

```text
draft
<
send after confirmation
<
autonomous bulk send
```

---

# 37. Dados de Membros

Classificação dependerá dos campos utilizados e finalidade.

---

# 38. Dados Ministeriais

Conteúdo pastoral ou de aconselhamento deverá receber classificação reforçada.

---

# 39. Dados Financeiros

Casos que envolvem valores ou registros financeiros deverão possuir controles reforçados.

---

# 40. Dados Sensíveis

A presença de dados sensíveis poderá elevar o caso para R2 ou superior.

---

# 41. Automação

Automação eleva o risco quando remove revisão humana.

---

# 42. Tools

Tool somente leitura possui risco menor que tool mutável.

---

# 43. Agentes

Agentes multi-step deverão ser no mínimo avaliados como R2, podendo subir conforme tools e dados.

---

# 44. Ações Mutáveis

Normalmente R2 ou superior.

---

# 45. Ações Destrutivas

Normalmente R3 ou R4.

---

# 46. Decisões Automatizadas

Decisões com impacto relevante sobre pessoas exigem avaliação jurídica, de produto, segurança e governança quando aplicável.

---

# 47. Conteúdo Público

Publicação automática possui risco reputacional e deverá ser tratada acima de simples geração de rascunho.

---

# 48. Integrações Externas

Avaliar dados enviados e efeitos externos.

---

# 49. Casos Internos de Engenharia

Ferramentas internas também precisam de classificação.

Acesso privilegiado pode tornar uma ferramenta interna R3 ou R4.

---

# 50. Desenvolvimento Assistido

Sugestão de código é diferente de execução autônoma em produção.

---

# 51. Operações e Suporte

Assistência diagnóstica poderá ser R1/R2.

Execução operacional privilegiada poderá ser R3/R4.

---

# 52. Segurança

IA não deverá tomar autonomamente decisões privilegiadas sem controles determinísticos.

---

# 53. Avaliação de Risco

Fluxo recomendado:

```text
Define Use Case
      ↓
Identify Data
      ↓
Identify Actions
      ↓
Measure Autonomy
      ↓
Measure Impact
      ↓
Classify Risk
      ↓
Apply Required Controls
```

---

# 54. Registro do Caso de Uso

Casos R2+ deverão possuir registro formal.

R0/R1 poderão utilizar registro simplificado conforme processo da equipe.

---

# 55. Use Case ID

Formato sugerido:

```text
AI-UC-###
```

---

# 56. Owner

Todo caso deverá possuir owner técnico.

---

# 57. Finalidade

Registrar objetivo específico.

---

# 58. Usuários

Identificar quem utilizará a feature.

---

# 59. Dados

Registrar categorias e classificação.

---

# 60. Provider

Registrar provider aprovado.

---

# 61. Modelo

Registrar alias ou modelo quando relevante.

---

# 62. Tools

Registrar tools disponíveis.

---

# 63. Autonomia

Registrar nível de autonomia.

---

# 64. Guardrails

Registrar controles específicos.

---

# 65. Human-in-the-Loop

Indicar quando confirmação é necessária.

---

# 66. Avaliação

Definir dataset, métricas e thresholds quando aplicável.

---

# 67. Observabilidade

Definir sinais mínimos.

---

# 68. Retenção

Registrar dados persistidos e prazo.

---

# 69. Rollout

Definir estratégia proporcional ao risco.

---

# 70. Kill Switch

R3+ deverá possuir mecanismo explícito de contenção quando tecnicamente aplicável.

---

# 71. Aprovação

A aprovação deverá ser proporcional ao risco.

---

# 72. Reavaliação

Casos deverão ser reavaliados periodicamente ou quando sofrerem mudanças relevantes.

---

# 73. Mudanças que Exigem Reclassificação

Exemplos:

- nova categoria de dados;
- nova tool;
- maior autonomia;
- novo provider;
- novo público;
- maior alcance;
- ação antes somente leitura torna-se mutável.

---

# 74. Exceções

Exceções deverão possuir:

- justificativa;
- risco;
- owner;
- aprovação;
- validade temporal.

---

# 75. Catálogo Inicial

Exemplo de catálogo:

| Caso de Uso | Risco Inicial | Observação |
|---|---:|---|
| Reformular texto genérico | R0 | Sem dados sensíveis |
| Gerar rascunho interno | R1 | Revisão humana |
| Resumir documento tenant-scoped | R2 | Autorização e minimização |
| Assistente RAG interno | R2 | Retrieval tenant-scoped |
| Preparar comunicação a membros | R2 | Preview obrigatório |
| Enviar comunicação após confirmação | R3 | Audit + confirmation |
| Agente com tools mutáveis | R3 | Limites + HITL |
| Exclusão massiva autônoma | R4 | Proibido por padrão |
| Alteração autônoma de privilégios | R4 | Proibido por padrão |

A classificação real deverá considerar implementação, dados e alcance específicos.

---

# 76. Template de Registro

```text
Use Case ID:
Nome:
Owner:
Descrição:
Finalidade:

Usuários:
Tenants afetados:

Dados utilizados:
Classificação dos dados:
Fonte:

Provider:
Modelo/alias:
Prompt ID:

RAG:
Tools:
Agente:

Nível de autonomia:
Ações mutáveis:
Ações destrutivas:

Human-in-the-Loop:
Guardrails:

Risco:
Justificativa:

Evaluation Dataset:
Métricas:
Thresholds:

Logs:
Métricas:
Auditoria:

Retenção:
Feature Flag:
Rollout:
Rollback:
Kill Switch:

Aprovação:
Data da revisão:
Próxima revisão:
```

---

# 77. Production Readiness

Antes de produção, o nível de risco deverá estar conhecido.

Caso de uso sem classificação não deverá avançar para produção quando estiver sujeito a este framework.

---

# 78. Auditoria

Deverá ser possível demonstrar:

- classificação;
- owner;
- controles;
- aprovação;
- mudanças relevantes.

---

# 79. Anti-Padrões

Evitar:

```text
"é só IA"
→ no risk review
```

---

```text
all AI features
=
same controls
```

---

```text
draft generation
=
autonomous execution
```

---

```text
R0 classification
while processing sensitive data
```

---

```text
agent gets new tool
without reclassification
```

---

```text
R4
enabled by feature flag alone
```

---

```text
risk level
based only on model name
```

---

# 80. Arquitetura Consolidada

```text
                       USE CASE
                           │
                           ▼
                       PURPOSE
                           │
                           ▼
                         DATA
                           │
                           ▼
                        ACTIONS
                           │
                           ▼
                       AUTONOMY
                           │
                           ▼
                        IMPACT
                           │
                           ▼
                    RISK CLASSIFIER
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
        R0/R1             R2               R3/R4
          │                │                │
          ▼                ▼                ▼
      Baseline         Enhanced         Strict
      Controls         Controls         Controls
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    QUALITY / SECURITY
                           │
                           ▼
                        RELEASE
                           │
                           ▼
                      REASSESSMENT
```

---

# 81. Checklist

## Caso de Uso

- [ ] ID;
- [ ] nome;
- [ ] finalidade;
- [ ] owner;
- [ ] usuários;
- [ ] tenants.

## Dados

- [ ] fontes;
- [ ] classificação;
- [ ] minimização;
- [ ] retenção;
- [ ] provider compatibility.

## Comportamento

- [ ] modelo;
- [ ] prompt;
- [ ] RAG;
- [ ] tools;
- [ ] agente;
- [ ] autonomia.

## Impacto

- [ ] pessoas;
- [ ] financeiro;
- [ ] operacional;
- [ ] segurança;
- [ ] privacidade;
- [ ] reversibilidade;
- [ ] alcance.

## Controles

- [ ] autorização;
- [ ] tenant;
- [ ] guardrails;
- [ ] HITL;
- [ ] limits;
- [ ] audit;
- [ ] kill switch quando necessário.

## Qualidade

- [ ] dataset;
- [ ] métricas;
- [ ] thresholds;
- [ ] adversarial tests;
- [ ] quality gate.

## Release

- [ ] feature flag;
- [ ] rollout;
- [ ] rollback;
- [ ] observabilidade;
- [ ] aprovação.

## Lifecycle

- [ ] risco registrado;
- [ ] revisão;
- [ ] reclassificação após mudança;
- [ ] exceções com prazo.

---

# 82. Documentos Relacionados

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
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 83. Princípios Finais

O risco de IA não é determinado apenas pelo modelo.

```text
Risk
=
Data
+
Action
+
Autonomy
+
Impact
+
Reach
+
Reversibility
```

O princípio central é:

```text
Low-risk AI
should remain simple.

High-risk AI
must earn autonomy
through stronger controls.
```

No GereIgreja, nenhuma capacidade de IA deverá receber mais autonomia, dados ou alcance do que o necessário para cumprir sua finalidade.

---

# 84. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`11-Catalogo-de-Casos-de-Uso-e-Niveis-de-Risco-de-IA.md`

**Documento**

`GAI-11`

**Código**

`GAI-AI-USE-CASE-RISK-CATALOG`

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

`GAI-10 — Padrões de Implementação e Referência de Inteligência Artificial`

**Próximo documento candidato**

`12-Registro-Inventario-e-Governanca-de-Ativos-de-IA.md`
