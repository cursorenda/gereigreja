Pasta:
docs/frontend/

Arquivo:
01-Frontend-Architecture.md

Documento:
GFE-01

Framework:
GereIgreja Frontend Engineering (GFE)

Versão:
2.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# 01 - Frontend Architecture

> *"O Frontend do GereIgreja não é apenas uma coleção de páginas HTML. Ele constitui a camada oficial de apresentação da plataforma, projetada para oferecer consistência visual, reutilização de componentes, baixa duplicação de código e integração transparente com a arquitetura do Backend."*

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia do Frontend
4. Objetivos Arquiteturais
5. Estado Atual da Arquitetura
6. Stack Oficial
7. Visão Geral da Arquitetura
8. Fluxo de Renderização
9. Decisões Arquiteturais
10. Documentos Relacionados

---

# 1. Objetivo

Este documento define a arquitetura oficial do Frontend do GereIgreja.

Seu propósito é estabelecer os princípios, padrões e decisões arquiteturais que orientam a construção da camada de apresentação da plataforma.

Este documento não descreve componentes específicos nem detalhes de implementação. Seu papel é apresentar a visão arquitetural de alto nível que deverá orientar toda evolução futura do Frontend.

Em termos práticos, o projeto já utiliza essa arquitetura como referência oficial, mas ainda convive com trechos legados e módulos em transição. A padronização deve ser entendida como um processo gradual, não como uma substituição imediata de tudo o que existe hoje.

Todos os documentos da pasta `docs/frontend/` complementam esta especificação.

---

# 2. Escopo

Este documento cobre exclusivamente a arquitetura da camada de apresentação do GereIgreja.

São abordados:

- arquitetura geral do Frontend;
- tecnologias oficiais;
- organização da renderização;
- comunicação com o Backend;
- hierarquia arquitetural;
- princípios de reutilização;
- diretrizes oficiais da interface.

Os detalhes específicos de Layouts, Templates, Componentes, Assets e JavaScript são documentados em arquivos próprios.

---

# 3. Filosofia do Frontend

O Frontend do GereIgreja foi concebido para ser uma camada de apresentação organizada, previsível e altamente reutilizável.

Toda decisão arquitetural deve preservar cinco princípios fundamentais:

- simplicidade;
- consistência visual;
- reutilização de estruturas existentes;
- separação clara entre apresentação e regra de negócio;
- facilidade de manutenção.

O Frontend não concentra regras de negócio. Sua responsabilidade é apresentar informações produzidas pelo Backend de forma clara, consistente e responsiva.

Toda nova funcionalidade deverá priorizar o reaproveitamento da arquitetura existente antes da criação de novas estruturas.

---

# 4. Objetivos Arquiteturais

A arquitetura do Frontend possui os seguintes objetivos permanentes:

- manter identidade visual única em toda a plataforma;
- reduzir duplicação de código;
- facilitar evolução dos módulos;
- simplificar manutenção dos templates;
- padronizar componentes reutilizáveis;
- proporcionar experiência consistente ao usuário;
- permitir crescimento contínuo sem aumento desnecessário da complexidade.

Esses objetivos orientam todas as decisões relacionadas à interface do sistema.

---

# 5. Estado Atual da Arquitetura

A tabela abaixo representa o estado oficial das tecnologias adotadas pelo Frontend.

| Tecnologia | Estado |
|------------|---------|
| Django Templates | ✅ Implementado |
| Bootstrap 5 | ✅ Implementado |
| CSS próprio | ✅ Implementado |
| JavaScript | ✅ Implementado |
| Font Awesome | ✅ Implementado |
| Dashboard Framework | ✅ Implementado |
| HTMX | 🟡 Padronizado (adoção gradual) |
| Alpine.js | 🟡 Padronizado (adoção gradual) |
| Progressive Web App (PWA) | 🔵 Planejado |
| Aplicativo Mobile | 🔵 Planejado |

A documentação diferencia claramente tecnologias implementadas, tecnologias oficialmente padronizadas e tecnologias previstas para evolução futura.

---

# 6. Stack Oficial

O Frontend do GereIgreja utiliza uma combinação de tecnologias consolidadas e amplamente adotadas pelo ecossistema Django.

