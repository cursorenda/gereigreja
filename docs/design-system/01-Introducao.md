Pasta:
docs/design-system/

Arquivo:
01-Introducao.md

Documento:
GDS-01

Código:
GDS-INTRO

Framework:
GereIgreja Design System (GDS)

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Agosto de 2026

# GDS-01 — Introdução ao GereIgreja Design System

> *"Um Design System não é apenas uma coleção de componentes visuais. É a tradução da identidade do produto em padrões reutilizáveis que garantem consistência, qualidade e evolução sustentável da plataforma."*

---

# Sumário

1. Objetivo
2. O que é o GereIgreja Design System
3. Missão
4. Visão
5. Escopo
6. Filosofia do Design
7. Identidade da Plataforma
8. Arquitetura do Design System
9. Atomic Design Adaptado ao GereIgreja
10. Design Tokens
11. Relação com Bootstrap
12. Relação com Django Templates
13. Relação com HTMX
14. Relação com Alpine.js
15. Relação com o Frontend Engineering
16. Casos Reais do GereIgreja
17. Roadmap

---

# 1. Objetivo

Este documento estabelece oficialmente os fundamentos do GereIgreja Design System (GDS).

Seu propósito é definir os princípios que orientam toda a construção visual da plataforma, garantindo consistência, reutilização, acessibilidade e evolução contínua.

Este documento serve como base para todos os demais documentos do Design System.

---

# 2. O que é o GereIgreja Design System

O GereIgreja Design System é o conjunto oficial de padrões visuais, componentes, diretrizes e convenções utilizados na construção da interface da plataforma.

Seu objetivo é assegurar que todas as telas apresentem comportamento uniforme, identidade visual consistente e excelente experiência para os usuários.

O Design System não define regras de negócio.

Sua responsabilidade limita-se à camada visual e à experiência de uso.

---

# 3. Missão

Fornecer uma linguagem visual consistente para toda a plataforma GereIgreja.

Isso permite que:

- novos módulos mantenham a identidade da plataforma;
- componentes sejam reutilizados;
- desenvolvedores trabalhem de forma padronizada;
- a manutenção seja simplificada;
- a experiência do usuário permaneça uniforme.

---

# 4. Visão

Construir uma plataforma cuja identidade visual seja reconhecida imediatamente por qualquer usuário, independentemente do módulo acessado.

A experiência deverá transmitir:

- organização;
- confiança;
- clareza;
- simplicidade;
- profissionalismo.

---

# 5. Escopo

O Design System aplica-se a toda a interface visual do GereIgreja.

Inclui:

- Área de Gestão do GereIgreja;
- Landing Pages;
- Portal Público;
- Blog;
- Dashboards;
- Componentes compartilhados;
- Formulários;
- Cards;
- Tabelas;
- Modais;
- Alertas;
- Navegação.

Não inclui:

- Backend;
- Banco de Dados;
- APIs;
- Administração Técnica (Django Admin), exceto customizações visuais específicas.

---

# 6. Filosofia do Design

Todo componente criado para o GereIgreja deverá respeitar cinco princípios fundamentais.

## 6.1 Clareza

O usuário deve compreender rapidamente cada tela.

A interface nunca deverá competir com o conteúdo.

---

## 6.2 Simplicidade

Sempre preferir soluções simples.

Evitar excesso de elementos visuais.

---

## 6.3 Consistência

Elementos semelhantes deverão possuir aparência e comportamento semelhantes.

Botões iguais deverão funcionar da mesma maneira.

Cards iguais deverão possuir o mesmo padrão visual.

Menus deverão manter comportamento uniforme.

---

## 6.4 Reutilização

Antes de criar um novo componente deverá ser verificado se já existe componente semelhante.

Sempre reutilizar antes de criar.

---

## 6.5 Escalabilidade

O Design System foi projetado para acompanhar o crescimento do GereIgreja.

Novos módulos deverão integrar-se naturalmente aos padrões existentes.

---

# 7. Identidade da Plataforma

O GereIgreja é um sistema de gestão ministerial.

