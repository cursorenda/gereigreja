"""
secretaria/views/membros.py
Views de listagem, detalhe, edição, criação, status e ficha dos membros.
"""
import logging
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

from configuracao.models import Igreja, PerfilUsuario
from configuracao.services_assinatura import contar_pessoas_ativas, ministerio_pode_adicionar_pessoa_ativa, obter_limite_pessoas_ativas
from contas.constants import MEMBRO_COMUM, SECRETARIO_LOCAL
from core.decorators import page_access_required, verificar_assinatura_valida
from core.utils import get_ministerio_or_error
from financeiro.models import Receitas
from secretaria.forms import MembroForm, MembroUserManagementForm, StatusHistoricoManualForm
from secretaria.models import (
    Membro, MembroCargo, StatusHistorico, StatusPessoa, Tag, TipoPessoa,
)
from secretaria.utils import get_allowed_churches_for_membros, is_admin_org, has_membro_edit_permission

from secretaria.views._helpers import (
    _get_navigation_context,
    _membros_queryset_por_escopo,
    _user_has_permission_level_or_higher,
    recalcular_grupos_efetivos_usuario,
)

logger = logging.getLogger(__name__)
User = get_user_model()


@login_required
@page_access_required('secretaria_pessoas')
def lista_membros(request):  # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = getattr(request, 'igrejas_permitidas', None)
    if allowed_churches is None:
        allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    membros_queryset = _membros_queryset_por_escopo(request)

    # Filtro por nome/apelido (busca parcial)
    nome_apelido = request.GET.get('nome_apelido')
    if nome_apelido:
        membros_queryset = membros_queryset.filter(
            Q(nome__icontains=nome_apelido) | Q(apelido__icontains=nome_apelido)
        )

    # Filtro GET de query (q)
    query = request.GET.get('q')
    if query:
        membros_queryset = membros_queryset.filter(
            Q(nome__icontains=query) | Q(apelido__icontains=query)
        )

    # Filtro GET de igreja na página (só se nenhuma igreja ativa globalmente)
    igreja_id_get = request.GET.get('igreja')
    if igreja_id_get and not request.igreja_ativa:
        if allowed_churches.filter(pk=igreja_id_get).exists():
            membros_queryset = membros_queryset.filter(igreja_id=igreja_id_get)

    tipos_pessoa = TipoPessoa.objects.all().order_by('nome')
    status_pendentes_qs = StatusPessoa.objects.filter(
        nome__iexact="Pendente"
    ) | StatusPessoa.objects.filter(
        nome__iexact="Aguardando aprovação"
    )
    status_pessoa = StatusPessoa.objects.filter(
        nome__in=["Ativo", "Desligado", "Em Disciplina", "Inativo", "Pendente", "Aguardando aprovação"]
    ).order_by('nome')

    # Filtros extras - tipos, status, gênero
    tipo_id = request.GET.get('tipo')
    if tipo_id and tipo_id.isdigit():
        membros_queryset = membros_queryset.filter(tipo_pessoa_id=tipo_id)
    status_id = request.GET.get('status')
    if status_id and status_id.isdigit():
        membros_queryset = membros_queryset.filter(status_pessoa_id=status_id)
    # Filtro rápido para status pendente
    if request.GET.get('pendentes') == '1':
        membros_queryset = membros_queryset.filter(status_pessoa__in=status_pendentes_qs)
    genero = request.GET.get('genero')
    if genero:
        membros_queryset = membros_queryset.filter(genero=genero)

    # Filtro por tags
    tag_ids = [tid for tid in request.GET.getlist('tags') if tid and tid.isdigit()]
    if tag_ids:
        membros_queryset = membros_queryset.filter(tags__in=tag_ids).distinct()
    todas_tags = Tag.objects.all().order_by('nome')

    # Ordenação clicável
    ORDEM_CAMPOS = {
        'nome': 'nome',
        'data_nascimento': 'nascimento',
        'genero': 'genero',
        'tipo': 'tipo_pessoa__nome',
        'status': 'status_pessoa__nome',
        'igreja': 'igreja__nome_igreja',
    }
    order_by = request.GET.get('order_by', 'nome')
    order_dir = request.GET.get('order_dir', 'asc')
    if order_by not in ORDEM_CAMPOS:
        order_by = 'nome'
    if order_dir not in ['asc', 'desc']:
        order_dir = 'asc'
    order_field = ORDEM_CAMPOS[order_by]
    if order_dir == 'desc':
        order_field = f'-{order_field}'

    membros_queryset = membros_queryset.select_related('igreja', 'tipo_pessoa', 'status_pessoa').order_by(order_field)

    # Paginação
    page = request.GET.get('page', 1)
    paginator = Paginator(membros_queryset, 25)
    try:
        membros_page = paginator.page(page)
    except PageNotAnInteger:
        membros_page = paginator.page(1)
    except EmptyPage:
        membros_page = paginator.page(paginator.num_pages)

    can_edit = has_membro_edit_permission(request.user)
    can_manage_transferencias = _user_has_permission_level_or_higher(request.user, SECRETARIO_LOCAL)
    igrejas_para_filtro_template = allowed_churches if not request.igreja_ativa else Igreja.objects.filter(pk=request.igreja_ativa.pk)

    if request.igreja_ativa:
        scope_label_membros = f"Igreja: {request.igreja_ativa.nome_igreja}"
    else:
        _n = allowed_churches.count()
        scope_label_membros = f"Consolidado ({_n} {'igrejas' if _n != 1 else 'igreja'})" if _n > 0 else "Consolidado"

    context = {
        'membros': membros_page,
        'ministerio': ministerio,
        'query': query,
        'can_edit_membros': can_edit,
        'can_manage_transferencias': can_manage_transferencias,
        'scope_label': scope_label_membros,
        'titulo_pagina': f"Lista de Membros{': ' + request.igreja_ativa.nome_igreja if request.igreja_ativa else ' (Consolidado)'}",
        'igrejas_org': igrejas_para_filtro_template,
        'igreja_selecionada': str(request.igreja_ativa.pk) if request.igreja_ativa else igreja_id_get,
        'tipos_pessoa': tipos_pessoa,
        'status_pessoa': status_pessoa,
        'todas_tags': todas_tags,
        'tags_selecionadas': tag_ids,
        'paginator': paginator,
        'page_obj': membros_page,
        'order_by': order_by,
        'order_dir': order_dir,
    }
    return render(request, 'secretaria/lista_membros.html', context)


