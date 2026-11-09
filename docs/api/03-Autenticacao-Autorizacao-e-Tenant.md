Pasta:

docs/api/

Arquivo:

03-Autenticacao-Autorizacao-e-Tenant.md

Documento:

GAPI-03

Código:

GAPI-AUTH-AUTHZ-TENANT

Família:

GAPI --- GereIgreja API Engineering

Frameworks relacionados:

GAF --- GereIgreja Authentication Framework GSF --- GereIgreja Security
Framework GEA --- GereIgreja Enterprise Architecture GQF --- GereIgreja
Quality Framework

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GAPI-03 --- Autenticação, Autorização e Tenant

> "Identificar o usuário é apenas o início. Toda operação também precisa
> responder o que ele pode fazer e em qual organização."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com GAF, GSF e GEA
4.  Princípio Central
5.  Três Perguntas Obrigatórias
6.  Fluxo Oficial
7.  Autenticação
8.  Identidade do Usuário
9.  Sessões e Tokens
10. Credenciais
11. Usuários Inativos e Revogados
12. Autorização
13. Permissões
14. Papéis e Grupos
15. Menor Privilégio
16. Tenant
17. Organização Atual
18. Resolução do Tenant
19. Propagação do Tenant
20. Tenant em Queries
21. Tenant em Services
22. Tenant em Selectors
23. Tenant em Tasks
24. Tenant em Cache
25. Tenant em Arquivos
26. Tenant em Relatórios e Exportações
27. Tenant em Integrações
28. Tenant em Webhooks
29. Recursos Globais
30. Recursos Organizacionais
31. Recursos Compartilhados
32. Objetos por ID
33. Autorização por Objeto
34. Operações Administrativas
35. APIs Internas
36. APIs Externas
37. Máquina-a-Máquina
38. Impersonação e Suporte
39. Troca de Organização
40. Falhas de Autenticação
41. Falhas de Autorização
42. Recurso Fora do Tenant
43. Respostas HTTP
44. Logging
45. Auditoria
46. Privacidade
47. Segurança
48. Performance
49. Testes
50. Casos Obrigatórios de Teste
51. Anti-Padrões
52. Exemplo de Leitura
53. Exemplo de Escrita
54. Checklist
55. Documentos Relacionados
56. Princípios Finais
57. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece como autenticação, autorização e contexto
multi-tenant deverão funcionar nas APIs do GereIgreja.

Esses três controles deverão ser tratados de forma relacionada, mas não
confundidos.

Uma requisição autenticada não está automaticamente autorizada.

Uma requisição autorizada em uma organização não está automaticamente
autorizada em outra.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   APIs REST;
-   endpoints internos;
-   endpoints administrativos;
-   integrações;
-   webhooks autenticados;
-   serviços máquina-a-máquina;
-   relatórios;
-   exportações;
-   arquivos;
-   tasks disparadas por API.

------------------------------------------------------------------------

# 3. Relação com GAF, GSF e GEA

O GAF estabelece os fundamentos de identidade, autenticação e
autorização.

O GSF estabelece os controles de segurança.

A arquitetura multi-tenant do GEA estabelece o isolamento
organizacional.

O GAPI-03 traduz esses princípios para o fluxo concreto das APIs.

``` text
GAF
Identidade e Acesso
       +
GSF
Controles de Segurança
       +
GEA
Arquitetura Multi-Tenant
       ↓
GAPI-03
Controles da API
```

------------------------------------------------------------------------

# 4. Princípio Central

Toda operação protegida deverá possuir contexto suficiente para
responder:

``` text
Quem?
  +
Onde?
  +
Pode?
```

A ausência de qualquer uma dessas respostas deverá impedir operações
protegidas.

------------------------------------------------------------------------

# 5. Três Perguntas Obrigatórias

## Quem?

``` text
Quem está realizando
a requisição?
```

Responsabilidade principal:

-   autenticação;
-   identidade.

## Onde?

``` text
Em qual organização
a operação ocorre?
```

Responsabilidade principal:

-   tenant;
-   contexto organizacional.

## Pode?

``` text
O usuário pode executar
esta ação neste contexto?
```

Responsabilidade principal:

-   autorização;
-   permissões.

