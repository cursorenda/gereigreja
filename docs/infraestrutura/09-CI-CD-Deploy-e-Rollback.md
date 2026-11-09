Pasta:

docs/infraestrutura/

Arquivo:

09-CI-CD-Deploy-e-Rollback.md

Documento:

GINF-09

Código:

GINF-CICD-DEPLOY-ROLLBACK

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

# GINF-09 --- CI/CD, Deploy e Rollback

> "Toda mudança em produção deve ser reproduzível, rastreável, validada
> e reversível dentro dos limites conhecidos da alteração."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com a Arquitetura
4.  Princípios Fundamentais
5.  Visão Geral do Pipeline
6.  Integração Contínua
7.  Entrega e Deploy Contínuos
8.  Repositório como Origem
9.  Branches e Commits
10. Pull Requests e Revisão
11. Pipeline Oficial
12. Etapas do Pipeline
13. Validação de Código
14. Testes
15. Segurança
16. Dependências
17. Build
18. Artefato de Release
19. Imagem de Container
20. Registry
21. Identificação da Release
22. Build Once
23. Ambientes
24. Development
25. Staging
26. Production
27. Promoção
28. Aprovação
29. Credenciais do Pipeline
30. Secrets
31. Menor Privilégio
32. Deploy
33. Estratégias de Deploy
34. Rolling Deploy
35. Recreate
36. Blue/Green
37. Canary
38. Escolha da Estratégia
39. Pre-Deploy
40. Migrações
41. Compatibilidade de Schema
42. Expand and Contract
43. Backfills
44. Jobs de Deploy
45. Ordem do Deploy
46. Readiness
47. Health Checks
48. Smoke Tests
49. Pós-Deploy
50. Observação Inicial
51. Rollback
52. Rollback de Código
53. Rollback de Imagem
54. Rollback de Configuração
55. Rollback de Banco
56. Migrações Irreversíveis
57. Feature Flags
58. Roll Forward
59. Falha Parcial
60. Deploy de Workers
61. Compatibilidade de Filas
62. Scheduler
63. Deploy de Frontend e Assets
64. Storage
65. Configuração
66. Mudanças de Infraestrutura
67. Infraestrutura como Código
68. Janelas de Manutenção
69. Zero Downtime
70. Observabilidade
71. Logging
72. Métricas
73. Alertas
74. Auditoria
75. Histórico de Deploy
76. Versionamento
77. Changelog
78. Comunicação
79. Incidentes durante Deploy
80. Hotfix
81. Emergency Deploy
82. Freeze
83. Recuperação
84. Permissões de Produção
85. Acesso Manual
86. Artefatos e Evidências
87. Retenção
88. Performance do Pipeline
89. Concorrência de Pipelines
90. Cancelamento
91. Testes do Processo de Deploy
92. Desenvolvimento Local
93. Staging como Gate
94. Produção
95. Anti-Padrões
96. Arquitetura de Referência
97. Checklist
98. Documentos Relacionados
99. Princípios Finais
100. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece o padrão oficial de CI/CD, deploy e rollback
do GereIgreja.

Seu objetivo é garantir que mudanças sejam entregues com:

-   automação;
-   rastreabilidade;
-   validação;
-   segurança;
-   previsibilidade;
-   capacidade de recuperação.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   pipelines;
-   testes automatizados;
-   builds;
-   imagens;
-   registry;
-   staging;
-   produção;
-   migrations;
-   workers;
-   configuração;
-   deploy;
-   rollback;
-   hotfixes;
-   evidências de release.

------------------------------------------------------------------------

# 3. Relação com a Arquitetura

``` text
Código
  │
  ▼
CI
  │
  ├── validação
  ├── testes
  ├── segurança
  └── build
       │
       ▼
    Artefato
       │
       ▼
    Registry
       │
       ▼
    Staging
       │
       ▼
    Production
```

GINF-08 define o artefato.

GINF-09 define como esse artefato chega aos ambientes.

------------------------------------------------------------------------

# 4. Princípios Fundamentais

Aplicar:

-   automação por padrão;
-   mesma release entre staging e production;
-   produção protegida;
-   migrations compatíveis;
-   health checks;
-   observação após deploy;
-   rollback conhecido;
-   rastreabilidade ponta a ponta.

