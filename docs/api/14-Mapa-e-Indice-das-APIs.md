Pasta:

docs/api/

Arquivo:

14-Mapa-e-Indice-das-APIs.md

Documento:

GAPI-14

Código:

GAPI-API-MAP-INDEX

Família:

GAPI --- GereIgreja API Engineering

Frameworks relacionados:

GEA --- GereIgreja Enterprise Architecture GAF --- GereIgreja
Authentication Framework GSF --- GereIgreja Security Framework GQF ---
GereIgreja Quality Framework GOC --- GereIgreja Operations Center GDF
--- GereIgreja Documentation Framework

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GAPI-14 --- Mapa e Índice das APIs

> "Uma plataforma só consegue governar suas APIs quando sabe quais
> contratos existem, onde estão, quem os utiliza e quais padrões os
> controlam."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Papel do GAPI-14
4.  Família GAPI
5.  Mapa Geral da Família
6.  Camadas de Governança
7.  GAPI-01 --- Arquitetura das APIs
8.  GAPI-02 --- Padrões de Endpoints
9.  GAPI-03 --- Autenticação, Autorização e Tenant
10. GAPI-04 --- Requests, Payloads e Validação
11. GAPI-05 --- Responses, Serialização e Erros
12. GAPI-06 --- Filtros, Busca, Ordenação e Paginação
13. GAPI-07 --- Versionamento e Compatibilidade
14. GAPI-08 --- Webhooks e Integrações
15. GAPI-09 --- Idempotência e Rate Limiting
16. GAPI-10 --- Segurança e Privacidade
17. GAPI-11 --- Logging, Monitoramento e Auditoria
18. GAPI-12 --- Testes de APIs
19. GAPI-13 --- Depreciação e Ciclo de Vida
20. GAPI-14 --- Mapa e Índice das APIs
21. Fluxo de uma Requisição
22. Fluxo de uma Operação Crítica
23. Fluxo de Integração
24. Fluxo de Evolução
25. Classificação das APIs
26. APIs Internas
27. APIs Externas
28. APIs Administrativas
29. Webhooks
30. Integrações
31. Inventário de APIs
32. Campos Mínimos do Inventário
33. Identificação de Owner
34. Identificação de Tenant
35. Classificação de Dados
36. Criticidade
37. Autenticação e Autorização
38. Versionamento
39. Observabilidade
40. Dependências
41. Consumidores
42. Estado do Ciclo de Vida
43. Mapa de Dependências Documentais
44. Relação com GEA
45. Relação com GAF
46. Relação com GSF
47. Relação com GQF
48. Relação com GOC
49. Relação com GDF
50. Relação com Frontend Engineering
51. Relação com Design System
52. Processo para Criar uma Nova API
53. Processo para Alterar uma API
54. Processo para Publicar uma API
55. Processo para Depreciar uma API
56. Processo para Remover uma API
57. Checklist de Governança
58. Matriz de Referência
59. Anti-Padrões
60. Documentos Relacionados
61. Princípios Finais
62. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento consolida o mapa oficial da família **GAPI --- GereIgreja
API Engineering**.

Seu objetivo é permitir que a Engenharia identifique rapidamente:

-   qual documento consultar;
-   quais controles se aplicam;
-   como os documentos se relacionam;
-   como uma API entra no ecossistema;
-   como uma API evolui;
-   como uma API é monitorada;
-   como uma API é retirada.

O GAPI-14 não substitui os documentos especializados.

Ele funciona como:

``` text
Mapa
+
Índice
+
Ponto de entrada
+
Referência de governança
```

------------------------------------------------------------------------

# 2. Escopo

Este documento cobre a organização documental e o inventário conceitual
das APIs do GereIgreja.

Aplica-se a:

-   APIs REST;
-   endpoints internos;
-   endpoints administrativos;
-   APIs externas;
-   webhooks;
-   integrações;
-   callbacks;
-   operações assíncronas iniciadas por API;
-   contratos versionados.

