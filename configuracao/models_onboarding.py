from django.conf import settings
from django.db import models

class OnboardingStatus(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='onboarding_status')
    etapa_atual = models.PositiveSmallIntegerField(default=1)  # 1=igreja, 2=membros, 3=config, 4=usuarios
    etapas_concluidas = models.JSONField(default=list)  # Ex: [1,2]
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_ultima_acao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Onboarding de {self.usuario}"
