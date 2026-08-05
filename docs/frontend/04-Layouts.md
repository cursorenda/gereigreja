Pasta:
docs/frontend/

Arquivo:
04-Layouts.md

Documento:
GFE-04

Código:
GFE-LAY

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

# GFE-04 — Arquitetura dos Layouts

> *"Os Layouts representam a espinha dorsal da interface do GereIgreja. Eles estabelecem a estrutura visual da plataforma, padronizam a experiência do usuário e garantem consistência entre todos os módulos do sistema."*

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia dos Layouts
4. Estado Atual da Arquitetura
5. Arquitetura Oficial dos Layouts
6. Separação das Camadas da Interface
7. Hierarquia de Herança
8. Fluxo de Renderização
9. Layouts Oficiais
10. Blocos Oficiais
11. Evidências Arquiteturais
12. Inventário Oficial
13. Especificações Oficiais
14. Boas Práticas
15. Anti-patterns
16. Checklist
17. Glossário
18. Roadmap
19. Documentos Relacionados

---

# 1. Objetivo

Este documento define oficialmente a arquitetura dos Layouts utilizados pelo Frontend do GereIgreja.

Seu objetivo é padronizar a construção das páginas da plataforma, estabelecendo regras para reutilização, herança de templates, organização estrutural e composição da interface.

Este documento serve como referência oficial para todo desenvolvimento relacionado à camada de apresentação.

---

# 2. Escopo

Este documento aplica-se exclusivamente aos Layouts do Frontend.

Inclui:

- Layouts Base;
- Herança de Templates;
- Organização estrutural;
- Fluxo de renderização;
- Blocos reutilizáveis;
- Hierarquia dos Layouts;
- Evidências arquiteturais;
- Inventário oficial.

Não inclui:

- Componentes;
- CSS;
- JavaScript;
- Models;
- Views;
- Banco de Dados.

Esses assuntos são documentados em seus respectivos documentos do GFE.

---

# 3. Filosofia dos Layouts

O GereIgreja adota oficialmente o mecanismo de herança de templates do Django como base arquitetural da interface.

Essa abordagem permite:

- reduzir duplicação de código;
- manter consistência visual;
- facilitar manutenção;
- acelerar desenvolvimento;
- centralizar alterações estruturais.

Cada Layout possui uma responsabilidade claramente definida.

Layouts não devem conter regras de negócio.

Toda lógica de negócio pertence ao Backend.

---

# 4. Estado Atual da Arquitetura

A arquitetura atual utiliza três grandes grupos de Layouts, que representam o modelo oficial de organização da interface da plataforma.

Ainda que a base esteja bem consolidada, o projeto pode conter trechos mais antigos em alguns módulos, especialmente em telas históricas, que estão sendo incorporados progressivamente ao padrão atual.

## Área de Gestão do GereIgreja

Interface utilizada pelos usuários autenticados da plataforma.

Essa camada concentra praticamente todos os módulos administrativos utilizados pelas igrejas.

---

## Administração Técnica (Django Admin)

Interface destinada exclusivamente à administração técnica da aplicação.

Essa estrutura utiliza os Layouts próprios do Django Admin e permanece independente da Área de Gestão.

---

## Área Pública

Interface destinada aos visitantes da plataforma.

Inclui páginas institucionais, landing pages, blog, planos e demais conteúdos públicos.

---

# 5. Arquitetura Oficial dos Layouts

A arquitetura oficial do GereIgreja encontra-se dividida em três estruturas independentes.

## 5.1 Área de Gestão

```
base.html
        │
        ▼
base_com_menu.html
        │
        ▼
dashboard_base.html
        │
        ▼
Templates dos módulos
```

Essa é a principal cadeia de herança utilizada pelas telas autenticadas do sistema.

---

## 5.2 Administração Técnica

```
admin/base_site.html
          │
          ▼
admin/index.html

dashboard_desenvolvedor.html
```

Essa estrutura pertence exclusivamente ao Django Admin.

Ela não compartilha Layouts com a Área de Gestão.

---

## 5.3 Área Pública

```
base_landing.html
        │
        ▼
Landing Pages

Blog

Planos

Contato

Demais páginas públicas
```

---

# 6. Separação das Camadas da Interface

