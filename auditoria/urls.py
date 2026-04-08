from django.urls import path
from . import views

app_name = 'auditoria'

urlpatterns = [
    path('auditar/', views.auditar_permissoes_view, name='auditar_permissoes'),
    path('alternar-modo-auditoria/', views.alternar_modo_auditoria, name='alternar_modo_auditoria'),
    
    # Painel de Auditoria
    path('painel/', views.painel_auditoria, name='painel_auditoria'),
    path('logs/alteracoes/', views.logs_alteracoes_permissoes, name='logs_alteracoes'),
    path('logs/acessos-negados/', views.logs_acessos_negados, name='logs_acessos_negados'),
    path('usuario/<int:user_id>/', views.detalhes_usuario_auditoria, name='detalhes_usuario'),
    path('api/estatisticas/', views.api_estatisticas_auditoria, name='api_estatisticas'),
    
    # Novas funcionalidades Passo 4
    path('sessoes-ativas/', views.sessoes_ativas, name='sessoes_ativas'),
    path('exportar-logs/', views.exportar_logs_csv, name='exportar_logs_csv'),
    path('atividades-suspeitas/', views.analise_atividades_suspeitas, name='atividades_suspeitas'),
    path('acumulacao-permissoes/', views.acumulacao_permissoes, name='acumulacao_permissoes'),
]
