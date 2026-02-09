README - Scripts Úteis

# Scripts do Sistema Gereigreja

Esta pasta contém scripts auxiliares organizados por skill.

## 📁 Estrutura

```
skills/
├── backup/scripts/
│   ├── backup.sh          # Bash: Backup automático
│   ├── backup.py          # Python: Backup com mais controle
│   └── restore.py         # Python: Restaurar backup
│
├── deploy/scripts/
│   ├── deploy.sh          # Bash: Deploy completo
│   ├── deploy.py          # Python: Deploy automatizado
│   └── generate_release_notes.py  # Gerar release notes
│
├── configuracao/scripts/
│   └── health_check.py    # Verificar saúde do sistema
│
├── secretaria/scripts/
│   ├── relatorio_membros.py    # Estatísticas de membros
│   └── aniversariantes.py      # Lista de aniversariantes
│
├── eventos/scripts/
│   └── listar_inscritos.py     # Lista inscritos em eventos
│
└── financeiro/scripts/
    └── relatorio_financeiro.py  # Relatório mensal de finanças
```

## 🚀 Como Usar

### Backup

**Criar backup (Python - Recomendado):**
```bash
cd skills/backup/scripts
python backup.py
```

**Criar backup (Bash):**
```bash
cd skills/backup/scripts
./backup.sh
```

**Restaurar backup:**
```bash
cd skills/backup/scripts
python restore.py backup_20260205_143000.dump
```

### Deploy

**Deploy completo com versionamento (Python):**
```bash
python skills/deploy/scripts/deploy.py 1.0.10
```

**Deploy sem versão:**
```bash
python skills/deploy/scripts/deploy.py
```

**Gerar release notes:**
```bash
python skills/deploy/scripts/generate_release_notes.py v1.0.9
```

### Health Check

**Verificar saúde do sistema:**
```bash
python skills/configuracao/scripts/health_check.py
```

Verifica:
- ✅ Conexão com banco
- ✅ Uso de memória/disco
- ✅ Backups recentes
- ✅ Logs de erro

### Secretaria

**Relatório de membros (terminal):**
```bash
python skills/secretaria/scripts/relatorio_membros.py
```

**Relatório em CSV:**
```bash
python skills/secretaria/scripts/relatorio_membros.py csv
```

**Relatório em JSON:**
```bash
python skills/secretaria/scripts/relatorio_membros.py json
```

**Aniversariantes do mês:**
```bash
python skills/secretaria/scripts/aniversariantes.py
```

**Aniversariantes de mês específico:**
```bash
python skills/secretaria/scripts/aniversariantes.py --mes 3
```

**Com mensagem para WhatsApp:**
```bash
python skills/secretaria/scripts/aniversariantes.py --mes 3 --whatsapp
```

### Eventos

**Listar eventos disponíveis:**
```bash
python skills/eventos/scripts/listar_inscritos.py --lista
```

**Ver inscritos de um evento:**
```bash
python skills/eventos/scripts/listar_inscritos.py 15
```

**Exportar lista para CSV:**
```bash
python skills/eventos/scripts/listar_inscritos.py 15 --exportar csv
```

### Financeiro

**Relatório do mês atual:**
```bash
python skills/financeiro/scripts/relatorio_financeiro.py
```

**Relatório de mês/ano específico:**
```bash
python skills/financeiro/scripts/relatorio_financeiro.py --mes 1 --ano 2026
```

## ⚙️ Configuração

### Variáveis de Ambiente

Todos os scripts leem do arquivo `.env` na raiz:

```env
# Banco de dados
SUPABASE_DB_HOST=seu-host.supabase.co
SUPABASE_DB_USER=postgres
SUPABASE_DB_NAME=postgres
SUPABASE_DB_PASSWORD=sua-senha

# Django
DJANGO_SECRET_KEY=sua-chave
DJANGO_DEBUG=False
```

### Dependências

**Python:**
```bash
pip install python-dotenv psutil
```

**Sistema (Windows):**
```bash
# PostgreSQL tools (pg_dump, pg_restore)
choco install postgresql
```

## 🔄 Automação

### Backup Automático (Windows Task Scheduler)

1. Abrir Task Scheduler
2. Criar tarefa básica
3. Trigger: Diariamente às 2h
4. Action: Executar programa
   - Program: `python`
   - Arguments: `C:\Gereigreja\skills\backup\scripts\backup.py`
   - Start in: `C:\Gereigreja`

### Backup Automático (Linux Cron)

```bash
# Editar crontab
crontab -e

# Adicionar linha (backup diário às 2h)
0 2 * * * cd /caminho/gereigreja && python skills/backup/scripts/backup.py
```

## 📊 Logs

- Backup: `backup/backup_log.txt`
- Django: `logs/django_errors.log`
- Health Check: Output direto no terminal

## 🆘 Troubleshooting

### Erro: "pg_dump not found"
```bash
# Windows
choco install postgresql

# Linux
sudo apt install postgresql-client
```

### Erro: "Permission denied"
```bash
# Dar permissão aos scripts bash
chmod +x skills/backup/scripts/backup.sh
chmod +x skills/deploy/scripts/deploy.sh
```

### Erro: "ModuleNotFoundError: dotenv"
```bash
pip install python-dotenv
```
