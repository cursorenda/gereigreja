Pasta:
`docs/design-system/`

Arquivo:
`18-Boas-Praticas.md`

Documento:
GDS-18

Código:
GDS-BEST-PRACTICES

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

# GDS-18 — Boas Práticas

> "A qualidade visual do GereIgreja não depende apenas de bons componentes, mas da forma consistente como eles são escolhidos, combinados, reutilizados e evoluídos."

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia
4. Princípios Gerais
5. Reutilização Antes de Criação
6. Consistência entre Módulos
7. Design Tokens
8. Cores
9. Tipografia
10. Espaçamento
11. Grid
12. Iconografia
13. Botões
14. Formulários
15. Cards
16. Tabelas e Listagens
17. Modais
18. Alertas, Toasts e Feedback
19. Navegação
20. Dashboards
21. Acessibilidade
22. Animações
23. Área de Gestão
24. Administração Técnica
25. Portal Público
26. Templates Django
27. Herança de Templates
28. Includes e Partials
29. CSS
30. `design_system.css`
31. Bootstrap
32. Font Awesome
33. JavaScript
34. HTMX
35. Alpine.js
36. Progressive Enhancement
37. Responsividade
38. Mobile First
39. Estados da Interface
40. Loading
41. Estados Vazios
42. Estados de Erro
43. Estados de Sucesso
44. Permissões
45. Multi-Tenant
46. Segurança
47. Privacidade
48. Secretaria
49. Financeiro
50. Eventos
51. Escola Bíblica
52. Comunicação
53. Patrimônio
54. Relatórios
55. Configurações
56. Componentização
57. Nomenclatura
58. Redução de Duplicações
59. Separação de Responsabilidades
60. HTML Semântico
61. URLs
62. Django URL Names
63. Conteúdo
64. Terminologia
65. Operações Críticas
66. Dados Financeiros
67. Dados Pessoais
68. Performance
69. Testes Visuais
70. Testes Funcionais
71. Testes Responsivos
72. Testes de Acessibilidade
73. Testes de Permissão
74. Revisão de Pull Request
75. Critérios de Aceite
76. Dívida Visual
77. Refatoração
78. Compatibilidade
79. Depreciação
80. Anti-Patterns
81. Processo para Novos Componentes
82. Processo para Novos Padrões
83. Evidências Arquiteturais
84. Especificações Oficiais
85. Checklist Geral
86. Checklist por Componente
87. Checklist de Entrega
88. Governança
89. Roadmap
90. Documentos Relacionados
91. Princípios Finais
92. Status do Documento

---

# 1. Objetivo

Este documento consolida as boas práticas oficiais para utilização e evolução do GereIgreja Design System.

Os documentos anteriores definem os padrões específicos de:

* cores;
* tipografia;
* espaçamento;
* grid;
* iconografia;
* botões;
* formulários;
* cards;
* tabelas;
* modais;
* feedback;
* navegação;
* dashboards;
* acessibilidade;
* movimento.

O GDS-18 define como esses padrões deverão ser utilizados em conjunto durante o desenvolvimento cotidiano da plataforma.

Seu objetivo principal é reduzir:

* divergências visuais;
* componentes duplicados;
* estilos isolados;
* decisões arbitrárias;
* inconsistências entre módulos;
* retrabalho;
* dívida técnica de frontend.

---

# 2. Escopo

Este documento aplica-se a toda interface produzida ou mantida no GereIgreja.

Inclui:

* Área de Gestão;
* dashboards;
* Secretaria;
* Financeiro;
* Eventos;
* Escola Bíblica;
* Comunicação;
* Patrimônio;
* Relatórios;
* Configurações;
* Portal Público;
* Landing Pages;
* customizações da Administração Técnica quando aplicáveis.

---

# 3. Filosofia

A melhor decisão de frontend deverá ser, nesta ordem:

```text
Reutilizar
   ↓
Compor
   ↓
Estender
   ↓
Criar
```

Criar um novo padrão deverá ser a última opção.

O GereIgreja não deverá crescer por acumulação de soluções independentes.

Deverá evoluir por expansão controlada de uma linguagem comum.

---

# 4. Princípios Gerais

Toda interface deverá buscar:

* simplicidade;
* consistência;
* previsibilidade;
* acessibilidade;
* reutilização;
* clareza;
* segurança;
* responsividade;
* baixo custo de manutenção.

Uma solução tecnicamente funcional, mas visualmente inconsistente, não deverá ser considerada concluída.

---

