from django.http import JsonResponse, HttpResponseForbidden
from django.http import Http404
from django.db.models import Exists, OuterRef
from secretaria.models import Membro, TipoPessoa, StatusPessoa, Cargo, MembroCargo
# Endpoint AJAX para autocomplete de convidados conforme filtros
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from core.decorators import page_access_required, verificar_assinatura_valida

@login_required
@require_GET
def autocomplete_convidados(request):
	try:
		import time
		start_time = time.time()
		
		filtro = request.GET.get('filtro')
		status = request.GET.get('status', '').split(',') if request.GET.get('status') else []
		igreja_id = request.GET.get('igreja')  # Parâmetro explícito de igreja
		
		# SEGURANÇA: Validar escopo de igreja se fornecido
		if igreja_id:
			from core.utils import validar_acesso_igreja
			from configuracao.models import Igreja
			try:
				igreja_obj = Igreja.objects.get(pk=igreja_id)
				if not validar_acesso_igreja(request.user, igreja_obj):
					from django.http import HttpResponseForbidden
					return HttpResponseForbidden()
			except Igreja.DoesNotExist:
				from django.http import HttpResponseForbidden
				return HttpResponseForbidden()
		
		# SEGURANÇA: Filtrar apenas membros da igreja ativa
		membros = Membro.objects.select_related('tipo_pessoa', 'status_pessoa', 'igreja')
		
		# Priorizar parâmetro explícito, depois igreja_ativa do contexto
		if igreja_id:
			membros = membros.filter(igreja_id=igreja_id)
		elif hasattr(request, 'igreja_ativa') and request.igreja_ativa:
			membros = membros.filter(igreja=request.igreja_ativa)
		
		# Filtro por tipo de pessoa
		if filtro == 'membro_obreiro':
			membros = membros.filter(tipo_pessoa__nome__in=['Membro', 'Obreiro'])
		elif filtro == 'cooperadores':
			# Filtrar membros que têm cargos (usa Exists para evitar problema com proxy model)
			tem_cargo = MembroCargo.objects.filter(membro_id=OuterRef('pk'))
			membros = membros.annotate(tem_cargo=Exists(tem_cargo)).filter(tem_cargo=True)
		elif filtro == 'todos':
			# Exclui visitantes (são recepcionados na porta do evento)
			membros = membros.exclude(tipo_pessoa__nome='Visitante')
		
		# Filtro de status
		status_map = {
			'ativo': 'Ativo',
			'inativo': 'Inativo',
			'desligado': 'Desligado',
			'disciplina': 'Em Disciplina',
		}
		status_nomes = [status_map[s] for s in status if s in status_map]
		if status_nomes:
			membros = membros.filter(status_pessoa__nome__in=status_nomes)
		
		# Limitar a 500 registros para performance
		membros = membros.distinct().order_by('nome')[:500]
		
		# Retornar IDs e informações completas para o modal
		pessoas = []
		for membro in membros:
			info_parts = []
			if membro.tipo_pessoa:
				info_parts.append(membro.tipo_pessoa.nome)
			if membro.status_pessoa:
				info_parts.append(membro.status_pessoa.nome)
			
			pessoas.append({
				'id': str(membro.pk),
				'nome': membro.nome,
				'info': ' • '.join(info_parts) if info_parts else ''
			})
		
		ids = [p['id'] for p in pessoas]
		
		elapsed = time.time() - start_time
		print(f"[PERFORMANCE] autocomplete_convidados: {elapsed:.2f}s - {len(pessoas)} pessoas")
		
		return JsonResponse({
			'ids': ids,
			'pessoas': pessoas
		})
	
	except Exception as e:
		# Log do erro para debug
		import logging
		logger = logging.getLogger('django.request')
		logger.error(f"Erro em autocomplete_convidados: {str(e)}", exc_info=True)
		
		# Retornar erro JSON ao invés de falhar
		return JsonResponse({
			'ids': [],
			'pessoas': [],
			'error': f'Erro ao carregar participantes: {str(e)}'
		}, status=500)

