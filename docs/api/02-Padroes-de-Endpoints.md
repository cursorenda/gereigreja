Pasta:

docs/api/

Arquivo:

02-Padroes-de-Endpoints.md

Documento:

GAPI-02

Código:

GAPI-ENDPOINT-STANDARDS

Família:

GAPI --- GereIgreja API Engineering

Frameworks relacionados:

GEA --- GereIgreja Enterprise Architecture GAF --- GereIgreja
Authentication Framework GSF --- GereIgreja Security Framework GQF ---
GereIgreja Quality Framework

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GAPI-02 --- Padrões de Endpoints

> "Um endpoint previsível reduz ambiguidades para quem consome,
> implementa, testa, monitora e mantém a plataforma."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com o GAPI-01
4.  Princípios
5.  Anatomia de um Endpoint
6.  Estrutura de URLs
7.  Prefixo da API
8.  Versionamento na URL
9.  Recursos e Coleções
10. Identificadores
11. Sub-recursos
12. Ações de Domínio
13. Métodos HTTP
14. GET
15. POST
16. PUT e PATCH
17. DELETE
18. HEAD e OPTIONS
19. Query Parameters
20. Path Parameters
21. Headers
22. Request Body
23. Content-Type
24. Status HTTP
25. Endpoints de Listagem
26. Endpoints de Detalhe
27. Endpoints de Criação
28. Endpoints de Atualização
29. Endpoints de Exclusão
30. Endpoints de Ação
31. Autenticação
32. Tenant
33. Autorização
34. Validação
35. Services e Selectors
36. Serialização
37. Erros
38. Paginação
39. Filtros
40. Busca
41. Ordenação
42. Expansão e Campos
43. Idempotência
44. Rate Limiting
45. Concorrência
46. Arquivos
47. Exportações
48. Webhooks
49. Endpoints Internos
50. Endpoints Administrativos
51. Segurança
52. Logging e Auditoria
53. Performance
54. Testes
55. Documentação
56. Nomenclatura
57. Anti-Padrões
58. Exemplo de Fluxo
59. Checklist
60. Documentos Relacionados
61. Princípios Finais
62. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece os padrões oficiais para criação e manutenção
de endpoints das APIs do GereIgreja.

Seu objetivo é garantir consistência entre módulos como:

-   membros;
-   secretaria;
-   financeiro;
-   comunicação;
-   departamentos;
-   EBD;
-   eventos;
-   patrimônio;
-   usuários;
-   configurações;
-   dashboards;
-   core.

Um consumidor não deverá precisar reaprender a estrutura da API a cada
módulo.

------------------------------------------------------------------------

# 2. Escopo

Este documento aplica-se a endpoints:

-   REST;
-   internos;
-   externos;
-   administrativos;
-   de integração;
-   de consulta;
-   de escrita;
-   de arquivos;
-   de relatórios;
-   de exportações;
-   utilizados por automações.

Webhooks possuem requisitos adicionais, mas também deverão observar os
princípios aplicáveis deste padrão.

------------------------------------------------------------------------

# 3. Relação com o GAPI-01

O GAPI-01 define a arquitetura da camada de APIs.

O GAPI-02 define como um endpoint individual deverá ser desenhado dentro
dessa arquitetura.

``` text
GAPI-01
Arquitetura
    ↓
GAPI-02
Padrão de Endpoint
    ↓
Implementação
```

------------------------------------------------------------------------

# 4. Princípios

Endpoints deverão ser:

-   previsíveis;
-   explícitos;
-   pequenos;
-   seguros;
-   tenant-aware;
-   testáveis;
-   observáveis;
-   documentáveis;
-   compatíveis com evolução.

O endpoint não deverá concentrar a regra de negócio.

------------------------------------------------------------------------

# 5. Anatomia de um Endpoint

Um endpoint poderá ser compreendido como:

``` text
Método
  +
URL
  +
Autenticação
  +
Tenant
  +
Permissão
  +
Entrada
  +
Regra de Negócio
  +
Resposta
  +
Efeitos Colaterais
```

Todos esses elementos deverão ser conhecidos durante sua implementação.