# 5. Reutilização Antes de Criação

Antes de implementar qualquer componente, verificar:

```text
Existe componente oficial?
        ↓
SIM → reutilizar

NÃO
        ↓
Existe componente semelhante?
        ↓
SIM → compor ou estender

NÃO
        ↓
Existe necessidade recorrente?
        ↓
SIM → propor novo componente
```

Evitar criar componentes apenas porque uma tela possui pequenas diferenças de conteúdo.

---

# 6. Consistência entre Módulos

Secretaria, Financeiro, Eventos, Escola Bíblica, Comunicação, Patrimônio e demais módulos deverão compartilhar a mesma linguagem visual.

Exemplo:

```text
Salvar
```

deverá utilizar o mesmo padrão visual independentemente do módulo.

O mesmo princípio vale para:

* tabelas;
* filtros;
* modais;
* mensagens;
* cards;
* navegação;
* estados.

---

# 7. Design Tokens

Valores visuais reutilizáveis deverão vir dos tokens oficiais.

Não utilizar diretamente:

```css
color: #0D8281;
```

quando existir token correspondente.

Tokens deverão centralizar:

* cores;
* espaçamentos;
* tipografia;
* bordas;
* radius;
* sombras;
* movimento.

---

# 8. Cores

Utilizar exclusivamente a paleta oficial.

Cores institucionais:

```text
Brand 700 — #0D8281
Brand 900 — #0A6665
Brand Soft — #DFF4F3
```

Neutros:

```text
Background — #F1F5F9
Surface — #FFFFFF
Border — #D7E2E8
Text — #1E293B
Text Muted — #64748B
```

Semânticas:

```text
Success — #10B981
Warning — #D97706
Danger — #EF4444
```

Não criar paletas próprias por módulo.

---

# 9. Tipografia

A tipografia deverá seguir a escala oficial definida no GDS-04.

Evitar:

* fontes diferentes por página;
* tamanhos arbitrários;
* excesso de negrito;
* títulos visualmente inconsistentes;
* textos pequenos demais.

Hierarquia visual deverá corresponder à hierarquia do conteúdo.

---

# 10. Espaçamento

Utilizar a escala definida no GDS-05.

Evitar valores como:

```css
margin-top: 17px;
padding: 13px;
gap: 21px;
```

quando não fizerem parte dos tokens oficiais.

---

# 11. Grid

Utilizar o sistema de grid definido no GDS-06.

O GereIgreja utiliza como base o grid responsivo do Bootstrap.

Distribuições deverão respeitar a necessidade do conteúdo e não apenas aparência.

---

# 12. Iconografia

A implementação deverá utilizar a biblioteca realmente consolidada na aplicação.

Font Awesome está amplamente presente na interface atual e deverá continuar sendo reutilizado enquanto permanecer o padrão oficial da implementação.

Não introduzir bibliotecas paralelas sem decisão arquitetural.

Ícones não deverão substituir textos essenciais.

---

# 13. Botões

Aplicar o GDS-08.

Regra principal:

```text
Ação principal
→ Primary

Ação secundária
→ Secondary / Outline

Ação destrutiva
→ Danger
```

Evitar múltiplos botões primários disputando atenção.

---

# 14. Formulários

Aplicar o GDS-09.

Todo formulário deverá possuir:

* labels;
* agrupamentos lógicos;
* validação clara;
* mensagens próximas ao campo;
* responsividade;
* backend como validação final.

Evitar formulários excessivamente longos sem estrutura.

---

# 15. Cards

Aplicar o GDS-10.

Utilizar card quando:

* existe agrupamento visual claro;
* o conteúdo é relativamente independente;
* há valor em apresentar a informação como unidade.

Não transformar toda a interface em caixas.

---

# 16. Tabelas e Listagens

Aplicar o GDS-11.

Utilizar tabela quando o usuário precisa:

* comparar;
* ordenar;
* filtrar;
* analisar múltiplos registros.

Não substituir tabela por cards apenas por preferência estética.

---

# 17. Modais

Aplicar o GDS-12.

Utilizar modal para:

* ações rápidas;
* confirmações;
* edição pequena;
* visualização contextual.

Não utilizar modal para processos extensos.

---

# 18. Alertas, Toasts e Feedback

Aplicar o GDS-13.

Escolher o componente conforme o contexto.

```text
Erro de campo
→ inline

Aviso contextual
→ alert

Resultado breve
→ toast

Decisão obrigatória
→ modal
```

