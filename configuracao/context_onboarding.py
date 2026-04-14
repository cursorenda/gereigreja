# context_onboarding.py
from configuracao.models_onboarding import OnboardingStatus
from configuracao.utils_onboarding import (
    etapa_igreja_concluida,
    etapa_membros_concluida,
    etapa_configuracoes_concluida,
    etapa_usuarios_concluida,
)

def onboarding_context(request):
    mostrar_assistente = False
    onboarding_etapa = None
    if request.user.is_authenticated:
        try:
            onboarding, _ = OnboardingStatus.objects.get_or_create(usuario=request.user)
            if not etapa_igreja_concluida(request.user):
                onboarding_etapa = 1
            elif not etapa_membros_concluida(request.user):
                onboarding_etapa = 2
            elif not etapa_configuracoes_concluida(request.user):
                onboarding_etapa = 3
            elif not etapa_usuarios_concluida(request.user):
                onboarding_etapa = 4
            if onboarding_etapa:
                mostrar_assistente = True
        except Exception as e:
            import sys
            print(f"[ONBOARDING CONTEXT PROCESSOR ERROR] {e}", file=sys.stderr)
            mostrar_assistente = False
            onboarding_etapa = None
    return {
        'mostrar_assistente': mostrar_assistente,
        'onboarding_etapa': onboarding_etapa,
    }
