# Checklist de Deploy - Comunicação WAHA

## Pré-Deploy (Local)
- [ ] `manage.py check comunicacao` passa sem erros
- [ ] `manage.py test comunicacao.tests --settings=core.settings_test -v 1` todos os testes passam
- [ ] Migrar banco local: `manage.py migrate comunicacao`
- [ ] Validar logs recentes de envio: sem erros de tipo `No LID for users`

## Configuração de Ambiente (Render)
- [ ] Variáveis de ambiente salvas no Render:
  - `WAHA_BASE_URL`: URL Railway WAHA (ex: `https://devlikeaprowaha-production-83c4.up.railway.app`)
  - `WAHA_API_KEY`: Chave válida e ativa no Railway WAHA
- [ ] Render deploy conclui sem erro de build/start
- [ ] Healthcheck retorna 200 OK

## Testes em Staging
- [ ] Acessar `/comunicacao/whatsapp/configuracao/` e clicar "Gerar / Atualizar QR Code"
  - [ ] QR aparece dentro de 10 segundos
  - [ ] Status exibe "Aguardando scan" (warning badge)
- [ ] Enviar WhatsApp em massa para 1 contato de teste
  - [ ] Sucesso retorna "WAHA aceitou o envio para 1 pessoa(s)"
  - [ ] Log em `/comunicacao/whatsapp/logs/` marca como sucesso
- [ ] Testar com contato sem WhatsApp (número inválido)
  - [ ] Erro retorna mensagem amigável sem stack trace
  - [ ] Log marca como erro com detalhe descritivo

## Validação de Segurança
- [ ] API Key do WAHA não aparece em logs/traces (logs truncam após X caracteres)
- [ ] Endpoint `/comunicacao/whatsapp/qr/<pk>/` requer login
- [ ] Webhook `/comunicacao/whatsapp/webhook/` valida webhook_token

## Pós-Deploy
- [ ] Monitorar logs do Render por erros WAHA 500+
- [ ] Verificar métricas de sucesso/falha em `/comunicacao/whatsapp/logs/`
- [ ] Confirmar automações (aniversariantes) rodam no horário configurado

## Rollback (se necessário)
- [ ] Revert do commit Django
- [ ] Render redeploy automático (~2 min)
- [ ] Validar status do QR novamente

## Contatos Críticos
- Railway WAHA: https://railway.app (painel)
- Render App: https://render.com (painel)
