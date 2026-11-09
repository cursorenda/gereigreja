Pasta:

docs/infraestrutura/

Arquivo:

17-Checklist-de-Producao-e-Prontidao-Operacional.md

Documento:

GINF-17

Código:

GINF-PRODUCTION-READINESS

Família:

GINF --- GereIgreja Infrastructure Engineering

Frameworks relacionados:

GEA --- GereIgreja Enterprise Architecture GSF --- GereIgreja Security
Framework GOC --- GereIgreja Operations Center GQF --- GereIgreja
Quality Framework GDF --- GereIgreja Documentation Framework GINF ---
GereIgreja Infrastructure Engineering

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GINF-17 --- Checklist de Produção e Prontidão Operacional

> "Publicar não significa apenas colocar software no ar. Significa
> demonstrar que a plataforma pode operar, falhar, recuperar e evoluir
> com segurança."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Conceito de Production Readiness
4.  Princípios Fundamentais
5.  Quando Aplicar
6.  Responsabilidade
7.  Critérios de Aprovação
8.  Arquitetura
9.  Dependências
10. Ambientes
11. Configuração
12. Secrets
13. Rede
14. DNS
15. TLS
16. Runtime
17. Containers
18. Imagens
19. Registry
20. Banco de Dados
21. Migrations
22. Redis
23. Cache
24. Filas
25. Workers
26. Scheduler
27. Storage
28. Uploads
29. Segurança
30. Autenticação e Autorização
31. Vulnerabilidades
32. Dados e Privacidade
33. Observabilidade
34. Logs
35. Métricas
36. Alertas
37. Health Checks
38. Readiness
39. Liveness
40. Performance
41. Capacidade
42. Escalabilidade
43. Alta Disponibilidade
44. Limites
45. Rate Limiting
46. Timeouts
47. Retries
48. Idempotência
49. Backpressure
50. Backup
51. Restore
52. Disaster Recovery
53. RPO
54. RTO
55. Deploy
56. CI/CD
57. Rollback
58. Compatibilidade entre Versões
59. Infraestrutura como Código
60. Drift
61. Acesso Operacional
62. Menor Privilégio
63. Break Glass
64. Runbooks
65. Incidentes
66. Escalonamento
67. Comunicação
68. Custos
69. Ownership
70. Documentação
71. Compliance
72. Evidências
73. Testes Funcionais
74. Testes de Integração
75. Testes de Carga
76. Testes de Falha
77. Smoke Tests
78. Critérios Go/No-Go
79. Bloqueadores
80. Riscos Aceitos
81. Aprovação para Produção
82. Validação Pós-Deploy
83. Hypercare
84. Revisão Pós-Lançamento
85. Checklist Oficial
86. Template de Production Readiness Review
87. Anti-Padrões
88. Documentos Relacionados
89. Princípios Finais
90. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece o checklist oficial de prontidão para produção
da infraestrutura e dos serviços do GereIgreja.

Seu objetivo é impedir que sistemas sejam considerados prontos apenas
porque funcionam em ambiente de desenvolvimento.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   novos serviços;
-   novos módulos críticos;
-   mudanças arquiteturais relevantes;
-   novas integrações;
-   novos componentes de infraestrutura;
-   migrações;
-   mudanças de alta criticidade.

------------------------------------------------------------------------

# 3. Conceito de Production Readiness

Production Readiness é a comprovação de que uma solução está preparada
para operar em produção de forma segura e sustentável.

``` text
Funciona
≠
Está pronto para produção
```

------------------------------------------------------------------------

# 4. Princípios Fundamentais

Uma solução pronta para produção deverá ser:

-   segura;
-   observável;
-   operável;
-   recuperável;
-   escalável conforme necessidade;
-   documentada;
-   testada;
-   auditável.

------------------------------------------------------------------------

# 5. Quando Aplicar

O processo deverá ser aplicado proporcionalmente ao risco.

Mudanças pequenas poderão utilizar checklist simplificado.

Mudanças estruturais deverão passar por revisão completa.

------------------------------------------------------------------------

# 6. Responsabilidade

O owner técnico da mudança é responsável por garantir que os critérios
sejam avaliados.

A aprovação não transfere a responsabilidade técnica para o revisor.

------------------------------------------------------------------------

# 7. Critérios de Aprovação

Cada item deverá ser classificado como:

``` text
OK
N/A
PENDENTE
BLOQUEADOR
RISCO ACEITO
```

Itens `N/A` deverão possuir justificativa quando não forem evidentes.

------------------------------------------------------------------------

# 8. Arquitetura

Verificar:

-   arquitetura documentada;
-   componentes identificados;
-   fluxo de dados conhecido;
-   pontos críticos conhecidos;
-   decisões relevantes registradas.

------------------------------------------------------------------------

# 9. Dependências

Dependências internas e externas deverão ser conhecidas.

Avaliar falha de cada dependência relevante.

------------------------------------------------------------------------

# 10. Ambientes

Confirmar separação entre:

-   development;
-   staging;
-   production.

------------------------------------------------------------------------

# 11. Configuração

Configuração de production deverá ser explícita e reproduzível.

Aplicar GINF-02.

------------------------------------------------------------------------

# 12. Secrets

Confirmar:

-   ausência de secrets no código;
-   armazenamento seguro;
-   acesso restrito;
-   rotação quando aplicável.

Aplicar GSF-09.

------------------------------------------------------------------------

# 13. Rede

Validar exposição mínima necessária.

Aplicar GINF-03.

------------------------------------------------------------------------

# 14. DNS

Confirmar:

-   registros;
-   ownership;
-   TTL apropriado;
-   procedimento de alteração.

------------------------------------------------------------------------

# 15. TLS

HTTPS deverá ser obrigatório para tráfego externo aplicável.

Certificados deverão possuir renovação confiável.

------------------------------------------------------------------------

# 16. Runtime

Runtime deverá possuir configuração adequada de:

-   processos;
-   memória;
-   timeouts;
-   graceful shutdown.

------------------------------------------------------------------------

# 17. Containers

Aplicar GINF-08.

------------------------------------------------------------------------

# 18. Imagens

Confirmar:

-   versão identificável;
-   origem conhecida;
-   scan quando aplicável;
-   imagem sem secrets;
-   rollback possível.

------------------------------------------------------------------------

# 19. Registry

Confirmar acesso e retenção adequados.

------------------------------------------------------------------------

# 20. Banco de Dados

Avaliar:

-   capacidade;
-   conexões;
-   índices;
-   backups;
-   monitoramento;
-   segurança.

------------------------------------------------------------------------

# 21. Migrations

Migrations deverão ser:

-   revisadas;
-   compatíveis com estratégia de deploy;
-   testadas;
-   avaliadas quanto a locks e duração.

------------------------------------------------------------------------

# 22. Redis

Validar criticidade, memória, persistência quando aplicável e
comportamento em indisponibilidade.

------------------------------------------------------------------------

# 23. Cache

A perda do cache não deverá causar perda de dados persistentes.

------------------------------------------------------------------------

# 24. Filas

Avaliar:

-   backlog;
-   retry;
-   DLQ quando aplicável;
-   observabilidade;
-   reprocessamento.

------------------------------------------------------------------------

# 25. Workers

Workers deverão possuir:

-   health operacional;
-   logs;
-   limites;
-   comportamento de retry;
-   estratégia de escala.

------------------------------------------------------------------------

# 26. Scheduler

Garantir que jobs agendados não sejam duplicados indevidamente.

------------------------------------------------------------------------

# 27. Storage

Validar:

-   permissões;
-   durabilidade;
-   backup quando necessário;
-   lifecycle;
-   capacidade.

------------------------------------------------------------------------

# 28. Uploads

Aplicar limites, validações e controles de segurança adequados.

------------------------------------------------------------------------

# 29. Segurança

Executar revisão conforme GSF.

------------------------------------------------------------------------

# 30. Autenticação e Autorização

Confirmar que acessos seguem mecanismos oficiais e escopo correto.

------------------------------------------------------------------------

# 31. Vulnerabilidades

Dependências e imagens deverão estar dentro da política definida.

Vulnerabilidades críticas não aceitas deverão bloquear release.

------------------------------------------------------------------------

# 32. Dados e Privacidade

Confirmar tratamento adequado de dados pessoais, confidenciais e
sensíveis.

------------------------------------------------------------------------

# 33. Observabilidade

Aplicar GINF-10.

Serviço sem observabilidade suficiente não deverá ser considerado
operacionalmente pronto.

------------------------------------------------------------------------

# 34. Logs

