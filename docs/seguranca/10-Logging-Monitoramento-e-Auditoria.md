Pasta:

docs/seguranca/

Arquivo:

10-Logging-Monitoramento-e-Auditoria.md

Documento:

GSF-10

Código:

GSF-LOGGING-MONITORING-AUDIT

Família:

GSF — GereIgreja Security

Framework:

GSF — GereIgreja Security Framework

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GSF-10 — Logging, Monitoramento e Auditoria

> "No GereIgreja, registrar eventos não significa apenas guardar mensagens técnicas. Significa produzir evidências suficientes para diagnosticar falhas, detectar comportamentos anormais, reconstruir operações relevantes e preservar a rastreabilidade da plataforma."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Relação entre Logging, Monitoramento e Auditoria
5. Princípios
6. Observabilidade de Segurança
7. Logging
8. Monitoramento
9. Auditoria
10. Diferença entre Log Técnico e Registro de Auditoria
11. Eventos que Devem ser Registrados
12. Login
13. Logout
14. Falhas de Autenticação
15. Alterações de Identidade
16. Alterações de Permissões
17. Mudanças de Grupo
18. Alterações de Tenant
19. Acessos Negados
20. Operações Financeiras
21. Exclusões
22. Exportações
23. Importações
24. Integrações
25. Webhooks
26. Tasks
27. Automações
28. Comunicação
29. Django Admin
30. Operações Administrativas
31. Configurações Críticas
32. Incidentes
33. Eventos de Infraestrutura
34. Estrutura de um Evento
35. Timestamp
36. Identidade
37. Tenant
38. Recurso
39. Operação
40. Resultado
41. Origem
42. Correlação
43. Request ID
44. Correlation ID
45. Níveis de Log
46. DEBUG
47. INFO
48. WARNING
49. ERROR
50. CRITICAL
51. Escolha do Nível Correto
52. Logs de Segurança
53. Logs de Aplicação
54. Logs de Infraestrutura
55. Logs de Integração
56. Logs de Tasks
57. Logs Financeiros
58. Logs Multi-Tenant
59. Dados que Não Devem ser Logados
60. Senhas
61. Tokens
62. Secrets
63. Dados Pessoais
64. Dados Financeiros
65. Payloads
66. Headers
67. Cookies
68. Arquivos
69. Sanitização de Logs
70. Minimização
71. Estrutura e Padronização
72. Logs Estruturados
73. Mensagens de Log
74. Exceções
75. Stack Traces
76. Contexto Técnico
77. Tratamento de Erros
78. Monitoramento de Disponibilidade
79. Monitoramento de Erros
80. Monitoramento de Performance
81. Monitoramento de Segurança
82. Monitoramento de Autenticação
83. Monitoramento de Autorização
84. Monitoramento Multi-Tenant
85. Monitoramento de APIs
86. Monitoramento de Integrações
87. Monitoramento de Cron Jobs
88. Monitoramento de Tasks
89. Monitoramento de Comunicação
90. Monitoramento Financeiro
91. Indicadores
92. Métricas
93. Alertas
94. Severidade de Alertas
95. Alertas Acionáveis
96. Ruído de Alertas
97. Thresholds
98. Detecção de Anomalias
99. Falhas Repetidas
100. Tentativas de Acesso Indevido
101. Enumeração
102. Brute Force
103. Vazamento Multi-Tenant
104. Falhas de Integração
105. Falhas de Backup
106. Auditoria Funcional
107. Auditoria de Segurança
108. Auditoria Administrativa
109. Auditoria Financeira
110. Auditoria de Permissões
111. Auditoria de Exportação
112. Auditoria de Integrações
113. Imutabilidade
114. Integridade dos Registros
115. Retenção
116. Acesso aos Logs
117. Acesso aos Registros de Auditoria
118. Privacidade nos Logs
119. Multi-Tenant nos Logs
120. Centralização
121. Produção
122. Desenvolvimento
123. Homologação
124. Django Logging
125. `logging` do Python
126. Middlewares
127. Views
128. Services
129. Selectors
130. Signals
131. Tasks
132. APIs
133. HTMX
134. Frontend
135. JavaScript
136. Django Admin
137. Infraestrutura
138. Incidentes
139. Preservação de Evidências
140. Investigação
141. Correlação de Eventos
142. Linha do Tempo
143. Testes
144. Testes de Logging
145. Testes de Auditoria
146. Testes de Monitoramento
147. Testes Multi-Tenant
148. Testes de Privacidade
149. Revisões Periódicas
150. Evidências Arquiteturais
151. Especificações Oficiais
152. Anti-Padrões
153. Checklist
154. Documentos Relacionados
155. Princípios Finais
156. Status do Documento

---

# 1. Objetivo

Este documento estabelece os padrões oficiais de logging, monitoramento e auditoria do GereIgreja.

Seu objetivo é garantir que a plataforma possua informações suficientes para:

- diagnosticar falhas;
- monitorar disponibilidade;
- detectar comportamentos anormais;
- identificar tentativas de acesso indevido;
- rastrear operações críticas;
- investigar incidentes;
- reconstruir sequências de eventos;
- comprovar alterações relevantes;
- acompanhar integrações;
- apoiar continuidade operacional.

Logging, monitoramento e auditoria deverão funcionar de maneira complementar.

Nenhum deles deverá ser tratado isoladamente como solução completa de observabilidade ou segurança.

---

# 2. Escopo

Este documento aplica-se a:

- aplicação Django;
- Área de Gestão;
- Django Admin;
- APIs;
- Portal Público;
- Core;
- Secretaria;
- Financeiro;
- Comunicação;
- Eventos;
- Escola Bíblica;
- Patrimônio;
- Relatórios;
- Configurações;
- integrações;
- webhooks;
- tasks;
- cron jobs;
- automações;
- banco de dados;
- infraestrutura;
- serviços externos.

