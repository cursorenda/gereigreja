from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from datetime import date
from urllib.parse import urlencode
import requests
import re
import time
import logging
import json

from .models import Aviso
from .forms import AvisoForm
from .models import WhatsAppConfiguracao, WhatsAppMensagemLog, WhatsAppConfiguracaoGlobal

from core.utils import get_ministerio_or_error
from configuracao.models import Igreja # Para filtrar igrejas
from secretaria.models import TipoPessoa, StatusPessoa
from .utils import can_manage_avisos # Para contexto de template
from core.decorators import verificar_assinatura_valida, page_access_required # Decorator de assinatura
from .services_whatsapp import send_whatsapp_text, WhatsAppSendError
from .services_whatsapp import send_whatsapp_text, WhatsAppSendError, get_waha_qr_code, get_waha_session_status

logger = logging.getLogger(__name__)

# Crie suas views aqui.

@login_required
@verificar_assinatura_valida
def templates_email(request):
    """
    View para exibir os templates de e-mail disponíveis.
    """
    return render(request, 'comunicacao/templates_email.html')

@login_required
def visualizar_template_email_massa(request):
    """
    Renderiza o template de e-mail em massa para visualização.
    """
    contexto = {
        'assunto': 'Exemplo de Assunto',
        'mensagem': 'Este é um exemplo de mensagem para o e-mail em massa.',
        'ministerio_nome': 'Nome do Ministério',
        'igreja_nome': 'Nome da Igreja',
        'remetente_email': 'contato@exemplo.com',
    }
    return render(request, 'comunicacao/email/email_massa_template.html', contexto)

@login_required
def visualizar_template_password_reset(request):
    """
    Renderiza o template de redefinição de senha para visualização.
    """
    contexto = {
        'site_name': 'Gereigreja',
        'protocol': 'https',
        'domain': 'gereigreja.site',
        'uid': 'uid-exemplo',
        'token': 'token-exemplo',
        'user': type('User', (), {'get_username': lambda self: 'usuario_exemplo'})(),
    }
    return render(request, 'contas/password_reset_email.html', contexto)

@login_required
@verificar_assinatura_valida
@page_access_required('mural_avisos')
def lista_avisos(request):
    ministerio = get_ministerio_or_error(request)
    avisos_qs = Aviso.objects.filter(ministerio=ministerio, publicado=True)

    # Filtra avisos que não expiraram ou não têm data de expiração
    avisos_qs = avisos_qs.filter(
        Q(data_expiracao__isnull=True) | Q(data_expiracao__gte=timezone.now().date())
    )

    # Filtra por igreja ativa (se houver) ou mostra avisos para toda a ministério
    # ou para as igrejas específicas que o usuário pode ver (se a lógica for mais complexa no futuro)
    if request.igreja_ativa:
        avisos_qs = avisos_qs.filter(
            Q(igrejas_destino__isnull=True) | Q(igrejas_destino=request.igreja_ativa)
        ).distinct() # distinct() é importante por causa do ManyToMany
    else:
        # Se nenhuma igreja ativa, mostra avisos para toda a ministério
        # ou aqueles que não têm igrejas destino específicas (são para toda a ministério)
        # Esta lógica pode precisar de ajuste dependendo de como você quer que "todas as igrejas" funcione
        # Por enquanto, mostra os que não têm igrejas_destino (para toda org)
        # ou os que têm alguma igreja destino (se o usuário for admin da org, por exemplo)
        # Para simplificar, se não há igreja ativa, mostramos os que são para toda a ministério.
        # Se o usuário for admin da org, ele verá todos os avisos do ministério de qualquer forma.
        avisos_qs = avisos_qs.filter(igrejas_destino__isnull=True).distinct()

    # Adicionar filtros de busca se necessário (ex: por título)
    query = request.GET.get('q')
    if query:
        avisos_qs = avisos_qs.filter(titulo__icontains=query)

    context = {
        'avisos': avisos_qs.order_by('-data_publicacao'),
        'ministerio': ministerio,
        'titulo_pagina': "Mural de Avisos",
        'can_manage': can_manage_avisos(request.user),
        'query': query,
    }
    return render(request, 'comunicacao/mural/lista_avisos.html', context)

