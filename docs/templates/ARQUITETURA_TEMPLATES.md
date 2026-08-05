# 📐 Arquitetura de Templates - Gereigreja

> **Última atualização:** 01/05/2026  
> **Versão do sistema:** v1.9.0  
> **Status:** Versão publicada em produção

---

## 📚 Índice

1. [Visão Geral](#visão-geral)
2. [Templates Base Disponíveis](#templates-base-disponíveis)
3. [Quando Usar Cada Template](#quando-usar-cada-template)
4. [Regras de Uso](#regras-de-uso)
5. [Estrutura de Componentes](#estrutura-de-componentes)
6. [Exemplos Práticos](#exemplos-práticos)
7. [Checklist de Validação](#checklist-de-validação)

---

## 🎯 Visão Geral

O Gereigreja utiliza uma **arquitetura de templates modular** baseada em herança do Django, com 4 templates base distintos para diferentes contextos de uso.

### Princípios Fundamentais

1. **Separação de Concerns**: Templates públicos vs autenticados
2. **Consistência Visual**: Cada contexto tem seu layout específico
3. **Principle of Least Privilege**: Não mostrar menus/elementos inacessíveis
4. **Manutenibilidade**: Código reutilizável e DRY

---

## 📄 Templates Base Disponíveis

### 1. `base.html` 🔓
**Uso:** Páginas de autenticação (público)

#### Características:
- ❌ Sem menu lateral (sidebar)
- ❌ Sem topnav com notificações
- ❌ Sem logo do ministério
- ✅ Footer simples (Política, Termos)
- ✅ Layout centralizado (cards)

#### Estrutura:
```html
<div id="layoutAuthentication">
    <div id="layoutAuthentication_content">
        <main>
            {% block content %}{% endblock %}
        </main>
    </div>
    <div id="layoutAuthentication_footer">
        <footer><!-- Footer simples --></footer>
    </div>
</div>
```

#### CSS Específico:
- `css/styles.css` (básico)
- Classes: `.bg-light`, sem `.sb-sidenav`

---

### 2. `base_landing.html` 🌐
**Uso:** Landing page pública (homepage de vendas)

#### Características:
- ❌ Sem autenticação
- ❌ Sem menu lateral
- ✅ Navbar de marketing
- ✅ SEO otimizado (Open Graph, Twitter Cards)
- ✅ Call-to-Actions (CTAs)
- ✅ Footer com redes sociais

#### Estrutura:
```html
<head>
    <!-- SEO Meta Tags -->
    <meta property="og:type" content="website">
    <!-- ... -->
</head>
<body>
    {% block content %}{% endblock %}
</body>
```

#### CSS Específico:
- `css/landing_page.css` (customizado)
- Bootstrap 5.2.3

---

### 3. `base_com_menu.html` 🔐
**Uso:** Área de Gestão do GereIgreja (dashboard, CRUD, relatórios, telas operacionais)

#### Características:
- ✅ **Menu lateral (sidebar)** com navegação completa
- ✅ **Topnav** com notificações, perfil, seletor de igreja
- ✅ **Logo do ministério** na sidebar
- ✅ **Dropdown do usuário** (perfil, configurações, logout)
- ✅ **Footer completo** (versão, links, redes sociais)
- ✅ **Seletor de tamanho de fonte** (acessibilidade)
- ✅ **Responsivo** (offcanvas mobile)
- ✅ **Não faz parte do Django Admin**: a Administração Técnica (Django Admin) utiliza sua própria hierarquia de templates

#### Estrutura:
```html
<div id="layoutSidenav">
    <!-- Sidebar Desktop -->
    <div id="layoutSidenav_nav">
        <nav class="sb-sidenav">
            {% include 'menu.html' %}
        </nav>
    </div>
    
    <!-- Conteúdo Principal -->
    <div id="layoutSidenav_content">
        <main>
            {% block content %}{% endblock %}
        </main>
        <footer><!-- Footer completo --></footer>
    </div>
</div>
```

#### CSS Específico:
- `css/styles.css`
- `css/layout.css`
- `css/menus.css`
- `css/botoes.css`

#### JavaScript:
- Sidebar toggle
- Offcanvas mobile
- Seletor de igreja (AJAX)
- Seletor de fonte (localStorage)

---

### 4. `base_com_sistema.html` ⚙️
**Uso:** Páginas de sistema/admin (não analisado completamente)

#### Status: 🟡 A documentar

---

## 🎯 Quando Usar Cada Template

### 📋 Matriz de Decisão

| Contexto | Template | Critério | Exemplos |
|----------|----------|----------|----------|
| **Usuário não autenticado** | `base.html` | Login, registro, senha | `/login/`, `/contas/registrar/` |
| **Landing page** | `base_landing.html` | Homepage pública | `/`, `/sobre/` |
| **Usuário autenticado** | `base_com_menu.html` | Dashboard, CRUD, admin | `/secretaria/`, `/financeiro/` |
| **Admin Django** | - | Padrão Django | `/admin/` |

---

### ✅ Páginas que DEVEM usar `base.html`

#### Autenticação
- ✅ `login.html` - Login do sistema
- ✅ `registrar.html` - Cadastro de nova conta
- ✅ `aceitar_convite_criar_conta.html` - Aceitar convite

#### Recuperação de Senha
- ✅ `password_reset_form.html` - Solicitar reset
- ✅ `password_reset_done.html` - Confirmação de envio
- ✅ `password_reset_confirm.html` - Definir nova senha
- ✅ `password_reset_complete.html` - Senha redefinida

---

### ✅ Páginas que DEVEM usar `base_com_menu.html`

#### Secretaria
- ✅ `lista_pessoas.html`
- ✅ `criar_membro.html`
- ✅ `editar_membro.html`
- ✅ Todas as views de gestão de membros

#### Financeiro
- ✅ `painel_financeiro.html`
- ✅ Lançamentos, receitas, despesas

#### Eventos
- ✅ `lista_eventos.html`
- ✅ `criar_evento.html`

#### Configurações (Usuário Logado)
- ✅ `meu_perfil.html`
- ✅ `editar_meu_perfil.html`
- ✅ `meus_dados_lgpd.html`
- ✅ `password_change_form.html` ← **Logado**
- ✅ `password_change_done.html` ← **Logado**

#### Liderança
- ✅ `painel_lideranca_secretaria.html`
- ✅ `painel_lideranca_financeiro.html`

---

## 📏 Regras de Uso

### 🔴 Regra 1: Autenticação Determina Template

```python
# ❌ ERRADO
# Página pública usando base_com_menu.html
{% extends 'base_com_menu.html' %}  # registrar.html

# ✅ CORRETO
# Página pública usando base.html
{% extends 'base.html' %}  # registrar.html
```

**Princípio:** Usuário não autenticado NÃO deve ver menu lateral.

---

### 🟡 Regra 2: Alterar Senha (Exceção)

```python
# Alterar Senha (usuário LOGADO)
{% extends 'base_com_menu.html' %}  # ✅ Correto

# Recuperar Senha (usuário NÃO logado)
{% extends 'base.html' %}  # ✅ Correto
```

**Princípio:** Contexto determina template, não a ação.

---

### 🟢 Regra 3: Consistência Visual

```python
# Todas as páginas de autenticação devem ser iguais
/login/                  → base.html
/contas/registrar/        → base.html
/password_reset/          → base.html

# Todas as páginas do sistema devem ser iguais
/secretaria/              → base_com_menu.html
/financeiro/              → base_com_menu.html
/eventos/                 → base_com_menu.html
```

---

## 🔄 Context Processors

### O que são?

**Context Processors** são funções Python que injetam variáveis no contexto de **todos os templates** automaticamente, sem precisar passar manualmente em cada view.

### Context Processors Ativos no Gereigreja

Configurados em `core/settings.py`:

```python
'context_processors': [
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'core.context_processors.deduplicate_assinatura_vencida',
    'core.context_processors.ministerio_context',        # ← Logo do ministério
    'core.context_processors.unread_notifications',
    'core.context_processors.sistema_nome',
],
```

---

### 1️⃣ `ministerio_context` ⭐

**Arquivo:** `core/context_processors.py`

**Propósito:** Adiciona o ministério do usuário ao contexto global.

**Variáveis disponíveis:**
- `ministerio` - Objeto Ministerio do usuário
- `request.ministerio` - Compatibilidade (mesmo objeto)

**Uso nos templates:**
```django
{# Logo no menu lateral #}
{% if ministerio and ministerio.logo %}
    <img src="{{ ministerio.logo.url }}" alt="Logo {{ ministerio.nome_fantasia }}">
{% endif %}

{# Nome no footer #}
Copyright © {{ request.ministerio.nome_fantasia|default:"Gereigreja" }}
```

**Lógica:**
```python
def ministerio_context(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.ministerio:
            return {
                'ministerio': request.user.perfil.ministerio,
                'request': {'ministerio': request.user.perfil.ministerio}
            }
    return {'ministerio': None}
```

**Benefícios:**
- ✅ Logo do ministério aparece em **100% das páginas**
- ✅ Views não precisam passar `ministerio` manualmente
- ✅ Consistência automática

---

### 2️⃣ `unread_notifications`

**Propósito:** Contador de notificações não lidas.

**Variável disponível:**
- `unread_notifications_count` - Inteiro (número de notificações)

**Uso nos templates:**
```django
<a href="{% url 'comunicacao:lista_notificacoes' %}">
    <i class="fas fa-bell"></i>
    {% if unread_notifications_count > 0 %}
        <span class="badge bg-danger">{{ unread_notifications_count }}</span>
    {% endif %}
</a>
```

---

### 3️⃣ `sistema_nome`

**Propósito:** Nome do sistema para uso global.

**Variável disponível:**
- `SISTEMA_NOME` - String ("Gereigreja")

**Uso nos templates:**
```django
<title>{% block title %}{{ SISTEMA_NOME }}{% endblock %}</title>
```

---

### 4️⃣ `deduplicate_assinatura_vencida`

**Propósito:** Remove mensagens duplicadas de assinatura vencida.

**Variável disponível:**
- `messages` - Lista de mensagens tratadas

**Uso automático** no sistema de mensagens do Django.

---

### 📝 Quando Criar um Context Processor?

**Critérios:**

✅ **SIM**, se:
- Variável usada em **70%+ das páginas**
- Dados vêm de **fonte única** (não mudam por página)
- **Independente** de parâmetros de URL
- **Leve** de computar (sem queries pesadas)

❌ **NÃO**, se:
- Dados variam por view/página
- Require parâmetros específicos
- Query pesada (> 100ms)
- Usado apenas em 1-2 páginas

**Exemplo:** `ministerio` é perfeito para context processor porque:
- ✅ Usado em todas as páginas (logo, footer)
- ✅ Vem de `request.user.perfil.ministerio` (sempre o mesmo)
- ✅ Sem parâmetros
- ✅ Acesso ao objeto já em memória (sem query extra)

---

## 🧩 Estrutura de Componentes

### Menu Lateral (`menu.html`)

Incluído sempre em `base_com_menu.html` (sem condicional). As seções internas são condicionais via templatetags de permissão:

```django
{% include 'menu.html' %}
```

#### Seções do Menu:
1. **Principal** — Home, Dashboard. O heading só aparece para superusuários, usuários com ministério inativo ou quem tem acesso ao `dashboard_secretaria`. Fica oculto para Membro Comum.
2. **Minha Conta** — Meu Portal, Meu Perfil, Mural de Avisos. Visível para todo usuário autenticado com ministério ativo (inclusive Membro Comum).
3. **Secretaria** — Pessoas, Cargos, Grupos, Tags, Relatórios
4. **Recepção** — Visitantes
5. **Agenda & Eventos**
6. **Escola Dominical**
7. **Financeiro**
8. **Liderança** (condicional — apenas ministérios com > 1 igreja)
9. **Sistema** — Dashboard Sistema, Novidades, Configurações
10. **Comunicação** — E-mail em Massa, Templates, Mural de Avisos (restrito a gestores)
11. **Suporte** (oculto para Membro Comum)

---

### Topnav (Barra Superior)

Componentes (esquerda → direita):

1. **Logo/Brand** - Link para home
2. **Toggle Sidebar** - Hamburger menu
3. **Seletor de Fonte** - Acessibilidade (4 tamanhos)
4. **Seletor de Igreja** - Multi-tenant (se > 1 igreja)
5. **Notificações** - Sino com badge contador
6. **Dropdown Usuário** - Avatar + nome

---

### Dropdown do Usuário

**Seção 1: Admin Ministerio** (condicional)
- Gerenciar Igrejas
- Meu Ministério
- Notificações Enviadas
- Gerenciar Usuários

**Seção 2: Todos os Usuários autenticados com ministério ativo**
- Meu Portal
- Mural de Avisos (para autenticados)

**Seção 3: Conta**
- Meu Perfil
- Gerenciar Assinatura (apenas Admin Ministerio)
- Alterar Senha
- Meus Dados - LGPD

**Seção 4: Logout**
- Sair (formulário POST + CSRF)

---

## 💻 Exemplos Práticos

### Exemplo 1: Página de Login
```django
{# templates/registration/login.html #}
{% extends 'base.html' %}
{% load static %}

{% block title %}Login - Gereigreja{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-lg-5">
            <div class="card shadow-lg">
                <div class="card-header">
                    <h3>Entrar no Sistema</h3>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        <!-- Campos de login -->
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

### Exemplo 2: Página de Dashboard
```django
{# secretaria/templates/secretaria/dashboard.html #}
{% extends 'base_com_menu.html' %}
{% load static %}

{% block title %}Dashboard - {{ block.super }}{% endblock %}

{% block content %}
<div class="container-fluid px-4">
    <h1 class="mt-4">Dashboard</h1>
    <ol class="breadcrumb mb-4">
        <li class="breadcrumb-item active">Dashboard</li>
    </ol>
    
    <div class="row">
        <!-- Cards de métricas -->
    </div>
</div>
{% endblock %}
```

---

### Exemplo 3: Página de Registro
```django
{# contas/templates/contas/registrar.html #}
{% extends 'base.html' %}  {# ✅ CORRETO #}
{% load static %}

{% block title %}Registrar Nova Conta{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-lg-7">
            <div class="card shadow-lg mt-5">
                <div class="card-header">
                    <h3>Criar Conta</h3>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        <!-- Formulário de registro -->
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## ✅ Checklist de Validação

### Antes de Criar um Novo Template

- [ ] **O usuário estará autenticado?**
  - Sim → `base_com_menu.html`
  - Não → `base.html` ou `base_landing.html`

- [ ] **Precisa de menu lateral?**
  - Sim → `base_com_menu.html`
  - Não → `base.html`

- [ ] **É uma página de marketing/vendas?**
  - Sim → `base_landing.html`
  - Não → Outro template

- [ ] **Precisa de notificações/dropdown usuário?**
  - Sim → `base_com_menu.html`
  - Não → `base.html`

---

### Ao Revisar Templates Existentes

- [ ] Template estende o base correto?
- [ ] Páginas públicas não usam `base_com_menu.html`?
- [ ] Páginas autenticadas usam `base_com_menu.html`?
- [ ] Comentários desnecessários foram removidos?
- [ ] Blocos estão sendo usados corretamente?

---

## 🐛 Problemas Comuns e Soluções

### Problema 1: Menu lateral em página pública

**Sintoma:**
```django
{# contas/templates/contas/registrar.html #}
{% extends 'base_com_menu.html' %}  {# ❌ ERRADO #}
```

**Resultado:** Sidebar visível para usuário não autenticado

**Solução:**
```django
{% extends 'base.html' %}  {# ✅ CORRETO #}
```

---

### Problema 2: Falta de navbar em página autenticada

**Sintoma:**
```django
{# secretaria/templates/secretaria/dashboard.html #}
{% extends 'base.html' %}  {# ❌ ERRADO #}
```

**Resultado:** Dashboard sem menu lateral

**Solução:**
```django
{% extends 'base_com_menu.html' %}  {# ✅ CORRETO #}
```

---

### Problema 3: Inconsistência visual

**Sintoma:** Algumas páginas autenticadas com menu, outras sem

**Solução:** Padronizar TODAS as páginas autenticadas para `base_com_menu.html`

---

## 🔍 Auditoria de Templates

### Comando para Verificar Templates

```bash
# Buscar todos os templates que estendem base_com_menu
grep -r "extends 'base_com_menu.html'" contas/templates/

# Buscar templates que estendem base.html
grep -r "extends 'base.html'" contas/templates/
```

### Templates Auditados (08/03/2026)

#### ✅ CORRETOS:

**Usando `base.html` (público):**
- `login.html`
- `registrar.html` ← Corrigido
- `aceitar_convite_criar_conta.html`
- `password_reset_form.html`
- `password_reset_done.html`
- `password_reset_confirm.html`
- `password_reset_complete.html`

**Usando `base_com_menu.html` (autenticado):**
- `meus_dados.html`
- `historico_consentimentos.html`
- `editar_meu_perfil.html`
- `password_change_form.html`
- `password_change_done.html`
- Todos os templates de secretaria/financeiro/eventos

---

## 📚 Referências

- **Django Templates:** https://docs.djangoproject.com/en/5.2/topics/templates/
- **Bootstrap 5:** https://getbootstrap.com/docs/5.2/
- **Documentação interna:**
  - [GRUPOS_PERMISSOES.md](GRUPOS_PERMISSOES.md)
  - [LGPD_IMPLEMENTACAO.md](LGPD_IMPLEMENTACAO.md)
  - [CHAT_RESPOSTAS.md](../CHAT_RESPOSTAS.md)

---

## 📝 Changelog

### v1.0.0 - 08/03/2026
- ✅ Documentação inicial criada
- ✅ Correção de `registrar.html` (base_com_menu → base)
- ✅ Auditoria completa de templates de autenticação
- ✅ Remoção de comentários desnecessários

---

**Mantido por:** Equipe Gereigreja  
**Última revisão:** 08/03/2026
