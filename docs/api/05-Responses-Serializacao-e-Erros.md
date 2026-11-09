Pasta:

docs/api/

Arquivo:

05-Responses-Serializacao-e-Erros.md

Documento:

GAPI-05

Código:

GAPI-RESPONSE-SERIALIZATION-ERRORS

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

# GAPI-05 --- Responses, Serialização e Erros

> "Uma resposta de API é um contrato público: deve ser previsível para o
> consumidor, mínima para a privacidade e segura diante de falhas."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com os Documentos Anteriores
4.  Princípios
5.  Fluxo de Saída
6.  Contrato de Resposta
7.  JSON
8.  Content-Type
9.  Status HTTP
10. Respostas de Sucesso
11. HTTP 200
12. HTTP 201
13. HTTP 202
14. HTTP 204
15. Respostas de Cliente
16. HTTP 400
17. HTTP 401
18. HTTP 403
19. HTTP 404
20. HTTP 409
21. HTTP 422
22. HTTP 429
23. Erros de Servidor
24. HTTP 500
25. Estrutura Oficial de Erro
26. Códigos de Erro
27. Mensagens
28. Erros por Campo
29. Erros de Domínio
30. Erros de Autenticação
31. Erros de Autorização
32. Erros Multi-Tenant
33. Exceções
34. Mapeamento de Exceções
35. Serialização
36. Campos Permitidos
37. Campos Sensíveis
38. Campos Derivados
39. Relacionamentos
40. Objetos Aninhados
41. Coleções
42. Paginação
43. Datas e Horários
44. Valores Financeiros
45. Enumerações
46. Valores Nulos
47. Identificadores
48. Dados Pessoais
49. Respostas de Arquivos
50. Exportações
51. Processamento Assíncrono
52. Integrações Externas
53. Webhooks
54. Headers de Resposta
55. Request e Correlation ID
56. Cache HTTP
57. Compatibilidade
58. Logging
59. Auditoria
60. Segurança
61. Performance
62. Testes
63. Anti-Padrões
64. Exemplos
65. Checklist
66. Documentos Relacionados
67. Princípios Finais
68. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece o padrão oficial de respostas, serialização e
tratamento de erros das APIs do GereIgreja.

Seu objetivo é garantir que consumidores recebam contratos:

-   consistentes;
-   previsíveis;
-   seguros;
-   mínimos;
-   documentáveis;
-   compatíveis com evolução.

A resposta não deverá refletir diretamente a estrutura interna dos
models.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   APIs REST;
-   endpoints internos;
-   endpoints administrativos;
-   integrações;
-   webhooks quando houver resposta estruturada;
-   relatórios;
-   exportações;
-   processamento assíncrono;
-   respostas de erro.

------------------------------------------------------------------------

# 3. Relação com os Documentos Anteriores

``` text
GAPI-02
Endpoint
   ↓
GAPI-03
Identidade + Tenant + Autorização
   ↓
GAPI-04
Request + Validação
   ↓
Service / Selector
   ↓
GAPI-05
Serialização + Response + Erros
```

O GAPI-05 trata a fronteira de saída.

------------------------------------------------------------------------

# 4. Princípios

Toda resposta deverá observar:

-   contrato explícito;
-   status HTTP coerente;
-   minimização de dados;
-   serialização controlada;
-   erros previsíveis;
-   ausência de detalhes internos;
-   consistência entre módulos;
-   compatibilidade.

------------------------------------------------------------------------

# 5. Fluxo de Saída

``` text
Domain Result
    ↓
Authorization Context
    ↓
Serialization
    ↓
Privacy Filter
    ↓
Response Contract
    ↓
HTTP Status
    ↓
Client
```

O resultado interno não deverá ser enviado automaticamente ao
consumidor.

------------------------------------------------------------------------

# 6. Contrato de Resposta

Cada endpoint deverá documentar:

-   status;
-   estrutura;
-   campos;
-   tipos;
-   nullability;
-   paginação quando aplicável;
-   códigos de erro.

