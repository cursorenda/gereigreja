"""
secretaria/views/visitantes.py
Views de listagem, cadastro, presença e acompanhamento de visitantes.
"""
import logging
import unicodedata
import uuid

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import close_old_connections, models
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from configuracao.models import Igreja
from core.decorators import page_access_required, verificar_assinatura_valida
from core.utils import get_ministerio_or_error
from configuracao.services_assinatura import contar_pessoas_ativas, ministerio_pode_adicionar_pessoa_ativa, obter_limite_pessoas_ativas
from eventos.models import Evento
from secretaria.forms import MembroForm
from secretaria.forms_acompanhamento import AcompanhamentoVisitaForm
from secretaria.forms_presenca_visitante_evento import PresencaVisitanteEventoForm
from secretaria.models import (
    AcompanhamentoVisita, Membro, PresencaVisitanteEvento, StatusPessoa, TipoPessoa,
)
from secretaria.utils import get_allowed_churches_for_membros, is_admin_org

from secretaria.views._helpers import _membros_queryset_por_escopo

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lista de visitantes
# ---------------------------------------------------------------------------

@login_required
@verificar_assinatura_valida
@page_access_required('recepcao_visitantes')
def lista_visitantes(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    igreja_id = request.GET.get('igreja')
    visitantes = (
        _membros_queryset_por_escopo(request)
        .filter(tipo_pessoa__nome__iexact='Visitante')
        .order_by('-data_primeira_visita', 'nome', 'chave')
    )
    if query:
        visitantes = visitantes.filter(
            Q(nome__icontains=query) | Q(telefone__icontains=query) | Q(email__icontains=query)
        )
    if status:
        visitantes = visitantes.filter(status_acompanhamento=status)

    page = request.GET.get('page', 1)
    paginator = Paginator(visitantes, 20)
    try:
        visitantes_page = paginator.page(page)
    except PageNotAnInteger:
        visitantes_page = paginator.page(1)
    except EmptyPage:
        visitantes_page = paginator.page(paginator.num_pages)

    igreja_selecionada = str(igreja_id) if igreja_id else (
        str(request.igreja_ativa.pk) if hasattr(request, 'igreja_ativa') and request.igreja_ativa else '0'
    )

    if request.igreja_ativa:
        scope_label_visitantes = f"Igreja: {request.igreja_ativa.nome_igreja}"
    else:
        _igrejas_perm = getattr(request, 'igrejas_permitidas', None)
        _n_v = _igrejas_perm.count() if _igrejas_perm is not None else 0
        scope_label_visitantes = f"Consolidado ({_n_v} {'igrejas' if _n_v != 1 else 'igreja'})" if _n_v > 0 else "Consolidado"

    context = {
        'visitantes': visitantes_page,
        'query': query,
        'status': status,
        'igreja_id': igreja_id,
        'igreja_selecionada': igreja_selecionada,
        'scope_label': scope_label_visitantes,
        'titulo_pagina': 'Lista de Visitantes',
        'paginator': paginator,
        'page_obj': visitantes_page,
    }
    return render(request, 'secretaria/lista_visitantes.html', context)


# ---------------------------------------------------------------------------
# Autocomplete e busca de visitantes (AJAX)
# ---------------------------------------------------------------------------

@login_required
def buscar_visitantes(request):
    termo = request.GET.get('q', '').strip()
    try:
        logger.info('buscar_visitantes called q=%s user=%s evento=%s', termo, getattr(request, 'user', None), request.GET.get('evento'))
    except Exception as exc:
        logger.debug('Falha ao registrar log inicial de buscar_visitantes: %s', exc)

    def remover_acentos(txt):
        return unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII') if txt else ''

    visitantes = []
    evento_id = request.GET.get('evento')
    tipos_ids = []
    status_ids = []
    if evento_id:
        try:
            evento = Evento.objects.get(pk=evento_id)
            tipos_ids = list(evento.tipos_participantes.values_list('id', flat=True))
            status_ids = list(evento.status_participantes.values_list('id', flat=True))
        except Evento.DoesNotExist:
            pass
    if termo:
        termo_sem_acento = remover_acentos(termo.lower())
        membros = Membro.objects.all()
        try:
            if getattr(__import__('django.conf', fromlist=['settings']).settings, 'DEBUG', False) and request.GET.get('force_global') == '1':
                membros = Membro.objects.all()
                raise StopIteration
            ministerio = get_ministerio_or_error(request)
            allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)

            try:
                if request.GET.get('recepcao') == '1' and hasattr(request, 'igreja_ativa') and request.igreja_ativa:
                    from configuracao.models import Igreja as _Igreja
                    if getattr(allowed_churches, 'filter', None) is not None:
                        allowed_churches = allowed_churches | _Igreja.objects.filter(pk=request.igreja_ativa.pk)
                    else:
                        try:
                            if all(getattr(ig, 'pk', None) != request.igreja_ativa.pk for ig in allowed_churches):
                                allowed_churches = list(allowed_churches) + [request.igreja_ativa]
                        except Exception:
                            allowed_churches = _Igreja.objects.filter(pk=request.igreja_ativa.pk)
                    logger.debug('buscar_visitantes: recepcao fallback applied; igreja_ativa=%s', request.igreja_ativa)
            except Exception as exc:
                logger.warning('buscar_visitantes: falha no fallback de recepcao: %s', exc)

            escola_qs_kwargs = None
            if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
                try:
                    if getattr(allowed_churches, 'filter', None) and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
                        escola_qs_kwargs = {'igreja': request.igreja_ativa}
                    elif hasattr(allowed_churches, '__contains__') and request.igreja_ativa in allowed_churches:
                        escola_qs_kwargs = {'igreja': request.igreja_ativa}
                except Exception:
                    escola_qs_kwargs = None

            if escola_qs_kwargs is None:
                if getattr(allowed_churches, 'exists', None) and allowed_churches.exists():
                    escola_qs_kwargs = {'igreja__in': allowed_churches}
                elif ministerio and is_admin_org(request.user):
                    escola_qs_kwargs = {'igreja__ministerio': ministerio}
                else:
                    escola_qs_kwargs = None

            if escola_qs_kwargs is None:
                membros = Membro.objects.none()
            else:
                membros = membros.filter(**escola_qs_kwargs)
        except Exception:
            membros = Membro.objects.all()
        if tipos_ids:
            membros = membros.filter(tipo_pessoa_id__in=tipos_ids)
        if status_ids:
            membros = membros.filter(status_pessoa_id__in=status_ids)
        for v in membros:
            nome = v.nome or ''
            apelido = v.apelido or ''
            if termo_sem_acento in remover_acentos(nome.lower()) or termo_sem_acento in remover_acentos(apelido.lower()):
                visitantes.append({
                    'id': (v.chave if getattr(v, 'chave', None) not in (None, '') else v.pk),
                    'pk': v.pk,
                    'chave': getattr(v, 'chave', v.pk),
                    'nome': v.nome,
                    'apelido': v.apelido,
                })
            if len(visitantes) >= 20:
                break

    if request.GET.get('debug') == '1':
        info = {
            'query': termo,
            'evento': evento_id,
            'count': len(visitantes),
            'visitantes': visitantes,
        }
        try:
            info['allowed_churches'] = str(allowed_churches)
        except Exception:
            info['allowed_churches'] = 'n/a'
        logger.debug('buscar_visitantes debug: %s', info)
        return JsonResponse(info, safe=False)

    logger.debug('buscar_visitantes q=%s results=%s', termo, len(visitantes))
    return JsonResponse(visitantes, safe=False)


