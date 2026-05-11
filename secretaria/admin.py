"""
Ponto de entrada do admin do modulo secretaria.
As classes admin estao organizadas em submodulos por dominio:
  - admin_membros.py : Membro, TipoPessoa, StatusPessoa, Acompanhamento, Historico, Tag
  - admin_grupos.py  : GrupoCasa, VisitaGrupoCasa
  - admin_cargos.py  : Cargo, MembroCargo, TransferenciaMembro
"""
# noqa: F401 - imports necessarios para que Django registre os admins via AppConfig
from .admin_cargos import (  # noqa: F401
    CargoAdmin,
    MembroCargoAdmin,
    TransferenciaMembroAdmin,
)
from .admin_grupos import (  # noqa: F401
    GrupoCasaAdmin,
    VisitaGrupoCasaAdmin,
)
from .admin_membros import (  # noqa: F401
    AcompanhamentoVisitaAdmin,
    MembroAdmin,
    StatusHistoricoAdmin,
    StatusPessoaAdmin,
    TagAdmin,
    TipoPessoaAdmin,
)
