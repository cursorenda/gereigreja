# Hierarquia de Permissões e Grupos – GereIgreja

## Visão Geral
O GereIgreja utiliza um sistema hierárquico de grupos para controlar o acesso a todas as funcionalidades. A lógica de permissão é centralizada em helpers únicos, garantindo consistência, segurança e facilidade de manutenção.

---

## 1. Hierarquia de Grupos
A hierarquia é definida em `contas/constants.py` na lista `HIERARQUIA_GRUPOS`, do mais alto para o mais baixo privilégio:

1. **Admin Ministerio**
2. **Secretaria Ministerial**
3. **Tesouraria Ministerial**
4. **Pastor Regional**
5. **Pastor Local**
6. **Secretario Local**
7. **Tesoureiro**
8. **Superintendente EBD**
9. **Equipe de Eventos**
10. **Equipe de Mídia**
11. **Equipe de Recepção**
12. **Professores EBD**
13. **Secretaria EBD**
14. **Membro Comum**

- O valor das constantes deve ser idêntico ao nome do grupo no banco de dados.
- Nunca use strings literais para grupos/permissões no código.

---

## 2. Helpers Centrais

### `get_user_permission_level(user)`
Retorna o nível hierárquico do usuário (0 = mais alto). Superusuário sempre retorna 0.

### `user_has_permission_level_or_higher(user, required_group)`
Retorna `True` se o usuário tem permissão igual ou superior ao grupo exigido.

**Exemplo:**
```python
from contas.constants import user_has_permission_level_or_higher, PASTOR_LOCAL
if user_has_permission_level_or_higher(user, PASTOR_LOCAL):
    # Usuário é Pastor Local ou superior (Regional, Admin...)
```

---

## 3. Política de Superusuário
- Usuários com `is_superuser=True` têm acesso total, independentemente dos grupos.
- Sempre cheque `is_superuser` antes de aplicar regras de grupo.

---

## 4. Boas Práticas
- Use sempre as funções centrais para checagem de permissão.
- Não duplique lógica de permissão em views, forms ou templates.
- Documente toda alteração de grupo/permissão.
- Atualize este documento e os arquivos relacionados ao criar/alterar grupos.

---

## 5. Exemplos de Uso

### Decorator em View
```python
from contas.constants import user_has_permission_level_or_higher, TESOUREIRO
from django.core.exceptions import PermissionDenied

def minha_view(request):
    if not user_has_permission_level_or_higher(request.user, TESOUREIRO):
        raise PermissionDenied('Acesso restrito!')
    # ...
```

### Template
```django
{% if user|has_permission:'Tesoureiro' %}
    <a href="/financeiro/">Financeiro</a>
{% endif %}
```

---

## 6. Testes de Permissão
- Teste todos os papéis: superusuário, staff sem grupo, staff com grupo correto, staff com grupo errado, usuário comum.
- Exemplo de resultado esperado:
    - Superuser tem acesso total: OK
    - Staff sem grupo não tem acesso: OK
    - Staff com grupo correto tem acesso: OK
    - Staff com grupo errado bloqueado: OK
    - Usuário comum bloqueado: OK

---

## 7. Escopo Hierárquico: Módulo de Cargos (Secretaria)

Além da permissão de acesso geral, o módulo de cargos implementa **filtro de escopo hierárquico** para limitar a visibilidade e gerenciamento de cargos:

### Regra de Escopo
- **Admin Ministério**: vê/gerencia todos os cargos (incluindo Admin Ministério, Secretaria Ministerial, Tesouraria Ministerial)
- **Pastor Regional**: vê/gerencia cargos a partir de `PASTOR_REGIONAL` para baixo (Regional + Local + Secretário Local + Tesoureiro + EBD + Equipes + Membro)
- **Pastor Local**: vê/gerencia cargos a partir de `PASTOR_LOCAL` para baixo (Local + Secretário Local + Tesoureiro + EBD + Equipes + Membro)
- **Outros**: sem acesso (bloqueados com 403)

### Implementação
Arquivo: `secretaria/views.py`

Funções helper:
- `_nomes_grupos_permitidos_para_cargos(user)` — Retorna `None` (sem restrição) ou set de nomes de grupos permitidos
- `_filtrar_cargos_por_escopo_usuario(user, cargos_qs)` — Filtra queryset de cargos
- `_cargo_dentro_escopo_usuario(user, cargo)` — Valida se um cargo específico está no escopo do usuário

### Views Afetadas
1. `lista_cargos` — Filtra lista de cargos visíveis
2. `criar_cargo` — Limita dropdown de grupos disponíveis para associar
3. `editar_cargo` — Bloqueia acesso direto a cargos fora do escopo (403) + limita groups no form
4. `excluir_cargo` — Bloqueia acesso direto (403)
5. `gerenciar_ocupantes` — Bloqueia acesso direto (403)

### Exemplos

#### Pastor Local vendo cargos
```
Admin Ministério       → BLOQUEADO (não aparece na lista)
Secretaria Ministerial → BLOQUEADO (não aparece na lista)
Tesouraria Ministerial → BLOQUEADO (não aparece na lista)
Pastor Regional        → BLOQUEADO (não aparece na lista)
Pastor Local           → VISÍVEL ✅
Secretário Local       → VISÍVEL ✅
Tesoureiro             → VISÍVEL ✅
... (tudo abaixo de PASTOR_LOCAL) → VISÍVEL ✅
```

#### Pastor Regional vendo cargos
```
Admin Ministério       → BLOQUEADO (não aparece na lista)
Secretaria Ministerial → BLOQUEADO (não aparece na lista)
Tesouraria Ministerial → BLOQUEADO (não aparece na lista)
Pastor Regional        → VISÍVEL ✅
Pastor Local           → VISÍVEL ✅
Secretário Local       → VISÍVEL ✅
Tesoureiro             → VISÍVEL ✅
... (tudo abaixo de PASTOR_REGIONAL) → VISÍVEL ✅
```

### Teste de Regressão
Arquivo: `secretaria/tests/test_cargos_autorizacao_views.py` (6 testes)

---

## 8. Referências
- [contas/constants.py](../contas/constants.py)
- [docs/GRUPOS_PERMISSOES.md](GRUPOS_PERMISSOES.md)
- [docs/DOCUMENTACAO_PADRAO_GRUPOS.md](DOCUMENTACAO_PADRAO_GRUPOS.md)
- [docs/ONBOARDING_PERMISSOES.md](ONBOARDING_PERMISSOES.md)

---

## 8. Checklist de Revisão
- [x] Toda permissão usa helper central
- [x] Superusuário sempre tem acesso total
- [x] Documentação atualizada
- [x] Testes automatizados cobrindo todos os cenários
- [x] Grupos e permissões revisados no banco

---

> Última revisão: 01/04/2026
