# Agendamento de WhatsApp no Render

## Decisao correta para producao

Como o sistema esta hospedado no Render, o agendamento de producao nao deve depender do Windows Task Scheduler.
O modelo correto e usar um Render Cron Job apontando para o mesmo repositorio e banco do sistema.

## O que deve rodar
Rotina diaria unica:
```bash
python manage.py rodar_automacoes_whatsapp_diarias
```

Essa rotina executa:
- aniversariantes do dia
- lembretes de eventos do dia

## Como configurar no Render

1. Acesse o dashboard do Render.
2. Clique em `New +`.
3. Escolha `Cron Job`.
4. Conecte o mesmo repositorio do Gereigreja.
5. Configure:
   - Name: `gereigreja-whatsapp-diario`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python manage.py rodar_automacoes_whatsapp_diarias`
   - Schedule: `0 8 * * *`
6. Copie as mesmas variaveis de ambiente usadas pelo Web Service:
   - `DATABASE_URL`
   - variaveis de e-mail
   - variaveis do projeto Django
   - variaveis do WAHA, se aplicavel
7. Salve e execute um run manual para validar.

## Observacoes importantes
- O Cron Job do Render e independente do Web Service.
- Ele precisa ter acesso ao mesmo banco e as mesmas configuracoes do projeto.
- O filesystem no Render nao deve ser usado como armazenamento permanente de auditoria; a auditoria precisa ficar no banco. Neste caso, os logs principais de envio ja estao no banco em `WhatsAppMensagemLog`.
- O arquivo `logs/whatsapp_automations.log` pode ser util localmente, mas em producao o principal e acompanhar os logs do proprio Render e os registros em banco.

## Horario sugerido
- `0 8 * * *`: bom para aniversariantes e lembretes matinais.

## Se quiser granularidade maior no futuro
Voce pode separar em 2 Cron Jobs:
- `07:00` para aniversariantes
- `08:00`, `12:00` ou `17:00` para lembretes de eventos

## Validacao manual
Rode localmente ou no shell do Render:
```bash
python manage.py rodar_automacoes_whatsapp_diarias
```

## Conclusao
Para producao no Render, a configuracao recomendada e `Render Cron Job`, nao `Windows Task Scheduler`.
