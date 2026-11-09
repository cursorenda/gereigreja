Pasta:

docs/infraestrutura/

Arquivo:

02-Ambientes-e-Configuracao.md

Documento:

GINF-02

Código:

GINF-ENVIRONMENTS-CONFIGURATION

Família:

GINF --- GereIgreja Infrastructure Engineering

Frameworks relacionados:

GEA --- GereIgreja Enterprise Architecture GSF --- GereIgreja Security
Framework GOC --- GereIgreja Operations Center GQF --- GereIgreja
Quality Framework GDF --- GereIgreja Documentation Framework GAPI ---
GereIgreja API Engineering

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GINF-02 --- Ambientes e Configuração

> "O mesmo software deve atravessar ambientes diferentes sem depender de
> alterações manuais, segredos embutidos ou conhecimento implícito."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Princípios
4.  Ambientes Oficiais
5.  Development
6.  Staging
7.  Production
8.  Ambientes Temporários
9.  Separação entre Ambientes
10. Paridade entre Ambientes
11. Configuração da Aplicação
12. Configuração por Ambiente
13. Variáveis de Ambiente
14. Secrets
15. Arquivos de Configuração
16. Configuração do Django
17. DEBUG
18. Hosts e Origens Confiáveis
19. Banco de Dados
20. Cache e Redis
21. Filas e Workers
22. E-mail
23. Storage
24. Integrações Externas
25. URLs e Domínios
26. Feature Flags
27. Configuração Multi-Tenant
28. Dados de Desenvolvimento
29. Dados de Staging
30. Dados de Produção
31. Migração de Configurações
32. Validação de Configuração
33. Fail Fast
34. Defaults
35. Configuração Opcional
36. Tipagem e Normalização
37. Versionamento
38. Build e Runtime
39. Configuração em Containers
40. Configuração em CI/CD
41. Configuração Local
42. Arquivo `.env`
43. Templates de Ambiente
44. Rotação
45. Auditoria de Mudanças
46. Permissões
47. Observabilidade
48. Segurança
49. LGPD
50. Backup de Configuração
51. Recuperação
52. Anti-Padrões
53. Estrutura de Referência
54. Checklist
55. Documentos Relacionados
56. Princípios Finais
57. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece o padrão oficial para ambientes e configuração
do GereIgreja.

Seu objetivo é garantir que:

-   ambientes sejam claramente separados;
-   configuração seja previsível;
-   secrets sejam protegidos;
-   deploys sejam reproduzíveis;
-   diferenças entre ambientes sejam intencionais;
-   produção não dependa de alterações manuais não rastreadas.

Este documento detalha os princípios estabelecidos em GINF-01.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   Django;
-   serviços web;
-   workers;
-   banco de dados;
-   Redis;
-   filas;
-   storage;
-   e-mail;
-   integrações;
-   CI/CD;
-   containers;
-   serviços de infraestrutura;
-   ferramentas operacionais.

------------------------------------------------------------------------

# 3. Princípios

A configuração deverá seguir:

``` text
Código
≠
Configuração
≠
Secret
```

Esses três elementos possuem ciclos e controles diferentes.

Princípios obrigatórios:

-   separação;
-   menor privilégio;
-   configuração externa;
-   validação;
-   rastreabilidade;
-   defaults seguros;
-   reprodução;
-   mínimo de diferenças entre ambientes.

------------------------------------------------------------------------

# 4. Ambientes Oficiais

Ambientes mínimos:

``` text
development
staging
production
```

Cada ambiente deverá possuir finalidade clara.

------------------------------------------------------------------------

# 5. Development

Development é destinado à construção e validação local.

Deverá permitir:

-   execução reproduzível;
-   dados fictícios;
-   debugging;
-   testes;
-   serviços locais ou isolados;
-   configuração simples e segura.

Development não deverá exigir credenciais de produção.

------------------------------------------------------------------------

# 6. Staging

Staging é destinado à validação pré-produção.

Deverá se aproximar de produção nos aspectos relevantes:

-   runtime;
-   serviços;
-   configuração estrutural;
-   deploy;
-   migrações;
-   integrações controladas.

Não é obrigatório possuir a mesma escala de produção.

