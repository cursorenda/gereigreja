Pasta:
docs/frontend/

Arquivo:
11-Dashboards.md

Documento:
GFE-11

Código:
GFE-DASH

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

# GFE-11 — Arquitetura dos Dashboards

> *"Os Dashboards representam a principal interface de gestão do GereIgreja, concentrando indicadores, ações rápidas, análises e informações estratégicas para apoiar a tomada de decisão dos usuários."*

---

# Sumário

1. Objetivo
2. Escopo
3. Visão Estratégica
4. Filosofia dos Dashboards
5. Estado Atual da Plataforma
6. Arquitetura Geral
7. Dashboard Base
8. Estrutura Oficial
9. Componentes do Dashboard
10. Sidebar Premium
11. Breadcrumbs
12. KPIs
13. Cards
14. Widgets
15. Integração com Layouts
16. Integração com HTMX
17. Integração com Alpine.js
18. Integração com JavaScript
19. Responsividade
20. Roadmap
21. Documentos Relacionados

---

# 1. Objetivo

Este documento estabelece oficialmente a arquitetura dos Dashboards do GereIgreja.

Seu objetivo é padronizar a construção de todos os dashboards da plataforma, garantindo consistência visual, reutilização de componentes e evolução sustentável da interface.

---

# 2. Escopo

Aplica-se exclusivamente aos Dashboards da Área de Gestão do GereIgreja.

Inclui:

- Dashboard Inicial;
- Dashboard Financeiro;
- Dashboard Secretaria;
- Dashboard Eventos;
- Dashboard Comunicação;
- Dashboard Escola Bíblica;
- Dashboard Patrimônio;
- futuros dashboards.

Não inclui:

- Administração Técnica (Django Admin);
- páginas públicas;
- Landing Pages;
- Blog.

---

# 3. Visão Estratégica

Os Dashboards constituem a principal interface operacional do GereIgreja.

Seu propósito é oferecer ao usuário uma visão consolidada das informações mais importantes do sistema, permitindo acesso rápido às funcionalidades mais utilizadas.

Todo Dashboard deverá seguir uma estrutura comum, independentemente do módulo.

---

# 4. Filosofia dos Dashboards

Todo Dashboard deverá priorizar:

- clareza;
- objetividade;
- velocidade;
- responsividade;
- acessibilidade;
- consistência visual.

Os Dashboards deverão apresentar informações relevantes antes de funcionalidades secundárias.

---

# 5. Estado Atual da Plataforma

Durante a análise da base do projeto foram identificados os seguintes elementos estruturais:

- existência do `dashboard_base.html`;
- utilização do `dashboard-sidebar.js`;
- infraestrutura para persistência do estado da Sidebar;
- blocos específicos para expansão dos Dashboards;
- integração com os Layouts oficiais.

Esses elementos constituem a base da arquitetura atual dos Dashboards Premium.

---

# 6. Arquitetura Geral

Arquitetura conceitual:

```
Dashboard Base

↓

Navbar

↓

Breadcrumb

↓

Área Principal

↓

KPIs

↓

Cards

↓

Widgets

↓

Tabelas

↓

Footer
```

Cada camada possui responsabilidade específica.

---

# 7. Dashboard Base

O arquivo estrutural identificado é:

```
dashboard_base.html
```

Este Layout atua como base para todos os Dashboards Premium da plataforma.

Responsabilidades:

- estrutura visual;
- integração com Sidebar;
- carregamento de scripts;
- carregamento de estilos;
- definição dos blocos de expansão;
- inicialização da infraestrutura comum.

Todo novo Dashboard deverá herdar desse layout, quando aplicável.

---

# 8. Estrutura Oficial

Organização recomendada:

```
Dashboard

├── Cabeçalho

├── Breadcrumb

├── Barra de ações

├── KPIs

├── Cards

├── Widgets

├── Listagens

├── Gráficos

└── Rodapé
```

Nem todos os dashboards utilizarão todos os elementos, mas a estrutura deverá permanecer consistente.

---

# 9. Componentes do Dashboard

Os Dashboards poderão ser compostos pelos seguintes elementos reutilizáveis:

- KPIs;
- Cards;
- Gráficos;
- Widgets;
- Tabelas;
- Listagens;
- Alertas;
- Ações rápidas;
- Filtros;
- Modais;
- Breadcrumbs.

Todos esses componentes deverão seguir o Design System oficial.

---

# 10. Sidebar Premium

A Sidebar constitui um dos principais elementos da experiência de navegação.

