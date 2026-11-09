Pasta:

docs/infraestrutura/

Arquivo:

08-Containers-Imagens-e-Registry.md

Documento:

GINF-08

Código:

GINF-CONTAINERS-IMAGES-REGISTRY

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

# GINF-08 --- Containers, Imagens e Registry

> "Uma release deve ser um artefato identificável, reproduzível e
> imutável. O ambiente muda a configuração; não o conteúdo da imagem."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com a Arquitetura
4.  Princípios Fundamentais
5.  Papel dos Containers
6.  Imutabilidade
7.  Build Once, Run Anywhere
8.  Imagens
9.  Imagem Base
10. Versões Fixadas
11. Dockerfile
12. Build Context
13. Multi-Stage Build
14. Dependências
15. Dependências de Sistema
16. Dependências Python
17. Assets Frontend
18. Arquivos Desnecessários
19. `.dockerignore`
20. Secrets no Build
21. Build Arguments
22. Configuração em Runtime
23. Variáveis de Ambiente
24. Entrypoint
25. Command
26. Processos
27. Um Container, Uma Responsabilidade
28. Web
29. Workers
30. Scheduler
31. Jobs Administrativos
32. Usuário Não-Root
33. Permissões de Arquivo
34. Filesystem
35. Volumes
36. Arquivos Persistentes
37. Logs
38. Sinais
39. Graceful Shutdown
40. Health Checks
41. Readiness e Liveness
42. Portas
43. Rede
44. Recursos
45. CPU e Memória
46. Registry
47. Acesso ao Registry
48. Tags
49. Tags Mutáveis
50. Digest
51. Versionamento de Imagens
52. Release
53. Rastreabilidade
54. Promoção entre Ambientes
55. Staging
56. Production
57. Rollback
58. Retenção de Imagens
59. Limpeza
60. Segurança da Supply Chain
61. Vulnerabilidades
62. Scanning
63. SBOM
64. Proveniência
65. Assinatura de Imagens
66. Dependências Confiáveis
67. Atualização de Imagens Base
68. CI/CD
69. Cache de Build
70. Reprodutibilidade
71. Ambientes de Desenvolvimento
72. Docker Compose
73. Dados Locais
74. Banco e Redis Locais
75. Compatibilidade de Arquitetura
76. Multi-Architecture
77. Observabilidade
78. Métricas
79. Auditoria
80. Falhas de Build
81. Falhas de Pull
82. Falhas de Startup
83. Imagem Corrompida ou Vulnerável
84. Recuperação
85. Testes
86. Anti-Padrões
87. Arquitetura de Referência
88. Checklist
89. Documentos Relacionados
90. Princípios Finais
91. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece o padrão oficial para containers, imagens e
registry do GereIgreja.

Seu objetivo é garantir que os artefatos executáveis da plataforma
sejam:

-   reproduzíveis;
-   identificáveis;
-   seguros;
-   imutáveis;
-   rastreáveis;
-   promovíveis entre ambientes;
-   compatíveis com rollback.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   Dockerfiles;
-   imagens de aplicação;
-   containers;
-   registry;
-   builds;
-   tags;
-   digests;
-   runtime web;
-   workers;
-   schedulers;
-   jobs;
-   CI/CD;
-   desenvolvimento local.

------------------------------------------------------------------------

# 3. Relação com a Arquitetura

``` text
Source Code
    │
    ▼
CI Build
    │
    ▼
Container Image
    │
    ▼
Registry
    │
    ├──► Staging
    │
    └──► Production
```

A mesma imagem deverá ser promovida quando possível.

------------------------------------------------------------------------

# 4. Princípios Fundamentais

Aplicar:

-   build reproduzível;
-   imagem imutável;
-   menor privilégio;
-   sem secrets embutidos;
-   versões identificáveis;
-   dependências controladas;
-   promoção do mesmo artefato;
-   scanning;
-   rollback disponível.

------------------------------------------------------------------------

# 5. Papel dos Containers

Containers empacotam:

``` text
aplicação
+
runtime
+
dependências
```

Não deverão empacotar:

``` text
dados permanentes
+
secrets de ambiente
+
configuração específica de produção
```

------------------------------------------------------------------------

# 6. Imutabilidade

Depois de publicada, uma imagem de release não deverá ser alterada.

Mudança exige novo artefato.

------------------------------------------------------------------------

# 7. Build Once, Run Anywhere

Princípio preferencial:

``` text
build uma vez
       ↓
mesma imagem
       ↓
staging
       ↓
production
```

As diferenças deverão entrar por configuração e secrets.

------------------------------------------------------------------------

# 8. Imagens

Imagens deverão conter somente o necessário para executar a
responsabilidade definida.

Imagens menores reduzem:

-   superfície de ataque;
-   transferência;
-   tempo de pull;
-   dependências desnecessárias.

------------------------------------------------------------------------

# 9. Imagem Base

Imagens base deverão possuir:

-   origem confiável;
-   versão controlada;
-   manutenção ativa;
-   compatibilidade conhecida.

------------------------------------------------------------------------

# 10. Versões Fixadas

Evitar depender exclusivamente de tags amplas como:

``` text
python:latest
```

Preferir versão explicitamente controlada.

------------------------------------------------------------------------

# 11. Dockerfile

Dockerfile deverá ser versionado junto ao código relevante.

Mudanças deverão passar pelo fluxo normal de revisão.

------------------------------------------------------------------------

# 12. Build Context

O contexto enviado ao build deverá ser mínimo.

Não incluir:

-   `.git`;
-   backups;
-   `.env`;
-   secrets;
-   arquivos locais desnecessários.

------------------------------------------------------------------------

# 13. Multi-Stage Build

Multi-stage build deverá ser considerado para separar:

``` text
build dependencies
```

de:

``` text
runtime dependencies
```

------------------------------------------------------------------------

# 14. Dependências

Somente dependências necessárias deverão chegar à imagem final.

------------------------------------------------------------------------

# 15. Dependências de Sistema

Pacotes do sistema operacional deverão ser explicitamente declarados.

Evitar instalação manual não reproduzível dentro de container em
execução.

------------------------------------------------------------------------

# 16. Dependências Python

Dependências Python deverão seguir o mecanismo oficial do projeto.

Versões deverão ser controladas de forma compatível com o processo de
atualização e segurança.

------------------------------------------------------------------------

# 17. Assets Frontend

Quando assets forem compilados no build, o resultado deverá ser
reproduzível e associado à mesma release.

------------------------------------------------------------------------

# 18. Arquivos Desnecessários

Não copiar para a imagem final:

-   testes quando não necessários em runtime;
-   documentação operacional irrelevante;
-   caches locais;
-   credenciais;
-   dumps.

------------------------------------------------------------------------

# 19. `.dockerignore`

Deverá existir `.dockerignore` adequado ao projeto.

Ele reduz risco e contexto de build.

------------------------------------------------------------------------

# 20. Secrets no Build

Secrets não deverão ser gravados em layers.

Evitar:

``` dockerfile
ENV API_KEY=...
```

ou:

``` dockerfile
COPY .env /app/.env
```

------------------------------------------------------------------------

# 21. Build Arguments

Build args não deverão ser considerados mecanismo seguro de
armazenamento de secrets.

Valores sensíveis exigem mecanismo próprio do pipeline/build quando
inevitáveis.

------------------------------------------------------------------------

# 22. Configuração em Runtime

Aplicar GINF-02.

``` text
IMAGE
+
CONFIG
+
SECRETS
=
RUNNING SERVICE
```

------------------------------------------------------------------------

# 23. Variáveis de Ambiente

Variáveis deverão ser injetadas no runtime conforme ambiente.

A imagem não deverá conhecer antecipadamente credenciais de production.

------------------------------------------------------------------------

# 24. Entrypoint

Entrypoint deverá possuir responsabilidade simples.

Evitar scripts gigantes que:

-   alteram infraestrutura;
-   executam migrações destrutivas;
-   iniciam múltiplos serviços;
-   escondem erros.

------------------------------------------------------------------------

# 25. Command

Comandos poderão diferenciar responsabilidades usando a mesma imagem.

