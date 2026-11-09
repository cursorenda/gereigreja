Pasta:

docs/infraestrutura/

Arquivo:

04-Runtime-Django-e-Workers.md

Documento:

GINF-04

Código:

GINF-DJANGO-RUNTIME-WORKERS

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

# GINF-04 --- Runtime Django e Workers

> "O código do GereIgreja deve executar em processos previsíveis,
> isolados por responsabilidade e observáveis do request HTTP ao
> processamento assíncrono."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com os Documentos Anteriores
4.  Princípios
5.  Visão Geral do Runtime
6.  Responsabilidades do Runtime Web
7.  Servidor de Desenvolvimento
8.  Runtime de Produção
9.  WSGI e ASGI
10. Processo Web
11. Quantidade de Processos
12. Threads
13. Concorrência
14. Estado Local
15. Statelessness
16. Inicialização da Aplicação
17. Configuração
18. Graceful Shutdown
19. Reinícios
20. Timeouts
21. Requests Longos
22. Processamento Assíncrono
23. Workers
24. Filas
25. Tipos de Tasks
26. Idempotência
27. Retries
28. Backoff
29. Timeouts de Tasks
30. Tasks Periódicas
31. Scheduler
32. Duplicidade
33. Locks
34. Prioridades
35. Filas Separadas
36. Dead Letter e Falhas Persistentes
37. Banco de Dados nos Workers
38. Transações
39. Redis e Broker
40. Integrações Externas
41. E-mail e Comunicações
42. Relatórios e Exportações
43. Webhooks
44. Contexto Multi-Tenant
45. Autenticação e Identidade
46. Auditoria
47. Segurança
48. Secrets
49. Privilégios
50. Containers
51. Imagens
52. Usuário do Processo
53. Recursos
54. CPU
55. Memória
56. Conexões com Banco
57. Autoscaling
58. Health Checks
59. Readiness
60. Liveness
61. Observabilidade
62. Logging
63. Métricas
64. Tracing e Correlação
65. Alertas
66. Deploy
67. Compatibilidade durante Deploy
68. Migrações
69. Rollback
70. Falhas
71. Jobs Presos
72. Poison Messages
73. Recuperação
74. Testes
75. Desenvolvimento Local
76. Staging
77. Produção
78. Anti-Padrões
79. Arquitetura de Referência
80. Checklist
81. Documentos Relacionados
82. Princípios Finais
83. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece o padrão oficial de execução da aplicação
Django e dos workers do GereIgreja.

Seu objetivo é garantir que os processos responsáveis por atender
requests e executar trabalhos assíncronos possuam:

-   responsabilidades claras;
-   configuração previsível;
-   isolamento;
-   segurança;
-   limites;
-   observabilidade;
-   capacidade de recuperação.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   aplicação Django;
-   processos HTTP;
-   WSGI/ASGI;
-   workers assíncronos;
-   schedulers;
-   filas;
-   jobs;
-   tasks periódicas;
-   containers de aplicação;
-   processos operacionais relacionados.

------------------------------------------------------------------------

# 3. Relação com os Documentos Anteriores

``` text
GINF-01
Arquitetura da Infraestrutura
        ↓
GINF-02
Ambientes e Configuração
        ↓
GINF-03
Rede, DNS, Proxy e TLS
        ↓
GINF-04
Runtime Django e Workers
```

GINF-03 termina na fronteira da aplicação.

GINF-04 define como a aplicação executa após essa fronteira.

------------------------------------------------------------------------

# 4. Princípios

O runtime deverá seguir:

-   processo com responsabilidade definida;
-   configuração externa;
-   ausência de dependência em estado local persistente;
-   graceful shutdown;
-   timeouts;
-   idempotência;
-   menor privilégio;
-   observabilidade;
-   escalabilidade por medição.

------------------------------------------------------------------------

# 5. Visão Geral do Runtime

``` text
Proxy / Load Balancer
          │
          ▼
    Django Runtime
          │
          ├────► PostgreSQL
          ├────► Redis
          ├────► Storage
          │
          └────► Queue
                    │
                    ▼
                  Workers
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Banco    Integrações  Storage
```

------------------------------------------------------------------------

# 6. Responsabilidades do Runtime Web

O processo web deverá priorizar operações compatíveis com o ciclo de
request/response.

Responsabilidades típicas:

-   autenticação;
-   autorização;
-   validação;
-   execução de services;
-   serialização;
-   resposta;
-   criação de jobs quando necessário.

------------------------------------------------------------------------

# 7. Servidor de Desenvolvimento

O servidor de desenvolvimento do Django deverá ser utilizado somente
para desenvolvimento.

Não utilizar:

``` text
python manage.py runserver
```

como servidor de produção.

------------------------------------------------------------------------

# 8. Runtime de Produção

Produção deverá utilizar servidor de aplicação apropriado e suportado
pela arquitetura adotada.

A escolha concreta poderá evoluir.

O requisito documental é:

``` text
runtime de produção
≠
servidor de desenvolvimento
```

------------------------------------------------------------------------

# 9. WSGI e ASGI

A arquitetura poderá utilizar WSGI ou ASGI conforme as necessidades
reais.

A decisão deverá considerar:

-   stack Django;
-   concorrência;
-   conexões persistentes;
-   bibliotecas;
-   observabilidade;
-   operação.

Não adotar ASGI apenas por modernidade se não houver necessidade
técnica.

------------------------------------------------------------------------

# 10. Processo Web

Cada processo deverá ser descartável.

Reiniciar uma instância não deverá causar perda de estado de negócio.

------------------------------------------------------------------------

# 11. Quantidade de Processos

Quantidade de processos não deverá ser definida por fórmula rígida
universal.

Deverá considerar:

-   CPU;
-   memória;
-   workload;
-   latência;
-   conexões;
-   banco.

Medir antes de aumentar.

------------------------------------------------------------------------

# 12. Threads

Threads poderão ser utilizadas quando compatíveis com o runtime
escolhido.

Deverão ser avaliadas em conjunto com:

-   thread safety;
-   conexões;
-   bibliotecas;
-   consumo de memória.

------------------------------------------------------------------------

# 13. Concorrência

Mais concorrência não significa automaticamente mais capacidade.

Exemplo:

``` text
mais workers web
        ↓
mais conexões
        ↓
banco saturado
```

A plataforma deverá ser dimensionada como sistema.

------------------------------------------------------------------------

# 14. Estado Local

Não armazenar estado permanente apenas na memória ou disco efêmero do
processo web.

Exemplos inadequados:

-   sessão crítica em memória local;
-   arquivo necessário apenas no container;
-   lock de negócio somente em variável Python.

------------------------------------------------------------------------

# 15. Statelessness

Sempre que possível, processos web deverão ser stateless.

Estado compartilhado deverá utilizar componentes apropriados:

-   banco;
-   cache;
-   storage;
-   fila.

------------------------------------------------------------------------

# 16. Inicialização da Aplicação

Startup deverá:

-   carregar configuração;
-   validar valores críticos;
-   inicializar dependências necessárias;
-   falhar claramente quando configuração essencial estiver inválida.

Evitar executar operações destrutivas automaticamente no startup.

------------------------------------------------------------------------

# 17. Configuração

Aplicar GINF-02.

O runtime deverá receber configuração sem alteração manual do código.

------------------------------------------------------------------------

# 18. Graceful Shutdown

Processos deverão responder adequadamente ao sinal de encerramento.

Objetivo:

``` text
parar de aceitar novo trabalho
        ↓
concluir trabalho seguro em andamento
        ↓
encerrar
```

------------------------------------------------------------------------

# 19. Reinícios

Reinícios deverão ser esperados.

A aplicação não deverá depender da longevidade de um processo
específico.

------------------------------------------------------------------------

# 20. Timeouts

Requests deverão possuir limites.

Timeouts deverão ser coerentes entre:

``` text
cliente
proxy
runtime
integração
```

Evitar runtime mantendo requests indefinidamente.

------------------------------------------------------------------------

# 21. Requests Longos

Operações longas deverão ser candidatas a processamento assíncrono.

Exemplos:

-   exportação extensa;
-   geração de relatório;
-   processamento de arquivo;
-   sincronização externa.

------------------------------------------------------------------------

# 22. Processamento Assíncrono

O processamento assíncrono deverá retirar do request trabalhos que:

-   demoram;
-   dependem de terceiros;
-   precisam de retry;
-   podem ser executados depois;
-   possuem volume variável.

------------------------------------------------------------------------

# 23. Workers

Workers deverão executar jobs de responsabilidade conhecida.