@login_required
@require_GET
def contar_participantes_criterios(request):
	"""
	Endpoint AJAX para contar quantas pessoas atendem os critérios selecionados.
	Usado no preview dinâmico do sistema híbrido.
	"""
	try:
		# jQuery envia arrays como 'tipos[]' e 'status[]'
		tipos_ids = request.GET.getlist('tipos[]') or request.GET.getlist('tipos')
		status_ids = request.GET.getlist('status[]') or request.GET.getlist('status')
		igreja_id = request.GET.get('igreja')
		
		# DEBUG: Log dos parâmetros recebidos
		import logging
		logger = logging.getLogger('django.request')
		logger.info(f"[CONTAR_CRITERIOS] tipos_ids={tipos_ids}, status_ids={status_ids}, igreja_id={igreja_id}")
		
		if not igreja_id:
			return JsonResponse({'count': 0, 'descricao': 'Igreja não selecionada'})
		
		# SEGURANÇA: Verificar se igreja pertence ao ministério do usuário
		from configuracao.models import Igreja
		try:
			igreja = Igreja.objects.get(pk=igreja_id)
			if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
				if igreja.ministerio != request.igreja_ativa.ministerio:
					return JsonResponse({'count': 0, 'descricao': 'Acesso negado'}, status=403)
		except Igreja.DoesNotExist:
			return JsonResponse({'count': 0, 'descricao': 'Igreja não encontrada'}, status=404)
		
		# Filtrar membros pela igreja
		membros = Membro.objects.filter(igreja_id=igreja_id)
		
		# Aplicar filtros de tipo
		if tipos_ids:
			membros = membros.filter(tipo_pessoa_id__in=tipos_ids)
		
		# Aplicar filtros de status
		if status_ids:
			membros = membros.filter(status_pessoa_id__in=status_ids)
		
		# Excluir visitantes (sempre)
		membros = membros.exclude(tipo_pessoa__nome='Visitante')
		
		count = membros.count()
		
		# DEBUG: Log da query SQL e contagem
		logger.info(f"[CONTAR_CRITERIOS] Query: {membros.query}")
		logger.info(f"[CONTAR_CRITERIOS] Count: {count}")
		
		# Gerar descrição legível
		tipos_nomes = []
		if tipos_ids:
			tipos_nomes = list(TipoPessoa.objects.filter(id__in=tipos_ids).values_list('nome', flat=True))
		
		status_nomes = []
		if status_ids:
			status_nomes = list(StatusPessoa.objects.filter(id__in=status_ids).values_list('nome', flat=True))
		
		descricao_partes = []
		if tipos_nomes:
			if len(tipos_nomes) > 3:
				descricao_partes.append(f"{len(tipos_nomes)} tipos diferentes")
			else:
				descricao_partes.append(', '.join(tipos_nomes))
		else:
			descricao_partes.append('Todos os tipos')
		
		if status_nomes:
			if len(status_nomes) > 2:
				descricao_partes.append(f"com {len(status_nomes)} status diferentes")
			else:
				descricao_partes.append(f"com status {', '.join(status_nomes)}")
		
		descricao = ' '.join(descricao_partes)
		
		logger.info(f"[CONTAR_CRITERIOS] Resultado: count={count}, descricao={descricao}, tipos={tipos_nomes}, status={status_nomes}")
		
		return JsonResponse({
			'count': count, 
			'descricao': descricao,
			'tipos': tipos_nomes,
			'status': status_nomes,
			'igreja_nome': igreja.nome_igreja
		})
	
	except Exception as e:
		import logging
		logger = logging.getLogger('django.request')
		logger.error(f"Erro em contar_participantes_criterios: {e}")
		return JsonResponse({'count': 0, 'descricao': 'Erro ao calcular', 'error': str(e)}, status=500)

