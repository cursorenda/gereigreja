Pasta:

docs/infraestrutura/

Arquivo:

10-Observabilidade-Logs-Metricas-e-Alertas.md

Documento:

GINF-10

Código:

GINF-OBSERVABILITY-LOGS-METRICS-ALERTS

Família:

GINF --- GereIgreja Infrastructure Engineering

Frameworks relacionados:

GEA --- GereIgreja Enterprise Architecture GSF --- GereIgreja Security
Framework GOC --- GereIgreja Operations Center GQF --- GereIgreja
Quality Framework GAPI --- GereIgreja API Engineering GereIgreja Backend
Engineering

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GINF-10 --- Observabilidade, Logs, Métricas e Alertas

> "Uma plataforma que não consegue explicar seu próprio estado não pode
> ser operada com segurança."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com a Arquitetura
4.  Princípios Fundamentais
5.  Observabilidade
6.  Monitoramento
7.  Telemetria
8.  Pilares
9.  Contexto Operacional
10. Ambientes
11. Serviços
12. Releases
13. Multi-Tenant
14. Correlação
15. Request ID
16. Trace ID
17. Task ID
18. Logs
19. Logs Estruturados
20. Campos Padronizados
21. Níveis de Log
22. DEBUG
23. INFO
24. WARNING
25. ERROR
26. CRITICAL
27. Conteúdo de Logs
28. Dados Sensíveis
29. Secrets
30. PII
31. Payloads
32. Exceções
33. Stack Traces
34. Logs HTTP
35. Logs de Aplicação
36. Logs de Workers
37. Logs de Banco
38. Logs de Redis
39. Logs de Proxy
40. Logs de Infraestrutura
41. Auditoria
42. Logs versus Auditoria
43. Retenção de Logs
44. Centralização
45. Busca
46. Métricas
47. Tipos de Métricas
48. Contadores
49. Gauges
50. Histogramas
51. Métricas RED
52. Métricas USE
53. Métricas Web
54. Métricas de Workers
55. Métricas de Filas
56. Métricas de Banco
57. Métricas Redis
58. Métricas de Storage
59. Métricas de Containers
60. Métricas de Rede
61. Métricas de Negócio
62. Cardinalidade
63. Labels
64. Tenant em Métricas
65. Dashboards
66. Dashboard de Plataforma
67. Dashboard de Aplicação
68. Dashboard de Banco
69. Dashboard de Filas
70. Dashboard de Deploy
71. Alertas
72. Princípios de Alertas
73. Severidade
74. Sinais de Usuário
75. Alertas de Disponibilidade
76. Alertas de Latência
77. Alertas de Erro
78. Alertas de Saturação
79. Alertas de Filas
80. Alertas de Banco
81. Alertas de Redis
82. Alertas de Storage
83. Alertas de Segurança
84. Alertas de Backup
85. Ruído
86. Deduplicação
87. Agrupamento
88. Escalonamento
89. Runbooks
90. SLO
91. SLI
92. Error Budget
93. Tracing
94. Distributed Tracing
95. Integrações Externas
96. Deploy e Observabilidade
97. Marcadores de Release
98. Incidentes
99. Evidências
100. Health Checks
101. Synthetic Monitoring
102. Disponibilidade Externa
103. Performance
104. Capacidade
105. Custos
106. Retenção
107. Segurança da Telemetria
108. Acesso
109. Integridade
110. Continuidade da Observabilidade
111. Falha do Sistema de Logs
112. Testes
113. Desenvolvimento
114. Staging
115. Produção
116. Anti-Padrões
117. Arquitetura de Referência
118. Checklist
119. Documentos Relacionados
120. Princípios Finais
121. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece o padrão oficial de observabilidade da
infraestrutura do GereIgreja.

Seu objetivo é garantir que a equipe consiga:

-   detectar falhas;
-   compreender comportamento;
-   correlacionar eventos;
-   diagnosticar incidentes;
-   acompanhar capacidade;
-   avaliar releases;
-   preservar evidências;
-   agir antes que problemas se tornem indisponibilidades graves.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   aplicação Django;
-   APIs;
-   workers;
-   filas;
-   banco;
-   Redis;
-   storage;
-   containers;
-   proxy;
-   rede;
-   integrações;
-   pipelines e deploys;
-   infraestrutura operacional.