# ---------------------------------------------------------------------------
# Registrar presença de visitante em evento
# ---------------------------------------------------------------------------

@login_required
@verificar_assinatura_valida
@page_access_required('recepcao_visitantes')
def registrar_presenca_visitante_evento(request):
    busca_evento = request.GET.get('busca_evento', '').strip()
    try:
        close_old_connections()
    except Exception as exc:
        logger.warning('registrar_presenca_visitante_evento: falha em close_old_connections: %s', exc)
    hoje = timezone.localdate()
    fim = hoje + timezone.timedelta(days=7)
    eventos_do_dia = Evento.objects.none()
    try:
        ministerio = get_ministerio_or_error(request)
        allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    except Exception:
        ministerio = None
        allowed_churches = Evento.objects.none()

    filtro = request.GET.get('filtro_eventos', 'ultimos')
    try:
        ultimos_n = int(request.GET.get('ultimos_n', 3))
    except (TypeError, ValueError):
        ultimos_n = 3

    escola_qs_kwargs = None
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        try:
            if getattr(allowed_churches, 'filter', None) and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
                escola_qs_kwargs = {'igreja': request.igreja_ativa}
            elif hasattr(allowed_churches, '__contains__') and request.igreja_ativa in allowed_churches:
                escola_qs_kwargs = {'igreja': request.igreja_ativa}
        except Exception:
            escola_qs_kwargs = None

    if escola_qs_kwargs is None:
        if getattr(allowed_churches, 'exists', None) and allowed_churches.exists():
            escola_qs_kwargs = {'igreja__in': allowed_churches}
        elif ministerio and is_admin_org(request.user):
            escola_qs_kwargs = {'igreja__ministerio': ministerio}
        else:
            escola_qs_kwargs = None

    if escola_qs_kwargs is None:
        eventos_do_dia = Evento.objects.none()
    else:
        if filtro == 'ultimos':
            qs = Evento.objects.filter(**escola_qs_kwargs, data_inicio__date__lte=hoje)
            if busca_evento:
                qs = qs.filter(titulo__icontains=busca_evento)
            qs = qs.order_by('-data_inicio')[:ultimos_n]
            eventos_do_dia = sorted(list(qs), key=lambda e: e.data_inicio)
        elif filtro == 'sem_visitantes':
            qs = Evento.objects.annotate(presencas_count=Count('visitantes_presentes')).filter(
                **escola_qs_kwargs,
                presencas_count=0,
                data_inicio__date__lte=hoje,
            )
            if busca_evento:
                qs = qs.filter(titulo__icontains=busca_evento)
            eventos_do_dia = qs.order_by('data_inicio')
        else:
            qs = Evento.objects.filter(
                **escola_qs_kwargs,
                data_inicio__date__gte=hoje,
                data_inicio__date__lte=fim,
            )
            if busca_evento:
                qs = qs.filter(titulo__icontains=busca_evento)
            eventos_do_dia = qs.order_by('data_inicio')

    evento_id = request.GET.get('evento')
    evento_selecionado = None
    pessoas_presentes = []
    if evento_id:
        try:
            evento_selecionado = Evento.objects.get(pk=evento_id)
            pessoas_presentes = PresencaVisitanteEvento.objects.filter(evento=evento_selecionado).select_related('membro').order_by('-data_registro')
        except Evento.DoesNotExist:
            evento_selecionado = None
            pessoas_presentes = []
            messages.error(request, 'Evento selecionado não encontrado.')
        except Exception as e:
            logger.exception('Erro ao carregar evento selecionado: %s', e)
            evento_selecionado = None
            pessoas_presentes = []
            messages.error(request, 'Erro ao carregar o evento selecionado. Verifique os logs.')

    if request.method == 'POST':
        try:
            trace_id = uuid.uuid4().hex[:8]
        except Exception:
            trace_id = 'na'
        try:
            logger.info('registrar_presenca_visitante_evento called trace=%s user=%s POST_keys=%s', trace_id, request.user, list(request.POST.keys()))
        except Exception:
            logger.info('registrar_presenca_visitante_evento called (could not format log)')

        form = PresencaVisitanteEventoForm(request.POST, request=request)
        if form.is_valid():
            membro = form.cleaned_data['membro']
            evento = form.cleaned_data['evento']
            if PresencaVisitanteEvento.objects.filter(membro=membro, evento=evento).exists():
                messages.warning(request, f'A pessoa "{membro.nome}" já está registrada neste evento!')
            else:
                presenca = form.save(commit=False)
                presenca.responsavel_registro = request.user
                presenca.save()
                try:
                    logger.info('Presença salva: trace=%s presenca_pk=%s membro_chave=%s evento_id=%s', trace_id, presenca.pk, getattr(membro, 'chave', membro.pk), getattr(evento, 'pk', None))
                except Exception:
                    logger.info('Presença salva (could not format ids)')
                _sync_participacao_evento(request, evento, membro)
                messages.success(request, f'Presença de "{presenca.membro.nome}" registrada no evento!')
            try:
                return redirect(request.path + f'?evento={evento.id}')
            except Exception:
                return redirect('secretaria:registrar_presenca_visitante_evento')
        else:
            try:
                logger.warning('presenca form invalid: errors=%s; POST keys=%s', dict(form.errors), list(request.POST.keys()))
            except Exception:
                logger.warning('presenca form invalid; POST keys=%s', list(request.POST.keys()))
            messages.error(request, 'Erro ao registrar presença: verifique se a pessoa e o evento foram selecionados corretamente.')
    else:
        form = PresencaVisitanteEventoForm(request=request)
        if evento_selecionado:
            form.fields['evento'].initial = evento_selecionado.id

    context = {
        'form': form,
        'eventos_do_dia': eventos_do_dia,
        'evento_selecionado': evento_selecionado,
        'visitantes_presentes': pessoas_presentes,
        'titulo_pagina': 'Registrar Presença no Evento',
        'filtro_eventos': filtro,
        'ultimos_n': ultimos_n,
    }
    return render(request, 'secretaria/registrar_presenca_visitante_evento.html', context)


