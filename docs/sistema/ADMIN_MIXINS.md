# Admin Mixins — GereIgreja

**Versão:** 1.0.0  
**Última atualização:** 11/05/2026  
**Arquivo de origem:** `core/admin_mixins.py`

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Mixins Disponíveis](#mixins-disponíveis)
3. [Padrão de Uso](#padrão-de-uso)
4. [Combinações Recomendadas](#combinações-recomendadas)
5. [Override de Campos](#override-de-campos)
6. [Aplicação por App](#aplicação-por-app)

---

## 🎯 Visão Geral

Os admin mixins centralizam comportamentos repetitivos das classes `ModelAdmin` em um único arquivo (`core/admin_mixins.py`), reduzindo duplicação e garantindo consistência em todo o sistema administrativo Django.

**Benefícios:**
- ✅ Redução de ~35% de código duplicado nas classes admin
- ✅ Comportamento uniforme (filtros, read-only, hierarquias)
- ✅ Fácil manutenção: mudar comportamento em 1 lugar reflete em todos os apps
- ✅ Testabilidade isolada

**Princípio de uso:**

```python
@admin.register(MeuModelo)
class MeuModeloAdmin(MixinA, MixinB, admin.ModelAdmin):
    list_display = (...)
```

> ⚠️ **Ordem importa:** Mixins devem vir **antes** de `admin.ModelAdmin` na herança. Mixins mais específicos vêm antes dos mais genéricos.

---

## 🧩 Mixins Disponíveis

### 1. `ReadOnlyAdminMixin`

Desabilita criação, edição e deleção — apenas visualização.

```python
class ReadOnlyAdminMixin:
    has_add_permission    → False
    has_change_permission → True  (exibe os dados)
    has_delete_permission → False
```

**Uso ideal:** Logs de auditoria, registros históricos imutáveis.

---

### 2. `NoAddDeleteMixin`

Permite edição, mas bloqueia criação e deleção.

```python
class NoAddDeleteMixin:
    has_add_permission    → False
    has_delete_permission → False
```

**Uso ideal:** Configurações criadas via código/fixtures, gerenciadas pelo sistema.

---

### 3. `SuperuserOnlyMixin`

Restringe todas as operações exclusivamente a superusuários.

```python
class SuperuserOnlyMixin:
    has_view_permission   → request.user.is_superuser
    has_add_permission    → request.user.is_superuser
    has_change_permission → request.user.is_superuser
    has_delete_permission → request.user.is_superuser
```

**Uso ideal:** Modelos sensíveis como planos, assinaturas, configurações de sistema.

---

### 4. `TimestampReadOnlyMixin`

Torna `criado_em` e `atualizado_em` somente leitura.

```python
class TimestampReadOnlyMixin:
    readonly_fields = ('criado_em', 'atualizado_em')
```

**Uso ideal:** Qualquer modelo com timestamps automáticos de criação/atualização.

---

### 5. `MinisterioFilteredMixin`

Filtra o queryset pelo ministério do usuário logado. Superusuários veem tudo.

```python
def get_queryset(self, request):
    if request.user.is_superuser:
        return qs  # vê todos
    ministerio = request.user.profile.ministerio
    return qs.filter(ministerio=ministerio)
```

**Uso ideal:** Receitas, despesas, avisos, WhatsApp — qualquer dado com campo `ministerio`.

---

### 6. `IgrejaFilteredMixin`

Filtra o queryset pelas igrejas permitidas do usuário. Superusuários veem tudo.

```python
def get_queryset(self, request):
    if request.user.is_superuser:
        return qs  # vê todas
    igrejas = request.user.profile.igrejas_permitidas.all()
    return qs.filter(igreja__in=igrejas)
```

**Uso ideal:** Dados com escopo de igreja específica.

---

### 7. `DateHierarchyMixin`

Adiciona navegação hierárquica pelo campo `criado_em`.

```python
class DateHierarchyMixin:
    date_hierarchy = 'criado_em'
```

**Override:** Se o modelo usa campo diferente, declare na subclasse:
```python
class ConsentimentoLGPDAdmin(DateHierarchyMixin, admin.ModelAdmin):
    date_hierarchy = 'data_consentimento'  # sobrescreve mixin
```

---

### 8. `DataInicioHierarchyMixin`

Hierarquia por `data_inicio` — para modelos de eventos e agendamentos.

```python
class DataInicioHierarchyMixin:
    date_hierarchy = 'data_inicio'
```

---

### 9. `DataTransicaoHierarchyMixin`

Hierarquia por `data_transicao` — para modelos de histórico de mudanças.

```python
class DataTransicaoHierarchyMixin:
    date_hierarchy = 'data_transicao'
```

---

### 10. `DataHierarchyMixin`

Hierarquia por `data` — para registros de movimentação financeira.

```python
class DataHierarchyMixin:
    date_hierarchy = 'data'
```

---

### 11. `AuditoriaTimestampMixin` _(composto)_

Combina `TimestampReadOnlyMixin` + `ReadOnlyAdminMixin`.

```python
class AuditoriaTimestampMixin(TimestampReadOnlyMixin, ReadOnlyAdminMixin):
    pass
```

**Uso ideal:** Logs internos do sistema, eventos de funil, histórico de ações.

---

### 12. `TenantFilteredAuditMixin` _(composto)_

Combina `MinisterioFilteredMixin` + `AuditoriaTimestampMixin`.

```python
class TenantFilteredAuditMixin(MinisterioFilteredMixin, AuditoriaTimestampMixin):
    pass
```

**Uso ideal:** Logs por ministério que devem ser read-only e filtrados por tenant.

---

## 📖 Padrão de Uso

### Importação

```python
from core.admin_mixins import (
    ReadOnlyAdminMixin,
    MinisterioFilteredMixin,
    DateHierarchyMixin,
    # ...
)
```

### Exemplo Completo

```python
from django.contrib import admin
from core.admin_mixins import MinisterioFilteredMixin, DateHierarchyMixin
from .models import Receitas

@admin.register(Receitas)
class ReceitasAdmin(MinisterioFilteredMixin, DateHierarchyMixin, admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'data', 'ministerio')
    list_filter = ('ministerio', 'categoria')
    search_fields = ('descricao',)
    # date_hierarchy = 'data' ← herdado do DataHierarchyMixin
```

---

## 🔗 Combinações Recomendadas

| Cenário | Mixins |
|---------|--------|
| Log de auditoria imutável | `ReadOnlyAdminMixin` + `DateHierarchyMixin` |
| Movimentação financeira | `MinisterioFilteredMixin` + `DataHierarchyMixin` |
| Aviso/notificação | `MinisterioFilteredMixin` + `TimestampReadOnlyMixin` |
| Histórico de membros | `DataTransicaoHierarchyMixin` |
| Evento/agenda | `DataInicioHierarchyMixin` |
| Configuração sensível | `SuperuserOnlyMixin` |
| Dado por ministério + auditado | `TenantFilteredAuditMixin` |

---

## 🔧 Override de Campos

Campos declarados nos mixins são atributos de classe — sempre podem ser sobrescritos:

```python
# Mixin define: date_hierarchy = 'criado_em'
# Seu modelo usa: 'data_consentimento'

class ConsentimentoLGPDAdmin(DateHierarchyMixin, admin.ModelAdmin):
    date_hierarchy = 'data_consentimento'  # ← sobrescreve sem quebrar o mixin
```

O mesmo vale para `readonly_fields`:

```python
class MeuAdmin(TimestampReadOnlyMixin, admin.ModelAdmin):
    readonly_fields = ('criado_em', 'atualizado_em', 'campo_extra')
    # ← estende, não usa o mixin diretamente; declare tudo que for necessário
```

---

## 🗂️ Aplicação por App

| App | Arquivo | AdminClasses com Mixin | Mixins Aplicados |
|-----|---------|----------------------|-----------------|
| auditoria | `admin.py` | PermissionChangeLogAdmin, AccessDeniedLogAdmin, AuditSessionAdmin | `ReadOnlyAdminMixin`, `DateHierarchyMixin` |
| financeiro | `admin_movimentacao.py` | ReceitasAdmin, DespesasAdmin, FechamentoCaixaAdmin | `MinisterioFilteredMixin`, `DataHierarchyMixin` |
| secretaria | `admin_membros.py` | StatusHistoricoAdmin | `DataTransicaoHierarchyMixin` |
| comunicacao | `admin_avisos.py` | AvisoAdmin | `MinisterioFilteredMixin`, `TimestampReadOnlyMixin` |
| comunicacao | `admin_whatsapp.py` | WhatsAppMensagemLogAdmin | `MinisterioFilteredMixin`, `DateHierarchyMixin` |
| contas | `admin_contas.py` | ConviteAdmin, NotaUsuarioAdmin | `DateHierarchyMixin` |
| contas | `admin_contas.py` | ConsentimentoLGPDAdmin | `ReadOnlyAdminMixin` + override `date_hierarchy` |
| eventos | `admin.py` | EventoAdmin | `DataInicioHierarchyMixin` |
| agenda | `admin.py` | AgendaEventoAdmin | `DataInicioHierarchyMixin` |
| escola_biblica | `admin_aulas.py` | LicaoAdmin | `DataHierarchyMixin` |
| suporte | `admin.py` | TicketAdmin | `DateHierarchyMixin` + override |
| notificacoes | `admin.py` | NotificacaoEnviadaAdmin | `DateHierarchyMixin` + override |
| deploy | `admin.py` | DeployHistoricoAdmin | `DateHierarchyMixin` + override |

---

## 📚 Documentação Relacionada

- [ARQUITETURA_ADMIN.md](ARQUITETURA_ADMIN.md) — Estrutura modular do sistema admin
- [GRUPOS_PERMISSOES.md](GRUPOS_PERMISSOES.md) — Grupos e permissões do sistema
- [AUDITORIA_PERMISSOES_SISTEMA_COMPLETO.md](AUDITORIA_PERMISSOES_SISTEMA_COMPLETO.md) — Auditoria completa de permissões
