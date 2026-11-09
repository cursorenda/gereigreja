Pasta:

docs/ai/

Arquivo:

22-Politica-de-Uso-Aceitavel-e-Praticas-Proibidas-de-IA.md

Documento:

GAI-22

Código:

GAI-AI-ACCEPTABLE-USE-PROHIBITED-PRACTICES

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

# GAI-22 — Política de Uso Aceitável e Práticas Proibidas de Inteligência Artificial

> "Capacidade técnica não implica autorização. Toda utilização de IA precisa respeitar finalidade, dados, autoridade, risco e limites explicitamente definidos."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com a Família GAI
4. Princípios Fundamentais
5. Política de Uso Aceitável
6. Usuários Abrangidos
7. Sistemas Abrangidos
8. Finalidade Autorizada
9. Necessidade de Negócio
10. Classificação de Risco
11. Uso Experimental
12. Uso em Produção
13. Uso Interno
14. Uso Voltado ao Cliente
15. Dados Permitidos
16. Dados Restritos
17. Dados Pessoais
18. Dados Sensíveis
19. Credenciais e Secrets
20. Dados de Tenant
21. Conteúdo de Terceiros
22. Propriedade Intelectual
23. Providers Aprovados
24. Modelos Aprovados
25. Ferramentas Não Aprovadas
26. Shadow AI
27. Contas Pessoais
28. Upload de Dados
29. Prompting Seguro
30. Prompt Injection
31. Output Handling
32. Validação Humana
33. Decisões de Alto Impacto
34. Automação
35. Agentes
36. Tools
37. Ações Mutáveis
38. Human-in-the-Loop
39. Autonomia
40. Limites de Execução
41. Comunicação com Usuários
42. Transparência
43. Representação de Conteúdo
44. Alucinações
45. Conteúdo Incorreto
46. Segurança
47. Privacidade
48. Tenant Isolation
49. Compliance
50. Práticas Proibidas
51. Exfiltração de Dados
52. Bypass de Autorização
53. Cross-Tenant Access
54. Uso de Secrets
55. Desativação de Guardrails
56. Provider Não Aprovado
57. Modelo Não Aprovado
58. Agente Sem Limites
59. Ações Irreversíveis Não Controladas
60. Autoaprovação
61. Manipulação de Evidências
62. Logging Indevido
63. Uso para Vigilância Indevida
64. Perfilamento Indevido
65. Discriminação
66. Engano
67. Impersonação
68. Conteúdo Fraudulento
69. Uso Ilegal
70. Uso Contrário a Contratos
71. Uso sem Base Autorizada
72. Uso Fora da Finalidade
73. Treinamento Não Autorizado
74. Retenção Não Autorizada
75. Exportação Não Autorizada
76. Uso de Dados Reais em Testes
77. Produção sem Avaliação
78. Produção sem Owner
79. Produção sem Observabilidade
80. Produção sem Kill Switch
81. Exceções
82. Solicitação de Exceção
83. Aprovação
84. Validade
85. Controles Compensatórios
86. Revogação
87. Enforcement
88. Controles Preventivos
89. Controles Detectivos
90. Controles Corretivos
91. AI Gateway
92. IAM
93. DLP
94. Policy as Code
95. Logging e Auditoria
96. Monitoramento
97. Violações
98. Classificação da Violação
99. Resposta
100. Incidentes
101. Escalation
102. Evidências
103. Treinamento
104. Awareness
105. Responsabilidades
106. Terceiros
107. Revisão da Política
108. Métricas
109. Production Readiness
110. Templates
111. Anti-Padrões
112. Arquitetura Consolidada
113. Checklist
114. Documentos Relacionados
115. Princípios Finais
116. Status do Documento

---

# 1. Objetivo

Este documento estabelece a política oficial de uso aceitável e práticas proibidas para Inteligência Artificial no GereIgreja.

Seu objetivo é definir limites claros para utilização de modelos, providers, ferramentas, agentes e dados, reduzindo riscos de segurança, privacidade, isolamento, conformidade, qualidade e uso indevido.

---

# 2. Escopo

Aplica-se a:

- colaboradores;
- desenvolvedores;
- administradores;
- operadores;
- prestadores autorizados;
- sistemas internos;
- features de produto;
- automações;
- agentes;
- ferramentas de IA;
- providers externos;
- ambientes de desenvolvimento, teste e produção.

---

# 3. Relação com a Família GAI

```text
GAI-06
Security / Privacy / Guardrails
        │
GAI-11
Use Cases / Risk
        │
GAI-14
Agents / Autonomy / HITL
        │
GAI-16
Third Parties / Providers
        │
GAI-18
Audit / Evidence
        │
GAI-21
Roles / Responsibilities
        │
        ▼
GAI-22
Acceptable Use / Prohibited Practices
```