Exemplo conceitual:

``` text
web
worker
scheduler
```

------------------------------------------------------------------------

# 26. Processos

Processos principais deverão permanecer em foreground para que o runtime
de containers consiga:

-   observar;
-   sinalizar;
-   reiniciar;
-   encerrar.

------------------------------------------------------------------------

# 27. Um Container, Uma Responsabilidade

Não significa necessariamente um único processo técnico.

Significa uma responsabilidade operacional clara.

Evitar container que seja simultaneamente:

``` text
proxy
+
Django
+
worker
+
database
```

------------------------------------------------------------------------

# 28. Web

Container web deverá executar somente o runtime necessário para atender
a aplicação.

------------------------------------------------------------------------

# 29. Workers

Workers poderão usar a mesma imagem da aplicação, mas comando próprio.

Aplicar GINF-04 e GINF-06.

------------------------------------------------------------------------

# 30. Scheduler

Scheduler deverá possuir instância/responsabilidade conhecida para
evitar duplicidade.

------------------------------------------------------------------------

# 31. Jobs Administrativos

Comandos como migrations ou tarefas operacionais deverão executar como
jobs controlados quando necessário.

Não acoplá-los cegamente a todo startup web.

------------------------------------------------------------------------

# 32. Usuário Não-Root

Produção deverá preferir execução como usuário não-root.

Root somente quando tecnicamente necessário e justificado.

------------------------------------------------------------------------

# 33. Permissões de Arquivo

Arquivos dentro da imagem deverão possuir permissões mínimas.

Não utilizar permissões globais amplas para resolver problemas de build.

------------------------------------------------------------------------

# 34. Filesystem

Filesystem do container deverá ser tratado como efêmero.

Quando possível, runtime deverá tolerar filesystem read-only, exceto
paths temporários necessários.

------------------------------------------------------------------------

# 35. Volumes

Volumes deverão existir apenas para dados que realmente precisam
persistir ou ser compartilhados.

------------------------------------------------------------------------

# 36. Arquivos Persistentes

Uploads de produção não deverão depender do filesystem do container.

Aplicar GINF-07.

------------------------------------------------------------------------

# 37. Logs

Aplicação deverá preferir logs para stdout/stderr conforme a plataforma
de containers.

O sistema de observabilidade será responsável por coleta e retenção.

------------------------------------------------------------------------

# 38. Sinais

O processo deverá responder corretamente aos sinais do runtime.

Especialmente encerramento.

------------------------------------------------------------------------

# 39. Graceful Shutdown

Ao receber encerramento:

``` text
parar novas entradas
→ finalizar trabalho seguro
→ liberar recursos
→ sair
```

------------------------------------------------------------------------

# 40. Health Checks

A imagem/runtime deverá permitir health checks úteis.

Não utilizar apenas "processo existe" quando a aplicação pode estar
incapaz de atender.

------------------------------------------------------------------------

# 41. Readiness e Liveness

Quando a plataforma suportar, distinguir:

``` text
readiness
→ pode receber tráfego?

liveness
→ precisa ser reiniciado?
```

------------------------------------------------------------------------

# 42. Portas

Expor somente portas necessárias.

O container de aplicação não deverá publicar diretamente banco, Redis ou
serviços internos.

------------------------------------------------------------------------

# 43. Rede

Aplicar GINF-03.

Containers deverão comunicar-se apenas com serviços necessários.

------------------------------------------------------------------------

# 44. Recursos

Definir limites de CPU e memória conforme a plataforma permitir.

------------------------------------------------------------------------

# 45. CPU e Memória

Limites deverão ser baseados em medição.

Monitorar:

-   throttling;
-   OOM;
-   utilização;
-   picos.

------------------------------------------------------------------------

# 46. Registry

O registry é repositório oficial de imagens executáveis.

Deverá possuir:

-   autenticação;
-   controle de acesso;
-   retenção;
-   auditoria quando disponível;
-   alta disponibilidade proporcional à necessidade.

------------------------------------------------------------------------

# 47. Acesso ao Registry

Somente pipelines e runtimes autorizados deverão publicar/puxar imagens
conforme necessidade.