Uma das principais diretrizes arquiteturais do GereIgreja consiste na separação completa entre as interfaces da plataforma.

## 6.1 Área de Gestão

Responsável pela utilização diária do sistema pelas igrejas.

Características:

- autenticação obrigatória;
- menu lateral;
- barra superior;
- dashboards;
- módulos administrativos;
- navegação interna.

Base arquitetural:

```
base.html

↓

base_com_menu.html

↓

dashboard_base.html
```

---

## 6.2 Administração Técnica

Responsável pela administração da plataforma.

Utiliza exclusivamente os templates do Django Admin.

Não herda de:

- base.html;
- base_com_menu.html;
- dashboard_base.html.

Sua arquitetura permanece isolada.

---

## 6.3 Área Pública

Destinada aos visitantes.

Possui identidade própria.

Não compartilha a estrutura visual utilizada na Área de Gestão.

---

# 7. Hierarquia de Herança

O GereIgreja utiliza herança de templates em múltiplos níveis.

Hierarquia oficial:

```
base.html
        │
        ▼
base_com_menu.html
        │
        ▼
dashboard_base.html
        │
        ▼
Template do módulo
```

Exemplo:

```
dashboard_base.html

↓

secretaria/dashboard.html
```

Outro exemplo:

```
dashboard_base.html

↓

financeiro/dashboard.html
```

Essa estratégia garante consistência visual entre todos os módulos.

---

# 8. Fluxo de Renderização

O processo de renderização de uma página ocorre na seguinte sequência:

```
Request

↓

View Django

↓

Template do módulo

↓

dashboard_base.html

↓

base_com_menu.html

↓

base.html

↓

HTML Final
```

Durante esse processo são aplicados:

- herança dos templates;
- blocos (`block`);
- includes;
- partials;
- arquivos CSS;
- arquivos JavaScript.

Essa arquitetura permite alterar toda a estrutura visual do sistema modificando apenas os Layouts base.

---

# 9. Layouts Oficiais

## 9.1 base.html

### Responsabilidade

Representa o Layout base da Área de Gestão.

É responsável por fornecer a infraestrutura mínima compartilhada pelas páginas autenticadas.

### Principais responsabilidades

- estrutura HTML principal;
- carregamento de recursos globais;
- definição dos blocos principais;
- ponto inicial da herança.

---

## 9.2 base_com_menu.html

### Responsabilidade

Representa o Layout oficial utilizado pelas páginas autenticadas.

Herda de:

```
base.html
```

Centraliza:

- menu lateral;
- barra superior;
- estrutura principal da página;
- footer;
- includes globais;
- CSS compartilhado;
- JavaScript compartilhado.

É a principal base dos módulos internos do GereIgreja.

---

## 9.3 dashboard_base.html

### Responsabilidade

Layout especializado para Dashboards.

Herda de:

```
base_com_menu.html
```

Responsabilidades:

- estrutura dos dashboards;
- cabeçalho;
- breadcrumb;
- área de filtros;
- persistência do estado da sidebar;
- integração com DashboardSidebar;
- carregamento de dashboard-base.css;
- inicialização dos scripts específicos dos dashboards.

---

## 9.4 base_landing.html

Responsável pelas páginas públicas da plataforma.

Utilizado para:

- Landing Pages;
- Página inicial;
- Funcionalidades;
- Planos;
- Blog;
- Contato.

---

## 9.5 Layouts da Administração Técnica

A Administração Técnica utiliza a estrutura padrão do Django Admin.

Principais arquivos:

- admin/base_site.html
- admin/index.html
- dashboard_desenvolvedor.html

Esses Layouts não fazem parte da cadeia de herança da Área de Gestão.

---
# 10. Blocos Oficiais

Os Layouts do GereIgreja utilizam o mecanismo oficial de herança de templates do Django através da definição de blocos (`{% block %}`).

Os blocos representam pontos de extensão da interface e permitem que os templates filhos personalizem apenas as regiões necessárias, preservando toda a estrutura arquitetural.

---

## 10.1 Blocos da Área de Gestão

Os layouts da Área de Gestão disponibilizam blocos reutilizáveis para construção das páginas.

Entre os principais blocos utilizados encontram-se:

