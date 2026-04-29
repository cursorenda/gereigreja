from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from contas.constants import SECRETARIO_LOCAL, user_has_permission_level_or_higher
from core.utils import get_igrejas_permitidas
from notificacoes.models import Notificacao

from .models import Membro, TransferenciaMembro
from .transferencia_forms import TransferenciaMembroForm


def _get_igrejas_permitidas(request):
    if hasattr(request, 'igrejas_permitidas') and request.igrejas_permitidas is not None:
        return request.igrejas_permitidas
    return None


def _can_manage_transferencias(user):
    return user.is_superuser or user_has_permission_level_or_higher(user, SECRETARIO_LOCAL)


def _notificar_igreja_destino_sobre_transferencia(transferencia):
    """
    Cria notificações para usuários que podem aprovar na igreja destino.
    """
    User = get_user_model()
    ministerio = transferencia.igreja_destino.ministerio
    destinatarios = User.objects.filter(
        is_active=True,
        perfil__ministerio=ministerio,
    ).distinct()

    for usuario in destinatarios:
        if usuario == transferencia.usuario_solicitante:
            continue

        if not _can_manage_transferencias(usuario):
            continue

        igrejas_usuario = get_igrejas_permitidas(usuario, ministerio)
        if not igrejas_usuario.filter(pk=transferencia.igreja_destino_id).exists():
            continue

        Notificacao.objects.create(
            user=usuario,
            ministerio=ministerio,
            message=(
                f"Nova solicitação de transferência para aprovação: "
                f"{transferencia.membro.nome} -> {transferencia.igreja_destino.nome_igreja}."
            ),
            notification_type='aviso',
            url='/secretaria/transferencias/',
        )


def _notificar_gestores_igreja(igreja, transferencia, mensagem, exclude_user=None):
    """Notifica gestores do escopo da igreja informada."""
    User = get_user_model()
    ministerio = igreja.ministerio
    destinatarios = User.objects.filter(is_active=True, perfil__ministerio=ministerio).distinct()

    for usuario in destinatarios:
        if exclude_user and usuario.pk == exclude_user.pk:
            continue
        if not _can_manage_transferencias(usuario):
            continue
        igrejas_usuario = get_igrejas_permitidas(usuario, ministerio)
        if not igrejas_usuario.filter(pk=igreja.pk).exists():
            continue

        Notificacao.objects.create(
            user=usuario,
            ministerio=ministerio,
            message=mensagem,
            notification_type='aviso',
            url='/secretaria/transferencias/',
        )


def _append_observacao(transferencia, observacao):
    texto = (observacao or '').strip()
    if not texto:
        return
    if transferencia.observacao:
        transferencia.observacao = f"{transferencia.observacao}\n{texto}"
    else:
        transferencia.observacao = texto


def _parse_int_or_none(value):
    if value in (None, ''):
        return None
    try:
        return int(value)
    except (TypeError, ValueError, ValidationError):
        return None


@login_required
def solicitar_transferencia(request):
    if not _can_manage_transferencias(request.user):
        raise PermissionDenied

    igrejas_permitidas = _get_igrejas_permitidas(request)

    # Em POST, o campo membro pode vir desabilitado no form (não enviado);
    # por isso mantemos fallback para o membro_id da querystring.
    membro_id_raw = request.POST.get('membro') or request.GET.get('membro_id')
    membro_id = _parse_int_or_none(membro_id_raw)
    membro = None

    if membro_id_raw and membro_id is None:
        messages.error(request, 'ID de membro inválido para solicitar transferência.')
        return redirect('secretaria:lista_membros')

    if membro_id is not None:
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

            _notificar_igreja_destino_sobre_transferencia(transferencia)
            Notificacao.objects.create(
                user=request.user,
                ministerio=transferencia.igreja_origem.ministerio,
                message=(
                    f"Solicitação registrada: {transferencia.membro.nome} -> "
                    f"{transferencia.igreja_destino.nome_igreja}. Aguardando aprovação."
                ),
                notification_type='info',
                url='/secretaria/transferencias/',
            )

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
def lista_transferencias(request):
    if not _can_manage_transferencias(request.user):
        raise PermissionDenied

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

    igrejas_permitidas_ids = []
    if igrejas_permitidas is not None:
        igrejas_permitidas_ids = list(igrejas_permitidas.values_list('id', flat=True))

    return render(
        request,
        'secretaria/transferencia_list.html',
        {
            'transferencias': transferencias,
            'igrejas_permitidas_ids': igrejas_permitidas_ids,
        },
    )


