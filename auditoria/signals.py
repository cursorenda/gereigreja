import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.signals import user_logged_out
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils import timezone

from .models import AccessDeniedLog, AuditPageView, AuditSession, PermissionChangeLog

logger = logging.getLogger(__name__)
User = get_user_model()


def obter_ip_do_usuario(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _obter_ministerio_usuario(usuario):
    perfil_usuario = getattr(usuario, 'perfil_usuario', None)
    if perfil_usuario and getattr(perfil_usuario, 'ministerio', None):
        return perfil_usuario.ministerio

    perfil = getattr(usuario, 'perfil', None)
    if perfil and getattr(perfil, 'ministerio', None):
        return perfil.ministerio

    return None


@receiver(m2m_changed, sender=User.groups.through)
def registrar_mudanca_grupos(sender, instance, action, reverse, pk_set, **kwargs):
    if action not in ['post_add', 'post_remove'] or not pk_set:
        return

    acao = 'ADD' if action == 'post_add' else 'REMOVE'

    try:
        if reverse:
            grupo = instance
            usuarios = User.objects.filter(pk__in=pk_set)
            for usuario in usuarios:
                PermissionChangeLog.objects.create(
                    usuario_afetado=usuario,
                    grupo=grupo,
                    acao=acao,
                    usuario_executor=None,
                    ministerio=_obter_ministerio_usuario(usuario),
                    observacao='Mudanca automatica de grupo via signal',
                )
            return

        usuario = instance
        grupos = Group.objects.filter(pk__in=pk_set)
        for grupo in grupos:
            PermissionChangeLog.objects.create(
                usuario_afetado=usuario,
                grupo=grupo,
                acao=acao,
                usuario_executor=None,
                ministerio=_obter_ministerio_usuario(usuario),
                observacao='Mudanca automatica de grupo via signal',
            )
    except Exception:
        logger.exception('Erro ao registrar mudanca de grupos')


def registrar_acesso_negado(usuario, tipo_acesso, recurso, permissao_requerida='', request=None, igreja=None, ministerio=None):
    try:
        ministerio = ministerio or _obter_ministerio_usuario(usuario)
        AccessDeniedLog.objects.create(
            usuario=usuario,
            tipo_acesso=tipo_acesso,
            recurso=recurso,
            permissao_requerida=permissao_requerida,
            igreja_tentada=igreja,
            ip_address=obter_ip_do_usuario(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255] if request else '',
            url_path=request.path[:500] if request else '',
            metodo_http=request.method if request else '',
            ministerio=ministerio,
        )
    except Exception:
        logger.exception('Erro ao registrar acesso negado')


def registrar_login_usuario(usuario, request):
    try:
        AuditSession.objects.create(
            usuario=usuario,
            ip_address=obter_ip_do_usuario(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255] if request else '',
            ministerio=_obter_ministerio_usuario(usuario),
            igreja_ativa=getattr(request, 'igreja_ativa', None),
        )
    except Exception:
        logger.exception('Erro ao registrar login de auditoria')


def registrar_logout_usuario(usuario):
    try:
        sessao = AuditSession.objects.filter(
            usuario=usuario,
            logout_data_hora__isnull=True,
        ).order_by('-login_data_hora').first()
        if sessao:
            sessao.logout_data_hora = timezone.now()
            sessao.save(update_fields=['logout_data_hora'])
    except Exception:
        logger.exception('Erro ao registrar logout de auditoria')


def incrementar_contador_paginas(usuario):
    try:
        sessao = AuditSession.objects.filter(
            usuario=usuario,
            logout_data_hora__isnull=True,
        ).order_by('-login_data_hora').first()
        if sessao:
            sessao.paginas_visitadas += 1
            sessao.save(update_fields=['paginas_visitadas'])
    except Exception:
        logger.exception('Erro ao incrementar contador de paginas')


def registrar_pageview_usuario(usuario, request, response, duracao_ms=None):
    try:
        if not request or not response:
            return

        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return

        if getattr(response, 'status_code', 0) < 200 or getattr(response, 'status_code', 0) >= 400:
            return

        sessao = AuditSession.objects.filter(
            usuario=usuario,
            logout_data_hora__isnull=True,
        ).order_by('-login_data_hora').first()

        query_string = (request.META.get('QUERY_STRING', '') or '')[:1000]

        AuditPageView.objects.create(
            usuario=usuario,
            sessao=sessao,
            ministerio=_obter_ministerio_usuario(usuario),
            ip_address=obter_ip_do_usuario(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            referer=request.META.get('HTTP_REFERER', '')[:500],
            metodo_http=(request.method or 'GET')[:10],
            path=(request.path or '')[:500],
            query_string=query_string,
            status_code=int(getattr(response, 'status_code', 200) or 200),
            duracao_ms=duracao_ms,
        )
    except Exception:
        logger.exception('Erro ao registrar pageview de auditoria')


@receiver(user_logged_out)
def fechar_sessao_ao_logout(sender, user, request, **kwargs):
    if user and user.is_authenticated:
        registrar_logout_usuario(user)
