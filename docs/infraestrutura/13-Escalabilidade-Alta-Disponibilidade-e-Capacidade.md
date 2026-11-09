Pasta:

docs/infraestrutura/

Arquivo:

13-Escalabilidade-Alta-Disponibilidade-e-Capacidade.md

Documento:

GINF-13

Código:

GINF-SCALABILITY-HA-CAPACITY

Família:

GINF --- GereIgreja Infrastructure Engineering

Frameworks relacionados:

GEA --- GereIgreja Enterprise Architecture GSF --- GereIgreja Security
Framework GOC --- GereIgreja Operations Center GQF --- GereIgreja
Quality Framework GereIgreja Backend Engineering

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GINF-13 --- Escalabilidade, Alta Disponibilidade e Capacidade

> "Escalar não é adicionar recursos indiscriminadamente. É preservar
> desempenho, disponibilidade e previsibilidade à medida que a
> plataforma cresce."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com a Arquitetura
4.  Princípios Fundamentais
5.  Escalabilidade
6.  Escala Vertical
7.  Escala Horizontal
8.  Stateless
9.  Estado Persistente
10. Alta Disponibilidade
11. Redundância
12. Eliminação de Pontos Únicos de Falha
13. Capacidade
14. Planejamento de Capacidade
15. Baseline
16. Crescimento
17. Headroom
18. Saturação
19. Gargalos
20. Web
21. Workers
22. Scheduler
23. PostgreSQL
24. Conexões de Banco
25. Connection Pooling
26. Read Replicas
27. Redis
28. Filas
29. Storage
30. Rede
31. Proxy e Load Balancer
32. DNS
33. TLS
34. Integrações Externas
35. Rate Limiting
36. Backpressure
37. Cache
38. Processamento Assíncrono
39. Autoscaling
40. Métricas para Autoscaling
41. Limites Mínimos e Máximos
42. Scale Up
43. Scale Down
44. Cooldown
45. Warm-Up
46. Picos de Tráfego
47. Eventos Sazonais
48. Jobs Pesados
49. Isolamento de Workloads
50. Prioridades
51. Multi-Tenant
52. Noisy Neighbor
53. Quotas
54. Limites
55. Resiliência
56. Timeout
57. Retry
58. Circuit Breaker
59. Bulkhead
60. Graceful Degradation
61. Health Checks
62. Readiness
63. Liveness
64. Failover
65. Banco de Dados e Failover
66. Redis e Failover
67. Storage e Durabilidade
68. Zonas de Disponibilidade
69. Regiões
70. Multi-Region
71. Consistência
72. CAP e Trade-offs
73. RPO e RTO
74. Disaster Recovery
75. Deploy sem Indisponibilidade
76. Rolling Deploy
77. Compatibilidade entre Versões
78. Observabilidade
79. Métricas RED
80. Métricas USE
81. Latência
82. Throughput
83. Taxa de Erro
84. CPU
85. Memória
86. Disco
87. I/O
88. Conexões
89. Filas
90. SLO e SLI
91. Testes de Carga
92. Testes de Stress
93. Testes de Soak
94. Testes de Failover
95. Chaos Engineering
96. Capacity Reviews
97. Custos
98. Eficiência
99. Otimização Prematura
100. Crescimento Planejado
101. Desenvolvimento
102. Staging
103. Produção
104. Anti-Padrões
105. Arquitetura de Referência
106. Checklist
107. Documentos Relacionados
108. Princípios Finais
109. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece o padrão oficial para escalabilidade, alta
disponibilidade e planejamento de capacidade do GereIgreja.

Seu objetivo é garantir que o crescimento da plataforma ocorra com:

-   desempenho previsível;
-   resiliência;
-   capacidade suficiente;
-   custos controlados;
-   redução de pontos únicos de falha;
-   recuperação planejada.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   aplicações web;
-   APIs;
-   workers;
-   filas;
-   PostgreSQL;
-   Redis;
-   storage;
-   proxy;
-   rede;
-   integrações;
-   infraestrutura de produção.

------------------------------------------------------------------------

# 3. Relação com a Arquitetura

