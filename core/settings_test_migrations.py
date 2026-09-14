"""Configuração isolada para testes reais de migrations em SQLite temporário."""

from .settings_test import *  # noqa: F401,F403


# settings_test desabilita migrations para testes funcionais rápidos. Aqui elas
# permanecem habilitadas para validar transformações históricas de dados.
MIGRATION_MODULES = {}

# Reafirma o banco local e descartável, sem host, usuário ou credencial externa.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
