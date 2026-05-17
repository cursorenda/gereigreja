
# financeiro/urls.py
from django.urls import path, re_path
from . import views

app_name = 'financeiro' # Namespace definido

urlpatterns = [
    # Painel Financeiro
    path('', views.painel_financeiro, name='painel_financeiro'),
    path('painel-lideranca/', views.painel_lideranca_financeiro, name='painel_lideranca_financeiro'),

    # Gestão de Permissões de Caixa
    path('contas-bancarias/<int:caixa_id>/permissoes/', views.gerenciar_permissoes_caixa, name='gerenciar_permissoes_caixa'),

    # Transferências entre Caixas
    path('transferencias/nova/', views.transferencia_caixa_create, name='nova_transferencia_caixa'),
    path('api/caixas-por-igreja/<int:igreja_id>/', views.api_caixas_por_igreja, name='api_caixas_por_igreja'),

    # Receitas
    path('receitas/', views.lista_receitas, name='lista_receitas'),
    path('receitas/cadastrar/', views.cadastrar_receita, name='cadastrar_receita'),
    path('receitas/editar/<int:pk>/', views.editar_receita, name='editar_receita'),
    path('receitas/excluir/<int:pk>/', views.excluir_receita, name='excluir_receita'), # Adicionado URL de exclusão

    # Despesas
    path('despesas/', views.lista_despesas, name='lista_despesas'),
    path('despesas/cadastrar/', views.cadastrar_despesa, name='cadastrar_despesa'),
    path('despesas/editar/<int:pk>/', views.editar_despesa, name='editar_despesa'),
    path('despesas/excluir/<int:pk>/', views.excluir_despesa, name='excluir_despesa'), # Adicionado URL de exclusão

    # Categorias de Despesa
    path('categorias-despesa/', views.lista_categorias_despesa, name='lista_categorias_despesa'),
    path('categorias-despesa/cadastrar/', views.cadastrar_categoria_despesa, name='cadastrar_categoria_despesa'),
    # --- NOVAS URLs ---
    path('categorias-despesa/<int:pk>/editar/', views.editar_categoria_despesa, name='editar_categoria_despesa'),
    path('categorias-despesa/<int:pk>/excluir/', views.excluir_categoria_despesa, name='excluir_categoria_despesa'),
    # --- FIM NOVAS URLs ---


    # Contas Bancárias/Caixas
    path('contas-bancarias/', views.lista_contas_bancarias, name='lista_contas_bancarias'),
    path('contas-bancarias/nova/', views.criar_conta_bancaria, name='criar_conta_bancaria'),
    path('contas-bancarias/<int:pk>/editar/', views.editar_conta_bancaria, name='editar_conta_bancaria'),
    path('contas-bancarias/<int:pk>/excluir/', views.excluir_conta_bancaria, name='excluir_conta_bancaria'),
    # Se preferir inativar em vez de excluir, pode ser uma view 'alternar_status_conta_bancaria'


    # Fechamento de Caixa
    path('fechamentos/', views.lista_fechamentos_caixa, name='lista_fechamentos_caixa'),
    path('fechamentos/criar/', views.criar_fechamento_caixa, name='criar_fechamento_caixa'),
    path('fechamentos/finalizar/', views.finalizar_fechamento_caixa, name='finalizar_fechamento_caixa'), # Etapa 2: Confirmar e fechar
    path('fechamentos/<int:pk>/', views.detalhe_fechamento_caixa, name='detalhe_fechamento_caixa'),
    path('fechamentos/<int:pk>/reabrir/', views.reabrir_fechamento_caixa, name='reabrir_fechamento_caixa'), # URL para reabrir
    path('fechamentos/<int:pk>/relatorio/', views.relatorio_mensal_detalhe, name='relatorio_financeiro_mensal'), # Mantido



    # ====================================================
    # ========= INÍCIO: URLs PARA FORNECEDORES =========
    # ====================================================
    path('fornecedores/', views.lista_fornecedores, name='lista_fornecedores'),
    path('fornecedores/novo/', views.criar_fornecedor, name='criar_fornecedor'),
    path('fornecedores/<int:pk>/editar/', views.editar_fornecedor, name='editar_fornecedor'),
    # Usaremos uma view para alternar o status ativo/inativo via POST
    path('fornecedores/<int:pk>/alternar-status/', views.alternar_status_fornecedor, name='alternar_status_fornecedor'),
    # Não teremos uma URL de exclusão direta por segurança, usamos o status 'ativo'
    # ==================================================
    # ========= FIM: URLs PARA FORNECEDORES =========
    # ==================================================

    # ====================================================
    # ========= URLs PARA CONTAS A PAGAR (ATUALIZADO) =========
    # ====================================================
    path('contas-pagar/', views.lista_contas_pagar, name='lista_contas_pagar'),
    path('contas-pagar/nova/', views.criar_conta_pagar, name='criar_conta_pagar'),
    path('contas-pagar/<int:pk>/editar/', views.editar_conta_pagar, name='editar_conta_pagar'), # <-- DESCOMENTADO/ADICIONADO
    path('contas-pagar/<int:pk>/detalhes/', views.detalhe_conta_pagar, name='detalhe_conta_pagar'), # <-- ADICIONADO
    path('contas-pagar/<int:pk>/cancelar/', views.cancelar_conta_pagar, name='cancelar_conta_pagar'), # <-- ADICIONADO (em vez de excluir)
    path('contas-pagar/<int:pk>/pagar/', views.registrar_pagamento_conta_pagar, name='registrar_pagamento_conta_pagar'),
    # ==================================================
    # ========= FIM: URLs PARA CONTAS A PAGAR =========
    # ==================================================
]

