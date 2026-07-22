# Backend - Padrões de Engenharia

Backend
↓
Como construir.

Esta pasta concentra os padrões de implementação do backend do GereIgreja.

Finalidade da pasta:

- definir como o backend deve ser escrito;
- consolidar convenções reutilizáveis;
- padronizar arquitetura, modelagem e camadas técnicas.

O que deve existir aqui:

- padrões de Models, Services, Selectors, Views e Forms;
- convenções de estrutura de app e separação de responsabilidades;
- decisões técnicas transversais aplicáveis a qualquer módulo.

O que não deve existir aqui:

- inventário de classes/serviços de um app específico;
- regras funcionais exclusivas de um módulo de negócio.

Esse conteúdo pertence em `docs/apps/`.

## Como criar um novo documento de Backend

1. Verifique se o tema é transversal e serve para mais de um app.
2. Escolha o próximo número disponível na sequência da pasta.
3. Nomeie no padrão `NN-Tema.md`.
4. Descreva: objetivo, padrão, exemplos e checklist de adoção.
5. Atualize este README e o `docs/INDEX.md`.

## Padrão de Nomenclatura

- `NN-Tema.md` (exemplo: `05-Services.md`)
- `NN` com dois dígitos para manter ordenação visual.

## Índice

- [01-Estrutura-do-Projeto.md](01-Estrutura-do-Projeto.md)
- [02-Core-da-Plataforma.md](02-Core-da-Plataforma.md)
- [03-Arquitetura-dos-Apps.md](03-Arquitetura-dos-Apps.md)
- [04-Models.md](04-Models.md)
- [05-Services.md](05-Services.md)
- [06-Selectors.md](06-Selectors.md)
- [07-Managers.md](07-Managers.md)
- [08-Views.md](08-Views.md)
- [09-Forms.md](09-Forms.md)
