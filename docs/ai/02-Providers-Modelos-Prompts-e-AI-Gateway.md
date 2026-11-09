Pasta:

docs/ai/

Arquivo:

02-Providers-Modelos-Prompts-e-AI-Gateway.md

Documento:

GAI-02

Código:

GAI-PROVIDERS-MODELS-PROMPTS-GATEWAY

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

# GAI-02 — Providers, Modelos, Prompts e AI Gateway

> "A aplicação deve depender de capacidades de IA, não de um fornecedor ou modelo específico."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com GAI-01
4. Princípios Fundamentais
5. AI Gateway
6. Responsabilidades do Gateway
7. Fronteiras Arquiteturais
8. Provider Adapters
9. Contratos Internos
10. Capacidades
11. Geração de Texto
12. Saída Estruturada
13. Classificação
14. Extração
15. Sumarização
16. Embeddings
17. Tool Calling
18. Catálogo de Providers
19. Catálogo de Modelos
20. Identificação de Modelos
21. Seleção de Modelo
22. Model Routing
23. Política de Fallback
24. Compatibilidade
25. Configuração
26. Ambientes
27. Secrets
28. Credenciais
29. Timeouts
30. Retries
31. Circuit Breaker
32. Rate Limits
33. Quotas
34. Concorrência
35. Limites de Contexto
36. Limites de Output
37. Tokens
38. Custos
39. Budgets
40. Prompts
41. Tipos de Prompt
42. System Prompt
43. Developer Instructions
44. User Input
45. Contexto Recuperado
46. Templates
47. Variáveis
48. Versionamento
49. Prompt Registry
50. Revisão de Prompts
51. Testes de Prompts
52. Segurança de Prompts
53. Prompt Injection
54. Delimitação de Conteúdo
55. Dados Sensíveis
56. Saída Estruturada
57. Schemas
58. Parsing
59. Validação
60. Erros
61. Respostas do Provider
62. Normalização
63. Streaming
64. Cancelamento
65. Idempotência
66. Observabilidade
67. Logging
68. Métricas
69. Tracing
70. Auditoria
71. Privacidade
72. Retenção
73. Uso de Dados por Providers
74. Resiliência
75. Degradação
76. Testabilidade
77. Mocks e Fakes
78. Avaliação
79. Mudança de Modelo
80. Depreciação
81. Provider Lock-in
82. Novos Providers
83. Governança
84. Anti-Padrões
85. Arquitetura de Referência
86. Checklist
87. Documentos Relacionados
88. Princípios Finais
89. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para integração entre o GereIgreja e providers/modelos de Inteligência Artificial.

Define:

- AI Gateway;
- adapters;
- contratos internos;
- seleção de modelos;
- configuração;
- prompts;
- versionamento;
- resiliência;
- custos;
- observabilidade.

---

# 2. Escopo

Aplica-se a qualquer código que utilize:

- LLMs;
- modelos multimodais;
- embeddings;
- classificação;
- extração estruturada;
- tool calling;
- serviços externos ou internos de IA.

---

# 3. Relação com GAI-01

O GAI-01 define a arquitetura e governança geral.

O GAI-02 detalha a fronteira:

```text
GereIgreja
    │
    ▼
AI Gateway
    │
    ▼
Provider / Model
```

---

# 4. Princípios Fundamentais

Aplicar:

- provider agnostic;
- capability-oriented design;
- configuração explícita;
- secrets fora do código;
- contratos internos estáveis;
- fallback controlado;
- observabilidade;
- custos mensuráveis;
- prompts versionados;
- validação de toda saída.

---

# 5. AI Gateway

O AI Gateway é a fronteira oficial entre a aplicação e providers de IA.

Nenhuma camada de domínio deverá depender diretamente do SDK de um provider.

---

# 6. Responsabilidades do Gateway

O Gateway deverá centralizar, quando aplicável:

- seleção de provider;
- seleção de modelo;
- autenticação com provider;
- timeouts;
- retries;
- fallback;
- normalização;
- telemetria;
- limites;
- custos;
- tratamento de erros.

---

# 7. Fronteiras Arquiteturais

Fluxo recomendado:

```text
Feature
   │
   ▼
AI Service
   │
   ▼
AI Gateway
   │
   ├── Provider Adapter A
   ├── Provider Adapter B
   └── Provider Adapter N
```

SDKs externos deverão permanecer nos adapters.

---

# 8. Provider Adapters

Cada provider deverá possuir adapter responsável por converter o contrato interno para o contrato externo.

---

# 9. Contratos Internos

