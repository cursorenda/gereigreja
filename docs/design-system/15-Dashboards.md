Pasta:
`docs/design-system/`

Arquivo:
`15-Dashboards.md`

Documento:
GDS-15

Código:
GDS-DASHBOARDS

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

# GDS-15 — Dashboards

> "O dashboard do GereIgreja deve transformar dados operacionais em informação compreensível, permitindo que o usuário identifique rapidamente o estado de sua gestão e encontre as ações mais relevantes para seu trabalho."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel dos Dashboards
4. Relação entre GDS e GFE
5. Contexto Arquitetural Atual
6. Princípios
7. Arquitetura Visual
8. Hierarquia da Informação
9. Estrutura Oficial
10. Cabeçalho
11. Breadcrumb
12. Título
13. Controle da Sidebar
14. Barra de Ações
15. Filtros
16. Área de Conteúdo
17. KPIs
18. Anatomia do KPI
19. Valor Principal
20. Rótulo
21. Contexto Temporal
22. Indicadores de Variação
23. Ícones
24. Cards
25. Widgets
26. Gráficos
27. Tabelas
28. Listagens
29. Grid
30. Espaçamento
31. Cores
32. Tipografia
33. Estados Semânticos
34. Dashboard Principal
35. Dashboard da Secretaria
36. Dashboard Financeiro
37. Dashboard de Eventos
38. Dashboard da Escola Bíblica
39. Dashboard de Comunicação
40. Dashboard de Patrimônio
41. Dashboard de Relatórios
42. Dashboards de Outros Módulos
43. Estados Vazios
44. Estado de Primeiro Uso
45. Loading
46. Skeleton
47. Erro
48. Dados Indisponíveis
49. Nenhum Resultado
50. Atualização de Dados
51. Atualização Parcial
52. HTMX
53. Alpine.js
54. JavaScript Compartilhado
55. `dashboard-sidebar.js`
56. Local Storage
57. Anti-FOUC
58. Blocos do `dashboard_base.html`
59. `dashboard_title`
60. `dashboard_breadcrumb`
61. `dashboard_filters`
62. `dashboard_content`
63. `dashboard_css`
64. `dashboard_extra_js`
65. Configuração da Sidebar
66. Permissões
67. Multi-Tenant
68. Congregações e Escopo
69. Segurança
70. Privacidade
71. Dados Financeiros
72. Dados Pessoais
73. Responsividade
74. Desktop
75. Notebook
76. Tablet
77. Smartphone
78. Sidebar Responsiva
79. Grid Responsivo
80. KPIs em Mobile
81. Gráficos em Mobile
82. Tabelas em Mobile
83. Acessibilidade
84. Navegação por Teclado
85. Foco
86. Contraste
87. Não Dependência de Cor
88. Leitores de Tela
89. Movimento
90. Performance
91. Densidade de Informação
92. Progressive Enhancement
93. Navegação e Deep Links
94. Preservação de Filtros
95. Períodos
96. Datas
97. Valores Monetários
98. Dados Comparativos
99. Atualização Automática
100. Tempo Real
101. Drill-down
102. Ações Rápidas
103. Personalização
104. Anti-Patterns
105. Regras de Implementação
106. Evidências Arquiteturais
107. Especificações Oficiais
108. Checklist
109. Governança
110. Roadmap
111. Documentos Relacionados
112. Princípios Finais
113. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão visual e de experiência dos dashboards do GereIgreja.

Seu objetivo é garantir consistência entre os painéis utilizados pelos diferentes módulos da Área de Gestão, definindo como indicadores, cards, widgets, gráficos, tabelas, filtros, ações e estados deverão ser apresentados.

O GDS-15 complementa a arquitetura técnica definida no GereIgreja Frontend Engineering.

---

# 2. Escopo

Este documento aplica-se aos dashboards da Área de Gestão do GereIgreja.

Inclui, conforme os módulos presentes ou futuros da plataforma:

* Dashboard Principal;
* Secretaria;
* Financeiro;
* Eventos;
* Comunicação;
* Escola Bíblica;
* Patrimônio;
* Relatórios;
* demais dashboards internos.

Não se aplica diretamente à Administração Técnica baseada no Django Admin.

A Administração Técnica possui arquitetura de templates e navegação própria.

---

# 3. Papel dos Dashboards

Dashboards deverão apresentar uma visão resumida de informações relevantes para a gestão.

Seu objetivo não é reunir todas as funcionalidades do módulo em uma única tela.

Um dashboard deverá ajudar o usuário a responder rapidamente:

```text
O que está acontecendo?

Existe algo que exige atenção?

Quais são os principais indicadores?

Quais ações posso executar agora?

Onde encontro os detalhes?
```

---

# 4. Relação entre GDS e GFE

O GDS e o GFE possuem responsabilidades diferentes.

```text
GFE-11 — Dashboards
        ↓
Arquitetura técnica

GDS-15 — Dashboards
        ↓
Experiência e linguagem visual
```

O GFE define:

* herança de templates;
* infraestrutura;
* scripts;
* blocos;
* integração técnica.

O GDS define:

* hierarquia visual;
* composição;
* apresentação;
* estados;
* responsividade;
* acessibilidade;
* comportamento visual.

Os dois documentos são complementares.

---

# 5. Contexto Arquitetural Atual

A arquitetura atual do GereIgreja possui infraestrutura específica para Dashboards Premium.

Entre os elementos identificados estão:

`dashboard_base.html`

e:

`static/js/dashboard-sidebar.js`

O `dashboard_base.html` herda da infraestrutura da Área de Gestão:

```django
{% extends 'base_com_menu.html' %}
```

A Administração Técnica baseada no Django Admin não utiliza essa mesma árvore de herança.

---

# 6. Princípios

Todo dashboard deverá seguir:

* clareza;
* relevância;
* hierarquia;
* consistência;
* baixa carga cognitiva;
* responsividade;
* acessibilidade;
* desempenho;
* segurança;
* reutilização.

A primeira dobra da página deverá privilegiar informação realmente útil.

---

# 7. Arquitetura Visual

Estrutura conceitual:

```text
Dashboard
│
├── Breadcrumb
├── Cabeçalho
│   ├── Controle da Sidebar
│   ├── Título
│   └── Ações
│
├── Filtros opcionais
│
├── KPIs
│
├── Conteúdo analítico
│   ├── Cards
│   ├── Widgets
│   └── Gráficos
│
├── Conteúdo operacional
│   ├── Tabelas
│   └── Listagens
│
└── Estados e Feedback
```

Nem todo dashboard deverá possuir todas essas regiões.

---

# 8. Hierarquia da Informação

A ordem visual recomendada é:

```text
Contexto
   ↓
Indicadores principais
   ↓
Informações que exigem atenção
   ↓
Análises
   ↓
Detalhamento operacional
```

O usuário deverá perceber primeiro os dados mais relevantes.

---

# 9. Estrutura Oficial

Estrutura recomendada:

```text
Breadcrumb

[Controle do Menu] Título              [Ações]

Filtros

[KPI] [KPI] [KPI] [KPI]

[Widget principal           ] [Resumo]

[Conteúdo secundário        ] [Widget]

[Tabela / Listagem                    ]
```

Essa estrutura é uma referência visual, não uma grade obrigatória para todos os módulos.

---

# 10. Cabeçalho

O cabeçalho deverá identificar claramente o dashboard.

Poderá conter:

* controle da sidebar;
* título;
* descrição curta;
* ações contextuais.

Não deverá competir visualmente com os KPIs.

---

# 11. Breadcrumb

Dashboards deverão utilizar o padrão oficial de breadcrumb da Área de Gestão.

Exemplo:

```text
Home > Financeiro
```

ou:

```text
Home > Secretaria > Dashboard
```

conforme a hierarquia real da aplicação.

---

# 12. Título

O título deverá informar claramente o contexto.

Exemplos:

```text
Dashboard Financeiro
```

```text
Dashboard da Secretaria
```

Evitar:

```text
Painel
```

quando isso não identifica o módulo.

---

# 13. Controle da Sidebar

Quando o dashboard utilizar a infraestrutura Premium, deverá disponibilizar o controle oficial da sidebar.

Exemplo conceitual:

```text
[☰ Ocultar menu] Dashboard Financeiro
```

O controle deverá permanecer próximo ao título conforme o padrão já adotado.

---

# 14. Barra de Ações

Ações frequentes poderão permanecer próximas ao cabeçalho.

Exemplo financeiro:

```text
[Novo lançamento]
```

Exemplo Secretaria:

```text
[Novo membro]
```

Exemplo Eventos:

```text
[Novo evento]
```

A quantidade deverá ser limitada às ações realmente relevantes.

---

# 15. Filtros

Filtros deverão ser utilizados quando alterarem significativamente a visão do dashboard.

Exemplos:

* período;
* congregação;
* categoria;
* status.

Filtros não deverão existir apenas porque os dados possuem parâmetros possíveis.

---

# 16. Área de Conteúdo

O conteúdo deverá ser organizado em blocos compreensíveis.

Evitar uma grade de componentes sem relação aparente.

Cada linha deverá possuir uma intenção visual clara.

---

# 17. KPIs

KPIs representam indicadores resumidos.

Exemplos aplicáveis ao GereIgreja:

```text
Total de membros
Visitantes
Congregações
Receitas
Despesas
Saldo
Eventos
Turmas
Alunos
```

O KPI deverá representar apenas uma métrica principal.

---

# 18. Anatomia do KPI

Estrutura:

```text
KPI
├── Ícone opcional
├── Rótulo
├── Valor principal
├── Contexto
└── Variação opcional
```

Exemplo:

```text
Membros

1.248

+12 neste mês
```

---

# 19. Valor Principal

O valor deverá possuir maior hierarquia dentro do KPI.

Exemplo:

```text
1.248
```

Não aumentar excessivamente o tamanho a ponto de prejudicar o equilíbrio do layout.

---

# 20. Rótulo

O rótulo deverá explicar o valor.

Preferir:

```text
Membros ativos
```

em vez de:

```text
Total
```

