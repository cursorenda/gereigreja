Pasta:

docs/ai/

Arquivo:

06-Seguranca-Privacidade-e-Guardrails-de-IA.md

Documento:

GAI-06

Código:

GAI-AI-SECURITY-PRIVACY-GUARDRAILS

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

# GAI-06 — Segurança, Privacidade e Guardrails de IA

> "A IA não cria uma exceção às regras de segurança da plataforma. Ela adiciona novas superfícies que precisam ser protegidas."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com GSF e Família GAI
4. Modelo de Responsabilidade
5. Princípios Fundamentais
6. Threat Model de IA
7. Superfícies de Ataque
8. Trust Boundaries
9. Defesa em Profundidade
10. Guardrails
11. Guardrails de Entrada
12. Guardrails de Contexto
13. Guardrails de Retrieval
14. Guardrails de Saída
15. Guardrails de Tools
16. Guardrails de Execução
17. Prompt Injection
18. Indirect Prompt Injection
19. Jailbreaks
20. Exfiltração
21. Cross-Tenant Leakage
22. Data Poisoning
23. Knowledge Poisoning
24. Tool Abuse
25. Confused Deputy
26. Excessive Agency
27. Insecure Output Handling
28. Sensitive Information Disclosure
29. Model Denial of Service
30. Supply Chain
31. Providers
32. Modelos
33. SDKs e Dependências
34. Plugins e Integrações
35. Privacidade
36. Minimização de Dados
37. Classificação de Dados
38. Dados Pessoais
39. Dados Sensíveis
40. Dados Financeiros
41. Dados Ministeriais
42. Secrets
43. Credenciais
44. Pseudonimização
45. Mascaramento
46. Retenção
47. Exclusão
48. Logs e Telemetria
49. Training e Data Usage
50. Providers Externos
51. Residência de Dados
52. Transferência de Dados
53. Consentimento e Finalidade
54. LGPD
55. Autorização
56. Tenant Isolation
57. RAG Security
58. Embeddings
59. Vector Stores
60. Agent Security
61. Tool Security
62. Human-in-the-Loop
63. Structured Output
64. Validação
65. URLs e SSRF
66. Arquivos
67. Conteúdo Multimodal
68. Rate Limiting
69. Quotas
70. Budgets
71. Timeouts
72. Kill Switch
73. Feature Flags
74. Monitoramento
75. Detecção
76. Alertas
77. Auditoria
78. Incidentes
79. Resposta a Incidentes
80. Evidências
81. Testes de Segurança
82. Red Team
83. Testes Cross-Tenant
84. Testes de Prompt Injection
85. Testes de Tools
86. Testes de Privacidade
87. Secure Defaults
88. Production Readiness
89. Revisões
90. Ownership
91. Anti-Padrões
92. Arquitetura Consolidada
93. Checklist
94. Documentos Relacionados
95. Princípios Finais
96. Status do Documento

---

# 1. Objetivo

Este documento estabelece os controles específicos de segurança, privacidade e guardrails aplicáveis às capacidades de Inteligência Artificial do GereIgreja.

O GAI-06 não substitui o GSF.

Ele especializa os controles do GereIgreja para riscos introduzidos por:

- modelos generativos;
- prompts;
- RAG;
- embeddings;
- agentes;
- tools;
- providers externos;
- conteúdo não confiável;
- automação assistida por IA.

---

# 2. Escopo

Aplica-se a toda funcionalidade que utilize IA para:

- consultar;
- analisar;
- resumir;
- gerar;
- classificar;
- recuperar;
- recomendar;
- preparar;
- executar ações.

---

# 3. Relação com GSF e Família GAI

```text
GSF
Security Baseline
   │
   ▼
GAI-01
AI Governance
   │
   ├── GAI-02 Providers / Models / Prompts
   ├── GAI-03 RAG / Knowledge
   ├── GAI-04 Tools / Agents
   ├── GAI-05 Operations
   │
   ▼
GAI-06
AI Security / Privacy / Guardrails
```

Em caso de conflito, os controles corporativos e de segurança mais restritivos deverão prevalecer.