Sua identidade visual deve transmitir:

- organização administrativa;
- confiabilidade;
- modernidade;
- leveza;
- produtividade;
- facilidade de utilização.

A identidade visual não deverá ser excessivamente carregada de elementos religiosos.

O foco principal é oferecer uma ferramenta profissional para gestão de igrejas, mantendo um visual elegante, limpo e acolhedor.

---

# 8. Arquitetura do Design System

O Design System organiza os elementos da interface em diferentes níveis.

```
Princípios

↓

Design Tokens

↓

Componentes

↓

Padrões

↓

Layouts

↓

Dashboards

↓

Páginas

↓

Experiência do Usuário
```

Cada camada possui responsabilidade própria.

Essa separação reduz acoplamento e facilita evolução.

---

# 9. Atomic Design Adaptado ao GereIgreja

O GereIgreja adota os conceitos do Atomic Design, adaptados à arquitetura baseada em Django Templates.

A estrutura conceitual é composta por:

```
Tokens

↓

Elementos HTML

↓

Componentes

↓

Partials

↓

Layouts

↓

Dashboards

↓

Páginas
```

Na implementação atual, os componentes reutilizáveis são organizados principalmente por meio de:

- Includes;
- Partials globais;
- Partials específicas dos módulos;
- Layouts compartilhados.

Não existe atualmente uma pasta global `components/`.

Esse modelo encontra-se alinhado com a arquitetura documentada no GFE.

---

# 10. Design Tokens

Os Design Tokens representam os elementos fundamentais da identidade visual.

Incluem:

- cores;
- tipografia;
- espaçamentos;
- bordas;
- sombras;
- ícones;
- tamanhos;
- raios de borda;
- estados dos componentes.

Os Tokens serão definidos detalhadamente nos documentos específicos do GDS.

---

# 11. Relação com Bootstrap

O Bootstrap constitui atualmente a base da interface do GereIgreja.

O Design System não substitui o Bootstrap.

Seu papel é padronizar como o Bootstrap deverá ser utilizado dentro da plataforma.

Isso inclui:

- padronização de botões;
- formulários;
- grids;
- tabelas;
- responsividade;
- componentes reutilizados.

---

# 12. Relação com Django Templates

Toda a interface do GereIgreja é construída prioritariamente utilizando Django Templates.

O Design System define a aparência.

Os Templates definem a estrutura.

Essa separação facilita manutenção e reutilização.

---

# 13. Relação com HTMX

O HTMX constitui a tecnologia oficial para atualizações parciais da interface.

Seu uso deverá preservar completamente os padrões definidos pelo Design System.

Componentes atualizados dinamicamente deverão manter a mesma identidade visual da renderização inicial.

---

# 14. Relação com Alpine.js

O Alpine.js é utilizado para estados locais da interface.

O Design System define como esses estados devem ser apresentados visualmente.

Exemplos:

- dropdowns;
- accordions;
- abas;
- modais;
- painéis expansíveis.

---

# 15. Relação com o Frontend Engineering

O GereIgreja Frontend Engineering (GFE) define a arquitetura técnica da interface.

O Design System define a linguagem visual.

Ambos os frameworks são complementares.

Enquanto o GFE orienta a implementação, o GDS orienta a aparência e a experiência do usuário.

---

# 16. Casos Reais do GereIgreja

O Design System foi concebido considerando a arquitetura e os módulos existentes do GereIgreja.

Os componentes documentados neste framework deverão atender, entre outros, aos seguintes contextos da plataforma.

---

## Área de Gestão

A Área de Gestão concentra as funcionalidades utilizadas pelos usuários autenticados.

Exemplos de módulos:

- Dashboard Principal;
- Secretaria;
- Tesouraria / Financeiro;
- Eventos;
- Comunicação;
- Escola Bíblica;
- Patrimônio;
- Relatórios;
- Assinaturas;
- Configurações.

Todos esses módulos deverão compartilhar a mesma linguagem visual.

---

## Portal Público

O Portal Público representa a interface institucional do GereIgreja.

