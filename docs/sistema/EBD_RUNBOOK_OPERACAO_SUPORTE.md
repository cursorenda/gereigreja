# EBD Runbook Completo de Operacao e Suporte

## Objetivo

Padronizar resposta a incidentes, recuperacao de servico e governanca operacional do modulo de Escola Biblica (EBD).

Escopo deste runbook:
- On-call e escalonamento
- Triage e diagnostico rapido
- Mitigacao e rollback
- Recuperacao de dados operacionais
- Checklist de encerramento e pos-incidente

## SLOs e Limiares

### SLOs operacionais
- Disponibilidade dos endpoints criticos EBD: >= 99.5%
- Latencia p95 dashboard/chamada: < 800 ms
- Taxa de erro 5xx endpoints EBD: < 1%

### Alertas recomendados
- Critico: 5xx > 3% por 5 min em endpoints EBD
- Alto: p95 > 1200 ms por 10 min
- Medio: cache hit ratio dashboard < 40% por 30 min
- Medio: aumento anormal de eventos `chamada_concorrente_ignorada`

## Responsabilidades de On-Call

### Niveis
- L1 (Atendimento): Secretaria tecnica / suporte operacional
- L2 (Aplicacao): Dev responsavel modulo EBD
- L3 (Infra/Dados): Responsavel plataforma e banco

### Janela alvo
- Ack inicial: ate 10 min
- Mitigacao inicial: ate 30 min
- Plano de correcao: ate 2 h

## Playbook de Triage

### 1. Confirmar escopo
- Identificar endpoint afetado (dashboard, chamada, relatorios)
- Verificar igreja/turma/data impactadas
- Confirmar se e erro geral ou localizado por permissao/escopo

### 2. Coletar sinais
- Logs `ebd.endpoint.metric` e `ebd.endpoint.error`
- Logs de auditoria `ebd.audit`
- Indicadores de cache hit/miss do dashboard
- Ultimos deploys e commits

### 3. Classificar severidade
- SEV1: indisponibilidade geral ou perda de dados em chamada
- SEV2: degradacao relevante de latencia/erro parcial
- SEV3: erro localizado com workaround

## Mitigacao Rapida

### Incidente: erro em chamada de presenca
- Acao 1: validar permissao/escopo (igreja ativa, turma acessivel)
- Acao 2: confirmar idempotencia/concorrencia (eventos de duplicidade)
- Acao 3: reprocessar apenas turma/data afetadas apos estabilizacao

### Incidente: dashboard lento
- Acao 1: confirmar saturacao de consultas e hit ratio de cache
- Acao 2: invalidar cache apenas se houver dado inconsistente
- Acao 3: priorizar acesso de operacao (professor/secretaria)

### Incidente: erro em massa apos release
- Acao 1: acionar rollback da release
- Acao 2: manter modo conservador para operacao critica
- Acao 3: abrir incidente SEV1 com freeze de novas mudancas

## Rollback

### Quando acionar rollback
- Aumento sustentado de 5xx acima do limiar critico
- Regressao funcional em chamada impedindo registro
- Inconsistencia de dados sem mitigacao segura imediata

### Passos
1. Identificar a ultima versao estavel
2. Executar rollback do deploy
3. Revalidar smoke EBD minimo
4. Comunicar status parcial e ETA

### Smoke minimo apos rollback
- Abrir dashboard EBD (status 200)
- Abrir chamada de turma com licao vigente
- Registrar chamada simples (1 aluno)
- Confirmar pontos_total salvo

## Recuperacao de Dados

### Cenarios cobertos
- Chamada salva parcialmente
- Oferta nao persistida
- Duplicidade operacional de submissao

### Procedimento base
1. Levantar turma, data e usuario afetados (logs audit)
2. Consolidar estado atual em frequencia/oferta
3. Corrigir somente registros do intervalo afetado
4. Validar totais e ranking apos correcao
5. Registrar acao corretiva no incidente

## Comunicacao do Incidente

### Atualizacao curta (template)
- Impacto: modulo/endpoint afetado
- Escopo: quem foi impactado
- Acao atual: mitigacao em andamento
- Proximo update: horario estimado

### Encerramento (template)
- Causa raiz
- Medida de contencao
- Correcao definitiva
- Acao preventiva e owner

## Pos-Incidente (PIR)

Checklist obrigatorio:
- Linha do tempo do incidente
- Causa tecnica validada
- Gap de monitoramento identificado
- Teste de regressao adicionado (quando aplicavel)
- Atualizacao deste runbook (quando aplicavel)

## Comandos uteis

### Validacao local focada EBD
```bash
python manage.py check
python manage.py test escola_biblica.tests.test_pontos_ebd escola_biblica.tests.test_chamada_fluxo --settings=core.settings_test -v 2
```

### Verificacao git antes de rollback/patch
```bash
git status -sb
git log --oneline -n 15
```

## Referencias
- docs/sistema/EBD_RUNBOOK_FASE1.md
- notes/melhorias_no_gereigreja.md
- escola_biblica/views.py
- escola_biblica/tests/test_chamada_fluxo.py