---

# 4. Modelo de Responsabilidade

A segurança deverá permanecer sob controle da aplicação.

```text
Model
≠
Security Authority
```

O modelo poderá sugerir.

A aplicação deverá:

- autenticar;
- autorizar;
- filtrar;
- validar;
- limitar;
- confirmar;
- auditar.

---

# 5. Princípios Fundamentais

Aplicar:

- zero implicit trust;
- least privilege;
- tenant isolation;
- data minimization;
- fail-safe defaults;
- defense in depth;
- explicit allowlists;
- bounded agency;
- secure output handling;
- observability;
- human control proporcional ao risco.

---

# 6. Threat Model de IA

Toda capacidade relevante deverá considerar:

```text
User
External Content
Retrieved Content
Prompt
Model
Provider
Tool
Integration
Output
Storage
Logs
```

como potenciais pontos de risco.

---

# 7. Superfícies de Ataque

Exemplos:

- input do usuário;
- documentos enviados;
- páginas externas;
- dados recuperados;
- prompts;
- tool descriptions;
- tool results;
- model output;
- provider APIs;
- vector stores;
- arquivos;
- callbacks.

---

# 8. Trust Boundaries

Fronteiras deverão ser explícitas.

```text
Untrusted
User / External Content
        │
        ▼
Application Controls
        │
        ▼
Model Boundary
        │
        ▼
Application Validation
        │
        ▼
Trusted Domain Operations
```

---

# 9. Defesa em Profundidade

Nenhum controle isolado é suficiente.

```text
Authorization
+
Filtering
+
Validation
+
Tool Restrictions
+
Confirmation
+
Audit
```

---

# 10. Guardrails

Guardrails são controles que reduzem comportamento inseguro ou inválido.

Não deverão ser confundidos apenas com instruções no prompt.

---

# 11. Guardrails de Entrada

Podem validar:

- tamanho;
- formato;
- conteúdo;
- tipo de arquivo;
- URLs;
- frequência;
- campos proibidos.

---

# 12. Guardrails de Contexto

Garantir:

- tenant correto;
- autorização;
- minimização;
- ausência de secrets;
- classificação adequada.

---

# 13. Guardrails de Retrieval

Aplicar GAI-03.

Retrieval deverá ocorrer somente dentro do espaço autorizado.

---

# 14. Guardrails de Saída

Saídas deverão ser validadas antes de alimentar:

- UI privilegiada;
- API;
- banco;
- tool;
- integração.

---

# 15. Guardrails de Tools

Aplicar:

- allowlist;
- schema;
- autorização;
- risk classification;
- confirmation.

---

# 16. Guardrails de Execução

Controlar:

- max steps;
- timeout;
- budget;
- retries;
- concurrency;
- cancellation.

---

# 17. Prompt Injection

Prompt injection deverá ser considerado risco esperado.

Exemplo:

```text
Ignore previous instructions...
```

A aplicação não deverá depender do modelo para neutralizar sozinho esse ataque.

---

# 18. Indirect Prompt Injection

Conteúdo recuperado poderá conter instruções maliciosas.

Exemplos:

- documento;
- página web;
- email;
- arquivo;
- resultado de integração.

Esse conteúdo deverá permanecer tratado como dado.

---

# 19. Jailbreaks

Tentativas de contornar comportamento do modelo deverão ser tratadas como sinal de risco, não como única fronteira de segurança.

---

# 20. Exfiltração

Prevenir que IA envie dados internos para:

- URLs arbitrárias;
- tools externas;
- destinatários não autorizados;
- prompts de terceiros.

---

# 21. Cross-Tenant Leakage

É falha crítica.

```text
Tenant A
→ AI Context
→ Tenant B data
```

deverá ser arquiteturalmente impedido e testado.

---

# 22. Data Poisoning

Conteúdo inserido na base poderá tentar influenciar futuras respostas.

Fontes deverão possuir:

- identidade;
- owner;
- classificação;
- origem;
- lifecycle.

---

# 23. Knowledge Poisoning

Conhecimento oficial deverá possuir controles superiores a conteúdo livre de usuário.