Contratos deverão utilizar estruturas controladas pelo GereIgreja.

Exemplo conceitual:

```text
AIRequest
AIResponse
AIUsage
AIError
AIToolCall
```

Não propagar objetos proprietários de SDK para o domínio.

---

# 10. Capacidades

A aplicação deverá solicitar capacidades.

Exemplo:

```text
generate_text()
generate_structured()
classify()
extract()
embed()
```

---

# 11. Geração de Texto

Utilizada quando texto livre for realmente necessário.

Saída textual nunca deverá ser assumida como estrutura confiável.

---

# 12. Saída Estruturada

Preferir saída estruturada quando o resultado alimentar lógica de aplicação.

---

# 13. Classificação

Classificações deverão possuir conjunto de labels conhecido quando possível.

---

# 14. Extração

Extrações deverão validar campos contra schema.

---

# 15. Sumarização

Sumarização deverá preservar o escopo de acesso do conteúdo original.

---

# 16. Embeddings

Embeddings deverão ser tratados como representação derivada de dados.

Sua persistência deverá respeitar as mesmas fronteiras de tenant e privacidade aplicáveis à origem.

---

# 17. Tool Calling

Tool calling deverá seguir GAI-04.

O Gateway somente transporta chamadas; autorização e regras de negócio não pertencem ao provider.

---

# 18. Catálogo de Providers

Providers aprovados deverão possuir registro contendo:

- nome;
- finalidade;
- owner;
- ambientes autorizados;
- requisitos de privacidade;
- credenciais;
- status.

---

# 19. Catálogo de Modelos

Modelos utilizados deverão ser identificáveis.

Registrar quando relevante:

- provider;
- model ID;
- capacidades;
- contexto;
- custo;
- status;
- casos de uso.

---

# 20. Identificação de Modelos

Não utilizar nomes informais em configuração crítica.

Preferir identificadores exatos suportados pelo provider.

---

# 21. Seleção de Modelo

A seleção deverá considerar:

```text
qualidade
latência
custo
context window
structured output
tool support
privacidade
disponibilidade
```

---

# 22. Model Routing

Uma capacidade poderá utilizar routing.

Exemplo:

```text
simple_task
→ modelo econômico

complex_task
→ modelo avançado
```

Routing deverá ser testável e observável.

---

# 23. Política de Fallback

Fallback deverá ser explícito.

```text
Primary
   │ failure
   ▼
Fallback
```

Não encadear providers indefinidamente.

---

# 24. Compatibilidade

Fallback deverá suportar os requisitos mínimos da capacidade.

Não utilizar fallback incapaz de preservar:

- schema;
- segurança;
- privacidade;
- tool contract.

---

# 25. Configuração

Configuração deverá permanecer fora do código quando variável por ambiente.

---

# 26. Ambientes

Development, staging e production poderão utilizar modelos ou limites diferentes.

A diferença deverá ser explícita.

---

# 27. Secrets

Secrets deverão seguir GSF e GINF.

Nunca:

```text
API_KEY = "..."
```

em repositório.

---

# 28. Credenciais

Credenciais deverão possuir:

- owner;
- escopo;
- rotação;
- revogação;
- acesso mínimo.

---

# 29. Timeouts

Toda chamada externa deverá possuir timeout.

---

# 30. Retries

Retries deverão ocorrer apenas para falhas adequadas.

Evitar retry indiscriminado em:

- erro de validação;
- request inválido;
- autorização;
- conteúdo rejeitado.

---

# 31. Circuit Breaker

Poderá ser utilizado quando falhas persistentes de provider causarem cascata.

---

# 32. Rate Limits

Limites do provider deverão ser conhecidos.

---

# 33. Quotas

O GereIgreja poderá aplicar quotas internas inferiores aos limites externos.

---

# 34. Concorrência

Controlar concorrência para evitar:

- saturação;
- custos inesperados;
- rate limit;
- degradação.

---

# 35. Limites de Contexto

Antes do envio, validar tamanho de contexto.

Não depender exclusivamente do erro do provider.

---

# 36. Limites de Output

Definir output máximo proporcional à tarefa.

---

# 37. Tokens

Uso de tokens deverá ser medido quando o provider disponibilizar.

---

# 38. Custos

Registrar custo estimado ou dados suficientes para calculá-lo quando possível.

---

# 39. Budgets

Capacidades de alto volume poderão possuir budgets.

---

# 40. Prompts

Prompts são código comportamental.

Devem receber disciplina semelhante a outros artefatos de engenharia.

---

# 41. Tipos de Prompt

