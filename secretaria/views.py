from django.http import HttpResponseRedirect
# Redirecionamento de /membros/ para /pessoas/
def redirect_pessoas(request):
    return HttpResponseRedirect('/sistema/pessoas/')
from core.decorators import verificar_assinatura_valida
from .forms import MembroForm
from .models import AcompanhamentoVisita, Membro, TipoPessoa, Tag, GrupoCasa
import logging
from datetime import date, datetime, timedelta
import os, shutil, json
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count, Sum, Case, When, Value, BooleanField
from django.conf import settings
from django.db import models, close_old_connections
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

# --- ETAPAS DO CADASTRO PROGRESSIVO ---
@login_required
def pre_cadastro(request):
    """
    Etapa 1: Pré-cadastro - coleta dados básicos e tipo de pessoa.
    """
    import logging
    logger = logging.getLogger("django")
    from financeiro.utils import get_allowed_churches_for_user
    allowed_churches = get_allowed_churches_for_user(request.user)
    igreja_inicial_para_form = None
    # Sempre pega a igreja do seletor global
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa and request.igreja_ativa in allowed_churches:
        igreja_inicial_para_form = request.igreja_ativa
    else:
        igreja_inicial_para_form = allowed_churches.first() if allowed_churches.exists() else None

    if request.method == 'POST':
        form = MembroForm(request.POST, igreja_inicial=igreja_inicial_para_form, allowed_churches=allowed_churches, user=request.user)
        if form.is_valid():
            pessoa = form.save(commit=True)
            messages.success(request, 'Pré-cadastro realizado com sucesso!')
            return redirect('secretaria:cadastro_detalhado', pessoa_id=pessoa.pk)
    else:
        form = MembroForm(igreja_inicial=igreja_inicial_para_form, allowed_churches=allowed_churches, user=request.user)
    return render(request, 'secretaria/pre_cadastro.html', {'form': form, 'igreja_selecionada': igreja_inicial_para_form})

