# RELEASE v1.13.20 - RESUMO EXECUTIVO

Data: 22/06/2026
Tipo: PATCH
Escopo: SEO técnico do blog para melhorar indexação e descoberta orgânica

## Resumo
A versão v1.13.20 fortalece o SEO técnico das páginas públicas do blog, com foco em qualidade de sinais para rastreamento e indexação no Google. O pacote resolve inconsistências de metadados e adiciona dados estruturados essenciais para melhorar compreensão semântica do conteúdo.

## Principais Entregas
- Melhoria de metadados no detalhe de posts:
  - padronização de descrição e palavras-chave usando os blocos oficiais do template base;
  - remoção de duplicidade de meta tags no head;
  - inclusão de metadado de modificação do artigo (`article:modified_time`).
- Dados estruturados implementados:
  - `Article` no detalhe do post;
  - `BreadcrumbList` no detalhe para hierarquia de navegação;
  - `ItemList` na listagem de blog para descoberta de artigos.
- Consistência de SEO on-page:
  - manutenção do canonical por URL absoluta do post;
  - reforço dos sinais para reduzir incidência de URLs "Detectadas, mas não indexadas no momento".

## Arquivos Impactados
- `templates/blog/detalhe.html`
- `templates/blog/lista.html`
- `CHANGELOG.md`

## Migrações
- Nenhuma.

## Validação
- `python manage.py check` executado com sucesso (0 issues).

## Impacto para o Usuário
- Melhor potencial de visibilidade orgânica dos artigos.
- Aumento da chance de indexação gradual de conteúdos já publicados.
- Base mais sólida para estratégia editorial e Search Console.

## Impacto Técnico
- Estrutura semântica mais clara para buscadores e sistemas de IA.
- Sinais de qualidade on-page mais consistentes.
- Sem alteração de schema e sem breaking changes.