------------------------------------------------------------------------

# 3. Relação com a Arquitetura

``` text
Usuário
   │
   ▼
Proxy
   │
   ▼
Django
   │
   ├──► PostgreSQL
   ├──► Redis
   ├──► Storage
   └──► Workers / Integrações

        │
        ▼
┌─────────────────────────────┐
│      OBSERVABILIDADE        │
│ Logs | Métricas | Traces    │
│ Dashboards | Alertas        │
└─────────────────────────────┘
```

A observabilidade é transversal.

------------------------------------------------------------------------

# 4. Princípios Fundamentais

Aplicar:

-   telemetria por padrão;
-   correlação;
-   logs estruturados;
-   métricas úteis;
-   alertas acionáveis;
-   mínimo dado sensível;
-   contexto de release;
-   retenção definida;
-   acesso controlado.

------------------------------------------------------------------------

# 5. Observabilidade

Observabilidade é a capacidade de inferir o estado interno da plataforma
a partir de sinais externos.

Não se limita a "ter logs".

------------------------------------------------------------------------

# 6. Monitoramento

Monitoramento verifica condições conhecidas.

Exemplo:

``` text
CPU > limite
fila acumulada
taxa de erro elevada
```

Observabilidade também ajuda a investigar condições não previstas.

------------------------------------------------------------------------

# 7. Telemetria

Telemetria inclui:

-   logs;
-   métricas;
-   traces;
-   eventos;
-   health checks.

------------------------------------------------------------------------

# 8. Pilares

Modelo principal:

``` text
Logs
+
Métricas
+
Tracing
```

com:

``` text
Alertas
+
Dashboards
+
Runbooks
```

------------------------------------------------------------------------

# 9. Contexto Operacional

Todo sinal deverá carregar contexto suficiente para identificar sua
origem.

------------------------------------------------------------------------

# 10. Ambientes

Telemetria deverá identificar:

``` text
development
staging
production
```

Nunca misturar ambientes sem capacidade clara de filtragem.

------------------------------------------------------------------------

# 11. Serviços

Identificar componente:

``` text
web
worker
scheduler
database
redis
proxy
```

------------------------------------------------------------------------

# 12. Releases

Logs e métricas deverão permitir identificar release quando tecnicamente
possível.

------------------------------------------------------------------------

# 13. Multi-Tenant

Tenant poderá ser incluído em logs operacionais quando necessário e
permitido.

Deverá ser utilizado identificador interno, evitando nome, CNPJ ou outro
dado pessoal/desnecessário.

------------------------------------------------------------------------

# 14. Correlação

Uma operação deverá ser rastreável entre componentes.

``` text
request
→ service
→ task
→ integração
```

------------------------------------------------------------------------

# 15. Request ID

Cada request deverá possuir identificador de correlação.

Quando recebido de fonte não confiável, deverá ser validado ou
substituído conforme implementação.

------------------------------------------------------------------------

# 16. Trace ID

Quando tracing distribuído for adotado, trace ID deverá conectar spans
da mesma operação.

------------------------------------------------------------------------

# 17. Task ID

Workers deverão registrar task/job ID.

Quando uma task nasce de request, preservar correlação quando possível.

------------------------------------------------------------------------

# 18. Logs

Logs são registros de eventos operacionais.

Deverão ser úteis para investigação e não simples despejo de texto.

------------------------------------------------------------------------

# 19. Logs Estruturados

Produção deverá preferir formato estruturado.

Exemplo conceitual:

``` json
{
  "level": "INFO",
  "service": "web",
  "request_id": "...",
  "event": "member.updated",
  "duration_ms": 42
}
```

------------------------------------------------------------------------

# 20. Campos Padronizados

Campos recomendados:

-   timestamp;
-   level;
-   environment;
-   service;
-   release;
-   event;
-   request_id;
-   trace_id;
-   task_id;
-   tenant_id quando permitido;
-   duration_ms;
-   result.

Nem todos são obrigatórios em todos os eventos.

------------------------------------------------------------------------

# 21. Níveis de Log

Os níveis deverão possuir semântica consistente.

------------------------------------------------------------------------

# 22. DEBUG

Detalhes de diagnóstico.

Produção deverá evitar DEBUG contínuo sem necessidade.

