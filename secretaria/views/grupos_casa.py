"""
secretaria/views/grupos_casa.py
Views para grupos/casas: listagem, detalhe, criação, edição, agrupamento automático.
"""
import logging
import re

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from core.decorators import page_access_required
from core.utils import get_ministerio_or_error
from secretaria.forms_grupocasa import GrupoCasaForm, VisitaGrupoCasaForm
from secretaria.models import AcompanhamentoVisita, GrupoCasa, Membro
from secretaria.utils import (
    agrupar_apply_from_preview,
    agrupar_preview_for_queryset,
    filter_people_by_name_or_nickname,
    get_allowed_churches_for_membros,
    has_membro_edit_permission,
    is_admin_org,
)

from secretaria.views._helpers import is_admin_or_pastor, is_admin_or_pastor_local, get_request_scoped_churches

logger = logging.getLogger(__name__)


def _normalize_people_ids(raw_values):
    """Normaliza IDs vindos do POST aceitando separadores de locale (ex.: 1.120)."""
    ids = []
    for raw in raw_values:
        text = str(raw or '').strip()
        if not text:
            continue
        if not re.fullmatch(r'[0-9\.,\s-]+', text):
            continue
        digits = re.sub(r'\D', '', text)
        if digits:
            ids.append(digits)
    return list(dict.fromkeys(ids))


def _serialize_selected_people(people_qs):
    data = []
    for p in people_qs:
        tipo_nome = p.tipo_pessoa.nome if getattr(p, 'tipo_pessoa', None) else ''
        igreja_nome = p.igreja.nome_igreja if getattr(p, 'igreja', None) else ''
        extra = ' - '.join([x for x in [tipo_nome, igreja_nome] if x])
        data.append({
            'id': str(p.pk),
            'nome': p.nome,
            'extra': extra,
        })
    return data