Logs deverão permitir diagnóstico sem expor secrets ou dados indevidos.

------------------------------------------------------------------------

# 35. Métricas

Métricas deverão cobrir saúde e comportamento relevante.

------------------------------------------------------------------------

# 36. Alertas

Alertas críticos deverão possuir:

-   condição clara;
-   destino;
-   owner;
-   ação conhecida.

------------------------------------------------------------------------

# 37. Health Checks

Health checks deverão refletir estado real do serviço.

------------------------------------------------------------------------

# 38. Readiness

Instância não pronta não deverá receber tráfego.

------------------------------------------------------------------------

# 39. Liveness

Liveness não deverá provocar reinícios destrutivos por dependências
externas transitórias.

------------------------------------------------------------------------

# 40. Performance

Desempenho deverá ser compatível com os requisitos conhecidos.

------------------------------------------------------------------------

# 41. Capacidade

Aplicar GINF-13.

------------------------------------------------------------------------

# 42. Escalabilidade

Confirmar estratégia para crescimento esperado.

------------------------------------------------------------------------

# 43. Alta Disponibilidade

Redundância deverá ser proporcional à criticidade.

------------------------------------------------------------------------

# 44. Limites

Definir limites para recursos que possam crescer sem controle.

------------------------------------------------------------------------

# 45. Rate Limiting

Aplicar quando endpoints ou integrações exigirem proteção.

------------------------------------------------------------------------

# 46. Timeouts

Toda dependência remota deverá possuir timeout adequado.

------------------------------------------------------------------------

# 47. Retries

Retries deverão ser limitados e utilizar backoff quando apropriado.

------------------------------------------------------------------------

# 48. Idempotência

Operações sujeitas a retry deverão ser idempotentes quando possível.

------------------------------------------------------------------------

# 49. Backpressure

O sistema deverá possuir comportamento conhecido quando downstream
estiver saturado.

------------------------------------------------------------------------

# 50. Backup

Aplicar GINF-11.

Backup crítico deverá estar ativo antes do go-live.

------------------------------------------------------------------------

# 51. Restore

Restore deverá possuir procedimento conhecido.

------------------------------------------------------------------------

# 52. Disaster Recovery

Serviços críticos deverão estar incluídos na estratégia de DR.

------------------------------------------------------------------------

# 53. RPO

RPO deverá ser conhecido para dados críticos.

------------------------------------------------------------------------

# 54. RTO

RTO deverá ser conhecido para serviços críticos.

------------------------------------------------------------------------

# 55. Deploy

Aplicar GINF-09.

------------------------------------------------------------------------

# 56. CI/CD

Release de production deverá ocorrer pelo pipeline oficial sempre que
possível.

------------------------------------------------------------------------

# 57. Rollback

Antes do go-live, deverá existir resposta para:

``` text
Como voltamos
se a nova versão falhar?
```

------------------------------------------------------------------------

# 58. Compatibilidade entre Versões

Rolling deploy exige compatibilidade temporária entre versões
adjacentes.

------------------------------------------------------------------------

# 59. Infraestrutura como Código

Aplicar GINF-12.

------------------------------------------------------------------------

# 60. Drift

Mudanças manuais necessárias deverão ser reconciliadas.

------------------------------------------------------------------------

# 61. Acesso Operacional

A equipe responsável deverá possuir acesso suficiente para operar sem
permissões excessivas.

------------------------------------------------------------------------

# 62. Menor Privilégio

Aplicar menor privilégio.

------------------------------------------------------------------------

# 63. Break Glass

Para componentes críticos, confirmar procedimento emergencial quando
necessário.

------------------------------------------------------------------------

# 64. Runbooks

Aplicar GINF-15.

Runbooks deverão existir para cenários de falha relevantes.

------------------------------------------------------------------------

# 65. Incidentes

O serviço deverá integrar-se ao processo oficial de incidentes.

------------------------------------------------------------------------

# 66. Escalonamento

Deverá estar claro quem acionar quando o owner inicial não conseguir
resolver.

------------------------------------------------------------------------

# 67. Comunicação

Mudanças com impacto potencial deverão possuir plano de comunicação
proporcional.

------------------------------------------------------------------------

# 68. Custos

Aplicar GINF-14.

Confirmar que custo esperado é conhecido e aceitável.

------------------------------------------------------------------------

