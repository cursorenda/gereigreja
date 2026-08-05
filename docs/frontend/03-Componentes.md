---
Documento: GFE-03
Código: GFE-CMP
Título: Componentes do Frontend
Seção: Frontend Engineering
Versão: 3.0
Status: Oficial
Responsável: Equipe de Engenharia
Última atualização: Agosto de 2026
---

# GFE-03 — Componentes do Frontend

> "A arquitetura de componentes do GereIgreja privilegia reutilização, baixo acoplamento e padronização. Todo componente deve possuir uma responsabilidade clara e integrar-se naturalmente à arquitetura oficial do Frontend."

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia da Componentização
4. Estado Atual
5. Classificação Oficial dos Componentes
6. Layouts
7. Includes
8. Partials
9. Componentes Estruturais
10. Componentes Funcionais
11. Componentes por App
12. Evidências Arquiteturais
13. Inventário Oficial
14. Especificações Oficiais
15. Boas Práticas
16. Checklist
17. Roadmap
18. Documentos Relacionados

---

# 1. Objetivo

Este documento define a arquitetura oficial de componentes utilizada pelo Frontend do GereIgreja.

Seu objetivo é padronizar o desenvolvimento da interface da plataforma, promovendo reutilização, consistência visual, baixo acoplamento e facilidade de manutenção.

Todos os componentes reutilizáveis da interface devem seguir as diretrizes estabelecidas neste documento.

---

# 2. Escopo

Este documento aplica-se aos componentes utilizados na camada de apresentação.

Inclui:

- Layouts;
- Includes;
- Partials;
- Componentes estruturais;
- Componentes funcionais;
- Componentes específicos de domínio.

Não inclui:

- CSS;
- JavaScript;
- Assets;
- Models;
- Services;
- Banco de Dados.

---

# 3. Filosofia da Componentização

O GereIgreja utiliza Django Templates como mecanismo oficial de renderização da interface.

A reutilização da camada de apresentação é baseada principalmente em:

- herança de templates (`extends`);
- inclusão de fragmentos (`include`);
- layouts especializados;
- partials reutilizáveis.

Essa abordagem reduz duplicação de código, facilita manutenção e garante consistência entre os módulos.

---

# 4. Estado Atual

Atualmente o projeto **não possui uma pasta `components`**.

A componentização é realizada por meio de:

- Layouts;
- Includes;
- Partials.

Além da estrutura compartilhada, alguns Apps possuem componentes próprios quando representam funcionalidades específicas do domínio. Esse modelo é o padrão oficial, mas o projeto ainda pode apresentar variações locais em módulos mais antigos, que devem ser tratados como evolução gradual.

---

# 5. Classificação Oficial dos Componentes

Os componentes do Frontend são classificados em cinco categorias.

## 5.1 Layouts

Estruturas base responsáveis pela composição das páginas.

Exemplos:

- `base.html`
- `base_com_menu.html`
- `dashboard_base.html`

---

## 5.2 Includes

Fragmentos compartilhados de infraestrutura da interface.

Exemplos conhecidos:

- `app_footer.html`
- `auth_footer.html`
- `public_footer.html`
- `footer_social_links.html`

---

## 5.3 Partials

Fragmentos reutilizáveis de interface.

Existem dois modelos oficiais:

### Partials Globais

```
templates/partials/
```

### Partials por App

```
<app>/templates/.../partials/
```

---

## 5.4 Componentes Estruturais

Responsáveis pela organização da interface.

Exemplos:

- Sidebar;
- Navbar;
- Breadcrumb;
- Footer;
- Header.

---

## 5.5 Componentes Funcionais

Responsáveis pelas funcionalidades da interface.

Exemplos:

- Cards;
- Dashboards;
- Formulários;
- Tabelas;
- Modais;
- Alertas;
- Paginação.

---

# 6. Layouts

