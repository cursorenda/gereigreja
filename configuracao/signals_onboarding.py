# signals_onboarding.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from configuracao.models_onboarding import OnboardingStatus

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def criar_onboarding_status(sender, instance, created, **kwargs):
    if created:
        OnboardingStatus.objects.get_or_create(usuario=instance)
