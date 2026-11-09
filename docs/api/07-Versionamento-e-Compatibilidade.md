Pasta:

docs/api/

Arquivo:

07-Versionamento-e-Compatibilidade.md

Documento:

GAPI-07

Código:

GAPI-VERSIONING-COMPATIBILITY

Família:

GAPI --- GereIgreja API Engineering

Frameworks relacionados:

GEA --- GereIgreja Enterprise Architecture GSF --- GereIgreja Security
Framework GQF --- GereIgreja Quality Framework GDF --- GereIgreja
Documentation Framework

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GAPI-07 --- Versionamento e Compatibilidade

> "Uma API pode evoluir sem obrigar todos os seus consumidores a
> evoluírem no mesmo instante."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com a Família GAPI
4.  Princípios
5.  Contrato de API
6.  O que Constitui uma Mudança
7.  Compatibilidade Retroativa
8.  Breaking Changes
9.  Mudanças Compatíveis
10. Mudanças Potencialmente Incompatíveis
11. Estratégia Oficial de Versionamento
12. Versionamento por URL
13. Versão do Contrato
14. Versão Interna da Aplicação
15. Quando Criar uma Nova Versão
16. Quando Não Criar uma Nova Versão
17. Endpoints Versionados
18. Recursos Versionados
19. Requests
20. Responses
21. Campos
22. Campos Obrigatórios
23. Campos Opcionais
24. Tipos de Dados
25. Enumerações
26. Valores Nulos
27. Status HTTP
28. Erros
29. Filtros
30. Busca
31. Ordenação
32. Paginação
33. Autenticação e Autorização
34. Multi-Tenant
35. Segurança
36. Mudanças de Regra de Negócio
37. Integrações
38. Webhooks
39. Clientes Internos
40. Frontend do GereIgreja
41. APIs Externas
42. Migração entre Versões
43. Execução Paralela
44. Depreciação
45. Sunset
46. Comunicação
47. Documentação
48. Changelog
49. Observabilidade
50. Testes de Compatibilidade
51. Testes de Contrato
52. Rollout
53. Rollback
54. Governança
55. Anti-Padrões
56. Exemplos
57. Checklist
58. Documentos Relacionados
59. Princípios Finais
60. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece os padrões oficiais de versionamento e
compatibilidade das APIs do GereIgreja.

Seu objetivo é permitir evolução controlada dos contratos sem provocar
quebra desnecessária de:

-   frontend;
-   integrações;
-   automações;
-   aplicativos;
-   serviços internos;
-   consumidores externos.

Versionamento deverá ser consequência de mudanças reais de contrato, não
de alterações internas de implementação.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   endpoints REST;
-   APIs internas com contratos persistentes;
-   APIs externas;
-   integrações;
-   webhooks;
-   payloads;
-   responses;
-   filtros;
-   paginação;
-   códigos de erro;
-   autenticação quando fizer parte do contrato.

------------------------------------------------------------------------

# 3. Relação com a Família GAPI

``` text
GAPI-01
Arquitetura
    ↓
GAPI-02 a GAPI-06
Contratos e comportamento
    ↓
GAPI-07
Evolução desses contratos
```

O GAPI-13 tratará especificamente de depreciação e ciclo de vida.

------------------------------------------------------------------------

# 4. Princípios

A evolução deverá observar:

-   estabilidade;
-   previsibilidade;
-   compatibilidade;
-   comunicação;
-   migração controlada;
-   segurança;
-   rastreabilidade;
-   documentação.

O objetivo não é impedir mudanças.

O objetivo é impedir mudanças inesperadas.

------------------------------------------------------------------------

# 5. Contrato de API

O contrato inclui mais do que a URL.

``` text
Contrato
├── método HTTP
├── URL
├── autenticação
├── autorização observável
├── parâmetros
├── payload
├── tipos
├── campos
├── response
├── status
├── erros
├── paginação
└── comportamento documentado
```

Alterações em qualquer desses elementos poderão afetar consumidores.

------------------------------------------------------------------------

# 6. O que Constitui uma Mudança

Uma mudança poderá ocorrer em:

-   rota;
-   método;
-   campo;
-   tipo;
-   enum;
-   obrigatoriedade;
-   semântica;
-   ordenação padrão;
-   paginação;
-   status;
-   código de erro;
-   autenticação;
-   limite;
-   regra observável.

Toda mudança deverá ser classificada antes da publicação.

------------------------------------------------------------------------

# 7. Compatibilidade Retroativa

