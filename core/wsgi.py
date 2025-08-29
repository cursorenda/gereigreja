"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
# Força o backend de storage S3 e o settings module antes de qualquer import do Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
os.environ['DEFAULT_FILE_STORAGE'] = 'storages.backends.s3boto3.S3Boto3Storage'

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