------------------------------------------------------------------------

# 6. Fluxo Oficial

``` text
Request
   ↓
Authentication
   ↓
User
   ↓
Tenant Resolution
   ↓
Current Organization
   ↓
Authorization
   ↓
Permission
   ↓
Resource Scope
   ↓
Service / Selector
   ↓
Response
```

Esse fluxo deverá ser preservado conceitualmente mesmo quando mecanismos
do framework executarem algumas etapas automaticamente.

------------------------------------------------------------------------

# 7. Autenticação

Autenticação deverá estabelecer uma identidade confiável para a
requisição.

A autenticação não deverá depender de parâmetros arbitrários enviados
pelo cliente para declarar quem ele é.

------------------------------------------------------------------------

# 8. Identidade do Usuário

Usuários deverão possuir identidade única e rastreável.

A API deverá utilizar a identidade autenticada como origem para:

-   autorização;
-   auditoria;
-   ownership;
-   tenant disponível;
-   ações administrativas.

Contas compartilhadas não deverão ser utilizadas.

------------------------------------------------------------------------

# 9. Sessões e Tokens

O mecanismo concreto poderá variar conforme o tipo de cliente.

Poderão existir, conforme arquitetura oficial:

-   sessão autenticada;
-   token;
-   credencial de integração;
-   identidade técnica.

Independentemente do mecanismo, deverão existir:

-   expiração quando aplicável;
-   revogação;
-   proteção da credencial;
-   rastreabilidade.

------------------------------------------------------------------------

# 10. Credenciais

Credenciais nunca deverão:

-   aparecer em URLs;
-   ser registradas integralmente em logs;
-   ser armazenadas em código;
-   ser retornadas por endpoints de consulta;
-   ser compartilhadas entre usuários.

Secrets de integração deverão seguir o GSF.

------------------------------------------------------------------------

# 11. Usuários Inativos e Revogados

Usuários inativos, bloqueados ou com acesso revogado não deverão
continuar operando APIs protegidas.

Revogação deverá produzir efeito coerente com o mecanismo de
autenticação utilizado.

------------------------------------------------------------------------

# 12. Autorização

Autorização deverá ocorrer depois que a identidade e o contexto
aplicável forem conhecidos.

``` text
Autenticação
≠
Autorização
```

A autorização deverá ser executada no backend.

------------------------------------------------------------------------

# 13. Permissões

Permissões deverão representar capacidades reais.

Exemplos conceituais:

``` text
membros.visualizar
membros.criar
membros.alterar
membros.excluir

financeiro.visualizar
financeiro.lancar
financeiro.aprovar
financeiro.exportar
```

Os nomes concretos deverão seguir o padrão oficial do GAF e da
plataforma.

------------------------------------------------------------------------

# 14. Papéis e Grupos

Papéis e grupos poderão facilitar atribuição de permissões.

Entretanto:

``` text
Papel
não substitui
verificação de permissão.
```

A API deverá avaliar a autorização efetiva.

------------------------------------------------------------------------

# 15. Menor Privilégio

Cada identidade deverá receber apenas as permissões necessárias.

Endpoints administrativos não deverão ser liberados apenas porque o
usuário possui acesso ao módulo.

------------------------------------------------------------------------

# 16. Tenant

Tenant representa o contexto organizacional no qual dados e operações
são executados.

No GereIgreja, o isolamento entre igrejas/organizações é requisito
estrutural.

``` text
Usuário
   ↓
Organização
   ↓
Recurso
```

------------------------------------------------------------------------

# 17. Organização Atual

Quando a plataforma possuir conceito de organização atual, esse contexto
deverá ser determinado de maneira confiável.

O cliente não deverá poder trocar de organização apenas alterando um ID
arbitrário no payload.

------------------------------------------------------------------------

# 18. Resolução do Tenant

A resolução deverá utilizar o mecanismo oficial da arquitetura.

Poderá envolver:

-   sessão;
-   contexto autenticado;
-   associação do usuário;
-   middleware;
-   domínio/subdomínio, se oficialmente adotado;
-   credencial de integração.

O mecanismo final deverá possuir uma única fonte de verdade por fluxo.

------------------------------------------------------------------------

