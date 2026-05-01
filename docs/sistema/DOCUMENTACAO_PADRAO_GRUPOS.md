# Padrão de Nomenclatura de Grupos e Permissões

Este documento define o padrão oficial de nomenclatura para grupos e permissões no Gereigreja, visando padronização, clareza e manutenção do sistema.

## 1. Convenções Gerais
- **Todos os nomes de grupos devem ser definidos em `contas/constants.py` como constantes.**
- **Os valores das constantes devem ser idênticos aos nomes dos grupos no banco de dados.**
- **Nunca use strings literais para nomes de grupos/permissões no código.**
- **Referencie sempre as constantes, inclusive em templates, scripts e testes.**

## 2. Exemplo de Definição
```python
# contas/constants.py
PASTOR_REGIONAL = "Pastor Regional"
ADMIN_MINISTERIO = "Admin Ministerio"
# ... demais grupos
```

## 3. Uso Correto
```python
from contas.constants import user_tem_grupo, PASTOR_REGIONAL

if user_tem_grupo(user, PASTOR_REGIONAL):
    # ...
```

## 4. Documentação Relacionada
- [docs/GRUPOS_PERMISSOES.md](GRUPOS_PERMISSOES.md): Hierarquia, permissões e descrição dos grupos.
- [docs/DOCUMENTACAO_PERMISSOES.md](DOCUMENTACAO_PERMISSOES.md): Detalhes sobre permissões customizadas.

---

## Referências Cruzadas

- Este documento é referenciado em:
    - [GRUPOS_PERMISSOES.md](GRUPOS_PERMISSOES.md)
    - [DOCUMENTACAO_PERMISSOES.md](DOCUMENTACAO_PERMISSOES.md)

## 5. Observações
- Sempre alinhe os nomes das constantes com o banco de dados.
- Atualize este documento e os arquivos relacionados ao criar/alterar grupos.
