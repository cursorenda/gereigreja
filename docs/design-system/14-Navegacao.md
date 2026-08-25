Pasta:
`docs/design-system/`

Arquivo:
`14-Navegacao.md`

Documento:
GDS-14

Código:
GDS-NAV

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

# GDS-14 — Navegação

> "A navegação do GereIgreja deve permitir que o usuário compreenda onde está, para onde pode ir e como retornar, sem precisar reaprender a interface a cada módulo."

---

# Sumário

1. Objetivo
2. Escopo
3. Contextos de Navegação do GereIgreja
4. Princípios
5. Arquitetura Geral
6. Área de Gestão do GereIgreja
7. Administração Técnica
8. Área Pública
9. Navegação Principal
10. Sidebar
11. Menu da Área de Gestão
12. Grupos de Menu
13. Itens de Menu
14. Ícones do Menu
15. Estados dos Itens
16. Item Ativo
17. Hover
18. Focus
19. Disabled
20. Submenus
21. Expansão e Recolhimento
22. Controle da Sidebar
23. Persistência da Sidebar
24. Dashboard Sidebar
25. Anti-FOUC
26. Navbar Superior
27. Breadcrumb
28. Padrão Oficial do Breadcrumb
29. Breadcrumb em Dashboards
30. Título da Página
31. Relação entre Título e Navegação
32. Ações Próximas ao Título
33. Navegação entre Módulos
34. Navegação dentro do Módulo
35. Navegação Contextual
36. Abas
37. Paginação
38. Links
39. Links Externos
40. Ações versus Navegação
41. Botões que Navegam
42. Voltar
43. Home
44. Navegação da Secretaria
45. Navegação Financeira
46. Navegação de Eventos
47. Navegação da Escola Bíblica
48. Navegação de Comunicação
49. Navegação de Patrimônio
50. Navegação de Relatórios
51. Navegação de Assinaturas
52. Navegação de Configurações
53. Navegação por Permissão
54. Navegação Multi-Tenant
55. Congregação Atual
56. Segurança
57. URLs
58. Django URL Names
59. Navegação e Templates
60. `base.html`
61. `base_com_menu.html`
62. `menu.html`
63. `dashboard_base.html`
64. Includes e Partials
65. HTMX
66. Alpine.js
67. JavaScript
68. `dashboard-sidebar.js`
69. Font Awesome
70. Bootstrap
71. Responsividade
72. Desktop
73. Notebook
74. Tablet
75. Smartphone
76. Sidebar Mobile
77. Área de Toque
78. Acessibilidade
79. Navegação por Teclado
80. Foco
81. ARIA
82. Leitores de Tela
83. Contraste
84. Estados Vazios
85. Acesso Negado
86. Página Não Encontrada
87. Preservação de Contexto
88. Filtros e Navegação
89. Paginação e Navegação
90. Histórico do Navegador
91. Deep Links
92. Anti-Patterns
93. Regras de Implementação
94. Evidências Arquiteturais
95. Especificações Oficiais
96. Checklist
97. Governança
98. Roadmap
99. Documentos Relacionados
100. Princípios Finais
101. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial de navegação do GereIgreja.

Seu objetivo é garantir que todos os usuários consigam:

* localizar funcionalidades;
* compreender sua posição atual;
* alternar entre módulos;
* retornar a níveis anteriores;
* acessar ações frequentes;
* utilizar o sistema em diferentes dispositivos;
* navegar com teclado e tecnologias assistivas.

A navegação deverá permanecer consistente em toda a plataforma.

---

# 2. Escopo

Este documento aplica-se a:

* Área de Gestão do GereIgreja;
* Dashboards;
* páginas internas autenticadas;
* Portal Público;
* Landing Pages;
* breadcrumbs;
* sidebar;
* navbar;
* menus;
* submenus;
* abas;
* paginação;
* links;
* navegação responsiva.

A Administração Técnica baseada no Django Admin possui arquitetura própria e deverá ser tratada separadamente.

---

# 3. Contextos de Navegação do GereIgreja

O GereIgreja possui três contextos principais de navegação:

```text
GereIgreja
│
├── Área Pública
│
├── Área de Gestão do GereIgreja
│
└── Administração Técnica
    └── Django Admin
```

Esses contextos possuem finalidades diferentes e não deverão ser confundidos.

---

# 4. Princípios

A navegação deverá seguir:

* clareza;
* previsibilidade;
* consistência;
* hierarquia;
* acessibilidade;
* responsividade;
* baixo esforço cognitivo;
* segurança;
* preservação de contexto.