Durante a análise foi identificado o script:

```
dashboard-sidebar.js
```

Esse script é responsável por:

- abrir Sidebar;
- fechar Sidebar;
- alternar largura;
- persistir estado no Local Storage;
- restaurar estado ao carregar a página.

A Sidebar deverá permanecer consistente em todos os Dashboards.

---

# 11. Breadcrumbs

Os Breadcrumbs fornecem contexto de navegação ao usuário.

Estrutura recomendada:

```
Início

↓

Módulo

↓

Tela Atual
```

Os Breadcrumbs deverão ser definidos através dos blocos disponibilizados pelo Layout Base.

---

# 12. KPIs

Os KPIs representam indicadores resumidos do módulo.

Exemplos:

- Total de membros;
- Congregações;
- Visitantes;
- Receitas;
- Despesas;
- Eventos;
- Alunos;
- Patrimônio.

Características:

- leitura rápida;
- destaque visual;
- atualização simples;
- possibilidade de atualização parcial com HTMX.

---

# 13. Cards

Os Cards representam blocos reutilizáveis de informação.

Exemplos:

- aniversariantes;
- últimos cadastros;
- próximos eventos;
- contas pendentes;
- tarefas.

Cada Card deverá possuir responsabilidade única.

---

# 14. Widgets

Widgets representam componentes mais ricos.

Exemplos:

- gráficos;
- calendários;
- mapas;
- agendas;
- listas inteligentes;
- indicadores.

Cada Widget deverá funcionar independentemente dos demais.

---

# 15. Integração com Layouts

Os Dashboards deverão integrar-se aos Layouts oficiais do GereIgreja.

Especialmente:

- `base_com_menu.html`;
- `dashboard_base.html`.

A estrutura global da aplicação deverá permanecer consistente em todos os módulos.

---

# 16. Integração com HTMX

HTMX será utilizado para atualização parcial de:

- KPIs;
- tabelas;
- widgets;
- notificações;
- cards;
- indicadores.

Sempre evitando recarregamentos completos da página.

---

# 17. Integração com Alpine.js

Alpine.js deverá controlar apenas estados locais.

Exemplos:

- abrir filtros;
- recolher painéis;
- alternar widgets;
- expandir cards.

---

# 18. Integração com JavaScript

JavaScript compartilhado permanecerá responsável por:

- Sidebar;
- gráficos;
- bibliotecas externas;
- Local Storage;
- componentes complexos.

---

# 19. Responsividade

Todos os Dashboards deverão funcionar adequadamente em:

- Desktop;
- Notebook;
- Tablet;
- Smartphone.

A organização dos componentes deverá adaptar-se automaticamente ao espaço disponível.

---

# 20. Roadmap

Curto prazo:

- consolidação da arquitetura.

Médio prazo:

- padronização de todos os módulos.

Longo prazo:

- dashboards analíticos;
- widgets inteligentes;
- integração com PWA;
- novos componentes reutilizáveis.

---

# 21. Documentos Relacionados

- GFE-01 — Frontend Architecture
- GFE-03 — Componentes
- GFE-04 — Layouts
- GFE-05 — Templates
- GFE-06 — Assets
- GFE-07 — CSS
- GFE-08 — JavaScript
- GFE-09 — HTMX
- GFE-10 — Alpine.js
- GereIgreja Design System (GDS)

---

# 22. Arquitetura da Sidebar Premium

A Sidebar Premium constitui um dos elementos centrais da experiência de navegação da Área de Gestão do GereIgreja.

Sua arquitetura foi projetada para oferecer:

- navegação consistente;
- persistência de preferências do usuário;
- adaptação responsiva;
- baixo acoplamento;
- reutilização entre todos os Dashboards.

A Sidebar deverá permanecer uniforme em todos os módulos que utilizem a infraestrutura de Dashboards.

---

# 23. Infraestrutura da Sidebar

Durante a análise do projeto foi identificado o arquivo:

```
static/js/dashboard-sidebar.js
```

Esse script representa a implementação oficial da infraestrutura da Sidebar.

Responsabilidades identificadas:

- inicialização automática;
- abertura;
- fechamento;
- alternância de largura;
- persistência do estado;
- restauração automática;
- integração com o Layout Base.

Novas funcionalidades relacionadas à Sidebar deverão evoluir preferencialmente neste arquivo, evitando implementações paralelas.

---

# 24. Fluxo de Inicialização

Fluxo arquitetural recomendado:

```
Usuário

↓

Dashboard

↓

dashboard_base.html

↓

DashboardSidebar.init()

↓

Leitura do Local Storage

↓

Aplicação do estado

↓

Renderização final
```

Essa sequência garante que a interface seja apresentada já no estado preferido pelo usuário.

---

# 25. Estados da Sidebar

A Sidebar poderá assumir os seguintes estados funcionais.

## Expandida

Modo padrão de navegação.

Características:

- menu completo;
- ícones;
- descrições;
- melhor legibilidade.

---

## Recolhida

Modo compacto.

Características:

- maior área útil;
- foco no conteúdo;
- navegação por ícones.

---

## Responsiva

Em dispositivos menores a Sidebar poderá assumir comportamento temporário, sendo aberta apenas quando solicitada.

---

# 26. Persistência

A arquitetura utiliza Local Storage para preservar preferências do usuário.

Durante a análise foram identificadas chaves relacionadas à Sidebar, incluindo:

```
dashboard.sidebar_visible
```

e chaves específicas definidas pelos próprios Dashboards através dos blocos disponibilizados pelo Layout Base.

Essa estratégia permite que diferentes dashboards mantenham estados independentes quando necessário.

---

# 27. Dashboard Base

O arquivo identificado:

```
dashboard_base.html
```

constitui a infraestrutura principal dos Dashboards Premium.

Responsabilidades:

- Navbar;
- Sidebar;
- Breadcrumb;
- Área principal;
- Blocos de expansão;
- Scripts compartilhados;
- Estilos compartilhados;
- Inicialização da infraestrutura comum.

Todo novo Dashboard deverá reutilizar essa base, salvo justificativa arquitetural documentada.

---

# 28. Blocos Oficiais

Durante a análise foram identificados blocos específicos destinados à expansão dos Dashboards.

Entre eles:

```
dashboard_sidebar_key
```

```
dashboard_sidebar_init_key
```

```
dashboard_extra_js
```

Esses blocos permitem que cada módulo personalize seu comportamento sem modificar o Layout Base.

Essa estratégia reduz acoplamento e facilita manutenção.

---

# 29. Tipos Oficiais de Dashboard

A arquitetura admite diferentes categorias de Dashboard.

---

## Dashboard Operacional

Apresenta informações utilizadas diariamente.

Exemplos:

- Secretaria;
- Financeiro;
- Escola Bíblica.

---

## Dashboard Gerencial

Focado em indicadores.

Exemplos:

- crescimento;
- receitas;
- despesas;
- frequência.

---

## Dashboard Analítico

Voltado para análise histórica.

Exemplos:

- comparativos;
- tendências;
- estatísticas.

---

## Dashboard Executivo

Consolida informações estratégicas para liderança.

Exemplos:

- indicadores gerais;
- visão ministerial;
- crescimento global.

---

# 30. Arquitetura dos Widgets

Cada Widget deverá possuir responsabilidade única.

Exemplos:

```
Agenda
```

```
Calendário
```

```
Receitas
```

```
Despesas
```

```
Aniversariantes
```

```
Visitantes
```

```
Próximos Eventos
```

```
Alertas
```

Os Widgets deverão ser independentes entre si.

Sempre que possível deverão permitir atualização parcial utilizando HTMX.

---

# 31. Atualização Parcial

A atualização parcial deverá ocorrer apenas sobre o Widget afetado.

Fluxo recomendado:

```
Widget

↓

HTMX

↓

View Django

↓

Partial

↓

Atualização do Widget
```

Evitar atualização do Dashboard completo.

---

# 32. Evidências Arquiteturais

Este documento foi elaborado considerando a implementação atual do GereIgreja.

---

## EA-DASH-001

Layout Base identificado.

```
dashboard_base.html
```

Representa a infraestrutura oficial dos Dashboards Premium.

---

## EA-DASH-002

Infraestrutura JavaScript.

Arquivo identificado.

```
dashboard-sidebar.js
```

Responsável pelo gerenciamento da Sidebar.

---

## EA-DASH-003

Persistência.

Utilização de Local Storage para armazenamento das preferências da Sidebar.

---

## EA-DASH-004

Blocos de expansão.

Foram identificados blocos específicos destinados à configuração dos Dashboards.

---

## EA-DASH-005

Integração.

Os Dashboards encontram-se totalmente compatíveis com:

- Django Templates;
- Bootstrap;
- HTMX;
- Alpine.js;
- JavaScript compartilhado.

---

# 33. Inventário Oficial

## Layouts