# ---------------------------------------------------------------------------
# AJAX: registrar presença
# ---------------------------------------------------------------------------

@login_required
@require_POST
def ajax_registrar_presenca_evento(request):
    """Endpoint AJAX para registrar presença e retornar JSON."""
    try:
        try:
            close_old_connections()
        except Exception as exc:
            logger.warning('ajax_registrar_presenca_evento: falha em close_old_connections: %s', exc)
        try:
            trace_id = uuid.uuid4().hex[:8]
        except Exception:
            trace_id = 'na'
        try:
            logger.info('ajax_registrar_presenca_evento called trace=%s user=%s POST_keys=%s', trace_id, request.user, list(request.POST.keys()))
        except Exception as exc:
            logger.debug('ajax_registrar_presenca_evento: falha em log de entrada: %s', exc)

        evento_id = request.POST.get('evento') or request.POST.get('evento_id')
        membro_id = request.POST.get('membro') or request.POST.get('membro_id')
        if not evento_id or not membro_id:
            return JsonResponse({'error': 'Evento ou membro não informado.', 'trace_id': trace_id}, status=400)

        try:
            evento = Evento.objects.get(pk=evento_id)
        except Evento.DoesNotExist:
            return JsonResponse({'error': 'Evento não encontrado.', 'trace_id': trace_id}, status=404)

        membro = None
        try:
            membro_numeric = None
            try:
                membro_numeric = int(membro_id)
            except Exception:
                membro_numeric = None
            if membro_numeric is not None:
                membro = Membro.objects.filter(models.Q(pk=membro_numeric) | models.Q(chave=membro_numeric)).first()
            if not membro:
                membro = Membro.objects.filter(models.Q(pk=membro_id) | models.Q(chave=membro_id)).first()
        except Exception as e:
            logger.exception('Erro buscando membro para registrar presença: %s', e)
            membro = None

        if not membro:
            return JsonResponse({'error': f'Membro não encontrado (valor enviado: {membro_id}).', 'trace_id': trace_id}, status=404)

        if PresencaVisitanteEvento.objects.filter(membro=membro, evento=evento).exists():
            return JsonResponse({'exists': True, 'message': 'Presença já registrada.', 'trace_id': trace_id})

        presenca = PresencaVisitanteEvento(evento=evento, membro=membro, responsavel_registro=request.user)
        presenca.save()
        try:
            logger.info('Presença salva via AJAX: trace=%s presenca_pk=%s membro_chave=%s evento_id=%s', trace_id, presenca.pk, getattr(membro, 'chave', membro.pk), getattr(evento, 'pk', None))
        except Exception:
            logger.info('Presença salva via AJAX (could not format identifiers)')

        _sync_participacao_evento(request, evento, membro)

        hora = presenca.data_registro.strftime('%H:%M') if presenca.data_registro else ''
        presenca_data = {'id': presenca.pk, 'nome': membro.nome, 'apelido': getattr(membro, 'apelido', '') or '', 'hora': hora}
        try:
            presenca_html = render_to_string('secretaria/partials/_presenca_list_item.html', {
                'presenca_id': presenca.pk,
                'presenca_nome': membro.nome,
                'presenca_apelido': getattr(membro, 'apelido', '') or '',
                'presenca_hora': hora,
            }, request=request)
        except Exception as e:
            logger.exception('Erro renderizando presenca item: %s', e)
            presenca_html = ''
        return JsonResponse({'presenca': presenca_data, 'presenca_html': presenca_html, 'trace_id': trace_id})
    except Exception as e:
        logger.exception('Erro ajax_registrar_presenca_evento: %s', e)
        try:
            return JsonResponse({'error': str(e), 'trace_id': trace_id}, status=500)
        except Exception:
            return JsonResponse({'error': 'Erro interno', 'trace_id': 'na'}, status=500)