Uma mudança é retrocompatível quando consumidores corretos do contrato
anterior continuam funcionando sem modificação.

Mesmo mudanças aparentemente aditivas deverão ser avaliadas contra
consumidores reais.

------------------------------------------------------------------------

# 8. Breaking Changes

Exemplos típicos:

-   remover endpoint;
-   alterar URL;
-   alterar método HTTP;
-   remover campo;
-   renomear campo;
-   mudar tipo;
-   tornar campo opcional em obrigatório no request;
-   mudar semântica de valor existente;
-   remover valor de enum;
-   mudar estrutura de erro;
-   alterar paginação de forma incompatível;
-   exigir nova autenticação sem transição.

Essas mudanças normalmente exigem nova versão ou processo formal de
migração.

------------------------------------------------------------------------

# 9. Mudanças Compatíveis

Exemplos geralmente compatíveis, sujeitos a avaliação:

-   novo endpoint;
-   novo filtro opcional;
-   novo campo opcional no request;
-   correção interna sem alteração observável;
-   melhoria de performance;
-   novo código interno não exposto.

Adicionar campo à response é frequentemente compatível, mas consumidores
estritos poderão falhar.

Por isso, deverá ser avaliado.

------------------------------------------------------------------------

# 10. Mudanças Potencialmente Incompatíveis

Exemplos:

``` text
Adicionar campo à response
Alterar ordenação padrão
Aumentar precisão
Alterar mensagem humana de erro
Adicionar novo valor de enum
Reduzir limite máximo
```

Essas mudanças deverão ser analisadas conforme o contrato e
consumidores.

------------------------------------------------------------------------

# 11. Estratégia Oficial de Versionamento

Quando houver necessidade de versionamento público do contrato, utilizar
versão maior explícita na URL:

``` text
/api/v1/
```

Nova versão incompatível:

``` text
/api/v2/
```

Não criar nova versão para cada alteração pequena.

------------------------------------------------------------------------

# 12. Versionamento por URL

Exemplo:

``` text
GET /api/v1/membros/
GET /api/v2/membros/
```

A versão deverá ser facilmente identificável por:

-   consumidores;
-   logs;
-   monitoramento;
-   documentação;
-   suporte.

------------------------------------------------------------------------

# 13. Versão do Contrato

`v1` representa uma geração do contrato.

Não significa:

-   release 1 da aplicação;
-   versão do Django;
-   versão do módulo;
-   versão do banco.

------------------------------------------------------------------------

# 14. Versão Interna da Aplicação

O GereIgreja poderá receber centenas de releases enquanto a API
permanece em `v1`.

``` text
Aplicação
1.0
1.1
1.2
2.0
...

API
v1
```

Somente uma quebra relevante do contrato justifica `v2`.

------------------------------------------------------------------------

# 15. Quando Criar uma Nova Versão

Considerar nova versão quando:

-   mudanças incompatíveis forem necessárias;
-   múltiplas alterações estruturais forem agrupadas;
-   a manutenção do contrato antigo impedir evolução adequada;
-   houver plano de migração.

Nova versão deverá ser decisão arquitetural, não escolha isolada de um
endpoint.

------------------------------------------------------------------------

# 16. Quando Não Criar uma Nova Versão

Não criar versão nova apenas por:

-   refatoração;
-   troca de service;
-   mudança de ORM;
-   índice novo;
-   otimização;
-   correção que restaura contrato documentado;
-   reorganização interna.

------------------------------------------------------------------------

# 17. Endpoints Versionados

Endpoints pertencentes a uma mesma geração de contrato deverão
preferencialmente permanecer sob o mesmo prefixo.

Evitar fragmentação arbitrária:

``` text
/v1/membros/
/v2/eventos/
/v7/financeiro/
```

sem estratégia arquitetural.

------------------------------------------------------------------------

# 18. Recursos Versionados

A versão pertence à interface da API.

Models internos não deverão ser duplicados automaticamente para cada
versão.

Quando possível:

``` text
v1 Serializer ─┐
               ├──► Service / Domain
v2 Serializer ─┘
```

Isso reduz duplicação de regra de negócio.

------------------------------------------------------------------------

# 19. Requests

Ao evoluir requests, avaliar:

-   novos campos;
-   campos removidos;
-   obrigatoriedade;
-   defaults;
-   tipos;
-   validações.

Novo campo obrigatório normalmente quebra consumidores existentes.

------------------------------------------------------------------------

# 20. Responses

Mudanças de response deverão considerar:

-   estrutura;
-   campos;
-   tipos;
-   null;
-   ordem quando consumidores incorretamente dependerem dela;
-   objetos aninhados.

Não utilizar serialização acidental como contrato.

------------------------------------------------------------------------

# 21. Campos

Renomear:

``` text
nome
→ nome_completo
```

é breaking change se o consumidor utiliza `nome`.

Uma transição poderá temporariamente suportar ambos quando apropriado.

------------------------------------------------------------------------

# 22. Campos Obrigatórios

Transformar campo opcional em obrigatório no request é mudança
incompatível.

Quando necessário, utilizar:

-   nova versão;
-   default;
-   período de transição;
-   migração coordenada.

------------------------------------------------------------------------

# 23. Campos Opcionais

Adicionar campo opcional ao request tende a ser compatível.

Ainda assim, sua semântica deverá ser documentada.

------------------------------------------------------------------------

# 24. Tipos de Dados

Alterar:

``` text
integer
→ string
```

é mudança de contrato.

Mesmo quando o conteúdo visual parece equivalente.

------------------------------------------------------------------------

# 25. Enumerações

Consumidores deverão idealmente tolerar novos valores quando o contrato
permitir evolução.

Porém, adicionar valor pode quebrar clientes com lógica exaustiva.

A introdução deverá ser avaliada e documentada.

------------------------------------------------------------------------

# 26. Valores Nulos

Alterar:

``` text
string
→ string | null
```

pode quebrar consumidores.

Nullability faz parte do contrato.

------------------------------------------------------------------------

# 27. Status HTTP

Alterar status observado poderá afetar lógica do cliente.

Exemplo:

``` text
200
→ 202
```

representa também mudança semântica: processamento deixou de ser
necessariamente concluído.

------------------------------------------------------------------------

# 28. Erros

Códigos de erro programáticos deverão ser estáveis dentro de uma versão.

Mensagens humanas poderão evoluir, mas não deverão ser utilizadas pelo
consumidor como código.

------------------------------------------------------------------------

# 29. Filtros

Remover ou renomear filtro é mudança de contrato.

Adicionar filtro opcional tende a ser compatível.

Alterar a semântica de filtro existente exige análise rigorosa.

------------------------------------------------------------------------

# 30. Busca

Alterar campos pesquisados poderá modificar resultados de forma
observável.

Mudanças relevantes deverão ser documentadas.

------------------------------------------------------------------------

# 31. Ordenação

Alterar ordenação padrão pode mudar:

-   telas;
-   paginação;
-   sincronizações;
-   testes;
-   exportações.

Não tratar como mudança puramente interna.

------------------------------------------------------------------------

# 32. Paginação

Alterações incompatíveis incluem:

-   mudar nomes dos campos;
-   trocar page por cursor sem transição;
-   remover total;
-   reduzir limites drasticamente;
-   alterar default de forma que afete consumidores sensíveis.

------------------------------------------------------------------------

# 33. Autenticação e Autorização

Segurança não deverá ser enfraquecida para preservar compatibilidade.

Quando um controle precisa ser fortalecido, deverá existir plano de
transição sempre que possível.

Correções urgentes de vulnerabilidade poderão exigir quebra imediata.

Segurança prevalece sobre compatibilidade.

------------------------------------------------------------------------

# 34. Multi-Tenant

Nenhuma versão poderá preservar comportamento que permita vazamento
cross-tenant.

Falhas de isolamento deverão ser corrigidas imediatamente, mesmo que
algum consumidor tenha dependido do comportamento incorreto.

------------------------------------------------------------------------

# 35. Segurança

Não manter por compatibilidade:

-   endpoint inseguro;
-   autenticação fraca obsoleta;
-   exposição de secrets;
-   vazamento de dados;
-   autorização incorreta.

A compatibilidade protege contratos legítimos, não vulnerabilidades.

------------------------------------------------------------------------

# 36. Mudanças de Regra de Negócio

Nem toda mudança de regra exige versão de API.

Pergunta:

``` text
O contrato observável mudou
de forma incompatível?
```

Se sim, avaliar versionamento.

Se não, poderá ser evolução interna/documental.

------------------------------------------------------------------------

# 37. Integrações

Integrações deverão declarar qual versão consomem.

Evitar integração sem versão quando o contrato possuir versionamento.

------------------------------------------------------------------------

# 38. Webhooks

Eventos enviados também possuem contrato.

Mudanças em:

-   event name;
-   payload;
-   tipos;
-   campos obrigatórios;
-   assinatura;

