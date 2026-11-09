Pasta:

docs/ai/

Arquivo:

04-Ferramentas-Agentes-e-Acoes-Seguras.md

Documento:

GAI-04

Código:

GAI-TOOLS-AGENTS-SAFE-ACTIONS

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

# GAI-04 — Ferramentas, Agentes e Ações Seguras

> "Um agente de IA nunca deve possuir mais autoridade do que o usuário, o serviço ou o processo que o autorizou."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Conceito de Tool
6. Conceito de Agente
7. Autonomia Controlada
8. Arquitetura de Referência
9. Tool Registry
10. Tool Contracts
11. Schemas
12. Entradas
13. Saídas
14. Tool Adapters
15. Services
16. Selectors
17. ORM e Banco de Dados
18. Sistema de Arquivos
19. Shell e Comandos
20. Rede e URLs
21. Integrações Externas
22. Autenticação
23. Autorização
24. Tenant
25. Menor Privilégio
26. Escopo de Execução
27. Allowlist
28. Denylist
29. Classificação de Ações
30. Ações de Leitura
31. Ações de Preparação
32. Ações Mutáveis
33. Ações Sensíveis
34. Ações Destrutivas
35. Human-in-the-Loop
36. Confirmação
37. Preview
38. Approval Token
39. Revalidação
40. Idempotência
41. Retries
42. Duplicidade
43. Transações
44. Concorrência
45. Locks
46. Compensação
47. Rollback
48. Limites
49. Rate Limiting
50. Quotas
51. Timeouts
52. Número Máximo de Passos
53. Loops
54. Budget
55. Contexto
56. Memória
57. Estado do Agente
58. Persistência de Estado
59. Dados Sensíveis
60. Prompt Injection
61. Tool Injection
62. Conteúdo Externo
63. Confused Deputy
64. Exfiltração
65. Segurança de Argumentos
66. Validação
67. Structured Output
68. Erros
69. Falha Parcial
70. Observabilidade
71. Logs
72. Métricas
73. Tracing
74. Auditoria
75. Evidências
76. Explicabilidade Operacional
77. Notificações
78. Jobs Assíncronos
79. Long-Running Tasks
80. Cancelamento
81. Agentes Multi-Step
82. Planejamento
83. Replanejamento
84. Subagentes
85. Delegação
86. Permissões de Subagentes
87. Agentes Autônomos
88. Agentes em Produção
89. Testes
90. Testes de Autorização
91. Testes Cross-Tenant
92. Testes Adversariais
93. Testes de Falha
94. Avaliação
95. Feature Flags
96. Kill Switch
97. Governança
98. Ownership
99. Lifecycle
100. Anti-Padrões
101. Arquitetura Consolidada
102. Checklist
103. Documentos Relacionados
104. Princípios Finais
105. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para ferramentas, agentes e ações executáveis por recursos de Inteligência Artificial no GereIgreja.

Seu objetivo é permitir automação assistida sem conceder ao modelo acesso irrestrito à plataforma.

---

# 2. Escopo

Aplica-se a:

- tool calling;
- function calling;
- agentes;
- workflows orientados por IA;
- ações preparadas por IA;
- automações multi-step;
- operações internas;
- integrações externas acionadas por IA;
- execução assíncrona originada por IA.

---

# 3. Relação com a Família GAI

```text
GAI-01
Arquitetura/Governança
       │
       ▼
GAI-02
Models / Gateway
       │
       ├───────────┐
       ▼           ▼
GAI-03          GAI-04
Knowledge       Actions
```

O GAI-03 governa o que a IA pode conhecer.

O GAI-04 governa o que a IA pode fazer.

---

# 4. Princípios Fundamentais

Aplicar:

- least privilege;
- explicit authorization;
- tenant isolation;
- allowlist;
- structured contracts;
- validation;
- human confirmation proporcional ao risco;
- bounded autonomy;
- idempotency;
- auditability;
- fail-safe defaults.

---

# 5. Conceito de Tool

Tool é uma capacidade estruturada que o sistema disponibiliza ao modelo.

Exemplo:

```text
get_member_summary
create_draft_event
prepare_financial_report
```

Tool não é acesso genérico à aplicação.

---

# 6. Conceito de Agente

Agente é um componente capaz de combinar modelo, contexto e ferramentas para alcançar um objetivo dentro de limites definidos.

