from django.contrib import admin
from django.urls import path
from django.http import HttpResponse, FileResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View

import subprocess
import os
import datetime
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# View para backup custom
@staff_member_required
def backup_custom(request):
    filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.dump"
    filepath = os.path.join('backup', filename)
    cmd = [
        'pg_dump',
        '-h', 'aws-0-us-east-2.pooler.supabase.com',
        '-U', 'postgres.vxzntgknvejluffgttpg',
        '-d', 'postgres',
        '-F', 'c',
        '-b',
        '-v',
        '-f', filepath
    ]
    env = os.environ.copy()
    env['PGPASSWORD'] = os.environ.get('PGPASSWORD', '')  # Segura: variável de ambiente
    try:
        subprocess.run(cmd, check=True, env=env)
        response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
        return response
    except Exception as e:
        return HttpResponse(f'Erro ao gerar backup: {e}', status=500)

# View para backup SQL
@staff_member_required
def backup_sql(request):
    filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    filepath = os.path.join('backup', filename)
    cmd = [
        'pg_dump',
        '-h', 'aws-0-us-east-2.pooler.supabase.com',
        '-U', 'postgres.vxzntgknvejluffgttpg',
        '-d', 'postgres',
        '-F', 'p',
        '-b',
        '-v',
        '-f', filepath
    ]
    env = os.environ.copy()
    env['PGPASSWORD'] = os.environ.get('PGPASSWORD', '')  # Segura: variável de ambiente
    try:
        subprocess.run(cmd, check=True, env=env)
        response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
        return response
    except Exception as e:
        return HttpResponse(f'Erro ao gerar backup: {e}', status=500)

# URLs para as views de backup
backup_urls = [
    path('backup/custom/', backup_custom, name='backup_custom'),
    path('backup/sql/', backup_sql, name='backup_sql'),
]