------------------------------------------------------------------------

# 7. Production

Production é o ambiente que atende usuários reais.

Deverá possuir:

-   `DEBUG=False`;
-   secrets próprios;
-   banco próprio;
-   storage próprio;
-   cache próprio;
-   filas próprias;
-   observabilidade;
-   backups;
-   acesso restrito.

------------------------------------------------------------------------

# 8. Ambientes Temporários

Preview, QA ou ambientes efêmeros poderão existir.

Deverão possuir:

-   owner;
-   finalidade;
-   tempo de vida;
-   isolamento;
-   política de remoção.

Nunca utilizar secrets de produção automaticamente em ambientes
temporários.

------------------------------------------------------------------------

# 9. Separação entre Ambientes

A separação deverá ocorrer no mínimo em:

``` text
Credenciais
Banco
Cache
Filas
Storage
Domínios
Secrets
Logs
```

Quando recursos físicos forem compartilhados, o isolamento lógico deverá
ser explícito e seguro.

------------------------------------------------------------------------

# 10. Paridade entre Ambientes

Buscar paridade estrutural sem exigir igualdade de escala.

Exemplo:

``` text
Staging:
Django + PostgreSQL + Redis

Production:
Django + PostgreSQL + Redis
```

é preferível a validar em uma arquitetura completamente diferente da
produção.

------------------------------------------------------------------------

# 11. Configuração da Aplicação

Configuração deverá ser fornecida externamente sempre que variar entre
ambientes.

Exemplos:

-   URLs;
-   hosts;
-   credenciais;
-   feature flags;
-   limites;
-   integrações;
-   parâmetros operacionais.

------------------------------------------------------------------------

# 12. Configuração por Ambiente

Diferenças deverão ser explícitas.

Exemplo conceitual:

``` text
BASE CONFIGURATION
      │
      ├── development
      ├── staging
      └── production
```

Evitar duplicação integral de configuração quando uma base comum for
suficiente.

------------------------------------------------------------------------

# 13. Variáveis de Ambiente

Variáveis de ambiente são mecanismo oficial para injeção de parte da
configuração em runtime.

Nomenclatura deverá ser:

-   clara;
-   consistente;
-   documentada;
-   estável.

Exemplo:

``` text
DJANGO_DEBUG
DATABASE_URL
REDIS_URL
EMAIL_BACKEND
STORAGE_BUCKET
```

Os nomes reais deverão seguir o padrão adotado no código.

------------------------------------------------------------------------

# 14. Secrets

Secret não é apenas uma variável de ambiente.

A variável poderá transportar o secret, mas o valor deverá ser
armazenado em mecanismo seguro.

Exemplos:

-   password;
-   token;
-   API key;
-   private key;
-   secret key.

Aplicar GSF-09.

------------------------------------------------------------------------

# 15. Arquivos de Configuração

Arquivos versionados poderão conter configuração não sensível.

Nunca deverão conter:

``` text
senha real
token real
private key
credencial de produção
```

------------------------------------------------------------------------

# 16. Configuração do Django

A configuração Django deverá separar claramente:

-   valores comuns;
-   valores dependentes de ambiente;
-   secrets;
-   integrações.

O módulo de settings não deverá acumular lógica operacional
desnecessária.

------------------------------------------------------------------------

# 17. DEBUG

Produção deverá executar com:

``` python
DEBUG = False
```

`DEBUG=True` em produção é falha de segurança e configuração.

------------------------------------------------------------------------

# 18. Hosts e Origens Confiáveis

Configurações como:

``` text
ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS
CORS
```

deverão possuir valores explícitos por ambiente.

Não utilizar wildcard amplo em produção sem justificativa arquitetural.

------------------------------------------------------------------------

# 19. Banco de Dados

Cada ambiente deverá utilizar banco apropriado ao seu escopo.

``` text
development DB
≠
staging DB
≠
production DB
```

Credenciais também deverão ser distintas.

------------------------------------------------------------------------

# 20. Cache e Redis

Redis/cache deverá possuir separação entre ambientes.

Não depender somente de prefixos quando o risco justificar isolamento
mais forte.

------------------------------------------------------------------------

