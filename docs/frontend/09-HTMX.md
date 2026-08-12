Pasta:
docs/frontend/

Arquivo:
09-HTMX.md

Documento:
GFE-09

Código:
GFE-HTMX

Framework:
GereIgreja Frontend Engineering (GFE)

Versão:
2.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Agosto de 2026

# GFE-09 — Arquitetura HTMX

> *"O HTMX representa a estratégia oficial do GereIgreja para evolução gradual da experiência do usuário, permitindo interfaces mais rápidas, interativas e modernas sem abandonar a arquitetura nativa do Django."*

---

# Sumário

1. Objetivo
2. Escopo
3. Visão Estratégica
4. Filosofia Arquitetural
5. Estado Atual da Plataforma
6. Estado Futuro Desejado
7. Papel do HTMX na Arquitetura
8. Integração com Django
9. Integração com Templates
10. Integração com Layouts
11. Integração com JavaScript
12. Princípios Arquiteturais
13. Casos Oficiais de Uso
14. Quando NÃO utilizar HTMX
15. Roadmap de Adoção
16. Evidências Arquiteturais
17. Especificações Oficiais
18. Boas Práticas
19. Anti-patterns
20. Checklist
21. Glossário
22. Documentos Relacionados

---

# 1. Objetivo

Este documento estabelece a arquitetura oficial para utilização do HTMX no Frontend do GereIgreja.

Seu propósito é definir como a plataforma deverá evoluir para uma interface mais dinâmica, mantendo compatibilidade total com a arquitetura nativa do Django.

O objetivo não é transformar o GereIgreja em uma Single Page Application (SPA), mas sim incorporar interatividade de forma progressiva, preservando simplicidade, desempenho e facilidade de manutenção.

---

# 2. Escopo

Este documento aplica-se a todas as páginas da Área de Gestão do GereIgreja que utilizem ou venham a utilizar HTMX.

Inclui:

- Templates Django;
- Layouts;
- Componentes;
- Partials;
- Includes;
- Formulários;
- Listagens;
- Dashboards;
- Modais;
- Tabelas;
- Filtros;
- Paginação;
- Atualizações parciais.

Não inclui:

- Administração Técnica (Django Admin);
- APIs REST;
- Aplicativos Mobile;
- Backend de regras de negócio.

---

# 3. Visão Estratégica

O GereIgreja adota oficialmente uma estratégia de evolução progressiva do Frontend.

A arquitetura continuará baseada em:

- Django Templates;
- Renderização Server Side (SSR);
- Bootstrap;
- JavaScript nativo.

O HTMX será utilizado para eliminar recarregamentos completos da página quando apenas uma parte da interface precisar ser atualizada.

Essa abordagem preserva:

- SEO;
- simplicidade arquitetural;
- baixo consumo de recursos;
- facilidade de manutenção;
- produtividade da equipe.

---

# 4. Filosofia Arquitetural

O HTMX não substitui o Django.

O HTMX amplia as capacidades do Django.

Toda renderização continuará sendo responsabilidade do servidor.

Toda regra de negócio continuará sendo executada no Backend.

O navegador será responsável apenas por solicitar atualizações parciais da interface.

Essa filosofia reduz significativamente a complexidade quando comparada a arquiteturas SPA tradicionais.

---

# 5. Estado Atual da Plataforma

A análise da base de código identificou que:

- HTMX já está definido como diretriz oficial nos documentos GFE;
- a estrutura de Templates já foi preparada para suportar sua adoção;
- não foram encontrados atributos `hx-*` utilizados de forma significativa na implementação atual.

Isso demonstra que a plataforma encontra-se preparada arquiteturalmente para receber HTMX de maneira gradual, porém sua utilização prática ainda está em fase inicial.

---

# 6. Estado Futuro Desejado

A longo prazo, espera-se que o HTMX seja utilizado em todos os cenários onde uma atualização parcial da interface seja mais eficiente que um recarregamento completo da página.

Exemplos:

- filtros;
- pesquisas;
- tabelas;
- paginação;
- formulários;
- dashboards;
- notificações;
- cards;
- listas;
- modais;
- indicadores.

