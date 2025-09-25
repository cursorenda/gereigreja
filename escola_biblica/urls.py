
from django.urls import path
from . import views

app_name = 'escola_biblica'

urlpatterns = [
    # Exemplo de rotas iniciais
    path('', views.dashboard, name='dashboard'),
    path('graficos-evolucao/', views.graficos_evolucao, name='graficos_evolucao'),
    path('graficos/', views.dashboard_graficos, name='dashboard_graficos'),
    # Ofertas por Classe
    path('ofertas/', views.oferta_classe_list, name='oferta_classe_list'),
    path('ofertas/nova/', views.oferta_classe_create, name='oferta_classe_create'),
    path('ofertas/<int:pk>/editar/', views.oferta_classe_edit, name='oferta_classe_edit'),
    path('ofertas/<int:pk>/excluir/', views.oferta_classe_delete, name='oferta_classe_delete'),
    path('relatorio/alunos/', views.relatorio_alunos, name='relatorio_alunos'),
    path('relatorio/frequencia/', views.relatorio_frequencia, name='relatorio_frequencia'),
    path('alunos/', views.aluno_list, name='aluno_list'),
    path('alunos/novo/', views.aluno_create, name='aluno_create'),
    path('alunos/<int:pk>/', views.aluno_detail, name='aluno_detail'),
    path('turmas/', views.turma_list, name='turma_list'),
    path('turmas/novo/', views.turma_create, name='turma_create'),
    path('turmas/<int:turma_id>/chamada/', views.chamada_presenca, name='chamada_presenca'),
    path('turmas/<int:pk>/editar/', views.turma_edit, name='turma_edit'),
    path('turmas/<int:pk>/excluir/', views.turma_delete, name='turma_delete'),
    path('frequencia/', views.frequencia_list, name='frequencia_list'),
    path('classes/', views.classe_list, name='classe_list'),
    path('classes/novo/', views.classe_create, name='classe_create'),
    path('classes/<int:pk>/editar/', views.classe_edit, name='classe_edit'),
    path('classes/<int:pk>/excluir/', views.classe_delete, name='classe_delete'),
    path('licoes/', views.licao_list, name='licao_list'),
    path('licoes/novo/', views.licao_create, name='licao_create'),
    path('licoes/<int:pk>/editar/', views.licao_edit, name='licao_edit'),
    path('licoes/<int:pk>/excluir/', views.licao_delete, name='licao_delete'),

    # Avaliações
    path('avaliacoes/', views.avaliacao_list, name='avaliacao_list'),
    path('avaliacoes/novo/', views.avaliacao_create, name='avaliacao_create'),
    path('avaliacoes/<int:pk>/editar/', views.avaliacao_edit, name='avaliacao_edit'),
    path('avaliacoes/<int:pk>/excluir/', views.avaliacao_delete, name='avaliacao_delete'),

    # Transferência de alunos
    path('alunos/<int:aluno_id>/transferir/', views.transferir_aluno, name='transferir_aluno'),

    # Listagem dinâmica de cargos/funções
    path('cargos-ebd/', views.cargos_ebd_list, name='cargos_ebd_list'),
]