@login_required
@page_access_required('secretaria_grupos_casa')
@require_GET
def buscar_pessoas_grupo_casa(request):
    """Busca paginada de pessoas para vincular em Grupo/Casa, respeitando escopo do usuário."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    scoped_churches = get_request_scoped_churches(request, allowed_churches)

    grupo_id = request.GET.get('grupo_id')
    status_permitidos = ['Ativo', 'Desligado', 'Em Disciplina']

    if grupo_id:
        grupo = get_object_or_404(GrupoCasa, pk=grupo_id)
        try:
            if not (request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists()) and allowed_churches.exists():
                if not allowed_churches.filter(pk=grupo.igreja_id).exists() and not is_admin_org(request.user):
                    raise PermissionDenied('Sem permissão para buscar pessoas deste grupo')
        except PermissionDenied:
            raise Http404()

        base_qs = Membro.objects.filter(
            igreja_id=grupo.igreja_id,
            status_pessoa__nome__in=status_permitidos,
        )
    else:
        base_qs = Membro.objects.filter(
            igreja__in=scoped_churches,
            status_pessoa__nome__in=status_permitidos,
        )

    termo = (request.GET.get('q') or '').strip()
    if termo:
        base_qs = filter_people_by_name_or_nickname(base_qs, termo)

    try:
        page = max(int(request.GET.get('page', 1)), 1)
    except (TypeError, ValueError):
        page = 1

    page_size = 25
    start = (page - 1) * page_size
    end = start + page_size

    selected_ids = set(_normalize_people_ids(request.GET.getlist('selected_ids')))

    total = base_qs.count()
    rows = list(
        base_qs
        .select_related('tipo_pessoa', 'igreja')
        .order_by('nome')[start:end]
    )

    results = []
    for p in rows:
        tipo_nome = p.tipo_pessoa.nome if getattr(p, 'tipo_pessoa', None) else ''
        igreja_nome = p.igreja.nome_igreja if getattr(p, 'igreja', None) else ''
        extra = ' - '.join([x for x in [tipo_nome, igreja_nome] if x])
        results.append({
            'id': str(p.pk),
            'nome': p.nome,
            'extra': extra,
            'checked': str(p.pk) in selected_ids,
        })

    return JsonResponse({
        'results': results,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': total,
            'has_prev': page > 1,
            'has_next': end < total,
        },
    })


@login_required
@staff_member_required
def limpar_grupos_casa_vazios(request):
    """Remove todos os grupos/casas sem moradores (pessoas). Protegido para admins/staff."""
    qs = GrupoCasa.objects.annotate(num_pessoas=Count('pessoas'), num_visitas=Count('visitas'))
    empty_qs = qs.filter(num_pessoas=0)
    total = empty_qs.count()
    deleted = 0
    skipped = 0
    for g in empty_qs:
        if g.visitas.exists():
            skipped += 1
            continue
        g.delete()
        deleted += 1
    if deleted:
        messages.success(request, f"{deleted} grupo(s)/casa(s) vazios removidos com sucesso.")
    if skipped:
        messages.warning(request, f"{skipped} grupo(s)/casa(s) não removidos pois possuem visitas associadas.")
    if not deleted and not skipped:
        messages.info(request, "Nenhum grupo/casa vazio encontrado para remover.")
    return redirect('secretaria:lista_grupos_casa')


@login_required
@page_access_required('secretaria_grupos_casa')
def lista_grupos_casa(request):
    """Lista de GrupoCasa (casas/famílias) com escopo por igreja/ministerio."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)

    if request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
        qs = GrupoCasa.objects.filter(igreja=request.igreja_ativa)
    elif allowed_churches.exists():
        qs = GrupoCasa.objects.filter(igreja__in=allowed_churches)
    elif is_admin_org(request.user):
        qs = GrupoCasa.objects.filter(igreja__ministerio=ministerio)
    else:
        qs = GrupoCasa.objects.none()

    q = request.GET.get('q')
    if q:
        qs = qs.filter(Q(rua__icontains=q) | Q(nome__icontains=q) | Q(bairro__icontains=q) | Q(cep__icontains=q))

    qs = qs.order_by('rua', 'numero')
    can_agrupar = is_admin_or_pastor(request.user) or is_admin_or_pastor_local(request.user)
    try:
        can_edit_grupo = is_admin_or_pastor(request.user) or has_membro_edit_permission(request.user)
    except Exception:
        can_edit_grupo = is_admin_or_pastor(request.user)

    status_permitidos = ['Ativo', 'Desligado', 'Em Disciplina']
    grupos = list(qs.select_related('igreja', 'responsavel').prefetch_related('pessoas__status_pessoa'))
    for g in grupos:
        g.membros_permitidos = g.pessoas.filter(status_pessoa__nome__in=status_permitidos)

    context = {
        'grupos': grupos,
        'titulo_pagina': 'Grupos / Casas',
        'query': q,
        'ministerio': ministerio,
        'igreja_selecionada': str(request.igreja_ativa.pk) if hasattr(request, 'igreja_ativa') and request.igreja_ativa else (request.GET.get('igreja') or ''),
        'can_agrupar_grupos': can_agrupar,
        'can_edit_grupo': can_edit_grupo,
    }
    return render(request, 'secretaria/grupocasa_list.html', context)