Evitar múltiplos mecanismos exibindo a mesma mensagem.

---

# 19. Navegação

Aplicar o GDS-14.

Páginas internas deverão preservar:

```text
Home > Módulo > Página
```

quando pertencentes à hierarquia padrão.

Sidebar e menu não deverão ser recriados por módulo.

---

# 20. Dashboards

Aplicar o GDS-15.

Dashboards deverão priorizar:

* informação relevante;
* KPIs úteis;
* atenção;
* análise;
* ações.

Não utilizar métricas apenas para preencher a tela.

---

# 21. Acessibilidade

Aplicar o GDS-16.

Todo componente deverá ser pensado desde o início para:

* teclado;
* foco;
* contraste;
* leitores de tela;
* touch;
* responsividade.

Acessibilidade não deverá ser adicionada apenas após a conclusão visual.

---

# 22. Animações

Aplicar o GDS-17.

Movimento deverá ser:

* curto;
* funcional;
* discreto;
* acessível.

Evitar animações decorativas na Área de Gestão.

---

# 23. Área de Gestão

A Área de Gestão possui infraestrutura própria e deverá reutilizar seus layouts compartilhados.

O principal layout administrativo utiliza:

`base_com_menu.html`

Páginas administrativas da aplicação não deverão ser confundidas com Django Admin.

---

# 24. Administração Técnica

A Administração Técnica utiliza Django Admin.

Essa interface possui:

* finalidade diferente;
* templates diferentes;
* fluxo diferente;
* estrutura de navegação própria.

Customizações deverão preservar essa separação arquitetural.

---

# 25. Portal Público

O Portal Público poderá possuir linguagem mais editorial, mas deverá manter:

* identidade do GereIgreja;
* paleta;
* tipografia;
* acessibilidade;
* responsividade.

Não deverá copiar diretamente a interface administrativa.

---

# 26. Templates Django

Templates deverão concentrar apresentação.

Regras complexas deverão permanecer em:

* views;
* services;
* models;
* forms;
* outras camadas apropriadas.

Evitar lógica de negócio dentro dos templates.

---

# 27. Herança de Templates

Reutilizar a arquitetura de herança oficial.

Exemplo:

```text
base.html
   ↓
base_com_menu.html
   ↓
dashboard_base.html
   ↓
Dashboard específico
```

Quando compatível com o contexto.

---

# 28. Includes e Partials

O GereIgreja utiliza includes e partials como estratégia predominante de reutilização de fragmentos de template.

Reutilizar estruturas existentes antes de criar HTML duplicado.

---

# 29. CSS

CSS deverá ser organizado por responsabilidade.

Evitar:

* estilos inline;
* duplicação;
* seletores excessivamente específicos;
* `!important` sem necessidade;
* regras específicas de página para componentes reutilizáveis.

---

# 30. `design_system.css`

A estilização global do Design System deverá permanecer centralizada em:

`static/css/design_system.css`

Alterações globais deverão ocorrer nessa infraestrutura ou nos arquivos oficiais relacionados.

Não criar uma segunda fonte de verdade para os tokens do GDS.

---

# 31. Bootstrap

Bootstrap fornece infraestrutura importante.

Deverá ser utilizado como base, não como identidade final.

O GDS possui precedência visual.

Evitar misturar aleatoriamente estilos nativos do Bootstrap com estilos customizados incompatíveis.

---

# 32. Font Awesome

Font Awesome está consolidado na implementação atual.

Reutilizar os ícones existentes.

Evitar trocar ícones equivalentes entre páginas sem necessidade.

Exemplo:

A ação de excluir deverá possuir iconografia consistente em toda a plataforma.

---

# 33. JavaScript

JavaScript deverá ser utilizado quando necessário para comportamentos reais.

Evitar JavaScript para:

* resolver espaçamento;
* aplicar cores;
* substituir CSS simples;
* duplicar comportamento do Bootstrap.

Scripts compartilhados deverão permanecer centralizados.

---

# 34. HTMX

HTMX deverá ser utilizado para atualizações parciais quando houver ganho real.

Casos apropriados:

* filtros;
* tabelas;
* paginação;
* modais;
* widgets;
* buscas;
* atualização de componentes.

Não utilizar HTMX apenas para transformar a aplicação em SPA.

---

# 35. Alpine.js

Alpine.js deverá ser utilizado para estado local leve.

Casos apropriados:

* mostrar/ocultar;
* dropdown;
* filtro;
* abas;
* pequenos painéis.

