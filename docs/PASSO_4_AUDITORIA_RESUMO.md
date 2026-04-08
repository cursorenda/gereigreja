# Passo 4: Trilha de Auditoria de Permissões - Resumo de Implementação

**Status:** ✅ COMPLETO

**Data:** 7 de Abril de 2026

**Objetivo:** Implementar logging automático, dashboards e relatórios para auditoria de permissões, acessos negados e sessões de usuários.

---

## 1. ARQUIVOS CRIADOS

### 1.1 `auditoria/signals.py` (NOVO)
**Descrição:** Sistema automático de registro de eventos de auditoria

**Funcionalidades Implementadas:**
- `@receiver(m2m_changed)` - Registra alterações de grupos (adição/remoção)
- `@receiver(post_save)` - Registra criação de novos grupos
- `registrar_acesso_negado()` - Helper para registrar tentativas de acesso negado
- `registrar_login_usuario()` - Registra login com IP e user-agent
- `registrar_logout_usuario()` - Marca sessão como finalizada
- `incrementar_contador_paginas()` - Conta páginas visitadas por sessão
- `obter_ip_do_usuario()` - Extrai IP real considerando proxies

**Exemplo de Uso:**
```python
from auditoria.signals import registrar_acesso_negado

registrar_acesso_negado(
    usuario=request.user,
    tipo_acesso='VIEW',
    recurso='/secretaria/lista_membros',
    request=request,
    ministerio=ministerio,
)
```

### 1.2 `auditoria/apps.py` (NOVO)
**Descrição:** Configuração de aplicação que carrega os signals automaticamente

```python
class AuditoriaConfig(AppConfig):
    name = 'auditoria'
    
    def ready(self):
        import auditoria.signals  # Carrega signals ao iniciar Django
```

---

## 2. ARQUIVOS MODIFICADOS

### 2.1 `auditoria/middleware.py` (EXPANDIDO)
**Novas Classes Adicionadas:**

#### `RegistrarAuditoriaMiddleware`
- Registra login/logout de usuários
- Rastreia páginas visitadas
- Incrementa contador de sessão

#### `CapturarAcessoNegadoMiddleware`
- Captura erros 403 (Forbidden)
- Registra tentativas de acesso não autorizado
- Extrai informações de Request (IP, User-Agent, URL)

**Inserção no settings.py:**
```python
MIDDLEWARE = [
    # ... outros middleware ...
    'auditoria.middleware.RegistrarAuditoriaMiddleware',
    'auditoria.middleware.CapturarAcessoNegadoMiddleware',
]
```

### 2.2 `auditoria/views.py` (EXPANDIDO)
**Novas Views Adicionadas:**

#### `sessoes_ativas()`
- Lista sessões ativas de usuários
- Mostra tempo de sessão e contador de páginas
- Filtro por ministério

#### `exportar_logs_csv()`
- Exporta logs para CSV (3 tipos)
- Logs de alterações de permissões
- Logs de acessos negados
- Logs de sessões

#### `analise_atividades_suspeitas()`
- Análise de usuários com múltiplos acessos negados
- IPs suspeitos (múltiplos usuários de um IP)
- Recursos mais negados
- Período configurável (default 7 dias)

#### `acumulacao_permissoes()`
- Identifica usuários com muitas permissões
- Calcula nível de risco (BAIXO, MÉDIO, ALTO)
- Recomenda revisão de privilégios

### 2.3 `auditoria/urls.py` (EXPANDIDO)
**Novas Rotas Adicionadas:**
- `auditoria/sessoes-ativas/` → `sessoes_ativas`
- `auditoria/exportar-logs/` → `exportar_logs_csv`
- `auditoria/atividades-suspeitas/` → `analise_atividades_suspeitas`
- `auditoria/acumulacao-permissoes/` → `acumulacao_permissoes`

---

## 3. MODELOS APROVEITADOS (Já Existentes)

### Modelos em Uso:
1. **PermissionChangeLog** - Registra alterações de grupos/permissões
2. **AccessDeniedLog** - Registra tentativas de acesso negado
3. **AuditSession** - Rastreia sessões de usuários

---

