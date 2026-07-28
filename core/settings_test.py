"""Test settings: import the main settings and override the database to use
an in-memory SQLite database. This avoids creating/dropping a remote Postgres
test database (useful when your DB is hosted on Supabase or another provider
that doesn't allow DB creation/deletion).

Use by running:

    python manage.py test <tests> --settings=core.settings_test

This file also speeds up tests by using the MD5 password hasher and a
lightweight email backend.
"""

from .settings import *  # noqa: F401,F403

# Use a fast, in-memory SQLite DB for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use fast password hasher for tests to speed up user creation
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Avoid using cloudinary/remote storage during tests
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': None,
    'API_KEY': None,
    'API_SECRET': None,
}

# Use in-memory email backend so tests don't try to send real emails
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Some tests may create files; ensure MEDIA_ROOT is writable in the project
import tempfile
MEDIA_ROOT = tempfile.mkdtemp(prefix='gereigreja_test_media_')

# Some apps in this project have complex or duplicated migration files that make
# running the full migration sequence in a fresh in-memory DB fail (duplicate
# CreateModel operations). For quick unit test runs we can disable migrations
# for specific local apps so Django will create tables directly from models.
# Disable migrations only for the app(s) that cause problems in tests.
# Disable migrations for local project apps during tests. This makes Django
# create tables directly from models (syncdb) for these apps and avoids
# complex or conflicting migration histories that break in-memory test runs.
# If a test requires running real migrations for an app, remove it from this
# mapping.
PROJECT_TEST_MIGRATION_DISABLE = [
    'configuracao',
    'secretaria',
    'financeiro',
    'eventos',
    'agenda',
    'escola_biblica',
    'contas',
    'suporte',
    'auditoria',
    'comunicacao',
    'hinario',
    'painel_desenvolvedor',
    'notificacoes',
    'deploy',
    'blog',
]

MIGRATION_MODULES = {app: None for app in PROJECT_TEST_MIGRATION_DISABLE}