------------------------------------------------------------------------

# 5. Visão Geral do Pipeline

Fluxo recomendado:

``` text
Commit
  ↓
Pull Request
  ↓
Checks
  ↓
Merge
  ↓
Build
  ↓
Artefato imutável
  ↓
Staging
  ↓
Validação
  ↓
Production
  ↓
Monitoramento
```

------------------------------------------------------------------------

# 6. Integração Contínua

CI deverá validar cada mudança relevante o mais cedo possível.

Objetivo:

``` text
detectar erro
antes do deploy
```

------------------------------------------------------------------------

# 7. Entrega e Deploy Contínuos

Automação não significa ausência de controle.

A maturidade poderá evoluir de:

``` text
deploy automatizado com aprovação
```

para fluxos mais automáticos quando segurança operacional permitir.

------------------------------------------------------------------------

# 8. Repositório como Origem

Código e arquivos necessários para reproduzir a release deverão estar
versionados.

Mudanças manuais fora do repositório deverão ser exceção.

------------------------------------------------------------------------

# 9. Branches e Commits

A estratégia Git deverá permitir identificar exatamente o commit da
release.

Commits de produção não deverão ser ambíguos.

------------------------------------------------------------------------

# 10. Pull Requests e Revisão

Mudanças relevantes deverão passar por revisão conforme processo oficial
de engenharia.

Mudanças emergenciais também deverão deixar rastreabilidade posterior.

------------------------------------------------------------------------

# 11. Pipeline Oficial

Produção deverá receber artefatos somente do pipeline oficial ou
processo emergencial formalmente autorizado.

------------------------------------------------------------------------

# 12. Etapas do Pipeline

Exemplo:

``` text
lint
↓
tests
↓
security checks
↓
build
↓
scan
↓
publish
↓
deploy staging
↓
validate
↓
deploy production
```

A implementação poderá evoluir.

------------------------------------------------------------------------

# 13. Validação de Código

O pipeline deverá executar verificações definidas pelos padrões de
qualidade.

Aplicar GQF.

------------------------------------------------------------------------

# 14. Testes

Testes obrigatórios deverão impedir promoção quando falharem, conforme
criticidade.

------------------------------------------------------------------------

# 15. Segurança

Aplicar GSF-15.

Pipeline deverá incluir controles compatíveis com:

-   secrets;
-   dependências;
-   vulnerabilidades;
-   artefatos.

------------------------------------------------------------------------

# 16. Dependências

Mudanças de dependências deverão passar pelas mesmas validações de
código.

------------------------------------------------------------------------

# 17. Build

Build deverá ser:

-   automatizado;
-   reproduzível;
-   identificável;
-   executado em ambiente controlado.

------------------------------------------------------------------------

# 18. Artefato de Release

A release deverá gerar artefato imutável.

No runtime containerizado, normalmente será uma imagem.

------------------------------------------------------------------------

# 19. Imagem de Container

Aplicar GINF-08.

Não reconstruir imagem diferente para production.

------------------------------------------------------------------------

# 20. Registry

O pipeline deverá publicar artefato em registry autorizado.

------------------------------------------------------------------------

# 21. Identificação da Release

Relacionar:

``` text
release_id
commit_sha
image_tag
image_digest
build_id
```

quando disponíveis.

------------------------------------------------------------------------

# 22. Build Once

Princípio:

``` text
Build Once
Promote Many
```

------------------------------------------------------------------------

# 23. Ambientes

Pipeline deverá reconhecer explicitamente:

-   development;
-   staging;
-   production.

------------------------------------------------------------------------

# 24. Development

Development pode possuir fluxo rápido, mas não deverá enfraquecer
controles de production.

------------------------------------------------------------------------

# 25. Staging

Staging é ambiente de validação da release candidata.

Deverá se aproximar de produção nas características relevantes.

------------------------------------------------------------------------

# 26. Production

Production deverá possuir proteção superior:

-   credenciais específicas;
-   approvals quando adotados;
-   auditoria;
-   restrição de acesso.

------------------------------------------------------------------------

# 27. Promoção

