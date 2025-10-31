from django.http import JsonResponse
from secretaria.models import Membro, TipoPessoa, StatusPessoa, Cargo
# Endpoint AJAX para autocomplete de convidados conforme filtros
from django.views.decorators.http import require_GET
@require_GET
def autocomplete_convidados(request):
	filtro = request.GET.get('filtro')
	status = request.GET.get('status', '').split(',') if request.GET.get('status') else []
	membros = Membro.objects.all()
	if filtro == 'membro_obreiro':
		membros = membros.filter(tipo_pessoa__nome__in=['Membro', 'Obreiro'])
	elif filtro == 'cooperadores':
		membros = membros.filter(membroscargos__isnull=False).distinct()
	elif filtro == 'todos':
		pass  # todos do sistema
	# Filtro de status
	status_map = {
		'ativo': 'Ativo',
		'desligado': 'Desligado',
		'disciplina': 'Em Disciplina',
	}
	status_nomes = [status_map[s] for s in status if s in status_map]
	if status_nomes:
		membros = membros.filter(status_pessoa__nome__in=status_nomes)
	membros = membros.distinct()
	ids = list(membros.values_list('pk', flat=True))
	return JsonResponse({'ids': [str(i) for i in ids]})
from django.db.models import Q
import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from django.db.models.functions import Coalesce
from django.utils.text import slugify
# Exportação de participantes para Excel
def exportar_participantes_excel(request, pk):
	from .models import ParticipacaoEvento, Evento
	evento = Evento.objects.get(pk=pk)
	# Permite exportar apenas a sessão selecionada (quando aplicável)
	sessao_id = request.GET.get('sessao')
	participacoes = ParticipacaoEvento.objects.filter(evento=evento)
	if sessao_id:
		participacoes = participacoes.filter(sessao__pk=sessao_id)

	# Ordena alfabeticamente pelo nome visível (membro.nome ou convidado_nome)
	participacoes = participacoes.select_related('membro').annotate(
		nome_ordem=Coalesce('membro__nome', 'convidado_nome')
	).order_by('nome_ordem')

	wb = openpyxl.Workbook()
	ws = wb.active
	ws.title = "Participantes"

	# Cabeçalho
	ws.append(["Nome", "Papel", "Status"])

	papel_map = {
		'PARTICIPANTE': 'Participante',
		'ORGANIZADOR': 'Organizador',
		'PALESTRANTE': 'Palestrante',
		'CONVIDADO': 'Convidado',
	}
	status_map = {
		'PENDENTE': 'Pendente',
		'CONFIRMADO': 'Confirmado',
		'RECUSADO': 'Recusado',
		'AUSENTE': 'Ausente',
		'PRESENTE': 'Presente',
	}

	for p in participacoes:
		nome = p.membro.nome if p.membro else p.convidado_nome
		papel = papel_map.get(p.papel, p.papel.title())
		status = status_map.get(p.status, p.status.title())
		ws.append([nome, papel, status])

	# Ajustar largura das colunas
	for col in ws.columns:
		max_length = 0
		col_letter = get_column_letter(col[0].column)
		for cell in col:
			try:
				if len(str(cell.value)) > max_length:
					max_length = len(str(cell.value))
			except:
				pass
		ws.column_dimensions[col_letter].width = max_length + 2

	response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	# Incluir informação da sessão no nome do arquivo quando disponível
	# Sanitiza e inclui título abreviado do evento
	titulo_slug = slugify(evento.titulo)[:40]
	if titulo_slug:
		filename = f"participantes_evento_{evento.pk}_{titulo_slug}"
	else:
		filename = f"participantes_evento_{evento.pk}"
	if sessao_id:
		try:
			sess = evento.sessoes.get(pk=sessao_id)
			filename += f"_sessao{sess.numero}_{sess.data_inicio.strftime('%Y%m%d')}"
		except Exception:
			pass
	filename += ".xlsx"
	response['Content-Disposition'] = f'attachment; filename={filename}'
	wb.save(response)
	return response
