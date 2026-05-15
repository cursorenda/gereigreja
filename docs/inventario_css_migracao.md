# Inventario de CSS e Plano de Migracao

Este inventario define o destino de cada grupo de CSS no projeto: Manter, Migrar ou Descontinuar.

## Regras de decisao
- Manter: arquivo ativo e necessario para layout/componente especifico.
- Migrar: arquivo ativo com cores/estilos que devem usar tokens do design system.
- Descontinuar: legado, duplicado, build gerado, ou nao deve ser editado manualmente.

## Fonte de verdade
- Design system oficial: static/css/design_system.css

## 1) CSS globais carregados nas bases

### Manter e migrar gradualmente
- static/css/styles.css
- static/css/layout.css
- static/css/formularios.css
- static/css/menus.css
- static/css/botoes.css
- static/css/acessibilidade.css
- static/css/onboarding.css
- static/css/assistente.css

Status:
- Manter ativos.
- Migrar cores/fontes hardcoded para tokens de static/css/design_system.css.

### Candidatos a consolidacao
- static/css/cores.css
- static/css/fontes.css

Status:
- Nao remover agora.
- Gradualmente mover o que for util para design_system.css.
- Quando zerar dependencia, descontinuar com seguranca.

## 2) CSS de paginas publicas

### Manter e migrar gradualmente
- static/css/landing_page.css
- static/css/header.css

Status:
- Continuam ativos.
- Aplicar tokens onde fizer sentido para aproximar identidade da area logada.

## 3) CSS de modulos internos

### Secretaria (ativos)
- static/css/secretaria/secretaria_pessoa.css
- static/css/secretaria/input_foto_colado.css
- static/css/secretaria/input_foto_compact.css
- static/css/secretaria/tab_fix.css
- static/css/secretaria/modern_selector.css

Status:
- Manter.
- Migrar visual (cores, borda, foco, texto) para tokens sem alterar estrutura de formulario.

### Outros modulos especificos
- static/css/agenda.css
- static/css/filtros.css
- static/css/relatorio.css
- static/css/fechamento_caixa.css
- static/css/admin_dashboard_panel.css
- static/css/documentos/carta_recomendacao.css
- static/css/certificados/*.css

Status:
- Manter.
- Migracao seletiva por prioridade visual e risco.
- Certificados e impressao exigem cuidado extra (nao padronizar sem validar output final).

## 4) CSS legados

### Pasta legado
- static/css - antigo/*.css

Status:
- Descontinuar para novas implementacoes.
- Nao usar em templates novos.
- Remocao apenas apos confirmar ausencia de referencia em templates.

## 5) CSS de build/collectstatic

### Nao editar manualmente
- staticfiles/**
- staticfiles_production/**

Status:
- Descontinuar como fonte de edicao.
- Arquivos gerados automaticamente por pipeline/deploy.

## 6) Ordem de trabalho recomendada

1. Fase A - Base global
- Manter design_system.css como fonte de verdade.
- Reduzir dependencias de cores.css e fontes.css.

2. Fase B - Templates base
- Reduzir estilos inline em templates/base_com_menu.html e templates/base.html.
- Criar classes reutilizaveis em CSS global.

3. Fase C - Modulos de maior uso
- Secretaria e Dashboard.
- Migrar para tokens sem mexer em regra de negocio.

4. Fase D - Publico e legado
- Landing/header.
- Higienizacao de arquivos antigos sem uso.

## 7) Politica para novos PRs
- Nao introduzir cor hardcoded sem justificativa.
- Reusar token existente antes de criar novo.
- Evitar style inline para visual estatico.
- Testar desktop e mobile.
