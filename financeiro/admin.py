"""
Ponto de entrada do admin do modulo financeiro.
As classes admin estao organizadas em submodulos por dominio:
  - admin_contas.py       : ContaBancaria, ContaPagar, PermissaoCaixa
  - admin_movimentacao.py : Receitas, Despesas, FechamentoCaixa
  - admin_catalogo.py     : CategoriaDespesa, Fornecedor
"""
# noqa: F401 - imports necessarios para que Django registre os admins via AppConfig
from .admin_catalogo import (  # noqa: F401
    CategoriaDespesaAdmin,
    FornecedorAdmin,
)
from .admin_contas import (  # noqa: F401
    ContaBancariaAdmin,
    ContaPagarAdmin,
    PermissaoCaixaAdmin,
)
from .admin_movimentacao import (  # noqa: F401
    DespesasAdmin,
    FechamentoCaixaAdmin,
    ReceitasAdmin,
)
