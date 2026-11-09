Pasta:

docs/ai/

Arquivo:

35-Mapa-Mestre-Indice-e-Governanca-Documental-da-Familia-GAI.md

Documento:

GAI-35

Código:

GAI-AI-MASTER-MAP-DOCUMENT-GOVERNANCE

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

# GAI-35 — Mapa Mestre, Índice e Governança Documental da Família GAI

> "A família GAI é um sistema documental fechado e governado. Novos documentos só devem existir quando uma lacuna real não puder ser tratada por evolução de um documento existente."

---

# 1. Objetivo

Estabelecer o mapa mestre, índice oficial, domínio de cada documento e regras de evolução da família GAI.

A versão 1.0 da pasta `docs/ai/` é composta por **35 documentos oficiais**.

---

# 2. Estrutura Oficial

```text
GAI
│
├── FOUNDATION
│   ├── GAI-01
│   ├── GAI-10
│   ├── GAI-11
│   ├── GAI-12
│   └── GAI-21
│
├── MODELS & PROVIDERS
│   ├── GAI-02
│   ├── GAI-13
│   ├── GAI-16
│   ├── GAI-28
│   └── GAI-29
│
├── DATA & KNOWLEDGE
│   ├── GAI-03
│   ├── GAI-07
│   ├── GAI-25
│   ├── GAI-27
│   └── GAI-30
│
├── AGENTS & ACTIONS
│   ├── GAI-04
│   └── GAI-14
│
├── SECURITY & QUALITY
│   ├── GAI-06
│   ├── GAI-08
│   ├── GAI-26
│   ├── GAI-32
│   └── GAI-33
│
├── OPERATIONS
│   ├── GAI-05
│   ├── GAI-15
│   ├── GAI-17
│   └── GAI-31
│
├── GOVERNANCE & ASSURANCE
│   ├── GAI-18
│   ├── GAI-20
│   ├── GAI-22
│   ├── GAI-23
│   ├── GAI-24
│   └── GAI-34
│
└── LIFECYCLE
    ├── GAI-09
    ├── GAI-19
    └── GAI-35
```

---

# 3. Índice Oficial dos 35 Documentos

| GAI | Documento |
|---|---|
| 01 | Arquitetura e Governança de Inteligência Artificial |
| 02 | Providers, Modelos, Prompts e AI Gateway |
| 03 | RAG, Contexto e Conhecimento |
| 04 | Ferramentas, Agentes e Ações Seguras |
| 05 | Avaliação, Observabilidade, Custos e Operação de IA |
| 06 | Segurança, Privacidade e Guardrails de IA |
| 07 | Governança de Dados para IA |
| 08 | Testes e Quality Gates para IA |
| 09 | Deploy, Release e Lifecycle de IA |
| 10 | Padrões de Implementação e Referência de IA |
| 11 | Catálogo de Casos de Uso e Níveis de Risco |
| 12 | Registro, Inventário e Governança de Ativos de IA |
| 13 | Governança de Prompts, Modelos e Configurações |
| 14 | Governança de Agentes, Autonomia e Human-in-the-Loop |
| 15 | Gestão de Custos, Capacidade e FinOps |
| 16 | Gestão de Riscos de Terceiros e Providers |
| 17 | Gestão de Incidentes, Continuidade e Recuperação |
| 18 | Auditoria, Evidências e Conformidade |
| 19 | Lifecycle, Desativação e Descomissionamento |
| 20 | Maturidade, KPIs e Roadmap de Governança |
| 21 | Responsabilidades, Papéis e Modelo Operacional |
| 22 | Política de Uso Aceitável e Práticas Proibidas |
| 23 | Gestão de Mudanças e Exceções |
| 24 | Transparência, Explicabilidade e Comunicação |
| 25 | Datasets Sintéticos, Fine-Tuning e Customização de Modelos |
| 26 | Red Teaming, Adversarial Testing e Segurança Ofensiva |
| 27 | Memória, Contexto Persistente e Personalização |
| 28 | Model Routing, Fallback e Resiliência Multi-Provider |
| 29 | AI Gateway, Policy Enforcement e Controle Centralizado |
| 30 | Embeddings, Vector Stores e Busca Semântica |
| 31 | Observabilidade, Tracing e Telemetria Avançada |
| 32 | Evaluations, Benchmarks, Golden Datasets e Regressão |
| 33 | Avaliação de Impacto, Fairness, Bias e Não Discriminação |
| 34 | Matriz de Controles por Nível de Risco e Production Readiness |
| 35 | Mapa Mestre, Índice e Governança Documental da Família GAI |

