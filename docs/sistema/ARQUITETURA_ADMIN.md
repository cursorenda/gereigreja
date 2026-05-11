# Arquitetura do Admin Django — GereIgreja

**Versão:** 1.0.0  
**Última atualização:** 11/05/2026

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Padrão de Modularização (Hub Re-export)](#padrão-de-modularização-hub-re-export)
3. [Estrutura por App](#estrutura-por-app)
4. [Admin Sites Disponíveis](#admin-sites-disponíveis)
5. [Template Admin Customizado](#template-admin-customizado)
6. [Convenções de Código](#convenções-de-código)

---

## 🎯 Visão Geral

O sistema admin do GereIgreja usa Django Admin padrão com customizações:

- **Modularização por domínio:** cada app com 3+ modelos admin tem os modelos divididos em subarchivos semânticos
- **Mixins reutilizáveis:** comportamentos comuns centralizados em `core/admin_mixins.py`
- **Dois admin sites:** `admin.site` (global) e `auditoria_admin_site` (auditoria isolada)
- **Template customizado:** `templates/admin/index.html` com layout orientado a fluxo de trabalho

---

## 🏗️ Padrão de Modularização (Hub Re-export)

Apps com muitos modelos admin são divididos em subarchivos semânticos. O `admin.py` principal funciona como um **hub** que apenas re-exporta as classes dos subarchivos.

### Estrutura do Hub

```python
# meuapp/admin.py  ← Hub (apenas re-exporta)
"""Ponto de entrada do admin do modulo meuapp.

As classes admin estao organizadas em submodulos por dominio:
  - admin_xyz.py : ModeloA, ModeloB
  - admin_abc.py : ModeloC, ModeloD
"""
from .admin_xyz import ModeloAAdmin, ModeloBAdmin  # noqa: F401
from .admin_abc import ModeloCAdmin, ModeloDAdmin  # noqa: F401
```

```python
# meuapp/admin_xyz.py  ← Subarchivo de domínio
from django.contrib import admin
from core.admin_mixins import MixinA
from .models import ModeloA, ModeloB

@admin.register(ModeloA)
class ModeloAAdmin(MixinA, admin.ModelAdmin):
    ...
```

### Por que `# noqa: F401`?

Os imports no hub são "apenas re-exportações" — não são usados diretamente no arquivo. O `# noqa: F401` suprime o aviso de "imported but unused" dos linters.

### Por que Django ainda auto-descobre?

O `AppConfig.ready()` do Django faz `autodiscover_modules('admin')`, que carrega o `admin.py` de cada app. O hub importa os subarchivos, que por sua vez registram os models via `@admin.register`. A cadeia funciona automaticamente.

---

## 🗂️ Estrutura por App

### Apps Modularizados (Hub + Subarchivos)

| App | Hub | Subarchivos |
|-----|-----|-------------|
| `configuracao` | `admin.py` | `admin_ministerio.py`, `admin_planos.py`, `admin_sistema.py` |
| `secretaria` | `admin.py` | `admin_membros.py`, `admin_grupos.py`, `admin_cargos.py` |
| `financeiro` | `admin.py` | `admin_contas.py`, `admin_movimentacao.py`, `admin_catalogo.py` |
| `escola_biblica` | `admin.py` | `admin_estrutura.py`, `admin_alunos.py`, `admin_aulas.py` |
| `comunicacao` | `admin.py` | `admin_avisos.py`, `admin_whatsapp.py` |
| `contas` | `admin.py` | `admin_contas.py` |

### Apps com Admin Simples (arquivo único)

| App | Arquivo | Classes |
|-----|---------|---------|
| `agenda` | `admin.py` | `AgendaEventoAdmin` |
| `auditoria` | `admin.py` | `UserAuditAdmin`, `PermissionChangeLogAdmin`, `AccessDeniedLogAdmin`, `AuditSessionAdmin` |
| `eventos` | `admin.py` | `EventoAdmin`, `ParticipacaoEventoAdmin` |
| `suporte` | `admin.py` | `TicketAdmin`, `RespostaTicketInline` |
| `notificacoes` | `admin.py` | `NotificacaoAdmin`, `NotificacaoEnviadaAdmin` |
| `deploy` | `admin.py` | `DeployHistoricoAdmin` |
| `blog` | `admin.py` | `CategoriaAdmin`, `PostAdmin` |

---

## 🔐 Admin Sites Disponíveis

### 1. `admin.site` — Admin Global

- **URL:** `/admin/`
- **Acesso:** `is_staff=True` + permissões de grupo
- **Contém:** Todos os modelos do sistema
- **Registro:** Via decorador `@admin.register(Modelo)` ou `admin.site.register(Modelo, ClasseAdmin)`

### 2. `auditoria_admin_site` — Admin de Auditoria

- **URL:** `/admin-auditoria/`
- **Arquivo:** `auditoria/admin_site.py`
- **Acesso:** Restrito (superusuários e equipe técnica)
- **Contém:** Apenas modelos de auditoria (logs de acesso, mudanças de permissão, sessões)
- **Propósito:** Interface isolada para revisão de trilhas de auditoria

> ⚠️ **Importante:** O registro do modelo `User` fica exclusivamente em `configuracao/admin_ministerio.py` (no `admin.site` global). O `auditoria_admin_site` **não** registra `User` para evitar conflito de `AlreadyRegistered`.

---

## 🖥️ Template Admin Customizado

### `templates/admin/index.html` — Dashboard

Layout de 2 colunas responsivo:
- **Sidebar** (286px, sticky): Navegação rápida com 3 seções por fluxo de trabalho:
  - 🔧 **Operação Diária:** membros, finanças, agenda, EBD, eventos
  - 📊 **Monitoramento:** auditoria, suporte, notificações, deploy
  - ⚙️ **Engenharia:** configuração, planos, sistema, validações
- **Conteúdo principal:** Dashboard de métricas com Chart.js (crescimento, engajamento, qualidade de dados)

### `templates/admin/base_site.html` — Base Global

- Painel de filtros recolhível com persistência via `localStorage`
- Chave: `admin_filters_hidden`
- Comportamento padrão: filtros ocultos na primeira visita

---

## 📏 Convenções de Código

### Nomenclatura de Arquivos

```
admin.py              ← Hub ou arquivo único (apps simples)
admin_<dominio>.py    ← Subarchivo de domínio
```

Exemplos de domínios: `membros`, `grupos`, `cargos`, `planos`, `ministerio`, `sistema`, `contas`, `movimentacao`, `catalogo`, `estrutura`, `alunos`, `aulas`, `avisos`, `whatsapp`

### Nomenclatura de Classes

```python
class <Modelo>Admin(Mixin1, Mixin2, admin.ModelAdmin):
```

### Ordem de Herança

```python
class MinhaAdmin(
    MixinEspecifico,   # 1. Mais específico primeiro
    MixinGenerico,     # 2. Depois os genéricos
    admin.ModelAdmin   # 3. Sempre por último
):
```

### Imports

```python
# 1. Django
from django.contrib import admin

# 2. Mixins internos
from core.admin_mixins import MinisterioFilteredMixin, DateHierarchyMixin

# 3. Models do mesmo app
from .models import MeuModelo
```

### Override de Campos de Mixin

Quando o campo do modelo difere do padrão do mixin, declare explicitamente na classe com comentário:

```python
class TicketAdmin(DateHierarchyMixin, admin.ModelAdmin):
    date_hierarchy = 'data_criacao'  # Override mixin default
```

---

## 📚 Documentação Relacionada

- [ADMIN_MIXINS.md](ADMIN_MIXINS.md) — Referência de todos os mixins disponíveis
- [GRUPOS_PERMISSOES.md](GRUPOS_PERMISSOES.md) — Grupos e permissões do sistema
- [DECORATORS_SEGURANCA.md](DECORATORS_SEGURANCA.md) — Decorators de segurança e autenticação
