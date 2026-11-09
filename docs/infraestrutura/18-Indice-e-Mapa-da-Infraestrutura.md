Pasta:

docs/infraestrutura/

Arquivo:

18-Indice-e-Mapa-da-Infraestrutura.md

Documento:

GINF-18

Código:

GINF-INDEX-INFRASTRUCTURE-MAP

Família:

GINF --- GereIgreja Infrastructure Engineering

Frameworks relacionados:

GEA --- GereIgreja Enterprise Architecture GSF --- GereIgreja Security
Framework GOC --- GereIgreja Operations Center GQF --- GereIgreja
Quality Framework GDF --- GereIgreja Documentation Framework

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GINF-18 --- Índice e Mapa da Infraestrutura

> "Uma arquitetura bem documentada precisa permitir que qualquer
> engenheiro descubra rapidamente onde está cada responsabilidade, qual
> documento governa cada decisão e como os componentes se relacionam."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Papel deste Documento
4.  Família GINF
5.  Mapa Geral
6.  GINF-01 --- Arquitetura da Infraestrutura
7.  GINF-02 --- Ambientes e Configuração
8.  GINF-03 --- Rede, DNS, Proxy e TLS
9.  GINF-04 --- Runtime Django e Workers
10. GINF-05 --- Banco de Dados e Persistência
11. GINF-06 --- Redis, Cache e Filas
12. GINF-07 --- Storage e Arquivos
13. GINF-08 --- Containers, Imagens e Registry
14. GINF-09 --- CI/CD, Deploy e Rollback
15. GINF-10 --- Observabilidade, Logs, Métricas e Alertas
16. GINF-11 --- Backup, Restore e Disaster Recovery
17. GINF-12 --- Infraestrutura como Código e Automação
18. GINF-13 --- Escalabilidade, Alta Disponibilidade e Capacidade
19. GINF-14 --- Custos, FinOps e Governança de Recursos
20. GINF-15 --- Operação, Manutenção e Runbooks
21. GINF-16 --- Governança, Padrões e Evolução
22. GINF-17 --- Checklist de Produção e Prontidão Operacional
23. Fluxo de Leitura
24. Mapa por Responsabilidade
25. Mapa por Componente
26. Mapa por Fase do Ciclo de Vida
27. Mapa de Segurança
28. Mapa de Operação
29. Mapa de Recuperação
30. Mapa de Deploy
31. Mapa de Dados
32. Mapa de Observabilidade
33. Mapa de Escalabilidade
34. Mapa de Governança
35. Relação com GEA
36. Relação com GSF
37. Relação com GOC
38. Relação com GQF
39. Relação com GDF
40. Relação com Backend Engineering
41. Relação com Frontend Engineering
42. Ordem Recomendada para Novos Engenheiros
43. Ordem Recomendada para Novos Serviços
44. Ordem Recomendada para Incidentes
45. Ordem Recomendada para Mudanças de Infraestrutura
46. Ordem Recomendada para Production Readiness
47. Matriz de Documentos
48. Regras de Evolução da Família
49. Convenções
50. Checklist de Integridade
51. Documentos Relacionados
52. Princípios Finais
53. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento constitui o índice oficial e o mapa de navegação da
família GINF --- GereIgreja Infrastructure Engineering.

Seu objetivo é permitir que a equipe identifique rapidamente:

-   qual documento consultar;
-   onde cada responsabilidade está definida;
-   como os documentos se relacionam;
-   qual sequência utilizar em diferentes cenários;
-   quais áreas da infraestrutura possuem norma oficial.

------------------------------------------------------------------------

# 2. Escopo

Este documento cobre toda a família:

``` text
GINF-01
até
GINF-17
```

Ele não substitui os documentos especializados.

Sua função é conectá-los.

------------------------------------------------------------------------

# 3. Papel deste Documento

O GINF-18 funciona como:

``` text
Índice
+
Mapa
+
Roteador documental
+
Visão consolidada
```

Quando houver dúvida sobre onde uma regra de infraestrutura está
definida, este deverá ser o primeiro documento consultado.

------------------------------------------------------------------------

