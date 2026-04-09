from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Membro, TransferenciaMembro
from .transferencia_forms import TransferenciaMembroForm


def _get_igrejas_permitidas(request):
    if hasattr(request, 'igrejas_permitidas') and request.igrejas_permitidas is not None:
        return request.igrejas_permitidas
    return None


@login_required
@permission_required('secretaria.add_transferenciamembro', raise_exception=True)
def solicitar_transferencia(request):
    igrejas_permitidas = _get_igrejas_permitidas(request)

    membro_id = request.POST.get('membro') if request.method == 'POST' else request.GET.get('membro_id')
    membro = None

    if membro_id:
        membro_qs = Membro.objects.select_related('igreja', 'igreja__ministerio')
        if igrejas_permitidas is not None:
            membro_qs = membro_qs.filter(igreja__in=igrejas_permitidas)
        membro = get_object_or_404(membro_qs, pk=membro_id)

    if request.method == 'POST':
        form = TransferenciaMembroForm(request.POST, user=request.user, membro=membro)
        if form.is_valid():
            transferencia = form.save(commit=False)
            transferencia.membro = form.cleaned_data['membro']
            transferencia.igreja_origem = transferencia.membro.igreja
            transferencia.usuario_solicitante = request.user
            transferencia.status = TransferenciaMembro.STATUS_AGUARDANDO
            transferencia.save()
            messages.success(request, 'Solicitação de transferência criada com sucesso.')
            return redirect('secretaria:lista_transferencias')
    else:
        form = TransferenciaMembroForm(user=request.user, membro=membro)

    return render(
        request,
        'secretaria/transferencia_form.html',
        {
            'form': form,
            'membro': membro,
        },
    )


@login_required
@permission_required('secretaria.view_transferenciamembro', raise_exception=True)
def lista_transferencias(request):
    igrejas_permitidas = _get_igrejas_permitidas(request)

    transferencias = TransferenciaMembro.objects.select_related(
        'membro',
        'igreja_origem',
        'igreja_destino',
        'usuario_solicitante',
        'usuario_aprovador',
    )

    if igrejas_permitidas is not None:
        transferencias = transferencias.filter(
            Q(igreja_origem__in=igrejas_permitidas) | Q(igreja_destino__in=igrejas_permitidas)
        )

    return render(
        request,
        'secretaria/transferencia_list.html',
        {'transferencias': transferencias},
    )


@login_required
@permission_required('secretaria.change_transferenciamembro', raise_exception=True)
def aprovar_transferencia(request, pk):
    igrejas_permitidas = _get_igrejas_permitidas(request)

    qs = TransferenciaMembro.objects.select_related('membro', 'igreja_destino')
    if igrejas_permitidas is not None:
        qs = qs.filter(igreja_destino__in=igrejas_permitidas)

    transferencia = get_object_or_404(qs, pk=pk)

    if request.method == 'POST':
        if transferencia.status != TransferenciaMembro.STATUS_AGUARDANDO:
            messages.warning(request, 'A transferência já foi processada anteriormente.')
            return redirect('secretaria:lista_transferencias')

        with transaction.atomic():
            membro = transferencia.membro
            membro.igreja = transferencia.igreja_destino
            membro.save(update_fields=['igreja'])

            transferencia.status = TransferenciaMembro.STATUS_APROVADA
            transferencia.data_aprovacao = timezone.now()
            transferencia.usuario_aprovador = request.user
            transferencia.save(update_fields=['status', 'data_aprovacao', 'usuario_aprovador'])

        messages.success(request, 'Transferência aprovada e membro movido para a igreja de destino.')
        return redirect('secretaria:lista_transferencias')

    return render(
        request,
        'secretaria/transferencia_aprovar.html',
        {'transferencia': transferencia},
    )