``` text
                    INTERNET
                       │
                       ▼
                LOAD BALANCER
                 / PROXY
                       │
              ┌────────┴────────┐
              ▼                 ▼
            WEB 1             WEB N
              │                 │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      PostgreSQL      Redis        Storage
                       │
                       ▼
                    Queues
                       │
              ┌────────┴────────┐
              ▼                 ▼
           Worker 1          Worker N
```

------------------------------------------------------------------------

# 4. Princípios Fundamentais

Aplicar:

-   medir antes de escalar;
-   stateless quando possível;
-   redundância proporcional ao risco;
-   capacidade com margem;
-   isolamento de workloads;
-   limites explícitos;
-   observabilidade;
-   testes;
-   simplicidade arquitetural.

------------------------------------------------------------------------

# 5. Escalabilidade

Escalabilidade é a capacidade de atender crescimento de carga sem
degradação descontrolada.

------------------------------------------------------------------------

# 6. Escala Vertical

Escala vertical aumenta recursos de uma instância:

``` text
mais CPU
mais memória
mais I/O
```

É simples, mas possui limites físicos e financeiros.

------------------------------------------------------------------------

# 7. Escala Horizontal

Escala horizontal aumenta número de instâncias.

``` text
1 web
→
N webs
```

Exige aplicação compatível.

------------------------------------------------------------------------

# 8. Stateless

Camada web deverá ser stateless sempre que possível.

Estado compartilhado deverá permanecer em serviços apropriados.

------------------------------------------------------------------------

# 9. Estado Persistente

Não armazenar estado crítico exclusivamente na memória ou filesystem de
uma instância web.

------------------------------------------------------------------------

# 10. Alta Disponibilidade

Alta disponibilidade reduz impacto de falhas individuais.

Não significa ausência absoluta de falhas.

------------------------------------------------------------------------

# 11. Redundância

Componentes críticos poderão possuir múltiplas instâncias quando o
requisito justificar.

------------------------------------------------------------------------

# 12. Eliminação de Pontos Únicos de Falha

Mapear:

``` text
proxy
web
database
redis
storage
DNS
network
```

e identificar quais falhas isoladas interrompem a plataforma.

------------------------------------------------------------------------

# 13. Capacidade

Capacidade é o volume de carga que o sistema suporta dentro dos
objetivos definidos.

------------------------------------------------------------------------

# 14. Planejamento de Capacidade

Deverá considerar:

-   usuários;
-   tenants;
-   requests;
-   jobs;
-   dados;
-   conexões;
-   storage;
-   crescimento.

------------------------------------------------------------------------

# 15. Baseline

Estabelecer comportamento normal.

Sem baseline, picos e degradações tornam-se difíceis de identificar.

------------------------------------------------------------------------

# 16. Crescimento

Acompanhar tendências, não apenas valores instantâneos.

------------------------------------------------------------------------

# 17. Headroom

Produção deverá possuir margem para absorver variações.

Operar permanentemente próximo de 100% reduz resiliência.

------------------------------------------------------------------------

# 18. Saturação

Saturação ocorre quando recurso não consegue atender demanda adicional.

------------------------------------------------------------------------

# 19. Gargalos

O gargalo poderá migrar entre camadas.

``` text
web
→ banco
→ Redis
→ storage
→ integração
```

Escalar apenas web pode não resolver.

------------------------------------------------------------------------

# 20. Web

Escala horizontal deverá ser preferida quando a aplicação for stateless
e a infraestrutura suportar.

------------------------------------------------------------------------

# 21. Workers

Workers deverão escalar conforme:

-   backlog;
-   idade da fila;
-   throughput;
-   duração das tasks.

------------------------------------------------------------------------

# 22. Scheduler

Scheduler normalmente não deverá escalar horizontalmente sem mecanismo
que impeça execução duplicada.

------------------------------------------------------------------------

# 23. PostgreSQL

Banco frequentemente será o componente mais sensível à escala.

Antes de adicionar complexidade:

-   otimizar queries;
-   criar índices adequados;
-   controlar conexões;
-   revisar transações.

------------------------------------------------------------------------

# 24. Conexões de Banco

Cada instância adicional pode aumentar conexões.

Planejar:

``` text
web processes
+
workers
+
jobs
+
admin
```

------------------------------------------------------------------------

# 25. Connection Pooling

