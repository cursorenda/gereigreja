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

    # Notificações
    path('notificacoes/', views.lista_notificacoes, name='lista_notificacoes'),
    path('notificacoes/<int:pk>/marcar-lida/', views.marcar_notificacao_lida, name='marcar_notificacao_lida'),
    path('notificacoes/marcar-todas-lidas/', views.marcar_todas_notificacoes_lidas, name='marcar_todas_notificacoes_lidas'),
    # E-mail em Massa
    path('email-massa/', views.enviar_email_massa, name='enviar_email_massa'),

]