A adoção deverá ocorrer gradualmente, módulo por módulo, sem comprometer a estabilidade da plataforma.

---

# 7. Papel do HTMX na Arquitetura

Dentro do GereIgreja, o HTMX possui papel complementar.

Arquitetura conceitual:

```
Usuário

↓

Template Django

↓

HTMX

↓

View Django

↓

Template Parcial

↓

Atualização do DOM
```

Observe que não existe uma camada intermediária de API JavaScript.

O próprio Django continua responsável pela geração do HTML.

Essa arquitetura preserva a filosofia Server Side Rendering (SSR).

---

# 8. Integração com Django

Toda requisição HTMX deverá ser tratada por uma View Django.

Fluxo recomendado:

```
Usuário

↓

HTMX

↓

URL Django

↓

View

↓

Template Parcial

↓

Resposta HTML

↓

Atualização Parcial
```

O retorno preferencial será sempre HTML renderizado pelo servidor.

O uso de JSON deverá ocorrer apenas quando estritamente necessário.

---

# 9. Integração com Templates

Os Templates continuam sendo o principal mecanismo de construção da interface.

O HTMX atuará sobre Templates completos ou Templates parciais.

Sempre que possível deverão ser reutilizados:

- Partials;
- Includes;
- Componentes existentes.

Essa estratégia reduz duplicação de código e mantém a consistência visual da plataforma.

---

# 10. Integração com Layouts

Os Layouts oficiais (`base.html`, `base_com_menu.html`, `dashboard_base.html`, `base_publico.html` e demais layouts especializados) permanecem responsáveis pela estrutura global da interface.

O HTMX deverá atuar apenas sobre regiões internas da página, preservando cabeçalho, menu lateral, rodapé e demais elementos estruturais.

Atualizações parciais não deverão substituir o layout completo.

---

# 11. Integração com JavaScript

O JavaScript continuará responsável por comportamentos que não pertencem ao HTMX.

Exemplos:

- gráficos;
- integração com bibliotecas externas;
- animações complexas;
- manipulação avançada do DOM;
- persistência em Local Storage;
- funcionalidades do `dashboard-sidebar.js`.

Sempre que possível, o HTMX deverá substituir apenas código JavaScript cuja única finalidade seja realizar requisições AJAX e atualizar trechos da interface.

---

# 12. Princípios Arquiteturais

Toda implementação HTMX deverá respeitar os seguintes princípios.

## Renderização no Servidor

O HTML permanece sendo produzido pelo Django.

---

## Reutilização

Os Templates existentes deverão ser reutilizados.

---

## Progressividade

A adoção ocorrerá gradualmente.

Não haverá reescrita completa da plataforma.

---

## Baixo Acoplamento

As requisições HTMX deverão permanecer independentes entre si.

---

## Simplicidade

Sempre escolher a solução mais simples possível.

---

## Compatibilidade

Toda implementação deverá permanecer compatível com:

- Django Templates;
- Bootstrap;
- JavaScript nativo;
- Alpine.js (quando utilizado);
- Design System do GereIgreja.

---
# 13. Casos Oficiais de Uso

O HTMX deverá ser utilizado exclusivamente em cenários onde sua adoção simplifique a interface e reduza recarregamentos completos da página.

Os casos abaixo representam os padrões oficialmente recomendados para o GereIgreja.

---

## 13.1 Pesquisa Instantânea

Permite atualizar resultados enquanto o usuário pesquisa.

Exemplos:

- membros;
- congregações;
- visitantes;
- patrimônio;
- contas financeiras;
- eventos;
- escalas;
- documentos.

Fluxo:

```
Campo de Pesquisa

↓

HTMX

↓

View Django

↓

Partial

↓

Lista Atualizada
```

---

## 13.2 Filtros

Os filtros deverão atualizar apenas a região afetada.

Exemplos:

- período;
- congregação;
- departamento;
- situação;
- categoria;
- tipo de lançamento.

Evitar:

```
Recarregar toda a página.
```

Preferir:

```
Atualizar apenas a tabela.
```

---

## 13.3 Paginação

A paginação deverá atualizar apenas:

- tabela;
- lista;
- cards;
- grid.