Também se aplica aos processos de investigação e resposta a incidentes.

---

# 3. Papel deste Documento

O GSF-10 concretiza os requisitos de monitoramento e auditoria definidos pelo GereIgreja Security Framework.

Sua relação é:

```text
GSF-01
Fundamentos
    ↓
GSF-09
Infraestrutura e Segredos
    ↓
GSF-10
Logging, Monitoramento e Auditoria
    ↓
GSF-13
Gestão de Incidentes
````

O GSF-10 produz a visibilidade necessária para detecção e investigação.

---

# 4. Relação entre Logging, Monitoramento e Auditoria

Os três conceitos possuem responsabilidades distintas.

```text
Logging
    ↓
Registrar eventos técnicos e operacionais

Monitoramento
    ↓
Observar estado, comportamento e tendências

Auditoria
    ↓
Preservar evidências de operações relevantes
```

Eles deverão trabalhar juntos.

Exemplo:

```text
Login falhou
    ↓
Log registra
    ↓
Monitoramento detecta repetição
    ↓
Alerta é gerado
    ↓
Auditoria e logs apoiam investigação
```

---

# 5. Princípios

Logging, monitoramento e auditoria deverão seguir:

* necessidade;
* rastreabilidade;
* minimização;
* contexto;
* consistência;
* integridade;
* segurança;
* acionabilidade;
* retenção adequada;
* privacidade.

Regra fundamental:

```text
Registrar o suficiente
para entender o evento,
mas não registrar
o suficiente para criar
um novo vazamento.
```

---

# 6. Observabilidade de Segurança

A segurança deverá possuir visibilidade sobre eventos relevantes.

Uma operação que não pode ser observada ou investigada possui maior risco operacional.

A observabilidade deverá permitir responder, quando aplicável:

```text
O que aconteceu?

Quando?

Quem estava envolvido?

Em qual tenant?

Qual recurso?

Qual resultado?

Qual contexto técnico?

