#!/usr/bin/env python
import os
import sys
sys.path.insert(0, '.')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.core.files.storage import default_storage
import zipfile
import datetime

def _adicionar_storage_ao_zip(zipf, storage, path=''):
    total_arquivos = 0
    try:
        diretorios, arquivos = storage.listdir(path)
        for nome_arquivo in arquivos:
            storage_path = f'{path}/{nome_arquivo}' if path else nome_arquivo
            with storage.open(storage_path, 'rb') as arquivo_origem:
                zipf.writestr(storage_path, arquivo_origem.read())
            total_arquivos += 1
        for nome_diretorio in diretorios:
            diretorio_path = f'{path}/{nome_diretorio}' if path else nome_diretorio
            total_arquivos += _adicionar_storage_ao_zip(zipf, storage, diretorio_path)
    except Exception as e:
        print(f'Erro: {e}')
    return total_arquivos

filename = f'backup_test_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
filepath = os.path.join('backup', filename)
os.makedirs('backup', exist_ok=True)

try:
    with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        total = _adicionar_storage_ao_zip(zipf, default_storage)
    print(f'✓ ZIP criado: {filepath} ({os.path.getsize(filepath)} bytes, {total} arquivos)')
except Exception as e:
    print(f'✗ Erro: {e}')
