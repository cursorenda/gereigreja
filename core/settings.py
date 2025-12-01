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

# --- CONFIGURAÇÕES DE SEGURANÇA RECOMENDADAS PARA PRODUÇÃO ---


# --- CONFIGURAÇÕES DE SEGURANÇA RECOMENDADAS PARA PRODUÇÃO ---

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
if not CLOUDINARY_STORAGE['CLOUD_NAME']:
    raise Exception("CLOUDINARY_CLOUD_NAME não está definida!")
MEDIA_URL = '/media/'

# --- Força o default_storage a usar o backend correto em runtime ---
from django.core.files.storage import default_storage
from django.utils.module_loading import import_string
default_storage._wrapped = import_string(DEFAULT_FILE_STORAGE)()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Em produção, carregue de uma variável de ambiente. Gere uma nova chave forte.
# Ex: no painel da hospedagem, defina DJANGO_SECRET_KEY='sua-nova-chave-super-secreta-aqui'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-r$cs+v_ad_nqusa5-_=ig)sn^*g*c5^ey&t#_$xkn36=pwr@52') # Fallback apenas para desenvolvimento local

# Em produção, carregue de uma variável de ambiente. Gere uma nova chave forte.

# SECURITY WARNING: don't run with debug turned on in production!
# Em produção, defina a variável de ambiente DJANGO_DEBUG='False' no painel da hospedagem.
# --- CONFIGURAÇÕES DE SEGURANÇA RECOMENDADAS PARA PRODUÇÃO ---
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'
if not DEBUG:
    SECURE_SSL_REDIRECT = True  # Redireciona todo tráfego HTTP para HTTPS
    SESSION_COOKIE_SECURE = True  # Cookies de sessão só via HTTPS
    CSRF_COOKIE_SECURE = True  # Cookies CSRF só via HTTPS
    SECURE_HSTS_SECONDS = 31536000  # HSTS por 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_HTTPONLY = True  # Cookies de sessão não acessíveis via JS
    CSRF_COOKIE_HTTPONLY = True  # Cookies CSRF não acessíveis via JS
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protege contra CSRF
    CSRF_COOKIE_SAMESITE = 'Lax'
    SECURE_REFERRER_POLICY = 'same-origin'  # Política de referência
    SECURE_CONTENT_TYPE_NOSNIFF = True  # Protege contra ataques de MIME
    X_FRAME_OPTIONS = 'DENY'  # Protege contra clickjacking
# ALLOWED_HOSTS deve conter os domínios/IPs que servirão sua aplicação.
ALLOWED_HOSTS = ['gereigreja.site', 'www.gereigreja.site', '199.167.147.66', 'localhost', '127.0.0.1']

# Para produção, é importante definir os hosts confiáveis para requisições POST.
CSRF_TRUSTED_ORIGINS = [
    'https://gereigreja.site',
    'https://www.gereigreja.site',
]
# --- Configuração para Produção na Render ---
# A Render injeta automaticamente a variável de ambiente RENDER_EXTERNAL_HOSTNAME
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
    'django.contrib.humanize', # <<< ADICIONE ESTA LINHA
    'django.contrib.sites', # <<< ADICIONAR SE NÃO EXISTIR
    'whitenoise.runserver_nostatic', # Adicionar Whitenoise (útil até mesmo em dev sem DEBUG=True para estáticos)
    'django_extensions', # Adicionar para usar shell_plus e outros comandos

    # Seus Apps
    'secretaria',
    'financeiro',
    'configuracao',
    'contas',
    'comunicacao', 
    'agenda',  # Novo app de agenda
    'eventos',  # App de eventos
    'suporte',
    'escola_biblica',
    'storages', # <- Move 'storages' here
    'cloudinary',
    'cloudinary_storage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Adicionar Whitenoise aqui
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.ActiveChurchMiddleware', # Adicionado nosso middleware
    'secretaria.middleware.DisableCacheMiddleware',  # Remova a linha comentada se esta é a ativa. Avalie a necessidade em produção.
    # 'comunicacao', # <<< REMOVA OU COMENTE ESTA LINHA

]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [

            BASE_DIR / 'templates',  # Usando pathlib para consistência
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.unread_notifications', # Adicionado para o contador de notificações
                'core.context_processors.sistema_nome', # Nome do sistema para o footer
            ],
        },
    },
]

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] # Usando pathlib para consistência
STATIC_ROOT = BASE_DIR / 'staticfiles_production' # Usando pathlib
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # Para Whitenoise

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# --- CONFIGURAÇÃO DO BANCO DE DADOS SUPABASE(LIDO DO ARQUIVO .ENV) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'CONN_MAX_AGE': 0,  # Desativa o pool padrão do Django
      
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