Regras de negócio continuarão sendo responsabilidade do backend.

---

# 36. Progressive Enhancement

A base funcional deverá permanecer no servidor.

Estratégia:

```text
Django
   ↓
HTML funcional
   ↓
CSS
   ↓
JavaScript
   ↓
HTMX / Alpine.js
   ↓
Experiência aprimorada
```

A camada adicional não deverá destruir a funcionalidade principal.

---

# 37. Responsividade

Toda interface deverá ser testada em:

* desktop;
* notebook;
* tablet;
* smartphone.

Responsividade significa reorganizar conteúdo, não apenas reduzir tamanhos.

---

# 38. Mobile First

Sempre que possível, considerar desde o início o comportamento em telas pequenas.

Perguntas fundamentais:

```text
O que é essencial?

O que pode empilhar?

O que pode ser simplificado?

Onde ficam as ações?
```

---

# 39. Estados da Interface

Componentes deverão considerar:

```text
Default
Hover
Focus
Active
Disabled
Loading
Empty
Error
Success
```

quando aplicável.

Uma interface que funciona apenas no estado ideal está incompleta.

---

# 40. Loading

Loading deverá representar operação real.

Quando um componente independente carregar, preferir loading local em vez de bloquear toda a página.

---

# 41. Estados Vazios

Estado vazio deverá informar:

* que não existem dados;
* o que isso significa;
* qual ação pode ser executada.

Exemplo:

```text
Nenhum evento cadastrado.

[Adicionar evento]
```

---

# 42. Estados de Erro

Mensagens deverão ser:

* contextualizadas;
* claras;
* não técnicas;
* acionáveis quando possível.

---

# 43. Estados de Sucesso

Sucesso deverá ser apresentado somente após confirmação real da operação.

Não mostrar sucesso antes da resposta do backend.

---

# 44. Permissões

Interface deverá respeitar permissões.

Entretanto:

```text
Ocultar botão
≠
Autorizar operação
```

Toda autorização deverá ser validada no backend.

---

# 45. Multi-Tenant

O isolamento organizacional deverá ocorrer no servidor.

Nenhum componente deverá receber dados de outro contexto e apenas escondê-los visualmente.

---

# 46. Segurança

Frontend deverá ser considerado interface, não camada de segurança.

Não confiar em:

* JavaScript;
* campos hidden;
* botão invisível;
* URL não exibida;
* CSS.

para impedir operações não autorizadas.

---

# 47. Privacidade

Exibir somente dados necessários ao contexto.

Evitar exposição excessiva de:

* CPF;
* contatos;
* informações financeiras;
* informações pessoais;
* dados administrativos.

---

# 48. Secretaria

A Secretaria deverá priorizar:

* produtividade;
* leitura rápida;
* formulários claros;
* tabelas eficientes;
* busca;
* filtros;
* cadastros consistentes.

Não criar linguagem visual própria para o módulo.

---

# 49. Financeiro

O Financeiro deverá priorizar:

* precisão;
* segurança;
* clareza de valores;
* períodos;
* status;
* operações críticas.

Receita, despesa, estorno, cancelamento e exclusão deverão possuir terminologia distinta.

---

# 50. Eventos

O módulo de Eventos deverá manter:

* datas legíveis;
* horários;
* status;
* local;
* ações contextuais.

Cards poderão ser adequados para visão editorial; tabelas poderão ser melhores para gestão operacional.

---

# 51. Escola Bíblica

O módulo deverá preservar consistência na apresentação de:

* turmas;
* alunos;
* professores;
* frequência;
* horários.

---

# 52. Comunicação

Estados de comunicação deverão ser explícitos.

Exemplos:

```text
Rascunho
Agendado
Enviado
Falha
```

Não comunicar `Agendado` como `Enviado`.

---

# 53. Patrimônio

Aplicar os mesmos padrões de:

* formulários;
* tabelas;
* cards;
* filtros;
* estados.

Evitar componentes específicos quando os existentes forem suficientes.

---

# 54. Relatórios

Relatórios deverão priorizar:

* legibilidade;
* organização;
* impressão;
* contexto temporal;
* dados precisos.

Não utilizar dashboard como substituto de relatório completo.

---

# 55. Configurações

Configurações deverão ser agrupadas por responsabilidade.

Evitar telas enormes com dezenas de campos sem separação.

---

# 56. Componentização

Todo componente reutilizável deverá possuir:

```text
Responsabilidade clara
+
Interface previsível
+
Estados definidos
+
Acessibilidade
+
Responsividade
```

