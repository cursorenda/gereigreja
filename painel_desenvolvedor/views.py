"""
Views para gerenciamento de ativos do sistema (galeria de imagens).

Fornece visualização e edição centralizada de logos, favicons e outras
imagens utilizadas no sistema.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone

from .models import SistemaImagem
from .forms import SistemaImagemForm
from hinario.models import HinoGlobal, HinoDaIgreja, HinoTema


def _redirect_fila_compliance(request):
    """Redireciona para a fila preservando filtros atuais quando informados."""
    tipo = request.POST.get('tipo_retorno', request.GET.get('tipo', 'global'))
    status = request.POST.get('status_retorno', request.GET.get('status', 'pendentes'))
    busca = request.POST.get('busca_retorno', request.GET.get('q', ''))
    page = request.POST.get('page_retorno', request.GET.get('page', '1'))

    query = f"?tipo={tipo}&status={status}&q={busca}&page={page}"
    return redirect(f"{reverse('painel_desenvolvedor:fila_compliance_hinos')}{query}")


def _build_compliance_queryset(filtro_tipo, filtro_status, busca):
    """Constroi o queryset da fila a partir dos filtros atuais."""
    if filtro_tipo not in ['global', 'igreja']:
        filtro_tipo = 'global'

    if filtro_status not in ['pendentes', 'licenciados', 'todos']:
        filtro_status = 'pendentes'

    if filtro_status == 'licenciados':
        status_filter = {
            'license_status': 'licensed',
        }
        blocked_filter = {'blocked_for_public_use': False}
    elif filtro_status == 'todos':
        status_filter = {}
        blocked_filter = {}
    else:
        status_filter = {
            'license_status__in': ['pending_review', 'unknown', 'restricted'],
        }
        blocked_filter = {'blocked_for_public_use': True}

    if filtro_tipo == 'global':
        queryset = HinoGlobal.objects.filter(**blocked_filter, **status_filter).prefetch_related('temas')
        if busca:
            queryset = queryset.filter(
                Q(titulo__icontains=busca)
                | Q(numero__icontains=busca)
                | Q(colecao__icontains=busca)
            )
        queryset = queryset.order_by('colecao', 'numero')
    else:
        queryset = HinoDaIgreja.objects.filter(**blocked_filter, **status_filter).select_related('igreja').prefetch_related('temas')
        if busca:
            queryset = queryset.filter(
                Q(titulo__icontains=busca)
                | Q(numero__icontains=busca)
                | Q(colecao__icontains=busca)
                | Q(igreja__nome__icontains=busca)
            )
        queryset = queryset.order_by('igreja__nome', 'colecao', 'numero')

    return filtro_tipo, filtro_status, queryset


def _resolve_hinos_lote(request, model):
    """Resolve hinos selecionados explicitamente ou todos os filtrados."""
    selection_mode = request.POST.get('selection_mode', 'selected').strip()
    ids_csv = request.POST.get('selected_hino_ids', '').strip()

    if selection_mode == 'filtered':
        tipo = request.POST.get('tipo', '').strip()
        status = request.POST.get('status_retorno', 'pendentes').strip()
        busca = request.POST.get('busca_retorno', '').strip()
        _, _, queryset = _build_compliance_queryset(tipo, status, busca)
        return queryset

    selected_ids = []
    if ids_csv:
        selected_ids = [item for item in ids_csv.split(',') if item.isdigit()]
    if not selected_ids:
        selected_ids = [hid for hid in request.POST.getlist('hino_ids') if hid.isdigit()]

    return model.objects.filter(pk__in=selected_ids)


def eh_desenvolvedor(user):
    """
    Verifica se o usuário é superusuário ou desenvolvedor.
    
    Args:
        user: Objeto User do Django
    
    Returns:
        bool: True se superusuário
    """
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(eh_desenvolvedor)
def galeria_imagens(request):
    """
    Exibe a galeria de imagens do sistema com filtros.
    
    Renderiza um grid com preview de todas as imagens cadastradas,
    organizadas por tipo, com opções de upload e edição.
    
    GET parameters:
        tipo: Filtrar por tipo de imagem
        q: Buscar por descrição
        page: Número da página
    
    Args:
        request: HttpRequest
    
    Returns:
        HttpResponse: Template com galeria renderizada
    """
    queryset = SistemaImagem.objects.all()
    filtro_tipo = request.GET.get('tipo', '')
    busca = request.GET.get('q', '')
    ordenacao = request.GET.get('ordem', 'data_desc')
    
    # Aplicar filtros
    if filtro_tipo and filtro_tipo in dict(SistemaImagem.TIPO_CHOICES):
        queryset = queryset.filter(tipo=filtro_tipo)
    
    if busca:
        queryset = queryset.filter(
            Q(descricao__icontains=busca) |
            Q(notas__icontains=busca)
        )

    # Aplicar ordenacao
    opcoes_ordenacao = {
        'data_desc': ('-data_upload',),
        'data_asc': ('data_upload',),
        'tipo_asc': ('tipo', 'variacao', '-data_upload'),
        'tipo_desc': ('-tipo', '-variacao', '-data_upload'),
    }
    campos_ordenacao = opcoes_ordenacao.get(ordenacao, opcoes_ordenacao['data_desc'])
    queryset = queryset.order_by(*campos_ordenacao)
    
    # Paginação
    paginator = Paginator(queryset, 12)  # 12 itens por página (grid 4x3)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Preparar dados para template
    tipos_disponiveis = SistemaImagem.TIPO_CHOICES
    
    contexto = {
        'page_obj': page_obj,
        'imagens': page_obj.object_list,
        'tipos_disponiveis': tipos_disponiveis,
        'filtro_tipo_selecionado': filtro_tipo,
        'busca': busca,
        'ordenacao': ordenacao,
        'total_imagens': queryset.count(),
    }
    
    return render(request, 'painel_desenvolvedor/galeria_imagens.html', contexto)


@login_required
@user_passes_test(eh_desenvolvedor)
@require_http_methods(['GET', 'POST'])
def criar_imagem(request):
    """
    Cria uma nova imagem do sistema.
    
    POST: Processa o upload e salva a imagem
    GET: Exibe formulário de criação
    
    Args:
        request: HttpRequest
    
    Returns:
        HttpResponse: Formulário (GET) ou redirecionamento (POST)
    """
    if request.method == 'POST':
        form = SistemaImagemForm(request.POST, request.FILES)
        if form.is_valid():
            imagem = form.save()
            messages.success(
                request,
                f'✓ Imagem "{imagem.descricao}" enviada com sucesso!'
            )
            return redirect('painel_desenvolvedor:galeria_imagens')
        else:
            messages.error(request, 'Erro ao processar a imagem. Verifique os dados.')
    else:
        form = SistemaImagemForm()
    
    contexto = {
        'form': form,
        'titulo': 'Nova Imagem',
        'acao': 'Adicionar',
    }
    
    return render(request, 'painel_desenvolvedor/form_imagem.html', contexto)


@login_required
@user_passes_test(eh_desenvolvedor)
@require_http_methods(['GET', 'POST'])
def editar_imagem(request, pk):
    """
    Edita uma imagem existente.
    
    POST: Atualiza os dados da imagem
    GET: Exibe formulário de edição com dados atuais
    
    Args:
        request: HttpRequest
        pk: Primary key da imagem
    
    Returns:
        HttpResponse: Formulário (GET) ou redirecionamento (POST)
    """
    imagem = get_object_or_404(SistemaImagem, pk=pk)
    
    if request.method == 'POST':
        form = SistemaImagemForm(request.POST, request.FILES, instance=imagem)
        if form.is_valid():
            imagem = form.save()
            messages.success(
                request,
                f'✓ Imagem "{imagem.descricao}" atualizada com sucesso!'
            )
            return redirect('painel_desenvolvedor:galeria_imagens')
        else:
            messages.error(request, 'Erro ao atualizar a imagem. Verifique os dados.')
    else:
        form = SistemaImagemForm(instance=imagem)
    
    contexto = {
        'form': form,
        'imagem': imagem,
        'titulo': f'Editar: {imagem.descricao}',
        'acao': 'Atualizar',
    }
    
    return render(request, 'painel_desenvolvedor/form_imagem.html', contexto)


@login_required
@user_passes_test(eh_desenvolvedor)
@require_http_methods(['POST'])
def ativar_imagem(request, pk):
    """
    Marca uma imagem como ativa (versão atual).
    
    Desativa automaticamente outras versões do mesmo tipo/variação.
    
    Args:
        request: HttpRequest
        pk: Primary key da imagem
    
    Returns:
        JsonResponse: Status da operação
    """
    imagem = get_object_or_404(SistemaImagem, pk=pk)
    
    try:
        imagem.ativo = True
        imagem.save()  # Desativa outras versões automaticamente
        
        messages.success(
            request,
            f'✓ {imagem.descricao} marcada como versão ativa!'
        )
        
        redirect_url = request.META.get('HTTP_REFERER') or reverse('painel_desenvolvedor:galeria_imagens')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'sucesso': True,
                'mensagem': f'{imagem.descricao} é agora a versão ativa',
                'redirect': redirect_url,
            })
        return redirect(redirect_url)
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'sucesso': False,
                'mensagem': f'Erro ao ativar imagem: {str(e)}',
            }, status=400)
        messages.error(request, f'Erro ao ativar imagem: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER') or reverse('painel_desenvolvedor:galeria_imagens'))


@login_required
@user_passes_test(eh_desenvolvedor)
@require_http_methods(['POST'])
def deletar_imagem(request, pk):
    """
    Deleta uma imagem do sistema.
    
    Args:
        request: HttpRequest
        pk: Primary key da imagem
    
    Returns:
        JsonResponse: Status da operação
    """
    imagem = get_object_or_404(SistemaImagem, pk=pk)
    descricao = imagem.descricao
    
    try:
        imagem.delete()
        messages.success(request, f'✓ Imagem "{descricao}" removida!')

        redirect_url = request.META.get('HTTP_REFERER') or reverse('painel_desenvolvedor:galeria_imagens')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'sucesso': True,
                'mensagem': f'Imagem "{descricao}" foi removida',
                'redirect': redirect_url,
            })
        return redirect(redirect_url)
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'sucesso': False,
                'mensagem': f'Erro ao deletar imagem: {str(e)}',
            }, status=400)
        messages.error(request, f'Erro ao deletar imagem: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER') or reverse('painel_desenvolvedor:galeria_imagens'))


@login_required
@user_passes_test(eh_desenvolvedor)
def detalhes_imagem(request, pk):
    """
    Exibe detalhes completos de uma imagem.
    
    Mostra preview, metadados, histórico de versões e opções de ação.
    
    Args:
        request: HttpRequest
        pk: Primary key da imagem
    
    Returns:
        HttpResponse: Template com detalhes renderizado
    """
    imagem = get_object_or_404(SistemaImagem, pk=pk)
    
    # Obter outras versões deste tipo
    outras_versoes = SistemaImagem.objects.filter(
        tipo=imagem.tipo,
        variacao=imagem.variacao
    ).exclude(pk=pk).order_by('-ativo', '-data_upload')
    
    # Obter outras variações do mesmo tipo
    outras_variacoes = SistemaImagem.objects.filter(
        tipo=imagem.tipo
    ).exclude(pk=pk).values('variacao').distinct()
    
    contexto = {
        'imagem': imagem,
        'outras_versoes': outras_versoes,
        'outras_variacoes': outras_variacoes,
        'tamanho_kb': imagem.get_tamanho_arquivo_kb(),
        'dimensoes': imagem.get_dimensoes_display(),
    }
    
    return render(request, 'painel_desenvolvedor/detalhes_imagem.html', contexto)


@login_required
@user_passes_test(eh_desenvolvedor)
def fila_compliance_hinos(request):
    """Fila de revisão jurídica/compliance de hinos no painel do desenvolvedor."""
    filtro_tipo = request.GET.get('tipo', 'global')
    filtro_status = request.GET.get('status', 'pendentes')
    busca = request.GET.get('q', '').strip()
    filtro_tipo, filtro_status, queryset = _build_compliance_queryset(filtro_tipo, filtro_status, busca)

    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    contexto = {
        'tipo': filtro_tipo,
        'status': filtro_status,
        'busca': busca,
        'page_obj': page_obj,
        'hinos': page_obj.object_list,
        'total': queryset.count(),
        'temas_disponiveis': HinoTema.objects.filter(ativo=True).order_by('nome'),
        'status_validos_liberacao': ['public_domain', 'licensed'],
        'status_opcoes': [
            ('pendentes', 'Pendentes'),
            ('licenciados', 'Licenciados'),
            ('todos', 'Todos'),
        ],
    }
    return render(request, 'painel_desenvolvedor/fila_compliance_hinos.html', contexto)


@login_required
@user_passes_test(eh_desenvolvedor)
@require_http_methods(['POST'])
def aprovar_liberar_hino(request):
    """Aprova e libera hino para uso publico com evidencias obrigatorias."""
    tipo = request.POST.get('tipo', '').strip()
    hino_id = request.POST.get('hino_id', '').strip()
    license_status = request.POST.get('license_status', '').strip()
    rights_holder = request.POST.get('rights_holder', '').strip()
    license_reference = request.POST.get('license_reference', '').strip()
    legal_notes = request.POST.get('legal_notes', '').strip()

    if tipo not in ['global', 'igreja']:
        return HttpResponseBadRequest('Tipo de hino invalido.')

    if not hino_id.isdigit():
        return HttpResponseBadRequest('ID de hino invalido.')

    if license_status not in ['public_domain', 'licensed']:
        messages.error(request, 'Para liberar, o status deve ser dominio publico ou licenciado.')
        return _redirect_fila_compliance(request)

    if not rights_holder or not license_reference or not legal_notes:
        messages.error(request, 'Detentor, referencia e notas legais sao obrigatorios para liberacao.')
        return _redirect_fila_compliance(request)

    model = HinoGlobal if tipo == 'global' else HinoDaIgreja
    hino = get_object_or_404(model, pk=int(hino_id))

    hino.license_status = license_status
    hino.rights_holder = rights_holder
    hino.license_reference = license_reference
    hino.legal_notes = legal_notes
    hino.reviewed_by = request.user
    hino.reviewed_at = timezone.now()
    hino.blocked_for_public_use = False
    hino.save(update_fields=[
        'license_status',
        'rights_holder',
        'license_reference',
        'legal_notes',
        'reviewed_by',
        'reviewed_at',
        'blocked_for_public_use',
        'updated_at',
    ])

    messages.success(
        request,
        f'Hino "{hino.titulo}" liberado com sucesso para uso publico.',
    )
    return _redirect_fila_compliance(request)


@login_required
@user_passes_test(eh_desenvolvedor)
@require_http_methods(['POST'])
def aprovar_liberar_hino_lote(request):
    """Aprova e libera hinos em lote mantendo as mesmas regras de evidencia."""
    tipo = request.POST.get('tipo', '').strip()
    selection_mode = request.POST.get('selection_mode', 'selected').strip()
    license_status = request.POST.get('license_status', '').strip()
    rights_holder = request.POST.get('rights_holder', '').strip()
    license_reference = request.POST.get('license_reference', '').strip()
    legal_notes = request.POST.get('legal_notes', '').strip()
    hino_ids = [hid for hid in request.POST.getlist('hino_ids') if hid.isdigit()]

    if tipo not in ['global', 'igreja']:
        return HttpResponseBadRequest('Tipo de hino invalido.')

    if selection_mode != 'filtered' and not hino_ids and not request.POST.get('selected_hino_ids', '').strip():
        messages.error(request, 'Selecione ao menos um hino para liberacao em lote.')
        return _redirect_fila_compliance(request)

    if license_status not in ['public_domain', 'licensed']:
        messages.error(request, 'Para liberar em lote, o status deve ser dominio publico ou licenciado.')
        return _redirect_fila_compliance(request)

    if not rights_holder or not license_reference or not legal_notes:
        messages.error(request, 'Detentor, referencia e notas legais sao obrigatorios para liberacao em lote.')
        return _redirect_fila_compliance(request)

    model = HinoGlobal if tipo == 'global' else HinoDaIgreja
    queryset = _resolve_hinos_lote(request, model)

    if not queryset.exists():
        messages.error(request, 'Nenhum hino encontrado para a liberacao em lote.')
        return _redirect_fila_compliance(request)

    liberados = 0
    for hino in queryset:
        hino.license_status = license_status
        hino.rights_holder = rights_holder
        hino.license_reference = license_reference
        hino.legal_notes = legal_notes
        hino.reviewed_by = request.user
        hino.reviewed_at = timezone.now()
        hino.blocked_for_public_use = False
        hino.save(update_fields=[
            'license_status',
            'rights_holder',
            'license_reference',
            'legal_notes',
            'reviewed_by',
            'reviewed_at',
            'blocked_for_public_use',
            'updated_at',
        ])
        liberados += 1

    messages.success(request, f'{liberados} hino(s) liberado(s) com sucesso em lote.')
    return _redirect_fila_compliance(request)


@login_required
@user_passes_test(eh_desenvolvedor)
@require_http_methods(['POST'])
def classificar_tema_hino_lote(request):
    """Aplica um mesmo tema a varios hinos de uma vez."""
    tipo = request.POST.get('tipo', '').strip()
    tema_id = request.POST.get('tema_id', '').strip()

    if tipo not in ['global', 'igreja']:
        return HttpResponseBadRequest('Tipo de hino invalido.')

    if not tema_id.isdigit():
        messages.error(request, 'Selecione um tema valido para a classificacao em lote.')
        return _redirect_fila_compliance(request)

    model = HinoGlobal if tipo == 'global' else HinoDaIgreja
    queryset = _resolve_hinos_lote(request, model)

    if not queryset.exists():
        messages.error(request, 'Selecione ao menos um hino ou use a opcao de todos os filtrados.')
        return _redirect_fila_compliance(request)

    tema = get_object_or_404(HinoTema, pk=int(tema_id), ativo=True)

    classificados = 0
    for hino in queryset:
        hino.temas.add(tema)
        classificados += 1

    messages.success(request, f'Tema "{tema.nome}" aplicado em {classificados} hino(s).')
    return _redirect_fila_compliance(request)
