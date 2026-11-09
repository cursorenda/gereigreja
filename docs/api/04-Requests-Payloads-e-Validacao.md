Pasta:

docs/api/

Arquivo:

04-Requests-Payloads-e-Validacao.md

Documento:

GAPI-04

Código:

GAPI-REQUEST-PAYLOAD-VALIDATION

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

# GAPI-04 --- Requests, Payloads e Validação

> "Toda entrada de uma API é não confiável até que seu formato, contexto
> e significado tenham sido validados."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com a Arquitetura das APIs
4.  Princípios
5.  Anatomia da Entrada
6.  Fronteira de Confiança
7.  Fontes de Entrada
8.  Path Parameters
9.  Query Parameters
10. Headers
11. Cookies e Sessão
12. Request Body
13. JSON
14. Form Data
15. Multipart e Uploads
16. Contrato de Entrada
17. Campos Obrigatórios
18. Campos Opcionais
19. Campos Desconhecidos
20. Tipos de Dados
21. Strings
22. Números
23. Booleanos
24. Datas e Horários
25. Enumerações
26. Identificadores
27. Valores Nulos
28. Coleções
29. Objetos Aninhados
30. Normalização
31. Validação Sintática
32. Validação Semântica
33. Validação de Domínio
34. Validação de Tenant
35. Validação de Autorização
36. Validação de Relacionamentos
37. Validação de Unicidade
38. Validação Financeira
39. Dados Pessoais
40. Mass Assignment
41. Campos Somente Leitura
42. Campos Derivados
43. Valores Gerados pelo Servidor
44. Sanitização
45. HTML e Conteúdo Rico
46. SQL e ORM
47. Limites de Payload
48. Uploads
49. Webhooks
50. Integrações Externas
51. Validação em Services
52. Validators
53. Forms e Serializers
54. Transações
55. Mensagens de Erro
56. Logging
57. Privacidade
58. Performance
59. Testes
60. Anti-Padrões
61. Exemplo de Criação
62. Exemplo de Atualização
63. Checklist
64. Documentos Relacionados
65. Princípios Finais
66. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece os padrões oficiais para requests, payloads e
validação nas APIs do GereIgreja.

Seu objetivo é garantir que dados recebidos pela plataforma sejam
tratados de maneira:

-   explícita;
-   previsível;
-   segura;
-   consistente;
-   tenant-aware;
-   compatível com as regras de negócio.

A validação deverá proteger tanto o contrato HTTP quanto o domínio da
aplicação.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a entradas recebidas através de:

-   APIs REST;
-   endpoints internos;
-   endpoints administrativos;
-   webhooks;
-   integrações;
-   uploads;
-   callbacks;
-   automações;
-   requests originados pelo frontend.

------------------------------------------------------------------------

# 3. Relação com a Arquitetura das APIs

O fluxo conceitual é:

``` text
Request
   ↓
Extração
   ↓
Validação de Formato
   ↓
Validação de Contexto
   ↓
Validação de Domínio
   ↓
Service
```

O endpoint deverá impedir que dados inválidos alcancem regras de negócio
em estado inconsistente.

------------------------------------------------------------------------

# 4. Princípios

Toda entrada deverá seguir:

-   deny by default para campos não previstos;
-   tipos explícitos;
-   limites definidos;
-   normalização consciente;
-   validação próxima da responsabilidade correta;
-   nenhuma confiança em IDs fornecidos pelo cliente;
-   nenhuma confiança em tenant fornecido arbitrariamente;
-   nenhuma atribuição automática de campos sensíveis.

------------------------------------------------------------------------

# 5. Anatomia da Entrada

Uma requisição poderá fornecer dados através de:

``` text
URL
├── Path
└── Query

Headers

Cookies / Session

Body
├── JSON
├── Form
└── Multipart
```

Todas as fontes deverão ser consideradas entradas externas.

------------------------------------------------------------------------

# 6. Fronteira de Confiança

O princípio oficial é:

``` text
Cliente
   ↓
Dados não confiáveis
   ↓
Validação
   ↓
Dados aceitos
```

O fato de a requisição vir do frontend oficial do GereIgreja não elimina
a necessidade de validação no backend.

------------------------------------------------------------------------

# 7. Fontes de Entrada

Cada valor deverá possuir origem conhecida.

Exemplos:

``` text
membro_id
→ path

page
→ query

Authorization
→ header

nome
→ body

tenant
→ contexto autenticado
```

Evitar múltiplas fontes concorrentes para a mesma informação crítica.

------------------------------------------------------------------------

# 8. Path Parameters

Parâmetros de rota deverão ser validados.

Exemplo:

``` text
/api/v1/membros/{membro_id}/
```

O identificador deverá ser validado antes da consulta.

O ID não comprova pertencimento ao tenant.

------------------------------------------------------------------------

# 9. Query Parameters

Query parameters deverão ser utilizados para opções de consulta.

Exemplo:

``` text
?ativo=true&page=2&ordenacao=nome
```

Deverão possuir:

-   tipos;
-   valores permitidos;
-   limites;
-   defaults;
-   documentação.

------------------------------------------------------------------------

# 10. Headers

Headers relevantes deverão ser validados conforme seu propósito.

Não confiar em headers customizados enviados pelo cliente para
estabelecer:

-   usuário;
-   tenant;
-   permissão;

sem mecanismo criptográfico ou arquitetural que os torne confiáveis.

------------------------------------------------------------------------

# 11. Cookies e Sessão

Quando a autenticação utilizar sessão, cookies deverão seguir os
controles de segurança aplicáveis.

Dados de sessão não deverão ser reproduzidos pelo cliente como
autoridade de negócio.

------------------------------------------------------------------------

# 12. Request Body

O body deverá representar apenas os dados necessários à operação.

Exemplo de criação:

``` json
{
  "nome": "Pessoa Exemplo",
  "email": "pessoa@example.test"
}
```

Evitar receber estruturas que reflitam integralmente o model interno.

------------------------------------------------------------------------

# 13. JSON

JSON será o formato padrão para payloads estruturados quando aplicável.

O endpoint deverá validar:

-   JSON bem formado;
-   estrutura esperada;
-   tipos;
-   campos;
-   profundidade;
-   tamanho.

------------------------------------------------------------------------

# 14. Form Data

Form data poderá ser utilizado quando necessário.

A mesma política de validação do backend deverá ser aplicada.

------------------------------------------------------------------------

# 15. Multipart e Uploads

`multipart/form-data` poderá ser utilizado para arquivos.

Campos textuais e arquivos deverão ser validados separadamente.

------------------------------------------------------------------------

# 16. Contrato de Entrada

Toda operação deverá possuir contrato explícito.

Exemplo conceitual:

``` text
Criar Membro

nome
- string
- obrigatório

email
- string
- opcional
- formato de e-mail

data_nascimento
- date
- opcional
```

O contrato não deverá ser inferido automaticamente de todos os campos
persistidos.

------------------------------------------------------------------------

# 17. Campos Obrigatórios

Campos obrigatórios deverão ser definidos pela operação.

Um campo obrigatório no banco pode não ser recebido do cliente se for
gerado pelo servidor.

------------------------------------------------------------------------

# 18. Campos Opcionais

Campos opcionais deverão possuir comportamento conhecido quando
ausentes.

Distinguir:

``` text
campo ausente
```

de:

``` text
campo presente com null
```

quando isso alterar a semântica.

------------------------------------------------------------------------

# 19. Campos Desconhecidos

A API deverá preferencialmente rejeitar ou ignorar de forma
explicitamente padronizada campos não previstos.

Para operações sensíveis, rejeitar campos desconhecidos reduz erros e
mass assignment.

------------------------------------------------------------------------

# 20. Tipos de Dados

Não depender de conversões implícitas excessivas.

Exemplo:

``` text
"10"
```

não deverá ser automaticamente aceito como inteiro em todos os contratos
apenas porque é convertível.

