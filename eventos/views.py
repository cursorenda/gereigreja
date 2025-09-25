from django.contrib.auth.decorators import login_required
@login_required
def criar_evento_profissional(request):
	if request.method == 'POST':
		form = EventoForm(request.POST, request.FILES)
		if form.is_valid():
			evento = form.save(commit=False)
			evento.criado_por = request.user
			if 'capa' in request.FILES:
				evento.capa = request.FILES['capa']
			from django.utils import timezone
			if evento.data_inicio and evento.quantidade_dias:
				data_fim = evento.data_inicio + timezone.timedelta(days=evento.quantidade_dias - 1)
				if evento.hora_termino:
					data_fim = data_fim.replace(hour=evento.hora_termino.hour, minute=evento.hora_termino.minute, second=0, microsecond=0)
				evento.data_fim = data_fim
			evento.save()
			form.save_m2m()
			# Salva anexos
			for file in request.FILES.getlist('anexos'):
				from .models import EventoAnexo
				anexo = EventoAnexo(evento=evento, arquivo=file, nome=file.name)
				anexo.save()

			# Geração de eventos recorrentes
			from .utils import gerar_datas_recorrencia
			datas = gerar_datas_recorrencia(evento)
			eventos_criados = []
			for dt in datas:
				if dt == evento.data_inicio:
					ev = evento
				else:
					data_fim = dt + timezone.timedelta(days=evento.quantidade_dias - 1)
					if evento.hora_termino:
						data_fim = data_fim.replace(hour=evento.hora_termino.hour, minute=evento.hora_termino.minute, second=0, microsecond=0)
					ev = Evento(
						igreja=evento.igreja,
						titulo=evento.titulo,
						descricao=evento.descricao,
						tipo=evento.tipo,
						local=evento.local,
						responsavel=evento.responsavel,
						data_inicio=dt,
						data_fim=data_fim,
						recorrente=False,  # filhos não são recorrentes
						frequencia='nenhuma',
						intervalo=1,
						capa=evento.capa,
						criado_por=request.user,
						atualizado_em=timezone.now(),
						criado_em=timezone.now(),
						quantidade_dias=evento.quantidade_dias,
						hora_termino=evento.hora_termino,
					)
					ev.save()
					ev.tipos_participantes.set(evento.tipos_participantes.all())
					ev.status_participantes.set(evento.status_participantes.all())
					ev.cargo_participantes.set(evento.cargo_participantes.all())
				eventos_criados.append(ev)

			# Geração automática dos participantes esperados para cada evento
			from secretaria.models import Membro, StatusPessoa
			from .models import ParticipacaoEvento
			status_nomes = ['Ativo', 'Desligado', 'Em Disciplina']
			status_ids = list(StatusPessoa.objects.filter(nome__in=status_nomes).values_list('id', flat=True))
			for ev in eventos_criados:
				if ev.incluir_todos_membros:
					membros_qs = Membro.objects.filter(igreja=ev.igreja, status_pessoa__in=status_ids)
				else:
					membros_qs = Membro.objects.filter(igreja=ev.igreja, status_pessoa__in=status_ids)
					if ev.tipos_participantes.exists():
						membros_qs = membros_qs.filter(tipo_pessoa__in=ev.tipos_participantes.all())
					if ev.status_participantes.exists():
						membros_qs = membros_qs.filter(status_pessoa__in=ev.status_participantes.all())
					if ev.cargo_participantes.exists():
						membros_qs = membros_qs.filter(membroscargos__cargo__in=ev.cargo_participantes.all()).distinct()
				for membro in membros_qs.distinct():
					ParticipacaoEvento.objects.get_or_create(
						evento=ev,
						membro=membro,
						defaults={
							'papel': 'PARTICIPANTE',
							'status': 'PENDENTE',
						}
					)

			messages.success(request, f'{len(eventos_criados)} evento(s) criado(s) com sucesso!')
			return redirect(reverse('eventos:lista_eventos'))
	else:
		form = EventoForm()
	return render(request, 'eventos/criar_evento.html', {'form': form})
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import ParticipacaoEvento

