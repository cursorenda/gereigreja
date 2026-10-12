# Apps — Documentação Funcional dos Módulos

Apps<br>
↓<br>
O que existe em cada domínio funcional do GereIgreja.

Esta pasta concentra a documentação funcional por módulo do GereIgreja, incluindo o inventário dos componentes técnicos relevantes apenas quando necessário para explicar o comportamento do domínio.

A pasta `docs/apps/` não substitui a documentação de arquitetura, backend, frontend, segurança, qualidade ou operação.

## Finalidade da pasta

- registrar o que existe em cada módulo funcional;
- documentar escopo, jornadas, regras e integrações por domínio;
- consolidar a visão funcional canônica de cada app;
- registrar serviços, selectors e componentes existentes quando forem relevantes para compreender o módulo;
- apontar para a documentação técnica especializada sem duplicá-la;
- distinguir funcionalidades implementadas de itens apenas planejados ou históricos.

## Fronteira com outras famílias

### `docs/backend/`

Define **como o backend deve ser construído**.

Exemplos:

- padrões para Services;
- padrões para Selectors;
- organização de Models;
- autorização no backend;
- testes e arquitetura de código.

### `docs/apps/`

Define **o que existe funcionalmente em cada domínio**.

Exemplos:

- quais jornadas o Financeiro suporta;
- quais regras governam a EBD;
- como Eventos se integra à Agenda;
- como cargos influenciam Usuários;
- quais configurações são locais ou ministeriais.

Um documento em `docs/apps/` pode citar Services, Selectors, Models ou Views existentes, mas não deve repetir padrões gerais de engenharia.

### `docs/frontend/` e `docs/design-system/`

Definem arquitetura de interface e padrões visuais transversais.

Por isso, Dashboard não é tratado como domínio funcional independente nesta pasta.

### `docs/arquitetura/` e `docs/backend/`

Definem componentes estruturais compartilhados da plataforma.

Por isso, Core não é tratado como domínio funcional independente nesta pasta.

## Regra para criar documentação de um novo App

Antes de criar um novo arquivo:

1. confirme que existe um domínio funcional real;
2. verifique se já existe documentação canônica equivalente;
3. confirme que o módulo está implementado ou possui evidência suficiente de existência funcional;
4. use o número definido no índice desta pasta;
5. crie o arquivo no padrão `NN-NomeDoApp.md`;
6. documente escopo, jornadas, regras, integrações, segurança, multi-tenancy, testes e limites;
7. diferencie claramente implementação atual, histórico e planejamento;
8. referencie documentação técnica especializada sem duplicá-la;
9. atualize este README e o `docs/INDEX.md`.

> Número disponível no índice não é justificativa suficiente para criar um arquivo.

## Padrão de Nomenclatura

- `NN-NomeDoApp.md`
- `NN` com dois dígitos;
- nomes sem acentos no arquivo;
- ordem estável para navegação.

A numeração não obriga a existência de todos os números quando um item não representa um domínio funcional documentável.

## Índice de Apps

| Nº | Documento | Situação |
|---:|---|---|
| 01 | [01-Membros.md](01-Membros.md) | Canônico |
| 02 | [02-Secretaria.md](02-Secretaria.md) | Canônico |
| 03 | [03-Financeiro.md](03-Financeiro.md) | Canônico |
| 04 | [04-Comunicacao.md](04-Comunicacao.md) | Canônico |
| 05 | [05-Departamentos.md](05-Departamentos.md) | Canônico |
| 06 | [06-EBD.md](06-EBD.md) | Canônico |
| 07 | [07-Eventos.md](07-Eventos.md) | Canônico |
| 08 | `08-Patrimonio.md` | Previsto, mas não criar até haver implementação funcional comprovada |
| 09 | [09-Usuarios.md](09-Usuarios.md) | Canônico |
| 10 | [10-Configuracoes.md](10-Configuracoes.md) | Canônico |

## Itens removidos da expectativa de `docs/apps/`

### Dashboard

`11-Dashboard.md` não deve ser criado como documento funcional desta pasta.

Dashboard é uma camada transversal de apresentação e gestão.

Referências canônicas:

- `docs/frontend/11-Dashboards.md` — arquitetura técnica dos dashboards;
- `docs/design-system/15-Dashboards.md` — experiência, composição e linguagem visual;
- documentos funcionais de cada módulo — métricas, filtros e jornadas específicas daquele dashboard.

### Core

`12-Core.md` não deve ser criado como documento funcional desta pasta.

Core é infraestrutura compartilhada da plataforma e não representa domínio de negócio.

Referências canônicas:

- `docs/backend/02-Core-da-Plataforma.md`;
- `docs/arquitetura/09-Arquitetura-do-Core.md`.

## Patrimônio

`08-Patrimonio.md` permanece reservado na sequência histórica, mas não deve ser criado apenas para preencher a numeração.

Até a revisão atual, existe evidência de Patrimônio como domínio previsto, porém não há documentação suficiente para comprovar um módulo funcional implementado com regras, jornadas e integrações estáveis.

Quando a implementação for confirmada, o documento poderá ser criado sem renumerar os arquivos posteriores.

## Princípio de manutenção

Esta pasta deve refletir a arquitetura funcional real do GereIgreja.

Sempre priorizar:

**evoluir antes de criar; consolidar antes de duplicar; documentar somente o que possui fundamento verificável.**
