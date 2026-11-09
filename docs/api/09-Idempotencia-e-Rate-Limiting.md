Pasta:

docs/api/

Arquivo:

09-Idempotencia-e-Rate-Limiting.md

Documento:

GAPI-09

Código:

GAPI-IDEMPOTENCY-RATE-LIMITING

Família:

GAPI --- GereIgreja API Engineering

Frameworks relacionados:

GEA --- GereIgreja Enterprise Architecture GAF --- GereIgreja
Authentication Framework GSF --- GereIgreja Security Framework GQF ---
GereIgreja Quality Framework GOC --- GereIgreja Operations Center

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GAPI-09 --- Idempotência e Rate Limiting

> "Uma API confiável deve resistir tanto à repetição legítima de
> requisições quanto ao excesso de requisições que comprometa a
> plataforma."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com a Família GAPI
4.  Princípios
5.  Idempotência
6.  Por que Idempotência é Necessária
7.  Idempotência HTTP
8.  Operações Naturalmente Idempotentes
9.  Operações Não Idempotentes
10. Casos Prioritários no GereIgreja
11. Idempotency-Key
12. Escopo da Chave
13. Geração da Chave
14. Armazenamento
15. Tenant e Idempotência
16. Usuário e Identidade Técnica
17. Fingerprint da Requisição
18. Repetição com Mesmo Payload
19. Repetição com Payload Diferente
20. Resposta Reutilizada
21. Estado em Processamento
22. Concorrência
23. Transações
24. Expiração e Retenção
25. Idempotência em Integrações
26. Idempotência em Webhooks
27. Idempotência Financeira
28. Tasks e Jobs
29. Reprocessamento
30. Rate Limiting
31. Objetivos do Rate Limiting
32. Dimensões de Limitação
33. Limite por IP
34. Limite por Usuário
35. Limite por Tenant
36. Limite por Credencial
37. Limite por Endpoint
38. Limite por Operação
39. Endpoints de Autenticação
40. APIs Públicas
41. Integrações
42. Webhooks
43. Operações Pesadas
44. Exportações
45. Limites Globais
46. Limites Específicos
47. Janelas de Tempo
48. Algoritmos
49. HTTP 429
50. Retry-After
51. Headers de Limite
52. Exceder Limites
53. Fail Open e Fail Closed
54. Armazenamento Distribuído
55. Cache e Redis
56. Multi-Tenant
57. Segurança
58. Disponibilidade
59. Observabilidade
60. Logging
61. Métricas
62. Alertas
63. Ajuste de Limites
64. Exceções e Bypass
65. Testes de Idempotência
66. Testes de Rate Limiting
67. Anti-Padrões
68. Exemplo de Operação Idempotente
69. Exemplo de Rate Limiting
70. Checklist
71. Documentos Relacionados
72. Princípios Finais
73. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece os padrões oficiais de idempotência e rate
limiting das APIs do GereIgreja.

Seu objetivo é proteger a plataforma contra dois problemas distintos:

``` text
Repetição
→ mesma operação executada mais de uma vez

Excesso
→ quantidade de requisições acima do aceitável
```

Esses controles são especialmente importantes em operações financeiras,
integrações, webhooks, autenticação, exportações e processamento
assíncrono.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   APIs REST;
-   endpoints internos;
-   APIs externas;
-   webhooks;
-   integrações;
-   callbacks;
-   operações financeiras;
-   criação de recursos críticos;
-   exportações;
-   autenticação;
-   tasks originadas por requests;
-   operações sujeitas a retry.

------------------------------------------------------------------------

# 3. Relação com a Família GAPI

``` text
GAPI-08
Webhooks e Integrações
        ↓
GAPI-09
Idempotência + Rate Limiting
        ↓
Confiabilidade e Proteção Operacional
```

O documento complementa também GAPI-02, GAPI-04, GAPI-05 e os controles
do GSF.

------------------------------------------------------------------------

# 4. Princípios