@login_required
@require_http_methods(["GET", "POST"])
def marcar_presenca_evento(request, pk):
	evento = get_object_or_404(Evento, pk=pk)
	# Exibir apenas membros com status permitido na lista de presença (usando IDs)
	from secretaria.models import StatusPessoa
	status_nomes = ['Ativo', 'Desligado', 'Em Disciplina']
	status_ids = list(StatusPessoa.objects.filter(nome__in=status_nomes).values_list('id', flat=True))
	participacoes = ParticipacaoEvento.objects.filter(
		evento=evento,
		membro__isnull=False,
		membro__status_pessoa__in=status_ids
	).select_related('membro')
	if request.method == 'POST':
		presentes_ids = request.POST.getlist('presentes')
		for participacao in participacoes:
			justificativa_sel = request.POST.get(f'justificativa_sel_{participacao.pk}', '').strip()
			justificativa_outro = request.POST.get(f'justificativa_outro_{participacao.pk}', '').strip()
			if justificativa_sel == 'Outro' and justificativa_outro:
				justificativa = f'Outro: {justificativa_outro}'
			else:
				justificativa = justificativa_sel
			if participacao.membro and str(participacao.membro.chave) in presentes_ids:
				if participacao.status != 'PRESENTE' or participacao.justificativa_falta:
					participacao.status = 'PRESENTE'
					participacao.justificativa_falta = ''
					participacao.save(update_fields=['status', 'justificativa_falta'])
			else:
				if participacao.status != 'AUSENTE' or participacao.justificativa_falta != justificativa:
					participacao.status = 'AUSENTE'
					participacao.justificativa_falta = justificativa
					participacao.save(update_fields=['status', 'justificativa_falta'])
		messages.success(request, 'Presenças e justificativas atualizadas com sucesso!')
		return redirect(reverse('eventos:detalhe_evento', args=[evento.pk]))
	return render(request, 'eventos/marcar_presenca.html', {'evento': evento, 'participacoes': participacoes})

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .forms import EventoForm
from .models import Evento
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

@login_required
def excluir_evento_profissional(request, pk):
	evento = get_object_or_404(Evento, pk=pk)
	if request.method == 'POST':
		evento.delete()
		messages.success(request, 'Evento excluído com sucesso!')
		return redirect(reverse('eventos:lista_eventos'))
	return render(request, 'eventos/excluir_evento.html', {'evento': evento})

