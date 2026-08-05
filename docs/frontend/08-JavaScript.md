Pasta:
docs/frontend/

Arquivo:
08-JavaScript.md

Documento:
GFE-08

Código:
GFE-JS

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

# GFE-08 — Arquitetura JavaScript

> *"A arquitetura JavaScript do GereIgreja tem como objetivo fornecer uma camada de comportamento previsível, reutilizável e desacoplada da lógica de negócio, preservando a simplicidade da interface e a integração nativa com o Django."*

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia do JavaScript
4. Arquitetura Geral
5. Organização Oficial
6. Estrutura dos Scripts
7. JavaScript Compartilhado
8. JavaScript dos Dashboards
9. Integração com Django
10. Integração com HTMX e Alpine.js
11. Convenções de Nomenclatura
12. Evidências Arquiteturais
13. Inventário Oficial
14. Especificações Oficiais
15. Boas Práticas
16. Anti-patterns
17. Checklist
18. Glossário
19. Roadmap
20. Documentos Relacionados

---

# 1. Objetivo

Este documento define oficialmente a arquitetura JavaScript utilizada pelo Frontend do GereIgreja.

Seu objetivo é padronizar a organização dos scripts, estabelecer critérios para reutilização e garantir que o comportamento da interface permaneça consistente, previsível e de fácil manutenção.

---

# 2. Escopo

Este documento aplica-se exclusivamente à camada JavaScript do Frontend.

Inclui:

- scripts compartilhados;
- scripts específicos dos módulos;
- organização da pasta `static/js`;
- carregamento dos scripts;
- integração com Templates;
- integração com Dashboards;
- integração futura com HTMX e Alpine.js.

Não inclui:

- Backend;
- APIs;
- Models;
- Views;
- lógica de negócio.

---

# 3. Filosofia do JavaScript

O GereIgreja adota uma arquitetura baseada em JavaScript leve.

Os scripts devem possuir responsabilidades específicas e bem definidas.

Sempre que possível:

- reutilizar código;
- evitar duplicação;
- manter baixo acoplamento;
- separar comportamento da estrutura HTML;
- preservar a simplicidade.

Toda regra de negócio permanece no Backend.

---

# 4. Arquitetura Geral

A camada JavaScript é organizada em níveis.

Arquitetura conceitual:

```
JavaScript Compartilhado

↓

JavaScript dos Dashboards

↓

JavaScript dos Módulos

↓

Scripts Específicos da Página

↓

Interação do Usuário
```

Cada camada possui responsabilidade própria.

---

# 5. Organização Oficial

Atualmente a arquitetura privilegia scripts compartilhados.

Estrutura conceitual:

```
static/

    js/

        dashboard-sidebar.js

        ...

```

Também podem existir scripts específicos para determinados módulos.

Esses scripts não substituem a infraestrutura compartilhada.

---

# 6. Estrutura dos Scripts

Os scripts deverão ser organizados conforme sua responsabilidade.

## Scripts Compartilhados

Utilizados por diversos módulos.

Exemplos:

- controle de Sidebar;
- utilidades;
- comportamentos globais;
- inicializações.

---

## Scripts dos Dashboards

Responsáveis pelos comportamentos exclusivos dos Dashboards Premium.

Arquivo identificado:

```
dashboard-sidebar.js
```

---

## Scripts Específicos

Pertencem exclusivamente a um domínio funcional.

Exemplos:

```
financeiro/

secretaria/

eventos/
```

Sempre que possível deverão permanecer desacoplados da infraestrutura compartilhada.

---

# 7. JavaScript Compartilhado

Os scripts compartilhados representam a base comportamental da plataforma.

Seu objetivo é fornecer funcionalidades reutilizáveis para diversos módulos.

Características desejadas:

- reutilização;
- baixo acoplamento;
- simplicidade;
- documentação.

---

# 8. JavaScript dos Dashboards

O arquivo atualmente identificado é:

```
dashboard-sidebar.js
```

Sua responsabilidade inclui:

- abertura da Sidebar;
- fechamento da Sidebar;
- alternância do modo Full Width;
- persistência do estado através do Local Storage;
- sincronização entre interface e armazenamento local.

Esse comportamento é inicializado automaticamente por:

```
dashboard_base.html
```

A inicialização ocorre através do objeto:

```javascript
DashboardSidebar.init(...)
```

---

# 9. Integração com Django

Os scripts locais deverão ser carregados utilizando a infraestrutura oficial do Django.

Exemplo:

```django
{% load static %}
```

Carregamento:

```django
<script src="{% static 'js/dashboard-sidebar.js' %}"></script>
```

Scripts específicos deverão utilizar os blocos disponibilizados pelos Layouts.

Exemplo:

```django
{% block dashboard_extra_js %}
{% endblock %}
```

ou

```django
{% block extra_js %}
{% endblock %}
```

---

# 10. Integração com HTMX e Alpine.js

A arquitetura oficial prevê evolução gradual da camada JavaScript.

Situação atual identificada:

## HTMX

Definido como diretriz arquitetural.

Ainda sem utilização ampla identificada nos Templates analisados.

---

## Alpine.js

Também definido como tecnologia oficial para comportamentos leves.

Até o momento da análise sua adoção permanece gradual.

---

## JavaScript Puro

Atualmente representa a principal tecnologia utilizada pela plataforma para controle da interface.

Essa abordagem mantém o Frontend simples, previsível e fortemente integrado ao Django.

---

# 11. Convenções de Nomenclatura

Os scripts deverão utilizar nomes claros e relacionados à funcionalidade.

Exemplos recomendados:

```
dashboard-sidebar.js

dashboard-filters.js

member-form.js

financial-charts.js
```

Evitar:

```
script1.js

novo.js

teste.js

codigo.js
```

Classes e objetos JavaScript deverão utilizar nomes descritivos.

Exemplo identificado:

```javascript
DashboardSidebar
```

Essa convenção facilita leitura e manutenção do código.

---
# 12. Evidências Arquiteturais

Este documento foi elaborado com base na arquitetura JavaScript atualmente implementada no GereIgreja.

As evidências abaixo representam os principais scripts, padrões e mecanismos identificados durante a análise do projeto.

---

## EA-JS-001

Diretório

```
static/js/
```

Responsabilidade

Repositório oficial dos scripts compartilhados do Frontend.

---

## EA-JS-002

Arquivo

```
dashboard-sidebar.js
```

Responsabilidade

Script responsável pelo gerenciamento da Sidebar dos Dashboards Premium.

Principais funcionalidades identificadas:

- abertura da Sidebar;
- fechamento da Sidebar;
- persistência do estado;
- alternância do modo Full Width.

---

## EA-JS-003

Template

```
dashboard_base.html
```

Responsabilidade

Inicialização automática do comportamento da Sidebar através de:

```javascript
DashboardSidebar.init(...)
```

---

## EA-JS-004

Local Storage

Chaves identificadas:

```
dashboard.sidebar_visible
```

e chaves específicas definidas por cada Dashboard através dos blocos:

```django
{% block dashboard_sidebar_key %}
```

e

```django
{% block dashboard_sidebar_init_key %}
```

Essa arquitetura permite que diferentes Dashboards mantenham estados independentes.

---

## EA-JS-005

Inicialização Centralizada

O carregamento ocorre pelo Layout Base do Dashboard.

Os Templates dos módulos apenas fornecem parâmetros através dos blocos disponíveis.

Essa estratégia reduz duplicação de código.

---

## EA-JS-006

Blocos JavaScript

Blocos identificados:

```django
{% block extra_js %}
```

```django
{% block dashboard_extra_js %}
```

Esses blocos permitem que cada módulo carregue seus próprios scripts sem alterar o Layout Base.

---

## EA-JS-007

HTMX

Situação atual.

Diretriz oficial.

Adoção prática ainda gradual.

Não foram identificados atributos como:

```
hx-get

hx-post

hx-trigger

hx-target
```

nos Templates analisados.

---

## EA-JS-008

Alpine.js

Situação atual.

Diretriz oficial.

Adoção gradual.

Até o momento não foram identificadas marcações como:

```
x-data

x-show

x-bind

x-on
```

na base analisada.

---

## EA-JS-009

JavaScript Puro

Representa atualmente a principal tecnologia utilizada para controle da interface.

Essa abordagem reduz dependências externas e mantém forte integração com Django.

---

# 13. Inventário Oficial

## Diretórios

| Diretório | Situação |
|-----------|----------|
| static/js/ | Oficial |

---

## Scripts Compartilhados