@login_required
def aprovar_transferencia(request, pk):
    if not _can_manage_transferencias(request.user):
        raise PermissionDenied

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

        Notificacao.objects.create(
            user=transferencia.usuario_solicitante,
            ministerio=transferencia.igreja_destino.ministerio,
            message=(
                f"Transferência aprovada: {transferencia.membro.nome} foi recebido em "
                f"{transferencia.igreja_destino.nome_igreja}."
            ),
            notification_type='sucesso',
            url='/secretaria/transferencias/',
        )

        messages.success(request, 'Transferência aprovada e membro movido para a igreja de destino.')
        return redirect('secretaria:lista_transferencias')

    return render(
        request,
        'secretaria/transferencia_aprovar.html',
        {'transferencia': transferencia},
    )


@login_required
def recusar_transferencia(request, pk):
    if not _can_manage_transferencias(request.user):
        raise PermissionDenied

    igrejas_permitidas = _get_igrejas_permitidas(request)
    qs = TransferenciaMembro.objects.select_related('membro', 'igreja_origem', 'igreja_destino', 'usuario_solicitante')
    if igrejas_permitidas is not None:
        qs = qs.filter(igreja_destino__in=igrejas_permitidas)

    transferencia = get_object_or_404(qs, pk=pk)

    if request.method == 'POST':
        if transferencia.status != TransferenciaMembro.STATUS_AGUARDANDO:
            messages.warning(request, 'A transferência já foi processada anteriormente.')
            return redirect('secretaria:lista_transferencias')

        motivo = request.POST.get('motivo', '').strip()

        transferencia.status = TransferenciaMembro.STATUS_RECUSADA
        transferencia.data_aprovacao = timezone.now()
        transferencia.usuario_aprovador = request.user
        _append_observacao(transferencia, f"[Recusa] {motivo}" if motivo else "[Recusa] Sem motivo informado")
        transferencia.save(update_fields=['status', 'data_aprovacao', 'usuario_aprovador', 'observacao'])

        mensagem = (
            f"Transferência recusada por {transferencia.igreja_destino.nome_igreja}: "
            f"{transferencia.membro.nome}."
        )
        if motivo:
            mensagem += f" Motivo: {motivo}"

        Notificacao.objects.create(
            user=transferencia.usuario_solicitante,
            ministerio=transferencia.igreja_destino.ministerio,
            message=mensagem,
            notification_type='alerta',
            url='/secretaria/transferencias/',
        )

        _notificar_gestores_igreja(
            transferencia.igreja_origem,
            transferencia,
            mensagem,
            exclude_user=transferencia.usuario_solicitante,
        )

        messages.success(request, 'Transferência recusada e origem notificada.')
        return redirect('secretaria:lista_transferencias')

    return render(
        request,
        'secretaria/transferencia_recusar.html',
        {'transferencia': transferencia},
    )


@login_required
def cancelar_transferencia(request, pk):
    if not _can_manage_transferencias(request.user):
        raise PermissionDenied

    transferencia = get_object_or_404(
        TransferenciaMembro.objects.select_related('membro', 'igreja_origem', 'igreja_destino', 'usuario_solicitante'),
        pk=pk,
    )

    ministerio = transferencia.igreja_origem.ministerio
    igrejas_usuario = get_igrejas_permitidas(request.user, ministerio)
    pode_cancelar = (
        request.user.pk == transferencia.usuario_solicitante_id
        or request.user.is_superuser
        or igrejas_usuario.filter(pk=transferencia.igreja_origem_id).exists()
    )
    if not pode_cancelar:
        raise PermissionDenied

    if request.method == 'POST':
        if transferencia.status != TransferenciaMembro.STATUS_AGUARDANDO:
            messages.warning(request, 'A transferência já foi processada anteriormente.')
            return redirect('secretaria:lista_transferencias')

        motivo = request.POST.get('motivo', '').strip()

        transferencia.status = TransferenciaMembro.STATUS_CANCELADA
        transferencia.data_aprovacao = timezone.now()
        transferencia.usuario_aprovador = request.user
        _append_observacao(transferencia, f"[Cancelamento] {motivo}" if motivo else "[Cancelamento] Sem motivo informado")
        transferencia.save(update_fields=['status', 'data_aprovacao', 'usuario_aprovador', 'observacao'])

        mensagem = (
            f"Transferência cancelada na origem ({transferencia.igreja_origem.nome_igreja}): "
            f"{transferencia.membro.nome}."
        )
        if motivo:
            mensagem += f" Motivo: {motivo}"

        _notificar_gestores_igreja(
            transferencia.igreja_destino,
            transferencia,
            mensagem,
            exclude_user=request.user,
        )

        messages.success(request, 'Transferência cancelada e destino notificado.')
        return redirect('secretaria:lista_transferencias')

    return render(
        request,
        'secretaria/transferencia_cancelar.html',
        {'transferencia': transferencia},
    )
