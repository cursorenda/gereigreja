from django.contrib import admin
from django.urls import path
from django.http import HttpResponse, FileResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from django.core.management import call_command

import subprocess
import os
import datetime
import io
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# View para backup JSON (funciona em qualquer ambiente)
@staff_member_required
def backup_json(request):
    """Backup usando Django dumpdata - funciona no servidor sem pg_dump"""
    try:
        filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join('backup', filename)
        
        # Criar diretório se não existir
        os.makedirs('backup', exist_ok=True)
        
        # Usar dumpdata para criar backup
        with open(filepath, 'w', encoding='utf-8') as f:
            call_command('dumpdata', '--indent', '2', '--natural-foreign', '--natural-primary', stdout=f)
        
        # Retornar arquivo para download
        response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
        return response
    except Exception as e:
        return HttpResponse(f'Erro ao gerar backup JSON: {e}', status=500)

# View para backup SQL (apenas para ambiente local com pg_dump)
# View para backup SQL (apenas para ambiente local com pg_dump)
@staff_member_required
def backup_custom(request):
    """Backup usando pg_dump - apenas funciona localmente ou com pg_dump instalado"""
    try:
        # Verificar se pg_dump está disponível (Windows usa 'where', Linux/Mac usa 'which')
        import platform
        check_command = 'where' if platform.system() == 'Windows' else 'which'
        
        try:
            check_cmd = subprocess.run([check_command, 'pg_dump'], capture_output=True, text=True)
            if check_cmd.returncode != 0:
                raise FileNotFoundError("pg_dump não encontrado")
        except FileNotFoundError:
            # pg_dump não disponível
            return HttpResponse(
                '<h2>❌ pg_dump não está disponível</h2>'
                '<p>O comando pg_dump não foi encontrado no sistema.</p>'
                '<p><strong>Solução:</strong> Use o <a href="/backup/json/">💾 Backup JSON</a> que funciona em qualquer ambiente.</p>'
                '<br><p><small>Para usar pg_dump, instale o PostgreSQL client tools.</small></p>',
                status=400
            )
        
        filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.dump"
        filepath = os.path.join('backup', filename)
        
        # Criar diretório se não existir
        os.makedirs('backup', exist_ok=True)
        
        cmd = [
            'pg_dump',
            '-h', os.environ.get('DB_HOST', 'aws-0-us-east-2.pooler.supabase.com'),
            '-U', os.environ.get('DB_USER', 'postgres.vxzntgknvejluffgttpg'),
            '-d', os.environ.get('DB_NAME', 'postgres'),
            '-F', 'c',
            '-b',
            '-v',
            '-f', filepath
        ]
        env = os.environ.copy()
        env['PGPASSWORD'] = os.environ.get('PGPASSWORD', '')
        
        subprocess.run(cmd, check=True, env=env)
        response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
        return response
    except Exception as e:
        return HttpResponse(f'Erro ao gerar backup: {e}<br><br>Use <a href="/backup/json/">Backup JSON</a> que funciona em qualquer ambiente.', status=500)

# View para backup SQL
@staff_member_required
def backup_sql(request):
    """Backup SQL usando pg_dump - apenas funciona localmente"""
    try:
        # Verificar se pg_dump está disponível (Windows usa 'where', Linux/Mac usa 'which')
        import platform
        check_command = 'where' if platform.system() == 'Windows' else 'which'
        
        try:
            check_cmd = subprocess.run([check_command, 'pg_dump'], capture_output=True, text=True)
            if check_cmd.returncode != 0:
                raise FileNotFoundError("pg_dump não encontrado")
        except FileNotFoundError:
            return HttpResponse(
                '<h2>❌ pg_dump não está disponível</h2>'
                '<p>O comando pg_dump não foi encontrado no sistema.</p>'
                '<p><strong>Solução:</strong> Use o <a href="/backup/json/">💾 Backup JSON</a> que funciona em qualquer ambiente.</p>'
                '<br><p><small>Para usar pg_dump, instale o PostgreSQL client tools.</small></p>',
                status=400
            )
        
        filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        filepath = os.path.join('backup', filename)
        
        # Criar diretório se não existir
        os.makedirs('backup', exist_ok=True)
        
        cmd = [
            'pg_dump',
            '-h', os.environ.get('DB_HOST', 'aws-0-us-east-2.pooler.supabase.com'),
            '-U', os.environ.get('DB_USER', 'postgres.vxzntgknvejluffgttpg'),
            '-d', os.environ.get('DB_NAME', 'postgres'),
            '-F', 'p',
            '-b',
            '-v',
            '-f', filepath
        ]
        env = os.environ.copy()
        env['PGPASSWORD'] = os.environ.get('PGPASSWORD', '')
        
        subprocess.run(cmd, check=True, env=env)
        response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
        return response
    except Exception as e:
        return HttpResponse(f'Erro ao gerar backup: {e}<br><br>Use <a href="/backup/json/">Backup JSON</a> que funciona em qualquer ambiente.', status=500)

# View para backup de arquivos (media)
@staff_member_required
def backup_arquivos(request):
    """Backup de todos os arquivos da pasta media (uploads, fotos, documentos)"""
    try:
        import zipfile
        from django.conf import settings
        
        filename = f"backup_arquivos_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        filepath = os.path.join('backup', filename)
        
        # Criar diretório se não existir
        os.makedirs('backup', exist_ok=True)
        
        # Verificar se existe pasta media
        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            return HttpResponse('Pasta media não encontrada. Não há arquivos para fazer backup.', status=404)
        
        # Criar arquivo ZIP com todos os arquivos da pasta media
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(media_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(media_root))
                    zipf.write(file_path, arcname)
        
        # Verificar se o arquivo foi criado
        if not os.path.exists(filepath):
            return HttpResponse('Erro ao criar arquivo de backup.', status=500)
        
        # Retornar arquivo para download
        response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
        return response
        
    except Exception as e:
        return HttpResponse(f'Erro ao gerar backup de arquivos: {e}', status=500)

# URLs para as views de backup
backup_urls = [
    path('backup/json/', backup_json, name='backup_json'),
    path('backup/arquivos/', backup_arquivos, name='backup_arquivos'),
    path('backup/custom/', backup_custom, name='backup_custom'),
    path('backup/sql/', backup_sql, name='backup_sql'),
]
