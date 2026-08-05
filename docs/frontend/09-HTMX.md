Pasta:
docs/frontend/

Arquivo:
09-HTMX.md

Documento:
GFE-09

Código:
GFE-HTMX

Framework:
GereIgreja Frontend Engineering (GFE)

Versão:
2.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Agosto de 2026

# GFE-09 — Arquitetura HTMX

> *"O HTMX representa a estratégia oficial do GereIgreja para evolução gradual da experiência do usuário, permitindo interfaces mais rápidas, interativas e modernas sem abandonar a arquitetura nativa do Django."*

---

# Sumário

1. Objetivo
2. Escopo
3. Visão Estratégica
4. Filosofia Arquitetural
5. Estado Atual da Plataforma
6. Estado Futuro Desejado
7. Papel do HTMX na Arquitetura
8. Integração com Django
9. Integração com Templates
10. Integração com Layouts
11. Integração com JavaScript
12. Princípios Arquiteturais
13. Casos Oficiais de Uso
14. Quando NÃO utilizar HTMX
15. Roadmap de Adoção
16. Evidências Arquiteturais
17. Especificações Oficiais
18. Boas Práticas
19. Anti-patterns
20. Checklist
21. Glossário
22. Documentos Relacionados

---

# 1. Objetivo

Este documento estabelece a arquitetura oficial para utilização do HTMX no Frontend do GereIgreja.

Seu propósito é definir como a plataforma deverá evoluir para uma interface mais dinâmica, mantendo compatibilidade total com a arquitetura nativa do Django.

O objetivo não é transformar o GereIgreja em uma Single Page Application (SPA), mas sim incorporar interatividade de forma progressiva, preservando simplicidade, desempenho e facilidade de manutenção.

---

# 2. Escopo

Este documento aplica-se a todas as páginas da Área de Gestão do GereIgreja que utilizem ou venham a utilizar HTMX.

Inclui:

- Templates Django;
- Layouts;
- Componentes;
- Partials;
- Includes;
- Formulários;
- Listagens;
- Dashboards;
- Modais;
- Tabelas;
- Filtros;
- Paginação;
- Atualizações parciais.

Não inclui:

- Administração Técnica (Django Admin);
- APIs REST;
- Aplicativos Mobile;
- Backend de regras de negócio.

---

# 3. Visão Estratégica

O GereIgreja adota oficialmente uma estratégia de evolução progressiva do Frontend.

A arquitetura continuará baseada em:

- Django Templates;
- Renderização Server Side (SSR);
- Bootstrap;
- JavaScript nativo.

O HTMX será utilizado para eliminar recarregamentos completos da página quando apenas uma parte da interface precisar ser atualizada.

Essa abordagem preserva:

- SEO;
- simplicidade arquitetural;
- baixo consumo de recursos;
- facilidade de manutenção;
- produtividade da equipe.

---

# 4. Filosofia Arquitetural

O HTMX não substitui o Django.

O HTMX amplia as capacidades do Django.

Toda renderização continuará sendo responsabilidade do servidor.

Toda regra de negócio continuará sendo executada no Backend.

O navegador será responsável apenas por solicitar atualizações parciais da interface.

Essa filosofia reduz significativamente a complexidade quando comparada a arquiteturas SPA tradicionais.

---

# 5. Estado Atual da Plataforma

A análise da base de código identificou que:

- HTMX já está definido como diretriz oficial nos documentos GFE;
- a estrutura de Templates já foi preparada para suportar sua adoção;
- não foram encontrados atributos `hx-*` utilizados de forma significativa na implementação atual.

Isso demonstra que a plataforma encontra-se preparada arquiteturalmente para receber HTMX de maneira gradual, porém sua utilização prática ainda está em fase inicial.

---

# 6. Estado Futuro Desejado

A longo prazo, espera-se que o HTMX seja utilizado em todos os cenários onde uma atualização parcial da interface seja mais eficiente que um recarregamento completo da página.

Exemplos:

- filtros;
- pesquisas;
- tabelas;
- paginação;
- formulários;
- dashboards;
- notificações;
- cards;
- listas;
- modais;
- indicadores.

A adoção deverá ocorrer gradualmente, módulo por módulo, sem comprometer a estabilidade da plataforma.

---

# 7. Papel do HTMX na Arquitetura

Dentro do GereIgreja, o HTMX possui papel complementar.

Arquitetura conceitual:

```
Usuário

↓

Template Django

↓

HTMX

↓

View Django

↓

Template Parcial

↓

Atualização do DOM
```

Observe que não existe uma camada intermediária de API JavaScript.

O próprio Django continua responsável pela geração do HTML.

Essa arquitetura preserva a filosofia Server Side Rendering (SSR).

---

# 8. Integração com Django

Toda requisição HTMX deverá ser tratada por uma View Django.

Fluxo recomendado:

```
Usuário

↓

HTMX

↓

URL Django

↓

View

↓

Template Parcial

↓

Resposta HTML

↓

Atualização Parcial
```

O retorno preferencial será sempre HTML renderizado pelo servidor.

O uso de JSON deverá ocorrer apenas quando estritamente necessário.

---

# 9. Integração com Templates

Os Templates continuam sendo o principal mecanismo de construção da interface.

O HTMX atuará sobre Templates completos ou Templates parciais.

Sempre que possível deverão ser reutilizados:

- Partials;
- Includes;
- Componentes existentes.

Essa estratégia reduz duplicação de código e mantém a consistência visual da plataforma.

---

# 10. Integração com Layouts

Os Layouts oficiais (`base.html`, `base_com_menu.html`, `dashboard_base.html`, `base_publico.html` e demais layouts especializados) permanecem responsáveis pela estrutura global da interface.

O HTMX deverá atuar apenas sobre regiões internas da página, preservando cabeçalho, menu lateral, rodapé e demais elementos estruturais.

Atualizações parciais não deverão substituir o layout completo.

---

# 11. Integração com JavaScript

O JavaScript continuará responsável por comportamentos que não pertencem ao HTMX.

Exemplos:

- gráficos;
- integração com bibliotecas externas;
- animações complexas;
- manipulação avançada do DOM;
- persistência em Local Storage;
- funcionalidades do `dashboard-sidebar.js`.

Sempre que possível, o HTMX deverá substituir apenas código JavaScript cuja única finalidade seja realizar requisições AJAX e atualizar trechos da interface.

---

# 12. Princípios Arquiteturais

Toda implementação HTMX deverá respeitar os seguintes princípios.

## Renderização no Servidor

O HTML permanece sendo produzido pelo Django.

---

## Reutilização

Os Templates existentes deverão ser reutilizados.

---

## Progressividade

A adoção ocorrerá gradualmente.

Não haverá reescrita completa da plataforma.

---

## Baixo Acoplamento

As requisições HTMX deverão permanecer independentes entre si.

---

## Simplicidade

Sempre escolher a solução mais simples possível.

---

## Compatibilidade

Toda implementação deverá permanecer compatível com:

- Django Templates;
- Bootstrap;
- JavaScript nativo;
- Alpine.js (quando utilizado);
- Design System do GereIgreja.

---
