import json
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import HinoGlobal, HinoDaIgreja, HinoAuditLog


def _serialize_hino_for_audit(hino):
    """Serializa modelo de hino para JSON seguro de auditoria."""
    return {
        'id': hino.id,
        'numero': hino.numero,
        'titulo': hino.titulo,
        'colecao': hino.colecao,
        'license_status': hino.license_status,
        'blocked_for_public_use': hino.blocked_for_public_use,
        'reviewed_by_id': hino.reviewed_by_id if hasattr(hino, 'reviewed_by') else None,
        'reviewed_at': hino.reviewed_at.isoformat() if hino.reviewed_at else None,
    }


@receiver(post_save, sender=HinoGlobal)
def audit_hino_global_change(sender, instance, created, **kwargs):
    """
    Registra mudanças em HinoGlobal na auditoria.

    Foca em eventos de compliance e status jurídico.
    """
    # Não auditar soft deletes aqui; usar sinal de pós-delete
    if instance.deleted_at:
        return

    action = 'created' if created else 'updated'

    # Registrar no log de auditoria
    HinoAuditLog.objects.create(
        tenant_igreja=None,  # HinoGlobal não é tenant-específico
        target_type='global',
        target_id=instance.id,
        action=action,
        after_json=_serialize_hino_for_audit(instance),
        actor_user=None,  # Será preenchido pela view/service
        reason=None,
    )


@receiver(post_save, sender=HinoDaIgreja)
def audit_hino_igreja_change(sender, instance, created, **kwargs):
    """
    Registra mudanças em HinoDaIgreja na auditoria.

    Importante para rastrear customizações por Igreja.
    """
    if instance.deleted_at:
        return

    action = 'created' if created else 'updated'

    HinoAuditLog.objects.create(
        tenant_igreja=instance.igreja,
        target_type='igreja',
        target_id=instance.id,
        action=action,
        after_json=_serialize_hino_for_audit(instance),
        actor_user=instance.created_by if created else instance.updated_by,
        reason=None,
    )


@receiver(post_save, sender=HinoGlobal)
def audit_hino_global_compliance_change(sender, instance, created, update_fields=None, **kwargs):
    """
    Registra mudanças críticas de compliance (bloqueio, desbloqueio, revisão).
    """
    if not update_fields or created:
        return

    # Detectar mudanças de compliance
    compliance_fields = {
        'blocked_for_public_use',
        'license_status',
        'reviewed_by',
        'reviewed_at',
    }

    if not compliance_fields.intersection(update_fields):
        return

    # Determinar ação específica
    if 'blocked_for_public_use' in update_fields:
        action = 'blocked' if instance.blocked_for_public_use else 'unblocked'
    elif 'reviewed_at' in update_fields:
        action = 'reviewed'
    else:
        action = 'updated'

    HinoAuditLog.objects.create(
        tenant_igreja=None,
        target_type='global',
        target_id=instance.id,
        action=action,
        after_json=_serialize_hino_for_audit(instance),
        actor_user=instance.reviewed_by,
        reason=f"Compliance: {instance.get_license_status_display()}",
    )


@receiver(post_save, sender=HinoDaIgreja)
def audit_hino_igreja_compliance_change(sender, instance, created, update_fields=None, **kwargs):
    """
    Registra mudanças críticas de compliance em HinoDaIgreja.
    """
    if not update_fields or created:
        return

    compliance_fields = {
        'blocked_for_public_use',
        'license_status',
        'reviewed_by',
        'reviewed_at',
    }

    if not compliance_fields.intersection(update_fields):
        return

    if 'blocked_for_public_use' in update_fields:
        action = 'blocked' if instance.blocked_for_public_use else 'unblocked'
    elif 'reviewed_at' in update_fields:
        action = 'reviewed'
    else:
        action = 'updated'

    HinoAuditLog.objects.create(
        tenant_igreja=instance.igreja,
        target_type='igreja',
        target_id=instance.id,
        action=action,
        after_json=_serialize_hino_for_audit(instance),
        actor_user=instance.reviewed_by,
        reason=f"Compliance: {instance.get_license_status_display()}",
    )