| Tecnologia | Responsabilidade |
|------------|------------------|
| Django Templates | Renderização server-side da interface |
| Bootstrap 5 | Sistema de layout responsivo e componentes básicos |
| CSS próprio | Design System e identidade visual da plataforma |
| JavaScript | Comportamentos dinâmicos da interface |
| Font Awesome | Biblioteca oficial de ícones |
| HTMX | Atualizações parciais da interface (adoção gradual) |
| Alpine.js | Comportamentos leves da interface (adoção gradual) |

A adoção de novas tecnologias deverá respeitar a arquitetura existente e evitar aumento desnecessário da complexidade do Frontend.

---

# 7. Visão Geral da Arquitetura

A arquitetura do Frontend integra-se diretamente à arquitetura do Backend.

O fluxo oficial da plataforma é representado pelo seguinte diagrama:

```text
                 Usuário
                    │
                    ▼
              Navegador Web
                    │
                    ▼
              URL do Django
                    │
                    ▼
                  View
          ┌─────────┴─────────┐
          ▼                   ▼
      Services          Selectors
          │                   │
          └─────────┬─────────┘
                    ▼
                 Models
                    │
                    ▼
           Django Templates
                    │
              Layouts Base
                    │
        Includes + Partials
                    │
                    ▼
               HTML Final
                    │
                    ▼
               Navegador
```

Esta arquitetura mantém responsabilidades claramente separadas entre Backend e Frontend, favorecendo manutenção, reutilização e evolução da plataforma.

---

# 8. Fluxo de Renderização

O processo oficial de renderização do GereIgreja segue as seguintes etapas:

1. O usuário realiza uma requisição.
2. A URL direciona a requisição para uma View.
3. A View delega regras de negócio aos Services.
4. As consultas reutilizáveis são executadas pelos Selectors.
5. Os Models fornecem os dados persistidos.
6. A View envia o contexto ao Template.
7. O Template herda o Layout correspondente.
8. Includes e Partials compõem a interface.
9. O HTML final é enviado ao navegador.

Esse fluxo representa a separação oficial de responsabilidades adotada pelo GereIgreja.

---

# 9. Decisões Arquiteturais

As decisões abaixo passam a fazer parte da arquitetura oficial da plataforma.

### DA-001 — Renderização Server-Side

Toda a interface do GereIgreja utiliza Django Templates como mecanismo oficial de renderização.

---

### DA-002 — Hierarquia de Templates

A interface deverá ser construída utilizando herança de layouts, evitando duplicação de código.

---

### DA-003 — Separação entre Backend e Frontend

Regras de negócio permanecem exclusivamente no Backend.

Templates não deverão implementar lógica de negócio.

---

### DA-004 — Reutilização

Sempre que possível deverão ser reutilizados:

- layouts;
- includes;
- partials;
- componentes existentes.

Novas estruturas deverão ser criadas apenas quando justificadas.

---

### DA-005 — Evolução Progressiva

Tecnologias como HTMX e Alpine.js fazem parte da arquitetura oficial do Frontend e serão incorporadas gradualmente aos novos módulos, preservando compatibilidade com a implementação existente.

---

# 10. Documentos Relacionados

- GFE-02 — Estrutura de Pastas
- GFE-03 — Componentes
- GFE-04 — Layouts
- GFE-05 — Templates
- GDS — GereIgreja Design System
- GQF — GereIgreja Quality Framework
- GDF — GereIgreja Documentation Framework

---

## ✅ Parte 1 concluída

---

# 11. Pilares da Arquitetura do Frontend

O Frontend do GereIgreja foi construído sobre pilares arquiteturais que orientam toda evolução da camada de apresentação.

## 11.1 Reutilização

Sempre que possível deverão ser reutilizados:

- layouts existentes;
- templates;
- partials;
- includes;
- componentes visuais;
- estilos CSS;
- scripts JavaScript.

Duplicação de código deve ser evitada.

---

## 11.2 Padronização

Todos os módulos devem apresentar comportamento visual consistente.

Isso inclui:

- navegação;
- breadcrumbs;
- botões;
- formulários;
- tabelas;
- mensagens;
- paginação;
- dashboards.

