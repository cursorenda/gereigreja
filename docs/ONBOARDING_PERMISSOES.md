# Onboarding: Permissões e Hierarquia GereIgreja

## Como funciona
- Todas as permissões são baseadas em grupos definidos em `contas/constants.py`.
- Use sempre as funções utilitárias (`user_tem_grupo`, `user_tem_qualquer_grupo`, etc).
- Nunca cheque grupos diretamente no código.

## Exemplos de uso correto
```python
from contas.constants import user_tem_grupo, ADMIN_MINISTERIO
if user_tem_grupo(user, ADMIN_MINISTERIO):
    # ...
```

## Checklist para revisão de permissões
- [ ] Usou funções utilitárias para checagem de grupo?
- [ ] Atualizou a documentação se criou/alterou grupos?
- [ ] Testou cenários de herança de permissões?

## Fluxo de dúvidas
- Consulte os arquivos em `docs/` e `contas/constants.py`.
- Fale com o responsável técnico do projeto para dúvidas sobre permissões.
