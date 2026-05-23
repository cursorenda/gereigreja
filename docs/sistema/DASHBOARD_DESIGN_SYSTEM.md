# Dashboard Design System — GereIgreja

**Última Atualização:** 23/05/2026  
**Versão:** v1.12.9+  
**Escopo:** Todos os dashboards internos do sistema

---

## Visão Geral

O Dashboard Design System define os padrões visuais, estruturais e comportamentais para todos os dashboards Premium do GereIgreja. O sistema foi desenvolvido e validado no **Dashboard Financeiro** (v1.12.8) e está disponível como base reutilizável para outros módulos.

### Princípios

1. **Consistência** — mesma experiência visual em todos os dashboards
2. **Hierarquia clara** — separação entre decisão rápida (KPIs) e monitoramento detalhado
3. **Responsividade** — grids adaptáveis, sidebar ocultável
4. **Manutenibilidade** — uma mudança no arquivo base propaga para todos

---

## Arquivos do Sistema

| Arquivo | Tipo | Finalidade |
|---------|------|-----------|
| `static/css/dashboard-base.css` | CSS | Tokens, layout, blocos, botões, badges |
| `static/js/dashboard-sidebar.js` | JS | Toggle parametrizável do menu lateral |
| `templates/dashboard_base.html` | Template Django | Template base para herança |

---

## Como Criar um Novo Dashboard

### 1. Criar o CSS específico do módulo

```css
/* meu-modulo-painel.css */

/* Modo full-width para ESTE dashboard */
html.dash-meu-modulo #layoutSidenav_nav,
body.dash-meu-modulo #layoutSidenav_nav { display: none !important; }

html.dash-meu-modulo #layoutSidenav_content,
body.dash-meu-modulo #layoutSidenav_content {
  margin-left: 0 !important;
  padding-left: 0 !important;
  width: 100% !important;
  min-width: 0;
}
html.dash-meu-modulo #layoutSidenav,
body.dash-meu-modulo #layoutSidenav { width: 100% !important; }
body.sb-nav-fixed.dash-meu-modulo #layoutSidenav #layoutSidenav_content,
body.sb-nav-fixed.dash-meu-modulo #layoutSidenav #layoutSidenav_content:before {
  padding-left: 0 !important;
  margin-left: 0 !important;
}

/* KPIs específicos do módulo */
.mp-kpi-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: .9rem;
}
/* ... */
```

### 2. Criar o template Django

```html
{% extends 'dashboard_base.html' %}
{% load static %}

{# CSS específico do módulo #}
{% block dashboard_css %}
<link rel="stylesheet" href="{% static 'css/meu-modulo-painel.css' %}">
{% endblock %}

{# Chave única de localStorage para este dashboard #}
{% block dashboard_sidebar_key %}'meu_modulo.sidebar_visible'{% endblock %}
{% block dashboard_sidebar_class %}'dash-meu-modulo'{% endblock %}
{% block dashboard_sidebar_init_key %}'meu_modulo.sidebar_visible'{% endblock %}
{% block dashboard_sidebar_init_class %}'dash-meu-modulo'{% endblock %}

{% block dashboard_title %}Meu Dashboard{% endblock %}

{% block dashboard_breadcrumb %}
<li><a href="{% url 'secretaria:dashboard' %}"><i class="fas fa-home me-1"></i>Home</a></li>
<li><a href="{% url 'meu_modulo:painel' %}">Meu Módulo</a></li>
<li><span class="active">Visão Geral</span></li>
{% endblock %}

{% block dashboard_filters %}
<form method="get" class="fp-filters">
  <div class="fp-filter-pill">
    <span class="fp-filter-label">Período</span>
    <select name="periodo" onchange="this.form.submit()">
      <option value="mes">Este mês</option>
      <option value="ano">Este ano</option>
    </select>
  </div>
</form>
{% endblock %}

{% block dashboard_content %}
<div class="fp-macro-grid">
  <div class="fp-block">
    <div class="fp-block-head">
      <span class="fp-block-label"><i class="fas fa-chart-bar"></i> Minha Métrica</span>
      <a href="#" class="fp-block-cta">Ver todos</a>
    </div>
    <!-- conteúdo -->
  </div>
</div>
{% endblock %}
```

---

## Design Tokens (CSS Custom Properties)

### Tokens `--dp-*` (canônicos — usar em novos dashboards)

