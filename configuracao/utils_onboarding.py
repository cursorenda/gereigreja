# utils_onboarding.py
from configuracao.models_onboarding import OnboardingStatus

def etapa_igreja_concluida(usuario):
    perfil = getattr(usuario, 'perfil', None)
    if perfil and getattr(perfil, 'ministerio', None):
        ministerio = perfil.ministerio
    else:
        # Se não houver perfil/ministério, etapa não concluída (deve mostrar assistente)
        return False
    return hasattr(ministerio, 'igrejas') and ministerio.igrejas.exists()

def etapa_membros_concluida(usuario):
    perfil = getattr(usuario, 'perfil', None)
    if perfil and getattr(perfil, 'ministerio', None):
        ministerio = perfil.ministerio
    else:
        return False
    if not hasattr(ministerio, 'igrejas'):
        return False
    return any(getattr(igreja, 'membros', []).exists() for igreja in ministerio.igrejas.all())

def etapa_configuracoes_concluida(usuario):
    perfil = getattr(usuario, 'perfil', None)
    if perfil and getattr(perfil, 'ministerio', None):
        ministerio = perfil.ministerio
    else:
        return False
    return (
        hasattr(ministerio, 'configuracaosistema_set') and ministerio.configuracaosistema_set.exists()
        and hasattr(ministerio, 'horarios') and ministerio.horarios.exists()
    )

def etapa_usuarios_concluida(usuario):
    perfil = getattr(usuario, 'perfil', None)
    if perfil and getattr(perfil, 'ministerio', None):
        ministerio = perfil.ministerio
    else:
        return False
    if not hasattr(ministerio, 'usuarios'):
        return False
    # Exclui o próprio usuário admin inicial
    return ministerio.usuarios.exclude(id=usuario.id).exists()
