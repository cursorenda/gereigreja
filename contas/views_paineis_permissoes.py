"""Views dos paineis hierarquicos de permissoes."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from contas.constants import ADMIN_MINISTERIO, HIERARQUIA_GRUPOS, PASTOR_LOCAL, PASTOR_REGIONAL, user_has_permission_level_or_higher
from contas.forms_hierarquia import EditarGruposUsuarioForm, VinculoHierarquicoForm
from contas.models import HierarquiaPermissoes
from core.group_sync import recalcular_grupos_efetivos_usuario


@login_required
def painel_permissoes_global(request):
    """Painel global para administracao de permissoes do ministerio."""
    if not user_has_permission_level_or_higher(request.user, ADMIN_MINISTERIO):
        messages.error(request, 'Voce nao tem permissao para acessar este painel.')
        return redirect('secretaria:dashboard')

    ministerio = _get_ministerio(request.user)
    usuarios = _usuarios_base_ministerio(ministerio)

    nome_filter = request.GET.get('nome', '').strip()
    grupo_filter = request.GET.get('grupo', '').strip()

    if nome_filter:
        usuarios = usuarios.filter(
            Q(first_name__icontains=nome_filter)
            | Q(last_name__icontains=nome_filter)
            | Q(username__icontains=nome_filter)
        )

    if grupo_filter:
        usuarios = usuarios.filter(groups__name__icontains=grupo_filter).distinct()

    context = {
        'usuarios': usuarios,
        'todos_grupos': Group.objects.all().order_by('name'),
        'ministerio': ministerio,
        'painel_tipo': 'global',
        'nome_filter': nome_filter,
        'grupo_filter': grupo_filter,
        'titulo_pagina': 'Painel Global de Permissoes',
        'descricao': 'Gerenciar permissoes de todos os usuarios do ministerio',
        'visibilidade_info': 'Todos os usuarios ativos do ministerio',
        'permissoes_editaveis_info': 'Todos os grupos de permissao',
    }
    return render(request, 'contas/painel_permissoes.html', context)


@login_required
def painel_permissoes_regional(request):
    """Painel regional com escopo das igrejas permitidas e vinculos hierarquicos."""
    if not user_has_permission_level_or_higher(request.user, PASTOR_REGIONAL):
        messages.error(request, 'Voce nao tem permissao para acessar este painel.')
        return redirect('secretaria:dashboard')

    ministerio = _get_ministerio(request.user)
    usuarios = _usuarios_visiveis_regional(request.user)

    nome_filter = request.GET.get('nome', '').strip()
    igreja_filter = request.GET.get('igreja', '').strip()

    if nome_filter:
        usuarios = usuarios.filter(
            Q(first_name__icontains=nome_filter)
            | Q(last_name__icontains=nome_filter)
            | Q(username__icontains=nome_filter)
        )

    if igreja_filter:
        usuarios = usuarios.filter(perfil__igrejas_permitidas__nome_igreja__icontains=igreja_filter).distinct()

    context = {
        'usuarios': usuarios,
        'todos_grupos': Group.objects.exclude(name=ADMIN_MINISTERIO).order_by('name'),
        'igrejas': _igrejas_visiveis_regional(request.user),
        'ministerio': ministerio,
        'painel_tipo': 'regional',
        'nome_filter': nome_filter,
        'igreja_filter': igreja_filter,
        'titulo_pagina': 'Painel Regional de Permissoes',
        'descricao': 'Gerenciar permissoes da sua regiao',
        'visibilidade_info': 'Pastores locais e equipes das igrejas da sua regiao',
        'permissoes_editaveis_info': 'Todos os grupos, exceto Admin Ministerio',
    }
    return render(request, 'contas/painel_permissoes.html', context)


@login_required
def painel_permissoes_local(request):
    """Painel local para gerenciar usuarios da igreja local."""
    if not user_has_permission_level_or_higher(request.user, PASTOR_LOCAL):
        messages.error(request, 'Voce nao tem permissao para acessar este painel.')
        return redirect('secretaria:dashboard')

    perfil = getattr(request.user, 'perfil', None)
    if not perfil or not perfil.igrejas_permitidas.exists():
        messages.warning(request, 'Voce nao possui uma igreja atribuida.')
        return redirect('secretaria:dashboard')

    igreja_local = perfil.igrejas_permitidas.first()
    usuarios = (
        User.objects.filter(perfil__igrejas_permitidas=igreja_local, is_active=True)
        .exclude(id=request.user.id)
        .distinct()
        .select_related('perfil')
        .prefetch_related('groups')
        .order_by('first_name', 'last_name', 'username')
    )

    nome_filter = request.GET.get('nome', '').strip()
    if nome_filter:
        usuarios = usuarios.filter(
            Q(first_name__icontains=nome_filter)
            | Q(last_name__icontains=nome_filter)
            | Q(username__icontains=nome_filter)
        )

    context = {
        'usuarios': usuarios,
        'todos_grupos': Group.objects.all().order_by('name'),
        'igreja': igreja_local,
        'painel_tipo': 'local',
        'nome_filter': nome_filter,
        'titulo_pagina': f'Painel Local de Permissoes - {igreja_local.nome_igreja}',
        'descricao': 'Gerenciar permissoes de sua equipe local',
        'visibilidade_info': f'Sua equipe na Igreja {igreja_local.nome_igreja}',
        'permissoes_editaveis_info': 'Todos os grupos, restritos aos usuarios da sua igreja local',
    }
    return render(request, 'contas/painel_permissoes.html', context)


@login_required
def editar_permissoes_usuario(request, user_id):
    """Edita grupos de um usuario respeitando nivel e escopo hierarquico."""
    usuario_alvo = get_object_or_404(User.objects.select_related('perfil'), pk=user_id)
    usuario_superior = request.user

    if not _pode_gerenciar_usuario(usuario_superior, usuario_alvo):
        messages.error(request, 'Voce nao tem permissao para alterar este usuario.')
        return redirect('secretaria:dashboard')

    grupos_alteraveis = _grupos_alteraveis_por_usuario(usuario_superior)

    if request.method == 'POST':
        form = EditarGruposUsuarioForm(
            request.POST,
            allowed_groups=grupos_alteraveis,
            current_groups=usuario_alvo.groups.all(),
        )
        if form.is_valid():
            grupos = form.cleaned_data['grupos']
            grupos = grupos_alteraveis.filter(id__in=grupos.values_list('id', flat=True))

            grupos_antigos = list(usuario_alvo.groups.all().values_list('name', flat=True))
            recalcular_grupos_efetivos_usuario(
                usuario_alvo,
                grupos_manuais=grupos,
                grupos_editaveis=grupos_alteraveis,
            )
            grupos_novos = list(usuario_alvo.groups.all().values_list('name', flat=True))

            from auditoria.models import PermissionChangeLog

            PermissionChangeLog.objects.create(
                usuario_afetado=usuario_alvo,
                usuario_executor=usuario_superior,
                acao='EDIT',
                ministerio=_get_ministerio(usuario_superior),
                observacao=(
                    'Permissoes alteradas via painel hierarquico. '
                    f"De: {', '.join(grupos_antigos) or 'nenhum'}. "
                    f"Para: {', '.join(grupos_novos) or 'nenhum'}"
                ),
            )
            messages.success(request, f'Permissoes de {usuario_alvo.get_full_name() or usuario_alvo.username} atualizadas com sucesso.')
            return redirect(_rota_painel_padrao(usuario_superior))
    else:
        form = EditarGruposUsuarioForm(
            allowed_groups=grupos_alteraveis,
            current_groups=usuario_alvo.groups.all(),
        )

    from auditoria.models import PermissionChangeLog

    ultimas_mudancas = (
        PermissionChangeLog.objects.filter(usuario_afetado=usuario_alvo)
        .select_related('grupo', 'usuario_executor')
        .order_by('-data_hora')[:5]
    )

    hierarquia_info = None
    vinculo = HierarquiaPermissoes.objects.filter(
        usuario_superior=usuario_superior,
        usuario_subordinado=usuario_alvo,
        ativo=True,
    ).first()
    if vinculo:
        nivel_nome = dict(HierarquiaPermissoes._meta.get_field('nivel_superior').choices).get(vinculo.nivel_superior, 'Desconhecido')
        perfil_alvo = getattr(usuario_alvo, 'perfil', None)
        igreja_nome = perfil_alvo.igrejas_permitidas.first().nome_igreja if perfil_alvo and perfil_alvo.igrejas_permitidas.exists() else None
        hierarquia_info = f'Usuario subordinado no nivel {nivel_nome}'
        if igreja_nome:
            hierarquia_info = f'{hierarquia_info} na Igreja {igreja_nome}.'

    context = {
        'usuario_alvo': usuario_alvo,
        'form': form,
        'ultimas_mudancas': ultimas_mudancas,
        'hierarquia_info': hierarquia_info,
        'nao_pode_editar': False,
    }
    return render(request, 'contas/editar_permissoes_usuario.html', context)


@login_required
def gestao_vinculos_hierarquicos(request):
    """Lista e cria vinculos hierarquicos de forma intuitiva."""
    if not user_has_permission_level_or_higher(request.user, PASTOR_LOCAL):
        messages.error(request, 'Voce nao tem permissao para acessar a gestao de vinculos.')
        return redirect('secretaria:dashboard')

    ministerio = _get_ministerio(request.user)

    if user_has_permission_level_or_higher(request.user, ADMIN_MINISTERIO):
        vinculos = HierarquiaPermissoes.objects.filter(usuario_superior__perfil__ministerio=ministerio)
    else:
        vinculos = HierarquiaPermissoes.objects.filter(usuario_superior=request.user)

    vinculos = vinculos.select_related('usuario_superior', 'usuario_subordinado', 'igreja').order_by('-data_vinculo')

    somente_ativos = request.GET.get('ativos', '1') == '1'
    if somente_ativos:
        vinculos = vinculos.filter(ativo=True)

    if request.method == 'POST':
        form = VinculoHierarquicoForm(request.POST, usuario_superior=request.user, ministerio=ministerio)
        if form.is_valid():
            novo_vinculo = form.save(commit=False)
            novo_vinculo.usuario_superior = request.user
            if not _pode_gerenciar_usuario(request.user, novo_vinculo.usuario_subordinado):
                messages.error(request, 'Nao e permitido vincular este usuario ao seu escopo hierarquico.')
            else:
                novo_vinculo.save()
                messages.success(request, 'Vinculo hierarquico criado com sucesso.')
                return redirect('contas:gestao_vinculos_hierarquicos')
    else:
        form = VinculoHierarquicoForm(usuario_superior=request.user, ministerio=ministerio)

    return render(
        request,
        'contas/gestao_vinculos_hierarquicos.html',
        {'vinculos': vinculos, 'form': form, 'somente_ativos': somente_ativos},
    )


@login_required
def editar_vinculo_hierarquico(request, vinculo_id):
    """Edita um vinculo hierarquico existente."""
    vinculo = get_object_or_404(HierarquiaPermissoes, pk=vinculo_id)
    if not _pode_gerenciar_vinculo(request.user, vinculo):
        messages.error(request, 'Voce nao tem permissao para editar este vinculo.')
        return redirect('secretaria:dashboard')

    ministerio = _get_ministerio(request.user)
    if request.method == 'POST':
        form = VinculoHierarquicoForm(request.POST, instance=vinculo, usuario_superior=request.user, ministerio=ministerio)
        if form.is_valid():
            vinculo_editado = form.save(commit=False)
            if not user_has_permission_level_or_higher(request.user, ADMIN_MINISTERIO):
                vinculo_editado.usuario_superior = request.user
            if not _pode_gerenciar_usuario(request.user, vinculo_editado.usuario_subordinado):
                messages.error(request, 'Usuario subordinado fora do escopo permitido.')
            else:
                vinculo_editado.save()
                messages.success(request, 'Vinculo atualizado com sucesso.')
                return redirect('contas:gestao_vinculos_hierarquicos')
    else:
        form = VinculoHierarquicoForm(instance=vinculo, usuario_superior=request.user, ministerio=ministerio)

    return render(request, 'contas/editar_vinculo_hierarquico.html', {'form': form, 'vinculo': vinculo})


@login_required
def inativar_vinculo_hierarquico(request, vinculo_id):
    """Inativa um vinculo de hierarquia sem apagar historico."""
    vinculo = get_object_or_404(HierarquiaPermissoes, pk=vinculo_id)
    if not _pode_gerenciar_vinculo(request.user, vinculo):
        messages.error(request, 'Voce nao tem permissao para inativar este vinculo.')
        return redirect('secretaria:dashboard')

    if request.method == 'POST':
        vinculo.ativo = False
        vinculo.save(update_fields=['ativo'])
        messages.success(request, 'Vinculo inativado com sucesso.')

    return redirect('contas:gestao_vinculos_hierarquicos')


def _get_ministerio(user):
    perfil = getattr(user, 'perfil', None)
    return getattr(perfil, 'ministerio', None)


def _usuarios_base_ministerio(ministerio):
    if ministerio is None:
        return User.objects.none()
    return (
        User.objects.filter(perfil__ministerio=ministerio, is_active=True)
        .select_related('perfil')
        .prefetch_related('groups')
        .order_by('first_name', 'last_name', 'username')
    )


def _igrejas_visiveis_regional(user):
    perfil = getattr(user, 'perfil', None)
    if perfil is None:
        return []

    # Regra: Painel regional usa a propria subsede (igreja regional principal)
    # e todas as igrejas descendentes dessa arvore.
    igreja_regional_principal = perfil.igrejas_permitidas.filter(tipo_igreja='regional').first()
    if igreja_regional_principal is None:
        igreja_regional_principal = perfil.igrejas_permitidas.first()

    if igreja_regional_principal is None:
        return []

    igrejas_base = [igreja_regional_principal]
    ids = {i.pk for i in igrejas_base}
    for igreja in igrejas_base:
        for filha in igreja.get_descendants():
            ids.add(filha.pk)

    if not ids:
        return []
    return list(perfil.igrejas_permitidas.model.objects.filter(pk__in=ids))


def _usuarios_visiveis_regional(user):
    base = _usuarios_base_ministerio(_get_ministerio(user))
    subordinados = HierarquiaPermissoes.objects.filter(
        usuario_superior=user,
        nivel_superior=PASTOR_REGIONAL,
        ativo=True,
    ).values_list('usuario_subordinado_id', flat=True)

    igrejas_regiao = _igrejas_visiveis_regional(user)
    if not igrejas_regiao:
        return base.filter(id__in=subordinados).exclude(id=user.id).distinct()

    return (
        base.filter(Q(id__in=subordinados) | Q(perfil__igrejas_permitidas__in=igrejas_regiao))
        .exclude(id=user.id)
        .distinct()
    )


def _usuario_mesmo_ministerio(manager, target_user):
    return _get_ministerio(manager) is not None and _get_ministerio(manager) == _get_ministerio(target_user)


def _pode_gerenciar_usuario(manager, target_user):
    if manager == target_user:
        return False
    if not _usuario_mesmo_ministerio(manager, target_user):
        return False

    if user_has_permission_level_or_higher(manager, ADMIN_MINISTERIO):
        return True

    if user_has_permission_level_or_higher(manager, PASTOR_REGIONAL):
        return _usuarios_visiveis_regional(manager).filter(pk=target_user.pk).exists() or HierarquiaPermissoes.objects.filter(
            usuario_superior=manager,
            usuario_subordinado=target_user,
            ativo=True,
        ).exists()

    if user_has_permission_level_or_higher(manager, PASTOR_LOCAL):
        perfil = getattr(manager, 'perfil', None)
        if perfil and perfil.igrejas_permitidas.exists():
            igreja_local = perfil.igrejas_permitidas.first()
            return User.objects.filter(pk=target_user.pk, perfil__igrejas_permitidas=igreja_local, is_active=True).exists()

    return False


def _grupos_alteraveis_por_usuario(user):
    if user_has_permission_level_or_higher(user, ADMIN_MINISTERIO):
        return Group.objects.all().order_by('name')
    if user_has_permission_level_or_higher(user, PASTOR_REGIONAL):
        return _grupos_ate_nivel(PASTOR_LOCAL)
    if user_has_permission_level_or_higher(user, PASTOR_LOCAL):
        # Regra solicitada: pastor local pode atribuir todos os grupos na propria igreja.
        return Group.objects.all().order_by('name')
    return Group.objects.none()


def _grupos_ate_nivel(grupo_maximo):
    """Retorna grupos do nivel especificado para baixo na hierarquia."""
    max_level = HIERARQUIA_GRUPOS.get(grupo_maximo)
    if max_level is None:
        return Group.objects.none()

    grupos_permitidos = [nome for nome, nivel in HIERARQUIA_GRUPOS.items() if nivel >= max_level]
    return Group.objects.filter(name__in=grupos_permitidos).order_by('name')


def _rota_painel_padrao(user):
    if user_has_permission_level_or_higher(user, ADMIN_MINISTERIO):
        return 'contas:painel_permissoes_global'
    if user_has_permission_level_or_higher(user, PASTOR_REGIONAL):
        return 'contas:painel_permissoes_regional'
    return 'contas:painel_permissoes_local'


def _pode_gerenciar_vinculo(user, vinculo):
    if user_has_permission_level_or_higher(user, ADMIN_MINISTERIO):
        return _usuario_mesmo_ministerio(user, vinculo.usuario_superior)
    return vinculo.usuario_superior_id == user.id