O usuário deverá sempre conseguir responder:

```text
Onde estou?

Como cheguei aqui?

Para onde posso ir?

Como retorno?
```

---

# 5. Arquitetura Geral

A navegação conceitual da Área de Gestão segue:

```text
base.html
   ↓
base_com_menu.html
   ↓
Página / Dashboard
   │
   ├── Navbar
   ├── Sidebar / Menu
   ├── Breadcrumb
   ├── Título
   └── Conteúdo
```

Dashboards Premium acrescentam uma camada própria:

```text
base.html
   ↓
base_com_menu.html
   ↓
dashboard_base.html
   ↓
Dashboard específico
```

---

# 6. Área de Gestão do GereIgreja

A Área de Gestão representa as páginas internas utilizadas pelos usuários da plataforma.

Exemplos:

* Secretaria;
* Financeiro;
* Eventos;
* Comunicação;
* Escola Bíblica;
* Patrimônio;
* Relatórios;
* Assinaturas;
* Configurações.

Sua navegação principal deverá utilizar a infraestrutura compartilhada da aplicação.

---

# 7. Administração Técnica

A Administração Técnica corresponde ao Django Admin.

Ela não deverá ser documentada como se utilizasse `base_com_menu.html`.

Sua hierarquia é independente e utiliza os templates do próprio Django Admin, incluindo customizações específicas quando existentes.

A navegação da Administração Técnica possui finalidade operacional para desenvolvimento, suporte e administração técnica da plataforma.

---

# 8. Área Pública

A Área Pública deverá possuir navegação independente da Área de Gestão.

Exemplos:

* Home;
* Funcionalidades;
* Planos;
* Blog;
* Contato;
* Termos de Uso;
* Política de Privacidade;
* Login.

A navegação pública deverá priorizar descoberta do produto e acesso às áreas institucionais.

---

# 9. Navegação Principal

Na Área de Gestão, o menu principal deverá concentrar os módulos e funcionalidades de maior relevância.

A navegação não deverá ser construída individualmente dentro de cada página.

Ela deverá permanecer centralizada na infraestrutura compartilhada.

---

# 10. Sidebar

A sidebar representa a principal estrutura de navegação lateral da Área de Gestão.

Ela deverá:

* agrupar módulos;
* apresentar ícones;
* destacar o contexto atual;
* permitir expansão quando necessário;
* adaptar-se ao viewport;
* respeitar permissões.

---

# 11. Menu da Área de Gestão

O projeto utiliza um template compartilhado de menu.

Arquivo identificado:

`menu.html`

Esse template concentra grande parte da navegação interna.

A manutenção dos itens principais deverá ocorrer preferencialmente nessa infraestrutura compartilhada, evitando menus paralelos por página.

---

# 12. Grupos de Menu

Os itens poderão ser organizados por contexto funcional.

Exemplo conceitual:

```text
Gestão
├── Dashboard
├── Secretaria
├── Financeiro
└── Eventos

Ministério
├── Escola Bíblica
├── Comunicação
└── Patrimônio

Sistema
├── Relatórios
├── Assinatura
└── Configurações
```

A organização real deverá seguir os módulos e permissões existentes no projeto.

---

# 13. Itens de Menu

Cada item deverá possuir:

```text
Ícone
+
Rótulo
+
Destino
+
Estado
+
Permissão, quando aplicável
```

O texto deverá ser curto e reconhecível.

---

# 14. Ícones do Menu

O menu atual do GereIgreja utiliza amplamente Font Awesome.

Exemplo estrutural:

```html
<i class="fas fa-home"></i>
```

ou equivalentes existentes no projeto.

A iconografia do menu deverá permanecer consistente com a biblioteca efetivamente carregada pela aplicação.

Não introduzir uma segunda biblioteca de ícones apenas para um novo módulo.

---

# 15. Estados dos Itens

Itens navegáveis deverão considerar:

```text
Default
Hover
Focus
Active
Disabled, quando aplicável
Expanded, quando possuir submenu
```

---

# 16. Item Ativo

O item correspondente à área atual deverá possuir destaque perceptível.

O destaque deverá informar onde o usuário está sem depender somente de cor.

---

# 17. Hover

Hover deverá oferecer feedback discreto em dispositivos que suportem cursor.

Não depender de hover para disponibilizar funcionalidade essencial.

---

# 18. Focus

Itens acessíveis por teclado deverão possuir foco visível.

Nunca remover o outline sem substituição equivalente.

---

# 19. Disabled

Um item não deverá ser exibido como desabilitado quando a regra correta for ocultá-lo por falta de permissão.

