
from django.contrib.auth.decorators import login_required
from core.decorators import verificar_assinatura_valida, page_access_required
from django.db import models
from django.shortcuts import render, redirect
from datetime import date, timedelta
from django.http import JsonResponse
from django.contrib import messages

@login_required
@page_access_required('agenda')
def editar_evento(request, pk):
	messages.info(request, 'A edição de eventos foi centralizada no módulo Eventos.')
	return redirect('eventos:lista_eventos')

@login_required
@page_access_required('agenda')
def excluir_evento(request, pk):
	messages.info(request, 'A exclusão de eventos foi centralizada no módulo Eventos.')
	return redirect('eventos:lista_eventos')

@login_required
@page_access_required('agenda')
def detalhe_evento(request, pk):
	messages.info(request, 'Os detalhes de eventos agora ficam no módulo Eventos.')
	return redirect('eventos:lista_eventos')

@login_required
@page_access_required('agenda')
def criar_evento(request):
	messages.info(request, 'A criação de eventos foi centralizada no módulo Eventos.')
	return redirect('eventos:criar_evento')

@login_required
def agenda_eventos_json(request):
	# Retorna todos os eventos do mês atual em formato JSON para o FullCalendar
	from django.utils import timezone
	from datetime import date, timedelta
	from eventos.models import Evento
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
	
	# Se não houver filtro de data, mostrar a partir do domingo da semana atual
	if not inicio and not fim:
		hoje = date.today()
		# Calcular domingo da semana atual (0=segunda, 6=domingo)
		dia_semana = hoje.weekday()  # 0=segunda, 6=domingo
		domingo_semana_atual = hoje - timedelta(days=(dia_semana + 1) % 7)
		data_maxima = hoje + timedelta(days=365)
		eventos = eventos.filter(
			data_inicio__date__gte=domingo_semana_atual,
			data_inicio__date__lte=data_maxima
		)
	
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
		'escola_dominical': '#0d8281',
		'outro': '#6c757d',      # cinza
	}
	tipo_icones = {
		'culto': 'fa-solid fa-cross',
		'reuniao': 'fa-solid fa-users',
		'festa': 'fa-solid fa-cake-candles',
		'feriado': 'fa-solid fa-umbrella-beach',
		'estudo': 'fa-solid fa-book',
		'escola_dominical': 'fa-solid fa-school',
		'outro': 'fa-solid fa-calendar',
	}
	eventos_json = []
	for evento in eventos:
		start_local = timezone.localtime(evento.data_inicio)
		end_local = timezone.localtime(evento.data_fim) if evento.data_fim else start_local
		start_str = start_local.isoformat(timespec='seconds')
		end_str = end_local.isoformat(timespec='seconds')
		cor = tipo_cores.get(evento.tipo, '#6c757d')
		status_evento = getattr(evento, 'status_evento', 'ativo')
		if status_evento == 'cancelado':
			cor = '#9aa0a6'
		
		# Calcular total de participantes esperados (com segurança)
		total_participantes = 0
		try:
			if hasattr(evento, 'get_participantes_esperados'):
				membros_criterios, adicionados_manualmente = evento.get_participantes_esperados()
				total_participantes = membros_criterios.count() + adicionados_manualmente.count()
		except Exception as e:
			# Se houver erro, participantes fica 0
			pass
		
		status_label = 'Cancelado' if status_evento == 'cancelado' else 'Ativo'
		tooltip = f"{evento.titulo}\n{evento.get_tipo_display()}\nStatus: {status_label}\n{evento.data_inicio:%d/%m/%Y %H:%M} - {evento.data_fim:%d/%m/%Y %H:%M if evento.data_fim else ''}\n{evento.local or ''}\n{evento.descricao or ''}"
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
				'status_evento': status_evento,
				'motivo_cancelamento': getattr(evento, 'motivo_cancelamento', ''),
				'participantes': total_participantes,
			},
			'tooltip': tooltip,
		})
	return JsonResponse(eventos_json, safe=False)

@login_required
@verificar_assinatura_valida
@page_access_required('agenda')
def agenda_view(request):
	# Exibe eventos do mês atual
	from eventos.models import Evento
	hoje = date.today()
	primeiro_dia = hoje.replace(day=1)
	if primeiro_dia.month == 12:
		proximo_mes = primeiro_dia.replace(year=primeiro_dia.year+1, month=1, day=1)
	else:
		proximo_mes = primeiro_dia.replace(month=primeiro_dia.month+1, day=1)
	eventos = Evento.objects.none()
	if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
		eventos = Evento.objects.filter(
			igreja=request.igreja_ativa,
			data_inicio__date__gte=primeiro_dia,
			data_inicio__date__lt=proximo_mes
		).order_by('data_inicio')
	return render(request, 'agenda/agenda.html', {
		'eventos': eventos,
		'mes': hoje.strftime('%B'),
		'ano': hoje.year,
	})

