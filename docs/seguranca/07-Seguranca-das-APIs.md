````markdown
Pasta:

docs/seguranca/

Arquivo:

07-Seguranca-das-APIs.md

Documento:

GSF-07

Código:

GSF-API-SECURITY

Família:

GSF — GereIgreja Security

Framework:

GSF — GereIgreja Security Framework

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GSF-07 — Segurança das APIs

> "Toda API do GereIgreja deve ser tratada como uma fronteira de segurança. Autenticar uma requisição não basta: é necessário validar identidade, autorização, tenant, recurso, entrada, saída e finalidade."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Relação com os Demais Documentos
5. Princípios
6. API como Fronteira de Segurança
7. Tipos de API no GereIgreja
8. APIs Internas
9. APIs Externas
10. APIs Públicas
11. APIs Privadas
12. Autenticação
13. Autorização
14. Multi-Tenant
15. Identidade da Requisição
16. Escopo Organizacional
17. Controle por Recurso
18. Controle por Operação
19. Permissões
20. Endpoints
21. Métodos HTTP
22. GET
23. POST
24. PUT e PATCH
25. DELETE
26. Idempotência
27. Validação de Entrada
28. Parâmetros de URL
29. Query Strings
30. Payloads JSON
31. Headers
32. IDs e Referências
33. Serialização
34. Minimização de Dados
35. Campos Sensíveis
36. Respostas
37. Status HTTP
38. Mensagens de Erro
39. Enumeração
40. IDOR
41. Paginação
42. Filtros
43. Ordenação
44. Busca
45. Exportações por API
46. Uploads por API
47. Downloads por API
48. Rate Limiting
49. Proteção contra Abuso
50. Brute Force
51. Replay
52. Webhooks
53. Assinatura de Webhooks
54. Integrações Externas
55. Tokens e Credenciais
56. API Keys
57. Rotação de Credenciais
58. Revogação
59. Expiração
60. Segredos
61. CORS
62. CSRF
63. HTTPS
64. Versionamento
65. Compatibilidade
66. Depreciação
67. Logs
68. Auditoria
69. Monitoramento
70. Dados Confidenciais
71. Financeiro
72. Secretaria
73. Comunicação
74. Eventos
75. Escola Bíblica
76. Patrimônio
77. Administração
78. Portal Público
79. Tasks e APIs
80. Cache
81. Performance e Segurança
82. Tratamento de Exceções
83. Dependências
84. Testes
85. Testes de Autenticação
86. Testes de Autorização
87. Testes Multi-Tenant
88. Testes de Entrada
89. Testes de Resposta
90. Testes de Rate Limiting
91. Testes de Webhooks
92. Testes de Regressão
93. Evidências Arquiteturais
94. Especificações Oficiais
95. Anti-Padrões
96. Checklist
97. Documentos Relacionados
98. Princípios Finais
99. Status do Documento

---

# 1. Objetivo

Este documento estabelece os padrões oficiais de segurança para APIs do GereIgreja.

Seu objetivo é garantir que toda API:

- identifique corretamente o chamador;
- aplique autorização;
- respeite o isolamento multi-tenant;
- valide entradas;
- minimize respostas;
- proteja informações sensíveis;
- registre eventos relevantes;
- limite abuso;
- mantenha compatibilidade;
- falhe de maneira segura.

Nenhuma API deverá ser considerada segura apenas porque:

- é interna;
- é consumida pelo próprio frontend;
- exige autenticação;
- utiliza HTTPS;
- possui um token válido.

A segurança deverá ser avaliada em todas as camadas.

---

# 2. Escopo

Este documento aplica-se a:

- APIs REST;
- endpoints JSON;
- endpoints internos;
- APIs utilizadas por aplicações móveis futuras;
- integrações externas;
- webhooks;
- endpoints de automação;
- endpoints administrativos;
- endpoints de exportação;
- endpoints de upload;
- serviços integrados;
- APIs eventualmente utilizadas pelo Portal Público.

Aplica-se também a endpoints que não utilizem formalmente um framework REST, mas ofereçam resposta estruturada para consumo por software.

---

# 3. Papel deste Documento

