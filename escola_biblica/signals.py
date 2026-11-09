from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Aluno, Frequencia, Licao, OfertaClasse, TransferenciaAluno
from .services_agenda import sync_licao_evento_agenda


def _bump_dashboard_cache_version():
    key = 'ebd:dashboard:version'
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 2, None)


@receiver(post_save, sender=Licao)
def sincronizar_licao_na_agenda(sender, instance, **kwargs):
    transaction.on_commit(lambda: sync_licao_evento_agenda(instance))
    transaction.on_commit(_bump_dashboard_cache_version)


@receiver(post_delete, sender=Licao)
@receiver(post_save, sender=Frequencia)
@receiver(post_delete, sender=Frequencia)
@receiver(post_save, sender=OfertaClasse)
@receiver(post_delete, sender=OfertaClasse)
@receiver(post_save, sender=Aluno)
@receiver(post_delete, sender=Aluno)
@receiver(post_save, sender=TransferenciaAluno)
@receiver(post_delete, sender=TransferenciaAluno)
def invalidar_cache_dashboard_ebd(sender, instance, **kwargs):
    transaction.on_commit(_bump_dashboard_cache_version)
