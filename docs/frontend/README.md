# Frontend — Arquitetura e Engenharia da Interface

Frontend  
↓  
Como a camada de apresentação do GereIgreja deve ser estruturada e implementada.

Esta pasta reúne a documentação canônica da engenharia de Frontend do GereIgreja.

Ela cobre arquitetura da interface, estrutura de pastas, componentes, layouts, templates, assets, CSS, JavaScript, HTMX, Alpine.js e dashboards.

## Finalidade da pasta

- definir a arquitetura do Frontend;
- padronizar organização de diretórios;
- documentar layouts e templates base;
- estabelecer padrões para componentes reutilizáveis;
- documentar assets, CSS e JavaScript;
- orientar uso de HTMX e Alpine.js;
- registrar padrões técnicos para dashboards;
- manter a implementação alinhada ao GereIgreja Design System.

## Fronteira com Design System

`docs/design-system/` define:

```text
o que a interface deve parecer
e quais padrões visuais devem existir
```

`docs/frontend/` define:

```text
como esses padrões são implementados
```

Portanto:

```text
design-system/
→ tokens, componentes visuais, linguagem visual, padrões de UX

frontend/
→ templates, layouts, assets, CSS, JS, HTMX, Alpine e composição técnica
```

O Frontend não deve redefinir a identidade visual.

## Fronteira com Backend

`docs/backend/` documenta a implementação Python e as regras de engenharia do backend.

`docs/frontend/` documenta a camada de apresentação.

A divisão é:

```text
backend/
→ Models, Services, Selectors, Views, Forms, Permissions etc.

frontend/
→ HTML, templates, layouts, CSS, JS e interação de interface
```

Django Templates pertencem ao Frontend, mesmo sendo renderizados pelo Django.

## Inventário atual

A família possui atualmente:

```text
01-Frontend-Architecture.md
02-Estrutura de Pastas.md
03-Componentes.md
04-Layouts.md
05-Templates.md
06-Assets.md
07-CSS.md
08-JavaScript.md
09-HTMX.md
10-AlpineJS.md
11-Dashboards.md
Migracao-CSS.md
```

A numeração canônica implementada hoje termina em `11`.

O README anterior projetava documentos `12` a `20`, mas esses arquivos não existem atualmente na pasta.

Isso significa que eles devem ser tratados como **ideias históricas de expansão**, não como lacunas obrigatórias.

## Estado da sequência 12–20

O README antigo previa:

```text
12 - Formulários
13 - Tabelas
14 - Modais
15 - Responsividade
16 - Acessibilidade
17 - Performance
18 - Boas Práticas
19 - Checklist
20 - Roadmap
```

Esses números **não devem ser criados automaticamente**.

Antes de qualquer novo documento:

1. demonstrar lacuna real;
2. verificar `design-system/`;
3. verificar `qualidade/`;
4. verificar se o tema já está coberto em `01–11`;
5. preferir evoluir documentos existentes;
6. só criar novo documento se o assunto possuir escopo autônomo e duradouro.

## 01 — Frontend Architecture

Define a visão geral da camada de apresentação.

Deve estabelecer:

- responsabilidades do Frontend;
- relação com Backend;
- relação com Design System;
- fluxo de renderização;
- organização tecnológica;
- princípios de modularização.

## 02 — Estrutura de Pastas

Documenta como o Frontend é organizado fisicamente.

Deve refletir a estrutura real do projeto e não uma estrutura idealizada que não exista no código.

## 03 — Componentes

Documenta padrões técnicos de reutilização de componentes.

A definição visual dos componentes continua pertencendo ao Design System.

## 04 — Layouts

Documenta os layouts estruturais e suas responsabilidades.

Layouts devem ser tratados como arquitetura de composição, não como regra funcional.

## 05 — Templates

`05-Templates.md` é a fonte canônica para arquitetura e padrões de Templates Django.

Ele substitui como referência principal documentos antigos como:

```text
docs/governanca/07-Padroes-de-Templates.md
docs/templates/ARQUITETURA_TEMPLATES.md
```

O segundo já foi consolidado e removido da árvore.

O documento de Governança deve agora ser comparado com `05-Templates.md`, `03-Componentes.md`, `04-Layouts.md`, `07-CSS.md`, `08-JavaScript.md` e o Design System.

Após absorver qualquer conteúdo exclusivo ainda válido, ele não deve continuar como norma concorrente.

## Governança antiga — Padrões de Templates

`docs/governanca/07-Padroes-de-Templates.md` cobre:

- organização de templates;
- templates base;
- componentes;
- GDS;
- formulários;
- tabelas;
- JavaScript;
- CSS;
- acessibilidade;
- performance;
- checklist.

Esse conteúdo hoje está distribuído por famílias mais especializadas.

A ação recomendada é:

```text
comparar
↓
absorver apenas conteúdo exclusivo e ainda válido
↓
corrigir referências
↓
arquivar ou remover o documento legado
```

Não mover simplesmente o arquivo inteiro para `frontend/`, pois isso criaria duplicação.

## 06 — Assets

Documenta recursos estáticos e sua organização.

Pode incluir:

- CSS;
- JavaScript;
- imagens;
- ícones;
- fontes;
- build ou coleta de assets quando aplicável.

Não documentar artefatos gerados como se fossem fonte editável.

## 07 — CSS

É a referência técnica para organização e manutenção do CSS.

Deve permanecer coerente com o Design System e com a fonte de verdade dos tokens visuais.

## `Migracao-CSS.md`

Este arquivo foi corretamente consolidado nesta família a partir da antiga pasta `docs/ui/`.

Ele possui valor como documento técnico de migração/inventário, especialmente ao diferenciar arquivos-fonte de diretórios gerados.

Por ser documento de transição, deve ser revisado periodicamente.

Quando a migração estiver totalmente encerrada e seu conteúdo já estiver absorvido por `07-CSS.md`, pode ser arquivado ou removido após verificar referências.

## 08 — JavaScript

Define padrões para scripts da aplicação.

Deve estabelecer limites claros para:

- JavaScript inline;
- reutilização;
- organização por responsabilidade;
- integração com HTMX;
- integração com Alpine.js.

## 09 — HTMX

Documenta o uso do HTMX no GereIgreja.

Deve refletir a versão e os padrões realmente adotados pela aplicação.

Não transformar intenção de adoção em afirmação de implementação ampla sem evidência.

## 10 — AlpineJS

Documenta a adoção gradual do Alpine.js.

O uso deve permanecer controlado e complementar à arquitetura existente.

Alpine não deve ser introduzido apenas para substituir JavaScript simples sem benefício claro.

## 11 — Dashboards

Documenta a implementação técnica dos dashboards.

A divisão é:

```text
design-system/15-Dashboards.md
→ padrão visual e UX

frontend/11-Dashboards.md
→ implementação e composição técnica

apps/
→ dados e comportamento funcional de cada dashboard
```

Por isso, Dashboard não deve existir como app documental independente.

## Templates base

A documentação atual reconhece a arquitetura baseada em herança de templates.

A família deve refletir os templates realmente vigentes no código, incluindo quando aplicável:

```text
base.html
base_com_menu.html
dashboard_base.html
menu.html
```

Qualquer template citado como oficial deve existir e possuir função atual comprovada.

## Relação com CSS legado

Evitar manter múltiplas fontes dizendo quais arquivos CSS são oficiais.

A hierarquia deve ser:

```text
design-system/
→ tokens e padrões

frontend/07-CSS.md
→ organização técnica

frontend/Migracao-CSS.md
→ histórico/plano de consolidação enquanto ainda necessário
```

## Relação com Qualidade

Checklists de revisão de tela, acessibilidade e validação visual podem ser referenciados pelo Frontend, mas gates reutilizáveis pertencem a:

```text
docs/qualidade/
docs/frameworks/04-GQF-...
```

Não criar política de qualidade paralela dentro do Frontend.

## Regra para novos documentos

Antes de criar `12+`:

1. comprovar que o tema não cabe em `01–11`;
2. verificar sobreposição com `design-system/`;
3. verificar sobreposição com `qualidade/`;
4. verificar se a necessidade é técnica e transversal;
5. preferir evolução do documento existente;
6. atualizar README e INDEX somente depois.

## Estado da família

Classificação atual:

```text
Status: CANÔNICA
Baseline real: 01–11
Documento transitório adicional: Migracao-CSS.md
Cobertura: ALTA
Expansão automática: NÃO
Sobreposição histórica com governanca/: SIM
```

## Decisão sobre o README antigo

O README anterior era valioso como visão inicial, mas continha uma expansão planejada até `20` que não corresponde ao inventário real atual.

Essa expectativa deve ser removida para evitar criação artificial de documentos.

A família deve crescer por necessidade comprovada, não por numeração previamente imaginada.

## Princípio de manutenção

Frontend documenta **como a interface é construída**.

**O Design System define a linguagem visual; o Frontend implementa essa linguagem sem duplicar sua autoridade.**
