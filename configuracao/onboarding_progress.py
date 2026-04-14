# onboarding_progress.py
from configuracao.models_onboarding import OnboardingStatus
from configuracao.utils_onboarding import (
    etapa_igreja_concluida,
    etapa_membros_concluida,
    etapa_configuracoes_concluida,
    etapa_usuarios_concluida,
)

def atualizar_onboarding_status(usuario):
    onboarding, _ = OnboardingStatus.objects.get_or_create(usuario=usuario)
    etapas = []
    if etapa_igreja_concluida(usuario):
        etapas.append(1)
    if etapa_membros_concluida(usuario):
        etapas.append(2)
    if etapa_configuracoes_concluida(usuario):
        etapas.append(3)
    if etapa_usuarios_concluida(usuario):
        etapas.append(4)
    onboarding.etapas_concluidas = etapas
    if etapas:
        onboarding.etapa_atual = max(etapas) + 1 if max(etapas) < 4 else 4
    else:
        onboarding.etapa_atual = 1
    onboarding.save()
    return onboarding
