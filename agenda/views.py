
from django.contrib.auth.decorators import login_required
from core.decorators import verificar_assinatura_valida
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, timedelta
from .models import AgendaEvento
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from .forms import AgendaEventoForm

@login_required
def editar_evento(request, pk):
	evento = get_object_or_404(AgendaEvento, pk=pk)
	if request.method == 'POST':
		form = AgendaEventoForm(request.POST, instance=evento, request=request)
		if form.is_valid():
			form.save()
			messages.success(request, 'Evento atualizado com sucesso!')
			return redirect(reverse('agenda:detalhe_evento', args=[evento.pk]))
	else:
		form = AgendaEventoForm(instance=evento, request=request)
	return render(request, 'agenda/editar_evento.html', {'form': form, 'evento': evento})

@login_required
def excluir_evento(request, pk):
	evento = get_object_or_404(AgendaEvento, pk=pk)
	if request.method == 'POST':
		evento.delete()
		messages.success(request, 'Evento excluído com sucesso!')
		return redirect(reverse('agenda:agenda'))
	return render(request, 'agenda/excluir_evento.html', {'evento': evento})

@login_required
def detalhe_evento(request, pk):
	evento = get_object_or_404(AgendaEvento, pk=pk)
	return render(request, 'agenda/detalhe_evento.html', {'evento': evento})

@login_required
def criar_evento(request):
	if request.method == 'POST':
		form = AgendaEventoForm(request.POST, request=request)
		if form.is_valid():
			evento = form.save()
			messages.success(request, 'Evento criado com sucesso!')
			return redirect(reverse('agenda:agenda'))
	else:
		form = AgendaEventoForm(request=request)
	return render(request, 'agenda/criar_evento.html', {'form': form})

@login_required
def agenda_eventos_json(request):
	# Retorna todos os eventos do mês atual em formato JSON para o FullCalendar
	from django.utils import timezone
	from eventos.models import Evento
	from configuracao.models import Igreja
	ministerio = getattr(getattr(request.user, 'perfil', None), 'ministerio', None)
	eventos = Evento.objects.none()
	if ministerio:
		eventos = Evento.objects.filter(igreja__ministerio=ministerio)
	# Filtros
	tipo = request.GET.get('tipo')
	# Sempre usar igreja_ativa do request, nunca GET
	inicio = request.GET.get('inicio')
	fim = request.GET.get('fim')
	busca = request.GET.get('busca')
	if tipo:
		eventos = eventos.filter(tipo=tipo)
	if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
		eventos = eventos.filter(igreja=request.igreja_ativa)
	if inicio:
		eventos = eventos.filter(data_inicio__date__gte=inicio)
	if fim:
		eventos = eventos.filter(data_fim__date__lte=fim)
	if busca:
		eventos = eventos.filter(
			models.Q(titulo__icontains=busca) |
			models.Q(descricao__icontains=busca)
		)
	# Definição de cores por tipo
	tipo_cores = {
		'culto': '#007bff',      # azul
		'reuniao': '#28a745',    # verde
		'festa': '#ffc107',      # amarelo
		'feriado': '#dc3545',    # vermelho
		'estudo': '#6f42c1',     # roxo
		'outro': '#6c757d',      # cinza
	}
	tipo_icones = {
		'culto': 'fa-solid fa-cross',
		'reuniao': 'fa-solid fa-users',
		'festa': 'fa-solid fa-cake-candles',
		'feriado': 'fa-solid fa-umbrella-beach',
		'estudo': 'fa-solid fa-book',
		'outro': 'fa-solid fa-calendar',
	}
	eventos_json = []
	for evento in eventos:
		start_local = timezone.localtime(evento.data_inicio)
		end_local = timezone.localtime(evento.data_fim) if evento.data_fim else start_local
		start_str = start_local.isoformat(timespec='seconds')
		end_str = end_local.isoformat(timespec='seconds')
		cor = tipo_cores.get(evento.tipo, '#6c757d')
		tooltip = f"{evento.titulo}\n{evento.get_tipo_display()}\n{evento.data_inicio:%d/%m/%Y %H:%M} - {evento.data_fim:%d/%m/%Y %H:%M if evento.data_fim else ''}\n{evento.local or ''}\n{evento.descricao or ''}"
		eventos_json.append({
			'id': evento.id,
			'title': evento.titulo,
			'start': start_str,
			'end': end_str,
			'color': cor,
			'icon': tipo_icones.get(evento.tipo, 'fa-solid fa-calendar'),
			'extendedProps': {
				'local': evento.local,
				'descricao': evento.descricao,
				'tipo': evento.get_tipo_display(),
			},
			'tooltip': tooltip,
		})
	return JsonResponse(eventos_json, safe=False)

@login_required
@verificar_assinatura_valida
def agenda_view(request):
	# Exibe eventos do mês atual
	hoje = date.today()
	primeiro_dia = hoje.replace(day=1)
	if primeiro_dia.month == 12:
		proximo_mes = primeiro_dia.replace(year=primeiro_dia.year+1, month=1, day=1)
	else:
		proximo_mes = primeiro_dia.replace(month=primeiro_dia.month+1, day=1)
	from configuracao.models import Igreja
	ministerio = getattr(getattr(request.user, 'perfil', None), 'ministerio', None)
	eventos = AgendaEvento.objects.none()
	if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
		eventos = AgendaEvento.objects.filter(
			igreja=request.igreja_ativa,
			data_inicio__date__gte=primeiro_dia,
			data_inicio__date__lt=proximo_mes
		).order_by('data_inicio')
	return render(request, 'agenda/agenda.html', {
		'eventos': eventos,
		'mes': hoje.strftime('%B'),
		'ano': hoje.year,
	})
