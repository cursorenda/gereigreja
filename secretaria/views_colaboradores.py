from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import MembroCargo
from .forms_colaboradores import MembroCargoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def equipe_ebd_list(request):
    vinculos = MembroCargo.objects.select_related('membro', 'cargo').order_by('-data_inicio')
    return render(request, 'secretaria/equipe_ebd_list.html', {'vinculos': vinculos})

@login_required
def colaborador_add(request):
    if request.method == 'POST':
        form = MembroCargoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Colaborador adicionado com sucesso!')
            return redirect('secretaria:equipe_ebd_list')
    else:
        form = MembroCargoForm()
    return render(request, 'secretaria/colaborador_form.html', {'form': form})

@login_required
def colaborador_edit(request, pk):
    vinculo = get_object_or_404(MembroCargo, pk=pk)
    if request.method == 'POST':
        form = MembroCargoForm(request.POST, instance=vinculo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vínculo atualizado com sucesso!')
            return redirect('secretaria:equipe_ebd_list')
    else:
        form = MembroCargoForm(instance=vinculo)
    return render(request, 'secretaria/colaborador_form.html', {'form': form, 'vinculo': vinculo})

@login_required
def colaborador_delete(request, pk):
    vinculo = get_object_or_404(MembroCargo, pk=pk)
    if request.method == 'POST':
        vinculo.delete()
        messages.success(request, 'Vínculo removido com sucesso!')
        return redirect('secretaria:equipe_ebd_list')
    return render(request, 'secretaria/colaborador_confirm_delete.html', {'vinculo': vinculo})