# 4. Família GINF

A família oficial é composta por:

``` text
GINF-01  Arquitetura
GINF-02  Ambientes e Configuração
GINF-03  Rede, DNS, Proxy e TLS
GINF-04  Runtime Django e Workers
GINF-05  Banco de Dados e Persistência
GINF-06  Redis, Cache e Filas
GINF-07  Storage e Arquivos
GINF-08  Containers, Imagens e Registry
GINF-09  CI/CD, Deploy e Rollback
GINF-10  Observabilidade
GINF-11  Backup, Restore e DR
GINF-12  IaC e Automação
GINF-13  Escalabilidade e HA
GINF-14  FinOps
GINF-15  Operação e Runbooks
GINF-16  Governança
GINF-17  Production Readiness
GINF-18  Índice e Mapa
```

------------------------------------------------------------------------

# 5. Mapa Geral

``` text
                         GINF-01
                  ARQUITETURA GERAL
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
    GINF-02           GINF-03           GINF-04
 Ambientes/Config    Rede/TLS       Runtime/Workers
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           GINF-05    GINF-06    GINF-07
             DB      Redis/Filas Storage
              └──────────┼──────────┘
                         ▼
                      GINF-08
               Containers/Registry
                         │
                         ▼
                      GINF-09
                   CI/CD/Deploy
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           GINF-10    GINF-11    GINF-12
        Observability Backup/DR   IaC
              │          │          │
              └──────────┼──────────┘
                         ▼
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           GINF-13    GINF-14    GINF-15
          Scale/HA     FinOps    Operations
              └──────────┼──────────┘
                         ▼
                      GINF-16
                    Governance
                         │
                         ▼
                      GINF-17
               Production Readiness
                         │
                         ▼
                      GINF-18
                  Index / Map
```

------------------------------------------------------------------------

# 6. GINF-01 --- Arquitetura da Infraestrutura

Documento de entrada da família.

Define a visão estrutural da infraestrutura e seus principais
componentes.

Consultar quando a pergunta for:

``` text
"Como a infraestrutura
do GereIgreja está organizada?"
```

------------------------------------------------------------------------

# 7. GINF-02 --- Ambientes e Configuração

Define:

-   development;
-   staging;
-   production;
-   variáveis;
-   configuração;
-   separação de ambientes.

Consultar para decisões sobre configuração e isolamento.

------------------------------------------------------------------------

# 8. GINF-03 --- Rede, DNS, Proxy e TLS

Define padrões de:

-   rede;
-   exposição;
-   DNS;
-   proxy;
-   HTTPS;
-   TLS.

Consultar para entrada e comunicação de rede.

------------------------------------------------------------------------

# 9. GINF-04 --- Runtime Django e Workers

Define execução de:

-   Django;
-   processos web;
-   workers;
-   scheduler;
-   lifecycle de processos.

------------------------------------------------------------------------

# 10. GINF-05 --- Banco de Dados e Persistência

Documento principal para:

-   PostgreSQL;
-   conexões;
-   migrations;
-   índices;
-   persistência;
-   operação do banco.

------------------------------------------------------------------------

# 11. GINF-06 --- Redis, Cache e Filas

Define uso de:

-   Redis;
-   cache;
-   filas;
-   processamento assíncrono;
-   retries;
-   workers relacionados.

------------------------------------------------------------------------

# 12. GINF-07 --- Storage e Arquivos

Define:

-   uploads;
-   arquivos;
-   object storage;
-   lifecycle;
-   segurança de storage;
-   retenção relacionada.

------------------------------------------------------------------------

# 13. GINF-08 --- Containers, Imagens e Registry

Define:

-   construção de imagens;
-   containers;
-   tags;
-   registry;
-   segurança de imagens;
-   lifecycle.

------------------------------------------------------------------------

# 14. GINF-09 --- CI/CD, Deploy e Rollback

Documento principal do fluxo de entrega.

``` text
Commit
→ Pipeline
→ Build
→ Test
→ Deploy
→ Validate
→ Rollback quando necessário
```

------------------------------------------------------------------------

# 15. GINF-10 --- Observabilidade, Logs, Métricas e Alertas