Não criar um worker genérico sem limites para qualquer tipo de trabalho
crítico.

------------------------------------------------------------------------

# 24. Filas

Tasks deverão ser enviadas para filas adequadas.

A fila é mecanismo de transporte e desacoplamento.

Não é substituto para modelagem de estado de negócio.

------------------------------------------------------------------------

# 25. Tipos de Tasks

Categorias possíveis:

``` text
notifications
integrations
reports
exports
webhooks
maintenance
```

A classificação concreta deverá acompanhar os módulos reais do
GereIgreja.

------------------------------------------------------------------------

# 26. Idempotência

Tasks sujeitas a retry deverão ser idempotentes quando possível.

Aplicar GAPI-09 para operações correlatas.

------------------------------------------------------------------------

# 27. Retries

Retry deverá ocorrer apenas quando a falha puder ser transitória.

Exemplos:

-   timeout;
-   429;
-   indisponibilidade externa.

Não repetir indefinidamente erro de validação permanente.

------------------------------------------------------------------------

# 28. Backoff

Retries deverão utilizar atraso crescente quando apropriado.

``` text
falha
 ↓
espera
 ↓
retry
 ↓
espera maior
```

Evitar tempestade de retries.

------------------------------------------------------------------------

# 29. Timeouts de Tasks

Tasks também deverão possuir limite de execução.

Jobs sem limite podem consumir workers indefinidamente.

------------------------------------------------------------------------

# 30. Tasks Periódicas

Tasks agendadas deverão possuir:

-   owner;
-   frequência;
-   finalidade;
-   idempotência;
-   observabilidade.

------------------------------------------------------------------------

# 31. Scheduler

O scheduler deverá evitar execução duplicada acidental quando a tarefa
exigir singleton.

A arquitetura concreta dependerá da solução de filas adotada.

------------------------------------------------------------------------

# 32. Duplicidade

Filas normalmente operam com possibilidade de redelivery.

A aplicação deverá assumir:

``` text
mensagem pode chegar
mais de uma vez
```

quando a tecnologia não garantir exatamente uma entrega.

------------------------------------------------------------------------

# 33. Locks

Locks distribuídos poderão ser utilizados quando realmente necessários.

Deverão possuir:

-   expiração;
-   owner;
-   chave correta;
-   recuperação de falha.

Evitar lock permanente.

------------------------------------------------------------------------

# 34. Prioridades

Operações críticas não deverão ficar bloqueadas indefinidamente por
trabalhos pesados de baixa prioridade.

Quando necessário, separar filas.

------------------------------------------------------------------------

# 35. Filas Separadas

Exemplo conceitual:

``` text
critical
default
reports
integrations
```

A quantidade de filas deverá permanecer simples e justificada.

------------------------------------------------------------------------

# 36. Dead Letter e Falhas Persistentes

Quando suportado pela arquitetura, jobs que falham repetidamente deverão
ser isolados para investigação.

Não permitir loop infinito silencioso.

------------------------------------------------------------------------

# 37. Banco de Dados nos Workers

Workers deverão utilizar conexões de banco de forma controlada.

A soma de:

``` text
web processes
+
worker concurrency
```

deverá respeitar capacidade do banco.

------------------------------------------------------------------------

# 38. Transações

Não manter transações abertas enquanto aguarda integração externa.

Preferir:

``` text
transação curta
→ commit
→ processamento externo controlado
```

conforme consistência exigida.

------------------------------------------------------------------------

# 39. Redis e Broker

Redis ou broker equivalente deverá seguir GINF-06 futuramente.

No runtime:

-   conexões controladas;
-   timeouts;
-   autenticação;
-   rede privada;
-   observabilidade.

------------------------------------------------------------------------

# 40. Integrações Externas

Workers são apropriados para várias integrações.

Sempre aplicar:

-   timeout;
-   retry controlado;
-   idempotência;
-   logging;
-   correlação.

------------------------------------------------------------------------

# 41. E-mail e Comunicações

Envio de comunicações não deverá bloquear request quando não houver
necessidade de resposta síncrona.

O job deverá registrar resultado suficiente para operação.

------------------------------------------------------------------------

# 42. Relatórios e Exportações

Relatórios pesados deverão evitar sobrecarregar processos web.

Fluxo recomendado:

``` text
Usuário solicita
      ↓
Job criado
      ↓
Worker processa
      ↓
Arquivo no storage
      ↓
Status atualizado
      ↓
Usuário acessa resultado
```

------------------------------------------------------------------------

# 43. Webhooks

Processamento de webhook deverá retornar rapidamente quando possível.

Fluxo:

``` text
receber
→ autenticar/validar
→ registrar/idempotência
→ enfileirar
→ responder
→ processar
```

quando compatível com o fornecedor.

------------------------------------------------------------------------

# 44. Contexto Multi-Tenant

Toda task relacionada a uma igreja deverá transportar contexto
suficiente para recuperar o tenant de forma segura.

Exemplo conceitual:

``` text
task_id
tenant_id
resource_id
```

O worker deverá revalidar o escopo.

Nunca confiar em tenant derivado apenas de dado não validado.

------------------------------------------------------------------------

# 45. Autenticação e Identidade

Tasks internas não deverão simular usuário arbitrário sem necessidade.

Quando uma ação precisar registrar ator, distinguir:

-   usuário;
-   sistema;
-   integração;
-   job.

------------------------------------------------------------------------

# 46. Auditoria

Operações auditáveis continuam auditáveis quando executadas por worker.

Mover para fila não remove obrigação de rastreabilidade.

------------------------------------------------------------------------

# 47. Segurança

Workers deverão seguir os mesmos princípios de segurança da aplicação.

Não considerar fila como fronteira confiável absoluta.

------------------------------------------------------------------------

# 48. Secrets

Secrets deverão ser injetados conforme GSF-09 e GINF-02.

Workers não deverão receber secrets que não utilizam.

------------------------------------------------------------------------

# 49. Privilégios

Separar privilégios quando necessário.

Exemplo:

``` text
worker de e-mail
não precisa
de credencial financeira
```

------------------------------------------------------------------------

# 50. Containers

Web e worker poderão compartilhar a mesma imagem quando utilizarem o
mesmo código, mas executar comandos diferentes.

Exemplo conceitual:

``` text
image: gereigreja:<release>

web:
  command: web-runtime

worker:
  command: worker-runtime
```

------------------------------------------------------------------------

# 51. Imagens

A imagem deverá:

-   ser identificável;
-   corresponder à release;
-   evitar secrets;
-   conter apenas dependências necessárias;
-   possuir origem controlada.

------------------------------------------------------------------------

# 52. Usuário do Processo

Evitar execução como root quando não necessária.

Aplicar menor privilégio no runtime.

------------------------------------------------------------------------

# 53. Recursos

Processos deverão possuir limites e reservas conforme a plataforma de
execução permitir.

Sem limites, um job defeituoso poderá afetar outros componentes.

------------------------------------------------------------------------

# 54. CPU

CPU deverá ser monitorada por tipo de processo.

Jobs CPU-bound poderão exigir estratégia diferente de jobs I/O-bound.

------------------------------------------------------------------------

# 55. Memória

Monitorar:

-   consumo médio;
-   picos;
-   crescimento;
-   OOM;
-   leaks.

Workers long-lived deverão ser observados para crescimento progressivo.

------------------------------------------------------------------------

# 56. Conexões com Banco

Conexões são recurso finito.

Dimensionamento deverá considerar:

``` text
web
+
workers
+
admin
+
jobs
<
capacidade segura do banco
```

------------------------------------------------------------------------

# 57. Autoscaling

Autoscaling poderá ser adotado quando houver métricas confiáveis.

Web:

-   CPU;
-   latência;
-   requests.

Workers:

-   tamanho da fila;
-   idade da mensagem;
-   throughput.

Não escalar workers sem considerar banco e APIs externas.

------------------------------------------------------------------------

# 58. Health Checks

Processos web deverão possuir health check adequado.

Workers poderão exigir sinais próprios de saúde.

------------------------------------------------------------------------

# 59. Readiness

Readiness responde:

``` text
este processo
está pronto
para receber trabalho?
```

------------------------------------------------------------------------

# 60. Liveness

Liveness responde:

``` text
este processo
continua operacional
ou precisa ser reiniciado?
```

Não confundir readiness com liveness.

------------------------------------------------------------------------

# 61. Observabilidade

Web e workers deverão ser distinguíveis em observabilidade.

Campos úteis:

``` text
service=web
service=worker
queue=reports
environment=production
release=...
```