Promoção significa mover o mesmo artefato aprovado para o próximo
ambiente.

------------------------------------------------------------------------

# 28. Aprovação

Aprovação manual poderá ser exigida para produção conforme maturidade e
risco.

Ela deverá identificar:

-   release;
-   aprovador;
-   momento.

------------------------------------------------------------------------

# 29. Credenciais do Pipeline

Pipelines deverão possuir identidades próprias.

Não utilizar credenciais pessoais permanentes de desenvolvedores.

------------------------------------------------------------------------

# 30. Secrets

Secrets deverão ser obtidos por mecanismo seguro.

Nunca armazená-los no arquivo do pipeline em texto aberto.

------------------------------------------------------------------------

# 31. Menor Privilégio

O pipeline de testes não precisa necessariamente de permissão de deploy.

Separar funções quando possível.

------------------------------------------------------------------------

# 32. Deploy

Deploy deverá ser uma operação conhecida e repetível.

Evitar sequências manuais dependentes da memória de uma pessoa.

------------------------------------------------------------------------

# 33. Estratégias de Deploy

Possíveis estratégias:

-   recreate;
-   rolling;
-   blue/green;
-   canary.

A escolha depende da infraestrutura e criticidade.

------------------------------------------------------------------------

# 34. Rolling Deploy

Substitui instâncias progressivamente.

Exige compatibilidade temporária entre versões.

------------------------------------------------------------------------

# 35. Recreate

Interrompe versão antiga e inicia nova.

Pode ser aceitável em ambientes ou serviços onde downtime controlado
seja permitido.

------------------------------------------------------------------------

# 36. Blue/Green

Mantém dois ambientes de aplicação e alterna tráfego.

Pode facilitar rollback, mas aumenta custo e complexidade.

------------------------------------------------------------------------

# 37. Canary

Expõe nova release a parte do tráfego.

Exige observabilidade e roteamento adequados.

------------------------------------------------------------------------

# 38. Escolha da Estratégia

Não adotar estratégia sofisticada apenas por padrão de mercado.

Utilizar a mais simples que cumpra requisitos de disponibilidade e
risco.

------------------------------------------------------------------------

# 39. Pre-Deploy

Antes do deploy verificar:

-   pipeline verde;
-   artefato existente;
-   configuração;
-   secrets;
-   migrations;
-   capacidade;
-   dependências externas críticas.

------------------------------------------------------------------------

# 40. Migrações

Migrations deverão ser parte explícita do processo.

Nunca depender de execução manual esquecível.

------------------------------------------------------------------------

# 41. Compatibilidade de Schema

Durante rolling deploy:

``` text
código N
+
código N+1
+
schema atual
```

podem coexistir.

------------------------------------------------------------------------

# 42. Expand and Contract

Preferir:

``` text
expand
→ deploy compatível
→ migrar dados
→ trocar uso
→ contract depois
```

------------------------------------------------------------------------

# 43. Backfills

Backfills longos deverão ser jobs controlados, não necessariamente
bloqueantes do deploy.

------------------------------------------------------------------------

# 44. Jobs de Deploy

Migrations e operações one-off deverão possuir status observável.

Falha deverá interromper a progressão quando necessário.

------------------------------------------------------------------------

# 45. Ordem do Deploy

A ordem depende da mudança.

Exemplo seguro:

``` text
schema compatível
→ aplicação
→ backfill
→ remoção futura
```

------------------------------------------------------------------------

# 46. Readiness

Nova instância somente deverá receber tráfego quando estiver pronta.

------------------------------------------------------------------------

# 47. Health Checks

Deploy deverá usar health checks significativos.

------------------------------------------------------------------------

# 48. Smoke Tests

Após deploy, executar verificações rápidas de fluxos essenciais.

Exemplos:

-   página de health;
-   autenticação básica;
-   acesso à aplicação;
-   dependências principais.

------------------------------------------------------------------------

# 49. Pós-Deploy

Após promoção:

``` text
validar
→ observar
→ confirmar estabilidade
```

------------------------------------------------------------------------

# 50. Observação Inicial

Monitorar especialmente:

-   erros;
-   latência;
-   CPU;
-   memória;
-   banco;
-   filas;
-   integrações.