Credenciais de push deverão ser mais restritas.

------------------------------------------------------------------------

# 48. Tags

Tags deverão comunicar versão ou contexto.

Exemplos conceituais:

``` text
1.4.2
release-2026.08.15
commit-abc123
```

O padrão oficial deverá ser consistente com releases do projeto.

------------------------------------------------------------------------

# 49. Tags Mutáveis

Tags como:

``` text
latest
staging
production
```

podem ser úteis como ponteiros, mas não deverão ser a única identidade
de um artefato.

------------------------------------------------------------------------

# 50. Digest

Digest identifica conteúdo imutável.

Para deploys críticos, registrar digest da imagem utilizada.

------------------------------------------------------------------------

# 51. Versionamento de Imagens

Cada build promovível deverá possuir identificador único.

Nunca sobrescrever silenciosamente uma versão publicada.

------------------------------------------------------------------------

# 52. Release

A release deverá relacionar:

``` text
commit
+
build
+
image
+
digest
+
deploy
```

------------------------------------------------------------------------

# 53. Rastreabilidade

Deverá ser possível responder:

``` text
qual código
está rodando
neste container?
```

sem investigação manual extensa.

------------------------------------------------------------------------

# 54. Promoção entre Ambientes

Preferir:

``` text
build
→ registry
→ staging
→ aprovação
→ production
```

e não:

``` text
build staging
+
build production diferente
```

------------------------------------------------------------------------

# 55. Staging

Staging deverá validar a imagem candidata real.

------------------------------------------------------------------------

# 56. Production

Production deverá executar imagem explicitamente aprovada e
identificável.

------------------------------------------------------------------------

# 57. Rollback

A imagem anterior deverá permanecer disponível por janela suficiente
para rollback.

Rollback deverá apontar para artefato conhecido, não reconstruí-lo às
pressas.

------------------------------------------------------------------------

# 58. Retenção de Imagens

Definir retenção que preserve:

-   releases atuais;
-   rollback;
-   auditoria;
-   segurança.

Não manter builds temporários indefinidamente.

------------------------------------------------------------------------

# 59. Limpeza

Registry deverá possuir política de limpeza de:

-   builds de branches antigas;
-   imagens não promovidas;
-   artefatos expirados.

Nunca remover imagens necessárias para rollback ativo.

------------------------------------------------------------------------

# 60. Segurança da Supply Chain

A cadeia deverá ser protegida:

``` text
source
→ dependencies
→ build
→ image
→ registry
→ runtime
```

------------------------------------------------------------------------

# 61. Vulnerabilidades

Imagens deverão ser avaliadas para vulnerabilidades conhecidas.

Aplicar GSF-12.

------------------------------------------------------------------------

# 62. Scanning

Scanning poderá ocorrer:

-   no build;
-   no registry;
-   periodicamente.

Vulnerabilidade crítica deverá seguir política de tratamento.

------------------------------------------------------------------------

# 63. SBOM

A geração de SBOM deverá ser considerada para aumentar rastreabilidade
de componentes.

Quando adotada, deverá acompanhar a release ou ser recuperável a partir
dela.

------------------------------------------------------------------------

# 64. Proveniência

A plataforma deverá evoluir para registrar origem do artefato:

-   repositório;
-   commit;
-   pipeline;
-   horário;
-   builder.

------------------------------------------------------------------------

# 65. Assinatura de Imagens

Assinatura/verificação criptográfica poderá ser adotada conforme
maturidade da infraestrutura.

O objetivo é impedir execução de artefatos não autorizados.

------------------------------------------------------------------------

# 66. Dependências Confiáveis

Pacotes e imagens deverão vir de fontes confiáveis.

Evitar imagens desconhecidas apenas por conveniência.

------------------------------------------------------------------------

# 67. Atualização de Imagens Base

Imagens base deverão ser atualizadas periodicamente.

Um Dockerfile imutável por anos acumula vulnerabilidades.

------------------------------------------------------------------------

# 68. CI/CD

Somente CI/CD autorizado deverá publicar releases oficiais no registry.