@login_required
@require_GET
def listar_participantes_criterios(request):
	"""
	Endpoint AJAX para listar pessoas que atendem os critérios selecionados.
	Usado no modal de remoção do sistema híbrido.
	"""
	try:
		# jQuery envia arrays como 'tipos[]' e 'status[]'
		tipos_ids = request.GET.getlist('tipos[]') or request.GET.getlist('tipos')
		status_ids = request.GET.getlist('status[]') or request.GET.getlist('status')
		igreja_id = request.GET.get('igreja')
		
		if not igreja_id:
			return JsonResponse({'pessoas': []})
		
		# Filtrar membros pela igreja
		membros = Membro.objects.filter(igreja_id=igreja_id).select_related('tipo_pessoa', 'status_pessoa')
		
		# Aplicar filtros de tipo
		if tipos_ids:
			membros = membros.filter(tipo_pessoa_id__in=tipos_ids)
		
		# Aplicar filtros de status
		if status_ids:
			membros = membros.filter(status_pessoa_id__in=status_ids)
		
		# Excluir visitantes (sempre)
		membros = membros.exclude(tipo_pessoa__nome='Visitante')
		
		# Limitar a 500 registros
		membros = membros.distinct().order_by('nome')[:500]
		
		# Retornar informações completas
		pessoas = []
		for membro in membros:
			info_parts = []
			if membro.tipo_pessoa:
				info_parts.append(membro.tipo_pessoa.nome)
			if membro.status_pessoa:
				info_parts.append(membro.status_pessoa.nome)
			
			pessoas.append({
				'id': str(membro.pk),  # Converter para string (consistência com autocomplete_convidados)
				'nome': membro.nome,
				'info': ' • '.join(info_parts) if info_parts else ''
			})
		
		return JsonResponse({'pessoas': pessoas})
	
	except Exception as e:
		import logging
		logger = logging.getLogger('django.request')
		logger.error(f"Erro em listar_participantes_criterios: {str(e)}", exc_info=True)
		return JsonResponse({'pessoas': [], 'error': str(e)}, status=500)


@login_required
@require_GET
def autocomplete_responsaveis(request):
	"""
	Retorna lista de responsáveis (usuários) que são membros da igreja especificada.
	IMPORTANTE: Filtra apenas usuários do mesmo ministério do usuário logado.
	"""
	igreja_id = request.GET.get('igreja_id')
	
	if not igreja_id:
		return JsonResponse({'responsaveis': [], 'error': 'Parâmetro obrigatório ausente'})
	
	try:
		from django.contrib.auth import get_user_model
		from configuracao.models import Igreja
		User = get_user_model()
		
		# 1. Obter a igreja
		try:
			igreja = Igreja.objects.get(pk=igreja_id)
		except Igreja.DoesNotExist:
			return JsonResponse({'responsaveis': [], 'error': 'Recurso não encontrado'})
		
		# 2. Obter ministério do usuário logado
		ministerio_usuario = None
		if hasattr(request.user, 'perfil') and hasattr(request.user.perfil, 'ministerio'):
			ministerio_usuario = request.user.perfil.ministerio
		
		# 3. SEGURANÇA: Validar se a igreja pertence ao ministério do usuário
		if ministerio_usuario and igreja.ministerio != ministerio_usuario:
			return JsonResponse({
				'responsaveis': [], 
				'error': 'Acesso negado'
			}, status=403)
		
		# 4. SEGURANÇA: Validar se o usuário tem permissão para acessar esta igreja
		if hasattr(request, 'igreja_ativa'):
			if request.igreja_ativa.pk != int(igreja_id):
				return JsonResponse({
					'responsaveis': [],
					'error': 'Acesso negado'
				}, status=403)
		
		# 5. Buscar membros da igreja que têm usuário vinculado
		membros_da_igreja = Membro.objects.filter(
			igreja_id=igreja_id, 
			usuario__isnull=False
		).values_list('usuario_id', flat=True)
		
		# 6. Buscar usuários correspondentes
		usuarios = User.objects.filter(id__in=membros_da_igreja)
		
		# 7. Filtrar apenas usuários do mesmo ministério
		if ministerio_usuario:
			usuarios = usuarios.filter(perfil__ministerio=ministerio_usuario)
		
		usuarios = usuarios.order_by('first_name', 'last_name', 'email')
		
		# 8. Formatar resposta
		responsaveis = []
		for user in usuarios:
			nome_completo = user.get_full_name() or user.email
			label = f"{nome_completo} ({user.email})" if user.get_full_name() else user.email
			responsaveis.append({
				'id': user.id,
				'text': label
			})
		
		return JsonResponse({'responsaveis': responsaveis})
	
	except Exception as e:
		# Log do erro (se logging configurado)
		import logging
		logger = logging.getLogger('django.request')
		logger.error(f"Erro em autocomplete_responsaveis: {str(e)}", exc_info=True)
		
		return JsonResponse({'error': 'Erro interno do servidor'}, status=500)

