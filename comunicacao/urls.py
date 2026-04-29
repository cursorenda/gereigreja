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

]
