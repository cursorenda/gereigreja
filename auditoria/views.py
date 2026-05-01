from datetime import timedelta
import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from contas.constants import user_has_permission_level_or_higher, ADMIN_MINISTERIO

from .models import AccessDeniedLog, AuditSession, PermissionChangeLog
from .utils import rodar_auditoria_permissoes

User = get_user_model()


def _get_user_ministerio(user):
    perfil_usuario = getattr(user, 'perfil_usuario', None)
    if perfil_usuario and getattr(perfil_usuario, 'ministerio', None):
        return perfil_usuario.ministerio
    perfil = getattr(user, 'perfil', None)
    if perfil and getattr(perfil, 'ministerio', None):
        return perfil.ministerio
    return None


def _can_access_auditoria(user):
    return user.is_superuser or user_has_permission_level_or_higher(user, ADMIN_MINISTERIO)


def _scope_queryset_by_ministerio(queryset, user):
    if user.is_superuser:
        return queryset
    ministerio = _get_user_ministerio(user)
    if ministerio is None:
        return queryset.none()
    return queryset.filter(ministerio=ministerio)


def _parse_int_param(raw_value, default_value, min_value, max_value):
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return default_value
    return max(min_value, min(max_value, value))


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

    ministerio = _get_user_ministerio(request.user)
    if ministerio and not request.user.is_superuser:
        usuarios_base = User.objects.filter(perfil_usuario__ministerio=ministerio, is_active=True).distinct()
    else:
        usuarios_base = User.objects.filter(is_active=True)

    usuarios_alto_risco = (
        usuarios_base.annotate(num_grupos=Count('groups', distinct=True)).filter(num_grupos__gte=5).count()
    )

    stats = {
        'total_alteracoes': logs_alteracoes_periodo.count(),
        'total_acessos_negados': logs_negados_periodo.count(),
        'usuarios_afetados': logs_alteracoes_periodo.values('usuario_afetado').distinct().count(),
        'sessoes_ativas': sessoes_qs.filter(logout_data_hora__isnull=True).count(),
        'usuarios_alto_risco': usuarios_alto_risco,
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
def auditar_permissoes_view(request):
    if not _can_access_auditoria(request.user):
        messages.error(request, 'Voce nao tem permissao para executar auditoria de permissoes.')
        return redirect('/')

    resultado = None
    if request.method == 'POST':
        resultado = rodar_auditoria_permissoes()

    return render(
        request,
        'auditoria/auditar_permissoes.html',
        {
            'resultado': resultado,
        },
    )


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


@login_required
def alternar_modo_auditoria(request):
    redirect_destino = request.META.get('HTTP_REFERER') or reverse('auditoria:painel_auditoria')

    if not request.user.is_superuser:
        messages.error(request, 'Apenas superusuarios podem alternar o modo auditoria.')
        return redirect(redirect_destino)

    modo_ativo = bool(request.session.get('modo_auditoria', False))
    request.session['modo_auditoria'] = not modo_ativo
    request.session.modified = True

    if modo_ativo:
        messages.info(request, 'Modo auditoria desativado.')
    else:
        messages.info(request, 'Modo auditoria ativado: operacoes sensiveis ficam em somente leitura.')

    return redirect(redirect_destino)


@login_required
def exportar_logs_csv(request):
    if not _can_access_auditoria(request.user):
        messages.error(request, 'Voce nao tem permissao para exportar logs de auditoria.')
        return redirect('/')

    tipo = request.GET.get('tipo', 'alteracoes').strip().lower()
    dias = _parse_int_param(request.GET.get('dias', 30), default_value=30, min_value=1, max_value=365)
    data_inicio = timezone.now() - timedelta(days=dias)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="auditoria_{tipo}_{timezone.now():%Y%m%d_%H%M%S}.csv"'
    writer = csv.writer(response)

    if tipo == 'acessos_negados':
        logs = _scope_queryset_by_ministerio(
            AccessDeniedLog.objects.select_related('usuario', 'ministerio').filter(data_hora__gte=data_inicio),
            request.user,
        )
        writer.writerow(['data_hora', 'usuario', 'tipo_acesso', 'recurso', 'permissao_requerida', 'ministerio', 'ip'])
        for log in logs.iterator():
            writer.writerow([
                log.data_hora.strftime('%Y-%m-%d %H:%M:%S'),
                log.usuario.username,
                log.tipo_acesso,
                log.recurso,
                log.permissao_requerida,
                getattr(log.ministerio, 'nome_fantasia', ''),
                log.ip_address or '',
            ])
        return response

    logs = _scope_queryset_by_ministerio(
        PermissionChangeLog.objects.select_related('usuario_afetado', 'usuario_executor', 'grupo', 'ministerio').filter(
            data_hora__gte=data_inicio
        ),
        request.user,
    )
    writer.writerow(['data_hora', 'usuario_afetado', 'acao', 'grupo', 'executor', 'ministerio', 'ip'])
    for log in logs.iterator():
        writer.writerow([
            log.data_hora.strftime('%Y-%m-%d %H:%M:%S'),
            log.usuario_afetado.username,
            log.acao,
            getattr(log.grupo, 'name', ''),
            getattr(log.usuario_executor, 'username', ''),
            getattr(log.ministerio, 'nome_fantasia', ''),
            log.ip_address or '',
        ])
    return response


@login_required
def analise_atividades_suspeitas(request):
    if not _can_access_auditoria(request.user):
        messages.error(request, 'Voce nao tem permissao para acessar a analise de atividades suspeitas.')
        return redirect('/')

    dias = _parse_int_param(request.GET.get('dias', 7), default_value=7, min_value=1, max_value=90)
    limite = _parse_int_param(request.GET.get('limite', 5), default_value=5, min_value=1, max_value=500)
    data_inicio = timezone.now() - timedelta(days=dias)

    logs_negados_periodo = _scope_queryset_by_ministerio(
        AccessDeniedLog.objects.select_related('usuario', 'ministerio').filter(data_hora__gte=data_inicio),
        request.user,
    )

    usuarios_suspeitos = (
        logs_negados_periodo.values('usuario__username', 'ministerio__nome_fantasia')
        .annotate(total_negados=Count('id'))
        .filter(total_negados__gte=limite)
        .order_by('-total_negados')
    )

    recursos_mais_negados = (
        logs_negados_periodo.values('recurso').annotate(total=Count('id')).order_by('-total')[:10]
    )

    context = {
        'dias': dias,
        'limite': limite,
        'total_logs_periodo': logs_negados_periodo.count(),
        'usuarios_suspeitos': usuarios_suspeitos,
        'recursos_mais_negados': recursos_mais_negados,
        'logs_recentes': logs_negados_periodo.order_by('-data_hora')[:30],
    }
    return render(request, 'auditoria/atividades_suspeitas.html', context)


@login_required
def detalhes_usuario_auditoria(request, user_id):
    if not _can_access_auditoria(request.user):
        messages.error(request, 'Voce nao tem permissao para acessar os detalhes de auditoria.')
        return redirect('/')

    usuario = get_object_or_404(User, pk=user_id)

    alteracoes = _scope_queryset_by_ministerio(
        PermissionChangeLog.objects.filter(usuario_afetado=usuario).select_related('grupo', 'usuario_executor'),
        request.user,
    )[:50]
    acessos_negados = _scope_queryset_by_ministerio(
        AccessDeniedLog.objects.filter(usuario=usuario).select_related('igreja_tentada'),
        request.user,
    )[:50]
    sessoes = _scope_queryset_by_ministerio(
        AuditSession.objects.filter(usuario=usuario).select_related('ministerio', 'igreja_ativa'),
        request.user,
    )[:20]

    stats = {
        'total_alteracoes': _scope_queryset_by_ministerio(
            PermissionChangeLog.objects.filter(usuario_afetado=usuario), request.user
        ).count(),
        'total_acessos_negados': _scope_queryset_by_ministerio(
            AccessDeniedLog.objects.filter(usuario=usuario), request.user
        ).count(),
        'total_sessoes': _scope_queryset_by_ministerio(
            AuditSession.objects.filter(usuario=usuario), request.user
        ).count(),
        'grupos_atuais': usuario.groups.all(),
    }

    context = {
        'usuario_auditado': usuario,
        'alteracoes': alteracoes,
        'acessos_negados': acessos_negados,
        'sessoes': sessoes,
        'stats': stats,
    }
    return render(request, 'auditoria/detalhes_usuario.html', context)


@login_required
def acumulacao_permissoes(request):
    if not _can_access_auditoria(request.user):
        messages.error(request, 'Voce nao tem permissao para acessar acumulacao de permissoes.')
        return redirect('/')

    ministerio = _get_user_ministerio(request.user)
    if ministerio and not request.user.is_superuser:
        usuarios = User.objects.filter(perfil_usuario__ministerio=ministerio, is_active=True).distinct()
    else:
        usuarios = User.objects.filter(is_active=True)

    usuarios_com_permissoes = []
    for usuario in usuarios:
        grupos = usuario.groups.all()
        num_grupos = grupos.count()
        if num_grupos == 0:
            continue
        usuarios_com_permissoes.append(
            {
                'usuario': usuario,
                'num_grupos': num_grupos,
                'grupos': grupos,
                'nivel_risco': 'ALTO' if num_grupos >= 5 else 'MEDIO' if num_grupos >= 3 else 'BAIXO',
            }
        )

    usuarios_com_permissoes.sort(key=lambda item: item['num_grupos'], reverse=True)

    stats = {
        'total_usuarios': len(usuarios_com_permissoes),
        'usuarios_alto_risco': sum(1 for item in usuarios_com_permissoes if item['nivel_risco'] == 'ALTO'),
        'usuarios_medio_risco': sum(1 for item in usuarios_com_permissoes if item['nivel_risco'] == 'MEDIO'),
        'media_grupos': (
            sum(item['num_grupos'] for item in usuarios_com_permissoes) / len(usuarios_com_permissoes)
            if usuarios_com_permissoes
            else 0
        ),
    }

    return render(
        request,
        'auditoria/acumulacao_permissoes.html',
        {
            'usuarios_com_permissoes': usuarios_com_permissoes[:50],
            'stats': stats,
        },
    )


@login_required
def api_estatisticas_auditoria(request):
    if not _can_access_auditoria(request.user):
        return JsonResponse({'error': 'Permissao negada'}, status=403)

    dias = _parse_int_param(request.GET.get('dias', 30), default_value=30, min_value=1, max_value=365)
    data_inicio = timezone.now() - timedelta(days=dias)

    logs_alteracoes_qs = _scope_queryset_by_ministerio(PermissionChangeLog.objects.all(), request.user)
    logs_negados_qs = _scope_queryset_by_ministerio(AccessDeniedLog.objects.all(), request.user)

    serie_alteracoes = []
    serie_acessos_negados = []
    for i in range(dias):
        dia = timezone.now() - timedelta(days=i)
        inicio_dia = dia.replace(hour=0, minute=0, second=0, microsecond=0)
        fim_dia = inicio_dia + timedelta(days=1)

        serie_alteracoes.append(
            {
                'data': inicio_dia.strftime('%d/%m'),
                'total': logs_alteracoes_qs.filter(data_hora__gte=inicio_dia, data_hora__lt=fim_dia).count(),
            }
        )
        serie_acessos_negados.append(
            {
                'data': inicio_dia.strftime('%d/%m'),
                'total': logs_negados_qs.filter(data_hora__gte=inicio_dia, data_hora__lt=fim_dia).count(),
            }
        )

    serie_alteracoes.reverse()
    serie_acessos_negados.reverse()

    distribuicao_acoes = list(
        logs_alteracoes_qs.filter(data_hora__gte=data_inicio)
        .values('acao')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    distribuicao_tipos_negados = list(
        logs_negados_qs.filter(data_hora__gte=data_inicio)
        .values('tipo_acesso')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    top_grupos = list(
        logs_alteracoes_qs.filter(data_hora__gte=data_inicio)
        .values('grupo__name')
        .annotate(total=Count('id'))
        .order_by('-total')[:10]
    )

    return JsonResponse(
        {
            'dias': dias,
            'serie_alteracoes': serie_alteracoes,
            'serie_acessos_negados': serie_acessos_negados,
            'distribuicao_acoes': distribuicao_acoes,
            'distribuicao_tipos_negados': distribuicao_tipos_negados,
            'top_grupos': top_grupos,
        }
    )