def detalhe_membro(request, membro_id):
    from contas.constants import SECRETARIO_LOCAL, PASTOR_LOCAL
    pode_aprovar = False
    if _user_has_permission_level_or_higher(request.user, SECRETARIO_LOCAL) or _user_has_permission_level_or_higher(request.user, PASTOR_LOCAL):
        pode_aprovar = True
    """View para visualização readonly de um membro."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    membro = get_object_or_404(Membro, pk=membro_id, igreja__in=allowed_churches)
    # Impede visualização se o membro não pertence à igreja ativa
    if request.igreja_ativa and membro.igreja != request.igreja_ativa:
        messages.warning(request, "O membro selecionado não pertence à igreja ativa atual.")
        return redirect('secretaria:lista_pessoas')

    tags = membro.tags.all()
    cargos_ativos = MembroCargo.objects.filter(
        membro=membro,
        data_fim__isnull=True
    ).select_related('cargo')
    historico_status = StatusHistorico.objects.filter(membro=membro).order_by('-data_transicao')

    try:
        print(f"[DEBUG editar_membro] igreja_ativa: {getattr(request.igreja_ativa, 'pk', request.igreja_ativa)} - {getattr(request.igreja_ativa, 'nome_igreja', request.igreja_ativa)}")
    except Exception as e:
        print(f"[DEBUG editar_membro] igreja_ativa exception: {e}")
    nav_context = _get_navigation_context(membro_id, request.igreja_ativa)
    try:
        print(f"[DEBUG _get_navigation_context] igreja_ativa: {getattr(request.igreja_ativa, 'pk', request.igreja_ativa)} - {getattr(request.igreja_ativa, 'nome_igreja', request.igreja_ativa)}")
    except Exception as e:
        print(f"[DEBUG _get_navigation_context] igreja_ativa exception: {e}")

    # Aprovação manual
    if request.method == 'POST' and pode_aprovar and membro.status_pessoa.nome == 'Pendente' and request.POST.get('aprovar_membro') == '1':
        status_ativo = StatusPessoa.objects.filter(nome__iexact='Ativo').first()
        if status_ativo:
            if not ministerio_pode_adicionar_pessoa_ativa(ministerio):
                limite = obter_limite_pessoas_ativas(ministerio)
                total_ativos = contar_pessoas_ativas(ministerio)
                messages.error(request, f'Limite de pessoas ativas do plano atingido ({total_ativos}/{limite}). Faça upgrade para aprovar mais pessoas.')
                return redirect('secretaria:detalhe_membro', membro_id=membro.pk)
            membro.status_pessoa = status_ativo
            membro.save(user=request.user)
            messages.success(request, 'Cadastro aprovado e status alterado para Ativo.')
            return redirect('secretaria:detalhe_membro', membro_id=membro.pk)

    membros_igreja_ativa = []
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        membros_igreja_ativa = Membro.objects.filter(
            igreja=request.igreja_ativa
        ).exclude(
            status_pessoa__nome='Inativo'
        ).order_by('nome')
        print(f"[DEBUG membros_igreja_ativa] quantidade: {membros_igreja_ativa.count()}")

    context = {
        'membro': membro,
        'tags': tags,
        'cargos_ativos': cargos_ativos,
        'historico_status': historico_status,
        'ministerio': ministerio,
        'titulo_pagina': f'Visualizar: {membro.nome}',
        'pode_aprovar': pode_aprovar,
        'can_manage_transferencias': _user_has_permission_level_or_higher(request.user, SECRETARIO_LOCAL),
        'membros_igreja_ativa': membros_igreja_ativa,
    }
    context.update(nav_context)
    return render(request, 'secretaria/detalhe_membro.html', context)


@login_required
def imprimir_lista_membros(request):
    """View para impressão da lista de membros com filtros aplicados."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = getattr(request, 'igrejas_permitidas', None)
    if allowed_churches is None:
        allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    membros_queryset = _membros_queryset_por_escopo(request)

    nome_apelido = request.GET.get('nome_apelido')
    if nome_apelido:
        membros_queryset = membros_queryset.filter(
            Q(nome__icontains=nome_apelido) | Q(apelido__icontains=nome_apelido)
        )
    query = request.GET.get('q')
    if query:
        membros_queryset = membros_queryset.filter(
            Q(nome__icontains=query) | Q(apelido__icontains=query)
        )
    igreja_id_get = request.GET.get('igreja')
    if igreja_id_get and not request.igreja_ativa:
        if allowed_churches.filter(pk=igreja_id_get).exists():
            membros_queryset = membros_queryset.filter(igreja_id=igreja_id_get)

    tipo_id = request.GET.get('tipo')
    if tipo_id and tipo_id.isdigit():
        membros_queryset = membros_queryset.filter(tipo_pessoa_id=tipo_id)
    status_id = request.GET.get('status')
    if status_id and status_id.isdigit():
        membros_queryset = membros_queryset.filter(status_pessoa_id=status_id)
    genero = request.GET.get('genero')
    if genero:
        membros_queryset = membros_queryset.filter(genero=genero)
    tag_ids = [tid for tid in request.GET.getlist('tags') if tid and tid.isdigit()]
    if tag_ids:
        membros_queryset = membros_queryset.filter(tags__in=tag_ids).distinct()

    ORDEM_CAMPOS = {
        'nome': 'nome',
        'data_nascimento': 'nascimento',
        'genero': 'genero',
        'tipo': 'tipo_pessoa__nome',
        'status': 'status_pessoa__nome',
        'igreja': 'igreja__nome_igreja',
    }
    order_by = request.GET.get('order_by', 'nome')
    order_dir = request.GET.get('order_dir', 'asc')
    if order_by not in ORDEM_CAMPOS:
        order_by = 'nome'
    if order_dir not in ['asc', 'desc']:
        order_dir = 'asc'
    order_field = ORDEM_CAMPOS[order_by]
    if order_dir == 'desc':
        order_field = f'-{order_field}'

    membros = membros_queryset.select_related('igreja', 'tipo_pessoa', 'status_pessoa').order_by(order_field)

    filtros_aplicados = []
    if nome_apelido:
        filtros_aplicados.append(f"Nome/Apelido: {nome_apelido}")
    if query:
        filtros_aplicados.append(f"Busca: {query}")
    if tipo_id:
        tipo = TipoPessoa.objects.filter(pk=tipo_id).first()
        if tipo:
            filtros_aplicados.append(f"Tipo: {tipo.nome}")
    if status_id:
        status = StatusPessoa.objects.filter(pk=status_id).first()
        if status:
            filtros_aplicados.append(f"Status: {status.nome}")
    if genero:
        filtros_aplicados.append(f"Gênero: {genero}")
    if tag_ids:
        tags = Tag.objects.filter(pk__in=tag_ids)
        filtros_aplicados.append(f"Tags: {', '.join([t.nome for t in tags])}")
    ordem_nomes = {
        'nome': 'Nome',
        'data_nascimento': 'Data de Nascimento',
        'genero': 'Gênero',
        'tipo': 'Tipo',
        'status': 'Status',
        'igreja': 'Igreja',
    }
    ordem_legivel = ordem_nomes.get(order_by, 'Nome')
    direcao_legivel = 'Crescente' if order_dir == 'asc' else 'Decrescente'
    filtros_aplicados.append(f"Ordenação: {ordem_legivel} ({direcao_legivel})")

    context = {
        'membros': membros,
        'ministerio': ministerio,
        'igreja_ativa': request.igreja_ativa,
        'total_membros': membros.count(),
        'filtros_aplicados': filtros_aplicados,
        'data_impressao': timezone.now(),
        'titulo_relatorio': f"Lista de Membros{': ' + request.igreja_ativa.nome_igreja if request.igreja_ativa else ' (Consolidado)'}",
    }
    return render(request, 'secretaria/imprimir_lista_membros.html', context)