Exemplo conceitual:

``` json
{
  "id": 42,
  "nome": "Pessoa Exemplo",
  "ativo": true
}
```

------------------------------------------------------------------------

# 7. JSON

JSON deverá ser o formato padrão para respostas estruturadas quando
aplicável.

As chaves deverão seguir nomenclatura consistente em toda a família de
APIs.

------------------------------------------------------------------------

# 8. Content-Type

Respostas JSON deverão utilizar:

``` text
Content-Type: application/json
```

Outros formatos deverão ser explícitos, especialmente em arquivos e
exportações.

------------------------------------------------------------------------

# 9. Status HTTP

O status HTTP deverá representar o resultado real da operação.

Não utilizar `200` para esconder falhas.

------------------------------------------------------------------------

# 10. Respostas de Sucesso

Sucessos deverão retornar apenas os dados necessários ao consumidor.

Evitar envelopes redundantes sem necessidade.

A família GAPI deverá adotar uma convenção única por tipo de resposta.

------------------------------------------------------------------------

# 11. HTTP 200

Utilizar para operações concluídas com corpo de resposta.

Exemplos:

-   consulta;
-   atualização;
-   ação concluída com resultado.

------------------------------------------------------------------------

# 12. HTTP 201

Utilizar quando um recurso for criado com sucesso.

Quando aplicável, poderá ser retornado identificador ou representação do
recurso criado.

------------------------------------------------------------------------

# 13. HTTP 202

Utilizar quando a requisição for aceita, mas o processamento continuar
de forma assíncrona.

Exemplo conceitual:

``` json
{
  "status": "accepted",
  "operation_id": "op_123"
}
```

O consumidor deverá poder compreender que o resultado final ainda não
está disponível.

------------------------------------------------------------------------

# 14. HTTP 204

Utilizar quando a operação for concluída sem necessidade de corpo.

Uma resposta `204` não deverá conter JSON.

------------------------------------------------------------------------

# 15. Respostas de Cliente

Falhas provocadas por autenticação, autorização, contrato ou estado da
requisição deverão utilizar status 4xx adequado.

------------------------------------------------------------------------

# 16. HTTP 400

Utilizar para requisição inválida quando o contrato adotado classificar
a falha como `Bad Request`.

Exemplos:

-   JSON malformado;
-   parâmetro inválido;
-   estrutura incompatível.

------------------------------------------------------------------------

# 17. HTTP 401

Utilizar quando a operação exige autenticação e não existe identidade
válida.

Não expor detalhes sobre credenciais.

------------------------------------------------------------------------

# 18. HTTP 403

Utilizar quando o usuário autenticado não possui autorização para a
operação, conforme política da API.

------------------------------------------------------------------------

# 19. HTTP 404

Utilizar quando o recurso não estiver disponível no escopo da
requisição.

Em ambiente multi-tenant, poderá também evitar revelar a existência de
recursos de outra organização.

------------------------------------------------------------------------

# 20. HTTP 409

Utilizar quando houver conflito com o estado atual do recurso.

Exemplos conceituais:

-   operação incompatível com estado;
-   conflito de unicidade;
-   concorrência;
-   duplicidade detectada.

------------------------------------------------------------------------

# 21. HTTP 422

Poderá ser adotado para erros de validação semântica caso essa seja a
convenção oficial consolidada da família GAPI.

A escolha entre `400` e `422` deverá ser uniforme.

Não misturar convenções entre módulos sem justificativa.

------------------------------------------------------------------------

# 22. HTTP 429

Utilizar quando o cliente exceder limites definidos.

A resposta não deverá revelar detalhes que facilitem abuso.

------------------------------------------------------------------------

# 23. Erros de Servidor

Falhas inesperadas deverão ser tratadas como erros internos.

O consumidor deverá receber resposta segura.

Os detalhes técnicos deverão permanecer na observabilidade interna.

------------------------------------------------------------------------

# 24. HTTP 500

Utilizar para falha interna inesperada.

Exemplo seguro:

``` json
{
  "error": {
    "code": "internal_error",
    "message": "Não foi possível concluir a operação."
  }
}
```

Nunca retornar stack trace ao consumidor.

------------------------------------------------------------------------

# 25. Estrutura Oficial de Erro

Estrutura recomendada:

``` json
{
  "error": {
    "code": "validation_error",
    "message": "Existem dados inválidos.",
    "fields": {
      "email": [
        "Informe um endereço de e-mail válido."
      ]
    }
  }
}
```

Campos opcionais deverão possuir comportamento consistente.

------------------------------------------------------------------------

# 26. Códigos de Erro

`code` deverá ser estável e adequado para consumo programático.

Exemplos conceituais:

``` text
validation_error
authentication_required
permission_denied
not_found
conflict
rate_limit_exceeded
internal_error
```

Não utilizar a mensagem humana como identificador programático.

------------------------------------------------------------------------

# 27. Mensagens

`message` deverá ser compreensível e segura.

Não incluir:

-   SQL;
-   stack trace;
-   paths internos;
-   secrets;
-   tokens;
-   detalhes de infraestrutura.

------------------------------------------------------------------------

# 28. Erros por Campo

Falhas de validação poderão retornar erros associados aos campos.

Exemplo:

``` json
{
  "error": {
    "code": "validation_error",
    "message": "Existem dados inválidos.",
    "fields": {
      "nome": ["Este campo é obrigatório."],
      "data": ["Informe uma data válida."]
    }
  }
}
```

------------------------------------------------------------------------

# 29. Erros de Domínio

Regras de negócio deverão possuir códigos previsíveis quando o
consumidor precisar reagir programaticamente.

Exemplo conceitual:

``` json
{
  "error": {
    "code": "event_already_cancelled",
    "message": "O evento já está cancelado."
  }
}
```

Evitar transformar toda regra de domínio em erro genérico.

------------------------------------------------------------------------

# 30. Erros de Autenticação

Falhas de autenticação deverão ser discretas.

Evitar mensagens que confirmem indevidamente:

-   existência de conta;
-   validade parcial de credencial;
-   detalhes do mecanismo interno.

------------------------------------------------------------------------

# 31. Erros de Autorização

A resposta deverá indicar que a operação não pode ser executada sem
revelar informações sensíveis sobre permissões internas.

------------------------------------------------------------------------

# 32. Erros Multi-Tenant

A API não deverá informar ao usuário que determinado ID existe em outra
organização.

Conceitualmente:

``` text
fora do tenant
→ indisponível neste contexto
```

------------------------------------------------------------------------

# 33. Exceções

Exceções deverão representar falhas de forma estruturada na aplicação.

Não utilizar exceções genéricas para todos os cenários esperados.

------------------------------------------------------------------------

# 34. Mapeamento de Exceções

Deverá existir uma política consistente:

``` text
Validation Exception
        ↓
4xx

Permission Exception
        ↓
403 / política equivalente

Not Found
        ↓
404

Domain Conflict
        ↓
409

Unexpected Exception
        ↓
500
```

O mapeamento concreto deverá ser centralizado quando possível.

------------------------------------------------------------------------

# 35. Serialização

Serialização deverá transformar objetos internos em contratos externos.

``` text
Model / Domain
      ↓
Serializer
      ↓
API Contract
```

Essas estruturas não são necessariamente iguais.

------------------------------------------------------------------------

# 36. Campos Permitidos

Campos retornados deverão ser definidos explicitamente.

Preferir allowlist.

Não serializar automaticamente todos os campos do model.

------------------------------------------------------------------------

# 37. Campos Sensíveis

Campos sensíveis não deverão ser retornados por padrão.

Exemplos:

-   hashes;
-   secrets;
-   tokens;
-   credenciais;
-   metadados internos;
-   flags de segurança;
-   dados pessoais sem finalidade.

------------------------------------------------------------------------

# 38. Campos Derivados

Campos derivados poderão ser retornados quando fizerem parte do
contrato.