------------------------------------------------------------------------

# 51. Rollback

Toda release deverá responder:

``` text
como voltar?
```

antes de chegar à produção.

------------------------------------------------------------------------

# 52. Rollback de Código

Código deverá voltar para artefato anterior conhecido.

------------------------------------------------------------------------

# 53. Rollback de Imagem

Preferir redeploy do digest/tag imutável anterior.

Não reconstruir versão antiga durante incidente.

------------------------------------------------------------------------

# 54. Rollback de Configuração

Mudanças de configuração também precisam ser versionadas/rastreáveis e
reversíveis quando possível.

------------------------------------------------------------------------

# 55. Rollback de Banco

Banco exige cuidado especial.

Rollback de aplicação não desfaz automaticamente migration ou dados
transformados.

------------------------------------------------------------------------

# 56. Migrações Irreversíveis

Mudanças destrutivas deverão possuir plano específico.

Pode ser mais seguro realizar roll forward do que tentar reversão.

------------------------------------------------------------------------

# 57. Feature Flags

Feature flags poderão desacoplar deploy de ativação.

Deverão possuir:

-   owner;
-   finalidade;
-   estado padrão;
-   plano de remoção.

------------------------------------------------------------------------

# 58. Roll Forward

Quando rollback não for seguro, corrigir com nova release pode ser a
melhor estratégia.

------------------------------------------------------------------------

# 59. Falha Parcial

Deploy pode falhar após apenas parte das instâncias atualizar.

A arquitetura deverá tolerar coexistência ou abortar de forma segura.

------------------------------------------------------------------------

# 60. Deploy de Workers

Workers deverão ser atualizados considerando mensagens existentes.

------------------------------------------------------------------------

# 61. Compatibilidade de Filas

Producer e consumer de versões adjacentes poderão coexistir.

Payloads deverão permanecer compatíveis ou versionados.

------------------------------------------------------------------------

# 62. Scheduler

Scheduler deverá evitar duplicação durante substituição.

------------------------------------------------------------------------

# 63. Deploy de Frontend e Assets

Assets versionados deverão evitar incompatibilidade com páginas ainda
servidas por versão anterior.

Preferir nomes com hash quando o processo de frontend utilizar build
estático.

------------------------------------------------------------------------

# 64. Storage

Deploy não deverá apagar uploads ou arquivos persistentes.

Aplicar GINF-07.

------------------------------------------------------------------------

# 65. Configuração

Aplicar GINF-02.

Mudanças de config devem ser tratadas como parte da release operacional.

------------------------------------------------------------------------

# 66. Mudanças de Infraestrutura

Infraestrutura deverá evoluir por processo controlado.

Evitar alterações manuais não registradas.

------------------------------------------------------------------------

# 67. Infraestrutura como Código

Quando adotada, infraestrutura como código deverá passar por revisão e
pipeline próprios.

A definição detalhada será tratada em documento específico.

------------------------------------------------------------------------

# 68. Janelas de Manutenção

Mudanças que exigem indisponibilidade deverão possuir janela planejada e
comunicação apropriada.

------------------------------------------------------------------------

# 69. Zero Downtime

Zero downtime é objetivo quando necessário, não promessa automática.

Exige:

-   compatibilidade;
-   readiness;
-   capacidade;
-   migrations adequadas.

------------------------------------------------------------------------

# 70. Observabilidade

Deploy deverá gerar marcador/evento na observabilidade.

Isso permite correlacionar:

``` text
erro começou
↔
release entrou
```

------------------------------------------------------------------------

# 71. Logging

Logs deverão incluir identificador de release quando possível.

------------------------------------------------------------------------

# 72. Métricas

Comparar métricas antes e depois da release.

------------------------------------------------------------------------

# 73. Alertas

Alertas críticos não deverão ser desativados apenas para "passar o
deploy".

Ajustes temporários exigem owner e prazo.

------------------------------------------------------------------------

# 74. Auditoria

Registrar:

-   quem promoveu;
-   qual release;
-   ambiente;
-   horário;
-   resultado.

------------------------------------------------------------------------

# 75. Histórico de Deploy

Manter histórico consultável de deploys.

------------------------------------------------------------------------