Build local não deverá ser promovido diretamente para produção.

------------------------------------------------------------------------

# 69. Cache de Build

Cache poderá acelerar build.

Deverá ser invalidado corretamente quando dependências mudarem.

------------------------------------------------------------------------

# 70. Reprodutibilidade

Dado o mesmo commit e dependências controladas, o build deverá ser tão
reproduzível quanto tecnicamente possível.

------------------------------------------------------------------------

# 71. Ambientes de Desenvolvimento

Containers poderão padronizar ambiente local.

Devem reduzir diferenças de versão entre desenvolvedores.

------------------------------------------------------------------------

# 72. Docker Compose

Compose poderá ser utilizado para desenvolvimento e integração local
quando adequado.

Não deverá ser automaticamente considerado orquestrador oficial de
produção.

------------------------------------------------------------------------

# 73. Dados Locais

Volumes locais de development poderão ser descartáveis.

Nunca incluir dumps reais de production por padrão.

------------------------------------------------------------------------

# 74. Banco e Redis Locais

Development poderá subir serviços isolados em containers para reproduzir
arquitetura sem acessar infraestrutura real.

------------------------------------------------------------------------

# 75. Compatibilidade de Arquitetura

Build deverá considerar arquitetura do runtime:

``` text
amd64
arm64
```

quando relevante.

------------------------------------------------------------------------

# 76. Multi-Architecture

Imagens multi-architecture poderão ser adotadas se existirem runtimes
distintos.

Não adicionar complexidade sem necessidade.

------------------------------------------------------------------------

# 77. Observabilidade

Containers deverão expor contexto operacional suficiente.

Campos úteis:

``` text
service
environment
release
image
container
```

------------------------------------------------------------------------

# 78. Métricas

Monitorar:

-   CPU;
-   memória;
-   restart count;
-   startup time;
-   OOM;
-   health failures.

------------------------------------------------------------------------

# 79. Auditoria

Publicações e deploys de imagens oficiais deverão ser rastreáveis.

------------------------------------------------------------------------

# 80. Falhas de Build

Build que falha não deverá produzir release parcial considerada válida.

------------------------------------------------------------------------

# 81. Falhas de Pull

Runtime deverá alertar quando não conseguir obter a imagem.

Causas possíveis:

-   credencial;
-   tag inexistente;
-   registry indisponível;
-   rede.

------------------------------------------------------------------------

# 82. Falhas de Startup

Container que inicia e encerra repetidamente deverá ser detectado.

Não mascarar crash loops com restart infinito sem alerta.

------------------------------------------------------------------------

# 83. Imagem Corrompida ou Vulnerável

Quando uma imagem precisar ser retirada:

``` text
identificar releases afetadas
→ bloquear nova promoção
→ construir correção
→ redeploy
→ revogar/remover quando seguro
```

------------------------------------------------------------------------

# 84. Recuperação

Registry é parte da continuidade operacional.

A estratégia deverá permitir recuperar ou reconstruir imagens oficiais a
partir de código e pipeline controlados.

------------------------------------------------------------------------

# 85. Testes

Testar:

-   build limpo;
-   startup;
-   health;
-   shutdown;
-   web;
-   worker;
-   migrations/job;
-   usuário não-root;
-   ausência de secrets;
-   compatibilidade da imagem.

------------------------------------------------------------------------

# 86. Anti-Padrões

Evitar:

``` text
docker exec
→ editar código
dentro do container
de produção
```

------------------------------------------------------------------------

``` text
latest
como única identificação
da release
```

------------------------------------------------------------------------

``` text
.env
copiado para imagem
```

------------------------------------------------------------------------

``` text
container
rodando como root
sem necessidade
```

------------------------------------------------------------------------

``` text
uploads persistentes
no filesystem
do container
```

------------------------------------------------------------------------

``` text
build diferente
para staging
e production
da mesma release
```

------------------------------------------------------------------------

``` text
imagem oficial
construída em notebook local
e enviada manualmente
```

------------------------------------------------------------------------

``` text
registry
sem política de acesso
```

------------------------------------------------------------------------