- dashboard_base.html

---

## Scripts

- dashboard-sidebar.js

---

## Componentes

- Sidebar
- Breadcrumb
- KPIs
- Cards
- Widgets
- Tabelas
- Alertas

---

## Tecnologias

- Django Templates
- Bootstrap
- JavaScript ES6
- HTMX (adoção gradual)
- Alpine.js (adoção gradual)

---

# 34. Especificações Oficiais

As especificações abaixo estabelecem os requisitos obrigatórios para todos os Dashboards do GereIgreja.

---

## GFE-DASH-001

Todo Dashboard deverá reutilizar a infraestrutura oficial definida pelo projeto.

---

## GFE-DASH-002

Sempre que aplicável, os Dashboards deverão herdar de:

```
dashboard_base.html
```

ou da infraestrutura equivalente definida pela arquitetura oficial.

---

## GFE-DASH-003

Nenhum Dashboard deverá implementar sua própria Sidebar.

Toda navegação lateral deverá reutilizar a infraestrutura compartilhada.

---

## GFE-DASH-004

O gerenciamento da Sidebar deverá permanecer centralizado no arquivo:

```
dashboard-sidebar.js
```

---

## GFE-DASH-005

A estrutura visual deverá preservar a seguinte ordem:

```
Navbar

↓

Breadcrumb

↓

Barra de ações

↓

KPIs

↓

Widgets

↓

Cards

↓

Listagens

↓

Rodapé
```

---

## GFE-DASH-006

Todo KPI deverá representar apenas um indicador.

Evitar múltiplas métricas dentro do mesmo Card.

---

## GFE-DASH-007

Widgets deverão possuir responsabilidade única.

---

## GFE-DASH-008

Cards deverão ser reutilizáveis entre diferentes módulos sempre que possível.

---

## GFE-DASH-009

Toda atualização parcial deverá utilizar HTMX quando houver benefício claro.

---

## GFE-DASH-010

Estados locais da interface deverão utilizar Alpine.js quando apropriado.

---

## GFE-DASH-011

Scripts compartilhados deverão permanecer independentes dos módulos.

---

## GFE-DASH-012

Todo Dashboard deverá permanecer totalmente responsivo.

---

## GFE-DASH-013

Todos os componentes deverão respeitar o Design System.

---

## GFE-DASH-014

Evitar duplicação de Widgets.

---

## GFE-DASH-015

Os Dashboards deverão priorizar leitura rápida.

---

## GFE-DASH-016

Sempre utilizar nomenclatura consistente para KPIs e Widgets.

---

## GFE-DASH-017

Cada Dashboard deverá possuir objetivo claramente definido.

---

## GFE-DASH-018

Novos componentes deverão ser documentados antes de serem reutilizados.

---

## GFE-DASH-019

Toda evolução deverá preservar compatibilidade com a arquitetura existente.

---

## GFE-DASH-020

Os Dashboards deverão permanecer compatíveis com futuras evoluções do GereIgreja, incluindo PWA e aplicações móveis.

---

# 35. Boas Práticas

Durante o desenvolvimento recomenda-se:

- reutilizar Layouts oficiais;
- reutilizar KPIs;
- reutilizar Cards;
- reutilizar Widgets;
- utilizar HTMX apenas onde houver ganho real;
- utilizar Alpine.js apenas para estados locais;
- manter JavaScript compartilhado desacoplado;
- preservar desempenho;
- preservar acessibilidade;
- preservar responsividade;
- manter consistência visual;
- documentar novos componentes.

---

# 36. Anti-patterns

Os padrões abaixo não fazem parte da arquitetura oficial.

---

## 36.1 Dashboard Monolítico

Evitar um único Dashboard contendo dezenas de responsabilidades.

---

## 36.2 Widgets Dependentes

Widgets não deverão depender diretamente uns dos outros.

---

## 36.3 Sidebar Duplicada

Nunca criar uma nova implementação da Sidebar.

---

## 36.4 KPIs Excessivos

Evitar excesso de indicadores na primeira tela.

Priorizar informações realmente relevantes.

---

## 36.5 Recarregamento Completo

Sempre que possível atualizar apenas:

- Widget;
- KPI;
- Card;
- Tabela.

---

## 36.6 JavaScript Específico Duplicado

Evitar criar scripts exclusivos quando já existir infraestrutura compartilhada.

---

## 36.7 Componentes Não Documentados

Todo novo componente reutilizável deverá ser incorporado à documentação oficial.

---

# 37. Checklist