Define como enxergar o comportamento da infraestrutura.

Abrange:

-   logs;
-   métricas;
-   alertas;
-   dashboards;
-   health signals.

------------------------------------------------------------------------

# 16. GINF-11 --- Backup, Restore e Disaster Recovery

Documento de recuperabilidade.

Define:

-   backup;
-   retenção;
-   restore;
-   testes;
-   RPO;
-   RTO;
-   disaster recovery.

------------------------------------------------------------------------

# 17. GINF-12 --- Infraestrutura como Código e Automação

Define:

-   IaC;
-   state;
-   plan;
-   apply;
-   drift;
-   automação operacional;
-   policy as code.

------------------------------------------------------------------------

# 18. GINF-13 --- Escalabilidade, Alta Disponibilidade e Capacidade

Define como a infraestrutura cresce e mantém disponibilidade.

Abrange:

-   escala vertical;
-   escala horizontal;
-   HA;
-   capacity planning;
-   autoscaling;
-   resiliência.

------------------------------------------------------------------------

# 19. GINF-14 --- Custos, FinOps e Governança de Recursos

Define:

-   visibilidade de custos;
-   ownership financeiro;
-   rightsizing;
-   budgets;
-   forecast;
-   otimização;
-   recursos órfãos.

------------------------------------------------------------------------

# 20. GINF-15 --- Operação, Manutenção e Runbooks

Documento principal para operação humana e automatizada.

Define:

-   manutenção;
-   mudanças;
-   runbooks;
-   rotinas;
-   escalonamento;
-   procedimentos operacionais.

------------------------------------------------------------------------

# 21. GINF-16 --- Governança, Padrões e Evolução

Define como a família GINF e a infraestrutura evoluem.

Abrange:

-   padrões;
-   exceções;
-   ADRs;
-   RFCs;
-   lifecycle;
-   dívida técnica;
-   roadmap.

------------------------------------------------------------------------

# 22. GINF-17 --- Checklist de Produção e Prontidão Operacional

É a barreira final antes de considerar um serviço pronto para
production.

Integra requisitos dos demais documentos em um checklist operacional.

------------------------------------------------------------------------

# 23. Fluxo de Leitura

Para compreender toda a infraestrutura:

``` text
GINF-01
   ↓
GINF-02
   ↓
GINF-03
   ↓
GINF-04
   ↓
GINF-05 / 06 / 07
   ↓
GINF-08
   ↓
GINF-09
   ↓
GINF-10 / 11 / 12
   ↓
GINF-13 / 14 / 15
   ↓
GINF-16
   ↓
GINF-17
```

GINF-18 poderá ser consultado a qualquer momento como mapa.

------------------------------------------------------------------------

# 24. Mapa por Responsabilidade

``` text
Arquitetura            → GINF-01
Ambientes              → GINF-02
Rede                   → GINF-03
Runtime                → GINF-04
Banco                  → GINF-05
Redis / Filas          → GINF-06
Storage                → GINF-07
Containers             → GINF-08
Deploy                 → GINF-09
Observabilidade        → GINF-10
Backup / DR            → GINF-11
IaC                    → GINF-12
Escala / HA            → GINF-13
Custos                 → GINF-14
Operação               → GINF-15
Governança             → GINF-16
Production Readiness   → GINF-17
Índice                  → GINF-18
```

------------------------------------------------------------------------

# 25. Mapa por Componente

## Django

``` text
GINF-02
GINF-04
GINF-09
GINF-10
GINF-13
GINF-17
```

## PostgreSQL

``` text
GINF-05
GINF-10
GINF-11
GINF-13
GINF-15
GINF-17
```

## Redis

``` text
GINF-06
GINF-10
GINF-13
GINF-15
GINF-17
```

## Storage

``` text
GINF-07
GINF-10
GINF-11
GINF-14
GINF-17
```

## Containers

``` text
GINF-08
GINF-09
GINF-12
GINF-13
GINF-17
```

------------------------------------------------------------------------

# 26. Mapa por Fase do Ciclo de Vida

## Design

