Pasta:
`docs/design-system/`

Arquivo:
`16-Acessibilidade.md`

Documento:
GDS-16

Código:
GDS-A11Y

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

# GDS-16 — Acessibilidade

> "A acessibilidade no GereIgreja não é um recurso adicional. É parte da qualidade da plataforma e deve estar presente desde a concepção de cada interface."

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia de Acessibilidade
4. Princípios
5. Referência de Conformidade
6. Responsabilidade Compartilhada
7. Semântica HTML
8. Estrutura de Cabeçalhos
9. Landmarks
10. Links
11. Botões
12. Navegação por Teclado
13. Ordem de Foco
14. Foco Visível
15. Skip Links
16. ARIA
17. Uso Correto de ARIA
18. `aria-label`
19. `aria-labelledby`
20. `aria-describedby`
21. `aria-current`
22. `aria-expanded`
23. `aria-live`
24. Contraste
25. Paleta Oficial
26. Texto
27. Texto Muted
28. Cores Semânticas
29. Não Dependência de Cor
30. Tipografia
31. Tamanho de Texto
32. Espaçamento
33. Zoom
34. Responsividade
35. Área de Toque
36. Formulários
37. Labels
38. Placeholders
39. Campos Obrigatórios
40. Validação
41. Mensagens de Erro
42. Autocomplete
43. Inputs Específicos
44. Selects
45. Checkboxes
46. Radio Buttons
47. Switches
48. Upload
49. Botões
50. Botões Somente com Ícones
51. Estados Disabled
52. Tabelas
53. Cabeçalhos de Tabela
54. Ordenação
55. Ações em Tabelas
56. Paginação
57. Cards
58. Cards Interativos
59. Modais
60. Gestão de Foco em Modais
61. Alerts
62. Toasts
63. Dashboards
64. KPIs
65. Gráficos
66. Dados Financeiros
67. Navegação
68. Sidebar
69. Breadcrumb
70. Menus
71. Submenus
72. Área Pública
73. Administração Técnica
74. Imagens
75. Texto Alternativo
76. Imagens Decorativas
77. Ícones
78. Font Awesome
79. Conteúdo Audiovisual
80. Movimento
81. `prefers-reduced-motion`
82. Animações
83. Loading
84. Skeleton
85. Estados Vazios
86. Estados de Erro
87. HTMX
88. Atualizações Dinâmicas
89. Alpine.js
90. Bootstrap
91. Django Templates
92. Django Forms
93. JavaScript
94. Secretaria
95. Financeiro
96. Eventos
97. Escola Bíblica
98. Comunicação
99. Patrimônio
100. Relatórios
101. Administração
102. Permissões
103. Multi-Tenant
104. Segurança e Acessibilidade
105. Linguagem
106. Mensagens
107. Abreviações
108. Conteúdo Cognitivo
109. Prevenção de Erros
110. Operações Críticas
111. Testes
112. Testes com Teclado
113. Testes de Contraste
114. Testes com Leitores de Tela
115. Testes de Zoom
116. Testes de Responsividade
117. Testes de Formulários
118. Testes de Componentes
119. Evidências Arquiteturais
120. Especificações Oficiais
121. Checklist
122. Governança
123. Roadmap
124. Documentos Relacionados
125. Princípios Finais
126. Status do Documento

---

# 1. Objetivo

Este documento estabelece os padrões oficiais de acessibilidade aplicáveis ao frontend do GereIgreja.

Seu objetivo é garantir que as funcionalidades da plataforma possam ser utilizadas por pessoas com diferentes necessidades, tecnologias assistivas, dispositivos e formas de interação.

A acessibilidade deverá fazer parte:

* do Design System;
* da arquitetura frontend;
* da criação dos componentes;
* dos testes;
* da manutenção;
* da evolução da plataforma.

Não deverá ser tratada como etapa posterior de correção.

---

# 2. Escopo

Este documento aplica-se a:

* Área de Gestão do GereIgreja;
* Portal Público;
* Landing Pages;
* dashboards;
* formulários;
* tabelas;
* cards;
* botões;
* modais;
* alerts;
* toasts;
* menus;
* sidebar;
* breadcrumbs;
* gráficos;
* componentes reutilizáveis.

Também orienta customizações visuais da Administração Técnica quando existirem.

---

# 3. Filosofia de Acessibilidade

A interface deverá permitir que o usuário:

```text
Perceba
   ↓
Compreenda
   ↓
Navegue
   ↓
Interaja
   ↓
Conclua a tarefa
```

sem depender obrigatoriamente de:

* mouse;
* visão perfeita;
* percepção de cores;
* tela grande;
* animações;
* velocidade elevada de interação.

---

# 4. Princípios

A acessibilidade do GereIgreja deverá seguir os princípios:

* perceptível;
* operável;
* compreensível;
* robusta;
* consistente;
* inclusiva;
* progressiva;
* testável.

---

# 5. Referência de Conformidade

O GereIgreja deverá evoluir em direção às boas práticas estabelecidas pelas WCAG.

A meta recomendada para interfaces de produção deverá ser compatibilidade com critérios equivalentes ao nível AA sempre que tecnicamente aplicável.

