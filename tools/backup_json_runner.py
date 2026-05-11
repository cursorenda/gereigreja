#!/usr/bin/env python
"""
Wrapper para executar dumpdata com limite de recursão aumentado.
Evita "maximum recursion depth exceeded" em modelos com ciclos de FK.
"""
import sys
import os

# Configurar paths antes de imports Django
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Aumentar limite de recursão significativamente antes de imports Django
# Ciclos de FK com modelos complexos precisam muito mais espaço
sys.setrecursionlimit(50000)

import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

if __name__ == '__main__':
    output_path = sys.argv[1] if len(sys.argv) > 1 else 'backup/validacao_backup.json'
    
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        call_command(
            'dumpdata',
            '--exclude=contenttypes',
            '--exclude=auth.permission',
            '--exclude=sessions.session',
            '--exclude=admin.logentry',
            '--indent=2',
            output=output_path,
        )
        print(f"✓ Backup JSON criado com sucesso em {output_path}")
    except Exception as e:
        print(f"✗ Erro ao criar backup: {str(e)}", file=sys.stderr)
        sys.exit(1)