| Block | Finalidade |
|--------|------------|
| content | Conteúdo principal da página |
| extra_css | Inclusão de CSS adicional |
| extra_js | Inclusão de JavaScript adicional |

Esses blocos representam a base para praticamente todos os módulos autenticados.

---

## 10.2 Blocos do dashboard_base.html

O arquivo `dashboard_base.html` amplia a arquitetura da Área de Gestão adicionando blocos específicos para dashboards.

### dashboard_css

Permite adicionar arquivos CSS específicos do dashboard.

Exemplo:

```django
{% block dashboard_css %}
<link rel="stylesheet" href="{% static 'css/meu-dashboard.css' %}">
{% endblock %}
```

---

### dashboard_title

Define o título principal exibido no cabeçalho.

Exemplo:

```django
{% block dashboard_title %}
Financeiro
{% endblock %}
```

---

### dashboard_breadcrumb

Responsável pela construção do breadcrumb.

Exemplo:

```django
{% block dashboard_breadcrumb %}

<li>
    <a href="{% url 'home' %}">
        Home
    </a>
</li>

<li>
    Financeiro
</li>

{% endblock %}
```

---

### dashboard_filters

Área destinada aos filtros do dashboard.

Seu uso é opcional.

Quando não utilizado, nenhuma área adicional é renderizada.

---

### dashboard_content

Representa o conteúdo principal do dashboard.

É o bloco mais importante do template.

Todo dashboard deverá implementar este bloco.

---

### dashboard_extra_js

Permite incluir JavaScript específico do dashboard.

Os scripts definidos nesse bloco são carregados após os scripts compartilhados.

---

### dashboard_sidebar_key

Define a chave utilizada no Local Storage para persistência da sidebar.

Valor padrão:

```
dashboard.sidebar_visible
```

---

### dashboard_sidebar_class

Classe CSS aplicada quando o menu lateral encontra-se recolhido.

Valor padrão:

```
dash-fullwidth
```

---

### dashboard_sidebar_init_key

Define a chave utilizada pela inicialização do componente DashboardSidebar.

---

### dashboard_sidebar_init_class

Classe utilizada pelo componente DashboardSidebar durante sua inicialização.

---

### dashboard_sidebar_default

Define o estado inicial da Sidebar.

Valor padrão atual:

```
false
```

---

# 11. Evidências Arquiteturais

Este documento foi elaborado com base na arquitetura atualmente implementada no GereIgreja.

As evidências abaixo representam os principais arquivos responsáveis pela infraestrutura dos Layouts.

---

## EA-LAY-001

Arquivo

```
base.html
```

Responsabilidade

Base principal da Área de Gestão.

---

## EA-LAY-002

Arquivo

```
base_com_menu.html
```

Responsabilidade

Layout autenticado.

Herda de:

```
base.html
```

---

## EA-LAY-003

Arquivo

```
dashboard_base.html
```

Responsabilidade

Layout oficial dos Dashboards.

Herda de:

```
base_com_menu.html
```

---

## EA-LAY-004

Arquivo

```
menu.html
```

Responsabilidade

Estrutura do menu lateral utilizada pela Área de Gestão.

---

## EA-LAY-005

Arquivo

```
dashboard-sidebar.js
```

Responsabilidade

Gerenciamento da abertura e fechamento da Sidebar.

Persistência do estado através do Local Storage.

---

## EA-LAY-006

Arquivo

```
dashboard-base.css
```

Responsabilidade

Estilos compartilhados entre os dashboards.

---

## EA-LAY-007

Arquivo

```
admin/base_site.html
```

Responsabilidade

Base da Administração Técnica.

---

## EA-LAY-008

Arquivo

```
admin/index.html
```

Responsabilidade

Página inicial da Administração Técnica.

---

## EA-LAY-009

Arquivo

```
dashboard_desenvolvedor.html
```

Responsabilidade

Dashboard utilizado pela equipe técnica.

---

## EA-LAY-010

Arquivo

```
base_landing.html
```

Responsabilidade

Base oficial das páginas públicas.

---

# 12. Inventário Oficial dos Layouts

## Área de Gestão

### Layouts Base

| Layout | Situação |
|---------|----------|
| base.html | Oficial |
| base_com_menu.html | Oficial |
| dashboard_base.html | Oficial |