------------------------------------------------------------------------

# 3. Papel do GAPI-14

A família GAPI possui documentos especializados.

O GAPI-14 conecta esses documentos.

``` text
GAPI-01
   │
   ├── GAPI-02
   ├── GAPI-03
   ├── GAPI-04
   ├── GAPI-05
   ├── GAPI-06
   ├── GAPI-07
   ├── GAPI-08
   ├── GAPI-09
   ├── GAPI-10
   ├── GAPI-11
   ├── GAPI-12
   └── GAPI-13
          │
          ▼
       GAPI-14
   Mapa e Índice
```

------------------------------------------------------------------------

# 4. Família GAPI

A família oficial é composta por:

1.  GAPI-01 --- Arquitetura das APIs
2.  GAPI-02 --- Padrões de Endpoints
3.  GAPI-03 --- Autenticação, Autorização e Tenant
4.  GAPI-04 --- Requests, Payloads e Validação
5.  GAPI-05 --- Responses, Serialização e Erros
6.  GAPI-06 --- Filtros, Busca, Ordenação e Paginação
7.  GAPI-07 --- Versionamento e Compatibilidade
8.  GAPI-08 --- Webhooks e Integrações
9.  GAPI-09 --- Idempotência e Rate Limiting
10. GAPI-10 --- Segurança e Privacidade
11. GAPI-11 --- Logging, Monitoramento e Auditoria
12. GAPI-12 --- Testes de APIs
13. GAPI-13 --- Depreciação e Ciclo de Vida
14. GAPI-14 --- Mapa e Índice das APIs

------------------------------------------------------------------------

# 5. Mapa Geral da Família

``` text
                         GAPI-01
                  Arquitetura das APIs
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
      GAPI-02           GAPI-03           GAPI-04
     Endpoints       Auth/Authz/Tenant     Requests
         │                 │                 │
         └────────────┬────┴────┬────────────┘
                      │         │
                      ▼         ▼
                   GAPI-05   GAPI-06
                   Responses  Consultas
                      │         │
                      └────┬────┘
                           ▼
                        GAPI-07
                       Evolução
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           GAPI-08      GAPI-09      GAPI-10
         Integrações   Resiliência    Segurança
              │            │            │
              └────────────┼────────────┘
                           ▼
                        GAPI-11
                    Observabilidade
                           │
                           ▼
                        GAPI-12
                         Testes
                           │
                           ▼
                        GAPI-13
                    Ciclo de Vida
                           │
                           ▼
                        GAPI-14
                    Mapa e Índice
```

------------------------------------------------------------------------

# 6. Camadas de Governança

A família pode ser compreendida em seis camadas.

``` text
1. Arquitetura
   GAPI-01

2. Contrato
   GAPI-02
   GAPI-04
   GAPI-05
   GAPI-06

3. Identidade e Segurança
   GAPI-03
   GAPI-09
   GAPI-10

4. Integração e Evolução
   GAPI-07
   GAPI-08

5. Operação e Qualidade
   GAPI-11
   GAPI-12

6. Governança do Ciclo de Vida
   GAPI-13
   GAPI-14
```

------------------------------------------------------------------------

# 7. GAPI-01 --- Arquitetura das APIs

Define a arquitetura geral das APIs do GereIgreja.

Consultar quando a pergunta for:

``` text
Como as APIs se encaixam
na arquitetura da plataforma?
```

É o documento-base da família.

------------------------------------------------------------------------

# 8. GAPI-02 --- Padrões de Endpoints

Define padrões para:

-   rotas;
-   recursos;
-   métodos HTTP;
-   nomenclatura;
-   operações.

Consultar ao desenhar um novo endpoint.

------------------------------------------------------------------------

# 9. GAPI-03 --- Autenticação, Autorização e Tenant

Define como APIs lidam com:

-   identidade;
-   autenticação;
-   permissões;
-   papéis;
-   tenant;
-   isolamento organizacional.