Os controles deverão observar:

-   comportamento determinístico;
-   tenant explícito;
-   escopo definido;
-   atomicidade;
-   limites proporcionais ao risco;
-   observabilidade;
-   segurança;
-   possibilidade de ajuste operacional.

Idempotência e rate limiting não deverão depender exclusivamente do
frontend.

------------------------------------------------------------------------

# 5. Idempotência

Uma operação é idempotente quando repeti-la com a mesma intenção não
produz efeitos adicionais indevidos.

``` text
Primeira requisição
→ efeito

Mesma requisição repetida
→ mesmo resultado lógico
→ sem novo efeito indevido
```

------------------------------------------------------------------------

# 6. Por que Idempotência é Necessária

Requisições podem ser repetidas por:

-   timeout;
-   retry automático;
-   duplo clique;
-   perda da resposta;
-   reenvio de webhook;
-   falha de rede;
-   worker reiniciado;
-   consumidor sem confirmação.

A API deverá assumir que repetições podem ocorrer.

------------------------------------------------------------------------

# 7. Idempotência HTTP

A semântica HTTP já fornece características importantes.

Conceitualmente:

  Método   Idempotência esperada
  -------- ----------------------------
  GET      sim
  HEAD     sim
  PUT      sim, conforme contrato
  DELETE   sim quanto ao estado final
  POST     não necessariamente
  PATCH    depende da operação

A implementação real deverá preservar a semântica declarada.

------------------------------------------------------------------------

# 8. Operações Naturalmente Idempotentes

Exemplo:

``` text
definir status = inativo
```

Executar novamente tende a manter o mesmo estado.

Isso é diferente de:

``` text
incrementar contador em 1
```

que produz novo efeito a cada execução.

------------------------------------------------------------------------

# 9. Operações Não Idempotentes

Operações de criação e comandos podem exigir proteção adicional.

Exemplos:

-   criar lançamento;
-   registrar pagamento;
-   emitir cobrança;
-   gerar transação externa;
-   criar inscrição;
-   enviar comunicação.

------------------------------------------------------------------------

# 10. Casos Prioritários no GereIgreja

Idempotência deverá ser avaliada prioritariamente em:

-   financeiro;
-   webhooks;
-   integrações;
-   importações;
-   inscrições;
-   processamento assíncrono;
-   comandos com efeitos externos;
-   operações sujeitas a retry.

------------------------------------------------------------------------

# 11. Idempotency-Key

Quando necessário, o consumidor poderá fornecer uma chave:

``` text
Idempotency-Key: <valor-opaco>
```

A chave identifica uma intenção de operação dentro de um escopo
definido.

------------------------------------------------------------------------

# 12. Escopo da Chave

A chave nunca deverá ser global sem necessidade.

O escopo poderá incluir:

``` text
tenant
+
identidade
+
endpoint/operação
+
idempotency_key
```

Isso evita colisões entre organizações e operações distintas.

------------------------------------------------------------------------

# 13. Geração da Chave

A chave deverá possuir entropia suficiente e ser tratada como
identificador opaco.

Poderá ser gerada pelo consumidor conforme contrato.

Não utilizar valores previsíveis simples como único mecanismo quando
houver risco de colisão.

------------------------------------------------------------------------

# 14. Armazenamento

O servidor deverá armazenar informação suficiente para reconhecer
repetição.

Exemplo conceitual:

``` text
tenant_id
actor/integration_id
operation
key
request_fingerprint
status
response_reference
created_at
expires_at
```

A estrutura concreta deverá seguir a arquitetura da plataforma.

------------------------------------------------------------------------

# 15. Tenant e Idempotência

A chave deverá ser isolada por tenant em operações organizacionais.

``` text
Tenant A + chave X
≠
Tenant B + chave X
```

Nunca permitir que uma chave de uma igreja interfira em outra.

------------------------------------------------------------------------

# 16. Usuário e Identidade Técnica

Quando apropriado, incluir no escopo:

-   usuário;
-   integração;
-   cliente técnico.

A decisão dependerá da semântica da operação.

------------------------------------------------------------------------

# 17. Fingerprint da Requisição

Poderá ser calculado fingerprint dos elementos relevantes da requisição.

Objetivo:

``` text
mesma chave
+
mesma intenção
→ repetição válida

mesma chave
+
payload diferente
→ conflito
```

Secrets e dados desnecessários não deverão ser incorporados de forma
insegura.

------------------------------------------------------------------------

# 18. Repetição com Mesmo Payload

Quando a mesma chave representar a mesma operação já concluída, a API
deverá evitar executar novamente o efeito.

Poderá retornar o resultado anterior conforme contrato.

------------------------------------------------------------------------

# 19. Repetição com Payload Diferente

A mesma chave não deverá ser reutilizada para uma intenção diferente.

Resposta recomendada:

``` text
409 Conflict
```

ou erro equivalente padronizado.

Exemplo conceitual:

``` json
{
  "error": {
    "code": "idempotency_conflict",
    "message": "A chave de idempotência já foi utilizada com outra requisição."
  }
}
```

------------------------------------------------------------------------

# 20. Resposta Reutilizada

Quando possível, a repetição poderá devolver:

-   mesmo status lógico;
-   mesma referência de recurso;
-   representação compatível.

Não é necessário repetir efeitos colaterais para reproduzir a resposta.

------------------------------------------------------------------------

# 21. Estado em Processamento

Duas requisições idênticas poderão chegar antes da conclusão da
primeira.

O registro de idempotência deverá prever estado como:

``` text
processing
completed
failed
```

A semântica concreta deverá impedir dupla execução.

------------------------------------------------------------------------

# 22. Concorrência

A proteção deverá ser atômica.

Fluxo inseguro:

``` text
verificar chave
   ↓
não existe
   ↓
duas requisições continuam
```

Utilizar mecanismos como:

-   restrição única;
-   transação;
-   lock;
-   operação atômica em storage apropriado.

------------------------------------------------------------------------

# 23. Transações

Quando o efeito e o registro de idempotência forem persistidos no mesmo
banco, avaliar transação para manter consistência.

Não marcar operação como concluída antes de seu efeito estar
efetivamente confirmado.

------------------------------------------------------------------------

# 24. Expiração e Retenção

Chaves não precisam necessariamente ser armazenadas para sempre.

A retenção deverá considerar:

-   janela de retry;
-   criticidade;
-   volume;
-   requisitos de auditoria;
-   comportamento do consumidor.

Operações financeiras poderão exigir retenção distinta de operações
comuns.

------------------------------------------------------------------------

# 25. Idempotência em Integrações

Chamadas externas também podem ser repetidas.

Quando o fornecedor suportar chave de idempotência, utilizá-la em
operações críticas conforme seu contrato.

Quando não suportar, o GereIgreja deverá controlar seus próprios estados
e reconciliação.

------------------------------------------------------------------------

# 26. Idempotência em Webhooks

Webhooks deverão utilizar identificador externo de evento quando
disponível.

Exemplo:

``` text
tenant
+
provider
+
external_event_id
```

Eventos duplicados não deverão produzir efeitos duplicados.

------------------------------------------------------------------------

# 27. Idempotência Financeira

Operações financeiras exigem atenção máxima.

Exemplos:

``` text
registrar pagamento
criar lançamento
processar confirmação
emitir cobrança
```

Uma falha de idempotência poderá gerar duplicidade contábil ou
financeira.

Além da chave, avaliar:

-   unicidade;
-   reconciliação;
-   auditoria;
-   estado externo;
-   transação.

------------------------------------------------------------------------

# 28. Tasks e Jobs

Tasks também poderão ser executadas mais de uma vez.

O código da task deverá ser idempotente quando houver risco de retry.

Não assumir entrega exatamente uma vez pela fila.

------------------------------------------------------------------------

