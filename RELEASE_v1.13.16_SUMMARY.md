# RELEASE v1.13.16 - RESUMO EXECUTIVO

Data: 13/06/2026
Tipo: PATCH
Escopo: Secretaria Premium (cadastro, edicao, listagem, UI e governanca)

## Resumo
A versao v1.13.16 consolida a migracao definitiva do cadastro legado para o fluxo premium da Secretaria, reforca a integridade de edicao de pessoas (incluindo controle de concorrencia e motivo obrigatorio para mudancas criticas), moderniza as telas premium principais e padroniza o comportamento de recolhimento do menu lateral nas paginas operacionais.

## Principais Entregas
- Descontinuidade do cadastro legado com compatibilidade mantida:
  - `pessoas/cadastrar/` passa a redirecionar para o cadastro premium;
  - etapas antigas de cadastro redirecionam para o novo fluxo com mensagem ao usuario;
  - remocao de templates legados obsoletos.
- Novo fluxo de `Cadastro Premium por Etapas`:
  - nova view dedicada (`cadastro_premium_multietapas`);
  - nova rota publica interna de cadastro premium;
  - template multietapas com regras de exibicao por tipo/grau.
- Evolucao de formulario e persistencia premium:
  - novos campos ministeriais no `MembroForm`;
  - parser/upsert de metadados premium em bloco estruturado de `observacoes_visita`;
  - normalizacao de nome/apelido para padrao visual consistente;
  - exclusao de `Obreiro` nas selecoes de tipo aplicaveis.
- Busca/ac autocomplete de nomes com tolerancia a acentos:
  - utilitarios novos em `secretaria.utils`;
  - aplicacao em listagens e endpoints AJAX de autocomplete.
- Governanca de edicao reforcada:
  - protecao de concorrencia por token de atualizacao;
  - motivo obrigatorio para mudancas de Tipo, Status, Igreja e Grau;
  - melhoria no registro de historico de transicoes com motivo e data final consistente.
- Padronizacao Premium de UI:
  - redesign de lista, detalhe, ficha de impressao e edicao;
  - novos JS/CSS premium por tela e por secao de formulario.
- Sidebar recolhivel padronizada em paginas premium da Secretaria:
  - lista, cadastro premium e editar pessoa;
  - persistencia via `secretaria.sidebar_visible`.

## Arquivos Impactados (nao commitados antes da release)
- Alterados:
  - `secretaria/forms.py`
  - `secretaria/models.py`
  - `secretaria/static/secretaria/form_date_masks.js`
  - `secretaria/static/secretaria/form_dynamic.js`
  - `secretaria/static/secretaria/form_tipo_status.js`
  - `secretaria/static/secretaria/secretaria_navegacao.js`
  - `secretaria/templates/partials/_form_pessoa_oficial.html`
  - `secretaria/templates/secretaria/cadastro_publico.html`
  - `secretaria/templates/secretaria/dashboard.html`
  - `secretaria/templates/secretaria/detalhe_membro.html`
  - `secretaria/templates/secretaria/editar_membro.html`
  - `secretaria/templates/secretaria/index.html`
  - `secretaria/templates/secretaria/lista_membros.html`
  - `secretaria/templates/secretaria/membro/ficha_membro_impressao.html`
  - `secretaria/urls.py`
  - `secretaria/utils.py`
  - `secretaria/views/__init__.py`
  - `secretaria/views/_legacy.py`
  - `secretaria/views/ajax.py`
  - `secretaria/views/membros.py`
- Novos:
  - `secretaria/static/secretaria/cadastro_premium_multietapas.js`
  - `secretaria/static/secretaria/editar_membro_premium.js`
  - `secretaria/static/secretaria/form_sections_premium.js`
  - `secretaria/templates/secretaria/cadastro_premium_multietapas.html`
  - `secretaria/views/cadastro_legado_redirects.py`
  - `secretaria/views/cadastro_premium.py`
  - `static/css/secretaria/detalhe_membro_premium.css`
  - `static/css/secretaria/ficha_membro_impressao_premium.css`
  - `static/css/secretaria/form_sections_premium.css`
  - `static/css/secretaria/lista_membros_premium.css`
  - `static/css/secretaria/premium_sidebar_toggle.css`
  - `tests/test_secretaria_edicao_concorrencia.py`
- Removidos:
  - `secretaria/templates/secretaria/backup_page.html`
  - `secretaria/templates/secretaria/cadastro_complementar.html`
  - `secretaria/templates/secretaria/cadastro_detalhado.html`

## Migracoes
- Nenhuma.

## Validacao
- `python manage.py check` executado com sucesso (0 issues).

## Impacto para o Usuario
- Navegacao mais simples e consistente no cadastro de pessoas.
- Menor risco de perder alteracoes em edicoes simultaneas.
- Interface premium mais clara para lista, cadastro, detalhe e impressao.
- Menos ruido no filtro de tipos com remocao de opcoes descontinuadas.

## Impacto Tecnico
- Sem mudanca de schema e sem breaking changes de API publica.
- Refatoracao significativa no fluxo da Secretaria, com compatibilidade de URLs legadas preservada.