Jamais deverá substituir o Layout completo.

---

## 13.4 Ordenação

Mudanças de ordenação deverão atualizar apenas o conteúdo listado.

Exemplos:

- Nome;
- Data;
- Valor;
- Cargo;
- Ministério.

---

## 13.5 Formulários

Formulários poderão utilizar HTMX para:

- validações;
- pré-visualizações;
- preenchimentos automáticos;
- salvamento parcial;
- atualização de listas relacionadas.

As validações continuam sendo responsabilidade do Django.

---

## 13.6 Modais

Modais representam um dos principais casos de uso.

Exemplos:

- cadastro rápido;
- edição;
- visualização;
- confirmação;
- detalhes.

Fluxo:

```
Clique

↓

HTMX

↓

View

↓

Partial

↓

Modal
```

---

## 13.7 Dashboards

Os Dashboards Premium deverão utilizar HTMX para atualização de indicadores.

Exemplos:

- cartões;
- gráficos;
- KPIs;
- estatísticas;
- alertas.

Cada componente deverá possuir atualização independente.

---

## 13.8 Cards

Atualizar apenas o Card necessário.

Exemplo:

```
Total de membros

↓

Atualizar somente este Card
```

Sem recarregar o Dashboard inteiro.

---

## 13.9 Tabelas

As tabelas constituem um dos principais cenários de utilização.

Atualizações permitidas:

- pesquisa;
- filtros;
- ordenação;
- paginação;
- exclusão;
- alteração de status.

---

## 13.10 Listas

Toda lista reutilizável poderá ser carregada parcialmente.

Exemplos:

- aniversariantes;
- visitantes;
- departamentos;
- eventos;
- mensagens.

---

## 13.11 Notificações

Atualização periódica de:

- notificações;
- lembretes;
- mensagens internas;
- alertas.

Sem necessidade de recarregar toda a página.

---

## 13.12 Uploads

Uploads poderão utilizar HTMX quando houver benefício claro para a experiência do usuário.

Exemplos:

- documentos;
- fotos;
- anexos.

---

# 14. Quando NÃO Utilizar HTMX

O HTMX não deverá ser utilizado indiscriminadamente.

Existem cenários onde o comportamento tradicional permanece mais simples.

---

## 14.1 Navegação Principal

Mudanças entre módulos deverão continuar utilizando navegação convencional.

Exemplos:

```
Secretaria

↓

Financeiro

↓

Eventos

↓

Comunicação
```

Não utilizar HTMX.

---

## 14.2 Alterações de Layout

Nunca substituir:

- Navbar;
- Sidebar;
- Footer;
- Estrutura Base;
- Breadcrumb completo.

Os Layouts permanecem responsabilidade do Django.

---

## 14.3 Regras de Negócio

HTMX não substitui lógica de negócio.

Toda validação continuará no Backend.

---

## 14.4 Processamentos Complexos

Relatórios extensos.

Exportações.

Importações.

Rotinas administrativas.

Continuam utilizando fluxo tradicional.

---

## 14.5 Administração Técnica

O Django Admin permanece independente.

Sua arquitetura não deverá utilizar HTMX como padrão.

---

# 15. Roadmap de Adoção

A adoção ocorrerá em etapas.

---

## Fase 1

Infraestrutura.

- documentação;
- padronização;
- preparação dos Templates.

Status:

Concluída.

---

## Fase 2

Primeiros módulos.

Prioridade:

- filtros;
- tabelas;
- paginação;
- pesquisas.

---

## Fase 3

Expansão.

Aplicação em:

- Dashboards;
- Cards;
- KPIs;
- Indicadores.

---

## Fase 4

Consolidação.

Todos os novos módulos deverão considerar HTMX desde sua concepção.

---

## Fase 5

Otimização.

Redução significativa de:

- JavaScript AJAX;
- duplicação de código;
- recarregamentos completos.

---

# 16. Evidências Arquiteturais

Este documento foi elaborado considerando a arquitetura atual do GereIgreja.

---

## EA-HTMX-001

Documentação oficial.

Arquivos:

```
GFE-02

GFE-03

GFE-04
```