@login_required
@page_access_required('secretaria_grupos_casa')
def agrupar_grupos_preview(request):
    """Preview das mudanças que o agrupamento faria por endereço."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)

    if request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
        people_qs = Membro.objects.filter(igreja=request.igreja_ativa)
    elif allowed_churches.exists():
        people_qs = Membro.objects.filter(igreja__in=allowed_churches)
    elif is_admin_org(request.user):
        people_qs = Membro.objects.filter(igreja__ministerio=ministerio)
    else:
        people_qs = Membro.objects.none()

    status_permitidos = ['Ativo', 'Desligado', 'Em Disciplina']
    people_qs = people_qs.filter(status_pessoa__nome__in=status_permitidos)
    people_qs = people_qs.filter(Q(rua__isnull=False) | Q(cep__isnull=False)).order_by('rua', 'numero_casa')

    rows = agrupar_preview_for_queryset(people_qs)
    to_apply = [r for r in rows if r.get('count', 0) >= 2]

    context = {
        'rows': rows,
        'to_apply_count': len(to_apply),
        'titulo_pagina': 'Preview: Agrupar Grupos / Casas por Endereço',
    }
    return render(request, 'secretaria/agrupar_grupos_preview.html', context)


@login_required
@page_access_required('secretaria_grupos_casa')
def agrupar_grupos_apply(request):
    """Aplica o agrupamento (cria GrupoCasa e associa pessoas)."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)

    if request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
        people_qs = Membro.objects.filter(igreja=request.igreja_ativa)
    elif allowed_churches.exists():
        people_qs = Membro.objects.filter(igreja__in=allowed_churches)
    elif is_admin_org(request.user):
        people_qs = Membro.objects.filter(igreja__ministerio=ministerio)
    else:
        people_qs = Membro.objects.none()

    people_qs = people_qs.filter(Q(rua__isnull=False) | Q(cep__isnull=False)).order_by('rua', 'numero_casa')
    rows = agrupar_preview_for_queryset(people_qs)
    to_apply = [r for r in rows if r.get('count', 0) >= 2]

    result = {'created': 0, 'updated': 0}
    if to_apply:
        result = agrupar_apply_from_preview(to_apply)
        messages.success(request, f"Agrupamento aplicado: {result.get('created', 0)} grupos criados, {result.get('updated', 0)} pessoas atualizadas.")
    else:
        messages.info(request, 'Nenhum agrupamento com 2+ pessoas detectado; nada foi aplicado.')

    return redirect('secretaria:lista_grupos_casa')


