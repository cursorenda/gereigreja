from datetime import date

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render

from core.decorators import page_access_required
from core.utils import get_ministerio_or_error
from configuracao.models import ModeloCartaRecomendacao
from secretaria.views.certificados_common import resolver_igreja_certificado


CARTA_MODELO_TO_TEMPLATE = {
    'padrao': 'secretaria/documentos/modelos/_carta_recomendacao_padrao.html',
    'vales_classico': 'secretaria/documentos/modelos/_carta_recomendacao_vales_classico.html',
}


def _template_carta_fallback():
    return CARTA_MODELO_TO_TEMPLATE['padrao']


def _resolver_template_carta_recomendacao(ministerio):
    codigo_escolhido = (getattr(ministerio, 'modelo_carta_recomendacao', '') or '').strip()

    modelos_disponiveis = ModeloCartaRecomendacao.objects.filter(ativo=True).filter(
        Q(tipo=ModeloCartaRecomendacao.TIPO_PADRAO) |
        Q(tipo=ModeloCartaRecomendacao.TIPO_EXCLUSIVO, ministerio=ministerio)
    ).order_by('ordem', 'nome')

    modelo_selecionado = None
    if codigo_escolhido:
        modelo_selecionado = modelos_disponiveis.filter(codigo=codigo_escolhido).first()

    if not modelo_selecionado:
        modelo_selecionado = modelos_disponiveis.filter(tipo=ModeloCartaRecomendacao.TIPO_PADRAO).first()

    if modelo_selecionado and modelo_selecionado.template_include:
        return modelo_selecionado.codigo, modelo_selecionado.template_include

    return 'padrao', _template_carta_fallback()


class CartaRecomendacaoForm(forms.Form):
    destino = forms.CharField(label='Destino', max_length=180, required=False)
    nome_irmao = forms.CharField(label='Nome do(a) irmao(a)', max_length=180, required=False)
    congregacao = forms.CharField(label='Congregacao', max_length=180, required=False)
    sub_sede = forms.CharField(label='Sub-sede', max_length=180, required=False)
    data_emissao = forms.DateField(
        label='Data da carta',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d'],
    )


@login_required
@page_access_required('dashboard_secretaria')
def carta_recomendacao(request):
    if not getattr(settings, 'FEATURE_CARTA_RECOMENDACAO', False) and not request.user.is_superuser:
        messages.info(request, 'Carta de Recomendacao em finalizacao e temporariamente indisponivel.')
        return redirect('secretaria:dashboard')

    try:
        ministerio = get_ministerio_or_error(request)
    except (PermissionDenied, Http404):
        messages.error(request, 'Nao foi possivel identificar o ministerio para gerar a carta.')
        return redirect('secretaria:dashboard')

    if request.method == 'POST':
        form = CartaRecomendacaoForm(request.POST)
        if not form.is_valid():
            messages.warning(request, 'Verifique os campos informados para continuar.')
    else:
        form = CartaRecomendacaoForm(initial={'data_emissao': date.today()})

    dados = form.cleaned_data if form.is_bound and form.is_valid() else {
        'destino': request.POST.get('destino', '') if request.method == 'POST' else '',
        'nome_irmao': request.POST.get('nome_irmao', '') if request.method == 'POST' else '',
        'congregacao': request.POST.get('congregacao', '') if request.method == 'POST' else '',
        'sub_sede': request.POST.get('sub_sede', '') if request.method == 'POST' else '',
        'data_emissao': None,
    }

    igreja = resolver_igreja_certificado(request, ministerio)

    nome_igreja = ''
    cnpj_igreja = ''
    email_igreja = ''
    logo_url_1 = ''
    logo_url_2 = ''

    if igreja:
        nome_igreja = (getattr(igreja, 'nome_igreja', '') or '').strip()
        cnpj_igreja = (getattr(igreja, 'cnpj', '') or '').strip()
        email_igreja = (getattr(igreja, 'email', '') or '').strip()
        logo_url_1 = igreja.logo1_url
        logo_url_2 = igreja.logo2_url

    if not logo_url_2:
        logo_url_2 = logo_url_1

    pastor_nome = ''
    if igreja:
        pastor_nome = (getattr(igreja, 'pastor_local', '') or '').strip()

    ministerio_nome = (getattr(ministerio, 'nome_fantasia', '') or '').strip()
    ministerio_email = (getattr(ministerio, 'email', '') or '').strip()
    ministerio_telefone = (getattr(ministerio, 'telefone', '') or '').strip()
    ministerio_cnpj = (getattr(ministerio, 'cnpj', '') or '').strip()

    endereco_partes = [
        (getattr(ministerio, 'rua', '') or '').strip(),
        (getattr(ministerio, 'numero', '') or '').strip(),
        (getattr(ministerio, 'bairro', '') or '').strip(),
        (getattr(ministerio, 'cidade', '') or '').strip(),
        (getattr(ministerio, 'estado', '') or '').strip(),
        (getattr(ministerio, 'cep', '') or '').strip(),
    ]
    ministerio_endereco = ', '.join([parte for parte in endereco_partes if parte])

    modelo_carta_recomendacao, template_carta_recomendacao = _resolver_template_carta_recomendacao(ministerio)

    context = {
        'form': form,
        'dados': dados,
        'igreja': igreja,
        'nome_igreja': nome_igreja or 'Assembleia de Deus',
        'cnpj_igreja': cnpj_igreja,
        'email_igreja': email_igreja,
        'logo_url_1': logo_url_1,
        'logo_url_2': logo_url_2,
        'pastor_nome': pastor_nome,
        'congregacao_nome': nome_igreja or 'Congregacao local',
        'ministerio_nome': ministerio_nome or 'Ministerio',
        'ministerio_email': ministerio_email,
        'ministerio_telefone': ministerio_telefone,
        'ministerio_cnpj': ministerio_cnpj,
        'ministerio_endereco': ministerio_endereco,
        'modelo_carta_recomendacao': modelo_carta_recomendacao,
        'template_carta_recomendacao': template_carta_recomendacao,
        'data_hoje': date.today(),
    }
    return render(request, 'secretaria/documentos/carta_recomendacao.html', context)