# 19. Propagação do Tenant

Depois de resolvido, o tenant deverá acompanhar a operação.

``` text
Request
   ↓
Tenant
   ├──► Permission
   ├──► Selector
   ├──► Service
   ├──► Audit
   └──► Task
```

Evitar reconstruir o contexto organizacional de formas diferentes em
cada camada.

------------------------------------------------------------------------

# 20. Tenant em Queries

Toda query organizacional deverá possuir escopo de tenant.

Exemplo conceitual:

``` python
Membro.objects.filter(
    organizacao=tenant,
    ...
)
```

ou através do manager/selector oficial equivalente.

Não utilizar consultas globais e filtrar posteriormente em memória.

------------------------------------------------------------------------

# 21. Tenant em Services

Services que alteram dados organizacionais deverão receber tenant
explicitamente ou por contexto arquitetural inequívoco.

Exemplo:

``` python
def atualizar_membro(*, tenant, user, membro, data):
    ...
```

O service não deverá confiar apenas no objeto recebido sem validar seu
contexto quando isso for necessário.

------------------------------------------------------------------------

# 22. Tenant em Selectors

Selectors deverão aplicar o isolamento na própria consulta.

Preferir:

``` python
def obter_membro(*, tenant, membro_id):
    ...
```

a:

``` python
def obter_membro(membro_id):
    ...
```

quando o recurso for multi-tenant.

------------------------------------------------------------------------

# 23. Tenant em Tasks

Tasks assíncronas deverão preservar contexto organizacional.

Uma task não deverá depender da organização atual de uma sessão HTTP que
já não existe.

Payload conceitual:

``` text
task
├── tenant_id
├── actor_id
├── resource_id
└── correlation_id
```

Enviar apenas identificadores necessários.

------------------------------------------------------------------------

# 24. Tenant em Cache

Caches de dados organizacionais deverão incorporar tenant na chave.

Exemplo conceitual:

``` text
tenant:{tenant_id}:dashboard:{user_id}
```

Cache global de dados multi-tenant sem isolamento é proibido.

------------------------------------------------------------------------

# 25. Tenant em Arquivos

Uploads e downloads deverão possuir vínculo organizacional quando o
arquivo pertencer a uma organização.

A autorização de download deverá ser reavaliada no momento do acesso.

Conhecer a URL do arquivo não deverá significar autorização.

------------------------------------------------------------------------

# 26. Tenant em Relatórios e Exportações

Relatórios deverão aplicar tenant antes da geração.

Exportações deverão ser consideradas operações sensíveis.

Nunca gerar exportação global e depois tentar remover registros de
outras organizações.

------------------------------------------------------------------------

# 27. Tenant em Integrações

Credenciais, configurações e dados de integrações poderão ser
específicos por organização.

A integração deverá identificar claramente:

``` text
Qual tenant?
Qual credencial?
Qual operação?
```

------------------------------------------------------------------------

# 28. Tenant em Webhooks

Webhooks poderão não possuir usuário humano.

Nesses casos, o tenant deverá ser resolvido através de contexto
confiável da integração.

Exemplos conceituais:

-   credencial;
-   configuração vinculada;
-   identificador previamente registrado;
-   assinatura validada.

Nunca confiar apenas em `tenant_id` enviado no corpo do webhook.

------------------------------------------------------------------------

# 29. Recursos Globais

Alguns recursos poderão ser globais à plataforma.

Esses casos deverão ser explicitamente classificados.

"Não possui tenant" deverá ser uma decisão arquitetural, não ausência
acidental de filtro.

------------------------------------------------------------------------

# 30. Recursos Organizacionais

Recursos organizacionais deverão possuir vínculo claro com a
organização.

Esse vínculo deverá ser considerado em:

-   leitura;
-   escrita;
-   exclusão;
-   exportação;
-   cache;
-   auditoria.

------------------------------------------------------------------------

# 31. Recursos Compartilhados

Se algum recurso puder ser compartilhado entre organizações, o modelo de
acesso deverá ser explícito.

Não tratar compartilhamento como exceção informal ao isolamento.

------------------------------------------------------------------------

# 32. Objetos por ID

Um dos principais riscos multi-tenant é acesso direto por identificador.