@login_required
@page_access_required('secretaria_pessoas')
def editar_membro(request, membro_id):  # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    membro = get_object_or_404(Membro, pk=membro_id, igreja__in=allowed_churches)
    if request.igreja_ativa and membro.igreja != request.igreja_ativa:
        messages.warning(request, "O membro selecionado não pertence à igreja ativa atual.")
        return redirect('secretaria:lista_pessoas')

    user_associado = User.objects.filter(email__iexact=membro.email, perfil__ministerio=ministerio).first()
    perfil_associado = user_associado.perfil if user_associado else None

    if request.method == 'POST':
        form = MembroForm(
            request.POST, request.FILES, instance=membro,
            ministerio=ministerio,
            user=request.user,
            allowed_churches=allowed_churches,
            igreja_inicial=membro.igreja,
        )
        user_management_form = MembroUserManagementForm(
            request.POST,
            membro_instance=membro,
            ministerio=ministerio,
            user_instance=user_associado,
            perfil_instance=perfil_associado,
        )

        if 'submit_membro_form' in request.POST:
            if form.is_valid():
                try:
                    membro_editado = form.save(commit=False)
                    if not is_admin_org(request.user) and not allowed_churches.filter(pk=membro_editado.igreja_id).exists():
                        messages.error(request, "Erro: Igreja selecionada inválida para sua permissão.")
                    else:
                        data_mudanca_tipo = form.cleaned_data.get('data_mudanca_tipo')
                        data_mudanca_status = form.cleaned_data.get('data_mudanca_status')
                        membro_editado.save(
                            user=request.user,
                            data_mudanca_tipo=data_mudanca_tipo,
                            data_mudanca_status=data_mudanca_status,
                        )
                        form.save_m2m()
                        messages.success(request, f'Membro "{membro_editado.nome}" atualizado com sucesso!')
                        submit_value = request.POST.get('submit_membro_form')
                        if submit_value == '_save_and_continue':
                            return redirect('secretaria:editar_membro', membro_id=membro_id)
                        else:
                            return redirect('secretaria:lista_membros')
                except Exception as e:
                    logger.exception(f"Erro ao salvar edição do membro {membro_id} para ministério {ministerio.id}")
                    messages.error(request, f"Ocorreu um erro ao salvar as alterações: {e}")
            else:
                messages.error(request, "Erro ao atualizar membro. Verifique os campos.")

        elif 'submit_user_management_form' in request.POST:
            if user_management_form.is_valid():
                try:
                    with transaction.atomic():
                        if not user_associado:
                            random_password = get_random_string(length=20)
                            user_associado = User.objects.create_user(
                                username=user_management_form.cleaned_data['email_usuario'],
                                email=user_management_form.cleaned_data['email_usuario'],
                                password=random_password,
                                is_active=user_management_form.cleaned_data.get('is_active', False),
                                first_name=membro.nome,
                                last_name=membro.apelido or '',
                            )
                            messages.info(request, "Nova conta de usuário criada. O usuário precisará usar a função 'Esqueci a senha' para definir sua primeira senha.")

                        user_associado.is_active = user_management_form.cleaned_data['is_active']
                        user_associado.is_staff = user_management_form.cleaned_data['is_staff']
                        user_associado.save()

                        recalcular_grupos_efetivos_usuario(
                            user_associado,
                            grupos_manuais=user_management_form.cleaned_data['grupos'],
                            grupos_editaveis=user_management_form.fields['grupos'].queryset,
                        )

                        perfil_associado, created = PerfilUsuario.objects.get_or_create(
                            user=user_associado, defaults={'ministerio': ministerio}
                        )
                        perfil_associado.igrejas_permitidas.set(user_management_form.cleaned_data['igrejas_permitidas'])
                        perfil_associado.ministerio = ministerio
                        perfil_associado.save()

                    messages.success(request, f"Acesso do usuário {user_associado.username} atualizado com sucesso!")
                    redirect_url = reverse('secretaria:editar_membro', args=[membro_id]) + '?tab=acesso-sistema'
                    return redirect(redirect_url)
                except Exception as e:
                    logger.exception(f"Erro ao gerenciar acesso do usuário para membro {membro_id}: {e}")
                    messages.error(request, f"Erro ao gerenciar acesso do usuário: {e}")
                form = MembroForm(
                    instance=membro, ministerio=ministerio, user=request.user,
                    allowed_churches=allowed_churches, igreja_inicial=membro.igreja,
                )
            else:
                messages.error(request, "Erro ao gerenciar acesso do usuário. Verifique os campos.")
                form = MembroForm(
                    instance=membro, ministerio=ministerio, user=request.user,
                    allowed_churches=allowed_churches, igreja_inicial=membro.igreja,
                )
    else:
        form = MembroForm(
            instance=membro,
            ministerio=ministerio,
            user=request.user,
            allowed_churches=allowed_churches,
            igreja_inicial=membro.igreja,
        )
        user_management_form = MembroUserManagementForm(
            membro_instance=membro,
            ministerio=ministerio,
            user_instance=user_associado,
            perfil_instance=perfil_associado,
        )

    contribuicoes_qs = Receitas.objects.filter(membro=membro).select_related('igreja', 'conta_bancaria').order_by('-data')
    contribuicoes = list(contribuicoes_qs) if contribuicoes_qs.exists() else []

    historico_status_qs = membro.transicoes_status_secretaria.all()
    historico_status_membro = list(historico_status_qs) if historico_status_qs.exists() else []

    for h in historico_status_membro:
        pass  # Bloco mantido para evitar erro de indentação

    acompanhamentos_visita = membro.acompanhamentos_visita.all()
    filtro_tipo = request.GET.get('filtro_tipo', '').strip()
    filtro_data = request.GET.get('filtro_data', '').strip()
    if filtro_tipo:
        acompanhamentos_visita = acompanhamentos_visita.filter(tipo_contato=filtro_tipo)
    if filtro_data:
        try:
            filtro_data_dt = datetime.strptime(filtro_data, '%Y-%m-%d').date()
            acompanhamentos_visita = acompanhamentos_visita.filter(data__date=filtro_data_dt)
        except ValueError:
            logger.debug('editar_membro: filtro_data inválido recebido: %s', filtro_data)

    cargos_historico = MembroCargo.objects.filter(membro=membro).select_related('cargo').order_by('-data_inicio')
    nav_context = _get_navigation_context(membro_id, request.igreja_ativa)

    context = {
        'form': form,
        'membro_id': membro_id,
        'ministerio': ministerio,
        'titulo_pagina': f'Editar Membro: {membro.nome}',
        'contribuicoes': list(contribuicoes),
        'user_management_form': user_management_form,
        'user_associado': user_associado,
        'acompanhamentos_visita': list(acompanhamentos_visita),
        'filtro_tipo': filtro_tipo,
        'filtro_data': filtro_data,
        'cargos_historico': list(cargos_historico),
        'historico_status_membro': historico_status_membro,
    }
    context.update(nav_context)
    return render(request, 'secretaria/editar_membro.html', context)


