"""
Views para gerenciamento de ativos do sistema (galeria de imagens).

Fornece visualização e edição centralizada de logos, favicons e outras
imagens utilizadas no sistema.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse

from .models import SistemaImagem
from .forms import SistemaImagemForm


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
