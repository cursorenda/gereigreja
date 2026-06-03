# EBD Runbook Fase 1

## Objetivo
Guia rápido para diagnosticar e mitigar incidentes no módulo Escola Dominical.

## Escopo crítico
- Dashboard EBD
- Chamada de presença
- Relatório diário da EBD

## Sinais de incidente
- Aumento de erro 5xx nos endpoints EBD
- Latência elevada no dashboard/chamada
- Queda brusca de cache hit do dashboard
- Falhas recorrentes ao salvar chamada ou oferta

## Alertas operacionais (limiares sugeridos)
1. Erro HTTP 5xx
- Condição: taxa de 5xx > 1% por 5 minutos em endpoints EBD.
- Ação: abrir incidente, coletar logs `ebd.endpoint.error` e `ebd.endpoint.metric`.

2. Latência do dashboard
- Condição: p95 > 800 ms por 10 minutos no endpoint de dashboard EBD.
- Ação: validar cache hit/miss, volume do período e consultas recentes.

3. Cache hit ratio do dashboard
- Condição: hit ratio < 60% por 15 minutos.
- Ação: revisar chaves de cache, invalidação por sinais e padrões de filtro.

4. Erro de gravação de chamada
- Condição: mais de 5 ocorrências em 10 minutos dos logs `ebd.chamada.save_error` ou `ebd.chamada.oferta_error`.
- Ação: validar payload, integridade de dados e regras de período/dia.

## Diagnóstico rápido
1. Verificar logs de endpoint:
- `ebd.endpoint.metric`
- `ebd.endpoint.error`

2. Verificar logs de cache dashboard:
- `ebd.dashboard.cache result=hit`
- `ebd.dashboard.cache result=miss`

3. Verificar logs de auditoria funcional:
- `ebd.audit action=chamada_registrada`
- `ebd.audit action=chamada_oferta_registrada`
- `ebd.audit action=transferencia_aluno`
- `ebd.audit action=oferta_create|oferta_edit|oferta_delete`

4. Verificar falhas de persistência:
- `ebd.chamada.save_error`
- `ebd.chamada.oferta_error`

## Mitigação imediata
1. Latência alta no dashboard:
- Validar taxa de cache hit/miss.
- Verificar consultas recentes e volume de dados do período selecionado.

2. Falha na chamada:
- Verificar se há lição válida no período e data selecionada.
- Verificar logs de validação/salvamento por aluno.

3. Falha em oferta:
- Revisar payload de valor e regras de escopo da turma/classe.

## Rollback operacional
1. Se incidente ligado a release recente:
- Reverter para commit estável anterior (branch `master`) e revalidar:
  - `manage.py check`
  - testes EBD focados

2. Se incidente de dados:
- Validar integridade de `Frequencia.pontos_total`.
- Reaplicar migration de backfill se necessário em janela controlada.

## Checklist pós-incidente
- Registrar causa raiz
- Registrar impacto e duração
- Documentar ação corretiva e prevenção
- Atualizar este runbook quando necessário

## Checklist de fumaça pós-implantação (homologação/produção)
1. Dashboard EBD abre com status 200 e conteúdo completo.
2. Recarregar dashboard duas vezes e confirmar logs de cache hit/miss.
3. Abrir chamada de turma com lição válida e salvar pelo menos 1 presença.
4. Confirmar log `ebd.audit action=chamada_registrada`.
5. Editar oferta da classe e confirmar log `ebd.audit action=oferta_edit`.
6. Executar transferência de aluno em homologação e confirmar log `ebd.audit action=transferencia_aluno`.
7. Rodar `manage.py check` e suíte EBD focada.