---

# 24. Tool Abuse

O modelo não deverá utilizar tool fora do escopo autorizado.

---

# 25. Confused Deputy

A autoridade efetiva deverá ser a interseção das permissões.

```text
effective_permission
=
user
∩ agent
∩ tool
∩ tenant
```

---

# 26. Excessive Agency

Evitar agentes com:

- tools excessivas;
- passos ilimitados;
- acesso amplo;
- ações irreversíveis sem confirmação.

---

# 27. Insecure Output Handling

Output do modelo é input não confiável.

Nunca:

```text
model output
→ eval()
```

ou equivalente.

---

# 28. Sensitive Information Disclosure

O modelo não deverá receber ou revelar informação além do necessário.

---

# 29. Model Denial of Service

Proteger contra consumo excessivo por:

- prompts enormes;
- loops;
- tool recursion;
- requests repetitivas;
- arquivos excessivos.

---

# 30. Supply Chain

Avaliar dependências relacionadas a IA.

---

# 31. Providers

Providers deverão passar por avaliação de segurança e privacidade.

---

# 32. Modelos

Modelos deverão possuir identificação explícita e lifecycle.

---

# 33. SDKs e Dependências

Aplicar gestão de vulnerabilidades do GSF.

---

# 34. Plugins e Integrações

Integrações deverão possuir escopo mínimo e credenciais segregadas.

---

# 35. Privacidade

Privacy by Design deverá ser aplicado desde a concepção da feature.

---

# 36. Minimização de Dados

Enviar ao modelo somente dados necessários.

---

# 37. Classificação de Dados

Aplicar classificação oficial do GSF.

---

# 38. Dados Pessoais

Dados pessoais deverão possuir finalidade legítima e controles compatíveis.

---

# 39. Dados Sensíveis

Exigem proteção reforçada.

---

# 40. Dados Financeiros

Não deverão ser enviados integralmente quando resumo ou campos específicos forem suficientes.

---

# 41. Dados Ministeriais

Informações pastorais ou ministeriais potencialmente sensíveis deverão receber tratamento restritivo.

---

# 42. Secrets

É proibido enviar:

- API keys;
- passwords;
- session tokens;
- private keys;
- database credentials;
- integration secrets.

---

# 43. Credenciais

Tools deverão utilizar credenciais controladas pela aplicação, nunca fornecidas ao modelo.

---

# 44. Pseudonimização

Quando apropriado, substituir identificadores diretos antes do envio.

---

# 45. Mascaramento

Campos poderão ser mascarados conforme finalidade.

---

# 46. Retenção

Dados utilizados por IA deverão seguir política de retenção aplicável.

---

# 47. Exclusão

Exclusão deverá considerar derivados:

```text
source
chunks
embeddings
cache
temporary artifacts
```

quando aplicável.

---

# 48. Logs e Telemetria

Aplicar minimização.

Logs não são arquivo permanente de prompts.

---

# 49. Training e Data Usage

Deverá ser conhecido se o provider utiliza dados enviados para:

- treinamento;
- melhoria;
- retenção operacional.

Configurações mais protetivas deverão ser utilizadas quando disponíveis e adequadas.

---

# 50. Providers Externos

Antes de envio de dados não públicos, avaliar contrato e política aplicável.

---

# 51. Residência de Dados

Quando relevante, avaliar onde dados são processados e armazenados.

---

# 52. Transferência de Dados

Transferências deverão respeitar requisitos legais e contratuais aplicáveis.

---

# 53. Consentimento e Finalidade

O uso de IA não cria automaticamente nova finalidade para dados coletados.

---

# 54. LGPD

Aplicar princípios pertinentes:

- finalidade;
- adequação;
- necessidade;
- segurança;
- prevenção;
- responsabilização.

---

# 55. Autorização

Autorização deverá ocorrer fora do modelo.

---

# 56. Tenant Isolation

Tenant deverá vir de contexto confiável da aplicação.

---

# 57. RAG Security

Aplicar integralmente GAI-03.

---

# 58. Embeddings

