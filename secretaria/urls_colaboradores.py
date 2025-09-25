from django.urls import path
from . import views_colaboradores

app_name = 'secretaria'

urlpatterns = [
    path('equipe-ebd/', views_colaboradores.equipe_ebd_list, name='equipe_ebd_list'),
    path('equipe-ebd/novo/', views_colaboradores.colaborador_add, name='colaborador_add'),
    path('equipe-ebd/<int:pk>/editar/', views_colaboradores.colaborador_edit, name='colaborador_edit'),
    path('equipe-ebd/<int:pk>/remover/', views_colaboradores.colaborador_delete, name='colaborador_delete'),
]
