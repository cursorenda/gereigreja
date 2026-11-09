# Arquitetura — Estrutura Sistêmica do GereIgreja

Arquitetura  
↓  
Como as partes da plataforma se organizam, se relacionam e evoluem estruturalmente.

Esta pasta reúne a documentação canônica da arquitetura do GereIgreja.

Ela descreve a visão sistêmica da plataforma, suas camadas, fronteiras, relações entre subsistemas e estruturas transversais como Backend, Frontend, Banco de Dados, APIs, Segurança, Multi-Tenancy e Core.

## Finalidade da pasta

- documentar a arquitetura vigente;
- consolidar a visão sistêmica da plataforma;
- registrar fronteiras entre camadas e domínios;
- documentar relações estruturais entre componentes;
- orientar evolução técnica;
- servir como referência para Backend, Frontend, API, Segurança e Infraestrutura;
- refletir decisões arquiteturais já aceitas.

## O que não pertence aqui

Não utilizar esta pasta para:

- regras funcionais específicas de um módulo;
- padrões detalhados de implementação;
- checklists;
- runbooks;
- procedimentos de deploy;
- decisões arquiteturais históricas isoladas;
- planos futuros não aprovados.

Esses conteúdos pertencem às famílias responsáveis.

## Relação com ADR

A distinção é:

```text
docs/adr/
→ por que uma decisão arquitetural foi tomada

docs/arquitetura/
→ como a arquitetura está organizada hoje
```

Uma decisão importante pode nascer em um ADR e depois ser refletida nesta família.

O README anterior dizia que “toda decisão arquitetural deverá ser registrada nesta pasta”. Essa formulação é ampla demais.

Decisões com contexto, alternativas e consequências devem preferencialmente ser registradas como ADR.

## Inventário atual

A família possui o baseline:

```text
01-GEA-GereIgreja-Engineering-Architecture.md
02-Arquitetura-da-Plataforma.md
03-Arquitetura-do-Backend.md
04-Arquitetura-do-Frontend.md
05-Arquitetura-do-Banco-de-Dados.md
06-Arquitetura-das-APIs.md
07-Arquitetura-da-Seguranca.md
08-Arquitetura-Multi-Tenant.md
09-Arquitetura-do-Core.md
```

## Estado da família

```text
Status: CANÔNICA
Baseline: 01–09
Cobertura: ALTA
Expansão automática: NÃO
Prioridade: aderência à arquitetura real
```

A existência de `09` não justifica criar `10`.

## 01 — GEA

`01-GEA-GereIgreja-Engineering-Architecture.md` funciona como referência arquitetural de alto nível.

Seu papel é apresentar princípios e enquadramento geral da arquitetura de engenharia.

Não deve competir com os documentos especializados `02–09`.

## 02 — Arquitetura da Plataforma

É a principal visão estrutural da plataforma.

Deve documentar:

- natureza modular do sistema;
- principais camadas;
- responsabilidades;
- dependências;
- relações entre componentes;
- fluxos arquiteturais de alto nível.

Detalhes especializados devem ser delegados aos documentos correspondentes.

## 03 — Arquitetura do Backend

Documenta a estrutura arquitetural do Backend.

A relação com `docs/backend/` é:

```text
arquitetura/03
→ estrutura e fronteiras

backend/
→ padrões concretos de implementação
```

## 04 — Arquitetura do Frontend

Documenta a estrutura arquitetural da camada de apresentação.

A relação correta é:

```text
arquitetura/04
→ estrutura

frontend/
→ implementação

design-system/
→ linguagem visual
```

## 05 — Arquitetura do Banco de Dados

Define a visão arquitetural da persistência.

Detalhes operacionais de PostgreSQL, backup, restore e ambientes pertencem principalmente a `docs/infraestrutura/`.

Regras específicas de Models pertencem a `docs/backend/` e `docs/apps/`.

## 06 — Arquitetura das APIs

Define a posição das APIs dentro da plataforma.

Detalhes de contratos, payloads, versionamento e ciclo de vida pertencem a:

```text
docs/api/
```

## 07 — Arquitetura da Segurança

Define a arquitetura de proteção em profundidade.

Os controles especializados pertencem a:

```text
docs/seguranca/
docs/frameworks/02-GAF-...
docs/frameworks/03-GSF-...
```

## 08 — Arquitetura Multi-Tenant

É um documento estrutural crítico.

Deve explicitar:

- resolução de tenant;
- contexto da igreja ativa;
- fronteiras de dados;
- isolamento;
- dependências entre autenticação, autorização e tenant;
- pontos de aplicação do escopo organizacional.

Regras funcionais específicas continuam nos Apps.

## 09 — Arquitetura do Core

Define o papel estrutural do Core.

A divisão é:

```text
arquitetura/09
→ papel arquitetural

backend/02-Core-da-Plataforma.md
→ implementação e padrões técnicos
```

O Core não deve ser tratado como módulo de negócio.

## Relação com Governança antiga

O arquivo:

```text
docs/governanca/02-Arquitetura-do-GereIgreja.md
```

foi criado como uma grande referência arquitetural monolítica.

Ele cobre, em um único documento:

- princípios arquiteturais;
- camadas;
- organização do projeto;
- Apps;
- fluxo de requisição;
- Core;
- GOC;
- GDS;
- banco;
- segurança;
- performance;
- escalabilidade;
- observabilidade;
- integrações;
- IA;
- roadmap;
- checklist.

Essa abrangência hoje é excessiva.

A arquitetura documental moderna já distribui esses assuntos entre famílias especializadas.

Portanto, `governanca/02-Arquitetura-do-GereIgreja.md` deve ser tratado como **legado arquitetural**.

A ação recomendada é:

```text
comparar
↓
absorver apenas conteúdo exclusivo ainda válido
↓
corrigir referências
↓
arquivar ou remover o documento legado
```

Não mover o arquivo inteiro para `docs/arquitetura/`.

## Conteúdo potencialmente desatualizado no legado

O documento antigo apresenta exemplos de Apps e estruturas sugeridas como se fossem arquitetura oficial.

Esse tipo de lista envelhece rapidamente.

Qualquer trecho que cite módulos, diretórios ou componentes deve ser confrontado com o código e com as famílias atuais antes de ser absorvido.

Planejamento arquitetural antigo também não deve ser preservado como estado vigente.

## Relação com Governança

```text
governanca/
→ princípios transversais

arquitetura/
→ estrutura sistêmica vigente
```

Governança não deve duplicar mapas arquiteturais detalhados.

## Relação com Backend e Frontend

Arquitetura responde:

```text
como as partes se organizam
```

Backend e Frontend respondem:

```text
como implementar dentro dessa organização
```

## Relação com Infraestrutura

Arquitetura descreve a posição estrutural dos componentes.

Infraestrutura descreve ambientes, serviços e sustentação operacional.

```text
arquitetura/
→ desenho lógico

infraestrutura/
→ plataforma técnica de execução
```

## Regra para novo documento 10+

Antes de criar:

1. demonstrar lacuna arquitetural real;
2. verificar se o tema já cabe em `01–09`;
3. verificar se é realmente arquitetura e não implementação;
4. considerar ADR se houver decisão nova relevante;
5. verificar sobreposição com Backend, Frontend, API, Segurança e Infraestrutura;
6. preferir evoluir documento existente;
7. atualizar README e INDEX somente quando necessário.

## Princípio de manutenção

Arquitetura deve representar o sistema real.

**Documentar estruturas idealizadas ou planejadas como se fossem vigentes é um defeito arquitetural de documentação.**
