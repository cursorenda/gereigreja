import logging
import re

import requests

from .models import WhatsAppMensagemLog

logger = logging.getLogger(__name__)


class WhatsAppSendError(Exception):
    pass


def normalize_phone_to_chat_id(phone_raw):
    digits = re.sub(r'\D', '', phone_raw or '')
    if not digits:
        return None, None
    if not digits.startswith('55'):
        digits = f'55{digits}'
    return digits, f'{digits}@c.us'


def send_whatsapp_text(configuracao, phone, text, *, tipo='outro', ministerio=None, igreja=None, membro=None):
    numero_normalizado, chat_id = normalize_phone_to_chat_id(phone)
    if not chat_id:
        raise WhatsAppSendError('Numero de telefone invalido para envio WhatsApp.')

    url = f"{configuracao.waha_base_url.rstrip('/')}/api/sendText"
    payload = {
        'session': configuracao.session_name,
        'chatId': chat_id,
        'text': text,
    }
    headers = {'Content-Type': 'application/json'}
    if configuracao.waha_api_key:
        headers['X-Api-Key'] = configuracao.waha_api_key

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
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
