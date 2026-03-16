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

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
if not CLOUDINARY_STORAGE['CLOUD_NAME']:
    raise Exception("CLOUDINARY_CLOUD_NAME não está definida!")
MEDIA_URL = '/media/'

from django.core.files.storage import default_storage
from django.utils.module_loading import import_string
default_storage._wrapped = import_string(DEFAULT_FILE_STORAGE)()

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
    'widget_tweaks',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
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
    'storages',
    'cloudinary',
    'cloudinary_storage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.DatabaseErrorMiddleware',  # Captura erros de BD e mostra página amigável
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.PermissionDeniedMiddleware',  # Captura PermissionDenied e mostra 403.html
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
                'core.context_processors.sistema_nome',
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
    LOGGING['loggers']['financeiro']['handlers'].append('file')
    LOGGING['loggers']['django']['handlers'].append('file')

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
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
