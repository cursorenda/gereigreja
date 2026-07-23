import base64
import logging
import re
import time

import requests
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError
from requests.exceptions import ReadTimeout

from .models import WhatsAppMensagemLog

logger = logging.getLogger(__name__)


class WhatsAppSendError(Exception):
    pass


def _is_core_default_only_response(response):
    if response is None or response.status_code != 422:
        return False
    try:
        data = response.json()
    except ValueError:
        return False
    message = (data.get('message') or '').lower()
    return "only 'default' session" in message


def _resolve_session_name(configuracao):
    """Resolve a sessao a usar; WAHA Core aceita apenas 'default'."""
    session = configuracao.get_session_name()
    base_url = configuracao.waha_url_efetiva.rstrip('/')
    headers = _waha_headers(configuracao)
    if session == 'default':
        return session

    try:
        resp = requests.get(f"{base_url}/api/sessions/{session}", headers=headers, timeout=5)
        if resp.status_code == 200:
            return session
        if _is_core_default_only_response(resp):
            return 'default'
        # Em algumas instalacoes (ou configuracoes atuais) apenas a sessao
        # 'default' existe; quando a sessao por congregacao retorna 404,
        # usamos 'default' se ela estiver disponivel.
        if resp.status_code == 404:
            default_resp = requests.get(f"{base_url}/api/sessions/default", headers=headers, timeout=5)
            if default_resp.status_code == 200:
                return 'default'
    except Exception:
        pass
    return session


def normalize_phone_to_chat_id(phone_raw):
    digits = re.sub(r'\D', '', phone_raw or '')
    if not digits:
        return None, None
    if not digits.startswith('55'):
        digits = f'55{digits}'
    return digits, f'{digits}@c.us'


def _resolve_chat_id_for_send(base_url, headers, session, numero_normalizado):
    """Resolve chatId canônico via WAHA (LID), com fallback para c.us."""
    fallback_chat_id = f'{numero_normalizado}@c.us'
    try:
        resp = requests.get(
            f"{base_url}/api/contacts/check-exists",
            headers=headers,
            params={"session": session, "phone": numero_normalizado},
            timeout=8,
        )
        if resp.status_code == 200:
            data = resp.json() if resp.content else {}
            number_exists = data.get('numberExists')
            if number_exists is False:
                return None, 'Numero sem conta WhatsApp ativa ou invalido.'
            chat_id = data.get('chatId')
            if chat_id:
                return chat_id, None
    except Exception:
        pass

    return fallback_chat_id, None


def _waha_headers(configuracao):
    headers = {'Content-Type': 'application/json'}
    key = configuracao.waha_key_efetiva
    if key:
        headers['X-Api-Key'] = key
    return headers


def _start_waha_session(base_url, headers, session):
    start_resp = requests.post(
        f"{base_url}/api/sessions/start",
        json={"name": session},
        headers=headers,
        timeout=8,
    )
    if start_resp.status_code in (404, 405):
        start_resp = requests.post(
            f"{base_url}/api/sessions/{session}/start",
            json={},
            headers=headers,
            timeout=8,
        )
    return start_resp


def _recover_failed_session(base_url, headers, session):
    """Tenta recuperar sessao WAHA em FAILED com stop + start."""
    try:
        requests.post(
            f"{base_url}/api/sessions/stop",
            json={"name": session},
            headers=headers,
            timeout=8,
        )
    except Exception:
        pass

    try:
        requests.post(
            f"{base_url}/api/sessions/{session}/stop",
            json={},
            headers=headers,
            timeout=8,
        )
    except Exception:
        pass

    try:
        _start_waha_session(base_url, headers, session)
    except Exception:
        pass


