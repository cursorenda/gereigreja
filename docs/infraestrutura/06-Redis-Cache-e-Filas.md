Pasta:

docs/infraestrutura/

Arquivo:

06-Redis-Cache-e-Filas.md

Documento:

GINF-06

Código:

GINF-REDIS-CACHE-QUEUES

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

# GINF-06 --- Redis, Cache e Filas

> "Redis deve acelerar e coordenar a plataforma sem se tornar uma fonte
> invisível de verdade, uma fronteira insegura entre tenants ou um ponto
> único de falha não observado."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com GINF-04 e GINF-05
4.  Princípios Fundamentais
5.  Papel do Redis no GereIgreja
6.  Responsabilidades Permitidas
7.  Responsabilidades que Exigem Cuidado
8.  Redis não é o Banco Principal
9.  Ambientes
10. Isolamento entre Ambientes
11. Rede
12. Autenticação
13. TLS
14. Secrets
15. Menor Privilégio
16. Namespaces
17. Multi-Tenant
18. Chaves
19. Convenção de Chaves
20. Dados Sensíveis
21. TTL
22. Expiração
23. Eviction
24. Memória
25. Persistência do Redis
26. Cache
27. Cache de Aplicação
28. Cache de Query
29. Cache de Resposta
30. Cache Multi-Tenant
31. Cache Invalidation
32. Cache Stampede
33. Cache Warming
34. Negative Cache
35. Sessões
36. Rate Limiting
37. Locks Distribuídos
38. Idempotência
39. Filas
40. Broker
41. Estrutura de Filas
42. Mensagens
43. Payloads
44. Contexto de Tenant
45. Idempotência de Tasks
46. Acknowledgement
47. Retries
48. Backoff
49. Dead Letter
50. Poison Messages
51. Priorização
52. Queue Depth
53. Queue Age
54. Workers
55. Concorrência
56. Scheduler
57. Tasks Periódicas
58. Duplicidade
59. Ordem
60. Garantias de Entrega
61. Falhas do Redis
62. Degradação
63. Reconexão
64. Timeouts
65. Circuit Breaker
66. Persistência de Estado de Negócio
67. Observabilidade
68. Logging
69. Métricas
70. Alertas
71. Capacidade
72. Escalabilidade
73. Alta Disponibilidade
74. Backup
75. Recuperação
76. Deploy
77. Mudanças de Estrutura
78. Segurança
79. LGPD
80. Testes
81. Desenvolvimento
82. Staging
83. Produção
84. Anti-Padrões
85. Arquitetura de Referência
86. Checklist
87. Documentos Relacionados
88. Princípios Finais
89. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece os padrões oficiais para uso de Redis, cache e
filas na infraestrutura do GereIgreja.

Seu objetivo é garantir que componentes de alta velocidade e
processamento assíncrono sejam utilizados com:

-   finalidade explícita;
-   isolamento multi-tenant;
-   segurança;
-   expiração controlada;
-   tolerância a falhas;
-   idempotência;
-   observabilidade;
-   capacidade previsível.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   Redis;
-   cache;
-   rate limiting;
-   locks;
-   chaves idempotentes;
-   sessões quando aplicável;
-   brokers;
-   filas;
-   tasks assíncronas;
-   schedulers;
-   workers.

------------------------------------------------------------------------

# 3. Relação com GINF-04 e GINF-05

``` text
GINF-04
Runtime Django e Workers
        │
        ▼
GINF-06
Redis, Cache e Filas
        │
        ├────► acelera
        ├────► coordena
        └────► transporta trabalho

GINF-05
PostgreSQL
        │
        └────► permanece como persistência principal
              dos dados relacionais de negócio
```

------------------------------------------------------------------------

# 4. Princípios Fundamentais

Aplicar:

-   Redis privado por padrão;
-   tenant explícito;
-   TTL onde apropriado;
-   chaves previsíveis;
-   payload mínimo;
-   idempotência;
-   timeouts;
-   observabilidade;
-   nenhuma dependência silenciosa de dados efêmeros.

------------------------------------------------------------------------

# 5. Papel do Redis no GereIgreja

Redis poderá apoiar:

``` text
Cache
Rate Limiting
Locks
Idempotência
Broker/Fila
Estado Transitório
```

Cada uso deverá ser identificado.

------------------------------------------------------------------------