@login_required
@require_GET
def ajax_get_presencas_evento(request):
    """Retorna fragmento HTML com as presenças do evento."""
    try:
        close_old_connections()
    except Exception as exc:
        logger.warning('ajax_get_presencas_evento: falha em close_old_connections: %s', exc)
    evento_id = request.GET.get('evento')
    if not evento_id:
        return JsonResponse({'error': 'evento não informado.'}, status=400)
    try:
        evento = Evento.objects.get(pk=evento_id)
    except Evento.DoesNotExist:
        return JsonResponse({'error': 'evento não encontrado.'}, status=404)
    presencas = PresencaVisitanteEvento.objects.filter(evento=evento).select_related('membro').order_by('-data_registro')
    try:
        html = render_to_string('secretaria/partials/_presencas_list.html', {'presencas': presencas}, request=request)
    except Exception as e:
        logger.exception('Erro renderizando partial de presenças: %s', e)
        return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'html': html})


# ---------------------------------------------------------------------------
# Cadastrar visitante (completo)
# ---------------------------------------------------------------------------

@login_required
@page_access_required('recepcao_visitantes')
def cadastrar_visitante(request):
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    igreja_inicial_para_form = None
    try:
        tipo_visitante = TipoPessoa.objects.get(nome__iexact='Visitante')
    except TipoPessoa.DoesNotExist:
        messages.error(request, "Tipo de pessoa 'Visitante' não encontrado. Cadastre o tipo primeiro.")
        return redirect('secretaria:lista_visitantes')

    if not is_admin_org(request.user) and not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar visitantes ou não está associado a nenhuma igreja específica.")
        return redirect('secretaria:lista_visitantes')

    if request.method == 'POST':
        form = MembroForm(
            request.POST, request.FILES,
            ministerio=ministerio,
            user=request.user,
            allowed_churches=allowed_churches,
            igreja_inicial=request.igreja_ativa,
        )
        if form.is_valid():
            try:
                visitante = form.save(commit=False)
                visitante.tipo_pessoa = tipo_visitante
                try:
                    status_ativo = StatusPessoa.objects.get(nome__iexact='Ativo')
                    if not ministerio_pode_adicionar_pessoa_ativa(ministerio):
                        limite = obter_limite_pessoas_ativas(ministerio)
                        total_ativos = contar_pessoas_ativas(ministerio)
                        messages.error(request, f'Limite de pessoas ativas do plano atingido ({total_ativos}/{limite}). Faça upgrade para cadastrar mais pessoas ativas.')
                        return redirect('secretaria:lista_visitantes')
                    visitante.status_pessoa = status_ativo
                except StatusPessoa.DoesNotExist:
                    messages.error(request, "Status 'Ativo' não encontrado. Cadastre o status primeiro.")
                    return redirect('secretaria:lista_visitantes')
                if not is_admin_org(request.user) and not allowed_churches.filter(pk=visitante.igreja_id).exists():
                    messages.error(request, "Erro: Igreja selecionada inválida para sua permissão.")
                else:
                    visitante.save(user=request.user)
                    messages.success(request, f"Visitante '{visitante.nome}' cadastrado com sucesso.")
                    if request.GET.get('opener') == 'recepcao':
                        import json
                        created_visitante = {
                            'id': visitante.pk,
                            'chave': getattr(visitante, 'chave', visitante.pk),
                            'nome': visitante.nome,
                            'apelido': visitante.apelido,
                        }
                        context = {
                            'form': form,
                            'ministerio': ministerio,
                            'titulo_pagina': 'Cadastrar Novo Visitante',
                            'created_visitante_json': json.dumps(created_visitante),
                        }
                        return render(request, 'secretaria/criar_visitante.html', context)
                    return redirect('secretaria:lista_visitantes')
            except Exception as e:
                logger.exception(f"Erro ao salvar novo visitante para ministério {ministerio.id}")
                messages.error(request, f"Ocorreu um erro ao salvar o visitante: {e}")
        else:
            messages.error(request, "Erro ao cadastrar visitante. Verifique os campos.")
    else:
        if request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
            igreja_inicial_para_form = request.igreja_ativa
        elif allowed_churches.count() == 1:
            igreja_inicial_para_form = allowed_churches.first()
        form = MembroForm(
            ministerio=ministerio,
            user=request.user,
            allowed_churches=allowed_churches,
            igreja_inicial=igreja_inicial_para_form,
        )
        form.fields['tipo_pessoa'].initial = tipo_visitante.pk
        form.fields['tipo_pessoa'].widget = forms.HiddenInput()

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Cadastrar Novo Visitante',
    }
    return render(request, 'secretaria/criar_visitante.html', context)