------------------------------------------------------------------------

# 23. INFO

Eventos normais relevantes.

Não registrar cada linha executada como INFO.

------------------------------------------------------------------------

# 24. WARNING

Condição anormal recuperável que merece atenção.

------------------------------------------------------------------------

# 25. ERROR

Falha de operação ou componente que exige investigação.

------------------------------------------------------------------------

# 26. CRITICAL

Falha grave com impacto amplo ou risco imediato.

Uso deverá ser raro.

------------------------------------------------------------------------

# 27. Conteúdo de Logs

Registrar:

``` text
o que ocorreu
onde
quando
resultado
contexto técnico necessário
```

Evitar conteúdo irrelevante.

------------------------------------------------------------------------

# 28. Dados Sensíveis

Logs não são repositório de dados de negócio.

Nunca registrar informação sensível sem necessidade e autorização
explícita.

------------------------------------------------------------------------

# 29. Secrets

Proibido registrar:

-   senhas;
-   tokens;
-   API keys;
-   private keys;
-   cookies de autenticação;
-   connection strings com credenciais.

------------------------------------------------------------------------

# 30. PII

Dados pessoais deverão ser minimizados.

Preferir IDs internos.

------------------------------------------------------------------------

# 31. Payloads

Não logar request/response bodies integralmente por padrão.

Payload pode conter:

-   dados pessoais;
-   financeiros;
-   ministeriais;
-   secrets.

------------------------------------------------------------------------

# 32. Exceções

Exceções deverão produzir contexto suficiente para diagnóstico sem expor
informação sensível.

------------------------------------------------------------------------

# 33. Stack Traces

Stack traces são úteis em logs internos de erro.

Não deverão ser apresentados integralmente ao usuário final.

------------------------------------------------------------------------

# 34. Logs HTTP

Podem registrar:

-   método;
-   path normalizado;
-   status;
-   duração;
-   request ID.

Evitar query strings sensíveis.

------------------------------------------------------------------------

# 35. Logs de Aplicação

Eventos importantes deverão utilizar nomes consistentes.

Exemplo:

``` text
auth.login.failed
integration.timeout
report.generated
```

------------------------------------------------------------------------

# 36. Logs de Workers

Registrar:

-   task;
-   fila;
-   tentativa;
-   duração;
-   resultado;
-   erro.

------------------------------------------------------------------------

# 37. Logs de Banco

Utilizar para:

-   erros;
-   conexões;
-   queries lentas;
-   manutenção.

Não habilitar logging indiscriminado de todas as queries em produção sem
avaliação.

------------------------------------------------------------------------

# 38. Logs de Redis

Monitorar:

-   conexão;
-   timeout;
-   memória;
-   falhas;
-   eventos operacionais relevantes.

------------------------------------------------------------------------

# 39. Logs de Proxy

Proxy deverá ajudar a diagnosticar:

-   requests;
-   status;
-   latência;
-   TLS;
-   upstream failures.

------------------------------------------------------------------------

# 40. Logs de Infraestrutura

Infraestrutura deverá produzir registros de:

-   deploy;
-   restart;
-   scaling;
-   health failure;
-   alterações operacionais.

------------------------------------------------------------------------

# 41. Auditoria

Auditoria registra eventos que precisam de rastreabilidade formal.

Exemplos:

-   alteração de permissão;
-   exportação sensível;
-   movimentação financeira;
-   exclusão relevante.

------------------------------------------------------------------------

# 42. Logs versus Auditoria

``` text
Log operacional
→ diagnóstico

Audit log
→ rastreabilidade de ação
```

Um não substitui automaticamente o outro.

------------------------------------------------------------------------

# 43. Retenção de Logs

Retenção deverá ser definida por:

-   finalidade;
-   custo;
-   investigação;
-   segurança;
-   conformidade.

------------------------------------------------------------------------

# 44. Centralização

Produção deverá centralizar logs.

Não depender de acessar individualmente containers efêmeros.

------------------------------------------------------------------------

# 45. Busca

A plataforma de logs deverá permitir busca por:

-   período;
-   serviço;
-   release;
-   request ID;
-   task ID;
-   nível;
-   evento.

------------------------------------------------------------------------

# 46. Métricas

Métricas representam comportamento agregado ao longo do tempo.