from django.db.models import Q
import openpyxl
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from django.db.models.functions import Coalesce
from django.utils.text import slugify
# Exportação de participantes para Excel
@login_required
def exportar_participantes_excel(request, pk):
	from .models import ParticipacaoEvento, Evento
	evento = Evento.objects.get(pk=pk)
	
	# SEGURANÇA: Validar escopo da igreja do evento
	igrejas_permitidas = getattr(request, 'igrejas_permitidas', None)
	if igrejas_permitidas is None:
		from core.utils import get_allowed_churches_for_membros
		ministerio = getattr(request.user.perfil, 'ministerio', None) if hasattr(request.user, 'perfil') else None
		igrejas_permitidas = get_allowed_churches_for_membros(request.user, ministerio)
	
	if not igrejas_permitidas.filter(pk=evento.igreja.pk).exists():
		raise Http404()
	
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
import sys
@page_access_required('eventos')
def criar_evento_profissional(request):
	
	if request.method == 'POST':
		form = EventoForm(request.POST, request.FILES, request=request)
		
		# CORREÇÃO: Se não for evento recorrente, limpar campos de recorrência do POST
		post_data = request.POST.copy()  # Criar cópia mutável
		frequencia = post_data.get('frequencia', 'nenhuma')
		
		if frequencia in ['nenhuma', '', None]:
			# Remover campos que causam erro de validação quando vazios
			for field in ['dia_semana', 'semana_mes', 'mes_ano']:
				# Remover completamente o campo do POST
				while field in post_data:
					post_data.pop(field)
				# Garantir que listas também sejam removidas
				field_list = f'{field}[]'
				while field_list in post_data:
					post_data.pop(field_list)
		
		# Usar post_data ao invés de request.POST
		form = EventoForm(post_data, request.FILES, request=request)
		
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

			# SISTEMA HÍBRIDO: Processar ajustes manuais
			import json
			from .models import ParticipacaoEvento
			adicionados_json = post_data.get('adicionados_manuais', '[]')
			removidos_json = post_data.get('removidos_manuais', '[]')
			
			try:
				adicionados_ids = json.loads(adicionados_json)
				removidos_ids = json.loads(removidos_json)
			except json.JSONDecodeError:
				adicionados_ids = []
				removidos_ids = []
			
			# Aplicar ajustes para todos os eventos criados
			for ev in eventos_criados:
				# Criar participações manuais ADICIONADAS
				for membro_id in adicionados_ids:
					try:
						from secretaria.models import Membro
						membro = Membro.objects.get(pk=membro_id, igreja=ev.igreja)
						ParticipacaoEvento.objects.get_or_create(
							evento=ev,
							membro=membro,
							sessao=None,
							defaults={
								'papel': 'PARTICIPANTE',
								'status': 'PENDENTE',
								'tipo_inclusao': 'MANUAL_ADICIONADO'
							}
						)
					except Membro.DoesNotExist:
						continue
				
				# Criar participações manuais REMOVIDAS (apenas marcador)
				for membro_id in removidos_ids:
					try:
						from secretaria.models import Membro
						membro = Membro.objects.get(pk=membro_id, igreja=ev.igreja)
						ParticipacaoEvento.objects.get_or_create(
							evento=ev,
							membro=membro,
							sessao=None,
							defaults={
								'tipo_inclusao': 'MANUAL_REMOVIDO'
							}
						)
					except Membro.DoesNotExist:
						continue

			# SISTEMA HÍBRIDO: Não criamos ParticipacaoEvento automáticas aqui!
			# Os participantes são gerados dinamicamente usando evento.get_participantes_esperados()
			# baseado em tipos_participantes e status_participantes salvos acima.
			# Isso permite que a lista se atualize automaticamente quando status de pessoas mudar.

			messages.success(request, f'{len(eventos_criados)} evento(s) criado(s) com sucesso!')
			return redirect(reverse('eventos:lista_eventos'))
		else:
			# Adicionar mensagem de erro para o usuário
			messages.error(request, 'Erro ao salvar evento. Verifique os campos obrigatórios.')
			
			# Mostrar quais campos têm erro na mensagem
			campos_com_erro = ', '.join(form.errors.keys())
			if campos_com_erro:
				messages.warning(request, f'Campos com problema: {campos_com_erro}')
	
	else:
		form = EventoForm(request=request)
		
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