Há eventos relacionados?
```

---

# 7. Logging

Logging é o registro técnico e operacional de eventos produzidos pelo sistema.

Exemplos:

* início de task;
* falha de integração;
* exceção;
* timeout;
* request inválido;
* acesso negado;
* erro de banco.

Logs podem ser utilizados para:

* diagnóstico;
* monitoramento;
* investigação;
* performance;
* segurança.

---

# 8. Monitoramento

Monitoramento observa continuamente o comportamento da plataforma.

Pode acompanhar:

* disponibilidade;
* erros;
* latência;
* recursos;
* integrações;
* tasks;
* falhas de autenticação;
* acessos negados;
* eventos críticos.

Monitoramento deverá transformar eventos em informação operacional.

---

# 9. Auditoria

Auditoria registra operações relevantes de forma orientada à rastreabilidade funcional e de segurança.

Exemplos definidos pelo GSF incluem:

* login;
* logout;
* alterações de permissões;
* movimentações financeiras;
* exclusões;
* exportações;
* integrações.

A auditoria deverá permitir reconstruir fatos relevantes.

---

# 10. Diferença entre Log Técnico e Registro de Auditoria

Exemplo de log técnico:

```text
Timeout ao chamar serviço de comunicação.
```

Exemplo de auditoria:

```text
Usuário 123
agendou comunicação 456
no tenant 10
às 14:32
com resultado SUCESSO.
```

Um registro poderá servir aos dois propósitos em alguns cenários, mas a distinção conceitual deverá permanecer clara.

---

# 11. Eventos que Devem ser Registrados

Eventos relevantes deverão ser definidos conforme risco.

Categorias principais:

```text
Identidade
Autorização
Tenant
Administração
Financeiro
Dados
Integrações
Infraestrutura
Incidentes
```

Nem toda ação de leitura deverá necessariamente gerar auditoria detalhada.

O nível de registro deverá ser proporcional à criticidade.

---

# 12. Login

Eventos de login poderão registrar:

* identidade;
* timestamp;
* resultado;
* origem adequada;
* contexto técnico necessário.

Não deverão registrar senha.

---

# 13. Logout

Logout poderá ser registrado quando necessário para rastreabilidade de sessão ou auditoria.

---

# 14. Falhas de Autenticação

Falhas poderão ser úteis para detectar:

* brute force;
* abuso;
* enumeração;
* credenciais comprometidas.

Não deverão revelar credenciais tentadas em texto claro.

---

# 15. Alterações de Identidade

Eventos como:

* criação;
* ativação;
* inativação;
* suspensão;
* revogação;

deverão possuir rastreabilidade conforme o risco.

---

# 16. Alterações de Permissões

Alterações de acesso deverão ser auditáveis quando relevantes.

Registrar, quando aplicável:

```text
Quem alterou?
Quem foi afetado?
Qual permissão?
Qual estado anterior?
Qual estado novo?
Quando?
```

---

# 17. Mudanças de Grupo

Inclusão ou remoção de grupo deverá ser rastreável quando afetar autorização.

---

# 18. Alterações de Tenant

Mudanças relevantes de associação ou contexto organizacional deverão ser registradas quando aplicável.

---

# 19. Acessos Negados

Acessos negados poderão gerar log de segurança.

Especial atenção a repetições envolvendo:

* outros tenants;
* recursos sequenciais;
* endpoints administrativos;
* permissões críticas.

Não deverá existir alerta para cada acesso negado comum sem contexto, pois isso pode gerar ruído excessivo.

---

# 20. Operações Financeiras

Movimentações financeiras deverão possuir rastreabilidade reforçada.

Podem incluir:

* criação;
* edição;
* exclusão;
* estorno;
* alteração relevante;
* exportação;
* fechamento ou operação equivalente.

Quando aplicável, registrar:

```text
Identidade
Tenant
Recurso
Operação
Valor ou referência mínima necessária
Resultado
Timestamp
```

Evitar reproduzir desnecessariamente todos os dados financeiros no log.

---

# 21. Exclusões

Exclusões relevantes deverão ser auditáveis.

O registro deverá permitir identificar:

* quem;
* o quê;
* quando;
* tenant;
* resultado.

Quando possível, utilizar referência ao recurso em vez de copiar todo o conteúdo excluído.

---

# 22. Exportações

Exportações podem gerar exposição em massa.

Deverão ser registradas quando o risco justificar.

Exemplos:

```text
Exportação de membros
Exportação financeira
Exportação de relatório
```

O evento poderá registrar:

* usuário;
* tenant;
* tipo de export;
* quantidade de registros;
* resultado.

---

# 23. Importações

Importações também podem alterar grande volume de dados.

Deverão registrar:

* origem;
* tenant;
* identidade;
* quantidade;
* resultado;
* falhas relevantes.

---

# 24. Integrações

Integrações deverão registrar eventos suficientes para diagnosticar:

* envio;
* recebimento;
* falha;
* timeout;
* resposta inválida;
* revogação;
* autenticação.

Não deverão registrar credenciais.

---

# 25. Webhooks

Webhooks poderão registrar:

* provedor;
* tipo de evento;
* timestamp;
* identificador externo;
* resultado;
* tenant quando aplicável.

Payload completo não deverá ser armazenado indiscriminadamente.

---

# 26. Tasks

Tasks deverão registrar:

* início quando relevante;
* finalização;
* falha;
* tenant;
* recurso;
* correlation ID quando aplicável.

---

# 27. Automações

Automações recorrentes deverão permitir identificar:

```text
Qual automação?
Quando iniciou?
Qual tenant?
Quantos registros?
Qual resultado?
```

Isso é especialmente importante para rotinas de comunicação e processos diários.

---

# 28. Comunicação

Operações de comunicação poderão registrar:

* criação;
* agendamento;
* tentativa de envio;
* resultado;
* falha;
* quantidade de destinatários.

Não registrar conteúdo confidencial integralmente sem necessidade.

---

# 29. Django Admin

Operações administrativas relevantes realizadas pelo Django Admin deverão permanecer rastreáveis.

Especial atenção a:

* usuários;
* permissões;
* grupos;
* configurações;
* exclusões;
* alterações sensíveis.

---

# 30. Operações Administrativas

Operações de alto privilégio deverão possuir registro proporcional ao risco.

---

# 31. Configurações Críticas

Mudanças em configurações de:

* segurança;
* integrações;
* permissões;
* identidade;
* tenant;

deverão ser auditadas quando relevantes.

---

# 32. Incidentes

Eventos relacionados a incidentes deverão possuir logs suficientes para investigação.

Não alterar ou excluir registros necessários durante resposta ao incidente sem estratégia de preservação.

---

# 33. Eventos de Infraestrutura

Podem incluir:

* deploy;
* indisponibilidade;
* falha de banco;
* reinício;
* falha de cron;
* erro de serviço externo.

---

# 34. Estrutura de um Evento

Um evento deverá possuir contexto suficiente.

Modelo conceitual:

```text
timestamp
event
actor
tenant
resource
operation
result
request_id
metadata
```

Nem todos os campos serão necessários em todos os eventos.

---

# 35. Timestamp

Todo evento deverá possuir timestamp confiável.

Preferir padrão consistente no backend e infraestrutura.

A apresentação ao usuário poderá ser convertida para o fuso aplicável.

---

# 36. Identidade

Quando houver usuário ou processo associado, registrar identificador adequado.

Preferir identificador estável.

Não depender somente de nome textual.

---

# 37. Tenant

Eventos organizacionais deverão registrar tenant quando isso auxiliar rastreabilidade.

Isso é fundamental para:

* investigação;
* segurança;
* segregação;
* análise de incidentes.

---

# 38. Recurso

O evento deverá identificar o recurso afetado quando necessário.

Exemplo:

```text
resource_type = membro
resource_id = 100
```

---

# 39. Operação

Operações deverão possuir nomes consistentes.

Exemplos:

```text
create
update
delete
export
login
logout
send
revoke
```

A nomenclatura final deverá seguir o padrão oficial implementado.

---

# 40. Resultado

Registrar resultado quando relevante:

```text
success
failure
denied
partial
```

---

# 41. Origem

A origem poderá incluir informações técnicas úteis, como:

* endpoint;
* serviço;
* task;
* integração.

Dados como IP deverão ser tratados conforme necessidade e privacidade.

---

# 42. Correlação

Eventos relacionados deverão poder ser correlacionados quando a arquitetura suportar.

Exemplo:

```text
Request
  ↓
Service
  ↓
Task
  ↓
