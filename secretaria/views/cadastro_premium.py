import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.decorators import page_access_required
from core.utils import get_ministerio_or_error
from secretaria.forms import CadastroPremiumMultietapasForm, MembroForm
from secretaria.utils import get_allowed_churches_for_membros, is_admin_org

logger = logging.getLogger(__name__)


@login_required
@page_access_required('secretaria_pessoas')
def cadastro_premium_multietapas(request):
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)

    if not is_admin_org(request.user) and not allowed_churches.exists():
        messages.error(request, 'Voce nao tem permissao para cadastrar pessoas.')
        return redirect('secretaria:lista_membros')

    if request.method == 'POST':
        form = CadastroPremiumMultietapasForm(
            request.POST,
            request.FILES,
            ministerio=ministerio,
            user=request.user,
            allowed_churches=allowed_churches,
            igreja_inicial=request.igreja_ativa,
        )
        if form.is_valid():
            try:
                pessoa = form.save(commit=False)

                if not is_admin_org(request.user) and not allowed_churches.filter(pk=pessoa.igreja_id).exists():
                    messages.error(request, 'Igreja selecionada invalida para seu perfil.')
                    return render(
                        request,
                        'secretaria/cadastro_premium_multietapas.html',
                        {'form': form, 'titulo_pagina': 'Cadastro Premium por Etapas'},
                    )

                pessoa.observacoes_visita = MembroForm.upsert_premium_etapas_metadata(
                    getattr(pessoa, 'observacoes_visita', ''),
                    {
                        'data_batismo': form.cleaned_data.get('data_batismo'),
                        'numero_credencial': (form.cleaned_data.get('numero_credencial') or '').strip(),
                        'data_consagracao': form.cleaned_data.get('data_consagracao'),
                        'convencao': (form.cleaned_data.get('convencao') or '').strip(),
                        'observacoes_ministeriais': (form.cleaned_data.get('observacoes_ministeriais') or '').strip(),
                    },
                )

                pessoa.save(user=request.user)
                form.save_m2m()
                messages.success(request, f'Pessoa "{pessoa.nome}" cadastrada com sucesso no fluxo premium.')
                return redirect('secretaria:editar_membro', membro_id=pessoa.pk)
            except Exception:
                logger.exception('Erro ao salvar cadastro premium')
                messages.error(request, 'Erro ao salvar cadastro premium. Tente novamente.')
        else:
            messages.error(request, 'Revise os campos destacados e tente novamente.')
    else:
        igreja_inicial = request.igreja_ativa if request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists() else None
        if not igreja_inicial and allowed_churches.count() == 1:
            igreja_inicial = allowed_churches.first()

        form = CadastroPremiumMultietapasForm(
            ministerio=ministerio,
            user=request.user,
            allowed_churches=allowed_churches,
            igreja_inicial=igreja_inicial,
        )

    return render(
        request,
        'secretaria/cadastro_premium_multietapas.html',
        {
            'form': form,
            'titulo_pagina': 'Cadastro Premium por Etapas',
        },
    )