@login_required
@page_access_required('secretaria_grupos_casa')
def reagrupar_grupo_casa(request, grupo_id):
    """Reagrupar moradores do GrupoCasa por endereço."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    grupo = get_object_or_404(GrupoCasa, pk=grupo_id)

    try:
        if not (request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists()) and allowed_churches.exists():
            if not allowed_churches.filter(pk=grupo.igreja_id).exists() and not is_admin_org(request.user):
                raise PermissionDenied('Sem permissão para reagrupar este grupo')
    except PermissionDenied:
        raise Http404()

    people_qs = Membro.objects.filter(grupo_casa=grupo)
    people_qs = people_qs.filter(Q(rua__isnull=False) | Q(cep__isnull=False)).order_by('rua', 'numero_casa')

    rows = agrupar_preview_for_queryset(people_qs)
    to_apply = [r for r in rows if r.get('count', 0) >= 2]

    if to_apply:
        result = agrupar_apply_from_preview(to_apply)
        messages.success(request, f"Reagrupamento aplicado: {result.get('created',0)} grupos criados, {result.get('updated',0)} pessoas atualizadas.")
    else:
        messages.info(request, 'Nenhum agrupamento com 2+ pessoas detectado para este grupo; nada foi aplicado.')

    return redirect('secretaria:detalhe_grupo_casa', grupo_id=grupo.id)


@login_required
def detalhe_grupo_casa(request, grupo_id):
    """Detalhe de GrupoCasa; GET mostra membros e histórico de visitas, POST cria VisitaGrupoCasa."""
    grupo = get_object_or_404(GrupoCasa, pk=grupo_id)
    try:
        ministerio = get_ministerio_or_error(request)
        allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
        if not (request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists()) and allowed_churches.exists():
            if not allowed_churches.filter(pk=grupo.igreja_id).exists() and not is_admin_org(request.user):
                raise PermissionDenied('Sem permissão para acessar este grupo')
    except PermissionDenied:
        raise Http404()

    status_permitidos = ['Ativo', 'Desligado', 'Em Disciplina']
    membros = grupo.pessoas.filter(status_pessoa__nome__in=status_permitidos).select_related('tipo_pessoa', 'status_pessoa')
    visitas = grupo.visitas.all().order_by('-data')[:50]

    if request.method == 'POST':
        form = VisitaGrupoCasaForm(request.POST)
        if form.is_valid():
            from django.db import transaction
            with transaction.atomic():
                visita = form.save(commit=False)
                visita.grupo_casa = grupo
                visita.responsavel = request.user
                visita.num_membros = membros.count()
                visita.save()
                if form.cleaned_data.get('marcar_todos'):
                    acompanhamentos = []
                    for p in membros:
                        acompanhamentos.append(AcompanhamentoVisita(
                            membro=p,
                            responsavel=request.user,
                            visita_grupo_casa=visita,
                            tipo_contato='visita',
                            resultado=form.cleaned_data.get('resultado') or '',
                            observacao=form.cleaned_data.get('observacao') or ''
                        ))
                    AcompanhamentoVisita.objects.bulk_create(acompanhamentos)
                messages.success(request, 'Visita registrada com sucesso!')
                return redirect('secretaria:detalhe_grupo_casa', grupo_id=grupo.id)
        else:
            messages.error(request, 'Erro ao registrar visita. Verifique os campos.')
    else:
        form = VisitaGrupoCasaForm()

    try:
        can_agrupar_local = is_admin_or_pastor(request.user)
    except Exception:
        can_agrupar_local = False

    context = {
        'grupo': grupo,
        'membros': membros,
        'visitas': visitas,
        'form': form,
        'titulo_pagina': f'Grupo / Casa: {grupo.nome or (grupo.rua or "")}',
        'ministerio': ministerio,
        'can_edit_grupo': (is_admin_or_pastor(request.user) or has_membro_edit_permission(request.user)),
        'can_agrupar_local': can_agrupar_local,
    }
    return render(request, 'secretaria/grupocasa_detail.html', context)


@login_required
@page_access_required('secretaria_grupos_casa')
def criar_grupo_casa(request):
    """Cria um novo GrupoCasa. Se houver `request.igreja_ativa`, vincula automaticamente."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    scoped_churches = get_request_scoped_churches(request, allowed_churches)

    pessoas_ids_selecionadas = request.POST.getlist('pessoas_ids') if request.method == 'POST' else []
    pessoas_ids_selecionadas = _normalize_people_ids(pessoas_ids_selecionadas)

    pessoas_selecionadas_qs = Membro.objects.filter(
        pk__in=pessoas_ids_selecionadas,
        igreja__in=scoped_churches,
    ).select_related('tipo_pessoa', 'igreja').order_by('nome')

    if request.method == 'POST':
        form = GrupoCasaForm(request.POST)
        if form.is_valid():
            grupo = form.save(commit=False)
            if hasattr(request, 'igreja_ativa') and request.igreja_ativa and scoped_churches.filter(pk=request.igreja_ativa.pk).exists():
                grupo.igreja = request.igreja_ativa
            else:
                try:
                    if getattr(scoped_churches, 'count', None) and scoped_churches.count() == 1:
                        grupo.igreja = scoped_churches.first()
                except Exception as exc:
                    logger.warning('criar_grupo_casa: falha ao inferir igreja única permitida: %s', exc)
            grupo.responsavel = request.user
            if not getattr(grupo, 'igreja', None):
                messages.error(request, 'Não foi possível determinar a igreja para o novo grupo. Verifique sua seleção de igreja/permissões.')
            else:
                from django.db import transaction

                with transaction.atomic():
                    grupo.save()
                    if pessoas_ids_selecionadas:
                        pessoas_para_vincular = Membro.objects.filter(
                            pk__in=pessoas_ids_selecionadas,
                            igreja_id=grupo.igreja_id,
                        )
                        pessoas_para_vincular.update(grupo_casa=grupo)

                if pessoas_ids_selecionadas:
                    messages.success(request, f'Grupo/Casa criado e {len(pessoas_ids_selecionadas)} pessoa(s) vinculada(s) com sucesso!')
                else:
                    messages.success(request, 'Grupo/Casa criado com sucesso!')
                return redirect('secretaria:detalhe_grupo_casa', grupo_id=grupo.id)
    else:
        form = GrupoCasaForm()

    context = {
        'form': form,
        'titulo_pagina': 'Criar Novo Grupo / Casa',
        'ministerio': ministerio,
        'pessoas_ids_selecionadas': pessoas_ids_selecionadas,
        'selected_people_seed': _serialize_selected_people(pessoas_selecionadas_qs),
        'modo_vincular_pessoas': True,
    }
    return render(request, 'secretaria/grupocasa_form.html', context)


