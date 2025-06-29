# c:\Gereigreja\contas\urls.py
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views # Sua view de registro

app_name = 'contas'

urlpatterns = [
    # Registro
    path('registrar/', views.registrar_usuario_e_org, name='registrar'),

    # Login / Logout (Exemplo usando views padrão - ajuste se necessário)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'), # Aponta para o template raiz
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'), # Redireciona para login após logout

    # Alteração de Senha (Dentro da área logada)
    path(
        'alterar-senha/',
        login_required(
            auth_views.PasswordChangeView.as_view(
                template_name='contas/password_change_form.html',
                success_url=reverse_lazy('contas:password_change_done')
            )
        ),
        name='password_change'
    ),
    path(
        'alterar-senha/concluido/',
        login_required(
            auth_views.PasswordChangeDoneView.as_view(
                template_name='contas/password_change_done.html'
            )
        ),
        name='password_change_done'
    ),

    # --- URLs PARA RESET DE SENHA (NOVAS/ATUALIZADAS) ---
    path(
        'resetar-senha/',
        auth_views.PasswordResetView.as_view(
            template_name='contas/password_reset_form.html', # Nosso template
            email_template_name='contas/password_reset_email.html', # Template do email (opcional, mas recomendado)
            subject_template_name='contas/password_reset_subject.txt', # Assunto do email (opcional)
            success_url=reverse_lazy('contas:password_reset_done') # Para onde ir após enviar email
        ),
        name='password_reset'
    ),
    path(
        'resetar-senha/enviado/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='contas/password_reset_done.html' # Nosso template
        ),
        name='password_reset_done'
    ),
    path(
        'resetar/<uidb64>/<token>/', # URL que vem no link do email
        auth_views.PasswordResetConfirmView.as_view(
            template_name='contas/password_reset_confirm.html', # Nosso template
            success_url=reverse_lazy('contas:password_reset_complete') # Para onde ir após mudar a senha
        ),
        name='password_reset_confirm'
    ),
    path(
        'resetar/concluido/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='contas/password_reset_complete.html' # Nosso template
        ),
        name='password_reset_complete'
    ),
    path('usuarios/', views.lista_usuarios_org, name='lista_usuarios'),

    path('convidar/', views.enviar_convite, name='enviar_convite'),
    # --- URL PARA ACEITAR CONVITE (NOVA) ---
    # Usa <uuid:token> para capturar o token UUID da URL
    path('aceitar/<uuid:token>/', views.aceitar_convite, name='aceitar_convite'),
    path('convites/<int:pk>/cancelar/', views.cancelar_convite, name='cancelar_convite'),
    
    # --- URL PARA EDITAR PAPÉIS/GRUPOS DE UM USUÁRIO (NOVA) ---
    # Usa <int:user_pk> para capturar a chave primária do User
    path('usuarios/<int:user_pk>/enviar-reset-senha/', views.enviar_link_reset_senha, name='enviar_link_reset_senha'),

    path('usuarios/<int:user_pk>/editar-papeis/', views.editar_papeis_usuario, name='editar_papeis_usuario'),
    # --- URL PARA ATIVAR/DESATIVAR USUÁRIO (NOVA) ---
    # Usa <int:user_pk> para capturar a chave primária do User
    path('usuarios/<int:user_pk>/alternar-status/', views.alternar_status_usuario_org, name='alternar_status_usuario'),
    # --- URL PARA PÁGINA DE AGUARDANDO APROVAÇÃO (NOVA) ---
    path('aguardando-aprovacao/', views.aguardando_aprovacao, name='aguardando_aprovacao'),

    # --- FIM URL ---
    # --- FIM URL ---
    # --- FIM URLs RESET DE SENHA ---
    
]
