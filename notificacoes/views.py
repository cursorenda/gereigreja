from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import verificar_assinatura_valida
from notificacoes.models import Notificacao
from core.utils import get_ministerio_or_error

@login_required
@verificar_assinatura_valida
def lista_notificacoes(request):
	"""
	Lista todas as notificações do usuário logado.
	"""
	ministerio = get_ministerio_or_error(request)
	notificacoes_qs = Notificacao.objects.filter(user=request.user, ministerio=ministerio).order_by('-created_at')

	# Opcional: Filtrar por lidas/não lidas
	status_filter = request.GET.get('status', 'todas')
	if status_filter == 'nao_lidas':
		notificacoes_qs = notificacoes_qs.filter(is_read=False)
	elif status_filter == 'lidas':
		notificacoes_qs = notificacoes_qs.filter(is_read=True)

	context = {
		'notificacoes': notificacoes_qs,
		'ministerio': ministerio,
		'titulo_pagina': "Minhas Notificações",
		'status_filter': status_filter,
	}
	return render(request, 'notificacoes/lista_notificacoes.html', context)

@login_required
@verificar_assinatura_valida
def marcar_notificacao_lida(request, pk):
	"""
	Marca uma notificação específica como lida.
	"""
	ministerio = get_ministerio_or_error(request)
	notificacao = get_object_or_404(Notificacao, pk=pk, user=request.user, ministerio=ministerio)

	if request.method == 'POST':
		notificacao.is_read = True
		notificacao.save()
		messages.success(request, "Notificação marcada como lida.")
		# Redireciona para a URL da notificação se houver, senão para a lista
		if notificacao.url:
			return redirect(notificacao.url)
		return redirect('notificacoes:lista_notificacoes')
    
	messages.error(request, "Método inválido para marcar notificação como lida.")
	return redirect('notificacoes:lista_notificacoes')

@login_required
@verificar_assinatura_valida
def marcar_todas_notificacoes_lidas(request):
	if request.method != 'POST':
		messages.error(request, "Método inválido para marcar todas as notificações como lidas.")
		return redirect('notificacoes:lista_notificacoes')

	ministerio = get_ministerio_or_error(request)
	Notificacao.objects.filter(user=request.user, ministerio=ministerio, is_read=False).update(is_read=True)
	messages.success(request, "Todas as notificações foram marcadas como lidas.")
	return redirect('notificacoes:lista_notificacoes')