quando o contexto não for autoexplicativo.

---

# 21. Contexto Temporal

Indicadores dependentes de período deverão informá-lo.

Exemplo:

```text
Receitas deste mês
```

ou:

```text
Agosto de 2026
```

Nunca apresentar um valor financeiro temporalmente ambíguo.

---

# 22. Indicadores de Variação

Quando houver comparação:

```text
+8,4% em relação ao mês anterior
```

A comparação deverá informar claramente a referência.

Evitar apenas:

```text
+8,4%
```

sem contexto.

---

# 23. Ícones

O GereIgreja utiliza amplamente Font Awesome na interface atual.

KPIs poderão utilizar ícones da biblioteca já consolidada.

Exemplo conceitual:

```html
<i class="fas fa-users"></i>
```

Não introduzir outra biblioteca de ícones apenas para dashboards.

---

# 24. Cards

Cards deverão seguir o GDS-10.

O dashboard poderá reutilizar:

* card de indicador;
* card de resumo;
* card financeiro;
* card de evento;
* card de ação;
* card de status.

Não criar cards exclusivos por dashboard quando um componente existente for suficiente.

---

# 25. Widgets

Widgets são componentes mais ricos do dashboard.

Exemplos:

* aniversariantes;
* próximos eventos;
* resumo financeiro;
* atividade recente;
* frequência;
* comunicados.

Cada widget deverá possuir responsabilidade única.

---

# 26. Gráficos

Gráficos deverão existir somente quando facilitarem análise.

Não utilizar gráfico quando um número ou pequena tabela comunicar melhor a informação.

Todo gráfico deverá possuir:

* título;
* contexto;
* período;
* legenda quando necessária;
* acessibilidade;
* alternativa textual quando apropriada.

---

# 27. Tabelas

Tabelas poderão apresentar informações operacionais resumidas.

Exemplos:

```text
Últimos membros cadastrados
Últimos lançamentos
Próximos eventos
```

As regras completas de tabelas seguem o GDS-11.

---

# 28. Listagens

Listagens simples são adequadas quando há poucos atributos por item.

Exemplo:

```text
Aniversariantes de hoje

João da Silva
Maria Oliveira
Carlos Souza
```

Não utilizar tabela quando uma lista for suficiente.

---

# 29. Grid

Dashboards deverão utilizar o grid oficial documentado no GDS-06.

Distribuições comuns poderão incluir:

```text
3 + 3 + 3 + 3
```

para quatro KPIs.

E:

```text
8 + 4
```

para conteúdo principal e resumo lateral.

A composição final dependerá do conteúdo real.

---

# 30. Espaçamento

Os dashboards deverão utilizar a escala definida no GDS-05.

Componentes equivalentes deverão preservar:

* padding;
* gaps;
* ritmo vertical;
* alinhamentos.

---

# 31. Cores

Os dashboards deverão utilizar a paleta oficial:

```text
Brand 700 — #0D8281
Brand 900 — #0A6665
Brand Soft — #DFF4F3

Background — #F1F5F9
Surface — #FFFFFF
Border — #D7E2E8
Text — #1E293B
Text Muted — #64748B

Success — #10B981
Warning — #D97706
Danger — #EF4444
```

Não criar uma paleta própria por dashboard.

---

# 32. Tipografia

A hierarquia deverá seguir o GDS-04.

Exemplo:

```text
Título do Dashboard
        ↓
Título do Widget
        ↓
Valor do KPI
        ↓
Descrição
        ↓
Metadados
```

---

# 33. Estados Semânticos

Success, Warning e Danger deverão representar significado funcional.

Não utilizar cores semânticas apenas para tornar KPIs visualmente diferentes.

---

# 34. Dashboard Principal

O Dashboard Principal deverá oferecer uma visão geral da Área de Gestão.

Seus indicadores deverão representar informações realmente úteis ao usuário autenticado.

Exemplos possíveis:

```text
Membros
Congregações
Eventos
Visitantes
```

A composição final deverá respeitar dados disponíveis, permissões e contexto.

---

# 35. Dashboard da Secretaria

O dashboard da Secretaria poderá priorizar indicadores relacionados a:

* membros;
* visitantes;
* congregações;
* aniversariantes;
* cadastros recentes;
* movimentações da área.

Exemplo:

```text
[Membros] [Visitantes] [Congregações] [Novos cadastros]

[Aniversariantes                 ] [Resumo]

[Cadastros recentes                        ]
```

---

# 36. Dashboard Financeiro

O Financeiro deverá priorizar dados de gestão financeira.

Exemplos:

```text
Receitas
Despesas
Saldo
Pendências
```

Uma composição possível:

```text
[Receitas] [Despesas] [Saldo] [Pendências]

[Evolução financeira             ] [Resumo]

[Últimos lançamentos                       ]
```

Valores financeiros somente deverão ser apresentados a usuários autorizados.

---

# 37. Dashboard de Eventos

Poderá apresentar:

* próximos eventos;
* eventos do período;
* status;
* agenda;
* informações resumidas.

A prioridade deverá ser temporal e operacional.

---

# 38. Dashboard da Escola Bíblica