@login_required
@verificar_assinatura_valida
@page_access_required('mural_avisos')
def detalhe_aviso(request, pk):
    ministerio = get_ministerio_or_error(request)
    aviso = get_object_or_404(Aviso, pk=pk, ministerio=ministerio, publicado=True)

    # Verifica se o aviso não expirou
    if aviso.data_expiracao and aviso.data_expiracao < timezone.now().date():
        raise PermissionDenied("Este aviso expirou.") # Ou redirecionar para lista com mensagem

    # Verifica se o aviso é para a igreja ativa do usuário ou para toda a ministério
    if request.igreja_ativa and aviso.igrejas_destino.exists() and request.igreja_ativa not in aviso.igrejas_destino.all():
        raise PermissionDenied("Você não tem permissão para ver este aviso específico para outra igreja.")

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
                aviso.ministerio = ministerio # Garante a ministério correta
                if not aviso.autor: # Define o autor se não foi preenchido (ex: se o campo estiver oculto)
                    aviso.autor = request.user
                aviso.save()
                form.save_m2m() # Necessário para salvar ManyToManyFields
                messages.success(request, "Aviso criado com sucesso!")
                return redirect('comunicacao:lista_avisos')
            except Exception as e:
                messages.error(request, f"Erro ao criar o aviso: {e}")
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = AvisoForm(initial={'ministerio': ministerio, 'autor': request.user}, ministerio=ministerio)
        form.fields['ministerio'].disabled = True # Não permitir mudar a ministério
        # O campo autor pode ser preenchido automaticamente e desabilitado ou oculto
        # form.fields['autor'].disabled = True

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': "Criar Novo Aviso",
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
                # Garante que a ministério não seja alterada
                if form.cleaned_data.get('ministerio') != ministerio:
                    raise PermissionDenied("Não é permitido alterar a ministério do aviso.")
                
                edited_aviso = form.save(commit=False)
                # Se o autor não puder ser alterado no form, garanta que ele não mude
                # edited_aviso.autor = aviso.autor # ou request.user se for o editor atual
                edited_aviso.save()
                form.save_m2m()
                messages.success(request, "Aviso atualizado com sucesso!")
                return redirect('comunicacao:lista_avisos')
            except PermissionDenied as pd:
                messages.error(request, str(pd))
            except Exception as e:
                messages.error(request, f"Erro ao atualizar o aviso: {e}")
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = AvisoForm(instance=aviso, ministerio=ministerio)
        form.fields['ministerio'].disabled = True
        # form.fields['autor'].disabled = True # Se o autor não puder ser alterado

    context = {
        'form': form,
        'aviso': aviso,
        'ministerio': ministerio,
        'titulo_pagina': f"Editar Aviso: {aviso.titulo}",
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
            messages.success(request, "Aviso excluído com sucesso!")
            return redirect('comunicacao:lista_avisos')
        except Exception as e:
            messages.error(request, f"Erro ao excluir o aviso: {e}")
            return redirect('comunicacao:detalhe_aviso', pk=pk)

    context = {
        'aviso': aviso,
        'ministerio': ministerio,
        'titulo_pagina': f"Confirmar Exclusão: {aviso.titulo}",
    }
    return render(request, 'comunicacao/mural/confirmar_excluir_aviso.html', context)

# --- VIEWS PARA ENVIO DE E-MAIL EM MASSA ---
from .forms import (
    EmailMassaForm, WhatsAppConfiguracaoForm, WhatsAppMassaForm,
    WhatsAppConfiguracaoGlobalForm, WhatsAppConfiguracaoSimplificadaForm,
)
from secretaria.models import Membro # Importar o modelo Membro

@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def enviar_email_massa(request):
    ministerio = get_ministerio_or_error(request)

    if request.method == 'POST':
        form = EmailMassaForm(request.POST, ministerio=ministerio)
        if form.is_valid():
            assunto = form.cleaned_data['assunto']
            mensagem = form.cleaned_data['mensagem']
            igrejas_destino = form.cleaned_data['igrejas_destino']
            tipos_pessoa = form.cleaned_data['tipos_pessoa']
            status_pessoa = form.cleaned_data['status_pessoa']
            apenas_ativos_para_relatorios = form.cleaned_data['apenas_ativos_para_relatorios']
            aniversariantes_do_mes = form.cleaned_data['aniversariantes_do_mes']

            # Construir o queryset de membros baseado nos filtros
            membros_qs = Membro.objects.filter(igreja__ministerio=ministerio)

            if igrejas_destino:
                membros_qs = membros_qs.filter(igreja__in=igrejas_destino)
            
            if tipos_pessoa:
                membros_qs = membros_qs.filter(tipo_pessoa__in=tipos_pessoa)
            
            if status_pessoa:
                membros_qs = membros_qs.filter(status_pessoa__in=status_pessoa)
            
            if apenas_ativos_para_relatorios:
                membros_qs = membros_qs.filter(status_pessoa__considerar_ativo_relatorios=True)
            
            if aniversariantes_do_mes:
                hoje = date.today()
                membros_qs = membros_qs.filter(nascimento__month=hoje.month)

            # Obter os e-mails dos destinatários
            destinatarios_emails = list(membros_qs.filter(email__isnull=False).exclude(email='').values_list('email', flat=True).distinct())

            if not destinatarios_emails:
                messages.warning(request, "Nenhum destinatário encontrado com os critérios selecionados.")
                return redirect('comunicacao:enviar_email_massa')

            try:
                igreja_nome = None
                remetente_email = settings.DEFAULT_FROM_EMAIL
                # Se o filtro igrejas_destino retornar só uma igreja, use ela
                if igrejas_destino and igrejas_destino.count() == 1:
                    igreja = igrejas_destino.first()
                    igreja_nome = getattr(igreja, 'nome_igreja', None)
                    if getattr(igreja, 'email', None):
                        remetente_email = igreja.email

                html_message = render_to_string('comunicacao/email/email_massa_template.html', {
                    'assunto': assunto,
                    'mensagem': mensagem,
                    'ministerio_nome': ministerio.nome_fantasia,
                    'igreja_nome': igreja_nome,
                    'remetente_email': remetente_email,
                })
                send_mail(
                    assunto,
                    mensagem, # Versão texto puro (fallback)
                    settings.DEFAULT_FROM_EMAIL,
                    destinatarios_emails,
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(request, f"E-mail enviado com sucesso para {len(destinatarios_emails)} destinatário(s)!")
                return redirect('comunicacao:enviar_email_massa')
            except BadHeaderError:
                messages.error(request, "Assunto inválido.")
            except Exception as e:
                messages.error(request, f"Erro ao enviar e-mail: {e}")
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = EmailMassaForm(ministerio=ministerio)

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': "Enviar E-mail em Massa",
    }
    return render(request, 'comunicacao/email/form_email_massa.html', context)


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def configurar_whatsapp(request):
    ministerio = get_ministerio_or_error(request)
    igreja_ativa = request.igreja_ativa

    if not igreja_ativa:
        messages.error(request, 'Selecione uma congregacao ativa no topo da tela para configurar o WhatsApp.')
        return redirect('secretaria:dashboard')

    instance = None
    if igreja_ativa:
        instance = WhatsAppConfiguracao.objects.filter(igreja=igreja_ativa, ministerio=ministerio).first()

    config_global = WhatsAppConfiguracaoGlobal.objects.filter(ministerio=ministerio).first()

    if request.method == 'POST':
        form = WhatsAppConfiguracaoSimplificadaForm(request.POST, instance=instance, ministerio=ministerio)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ministerio = ministerio
            obj.igreja = igreja_ativa
            obj.save()
            messages.success(request, 'Configuracao de WhatsApp salva com sucesso.')
            return redirect('comunicacao:configurar_whatsapp')
        messages.error(request, 'Corrija os erros do formulario de configuracao WhatsApp.')
    else:
        form = WhatsAppConfiguracaoSimplificadaForm(instance=instance, ministerio=ministerio)

    status_sessao = None
    if instance and instance.pk:
        status_sessao = get_waha_session_status(instance)

    return render(
        request,
        'comunicacao/whatsapp/configuracao_whatsapp.html',
        {
            'form': form,
            'ministerio': ministerio,
            'config': instance,
            'config_global': config_global,
            'status_sessao': status_sessao,
            'igreja_ativa': igreja_ativa,
            'titulo_pagina': 'Configuracao WhatsApp por Congregacao',
        },
    )


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def configurar_whatsapp_global(request):
    """Config do servidor WAHA do ministerio (admin do ministerio)."""
    ministerio = get_ministerio_or_error(request)
    instance, _ = WhatsAppConfiguracaoGlobal.objects.get_or_create(ministerio=ministerio)

    if request.method == 'POST':
        form = WhatsAppConfiguracaoGlobalForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuracao global do WhatsApp salva com sucesso.')
            return redirect('comunicacao:configurar_whatsapp_global')
        messages.error(request, 'Corrija os erros do formulario.')
    else:
        form = WhatsAppConfiguracaoGlobalForm(instance=instance)

    return render(request, 'comunicacao/whatsapp/configuracao_whatsapp_global.html', {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Configuracao Global do WhatsApp',
    })




@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def qr_code_whatsapp(request, pk):
    """Retorna JSON com status da sessao e QR code (base64) para uma configuracao."""
    ministerio = get_ministerio_or_error(request)
    config = get_object_or_404(WhatsAppConfiguracao, pk=pk, ministerio=ministerio)
    status = get_waha_session_status(config)
    qr_data = None
    if status in ('SCAN_QR_CODE', 'STOPPED', 'OFFLINE', 'UNKNOWN', None):
        qr_data = get_waha_qr_code(config)
        if qr_data and status in ('STOPPED', 'UNKNOWN', None):
            status = 'SCAN_QR_CODE'
    return JsonResponse({'status': status, 'qr': qr_data})


def _filtrar_membros_whatsapp_destino(
    *,
    ministerio,
    igreja_ativa,
    tipos_pessoa,
    status_pessoa,
    aniversariantes_do_mes,
    somente_com_celular,
):
    """Filtra membros da igreja ativa por critérios."""
    membros_qs = Membro.objects.filter(igreja__ministerio=ministerio)

    # Sempre filtra pela igreja ativa
    if igreja_ativa:
        membros_qs = membros_qs.filter(igreja=igreja_ativa)
    
    if tipos_pessoa:
        membros_qs = membros_qs.filter(tipo_pessoa__in=tipos_pessoa)
    if status_pessoa:
        membros_qs = membros_qs.filter(status_pessoa__in=status_pessoa)
    if aniversariantes_do_mes:
        hoje = date.today()
        membros_qs = membros_qs.filter(nascimento__month=hoje.month)
    if somente_com_celular:
        membros_qs = membros_qs.exclude(celular__isnull=True).exclude(celular='')

    return membros_qs.select_related('igreja').distinct()


def _parse_whatsapp_filtros(query_data):
    tipos_pessoa_ids = [int(v) for v in query_data.getlist('tipos_pessoa') if str(v).isdigit()]
    status_pessoa_ids = [int(v) for v in query_data.getlist('status_pessoa') if str(v).isdigit()]

    return {
        'tipos_pessoa_ids': tipos_pessoa_ids,
        'status_pessoa_ids': status_pessoa_ids,
        'aniversariantes_do_mes': query_data.get('aniversariantes_do_mes') in ('on', 'true', '1'),
        'somente_com_celular': query_data.get('somente_com_celular') in ('on', 'true', '1'),
    }


def _build_whatsapp_filtros_querystring(filtros):
    params = []
    for tipo_id in filtros.get('tipos_pessoa_ids', []):
        params.append(('tipos_pessoa', str(tipo_id)))
    for status_id in filtros.get('status_pessoa_ids', []):
        params.append(('status_pessoa', str(status_id)))
    if filtros.get('aniversariantes_do_mes'):
        params.append(('aniversariantes_do_mes', 'on'))
    if filtros.get('somente_com_celular'):
        params.append(('somente_com_celular', 'on'))
    return urlencode(params, doseq=True)


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def preview_whatsapp_destinatarios(request):
    """Retorna uma prévia dos destinatarios aptos a receber o envio em massa."""
    try:
        ministerio = get_ministerio_or_error(request)
        igreja_ativa = request.igreja_ativa
        
        filtros = _parse_whatsapp_filtros(request.GET)
        tipos_pessoa = (
            TipoPessoa.objects.filter(pk__in=filtros['tipos_pessoa_ids'])
            if filtros['tipos_pessoa_ids']
            else TipoPessoa.objects.none()
        )
        status_pessoa = (
            StatusPessoa.objects.filter(pk__in=filtros['status_pessoa_ids'])
            if filtros['status_pessoa_ids']
            else StatusPessoa.objects.none()
        )
        
        membros_qs = _filtrar_membros_whatsapp_destino(
            ministerio=ministerio,
            igreja_ativa=igreja_ativa,
            tipos_pessoa=tipos_pessoa,
            status_pessoa=status_pessoa,
            aniversariantes_do_mes=filtros['aniversariantes_do_mes'],
            somente_com_celular=filtros['somente_com_celular'],
        )

        config_igrejas_ids = set(
            WhatsAppConfiguracao.objects.filter(ministerio=ministerio, ativo=True)
            .exclude(igreja__isnull=True)
            .values_list('igreja_id', flat=True)
        )

        sem_celular_q = Q(celular__isnull=True) | Q(celular='')
        total_filtrados = membros_qs.count()
        sem_config_total = membros_qs.exclude(igreja_id__in=config_igrejas_ids).count()
        sem_celular_total = membros_qs.filter(sem_celular_q).count()

        aptos_qs = membros_qs.filter(igreja_id__in=config_igrejas_ids).exclude(sem_celular_q)
        total_aptos = aptos_qs.count()

        pessoas = []
        membros_preview = membros_qs.order_by('pk')[:200]
        for membro in membros_preview:
            tem_celular = bool((membro.celular or '').strip())
            tem_config = membro.igreja_id in config_igrejas_ids
            habilitado = tem_celular and tem_config

            motivo_bloqueio = ''
            if not tem_celular:
                motivo_bloqueio = 'Sem celular cadastrado'
            elif not tem_config:
                motivo_bloqueio = 'Igreja sem configuracao WhatsApp ativa'

            pessoas.append({
                'id': membro.pk,
                'nome': membro.nome or 'Sem nome',
                'igreja': membro.igreja.nome_igreja if membro.igreja else 'Sem igreja',
                'celular': membro.celular or '-',
                'tem_celular': tem_celular,
                'habilitado': habilitado,
                'motivo_bloqueio': motivo_bloqueio,
            })

        return JsonResponse({
            'ok': True,
            'total_filtrados': total_filtrados,
            'total_aptos': total_aptos,
            'sem_config_total': sem_config_total,
            'sem_celular_total': sem_celular_total,
            'pessoas': pessoas,
            'limite_nomes': 200,
        })
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def editar_celulares_whatsapp_massa(request):
    """Tela de edicao em massa de celulares usando os mesmos filtros do envio WhatsApp."""
    ministerio = get_ministerio_or_error(request)
    igreja_ativa = request.igreja_ativa

    if not igreja_ativa:
        messages.error(request, 'Selecione uma congregacao ativa no topo da tela para editar celulares.')
        return redirect('comunicacao:enviar_whatsapp_massa')

    query_data = request.POST if request.method == 'POST' else request.GET
    filtros = _parse_whatsapp_filtros(query_data)

    tipos_pessoa = (
        TipoPessoa.objects.filter(pk__in=filtros['tipos_pessoa_ids'])
        if filtros['tipos_pessoa_ids']
        else TipoPessoa.objects.none()
    )
    status_pessoa = (
        StatusPessoa.objects.filter(pk__in=filtros['status_pessoa_ids'])
        if filtros['status_pessoa_ids']
        else StatusPessoa.objects.none()
    )

    membros_qs = _filtrar_membros_whatsapp_destino(
        ministerio=ministerio,
        igreja_ativa=igreja_ativa,
        tipos_pessoa=tipos_pessoa,
        status_pessoa=status_pessoa,
        aniversariantes_do_mes=filtros['aniversariantes_do_mes'],
        # Na tela de edicao em massa, sempre incluir pessoas sem celular para permitir preenchimento.
        somente_com_celular=False,
    ).order_by('nome', 'pk')

    if request.method == 'POST':
        post_celular_keys = [k for k in request.POST.keys() if k.startswith('celular_')]
        logger.info(
            'WhatsApp massa celulares POST keys: total=%s sample=%s',
            len(post_celular_keys),
            post_celular_keys[:10],
        )

        atualizados = []
        para_persistir = []
        invalidos = []
        sem_alteracao = 0

        # Prioriza payload JSON de alteracoes enviado pelo frontend.
        celular_updates = {}
        payload_raw = (request.POST.get('celulares_payload') or '').strip()
        payload_mode = (request.POST.get('celulares_payload_mode') or '').strip().lower()
        payload_dirty_only = payload_mode == 'dirty_only'
        if payload_raw:
            try:
                payload = json.loads(payload_raw)
                if isinstance(payload, dict):
                    for pk_raw, value in payload.items():
                        try:
                            pk = int(pk_raw)
                        except (TypeError, ValueError):
                            continue
                        celular_updates[pk] = (value or '').strip()
            except (TypeError, ValueError, json.JSONDecodeError):
                logger.warning('WhatsApp massa celulares: payload JSON invalido recebido.')

        # Fallback para suporte a envio classico por campos celular_X.
        # Se o payload vier vazio por qualquer motivo, usa os campos do formulario.
        if not celular_updates:
            for key, value in request.POST.items():
                if key.startswith('celular_'):
                    # Strip non-digit characters to handle locale-formatted decimal separators
                    # e.g., 'celular_1.112' (locale) -> '1112' -> int(1112)
                    pk_str = re.sub(r'\D', '', key[len('celular_'):])
                    if pk_str:
                        try:
                            pk = int(pk_str)
                            celular_updates[pk] = value.strip()
                        except ValueError:
                            pass

        if celular_updates:
            amostra_payload = [
                {
                    'pk': pk,
                    'raw': raw,
                    'digits': re.sub(r'\D', '', raw),
                }
                for pk, raw in list(celular_updates.items())[:10]
            ]
            logger.info('WhatsApp massa celulares payload sample: %s', amostra_payload)

        # Busca apenas os membros cujos PKs vieram no POST (filtrando pelo queryset
        # já restrito ao ministerio/igreja_ativa para evitar alterações indevidas)
        membros_para_update = {m.pk: m for m in membros_qs.filter(pk__in=celular_updates.keys())}
        pks_ignorados = [pk for pk in celular_updates.keys() if pk not in membros_para_update]
        diagnostico_por_pk = []

        for pk, raw in celular_updates.items():
            membro = membros_para_update.get(pk)
            if membro is None:
                continue  # PK não pertence à congregação ativa, ignora

            celular_limpo = re.sub(r'\D', '', raw)

            if celular_limpo and len(celular_limpo) > 15:
                invalidos.append(membro.nome or f'ID {membro.pk}')
                continue

            novo_celular = celular_limpo or None
            atual_celular = re.sub(r'\D', '', membro.celular or '') or None
            diagnostico_por_pk.append({
                'pk': membro.pk,
                'nome': membro.nome,
                'atual': atual_celular,
                'novo': novo_celular,
            })
            if atual_celular != novo_celular:
                atualizados.append(membro)
            else:
                sem_alteracao += 1

            # Persistimos explicitamente todo campo valido recebido para evitar
            # discrepancias entre o valor exibido na tela e o valor no banco.
            membro.celular = novo_celular
            para_persistir.append(membro)

        preenchidos = sum(1 for v in celular_updates.values() if v)
        limpados = len(celular_updates) - preenchidos

        logger.info(
            (
                'WhatsApp massa celulares: igreja_id=%s, campos_recebidos=%s, '
                'preenchidos=%s, vazios=%s, reconhecidos=%s, ignorados=%s, '
                'atualizados=%s, sem_alteracao=%s, invalidos=%s, payload=%s, payload_mode=%s'
            ),
            getattr(igreja_ativa, 'id', None),
            len(celular_updates),
            preenchidos,
            limpados,
            len(membros_para_update),
            len(pks_ignorados),
            len(atualizados),
            sem_alteracao,
            len(invalidos),
            bool(payload_raw),
            payload_mode or '-',
        )
        if diagnostico_por_pk:
            logger.info('WhatsApp massa celulares comparacao sample: %s', diagnostico_por_pk[:10])

        if para_persistir:
            for membro in para_persistir:
                membro.save(update_fields=['celular'])

        if atualizados:
            messages.success(request, f'Celular atualizado para {len(atualizados)} pessoa(s).')
        else:
            messages.info(request, 'Nenhum celular foi atualizado.')

        if invalidos:
            exemplos = ', '.join(invalidos[:5])
            sufixo = '...' if len(invalidos) > 5 else ''
            messages.warning(
                request,
                (
                    f'{len(invalidos)} numero(s) ignorados por exceder 15 digitos '
                    f'(ex.: {exemplos}{sufixo}).'
                ),
            )

        querystring = _build_whatsapp_filtros_querystring(filtros)
        redirect_url = reverse('comunicacao:editar_celulares_whatsapp_massa')
        if querystring:
            redirect_url = f'{redirect_url}?{querystring}'
        return redirect(redirect_url)

    querystring = _build_whatsapp_filtros_querystring(filtros)
    return render(
        request,
        'comunicacao/whatsapp/editar_celulares_massa.html',
        {
            'ministerio': ministerio,
            'igreja_ativa': igreja_ativa,
            'membros': list(membros_qs),
            'filtros': filtros,
            'querystring': querystring,
            'titulo_pagina': 'Editar Celulares em Massa',
        },
    )


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def enviar_whatsapp_massa(request):
    ministerio = get_ministerio_or_error(request)
    igreja_ativa = request.igreja_ativa

    if request.method == 'POST':
        form = WhatsAppMassaForm(request.POST, ministerio=ministerio)
        if form.is_valid():
            mensagem = form.cleaned_data['mensagem']
            tipos_pessoa = form.cleaned_data['tipos_pessoa']
            status_pessoa = form.cleaned_data['status_pessoa']
            aniversariantes_do_mes = form.cleaned_data['aniversariantes_do_mes']
            somente_com_celular = form.cleaned_data['somente_com_celular']

            membros_qs = _filtrar_membros_whatsapp_destino(
                ministerio=ministerio,
                igreja_ativa=igreja_ativa,
                tipos_pessoa=tipos_pessoa,
                status_pessoa=status_pessoa,
                aniversariantes_do_mes=aniversariantes_do_mes,
                somente_com_celular=somente_com_celular,
            )

            selected_ids = set()
            for raw_id in request.POST.getlist('destinatarios_ids'):
                try:
                    selected_ids.add(int(raw_id))
                except (TypeError, ValueError):
                    continue
            if selected_ids:
                membros_qs = membros_qs.filter(pk__in=selected_ids)

            enviados = 0
            falhas = 0
            sem_config = 0
            igrejas_sem_config = set()
            falhas_detalhes = []
            for membro in membros_qs.select_related('igreja'):
                config = WhatsAppConfiguracao.objects.filter(
                    ministerio=ministerio,
                    igreja=membro.igreja,
                    ativo=True,
                ).first()
                if not config:
                    sem_config += 1
                    falhas += 1
                    nome_igreja = membro.igreja.nome_igreja if membro.igreja else 'Sem igreja'
                    igrejas_sem_config.add(nome_igreja)
                    if len(falhas_detalhes) < 3:
                        falhas_detalhes.append(f"{membro.nome or 'Sem nome'}: igreja sem configuracao WA ativa.")
                    WhatsAppMensagemLog.objects.create(
                        ministerio=ministerio,
                        igreja=membro.igreja,
                        membro=membro,
                        configuracao=None,
                        tipo='manual',
                        status='erro',
                        telefone_destino=membro.celular or '',
                        mensagem=mensagem,
                        erro='Igreja sem configuracao WhatsApp ativa para envio em massa.',
                    )
                    continue
                texto = (
                    mensagem.replace('{nome}', membro.nome or '')
                    .replace('{igreja}', membro.igreja.nome_igreja if membro.igreja else '')
                    .replace('{ministerio}', ministerio.nome_fantasia)
                )
                try:
                    send_whatsapp_text(
                        config,
                        membro.celular,
                        texto,
                        tipo='manual',
                        ministerio=ministerio,
                        igreja=membro.igreja,
                        membro=membro,
                    )
                    enviados += 1
                except WhatsAppSendError as exc:
                    falhas += 1
                    if len(falhas_detalhes) < 3:
                        falhas_detalhes.append(f"{membro.nome or 'Sem nome'}: {str(exc)[:140]}")

            if enviados:
                messages.success(request, f'WAHA aceitou o envio para {enviados} pessoa(s).')
            if falhas:
                messages.warning(request, f'{falhas} envio(s) falharam ou nao tinham configuracao ativa.')
                if falhas_detalhes:
                    messages.warning(request, 'Detalhes: ' + ' | '.join(falhas_detalhes))
            if sem_config:
                igrejas_txt = ', '.join(sorted(igrejas_sem_config)[:5])
                sufixo = '...' if len(igrejas_sem_config) > 5 else ''
                messages.warning(
                    request,
                    f'{sem_config} destinatario(s) foram ignorados por falta de configuracao ativa nas igrejas: {igrejas_txt}{sufixo}'
                )
            if not enviados and not falhas:
                if selected_ids:
                    messages.warning(request, 'Nenhum destinatario selecionado esta apto para envio.')
                else:
                    messages.warning(request, 'Nenhum destinatario encontrado com os filtros selecionados.')
            return redirect('comunicacao:enviar_whatsapp_massa')
        messages.error(request, 'Corrija os erros do formulario de envio WhatsApp.')
    else:
        form = WhatsAppMassaForm(ministerio=ministerio)

    return render(
        request,
        'comunicacao/whatsapp/form_whatsapp_massa.html',
        {
            'form': form,
            'ministerio': ministerio,
            'titulo_pagina': 'Enviar WhatsApp em Massa',
        },
    )


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def test_waha_health(request):
    """Testa saúde e latência do servidor WAHA."""
    ministerio = get_ministerio_or_error(request)
    
    try:
        # Obter a configuração da igreja ativa (não a global)
        from secretaria.models import Membro
        Igreja = Membro.objects.model.__class__.__bases__[0].__module__
        
        # Pega a configuração da igreja ativa via request
        if not hasattr(request, 'igreja_ativa'):
            return JsonResponse({'ok': False, 'error': 'Igreja ativa não definida na request.'})
        
        config = WhatsAppConfiguracao.objects.filter(
            ministerio=ministerio,
            igreja=request.igreja_ativa
        ).first()
        
        if not config:
            return JsonResponse({'ok': False, 'error': 'Configuracao WhatsApp nao encontrada para a igreja.'})
        
        # Usa as propriedades waha_url_efetiva e waha_key_efetiva que fazem o fallback correto
        base_url = config.waha_url_efetiva.rstrip('/')
        headers = {'Content-Type': 'application/json'}
        if config.waha_key_efetiva:
            headers['X-Api-Key'] = config.waha_key_efetiva
        
        start = time.time()
        resp = requests.get(f"{base_url}/api/sessions/default", headers=headers, timeout=(5, 10))
        elapsed = (time.time() - start) * 1000
        
        return JsonResponse({
            'ok': True,
            'status': resp.status_code,
            'tempo_ms': round(elapsed, 2),
            'mensagem': f'WAHA respondeu em {elapsed:.0f}ms - Status: {resp.status_code}'
        })
    except Exception as exc:
        elapsed = (time.time() - start) * 1000 if 'start' in locals() else None
        tempo_info = f' ({elapsed:.0f}ms)' if elapsed else ''
        return JsonResponse({
            'ok': False,
            'error': f'Falha ao conectar WAHA{tempo_info}: {str(exc)[:200]}'
        })


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def logs_whatsapp(request):
    ministerio = get_ministerio_or_error(request)
    logs = WhatsAppMensagemLog.objects.filter(ministerio=ministerio).select_related('igreja', 'membro')[:200]
    return render(
        request,
        'comunicacao/whatsapp/logs_whatsapp.html',
        {
            'logs': logs,
            'ministerio': ministerio,
            'titulo_pagina': 'Logs de WhatsApp',
        },
    )


@csrf_exempt
@require_POST
def waha_webhook(request):
    token = request.headers.get('X-Webhook-Token') or request.GET.get('token')
    payload = request.body.decode('utf-8', errors='ignore')

    configuracao = None
    if token:
        configuracao = WhatsAppConfiguracao.objects.filter(webhook_token=token, ativo=True).first()
    if not configuracao:
        return HttpResponseForbidden('Webhook token invalido')

    WhatsAppMensagemLog.objects.create(
        ministerio=configuracao.ministerio,
        igreja=configuracao.igreja,
        configuracao=configuracao,
        tipo='webhook',
        status='recebido',
        telefone_destino='entrada',
        mensagem=payload[:3000],
        resposta_waha={'headers': dict(request.headers)},
    )
    return JsonResponse({'ok': True})
