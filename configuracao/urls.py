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
 
    # ====================================================
    # ========= INÍCIO: URLs PARA GERENCIAR IGREJAS =========
    # ====================================================
    path('igrejas/', views.lista_igrejas, name='lista_igrejas'),
    path('igrejas/adicionar/', views.adicionar_igreja, name='adicionar_igreja'),
    # path('igrejas/<int:igreja_id>/editar/', views.editar_igreja, name='editar_igreja'), # Se você já tem uma, pode adaptar
    path('igrejas/<int:igreja_id>/editar-config/', views.editar_igreja_config, name='editar_igreja_config'), # Nova URL
    path('igrejas/<int:igreja_id>/excluir/', views.excluir_igreja, name='excluir_igreja'),    

    
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
]