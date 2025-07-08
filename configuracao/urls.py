# configuracao/urls.py
from . import views
from django.urls import path
# Importar views de autenticação do Django
from django.contrib.auth import views as auth_views
# Importar decorator para exigir login
from django.contrib.auth.decorators import login_required
# Importar reverse_lazy para URLs de sucesso
from django.urls import reverse_lazy

app_name = 'configuracao' # Define o namespace
 
urlpatterns = [
    # URL Principal de Configuração (agora lista as igrejas)
    path('', views.configuracao_view, name='configuracao'), # Aponta para a view refatorada
    path('minha-organizacao/', views.detalhes_organizacao, name='detalhes_organizacao'),
    path('minha-organizacao/editar/', views.editar_organizacao, name='editar_organizacao'),
 
    # URL para Gerenciar Assinatura
    path('assinatura/', views.gerenciar_assinatura, name='gerenciar_assinatura'),

    # --- NOVA URL PARA WEBHOOK DO STRIPE ---
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),

    #path('processar-pagamento-teste/', views.processar_pagamento_teste, name='processar_pagamento_teste'),
    # --- NOVA URL PARA ATUALIZAÇÕES DO SISTEMA ---
    path('novidades/', login_required(views.lista_atualizacoes_sistema), name='lista_atualizacoes_sistema'),

    # ====================================================
    # ========= INÍCIO: URLs PARA GERENCIAR IGREJAS =========
    # ====================================================
    path('igrejas/', views.lista_igrejas, name='lista_igrejas'),
    path('igrejas/adicionar/', views.adicionar_igreja, name='adicionar_igreja'),
    # path('igrejas/<int:igreja_id>/editar/', views.editar_igreja, name='editar_igreja'), # Se você já tem uma, pode adaptar
    path('igrejas/<int:igreja_id>/editar-config/', views.editar_igreja_config, name='editar_igreja_config'), # Nova URL
    path('igrejas/<int:igreja_id>/excluir/', views.excluir_igreja, name='excluir_igreja'),    
    path('definir-igreja-ativa/', views.set_active_church, name='set_active_church'), # Nova URL

    
    # ==================================================
    # ========= FIM: URLs PARA GERENCIAR IGREJAS =========
    # ==================================================
 
    path(
        'alterar-senha/',
        login_required( # Garante que só usuários logados acessem
            auth_views.PasswordChangeView.as_view(
                template_name='configuracao/password_change_form.html', # Nosso template customizado
                success_url=reverse_lazy('configuracao:password_change_done') # URL para onde ir após sucesso
            )
        ),
        name='password_change'
    ),
    path(
        'alterar-senha/concluido/',
        login_required( # Garante que só usuários logados acessem
            auth_views.PasswordChangeDoneView.as_view(
                template_name='configuracao/password_change_done.html' # Nosso template customizado de sucesso
            )
        ),
        name='password_change_done'
    ),
    # Outras URLs que você possa ter (login, etc., podem estar no urls.py principal)
    path('perfil/', views.meu_perfil, name='meu_perfil'), # <--- AQUI!
    path('perfil/editar/', views.editar_meu_perfil, name='editar_meu_perfil'), # <-- NOVA URL

]