| Token | Valor | Uso |
|-------|-------|-----|
| `--dp-primary` | `#0D8281` | Cor da marca, botões primários, links |
| `--dp-primary-dk` | `#0A6665` | Hover, estados ativos |
| `--dp-primary-lt` | `#2AA5A4` | Destaque secundário |
| `--dp-primary-bg` | `#DFF4F3` | Fundo suave da marca |
| `--dp-surface` | `#FFFFFF` | Cards, blocos |
| `--dp-bg` | `#F1F5F9` | Fundo da página |
| `--dp-border` | `#E2E8F0` | Bordas, divisores |
| `--dp-text` | `#1E293B` | Texto principal |
| `--dp-muted` | `#64748B` | Labels, texto secundário |
| `--dp-success` | `#10B981` | Valores positivos |
| `--dp-warning` | `#D97706` | Alertas, pendências |
| `--dp-danger` | `#EF4444` | Erros, negativos |
| `--dp-radius` | `16px` | Border-radius de cards |
| `--dp-radius-sm` | `10px` | Border-radius de elementos menores |
| `--dp-shadow` | `0 1px 3px rgba(0,0,0,.06), ...` | Sombra padrão |
| `--dp-shadow-hover` | `0 4px 8px rgba(0,0,0,.07), ...` | Sombra no hover |
| `--dp-trans` | `all .18s cubic-bezier(.4,0,.2,1)` | Transição padrão |

### Aliases `--fp-*` (compatibilidade — Dashboard Financeiro)

O Dashboard Financeiro usa `--fp-*`. Esses tokens são aliases que apontam para `--dp-*`:

```css
--fp-primary: var(--dp-primary);
--fp-surface: var(--dp-surface);
/* etc. */
```

Novos dashboards **devem usar `--dp-*`**. Os aliases `--fp-*` existem apenas para compatibilidade.

---

## Classes CSS de Referência

### Layout

| Classe | Descrição |
|--------|-----------|
| `.fp-page` | Container principal da página (padding, bg, min-height) |
| `.fp-header` | Cabeçalho: título + breadcrumb + filtros |
| `.fp-title-wrap` | Wrapper do título e breadcrumb |
| `.fp-title` | Título principal (`h1`, 1.6rem, 800wt) |
| `.fp-breadcrumb` | Breadcrumb de navegação |
| `.fp-filters` | Container dos filtros |
| `.fp-filter-pill` | Pill de filtro (label + select) |
| `.fp-filter-label` | Rótulo do filtro |
| `.fp-span-full` | `grid-column: 1 / -1` (full-width em grid) |

### Blocos (Cards)

| Classe | Descrição |
|--------|-----------|
| `.fp-block` | Card branco elevado (base para qualquer bloco) |
| `.fp-block-head` | Cabeçalho do bloco (label + CTA) |
| `.fp-block-label` | Rótulo da seção (ícone + texto uppercase) |
| `.fp-block-cta` | Link de ação no cabeçalho |
| `.fp-block-footer` | Rodapé do bloco (botões) |

### Botões

| Classe | Descrição |
|--------|-----------|
| `.fp-btn` | Botão base (inline-flex, 0.75rem, 700wt) |
| `.fp-btn-ghost` | Botão com borda e fundo claro |
| `.fp-btn-prim` | Botão primário (fundo turquesa) |

### Badges

| Classe | Descrição |
|--------|-----------|
| `.fp-badge` | Badge base |
| `.fp-badge-ok` | Verde (sucesso) |
| `.fp-badge-warn` | Amarelo (alerta) |
| `.fp-badge-danger` | Vermelho (erro) |
| `.fp-badge-neutral` | Cinza (neutro) |

### Indicadores de Status (Dots)

| Classe | Descrição |
|--------|-----------|
| `.fp-dot` | Ponto indicador (7×7px, circular) |
| `.fp-dot-prim` | Turquesa |
| `.fp-dot-warn` | Amarelo |
| `.fp-dot-danger` | Vermelho |

### Interface

| Classe | Descrição |
|--------|-----------|
| `.fp-menu-toggle` | Botão toggle do menu lateral |
| `.fp-empty` | Estado vazio (texto centralizado, ícone) |

---

## Sidebar Toggle — Comportamento

### Fluxo Completo

```
Page Load
  ↓
Script anti-FOUC (inline, síncrono)
  └─ localStorage[storageKey] !== '1' → adiciona toggleClass ao <html>/<body>
  └─ Evita flash do menu antes da página renderizar

DOMContentLoaded (dashboard-sidebar.js)
  ↓
Coleta botões #fp-toggle-sidebar e #sidebarToggle
  ↓
Adiciona event listener (click) em cada botão
  ↓
Aplica estado persistido do localStorage
  └─ '1' → sidebar visível → remove toggleClass
  └─ '0' ou null → sidebar oculta → adiciona toggleClass
  └─ null → usa defaultVisible do init()

Clique do usuário
  ↓
toggleFinanceiroSidebar()
  ↓
Inverte estado do toggleClass → persiste no localStorage
  ↓
Atualiza aria-expanded + texto do botão
```