Exemplo:

``` json
{
  "nome_completo": "Pessoa Exemplo",
  "idade_aproximada": 30
}
```

O cálculo deverá ocorrer na camada apropriada.

------------------------------------------------------------------------

# 39. Relacionamentos

Relacionamentos deverão ser serializados conscientemente.

Evitar retornar árvores completas de objetos por padrão.

Exemplo simples:

``` json
{
  "departamento": {
    "id": 5,
    "nome": "Exemplo"
  }
}
```

quando esses campos forem realmente necessários.

------------------------------------------------------------------------

# 40. Objetos Aninhados

Objetos aninhados deverão considerar:

-   profundidade;
-   privacidade;
-   performance;
-   estabilidade;
-   autorização.

Evitar serialização recursiva sem limites.

------------------------------------------------------------------------

# 41. Coleções

Coleções deverão possuir contrato consistente.

Grandes coleções deverão utilizar paginação.

------------------------------------------------------------------------

# 42. Paginação

Uma resposta paginada poderá conceitualmente possuir:

``` json
{
  "results": [],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total": 0
  }
}
```

O formato oficial será consolidado no GAPI-06.

------------------------------------------------------------------------

# 43. Datas e Horários

Datas e horários deverão possuir formato interoperável e consistente.

Quando houver horário, timezone deverá ser tratado explicitamente.

Evitar formatos locais ambíguos no contrato da API.

------------------------------------------------------------------------

# 44. Valores Financeiros

Valores monetários deverão preservar precisão.

O contrato deverá definir claramente:

-   valor;
-   moeda quando aplicável;
-   representação.

Não depender de float binário como contrato financeiro.

------------------------------------------------------------------------

# 45. Enumerações

Enums deverão retornar valores estáveis.

Se também houver label humana, separar valor programático e apresentação
quando necessário.

Exemplo:

``` json
{
  "status": "ativo",
  "status_label": "Ativo"
}
```

------------------------------------------------------------------------

# 46. Valores Nulos

A semântica de `null` deverá ser conhecida.

Evitar alternar arbitrariamente entre:

``` json
null
```

``` json
""
```

e ausência do campo.

------------------------------------------------------------------------

# 47. Identificadores

IDs expostos fazem parte do contrato.

Mesmo quando um identificador não é secreto, ele nunca deverá substituir
autorização.

------------------------------------------------------------------------

# 48. Dados Pessoais

A resposta deverá aplicar minimização.

Pergunta obrigatória:

``` text
O consumidor precisa
deste campo para cumprir
a finalidade do endpoint?
```

Se não, o campo não deverá ser retornado.

------------------------------------------------------------------------

# 49. Respostas de Arquivos

Downloads deverão definir:

-   Content-Type;
-   nome seguro;
-   Content-Disposition quando aplicável;
-   autorização;
-   tenant;
-   política de cache.

------------------------------------------------------------------------

# 50. Exportações

Exportações poderão retornar arquivo diretamente ou operação assíncrona.

Para grandes volumes, preferir fluxo conceitual:

``` text
POST exportação
      ↓
202
      ↓
Task
      ↓
Arquivo protegido
      ↓
Download autorizado
```

------------------------------------------------------------------------

# 51. Processamento Assíncrono

Quando o resultado não estiver pronto, não retornar representação
fictícia de sucesso final.

Exemplo:

``` json
{
  "status": "processing",
  "operation_id": "op_123"
}
```

O ciclo de consulta do status deverá ser documentado quando existir.

------------------------------------------------------------------------

# 52. Integrações Externas

Erros de fornecedores externos não deverão ser repassados integralmente
ao consumidor.

A API deverá traduzuzi-los para seu próprio contrato.

Registrar detalhes técnicos internamente quando permitido.

------------------------------------------------------------------------

# 53. Webhooks

A resposta a webhook deverá ser simples e rápida.

Não incluir dados internos desnecessários.

O status deverá permitir ao fornecedor compreender se o evento foi
aceito conforme o contrato da integração.