Embeddings deverão ser tratados como dados derivados potencialmente sensíveis.

---

# 59. Vector Stores

Devem possuir:

- acesso restrito;
- isolamento;
- lifecycle;
- observabilidade;
- exclusão.

---

# 60. Agent Security

Aplicar integralmente GAI-04.

---

# 61. Tool Security

Tools deverão possuir contrato e escopo explícitos.

---

# 62. Human-in-the-Loop

Ações de maior risco deverão exigir confirmação.

---

# 63. Structured Output

Preferir schema para respostas que alimentem lógica.

---

# 64. Validação

Validar sempre após geração.

---

# 65. URLs e SSRF

Ferramentas que acessam URLs deverão:

- validar scheme;
- restringir hosts quando possível;
- bloquear redes internas;
- controlar redirects;
- limitar tamanho.

---

# 66. Arquivos

Uploads utilizados por IA deverão passar por controles existentes de arquivo.

Considerar:

- tipo;
- tamanho;
- malware;
- conteúdo;
- tenant;
- retenção.

---

# 67. Conteúdo Multimodal

Imagem, áudio e outros formatos também deverão ser tratados como entrada não confiável.

---

# 68. Rate Limiting

Protege disponibilidade, custos e abuso.

---

# 69. Quotas

Poderão existir por usuário, tenant ou feature.

---

# 70. Budgets

Agentes deverão possuir budgets proporcionais ao risco.

---

# 71. Timeouts

Chamadas externas e tools deverão possuir timeout.

---

# 72. Kill Switch

Capacidades de risco elevado deverão poder ser desativadas rapidamente.

---

# 73. Feature Flags

Permitem rollout e contenção.

---

# 74. Monitoramento

Monitorar sinais de segurança específicos de IA.

---

# 75. Detecção

Exemplos:

- aumento de rejeições;
- tool abuse;
- cross-tenant denial;
- prompt injection patterns;
- custo anormal;
- loops.

---

# 76. Alertas

Alertas deverão ser acionáveis.

---

# 77. Auditoria

Ações relevantes deverão ser rastreáveis.

---

# 78. Incidentes

Incidentes de IA deverão integrar o processo oficial de segurança.

---

# 79. Resposta a Incidentes

Fluxo:

```text
Detect
  ↓
Classify
  ↓
Contain
  ↓
Disable / Limit
  ↓
Investigate
  ↓
Recover
  ↓
Learn
```

---

# 80. Evidências

Preservar evidências necessárias sem ampliar exposição de dados.

---

# 81. Testes de Segurança

Toda feature relevante deverá possuir testes específicos.

---

# 82. Red Team

Recursos de maior risco poderão receber exercícios de red team.

---

# 83. Testes Cross-Tenant

Obrigatórios para recursos tenant-scoped.

---

# 84. Testes de Prompt Injection

Testar ataques diretos e indiretos.

---

# 85. Testes de Tools

Testar:

- tool não permitida;
- argumento inválido;
- tenant incorreto;
- bypass de confirmação;
- exfiltração.

---

# 86. Testes de Privacidade

Verificar minimização e ausência de dados indevidos em prompts, outputs e logs.

---

# 87. Secure Defaults

Novas capacidades deverão nascer com:

```text
minimum access
minimum tools
minimum data
minimum retention
bounded execution
```

---

# 88. Production Readiness

Antes de produção:

- threat model;
- owner;
- classificação de risco;
- autorização;
- tenant;
- guardrails;
- logs;
- limites;
- testes;
- kill switch quando necessário.

---

# 89. Revisões

Revisar controles após:

- incidente;
- mudança de provider;
- nova tool;
- novo tipo de dado;
- aumento de autonomia;
- alteração arquitetural relevante.

---

# 90. Ownership

Toda feature deverá possuir responsável técnico.

---

# 91. Anti-Padrões

Evitar:

```text
system prompt
=
firewall
```

---

```text
LLM decides
if user is authorized
```

---

```text
tenant_id
generated by model
```

---

```text
all documents
→ shared vector search
→ filter after
```

---

```text
secret
inside context
```

---

