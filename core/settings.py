from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR / 'secretaria' / 'templates'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-r$cs+v_ad_nqusa5-_=ig)sn^*g*c5^ey&t#_$xkn36=pwr@52'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize', # <<< ADICIONE ESTA LINHA
    'django.contrib.sites', # <<< ADICIONAR SE NÃO EXISTIR


    # Seus Apps
    'secretaria',
    'financeiro',
    'configuracao',
    'contas', # <<< ADICIONE ESTA LINHA

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'secretaria.middleware.DisableCacheMiddleware',  # Adicione esta linha

]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')

            #BASE_DIR / 'templates',  # Diretório de templates na raiz
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = 'static/'
#STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
       # 'NAME': BASE_DIR / 'bdmembros.db db.sqlite3',
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
USE_L10N = True
USE_I18N = True
USE_THOUSAND_SEPARATOR = True
# Opcional, mas explícito para pt-br:
# DECIMAL_SEPARATOR = ','
# THOUSAND_SEPARATOR = '.'
# NUMBER_GROUPING = 3
TIME_ZONE = 'UTC'

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'financeiro': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# ... (outras configurações) ...

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


LOGIN_URL = '/accounts/login/' # URL para onde @login_required redireciona (já está funcionando)
LOGIN_REDIRECT_URL = '/' # URL para onde o usuário vai APÓS o login SE NENHUM 'next' for especificado (ex: '/', '/dashboard/')
LOGOUT_REDIRECT_URL = '/' # URL para onde o usuário vai APÓS fazer logout (opcional, mas bom ter)

# core/settings.py

# Configuração de E-mail (Usando Brevo/Sendinblue SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'  # Ou smtp-relay.sendinblue.com
EMAIL_PORT = 587
EMAIL_USE_TLS = True  # Usar TLS (recomendado para porta 587)
EMAIL_HOST_USER = 'cursorenda@gmail.com'  # <<< SUBSTITUA PELO SEU EMAIL BREVO
EMAIL_HOST_PASSWORD = 'xsmtpsib-cfb0a4c4c63c5919662db2720a70a7953d6b9435da5c61f1570c445e8602aa6d-zWd5Uctx3R8E1XKC'  # <<< SUBSTITUA PELA CHAVE SMTP QUE VOCÊ COPIOU
DEFAULT_FROM_EMAIL = 'cursorenda@gmail.com' # <<< SUBSTITUA por um email verificado como remetente no Brevo (idealmente do seu domínio)

SITE_ID = 1