A documentação não deverá declarar certificação formal sem auditoria apropriada.

---

# 6. Responsabilidade Compartilhada

A acessibilidade não pertence somente ao CSS.

Ela envolve:

```text
Design
+
HTML
+
Templates
+
Backend
+
JavaScript
+
Conteúdo
+
Testes
```

Uma interface visualmente acessível poderá continuar inacessível se:

* os elementos não possuírem semântica;
* o foco for quebrado;
* as mensagens não forem anunciadas;
* os campos não possuírem labels;
* ações dependerem exclusivamente do mouse.

---

# 7. Semântica HTML

Elementos HTML deverão ser utilizados conforme sua função.

Preferir:

```html
<button type="button">Salvar</button>
```

para ações.

Preferir:

```html
<a href="/membros/">Membros</a>
```

para navegação.

Evitar transformar elementos genéricos em componentes interativos sem implementar toda a semântica necessária.

---

# 8. Estrutura de Cabeçalhos

A hierarquia de títulos deverá refletir a estrutura do conteúdo.

Exemplo:

```text
H1 — Membros

H2 — Dados Pessoais

H2 — Dados Ministeriais

H3 — Informações Complementares
```

Não escolher níveis de heading apenas por aparência visual.

A aparência pertence ao CSS.

A hierarquia pertence ao documento.

---

# 9. Landmarks

A estrutura principal poderá utilizar elementos semânticos como:

```html
<header>
<nav>
<main>
<aside>
<footer>
```

quando apropriado.

Isso facilita a navegação por tecnologias assistivas.

---

# 10. Links

Links deverão possuir texto compreensível.

Preferir:

```text
Ver relatório financeiro
```

Evitar:

```text
Clique aqui
```

quando o contexto não estiver explícito.

---

# 11. Botões

Botões deverão comunicar a ação.

Exemplos:

```text
Salvar membro
Excluir evento
Gerar relatório
Enviar comunicado
```

As regras visuais e comportamentais seguem o GDS-08.

---

# 12. Navegação por Teclado

Toda funcionalidade essencial deverá ser utilizável sem mouse.

O usuário deverá conseguir navegar utilizando:

* Tab;
* Shift + Tab;
* Enter;
* Espaço;
* setas, quando o componente justificar.

---

# 13. Ordem de Foco

A ordem de foco deverá seguir a leitura lógica da página.

Exemplo:

```text
Navbar
   ↓
Sidebar
   ↓
Breadcrumb
   ↓
Título
   ↓
Filtros
   ↓
Conteúdo
   ↓
Ações
```

Evitar `tabindex` positivo para forçar ordem artificial.

---

# 14. Foco Visível

Todo elemento interativo deverá possuir foco claramente perceptível.

Nunca remover:

```css
outline: none;
```

sem substituição visual adequada.

---

# 15. Skip Links

Páginas extensas com navegação repetitiva poderão disponibilizar mecanismo para pular diretamente ao conteúdo principal.

Exemplo conceitual:

```text
Ir para o conteúdo principal
```

Esse recurso deverá ser avaliado especialmente na Área de Gestão com sidebar persistente.

---

# 16. ARIA

ARIA deverá complementar o HTML quando a semântica nativa não for suficiente.

Regra fundamental:

```text
HTML semântico primeiro
ARIA depois
```

Não adicionar ARIA indiscriminadamente.

---

# 17. Uso Correto de ARIA

Um atributo ARIA deverá refletir o estado real do componente.

Exemplo:

```html
aria-expanded="true"
```

somente quando o componente estiver realmente expandido.

---

# 18. `aria-label`

Pode ser utilizado quando um elemento interativo não possuir texto visível suficiente.

Exemplo:

```html
<button
    type="button"
    aria-label="Fechar modal">
</button>
```

---

# 19. `aria-labelledby`

Pode associar um elemento a um título já existente.

É especialmente útil em:

* dialogs;
* regiões;
* componentes complexos.

---

# 20. `aria-describedby`

Deverá ser utilizado quando uma descrição complementar precisar ser associada ao elemento.

Exemplo:

```text
Campo
+
Texto de ajuda
+
Erro
```

---

# 21. `aria-current`

Navegação poderá utilizar:

```html
aria-current="page"
```

no item correspondente à página atual.

Isso é particularmente adequado para:

* breadcrumbs;
* menus;
* paginação.

---

# 22. `aria-expanded`

Submenus e controles expansíveis deverão comunicar seu estado.

Exemplo:

```html
aria-expanded="false"
```

e:

```html
aria-expanded="true"
```

---

# 23. `aria-live`

Mensagens dinâmicas poderão utilizar regiões live.

Exemplo:

```html
aria-live="polite"
```

para mensagens comuns.

Estados realmente urgentes poderão exigir tratamento mais imediato.

O uso deverá seguir o GDS-13.

---

# 24. Contraste

O contraste deverá permitir leitura confortável.

Toda combinação entre:

* texto;
* fundo;
* borda;
* botão;
* ícone;
* badge;

deverá ser validada.