Poderá apresentar:

* turmas;
* alunos;
* professores;
* frequência;
* atividades relacionadas.

A composição deverá refletir as funcionalidades realmente disponíveis no módulo.

---

# 39. Dashboard de Comunicação

Poderá apresentar:

* comunicações recentes;
* agendamentos;
* estados de envio;
* indicadores relevantes.

Estados como:

```text
Rascunho
Agendado
Enviado
Falha
```

deverão permanecer semanticamente distintos quando existirem.

---

# 40. Dashboard de Patrimônio

Poderá apresentar resumos relacionados aos registros patrimoniais existentes no sistema.

Não deverá inventar métricas sem significado administrativo real.

---

# 41. Dashboard de Relatórios

Relatórios não deverão ser simplesmente transformados em gráficos.

O dashboard poderá apresentar atalhos e indicadores resumidos, mantendo relatórios completos em suas interfaces próprias.

---

# 42. Dashboards de Outros Módulos

Novos módulos deverão utilizar a mesma arquitetura visual.

A identidade poderá variar pelo conteúdo, nunca por uma linguagem visual completamente independente.

---

# 43. Estados Vazios

Um widget sem dados deverá apresentar estado vazio.

Exemplo:

```text
Próximos eventos

Nenhum evento agendado.

[Adicionar evento]
```

Quando a ação for permitida.

Estado vazio não é erro.

---

# 44. Estado de Primeiro Uso

Em módulos ainda não configurados, poderá existir orientação.

Exemplo:

```text
Nenhuma turma cadastrada.

Crie a primeira turma para começar a utilizar
os recursos da Escola Bíblica.

[Criar turma]
```

---

# 45. Loading

Componentes carregados de forma assíncrona deverão apresentar estado de processamento quando perceptível.

Exemplo:

```text
Carregando dados financeiros...
```

---

# 46. Skeleton

Skeleton poderá ser utilizado para preservar estrutura durante carregamento.

Ele deverá aproximar-se das dimensões do conteúdo final.

Não utilizar skeleton em operações instantâneas sem benefício perceptível.

---

# 47. Erro

Quando um widget falhar:

```text
Não foi possível carregar os dados.

[Tentar novamente]
```

O erro deverá permanecer limitado ao componente quando o restante do dashboard continuar funcional.

---

# 48. Dados Indisponíveis

Ausência temporária de dados não deverá ser confundida com valor zero.

Diferenciar:

```text
0
```

de:

```text
Não disponível
```

e:

```text
Não informado
```

---

# 49. Nenhum Resultado

Quando filtros resultarem em nenhum dado:

```text
Nenhum resultado encontrado para os filtros aplicados.

[Limpar filtros]
```

Não apresentar como falha do sistema.

---

# 50. Atualização de Dados

O usuário deverá compreender quando dados relevantes foram atualizados.

Quando necessário:

```text
Atualizado às 09:35
```

ou equivalente.

Não adicionar timestamps a todos os widgets sem necessidade.

---

# 51. Atualização Parcial

Widgets independentes deverão poder ser atualizados sem recarregar todo o dashboard quando isso oferecer benefício real.

Fluxo:

```text
Widget
  ↓
Request
  ↓
Django
  ↓
Partial
  ↓
Widget atualizado
```

---

# 52. HTMX

HTMX constitui a diretriz oficial para atualizações parciais servidor-interface.

Sua adoção prática no GereIgreja é gradual.

Aplicações adequadas incluem:

* atualização de KPI;
* filtros;
* widgets;
* tabelas;
* listagens.

Não documentar um fluxo HTMX específico como existente sem implementação correspondente.

---

# 53. Alpine.js

Alpine.js é recomendado para estados locais leves.

Sua adoção prática também é gradual.

Exemplos apropriados:

* mostrar filtros;
* recolher painel;
* alternar área visual;
* controlar pequena interação local.

Regras de negócio continuarão no backend.

---

# 54. JavaScript Compartilhado

JavaScript compartilhado permanece responsável por infraestrutura mais complexa.

Exemplos:

* sidebar;
* Local Storage;
* gráficos;
* bibliotecas externas;
* comportamento estrutural.

---

# 55. `dashboard-sidebar.js`

O script:

`static/js/dashboard-sidebar.js`

constitui infraestrutura compartilhada dos Dashboards Premium.

Ele não deverá ser duplicado por módulo.

---

# 56. Local Storage

A sidebar dos dashboards utiliza persistência local para preservar o estado escolhido pelo usuário.

Entre as chaves identificadas na documentação arquitetural está:

`dashboard.sidebar_visible`

Além de configurações específicas fornecidas pelo próprio dashboard quando aplicável.

---

# 57. Anti-FOUC

O layout de dashboard possui lógica destinada a aplicar o estado da sidebar antes da apresentação final da página.

Essa estratégia reduz mudanças visuais abruptas durante o carregamento.

Alterações no dashboard não deverão remover esse comportamento sem substituição adequada.

---

# 58. Blocos do `dashboard_base.html`

A infraestrutura do dashboard disponibiliza pontos de extensão.

Entre eles:

```text
dashboard_title
dashboard_breadcrumb
dashboard_filters
dashboard_content
dashboard_css
dashboard_extra_js
```

Além de blocos relacionados à configuração da sidebar.

---

# 59. `dashboard_title`

Deverá definir o título específico do dashboard.

---

# 60. `dashboard_breadcrumb`

Deverá definir sua posição dentro da Área de Gestão.

---

# 61. `dashboard_filters`

Deverá concentrar filtros específicos quando existirem.

Não colocar filtros do módulo diretamente no layout base.

---

# 62. `dashboard_content`

Representa a região principal do dashboard.

Todo conteúdo específico deverá permanecer dentro dessa extensão.

---

# 63. `dashboard_css`

Deverá ser utilizado somente quando houver necessidade legítima de estilo complementar.

Estilos compartilháveis deverão migrar para infraestrutura global.

---

# 64. `dashboard_extra_js`

Scripts específicos poderão ser carregados quando necessários.

Evitar JavaScript inline extenso.

---

# 65. Configuração da Sidebar

Blocos como:

```text
dashboard_sidebar_key
dashboard_sidebar_init_key
```

permitem especialização sem alteração do layout base.

Novos dashboards deverão reutilizar esse mecanismo quando aplicável.

---

# 66. Permissões

O dashboard deverá respeitar as permissões do usuário.

Um usuário poderá visualizar apenas os indicadores, widgets e ações aos quais possui acesso.

---

# 67. Multi-Tenant

Dashboards deverão respeitar integralmente o isolamento organizacional da plataforma.

Nenhum KPI, gráfico, card ou tabela poderá combinar indevidamente informações pertencentes a contextos não autorizados.

---

# 68. Congregações e Escopo

Quando dados dependerem de congregação ou outro escopo organizacional, esse contexto deverá ser compreensível.

Filtros e indicadores deverão indicar claramente o universo analisado quando necessário.

---

# 69. Segurança

Ocultar um widget não substitui autorização.

O backend deverá controlar o acesso aos dados.

---

# 70. Privacidade

Dashboards deverão apresentar apenas dados pessoais necessários à finalidade da tela.

Não expor informações sensíveis apenas porque há espaço disponível.

---

# 71. Dados Financeiros

Informações financeiras deverão considerar:

* permissão;
* período;
* moeda;
* precisão;
* contexto.

Utilizar:

```text
R$ 1.250,00
```

conforme o padrão brasileiro.

---

# 72. Dados Pessoais

Cards como aniversariantes ou visitantes deverão respeitar as regras de acesso e privacidade do sistema.

---

# 73. Responsividade

Todo dashboard deverá funcionar adequadamente em:

* desktop;
* notebook;
* tablet;
* smartphone.

A responsividade não deverá consistir apenas em reduzir dimensões.

Os componentes deverão ser reorganizados.

---

# 74. Desktop

Em desktop, o dashboard poderá aproveitar múltiplas colunas.

Exemplo:

```text
[KPI] [KPI] [KPI] [KPI]
```

---

# 75. Notebook

A composição poderá permanecer semelhante ao desktop, ajustando densidade e largura.

---

# 76. Tablet

KPIs poderão reduzir a quantidade por linha.

Exemplo:

```text
[KPI] [KPI]

[KPI] [KPI]
```

---

# 77. Smartphone

Priorizar fluxo vertical:

```text
[KPI]

[KPI]

[KPI]

[Widget]

[Tabela adaptada]
```

---

# 78. Sidebar Responsiva

A sidebar não deverá reduzir excessivamente a área de conteúdo em dispositivos pequenos.

Seu comportamento deverá seguir a infraestrutura compartilhada.

---

# 79. Grid Responsivo

Não definir número fixo de colunas independentemente do viewport.

Utilizar as regras do GDS-06.

---

# 80. KPIs em Mobile

KPIs deverão permanecer legíveis.

Evitar:

* números cortados;
* rótulos truncados;
* ícones excessivos;
* quatro colunas estreitas.

---

# 81. Gráficos em Mobile

Gráficos deverão:

* permanecer legíveis;
* reduzir elementos secundários;
* permitir compreensão sem zoom;
* evitar legendas excessivamente grandes.

Se um gráfico não funcionar em mobile, reconsiderar o componente.

---

# 82. Tabelas em Mobile

Aplicar as estratégias do GDS-11:

* colunas prioritárias;
* responsividade;
* rolagem horizontal controlada;
* representação alternativa quando apropriada.

---

# 83. Acessibilidade

Dashboards deverão ser acessíveis como qualquer outra interface da plataforma.

---

# 84. Navegação por Teclado

Todos os controles deverão funcionar sem mouse.

Incluindo:

* filtros;
* ações;
* sidebar;
* tabelas;
* menus;
* links.

---

# 85. Foco

O foco deverá permanecer visível.

Cards clicáveis, gráficos interativos e ações deverão possuir tratamento apropriado.

---

# 86. Contraste

Cores dos indicadores deverão possuir contraste adequado.

---

# 87. Não Dependência de Cor

Não comunicar:

```text
positivo
negativo
atenção
erro
```

