from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Licao
from .services_agenda import sync_licao_evento_agenda


@receiver(post_save, sender=Licao)
def sincronizar_licao_na_agenda(sender, instance, **kwargs):
	transaction.on_commit(lambda: sync_licao_evento_agenda(instance))


@receiver(post_delete, sender=Licao)
def limpar_referencia_evento_apos_exclusao(sender, instance, **kwargs):
	evento = getattr(instance, 'evento_agenda', None)
	if evento is None:
		return

	if Licao.objects.filter(evento_agenda=evento).exists():
		return

	if evento.tipo == 'escola_dominical' and evento.status_evento != 'cancelado':
		transaction.on_commit(lambda: evento.delete())
