# Changelog — EBD e Documentação

## EBD

- Reforçado o isolamento de chamada: professor só acessa turmas às quais está vinculado e possui cargo EBD ativo.
- Adicionado teste de regressão para acesso permitido à própria turma e bloqueio `403` às demais.
- Criado fluxo de fechamento de período por igreja, com diagnóstico de chamadas pendentes e exceção justificada.
- Evoluídos dashboard, relatórios, cópia/preparação anual, cronograma, filtros e listagens da EBD.
- Extraídas responsabilidades da `views.py` para serviços especializados de chamada, períodos, cópia, consultas, dashboard e vínculos.
- Melhorado o cadastro de turma: seletor de professores/colaboradores com cargos EBD exibidos e opções únicas.
- Ampliada a cobertura automatizada do módulo.

## Documentação

- Atualizado o guia operacional da EBD e a governança de períodos.
- Incluída a documentação do Design System, abrangendo formulários, cards, tabelas, modais, feedback, navegação, dashboards, acessibilidade, animações, boas práticas e governança.
- Incluído o conjunto de documentos de segurança, com fundamentos, proteção da informação, identidade, autorização, multi-tenant, aplicação, APIs, privacidade e infraestrutura.