Já estabelecem HTMX como diretriz arquitetural.

---

## EA-HTMX-002

Templates.

Durante a análise realizada não foram identificados atributos:

```
hx-get

hx-post

hx-target

hx-trigger

hx-swap
```

Isso confirma que a adoção prática ainda é inicial.

---

## EA-HTMX-003

Arquitetura.

A estrutura baseada em:

- Templates;
- Layouts;
- Partials;
- Includes.

Já se encontra preparada para receber HTMX sem necessidade de refatoração estrutural.

---

## EA-HTMX-004

Dashboard.

O `dashboard_base.html` já utiliza blocos que facilitam a evolução para componentes atualizados parcialmente.

---

## EA-HTMX-005

Separação Arquitetural.

A Área de Gestão poderá adotar HTMX.

A Administração Técnica (Django Admin) permanece independente.

---

# 17. Especificações Oficiais

As especificações abaixo estabelecem os requisitos oficiais para utilização do HTMX no Frontend do GereIgreja.

---

## GFE-HTMX-001

O HTMX deverá ser utilizado exclusivamente como complemento da arquitetura baseada em Django Templates.

---

## GFE-HTMX-002

Toda resposta HTMX deverá ser gerada por uma View Django.

---

## GFE-HTMX-003

O retorno preferencial deverá ser HTML renderizado pelo servidor.

Sempre que possível evitar respostas JSON.

---

## GFE-HTMX-004

Toda atualização deverá afetar apenas a região necessária da interface.

Evitar substituições completas da página.

---

## GFE-HTMX-005

Os Layouts oficiais nunca deverão ser substituídos por requisições HTMX.

Inclui:

- base.html
- base_com_menu.html
- dashboard_base.html
- base_publico.html
- demais layouts especializados

---

## GFE-HTMX-006

Sempre reutilizar Partials e Includes existentes.

A criação de novos Templates parciais deverá seguir a arquitetura oficial de Templates.

---

## GFE-HTMX-007

O HTMX não deverá conter regras de negócio.

Toda validação continuará sendo executada pelo Backend.

---

## GFE-HTMX-008

Sempre preservar compatibilidade com:

- Bootstrap;
- JavaScript nativo;
- Alpine.js (quando utilizado);
- Design System;
- Accessibility Guidelines.

---

## GFE-HTMX-009

Requisições HTMX deverão possuir responsabilidade única.

Cada interação deverá resolver apenas um objetivo.

---

## GFE-HTMX-010

Os atributos HTMX deverão permanecer legíveis.

Evitar excesso de atributos em um único elemento.

---

## GFE-HTMX-011

Priorizar reutilização de endpoints.

Evitar múltiplas URLs para a mesma responsabilidade.

---

## GFE-HTMX-012

Sempre documentar novos padrões arquiteturais antes de adotá-los como oficiais.

---

## GFE-HTMX-013

Os módulos existentes poderão migrar para HTMX de forma gradual.

Não haverá obrigatoriedade de migração imediata.

---

## GFE-HTMX-014

Toda implementação deverá preservar compatibilidade com renderização tradicional do Django.

---

## GFE-HTMX-015

A adoção do HTMX deverá priorizar simplicidade.

Caso a implementação se torne mais complexa que a solução tradicional, o uso deverá ser reavaliado.

---

# 18. Boas Práticas

Durante o desenvolvimento recomenda-se:

- reutilizar Views existentes;
- reutilizar Templates parciais;
- reutilizar Partials;
- reutilizar Includes;
- manter respostas pequenas;
- utilizar HTML renderizado pelo Django;
- evitar JavaScript desnecessário;
- preservar acessibilidade;
- preservar responsividade;
- manter compatibilidade com Bootstrap;
- utilizar nomes claros para endpoints;
- documentar novas convenções.

---

# 19. Anti-patterns

Os padrões abaixo não fazem parte da arquitetura oficial.

---

## 19.1 Transformar o GereIgreja em SPA

O HTMX não substitui o Django.

---

## 19.2 Duplicar Templates

Evitar criar uma versão "HTMX" e outra "normal" quando o mesmo Partial puder ser reutilizado.

---

