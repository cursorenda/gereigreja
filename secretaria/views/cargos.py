"""
secretaria/views/cargos.py
Views para gerenciamento de cargos (criação, edição, exclusão, ocupantes).
"""
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.decorators import page_access_required, verificar_assinatura_valida
from core.utils import get_ministerio_or_error
from secretaria.forms import AssociarUsuarioMembroForm, CargoForm
from secretaria.models import Cargo, Membro, MembroCargo
from secretaria.utils import get_allowed_churches_for_membros

from secretaria.views._helpers import (
    _cargo_dentro_escopo_usuario,
    _filtrar_cargos_por_escopo_usuario,
    get_request_scoped_churches,
    _membros_queryset_por_escopo,
    _nomes_grupos_permitidos_para_cargos,
)

logger = logging.getLogger(__name__)


@login_required
@page_access_required('secretaria_cargos')
def gerenciar_ocupantes(request, cargo_id):
    cargo = get_object_or_404(Cargo, id=cargo_id)
    if not _cargo_dentro_escopo_usuario(request.user, cargo):
        raise PermissionDenied('Você não pode gerenciar ocupantes deste cargo.')

    membros_base_escopo = _membros_queryset_por_escopo(request)
    membros_selecionaveis_qs = membros_base_escopo.filter(
        Q(tipo_pessoa__nome='Membro') | Q(tipo_pessoa__nome='Obreiro'),
        status_pessoa__nome='Ativo',
    ).order_by('nome')
    membros = list(membros_selecionaveis_qs)

    ocupantes_atual = list(
        MembroCargo.objects.filter(
            cargo=cargo,
            data_fim__isnull=True,
            membro__in=membros_base_escopo,
        ).select_related('membro')
    )
    historico_ocupantes = list(
        MembroCargo.objects.filter(
            cargo=cargo,
            data_fim__isnull=False,
            membro__in=membros_base_escopo,
        ).select_related('membro').order_by('-data_fim')
    )

    membros_lookup_ids = {m.pk for m in membros}
    membros_lookup_ids.update(mc.membro_id for mc in ocupantes_atual if mc.membro_id)
    membros_lookup = list(Membro.objects.filter(pk__in=membros_lookup_ids).order_by('nome'))

    membros_lista = membros_base_escopo.filter(
        Q(tipo_pessoa__nome='Membro') | Q(tipo_pessoa__nome='Obreiro')
    ).order_by('nome')

    page = request.GET.get('page', 1)
    paginator = Paginator(membros_lista, 15)
    try:
        membros_page = paginator.page(page)
    except PageNotAnInteger:
        membros_page = paginator.page(1)
    except EmptyPage:
        membros_page = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        ocupantes_ids = request.POST.get('ocupantes', '')
        if ocupantes_ids:
            ids = []
            for raw_id in ocupantes_ids.split(','):
                normalized = raw_id.strip().replace('.', '').replace(',', '')
                if normalized.isdigit():
                    ids.append(int(normalized))
        else:
            ids = []

        ocupantes_atuais = list(
            MembroCargo.objects.filter(
                cargo=cargo,
                data_fim__isnull=True,
                membro__in=membros_base_escopo,
            ).select_related('membro')
        )
        ids_atuais = [mc.membro_id for mc in ocupantes_atuais]

        removidos = [mc for mc in ocupantes_atuais if mc.membro_id not in ids]
        for mc in removidos:
            mc.data_fim = timezone.now().date()
            mc.save()

        novos_ids = [i for i in ids if i not in ids_atuais]
        for novo_id in novos_ids:
            membro = membros_selecionaveis_qs.filter(pk=novo_id).first()
            if membro:
                MembroCargo.objects.create(membro=membro, cargo=cargo, data_inicio=timezone.now().date())

        messages.success(request, 'Ocupantes do cargo atualizados com sucesso!')
        return redirect('secretaria:gerenciar_ocupantes', cargo_id=cargo.id)
    else:
        ocupantes_iniciais = [mc.membro_id for mc in ocupantes_atual]
        forms_list = []
        sugestoes = {}
        for membro in membros_page:
            form = AssociarUsuarioMembroForm(request.POST if request.method == 'POST' else None, prefix=str(membro.pk), membro=membro)
            if request.method == 'POST' and form.is_valid():
                usuario = form.cleaned_data['usuario']
                membro.usuario = usuario
                membro.save()
            sugestao_id = form.fields['sugestao_usuario_id'].initial
            sugestoes[membro.pk] = int(sugestao_id) if sugestao_id else None
            forms_list.append(form)
        return render(request, 'secretaria/gerenciar_ocupantes.html', {
            'cargo': cargo,
            'membros_page': membros_page,
            'forms_list': forms_list,
            'sugestoes': sugestoes,
            'ocupantes_iniciais': ocupantes_iniciais,
            'membros': membros,
            'membros_lookup': membros_lookup,
            'historico_ocupantes': historico_ocupantes,
        })