# core/settings.py
LANGUAGE_CODE = 'pt-br'
# USE_L10N = True # Obsoleto no Django 4.0+. True é o comportamento padrão se USE_I18N = True.
USE_I18N = True
USE_THOUSAND_SEPARATOR = True
# Opcional, mas explícito para pt-br:
# DECIMAL_SEPARATOR = ','
# THOUSAND_SEPARATOR = '.'
# NUMBER_GROUPING = 3
TIME_ZONE = 'America/Sao_Paulo'
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

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
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        # O handler 'file' será adicionado condicionalmente abaixo para desenvolvimento.
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
        # --- LOGGING DETALHADO PARA S3 ---
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

# --- LÓGICA CONDICIONAL PARA LOGGING EM ARQUIVO ---
# Apenas em ambiente de desenvolvimento (DEBUG=True), tentamos logar para um arquivo.
# Em produção (Render), os logs irão para o console e serão capturados pela plataforma.
if DEBUG:
    LOGS_DIR = BASE_DIR / 'logs'
    LOGS_DIR.mkdir(exist_ok=True) # Cria a pasta 'logs' se não existir (para dev local)

    LOGGING['handlers']['file'] = {
        'level': 'ERROR',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': LOGS_DIR / 'django_errors.log',
        'maxBytes': 1024 * 1024 * 5,  # 5 MB
        'backupCount': 5,
        'formatter': 'verbose',
    }
    # Adiciona o handler de arquivo aos loggers
    LOGGING['loggers']['financeiro']['handlers'].append('file')
    LOGGING['loggers']['django']['handlers'].append('file')

# ... (outras configurações) ...


# MEDIA_URL = '/media/'

# MEDIA_ROOT = BASE_DIR / 'media' # Usando pathlib

# Em produção na Render, o caminho do disco persistente é definido por uma variável de ambiente.
# O padrão é '/var/data'. Se você montou em '/var/www/media', use esse caminho.
# A melhor prática é usar uma variável de ambiente para isso também.
# MEDIA_ROOT = os.environ.get('DJANGO_MEDIA_ROOT', BASE_DIR / 'media')

LOGIN_URL = '/accounts/login/' # URL para onde @login_required redireciona (já está funcionando)
LOGIN_REDIRECT_URL = '/sistema/' # URL para onde o usuário vai APÓS o login SE NENHUM 'next' for especificado
LOGOUT_REDIRECT_URL = '/' # URL para onde o usuário vai APÓS fazer logout (opcional, mas bom ter)

# Configuração de E-mail (Usando Brevo/Sendinblue SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'  # Ou smtp-relay.sendinblue.com
EMAIL_PORT = 587                     # Porta 465 geralmente usa SSL
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True  # Usar TLS (recomendado para porta 587)

# Carregue de variáveis de ambiente em produção
EMAIL_HOST_USER = '8b9a59002@smtp-brevo.com' # <<< CORRIGIDO: Este é o seu Login SMTP fornecido pelo Brevo
# A linha abaixo tenta ler a variável de ambiente 'gereigreja_email_password'.

# Se não encontrar, e você estiver em DEBUG=True (localmente), pode usar uma senha padrão para teste.
# NUNCA deixe uma senha real como padrão se DEBUG=False.
EMAIL_HOST_PASSWORD = os.environ.get('gereigreja_email_password')

# Para desenvolvimento local, se você ainda não configurou a variável de ambiente
# e precisa testar, você pode temporariamente fazer:
# if DEBUG and not EMAIL_HOST_PASSWORD:
#     EMAIL_HOST_PASSWORD = 'sua_senha_real_para_teste_local'
# Verifique se a senha foi carregada, especialmente em produção
if not DEBUG and not EMAIL_HOST_PASSWORD:
    raise ValueError("A variável de ambiente gereigreja_email_password não está configurada para produção.")

DEFAULT_FROM_EMAIL = 'Gereigreja <nao-responda@gereigreja.site>' # E-mail que aparecerá como remetente
SERVER_EMAIL = DEFAULT_FROM_EMAIL # Para e-mails de erro do servidor (enviados para ADMINS)
ADMINS = [('sr. Júlio ', 'juliobsouza24@gmail.com')] # E-mail para onde o Django envia erros críticos

SITE_ID = 2

# --- STRIPE CONFIGURATION ---
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')



CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