# ---------------------------------------------------------------------------
# Criar visitante parcial (modal / AJAX)
# ---------------------------------------------------------------------------

@login_required
def criar_visitante_parcial(request):
    """Retorna o formulário parcial do visitante para uso em modal (GET) ou cria via AJAX (POST→JSON)."""
    try:
        close_old_connections()
    except Exception as exc:
        logger.warning('criar_visitante_parcial: falha em close_old_connections: %s', exc)
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)

    if request.method == 'POST':
        is_ajax = bool(request.headers.get('x-requested-with') == 'XMLHttpRequest')
        logger.debug('criar_visitante_parcial called via POST; is_ajax=%s; POST keys=%s', is_ajax, list(request.POST.keys()))

        try:
            tipo_visitante = TipoPessoa.objects.get(nome__iexact='Visitante')
        except TipoPessoa.DoesNotExist:
            return JsonResponse({'error': "Tipo 'Visitante' não encontrado."}, status=400)

        try:
            default_status = StatusPessoa.objects.filter(nome__iexact='Ativo').first() or StatusPessoa.objects.first()
        except Exception as exc:
            logger.warning('criar_visitante_parcial: falha ao buscar status padrão: %s', exc)
            default_status = None

        data = request.POST.copy()
        data['tipo_pessoa'] = str(tipo_visitante.pk)
        if default_status:
            data['status_pessoa'] = str(default_status.pk)
        try:
            if not data.get('igreja') or str(data.get('igreja')).strip() == '':
                data['igreja'] = str(request.igreja_ativa.pk) if hasattr(request, 'igreja_ativa') and request.igreja_ativa else ''
        except Exception as exc:
            logger.warning('criar_visitante_parcial: falha ao injetar igreja ativa no payload: %s', exc)

        try:
            if not data.get('genero'):
                data['genero'] = 'M'
            if not data.get('estado_civil'):
                data['estado_civil'] = 'Solteiro'
            if not data.get('escolaridade'):
                data['escolaridade'] = 'Sem Escolaridade'
        except Exception as exc:
            logger.warning('criar_visitante_parcial: falha ao injetar defaults de campos obrigatórios: %s', exc)

        try:
            form = MembroForm(
                data, request.FILES,
                ministerio=ministerio,
                user=request.user,
                allowed_churches=allowed_churches,
                igreja_inicial=request.igreja_ativa,
            )
        except Exception as e:
            try:
                payload = {k: request.POST.getlist(k) for k in request.POST.keys()}
                SENSITIVE_KEYS = {'senha', 'password', 'ssn', 'cpf', 'rg'}
                def _sanitize(v):
                    try:
                        return [str(x)[:200] for x in v] if isinstance(v, list) else str(v)[:200]
                    except Exception:
                        return '[unserializable]'
                sanitized = {k: _sanitize(v) for k, v in payload.items() if k.lower() not in SENSITIVE_KEYS}
                logger.debug('visitante create - form_init_error - user=%s exception=%s post=%s', request.user, e, sanitized)
            except Exception:
                logger.debug('visitante create - failed to log form_init_error', exc_info=True)
            logger.exception('Erro ao instanciar MembroForm na criar_visitante_parcial: %s', e)
            return JsonResponse({'error': 'Erro interno ao preparar o formulário. Verifique os logs.'}, status=500)

        if form.is_valid():
            visitante = form.save(commit=False)
            visitante.tipo_pessoa = tipo_visitante
            if default_status and not visitante.status_pessoa:
                if not ministerio_pode_adicionar_pessoa_ativa(ministerio):
                    limite = obter_limite_pessoas_ativas(ministerio)
                    total_ativos = contar_pessoas_ativas(ministerio)
                    return JsonResponse({
                        'error': f'Limite de pessoas ativas do plano atingido ({total_ativos}/{limite}). Faça upgrade para cadastrar mais pessoas ativas.'
                    }, status=400)
                visitante.status_pessoa = default_status
            try:
                visitante.save(user=request.user)
            except Exception as e:
                logger.exception('Erro ao salvar visitante via AJAX: %s', e)

            persisted = False
            try:
                persisted = Membro.objects.filter(pk=visitante.pk).exists()
            except Exception as e:
                logger.exception('Erro verificando persistência do visitante: %s', e)
            logger.info('Visitante criado via AJAX: %s (id=%s) persisted=%s', visitante.nome, visitante.pk, persisted)

            created = {
                'id': visitante.pk,
                'chave': getattr(visitante, 'chave', visitante.pk),
                'id_str': str(getattr(visitante, 'pk', '')),
                'chave_str': str(getattr(visitante, 'chave', getattr(visitante, 'pk', ''))),
                'nome': visitante.nome,
                'apelido': visitante.apelido or '',
            }

            # Auto-registro de presença
            auto_submit_flag = (data.get('auto_submit_presenca') or request.POST.get('auto_submit_presenca') or request.GET.get('auto_submit_presenca'))
            evento_id_for_auto = (data.get('evento') or request.POST.get('evento') or request.GET.get('evento'))
            presenca_payload = None
            presenca_html = ''
            if auto_submit_flag and evento_id_for_auto:
                try:
                    from eventos.models import ParticipacaoEvento, EventoSessao
                    from django.utils import timezone as _tz
                    evento_obj = Evento.objects.get(pk=evento_id_for_auto)
                    presenca_obj = PresencaVisitanteEvento(evento=evento_obj, membro=visitante, responsavel_registro=request.user)
                    presenca_obj.save()
                    sessao_id = None
                    try:
                        sessao_val = data.get('sessao') or request.POST.get('sessao') or request.GET.get('sessao')
                        sessao_id = int(sessao_val) if sessao_val else None
                    except Exception:
                        sessao_id = None
                    _sync_participacao_evento(request, evento_obj, visitante, sessao_id=sessao_id)
                    hora = presenca_obj.data_registro.strftime('%H:%M') if getattr(presenca_obj, 'data_registro', None) else ''
                    presenca_payload = {
                        'id': presenca_obj.pk,
                        'nome': visitante.nome,
                        'apelido': getattr(visitante, 'apelido', '') or '',
                        'hora': hora,
                    }
                    try:
                        presenca_html = render_to_string('secretaria/partials/_presenca_list_item.html', {
                            'presenca_id': presenca_obj.pk,
                            'presenca_nome': visitante.nome,
                            'presenca_apelido': getattr(visitante, 'apelido', '') or '',
                            'presenca_hora': hora,
                        }, request=request)
                    except Exception:
                        presenca_html = ''
                except Exception:
                    logger.exception('Erro criando presença automaticamente após criar visitante via AJAX')

            resp = {'visitante': created, 'saved': True, 'found_in_db': bool(persisted)}
            if presenca_payload:
                resp.update({'presenca': presenca_payload, 'presenca_html': presenca_html})
            return JsonResponse(resp)
        else:
            errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
            try:
                errors_html = render_to_string('secretaria/partials/_visitante_form.html', {'form': form, 'ministerio': ministerio}, request=request)
            except Exception:
                errors_html = ''
            try:
                logger.warning('Form inválido ao criar visitante via AJAX: %s; POST keys: %s', errors, list(request.POST.keys()))
            except Exception:
                logger.warning('Form inválido ao criar visitante via AJAX: %s', errors)
            return JsonResponse({'errors': errors, 'errors_html': errors_html}, status=400)

    # GET → render partial
    try:
        igreja_inicial_for_form = (
            request.igreja_ativa if hasattr(request, 'igreja_ativa') and request.igreja_ativa
            else (allowed_churches.first() if allowed_churches and getattr(allowed_churches, 'exists', None) and allowed_churches.exists() else None)
        )
    except Exception:
        igreja_inicial_for_form = None

    q = request.GET.get('q')
    form_init_kwargs = {
        'ministerio': ministerio,
        'user': request.user,
        'allowed_churches': allowed_churches,
        'igreja_inicial': igreja_inicial_for_form,
    }
    if q:
        form_init_kwargs['initial'] = {'nome': q}
    try:
        form = MembroForm(**form_init_kwargs)
    except Exception as e:
        logger.exception('Erro ao instanciar MembroForm (GET) na criar_visitante_parcial: %s', e)
        try:
            form = MembroForm(ministerio=ministerio, user=request.user, allowed_churches=allowed_churches, igreja_inicial=igreja_inicial_for_form)
        except Exception:
            try:
                form = MembroForm(ministerio=ministerio, user=request.user, allowed_churches=allowed_churches)
            except Exception:
                form = MembroForm()

    if q:
        try:
            form.initial['nome'] = q
            if 'nome' in form.fields:
                form.fields['nome'].initial = q
        except Exception as exc:
            logger.warning('criar_visitante_parcial: falha ao preencher nome inicial: %s', exc)

    try:
        tipo_visitante = TipoPessoa.objects.get(nome__iexact='Visitante')
    except TipoPessoa.DoesNotExist:
        tipo_visitante = None
    try:
        default_status = StatusPessoa.objects.filter(nome__iexact='Ativo').first() or StatusPessoa.objects.first()
    except Exception as exc:
        logger.warning('criar_visitante_parcial: falha ao buscar status padrão (GET): %s', exc)
        default_status = None

    try:
        if hasattr(request, 'igreja_ativa') and request.igreja_ativa and 'igreja' in form.fields:
            igreja_field_qs = form.fields['igreja'].queryset
            try:
                if not igreja_field_qs.filter(pk=request.igreja_ativa.pk).exists():
                    form.fields['igreja'].queryset = Igreja.objects.filter(pk=request.igreja_ativa.pk) | igreja_field_qs
            except Exception as exc:
                logger.warning('criar_visitante_parcial: falha ao ajustar queryset de igreja: %s', exc)
                try:
                    form.fields['igreja'].queryset = Igreja.objects.filter(pk=request.igreja_ativa.pk)
                except Exception as exc2:
                    logger.warning('criar_visitante_parcial: falha no fallback de queryset de igreja: %s', exc2)
            try:
                if not form.initial.get('igreja'):
                    form.initial['igreja'] = request.igreja_ativa
            except Exception as exc:
                logger.warning('criar_visitante_parcial: falha ao setar igreja inicial: %s', exc)
    except Exception as exc:
        logger.warning('criar_visitante_parcial: falha ao preparar campo de igreja: %s', exc)

    return render(request, 'secretaria/partials/_visitante_form.html', {
        'form': form,
        'ministerio': ministerio,
        'tipo_visitante_id': tipo_visitante.pk if tipo_visitante else '',
        'default_status_id': default_status.pk if default_status else '',
        'igreja_inicial_id': (igreja_inicial_for_form.pk if igreja_inicial_for_form else ''),
        'igreja_inicial_name': (getattr(igreja_inicial_for_form, 'nome_igreja', str(igreja_inicial_for_form)) if igreja_inicial_for_form else ''),
    })