somente por cor.

Utilizar texto, ícone ou outro indicador.

---

# 88. Leitores de Tela

A ordem semântica deverá refletir a ordem lógica das informações.

Valores de KPIs deverão possuir rótulos compreensíveis.

---

# 89. Movimento

Animações deverão ser discretas.

Evitar:

* contadores constantemente animados;
* gráficos em movimento contínuo;
* cards saltando;
* transições longas.

Preferências de redução de movimento deverão ser respeitadas quando aplicável.

---

# 90. Performance

Dashboards possuem potencial para executar várias consultas e carregar muitos recursos.

A implementação deverá considerar:

* quantidade de queries;
* agregações;
* cache quando apropriado;
* carregamento parcial;
* bibliotecas de gráficos;
* payload;
* atualização seletiva.

---

# 91. Densidade de Informação

Mais informação não significa melhor dashboard.

Evitar a chamada "parede de KPIs".

Cada métrica deverá justificar sua presença.

---

# 92. Progressive Enhancement

O dashboard deverá preservar funcionalidade fundamental mesmo quando interações adicionais não estiverem disponíveis.

Django Templates continuam sendo a base de renderização.

HTMX e Alpine.js deverão atuar como melhorias progressivas.

---

# 93. Navegação e Deep Links

Widgets e ações importantes deverão direcionar para páginas específicas quando existir conteúdo detalhado.

Exemplo:

```text
Membros ativos
1.248

[Ver membros]
```

O usuário não deverá depender exclusivamente do dashboard para trabalhar com os registros.

---

# 94. Preservação de Filtros

Filtros deverão permanecer enquanto o usuário interage com widgets relacionados quando isso for coerente.

Evitar resets inesperados.

---

# 95. Períodos

Dashboards temporais deverão utilizar períodos claramente definidos.

Exemplos:

```text
Hoje
Esta semana
Este mês
Período personalizado
```

O significado deverá ser consistente dentro do módulo.

---

# 96. Datas

Datas deverão utilizar o padrão brasileiro quando apresentadas ao usuário:

```text
DD/MM/AAAA
```

---

# 97. Valores Monetários

Valores financeiros deverão utilizar:

```text
R$ 1.250,00
```

Mantendo precisão e alinhamento consistente.

---

# 98. Dados Comparativos

Comparações deverão utilizar bases equivalentes.

Exemplo:

```text
Agosto de 2026
versus
Julho de 2026
```

Evitar comparações visualmente convincentes, mas metodologicamente inconsistentes.

---

# 99. Atualização Automática

Atualização automática somente deverá existir quando houver benefício real.

Dashboards administrativos comuns não deverão fazer requests contínuos sem necessidade.

---

# 100. Tempo Real

Tempo real não deverá ser tratado como requisito padrão.

Quando uma informação não precisa de atualização imediata, utilizar estratégias mais simples.

---

# 101. Drill-down

Indicadores poderão levar a uma visão detalhada.

Exemplo:

```text
Despesas
R$ 11.200,00
    ↓
Lançamentos filtrados
```

O destino deverá preservar o contexto quando possível.

---

# 102. Ações Rápidas

Ações rápidas deverão representar tarefas realmente frequentes.

Exemplos:

```text
Novo membro
Novo lançamento
Novo evento
```

Não utilizar o dashboard como substituto completo do menu.

---

# 103. Personalização

Personalização individual de widgets poderá ser considerada futuramente.

Não deverá ser tratada como recurso atual sem implementação correspondente.

---

# 104. Anti-Patterns

Evitar:

* dashboards com dezenas de KPIs;
* gráfico para qualquer número;
* cores diferentes por módulo;
* cards duplicados;
* widgets sem finalidade;
* dados sem período;
* valores sem contexto;
* métricas não autorizadas;
* JavaScript duplicado;
* sidebar própria por dashboard;
* múltiplas fontes de verdade;
* carregamento integral por pequena atualização;
* animações excessivas;
* informação crítica apenas por cor;
* tabelas gigantes na primeira dobra;
* atualização automática sem necessidade;
* regras de negócio no template;
* frontend como mecanismo de segurança;
* HTMX utilizado como SPA improvisada;
* Alpine.js utilizado para lógica de domínio.

---

# 105. Regras de Implementação

A prioridade será:

```text
Reutilizar dashboard_base.html
        ↓
Reutilizar componentes GDS
        ↓
Reutilizar JavaScript compartilhado
        ↓
Especializar somente o necessário
```

Novos dashboards não deverão recriar infraestrutura já disponível.

---

# 106. Evidências Arquiteturais

## EA-GDS-DASH-001

Existe infraestrutura específica em `dashboard_base.html`.

## EA-GDS-DASH-002

`dashboard_base.html` herda de `base_com_menu.html`.

## EA-GDS-DASH-003

A Área de Gestão é arquiteturalmente distinta do Django Admin.

## EA-GDS-DASH-004

Existe script compartilhado `static/js/dashboard-sidebar.js`.

## EA-GDS-DASH-005

A sidebar utiliza persistência via Local Storage.

## EA-GDS-DASH-006