Integração
```

A correlação facilita investigação.

---

# 43. Request ID

A plataforma deverá avaliar a utilização de identificador único por request.

Exemplo conceitual:

```text
request_id = abc123
```

Isso permite acompanhar um fluxo em múltiplos logs.

---

# 44. Correlation ID

Fluxos que atravessam:

* API;
* task;
* integração;
* webhook;

poderão utilizar correlation ID.

Sua adoção deverá ser padronizada antes do uso transversal.

---

# 45. Níveis de Log

Os níveis deverão ser utilizados consistentemente:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

---

# 46. DEBUG

Utilizado para diagnóstico detalhado em ambientes apropriados.

Não deverá produzir exposição de dados sensíveis.

Produção poderá reduzir ou limitar esse nível.

---

# 47. INFO

Utilizado para eventos normais relevantes.

Exemplos:

* task concluída;
* integração executada;
* serviço iniciado.

Não registrar todo detalhe de cada operação se isso gerar volume sem valor.

---

# 48. WARNING

Utilizado quando algo anormal ocorreu, mas o sistema conseguiu continuar.

Exemplos:

* tentativa negada recorrente;
* resposta inesperada tratada;
* configuração incompleta não crítica.

---

# 49. ERROR

Utilizado para falhas que impediram operação ou exigem investigação.

---

# 50. CRITICAL

Utilizado para situações graves com impacto amplo ou imediato.

Exemplos:

* perda de serviço crítico;
* indisponibilidade grave;
* falha de infraestrutura essencial.

O uso excessivo de `CRITICAL` reduz seu valor.

---

# 51. Escolha do Nível Correto

Níveis deverão refletir severidade real.

Anti-padrão:

```text
Toda exceção
=
CRITICAL
```

O nível deverá considerar impacto operacional.

---

# 52. Logs de Segurança

Logs de segurança poderão incluir:

* autenticação;
* autorização;
* tenant;
* tentativas anormais;
* alterações críticas;
* incidentes.

---

# 53. Logs de Aplicação

Logs de aplicação deverão apoiar:

* erros;
* regras;
* processamento;
* integrações;
* tarefas.

---

# 54. Logs de Infraestrutura

Podem incluir:

* deploy;
* runtime;
* banco;
* serviços;
* rede;
* cron jobs.

---

# 55. Logs de Integração

Deverão identificar:

* integração;
* operação;
* resultado;
* tempo;
* erro.

Sem registrar segredo ou payload confidencial completo.

---

# 56. Logs de Tasks

Tasks deverão produzir contexto suficiente para identificar:

* qual task;
* tenant;
* recurso;
* tentativa;
* resultado.

---

# 57. Logs Financeiros

Logs técnicos não deverão substituir auditoria financeira.

Dados financeiros deverão ser minimizados.

Preferir referências:

```text
lancamento_id=123
```

em vez de reproduzir todo o lançamento.

---

# 58. Logs Multi-Tenant

Logs de operações organizacionais deverão preservar identificação de tenant quando necessária.

Não misturar contextos de forma ambígua.

---

# 59. Dados que Não Devem ser Logados

Por padrão, não registrar:

```text
Senhas
Tokens
Secrets
Chaves privadas
Cookies completos
Credenciais
Dados confidenciais completos
```

---

# 60. Senhas

Senhas nunca deverão ser registradas.

Inclui:

* senha correta;
* senha incorreta;
* senha temporária.

---

# 61. Tokens

Tokens deverão ser tratados como secrets.

Não registrar integralmente:

* access tokens;
* refresh tokens;
* API keys;
* códigos temporários.

---

# 62. Secrets

Nenhum secret deverá ser inserido em log intencionalmente.

---

# 63. Dados Pessoais

Dados pessoais deverão ser minimizados.

Em vez de:

```text
nome completo
telefone
endereço
documento
```

preferir identificadores quando suficientes.

---

# 64. Dados Financeiros

Valores poderão ser registrados apenas quando necessários à finalidade de auditoria.

Logs técnicos deverão preferir IDs.

---

# 65. Payloads

Payloads completos não deverão ser logados indiscriminadamente.

Especial atenção a:

* APIs;
* webhooks;
* forms;
* comunicação;
* financeiro.

---

# 66. Headers

Não registrar indiscriminadamente:

```text
Authorization
Cookie
X-API-Key
```

ou outros headers confidenciais.

---

# 67. Cookies

Cookies completos não deverão aparecer em logs.

---

# 68. Arquivos

Conteúdo de arquivos não deverá ser colocado em logs.

Podem ser registrados:

* identificador;
* nome sanitizado;
* tamanho;
* resultado.

---

# 69. Sanitização de Logs

Quando entrada externa for usada em mensagem de log, deverá ser tratada de maneira adequada.

Evitar que conteúdo manipulado produza:

* quebra de estrutura;
* falsificação de linhas;
* dados inesperados.

---

# 70. Minimização

O log deverá conter somente o necessário para sua finalidade.

---

# 71. Estrutura e Padronização

Logs consistentes facilitam busca e correlação.

O projeto deverá evoluir para uma estrutura padronizada.

---

# 72. Logs Estruturados

Quando adequado, logs estruturados poderão possuir campos como:

```text
event
level
timestamp
user_id
tenant_id
resource
resource_id
request_id
result
```

A adoção deverá ser centralizada e não implementada de forma diferente por módulo.

---

# 73. Mensagens de Log

Mensagens deverão ser objetivas.

Preferir:

```text
Falha ao enviar comunicação.
```

com contexto estruturado.

Evitar:

```text
DEU RUIM
```

ou mensagens vagas.

---

# 74. Exceções

Exceções deverão ser registradas no nível adequado.

O log técnico poderá conter stack trace quando necessário para investigação e protegido adequadamente.

---

# 75. Stack Traces

Stack traces são úteis internamente, mas não deverão ser exibidos ao usuário final.

Também deverão ser protegidos de acesso público.

---

# 76. Contexto Técnico

Contexto deverá ser suficiente para investigar sem reproduzir dados confidenciais.

---

# 77. Tratamento de Erros

O fluxo esperado é:

```text
Erro
  ↓
Log técnico
  ↓
Resposta segura ao usuário
  ↓
