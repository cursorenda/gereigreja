from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from core.decorators import page_access_required


@login_required
@page_access_required('secretaria_pessoas')
def pre_cadastro(request):
    messages.info(request, 'Fluxo antigo de cadastro descontinuado. Voce foi redirecionado para o Cadastro Premium.')
    return redirect('secretaria:cadastrar_membro_premium')


@login_required
@page_access_required('secretaria_pessoas')
def cadastro_detalhado(request, pessoa_id):
    messages.info(request, 'Fluxo antigo de cadastro descontinuado. Voce foi redirecionado para o Cadastro Premium.')
    return redirect('secretaria:cadastrar_membro_premium')


@login_required
@page_access_required('secretaria_pessoas')
def cadastro_complementar(request, pessoa_id):
    messages.info(request, 'Fluxo antigo de cadastro descontinuado. Voce foi redirecionado para o Cadastro Premium.')
    return redirect('secretaria:cadastrar_membro_premium')
