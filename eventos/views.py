from django.http import JsonResponse, HttpResponseForbidden
from django.http import Http404
from django.db.models import Exists, OuterRef
from secretaria.models import Membro, TipoPessoa, StatusPessoa, Cargo, MembroCargo
# Endpoint AJAX para autocomplete de convidados conforme filtros
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from core.decorators import page_access_required, verificar_assinatura_valida



def _obter_sessao_evento(evento, sessao_id):
	"""Resolve a sessão selecionada para o evento, mantendo o fallback atual."""
	if not sessao_id:
		return None
	try:
		return EventoSessao.objects.get(pk=sessao_id, evento=evento)
	except EventoSessao.DoesNotExist:
		return None


def _carregar_participacoes_presenca(evento, sessao):
	"""Carrega ou cria participações elegíveis para a sessão de presença."""
	from django.db.models import Q
	from secretaria.models import StatusPessoa, Membro

	status_ids = list(
		StatusPessoa.objects.filter(
			Q(nome__iexact='Ativo') |
			Q(nome__iexact='Desligado') |
			Q(nome__iexact='Em Disciplina')
		).values_list('id', flat=True)
	)

	participacoes_base = ParticipacaoEvento.objects.filter(
		evento=evento,
		sessao=sessao
	).select_related('membro')

	if status_ids:
		participacoes = participacoes_base.filter(
			Q(membro__isnull=False, membro__status_pessoa__in=status_ids) | Q(convidado_email__isnull=False)
		)
	else:
		participacoes = participacoes_base.filter(
			Q(membro__isnull=False) | Q(convidado_email__isnull=False)
		)

	if participacoes.exists():
		return participacoes, status_ids

	membros_criterios, adicionados_manualmente = evento.get_participantes_esperados()
	created = []
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

	return participacoes, status_ids


def _extrair_presencas_submetidas(request, participacoes, evento_obj=None, sessao_obj=None):
	"""Extrai a lista de participações marcadas sem mudar a compatibilidade legada."""
	import json
	import re
	import unicodedata

	def _valor_indica_true(raw):
		if isinstance(raw, bool):
			return raw
		texto = str(raw or '').strip().lower()
		return texto in {'1', 'true', 'on', 'yes', 'sim', 'checked'}

	def _parse_pk_localizado(valor_raw):
		texto = str(valor_raw or '').strip()
		if not texto:
			return None

		try:
			return int(texto)
		except (TypeError, ValueError):
			pass

		if re.fullmatch(r'[\d\.,\s]+', texto):
			digitos = re.sub(r'\D', '', texto)
			if digitos:
				try:
					return int(digitos)
				except (TypeError, ValueError):
					return None

		return None

	def _coletar_tokens_json(node):
		tokens = []
		if isinstance(node, list):
			for item in node:
				tokens.extend(_coletar_tokens_json(item))
			return tokens

		if isinstance(node, dict):
			for k, v in node.items():
				chave = str(k or '').strip()
				if chave and _valor_indica_true(v):
					tokens.append(chave)
				tokens.extend(_coletar_tokens_json(v))
			for field in [
				'participacao_id', 'participacaoPk', 'participacao_pk',
				'pk', 'id', 'membro_id', 'membroId', 'email', 'nome', 'value'
			]:
				if field in node and node.get(field) is not None:
					tokens.append(str(node.get(field)).strip())
			return tokens

		valor = str(node or '').strip()
		return [valor] if valor else []

	valores_json_brutos = []
	valores_checkbox_brutos = []
	presentes_json = request.POST.get('presentes_json', '').strip()
	for presentes_json_raw in request.POST.getlist('presentes_json'):
		presentes_json_raw = str(presentes_json_raw or '').strip()
		if not presentes_json_raw:
			continue
		try:
			parsed = json.loads(presentes_json_raw)
			for token in _coletar_tokens_json(parsed):
				if token:
					valores_json_brutos.append(token)
		except (ValueError, TypeError, json.JSONDecodeError):
			for token in re.split(r'[;,|\s]+', presentes_json_raw):
				token = str(token or '').strip()
				if token:
					valores_json_brutos.append(token)

	presentes_map_name_pks = set()
	presentes_state_pks = set()
	for key in request.POST.keys():
		if not str(key).startswith('presentes_map_'):
			continue
		suffix = str(key).split('presentes_map_', 1)[1].strip()
		pk_normalizado = _parse_pk_localizado(suffix)
		if pk_normalizado is not None:
			presentes_map_name_pks.add(pk_normalizado)

	for key, val in request.POST.items():
		if not str(key).startswith('presenca_estado_'):
			continue
		suffix = str(key).split('presenca_estado_', 1)[1].strip()
		pk_participacao = _parse_pk_localizado(suffix)
		if pk_participacao is None:
			continue
		if str(val).strip() == '1':
			presentes_state_pks.add(pk_participacao)

	for value in request.POST.getlist('presentes'):
		valor_normalizado = str(value or '').strip()
		if valor_normalizado:
			valores_checkbox_brutos.append(valor_normalizado)

	for key, value in request.POST.items():
		key_lower = str(key or '').lower()
		if ('presen' not in key_lower) or str(key).startswith('presenca_estado_'):
			continue
		valor_normalizado = str(value or '').strip()
		if valor_normalizado:
			valores_checkbox_brutos.append(valor_normalizado)

	participacoes_lista = list(participacoes)
	participacoes_ids = {p.pk for p in participacoes_lista}
	participacoes_por_membro = {}
	participacoes_por_email = {}
	participacoes_por_nome = {}

	def _normalizar_nome(valor):
		if not valor:
			return ''
		return ''.join(
			ch for ch in unicodedata.normalize('NFKD', str(valor).strip().lower())
			if not unicodedata.combining(ch)
		)

	for p in participacoes_lista:
		if p.membro_id:
			participacoes_por_membro.setdefault(str(p.membro_id), set()).add(p.pk)
			nome_membro = _normalizar_nome(getattr(p.membro, 'nome', ''))
			if nome_membro:
				participacoes_por_nome.setdefault(nome_membro, set()).add(p.pk)
		if p.convidado_email:
			participacoes_por_email.setdefault(str(p.convidado_email).strip().lower(), set()).add(p.pk)
		nome_convidado = _normalizar_nome(getattr(p, 'convidado_nome', ''))
		if nome_convidado:
			participacoes_por_nome.setdefault(nome_convidado, set()).add(p.pk)

	def _mapear_valor_para_participacao(valor_raw):
		valor_raw = str(valor_raw or '').strip()
		if not valor_raw:
			return set()

		candidato_pk = _parse_pk_localizado(valor_raw)
		if candidato_pk is not None and candidato_pk in participacoes_ids:
			return {candidato_pk}

		if valor_raw in participacoes_por_membro:
			return set(participacoes_por_membro[valor_raw])

		match_digitos = re.search(r'(\d+)$', valor_raw)
		if match_digitos:
			candidato = int(match_digitos.group(1))
			if candidato in participacoes_ids:
				return {candidato}
			if str(candidato) in participacoes_por_membro:
				return set(participacoes_por_membro[str(candidato)])

		valor_email = valor_raw
		if valor_raw.lower().startswith('email:'):
			valor_email = valor_raw.split(':', 1)[1].strip()
		valor_email = valor_email.lower()
		if valor_email in participacoes_por_email:
			return set(participacoes_por_email[valor_email])

		nome_normalizado = _normalizar_nome(valor_raw)
		if nome_normalizado in participacoes_por_nome:
			return set(participacoes_por_nome[nome_normalizado])

		return set()

	presentes_json_pks = set()
	presentes_checkbox_pks = set()
	for valor in valores_json_brutos:
		presentes_json_pks.update(_mapear_valor_para_participacao(valor))
	for valor in valores_checkbox_brutos:
		presentes_checkbox_pks.update(_mapear_valor_para_participacao(valor))

	presentes_map_name_pks = presentes_map_name_pks.intersection(participacoes_ids)
	presentes_state_pks = presentes_state_pks.intersection(participacoes_ids)
	presentes_pks = presentes_state_pks.union(presentes_json_pks).union(presentes_checkbox_pks).union(presentes_map_name_pks)
	houve_ids_submetidos = bool(valores_json_brutos or valores_checkbox_brutos or presentes_map_name_pks or presentes_state_pks)

	import logging
	logger = logging.getLogger('eventos')
	logger.info(
		"[PRESENCA_EVENTO] evento=%s sessao=%s json_brutos=%s checkbox_brutos=%s presentes_json=%s presentes_checkbox=%s presentes_nomecampo=%s presentes_estado=%s presentes_recebidos=%s json_len=%s participacoes_carregadas=%s amostra_json=%s amostra_checkbox=%s amostra_keys=%s",
		getattr(evento_obj, 'pk', None),
		getattr(sessao_obj, 'pk', None),
		len(valores_json_brutos),
		len(valores_checkbox_brutos),
		len(presentes_json_pks),
		len(presentes_checkbox_pks),
		len(presentes_map_name_pks),
		len(presentes_state_pks),
		len(presentes_pks),
		len(presentes_json),
		len(participacoes_lista),
		valores_json_brutos[:5],
		valores_checkbox_brutos[:5],
		list(k for k in request.POST.keys() if ('presenca' in str(k).lower() or 'presente' in str(k).lower()))[:12]
	)

	return {
		'participacoes': participacoes,
		'participacoes_lista': participacoes_lista,
		'presentes_pks': presentes_pks,
		'houve_ids_submetidos': houve_ids_submetidos,
		'status_ids': None,
	}