from django.contrib.auth.decorators import login_required
@login_required
def criar_evento_profissional(request):
	if request.method == 'POST':
		form = EventoForm(request.POST, request.FILES, request=request)
		if form.is_valid():
			evento = form.save(commit=False)
			# Corrigir campos múltiplos para string simples (evita erro de lista serializada)
			for field in ['semana_mes', 'dia_semana', 'mes_ano']:
				val = getattr(evento, field, None)
				if isinstance(val, list):
					setattr(evento, field, ','.join(val))
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
					# Removido: cargo_participantes não existe mais no modelo Evento
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
					# Removido: cargo_participantes não existe mais no modelo Evento
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
		form = EventoForm(request=request)
	igreja_nome = None
	igreja_obj = None
	# 1. Se houver igreja ativa, inicializa o campo e pega o nome
	if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
		igreja_obj = request.igreja_ativa
		igreja_nome = getattr(igreja_obj, 'nome_igreja', str(igreja_obj))
		# Garante que o campo igreja está inicializado corretamente
		if 'igreja' in form.fields:
			form.fields['igreja'].initial = igreja_obj.pk
			form.fields['igreja'].widget = form.fields['igreja'].widget.__class__()
			form.fields['igreja'].queryset = form.fields['igreja'].queryset.model.objects.filter(pk=igreja_obj.pk)
	# 2. Tenta pegar do perfil do usuário
	elif hasattr(request.user, 'perfil') and hasattr(request.user.perfil, 'igreja') and request.user.perfil.igreja:
		igreja_obj = request.user.perfil.igreja
		igreja_nome = getattr(igreja_obj, 'nome_igreja', str(igreja_obj))
	# 3. Fallback: pega do queryset do campo igreja no form
	if not igreja_nome and hasattr(form.fields['igreja'], 'queryset'):
		qs = form.fields['igreja'].queryset
		if qs and qs.count() == 1:
			igreja_obj = qs.first()
			igreja_nome = getattr(igreja_obj, 'nome_igreja', str(igreja_obj))
	return render(request, 'eventos/criar_evento.html', {'form': form, 'igreja_nome': igreja_nome})
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import ParticipacaoEvento, EventoSessao