``` text
GINF-01
GINF-02
GINF-03
GINF-13
GINF-16
```

## Build

``` text
GINF-08
GINF-12
```

## Deploy

``` text
GINF-09
GINF-17
```

## Operate

``` text
GINF-10
GINF-14
GINF-15
```

## Recover

``` text
GINF-11
GINF-15
```

## Evolve

``` text
GINF-13
GINF-14
GINF-16
```

------------------------------------------------------------------------

# 27. Mapa de Segurança

Segurança de infraestrutura deverá combinar:

``` text
GSF
 │
 ├── GINF-02  configuração
 ├── GINF-03  rede/TLS
 ├── GINF-05  dados
 ├── GINF-07  arquivos
 ├── GINF-08  imagens
 ├── GINF-09  pipeline
 ├── GINF-10  logs
 ├── GINF-11  backups
 ├── GINF-12  IaC
 ├── GINF-15  operação
 └── GINF-17  readiness
```

------------------------------------------------------------------------

# 28. Mapa de Operação

``` text
GINF-10
Observabilidade
    │
    ▼
GINF-15
Operação / Runbooks
    │
    ├──► GOC
    │
    ├──► GSF-13
    │
    └──► GINF-11
          Recuperação
```

------------------------------------------------------------------------

# 29. Mapa de Recuperação

``` text
Falha
 │
 ▼
Detecção
GINF-10
 │
 ▼
Resposta
GINF-15 / GOC
 │
 ▼
Restore / DR
GINF-11
 │
 ▼
Validação
GINF-17
 │
 ▼
Melhoria
GINF-16
```

------------------------------------------------------------------------

# 30. Mapa de Deploy

``` text
Código
 │
 ▼
GINF-08
Imagem
 │
 ▼
GINF-09
CI/CD
 │
 ▼
GINF-12
Infraestrutura
 │
 ▼
Production
 │
 ▼
GINF-10
Observabilidade
```

------------------------------------------------------------------------

# 31. Mapa de Dados

``` text
Aplicação
   │
   ├──► PostgreSQL → GINF-05
   ├──► Redis      → GINF-06
   └──► Storage    → GINF-07
                      │
                      ▼
                 GINF-11
               Backup / DR
```

------------------------------------------------------------------------

# 32. Mapa de Observabilidade

``` text
Web
Workers
DB
Redis
Storage
Network
   │
   ▼
GINF-10
   │
   ├── Logs
   ├── Metrics
   ├── Alerts
   └── Dashboards
        │
        ▼
      GOC
```

------------------------------------------------------------------------

# 33. Mapa de Escalabilidade

``` text
Demanda
  │
  ▼
Métricas
GINF-10
  │
  ▼
Capacity Planning
GINF-13
  │
  ├── Web
  ├── Workers
  ├── DB
  ├── Redis
  └── Storage
       │
       ▼
Custos
GINF-14
```

------------------------------------------------------------------------

# 34. Mapa de Governança

``` text
GEA
 │
 ▼
GINF-16
 │
 ├── Padrões
 ├── Decisões
 ├── Exceções
 ├── Lifecycle
 └── Roadmap
      │
      ▼
GINF-12 / GINF-15
Implementação e Operação
```

------------------------------------------------------------------------

# 35. Relação com GEA

GEA define arquitetura empresarial e princípios arquiteturais
superiores.

GINF detalha a camada de infraestrutura.

Em conflito normativo, decisões deverão ser reconciliadas com a
arquitetura superior.

------------------------------------------------------------------------

# 36. Relação com GSF

GSF define os controles oficiais de segurança.

GINF implementa esses controles na infraestrutura.

------------------------------------------------------------------------

# 37. Relação com GOC

GOC coordena operação e resposta.

GINF define como os componentes de infraestrutura devem ser operados e
observados.

------------------------------------------------------------------------

# 38. Relação com GQF

GQF define critérios de qualidade.

GINF traduz parte desses critérios para infraestrutura, deploy,
disponibilidade e operação.

------------------------------------------------------------------------

# 39. Relação com GDF

GDF governa documentação.

A família GINF deverá seguir padrões documentais oficiais.