---

# 25. Paleta Oficial

A paleta oficial inclui:

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

A presença dessas cores no Design System não elimina a necessidade de validar contraste em cada combinação.

---

# 26. Texto

O texto principal deverá utilizar contraste elevado sobre as superfícies oficiais.

O token `Text` deverá ser preferido para conteúdos essenciais.

---

# 27. Texto Muted

`Text Muted` deverá ser utilizado somente para informações secundárias.

Não utilizar texto muted para:

* instruções essenciais;
* mensagens de erro;
* labels importantes;
* ações críticas.

---

# 28. Cores Semânticas

Success, Warning e Danger deverão ser acompanhados por significado textual ou iconográfico.

Exemplo:

```text
✓ Pagamento registrado
```

e não apenas uma área verde.

---

# 29. Não Dependência de Cor

O usuário não deverá precisar distinguir verde, amarelo ou vermelho para compreender o estado.

Exemplo adequado:

```text
✓ Ativo
```

```text
⚠ Pendente
```

```text
× Cancelado
```

---

# 30. Tipografia

A tipografia deverá seguir o GDS-04.

Acessibilidade tipográfica inclui:

* tamanho;
* contraste;
* peso;
* altura de linha;
* espaçamento;
* largura de leitura.

---

# 31. Tamanho de Texto

Textos essenciais não deverão utilizar tamanhos excessivamente pequenos.

Conteúdo operacional deverá permanecer legível em dispositivos móveis e diferentes níveis de zoom.

---

# 32. Espaçamento

Componentes deverão possuir espaço suficiente para diferenciar:

* grupos;
* campos;
* ações;
* seções.

A escala oficial definida no GDS-05 deverá ser utilizada.

---

# 33. Zoom

A interface deverá permanecer utilizável com zoom aumentado sempre que tecnicamente possível.

Evitar layouts que:

* cortem conteúdo;
* escondam ações;
* criem sobreposição;
* exijam redução manual do zoom.

---

# 34. Responsividade

Responsividade e acessibilidade são complementares.

A interface deverá adaptar-se sem:

* remover funcionalidades essenciais;
* ocultar informações críticas;
* tornar alvos de toque muito pequenos.

---

# 35. Área de Toque

Controles importantes deverão possuir área confortável.

A recomendação de referência do GDS para elementos interativos em touch é aproximadamente:

```text
44 × 44 px
```

especialmente em smartphones.

---

# 36. Formulários

Formulários deverão seguir o GDS-09.

Acessibilidade deverá estar presente em:

* labels;
* instruções;
* erros;
* campos obrigatórios;
* foco;
* teclado.

---

# 37. Labels

Todo campo deverá possuir identificação programaticamente associada.

Exemplo:

```html
<label for="nome">Nome completo</label>
<input id="nome" name="nome">
```

---

# 38. Placeholders

Placeholder não deverá substituir label.

Ele pode fornecer exemplo ou ajuda complementar.

---

# 39. Campos Obrigatórios

Campos obrigatórios deverão ser comunicados visualmente e programaticamente.

Não depender somente de:

```text
*
```

sem contexto.

---

# 40. Validação

A validação deverá fornecer informação compreensível.

Exemplo:

```text
Informe um endereço de e-mail válido.
```

Evitar:

```text
Valor inválido.
```

quando for possível especificar o problema.

---

# 41. Mensagens de Erro

A mensagem deverá estar associada ao campo.

Quando apropriado, o foco poderá ser direcionado ao primeiro erro após submissão.

A experiência deverá evitar que o usuário precise procurar manualmente onde está o problema.

---

# 42. Autocomplete

Campos de informações comuns poderão utilizar atributos de autocomplete adequados quando isso beneficiar o preenchimento.

Exemplos:

* nome;
* e-mail;
* telefone;
* endereço.

A aplicação deverá avaliar riscos específicos para dados sensíveis.

---

# 43. Inputs Específicos

Utilizar tipos adequados:

```html
type="email"
type="tel"
type="date"
type="number"
```

quando compatíveis com a experiência desejada.

---

# 44. Selects

Selects deverão ser utilizáveis por teclado.

Selects com busca deverão manter:

* foco;
* leitura;
* seleção;
* identificação.

---

# 45. Checkboxes

Checkboxes deverão possuir labels clicáveis.

Não apresentar apenas pequenas caixas sem identificação.

---

# 46. Radio Buttons

Grupos deverão possuir contexto claro.

Exemplo:

```text
Estado civil

○ Solteiro
○ Casado
○ Viúvo
```

---

# 47. Switches

Switches deverão comunicar claramente:

* função;
* estado atual.

Evitar apenas:

```text
[ON]
```

sem identificar o que está ativado.

---

# 48. Upload

Uploads deverão permitir compreender:

* campo;
* formatos;
* limite;
* resultado;
* erro.

O status do upload deverá ser acessível.

---

# 49. Botões

Botões deverão seguir:

* GDS-08;
* foco visível;
* semântica correta;
* contraste;
* área de toque.

---

# 50. Botões Somente com Ícones

Deverão possuir nome acessível.

Exemplo:

```html
<button aria-label="Editar membro">
    <i class="..."></i>
</button>
```

---

# 51. Estados Disabled

O estado desabilitado deverá permanecer compreensível.

Quando necessário, explicar por que a ação está indisponível.

Não reduzir contraste a ponto de o elemento se tornar completamente ilegível.

---

# 52. Tabelas

Tabelas deverão seguir o GDS-11.

Quando o conteúdo for realmente tabular, utilizar estrutura semântica de tabela.

---

# 53. Cabeçalhos de Tabela

Utilizar:

```html
<th>
```

de forma apropriada.

Cabeçalhos deverão permitir compreender a relação entre colunas e células.

---

# 54. Ordenação

Colunas ordenáveis deverão comunicar:

* que podem ser ordenadas;
* ordem atual;
* direção.

O estado não deverá depender apenas de um ícone pouco perceptível.

---

# 55. Ações em Tabelas

Botões de ação deverão possuir nomes acessíveis.

Exemplo:

```text
Editar João da Silva
```

para tecnologia assistiva, mesmo que visualmente apareça apenas o ícone de edição.

---

# 56. Paginação

Paginação deverá indicar:

* página atual;
* anterior;
* próxima;
* estados desabilitados.

Utilizar estrutura de navegação apropriada.

---

# 57. Cards

Cards seguem o GDS-10.

Cards informativos não deverão ser artificialmente focáveis.

Somente elementos realmente interativos deverão entrar na ordem de tabulação.

---

# 58. Cards Interativos

Cards inteiramente clicáveis deverão:

* possuir semântica correta;
* foco visível;
* destino previsível;
* interação por teclado.

---

# 59. Modais

Modais seguem o GDS-12.

A acessibilidade deverá considerar:

* título;
* dialog semantics;
* foco;
* fechamento;
* teclado;
* retorno do foco.

---

# 60. Gestão de Foco em Modais

Fluxo esperado:

```text
Botão abre modal
       ↓
Foco entra no modal
       ↓
Usuário interage
       ↓
Modal fecha
       ↓
Foco retorna ao acionador
```

O foco não deverá continuar navegando pelo conteúdo atrás do modal enquanto ele estiver ativo.

---

# 61. Alerts

Alerts deverão possuir conteúdo compreensível sem depender exclusivamente da cor.

---

# 62. Toasts

Toasts não deverão roubar foco automaticamente em operações comuns.

Mensagens dinâmicas deverão utilizar mecanismo adequado para tecnologias assistivas.

As regras completas seguem o GDS-13.

---

# 63. Dashboards

Dashboards seguem o GDS-15.

Acessibilidade deverá envolver:

* KPIs;
* gráficos;
* filtros;
* cards;
* tabelas;
* sidebar.

---

# 64. KPIs

Um KPI deverá possuir rótulo programaticamente compreensível.

Exemplo:

```text
Membros ativos
1.248
```

Evitar apresentar apenas:

```text
1.248
```

---

# 65. Gráficos

Gráficos não poderão ser o único meio de fornecer informação crítica.

Sempre que apropriado, deverá existir:

* resumo textual;
* tabela;
* valor;
* descrição.

Exemplo:

```text
Receitas cresceram 8,4% em relação ao mês anterior.
```

---

# 66. Dados Financeiros

Valores financeiros deverão ser apresentados de maneira legível.

Exemplo:

```text
R$ 1.250,00
```

Quando houver positivo ou negativo, não depender somente de verde ou vermelho.

---

# 67. Navegação

A navegação segue o GDS-14.

Acessibilidade deverá envolver:

* menu;
* sidebar;
* breadcrumb;
* foco;
* teclado;
* estado atual.

---

# 68. Sidebar

A sidebar deverá funcionar por teclado.

Itens ativos deverão ser identificáveis sem depender apenas da cor.

---

# 69. Breadcrumb

A página atual poderá utilizar:

```html
aria-current="page"
```

quando apropriado.

---

# 70. Menus

Menus deverão possuir ordem lógica.

Rótulos deverão ser objetivos.

---

# 71. Submenus

O estado expandido deverá ser comunicado.

Exemplo:

```html
aria-expanded="true"
```

A navegação não deverá depender exclusivamente do clique com mouse.

---

# 72. Área Pública

Landing Pages e Portal Público deverão seguir os mesmos requisitos essenciais de acessibilidade.

Especial atenção deverá ser dada a:

* navegação;
* headings;
* links;
* formulários;
* imagens;
* CTAs;
* contraste.

---

# 73. Administração Técnica

A Administração Técnica baseada no Django Admin possui estrutura própria.

Customizações visuais deverão preservar a acessibilidade fornecida pelo framework e evitar regressões introduzidas por CSS ou templates customizados.

Ela não deverá ser confundida com a Área de Gestão do GereIgreja.

---

# 74. Imagens

Imagens informativas deverão possuir descrição adequada quando necessária.

---

# 75. Texto Alternativo

O atributo `alt` deverá comunicar a função ou conteúdo relevante da imagem.

Exemplo:

```html
<img
    src="..."
    alt="Logotipo do GereIgreja">
```