---

# 4. Princípios Fundamentais

Aplicar:

- authorized purpose only;
- approved systems only;
- minimum necessary data;
- least privilege;
- tenant isolation;
- human accountability;
- no implicit autonomy;
- secure by default;
- auditable use;
- prohibition by risk, not convenience.

---

# 5. Política de Uso Aceitável

O uso de IA deverá possuir finalidade legítima e compatível com os objetivos do GereIgreja.

---

# 6. Usuários Abrangidos

Qualquer pessoa com acesso a recursos de IA corporativos está sujeita a esta política.

---

# 7. Sistemas Abrangidos

Inclui sistemas oficiais e integrações autorizadas que processem dados ou executem ações por meio de IA.

---

# 8. Finalidade Autorizada

IA somente deverá ser utilizada para finalidade aprovada ou compatível com o escopo autorizado.

---

# 9. Necessidade de Negócio

A adoção de IA deverá resolver necessidade real ou produzir valor mensurável.

---

# 10. Classificação de Risco

Novos casos de uso deverão seguir GAI-11.

---

# 11. Uso Experimental

Experimentos deverão utilizar ambiente e dados adequados ao nível de risco.

---

# 12. Uso em Produção

Exige controles, owner, avaliação e release aplicáveis.

---

# 13. Uso Interno

Uso interno não elimina requisitos de segurança, privacidade ou proteção de dados.

---

# 14. Uso Voltado ao Cliente

Features expostas a clientes deverão possuir comportamento, limitações e fallback adequados.

---

# 15. Dados Permitidos

Somente dados necessários e autorizados à finalidade deverão ser processados.

---

# 16. Dados Restritos

Dados classificados deverão respeitar controles específicos antes do envio a modelos ou providers.

---

# 17. Dados Pessoais

Tratamento deverá seguir políticas de privacidade e requisitos aplicáveis.

---

# 18. Dados Sensíveis

Dados sensíveis exigem avaliação proporcional ao risco e controles reforçados.

---

# 19. Credenciais e Secrets

É proibido inserir deliberadamente em prompts:

- senhas;
- API keys;
- private keys;
- tokens;
- secrets;
- credenciais de infraestrutura.

---

# 20. Dados de Tenant

Dados de um tenant nunca deverão ser disponibilizados a outro tenant.

---

# 21. Conteúdo de Terceiros

Uso deverá respeitar autorização, contratos e direitos aplicáveis.

---

# 22. Propriedade Intelectual

Conteúdo protegido não deverá ser utilizado fora dos direitos e finalidades autorizados.

---

# 23. Providers Aprovados

Dados corporativos somente deverão ser processados por providers aprovados para a classe de uso correspondente.

---

# 24. Modelos Aprovados

Produção deverá utilizar modelos ou aliases aprovados.

---

# 25. Ferramentas Não Aprovadas

Ferramentas externas não aprovadas não deverão receber dados corporativos protegidos.

---

# 26. Shadow AI

Shadow AI é o uso de ferramentas ou serviços de IA fora dos processos e controles aprovados.

Deverá ser prevenido e tratado como risco de governança.

---

# 27. Contas Pessoais

Contas pessoais em serviços de IA não deverão ser utilizadas para processar dados corporativos restritos.

---

# 28. Upload de Dados

Antes de upload, verificar:

```text
Is this data necessary?
Is it authorized?
Is the provider approved?
Is retention acceptable?
Does tenant isolation remain intact?
```

---

# 29. Prompting Seguro

Prompts não deverão solicitar ações ou informações incompatíveis com permissões do usuário.

---

# 30. Prompt Injection

Conteúdo recuperado ou fornecido por usuários deverá ser tratado como não confiável quando puder influenciar instruções.

---

# 31. Output Handling

Outputs de IA deverão ser tratados conforme criticidade.

---

# 32. Validação Humana

Conteúdo de alto impacto poderá exigir revisão humana antes de produzir efeito.

---

# 33. Decisões de Alto Impacto

IA não deverá assumir autoridade decisória além do nível explicitamente aprovado.

---

# 34. Automação

Automação deverá possuir limites, observabilidade e mecanismo de interrupção.

---

# 35. Agentes

Agentes deverão seguir GAI-14.

---

# 36. Tools

Tools deverão possuir contratos e autorização explícita.

---

# 37. Ações Mutáveis

Ações que alteram estado deverão possuir proteção proporcional ao impacto.

---