@login_required
@require_GET
def autocomplete_convidados(request):
	try:
		import time
		start_time = time.time()
		filtro = request.GET.get('filtro')
		status = request.GET.get('status', '').split(',') if request.GET.get('status') else []
		igreja_id = request.GET.get('igreja')

		if igreja_id:
			from core.utils import validar_acesso_igreja
			from configuracao.models import Igreja
			try:
				igreja_obj = Igreja.objects.get(pk=igreja_id)
				if not validar_acesso_igreja(request.user, igreja_obj):
					return HttpResponseForbidden()
			except Igreja.DoesNotExist:
				return HttpResponseForbidden()

		membros = Membro.objects.select_related('tipo_pessoa', 'status_pessoa', 'igreja')
		if igreja_id:
			membros = membros.filter(igreja_id=igreja_id)
		elif hasattr(request, 'igreja_ativa') and request.igreja_ativa:
			membros = membros.filter(igreja=request.igreja_ativa)

		if filtro == 'membro_obreiro':
			membros = membros.filter(tipo_pessoa__nome__in=['Membro', 'Obreiro'])
		elif filtro == 'cooperadores':
			tem_cargo = MembroCargo.objects.filter(membro_id=OuterRef('pk'))
			membros = membros.annotate(tem_cargo=Exists(tem_cargo)).filter(tem_cargo=True)
		elif filtro == 'todos':
			membros = membros.exclude(tipo_pessoa__nome='Visitante')

		status_map = {
			'ativo': 'Ativo',
			'inativo': 'Inativo',
			'desligado': 'Desligado',
			'disciplina': 'Em Disciplina',
		}
		status_nomes = [status_map[s] for s in status if s in status_map]
		if status_nomes:
			membros = membros.filter(status_pessoa__nome__in=status_nomes)

		membros = membros.distinct().order_by('nome')[:500]
		pessoas = []
		for membro in membros:
			info_parts = []
			if membro.tipo_pessoa:
				info_parts.append(membro.tipo_pessoa.nome)
			if membro.status_pessoa:
				info_parts.append(membro.status_pessoa.nome)
			pessoas.append({'id': str(membro.pk), 'nome': membro.nome, 'info': ' • '.join(info_parts) if info_parts else ''})

		ids = [p['id'] for p in pessoas]
		elapsed = time.time() - start_time
		print(f"[PERFORMANCE] autocomplete_convidados: {elapsed:.2f}s - {len(pessoas)} pessoas")
		return JsonResponse({'ids': ids, 'pessoas': pessoas})
	except Exception as e:
		import logging
		logger = logging.getLogger('django.request')
		logger.error(f"Erro em autocomplete_convidados: {str(e)}", exc_info=True)
		return JsonResponse({'ids': [], 'pessoas': [], 'error': f'Erro ao carregar participantes: {str(e)}'}, status=500)