---

## Administração Técnica

### Layouts

| Layout | Situação |
|---------|----------|
| admin/base_site.html | Oficial |
| admin/index.html | Oficial |
| dashboard_desenvolvedor.html | Oficial |

---

## Área Pública

### Layouts

| Layout | Situação |
|---------|----------|
| base_landing.html | Oficial |

---

# 13. Especificações Oficiais

As especificações abaixo definem as regras obrigatórias para evolução dos Layouts do GereIgreja.

---

## GFE-LAY-001

Todo Layout deverá possuir responsabilidade única.

---

## GFE-LAY-002

Layouts não deverão conter regras de negócio.

---

## GFE-LAY-003

A reutilização deverá ocorrer através da herança de templates.

---

## GFE-LAY-004

Novos Layouts deverão herdar dos Layouts oficiais sempre que possível.

---

## GFE-LAY-005

Componentes específicos não deverão ser incorporados diretamente aos Layouts.

---

## GFE-LAY-006

Toda alteração estrutural deverá preservar compatibilidade com os módulos existentes.

---

## GFE-LAY-007

Os Layouts da Área de Gestão e da Administração Técnica deverão permanecer independentes.

---

## GFE-LAY-008

Toda nova estrutura deverá ser documentada antes de ser considerada oficial.

---

## GFE-LAY-009

Cards de resumo e blocos equivalentes deverão seguir o padrão responsivo oficial de grid:

- Desktop: 4 colunas (`col-lg-3`);
- Tablet: 2 colunas (`col-sm-6`);
- Mobile: 1 coluna (`col-12`, implícita quando não houver classe menor);
- Espaçamento horizontal/vertical: `g-3` na `row`.

Referência base:

```html
<div class="row g-3">
        <div class="col-sm-6 col-lg-3">...</div>
        <div class="col-sm-6 col-lg-3">...</div>
        <div class="col-sm-6 col-lg-3">...</div>
        <div class="col-sm-6 col-lg-3">...</div>
</div>
```

Variações serão permitidas apenas quando houver justificativa funcional documentada.

---

# 14. Boas Práticas

Durante o desenvolvimento recomenda-se:

- reutilizar Layouts existentes;
- utilizar herança de templates;
- manter blocos pequenos;
- evitar HTML duplicado;
- documentar novos Layouts;
- preservar compatibilidade com o Design System;
- manter separação entre estrutura e regras de negócio;
- utilizar Includes e Partials para reutilização de interface.

---
# 15. Anti-patterns

Os padrões abaixo não fazem parte da arquitetura oficial do GereIgreja e devem ser evitados durante o desenvolvimento.

---

## 15.1 Duplicação de Layouts

Não criar múltiplos Layouts para resolver o mesmo problema.

Quando um Layout existente atender à necessidade, ele deverá ser reutilizado.

---

## 15.2 Regras de Negócio

Layouts representam exclusivamente a estrutura da interface.

Não devem conter:

- validações;
- regras de domínio;
- cálculos;
- decisões de negócio;
- manipulação de dados.

Essas responsabilidades pertencem ao Backend.

---

## 15.3 HTML Duplicado

Regiões reutilizáveis não devem ser copiadas entre páginas.

Utilizar:

- Includes;
- Partials;
- Componentes compartilhados.

---

## 15.4 JavaScript Específico

Layouts não devem conter JavaScript específico de um único módulo.

Scripts específicos deverão ser carregados através dos blocos apropriados.

Exemplo:

```django
{% block dashboard_extra_js %}
{% endblock %}
```

---

## 15.5 CSS Específico

Evitar inserir CSS exclusivo de um módulo diretamente no Layout.

Utilizar:

```django
{% block extra_css %}
```

ou

```django
{% block dashboard_css %}
```

---

## 15.6 Dependência entre Módulos

Um Layout nunca deverá depender de arquivos específicos de um módulo da aplicação.

Layouts representam infraestrutura compartilhada.

---

## 15.7 Mistura entre Interfaces

A Área de Gestão e a Administração Técnica possuem arquiteturas distintas.

Não reutilizar:

- templates do Django Admin dentro da Área de Gestão;
- layouts da Área de Gestão dentro do Django Admin.