Monitoramento quando relevante
```

---

# 78. Monitoramento de Disponibilidade

Deverá acompanhar serviços essenciais.

Exemplos:

* aplicação;
* banco;
* integrações críticas;
* cron jobs;
* serviços externos relevantes.

---

# 79. Monitoramento de Erros

Deverá permitir identificar:

* aumento de exceções;
* endpoint com falhas;
* task recorrente quebrada;
* integração indisponível.

---

# 80. Monitoramento de Performance

Indicadores poderão incluir:

* latência;
* tempo de query;
* duração de task;
* uso de recursos.

O detalhamento operacional poderá ser tratado pelo GOC.

---

# 81. Monitoramento de Segurança

Eventos de segurança deverão possuir monitoramento proporcional ao risco.

---

# 82. Monitoramento de Autenticação

Poderá acompanhar:

* falhas de login;
* frequência anormal;
* bloqueios;
* recuperação de acesso.

---

# 83. Monitoramento de Autorização

Repetidas tentativas negadas poderão indicar:

* configuração incorreta;
* automação quebrada;
* abuso;
* tentativa de exploração.

---

# 84. Monitoramento Multi-Tenant

Tentativas sistemáticas de acesso a diferentes tenants deverão receber atenção.

Exemplo:

```text
tenant 1 → denied
tenant 2 → denied
tenant 3 → denied
tenant 4 → denied
```

poderá indicar enumeração.

---

# 85. Monitoramento de APIs

Avaliar:

* status;
* latência;
* erros;
* rate limiting;
* volume;
* autenticação;
* autorização.

---

# 86. Monitoramento de Integrações

Integrações deverão possuir visibilidade de:

* indisponibilidade;
* timeout;
* autenticação inválida;
* erro de provedor;
* volume.

---

# 87. Monitoramento de Cron Jobs

Cron jobs deverão permitir saber:

```text
Executou?
Quando?
Terminou?
Falhou?
```

A ausência silenciosa de execução deverá ser detectável quando a rotina for crítica.

---

# 88. Monitoramento de Tasks

Tasks relevantes deverão permitir acompanhar:

* fila;
* falha;
* retry;
* duração;
* processamento.

---

# 89. Monitoramento de Comunicação

Rotinas de comunicação poderão acompanhar:

* envios;
* falhas;
* volume;
* erros de integração;
* duplicidade.

---

# 90. Monitoramento Financeiro

Monitoramento financeiro não deverá consistir em vigiar valores individuais indiscriminadamente.

O foco de segurança poderá incluir:

* falhas de operação;
* duplicidades;
* erros;
* operações críticas;
* mudanças administrativas.

---

# 91. Indicadores

Indicadores deverão possuir finalidade clara.

Exemplos:

```text
Taxa de erro
Falhas de login
Acessos negados
Tasks com falha
Integrações indisponíveis
```

---

# 92. Métricas

Métricas poderão alimentar dashboards técnicos do GOC.

Elas não deverão substituir logs e auditoria.

---

# 93. Alertas

Alertas deverão ser gerados somente quando houver necessidade de ação ou investigação.

---

# 94. Severidade de Alertas

Poderão existir categorias como:

```text
Informativo
Warning
High
Critical
```

A nomenclatura final deverá ser padronizada pelo GOC quando aplicável.

---

# 95. Alertas Acionáveis

Um bom alerta deverá informar:

```text
O que aconteceu?

Qual serviço?

Qual impacto?

Quando?

Qual ação inicial?
```

---

# 96. Ruído de Alertas

Alertas em excesso geram fadiga.

Se tudo alerta, nada alerta.

Os thresholds deverão evitar ruído desnecessário.

---

# 97. Thresholds

Limites deverão ser definidos com base em comportamento esperado.

Exemplo conceitual:

```text
N falhas de autenticação
em determinada janela
```

O valor exato deverá ser definido conforme operação e infraestrutura.

---

# 98. Detecção de Anomalias

Comportamentos anormais poderão ser detectados por:

* frequência;
* volume;
* origem;
* padrão;
* sequência;
* tenant.

Não deverá ser presumida a existência de plataforma avançada de detecção sem implementação correspondente.

---

# 99. Falhas Repetidas

Falhas repetidas poderão indicar problema sistêmico ou abuso.

---

# 100. Tentativas de Acesso Indevido

Eventos repetitivos de:

```text
403
404 em sequência
IDs diferentes
tenants diferentes
```

podem ser relevantes para investigação.

---

# 101. Enumeração

Tentativas sistemáticas de descoberta de recursos deverão ser monitoradas quando tecnicamente possível.

---

# 102. Brute Force

Tentativas repetidas de autenticação deverão ser tratadas em conjunto com o GAF.

---

# 103. Vazamento Multi-Tenant

Qualquer evidência de acesso entre tenants deverá possuir prioridade elevada.

Exemplo:

```text
Usuário da Igreja A
acessou recurso da Igreja B
```

deverá ser tratado como possível incidente.

---

# 104. Falhas de Integração

Integrações críticas não deverão falhar silenciosamente.

---

# 105. Falhas de Backup

Falha de backup deverá gerar visibilidade operacional.

Backup quebrado silenciosamente representa risco de continuidade.

---

# 106. Auditoria Funcional

Auditoria funcional registra ações relevantes de negócio.

Exemplos:

* alteração importante;
* exclusão;
* exportação;
* envio;
* configuração.

---

# 107. Auditoria de Segurança

Pode incluir:

* alteração de permissão;
* revogação;
* mudança de identidade;
* tentativa de acesso indevido;
* configuração de segurança.

---

# 108. Auditoria Administrativa

Ações realizadas por usuários privilegiados deverão possuir rastreabilidade proporcional ao risco.

---

# 109. Auditoria Financeira

O Financeiro deverá possuir rastreabilidade suficiente para operações críticas.

A auditoria deverá ser definida em conjunto com as regras de domínio financeiro.

---

# 110. Auditoria de Permissões

Alterações em:

* grupos;
* permissões;
* papéis;
* acesso administrativo;

deverão ser auditáveis.

---

# 111. Auditoria de Exportação

Exports contendo dados Restritos ou Confidenciais deverão ser avaliados para auditoria.

---

# 112. Auditoria de Integrações

Alterações de configuração, credencial, ativação e desativação de integrações poderão ser auditadas.

---

# 113. Imutabilidade

Registros de auditoria não deverão ser facilmente alteráveis por usuários comuns.

A estratégia técnica deverá ser proporcional ao risco.

---

# 114. Integridade dos Registros

A plataforma deverá evitar que uma operação auditada possa apagar silenciosamente a própria evidência.

---

# 115. Retenção

Logs e auditoria deverão possuir política de retenção.

A retenção deverá considerar:

* finalidade;
* volume;
* investigação;
* conformidade;
* custo;
* privacidade.

Não deverá existir retenção infinita por padrão.

---

# 116. Acesso aos Logs

Logs técnicos deverão ser acessíveis somente a pessoas ou sistemas autorizados.

---

# 117. Acesso aos Registros de Auditoria

Registros de auditoria poderão conter informações sensíveis.

O acesso deverá ser controlado.

---

# 118. Privacidade nos Logs

Logs também são dados.

Eles deverão seguir o GSF-08.

---

# 119. Multi-Tenant nos Logs

Logs centralizados poderão conter eventos de múltiplos tenants.

A visualização deverá evitar exposição cruzada quando usuários organizacionais tiverem acesso a registros.

---

# 120. Centralização

A plataforma deverá evoluir para centralizar logs e eventos quando isso trouxer benefício operacional.

Não deverá ser presumida a existência de solução centralizada específica sem implementação comprovada.

---

# 121. Produção

Produção deverá possuir logging adequado para diagnóstico e investigação.

Níveis excessivamente verbosos deverão ser avaliados.

---

# 122. Desenvolvimento

Desenvolvimento poderá utilizar logging mais detalhado.

Ainda assim, secrets não deverão ser logados.

---

# 123. Homologação

Homologação deverá reproduzir suficientemente os comportamentos de observabilidade de produção quando necessário para testes.

---

# 124. Django Logging

O GereIgreja deverá utilizar a infraestrutura de logging do Django e Python como base da aplicação.

A configuração deverá ser centralizada.

---

# 125. `logging` do Python

Código deverá preferir loggers apropriados em vez de `print()` para eventos operacionais.

Exemplo conceitual:

```python
import logging