É obrigatório para endpoints protegidos e multi-tenant.

------------------------------------------------------------------------

# 10. GAPI-04 --- Requests, Payloads e Validação

Define:

-   estrutura de entrada;
-   campos;
-   tipos;
-   validação;
-   allowlist;
-   campos protegidos.

Consultar sempre que a API receber dados do consumidor.

------------------------------------------------------------------------

# 11. GAPI-05 --- Responses, Serialização e Erros

Define:

-   status HTTP;
-   respostas;
-   serialização;
-   erros;
-   códigos programáticos;
-   exposição mínima de dados.

É a referência oficial do contrato de saída.

------------------------------------------------------------------------

# 12. GAPI-06 --- Filtros, Busca, Ordenação e Paginação

Define o comportamento de endpoints de listagem.

Consultar para:

-   filtros;
-   pesquisa;
-   ordenação;
-   paginação;
-   parâmetros de consulta.

------------------------------------------------------------------------

# 13. GAPI-07 --- Versionamento e Compatibilidade

Define como contratos evoluem sem quebrar consumidores.

Consultar antes de alterar:

-   endpoint;
-   campo;
-   tipo;
-   semântica;
-   erro;
-   comportamento.

------------------------------------------------------------------------

# 14. GAPI-08 --- Webhooks e Integrações

Define padrões de comunicação com sistemas externos.

Inclui:

-   webhooks;
-   callbacks;
-   assinatura;
-   retries;
-   integrações;
-   falhas externas.

------------------------------------------------------------------------

# 15. GAPI-09 --- Idempotência e Rate Limiting

Define controles de:

``` text
repetição
+
excesso
```

É prioritário em:

-   financeiro;
-   webhooks;
-   autenticação;
-   integrações;
-   exportações;
-   operações críticas.

------------------------------------------------------------------------

# 16. GAPI-10 --- Segurança e Privacidade

Aplica o GSF diretamente às APIs.

Abrange:

-   segurança por design;
-   tenant;
-   dados sensíveis;
-   LGPD;
-   CORS;
-   CSRF;
-   SSRF;
-   uploads;
-   secrets;
-   minimização.

------------------------------------------------------------------------

# 17. GAPI-11 --- Logging, Monitoramento e Auditoria

Define como APIs se tornam observáveis.

Abrange:

-   logs;
-   request ID;
-   correlation ID;
-   métricas;
-   alertas;
-   auditoria;
-   investigação.

------------------------------------------------------------------------

# 18. GAPI-12 --- Testes de APIs

Transforma os contratos da família em evidência automatizada.

Abrange:

-   testes funcionais;
-   segurança;
-   cross-tenant;
-   contratos;
-   integrações;
-   concorrência;
-   regressão.

------------------------------------------------------------------------

# 19. GAPI-13 --- Depreciação e Ciclo de Vida

Define como APIs antigas deixam de existir.

Abrange:

-   depreciação;
-   consumidores;
-   migração;
-   sunset;
-   remoção;
-   limpeza técnica.

------------------------------------------------------------------------

# 20. GAPI-14 --- Mapa e Índice das APIs

Este documento conecta toda a família.

Deverá ser utilizado como ponto inicial quando não estiver claro qual
padrão consultar.

------------------------------------------------------------------------

# 21. Fluxo de uma Requisição

Fluxo conceitual:

``` text
Cliente
   │
   ▼
Endpoint
GAPI-02
   │
   ▼
Autenticação
Tenant
Autorização
GAPI-03
   │
   ▼
Request
Validação
GAPI-04
   │
   ▼
Service / Domínio
   │
   ▼
Response
Erros
GAPI-05
   │
   ▼
Logging / Métricas
GAPI-11
```

Transversalmente:

``` text
GAPI-09
GAPI-10
GAPI-12
```

------------------------------------------------------------------------

# 22. Fluxo de uma Operação Crítica