A descrição deverá ser contextual.

---

# 76. Imagens Decorativas

Quando a imagem não transmitir informação:

```html
alt=""
```

poderá ser adequado.

Evitar descrições desnecessárias que criem ruído para leitores de tela.

---

# 77. Ícones

Ícones deverão seguir o GDS-07.

Ícones decorativos poderão ser ocultados das tecnologias assistivas.

Ícones funcionais deverão possuir nome acessível.

---

# 78. Font Awesome

O GereIgreja utiliza amplamente Font Awesome na implementação atual.

Um ícone como:

```html
<i class="fas fa-trash"></i>
```

não deverá ser considerado suficiente para comunicar uma ação.

O botão ou link deverá fornecer contexto textual acessível.

---

# 79. Conteúdo Audiovisual

Se o GereIgreja incorporar conteúdos de áudio ou vídeo, deverão ser considerados:

* legendas;
* transcrição;
* controles acessíveis;
* ausência de autoplay intrusivo.

Isso constitui diretriz para componentes audiovisuais presentes ou futuros.

---

# 80. Movimento

Movimento não deverá ser necessário para compreender a interface.

---

# 81. `prefers-reduced-motion`

Quando animações forem utilizadas, o sistema deverá considerar a preferência do usuário por redução de movimento quando tecnicamente aplicável.

Exemplo conceitual:

```css
@media (prefers-reduced-motion: reduce) {
    ...
}
```

---

# 82. Animações

Evitar:

* elementos piscando;
* movimento contínuo;
* transformações excessivas;
* animações que atrasem a operação.

As regras específicas serão complementadas pelo GDS-17.

---

# 83. Loading

Estados de carregamento deverão possuir informação acessível quando o atraso for perceptível.

Exemplo:

```text
Carregando membros...
```

---

# 84. Skeleton

Skeleton não deverá ser o único indicador para tecnologia assistiva.

Quando necessário, associar estado programático equivalente.

---

# 85. Estados Vazios

Estados vazios deverão explicar a situação.

Exemplo:

```text
Nenhum evento cadastrado.
```

e, quando permitido:

```text
[Criar evento]
```

---

# 86. Estados de Erro

Erros deverão informar:

* o problema;
* a ação possível.

Exemplo:

```text
Não foi possível carregar os membros.

[Tentar novamente]
```

---

# 87. HTMX

HTMX deverá preservar acessibilidade durante atualizações parciais.

Uma atualização de DOM não deverá:

* perder foco sem necessidade;
* deixar o usuário sem feedback;
* duplicar IDs;
* remover labels;
* quebrar regiões semânticas.

---

# 88. Atualizações Dinâmicas

Quando uma região for atualizada:

```text
Request
   ↓
Swap
   ↓
Novo conteúdo
```

o sistema deverá considerar:

* foco;
* anúncio;
* contexto;
* continuidade de leitura.

---

# 89. Alpine.js

Alpine.js poderá controlar estados locais.

Componentes criados com Alpine deverão preservar:

* semântica;
* teclado;
* ARIA;
* foco.

O uso da biblioteca não elimina requisitos de acessibilidade.

---

# 90. Bootstrap

Bootstrap fornece componentes com infraestrutura acessível em vários contextos.

Customizações do GDS não deverão remover comportamentos importantes.

Alterar CSS ou markup de componentes Bootstrap exige verificar regressões.

---

# 91. Django Templates

Templates deverão gerar HTML semântico.

A acessibilidade deverá ser incorporada aos templates reutilizáveis para evitar replicação de erros em toda a plataforma.

---

# 92. Django Forms

Django Forms deverá fornecer validação no backend.

A apresentação dos campos deverá mapear corretamente:

* label;
* help text;
* required;
* error;
* widget.

---

# 93. JavaScript

JavaScript não deverá tornar componentes inacessíveis.

Sempre verificar:

```text
Sem JavaScript
        ↓
Funcionalidade fundamental preservada quando possível

Com JavaScript
        ↓
Experiência aprimorada
```

Esse princípio está alinhado à estratégia de Progressive Enhancement do GereIgreja.

---

# 94. Secretaria

Interfaces da Secretaria envolvem grande quantidade de dados pessoais e formulários.

Prioridades:

* labels claros;
* fluxo de teclado;
* tabelas compreensíveis;
* buscas acessíveis;
* formulários extensos organizados;
* mensagens de validação.

---

# 95. Financeiro

O Financeiro exige atenção especial à distinção entre:

* receita;
* despesa;
* saldo;
* estorno;
* pendência;
* status.

Essas informações não deverão depender exclusivamente de cores.

---

# 96. Eventos

Datas, horários e status deverão possuir representação textual compreensível.

Calendários visuais deverão oferecer alternativa acessível quando necessário.

---

# 97. Escola Bíblica

Listagens de:

* turmas;
* alunos;
* professores;
* frequência;

deverão possuir estrutura adequada para leitura por teclado e tecnologias assistivas.

---

# 98. Comunicação

Estados como:

```text
Rascunho
Agendado
Enviado
Falha
```

