#!/bin/bash
# Script de backup automático do banco PostgreSQL (Supabase)
# Uso: ./backup.sh

# Configurações (ler de .env)
source ../.env 2>/dev/null || true

# Variáveis
BACKUP_DIR="../../backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILENAME="backup_${TIMESTAMP}.dump"
FILEPATH="${BACKUP_DIR}/${FILENAME}"

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🔄 Iniciando backup do banco de dados..."
echo "📁 Destino: ${FILEPATH}"

# Criar diretório se não existir
mkdir -p "${BACKUP_DIR}"

# Executar backup
pg_dump -h "${SUPABASE_DB_HOST}" \
        -U "${SUPABASE_DB_USER}" \
        -d "${SUPABASE_DB_NAME}" \
        -F c \
        -f "${FILEPATH}"

# Verificar se foi bem-sucedido
if [ $? -eq 0 ]; then
    # Registrar no log
    echo "${TIMESTAMP} - Backup criado: ${FILENAME}" >> "${BACKUP_DIR}/backup_log.txt"
    
    echo -e "${GREEN}✅ Backup concluído com sucesso!${NC}"
    echo "📦 Arquivo: ${FILENAME}"
    echo "📊 Tamanho: $(du -h ${FILEPATH} | cut -f1)"
    
    # Limpar backups antigos (manter últimos 30 dias)
    find "${BACKUP_DIR}" -name "backup_*.dump" -mtime +30 -delete
    echo "🧹 Backups antigos removidos (>30 dias)"
else
    echo -e "${RED}❌ Erro ao criar backup!${NC}"
    exit 1
fi
