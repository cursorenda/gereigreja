# GAI — GereIgreja Artificial Intelligence Engineering

Inteligência Artificial  
↓  
Família canônica de arquitetura, segurança, governança, operação e lifecycle de IA do GereIgreja.

Esta pasta reúne a documentação oficial da família **GAI — GereIgreja Artificial Intelligence Engineering**.

A versão 1.0 da família está **fechada em 35 documentos oficiais**.

O mapa mestre e índice canônico é:

```text
35-Mapa-Mestre-Indice-e-Governanca-Documental-da-Familia-GAI.md
```

## Estado da família

```text
Status: CANÔNICA
Baseline: GAI-01 ... GAI-35
Versão documental: GAI Framework 1.0
Freeze estrutural: SIM
GAI-36+: SOMENTE COM GAP ANALYSIS FORMAL
Prioridade: manutenção, auditoria e consistência
```

A existência de `GAI-35` encerra a expansão automática da família.

## Regra central

```text
Create only when necessary.
Update when sufficient.
Keep domains clear.
Keep references consistent.
Keep ownership explicit.
Keep the family finite and navigable.
```

Em termos práticos:

**evoluir documento existente é a regra; criar novo documento é a exceção.**

## Papel desta pasta

A família GAI cobre, de forma transversal:

- arquitetura e governança de IA;
- providers e modelos;
- prompts e configurações;
- RAG, contexto e conhecimento;
- agentes, ferramentas e ações;
- segurança, privacidade e guardrails;
- governança de dados;
- testes e quality gates;
- deploy e lifecycle;
- observabilidade;
- custos e FinOps;
- riscos de terceiros;
- incidentes e continuidade;
- auditoria e conformidade;
- papéis e responsabilidades;
- uso aceitável;
- mudanças e exceções;
- transparência e explicabilidade;
- fine-tuning e datasets sintéticos;
- red teaming;
- memória e personalização;
- model routing e fallback;
- AI Gateway;
- embeddings e vector stores;
- evaluations e benchmarks;
- fairness e não discriminação;
- production readiness;
- governança documental.

## O README não é o índice mestre

Este README serve apenas como porta de entrada da família.

O inventário completo, domínio de cada documento, ordem de leitura, status e regras de evolução pertencem a:

```text
GAI-35
```

Não manter dois índices completos concorrentes.

## Estrutura conceitual

A família está organizada em oito grandes áreas:

```text
FOUNDATION
MODELS & PROVIDERS
DATA & KNOWLEDGE
AGENTS & ACTIONS
SECURITY & QUALITY
OPERATIONS
GOVERNANCE & ASSURANCE
LIFECYCLE
```

A estrutura detalhada é governada pelo GAI-35.

## Relação com outras famílias

A família GAI é especializada em IA, mas não substitui as autoridades transversais do GereIgreja.

```text
seguranca/
→ política e controles gerais de segurança

qualidade/
→ processos gerais de validação

infraestrutura/
→ ambientes e plataforma técnica

operacoes/
→ runbooks operacionais gerais

backend/
→ padrões de implementação backend

api/
→ contratos de integração

ai/
→ aplicação especializada desses princípios ao domínio de IA
```

Quando um tema é geral da plataforma, sua autoridade permanece na família transversal correspondente.

Quando o tema é específico de IA, o GAI detalha sua aplicação.

## Segurança

Documentos de IA sobre segurança, guardrails, red teaming e incidentes devem permanecer alinhados ao:

```text
docs/frameworks/03-GSF-GereIgreja-Security-Framework.md
docs/seguranca/
```

O GAI não cria uma política geral de segurança paralela.

## Qualidade

Testes, benchmarks, golden datasets, regressão e production readiness de IA devem permanecer alinhados ao:

```text
docs/frameworks/04-GQF-GereIgreja-Quality-Framework.md
docs/qualidade/
```

O GAI define critérios especializados de IA.

## Operações

Observabilidade, tracing, custos, incidentes e continuidade de IA podem exigir runbooks operacionais.

A divisão é:

```text
ai/
→ norma e engenharia especializada de IA

operacoes/
→ procedimento executável recorrente
```

Não duplicar o mesmo runbook integralmente nas duas famílias.

## Infraestrutura

AI Gateway, providers, vector stores, embeddings e observabilidade podem depender de infraestrutura.

A divisão é:

```text
ai/
→ arquitetura, política e governança da capacidade de IA

infraestrutura/
→ serviço, ambiente, disponibilidade e configuração operacional
```

## Source of Truth

A própria família declara:

```text
docs/ai/
```

como fonte documental oficial da GAI.

Dentro dela:

```text
GAI-35
→ mapa documental

GAI-34
→ ponto de entrada para production readiness
```

## Freeze estrutural

O GAI-35 estabelece formalmente:

```text
GAI-01 ... GAI-35
=
FAMILY BASELINE 1.0
```

Portanto:

```text
GAI-36
GAI-37
...
```

não devem ser criados por continuidade numérica.

## Critério para GAI-36+

Novo documento exige Gap Analysis que demonstre que:

1. o tema é material;
2. possui lifecycle próprio;
3. possui controles próprios;
4. não cabe adequadamente em documento existente;
5. não é mero subtópico de disciplina já coberta;
6. a criação reduz ambiguidade mais do que aumenta duplicidade.

Sem essa demonstração, o conteúdo deve ser incorporado a documento existente.

## Evolução sem novos documentos

A família pode evoluir normalmente por versão:

```text
GAI Framework 1.0
GAI Framework 1.1
GAI Framework 1.2
...
GAI Framework 2.0
```

Uma nova versão não exige aumento da quantidade de arquivos.

## Status dos documentos

Os estados oficiais definidos pela família são:

```text
DRAFT
REVIEW
OFFICIAL
DEPRECATED
RETIRED
```

Todo documento deve manter status explícito.

## Ownership

Cada documento deve possuir owner funcional e/ou técnico.

Documento sem responsável claro tende a ficar obsoleto e não deve ser tratado como controle confiável.

## Auditoria documental

A família deve ser revisada periodicamente para identificar:

- duplicidades;
- conflitos;
- referências quebradas;
- documentos obsoletos;
- controles sem owner;
- inconsistência de terminologia;
- divergência entre documentação e implementação;
- divergência entre política geral e regra especializada.

## Relação com o README antigo

O README anterior descrevia apenas:

```text
Prompts
Agentes
MCP
Automações
Contextos
Integrações
```

Esse escopo ficou completamente ultrapassado diante do baseline GAI-01..35.

A família hoje não é apenas um local para documentos sobre uso de IA.

Ela é um **framework completo de engenharia e governança de IA**.

## Princípio de manutenção

A família GAI já é extensa.

Seu principal risco atual não é falta de documentação, mas:

```text
duplicidade
desalinhamento
obsolescência
referências quebradas
controles sem aplicação real
```

**Mais documentos não significam mais governança.**
