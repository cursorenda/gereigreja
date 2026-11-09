Pasta:

docs/ai/

Arquivo:

01-Arquitetura-e-Governanca-de-Inteligencia-Artificial.md

Documento:

GAI-01

Código:

GAI-AI-ARCHITECTURE-GOVERNANCE

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

# GAI-01 — Arquitetura e Governança de Inteligência Artificial

> "A IA deve ampliar a capacidade da plataforma sem substituir as regras de negócio, a segurança, a autorização ou a responsabilidade humana."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel da IA no GereIgreja
4. Princípios Arquiteturais
5. IA não é Fonte de Verdade
6. Arquitetura Multi-Tenant
7. Menor Privilégio
8. Provider Agnostic
9. Human-in-the-Loop
10. Arquitetura Lógica
11. Interface de Uso
12. Orquestração
13. Context Builder
14. AI Gateway
15. Retrieval
16. Tool e Action Layer
17. Guardrails
18. Observabilidade
19. Integração com Backend
20. Services e Selectors
21. Providers e Modelos
22. Capacidades de IA
23. Seleção de Modelo
24. Configuração
25. Secrets
26. Prompts
27. Versionamento de Prompts
28. Contexto
29. Minimização de Dados
30. Prompt Injection
31. RAG
32. Recuperação de Conhecimento
33. Metadados
34. Isolamento no Retrieval
35. Índices
36. Ferramentas
37. Agentes
38. Ações Executáveis
39. Allowlist
40. Confirmação Humana
41. Segurança
42. Privacidade
43. Dados Sensíveis
44. Providers Externos
45. Saídas Estruturadas
46. Validação
47. Auditoria
48. Logs
49. Métricas
50. Custos
51. Quotas
52. Rate Limiting
53. Resiliência
54. Timeouts
55. Retries
56. Fallback
57. Degradação Controlada
58. Avaliação
59. Quality Gates
60. Testes Adversariais
61. Regressão
62. Ciclo de Vida
63. Feature Flags
64. Classificação de Risco
65. Baixo Risco
66. Médio Risco
67. Alto Risco
68. Critérios para Produção
69. Anti-Padrões
70. Relação com Documentação Existente
71. Próximos Documentos
72. Checklist
73. Documentos Relacionados
74. Princípios Finais
75. Status do Documento

---

# 1. Objetivo

Este documento estabelece a arquitetura, os limites operacionais e os princípios de governança para recursos de Inteligência Artificial no GereIgreja.

Seu objetivo é permitir a evolução segura e consistente das capacidades de IA sem acoplá-las de forma irreversível a:

- um fornecedor;
- um modelo;
- uma interface;
- uma estratégia específica de execução.

A IA deverá ser tratada como uma capacidade assistiva da plataforma.

Ela não substitui:

- regras de negócio;
- autorização;
- validação;
- auditoria;
- isolamento entre igrejas;
- responsabilidade humana.

---

# 2. Escopo

Aplica-se a:

- assistentes;
- chat;
- geração de conteúdo;
- classificação;
- extração;
- sumarização;
- embeddings;
- RAG;
- agentes;
- tools;
- ações assistidas;
- automações com IA;
- integrações com modelos externos;
- modelos futuros executados internamente.

---

# 3. Papel da IA no GereIgreja

A IA deverá ampliar capacidades já existentes na plataforma.

Exemplos:

```text
buscar
resumir
explicar
organizar
sugerir
classificar
preparar
automatizar sob controle
```

Não deverá criar uma arquitetura paralela ao domínio existente.

---

# 4. Princípios Arquiteturais

Toda capacidade de IA deverá seguir:

- segurança por padrão;
- tenant explícito;
- menor privilégio;
- provider agnostic;
- minimização de dados;
- observabilidade;
- avaliação;
- fallback;
- human-in-the-loop proporcional ao risco;
- integração com services e regras existentes.

---

# 5. IA não é Fonte de Verdade

Dados persistidos pelo GereIgreja, regras de domínio e permissões continuam sendo as fontes autoritativas.