# 6. Responsabilidades Permitidas

Exemplos adequados:

-   cache de dados reconstruíveis;
-   contadores temporários;
-   controle de rate limit;
-   locks com expiração;
-   transporte de tasks;
-   chaves de idempotência.

------------------------------------------------------------------------

# 7. Responsabilidades que Exigem Cuidado

Exigem análise específica:

-   sessões;
-   estado de workflow;
-   resultados de jobs;
-   dados que não podem ser perdidos;
-   eventos financeiros.

Se a perda do Redis causar perda irreversível de negócio, a arquitetura
deverá ser revista.

------------------------------------------------------------------------

# 8. Redis não é o Banco Principal

Regra:

``` text
Dado crítico e permanente
→ persistência durável

Redis
→ aceleração, coordenação ou estado transitório
```

------------------------------------------------------------------------

# 9. Ambientes

Cada ambiente deverá utilizar instância, cluster, database lógico ou
isolamento equivalente adequado.

Production não deverá compartilhar chaves com staging.

------------------------------------------------------------------------

# 10. Isolamento entre Ambientes

A separação deverá impedir:

``` text
staging worker
→ production queue

development cache
→ production Redis
```

------------------------------------------------------------------------

# 11. Rede

Redis deverá permanecer privado.

Não expor diretamente à Internet.

------------------------------------------------------------------------

# 12. Autenticação

Quando suportada pela solução adotada, autenticação deverá estar
habilitada e protegida.

Rede privada não substitui autenticação quando a arquitetura permitir
ambas.

------------------------------------------------------------------------

# 13. TLS

TLS deverá ser utilizado quando exigido pela topologia, provedor ou
classificação de risco.

------------------------------------------------------------------------

# 14. Secrets

Credenciais Redis/broker deverão seguir GSF-09 e GINF-02.

Nunca registrar senha ou connection string completa em logs.

------------------------------------------------------------------------

# 15. Menor Privilégio

Quando a tecnologia permitir ACLs, separar permissões conforme
responsabilidade.

Um consumidor de cache não deverá necessariamente administrar toda a
instância.

------------------------------------------------------------------------

# 16. Namespaces

Chaves deverão possuir namespace.

Exemplo conceitual:

``` text
gereigreja:<env>:<purpose>:...
```

A implementação real deverá evitar duplicar ambiente quando a instância
já for totalmente isolada, se isso não trouxer valor.

------------------------------------------------------------------------

# 17. Multi-Tenant

Dados relacionados a uma igreja deverão possuir tenant no escopo da
chave quando compartilharem o mesmo Redis.

Exemplo:

``` text
cache:tenant:<tenant_id>:member:<member_id>
```

Nunca permitir colisão entre tenants.

------------------------------------------------------------------------

# 18. Chaves

Chaves deverão ser:

-   determinísticas;
-   curtas o suficiente;
-   legíveis operacionalmente;
-   sem dados pessoais desnecessários.

------------------------------------------------------------------------

# 19. Convenção de Chaves

Padrão conceitual:

``` text
<purpose>:<scope>:<identifier>:<version>
```

Exemplo:

``` text
ratelimit:tenant:42:api:v1
```

------------------------------------------------------------------------

# 20. Dados Sensíveis

Evitar dados sensíveis no nome da chave.

Não utilizar:

``` text
cache:cpf:123...
```

quando um identificador interno for suficiente.

------------------------------------------------------------------------

# 21. TTL

Toda chave transitória deverá avaliar TTL.

TTL evita estado esquecido e crescimento indefinido.

------------------------------------------------------------------------

# 22. Expiração

Expiração deverá refletir a semântica.

Exemplos:

``` text
cache → minutos
idempotência → janela da operação
lock → segundos/minutos
rate limit → janela do limite
```

Valores reais deverão ser definidos por caso de uso.

------------------------------------------------------------------------

# 23. Eviction

A política de eviction deverá ser compatível com os dados armazenados.

Não misturar indiscriminadamente cache descartável e estado que não pode
ser evicted.

------------------------------------------------------------------------

# 24. Memória

Redis é memória finita.

Monitorar:

-   used memory;
-   fragmentation;
-   evictions;
-   key count;
-   crescimento.

------------------------------------------------------------------------

# 25. Persistência do Redis

RDB/AOF ou mecanismos equivalentes poderão ser adotados conforme o papel
da instância.