------------------------------------------------------------------------

# 62. Logging

Logs deverão incluir contexto suficiente.

Para tasks:

-   task ID;
-   tenant quando permitido;
-   tipo;
-   tentativa;
-   duração;
-   resultado.

Não registrar payload sensível indiscriminadamente.

------------------------------------------------------------------------

# 63. Métricas

Web:

-   throughput;
-   latência;
-   5xx;
-   workers ocupados.

Assíncrono:

-   queue depth;
-   queue age;
-   execução;
-   falhas;
-   retries;
-   duração.

------------------------------------------------------------------------

# 64. Tracing e Correlação

Quando um request cria uma task, preservar correlação quando possível.

``` text
request_id
   ↓
task_id
   ↓
integration call
```

Isso melhora investigação ponta a ponta.

------------------------------------------------------------------------

# 65. Alertas

Alertar para:

-   fila acumulada;
-   tasks antigas;
-   taxa de falha;
-   workers indisponíveis;
-   OOM;
-   reinícios excessivos;
-   saturação.

------------------------------------------------------------------------

# 66. Deploy

Web e workers de uma mesma release deverão possuir estratégia
compatível.

Evitar worker antigo processando payload que somente código novo
compreende sem estratégia de compatibilidade.

------------------------------------------------------------------------

# 67. Compatibilidade durante Deploy

Durante rolling deploy poderá existir coexistência:

``` text
release N
+
release N+1
```

Contratos internos de fila e banco deverão tolerar a janela quando
necessário.

------------------------------------------------------------------------

# 68. Migrações

Aplicar estratégia compatível com deploy.

Preferir mudanças expansíveis:

``` text
adicionar
→ migrar
→ utilizar
→ remover depois
```

em vez de mudança destrutiva instantânea.

------------------------------------------------------------------------

# 69. Rollback

Rollback deverá considerar:

-   código web;
-   workers;
-   schema;
-   mensagens já enfileiradas;
-   configurações.

------------------------------------------------------------------------

# 70. Falhas

Falhas de runtime deverão ser classificáveis.

Exemplos:

-   crash;
-   timeout;
-   OOM;
-   dependency failure;
-   poison task;
-   configuração inválida.

------------------------------------------------------------------------

# 71. Jobs Presos

Deverá ser possível identificar jobs que excedem duração esperada.

Jobs presos não deverão permanecer invisíveis.

------------------------------------------------------------------------

# 72. Poison Messages

Mensagem que sempre causa falha deverá ser isolada após política
definida de retries.

Evitar que uma única mensagem consuma capacidade indefinidamente.

------------------------------------------------------------------------

# 73. Recuperação

Após indisponibilidade:

``` text
restaurar broker/cache
      ↓
subir workers
      ↓
verificar filas
      ↓
processar backlog controladamente
      ↓
monitorar dependências
```

A ordem real dependerá da arquitetura.

------------------------------------------------------------------------

# 74. Testes

Testar:

-   execução web;
-   tasks;
-   retries;
-   idempotência;
-   tenant;
-   falhas externas;
-   shutdown;
-   compatibilidade;
-   jobs periódicos.

------------------------------------------------------------------------

# 75. Desenvolvimento Local

Development deverá permitir executar web e worker sem dependências de
produção.

Comandos e serviços necessários deverão ser documentados.

------------------------------------------------------------------------

# 76. Staging

Staging deverá validar:

-   runtime real;
-   worker;
-   broker;
-   scheduler;
-   deploy;
-   shutdown;
-   integração;
-   métricas.

------------------------------------------------------------------------

# 77. Produção

Produção deverá possuir:

-   runtime apropriado;
-   limites;
-   health checks;
-   observabilidade;
-   restart policy;
-   acesso controlado;
-   versionamento de release.

------------------------------------------------------------------------

# 78. Anti-Padrões

Evitar:

``` text
runserver
em produção
```

------------------------------------------------------------------------

``` text
request HTTP
esperando relatório de minutos
```

------------------------------------------------------------------------

``` text
task com retry infinito
```

------------------------------------------------------------------------

``` text
worker
sem tenant explícito
para operação multi-tenant
```

------------------------------------------------------------------------

``` text
toda task
na mesma fila
independentemente da criticidade
```

------------------------------------------------------------------------

``` text
aumentar concorrência
sem verificar banco
```

