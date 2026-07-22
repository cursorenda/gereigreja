Pasta:
docs/frontend/

Arquivo:
04-Layouts.md

Documento:
GFE-04

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

# 04 - Layouts

> *"Layouts bem definidos proporcionam consistência visual, facilitam a navegação e reduzem a complexidade da interface."*

---

# Sumário

1. Objetivo
2. Filosofia dos Layouts
3. Papel dos Layouts
4. Estrutura Geral
5. Layouts Oficiais
6. Estrutura Base
7. Responsabilidades
8. Reutilização
9. Documentos Relacionados
10. Princípios Finais

---

# 1. Objetivo

Este documento define a arquitetura oficial dos layouts utilizados no Frontend do GereIgreja.

Seu objetivo é padronizar a estrutura visual da plataforma, promovendo consistência, reutilização e facilidade de manutenção.

Todos os módulos deverão utilizar os layouts oficiais definidos neste documento.

---

# 2. Filosofia dos Layouts

Os layouts representam a estrutura principal da interface.

Eles devem fornecer uma base comum para todas as páginas do sistema, evitando duplicação de código e garantindo uma experiência uniforme ao usuário.

Cada layout deverá possuir responsabilidade claramente definida.

---

# 3. Papel dos Layouts

Os layouts possuem as seguintes responsabilidades:

- definir a estrutura visual da página;
- organizar áreas comuns da interface;
- centralizar elementos compartilhados;
- manter identidade visual consistente;
- facilitar a reutilização.

Os layouts não deverão conter regras de negócio.

---

# 4. Estrutura Geral

Hierarquia recomendada:

```text
Base

↓

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

Cada camada possui responsabilidade própria.

---

# 5. Layouts Oficiais do GereIgreja

Atualmente, o GereIgreja utiliza os seguintes layouts principais:

- base.html
- base_com_menu.html
- base_auth.html
- base_publico.html
- base_relatorio.html (quando existente)
- base_impressao.html (quando existente)

Cada layout possui uma finalidade específica e deverá ser reutilizado por todos os módulos compatíveis.

Novos layouts somente poderão ser criados mediante necessidade arquitetural devidamente justificada.

# 6. Estrutura Base

O layout administrativo oficial é o arquivo:

base_com_menu.html

Ele centraliza:

- Navbar superior
- Sidebar lateral
- Breadcrumb
- Mensagens
- Área principal
- Footer
- Scripts globais
- CSS compartilhado

Todos os módulos administrativos deverão herdar deste layout.

# 7. Responsabilidades

Cada layout deverá definir apenas:

- estrutura da página;
- posicionamento dos elementos;
- áreas de conteúdo;
- regiões reutilizáveis.

Componentes específicos deverão permanecer fora dos layouts.

---

# 8. Reutilização

Sempre que um novo módulo for criado, deverá reutilizar um layout existente.

A criação de novos layouts somente será permitida quando houver necessidade arquitetural claramente justificada.

---

# 9. Documentos Relacionados

- GFE-01 — Frontend Architecture
- GFE-02 — Estrutura de Pastas
- GFE-03 — Componentes
- GDS — GereIgreja Design System

---

# 10. Princípios Finais

Os layouts representam a base estrutural do Frontend do GereIgreja.

Sua padronização garante consistência visual, reduz retrabalho e facilita a evolução contínua da interface.

---

## ✅ Parte 1 concluída

---

# 11. Herança de Templates

O GereIgreja adota oficialmente a herança de templates do Django.

Toda página deverá herdar de um layout base.

Exemplo:

```django
{% extends "layouts/base.html" %}
```

Essa abordagem reduz duplicação de código e facilita alterações globais na interface.

---

# 12. Blocos de Conteúdo

Os layouts deverão utilizar blocos (`{% block %}`) padronizados.

Estrutura recomendada:

```django
{% block title %}{% endblock %}

{% block extra_css %}{% endblock %}

{% block breadcrumbs %}{% endblock %}

{% block content %}{% endblock %}

{% block modals %}{% endblock %}