# 76. Versionamento

Versões deverão seguir padrão oficial do GereIgreja.

A infraestrutura precisa conseguir mapear versão para artefato.

------------------------------------------------------------------------

# 77. Changelog

Mudanças relevantes deverão ser documentadas conforme GDF.

------------------------------------------------------------------------

# 78. Comunicação

Deploys de alto impacto deverão possuir comunicação proporcional ao
risco.

------------------------------------------------------------------------

# 79. Incidentes durante Deploy

Se um deploy causar incidente:

``` text
detectar
→ conter
→ rollback/roll forward
→ validar
→ registrar
→ aprender
```

Aplicar GSF-13.

------------------------------------------------------------------------

# 80. Hotfix

Hotfix deverá manter o máximo possível dos controles normais.

Urgência não elimina:

-   testes essenciais;
-   rastreabilidade;
-   artefato;
-   revisão posterior.

------------------------------------------------------------------------

# 81. Emergency Deploy

Processo emergencial deverá ser excepcional e auditável.

Após estabilização, reconciliar tudo com o fluxo normal.

------------------------------------------------------------------------

# 82. Freeze

Períodos de freeze poderão ser adotados em datas de risco elevado.

Exceções deverão ser autorizadas.

------------------------------------------------------------------------

# 83. Recuperação

O processo de deploy é parte da estratégia de recuperação.

Deverá ser possível reconstruir ambiente a partir de artefatos e
configuração controlados.

------------------------------------------------------------------------

# 84. Permissões de Produção

Poucas identidades deverão possuir capacidade de deploy direto em
production.

Preferir pipeline como caminho oficial.

------------------------------------------------------------------------

# 85. Acesso Manual

Acesso manual poderá existir para incidentes e diagnóstico.

Não deverá se tornar mecanismo normal de deploy.

------------------------------------------------------------------------

# 86. Artefatos e Evidências

Preservar quando necessário:

-   logs de pipeline;
-   resultados de testes;
-   scans;
-   digest;
-   aprovação;
-   status de deploy.

------------------------------------------------------------------------

# 87. Retenção

Retenção deverá permitir investigação e rollback dentro da política
definida.

------------------------------------------------------------------------

# 88. Performance do Pipeline

Pipeline deverá ser rápido o suficiente para incentivar seu uso, sem
remover verificações críticas.

------------------------------------------------------------------------

# 89. Concorrência de Pipelines

Deploys simultâneos no mesmo ambiente deverão ser controlados.

Evitar duas releases concorrendo por production.

------------------------------------------------------------------------

# 90. Cancelamento

Pipeline cancelado deverá deixar ambiente em estado conhecido.

------------------------------------------------------------------------

# 91. Testes do Processo de Deploy

Não testar somente a aplicação.

Testar também:

-   deploy;
-   rollback;
-   migration;
-   health;
-   worker;
-   scheduler.

------------------------------------------------------------------------

# 92. Desenvolvimento Local

Desenvolvedores deverão conseguir executar verificações essenciais antes
do push.

------------------------------------------------------------------------

# 93. Staging como Gate

Staging deverá validar a release candidata, não uma build diferente.

------------------------------------------------------------------------

# 94. Produção

Produção deverá receber somente artefato:

-   aprovado;
-   identificado;
-   validado;
-   rastreável.

------------------------------------------------------------------------

# 95. Anti-Padrões

Evitar:

``` text
ssh production
→ git pull
```

------------------------------------------------------------------------

``` text
docker build
diretamente
no servidor de produção
```

------------------------------------------------------------------------

``` text
deploy
sem saber qual commit
```

------------------------------------------------------------------------

``` text
migration destrutiva
junto com rolling deploy
incompatível
```

------------------------------------------------------------------------

``` text
rollback
reconstruindo imagem antiga
```

------------------------------------------------------------------------

``` text
secret
dentro do pipeline
em texto aberto
```

------------------------------------------------------------------------

``` text
staging testa
artefato diferente
de production
```

------------------------------------------------------------------------

``` text
deploy manual
como processo normal
```

------------------------------------------------------------------------

``` text
pipeline verde
mas sem health check
pós-deploy
```

------------------------------------------------------------------------

