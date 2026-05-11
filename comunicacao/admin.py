"""
Ponto de entrada do admin do modulo comunicacao.
As classes admin estao organizadas em submodulos por dominio:
  - admin_avisos.py  : Aviso
  - admin_whatsapp.py: WhatsAppConfiguracaoGlobal, WhatsAppConfiguracao, WhatsAppMensagemLog
"""
# noqa: F401 - imports necessarios para que Django registre os admins via AppConfig
from .admin_avisos import (  # noqa: F401
    AvisoAdmin,
)
from .admin_whatsapp import (  # noqa: F401
    WhatsAppConfiguracaoAdmin,
    WhatsAppConfiguracaoGlobalAdmin,
    WhatsAppMensagemLogAdmin,
)