Distinguir:

```text
system instructions
application/developer instructions
user input
retrieved context
tool results
```

---

# 42. System Prompt

Deverá conter regras estáveis de comportamento da capacidade.

Não deverá conter secrets.

---

# 43. Developer Instructions

Instruções específicas da aplicação deverão permanecer controladas pelo GereIgreja.

---

# 44. User Input

Input do usuário é conteúdo não confiável.

---

# 45. Contexto Recuperado

Conteúdo recuperado também é não confiável como instrução.

---

# 46. Templates

Templates deverão possuir variáveis explícitas.

Evitar concatenação informal de grandes strings em código de negócio.

---

# 47. Variáveis

Variáveis deverão ser delimitadas e validadas conforme natureza.

---

# 48. Versionamento

Prompts relevantes deverão possuir versão.

Exemplo:

```text
member_summary:v1
member_summary:v2
```

---

# 49. Prompt Registry

A família GAI poderá adotar registry para prompts quando volume justificar.

O registry poderá registrar:

- ID;
- versão;
- owner;
- finalidade;
- modelo/capacidade;
- status.

---

# 50. Revisão de Prompts

Mudanças relevantes deverão passar por code review.

---

# 51. Testes de Prompts

Testar:

- caso esperado;
- contexto incompleto;
- input ambíguo;
- conteúdo adversarial;
- saída inválida.

---

# 52. Segurança de Prompts

Prompts não são mecanismo de segurança suficiente.

```text
"não revele dados"
```

não substitui autorização.

---

# 53. Prompt Injection

A aplicação deverá assumir que usuários e documentos podem tentar modificar o comportamento do modelo.

Controles reais deverão existir fora do prompt.

---

# 54. Delimitação de Conteúdo

Separar claramente instruções e dados quando o provider permitir.

---

# 55. Dados Sensíveis

Antes de construir prompt, aplicar minimização.

---

# 56. Saída Estruturada

Para operações programáticas, preferir schema.

---

# 57. Schemas

Schemas deverão ser definidos pela aplicação.

---

# 58. Parsing

Parsing deverá falhar de forma segura.

---

# 59. Validação

Após parsing, aplicar:

- tipos;
- limites;
- enums;
- regras de domínio;
- autorização quando aplicável.

---

# 60. Erros

O Gateway deverá normalizar erros externos.

Categorias internas sugeridas:

```text
AI_TIMEOUT
AI_RATE_LIMIT
AI_PROVIDER_UNAVAILABLE
AI_INVALID_RESPONSE
AI_CONTEXT_LIMIT
AI_POLICY_REJECTION
AI_CONFIGURATION_ERROR
```

---

# 61. Respostas do Provider

Não expor resposta bruta de erro do provider ao usuário sem necessidade.

---

# 62. Normalização

Providers diferentes deverão produzir contratos internos equivalentes quando executarem a mesma capacidade.

---

# 63. Streaming

Streaming poderá ser usado para UX.

A aplicação deverá considerar:

- cancelamento;
- erro parcial;
- auditoria;
- conteúdo incompleto.

---

# 64. Cancelamento

Quando suportado, cancelar operações que perderam utilidade.

---

# 65. Idempotência

Retries em ações associadas a tools deverão respeitar idempotência.

O modelo não controla idempotência do domínio.

---

# 66. Observabilidade

Cada chamada deverá gerar telemetria proporcional ao risco.

---

# 67. Logging

Registrar preferencialmente:

- request ID;
- tenant ID técnico;
- feature;
- provider;
- modelo;
- duração;
- status;
- erro normalizado.

Evitar payload sensível.

---

# 68. Métricas

Exemplos:

```text
ai_requests_total
ai_request_duration
ai_errors_total
ai_tokens_input
ai_tokens_output
ai_fallback_total
ai_estimated_cost
```

Os nomes reais deverão seguir o padrão de observabilidade adotado pela plataforma.

---

# 69. Tracing

Chamadas poderão integrar tracing distribuído.

---

# 70. Auditoria

Auditoria de ações de negócio deverá ocorrer fora do Gateway, na camada responsável pelo efeito.

---

# 71. Privacidade

Provider/modelo selecionado deverá ser compatível com a classificação dos dados enviados.

---

# 72. Retenção

Conhecer política de retenção do provider para os serviços utilizados.

---

# 73. Uso de Dados por Providers

A utilização dos dados pelo provider deverá ser avaliada antes de liberar dados não públicos.

---

# 74. Resiliência

Falha externa deverá permanecer confinada.

---

# 75. Degradação