Exemplo inseguro:

``` python
membro = Membro.objects.get(pk=membro_id)
```

Exemplo conceitualmente correto:

``` python
membro = Membro.objects.get(
    pk=membro_id,
    organizacao=tenant,
)
```

ou selector/manager equivalente.

------------------------------------------------------------------------

# 33. Autorização por Objeto

Algumas operações poderão exigir autorização além da permissão geral.

Exemplo:

``` text
Usuário pode visualizar membros
        +
Membro pertence ao tenant
        +
Regra específica permite acesso
```

Essas condições deverão ser avaliadas no backend.

------------------------------------------------------------------------

# 34. Operações Administrativas

Operações administrativas deverão possuir controles adicionais quando
apropriado.

Exemplos:

-   alteração de permissões;
-   acesso a configurações;
-   gestão de usuários;
-   exportações amplas;
-   ações financeiras;
-   suporte técnico.

Auditoria deverá ser avaliada como obrigatória.

------------------------------------------------------------------------

# 35. APIs Internas

APIs internas continuam sujeitas a:

-   autenticação;
-   autorização;
-   tenant;
-   validação.

A localização em rede privada não deverá ser a única proteção de
operações sensíveis.

------------------------------------------------------------------------

# 36. APIs Externas

APIs externas deverão possuir contrato de autenticação claramente
definido.

Também deverão avaliar:

-   rate limiting;
-   revogação;
-   scopes;
-   rotação de credenciais;
-   monitoramento.

------------------------------------------------------------------------

# 37. Máquina-a-Máquina

Identidades técnicas deverão ser distintas de usuários humanos.

Cada integração deverá possuir:

-   identidade;
-   finalidade;
-   escopo;
-   credencial;
-   revogação;
-   auditoria.

Evitar uma credencial global para todas as integrações.

------------------------------------------------------------------------

# 38. Impersonação e Suporte

Caso exista funcionalidade de impersonação, ela deverá ser tratada como
operação altamente privilegiada.

Deverá possuir:

-   autorização específica;
-   indicação clara;
-   auditoria;
-   actor original;
-   usuário representado;
-   tenant;
-   início e término rastreáveis.

Nunca sobrescrever a identidade original nos registros de auditoria.

------------------------------------------------------------------------

# 39. Troca de Organização

Quando um usuário pertencer a múltiplas organizações, a troca de
contexto deverá validar sua associação.

Fluxo:

``` text
Usuário
   ↓
Solicita organização
   ↓
Valida associação
   ↓
Define organização atual
   ↓
Recalcula contexto de acesso
```

------------------------------------------------------------------------

# 40. Falhas de Autenticação

Quando não houver identidade válida, a operação protegida deverá ser
interrompida.

Resposta típica:

``` text
401 Unauthorized
```

Não revelar detalhes desnecessários sobre credenciais.

------------------------------------------------------------------------

# 41. Falhas de Autorização

Quando o usuário estiver autenticado, mas não possuir acesso:

``` text
403 Forbidden
```

poderá ser utilizado conforme o contrato da API.

Em determinados casos, ocultar a existência de recurso fora do escopo
poderá justificar `404`.

A convenção deverá ser consistente.

------------------------------------------------------------------------

# 42. Recurso Fora do Tenant

Recursos de outra organização não deverão ser retornados.

O comportamento recomendado deverá evitar confirmação indevida da
existência do recurso.

Conceitualmente:

``` text
ID existe globalmente
        +
não pertence ao tenant
        ↓
não está disponível
para esta requisição
```

------------------------------------------------------------------------

# 43. Respostas HTTP

Referência:

  Situação                                   Status típico
  ------------------------------------------ ---------------
  não autenticado                            401
  autenticado sem permissão                  403
  recurso indisponível no escopo             404
  autenticação válida e operação concluída   2xx

O contrato específico de erros será definido no GAPI-05.

------------------------------------------------------------------------

# 44. Logging

Logs poderão registrar identificadores necessários para diagnóstico:

-   user ID;
-   tenant ID;
-   endpoint;
-   request ID;
-   status;
-   duração.

Não registrar:

-   senha;
-   token completo;
-   secret;
-   cookie sensível.

