from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import TransferenciaMembro
from .transferencia_forms import TransferenciaMembroForm

@login_required
@permission_required('secretaria.add_transferenciamembro', raise_exception=True)
def solicitar_transferencia(request):
    if request.method == 'POST':
        form = TransferenciaMembroForm(request.POST)
        if form.is_valid():
            transferencia = form.save(commit=False)
            transferencia.solicitante = request.user
            transferencia.save()
            messages.success(request, 'Solicitação de transferência criada com sucesso.')
            return redirect('secretaria:lista_transferencias')
    else:
        form = TransferenciaMembroForm()
    return render(request, 'secretaria/transferencia_form.html', {'form': form})

@login_required
def lista_transferencias(request):
    transferencias = TransferenciaMembro.objects.all()
    return render(request, 'secretaria/transferencia_list.html', {'transferencias': transferencias})

@login_required
@permission_required('secretaria.change_transferenciamembro', raise_exception=True)
def aprovar_transferencia(request, pk):
    transferencia = get_object_or_404(TransferenciaMembro, pk=pk)
    if request.method == 'POST':
        transferencia.status = 'aprovada'
        transferencia.save()
        messages.success(request, 'Transferência aprovada com sucesso.')
        return redirect('secretaria:lista_transferencias')
    return render(request, 'secretaria/transferencia_aprovar.html', {'transferencia': transferencia})
