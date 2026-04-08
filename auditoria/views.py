
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator

from .utils import rodar_auditoria_permissoes
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PermissionChangeLog, AccessDeniedLog, AuditSession
from contas.constants import HIERARQUIA_GRUPOS, user_has_permission_level_or_higher
from configuracao.models import Ministerio

@staff_member_required
def auditar_permissoes_view(request):
    resultado = None
    if request.method == 'POST':
        resultado = rodar_auditoria_permissoes()
    return render(request, 'auditoria/auditar_permissoes.html', {'resultado': resultado})


@login_required
def alternar_modo_auditoria(request):
    if not request.user.is_superuser:
        messages.error(request, "Apenas superusuários podem alternar o modo auditoria.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    flag = request.session.get('modo_auditoria', False)
    request.session['modo_auditoria'] = not flag
    request.session.modified = True
    if not flag:
        messages.info(request, "Modo Auditoria ativado: navegação somente leitura.")
    else:
        messages.info(request, "Modo Auditoria desativado: permissões normais restauradas.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def painel_auditoria(request):
    """
    Painel principal de auditoria de permissões.
    Mostra estatísticas, logs recentes e gráficos de atividade.
    
    Permissão: ADMIN_MINISTERIO ou superior
    """
    # Verifica permissão
    if not user_has_permission_level_or_higher(request.user, 'ADMIN_MINISTERIO'):
        messages.error(request, "Você não tem permissão para acessar o painel de auditoria.")
        return redirect('/')
    
    # Obtém filtros
    dias = int(request.GET.get('dias', 30))
    data_inicio = timezone.now() - timedelta(days=dias)
    
    # Filtra pelo ministério do usuário (se aplicável)
    ministerio = getattr(request.user, 'perfil_usuario', None)
    ministerio = ministerio.ministerio if ministerio else None
    
    # Estatísticas gerais
    stats = {
        'total_alteracoes': PermissionChangeLog.objects.filter(
            data_hora__gte=data_inicio,
            ministerio=ministerio if ministerio else None
        ).count() if ministerio else PermissionChangeLog.objects.filter(data_hora__gte=data_inicio).count(),
        
        'total_acessos_negados': AccessDeniedLog.objects.filter(
            data_hora__gte=data_inicio,
            ministerio=ministerio if ministerio else None
        ).count() if ministerio else AccessDeniedLog.objects.filter(data_hora__gte=data_inicio).count(),
        
        'usuarios_afetados': PermissionChangeLog.objects.filter(
            data_hora__gte=data_inicio,
            ministerio=ministerio if ministerio else None
        ).values('usuario_afetado').distinct().count() if ministerio else PermissionChangeLog.objects.filter(
            data_hora__gte=data_inicio
        ).values('usuario_afetado').distinct().count(),
        
        'sessoes_ativas': AuditSession.objects.filter(
            logout_data_hora__isnull=True,
            ministerio=ministerio if ministerio else None
        ).count() if ministerio else AuditSession.objects.filter(logout_data_hora__isnull=True).count(),
    }
    
    # Logs recentes de alterações
    logs_alteracoes = PermissionChangeLog.objects.select_related(
        'usuario_afetado', 'grupo', 'usuario_executor'
    ).filter(
        ministerio=ministerio if ministerio else None
    )[:20] if ministerio else PermissionChangeLog.objects.select_related(
        'usuario_afetado', 'grupo', 'usuario_executor'
    )[:20]
    
    # Logs recentes de acessos negados
    logs_negados = AccessDeniedLog.objects.select_related(
        'usuario', 'igreja_tentada'
    ).filter(
        ministerio=ministerio if ministerio else None
    )[:20] if ministerio else AccessDeniedLog.objects.select_related(
        'usuario', 'igreja_tentada'
    )[:20]
    
    # Top 5 usuários com mais alterações
    top_usuarios_alterados = PermissionChangeLog.objects.filter(
        data_hora__gte=data_inicio,
        ministerio=ministerio if ministerio else None
    ).values(
        'usuario_afetado__username'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5] if ministerio else PermissionChangeLog.objects.filter(
        data_hora__gte=data_inicio
    ).values(
        'usuario_afetado__username'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    # Top 5 usuários com mais acessos negados
    top_usuarios_negados = AccessDeniedLog.objects.filter(
        data_hora__gte=data_inicio,
        ministerio=ministerio if ministerio else None
    ).values(
        'usuario__username'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5] if ministerio else AccessDeniedLog.objects.filter(
        data_hora__gte=data_inicio
    ).values(
        'usuario__username'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    # Distribuição por tipo de ação
    distribuicao_acoes = PermissionChangeLog.objects.filter(
        data_hora__gte=data_inicio,
        ministerio=ministerio if ministerio else None
    ).values(
        'acao'
    ).annotate(
        total=Count('id')
    ).order_by('-total') if ministerio else PermissionChangeLog.objects.filter(
        data_hora__gte=data_inicio
    ).values(
        'acao'
    ).annotate(
        total=Count('id')
    ).order_by('-total')
    
    context = {
        'stats': stats,
        'logs_alteracoes': logs_alteracoes,
        'logs_negados': logs_negados,
        'top_usuarios_alterados': top_usuarios_alterados,
        'top_usuarios_negados': top_usuarios_negados,
        'distribuicao_acoes': distribuicao_acoes,
        'dias': dias,
        'ministerio': ministerio,
    }
    
    return render(request, 'auditoria/painel_auditoria.html', context)


@login_required
def logs_alteracoes_permissoes(request):
    """
    Lista completa de logs de alterações de permissões.
    Permite filtrar por usuário, grupo, período, etc.
    
    Permissão: ADMIN_MINISTERIO ou superior
    """
    if not user_has_permission_level_or_higher(request.user, 'ADMIN_MINISTERIO'):
        messages.error(request, "Você não tem permissão para acessar os logs.")
        return redirect('/')
    
    # Filtros
    ministerio = getattr(request.user, 'perfil_usuario', None)
    ministerio = ministerio.ministerio if ministerio else None
    
    logs = PermissionChangeLog.objects.select_related(
        'usuario_afetado', 'grupo', 'usuario_executor'
    )
    
    if ministerio:
        logs = logs.filter(ministerio=ministerio)
    
    # Filtros da URL
    usuario_id = request.GET.get('usuario')
    grupo_id = request.GET.get('grupo')
    acao = request.GET.get('acao')
    dias = request.GET.get('dias')
    
    if usuario_id:
        logs = logs.filter(usuario_afetado_id=usuario_id)
    
    if grupo_id:
        logs = logs.filter(grupo_id=grupo_id)
    
    if acao:
        logs = logs.filter(acao=acao)
    
    if dias:
        data_inicio = timezone.now() - timedelta(days=int(dias))
        logs = logs.filter(data_hora__gte=data_inicio)
    
    # Paginação
    paginator = Paginator(logs, 50)
    page = request.GET.get('page', 1)
    logs_page = paginator.get_page(page)
    
    # Dados para filtros
    usuarios = User.objects.filter(
        id__in=PermissionChangeLog.objects.values_list('usuario_afetado_id', flat=True).distinct()
    )
    grupos = Group.objects.filter(
        id__in=PermissionChangeLog.objects.values_list('grupo_id', flat=True).distinct()
    )
    
    context = {
        'logs': logs_page,
        'usuarios': usuarios,
        'grupos': grupos,
        'acoes': PermissionChangeLog.ACAO_CHOICES,
        'filtros_ativos': {
            'usuario': usuario_id,
            'grupo': grupo_id,
            'acao': acao,
            'dias': dias,
        }
    }
    
    return render(request, 'auditoria/logs_alteracoes.html', context)


@login_required
def logs_acessos_negados(request):
    """
    Lista completa de logs de acessos negados.
    Permite identificar problemas de permissão e tentativas suspeitas.
    
    Permissão: ADMIN_MINISTERIO ou superior
    """
    if not user_has_permission_level_or_higher(request.user, 'ADMIN_MINISTERIO'):
        messages.error(request, "Você não tem permissão para acessar os logs.")
        return redirect('/')
    
    # Filtros
    ministerio = getattr(request.user, 'perfil_usuario', None)
    ministerio = ministerio.ministerio if ministerio else None
    
    logs = AccessDeniedLog.objects.select_related(
        'usuario', 'igreja_tentada'
    )
    
    if ministerio:
        logs = logs.filter(ministerio=ministerio)
    
    # Filtros da URL
    usuario_id = request.GET.get('usuario')
    tipo_acesso = request.GET.get('tipo')
    recurso = request.GET.get('recurso')
    dias = request.GET.get('dias')
    
    if usuario_id:
        logs = logs.filter(usuario_id=usuario_id)
    
    if tipo_acesso:
        logs = logs.filter(tipo_acesso=tipo_acesso)
    
    if recurso:
        logs = logs.filter(recurso__icontains=recurso)
    
    if dias:
        data_inicio = timezone.now() - timedelta(days=int(dias))
        logs = logs.filter(data_hora__gte=data_inicio)
    
    # Paginação
    paginator = Paginator(logs, 50)
    page = request.GET.get('page', 1)
    logs_page = paginator.get_page(page)
    
    # Dados para filtros
    usuarios = User.objects.filter(
        id__in=AccessDeniedLog.objects.values_list('usuario_id', flat=True).distinct()
    )
    
    context = {
        'logs': logs_page,
        'usuarios': usuarios,
        'tipos_acesso': AccessDeniedLog.TIPO_CHOICES,
        'filtros_ativos': {
            'usuario': usuario_id,
            'tipo': tipo_acesso,
            'recurso': recurso,
            'dias': dias,
        }
    }
    
    return render(request, 'auditoria/logs_acessos_negados.html', context)


@login_required
def detalhes_usuario_auditoria(request, user_id):
    """
    Detalhes de auditoria de um usuário específico.
    Mostra histórico completo de alterações, acessos negados e sessões.
    
    Permissão: ADMIN_MINISTERIO ou superior
    """
    if not user_has_permission_level_or_higher(request.user, 'ADMIN_MINISTERIO'):
        messages.error(request, "Você não tem permissão para acessar os detalhes.")
        return redirect('/')
    
    usuario = get_object_or_404(User, pk=user_id)
    
    # Histórico de alterações
    alteracoes = PermissionChangeLog.objects.filter(
        usuario_afetado=usuario
    ).select_related('grupo', 'usuario_executor')[:50]
    
    # Acessos negados
    acessos_negados = AccessDeniedLog.objects.filter(
        usuario=usuario
    ).select_related('igreja_tentada')[:50]
    
    # Sessões recentes
    sessoes = AuditSession.objects.filter(
        usuario=usuario
    )[:20]
    
    # Estatísticas do usuário
    stats = {
        'total_alteracoes': PermissionChangeLog.objects.filter(usuario_afetado=usuario).count(),
        'total_acessos_negados': AccessDeniedLog.objects.filter(usuario=usuario).count(),
        'total_sessoes': AuditSession.objects.filter(usuario=usuario).count(),
        'grupos_atuais': usuario.groups.all(),
        'ultima_alteracao': PermissionChangeLog.objects.filter(usuario_afetado=usuario).first(),
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
def api_estatisticas_auditoria(request):
    """
    API JSON para gráficos e estatísticas do painel.
    Retorna dados agregados para visualizações.
    
    Permissão: ADMIN_MINISTERIO ou superior
    """
    if not user_has_permission_level_or_higher(request.user, 'ADMIN_MINISTERIO'):
        return JsonResponse({'error': 'Permissão negada'}, status=403)
    
    dias = int(request.GET.get('dias', 30))
    data_inicio = timezone.now() - timedelta(days=dias)
    
    ministerio = getattr(request.user, 'perfil_usuario', None)
    ministerio = ministerio.ministerio if ministerio else None
    
    # Série temporal de alterações (últimos N dias)
    serie_alteracoes = []
    for i in range(dias):
        data = timezone.now() - timedelta(days=i)
        data_inicio_dia = data.replace(hour=0, minute=0, second=0, microsecond=0)
        data_fim_dia = data_inicio_dia + timedelta(days=1)
        
        count = PermissionChangeLog.objects.filter(
            data_hora__gte=data_inicio_dia,
            data_hora__lt=data_fim_dia,
            ministerio=ministerio if ministerio else None
        ).count() if ministerio else PermissionChangeLog.objects.filter(
            data_hora__gte=data_inicio_dia,
            data_hora__lt=data_fim_dia
        ).count()
        
        serie_alteracoes.append({
            'data': data.strftime('%d/%m'),
            'total': count
        })
    
    serie_alteracoes.reverse()  # Ordem cronológica
    
    # Distribuição por grupo
    distribuicao_grupos = list(PermissionChangeLog.objects.filter(
        data_hora__gte=data_inicio,
        ministerio=ministerio if ministerio else None
    ).values(
        'grupo__name'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:10]) if ministerio else list(PermissionChangeLog.objects.filter(
        data_hora__gte=data_inicio
    ).values(
        'grupo__name'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:10])
    
    data = {
        'serie_alteracoes': serie_alteracoes,
        'distribuicao_grupos': distribuicao_grupos,
    }
    
    return JsonResponse(data)


@login_required
def sessoes_ativas(request):
    """
    Dashboard de sessões ativas de usuários.
    Mostra quem está usando o sistema agora e há quanto tempo.
    
    Permissão: ADMIN_MINISTERIO ou superior
    """
    if not user_has_permission_level_or_higher(request.user, 'ADMIN_MINISTERIO'):
        messages.error(request, "Você não tem permissão para acessar.")
        return redirect('/')
    
    ministerio = getattr(request.user, 'perfil_usuario', None)
    ministerio = ministerio.ministerio if ministerio else None
    
    # Sessões ativas
    sessoes = AuditSession.objects.filter(
        logout_data_hora__isnull=True,
        ministerio=ministerio if ministerio else None
    ).select_related('usuario', 'igreja_ativa')
    
    if not ministerio:
        sessoes = AuditSession.objects.filter(
            logout_data_hora__isnull=True
        ).select_related('usuario', 'igreja_ativa')
    
    context = {
        'sessoes': sessoes,
        'total_ativas': sessoes.count(),
        'ministerio': ministerio,
    }
    
    return render(request, 'auditoria/sessoes_ativas.html', context)

@login_required
def exportar_logs_csv(request):
    """
    Exporta logs de permissões para CSV.
    
    Permissão: ADMIN_MINISTERIO ou superior
    """
    if not user_has_permission_level_or_higher(request.user, 'ADMIN_MINISTERIO'):
        return JsonResponse({'error': 'Permissão negada'}, status=403)
    
    import csv
    from io import StringIO
    
    ministerio = getattr(request.user, 'perfil_usuario', None)
    ministerio = ministerio.ministerio if ministerio else None
    
    # Filtros
    tipo = request.GET.get('tipo', 'alteracoes')  # alteracoes, negados, sessoes
    dias = int(request.GET.get('dias', 30))
    data_inicio = timezone.now() - timedelta(days=dias)
    
    # Preparar CSV
    output = StringIO()
    
    if tipo == 'alteracoes':
        logs = PermissionChangeLog.objects.filter(
            data_hora__gte=data_inicio,
            ministerio=ministerio if ministerio else None
        ).select_related('usuario_afetado', 'grupo', 'usuario_executor')
        
        if not ministerio:
            logs = PermissionChangeLog.objects.filter(
                data_hora__gte=data_inicio
            ).select_related('usuario_afetado', 'grupo', 'usuario_executor')
        
        writer = csv.writer(output)
        writer.writerow([
            'Data/Hora', 'Usuario Afetado', 'Ação', 'Grupo', 
            'Executado Por', 'IP', 'Observação'
        ])
        
        for log in logs:
            writer.writerow([
                log.data_hora.strftime('%d/%m/%Y %H:%M:%S'),
                log.usuario_afetado.username if log.usuario_afetado else '',
                log.get_acao_display(),
                log.grupo.name if log.grupo else '',
                log.usuario_executor.username if log.usuario_executor else '',
                log.ip_address or '',
                log.observacao,
            ])
        
        filename = f'logs_alteracoes_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    elif tipo == 'negados':
        logs = AccessDeniedLog.objects.filter(
            data_hora__gte=data_inicio,
            ministerio=ministerio if ministerio else None
        ).select_related('usuario', 'igreja_tentada')
        
        if not ministerio:
            logs = AccessDeniedLog.objects.filter(
                data_hora__gte=data_inicio
            ).select_related('usuario', 'igreja_tentada')
        
        writer = csv.writer(output)
        writer.writerow([
            'Data/Hora', 'Usuario', 'Tipo Acesso', 'Recurso', 
            'Permissao Requerida', 'Igreja', 'IP', 'URL'
        ])
        
        for log in logs:
            writer.writerow([
                log.data_hora.strftime('%d/%m/%Y %H:%M:%S'),
                log.usuario.username,
                log.get_tipo_acesso_display(),
                log.recurso,
                log.permissao_requerida,
                log.igreja_tentada.nome_igreja if log.igreja_tentada else '',
                log.ip_address or '',
                log.url_path,
            ])
        
        filename = f'logs_acessos_negados_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    elif tipo == 'sessoes':
        logs = AuditSession.objects.filter(
            login_data_hora__gte=data_inicio,
            ministerio=ministerio if ministerio else None
        ).select_related('usuario', 'igreja_ativa')
        
        if not ministerio:
            logs = AuditSession.objects.filter(
                login_data_hora__gte=data_inicio
            ).select_related('usuario', 'igreja_ativa')
        
        writer = csv.writer(output)
        writer.writerow([
            'Login', 'Logout', 'Usuario', 'IP', 'Páginas Visitadas', 'Igreja'
        ])
        
        for log in logs:
            duracao = log.duracao if log.logout_data_hora else 'Ativa'
            logout_str = log.logout_data_hora.strftime('%d/%m/%Y %H:%M:%S') if log.logout_data_hora else 'Ativa'
            
            writer.writerow([
                log.login_data_hora.strftime('%d/%m/%Y %H:%M:%S'),
                logout_str,
                log.usuario.username,
                log.ip_address or '',
                log.paginas_visitadas,
                log.igreja_ativa.nome_igreja if log.igreja_ativa else '',
            ])
        
        filename = f'logs_sessoes_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    # Retornar CSV como download
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def analise_atividades_suspeitas(request):
    """
    Análise de atividades suspeitas:
    - Múltiplos acessos negados em curto período
    - Acesso de vários IPs simultâneos
    - Tentativas de acesso a recursos não autorizados
    
    Permissão: ADMIN_MINISTERIO ou superior
    """
    if not user_has_permission_level_or_higher(request.user, 'ADMIN_MINISTERIO'):
        messages.error(request, "Você não tem permissão para acessar.")
        return redirect('/')
    
    ministerio = getattr(request.user, 'perfil_usuario', None)
    ministerio = ministerio.ministerio if ministerio else None
    
    # Período analisado
    dias = int(request.GET.get('dias', 7))
    data_inicio = timezone.now() - timedelta(days=dias)
    
    # Análise 1: Usuários com múltiplos acessos negados
    acessos_negados_por_usuario = AccessDeniedLog.objects.filter(
        data_hora__gte=data_inicio,
        ministerio=ministerio if ministerio else None
    ).values(
        'usuario__username', 'usuario_id'
    ).annotate(
        total=Count('id')
    ).filter(total__gte=5).order_by('-total')
    
    if not ministerio:
        acessos_negados_por_usuario = AccessDeniedLog.objects.filter(
            data_hora__gte=data_inicio
        ).values(
            'usuario__username', 'usuario_id'
        ).annotate(
            total=Count('id')
        ).filter(total__gte=5).order_by('-total')
    
    # Análise 2: IPs suspeitos (múltiplos usuários de mesmo IP)
    ips_suspeitos = AccessDeniedLog.objects.filter(
        data_hora__gte=data_inicio,
        ip_address__isnull=False,
        ministerio=ministerio if ministerio else None
    ).values(
        'ip_address'
    ).annotate(
        total_usuarios=Count('usuario_id', distinct=True),
        total_acessos=Count('id')
    ).filter(total_usuarios__gte=2).order_by('-total_acessos')
    
    if not ministerio:
        ips_suspeitos = AccessDeniedLog.objects.filter(
            data_hora__gte=data_inicio,
            ip_address__isnull=False
        ).values(
            'ip_address'
        ).annotate(
            total_usuarios=Count('usuario_id', distinct=True),
            total_acessos=Count('id')
        ).filter(total_usuarios__gte=2).order_by('-total_acessos')
    
    # Análise 3: Recursos que mais geram acessos negados
    recursos_negados = AccessDeniedLog.objects.filter(
        data_hora__gte=data_inicio,
        ministerio=ministerio if ministerio else None
    ).values(
        'recurso'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    if not ministerio:
        recursos_negados = AccessDeniedLog.objects.filter(
            data_hora__gte=data_inicio
        ).values(
            'recurso'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:10]
    
    context = {
        'acessos_negados_por_usuario': acessos_negados_por_usuario[:20],
        'ips_suspeitos': list(ips_suspeitos)[:20],
        'recursos_negados': recursos_negados,
        'dias': dias,
        'ministerio': ministerio,
    }
    
    return render(request, 'auditoria/atividades_suspeitas.html', context)


@login_required
def acumulacao_permissoes(request):
    """
    Relatório de acumulação de permissões.
    Identifica usuários com muitos grupos/permissões e possíveis escalações.
    
    Permissão: ADMIN_MINISTERIO ou superior
    """
    if not user_has_permission_level_or_higher(request.user, 'ADMIN_MINISTERIO'):
        messages.error(request, "Você não tem permissão para acessar.")
        return redirect('/')
    
    ministerio = getattr(request.user, 'perfil_usuario', None)
    ministerio = ministerio.ministerio if ministerio else None
    
    # Usuários com muitos grupos
    usuarios_com_permissoes = []
    
    if ministerio and hasattr(ministerio, 'usuarios'):
        usuarios = ministerio.usuarios.all()
    else:
        usuarios = User.objects.filter(is_active=True)
    
    for usuario in usuarios:
        grupos = usuario.groups.all()
        num_grupos = grupos.count()
        
        if num_grupos > 0:
            usuarios_com_permissoes.append({
                'usuario': usuario,
                'num_grupos': num_grupos,
                'grupos': grupos,
                'nivel_risco': 'ALTO' if num_grupos >= 5 else 'MEDIO' if num_grupos >= 3 else 'BAIXO',
            })
    
    # Ordenar por número de grupos
    usuarios_com_permissoes.sort(key=lambda x: x['num_grupos'], reverse=True)
    
    # Estatísticas
    stats = {
        'total_usuarios': len(usuarios_com_permissoes),
        'usuarios_alto_risco': sum(1 for u in usuarios_com_permissoes if u['nivel_risco'] == 'ALTO'),
        'usuarios_medio_risco': sum(1 for u in usuarios_com_permissoes if u['nivel_risco'] == 'MEDIO'),
        'media_grupos': sum(u['num_grupos'] for u in usuarios_com_permissoes) / len(usuarios_com_permissoes) if usuarios_com_permissoes else 0,
    }
    
    context = {
        'usuarios_com_permissoes': usuarios_com_permissoes[:50],
        'stats': stats,
        'ministerio': ministerio,
    }
    
    return render(request, 'auditoria/acumulacao_permissoes.html', context)
