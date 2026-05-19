"""
URLs para o módulo de galeria de imagens do painel desenvolvedor.
"""
from django.urls import path
from . import views

app_name = 'painel_desenvolvedor'

urlpatterns = [
    # Galeria
    path('galeria-imagens/', views.galeria_imagens, name='galeria_imagens'),
    path('galeria-imagens/criar/', views.criar_imagem, name='criar_imagem'),
    path('galeria-imagens/<int:pk>/', views.detalhes_imagem, name='detalhes_imagem'),
    path('galeria-imagens/<int:pk>/editar/', views.editar_imagem, name='editar_imagem'),
    path('galeria-imagens/<int:pk>/ativar/', views.ativar_imagem, name='ativar_imagem'),
    path('galeria-imagens/<int:pk>/deletar/', views.deletar_imagem, name='deletar_imagem'),
]
