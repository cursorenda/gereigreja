# APIs — Contratos, Segurança e Ciclo de Vida

APIs  
↓  
Como integrações e consumidores interagem com o GereIgreja por contratos estáveis e governados.

Esta pasta reúne a documentação canônica das APIs do GereIgreja.

Ela define arquitetura, contratos, autenticação, autorização, tenant, payloads, responses, filtros, versionamento, integrações, segurança, testes, observabilidade e ciclo de vida das APIs.

## Finalidade da pasta

- documentar a arquitetura das APIs;
- definir padrões de endpoints;
- registrar autenticação, autorização e isolamento multi-tenant;
- padronizar requests, payloads e validação;
- padronizar responses, serialização e erros;
- definir filtros, busca, ordenação e paginação;
- estabelecer versionamento e compatibilidade;
- documentar webhooks e integrações;
- definir idempotência e rate limiting;
- consolidar controles de segurança e privacidade aplicáveis às APIs;
- documentar logging, monitoramento e auditoria;
- definir estratégia de testes;
- estabelecer depreciação e ciclo de vida;
- manter mapa e índice da família.

## Inventário canônico

A família atual está estruturada em 14 documentos numerados:

```text
01-Arquitetura-das-APIs.md
02-Padroes-de-Endpoints.md
03-Autenticacao-Autorizacao-e-Tenant.md
04-Requests-Payloads-e-Validacao.md
05-Responses-Serializacao-e-Erros.md
06-Filtros-Busca-Ordenacao-e-Paginacao.md
07-Versionamento-e-Compatibilidade.md
08-Webhooks-e-Integracoes.md
09-Idempotencia-e-Rate-Limiting.md
10-Seguranca-e-Privacidade.md
11-Logging-Monitoramento-e-Auditoria.md
12-Testes-de-APIs.md
13-Depreciacao-e-Ciclo-de-Vida.md
14-Mapa-e-Indice-das-APIs.md
```

O detalhamento da família deve ser consultado em:

```text
14-Mapa-e-Indice-das-APIs.md
```

O README não deve duplicar integralmente esse índice.

## Fronteira com Backend

`docs/backend/` documenta implementação interna da aplicação.

`docs/api/` documenta o contrato exposto para consumidores e integrações.

A divisão é:

```text
backend/
→ como o sistema implementa

api/
→ como consumidores interagem
```

Detalhes internos podem ser referenciados, mas não devem transformar a API em documentação de implementação.

## Fronteira com Segurança

`docs/seguranca/` e os frameworks GAF/GSF possuem autoridade normativa transversal.

A família API aplica esses princípios ao contexto de endpoints, tokens, autenticação, autorização, tenant e privacidade.

Portanto:

```text
seguranca/frameworks
→ política geral

api/
→ aplicação da política na superfície de API
```

`10-Seguranca-e-Privacidade.md` não deve redefinir controles globais de segurança.

## Fronteira com Apps

Os documentos de `docs/apps/` definem regras funcionais dos domínios.

A API expõe ou operacionaliza essas regras.

Quando houver conflito:

```text
app canônico
→ autoridade sobre regra funcional

api/
→ autoridade sobre contrato de integração
```

Não duplicar regra de negócio complexa dentro do contrato da API.

## Multi-tenancy

Toda API que opere dados vinculados a igreja deve respeitar o contexto multi-tenant.

A documentação deve deixar claro:

- como a igreja ativa é resolvida;
- quais recursos dependem de tenant;
- como acessos cruzados são prevenidos;
- como permissões são aplicadas;
- quais operações são globais, quando existirem.

Nunca assumir que autenticação, por si só, garante isolamento de tenant.

## Autenticação e autorização

`03-Autenticacao-Autorizacao-e-Tenant.md` concentra o comportamento esperado dessa camada para APIs.

A documentação deve distinguir:

```text
autenticação
→ quem é o consumidor

autorização
→ o que ele pode fazer

tenant
→ sobre quais dados ele pode operar
```

Esses três conceitos não devem ser tratados como equivalentes.

## Requests e validação

`04-Requests-Payloads-e-Validacao.md` deve definir:

- formato esperado;
- tipos;
- campos obrigatórios;
- validações;
- erros de entrada;
- comportamento diante de campos desconhecidos;
- limites aplicáveis.

O contrato documentado deve refletir a implementação real.

## Responses e erros

`05-Responses-Serializacao-e-Erros.md` deve estabelecer consistência para:

- estrutura de responses;
- códigos HTTP;
- serialização;
- mensagens de erro;
- identificadores de erro quando aplicáveis;
- respostas de autorização;
- validação;
- recursos inexistentes.

Erros não devem vazar informações sensíveis ou detalhes internos desnecessários.

## Filtros, busca, ordenação e paginação

`06-Filtros-Busca-Ordenacao-e-Paginacao.md` define convenções para consultas de coleções.

Toda API que suporte esses recursos deve documentar explicitamente:

- parâmetros aceitos;
- comportamento padrão;
- limites;
- campos ordenáveis;
- filtros permitidos;
- formato de paginação.

## Versionamento e compatibilidade

`07-Versionamento-e-Compatibilidade.md` deve orientar mudanças sem quebrar consumidores desnecessariamente.

Alterações incompatíveis precisam ser tratadas explicitamente.

Não usar mudança silenciosa de contrato como substituto de versionamento.

## Webhooks e integrações

`08-Webhooks-e-Integracoes.md` documenta contratos de integração assíncrona ou externa.

Quando aplicável, registrar:

- evento;
- payload;
- autenticação;
- assinatura;
- reenvio;
- idempotência;
- timeout;
- erros;
- observabilidade.

Runbooks operacionais de uma integração pertencem a `docs/operacoes/` quando forem procedimentos de suporte.

## Idempotência e rate limiting

`09-Idempotencia-e-Rate-Limiting.md` deve ser aplicado quando operações puderem:

- ser repetidas;
- gerar efeitos duplicados;
- sofrer abuso;
- impactar capacidade da plataforma.

Não adicionar rate limiting ou idempotência apenas por convenção documental; sua existência deve corresponder à implementação ou plano explicitamente marcado como tal.

## Segurança e privacidade

`10-Seguranca-e-Privacidade.md` deve tratar do recorte específico de API:

- exposição mínima de dados;
- autenticação segura;
- autorização;
- tenant;
- dados pessoais;
- logs;
- tokens;
- transporte seguro;
- prevenção de enumeração;
- limitação de abuso.

LGPD e políticas transversais continuam sendo governadas pela documentação de Segurança.

## Logging, monitoramento e auditoria

`11-Logging-Monitoramento-e-Auditoria.md` deve permitir rastrear comportamento da API sem registrar segredos ou dados sensíveis desnecessários.

A família API pode definir quais sinais devem existir, enquanto infraestrutura e operações definem como esses sinais são coletados e utilizados em produção.

## Testes de APIs

`12-Testes-de-APIs.md` define o recorte específico de validação de contratos.

Ele deve permanecer alinhado com:

```text
docs/frameworks/04-GQF-...
docs/qualidade/
docs/desenvolvimento/
```

Não deve criar uma política paralela de qualidade.

## Depreciação e ciclo de vida

`13-Depreciacao-e-Ciclo-de-Vida.md` deve definir como endpoints e versões são:

```text
introduzidos
mantidos
depreciados
retirados
```

Depreciação deve ser comunicada e rastreável.

A remoção de um endpoint sem janela de transição deve ser exceção justificada, não padrão.

## Mapa e índice

`14-Mapa-e-Indice-das-APIs.md` encerra o baseline atual da família.

Ele existe justamente para evitar que o README precise listar detalhes operacionais de todos os documentos.

## Regra para criar documento 15+

A sequência atual termina em `14`.

Isso não significa que `15` deva ser criado.

Antes de qualquer novo documento:

1. demonstrar uma lacuna real;
2. verificar se o assunto cabe em `01` a `14`;
3. consultar `14-Mapa-e-Indice-das-APIs.md`;
4. verificar sobreposição com Backend, Segurança, Infraestrutura, Operações e Qualidade;
5. preferir evoluir documento existente;
6. criar novo arquivo somente se houver um tema autônomo e duradouro;
7. atualizar o mapa da família.

## Estado da família

Classificação atual:

```text
Status: CANÔNICA
Baseline: 01–14
Cobertura: ALTA
Expansão automática: NÃO
Prioridade: manutenção, aderência ao código e contratos reais
```

A família está documentalmente fechada em seu baseline atual.

Isso não impede evolução dos documentos existentes.

## Princípio de manutenção

Documentação de API é contrato.

**Se o comportamento real diverge do documento, existe um defeito — no código, na documentação ou em ambos.**

A prioridade deve ser preservar consistência, compatibilidade e segurança, não aumentar a quantidade de arquivos.
