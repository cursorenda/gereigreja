# RELEASE v1.13.13 - RESUMO EXECUTIVO

Data: 02/06/2026
Tipo: PATCH
Escopo: Escola Dominical (EBD) + Blog (SEO Social)

## Resumo
A versao v1.13.13 introduz pontuacao configuravel por igreja na EBD, com ranking de alunos por desempenho no dashboard, e consolida correcoes de Open Graph/Twitter para garantir preview social correto dos posts do blog.

## Principais Entregas
- Configuracao de pontuacao EBD por igreja:
  - Presenca
  - Biblia
  - Revista
  - Oferta
  - Visitante
- Chamada de presenca com exibicao da regra de pontos ativa e computo automatico ao salvar.
- Dashboard EBD com ranking de melhores alunos por pontos no periodo selecionado.
- Melhor feedback operacional na chamada com total de pontos da aula.
- Correcao de metadados sociais do blog:
  - canonical e og:url por post,
  - og:image/twitter:image absolutos,
  - og:type=article no detalhe,
  - og:image:alt/width/height.

## Migracoes
- configuracao/migrations/0028_igreja_ebd_pontos.py

## Impacto para o Usuario
- Estimula participacao e engajamento em sala de aula com criterio claro.
- Permite estrategia local por igreja sem perder padrao do sistema.
- Lideranca passa a acompanhar desempenho de forma objetiva pelo ranking.
- Compartilhamento de posts com imagem correta nas redes sociais.

## Impacto Tecnico
- Com migration de schema (novos campos de pontuacao na igreja).
- Sem breaking changes de API publica.

## Check de Qualidade
- `manage.py migrate` executado com sucesso.
- `manage.py check` executado com sucesso.
- Validacao de query ORM de ranking por pontos executada com sucesso.
