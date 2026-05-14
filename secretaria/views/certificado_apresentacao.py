from datetime import date

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render

from core.decorators import page_access_required
from core.utils import get_ministerio_or_error
from secretaria.views.certificados_common import resolver_igreja_certificado


class CertificadoApresentacaoForm(forms.Form):
    MODELO_CHOICES = (
        ('moderno_rosa', 'Modelo 1 - Moderno (Rosa)'),
        ('moderno_azul', 'Modelo 1 - Moderno (Azul)'),
        ('floral_rosa', 'Modelo 2 - Floral (Rosa)'),
        ('floral_azul', 'Modelo 2 - Floral (Azul)'),
    )

    modelo = forms.ChoiceField(label='Modelo do certificado', choices=MODELO_CHOICES, initial='moderno_rosa')
    nome_crianca = forms.CharField(label='Nome da criança', max_length=150, required=False)
    nome_pai = forms.CharField(label='Nome do pai', max_length=150, required=False)
    nome_mae = forms.CharField(label='Nome da mãe', max_length=150, required=False)
    data_nascimento = forms.DateField(
        label='Data de nascimento',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d'],
    )


@login_required
@page_access_required('dashboard_secretaria')
def certificado_apresentacao(request):
    try:
        ministerio = get_ministerio_or_error(request)
    except (PermissionDenied, Http404):
        messages.error(request, 'Não foi possível identificar o ministério para gerar o certificado.')
        return redirect('secretaria:dashboard')

    modelo_inicial = request.GET.get('modelo', 'moderno_rosa')
    valid_modelos = {'moderno_rosa', 'moderno_azul', 'floral_rosa', 'floral_azul'}
    if modelo_inicial not in valid_modelos:
        modelo_inicial = 'moderno_rosa'

    if request.method == 'POST':
        form = CertificadoApresentacaoForm(request.POST)
        if not form.is_valid():
            messages.warning(request, 'Verifique os campos informados para continuar.')
    else:
        form = CertificadoApresentacaoForm(initial={'modelo': modelo_inicial})

    dados = form.cleaned_data if form.is_bound and form.is_valid() else {
        'modelo': request.POST.get('modelo', modelo_inicial) if request.method == 'POST' else modelo_inicial,
        'nome_crianca': request.POST.get('nome_crianca', '') if request.method == 'POST' else '',
        'nome_pai': request.POST.get('nome_pai', '') if request.method == 'POST' else '',
        'nome_mae': request.POST.get('nome_mae', '') if request.method == 'POST' else '',
        'data_nascimento': None,
    }

    modelo_selecionado = dados.get('modelo') or 'moderno_rosa'
    if modelo_selecionado not in valid_modelos:
        modelo_selecionado = 'moderno_rosa'

    igreja = resolver_igreja_certificado(request, ministerio)

    pastor_nome = ''
    logo_url = ''
    nome_igreja = ''

    if igreja:
        pastor_nome = (igreja.pastor_local or '').strip()
        nome_igreja = igreja.nome_igreja or ''
        if getattr(igreja, 'logo1', None):
            logo_url = igreja.logo1.url
        elif getattr(igreja, 'logo2', None):
            logo_url = igreja.logo2.url

    context = {
        'form': form,
        'dados': dados,
        'igreja': igreja,
        'nome_igreja': nome_igreja,
        'pastor_nome': pastor_nome,
        'logo_url': logo_url,
        'data_hoje': date.today(),
        'modelo_selecionado': modelo_selecionado,
    }
    return render(request, 'secretaria/certificados/certificado_apresentacao.html', context)
