"""
URLs para o módulo de galeria de imagens do painel desenvolvedor.
"""
from django.urls import path
from . import views

app_name = 'painel_desenvolvedor'

urlpatterns = [
    # Dashboard de custo e risco
    path('custo-risco/', views.dashboard_custo_risco, name='dashboard_custo_risco'),

    # Compliance de hinos
    path('hinario-compliance/', views.fila_compliance_hinos, name='fila_compliance_hinos'),
    path('hinario-compliance/aprovar-liberar/', views.aprovar_liberar_hino, name='aprovar_liberar_hino'),
    path('hinario-compliance/aprovar-liberar-lote/', views.aprovar_liberar_hino_lote, name='aprovar_liberar_hino_lote'),
    path('hinario-compliance/classificar-tema-lote/', views.classificar_tema_hino_lote, name='classificar_tema_hino_lote'),

    # Galeria
    path('galeria-imagens/', views.galeria_imagens, name='galeria_imagens'),
    path('galeria-imagens/criar/', views.criar_imagem, name='criar_imagem'),
    path('galeria-imagens/<int:pk>/', views.detalhes_imagem, name='detalhes_imagem'),
    path('galeria-imagens/<int:pk>/editar/', views.editar_imagem, name='editar_imagem'),
    path('galeria-imagens/<int:pk>/ativar/', views.ativar_imagem, name='ativar_imagem'),
    path('galeria-imagens/<int:pk>/deletar/', views.deletar_imagem, name='deletar_imagem'),
]