``` text
Request
   ↓
Rate Limit
   ↓
Autenticação
   ↓
Tenant
   ↓
Autorização
   ↓
Validação
   ↓
Idempotência
   ↓
Transação / Service
   ↓
Auditoria
   ↓
Response
   ↓
Métricas
```

Operações financeiras deverão receber atenção especial nesse fluxo.

------------------------------------------------------------------------

# 23. Fluxo de Integração

``` text
GereIgreja
   │
   ▼
Adapter / Integration Service
   │
   ▼
Fornecedor Externo
   │
   ├── sucesso
   ├── timeout
   ├── 429
   └── erro
   │
   ▼
Retry controlado
   │
   ▼
Observabilidade
```

No retorno:

``` text
Webhook
   ↓
Validação / Assinatura
   ↓
Tenant
   ↓
Idempotência
   ↓
Processamento
   ↓
Auditoria
```

------------------------------------------------------------------------

# 24. Fluxo de Evolução

``` text
Contrato atual
    ↓
Necessidade de mudança
    ↓
GAPI-07
    ↓
Compatível?
  ┌─────┴─────┐
  │           │
 sim         não
  │           │
 evoluir    nova versão
              │
              ▼
          coexistência
              │
              ▼
           GAPI-13
              │
              ▼
        depreciação
              │
              ▼
           sunset
```

------------------------------------------------------------------------

# 25. Classificação das APIs

Toda API deverá possuir classificação suficiente para governança.

Categorias principais:

-   interna;
-   externa;
-   administrativa;
-   webhook;
-   integração.

Uma API poderá participar de mais de uma classificação quando
necessário.

------------------------------------------------------------------------

# 26. APIs Internas

Consumidas por componentes do próprio GereIgreja.

Ainda deverão seguir:

-   autenticação quando aplicável;
-   tenant;
-   contrato;
-   segurança;
-   testes;
-   observabilidade.

"Interna" não significa "sem governança".

------------------------------------------------------------------------

# 27. APIs Externas

Consumidas por terceiros.

Exigem atenção reforçada a:

-   estabilidade;
-   documentação;
-   autenticação;
-   versionamento;
-   rate limiting;
-   depreciação.

------------------------------------------------------------------------

# 28. APIs Administrativas

Operações administrativas deverão possuir:

-   autorização forte;
-   menor privilégio;
-   auditoria;
-   tenant ou escopo global explícito;
-   segurança reforçada.

------------------------------------------------------------------------

# 29. Webhooks

Webhooks recebidos ou emitidos deverão ser inventariados como contratos.

Registrar:

-   evento;
-   direção;
-   fornecedor;
-   versão/schema;
-   segurança;
-   owner.

------------------------------------------------------------------------

# 30. Integrações

Toda integração relevante deverá possuir:

-   sistema externo;
-   finalidade;
-   credencial;
-   tenant quando aplicável;
-   endpoints utilizados;
-   webhooks;
-   owner;
-   observabilidade.

------------------------------------------------------------------------

# 31. Inventário de APIs

O GereIgreja deverá manter inventário progressivo dos contratos
relevantes.

O inventário não substitui documentação detalhada.

Ele responde:

``` text
O que existe?
Onde?
Quem mantém?
Quem usa?
Qual o estado?
```

------------------------------------------------------------------------

# 32. Campos Mínimos do Inventário

Estrutura conceitual:

``` text
id
name
route/event
version
type
owner
domain
authentication
tenant_scope
data_classification
criticality
consumers
status
documentation
```

Campos adicionais poderão ser adotados conforme maturidade.

------------------------------------------------------------------------

# 33. Identificação de Owner

Toda API relevante deverá possuir responsável técnico ou domínio
responsável.

Evitar contratos órfãos.

Owner é responsável por coordenar:

-   evolução;
-   incidentes;
-   documentação;
-   depreciação.

------------------------------------------------------------------------