Saídas de modelos são probabilísticas.

Deverão ser tratadas como:

- propostas;
- classificações;
- resumos;
- conteúdo gerado;
- interpretações;
- sugestões.

Nunca como autorização automática.

---

# 6. Arquitetura Multi-Tenant

Nenhum contexto enviado a um modelo poderá misturar informações pertencentes a igrejas distintas.

A resolução do tenant deverá ocorrer antes da construção do contexto.

```text
User
  ↓
Authentication
  ↓
Tenant Resolution
  ↓
Authorization
  ↓
Context Builder
  ↓
AI
```

---

# 7. Menor Privilégio

Uma capacidade de IA somente poderá consultar dados e propor ou executar ações que o usuário autenticado teria autorização para realizar pela aplicação convencional.

```text
AI permission
<=
User permission
```

---

# 8. Provider Agnostic

Código de domínio não deverá depender diretamente de SDKs de fornecedores de IA.

Integrações externas deverão ficar atrás de interfaces internas.

```text
Application
    │
    ▼
AI Gateway
    │
    ├── Provider A
    ├── Provider B
    └── Future Provider
```

---

# 9. Human-in-the-Loop

Ações de impacto relevante deverão exigir confirmação humana explícita quando apropriado.

Especialmente:

- operações financeiras;
- alterações cadastrais relevantes;
- comunicação em massa;
- exclusão;
- mudança de permissões;
- exposição de dados;
- decisões sobre pessoas.

---

# 10. Arquitetura Lógica

```text
User / UI / API
       │
       ▼
AI Orchestrator
       │
       ├── Authorization
       ├── Context Builder
       ├── Guardrails
       │
       ▼
    AI Gateway
       │
       ├── Models
       ├── Embeddings
       └── Structured Output
       │
       ├───────────────┐
       ▼               ▼
   Retrieval        Tool Layer
       │               │
       ▼               ▼
 Knowledge Base     Services
       │               │
       └───────┬───────┘
               ▼
        Validation/Audit
```

---

# 11. Interface de Uso

A interface poderá ser:

- chat;
- botão assistido;
- sugestão contextual;
- API;
- automação;
- painel.

A UI não deverá conter regras críticas de IA.

---

# 12. Orquestração

A orquestração deverá identificar:

- usuário;
- tenant;
- intenção;
- política;
- contexto;
- modelo/capacidade;
- ferramentas permitidas;
- necessidade de confirmação.

---

# 13. Context Builder

O Context Builder deverá construir apenas o contexto necessário e autorizado.

Responsabilidades:

- tenant;
- autorização;
- minimização;
- recuperação;
- normalização;
- limite de contexto.

---

# 14. AI Gateway

O AI Gateway deverá abstrair:

- provider;
- modelo;
- timeout;
- retry;
- fallback;
- tokens;
- custo;
- saída estruturada;
- embeddings;
- tools quando aplicável.

---

# 15. Retrieval

Retrieval deverá recuperar somente conteúdo autorizado.

Não deverá depender de filtragem feita apenas depois da geração.

---

# 16. Tool e Action Layer

Ferramentas disponibilizadas à IA deverão reutilizar operações existentes da aplicação.

```text
AI Tool
   ↓
Application Service
   ↓
Domain Rules
   ↓
Persistence
```

---

# 17. Guardrails

Guardrails deverão existir em múltiplas etapas:

```text
Input
  ↓
Context
  ↓
Model
  ↓
Output
  ↓
Action
```

---

# 18. Observabilidade

Toda operação relevante de IA deverá ser observável.

---

# 19. Integração com Backend

Recursos de IA deverão reutilizar:

- services;
- selectors;
- políticas de autorização;
- validações;
- auditoria.

Não deverão acessar modelos Django arbitrariamente.

---

# 20. Services e Selectors

O AI Layer deverá agir como consumidor da arquitetura Backend.

Exemplo:

```text
AI
→ Selector autorizado
→ Dados

AI Action
→ Service
→ Regra de negócio
```