def _format_http_error(response):
    """Gera mensagem de erro mais útil com status e corpo de resposta da WAHA."""
    if response is None:
        return 'Falha HTTP ao enviar WhatsApp (sem resposta do servidor).'

    body = ''
    try:
        data = response.json()
        body = (
            data.get('message')
            or data.get('error')
            or (data.get('exception') or {}).get('message')
            or str(data)
        )
    except Exception:
        body = (response.text or '').strip()

    if body:
        if 'no lid for user' in body.lower():
            return (
                'Numero de destino invalido ou sem WhatsApp ativo para esta sessao. '
                'Confirme o celular com DDD e WhatsApp ativo.'
            )
        # Detectar erro de sessão desconectada do Chromium/Puppeteer
        if 'protocol error' in body.lower() or 'runtime.callfunctionon' in body.lower():
            return (
                'Sessao WhatsApp desconectada internamente no WAHA (Protocol error). '
                'Acesse "Configurar WAHA" e reconecte a sessao escaneando o QR novamente.'
            )
        body = body[:400]
        return f'WAHA HTTP {response.status_code}: {body}'
    return f'WAHA HTTP {response.status_code} sem detalhes no corpo da resposta.'


def send_whatsapp_text(configuracao, phone, text, *, tipo='outro', ministerio=None, igreja=None, membro=None):
    numero_normalizado, chat_id = normalize_phone_to_chat_id(phone)
    if not chat_id:
        raise WhatsAppSendError('Numero de telefone invalido para envio WhatsApp.')

    session = _resolve_session_name(configuracao)
    url = f"{configuracao.waha_url_efetiva.rstrip('/')}/api/sendText"
    payload = {'session': session, 'chatId': chat_id, 'text': text}
    headers = _waha_headers(configuracao)
    base_url = configuracao.waha_url_efetiva.rstrip('/')

    resolved_chat_id, resolve_error = _resolve_chat_id_for_send(
        base_url,
        headers,
        session,
        numero_normalizado,
    )
    if resolve_error:
        raise WhatsAppSendError(resolve_error)
    if resolved_chat_id:
        chat_id = resolved_chat_id
        payload['chatId'] = chat_id

    try:
        max_tentativas = 3
        response = None
        for tentativa in range(1, max_tentativas + 1):
            try:
                # Timeout mais tolerante para instancias WAHA frias/lentas no Railway.
                response = requests.post(url, json=payload, headers=headers, timeout=(10, 75))
                # Erros 5xx da WAHA podem ser transitórios no Railway; tenta novamente antes de falhar.
                if response.status_code >= 500 and tentativa < max_tentativas:
                    time.sleep(tentativa)
                    continue
                break
            except (ReadTimeout, RequestsConnectionError):
                if tentativa >= max_tentativas:
                    raise

                # Warm-up: força verificação de sessão para "acordar" a instância antes de tentar de novo.
                try:
                    requests.get(f"{base_url}/api/sessions/default", headers=headers, timeout=(5, 20))
                except Exception:
                    pass
                time.sleep(tentativa)

        if response is None:
            raise WhatsAppSendError('Falha ao enviar WhatsApp: resposta vazia do servidor WAHA.')

        response.raise_for_status()
        response_data = response.json() if response.content else {'ok': True}

        WhatsAppMensagemLog.objects.create(
            ministerio=ministerio or configuracao.ministerio,
            igreja=igreja or configuracao.igreja,
            membro=membro,
            configuracao=configuracao,
            tipo=tipo,
            status='sucesso',
            telefone_destino=numero_normalizado,
            chat_id=chat_id,
            mensagem=text,
            resposta_waha=response_data,
        )
        return response_data
    except Exception as exc:
        if isinstance(exc, HTTPError):
            err_text = _format_http_error(getattr(exc, 'response', None))
        elif isinstance(exc, ReadTimeout):
            err_text = 'Timeout ao enviar para WAHA. O servidor pode estar frio/lento; tente novamente em alguns segundos.'
        else:
            err_text = str(exc)
        logger.exception('Falha ao enviar mensagem WhatsApp via WAHA')
        WhatsAppMensagemLog.objects.create(
            ministerio=ministerio or configuracao.ministerio,
            igreja=igreja or configuracao.igreja,
            membro=membro,
            configuracao=configuracao,
            tipo=tipo,
            status='erro',
            telefone_destino=numero_normalizado or phone,
            chat_id=chat_id,
            mensagem=text,
            erro=err_text,
        )
        raise WhatsAppSendError(err_text) from exc


