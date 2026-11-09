# Backend — Padrões de Engenharia e Implementação

Backend  
↓  
Como o GereIgreja deve ser construído internamente.

Esta pasta reúne a documentação canônica dos padrões transversais de implementação do backend.

Ela define como estruturar Apps, Models, Services, Selectors, Managers, Views, Forms, Validators, Permissions, Middlewares, Signals, Tasks, Cache, Logging, Exceptions, Testing, Performance e padrões gerais de código.

## Finalidade da pasta

- definir padrões transversais de implementação;
- padronizar responsabilidades entre camadas;
- reduzir acoplamento e duplicação;
- orientar novas implementações;
- registrar convenções técnicas reutilizáveis;
- preservar coerência entre módulos;
- servir como referência prática de engenharia backend.

## O que pertence aqui

Documentos que respondem principalmente:

```text
Como esta camada deve ser implementada no GereIgreja?
```

Exemplos:

- estrutura do projeto;
- Core da plataforma;
- arquitetura dos Apps;
- Models;
- Services;
- Selectors;
- Managers;
- Views;
- Forms;
- Validators;
- Permissions;
- Middlewares;
- Signals;
- Tasks;
- Cache;
- Logging;
- Exceptions;
- testes;
- performance;
- padrões de código.

## O que não pertence aqui

Não utilizar esta pasta para:

- regras funcionais exclusivas de um domínio;
- manuais de usuário;
- histórico de release;
- runbooks;
- procedimentos de deploy;
- políticas gerais de segurança;
- decisões arquiteturais isoladas que justifiquem ADR;
- inventários detalhados de uma implementação específica.

Esses conteúdos possuem famílias próprias.

## Inventário atual

A família já possui pelo menos o baseline abaixo:

```text
01-Estrutura-do-Projeto.md
02-Core-da-Plataforma.md
03-Arquitetura-dos-Apps.md
04-Models.md
05-Services.md
06-Selectors.md
07-Managers.md
08-Views.md
09-Forms.md
10-Validators.md
11-Permissions.md
12-Middlewares.md
13-Signals.md
14-Tasks.md
15-Cache.md
16-Logging.md
17-Exceptions.md
18-Testing.md
19-Performance.md
20-Code-Standards.md
```

O README anterior listava apenas `01` a `09`, embora a família já tenha evoluído até `20`.

Portanto, o índice precisa refletir a estrutura real ou apontar para um mapa mais completo, caso venha a existir.

## Relação com Apps

A fronteira principal é:

```text
backend/
→ como implementar

apps/
→ o que o domínio faz
```

Exemplo:

```text
backend/04-Models.md
→ padrão de modelagem

apps/02-Secretaria.md
→ regras funcionais da Secretaria
```

O Backend não deve absorver regras de negócio específicas apenas porque elas são implementadas em Python.

## Relação com Arquitetura

`docs/arquitetura/` documenta estrutura sistêmica e relações entre partes.

`docs/backend/` documenta padrões concretos de implementação.

A divisão é:

```text
arquitetura/
→ como o sistema é organizado

backend/
→ como construir dentro dessa organização
```

Decisões arquiteturais importantes podem ser registradas em `docs/adr/` e depois refletidas aqui.

## Relação com Governança

A família Backend hoje absorve grande parte dos antigos padrões técnicos existentes em `docs/governanca/`.

Correspondências evidentes:

```text
governanca/05-Padroes-de-Models.md
→ backend/04-Models.md

governanca/06-Padroes-de-Views.md
→ backend/08-Views.md

governanca/09-Padroes-de-Forms.md
→ backend/09-Forms.md
```

Esses documentos antigos de Governança devem ser comparados com as versões canônicas de Backend.

Se o conteúdo já estiver coberto:

```text
consolidar
↓
atualizar referências
↓
remover ou arquivar o legado
```

Não manter duas normas concorrentes.

## Django Admin

O antigo:

```text
governanca/04-Padroes-do-Django-Admin.md
```

não possui, pelo inventário atual, um documento backend de mesmo nome.

Isso não significa que deva permanecer indefinidamente em Governança.

Antes de criar um novo documento no Backend:

1. verificar se o conteúdo já está distribuído entre estrutura de Apps, Views, Forms, Permissions ou Code Standards;
2. identificar se há regra exclusiva e ainda válida;
3. somente criar um documento específico de Django Admin se houver uma lacuna comprovada.

Não criar novo documento apenas para preservar simetria histórica.

## URLs

O antigo:

```text
governanca/08-Padroes-de-URLs.md
```

também não possui correspondência nominal explícita no baseline `01–20`.

Esse conteúdo deve ser comparado principalmente com:

```text
03-Arquitetura-dos-Apps.md
08-Views.md
20-Code-Standards.md
docs/api/
```

Se URLs internas Django não estiverem cobertas de forma suficiente, poderá existir lacuna real.

A decisão deve vir da comparação de conteúdo, não da numeração histórica.

## Models

`04-Models.md` é a referência transversal para modelagem backend.

Ele deve tratar de padrões como:

- responsabilidade do Model;
- constraints;
- integridade;
- relacionamentos;
- timestamps;
- estados;
- soft delete quando aplicável;
- multi-tenancy;
- separação entre regra funcional e persistência.

Regras específicas de entidades continuam nos Apps.

## Services

`05-Services.md` deve concentrar operações de negócio que:

- alteram estado;
- coordenam múltiplos Models;
- encapsulam transações;
- possuem efeitos colaterais;
- não pertencem diretamente a Views ou Forms.

Services não devem virar repositório genérico de funções.

## Selectors

`06-Selectors.md` concentra leitura e consultas reutilizáveis.

A distinção deve permanecer clara:

```text
Selector
→ leitura

Service
→ operação/mutação
```

Queries complexas reutilizadas por múltiplos pontos devem preferencialmente ser extraídas para Selectors quando esse for o padrão vigente.

## Managers

`07-Managers.md` documenta managers e QuerySets quando a lógica pertence naturalmente à camada de persistência.

Evitar duplicar em Manager o que já pertence a Selector ou Service.

## Views

`08-Views.md` deve orientar Views finas.

Em geral, Views devem:

- resolver request;
- validar acesso;
- delegar regra de negócio;
- montar response;
- evitar lógica complexa.

## Forms

`09-Forms.md` define padrões para validação e interação de formulários Django.

Forms não devem assumir responsabilidades de Service apenas por conveniência.

## Validators

`10-Validators.md` concentra validações reutilizáveis e puras quando possível.

Evitar validadores com acesso implícito a contexto global ou efeitos colaterais.

## Permissions

`11-Permissions.md` documenta implementação técnica de permissões no Backend.

Ele deve permanecer alinhado com:

```text
docs/frameworks/02-GAF-GereIgreja-Authentication-Framework.md
docs/seguranca/
```

A divisão é:

```text
GAF/seguranca
→ política

backend/11-Permissions.md
→ implementação
```

## Middlewares

`12-Middlewares.md` deve documentar responsabilidades adequadas para middleware.

Evitar lógica de domínio ou queries pesadas por request sem justificativa.

Contexto multi-tenant, autenticação e observabilidade podem envolver middleware, mas precisam permanecer coerentes com as políticas transversais.

## Signals

`13-Signals.md` deve tratar Signals como mecanismo de integração interna cuidadosamente controlado.

Signals não devem esconder fluxos de negócio importantes quando um Service explícito seria mais rastreável.

## Tasks

`14-Tasks.md` documenta tarefas assíncronas ou programadas do ponto de vista de implementação backend.

A execução operacional dessas tarefas pode possuir documentação complementar em:

```text
docs/automacao/
docs/operacoes/
```

## Cache

`15-Cache.md` deve documentar padrões de cache e invalidação.

Cache nunca deve ser tratado como fonte de verdade.

Toda estratégia deve deixar claro:

- chave;
- escopo;
- tenant;
- TTL;
- invalidação;
- fallback.

## Logging

`16-Logging.md` documenta como o backend registra eventos.

Deve permanecer alinhado com Segurança, Infraestrutura e Operações.

Nunca registrar:

- senhas;
- tokens;
- segredos;
- dados pessoais desnecessários.

## Exceptions

`17-Exceptions.md` define tratamento consistente de exceções.

Erro interno, erro de validação, erro de autorização e erro de domínio não devem ser tratados como equivalentes.

## Testing

`18-Testing.md` documenta práticas de teste do Backend.

Ele deve se alinhar a:

```text
docs/frameworks/04-GQF-...
docs/qualidade/
docs/desenvolvimento/Como-Rodar-Testes.md
```

A divisão recomendada é:

```text
backend/18-Testing.md
→ como escrever testes backend

desenvolvimento/
→ como executar localmente

qualidade/
→ critérios e gates
```

## Performance

`19-Performance.md` registra padrões para consultas, carregamento, cache e eficiência backend.

Otimização deve ser guiada por evidência.

Não adicionar complexidade preventiva sem problema demonstrado.

## Code Standards

`20-Code-Standards.md` funciona como consolidação de padrões gerais de código.

Ele deve evitar repetir profundamente documentos especializados.

Seu papel é definir convenções transversais e apontar para as referências específicas.

## Regra para criar documento 21+

A existência de `20-Code-Standards.md` não implica necessidade de `21`.

Antes de criar qualquer novo documento:

1. demonstrar lacuna real;
2. revisar o baseline `01–20`;
3. verificar se o assunto cabe em documento existente;
4. verificar sobreposição com Arquitetura, API, Segurança, Qualidade e Infraestrutura;
5. preferir evolução antes de criação;
6. atualizar README e INDEX somente quando necessário.

## Estado da família

Classificação atual:

```text
Status: CANÔNICA
Baseline atual: 01–20
Cobertura: ALTA
Sobreposição histórica com governanca/: SIM
Expansão automática: NÃO
Prioridade: consolidação do legado + aderência ao código
```

## Decisão sobre Governança antiga

Os documentos:

```text
04-Padroes-do-Django-Admin.md
05-Padroes-de-Models.md
06-Padroes-de-Views.md
08-Padroes-de-URLs.md
09-Padroes-de-Forms.md
```

não devem continuar sendo considerados fontes normativas principais.

A família Backend é hoje o destino canônico para padrões de implementação.

A ação correta é:

```text
comparar
↓
absorver conteúdo exclusivo ainda válido
↓
corrigir referências
↓
remover/arquivar legado
```

## Princípio de manutenção

Backend documenta **como construir corretamente**.

**Padrão transversal deve existir uma vez, na fonte canônica apropriada.**