@login_required
@page_access_required('secretaria_grupos_casa')
def editar_grupo_casa(request, grupo_id):
    """Editar um GrupoCasa existente."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    scoped_churches = get_request_scoped_churches(request, allowed_churches)
    grupo = get_object_or_404(GrupoCasa, pk=grupo_id)

    try:
        if not (request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists()) and allowed_churches.exists():
            if not allowed_churches.filter(pk=grupo.igreja_id).exists() and not is_admin_org(request.user):
                raise PermissionDenied('Sem permissão para editar este grupo')
    except PermissionDenied:
        raise Http404()

    pessoas_ids_selecionadas = request.POST.getlist('pessoas_ids') if request.method == 'POST' else [
        str(pk) for pk in grupo.pessoas.values_list('pk', flat=True)
    ]
    pessoas_ids_selecionadas = _normalize_people_ids(pessoas_ids_selecionadas)

    pessoas_selecionadas_qs = Membro.objects.filter(
        pk__in=pessoas_ids_selecionadas,
        igreja_id=grupo.igreja_id,
    ).select_related('tipo_pessoa', 'igreja').order_by('nome')

    if request.method == 'POST':
        form = GrupoCasaForm(request.POST, instance=grupo)
        if form.is_valid():
            grupo_editado = form.save(commit=False)
            try:
                if not is_admin_org(request.user) and getattr(grupo_editado, 'igreja', None) and not scoped_churches.filter(pk=grupo_editado.igreja_id).exists():
                    messages.error(request, 'Igreja selecionada inválida para sua permissão.')
                else:
                    from django.db import transaction

                    with transaction.atomic():
                        grupo_editado.save()

                        ids_selecionados = pessoas_ids_selecionadas
                        pessoas_selecionadas_qs = Membro.objects.filter(
                            pk__in=ids_selecionados,
                            igreja_id=grupo_editado.igreja_id,
                        )

                        # Remove vínculos antigos não selecionados
                        Membro.objects.filter(grupo_casa=grupo_editado).exclude(
                            pk__in=pessoas_selecionadas_qs.values_list('pk', flat=True)
                        ).update(grupo_casa=None)

                        # Aplica vínculos selecionados
                        pessoas_selecionadas_qs.update(grupo_casa=grupo_editado)

                    messages.success(request, 'Grupo/Casa e vínculo de pessoas atualizados com sucesso!')
                    return redirect('secretaria:detalhe_grupo_casa', grupo_id=grupo.id)
            except Exception as e:
                logger.exception('Erro ao salvar grupo: %s', e)
                messages.error(request, f'Erro ao salvar o grupo: {e}')
    else:
        form = GrupoCasaForm(instance=grupo)

    context = {
        'form': form,
        'titulo_pagina': f'Editar Grupo / Casa: {grupo.nome or grupo.rua}',
        'ministerio': ministerio,
        'grupo': grupo,
        'pessoas_ids_selecionadas': pessoas_ids_selecionadas,
        'selected_people_seed': _serialize_selected_people(pessoas_selecionadas_qs),
        'modo_vincular_pessoas': True,
    }
    return render(request, 'secretaria/grupocasa_form.html', context)