---

# 57. Nomenclatura

Nomes de componentes, classes e arquivos deverão refletir finalidade.

Preferir:

```text
member-table
dashboard-kpi
form-error
```

a nomes vagos como:

```text
box1
content2
custom-item
```

Os nomes efetivos deverão seguir as convenções existentes no projeto.

---

# 58. Redução de Duplicações

Duplicação deverá ser tratada como sinal de oportunidade de componentização.

Se duas ou mais páginas repetirem:

* HTML;
* CSS;
* JavaScript;
* estados;

avaliar extração para componente compartilhado.

---

# 59. Separação de Responsabilidades

Cada tecnologia deverá permanecer no seu papel principal.

```text
Django
→ dados, regras, autorização

Template
→ estrutura

CSS
→ apresentação

JavaScript
→ comportamento

HTMX
→ atualização servidor-interface

Alpine.js
→ estado local
```

---

# 60. HTML Semântico

Utilizar elementos conforme finalidade.

Exemplos:

```text
Link
→ navegação

Button
→ ação

Table
→ dados tabulares

Heading
→ hierarquia
```

Evitar `div` para tudo.

---

# 61. URLs

URLs deverão ser previsíveis e estáveis.

Evitar alterar rotas sem necessidade.

Deep links deverão permanecer utilizáveis quando o usuário possuir permissão.

---

# 62. Django URL Names

Templates deverão preferir:

```django
{% url 'home' %}
```

em vez de caminhos hardcoded.

---

# 63. Conteúdo

A interface deverá utilizar textos curtos e objetivos.

Evitar termos técnicos destinados à equipe de desenvolvimento.

---

# 64. Terminologia

Uma mesma ação deverá possuir o mesmo nome em toda a plataforma.

Exemplo:

Se a operação chama-se:

```text
Salvar
```

não alternar arbitrariamente com:

```text
Gravar
Persistir
Registrar
Confirmar
```

quando significarem a mesma coisa.

---

# 65. Operações Críticas

Operações destrutivas deverão possuir:

* Danger;
* texto claro;
* confirmação quando necessária;
* autorização backend;
* feedback final.

---

# 66. Dados Financeiros

Valores monetários deverão utilizar:

```text
R$ 1.250,00
```

Não utilizar `float` no backend quando puder causar imprecisão financeira.

O Design System deverá apresentar o valor de forma consistente; a regra de persistência pertence à arquitetura backend.

---

# 67. Dados Pessoais

Dados pessoais deverão ser exibidos somente quando relevantes.

Tabelas de membros não deverão apresentar todas as informações disponíveis apenas porque existem no banco.

---

# 68. Performance

Interfaces deverão evitar:

* DOM excessivo;
* scripts repetidos;
* requests desnecessários;
* imagens grandes;
* tabelas enormes sem paginação;
* bibliotecas redundantes;
* atualizações completas sem necessidade.

---

# 69. Testes Visuais

Verificar cada componente com:

* conteúdo curto;
* conteúdo longo;
* ausência de conteúdo;
* loading;
* erro;
* responsividade.

---

# 70. Testes Funcionais

Testar os fluxos reais.

Exemplo:

```text
Abrir
→ editar
→ validar
→ salvar
→ receber feedback
→ atualizar contexto
```

---

# 71. Testes Responsivos

Testar pelo menos:

```text
Desktop
Notebook
Tablet
Smartphone
```

Não considerar apenas o DevTools em uma única largura.

---

# 72. Testes de Acessibilidade

Verificar:

* teclado;
* foco;
* contraste;
* labels;
* ARIA;
* leitores de tela quando possível;
* reduced motion.

---

# 73. Testes de Permissão

Validar diferentes perfis de usuário.

Não testar apenas com conta administrativa.

---

# 74. Revisão de Pull Request

Alterações de frontend deverão ser avaliadas também sob perspectiva do GDS.

Perguntas recomendadas:

```text
Reutiliza componente?

Está consistente?

Está acessível?

Está responsivo?

Introduz novo padrão?

Há duplicação?

Há impacto global?
```

---

# 75. Critérios de Aceite

Uma interface somente deverá ser considerada pronta quando cumprir:

* requisito funcional;
* Design System;
* responsividade;
* acessibilidade;
* segurança;
* permissões;
* estados;
* testes.

---

# 76. Dívida Visual

Diferenças visuais acumuladas deverão ser tratadas como dívida técnica.

Exemplos:

* botões diferentes para mesma ação;
* múltiplos estilos de tabela;
* cores divergentes;
* modais inconsistentes;
* formulários com padrões distintos.

---

# 77. Refatoração

Quando um componente legado for alterado significativamente, avaliar sua adaptação ao GDS.

Não é necessário reescrever toda a plataforma de uma só vez.

A evolução poderá ser incremental.

---

# 78. Compatibilidade

Mudanças em componentes globais deverão considerar todos os consumidores.

Antes de alterar:

* botão;
* card;
* tabela;
* modal;
* sidebar;
* dashboard;

avaliar impacto transversal.

---

# 79. Depreciação

Quando um componente antigo for substituído:

```text
Novo padrão aprovado
      ↓
Componente legado marcado
      ↓
Novos usos bloqueados
      ↓
Migração gradual
      ↓
Remoção
```

Evitar manter duas soluções oficiais indefinidamente.

---

# 80. Anti-Patterns

Evitar:

* CSS inline;
* cores hardcoded;
* componentes duplicados;
* JavaScript copiado entre páginas;
* múltiplas bibliotecas de ícones;
* novas fontes arbitrárias;
* novo grid paralelo;
* lógica de negócio em template;
* autorização somente no frontend;
* dados multi-tenant filtrados apenas na interface;
* botões primários em excesso;
* formulários sem labels;
* tabela substituída por card sem motivo;
* modal para processo extenso;
* toast para erro de campo;
* animação sem finalidade;
* dashboard com métricas irrelevantes;
* breadcrumb ausente;
* sidebar diferente por módulo;
* estilos específicos sem documentação;
* HTMX usado como SPA improvisada;
* Alpine.js usado para regra de negócio.

---

# 81. Processo para Novos Componentes

Antes de criar um novo componente, documentar:

```text
Problema

Casos de uso

Por que os componentes atuais não atendem

Estrutura

Estados

Responsividade

Acessibilidade

Dependências

Impacto
```

---

# 82. Processo para Novos Padrões

Um novo padrão de Design System deverá existir somente quando:

1. resolver problema recorrente;
2. possuir aplicação em mais de um contexto ou justificar claramente sua especificidade;
3. ser compatível com o GDS;
4. preservar acessibilidade;
5. possuir implementação sustentável;
6. ser documentado;
7. ser aprovado pela Engenharia.

---

# 83. Evidências Arquiteturais

## EA-GDS-BP-001

Django Templates permanecem como base de renderização da Área de Gestão.

## EA-GDS-BP-002

`base_com_menu.html` representa a principal infraestrutura de layout da Área de Gestão.

## EA-GDS-BP-003

Dashboards Premium utilizam `dashboard_base.html`.

## EA-GDS-BP-004

Existe infraestrutura compartilhada em `dashboard-sidebar.js`.

## EA-GDS-BP-005

Bootstrap participa da estrutura frontend.

## EA-GDS-BP-006

Font Awesome está amplamente presente na implementação atual.

## EA-GDS-BP-007

HTMX constitui diretriz oficial para atualizações parciais com adoção progressiva.

## EA-GDS-BP-008

Alpine.js constitui diretriz para estados locais leves com adoção progressiva.

## EA-GDS-BP-009

Includes e partials são mecanismos predominantes de reutilização de fragmentos HTML.

## EA-GDS-BP-010

`static/css/design_system.css` centraliza a estilização global do Design System.

## EA-GDS-BP-011

A Área de Gestão e o Django Admin possuem arquiteturas distintas.

## EA-GDS-BP-012

A plataforma possui múltiplos módulos que devem compartilhar a mesma linguagem visual.

---

# 84. Especificações Oficiais

## GDS-BP-001

Reutilização deverá ser preferida à criação de novos componentes.

## GDS-BP-002

Componentes equivalentes deverão possuir aparência e comportamento equivalentes.

## GDS-BP-003

Todo estilo global deverá utilizar tokens oficiais quando disponíveis.

## GDS-BP-004

Não deverão existir cores hardcoded em componentes reutilizáveis.

## GDS-BP-005

Não deverão existir estilos inline sem necessidade técnica justificada.

## GDS-BP-006

A Área de Gestão deverá reutilizar sua infraestrutura oficial de layouts.

## GDS-BP-007

A Administração Técnica não deverá ser confundida com a Área de Gestão.

## GDS-BP-008

Bootstrap deverá funcionar como infraestrutura e não substituir o GDS.

## GDS-BP-009

Font Awesome deverá permanecer consistente enquanto for a biblioteca consolidada.