Pooling poderá ser adotado quando necessário para controlar pressão
sobre PostgreSQL.

------------------------------------------------------------------------

# 26. Read Replicas

Réplicas de leitura poderão ser avaliadas quando leitura se tornar
gargalo real.

Não introduzir antes da necessidade.

------------------------------------------------------------------------

# 27. Redis

Monitorar:

-   memória;
-   throughput;
-   conexões;
-   latência;
-   evictions.

------------------------------------------------------------------------

# 28. Filas

Fila é mecanismo de absorção de picos, mas backlog ilimitado apenas
transfere o problema.

------------------------------------------------------------------------

# 29. Storage

Storage deverá escalar independentemente das instâncias da aplicação.

Aplicar GINF-07.

------------------------------------------------------------------------

# 30. Rede

Capacidade de rede deverá acompanhar tráfego e dependências.

------------------------------------------------------------------------

# 31. Proxy e Load Balancer

Deverá distribuir tráfego apenas para instâncias prontas.

------------------------------------------------------------------------

# 32. DNS

DNS deverá possuir disponibilidade adequada e TTL compatível com
estratégia de failover.

------------------------------------------------------------------------

# 33. TLS

Renovação e terminação TLS não deverão constituir gargalo ou ponto
operacional frágil.

------------------------------------------------------------------------

# 34. Integrações Externas

Escala interna não elimina limites externos.

Considerar:

-   quotas;
-   rate limits;
-   latência;
-   indisponibilidade.

------------------------------------------------------------------------

# 35. Rate Limiting

Rate limiting protege recursos compartilhados e integrações.

------------------------------------------------------------------------

# 36. Backpressure

Quando downstream está saturado, upstream deverá reduzir pressão quando
possível.

------------------------------------------------------------------------

# 37. Cache

Cache poderá reduzir carga em recursos caros.

Aplicar GINF-06.

------------------------------------------------------------------------

# 38. Processamento Assíncrono

Operações pesadas deverão ser movidas para workers quando apropriado.

------------------------------------------------------------------------

# 39. Autoscaling

Autoscaling poderá ajustar capacidade automaticamente.

Deverá ser baseado em sinais confiáveis.

------------------------------------------------------------------------

# 40. Métricas para Autoscaling

Possíveis sinais:

-   CPU;
-   memória;
-   requests;
-   latência;
-   queue depth;
-   queue age.

------------------------------------------------------------------------

# 41. Limites Mínimos e Máximos

Autoscaling deverá possuir limites.

Sem máximo, falha pode transformar-se em crescimento descontrolado de
custo.

------------------------------------------------------------------------

# 42. Scale Up

Aumento de capacidade deverá ocorrer antes de saturação prolongada
quando possível.

------------------------------------------------------------------------

# 43. Scale Down

Redução deverá preservar margem e evitar oscilação.

------------------------------------------------------------------------

# 44. Cooldown

Após mudança de capacidade, aguardar tempo suficiente para avaliar
efeito.

------------------------------------------------------------------------

# 45. Warm-Up

Novas instâncias podem precisar de tempo para:

-   iniciar;
-   carregar código;
-   estabelecer conexões;
-   aquecer caches.

------------------------------------------------------------------------

# 46. Picos de Tráfego

Picos conhecidos deverão ser planejados antecipadamente.

------------------------------------------------------------------------

# 47. Eventos Sazonais

Eventos, campanhas, fechamentos financeiros ou períodos especiais
poderão gerar padrões diferentes de carga.

------------------------------------------------------------------------

# 48. Jobs Pesados

Jobs intensivos não deverão competir indiscriminadamente com tráfego
interativo.

------------------------------------------------------------------------

# 49. Isolamento de Workloads

Separar quando necessário:

``` text
web
workers rápidos
workers pesados
exports
integrações
```

------------------------------------------------------------------------

# 50. Prioridades

Filas poderão possuir prioridades distintas quando o domínio exigir.

------------------------------------------------------------------------

# 51. Multi-Tenant

Escalabilidade deverá preservar isolamento entre igrejas.

------------------------------------------------------------------------

# 52. Noisy Neighbor

Um tenant não deverá consumir recursos ilimitados prejudicando todos os
demais.