Estados desabilitados deverão ser usados somente quando o usuário possui contexto suficiente para compreender por que a funcionalidade está temporariamente indisponível.

---

# 20. Submenus

Submenus deverão representar hierarquia real.

Evitar profundidade excessiva.

Preferir:

```text
Módulo
   ↓
Funcionalidade
```

em vez de:

```text
Módulo
   ↓
Grupo
   ↓
Subgrupo
   ↓
Categoria
   ↓
Página
```

---

# 21. Expansão e Recolhimento

Submenus expansíveis deverão apresentar estado visual claro.

O usuário deverá identificar:

* fechado;
* aberto;
* item atual.

---

# 22. Controle da Sidebar

Páginas que utilizem sidebar deverão oferecer controle visível para mostrar ou ocultar o menu.

No padrão de dashboards, esse controle fica próximo ao título da página.

Exemplo identificado em `dashboard_base.html`:

```text
[☰ Ocultar menu] Título do Dashboard
```

Essa proximidade melhora a descoberta da funcionalidade.

---

# 23. Persistência da Sidebar

A preferência de visibilidade poderá ser preservada localmente.

A infraestrutura atual dos Dashboards Premium utiliza Local Storage para persistir o estado da sidebar.

Essa lógica deverá permanecer centralizada.

---

# 24. Dashboard Sidebar

Os dashboards utilizam:

`static/js/dashboard-sidebar.js`

Esse script é responsável pela infraestrutura compartilhada de sidebar dos Dashboards Premium.

Entre suas responsabilidades documentadas estão:

* abertura;
* fechamento;
* persistência;
* atualização do estado;
* integração com o layout.

---

# 25. Anti-FOUC

O `dashboard_base.html` possui lógica síncrona destinada a aplicar o estado de largura da interface antes do render visual.

O objetivo é evitar que o usuário veja rapidamente uma sidebar em um estado e logo depois em outro.

Esse comportamento faz parte da experiência de navegação dos Dashboards Premium e deverá ser preservado durante evoluções da infraestrutura.

---

# 26. Navbar Superior

A navbar deverá concentrar informações e ações globais.

Exemplos possíveis conforme o contexto da plataforma:

* identidade da aplicação;
* acesso ao perfil;
* ações globais;
* conta;
* navegação auxiliar.

A navbar não deverá duplicar desnecessariamente toda a sidebar.

---

# 27. Breadcrumb

O breadcrumb deverá informar a posição estrutural atual.

Ele é obrigatório nas páginas internas segundo o padrão já estabelecido no GDS.

---

# 28. Padrão Oficial do Breadcrumb

Formato:

```text
Home > Módulo > Página
```

Exemplos:

```text
Home > Secretaria > Membros
```

```text
Home > Financeiro > Lançamentos
```

```text
Home > Escola Bíblica > Turmas
```

---

# 29. Breadcrumb em Dashboards

O `dashboard_base.html` disponibiliza bloco específico:

```django
{% block dashboard_breadcrumb %}
{% endblock %}
```

Exemplo estrutural:

```django
<li>
    <a href="{% url 'home' %}">
        <i class="fas fa-home me-1"></i>
        Home
    </a>
</li>
<li>
    <span class="active">Meu Dashboard</span>
</li>
```

Cada dashboard deverá informar sua própria trilha sem modificar a infraestrutura base.

---

# 30. Título da Página

Cada página deverá possuir título principal claramente identificado.

O título deverá representar o conteúdo atual, e não apenas repetir o nome do sistema.

---

# 31. Relação entre Título e Navegação

Título e breadcrumb possuem funções diferentes.

```text
Breadcrumb
→ localização

Título
→ conteúdo atual
```

Exemplo:

```text
Home > Secretaria > Membros

Membros
```

---

# 32. Ações Próximas ao Título

Ações estruturais importantes poderão permanecer próximas ao título quando isso melhorar a descoberta.

Exemplo real dos dashboards:

```text
[☰ Ocultar menu] Dashboard Financeiro
```

Ações de negócio, como `Novo lançamento`, poderão permanecer na barra de ações ou região apropriada da página.

---

# 33. Navegação entre Módulos

Mudanças entre módulos principais deverão utilizar navegação convencional da aplicação.

Exemplo:

```text
Secretaria
   ↓
Financeiro
```

Não utilizar HTMX como padrão para substituir toda a página durante mudança de módulo.

---

# 34. Navegação dentro do Módulo

Dentro de um módulo, o usuário poderá acessar:

* dashboard;
* listagens;
* cadastros;
* relatórios;
* configurações específicas.