---

# 7. Autonomia Controlada

Autonomia deverá possuir fronteiras.

```text
Goal
  ↓
Allowed Tools
  ↓
Policies
  ↓
Limits
  ↓
Execution
```

Agente não significa acesso irrestrito.

---

# 8. Arquitetura de Referência

```text
User
 │
 ▼
Authentication
 │
 ▼
Tenant
 │
 ▼
Authorization
 │
 ▼
AI Orchestrator
 │
 ├── Context
 ├── Policies
 ├── Limits
 │
 ▼
Model
 │
 ▼
Tool Proposal
 │
 ▼
Tool Registry
 │
 ▼
Schema Validation
 │
 ▼
Authorization Recheck
 │
 ▼
Confirmation if Required
 │
 ▼
Application Service
 │
 ▼
Domain / Persistence
 │
 ▼
Audit
```

---

# 9. Tool Registry

Ferramentas disponíveis deverão ser registradas explicitamente.

O registry poderá conter:

- tool ID;
- descrição;
- input schema;
- output schema;
- risk level;
- owner;
- required permission;
- confirmation policy;
- timeout.

---

# 10. Tool Contracts

Contratos deverão ser definidos pela aplicação.

O provider apenas recebe uma representação desses contratos.

---

# 11. Schemas

Toda tool deverá possuir schema de entrada.

Preferencialmente também deverá possuir schema de saída.

---

# 12. Entradas

Argumentos produzidos pelo modelo são dados não confiáveis.

---

# 13. Saídas

Saídas deverão ser limitadas ao necessário.

Uma tool não deverá retornar objetos inteiros quando apenas poucos campos forem necessários.

---

# 14. Tool Adapters

Adapters poderão traduzir contratos internos para formatos específicos do provider.

---

# 15. Services

Ações mutáveis deverão reutilizar Application/Domain Services oficiais.

```text
AI Tool
→ Service
→ Business Rules
```

---

# 16. Selectors

Consultas deverão reutilizar selectors autorizados quando existentes.

---

# 17. ORM e Banco de Dados

É proibido conceder ao modelo acesso genérico ao ORM ou SQL.

```text
LLM
→ arbitrary SQL
```

não deverá ser arquitetura padrão.

---

# 18. Sistema de Arquivos

Acesso genérico ao filesystem deverá ser proibido por padrão.

Quando necessário, limitar:

- diretórios;
- tipos;
- tamanho;
- operação.

---

# 19. Shell e Comandos

Modelos não deverão executar shell arbitrário em production.

Exceções exigem ambiente isolado e arquitetura específica formalmente aprovada.

---

# 20. Rede e URLs

Tools que acessam URLs deverão proteger contra:

- SSRF;
- hosts internos;
- esquemas proibidos;
- redirects perigosos;
- downloads excessivos.

---

# 21. Integrações Externas

Integrações deverão reutilizar credenciais e services oficiais.

O modelo não deverá receber secrets.

---

# 22. Autenticação

A identidade do solicitante deverá ser conhecida antes da execução.

---

# 23. Autorização

Autorização deverá ser aplicada por código determinístico.

O modelo não decide permissões.

---

# 24. Tenant

Toda tool que manipula dados tenant-scoped deverá receber o tenant do contexto confiável da aplicação.

Nunca aceitar `tenant_id` arbitrário produzido pelo modelo como fonte autoritativa.

---

# 25. Menor Privilégio

A ferramenta deverá possuir somente a capacidade necessária.

Preferir:

```text
create_event_draft
```

a:

```text
manage_everything
```

---

# 26. Escopo de Execução

Toda execução deverá possuir escopo explícito.

---

# 27. Allowlist

Somente tools aprovadas poderão ser expostas ao agente.

---

# 28. Denylist

Denylist poderá complementar controles, mas não substituir allowlist.

---

# 29. Classificação de Ações

Categorias recomendadas:

```text
READ
PREPARE
WRITE
SENSITIVE
DESTRUCTIVE
```

---

# 30. Ações de Leitura

Ações somente leitura ainda exigem autorização.

---

# 31. Ações de Preparação

Podem gerar:

- draft;
- preview;
- proposta;
- relatório.

São preferíveis quando a decisão final pertence ao usuário.

---