------------------------------------------------------------------------

# 53. Quotas

Quotas poderão ser aplicadas a recursos caros.

------------------------------------------------------------------------

# 54. Limites

Exemplos:

-   tamanho de upload;
-   exportações simultâneas;
-   requests;
-   jobs;
-   integrações.

------------------------------------------------------------------------

# 55. Resiliência

Escalabilidade sem resiliência pode apenas multiplicar falhas.

------------------------------------------------------------------------

# 56. Timeout

Toda chamada remota deverá possuir timeout apropriado.

------------------------------------------------------------------------

# 57. Retry

Retries deverão utilizar:

-   limite;
-   backoff;
-   jitter quando adequado;
-   idempotência.

------------------------------------------------------------------------

# 58. Circuit Breaker

Circuit breaker poderá ser adotado para dependências instáveis quando
necessário.

------------------------------------------------------------------------

# 59. Bulkhead

Separar pools ou filas reduz propagação de falhas entre workloads.

------------------------------------------------------------------------

# 60. Graceful Degradation

Em falha parcial, funcionalidades não críticas poderão degradar sem
derrubar toda a plataforma.

------------------------------------------------------------------------

# 61. Health Checks

Componentes deverão possuir checks úteis.

------------------------------------------------------------------------

# 62. Readiness

Instância só deverá receber tráfego quando pronta.

------------------------------------------------------------------------

# 63. Liveness

Runtime poderá reiniciar processo travado quando liveness indicar falha
real.

------------------------------------------------------------------------

# 64. Failover

Failover deverá ser conhecido e testado para componentes críticos.

------------------------------------------------------------------------

# 65. Banco de Dados e Failover

Failover do banco exige atenção a:

-   consistência;
-   DNS/endpoints;
-   conexões;
-   promoção;
-   split-brain.

Preferir capacidades gerenciadas e testadas quando disponíveis.

------------------------------------------------------------------------

# 66. Redis e Failover

A estratégia depende de sua criticidade.

Cache pode tolerar reconstrução; filas podem exigir controles
adicionais.

------------------------------------------------------------------------

# 67. Storage e Durabilidade

Utilizar mecanismos de durabilidade compatíveis com criticidade.

------------------------------------------------------------------------

# 68. Zonas de Disponibilidade

Distribuição entre zonas poderá reduzir impacto de falha localizada.

------------------------------------------------------------------------

# 69. Regiões

Região adicional aumenta resiliência, mas também complexidade e custo.

------------------------------------------------------------------------

# 70. Multi-Region

Multi-region não deverá ser adotado sem requisito claro.

Exige resolver:

-   dados;
-   consistência;
-   roteamento;
-   observabilidade;
-   deploy;
-   DR.

------------------------------------------------------------------------

# 71. Consistência

Escala distribuída exige decisões sobre consistência.

------------------------------------------------------------------------

# 72. CAP e Trade-offs

A arquitetura deverá reconhecer trade-offs de sistemas distribuídos sem
usar conceitos teóricos como justificativa para complexidade
desnecessária.

------------------------------------------------------------------------

# 73. RPO e RTO

Alta disponibilidade e DR deverão respeitar objetivos definidos no
GINF-11.

------------------------------------------------------------------------

# 74. Disaster Recovery

HA reduz algumas falhas.

DR trata eventos que ultrapassam mecanismos normais de redundância.

------------------------------------------------------------------------

# 75. Deploy sem Indisponibilidade

Aplicar GINF-09.

------------------------------------------------------------------------

# 76. Rolling Deploy

Exige capacidade suficiente para manter serviço enquanto instâncias são
substituídas.

------------------------------------------------------------------------

# 77. Compatibilidade entre Versões

Versões adjacentes podem coexistir temporariamente.

Banco, cache e filas deverão tolerar isso quando rolling deploy for
usado.

------------------------------------------------------------------------

# 78. Observabilidade

Toda decisão de capacidade deverá ser baseada em telemetria.

Aplicar GINF-10.

------------------------------------------------------------------------

# 79. Métricas RED

Para serviços:

``` text
Rate
Errors
Duration
```

------------------------------------------------------------------------

# 80. Métricas USE

Para recursos:

