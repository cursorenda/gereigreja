---
name: "gerenciando-backup"
description: "Faz backup e restauração do banco PostgreSQL (Supabase). Use para backup automático, restore de dados ou manutenção do banco."
---

# Quando Usar Esta Skill

Use esta skill quando:
- Fazer backup do banco de dados
- Restaurar dados de um backup
- Configurar backup automático
- Migrar dados entre ambientes
- Recuperar sistema após falha

## Como Fazer Backup

### Backup Manual (Supabase)
```bash
# Via pg_dump
pg_dump -h [HOST] -U [USER] -d [DATABASE] -F c -f backup/backup_$(date +%Y%m%d_%H%M%S).dump

# Via Django
python manage.py dumpdata > backup/backup_$(date +%Y%m%d_%H%M%S).json
```

### Script Automatizado
```python
import subprocess
from datetime import datetime

def fazer_backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'backup/backup_{timestamp}.dump'
    
    command = [
        'pg_dump',
        '-h', settings.DATABASES['default']['HOST'],
        '-U', settings.DATABASES['default']['USER'],
        '-d', settings.DATABASES['default']['NAME'],
        '-F', 'c',
        '-f', filename
    ]
    
    subprocess.run(command, check=True)
    
    # Log do backup
    with open('backup_log.txt', 'a') as f:
        f.write(f'{timestamp} - Backup criado: {filename}\n')
    
    return filename
```

## Como Restaurar

### Restauração Completa
```bash
# Via pg_restore
pg_restore -h [HOST] -U [USER] -d [DATABASE] -c backup/backup_20260205_143000.dump

# Via Django (JSON)
python manage.py loaddata backup/backup_20260205_143000.json
```

### Restauração Seletiva (Tabela Específica)
```bash
# Restaurar apenas uma tabela
pg_restore -h [HOST] -U [USER] -d [DATABASE] -t secretaria_membro backup/backup.dump
```

## Estrutura de Arquivos

```
backup/
├── backup_20260205_143000.dump  # Backup PostgreSQL binário
├── backup_20260204_120000.dump
├── backup_20260203_100000.dump
└── backup_log.txt               # Log de todos os backups
```

## Backup Automático (Cron)

### Linux/Mac
```bash
# Editar crontab
crontab -e

# Adicionar linha (backup diário às 2h)
0 2 * * * cd /caminho/gereigreja && /usr/bin/python manage.py fazer_backup
```

### Windows (Task Scheduler)
```powershell
# PowerShell script
$date = Get-Date -Format "yyyyMMdd_HHmmss"
pg_dump -h HOST -U USER -d DB -F c -f "backup\backup_$date.dump"
```

## Verificar Integridade do Backup

```bash
# Verificar tamanho do arquivo
ls -lh backup/backup_*.dump

# Testar restauração em banco temporário
createdb test_restore
pg_restore -d test_restore backup/backup_20260205_143000.dump
dropdb test_restore
```

## Boas Práticas

1. **Backup antes de deploy crítico** - Sempre!
2. **Testar restauração mensalmente** - Backup não testado é backup inexistente
3. **Manter pelo menos 7 backups históricos**
4. **Armazenar backups fora do servidor** - Cloud storage (S3, Cloudinary)
5. **Backup automático diário às 2h da madrugada**
6. **Logs de backup** - Sempre registrar em `backup_log.txt`
7. **Limpeza de backups antigos** - Manter últimos 30 dias

## Limpeza de Backups Antigos

```bash
# Remover backups com mais de 30 dias
find backup/ -name "backup_*.dump" -mtime +30 -delete
```

## Troubleshooting

### Erro: "Permission denied"
```bash
# Dar permissão ao usuário PostgreSQL
CHMOD 755 backup/
```

### Banco muito grande
```bash
# Usar compressão
pg_dump -h HOST -U USER -d DB -F c -Z 9 -f backup.dump.gz
```
