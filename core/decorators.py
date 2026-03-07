# c:\Gereigreja\core\decorators.py
from functools import wraps
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404

# Importar get_ministerio_or_error de core.utils
from core.utils import get_ministerio_or_error
# Importar AssinaturaMinisterio para o except
from configuracao.models import AssinaturaMinisterio
from django.contrib.auth.decorators import login_required # Adicionado
from django.urls import reverse_lazy # Adicionado


def verificar_assinatura_valida(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Permite acesso direto para superusuário
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Permite acesso à página de gerenciamento de assinatura
        if request.path == reverse('configuracao:gerenciar_assinatura'):
            return view_func(request, *args, **kwargs)

        # Obtém ministério e verifica se está ativo
        try:
            ministerio = get_ministerio_or_error(request)
        except (PermissionDenied, Http404):
            # Redireciona para login se ministério não encontrado ou inativo
            return redirect('login')

        # Verifica se ministério possui assinatura ativa
        try:
            assinatura = ministerio.assinatura  # Acesso via related_name
            # Mensagem de assinatura vencida está centralizada em core/utils.py
        except AssinaturaMinisterio.DoesNotExist:
            # Adiciona mensagem se não houver assinatura e não for elegível para plano gratuito
            if not ministerio.verificar_elegibilidade_plano_gratuito():
                msg_sem_assinatura = "Sua ministério não possui uma assinatura ativa. Por favor, escolha um plano ou ative sua cortesia."
                if not any(msg_sem_assinatura in str(m) for m in messages.get_messages(request)):
                    messages.warning(request, msg_sem_assinatura)
                return redirect('configuracao:gerenciar_assinatura')

        # Executa a view se tudo estiver OK
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def check_permission(test_func, login_url_name=None): # Renomeado o parâmetro para clareza
    def decorator(view_func):
        # Calcula a URL de login a ser usada.
        # Passamos o NOME da URL para login_required, que resolverá de forma lazy.
        _login_url_to_use = login_url_name or 'login'


        # Aplica os decorators à função _wrapped_view.
        # @wraps geralmente fica mais próximo da função que está envolvendo.
        @login_required(login_url=_login_url_to_use)
        @wraps(view_func)



        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user): # Executa a função de teste de permissão
                return view_func(request, *args, **kwargs)
            else: # Usuário está logado, mas não tem a permissão
                raise PermissionDenied("Você não tem permissão para acessar esta página.")
        return _wrapped_view
    return decorator


def permission_required_or_403(test_func):
    """
    Decorator que verifica permissão e lança PermissionDenied (mostra 403.html)
    em vez de redirecionar para login.
    
    Uso:
        @permission_required_or_403(lambda u: u.is_superuser or u.groups.filter(name='Pastor').exists())
        def minha_view(request):
            ...
    """
    def decorator(view_func):
        @login_required  # Garante que usuário está autenticado
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                # Lança exceção que será capturada pelo PermissionDeniedMiddleware
                raise PermissionDenied("Você não tem permissão para acessar esta página.")
        return _wrapped_view
    return decorator

# --- DECORATORS EBD ---
from django.contrib.auth.decorators import user_passes_test
from contas.constants import SUPERINTENDENTE_EBD, SECRETARIA_EBD

def user_passes_test_or_403(test_func):
    """
    Versão do user_passes_test que lança PermissionDenied em vez de redirecionar.
    Substitui @user_passes_test(funcao) por @user_passes_test_or_403(funcao)
    """
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied("Você não tem permissão para acessar esta página.")
        return _wrapped_view
    return decorator

def admin_ministerio_required(view_func):
    """Requer Admin Ministerio ou superuser para acessar a view."""
    from contas.constants import user_is_admin
    return user_passes_test_or_403(user_is_admin)(view_func)

def superintendente_required(view_func):
    """Permite acesso a superusers ou membros do grupo 'Superintendente EBD'."""
    test_func = lambda u: u.is_superuser or u.groups.filter(name=SUPERINTENDENTE_EBD).exists()
    return user_passes_test_or_403(test_func)(view_func)

def secretaria_ebd_required(view_func):
    """Permite acesso a superusers, superintendentes ou membros do grupo 'Secretaria EBD'."""
    test_func = lambda u: u.is_superuser or u.groups.filter(name__in=[SUPERINTENDENTE_EBD, SECRETARIA_EBD]).exists()
    return user_passes_test_or_403(test_func)(view_func)

def secretaria_dashboard_required(view_func):
    """
    Permite acesso ao dashboard da secretaria apenas para liderança operacional.
    
    Grupos permitidos:
    - GRUPOS_OPERACIONAL (Secretário Local, Tesoureiro, Superintendente EBD, Pastores)
    - Liderança ministerial (Admin, Lideranças regionais)
    
    Bloqueados:
    - GRUPOS_EQUIPES (Eventos, Mídia, Recepção)
    - Professores EBD
    
    Uso:
        @secretaria_dashboard_required
        def dashboard(request):
            # Apenas liderança/secretaria acessam
            ...
    """
    from contas.constants import GRUPOS_OPERACIONAL
    
    test_func = lambda u: u.is_superuser or u.groups.filter(
        name__in=GRUPOS_OPERACIONAL
    ).exists()
    
    return user_passes_test_or_403(test_func)(view_func)
