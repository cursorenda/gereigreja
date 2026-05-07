#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON_EXE="$PROJECT_ROOT/.venv/Scripts/python.exe"

if [ ! -x "$PYTHON_EXE" ]; then
  PYTHON_EXE="$PROJECT_ROOT/.venv/bin/python"
fi

LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/whatsapp_automations.log"
mkdir -p "$LOG_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Inicio da automacao diaria de WhatsApp" >> "$LOG_FILE"
cd "$PROJECT_ROOT"
PYTHONWARNINGS=ignore "$PYTHON_EXE" -W ignore manage.py enviar_whatsapp_automatico --tipo aniversariantes >> "$LOG_FILE" 2>&1
PYTHONWARNINGS=ignore "$PYTHON_EXE" -W ignore manage.py enviar_whatsapp_automatico --tipo lembrete_eventos >> "$LOG_FILE" 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Automacao diaria finalizada com sucesso" >> "$LOG_FILE"