## 19.3 Retornar Grandes Blocos HTML

Atualizações deverão ser pequenas.

Substituir apenas a região necessária.

---

## 19.4 Misturar Regras de Negócio

Toda lógica permanece no Backend.

---

## 19.5 Criar Dependências entre Componentes

Cada atualização deverá ser independente.

---

## 19.6 Excesso de Requisições

Evitar chamadas desnecessárias.

Sempre considerar desempenho e experiência do usuário.

---

## 19.7 Ignorar o Design System

Toda interface retornada pelo HTMX deverá respeitar os padrões visuais oficiais.

---

# 20. Checklist

Antes de implementar HTMX verificar:

## Arquitetura

- [ ] Existe benefício real?
- [ ] A solução continua simples?
- [ ] O Layout permanece intacto?

---

## Templates

- [ ] Está reutilizando Partial?
- [ ] Está reutilizando Include?
- [ ] Está reutilizando Componentes existentes?

---

## Django

- [ ] Existe View dedicada?
- [ ] A resposta é HTML?
- [ ] Não há lógica de negócio no Frontend?

---

## Interface

- [ ] Atualiza apenas a região necessária?
- [ ] Mantém responsividade?
- [ ] Mantém acessibilidade?

---

## Documentação

- [ ] Segue o GFE?
- [ ] Segue o Design System?
- [ ] Segue os padrões arquiteturais?

---

# 21. Glossário

## HTMX

Biblioteca que permite atualizações parciais da interface utilizando HTML renderizado pelo servidor.

---

## Partial

Template reutilizável responsável por uma região específica da interface.

---

## Include

Fragmento reutilizado através da tag `{% include %}`.

---

## SSR

Server Side Rendering.

Modelo arquitetural adotado oficialmente pelo GereIgreja.

---

## Atualização Parcial

Atualização restrita a uma região específica da interface sem recarregar toda a página.

---

## Progressive Enhancement

Estratégia adotada pelo GereIgreja para evolução gradual da interface, preservando compatibilidade com a renderização tradicional do Django.

---

# 22. Governança da Arquitetura HTMX

A adoção do HTMX deverá respeitar os seguintes princípios de governança.

- Toda nova implementação deverá seguir este documento.
- Novos padrões deverão ser documentados antes de se tornarem oficiais.
- A arquitetura deverá permanecer compatível com Django Templates.
- O uso do HTMX não deverá comprometer a legibilidade do código.
- Toda evolução deverá preservar simplicidade, reutilização e baixo acoplamento.

O objetivo da governança é garantir que o crescimento da plataforma ocorra de maneira consistente e sustentável.

---

# 23. Documentos Relacionados

## GereIgreja Frontend Engineering

- README.md
- GFE-01 — Frontend Architecture
- GFE-02 — Estrutura de Pastas
- GFE-03 — Componentes
- GFE-04 — Layouts
- GFE-05 — Templates
- GFE-06 — Assets
- GFE-07 — CSS
- GFE-08 — JavaScript
- GFE-10 — Alpine.js
- GFE-11 — Dashboards

---

## Documentação Corporativa

- GereIgreja Design System (GDS)
- GereIgreja Documentation Framework (GDF)
- GereIgreja Quality Framework (GQF)

---

# Conclusão

O HTMX constitui a estratégia oficial de evolução progressiva da experiência do usuário no GereIgreja.

Sua adoção preserva a arquitetura baseada em Django Templates e Renderização no Servidor (SSR), permitindo interfaces mais rápidas e responsivas sem introduzir a complexidade de uma Single Page Application.

A combinação entre Django, HTMX, Bootstrap e JavaScript nativo estabelece uma base tecnológica moderna, sustentável e alinhada aos princípios arquiteturais da plataforma.

Toda implementação futura deverá seguir os padrões definidos neste documento, garantindo consistência, reutilização, desempenho e facilidade de manutenção.

---

# Status do Documento

**Pasta**

```
docs/frontend/
```

**Arquivo**

```
09-HTMX.md
```

**Código**

```
GFE-HTMX
```

**Versão**

```
2.0
```

**Status**

```
OFICIAL
```

---

**Fim do Documento**