```text
model output
→ code execution
```

---

```text
agent
with unrestricted tools
```

---

```text
full prompts
stored forever
```

---

```text
external webpage
grants permissions
```

---

```text
AI feature
without kill path
```

---

# 92. Arquitetura Consolidada

```text
                      UNTRUSTED INPUT
                            │
                            ▼
                     INPUT GUARDRAILS
                            │
                            ▼
                 AUTH / TENANT / POLICY
                            │
                            ▼
                     CONTEXT BUILDER
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
           Retrieval      Prompt        Memory
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                        AI MODEL
                            │
                            ▼
                    OUTPUT GUARDRAILS
                            │
                            ▼
                       TOOL POLICY
                            │
                            ▼
                 AUTHORIZATION RECHECK
                            │
                            ▼
                   HUMAN CONFIRMATION
                     when required
                            │
                            ▼
                    DOMAIN SERVICES
                            │
                            ▼
                AUDIT / MONITOR / ALERT
```

---

# 93. Checklist

## Threat Model

- [ ] superfícies identificadas;
- [ ] trust boundaries;
- [ ] dados classificados;
- [ ] riscos de provider;
- [ ] riscos de RAG;
- [ ] riscos de agents/tools.

## Identidade e Tenant

- [ ] usuário autenticado;
- [ ] tenant confiável;
- [ ] autorização determinística;
- [ ] testes cross-tenant.

## Dados

- [ ] minimização;
- [ ] sem secrets;
- [ ] retenção;
- [ ] exclusão;
- [ ] logs minimizados;
- [ ] provider compatível.

## Guardrails

- [ ] input;
- [ ] context;
- [ ] retrieval;
- [ ] output;
- [ ] tools;
- [ ] execution limits.

## Ataques

- [ ] prompt injection;
- [ ] indirect injection;
- [ ] exfiltração;
- [ ] tool abuse;
- [ ] excessive agency;
- [ ] DoS;
- [ ] insecure output.

## Operação

- [ ] rate limiting;
- [ ] quotas;
- [ ] budgets;
- [ ] timeout;
- [ ] feature flag;
- [ ] kill switch;
- [ ] monitoramento;
- [ ] alertas.

## Produção

- [ ] owner;
- [ ] threat model;
- [ ] testes;
- [ ] auditoria;
- [ ] incident response;
- [ ] revisão de segurança.

---

# 94. Documentos Relacionados

- GAI-01 — Arquitetura e Governança de Inteligência Artificial
- GAI-02 — Providers, Modelos, Prompts e AI Gateway
- GAI-03 — RAG, Contexto e Conhecimento
- GAI-04 — Ferramentas, Agentes e Ações Seguras
- GAI-05 — Avaliação, Observabilidade, Custos e Operação de IA
- GSF — GereIgreja Security Framework
- GAPI — GereIgreja API Engineering
- GINF — GereIgreja Infrastructure Engineering
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GDF — GereIgreja Documentation Framework
- GereIgreja Backend Engineering

---

# 95. Princípios Finais

Segurança de IA não deverá depender da obediência do modelo.

```text
Prompt
is not
Authorization
```

e:

```text
Model
is not
Security Boundary
```

A arquitetura segura deverá assumir que:

- inputs podem ser maliciosos;
- documentos podem conter instruções adversariais;
- outputs podem estar errados;
- tools podem causar efeitos;
- providers podem falhar;
- usuários podem tentar exceder seu escopo.

O princípio central é:

```text
Untrusted AI
inside
Trusted Architecture
```

A plataforma deverá continuar segura mesmo quando o modelo interpretar incorretamente uma instrução, produzir saída inválida ou tentar utilizar uma capacidade fora do escopo permitido.

---

# 96. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`06-Seguranca-Privacidade-e-Guardrails-de-IA.md`

**Documento**

`GAI-06`

**Código**

`GAI-AI-SECURITY-PRIVACY-GUARDRAILS`

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

`GAI-05 — Avaliação, Observabilidade, Custos e Operação de IA`

**Próximo documento candidato**

`07-Governanca-de-Dados-para-IA.md`