A infraestrutura possui mecanismo anti-FOUC relacionado ao estado da sidebar.

## EA-GDS-DASH-007

O layout disponibiliza blocos específicos para título, breadcrumb, filtros, conteúdo, CSS e JavaScript.

## EA-GDS-DASH-008

Font Awesome está consolidado na interface atual.

## EA-GDS-DASH-009

Bootstrap participa da estrutura visual e responsiva.

## EA-GDS-DASH-010

HTMX está definido como diretriz para atualização parcial, com adoção prática gradual.

## EA-GDS-DASH-011

Alpine.js está definido como tecnologia recomendada para estados locais leves, também em adoção gradual.

## EA-GDS-DASH-012

Django Templates permanecem como base da renderização.

---

# 107. Especificações Oficiais

## GDS-DASH-001

Todo dashboard deverá possuir objetivo claro.

## GDS-DASH-002

Dashboards compatíveis deverão reutilizar `dashboard_base.html`.

## GDS-DASH-003

Dashboards não deverão recriar a sidebar.

## GDS-DASH-004

A lógica da sidebar deverá permanecer centralizada em `dashboard-sidebar.js`.

## GDS-DASH-005

O estado da sidebar deverá preservar a infraestrutura existente.

## GDS-DASH-006

Dashboards deverão utilizar breadcrumb.

## GDS-DASH-007

Dashboards deverão possuir título específico.

## GDS-DASH-008

KPIs deverão representar uma métrica principal.

## GDS-DASH-009

KPIs temporais deverão indicar período quando necessário.

## GDS-DASH-010

Valores financeiros deverão utilizar representação monetária brasileira.

## GDS-DASH-011

Dados financeiros deverão respeitar permissões.

## GDS-DASH-012

Todos os dados deverão respeitar isolamento multi-tenant.

## GDS-DASH-013

Cards deverão seguir o GDS-10.

## GDS-DASH-014

Tabelas deverão seguir o GDS-11.

## GDS-DASH-015

Feedback deverá seguir o GDS-13.

## GDS-DASH-016

A navegação deverá seguir o GDS-14.

## GDS-DASH-017

O grid deverá seguir o GDS-06.

## GDS-DASH-018

Cores deverão utilizar tokens oficiais.

## GDS-DASH-019

Não deverá existir paleta independente por módulo.

## GDS-DASH-020

Font Awesome deverá permanecer a biblioteca de iconografia utilizada enquanto for o padrão consolidado da plataforma.

## GDS-DASH-021

Dashboards deverão ser responsivos.

## GDS-DASH-022

Dashboards deverão funcionar por teclado.

## GDS-DASH-023

Informações não deverão depender exclusivamente de cor.

## GDS-DASH-024

Widgets assíncronos deverão possuir loading quando perceptível.

## GDS-DASH-025

Widgets deverão possuir estado de erro quando puderem falhar isoladamente.

## GDS-DASH-026

Estados vazios não deverão ser apresentados como erro.

## GDS-DASH-027

HTMX deverá ser utilizado somente quando houver benefício real para atualização parcial.

## GDS-DASH-028

Alpine.js deverá limitar-se a estados locais.

## GDS-DASH-029

Regras de negócio deverão permanecer no backend.

## GDS-DASH-030

Permissões deverão ser validadas no backend.

## GDS-DASH-031

Gráficos deverão possuir finalidade analítica clara.

## GDS-DASH-032

Dashboards não deverão apresentar métricas apenas para ocupar espaço.

## GDS-DASH-033

Atualização automática deverá possuir justificativa funcional.

## GDS-DASH-034

Componentes reutilizáveis não deverão ser duplicados por módulo.

## GDS-DASH-035

Novos padrões deverão ser documentados antes de sua adoção ampla.

---

# 108. Checklist

## Estrutura

* [ ] utiliza `dashboard_base.html`;
* [ ] utiliza breadcrumb;
* [ ] possui título;
* [ ] sidebar integrada;
* [ ] ações bem posicionadas;
* [ ] filtros somente quando necessários;
* [ ] conteúdo possui hierarquia clara.

## KPIs

* [ ] métrica possui finalidade;
* [ ] rótulo é compreensível;
* [ ] valor possui contexto;
* [ ] período informado quando necessário;
* [ ] comparação possui referência;
* [ ] não depende somente de cor.

## Cards e Widgets

* [ ] reutiliza GDS-10;
* [ ] cada widget possui responsabilidade única;
* [ ] estado vazio;
* [ ] loading;
* [ ] erro;
* [ ] conteúdo não é excessivo.

## Gráficos

* [ ] gráfico realmente melhora a análise;
* [ ] título;
* [ ] período;
* [ ] legenda quando necessária;
* [ ] alternativa compreensível;
* [ ] responsividade.

## Tabelas

* [ ] segue GDS-11;
* [ ] possui somente colunas necessárias;
* [ ] funciona em mobile;
* [ ] preserva filtros quando apropriado.

## Navegação

* [ ] segue GDS-14;
* [ ] deep links funcionam;
* [ ] sidebar preserva estado;
* [ ] botão de mostrar/ocultar menu está acessível.