@login_required
@page_access_required('secretaria_pessoas')
def criar_membro(request):  # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    igreja_inicial_para_form = None

    if not is_admin_org(request.user) and not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar membros ou não está associado a nenhuma igreja específica.")
        return redirect('secretaria:lista_membros')

    if request.method == 'POST':
        form = MembroForm(
            request.POST, request.FILES,
            ministerio=ministerio,
            user=request.user,
            allowed_churches=allowed_churches,
            igreja_inicial=request.igreja_ativa,
        )
        if form.is_valid():
            try:
                novo_membro = form.save(commit=False)
                if not is_admin_org(request.user) and not allowed_churches.filter(pk=novo_membro.igreja_id).exists():
                    messages.error(request, "Erro: Igreja selecionada inválida para sua permissão.")
                else:
                    status_destino_nome = getattr(getattr(novo_membro, 'status_pessoa', None), 'nome', '').strip().lower()
                    if status_destino_nome == 'ativo' and not ministerio_pode_adicionar_pessoa_ativa(ministerio):
                        limite = obter_limite_pessoas_ativas(ministerio)
                        total_ativos = contar_pessoas_ativas(ministerio)
                        messages.error(
                            request,
                            f'Limite de pessoas ativas do plano atingido ({total_ativos}/{limite}). Faça upgrade para cadastrar mais pessoas ativas.'
                        )
                        return render(
                            request,
                            'secretaria/criar_membro.html',
                            {
                                'form': form,
                                'ministerio': ministerio,
                                'titulo_pagina': 'Cadastrar Novo Membro',
                            },
                        )
                    data_mudanca_tipo = form.cleaned_data.get('data_mudanca_tipo')
                    data_mudanca_status = form.cleaned_data.get('data_mudanca_status')
                    novo_membro.save(
                        user=request.user,
                        data_mudanca_tipo=data_mudanca_tipo,
                        data_mudanca_status=data_mudanca_status,
                    )
                    messages.success(request, f'Membro "{novo_membro.nome}" cadastrado com sucesso!')
                    if request.POST.get('submit_membro_form') == '_save_and_continue':
                        return redirect('secretaria:editar_membro', membro_id=novo_membro.pk)
                    else:
                        return redirect('secretaria:lista_membros')
            except Exception as e:
                logger.exception(f"Erro ao salvar novo membro para ministério {ministerio.id}")
                messages.error(request, f"Ocorreu um erro ao salvar o membro: {e}")
        else:
            messages.error(request, "Erro ao cadastrar membro. Verifique os campos.")
    else:
        if request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
            igreja_inicial_para_form = request.igreja_ativa
        elif allowed_churches.count() == 1:
            igreja_inicial_para_form = allowed_churches.first()
        form = MembroForm(
            ministerio=ministerio,
            user=request.user,
            allowed_churches=allowed_churches,
            igreja_inicial=igreja_inicial_para_form,
        )

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Cadastrar Novo Membro',
    }
    return render(request, 'secretaria/criar_membro.html', context)