@login_required
@verificar_assinatura_valida
@page_access_required('secretaria_cargos')
def excluir_cargo(request, cargo_id):
    cargo = get_object_or_404(Cargo, id=cargo_id)
    if not _cargo_dentro_escopo_usuario(request.user, cargo):
        raise PermissionDenied('Você não pode excluir este cargo.')
    ocupantes = MembroCargo.objects.filter(cargo=cargo).select_related('membro')

    if request.method == 'POST':
        if ocupantes.exists():
            messages.error(request, 'Este cargo possui vínculos de ocupação e não pode ser excluído.')
            return redirect('secretaria:excluir_cargo', cargo_id=cargo.id)

        cargo.delete()
        messages.success(request, 'Cargo excluído com sucesso!')
        return redirect('secretaria:lista_cargos')

    return render(request, 'secretaria/excluir_cargo.html', {'cargo': cargo, 'ocupantes': ocupantes})


@login_required
@verificar_assinatura_valida
@page_access_required('secretaria_cargos')
def criar_cargo(request):
    grupos_permitidos = _nomes_grupos_permitidos_para_cargos(request.user)
    if request.method == 'POST':
        form = CargoForm(request.POST)
        if 'grupo_permissao' in form.fields and grupos_permitidos is not None:
            form.fields['grupo_permissao'].queryset = Group.objects.filter(name__in=grupos_permitidos).order_by('name')
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo criado com sucesso!')
            return redirect('secretaria:lista_cargos')
    else:
        form = CargoForm()
        if 'grupo_permissao' in form.fields and grupos_permitidos is not None:
            form.fields['grupo_permissao'].queryset = Group.objects.filter(name__in=grupos_permitidos).order_by('name')
    return render(request, 'secretaria/criar_cargo.html', {'form': form})


@login_required
@verificar_assinatura_valida
@page_access_required('secretaria_cargos')
def editar_cargo(request, cargo_id):
    cargo = get_object_or_404(Cargo, id=cargo_id)
    if not _cargo_dentro_escopo_usuario(request.user, cargo):
        raise PermissionDenied('Você não pode editar este cargo.')

    grupos_permitidos = _nomes_grupos_permitidos_para_cargos(request.user)
    if request.method == 'POST':
        form = CargoForm(request.POST, instance=cargo)
        if 'grupo_permissao' in form.fields and grupos_permitidos is not None:
            form.fields['grupo_permissao'].queryset = Group.objects.filter(name__in=grupos_permitidos).order_by('name')
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo atualizado com sucesso!')
            return redirect('secretaria:lista_cargos')
    else:
        form = CargoForm(instance=cargo)
        if 'grupo_permissao' in form.fields and grupos_permitidos is not None:
            form.fields['grupo_permissao'].queryset = Group.objects.filter(name__in=grupos_permitidos).order_by('name')
    return render(request, 'secretaria/editar_cargo.html', {'form': form, 'cargo': cargo})


@login_required
@verificar_assinatura_valida
@page_access_required('secretaria_cargos')
def lista_cargos(request):
    nome_cargo = request.GET.get('nome_cargo', '').strip()
    grupo_permissao_id = request.GET.get('grupo_permissao', '').strip()
    ocupante = request.GET.get('ocupante', '').strip()

    ministerio = get_ministerio_or_error(request)
    allowed_churches = getattr(request, 'igrejas_permitidas', None)
    if allowed_churches is None:
        allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    igrejas_filtro = get_request_scoped_churches(request, allowed_churches)

    cargos = Cargo.objects.all().prefetch_related('membrocargo_set__membro', 'grupo_permissao')
    cargos = _filtrar_cargos_por_escopo_usuario(request.user, cargos)

    if nome_cargo:
        cargos = cargos.filter(nome__icontains=nome_cargo)

    if grupo_permissao_id:
        cargos = cargos.filter(grupo_permissao_id=grupo_permissao_id)

    if ocupante:
        cargos = cargos.filter(
            membrocargo__data_fim__isnull=True,
            membrocargo__membro__nome__icontains=ocupante,
            membrocargo__membro__igreja__in=igrejas_filtro,
        ).distinct()

    cargos = cargos.order_by('nome')
    cargos_list = list(cargos)
    igrejas_filtro_ids = set(igrejas_filtro.values_list('pk', flat=True))

    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        for cargo in cargos_list:
            cargo.ocupantes = [
                mc.membro for mc in cargo.membrocargo_set.all()
                if (
                    mc.membro
                    and mc.data_fim is None
                    and mc.membro.igreja_id == request.igreja_ativa.id
                )
            ]
            cargo.igreja = request.igreja_ativa
    else:
        for cargo in cargos_list:
            cargo.ocupantes = [
                mc.membro
                for mc in cargo.membrocargo_set.all()
                if (
                    mc.membro
                    and mc.data_fim is None
                    and mc.membro.igreja_id in igrejas_filtro_ids
                )
            ]
            cargo.igreja = cargo.ocupantes[0].igreja if cargo.ocupantes else None

    igreja_selecionada = str(request.igreja_ativa.pk) if hasattr(request, 'igreja_ativa') and request.igreja_ativa else '0'
    grupos_permitidos = _nomes_grupos_permitidos_para_cargos(request.user)
    grupos_permissao_qs = Group.objects.order_by('name')
    if grupos_permitidos is not None:
        grupos_permissao_qs = grupos_permissao_qs.filter(name__in=grupos_permitidos)

    context = {
        'cargos': cargos_list,
        'grupos_permissao': grupos_permissao_qs,
        'igreja_selecionada': igreja_selecionada,
        'scope_label': f'Igreja: {request.igreja_ativa.nome_igreja}' if hasattr(request, 'igreja_ativa') and request.igreja_ativa else None,
    }
    return render(request, 'secretaria/lista_cargos.html', context)