------------------------------------------------------------------------

# 6. Estrutura de URLs

URLs deverão representar recursos e relações de forma consistente.

Exemplo:

``` text
/api/v1/membros/
/api/v1/membros/{id}/
/api/v1/eventos/
/api/v1/departamentos/
```

Evitar verbos em URLs quando o método HTTP já representa a operação.

Preferir:

``` text
POST /api/v1/membros/
```

em vez de:

``` text
POST /api/v1/criar-membro/
```

------------------------------------------------------------------------

# 7. Prefixo da API

O prefixo recomendado é:

``` text
/api/
```

APIs versionadas deverão incluir a versão após o prefixo:

``` text
/api/v1/
```

------------------------------------------------------------------------

# 8. Versionamento na URL

Quando a API exigir contrato versionado, utilizar versão explícita.

Exemplo:

``` text
/api/v1/membros/
```

A versão deverá representar o contrato da API, não a versão interna da
aplicação.

------------------------------------------------------------------------

# 9. Recursos e Coleções

Coleções deverão utilizar substantivos consistentes.

Exemplos:

``` text
/membros/
/eventos/
/departamentos/
/usuarios/
/lancamentos/
```

Um item específico deverá utilizar identificador:

``` text
/membros/{id}/
```

------------------------------------------------------------------------

# 10. Identificadores

Identificadores recebidos pela API deverão ser tratados como entrada não
confiável.

A existência do ID não comprova:

-   autorização;
-   pertencimento ao tenant;
-   visibilidade;
-   validade da operação.

Fluxo obrigatório:

``` text
ID
 ↓
Validação
 ↓
Tenant
 ↓
Permissão
 ↓
Recurso
```

------------------------------------------------------------------------

# 11. Sub-recursos

Sub-recursos poderão ser utilizados quando houver relação clara.

Exemplo conceitual:

``` text
/departamentos/{id}/membros/
```

Evitar URLs excessivamente profundas.

A relação de domínio deverá ser clara e necessária.

------------------------------------------------------------------------

# 12. Ações de Domínio

Algumas operações não correspondem naturalmente a CRUD.

Nesses casos, ações explícitas poderão ser utilizadas.

Exemplos conceituais:

``` text
POST /api/v1/eventos/{id}/publicar/
POST /api/v1/usuarios/{id}/desativar/
POST /api/v1/relatorios/{id}/gerar/
```

A ação deverá representar uma operação real de domínio.

Não utilizar ações apenas para contornar modelagem inadequada.

------------------------------------------------------------------------

# 13. Métodos HTTP

Os métodos deverão seguir sua semântica.

  Método    Uso principal
  --------- -------------------------------------------
  GET       consultar
  POST      criar ou executar ação
  PUT       substituir representação quando aplicável
  PATCH     atualizar parcialmente
  DELETE    remover ou solicitar exclusão
  HEAD      metadados sem corpo
  OPTIONS   capacidades/protocolo

------------------------------------------------------------------------

# 14. GET

GET deverá ser utilizado para leitura.

GET não deverá:

-   criar registros;
-   alterar estado de negócio;
-   executar exclusões;
-   produzir efeitos colaterais relevantes.

Consultas deverão ser seguras para repetição.

------------------------------------------------------------------------

# 15. POST

POST deverá ser utilizado para:

-   criação;
-   comandos;
-   ações de domínio;
-   operações não idempotentes quando apropriado.

Operações críticas deverão avaliar chave de idempotência.

------------------------------------------------------------------------

# 16. PUT e PATCH

PATCH deverá ser preferido para atualização parcial quando o contrato
permitir.

PUT deverá ser utilizado quando houver semântica real de substituição da
representação.

A atualização deverá validar novamente:

-   tenant;
-   permissão;
-   campos permitidos;
-   regras de domínio.

------------------------------------------------------------------------

# 17. DELETE

DELETE deverá exigir autorização explícita.

Antes da implementação, avaliar:

-   exclusão física;
-   exclusão lógica;
-   retenção;
-   LGPD;
-   auditoria;
-   dependências;
-   impacto financeiro ou ministerial.

