from django.urls import path
from . import views
from .views_test_tag import test_tag_form_view

app_name = 'secretaria'

urlpatterns = [
    path('acompanhamento-visita/<int:acompanhamento_id>/ver/', views.ver_acompanhamento_visita, name='ver_acompanhamento_visita'),
    path('acompanhamento-visita/<int:acompanhamento_id>/editar/', views.editar_acompanhamento_visita, name='editar_acompanhamento_visita'),
    path('acompanhamento-visita/<int:acompanhamento_id>/excluir/', views.excluir_acompanhamento_visita, name='excluir_acompanhamento_visita'),
    path('acompanhamentos-visita/escolher-pessoa/', views.escolher_pessoa_para_acompanhamento, name='escolher_pessoa_para_acompanhamento'),
    path('autocomplete_nome/', views.autocomplete_nome, name='autocomplete_nome'),
    # Página geral de acompanhamentos de visita
    path('acompanhamentos-visita/', views.lista_acompanhamentos_visita, name='acompanhamentos_visita'),
    path('', views.index, name='index'), # Esta URL agora será /sistema/
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pessoas/', views.lista_membros, name='lista_membros'),
    path('pessoas/', views.lista_membros, name='lista_pessoas'),  # Alias para compatibilidade de templates
    path('pessoas/imprimir/', views.imprimir_lista_membros, name='imprimir_lista_membros'),
    # Redirecionamento da URL antiga para a nova
    path('membros/', views.redirect_pessoas, name='redirect_pessoas'),  # Redirecionamento legado
    # Etapa 1: Pré-cadastro (dados básicos)
    path('pessoas/pre-cadastro/', views.pre_cadastro, name='pre_cadastro'),
    # Etapa 2: Cadastro detalhado (dados adicionais)
    path('pessoas/cadastro-detalhado/<int:pessoa_id>/', views.cadastro_detalhado, name='cadastro_detalhado'),
    # Etapa 3: Cadastro complementar (histórico, tags, acompanhamento)
    path('pessoas/cadastro-complementar/<int:pessoa_id>/', views.cadastro_complementar, name='cadastro_complementar'),
    # Cadastro antigo (pode ser removido após migração)
    path('pessoas/cadastrar/', views.criar_membro, name='cadastrar_membro'),
    path('pessoas/<int:membro_id>/visualizar/', views.detalhe_membro, name='detalhe_membro'),
    path('pessoas/<int:membro_id>/editar/', views.editar_membro, name='editar_membro'),
    # path('backup/', views.backup_page, name='backup_page'),  # Removido: backup antigo (SQLite)
    path('pessoas/<int:membro_id>/alternar-status/', views.alternar_status_membro, name='alternar_status_membro'),
    path('pessoas/<int:membro_id>/ficha-impressao/', views.ficha_membro_impressao, name='ficha_membro_impressao'), # NOVA URL
    path('painel-lideranca-secretaria/', views.painel_lideranca_secretaria, name='painel_lideranca_secretaria'),
     # --- NOVA URL PARA ADICIONAR HISTÓRICO MANUAL ---
    path('pessoas/<int:membro_id>/historico/adicionar-manual/', views.adicionar_historico_status_manual, name='adicionar_historico_status_manual'),
    # --- URL PARA O PORTAL DO MEMBRO ---
    path('portal/', views.portal_membro, name='portal_membro'),

    path('ajax/autocomplete_nome_membro/', views.autocomplete_nome_membro, name='autocomplete_nome_membro'),
    # Salvar nota pessoal do usuário
    path('ajax/salvar-nota/', views.salvar_nota_usuario, name='salvar_nota_usuario'),
    # Relatório de reunião de membros
    path('relatorio/reuniao-membros/', views.relatorio_reuniao_membros, name='relatorio_reuniao_membros'),
    path('linha-do-tempo/', views.linha_do_tempo, name='linha_do_tempo'),
    # --- NOVA URL PARA LISTAGEM DE CARGOS ---
    path('cargos/', views.lista_cargos, name='lista_cargos'),
    path('cargos/novo/', views.criar_cargo, name='criar_cargo'),
    path('cargos/<int:cargo_id>/editar/', views.editar_cargo, name='editar_cargo'),
    path('cargos/<int:cargo_id>/excluir/', views.excluir_cargo, name='excluir_cargo'),
    path('cargos/<int:cargo_id>/ocupantes/', views.gerenciar_ocupantes, name='gerenciar_ocupantes'),
    # --- URL para registrar acompanhamento de visita ---
    path('pessoas/<int:membro_id>/acompanhamento-visita/', views.registrar_acompanhamento_visita, name='registrar_acompanhamento_visita'),
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
    path('tags/criar/', views.criar_tag, name='criar_tag'),
    path('tags/<int:tag_id>/editar/', views.editar_tag, name='editar_tag'),
    path('tags/<int:tag_id>/excluir/', views.excluir_tag, name='excluir_tag'),
    # URL de teste para o formulário de tags
    path('test-tag-form/', test_tag_form_view, name='test_tag_form'),
    path('ajax/desvincular_usuario_membro/', views.desvincular_usuario_membro, name='desvincular_usuario_membro'),

]