from django.views.decorators.http import require_http_methods
from .models import ParticipacaoEvento, EventoSessao

@page_access_required('eventos')
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
	status_ids = list(
		StatusPessoa.objects.filter(
			Q(nome__iexact='Ativo') |
			Q(nome__iexact='Desligado') |
			Q(nome__iexact='Em Disciplina')
		).values_list('id', flat=True)
	)

	# Buscar participações para a sessão selecionada; se não existirem, criar
	# participações baseadas nos membros esperados do evento.
	# Buscar participações para a sessão selecionada; incluir tanto membros
	# quanto convidados por email (convidado_email). Para membros, respeitar
	# o filtro de status; convidados por email não têm membro associado.
	participacoes_base = ParticipacaoEvento.objects.filter(
		evento=evento,
		sessao=sessao
	).select_related('membro')

	if status_ids:
		participacoes = participacoes_base.filter(
			Q(membro__isnull=False, membro__status_pessoa__in=status_ids) | Q(convidado_email__isnull=False)
		)
	else:
		# Fallback defensivo: quando o catálogo de status divergir do padrão,
		# não bloquear o registro de presença por filtro rígido.
		participacoes = participacoes_base.filter(
			Q(membro__isnull=False) | Q(convidado_email__isnull=False)
		)

	# Se não há participações para a sessão, preencha automaticamente usando sistema híbrido
	if not participacoes.exists():
		from secretaria.models import Membro
		# Usar get_participantes_esperados para lista dinâmica
		membros_criterios, adicionados_manualmente = evento.get_participantes_esperados()
		
		created = []
		# Criar participações para membros que atendem critérios
		for membro in membros_criterios.distinct():
			pe, created_flag = ParticipacaoEvento.objects.get_or_create(
				evento=evento,
				sessao=sessao,
				membro=membro,
				defaults={
					'papel': 'PARTICIPANTE',
					'status': 'PENDENTE',
					'tipo_inclusao': 'AUTOMATICA'
				}
			)
			if created_flag:
				created.append(pe)
		
		# Adicionar os que foram incluídos manualmente
		for participacao_manual in adicionados_manualmente:
			if participacao_manual.membro:
				pe, created_flag = ParticipacaoEvento.objects.get_or_create(
					evento=evento,
					sessao=sessao,
					membro=participacao_manual.membro,
					defaults={
						'papel': 'PARTICIPANTE',
						'status': 'PENDENTE',
						'tipo_inclusao': 'MANUAL_ADICIONADO'
					}
				)
				if created_flag:
					created.append(pe)
		
		participacoes_base = ParticipacaoEvento.objects.filter(evento=evento, sessao=sessao).select_related('membro')
		if status_ids:
			participacoes = participacoes_base.filter(
				Q(membro__isnull=False, membro__status_pessoa__in=status_ids) | Q(convidado_email__isnull=False)
			)
		else:
			participacoes = participacoes_base.filter(Q(membro__isnull=False) | Q(convidado_email__isnull=False))

	if request.method == 'POST':
		presentes_pks = set()
		import json
		presentes_json = request.POST.get('presentes_json', '').strip()
		if presentes_json:
			try:
				for value in json.loads(presentes_json):
					presentes_pks.add(int(value))
			except (ValueError, TypeError, json.JSONDecodeError):
				presentes_pks = set()

		# Fallback para submissão padrão de checkboxes.
		if not presentes_pks:
			for value in request.POST.getlist('presentes'):
				try:
					presentes_pks.add(int(value))
				except (TypeError, ValueError):
					continue

		import logging
		logger = logging.getLogger('django.request')
		logger.info(
			"[PRESENCA_EVENTO] evento=%s sessao=%s presentes_recebidos=%s presentes_post=%s json_len=%s participacoes_carregadas=%s",
			evento.pk,
			sessao.pk if sessao else None,
			len(presentes_pks),
			len(request.POST.getlist('presentes')),
			len(presentes_json),
			participacoes.count()
		)

		if not participacoes.exists():
			messages.warning(
				request,
				'Nenhum participante elegivel foi encontrado para registrar presença nesta sessão.'
			)
			redirect_url = reverse('eventos:detalhe_evento', args=[evento.pk])
			if sessao:
				redirect_url = f"{redirect_url}?sessao={sessao.pk}"
			return redirect(redirect_url)

		# Atualiza participações existentes (membros e convidados por email)
		for participacao in participacoes:
			justificativa_sel = request.POST.get(f'justificativa_sel_{participacao.pk}', '').strip()
			justificativa_outro = request.POST.get(f'justificativa_outro_{participacao.pk}', '').strip()
			if justificativa_sel == 'Outro' and justificativa_outro:
				justificativa = f'Outro: {justificativa_outro}'
			else:
				justificativa = justificativa_sel

			# Mapeamento por conjunto de PKs marcadas no POST.
			marcado_presente = participacao.pk in presentes_pks

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
		messages.success(request, 'Presenças e justificativas atualizadas com sucesso!')
		redirect_url = reverse('eventos:detalhe_evento', args=[evento.pk])
		if sessao:
			redirect_url = f"{redirect_url}?sessao={sessao.pk}"
		return redirect(redirect_url)

	return render(request, 'eventos/marcar_presenca.html', {'evento': evento, 'participacoes': participacoes, 'sessoes': sessoes, 'sessao': sessao})

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .forms import EventoForm
from .models import Evento
from django.core.paginator import Paginator

