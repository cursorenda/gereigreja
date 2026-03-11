
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
		
		# Aplicar filtro de responsáveis
		from django.contrib.auth import get_user_model
		from secretaria.models import Membro
		User = get_user_model()
		
		ministerio_ativo = None
		if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
			ministerio_ativo = request.igreja_ativa.ministerio
		elif hasattr(request.user, 'perfil'):
			ministerio_ativo = request.user.perfil.ministerio
		
		igreja_id = evento.igreja_id  # Usar igreja do evento sendo editado
		
		if ministerio_ativo and igreja_id:
			membros_com_usuario = Membro.objects.filter(
				igreja_id=igreja_id,
				usuario__isnull=False
			).values_list('usuario_id', flat=True)
			responsaveis_qs = User.objects.filter(id__in=membros_com_usuario)
			usuarios_ministerio = User.objects.filter(
				perfil__ministerio=ministerio_ativo
			).values_list('id', flat=True)
			responsaveis_qs = responsaveis_qs.filter(id__in=usuarios_ministerio)
			form.fields['responsavel'].queryset = responsaveis_qs
		else:
			form.fields['responsavel'].queryset = User.objects.none()
		
		if form.is_valid():
			form.save()
			messages.success(request, 'Evento atualizado com sucesso!')
			return redirect(reverse('agenda:detalhe_evento', args=[evento.pk]))
	else:
		form = AgendaEventoForm(instance=evento, request=request)
		
		# Aplicar filtro de responsáveis
		from django.contrib.auth import get_user_model
		from secretaria.models import Membro
		
		User = get_user_model()
		
		ministerio_ativo = None
		if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
			ministerio_ativo = request.igreja_ativa.ministerio
		elif hasattr(request.user, 'perfil'):
			ministerio_ativo = request.user.perfil.ministerio
		
		igreja_id = evento.igreja_id
		
		if ministerio_ativo and igreja_id:
			# Triplo filtro: igreja + membro com usuário + ministério
			membros_com_usuario = Membro.objects.filter(
				igreja_id=igreja_id,
				usuario__isnull=False
			).values_list('usuario_id', flat=True)
			
			responsaveis_qs = User.objects.filter(id__in=membros_com_usuario)
			
			usuarios_ministerio = User.objects.filter(
				perfil__ministerio=ministerio_ativo
			).values_list('id', flat=True)
			
			responsaveis_qs = responsaveis_qs.filter(id__in=usuarios_ministerio)
			form.fields['responsavel'].queryset = responsaveis_qs
		else:
			form.fields['responsavel'].queryset = User.objects.none()
	
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
		
		# Aplicar filtro de responsáveis
		from django.contrib.auth import get_user_model
		from secretaria.models import Membro
		User = get_user_model()
		
		ministerio_ativo = None
		if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
			ministerio_ativo = request.igreja_ativa.ministerio
		elif hasattr(request.user, 'perfil'):
			ministerio_ativo = request.user.perfil.ministerio
		
		igreja_id = None
		if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
			igreja_id = request.igreja_ativa.pk
		
		if ministerio_ativo and igreja_id:
			membros_com_usuario = Membro.objects.filter(
				igreja_id=igreja_id,
				usuario__isnull=False
			).values_list('usuario_id', flat=True)
			responsaveis_qs = User.objects.filter(id__in=membros_com_usuario)
			usuarios_ministerio = User.objects.filter(
				perfil__ministerio=ministerio_ativo
			).values_list('id', flat=True)
			responsaveis_qs = responsaveis_qs.filter(id__in=usuarios_ministerio)
			form.fields['responsavel'].queryset = responsaveis_qs
		else:
			form.fields['responsavel'].queryset = User.objects.none()
		
		if form.is_valid():
			evento = form.save()
			messages.success(request, 'Evento criado com sucesso!')
			return redirect(reverse('agenda:agenda'))
	else:
		form = AgendaEventoForm(request=request)
		
		# Aplicar filtro de responsáveis
		from django.contrib.auth import get_user_model
		from secretaria.models import Membro
		
		User = get_user_model()
		
		ministerio_ativo = None
		if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
			ministerio_ativo = request.igreja_ativa.ministerio
		elif hasattr(request.user, 'perfil'):
			ministerio_ativo = request.user.perfil.ministerio
		
		igreja_id = None
		if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
			igreja_id = request.igreja_ativa.pk
		
		if ministerio_ativo and igreja_id:
			# Triplo filtro: igreja + membro com usuário + ministério
			membros_com_usuario = Membro.objects.filter(
				igreja_id=igreja_id,
				usuario__isnull=False
			).values_list('usuario_id', flat=True)
			
			responsaveis_qs = User.objects.filter(id__in=membros_com_usuario)
			
			usuarios_ministerio = User.objects.filter(
				perfil__ministerio=ministerio_ativo
			).values_list('id', flat=True)
			
			responsaveis_qs = responsaveis_qs.filter(id__in=usuarios_ministerio)
			form.fields['responsavel'].queryset = responsaveis_qs
		else:
			form.fields['responsavel'].queryset = User.objects.none()
	
	return render(request, 'agenda/criar_evento.html', {'form': form})

@login_required
def agenda_eventos_json(request):
	# Retorna todos os eventos do mês atual em formato JSON para o FullCalendar
	from django.utils import timezone
	from datetime import date, timedelta
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
		
		# Calcular total de participantes esperados (com segurança)
		total_participantes = 0
		try:
			if hasattr(evento, 'get_participantes_esperados'):
				membros_criterios, adicionados_manualmente = evento.get_participantes_esperados()
				total_participantes = membros_criterios.count() + adicionados_manualmente.count()
		except Exception as e:
			# Se houver erro, participantes fica 0
			pass
		
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
				'participantes': total_participantes,
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

@login_required
@verificar_assinatura_valida
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
def importar_feriados_view(request):
	"""View para importar feriados brasileiros via interface web"""
	from django.utils import timezone
	from datetime import datetime, time
	import holidays
	
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
		if AgendaEvento.objects.filter(
			igreja=igreja,
			tipo='feriado',
			data_inicio__date=data
		).exists():
			eventos_existentes += 1
			continue
		
		# Criar evento de feriado
		data_inicio = timezone.make_aware(datetime.combine(data, time(0, 0)))
		data_fim = timezone.make_aware(datetime.combine(data, time(23, 59)))
		
		evento = AgendaEvento.objects.create(
			titulo=nome,
			tipo='feriado',
			data_inicio=data_inicio,
			data_fim=data_fim,
			igreja=igreja,
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