A arquitetura deverá manter nomes e destinos consistentes.

---

# 35. Navegação Contextual

A navegação contextual deverá permanecer próxima do conteúdo relacionado.

Exemplo:

```text
Membro
├── Dados
├── Histórico
└── Informações relacionadas
```

Não adicionar links globais dentro de componentes locais sem necessidade.

---

# 36. Abas

Abas poderão organizar diferentes visões da mesma entidade.

Exemplo:

```text
Dados Gerais | Histórico | Documentos
```

Abas não deverão representar módulos independentes.

Quando o destino constitui página funcional independente, utilizar navegação apropriada.

---

# 37. Paginação

Paginação é uma forma de navegação dentro de coleções.

Ela deverá preservar:

* filtros;
* busca;
* ordenação;
* contexto.

As regras específicas encontram-se no GDS-11.

---

# 38. Links

Links deverão representar navegação.

Se a interação executa uma operação, utilizar componente de ação apropriado.

---

# 39. Links Externos

Links que levam para fora do GereIgreja deverão ser identificáveis quando o comportamento puder surpreender o usuário.

Quando uma nova aba for utilizada, considerar comunicação e acessibilidade apropriadas.

---

# 40. Ações versus Navegação

Regra fundamental:

```text
Ir para outro lugar
→ Link

Executar uma ação
→ Button
```

Não utilizar link estilizado como botão para operações destrutivas sem necessidade semântica.

---

# 41. Botões que Navegam

Botões de Call to Action poderão levar a outra página em contextos como Landing Pages.

Sua implementação semântica deverá corresponder ao comportamento real.

---

# 42. Voltar

O botão `Voltar` deverá possuir destino previsível.

Evitar depender exclusivamente de `history.back()` em fluxos onde o usuário poderá chegar à página por diferentes caminhos.

Sempre que possível, utilizar um destino estrutural conhecido.

---

# 43. Home

`Home` representa a raiz da Área de Gestão nos breadcrumbs internos.

Não utilizar `Dashboard` e `Home` como sinônimos automaticamente quando representarem destinos diferentes.

---

# 44. Navegação da Secretaria

A Secretaria poderá direcionar para funcionalidades como:

* membros;
* visitantes;
* congregações;
* cadastros relacionados;
* relatórios da área.

A navegação deverá preservar a terminologia real utilizada no sistema.

---

# 45. Navegação Financeira

O Financeiro deverá organizar funcionalidades relacionadas à gestão financeira de maneira previsível.

Exemplos de contextos:

* dashboard;
* lançamentos;
* receitas;
* despesas;
* relatórios;
* configurações financeiras.

A exposição final dependerá das funcionalidades efetivamente disponíveis e das permissões.

---

# 46. Navegação de Eventos

O módulo de Eventos deverá permitir acesso claro a:

* eventos;
* cadastros;
* acompanhamento;
* funcionalidades relacionadas.

---

# 47. Navegação da Escola Bíblica

A navegação poderá organizar:

* turmas;
* alunos;
* professores;
* frequência;
* funcionalidades relacionadas.

---

# 48. Navegação de Comunicação

A navegação deverá distinguir claramente contextos como:

* comunicação;
* criação;
* acompanhamento;
* histórico;

quando existentes na implementação.

---

# 49. Navegação de Patrimônio

O módulo deverá utilizar a mesma infraestrutura geral da Área de Gestão, evitando uma interface de navegação própria.

---

# 50. Navegação de Relatórios

Relatórios deverão ser agrupados de forma que o usuário compreenda seu domínio.

Evitar uma única lista desorganizada de dezenas de relatórios.

---

# 51. Navegação de Assinaturas

Telas relacionadas a assinatura pertencem à Área de Gestão quando utilizadas pelo cliente autenticado.

Elas não deverão ser confundidas com Administração Técnica.

---

# 52. Navegação de Configurações

Configurações deverão ser agrupadas por responsabilidade.

Evitar criar um menu de configurações com itens sem relação aparente.

---

# 53. Navegação por Permissão

O menu deverá respeitar permissões.

Entretanto:

```text
Ocultar item
≠
Garantir segurança
```

O backend deverá continuar validando autorização.

---

# 54. Navegação Multi-Tenant

O usuário deverá visualizar somente destinos compatíveis com seu contexto organizacional e suas permissões.

A navegação não deverá permitir descoberta indevida de entidades pertencentes a outros contextos.

---

# 55. Congregação Atual

Quando uma operação depender da congregação ou escopo selecionado, esse contexto deverá permanecer compreensível.