Persistência do Redis não transforma automaticamente cache em banco de
negócio.

------------------------------------------------------------------------

# 26. Cache

Cache deverá melhorar desempenho sem alterar a verdade do domínio.

A fonte autoritativa deverá permanecer conhecida.

------------------------------------------------------------------------

# 27. Cache de Aplicação

Cache poderá guardar dados reconstruíveis.

Antes de cachear, perguntar:

``` text
qual é a fonte?
como invalida?
quanto tempo pode ficar desatualizado?
```

------------------------------------------------------------------------

# 28. Cache de Query

Cachear queries somente quando:

-   consulta for relevante;
-   invalidação for compreensível;
-   benefício for medido.

Não cachear toda query por padrão.

------------------------------------------------------------------------

# 29. Cache de Resposta

Respostas autenticadas ou específicas de tenant exigem chave e política
corretas.

Nunca compartilhar cache entre igrejas.

------------------------------------------------------------------------

# 30. Cache Multi-Tenant

Regra obrigatória:

``` text
tenant A
X
cache do tenant B
```

O tenant deverá participar da chave ou existir isolamento equivalente.

------------------------------------------------------------------------

# 31. Cache Invalidation

Estratégias possíveis:

-   TTL;
-   delete na escrita;
-   versionamento de chave;
-   eventos.

Evitar invalidação complexa sem necessidade.

------------------------------------------------------------------------

# 32. Cache Stampede

Para chaves muito acessadas, considerar proteção contra múltiplos
processos reconstruindo o mesmo valor simultaneamente.

Possíveis mecanismos:

-   lock curto;
-   jitter;
-   stale-while-revalidate quando aplicável.

------------------------------------------------------------------------

# 33. Cache Warming

Warming somente deverá existir quando necessário.

Não transformar deploy em processo longo de reconstrução de todo cache.

------------------------------------------------------------------------

# 34. Negative Cache

Resultados "não encontrado" poderão ser cacheados por janela curta
quando isso reduzir carga e não causar comportamento incorreto.

------------------------------------------------------------------------

# 35. Sessões

Se sessões utilizarem Redis, deverão existir decisões claras sobre:

-   expiração;
-   logout;
-   indisponibilidade;
-   persistência;
-   segurança.

Aplicar GAF.

------------------------------------------------------------------------

# 36. Rate Limiting

Redis poderá sustentar contadores de rate limiting.

Chaves deverão considerar o escopo correto:

``` text
IP
user
tenant
API key
operation
```

conforme GAPI-09.

------------------------------------------------------------------------

# 37. Locks Distribuídos

Locks deverão possuir expiração obrigatória.

Fluxo:

``` text
acquire
→ execute
→ release
```

e o sistema deverá tolerar expiração ou falha do processo proprietário.

------------------------------------------------------------------------

# 38. Idempotência

Chaves idempotentes poderão registrar:

-   chave;
-   estado;
-   resultado mínimo;
-   expiração.

Para operações críticas, a persistência durável poderá ser necessária em
vez de depender exclusivamente do Redis.

------------------------------------------------------------------------

# 39. Filas

Filas desacoplam produtor e consumidor.

``` text
Producer
   ↓
Queue
   ↓
Worker
```

A fila não deverá esconder falhas de processamento.

------------------------------------------------------------------------

# 40. Broker

O broker deverá possuir:

-   rede privada;
-   autenticação;
-   limites;
-   observabilidade;
-   estratégia de recuperação.

------------------------------------------------------------------------

# 41. Estrutura de Filas

Começar simples.

Exemplo:

``` text
critical
default
reports
integrations
```

Criar nova fila somente quando houver diferença operacional real.

------------------------------------------------------------------------

# 42. Mensagens

Mensagens deverão conter apenas dados necessários para localizar e
processar a operação.

Preferir IDs a objetos completos.

------------------------------------------------------------------------

# 43. Payloads

Evitar:

``` text
task(payload_completo_de_membro)
```

Preferir:

``` text
task(tenant_id, member_id)
```

quando a task puder buscar estado atual de forma segura.

------------------------------------------------------------------------

# 44. Contexto de Tenant

Tasks multi-tenant deverão carregar tenant explicitamente.

O worker deverá revalidar que o recurso pertence ao tenant.

------------------------------------------------------------------------

# 45. Idempotência de Tasks