deverão possuir rótulos claros.

Não comunicar o estado somente por cor ou ícone.

---

# 99. Patrimônio

Campos e tabelas patrimoniais deverão seguir as mesmas regras de formulários, tabelas e ações.

---

# 100. Relatórios

Relatórios deverão possuir:

* estrutura de títulos;
* tabelas semânticas;
* valores identificados;
* contexto temporal;
* boa legibilidade.

A versão de impressão deverá preservar compreensão mesmo sem cores.

---

# 101. Administração

Telas administrativas deverão manter os mesmos padrões de:

* teclado;
* foco;
* labels;
* mensagens;
* semântica.

Configurações críticas deverão possuir confirmação adequada.

---

# 102. Permissões

A acessibilidade deverá funcionar independentemente do perfil do usuário.

Quando uma ação não estiver disponível, a interface deverá permanecer coerente.

Ocultar uma ação por permissão não deverá quebrar:

* ordem visual;
* ordem de foco;
* agrupamentos;
* tabelas.

---

# 103. Multi-Tenant

O isolamento organizacional deverá permanecer consistente também nas mensagens acessíveis.

Tecnologias assistivas não deverão receber conteúdo oculto visualmente pertencente a outro contexto.

---

# 104. Segurança e Acessibilidade

Ocultar conteúdo apenas com CSS não constitui segurança.

Se o usuário não possui permissão para determinado dado, ele não deverá estar presente no DOM apenas invisível visualmente.

A filtragem deverá ocorrer no backend.

---

# 105. Linguagem

A linguagem da interface deverá ser compreensível.

Preferir:

```text
Salvar membro
```

em vez de:

```text
Persistir entidade
```

---

# 106. Mensagens

Mensagens deverão evitar jargão técnico.

Exemplo inadequado:

```text
IntegrityError.
```

Exemplo adequado:

```text
Não foi possível concluir a operação.
```

---

# 107. Abreviações

Abreviações deverão ser utilizadas somente quando amplamente compreendidas no contexto.

Quando houver risco de ambiguidade, escrever o termo completo.

---

# 108. Conteúdo Cognitivo

Interfaces deverão evitar:

* excesso de decisões simultâneas;
* textos longos sem estrutura;
* múltiplas ações primárias;
* terminologia inconsistente;
* mudanças inesperadas de contexto.

---

# 109. Prevenção de Erros

Sempre que possível, o Design System deverá ajudar o usuário a evitar erros antes que aconteçam.

Exemplos:

* tipos de campo adequados;
* máscara;
* limites claros;
* confirmação em operações críticas;
* seleção contextual.

---

# 110. Operações Críticas

Operações como:

* exclusão;
* estorno;
* alterações financeiras relevantes;
* mudanças de permissão;

deverão possuir linguagem clara e controles acessíveis.

Confirmações seguem o GDS-12.

---

# 111. Testes

A acessibilidade deverá ser testada.

Não deverá ser validada apenas por inspeção visual.

---

# 112. Testes com Teclado

Para cada tela, verificar:

1. acesso inicial;
2. sequência de Tab;
3. foco;
4. ativação de controles;
5. abertura e fechamento de menus;
6. modais;
7. formulários;
8. retorno do foco.

---

# 113. Testes de Contraste

Validar especialmente:

* Brand 700;
* Brand 900;
* Brand Soft;
* Text Muted;
* Success;
* Warning;
* Danger;
* estados disabled;
* links;
* foco.

---

# 114. Testes com Leitores de Tela

Componentes críticos deverão ser avaliados com tecnologia assistiva quando possível.

Prioridades:

* navegação;
* formulários;
* modais;
* tabelas;
* mensagens dinâmicas;
* dashboards.

---

# 115. Testes de Zoom

Verificar interfaces com aumento significativo de zoom.

Confirmar:

* ausência de conteúdo perdido;
* navegação funcional;
* controles acessíveis;
* ausência de sobreposição crítica.

---

# 116. Testes de Responsividade

Verificar:

* smartphone;
* tablet;
* notebook;
* desktop.

---

# 117. Testes de Formulários

Validar:

* labels;
* required;
* erros;
* help text;
* tabulação;
* foco;
* campos disabled;
* submit.

---

# 118. Testes de Componentes

Componentes reutilizáveis deverão ser testados antes de ampla adoção.

Um erro em componente compartilhado poderá afetar diversos módulos simultaneamente.

---

# 119. Evidências Arquiteturais

## EA-GDS-A11Y-001

O GereIgreja utiliza Django Templates como base de renderização.

## EA-GDS-A11Y-002

Bootstrap participa da infraestrutura visual.

## EA-GDS-A11Y-003

Font Awesome é amplamente utilizado na interface atual.

## EA-GDS-A11Y-004

A Área de Gestão utiliza `base_com_menu.html`.

## EA-GDS-A11Y-005

Dashboards Premium utilizam `dashboard_base.html`.

## EA-GDS-A11Y-006

A infraestrutura de dashboard utiliza `dashboard-sidebar.js`.

## EA-GDS-A11Y-007

HTMX é diretriz oficial para atualizações parciais e possui adoção progressiva.