Exemplos:

- Página Inicial;
- Funcionalidades;
- Planos;
- Blog;
- Contato;
- Política de Privacidade;
- Termos de Uso.

Embora possua objetivos diferentes da Área de Gestão, deverá preservar a identidade visual oficial da plataforma.

---

## Dashboards

Os Dashboards representam a principal interface operacional do sistema.

Exemplos de informações apresentadas:

- Total de Membros;
- Congregações;
- Visitantes;
- Receitas;
- Despesas;
- Eventos Próximos;
- Aniversariantes;
- Turmas da Escola Bíblica;
- Indicadores Financeiros;
- Comunicados.

Os componentes utilizados nesses painéis deverão seguir integralmente o Design System.

---

## Formulários

O GereIgreja possui grande quantidade de formulários administrativos.

Exemplos:

- Cadastro de Membros;
- Cadastro de Congregações;
- Cadastro de Pastores;
- Cadastro de Eventos;
- Cadastro de Patrimônio;
- Registro de Receitas;
- Registro de Despesas;
- Comunicação Interna.

Todos deverão utilizar padrões visuais consistentes.

---

## Relatórios

Relatórios deverão utilizar a mesma identidade visual da plataforma.

Exemplos:

- Relatório Financeiro;
- Lista de Membros;
- Lista de Visitantes;
- Relatório de Eventos;
- Relatório Patrimonial;
- Frequência da Escola Bíblica.

---

# 17. Consistência Visual

Independentemente do módulo acessado, o usuário deverá perceber que continua utilizando o GereIgreja.

Essa consistência deverá ser preservada por meio de:

- cores;
- tipografia;
- espaçamentos;
- botões;
- formulários;
- tabelas;
- ícones;
- componentes;
- layouts;
- dashboards.

A experiência visual deve permanecer uniforme durante toda a navegação.

---

# 18. Experiência do Usuário

A experiência do usuário deverá priorizar:

## Facilidade

Interfaces intuitivas.

---

## Rapidez

Menor quantidade possível de cliques.

---

## Legibilidade

Informações organizadas e fáceis de localizar.

---

## Previsibilidade

Comportamentos semelhantes para elementos semelhantes.

---

## Continuidade

Mudanças de contexto não deverão causar ruptura visual.

---

# 19. Evidências Arquiteturais

As diretrizes deste documento foram elaboradas considerando a arquitetura atual do GereIgreja.

---

## EA-GDS-001

A Área de Gestão utiliza layouts compartilhados documentados no Frontend Engineering.

---

## EA-GDS-002

O projeto utiliza predominantemente Django Templates como tecnologia de renderização.

---

## EA-GDS-003

Os componentes reutilizáveis são organizados principalmente através de Includes e Partials.

Não existe atualmente uma pasta global `components/`.

---

## EA-GDS-004

Os recursos estáticos encontram-se centralizados em `static/`, havendo também assets específicos em alguns módulos quando necessário.

---

## EA-GDS-005

Bootstrap constitui a base atual da interface da plataforma.

---

## EA-GDS-006

Font Awesome é utilizado como biblioteca principal de iconografia.

---

## EA-GDS-007

A arquitetura visual dos Dashboards encontra-se baseada na infraestrutura documentada em `dashboard_base.html` e `dashboard-sidebar.js`.

---

## EA-GDS-008

A Área Pública e a Área de Gestão compartilham a identidade visual da plataforma, embora utilizem layouts distintos.

---

# 20. Especificações Oficiais

As especificações abaixo estabelecem os requisitos obrigatórios para todos os componentes do GereIgreja.

---

## GDS-001

Todo componente deverá respeitar a identidade visual oficial da plataforma.

---

## GDS-002

Todo componente deverá ser reutilizável.

---

## GDS-003

Novos componentes deverão ser documentados antes de serem utilizados em múltiplos módulos.

---

## GDS-004

Toda evolução deverá preservar compatibilidade visual.

---

## GDS-005

Elementos semelhantes deverão possuir comportamento semelhante.

---

