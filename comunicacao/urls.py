from django.urls import path
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

app_name = 'comunicacao'

urlpatterns = [
    # Home da Comunicacao
    path('', home_comunicacao, name='home'),
    path('home/', home_comunicacao, name='home'),

    # Mural de Avisos
    path('mural/', lista_avisos, name='lista_avisos'),
    path('mural/novo/', criar_aviso, name='criar_aviso'),
    path('mural/<int:pk>/', detalhe_aviso, name='detalhe_aviso'),
    path('mural/<int:pk>/editar/', editar_aviso, name='editar_aviso'),
    path('mural/<int:pk>/excluir/', excluir_aviso, name='excluir_aviso'),

    # E-mail em Massa
    path('email-massa/', enviar_email_massa, name='enviar_email_massa'),
    # Templates de E-mail
    path('templates-email/', templates_email, name='templates_email'),
    path('templates-email/email-massa/', visualizar_template_email_massa, name='visualizar_template_email_massa'),
    path('templates-email/password-reset/', visualizar_template_password_reset, name='visualizar_template_password_reset'),

    # WhatsApp (WAHA)
    path('whatsapp/configuracao/', configurar_whatsapp, name='configurar_whatsapp'),
    path('whatsapp/massa/', enviar_whatsapp_massa, name='enviar_whatsapp_massa'),
    path('whatsapp/massa/preview/', preview_whatsapp_destinatarios, name='preview_whatsapp_destinatarios'),
    path('whatsapp/massa/editar-celulares/', editar_celulares_whatsapp_massa, name='editar_celulares_whatsapp_massa'),
    path('whatsapp/massa/test-health/', test_waha_health, name='test_waha_health'),
    path('whatsapp/logs/', logs_whatsapp, name='logs_whatsapp'),
    path('whatsapp/webhook/', waha_webhook, name='waha_webhook'),
    path('whatsapp/configuracao-global/', configurar_whatsapp_global, name='configurar_whatsapp_global'),
    path('whatsapp/qr/<int:pk>/', qr_code_whatsapp, name='qr_code_whatsapp'),

]