------------------------------------------------------------------------

# 54. Headers de Resposta

Headers poderão comunicar informações de protocolo.

Exemplos:

``` text
Content-Type
Location
Retry-After
X-Request-ID
```

Headers customizados deverão possuir finalidade clara.

------------------------------------------------------------------------

# 55. Request e Correlation ID

Quando adotado, o identificador de requisição poderá ser devolvido ao
consumidor.

Exemplo:

``` text
X-Request-ID: ...
```

Isso facilita suporte sem expor detalhes internos.

------------------------------------------------------------------------

# 56. Cache HTTP

Respostas deverão avaliar política de cache.

Dados:

-   pessoais;
-   financeiros;
-   administrativos;
-   tenant-specific;

não deverão receber cache público inadequado.

------------------------------------------------------------------------

# 57. Compatibilidade

Adicionar, remover ou alterar campos poderá afetar consumidores.

Mudanças deverão seguir GAPI-07.

Não assumir que "apenas adicionar um campo" é sempre inofensivo para
consumidores estritos.

------------------------------------------------------------------------

# 58. Logging

Falhas deverão gerar contexto suficiente para diagnóstico.

Logs poderão registrar:

-   request ID;
-   endpoint;
-   status;
-   exception class;
-   tenant ID;
-   user ID.

Não registrar resposta sensível integralmente por padrão.

------------------------------------------------------------------------

# 59. Auditoria

A resposta HTTP não substitui auditoria.

Operações relevantes deverão registrar o evento de negócio
independentemente do payload retornado.

------------------------------------------------------------------------

# 60. Segurança

Respostas deverão prevenir:

-   exposição de secrets;
-   enumeração indevida;
-   vazamento cross-tenant;
-   exposição de stack trace;
-   excesso de dados;
-   cache inseguro.

------------------------------------------------------------------------

# 61. Performance

Serialização deverá evitar:

-   N+1;
-   objetos aninhados excessivos;
-   campos caros não utilizados;
-   payloads enormes;
-   cálculos repetidos.

A resposta deverá conter o necessário, não tudo que está disponível.

------------------------------------------------------------------------

# 62. Testes

Testar:

-   status correto;
-   estrutura;
-   tipos;
-   campos obrigatórios;
-   ausência de campos sensíveis;
-   erro de validação;
-   erro de autorização;
-   recurso fora do tenant;
-   erro de domínio;
-   erro inesperado seguro;
-   serialização de null;
-   datas;
-   valores financeiros;
-   paginação;
-   compatibilidade crítica.

------------------------------------------------------------------------

# 63. Anti-Padrões

Evitar:

``` python
return model.__dict__
```

------------------------------------------------------------------------

``` text
serializer = todos_os_campos
```

------------------------------------------------------------------------

``` text
erro ocorreu
→ HTTP 200
```

------------------------------------------------------------------------

``` text
except Exception as exc:
    return {"error": str(exc)}
```

------------------------------------------------------------------------

``` text
recurso de outro tenant
→ "Existe, mas pertence à igreja X"
```

------------------------------------------------------------------------

``` text
resposta de fornecedor
→ repassar integralmente ao cliente
```

------------------------------------------------------------------------

``` text
campo existe no banco
→ retornar na API
```

------------------------------------------------------------------------

``` text
status 500
→ stack trace no JSON
```

------------------------------------------------------------------------

# 64. Exemplos

## Sucesso

``` json
{
  "id": 42,
  "nome": "Pessoa Exemplo",
  "ativo": true
}
```

## Criação

``` text
HTTP 201
```

``` json
{
  "id": 42,
  "nome": "Pessoa Exemplo"
}
```

## Validação

``` text
HTTP 400 ou 422
conforme convenção consolidada
```

``` json
{
  "error": {
    "code": "validation_error",
    "message": "Existem dados inválidos.",
    "fields": {
      "email": [
        "Informe um endereço de e-mail válido."
      ]
    }
  }
}
```

## Sem autenticação

``` text
HTTP 401
```

