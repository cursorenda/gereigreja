# Permissões em Hierarquia – GereIgreja

## Introdução
O GereIgreja utiliza um modelo de permissões hierárquico, onde cada grupo possui um nível de privilégio. Usuários em grupos de nível superior herdam automaticamente todas as permissões dos níveis inferiores.

---

## Como funciona a hierarquia
- A hierarquia é definida em `contas/constants.py` na lista `HIERARQUIA_GRUPOS`.
- O helper central `user_has_permission_level_or_higher(user, required_group)` garante que quem está acima na hierarquia pode tudo que está abaixo.
- Em views protegidas por `@page_access_required`, o superusuário também segue a regra da `page_key` (não há bypass automático global).
- Para permissões por tela/modulo, use `@page_access_required` com chaves em `contas/page_permissions.py`.

---

## Exemplo prático de herança
Se uma view exige permissão de "Tesoureiro":
- Um usuário no grupo "Tesoureiro" pode acessar.
- Um usuário em qualquer grupo acima (Secretario Local, Pastor Local, Pastor Regional, Liderança, Admin Ministerio) também pode acessar.
- Usuários em grupos abaixo (Equipe de Eventos, Membro Comum, etc.) não podem acessar.

---

## Fluxo de checagem de permissão
1. Verificar autenticação e regra aplicada (ex.: `@page_access_required` ou helper hierárquico).
2. Se `user_has_permission_level_or_higher(user, required_group)` → acesso concedido.
3. Caso contrário → acesso negado.

---

## Exemplo de código
```python
from contas.constants import user_has_permission_level_or_higher, TESOUREIRO
if user_has_permission_level_or_higher(request.user, TESOUREIRO):
    # Permissão concedida
else:
    # Permissão negada
```

---

## Checklist para permissões hierárquicas
- [x] Toda checagem de permissão usa o helper central
- [x] Regra de superusuário está documentada conforme o decorator usado
- [x] Não há checagens manuais de grupo fora do helper
- [x] Documentação e exemplos atualizados

---

## Referências
- [docs/HIERARQUIA_PERMISSOES.md](HIERARQUIA_PERMISSOES.md)
- [contas/constants.py](../contas/constants.py)

---

> Última revisão: 01/04/2026