## EA-GDS-A11Y-008

Alpine.js é diretriz para estados locais leves e possui adoção progressiva.

## EA-GDS-A11Y-009

Includes e partials representam o mecanismo predominante para fragmentos reutilizáveis.

## EA-GDS-A11Y-010

A estilização global do Design System é centralizada em `static/css/design_system.css`.

## EA-GDS-A11Y-011

A Administração Técnica baseada no Django Admin possui arquitetura distinta da Área de Gestão.

## EA-GDS-A11Y-012

O GDS já estabelece contraste, foco, teclado, responsividade e acessibilidade como requisitos transversais.

---

# 120. Especificações Oficiais

## GDS-A11Y-001

Toda funcionalidade essencial deverá ser operável por teclado.

## GDS-A11Y-002

Todo elemento interativo deverá possuir foco visível.

## GDS-A11Y-003

Todo campo de formulário deverá possuir identificação acessível.

## GDS-A11Y-004

Placeholder não deverá substituir label.

## GDS-A11Y-005

Estados não deverão depender exclusivamente de cor.

## GDS-A11Y-006

Imagens informativas deverão possuir texto alternativo adequado.

## GDS-A11Y-007

Imagens decorativas deverão ser ocultadas adequadamente das tecnologias assistivas.

## GDS-A11Y-008

Botões somente com ícones deverão possuir nome acessível.

## GDS-A11Y-009

Links deverão possuir destino compreensível.

## GDS-A11Y-010

Modais deverão controlar foco adequadamente.

## GDS-A11Y-011

Mensagens dinâmicas deverão considerar regiões live quando apropriado.

## GDS-A11Y-012

Tabelas deverão utilizar semântica apropriada quando apresentarem dados tabulares.

## GDS-A11Y-013

KPIs deverão possuir rótulos compreensíveis.

## GDS-A11Y-014

Gráficos não deverão ser o único meio de comunicar informação crítica.

## GDS-A11Y-015

A interface deverá permanecer utilizável em diferentes tamanhos de viewport.

## GDS-A11Y-016

A interface deverá suportar aumento de zoom sem perda crítica de funcionalidade.

## GDS-A11Y-017

Áreas de toque deverão possuir dimensões adequadas.

## GDS-A11Y-018

Customizações Bootstrap não deverão remover comportamentos importantes de acessibilidade.

## GDS-A11Y-019

HTMX não deverá causar perda desnecessária de foco ou contexto.

## GDS-A11Y-020

Alpine.js deverá preservar semântica, foco e teclado.

## GDS-A11Y-021

Regras de negócio deverão permanecer no backend.

## GDS-A11Y-022

Conteúdo não autorizado não deverá permanecer oculto apenas via CSS.

## GDS-A11Y-023

Mensagens de erro deverão explicar o problema de maneira compreensível.

## GDS-A11Y-024

Operações críticas deverão utilizar linguagem clara e controles acessíveis.

## GDS-A11Y-025

Animações deverão considerar redução de movimento quando aplicável.

## GDS-A11Y-026

Novos componentes reutilizáveis deverão ser avaliados quanto à acessibilidade antes da adoção ampla.

## GDS-A11Y-027

Páginas internas deverão manter estrutura de heading coerente.

## GDS-A11Y-028

A navegação deverá informar o item ou página atual quando apropriado.

## GDS-A11Y-029

A Administração Técnica e a Área de Gestão deverão preservar acessibilidade dentro de suas respectivas arquiteturas.

## GDS-A11Y-030

Acessibilidade deverá ser considerada requisito de qualidade e não melhoria opcional.

---

# 121. Checklist

## Estrutura

* [ ] HTML semântico;
* [ ] H1 existente;
* [ ] hierarquia de headings correta;
* [ ] landmarks adequados;
* [ ] conteúdo principal identificável.

## Navegação

* [ ] teclado;
* [ ] Tab;
* [ ] Shift + Tab;
* [ ] foco visível;
* [ ] item atual identificado;
* [ ] submenus acessíveis;
* [ ] breadcrumb compreensível.

## Formulários

* [ ] labels;
* [ ] campos obrigatórios;
* [ ] help text;
* [ ] erros;
* [ ] autocomplete quando apropriado;
* [ ] validação compreensível;
* [ ] foco após erro avaliado.

## Botões e Links

* [ ] semântica correta;
* [ ] texto claro;
* [ ] ícones possuem nome acessível;
* [ ] área de toque adequada;
* [ ] disabled compreensível.

## Cores

* [ ] contraste;
* [ ] Text Muted validado;
* [ ] estados semânticos legíveis;
* [ ] sem dependência exclusiva de cor.

## Imagens

* [ ] `alt` adequado;
* [ ] imagens decorativas tratadas;
* [ ] ícones decorativos ocultados quando necessário.

## Tabelas

* [ ] `table`;
* [ ] `thead`;
* [ ] `tbody`;
* [ ] `th`;
* [ ] cabeçalhos corretos;
* [ ] ordenação acessível;
* [ ] paginação acessível.

## Modais

