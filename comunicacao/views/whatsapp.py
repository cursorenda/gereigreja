import json
import logging
import re
import time

import requests
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ReadTimeout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
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
from ..models import (
    WhatsAppConfiguracao,
    WhatsAppConfiguracaoGlobal,
    WhatsAppFiltroPerfil,
    WhatsAppMensagemLog,
)
from ..selectors import (
    build_whatsapp_filtros_querystring,
    build_whatsapp_preview_data,
    filtrar_status_whatsapp_para_tipos,
    filtrar_membros_whatsapp_destino,
    listar_agendamentos_aniversariantes,
    listar_proximos_aniversariantes,
    obter_automacao_aniversariantes,
    parse_whatsapp_filtros,
)
from ..services import enviar_whatsapp_massa as enviar_whatsapp_massa_service
from ..services_whatsapp import get_waha_qr_code, get_waha_session_status

logger = logging.getLogger(__name__)


def _queryset_perfis_whatsapp_massa(*, ministerio, igreja_ativa):
    qs = WhatsAppFiltroPerfil.objects.filter(ministerio=ministerio)
    if igreja_ativa:
        qs = qs.filter(Q(igreja=igreja_ativa) | Q(igreja__isnull=True))
    else:
        qs = qs.filter(igreja__isnull=True)
    return qs.select_related('igreja').order_by('nome', 'pk')


def _desmarcar_outras_listas_favoritas(*, ministerio, igreja_ativa, perfil_id):
    WhatsAppFiltroPerfil.objects.filter(
        ministerio=ministerio,
        igreja=igreja_ativa,
        favorita=True,
    ).exclude(pk=perfil_id).update(favorita=False)


def _carregar_perfil_whatsapp_massa(*, ministerio, igreja_ativa, perfil_id):
    if not str(perfil_id).isdigit():
        return None
    return _queryset_perfis_whatsapp_massa(ministerio=ministerio, igreja_ativa=igreja_ativa).filter(
        pk=int(perfil_id)
    ).first()


def _filtros_iniciais_por_perfil(perfil):
    filtros = (perfil.filtros or {}) if perfil else {}
    return {
        'tipos_pessoa': filtros.get('tipos_pessoa_ids', []),
        'status_pessoa': filtros.get('status_pessoa_ids', []),
        'graus_eclesiasticos': filtros.get('graus_eclesiasticos', []),
        'aniversariantes_do_mes': bool(filtros.get('aniversariantes_do_mes')),
        'somente_com_celular': bool(filtros.get('somente_com_celular', True)),
    }


def _montar_filtros_para_perfil(*, request, tipos_pessoa_ids, status_pessoa_ids, graus_eclesiasticos, aniversariantes_do_mes, somente_com_celular):
    tipos_qs = TipoPessoa.objects.filter(pk__in=tipos_pessoa_ids)
    status_qs = StatusPessoa.objects.filter(pk__in=status_pessoa_ids)
    status_qs = filtrar_status_whatsapp_para_tipos(status_qs, tipos_qs)

    return {
        'tipos_pessoa_ids': list(tipos_qs.values_list('pk', flat=True)),
        'status_pessoa_ids': list(status_qs.values_list('pk', flat=True)),
        'graus_eclesiasticos': list(graus_eclesiasticos),
        'aniversariantes_do_mes': bool(aniversariantes_do_mes),
        'somente_com_celular': bool(somente_com_celular),
        'salvo_por_user_id': getattr(request.user, 'id', None),
    }