------------------------------------------------------------------------

# 45. Auditoria

Eventos de segurança e negócio relevantes deverão registrar:

``` text
Quem?
O quê?
Quando?
Onde?
Em qual tenant?
Sobre qual recurso?
Qual resultado?
```

Em impersonação, registrar também o actor real.

------------------------------------------------------------------------

# 46. Privacidade

A autorização deverá ser combinada com minimização.

Ter permissão para acessar um recurso não significa necessariamente
receber todos os seus campos.

------------------------------------------------------------------------

# 47. Segurança

Este documento deverá ser aplicado em conjunto com:

-   GSF-03 --- Gestão de Identidade;
-   GSF-04 --- Autorização e Controle de Acesso;
-   GSF-05 --- Segurança Multi-Tenant;
-   GSF-07 --- Segurança das APIs;
-   GSF-08 --- Segurança de Dados e Privacidade;
-   GSF-10 --- Logging, Monitoramento e Auditoria.

------------------------------------------------------------------------

# 48. Performance

Segurança multi-tenant deverá ser eficiente, mas nunca removida como
"otimização".

Filtros de tenant deverão possuir suporte adequado de modelagem e
índices quando necessário.

------------------------------------------------------------------------

# 49. Testes

Testes deverão comprovar não apenas acesso permitido, mas também
isolamento.

``` text
Tenant A
não pode acessar
Tenant B
```

Esse cenário deverá ser tratado como requisito básico.

------------------------------------------------------------------------

# 50. Casos Obrigatórios de Teste

Para endpoints organizacionais relevantes:

-   usuário não autenticado;
-   usuário autenticado;
-   usuário sem permissão;
-   usuário com permissão;
-   recurso do tenant atual;
-   recurso de outro tenant;
-   ID inexistente;
-   tenant inválido;
-   usuário removido da organização;
-   usuário inativo;
-   operação administrativa;
-   tentativa de alterar tenant pelo payload.

Para endpoints críticos, adicionar testes de regressão específicos.

------------------------------------------------------------------------

# 51. Anti-Padrões

Proibido assumir:

``` text
request.user existe
=
pode executar
```

------------------------------------------------------------------------

``` text
tenant_id veio no JSON
=
tenant válido
```

------------------------------------------------------------------------

``` text
objeto existe
=
usuário pode acessá-lo
```

------------------------------------------------------------------------

``` text
usuário é admin em A
=
é admin em B
```

------------------------------------------------------------------------

``` text
endpoint interno
=
não precisa autorização
```

------------------------------------------------------------------------

``` text
frontend não mostra
=
backend está protegido
```

------------------------------------------------------------------------

``` text
cache acertou
=
resultado pertence ao tenant
```

------------------------------------------------------------------------

``` text
task foi criada por usuário autorizado
=
não precisa preservar tenant
```

------------------------------------------------------------------------

# 52. Exemplo de Leitura

Exemplo conceitual:

``` text
GET /api/v1/membros/42/
          │
          ▼
     Authentication
          │
          ▼
       User 17
          │
          ▼
   Current Tenant 5
          │
          ▼
membros.visualizar?
          │
          ▼
Selector:
tenant=5
membro_id=42
          │
          ▼
      Serializer
          │
          ▼
        200
```

Se o membro `42` pertencer ao tenant `9`, ele não deverá ser retornado.

------------------------------------------------------------------------

# 53. Exemplo de Escrita

``` text
POST /api/v1/financeiro/lancamentos/
              │
              ▼
         Authentication
              │
              ▼
          Tenant Context
              │
              ▼
     financeiro.lancar?
              │
              ▼
          Validation
              │
              ▼
   criar_lancamento(
       tenant,
       actor,
       data
   )
              │
              ▼
          Transaction
              │
              ▼
            Audit
              │
              ▼
             201
```

O `tenant` utilizado na criação deverá vir do contexto autorizado, não
de escolha arbitrária do payload.

------------------------------------------------------------------------

# 54. Checklist

## Identidade

-   [ ] identidade autenticada;
-   [ ] usuário ativo;
-   [ ] mecanismo revogável;
-   [ ] credenciais protegidas.

## Tenant