## GDS-BP-010

HTMX deverá ser utilizado para atualizações parciais quando houver benefício real.

## GDS-BP-011

Alpine.js deverá ser utilizado somente para estados locais leves.

## GDS-BP-012

Regras de negócio deverão permanecer fora dos templates.

## GDS-BP-013

Autorização deverá ser validada no backend.

## GDS-BP-014

Isolamento multi-tenant deverá ser aplicado no backend.

## GDS-BP-015

Interfaces deverão possuir estados de loading, erro e vazio quando aplicáveis.

## GDS-BP-016

Toda interface deverá ser responsiva.

## GDS-BP-017

Toda interface deverá considerar acessibilidade.

## GDS-BP-018

Novos componentes deverão possuir estados documentados.

## GDS-BP-019

Componentes compartilhados deverão ser testados em múltiplos módulos.

## GDS-BP-020

Mudanças globais deverão avaliar impacto transversal.

## GDS-BP-021

Novos padrões deverão ser documentados antes da adoção ampla.

## GDS-BP-022

Componentes legados deverão ser migrados gradualmente quando modificados.

## GDS-BP-023

A plataforma deverá evitar múltiplas soluções oficiais para o mesmo problema.

## GDS-BP-024

Progressive Enhancement deverá orientar interações avançadas.

## GDS-BP-025

A implementação deverá preservar consistência entre módulos.

---

# 85. Checklist Geral

## Design System

* [ ] utiliza GDS;
* [ ] utiliza tokens;
* [ ] cores oficiais;
* [ ] tipografia oficial;
* [ ] espaçamento oficial;
* [ ] grid oficial;
* [ ] iconografia consistente.

## Componentes

* [ ] componente existente foi avaliado;
* [ ] não há duplicação;
* [ ] estados definidos;
* [ ] responsividade;
* [ ] acessibilidade;
* [ ] conteúdo variável suportado.

## Templates

* [ ] herança correta;
* [ ] includes reutilizados;
* [ ] partials reutilizadas;
* [ ] sem lógica de negócio complexa;
* [ ] URLs nomeadas.

## CSS

* [ ] sem hardcode desnecessário;
* [ ] sem inline desnecessário;
* [ ] tokens utilizados;
* [ ] `design_system.css` respeitado;
* [ ] sem `!important` arbitrário.

## JavaScript

* [ ] realmente necessário;
* [ ] sem duplicação;
* [ ] infraestrutura compartilhada reutilizada;
* [ ] sem regra de negócio;
* [ ] acessível.

## HTMX

* [ ] ganho real;
* [ ] loading;
* [ ] erro;
* [ ] foco;
* [ ] contexto;
* [ ] URL quando apropriado.

## Alpine.js

* [ ] estado local;
* [ ] sem regra de domínio;
* [ ] teclado;
* [ ] ARIA;
* [ ] fallback funcional.

## Segurança

* [ ] permissões backend;
* [ ] multi-tenant;
* [ ] dados pessoais;
* [ ] dados financeiros;
* [ ] sem exposição técnica.

## Responsividade

* [ ] desktop;
* [ ] notebook;
* [ ] tablet;
* [ ] smartphone;
* [ ] touch.

## Acessibilidade

* [ ] teclado;
* [ ] foco;
* [ ] contraste;
* [ ] labels;
* [ ] semântica;
* [ ] leitor de tela quando aplicável;
* [ ] reduced motion.

---

# 86. Checklist por Componente

## Botão

* [ ] variante correta;
* [ ] uma ação primária;
* [ ] Danger para destrutivo;
* [ ] loading;
* [ ] disabled;
* [ ] foco;
* [ ] nome acessível.

## Formulário

* [ ] labels;
* [ ] required;
* [ ] erros;
* [ ] preservação dos dados;
* [ ] backend valida;
* [ ] responsive.

## Card

* [ ] propósito;
* [ ] sem excesso de conteúdo;
* [ ] estado vazio;
* [ ] loading;
* [ ] ação clara;
* [ ] não substitui tabela indevidamente.

## Tabela

* [ ] colunas necessárias;
* [ ] filtros;
* [ ] busca;
* [ ] paginação;
* [ ] ações;
* [ ] mobile;
* [ ] semântica.

## Modal

* [ ] realmente necessário;
* [ ] título;
* [ ] foco;
* [ ] fechamento;
* [ ] teclado;
* [ ] confirmação para ação crítica.

## Feedback

