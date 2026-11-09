Pasta:

docs/api/

Arquivo:

06-Filtros-Busca-Ordenacao-e-Paginacao.md

Documento:

GAPI-06

Código:

GAPI-QUERY-COLLECTIONS

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

# GAPI-06 --- Filtros, Busca, Ordenação e Paginação

> "Uma coleção de API precisa continuar previsível, segura e eficiente
> mesmo quando o volume de dados cresce."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com a Arquitetura das APIs
4.  Princípios
5.  Fluxo Oficial de Consulta
6.  Coleções
7.  Query Parameters
8.  Filtros
9.  Allowlist de Filtros
10. Tipos de Filtros
11. Filtros Booleanos
12. Filtros por Enumeração
13. Filtros por Data
14. Filtros por Intervalo
15. Filtros por Relacionamento
16. Filtros por Identificador
17. Filtros Multi-Tenant
18. Combinação de Filtros
19. Busca Textual
20. Campos Pesquisáveis
21. Normalização da Busca
22. Busca e Dados Sensíveis
23. Ordenação
24. Campos Ordenáveis
25. Direção da Ordenação
26. Ordenação Padrão
27. Ordenação Determinística
28. Paginação
29. Tamanho de Página
30. Limites Máximos
31. Formato da Resposta Paginada
32. Page-Based Pagination
33. Cursor-Based Pagination
34. Contagem Total
35. Tenant e Paginação
36. Autorização e Coleções
37. Selectors
38. ORM e Segurança
39. Performance
40. Índices
41. N+1 Queries
42. Cache
43. Relatórios e Dashboards
44. Exportações
45. APIs Externas
46. Compatibilidade
47. Erros
48. Logging e Monitoramento
49. Testes
50. Anti-Padrões
51. Exemplos
52. Checklist
53. Documentos Relacionados
54. Princípios Finais
55. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece os padrões oficiais para filtros, busca,
ordenação e paginação nas APIs do GereIgreja.

Seu objetivo é garantir que endpoints de coleção permaneçam:

-   previsíveis;
-   seguros;
-   multi-tenant;
-   eficientes;
-   documentados;
-   estáveis à medida que os dados crescem.

Listagens não deverão depender da existência de poucos registros.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a endpoints de coleção e consulta dos módulos do GereIgreja,
incluindo:

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

Também se aplica, quando pertinente, a:

-   relatórios;
-   exportações;
-   integrações;
-   APIs administrativas.

------------------------------------------------------------------------

# 3. Relação com a Arquitetura das APIs

O fluxo recomendado é:

``` text
Request
   ↓
Authentication
   ↓
Tenant
   ↓
Authorization
   ↓
Query Validation
   ↓
Selector
   ↓
Filter
   ↓
Search
   ↓
Ordering
   ↓
Pagination
   ↓
Serialization
   ↓
Response
```

Tenant e autorização deverão ser aplicados antes da exposição dos
resultados.

------------------------------------------------------------------------

# 4. Princípios

Consultas deverão observar:

-   allowlist;
-   tenant-first;
-   autorização;
-   limites;
-   ordenação determinística;
-   paginação;
-   performance;
-   contratos explícitos.

Parâmetros do cliente não deverão ser convertidos diretamente em
operações arbitrárias de ORM.

------------------------------------------------------------------------

# 5. Fluxo Oficial de Consulta

Exemplo conceitual:

``` text
GET /api/v1/membros/?ativo=true&search=ana&page=2
                         │
                         ▼
                    Validar Query
                         │
                         ▼
                    Tenant Scope
                         │
                         ▼
                     Permission
                         │
                         ▼
                      Selector
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
          Filter       Search      Ordering
            └────────────┼────────────┘
                         ▼
                     Pagination
                         ▼
                    Serialization
                         ▼
                       200
```

------------------------------------------------------------------------

# 6. Coleções

Toda coleção potencialmente crescente deverá possuir estratégia de
limitação.

Não retornar todos os registros por padrão apenas porque o volume atual
é pequeno.

------------------------------------------------------------------------

# 7. Query Parameters

Parâmetros deverão ser:

-   documentados;
-   tipados;
-   validados;
-   limitados;
-   previsíveis.

Exemplo:

``` text
/api/v1/membros/?ativo=true&search=ana&ordering=nome&page=1&page_size=25
```