@login_required
@page_access_required('secretaria_pessoas')
def alternar_status_membro(request, membro_id):  # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    membro = get_object_or_404(Membro, pk=membro_id, igreja__in=allowed_churches)

    NOME_STATUSPESSOA_ATIVO = "Ativo"
    NOME_STATUSPESSOA_INATIVO = "Inativo"

    if request.method == 'POST':
        try:
            status_ativo_novo = StatusPessoa.objects.get(nome=NOME_STATUSPESSOA_ATIVO)
            status_inativo_novo = StatusPessoa.objects.get(nome=NOME_STATUSPESSOA_INATIVO)

            acao = ""
            if membro.status_pessoa and membro.status_pessoa.considerar_ativo_relatorios:
                membro.status_pessoa = status_inativo_novo
                acao = "inativado (para relatórios)"
            else:
                if not ministerio_pode_adicionar_pessoa_ativa(ministerio):
                    limite = obter_limite_pessoas_ativas(ministerio)
                    total_ativos = contar_pessoas_ativas(ministerio)
                    messages.error(request, f'Limite de pessoas ativas do plano atingido ({total_ativos}/{limite}). Faça upgrade para ativar mais pessoas.')
                    return redirect('secretaria:lista_membros')
                membro.status_pessoa = status_ativo_novo
                acao = "ativado (para relatórios)"

            membro.save(update_fields=['status_pessoa'])
            messages.success(request, f'Membro "{membro.nome}" foi {acao} com sucesso.')

        except StatusPessoa.DoesNotExist:
            messages.error(request, f"Erro: Os status '{NOME_STATUSPESSOA_ATIVO}' ou '{NOME_STATUSPESSOA_INATIVO}' não foram encontrados no cadastro de Status de Pessoa. Verifique os nomes e o cadastro.")
        except Exception as e:
            logger.exception(f"Erro ao alternar status do membro {membro_id} para ministério {ministerio.id}")
            messages.error(request, f"Ocorreu um erro ao alternar o status do membro: {e}")
        return redirect('secretaria:lista_membros')
    else:
        messages.error(request, "Ação inválida.")
        return redirect('secretaria:lista_membros')


@login_required
@page_access_required('secretaria_pessoas')
def ficha_membro_impressao(request, membro_id):  # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)

    membro = get_object_or_404(
        Membro.objects.select_related(
            'igreja',
            'tipo_pessoa', 'status_pessoa',
        ).prefetch_related(
            'contatos_set',
            'infoeclesiastica_set',
            'familia_set',
            'filhos_set',
            'observacoes_set',
            'membrocargo_set',
            'membrocargo_set__cargo',
        ),
        pk=membro_id,
        igreja__in=allowed_churches,
    )

    context = {
        'membro': membro,
        'ministerio_sistema': ministerio,
        'titulo_pagina': f"Ficha Cadastral - {membro.nome}",
    }
    return render(request, 'secretaria/membro/ficha_membro_impressao.html', context)