# 38. Human-in-the-Loop

HITL deverá ser utilizado quando exigido pelo risco.

---

# 39. Autonomia

Autonomia deverá ser concedida explicitamente.

---

# 40. Limites de Execução

Agentes deverão possuir limites aplicáveis, como:

```text
max_steps
max_runtime
max_cost
allowed_tools
allowed_scope
```

---

# 41. Comunicação com Usuários

Não representar capacidade de IA como infalível.

---

# 42. Transparência

Quando relevante, usuários deverão compreender que estão interagindo com ou recebendo conteúdo produzido por IA.

---

# 43. Representação de Conteúdo

Conteúdo gerado não deverá ser apresentado como fato verificado quando não houver validação suficiente.

---

# 44. Alucinações

Risco de alucinação deverá ser tratado no design e na experiência.

---

# 45. Conteúdo Incorreto

Erros materiais deverão possuir mecanismo de correção ou fallback quando necessário.

---

# 46. Segurança

Aplicar GAI-06 e GSF.

---

# 47. Privacidade

Aplicar minimização, finalidade e retenção apropriadas.

---

# 48. Tenant Isolation

Isolamento é requisito estrutural, não instrução de prompt.

---

# 49. Compliance

Uso deverá respeitar requisitos legais, contratuais e políticas internas aplicáveis.

---

# 50. Práticas Proibidas

As práticas a seguir são proibidas salvo quando uma seção explicitamente permitir processo formal de exceção e a exceção for tecnicamente e juridicamente admissível.

---

# 51. Exfiltração de Dados

É proibido utilizar IA para extrair, transferir ou revelar dados sem autorização.

---

# 52. Bypass de Autorização

É proibido utilizar modelos, agentes ou tools para contornar controles de acesso.

---

# 53. Cross-Tenant Access

É proibido acessar ou inferir dados de outro tenant sem autorização legítima e controle técnico apropriado.

---

# 54. Uso de Secrets

É proibido fornecer secrets a modelos como mecanismo de execução.

Tools deverão receber credenciais por infraestrutura segura.

---

# 55. Desativação de Guardrails

É proibido remover controles obrigatórios sem processo autorizado.

---

# 56. Provider Não Aprovado

É proibido processar dados protegidos em provider não aprovado.

---

# 57. Modelo Não Aprovado

É proibido utilizar em produção modelo não autorizado para o caso de uso.

---

# 58. Agente Sem Limites

É proibido colocar em produção agente de autonomia relevante sem limites operacionais.

---

# 59. Ações Irreversíveis Não Controladas

É proibido delegar ações destrutivas ou irreversíveis sem controles proporcionais.

---

# 60. Autoaprovação

Agente não deverá aprovar a própria ação quando HITL independente for exigido.

---

# 61. Manipulação de Evidências

É proibido apagar, adulterar ou fabricar evidências para ocultar comportamento ou violação.

---

# 62. Logging Indevido

É proibido registrar indiscriminadamente dados sensíveis, secrets ou conteúdo sem finalidade.

---

# 63. Uso para Vigilância Indevida

É proibido utilizar IA para monitoramento invasivo ou incompatível com finalidade e autorização aplicáveis.

---

# 64. Perfilamento Indevido

É proibido criar perfis pessoais sem finalidade, base e controles apropriados.

---

# 65. Discriminação

É proibido projetar ou utilizar IA deliberadamente para discriminação ilícita ou tratamento incompatível com políticas aplicáveis.

---

# 66. Engano

É proibido utilizar IA para enganar usuários sobre identidade, autoridade ou natureza de uma ação de forma materialmente prejudicial.

---

# 67. Impersonação

É proibida impersonação não autorizada de pessoas ou organizações.

---

# 68. Conteúdo Fraudulento

É proibido utilizar IA para fraude, falsificação ou manipulação maliciosa.

---

# 69. Uso Ilegal

É proibido utilizar IA para atividade ilegal.

---

# 70. Uso Contrário a Contratos

É proibido violar obrigações contratuais de clientes, fornecedores ou parceiros.

---

# 71. Uso sem Base Autorizada

Dados não deverão ser processados apenas porque estão tecnicamente acessíveis.

---

# 72. Uso Fora da Finalidade

Dados coletados para uma finalidade não deverão ser reutilizados por IA sem avaliação apropriada.

---

# 73. Treinamento Não Autorizado

É proibido utilizar dados corporativos ou de clientes para treinamento/fine-tuning não aprovado.

---

# 74. Retenção Não Autorizada

É proibido manter dados além da política ou finalidade autorizada.

---

# 75. Exportação Não Autorizada