A interface não deverá permitir que o usuário realize uma operação sem saber em qual contexto organizacional está atuando quando isso for relevante.

---

# 56. Segurança

URLs não protegidas não se tornam seguras apenas porque não aparecem no menu.

Toda View deverá aplicar as regras de acesso apropriadas.

---

# 57. URLs

URLs deverão possuir estrutura previsível.

Evitar alterações desnecessárias que prejudiquem:

* favoritos;
* deep links;
* histórico;
* documentação;
* testes.

---

# 58. Django URL Names

Templates deverão preferir URLs nomeadas.

Exemplo:

```django
{% url 'home' %}
```

Evitar hardcode de caminhos quando existir nome de URL apropriado.

---

# 59. Navegação e Templates

A infraestrutura compartilhada deverá continuar sendo fornecida pelos templates base e includes.

Cada página não deverá recriar:

* navbar;
* sidebar;
* menu;
* footer;
* navegação principal.

---

# 60. `base.html`

`base.html` constitui o tronco estrutural da hierarquia interna de templates.

Layouts especializados deverão reutilizá-lo indiretamente conforme a arquitetura existente.

---

# 61. `base_com_menu.html`

`base_com_menu.html` representa a principal base da Área de Gestão com navegação compartilhada.

É diferente da infraestrutura do Django Admin.

Essa distinção deverá permanecer explícita em toda documentação.

---

# 62. `menu.html`

`menu.html` concentra a navegação lateral compartilhada.

Mudanças estruturais nesse template possuem impacto amplo e deverão ser tratadas como alteração de infraestrutura.

---

# 63. `dashboard_base.html`

`dashboard_base.html` herda de:

```django
{% extends 'base_com_menu.html' %}
```

Ele acrescenta a infraestrutura visual específica dos Dashboards Premium.

Entre seus blocos estão:

```text
dashboard_title
dashboard_breadcrumb
dashboard_filters
dashboard_content
dashboard_css
dashboard_extra_js
```

Além das configurações relacionadas à sidebar.

---

# 64. Includes e Partials

Elementos reutilizáveis de navegação deverão seguir a arquitetura existente baseada em:

* includes;
* partials globais;
* partials específicas dos módulos.

Não existe necessidade atual de criar uma nova estrutura paralela apenas para navegação.

---

# 65. HTMX

HTMX deverá ser utilizado principalmente para atualizações parciais internas.

Não deverá ser adotado como mecanismo padrão de navegação entre módulos principais.

Exemplos apropriados:

* filtros;
* paginação;
* conteúdo de modal;
* atualização de componentes.

---

# 66. Alpine.js

Alpine.js poderá futuramente controlar estados locais de navegação leve.

Exemplos:

* submenu;
* dropdown;
* painel.

Sua adoção prática é gradual e não deverá ser documentada como infraestrutura já consolidada onde ainda não estiver implementada.

---

# 67. JavaScript

JavaScript nativo permanece responsável por infraestrutura compartilhada mais complexa.

Exemplo real:

`dashboard-sidebar.js`

---

# 68. `dashboard-sidebar.js`

O script deverá permanecer centralizado.

Dashboards individuais não deverão duplicar sua lógica.

A inicialização ocorre por meio de:

```javascript
DashboardSidebar.init(...)
```

com parâmetros fornecidos pelo `dashboard_base.html`.

---

# 69. Font Awesome

Font Awesome está consolidado no GereIgreja.

É carregado em bases da plataforma e utilizado amplamente no menu e em outras interfaces.

A navegação deverá reutilizar a biblioteca efetivamente adotada pelo projeto.

---

# 70. Bootstrap

Bootstrap fornece infraestrutura visual e responsiva importante para a navegação.

O GDS deverá determinar:

* identidade;
* espaçamento;
* hierarquia;
* estados;
* comportamento visual.

---

# 71. Responsividade

A navegação deverá adaptar-se a:

* desktop;
* notebook;
* tablet;
* smartphone.

Nenhum módulo deverá exigir desktop para acessar funcionalidades essenciais.

---

# 72. Desktop

Em desktop, a sidebar poderá permanecer visível conforme o estado escolhido pelo usuário.

O conteúdo deverá aproveitar o espaço disponível.

---

# 73. Notebook

A navegação deverá manter legibilidade sem reduzir excessivamente a área útil do conteúdo.

---

# 74. Tablet

A sidebar poderá assumir comportamento mais compacto ou temporário.

A prioridade deverá ser o conteúdo principal.

---

# 75. Smartphone

Em smartphone:

* menu deverá ser facilmente acessível;
* conteúdo deverá ocupar a largura disponível;
* navegação não deverá bloquear a leitura;
* áreas de toque deverão ser adequadas.

---

# 76. Sidebar Mobile

A sidebar em mobile deverá comportar-se como navegação temporária quando apropriado.

Ao abrir, deverá permanecer evidente como fechá-la.

---

# 77. Área de Toque

Itens interativos deverão possuir área suficiente para interação confortável.

Isso é especialmente importante em:

* menu;
* ícone hambúrguer;
* dropdowns;
* paginação;
* botão de fechar.

---

# 78. Acessibilidade

A navegação deverá ser utilizável sem mouse.

---

# 79. Navegação por Teclado

O usuário deverá conseguir acessar:

* menu;
* submenus;
* links;
* breadcrumb;
* controles;
* dropdowns.

A ordem de tabulação deverá ser lógica.

---

# 80. Foco

Todo elemento navegável deverá apresentar foco visível.

O foco deverá permanecer perceptível sobre fundos claros e institucionais.

---

# 81. ARIA

Componentes expansíveis deverão utilizar atributos apropriados quando necessário.

Exemplos:

```text
aria-expanded
aria-controls
aria-current
```

A implementação deverá corresponder ao estado real.

---

# 82. Leitores de Tela

Links e controles deverão possuir nomes compreensíveis fora do contexto visual.

Evitar:

```text
Clique aqui
Mais
Abrir
```

quando o destino puder ser nomeado de forma mais específica.

---

# 83. Contraste

Estados:

* ativo;
* hover;
* focus;
* disabled;

deverão preservar contraste adequado.

---

# 84. Estados Vazios

Quando um módulo não possuir dados, o estado vazio poderá fornecer navegação contextual.

Exemplo:

```text
Nenhum evento cadastrado.

[Adicionar evento]
```

---

# 85. Acesso Negado

Ao tentar acessar recurso sem autorização, o usuário deverá receber resposta apropriada sem exposição de informações indevidas.

A navegação deverá oferecer caminho seguro para continuar utilizando o sistema.

---

# 86. Página Não Encontrada

A página 404 deverá permitir recuperação.

Exemplo de destinos:

```text
Voltar para Home
```

ou outra navegação segura definida pela aplicação.

---

# 87. Preservação de Contexto

Ao navegar por listagens, o sistema deverá preservar contexto quando apropriado.

Exemplos:

* filtros;
* paginação;
* ordenação;
* busca.

---

# 88. Filtros e Navegação

Filtros não deverão desaparecer inesperadamente durante paginação ou atualização parcial.

---

# 89. Paginação e Navegação

A paginação deverá produzir URLs previsíveis quando aplicável.

O botão Voltar do navegador deverá continuar sendo útil.

---

# 90. Histórico do Navegador

Interações não deverão quebrar injustificadamente:

* voltar;
* avançar;
* refresh;
* abertura em nova aba.

---

# 91. Deep Links

Páginas importantes deverão poder ser acessadas diretamente por URL quando as permissões permitirem.

O usuário não deverá ser obrigado a percorrer o menu desde o início para alcançar um destino conhecido.

---

# 92. Anti-Patterns

Evitar:

* menus diferentes para páginas equivalentes;
* sidebar duplicada;
* múltiplas bibliotecas de ícones;
* breadcrumb ausente em página interna;
* menu sem indicação do item ativo;
* links para ações destrutivas;
* ações escondidas somente em hover;
* profundidade excessiva de submenu;
* URLs hardcoded sem necessidade;
* navegação HTMX entre módulos como padrão;
* menus construídos diretamente dentro das páginas;
* dependência exclusiva de cor;
* item visível sem permissão correspondente;
* uso do menu como mecanismo de segurança;
* comportamento diferente entre dashboards equivalentes;
* sidebar ocupando área excessiva em mobile.

---

# 93. Regras de Implementação

A navegação deverá seguir esta prioridade:

```text
Infraestrutura existente
        ↓
Reutilização
        ↓
Extensão controlada
        ↓
Novo padrão somente quando necessário
```

Antes de criar novo componente navegacional, verificar:

* `base_com_menu.html`;
* `menu.html`;
* `dashboard_base.html`;
* includes;
* partials;
* scripts compartilhados.

---

# 94. Evidências Arquiteturais

## EA-GDS-NAV-001

A Área de Gestão utiliza predominantemente `base_com_menu.html`.

## EA-GDS-NAV-002

`dashboard_base.html` herda de `base_com_menu.html`.

## EA-GDS-NAV-003