def get_waha_session_status(configuracao):
    """Retorna o status da sessao WAHA: WORKING, SCAN_QR_CODE, STOPPED, etc."""
    session = _resolve_session_name(configuracao)
    base_url = configuracao.waha_url_efetiva.rstrip('/')
    headers = _waha_headers(configuracao)
    try:
        resp = requests.get(f"{base_url}/api/sessions/{session}", headers=headers, timeout=5)
        if resp.status_code == 200:
            return resp.json().get('status', 'UNKNOWN')
        if resp.status_code == 404:
            return 'STOPPED'
        if _is_core_default_only_response(resp):
            resp = requests.get(f"{base_url}/api/sessions/default", headers=headers, timeout=5)
            if resp.status_code == 200:
                return resp.json().get('status', 'UNKNOWN')
            if resp.status_code == 404:
                return 'STOPPED'
        return 'UNKNOWN'
    except Exception:
        return 'OFFLINE'


def get_waha_qr_code(configuracao):
    """
    Inicia a sessao WAHA se necessario e retorna o QR code como data URL (base64).
    Retorna None se a sessao ja estiver conectada ou em caso de erro.
    """
    session = _resolve_session_name(configuracao)
    base_url = configuracao.waha_url_efetiva.rstrip('/')
    headers = _waha_headers(configuracao)

    # Se a sessao ficou em FAILED, forca ciclo de recuperacao antes do QR.
    try:
        sess_resp = requests.get(f"{base_url}/api/sessions/{session}", headers=headers, timeout=8)
        if sess_resp.status_code == 200:
            status = (sess_resp.json().get('status') or '').upper()
            if status == 'FAILED':
                _recover_failed_session(base_url, headers, session)
    except Exception:
        pass

    # Tenta iniciar a sessao antes de solicitar o QR.
    # Em muitas instalacoes, sessao STOPPED so passa a expor QR depois de start.
    try:
        start_resp = _start_waha_session(base_url, headers, session)

        # Se a sessao ainda nao existir, cria e tenta iniciar novamente.
        if start_resp.status_code == 404 and session != 'default':
            create_resp = requests.post(
                f"{base_url}/api/sessions",
                json={"name": session},
                headers=headers,
                timeout=8,
            )
            if create_resp.status_code in (200, 201, 409):
                _start_waha_session(base_url, headers, session)

        if _is_core_default_only_response(start_resp):
            session = 'default'
            requests.post(
                f"{base_url}/api/sessions/start",
                json={"name": "default"},
                headers=headers,
                timeout=8,
            )
    except Exception:
        pass

    # Busca o QR code
    try:
        resp = requests.get(f"{base_url}/api/{session}/auth/qr", headers=headers, timeout=10)
        if resp.status_code != 200:
            # Nova tentativa apos pequena pausa para dar tempo do WAHA concluir STARTING.
            time.sleep(1)
            resp = requests.get(f"{base_url}/api/{session}/auth/qr", headers=headers, timeout=10)
        if _is_core_default_only_response(resp):
            session = 'default'
            resp = requests.get(
                f"{base_url}/api/{session}/auth/qr",
                headers=headers,
                timeout=10,
            )
        if resp.status_code != 200 and session != 'default':
            # Alguns ambientes mantem apenas o QR no endpoint da sessao default.
            fallback_resp = requests.get(
                f"{base_url}/api/default/auth/qr",
                headers=headers,
                timeout=10,
            )
            if fallback_resp.status_code == 200:
                resp = fallback_resp

        if resp.status_code != 200:
            return None
        content_type = resp.headers.get('content-type', '')
        if 'image' in content_type:
            b64 = base64.b64encode(resp.content).decode()
            return f"data:{content_type};base64,{b64}"
        # Resposta JSON com campo value ou qr
        data = resp.json()
        return data.get('value') or data.get('qr')
    except Exception:
        return None