# 69. Ownership

Todo serviço em production deverá possuir owner.

------------------------------------------------------------------------

# 70. Documentação

Documentação deverá incluir:

-   arquitetura;
-   configuração;
-   operação;
-   dependências;
-   runbooks;
-   owner.

------------------------------------------------------------------------

# 71. Compliance

Verificar requisitos aplicáveis de:

-   LGPD;
-   segurança;
-   retenção;
-   auditoria.

------------------------------------------------------------------------

# 72. Evidências

A revisão deverá preservar evidências suficientes para demonstrar o que
foi validado.

------------------------------------------------------------------------

# 73. Testes Funcionais

Fluxos críticos deverão estar testados.

------------------------------------------------------------------------

# 74. Testes de Integração

Dependências relevantes deverão possuir validação integrada.

------------------------------------------------------------------------

# 75. Testes de Carga

Necessários quando volume ou criticidade justificarem.

------------------------------------------------------------------------

# 76. Testes de Falha

Cenários críticos deverão ser testados quando viável.

------------------------------------------------------------------------

# 77. Smoke Tests

Definir smoke tests pós-deploy.

------------------------------------------------------------------------

# 78. Critérios Go/No-Go

Antes da publicação deverá existir decisão explícita:

``` text
GO
ou
NO-GO
```

------------------------------------------------------------------------

# 79. Bloqueadores

São exemplos de bloqueadores:

-   vulnerabilidade crítica não aceita;
-   ausência de backup obrigatório;
-   migration destrutiva não validada;
-   secret exposto;
-   ausência de rollback em mudança crítica;
-   falha conhecida que compromete integridade;
-   observabilidade insuficiente para componente crítico.

------------------------------------------------------------------------

# 80. Riscos Aceitos

Risco não bloqueador poderá ser aceito formalmente.

Registrar:

-   risco;
-   impacto;
-   owner;
-   mitigação;
-   prazo;
-   aprovador.

------------------------------------------------------------------------

# 81. Aprovação para Produção

A aprovação deverá ocorrer somente após avaliação dos bloqueadores e
riscos.

------------------------------------------------------------------------

# 82. Validação Pós-Deploy

Após deploy verificar:

-   saúde;
-   erros;
-   latência;
-   filas;
-   banco;
-   logs;
-   métricas;
-   fluxos críticos.

------------------------------------------------------------------------

# 83. Hypercare

Mudanças de maior risco poderão possuir período de observação reforçada
após lançamento.

------------------------------------------------------------------------

# 84. Revisão Pós-Lançamento

Após mudanças relevantes avaliar:

-   comportamento real;
-   incidentes;
-   capacidade;
-   custos;
-   alertas;
-   documentação.

------------------------------------------------------------------------

# 85. Checklist Oficial

## Arquitetura

-   [ ] arquitetura documentada;
-   [ ] owner definido;
-   [ ] dependências conhecidas;
-   [ ] fluxo de dados conhecido;
-   [ ] decisões estruturais registradas.

## Ambientes e Configuração

-   [ ] ambientes isolados;
-   [ ] configuração de production;
-   [ ] secrets protegidos;
-   [ ] sem credenciais hardcoded;
-   [ ] configuração reproduzível.

## Rede e TLS

-   [ ] exposição mínima;
-   [ ] DNS validado;
-   [ ] HTTPS;
-   [ ] certificados;
-   [ ] renovação.

## Runtime

-   [ ] processos adequados;
-   [ ] timeouts;
-   [ ] graceful shutdown;
-   [ ] health checks;
-   [ ] readiness;
-   [ ] liveness.

## Dados

-   [ ] banco dimensionado;
-   [ ] conexões revisadas;
-   [ ] migrations testadas;
-   [ ] Redis revisado;
-   [ ] storage revisado;
-   [ ] backups ativos.

## Segurança

-   [ ] autenticação;
-   [ ] autorização;
-   [ ] vulnerabilidades;
-   [ ] secrets;
-   [ ] dados e privacidade;
-   [ ] menor privilégio;
-   [ ] auditoria.

## Observabilidade

-   [ ] logs;
-   [ ] métricas;
-   [ ] dashboards;
-   [ ] alertas;
-   [ ] owners dos alertas;
-   [ ] ações conhecidas.

## Resiliência

