from django.http import HttpResponseForbidden

from .signals import incrementar_contador_paginas, registrar_acesso_negado, registrar_login_usuario
from .utils import modo_auditoria_ativo


class BloquearEscritaModoAuditoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and request.user.is_superuser
            and modo_auditoria_ativo(request)
            and request.method in ('POST', 'PUT', 'PATCH', 'DELETE')
            and request.path != '/auditoria/alternar-modo/'
            and not request.path.startswith('/admin/')
        ):
            return HttpResponseForbidden('Acao bloqueada: Modo Auditoria ativo. Apenas leitura e permitida.')
        return self.get_response(request)


class RegistrarAuditoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.session.get('auditoria_login_registrado'):
                registrar_login_usuario(request.user, request)
                request.session['auditoria_login_registrado'] = True
                request.session.modified = True

            if request.method == 'GET' and not request.path.startswith('/static/') and not request.path.startswith('/media/'):
                incrementar_contador_paginas(request.user)

        return self.get_response(request)


class CapturarAcessoNegadoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 403 and request.user.is_authenticated:
            registrar_acesso_negado(
                usuario=request.user,
                tipo_acesso=self._determinar_tipo_acesso(request.path),
                recurso=f'{request.method} {request.path}',
                request=request,
            )
        return response

    @staticmethod
    def _determinar_tipo_acesso(path):
        if '/api/' in path:
            return 'API'
        if 'delete' in path or 'remover' in path or 'excluir' in path:
            return 'ACTION'
        if 'detail' in path or 'view' in path:
            return 'VIEW'
        return 'ACTION'