# 29. Reprocessamento

Reprocessamento manual deverá possuir comportamento explícito.

Distinguir:

``` text
retry da mesma operação
```

de:

``` text
nova operação intencional
```

Uma nova intenção poderá exigir nova chave.

------------------------------------------------------------------------

# 30. Rate Limiting

Rate limiting controla quantas requisições um escopo pode executar em
determinada janela.

``` text
Identidade / IP / Tenant
          ↓
        Limite
          ↓
   permitir ou bloquear
```

------------------------------------------------------------------------

# 31. Objetivos do Rate Limiting

O controle deverá ajudar a:

-   reduzir abuso;
-   proteger autenticação;
-   preservar disponibilidade;
-   controlar custo;
-   evitar sobrecarga;
-   proteger fornecedores externos;
-   reduzir automações defeituosas.

------------------------------------------------------------------------

# 32. Dimensões de Limitação

Limites poderão considerar:

-   IP;
-   usuário;
-   tenant;
-   API key;
-   integração;
-   endpoint;
-   operação;
-   combinação desses elementos.

Nenhuma dimensão isolada é adequada para todos os casos.

------------------------------------------------------------------------

# 33. Limite por IP

Útil principalmente para tráfego não autenticado.

Deverá considerar proxies e infraestrutura de rede de forma segura.

Não confiar cegamente em headers de IP fornecidos pelo cliente.

------------------------------------------------------------------------

# 34. Limite por Usuário

Adequado para controlar uso autenticado individual.

Não substitui limite por tenant quando uma organização possui muitos
usuários.

------------------------------------------------------------------------

# 35. Limite por Tenant

Protege a plataforma contra consumo excessivo concentrado em uma
organização.

Também ajuda a evitar que um tenant afete a disponibilidade dos demais.

------------------------------------------------------------------------

# 36. Limite por Credencial

Integrações deverão poder possuir limites por:

-   API key;
-   client;
-   token técnico;
-   configuração de integração.

------------------------------------------------------------------------

# 37. Limite por Endpoint

Endpoints possuem custos diferentes.

Exemplo:

``` text
GET detalhe
≠
gerar relatório
≠
exportar milhares de registros
```

Limites deverão refletir custo e risco.

------------------------------------------------------------------------

# 38. Limite por Operação

Algumas ações merecem controle específico mesmo dentro do mesmo
endpoint.

Exemplos:

-   envio de código;
-   recuperação de acesso;
-   geração de exportação;
-   disparo de comunicação.

------------------------------------------------------------------------

# 39. Endpoints de Autenticação

Endpoints relacionados a autenticação deverão possuir proteção rigorosa.

Exemplos:

-   login;
-   recuperação;
-   verificação;
-   emissão de código;
-   tentativas de credencial.

Aplicar GAF e GSF.

------------------------------------------------------------------------

# 40. APIs Públicas

APIs sem autenticação deverão possuir proteção proporcional ao risco.

Rate limiting é especialmente importante porque não existe identidade
autenticada confiável para controlar abuso.

------------------------------------------------------------------------

# 41. Integrações

Integrações deverão respeitar:

-   limites internos;
-   limites do fornecedor;
-   capacidade de retry;
-   quotas contratadas.

------------------------------------------------------------------------

# 42. Webhooks

Endpoints de webhook também poderão sofrer abuso.

Rate limiting deverá ser configurado sem bloquear tráfego legítimo de
provedores durante rajadas esperadas.

Assinatura continua obrigatória quando aplicável.

------------------------------------------------------------------------

# 43. Operações Pesadas

Consultas caras deverão possuir controles adicionais.

Exemplos:

-   dashboards complexos;
-   relatórios;
-   agregações;
-   busca extensa;
-   geração de documentos.

------------------------------------------------------------------------

# 44. Exportações

Exportações não deverão permitir geração ilimitada.

Avaliar:

``` text
limite por usuário
+
limite por tenant
+
quantidade de jobs simultâneos
```

