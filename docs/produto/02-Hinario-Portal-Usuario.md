# Hinário do Usuário no Meu Portal

## Objetivo

Substituir o link externo da Harpa Cristã por um catálogo interno premium no portal do membro, mantendo a política de compliance e a experiência visual do sistema.

## Fluxo de Uso

1. O membro acessa a seção **Recursos Devocionais** em `Meu Portal`.
2. O botão **Acessar Hinário** abre o catálogo interno em `/portal/hinario/`.
3. A lista exibe apenas hinos liberados para exibição pública no contexto da igreja.
4. Ao abrir um hino, o sistema mostra letra, cifra e metadados somente se o conteúdo estiver liberado.
5. Conteúdo bloqueado é apresentado com mensagem de revisão, sem exposição do texto protegido.

## Diretrizes Visuais

- Base interna autenticada: `base_com_menu.html`.
- Paleta principal: `#0d8281` com variações escuras para hero e CTA.
- Cantos arredondados, cards com sombra leve e tipografia forte.
- Layout responsivo com hero, estatísticas, filtros e cards em grade.

## Rotas

- Catálogo: `/portal/hinario/`
- Detalhe: `/portal/hinario/hino/<colecao>/<numero>/`

## Regras de Compliance

- Exibir apenas conteúdos liberados por revisão ou domínio público.
- Não renderizar letra/cifra bloqueada.
- Respeitar o contexto da igreja ativa do membro.