O usuário deve perceber uma experiência uniforme em toda a plataforma.

---

## 11.3 Modularização

Cada módulo do sistema possui autonomia funcional, porém compartilha a mesma infraestrutura de interface.

A evolução de um módulo não deve causar impacto visual ou estrutural em outros módulos.

---

## 11.4 Separação de Responsabilidades

A camada de apresentação não deve conter regras de negócio.

A responsabilidade do Frontend limita-se a:

- apresentar informações;
- receber entradas do usuário;
- organizar componentes visuais;
- melhorar a experiência de navegação.

Toda regra de negócio permanece concentrada no Backend.

---

## 11.5 Evolução Contínua

A arquitetura foi projetada para permitir evolução incremental.

Novas tecnologias poderão ser incorporadas desde que:

- preservem compatibilidade com a arquitetura existente;
- reduzam complexidade;
- aumentem reutilização;
- mantenham estabilidade da plataforma.

---

# 12. Hierarquia Arquitetural dos Layouts

O GereIgreja possui duas arquiteturas distintas de interface, cada uma destinada a um contexto específico da aplicação.

Essa separação é uma decisão arquitetural oficial da plataforma e evita o acoplamento entre a administração técnica do sistema e a interface utilizada pelos usuários.

> Nomenclatura oficial desta separação: "Administração Técnica (Django Admin)" e "Área de Gestão do GereIgreja".

## 12.1 Administração Técnica (Django Admin)

A Administração Técnica é baseada na infraestrutura nativa do Django Admin.

Essa área é destinada exclusivamente à administração técnica da plataforma, manutenção do sistema e funcionalidades voltadas aos desenvolvedores ou administradores técnicos.

Sua hierarquia de templates permanece baseada nos arquivos do próprio Django Admin.

Exemplos:

- `admin/base_site.html`
- `admin/index.html`
- `dashboard_desenvolvedor.html`

Esses templates **não herdam de `base_com_menu.html`**.

---

## 12.2 Área de Gestão do GereIgreja

A Área de Gestão corresponde às telas utilizadas pelos usuários autenticados da plataforma, como:

- Pastores;
- Secretários;
- Tesoureiros;
- Professores;
- Equipe de Comunicação;
- Recepção;
- Demais perfis do ministério.

Essa interface é construída sobre a arquitetura própria do GereIgreja.

Sua hierarquia é baseada em:

```text
base.html
        │
        ▼
base_com_menu.html
        │
        ▼
dashboard_base.html
        │
        ▼
Templates dos módulos
```

Todos os módulos funcionais da plataforma devem utilizar essa infraestrutura, garantindo identidade visual, reutilização e padronização da experiência do usuário.

Essa camada corresponde à Área de Gestão do GereIgreja. A Administração Técnica (Django Admin) permanece com sua própria hierarquia de templates, preservando a separação entre a interface técnica e a interface de gestão utilizada pelos usuários.

---

## 12.3 Motivações da Separação

A existência de duas arquiteturas independentes permite:

- preservar a identidade do Django Admin para tarefas técnicas;
- evoluir a interface de gestão sem depender da estrutura do Django Admin;
- reduzir acoplamento entre camadas;
- facilitar manutenção da plataforma;
- manter experiências distintas para usuários finais e administradores técnicos.

Essa separação é considerada uma decisão arquitetural permanente do GereIgreja.

---

# 13. Organização da Camada de Apresentação

A camada de apresentação do GereIgreja é composta por diferentes níveis de reutilização.

## Layouts

Responsáveis pela estrutura principal das páginas.

Exemplos:

- base.html;
- base_com_menu.html;
- dashboard_base.html.

---

## Includes

Responsáveis por elementos estruturais reutilizados pelos layouts.

Atualmente incluem, entre outros:

- app_footer.html;
- auth_footer.html;
- public_footer.html;
- footer_social_links.html.

Esses arquivos representam infraestrutura compartilhada da interface.

---

## Partials

Representam fragmentos reutilizáveis de telas.

Exemplos atuais:

- abas;
- formulários;
- conjuntos de campos;
- blocos específicos reutilizados por diferentes páginas.

