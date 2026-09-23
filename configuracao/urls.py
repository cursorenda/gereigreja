# configuracao/urls.py
from . import views
from .views_dashboard import api_metricas_sistema
from .views_permissions import auditoria_permissoes, comparar_usuario_grupo, exportar_relatorio_permissions
from django.urls import path
# Importar views de autenticação do Django
from django.contrib.auth import views as auth_views
# Importar decorator para exigir login
from django.contrib.auth.decorators import login_required
# Importar reverse_lazy para URLs de sucesso
from django.urls import reverse_lazy
from .views import validar_imagens_perfil
from .views_localidades import api_buscar_cidades
from django.conf import settings
from django.conf.urls.static import static # Importar static

app_name = 'configuracao' # Define o namespace
 
urlpatterns = [
    # URL Principal de Configuração (agora lista as igrejas)
    path('', views.configuracao_view, name='configuracao'), # Aponta para a view refatorada
    path('meu-ministerio/', views.detalhes_ministerio, name='detalhes_ministerio'),
    path('meu-ministerio/centro/', views.centro_ministerial, name='centro_ministerial'),
    path('meu-ministerio/editar/', views.editar_ministerio, name='editar_ministerio'),
    path('meu-ministerio/carteirinha/', views.carteirinha_ministerio, name='carteirinha_ministerio'),
    path('meu-ministerio/configuracoes/', views.configuracoes_ministerio, name='configuracoes_ministerio'),
 
    # URL para Gerenciar Assinatura
    path('assinatura/', views.gerenciar_assinatura, name='gerenciar_assinatura'),
    path('assinatura/minha-assinatura/', views.minha_assinatura, name='minha_assinatura'),


    # Portal do cliente Stripe (gerenciar cartão, faturas, cancelamento)
    path('assinatura/portal/', views.abrir_billing_portal, name='billing_portal'),

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
    path('igrejas/<int:igreja_id>/programacoes/adicionar/', views.adicionar_programacao_padrao_igreja, name='adicionar_programacao_padrao_igreja'),
    path('igrejas/<int:igreja_id>/programacoes/<int:programacao_id>/excluir/', views.excluir_programacao_padrao_igreja, name='excluir_programacao_padrao_igreja'),
    path('igrejas/<int:igreja_id>/programacoes/sincronizar/', views.sincronizar_programacoes_padrao_igreja, name='sincronizar_programacoes_padrao_igreja'),
    path('igrejas/<int:igreja_id>/excluir/', views.excluir_igreja, name='excluir_igreja'),    
    path('departamentos/', views.gestao_departamentos, name='gestao_departamentos'),
    path('meus-departamentos/', views.meus_departamentos, name='meus_departamentos'),
    path('departamentos/ministeriais/', views.gestao_departamentos_ministeriais, name='gestao_departamentos_ministeriais'),
    path('definir-igreja-ativa/', views.set_active_church, name='set_active_church'), # Nova URL
    path('configuracoes/', views.configuracoes_sistema_legacy_redirect, name='configuracoes_sistema'),


    
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

    path('perfil/', views.meu_perfil, name='meu_perfil'),
    path('perfil/editar/', views.editar_meu_perfil, name='editar_meu_perfil'),
    path('perfil/<int:user_id>/', views.perfil_usuario, name='perfil_usuario'),

    #path('admin/validar-imagens/',views.validar_imagens_perfil, name='validar_imagens'),
    path('validar-imagens/', views.validar_imagens_perfil, name='validar_imagens'),
    
    # Dashboard do Sistema (uso interno do admin)
    path('api/metricas-sistema/', login_required(api_metricas_sistema), name='api_metricas_sistema'),
    path('api/localidades/cidades/', api_buscar_cidades, name='api_buscar_cidades'),
    
    # Auditoria de Permissões
    path('auditoria-permissoes/', auditoria_permissoes, name='auditoria_permissoes'),
    path('comparar-usuario-grupo/<int:user_id>/<int:group_id>/', comparar_usuario_grupo, name='comparar_usuario_grupo'),
    path('exportar-relatorio-permissions/', exportar_relatorio_permissions, name='exportar_relatorio_permissions'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