# 21. Filas e Workers

Filas deverão impedir que um worker de ambiente incorreto processe
mensagens de outro ambiente.

``` text
staging worker
X
production queue
```

Essa comunicação deverá ser impossível por configuração normal.

------------------------------------------------------------------------

# 22. E-mail

Development e staging deverão evitar envio acidental para usuários
reais.

Poderão utilizar:

-   backend local;
-   sandbox;
-   recipient override controlado.

Produção utilizará a integração oficial.

------------------------------------------------------------------------

# 23. Storage

Buckets, containers ou namespaces deverão ser separados conforme
necessidade.

Arquivos de produção não deverão ser utilizados livremente em
development.

------------------------------------------------------------------------

# 24. Integrações Externas

Quando o fornecedor oferecer sandbox, staging deverá preferi-lo.

Configurar separadamente:

``` text
endpoint
credential
webhook
environment
```

------------------------------------------------------------------------

# 25. URLs e Domínios

Cada ambiente deverá possuir URLs reconhecíveis.

Exemplo conceitual:

``` text
local
staging.gereigreja...
app.gereigreja...
```

Os domínios reais deverão ser documentados no inventário de
infraestrutura.

------------------------------------------------------------------------

# 26. Feature Flags

Feature flags não deverão substituir ambientes.

Uma flag poderá controlar comportamento, mas não deverá permitir mistura
insegura entre dados e serviços de ambientes diferentes.

------------------------------------------------------------------------

# 27. Configuração Multi-Tenant

Configuração global e configuração de tenant são conceitos distintos.

``` text
Infra Configuration
        │
        ▼
Application Configuration
        │
        ▼
Tenant Configuration
```

Nunca utilizar configuração de tenant para contornar controles globais
de segurança.

------------------------------------------------------------------------

# 28. Dados de Desenvolvimento

Development deverá utilizar preferencialmente:

-   fixtures;
-   factories;
-   dados sintéticos;
-   dados anonimizados quando formalmente permitido.

------------------------------------------------------------------------

# 29. Dados de Staging

Staging deverá evitar dados pessoais reais.

Se dados derivados de produção forem indispensáveis, deverão existir
processo formal de:

-   minimização;
-   anonimização;
-   autorização;
-   descarte.

------------------------------------------------------------------------

# 30. Dados de Produção

Dados reais pertencem ao ambiente de produção e aos fluxos oficialmente
autorizados.

Acesso deverá seguir GSF e GAF.

------------------------------------------------------------------------

# 31. Migração de Configurações

Alterações de configuração deverão acompanhar releases quando houver
dependência.

Ordem deverá ser planejada.

Exemplo:

``` text
adicionar configuração compatível
        ↓
deploy
        ↓
ativar comportamento
        ↓
remover configuração antiga
```

------------------------------------------------------------------------

# 32. Validação de Configuração

A aplicação deverá validar configurações críticas antes de atender
tráfego.

Exemplos:

-   variável obrigatória ausente;
-   URL inválida;
-   secret vazio;
-   configuração incompatível.

------------------------------------------------------------------------

# 33. Fail Fast

Configuração inválida deverá falhar cedo quando continuar a execução
representar risco.

É preferível:

``` text
startup falhar claramente
```

a:

``` text
aplicação iniciar
e falhar silenciosamente depois
```

------------------------------------------------------------------------

# 34. Defaults

Defaults deverão ser seguros.

Exemplo inadequado:

``` text
DEBUG default = True
```

para runtime potencialmente produtivo.

Valores sensíveis não deverão possuir defaults inseguros.

------------------------------------------------------------------------

# 35. Configuração Opcional

Configuração opcional deverá possuir comportamento conhecido quando
ausente.

Documentar:

-   default;
-   impacto;
-   ambiente aplicável.

------------------------------------------------------------------------

# 36. Tipagem e Normalização

Valores deverão ser convertidos explicitamente.

Uma variável textual:

``` text
"false"
```

não deverá ser interpretada incorretamente como booleano verdadeiro.

Validar tipos como:

-   boolean;
-   integer;
-   URL;
-   lista;
-   duração.

------------------------------------------------------------------------

# 37. Versionamento