------------------------------------------------------------------------

# 47. Tipos de Métricas

Utilizar tipos adequados à ferramenta adotada.

------------------------------------------------------------------------

# 48. Contadores

Exemplos:

``` text
requests_total
tasks_failed_total
```

------------------------------------------------------------------------

# 49. Gauges

Exemplos:

``` text
queue_depth
active_connections
```

------------------------------------------------------------------------

# 50. Histogramas

Úteis para distribuições como:

``` text
request_duration
task_duration
```

------------------------------------------------------------------------

# 51. Métricas RED

Para serviços:

``` text
Rate
Errors
Duration
```

------------------------------------------------------------------------

# 52. Métricas USE

Para recursos:

``` text
Utilization
Saturation
Errors
```

------------------------------------------------------------------------

# 53. Métricas Web

Monitorar:

-   requests;
-   status;
-   latência;
-   erros;
-   throughput.

------------------------------------------------------------------------

# 54. Métricas de Workers

Monitorar:

-   tasks processadas;
-   falhas;
-   retries;
-   duração;
-   workers ativos.

------------------------------------------------------------------------

# 55. Métricas de Filas

Monitorar:

-   depth;
-   age;
-   throughput;
-   falhas;
-   retries.

------------------------------------------------------------------------

# 56. Métricas de Banco

Monitorar:

-   conexões;
-   CPU;
-   I/O;
-   locks;
-   latência;
-   disco;
-   queries lentas.

------------------------------------------------------------------------

# 57. Métricas Redis

Monitorar:

-   memória;
-   conexões;
-   evictions;
-   hits/misses;
-   latência.

------------------------------------------------------------------------

# 58. Métricas de Storage

Monitorar:

-   uso;
-   operações;
-   erros;
-   latência;
-   crescimento.

------------------------------------------------------------------------

# 59. Métricas de Containers

Monitorar:

-   CPU;
-   memória;
-   OOM;
-   restarts;
-   health.

------------------------------------------------------------------------

# 60. Métricas de Rede

Monitorar quando disponível:

-   latência;
-   erros;
-   conexões;
-   tráfego;
-   falhas de upstream.

------------------------------------------------------------------------

# 61. Métricas de Negócio

Métricas técnicas poderão ser complementadas por sinais de negócio.

Exemplo:

``` text
exports concluídas
integrações processadas
```

Evitar labels com dados pessoais.

------------------------------------------------------------------------

# 62. Cardinalidade

Alta cardinalidade pode tornar métricas caras e inutilizáveis.

Evitar labels como:

``` text
request_id
user_id
email
```

em séries métricas.

------------------------------------------------------------------------

# 63. Labels

Labels deverão possuir conjunto limitado e previsível.

------------------------------------------------------------------------

# 64. Tenant em Métricas

Evitar `tenant_id` como label global de métricas se houver grande
quantidade de igrejas.

Investigações específicas poderão utilizar logs.

------------------------------------------------------------------------

# 65. Dashboards

Dashboards deverão responder perguntas operacionais.

Não criar gráficos sem finalidade.

------------------------------------------------------------------------

# 66. Dashboard de Plataforma

Deverá resumir:

-   disponibilidade;
-   erros;
-   latência;
-   capacidade;
-   dependências.

------------------------------------------------------------------------

# 67. Dashboard de Aplicação

Incluir:

-   throughput;
-   status;
-   latência;
-   erros;
-   releases.

------------------------------------------------------------------------

# 68. Dashboard de Banco

Incluir:

-   conexões;
-   CPU;
-   disco;
-   locks;
-   queries;
-   latência.

------------------------------------------------------------------------

# 69. Dashboard de Filas

Incluir:

-   depth;
-   age;
-   throughput;
-   failures;
-   retries.

------------------------------------------------------------------------

# 70. Dashboard de Deploy

Permitir correlacionar releases com comportamento da plataforma.

------------------------------------------------------------------------

# 71. Alertas

Alertas deverão existir para condições que exigem ação.

------------------------------------------------------------------------

# 72. Princípios de Alertas

Todo alerta deverá responder:

``` text
o que aconteceu?
qual impacto?
quem deve agir?
qual primeiro passo?
```

------------------------------------------------------------------------

# 73. Severidade

Exemplo conceitual:

``` text
SEV1 — indisponibilidade/risco crítico
SEV2 — degradação relevante
SEV3 — problema operacional
SEV4 — aviso/tendência
```

A taxonomia oficial poderá ser refinada pelo GOC.

------------------------------------------------------------------------

# 74. Sinais de Usuário

Priorizar alertas que representem impacto real.

Exemplo:

``` text
taxa de 5xx
```

pode ser mais relevante que CPU alta isoladamente.

------------------------------------------------------------------------

# 75. Alertas de Disponibilidade

Alertar quando serviço essencial não estiver acessível.

------------------------------------------------------------------------

# 76. Alertas de Latência

Alertar quando latência exceder limite sustentado relevante.

------------------------------------------------------------------------

# 77. Alertas de Erro

Taxas anormais de erro deverão gerar sinal.

------------------------------------------------------------------------

# 78. Alertas de Saturação

Monitorar:

-   CPU;
-   memória;
-   conexões;
-   disco;
-   workers.

------------------------------------------------------------------------

# 79. Alertas de Filas

Alertar para:

-   depth excessivo;
-   age excessiva;
-   workers ausentes;
-   falhas crescentes.

------------------------------------------------------------------------

# 80. Alertas de Banco

Alertar para:

-   conexões próximas ao limite;
-   disco;
-   locks prolongados;
-   indisponibilidade;
-   replication lag quando aplicável.

------------------------------------------------------------------------

# 81. Alertas de Redis

Alertar para:

-   memória crítica;
-   evictions inesperadas;
-   indisponibilidade;
-   latência elevada.

------------------------------------------------------------------------

# 82. Alertas de Storage

Alertar para erros relevantes e falhas de acesso.

------------------------------------------------------------------------

# 83. Alertas de Segurança

Eventos de segurança deverão integrar o processo do GSF e GOC.

------------------------------------------------------------------------

# 84. Alertas de Backup

Backup crítico falhou:

``` text
deve gerar alerta
```

Não descobrir falha apenas durante restauração.

------------------------------------------------------------------------

# 85. Ruído

Alerta excessivo reduz confiança.

Alertas sem ação deverão ser removidos, ajustados ou convertidos em
dashboard.

------------------------------------------------------------------------

# 86. Deduplicação

Eventos repetidos deverão ser agrupados quando possível.

------------------------------------------------------------------------

# 87. Agrupamento

Alertas relacionados ao mesmo incidente deverão evitar múltiplas
notificações desnecessárias.

------------------------------------------------------------------------

# 88. Escalonamento

Incidentes críticos deverão possuir caminho de escalonamento definido
pelo GOC.

------------------------------------------------------------------------

# 89. Runbooks

Alertas importantes deverão apontar para runbook quando disponível.

Runbook deve explicar primeiros passos de diagnóstico e recuperação.

------------------------------------------------------------------------

# 90. SLO

Service Level Objectives deverão ser definidos para serviços críticos
conforme maturidade operacional.

------------------------------------------------------------------------

# 91. SLI

SLIs são medidas utilizadas para avaliar objetivos.

Exemplos:

-   disponibilidade;
-   latência;
-   taxa de sucesso.

------------------------------------------------------------------------

# 92. Error Budget

Error budget poderá orientar equilíbrio entre confiabilidade e
velocidade de mudança.

Sua adoção deverá acompanhar maturidade do GOC.

------------------------------------------------------------------------

# 93. Tracing

Tracing deverá ser adotado quando ajudar a compreender operações
distribuídas.

Não é obrigatório instrumentar tudo desde o primeiro momento.

------------------------------------------------------------------------

# 94. Distributed Tracing

Fluxos relevantes:

``` text
HTTP
→ Django
→ Worker
→ Integração
```

deverão preservar contexto quando a tecnologia permitir.

------------------------------------------------------------------------

# 95. Integrações Externas

Monitorar:

-   latência;
-   status;
-   timeout;
-   retries;
-   circuit state quando aplicável.

------------------------------------------------------------------------

# 96. Deploy e Observabilidade

Todo deploy deverá ser visível na plataforma de observabilidade.

Aplicar GINF-09.

------------------------------------------------------------------------

# 97. Marcadores de Release

Dashboards deverão permitir visualizar quando uma nova release entrou.

------------------------------------------------------------------------