Os Layouts representam o maior nível de reutilização da interface.

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
Templates dos módulos
```

---

# 7. Includes

Os Includes concentram infraestrutura compartilhada.

Características:

- reutilizáveis;
- independentes do domínio de negócio;
- carregados através de `{% include %}`.

Não devem conter regras de negócio.

---

# 8. Partials

Os Partials representam pequenos fragmentos reutilizáveis.

Modelo oficial:

- Partials Globais;
- Partials específicos de App.

Quando um Partial passar a ser utilizado por vários módulos, recomenda-se sua migração para o diretório global.

---

# 9. Componentes Estruturais

Os componentes estruturais organizam a navegação da plataforma.

Incluem:

- Menu lateral;
- Barra superior;
- Breadcrumb;
- Footer;
- Containers;
- Cabeçalhos.

---

# 10. Componentes Funcionais

São utilizados diretamente pelas funcionalidades dos módulos.

Exemplos:

- Cards;
- Dashboards;
- Formulários;
- Tabelas;
- Modais;
- Widgets;
- Indicadores.

---

# 11. Componentes por App

Cada módulo pode possuir componentes próprios.

Esses componentes representam funcionalidades específicas do domínio e não devem ser reutilizados por outros Apps sem avaliação arquitetural.

---

# 12. Evidências Arquiteturais

## EA-CMP-001

**Arquivo**

`templates/base.html`

**Responsabilidade**

Base principal da Área de Gestão do GereIgreja.

---

## EA-CMP-002

**Arquivo**

`templates/base_com_menu.html`

**Responsabilidade**

Layout principal da interface autenticada.

Herda de:

`base.html`

---

## EA-CMP-003

**Arquivo**

`templates/dashboard_base.html`

**Responsabilidade**

Layout base para dashboards premium.

Herda de:

`base_com_menu.html`

---

## EA-CMP-004

**Diretório**

`templates/includes/`

Infraestrutura compartilhada da interface.

---

## EA-CMP-005

**Diretório**

`templates/partials/`

Partials compartilhados.

---

## EA-CMP-006

**Diretórios**

`*/templates/*/partials/`

Partials específicos dos Apps.

---

# 13. Inventário Oficial

## Templates Base

| Arquivo | Função |
|---------|--------|
| base.html | Base principal da Área de Gestão |
| base_com_menu.html | Interface autenticada |
| dashboard_base.html | Base dos dashboards |

### Includes

Atualmente identificados:

- app_footer.html
- auth_footer.html
- public_footer.html
- footer_social_links.html

### Partials Globais

Atualmente identificados:

- _aba_acesso_sistema.html
- _aba_acompanhamento_visita.html
- _aba_cargos.html
- _aba_contribuicoes.html
- _aba_dados_cadastrais.html
- _aba_tipo_status.html
- _form_dados_cadastrais.html
- _form_fields.html
- _form_membro_oficial.html
- _form_pessoa_oficial.html

### Partials por App

Existem diretórios específicos de `partials` em alguns módulos da plataforma.

Esses componentes representam funcionalidades exclusivas de seus respectivos domínios.

---

# 14. Especificações Oficiais

### GFE-CMP-001

Todo componente deve possuir responsabilidade única.

### GFE-CMP-002

Includes não devem conter regras de negócio.

### GFE-CMP-003

Partials reutilizáveis devem permanecer preferencialmente centralizados.

### GFE-CMP-004

Layouts não devem conter lógica específica de módulos.

### GFE-CMP-005

Componentes específicos devem permanecer dentro do respectivo App.

### GFE-CMP-006

Antes da criação de um novo componente, deve-se verificar se já existe solução equivalente na plataforma.

### GFE-CMP-007

Alterações em componentes compartilhados devem considerar todos os módulos consumidores.

---

# 15. Boas Práticas

- Priorizar reutilização.
- Evitar duplicação de código.
- Utilizar nomenclatura consistente.
- Documentar componentes compartilhados.
- Manter a lógica de negócio fora dos templates.
- Seguir o GereIgreja Design System.

---

# 16. Checklist

Antes de criar um novo componente:

- [ ] Existe componente equivalente?
- [ ] Pode ser reutilizado?
- [ ] Deve ser global?
- [ ] Deve permanecer no App?
- [ ] Está documentado?
- [ ] Está alinhado ao Design System?

---

# 17. Roadmap

A arquitetura continuará baseada em Django Templates.

HTMX e Alpine.js poderão ser adotados gradualmente em novos componentes, preservando compatibilidade com a estrutura existente.

---

# 18. Documentos Relacionados

- README.md
- GFE-01 — Frontend Architecture
- GFE-02 — Estrutura de Pastas
- GFE-04 — Layouts
- GFE-05 — Templates
- GereIgreja Design System (GDS)
- GereIgreja Documentation Framework (GDF)
- GereIgreja Quality Framework (GQF)

# 19. Fluxo de Composição dos Componentes

A interface do GereIgreja é construída de forma hierárquica.

A composição de uma página segue o fluxo abaixo:

View Django

↓

Template do módulo

↓

Layout Base

↓

Includes

↓

Partials

↓

HTML Final

View

↓

secretaria/membros/lista.html

↓

dashboard_base.html

↓

base_com_menu.html

↓

base.html

↓

menu.html

↓

app_footer.html

↓

HTML

# 20. Ciclo de Vida de um Componente

Todo componente deverá seguir o ciclo abaixo.

Planejamento

↓

Desenvolvimento

↓

Documentação

↓

Validação

↓

Reutilização

↓

Evolução

↓

Descontinuação (quando necessário)

# 21. Critérios para Criação de Novos Componentes

Antes da criação de um componente deve-se responder:

Existe componente semelhante?

Pode ser reutilizado?

É específico do domínio?

Será utilizado por outros Apps?

Deve permanecer no diretório global?

Necessita documentação?

# 22. Promoção de Componentes

Um componente criado dentro de um App poderá ser promovido para componente compartilhado quando:

for utilizado por dois ou mais módulos;

não possuir regras específicas de domínio;

representar um padrão recorrente da plataforma;

reduzir duplicação de código.

# 23. Componentes Não Permitidos

Não deverão existir:

HTML duplicado em múltiplos módulos;

Includes contendo regras de negócio;

Partials dependentes de um único módulo armazenados como globais;

Layouts específicos de um App utilizados como Layout global;

Componentes sem documentação mínima.

# Glossário

Layout

Estrutura principal reutilizável de uma página.

Include

Fragmento compartilhado incorporado através da tag {% include %}.

Partial

Fragmento reutilizável de interface.

Template Base

Template responsável pela infraestrutura de renderização.

Dashboard

Layout especializado para páginas analíticas.

Área de Gestão

Interface utilizada pelos usuários autenticados.

Administração Técnica

Interface administrativa baseada no Django Admin.

