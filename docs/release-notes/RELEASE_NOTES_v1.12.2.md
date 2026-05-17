# Release Notes - Versao 1.12.2

Data de lancamento: 17/05/2026
Tipo: PATCH (correcoes e melhorias de estabilidade)

## Resumo Executivo
Esta versao foca em tres frentes criticas:
- seguranca de escopo multi-igreja no modulo financeiro,
- estabilidade e previsibilidade no modo demonstracao,
- melhorias tecnicas de SEO/indexacao para paginas publicas.

## O que mudou

### 1) Seguranca de dados (Financeiro)
- Transferencias entre caixas agora respeitam `request.igreja_ativa`.
- Removido seletor de igreja redundante na tela de nova transferencia.
- Validacao backend impede transferencias entre igrejas distintas.
- Listagens/historicos de transferencia filtrados por igreja ativa.

Beneficio:
- reduz risco de vazamento de dados entre congregacoes.

### 2) Menu e permissao de lideranca
- Reorganizacao do bloco de lideranca dentro de Gestao Ministerial.
- Rotulos atualizados para melhor entendimento:
  - Paineis Ministeriais
  - Secretaria Ministerial
  - Financeiro Ministerial
- Ajustes de exibicao por perfil/permissao.

Beneficio:
- navegacao mais clara e menor chance de acesso indevido por contexto.

### 3) Modo demonstracao
- Expansao dos perfis demo disponiveis para troca.
- Melhoria de resiliencia quando usuarios demo estao ausentes.
- Ajustes de redirecionamento por perfil apos login/troca.
- Ajustes para evitar bloqueios indevidos por plano no ambiente demo.
- Mensagens orientativas para reset de dados demo.

Beneficio:
- experiencia demo mais estavel para apresentacao comercial e treinamento.

### 4) SEO e indexacao
- Paginas de Politica e Termos migradas para layout publico (`base_landing`).
- Canonical dedicado em ambas as paginas.
- `robots.txt` com allow explicito para `/contas/registrar/`.
- `sitemap.xml` expandido com pagina publica de cadastro.
- Landing com links diretos para posts recentes do blog.

Beneficio:
- melhora sinais de rastreio e descoberta de conteudo publico.

## Impacto esperado
- Menor risco de regressao de escopo multi-tenant no financeiro.
- Menos falhas no fluxo demo e melhor navegacao por perfil.
- Melhor prioridade de rastreamento para conteudos publicos.

## Checklist operacional
- [ ] Executar deploy em producao
- [ ] Confirmar `https://gereigreja.site/sitemap.xml` atualizado
- [ ] Validar retorno 200 para:
  - `/politica-privacidade/`
  - `/termos-condicoes/`
  - `/contas/registrar/`
- [ ] Solicitar indexacao no Google Search Console para URLs prioritarias

## Arquivos-chave desta release
- `financeiro/forms.py`
- `financeiro/views.py`
- `financeiro/templates/financeiro/transferencia_caixa_form.html`
- `templates/menu.html`
- `templates/base_com_menu.html`
- `demo/views.py`
- `secretaria/management/commands/popular_demo.py`
- `configuracao/services_assinatura.py`
- `core/context_status_plano.py`
- `templates/core/politica_privacidade.html`
- `templates/core/termos_condicoes.html`
- `templates/robots.txt`
- `core/sitemaps.py`
- `contas/views.py`
- `contas/templates/contas/landing_page.html`

---
Equipe Gereigreja