@login_required
@require_http_methods(["GET", "POST"])
def marcar_presenca_evento(request, pk):
	evento = get_object_or_404(Evento, pk=pk)
	# Sessões do evento (se houver)
	sessoes = list(evento.sessoes.all().order_by('numero'))
	sessao_id = request.GET.get('sessao') or request.POST.get('sessao')
	sessao = None
	if sessao_id:
		try:
			sessao = EventoSessao.objects.get(pk=sessao_id, evento=evento)
		except EventoSessao.DoesNotExist:
			sessao = None
	if not sessao:
		sessao = sessoes[0] if sessoes else None

	# Exibir apenas membros com status permitido na lista de presença (usando IDs)
	from secretaria.models import StatusPessoa
	status_nomes = ['Ativo', 'Desligado', 'Em Disciplina']
	status_ids = list(StatusPessoa.objects.filter(nome__in=status_nomes).values_list('id', flat=True))

	# Buscar participações para a sessão selecionada; se não existirem, criar
	# participações baseadas nos membros esperados do evento.
	# Buscar participações para a sessão selecionada; incluir tanto membros
	# quanto convidados por email (convidado_email). Para membros, respeitar
	# o filtro de status; convidados por email não têm membro associado.
	participacoes = ParticipacaoEvento.objects.filter(
		evento=evento,
		sessao=sessao
	).filter(
		Q(membro__isnull=False, membro__status_pessoa__in=status_ids) | Q(convidado_email__isnull=False)
	).select_related('membro')

	# Se não há participações para a sessão, preencha automaticamente
	if not participacoes.exists():
		from secretaria.models import Membro
		membros_qs = Membro.objects.filter(igreja=evento.igreja, status_pessoa__in=status_ids)
		# Aplicar filtros de tipos/status se presentes no evento
		if evento.tipos_participantes.exists():
			membros_qs = membros_qs.filter(tipo_pessoa__in=evento.tipos_participantes.all())
		if evento.status_participantes.exists():
			membros_qs = membros_qs.filter(status_pessoa__in=evento.status_participantes.all())
		created = []
		for membro in membros_qs.distinct():
			pe, created_flag = ParticipacaoEvento.objects.get_or_create(
				evento=evento,
				sessao=sessao,
				membro=membro,
				defaults={'papel': 'PARTICIPANTE', 'status': 'PENDENTE'}
			)
			if created_flag:
				created.append(pe)
		participacoes = ParticipacaoEvento.objects.filter(evento=evento, sessao=sessao, membro__status_pessoa__in=status_ids).select_related('membro')

	if request.method == 'POST':
		presentes_ids = request.POST.getlist('presentes')
		# Normalize presentes_ids to strings
		presentes_ids = [str(p) for p in presentes_ids]

		# Atualiza participações existentes (membros e convidados por email)
		for participacao in participacoes:
			justificativa_sel = request.POST.get(f'justificativa_sel_{participacao.pk}', '').strip()
			justificativa_outro = request.POST.get(f'justificativa_outro_{participacao.pk}', '').strip()
			if justificativa_sel == 'Outro' and justificativa_outro:
				justificativa = f'Outro: {justificativa_outro}'
			else:
				justificativa = justificativa_sel

			marcado_presente = False
			# Caso seja membro, identificador esperado é a chave do membro
			if participacao.membro and str(participacao.membro.chave) in presentes_ids:
				marcado_presente = True
			# Caso seja convidado por email, a UI envia tokens como 'email:addr@ex.com'
			if not marcado_presente and participacao.convidado_email and f'email:{participacao.convidado_email}' in presentes_ids:
				marcado_presente = True

			if marcado_presente:
				if participacao.status != 'PRESENTE' or participacao.justificativa_falta:
					participacao.status = 'PRESENTE'
					participacao.justificativa_falta = ''
					participacao.save(update_fields=['status', 'justificativa_falta'])
			else:
				if participacao.status != 'AUSENTE' or participacao.justificativa_falta != justificativa:
					participacao.status = 'AUSENTE'
					participacao.justificativa_falta = justificativa
					participacao.save(update_fields=['status', 'justificativa_falta'])

		# Se houver emails marcados como presentes que não possuem participação
		# criada para esta sessão, cria-las como PRESENTE (convidado)
		emails_marcados = [p.split(':', 1)[1] for p in presentes_ids if str(p).startswith('email:')]
		for email in emails_marcados:
			exists = ParticipacaoEvento.objects.filter(evento=evento, sessao=sessao, convidado_email__iexact=email).exists()
			if not exists:
				ParticipacaoEvento.objects.create(
					evento=evento,
					sessao=sessao,
					convidado_email=email,
					papel='CONVIDADO',
					status='PRESENTE'
				)
		messages.success(request, 'Presenças e justificativas atualizadas com sucesso!')
		return redirect(reverse('eventos:detalhe_evento', args=[evento.pk]))

	return render(request, 'eventos/marcar_presenca.html', {'evento': evento, 'participacoes': participacoes, 'sessoes': sessoes, 'sessao': sessao})

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
						# Removido: cargo_participantes não existe mais no modelo Evento
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
					# Removido: cargo_participantes não existe mais no modelo Evento
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
	from configuracao.models import Igreja
	from financeiro.utils import get_allowed_churches_for_user
	# Exibe apenas eventos da igreja ativa
	eventos = Evento.objects.none()
	allowed_igrejas = get_allowed_churches_for_user(request.user)
	igreja_ativa = getattr(request, 'igreja_ativa', None)
	mostrar_coluna_igreja = allowed_igrejas.count() > 1 and not igreja_ativa
	if igreja_ativa:
		eventos = Evento.objects.filter(igreja=igreja_ativa).order_by('data_inicio')
	# Filtros
	tipo = request.GET.get('tipo')
	from datetime import date, timedelta
	today = timezone.localdate()
	primeiro_dia_mes = today.replace(day=1)
	if today.month == 12:
		proximo_mes = today.replace(year=today.year+1, month=1, day=1)
	else:
		proximo_mes = today.replace(month=today.month+1, day=1)
	ultimo_dia_mes = proximo_mes - timedelta(days=1)

	data_inicio = request.GET.get('data_inicio') or primeiro_dia_mes.strftime('%Y-%m-%d')
	data_fim = request.GET.get('data_fim') or ultimo_dia_mes.strftime('%Y-%m-%d')
	# Por padrão, mostra eventos do mês corrente
	if not request.GET.get('data_inicio') and not request.GET.get('data_fim'):
		eventos = eventos.filter(data_inicio__date__gte=primeiro_dia_mes, data_inicio__date__lte=ultimo_dia_mes)
	if tipo:
		eventos = eventos.filter(tipo=tipo)
	if data_inicio:
		eventos = eventos.filter(data_inicio__date__gte=data_inicio)
	if data_fim:
		eventos = eventos.filter(data_inicio__date__lte=data_fim)
	# Cálculo do status de presença para cada evento (antes da paginação)
	from .models import ParticipacaoEvento
	eventos_status = []
	eventos_list = list(eventos)
	for evento in eventos_list:
		total_esperados = 0
		total_lancados = 0
		if evento.incluir_todos_membros:
			total_esperados = evento.igreja.membros.count()
		else:
			total_esperados = ParticipacaoEvento.objects.filter(evento=evento).count()
		total_lancados = ParticipacaoEvento.objects.filter(evento=evento).exclude(status='PENDENTE').count()
		if total_lancados == 0:
			status = 'aguardando'
		elif total_lancados < total_esperados:
			status = 'parcial'
		else:
			status = 'finalizada'
		eventos_status.append((evento.pk, status))
	status_dict = dict(eventos_status)

	# Filtro por status de presença (antes da paginação)
	status_filtro = request.GET.get('status')
	if status_filtro is None:
		status_filtro = 'aguardando'
	if status_filtro in ['aguardando', 'parcial', 'finalizada']:
		eventos_list = [evento for evento in eventos_list if status_dict.get(evento.pk) == status_filtro]

	paginator = Paginator(eventos_list, 20)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	today = timezone.localdate()

	return render(request, 'eventos/lista_eventos.html', {
		'page_obj': page_obj,
		'today': today,
		'mostrar_coluna_igreja': mostrar_coluna_igreja,
		'eventos_status': status_dict,
		'data_inicio': data_inicio,
		'data_fim': data_fim,
	})

