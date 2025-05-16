# c:\Gereigreja\secretaria\urls.py

from django.urls import path
from . import views


app_name = 'secretaria' # Adicione esta linha


urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('membros/', views.lista_membros, name='lista_membros'),
    path('membros/cadastrar/', views.criar_membro, name='cadastrar_membro'),
    path('membros/<int:membro_id>/editar/', views.editar_membro, name='editar_membro'),
    path('backup/', views.backup_page, name='backup_page'),
    path('membros/<int:membro_id>/alternar-status/', views.alternar_status_membro, name='alternar_status_membro'),
    path('painel-lideranca-secretaria/', views.painel_lideranca_secretaria, name='painel_lideranca_secretaria'),

]
