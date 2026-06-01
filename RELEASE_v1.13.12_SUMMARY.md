# RELEASE v1.13.12 - RESUMO EXECUTIVO

Data: 01/06/2026
Tipo: PATCH
Escopo: Escola Dominical (EBD)

## Resumo
A versao v1.13.12 consolida a configuracao EBD por igreja (church-first com fallback ministerial) e melhora o fluxo operacional da chamada de presenca para evitar erros de periodo/data. O foco da release foi reduzir risco de lancamento incorreto e tornar a experiencia de uso mais clara para operacao semanal.

## Principais Entregas
- Configuracao local EBD por igreja com novos campos para periodo, dia da semana e horario.
- Fallback seguro para configuracao ministerial quando a igreja nao define override local.
- Mini-paineis e atalhos EBD nas configuracoes da igreja (classes, turmas e status operacional da chamada).
- Dashboard e lista de turmas com indicacao da origem da configuracao (local x herdada).
- Chamada por turma com selecao de aula segura:
  - considera periodo vigente;
  - lista apenas datas com licao valida no periodo;
  - bloqueia registro quando nao existe licao valida;
  - sinaliza status da aula selecionada (HOJE, PASSADA, FUTURA).
- Sincronizacao EBD-Agenda ajustada para respeitar horario local da igreja quando configurado.

## Migracoes
- configuracao/migrations/0027_igreja_ebd_config_local.py
- escola_biblica/migrations/0026_licao_evento_agenda.py
- eventos/migrations/0013_evento_tipo_escola_dominical.py
- eventos/migrations/0014_evento_status_cancelamento.py

## Impacto para o Usuario
- Menor chance de erro ao registrar chamada em aula de periodo incorreto.
- Operacao EBD mais intuitiva para secretaria e professores.
- Melhor rastreabilidade de configuracao por igreja.

## Impacto Tecnico
- Com migracoes de banco (schema controlado).
- Sem breaking changes de API publica.

## Check de Qualidade
- `manage.py check` executado com sucesso.
- Views e templates principais da chamada sem erros reportados.