logger = logging.getLogger(__name__)
```

A configuração final deverá seguir a infraestrutura oficial do backend.

---

# 126. Middlewares

Middlewares poderão adicionar contexto transversal, como:

* request ID;
* tenant;
* usuário;
* tempo de resposta.

A introdução de novos mecanismos deverá ser arquiteturalmente revisada.

---

# 127. Views

Views deverão registrar somente eventos relevantes.

Não adicionar log a cada linha de processamento.

---

# 128. Services

Services são pontos adequados para registrar eventos relevantes de domínio quando a operação realmente ocorrer nessa camada.

Exemplo:

```text
service de estorno
    ↓
operação concluída
    ↓
auditoria
```

Isso evita depender somente do frontend ou da view.

---

# 129. Selectors

Selectors geralmente não deverão gerar auditoria apenas por leitura normal.

Consultas excepcionalmente sensíveis poderão possuir regra específica.

---

# 130. Signals

Signals não deverão esconder auditoria crítica de forma difícil de compreender.

Se utilizados, deverão possuir testes e documentação.

---

# 131. Tasks

Tasks deverão possuir logging próprio e contexto de correlação quando aplicável.

---

# 132. APIs

APIs deverão seguir o GSF-07.

Eventos críticos via API deverão produzir rastreabilidade equivalente às operações pela interface.

---

# 133. HTMX

HTMX não muda os requisitos de logging ou auditoria.

A operação deverá ser registrada pela lógica backend correspondente.

---

# 134. Frontend

O frontend não deverá ser a fonte oficial de auditoria de operações críticas.

Eventos enviados pelo navegador podem ser manipulados.

Auditoria deverá ser produzida no backend.

---

# 135. JavaScript

Logs do navegador podem auxiliar diagnóstico, mas não substituem observabilidade do servidor.

Não utilizar `console.log()` com dados confidenciais.

---

# 136. Django Admin

Alterações relevantes via Admin deverão permanecer rastreáveis.

A infraestrutura nativa poderá ser complementada conforme a necessidade da plataforma.

---

# 137. Infraestrutura

Logs de infraestrutura deverão alimentar monitoramento e investigação.

---

# 138. Incidentes

Durante incidentes, logs e auditoria são fontes fundamentais de evidência.

---

# 139. Preservação de Evidências

Ao detectar incidente:

```text
Preservar
    ↓
Copiar ou proteger quando necessário
    ↓
Analisar
    ↓
Corrigir
```

Não apagar evidências relevantes durante tentativa de resolução.

---

# 140. Investigação

Uma investigação deverá poder reconstruir:

```text
Antes
  ↓
Evento inicial
  ↓
Eventos correlacionados
  ↓
Impacto
  ↓
Resposta
```

---

# 141. Correlação de Eventos

Eventos técnicos e funcionais deverão poder ser relacionados quando necessário.

---

# 142. Linha do Tempo

Incidentes relevantes deverão possuir linha do tempo baseada em evidências confiáveis.

---

# 143. Testes

Observabilidade deverá ser testada.

---

# 144. Testes de Logging

Verificar:

* evento produzido;
* nível correto;
* contexto;
* ausência de secret;
* ausência de dado indevido.

---

# 145. Testes de Auditoria

Testar operações críticas.

Exemplo:

```text
executar operação
    ↓