------------------------------------------------------------------------

# 8. Filtros

Filtros deverão representar critérios conhecidos pelo endpoint.

Exemplos conceituais:

``` text
ativo=true
status=confirmado
departamento_id=5
data_inicio=2026-08-01
```

------------------------------------------------------------------------

# 9. Allowlist de Filtros

Somente campos explicitamente permitidos deverão ser filtráveis.

Evitar mecanismos que aceitem qualquer nome de campo do model.

``` text
Parâmetro recebido
      ↓
Está na allowlist?
      ↓
Validar
      ↓
Aplicar
```

------------------------------------------------------------------------

# 10. Tipos de Filtros

Filtros poderão incluir:

-   igualdade;
-   booleano;
-   enum;
-   intervalo;
-   data;
-   relacionamento;
-   identificador;
-   estado.

Operadores deverão ser explicitamente definidos.

------------------------------------------------------------------------

# 11. Filtros Booleanos

Valores booleanos deverão possuir representação consistente.

Exemplo:

``` text
?ativo=true
```

Não interpretar strings arbitrárias como booleanos.

------------------------------------------------------------------------

# 12. Filtros por Enumeração

Somente valores conhecidos deverão ser aceitos.

Exemplo:

``` text
?status=ativo
```

Valor desconhecido deverá produzir comportamento padronizado,
preferencialmente erro de validação.

------------------------------------------------------------------------

# 13. Filtros por Data

Datas deverão utilizar formato consistente.

Exemplo:

``` text
?data=2026-08-27
```

Quando o campo persistido possuir horário, a semântica do filtro por
data deverá ser documentada.

------------------------------------------------------------------------

# 14. Filtros por Intervalo

Intervalos poderão utilizar parâmetros explícitos:

``` text
?data_inicio=2026-08-01&data_fim=2026-08-31
```

Validar:

``` text
data_inicio <= data_fim
```

Limites máximos poderão ser necessários para consultas caras.

------------------------------------------------------------------------

# 15. Filtros por Relacionamento

Relacionamentos deverão respeitar tenant e autorização.

Exemplo:

``` text
?departamento_id=5
```

O ID `5` não deverá permitir inferência ou acesso a dados de outro
tenant.

------------------------------------------------------------------------

# 16. Filtros por Identificador

IDs deverão possuir tipo e formato validados.

Quando o identificador representar recurso organizacional, seu escopo
deverá ser considerado.

------------------------------------------------------------------------

# 17. Filtros Multi-Tenant

O filtro de tenant não deverá ser uma opção comum do consumidor em
endpoints organizacionais.

Preferir:

``` text
tenant
→ contexto da requisição
```

e não:

``` text
?tenant_id=qualquer_valor
```

A consulta base deverá nascer isolada.

------------------------------------------------------------------------

# 18. Combinação de Filtros

A combinação deverá possuir semântica previsível.

Por padrão, múltiplos filtros poderão representar interseção:

``` text
ativo=true
+
departamento_id=5
```

resultando em:

``` text
ativos
E
do departamento 5
```

Comportamentos OR deverão ser explicitamente documentados.

------------------------------------------------------------------------

# 19. Busca Textual

Busca textual deverá ser diferenciada de filtros exatos.

Exemplo:

``` text
?search=ana
```

O endpoint deverá documentar em quais campos a busca ocorre.

------------------------------------------------------------------------

# 20. Campos Pesquisáveis

Somente campos previamente definidos deverão participar da busca.

Exemplo conceitual para membros:

``` text
nome
email
```

Dados sensíveis não deverão ser automaticamente pesquisáveis.

------------------------------------------------------------------------

# 21. Normalização da Busca

Quando apropriado, a busca poderá considerar:

-   trim;
-   caixa;
-   acentuação;
-   espaços.

A normalização deverá ser coerente com o domínio e banco utilizados.

------------------------------------------------------------------------

# 22. Busca e Dados Sensíveis

Busca não deverá facilitar enumeração de informações confidenciais.

Avaliar especialmente:

-   documentos pessoais;
-   dados financeiros;
-   contatos;
-   credenciais;
-   informações ministeriais classificadas.

------------------------------------------------------------------------

# 23. Ordenação

Ordenação deverá utilizar parâmetro padronizado.

Exemplo:

``` text
?ordering=nome
```

Direção descendente poderá utilizar convenção:

``` text
?ordering=-nome
```

desde que oficialmente adotada.

------------------------------------------------------------------------

# 24. Campos Ordenáveis

Somente campos permitidos poderão ser usados.

Nunca executar diretamente:

``` python
queryset.order_by(request.GET["ordering"])
```

sem validação contra allowlist.

------------------------------------------------------------------------

# 25. Direção da Ordenação

A direção deverá ser validada.

Exemplo conceitual:

``` text
nome
-nome
data
-data
```

Outros operadores arbitrários não deverão ser aceitos.

------------------------------------------------------------------------

# 26. Ordenação Padrão

Toda coleção paginada deverá possuir ordenação padrão definida.

Exemplo:

``` text
nome ASC
```

ou:

``` text
created_at DESC
```

conforme o domínio.

------------------------------------------------------------------------

# 27. Ordenação Determinística

Paginação exige ordenação estável.

Quando o campo principal puder repetir, adicionar critério de desempate.

Exemplo:

``` text
ORDER BY nome, id
```

Isso reduz duplicidade ou ausência de itens entre páginas.

------------------------------------------------------------------------

# 28. Paginação

Paginação deverá ser padrão para coleções potencialmente grandes.

A ausência de parâmetros deverá utilizar valores seguros.

------------------------------------------------------------------------

# 29. Tamanho de Página

Deverá existir `page_size` padrão.

Exemplo conceitual:

``` text
25
```

O valor concreto poderá variar conforme o tipo de recurso.

------------------------------------------------------------------------

# 30. Limites Máximos

O cliente não deverá poder solicitar quantidade ilimitada.

Exemplo conceitual:

``` text
default_page_size = 25
max_page_size = 100
```

Os números definitivos deverão ser definidos conforme características
reais dos endpoints.

------------------------------------------------------------------------

# 31. Formato da Resposta Paginada

Formato recomendado:

``` json
{
  "results": [],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total": 0,
    "pages": 0
  }
}
```

A família GAPI deverá utilizar estrutura consistente.

------------------------------------------------------------------------

# 32. Page-Based Pagination

Paginação por página é adequada para diversas telas administrativas.

Exemplo:

``` text
?page=2&page_size=25
```

É simples para interfaces com navegação por páginas.

------------------------------------------------------------------------

# 33. Cursor-Based Pagination

Cursor poderá ser adotado para:

-   grandes volumes;
-   feeds;
-   dados com alta taxa de mudança;
-   integrações.

Não deverá ser introduzido sem necessidade real.

Quando adotado, o cursor deverá ser opaco para o consumidor.

------------------------------------------------------------------------

# 34. Contagem Total

`COUNT(*)` pode ser caro em determinadas consultas.

O endpoint deverá avaliar se `total` é realmente necessário.

Para interfaces administrativas comuns, poderá ser útil.

Para coleções massivas, outras estratégias poderão ser necessárias.

------------------------------------------------------------------------

# 35. Tenant e Paginação

A paginação deverá ocorrer depois do escopo de tenant.

Correto:

``` text
Tenant
  ↓
Query
  ↓
Pagination
```

Incorreto:

``` text
Query global
  ↓
Pagination
  ↓
remover outros tenants
```

------------------------------------------------------------------------

# 36. Autorização e Coleções

Permissões poderão afetar quais registros são visíveis.

A autorização deverá participar da consulta quando houver restrição por
objeto ou escopo.

Não carregar registros proibidos para filtrá-los posteriormente no
frontend.

------------------------------------------------------------------------

# 37. Selectors

Selectors deverão concentrar consultas reutilizáveis e complexas.

Exemplo conceitual:

``` python
def listar_membros(
    *,
    tenant,
    filtros,
    search=None,
    ordering=None,
):
    ...
```

O selector deverá partir do escopo seguro.

------------------------------------------------------------------------

# 38. ORM e Segurança

Parâmetros externos não deverão controlar diretamente:

-   nomes de campos;
-   lookups;
-   joins;
-   annotations;
-   raw SQL.

Mapear valores públicos para operações internas conhecidas.

Exemplo:

``` python
ORDERING_MAP = {
    "nome": "nome",
    "-nome": "-nome",
}
```

------------------------------------------------------------------------

# 39. Performance