``` text
Utilization
Saturation
Errors
```

------------------------------------------------------------------------

# 81. Latência

Avaliar percentis, não apenas média.

------------------------------------------------------------------------

# 82. Throughput

Medir volume processado por unidade de tempo.

------------------------------------------------------------------------

# 83. Taxa de Erro

Escala não é saudável se throughput aumenta junto com falhas.

------------------------------------------------------------------------

# 84. CPU

CPU elevada pode indicar necessidade de escala ou ineficiência.

------------------------------------------------------------------------

# 85. Memória

Monitorar consumo, crescimento, OOM e pressão.

------------------------------------------------------------------------

# 86. Disco

Monitorar capacidade e crescimento antes de atingir limite.

------------------------------------------------------------------------

# 87. I/O

Banco e storage podem saturar por I/O antes de CPU.

------------------------------------------------------------------------

# 88. Conexões

Monitorar pools e limites de conexões.

------------------------------------------------------------------------

# 89. Filas

Queue age frequentemente é sinal mais útil que apenas número de
mensagens.

------------------------------------------------------------------------

# 90. SLO e SLI

Objetivos de serviço deverão orientar decisões de capacidade conforme
maturidade do GOC.

------------------------------------------------------------------------

# 91. Testes de Carga

Testes de carga deverão medir comportamento sob volume esperado.

------------------------------------------------------------------------

# 92. Testes de Stress

Stress testa além da carga esperada para identificar limites e modos de
falha.

------------------------------------------------------------------------

# 93. Testes de Soak

Soak tests verificam comportamento prolongado e possíveis vazamentos.

------------------------------------------------------------------------

# 94. Testes de Failover

Failover deverá ser testado em ambiente seguro.

------------------------------------------------------------------------

# 95. Chaos Engineering

Práticas de chaos poderão ser adotadas futuramente quando
observabilidade, automação e recuperação estiverem maduras.

------------------------------------------------------------------------

# 96. Capacity Reviews

Revisões periódicas deverão avaliar:

-   tendências;
-   limites;
-   custos;
-   crescimento;
-   incidentes;
-   previsões.

------------------------------------------------------------------------

# 97. Custos

Escalabilidade deverá considerar custo por unidade de carga.

------------------------------------------------------------------------

# 98. Eficiência

Antes de duplicar infraestrutura, verificar:

-   query lenta;
-   N+1;
-   cache;
-   processamento redundante;
-   payload excessivo;
-   job ineficiente.

------------------------------------------------------------------------

# 99. Otimização Prematura

Não criar arquitetura distribuída complexa para carga inexistente.

Escalar conforme evidência.

------------------------------------------------------------------------

# 100. Crescimento Planejado

Capacidade deverá ser revisada antes de:

-   grandes lançamentos;
-   migrações;
-   campanhas;
-   aumento relevante de tenants.

------------------------------------------------------------------------

# 101. Desenvolvimento

Development deverá permitir testes funcionais, mas não precisa
reproduzir toda redundância de production.

------------------------------------------------------------------------

# 102. Staging

Staging deverá permitir validar comportamento arquitetural relevante.

------------------------------------------------------------------------

# 103. Produção

Produção deverá possuir:

-   métricas;
-   alertas;
-   capacidade conhecida;
-   headroom;
-   estratégia de escala;
-   failover proporcional à criticidade.

------------------------------------------------------------------------

# 104. Anti-Padrões

Evitar:

``` text
CPU alta
→ adicionar servidor
sem investigar
```

------------------------------------------------------------------------

``` text
web horizontal
+
sessão em memória local
```

------------------------------------------------------------------------

``` text
autoscaling
sem limite máximo
```

------------------------------------------------------------------------

``` text
retry infinito
```

------------------------------------------------------------------------

``` text
fila crescendo
sem alerta
```

------------------------------------------------------------------------

``` text
um tenant
consumindo recursos
sem limite
```

------------------------------------------------------------------------

``` text
multi-region
sem necessidade real
```

------------------------------------------------------------------------

``` text
alta disponibilidade
sem teste de failover
```

------------------------------------------------------------------------

``` text
capacity planning
baseado apenas
em opinião
```

------------------------------------------------------------------------

# 105. Arquitetura de Referência