------------------------------------------------------------------------

# 40. Relação com Backend Engineering

Backend Engineering define como a aplicação é construída.

GINF define o ambiente em que ela é executada.

A fronteira deverá permanecer clara:

``` text
Aplicação
→ Backend Engineering

Infraestrutura
→ GINF
```

Há pontos de integração em runtime, banco, cache, filas, observabilidade
e deploy.

------------------------------------------------------------------------

# 41. Relação com Frontend Engineering

Frontend Engineering governa a camada de interface e seus artefatos.

GINF participa quando houver:

-   build;
-   entrega;
-   CDN/storage;
-   headers;
-   TLS;
-   observabilidade;
-   pipeline.

------------------------------------------------------------------------

# 42. Ordem Recomendada para Novos Engenheiros

``` text
1. GINF-18
2. GINF-01
3. GINF-02
4. GINF-09
5. GINF-10
6. GINF-15
7. documentos específicos da área
```

------------------------------------------------------------------------

# 43. Ordem Recomendada para Novos Serviços

``` text
GINF-01
→ GINF-02
→ GINF-03
→ GINF-04
→ GINF-05/06/07
→ GINF-08
→ GINF-09
→ GINF-10
→ GINF-11
→ GINF-12
→ GINF-13
→ GINF-14
→ GINF-15
→ GINF-17
```

------------------------------------------------------------------------

# 44. Ordem Recomendada para Incidentes

``` text
GINF-10
→ GINF-15
→ GOC
→ GSF-13 quando segurança
→ GINF-11 quando recuperação
→ GINF-16 para melhoria estrutural
```

------------------------------------------------------------------------

# 45. Ordem Recomendada para Mudanças de Infraestrutura

``` text
GINF-16
Governança
   ↓
GINF-12
IaC
   ↓
GINF-09
Pipeline
   ↓
GINF-15
Operação
   ↓
GINF-10
Validação
```

------------------------------------------------------------------------

# 46. Ordem Recomendada para Production Readiness

``` text
GINF-17
   │
   ├── arquitetura → GINF-01
   ├── config      → GINF-02
   ├── rede        → GINF-03
   ├── runtime     → GINF-04
   ├── dados       → GINF-05/06/07
   ├── container   → GINF-08
   ├── deploy      → GINF-09
   ├── observe     → GINF-10
   ├── recover     → GINF-11
   ├── IaC         → GINF-12
   ├── scale       → GINF-13
   ├── cost        → GINF-14
   ├── operate     → GINF-15
   └── govern      → GINF-16
```

------------------------------------------------------------------------

# 47. Matriz de Documentos

  Área              Documento principal   Documentos complementares
  ----------------- --------------------- ------------------------------
  Arquitetura       GINF-01               GEA, GINF-16
  Ambientes         GINF-02               GSF, GINF-12
  Rede/TLS          GINF-03               GSF, GINF-10
  Runtime           GINF-04               Backend Engineering, GINF-13
  Banco             GINF-05               GINF-10, GINF-11
  Redis/Filas       GINF-06               GINF-10, GINF-13
  Storage           GINF-07               GSF, GINF-11
  Containers        GINF-08               GSF, GINF-09
  Deploy            GINF-09               GQF, GINF-17
  Observabilidade   GINF-10               GOC, GSF
  Backup/DR         GINF-11               GOC, GSF
  IaC               GINF-12               GSF, GINF-16
  Escala/HA         GINF-13               GINF-10, GINF-14
  FinOps            GINF-14               GINF-13, GINF-16
  Operação          GINF-15               GOC, GINF-10
  Governança        GINF-16               GEA, GDF
  Readiness         GINF-17               Toda família GINF
  Índice            GINF-18               Toda família GINF

------------------------------------------------------------------------

# 48. Regras de Evolução da Família

Novos documentos GINF somente deverão ser criados quando:

-   existir domínio relevante não coberto;
-   o conteúdo justificar documento próprio;
-   a separação melhorar governança;
-   não houver duplicação desnecessária.

Antes de criar novo documento, verificar se o tema deve ser incorporado
a um GINF existente.