@login_required
@verificar_assinatura_valida
@page_access_required('agenda')
def exportar_ics(request):
	"""Exporta eventos filtrados como arquivo ICS para importação em Google Calendar/Outlook"""
	from django.http import HttpResponse
	from django.utils import timezone
	from eventos.models import Evento
	
	try:
		from icalendar import Calendar, Event as iCalEvent
	except ImportError:
		messages.error(request, 'Biblioteca icalendar não instalada. Execute: pip install icalendar')
		return redirect('agenda:agenda')
	
	# Obter eventos com os mesmos filtros da agenda
	ministerio = getattr(getattr(request.user, 'perfil', None), 'ministerio', None)
	eventos = Evento.objects.none()
	if ministerio:
		eventos = Evento.objects.filter(igreja__ministerio=ministerio)
	
	# Aplicar filtros
	tipo = request.GET.get('tipo')
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
	
	# Verificar se há eventos para exportar
	if not eventos.exists():
		messages.warning(request, 'Nenhum evento encontrado com os filtros selecionados.')
		return redirect('agenda:agenda')
	
	# Criar calendário ICS
	cal = Calendar()
	cal.add('prodid', '-//GereIgreja//Agenda//PT')
	cal.add('version', '2.0')
	cal.add('calscale', 'GREGORIAN')
	cal.add('method', 'PUBLISH')
	cal.add('x-wr-calname', f'Agenda - {request.igreja_ativa.nome_igreja if request.igreja_ativa else "GereIgreja"}')
	cal.add('x-wr-timezone', 'America/Sao_Paulo')
	
	# Adicionar eventos ao calendário
	for evento in eventos:
		ical_event = iCalEvent()
		ical_event.add('summary', evento.titulo)
		ical_event.add('dtstart', evento.data_inicio)
		ical_event.add('dtend', evento.data_fim or evento.data_inicio)
		
		if evento.local:
			ical_event.add('location', evento.local)
		if evento.descricao:
			ical_event.add('description', evento.descricao)
		
		ical_event.add('uid', f'evento-{evento.id}@gereigreja.com')
		ical_event.add('dtstamp', timezone.now())
		ical_event.add('status', 'CONFIRMED')
		
		cal.add_component(ical_event)
	
	# Retornar arquivo ICS
	response = HttpResponse(cal.to_ical(), content_type='text/calendar; charset=utf-8')
	filename = f'agenda_{timezone.now():%Y%m%d_%H%M%S}.ics'
	response['Content-Disposition'] = f'attachment; filename="{filename}"'
	
	return response


@login_required
@verificar_assinatura_valida
@page_access_required('agenda')
def importar_feriados_view(request):
	"""View para importar feriados brasileiros via interface web"""
	from django.utils import timezone
	from datetime import datetime, time
	import holidays
	from eventos.models import Evento
	
	if request.method != 'POST':
		return JsonResponse({'sucesso': False, 'erro': 'Método não permitido'}, status=405)
	
	# Obter parâmetros
	ano = int(request.POST.get('ano', datetime.now().year))
	estado = request.POST.get('estado', '').upper() or None
	
	# Obter igreja ativa
	igreja = None
	if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
		igreja = request.igreja_ativa
	else:
		# Buscar pela primeira igreja do ministério do usuário
		ministerio = getattr(getattr(request.user, 'perfil', None), 'ministerio', None)
		if ministerio:
			from configuracao.models import Igreja
			igreja = Igreja.objects.filter(ministerio=ministerio).first()
	
	if not igreja:
		return JsonResponse({'sucesso': False, 'erro': 'Igreja não encontrada'}, status=400)
	
	# Obter feriados brasileiros
	try:
		if estado and len(estado) == 2:
			br_holidays = holidays.Brazil(state=estado, years=ano)
		else:
			br_holidays = holidays.Brazil(years=ano)
	except Exception as e:
		return JsonResponse({'sucesso': False, 'erro': f'Erro ao buscar feriados: {str(e)}'}, status=400)
	
	eventos_criados = 0
	eventos_existentes = 0
	feriados_importados = []
	
	for data, nome in sorted(br_holidays.items()):
		# Verificar se já existe evento de feriado nesta data para esta igreja
		if Evento.objects.filter(
			igreja=igreja,
			tipo='feriado',
			data_inicio__date=data
		).exists():
			eventos_existentes += 1
			continue
		
		# Criar evento de feriado
		data_inicio = timezone.make_aware(datetime.combine(data, time(0, 0)))
		data_fim = timezone.make_aware(datetime.combine(data, time(23, 59)))
		
		evento = Evento.objects.create(
			titulo=nome,
			tipo='feriado',
			data_inicio=data_inicio,
			data_fim=data_fim,
			igreja=igreja,
			criado_por=request.user,
			descricao=f'Feriado {"nacional" if not estado else "nacional/estadual"} importado automaticamente'
		)
		eventos_criados += 1
		feriados_importados.append({
			'data': data.strftime('%d/%m/%Y'),
			'nome': nome
		})
	
	return JsonResponse({
		'sucesso': True,
		'eventos_criados': eventos_criados,
		'eventos_existentes': eventos_existentes,
		'total': eventos_criados + eventos_existentes,
		'feriados': feriados_importados,
		'ano': ano,
		'estado': estado or 'Nacional'
	})
