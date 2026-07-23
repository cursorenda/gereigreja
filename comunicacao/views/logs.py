from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.decorators import page_access_required, verificar_assinatura_valida
from core.utils import get_ministerio_or_error

from ..selectors import listar_logs_whatsapp, resumir_logs_whatsapp


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def logs_whatsapp(request):
	ministerio = get_ministerio_or_error(request)
	status = (request.GET.get('status') or '').strip()
	tipo = (request.GET.get('tipo') or '').strip()
	busca = (request.GET.get('q') or '').strip()

	logs = listar_logs_whatsapp(
		ministerio=ministerio,
		limite=200,
		status=status or None,
		tipo=tipo or None,
		busca=busca or None,
	)
	resumo = resumir_logs_whatsapp(
		ministerio=ministerio,
		status=status or None,
		tipo=tipo or None,
		busca=busca or None,
	)
	return render(
		request,
		'comunicacao/whatsapp/logs_whatsapp.html',
		{
			'logs': logs,
			'resumo': resumo,
			'filtros': {
				'status': status,
				'tipo': tipo,
				'q': busca,
			},
			'ministerio': ministerio,
			'titulo_pagina': 'Logs de WhatsApp',
		},
	)
