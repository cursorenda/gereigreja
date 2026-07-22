# Plano de Automacoes - Comunicacao

## Objetivo
Evoluir o app Comunicacao para uma esteira de relacionamento com membros e visitantes,
com foco em experiencia pastoral e aumento de participacao.

## Fase 1 (implementada)
- Boas-vindas automaticas no WhatsApp para novos membros.
- Rotina diaria incluindo:
  - aniversariantes
  - novos membros
  - lembrete de eventos

### Como executar manualmente
```powershell
python manage.py enviar_whatsapp_automatico --tipo novos_membros --dias-novos 7
python manage.py rodar_automacoes_whatsapp_diarias
```

### Regras da Fase 1
- Usa configuracao por congregacao (`WhatsAppConfiguracao`) com `auto_novos_membros=True`.
- Evita duplicidade: nao reenvia boas-vindas para membro que ja recebeu log de sucesso `tipo=novo_membro`.
- Usa janela configuravel por parametro (`--dias-novos`).

## Fase 2 (proxima)
- Follow-up de visitante:
  - D+1 apos primeira visita.
  - Mensagem de acolhimento e convite para retorno.
- Lembrete de evento melhorado:
  - D-1 e D-0 por horario.
  - Evitar envio duplicado por evento/pessoa.

## Fase 3
- Trilha de integracao 30/60/90 dias:
  - D+30: convite para integracao e grupos.
  - D+60: incentivo a participacao em ministerio.
  - D+90: acompanhamento pastoral estruturado.

## Fase 4
- Reengajamento de membros sem participacao recente.
- Segmentacao por perfil (idade, tipo de pessoa, igreja, status).
- Dashboard de resultado por campanha automatica.

## Boas praticas operacionais
- Agendar rotina diaria no servidor em horario fora de pico.
- Monitorar `comunicacao/whatsapp/logs/` diariamente.
- Revisar templates mensalmente com equipe pastoral.
- Manter celular e e-mail atualizados no cadastro.

## Indicadores sugeridos
- Taxa de entrega por tipo (`aniversario`, `novo_membro`, `evento`).
- Taxa de falha por congregacao.
- Tempo medio entre cadastro e 1a mensagem.
- Quantidade de novos membros contatados em ate 24h.