``` json
{
  "error": {
    "code": "authentication_required",
    "message": "Autenticação necessária."
  }
}
```

## Sem permissão

``` text
HTTP 403
```

``` json
{
  "error": {
    "code": "permission_denied",
    "message": "Operação não autorizada."
  }
}
```

## Não encontrado

``` text
HTTP 404
```

``` json
{
  "error": {
    "code": "not_found",
    "message": "Recurso não encontrado."
  }
}
```

## Erro interno

``` text
HTTP 500
```

``` json
{
  "error": {
    "code": "internal_error",
    "message": "Não foi possível concluir a operação."
  }
}
```

------------------------------------------------------------------------

# 65. Checklist

## Status

-   [ ] status representa o resultado real;
-   [ ] criação usa status apropriado;
-   [ ] assíncrono usa status apropriado;
-   [ ] falhas não retornam 2xx.

## Serialização

-   [ ] allowlist de campos;
-   [ ] sem secrets;
-   [ ] sem campos internos;
-   [ ] relacionamentos controlados;
-   [ ] dados pessoais minimizados.

## Erros

-   [ ] estrutura consistente;
-   [ ] code estável;
-   [ ] message segura;
-   [ ] fields quando necessário;
-   [ ] sem stack trace;
-   [ ] sem SQL;
-   [ ] sem paths internos.

## Tenant

-   [ ] nenhum dado cross-tenant;
-   [ ] mensagens não revelam existência indevida;
-   [ ] cache respeita tenant.

## Formatos

-   [ ] datas consistentes;
-   [ ] horários/timezone definidos;
-   [ ] moeda precisa;
-   [ ] null consistente;
-   [ ] enums estáveis.

## Operação

-   [ ] request ID avaliado;
-   [ ] logging;
-   [ ] auditoria quando necessária;
-   [ ] performance da serialização avaliada.

## Testes

-   [ ] sucesso;
-   [ ] criação;
-   [ ] validação;
-   [ ] autenticação;
-   [ ] autorização;
-   [ ] tenant incorreto;
-   [ ] conflito;
-   [ ] erro interno seguro;
-   [ ] campos sensíveis ausentes.

------------------------------------------------------------------------

# 66. Documentos Relacionados

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

Especialmente:

-   exceptions;
-   views;
-   services;
-   selectors;
-   models;
-   logging;
-   testing;
-   performance.

## Segurança

-   GSF-05 --- Segurança Multi-Tenant
-   GSF-07 --- Segurança das APIs
-   GSF-08 --- Segurança de Dados e Privacidade
-   GSF-10 --- Logging, Monitoramento e Auditoria
-   GSF-14 --- Conformidade e LGPD
-   GSF-15 --- Secure Development Lifecycle

------------------------------------------------------------------------

# 67. Princípios Finais

A saída de uma API deverá ser tão controlada quanto sua entrada.

``` text
Objeto interno
não é
contrato externo.
```

Da mesma forma:

``` text
Exceção interna
não é
mensagem pública.
```

O padrão do GereIgreja deverá preservar:

``` text
Resultado
   ↓
Serialização explícita
   ↓
Minimização
   ↓
Contrato
   ↓
Status correto
```

Quando ocorrer uma falha:

``` text
Erro interno
   ├──► Log seguro
   ├──► Monitoramento
   └──► Resposta pública controlada
```

O consumidor deverá receber informação suficiente para usar corretamente
a API, mas nunca detalhes que comprometam segurança, privacidade,
isolamento multi-tenant ou estabilidade da plataforma.

------------------------------------------------------------------------

# 68. Status do Documento

**Pasta**

`docs/api/`

**Arquivo**

`05-Responses-Serializacao-e-Erros.md`

**Documento**

`GAPI-05`

**Código**

`GAPI-RESPONSE-SERIALIZATION-ERRORS`

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

`GAPI-04 — Requests, Payloads e Validação`

**Próximo documento recomendado**

`06-Filtros-Busca-Ordenacao-e-Paginacao.md`
