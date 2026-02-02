from django.urls import path
from . import views

app_name = 'escola_biblica'

urlpatterns = [
    # Dashboard e gráficos
    path('', views.dashboard, name='dashboard'),
    path('graficos-evolucao/', views.graficos_evolucao, name='graficos_evolucao'),
    path('graficos/', views.dashboard_graficos, name='dashboard_graficos'),

    # Turmas
    path('turmas/', views.turma_list, name='turma_list'),
    path('turmas/novo/', views.turma_create, name='turma_create'),
    path('turmas/<int:pk>/editar/', views.turma_edit, name='turma_edit'),
    path('turmas/<int:pk>/excluir/', views.turma_delete, name='turma_delete'),
    path('turmas/<int:turma_id>/chamada/', views.chamada_presenca, name='chamada_presenca'),

    # Alunos
    path('alunos/', views.aluno_list, name='aluno_list'),
    path('alunos/novo/', views.aluno_create, name='aluno_create'),
    path('alunos/<int:pk>/', views.aluno_detail, name='aluno_detail'),
    path('alunos/<int:aluno_id>/transferir/', views.transferir_aluno, name='transferir_aluno'),

    # Classes
    path('classes/', views.classe_list, name='classe_list'),
    path('classes/novo/', views.classe_create, name='classe_create'),
    path('classes/<int:pk>/editar/', views.classe_edit, name='classe_edit'),
    path('classes/<int:pk>/excluir/', views.classe_delete, name='classe_delete'),

    # Licoes
    path('licoes/', views.licao_list, name='licao_list'),
    path('licoes/novo/', views.licao_create, name='licao_create'),
    path('licoes/<int:pk>/editar/', views.licao_edit, name='licao_edit'),
    path('licoes/<int:pk>/excluir/', views.licao_delete, name='licao_delete'),
    path('licoes/gerar_cronograma/', views.gerar_cronograma, name='gerar_cronograma'),

    # Wizard de geração de lições
    path('licoes/gerar_cronograma_wizard/', views.gerar_cronograma_wizard, name='gerar_cronograma_wizard'),

    # Ofertas
    path('ofertas/', views.oferta_classe_list, name='oferta_classe_list'),
    path('ofertas/nova/', views.oferta_classe_create, name='oferta_classe_create'),
    path('ofertas/<int:pk>/editar/', views.oferta_classe_edit, name='oferta_classe_edit'),
    path('ofertas/<int:pk>/excluir/', views.oferta_classe_delete, name='oferta_classe_delete'),

    # Avaliações
    path('avaliacoes/', views.avaliacao_list, name='avaliacao_list'),
    path('avaliacoes/novo/', views.avaliacao_create, name='avaliacao_create'),
    path('avaliacoes/<int:pk>/editar/', views.avaliacao_edit, name='avaliacao_edit'),
    path('avaliacoes/<int:pk>/excluir/', views.avaliacao_delete, name='avaliacao_delete'),

    # Relatórios
    path('relatorio/alunos/', views.relatorio_alunos, name='relatorio_alunos'),
    path('relatorio/frequencia/', views.relatorio_frequencia, name='relatorio_frequencia'),
    path('relatorio/ebd-dia/', views.relatorio_ebd_dia, name='relatorio_ebd_dia'),

    # Frequência
    path('frequencia/', views.frequencia_list, name='frequencia_list'),

    # Cargos/Funções
    path('cargos-ebd/', views.cargos_ebd_list, name='cargos_ebd_list'),

    # Períodos e cópias
    path('abrir_novo_periodo/', views.abrir_novo_periodo, name='abrir_novo_periodo'),
    path('copiar_turmas_ano_anterior/', views.copiar_turmas_ano_anterior, name='copiar_turmas_ano_anterior'),
    path('copiar_periodo_selecao/', views.copiar_periodo_selecao, name='copiar_periodo_selecao'),

    # AJAX e utilitários
    path('get_professor/', views.get_professor_nome, name='get_professor_nome'),
]