verificar registro de auditoria
```

---

# 146. Testes de Monitoramento

Quando alertas ou métricas forem automatizados, deverão possuir testes ou validações operacionais compatíveis.

---

# 147. Testes Multi-Tenant

Verificar que eventos identificam corretamente o tenant.

Também verificar que visualizações organizacionais não expõem eventos de outros tenants quando aplicável.

---

# 148. Testes de Privacidade

Buscar:

* tokens;
* senhas;
* secrets;
* documentos;
* payloads;
* cookies;

nos logs de testes e ambientes de validação.

---

# 149. Revisões Periódicas

A configuração de logging e monitoramento deverá ser revisada periodicamente.

Avaliar:

* eventos inúteis;
* ausência de eventos importantes;
* ruído;
* dados sensíveis;
* retenção;
* alertas obsoletos.

---

# 150. Evidências Arquiteturais

## EA-GSF-LOG-001

O GSF estabelece monitoramento contínuo de disponibilidade, falhas, tentativas de invasão, recursos e eventos críticos.

## EA-GSF-LOG-002

O GSF estabelece auditoria de login, logout, alterações de permissões, movimentações financeiras, exclusões, exportações e integrações.

## EA-GSF-LOG-003

O backend possui documentação específica de Logging.

## EA-GSF-LOG-004

O backend possui documentação de Exceptions.

## EA-GSF-LOG-005

O backend possui documentação de Tasks.

## EA-GSF-LOG-006

O backend possui documentação de Performance.

## EA-GSF-LOG-007

O GereIgreja possui arquitetura multi-tenant documentada.

## EA-GSF-LOG-008

O projeto possui módulos Financeiro e Comunicação com operações que exigem rastreabilidade elevada.

## EA-GSF-LOG-009

A governança possui documentação de auditoria e padrões de segurança.

## EA-GSF-LOG-010

O GereIgreja possui documentação operacional e de deploy que requer observabilidade para manutenção e resposta a falhas.

---

# 151. Especificações Oficiais

## GSF-LOG-001

Logging, monitoramento e auditoria deverão possuir responsabilidades claramente diferenciadas.

## GSF-LOG-002

Eventos relevantes deverão possuir timestamp.

## GSF-LOG-003

Eventos associados a usuários deverão registrar identidade adequada quando necessário.

## GSF-LOG-004

Eventos organizacionais deverão registrar tenant quando relevante.

## GSF-LOG-005

Operações críticas deverão possuir rastreabilidade proporcional ao risco.

## GSF-LOG-006

Senhas nunca deverão ser registradas.

## GSF-LOG-007

Tokens e secrets não deverão ser registrados integralmente.

## GSF-LOG-008

Payloads confidenciais não deverão ser registrados indiscriminadamente.

## GSF-LOG-009

Headers de autenticação não deverão ser registrados integralmente.

## GSF-LOG-010

Cookies completos não deverão ser registrados.

## GSF-LOG-011

Dados pessoais deverão ser minimizados nos logs.

## GSF-LOG-012

Logs financeiros deverão preferir identificadores a conteúdo integral.

## GSF-LOG-013

Exceções deverão ser registradas no nível apropriado.

## GSF-LOG-014

Stack traces não deverão ser exibidos ao usuário final.

## GSF-LOG-015

Logs deverão utilizar níveis consistentes.

## GSF-LOG-016

Eventos de alteração de permissões deverão ser auditáveis quando relevantes.

## GSF-LOG-017

Operações financeiras críticas deverão possuir auditoria.

## GSF-LOG-018

Exportações sensíveis deverão ser avaliadas para auditoria.

## GSF-LOG-019

Integrações críticas não deverão falhar silenciosamente.

## GSF-LOG-020

Cron jobs críticos deverão possuir execução observável.

## GSF-LOG-021

Tasks críticas deverão possuir logging de resultado.

## GSF-LOG-022

Tentativas anormais de acesso multi-tenant deverão ser monitoráveis.

## GSF-LOG-023

Falhas de backup deverão possuir visibilidade operacional.

## GSF-LOG-024

Alertas deverão ser acionáveis.

## GSF-LOG-025

Alertas excessivamente ruidosos deverão ser revisados.

## GSF-LOG-026

Auditoria crítica deverá ser produzida no backend.

## GSF-LOG-027

Frontend não deverá ser considerado fonte confiável de auditoria.

## GSF-LOG-028

Registros de auditoria não deverão ser facilmente alteráveis por usuários comuns.

## GSF-LOG-029

Logs deverão possuir política de retenção.

## GSF-LOG-030

Acesso a logs e auditoria deverá ser restrito.

## GSF-LOG-031

Logs deverão seguir os requisitos de privacidade do GSF-08.

## GSF-LOG-032

Incidentes deverão preservar evidências relevantes.

## GSF-LOG-033

A plataforma deverá avaliar adoção de request ID para correlação de eventos.

## GSF-LOG-034

Logs estruturados deverão ser padronizados antes da adoção transversal.

## GSF-LOG-035

Revisões periódicas deverão identificar eventos inúteis, ausentes ou inseguros.

---

# 152. Anti-Padrões

São considerados anti-padrões:

```text
print("erro")
```

como mecanismo oficial de observabilidade.

---

```python
logger.info(f"Senha informada: {senha}")
```

---

```python
logger.debug(token)
```

---

```text
Logar request.POST inteiro
```

sem análise.

---

```text
Logar header Authorization
```

integralmente.

---

```text
Toda exceção
=
CRITICAL
```

---

```text
Toda operação
=
INFO
```

gerando volume sem valor.

---

```text
Erro crítico
=
nenhum alerta
```

---

```text
Alerta
a cada acesso negado normal
```

---

```text
Auditoria produzida
somente pelo JavaScript
```

---

```text
Usuário excluído
    ↓