O uso de partials reduz duplicação e facilita manutenção.

---

# 14. Comunicação entre Backend e Frontend

O Frontend não acessa diretamente a camada de persistência.

O fluxo oficial de comunicação é:

```text
Template
    │
    ▼
View
    │
    ▼
Services
    │
    ▼
Selectors
    │
    ▼
Models
```

Cada camada possui responsabilidade específica.

Essa separação reduz acoplamento e aumenta a manutenibilidade do sistema.

---

# 15. Estado Evolutivo da Arquitetura

A arquitetura do GereIgreja encontra-se em evolução contínua.

Atualmente:

### Implementado

- Django Templates;
- Bootstrap;
- CSS próprio;
- JavaScript;
- Font Awesome;
- Layouts hierárquicos;
- Dashboard Framework;
- reutilização de partials;
- reutilização de includes.

### Em adoção gradual

- HTMX;
- Alpine.js.

### Planejado

- Progressive Web App (PWA);
- Aplicativos móveis;
- ampliação da componentização da interface.

Essa distinção permite que a documentação reflita fielmente o estado atual do projeto.

---

# 16. Convenções Oficiais

Todo novo desenvolvimento deverá seguir obrigatoriamente as seguintes convenções:

- reutilizar layouts existentes;
- evitar HTML duplicado;
- utilizar includes apenas para elementos estruturais;
- utilizar partials para fragmentos reutilizáveis de telas;
- manter compatibilidade com o Design System;
- preservar a hierarquia oficial dos templates;
- respeitar os padrões definidos na documentação do Frontend.

---

# 17. Boas Práticas

Sempre:

- reutilizar componentes existentes;
- manter templates pequenos e organizados;
- documentar novas decisões arquiteturais;
- utilizar nomenclaturas consistentes;
- preservar separação entre apresentação e lógica.

A simplicidade deve ser priorizada em todas as implementações.

---

# 18. Antipadrões

Evitar:

- duplicação de layouts;
- lógica de negócio em templates;
- criação de novos layouts sem necessidade;
- JavaScript desnecessário;
- CSS específico para apenas uma página quando puder ser reutilizado;
- fragmentação excessiva de componentes;
- acoplamento entre módulos.

Esses padrões aumentam a complexidade e dificultam a manutenção da plataforma.

---

# 19. Checklist Arquitetural

Antes de implementar qualquer nova funcionalidade no Frontend verificar:

- utiliza os layouts oficiais?
- reutiliza componentes existentes?
- evita duplicação?
- respeita o Design System?
- mantém separação entre Backend e Frontend?
- utiliza partials quando apropriado?
- documentou alterações arquiteturais?
- preserva compatibilidade com futuras evoluções?

---

# 20. Roadmap Arquitetural

A evolução planejada do Frontend contempla:

- ampliação da adoção de HTMX;
- adoção gradual de Alpine.js quando aplicável;
- expansão do Dashboard Framework;
- aumento da componentização da interface;
- preparação para Progressive Web App (PWA);
- suporte à futura camada mobile.

Toda evolução deverá preservar compatibilidade com a arquitetura estabelecida neste documento.

---

# 21. Documentos Relacionados

### Frontend

- GFE-02 — Estrutura de Pastas
- GFE-03 — Componentes
- GFE-04 — Layouts
- GFE-05 — Templates

### Frameworks

- GDS — GereIgreja Design System
- GQF — GereIgreja Quality Framework
- GDF — GereIgreja Documentation Framework

### Backend

- GBE-03 — Arquitetura dos Apps
- GBE-05 — Services
- GBE-06 — Selectors
- GBE-08 — Views

---

# 22. Princípios Finais

O Frontend do GereIgreja constitui a camada oficial de apresentação da plataforma.

Sua arquitetura foi concebida para garantir consistência visual, reutilização de componentes, baixo acoplamento e evolução contínua.

Toda alteração na interface deverá preservar os princípios estabelecidos neste documento, assegurando que a experiência do usuário permaneça uniforme e que a manutenção do sistema continue simples, previsível e escalável.

Este documento é a referência arquitetural oficial para toda a camada de Frontend do GereIgreja.