É proibido exportar datasets, logs ou evidências sem autorização.

---

# 76. Uso de Dados Reais em Testes

Dados reais protegidos não deverão ser utilizados em testes quando dados sintéticos ou adequadamente anonimizados forem suficientes.

---

# 77. Produção sem Avaliação

É proibido promover capacidade material de IA sem avaliações exigidas pelo risco.

---

# 78. Produção sem Owner

Nenhuma capacidade de IA deverá operar em produção sem owner.

---

# 79. Produção sem Observabilidade

Capacidades críticas não deverão operar sem sinais mínimos de operação e incidente.

---

# 80. Produção sem Kill Switch

Agentes ou automações de alto impacto não deverão operar sem mecanismo apropriado de interrupção.

---

# 81. Exceções

Nem toda proibição admite exceção.

Exceções somente poderão existir quando:

- permitidas por política superior;
- tecnicamente seguras;
- juridicamente admissíveis;
- limitadas em escopo e tempo.

---

# 82. Solicitação de Exceção

Deverá registrar:

```text
control
reason
scope
risk
duration
owner
compensating controls
```

---

# 83. Aprovação

A autoridade de aprovação deverá refletir o risco.

---

# 84. Validade

Toda exceção deverá possuir expiração ou revisão obrigatória.

---

# 85. Controles Compensatórios

Deverão reduzir materialmente o risco durante a exceção.

---

# 86. Revogação

Exceções poderão ser revogadas imediatamente diante de incidente ou mudança de risco.

---

# 87. Enforcement

A política deverá ser aplicada tecnicamente sempre que possível.

---

# 88. Controles Preventivos

Exemplos:

- allowlists;
- IAM;
- provider restrictions;
- model aliases;
- DLP;
- feature gates.

---

# 89. Controles Detectivos

Exemplos:

- audit logs;
- anomaly detection;
- cost alerts;
- policy violations.

---

# 90. Controles Corretivos

Exemplos:

- revoke;
- rollback;
- disable;
- kill switch;
- incident response.

---

# 91. AI Gateway

Deverá centralizar controles possíveis sobre providers, modelos e políticas de execução.

---

# 92. IAM

Permissões deverão seguir least privilege.

---

# 93. DLP

Controles de prevenção de perda de dados poderão ser aplicados conforme classificação.

---

# 94. Policy as Code

Regras objetivas deverão ser automatizadas quando apropriado.

Exemplos:

```text
deny unapproved provider
deny unapproved model
deny agent without max_steps
deny production asset without owner
```

---

# 95. Logging e Auditoria

Violações e ações relevantes deverão produzir evidências adequadas.

---

# 96. Monitoramento

Monitorar padrões de uso incompatíveis com a política.

---

# 97. Violações

Suspeitas de violação deverão ser avaliadas proporcionalmente ao impacto.

---

# 98. Classificação da Violação

Categorias sugeridas:

```text
POLICY-LOW
POLICY-MEDIUM
POLICY-HIGH
POLICY-CRITICAL
```

---

# 99. Resposta

A resposta poderá incluir:

- contenção;
- revogação de acesso;
- bloqueio técnico;
- investigação;
- correção;
- treinamento;
- processo de incidente.

---

# 100. Incidentes

Violações com impacto material deverão seguir GAI-17 e processos de segurança aplicáveis.

---

# 101. Escalation

Escalonar imediatamente quando envolver:

- cross-tenant;
- secrets;
- dados sensíveis;
- ações destrutivas;
- fraude;
- comprometimento de provider;
- exposição material.

---

# 102. Evidências

Preservar evidências conforme GAI-18.

---

# 103. Treinamento

Usuários autorizados deverão receber orientação proporcional ao uso.

---

# 104. Awareness

A política deverá ser comunicada em linguagem adequada ao público.

---

# 105. Responsabilidades

Aplicar GAI-21.

Managers e owners deverão assegurar que suas equipes conheçam limites relevantes.

---

# 106. Terceiros

Prestadores e parceiros com acesso a recursos de IA deverão observar requisitos equivalentes quando aplicável.

---

# 107. Revisão da Política

Revisar diante de:

- novos riscos;
- novos providers;
- novos tipos de agente;
- incidentes;
- mudanças regulatórias;
- evolução arquitetural.

---

# 108. Métricas

Exemplos:

```text
ai_policy_violations
ai_shadow_ai_findings
ai_unapproved_provider_attempts
ai_unapproved_model_attempts
ai_secret_exposure_attempts
ai_cross_tenant_policy_events
ai_exceptions_open
ai_exceptions_expired
ai_training_coverage
```

---