Uma task poderá ser executada mais de uma vez.

Projetar para:

``` text
at-least-once
```

quando essa for a garantia prática do sistema.

------------------------------------------------------------------------

# 46. Acknowledgement

A mensagem somente deverá ser considerada concluída quando o
processamento atingir ponto seguro.

A estratégia concreta dependerá da biblioteca adotada.

------------------------------------------------------------------------

# 47. Retries

Retry deverá possuir:

-   limite;
-   motivo;
-   observabilidade;
-   backoff.

------------------------------------------------------------------------

# 48. Backoff

Preferir exponential backoff com jitter quando adequado para integrações
externas.

Evitar sincronizar milhares de retries no mesmo instante.

------------------------------------------------------------------------

# 49. Dead Letter

Quando suportado, falhas persistentes deverão ser isoladas para análise.

A dead letter queue não deverá virar depósito permanente sem owner.

------------------------------------------------------------------------

# 50. Poison Messages

Mensagens que sempre quebram o consumidor deverão ser identificadas.

Após limite:

``` text
isolar
→ alertar
→ investigar
```

------------------------------------------------------------------------

# 51. Priorização

Tasks críticas poderão possuir fila própria.

Exemplo:

``` text
critical
```

não deverá ser inundada por relatórios pesados.

------------------------------------------------------------------------

# 52. Queue Depth

Monitorar quantidade de mensagens aguardando.

Depth crescente continuamente indica incapacidade de acompanhar
produção.

------------------------------------------------------------------------

# 53. Queue Age

Idade da mensagem mais antiga é métrica essencial.

Uma fila pequena também pode estar travada.

------------------------------------------------------------------------

# 54. Workers

Workers deverão seguir GINF-04.

A fila e o worker formam uma unidade operacional.

------------------------------------------------------------------------

# 55. Concorrência

Concorrência deverá respeitar:

-   banco;
-   APIs externas;
-   CPU;
-   memória;
-   Redis;
-   limites do fornecedor.

------------------------------------------------------------------------

# 56. Scheduler

Tasks periódicas deverão possuir scheduler controlado.

Evitar múltiplos schedulers executando a mesma rotina quando ela exige
singleton.

------------------------------------------------------------------------

# 57. Tasks Periódicas

Toda rotina periódica deverá ter:

-   owner;
-   frequência;
-   timeout;
-   idempotência;
-   alerta quando crítica.

------------------------------------------------------------------------

# 58. Duplicidade

Duplicidade deverá ser tratada como cenário normal em sistemas de fila.

Nunca assumir "esta task só executará uma vez" sem garantia concreta.

------------------------------------------------------------------------

# 59. Ordem

Não depender de ordenação global de mensagens sem necessidade.

Se ordem for requisito de negócio, ela deverá ser explicitamente
projetada.

------------------------------------------------------------------------

# 60. Garantias de Entrega

A equipe deverá conhecer a garantia prática da tecnologia adotada.

Termos importantes:

``` text
at-most-once
at-least-once
exactly-once
```

Não afirmar exactly-once sem mecanismo real que o sustente.

------------------------------------------------------------------------

# 61. Falhas do Redis

A aplicação deverá considerar Redis indisponível.

O impacto depende do uso.

``` text
cache falha
→ possível degradação

broker falha
→ processamento assíncrono interrompido

rate limit falha
→ decisão de fail-open/fail-closed deve ser explícita
```

------------------------------------------------------------------------

# 62. Degradação

Cache não crítico deverá preferencialmente permitir fallback à fonte
autoritativa, respeitando capacidade.

Não criar avalanche no banco durante indisponibilidade.

------------------------------------------------------------------------

# 63. Reconexão

Clientes deverão possuir estratégia controlada de reconexão.

Evitar loop agressivo sem atraso.

------------------------------------------------------------------------

# 64. Timeouts

Toda operação Redis deverá possuir timeout adequado.

Não bloquear request indefinidamente esperando cache.

------------------------------------------------------------------------

# 65. Circuit Breaker

Para dependências críticas, circuit breaker poderá ser considerado
quando a arquitetura justificar.

Não aplicar mecanicamente a todas as chamadas.

------------------------------------------------------------------------

# 66. Persistência de Estado de Negócio

Estados como:

-   pagamento confirmado;
-   membro cadastrado;
-   lançamento financeiro;
-   permissão concedida;

