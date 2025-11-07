django.setup()
import os
import sys
import psycopg2

# Garantir que o diretório do projeto esteja no sys.path (para importar settings)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Ajuste conforme manage.py: usar core.settings por padrão
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.db import connections
cfg = connections['default'].settings_dict
# Determinar nome do DB de teste (Django normalmente prefixa com 'test_')
default_name = cfg.get('NAME')
if default_name.startswith('test_'):
    test_db = default_name
else:
    test_db = 'test_' + default_name

print('Will attempt to drop test database:', test_db)

# Conectar ao postgres para executar DROP DATABASE
connect_db = cfg.get('NAME')
# connect to maintenance DB 'postgres'
conn = None
try:
    conn = psycopg2.connect(dbname='postgres', user=cfg.get('USER'), password=cfg.get('PASSWORD'), host=cfg.get('HOST') or 'localhost', port=cfg.get('PORT') or 5432)
    conn.autocommit = True
    cur = conn.cursor()
    # terminate backends
    cur.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s;", (test_db,))
    cur.execute(f"DROP DATABASE IF EXISTS {test_db};")
    cur.close()
    print('Dropped test DB:', test_db)
except Exception as e:
    print('Error dropping test DB:', e)
finally:
    if conn:
        conn.close()
