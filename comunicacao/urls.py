from django.urls import path
from . import views

app_name = 'comunicacao'

urlpatterns = [
    # Mural de Avisos
    path('mural/', views.lista_avisos, name='lista_avisos'),
    path('mural/novo/', views.criar_aviso, name='criar_aviso'),
    path('mural/<int:pk>/', views.detalhe_aviso, name='detalhe_aviso'),
    path('mural/<int:pk>/editar/', views.editar_aviso, name='editar_aviso'),
    path('mural/<int:pk>/excluir/', views.excluir_aviso, name='excluir_aviso'),

    # E-mail em Massa
    path('email-massa/', views.enviar_email_massa, name='enviar_email_massa'),
    # Templates de E-mail
    path('templates-email/', views.templates_email, name='templates_email'),
    path('templates-email/email-massa/', views.visualizar_template_email_massa, name='visualizar_template_email_massa'),
    path('templates-email/password-reset/', views.visualizar_template_password_reset, name='visualizar_template_password_reset'),

    # WhatsApp (WAHA)
    path('whatsapp/configuracao/', views.configurar_whatsapp, name='configurar_whatsapp'),
    path('whatsapp/massa/', views.enviar_whatsapp_massa, name='enviar_whatsapp_massa'),
    path('whatsapp/massa/preview/', views.preview_whatsapp_destinatarios, name='preview_whatsapp_destinatarios'),
    path('whatsapp/massa/editar-celulares/', views.editar_celulares_whatsapp_massa, name='editar_celulares_whatsapp_massa'),
    path('whatsapp/massa/test-health/', views.test_waha_health, name='test_waha_health'),
    path('whatsapp/logs/', views.logs_whatsapp, name='logs_whatsapp'),
    path('whatsapp/webhook/', views.waha_webhook, name='waha_webhook'),
        path('whatsapp/configuracao-global/', views.configurar_whatsapp_global, name='configurar_whatsapp_global'),
        path('whatsapp/qr/<int:pk>/', views.qr_code_whatsapp, name='qr_code_whatsapp'),

]