não deverão existir exclusivamente no Redis.

------------------------------------------------------------------------

# 67. Observabilidade

Redis, filas e workers deverão ser observáveis como conjunto.

------------------------------------------------------------------------

# 68. Logging

Registrar eventos relevantes:

-   conexão falha;
-   retry;
-   task falha;
-   fila;
-   duração;
-   idempotência.

Não logar secrets ou payload sensível integral.

------------------------------------------------------------------------

# 69. Métricas

Redis:

-   memória;
-   conexões;
-   hits/misses;
-   evictions;
-   latência;
-   erros.

Filas:

-   depth;
-   age;
-   throughput;
-   retries;
-   failures.

------------------------------------------------------------------------

# 70. Alertas

Alertar para:

-   Redis indisponível;
-   memória crítica;
-   evictions inesperadas;
-   fila acumulada;
-   mensagem antiga;
-   taxa alta de falha;
-   workers indisponíveis.

------------------------------------------------------------------------

# 71. Capacidade

Capacidade deverá considerar:

``` text
memória
+
taxa de operações
+
número de conexões
+
volume de filas
+
tamanho dos payloads
```

------------------------------------------------------------------------

# 72. Escalabilidade

Escalar apenas após identificar gargalo.

Possibilidades:

-   mais workers;
-   separar filas;
-   aumentar capacidade Redis;
-   particionar responsabilidades.

------------------------------------------------------------------------

# 73. Alta Disponibilidade

HA deverá ser avaliada conforme papel da instância.

Um Redis usado apenas para cache possui impacto diferente de um broker
central de processamento.

------------------------------------------------------------------------

# 74. Backup

Backup de Redis somente será necessário conforme a durabilidade exigida
pelo uso.

Nunca considerar backup de cache requisito automático.

------------------------------------------------------------------------

# 75. Recuperação

Após falha:

-   validar disponibilidade;
-   verificar perda de mensagens/estado;
-   avaliar backlog;
-   subir workers controladamente;
-   monitorar banco e integrações.

------------------------------------------------------------------------

# 76. Deploy

Mudanças em nomes de filas, formatos de mensagens e chaves deverão
considerar coexistência entre releases.

------------------------------------------------------------------------

# 77. Mudanças de Estrutura

Para mensagens:

``` text
producer N+1
+
consumer N
```

poderão coexistir durante deploy.

Payloads deverão ser compatíveis ou versionados quando necessário.

------------------------------------------------------------------------

# 78. Segurança

Aplicar:

-   rede privada;
-   autenticação;
-   TLS quando necessário;
-   menor privilégio;
-   secrets protegidos;
-   dados mínimos.

------------------------------------------------------------------------

# 79. LGPD

Cache e filas também processam dados pessoais.

Aplicar:

-   minimização;
-   TTL;
-   proteção;
-   descarte;
-   não registrar conteúdo sensível desnecessariamente.

------------------------------------------------------------------------

# 80. Testes

Testar:

-   cache hit/miss;
-   invalidação;
-   tenant;
-   TTL;
-   retry;
-   idempotência;
-   duplicidade;
-   falha do Redis;
-   fila acumulada;
-   poison message.

------------------------------------------------------------------------

# 81. Desenvolvimento

Development deverá utilizar Redis/broker isolado.

Deverá ser fácil limpar estado local sem afetar outros ambientes.

------------------------------------------------------------------------

# 82. Staging

Staging deverá validar:

-   filas reais;
-   workers;
-   scheduler;
-   retries;
-   observabilidade;
-   falhas controladas.

------------------------------------------------------------------------

# 83. Produção

Produção deverá possuir:

-   Redis privado;
-   credenciais próprias;
-   monitoramento;
-   limites;
-   alertas;
-   owner;
-   capacidade conhecida.

------------------------------------------------------------------------

# 84. Anti-Padrões

Evitar:

``` text
Redis público
```

------------------------------------------------------------------------

``` text
cache key
sem tenant
para dado multi-tenant
```

------------------------------------------------------------------------

``` text
lock
sem TTL
```

------------------------------------------------------------------------

``` text
task
com objeto inteiro sensível
quando IDs bastam
```

------------------------------------------------------------------------

``` text
retry infinito
```

------------------------------------------------------------------------

``` text
fila crítica
misturada com relatório pesado
sem necessidade
```