Nem todo recurso deverá permitir DELETE.

------------------------------------------------------------------------

# 18. HEAD e OPTIONS

HEAD e OPTIONS poderão ser suportados conforme necessidade do framework,
protocolo ou integração.

Eles não deverão introduzir regras de negócio paralelas.

------------------------------------------------------------------------

# 19. Query Parameters

Query parameters deverão ser utilizados para:

-   filtros;
-   busca;
-   ordenação;
-   paginação;
-   opções de representação.

Exemplo:

``` text
/api/v1/membros/?ativo=true&page=2
```

Parâmetros deverão ser validados.

------------------------------------------------------------------------

# 20. Path Parameters

Path parameters deverão identificar recursos ou contexto estrutural da
URL.

Exemplo:

``` text
/api/v1/membros/{id}/
```

O valor deverá ser validado antes do acesso ao recurso.

------------------------------------------------------------------------

# 21. Headers

Headers poderão transportar informações de protocolo, autenticação,
idempotência e rastreabilidade.

Exemplos conceituais:

``` text
Authorization
Content-Type
Accept
Idempotency-Key
X-Request-ID
```

Headers customizados deverão ser utilizados somente quando houver
justificativa.

------------------------------------------------------------------------

# 22. Request Body

O corpo deverá conter apenas dados necessários à operação.

Não aceitar indiscriminadamente todos os campos de um model.

O contrato de entrada deverá ser explícito.

------------------------------------------------------------------------

# 23. Content-Type

JSON deverá ser utilizado como formato padrão das APIs estruturadas,
salvo necessidade específica.

Exemplo:

``` text
Content-Type: application/json
```

Uploads poderão utilizar formatos apropriados, como
`multipart/form-data`.

------------------------------------------------------------------------

# 24. Status HTTP

Status HTTP deverão representar o resultado da operação.

Referência recomendada:

  Status   Uso
  -------- ---------------------------------------
  200      sucesso com resposta
  201      recurso criado
  202      processamento aceito/assíncrono
  204      sucesso sem corpo
  400      requisição inválida
  401      autenticação ausente ou inválida
  403      autenticado sem autorização
  404      recurso não encontrado ou não visível
  409      conflito
  422      validação semântica quando adotada
  429      limite de requisições
  500      erro interno

A família GAPI deverá manter uma convenção única para erros de
validação.

------------------------------------------------------------------------

# 25. Endpoints de Listagem

Listagens deverão considerar:

-   tenant;
-   autorização;
-   paginação;
-   filtros;
-   ordenação;
-   performance;
-   minimização de campos.

Não retornar coleções ilimitadas por padrão.

------------------------------------------------------------------------

# 26. Endpoints de Detalhe

Detalhes deverão recuperar o recurso dentro do tenant aplicável.

Não utilizar:

``` python
Model.objects.get(pk=id)
```

quando o recurso for organizacional e exigir isolamento.

A consulta deverá incorporar o escopo correto.

------------------------------------------------------------------------

# 27. Endpoints de Criação

Criação deverá seguir:

``` text
Request
   ↓
Authentication
   ↓
Tenant
   ↓
Permission
   ↓
Validation
   ↓
Service
   ↓
Persistence
   ↓
Audit
   ↓
201
```

O tenant não deverá ser confiado cegamente a partir do payload.

------------------------------------------------------------------------

# 28. Endpoints de Atualização

Atualização deverá controlar quais campos podem ser modificados.

Campos internos, administrativos ou derivados não deverão ser alteráveis
apenas porque existem no model.

------------------------------------------------------------------------

# 29. Endpoints de Exclusão

Exclusão deverá possuir comportamento documentado.

Quando houver soft delete, a API deverá definir claramente:

-   estado resultante;
-   visibilidade;
-   restauração;
-   auditoria.

------------------------------------------------------------------------

# 30. Endpoints de Ação

Ações deverão possuir nomes claros e corresponder a services explícitos.

Exemplo conceitual:

``` text
POST /api/v1/eventos/{id}/cancelar/
```

``` python
cancelar_evento(
    tenant=tenant,
    user=request.user,
    evento=evento,
)
```

