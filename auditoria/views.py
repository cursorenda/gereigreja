from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import redirect, render
from django.utils import timezone

from contas.constants import user_has_permission_level_or_higher

from .models import AccessDeniedLog, AuditSession, PermissionChangeLog


def _get_user_ministerio(user):
    perfil_usuario = getattr(user, 'perfil_usuario', None)
    if perfil_usuario and getattr(perfil_usuario, 'ministerio', None):
        return perfil_usuario.ministerio
    perfil = getattr(user, 'perfil', None)
    if perfil and getattr(perfil, 'ministerio', None):
        return perfil.ministerio
    return None


def _can_access_auditoria(user):
    return user.is_superuser or user_has_permission_level_or_higher(user, 'ADMIN_MINISTERIO')


def _scope_queryset_by_ministerio(queryset, user):
    if user.is_superuser:
        return queryset
    ministerio = _get_user_ministerio(user)
    if ministerio is None:
        return queryset.none()
    return queryset.filter(ministerio=ministerio)


@login_required
def painel_auditoria(request):
    if not _can_access_auditoria(request.user):
        messages.error(request, 'Voce nao tem permissao para acessar o painel de auditoria.')
        return redirect('/')

    dias = int(request.GET.get('dias', 30) or 30)
    data_inicio = timezone.now() - timedelta(days=dias)

    logs_alteracoes_qs = _scope_queryset_by_ministerio(PermissionChangeLog.objects.all(), request.user)
    logs_negados_qs = _scope_queryset_by_ministerio(AccessDeniedLog.objects.all(), request.user)
    sessoes_qs = _scope_queryset_by_ministerio(AuditSession.objects.all(), request.user)

    logs_alteracoes_periodo = logs_alteracoes_qs.filter(data_hora__gte=data_inicio)
    logs_negados_periodo = logs_negados_qs.filter(data_hora__gte=data_inicio)

    stats = {
        'total_alteracoes': logs_alteracoes_periodo.count(),
        'total_acessos_negados': logs_negados_periodo.count(),
        'usuarios_afetados': logs_alteracoes_periodo.values('usuario_afetado').distinct().count(),
        'sessoes_ativas': sessoes_qs.filter(logout_data_hora__isnull=True).count(),
    }

    distribuicao_acoes = logs_alteracoes_periodo.values('acao').annotate(total=Count('id')).order_by('-total')

    context = {
        'dias': dias,
        'stats': stats,
        'distribuicao_acoes': distribuicao_acoes,
        'logs_alteracoes_recentes': logs_alteracoes_qs.select_related('usuario_afetado', 'grupo', 'usuario_executor')[:15],
        'logs_negados_recentes': logs_negados_qs.select_related('usuario', 'igreja_tentada')[:15],
    }
    return render(request, 'auditoria/painel_auditoria.html', context)


@login_required
def logs_alteracoes_permissoes(request):
    if not _can_access_auditoria(request.user):
        messages.error(request, 'Voce nao tem permissao para acessar os logs de alteracoes.')
        return redirect('/')

    logs = _scope_queryset_by_ministerio(
        PermissionChangeLog.objects.select_related('usuario_afetado', 'grupo', 'usuario_executor'),
        request.user,
    )

    acao = request.GET.get('acao', '').strip()
    usuario = request.GET.get('usuario', '').strip()
    if acao:
        logs = logs.filter(acao=acao)
    if usuario:
        logs = logs.filter(usuario_afetado__username__icontains=usuario)

    paginator = Paginator(logs, 50)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(
        request,
        'auditoria/logs_alteracoes.html',
        {
            'page_obj': page_obj,
            'acao': acao,
            'usuario': usuario,
            'acoes_disponiveis': PermissionChangeLog.ACAO_CHOICES,
        },
    )


@login_required
def logs_acessos_negados(request):
    if not _can_access_auditoria(request.user):
        messages.error(request, 'Voce nao tem permissao para acessar os logs de acesso negado.')
        return redirect('/')

    logs = _scope_queryset_by_ministerio(
        AccessDeniedLog.objects.select_related('usuario', 'igreja_tentada'),
        request.user,
    )

    tipo = request.GET.get('tipo', '').strip()
    usuario = request.GET.get('usuario', '').strip()
    if tipo:
        logs = logs.filter(tipo_acesso=tipo)
    if usuario:
        logs = logs.filter(usuario__username__icontains=usuario)

    paginator = Paginator(logs, 50)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(
        request,
        'auditoria/logs_acessos_negados.html',
        {
            'page_obj': page_obj,
            'tipo': tipo,
            'usuario': usuario,
            'tipos_disponiveis': AccessDeniedLog.TIPO_CHOICES,
        },
    )


@login_required
def sessoes_ativas(request):
    if not _can_access_auditoria(request.user):
        messages.error(request, 'Voce nao tem permissao para acessar sessoes ativas.')
        return redirect('/')

    sessoes = _scope_queryset_by_ministerio(
        AuditSession.objects.select_related('usuario', 'ministerio', 'igreja_ativa').filter(logout_data_hora__isnull=True),
        request.user,
    )

    paginator = Paginator(sessoes, 50)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'auditoria/sessoes_ativas.html', {'page_obj': page_obj})