O GSF-07 especializa os princípios definidos em:

```text
GSF-01 — Fundamentos
        ↓
GSF-03 — Gestão de Identidade
        ↓
GSF-04 — Autorização
        ↓
GSF-05 — Multi-Tenant
        ↓
GSF-06 — Segurança da Aplicação
        ↓
GSF-07 — Segurança das APIs
````

O foco deste documento é a fronteira programática entre o GereIgreja e seus consumidores.

---

# 4. Relação com os Demais Documentos

Este documento deverá ser aplicado em conjunto com:

```text
GSF-03
→ identidade

GSF-04
→ autorização

GSF-05
→ isolamento multi-tenant

GSF-06
→ segurança de aplicação

GSF-08
→ proteção e privacidade de dados

GSF-10
→ logging, monitoramento e auditoria
```

Uma API segura depende desses controles combinados.

---

# 5. Princípios

Toda API deverá seguir:

* autenticação apropriada;
* autorização explícita;
* mínimo privilégio;
* tenant validado;
* entrada não confiável;
* resposta mínima;
* fail closed;
* rate limiting quando necessário;
* rastreabilidade;
* versionamento;
* compatibilidade;
* segurança por padrão.

---

# 6. API como Fronteira de Segurança

Uma API representa fronteira entre:

```text
Cliente
   ↓
Rede
   ↓
Endpoint
   ↓
Autenticação
   ↓
Autorização
   ↓
Tenant
   ↓
Domínio
   ↓
Dados
```

Cada passagem deverá ser validada.

---

# 7. Tipos de API no GereIgreja

As APIs poderão ser classificadas como:

```text
Pública
Privada
Interna
Externa
Administrativa
Integração
Webhook
```

A classificação deverá considerar quem pode consumir e quais dados são expostos.

---

# 8. APIs Internas

Uma API utilizada apenas pelo próprio GereIgreja não deverá ser considerada confiável automaticamente.

Exemplo incorreto:

```text
Frontend oficial
=
request confiável
```

O usuário poderá reproduzir manualmente a requisição.

Portanto, autenticação, autorização e tenant continuam obrigatórios quando aplicáveis.

---

# 9. APIs Externas

APIs consumidas por sistemas externos deverão possuir contratos claros.

Deverão definir:

* autenticação;
* autorização;
* formato;
* limites;
* versionamento;
* erros;
* credenciais;
* revogação.

---

# 10. APIs Públicas

Uma API pública poderá dispensar autenticação quando sua finalidade realmente exigir acesso público.

Entretanto deverá possuir:

* validação;
* limitação de abuso;
* minimização de dados;
* proteção contra enumeração;
* monitoramento quando aplicável.

"Pública" não significa "sem controles".

---

# 11. APIs Privadas

APIs privadas deverão exigir identidade e autorização adequadas.

Não deverão utilizar apenas a existência de um token como autorização completa.

---

# 12. Autenticação

A autenticação deverá seguir o GAF.

A API deverá identificar de forma confiável:

```text
Quem está chamando?
```

Dependendo da arquitetura, isso poderá ocorrer por:

* sessão;
* token;
* credencial de integração;
* mecanismo futuro aprovado.

O GSF-07 não define mecanismo paralelo ao GAF.

---

# 13. Autorização

Após autenticar, a API deverá avaliar:

```text
O chamador pode executar esta operação?
```

A resposta deverá considerar:

* permissão;
* tenant;
* recurso;
* operação;
* regra de negócio.

---

# 14. Multi-Tenant

Toda API que manipule dados organizacionais deverá validar tenant.

Fluxo:

```text
Identidade
    ↓
Tenant autorizado
    ↓
Permissão
    ↓
Objeto do tenant
    ↓
Resposta
```

Não deverá ser possível mudar o tenant apenas alterando um ID.

---

# 15. Identidade da Requisição

Cada requisição autenticada deverá estar associada a uma identidade conhecida.

Essa identidade deverá ser utilizável em:

* autorização;
* auditoria;
* rate limiting;
* investigação.

---

# 16. Escopo Organizacional

Uma API não deverá retornar dados de organização diferente da autorizada.

Exemplo:

```text
Usuário da Igreja A
        ↓