``` text
imagem base
sem atualização
por tempo indefinido
```

------------------------------------------------------------------------

# 87. Arquitetura de Referência

``` text
                   SOURCE REPOSITORY
                          │
                          ▼
                    CI/CD PIPELINE
                          │
              ┌───────────┼───────────┐
              │           │           │
              ▼           ▼           ▼
            TEST       SECURITY      BUILD
                          │           │
                          └─────┬─────┘
                                ▼
                        CONTAINER IMAGE
                                │
                                ▼
                         PRIVATE REGISTRY
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
                  STAGING              PRODUCTION
                     │                     │
             ┌───────┼───────┐     ┌──────┼──────┐
             ▼       ▼       ▼     ▼      ▼      ▼
            WEB    WORKER  SCHED   WEB   WORKER  SCHED

Configuração e secrets
são injetados no runtime.
A imagem permanece a mesma.
```

------------------------------------------------------------------------

# 88. Checklist

## Build

-   [ ] Dockerfile versionado;
-   [ ] imagem base controlada;
-   [ ] `.dockerignore`;
-   [ ] dependências reproduzíveis;
-   [ ] multi-stage quando útil;
-   [ ] sem secrets.

## Runtime

-   [ ] usuário não-root;
-   [ ] processo em foreground;
-   [ ] graceful shutdown;
-   [ ] health check;
-   [ ] limites de recursos;
-   [ ] filesystem tratado como efêmero.

## Registry

-   [ ] privado;
-   [ ] autenticação;
-   [ ] acesso de push restrito;
-   [ ] tags identificáveis;
-   [ ] digest disponível;
-   [ ] retenção definida.

## Release

-   [ ] commit associado;
-   [ ] imagem única;
-   [ ] staging usa imagem candidata;
-   [ ] production promove o mesmo artefato;
-   [ ] rollback preservado.

## Segurança

-   [ ] scanning;
-   [ ] vulnerabilidades avaliadas;
-   [ ] imagens base atualizadas;
-   [ ] fontes confiáveis;
-   [ ] SBOM/proveniência em evolução.

## Observabilidade

-   [ ] CPU;
-   [ ] memória;
-   [ ] restarts;
-   [ ] OOM;
-   [ ] health;
-   [ ] release identificável.

------------------------------------------------------------------------

# 89. Documentos Relacionados

-   GINF-01 --- Arquitetura da Infraestrutura
-   GINF-02 --- Ambientes e Configuração
-   GINF-03 --- Rede, DNS, Proxy e TLS
-   GINF-04 --- Runtime Django e Workers
-   GINF-05 --- Banco de Dados e Persistência
-   GINF-06 --- Redis, Cache e Filas
-   GINF-07 --- Storage e Arquivos
-   GSF-09 --- Gestão de Segredos e Criptografia
-   GSF-12 --- Gestão de Vulnerabilidades
-   GSF-13 --- Gestão de Incidentes de Segurança
-   GSF-15 --- Secure Development Lifecycle
-   GOC --- GereIgreja Operations Center
-   GQF --- GereIgreja Quality Framework
-   GereIgreja Backend Engineering

------------------------------------------------------------------------

# 90. Princípios Finais

A unidade de deploy do GereIgreja deverá ser um artefato conhecido.

``` text
Código
→ Build
→ Imagem
→ Registry
→ Deploy
```

O princípio central é:

``` text
Build uma vez.
Identifique o artefato.
Promova o mesmo artefato.
Configure no runtime.
```

Containers deverão ser descartáveis.

Imagens deverão ser imutáveis.

Secrets deverão permanecer fora das imagens.

E production nunca deverá depender de alterações manuais realizadas
dentro de containers em execução.

------------------------------------------------------------------------

# 91. Status do Documento

**Pasta**

`docs/infraestrutura/`

**Arquivo**

`08-Containers-Imagens-e-Registry.md`

**Documento**

`GINF-08`

**Código**

`GINF-CONTAINERS-IMAGES-REGISTRY`

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

`GINF-07 — Storage e Arquivos`

**Próximo documento recomendado**

`09-CI-CD-Deploy-e-Rollback.md`