@login_required
@require_GET
def contar_participantes_criterios(request):
	"""Endpoint AJAX para contar quantas pessoas atendem os critérios selecionados."""
	try:
		tipos_ids = request.GET.getlist('tipos[]') or request.GET.getlist('tipos')
		status_ids = request.GET.getlist('status[]') or request.GET.getlist('status')
		igreja_id = request.GET.get('igreja')
		import logging
		logger = logging.getLogger('django.request')
		logger.info(f"[CONTAR_CRITERIOS] tipos_ids={tipos_ids}, status_ids={status_ids}, igreja_id={igreja_id}")
		if not igreja_id:
			return JsonResponse({'count': 0, 'descricao': 'Igreja não selecionada'})
		from configuracao.models import Igreja
		try:
			igreja = Igreja.objects.get(pk=igreja_id)
			if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
				if igreja.ministerio != request.igreja_ativa.ministerio:
					return JsonResponse({'count': 0, 'descricao': 'Acesso negado'}, status=403)
		except Igreja.DoesNotExist:
			return JsonResponse({'count': 0, 'descricao': 'Igreja não encontrada'}, status=404)

		membros = Membro.objects.filter(igreja_id=igreja_id)
		if tipos_ids:
			membros = membros.filter(tipo_pessoa_id__in=tipos_ids)
		if status_ids:
			membros = membros.filter(status_pessoa_id__in=status_ids)
		membros = membros.exclude(tipo_pessoa__nome='Visitante')
		count = membros.count()
		logger.info(f"[CONTAR_CRITERIOS] Query: {membros.query}")
		logger.info(f"[CONTAR_CRITERIOS] Count: {count}")
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
		return JsonResponse({'count': count, 'descricao': descricao, 'tipos': tipos_nomes, 'status': status_nomes, 'igreja_nome': igreja.nome_igreja})
	except Exception as e:
		import logging
		logger = logging.getLogger('django.request')
		logger.error(f"Erro em contar_participantes_criterios: {e}")
		return JsonResponse({'count': 0, 'descricao': 'Erro ao calcular', 'error': str(e)}, status=500)


@login_required
@require_GET
def listar_participantes_criterios(request):
	"""Endpoint AJAX para listar pessoas que atendem os critérios selecionados."""
	try:
		tipos_ids = request.GET.getlist('tipos[]') or request.GET.getlist('tipos')
		status_ids = request.GET.getlist('status[]') or request.GET.getlist('status')
		igreja_id = request.GET.get('igreja')
		if not igreja_id:
			return JsonResponse({'pessoas': []})
		membros = Membro.objects.filter(igreja_id=igreja_id).select_related('tipo_pessoa', 'status_pessoa')
		if tipos_ids:
			membros = membros.filter(tipo_pessoa_id__in=tipos_ids)
		if status_ids:
			membros = membros.filter(status_pessoa_id__in=status_ids)
		membros = membros.exclude(tipo_pessoa__nome='Visitante')
		membros = membros.distinct().order_by('nome')[:500]
		pessoas = []
		for membro in membros:
			info_parts = []
			if membro.tipo_pessoa:
				info_parts.append(membro.tipo_pessoa.nome)
			if membro.status_pessoa:
				info_parts.append(membro.status_pessoa.nome)
			pessoas.append({'id': str(membro.pk), 'nome': membro.nome, 'info': ' • '.join(info_parts) if info_parts else ''})
		return JsonResponse({'pessoas': pessoas})
	except Exception as e:
		import logging
		logger = logging.getLogger('django.request')
		logger.error(f"Erro em listar_participantes_criterios: {str(e)}", exc_info=True)
		return JsonResponse({'pessoas': [], 'error': str(e)}, status=500)