deverão possuir estratégia de compatibilidade.

Webhooks poderão possuir versão própria do schema quando necessário.

------------------------------------------------------------------------

# 39. Clientes Internos

Clientes internos também são consumidores.

Não assumir:

``` text
é nosso frontend
→ podemos quebrar sem processo
```

Mudanças coordenadas ainda deverão possuir testes e rollout.

------------------------------------------------------------------------

# 40. Frontend do GereIgreja

Quando frontend e backend forem publicados juntos, algumas migrações
poderão ser coordenadas.

Mesmo assim, preservar contrato claro ajuda:

-   testes;
-   rollback;
-   deploy gradual;
-   manutenção;
-   futuras integrações.

------------------------------------------------------------------------

# 41. APIs Externas

Contratos externos exigem maior disciplina.

Deverão possuir:

-   documentação;
-   versão explícita;
-   changelog;
-   política de depreciação;
-   comunicação de breaking changes.

------------------------------------------------------------------------

# 42. Migração entre Versões

Fluxo recomendado:

``` text
v1 ativa
   ↓
v2 implementada
   ↓
Testes
   ↓
Documentação
   ↓
Consumidores migram
   ↓
Métricas confirmam adoção
   ↓
v1 depreciada
   ↓
Sunset
```

------------------------------------------------------------------------

# 43. Execução Paralela

Quando necessário, duas versões poderão coexistir.

``` text
/api/v1/
/api/v2/
```

O período deverá ser controlado.

Evitar manter versões indefinidamente.

------------------------------------------------------------------------

# 44. Depreciação

Depreciação significa:

``` text
ainda funciona
+
não deve ser usada em novos desenvolvimentos
+
será removida futuramente
```

O processo completo será definido no GAPI-13.

------------------------------------------------------------------------

# 45. Sunset

Sunset é a retirada planejada de uma versão ou contrato.

Antes do sunset deverão ser avaliados:

-   consumidores ativos;
-   comunicação;
-   métricas;
-   documentação;
-   suporte;
-   riscos.

------------------------------------------------------------------------

# 46. Comunicação

Mudanças relevantes deverão ser comunicadas aos responsáveis pelos
consumidores.

A comunicação deverá informar:

-   o que mudou;
-   impacto;
-   versão;
-   ação necessária;
-   prazo quando aplicável.

------------------------------------------------------------------------

# 47. Documentação

Cada versão suportada deverá possuir documentação correspondente.

Não documentar somente a versão mais nova enquanto versões anteriores
continuam oficiais.

------------------------------------------------------------------------

# 48. Changelog

Mudanças de contrato deverão constar em changelog apropriado.

Categorias úteis:

``` text
Added
Changed
Deprecated
Removed
Fixed
Security
```

------------------------------------------------------------------------

# 49. Observabilidade

Métricas deverão permitir identificar uso por versão.

Exemplo:

``` text
API requests
├── v1
└── v2
```

Isso é essencial para decidir quando uma versão pode ser removida.

------------------------------------------------------------------------

# 50. Testes de Compatibilidade

Antes de alterar contrato existente, testar cenários do contrato
anterior.

A pergunta não é apenas:

``` text
A nova implementação funciona?
```

Também:

``` text
Os consumidores existentes
continuam funcionando?
```

------------------------------------------------------------------------

# 51. Testes de Contrato

Endpoints relevantes deverão possuir testes que fixem:

-   status;
-   estrutura;
-   campos;
-   tipos;
-   erros;
-   paginação;
-   comportamentos críticos.

Esses testes ajudam a detectar breaking changes acidentais.

------------------------------------------------------------------------

# 52. Rollout

Mudanças relevantes poderão exigir rollout gradual.

Avaliar:

-   feature flags;
-   consumidores selecionados;
-   ambiente de homologação;
-   métricas;
-   logs;
-   fallback.

------------------------------------------------------------------------

# 53. Rollback

A estratégia de mudança deverá considerar rollback.

Se uma nova versão depende de migração irreversível de dados, isso
deverá ser avaliado antes do deploy.

Compatibilidade de API e compatibilidade de dados são relacionadas, mas
distintas.

------------------------------------------------------------------------

# 54. Governança

Breaking changes deverão passar por revisão arquitetural proporcional ao
impacto.

A decisão deverá registrar:

-   motivo;
-   consumidores;
-   alternativa;
-   versão;
-   migração;
-   depreciação;
-   documentação.

------------------------------------------------------------------------