-   [ ] tenant resolvido;
-   [ ] associação validada;
-   [ ] tenant propagado;
-   [ ] query isolada;
-   [ ] cache isolado;
-   [ ] task preserva tenant.

## Autorização

-   [ ] permissão definida;
-   [ ] menor privilégio;
-   [ ] autorização no backend;
-   [ ] autorização por objeto avaliada;
-   [ ] operação administrativa protegida.

## Dados

-   [ ] recurso pertence ao tenant;
-   [ ] saída minimizada;
-   [ ] arquivo protegido;
-   [ ] exportação protegida.

## Observabilidade

-   [ ] user ID disponível;
-   [ ] tenant ID disponível;
-   [ ] request ID avaliado;
-   [ ] auditoria quando necessária;
-   [ ] secrets fora dos logs.

## Testes

-   [ ] não autenticado;
-   [ ] sem permissão;
-   [ ] tenant correto;
-   [ ] tenant incorreto;
-   [ ] recurso inexistente;
-   [ ] tentativa de manipular tenant;
-   [ ] regressões críticas.

------------------------------------------------------------------------

# 55. Documentos Relacionados

## API Engineering

-   GAPI-01 --- Arquitetura das APIs
-   GAPI-02 --- Padrões de Endpoints
-   GAPI-03 --- Autenticação, Autorização e Tenant
-   GAPI-04 --- Requests, Payloads e Validação
-   GAPI-05 --- Responses, Serialização e Erros
-   GAPI-06 --- Filtros, Busca, Ordenação e Paginação
-   GAPI-07 --- Versionamento e Compatibilidade
-   GAPI-08 --- Webhooks e Integrações
-   GAPI-09 --- Idempotência e Rate Limiting
-   GAPI-10 --- Segurança e Privacidade
-   GAPI-11 --- Logging, Monitoramento e Auditoria
-   GAPI-12 --- Testes de APIs
-   GAPI-13 --- Depreciação e Ciclo de Vida
-   GAPI-14 --- Mapa e Índice das APIs

## Segurança

-   GSF-03 --- Gestão de Identidade
-   GSF-04 --- Autorização e Controle de Acesso
-   GSF-05 --- Segurança Multi-Tenant
-   GSF-07 --- Segurança das APIs
-   GSF-08 --- Segurança de Dados e Privacidade
-   GSF-10 --- Logging, Monitoramento e Auditoria

## Autenticação

-   GAF --- GereIgreja Authentication Framework

## Arquitetura

-   GEA-08 --- Arquitetura Multi-Tenant

## Backend

Consultar:

``` text
docs/backend/
```

Especialmente:

-   permissions;
-   middlewares;
-   managers;
-   selectors;
-   services;
-   views;
-   testing.

------------------------------------------------------------------------

# 56. Princípios Finais

O GereIgreja deverá tratar identidade, autorização e tenant como
controles complementares.

``` text
IDENTIDADE
Quem é?
    +
TENANT
Onde está?
    +
AUTORIZAÇÃO
Pode fazer?
    ↓
ACESSO
```

Nenhuma dessas dimensões deverá substituir as demais.

O princípio operacional é:

``` text
Nunca consultar primeiro
e proteger depois.

O escopo de segurança
deve participar da própria
operação.
```

Em uma plataforma multi-tenant, uma consulta funcionalmente correta, mas
sem isolamento organizacional, é uma falha de segurança.

Por isso, toda API do GereIgreja deverá preservar identidade, tenant e
autorização desde a entrada da requisição até a resposta e seus efeitos
assíncronos.

------------------------------------------------------------------------

# 57. Status do Documento

**Pasta**

`docs/api/`

**Arquivo**

`03-Autenticacao-Autorizacao-e-Tenant.md`

**Documento**

`GAPI-03`

**Código**

`GAPI-AUTH-AUTHZ-TENANT`

**Família**

`GAPI — GereIgreja API Engineering`

**Versão**

`1.0`

**Status**

`OFICIAL`

**Responsável**

`Equipe de Engenharia`

**Última atualização**

`Agosto de 2026`

**Documento anterior**

`GAPI-02 — Padrões de Endpoints`

**Próximo documento recomendado**

`04-Requests-Payloads-e-Validacao.md`