# 34. Identificação de Tenant

O inventário deverá indicar se o contrato é:

``` text
tenant-scoped
platform-scoped
public
mixed
```

Escopo misto exige regras explícitas.

------------------------------------------------------------------------

# 35. Classificação de Dados

Registrar a classe de dados quando relevante:

-   pública;
-   interna;
-   restrita;
-   confidencial.

Aplicar classificação oficial do GSF.

------------------------------------------------------------------------

# 36. Criticidade

Classificar criticidade conforme impacto.

Exemplo conceitual:

``` text
LOW
MEDIUM
HIGH
CRITICAL
```

Operações financeiras, autenticação e permissões tendem a exigir
tratamento reforçado.

------------------------------------------------------------------------

# 37. Autenticação e Autorização

O inventário deverá permitir identificar:

-   mecanismo de autenticação;
-   necessidade de permissão;
-   identidade técnica;
-   escopo de tenant.

------------------------------------------------------------------------

# 38. Versionamento

Registrar:

-   versão atual;
-   versões suportadas;
-   versão depreciada;
-   sunset quando aplicável.

------------------------------------------------------------------------

# 39. Observabilidade

APIs críticas deverão possuir referência para:

-   logs;
-   métricas;
-   alertas;
-   dashboard;
-   auditoria.

------------------------------------------------------------------------

# 40. Dependências

Mapear dependências relevantes:

``` text
API
→ service
→ banco
→ cache
→ fila
→ fornecedor externo
```

Não é necessário transformar o inventário em mapa completo de código.

------------------------------------------------------------------------

# 41. Consumidores

Consumidores poderão incluir:

-   frontend;
-   aplicativo;
-   módulo interno;
-   integração;
-   parceiro;
-   job;
-   script.

Esse dado é essencial para depreciação.

------------------------------------------------------------------------

# 42. Estado do Ciclo de Vida

Utilizar os estados do GAPI-13:

``` text
PROPOSED
EXPERIMENTAL
ACTIVE
STABLE
DEPRECATED
SUNSET
REMOVED
```

------------------------------------------------------------------------

# 43. Mapa de Dependências Documentais

``` text
                   GEA
                    │
                    ▼
                 GAPI-01
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
      GAF          GSF          GQF
       │            │            │
       └────────────┼────────────┘
                    ▼
               Família GAPI
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
      GOC          GDF          GFE
```

A relação não representa dependência de código obrigatória, mas
governança documental.

------------------------------------------------------------------------

# 44. Relação com GEA

A GEA define a arquitetura empresarial da plataforma.

A família GAPI deverá permanecer coerente com:

-   camadas;
-   módulos;
-   services;
-   infraestrutura;
-   segurança;
-   integração.

------------------------------------------------------------------------

# 45. Relação com GAF

O GAF define autenticação e identidade.

O GAPI não deverá criar mecanismo paralelo.

``` text
GAF
→ identidade

GAPI-03
→ aplicação dessa identidade
na fronteira da API
```

------------------------------------------------------------------------

# 46. Relação com GSF

O GSF define política de segurança.

A família GAPI aplica essa política aos contratos HTTP e integrações.

Especialmente:

-   autorização;
-   multi-tenant;
-   APIs;
-   dados;
-   secrets;
-   logging;
-   vulnerabilidades;
-   incidentes;
-   LGPD;
-   SDLC.

------------------------------------------------------------------------

# 47. Relação com GQF

O GQF define qualidade.

GAPI-12 especializa a qualidade para APIs.

Qualidade inclui:

-   testes;
-   revisão;
-   regressão;
-   compatibilidade;
-   confiabilidade.

------------------------------------------------------------------------

# 48. Relação com GOC

O GOC orienta operação.

GAPI-11 fornece sinais que deverão alimentar:

-   monitoramento;
-   alertas;
-   investigação;
-   resposta operacional.

------------------------------------------------------------------------

# 49. Relação com GDF

