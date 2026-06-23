"""
Ponto de entrada do admin do módulo configuracao.
As classes admin estão organizadas em submódulos por domínio:
  - admin_ministerio.py : ConfiguracaoSistema, Ministerio, Igreja, Perfil, User
  - admin_planos.py     : Plano, LiberacaoPlanoMinisterio, AssinaturaMinisterio, CodigoPromocional
  - admin_sistema.py    : AtualizacaoSistema, EventoFunil, ValidacaoImagens
  - admin_onboarding.py : OnboardingStatus (já existente)
"""
# noqa: F401 — imports necessários para que Django registre os admins via AppConfig
from .admin_ministerio import (  # noqa: F401
    ConfiguracaoSistemaAdmin,
    IgrejaAdmin,
    MinisterioAdmin,
    PerfilUsuarioAdmin,
    PerfilUsuarioInline,
    UserAdmin,
)
from .admin_planos import (  # noqa: F401
    AssinaturaMinisterioAdmin,
    CodigoPromocionalAdmin,
    LiberacaoPlanoMinisterioAdmin,
    PlanoAdmin,
)
from .admin_sistema import (  # noqa: F401
    AtualizacaoSistemaAdmin,
    EventoFunilAdmin,
    ValidacaoImagens,
    ValidacaoImagensAdmin,
)
from .admin_financeiro_sistema import (  # noqa: F401
    CategoriaGastoSistemaAdmin,
    GastoSistemaAdmin,
)