def _calcular_totais_lista_salva(*, ministerio, igreja_ativa, filtros):
    tipos_ids = [int(v) for v in (filtros or {}).get('tipos_pessoa_ids', []) if str(v).isdigit()]
    status_ids = [int(v) for v in (filtros or {}).get('status_pessoa_ids', []) if str(v).isdigit()]
    graus = [v for v in (filtros or {}).get('graus_eclesiasticos', []) if v]
    aniversariantes = bool((filtros or {}).get('aniversariantes_do_mes'))
    somente_com_celular = bool((filtros or {}).get('somente_com_celular', True))

    tipos_qs = TipoPessoa.objects.filter(pk__in=tipos_ids) if tipos_ids else TipoPessoa.objects.none()
    status_qs = StatusPessoa.objects.filter(pk__in=status_ids) if status_ids else StatusPessoa.objects.none()
    status_qs = filtrar_status_whatsapp_para_tipos(status_qs, tipos_qs)

    membros_qs = filtrar_membros_whatsapp_destino(
        ministerio=ministerio,
        igreja_ativa=igreja_ativa,
        tipos_pessoa=tipos_qs,
        graus_eclesiasticos=graus,
        status_pessoa=status_qs,
        aniversariantes_do_mes=aniversariantes,
        somente_com_celular=somente_com_celular,
    )
    preview = build_whatsapp_preview_data(ministerio=ministerio, membros_qs=membros_qs, limite_nomes=1)
    return preview['total_filtrados'], preview['total_aptos']