------------------------------------------------------------------------

``` text
estado financeiro
existindo apenas no Redis
```

------------------------------------------------------------------------

``` text
cache sem estratégia
de invalidação
```

------------------------------------------------------------------------

``` text
autoscaling de workers
sem considerar banco
```

------------------------------------------------------------------------

# 85. Arquitetura de Referência

``` text
                    DJANGO WEB
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
        CACHE       RATE LIMIT    IDEMPOTENCY
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                  ┌───────────┐
                  │   REDIS   │
                  │  PRIVATE  │
                  └─────┬─────┘
                        │
                        ▼
                   QUEUE/BROKER
                        │
            ┌───────────┼───────────┐
            ▼           ▼           ▼
         WORKER      WORKER      WORKER
         critical    reports   integrations
            │           │           │
            └───────────┼───────────┘
                        ▼
                    POSTGRESQL

Fonte autoritativa de negócio:
PostgreSQL

Aceleração/coordenação:
Redis
```

------------------------------------------------------------------------

# 86. Checklist

## Infraestrutura

-   [ ] Redis privado;
-   [ ] ambientes separados;
-   [ ] autenticação;
-   [ ] secrets protegidos;
-   [ ] timeouts.

## Cache

-   [ ] fonte autoritativa conhecida;
-   [ ] tenant na chave;
-   [ ] TTL;
-   [ ] invalidação;
-   [ ] eviction compreendida.

## Filas

-   [ ] filas com finalidade;
-   [ ] payload mínimo;
-   [ ] tenant explícito;
-   [ ] retries limitados;
-   [ ] backoff;
-   [ ] poison messages tratadas.

## Workers

-   [ ] concorrência dimensionada;
-   [ ] banco considerado;
-   [ ] idempotência;
-   [ ] timeout;
-   [ ] scheduler controlado.

## Observabilidade

-   [ ] memória;
-   [ ] evictions;
-   [ ] cache hit/miss;
-   [ ] queue depth;
-   [ ] queue age;
-   [ ] failures;
-   [ ] retries;
-   [ ] alertas.

## Segurança e Privacidade

-   [ ] sem exposição pública;
-   [ ] sem secrets em logs;
-   [ ] dados mínimos;
-   [ ] TTL para dados transitórios;
-   [ ] isolamento multi-tenant.

------------------------------------------------------------------------

# 87. Documentos Relacionados

-   GINF-01 --- Arquitetura da Infraestrutura
-   GINF-02 --- Ambientes e Configuração
-   GINF-03 --- Rede, DNS, Proxy e TLS
-   GINF-04 --- Runtime Django e Workers
-   GINF-05 --- Banco de Dados e Persistência
-   GSF-05 --- Segurança Multi-Tenant
-   GSF-08 --- Segurança de Dados e Privacidade
-   GSF-09 --- Gestão de Segredos e Criptografia
-   GSF-10 --- Logging, Monitoramento e Auditoria
-   GAPI-08 --- Webhooks e Integrações
-   GAPI-09 --- Idempotência e Rate Limiting
-   GAPI-11 --- Logging, Monitoramento e Auditoria
-   GOC --- GereIgreja Operations Center
-   GQF --- GereIgreja Quality Framework
-   GereIgreja Backend Engineering

------------------------------------------------------------------------

# 88. Princípios Finais

Redis deverá ser utilizado porque existe uma necessidade clara, não
porque está disponível.

O princípio central é:

``` text
PostgreSQL
preserva a verdade do negócio.

Redis
acelera, coordena
e transporta trabalho.
```

E, em ambiente multi-tenant:

``` text
Toda chave compartilhada
que representa dado de uma igreja
deve preservar o tenant.
```

Filas deverão ser tratadas como sistemas sujeitos a duplicidade, atraso
e falha. Workers deverão ser idempotentes e observáveis.

O GereIgreja não deverá transformar componentes efêmeros em dependências
permanentes invisíveis.

------------------------------------------------------------------------

# 89. Status do Documento

**Pasta**

`docs/infraestrutura/`

**Arquivo**

`06-Redis-Cache-e-Filas.md`

**Documento**

`GINF-06`

**Código**

`GINF-REDIS-CACHE-QUEUES`

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

`GINF-05 — Banco de Dados e Persistência`

**Próximo documento recomendado**

`07-Storage-e-Arquivos.md`
