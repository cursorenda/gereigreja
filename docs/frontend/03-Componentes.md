Pasta:
docs/frontend/

Arquivo:
03-Componentes.md

Documento:
GFE-03

Framework:
GereIgreja Frontend Engineering (GFE)

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# 03 - Componentes

> *"Interfaces consistentes são construídas a partir de componentes reutilizáveis, independentes e previsíveis."*

---

# Sumário

1. Objetivo
2. Filosofia dos Componentes
3. O Papel dos Componentes
4. Arquitetura de Componentes
5. Classificação dos Componentes
6. Estrutura Oficial
7. Organização dos Arquivos
8. Reutilização
9. Documentos Relacionados
10. Princípios Finais

---

# 1. Objetivo

Este documento define o padrão oficial para criação, organização e utilização de componentes no Frontend do GereIgreja.

Seu objetivo é garantir consistência visual, reutilização, facilidade de manutenção e evolução contínua da interface.

Todo componente desenvolvido deverá seguir estas diretrizes.

---

# 2. Filosofia dos Componentes

O Frontend do GereIgreja será construído utilizando componentes reutilizáveis.

Cada componente deverá possuir:

- responsabilidade única;
- interface previsível;
- baixo acoplamento;
- alta reutilização;
- fácil manutenção;
- comportamento consistente.

Sempre que uma interface puder ser reutilizada em dois ou mais locais, deverá ser transformada em componente.

---

# 3. O Papel dos Componentes

Os componentes representam os blocos fundamentais da interface.

Eles possuem quatro responsabilidades principais:

- apresentar informações;
- receber interações do usuário;
- manter consistência visual;
- reduzir duplicação de código.

Os componentes não deverão conter regras de negócio.

---

# 4. Arquitetura de Componentes

Fluxo simplificado:

```text
Layout

↓

Página

↓

Seções

↓

Componentes

↓

Elementos HTML
```

Quanto menor e mais especializado for o componente, maior será seu potencial de reutilização.

---

# 5. Classificação dos Componentes

Os componentes poderão ser classificados em:

## Componentes Básicos

São elementos fundamentais da interface.

Exemplos:

- Botão;
- Input;
- Select;
- Checkbox;
- Badge;
- Alert;
- Card.

---

## Componentes Compostos

São formados pela combinação de componentes básicos.

Exemplos:

- Tabela;
- Modal;
- Formulário;
- Breadcrumb;
- Paginação;
- Timeline.

---

## Componentes de Layout

São responsáveis pela organização visual.

Exemplos:

- Sidebar;
- Navbar;
- Footer;
- Header;
- Painéis;
- Grid.

---

## Componentes de Domínio

Representam funcionalidades específicas do GereIgreja.

Exemplos:

- Cartão de Membro;
- Cartão Financeiro;
- Cartão de Evento;
- Indicadores da Dashboard;
- Agenda Ministerial;
- Lista de Congregações.

Esses componentes normalmente não são reutilizados fora do domínio correspondente.

---

# 6. Estrutura Oficial

Estrutura sugerida:

```text
components/

base/

layout/

forms/

tables/

navigation/

feedback/

dashboard/

membros/

financeiro/

eventos/

comunicacao/
```

Cada diretório deverá possuir responsabilidade claramente definida.

---

# 7. Organização dos Arquivos

Cada componente deverá possuir arquivos próprios quando sua complexidade justificar.

Exemplo:

```text
card_membro/

card_membro.html

card_membro.css

card_membro.js
```

Ou, quando apropriado:

```text
components/

card_membro.html
```

A escolha deverá considerar simplicidade e facilidade de manutenção.

---

# 8. Reutilização

Antes de criar um novo componente verificar:

- já existe componente semelhante?
- é possível estender um componente existente?
- vale criar uma variação?
- haverá reutilização futura?

Duplicação deverá ser evitada sempre que possível.

---

# 9. Documentos Relacionados

- GFE-01 — Frontend Architecture
- GFE-02 — Estrutura de Pastas
- GDS — GereIgreja Design System
- GBE-20 — Code Standards

---

# 10. Princípios Finais

Componentes representam a base do Frontend do GereIgreja.

Sua correta organização reduz custos de manutenção, aumenta a produtividade da equipe e garante uma experiência consistente para os usuários.

---

## ✅ Parte 1 concluída

---

# 11. Ciclo de Vida dos Componentes

Todo componente deverá possuir um ciclo de vida previsível.

Fluxo recomendado:

```text
Criação

↓

Configuração

↓

Renderização

↓

Interação do Usuário

↓

Atualização

↓

Destruição (quando aplicável)
```

O comportamento do componente deverá ser consistente em todas as telas da aplicação.

---

# 12. Configuração e Parâmetros

Os componentes deverão receber informações por meio de parâmetros claramente definidos.

Exemplos:

- título;
- subtítulo;
- ícone;
- cor;
- tamanho;
- estado;
- permissões;
- ações disponíveis.

Os componentes nunca deverão depender de variáveis globais quando puderem receber seus dados explicitamente.

---