# ---------------------------------------------------------------------------
# Acompanhamento de visita
# ---------------------------------------------------------------------------

@login_required
def registrar_acompanhamento_visita(request, membro_id):
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    membro = get_object_or_404(Membro, pk=membro_id, igreja__in=allowed_churches)
    if request.method == 'POST':
        form = AcompanhamentoVisitaForm(request.POST)
        if form.is_valid():
            acompanhamento = form.save(commit=False)
            acompanhamento.membro = membro
            acompanhamento.responsavel = request.user
            acompanhamento.save()
            messages.success(request, 'Acompanhamento registrado com sucesso!')
            return redirect('secretaria:editar_membro', membro_id=membro_id)
    else:
        now = timezone.localtime(timezone.now()).replace(second=0, microsecond=0)
        initial = {'data': now.strftime('%Y-%m-%dT%H:%M')}
        form = AcompanhamentoVisitaForm(initial=initial)
        acompanhamentos = AcompanhamentoVisita.objects.filter(membro=membro).order_by('-data')
        context = {
            'form': form,
            'membro': membro,
            'acompanhamentos': acompanhamentos,
        }
        return render(request, 'secretaria/registrar_acompanhamento_visita.html', context)


# ---------------------------------------------------------------------------
# Utilitário interno: sincronizar ParticipacaoEvento
# ---------------------------------------------------------------------------

