# Rotação Segura de API Key WAHA

## Contexto
A API Key `WAHA_API_KEY` é credencial crítica para autenticar envios e acessar o QR code. Deve ser rotacionada regularmente para limitar exposição em caso de vazamento.

## Processo de Rotação (Sem Downtime)

### 1. Preparar Nova Key no Railway WAHA
1. Acessar painel Railway: https://railway.app
2. Selecionar projeto WAHA
3. Ir para "Settings" → "API Keys" (ou ambiente/variáveis)
4. Gerar nova chave (copy de uma existente com escopo adequado ou criar nova)
5. Aguardar Railway confirmar ativação (~5-10 segundos)
6. **Não deletar a chave antiga ainda**

### 2. Atualizar Chave em Staging (Render)
1. Acessar painel Render: https://render.com
2. Selecionar app `gereigreja` (ou similar)
3. Ir para "Environment"
4. Editar variável `WAHA_API_KEY` com valor da **nova chave**
5. Salvar (Rails faz redeploy automático)
6. Aguardar deploy completar (~2-3 min)
7. Testar QR e envio em staging para confirmar

### 3. Validar Funcionalidade em Staging
```bash
# Local de teste, set novo valor e valide:
export WAHA_BASE_URL="https://devlikeaprowaha-production-83c4.up.railway.app"
export WAHA_API_KEY="wak_<nova-chave>"

python manage.py shell
>>> from comunicacao.models import WhatsAppConfiguracao
>>> from comunicacao.services_whatsapp import get_waha_session_status
>>> c = WhatsAppConfiguracao.objects.get(pk=1)
>>> status = get_waha_session_status(c)
>>> print(status)  # Deve retornar um status válido (WORKING, SCAN_QR_CODE, etc)
```

### 4. Deletar Chave Antiga no Railway
1. Acessar Railway painel
2. Ir para API Keys
3. Deletar chave antiga
4. Confirmar

### 5. Documentar Rotação
1. Abrir arquivo `notes/api-key-rotation-log.txt` (ou criar)
2. Registrar:
   - Data/hora da rotação
   - Chave antiga (mascarada): `wak_XXXXXE40K` (últimos 6 caracteres)
   - Chave nova (mascarada): `wak_XXXXX1GZ` (últimos 6 caracteres)
   - Executor: `<nome>`
   - Status: `sucesso` / `falha`

## Automação (Futuro)
Para rotação completamente automática:
1. Criar script Python em `scripts/rotate-waha-api-key.py`
2. Usar API Render para atualizar env var programaticamente
3. Agendar com cron/celery em intervalos (ex: 30 dias)
4. Log automático em banco (tabela `APIKeyRotationLog`)

## Emergência (Chave Comprometida)
1. Gerar nova chave em Railway imediatamente
2. Atualizar Render em < 5 minutos
3. Monitorar logs por acesso não autorizado (HTTP 401 anômalo)
4. Deletar chave comprometida
5. Revisar logs históricos em `/comunicacao/whatsapp/logs/`

## Checklist de Rotação
- [ ] Nova chave gerada em Railway
- [ ] Chave antiga ainda ativa para redund. temporária
- [ ] Render env atualizado
- [ ] Redeploy Render concluído
- [ ] Teste de QR passou
- [ ] Teste de envio passou
- [ ] Chave antiga deletada no Railway
- [ ] Rotação documentada em log
- [ ] Alerta enviado ao time (Slack/email)