## GDS-006

A experiência deverá permanecer consistente entre Área Pública e Área de Gestão.

---

## GDS-007

O Design System deverá permanecer independente das regras de negócio.

---

## GDS-008

Toda implementação deverá respeitar o Frontend Engineering (GFE).

---

## GDS-009

A documentação do Design System será considerada a referência oficial para decisões relacionadas à interface.

---

## GDS-010

Mudanças significativas na identidade visual deverão ser registradas previamente na documentação.

---

# 21. Roadmap

## Curto Prazo

- Consolidação dos componentes reutilizáveis;
- Padronização visual dos módulos existentes;
- Documentação das cores oficiais.

---

## Médio Prazo

- Biblioteca completa de componentes;
- Catálogo visual;
- Tokens documentados;
- Expansão dos padrões de acessibilidade.

---

## Longo Prazo

- Dark Mode;
- White Label;
- Temas ministeriais;
- Biblioteca de componentes móveis;
- Evolução para aplicações PWA.

---
# 22. Boas Práticas

Todo desenvolvimento da interface do GereIgreja deverá seguir os princípios estabelecidos neste documento.

Recomenda-se:

- reutilizar componentes existentes;
- preservar a identidade visual oficial;
- manter consistência entre módulos;
- utilizar nomenclatura padronizada;
- documentar novos componentes antes da reutilização;
- respeitar o Frontend Engineering (GFE);
- preservar acessibilidade;
- manter responsividade;
- utilizar Design Tokens oficiais;
- evitar personalizações desnecessárias.

O Design System deve ser considerado a fonte oficial para todas as decisões relacionadas à interface.

---

# 23. Anti-patterns

Os padrões abaixo não fazem parte da arquitetura oficial do GereIgreja.

---

## 23.1 Componentes Duplicados

Evitar criar um novo componente quando já existir outro com a mesma finalidade.

Sempre reutilizar antes de criar.

---

## 23.2 Inconsistência Visual

Não alterar:

- cores;
- espaçamentos;
- tipografia;
- bordas;
- sombras;
- tamanhos;
- estados dos componentes

sem atualização prévia do Design System.

---

## 23.3 Personalização por Módulo

Cada módulo não deverá criar sua própria identidade visual.

Exemplo:

- Secretaria;
- Financeiro;
- Escola Bíblica;
- Patrimônio;
- Comunicação;
- Eventos.

Todos deverão compartilhar a mesma linguagem visual.

---

## 23.4 Componentes Sem Documentação

Todo componente reutilizável deverá ser documentado antes de ser utilizado por múltiplos módulos.

---

## 23.5 Mistura de Responsabilidades

O Design System não deverá conter:

- regras de negócio;
- consultas ao banco de dados;
- decisões de Backend.

Sua responsabilidade limita-se à camada visual.

---

## 23.6 Quebra da Consistência

Evitar comportamentos diferentes para elementos visualmente idênticos.

Botões iguais deverão agir da mesma forma.

Cards semelhantes deverão possuir aparência semelhante.

---

# 24. Checklist

Antes de criar um novo componente verificar:

## Identidade Visual

- [ ] segue o Design System?
- [ ] mantém consistência visual?
- [ ] utiliza Design Tokens oficiais?

---

## Reutilização

- [ ] já existe componente semelhante?
- [ ] poderá ser reutilizado?
- [ ] está desacoplado?

---

## Arquitetura

- [ ] compatível com Django Templates?
- [ ] compatível com Bootstrap?
- [ ] compatível com HTMX?
- [ ] compatível com Alpine.js?

---

## Experiência

- [ ] interface intuitiva?
- [ ] acessível?
- [ ] responsiva?
- [ ] consistente?

---

## Documentação

- [ ] documentado?
- [ ] referenciado?
- [ ] compatível com o GFE?

---

# 25. Glossário

## Design System

Conjunto oficial de padrões visuais, componentes e diretrizes de interface utilizados pelo GereIgreja.

---

## Design Token

Elemento fundamental da identidade visual.

Exemplos:

- cor;
- tipografia;
- espaçamento;
- sombra;
- raio de borda.

---

## Componente

Elemento reutilizável utilizado na construção da interface.

Exemplos:

- botão;
- card;
- formulário;
- tabela;
- alerta;
- modal.

---

## Layout

Estrutura responsável pela organização da página.

Os Layouts são documentados no GereIgreja Frontend Engineering.

---

## Dashboard

Interface principal da Área de Gestão responsável por apresentar indicadores, ações rápidas e informações estratégicas.

---

## Consistência

Princípio segundo o qual elementos semelhantes devem possuir aparência e comportamento semelhantes.

---

## Reutilização

Capacidade de utilizar um mesmo componente em diferentes módulos sem duplicação de código.

---

## Progressive Enhancement

Estratégia adotada pelo GereIgreja para evolução gradual da interface, preservando a renderização pelo servidor e adicionando recursos interativos quando necessário.

---

# 26. Governança do Design System

O GereIgreja Design System deverá evoluir continuamente, preservando estabilidade e compatibilidade.

Toda alteração deverá seguir os princípios abaixo.

---

## Documentação Antes da Implementação

Mudanças estruturais deverão ser documentadas antes de serem adotadas.

---

## Reutilização Antes da Criação

Sempre avaliar a reutilização de componentes existentes.

---

## Consistência Antes da Personalização

A identidade visual da plataforma possui prioridade sobre preferências individuais de implementação.

---

## Compatibilidade

Toda evolução deverá permanecer compatível com:

- GereIgreja Frontend Engineering (GFE);
- Bootstrap;
- Django Templates;
- HTMX;
- Alpine.js.

---

## Evolução Controlada

Novos componentes deverão ser incorporados de forma incremental, preservando estabilidade da plataforma.

---

# 27. Roadmap Arquitetural

## Curto Prazo

- documentação completa dos componentes;
- consolidação dos Design Tokens;
- padronização visual dos módulos existentes.

---

## Médio Prazo

- catálogo visual oficial;
- biblioteca de componentes reutilizáveis;
- ampliação dos padrões de acessibilidade;
- refinamento dos dashboards.

---

## Longo Prazo

- Dark Mode;
- múltiplos temas;
- White Label;
- Design System para aplicativos móveis;
- sincronização com Progressive Web App (PWA).

---

# 28. Documentos Relacionados

## GereIgreja Design System

- README.md
- GDS-02 — Princípios de Design
- GDS-03 — Cores
- GDS-04 — Tipografia
- GDS-05 — Espaçamento
- GDS-06 — Grid
- GDS-07 — Iconografia
- GDS-08 — Botões
- GDS-09 — Formulários
- GDS-10 — Cards
- GDS-11 — Tabelas
- GDS-12 — Alertas
- GDS-13 — Modais
- GDS-14 — Navegação
- GDS-15 — Dashboards
- GDS-16 — Acessibilidade
- GDS-17 — Animações
- GDS-18 — Boas Práticas
- GDS-19 — Governança

---

## GereIgreja Frontend Engineering

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
- GFE-11 — Dashboards

---

# Conclusão

O GereIgreja Design System representa a base oficial da identidade visual da plataforma.

Mais do que um conjunto de componentes, ele estabelece uma linguagem comum para toda a aplicação, promovendo consistência, reutilização e evolução sustentável.

A combinação entre o Design System e o Frontend Engineering permite que novos módulos sejam desenvolvidos de forma previsível, mantendo a experiência do usuário uniforme em toda a Área de Gestão e no Portal Público.

Toda implementação futura deverá seguir as diretrizes estabelecidas neste documento, preservando a identidade visual, a qualidade da interface e a arquitetura oficial do GereIgreja.

---

# Status do Documento

**Pasta**

```
docs/design-system/
```

**Arquivo**

```
01-Introducao.md
```

**Documento**

```
GDS-01
```

**Código**

```
GDS-INTRO
```

**Versão**

```
1.0
```

**Status**

```
OFICIAL
```

---

**Fim do Documento**