# 98. Incidentes

Durante incidente, observabilidade deverá fornecer evidências para:

``` text
detectar
→ classificar
→ diagnosticar
→ conter
→ recuperar
```

------------------------------------------------------------------------

# 99. Evidências

Logs relevantes poderão compor investigação de incidentes.

Preservação deverá seguir política de segurança e retenção.

------------------------------------------------------------------------

# 100. Health Checks

Health checks deverão ser simples e significativos.

Não executar consultas extremamente pesadas em cada probe.

------------------------------------------------------------------------

# 101. Synthetic Monitoring

Testes sintéticos poderão verificar fluxos essenciais externamente.

Exemplo:

``` text
DNS
→ HTTPS
→ aplicação
→ resposta
```

------------------------------------------------------------------------

# 102. Disponibilidade Externa

Monitoramento somente interno não detecta todos os problemas.

Produção deverá evoluir para possuir visão externa de disponibilidade.

------------------------------------------------------------------------

# 103. Performance

Observabilidade deverá permitir detectar regressões após mudanças.

------------------------------------------------------------------------

# 104. Capacidade

Tendências deverão apoiar planejamento.

Exemplos:

-   crescimento de disco;
-   memória Redis;
-   conexões;
-   filas;
-   storage.

------------------------------------------------------------------------

# 105. Custos

Telemetria possui custo.

Controlar:

-   volume de logs;
-   retenção;
-   cardinalidade;
-   sampling de traces.

Nunca reduzir sinais críticos apenas sem análise.

------------------------------------------------------------------------

# 106. Retenção

Cada tipo de telemetria poderá possuir retenção diferente.

------------------------------------------------------------------------

# 107. Segurança da Telemetria

Sistemas de observabilidade contêm informação interna sensível.

Devem possuir:

-   autenticação;
-   autorização;
-   rede adequada;
-   auditoria quando disponível.

------------------------------------------------------------------------

# 108. Acesso

Acesso deverá seguir menor privilégio.

Nem todo usuário precisa visualizar logs completos de produção.

------------------------------------------------------------------------

# 109. Integridade

Telemetria crítica não deverá ser facilmente alterável por usuários
comuns da aplicação.

------------------------------------------------------------------------

# 110. Continuidade da Observabilidade

A falha da observabilidade não deverá necessariamente derrubar a
aplicação.

Porém, deverá ser detectável.

------------------------------------------------------------------------

# 111. Falha do Sistema de Logs

Aplicação não deverá bloquear indefinidamente porque o coletor de logs
está indisponível.

Buffers e políticas deverão evitar consumo ilimitado de disco/memória.

------------------------------------------------------------------------

# 112. Testes

Testar:

-   emissão de logs;
-   correlação;
-   métricas;
-   alertas;
-   dashboards críticos;
-   health checks;
-   ausência de secrets.

------------------------------------------------------------------------

# 113. Desenvolvimento

Development deverá permitir logs legíveis e debugging.

Formato poderá ser mais amigável ao humano.

------------------------------------------------------------------------

# 114. Staging

Staging deverá validar a instrumentação que irá para produção.

------------------------------------------------------------------------

# 115. Produção

Produção deverá possuir:

-   logs centralizados;
-   métricas;
-   dashboards;
-   alertas;
-   retenção;
-   controle de acesso;
-   contexto de release.

------------------------------------------------------------------------

# 116. Anti-Padrões

Evitar:

``` text
print()
como estratégia
de observabilidade
```

------------------------------------------------------------------------

``` text
senha/token
em log
```

------------------------------------------------------------------------

``` text
request body completo
por padrão
```

------------------------------------------------------------------------

``` text
alerta para tudo
```

------------------------------------------------------------------------

``` text
dashboard
sem pergunta operacional
```

------------------------------------------------------------------------

``` text
request_id
como label de métrica
```

------------------------------------------------------------------------

``` text
tenant_id de milhares de tenants
como label global
```

------------------------------------------------------------------------

``` text
container
como única fonte
de logs históricos
```

------------------------------------------------------------------------

``` text
backup falha
sem alerta
```

------------------------------------------------------------------------

# 117. Arquitetura de Referência

