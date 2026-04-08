from django.http import HttpResponseForbidden
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from .utils import modo_auditoria_ativo
from .signals import (
    registrar_login_usuario,
    registrar_logout_usuario,
    incrementar_contador_paginas,
    registrar_acesso_negado,
)


class BloquearEscritaModoAuditoriaMiddleware:
    """
    Middleware que bloqueia requisições POST, PUT, DELETE se modo auditoria estiver ativo.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if modo_auditoria_ativo(request) and request.method in ("POST", "PUT", "DELETE"):
            return HttpResponseForbidden("Ação bloqueada: Modo Auditoria ativo. Apenas leitura é permitida.")
        return self.get_response(request)


class RegistrarAuditoriaMiddleware:
    """
    Middleware para registrar eventos de auditoria.
    - Rastreia logins/logouts
    - Incrementa contador de páginas visitadas
    - Registra atributos de sessão (igreja_ativa)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        usuario = request.user
        
        # Verificar login (usuário não é anônimo)
        if not isinstance(usuario, AnonymousUser):
            # Rastrear login se o usuário não estava registrado na sessão
            if not request.session.get('auditoria_login_registrado'):
                registrar_login_usuario(usuario, request)
                request.session['auditoria_login_registrado'] = True
                request.session.modified = True
            
            # Incrementar contador de páginas para requisições GET
            if request.method == 'GET':
                incrementar_contador_paginas(usuario)
            
            # Armazenar Igreja Ativa na sessão de auditoria (opcional - feito pelo middleware ActiveChurch)
            # Isso é capturado no signal ao registrar o login
        
        response = self.get_response(request)
        
        return response


class CapturarAcessoNegadoMiddleware:
    """
    Middleware para registrar tentativas de acesso negado (403 Forbidden).
    Útil para detectar tentativas de acesso não autorizado.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Registrar acessos negados 403
        if response.status_code == 403 and request.user.is_authenticated:
            recurso = f"{request.method} {request.path}"
            tipo_acesso = self._determinar_tipo_acesso(request.path)
            
            registrar_acesso_negado(
                usuario=request.user,
                tipo_acesso=tipo_acesso,
                recurso=recurso,
                request=request,
            )
        
        return response
    
    @staticmethod
    def _determinar_tipo_acesso(path):
        """
        Determina o tipo de acesso baseado na URL.
        """
        if '/api/' in path:
            return 'API'
        elif 'delete' in path or 'remover' in path:
            return 'ACTION'
        elif 'detail' in path or 'view' in path:
            return 'VIEW'
        else:
            return 'ACTION'
