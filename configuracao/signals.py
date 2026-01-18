from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import PerfilUsuario, Ministerio

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_perfilusuario_for_new_user(sender, instance, created, **kwargs):
    """
    Cria automaticamente um PerfilUsuario para cada novo usuário.
    Se já existir, não faz nada.
    """
    if created:
        # Tenta obter o ministério padrão (opcional, pode ser None)
        ministerio = getattr(instance, 'ministerio', None)
        if ministerio is not None:
            PerfilUsuario.objects.get_or_create(user=instance, defaults={'ministerio': ministerio})

# Função utilitária para garantir/atualizar perfil ao aceitar convite
# (pode ser chamada no fluxo de aceite do convite)
def garantir_perfilusuario(user, ministerio):
    perfil, created = PerfilUsuario.objects.get_or_create(user=user, defaults={'ministerio': ministerio})
    if not created and perfil.ministerio != ministerio:
        perfil.ministerio = ministerio
        perfil.save()
    return perfil
