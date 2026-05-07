# Automacoes Diarias de WhatsApp

Este projeto possui automacao diaria para WhatsApp no app `comunicacao`.

## Producao correta

Como o sistema esta hospedado no Render, o ambiente correto de producao para o agendamento e:
- Render Cron Job

Nao depende de Windows Task Scheduler para producao.

Guia de producao:
- `docs/deploy/RENDER_CRON_WHATSAPP.md`

## O que roda diariamente
- aniversariantes do dia
- lembretes de eventos do dia

## Comando unico recomendado

```bash
python manage.py rodar_automacoes_whatsapp_diarias
```

## Scripts auxiliares

Uso local ou servidor generico:
- Windows: `scripts/automation/run_whatsapp_automations.ps1`
- Linux: `scripts/automation/run_whatsapp_automations.sh`

## Log auxiliar local

- `logs/whatsapp_automations.log`

Em producao no Render, acompanhe preferencialmente:
- logs do proprio Cron Job no painel do Render
- registros no banco em `WhatsAppMensagemLog`

## Opcional: Windows Task Scheduler

Esta opcao fica apenas para uso local ou servidor Windows proprio:
- `deploy/windows/register_whatsapp_automations_task.ps1`

## Opcional: cron Linux tradicional

Exemplo:
```bash
0 8 * * * /bin/bash /c/Gereigreja/scripts/automation/run_whatsapp_automations.sh
```

## Observacoes
- Cada congregacao precisa ter configuracao ativa em Comunicacao > Configurar WhatsApp.
- As automacoes respeitam as flags da configuracao por congregacao.
- O webhook WAHA continua independente do agendamento.