@login_required
def editar_evento_profissional(request, pk):
	evento = get_object_or_404(Evento, pk=pk)
	from django.utils import timezone
	if request.method == 'POST':
		import logging
		logger = logging.getLogger('django.request')
		logger.warning('DEBUG POST editar_evento_profissional: %s', dict(request.POST))

		form = EventoForm(request.POST, request.FILES, instance=evento)
		if form.is_valid():
			evento = form.save(commit=False)
			# Atualiza data_fim com hora_termino
			if evento.data_inicio and evento.quantidade_dias:
				data_fim = evento.data_inicio + timezone.timedelta(days=evento.quantidade_dias - 1)
				if evento.hora_termino:
					data_fim = data_fim.replace(hour=evento.hora_termino.hour, minute=evento.hora_termino.minute, second=0, microsecond=0)
				evento.data_fim = data_fim
			evento.save()
			form.save_m2m()

			# Lógica de recorrência: atualizar todas as ocorrências
			from .utils import gerar_datas_recorrencia
			from django.utils import timezone
			from .models import Evento as EventoModel
			datas = gerar_datas_recorrencia(evento)
			eventos_existentes = list(EventoModel.objects.filter(
				titulo=evento.titulo,
				igreja=evento.igreja,
				local=evento.local,
				responsavel=evento.responsavel,
				descricao=evento.descricao,
				tipo=evento.tipo,
			).exclude(pk=evento.pk))
			eventos_atualizados = [evento]
			for dt in datas:
				if dt == evento.data_inicio:
					ev = evento
				else:
					# Procura evento existente para esta data
					ev = next((e for e in eventos_existentes if e.data_inicio == dt), None)
					data_fim = dt + timezone.timedelta(days=evento.quantidade_dias - 1)
					if evento.hora_termino:
						data_fim = data_fim.replace(hour=evento.hora_termino.hour, minute=evento.hora_termino.minute, second=0, microsecond=0)
					if ev is None:
						ev = EventoModel(
							igreja=evento.igreja,
							titulo=evento.titulo,
							descricao=evento.descricao,
							tipo=evento.tipo,
							local=evento.local,
							responsavel=evento.responsavel,
							data_inicio=dt,
							data_fim=data_fim,
							recorrente=False,
							frequencia='nenhuma',
							intervalo=1,
							capa=evento.capa,
							criado_por=evento.criado_por,
							atualizado_em=timezone.now(),
							criado_em=timezone.now(),
							quantidade_dias=evento.quantidade_dias,
							hora_termino=evento.hora_termino,
						)
						ev.save()
						ev.tipos_participantes.set(evento.tipos_participantes.all())
						ev.status_participantes.set(evento.status_participantes.all())
						ev.cargo_participantes.set(evento.cargo_participantes.all())
						eventos_existentes.append(ev)
					else:
						ev.data_fim = data_fim
						ev.hora_termino = evento.hora_termino
						ev.save()
				eventos_atualizados.append(ev)

			# Geração automática dos participantes esperados para cada evento
			from secretaria.models import Membro, StatusPessoa
			from .models import ParticipacaoEvento
			status_nomes = ['Ativo', 'Desligado', 'Em Disciplina']
			status_ids = list(StatusPessoa.objects.filter(nome__in=status_nomes).values_list('id', flat=True))
			for ev in eventos_atualizados:
				if ev.incluir_todos_membros:
					membros_qs = Membro.objects.filter(igreja=ev.igreja, status_pessoa__in=status_ids)
				else:
					membros_qs = Membro.objects.filter(igreja=ev.igreja, status_pessoa__in=status_ids)
					if ev.tipos_participantes.exists():
						membros_qs = membros_qs.filter(tipo_pessoa__in=ev.tipos_participantes.all())
					if ev.status_participantes.exists():
						membros_qs = membros_qs.filter(status_pessoa__in=ev.status_participantes.all())
					if ev.cargo_participantes.exists():
						membros_qs = membros_qs.filter(membroscargos__cargo__in=ev.cargo_participantes.all()).distinct()
				# Remove participações de membros que não estão mais no filtro
				membros_chaves_atuais = set(membros_qs.values_list('chave', flat=True))
				ParticipacaoEvento.objects.filter(evento=ev).exclude(membro__chave__in=membros_chaves_atuais).delete()
				# Cria participações para membros do filtro
				for membro in membros_qs.distinct():
					ParticipacaoEvento.objects.get_or_create(
						evento=ev,
						membro=membro,
						defaults={
							'papel': 'PARTICIPANTE',
							'status': 'PENDENTE',
						}
					)

			messages.success(request, f'{len(eventos_atualizados)} evento(s) atualizado(s) com sucesso!')
			return redirect(reverse('eventos:detalhe_evento', args=[evento.pk]))
	else:
		form = EventoForm(instance=evento)
	return render(request, 'eventos/editar_evento.html', {'form': form, 'evento': evento})

@login_required
def lista_eventos(request):
	from django.utils import timezone
	eventos = Evento.objects.all().order_by('data_inicio')
	# Filtros
	tipo = request.GET.get('tipo')
	igreja = request.GET.get('igreja')
	data_inicio = request.GET.get('data_inicio')
	data_fim = request.GET.get('data_fim')
	mostrar_passados = request.GET.get('mostrar_passados') == 'on'
	if not mostrar_passados:
		eventos = eventos.filter(data_inicio__gte=timezone.now())
	if tipo:
		eventos = eventos.filter(tipo=tipo)
	if igreja:
		eventos = eventos.filter(igreja_id=igreja)
	if data_inicio:
		eventos = eventos.filter(data_inicio__date__gte=data_inicio)
	if data_fim:
		eventos = eventos.filter(data_inicio__date__lte=data_fim)
	from configuracao.models import Igreja
	igrejas = Igreja.objects.all().order_by('nome_igreja')
	paginator = Paginator(eventos, 20)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	today = timezone.localdate()
	return render(request, 'eventos/lista_eventos.html', {
		'page_obj': page_obj,
		'igrejas': igrejas,
		'mostrar_passados': mostrar_passados,
		'today': today,
	})

## DUPLICIDADE REMOVIDA: manter apenas uma definição de criar_evento_profissional

@login_required
def detalhe_evento_profissional(request, pk):
	evento = get_object_or_404(Evento, pk=pk)
	return render(request, 'eventos/detalhe_evento.html', {'evento': evento})