* [ ] nome acessível;
* [ ] foco inicial;
* [ ] foco preso quando apropriado;
* [ ] ESC;
* [ ] fechamento acessível;
* [ ] retorno do foco.

## Feedback

* [ ] erros anunciáveis;
* [ ] alerts acessíveis;
* [ ] toasts não roubam foco;
* [ ] `aria-live` avaliado;
* [ ] mensagens compreensíveis.

## Dashboards

* [ ] KPIs possuem rótulos;
* [ ] gráficos possuem alternativa compreensível;
* [ ] filtros acessíveis;
* [ ] widgets utilizáveis por teclado;
* [ ] dados não dependem somente de cor.

## Responsividade

* [ ] smartphone;
* [ ] tablet;
* [ ] notebook;
* [ ] desktop;
* [ ] zoom;
* [ ] área de toque;
* [ ] sem conteúdo crítico cortado.

## Movimento

* [ ] animações discretas;
* [ ] `prefers-reduced-motion` avaliado;
* [ ] ausência de movimento essencial.

## Tecnologia

* [ ] Django Templates semânticos;
* [ ] Bootstrap customizado sem regressões;
* [ ] Font Awesome com tratamento acessível;
* [ ] HTMX preserva foco e contexto;
* [ ] Alpine.js preserva teclado e semântica;
* [ ] JavaScript não bloqueia funcionalidade fundamental.

## Segurança

* [ ] conteúdo não autorizado não está no DOM;
* [ ] permissões verificadas no backend;
* [ ] multi-tenant preservado;
* [ ] mensagens não revelam dados indevidos.

---

# 122. Governança

A acessibilidade deverá fazer parte da governança do GereIgreja Design System.

Mudanças em componentes compartilhados deverão ser avaliadas quanto a regressões.

São consideradas mudanças críticas:

* remoção de foco;
* alteração de contraste;
* mudança de semântica;
* alteração de navegação por teclado;
* introdução de novos dialogs;
* troca de bibliotecas;
* mudança na estrutura de headings;
* alteração em templates globais.

---

# 123. Roadmap

## Fase 1 — Consolidação

* revisar foco visível;
* revisar labels;
* revisar breadcrumbs;
* revisar botões somente com ícones;
* revisar contraste;
* revisar formulários existentes.

## Fase 2 — Navegação

* revisar sidebar por teclado;
* validar submenus;
* avaliar skip links;
* padronizar `aria-current`;
* validar áreas de toque.

## Fase 3 — Componentes

Auditar:

* cards;
* modais;
* alerts;
* toasts;
* tabelas;
* dashboards.

## Fase 4 — Atualizações Dinâmicas

Padronizar acessibilidade para:

* HTMX swaps;
* loading;
* mensagens;
* foco;
* regiões live.

## Fase 5 — Testes

Incorporar progressivamente testes de acessibilidade ao processo de qualidade.

## Fase 6 — Auditoria

Realizar auditorias periódicas das interfaces mais utilizadas.

Prioridade:

* Login;
* Dashboard;
* Secretaria;
* Financeiro;
* formulários;
* tabelas;
* navegação.

## Fase 7 — Evolução

Preparar os padrões para:

* PWA;
* aplicações móveis;
* Dark Mode;
* White Label;
* novos dispositivos.

Toda evolução deverá preservar os requisitos fundamentais deste documento.

---

# 124. Documentos Relacionados

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
* GDS-15 — Dashboards
* GDS-17 — Animações
* GDS-18 — Boas Práticas
* GDS-19 — Governança
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

# 125. Princípios Finais

A acessibilidade deverá fazer parte da definição de qualidade do GereIgreja.

Uma interface somente poderá ser considerada adequada quando o usuário conseguir:

```text
Encontrar
   ↓
Compreender
   ↓
Navegar
   ↓
Interagir
   ↓
Receber feedback
   ↓
Concluir sua tarefa
```

independentemente de utilizar mouse como forma principal de interação.

Os padrões deverão proteger especialmente os fluxos operacionais mais importantes da plataforma:

* cadastro de membros;
* navegação da Secretaria;
* operações financeiras;
* eventos;
* Escola Bíblica;
* comunicação;
* configurações;
* dashboards;
* relatórios.

O GereIgreja deverá evitar tratar acessibilidade como uma camada visual isolada.

Ela deverá estar presente em:

```text
Design
+
Templates
+
Componentes
+
CSS
+
JavaScript
+
Backend
+
Conteúdo
+
Testes
```

A adoção de Django Templates, Bootstrap, Font Awesome, HTMX ou Alpine.js não garante acessibilidade automaticamente.

Cada implementação deverá utilizar essas tecnologias de forma compatível com os princípios definidos neste documento.

O objetivo final é oferecer uma plataforma de gestão que permaneça clara, profissional, segura e utilizável para o maior número possível de pessoas.

---

# 126. Status do Documento

**Pasta**

`docs/design-system/`

**Arquivo**

`16-Acessibilidade.md`

**Documento**

`GDS-16`

**Código**

`GDS-A11Y`

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

**GDS-16 — Acessibilidade**
**GereIgreja Design System**