Arquivos identificados.

| Arquivo | Finalidade |
|----------|------------|
| dashboard-sidebar.js | Sidebar Premium |

---

## Objetos JavaScript

Objetos atualmente identificados.

| Objeto | Finalidade |
|---------|------------|
| DashboardSidebar | Controle da Sidebar |

---

## Blocos dos Templates

Blocos disponíveis para carregamento de scripts.

| Bloco | Finalidade |
|--------|------------|
| extra_js | Scripts gerais |
| dashboard_extra_js | Scripts dos Dashboards |

---

## Tecnologias Integradas

| Tecnologia | Situação |
|-------------|----------|
| JavaScript ES6 | Oficial |
| HTMX | Adoção Gradual |
| Alpine.js | Adoção Gradual |

---

# 14. Especificações Oficiais

As regras abaixo estabelecem o padrão oficial para evolução da camada JavaScript.

---

## GFE-JS-001

Todo script compartilhado deverá permanecer centralizado.

---

## GFE-JS-002

Scripts específicos deverão permanecer restritos ao respectivo módulo.

---

## GFE-JS-003

Não duplicar funcionalidades.

---

## GFE-JS-004

Objetos JavaScript deverão possuir responsabilidade única.

---

## GFE-JS-005

Toda inicialização deverá ocorrer preferencialmente através dos Layouts Base.

---

## GFE-JS-006

Scripts deverão ser carregados através dos blocos oficiais.

---

## GFE-JS-007

Evitar dependência direta entre módulos distintos.

---

## GFE-JS-008

Toda nova infraestrutura JavaScript deverá ser documentada antes de tornar-se padrão arquitetural.

---

# 15. Boas Práticas

Durante o desenvolvimento recomenda-se:

- reutilizar scripts existentes;
- manter baixo acoplamento;
- utilizar objetos com responsabilidade única;
- evitar funções excessivamente grandes;
- documentar novos scripts compartilhados;
- utilizar os blocos oficiais para carregamento;
- manter compatibilidade com HTMX e Alpine.js;
- preservar integração com Django;
- utilizar nomes claros e consistentes;
- remover código obsoleto.

---

# 16. Anti-patterns

Os padrões abaixo não fazem parte da arquitetura oficial.

---

## 16.1 Código Duplicado

Evitar copiar funções entre diferentes arquivos.

---

## 16.2 JavaScript Embutido

Evitar grandes blocos de JavaScript diretamente nos Templates.

Sempre que possível utilizar arquivos dedicados.

---

## 16.3 Objetos Monolíticos

Objetos muito grandes dificultam manutenção.

Preferir responsabilidades pequenas.

---

## 16.4 Acoplamento Excessivo

Scripts não deverão depender diretamente da estrutura interna de outros módulos.

---

## 16.5 Manipulação Direta Excessiva do DOM

Sempre que possível centralizar comportamentos reutilizáveis.

---

## 16.6 Dependências Desnecessárias

Evitar inclusão de bibliotecas quando JavaScript nativo resolver adequadamente o problema.

---

## 16.7 Mistura de Responsabilidades

Não misturar:

- lógica de interface;
- regras de negócio;
- comunicação com Backend;
- renderização.

Cada camada deverá permanecer independente.

---

# 17. Checklist

Antes de criar, alterar ou remover um script JavaScript, verificar os itens abaixo.

---

## Organização

- [ ] O script está localizado na pasta correta?
- [ ] A responsabilidade está claramente definida?
- [ ] O nome do arquivo segue o padrão oficial?

---

## Reutilização

- [ ] Já existe funcionalidade semelhante?
- [ ] O código pode ser reutilizado por outros módulos?
- [ ] Foi evitada duplicação?

---

## Estrutura

- [ ] O código está organizado em funções ou objetos?
- [ ] Cada função possui responsabilidade única?
- [ ] O script permanece desacoplado?

---

## Integração

- [ ] O carregamento ocorre através do bloco correto?
- [ ] Está compatível com os Layouts oficiais?
- [ ] Está compatível com os Templates existentes?

---

## Performance

- [ ] Foram evitadas consultas desnecessárias ao DOM?
- [ ] Os eventos foram registrados apenas quando necessários?
- [ ] Não existem execuções redundantes?

---

## Compatibilidade