# 32. Ações Mutáveis

Alterações persistentes deverão utilizar services e auditoria.

---

# 33. Ações Sensíveis

Exemplos:

- financeiro;
- dados pessoais;
- permissões;
- comunicação ampla;
- exportações.

Exigem controles reforçados.

---

# 34. Ações Destrutivas

Exemplos:

- exclusão;
- revogação;
- cancelamento irreversível.

Deverão exigir confirmação humana explícita salvo arquitetura excepcional formalmente aprovada.

---

# 35. Human-in-the-Loop

A confirmação deverá ocorrer fora do modelo.

---

# 36. Confirmação

O usuário deverá compreender o que será executado.

Evitar:

```text
"Confirmar ação?"
```

Preferir informação concreta sobre:

- ação;
- alvo;
- impacto;
- quantidade;
- consequências.

---

# 37. Preview

Quando possível, gerar preview antes da execução.

---

# 38. Approval Token

Fluxos de confirmação poderão utilizar token/identificador associado à proposta aprovada.

O token deverá ser:

- temporário;
- vinculado ao usuário;
- vinculado ao tenant;
- vinculado à ação;
- não reutilizável quando necessário.

---

# 39. Revalidação

Após confirmação, revalidar autorização e estado relevante.

A aprovação anterior não garante que o contexto ainda seja válido.

---

# 40. Idempotência

Ações sujeitas a retry deverão possuir proteção contra duplicidade.

---

# 41. Retries

Retry automático de ação mutável exige cuidado.

---

# 42. Duplicidade

Evitar:

```text
retry
→ duas doações
→ dois eventos
→ duas mensagens
```

---

# 43. Transações

Usar transações quando apropriado às regras do domínio.

---

# 44. Concorrência

Considerar alterações concorrentes entre usuário, agente e outros processos.

---

# 45. Locks

Locks poderão ser utilizados quando justificáveis.

---

# 46. Compensação

Workflows distribuídos poderão exigir ações compensatórias.

---

# 47. Rollback

Nem toda ação possui rollback.

Essa limitação deverá influenciar classificação de risco e confirmação.

---

# 48. Limites

Agentes deverão possuir limites explícitos.

---

# 49. Rate Limiting

Aplicar limites por:

- usuário;
- tenant;
- agent;
- tool;
- integração.

---

# 50. Quotas

Quotas poderão limitar volume operacional.

---

# 51. Timeouts

Cada tool deverá possuir timeout compatível.

---

# 52. Número Máximo de Passos

Agentes multi-step deverão possuir máximo de iterações.

---

# 53. Loops

Detectar ou interromper loops improdutivos.

---

# 54. Budget

Poderão existir budgets de:

- tokens;
- custo;
- tempo;
- tools;
- passos.

---

# 55. Contexto

O agente deverá receber apenas contexto necessário.

---

# 56. Memória

Memória de agente não deverá ser confundida com fonte autoritativa.

---

# 57. Estado do Agente

Estado deverá ser explícito quando necessário.

---

# 58. Persistência de Estado

Persistir somente o necessário.

Não armazenar indefinidamente raciocínio, prompts ou dados sensíveis sem finalidade.

---

# 59. Dados Sensíveis

Tools deverão minimizar exposição de dados.

---

# 60. Prompt Injection

Conteúdo malicioso poderá tentar induzir o agente a chamar ferramentas.

A autorização não deverá depender do prompt.

---

# 61. Tool Injection

Descrições ou resultados de tools externas deverão ser tratados como conteúdo não confiável quando apropriado.

---

# 62. Conteúdo Externo

Uma página externa não poderá conceder novas permissões ao agente.

---

# 63. Confused Deputy

Evitar que o agente use sua própria autoridade para realizar algo que o usuário não poderia fazer.

Regra:

```text
effective_permission
=
intersection(
 user_permission,
 agent_permission,
 tool_permission
)
```

---

# 64. Exfiltração

Tools não deverão permitir enviar dados internos arbitrariamente para destinos externos.

---

# 65. Segurança de Argumentos

Validar:

- IDs;
- enums;
- datas;
- limites;
- URLs;
- destinatários;
- tamanhos;
- formatos.

---

# 66. Validação

Validação deverá ocorrer antes da execução.

---

# 67. Structured Output