Quando possível:

```text
AI unavailable
→ AI feature degraded

Core platform
→ available
```

---

# 76. Testabilidade

Código consumidor deverá ser testável sem chamar provider real.

---

# 77. Mocks e Fakes

Preferir fake do contrato interno.

Não espalhar mocks específicos de SDK pela base.

---

# 78. Avaliação

Avaliação de qualidade pertence ao GAI-05, mas mudanças de provider/modelo deverão ser submetidas aos conjuntos relevantes.

---

# 79. Mudança de Modelo

Troca de modelo não deverá ser considerada alteração puramente operacional quando puder modificar comportamento.

Deverá possuir avaliação proporcional ao risco.

---

# 80. Depreciação

Modelos deprecated deverão possuir plano de migração.

---

# 81. Provider Lock-in

Recursos proprietários poderão ser utilizados quando justificados.

O lock-in deverá ser consciente.

---

# 82. Novos Providers

Antes de adicionar provider:

- justificar necessidade;
- avaliar segurança;
- avaliar privacidade;
- avaliar custo;
- implementar adapter;
- testar contratos;
- documentar fallback;
- configurar observabilidade.

---

# 83. Governança

Mudanças relevantes em providers, modelos e políticas deverão possuir owner e revisão.

---

# 84. Anti-Padrões

Evitar:

```text
View
→ Provider SDK
```

---

```text
Domain Service
→ objeto proprietário do SDK
```

---

```text
model="qualquer-modelo"
hardcoded em dezenas de arquivos
```

---

```text
prompt crítico
sem versão
```

---

```text
retry infinito
```

---

```text
fallback
sem observabilidade
```

---

```text
output JSON
usado sem validação
```

---

```text
provider error
exposto diretamente
ao usuário
```

---

```text
segurança
dependente apenas
do system prompt
```

---

# 85. Arquitetura de Referência

```text
                     APPLICATION
                         │
                         ▼
                    AI SERVICE
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     Prompt Registry   Policies      Context
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                     AI GATEWAY
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
   Adapter A         Adapter B         Adapter N
       │                 │                 │
       ▼                 ▼                 ▼
   Provider A        Provider B        Provider N
                         │
                         ▼
                    TELEMETRY
```

---

# 86. Checklist

## Gateway

- [ ] interface interna;
- [ ] adapters;
- [ ] erros normalizados;
- [ ] timeout;
- [ ] retry;
- [ ] fallback;
- [ ] telemetria.

## Providers

- [ ] provider aprovado;
- [ ] owner;
- [ ] credencial segura;
- [ ] política de dados conhecida;
- [ ] limites conhecidos.

## Modelos

- [ ] model ID explícito;
- [ ] capacidade conhecida;
- [ ] custo conhecido;
- [ ] contexto conhecido;
- [ ] lifecycle conhecido.

## Prompts

- [ ] ID;
- [ ] versão;
- [ ] owner;
- [ ] template controlado;
- [ ] sem secrets;
- [ ] testes.

## Output

- [ ] schema quando necessário;
- [ ] parsing seguro;
- [ ] validação;
- [ ] erros tratados.

## Operação

- [ ] métricas;
- [ ] logs minimizados;
- [ ] custos;
- [ ] rate limits;
- [ ] quotas;
- [ ] fallback observado.

---

# 87. Documentos Relacionados

- GAI-01 — Arquitetura e Governança de Inteligência Artificial
- GSF — GereIgreja Security Framework
- GAPI — GereIgreja API Engineering
- GINF — GereIgreja Infrastructure Engineering
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GDF — GereIgreja Documentation Framework
- GereIgreja Backend Engineering

---

# 88. Princípios Finais

A integração com IA deverá preservar a independência arquitetural da plataforma.

```text
Feature
→ Capability
→ AI Gateway
→ Adapter
→ Provider
```

O princípio central é:

```text
Providers mudam.
Modelos mudam.
Prompts evoluem.

O contrato da plataforma
deve permanecer controlado
pelo GereIgreja.
```

Prompts deverão ser tratados como artefatos de engenharia, providers como dependências externas e modelos como componentes substituíveis sujeitos a avaliação.

---

# 89. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`02-Providers-Modelos-Prompts-e-AI-Gateway.md`

**Documento**

`GAI-02`

**Código**

`GAI-PROVIDERS-MODELS-PROMPTS-GATEWAY`

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

`GAI-01 — Arquitetura e Governança de Inteligência Artificial`

**Próximo documento candidato**

`03-RAG-Contexto-e-Conhecimento.md`