GET /api/membros/100/
```

Se o membro 100 pertencer à Igreja B, o acesso deverá ser negado.

---

# 17. Controle por Recurso

Autorização por endpoint poderá ser insuficiente.

Exemplo:

```text
Pode acessar /api/membros/
        ↓
não significa
        ↓
Pode acessar qualquer membro
```

O recurso concreto deverá ser validado.

---

# 18. Controle por Operação

Operações diferentes poderão exigir permissões distintas.

```text
GET
→ visualizar

POST
→ criar

PATCH
→ alterar

DELETE
→ excluir
```

Não assumir que uma permissão cobre todas.

---

# 19. Permissões

Permissões deverão utilizar os padrões oficiais do GereIgreja.

Exemplos conceituais:

```text
view
add
change
delete
export
manage
```

Permissões administrativas deverão possuir escopo adequado.

---

# 20. Endpoints

Endpoints deverão possuir responsabilidade clara.

Evitar endpoints genéricos excessivamente poderosos.

Exemplo inadequado:

```text
/api/execute/
```

recebendo uma operação arbitrária.

Preferir contratos explícitos.

---

# 21. Métodos HTTP

Métodos HTTP deverão refletir corretamente a operação.

Isso melhora:

* previsibilidade;
* controle;
* monitoramento;
* idempotência;
* segurança.

---

# 22. GET

GET deverá ser utilizado para leitura.

Não deverá executar alterações de estado.

Exemplo inadequado:

```text
GET /api/excluir/10/
```

---

# 23. POST

POST poderá ser utilizado para criação ou operações não idempotentes.

Deverá aplicar:

* validação;
* autorização;
* tenant;
* proteção contra abuso.

---

# 24. PUT e PATCH

Atualizações deverão validar:

* objeto;
* tenant;
* campos permitidos;
* permissões;
* regra de negócio.

Mass assignment indevido deverá ser evitado.

---

# 25. DELETE

DELETE deverá exigir autorização compatível com o impacto.

Em recursos críticos, a operação poderá ser substituída por inativação ou outro fluxo conforme o domínio.

---

# 26. Idempotência

Operações sujeitas a repetição deverão avaliar idempotência.

Especial atenção a:

* financeiro;
* webhooks;
* integrações;
* envio de comunicação;
* tasks.

Uma requisição repetida não deverá criar efeitos duplicados quando o contrato exigir idempotência.

---

# 27. Validação de Entrada

Toda entrada deverá ser validada.

Isso inclui:

* tipo;
* formato;
* tamanho;
* intervalo;
* enumeração;
* relacionamentos;
* tenant;
* domínio.

---

# 28. Parâmetros de URL

Parâmetros em URL deverão ser tratados como não confiáveis.

Exemplo:

```text
/api/igrejas/10/membros/20/
```

Todos os IDs deverão ser validados.

---

# 29. Query Strings

Filtros deverão atuar apenas sobre o universo já autorizado.

Exemplo:

```text
?congregacao=5
```

não deverá permitir acesso a congregação de outro tenant.

---

# 30. Payloads JSON

Payloads deverão aceitar somente campos previstos.

Evitar comportamento como:

```text
receber JSON
    ↓
atribuir tudo ao model
```

Campos administrativos não deverão ser alteráveis sem autorização explícita.

---

# 31. Headers

Headers também são entradas.

Não confiar automaticamente em:

* tenant;
* user;
* role;
* permission;
* IP encaminhado;
* origem.

A infraestrutura deverá definir quais headers podem ser confiáveis.

---

# 32. IDs e Referências

IDs não são segredos e não representam autorização.

Exemplo:

```text
Conhecer o ID 100
≠
poder acessar o objeto 100
```

---

# 33. Serialização

Serialização deverá ser explícita.

Evitar expor todos os campos de um model por padrão.

---

# 34. Minimização de Dados

A resposta deverá conter somente os dados necessários à finalidade.

Exemplo:

```text
lista de membros
```

não precisa necessariamente retornar:

* dados financeiros;
* informações administrativas;
* metadados internos;
* campos de auditoria.

---

# 35. Campos Sensíveis

Campos sensíveis deverão ser excluídos da resposta salvo necessidade e autorização.

Nunca retornar:

* password hashes;
* secrets;
* tokens;
* credenciais;
* chaves privadas.

---

# 36. Respostas

Respostas deverão possuir estrutura consistente.

A resposta não deverá revelar detalhes internos desnecessários.

---

# 37. Status HTTP

Status HTTP deverão ser utilizados de forma coerente.

Exemplos conceituais:

```text
200
→ sucesso

