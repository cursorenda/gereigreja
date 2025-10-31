"""
Script de limpeza conservadora para `secretaria/views.py`.
- Cria um backup em `secretaria/views.py.bak_YYYYMMDD_HHMMSS`.
- Remove import lines duplicadas que estão no nível top-level (sem indentação).
  Isso preserva imports dentro de funções (mantém lazy imports).
- Não tenta remover funções duplicadas para evitar apagar lógica por engano.

Use: python tools/clean_views_imports.py
"""
from __future__ import annotations
import os
import sys
import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TARGET = os.path.join(ROOT, 'secretaria', 'views.py')

if not os.path.exists(TARGET):
    print(f'Arquivo alvo não encontrado: {TARGET}', file=sys.stderr)
    sys.exit(2)

with open(TARGET, 'r', encoding='utf-8') as f:
    original = f.read()
    lines = original.splitlines(keepends=True)

seen = set()
out_lines = []
removed_count = 0
removed_examples = []

for ln in lines:
    # consider only top-level import statements
    if ln and (ln[0] != ' ' and ln[0] != '\t'):
        s = ln.strip()
        if s.startswith('from ') or s.startswith('import '):
            # use exact stripped line as key
            key = s
            if key in seen:
                removed_count += 1
                if len(removed_examples) < 50:
                    removed_examples.append(key)
                # skip this duplicate import
                continue
            seen.add(key)
    out_lines.append(ln)

# backup
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
backup_path = TARGET + f'.bak_{ts}'
with open(backup_path, 'w', encoding='utf-8') as bf:
    bf.write(original)

# write cleaned file
with open(TARGET, 'w', encoding='utf-8') as wf:
    wf.write(''.join(out_lines))

print('Backup criado em:', backup_path)
print('Imports removidos (top-level, duplicados):', removed_count)
if removed_examples:
    print('\nExemplos removidos:')
    for ex in removed_examples:
        print('  ', ex)

print('\nArquivo atualizado:', TARGET)
print('Se algo parecer errado, restaure o backup com:')
print('  copy "{0}" "{1}"'.format(backup_path, TARGET))