@login_required
@require_GET
def autocomplete_responsaveis(request):
	"""Retorna lista de responsáveis (usuários) que são membros da igreja especificada."""
	igreja_id = request.GET.get('igreja_id')
	if not igreja_id:
		return JsonResponse({'responsaveis': [], 'error': 'Parâmetro obrigatório ausente'})
	try:
		from django.contrib.auth import get_user_model
		from configuracao.models import Igreja
		User = get_user_model()
		try:
			igreja = Igreja.objects.get(pk=igreja_id)
		except Igreja.DoesNotExist:
			return JsonResponse({'responsaveis': [], 'error': 'Recurso não encontrado'})

		ministerio_usuario = None
		if hasattr(request.user, 'perfil') and hasattr(request.user.perfil, 'ministerio'):
			ministerio_usuario = request.user.perfil.ministerio

		if ministerio_usuario and igreja.ministerio != ministerio_usuario:
			return JsonResponse({'responsaveis': [], 'error': 'Acesso negado'}, status=403)

		if hasattr(request, 'igreja_ativa'):
			if request.igreja_ativa.pk != int(igreja_id):
				return JsonResponse({'responsaveis': [], 'error': 'Acesso negado'}, status=403)

		membros_da_igreja = Membro.objects.filter(igreja_id=igreja_id, usuario__isnull=False).values_list('usuario_id', flat=True)
		usuarios = User.objects.filter(id__in=membros_da_igreja)
		if ministerio_usuario:
			usuarios = usuarios.filter(perfil__ministerio=ministerio_usuario)
		usuarios = usuarios.order_by('first_name', 'last_name', 'email')
		responsaveis = []
		for user in usuarios:
			nome_completo = user.get_full_name() or user.email
			label = f"{nome_completo} ({user.email})" if user.get_full_name() else user.email
			responsaveis.append({'id': user.id, 'text': label})
		return JsonResponse({'responsaveis': responsaveis})
	except Exception as e:
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
		form = EventoForm(request.POST, request.FILES, request=request, somente_eventos_individuais=True)
		
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
		form = EventoForm(post_data, request.FILES, request=request, somente_eventos_individuais=True)
		
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

			# Novo Evento cria apenas eventos individuais (não recorrentes).
			evento.recorrente = False
			evento.frequencia = 'nenhuma'
			evento.intervalo = 1
			evento.dia_semana = ''
			evento.semana_mes = ''
			evento.mes_ano = ''
			evento.data_fim_recorrencia = None
			# Corrigir campos múltiplos para string simples (evita erro de lista serializada)
			for field in ['semana_mes', 'dia_semana', 'mes_ano']:
				val = getattr(evento, field, None)
				if isinstance(val, list):
					setattr(evento, field, ','.join(val))
			evento.criado_por = request.user
			if evento.status_operacional == 'encerrado':
				evento.encerrado_em = timezone.now()
				evento.encerrado_por = request.user
			else:
				evento.encerrado_em = None
				evento.encerrado_por = None
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
		form = EventoForm(request=request, somente_eventos_individuais=True)
		
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
	return render(request, 'eventos/criar_evento.html', {'form': form, 'igreja_nome': igreja_nome, 'modo_evento_individual': True})

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
		presentes_json_pks = set()
		presentes_checkbox_pks = set()
		presentes_map_name_pks = set()
		presentes_state_pks = set()
		valores_json_brutos = []
		valores_checkbox_brutos = []
		import json
		import re
		import unicodedata

		def _valor_indica_true(raw):
			if isinstance(raw, bool):
				return raw
			texto = str(raw or '').strip().lower()
			return texto in {'1', 'true', 'on', 'yes', 'sim', 'checked'}

		def _parse_pk_localizado(valor_raw):
			texto = str(valor_raw or '').strip()
			if not texto:
				return None

			try:
				return int(texto)
			except (TypeError, ValueError):
				pass

			# Aceita formato localizado com separadores (ex.: 11.398 -> 11398).
			if re.fullmatch(r'[\d\.,\s]+', texto):
				digitos = re.sub(r'\D', '', texto)
				if digitos:
					try:
						return int(digitos)
					except (TypeError, ValueError):
						return None

			return None

		def _coletar_tokens_json(node):
			tokens = []
			if isinstance(node, list):
				for item in node:
					tokens.extend(_coletar_tokens_json(item))
				return tokens

			if isinstance(node, dict):
				# Formato mapa: {"123": true, "124": false}
				for k, v in node.items():
					chave = str(k or '').strip()
					if chave and _valor_indica_true(v):
						tokens.append(chave)
					tokens.extend(_coletar_tokens_json(v))

				# Campos comuns em payloads de seleção.
				for field in [
					'participacao_id', 'participacaoPk', 'participacao_pk',
					'pk', 'id', 'membro_id', 'membroId', 'email', 'nome', 'value'
				]:
					if field in node and node.get(field) is not None:
						tokens.append(str(node.get(field)).strip())
				return tokens

			valor = str(node or '').strip()
			return [valor] if valor else []

		for presentes_json_raw in request.POST.getlist('presentes_json'):
			presentes_json_raw = str(presentes_json_raw or '').strip()
			if not presentes_json_raw:
				continue
			try:
				parsed = json.loads(presentes_json_raw)
				for token in _coletar_tokens_json(parsed):
					if token:
						valores_json_brutos.append(token)
			except (ValueError, TypeError, json.JSONDecodeError):
				# Payload não-JSON: tenta fallback por CSV/pipe/separadores comuns.
				for token in re.split(r'[;,|\s]+', presentes_json_raw):
					token = str(token or '').strip()
					if token:
						valores_json_brutos.append(token)

		# Formato robusto: nome do campo carrega o pk da participação.
		for key in request.POST.keys():
			if not str(key).startswith('presentes_map_'):
				continue
			suffix = str(key).split('presentes_map_', 1)[1].strip()
			pk_normalizado = _parse_pk_localizado(suffix)
			if pk_normalizado is not None:
				presentes_map_name_pks.add(pk_normalizado)

		# Formato determinístico: cada linha envia estado 1/0 por PK de participação.
		for key, val in request.POST.items():
			if not str(key).startswith('presenca_estado_'):
				continue
			suffix = str(key).split('presenca_estado_', 1)[1].strip()
			pk_participacao = _parse_pk_localizado(suffix)
			if pk_participacao is None:
				continue
			if str(val).strip() == '1':
				presentes_state_pks.add(pk_participacao)

		# Compatibilidade com payload antigo por lista "presentes".
		for value in request.POST.getlist('presentes'):
			valor_normalizado = str(value or '').strip()
			if valor_normalizado:
				valores_checkbox_brutos.append(valor_normalizado)

		# Fallback ultra-defensivo: qualquer chave de presença que carregue valor textual.
		for key, value in request.POST.items():
			key_lower = str(key or '').lower()
			if ('presen' not in key_lower) or str(key).startswith('presenca_estado_'):
				continue
			valor_normalizado = str(value or '').strip()
			if valor_normalizado:
				valores_checkbox_brutos.append(valor_normalizado)

		participacoes_lista = list(participacoes)
		participacoes_ids = {p.pk for p in participacoes_lista}
		participacoes_por_membro = {}
		participacoes_por_email = {}
		participacoes_por_nome = {}

		def _normalizar_nome(valor):
			if not valor:
				return ''
			return ''.join(
				ch for ch in unicodedata.normalize('NFKD', str(valor).strip().lower())
				if not unicodedata.combining(ch)
			)

		for p in participacoes_lista:
			if p.membro_id:
				participacoes_por_membro.setdefault(str(p.membro_id), set()).add(p.pk)
				nome_membro = _normalizar_nome(getattr(p.membro, 'nome', ''))
				if nome_membro:
					participacoes_por_nome.setdefault(nome_membro, set()).add(p.pk)
			if p.convidado_email:
				participacoes_por_email.setdefault(str(p.convidado_email).strip().lower(), set()).add(p.pk)
			nome_convidado = _normalizar_nome(getattr(p, 'convidado_nome', ''))
			if nome_convidado:
				participacoes_por_nome.setdefault(nome_convidado, set()).add(p.pk)

		def _mapear_valor_para_participacao(valor_raw):
			valor_raw = str(valor_raw or '').strip()
			if not valor_raw:
				return set()

			# 1) Valor já é PK da participação.
			candidato_pk = _parse_pk_localizado(valor_raw)
			if candidato_pk is not None and candidato_pk in participacoes_ids:
				return {candidato_pk}

			# 2) Valor é ID do membro (compatibilidade com payload legado).
			if valor_raw in participacoes_por_membro:
				return set(participacoes_por_membro[valor_raw])

			# 2.1) Valor em formatos comuns "pk:123", "id=123", etc.
			match_digitos = re.search(r'(\d+)$', valor_raw)
			if match_digitos:
				candidato = int(match_digitos.group(1))
				if candidato in participacoes_ids:
					return {candidato}
				if str(candidato) in participacoes_por_membro:
					return set(participacoes_por_membro[str(candidato)])

			# 3) Valor legado por e-mail de convidado: email:alguem@dominio.
			valor_email = valor_raw
			if valor_raw.lower().startswith('email:'):
				valor_email = valor_raw.split(':', 1)[1].strip()
			valor_email = valor_email.lower()
			if valor_email in participacoes_por_email:
				return set(participacoes_por_email[valor_email])

			# 4) Valor por nome de participante (fallback defensivo).
			nome_normalizado = _normalizar_nome(valor_raw)
			if nome_normalizado in participacoes_por_nome:
				return set(participacoes_por_nome[nome_normalizado])

			return set()

		for valor in valores_json_brutos:
			mapeados = _mapear_valor_para_participacao(valor)
			presentes_json_pks.update(mapeados)

		for valor in valores_checkbox_brutos:
			mapeados = _mapear_valor_para_participacao(valor)
			presentes_checkbox_pks.update(mapeados)

		presentes_map_name_pks = presentes_map_name_pks.intersection(participacoes_ids)
		presentes_state_pks = presentes_state_pks.intersection(participacoes_ids)
		presentes_pks = presentes_state_pks.union(presentes_json_pks).union(presentes_checkbox_pks).union(presentes_map_name_pks)
		houve_ids_submetidos = bool(valores_json_brutos or valores_checkbox_brutos or presentes_map_name_pks or presentes_state_pks)

		import logging
		logger = logging.getLogger('eventos')
		logger.info(
			"[PRESENCA_EVENTO] evento=%s sessao=%s json_brutos=%s checkbox_brutos=%s presentes_json=%s presentes_checkbox=%s presentes_nomecampo=%s presentes_estado=%s presentes_recebidos=%s json_len=%s participacoes_carregadas=%s amostra_json=%s amostra_checkbox=%s amostra_keys=%s",
			evento.pk,
			sessao.pk if sessao else None,
			len(valores_json_brutos),
			len(valores_checkbox_brutos),
			len(presentes_json_pks),
			len(presentes_checkbox_pks),
			len(presentes_map_name_pks),
			len(presentes_state_pks),
			len(presentes_pks),
			len(request.POST.get('presentes_json', '') or ''),
			participacoes.count(),
			valores_json_brutos[:5],
			valores_checkbox_brutos[:5],
			list(k for k in request.POST.keys() if ('presenca' in str(k).lower() or 'presente' in str(k).lower()))[:12]
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

		if houve_ids_submetidos and not presentes_pks:
			messages.warning(
				request,
				'Nao foi possivel mapear os participantes marcados para esta sessao. Recarregue a pagina e tente novamente.'
			)
			redirect_url = reverse('eventos:marcar_presenca', args=[evento.pk])
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
			status_operacional_anterior = evento.status_operacional
			evento = form.save(commit=False)
			# Atualiza data_fim com hora_termino
			if evento.data_inicio and evento.quantidade_dias:
				data_fim = evento.data_inicio + timezone.timedelta(days=evento.quantidade_dias - 1)
				if evento.hora_termino:
					data_fim = data_fim.replace(hour=evento.hora_termino.hour, minute=evento.hora_termino.minute, second=0, microsecond=0)
				evento.data_fim = data_fim
			if evento.status_operacional == 'encerrado' and status_operacional_anterior != 'encerrado':
				evento.encerrado_em = timezone.now()
				evento.encerrado_por = request.user
			elif evento.status_operacional != 'encerrado':
				evento.encerrado_em = None
				evento.encerrado_por = None
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
	from financeiro.models import Receitas, Despesas, FundoDepartamental
	from django.db import connection
	from django.db.utils import OperationalError, ProgrammingError
	from django.db.models import Sum, Count
	from decimal import Decimal
	# Exibe apenas eventos da igreja ativa
	eventos = Evento.objects.none()
	allowed_igrejas = get_allowed_churches_for_user(request.user)
	igreja_ativa = getattr(request, 'igreja_ativa', None)
	mostrar_coluna_igreja = allowed_igrejas.count() > 1 and not igreja_ativa
	if igreja_ativa:
		eventos = Evento.objects.filter(igreja=igreja_ativa).select_related('igreja', 'criado_por', 'programacao_padrao').prefetch_related('sessoes').order_by('data_inicio')
	# Filtros
	tipo = request.GET.get('tipo')
	origem = request.GET.get('origem')
	ordenacao = request.GET.get('ordenacao') or 'data_asc'
	periodo_filtro = request.GET.get('periodo_filtro') or '30d'
	from datetime import date, timedelta
	today = timezone.localdate()
	primeiro_dia_mes = today.replace(day=1)
	if today.month == 12:
		proximo_mes = today.replace(year=today.year+1, month=1, day=1)
	else:
		proximo_mes = today.replace(month=today.month+1, day=1)
	ultimo_dia_mes = proximo_mes - timedelta(days=1)

	data_inicio_raw = (request.GET.get('data_inicio') or '').strip()
	data_fim_raw = (request.GET.get('data_fim') or '').strip()
	if (data_inicio_raw or data_fim_raw) and 'periodo_filtro' not in request.GET:
		periodo_filtro = 'custom'

	if periodo_filtro == 'hoje':
		data_inicio = today
		data_fim = today
	elif periodo_filtro == '7d':
		data_inicio = today - timedelta(days=6)
		data_fim = today
	elif periodo_filtro == '30d':
		data_inicio = today - timedelta(days=29)
		data_fim = today
	elif periodo_filtro == 'ano_atual':
		data_inicio = today.replace(month=1, day=1)
		data_fim = today
	elif periodo_filtro == 'custom':
		data_inicio = primeiro_dia_mes
		data_fim = ultimo_dia_mes
		if data_inicio_raw:
			try:
				data_inicio = date.fromisoformat(data_inicio_raw)
			except ValueError:
				pass
		if data_fim_raw:
			try:
				data_fim = date.fromisoformat(data_fim_raw)
			except ValueError:
				pass
	else:
		periodo_filtro = '30d'
		data_inicio = primeiro_dia_mes
		data_fim = ultimo_dia_mes

	data_inicio_filtro = data_inicio.isoformat()
	data_fim_filtro = data_fim.isoformat()
	if tipo:
		eventos = eventos.filter(tipo=tipo)
	if origem == 'padrao':
		eventos = eventos.filter(programacao_padrao__isnull=False)
	elif origem == 'manual':
		eventos = eventos.filter(programacao_padrao__isnull=True)

	eventos = eventos.filter(data_inicio__date__gte=data_inicio, data_inicio__date__lte=data_fim)
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

	def _to_local(dt):
		if dt is None:
			return None
		return timezone.localtime(dt) if timezone.is_aware(dt) else dt

	if ordenacao == 'data_desc':
		eventos_list = sorted(eventos_list, key=lambda e: (_to_local(e.data_inicio), e.pk), reverse=True)
	elif ordenacao == 'dia_data':
		eventos_list = sorted(eventos_list, key=lambda e: (_to_local(e.data_inicio).weekday(), _to_local(e.data_inicio), e.pk))
	else:
		ordenacao = 'data_asc'
		eventos_list = sorted(eventos_list, key=lambda e: (_to_local(e.data_inicio), e.pk))

	# Resumo financeiro consolidado para o caixa geral de eventos no período filtrado.
	evento_ids = [evento.pk for evento in eventos_list]
	total_entradas_geral = Decimal('0.00')
	total_saidas_geral = Decimal('0.00')
	total_lancamentos_geral = 0

	def _fundo_eventos_disponivel():
		"""Compatibilidade: alguns ambientes ainda podem estar sem a estrutura de fundos."""
		try:
			if 'financeiro_fundodepartamental' not in connection.introspection.table_names():
				return False
			with connection.cursor() as cursor:
				colunas_receitas = {col.name for col in connection.introspection.get_table_description(cursor, 'financeiro_receitas')}
				colunas_despesas = {col.name for col in connection.introspection.get_table_description(cursor, 'financeiro_despesas')}
			return 'fundo_departamental_id' in colunas_receitas and 'fundo_departamental_id' in colunas_despesas
		except (OperationalError, ProgrammingError):
			return False
		except Exception:
			return False

	receitas_qs = Receitas.objects.none()
	despesas_qs = Despesas.objects.none()

	if igreja_ativa:
		receitas_qs = Receitas.objects.filter(igreja=igreja_ativa, data__gte=data_inicio, data__lte=data_fim)
		despesas_qs = Despesas.objects.filter(igreja=igreja_ativa, data__gte=data_inicio, data__lte=data_fim)
	elif allowed_igrejas.exists():
		receitas_qs = Receitas.objects.filter(igreja__in=allowed_igrejas, data__gte=data_inicio, data__lte=data_fim)
		despesas_qs = Despesas.objects.filter(igreja__in=allowed_igrejas, data__gte=data_inicio, data__lte=data_fim)

	if _fundo_eventos_disponivel():
		receitas_qs = receitas_qs.filter(fundo_departamental__codigo='EVENTOS')
		despesas_qs = despesas_qs.filter(fundo_departamental__codigo='EVENTOS')
	elif evento_ids:
		# Fallback legado: sem estrutura de fundos, usa apenas lançamentos vinculados a evento.
		receitas_qs = receitas_qs.filter(evento_id__in=evento_ids)
		despesas_qs = despesas_qs.filter(evento_id__in=evento_ids)
	else:
		receitas_qs = Receitas.objects.none()
		despesas_qs = Despesas.objects.none()

	total_entradas_geral = receitas_qs.aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
	total_saidas_geral = despesas_qs.aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
	total_receitas_geral = receitas_qs.aggregate(total=Count('id')).get('total') or 0
	total_despesas_geral = despesas_qs.aggregate(total=Count('id')).get('total') or 0
	total_lancamentos_geral = total_receitas_geral + total_despesas_geral

	painel_financeiro_eventos = {
		'total_entradas': total_entradas_geral,
		'total_saidas': total_saidas_geral,
		'saldo': total_entradas_geral - total_saidas_geral,
		'total_lancamentos': total_lancamentos_geral,
		'eventos_no_periodo': len(eventos_list),
	}

	link_doacoes_eventos = reverse('financeiro:lista_receitas')
	link_saidas_eventos = reverse('financeiro:lista_despesas')
	link_prestacao_contas_eventos = reverse('eventos:prestacao_contas_eventos')
	filtro_doacoes_params = {
		'categoria': 'doacao',
		'fechado': 'todos',
		'data_inicio': data_inicio_filtro,
		'data_fim': data_fim_filtro,
	}
	filtro_saidas_params = {
		'fechado': 'todos',
		'data_inicio': data_inicio_filtro,
		'data_fim': data_fim_filtro,
	}
	if _fundo_eventos_disponivel():
		fundo_eventos_qs = FundoDepartamental.objects.filter(codigo=FundoDepartamental.CODIGO_EVENTOS, ativo=True)
		if igreja_ativa:
			fundo_eventos = fundo_eventos_qs.filter(igreja=igreja_ativa).first()
		elif allowed_igrejas.exists():
			fundo_eventos = fundo_eventos_qs.filter(igreja__in=allowed_igrejas).first()
		else:
			fundo_eventos = None
		if fundo_eventos:
			filtro_doacoes_params['fundo_filtro'] = str(fundo_eventos.pk)
			filtro_saidas_params['fundo_filtro'] = str(fundo_eventos.pk)

	query_params_doacoes = request.GET.copy()
	for chave, valor in filtro_doacoes_params.items():
		query_params_doacoes[chave] = valor
	query_params_doacoes.pop('page', None)
	link_doacoes_eventos = f"{link_doacoes_eventos}?{query_params_doacoes.urlencode()}"

	query_params_saidas = request.GET.copy()
	for chave, valor in filtro_saidas_params.items():
		query_params_saidas[chave] = valor
	query_params_saidas.pop('page', None)
	link_saidas_eventos = f"{link_saidas_eventos}?{query_params_saidas.urlencode()}"

	query_params_prestacao = request.GET.copy()
	query_params_prestacao['periodo_filtro'] = 'custom'
	query_params_prestacao['data_inicio'] = data_inicio_filtro
	query_params_prestacao['data_fim'] = data_fim_filtro
	if _fundo_eventos_disponivel() and filtro_saidas_params.get('fundo_filtro'):
		query_params_prestacao['fundo_filtro'] = filtro_saidas_params['fundo_filtro']
	query_params_prestacao.pop('page', None)
	link_prestacao_contas_eventos = f"{link_prestacao_contas_eventos}?{query_params_prestacao.urlencode()}"

	paginator = Paginator(eventos_list, 20)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	dias_semana_abrev = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']
	query_params = request.GET.copy()
	if 'page' in query_params:
		del query_params['page']
	querystring_base = query_params.urlencode()

	for evento in page_obj.object_list:
		qtd_dias = max(1, int(getattr(evento, 'quantidade_dias', 1) or 1))
		inicio_local = _to_local(evento.data_inicio)
		evento.dia_semana_abrev = dias_semana_abrev[inicio_local.weekday()]
		evento.dia_semana_classe = 'fim-semana' if inicio_local.weekday() >= 5 else 'dia-util'
		evento.eh_hoje = inicio_local.date() == today
		sessoes_por_numero = {sessao.numero: sessao for sessao in evento.sessoes.all()}
		dias_evento = []
		for indice in range(qtd_dias):
			numero_dia = indice + 1
			sessao = sessoes_por_numero.get(numero_dia)
			inicio_dia = _to_local(sessao.data_inicio) if sessao and sessao.data_inicio else (inicio_local + timedelta(days=indice))
			dias_evento.append({
				'indice': numero_dia,
				'titulo': f'{evento.titulo} - Dia {numero_dia}',
				'inicio': inicio_dia,
				'dia_semana_abrev': dias_semana_abrev[inicio_dia.weekday()],
				'dia_semana_classe': 'fim-semana' if inicio_dia.weekday() >= 5 else 'dia-util',
				'sessao_id': sessao.pk if sessao else None,
				'eh_hoje': inicio_dia.date() == today,
			})

		evento.qtd_dias_exibicao = qtd_dias
		evento.dias_evento_exibicao = dias_evento
	today = timezone.localdate()

	return render(request, 'eventos/lista_eventos.html', {
		'page_obj': page_obj,
		'today': today,
		'mostrar_coluna_igreja': mostrar_coluna_igreja,
		'eventos_status': status_dict,
		'data_inicio': data_inicio_filtro,
		'data_fim': data_fim_filtro,
		'periodo_filtro_selecionado': periodo_filtro,
		'data_inicio_filtro': data_inicio_filtro,
		'data_fim_filtro': data_fim_filtro,
		'origem_filtro': origem or '',
		'ordenacao_filtro': ordenacao,
		'querystring_base': querystring_base,
		'painel_financeiro_eventos': painel_financeiro_eventos,
		'link_doacoes_eventos': link_doacoes_eventos,
		'link_saidas_eventos': link_saidas_eventos,
		'link_prestacao_contas_eventos': link_prestacao_contas_eventos,
	})


@page_access_required('eventos')
@verificar_assinatura_valida
def prestacao_contas_eventos(request):
	from datetime import date, datetime, timedelta
	from decimal import Decimal
	from django.db import connection, transaction
	from django.db.models import Q, Sum
	from django.db.utils import OperationalError, ProgrammingError
	from django.utils import timezone
	from configuracao.models import Igreja
	from financeiro.models import Despesas, FechamentoCaixa, FundoDepartamental, LogTransacaoFinanceira, Receitas
	from financeiro.utils import get_allowed_churches_for_user

	allowed_igrejas = get_allowed_churches_for_user(request.user)
	igreja_ativa = getattr(request, 'igreja_ativa', None)

	if igreja_ativa and allowed_igrejas.filter(pk=igreja_ativa.pk).exists():
		igrejas_escopo = Igreja.objects.filter(pk=igreja_ativa.pk)
	elif allowed_igrejas.exists():
		igrejas_escopo = allowed_igrejas
	else:
		messages.error(request, 'Você não possui igrejas permitidas para prestação de contas de eventos.')
		return redirect('eventos:lista_eventos')

	periodo_filtro = (request.GET.get('periodo_filtro') or '30d').strip()
	data_inicio_raw = (request.GET.get('data_inicio') or '').strip()
	data_fim_raw = (request.GET.get('data_fim') or '').strip()
	today = timezone.localdate()

	def _parse_date(data_str):
		if not data_str:
			return None
		try:
			return datetime.strptime(data_str, '%Y-%m-%d').date()
		except ValueError:
			return None

	data_inicio = _parse_date(data_inicio_raw)
	data_fim = _parse_date(data_fim_raw)

	if not data_inicio or not data_fim:
		if periodo_filtro == '7d':
			data_inicio = today - timedelta(days=6)
			data_fim = today
		elif periodo_filtro == '90d':
			data_inicio = today - timedelta(days=89)
			data_fim = today
		elif periodo_filtro == 'mes_atual':
			data_inicio = today.replace(day=1)
			data_fim = today
		elif periodo_filtro == 'ano_atual':
			data_inicio = date(today.year, 1, 1)
			data_fim = today
		else:
			periodo_filtro = '30d'
			data_inicio = today - timedelta(days=29)
			data_fim = today

	if data_inicio > data_fim:
		data_inicio, data_fim = data_fim, data_inicio

	def _fundo_eventos_disponivel_local():
		try:
			if 'financeiro_fundodepartamental' not in connection.introspection.table_names():
				return False
			with connection.cursor() as cursor:
				colunas_receitas = {col.name for col in connection.introspection.get_table_description(cursor, 'financeiro_receitas')}
				colunas_despesas = {col.name for col in connection.introspection.get_table_description(cursor, 'financeiro_despesas')}
			return 'fundo_departamental_id' in colunas_receitas and 'fundo_departamental_id' in colunas_despesas
		except (OperationalError, ProgrammingError):
			return False
		except Exception:
			return False

	fundos_disponivel = _fundo_eventos_disponivel_local()
	receitas_qs = Receitas.objects.filter(
		igreja__in=igrejas_escopo,
		data__gte=data_inicio,
		data__lte=data_fim,
	).select_related('igreja', 'evento', 'conta_bancaria')
	despesas_qs = Despesas.objects.filter(
		igreja__in=igrejas_escopo,
		data__gte=data_inicio,
		data__lte=data_fim,
	).select_related('igreja', 'evento', 'categoria', 'conta_bancaria')

	fundo_eventos_ids = []
	if fundos_disponivel:
		fundo_eventos_ids = list(
			FundoDepartamental.objects.filter(
				igreja__in=igrejas_escopo,
				codigo=FundoDepartamental.CODIGO_EVENTOS,
				ativo=True,
			).values_list('id', flat=True)
		)
		if fundo_eventos_ids:
			receitas_qs = receitas_qs.filter(fundo_departamental_id__in=fundo_eventos_ids)
			despesas_qs = despesas_qs.filter(fundo_departamental_id__in=fundo_eventos_ids)
		else:
			receitas_qs = receitas_qs.none()
			despesas_qs = despesas_qs.none()
	else:
		receitas_qs = receitas_qs.filter(evento__isnull=False)
		despesas_qs = despesas_qs.filter(evento__isnull=False)

	total_entradas = receitas_qs.aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
	total_saidas = despesas_qs.aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
	saldo = total_entradas - total_saidas

	if request.method == 'POST' and request.POST.get('acao') == 'fechar_periodo_eventos':
		if not igreja_ativa or not allowed_igrejas.filter(pk=igreja_ativa.pk).exists():
			messages.error(request, 'Selecione uma igreja ativa para fechar o caixa de eventos deste período.')
			return redirect(f"{reverse('eventos:prestacao_contas_eventos')}?{request.GET.urlencode()}")

		with transaction.atomic():
			receitas_fechadas = receitas_qs.filter(fechado=False).update(fechado=True)
			despesas_fechadas = despesas_qs.filter(fechado=False).update(fechado=True)

			FechamentoCaixa.objects.update_or_create(
				igreja=igreja_ativa,
				data_inicio=data_inicio,
				data_fim=data_fim,
				defaults={
					'total_entradas': total_entradas,
					'total_saidas': total_saidas,
					'saldo_final': saldo,
					'status': 'fechado',
					'observacoes': 'Fechamento do Caixa de Eventos realizado pela Prestação de Contas de Eventos.',
				},
			)

		messages.success(
			request,
			f'Prestação de contas fechada: {receitas_fechadas} entrada(s) e {despesas_fechadas} saída(s) bloqueadas para edição/exclusão.'
		)
		return redirect(f"{reverse('eventos:prestacao_contas_eventos')}?{request.GET.urlencode()}")

	movimentos = []
	for receita in receitas_qs:
		movimentos.append({
			'pk': receita.pk,
			'tipo': 'entrada',
			'data': receita.data,
			'igreja': receita.igreja,
			'evento': receita.evento,
			'categoria': receita.get_categoria_display(),
			'descricao': receita.observacao or 'Entrada de eventos',
			'conta': receita.conta_bancaria,
			'valor': receita.valor,
			'fechado': receita.fechado,
			'editar_url': reverse('financeiro:editar_receita', args=[receita.pk]),
			'excluir_url': reverse('financeiro:excluir_receita', args=[receita.pk]),
			'chave_log': ('Receitas', receita.pk),
		})

	for despesa in despesas_qs:
		movimentos.append({
			'pk': despesa.pk,
			'tipo': 'saida',
			'data': despesa.data,
			'igreja': despesa.igreja,
			'evento': despesa.evento,
			'categoria': despesa.categoria.nome if despesa.categoria else '-',
			'descricao': despesa.descricao,
			'conta': despesa.conta_bancaria,
			'valor': despesa.valor,
			'fechado': despesa.fechado,
			'editar_url': reverse('financeiro:editar_despesa', args=[despesa.pk]),
			'excluir_url': reverse('financeiro:excluir_despesa', args=[despesa.pk]),
			'chave_log': ('Despesas', despesa.pk),
		})

	movimentos.sort(key=lambda item: (item['data'], item['pk']), reverse=True)

	ids_receitas = [item['pk'] for item in movimentos if item['tipo'] == 'entrada']
	ids_despesas = [item['pk'] for item in movimentos if item['tipo'] == 'saida']
	mapa_logs = {}
	if ids_receitas or ids_despesas:
		query_logs = LogTransacaoFinanceira.objects.filter(
			igreja__in=igrejas_escopo,
		).filter(
			Q(referencia_modelo='Receitas', referencia_id__in=ids_receitas)
			| Q(referencia_modelo='Despesas', referencia_id__in=ids_despesas)
		).select_related('usuario').order_by('-criado_em')

		for log in query_logs:
			chave = (log.referencia_modelo, log.referencia_id)
			if chave not in mapa_logs:
				mapa_logs[chave] = log

	for item in movimentos:
		log = mapa_logs.get(item['chave_log'])
		item['log'] = log

	query_params_entradas = request.GET.copy()
	query_params_entradas['data_inicio'] = data_inicio.isoformat()
	query_params_entradas['data_fim'] = data_fim.isoformat()
	query_params_entradas['fechado'] = 'todos'
	if fundo_eventos_ids:
		query_params_entradas['fundo_filtro'] = str(fundo_eventos_ids[0])
	query_params_entradas.pop('page', None)
	link_entradas = f"{reverse('financeiro:lista_receitas')}?{query_params_entradas.urlencode()}"

	query_params_saidas = request.GET.copy()
	query_params_saidas['data_inicio'] = data_inicio.isoformat()
	query_params_saidas['data_fim'] = data_fim.isoformat()
	query_params_saidas['fechado'] = 'todos'
	if fundo_eventos_ids:
		query_params_saidas['fundo_filtro'] = str(fundo_eventos_ids[0])
	query_params_saidas.pop('page', None)
	link_saidas = f"{reverse('financeiro:lista_despesas')}?{query_params_saidas.urlencode()}"

	context = {
		'data_inicio': data_inicio,
		'data_fim': data_fim,
		'periodo_filtro': periodo_filtro,
		'total_entradas': total_entradas,
		'total_saidas': total_saidas,
		'saldo': saldo,
		'movimentos': movimentos,
		'quantidade_movimentos': len(movimentos),
		'link_entradas': link_entradas,
		'link_saidas': link_saidas,
		'pode_fechar_periodo': bool(igreja_ativa and allowed_igrejas.filter(pk=igreja_ativa.pk).exists()),
		'igreja_ativa': igreja_ativa,
	}
	return render(request, 'eventos/prestacao_contas_eventos.html', context)

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

	from decimal import Decimal
	from django.db.models import Sum
	from financeiro.models import Receitas, Despesas

	receitas_evento_qs = Receitas.objects.filter(evento=evento)
	despesas_evento_qs = Despesas.objects.filter(evento=evento)
	total_entradas_evento = receitas_evento_qs.aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
	total_saidas_evento = despesas_evento_qs.aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
	saldo_evento = total_entradas_evento - total_saidas_evento

	meta_arrecadacao = evento.meta_arrecadacao or Decimal('0.00')
	percentual_meta_arrecadacao = Decimal('0.00')
	if meta_arrecadacao > 0:
		percentual_meta_arrecadacao = (total_entradas_evento / meta_arrecadacao) * Decimal('100')
	percentual_meta_arrecadacao = min(percentual_meta_arrecadacao, Decimal('999.99'))

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
		'total_entradas_evento': total_entradas_evento,
		'total_saidas_evento': total_saidas_evento,
		'saldo_evento': saldo_evento,
		'quantidade_receitas_evento': receitas_evento_qs.count(),
		'quantidade_despesas_evento': despesas_evento_qs.count(),
		'percentual_meta_arrecadacao': percentual_meta_arrecadacao,
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
