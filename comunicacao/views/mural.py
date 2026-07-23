from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.decorators import page_access_required, verificar_assinatura_valida
from core.utils import get_ministerio_or_error

from ..forms import AvisoForm
from ..models import Aviso
from ..utils import can_manage_avisos


@login_required
@verificar_assinatura_valida
@page_access_required('mural_avisos')
def lista_avisos(request):
	ministerio = get_ministerio_or_error(request)
	avisos_qs = Aviso.objects.filter(ministerio=ministerio, publicado=True)
	hoje = timezone.now().date()

	avisos_qs = avisos_qs.filter(Q(data_expiracao__isnull=True) | Q(data_expiracao__gte=hoje))

	if request.igreja_ativa:
		avisos_qs = avisos_qs.filter(
			Q(igrejas_destino__isnull=True) | Q(igrejas_destino=request.igreja_ativa)
		).distinct()
	else:
		avisos_qs = avisos_qs.filter(igrejas_destino__isnull=True).distinct()

	escopo = (request.GET.get('escopo') or 'todos').strip()
	if escopo == 'ministerio':
		avisos_qs = avisos_qs.filter(igrejas_destino__isnull=True)
	elif escopo == 'congregacao' and request.igreja_ativa:
		avisos_qs = avisos_qs.filter(igrejas_destino=request.igreja_ativa)

	query = request.GET.get('q')
	if query:
		avisos_qs = avisos_qs.filter(titulo__icontains=query)

	total_avisos = avisos_qs.count()
	total_sem_expiracao = avisos_qs.filter(data_expiracao__isnull=True).count()
	total_expira_7_dias = avisos_qs.filter(data_expiracao__isnull=False, data_expiracao__lte=hoje + timezone.timedelta(days=7)).count()

	context = {
		'avisos': avisos_qs.order_by('-data_publicacao'),
		'ministerio': ministerio,
		'titulo_pagina': 'Mural de Avisos',
		'can_manage': can_manage_avisos(request.user),
		'query': query,
		'escopo': escopo,
		'total_avisos': total_avisos,
		'total_sem_expiracao': total_sem_expiracao,
		'total_expira_7_dias': total_expira_7_dias,
	}
	return render(request, 'comunicacao/mural/lista_avisos.html', context)


@login_required
@verificar_assinatura_valida
@page_access_required('mural_avisos')
def detalhe_aviso(request, pk):
	ministerio = get_ministerio_or_error(request)
	aviso = get_object_or_404(Aviso, pk=pk, ministerio=ministerio, publicado=True)

	if aviso.data_expiracao and aviso.data_expiracao < timezone.now().date():
		raise PermissionDenied('Este aviso expirou.')

	if request.igreja_ativa and aviso.igrejas_destino.exists() and request.igreja_ativa not in aviso.igrejas_destino.all():
		raise PermissionDenied('Voce nao tem permissao para ver este aviso especifico para outra igreja.')

	context = {
		'aviso': aviso,
		'ministerio': ministerio,
		'titulo_pagina': aviso.titulo,
		'can_manage': can_manage_avisos(request.user),
	}
	return render(request, 'comunicacao/mural/detalhe_aviso.html', context)


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def criar_aviso(request):
	ministerio = get_ministerio_or_error(request)
	if request.method == 'POST':
		form = AvisoForm(request.POST, ministerio=ministerio)
		form.fields['ministerio'].disabled = True
		if form.is_valid():
			try:
				aviso = form.save(commit=False)
				aviso.ministerio = ministerio
				if not aviso.autor:
					aviso.autor = request.user
				aviso.save()
				form.save_m2m()
				messages.success(request, 'Aviso criado com sucesso!')
				return redirect('comunicacao:lista_avisos')
			except Exception as exc:
				messages.error(request, f'Erro ao criar o aviso: {exc}')
		else:
			messages.error(request, 'Por favor, corrija os erros no formulario.')
	else:
		form = AvisoForm(initial={'ministerio': ministerio, 'autor': request.user}, ministerio=ministerio)
		form.fields['ministerio'].disabled = True

	context = {
		'form': form,
		'ministerio': ministerio,
		'titulo_pagina': 'Criar Novo Aviso',
	}
	return render(request, 'comunicacao/mural/form_aviso.html', context)


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def editar_aviso(request, pk):
	ministerio = get_ministerio_or_error(request)
	aviso = get_object_or_404(Aviso, pk=pk, ministerio=ministerio)

	if request.method == 'POST':
		form = AvisoForm(request.POST, instance=aviso, ministerio=ministerio)
		form.fields['ministerio'].disabled = True
		if form.is_valid():
			try:
				if form.cleaned_data.get('ministerio') != ministerio:
					raise PermissionDenied('Nao e permitido alterar o ministerio do aviso.')

				edited_aviso = form.save(commit=False)
				edited_aviso.save()
				form.save_m2m()
				messages.success(request, 'Aviso atualizado com sucesso!')
				return redirect('comunicacao:lista_avisos')
			except PermissionDenied as pd:
				messages.error(request, str(pd))
			except Exception as exc:
				messages.error(request, f'Erro ao atualizar o aviso: {exc}')
		else:
			messages.error(request, 'Por favor, corrija os erros no formulario.')
	else:
		form = AvisoForm(instance=aviso, ministerio=ministerio)
		form.fields['ministerio'].disabled = True

	context = {
		'form': form,
		'aviso': aviso,
		'ministerio': ministerio,
		'titulo_pagina': f'Editar Aviso: {aviso.titulo}',
	}
	return render(request, 'comunicacao/mural/form_aviso.html', context)


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def excluir_aviso(request, pk):
	ministerio = get_ministerio_or_error(request)
	aviso = get_object_or_404(Aviso, pk=pk, ministerio=ministerio)

	if request.method == 'POST':
		try:
			aviso.delete()
			messages.success(request, 'Aviso excluido com sucesso!')
			return redirect('comunicacao:lista_avisos')
		except Exception as exc:
			messages.error(request, f'Erro ao excluir o aviso: {exc}')
			return redirect('comunicacao:detalhe_aviso', pk=pk)

	context = {
		'aviso': aviso,
		'ministerio': ministerio,
		'titulo_pagina': f'Confirmar Exclusao: {aviso.titulo}',
	}
	return render(request, 'comunicacao/mural/confirmar_excluir_aviso.html', context)