# 96. Arquitetura de Referência

``` text
                    DEVELOPER
                        │
                        ▼
                  SOURCE CONTROL
                        │
                        ▼
                   PULL REQUEST
                        │
                        ▼
                  CI VALIDATION
              ┌─────────┼─────────┐
              ▼         ▼         ▼
            TESTS    SECURITY    QUALITY
              └─────────┼─────────┘
                        ▼
                       BUILD
                        │
                        ▼
                IMMUTABLE IMAGE
                        │
                        ▼
                 PRIVATE REGISTRY
                        │
                        ▼
                     STAGING
                        │
                 Smoke / Validate
                        │
                        ▼
                    APPROVAL
                        │
                        ▼
                   PRODUCTION
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
            HEALTH    METRICS    LOGS
                        │
                        ▼
                STABLE / ROLLBACK
```

------------------------------------------------------------------------

# 97. Checklist

## CI

-   [ ] lint/quality;
-   [ ] testes;
-   [ ] segurança;
-   [ ] dependências;
-   [ ] build automatizado.

## Artefato

-   [ ] imutável;
-   [ ] commit associado;
-   [ ] tag única;
-   [ ] digest conhecido;
-   [ ] registry autorizado.

## Staging

-   [ ] mesma imagem candidata;
-   [ ] migrations validadas;
-   [ ] smoke tests;
-   [ ] workers;
-   [ ] scheduler.

## Production

-   [ ] aprovação quando exigida;
-   [ ] config validada;
-   [ ] secrets disponíveis;
-   [ ] readiness;
-   [ ] health checks;
-   [ ] observação pós-deploy.

## Banco

-   [ ] migration compatível;
-   [ ] backfill avaliado;
-   [ ] rollback conhecido;
-   [ ] mudança destrutiva separada quando necessário.

## Rollback

-   [ ] imagem anterior disponível;
-   [ ] configuração reversível;
-   [ ] impacto de schema conhecido;
-   [ ] estratégia roll forward considerada.

## Auditoria

-   [ ] release;
-   [ ] commit;
-   [ ] ambiente;
-   [ ] responsável;
-   [ ] horário;
-   [ ] resultado.

------------------------------------------------------------------------

# 98. Documentos Relacionados

-   GINF-01 --- Arquitetura da Infraestrutura
-   GINF-02 --- Ambientes e Configuração
-   GINF-03 --- Rede, DNS, Proxy e TLS
-   GINF-04 --- Runtime Django e Workers
-   GINF-05 --- Banco de Dados e Persistência
-   GINF-06 --- Redis, Cache e Filas
-   GINF-07 --- Storage e Arquivos
-   GINF-08 --- Containers, Imagens e Registry
-   GSF-09 --- Gestão de Segredos e Criptografia
-   GSF-12 --- Gestão de Vulnerabilidades
-   GSF-13 --- Gestão de Incidentes de Segurança
-   GSF-15 --- Secure Development Lifecycle
-   GQF --- GereIgreja Quality Framework
-   GOC --- GereIgreja Operations Center
-   GDF --- GereIgreja Documentation Framework
-   GereIgreja Backend Engineering

------------------------------------------------------------------------

# 99. Princípios Finais

O pipeline do GereIgreja deverá transformar código revisado em uma
release conhecida.

``` text
Commit
+
Validação
+
Artefato
+
Promoção
+
Observabilidade
=
Deploy controlado
```

O princípio central é:

``` text
Production não recebe código.
Production recebe releases.
```

E toda release deverá possuir resposta para quatro perguntas:

``` text
O que estamos implantando?
Quem autorizou?
Como sabemos que funcionou?
Como recuperamos se falhar?
```

Automação deverá reduzir erro humano sem eliminar governança.

------------------------------------------------------------------------

# 100. Status do Documento

**Pasta**

`docs/infraestrutura/`

**Arquivo**

`09-CI-CD-Deploy-e-Rollback.md`

**Documento**

`GINF-09`

**Código**

`GINF-CICD-DEPLOY-ROLLBACK`

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

`GINF-08 — Containers, Imagens e Registry`

**Próximo documento recomendado**

`10-Observabilidade-Logs-Metricas-e-Alertas.md`