`menu.html` concentra a navegação lateral compartilhada.

## EA-GDS-NAV-004

O Django Admin utiliza sua própria árvore de templates e não deverá ser confundido com a Área de Gestão.

## EA-GDS-NAV-005

Dashboards Premium utilizam `dashboard-sidebar.js`.

## EA-GDS-NAV-006

O estado da sidebar dos dashboards utiliza Local Storage.

## EA-GDS-NAV-007

`dashboard_base.html` possui mecanismo anti-FOUC para o estado da sidebar.

## EA-GDS-NAV-008

O layout de dashboard disponibiliza bloco `dashboard_breadcrumb`.

## EA-GDS-NAV-009

Font Awesome é utilizado amplamente na navegação atual.

## EA-GDS-NAV-010

Bootstrap participa da infraestrutura responsiva da interface.

## EA-GDS-NAV-011

HTMX e Alpine.js constituem diretrizes de evolução, mas sua adoção prática permanece gradual.

## EA-GDS-NAV-012

Includes e partials são os mecanismos atuais predominantes para fragmentos reutilizáveis de template.

---

# 95. Especificações Oficiais

## GDS-NAV-001

Toda página interna deverá possuir localização navegacional compreensível.

## GDS-NAV-002

Páginas internas deverão utilizar breadcrumb quando pertencentes à hierarquia padrão da Área de Gestão.

## GDS-NAV-003

O padrão de breadcrumb será:

```text
Home > Módulo > Página
```

## GDS-NAV-004

A Área de Gestão deverá reutilizar a infraestrutura baseada em `base_com_menu.html`.

## GDS-NAV-005

Dashboards deverão reutilizar `dashboard_base.html` quando compatíveis com essa arquitetura.

## GDS-NAV-006

A sidebar não deverá ser recriada individualmente por módulo.

## GDS-NAV-007

A lógica compartilhada dos Dashboards Premium deverá permanecer centralizada em `dashboard-sidebar.js`.

## GDS-NAV-008

O item atual deverá possuir estado ativo perceptível.

## GDS-NAV-009

A navegação deverá funcionar por teclado.

## GDS-NAV-010

O foco deverá permanecer visível.

## GDS-NAV-011

A navegação deverá respeitar permissões.

## GDS-NAV-012

Permissões deverão ser validadas no backend.

## GDS-NAV-013

Itens de navegação não deverão ser utilizados como mecanismo de segurança.

## GDS-NAV-014

Font Awesome deverá ser reutilizado enquanto permanecer a biblioteca consolidada do projeto.

## GDS-NAV-015

Novas bibliotecas de ícones não deverão ser introduzidas sem decisão arquitetural.

## GDS-NAV-016

HTMX não deverá substituir a navegação principal entre módulos por padrão.

## GDS-NAV-017

Alpine.js deverá limitar-se a comportamento local quando adotado.

## GDS-NAV-018

URLs nomeadas do Django deverão ser preferidas a caminhos hardcoded.

## GDS-NAV-019

A navegação deverá preservar contexto de filtros e paginação quando apropriado.

## GDS-NAV-020

A navegação deverá ser responsiva.

## GDS-NAV-021

O controle de mostrar/ocultar sidebar deverá permanecer facilmente descobrível quando aplicável.

## GDS-NAV-022

A Administração Técnica deverá permanecer arquiteturalmente separada da Área de Gestão.

## GDS-NAV-023

A Área Pública deverá possuir navegação apropriada ao contexto institucional.

## GDS-NAV-024

Novos padrões de navegação deverão ser documentados antes da adoção ampla.

---

# 96. Checklist

## Estrutura

* [ ] utiliza layout oficial;
* [ ] não recria sidebar;
* [ ] não recria navbar;
* [ ] utiliza menu compartilhado;
* [ ] possui título claro;
* [ ] possui breadcrumb quando aplicável.

## Breadcrumb

* [ ] começa em Home;
* [ ] contém módulo;
* [ ] identifica página atual;
* [ ] utiliza URLs nomeadas;
* [ ] página atual não cria navegação ambígua.

## Sidebar

* [ ] item ativo visível;
* [ ] ícones consistentes;
* [ ] grupos coerentes;
* [ ] expansão previsível;
* [ ] controle mostrar/ocultar acessível;
* [ ] responsiva.

## Permissões

* [ ] itens respeitam permissões;
* [ ] backend valida acesso;
* [ ] nenhum dado externo ao contexto é revelado;
* [ ] menu não é tratado como segurança.

## Responsividade

