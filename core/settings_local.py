"""Settings locais seguros, sem leitura do ``.env`` e sem banco remoto."""

import os

import dotenv


# Impede que o modulo legado carregue credenciais enquanto esta configuracao
# reaproveita as definicoes comuns ainda concentradas nele.
_load_dotenv_original = dotenv.load_dotenv
dotenv.load_dotenv = lambda *args, **kwargs: False

# Valores seguros precisam existir antes do import das configuracoes comuns.
os.environ['DJANGO_DEBUG'] = 'True'
os.environ['DJANGO_SECRET_KEY'] = 'gereigreja-local-only-not-for-production'
for _variable in (
    'DB_NAME',
    'DB_USER',
    'DB_PASSWORD',
    'DB_HOST',
    'DB_PORT',
    'CLOUDINARY_CLOUD_NAME',
    'CLOUDINARY_API_KEY',
    'CLOUDINARY_API_SECRET',
    'STRIPE_PUBLISHABLE_KEY',
    'STRIPE_SECRET_KEY',
    'STRIPE_WEBHOOK_SECRET',
    'WAHA_API_KEY',
    'RAILWAY_API_TOKEN',
    'RAILWAY_PROJECT_ID',
    'RAILWAY_WAHA_SERVICE_ID',
    'RAILWAY_WORKSPACE_ID',
    'gereigreja_email_password',
):
    os.environ[_variable] = ''
os.environ['WAHA_BASE_URL'] = 'http://localhost:3000'

try:
    from .settings import *  # noqa: F401,F403
finally:
    dotenv.load_dotenv = _load_dotenv_original


SETTINGS_ENVIRONMENT = 'local'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