------------------------------------------------------------------------

# 45. Limites Globais

A infraestrutura poderá possuir limite global de proteção.

Esse limite não substitui políticas específicas por usuário, tenant ou
operação.

------------------------------------------------------------------------

# 46. Limites Específicos

Exemplo conceitual, não normativo:

``` text
login
→ limite baixo e defensivo

consultas comuns autenticadas
→ limite mais alto

exportações
→ limite baixo por janela
```

Valores deverão ser definidos por medição e risco, não copiados
genericamente.

------------------------------------------------------------------------

# 47. Janelas de Tempo

Possíveis modelos:

``` text
N por minuto
N por hora
N por dia
```

Alguns endpoints poderão combinar janelas.

------------------------------------------------------------------------

# 48. Algoritmos

Poderão ser utilizados:

-   fixed window;
-   sliding window;
-   token bucket;
-   leaky bucket.

A escolha deverá considerar:

-   precisão;
-   distribuição;
-   custo;
-   comportamento de burst.

------------------------------------------------------------------------

# 49. HTTP 429

Quando o limite for excedido, utilizar:

``` text
429 Too Many Requests
```

Resposta conceitual:

``` json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Limite de requisições excedido. Tente novamente mais tarde."
  }
}
```

------------------------------------------------------------------------

# 50. Retry-After

Quando apropriado, informar:

``` text
Retry-After
```

para orientar o consumidor sobre nova tentativa.

------------------------------------------------------------------------

# 51. Headers de Limite

Headers adicionais poderão ser utilizados se houver padrão oficial e
necessidade real.

Não expor detalhes que facilitem abuso sem benefício operacional.

------------------------------------------------------------------------

# 52. Exceder Limites

O bloqueio deverá ocorrer antes de executar operações caras sempre que
possível.

``` text
Request
   ↓
Rate Limit
   ↓
Authentication / Context
   ↓
Operation
```

A posição exata poderá variar conforme o tipo de limite e necessidade de
identidade.

------------------------------------------------------------------------

# 53. Fail Open e Fail Closed

Se o storage do rate limiter falhar, deverá existir decisão explícita.

``` text
Fail open
→ permite requisição

Fail closed
→ bloqueia requisição
```

A escolha dependerá do risco.

Exemplo:

-   login pode exigir postura mais defensiva;
-   endpoint interno de baixa criticidade poderá priorizar
    disponibilidade.

------------------------------------------------------------------------

# 54. Armazenamento Distribuído

Em múltiplas instâncias da aplicação, rate limiting não deverá depender
apenas de memória local se o limite precisar ser global.

O storage deverá ser compartilhado ou arquiteturalmente adequado.

------------------------------------------------------------------------

# 55. Cache e Redis

Quando Redis ou tecnologia equivalente for utilizada, avaliar:

-   atomicidade;
-   TTL;
-   disponibilidade;
-   isolamento de chaves;
-   prefixos;
-   tenant;
-   comportamento em falha.

A tecnologia concreta deverá seguir a infraestrutura oficial do
GereIgreja.

------------------------------------------------------------------------

# 56. Multi-Tenant

Rate limiting deverá preservar justiça entre tenants.

``` text
Tenant A com tráfego excessivo
não deve
consumir toda capacidade
do Tenant B
```

Limites organizacionais poderão complementar controles globais.

------------------------------------------------------------------------

# 57. Segurança

Rate limiting é controle complementar.

Não substitui:

-   autenticação;
-   autorização;
-   validação;
-   WAF/firewall;
-   monitoramento;
-   proteção contra ataques distribuídos.

------------------------------------------------------------------------

# 58. Disponibilidade

Limites excessivamente baixos também podem causar indisponibilidade
funcional.

O objetivo é:

``` text
proteger sem impedir
uso legítimo
```

A configuração deverá ser baseada em dados.

------------------------------------------------------------------------

# 59. Observabilidade

Deverá ser possível identificar:

-   quem atingiu limite;
-   qual endpoint;
-   qual tenant;
-   frequência;
-   origem;
-   tendência.

Sem registrar dados sensíveis desnecessários.

------------------------------------------------------------------------

# 60. Logging

Eventos relevantes poderão registrar:

``` text
request_id
tenant_id
user/integration_id
endpoint
limit_policy
result
```

Não registrar tokens ou secrets.

------------------------------------------------------------------------

# 61. Métricas

Métricas recomendadas conceitualmente:

``` text
rate_limit_allowed_total
rate_limit_blocked_total
idempotency_hit_total
idempotency_conflict_total
idempotency_processing_total
```

Os nomes concretos dependerão da stack.

------------------------------------------------------------------------

# 62. Alertas

Alertas poderão ser necessários para:

-   aumento abrupto de 429;
-   ataques de autenticação;
-   tenant com comportamento anormal;
-   falha do storage de rate limiting;
-   conflitos de idempotência em operações financeiras.

------------------------------------------------------------------------

# 63. Ajuste de Limites

Limites deverão ser revisados com base em:

-   métricas;
-   comportamento real;
-   crescimento;
-   custo;
-   incidentes;
-   novos clientes;
-   novas integrações.

Rate limiting é política operacional evolutiva.

------------------------------------------------------------------------

# 64. Exceções e Bypass

Bypasses deverão ser raros e controlados.

Nunca utilizar:

``` text
X-Bypass-Rate-Limit: true
```

como header público sem mecanismo seguro.

Exceções deverão possuir:

-   justificativa;
-   identidade;
-   escopo;
-   prazo;
-   auditoria quando necessário.

------------------------------------------------------------------------

# 65. Testes de Idempotência

Testar:

-   primeira requisição;
-   repetição;
-   mesma chave e mesmo payload;
-   mesma chave e payload diferente;
-   tenants diferentes;
-   usuários/integrações diferentes quando aplicável;
-   requisições concorrentes;
-   falha durante processamento;
-   retry após timeout;
-   expiração da chave.

------------------------------------------------------------------------

# 66. Testes de Rate Limiting

Testar:

-   abaixo do limite;
-   exatamente no limite;
-   acima do limite;
-   janela expirada;
-   usuários distintos;
-   tenants distintos;
-   IPs distintos quando aplicável;
-   HTTP 429;
-   Retry-After;
-   falha do storage;
-   concorrência.

------------------------------------------------------------------------

# 67. Anti-Padrões

Evitar:

``` text
duplo clique
→ dois lançamentos financeiros
```

------------------------------------------------------------------------

``` text
webhook duplicado
→ processar novamente
```

------------------------------------------------------------------------

``` text
Idempotency-Key
global para todos os tenants
```

------------------------------------------------------------------------

``` text
verificar chave
sem atomicidade
```

------------------------------------------------------------------------

``` text
retry infinito
```

------------------------------------------------------------------------

``` text
rate limit apenas no frontend
```

------------------------------------------------------------------------

``` text
um limite igual
para todos os endpoints
```

------------------------------------------------------------------------

``` text
memória local
como contador global
em múltiplas instâncias
```

------------------------------------------------------------------------

``` text
bypass permanente
para resolver configuração ruim
```

------------------------------------------------------------------------

# 68. Exemplo de Operação Idempotente

``` text
POST /api/v1/financeiro/lancamentos/

Idempotency-Key: 8c95...
               │
               ▼
          Authentication
               │
               ▼
            Tenant
               │
               ▼
           Permission
               │
               ▼
     Localizar chave no escopo
               │
       ┌───────┴────────┐
       │                │
     nova?            existe?
       │                │
       ▼                ▼
 criar registro     comparar fingerprint
 processing             │
       │          ┌─────┴─────┐
       ▼          │           │
   executar     igual?     diferente?
   service        │           │
       │          ▼           ▼
       ▼       resposta      409
  transaction   anterior
       │
       ▼
 completed
       │
       ▼
 resposta
```

