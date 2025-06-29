# c:\Gereigreja\core\decorators.py
from functools import wraps
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404

# Importar get_organizacao_or_error de core.utils
from core.utils import get_organizacao_or_error
# Importar AssinaturaOrganizacao para o except
from configuracao.models import AssinaturaOrganizacao
from django.contrib.auth.decorators import login_required # Adicionado
from django.urls import reverse_lazy # Adicionado


def verificar_assinatura_valida(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Se for superuser, permite acesso direto
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Se o request for para a própria página de gerenciar assinatura,
        # permite o acesso para que o usuário possa resolver a situação.
        # A view 'gerenciar_assinatura' ainda chamará get_organizacao_or_error
        # para obter a organização, mas não bloqueará aqui.
        if request.path == reverse('configuracao:gerenciar_assinatura'):
            return view_func(request, *args, **kwargs)

        try:
            # get_organizacao_or_error já verifica se a organização está ativa.
            # Se não estiver, levanta PermissionDenied ou Http404.
            organizacao = get_organizacao_or_error(request)
        except (PermissionDenied, Http404):
            # Se a organização não for encontrada ou estiver inativa,
            # e não for a página de assinatura (já tratada acima),
            # a mensagem de erro já é adicionada por get_organizacao_or_error.
            # Redireciona para login ou página de erro apropriada (a view chamadora pode tratar).
            # Para um decorator, redirecionar para login é uma ação comum.
            return redirect('login') # Ou uma página de erro mais específica

        # Se chegamos aqui, a organização existe e está ativa. Agora verificamos a assinatura.
        try:
            assinatura = organizacao.assinatura # Acesso via related_name
            status_validos = ['ativa', 'gratuita']

            if not (assinatura.status in status_validos or assinatura.is_periodo_cortesia_valido()):
                # Se a assinatura não for válida e não estivermos na página de gerenciamento
                messages.warning(request, f"Sua assinatura do plano {assinatura.plano.get_nome_display() if assinatura.plano else ''} está {assinatura.get_status_display()}. Por favor, regularize sua situação ou ative sua cortesia.")
                return redirect('configuracao:gerenciar_assinatura')

        except AssinaturaOrganizacao.DoesNotExist:
            # Se não tem assinatura E não é elegível para gratuita
            if not organizacao.verificar_elegibilidade_plano_gratuito():
                messages.warning(request, "Sua organização não possui uma assinatura ativa. Por favor, escolha um plano ou ative sua cortesia.")
                return redirect('configuracao:gerenciar_assinatura')

        # Se tudo estiver OK (organização ativa e assinatura válida/cortesia), executa a view.
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