------------------------------------------------------------------------

# 31. Autenticação

Endpoints protegidos deverão declarar o mecanismo de autenticação
aplicável.

Não deverá existir endpoint sensível protegido apenas por convenção do
frontend.

------------------------------------------------------------------------

# 32. Tenant

Todo endpoint organizacional deverá possuir estratégia explícita de
resolução de tenant.

O tenant poderá vir do contexto autenticado, organização atual ou
mecanismo arquitetural oficial.

Não aceitar `tenant_id` arbitrário como autoridade suficiente.

------------------------------------------------------------------------

# 33. Autorização

A permissão deverá ser verificada antes da operação.

Quando houver diferença entre:

-   visualizar;
-   criar;
-   alterar;
-   excluir;
-   exportar;
-   aprovar;
-   administrar;

as permissões deverão refletir essa diferença.

------------------------------------------------------------------------

# 34. Validação

Validação deverá ocorrer em camadas apropriadas.

``` text
Formato
  ↓
Contrato
  ↓
Domínio
  ↓
Permissão contextual
```

Mensagens de erro deverão ser úteis sem expor detalhes internos.

------------------------------------------------------------------------

# 35. Services e Selectors

Endpoints de escrita deverão delegar regras relevantes a services.

Endpoints de leitura poderão utilizar selectors.

``` text
GET
 ↓
Selector
 ↓
Serializer
```

``` text
POST/PATCH/DELETE
 ↓
Service
 ↓
Domain
```

Essa é uma orientação estrutural, não uma proibição absoluta de casos
simples.

------------------------------------------------------------------------

# 36. Serialização

Serializadores ou mecanismos equivalentes deverão possuir campos
explicitamente definidos.

A saída deverá respeitar:

-   autorização;
-   classificação da informação;
-   privacidade;
-   finalidade.

------------------------------------------------------------------------

# 37. Erros

Erros deverão seguir contrato comum.

Estrutura conceitual:

``` json
{
  "error": {
    "code": "validation_error",
    "message": "Não foi possível processar a requisição.",
    "fields": {}
  }
}
```

Detalhes técnicos internos deverão permanecer nos logs, não na resposta
pública.

------------------------------------------------------------------------

# 38. Paginação

Coleções potencialmente grandes deverão ser paginadas.

O padrão específico será definido no documento dedicado a filtros,
busca, ordenação e paginação.

------------------------------------------------------------------------

# 39. Filtros

Filtros deverão utilizar parâmetros documentados e validados.

Não permitir filtros arbitrários sobre qualquer campo do model sem
análise.

------------------------------------------------------------------------

# 40. Busca

Busca textual deverá possuir semântica previsível.

Deverá ser documentado:

-   quais campos participam;
-   sensibilidade a acentos quando relevante;
-   limites;
-   combinação com filtros.

------------------------------------------------------------------------

# 41. Ordenação

Ordenação deverá aceitar apenas campos permitidos.

Não repassar diretamente nomes arbitrários de campos para ORM.

------------------------------------------------------------------------

# 42. Expansão e Campos

Recursos como `include`, `expand` ou seleção dinâmica de campos somente
deverão ser adotados quando houver necessidade real.

A flexibilidade não deverá comprometer:

-   autorização;
-   performance;
-   privacidade;
-   estabilidade do contrato.

------------------------------------------------------------------------

# 43. Idempotência

Endpoints críticos deverão avaliar `Idempotency-Key` ou mecanismo
equivalente.

Casos prioritários:

-   lançamentos financeiros;
-   criação por integrações;
-   callbacks;
-   retries automáticos;
-   operações externas.

------------------------------------------------------------------------

# 44. Rate Limiting

Limites deverão ser proporcionais ao risco e custo.

Prioridade:

-   login;
-   recuperação de acesso;
-   endpoints públicos;
-   webhooks;
-   consultas pesadas;
-   exportações;
-   integrações externas.

------------------------------------------------------------------------

# 45. Concorrência

Operações suscetíveis a corrida deverão considerar:

-   transações;
-   locks;
-   versão do recurso;
-   unicidade;
-   idempotência.

