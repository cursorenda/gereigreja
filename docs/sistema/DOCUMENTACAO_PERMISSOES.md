# Documentação de Permissões e Fluxo de Usuários - Gereigreja

## 1. Conceitos-Chave

- **Usuário**: Conta de acesso ao sistema (Django User).
- **Membro**: Pessoa cadastrada na secretaria, com ou sem login no sistema.
- **Grupo/Papel**: Papel em Django Groups que define nível hierárquico e escopo.
- **Página/Feature key**: Chave de acesso centralizada no `PAGE_ACCESS_RULES`.

## 2. Arquitetura Atual de Permissões (padrão vigente)

O controle de acesso de módulos deve seguir este fluxo:

1. `@login_required`
2. `@page_access_required('<chave_da_pagina>')`
3. Regra resolvida via `contas/page_permissions.py` (`PAGE_ACCESS_RULES`)

### Exemplo

```python
from django.contrib.auth.decorators import login_required
from core.decorators import page_access_required

@login_required
@page_access_required('financeiro')
def listar_transacoes(request):
    ...
```

## 3. Matriz Central de Acesso

Fonte oficial: `contas/page_permissions.py`.

Chaves em uso no sistema:

- `menu_interno`
- `dashboard_secretaria`
- `secretaria_pessoas`
- `secretaria_transferencias`
- `secretaria_cargos`
- `secretaria_grupos_casa`
- `secretaria_acompanhamentos`
- `secretaria_tags`
- `secretaria_relatorios`
- `recepcao_visitantes`
- `agenda`
- `eventos`
- `escola_biblica`
- `escola_biblica_professor`
- `financeiro`
- `lideranca_secretaria`
- `lideranca_financeira`
- `comunicacao`
- `comunicacao_massa`
- `mural_avisos`
- `suporte`
- `dashboard_sistema`
- `novidades_sistema`
- `configuracoes_sistema`

> **Notas importantes sobre permissões de acesso:**
>
> | Chave | Regra | Observação |
> |---|---|---|
> | `mural_avisos` | `_is_authenticated` | Qualquer usuário logado — inclui Membro Comum. Usado em `lista_avisos` e `detalhe_aviso` |
> | `comunicacao` | `user_pode_gerenciar_comunicacao` | Restrito a gestores. Usado em criar/editar/excluir avisos |
> | `suporte` | `_can_view_internal_menu` | Oculto para Membro Comum (requer grupo diferente de `MEMBRO_COMUM`) |

## 4. Quando Usar Decorators Legados

Decorators legados ainda existem e podem ser usados em casos específicos:

- `@admin_ministerio_required`: operações estritamente administrativas.
- `@user_passes_test_or_403`: regra muito específica de objeto/contexto que ainda não virou chave central.
- `@check_permission`: compatibilidade em trechos antigos, preferindo migração gradual para `page_access_required`.

Regra prática: para páginas de módulo, **prefira sempre** `@page_access_required`.

## 5. Fluxo de Cadastro e Onboarding

1. Criar usuário (nome/e-mail/senha).
2. Atribuir grupo adequado.
3. (Opcional) Vincular com membro para fluxos de secretaria/relatórios.

## 6. Boas Práticas

- Nunca usar strings literais para grupos.
- Nunca duplicar regra de grupo dentro da view quando há chave equivalente.
- Atualizar `PAGE_ACCESS_RULES` ao criar novo módulo/tela protegida.
- Documentar novas chaves neste arquivo e nos guias de onboarding.

## 7. Pontos de Atenção

- Usuário sem grupo tende a ficar sem acesso funcional mesmo autenticado.
- Superusuário não recebe bypass automático em `page_access_required`; acesso depende da regra da `page_key`, exceto em fluxos com checagem explícita de `is_superuser`.
- Divergência entre docs e `PAGE_ACCESS_RULES` deve ser tratada como bug de documentação.

---

Ultima revisao: 29/04/2026
