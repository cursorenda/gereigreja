from django.urls import path

from . import views

app_name = 'auditoria'

urlpatterns = [
    path('painel/', views.painel_auditoria, name='painel_auditoria'),
    path('auditar/', views.auditar_permissoes_view, name='auditar_permissoes'),
    path('api/estatisticas/', views.api_estatisticas_auditoria, name='api_estatisticas'),
    path('logs/alteracoes/', views.logs_alteracoes_permissoes, name='logs_alteracoes'),
    path('logs/acessos-negados/', views.logs_acessos_negados, name='logs_acessos_negados'),
    path('usuario/<int:user_id>/', views.detalhes_usuario_auditoria, name='detalhes_usuario'),
    path('sessoes-ativas/', views.sessoes_ativas, name='sessoes_ativas'),
    path('acumulacao-permissoes/', views.acumulacao_permissoes, name='acumulacao_permissoes'),
    path('alternar-modo/', views.alternar_modo_auditoria, name='alternar_modo_auditoria'),
    path('exportar-csv/', views.exportar_logs_csv, name='exportar_logs_csv'),
    path('analise/atividades-suspeitas/', views.analise_atividades_suspeitas, name='analise_atividades_suspeitas'),
]