------------------------------------------------------------------------

# 69. Exemplo de Rate Limiting

``` text
Request
   │
   ▼
Identificar política
   │
   ▼
Chave de limite:
tenant + user + endpoint
   │
   ▼
Incremento atômico
   │
   ├──► dentro do limite
   │       ↓
   │    continuar
   │
   └──► excedido
           ↓
         429
           +
      Retry-After
```

------------------------------------------------------------------------

# 70. Checklist

## Idempotência

-   [ ] operação precisa de idempotência;
-   [ ] chave definida;
-   [ ] escopo inclui tenant;
-   [ ] identidade/operação avaliadas;
-   [ ] fingerprint avaliado;
-   [ ] armazenamento atômico;
-   [ ] concorrência protegida;
-   [ ] resposta repetida definida;
-   [ ] conflito definido;
-   [ ] retenção definida.

## Integrações

-   [ ] external event ID utilizado quando disponível;
-   [ ] webhooks duplicados tratados;
-   [ ] retries seguros;
-   [ ] tasks idempotentes;
-   [ ] operações financeiras protegidas.

## Rate Limiting

-   [ ] política definida;
-   [ ] dimensão correta;
-   [ ] limite proporcional;
-   [ ] janela definida;
-   [ ] 429 padronizado;
-   [ ] Retry-After avaliado;
-   [ ] storage distribuído quando necessário;
-   [ ] comportamento em falha definido.

## Multi-Tenant

-   [ ] chaves isoladas;
-   [ ] contadores isolados quando necessário;
-   [ ] um tenant não afeta indevidamente outro.

## Observabilidade

-   [ ] logs;
-   [ ] métricas;
-   [ ] alertas;
-   [ ] conflitos monitorados;
-   [ ] 429 monitorados.

## Testes

-   [ ] repetição;
-   [ ] concorrência;
-   [ ] payload diferente;
-   [ ] tenant diferente;
-   [ ] limite excedido;
-   [ ] janela renovada;
-   [ ] storage indisponível.

------------------------------------------------------------------------

# 71. Documentos Relacionados

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

-   GSF-04 --- Autorização e Controle de Acesso
-   GSF-05 --- Segurança Multi-Tenant
-   GSF-07 --- Segurança das APIs
-   GSF-10 --- Logging, Monitoramento e Auditoria
-   GSF-12 --- Gestão de Vulnerabilidades
-   GSF-13 --- Gestão de Incidentes de Segurança
-   GSF-15 --- Secure Development Lifecycle

## Autenticação

-   GAF --- GereIgreja Authentication Framework

## Operações

-   GOC --- GereIgreja Operations Center

------------------------------------------------------------------------

# 72. Princípios Finais

O GereIgreja deverá assumir que redes, clientes, filas e integrações
podem repetir operações.

``` text
Retry
não pode significar
duplicidade de negócio.
```

Também deverá assumir que recursos da plataforma são finitos.

``` text
Acesso permitido
não significa
uso ilimitado.
```

Os dois controles se complementam:

``` text
Idempotência
→ controla repetição da intenção

Rate Limiting
→ controla frequência de uso
```

O princípio final é:

``` text
Toda operação crítica
deve sobreviver a retries.

Todo endpoint exposto
deve possuir uma estratégia
contra excesso proporcional
ao seu risco.
```

Esses mecanismos deverão preservar isolamento multi-tenant,
disponibilidade, integridade financeira e previsibilidade operacional em
toda a plataforma GereIgreja.

------------------------------------------------------------------------

# 73. Status do Documento

**Pasta**

`docs/api/`

**Arquivo**

`09-Idempotencia-e-Rate-Limiting.md`

**Documento**

`GAPI-09`

**Código**

`GAPI-IDEMPOTENCY-RATE-LIMITING`

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

`GAPI-08 — Webhooks e Integrações`

**Próximo documento recomendado**

`10-Seguranca-e-Privacidade.md`
