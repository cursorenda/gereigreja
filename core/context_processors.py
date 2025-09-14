
def sistema_nome(request):
    """Adiciona o nome do sistema ao contexto de todos os templates."""
    return {'SISTEMA_NOME': 'Gereigreja'}
from comunicacao.models import Notificacao

def unread_notifications(request):
    """
    Context processor para adicionar a contagem de notificações não lidas ao contexto de cada template.
    """
    if request.user.is_authenticated:
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.ministerio:
            unread_count = Notificacao.objects.filter(
                user=request.user,
                ministerio=request.user.perfil.ministerio,
                is_read=False
            ).count()
            return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0} # Retorna 0 se não autenticado ou sem ministério