def _montar_resumo_listas_salvas(*, ministerio, igreja_ativa, perfis):
    resumo = []
    for perfil in perfis:
        total_filtrados, total_aptos = _calcular_totais_lista_salva(
            ministerio=ministerio,
            igreja_ativa=igreja_ativa,
            filtros=perfil.filtros,
        )
        resumo.append(
            {
                'id': perfil.pk,
                'nome': perfil.nome,
                'igreja_nome': perfil.igreja.nome_igreja if perfil.igreja else 'Ministerio',
                'favorita': bool(perfil.favorita),
                'total_filtrados': total_filtrados,
                'total_aptos': total_aptos,
            }
        )
    return resumo


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
    if status in ('SCAN_QR_CODE', 'STOPPED', 'OFFLINE', 'UNKNOWN', 'FAILED', None):
        qr_data = get_waha_qr_code(config)
        if qr_data and status in ('STOPPED', 'UNKNOWN', 'FAILED', None):
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
        status_pessoa = filtrar_status_whatsapp_para_tipos(status_pessoa, tipos_pessoa)

        membros_qs = filtrar_membros_whatsapp_destino(
            ministerio=ministerio,
            igreja_ativa=igreja_ativa,
            tipos_pessoa=tipos_pessoa,
            graus_eclesiasticos=filtros['graus_eclesiasticos'],
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
    status_pessoa = filtrar_status_whatsapp_para_tipos(status_pessoa, tipos_pessoa)

    membros_qs = filtrar_membros_whatsapp_destino(
        ministerio=ministerio,
        igreja_ativa=igreja_ativa,
        tipos_pessoa=tipos_pessoa,
        graus_eclesiasticos=filtros['graus_eclesiasticos'],
        status_pessoa=status_pessoa,
        aniversariantes_do_mes=filtros['aniversariantes_do_mes'],
        somente_com_celular=False,
    ).order_by('nome', 'pk')

    total_membros = membros_qs.count()
    total_com_celular = membros_qs.exclude(celular__isnull=True).exclude(celular__exact='').count()
    total_sem_celular = max(total_membros - total_com_celular, 0)

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
            'total_membros': total_membros,
            'total_com_celular': total_com_celular,
            'total_sem_celular': total_sem_celular,
            'titulo_pagina': 'Editar Celulares em Massa',
        },
    )


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def enviar_whatsapp_massa(request):
    ministerio = get_ministerio_or_error(request)
    igreja_ativa = request.igreja_ativa
    automacao_aniversarios = obter_automacao_aniversariantes(ministerio=ministerio)
    agendamentos_aniversario = listar_agendamentos_aniversariantes(ministerio=ministerio)
    proximos_aniversariantes = listar_proximos_aniversariantes(
        ministerio=ministerio,
        igreja=igreja_ativa,
    )
    config_global_ativa = WhatsAppConfiguracaoGlobal.objects.filter(
        ministerio=ministerio,
        ativo=True,
    ).exists()
    perfis_filtro = _queryset_perfis_whatsapp_massa(ministerio=ministerio, igreja_ativa=igreja_ativa)
    perfil_id = request.GET.get('perfil_id')
    perfil_selecionado = _carregar_perfil_whatsapp_massa(
        ministerio=ministerio,
        igreja_ativa=igreja_ativa,
        perfil_id=perfil_id,
    )
    if not perfil_id:
        perfil_selecionado = perfis_filtro.filter(favorita=True).first()
    perfis_filtro_resumo = _montar_resumo_listas_salvas(
        ministerio=ministerio,
        igreja_ativa=igreja_ativa,
        perfis=perfis_filtro,
    )

    if request.method == 'POST' and request.POST.get('acao') == 'aplicar_perfil':
        perfil_id_post = request.POST.get('perfil_id')
        if not perfil_id_post:
            return redirect('comunicacao:enviar_whatsapp_massa')
        perfil = _carregar_perfil_whatsapp_massa(
            ministerio=ministerio,
            igreja_ativa=igreja_ativa,
            perfil_id=perfil_id_post,
        )
        if not perfil:
            messages.warning(request, 'Selecione uma lista valida para aplicar.')
            return redirect('comunicacao:enviar_whatsapp_massa')
        return redirect(f"{reverse('comunicacao:enviar_whatsapp_massa')}?perfil_id={perfil.pk}")

    if request.method == 'POST':
        form = WhatsAppMassaForm(request.POST, ministerio=ministerio)
        if form.is_valid():
            mensagem = form.cleaned_data['mensagem']
            tipos_pessoa = form.cleaned_data['tipos_pessoa']
            graus_eclesiasticos = form.cleaned_data['graus_eclesiasticos']
            status_pessoa = form.cleaned_data['status_pessoa']
            aniversariantes_do_mes = form.cleaned_data['aniversariantes_do_mes']
            somente_com_celular = form.cleaned_data['somente_com_celular']

            membros_qs = filtrar_membros_whatsapp_destino(
                ministerio=ministerio,
                igreja_ativa=igreja_ativa,
                tipos_pessoa=tipos_pessoa,
                graus_eclesiasticos=graus_eclesiasticos,
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
        form = WhatsAppMassaForm(
            ministerio=ministerio,
            initial=_filtros_iniciais_por_perfil(perfil_selecionado),
        )

    return render(
        request,
        'comunicacao/whatsapp/form_whatsapp_massa.html',
        {
            'form': form,
            'ministerio': ministerio,
            'igreja_ativa': igreja_ativa,
            'automacao_aniversarios': automacao_aniversarios,
            'agendamentos_aniversario': agendamentos_aniversario,
            'proximos_aniversariantes': proximos_aniversariantes,
            'config_global_ativa': config_global_ativa,
            'perfis_filtro_resumo': perfis_filtro_resumo,
            'perfil_selecionado': perfil_selecionado,
            'titulo_pagina': 'Enviar WhatsApp em Massa',
        },
    )


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
@require_POST
def salvar_perfil_filtro_whatsapp_massa(request):
    ministerio = get_ministerio_or_error(request)
    igreja_ativa = request.igreja_ativa
    nome = (request.POST.get('perfil_nome') or '').strip()

    if not nome:
        messages.warning(request, 'Informe um nome para salvar a lista.')
        return redirect('comunicacao:enviar_whatsapp_massa')

    marcar_favorita = request.POST.get('lista_favorita') in ('on', 'true', '1')

    filtros = _montar_filtros_para_perfil(
        request=request,
        tipos_pessoa_ids=[int(v) for v in request.POST.getlist('tipos_pessoa') if str(v).isdigit()],
        status_pessoa_ids=[int(v) for v in request.POST.getlist('status_pessoa') if str(v).isdigit()],
        graus_eclesiasticos=[v for v in request.POST.getlist('graus_eclesiasticos') if v],
        aniversariantes_do_mes=request.POST.get('aniversariantes_do_mes') in ('on', 'true', '1'),
        somente_com_celular=request.POST.get('somente_com_celular') in ('on', 'true', '1'),
    )

    perfil, criado = WhatsAppFiltroPerfil.objects.update_or_create(
        ministerio=ministerio,
        igreja=igreja_ativa,
        nome=nome,
        defaults={
            'filtros': filtros,
            'favorita': marcar_favorita,
            'criado_por': request.user,
        },
    )

    if marcar_favorita:
        _desmarcar_outras_listas_favoritas(
            ministerio=ministerio,
            igreja_ativa=igreja_ativa,
            perfil_id=perfil.pk,
        )

    if criado:
        messages.success(request, f'Lista "{perfil.nome}" salva com sucesso.')
    else:
        messages.success(request, f'Lista "{perfil.nome}" atualizada com sucesso.')

    if marcar_favorita:
        messages.info(request, f'Lista "{perfil.nome}" definida como favorita.')

    return redirect(f"{reverse('comunicacao:enviar_whatsapp_massa')}?perfil_id={perfil.pk}")


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
@require_POST
def excluir_perfil_filtro_whatsapp_massa(request):
    ministerio = get_ministerio_or_error(request)
    igreja_ativa = request.igreja_ativa

    perfil = _carregar_perfil_whatsapp_massa(
        ministerio=ministerio,
        igreja_ativa=igreja_ativa,
        perfil_id=request.POST.get('perfil_id'),
    )
    if not perfil:
        messages.warning(request, 'Lista salva nao encontrada para exclusao.')
        return redirect('comunicacao:enviar_whatsapp_massa')

    nome = perfil.nome
    perfil.delete()
    messages.success(request, f'Lista "{nome}" removida com sucesso.')
    return redirect('comunicacao:enviar_whatsapp_massa')


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

        endpoint = f"{base_url}/api/sessions/default"
        start = time.time()
        resp = requests.get(endpoint, headers=headers, timeout=(5, 10))
        elapsed = (time.time() - start) * 1000

        if resp.status_code >= 400:
            detalhe = (resp.text or '').strip()[:180]
            return JsonResponse(
                {
                    'ok': False,
                    'status': resp.status_code,
                    'tempo_ms': round(elapsed, 2),
                    'error': (
                        f'WAHA respondeu com HTTP {resp.status_code} em {elapsed:.0f}ms '
                        f'na URL {endpoint}. {detalhe}'
                    ),
                    'base_url': base_url,
                }
            )

        return JsonResponse(
            {
                'ok': True,
                'status': resp.status_code,
                'tempo_ms': round(elapsed, 2),
                'mensagem': f'WAHA respondeu em {elapsed:.0f}ms - Status: {resp.status_code} ({base_url})',
                'base_url': base_url,
            }
        )
    except RequestsConnectionError:
        elapsed = (time.time() - start) * 1000 if 'start' in locals() else None
        tempo_info = f' ({elapsed:.0f}ms)' if elapsed else ''
        base_url = locals().get('base_url', 'N/D')
        if 'localhost' in (base_url or '') or '127.0.0.1' in (base_url or ''):
            msg = (
                f'Falha ao conectar WAHA{tempo_info}: nenhum servidor encontrado em {base_url}. '
                'Ajuste a variável de ambiente WAHA_BASE_URL para a URL real do servidor WAHA '
                '(ou configure via painel técnico/admin avançado).'
            )
        else:
            msg = (
                f'Falha ao conectar WAHA{tempo_info} em {base_url}. '
                'Verifique se o servidor WAHA está online e acessível a partir da aplicação.'
            )
        return JsonResponse({'ok': False, 'error': msg, 'base_url': base_url})
    except ReadTimeout:
        elapsed = (time.time() - start) * 1000 if 'start' in locals() else None
        tempo_info = f' ({elapsed:.0f}ms)' if elapsed else ''
        base_url = locals().get('base_url', 'N/D')
        return JsonResponse(
            {
                'ok': False,
                'error': (
                    f'Timeout ao conectar WAHA{tempo_info} em {base_url}. '
                    'O servidor pode estar frio/lento ou indisponível temporariamente.'
                ),
                'base_url': base_url,
            }
        )
    except Exception as exc:
        elapsed = (time.time() - start) * 1000 if 'start' in locals() else None
        tempo_info = f' ({elapsed:.0f}ms)' if elapsed else ''
        base_url = locals().get('base_url', 'N/D')
        return JsonResponse(
            {
                'ok': False,
                'error': f'Falha ao conectar WAHA{tempo_info} em {base_url}: {str(exc)[:200]}',
                'base_url': base_url,
            }
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