Antes de criar um novo Dashboard verificar:

## Arquitetura

- [ ] Utiliza a infraestrutura oficial?
- [ ] Reutiliza o Dashboard Base?
- [ ] Reutiliza a Sidebar?

---

## Componentes

- [ ] KPIs reutilizáveis?
- [ ] Widgets reutilizáveis?
- [ ] Cards reutilizáveis?

---

## Interface

- [ ] Responsivo?
- [ ] Compatível com Bootstrap?
- [ ] Compatível com o Design System?

---

## Integração

- [ ] Compatível com HTMX?
- [ ] Compatível com Alpine.js?
- [ ] Compatível com JavaScript compartilhado?

---

## Documentação

- [ ] Segue os documentos GFE?
- [ ] Componentes documentados?
- [ ] Padrões preservados?

---

# 38. Glossário

## Dashboard

Interface principal de acompanhamento operacional ou estratégico.

---

## KPI

Key Performance Indicator.

Indicador resumido utilizado para apresentar informações críticas.

---

## Widget

Componente independente responsável por apresentar determinado conjunto de informações.

---

## Card

Bloco visual reutilizável contendo uma informação específica.

---

## Sidebar Premium

Estrutura lateral compartilhada responsável pela navegação dos Dashboards.

---

## Dashboard Base

Layout estrutural responsável por fornecer a infraestrutura comum dos Dashboards Premium.

---

## Progressive Dashboard

Conceito adotado pelo GereIgreja em que cada Dashboard evolui de forma incremental, reutilizando componentes existentes e preservando compatibilidade arquitetural.

---

# 39. Governança da Arquitetura dos Dashboards

A evolução dos Dashboards deverá obedecer aos seguintes princípios:

- reutilização antes de criação;
- simplicidade antes de complexidade;
- padronização antes de personalização;
- documentação antes de expansão;
- baixo acoplamento entre componentes;
- compatibilidade com os Layouts oficiais;
- compatibilidade com o Design System;
- compatibilidade com HTMX, Alpine.js e JavaScript compartilhado.

Toda nova convenção deverá ser registrada na documentação oficial antes de ser adotada em novos módulos.

---

# 40. Roadmap de Evolução

## Curto Prazo

- Padronização completa dos Dashboards existentes;
- Consolidação dos componentes compartilhados;
- Ampliação da documentação.

---

## Médio Prazo

- Biblioteca oficial de Widgets;
- Biblioteca oficial de KPIs;
- Biblioteca oficial de Cards;
- Atualizações parciais com HTMX.

---

## Longo Prazo

- Dashboards analíticos avançados;
- Indicadores inteligentes;
- Personalização por perfil de usuário;
- Temas visuais;
- Integração completa com Progressive Web App (PWA);
- Base preparada para aplicações móveis.

Toda evolução deverá preservar compatibilidade com a arquitetura estabelecida neste documento.

---

# 41. Documentos Relacionados

## GereIgreja Frontend Engineering

- README.md
- GFE-01 — Frontend Architecture
- GFE-02 — Estrutura de Pastas
- GFE-03 — Componentes
- GFE-04 — Layouts
- GFE-05 — Templates
- GFE-06 — Assets
- GFE-07 — CSS
- GFE-08 — JavaScript
- GFE-09 — HTMX
- GFE-10 — Alpine.js

---

## Documentação Corporativa

- GereIgreja Design System (GDS)
- GereIgreja Documentation Framework (GDF)
- GereIgreja Quality Framework (GQF)

---

# Conclusão

Os Dashboards constituem a principal interface operacional da Área de Gestão do GereIgreja.

Sua arquitetura foi projetada para oferecer uma experiência consistente, modular e escalável, baseada na reutilização de Layouts, Componentes, Widgets, KPIs e infraestrutura compartilhada.

A combinação entre Django Templates, Bootstrap, HTMX, Alpine.js e JavaScript compartilhado estabelece uma plataforma moderna, preparada para crescimento contínuo, mantendo a simplicidade arquitetural e a facilidade de manutenção.

Toda implementação futura deverá seguir os padrões definidos neste documento, garantindo uniformidade visual, desempenho, reutilização e alinhamento com o Design System oficial do GereIgreja.

---

# Status do Documento

**Pasta**

```
docs/frontend/
```

**Arquivo**

```
11-Dashboards.md
```

**Código**

```
GFE-DASH
```

**Versão**

```
2.0
```

**Status**

```
OFICIAL
```

---

**Fim do Documento**

