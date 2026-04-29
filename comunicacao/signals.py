# c:\Gereigreja\comunicacao\signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Aviso
from notificacoes.models import Notificacao
from configuracao.models import PerfilUsuario # Para pegar todos os usuários do ministério
from django.urls import reverse # Para gerar a URL da notificação

@receiver(post_save, sender=Aviso)
def create_aviso_notification(sender, instance, created, **kwargs):
    if created and instance.publicado:
        # Notificar todos os usuários do ministério
        ministerio = instance.ministerio
        users_in_org = [p.user for p in PerfilUsuario.objects.filter(ministerio=ministerio, user__is_active=True)]

        notification_url = reverse('comunicacao:detalhe_aviso', kwargs={'pk': instance.pk})

        for user in users_in_org:
            # Evitar notificar o próprio autor do aviso se ele não precisar ser notificado
            if user == instance.autor:
                continue # Ou crie uma notificação diferente para o autor

            Notificacao.objects.create(
                user=user,
                ministerio=ministerio,
                message=f"Um novo aviso foi publicado: '{instance.titulo}'",
                notification_type='aviso',
                url=notification_url,
                content_object=instance # Vincula a notificação ao objeto Aviso
            )
