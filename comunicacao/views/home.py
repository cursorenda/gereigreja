from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.decorators import verificar_assinatura_valida
from core.utils import get_ministerio_or_error

from ..selectors import obter_contexto_home_comunicacao


@login_required
@verificar_assinatura_valida
def home_comunicacao(request):
	"""Home da Comunicação com KPIs e atalhos de campanhas."""
	ministerio = get_ministerio_or_error(request)
	contexto = obter_contexto_home_comunicacao(ministerio=ministerio)
	contexto['ministerio'] = ministerio
	return render(request, 'comunicacao/home.html', contexto)