``` text
                  USERS / CLIENTS
                        │
                        ▼
                      PROXY
                        │
                        ▼
                   DJANGO WEB
                   │    │    │
                   │    │    └────► STORAGE
                   │    └─────────► REDIS
                   └──────────────► DATABASE
                        │
                        ▼
                     WORKERS
                        │
                        ▼
                  INTEGRATIONS

Todos os componentes
        │
        ├────────► LOGS
        ├────────► METRICS
        └────────► TRACES
                      │
                      ▼
              OBSERVABILITY PLATFORM
               │        │        │
               ▼        ▼        ▼
           DASHBOARDS  ALERTS   SEARCH
                         │
                         ▼
                    GOC / INCIDENT
```

------------------------------------------------------------------------

# 118. Checklist

## Contexto

-   [ ] environment;
-   [ ] service;
-   [ ] release;
-   [ ] request ID;
-   [ ] task ID quando aplicável.

## Logs

-   [ ] estruturados em produção;
-   [ ] centralizados;
-   [ ] níveis consistentes;
-   [ ] sem secrets;
-   [ ] PII minimizada;
-   [ ] retenção definida.

## Métricas

-   [ ] web;
-   [ ] workers;
-   [ ] filas;
-   [ ] banco;
-   [ ] Redis;
-   [ ] containers;
-   [ ] storage;
-   [ ] cardinalidade controlada.

## Dashboards

-   [ ] plataforma;
-   [ ] aplicação;
-   [ ] banco;
-   [ ] filas;
-   [ ] releases visíveis.

## Alertas

-   [ ] disponibilidade;
-   [ ] erros;
-   [ ] latência;
-   [ ] saturação;
-   [ ] filas;
-   [ ] banco;
-   [ ] backup;
-   [ ] runbooks para alertas críticos.

## Segurança

-   [ ] acesso restrito;
-   [ ] secrets mascarados;
-   [ ] payloads controlados;
-   [ ] retenção adequada;
-   [ ] auditoria separada quando necessário.

------------------------------------------------------------------------

# 119. Documentos Relacionados

-   GINF-01 --- Arquitetura da Infraestrutura
-   GINF-02 --- Ambientes e Configuração
-   GINF-03 --- Rede, DNS, Proxy e TLS
-   GINF-04 --- Runtime Django e Workers
-   GINF-05 --- Banco de Dados e Persistência
-   GINF-06 --- Redis, Cache e Filas
-   GINF-07 --- Storage e Arquivos
-   GINF-08 --- Containers, Imagens e Registry
-   GINF-09 --- CI/CD, Deploy e Rollback
-   GSF-10 --- Logging, Monitoramento e Auditoria
-   GSF-13 --- Gestão de Incidentes de Segurança
-   GAPI-11 --- Logging, Monitoramento e Auditoria
-   GOC --- GereIgreja Operations Center
-   GQF --- GereIgreja Quality Framework
-   GDF --- GereIgreja Documentation Framework

------------------------------------------------------------------------

# 120. Princípios Finais

Observabilidade deverá permitir que a Engenharia responda rapidamente:

``` text
O sistema está funcionando?
Quem está sendo impactado?
O que mudou?
Onde está a falha?
Desde quando?
Qual componente está saturado?
A recuperação funcionou?
```

O princípio central é:

``` text
Logs explicam eventos.
Métricas mostram comportamento.
Tracing conecta operações.
Alertas chamam para ação.
```

E:

``` text
Telemetria sem contexto
é apenas volume de dados.
```

O GereIgreja deverá evoluir sua observabilidade junto com a complexidade
da plataforma, mantendo segurança, utilidade e capacidade operacional.

------------------------------------------------------------------------

# 121. Status do Documento

**Pasta**

`docs/infraestrutura/`

**Arquivo**

`10-Observabilidade-Logs-Metricas-e-Alertas.md`

**Documento**

`GINF-10`

**Código**

`GINF-OBSERVABILITY-LOGS-METRICS-ALERTS`

**Família**

`GINF — GereIgreja Infrastructure Engineering`

**Versão**

`1.0`

**Status**

`OFICIAL`

**Responsável**

`Equipe de Engenharia`

**Última atualização**

`Agosto de 2026`

**Documento anterior**

`GINF-09 — CI/CD, Deploy e Rollback`

**Próximo documento recomendado**

`11-Backup-Restore-e-Disaster-Recovery.md`
