# Onboarding: Permissões e Hierarquia GereIgreja

## Como funciona
- Todas as permissões são baseadas em grupos definidos em `contas/constants.py`.
- O controle de acesso por tela deve usar a matriz `PAGE_ACCESS_RULES` em `contas/page_permissions.py`.
- Em views de modulo, use `@page_access_required('<chave>')` junto com `@login_required`.
- Use sempre as funções utilitárias (`user_tem_grupo`, `user_tem_qualquer_grupo`, etc).
- Nunca cheque grupos diretamente no código.

## Exemplos de uso correto
```python
from django.contrib.auth.decorators import login_required
from core.decorators import page_access_required

@login_required
@page_access_required('secretaria_pessoas')
def listar_membros(request):
    ...
```

## Checklist para revisão de permissões
- [ ] A view usa `@page_access_required` quando ha chave correspondente?
- [ ] A chave existe em `PAGE_ACCESS_RULES`?
- [ ] Usou funções utilitárias para checagem de grupo?
- [ ] Atualizou a documentação se criou/alterou grupos?
- [ ] Testou cenários de herança de permissões?

## Fluxo de dúvidas
- Consulte os arquivos em `docs/`, `contas/constants.py` e `contas/page_permissions.py`.
- Fale com o responsável técnico do projeto para dúvidas sobre permissões.
