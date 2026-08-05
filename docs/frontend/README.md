---
Documento: GFE-README
Título: Frontend Engineering
Seção: Frontend
Versão: 1.0
Status: Oficial
Responsável: Equipe de Engenharia
Última atualização: Agosto de 2026
---

# Frontend Engineering (GFE)

> "O Frontend do GereIgreja é construído sobre princípios de modularização, reutilização e padronização, utilizando Django Templates como mecanismo de renderização e o GereIgreja Design System como base visual."

---

# Objetivo

Esta pasta reúne toda a documentação oficial da camada de Frontend do GereIgreja.

Seu objetivo é servir como referência para desenvolvedores, arquitetos e mantenedores da plataforma, documentando a arquitetura da interface, padrões de desenvolvimento, organização dos templates e boas práticas adotadas pelo projeto.

---

# Escopo

A documentação desta coleção abrange:

- Arquitetura do Frontend;
- Estrutura de diretórios;
- Layouts;
- Templates;
- Assets;
- Componentes;
- Dashboards;
- Responsividade;
- JavaScript;
- CSS;
- Padrões de interface;
- Boas práticas.

Não fazem parte desta coleção:

- Backend;
- Modelos;
- Services;
- Selectors;
- APIs;
- Banco de Dados.

Esses assuntos pertencem à coleção **GBE — GereIgreja Backend Engineering**.

---

# Organização da Documentação

Os documentos desta coleção seguem uma ordem progressiva.

Primeiro são apresentados os conceitos arquiteturais.

Depois são detalhados os componentes especializados do Frontend.

---

## Arquitetura

| Documento | Descrição |
|------------|-----------|
| 01 - Frontend Architecture | Visão geral da arquitetura do Frontend. |
| 02 - Estrutura de Pastas | Organização oficial dos diretórios do Frontend. |
| 03 - Componentes | Componentes reutilizáveis da interface. |
| 04 - Layouts | Hierarquia dos layouts e templates base. |

---

## Interface

| Documento | Descrição |
|------------|-----------|
| 05 - Templates | Organização dos templates Django. |
| 06 - Assets | CSS, JavaScript, imagens e fontes. |
| 07 - CSS | Organização das folhas de estilo. |
| 08 - JavaScript | Estrutura dos scripts da aplicação. |
| 09 - HTMX | Diretrizes para utilização do HTMX. |
| 10 - Alpine | Diretrizes para utilização do Alpine.js. |

---

## Experiência do Usuário

| Documento | Descrição |
|------------|-----------|
| 11 - Dashboards | Estrutura dos dashboards. |
| 12 - Formulários | Padrões para formulários. |
| 13 - Tabelas | Estrutura das tabelas do sistema. |
| 14 - Modais | Padrões para janelas modais. |
| 15 - Responsividade | Adaptação para diferentes dispositivos. |
| 16 - Acessibilidade | Diretrizes de acessibilidade. |

---

## Engenharia

| Documento | Descrição |
|------------|-----------|
| 17 - Performance | Otimizações de Frontend. |
| 18 - Boas Práticas | Convenções oficiais do projeto. |
| 19 - Checklist | Checklist para revisão de telas. |
| 20 - Roadmap | Evolução planejada da arquitetura Frontend. |

---

# Tecnologias Utilizadas

O Frontend do GereIgreja utiliza oficialmente:

- Django Templates;
- HTML5;
- Bootstrap;
- CSS próprio;
- JavaScript puro;
- Font Awesome.

Além disso, o projeto estabelece como diretriz arquitetural a adoção gradual de:

- HTMX;
- Alpine.js.

No momento da elaboração desta documentação, essas tecnologias encontram-se em processo de adoção e ainda não estão presentes de forma ampla na base de código.

---

# Organização dos Templates

O GereIgreja utiliza uma arquitetura baseada em herança de templates.

De forma simplificada:

```text
Administração Técnica

admin/base_site.html
        │
        ▼
admin/index.html


Área de Gestão

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

Essa separação é uma decisão arquitetural oficial da plataforma.

---

# Convenções Gerais

A documentação do Frontend segue as seguintes convenções:

- nomenclatura padronizada;
- diretórios organizados por responsabilidade;
- reutilização por meio de Layouts, Includes e Partials;
- separação entre infraestrutura e regras de negócio;
- utilização do GereIgreja Design System.

---

# Relação com Outras Coleções

Esta documentação complementa:

- Backend Engineering (GBE);
- GereIgreja Design System (GDS);
- GereIgreja Quality Framework (GQF);
- GereIgreja Documentation Framework (GDF);
- GereIgreja Security Framework (GSF).

---

# Evolução da Documentação

Esta coleção é considerada documentação viva.

Novos documentos poderão ser adicionados conforme a evolução da arquitetura do GereIgreja.

Alterações estruturais deverão ser refletidas nesta documentação para manter a consistência entre o código-fonte e a especificação oficial da plataforma.

