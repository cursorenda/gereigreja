"""
Backfill de notificações para transferências de membros históricas.

Uso:
    python manage.py backfill_notificacoes_transferencias

Opções:
    --dry-run    Apenas exibe o que seria criado, sem persistir nada.
    --force      Recria notificações mesmo para transferências que já possuem
                 ao menos uma notificação vinculada (permite re-execução limpa).

A lógica espelha a implementada na criação normal de transferências em
transferencia_views.py para garantir consistência.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q

from notificacoes.models import Notificacao
from core.utils import get_igrejas_permitidas
from secretaria.models import TransferenciaMembro

User = get_user_model()

URL_TRANSFERENCIAS = '/secretaria/transferencias/'


def _can_manage_transferencias(user):
    from contas.constants import SECRETARIO_LOCAL, user_has_permission_level_or_higher
    return user.is_superuser or user_has_permission_level_or_higher(user, SECRETARIO_LOCAL)


class Command(BaseCommand):
    help = (
        "Gera notificações retroativas para transferências históricas que ainda "
        "não possuem notificação registrada."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Mostra o que seria criado sem salvar no banco.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help='Recria notificações mesmo quando já existem para a transferência.',
        )
        parser.add_argument(
            '--only-id',
            type=int,
            default=None,
            metavar='PK',
            help='Processa apenas a transferência com este ID.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        only_id = options['only_id']

        qs = TransferenciaMembro.objects.select_related(
            'membro',
            'membro__igreja',
            'membro__igreja__ministerio',
            'igreja_origem',
            'igreja_origem__ministerio',
            'igreja_destino',
            'igreja_destino__ministerio',
            'usuario_solicitante',
            'usuario_aprovador',
        ).order_by('data_solicitacao')

        if only_id is not None:
            qs = qs.filter(pk=only_id)
            if not qs.exists():
                raise CommandError(f"Transferência com ID {only_id} não encontrada.")

        total = qs.count()
        self.stdout.write(
            self.style.NOTICE(
                f"Processando {total} transferência(s). "
                f"dry-run={'sim' if dry_run else 'não'}  force={'sim' if force else 'não'}"
            )
        )

        criadas = 0
        ignoradas = 0

        with transaction.atomic():
            for transferencia in qs:
                if not force:
                    ja_tem = Notificacao.objects.filter(
                        url=URL_TRANSFERENCIAS,
                        message__icontains=transferencia.membro.nome,
                    ).filter(
                        Q(user=transferencia.usuario_solicitante)
                        | Q(ministerio=transferencia.igreja_destino.ministerio)
                    ).exists()
                    if ja_tem:
                        ignoradas += 1
                        self.stdout.write(
                            f"  [SKIP] ID={transferencia.id} — {transferencia}"
                        )
                        continue

                novas = self._build_notificacoes(transferencia)
                criadas += len(novas)

                self.stdout.write(
                    f"  [{'DRY' if dry_run else 'OK'}] ID={transferencia.id} — "
                    f"{transferencia.membro.nome} "
                    f"({transferencia.get_status_display()}) → {len(novas)} notificação(ões)"
                )
                for n in novas:
                    self.stdout.write(f"       → [{n.notification_type}] {n.user}: {n.message}")

                if not dry_run:
                    Notificacao.objects.bulk_create(novas, ignore_conflicts=False)

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nConcluído. Notificações criadas: {criadas}  Ignoradas: {ignoradas}"
            )
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_notificacoes(self, transferencia):
        """Retorna lista de instâncias Notificacao não persistidas."""
        status = transferencia.status

        if status == TransferenciaMembro.STATUS_AGUARDANDO:
            return self._notificacoes_aguardando(transferencia)
        elif status == TransferenciaMembro.STATUS_APROVADA:
            return self._notificacoes_aprovada(transferencia)
        elif status == TransferenciaMembro.STATUS_RECUSADA:
            return self._notificacoes_recusada(transferencia)
        elif status == TransferenciaMembro.STATUS_CANCELADA:
            return self._notificacoes_cancelada(transferencia)
        return []

    # --- aguardando ---

    def _notificacoes_aguardando(self, transferencia):
        novas = []

        # Confirmação para o solicitante
        novas.append(Notificacao(
            user=transferencia.usuario_solicitante,
            ministerio=transferencia.igreja_origem.ministerio,
            message=(
                f"Solicitação registrada: {transferencia.membro.nome} → "
                f"{transferencia.igreja_destino.nome_igreja}. Aguardando aprovação."
            ),
            notification_type='info',
            url=URL_TRANSFERENCIAS,
        ))

        # Notificar gestores da igreja destino que podem aprovar
        novas.extend(self._notificacoes_gestores_destino(transferencia))
        return novas

    # --- aprovada ---

    def _notificacoes_aprovada(self, transferencia):
        novas = []

        # Confirmação para o solicitante
        novas.append(Notificacao(
            user=transferencia.usuario_solicitante,
            ministerio=transferencia.igreja_destino.ministerio,
            message=(
                f"Transferência aprovada: {transferencia.membro.nome} foi recebido em "
                f"{transferencia.igreja_destino.nome_igreja}."
            ),
            notification_type='sucesso',
            url=URL_TRANSFERENCIAS,
        ))

        # Notificar gestores da origem sobre saída confirmada
        novas.extend(
            self._notificacoes_gestores_igreja(
                transferencia.igreja_origem,
                transferencia,
                (
                    f"Membro {transferencia.membro.nome} transferido para "
                    f"{transferencia.igreja_destino.nome_igreja}."
                ),
                tipo='sucesso',
                exclude_user=transferencia.usuario_solicitante,
            )
        )
        return novas

    # --- recusada ---

    def _notificacoes_recusada(self, transferencia):
        obs = (transferencia.observacao or '').replace('[Recusa]', '').strip()
        mensagem_base = (
            f"Transferência recusada por {transferencia.igreja_destino.nome_igreja}: "
            f"{transferencia.membro.nome}."
        )
        if obs:
            mensagem_base += f" Motivo: {obs}"

        novas = [
            Notificacao(
                user=transferencia.usuario_solicitante,
                ministerio=transferencia.igreja_destino.ministerio,
                message=mensagem_base,
                notification_type='alerta',
                url=URL_TRANSFERENCIAS,
            )
        ]
        novas.extend(
            self._notificacoes_gestores_igreja(
                transferencia.igreja_origem,
                transferencia,
                mensagem_base,
                tipo='alerta',
                exclude_user=transferencia.usuario_solicitante,
            )
        )
        return novas

    # --- cancelada ---

    def _notificacoes_cancelada(self, transferencia):
        obs = (transferencia.observacao or '').replace('[Cancelamento]', '').strip()
        mensagem_base = (
            f"Transferência cancelada na origem ({transferencia.igreja_origem.nome_igreja}): "
            f"{transferencia.membro.nome}."
        )
        if obs:
            mensagem_base += f" Motivo: {obs}"

        novas = []
        novas.extend(
            self._notificacoes_gestores_igreja(
                transferencia.igreja_destino,
                transferencia,
                mensagem_base,
                tipo='alerta',
                exclude_user=transferencia.usuario_solicitante,
            )
        )
        return novas

    # --- infra ---

    def _notificacoes_gestores_destino(self, transferencia):
        """Notifica gestores da igreja destino (quem deve aprovar)."""
        return self._notificacoes_gestores_igreja(
            transferencia.igreja_destino,
            transferencia,
            (
                f"Nova solicitação de transferência para aprovação: "
                f"{transferencia.membro.nome} → {transferencia.igreja_destino.nome_igreja}."
            ),
            tipo='aviso',
            exclude_user=transferencia.usuario_solicitante,
        )

    def _notificacoes_gestores_igreja(self, igreja, transferencia, mensagem, tipo='aviso', exclude_user=None):
        ministerio = igreja.ministerio
        candidatos = User.objects.filter(
            is_active=True,
            perfil__ministerio=ministerio,
        ).distinct()

        resultado = []
        for usuario in candidatos:
            if exclude_user and usuario.pk == exclude_user.pk:
                continue
            if not _can_manage_transferencias(usuario):
                continue
            igrejas_usuario = get_igrejas_permitidas(usuario, ministerio)
            if not igrejas_usuario.filter(pk=igreja.pk).exists():
                continue
            resultado.append(Notificacao(
                user=usuario,
                ministerio=ministerio,
                message=mensagem,
                notification_type=tipo,
                url=URL_TRANSFERENCIAS,
            ))
        return resultado
