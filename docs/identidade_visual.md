# Identidade Visual - Gereigreja

Este documento define o padrao visual minimo do sistema para reduzir variacoes de cores, fontes e estilos entre telas.

## Objetivo
- Garantir consistencia visual entre modulos.
- Reduzir CSS inline e valores hardcoded.
- Facilitar manutencao e evolucao de interface.

## Fonte da Verdade
- Arquivo principal: static/css/design_system.css
- Bases que carregam o design system:
  - templates/base_com_menu.html
  - templates/base.html
  - templates/base_publico.html

## Paleta Oficial (enxuta)
- Regra de identidade:
  - Uma cor de marca principal
  - Variacoes tonais da mesma marca para hover e estados suaves
  - Neutros para a maior parte da interface
  - Cores semanticas apenas para feedback

- Marca (turquesa):
  - --gi-color-brand-700: #0D8281 (principal)
  - --gi-color-brand-900: #0A6665 (hover/ativo)
  - --gi-color-brand-soft: #DFF4F3 (fundo suave de destaque)

- Neutros:
  - --gi-color-bg: #F1F5F9
  - --gi-color-surface: #FFFFFF
  - --gi-color-border: #D7E2E8
  - --gi-color-text: #1E293B
  - --gi-color-text-muted: #64748B

- Semanticos:
  - --gi-color-success: #10B981
  - --gi-color-warning: #D97706
  - --gi-color-danger: #EF4444

- Tipografia:
  - --gi-font-sans
  - --gi-font-mono
  - --gi-font-size-base

## Regras Praticas
- Evitar usar style="..." em templates, exceto quando for dinamico e inevitavel.
- Preferir classes de componente e utilitarios do design system.
- Para cores, usar variaveis CSS em vez de hex direto.
- Evitar criar novas familias de fonte sem justificativa de produto.
- Em fundo de marca, usar texto claro para contraste.
- Evitar usar cores de alerta/erro como cor principal de layout.
- Priorizar texto padrao em --gi-color-text (#1E293B); reservar turquesa para interacoes (botoes, links, foco e destaques de navegacao).

## Padrao de Novos Componentes
- Botao principal: usar btn btn-primary.
- Cartao: usar .card com borda e sombra padrao do design system.
- Inputs: usar form-control/form-select sem sobrescrever visual localmente.

## Guia Rapido por Componente
- Menu ativo: icone/texto em --gi-color-brand-700 e fundo em --gi-color-brand-soft.
- Botao primario: --gi-color-brand-700 e hover em --gi-color-brand-900.
- Formularios: campos claros, borda neutra, foco com anel da cor de marca.
- Tabelas: base neutra com listras leves em --gi-color-surface-soft.

## Plano de Migracao
1. Fase 1: base global de tokens (concluida).
2. Fase 2: remover estilos inline de templates estruturais (base, menu, dashboard).
3. Fase 3: consolidar CSS por modulo para consumir tokens.
4. Fase 4: revisar acessibilidade visual (contraste e estados de foco).

## Checklist para PR
- Nao adicionou cor hardcoded sem necessidade.
- Nao adicionou nova fonte sem alinhamento.
- Reutilizou token existente antes de criar um novo.
- Testou em desktop e mobile.