201
→ criação

400
→ entrada inválida

401
→ autenticação necessária ou inválida

403
→ acesso negado

404
→ recurso não encontrado ou não disponível no escopo

429
→ limite excedido

500
→ erro interno
```

O uso final deverá respeitar o contrato real da API.

---

# 38. Mensagens de Erro

Mensagens não deverão revelar:

* stack trace;
* SQL;
* model interno;
* secret;
* paths;
* configuração.

---

# 39. Enumeração

Respostas não deverão facilitar descoberta indevida de:

* usuários;
* e-mails;
* tenants;
* registros;
* identificadores.

---

# 40. IDOR

IDOR é risco crítico.

Exemplo:

```text
GET /api/membros/100/
```

alterado para:

```text
GET /api/membros/101/
```

não deverá revelar objeto não autorizado.

---

# 41. Paginação

Paginação deverá ocorrer após a aplicação dos filtros de autorização e tenant.

Fluxo correto:

```text
Query autorizada
      ↓
Filtro
      ↓
Paginação
```

Nunca paginar dados globais para depois esconder registros.

---

# 42. Filtros

Filtros deverão reduzir o conjunto autorizado.

Não deverão ampliar acesso.

---

# 43. Ordenação

Ordenação deverá aceitar apenas campos permitidos.

Evitar uso indiscriminado de valores recebidos do cliente em construções de query.

---

# 44. Busca

Busca deverá respeitar:

* tenant;
* autorização;
* campos permitidos;
* minimização.

Buscas não deverão retornar recursos invisíveis ao usuário.

---

# 45. Exportações por API

Exports deverão possuir autorização compatível com o impacto.

Devem validar:

* tenant;
* volume;
* campos;
* classificação;
* auditoria.

---

# 46. Uploads por API

Uploads deverão seguir as regras do GSF-06.

Validar:

* tamanho;
* tipo;
* tenant;
* finalidade;
* autorização.

---

# 47. Downloads por API

Downloads de arquivos privados deverão exigir autorização.

URL conhecida não deverá significar acesso permitido.

---

# 48. Rate Limiting

Rate limiting deverá ser considerado em endpoints sujeitos a abuso.

Exemplos:

* autenticação;
* recuperação;
* busca pública;
* APIs externas;
* envio;
* exportação;
* integrações.

---

# 49. Proteção contra Abuso

Além de rate limiting, poderão ser necessários:

* limites de volume;
* limites por usuário;
* limites por tenant;
* quotas;
* bloqueios temporários;
* monitoramento.

---

# 50. Brute Force

Endpoints relacionados a autenticação ou recuperação deverão possuir controles compatíveis com o GAF.

---

# 51. Replay

Operações críticas deverão considerar risco de repetição da mesma requisição.

Isso é especialmente importante em:

* financeiro;
* pagamentos;
* webhooks;
* automações.

---

# 52. Webhooks

Webhooks recebidos deverão ser tratados como entrada externa.

Deverão validar:

* origem;
* assinatura quando disponível;
* payload;
* timestamp quando aplicável;
* idempotência;
* tenant;
* evento.

---

# 53. Assinatura de Webhooks

Quando o provedor oferecer assinatura criptográfica, ela deverá ser validada.

Não confiar somente em IP ou URL.

---

# 54. Integrações Externas

Integrações deverão possuir contrato claro.

Devem definir:

* dados enviados;
* dados recebidos;
* autenticação;
* autorização;
* tenant;
* logging;
* erro;
* timeout;
* revogação.

---

# 55. Tokens e Credenciais

Tokens deverão possuir escopo mínimo.

Quando possível, evitar tokens com acesso irrestrito a toda a plataforma.

---

# 56. API Keys

API Keys deverão ser tratadas como segredo.

Não deverão ser:

* commitadas;
* expostas no frontend;
* registradas integralmente em logs;
* reutilizadas desnecessariamente.

---

# 57. Rotação de Credenciais

Credenciais de integração deverão possuir estratégia de rotação quando aplicável.

---

# 58. Revogação

Deverá ser possível remover acesso de integração comprometida ou obsoleta.

---

# 59. Expiração

Tokens temporários deverão possuir expiração quando essa característica for compatível com o mecanismo adotado.

---

# 60. Segredos

Segredos relacionados às APIs deverão seguir GSF-09.

---

# 61. CORS

CORS deverá ser configurado restritivamente.

Não habilitar:

```text
*
```

sem necessidade e análise.

CORS não substitui autenticação ou autorização.

---

# 62. CSRF

APIs baseadas em sessão e cookies poderão continuar sujeitas a CSRF.

O mecanismo deverá considerar a arquitetura efetiva.

Não desabilitar CSRF indiscriminadamente apenas porque o endpoint retorna JSON.

---

# 63. HTTPS

APIs em produção deverão utilizar HTTPS.

Credenciais não deverão trafegar em texto claro.

---

# 64. Versionamento

APIs deverão possuir estratégia de versionamento quando mudanças de contrato puderem afetar consumidores.

Exemplo conceitual:

```text
/api/v1/
```

A forma real deverá seguir a arquitetura da API do GereIgreja.

---

# 65. Compatibilidade

Mudanças deverão avaliar consumidores existentes.

Especial atenção a:

* aplicações externas;
* automações;
* integrações;
* mobile futuro.

---

# 66. Depreciação

Endpoints obsoletos deverão ser depreciados antes da remoção quando existirem consumidores ativos.

---

# 67. Logs

Logs de API poderão registrar:

* endpoint;
* identidade;
* tenant;
* status;
* duração;
* evento;
* erro técnico adequado.

Não registrar indiscriminadamente payloads confidenciais completos.

---

# 68. Auditoria

Operações críticas por API deverão possuir a mesma auditabilidade das operações realizadas pela interface.

Exemplo:

```text
API
ou
Tela
```

não deverá alterar a necessidade de auditoria.

---

# 69. Monitoramento

APIs deverão ser monitoradas quanto a:

* erros;
* latência;
* volume;
* rate limiting;
* tentativas negadas;
* abuso;
* indisponibilidade.

---

# 70. Dados Confidenciais

Respostas contendo dados confidenciais deverão possuir controle reforçado.

Dados financeiros, pessoais e ministeriais seguem o GSF-02.

---

# 71. Financeiro

APIs financeiras deverão proteger:

* lançamentos;
* receitas;
* despesas;
* saldos;
* estornos;
* relatórios.

Controles prioritários:

```text
autorização
+
tenant
+
idempotência
+
auditoria
```

---

# 72. Secretaria

APIs da Secretaria deverão minimizar dados pessoais retornados.

Uma listagem resumida não deverá retornar o cadastro completo sem necessidade.

---

# 73. Comunicação

APIs relacionadas a comunicação deverão proteger:

* destinatários;
* conteúdo;
* agendamentos;
* envios;
* integrações.

Operações de envio poderão exigir rate limiting e idempotência.

---

# 74. Eventos

Conteúdo público e administrativo deverá ser diferenciado.

Uma API pública de eventos não deverá expor dados administrativos internos.

---

# 75. Escola Bíblica

Dados de turmas, alunos, professores e frequência deverão respeitar tenant e permissões.

---

# 76. Patrimônio

Endpoints patrimoniais deverão respeitar isolamento e autorização.

---

# 77. Administração

APIs administrativas deverão possuir proteção elevada.

Exemplos:

* usuários;
* grupos;
* permissões;
* configurações;
* integrações.

---

# 78. Portal Público

APIs públicas utilizadas pelo portal deverão expor somente conteúdo realmente público.

Não reutilizar diretamente endpoints administrativos sem uma camada adequada de minimização e autorização.

---

# 79. Tasks e APIs

Uma API poderá disparar processamento assíncrono.

Nesse caso, deverá registrar e preservar:

* tenant;
* identidade;
* recurso;
* operação;
* parâmetros validados.

---

# 80. Cache

Cache de respostas deverá considerar:

* tenant;
* usuário;
* autorização;
* parâmetros;
* dados sensíveis.

Nunca reutilizar resposta privada entre tenants.

---

# 81. Performance e Segurança

Otimizações não deverão remover controles.

Exemplo inadequado:

```text
Para melhorar performance
→ remover filtro de tenant
```

Performance deverá ser otimizada sem quebrar a fronteira de segurança.

---

# 82. Tratamento de Exceções

Exceções internas deverão ser convertidas em respostas seguras.

O cliente não precisa conhecer o traceback.

---

# 83. Dependências

Frameworks e bibliotecas utilizados para APIs deverão ser mantidos conforme política de vulnerabilidades.

---

# 84. Testes

APIs deverão possuir testes de segurança automatizados quando aplicável.

---

# 85. Testes de Autenticação

Testar:

* sem autenticação;
* credencial inválida;
* credencial expirada;
* identidade inativa;
* credencial revogada.

---

# 86. Testes de Autorização

Testar:

* usuário autorizado;
* usuário sem permissão;
* usuário com permissão parcial;
* endpoint administrativo;
* operação diferente.

---

# 87. Testes Multi-Tenant

Padrão mínimo:

```text
Usuário A
Tenant A
Objeto A

