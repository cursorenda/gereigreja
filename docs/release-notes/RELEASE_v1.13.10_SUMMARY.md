# RELEASE v1.13.10 - RESUMO EXECUTIVO

Data: 28/05/2026
Tipo: PATCH
Escopo: Escola Dominical (EBD)

## Resumo
A versao v1.13.10 evolui a EBD para um modelo mais automatico e mais seguro: periodos e licoes passam a ser sincronizados automaticamente no uso do modulo, e o sistema passa a aplicar validacoes estritas para garantir que licoes, frequencias e ofertas respeitem o periodo EBD configurado.

## Principais Entregas
- Auto-sync de periodos EBD para ano atual e proximo ano.
- Auto-geracao de licoes do periodo vigente (ou proximo) sem depender de clique manual.
- Acionamento automatico em dashboard EBD, chamada por turma e lista de turmas.
- Novo utilitario para gerar datas pelo dia da semana configurado da EBD.
- Validacoes de dominio para bloquear registros fora do periodo valido em:
  - Licoes
  - Frequencias
  - Ofertas por turma
- Constraint de unicidade para licoes por turma+data.

## Impacto para o Usuario
- Menos passos manuais para a secretaria/superintendencia EBD.
- Mais previsibilidade: operacao e relatorios alinhados ao periodo oficial.
- Menor risco de inconsistencias de lancamento.

## Impacto Tecnico
- Com migration de schema (constraint de unicidade em licoes).
- Sem breaking changes de API publica.

## Check de Qualidade
- `manage.py check` executado com sucesso.
- Verificacao de duplicidade para turma+data de licoes retornou 0 antes da constraint.