``` text
                         INTERNET
                            │
                            ▼
                    LOAD BALANCER
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
             WEB NODES               WEB NODES
                │                       │
                └───────────┬───────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
      POSTGRESQL           REDIS            STORAGE
          │                 │
          │                 ▼
          │               QUEUES
          │                 │
          │        ┌────────┴────────┐
          │        ▼                 ▼
          │     WORKER N          WORKER N
          │
          └─────────────────────────────────────┐
                                                ▼
                                      OBSERVABILITY
                                    Metrics / Alerts
                                                │
                                                ▼
                                      CAPACITY / SCALE

Backup e DR protegem contra
falhas além da alta disponibilidade.
```

------------------------------------------------------------------------

# 106. Checklist

## Arquitetura

-   [ ] web stateless;
-   [ ] persistência externa;
-   [ ] pontos únicos de falha identificados;
-   [ ] workloads isolados quando necessário.

## Capacidade

-   [ ] baseline conhecido;
-   [ ] tendências acompanhadas;
-   [ ] headroom;
-   [ ] limites;
-   [ ] capacidade de banco;
-   [ ] capacidade de filas.

## Escala

-   [ ] vertical/horizontal avaliadas;
-   [ ] autoscaling somente com sinais confiáveis;
-   [ ] mínimo/máximo definidos;
-   [ ] warm-up considerado;
-   [ ] scale down seguro.

## Resiliência

-   [ ] timeouts;
-   [ ] retries limitados;
-   [ ] backoff;
-   [ ] idempotência;
-   [ ] graceful degradation;
-   [ ] failover conhecido.

## Multi-Tenant

-   [ ] noisy neighbor avaliado;
-   [ ] quotas quando necessário;
-   [ ] recursos caros limitados;
-   [ ] isolamento preservado.

## Observabilidade

-   [ ] RED;
-   [ ] USE;
-   [ ] latência;
-   [ ] erros;
-   [ ] CPU/memória;
-   [ ] conexões;
-   [ ] queue age.

## Testes

-   [ ] carga;
-   [ ] stress quando necessário;
-   [ ] soak quando necessário;
-   [ ] failover;
-   [ ] capacidade revisada.

------------------------------------------------------------------------

# 107. Documentos Relacionados

-   GINF-01 --- Arquitetura da Infraestrutura
-   GINF-02 --- Ambientes e Configuração
-   GINF-03 --- Rede, DNS, Proxy e TLS
-   GINF-04 --- Runtime Django e Workers
-   GINF-05 --- Banco de Dados e Persistência
-   GINF-06 --- Redis, Cache e Filas
-   GINF-07 --- Storage e Arquivos
-   GINF-08 --- Containers, Imagens e Registry
-   GINF-09 --- CI/CD, Deploy e Rollback
-   GINF-10 --- Observabilidade, Logs, Métricas e Alertas
-   GINF-11 --- Backup, Restore e Disaster Recovery
-   GINF-12 --- Infraestrutura como Código e Automação
-   GSF --- GereIgreja Security Framework
-   GOC --- GereIgreja Operations Center
-   GQF --- GereIgreja Quality Framework
-   GereIgreja Backend Engineering

------------------------------------------------------------------------

# 108. Princípios Finais

O GereIgreja deverá escalar com base em evidências.

``` text
Medir
→ Entender
→ Otimizar
→ Escalar
→ Validar
```

O princípio central é:

``` text
Capacidade sem observabilidade
é adivinhação.

Escalabilidade sem limites
é risco.

Alta disponibilidade sem testes
é expectativa.
```

A arquitetura deverá permanecer simples enquanto simples for suficiente
e evoluir somente quando volume, disponibilidade ou risco justificarem a
complexidade adicional.

------------------------------------------------------------------------

# 109. Status do Documento

**Pasta**

`docs/infraestrutura/`

**Arquivo**

`13-Escalabilidade-Alta-Disponibilidade-e-Capacidade.md`

**Documento**

`GINF-13`

**Código**

`GINF-SCALABILITY-HA-CAPACITY`

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

`GINF-12 — Infraestrutura como Código e Automação`

**Próximo documento recomendado**

`14-Custos-FinOps-e-Governanca-de-Recursos.md`
