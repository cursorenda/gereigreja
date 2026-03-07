# configuracao/views_permissions.py
"""
Views para auditoria de grupos e permissões.
Apenas Admin Ministerio e Pastor Local podem acessar.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission, User
from django.db.models import Count, Q
from core.decorators import admin_ministerio_required
from contas.constants import (
    GRUPOS_ADMIN,
    GRUPOS_LIDERANCA_MINISTERIAL,
    GRUPOS_LIDERANCA_REGIONAL,
    GRUPOS_LIDERANCA_LOCAL,
    GRUPOS_OPERACIONAL,
    GRUPOS_EQUIPES,
    GRUPOS_TODOS,
)
from datetime import datetime


@login_required
@admin_ministerio_required
def auditoria_permissoes(request):
    """
    Dashboard de auditoria de grupos e permissões.
    
    Mostra:
    - Hierarquia de grupos
    - Permissions de cada grupo
    - Usuários em cada grupo (filtrado por ministério)
    - Problemas detectados
    - Compatibilidade com decorators
    """
    
    # Pegar ministério do usuário logado
    ministerio = None
    if hasattr(request.user, 'perfil') and request.user.perfil:
        ministerio = request.user.perfil.ministerio
    
    # Busca/filtro
    busca = request.GET.get('q', '')
    filtro_grupo = request.GET.get('grupo', '')
    
    # Grupos organizados por hierarquia
    hierarquia = {
        'NÍVEL 1: ADMINISTRATIVO': {
            'grupos_nomes': GRUPOS_ADMIN,
            'descricao': 'Administração geral do ministério',
            'cor': 'danger',
        },
        'NÍVEL 2: LIDERANÇA MINISTERIAL': {
            'grupos_nomes': [g for g in GRUPOS_LIDERANCA_MINISTERIAL if g not in GRUPOS_ADMIN],
            'descricao': 'Visão consolidada de todas as igrejas',
            'cor': 'warning',
        },
        'NÍVEL 3: LIDERANÇA REGIONAL': {
            'grupos_nomes': [g for g in GRUPOS_LIDERANCA_REGIONAL if g not in GRUPOS_LIDERANCA_MINISTERIAL],
            'descricao': 'Supervisiona várias congregações',
            'cor': 'info',
        },
        'NÍVEL 4: OPERACIONAL LOCAL': {
            'grupos_nomes': [g for g in GRUPOS_OPERACIONAL if g not in GRUPOS_LIDERANCA_LOCAL],
            'descricao': 'Equipe administrativa de uma igreja',
            'cor': 'primary',
        },
        'NÍVEL 5: EQUIPES E AUXILIARES': {
            'grupos_nomes': GRUPOS_EQUIPES,
            'descricao': 'Funções específicas e auxiliares',
            'cor': 'secondary',
        },
    }
    
    # Enriquecer dados de cada grupo
    grupos_data = []
    problemas_globais = []
    total_permissions = Permission.objects.exclude(
        content_type__app_label__in=['admin', 'contenttypes', 'sessions']
    ).count()
    
    for nivel, info in hierarquia.items():
        grupos_nivel = []
        
        for grupo_nome in info['grupos_nomes']:
            try:
                grupo = Group.objects.get(name=grupo_nome)
            except Group.DoesNotExist:
                problemas_globais.append({
                    'tipo': 'erro',
                    'mensagem': f"Grupo '{grupo_nome}' definido em constants.py mas não existe no banco!",
                    'grupo': grupo_nome,
                    'nivel': nivel,
                })
                continue
            
            # Dados do grupo - filtrar usuários do ministério atual
            usuarios_query = User.objects.filter(groups=grupo).select_related('perfil')
            
            # Filtrar por ministério se disponível
            if ministerio:
                usuarios_query = usuarios_query.filter(perfil__ministerio=ministerio)
            
            usuarios = usuarios_query
            usuarios_count = usuarios.count()
            permissions = grupo.permissions.all()
            permissions_count = permissions.count()
            
            # Verificar problemas
            problemas_grupo = []
            
            # Problema 1: Grupo operacional sem permissions
            if grupo_nome in GRUPOS_OPERACIONAL and permissions_count == 0:
                problemas_grupo.append({
                    'tipo': 'warning',
                    'mensagem': 'Grupo operacional sem nenhuma permission!',
                })
            
            # Problema 2: Equipe com permissions perigosas
            if grupo_nome in GRUPOS_EQUIPES:
                perms_delete = permissions.filter(codename__startswith='delete_')
                if perms_delete.exists():
                    problemas_grupo.append({
                        'tipo': 'danger',
                        'mensagem': f'Grupo de equipe com permissions DELETE: {", ".join(perms_delete.values_list("codename", flat=True))}',
                    })
            
            # Permissions por app
            permissions_por_app = {}
            for perm in permissions:
                app = perm.content_type.app_label
                if app not in permissions_por_app:
                    permissions_por_app[app] = []
                permissions_por_app[app].append({
                    'codename': perm.codename,
                    'name': perm.name,
                    'perigosa': perm.codename.startswith('delete_'),
                })
            
            # Decorators que usam este grupo
            decorators_relacionados = []
            if grupo_nome in GRUPOS_OPERACIONAL:
                decorators_relacionados.append('@secretaria_dashboard_required')
            # Adicionar outros decorators conforme necessário
            
            grupos_nivel.append({
                'nome': grupo_nome,
                'grupo_obj': grupo,
                'usuarios': list(usuarios[:10]),  # Limitar a 10 para performance
                'usuarios_count': usuarios_count,
                'permissions_count': permissions_count,
                'permissions_percentual': round((permissions_count / total_permissions) * 100, 1) if total_permissions > 0 else 0,
                'permissions_por_app': dict(sorted(permissions_por_app.items())),
                'problemas': problemas_grupo,
                'decorators': decorators_relacionados,
                'status': 'danger' if problemas_grupo else 'success',
            })
        
        if grupos_nivel:  # Só adicionar se tiver grupos
            grupos_data.append({
                'nivel': nivel,
                'descricao': info['descricao'],
                'cor': info['cor'],
                'grupos': grupos_nivel,
            })
    
    # Estatísticas gerais - filtradas por ministério
    usuarios_queryset = User.objects.filter(is_active=True)
    if ministerio:
        usuarios_queryset = usuarios_queryset.filter(perfil__ministerio=ministerio)
    
    stats = {
        'total_grupos': Group.objects.count(),
        'total_usuarios': usuarios_queryset.count(),
        'grupos_sem_permissions': Group.objects.annotate(
            perm_count=Count('permissions')
        ).filter(perm_count=0).count(),
        'total_permissions': total_permissions,
        'ultima_sincronizacao': None,  # TODO: salvar em cache quando rodar sync
        'ministerio': ministerio.nome_fantasia if ministerio else 'Todos',
    }
    
    context = {
        'hierarquia': grupos_data,
        'stats': stats,
        'problemas_globais': problemas_globais,
        'busca': busca,
        'filtro_grupo': filtro_grupo,
        'total_problemas': len(problemas_globais) + sum(
            len(g['problemas']) 
            for nivel in grupos_data 
            for g in nivel['grupos']
        ),
    }
    
    return render(request, 'configuracao/auditoria_permissoes.html', context)


@login_required
@admin_ministerio_required
def comparar_usuario_grupo(request, user_id, group_id):
    """
    Compara um usuário específico com as permissions esperadas do grupo.
    Útil para troubleshooting.
    """
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse
    
    user = get_object_or_404(User, id=user_id)
    group = get_object_or_404(Group, id=group_id)
    
    # Permissions do usuário (via grupos)
    user_perms = set(Permission.objects.filter(group__user=user).values_list('id', flat=True))
    
    # Permissions do grupo
    group_perms = set(group.permissions.values_list('id', flat=True))
    
    # Comparação
    tem_todas = group_perms.issubset(user_perms)
    faltando = group_perms - user_perms
    extras = user_perms - group_perms
    
    return JsonResponse({
        'usuario': user.get_full_name() or user.username,
        'grupo': group.name,
        'tem_todas_permissions': tem_todas,
        'faltando': list(Permission.objects.filter(id__in=faltando).values('codename', 'name')),
        'extras': list(Permission.objects.filter(id__in=extras).values('codename', 'name')),
    })


@login_required
@admin_ministerio_required
def exportar_relatorio_permissions(request):
    """Exporta relatório CSV de todos os grupos e permissions (filtrado por ministério)."""
    import csv
    from django.http import HttpResponse
    
    # Pegar ministério do usuário logado
    ministerio = None
    if hasattr(request.user, 'perfil') and request.user.perfil:
        ministerio = request.user.perfil.ministerio
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="permissions_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Nível', 'Grupo', 'Usuários', 'Total Permissions', 'App', 'Permission', 'É Delete?'])
    
    for grupo in Group.objects.all().prefetch_related('permissions', 'user_set'):
        nivel = _determinar_nivel(grupo.name)
        
        # Filtrar usuários por ministério
        usuarios_query = grupo.user_set.filter(is_active=True)
        if ministerio:
            usuarios_query = usuarios_query.filter(perfil__ministerio=ministerio)
        usuarios_count = usuarios_query.count()
        
        permissions = grupo.permissions.all()
        if permissions:
            for perm in permissions:
                writer.writerow([
                    nivel,
                    grupo.name,
                    usuarios_count,
                    permissions.count(),
                    perm.content_type.app_label,
                    perm.codename,
                    'SIM' if perm.codename.startswith('delete_') else 'NÃO',
                ])
        else:
            writer.writerow([
                nivel,
                grupo.name,
                usuarios_count,
                0,
                '-',
                '-',
                '-',
            ])
    
    return response


def _determinar_nivel(grupo_nome):
    """Helper para determinar nível hierárquico do grupo."""
    if grupo_nome in GRUPOS_ADMIN:
        return 'Nível 1'
    elif grupo_nome in GRUPOS_LIDERANCA_MINISTERIAL:
        return 'Nível 2'
    elif grupo_nome in GRUPOS_LIDERANCA_REGIONAL:
        return 'Nível 3'
    elif grupo_nome in GRUPOS_OPERACIONAL:
        return 'Nível 4'
    elif grupo_nome in GRUPOS_EQUIPES:
        return 'Nível 5'
    else:
        return 'Desconhecido'
