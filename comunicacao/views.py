# Backwards-compatible reexports from the modular views package.
from .views.email import (
    enviar_email_massa,
    templates_email,
    visualizar_template_email_massa,
    visualizar_template_password_reset,
)
from .views.home import home_comunicacao
from .views.logs import logs_whatsapp
from .views.mural import criar_aviso, detalhe_aviso, editar_aviso, excluir_aviso, lista_avisos
from .views.whatsapp import (
    configurar_whatsapp,
    configurar_whatsapp_global,
    editar_celulares_whatsapp_massa,
    enviar_whatsapp_massa,
    preview_whatsapp_destinatarios,
    qr_code_whatsapp,
    test_waha_health,
    waha_webhook,
)
