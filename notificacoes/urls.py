from django.urls import path
from . import views

app_name = 'notificacoes'

urlpatterns = [
    path('', views.lista_notificacoes, name='lista_notificacoes'),
    path('<int:pk>/marcar-lida/', views.marcar_notificacao_lida, name='marcar_notificacao_lida'),
    path('marcar-todas-lidas/', views.marcar_todas_notificacoes_lidas, name='marcar_todas_notificacoes_lidas'),
]