A política deverá ser previsível.

------------------------------------------------------------------------

# 21. Strings

Strings deverão avaliar:

-   tamanho mínimo;
-   tamanho máximo;
-   trim;
-   caracteres permitidos quando necessário;
-   vazio;
-   normalização.

Não remover conteúdo significativo indiscriminadamente.

------------------------------------------------------------------------

# 22. Números

Números deverão possuir:

-   tipo;
-   faixa;
-   precisão;
-   sinal permitido;
-   unidade.

Valores financeiros deverão evitar tipos binários inadequados para
moeda.

------------------------------------------------------------------------

# 23. Booleanos

Booleanos deverão possuir representação previsível.

Evitar interpretar qualquer string não vazia como verdadeiro.

------------------------------------------------------------------------

# 24. Datas e Horários

Datas e horários deverão possuir formato definido.

Preferir formatos interoperáveis e inequívocos.

Quando houver horário, considerar:

-   timezone;
-   armazenamento;
-   exibição;
-   conversão.

------------------------------------------------------------------------

# 25. Enumerações

Campos com conjunto fechado deverão aceitar apenas valores conhecidos.

Exemplo conceitual:

``` text
status ∈ {
  ativo,
  inativo
}
```

Não aceitar qualquer string e validar somente posteriormente.

------------------------------------------------------------------------

# 26. Identificadores

IDs deverão ser validados em três dimensões:

``` text
Formato
   ↓
Existência
   ↓
Escopo
```

Para recursos multi-tenant:

``` text
Escopo
=
tenant correto
+
autorização aplicável
```

------------------------------------------------------------------------

# 27. Valores Nulos

`null` deverá possuir semântica explícita.

Não confundir:

-   ausência;
-   vazio;
-   nulo;
-   zero;
-   falso.

------------------------------------------------------------------------

# 28. Coleções

Arrays/listas deverão possuir:

-   tipo dos itens;
-   quantidade máxima;
-   duplicidade permitida ou não;
-   validação individual;
-   validação do conjunto.

------------------------------------------------------------------------

# 29. Objetos Aninhados

Objetos aninhados deverão ser utilizados com cautela.

Atualizações complexas de múltiplas entidades deverão avaliar services
específicos e transações.

------------------------------------------------------------------------

# 30. Normalização

Normalização poderá incluir:

-   trim;
-   padronização de caixa quando semanticamente válida;
-   formatos;
-   remoção de caracteres de apresentação.

Normalização não deverá alterar silenciosamente significado de dados.

------------------------------------------------------------------------

# 31. Validação Sintática

Validação sintática responde:

``` text
O valor possui
o formato esperado?
```

Exemplos:

-   data válida;
-   e-mail bem formado;
-   UUID válido;
-   número no formato correto.

------------------------------------------------------------------------

# 32. Validação Semântica

Validação semântica responde:

``` text
O valor faz sentido
para esta operação?
```

Exemplo:

``` text
data_fim >= data_inicio
```

------------------------------------------------------------------------

# 33. Validação de Domínio

Regras de domínio deverão ser executadas na camada adequada.

Exemplos:

-   membro pode ser incluído no departamento;
-   lançamento pode ser alterado;
-   evento pode ser cancelado;
-   turma da EBD aceita determinada operação.

Regras reutilizáveis não deverão ficar duplicadas em múltiplos
endpoints.

------------------------------------------------------------------------

# 34. Validação de Tenant

Relacionamentos recebidos por ID deverão pertencer ao tenant correto.

Exemplo:

``` text
departamento_id
   ↓
buscar dentro do tenant
   ↓
usar objeto validado
```

Nunca aceitar associação cross-tenant por ID.

------------------------------------------------------------------------

# 35. Validação de Autorização

Validação de formato não substitui autorização.

``` text
ID válido
+
objeto existente
≠
usuário autorizado
```

Permissões deverão ser verificadas separadamente.

------------------------------------------------------------------------

# 36. Validação de Relacionamentos