@login_required
def cadastro_detalhado(request, pessoa_id):
    """
    Etapa 2: Cadastro detalhado - coleta dados adicionais conforme tipo de pessoa.
    """
    pessoa = get_object_or_404(Membro, pk=pessoa_id)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    igreja_inicial = getattr(request, 'igreja_ativa', None)
    if request.method == 'POST':
        form = MembroForm(request.POST, instance=pessoa, allowed_churches=allowed_churches, igreja_inicial=igreja_inicial, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro detalhado salvo!')
            return redirect('secretaria:cadastro_complementar', pessoa_id=pessoa.pk)
    else:
        form = MembroForm(instance=pessoa, allowed_churches=allowed_churches, igreja_inicial=igreja_inicial, user=request.user)
    return render(request, 'secretaria/cadastro_detalhado.html', {'form': form, 'pessoa': pessoa})

@login_required
def cadastro_complementar(request, pessoa_id):
    """
    Etapa 3: Cadastro complementar - histórico, tags, acompanhamento, etc.
    """
    pessoa = get_object_or_404(Membro, pk=pessoa_id)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    igreja_inicial = getattr(request, 'igreja_ativa', None)
    if request.method == 'POST':
        form = MembroForm(request.POST, instance=pessoa, allowed_churches=allowed_churches, igreja_inicial=igreja_inicial, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro complementar salvo!')
            return redirect('secretaria:lista_membros')
    else:
        form = MembroForm(instance=pessoa, allowed_churches=allowed_churches, igreja_inicial=igreja_inicial, user=request.user)
    return render(request, 'secretaria/cadastro_complementar.html', {'form': form, 'pessoa': pessoa})

# --- VIEWS DE AÇÕES RÁPIDAS DE ACOMPANHAMENTO ---
@login_required
def ver_acompanhamento_visita(request, acompanhamento_id):
    acompanhamento = get_object_or_404(AcompanhamentoVisita, pk=acompanhamento_id)
    return render(request, 'secretaria/ver_acompanhamento_visita.html', {'acompanhamento': acompanhamento})

@login_required
def editar_acompanhamento_visita(request, acompanhamento_id):
    acompanhamento = get_object_or_404(AcompanhamentoVisita, pk=acompanhamento_id)
    from .forms_acompanhamento import AcompanhamentoVisitaForm
    if request.method == 'POST':
        form = AcompanhamentoVisitaForm(request.POST, instance=acompanhamento)
        if form.is_valid():
            form.save()
            return redirect('secretaria:acompanhamentos_visita')
    else:
        form = AcompanhamentoVisitaForm(instance=acompanhamento)
    return render(request, 'secretaria/editar_acompanhamento_visita.html', {'form': form, 'acompanhamento': acompanhamento})

@login_required
def excluir_acompanhamento_visita(request, acompanhamento_id):
    acompanhamento = get_object_or_404(AcompanhamentoVisita, pk=acompanhamento_id)
    if request.method == 'POST':
        acompanhamento.delete()
        return redirect('secretaria:acompanhamentos_visita')
    return render(request, 'secretaria/excluir_acompanhamento_visita.html', {'acompanhamento': acompanhamento})

# --- VIEW PARA ESCOLHER PESSOA PARA REGISTRAR ACOMPANHAMENTO ---
@login_required
def escolher_pessoa_para_acompanhamento(request):
    nome = request.GET.get('nome', '').strip()
    tipo_pessoa_id = request.GET.get('tipo_pessoa')
    qs = Membro.objects.select_related('tipo_pessoa').all()
    if nome:
        qs = qs.filter(nome__icontains=nome)
    if tipo_pessoa_id:
        qs = qs.filter(tipo_pessoa_id=tipo_pessoa_id)
    tipos = TipoPessoa.objects.all().order_by('nome')
    context = {
        'pessoas': qs.order_by('nome')[:100],
        'tipos': tipos,
    }
    return render(request, 'secretaria/escolher_pessoa_para_acompanhamento.html', context)
from .models import AcompanhamentoVisita, Membro, TipoPessoa, Tag, GrupoCasa
import logging
from datetime import date, datetime, timedelta
import os, shutil, json
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count, Sum, Case, When, Value, BooleanField
from django.conf import settings
from django.db import models, close_old_connections
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.urls import reverse

# --- VIEW PARA EDITAR TAG ---
@login_required
def editar_tag(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    if not request.user.is_staff:
        return redirect('login')
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tag atualizada com sucesso!')
            return redirect('secretaria:criar_tag')
    else:
        form = TagForm(instance=tag)
    return render(request, 'secretaria/editar_tag.html', {'form': form, 'tag': tag})

# --- VIEW PARA EXCLUIR TAG ---
@login_required
def excluir_tag(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    if not request.user.is_staff:
        return redirect('login')
    if request.method == 'POST':
        tag.delete()
        messages.success(request, 'Tag excluída com sucesso!')
        return redirect('secretaria:criar_tag')
    return render(request, 'secretaria/excluir_tag.html', {'tag': tag})
from django.template.loader import render_to_string


@login_required
@verificar_assinatura_valida
def lista_acompanhamentos_visita(request):
    """Listagem geral de acompanhamentos de visita com filtros padrão."""
    qs = AcompanhamentoVisita.objects.select_related('membro', 'responsavel', 'membro__tipo_pessoa').all()
    tipos = TipoPessoa.objects.all().order_by('nome')
    nome = request.GET.get('nome', '').strip()
    tipo_pessoa_id = request.GET.get('tipo_pessoa')
    tipo_contato = request.GET.get('tipo_contato')
    data_ini = request.GET.get('data_ini')
    data_fim = request.GET.get('data_fim')
    igreja_id = request.GET.get('igreja')
    if nome:
        qs = qs.filter(membro__nome__icontains=nome)
    if tipo_pessoa_id:
        qs = qs.filter(membro__tipo_pessoa_id=tipo_pessoa_id)
    if tipo_contato:
        qs = qs.filter(tipo_contato=tipo_contato)
    if data_ini:
        qs = qs.filter(data__gte=data_ini)
    if data_fim:
        qs = qs.filter(data__lte=data_fim)
    if igreja_id:
        qs = qs.filter(membro__igreja_id=igreja_id)
    qs = qs.order_by('-data')
    context = {
        'acompanhamentos': qs,
        'tipos': tipos,
        'filtros': {
            'nome': nome,
            'tipo_pessoa': tipo_pessoa_id,
            'tipo_contato': tipo_contato,
            'data_ini': data_ini,
            'data_fim': data_fim,
            'igreja': igreja_id,
        },
        'titulo_pagina': 'Acompanhamentos de Visita',
    }
    return render(request, 'secretaria/acompanhamentos_visita_list.html', context)

logger = logging.getLogger(__name__)
User = get_user_model()

def is_admin_or_pastor(user):
    """Permissão: é superuser ou pertence a grupos administrativos/pastorais."""
    grupos_permitidos = ["Pastor", "Administrador", "Admin Ministerio", "Lider Igreja"]
    try:
        return user.is_superuser or user.groups.filter(name__in=grupos_permitidos).exists()
    except Exception:
        return False

# --- AUTOCOMPLETE DE NOMES DE MEMBROS/VISITANTES ---
@require_GET
def autocomplete_nome(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q and len(q) >= 1:
        # import here to avoid top-level import cycles
        from .models import Membro
        membros = Membro.objects.filter(nome__istartswith=q).order_by('nome')[:10]
        for m in membros:
            results.append({
                'id': m.pk,
                'nome': m.nome,
                'tipo_pessoa': m.tipo_pessoa.nome if getattr(m, 'tipo_pessoa', None) else ''
            })
    return JsonResponse({'results': results})
# --- LISTA DE VISITANTES (usando membros com tipo_pessoa=Visitante) ---
from django.views.decorators.http import require_POST
from .models import Membro, TipoPessoa
@login_required
def lista_visitantes(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    igreja_id = request.GET.get('igreja')
    visitantes = Membro.objects.filter(tipo_pessoa__nome__iexact='Visitante')
    # Aplicar escopo de igreja/ministerio similar ao usado em `lista_membros`.
    # Sem esse escopo, visitantes registrados em outras igrejas (ex.: testes) aparecem para todos os usuários.
    try:
        from secretaria.utils import get_allowed_churches_for_membros, is_admin_org
        from core.utils import get_ministerio_or_error
        ministerio = get_ministerio_or_error(request)
        allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
        if hasattr(request, 'igreja_ativa') and request.igreja_ativa and request.igreja_ativa in allowed_churches:
            visitantes = visitantes.filter(igreja=request.igreja_ativa)
        elif allowed_churches.exists():
            visitantes = visitantes.filter(igreja__in=allowed_churches)
        elif is_admin_org(request.user):
            visitantes = visitantes.filter(igreja__ministerio=ministerio)
        else:
            visitantes = Membro.objects.none()
    except Exception as e:
        # Em caso de erro inesperado, logar e retornar nenhum visitante para evitar vazamento de dados
        try:
            logger.exception('Erro ao filtrar visitantes por igreja: %s', e)
        except Exception:
            pass
        visitantes = Membro.objects.none()
    if query:
        visitantes = visitantes.filter(
            Q(nome__icontains=query) | Q(telefone__icontains=query) | Q(email__icontains=query)
        )
    if status:
        visitantes = visitantes.filter(status_acompanhamento=status)

    # Paginação
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = request.GET.get('page', 1)
    paginator = Paginator(visitantes, 20)  # 20 visitantes por página
    try:
        visitantes_page = paginator.page(page)
    except PageNotAnInteger:
        visitantes_page = paginator.page(1)
    except EmptyPage:
        visitantes_page = paginator.page(paginator.num_pages)

    igreja_selecionada = str(igreja_id) if igreja_id else (str(request.igreja_ativa.pk) if hasattr(request, 'igreja_ativa') and request.igreja_ativa else '0')

    context = {
        'visitantes': visitantes_page,
        'query': query,
        'status': status,
        'igreja_id': igreja_id,
        'igreja_selecionada': igreja_selecionada,
        'titulo_pagina': 'Lista de Visitantes',
        'paginator': paginator,
        'page_obj': visitantes_page,
    }
    return render(request, 'secretaria/lista_visitantes.html', context)
from django.http import JsonResponse
from django.db import models
from django.db import close_old_connections
# --- VIEW AJAX: BUSCAR VISITANTES POR NOME OU APELIDO ---
def buscar_visitantes(request):
    termo = request.GET.get('q', '').strip()
    try:
        logger.info('buscar_visitantes called q=%s user=%s evento=%s', termo, getattr(request, 'user', None), request.GET.get('evento'))
    except Exception:
        pass
    # Busca ignorando acentuação (PostgreSQL: unaccent)
    import unicodedata
    from .models import Membro
    from eventos.models import Evento
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
        # Limitar busca às igrejas/ministerio permitidos para o usuário, evitando retornar visitantes de teste
        try:
            # Debug bypass: em DEBUG, aceitar parâmetro ?force_global=1 para ignorar escopo de igrejas
            if getattr(settings, 'DEBUG', False) and request.GET.get('force_global') == '1':
                membros = Membro.objects.all()
                # pula a lógica de allowed_churches
                raise StopIteration
            from secretaria.utils import get_allowed_churches_for_membros, is_admin_org
            from core.utils import get_ministerio_or_error
            ministerio = get_ministerio_or_error(request)
            allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)

            # Hotfix for reception page: if the request explicitly indicates it's
            # coming from the recepção UI (recepcao=1) and there is an active
            # church on the request, ensure that church is part of the allowed
            # set. This avoids empty autocomplete results when the user's perfil
            # is missing or not yet linked to the active church but the
            # recepcionista is operating within that church.
            try:
                if request.GET.get('recepcao') == '1' and hasattr(request, 'igreja_ativa') and request.igreja_ativa:
                    from configuracao.models import Igreja as _Igreja
                    # If allowed_churches is a QuerySet, union it with the active church
                    if getattr(allowed_churches, 'filter', None) is not None:
                        allowed_churches = allowed_churches | _Igreja.objects.filter(pk=request.igreja_ativa.pk)
                    else:
                        # If it's an in-memory iterable (list/tuple), ensure the active church is included
                        try:
                            if request.igreja_ativa not in allowed_churches:
                                allowed_churches = list(allowed_churches) + [request.igreja_ativa]
                        except Exception:
                            # As a last resort, make a QuerySet that contains only the active church
                            allowed_churches = _Igreja.objects.filter(pk=request.igreja_ativa.pk)
                    try:
                        logger.debug('buscar_visitantes: recepcao fallback applied; igreja_ativa=%s', request.igreja_ativa)
                    except Exception:
                        pass
            except Exception:
                # Don't break the search if this fallback fails; continue with original allowed_churches
                pass

            # Determine escola_qs_kwargs de forma robusta (suporta QuerySet ou lista)
            escola_qs_kwargs = None
            if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
                try:
                    # Se allowed_churches parece um queryset, usar filter().exists()
                    if getattr(allowed_churches, 'filter', None) and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
                        escola_qs_kwargs = {'igreja': request.igreja_ativa}
                    # Se allowed_churches é uma lista/iterable em memória, usar 'in'
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
            # fallback: deixar `membros` sem filtro (evita quebrar autocomplete por erros de permissão)
            membros = Membro.objects.all()
        if tipos_ids:
            membros = membros.filter(tipo_pessoa_id__in=tipos_ids)
        if status_ids:
            membros = membros.filter(status_pessoa_id__in=status_ids)
        for v in membros:
            nome = v.nome or ''
            apelido = v.apelido or ''
            if termo_sem_acento in remover_acentos(nome.lower()) or termo_sem_acento in remover_acentos(apelido.lower()):
                # Compatibilidade: alguns clientes esperam que `id` seja a chave pública (chave),
                # outros usam o PK. Fornecemos ambos e também `pk` para evitar ambiguidade.
                visitantes.append({
                    'id': (v.chave if getattr(v, 'chave', None) not in (None, '') else v.pk),
                    'pk': v.pk,
                    'chave': getattr(v, 'chave', v.pk),
                    'nome': v.nome,
                    'apelido': v.apelido
                })
            if len(visitantes) >= 20:
                break
    # debug helper: if ?debug=1 is present, return extra diagnostic info
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
        try:
            logger.debug('buscar_visitantes debug: %s', info)
        except Exception:
            pass
        return JsonResponse(info, safe=False)

    try:
        # debug log to help diagnose empty autocomplete results
        try:
            logger.debug('buscar_visitantes q=%s results=%s', termo, len(visitantes))
        except Exception:
            pass
    except Exception:
        pass
    return JsonResponse(visitantes, safe=False)
from .forms_presenca_visitante_evento import PresencaVisitanteEventoForm
from eventos.models import Evento
from .models import PresencaVisitanteEvento
from django.utils import timezone

# --- VIEW: REGISTRAR PRESENÇA DE VISITANTE EM EVENTO ---
@login_required
def registrar_presenca_visitante_evento(request):
    busca_evento = request.GET.get('busca_evento', '').strip()
    # Garantir conexões ativas/recém-abertas (mitiga 'connection already closed')
    try:
        close_old_connections()
    except Exception:
        pass
    print(f"[DEBUG] igreja_ativa: {getattr(request, 'igreja_ativa', None)} | id: {getattr(getattr(request, 'igreja_ativa', None), 'id', None)} | user: {request.user}")
    hoje = timezone.localdate()
    fim = hoje + timezone.timedelta(days=7)
    eventos_do_dia = Evento.objects.none()
    # Preparar contexto de igreja/ministerio similar a outras views: suportar igreja_ativa, allowed_churches ou admin do ministério
    try:
        from secretaria.utils import get_allowed_churches_for_membros, is_admin_org
        from core.utils import get_ministerio_or_error
        ministerio = get_ministerio_or_error(request)
        allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    except Exception:
        ministerio = None
        allowed_churches = Evento.objects.none()

    # Suporta filtros: próximos 7 dias, últimos N eventos (default), e eventos sem visitantes
    # Por padrão utilizar 'ultimos' com ultimos_n = 3 para a UX de recepção
    filtro = request.GET.get('filtro_eventos', 'ultimos')
    try:
        ultimos_n = int(request.GET.get('ultimos_n', 3))
    except (TypeError, ValueError):
        ultimos_n = 3

    # Decide o escopo de igrejas a consultar
    escola_qs_kwargs = None
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        try:
            # Se allowed_churches parece um queryset, usar filter().exists()
            if getattr(allowed_churches, 'filter', None) and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
                escola_qs_kwargs = {'igreja': request.igreja_ativa}
            # Se allowed_churches é uma lista/iterable em memória, usar 'in'
            elif hasattr(allowed_churches, '__contains__') and request.igreja_ativa in allowed_churches:
                escola_qs_kwargs = {'igreja': request.igreja_ativa}
        except Exception:
            # falha ao testar membership -> continuar para próximos testes
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
            qs = Evento.objects.filter(
                **escola_qs_kwargs,
                data_inicio__date__lte=hoje
            )
            if busca_evento:
                qs = qs.filter(titulo__icontains=busca_evento)
            qs = qs.order_by('-data_inicio')[:ultimos_n]
            eventos_do_dia = sorted(list(qs), key=lambda e: e.data_inicio)
        elif filtro == 'sem_visitantes':
            qs = Evento.objects.annotate(presencas_count=Count('visitantes_presentes')).filter(
                **escola_qs_kwargs,
                presencas_count=0,
                data_inicio__date__lte=hoje
            )
            if busca_evento:
                qs = qs.filter(titulo__icontains=busca_evento)
            eventos_do_dia = qs.order_by('data_inicio')
        else:
            qs = Evento.objects.filter(
                **escola_qs_kwargs,
                data_inicio__date__gte=hoje,
                data_inicio__date__lte=fim
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
            # Evita 500 quando o banco está indisponível ou outra falha ocorre; registra e mostra mensagem amigável
            try:
                logger.exception('Erro ao carregar evento selecionado: %s', e)
            except Exception:
                pass
            evento_selecionado = None
            pessoas_presentes = []
            messages.error(request, 'Erro ao carregar o evento selecionado. Verifique os logs.')
    if request.method == 'POST':
        # short trace id to correlate logs with requests
        try:
            import uuid
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
            # Verifica se já existe presença para este membro neste evento
            if PresencaVisitanteEvento.objects.filter(membro=membro, evento=evento).exists():
                messages.warning(request, f'A pessoa "{membro.nome}" já está registrada neste evento!')
            else:
                presenca = form.save(commit=False)
                presenca.responsavel_registro = request.user
                presenca.save()
                try:
                    logger.info('registrar_presenca_visitante_evento presenca_saved trace=%s presenca_pk=%s membro=%s evento=%s', trace_id, presenca.pk, getattr(presenca.membro, 'pk', None), getattr(presenca.evento, 'pk', None))
                except Exception:
                    logger.info('registrar_presenca_visitante_evento presenca_saved (could not format ids)')
                # Sincronizar com ParticipacaoEvento (evento.participacoes)
                try:
                    from eventos.models import ParticipacaoEvento, EventoSessao
                    from django.utils import timezone as _tz
                    sessao_id = None
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
                        # cria uma participação para a sessão especificada (se houver) ou sessao=NULL
                        sessao_obj = None
                        if sessao_id:
                            try:
                                sessao_obj = EventoSessao.objects.get(pk=sessao_id, evento=evento)
                            except Exception:
                                sessao_obj = None
                        ParticipacaoEvento.objects.create(evento=evento, membro=membro, sessao=sessao_obj, papel='PARTICIPANTE', status='PRESENTE', confirmado_em=_tz.now())
                except Exception:
                    try:
                        logger.exception('Erro ao sincronizar ParticipacaoEvento após registrar PresencaVisitanteEvento')
                    except Exception:
                        pass
                messages.success(request, f'Presença de "{presenca.membro.nome}" registrada no evento!')
            # Redirect back to the same path with the evento querystring.
            try:
                return redirect(request.path + f'?evento={evento.id}')
            except Exception:
                # Fallback: use simple redirect to the view name if above fails
                return redirect('secretaria:registrar_presenca_visitante_evento')
        else:
            # Log invalid form for diagnosis
            try:
                logger.warning('presenca form invalid: errors=%s; POST keys=%s', dict(form.errors), list(request.POST.keys()))
            except Exception:
                try:
                    logger.warning('presenca form invalid; unable to serialize errors; POST keys=%s', list(request.POST.keys()))
                except Exception:
                    pass
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


@login_required
@require_POST
def ajax_registrar_presenca_evento(request):
    """Endpoint AJAX para registrar presença de visitante em um evento e retornar JSON para atualizar a lista na página."""
    try:
        try:
            close_old_connections()
        except Exception:
            pass
        # generate a short trace id for this AJAX request to correlate logs/responses
        try:
            import uuid
            trace_id = uuid.uuid4().hex[:8]
        except Exception:
            trace_id = 'na'
        try:
            logger.info('ajax_registrar_presenca_evento called trace=%s user=%s POST_keys=%s', trace_id, request.user, list(request.POST.keys()))
        except Exception:
            pass
        evento_id = request.POST.get('evento') or request.POST.get('evento_id')
        membro_id = request.POST.get('membro') or request.POST.get('membro_id')
        try:
            logger.debug('ajax_registrar_presenca_evento POST keys: %s', list(request.POST.keys()))
        except Exception:
            pass
        if not evento_id or not membro_id:
            return JsonResponse({'error': 'Evento ou membro não informado.', 'trace_id': trace_id}, status=400)
        # Tenta localizar evento e membro
        try:
            evento = Evento.objects.get(pk=evento_id)
        except Evento.DoesNotExist:
            return JsonResponse({'error': 'Evento não encontrado.', 'trace_id': trace_id}, status=404)
        # membro_id may be numeric or string. Try numeric lookup first, then fallback to matching 'chave'.
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
            return JsonResponse({'error': f'Membro não encontrado (valor enviado: {membro_id}). Verifique se o cadastro foi persistido e tente novamente.', 'trace_id': trace_id}, status=404)
        # Verifica duplicidade
        if PresencaVisitanteEvento.objects.filter(membro=membro, evento=evento).exists():
            return JsonResponse({'exists': True, 'message': 'Presença já registrada.', 'trace_id': trace_id})
        presenca = PresencaVisitanteEvento(evento=evento, membro=membro, responsavel_registro=request.user)
        presenca.save()
        try:
            logger.info('Presença salva via AJAX: trace=%s presenca_pk=%s membro_chave=%s evento_id=%s', trace_id, presenca.pk, getattr(membro, 'chave', membro.pk), getattr(evento, 'pk', None))
        except Exception:
            try:
                logger.info('Presença salva via AJAX (could not format identifiers)')
            except Exception:
                pass
        # Também sincroniza com ParticipacaoEvento para que a presença apareça
        try:
            from eventos.models import ParticipacaoEvento, EventoSessao
            from django.utils import timezone as _tz
            sessao_id = None
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
                try:
                    logger.info('ParticipacaoEvento updated via AJAX: evento=%s membro_chave=%s sessao=%s count=%s', evento.pk, getattr(membro, 'chave', membro.pk), sessao_id, parts.count())
                except Exception:
                    try:
                        logger.info('ParticipacaoEvento updated via AJAX (could not format identifiers)')
                    except Exception:
                        pass
            else:
                sessao_obj = None
                if sessao_id:
                    try:
                        sessao_obj = EventoSessao.objects.get(pk=sessao_id, evento=evento)
                    except Exception:
                        sessao_obj = None
                new_part = ParticipacaoEvento.objects.create(evento=evento, membro=membro, sessao=sessao_obj, papel='PARTICIPANTE', status='PRESENTE', confirmado_em=_tz.now())
                try:
                    logger.info('ParticipacaoEvento criado via AJAX: pk=%s evento=%s membro_chave=%s sessao=%s', new_part.pk, evento.pk, getattr(membro, 'chave', membro.pk), getattr(sessao_obj, 'pk', None) if sessao_obj else None)
                except Exception:
                    try:
                        logger.info('ParticipacaoEvento criado via AJAX (could not format identifiers)')
                    except Exception:
                        pass
        except Exception:
            try:
                logger.exception('Erro ao sincronizar ParticipacaoEvento após ajax_registrar_presenca_evento')
            except Exception:
                pass
        hora = presenca.data_registro.strftime('%H:%M') if presenca.data_registro else ''
        presenca_data = {'id': presenca.pk, 'nome': membro.nome, 'apelido': getattr(membro, 'apelido', '') or '', 'hora': hora}
        try:
            presenca_html = render_to_string('secretaria/partials/_presenca_list_item.html', {
                'presenca_id': presenca.pk,
                'presenca_nome': membro.nome,
                'presenca_apelido': getattr(membro, 'apelido', '') or '',
                'presenca_hora': hora
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
            return JsonResponse({'error': 'Erro interno', 'trace_id': trace_id}, status=500)
from .forms_acompanhamento import AcompanhamentoVisitaForm
from .forms import AssociarUsuarioMembroForm
from .forms_grupocasa import GrupoCasaForm


@login_required
def registrar_acompanhamento_visita(request, membro_id):
    membro = get_object_or_404(Membro, pk=membro_id)
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
            'acompanhamentos': acompanhamentos
        }
        return render(request, 'secretaria/registrar_acompanhamento_visita.html', context)
    


# --- Associação em massa de membros a usuários ---
@login_required
@user_passes_test(is_admin_or_pastor)
@verificar_assinatura_valida
def associar_usuarios_membros(request):
    membros_queryset = Membro.objects.none()
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        tipo_pessoa = request.GET.get('tipo_pessoa', '')
        tipos_validos = ['Membro', 'Obreiro']
        if tipo_pessoa in tipos_validos:
            membros_queryset = Membro.objects.filter(
                igreja=request.igreja_ativa,
                tipo_pessoa__nome=tipo_pessoa
            )
        else:
            membros_queryset = Membro.objects.filter(
                igreja=request.igreja_ativa,
                tipo_pessoa__nome__in=tipos_validos
            )
        # Filtro por status de associação
        status_associacao = request.GET.get('status_associacao', '')
        if status_associacao == 'associado':
            membros_queryset = membros_queryset.filter(usuario__isnull=False)
        elif status_associacao == 'nao_associado':
            membros_queryset = membros_queryset.filter(usuario__isnull=True)
        membros_queryset = membros_queryset.order_by('nome')

    # Paginação
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = request.GET.get('page', 1)
    paginator = Paginator(membros_queryset, 15)  # 15 membros por página
    try:
        membros_page = paginator.page(page)
    except PageNotAnInteger:
        membros_page = paginator.page(1)
    except EmptyPage:
        membros_page = paginator.page(paginator.num_pages)
    User = get_user_model()
    sugestoes = {}
    resultados = []  # Para feedback por linha
    if request.method == 'POST':
        alterados = 0
        for membro in membros_page:
            usuario_id = request.POST.get(f"usuario_{membro.pk}")
            if usuario_id:
                try:
                    usuario = User.objects.get(pk=usuario_id)
                    if membro.usuario != usuario:
                        membro.usuario = usuario
                        membro.save()
                        resultados.append((membro, 'ok', f"Associado a {usuario.get_full_name() or usuario.username}"))
                        alterados += 1
                    else:
                        resultados.append((membro, 'info', "Já estava associado"))
                except User.DoesNotExist:
                    resultados.append((membro, 'erro', "Usuário não encontrado"))
            else:
                resultados.append((membro, 'info', "Nenhum usuário selecionado"))
        if alterados:
            messages.success(request, f"{alterados} associação(ões) salva(s) com sucesso! <i class='fas fa-check-circle text-success'></i>")
        else:
            messages.info(request, "Nenhuma alteração realizada.")
        # Passa resultados para template para feedback por linha
        context = {
            'membros_page': membros_page,
            'resultados': resultados,
            'paginator': paginator,
            'page_obj': membros_page,
        }
        return render(request, 'secretaria/associar_usuarios_membros.html', context)
    # GET: monta selects e sugestões normalmente
    forms_list = []
    for membro in membros_page:
        form = AssociarUsuarioMembroForm(membro=membro)
        sugestao_id = form.fields['sugestao_usuario_id'].initial
        sugestoes[membro.pk] = int(sugestao_id) if sugestao_id else None
        forms_list.append(form)
    context = {
        'membros_page': membros_page,
        'forms_list': forms_list,
        'sugestoes': sugestoes,
        'paginator': paginator,
        'page_obj': membros_page,
    }
    return render(request, 'secretaria/associar_usuarios_membros.html', context)


from django.http import HttpResponse, JsonResponse, Http404
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Sum, Case, When, Value, BooleanField
from django.db.models.functions import Extract
from django.utils.crypto import get_random_string
import zipfile
from django import forms

# Gerenciar ocupantes do cargo

from .forms import GerenciarOcupantesForm, CargoForm



# --- NOVA VIEW: Gerenciar Ocupantes (usando novos modelos) ---
from .models import Cargo, MembroCargo

@login_required
@user_passes_test(is_admin_or_pastor)
def gerenciar_ocupantes(request, cargo_id):
    cargo = get_object_or_404(Cargo, id=cargo_id)
    membros = list(Membro.objects.all().order_by('nome'))
    ocupantes_atual = list(MembroCargo.objects.filter(cargo=cargo).select_related('membro'))
    if request.method == 'POST':
        ocupantes_ids = request.POST.get('ocupantes', '')
        if ocupantes_ids:
            ids = [int(i) for i in ocupantes_ids.split(',') if i.isdigit()]
            novos_ocupantes = Membro.objects.filter(chave__in=ids)
        else:
            from django.db.models import Q
            membros_lista = Membro.objects.filter(
                Q(igreja=request.igreja_ativa) & (Q(tipo_pessoa__nome='Membro') | Q(tipo_pessoa__nome='Obreiro'))
            ).order_by('nome')
        # Adiciona novos ocupantes (evita duplicidade)
            # Paginação
            from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
            page = request.GET.get('page', 1)
            paginator = Paginator(membros_lista, 15)  # 15 membros por página
            try:
                membros_page = paginator.page(page)
            except PageNotAnInteger:
                membros_page = paginator.page(1)
            except EmptyPage:
                membros_page = paginator.page(paginator.num_pages)
        return redirect('secretaria:lista_cargos')
    else:
        ocupantes_iniciais = [mc.membro.chave for mc in ocupantes_atual]
        forms_list = []
        sugestoes = {}
        for membro in membros_page:
            form = AssociarUsuarioMembroForm(request.POST if request.method == 'POST' else None, prefix=str(membro.pk), membro=membro)
            if request.method == 'POST' and form.is_valid():
                usuario = form.cleaned_data['usuario']
                membro.usuario = usuario
                membro.save()
            sugestao_id = form.fields['sugestao_usuario_id'].initial
            sugestoes[membro.pk] = int(sugestao_id) if sugestao_id else None
            forms_list.append(form)
        return render(request, 'secretaria/gerenciar_ocupantes.html', {
            'cargo': cargo,
            'membros_page': membros_page,
            'forms_list': forms_list,
            'sugestoes': sugestoes,
            'ocupantes_iniciais': ocupantes_iniciais,
        })
def excluir_cargo(request, cargo_id):
    cargo = get_object_or_404(Cargo, id=cargo_id)
    ocupantes = MembroCargo.objects.filter(cargo=cargo)



@login_required
@user_passes_test(is_admin_or_pastor)
def criar_cargo(request):
    if request.method == 'POST':
        form = CargoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo criado com sucesso!')
            return redirect('secretaria:lista_cargos')
    else:
        form = CargoForm()
    return render(request, 'secretaria/criar_cargo.html', {'form': form})



@login_required
@user_passes_test(is_admin_or_pastor)
def editar_cargo(request, cargo_id):
    cargo = get_object_or_404(Cargo, id=cargo_id)
    if request.method == 'POST':
        form = CargoForm(request.POST, instance=cargo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo atualizado com sucesso!')
            return redirect('secretaria:lista_cargos')
    else:
        form = CargoForm(instance=cargo)
    return render(request, 'secretaria/editar_cargo.html', {'form': form, 'cargo': cargo})


# --- VIEW: LISTA DE CARGOS ---



# --- NOVA VIEW: Lista deCargo (usando novos modelos) ---
@login_required
@user_passes_test(is_admin_or_pastor)


@verificar_assinatura_valida
def lista_cargos(request):
    from django.contrib import messages
    cargos = Cargo.objects.all().prefetch_related('membrocargo_set__membro', 'grupo_permissao')
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        # Filtra ocupantes dos cargos pela igreja ativa
        for cargo in cargos:
            cargo.ocupantes = [mc.membro for mc in cargo.membrocargo_set.all() if mc.membro and mc.membro.igreja_id == request.igreja_ativa.id]
            # Define a igreja do cargo como a igreja ativa
            cargo.igreja = request.igreja_ativa
    else:
        for cargo in cargos:
            cargo.ocupantes = [mc.membro for mc in cargo.membrocargo_set.all() if mc.membro]
            # Tenta pegar a igreja do primeiro ocupante, se existir
            cargo.igreja = cargo.ocupantes[0].igreja if cargo.ocupantes else None
    igreja_selecionada = str(request.igreja_ativa.pk) if hasattr(request, 'igreja_ativa') and request.igreja_ativa else '0'
    context = {
        'cargos': cargos,
        'igreja_selecionada': igreja_selecionada,
    }
    return render(request, 'secretaria/lista_cargos.html', context)
# --- LINHA DO TEMPO DOS MEMBROS ---
from .models import TimelineEvent


# Apenas para administradores/pastores (ajuste conforme seu sistema de permissões)

# --- IMPORTS PADRÃO PYTHON ---
import os
from datetime import date, datetime
import json

# --- IMPORTS DJANGO ---
from django.http import JsonResponse, Http404

# --- OUTROS IMPORTS DO PROJETO ---
from .models import TimelineEvent, Membro, TipoPessoa, StatusPessoa, StatusHistorico
from .forms import MembroForm, MembroUserManagementForm, StatusHistoricoManualForm

# Helper: instantiate MembroForm safely when some versions of the class do not accept
# extra kwargs like ministerio/user/allowed_churches/igreja_inicial. This tries
# the normal instantiation first and on TypeError falls back to removing those
# kwargs and then applies minimal queryset/initial adjustments expected by views.
def safe_instantiate_membroform(*args, **kwargs):
    extras = ('ministerio', 'user', 'allowed_churches', 'igreja_inicial')
    try:
        return MembroForm(*args, **kwargs)
    except TypeError as e:
        # try remove known extras and instantiate
        filtered = kwargs.copy()
        for k in extras:
            filtered.pop(k, None)
        try:
            inst = MembroForm(*args, **filtered)
        except TypeError:
            # last-resort: call without kwargs
            try:
                inst = MembroForm(*args[:2]) if args else MembroForm()
            except Exception:
                inst = MembroForm()

        # apply minimal post-init adjustments expected by views
        try:
            ministerio = kwargs.get('ministerio')
            user = kwargs.get('user')
            allowed_churches = kwargs.get('allowed_churches')
            igreja_inicial = kwargs.get('igreja_inicial')
            if hasattr(inst, 'fields'):
                if 'igreja' in inst.fields:
                    try:
                        if user and not is_admin_org(user) and allowed_churches is not None:
                            inst.fields['igreja'].queryset = allowed_churches
                        elif ministerio:
                            inst.fields['igreja'].queryset = Igreja.objects.filter(ministerio=ministerio).order_by('nome_igreja')
                        else:
                            inst.fields['igreja'].queryset = Igreja.objects.none()
                    except Exception:
                        pass
                    try:
                        if igreja_inicial and getattr(inst.fields['igreja'].queryset, 'filter', None):
                            if inst.fields['igreja'].queryset.filter(pk=igreja_inicial.pk).exists():
                                inst.initial.setdefault('igreja', igreja_inicial)
                                inst.fields['igreja'].disabled = True
                    except Exception:
                        pass
                if 'tipo_pessoa' in inst.fields:
                    try:
                        inst.fields['tipo_pessoa'].queryset = TipoPessoa.objects.all().order_by('nome')
                    except Exception:
                        pass
                if 'status_pessoa' in inst.fields:
                    try:
                        inst.fields['status_pessoa'].queryset = StatusPessoa.objects.all().order_by('nome')
                    except Exception:
                        pass
        except Exception:
            pass
        return inst
from django.urls import reverse
# --- VIEW PARA CADASTRAR VISITANTE (cria membro com tipo_pessoa=Visitante) ---
@login_required
def cadastrar_visitante(request):
    from .models import TipoPessoa
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    igreja_inicial_para_form = None
    # Busca o tipo_pessoa Visitante
    try:
        tipo_visitante = TipoPessoa.objects.get(nome__iexact='Visitante')
    except TipoPessoa.DoesNotExist:
        messages.error(request, "Tipo de pessoa 'Visitante' não encontrado. Cadastre o tipo primeiro.")
        return redirect('secretaria:lista_visitantes')

    if not is_admin_org(request.user) and not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar visitantes ou não está associado a nenhuma igreja específica.")
        return redirect('secretaria:lista_visitantes')

    if request.method == 'POST':
        form = MembroForm(request.POST, request.FILES,
                          ministerio=ministerio,
                          user=request.user,
                          allowed_churches=allowed_churches,
                          igreja_inicial=request.igreja_ativa)
        if form.is_valid():
            try:
                visitante = form.save(commit=False)
                visitante.tipo_pessoa = tipo_visitante
                # Definir status_pessoa como 'Ativo' automaticamente
                from .models import StatusPessoa
                try:
                    status_ativo = StatusPessoa.objects.get(nome__iexact='Ativo')
                    visitante.status_pessoa = status_ativo
                except StatusPessoa.DoesNotExist:
                    messages.error(request, "Status 'Ativo' não encontrado. Cadastre o status primeiro.")
                    return redirect('secretaria:lista_visitantes')
                if not is_admin_org(request.user) and visitante.igreja not in allowed_churches:
                    messages.error(request, "Erro: Igreja selecionada inválida para sua permissão.")
                else:
                    visitante.save(user=request.user)
                    messages.success(request, f"Visitante '{visitante.nome}' cadastrado com sucesso!")
                    # Se a janela foi aberta a partir da recepção, não redirecionamos: retornamos o template com dados do visitante
                    if request.GET.get('opener') == 'recepcao':
                        import json
                        created_visitante = {
                            'id': visitante.pk,
                            'chave': getattr(visitante, 'chave', visitante.pk),
                            'nome': visitante.nome,
                            'apelido': visitante.apelido
                        }
                        context = {
                            'form': form,
                            'ministerio': ministerio,
                            'titulo_pagina': 'Cadastrar Novo Visitante',
                            'created_visitante_json': json.dumps(created_visitante)
                        }
                        return render(request, 'secretaria/criar_visitante.html', context)
                    return redirect('secretaria:lista_visitantes')
            except Exception as e:
                logger.exception(f"Erro ao salvar novo visitante para ministério {ministerio.id}")
                messages.error(request, f"Ocorreu um erro ao salvar o visitante: {e}")
        else:
            messages.error(request, "Erro ao cadastrar visitante. Verifique os campos.")
    else:
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            igreja_inicial_para_form = request.igreja_ativa
        elif allowed_churches.count() == 1:
            igreja_inicial_para_form = allowed_churches.first()

        form = MembroForm(ministerio=ministerio,
                          user=request.user,
                          allowed_churches=allowed_churches,
                          igreja_inicial=igreja_inicial_para_form)
        # Pré-seleciona o tipo_pessoa como Visitante
        form.fields['tipo_pessoa'].initial = tipo_visitante.pk
        form.fields['tipo_pessoa'].widget = forms.HiddenInput()

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Cadastrar Novo Visitante'
    }
    return render(request, 'secretaria/criar_visitante.html', context)


@login_required
def criar_visitante_parcial(request):
    """Retorna o formulário parcial do visitante para uso em modal (GET) ou processa criação via AJAX (POST -> JSON)."""
    try:
        close_old_connections()
    except Exception:
        pass
    # Debug writes for visitante creation are controlled by Django's settings.DEBUG.
    # Temporary forcing toggles were removed to avoid writing debug files in production.
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)

    if request.method == 'POST':
        # Accept POSTs even if the client did not set the X-Requested-With header.
        # Some browsers or user actions may submit the form as a regular POST; in that case
        # we still want to process the creation and return structured JSON instead of
        # rendering the partial HTML (which causes the browser to navigate to the partial).
        is_ajax = bool(request.headers.get('x-requested-with') == 'XMLHttpRequest')
        try:
            logger.debug('criar_visitante_parcial called via POST; is_ajax=%s; POST keys=%s', is_ajax, list(request.POST.keys()))
        except Exception:
            pass
        # Log incoming POST keys for easier debugging when the client reports missing IDs
        try:
            logger.debug('criar_visitante_parcial POST keys (before injection): %s', list(request.POST.keys()))
        except Exception:
            pass

        # Ensure the POST contains the required tipo_pessoa (Visitante) and a sensible default status_pessoa
        try:
            tipo_visitante = TipoPessoa.objects.get(nome__iexact='Visitante')
        except TipoPessoa.DoesNotExist:
            return JsonResponse({'error': "Tipo 'Visitante' não encontrado."}, status=400)

        # Escolher um status padrão (preferir 'Ativo' se existir, senão o primeiro disponível)
        try:
            from .models import StatusPessoa
            default_status = StatusPessoa.objects.filter(nome__iexact='Ativo').first() or StatusPessoa.objects.first()
        except Exception:
            default_status = None

        # Copy POST data and inject tipo_pessoa and status_pessoa so form validation passes
        data = request.POST.copy()
        data['tipo_pessoa'] = str(tipo_visitante.pk)
        if default_status:
            data['status_pessoa'] = str(default_status.pk)
        # If the POST did not include 'igreja', default to the current active church (server-side safety)
        try:
            if (not data.get('igreja') or str(data.get('igreja')).strip() == ''):
                if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
                    data['igreja'] = str(request.igreja_ativa.pk)
                elif allowed_churches and getattr(allowed_churches, 'exists', None) and allowed_churches.exists():
                    # fallback: use the first allowed church
                    try:
                        data['igreja'] = str(allowed_churches.first().pk)
                    except Exception:
                        pass
        except Exception:
            pass

        try:
            logger.debug('criar_visitante_parcial POST keys (after injection): %s', list(data.keys()))
        except Exception:
            pass

        # For visitante creation, some choice fields in MembroForm are required but
        # the modal/client typically sends a minimal payload. Inject sensible
        # defaults for those required choice fields so validation passes.
        try:
            # genero choices: ('M','F') - default to 'M'
            if not data.get('genero'):
                data['genero'] = 'M'
            # estado_civil choices include 'Solteiro' - default to 'Solteiro'
            if not data.get('estado_civil'):
                data['estado_civil'] = 'Solteiro'
            # escolaridade: choose a safe default matching choices in forms
            if not data.get('escolaridade'):
                data['escolaridade'] = 'Sem Escolaridade'
        except Exception:
            pass

        try:
            form = MembroForm(data, request.FILES,
                              ministerio=ministerio,
                              user=request.user,
                              allowed_churches=allowed_churches,
                              igreja_inicial=request.igreja_ativa)
        except Exception as e:
            # Write an ephemeral debug entry and return structured JSON so the client
            # does not receive a full HTML error page (which causes navigation).
            try:
                # Log sanitized payload via logger instead of writing ad-hoc files.
                payload = {k: request.POST.getlist(k) for k in request.POST.keys()}
                # sanitize: remove long values and potential sensitive keys
                SENSITIVE_KEYS = {'senha', 'password', 'ssn', 'cpf', 'rg'}
                def _sanitize(v):
                    try:
                        if isinstance(v, list):
                            return [str(x)[:200] for x in v]
                        return str(v)[:200]
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
                visitante.status_pessoa = default_status
            try:
                visitante.save(user=request.user)
            except Exception as e:
                logger.exception('Erro ao salvar visitante via AJAX: %s', e)
                # Ephemeral debug via logger with sanitized payload
                try:
                    import json as _json
                    payload = {k: request.POST.getlist(k) for k in request.POST.keys()}
                    SENSITIVE_KEYS = {'senha', 'password', 'ssn', 'cpf', 'rg'}
                    def _sanitize(v):
                        try:
                            if isinstance(v, list):
                                return [str(x)[:200] for x in v]
                            return str(v)[:200]
                        except Exception:
                            return '[unserializable]'
                    sanitized = {k: _sanitize(v) for k, v in payload.items() if k.lower() not in SENSITIVE_KEYS}
                    logger.debug('visitante create - save_error - user=%s exception=%s post=%s', request.user, e, sanitized)
                except Exception:
                    logger.debug('visitante create - failed to log save_error', exc_info=True)
            # Provide both numeric and string forms to avoid client-side ambiguity
            created = {
                'id': visitante.pk,
                'chave': getattr(visitante, 'chave', visitante.pk),
                'id_str': str(getattr(visitante, 'pk', '')),
                'chave_str': str(getattr(visitante, 'chave', getattr(visitante, 'pk', ''))),
                'nome': visitante.nome,
                'apelido': visitante.apelido or ''
            }
            # Verifica persistência no banco
            try:
                persisted = Membro.objects.filter(pk=visitante.pk).exists()
            except Exception as e:
                persisted = False
                logger.exception('Erro verificando persistência do visitante: %s', e)
            logger.info('Visitante criado via AJAX: %s (id=%s) persisted=%s', visitante.nome, visitante.pk, persisted)
            # If the client requested automatic presence registration, attempt to create it
            auto_submit_flag = (data.get('auto_submit_presenca') or request.POST.get('auto_submit_presenca') or request.GET.get('auto_submit_presenca'))
            evento_id_for_auto = (data.get('evento') or request.POST.get('evento') or request.GET.get('evento'))

            presenca_payload = None
            presenca_html = ''
            if auto_submit_flag and evento_id_for_auto:
                try:
                    # reuse logic similar to ajax_registrar_presenca_evento to create presence
                    from .models import PresencaVisitanteEvento
                    from eventos.models import ParticipacaoEvento, EventoSessao, Evento
                    from django.utils import timezone as _tz

                    evento_obj = Evento.objects.get(pk=evento_id_for_auto)
                    presenca_obj = PresencaVisitanteEvento(evento=evento_obj, membro=visitante, responsavel_registro=request.user)
                    presenca_obj.save()

                    # sync ParticipacaoEvento
                    sessao_id = None
                    try:
                        sessao_val = data.get('sessao') or request.POST.get('sessao') or request.GET.get('sessao')
                        sessao_id = int(sessao_val) if sessao_val else None
                    except Exception:
                        sessao_id = None

                    if sessao_id:
                        parts = ParticipacaoEvento.objects.filter(evento=evento_obj, membro=visitante, sessao__pk=sessao_id)
                    else:
                        parts = ParticipacaoEvento.objects.filter(evento=evento_obj, membro=visitante)

                    if parts.exists():
                        parts.update(status='PRESENTE', confirmado_em=_tz.now(), justificativa_falta='')
                    else:
                        sessao_obj = None
                        if sessao_id:
                            try:
                                sessao_obj = EventoSessao.objects.get(pk=sessao_id, evento=evento_obj)
                            except Exception:
                                sessao_obj = None
                        ParticipacaoEvento.objects.create(evento=evento_obj, membro=visitante, sessao=sessao_obj, papel='PARTICIPANTE', status='PRESENTE', confirmado_em=_tz.now())

                    hora = presenca_obj.data_registro.strftime('%H:%M') if getattr(presenca_obj, 'data_registro', None) else ''
                    presenca_payload = {
                        'id': presenca_obj.pk,
                        'nome': visitante.nome,
                        'apelido': getattr(visitante, 'apelido', '') or '',
                        'hora': hora
                    }

                    try:
                        presenca_html = render_to_string('secretaria/partials/_presenca_list_item.html', {
                            'presenca_id': presenca_obj.pk,
                            'presenca_nome': visitante.nome,
                            'presenca_apelido': getattr(visitante, 'apelido', '') or '',
                            'presenca_hora': hora
                        }, request=request)
                    except Exception:
                        presenca_html = ''
                except Exception:
                    # Log but don't fail the visitor creation when presence creation fails
                    logger.exception('Erro criando presença automaticamente após criar visitante via AJAX')

            resp = {'visitante': created, 'saved': True, 'found_in_db': bool(persisted)}
            if presenca_payload:
                resp.update({'presenca': presenca_payload, 'presenca_html': presenca_html})
            return JsonResponse(resp)
        else:
            # Retorna erros do form para o cliente renderizar
            errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
            # Renderiza o partial com erros para facilitar exibição no modal
            try:
                errors_html = render_to_string('secretaria/partials/_visitante_form.html', {'form': form, 'ministerio': ministerio}, request=request)
            except Exception:
                errors_html = ''
            # Também logar os dados recebidos para diagnóstico e escrever debug, se em DEBUG
            try:
                logger.warning('Form inválido ao criar visitante via AJAX: %s; POST keys: %s', errors, list(request.POST.keys()))
            except Exception:
                logger.warning('Form inválido ao criar visitante via AJAX: %s', errors)
            try:
                try:
                    import json as _json
                    payload = {k: request.POST.getlist(k) for k in request.POST.keys()}
                    SENSITIVE_KEYS = {'senha', 'password', 'ssn', 'cpf', 'rg'}
                    def _sanitize(v):
                        try:
                            if isinstance(v, list):
                                return [str(x)[:200] for x in v]
                            return str(v)[:200]
                        except Exception:
                            return '[unserializable]'
                    sanitized = {k: _sanitize(v) for k, v in payload.items() if k.lower() not in SENSITIVE_KEYS}
                    logger.debug('visitante create - validation_failed - user=%s post=%s errors=%s', request.user, sanitized, errors)
                except Exception:
                    logger.debug('visitante create - failed to log validation_failed', exc_info=True)
            except Exception:
                pass
            return JsonResponse({'errors': errors, 'errors_html': errors_html}, status=400)

    # GET -> render partial
    # Determine igreja inicial for the form: prefer request.igreja_ativa, else fall back to the first allowed church (if any)
    try:
        igreja_inicial_for_form = request.igreja_ativa if hasattr(request, 'igreja_ativa') and request.igreja_ativa else (allowed_churches.first() if allowed_churches and getattr(allowed_churches, 'exists', None) and allowed_churches.exists() else None)
    except Exception:
        igreja_inicial_for_form = None

    # Prefer server-side prefill: if ?q= is present, pass it as initial for the 'nome' field
    q = request.GET.get('q')
    form_init_kwargs = {'ministerio': ministerio, 'user': request.user, 'allowed_churches': allowed_churches, 'igreja_inicial': igreja_inicial_for_form}
    if q:
        # pass initial so the ModelForm renders the value directly into the widget
        form_init_kwargs['initial'] = {'nome': q}
    try:
        form = MembroForm(**form_init_kwargs)
    except Exception as e:
        try:
            logger.debug('visitante create - form_init_get_error - user=%s exception=%s', request.user, e)
        except Exception:
            logger.debug('visitante create - failed to log form_init_get_error', exc_info=True)

        logger.exception('Erro ao instanciar MembroForm (GET) na criar_visitante_parcial: %s', e)
        # Fallback: try to instantiate with safest available defaults, then last-resort bare form
        try:
            form = MembroForm(ministerio=ministerio, user=request.user, allowed_churches=allowed_churches, igreja_inicial=igreja_inicial_for_form)
        except Exception:
            try:
                form = MembroForm(ministerio=ministerio, user=request.user, allowed_churches=allowed_churches)
            except Exception:
                # Last-resort fallback: instantiate with the minimal sensible context
                # so that ModelChoiceFields (tipo/status/igreja) have their querysets populated
                try:
                    form = MembroForm(ministerio=ministerio, user=request.user, allowed_churches=allowed_churches)
                except Exception:
                    # If even that fails, fall back to a bare form to avoid raising further
                    form = MembroForm()
    q = request.GET.get('q')
    if q:
        # prefill the 'nome' field with the query if provided
        try:
            form.initial['nome'] = q
            if 'nome' in form.fields:
                form.fields['nome'].initial = q
        except Exception:
            pass

    # Ensure the partial knows which tipo/status will be applied so we can render hidden inputs
    try:
        tipo_visitante = TipoPessoa.objects.get(nome__iexact='Visitante')
    except TipoPessoa.DoesNotExist:
        tipo_visitante = None
    try:
        default_status = StatusPessoa.objects.filter(nome__iexact='Ativo').first() or StatusPessoa.objects.first()
    except Exception:
        default_status = None
    # Ensure the form's igreja queryset includes the active church so the select shows the correct value
    try:
        if hasattr(request, 'igreja_ativa') and request.igreja_ativa and 'igreja' in form.fields:
            igreja_field_qs = form.fields['igreja'].queryset
            try:
                if not igreja_field_qs.filter(pk=request.igreja_ativa.pk).exists():
                    from configuracao.models import Igreja as _Igreja
                    # prepend the active church to the queryset so it appears in the select
                    form.fields['igreja'].queryset = _Igreja.objects.filter(pk=request.igreja_ativa.pk) | igreja_field_qs
            except Exception:
                # fallback: set queryset to include at least the active church
                try:
                    from configuracao.models import Igreja as _Igreja
                    form.fields['igreja'].queryset = _Igreja.objects.filter(pk=request.igreja_ativa.pk)
                except Exception:
                    pass
            # set initial if not already set
            try:
                if not form.initial.get('igreja'):
                    form.initial['igreja'] = request.igreja_ativa
            except Exception:
                pass
    except Exception:
        pass

    return render(request, 'secretaria/partials/_visitante_form.html', {
        'form': form,
        'ministerio': ministerio,
        'tipo_visitante_id': tipo_visitante.pk if tipo_visitante else '',
        'default_status_id': default_status.pk if default_status else '',
        'igreja_inicial_id': (igreja_inicial_for_form.pk if igreja_inicial_for_form else ''),
        'igreja_inicial_name': (getattr(igreja_inicial_for_form, 'nome_igreja', str(igreja_inicial_for_form)) if igreja_inicial_for_form else '')
    })
from core.utils import get_ministerio_or_error
from secretaria.utils import get_allowed_churches_for_membros, is_admin_org, has_membro_view_permission, has_membro_edit_permission
from core.decorators import check_permission
from configuracao.models import AssinaturaMinisterio, Igreja, PerfilUsuario

# --- Função de permissão para uso em decorators ---


@login_required
@require_GET
def ajax_get_presencas_evento(request):
    """Retorna fragmento HTML com as presenças do evento (para atualização parcial)."""
    try:
        close_old_connections()
    except Exception:
        pass
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
    # Retorna o fragmento HTML pronto para injeção via AJAX
    return JsonResponse({'html': html})

@login_required
@user_passes_test(is_admin_or_pastor)
@verificar_assinatura_valida
def linha_do_tempo(request):
    # Força valor padrão do filtro período
    periodo_predefinido = request.GET.get('periodo_predefinido')
    # Se não houver filtro, redireciona para a página já filtrando por 'mes_atual'
    if not periodo_predefinido and not request.GET:
        from django.urls import reverse
        return redirect(f"{reverse('secretaria:linha_do_tempo')}?periodo_predefinido=mes_atual")
    # ...existing code...
    from collections import OrderedDict, defaultdict
    import json
    from itertools import zip_longest
    from .models import TimelineEvent, StatusHistorico, StatusPessoa, TipoPessoa
    # from .forms import TimelineFilterForm  # Removed: defined locally below
    TIPO_COLORS = {
        'membro': 'bg-primary',
        'visitante': 'bg-info',
        'obreiro': 'bg-success',
        'congregado': 'bg-warning',
        'novo convertido': 'bg-secondary',
    }
    STATUS_COLORS = {
        'ativo': 'bg-success',
        'inativo': 'bg-secondary',
        'em disciplina': 'bg-warning',
        'desligado': 'bg-danger',
        'transferido': 'bg-info',
        'falecido': 'bg-dark',
    }
    # Minimal local TimelineFilterForm to avoid importing the full forms module here.
    # This mirrors the expected cleaned_data keys used below: tipo_evento, data_inicio, data_fim,
    # tipo_pessoa_novo, status_pessoa_novo. If you have a canonical form in .forms, it can replace this.
    from django import forms as _forms
    class TimelineFilterForm(_forms.Form):
        tipo_evento = _forms.MultipleChoiceField(required=False, choices=getattr(TimelineEvent, 'TIPO_EVENTO_CHOICES', []))
        data_inicio = _forms.DateField(required=False)
        data_fim = _forms.DateField(required=False)
        tipo_pessoa_novo = _forms.ModelMultipleChoiceField(required=False, queryset=TipoPessoa.objects.all())
        status_pessoa_novo = _forms.ModelMultipleChoiceField(required=False, queryset=StatusPessoa.objects.all())

    form = TimelineFilterForm(request.GET or None)
    print('linha_do_tempo: form.is_valid =', form.is_valid())
    print('linha_do_tempo: cleaned_data =', getattr(form, 'cleaned_data', {}))
    eventos_timeline = []
    # Filtros do formulário
    from django.utils import timezone
    tipos_evento = form.cleaned_data.get('tipo_evento') if form.is_valid() else []
    data_inicio = form.cleaned_data.get('data_inicio') if form.is_valid() else None
    data_fim = form.cleaned_data.get('data_fim') if form.is_valid() else None
    # Se filtro é 'mes_atual' e não há datas, preencher datas do mês atual
    if periodo_predefinido == 'mes_atual' and not data_inicio and not data_fim:
        hoje = datetime.today()
        data_inicio = hoje.replace(day=1)
        # Último dia do mês
        if hoje.month == 12:
            data_fim = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            data_fim = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
        from django.utils import timezone
        data_inicio = timezone.make_aware(datetime.combine(data_inicio, datetime.min.time()))
        data_fim = timezone.make_aware(datetime.combine(data_fim, datetime.max.time()))
    tipos_pessoa_novo = form.cleaned_data.get('tipo_pessoa_novo') if form.is_valid() else None
    status_pessoa_novo = form.cleaned_data.get('status_pessoa_novo') if form.is_valid() else None
    # Corrige datas para timezone-aware
    if data_inicio:
        data_inicio = timezone.make_aware(datetime.combine(data_inicio, datetime.min.time()))
    if data_fim:
        data_fim = timezone.make_aware(datetime.combine(data_fim, datetime.max.time()))

    # Eventos de entrada
    entrada_qs = TimelineEvent.objects.select_related('membro')
    if tipos_evento:
        entrada_qs = entrada_qs.filter(tipo_evento__in=tipos_evento)
    if data_inicio:
        entrada_qs = entrada_qs.filter(data__gte=data_inicio)
    if data_fim:
        entrada_qs = entrada_qs.filter(data__lte=data_fim)
    for evento in entrada_qs:
        evento.data_evento = getattr(evento, 'data', None)
        if hasattr(evento, 'tipo_pessoa_novo') and evento.tipo_evento == 'entrada':
            evento.valor_anterior = '-'
            evento.novo_valor = getattr(evento, 'tipo_pessoa_novo', None)
            nome = evento.membro.nome if hasattr(evento, 'membro') and evento.membro else 'Alguém'
            tipo = evento.novo_valor if evento.novo_valor else 'membro'
            evento.descricao_evento = f"{nome} entrou como {tipo}" if tipo else f"{nome} entrou"
        else:
            evento.valor_anterior = getattr(evento, 'valor_anterior', '-')
            evento.novo_valor = getattr(evento, 'novo_valor', '-')
            nome = evento.membro.nome if hasattr(evento, 'membro') and evento.membro else 'Alguém'
            tipo = evento.novo_valor if evento.novo_valor else 'membro'
            evento.descricao_evento = f"{nome} mudou para {tipo}" if tipo else f"{nome} teve uma mudança"
        if (
            hasattr(evento, 'membro') and evento.membro and getattr(evento.membro, 'nome', None)
            and (
                (hasattr(evento, 'valor_anterior') and evento.valor_anterior and evento.valor_anterior != '-') or
                (hasattr(evento, 'novo_valor') and evento.novo_valor and evento.novo_valor != '-')
            )
        ):
            eventos_timeline.append(evento)

    # Transições
    transicao_qs = StatusHistorico.objects.select_related('membro', 'status_pessoa_anterior', 'status_pessoa_novo', 'tipo_pessoa_anterior', 'tipo_pessoa_novo')
    if data_inicio:
        transicao_qs = transicao_qs.filter(data_transicao__gte=data_inicio)
    if data_fim:
        transicao_qs = transicao_qs.filter(data_transicao__lte=data_fim)
    if tipos_pessoa_novo:
        transicao_qs = transicao_qs.filter(tipo_pessoa_novo__in=tipos_pessoa_novo)
    if status_pessoa_novo:
        transicao_qs = transicao_qs.filter(status_pessoa_novo__in=status_pessoa_novo)
    for transicao in transicao_qs:
        transicao.data_evento = getattr(transicao, 'data_transicao', None)
        if hasattr(transicao, 'tipo_pessoa_anterior') and hasattr(transicao, 'tipo_pessoa_novo') and transicao.tipo_pessoa_anterior != transicao.tipo_pessoa_novo:
            transicao.get_tipo_evento_display = lambda: "Mudança de Tipo"
            transicao.tipo_evento = 'mudanca_tipo'
            transicao.valor_anterior = transicao.tipo_pessoa_anterior.nome if transicao.tipo_pessoa_anterior else '-'
            transicao.novo_valor = transicao.tipo_pessoa_novo.nome if transicao.tipo_pessoa_novo else '-'
            nome = transicao.membro.nome if hasattr(transicao, 'membro') and transicao.membro else 'Alguém'
            tipo = transicao.novo_valor if transicao.novo_valor else 'membro'
            transicao.descricao_evento = f"{nome} virou {tipo}"
        elif hasattr(transicao, 'status_pessoa_anterior') and hasattr(transicao, 'status_pessoa_novo') and transicao.status_pessoa_anterior != transicao.status_pessoa_novo:
            transicao.get_tipo_evento_display = lambda: "Mudança de Status"
            transicao.tipo_evento = 'mudanca_status'
            transicao.valor_anterior = transicao.status_pessoa_anterior.nome if transicao.status_pessoa_anterior else '-'
            transicao.novo_valor = transicao.status_pessoa_novo.nome if transicao.status_pessoa_novo else '-'
            nome = transicao.membro.nome if hasattr(transicao, 'membro') and transicao.membro else 'Alguém'
            status = transicao.novo_valor if transicao.novo_valor else 'ativo'
            transicao.descricao_evento = f"{nome} ficou {status}"
        else:
            transicao.get_tipo_evento_display = lambda: "Mudança de Tipo/Status"
            transicao.tipo_evento = 'mudanca_tipo_status'
            transicao.valor_anterior = '-'
            transicao.novo_valor = '-'
            nome = transicao.membro.nome if hasattr(transicao, 'membro') and transicao.membro else 'Alguém'
            transicao.descricao_evento = f"{nome} teve uma mudança"
        if (
            hasattr(transicao, 'membro') and transicao.membro and getattr(transicao.membro, 'nome', None)
            and (
                (hasattr(transicao, 'valor_anterior') and transicao.valor_anterior and transicao.valor_anterior != '-') or
                (hasattr(transicao, 'novo_valor') and transicao.novo_valor and transicao.novo_valor != '-')
            )
        ):
            eventos_timeline.append(transicao)

    # Agrupa apenas por data, sem pares (cada evento é um card)
    eventos_timeline = sorted(eventos_timeline, key=lambda e: e.data_evento, reverse=True)
    eventos_por_data = OrderedDict()
    for evento in eventos_timeline:
        data_str = evento.data_evento.strftime('%Y-%m-%d')
        if data_str not in eventos_por_data:
            eventos_por_data[data_str] = []
        eventos_por_data[data_str].append(evento)
    # Dados para gráfico (opcional)
    eventos_por_mes_tipo = defaultdict(lambda: defaultdict(int))
    for evento in eventos_timeline:
        mes = evento.data_evento.strftime('%Y-%m') if evento.data_evento else ''
        eventos_por_mes_tipo[mes][evento.get_tipo_evento_display()] += 1
    meses = sorted(eventos_por_mes_tipo.keys())
    tipos_set = set()
    for tipo_dict in eventos_por_mes_tipo.values():
        tipos_set.update(tipo_dict.keys())
    tipos_list = sorted(tipos_set)
    chart_labels = meses
    chart_datasets = []
    for tipo in tipos_list:
        data = [eventos_por_mes_tipo[mes].get(tipo, 0) for mes in meses]
        chart_datasets.append({
            'label': tipo,
            'data': data,
        })
    chart_data = {
        'labels': chart_labels,
        'datasets': chart_datasets,
    }
    from .models import StatusPessoa
    status_pessoa_list = StatusPessoa.objects.all().order_by('nome')
    context = {
        'eventos_por_data': eventos_por_data,
        'form': form,
        'chart_data_json': json.dumps(chart_data),
        'mostrar_anterior': request.GET.get('mostrar_anterior'),
        'status_pessoa_list': status_pessoa_list,
        'periodo_predefinido': request.GET.get('periodo_predefinido', 'mes_atual'),
    }
    logger = logging.getLogger('django')
    logger.warning(f"linha_do_tempo: eventos_timeline={len(eventos_timeline)}, eventos_por_data={len(eventos_por_data)}")
    print(f"linha_do_tempo: eventos_timeline={len(eventos_timeline)}, eventos_por_data={len(eventos_por_data)}")
    return render(request, 'secretaria/linha_do_tempo.html', context)


@require_GET
def autocomplete_nome_membro(request):
    """Retorna nomes de membros para autocomplete AJAX."""
    termo = request.GET.get('q', '').strip()
    results = []
    if termo:
        membros = Membro.objects.filter(nome__icontains=termo)[:20]
        results = [{'id': m.id, 'nome': m.nome} for m in membros]
    return JsonResponse({'results': results})
import shutil
# c:\Gereigreja\secretaria\views.py

from django.http import Http404
from .models import Membro, TipoPessoa, StatusPessoa, StatusHistorico






@login_required
def index(request):
    if request.user.is_superuser:
        return redirect('admin:index')

    if request.user.groups.filter(name='Membro Comum').exists() and not request.user.is_staff:
        return redirect('secretaria:portal_membro')

    ministerio = get_ministerio_or_error(request)
    allowed_churches_secretaria = get_allowed_churches_for_membros(request.user, ministerio)
    titulo_contextual = f"Visão Geral - {ministerio.nome_fantasia}"
    membros_para_relatorios = Membro.objects.none()

    if request.igreja_ativa and request.igreja_ativa in allowed_churches_secretaria:
        membros_para_relatorios = Membro.objects.filter(
            igreja=request.igreja_ativa,
            tipo_pessoa__nome__iexact="Membro",
            status_pessoa__nome__iexact="Ativo"
        )
        titulo_contextual = f"Visão Geral - Igreja: {request.igreja_ativa.nome_igreja}"
    elif allowed_churches_secretaria.exists():
        membros_para_relatorios = Membro.objects.filter(
            igreja__in=allowed_churches_secretaria,
            tipo_pessoa__nome__iexact="Membro",
            status_pessoa__nome__iexact="Ativo"
        )
        titulo_contextual += " (Consolidado)"
    elif is_admin_org(request.user):
        membros_para_relatorios = Membro.objects.filter(
            igreja__ministerio=ministerio,
            tipo_pessoa__nome__iexact="Membro",
            status_pessoa__nome__iexact="Ativo"
        )
        titulo_contextual += " (Ministério)"

    # Gráficos e cards
    membros_base_para_grafico_status = (
        Membro.objects.filter(igreja=request.igreja_ativa) if request.igreja_ativa and request.igreja_ativa in allowed_churches_secretaria
        else Membro.objects.filter(igreja__in=allowed_churches_secretaria) if allowed_churches_secretaria.exists()
        else Membro.objects.filter(igreja__ministerio=ministerio) if is_admin_org(request.user)
        else Membro.objects.none()
    )

    status_data_qs = membros_base_para_grafico_status.values('status_pessoa__nome').annotate(total=Count('chave')).order_by('status_pessoa__nome')
    status_data_list = [{'status': item['status_pessoa__nome'], 'total': item['total']} for item in status_data_qs if item['status_pessoa__nome']]

    genero_data_qs = membros_para_relatorios.values('genero').annotate(total=Count('chave'))
    genero_map = {'F': 'Feminino', 'M': 'Masculino', '': 'Não Informado', None: 'Não Informado'}
    aggregated_genero = {}
    for item in genero_data_qs:
        genero_display = genero_map.get(item['genero'], 'Não Informado')
        aggregated_genero[genero_display] = aggregated_genero.get(genero_display, 0) + item['total']
    genero_data_normalized = [{'genero': key, 'total': value} for key, value in aggregated_genero.items()]

    membros_com_nascimento = membros_para_relatorios.filter(nascimento__isnull=False).values_list('nascimento', flat=True)
    idades = []
    hoje_data = date.today()
    for nascimento in membros_com_nascimento:
        if nascimento:
            try:
                idade = hoje_data.year - nascimento.year - ((hoje_data.month, hoje_data.day) < (nascimento.month, nascimento.day))
                idades.append(idade)
            except AttributeError:
                logger.warning(f"Valor inesperado encontrado para data de nascimento ao calcular idade: {nascimento}")
        else:
            logger.warning("Valor None encontrado para nascimento mesmo após filtro isnull=False.")
    faixas = {
        '0-5 anos': 0,
        '6-10 anos': 0,
        '11-14 anos': 0,
        '15-17 anos': 0,
        '18-30 anos': 0,
        '31-50 anos': 0,
        '51-65 anos': 0,
        'Mais de 65 anos': 0,
        'Não Informado': membros_para_relatorios.filter(nascimento__isnull=True).count()
    }
    for idade_val in idades:
        if 0 <= idade_val <= 5:
            faixas['0-5 anos'] += 1
        elif 6 <= idade_val <= 10:
            faixas['6-10 anos'] += 1
        elif 11 <= idade_val <= 14:
            faixas['11-14 anos'] += 1
        elif 15 <= idade_val <= 17:
            faixas['15-17 anos'] += 1
        elif 18 <= idade_val <= 30:
            faixas['18-30 anos'] += 1
        elif 31 <= idade_val <= 50:
            faixas['31-50 anos'] += 1
        elif 51 <= idade_val <= 65:
            faixas['51-65 anos'] += 1
        elif idade_val > 65:
            faixas['Mais de 65 anos'] += 1
    faixa_etaria_data = [{'faixa_etaria': k, 'total': v} for k, v in faixas.items()]

    # Total de pessoas cadastradas (todos os tipos)
    total_pessoas = Membro.objects.all().count()
    # Total de membros ativos (apenas tipo 'Membro', exceto inativos)
    total_membros_ativos = membros_para_relatorios.filter(tipo_pessoa__nome__iexact='Membro').count()

    from datetime import timedelta
    trinta_dias_atras = hoje_data - timedelta(days=30)
    novos_membros_30_dias = membros_para_relatorios.filter(data_entrada__gte=trinta_dias_atras).count()
    aniversariantes_mes_atual_count = membros_para_relatorios.filter(nascimento__month=hoje_data.month).count()
    idades_para_media = []
    membros_ativos_com_nascimento = membros_para_relatorios.filter(nascimento__isnull=False).values_list('nascimento', flat=True)
    for nascimento_dt in membros_ativos_com_nascimento:
        if nascimento_dt:
            idade = hoje_data.year - nascimento_dt.year - ((hoje_data.month, hoje_data.day) < (nascimento_dt.month, nascimento_dt.day))
            idades_para_media.append(idade)
    media_idade_membros = round(sum(idades_para_media) / len(idades_para_media)) if idades_para_media else 0

    mes_atual = hoje_data.month
    dia_atual = hoje_data.day
    aniversariantes_qs = membros_para_relatorios.filter(nascimento__isnull=False).annotate(
        nascimento_month=Extract('nascimento', 'month'),
        nascimento_day=Extract('nascimento', 'day'),
        passed_this_year=Case(
            When(nascimento_month__lt=mes_atual, then=Value(True)),
            When(nascimento_month=mes_atual, nascimento_day__lt=dia_atual, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    ).order_by('passed_this_year', 'nascimento_month', 'nascimento_day')
    limite_aniversariantes = 10
    aniversariantes_proximos = list(aniversariantes_qs[:limite_aniversariantes])

    # Cards e alertas esperados pelo template
    # --- Pendências de cadastro ---
    pendencias_cadastro = membros_para_relatorios.filter(Q(nascimento__isnull=True) | Q(email__isnull=True) | Q(email=''))
    total_pendencias_cadastro = pendencias_cadastro.count()

    # --- Contas vencidas (financeiro) ---
    igrejas_ids = membros_para_relatorios.values_list('igreja_id', flat=True).distinct()
    from financeiro.models import ContaPagar
    contas_vencidas = ContaPagar.objects.filter(
        igreja_id__in=igrejas_ids,
        status='VEN'
    )
    total_contas_vencidas = contas_vencidas.count()
    valor_total_contas_vencidas = contas_vencidas.aggregate(total=Sum('valor'))['total'] or 0

    # --- Assinatura prestes a vencer (exemplo: menos de 10 dias) ---
    assinatura_alerta = None
    hoje = hoje_data
    if hasattr(ministerio, 'assinatura') and ministerio.assinatura:
        dias_restantes = (ministerio.assinatura.data_fim - hoje).days if ministerio.assinatura.data_fim else None
        if dias_restantes is not None and dias_restantes <= 10 and ministerio.assinatura.status != 'ATIVA':
            assinatura_alerta = {
                'dias_restantes': dias_restantes,
                'status': ministerio.assinatura.get_status_display(),
            }

    # --- Evolução de membros nos últimos 12 meses (filtrado pelo contexto do dashboard) ---
    meses = []
    membros_evolucao = []
    for i in range(11, -1, -1):
        mes_ref = (hoje.replace(day=1) - timedelta(days=30*i))
        ano_mes = mes_ref.strftime('%Y-%m')
        meses.append(ano_mes)
        membros_count = membros_para_relatorios.filter(
            data_entrada__lte=mes_ref.replace(day=28) + timedelta(days=4)
        ).count()
        membros_evolucao.append(membros_count)

    # --- Novos membros por mês (últimos 12 meses) ---
    novos_membros_por_mes = []
    for i in range(11, -1, -1):
        mes_ref = (hoje.replace(day=1) - timedelta(days=30*i))
        ano = mes_ref.year
        mes = mes_ref.month
        count = membros_para_relatorios.filter(
            data_entrada__year=ano,
            data_entrada__month=mes
        ).count()
        novos_membros_por_mes.append(count)

    # --- Aniversariantes (ontem, hoje, amanhã) ---
    ontem = hoje - timedelta(days=1)
    amanha = hoje + timedelta(days=1)
    aniversariantes_hoje = membros_para_relatorios.filter(nascimento__month=hoje.month, nascimento__day=hoje.day)
    aniversariantes_ontem = membros_para_relatorios.filter(nascimento__month=ontem.month, nascimento__day=ontem.day)
    aniversariantes_amanha = membros_para_relatorios.filter(nascimento__month=amanha.month, nascimento__day=amanha.day)

    context = {
        'status_data_json': json.dumps(status_data_list),
        'status_labels_json': json.dumps([item['status'] for item in status_data_list]),
        'status_values_json': json.dumps([item['total'] for item in status_data_list]),
        'genero_data_json': json.dumps(genero_data_normalized),
        'genero_labels_json': json.dumps([item['genero'] for item in genero_data_normalized]),
        'genero_values_json': json.dumps([item['total'] for item in genero_data_normalized]),
        'faixa_etaria_data_json': json.dumps(faixa_etaria_data),
        'faixa_labels_json': json.dumps([item['faixa_etaria'] for item in faixa_etaria_data]),
        'faixa_values_json': json.dumps([item['total'] for item in faixa_etaria_data]),
        # 'total_membros_dashboard' removido (não existe mais)
        'novos_membros_30_dias': novos_membros_30_dias,
        'aniversariantes_mes_atual_count': aniversariantes_mes_atual_count,
        'media_idade_membros': media_idade_membros,
        'ministerio': ministerio,
        'aniversariantes_proximos': aniversariantes_proximos,
        'titulo_pagina': titulo_contextual,
        'igreja_ativa_atual': request.igreja_ativa,
        # Cards e gráficos esperados pelo template:
        'total_membros_ativos': membros_para_relatorios.count(),
        'novos_membros_ultimo_mes': novos_membros_30_dias,
        'total_pendencias_cadastro': total_pendencias_cadastro,
        'total_contas_vencidas': total_contas_vencidas,
        'valor_total_contas_vencidas': valor_total_contas_vencidas,
        'assinatura_alerta': assinatura_alerta,
        'evolucao_meses': meses,
        'evolucao_membros': membros_evolucao,
        'novos_membros_por_mes': novos_membros_por_mes,
        'aniversariantes_ontem': aniversariantes_ontem,
        'aniversariantes_hoje': aniversariantes_hoje,
        'aniversariantes_amanha': aniversariantes_amanha,
    }
    return render(request, 'secretaria/index.html', context)




@login_required
def dashboard(request):
    # --- Pie Chart: Distribuição dinâmica de membros por tipo_pessoa ---
    tipos_pessoa_qs = TipoPessoa.objects.all().order_by('nome')
    membros_para_relatorios = Membro.objects.none()  # Garante inicialização para todos os fluxos
    # ... lógica de filtro de membros_para_relatorios ...
    # (deixe a lógica de filtro como está)
    # Após a lógica de filtro:
    # Total de membros ativos (apenas tipo 'Membro', exceto inativos)
    total_membros_ativos = membros_para_relatorios.count()
    # Total de pessoas cadastradas (todos os tipos)
    total_pessoas = Membro.objects.all().count()
    # membros_para_relatorios será definido após a lógica de filtro abaixo
    from datetime import date, timedelta
    hoje_data = date.today()

    # --- Evolução de membros, congregados, novos convertidos e visitantes nos últimos 12 meses ---
    from collections import defaultdict
    tipos_para_grafico = ['Membro', 'Congregado', 'Novo Convertido', 'Visitante']
    evolucao_por_tipo = defaultdict(list)
    meses_labels = []
    for i in range(11, -1, -1):
        mes_ref = hoje_data.replace(day=1) - timedelta(days=30*i)
        ano = mes_ref.year
        mes = mes_ref.month
        meses_labels.append(mes_ref.strftime('%b/%Y'))
        for tipo_nome in tipos_para_grafico:
            count = Membro.objects.filter(
                tipo_pessoa__nome__iexact=tipo_nome,
                data_entrada__year__lte=ano,
                data_entrada__month__lte=mes
            ).count()
            evolucao_por_tipo[tipo_nome].append(count)
    # --- Lógica completa baseada na função index para montar todos os dados do dashboard ---
    if request.user.is_superuser:
        return redirect('admin:index')

    if request.user.groups.filter(name='Membro Comum').exists() and not request.user.is_staff:
        return redirect('secretaria:portal_membro')

    ministerio = get_ministerio_or_error(request)
    allowed_churches_secretaria = get_allowed_churches_for_membros(request.user, ministerio)
    titulo_contextual = f"Visão Geral - {ministerio.nome_fantasia}"
    membros_para_relatorios = Membro.objects.none()

    if request.igreja_ativa and request.igreja_ativa in allowed_churches_secretaria:
        membros_para_relatorios = Membro.objects.filter(
            igreja=request.igreja_ativa,
            tipo_pessoa__nome__iexact="Membro",
            status_pessoa__nome__iexact="Ativo"
        )
        titulo_contextual = f"Visão Geral - Igreja: {request.igreja_ativa.nome_igreja}"
    elif allowed_churches_secretaria.exists():
        membros_para_relatorios = Membro.objects.filter(
            igreja__in=allowed_churches_secretaria,
            tipo_pessoa__nome__iexact="Membro",
            status_pessoa__nome__iexact="Ativo"
        )
        titulo_contextual += " (Consolidado)"
    elif is_admin_org(request.user):
        membros_para_relatorios = Membro.objects.filter(
            igreja__ministerio=ministerio,
            tipo_pessoa__nome__iexact="Membro",
            status_pessoa__nome__iexact="Ativo"
        )
        titulo_contextual += " (Ministério)"

    # Gráficos e cards
    membros_base_para_grafico_status = (
        Membro.objects.filter(igreja=request.igreja_ativa) if request.igreja_ativa and request.igreja_ativa in allowed_churches_secretaria
        else Membro.objects.filter(igreja__in=allowed_churches_secretaria) if allowed_churches_secretaria.exists()
        else Membro.objects.filter(igreja__ministerio=ministerio) if is_admin_org(request.user)
        else Membro.objects.none()
    )

    status_data_qs = membros_base_para_grafico_status.values('status_pessoa__nome').annotate(total=Count('chave')).order_by('status_pessoa__nome')
    status_data_list = [{'status': item['status_pessoa__nome'], 'total': item['total']} for item in status_data_qs if item['status_pessoa__nome']]

    genero_data_qs = membros_para_relatorios.values('genero').annotate(total=Count('chave'))
    genero_map = {'F': 'Feminino', 'M': 'Masculino', '': 'Não Informado', None: 'Não Informado'}
    aggregated_genero = {}
    for item in genero_data_qs:
        genero_display = genero_map.get(item['genero'], 'Não Informado')
        aggregated_genero[genero_display] = aggregated_genero.get(genero_display, 0) + item['total']
    genero_data_normalized = [{'genero': key, 'total': value} for key, value in aggregated_genero.items()]

    membros_com_nascimento = membros_para_relatorios.filter(nascimento__isnull=False).values_list('nascimento', flat=True)
    idades = []
    hoje_data = date.today()
    for nascimento in membros_com_nascimento:
        if nascimento:
            try:
                idade = hoje_data.year - nascimento.year - ((hoje_data.month, hoje_data.day) < (nascimento.month, nascimento.day))
                idades.append(idade)
            except AttributeError:
                logger.warning(f"Valor inesperado encontrado para data de nascimento ao calcular idade: {nascimento}")
        else:
            logger.warning("Valor None encontrado para nascimento mesmo após filtro isnull=False.")
    faixas = {
        '0-5 anos': 0,
        '6-10 anos': 0,
        '11-14 anos': 0,
        '15-17 anos': 0,
        '18-30 anos': 0,
        '31-50 anos': 0,
        '51-65 anos': 0,
        'Mais de 65 anos': 0,
        'Não Informado': membros_para_relatorios.filter(nascimento__isnull=True).count()
    }
    for idade_val in idades:
        if 0 <= idade_val <= 5:
            faixas['0-5 anos'] += 1
        elif 6 <= idade_val <= 10:
            faixas['6-10 anos'] += 1
        elif 11 <= idade_val <= 14:
            faixas['11-14 anos'] += 1
        elif 15 <= idade_val <= 17:
            faixas['15-17 anos'] += 1
        elif 18 <= idade_val <= 30:
            faixas['18-30 anos'] += 1
        elif 31 <= idade_val <= 50:
            faixas['31-50 anos'] += 1
        elif 51 <= idade_val <= 65:
            faixas['51-65 anos'] += 1
        elif idade_val > 65:
            faixas['Mais de 65 anos'] += 1
    faixa_etaria_data = [{'faixa_etaria': k, 'total': v} for k, v in faixas.items()]

    # Total de pessoas cadastradas (todos os tipos)
    total_pessoas = Membro.objects.all().count()
    # Total de membros ativos (apenas tipo 'Membro', exceto inativos)
    total_membros_ativos = membros_para_relatorios.filter(tipo_pessoa__nome__iexact='Membro').count()

    from datetime import timedelta
    trinta_dias_atras = hoje_data - timedelta(days=30)
    novos_membros_30_dias = membros_para_relatorios.filter(data_entrada__gte=trinta_dias_atras).count()
    aniversariantes_mes_atual_count = membros_para_relatorios.filter(nascimento__month=hoje_data.month).count()
    idades_para_media = []
    membros_ativos_com_nascimento = membros_para_relatorios.filter(nascimento__isnull=False).values_list('nascimento', flat=True)
    for nascimento_dt in membros_ativos_com_nascimento:
        if nascimento_dt:
            idade = hoje_data.year - nascimento_dt.year - ((hoje_data.month, hoje_data.day) < (nascimento_dt.month, nascimento_dt.day))
            idades_para_media.append(idade)
    media_idade_membros = round(sum(idades_para_media) / len(idades_para_media)) if idades_para_media else 0

    mes_atual = hoje_data.month
    dia_atual = hoje_data.day
    aniversariantes_qs = membros_para_relatorios.filter(nascimento__isnull=False).annotate(
        nascimento_month=Extract('nascimento', 'month'),
        nascimento_day=Extract('nascimento', 'day'),
        passed_this_year=Case(
            When(nascimento_month__lt=mes_atual, then=Value(True)),
            When(nascimento_month=mes_atual, nascimento_day__lt=dia_atual, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    ).order_by('passed_this_year', 'nascimento_month', 'nascimento_day')
    limite_aniversariantes = 10
    aniversariantes_proximos = list(aniversariantes_qs[:limite_aniversariantes])

    # Cards e alertas esperados pelo template
    # --- Pendências de cadastro ---
    pendencias_cadastro = membros_para_relatorios.filter(Q(nascimento__isnull=True) | Q(email__isnull=True) | Q(email=''))
    total_pendencias_cadastro = pendencias_cadastro.count()

    # --- Contas vencidas (financeiro) ---
    igrejas_ids = membros_para_relatorios.values_list('igreja_id', flat=True).distinct()
    from financeiro.models import ContaPagar
    contas_vencidas = ContaPagar.objects.filter(
        igreja_id__in=igrejas_ids,
        status='VEN'
    )
    total_contas_vencidas = contas_vencidas.count()
    valor_total_contas_vencidas = contas_vencidas.aggregate(total=Sum('valor'))['total'] or 0

    # --- Assinatura prestes a vencer (exemplo: menos de 10 dias) ---
    assinatura_alerta = None
    hoje = hoje_data
    if hasattr(ministerio, 'assinatura') and ministerio.assinatura:
        dias_restantes = (ministerio.assinatura.data_fim - hoje).days if ministerio.assinatura.data_fim else None
        if dias_restantes is not None and dias_restantes <= 10 and ministerio.assinatura.status != 'ATIVA':
            assinatura_alerta = {
                'dias_restantes': dias_restantes,
                'status': ministerio.assinatura.get_status_display(),
            }

    # --- Evolução de membros nos últimos 12 meses (filtrado pelo contexto do dashboard) ---
    meses = []
    membros_evolucao = []
    for i in range(11, -1, -1):
        mes_ref = (hoje.replace(day=1) - timedelta(days=30*i))
        ano_mes = mes_ref.strftime('%Y-%m')
        meses.append(ano_mes)
        membros_count = membros_para_relatorios.filter(
            data_entrada__lte=mes_ref.replace(day=28) + timedelta(days=4)
        ).count()
        membros_evolucao.append(membros_count)

    # --- Novos membros por mês (últimos 12 meses) ---
    novos_membros_por_mes = []
    for i in range(11, -1, -1):
        mes_ref = (hoje.replace(day=1) - timedelta(days=30*i))
        ano = mes_ref.year
        mes = mes_ref.month
        count = membros_para_relatorios.filter(
            data_entrada__year=ano,
            data_entrada__month=mes
        ).count()
        novos_membros_por_mes.append(count)

    # --- Aniversariantes (ontem, hoje, amanhã) ---
    ontem = hoje - timedelta(days=1)
    amanha = hoje + timedelta(days=1)
    aniversariantes_hoje = membros_para_relatorios.filter(nascimento__month=hoje.month, nascimento__day=hoje.day)
    aniversariantes_ontem = membros_para_relatorios.filter(nascimento__month=ontem.month, nascimento__day=ontem.day)
    aniversariantes_amanha = membros_para_relatorios.filter(nascimento__month=amanha.month, nascimento__day=amanha.day)

    # Pie Chart: distribuição dinâmica de membros por tipo_pessoa
    tipos_pessoa_qs = TipoPessoa.objects.all().order_by('nome')
    if request.igreja_ativa and request.igreja_ativa in allowed_churches_secretaria:
        membros_para_grafico_tipo = Membro.objects.filter(igreja=request.igreja_ativa)
    elif allowed_churches_secretaria.exists():
        membros_para_grafico_tipo = Membro.objects.filter(igreja__in=allowed_churches_secretaria)
    elif is_admin_org(request.user):
        membros_para_grafico_tipo = Membro.objects.filter(igreja__ministerio=ministerio)
    else:
        membros_para_grafico_tipo = Membro.objects.none()

    membros_por_tipo = (
        membros_para_grafico_tipo.values('tipo_pessoa__nome')
        .annotate(total=Count('chave'))
        .order_by('tipo_pessoa__nome')
    )
    pie_labels = []
    pie_values = []
    for tipo in tipos_pessoa_qs:
        found = next((item for item in membros_por_tipo if item['tipo_pessoa__nome'] == tipo.nome), None)
        pie_labels.append(tipo.nome)
        pie_values.append(found['total'] if found else 0)

    # --- Participação por Categoria de Evento ---
    from eventos.models import ParticipacaoEvento, Evento
    eventos_ids = []
    if request.igreja_ativa and request.igreja_ativa in allowed_churches_secretaria:
        eventos_ids = list(Evento.objects.filter(igreja=request.igreja_ativa).values_list('id', flat=True))
    elif allowed_churches_secretaria.exists():
        eventos_ids = list(Evento.objects.filter(igreja__in=allowed_churches_secretaria).values_list('id', flat=True))
    elif is_admin_org(request.user):
        eventos_ids = list(Evento.objects.filter(igreja__ministerio=ministerio).values_list('id', flat=True))
    participacoes_qs = ParticipacaoEvento.objects.filter(status__in=["CONFIRMADO", "PRESENTE", "AUSENTE"], evento_id__in=eventos_ids)
    participacoes_por_categoria = (
        participacoes_qs.values('evento__tipo')
        .annotate(total=Count('id'))
        .order_by('evento__tipo')
    )
    tipo_dict = dict(Evento.TIPO_EVENTO_CHOICES)
    categoria_labels = []
    categoria_values = []
    for item in participacoes_por_categoria:
        tipo = item['evento__tipo']
        label = tipo_dict.get(tipo, tipo.title())
        categoria_labels.append(label)
        categoria_values.append(item['total'])

    # --- Cards adicionais ---
    # Total de pessoas cadastradas (todos os tipos)
    total_membros = Membro.objects.all().count()
    # Total de visitantes
    total_visitantes = Membro.objects.filter(tipo_pessoa__nome__iexact='Visitante').count()
    # Total de cargos
    total_cargos = Cargo.objects.all().count()
    # Total de grupos/casas
    total_grupos_casa = GrupoCasa.objects.all().count()
    # Total de relatórios (usando reuniões de membros como proxy)
    total_relatorios = Membro.objects.filter(tipo_pessoa__nome__in=['Membro', 'Obreiro'], status_pessoa__nome__in=['Ativo', 'Em Disciplina']).count()
    # Total de acompanhamentos de visita
    total_acompanhamentos = AcompanhamentoVisita.objects.all().count()
    # Total de tags
    total_tags = Tag.objects.all().count()
    # Total de associações usuário-membro
    total_associacoes = Membro.objects.filter(usuario__isnull=False).count()

    context = {
        'status_data_json': json.dumps(status_data_list),
        'status_labels_json': json.dumps([item['status'] for item in status_data_list]),
        'status_values_json': json.dumps([item['total'] for item in status_data_list]),
        'genero_data_json': json.dumps(genero_data_normalized),
        'genero_labels_json': json.dumps([item['genero'] for item in genero_data_normalized]),
        'genero_values_json': json.dumps([item['total'] for item in genero_data_normalized]),
        'faixa_etaria_data_json': json.dumps(faixa_etaria_data),
        'faixa_labels_json': json.dumps([item['faixa_etaria'] for item in faixa_etaria_data]),
        'faixa_values_json': json.dumps([item['total'] for item in faixa_etaria_data]),
        'novos_membros_30_dias': novos_membros_30_dias,
        'aniversariantes_mes_atual_count': aniversariantes_mes_atual_count,
        'media_idade_membros': media_idade_membros,
        'ministerio': ministerio,
        'aniversariantes_proximos': aniversariantes_proximos,
        'titulo_pagina': titulo_contextual,
        'igreja_ativa_atual': request.igreja_ativa,
        'total_membros_ativos': membros_para_relatorios.count(),
        'novos_membros_ultimo_mes': novos_membros_30_dias,
        'total_pendencias_cadastro': total_pendencias_cadastro,
        'total_contas_vencidas': total_contas_vencidas,
        'valor_total_contas_vencidas': valor_total_contas_vencidas,
        'assinatura_alerta': assinatura_alerta,
        # Gráficos de evolução (garante que *_json estão presentes)
        'evolucao_meses_labels_json': json.dumps(meses_labels),
        'evolucao_membros_json': json.dumps(evolucao_por_tipo['Membro']),
        'evolucao_congregados_json': json.dumps(evolucao_por_tipo['Congregado']),
        'evolucao_novos_convertidos_json': json.dumps(evolucao_por_tipo['Novo Convertido']),
        'evolucao_visitantes_json': json.dumps(evolucao_por_tipo['Visitante']),
        # Pie chart
        'pie_labels_json': json.dumps(pie_labels),
        'pie_values_json': json.dumps(pie_values),
        # Categoria evento
        'categoria_evento_labels_json': json.dumps(categoria_labels),
        'categoria_evento_values_json': json.dumps(categoria_values),
        # --- Cards adicionais ---
        'total_membros': total_membros,
        'total_visitantes': total_visitantes,
        'total_cargos': total_cargos,
        'total_grupos_casa': total_grupos_casa,
        'total_relatorios': total_relatorios,
        'total_acompanhamentos': total_acompanhamentos,
        'total_tags': total_tags,
        'total_associacoes': total_associacoes,
    }
    # Removido bloco de debug dos dados JSON do dashboard
    return render(request, 'secretaria/dashboard.html', context)


@login_required
def lista_grupos_casa(request):
    """Lista de GrupoCasa (casas/famílias) com escopo por igreja/ministerio semelhante a outras views."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)

    qs = []
    if request.igreja_ativa and request.igreja_ativa in allowed_churches:
        qs = GrupoCasa.objects.filter(igreja=request.igreja_ativa)
    elif allowed_churches.exists():
        qs = GrupoCasa.objects.filter(igreja__in=allowed_churches)
    elif is_admin_org(request.user):
        qs = GrupoCasa.objects.filter(igreja__ministerio=ministerio)
    else:
        qs = GrupoCasa.objects.none()

    q = request.GET.get('q')
    if q:
        qs = qs.filter(Q(rua__icontains=q) | Q(nome__icontains=q) | Q(bairro__icontains=q) | Q(cep__icontains=q))

    qs = qs.order_by('rua', 'numero')
    # Permissão para exibir botão de agrupamento na UI
    can_agrupar = is_admin_or_pastor(request.user)
    # Permissão para editar grupos (pode ser mais restrita se necessário)
    try:
        can_edit_grupo = is_admin_or_pastor(request.user) or has_membro_edit_permission(request.user)
    except Exception:
        can_edit_grupo = is_admin_or_pastor(request.user)

    context = {
        'grupos': qs.select_related('igreja', 'responsavel'),
        'titulo_pagina': 'Grupos / Casas',
        'query': q,
        'ministerio': ministerio,
        'igreja_selecionada': str(request.igreja_ativa.pk) if hasattr(request, 'igreja_ativa') and request.igreja_ativa else (request.GET.get('igreja') or ''),
        'can_agrupar_grupos': can_agrupar,
        'can_edit_grupo': can_edit_grupo,
    }
    return render(request, 'secretaria/grupocasa_list.html', context)



@login_required
@user_passes_test(is_admin_or_pastor)
def agrupar_grupos_preview(request):
    """Preview das mudanças que o agrupamento faria. Mostra agrupamentos detectados por endereço."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    from .models import Membro
    from .utils import agrupar_preview_for_queryset

    if request.igreja_ativa and request.igreja_ativa in allowed_churches:
        people_qs = Membro.objects.filter(igreja=request.igreja_ativa)
    elif allowed_churches.exists():
        people_qs = Membro.objects.filter(igreja__in=allowed_churches)
    elif is_admin_org(request.user):
        people_qs = Membro.objects.filter(igreja__ministerio=ministerio)
    else:
        people_qs = Membro.objects.none()

    # considerar apenas pessoas com endereço mínimo (rua ou cep)
    people_qs = people_qs.filter(Q(rua__isnull=False) | Q(cep__isnull=False)).order_by('rua', 'numero_casa')

    rows = agrupar_preview_for_queryset(people_qs)
    # filtrar apenas grupos com 2+ pessoas para aplicar
    to_apply = [r for r in rows if r.get('count', 0) >= 2]

    context = {
        'rows': rows,
        'to_apply_count': len(to_apply),
        'titulo_pagina': 'Preview: Agrupar Grupos / Casas por Endereço',
    }
    return render(request, 'secretaria/agrupar_grupos_preview.html', context)


@login_required
@user_passes_test(is_admin_or_pastor)
def agrupar_grupos_apply(request):
    """Aplica o agrupamento (cria GrupoCasa e associa pessoas).
    Esta view recalcula o preview e aplica apenas os agrupamentos com 2+ pessoas.
    """
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    from .models import Membro
    from .utils import agrupar_preview_for_queryset, agrupar_apply_from_preview

    if request.igreja_ativa and request.igreja_ativa in allowed_churches:
        people_qs = Membro.objects.filter(igreja=request.igreja_ativa)
    elif allowed_churches.exists():
        people_qs = Membro.objects.filter(igreja__in=allowed_churches)
    elif is_admin_org(request.user):
        people_qs = Membro.objects.filter(igreja__ministerio=ministerio)
    else:
        people_qs = Membro.objects.none()

    people_qs = people_qs.filter(Q(rua__isnull=False) | Q(cep__isnull=False)).order_by('rua', 'numero_casa')
    rows = agrupar_preview_for_queryset(people_qs)
    to_apply = [r for r in rows if r.get('count', 0) >= 2]

    result = {'created': 0, 'updated': 0}
    if to_apply:
        result = agrupar_apply_from_preview(to_apply)
        messages.success(request, f"Agrupamento aplicado: {result.get('created', 0)} grupos criados, {result.get('updated', 0)} pessoas atualizadas.")
    else:
        messages.info(request, 'Nenhum agrupamento com 2+ pessoas detectado; nada foi aplicado.')

    return redirect('secretaria:lista_grupos_casa')


@login_required
@user_passes_test(is_admin_or_pastor)
def reagrupar_grupo_casa(request, grupo_id):
    """Reagrupar moradores do GrupoCasa: recalcula preview para as pessoas deste grupo e aplica apenas os agrupamentos relevantes.
    Fluxo seguro: só executa para membros do próprio grupo/igreja no escopo do usuário.
    """
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    grupo = get_object_or_404(GrupoCasa, pk=grupo_id)

    # Verifica escopo
    try:
        if not (request.igreja_ativa and request.igreja_ativa in allowed_churches) and allowed_churches.exists():
            if grupo.igreja not in allowed_churches and not is_admin_org(request.user):
                raise PermissionError('Sem permissão para reagrupar este grupo')
    except PermissionError:
        raise Http404()

    from .models import Membro
    from .utils import agrupar_preview_for_queryset, agrupar_apply_from_preview

    people_qs = Membro.objects.filter(grupo_casa=grupo)
    # considerar apenas com endereço mínimo
    people_qs = people_qs.filter(Q(rua__isnull=False) | Q(cep__isnull=False)).order_by('rua', 'numero_casa')

    rows = agrupar_preview_for_queryset(people_qs)
    to_apply = [r for r in rows if r.get('count', 0) >= 2]

    if to_apply:
        result = agrupar_apply_from_preview(to_apply)
        messages.success(request, f"Reagrupamento aplicado: {result.get('created',0)} grupos criados, {result.get('updated',0)} pessoas atualizadas.")
    else:
        messages.info(request, 'Nenhum agrupamento com 2+ pessoas detectado para este grupo; nada foi aplicado.')

    return redirect('secretaria:detalhe_grupo_casa', grupo_id=grupo.id)


@login_required
def detalhe_grupo_casa(request, grupo_id):
    """Detalhe de GrupoCasa; GET mostra membros e histórico de visitas, POST cria VisitaGrupoCasa e opcionalmente AcompanhamentoVisita para todos."""
    grupo = get_object_or_404(GrupoCasa, pk=grupo_id)
    # verificar permissão/escopo similar a outras views
    try:
        ministerio = get_ministerio_or_error(request)
        allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
        if not (request.igreja_ativa and request.igreja_ativa in allowed_churches) and allowed_churches.exists():
            if grupo.igreja not in allowed_churches and not is_admin_org(request.user):
                raise PermissionError('Sem permissão para acessar este grupo')
    except PermissionError:
        raise Http404()

    membros = grupo.pessoas.all().select_related('tipo_pessoa', 'status_pessoa')
    visitas = grupo.visitas.all().order_by('-data')[:50]

    if request.method == 'POST':
        # criar visita
        from .forms_grupocasa import VisitaGrupoCasaForm
        form = VisitaGrupoCasaForm(request.POST)
        if form.is_valid():
            from django.db import transaction
            with transaction.atomic():
                visita = form.save(commit=False)
                visita.grupo_casa = grupo
                visita.responsavel = request.user
                visita.num_membros = membros.count()
                visita.save()
                # criar acompanhamentos se solicitado
                if form.cleaned_data.get('marcar_todos'):
                    acompanhamentos = []
                    for p in membros:
                        acompanhamentos.append(AcompanhamentoVisita(
                            membro=p,
                            responsavel=request.user,
                            visita_grupo_casa=visita,
                            tipo_contato='visita',
                            resultado=form.cleaned_data.get('resultado') or '',
                            observacao=form.cleaned_data.get('observacao') or ''
                        ))
                    AcompanhamentoVisita.objects.bulk_create(acompanhamentos)
                messages.success(request, 'Visita registrada com sucesso!')
                return redirect('secretaria:detalhe_grupo_casa', grupo_id=grupo.id)
        else:
            messages.error(request, 'Erro ao registrar visita. Verifique os campos.')
    else:
        from .forms_grupocasa import VisitaGrupoCasaForm
        form = VisitaGrupoCasaForm()

    # Permissão para aplicar agrupamento localmente (reagrupar moradores)
    try:
        can_agrupar_local = is_admin_or_pastor(request.user)
    except Exception:
        can_agrupar_local = False

    context = {
        'grupo': grupo,
        'membros': membros,
        'visitas': visitas,
        'form': form,
        'titulo_pagina': f'Grupo / Casa: {grupo.nome or (grupo.rua or "")}',
        'ministerio': ministerio,
        'can_edit_grupo': (is_admin_or_pastor(request.user) or has_membro_edit_permission(request.user)),
        'can_agrupar_local': can_agrupar_local,
    }
    return render(request, 'secretaria/grupocasa_detail.html', context)


@login_required
@user_passes_test(is_admin_or_pastor)
def criar_grupo_casa(request):
    """Cria um novo GrupoCasa. Se houver `request.igreja_ativa`, vincula automaticamente."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)

    if request.method == 'POST':
        form = GrupoCasaForm(request.POST)
        if form.is_valid():
            grupo = form.save(commit=False)
            # determinar igreja alvo
            if hasattr(request, 'igreja_ativa') and request.igreja_ativa and request.igreja_ativa in allowed_churches:
                grupo.igreja = request.igreja_ativa
            else:
                # se só houver uma igreja permitida, usar ela
                try:
                    if getattr(allowed_churches, 'count', None) and allowed_churches.count() == 1:
                        grupo.igreja = allowed_churches.first()
                except Exception:
                    pass
            grupo.responsavel = request.user
            if not getattr(grupo, 'igreja', None):
                messages.error(request, 'Não foi possível determinar a igreja para o novo grupo. Verifique sua seleção de igreja/permissões.')
            else:
                grupo.save()
                messages.success(request, 'Grupo/Casa criado com sucesso!')
                return redirect('secretaria:detalhe_grupo_casa', grupo_id=grupo.id)
    else:
        form = GrupoCasaForm()

    context = {
        'form': form,
        'titulo_pagina': 'Criar Novo Grupo / Casa',
        'ministerio': ministerio,
    }
    return render(request, 'secretaria/grupocasa_form.html', context)


@login_required
@user_passes_test(is_admin_or_pastor)
def editar_grupo_casa(request, grupo_id):
    """Editar um GrupoCasa existente. Sem migrações de modelo — apenas edição via form."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user, ministerio)
    grupo = get_object_or_404(GrupoCasa, pk=grupo_id)

    # Verifica escopo: só permitir se o grupo pertence às igrejas permitidas do usuário
    try:
        if not (request.igreja_ativa and request.igreja_ativa in allowed_churches) and allowed_churches.exists():
            if grupo.igreja not in allowed_churches and not is_admin_org(request.user):
                raise PermissionError('Sem permissão para editar este grupo')
    except PermissionError:
        raise Http404()

    if request.method == 'POST':
        form = GrupoCasaForm(request.POST, instance=grupo)
        if form.is_valid():
            grupo_editado = form.save(commit=False)
            # Permitir alteração de igreja somente se o usuário tiver permissão nessa igreja
            try:
                if not is_admin_org(request.user) and getattr(grupo_editado, 'igreja', None) and grupo_editado.igreja not in allowed_churches:
                    messages.error(request, 'Igreja selecionada inválida para sua permissão.')
                else:
                    grupo_editado.save()
                    messages.success(request, 'Grupo/Casa atualizado com sucesso!')
                    return redirect('secretaria:detalhe_grupo_casa', grupo_id=grupo.id)
            except Exception as e:
                logger.exception('Erro ao salvar grupo: %s', e)
                messages.error(request, f'Erro ao salvar o grupo: {e}')
    else:
        form = GrupoCasaForm(instance=grupo)

    context = {
        'form': form,
        'titulo_pagina': f'Editar Grupo / Casa: {grupo.nome or grupo.rua}',
        'ministerio': ministerio,
        'grupo': grupo,
    }
    return render(request, 'secretaria/grupocasa_form.html', context)


@check_permission(has_membro_view_permission, login_url_name='login')
def lista_membros(request): # noqa: E302
    # Filtro por nome/apelido (busca parcial)
    nome_apelido = request.GET.get('nome_apelido')
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)

    # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
    if request.igreja_ativa and request.igreja_ativa in allowed_churches:
        membros_queryset = Membro.objects.filter(igreja=request.igreja_ativa)
    elif allowed_churches.exists():
        membros_queryset = Membro.objects.filter(igreja__in=allowed_churches)
    elif is_admin_org(request.user): # Admin do Minist. sem igrejas no perfil e sem igreja ativa
        membros_queryset = Membro.objects.filter(igreja__ministerio=ministerio)
    else:
        membros_queryset = Membro.objects.none()
    # --- Fim Lógica de Filtragem Inicial ---

    if nome_apelido:
        membros_queryset = membros_queryset.filter(
            Q(nome__icontains=nome_apelido) | Q(apelido__icontains=nome_apelido)
        )

    membros_queryset = membros_queryset.select_related('igreja', 'tipo_pessoa', 'status_pessoa').order_by('nome') # Adicionado tipo_pessoa, status_pessoa

    # Paginação igual associar_usuarios_membros
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = request.GET.get('page', 1)
    paginator = Paginator(membros_queryset, 25)  # 25 membros por página
    try:
        membros_page = paginator.page(page)
    except PageNotAnInteger:
        membros_page = paginator.page(1)
    except EmptyPage:
        membros_page = paginator.page(paginator.num_pages)


    query = request.GET.get('q')
    if query:
        membros_queryset = membros_queryset.filter(
            Q(nome__icontains=query) | Q(apelido__icontains=query)
        )
    # Filtro GET de igreja na página (só se nenhuma igreja ativa globalmente)
    igreja_id_get = request.GET.get('igreja')
    if igreja_id_get and not request.igreja_ativa:
        if allowed_churches.filter(pk=igreja_id_get).exists() or is_admin_org(request.user):
            membros_queryset = membros_queryset.filter(igreja_id=igreja_id_get)

    can_edit = has_membro_edit_permission(request.user)
    igrejas_para_filtro_template = allowed_churches if not request.igreja_ativa else Igreja.objects.filter(pk=request.igreja_ativa.pk)

    from .models import TipoPessoa, StatusPessoa, Tag
    tipos_pessoa = TipoPessoa.objects.all().order_by('nome')
    status_pessoa = StatusPessoa.objects.filter(nome__in=["Ativo", "Desligado", "Em Disciplina", "Inativo"]).order_by('nome')

    # Filtros extras
    tipo_id = request.GET.get('tipo')
    if tipo_id and tipo_id.isdigit():
        membros_queryset = membros_queryset.filter(tipo_pessoa_id=tipo_id)
    status_id = request.GET.get('status')
    if status_id and status_id.isdigit():
        membros_queryset = membros_queryset.filter(status_pessoa_id=status_id)
    genero = request.GET.get('genero')
    if genero:
        membros_queryset = membros_queryset.filter(genero=genero)

    # --- FILTRO POR TAGS ---
    tag_ids = [tid for tid in request.GET.getlist('tags') if tid and tid.isdigit()]
    if tag_ids:
        membros_queryset = membros_queryset.filter(tags__in=tag_ids).distinct()
    todas_tags = Tag.objects.all().order_by('nome')

    context = {
        'membros': membros_page,
        'ministerio': ministerio,
        'query': query,
        'can_edit_membros': can_edit,
        'titulo_pagina': f"Lista de Membros{': ' + request.igreja_ativa.nome_igreja if request.igreja_ativa else ' (Consolidado)'}",
        'igrejas_org': igrejas_para_filtro_template, # Para o filtro da página
        'igreja_selecionada': str(request.igreja_ativa.pk) if request.igreja_ativa else igreja_id_get,
        'tipos_pessoa': tipos_pessoa,
        'status_pessoa': status_pessoa,
        'todas_tags': todas_tags,
        'tags_selecionadas': tag_ids,
        'paginator': paginator,
        'page_obj': membros_page,
    }
    return render(request, 'secretaria/lista_membros.html', context)


@check_permission(has_membro_edit_permission, login_url_name='login')
def editar_membro(request, membro_id): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    membro = get_object_or_404(Membro, pk=membro_id, igreja__in=allowed_churches)
     # DEBUG: Verificar o membro que está sendo editado
    
     # Tenta encontrar o User e PerfilUsuario associados ao membro
    user_associado = User.objects.filter(email__iexact=membro.email, perfil__ministerio=ministerio).first()
    perfil_associado = user_associado.perfil if user_associado else None
    # print(f"DEBUG [editar_membro]: Editando membro: {membro.nome} (ID: {membro.pk})") # Removido para produção

    if request.method == 'POST':
        # Ao editar, a igreja do membro não deve mudar via seletor global, mas o form precisa das allowed_churches
        form = MembroForm(request.POST, request.FILES, instance=membro, 
                          ministerio=ministerio, 
                          user=request.user, 
                          allowed_churches=allowed_churches, # noqa
                          igreja_inicial=membro.igreja) # Passa a igreja atual do membro 
    # print(f"DEBUG POST - request.POST: {request.POST}") # Removido para produção
        # --- Lógica para o formulário de gerenciamento de usuário ---
        user_management_form = MembroUserManagementForm(
            request.POST,
            membro_instance=membro,
            ministerio=ministerio,
            user_instance=user_associado,
            perfil_instance=perfil_associado
        )

        if 'submit_membro_form' in request.POST: # Se o formulário principal do membro foi submetido
            if form.is_valid():
                # print(f"DEBUG POST - form.cleaned_data: {form.cleaned_data}") # Removido para produção
                nascimento_do_form = form.cleaned_data.get('nascimento')
                # print(f"DEBUG POST - Nascimento do form.cleaned_data: {nascimento_do_form}, Tipo: {type(nascimento_do_form)}") # Removido para produção
                try:
                    membro_editado = form.save(commit=False)
                    # print(f"DEBUG POST - membro_editado.nascimento ANTES do save: {membro_editado.nascimento}, Tipo: {type(membro_editado.nascimento)}") # Removido para produção
                    if not is_admin_org(request.user) and membro_editado.igreja not in allowed_churches:
                        messages.error(request, "Erro: Igreja selecionada inválida para sua permissão.")
                   
                   
                    else:
                        form.save(commit=True) # Salva via formulário, garantindo tags
                        messages.success(request, f'Membro "{membro_editado.nome}" atualizado com sucesso!')
                        # Verifica o VALOR do botão pressionado, não a presença de uma chave.
                        # O botão "Salvar e Continuar" envia o valor "_save_and_continue".
                        # O botão "Salvar Alterações" não tem valor, então o get() retornará None.
                        if request.POST.get('submit_membro_form') == '_save_and_continue':
                            return redirect('secretaria:editar_membro', membro_id=membro_id)
                        else:
                            return redirect('secretaria:lista_membros')
                except Exception as e:
                    # print(f"DEBUG POST - Exceção ao salvar: {e}") # Removido para produção

                    logger.exception(f"Erro ao salvar edição do membro {membro_id} para ministério {ministerio.id}")
                    messages.error(request, f"Ocorreu um erro ao salvar as alterações: {e}")
            else:
                # print(f"DEBUG POST - Membro Form inválido. Erros: {form.errors.as_json()}") # Removido para produção
                messages.error(request, "Erro ao atualizar membro. Verifique os campos.")

        elif 'submit_user_management_form' in request.POST: # Se o formulário de gerenciamento de usuário foi submetido
            if user_management_form.is_valid():
                try:
                    with transaction.atomic():
                        # 1. Criar ou obter o User
                        if not user_associado:
                            # Se não existe User, cria um novo com senha aleatória e inativa
                            # O usuário terá que usar o fluxo de "esqueci a senha" para definir a primeira senha
                            random_password = get_random_string(length=20)
                            user_associado = User.objects.create_user(
                                username=user_management_form.cleaned_data['email_usuario'],
                                email=user_management_form.cleaned_data['email_usuario'],
                                password=random_password,
                                is_active=user_management_form.cleaned_data.get('is_active', False),
                                first_name=membro.nome, # Usa o nome do membro
                                last_name=membro.apelido or ''
                            )
                            messages.info(request, "Nova conta de usuário criada. O usuário precisará usar a função 'Esqueci a senha' para definir sua primeira senha.")
                        
                        # 2. Atualizar dados do User
                        user_associado.is_active = user_management_form.cleaned_data['is_active']
                        user_associado.is_staff = user_management_form.cleaned_data['is_staff']
                        user_associado.save()

                        # 3. Atualizar grupos do User
                        user_associado.groups.set(user_management_form.cleaned_data['grupos'])

                        # 4. Criar ou obter PerfilUsuario e atualizar igrejas permitidas
                        perfil_associado, created = PerfilUsuario.objects.get_or_create(user=user_associado, defaults={'ministerio': ministerio})
                        perfil_associado.igrejas_permitidas.set(user_management_form.cleaned_data['igrejas_permitidas'])
                        perfil_associado.ministerio = ministerio # Garante que a ministério está correta
                        perfil_associado.save()

                    messages.success(request, f"Acesso do usuário {user_associado.username} atualizado com sucesso!")
                    # Redireciona de volta para a mesma página, na aba correta
                    redirect_url = reverse('secretaria:editar_membro', args=[membro_id]) + '?tab=acesso-sistema'
                    return redirect(redirect_url)
                except Exception as e:
                    logger.exception(f"Erro ao gerenciar acesso do usuário para membro {membro_id}: {e}")
                    messages.error(request, f"Erro ao gerenciar acesso do usuário: {e}")
                    # RECARREGA O FORMULÁRIO PRINCIPAL PARA NÃO PERDER OS DADOS
                form = MembroForm(instance=membro, ministerio=ministerio, user=request.user,
                                  allowed_churches=allowed_churches, igreja_inicial=membro.igreja)
            
           
            else:
                # print(f"DEBUG POST - User Management Form inválido. Erros: {user_management_form.errors.as_json()}") # Removido para produção
                messages.error(request, "Erro ao gerenciar acesso do usuário. Verifique os campos.")
                # RECARREGA O FORMULÁRIO PRINCIPAL PARA NÃO PERDER OS DADOS
                form = MembroForm(instance=membro, ministerio=ministerio, user=request.user, allowed_churches=allowed_churches, igreja_inicial=membro.igreja)
       
    else:
        form = MembroForm(instance=membro, 
                          ministerio=ministerio, 
                          user=request.user, 
                          allowed_churches=allowed_churches,
                          igreja_inicial=membro.igreja) # Passa a igreja atual do membro
        
        user_management_form = MembroUserManagementForm(
            membro_instance=membro,
            ministerio=ministerio,
            user_instance=user_associado,
            perfil_instance=perfil_associado
        )    
        # Print para quando o formulário é carregado (GET)
    # print(f"DEBUG GET - Editando Membro ID: {membro.pk}") # Removido para produção
    # print(f"DEBUG GET - Valor de membro.nascimento no BD: {membro.nascimento}") # Removido para produção
    # print(f"DEBUG GET - Tipo de membro.nascimento no BD: {type(membro.nascimento)}") # Removido para produção
    # Buscar histórico de contribuições do membro
    contribuicoes = Receitas.objects.filter(membro=membro).select_related(
        'igreja', 'conta_bancaria'
    ).order_by('-data')
    
     # DEBUG: Verificar as contribuições encontradas
    # print(f"DEBUG [editar_membro]: Contribuições encontradas para {membro.nome} (ID: {membro.pk}): {list(contribuicoes)}") # Removido para produção
    # Para ver a query SQL gerada (pode ajudar a identificar problemas no filtro):
    # print(f"DEBUG [editar_membro]: Query SQL para contribuições: {str(contribuicoes.query)}")

    # >>> ADICIONAR ESTE LOG <<<
    historico_status_membro = membro.transicoes_status_secretaria.all()
    # print(f"DEBUG [editar_membro]: Histórico de Status para {membro.nome} (ID: {membro.pk}): {list(historico_status_membro)}") # Removido para produção

    for h in historico_status_membro:
        pass  # Bloco mantido para evitar erro de indentação
    # >>> FIM DO LOG ADICIONADO <<<

    # --- FILTRO DE ACOMPANHAMENTO DE VISITA ---
    acompanhamentos_visita = membro.acompanhamentos_visita.all()
    filtro_tipo = request.GET.get('filtro_tipo', '').strip()
    filtro_data = request.GET.get('filtro_data', '').strip()
    if filtro_tipo:
        acompanhamentos_visita = acompanhamentos_visita.filter(tipo_contato=filtro_tipo)
    if filtro_data:
        try:
            from datetime import datetime
            filtro_data_dt = datetime.strptime(filtro_data, '%Y-%m-%d').date()
            acompanhamentos_visita = acompanhamentos_visita.filter(data__date=filtro_data_dt)
        except Exception:
            pass
    context = {
        'form': form,
        'membro_id': membro_id,
        'ministerio': ministerio,
        'titulo_pagina': f'Editar Membro: {membro.nome}',
        'contribuicoes': contribuicoes,
        'user_management_form': user_management_form,
        'user_associado': user_associado,
        'acompanhamentos_visita': acompanhamentos_visita,
        'filtro_tipo': filtro_tipo,
        'filtro_data': filtro_data,
    }
    return render(request, 'secretaria/editar_membro.html', context)


@check_permission(has_membro_edit_permission, login_url_name='login')
def criar_membro(request): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    igreja_inicial_para_form = None


    if not is_admin_org(request.user) and not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar membros ou não está associado a nenhuma igreja específica.")
        return redirect('secretaria:lista_membros')

    if request.method == 'POST':
        # Ao criar, a igreja_ativa (se houver) deve ser a sugestão inicial
        form = MembroForm(request.POST, request.FILES, 
                          ministerio=ministerio, 
                          user=request.user, 
                          allowed_churches=allowed_churches,
                          igreja_inicial=request.igreja_ativa) # Passa request.igreja_ativa
        if form.is_valid():
            # print(f"DEBUG POST - form.cleaned_data: {form.cleaned_data}") # Removido para produção
            nascimento_do_form = form.cleaned_data.get('nascimento')
            # print(f"DEBUG POST - Nascimento do form.cleaned_data: {nascimento_do_form}, Tipo: {type(nascimento_do_form)}") # Removido para produção

            try:
                membro_editado = form.save(commit=False)

                novo_membro = form.save(commit=False)
                if not is_admin_org(request.user) and novo_membro.igreja not in allowed_churches:
                    messages.error(request, "Erro: Igreja selecionada inválida para sua permissão.")
                else:
                    novo_membro.save(user=request.user) # Passa o usuário
                    messages.success(request, f'Membro "{novo_membro.nome}" cadastrado com sucesso!')
                    return redirect('secretaria:lista_membros')
            except Exception as e:
                logger.exception(f"Erro ao salvar novo membro para ministério {ministerio.id}")
                messages.error(request, f"Ocorreu um erro ao salvar o membro: {e}")
        else:
             messages.error(request, "Erro ao cadastrar membro. Verifique os campos.")
    else:
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            igreja_inicial_para_form = request.igreja_ativa
        elif allowed_churches.count() == 1:
            igreja_inicial_para_form = allowed_churches.first()

        form = MembroForm(ministerio=ministerio, 
                          user=request.user, 
                          allowed_churches=allowed_churches,
                          igreja_inicial=igreja_inicial_para_form)

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Cadastrar Novo Membro'
    }
    return render(request, 'secretaria/criar_membro.html', context)



# --- NOVA VIEW PARA ALTERNAR STATUS DO MEMBRO ---
@check_permission(has_membro_edit_permission, login_url_name='login')
def alternar_status_membro(request, membro_id): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    membro = get_object_or_404(Membro, pk=membro_id, igreja__in=allowed_churches)

    # Nomes dos novos StatusPessoa para Ativo e Inativo
    # Certifique-se que estes existem na sua tabela StatusPessoa
    NOME_STATUSPESSOA_ATIVO = "Ativo" # Ajuste se o nome do seu status Ativo for diferente
    NOME_STATUSPESSOA_INATIVO = "Inativo" # Ajuste se o nome do seu status Inativo for diferente


    if request.method == 'POST':
        try:
            status_ativo_novo = StatusPessoa.objects.get(nome=NOME_STATUSPESSOA_ATIVO)
            status_inativo_novo = StatusPessoa.objects.get(nome=NOME_STATUSPESSOA_INATIVO)

            acao = ""
             # Agora verificamos o novo campo status_pessoa
            if membro.status_pessoa and membro.status_pessoa.considerar_ativo_relatorios:

                # Se está ativo para relatórios, inativa
                membro.status_pessoa = status_inativo_novo
                acao = "inativado (para relatórios)"
            else:
                # Se está inativo para relatórios (ou sem status), ativa
                membro.status_pessoa = status_ativo_novo
                acao = "ativado (para relatórios)"

            membro.save(update_fields=['status_pessoa']) # Salva o novo campo
            messages.success(request, f'Membro "{membro.nome}" foi {acao} com sucesso.')

        except StatusPessoa.DoesNotExist:
            messages.error(request, f"Erro: Os status '{NOME_STATUSPESSOA_ATIVO}' ou '{NOME_STATUSPESSOA_INATIVO}' não foram encontrados no cadastro de Status de Pessoa. Verifique os nomes e o cadastro.")
        except Exception as e:
            logger.exception(f"Erro ao alternar status do membro {membro_id} para ministério {ministerio.id}")
            messages.error(request, f"Ocorreu um erro ao alternar o status do membro: {e}")
        return redirect('secretaria:lista_membros') # Sempre redireciona para a lista
    else:
        # GET request não é permitido para esta ação
        messages.error(request, "Ação inválida.")
        return redirect('secretaria:lista_membros')
# --- FIM NOVA VIEW ---


# --- NOVA VIEW PARA FICHA DE MEMBRO PARA IMPRESSÃO ---
@check_permission(has_membro_view_permission, login_url_name='login')
def ficha_membro_impressao(request, membro_id): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    
    # Usar select_related e prefetch_related para otimizar a busca de dados relacionados
    membro = get_object_or_404(
        Membro.objects.select_related(
            'igreja',
            'tipo_pessoa', 'status_pessoa', # Adicionados novos campos

            # Adicione outros select_related para ForeignKeys diretos se necessário
        ).prefetch_related(
            'contatos_set', # related_name padrão se não definido explicitamente
            'infoeclesiastica_set',
            'familia_set',
            'filhos_set',
            'observacoes_set',
            'membrocargo_set', # Para cargos (novo related_name padrão)
            'membrocargo_set__cargo', # Para acessar o nome do cargo
            # Adicione outros prefetch_related para ManyToMany ou Reverse ForeignKeys
        ),
        pk=membro_id, 
        igreja__in=allowed_churches
    )

    context = {
        'membro': membro,
        'ministerio_sistema': ministerio, # Para diferenciar do ministério do membro, se necessário
        'titulo_pagina': f"Ficha Cadastral - {membro.nome}",
        # Passar dados relacionados específicos se o template precisar deles de forma mais direta
        # Ex: 'contatos': membro.contatos_set.first() # Se for OneToOne ou você só quer o primeiro
    }
    return render(request, 'secretaria/membro/ficha_membro_impressao.html', context)
# --- FIM NOVA VIEW ---

from secretaria.utils import is_secretaria_leader
@check_permission(is_secretaria_leader, login_url_name='login') # Ajuste login_url_name se 'core:home' for diferente de 'login'
def painel_lideranca_secretaria(request): # noqa: E302
    try:
        # Chama get_ministerio_or_error no início para validar o acesso à ministério
        ministerio_usuario = get_ministerio_or_error(request) # Usar a função centralizada
        # Obtém o conjunto base de igrejas que este líder pode acessar

        allowed_churches_base_secretaria = get_allowed_churches_for_membros(request.user, ministerio_usuario) # Passa ministerio_usuario
        
    # print(f"DEBUG (Secretaria): Usuário: {request.user.username}, É Líder Secretaria: {is_secretaria_leader(request.user)}") # Removido para produção

        if not allowed_churches_base_secretaria.exists() and not is_admin_org(request.user):

            messages.warning(request, "Nenhuma igreja encontrada para visualização no painel de liderança da secretaria.")
            # Adiciona ministerio_usuario ao contexto para o template base
            return render(request, 'secretaria/painel_lideranca_secretaria.html', {
                'nenhuma_igreja_permissao': True, 
                'ministerio_usuario': ministerio_usuario,
                'titulo_dashboard': f"Liderança Secretaria - {ministerio_usuario.nome_fantasia}"
            })


        # --- Lógica do Filtro de Igreja/Regional (similar ao financeiro) ---
        churches_for_queries = None # Igrejas que serão usadas para buscar os dados
        titulo_escopo_igreja = f"Consolidado - {ministerio_usuario.nome_fantasia}" 
        ver_apenas_entidade_foco = False
        
        titulo_escopo_igreja = f"Consolidado - {ministerio_usuario.nome_fantasia}"
        
        # Para o dropdown de filtro na página (será ajustado abaixo)

        opcoes_filtro_pagina = allowed_churches_base_secretaria.order_by('nome_igreja')
        igreja_id_filtro_selecionado_template_lider_sec = request.GET.get('igreja_filtro', '')
        if request.igreja_ativa and request.igreja_ativa in allowed_churches_base_secretaria:
            igreja_em_foco_obj = request.igreja_ativa
            
            temp_pks_dropdown = {request.igreja_ativa.pk}
            if hasattr(request.igreja_ativa, 'get_descendants'):
                desc_dropdown_qs = request.igreja_ativa.get_descendants(include_self=False).filter(
                    pk__in=allowed_churches_base_secretaria.values_list('pk', flat=True)
                )
                if desc_dropdown_qs.exists():
                    temp_pks_dropdown.update(desc_dropdown_qs.values_list('pk', flat=True))
            opcoes_filtro_pagina = Igreja.objects.filter(pk__in=list(temp_pks_dropdown)).order_by('nome_igreja')

            if not igreja_id_filtro_selecionado_template_lider_sec: # Se filtro da página vazio, assume o global
                igreja_id_filtro_selecionado_template_lider_sec = str(request.igreja_ativa.pk)
            # Se o filtro da página é a própria igreja global


            if igreja_id_filtro_selecionado_template_lider_sec == str(request.igreja_ativa.pk):
                igreja_em_foco_obj = request.igreja_ativa
                # Se o filtro GET da página é explicitamente a igreja global E ela tem descendentes, vemos SÓ ela

                if request.GET.get('igreja_filtro') == str(request.igreja_ativa.pk) and \
                   hasattr(request.igreja_ativa, 'get_descendants') and \
                   request.igreja_ativa.get_descendants(include_self=False).filter(pk__in=allowed_churches_base_secretaria.values_list('pk', flat=True)).exists():
                    ver_apenas_entidade_foco = True
                    titulo_escopo_igreja = f"Apenas: {request.igreja_ativa.nome_igreja}"
                else: # Filtro da página vazio ou igreja global é folha -> visão de rede
                    ver_apenas_entidade_foco = False
                    titulo_escopo_igreja = f"Rede: {request.igreja_ativa.nome_igreja}" if len(temp_pks_dropdown) > 1 else f"Igreja: {request.igreja_ativa.nome_igreja}"
            else: # Filtro da página selecionou uma descendente específica
                try:
                    igreja_descendente_selecionada = opcoes_filtro_pagina.get(pk=igreja_id_filtro_selecionado_template_lider_sec)
                    igreja_em_foco_obj = igreja_descendente_selecionada
                    ver_apenas_entidade_foco = True
                    titulo_escopo_igreja = f"Igreja: {igreja_descendente_selecionada.nome_igreja}"
                    # id_selecionado_filtro_pagina já é o da descendente

                except Igreja.DoesNotExist:
                    igreja_id_filtro_selecionado_template_lider_sec = str(request.igreja_ativa.pk)
                    igreja_em_foco_obj = request.igreja_ativa
                    ver_apenas_entidade_foco = False
                    titulo_escopo_igreja = f"Rede: {request.igreja_ativa.nome_igreja}" if len(temp_pks_dropdown) > 1 else f"Igreja: {request.igreja_ativa.nome_igreja}"
        else: 
            opcoes_filtro_pagina = allowed_churches_base_secretaria.order_by('nome_igreja')
            if igreja_id_filtro_selecionado_template_lider_sec:
                try:
                    igreja_em_foco_obj = allowed_churches_base_secretaria.get(pk=igreja_id_filtro_selecionado_template_lider_sec)
                    ver_apenas_entidade_foco = False 
                    ver_apenas_entidade_foco = False 
                    # Título será definido ao construir pks_to_include

                except Igreja.DoesNotExist:
                    messages.warning(request, "Igreja selecionada no filtro inválida. Mostrando consolidado.")
                    igreja_id_filtro_selecionado_template_lider_sec = ''
                    igreja_em_foco_obj = None
                    titulo_escopo_igreja = f"Consolidado - {ministerio_usuario.nome_fantasia}"
            else: 
                igreja_em_foco_obj = None
                igreja_id_filtro_selecionado_template_lider_sec = ''
                titulo_escopo_igreja = f"Consolidado - {ministerio_usuario.nome_fantasia}"
       
        # --- Construir churches_for_queries e título final com base no foco e flag ---
        if igreja_em_foco_obj:
            if ver_apenas_entidade_foco:
                churches_for_queries = Igreja.objects.filter(pk=igreja_em_foco_obj.pk)
                # Título já deve estar como "Apenas:" ou "Igreja:"

            else: 
                pks_to_include = {igreja_em_foco_obj.pk}
                if hasattr(igreja_em_foco_obj, 'get_descendants'):
                    desc_qs = igreja_em_foco_obj.get_descendants(include_self=False).filter(
                        pk__in=allowed_churches_base_secretaria.values_list('pk', flat=True)
                    )
                    if desc_qs.exists():
                        pks_to_include.update(desc_qs.values_list('pk', flat=True))
                churches_for_queries = Igreja.objects.filter(pk__in=list(pks_to_include), ministerio=ministerio_usuario)
                if len(pks_to_include) > 1 and not ver_apenas_entidade_foco:
                    titulo_escopo_igreja = f"Rede: {igreja_em_foco_obj.nome_igreja}"
                elif not ver_apenas_entidade_foco:
                    titulo_escopo_igreja = f"Igreja: {igreja_em_foco_obj.nome_igreja}"
        else: 
            churches_for_queries = allowed_churches_base_secretaria
            # titulo_escopo_igreja já é "Consolidado - Ministério"

        if not churches_for_queries or not churches_for_queries.exists():
            messages.warning(request, "Nenhuma igreja corresponde aos filtros aplicados.")
            return render(request, 'secretaria/painel_lideranca_secretaria.html', {
                'nenhuma_igreja_filtro': True, 
                'ministerio_usuario': ministerio_usuario,
                'titulo_dashboard': f"Liderança Secretaria - {ministerio_usuario.nome_fantasia}",
                'igrejas_permitidas_filtro': allowed_churches_base_secretaria.order_by('nome_igreja'),
                'igreja_id_filtro_selecionado': igreja_id_filtro_selecionado_template_lider_sec,
            })

        # --- Cálculos de dados para o painel da secretaria ---
        total_membros_rede = Membro.objects.filter(
            igreja__in=churches_for_queries, 
            # status__considerar_ativo_relatorios=True # Lógica antiga
           
            status_pessoa__considerar_ativo_relatorios=True # Nova lógica
        ).count()

        from datetime import date, timedelta # Já importado no topo do arquivo
        hoje_data_lider = date.today()
        trinta_dias_atras_lider = hoje_data_lider - timedelta(days=30)
        novos_membros_rede_30_dias = Membro.objects.filter(
            igreja__in=churches_for_queries,
            status_pessoa__considerar_ativo_relatorios=True, # Alterado
            data_entrada__gte=trinta_dias_atras_lider
        ).count()

        num_igrejas_consideradas = churches_for_queries.count() 
        media_membros_por_igreja = (total_membros_rede / num_igrejas_consideradas) if num_igrejas_consideradas > 0 else 0 # noqa
        media_membros_por_igreja = round(media_membros_por_igreja, 1)

        membros_por_status_qs = Membro.objects.filter(
            igreja__in=churches_for_queries,
            status_pessoa__considerar_ativo_relatorios=True # Alterado
        ).values('status_pessoa__nome').annotate(total=Count('chave')).order_by('status_pessoa__nome') # Alterado
        grafico_membros_status_labels = [item['status_pessoa__nome'] if item['status_pessoa__nome'] else "Sem Status" for item in membros_por_status_qs]
        grafico_membros_status_valores = [item['total'] for item in membros_por_status_qs]

        membros_lideranca_ativos = Membro.objects.filter(
            igreja__in=churches_for_queries,
            status_pessoa__considerar_ativo_relatorios=True # Alterado
        )
        genero_data_lider_qs = membros_lideranca_ativos.values('genero').annotate(total=Count('chave'))
        genero_map_lider = {'F': 'Feminino', 'M': 'Masculino', '': 'Não Informado', None: 'Não Informado'}
        aggregated_genero_lider = {}
        for item_gen_lid in genero_data_lider_qs:
            genero_display_lid = genero_map_lider.get(item_gen_lid['genero'], 'Não Informado')
            aggregated_genero_lider[genero_display_lid] = aggregated_genero_lider.get(genero_display_lid, 0) + item_gen_lid['total']
        grafico_membros_genero_labels = [key for key, value in aggregated_genero_lider.items()]
        grafico_membros_genero_valores = [value for key, value in aggregated_genero_lider.items()]

        membros_com_nascimento_lider = membros_lideranca_ativos.filter(nascimento__isnull=False).values_list('nascimento', flat=True)
        idades_lider = []
        for nascimento_lid in membros_com_nascimento_lider:
            if nascimento_lid:
                idade_lid = hoje_data_lider.year - nascimento_lid.year - ((hoje_data_lider.month, hoje_data_lider.day) < (nascimento_lid.month, nascimento_lid.day))
                idades_lider.append(idade_lid)
        faixas_lider = {
            '0-5 anos': 0, '6-10 anos': 0, '11-14 anos': 0, '15-17 anos': 0,
            '18-30 anos': 0, '31-50 anos': 0, '51-65 anos': 0, 'Mais de 65 anos': 0,
            'Não Informado': membros_lideranca_ativos.filter(nascimento__isnull=True).count() # Contar quem não tem nascimento
        }
        for idade_val_lid in idades_lider:
            if 0 <= idade_val_lid <= 5: faixas_lider['0-5 anos'] += 1
            elif 6 <= idade_val_lid <= 10: faixas_lider['6-10 anos'] += 1
            elif 11 <= idade_val_lid <= 14: faixas_lider['11-14 anos'] += 1
            elif 15 <= idade_val_lid <= 17: faixas_lider['15-17 anos'] += 1
            elif 18 <= idade_val_lid <= 30: faixas_lider['18-30 anos'] += 1
            elif 31 <= idade_val_lid <= 50: faixas_lider['31-50 anos'] += 1
            elif 51 <= idade_val_lid <= 65: faixas_lider['51-65 anos'] += 1
            elif idade_val_lid > 65: faixas_lider['Mais de 65 anos'] += 1
        grafico_membros_faixa_labels = [k for k, v in faixas_lider.items()]
        grafico_membros_faixa_valores = [v for k, v in faixas_lider.items()]

         # Novo: Gráfico de Membros por Tipo de Pessoa (Consolidado)
        membros_por_tipo_qs = membros_lideranca_ativos.values(
            'tipo_pessoa__nome'
        ).annotate(total=Count('chave')).order_by('tipo_pessoa__nome')
        grafico_membros_tipo_labels = [item['tipo_pessoa__nome'] if item['tipo_pessoa__nome'] else "Sem Tipo" for item in membros_por_tipo_qs]
        grafico_membros_tipo_valores = [item['total'] for item in membros_por_tipo_qs]

        # Novo: Gráfico de Membros por Status Pessoa (Consolidado - todos os status, não apenas os ativos para relatório)
        # Usaremos 'churches_for_queries' para pegar todos os membros da rede, sem o filtro de 'considerar_ativo_relatorios'
        membros_rede_completa_para_status = Membro.objects.filter(igreja__in=churches_for_queries)
        membros_por_status_geral_qs = membros_rede_completa_para_status.values(
            'status_pessoa__nome'
        ).annotate(total=Count('chave')).order_by('status_pessoa__nome')
        grafico_membros_status_geral_labels = [item['status_pessoa__nome'] if item['status_pessoa__nome'] else "Sem Status" for item in membros_por_status_geral_qs]
        grafico_membros_status_geral_valores = [item['total'] for item in membros_por_status_geral_qs]

        context = {
            'titulo_dashboard': f"Liderança Secretaria - {titulo_escopo_igreja}", # Usar o título do escopo
            'total_membros_rede': total_membros_rede,
            'novos_membros_rede_30_dias': novos_membros_rede_30_dias,
            'media_membros_por_igreja': media_membros_por_igreja,
            'grafico_membros_status_labels_json': json.dumps(grafico_membros_status_labels),
            'grafico_membros_status_valores_json': json.dumps(grafico_membros_status_valores),
            'grafico_membros_genero_labels_json': json.dumps(grafico_membros_genero_labels),
            'grafico_membros_genero_valores_json': json.dumps(grafico_membros_genero_valores),
            'grafico_membros_faixa_labels_json': json.dumps(grafico_membros_faixa_labels),
            'grafico_membros_faixa_valores_json': json.dumps(grafico_membros_faixa_valores),
            'grafico_membros_tipo_labels_json': json.dumps(grafico_membros_tipo_labels), # Novo
            'grafico_membros_tipo_valores_json': json.dumps(grafico_membros_tipo_valores), # Novo
            'grafico_membros_status_geral_labels_json': json.dumps(grafico_membros_status_geral_labels), # Novo
            'grafico_membros_status_geral_valores_json': json.dumps(grafico_membros_status_geral_valores), # Novo
    
            'igrejas_permitidas_filtro': opcoes_filtro_pagina, 
            'igreja_id_filtro_selecionado': igreja_id_filtro_selecionado_template_lider_sec,
            'allowed_churches_count': churches_for_queries.count() if churches_for_queries else 0,
            'ministerio_usuario': ministerio_usuario,
        }
        return render(request, 'secretaria/painel_lideranca_secretaria.html', context)
    except PermissionDenied:
        raise 
    except Http404:
        raise
    except Exception as e: 
        org_nome_log = getattr(getattr(getattr(request.user, 'perfil', None), 'ministerio', None), 'nome_fantasia', "N/A")
        logger.exception(f"Erro inesperado no painel de liderança da secretaria para ministério '{org_nome_log}': {e}")
        messages.error(request, f"Ocorreu um erro ao carregar o painel de liderança da secretaria: {e}")
        return redirect('secretaria:dashboard')

# --- VIEW PARA ADICIONAR HISTÓRICO DE STATUS MANUALMENTE ---
@check_permission(has_membro_edit_permission, login_url_name='login')
def adicionar_historico_status_manual(request, membro_id=None): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    membro_obj = None
    if membro_id:
        # Garante que o membro_id pertence à ministério do usuário
        allowed_churches = get_allowed_churches_for_membros(request.user)
        membro_obj = get_object_or_404(Membro, pk=membro_id, igreja__in=allowed_churches)

    if request.method == 'POST':
        form = StatusHistoricoManualForm(request.POST, ministerio=ministerio, membro_inicial=membro_obj)
        if form.is_valid():
            try:
                historico = form.save(commit=False)
                if membro_obj: # Se o membro veio da URL, garante que é ele
                    historico.membro = membro_obj
                
                historico.registrado_por = request.user
                historico.save()
                messages.success(request, f"Entrada de histórico manual adicionada para {historico.membro.nome}.")
                # Redireciona para a página de edição do membro, na aba correta
                return redirect(reverse('secretaria:editar_membro', args=[historico.membro.pk]) + '?tab=historico-status')
            except Exception as e:
                logger.error(f"Erro ao salvar histórico manual para ministério {ministerio.id}: {e}")
                messages.error(request, f"Ocorreu um erro ao salvar o histórico: {e}")
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = StatusHistoricoManualForm(ministerio=ministerio, membro_inicial=membro_obj)

    context = {
        'form': form,
        'ministerio': ministerio,
        'membro_obj': membro_obj, # Passa o objeto do membro para o template, se houver
        'titulo_pagina': f"Adicionar Histórico Manual para {membro_obj.nome}" if membro_obj else "Adicionar Histórico Manual de Tipo/Status"
    }
    return render(request, 'secretaria/membro/adicionar_historico_status_manual.html', context)

# --- FIM VIEW HISTÓRICO MANUAL ---

# --- NOVA VIEW PARA O PORTAL DO MEMBRO COMUM ---
@login_required
def portal_membro(request):
    """
    Página inicial para usuários do grupo 'Membro Comum'.
    Exibe um resumo dos dados pessoais e atalhos.
    """
    ministerio = get_ministerio_or_error(request)
    try:
        # Busca o objeto Membro associado ao usuário logado
        membro_obj = Membro.objects.get(email__iexact=request.user.email, igreja__ministerio=ministerio)
    except Membro.DoesNotExist:
        # Se não encontrar um registro de membro correspondente, mostra uma mensagem.
        # Isso pode acontecer se o e-mail do usuário não corresponder ao e-mail no cadastro de membro.
        messages.warning(request, "Seu cadastro de membro não foi encontrado. Por favor, contate a secretaria da sua igreja para verificar seus dados.")
        membro_obj = None

    # Busca o histórico de contribuições se o membro foi encontrado
    contribuicoes = []
    if membro_obj:
        contribuicoes = Receitas.objects.filter(membro=membro_obj).order_by('-data')[:10] # Pega as 10 últimas

    context = {
        'ministerio': ministerio,
        'membro': membro_obj,
        'contribuicoes': contribuicoes,
        'titulo_pagina': "Meu Portal"
    }
    return render(request, 'secretaria/portal_membro.html', context)


# ...existing code...
from financeiro.models import Receitas
from django.db import transaction
User = get_user_model()
logger = logging.getLogger(__name__)

# --- NOVA VIEW: RELATÓRIO DE REUNIÃO DE MEMBROS ---
@login_required
def relatorio_reuniao_membros(request):
    """
    Gera relatório HTML para impressão da reunião de membros, listando membros ativos em ordem alfabética.
    """
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    igreja = None
    if request.igreja_ativa and request.igreja_ativa in allowed_churches:
        igreja = request.igreja_ativa
    elif allowed_churches.exists():
        igreja = allowed_churches.first()
    else:
        messages.error(request, "Nenhuma igreja selecionada ou permitida para gerar relatório.")
        return redirect('secretaria:dashboard')

    # Buscar membros ativos para relatórios

    # Buscar apenas membros do tipo 'Membro' (não visitantes, congregados, etc)
    membros = Membro.objects.filter(
        igreja=igreja,
        tipo_pessoa__nome__in=['Membro', 'Obreiro'],
        status_pessoa__nome__in=['Ativo', 'Em Disciplina']
    ).order_by('nome')

    # Dados do cabeçalho
    nome_igreja = igreja.nome_igreja if hasattr(igreja, 'nome_igreja') else str(igreja)
    bairro = getattr(igreja, 'bairro', '')
    cidade = getattr(igreja, 'cidade', '')
    nome_ministerio = getattr(ministerio, 'nome_fantasia', str(ministerio))
    pastor_local = getattr(igreja, 'pastor_local', '')
    pastor_regional = getattr(igreja, 'pastor_regional', '')
    data_reuniao = timezone.now().strftime('%d de %B de %Y')


    # URLs dos logos (preferencialmente logo1 da igreja e logo do ministério)
    if hasattr(igreja, 'logo1') and igreja.logo1:
        logo_igreja_url = igreja.logo1.url
    else:
        logo_igreja_url = '/static/favicon.ico'

    if hasattr(ministerio, 'logo') and ministerio.logo:
        logo_ministerio_url = ministerio.logo.url
    else:
        logo_ministerio_url = '/static/favicon.ico'

    context = {
        'membros': membros,
        'nome_igreja': nome_igreja,
        'bairro': bairro,
        'cidade': cidade,
        'nome_ministerio': nome_ministerio,
        'pastor_local': pastor_local,
        'pastor_regional': pastor_regional,
        'data_reuniao': data_reuniao,
        'logo_igreja_url': logo_igreja_url,
        'logo_ministerio_url': logo_ministerio_url,
    }
    return render(request, 'secretaria/relatorio_reuniao_membros.html', context)
# --- FIM NOVA VIEW ---

from .models import Tag
from .forms import TagForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
@verificar_assinatura_valida
def criar_tag(request):
    if not request.user.is_staff:
        return redirect('login')
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('secretaria:lista_membros')
    else:
        form = TagForm()
    # Fetch all tags to display below the form
    all_tags = Tag.objects.all().order_by('nome')
    return render(request, 'secretaria/criar_tag.html', {'form': form, 'all_tags': all_tags})