O GDF governa documentação.

Contratos, exemplos, changelogs e estados deverão permanecer
documentados conforme os padrões oficiais.

------------------------------------------------------------------------

# 50. Relação com Frontend Engineering

O frontend é consumidor relevante das APIs.

A integração deverá respeitar:

``` text
GAPI
→ contrato backend

GFE
→ consumo frontend
```

O frontend não deverá depender de campos internos não documentados.

------------------------------------------------------------------------

# 51. Relação com Design System

O Design System não governa contratos de API.

Porém, dados e estados retornados pelas APIs alimentam componentes da
interface.

A separação deverá permanecer clara:

``` text
GAPI
→ dados e operações

GDS
→ apresentação e interação visual
```

------------------------------------------------------------------------

# 52. Processo para Criar uma Nova API

Fluxo recomendado:

``` text
1. identificar necessidade
2. definir owner
3. definir recurso/operação
4. aplicar GAPI-01 e GAPI-02
5. definir autenticação/tenant
6. definir request
7. definir response
8. avaliar filtros/paginação
9. avaliar versionamento
10. avaliar idempotência/rate limit
11. revisar segurança/privacidade
12. definir observabilidade
13. criar testes
14. documentar
15. publicar
16. incluir no inventário
```

------------------------------------------------------------------------

# 53. Processo para Alterar uma API

Antes de alterar:

``` text
Mudança
   ↓
Impacta contrato?
   ↓
GAPI-07
   ↓
Impacta segurança?
   ↓
GAPI-10
   ↓
Atualizar testes
   ↓
Atualizar documentação
   ↓
Atualizar inventário se necessário
```

------------------------------------------------------------------------

# 54. Processo para Publicar uma API

Antes de produção:

-   contrato definido;
-   autorização revisada;
-   tenant revisado;
-   validação concluída;
-   segurança revisada;
-   testes aprovados;
-   observabilidade configurada;
-   documentação atualizada;
-   owner definido.

------------------------------------------------------------------------

# 55. Processo para Depreciar uma API

Aplicar GAPI-13.

Resumo:

``` text
inventariar consumidores
        ↓
definir substituição
        ↓
comunicar
        ↓
medir migração
        ↓
sunset
```

------------------------------------------------------------------------

# 56. Processo para Remover uma API

Após sunset:

-   remover rota;
-   remover código morto;
-   remover configurações obsoletas;
-   atualizar testes;
-   atualizar documentação;
-   atualizar inventário;
-   monitorar uso residual.

------------------------------------------------------------------------

# 57. Checklist de Governança

## Identidade

-   [ ] API possui nome;
-   [ ] owner;
-   [ ] domínio;
-   [ ] classificação;
-   [ ] estado.

## Contrato

-   [ ] rota/evento;
-   [ ] versão;
-   [ ] request;
-   [ ] response;
-   [ ] erros.

## Segurança

-   [ ] autenticação;
-   [ ] autorização;
-   [ ] tenant;
-   [ ] classificação de dados;
-   [ ] rate limiting;
-   [ ] idempotência quando necessária.

## Operação

-   [ ] logs;
-   [ ] métricas;
-   [ ] alertas quando necessários;
-   [ ] auditoria quando necessária.

## Qualidade

-   [ ] testes;
-   [ ] regressão;
-   [ ] compatibilidade;
-   [ ] integração testada.

## Ciclo de Vida

-   [ ] consumidores;
-   [ ] documentação;
-   [ ] status;
-   [ ] depreciação quando aplicável;
-   [ ] sunset quando aplicável.

------------------------------------------------------------------------