# 55. Anti-Padrões

Evitar:

``` text
mudou o serializer
→ pronto
```

------------------------------------------------------------------------

``` text
é só um campo
→ não pode quebrar
```

------------------------------------------------------------------------

``` text
frontend é nosso
→ compatibilidade não importa
```

------------------------------------------------------------------------

``` text
criar v2
para qualquer alteração
```

------------------------------------------------------------------------

``` text
manter v1 eternamente
```

------------------------------------------------------------------------

``` text
preservar vulnerabilidade
por compatibilidade
```

------------------------------------------------------------------------

``` text
remover endpoint
sem medir consumidores
```

------------------------------------------------------------------------

``` text
documentar v2
e apagar documentação de v1
enquanto v1 continua ativa
```

------------------------------------------------------------------------

# 56. Exemplos

## Mudança compatível

Contrato anterior:

``` json
{
  "id": 42,
  "nome": "Pessoa Exemplo"
}
```

Possível evolução:

``` json
{
  "id": 42,
  "nome": "Pessoa Exemplo",
  "ativo": true
}
```

A adição deverá ser avaliada contra consumidores estritos.

------------------------------------------------------------------------

## Mudança incompatível

Anterior:

``` json
{
  "nome": "Pessoa Exemplo"
}
```

Novo:

``` json
{
  "nome_completo": "Pessoa Exemplo"
}
```

Consumidores que esperam `nome` quebrarão.

------------------------------------------------------------------------

## Nova versão

``` text
GET /api/v1/membros/42/
GET /api/v2/membros/42/
```

As duas poderão utilizar o mesmo domínio interno com adaptadores de
contrato diferentes.

------------------------------------------------------------------------

# 57. Checklist

## Classificação

-   [ ] mudança identificada;
-   [ ] contrato afetado;
-   [ ] consumidores identificados;
-   [ ] compatibilidade avaliada;
-   [ ] impacto de segurança avaliado.

## Breaking Change

-   [ ] nova versão avaliada;
-   [ ] alternativa compatível avaliada;
-   [ ] migração definida;
-   [ ] depreciação planejada;
-   [ ] comunicação planejada.

## Contrato

-   [ ] requests revisados;
-   [ ] responses revisadas;
-   [ ] tipos revisados;
-   [ ] enums revisados;
-   [ ] status revisados;
-   [ ] erros revisados;
-   [ ] filtros revisados;
-   [ ] paginação revisada.

## Segurança

-   [ ] nenhuma vulnerabilidade mantida;
-   [ ] tenant preservado;
-   [ ] autorização preservada;
-   [ ] dados sensíveis protegidos.

## Operação

-   [ ] observabilidade por versão;
-   [ ] rollout definido;
-   [ ] rollback avaliado;
-   [ ] uso da versão antiga mensurável.

## Qualidade

-   [ ] testes de contrato;
-   [ ] testes de regressão;
-   [ ] documentação atualizada;
-   [ ] changelog atualizado.

------------------------------------------------------------------------

# 58. Documentos Relacionados

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

-   GSF --- GereIgreja Security Framework
-   GSF-07 --- Segurança das APIs
-   GSF-15 --- Secure Development Lifecycle

## Qualidade

-   GQF --- GereIgreja Quality Framework

## Documentação

-   GDF --- GereIgreja Documentation Framework

------------------------------------------------------------------------

# 59. Princípios Finais

Versionamento não deverá esconder falta de governança.

``` text
Mudança
   ↓
Classificação
   ↓
Compatível?
  /       \
Sim       Não
 ↓         ↓
v atual   Nova versão
           ↓
        Migração
           ↓
       Depreciação
```

O princípio central é:

``` text
Refatorar implementação
não exige nova API.

Quebrar contrato
exige estratégia.
```

Ao mesmo tempo:

``` text
Compatibilidade
nunca justifica
manter uma vulnerabilidade.
```

O GereIgreja deverá evoluir suas APIs de forma deliberada, mensurável e
documentada, permitindo crescimento da plataforma sem transformar cada
mudança em risco para seus consumidores.

------------------------------------------------------------------------

# 60. Status do Documento

**Pasta**

`docs/api/`

**Arquivo**

`07-Versionamento-e-Compatibilidade.md`

**Documento**

`GAPI-07`

**Código**

`GAPI-VERSIONING-COMPATIBILITY`

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

`GAPI-06 — Filtros, Busca, Ordenação e Paginação`

**Próximo documento recomendado**

`08-Webhooks-e-Integracoes.md`