### Script Anti-FOUC (obrigatório no `<head>`)

```html
<script>
(function () {
  var storageKey  = 'meu_modulo.sidebar_visible';
  var toggleClass = 'dash-meu-modulo';
  try {
    if (localStorage.getItem(storageKey) !== '1') {
      document.documentElement.classList.add(toggleClass);
    }
  } catch (e) {
    document.documentElement.classList.add(toggleClass);
  }
})();
</script>
```

> **Por que inline?** O script precisa rodar de forma síncrona, antes do render do body, para evitar o "flash" do menu aparecendo brevemente antes de ser ocultado.

### Inicialização do JS

```javascript
DashboardSidebar.init({
  storageKey:    'meu_modulo.sidebar_visible',  // chave única por dashboard
  toggleClass:   'dash-meu-modulo',             // classe CSS fullwidth
  defaultVisible: false                         // padrão se localStorage vazio
});
```

### Parâmetros de `DashboardSidebar.init()`

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|----------|
| `storageKey` | string | `'dashboard.sidebar_visible'` | Chave no localStorage |
| `toggleClass` | string | `'dash-fullwidth'` | Classe CSS para modo full-width |
| `defaultVisible` | boolean | `false` | Estado padrão sem histórico |
| `labelAttr` | string | `'data-fp-sidebar-label'` | Atributo do span de label do botão |
| `toggleIds` | array | `['fp-toggle-sidebar', 'sidebarToggle']` | IDs dos botões de toggle |

---

## CSS do Modo Full-Width (por dashboard)

Cada dashboard precisa de seu próprio seletor CSS para ocultar o sidebar. Exemplo:

```css
/* Em meu-modulo-painel.css */
html.dash-meu-modulo #layoutSidenav_nav,
body.dash-meu-modulo #layoutSidenav_nav { display: none !important; }

html.dash-meu-modulo #layoutSidenav_content,
body.dash-meu-modulo #layoutSidenav_content {
  margin-left: 0 !important;
  padding-left: 0 !important;
  width: 100% !important;
  min-width: 0;
}
html.dash-meu-modulo #layoutSidenav,
body.dash-meu-modulo #layoutSidenav { width: 100% !important; }
body.sb-nav-fixed.dash-meu-modulo #layoutSidenav #layoutSidenav_content,
body.sb-nav-fixed.dash-meu-modulo #layoutSidenav #layoutSidenav_content:before {
  padding-left: 0 !important;
  margin-left: 0 !important;
}
```

> **Nota:** O `dashboard-base.css` inclui esses seletores para a classe `.dash-fullwidth` (nome canônico). Para cada novo dashboard, copie o padrão acima trocando a classe.

---

## Dashboards Existentes

| Dashboard | CSS Específico | Toggle Class | Storage Key |
|-----------|---------------|--------------|-------------|
| Financeiro | `financeiro-painel.css` | `dash-financeiro` | `financeiro.sidebar_visible` |
| *(Secretaria)* | `secretaria-painel.css` *(a criar)* | `dash-secretaria` | `secretaria.sidebar_visible` |
| *(EBD)* | `escola-biblica-painel.css` *(a criar)* | `dash-ebd` | `ebd.sidebar_visible` |

---

## Checklist para Novos Dashboards

- [ ] Criar `static/css/[modulo]-painel.css` com seletores do modo full-width e KPIs específicos
- [ ] Criar template estendendo `dashboard_base.html`
- [ ] Definir `storageKey` único (ex: `modulo.sidebar_visible`)
- [ ] Definir `toggleClass` único (ex: `dash-modulo`)
- [ ] Sobreescrever blocos: `dashboard_title`, `dashboard_breadcrumb`, `dashboard_content`
- [ ] Usar classes `fp-*` para layout e componentes compartilhados
- [ ] Usar `var(--dp-*)` para tokens de cor/espaçamento
- [ ] Testar toggle sidebar em desktop e mobile
- [ ] Testar persistência entre reloads (localStorage)

---

## Histórico de Versões

| Versão | Data | Mudança |
|--------|------|--------|
| v1.0 | 23/05/2026 | Criação inicial — extraído do Dashboard Financeiro v1.12.8 |
