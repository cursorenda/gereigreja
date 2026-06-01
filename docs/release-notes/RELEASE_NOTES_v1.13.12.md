# Release Notes - Versao 1.13.12

Data de lancamento: 01/06/2026
Tipo: PATCH (melhorias operacionais e governanca EBD)

## Resumo Executivo
Esta versao fortalece o modulo Escola Dominical em dois pontos centrais:
- governanca de configuracao por igreja (church-first com fallback);
- seguranca operacional da chamada para evitar erros de periodo e data.

## O que mudou

### 1) Configuracao EBD local por igreja
- Novos campos na igreja para configurar:
  - tipo de periodo EBD,
  - dia da semana da EBD,
  - horario da EBD.
- Formularios e tela de configuracao da igreja atualizados para edicao desses campos.
- Regras church-first aplicadas no backend, com fallback para `ConfiguracaoSistema` quando necessario.

Beneficio:
- cada igreja pode operar EBD com autonomia local sem perder padrao global.

### 2) Chamada com selecao segura de aula
- Seleciona corretamente o periodo vigente para a turma.
- Seletor da chamada exibe apenas aulas com licao valida no periodo.
- Bloqueia registro de chamada quando nao ha licao valida no periodo.
- Interface indica status da aula selecionada:
  - [HOJE]
  - [PASSADA]
  - [FUTURA]
- Banner superior destaca confirmacao quando a aula de HOJE esta selecionada.

Beneficio:
- reduz erros de lancamento em aula de trimestre anterior e melhora confianca da equipe.

### 3) Operacao e visibilidade
- Dashboard EBD e lista de turmas passaram a indicar origem da configuracao (local/herdada).
- Tela de configuracao da igreja ganhou mini-paineis de classes/turmas com atalhos de acao.
- Sincronizacao EBD-Agenda ajustada para usar horario local da igreja quando houver override.

Beneficio:
- visao operacional mais clara e fluxo mais rapido para secretaria/superintendencia.

## Migracoes desta release
- `configuracao/migrations/0027_igreja_ebd_config_local.py`
- `escola_biblica/migrations/0026_licao_evento_agenda.py`
- `eventos/migrations/0013_evento_tipo_escola_dominical.py`
- `eventos/migrations/0014_evento_status_cancelamento.py`

## Impacto esperado
- menor incidencia de erro humano na chamada de presenca;
- maior consistencia de configuracao em ambiente multi-igreja;
- melhor alinhamento entre EBD e agenda operacional.

## Checklist operacional
- [ ] Executar deploy em producao
- [ ] Executar migracoes pendentes
- [ ] Validar fluxo de chamada em turma com licao no periodo vigente
- [ ] Validar turma sem licao cadastrada (deve bloquear chamada)
- [ ] Validar rotinas EBD/agenda apos deploy

## Arquivos-chave desta release
- `configuracao/models.py`
- `configuracao/forms.py`
- `configuracao/views.py`
- `configuracao/signals.py`
- `configuracao/templates/configuracao/igrejas/editar_igreja_config.html`
- `escola_biblica/models.py`
- `escola_biblica/views.py`
- `escola_biblica/services_agenda.py`
- `escola_biblica/templates/escola_biblica/chamada_presenca.html`
- `escola_biblica/templates/escola_biblica/dashboard.html`
- `escola_biblica/templates/escola_biblica/turma_list.html`
- `docs/sistema/ESCOLA_DOMINICAL_CONFIG_LOCAL_IGREJA.md`
- `docs/sistema/ESCOLA_DOMINICAL_HOMOLOGACAO_CONFIG_LOCAL_IGREJA.md`
- `docs/sistema/ESCOLA_DOMINICAL_ROADMAP_PREMIUM.md`

---
Equipe Gereigreja