Não assumir que duas requisições nunca ocorrerão simultaneamente.

------------------------------------------------------------------------

# 46. Arquivos

Endpoints de upload deverão validar:

-   tamanho;
-   extensão;
-   tipo real quando possível;
-   autorização;
-   tenant;
-   destino;
-   nome;
-   retenção.

Downloads deverão validar novamente autorização e tenant.

------------------------------------------------------------------------

# 47. Exportações

Exportações deverão ser tratadas como operações sensíveis.

Avaliar:

-   permissão específica;
-   volume;
-   dados pessoais;
-   auditoria;
-   geração assíncrona;
-   expiração do arquivo.

------------------------------------------------------------------------

# 48. Webhooks

Webhooks recebidos deverão possuir endpoint dedicado quando apropriado.

Fluxo recomendado:

``` text
Webhook
   ↓
Validação de Origem
   ↓
Validação do Payload
   ↓
Idempotência
   ↓
Persistência / Task
   ↓
Resposta Rápida
```

------------------------------------------------------------------------

# 49. Endpoints Internos

"Interno" não significa "sem segurança".

Endpoints internos deverão possuir proteção proporcional ao ambiente e
risco.

------------------------------------------------------------------------

# 50. Endpoints Administrativos

Endpoints administrativos deverão possuir:

-   autenticação forte;
-   autorização específica;
-   menor privilégio;
-   auditoria;
-   validação;
-   proteção contra uso fora do tenant.

------------------------------------------------------------------------

# 51. Segurança

Todo endpoint deverá ser analisado em relação a:

-   GSF-04;
-   GSF-05;
-   GSF-06;
-   GSF-07;
-   GSF-08;
-   GSF-10;
-   GSF-14;
-   GSF-15.

------------------------------------------------------------------------

# 52. Logging e Auditoria

Logs técnicos e auditoria de negócio possuem funções diferentes.

``` text
Logging
→ diagnóstico técnico

Auditoria
→ rastreabilidade da ação
```

Um endpoint poderá necessitar de ambos.

------------------------------------------------------------------------

# 53. Performance

Antes de publicar um endpoint de coleção ou relatório, avaliar:

-   quantidade de queries;
-   N+1;
-   índices;
-   paginação;
-   tamanho do payload;
-   tempo de serialização;
-   chamadas externas.

------------------------------------------------------------------------

# 54. Testes

Todo endpoint relevante deverá possuir testes para:

-   caminho feliz;
-   autenticação;
-   autorização;
-   tenant;
-   validação;
-   recurso inexistente;
-   conflito;
-   regressão.

Endpoints críticos deverão possuir testes de isolamento entre
organizações.

------------------------------------------------------------------------

# 55. Documentação

Cada endpoint deverá registrar, no mínimo:

``` text
Método
URL
Descrição
Autenticação
Permissão
Tenant
Parâmetros
Payload
Resposta
Status
Erros
Efeitos colaterais
```

Exemplos deverão utilizar dados fictícios.

------------------------------------------------------------------------

# 56. Nomenclatura

A nomenclatura deverá ser consistente entre:

-   URL;
-   domínio;
-   service;
-   selector;
-   documentação;
-   testes.

Evitar múltiplos nomes para o mesmo conceito.

------------------------------------------------------------------------

# 57. Anti-Padrões

Evitar:

``` text
GET /api/v1/excluir-membro/123/
```

------------------------------------------------------------------------

``` text
POST /api/v1/fazerTudo/
```

------------------------------------------------------------------------

``` text
/api/v1/igrejas/{tenant_id}/dados/
```

quando o `tenant_id` fornecido pelo cliente for utilizado sem validação
de contexto.

------------------------------------------------------------------------

``` text
Model.objects.get(pk=id)
```

para recursos multi-tenant sem escopo organizacional.

------------------------------------------------------------------------

``` text
return model.__dict__
```

ou qualquer serialização indiscriminada.

------------------------------------------------------------------------

``` text
except Exception:
    return 200
```

Erros não deverão ser escondidos com status de sucesso.

------------------------------------------------------------------------

``` text
Endpoint interno
=
endpoint confiável
```