Tool calls deverão ser estruturadas.

Não interpretar texto livre como comando privilegiado.

---

# 68. Erros

Erros deverão ser normalizados antes de retornar ao modelo.

Evitar expor:

- stack traces;
- secrets;
- SQL;
- caminhos internos;
- detalhes desnecessários.

---

# 69. Falha Parcial

Workflows multi-step deverão conhecer efeitos já executados.

---

# 70. Observabilidade

Toda execução de tool relevante deverá ser observável.

---

# 71. Logs

Registrar:

- correlation ID;
- user;
- tenant;
- agent;
- tool;
- status;
- duração;
- erro normalizado.

Minimizar argumentos sensíveis.

---

# 72. Métricas

Exemplos:

```text
ai_tool_calls_total
ai_tool_failures_total
ai_tool_duration
ai_agent_steps
ai_agent_aborts
ai_confirmations_required
ai_confirmations_rejected
```

---

# 73. Tracing

Fluxos multi-step poderão utilizar tracing para reconstrução operacional.

---

# 74. Auditoria

Ações mutáveis deverão registrar trilha de auditoria conforme domínio.

---

# 75. Evidências

Para ações sensíveis, preservar evidências suficientes de:

- solicitação;
- proposta;
- aprovação;
- execução;
- resultado.

---

# 76. Explicabilidade Operacional

Deverá ser possível explicar quais ferramentas foram executadas.

Não é necessário expor raciocínio interno do modelo.

---

# 77. Notificações

Ações que enviam mensagens ou notificações deverão possuir controles de destinatário, volume e confirmação quando aplicável.

---

# 78. Jobs Assíncronos

Tools poderão enfileirar jobs.

O job deverá carregar identidade, tenant e autorização necessária de forma segura.

---

# 79. Long-Running Tasks

Tarefas longas deverão possuir:

- status;
- timeout;
- cancelamento quando possível;
- observabilidade.

---

# 80. Cancelamento

Cancelar tarefas não deverá deixar estado inconsistente.

---

# 81. Agentes Multi-Step

Cada passo deverá permanecer dentro das mesmas fronteiras de segurança.

---

# 82. Planejamento

Planos produzidos pelo modelo são propostas, não autorização.

---

# 83. Replanejamento

Falhas não deverão permitir que o agente escape das políticas para tentar alternativas proibidas.

---

# 84. Subagentes

Subagentes poderão ser utilizados somente quando a complexidade justificar.

---

# 85. Delegação

Delegação deverá ser explícita.

---

# 86. Permissões de Subagentes

Subagente não deverá receber automaticamente todas as tools do agente pai.

---

# 87. Agentes Autônomos

Autonomia contínua em production exige revisão de risco específica.

---

# 88. Agentes em Produção

Antes de production, definir:

- owner;
- objetivo;
- tools;
- limites;
- budget;
- timeout;
- confirmação;
- kill switch;
- observabilidade.

---

# 89. Testes

Tools e agentes deverão possuir testes determinísticos nas fronteiras controláveis.

---

# 90. Testes de Autorização

Testar explicitamente acesso permitido e negado.

---

# 91. Testes Cross-Tenant

Obrigatório para tools tenant-scoped.

Resultado esperado:

```text
zero cross-tenant execution
```

---

# 92. Testes Adversariais

Incluir:

- prompt injection;
- tool abuse;
- argumentos inválidos;
- IDs de outro tenant;
- tentativa de bypass de confirmação;
- loops;
- exfiltração.

---

# 93. Testes de Falha

Testar:

- timeout;
- provider failure;
- tool failure;
- partial execution;
- retry;
- cancellation.

---

# 94. Avaliação

Avaliar não apenas qualidade da resposta, mas segurança da trajetória de execução.

---

# 95. Feature Flags

Agentes e tools novas poderão ser liberados gradualmente.

---

# 96. Kill Switch

Capacidades de maior risco deverão poder ser desativadas rapidamente.

---

# 97. Governança

Nova tool deverá possuir revisão proporcional ao risco.

---

# 98. Ownership

Toda tool e agente deverá possuir owner.

---

# 99. Lifecycle

Estados sugeridos:

```text
EXPERIMENTAL
APPROVED
DEPRECATED
DISABLED
```

---

# 100. Anti-Padrões

Evitar:

```text
LLM
→ ORM
```

---

```text
LLM
→ shell production
```

---

```text
model generated tenant_id
→ trusted
```

---

```text
"o prompt diz para não fazer"
=
controle de autorização
```

---

```text
tool genérica
manage_everything()
```

---

```text
ação destrutiva
sem confirmação
```

---

```text
agente
sem limite de passos
```

---

```text
retry
sem idempotência
```

---

```text
subagente
herda todas as permissões
```

---

```text
erro interno
com secret
retornado ao modelo
```

---

# 101. Arquitetura Consolidada

```text
                         USER
                           │
                           ▼
                  AUTH / TENANT / RBAC
                           │
                           ▼
                    AI ORCHESTRATOR
                           │
               ┌───────────┼───────────┐
               ▼           ▼           ▼
            Context      Policies     Budget
               └───────────┼───────────┘
                           ▼
                         MODEL
                           │
                           ▼
                    TOOL PROPOSAL
                           │
                           ▼
                     TOOL REGISTRY
                           │
                           ▼
                   SCHEMA VALIDATION
                           │
                           ▼
                 AUTHORIZATION RECHECK
                           │
                           ▼
                RISK / CONFIRMATION
                           │
                           ▼
                  APPLICATION SERVICE
                           │
                           ▼
                    DOMAIN / DATA
                           │
                           ▼
                 AUDIT / OBSERVABILITY
```

---

# 102. Checklist

## Tool

- [ ] ID único;
- [ ] owner;
- [ ] input schema;
- [ ] output controlado;
- [ ] risk level;
- [ ] permission;
- [ ] timeout;
- [ ] documentação.

## Segurança

- [ ] allowlist;
- [ ] tenant confiável;
- [ ] autorização determinística;
- [ ] menor privilégio;
- [ ] argumentos validados;
- [ ] sem secrets;
- [ ] sem acesso genérico a ORM/shell.

## Ações

- [ ] classificação;
- [ ] idempotência;
- [ ] transação quando necessária;
- [ ] preview quando apropriado;
- [ ] confirmação;
- [ ] revalidação;
- [ ] auditoria.

## Agente

- [ ] objetivo limitado;
- [ ] tools limitadas;
- [ ] máximo de passos;
- [ ] timeout;
- [ ] budget;
- [ ] cancelamento;
- [ ] kill switch;
- [ ] feature flag quando apropriado.

## Testes

- [ ] autorização;
- [ ] cross-tenant;
- [ ] prompt injection;
- [ ] tool abuse;
- [ ] falha parcial;
- [ ] retry;
- [ ] duplicidade;
- [ ] loops.

## Operação

- [ ] logs;
- [ ] métricas;
- [ ] tracing quando necessário;
- [ ] alertas;
- [ ] owner;
- [ ] lifecycle.

---

# 103. Documentos Relacionados

- GAI-01 — Arquitetura e Governança de Inteligência Artificial
- GAI-02 — Providers, Modelos, Prompts e AI Gateway
- GAI-03 — RAG, Contexto e Conhecimento
- GSF — GereIgreja Security Framework
- GAPI — GereIgreja API Engineering
- GINF — GereIgreja Infrastructure Engineering
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GDF — GereIgreja Documentation Framework
- GereIgreja Backend Engineering

---

# 104. Princípios Finais

Ferramentas e agentes ampliam a capacidade da IA e, consequentemente, ampliam o risco quando mal delimitados.

```text
Model
+
Tool
=
Potential Action
```

Por isso:

```text
Potential Action
+
Authorization
+
Validation
+
Limits
+
Confirmation
+
Audit
=
Controlled Action
```

O princípio central é:

```text
A IA pode propor.

A aplicação autoriza.

O domínio valida.

O usuário confirma
quando necessário.

Somente então
a ação acontece.
```

Agentes do GereIgreja deverão operar dentro da arquitetura existente, nunca acima dela.

---

# 105. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`04-Ferramentas-Agentes-e-Acoes-Seguras.md`

**Documento**

`GAI-04`

**Código**

`GAI-TOOLS-AGENTS-SAFE-ACTIONS`

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

`GAI-03 — RAG, Contexto e Conhecimento`

**Próximo documento candidato**

`05-Avaliacao-Observabilidade-Custos-e-Operacao-de-IA.md`
