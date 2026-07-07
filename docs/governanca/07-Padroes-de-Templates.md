# 07 - Padrões de Templates

> "A interface do GereIgreja deve transmitir organização antes mesmo do usuário utilizar suas funcionalidades."

---

# Sumário

1. Objetivo
2. Filosofia dos Templates
3. Organização dos Templates
4. Estrutura dos Arquivos
5. Templates Base
6. Componentização
7. Integração com o GDS
8. Organização do HTML
9. Formulários
10. Tabelas
11. Componentes Reutilizáveis
12. JavaScript
13. CSS
14. Acessibilidade
15. Performance
16. Checklist
17. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para desenvolvimento dos Templates do GereIgreja.

Seu objetivo é garantir consistência visual, reutilização de componentes, facilidade de manutenção e alinhamento com o GereIgreja Design System (GDS).

Todos os Templates da plataforma deverão seguir estas diretrizes.

---

# 2. Filosofia dos Templates

Os Templates representam a camada de apresentação da plataforma.

Sua responsabilidade é exibir informações ao usuário de forma clara, organizada e acessível.

Os Templates não deverão conter regras de negócio.

Toda lógica deverá permanecer em Views, Services ou Context Processors.

O HTML deverá permanecer limpo, simples e fácil de compreender.

---

# 3. Organização dos Templates

Cada módulo deverá possuir seus próprios Templates.

Exemplo:

```text
templates/
├── dashboard/
├── financeiro/
├── membros/
├── eventos/
├── blog/
└── usuarios/
```

A organização deverá refletir a estrutura funcional da plataforma.

Nunca concentrar Templates de módulos diferentes em uma única pasta.

---

# 4. Estrutura dos Arquivos

Os Templates deverão seguir uma organização consistente.

Exemplo:

```text
templates/
├── base.html
├── base_com_menu.html
├── base_publico.html
├── dashboard/
├── financeiro/
├── membros/
├── eventos/
├── blog/
├── componentes/
├── emails/
└── errors/
```

Essa estrutura facilita localização e manutenção.

---

# 5. Templates Base

Toda página deverá herdar um Template base.

Preferencialmente:

- `base.html`
- `base_com_menu.html`
- `base_publico.html`

Evitar duplicação de cabeçalhos, menus, rodapés e scripts.

---

# 6. Componentização

Sempre que possível utilizar componentes reutilizáveis.

Exemplos:

- Cards
- Tabelas
- Alertas
- Paginação
- Breadcrumbs
- Menus
- Modais
- Botões
- Badges
- Dropdowns

Nenhum componente visual deverá ser duplicado desnecessariamente.

---

# 7. Integração com o GDS

Todos os Templates deverão seguir integralmente o GereIgreja Design System (GDS).

O GDS define oficialmente:

- paleta de cores;
- tipografia;
- espaçamentos;
- componentes;
- botões;
- formulários;
- tabelas;
- identidade visual.

Nenhum Template deverá criar estilos próprios que contrariem o GDS.

---

# 8. Organização do HTML

O HTML deverá permanecer limpo.

Boas práticas:

- indentação consistente;
- blocos bem definidos;
- comentários apenas quando realmente necessários;
- evitar estruturas excessivamente profundas;
- utilizar nomes descritivos.

Legibilidade deverá ser prioridade.

---

# 9. Formulários

Todos os formulários deverão seguir o padrão visual da plataforma.

Utilizar:

- labels consistentes;
- mensagens de erro claras;
- ajuda contextual;
- componentes reutilizáveis.

A experiência do usuário deverá permanecer uniforme.

---

# 10. Tabelas

Todas as tabelas deverão seguir um padrão único.

Sempre considerar:

- paginação;
- ordenação;
- filtros;
- responsividade;
- estados vazios;
- carregamento eficiente.

As tabelas representam um dos principais componentes administrativos da plataforma.

---

# 11. Componentes Reutilizáveis

Sempre utilizar `include` para componentes compartilhados.

Exemplos:

```django
{% include "componentes/card.html" %}
{% include "componentes/modal.html" %}
{% include "componentes/paginacao.html" %}
{% include "componentes/alerta.html" %}
```

Isso reduz duplicação e facilita manutenção.

---

# 12. JavaScript

Scripts específicos deverão permanecer em arquivos próprios.

Evitar JavaScript inline.

Sempre que possível:

- organizar por módulo;
- reutilizar funções;
- documentar comportamentos complexos.

O JavaScript deverá complementar a interface, nunca dificultá-la.

---

# 13. CSS

Todo CSS deverá utilizar os tokens definidos pelo GDS.

Evitar:

- cores hardcoded;
- estilos inline;
- duplicação de regras;
- sobrescritas desnecessárias.

A identidade visual deverá permanecer consistente.

---

# 14. Acessibilidade

Toda interface deverá considerar:

- contraste adequado;
- navegação por teclado;
- textos alternativos;
- foco visível;
- hierarquia correta de títulos.

A acessibilidade faz parte da qualidade da plataforma.

---

# 15. Performance

Os Templates deverão priorizar carregamento rápido.

Boas práticas:

- reutilização de componentes;
- carregamento otimizado de recursos;
- redução de HTML duplicado;
- minimização de consultas desnecessárias.

Interfaces leves proporcionam melhor experiência ao usuário.

---

# 16. Checklist

Antes da publicação verificar:

- utiliza Template Base;
- segue o GDS;
- componentes reutilizados;
- HTML organizado;
- CSS padronizado;
- JavaScript externo;
- acessibilidade revisada;
- responsividade validada.

---

# 17. Princípios Finais

Os Templates representam a identidade visual do GereIgreja.

Toda interface deverá transmitir organização, clareza, profissionalismo e confiança.

A consistência visual fortalece a experiência do usuário e reduz a complexidade de manutenção da plataforma.

Cada nova tela deverá parecer uma continuação natural das demais, preservando a identidade definida pelo GereIgreja Design System (GDS).