Relacionamentos deverão ser validados antes da persistência.

Avaliar:

-   existência;
-   tenant;
-   estado;
-   autorização;
-   compatibilidade de domínio.

------------------------------------------------------------------------

# 37. Validação de Unicidade

Unicidade deverá ser garantida também pela camada de persistência quando
for uma invariável real.

Não depender exclusivamente de:

``` text
SELECT
↓
não existe
↓
INSERT
```

pois requisições concorrentes podem ocorrer.

------------------------------------------------------------------------

# 38. Validação Financeira

Dados financeiros deverão possuir controles adicionais.

Avaliar:

-   precisão decimal;
-   sinal;
-   moeda;
-   competência;
-   conta;
-   categoria;
-   autorização;
-   duplicidade;
-   idempotência;
-   auditoria.

------------------------------------------------------------------------

# 39. Dados Pessoais

Solicitar apenas dados necessários.

Antes de adicionar um campo ao payload:

``` text
Precisamos receber
este dado?
```

Aplicar GSF-08 e GSF-14.

------------------------------------------------------------------------

# 40. Mass Assignment

É proibido utilizar payloads arbitrários diretamente na criação ou
atualização de models sensíveis.

Evitar:

``` python
Model.objects.create(**request.data)
```

quando `request.data` não foi explicitamente filtrado e validado.

------------------------------------------------------------------------

# 41. Campos Somente Leitura

Campos internos deverão ser definidos pelo servidor.

Exemplos conceituais:

-   ID;
-   tenant;
-   created_at;
-   updated_at;
-   created_by;
-   flags administrativas;
-   totais calculados.

------------------------------------------------------------------------

# 42. Campos Derivados

Campos derivados deverão preferencialmente ser calculados no servidor.

O cliente não deverá ser autoridade para valores que podem ser obtidos
da regra de negócio.

------------------------------------------------------------------------

# 43. Valores Gerados pelo Servidor

Exemplos:

``` text
tenant
actor
timestamps
identificadores
status inicial
número sequencial
```

Esses valores não deverão ser aceitos do cliente sem necessidade
explícita.

------------------------------------------------------------------------

# 44. Sanitização

Sanitização e validação não são sinônimos.

``` text
Validação
→ decide se o valor é aceitável

Sanitização
→ transforma conteúdo para uso seguro
```

A estratégia dependerá do tipo de dado.

------------------------------------------------------------------------

# 45. HTML e Conteúdo Rico

Se algum módulo aceitar HTML ou conteúdo rico, deverá existir política
específica.

Nunca considerar HTML recebido como seguro.

Avaliar:

-   sanitização;
-   elementos permitidos;
-   atributos permitidos;
-   URLs;
-   XSS.

------------------------------------------------------------------------

# 46. SQL e ORM

Entradas não deverão ser concatenadas em SQL.

Preferir ORM e mecanismos parametrizados.

Também evitar transformar parâmetros arbitrários diretamente em nomes de
campos, ordenações ou expressões.

------------------------------------------------------------------------

# 47. Limites de Payload

Endpoints deverão possuir limites proporcionais.

Avaliar:

-   tamanho total;
-   quantidade de itens;
-   profundidade;
-   tamanho de strings;
-   número de relacionamentos.

Limites ajudam segurança e disponibilidade.

------------------------------------------------------------------------

# 48. Uploads

Uploads deverão validar:

-   tamanho;
-   extensão;
-   tipo;
-   nome;
-   quantidade;
-   autorização;
-   tenant;
-   destino.

O nome enviado pelo cliente não deverá ser utilizado cegamente como
caminho de armazenamento.

------------------------------------------------------------------------

# 49. Webhooks

Payloads de webhooks deverão ser considerados não confiáveis mesmo
quando o fornecedor é conhecido.

Fluxo:

``` text
Request
   ↓
Validação de Origem
   ↓
Parse
   ↓
Validação de Estrutura
   ↓
Idempotência
   ↓
Regra de Negócio
```

------------------------------------------------------------------------

# 50. Integrações Externas