* [ ] canal correto;
* [ ] mensagem clara;
* [ ] sem duplicação;
* [ ] sem detalhes técnicos;
* [ ] resultado confirmado.

## Dashboard

* [ ] métricas relevantes;
* [ ] período;
* [ ] permissões;
* [ ] grid;
* [ ] estados;
* [ ] links para detalhamento.

---

# 87. Checklist de Entrega

Antes de considerar uma interface pronta:

* [ ] requisito funcional atendido;
* [ ] GDS aplicado;
* [ ] componente reutilizado;
* [ ] comportamento testado;
* [ ] erros testados;
* [ ] loading testado;
* [ ] estado vazio testado;
* [ ] permissões testadas;
* [ ] multi-tenant testado;
* [ ] responsividade testada;
* [ ] teclado testado;
* [ ] foco testado;
* [ ] contraste revisado;
* [ ] CSS revisado;
* [ ] JavaScript revisado;
* [ ] URLs revisadas;
* [ ] nomenclatura consistente;
* [ ] documentação atualizada quando necessário.

---

# 88. Governança

O GDS-18 funciona como referência operacional para utilização dos demais documentos do Design System.

A governança formal será definida pelo GDS-19.

Toda decisão local deverá respeitar primeiro os padrões existentes.

A exceção deverá ser:

* consciente;
* justificada;
* limitada;
* documentada.

---

# 89. Roadmap

## Fase 1 — Auditoria

* identificar divergências;
* mapear componentes duplicados;
* identificar estilos inline;
* localizar cores hardcoded;
* revisar bibliotecas duplicadas.

## Fase 2 — Consolidação

* centralizar tokens;
* padronizar componentes;
* eliminar duplicações;
* consolidar includes e partials.

## Fase 3 — Qualidade

Integrar verificações de:

* acessibilidade;
* responsividade;
* estados;
* segurança;
* consistência visual.

## Fase 4 — Componentização

Expandir progressivamente a biblioteca interna de componentes.

Priorizar:

* alto reuso;
* alta frequência;
* alto impacto visual.

## Fase 5 — Progressive Enhancement

Expandir HTMX e Alpine.js somente nos pontos onde houver benefício comprovado.

## Fase 6 — Governança

Implementar o processo formal definido no GDS-19.

---

# 90. Documentos Relacionados

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
* GDS-16 — Acessibilidade
* GDS-17 — Animações e Movimento
* GDS-19 — Governança
* GFE-01 — Frontend Architecture
* GFE-02 — Estrutura de Pastas
* GFE-03 — Componentes
* GFE-04 — Layouts
* GFE-05 — Templates
* GFE-06 — Assets
* GFE-07 — CSS
* GFE-08 — JavaScript
* GFE-09 — HTMX
* GFE-10 — Alpine.js
* GFE-11 — Dashboards

---

# 91. Princípios Finais

As boas práticas do GereIgreja deverão transformar o Design System em uma disciplina de desenvolvimento, e não apenas em um catálogo visual.

A sequência recomendada para qualquer decisão de frontend é:

```text
Compreender o problema
        ↓
Consultar o GDS
        ↓
Localizar componente existente
        ↓
Reutilizar
        ↓
Compor
        ↓
Estender quando necessário
        ↓
Criar somente como última opção
        ↓
Testar
        ↓
Documentar
```

A plataforma deverá evitar que cada módulo desenvolva sua própria linguagem.

Secretaria, Financeiro, Eventos, Escola Bíblica, Comunicação, Patrimônio, Relatórios e Configurações fazem parte de uma única experiência.

Django Templates deverão continuar oferecendo a base estrutural.

Bootstrap deverá permanecer como infraestrutura visual onde apropriado.

Font Awesome deverá permanecer consistente com a implementação atual.

HTMX deverá evoluir as atualizações parciais sem transformar o projeto em uma SPA improvisada.

Alpine.js deverá complementar apenas estados locais.

`static/css/design_system.css` deverá permanecer como referência central da identidade visual.

Acessibilidade, responsividade, segurança e multi-tenant deverão ser requisitos transversais.

O objetivo final do GDS-18 é garantir que cada nova tela do GereIgreja pareça inevitavelmente parte do mesmo produto.

---

# 92. Status do Documento

**Pasta**

`docs/design-system/`

**Arquivo**

`18-Boas-Praticas.md`

**Documento**

`GDS-18`

**Código**

`GDS-BEST-PRACTICES`

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

**GDS-18 — Boas Práticas**
**GereIgreja Design System**