Usuário B
Tenant B
Objeto B
```

Testar:

```text
A → A = permitido
A → B = negado

B → B = permitido
B → A = negado
```

---

# 88. Testes de Entrada

Testar:

* JSON inválido;
* campo ausente;
* tipo incorreto;
* valor fora de faixa;
* ID de outro tenant;
* campo extra;
* tamanho excessivo.

---

# 89. Testes de Resposta

Verificar:

* campos sensíveis ausentes;
* campos mínimos;
* status correto;
* ausência de traceback;
* ausência de dados de outro tenant.

---

# 90. Testes de Rate Limiting

Quando existir rate limiting, testar:

* limite;
* janela;
* resposta;
* isolamento por usuário ou tenant conforme implementação.

---

# 91. Testes de Webhooks

Testar:

* assinatura inválida;
* evento duplicado;
* payload inválido;
* tenant incorreto;
* evento desconhecido.

---

# 92. Testes de Regressão

Toda vulnerabilidade corrigida deverá, quando tecnicamente possível, produzir teste que impeça sua reintrodução.

---

# 93. Evidências Arquiteturais

## EA-GSF-API-001

O GSF estabelece autenticação, autorização, versionamento, validação, rate limiting e auditoria como requisitos das APIs.

## EA-GSF-API-002

O GereIgreja possui arquitetura específica de APIs documentada em GEA-06.

## EA-GSF-API-003

O GereIgreja possui arquitetura de segurança documentada em GEA-07.

## EA-GSF-API-004

O GereIgreja possui arquitetura multi-tenant documentada em GEA-08.

## EA-GSF-API-005

O backend possui documentação de Views, Services, Selectors e Permissions.

## EA-GSF-API-006

O backend possui documentação de Validators.

## EA-GSF-API-007

O backend possui documentação de Tasks, Cache, Logging e Exceptions.

## EA-GSF-API-008

O GAF constitui o framework oficial de autenticação.

## EA-GSF-API-009

O GSF classifica dados pessoais, financeiros e ministeriais como Confidenciais.

## EA-GSF-API-010

O projeto possui pasta `docs/api/`, destinada à documentação especializada de APIs.

---

# 94. Especificações Oficiais

## GSF-API-001

Toda API privada deverá possuir autenticação adequada.

## GSF-API-002

Autenticação não deverá substituir autorização.

## GSF-API-003

Toda API multi-tenant deverá validar o tenant no backend.

## GSF-API-004

IDs não deverão ser utilizados como prova de autorização.

## GSF-API-005

Toda operação deverá validar o recurso correspondente.

## GSF-API-006

Métodos HTTP deverão refletir a semântica da operação.

## GSF-API-007

GET não deverá alterar estado.

## GSF-API-008

Payloads deverão aceitar somente campos permitidos.

## GSF-API-009

Serialização deverá minimizar a exposição de dados.

## GSF-API-010

Campos confidenciais deverão ser excluídos das respostas quando não forem necessários.

## GSF-API-011

Filtros deverão operar sobre querysets já autorizados.

## GSF-API-012

Paginação deverá ocorrer depois do filtro de autorização e tenant.

## GSF-API-013

Exportações por API deverão possuir autorização compatível com seu impacto.

## GSF-API-014

Uploads por API deverão ser validados.

## GSF-API-015

Downloads privados deverão possuir autorização.

## GSF-API-016

Rate limiting deverá ser avaliado em endpoints sujeitos a abuso.

## GSF-API-017

Webhooks deverão validar origem e integridade quando o provedor oferecer mecanismos adequados.

## GSF-API-018

Webhooks deverão possuir proteção contra duplicidade quando necessário.

## GSF-API-019

API Keys deverão ser tratadas como segredos.

## GSF-API-020

Credenciais deverão ser revogáveis.

## GSF-API-021

CORS não deverá ser utilizado como mecanismo de autorização.

## GSF-API-022

HTTPS deverá ser obrigatório para APIs de produção.

## GSF-API-023

CSRF deverá ser considerado em APIs autenticadas por sessão.

## GSF-API-024

Mudanças de contrato deverão avaliar compatibilidade.

## GSF-API-025

APIs críticas deverão possuir logging e auditoria adequados.

## GSF-API-026

Payloads confidenciais não deverão ser registrados integralmente em logs.

## GSF-API-027

Cache de API deverá preservar tenant e autorização.

## GSF-API-028

Operações financeiras por API deverão avaliar idempotência.

## GSF-API-029

Testes multi-tenant deverão fazer parte de APIs organizacionais.

## GSF-API-030

Correções de vulnerabilidades deverão possuir teste de regressão quando tecnicamente possível.

---

# 95. Anti-Padrões

São considerados anti-padrões:

```text
Token válido
=
acesso a qualquer recurso
```

---

```text
API interna
=
API confiável
```

---

```text
/api/membros/<id>/
```

sem tenant.

---

```text
Serializer
=
todos os campos do model
```

---

```text
CORS permitido
=
usuário autorizado
```

---

```text
GET /api/excluir/10/
```

---

```text
API Key no JavaScript do navegador
```

---

```text
Webhook recebido
=
evento legítimo
```

sem validação.

---

```text
Payload recebido
=
estrutura confiável
```

---

```text
Cache:
api:membros
```

para dados de tenant.

---

```text
Logar token completo
para facilitar debug
```

---

```text
Endpoint autenticado
=
não precisa rate limiting
```

---

```text
API de Portal Público
reutiliza resposta administrativa completa
```

---

# 96. Checklist

## Arquitetura

* [ ] finalidade da API definida;
* [ ] tipo da API definido;
* [ ] consumidores definidos;
* [ ] dados classificados;
* [ ] versionamento avaliado.

## Autenticação

* [ ] mecanismo oficial;
* [ ] identidade válida;
* [ ] credencial revogável;
* [ ] expiração avaliada.

## Autorização

* [ ] endpoint;
* [ ] operação;
* [ ] recurso;
* [ ] permissão;
* [ ] tenant.

## Entrada

* [ ] URL validada;
* [ ] query string validada;
* [ ] JSON validado;
* [ ] headers revisados;
* [ ] IDs validados;
* [ ] campos extras rejeitados ou ignorados de forma segura.

## Saída

* [ ] campos mínimos;
* [ ] sem credenciais;
* [ ] sem secrets;
* [ ] sem dados de outro tenant;
* [ ] erros seguros.

## Multi-Tenant

* [ ] queryset restrito;
* [ ] detalhe restrito;
* [ ] criação restrita;
* [ ] alteração restrita;
* [ ] exclusão restrita;
* [ ] filtros restritos.

## Rate Limiting

* [ ] necessidade avaliada;
* [ ] limite definido quando aplicável;
* [ ] usuário ou tenant considerado;
* [ ] monitoramento disponível.

## Webhooks

* [ ] assinatura validada quando disponível;
* [ ] idempotência;
* [ ] evento validado;
* [ ] tenant validado;
* [ ] replay considerado.

## Credenciais

* [ ] segredo fora do código;
* [ ] API Key protegida;
* [ ] rotação prevista;
* [ ] revogação prevista;
* [ ] logging seguro.

## Transporte

* [ ] HTTPS;
* [ ] CORS revisado;
* [ ] CSRF avaliado;
* [ ] cookies revisados quando aplicável.

## Auditoria

* [ ] identidade registrada;
* [ ] tenant registrado;
* [ ] operação registrada;
* [ ] eventos críticos rastreáveis.

## Testes

* [ ] sem autenticação;
* [ ] credencial inválida;
* [ ] sem permissão;
* [ ] outro tenant;
* [ ] IDOR;
* [ ] campo sensível;
* [ ] payload inválido;
* [ ] rate limiting;
* [ ] webhook inválido;
* [ ] regressão.

---

# 97. Documentos Relacionados

## Frameworks

* GSF — GereIgreja Security Framework
* GAF — GereIgreja Authentication Framework
* GQF — GereIgreja Quality Framework
* GOC — GereIgreja Operations Center

## Segurança

* GSF-01 — Fundamentos de Segurança
* GSF-02 — Classificação e Proteção da Informação
* GSF-03 — Gestão de Identidade
* GSF-04 — Autorização e Controle de Acesso
* GSF-05 — Segurança Multi-Tenant
* GSF-06 — Segurança da Aplicação
* GSF-08 — Segurança de Dados e Privacidade
* GSF-09 — Segurança de Infraestrutura e Segredos
* GSF-10 — Logging, Monitoramento e Auditoria
* GSF-12 — Gestão de Vulnerabilidades
* GSF-13 — Gestão de Incidentes de Segurança

## Arquitetura

* GEA-06 — Arquitetura das APIs
* GEA-07 — Arquitetura da Segurança
* GEA-08 — Arquitetura Multi-Tenant

## Backend

* Views
* Services
* Selectors
* Validators
* Permissions
* Tasks
* Cache
* Logging
* Exceptions
* Testing

## API

* `docs/api/README.md`

---

# 98. Princípios Finais

Uma API do GereIgreja deverá ser segura mesmo quando o consumidor:

```text
altera IDs
+
altera tenant
+
altera payload
+
chama endpoint diretamente
+
repete requests
+
ignora a interface
```

A API deverá continuar aplicando:

```text
Identidade
    ↓