------------------------------------------------------------------------

# 49. Convenções

A família deverá preservar:

``` text
NN-Nome-do-Documento.md
```

com metadados contendo:

-   pasta;
-   arquivo;
-   documento;
-   código;
-   família;
-   versão;
-   status;
-   responsável;
-   atualização.

Referências cruzadas deverão utilizar códigos oficiais.

------------------------------------------------------------------------

# 50. Checklist de Integridade

## Família

-   [ ] GINF-01 presente;
-   [ ] GINF-02 presente;
-   [ ] GINF-03 presente;
-   [ ] GINF-04 presente;
-   [ ] GINF-05 presente;
-   [ ] GINF-06 presente;
-   [ ] GINF-07 presente;
-   [ ] GINF-08 presente;
-   [ ] GINF-09 presente;
-   [ ] GINF-10 presente;
-   [ ] GINF-11 presente;
-   [ ] GINF-12 presente;
-   [ ] GINF-13 presente;
-   [ ] GINF-14 presente;
-   [ ] GINF-15 presente;
-   [ ] GINF-16 presente;
-   [ ] GINF-17 presente;
-   [ ] GINF-18 presente.

## Consistência

-   [ ] códigos únicos;
-   [ ] nomes consistentes;
-   [ ] referências cruzadas válidas;
-   [ ] versões registradas;
-   [ ] status registrado;
-   [ ] owner registrado;
-   [ ] documentos relacionados atualizados.

## Cobertura

-   [ ] arquitetura;
-   [ ] ambientes;
-   [ ] rede;
-   [ ] runtime;
-   [ ] dados;
-   [ ] cache/filas;
-   [ ] storage;
-   [ ] containers;
-   [ ] deploy;
-   [ ] observabilidade;
-   [ ] recuperação;
-   [ ] IaC;
-   [ ] escala;
-   [ ] custos;
-   [ ] operação;
-   [ ] governança;
-   [ ] readiness.

------------------------------------------------------------------------

# 51. Documentos Relacionados

## GereIgreja Infrastructure Engineering

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
-   GINF-13 --- Escalabilidade, Alta Disponibilidade e Capacidade
-   GINF-14 --- Custos, FinOps e Governança de Recursos
-   GINF-15 --- Operação, Manutenção e Runbooks de Infraestrutura
-   GINF-16 --- Governança, Padrões e Evolução da Infraestrutura
-   GINF-17 --- Checklist de Produção e Prontidão Operacional

## Frameworks e famílias relacionadas

-   GEA --- GereIgreja Enterprise Architecture
-   GSF --- GereIgreja Security Framework
-   GOC --- GereIgreja Operations Center
-   GQF --- GereIgreja Quality Framework
-   GDF --- GereIgreja Documentation Framework
-   GereIgreja Backend Engineering
-   GereIgreja Frontend Engineering

------------------------------------------------------------------------

# 52. Princípios Finais

A família GINF deverá funcionar como um sistema documental, e não como
uma coleção isolada de arquivos.

``` text
Arquitetura
→ Construção
→ Deploy
→ Observação
→ Operação
→ Recuperação
→ Escala
→ Governança
→ Evolução
```

O princípio central é:

``` text
Para cada responsabilidade
de infraestrutura,
deve existir um lugar
oficial para encontrá-la.
```

O GINF-18 é o mapa oficial dessa estrutura.

Ele deverá ser atualizado sempre que a família GINF receber novos
documentos, mudanças de nomenclatura ou alterações relevantes de
responsabilidade.

------------------------------------------------------------------------

# 53. Status do Documento

**Pasta**

`docs/infraestrutura/`

**Arquivo**

`18-Indice-e-Mapa-da-Infraestrutura.md`

**Documento**

`GINF-18`

**Código**

`GINF-INDEX-INFRASTRUCTURE-MAP`

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

`GINF-17 — Checklist de Produção e Prontidão Operacional`

**Posição na família**

`Documento de índice, navegação e consolidação da família GINF`

**Próxima ação recomendada**

`Revisar a família GINF completa antes de criar novos documentos, identificando lacunas reais e evitando duplicação normativa.`
