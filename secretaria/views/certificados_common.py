from secretaria.utils import get_allowed_churches_for_membros
from secretaria.views._helpers import get_request_scoped_churches


def resolver_igreja_certificado(request, ministerio):
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    scoped_churches = get_request_scoped_churches(request, allowed_churches)

    igreja_ativa = getattr(request, 'igreja_ativa', None)
    if igreja_ativa and scoped_churches.filter(pk=igreja_ativa.pk).exists():
        return igreja_ativa

    return scoped_churches.order_by('nome_igreja').first() or allowed_churches.order_by('nome_igreja').first()