todos os registros históricos
perdem referência de identidade
```

---

```text
Tenant ausente do log
em operação organizacional crítica
```

---

```text
Integração falha diariamente
sem qualquer visibilidade
```

---

```text
Cron job não executou
e ninguém consegue detectar
```

---

```text
Backup falha
silenciosamente
```

---

```text
Durante incidente:
apagar logs para liberar espaço
```

sem preservação das evidências.

---

# 153. Checklist

## Logging

* [ ] logger adequado utilizado;
* [ ] nível correto;
* [ ] mensagem clara;
* [ ] contexto suficiente;
* [ ] sem senha;
* [ ] sem token;
* [ ] sem secret;
* [ ] sem payload confidencial completo.

## Identidade

* [ ] usuário registrado quando necessário;
* [ ] identidade técnica registrada quando aplicável;
* [ ] ações históricas permanecem rastreáveis.

## Multi-Tenant

* [ ] tenant registrado quando relevante;
* [ ] sem exposição cruzada;
* [ ] tentativas anormais detectáveis.

## Auditoria

* [ ] login avaliado;
* [ ] logout avaliado;
* [ ] permissões;
* [ ] grupos;
* [ ] financeiro;
* [ ] exclusões;
* [ ] exportações;
* [ ] integrações;
* [ ] administração.

## Financeiro

* [ ] operações críticas rastreáveis;
* [ ] IDs utilizados;
* [ ] valores minimizados;
* [ ] tenant;
* [ ] resultado.

## Integrações

* [ ] início e resultado;
* [ ] timeout;
* [ ] falha;
* [ ] tenant;
* [ ] sem credenciais;
* [ ] correlation ID avaliado.

## Tasks

* [ ] identificação da task;
* [ ] tenant;
* [ ] recurso;
* [ ] resultado;
* [ ] falha;
* [ ] retry quando aplicável.

## Cron Jobs

* [ ] execução detectável;
* [ ] falha detectável;
* [ ] horário;
* [ ] resultado;
* [ ] alerta para falha crítica.

## Monitoramento

* [ ] disponibilidade;
* [ ] erros;
* [ ] APIs;
* [ ] integrações;
* [ ] tasks;
* [ ] cron;
* [ ] banco;
* [ ] segurança.

## Alertas

* [ ] acionável;
* [ ] severidade correta;
* [ ] baixo ruído;
* [ ] sem dados sensíveis;
* [ ] responsável ou destino definido.

## Retenção

* [ ] política definida;
* [ ] volume avaliado;
* [ ] privacidade;
* [ ] conformidade;
* [ ] acesso restrito.

## Incidentes

* [ ] logs preserváveis;
* [ ] auditoria disponível;
* [ ] timestamps consistentes;
* [ ] correlação possível;
* [ ] evidências não destruídas.

## Testes

* [ ] evento registrado;
* [ ] nível;
* [ ] tenant;
* [ ] identidade;
* [ ] ausência de secrets;
* [ ] operação crítica;
* [ ] regressão.

---

# 154. Documentos Relacionados

## Frameworks

* GSF — GereIgreja Security Framework
* GAF — GereIgreja Authentication Framework
* GQF — GereIgreja Quality Framework
* GOC — GereIgreja Operations Center

## Segurança

* GSF-01 — Fundamentos de Segurança
* GSF-03 — Gestão de Identidade
* GSF-04 — Autorização e Controle de Acesso
* GSF-05 — Segurança Multi-Tenant
* GSF-07 — Segurança das APIs
* GSF-08 — Segurança de Dados e Privacidade
* GSF-09 — Segurança de Infraestrutura e Segredos
* GSF-11 — Backup, Continuidade e Recuperação
* GSF-12 — Gestão de Vulnerabilidades
* GSF-13 — Gestão de Incidentes de Segurança
* GSF-15 — Secure Development Lifecycle

## Backend

* 14 — Tasks
* 15 — Cache
* 16 — Logging
* 17 — Exceptions
* 18 — Testing
* 19 — Performance

## Governança

* Padrões de Permissões
* Padrões de Segurança
* Padrões de Testes
* Checklist de Release
* Auditoria 360 do GereIgreja

## Operações

* documentação existente em `docs/operacoes/`
* documentação de deploy
* documentação de automações
* documentação de cron jobs

---

# 155. Princípios Finais

Logging, monitoramento e auditoria deverão permitir que a Engenharia responda:

```text
O sistema está funcionando?

Algo anormal está acontecendo?

Quem executou esta operação?

Em qual tenant?

Qual recurso foi afetado?

O que aconteceu antes?

O que aconteceu depois?

Qual foi o impacto?
```

O GereIgreja deverá evitar dois extremos:

```text
Registrar quase nada
```

e:

```text
Registrar tudo
```

O primeiro impede investigação.

O segundo cria ruído, custo e risco de vazamento.

A estratégia correta é:

```text
Registrar o necessário
+
Estruturar corretamente
+
Monitorar o relevante
+
Alertar o acionável
+
Auditar o crítico
+
Proteger os próprios registros
```

Logs deverão ajudar a encontrar problemas.

Monitoramento deverá ajudar a perceber problemas.

Auditoria deverá ajudar a provar e reconstruir eventos.

Nenhum desses mecanismos deverá expor secrets ou dados confidenciais desnecessariamente.

A regra final é:

```text
Se uma operação é crítica
o suficiente para exigir controle,
ela também deve ser observável
o suficiente para ser investigada.
```

---

# 156. Status do Documento

**Pasta**

`docs/seguranca/`

**Arquivo**

`10-Logging-Monitoramento-e-Auditoria.md`

**Documento**

`GSF-10`

**Código**

`GSF-LOGGING-MONITORING-AUDIT`

**Framework**

`GSF — GereIgreja Security Framework`

**Versão**

`1.0`

**Status**

`OFICIAL`

**Responsável**

`Equipe de Engenharia`

**Última atualização**

`Agosto de 2026`

**Próximo documento**

`11-Backup-Continuidade-e-Recuperacao.md`

**Código do próximo documento**

`GSF-11`

```
```