------------------------------------------------------------------------

``` text
task auditável
sem auditoria
porque roda em background
```

------------------------------------------------------------------------

``` text
processo dependendo
de arquivo local persistente
```

------------------------------------------------------------------------

``` text
worker antigo + mensagem nova
sem estratégia de compatibilidade
```

------------------------------------------------------------------------

# 79. Arquitetura de Referência

``` text
                     INTERNET
                        │
                        ▼
                 PROXY / LOAD BALANCER
                        │
                        ▼
              ┌───────────────────┐
              │   DJANGO WEB      │
              │  stateless        │
              └───────┬───────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      DATABASE      REDIS       STORAGE
          ▲           │
          │           ▼
          │       QUEUE/BROKER
          │           │
          │    ┌──────┼─────────┐
          │    ▼      ▼         ▼
          │  WORKER  WORKER   WORKER
          │ critical reports integrations
          │    │      │         │
          └────┴──────┴─────────┘
                       │
                       ▼
               EXTERNAL SERVICES

Observabilidade transversal:
Logs + Métricas + Correlação + Alertas
```

------------------------------------------------------------------------

# 80. Checklist

## Web

-   [ ] runtime de produção;
-   [ ] stateless;
-   [ ] timeouts;
-   [ ] graceful shutdown;
-   [ ] health checks;
-   [ ] limites de recursos.

## Workers

-   [ ] filas definidas;
-   [ ] retries controlados;
-   [ ] backoff;
-   [ ] timeouts;
-   [ ] idempotência;
-   [ ] contexto de tenant.

## Dados

-   [ ] conexões controladas;
-   [ ] transações curtas;
-   [ ] capacidade do banco considerada;
-   [ ] broker privado.

## Segurança

-   [ ] secrets mínimos;
-   [ ] menor privilégio;
-   [ ] usuário não-root quando possível;
-   [ ] auditoria preservada;
-   [ ] payload sensível não logado.

## Observabilidade

-   [ ] logs web;
-   [ ] logs workers;
-   [ ] queue depth;
-   [ ] queue age;
-   [ ] falhas;
-   [ ] retries;
-   [ ] alertas.

## Deploy

-   [ ] release identificável;
-   [ ] compatibilidade web/worker;
-   [ ] schema compatível;
-   [ ] rollback avaliado;
-   [ ] mensagens antigas consideradas.

------------------------------------------------------------------------

# 81. Documentos Relacionados

-   GINF-01 --- Arquitetura da Infraestrutura
-   GINF-02 --- Ambientes e Configuração
-   GINF-03 --- Rede, DNS, Proxy e TLS
-   GSF-03 --- GereIgreja Security Framework
-   GSF-05 --- Segurança Multi-Tenant
-   GSF-09 --- Gestão de Segredos e Criptografia
-   GSF-10 --- Logging, Monitoramento e Auditoria
-   GSF-15 --- Secure Development Lifecycle
-   GAPI-08 --- Webhooks e Integrações
-   GAPI-09 --- Idempotência e Rate Limiting
-   GAPI-11 --- Logging, Monitoramento e Auditoria
-   GAPI-12 --- Testes de APIs
-   GOC --- GereIgreja Operations Center
-   GQF --- GereIgreja Quality Framework
-   GereIgreja Backend Engineering

------------------------------------------------------------------------

# 82. Princípios Finais

O runtime do GereIgreja deverá separar claramente dois ciclos:

``` text
Request / Response
```

e:

``` text
Background Processing
```

Nem toda operação pertence ao request HTTP.

Nem toda operação em background pode ser executada sem contexto, limites
ou governança.

O princípio central é:

``` text
Processos web devem ser
rápidos, descartáveis e previsíveis.

Workers devem ser
idempotentes, limitados e observáveis.
```

Ambos deverão preservar segurança, tenant, auditoria e consistência da
plataforma.

------------------------------------------------------------------------

# 83. Status do Documento

**Pasta**

`docs/infraestrutura/`

**Arquivo**

`04-Runtime-Django-e-Workers.md`

**Documento**

`GINF-04`

**Código**

`GINF-DJANGO-RUNTIME-WORKERS`

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

`GINF-03 — Rede, DNS, Proxy e TLS`

**Próximo documento recomendado**

`05-Banco-de-Dados-e-Persistencia.md`