------------------------------------------------------------------------

``` text
Frontend esconde botão
=
usuário não consegue executar ação
```

------------------------------------------------------------------------

# 58. Exemplo de Fluxo

Exemplo conceitual de atualização de membro:

``` text
PATCH /api/v1/membros/42/
          │
          ▼
     Authentication
          │
          ▼
     Tenant Context
          │
          ▼
      Permission
          │
          ▼
   Member Selector
   tenant=current
   id=42
          │
          ▼
      Validation
          │
          ▼
   atualizar_membro()
       Service
          │
          ▼
      Transaction
          │
          ▼
        Audit
          │
          ▼
     Serialization
          │
          ▼
       HTTP 200
```

O ID `42` sozinho nunca deverá ser suficiente para acessar o membro.

------------------------------------------------------------------------

# 59. Checklist

## Contrato

-   [ ] método correto;
-   [ ] URL consistente;
-   [ ] recurso identificado;
-   [ ] versão definida quando aplicável.

## Segurança

-   [ ] autenticação;
-   [ ] tenant;
-   [ ] autorização;
-   [ ] menor privilégio;
-   [ ] dados sensíveis avaliados.

## Entrada

-   [ ] path validado;
-   [ ] query validada;
-   [ ] body validado;
-   [ ] headers relevantes validados.

## Negócio

-   [ ] service utilizado quando necessário;
-   [ ] selector seguro;
-   [ ] transação avaliada;
-   [ ] concorrência avaliada;
-   [ ] idempotência avaliada.

## Saída

-   [ ] status correto;
-   [ ] campos mínimos;
-   [ ] contrato consistente;
-   [ ] erro padronizado.

## Operação

-   [ ] logging;
-   [ ] auditoria;
-   [ ] rate limiting avaliado;
-   [ ] performance avaliada;
-   [ ] monitoramento possível.

## Qualidade

-   [ ] testes de sucesso;
-   [ ] testes de erro;
-   [ ] testes de autorização;
-   [ ] testes multi-tenant;
-   [ ] documentação atualizada.

------------------------------------------------------------------------

# 60. Documentos Relacionados

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

## Backend

Consultar:

``` text
docs/backend/
```

Especialmente documentação de:

-   views;
-   services;
-   selectors;
-   permissions;
-   validators;
-   logging;
-   testing;
-   performance;
-   code standards.

## Segurança

-   GSF-04 --- Autorização e Controle de Acesso
-   GSF-05 --- Segurança Multi-Tenant
-   GSF-07 --- Segurança das APIs
-   GSF-08 --- Segurança de Dados e Privacidade
-   GSF-10 --- Logging, Monitoramento e Auditoria
-   GSF-15 --- Secure Development Lifecycle

## Autenticação

-   GAF --- GereIgreja Authentication Framework

## Arquitetura

-   GEA --- GereIgreja Enterprise Architecture

------------------------------------------------------------------------

# 61. Princípios Finais

Um bom endpoint deverá ser previsível antes mesmo de sua documentação
ser aberta.

O consumidor deverá reconhecer:

``` text
Recurso
   ↓
Método
   ↓
URL
   ↓
Entrada
   ↓
Resultado
```

A Engenharia deverá reconhecer:

``` text
Request
   ↓
Authentication
   ↓
Tenant
   ↓
Authorization
   ↓
Validation
   ↓
Service / Selector
   ↓
Serialization
   ↓
Response
```

O princípio final é:

``` text
Endpoint simples
não significa
segurança simples.

A interface pode ser pequena,
mas os controles precisam
estar completos.
```

No GereIgreja, consistência de endpoints é parte da arquitetura, da
segurança e da qualidade da plataforma.

------------------------------------------------------------------------

# 62. Status do Documento

**Pasta**

`docs/api/`

**Arquivo**

`02-Padroes-de-Endpoints.md`

**Documento**

`GAPI-02`

**Código**

`GAPI-ENDPOINT-STANDARDS`

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

`GAPI-01 — Arquitetura das APIs`

**Próximo documento recomendado**

`03-Autenticacao-Autorizacao-e-Tenant.md`