Endpoints de coleção deverão avaliar:

-   número de queries;
-   tempo de consulta;
-   volume;
-   índices;
-   joins;
-   serialização;
-   contagem;
-   tamanho da página.

------------------------------------------------------------------------

# 40. Índices

Filtros e ordenações frequentes poderão exigir índices.

Priorizar análise sobre campos como:

-   tenant;
-   status;
-   datas;
-   chaves estrangeiras;
-   campos frequentemente ordenados.

Índices deverão refletir padrões reais de consulta.

------------------------------------------------------------------------

# 41. N+1 Queries

Serialização de relacionamentos deverá evitar N+1.

Utilizar mecanismos apropriados do Django, quando aplicável, como:

``` text
select_related
prefetch_related
```

de forma consciente.

------------------------------------------------------------------------

# 42. Cache

Cache de coleções deverá incorporar contexto relevante.

Exemplo conceitual:

``` text
tenant
+
permissão/usuário quando necessário
+
filtros
+
busca
+
ordenação
+
página
```

Não compartilhar cache organizacional sem isolamento.

------------------------------------------------------------------------

# 43. Relatórios e Dashboards

Relatórios e dashboards podem exigir consultas agregadas.

Não forçar a mesma estratégia de paginação de CRUD quando ela não fizer
sentido.

Ainda assim deverão preservar:

-   tenant;
-   autorização;
-   limites;
-   performance;
-   contratos.

------------------------------------------------------------------------

# 44. Exportações

Exportação não deverá ser usada como forma de contornar paginação.

Quando o usuário realmente precisar do conjunto completo, utilizar fluxo
específico de exportação com:

-   permissão;
-   auditoria;
-   limites;
-   processamento assíncrono quando necessário.

------------------------------------------------------------------------

# 45. APIs Externas

APIs consumidas por integrações deverão documentar claramente:

-   filtros suportados;
-   ordenação;
-   paginação;
-   limites;
-   estabilidade.

Mudanças nesses contratos deverão seguir versionamento.

------------------------------------------------------------------------

# 46. Compatibilidade

Não alterar silenciosamente:

-   nome de parâmetros;
-   semântica de filtros;
-   ordenação padrão;
-   tamanho máximo;
-   formato de paginação.

Mudanças relevantes deverão seguir GAPI-07.

------------------------------------------------------------------------

# 47. Erros

Parâmetros inválidos deverão produzir erro previsível.

Exemplo:

``` json
{
  "error": {
    "code": "validation_error",
    "message": "Existem parâmetros inválidos.",
    "fields": {
      "ordering": [
        "Campo de ordenação não permitido."
      ]
    }
  }
}
```

Não ignorar silenciosamente parâmetros críticos inválidos se isso puder
induzir o consumidor a erro.

------------------------------------------------------------------------

# 48. Logging e Monitoramento

Monitorar endpoints de coleção quanto a:

-   latência;
-   quantidade de queries;
-   page_size;
-   erros;
-   filtros caros;
-   timeouts;
-   volume.

Não registrar termos de busca sensíveis indiscriminadamente.

------------------------------------------------------------------------

# 49. Testes

Testes deverão cobrir:

-   listagem padrão;
-   tenant;
-   sem permissão;
-   filtro válido;
-   filtro inválido;
-   busca;
-   ordenação ascendente;
-   ordenação descendente;
-   campo de ordenação proibido;
-   primeira página;
-   página intermediária;
-   página vazia;
-   page_size padrão;
-   page_size máximo;
-   page_size acima do limite;
-   estabilidade da ordenação;
-   relacionamento de outro tenant;
-   ausência de N+1 em endpoints críticos quando apropriado.

------------------------------------------------------------------------

# 50. Anti-Padrões

Evitar:

``` python
Model.objects.all()
```

como base de endpoint multi-tenant sem escopo.

------------------------------------------------------------------------

``` python
queryset.filter(**request.GET.dict())
```

------------------------------------------------------------------------

``` python
queryset.order_by(request.GET["ordering"])
```

------------------------------------------------------------------------

``` text
?page_size=999999
```

sem limite.

------------------------------------------------------------------------

``` text
tenant_id
como filtro público
para escolher qualquer organização
```

------------------------------------------------------------------------

``` text
paginar primeiro
e aplicar tenant depois
```