@page_access_required('eventos')
def excluir_evento_profissional(request, pk):
	evento = get_object_or_404(Evento, pk=pk)
	if request.method == 'POST':
		evento.delete()
		messages.success(request, 'Evento excluído com sucesso!')
		return redirect(reverse('eventos:lista_eventos'))
	return render(request, 'eventos/excluir_evento.html', {'evento': evento})

@page_access_required('eventos')
def editar_evento_profissional(request, pk):
	evento = get_object_or_404(Evento, pk=pk)
	from django.utils import timezone
	if request.method == 'POST':
		import logging
		logger = logging.getLogger('django.request')
		logger.warning('DEBUG POST editar_evento_profissional: %s', dict(request.POST))

		form = EventoForm(request.POST, request.FILES, instance=evento, request=request)
		
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

			# SISTEMA HÍBRIDO: Não criamos/removemos ParticipacaoEvento aqui!
			# Os participantes são gerados dinamicamente usando evento.get_participantes_esperados()
			# baseado em tipos_participantes e status_participantes salvos acima.
			# Participações MANUAIS (adicionadas ou removidas pelo usuário) são preservadas.

			messages.success(request, f'{len(eventos_atualizados)} evento(s) atualizado(s) com sucesso!')
			return redirect(reverse('eventos:detalhe_evento', args=[evento.pk]))
	else:
		form = EventoForm(instance=evento, request=request)
		
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
	
	return render(request, 'eventos/editar_evento.html', {'form': form, 'evento': evento})

@page_access_required('eventos')
@verificar_assinatura_valida
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
	
	# SEGURANÇA: Validar escopo da igreja do evento
	igrejas_permitidas = getattr(request, 'igrejas_permitidas', None)
	if igrejas_permitidas is None:
		from core.utils import get_allowed_churches_for_membros
		ministerio = getattr(request.user.perfil, 'ministerio', None) if hasattr(request.user, 'perfil') else None
		igrejas_permitidas = get_allowed_churches_for_membros(request.user, ministerio)
	
	if not igrejas_permitidas.filter(pk=evento.igreja.pk).exists():
		raise Http404()
	
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

	# Esperados: usar sistema híbrido
	membros_criterios, adicionados_manualmente = evento.get_participantes_esperados()
	
	# Combinar membros dos critérios + adicionados manualmente
	membros_esperados_ids = set(membros_criterios.values_list('pk', flat=True))
	for participacao_manual in adicionados_manualmente:
		if participacao_manual.membro:
			membros_esperados_ids.add(participacao_manual.membro.pk)
	
	membros_esperados = Membro.objects.filter(pk__in=membros_esperados_ids)

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
