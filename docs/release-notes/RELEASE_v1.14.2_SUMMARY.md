# RELEASE v1.14.2 - Hinário Premium com compliance, temas e UX otimizada

Data: 10/07/2026

## Resumo Executivo
A release v1.14.2 consolida a entrega do Hinário Premium no GereIgreja. Foram adicionados o catálogo interno, detalhe do hino, governança jurídica com bloqueio por padrão, fila de compliance no painel do desenvolvedor, liberação em lote e classificação por temas. A interface do catálogo e do detalhe foi ajustada para priorizar a leitura do hino e reduzir distrações visuais.

## Principais Entregas
- Hinário com catálogo interno e detalhe premium para o portal do membro.
- Governança jurídica com status de licença, detentor de direitos, referência legal e notas de análise.
- Fila de compliance no painel do desenvolvedor com liberação individual e em lote.
- Seleção em massa por página e por conjunto filtrado na fila de compliance.
- Classificação em lote por tema para facilitar navegação litúrgica.
- Sistema de temas de hino com filtros por tema, chips nos cards e exibição no detalhe.
- Otimização visual do catálogo e do detalhe para priorizar a letra do hino.
- Correção de uso de `deleted_at` no admin e ajuste de layout da fila de compliance.

## Documentação Incluída
- Base jurídica e política de conformidade em `docs/produto/00-Hinario-Base-Juridica.md`
- Especificação funcional do Hinário em `docs/produto/01-Hinario-Especificacao.md`
- Portal do usuário do Hinário em `docs/produto/02-Hinario-Portal-Usuario.md`
- Registro de deploy em `docs/deploy/Deploy-Release-V1.14.2.md`
- Changelog principal atualizado em `CHANGELOG.md`

## Impacto
- Melhora a experiência de leitura e navegação no Hinário.
- Centraliza a governança jurídica antes da liberação pública.
- Permite organizar hinos por uso litúrgico e tema.
- Dá suporte a revisões em lote com rastreabilidade operacional.

## Validação
- `python manage.py makemigrations hinario --check --dry-run` executado com sucesso.
- `python manage.py check` executado com sucesso.
- Migração de temas aplicada com sucesso.

## Observações Operacionais
- Deploy seguro via push para `main`, com acionamento automático do fluxo configurado do projeto.
- Recomenda-se revisar os temas padrões e expandir a taxonomia conforme uso real do portal.
