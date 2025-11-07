from .views import associar_usuarios_membros
from django.urls import path
from . import views

app_name = 'secretaria'

urlpatterns = [
    path('autocomplete_nome/', views.autocomplete_nome, name='autocomplete_nome'),
    path('', views.index, name='index'), # Esta URL agora será /sistema/
    path('dashboard/', views.dashboard, name='dashboard'),
    path('membros/', views.lista_membros, name='lista_membros'),
    path('membros/cadastrar/', views.criar_membro, name='cadastrar_membro'),
    path('membros/<int:membro_id>/editar/', views.editar_membro, name='editar_membro'),
    # path('backup/', views.backup_page, name='backup_page'),  # Removido: backup antigo (SQLite)
    path('membros/<int:membro_id>/alternar-status/', views.alternar_status_membro, name='alternar_status_membro'),
    path('membros/<int:membro_id>/ficha-impressao/', views.ficha_membro_impressao, name='ficha_membro_impressao'), # NOVA URL
    path('painel-lideranca-secretaria/', views.painel_lideranca_secretaria, name='painel_lideranca_secretaria'),
     # --- NOVA URL PARA ADICIONAR HISTÓRICO MANUAL ---
    path('membros/<int:membro_id>/historico/adicionar-manual/', views.adicionar_historico_status_manual, name='adicionar_historico_status_manual'),
    # --- URL PARA O PORTAL DO MEMBRO ---
    path('portal/', views.portal_membro, name='portal_membro'),

    path('ajax/autocomplete_nome_membro/', views.autocomplete_nome_membro, name='autocomplete_nome_membro'),
    # Relatório de reunião de membros
    path('relatorio/reuniao-membros/', views.relatorio_reuniao_membros, name='relatorio_reuniao_membros'),
    path('linha-do-tempo/', views.linha_do_tempo, name='linha_do_tempo'),
    # --- NOVA URL PARA LISTAGEM DE CARGOS ---
    path('cargos/', views.lista_cargos, name='lista_cargos'),
    path('cargos/novo/', views.criar_cargo, name='criar_cargo'),
    path('cargos/<int:cargo_id>/editar/', views.editar_cargo, name='editar_cargo'),
    path('cargos/<int:cargo_id>/excluir/', views.excluir_cargo, name='excluir_cargo'),
    path('cargos/<int:cargo_id>/ocupantes/', views.gerenciar_ocupantes, name='gerenciar_ocupantes'),
    path('associar-usuarios-membros/', associar_usuarios_membros, name='associar_usuarios_membros'),
    # --- URL para registrar acompanhamento de visita ---
    path('membros/<int:membro_id>/acompanhamento-visita/', views.registrar_acompanhamento_visita, name='registrar_acompanhamento_visita'),
    # --- VISITANTES (removido: agora visitante é membro com tipo_pessoa=Visitante) ---
    path('recepcao-evento/', views.registrar_presenca_visitante_evento, name='registrar_presenca_visitante_evento'),
    path('ajax/buscar_visitantes/', views.buscar_visitantes, name='buscar_visitantes'),
    path('visitantes/', views.lista_visitantes, name='lista_visitantes'),
    path('visitantes/cadastrar/', views.cadastrar_visitante, name='cadastrar_visitante'),
    path('visitantes/criar-parcial/', views.criar_visitante_parcial, name='criar_visitante_parcial'),
    path('visitantes/registrar-presenca-ajax/', views.ajax_registrar_presenca_evento, name='ajax_registrar_presenca_evento'),
    path('visitantes/presencas-por-evento/', views.ajax_get_presencas_evento, name='ajax_get_presencas_evento'),
    path('autocomplete_nome/', views.autocomplete_nome, name='autocomplete_nome'),
    # URLs para Grupos/Casas
    path('grupos-casa/', views.lista_grupos_casa, name='lista_grupos_casa'),
    path('grupos-casa/criar/', views.criar_grupo_casa, name='criar_grupo_casa'),
    path('grupos-casa/<int:grupo_id>/editar/', views.editar_grupo_casa, name='editar_grupo_casa'),
    path('grupos-casa/<int:grupo_id>/', views.detalhe_grupo_casa, name='detalhe_grupo_casa'),
    path('grupos-casa/<int:grupo_id>/reagrupar/', views.reagrupar_grupo_casa, name='reagrupar_grupo_casa'),
    path('grupos-casa/agrupar/preview/', views.agrupar_grupos_preview, name='agrupar_grupos_preview'),
    path('grupos-casa/agrupar/aplicar/', views.agrupar_grupos_apply, name='agrupar_grupos_apply'),

]