{% block extra_js %}{% endblock %}
```

Novos blocos somente deverão ser criados quando realmente necessários.

---

# 13. Layout Administrativo

O layout administrativo será utilizado pela maior parte do sistema.

Elementos obrigatórios:

- Navbar;
- Sidebar;
- Breadcrumb;
- Área principal;
- Mensagens do sistema;
- Footer.

Esse layout será a base para módulos como:

- Membros;
- Secretaria;
- Financeiro;
- Eventos;
- Comunicação;
- Escola Bíblica;
- Relatórios.

---

# 14. Layout de Autenticação

As páginas de autenticação deverão utilizar um layout próprio.

Exemplos:

- Login;
- Recuperação de senha;
- Alteração de senha;
- Primeiro acesso.

Esse layout deverá ser minimalista, focando na ação principal da página.

---

# 15. Layout Público

As páginas públicas deverão utilizar estrutura independente da área administrativa.

Exemplos:

- Página inicial;
- Planos;
- Funcionalidades;
- Blog;
- Contato;
- Política de Privacidade;
- Termos de Uso.

A navegação pública deverá ser simples e objetiva.

---

# 16. Layout de Relatórios

Relatórios exigem organização específica para facilitar leitura e impressão.

Características:

- cabeçalho institucional;
- filtros utilizados;
- data de geração;
- paginação;
- rodapé com informações do sistema.

A apresentação deve priorizar clareza dos dados.

---

# 17. Layout para Impressão

Documentos destinados à impressão deverão utilizar um layout dedicado.

Exemplos:

- fichas cadastrais;
- certificados;
- listas de presença;
- relatórios financeiros;
- atas;
- declarações.

Elementos de navegação deverão ser ocultados durante a impressão.

---

# 18. Responsividade

Todos os layouts deverão adaptar-se automaticamente às diferentes resoluções.

Prioridades:

- Desktop;
- Notebook;
- Tablet;
- Smartphone.

A experiência do usuário deverá permanecer consistente em qualquer dispositivo.

---

# 19. Integração com HTMX

Os layouts deverão suportar atualizações parciais da interface.

Exemplos:

- atualização de tabelas;
- filtros;
- modais;
- notificações;
- dashboards.

Sempre que possível, evitar recarregamentos completos da página.

---

# 20. Integração com Alpine.js

Comportamentos leves da interface poderão utilizar Alpine.js.

Exemplos:

- abrir menus;
- controlar dropdowns;
- alternar abas;
- expandir painéis;
- controlar modais.

Toda lógica de negócio continuará sendo responsabilidade do Backend.

---

# 21. Boas Práticas

Sempre:

- utilizar herança de templates;
- reutilizar layouts existentes;
- manter blocos padronizados;
- evitar HTML duplicado;
- utilizar partials para regiões compartilhadas;
- preservar consistência visual;
- manter compatibilidade com o Design System.

---

# 22. Anti-patterns

Evitar:

- duplicação de layouts;
- páginas independentes sem necessidade;
- múltiplos layouts para o mesmo contexto;
- CSS específico dentro dos layouts;
- JavaScript embutido;
- lógica de negócio nos templates;
- blocos excessivos ou redundantes.

Esses padrões aumentam a complexidade da manutenção.

---

# 23. Checklist

Antes de criar um novo layout verificar:

- existe layout semelhante?
- utiliza herança de templates?
- blocos padronizados?
- responsividade validada?
- compatível com o Design System?
- componentes reutilizados?
- documentação atualizada?

---

# 24. Evolução Futura

A arquitetura de layouts foi projetada para suportar:

- múltiplos temas;
- white-label;
- Progressive Web App (PWA);
- aplicativos móveis;
- novos módulos administrativos;
- novos portais públicos.

A evolução deverá preservar compatibilidade entre os layouts existentes.

---

# 25. Documentos Relacionados

- GFE-01 — Frontend Architecture
- GFE-02 — Estrutura de Pastas
- GFE-03 — Componentes
- GFE-05 — Templates
- GDS — GereIgreja Design System
- GXS — GereIgreja Experience System

---

# 26. Princípios Finais

Os layouts constituem a estrutura permanente da interface do GereIgreja.

Sua padronização garante uniformidade visual, facilita a evolução da plataforma e reduz significativamente o custo de manutenção.

Todo novo módulo deverá utilizar os layouts oficiais definidos neste documento, preservando a identidade visual e a experiência consistente para todos os usuários.

---

## ✅ Status

**Pasta:** `docs/frontend/`

**Arquivo:** `04-Layouts.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento estabelece a arquitetura oficial dos layouts do Frontend do GereIgreja e define os padrões para construção das páginas da plataforma.

