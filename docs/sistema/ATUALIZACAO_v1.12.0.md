# Atualizacao Gereigreja v1.12.0 - 13/05/2026

## Visao Geral

Este documento consolida as melhorias implementadas no ciclo v1.12.0 com foco em Secretaria > Documentos, certificados e governanca multi-ministerio para cartas de recomendacao.

Status de deploy:
- A sessao de Carta de Recomendacao foi iniciada e documentada.
- O acesso para usuarios comuns esta temporariamente desativado para producao via feature flag (`FEATURE_CARTA_RECOMENDACAO = False` por padrao).
- Superusuario pode acessar para validacao interna ate a conclusao funcional.

## Principais Entregas

### 1) Reorganizacao de Menu da Secretaria

- Estrutura da Secretaria reorganizada com foco em documentos.
- Inclusao de agrupamento de Certificados dentro de Documentos.
- Inclusao de Carta de Recomendacao na area de Documentos.
- Reuniao de Membros reposicionada para dentro de Documentos.

Resultado:
- Navegacao mais coerente para operacao diaria da secretaria.
- Menor dispersao de funcionalidades relacionadas a documentos.

### 2) Certificados - Apresentacao e Batismo

- Consolidacao da estrategia de impressao por imagem (html2canvas) para preservar fidelidade da previa.
- Certificado de Batismo evoluido com multiplos modelos:
  - classico_unissex
  - elegante_unissex
  - solene_unissex
  - caligrafico_unissex
- Barra de modelos com miniaturas para troca rapida de layout.
- Ajustes de tipografia, composicao de versiculo e blocos de assinatura.
- Ajuste de nomenclatura de arquivos para facilitar escalabilidade e manutencao.

Resultado:
- Previa e impressao com maior consistencia visual.
- Menor risco de regressao de layout entre navegadores na impressao.

### 3) Novo Modulo - Carta de Recomendacao

- Nova rota: secretaria/documentos/carta-recomendacao/
- Nova tela com formulario lateral e previa central.
- Impressao A5 padronizada com html2canvas.
- Inclusao de modelo padrao para ministerios nao organizados.
- Inclusao de modelo exclusivo Vales Classico.

Resultado:
- Emissao de carta com fluxo padronizado.
- Flexibilidade para identidade visual por ministerio.

### 4) Governanca de Modelos por Ministerio

Foi implementada governanca de templates para evitar compartilhamento indevido de modelos exclusivos entre ministerios.

- Novo cadastro tecnico de modelos de carta com classificacao:
  - padrao
  - exclusivo
- Vinculo opcional de modelo exclusivo a um ministerio.
- Ministerio passa a armazenar codigo do modelo selecionado.
- Filtro dinamico no formulario do ministerio para exibir somente:
  - modelos padrao
  - modelos exclusivos do proprio ministerio
- Blindagem no backend ao resolver template:
  - bloqueio de modelo exclusivo de outro ministerio
  - fallback automatico para modelo permitido

Regras de integridade:
- Modelo exclusivo exige ministerio vinculado.
- Modelo padrao nao pode estar vinculado a ministerio.

Resultado:
- Isolamento multi-tenant reforcado.
- Menor risco de vazamento de identidade visual entre organizacoes.

### 5) Melhorias de Admin para Desenvolvedor

- Admin dedicado para modelo de carta de recomendacao.
- Coluna de escopo para leitura rapida:
  - Global
  - Exclusivo de Ministerio
- Orientacoes de preenchimento no formulario administrativo.
- Previa embutida renderizada a partir de template_include.
- Acao para abrir previa em nova aba para validacao em tela maior.

Resultado:
- Reducao de erros de configuracao por template incorreto.
- Operacao tecnica mais rapida para suporte e implantacao.

## Impacto Tecnico

### Integracoes

- Inclusao da view de carta de recomendacao no pacote de views.
- Inclusao da rota de documentos de carta em secretaria/urls.
- Integracao no menu principal da aplicacao.

### Persistencia e Migracoes

- Campo de modelo de carta no Ministerio.
- Nova entidade de registro de modelos de carta.
- Seed inicial com modelos de referencia (padrao e vales_classico).

## Fluxo Operacional Resumido

1. Desenvolvedor cadastra ou ajusta modelos no admin.
2. Ministerio seleciona seu modelo permitido.
3. Secretaria acessa Documentos > Carta de Recomendacao.
4. Sistema resolve template com validacao de escopo.
5. Usuario imprime mantendo fidelidade da previa.

## Arquivos Relevantes

- templates/menu.html
- secretaria/views/carta_recomendacao.py
- secretaria/templates/secretaria/documentos/carta_recomendacao.html
- secretaria/templates/secretaria/documentos/modelos/_carta_recomendacao_padrao.html
- secretaria/templates/secretaria/documentos/modelos/_carta_recomendacao_vales_classico.html
- static/css/documentos/carta_recomendacao.css
- secretaria/views/certificado_batismo.py
- secretaria/templates/secretaria/certificados/certificado_batismo.html
- static/css/certificados/certificado_batismo_base.css
- static/css/certificados/certificado_batismo_classico.css
- static/css/certificados/certificado_batismo_caligrafico.css
- configuracao/models.py
- configuracao/forms.py
- configuracao/admin_ministerio.py
- configuracao/migrations/0025_ministerio_modelo_carta_recomendacao.py
- configuracao/migrations/0026_modelocartarecomendacao_and_seed.py

## Validacao

- Execucao de verificacoes com manage.py check durante o ciclo.
- Sem erros de sintaxe nas alteracoes de documentacao.

---

Atualizado em: 13/05/2026