# 58. Matriz de Referência

  Necessidade                      Documento principal
  -------------------------------- ---------------------
  arquitetura da API               GAPI-01
  criar endpoint                   GAPI-02
  autenticação/permissão/tenant    GAPI-03
  validar payload                  GAPI-04
  definir response/erro            GAPI-05
  filtros/busca/paginação          GAPI-06
  alterar contrato/versionar       GAPI-07
  webhook/integração               GAPI-08
  retry/duplicidade/rate limit     GAPI-09
  segurança/LGPD                   GAPI-10
  logs/métricas/auditoria          GAPI-11
  testes                           GAPI-12
  depreciação/sunset               GAPI-13
  localizar padrões e governança   GAPI-14

------------------------------------------------------------------------

# 59. Anti-Padrões

Evitar:

``` text
endpoint criado
sem owner
```

------------------------------------------------------------------------

``` text
API interna
sem documentação
```

------------------------------------------------------------------------

``` text
tenant implícito
sem teste cross-tenant
```

------------------------------------------------------------------------

``` text
integração
sem inventário
```

------------------------------------------------------------------------

``` text
versão antiga
sem consumidores mapeados
```

------------------------------------------------------------------------

``` text
contrato alterado
sem GAPI-07
```

------------------------------------------------------------------------

``` text
API crítica
sem observabilidade
```

------------------------------------------------------------------------

``` text
documentação
não corresponde ao comportamento real
```

------------------------------------------------------------------------

``` text
GAPI-14
como substituto dos documentos especializados
```

------------------------------------------------------------------------

# 60. Documentos Relacionados

## GereIgreja API Engineering

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

## GereIgreja Enterprise Architecture

-   GEA --- GereIgreja Enterprise Architecture
-   GEA-07 --- Arquitetura da Segurança

## GereIgreja Security Framework

-   GSF-03 --- GereIgreja Security Framework
-   GSF-04 --- Autorização e Controle de Acesso
-   GSF-05 --- Segurança Multi-Tenant
-   GSF-07 --- Segurança das APIs
-   GSF-08 --- Segurança de Dados e Privacidade
-   GSF-09 --- Gestão de Segredos e Criptografia
-   GSF-10 --- Logging, Monitoramento e Auditoria
-   GSF-12 --- Gestão de Vulnerabilidades
-   GSF-13 --- Gestão de Incidentes de Segurança
-   GSF-14 --- Conformidade e LGPD
-   GSF-15 --- Secure Development Lifecycle

## Outros Frameworks

-   GAF --- GereIgreja Authentication Framework
-   GQF --- GereIgreja Quality Framework
-   GOC --- GereIgreja Operations Center
-   GDF --- GereIgreja Documentation Framework

## Frontend e Design

-   GFE --- GereIgreja Frontend Engineering
-   GDS --- GereIgreja Design System

------------------------------------------------------------------------

# 61. Princípios Finais

A família GAPI estabelece uma linha contínua de governança:

``` text
Arquitetar
    ↓
Contratar
    ↓
Autenticar
    ↓
Autorizar
    ↓
Validar
    ↓
Responder
    ↓
Integrar
    ↓
Proteger
    ↓
Observar
    ↓
Testar
    ↓
Evoluir
    ↓
Depreciar
    ↓
Remover
```

Nenhum endpoint deverá ser visto isoladamente.

Ele pertence a:

``` text
um domínio
+
um tenant ou escopo
+
um contrato
+
uma política de segurança
+
um ciclo de vida
+
uma cadeia operacional
```

O princípio central do GAPI-14 é:

``` text
Toda API relevante
deve ser conhecida,
classificada,
documentada,
testada,
observável
e possuir responsável.
```

Com este documento, a família GAPI passa a possuir um mapa consolidado
para orientar criação, evolução, operação e retirada dos contratos de
API do GereIgreja.

------------------------------------------------------------------------

# 62. Status do Documento

**Pasta**

`docs/api/`

**Arquivo**

`14-Mapa-e-Indice-das-APIs.md`

**Documento**

`GAPI-14`

**Código**

`GAPI-API-MAP-INDEX`

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

`GAPI-13 — Depreciação e Ciclo de Vida`

**Posição na família**

`Documento de fechamento, mapa e índice da família GAPI`