def _sync_participacao_evento(request, evento, membro, sessao_id=None):
    """Sincroniza a presença com ParticipacaoEvento. Não levanta exceção em caso de falha."""
    try:
        from eventos.models import ParticipacaoEvento, EventoSessao
        from django.utils import timezone as _tz
        if sessao_id is None:
            try:
                sessao_id = int(request.POST.get('sessao')) if request.POST.get('sessao') else None
            except Exception:
                sessao_id = None

        if sessao_id:
            parts = ParticipacaoEvento.objects.filter(evento=evento, membro=membro, sessao__pk=sessao_id)
        else:
            parts = ParticipacaoEvento.objects.filter(evento=evento, membro=membro)

        if parts.exists():
            parts.update(status='PRESENTE', confirmado_em=_tz.now(), justificativa_falta='')
        else:
            sessao_obj = None
            if sessao_id:
                try:
                    sessao_obj = EventoSessao.objects.get(pk=sessao_id, evento=evento)
                except Exception:
                    sessao_obj = None
            ParticipacaoEvento.objects.create(
                evento=evento, membro=membro, sessao=sessao_obj,
                papel='PARTICIPANTE', status='PRESENTE', confirmado_em=_tz.now(),
            )
    except Exception:
        logger.exception('Erro ao sincronizar ParticipacaoEvento')