# 13. Estados Visuais

Sempre que aplicável, um componente deverá possuir estados padronizados.

Exemplos:

- padrão;
- hover;
- foco;
- ativo;
- desabilitado;
- carregando;
- vazio;
- erro;
- sucesso.

Todos os estados deverão manter consistência visual em toda a plataforma.

---

# 14. Composição de Componentes

Componentes complexos deverão ser compostos por componentes menores.

Exemplo:

```text
Modal

↓

Header

↓

Body

↓

Footer

↓

Botões
```

A composição facilita reutilização e reduz duplicação de código.

---

# 15. Componentes Assíncronos

Quando houver atualização parcial da interface, deverão ser utilizados mecanismos assíncronos.

Exemplos:

- carregamento de tabelas;
- filtros;
- paginação;
- modais;
- dashboards;
- notificações.

Sempre que possível, utilizar HTMX para reduzir complexidade de JavaScript personalizado.

---

# 16. Integração com Alpine.js

Quando for necessário comportamento reativo simples, utilizar Alpine.js.

Exemplos:

- abrir e fechar menus;
- controlar modais;
- abas;
- dropdowns;
- accordions;
- indicadores visuais.

Evitar lógica complexa no navegador.

A regra de negócio deverá permanecer no Backend.

---

# 17. Acessibilidade

Todo componente deverá seguir boas práticas de acessibilidade.

Requisitos mínimos:

- navegação por teclado;
- foco visível;
- contraste adequado;
- labels em formulários;
- uso de atributos ARIA quando necessário;
- estrutura HTML semântica.

Componentes inacessíveis não deverão ser aprovados.

---

# 18. Nomenclatura

Os nomes deverão refletir claramente sua finalidade.

Exemplos:

```text
card_membro.html

modal_confirmacao.html

tabela_financeiro.html

breadcrumb.html

botao_salvar.html
```

Evitar nomes genéricos como:

```text
item.html

box.html

novo.html

teste.html
```

---

# 19. Boas Práticas

Sempre:

- reutilizar componentes existentes;
- manter responsabilidade única;
- documentar componentes compartilhados;
- evitar dependências ocultas;
- manter consistência visual;
- reutilizar estilos;
- minimizar JavaScript personalizado.

---

# 20. Anti-patterns

Evitar:

- componentes gigantes;
- mistura de responsabilidades;
- duplicação de HTML;
- JavaScript embutido no template;
- estilos inline;
- dependência entre componentes sem necessidade;
- componentes específicos quando um componente genérico resolveria.

Esses padrões aumentam o débito técnico da aplicação.

---

# 21. Catálogo Oficial de Componentes

Os principais componentes reutilizáveis do GereIgreja incluem:

### Navegação

- Sidebar
- Navbar
- Breadcrumb
- Menu lateral
- Menu suspenso

### Formulários

- Campo de texto
- Select
- Checkbox
- Radio
- Switch
- DatePicker
- Campo monetário
- Upload

### Feedback

- Alertas
- Toasts
- Badges
- Spinner
- Skeleton Loading

### Dados

- Cards
- KPIs
- Tabelas
- Paginação
- Timeline
- Estatísticas
- Gráficos

### Interação

- Modal
- Confirmação
- Accordion
- Abas
- Dropdown
- Offcanvas

### Componentes do Domínio

- Card de Membro
- Card Financeiro
- Card de Evento
- Card de Congregação
- Card de Ministério
- Indicadores Pastorais
- Agenda Ministerial
- Calendário de Eventos

Este catálogo deverá evoluir conforme a plataforma crescer.

---

# 22. Checklist

Antes de criar um novo componente verificar:

- já existe componente semelhante;
- responsabilidade única;
- reutilização possível;
- acessibilidade implementada;
- estados visuais completos;
- documentação atualizada;
- integração com Design System;
- nomenclatura correta.

---

# 23. Evolução Futura

A arquitetura de componentes foi projetada para suportar:

- novos módulos;
- novos temas;
- múltiplas marcas (white-label);
- Progressive Web App (PWA);
- aplicativos móveis;
- biblioteca oficial de componentes;
- Storybook ou ferramenta equivalente.

A evolução deverá preservar a compatibilidade dos componentes compartilhados.

---

# 24. Documentos Relacionados

- GFE-01 — Frontend Architecture
- GFE-02 — Estrutura de Pastas
- GFE-04 — Layouts
- GDS — GereIgreja Design System
- GXS — GereIgreja Experience System

---

# 25. Princípios Finais

Os componentes constituem a base do Frontend do GereIgreja.

Sua padronização garante consistência visual, reduz retrabalho, facilita a manutenção e permite que a interface evolua de forma sustentável.

Todo componente deverá ser concebido para ser reutilizável, previsível e acessível, contribuindo para uma experiência de uso uniforme em toda a plataforma.

---

## ✅ Status

**Pasta:** `docs/frontend/`

**Arquivo:** `03-Componentes.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento estabelece o padrão oficial para criação, organização e evolução dos componentes do Frontend do GereIgreja.
