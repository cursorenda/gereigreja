from eventos.models import Evento
from .policies import categoria_receita_por_evento

def obter_conta_evento_efetiva_id(evento):
    """Resolve a conta de evento, usando fallback da igreja quando existir."""
    if not getattr(evento, 'pk', None):
        return None
    return evento.conta_bancaria_evento_id or getattr(evento.igreja, 'conta_padrao_eventos_id', None)


def obter_evento_no_escopo(allowed_churches, evento_id):
    """Busca evento no escopo permitido, retornando None se invalido."""
    if not evento_id:
        return None
    return (
        Evento.objects
        .filter(pk=evento_id, igreja__in=allowed_churches)
        .select_related('igreja')
        .first()
    )
