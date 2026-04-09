import pytest
import os
import django
import json

@pytest.mark.django_db
def test_create_visitante():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    import django as dj
    dj.setup()

    from django.test import Client
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # pick an active user to force_login
    user = User.objects.filter(is_active=True).first()
    if not user:
        print('NO_ACTIVE_USER_FOUND')
        raise SystemExit(1)

    c = Client()
    c.force_login(user)

    # Minimal payload: the view will inject tipo_pessoa/status/igreja server-side
    payload = {
        'nome': 'Teste Visitante Automático',
        'apelido': 'TstAuto'
    }

    resp = c.post('/sistema/visitantes/criar-parcial/', payload)
    print('STATUS', resp.status_code)
    try:
        body = resp.content.decode('utf-8')
        # try pretty-print JSON if possible
        try:
            parsed = json.loads(body)
            print('JSON RESPONSE:\n', json.dumps(parsed, ensure_ascii=False, indent=2))
        except Exception:
            print('RAW RESPONSE:\n', body)
    except Exception as e:
        print('ERROR READING RESPONSE:', e)
        print(resp.content)

    # If created, also try to register presence (optional)
    if resp.status_code == 200:
        try:
            visitante = json.loads(resp.content)
            vid = visitante.get('visitante', {}).get('id') or visitante.get('visitante', {}).get('id_str')
            print('CRIADO_ID:', vid)
        except Exception:
            pass