---

# 21. Providers e Modelos

Providers e modelos deverão ser tratados como dependências substituíveis.

---

# 22. Capacidades de IA

A aplicação deverá solicitar capacidade, não necessariamente modelo concreto.

Exemplos:

```text
text_generation
classification
structured_extraction
embedding
summarization
tool_use
```

---

# 23. Seleção de Modelo

A seleção poderá considerar:

- qualidade;
- custo;
- latência;
- contexto;
- suporte a tools;
- saída estruturada;
- privacidade;
- disponibilidade.

---

# 24. Configuração

Cada capacidade poderá declarar:

- provider;
- modelo;
- finalidade;
- timeout;
- limite de tokens;
- retry;
- fallback;
- orçamento;
- política de dados.

---

# 25. Secrets

Chaves de API nunca deverão existir em:

- prompts;
- código;
- logs;
- documentação pública;
- frontend.

Aplicar GSF-09 e GINF-02.

---

# 26. Prompts

Prompts relevantes deverão ser tratados como artefatos de engenharia.

---

# 27. Versionamento de Prompts

Mudanças materiais deverão ser:

- versionadas;
- revisáveis;
- testáveis;
- associáveis a releases quando necessário.

---

# 28. Contexto

Contexto deverá conter apenas o necessário para cumprir a tarefa.

---

# 29. Minimização de Dados

Dados pessoais, financeiros, ministeriais ou sensíveis exigem justificativa funcional e controles adequados.

---

# 30. Prompt Injection

Conteúdo recuperado de:

- documentos;
- usuários;
- páginas;
- integrações;

deverá ser considerado não confiável como instrução.

Texto recuperado não poderá sobrescrever:

- políticas de sistema;
- autorização;
- regras de execução.

---

# 31. RAG

Retrieval-Augmented Generation deverá separar:

```text
Knowledge Retrieval
≠
Authorization
```

Autorização vem antes.

---

# 32. Recuperação de Conhecimento

Todo fragmento recuperado deverá possuir contexto suficiente para saber sua origem e escopo.

---

# 33. Metadados

Metadados recomendados:

- tenant;
- documento;
- origem;
- tipo;
- classificação;
- versão;
- permissões relevantes.

---

# 34. Isolamento no Retrieval

Um documento não autorizado não poderá ser inserido no contexto do modelo.

```text
Unauthorized document
X
Model context
```

---

# 35. Índices

Índices compartilhados somente serão aceitáveis quando o isolamento lógico for tecnicamente obrigatório, verificável e testado.

Conteúdo mais sensível poderá exigir segregação adicional.

---

# 36. Ferramentas

Ferramentas são operações estruturadas disponibilizadas ao modelo.

---

# 37. Agentes

Agentes deverão operar dentro de limites explícitos.

Agente não significa autonomia irrestrita.

---

# 38. Ações Executáveis

Texto livre não deverá virar diretamente operação privilegiada.

Fluxo obrigatório:

```text
Model Proposal
   ↓
Structured Schema
   ↓
Validation
   ↓
Authorization
   ↓
Business Rule
   ↓
Confirmation if required
   ↓
Execution
```

---

# 39. Allowlist

Somente ferramentas explicitamente aprovadas deverão ser disponibilizadas.

---

# 40. Confirmação Humana

A aplicação deverá diferenciar:

- resposta informativa;
- sugestão;
- ação preparada;
- ação aguardando confirmação;
- ação executada.

---

# 41. Segurança

Aplicar integralmente o GSF.

Riscos específicos de IA incluem:

- prompt injection;
- exfiltração de contexto;
- abuso de tools;
- vazamento cross-tenant;
- conteúdo adversarial;
- execução excessiva;
- exposição de dados.

---

# 42. Privacidade

Dados enviados a providers externos deverão respeitar políticas de privacidade e requisitos legais.

---

# 43. Dados Sensíveis

Nunca enviar ao modelo:

- senhas;
- tokens de sessão;
- private keys;
- secrets de infraestrutura;
- credenciais de integração.

---

# 44. Providers Externos

Antes de utilizar provider externo, avaliar:

- retenção de dados;
- uso para treinamento;
- localização;
- segurança;
- contrato;
- disponibilidade.

---

# 45. Saídas Estruturadas

Quando uma resposta alimentar código, preferir schema estruturado.

---

# 46. Validação

Toda saída de modelo deverá ser tratada como entrada não confiável.

Falhas de:

- parsing;
- schema;
- tipo;
- domínio;

deverão resultar em rejeição segura ou fallback.

---

# 47. Auditoria

Ações com efeito no sistema deverão registrar:

- solicitante;
- tenant;
- capacidade de IA;
- ação proposta;
- confirmação quando aplicável;
- resultado.

---

# 48. Logs

Não registrar indiscriminadamente prompts e respostas completas.

Preferir:

- metadados;
- IDs;
- hashes;
- trechos minimizados;
- métricas.

---

# 49. Métricas

Métricas úteis:

- requests;
- latência;
- erros;
- provider;
- modelo;
- tokens;
- custo aproximado;
- fallback;
- rejeições;
- tool calls.

---

# 50. Custos

Toda capacidade relevante deverá possuir visibilidade de custo.

---

# 51. Quotas

Poderão existir quotas por:

- tenant;
- usuário;
- feature;
- período.

---

# 52. Rate Limiting

Rate limiting deverá proteger:

- custos;
- provider;
- disponibilidade;
- abuso.

---

# 53. Resiliência

IA não deverá se tornar ponto único de falha para funções essenciais que possam operar sem ela.

---

# 54. Timeouts

Toda chamada externa deverá possuir timeout.

---

# 55. Retries

Retries deverão ser:

- limitados;
- observáveis;
- compatíveis com idempotência.

---

# 56. Fallback

Fallback poderá trocar:

- modelo;
- provider;
- capacidade;
- comportamento funcional.

Deverá preservar as mesmas políticas de segurança.

---

# 57. Degradação Controlada

Exemplo:

```text
AI unavailable
→ feature assistiva indisponível

Core GereIgreja
→ continua operacional
```

quando arquiteturalmente possível.

---

# 58. Avaliação

Funcionalidade de IA não deverá ser aprovada apenas com exemplos manuais convincentes.

---

# 59. Quality Gates

Cada caso de uso deverá definir critérios objetivos.

---

# 60. Testes Adversariais

Avaliações deverão incluir:

- prompt injection;
- tenant incorreto;
- contexto ausente;
- permissão insuficiente;
- input ambíguo;
- conteúdo malicioso;
- resposta inválida.

---

# 61. Regressão

Mudanças de:

- modelo;
- prompt;
- retrieval;
- tool;

deverão ser avaliadas contra regressões relevantes.

---

# 62. Ciclo de Vida

Toda capacidade deverá possuir:

- owner;
- finalidade;
- estado;
- dependências;
- estratégia de desativação.

---

# 63. Feature Flags

Funcionalidades experimentais deverão poder ser desativadas quando apropriado.

---

# 64. Classificação de Risco

Categorias oficiais:

```text
Baixo
Médio
Alto
```

---

# 65. Baixo Risco

Exemplos:

- reformulação;
- sumarização de conteúdo pouco sensível;
- sugestões sem efeito automático.

---

# 66. Médio Risco

Exemplos:

- análise de dados internos;
- recomendações;
- preparação de alterações sujeitas a confirmação.

---

# 67. Alto Risco

Exemplos:

- financeiro;
- permissões;
- exclusões;
- comunicação em massa;
- decisões sobre pessoas;
- acesso amplo a dados sensíveis.

Quanto maior o risco, maiores deverão ser:

- revisão;
- confirmação;
- auditoria;
- testes;
- controles.

---

# 68. Critérios para Produção

Antes de production, toda capacidade deverá possuir:

- owner;
- escopo;
- autorização;
- tenant;
- tratamento de erros;
- limites;
- observabilidade;
- avaliação proporcional ao risco;
- estratégia de desativação.

Ações executáveis deverão também possuir:

- schema;
- validação;
- confirmação quando exigida;
- auditoria.

---

# 69. Anti-Padrões

Evitar:

```text
view Django
→ SDK do provider diretamente
```

---

```text
AI
→ ORM irrestrito
```

---

```text
model output
=
authorization
```

---

```text
contexto misturando tenants
```

---

```text
comando livre gerado pelo modelo
→ execução
```

---

```text
secret dentro do prompt
```

---

```text
prompt sensível
registrado integralmente
```

---

```text
ação crítica
sem confirmação/auditoria
```

---

# 70. Relação com Documentação Existente

Os arquivos:

- `AI_CONTEXT_SISTEMA_COMPLETO.md`
- `AI_CONTEXT_CHURCH_SELECTOR.md`

permanecem como documentos de contexto para agentes e ferramentas.

O GAI-01 passa a ser a referência normativa de arquitetura e governança da área de IA.

---

# 71. Próximos Documentos

Documentos candidatos:

```text
GAI-02 — Providers, Modelos, Prompts e AI Gateway
GAI-03 — RAG, Contexto e Conhecimento
GAI-04 — Ferramentas, Agentes e Ações Seguras
GAI-05 — Avaliação, Observabilidade, Custos e Operação
```

Essa lista não obriga criação automática.

Cada novo documento deverá eliminar lacuna real e não duplicar outras famílias.

---

# 72. Checklist

## Arquitetura

- [ ] AI Gateway;
- [ ] provider desacoplado;
- [ ] services reutilizados;
- [ ] tenant explícito;
- [ ] autorização anterior ao contexto.

## Dados

- [ ] minimização;
- [ ] classificação;
- [ ] retrieval autorizado;
- [ ] sem mistura de tenants;
- [ ] sem secrets.

## Prompts

- [ ] versionados;
- [ ] revisáveis;
- [ ] testáveis;
- [ ] resistentes a conteúdo não confiável.

## Ações

- [ ] allowlist;
- [ ] schema;
- [ ] validação;
- [ ] autorização;
- [ ] confirmação quando necessária;
- [ ] auditoria.

## Operação

- [ ] timeout;
- [ ] retry;
- [ ] fallback;
- [ ] métricas;
- [ ] logs;
- [ ] custos;
- [ ] limites.

## Qualidade

- [ ] critérios;
- [ ] casos normais;
- [ ] adversarial;
- [ ] cross-tenant;
- [ ] regressão.

---

# 73. Documentos Relacionados

- GEA — GereIgreja Enterprise Architecture
- GSF — GereIgreja Security Framework
- GOC — GereIgreja Operations Center
- GQF — GereIgreja Quality Framework
- GDF — GereIgreja Documentation Framework
- GAPI — GereIgreja API Engineering
- GINF — GereIgreja Infrastructure Engineering
- GereIgreja Backend Engineering
- GereIgreja Frontend Engineering
- `AI_CONTEXT_SISTEMA_COMPLETO.md`
- `AI_CONTEXT_CHURCH_SELECTOR.md`

---

# 74. Princípios Finais

No GereIgreja:

```text
IA
não substitui
Segurança
Autorização
Domínio
Auditoria
Responsabilidade
```

O princípio central é:

```text
AI proposes.
Application validates.
Authorization limits.
Humans confirm when necessary.
Domain rules decide.
```

A Inteligência Artificial deverá ser incorporada à arquitetura existente como uma capacidade controlada e substituível.

Ela não deverá criar um sistema paralelo menos seguro que o restante da plataforma.

---

# 75. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`01-Arquitetura-e-Governanca-de-Inteligencia-Artificial.md`

**Documento**

`GAI-01`

**Código**

`GAI-AI-ARCHITECTURE-GOVERNANCE`

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

**Próximo documento candidato**

`02-Providers-Modelos-Prompts-e-AI-Gateway.md`
