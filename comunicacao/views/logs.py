from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.decorators import page_access_required, verificar_assinatura_valida
from core.utils import get_ministerio_or_error

from ..selectors import listar_logs_whatsapp


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def logs_whatsapp(request):
	ministerio = get_ministerio_or_error(request)
	logs = listar_logs_whatsapp(ministerio=ministerio, limite=200)
	return render(
		request,
		'comunicacao/whatsapp/logs_whatsapp.html',
		{
			'logs': logs,
			'ministerio': ministerio,
			'titulo_pagina': 'Logs de WhatsApp',
		},
	)