Autorização
    ↓
Tenant
    ↓
Validação
    ↓
Regra de negócio
    ↓
Minimização
    ↓
Auditoria
```

O princípio central é:

```text
Autenticar
não é suficiente.

Autorizar
não é suficiente.

Autorizar sem tenant
não é suficiente.

Autorizar e validar
sem limitar a resposta
não é suficiente.
```

A segurança efetiva deverá combinar todos os controles.

APIs internas deverão ser protegidas.

APIs externas deverão possuir contratos claros.

APIs públicas deverão minimizar dados.

Webhooks deverão ser validados.

Integrações deverão utilizar credenciais específicas.

Financeiro deverá considerar idempotência e auditoria.

Secretaria deverá minimizar dados pessoais.

Comunicação deverá limitar abuso e envios repetidos.

Toda API multi-tenant deverá impedir acesso horizontal.

A regra final é:

```text
Uma API somente deverá retornar
o que aquele chamador
pode acessar,
naquele tenant,
para aquela operação,
naquele momento.
```

---

# 99. Status do Documento

**Pasta**

`docs/seguranca/`

**Arquivo**

`07-Seguranca-das-APIs.md`

**Documento**

`GSF-07`

**Código**

`GSF-API-SECURITY`

**Framework**

`GSF — GereIgreja Security Framework`

**Versão**

`1.0`

**Status**

`OFICIAL`

**Responsável**

`Equipe de Engenharia`

**Última atualização**

`Agosto de 2026`

**Próximo documento**

`08-Seguranca-de-Dados-e-Privacidade.md`

**Código do próximo documento**

`GSF-08`

```
```
