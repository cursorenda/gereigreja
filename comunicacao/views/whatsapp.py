import json
import logging
import re
import time

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.decorators import page_access_required, verificar_assinatura_valida
from core.utils import get_ministerio_or_error
from secretaria.models import StatusPessoa, TipoPessoa

from ..forms import (
    WhatsAppConfiguracaoGlobalForm,
    WhatsAppConfiguracaoSimplificadaForm,
    WhatsAppMassaForm,
)
from ..models import WhatsAppConfiguracao, WhatsAppConfiguracaoGlobal, WhatsAppMensagemLog
from ..selectors import (
    build_whatsapp_filtros_querystring,
    build_whatsapp_preview_data,
    filtrar_membros_whatsapp_destino,
    parse_whatsapp_filtros,
)
from ..services import enviar_whatsapp_massa as enviar_whatsapp_massa_service
from ..services_whatsapp import get_waha_qr_code, get_waha_session_status

logger = logging.getLogger(__name__)


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def configurar_whatsapp(request):
    ministerio = get_ministerio_or_error(request)
    igreja_ativa = request.igreja_ativa

    if not igreja_ativa:
        messages.error(request, 'Selecione uma congregacao ativa no topo da tela para configurar o WhatsApp.')
        return redirect('secretaria:dashboard')

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

    status_sessao = get_waha_session_status(instance) if instance and instance.pk else None

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

    return render(
        request,
        'comunicacao/whatsapp/configuracao_whatsapp_global.html',
        {
            'form': form,
            'ministerio': ministerio,
            'titulo_pagina': 'Configuracao Global do WhatsApp',
        },
    )


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


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def preview_whatsapp_destinatarios(request):
    """Retorna uma previa dos destinatarios aptos a receber o envio em massa."""
    try:
        ministerio = get_ministerio_or_error(request)
        igreja_ativa = request.igreja_ativa

        filtros = parse_whatsapp_filtros(request.GET)
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

        membros_qs = filtrar_membros_whatsapp_destino(
            ministerio=ministerio,
            igreja_ativa=igreja_ativa,
            tipos_pessoa=tipos_pessoa,
            status_pessoa=status_pessoa,
            aniversariantes_do_mes=filtros['aniversariantes_do_mes'],
            somente_com_celular=filtros['somente_com_celular'],
        )

        preview = build_whatsapp_preview_data(
            ministerio=ministerio,
            membros_qs=membros_qs,
            limite_nomes=200,
        )

        return JsonResponse({'ok': True, **preview})
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
    filtros = parse_whatsapp_filtros(query_data)

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

    membros_qs = filtrar_membros_whatsapp_destino(
        ministerio=ministerio,
        igreja_ativa=igreja_ativa,
        tipos_pessoa=tipos_pessoa,
        status_pessoa=status_pessoa,
        aniversariantes_do_mes=filtros['aniversariantes_do_mes'],
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

        celular_updates = {}
        payload_raw = (request.POST.get('celulares_payload') or '').strip()
        payload_mode = (request.POST.get('celulares_payload_mode') or '').strip().lower()
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

        if not celular_updates:
            for key, value in request.POST.items():
                if key.startswith('celular_'):
                    pk_str = re.sub(r'\D', '', key[len('celular_'):])
                    if pk_str:
                        try:
                            pk = int(pk_str)
                            celular_updates[pk] = value.strip()
                        except ValueError:
                            pass

        if celular_updates:
            amostra_payload = [
                {'pk': pk, 'raw': raw, 'digits': re.sub(r'\D', '', raw)}
                for pk, raw in list(celular_updates.items())[:10]
            ]
            logger.info('WhatsApp massa celulares payload sample: %s', amostra_payload)

        membros_para_update = {m.pk: m for m in membros_qs.filter(pk__in=celular_updates.keys())}
        pks_ignorados = [pk for pk in celular_updates.keys() if pk not in membros_para_update]
        diagnostico_por_pk = []

        for pk, raw in celular_updates.items():
            membro = membros_para_update.get(pk)
            if membro is None:
                continue

            celular_limpo = re.sub(r'\D', '', raw)
            if celular_limpo and len(celular_limpo) > 15:
                invalidos.append(membro.nome or f'ID {membro.pk}')
                continue

            novo_celular = celular_limpo or None
            atual_celular = re.sub(r'\D', '', membro.celular or '') or None
            diagnostico_por_pk.append(
                {
                    'pk': membro.pk,
                    'nome': membro.nome,
                    'atual': atual_celular,
                    'novo': novo_celular,
                }
            )
            if atual_celular != novo_celular:
                atualizados.append(membro)
            else:
                sem_alteracao += 1

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

        querystring = build_whatsapp_filtros_querystring(filtros)
        redirect_url = reverse('comunicacao:editar_celulares_whatsapp_massa')
        if querystring:
            redirect_url = f'{redirect_url}?{querystring}'
        return redirect(redirect_url)

    querystring = build_whatsapp_filtros_querystring(filtros)
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

            membros_qs = filtrar_membros_whatsapp_destino(
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

            resumo_envio = enviar_whatsapp_massa_service(
                ministerio=ministerio,
                membros_qs=membros_qs,
                mensagem=mensagem,
            )
            enviados = resumo_envio['enviados']
            falhas = resumo_envio['falhas']
            sem_config = resumo_envio['sem_config']
            igrejas_sem_config = resumo_envio['igrejas_sem_config']
            falhas_detalhes = resumo_envio['falhas_detalhes']

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
    """Testa saude e latencia do servidor WAHA."""
    ministerio = get_ministerio_or_error(request)

    try:
        if not hasattr(request, 'igreja_ativa'):
            return JsonResponse({'ok': False, 'error': 'Igreja ativa não definida na request.'})

        config = WhatsAppConfiguracao.objects.filter(
            ministerio=ministerio,
            igreja=request.igreja_ativa,
        ).first()

        if not config:
            return JsonResponse({'ok': False, 'error': 'Configuracao WhatsApp nao encontrada para a igreja.'})

        base_url = config.waha_url_efetiva.rstrip('/')
        headers = {'Content-Type': 'application/json'}
        if config.waha_key_efetiva:
            headers['X-Api-Key'] = config.waha_key_efetiva

        start = time.time()
        resp = requests.get(f"{base_url}/api/sessions/default", headers=headers, timeout=(5, 10))
        elapsed = (time.time() - start) * 1000

        return JsonResponse(
            {
                'ok': True,
                'status': resp.status_code,
                'tempo_ms': round(elapsed, 2),
                'mensagem': f'WAHA respondeu em {elapsed:.0f}ms - Status: {resp.status_code}',
            }
        )
    except Exception as exc:
        elapsed = (time.time() - start) * 1000 if 'start' in locals() else None
        tempo_info = f' ({elapsed:.0f}ms)' if elapsed else ''
        return JsonResponse({'ok': False, 'error': f'Falha ao conectar WAHA{tempo_info}: {str(exc)[:200]}'})


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