---

# 4. Ordem de Leitura Recomendada

## Engenharia começando uma feature

```text
GAI-11
→ GAI-34
→ documentos específicos do domínio
→ GAI-08
→ GAI-09
```

## Arquitetura

```text
GAI-01
→ GAI-02
→ GAI-10
→ GAI-29
→ GAI-34
```

## Segurança

```text
GAI-06
→ GAI-14
→ GAI-26
→ GAI-33
→ GAI-34
```

## Operações

```text
GAI-05
→ GAI-15
→ GAI-17
→ GAI-31
```

---

# 5. Regra de Criação de Novos Documentos

A criação de `GAI-36` ou superior exige Gap Analysis formal.

A Gap Analysis deverá provar que:

```text
1. o tema é material;
2. possui lifecycle próprio;
3. possui controles próprios;
4. não cabe adequadamente em documento existente;
5. não é apenas subtópico de uma disciplina já coberta;
6. a criação reduz ambiguidade mais do que aumenta duplicidade;
```

Sem essa demonstração, o conteúdo deverá ser incorporado a documento existente.

---

# 6. Regra de Atualização

Preferir:

```text
update existing document
```

em vez de:

```text
create new document
```

quando o novo conteúdo pertencer claramente a um domínio já definido.

---

# 7. Versionamento da Família

Versões:

```text
GAI Framework 1.0
GAI Framework 1.1
GAI Framework 1.2
...
GAI Framework 2.0
```

Mudanças menores podem atualizar documentos sem alterar o total.

Mudanças estruturais podem alterar domínios ou quantidade apenas mediante revisão formal.

---

# 8. Source of Truth

A pasta oficial:

```text
docs/ai/
```

deverá ser considerada a fonte documental oficial da família GAI.

---

# 9. Consistência Obrigatória

Todos os documentos deverão manter:

- código GAI;
- versão;
- status;
- owner;
- data de atualização;
- documentos relacionados;
- linguagem normativa consistente;
- referências cruzadas corretas.

---

# 10. Auditoria Documental Periódica

A família deverá ser auditada para:

- duplicidades;
- conflitos;
- links quebrados;
- referências inexistentes;
- controles sem owner;
- templates divergentes;
- terminologia inconsistente;
- documentos obsoletos.

---

# 11. Status de Documento

Estados:

```text
DRAFT
REVIEW
OFFICIAL
DEPRECATED
RETIRED
```

---

# 12. Ownership

Cada documento deverá possuir owner funcional e/ou técnico.

---

# 13. Relação com GAI-34

GAI-34 é o ponto de entrada operacional.

GAI-35 é o ponto de entrada documental.

```text
Need to ship AI?
→ GAI-34

Need to understand the documentation?
→ GAI-35
```

---

# 14. Freeze Estrutural da Versão 1.0

Após aprovação do GAI-35:

```text
GAI-01 ... GAI-35
=
FAMILY BASELINE 1.0
```

Nenhum documento adicional deverá ser criado por continuidade automática de numeração.

---

# 15. Próxima Fase

Após fechamento dos 35 documentos, a prioridade passa a ser:

```text
1. auditoria transversal;
2. correção de referências cruzadas;
3. padronização de cabeçalhos;
4. classificação normative SHOULD/MUST/MAY;
5. revisão de duplicidades;
6. geração de índice navegável;
7. baseline GAI Framework 1.0.
```

---

# 16. Princípios Finais

```text
More Documents
≠
More Governance
```

A regra central é:

```text
Create only when necessary.
Update when sufficient.
Keep domains clear.
Keep references consistent.
Keep ownership explicit.
Keep the family finite and navigable.
```

---

# 17. Status do Documento

**Arquivo**

`35-Mapa-Mestre-Indice-e-Governanca-Documental-da-Familia-GAI.md`

**Documento**

`GAI-35`

**Versão**

`1.0`

**Status**

`OFICIAL`

**Marco**

`FECHAMENTO DA FAMÍLIA GAI — BASELINE 1.0`