Essa separação é uma diretriz oficial da arquitetura.

---

# 16. Checklist

Antes de criar ou alterar um Layout, verificar:

## Arquitetura

- [ ] Existe Layout equivalente?
- [ ] A herança está correta?
- [ ] A alteração impacta outros módulos?

---

## Estrutura

- [ ] A responsabilidade do Layout permanece única?
- [ ] O HTML está organizado?
- [ ] O Layout continua reutilizável?

---

## Blocos

- [ ] Os blocos existentes foram preservados?
- [ ] Foi realmente necessário criar um novo block?
- [ ] O novo block foi documentado?

---

## Compatibilidade

- [ ] Compatível com a Área de Gestão?
- [ ] Compatível com os Dashboards?
- [ ] Compatível com o Design System?

---

## Documentação

- [ ] Evidências atualizadas?
- [ ] Inventário atualizado?
- [ ] Arquitetura preservada?

---

# 17. Glossário

## Administração Técnica

Interface administrativa baseada no Django Admin.

Utilizada exclusivamente para administração técnica da plataforma.

---

## Área de Gestão

Interface principal utilizada pelos usuários autenticados do GereIgreja.

Concentra todos os módulos administrativos utilizados pelas igrejas.

---

## Área Pública

Conjunto de páginas destinadas aos visitantes da plataforma.

Exemplos:

- Página Inicial;
- Funcionalidades;
- Blog;
- Contato;
- Planos.

---

## Layout

Template responsável pela estrutura principal de uma página.

Representa o maior nível de reutilização da interface.

---

## Herança de Templates

Mecanismo do Django utilizado para reutilizar estruturas através da diretiva:

```django
{% extends %}
```

---

## Include

Fragmento reutilizável incorporado através de:

```django
{% include %}
```

---

## Partial

Pequena porção reutilizável da interface.

Pode ser:

- Global;
- Específica de um App.

---

## Dashboard

Página destinada à apresentação de indicadores, métricas e informações analíticas.

No GereIgreja, utiliza oficialmente o layout:

```
dashboard_base.html
```

---

## Sidebar

Menu lateral utilizado pela Área de Gestão.

Seu estado é persistido através do componente `DashboardSidebar` utilizando Local Storage.

---

## Breadcrumb

Estrutura de navegação hierárquica exibida no cabeçalho dos dashboards.

---

# 18. Roadmap

A arquitetura dos Layouts foi projetada para suportar a evolução contínua da plataforma.

As próximas etapas previstas incluem:

## Curto Prazo

- Consolidação da arquitetura atual;
- Padronização completa dos templates;
- Expansão do inventário arquitetural.

---

## Médio Prazo

- Ampliação gradual do uso de HTMX em interfaces compatíveis;
- Introdução gradual de Alpine.js para interações leves;
- Maior reutilização de componentes compartilhados.

---

## Longo Prazo

- Suporte a múltiplos temas;
- White-label;
- Progressive Web App (PWA);
- Evolução para aplicações móveis mantendo a arquitetura atual de templates.

Toda evolução deverá preservar compatibilidade com a arquitetura oficial documentada.

---

# 19. Documentos Relacionados

## GereIgreja Frontend Engineering

- README.md
- GFE-01 — Frontend Architecture
- GFE-02 — Estrutura de Pastas
- GFE-03 — Componentes
- GFE-05 — Templates
- GFE-06 — Assets
- GFE-07 — CSS
- GFE-08 — JavaScript
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

Os Layouts representam a infraestrutura estrutural da interface do GereIgreja.

Toda página da plataforma deve ser construída sobre essa arquitetura, utilizando herança de templates, reutilização de estruturas e separação clara de responsabilidades.

A distinção entre a Área de Gestão, a Administração Técnica (Django Admin) e a Área Pública constitui um princípio arquitetural permanente do projeto e deve ser preservada em todas as evoluções da plataforma.

Os Layouts oficiais estabelecem a base para uma interface consistente, escalável e de fácil manutenção, permitindo que novos módulos sejam desenvolvidos seguindo um padrão único de implementação.

---

# Status do Documento

**Pasta**

```
docs/frontend/
```

**Arquivo**

```
04-Layouts.md
```

**Código**

```
GFE-LAY
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