## DUPLICIDADE REMOVIDA: manter apenas uma definição de criar_evento_profissional

@login_required
def detalhe_evento_profissional(request, pk):
	evento = get_object_or_404(Evento, pk=pk)
	# IDs dos tipos de pessoa para "Membro" e "Congregado"
	from secretaria.models import TipoPessoa, StatusPessoa, Membro
	from .models import ParticipacaoEvento
	tipo_membro = TipoPessoa.objects.filter(nome__iexact='Membro').first()
	tipo_congregado = TipoPessoa.objects.filter(nome__iexact='Congregado').first()
	status_ativo = StatusPessoa.objects.filter(nome__iexact='Ativo').first()

	# ...
	# Sessões do evento (se houver) e seleção de sessão via GET
	sessoes = list(evento.sessoes.all().order_by('numero'))
	sessao_id = request.GET.get('sessao')
	sessao = None
	if sessao_id:
		try:
			sessao = EventoSessao.objects.get(pk=sessao_id, evento=evento)
		except EventoSessao.DoesNotExist:
			sessao = None
	if not sessao:
		sessao = sessoes[0] if sessoes else None

	# Filtros vindos do GET
	filtros_ativos = request.GET.getlist('filtro')
	if not filtros_ativos or 'todos' in filtros_ativos:
		filtros_ativos = ['todos']

	# Se houver sessões, filtra participações pela sessão selecionada; caso
	# contrário, usa as participações legado com sessao IS NULL.
	if sessao:
		participacoes = ParticipacaoEvento.objects.filter(evento=evento, sessao=sessao)
	else:
		participacoes = ParticipacaoEvento.objects.filter(evento=evento, sessao__isnull=True)
	# Filtros combinados
	if 'todos' not in filtros_ativos:
		q = None
		if 'presentes' in filtros_ativos:
			q = (q | Q(status='PRESENTE')) if q else Q(status='PRESENTE')
		if 'ausentes' in filtros_ativos:
			q = (q | Q(status='AUSENTE')) if q else Q(status='AUSENTE')
		if 'justificados' in filtros_ativos:
			q = (q | (Q(justificativa_falta__isnull=False) & ~Q(justificativa_falta='')) ) if q else (Q(justificativa_falta__isnull=False) & ~Q(justificativa_falta=''))
		if q:
			participacoes = participacoes.filter(q)

	# Esperados: membros filtrados por tipos_participantes, status_participantes, incluir_todos_membros
	membros_esperados = Membro.objects.none()
	if evento.incluir_todos_membros:
		membros_esperados = Membro.objects.filter(igreja=evento.igreja)
	else:
		tipos = evento.tipos_participantes.all()
		status = evento.status_participantes.all()
		qs = Membro.objects.filter(igreja=evento.igreja)
		if tipos.exists():
			qs = qs.filter(tipo_pessoa__in=tipos)
		if status.exists():
			qs = qs.filter(status_pessoa__in=status)
		membros_esperados = qs.distinct()

	# Agora sim, cálculos dependentes de membros_esperados
	membros_ativos = membros_esperados.filter(tipo_pessoa=tipo_membro, status_pessoa=status_ativo) if tipo_membro and status_ativo else membros_esperados.none()
	congregados_ativos = membros_esperados.filter(tipo_pessoa=tipo_congregado, status_pessoa=status_ativo) if tipo_congregado and status_ativo else membros_esperados.none()

	# Participantes presentes (membros ativos/congregados ativos)
	participantes_presentes = participacoes.filter(status='PRESENTE')
	membros_presentes = participantes_presentes.filter(membro__tipo_pessoa=tipo_membro, membro__status_pessoa=status_ativo) if tipo_membro and status_ativo else participantes_presentes.none()
	congregados_presentes = participantes_presentes.filter(membro__tipo_pessoa=tipo_congregado, membro__status_pessoa=status_ativo) if tipo_congregado and status_ativo else participantes_presentes.none()

	# % de membros ativos participantes (presentes / membros ativos esperados)
	perc_membros_ativos_participantes = (membros_presentes.count() / membros_ativos.count() * 100) if membros_ativos.count() else 0
	# % de congregados ativos participantes
	perc_congregados_ativos_participantes = (congregados_presentes.count() / congregados_ativos.count() * 100) if congregados_ativos.count() else 0
	# % dos participantes que são membros ativos
	perc_participantes_membros_ativos = (membros_presentes.count() / participantes_presentes.count() * 100) if participantes_presentes.count() else 0
	# % dos participantes que são congregados ativos
	perc_participantes_congregados_ativos = (congregados_presentes.count() / participantes_presentes.count() * 100) if participantes_presentes.count() else 0
	evento = get_object_or_404(Evento, pk=pk)

	# Ao recalcular participacoes em outra seção do código, respeitamos a
	# mesma lógica de sessao definida acima (se houver sessoes, já filtramos
	# pelo objeto sessao selecionado, caso contrário consideramos sessao NULL).
	if sessao:
		participacoes = ParticipacaoEvento.objects.filter(evento=evento, sessao=sessao)
	else:
		participacoes = ParticipacaoEvento.objects.filter(evento=evento, sessao__isnull=True)
	# Filtros combinados
	if 'todos' not in filtros_ativos:
		q = None
		if 'presentes' in filtros_ativos:
			q = (q | Q(status='PRESENTE')) if q else Q(status='PRESENTE')
		if 'ausentes' in filtros_ativos:
			q = (q | Q(status='AUSENTE')) if q else Q(status='AUSENTE')
		if 'justificados' in filtros_ativos:
			q = (q | (Q(justificativa_falta__isnull=False) & ~Q(justificativa_falta='')) ) if q else (Q(justificativa_falta__isnull=False) & ~Q(justificativa_falta=''))
		if q:
			participacoes = participacoes.filter(q)

	# Esperados: membros filtrados por tipos_participantes, status_participantes, incluir_todos_membros
	membros_esperados = Membro.objects.none()
	if evento.incluir_todos_membros:
		membros_esperados = Membro.objects.filter(igreja=evento.igreja)
	else:
		tipos = evento.tipos_participantes.all()
		status = evento.status_participantes.all()
		qs = Membro.objects.filter(igreja=evento.igreja)
		if tipos.exists():
			qs = qs.filter(tipo_pessoa__in=tipos)
		if status.exists():
			qs = qs.filter(status_pessoa__in=status)
		membros_esperados = qs.distinct()

	total_esperados = membros_esperados.count()
	# Use same session-aware filter as the visible participacoes to compute
	# totals and distributions — evita somar participações de múltiplas sessões.
	if sessao:
		qs_participacoes = ParticipacaoEvento.objects.filter(evento=evento, sessao=sessao)
	else:
		qs_participacoes = ParticipacaoEvento.objects.filter(evento=evento, sessao__isnull=True)
	total_presentes = qs_participacoes.filter(status='PRESENTE').count()
	total_ausentes = qs_participacoes.filter(status='AUSENTE').count()
	total_justificados = qs_participacoes.filter(status='AUSENTE').exclude(justificativa_falta__isnull=True).exclude(justificativa_falta='').count()

	percentual_presenca = (total_presentes / total_esperados * 100) if total_esperados else 0
	percentual_ausencia = (total_ausentes / total_esperados * 100) if total_esperados else 0
	percentual_justificados = (total_justificados / total_esperados * 100) if total_esperados else 0

	from collections import Counter
	papel_counter = Counter(qs_participacoes.values_list('papel', flat=True))
	status_counter = Counter(qs_participacoes.values_list('status', flat=True))

	estatisticas = {
		'total_esperados': total_esperados,
		'total_presentes': total_presentes,
		'total_ausentes': total_ausentes,
		'total_justificados': total_justificados,
		'percentual_presenca': percentual_presenca,
		'percentual_ausencia': percentual_ausencia,
		'percentual_justificados': percentual_justificados,
		'por_papel': dict(papel_counter),
		'por_status': dict(status_counter),
		'perc_membros_ativos_participantes': perc_membros_ativos_participantes,
		'perc_congregados_ativos_participantes': perc_congregados_ativos_participantes,
		'perc_participantes_membros_ativos': perc_participantes_membros_ativos,
		'perc_participantes_congregados_ativos': perc_participantes_congregados_ativos,
		'membros_ativos': membros_ativos.count(),
		'congregados_ativos': congregados_ativos.count(),
		'membros_presentes': membros_presentes.count(),
		'congregados_presentes': congregados_presentes.count(),
	}

	# Ordena a lista de participações alfabeticamente pelo nome exibido
	try:
		participacoes = participacoes.select_related('membro').annotate(nome_ordem=Coalesce('membro__nome', 'convidado_nome')).order_by('nome_ordem')
	except Exception:
		# Em caso de qualquer problema com a anotação (bancos antigos), apenas
		# force um select_related e deixe a ordem natural do queryset.
		participacoes = participacoes.select_related('membro')

	return render(request, 'eventos/detalhe_evento.html', {
		'evento': evento,
		'estatisticas': estatisticas,
		'participacoes': participacoes,
		'filtros_ativos': filtros_ativos,
		'sessoes': sessoes,
		'sessao': sessao,
	})
