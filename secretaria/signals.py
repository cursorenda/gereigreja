from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Membro, TimelineEvent, StatusHistorico, MembrosCargos, Cargos
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

# Cria evento ao cadastrar novo membro
@receiver(post_save, sender=Membro)
def cria_evento_entrada_membro(sender, instance, created, **kwargs):
    if created and instance.data_entrada:
        # Evita duplicidade
        if not TimelineEvent.objects.filter(membro=instance, tipo_evento='entrada', data=instance.data_entrada).exists():
            data_entrada = instance.data_entrada
            if data_entrada and not hasattr(data_entrada, 'tzinfo'):
                from datetime import datetime
                from django.utils.timezone import make_aware, get_current_timezone
                data_entrada = make_aware(datetime.combine(data_entrada, datetime.min.time()), get_current_timezone())
            TimelineEvent.objects.create(
                membro=instance,
                data=data_entrada,
                tipo_evento='entrada',
                descricao='Entrada do membro no sistema.'
            )


# Cria evento ao registrar histórico de status ou tipo
@receiver(post_save, sender=StatusHistorico)
def cria_evento_status_tipo_membro(sender, instance, created, **kwargs):
    if created:
        data_transicao = instance.data_transicao
        if data_transicao and timezone.is_naive(data_transicao):
            from django.utils.timezone import make_aware, get_current_timezone
            data_transicao = make_aware(data_transicao, get_current_timezone())
        # Mudança de status
        if instance.status_pessoa_anterior != instance.status_pessoa_novo and instance.status_pessoa_novo:
            if not TimelineEvent.objects.filter(membro=instance.membro, tipo_evento='mudanca_status', data=data_transicao).exists():
                TimelineEvent.objects.create(
                    membro=instance.membro,
                    data=data_transicao,
                    tipo_evento='mudanca_status',
                    descricao=f"Mudança de status: {instance.status_pessoa_anterior} → {instance.status_pessoa_novo}"
                )
        # Mudança de tipo
        if instance.tipo_pessoa_anterior != instance.tipo_pessoa_novo and instance.tipo_pessoa_novo:
            if not TimelineEvent.objects.filter(membro=instance.membro, tipo_evento='mudanca_tipo', data=data_transicao).exists():
                TimelineEvent.objects.create(
                    membro=instance.membro,
                    data=data_transicao,
                    tipo_evento='mudanca_tipo',
                    descricao=f"Mudança de tipo: {instance.tipo_pessoa_anterior} → {instance.tipo_pessoa_novo}"
                )


# --- Sinal para adicionar membro ao grupo de permissão ao atribuir cargo ---

# Sempre sincroniza o grupo ao salvar MembrosCargos
@receiver(post_save, sender=MembrosCargos)
def sincroniza_membro_grupo(sender, instance, created, **kwargs):
    if instance.membro and instance.cargo and instance.cargo.grupo_permissao:
        user = getattr(instance.membro, 'usuario', None)
        if user and isinstance(instance.cargo.grupo_permissao, Group):
            instance.cargo.grupo_permissao.user_set.add(user)

# --- Sinal para remover membro do grupo de permissão ao remover cargo ---

# Remove o usuário do grupo ao remover o vínculo de cargo
@receiver(post_delete, sender=MembrosCargos)
def remove_membro_do_grupo(sender, instance, **kwargs):
    if instance.membro and instance.cargo and instance.cargo.grupo_permissao:
        user = getattr(instance.membro, 'usuario', None)
        if user and isinstance(instance.cargo.grupo_permissao, Group):
            instance.cargo.grupo_permissao.user_set.remove(user)
