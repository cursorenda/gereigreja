# Release Notes - Versao 1.13.13

Data de lancamento: 02/06/2026
Tipo: PATCH (engajamento EBD + SEO social)

## Resumo Executivo
Esta release fortalece dois pilares importantes:
- operacao da Escola Dominical com pontuacao e ranking de alunos;
- confiabilidade de compartilhamento social dos posts do blog.

## O que mudou

### 1) EBD com pontuacao configuravel por igreja
- Novos campos na configuracao da igreja para definir pontos por categoria:
  - Presenca
  - Biblia
  - Revista
  - Oferta
  - Visitante
- Regras ficam acessiveis na aba EBD, com fallback para valores padrao quando nao preenchidas.

Beneficio:
- cada igreja pode calibrar o incentivo pedagogico conforme sua realidade.

### 2) Chamada com calculo automatico de pontos
- A chamada continua com o fluxo atual de marcacao (presente/biblia/revista/oferta/visitante).
- Ao salvar, a pontuacao da aula e computada automaticamente.
- A tela exibe a regra ativa de pontos para reduzir ambiguidades na operacao.

Beneficio:
- experiencia simples para a professora e maior consistencia dos dados de desempenho.

### 3) Dashboard com ranking de melhores alunos
- Novo bloco no dashboard EBD: Melhores Alunos por Pontos.
- Ranking respeita o periodo selecionado no dashboard.
- Ordenacao por pontos totais e, em empate, por presencas.

Beneficio:
- visao premium e acionavel para lideranca EBD acompanhar evolucao de engajamento.

### 4) Preview social do blog corrigido
- Ajustes de Open Graph/Twitter no detalhe do post:
  - canonical e og:url coerentes com a URL do post;
  - og:image/twitter:image absolutos;
  - og:type por pagina com article no detalhe;
  - metadados de imagem (alt, width, height).

Beneficio:
- compartilhamento social mais confiavel em Facebook/WhatsApp/LinkedIn.

## Migracoes desta release
- `configuracao/migrations/0028_igreja_ebd_pontos.py`

## Checklist operacional
- [x] Executar migration em producao
- [x] Validar `manage.py check`
- [ ] Validar configuracao de pontos em ao menos uma igreja
- [ ] Validar ranking de alunos no dashboard EBD
- [ ] Validar preview de post no Facebook Sharing Debugger

## Arquivos-chave desta release
- `configuracao/models.py`
- `configuracao/forms.py`
- `configuracao/templates/configuracao/igrejas/editar_igreja_config.html`
- `configuracao/migrations/0028_igreja_ebd_pontos.py`
- `escola_biblica/views.py`
- `escola_biblica/templates/escola_biblica/chamada_presenca.html`
- `escola_biblica/templates/escola_biblica/dashboard.html`
- `templates/base_landing.html`
- `templates/blog/detalhe.html`
- `blog/views.py`

---
Equipe Gereigreja