Mudanças incompatíveis de configuração deverão acompanhar documentação e
release.

Variáveis obsoletas deverão possuir processo de depreciação.

------------------------------------------------------------------------

# 38. Build e Runtime

Preferir:

``` text
build once
configure at runtime
```

quando tecnicamente adequado.

O mesmo artefato deverá poder atravessar staging e production com
configurações diferentes.

------------------------------------------------------------------------

# 39. Configuração em Containers

Containers não deverão incorporar secrets na imagem.

``` text
IMAGE
+
runtime configuration
+
secret injection
```

A imagem deverá permanecer reutilizável.

------------------------------------------------------------------------

# 40. Configuração em CI/CD

Pipelines deverão acessar somente secrets necessários.

Evitar:

-   impressão em logs;
-   exposição em artifacts;
-   passagem desnecessária entre jobs.

------------------------------------------------------------------------

# 41. Configuração Local

Desenvolvedores deverão possuir forma documentada de preparar ambiente
local.

A configuração local deverá ser simples o suficiente para evitar
"configuração tribal".

------------------------------------------------------------------------

# 42. Arquivo `.env`

Arquivos `.env` poderão ser usados localmente conforme padrão do
projeto.

O arquivo contendo valores reais deverá estar fora do versionamento.

Exemplo versionável:

``` text
.env.example
```

Exemplo não versionável:

``` text
.env
```

com secrets locais.

------------------------------------------------------------------------

# 43. Templates de Ambiente

Manter template das variáveis necessárias.

Exemplo:

``` text
DATABASE_URL=
REDIS_URL=
DJANGO_SECRET_KEY=
EMAIL_BACKEND=
```

O template não deverá conter secrets reais.

------------------------------------------------------------------------

# 44. Rotação

Configurações sensíveis deverão suportar rotação quando aplicável.

Planejar mudanças que permitam transição sem indisponibilidade
desnecessária.

------------------------------------------------------------------------

# 45. Auditoria de Mudanças

Mudanças críticas em produção deverão ser rastreáveis.

Exemplos:

-   database endpoint;
-   secret;
-   domínio;
-   storage;
-   integração;
-   feature crítica.

------------------------------------------------------------------------

# 46. Permissões

Nem todos os membros da equipe precisam acessar todas as configurações.

Aplicar menor privilégio.

------------------------------------------------------------------------

# 47. Observabilidade

A aplicação deverá expor informações suficientes para identificar o
ambiente sem vazar secrets.

Logs poderão incluir:

``` text
environment=production
release=1.14.x
service=web
```

Nunca registrar credenciais.

------------------------------------------------------------------------

# 48. Segurança

Configuração é parte da superfície de segurança.

Falhas comuns:

-   debug ativo;
-   wildcard;
-   secret padrão;
-   banco exposto;
-   origem confiável ampla;
-   credencial reutilizada.

Aplicar GSF integralmente.

------------------------------------------------------------------------

# 49. LGPD

Configurações deverão evitar fluxo acidental de dados pessoais para:

-   sandbox;
-   logs;
-   development;
-   staging;
-   integrações erradas.

------------------------------------------------------------------------

# 50. Backup de Configuração

Configuração necessária para reconstrução deverá ser preservada de
maneira segura.

Isso não significa fazer cópia insegura de secrets.

A estratégia deverá preservar:

``` text
definição
+
processo
+
acesso seguro aos valores necessários
```

------------------------------------------------------------------------

# 51. Recuperação

Um ambiente crítico deverá poder ser reconstruído a partir de:

``` text
código
artefatos
infraestrutura definida
configuração documentada
secrets recuperáveis
backups de dados
```

------------------------------------------------------------------------

# 52. Anti-Padrões

Evitar:

``` text
if production:
    alterar código manualmente
```

------------------------------------------------------------------------

``` text
DEBUG=True
em produção
```

------------------------------------------------------------------------

``` text
development
usando banco de produção
```

------------------------------------------------------------------------

``` text
mesma API key
em todos os ambientes
```

------------------------------------------------------------------------

``` text
secret
commitado no Git
```

------------------------------------------------------------------------

``` text
.env de produção
enviado por chat
```