-   [ ] timeouts;
-   [ ] retries;
-   [ ] idempotência;
-   [ ] backpressure;
-   [ ] limites;
-   [ ] failover quando necessário.

## Capacidade

-   [ ] baseline;
-   [ ] carga esperada;
-   [ ] headroom;
-   [ ] escala;
-   [ ] gargalos conhecidos;
-   [ ] custos estimados.

## Recuperação

-   [ ] backup;
-   [ ] restore;
-   [ ] RPO;
-   [ ] RTO;
-   [ ] DR quando aplicável.

## Deploy

-   [ ] CI/CD;
-   [ ] artefato versionado;
-   [ ] migrations compatíveis;
-   [ ] rollback;
-   [ ] smoke tests;
-   [ ] validação pós-deploy.

## Operação

-   [ ] runbooks;
-   [ ] escalonamento;
-   [ ] acesso operacional;
-   [ ] break glass quando aplicável;
-   [ ] processo de incidentes;
-   [ ] documentação.

## Governança

-   [ ] IaC;
-   [ ] drift controlado;
-   [ ] owner;
-   [ ] riscos registrados;
-   [ ] exceções documentadas;
-   [ ] aprovação GO/NO-GO.

------------------------------------------------------------------------

# 86. Template de Production Readiness Review

``` markdown
# Production Readiness Review — <Serviço/Mudança>

## Identificação

Serviço:
Owner:
Versão:
Data:
Ambiente:
Criticidade:

## Objetivo

Descrever o que será colocado em produção.

## Arquitetura

Resumo:
Dependências:
Fluxo de dados:

## Segurança

Status:
Riscos:

## Dados

Banco:
Migrations:
Backup:
Restore:

## Observabilidade

Logs:
Métricas:
Alertas:
Dashboards:

## Capacidade

Carga esperada:
Limites:
Estratégia de escala:

## Deploy

Pipeline:
Estratégia:
Rollback:
Smoke tests:

## Operação

Runbooks:
Escalonamento:
Owner operacional:

## Riscos Conhecidos

1.
2.

## Bloqueadores

1.
2.

## Riscos Aceitos

1.
2.

## Decisão

[ ] GO
[ ] NO-GO

Aprovadores:

Data:
```

------------------------------------------------------------------------

# 87. Anti-Padrões

Evitar:

``` text
"funciona em staging,
então está pronto"
```

------------------------------------------------------------------------

``` text
produção
sem owner
```

------------------------------------------------------------------------

``` text
serviço crítico
sem alerta
```

------------------------------------------------------------------------

``` text
deploy
sem rollback
```

------------------------------------------------------------------------

``` text
banco crítico
sem restore testado
```

------------------------------------------------------------------------

``` text
migration grande
testada pela primeira vez
em production
```

------------------------------------------------------------------------

``` text
risco conhecido
não registrado
```

------------------------------------------------------------------------

``` text
checklist
marcado automaticamente
sem evidência
```

------------------------------------------------------------------------

``` text
GO
com bloqueador
não resolvido
```

------------------------------------------------------------------------

# 88. Documentos Relacionados

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
-   GSF --- GereIgreja Security Framework
-   GOC --- GereIgreja Operations Center
-   GQF --- GereIgreja Quality Framework
-   GDF --- GereIgreja Documentation Framework

------------------------------------------------------------------------

# 89. Princípios Finais

Production Readiness transforma publicação em decisão de engenharia.

``` text
Arquitetura
+
Segurança
+
Observabilidade
+
Recuperação
+
Operação
+
Validação
=
Prontidão para Produção
```

O princípio central é:

``` text
Antes de perguntar
"podemos colocar no ar?"

devemos conseguir responder:

como observar,
como operar,
como escalar,
como proteger
e como recuperar.
```

O checklist não deverá ser utilizado como burocracia ou exercício de
marcação.

Ele existe para revelar riscos antes que produção os transforme em
incidentes.

------------------------------------------------------------------------

# 90. Status do Documento

**Pasta**

`docs/infraestrutura/`

**Arquivo**

`17-Checklist-de-Producao-e-Prontidao-Operacional.md`

**Documento**

`GINF-17`

**Código**

`GINF-PRODUCTION-READINESS`

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

`GINF-16 — Governança, Padrões e Evolução da Infraestrutura`

**Próximo documento recomendado**

`18-Indice-e-Mapa-da-Infraestrutura.md`