Respostas recebidas de APIs externas também são entradas.

Devem ser validadas antes de afetar o domínio interno.

Não assumir que o fornecedor sempre respeitará o contrato.

------------------------------------------------------------------------

# 51. Validação em Services

Regras de negócio importantes deverão permanecer protegidas mesmo quando
o service for chamado fora de uma API.

Por isso, validações estruturais podem existir na borda, mas invariantes
de domínio deverão ser preservadas na camada de negócio apropriada.

------------------------------------------------------------------------

# 52. Validators

Validators reutilizáveis deverão ser utilizados para regras
independentes e recorrentes.

Evitar validators que façam múltiplas operações de negócio escondidas.

------------------------------------------------------------------------

# 53. Forms e Serializers

Forms, serializers ou estruturas equivalentes poderão realizar validação
de contrato.

Eles não deverão se tornar automaticamente a única camada de proteção de
invariantes complexas.

------------------------------------------------------------------------

# 54. Transações

Quando uma operação validada alterar múltiplos registros relacionados,
avaliar transação.

A validação anterior não elimina riscos de concorrência entre validação
e persistência.

------------------------------------------------------------------------

# 55. Mensagens de Erro

Mensagens deverão ajudar o consumidor a corrigir a requisição.

Exemplo conceitual:

``` json
{
  "error": {
    "code": "validation_error",
    "message": "Existem campos inválidos.",
    "fields": {
      "email": [
        "Informe um endereço de e-mail válido."
      ]
    }
  }
}
```

Não expor:

-   stack traces;
-   SQL;
-   caminhos internos;
-   secrets;
-   detalhes de infraestrutura.

------------------------------------------------------------------------

# 56. Logging

Falhas de validação poderão ser registradas de forma agregada quando
úteis.

Evitar registrar payload completo contendo:

-   dados pessoais;
-   dados financeiros;
-   tokens;
-   secrets.

------------------------------------------------------------------------

# 57. Privacidade

A validação deverá apoiar minimização de dados.

Campos que não fazem parte do contrato não deverão ser armazenados "para
uso futuro" sem finalidade definida.

------------------------------------------------------------------------

# 58. Performance

Validação deverá ser eficiente.

Evitar:

-   uma query por item quando puder ser agregada;
-   consultas repetidas;
-   validações externas síncronas desnecessárias;
-   payloads ilimitados.

Performance não justifica remover validações de segurança.

------------------------------------------------------------------------

# 59. Testes

Testes deverão cobrir:

-   payload válido;
-   campo obrigatório ausente;
-   campo desconhecido;
-   tipo inválido;
-   valor fora do limite;
-   relacionamento inexistente;
-   relacionamento de outro tenant;
-   valor não autorizado;
-   null;
-   lista vazia;
-   lista excessiva;
-   upload inválido;
-   regra de domínio;
-   concorrência quando relevante.

------------------------------------------------------------------------

# 60. Anti-Padrões

Evitar:

``` python
Model.objects.create(**request.data)
```

------------------------------------------------------------------------

``` text
tenant_id recebido
=
tenant autorizado
```

------------------------------------------------------------------------

``` text
ID existe
=
relacionamento válido
```

------------------------------------------------------------------------

``` text
frontend validou
=
backend não precisa validar
```

------------------------------------------------------------------------

``` text
campo existe no model
=
campo pode ser enviado
```

------------------------------------------------------------------------

``` text
string convertível
=
tipo válido
```

------------------------------------------------------------------------

``` text
fornecedor enviou
=
payload confiável
```

------------------------------------------------------------------------

``` text
sanitizar tudo
=
validar corretamente
```

------------------------------------------------------------------------

# 61. Exemplo de Criação

Payload:

``` json
{
  "nome": "Pessoa Exemplo",
  "email": "pessoa@example.test",
  "departamento_id": 12
}
```

Fluxo:

``` text
JSON válido?
    ↓
Campos permitidos?
    ↓
Tipos válidos?
    ↓
Tenant resolvido?
    ↓
Departamento 12
pertence ao tenant?
    ↓
Usuário pode associar?
    ↓
Regra de domínio válida?
    ↓
Service
    ↓
Persistência
```

O payload não deverá incluir:

``` text
tenant_id
created_by
is_superuser
created_at
```

quando esses valores forem responsabilidade do servidor.

------------------------------------------------------------------------

# 62. Exemplo de Atualização

Payload:

``` json
{
  "email": "novo@example.test"
}
```

Em PATCH:

``` text
Campo ausente
→ não alterar

Campo presente
→ validar e atualizar

Campo somente leitura
→ rejeitar ou ignorar conforme padrão oficial
```

A política deverá ser consistente entre endpoints.

------------------------------------------------------------------------

# 63. Checklist

## Contrato

-   [ ] campos definidos;
-   [ ] obrigatórios definidos;
-   [ ] opcionais definidos;
-   [ ] desconhecidos tratados;
-   [ ] tipos definidos;
-   [ ] limites definidos.

## Contexto

-   [ ] usuário autenticado;
-   [ ] tenant resolvido;
-   [ ] permissão validada;
-   [ ] IDs limitados ao tenant.

## Dados

-   [ ] strings validadas;
-   [ ] números validados;
-   [ ] datas validadas;
-   [ ] enums validados;
-   [ ] null tratado;
-   [ ] coleções limitadas.

## Segurança

-   [ ] sem mass assignment;
-   [ ] campos internos protegidos;
-   [ ] HTML tratado;
-   [ ] SQL parametrizado/ORM;
-   [ ] payload limitado;
-   [ ] uploads protegidos.

## Domínio

-   [ ] relacionamentos válidos;
-   [ ] invariantes preservadas;
-   [ ] unicidade garantida;
-   [ ] transação avaliada;
-   [ ] concorrência avaliada.

## Privacidade

-   [ ] minimização;
-   [ ] dados sensíveis identificados;
-   [ ] logs não expõem payload sensível.

## Testes

-   [ ] sucesso;
-   [ ] obrigatório ausente;
-   [ ] tipo inválido;
-   [ ] campo desconhecido;
-   [ ] tenant incorreto;
-   [ ] relacionamento inválido;
-   [ ] regra de domínio;
-   [ ] limites.

------------------------------------------------------------------------

# 64. Documentos Relacionados

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

-   validators;
-   forms;
-   services;
-   selectors;
-   models;
-   views;
-   exceptions;
-   testing;
-   code standards.

## Segurança

-   GSF-05 --- Segurança Multi-Tenant
-   GSF-06 --- Segurança da Aplicação
-   GSF-07 --- Segurança das APIs
-   GSF-08 --- Segurança de Dados e Privacidade
-   GSF-14 --- Conformidade e LGPD
-   GSF-15 --- Secure Development Lifecycle

## Autenticação

-   GAF --- GereIgreja Authentication Framework

------------------------------------------------------------------------

# 65. Princípios Finais

Toda entrada deverá possuir um contrato.

``` text
Receber
   ↓
Validar
   ↓
Contextualizar
   ↓
Autorizar
   ↓
Executar
```

O princípio central é:

``` text
Dados recebidos
não são dados válidos.

Dados parseados
não são dados autorizados.

IDs existentes
não são relacionamentos permitidos.
```

A validação correta no GereIgreja deverá combinar:

``` text
Formato
   +
Semântica
   +
Domínio
   +
Tenant
   +
Autorização
```

Somente depois disso a operação deverá afetar o estado da plataforma.

------------------------------------------------------------------------

# 66. Status do Documento

**Pasta**

`docs/api/`

**Arquivo**

`04-Requests-Payloads-e-Validacao.md`

**Documento**

`GAPI-04`

**Código**

`GAPI-REQUEST-PAYLOAD-VALIDATION`

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

`GAPI-03 — Autenticação, Autorização e Tenant`

**Próximo documento recomendado**

`05-Responses-Serializacao-e-Erros.md`