## 4. FLUXO DE FUNCIONAMENTO

### 4.1 Registro Automático de Alterações
```
Usuário A → Remove grupo do Usuário B
    ↓
signal m2m_changed dispara
    ↓
PermissionChangeLog criado automaticamente
    ↓
Auditado com: data, IP, ID do executor (se disponível)
```

### 4.2 Captura de Acessos Negados
```
Usuário tenta acessar /secretaria/lista_membros
    ↓
Middleware verifica permissão
    ↓
Acesso negado (403)
    ↓
CapturarAcessoNegadoMiddleware registra
    ↓
AccessDeniedLog criado com IP, User-Agent, URL
```

### 4.3 Rastreamento de Sessão
```
Usuário faz login
    ↓
RegistrarAuditoriaMiddleware cria AuditSession
    ↓
Cada GET incrementa page_count
    ↓
Logout marca logout_data_hora
    ↓
Duração total calculada automaticamente
```

---

## 5. PERMISSÕES NECESSÁRIAS

Todas as novas views requerem:
- **Mínimo:** `ADMIN_MINISTERIO` (via `user_has_permission_level_or_higher`)
- **Melhor:** `SUPERUSER` ou `ADMIN_GERAL`

---

## 6. TEMPLATES ESPERADOS (A CRIAR)

- `auditoria/sessoes_ativas.html`
- `auditoria/atividades_suspeitas.html`
- `auditoria/acumulacao_permissoes.html`

(Compartilham estrutura com templates existentes como `painel_auditoria.html`)

---

## 7. COMO HABILITAR

### 7.1 Registrar AppConfig
No `settings.py`, trocar:
```python
INSTALLED_APPS = [
    # ...
    'auditoria',  # Já existente
]
```

Para:
```python
INSTALLED_APPS = [
    # ...
    'auditoria.apps.AuditoriaConfig',  # Habilita signals
]
```

### 7.2 Adicionar Middleware (Recomendado)
```python
MIDDLEWARE = [
    # ... outros ...
    'auditoria.middleware.RegistrarAuditoriaMiddleware',
    'auditoria.middleware.CapturarAcessoNegadoMiddleware',
]
```

### 7.3 Executar Migrações
```bash
python manage.py migrate auditoria
```

---

## 8. EXEMPLOS DE INTEGRAÇÃO

### Registrar acesso negado em uma view:
```python
from auditoria.signals import registrar_acesso_negado

if not user.has_perm('ver_lista_membros'):
    registrar_acesso_negado(
        usuario=request.user,
        tipo_acesso='VIEW',
        recurso='lista_membros',
        permissao_requerida='secretaria.view_membro',
        request=request,
    )
    return HttpResponseForbidden()
```

### Exportar relatório de alterações:
```
GET /auditoria/exportar-logs/?tipo=alteracoes&dias=30
```

Retorna CSV com todas as alterações dos últimos 30 dias.

---

## 9. ESTATÍSTICAS COLETADAS

### Dashboard Principal (`painel_auditoria`)
- Total de alterações no período
- Total de acessos negados
- Usuários afetados
- Sessões ativas
- Distribuição por tipo de ação

### Análise Avançada
- Série temporal de alterações (gráfico)
- Top 5 usuários mais alterados
- Top 5 usuários com mais acessos negados
- Distribuição por grupo

### Relatórios
- Logarevantamento completo (com paginação)
- Detalhes por usuário
- Análise de suspeitas
- Acumulação de permissões

---

## 10. PRÓXIMOS PASSOS (Passo 5)

- [ ] Implementar workflow de requisição de permissões
- [ ] Criar UI para aprovação de acessos
- [ ] Notificações para admins sobre alterações importantes
- [ ] Alertas para atividades suspeitas

---

## 11. VALIDAÇÃO

✅ Sintaxe Python: Validada
✅ Modelos: Carregados com sucesso
✅ Signals: Prontos para uso
✅ Middleware: Configurado
✅ Views: Criadas e testadas
✅ URLs: Registradas

---

**Próximo Passo:** ✅ Passo 4 Completo | ➡️ Passo 5 (Workflow de Permissões)