------------------------------------------------------------------------

``` text
frontend filtra
o que o backend retornou
```

para segurança.

------------------------------------------------------------------------

``` text
exportar tudo
porque paginação incomoda
```

------------------------------------------------------------------------

# 51. Exemplos

## Listagem simples

``` text
GET /api/v1/membros/
```

## Filtro

``` text
GET /api/v1/membros/?ativo=true
```

## Busca

``` text
GET /api/v1/membros/?search=ana
```

## Ordenação

``` text
GET /api/v1/membros/?ordering=nome
```

## Ordenação descendente

``` text
GET /api/v1/eventos/?ordering=-data_inicio
```

## Paginação

``` text
GET /api/v1/membros/?page=2&page_size=25
```

## Combinação

``` text
GET /api/v1/membros/?ativo=true&search=ana&ordering=nome&page=1&page_size=25
```

Resposta conceitual:

``` json
{
  "results": [
    {
      "id": 42,
      "nome": "Ana Exemplo",
      "ativo": true
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total": 1,
    "pages": 1
  }
}
```

------------------------------------------------------------------------

# 52. Checklist

## Segurança

-   [ ] query inicia no tenant correto;
-   [ ] autorização aplicada;
-   [ ] filtros usam allowlist;
-   [ ] ordenação usa allowlist;
-   [ ] relacionamentos respeitam tenant;
-   [ ] busca não expõe dados sensíveis.

## Filtros

-   [ ] tipos definidos;
-   [ ] enums validados;
-   [ ] datas validadas;
-   [ ] intervalos validados;
-   [ ] combinação documentada.

## Busca

-   [ ] parâmetro padronizado;
-   [ ] campos definidos;
-   [ ] normalização definida;
-   [ ] limites avaliados.

## Ordenação

-   [ ] parâmetro padronizado;
-   [ ] campos permitidos;
-   [ ] direção validada;
-   [ ] default definido;
-   [ ] desempate determinístico.

## Paginação

-   [ ] habilitada quando necessária;
-   [ ] page_size padrão;
-   [ ] page_size máximo;
-   [ ] resposta consistente;
-   [ ] total avaliado;
-   [ ] ordenação estável.

## Performance

-   [ ] índices avaliados;
-   [ ] N+1 avaliado;
-   [ ] tamanho do payload;
-   [ ] contagem avaliada;
-   [ ] consultas caras monitoradas.

## Testes

-   [ ] filtro válido;
-   [ ] filtro inválido;
-   [ ] busca;
-   [ ] ordenação;
-   [ ] paginação;
-   [ ] limite máximo;
-   [ ] tenant incorreto;
-   [ ] permissão;
-   [ ] estabilidade.

------------------------------------------------------------------------

# 53. Documentos Relacionados

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

-   selectors;
-   managers;
-   models;
-   performance;
-   testing;
-   permissions;
-   views.

## Segurança

-   GSF-05 --- Segurança Multi-Tenant
-   GSF-07 --- Segurança das APIs
-   GSF-08 --- Segurança de Dados e Privacidade
-   GSF-10 --- Logging, Monitoramento e Auditoria

------------------------------------------------------------------------

# 54. Princípios Finais

Uma coleção deverá nascer segura e limitada.

``` text
Tenant
   ↓
Autorização
   ↓
Query Base
   ↓
Filtros Permitidos
   ↓
Busca Permitida
   ↓
Ordenação Permitida
   ↓
Paginação
   ↓
Resposta
```

Nunca:

``` text
Consultar tudo
   ↓
retornar tudo
   ↓
deixar o cliente decidir
```

O princípio central é:

``` text
O cliente pode escolher
entre opções de consulta
que a API oferece.

O cliente não controla
a consulta interna.
```

Filtros, busca, ordenação e paginação são parte do contrato, da
segurança e da capacidade de crescimento do GereIgreja.

------------------------------------------------------------------------

# 55. Status do Documento

**Pasta**

`docs/api/`

**Arquivo**

`06-Filtros-Busca-Ordenacao-e-Paginacao.md`

**Documento**

`GAPI-06`

**Código**

`GAPI-QUERY-COLLECTIONS`

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

`GAPI-05 — Responses, Serialização e Erros`

**Próximo documento recomendado**

`07-Versionamento-e-Compatibilidade.md`