- [ ] Compatível com Bootstrap?
- [ ] Compatível com HTMX (quando adotado)?
- [ ] Compatível com Alpine.js (quando adotado)?
- [ ] Compatível com o Design System?

---

## Documentação

- [ ] Inventário atualizado?
- [ ] Evidências atualizadas?
- [ ] Especificações preservadas?

---

# 18. Glossário

## Script Compartilhado

Arquivo JavaScript reutilizado por diferentes módulos da plataforma.

---

## Script Específico

Arquivo utilizado exclusivamente por um determinado domínio funcional.

---

## DashboardSidebar

Objeto JavaScript responsável pelo gerenciamento da Sidebar dos Dashboards Premium.

Responsabilidades identificadas:

- abertura;
- fechamento;
- persistência do estado;
- alternância do modo Full Width.

---

## Local Storage

Mecanismo do navegador utilizado para armazenar pequenas informações localmente.

No GereIgreja é utilizado para preservar preferências da interface, como a visibilidade da Sidebar.

---

## Inicialização

Processo responsável por ativar um comportamento JavaScript após o carregamento da página.

No Dashboard ocorre através de:

```javascript
DashboardSidebar.init(...)
```

---

## JavaScript Modular

Estratégia na qual cada arquivo possui responsabilidade específica, reduzindo acoplamento e facilitando manutenção.

---

## Evento

Ação executada em resposta à interação do usuário ou ao ciclo de vida da página.

Exemplos:

- clique;
- carregamento;
- alteração de formulário.

---

## HTMX

Tecnologia prevista para modernizar a comunicação entre Frontend e Backend através de atualizações parciais.

Sua adoção encontra-se em evolução.

---

## Alpine.js

Biblioteca destinada à implementação de comportamentos leves diretamente nos Templates.

Também se encontra em adoção gradual.

---

# 19. Roadmap

A arquitetura JavaScript foi projetada para evoluir progressivamente, preservando simplicidade e compatibilidade com Django.

---

## Curto Prazo

- Consolidação dos scripts compartilhados;
- Revisão da organização da pasta `static/js`;
- Expansão da documentação técnica;
- Padronização da nomenclatura.

---

## Médio Prazo

- Modularização gradual dos scripts;
- Maior reutilização entre módulos;
- Integração progressiva com HTMX;
- Introdução controlada de Alpine.js para interações leves.

---

## Longo Prazo

- Arquitetura totalmente modular;
- Redução de scripts específicos duplicados;
- Biblioteca oficial de utilitários JavaScript;
- Automatização de validações de qualidade;
- Otimização de carregamento;
- Suporte ampliado a Progressive Web App (PWA).

Toda evolução deverá preservar compatibilidade com os Layouts, Templates e Componentes oficiais do GereIgreja.

---

# 20. Documentos Relacionados

## GereIgreja Frontend Engineering

- README.md
- GFE-01 — Frontend Architecture
- GFE-02 — Estrutura de Pastas
- GFE-03 — Componentes
- GFE-04 — Layouts
- GFE-05 — Templates
- GFE-06 — Assets
- GFE-07 — CSS
- GFE-09 — HTMX
- GFE-10 — Alpine.js
- GFE-11 — Dashboards

---

## Documentação Corporativa

- GereIgreja Design System (GDS)
- GereIgreja Documentation Framework (GDF)
- GereIgreja Quality Framework (GQF)

---

# Conclusão

A arquitetura JavaScript do GereIgreja estabelece os princípios responsáveis pelo comportamento da interface, priorizando simplicidade, reutilização e baixo acoplamento.

A estrutura atual utiliza predominantemente JavaScript nativo (ES6), organizado em scripts compartilhados e específicos, com destaque para o arquivo `dashboard-sidebar.js`, responsável pela infraestrutura de navegação dos Dashboards Premium.

A adoção planejada de HTMX e Alpine.js permitirá evoluir a experiência da interface sem abandonar a filosofia de integração nativa com Django, preservando a clareza arquitetural da plataforma.

Toda evolução deverá seguir os padrões definidos neste documento, mantendo compatibilidade com a Arquitetura Frontend, os Layouts, os Templates, os Assets e o Design System oficial do GereIgreja.

---

# Status do Documento

**Pasta**

```
docs/frontend/
```

**Arquivo**

```
08-JavaScript.md
```

**Código**

```
GFE-JS
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