* [ ] desktop;
* [ ] notebook;
* [ ] tablet;
* [ ] smartphone;
* [ ] sidebar mobile funcional;
* [ ] áreas de toque adequadas.

## Acessibilidade

* [ ] teclado;
* [ ] foco visível;
* [ ] nomes acessíveis;
* [ ] `aria-current` quando apropriado;
* [ ] `aria-expanded` quando apropriado;
* [ ] contraste adequado.

## Tecnologia

* [ ] Django URL names;
* [ ] Font Awesome consistente;
* [ ] Bootstrap compatível com GDS;
* [ ] HTMX apenas onde apropriado;
* [ ] Alpine.js somente para estado local;
* [ ] JavaScript compartilhado reutilizado.

## Dashboards

* [ ] utiliza `dashboard_base.html`;
* [ ] utiliza `dashboard_breadcrumb`;
* [ ] utiliza `dashboard-sidebar.js`;
* [ ] não duplica persistência;
* [ ] preserva anti-FOUC;
* [ ] configuração localStorage está correta.

---

# 97. Governança

Mudanças na navegação principal possuem impacto transversal.

Alterações em:

* `base_com_menu.html`;
* `menu.html`;
* `dashboard_base.html`;
* `dashboard-sidebar.js`;

deverão ser tratadas como alterações de infraestrutura.

Antes da modificação, avaliar impacto em todos os módulos da Área de Gestão.

---

# 98. Roadmap

## Fase 1 — Consolidação

* revisar nomenclaturas;
* eliminar itens duplicados;
* revisar breadcrumbs;
* revisar estados ativos;
* consolidar comportamento responsivo.

## Fase 2 — Padronização

* documentar grupos oficiais;
* padronizar submenus;
* revisar permissões;
* padronizar navegação mobile.

## Fase 3 — Acessibilidade

* consolidar foco;
* navegação por teclado;
* ARIA;
* áreas de toque;
* testes assistivos.

## Fase 4 — Evolução

* integrar progressivamente Alpine.js onde houver benefício real;
* expandir HTMX apenas para navegação parcial apropriada;
* preparar infraestrutura para PWA;
* preservar compatibilidade com mobile.

---

# 99. Documentos Relacionados

* GDS-01 — Introdução
* GDS-02 — Princípios
* GDS-03 — Cores
* GDS-04 — Tipografia
* GDS-05 — Espaçamento
* GDS-06 — Grid
* GDS-07 — Iconografia
* GDS-08 — Botões
* GDS-09 — Formulários
* GDS-10 — Cards
* GDS-11 — Tabelas e Listagens
* GDS-12 — Modais, Dialogs e Confirmações
* GDS-13 — Alertas, Toasts e Feedback
* GDS-15 — Dashboards
* GDS-16 — Acessibilidade
* GFE-01 — Frontend Architecture
* GFE-04 — Layouts
* GFE-05 — Templates
* GFE-08 — JavaScript
* GFE-09 — HTMX
* GFE-10 — Alpine.js
* GFE-11 — Dashboards

---

# 100. Princípios Finais

A navegação do GereIgreja deverá funcionar como uma infraestrutura única e previsível.

O usuário não deverá perceber que diferentes módulos foram construídos em momentos distintos.

Independentemente de estar em:

* Secretaria;
* Financeiro;
* Escola Bíblica;
* Eventos;
* Comunicação;
* Patrimônio;
* Relatórios;
* Assinaturas;

a lógica de navegação deverá permanecer familiar.

A estrutura ideal é:

```text
Identidade global
      ↓
Navegação principal
      ↓
Localização
      ↓
Conteúdo
      ↓
Ações contextuais
```

A Área de Gestão deverá permanecer claramente distinta da Administração Técnica baseada no Django Admin.

A navegação deverá ser construída sobre a infraestrutura existente, preservando `base_com_menu.html`, `menu.html`, `dashboard_base.html` e `dashboard-sidebar.js` como elementos centrais quando aplicáveis.

O objetivo final é permitir que o usuário navegue pelo GereIgreja de forma natural, segura e eficiente, sem precisar pensar sobre a estrutura da interface.

---

# 101. Status do Documento

**Pasta**

`docs/design-system/`

**Arquivo**

`14-Navegacao.md`

**Documento**

`GDS-14`

**Código**

`GDS-NAV`

**Framework**

`GereIgreja Design System (GDS)`

**Versão**

`1.0`

**Status**

`OFICIAL`

**Responsável**

`Equipe de Engenharia`

**Última atualização**

`Agosto de 2026`

---

# Fim do Documento

**GDS-14 — Navegação**
**GereIgreja Design System**