## Tecnologia

* [ ] Django Templates;
* [ ] Bootstrap compatível com GDS;
* [ ] Font Awesome consistente;
* [ ] HTMX somente quando apropriado;
* [ ] Alpine.js somente para estado local;
* [ ] JavaScript compartilhado reutilizado;
* [ ] sem scripts duplicados.

## Segurança

* [ ] permissões;
* [ ] isolamento organizacional;
* [ ] dados financeiros protegidos;
* [ ] dados pessoais protegidos;
* [ ] backend valida acesso.

## Responsividade

* [ ] desktop;
* [ ] notebook;
* [ ] tablet;
* [ ] smartphone;
* [ ] grid adaptado;
* [ ] gráficos legíveis;
* [ ] KPIs legíveis;
* [ ] tabelas utilizáveis.

## Acessibilidade

* [ ] teclado;
* [ ] foco;
* [ ] contraste;
* [ ] leitor de tela;
* [ ] sem dependência de cor;
* [ ] movimento controlado.

## Performance

* [ ] queries revisadas;
* [ ] sem atualizações desnecessárias;
* [ ] widgets independentes quando apropriado;
* [ ] bibliotecas carregadas somente quando necessárias;
* [ ] atualização parcial avaliada.

---

# 109. Governança

Dashboards fazem parte da infraestrutura compartilhada do GereIgreja.

Mudanças em:

* `dashboard_base.html`;
* `dashboard-sidebar.js`;
* configuração da sidebar;
* tokens visuais;
* componentes de KPI;
* componentes de widget;

deverão ser avaliadas como alterações transversais.

Um dashboard específico não deverá alterar infraestrutura global para resolver problema exclusivamente local sem análise de impacto.

---

# 110. Roadmap

## Fase 1 — Consolidação

* revisar dashboards existentes;
* padronizar KPIs;
* consolidar cards;
* revisar grids;
* eliminar estilos duplicados;
* revisar responsividade.

## Fase 2 — Componentização

Criar padrões reutilizáveis para:

* KPI;
* widget;
* filtro;
* estado vazio;
* loading;
* erro;
* ações rápidas.

A organização física deverá seguir a arquitetura atual baseada em includes e partials, sem presumir a existência de uma pasta global `components/`.

## Fase 3 — Atualização Parcial

Adotar HTMX progressivamente em:

* filtros;
* KPIs;
* tabelas;
* widgets;

quando houver benefício real.

## Fase 4 — Estados Locais

Adotar Alpine.js progressivamente para interações leves quando sua utilização simplificar a interface.

## Fase 5 — Evolução Analítica

Avaliar:

* comparativos;
* tendências;
* drill-down;
* filtros avançados;
* personalização de widgets;
* dashboards por perfil.

Essas funcionalidades constituem evolução futura e não deverão ser tratadas como implementação atual sem evidência correspondente.

## Fase 6 — Novas Plataformas

Preparar componentes para:

* PWA;
* interfaces móveis;
* novos formatos de dispositivo;
* futuras estratégias de temas e White Label.

---

# 111. Documentos Relacionados

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
* GDS-14 — Navegação
* GDS-16 — Acessibilidade
* GFE-01 — Frontend Architecture
* GFE-03 — Componentes
* GFE-04 — Layouts
* GFE-05 — Templates
* GFE-07 — CSS
* GFE-08 — JavaScript
* GFE-09 — HTMX
* GFE-10 — Alpine.js
* GFE-11 — Dashboards

---

# 112. Princípios Finais

O dashboard do GereIgreja não deverá ser uma coleção de gráficos, números e cards.

Ele deverá funcionar como uma interface de decisão.

A estrutura deverá transformar dados em uma sequência compreensível:

```text
Contexto
   ↓
Indicadores
   ↓
Atenção
   ↓
Análise
   ↓
Detalhamento
   ↓
Ação
```

Cada componente deverá justificar sua presença.

O usuário deverá conseguir identificar rapidamente:

* o estado atual de sua área de gestão;
* dados que exigem atenção;
* tendências importantes;
* tarefas frequentes;
* caminhos para informações detalhadas.

A infraestrutura técnica deverá permanecer baseada nos padrões já existentes do GereIgreja, especialmente:

`base_com_menu.html`

`dashboard_base.html`

`dashboard-sidebar.js`

Django Templates

Bootstrap

Font Awesome

com adoção progressiva de HTMX e Alpine.js quando houver benefício comprovado.

A Administração Técnica baseada no Django Admin permanece fora dessa arquitetura de dashboard da Área de Gestão.

O objetivo final é que os dashboards de Secretaria, Financeiro, Eventos, Escola Bíblica, Comunicação, Patrimônio e demais módulos pareçam partes de uma única plataforma, mantendo a mesma identidade, hierarquia, comportamento e qualidade de experiência.

---

# 113. Status do Documento

**Pasta**

`docs/design-system/`

**Arquivo**

`15-Dashboards.md`

**Documento**

`GDS-15`

**Código**

`GDS-DASHBOARDS`

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

**GDS-15 — Dashboards**
**GereIgreja Design System**