# 109. Production Readiness

Antes de produção:

```text
authorized purpose?
approved provider?
approved model?
allowed data?
owner?
risk classification?
guardrails?
authorization?
observability?
kill switch if required?
audit trail?
```

---

# 110. Templates

## AI Acceptable Use Assessment

```text
Use Case ID:
Owner:
Purpose:

Users:
Environment:
Provider:
Model:

Data Classes:
Tenant Data:
Personal Data:
Sensitive Data:

Allowed Actions:
Prohibited Actions:
Tools:
Autonomy Level:

Human Review:
Guardrails:
Monitoring:

Risk Level:
Approval:
Review Date:
```

## AI Policy Exception

```text
Exception ID:
Requester:
Owner:

Policy / Control:
Requested Exception:
Business Reason:

Scope:
Affected Assets:
Affected Tenants:
Data Classes:

Risk:
Compensating Controls:

Start Date:
Expiration Date:

Approver:
Evidence:
Status:
```

---

# 111. Anti-Padrões

Evitar:

```text
public AI tool
+
customer data
+
personal account
```

---

```text
"the model will not leak it"
as tenant isolation
```

---

```text
agent has admin credentials
because it is easier
```

---

```text
production experiment
without owner
```

---

```text
disable guardrail
to fix UX
```

---

```text
copy production database
into AI sandbox
```

---

```text
prompt contains API key
```

---

```text
human approval
=
click approve without context
```

---

```text
policy exception
with no expiration
```

---

# 112. Arquitetura Consolidada

```text
                        USER / SYSTEM
                              │
                              ▼
                       AUTHORIZED PURPOSE
                              │
                              ▼
                      RISK CLASSIFICATION
                              │
                              ▼
                         DATA POLICY
                              │
                              ▼
                         AI GATEWAY
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
            PROVIDER        MODEL         GUARDRAILS
               │              │              │
               └──────────────┼──────────────┘
                              ▼
                         AI EXECUTION
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
             OUTPUT          TOOL          AGENT
               │              │              │
               └──────────────┼──────────────┘
                              ▼
                      POLICY ENFORCEMENT
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
              ALLOW                      DENY
                 │                         │
                 ▼                         ▼
              AUDIT                 ALERT / INCIDENT
```

---

# 113. Checklist

## Finalidade

- [ ] finalidade autorizada;
- [ ] necessidade de negócio;
- [ ] risk classification;
- [ ] owner.

## Dados

- [ ] minimização;
- [ ] classificação;
- [ ] tenant isolation;
- [ ] personal data review;
- [ ] sensitive data review;
- [ ] no secrets in prompts.

## Tecnologia

- [ ] provider aprovado;
- [ ] modelo aprovado;
- [ ] AI Gateway;
- [ ] IAM;
- [ ] guardrails;
- [ ] observabilidade.

## Agentes e Tools

- [ ] allowed tools;
- [ ] authorization;
- [ ] autonomy level;
- [ ] max steps;
- [ ] budget;
- [ ] HITL;
- [ ] kill switch.

## Uso

- [ ] no shadow AI;
- [ ] no personal account for protected data;
- [ ] no unauthorized training;
- [ ] no unauthorized export;
- [ ] no bypass;
- [ ] no cross-tenant access.

## Governança

- [ ] exceptions documented;
- [ ] expiration;
- [ ] compensating controls;
- [ ] evidence;
- [ ] monitoring;
- [ ] training.

---

# 114. Documentos Relacionados

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
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GINF — GereIgreja Infrastructure Engineering
- GDF — GereIgreja Documentation Framework

---

# 115. Princípios Finais

O fato de uma ferramenta de IA conseguir executar uma tarefa não significa que esteja autorizada a executá-la.

```text
Possible
≠
Permitted
```

O princípio central é:

```text
Use approved systems.

Process only necessary data.

Respect tenant boundaries.

Never expose secrets.

Limit autonomy.

Require authorization.

Preserve human accountability.

Block prohibited practices by design.
```

No GereIgreja, o uso responsável de Inteligência Artificial deverá ser protegido por políticas claras, controles técnicos e responsabilidade humana verificável.

---

# 116. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`22-Politica-de-Uso-Aceitavel-e-Praticas-Proibidas-de-IA.md`

**Documento**

`GAI-22`

**Código**

`GAI-AI-ACCEPTABLE-USE-PROHIBITED-PRACTICES`

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

`GAI-21 — Responsabilidades, Papéis e Modelo Operacional de Inteligência Artificial`

**Próximo documento candidato**

`23-Gestao-de-Mudancas-e-Excecoes-de-IA.md`