------------------------------------------------------------------------

``` text
configuração crítica
conhecida apenas por uma pessoa
```

------------------------------------------------------------------------

``` text
staging worker
consumindo fila de produção
```

------------------------------------------------------------------------

# 53. Estrutura de Referência

``` text
                    SOURCE CODE
                         │
                         ▼
                    BUILD ARTIFACT
                         │
             ┌───────────┼───────────┐
             │           │           │
             ▼           ▼           ▼
        DEVELOPMENT    STAGING    PRODUCTION
             │           │           │
             ▼           ▼           ▼
          CONFIG       CONFIG       CONFIG
             │           │           │
             ▼           ▼           ▼
          SECRETS      SECRETS      SECRETS
             │           │           │
             ▼           ▼           ▼
        RESOURCES     RESOURCES     RESOURCES

Nenhum ambiente deve depender
das credenciais ou dados do outro.
```

------------------------------------------------------------------------

# 54. Checklist

## Ambientes

-   [ ] development definido;
-   [ ] staging definido;
-   [ ] production definido;
-   [ ] finalidade documentada;
-   [ ] recursos separados adequadamente.

## Configuração

-   [ ] configuração externa;
-   [ ] variáveis documentadas;
-   [ ] tipos validados;
-   [ ] defaults seguros;
-   [ ] fail fast para valores críticos.

## Secrets

-   [ ] fora do código;
-   [ ] fora da documentação;
-   [ ] separados por ambiente;
-   [ ] menor privilégio;
-   [ ] rotação possível.

## Django

-   [ ] `DEBUG=False` em produção;
-   [ ] hosts explícitos;
-   [ ] CSRF configurado;
-   [ ] banco por ambiente;
-   [ ] cache por ambiente.

## Serviços

-   [ ] filas separadas;
-   [ ] storage separado;
-   [ ] e-mail seguro em staging;
-   [ ] integrações usam sandbox quando aplicável.

## Dados

-   [ ] production isolado;
-   [ ] development usa dados sintéticos;
-   [ ] staging evita dados reais;
-   [ ] LGPD considerada.

## Operação

-   [ ] mudanças rastreáveis;
-   [ ] configuração reconstruível;
-   [ ] CI/CD não vaza secrets;
-   [ ] logs identificam ambiente;
-   [ ] documentação atualizada.

------------------------------------------------------------------------

# 55. Documentos Relacionados

-   GINF-01 --- Arquitetura da Infraestrutura
-   GSF-03 --- GereIgreja Security Framework
-   GSF-05 --- Segurança Multi-Tenant
-   GSF-08 --- Segurança de Dados e Privacidade
-   GSF-09 --- Gestão de Segredos e Criptografia
-   GSF-10 --- Logging, Monitoramento e Auditoria
-   GSF-14 --- Conformidade e LGPD
-   GSF-15 --- Secure Development Lifecycle
-   GOC --- GereIgreja Operations Center
-   GQF --- GereIgreja Quality Framework
-   GDF --- GereIgreja Documentation Framework
-   GAPI --- GereIgreja API Engineering
-   GereIgreja Backend Engineering

------------------------------------------------------------------------

# 56. Princípios Finais

Ambientes deverão ser diferentes apenas onde existe motivo explícito
para serem diferentes.

O objetivo é permitir:

``` text
Código único
+
Artefato conhecido
+
Configuração controlada
+
Secrets protegidos
=
Deploy previsível
```

A regra central é:

``` text
Nenhum ambiente
deve depender acidentalmente
de dados, credenciais
ou recursos de outro ambiente.
```

A configuração do GereIgreja deverá ser tratada como parte da
arquitetura e da segurança, e não como detalhe informal de deploy.

------------------------------------------------------------------------

# 57. Status do Documento

**Pasta**

`docs/infraestrutura/`

**Arquivo**

`02-Ambientes-e-Configuracao.md`

**Documento**

`GINF-02`

**Código**

`GINF-ENVIRONMENTS-CONFIGURATION`

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

`GINF-01 — Arquitetura da Infraestrutura`

**Próximo documento recomendado**

`03-Rede-DNS-Proxy-e-TLS.md`
