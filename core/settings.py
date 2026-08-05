# --- CONFIGURAÇÕES DE SEGURANÇA RECOMENDADAS PARA PRODUÇÃO ---

import os
from pathlib import Path
from dotenv import load_dotenv # pip install python-dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env') # Carrega as variáveis do arquivo .env

# --- Cloudinary ---
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

# Durante o build do Render as env vars de runtime ainda não estão disponíveis.
# Só ativamos o storage Cloudinary quando a variável existir.
_IS_BUILD_PHASE = not os.environ.get('CLOUDINARY_CLOUD_NAME')

if _IS_BUILD_PHASE:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
else:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    # Força a inicialização do storage Cloudinary imediatamente
    # (necessário para django-cloudinary-storage 0.3.0 com Django 5.x)
    from django.core.files.storage import default_storage
    from django.utils.module_loading import import_string
    default_storage._wrapped = import_string(DEFAULT_FILE_STORAGE)()

MEDIA_URL = '/media/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-r$cs+v_ad_nqusa5-_=ig)sn^*g*c5^ey&t#_$xkn36=pwr@52') # Fallback apenas para desenvolvimento local

DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'
    SECURE_REFERRER_POLICY = 'same-origin'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

ALLOWED_HOSTS = ['gereigreja.site', 'www.gereigreja.site', '199.167.147.66', 'localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = [
    'https://gereigreja.site',
    'https://www.gereigreja.site',
]
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'whitenoise.runserver_nostatic',
    'django_extensions',
    'secretaria',
    'financeiro',
    'configuracao',
    'contas',
    'comunicacao',
    'agenda',
    'eventos',
    'suporte',
    'escola_biblica',
    'deploy',
    'core',
    'auditoria.apps.AuditoriaConfig',
    'painel_desenvolvedor',
    'storages',
    'cloudinary',
    'cloudinary_storage',
    'widget_tweaks',
    'notificacoes',
    'demo',
    'blog',
    'hinario.apps.HinarioConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.DatabaseErrorMiddleware',  # Captura erros de BD e mostra página amigável
    'core.middleware.ValidationErrorMiddleware',  # Captura ValidationError globalmente
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'auditoria.middleware.RegistrarAuditoriaMiddleware',
    'auditoria.middleware.BloquearEscritaModoAuditoriaMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.PermissionDeniedMiddleware',  # Captura PermissionDenied e mostra 403.html
    'auditoria.middleware.CapturarAcessoNegadoMiddleware',
    'core.middleware.VerificarGruposUsuarioMiddleware',  # Middleware para verificar se usuário tem grupos
    'core.middleware.ActiveChurchMiddleware',
    'secretaria.middleware.DisableCacheMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.deduplicate_assinatura_vencida',
                'core.context_processors.ministerio_context',
                'core.context_processors.unread_notifications',
                'core.context_processors.transferencias_pendentes_count',
                'core.context_status_plano.status_plano_unificado',
                'core.context_processors.sistema_nome',
                'core.context_processors.ultimos_cadastros',
                'auditoria.context_processors.modo_auditoria_flag',
                'configuracao.context_onboarding.onboarding_context',
            ],
        },
    },
]

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles_production'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'CONN_MAX_AGE': 0,
        'DISABLE_SERVER_SIDE_CURSORS': True,
        'CONN_HEALTH_CHECKS': False,  # Não verifica BD no startup
        'OPTIONS': {
            'connect_timeout': 5,  # Timeout rápido (5s em vez de padrão 60s+)
        }
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'pt-br'
USE_I18N = True
USE_THOUSAND_SEPARATOR = True
TIME_ZONE = 'America/Sao_Paulo'
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django_errors.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'eventos_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'eventos_presenca.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'financeiro': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'secretaria': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'configuracao': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'contas': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'eventos': {
            'handlers': ['eventos_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'comunicacao': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'suporte': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'boto3': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'botocore': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'storages': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

if DEBUG:
    LOGS_DIR = BASE_DIR / 'logs'
    LOGS_DIR.mkdir(exist_ok=True)
    LOGGING['handlers']['file'] = {
        'level': 'ERROR',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': LOGS_DIR / 'django_errors.log',
        'maxBytes': 1024 * 1024 * 5,
        'backupCount': 5,
        'formatter': 'verbose',
    }
    LOGGING['handlers']['eventos_file'] = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': LOGS_DIR / 'eventos_presenca.log',
        'maxBytes': 1024 * 1024 * 5,
        'backupCount': 5,
        'formatter': 'verbose',
    }
    LOGGING['loggers']['financeiro']['handlers'].append('file')
    LOGGING['loggers']['django']['handlers'].append('file')


DEV_FINANCEIRO_USERNAMES = [
    u.strip() for u in os.environ.get('DEV_FINANCEIRO_USERNAMES', '').split(',') if u.strip()
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/secretaria/'
LOGOUT_REDIRECT_URL = '/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '8b9a59002@smtp-brevo.com'
EMAIL_HOST_PASSWORD = os.environ.get('gereigreja_email_password')
if not DEBUG and not EMAIL_HOST_PASSWORD:
    raise ValueError("A variável de ambiente gereigreja_email_password não está configurada para produção.")
DEFAULT_FROM_EMAIL = 'Gereigreja <nao-responda@gereigreja.site>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
ADMINS = [('sr. Júlio ', 'juliobsouza24@gmail.com')]
SITE_ID = 2

# --- WAHA (WhatsApp HTTP API) ---
# Hospedado pela equipe tecnica. Nao exposto ao admin do ministerio.
WAHA_BASE_URL = os.environ.get('WAHA_BASE_URL', 'http://localhost:3000')
WAHA_API_KEY = os.environ.get('WAHA_API_KEY', '')

# --- Railway (custo/monitoramento WAHA) ---
# Alias suportados para facilitar compatibilidade entre ambientes.
RAILWAY_API_TOKEN = os.environ.get('RAILWAY_API_TOKEN', os.environ.get('RAILWAY_TOKEN', ''))
RAILWAY_PROJECT_ID = os.environ.get('RAILWAY_PROJECT_ID', os.environ.get('RAILWAY_PROJECT', ''))
RAILWAY_WAHA_SERVICE_ID = os.environ.get('RAILWAY_WAHA_SERVICE_ID', os.environ.get('RAILWAY_SERVICE_ID', ''))
RAILWAY_API_URL = os.environ.get('RAILWAY_API_URL', 'https://backboard.railway.com/graphql/v2')
# Workspace ID é descoberto automaticamente via me.workspaces quando o Account Token está ativo.
# Defina manualmente para acelerar a consulta e evitar a chamada extra à API.
RAILWAY_WORKSPACE_ID = os.environ.get('RAILWAY_WORKSPACE_ID', '')

STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
