Pasta:
`docs/design-system/`

Arquivo:
`19-Governanca.md`

Documento:
GDS-19

Código:
GDS-GOVERNANCE

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

# GDS-19 — Governança

> "Um Design System só permanece confiável quando sua evolução é controlada. No GereIgreja, consistência visual, arquitetura frontend e qualidade de experiência devem evoluir sob regras claras de responsabilidade, aprovação, versionamento e compatibilidade."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel da Governança
4. Princípios
5. Estrutura de Responsabilidade
6. Responsável pelo GDS
7. Responsabilidade da Engenharia
8. Responsabilidade dos Módulos
9. Fonte Oficial
10. Hierarquia dos Documentos
11. Ciclo de Vida do GDS
12. Proposição
13. Análise
14. Aprovação
15. Implementação
16. Validação
17. Documentação
18. Publicação
19. Monitoramento
20. Evolução
21. Tipos de Alteração
22. Alteração Corretiva
23. Alteração Compatível
24. Alteração Evolutiva
25. Breaking Change
26. Versionamento
27. Versão Major
28. Versão Minor
29. Versão Patch
30. Changelog
31. Compatibilidade
32. Compatibilidade Retroativa
33. Componentes Legados
34. Depreciação
35. Remoção
36. Migração
37. Tokens
38. Governança de Cores
39. Governança de Tipografia
40. Governança de Espaçamento
41. Governança de Grid
42. Governança de Iconografia
43. Governança de Componentes
44. Botões
45. Formulários
46. Cards
47. Tabelas
48. Modais
49. Feedback
50. Navegação
51. Dashboards
52. Acessibilidade
53. Movimento
54. `design_system.css`
55. Templates Compartilhados
56. `base.html`
57. `base_com_menu.html`
58. `menu.html`
59. `dashboard_base.html`
60. JavaScript Compartilhado
61. `dashboard-sidebar.js`
62. Bootstrap
63. Font Awesome
64. HTMX
65. Alpine.js
66. Django Templates
67. Progressive Enhancement
68. Pull Requests
69. Revisão Visual
70. Revisão Arquitetural
71. Revisão de Acessibilidade
72. Revisão de Segurança
73. Revisão de Responsividade
74. Critérios de Aceite
75. Exceções
76. Processo de Exceção
77. Exceções Temporárias
78. Exceções Permanentes
79. Documentação de Exceções
80. Multi-Tenant
81. Permissões
82. Segurança
83. Privacidade
84. Secretaria
85. Financeiro
86. Eventos
87. Escola Bíblica
88. Comunicação
89. Patrimônio
90. Relatórios
91. Administração
92. Portal Público
93. Auditoria
94. Auditoria Visual
95. Auditoria Técnica
96. Auditoria de Acessibilidade
97. Auditoria de Componentes
98. Métricas
99. Dívida Visual
100. Dívida Técnica
101. Matriz de Responsabilidade
102. Processo para Novo Componente
103. Processo para Novo Token
104. Processo para Nova Variante
105. Processo para Nova Biblioteca
106. Processo para Alteração Global
107. Processo para Breaking Change
108. Evidências Arquiteturais
109. Especificações Oficiais
110. Checklist de Governança
111. Checklist de Release
112. Roadmap
113. Documentos Relacionados
114. Princípios Finais
115. Status do Documento

---

# 1. Objetivo

Este documento define a governança oficial do GereIgreja Design System.

Seu objetivo é estabelecer como o GDS deverá ser:

* mantido;
* revisado;
* alterado;
* versionado;
* aprovado;
* implementado;
* documentado;
* auditado;
* evoluído.

O GDS-19 encerra a sequência principal do Design System e transforma os documentos anteriores em uma disciplina formal de engenharia.

---

# 2. Escopo

Este documento aplica-se a toda alteração que possa afetar a experiência visual ou estrutural da plataforma.

Inclui:

* Design Tokens;
* componentes;
* templates;
* estilos globais;
* bibliotecas frontend;
* padrões de interação;
* navegação;
* dashboards;
* acessibilidade;
* responsividade;
* movimento;
* infraestrutura compartilhada.

Aplica-se à:

* Área de Gestão;
* Portal Público;
* Landing Pages;
* customizações da Administração Técnica quando relacionadas ao GDS.

---

# 3. Papel da Governança

O objetivo da governança é impedir que o Design System se fragmente ao longo do crescimento da plataforma.

Sem governança, o projeto tende a acumular:

```text id="m3n9va"
Novo módulo
    ↓
Nova solução visual
    ↓
Nova classe CSS
    ↓
Novo componente
    ↓
Nova convenção
    ↓
Inconsistência
```

A governança deverá produzir o fluxo oposto:

```text id="3k1r6t"
Nova necessidade
      ↓
Consultar GDS
      ↓
Reutilizar
      ↓
Estender quando necessário
      ↓
Documentar
      ↓
Aprovar
      ↓
Implementar
```

---

# 4. Princípios

A governança deverá seguir:

* consistência;
* rastreabilidade;
* responsabilidade;
* compatibilidade;
* simplicidade;
* evolução controlada;
* documentação;
* segurança;
* acessibilidade;
* sustentabilidade.

---

# 5. Estrutura de Responsabilidade

A governança deverá possuir uma fonte clara de responsabilidade.

Estrutura conceitual:

```text id="au13bk"
Equipe de Engenharia
        │
        ├── Arquitetura
        ├── Design System
        ├── Frontend
        ├── Qualidade
        └── Segurança
```

Alterações globais não deverão depender exclusivamente da decisão isolada de um módulo.

---

# 6. Responsável pelo GDS

A responsabilidade formal pelo GDS é da:

```text id="vqm6fe"
Equipe de Engenharia
```

Isso inclui:

* manutenção dos documentos;
* aprovação de padrões;
* revisão de componentes;
* aprovação de breaking changes;
* controle de versionamento;
* auditorias.

---

# 7. Responsabilidade da Engenharia

A Engenharia deverá:

* preservar consistência;
* manter infraestrutura compartilhada;
* evitar duplicações;
* revisar novos padrões;
* documentar decisões;
* validar acessibilidade;
* validar compatibilidade;
* orientar migrações.

---

# 8. Responsabilidade dos Módulos

Cada módulo poderá criar conteúdo e funcionalidade específicos.

Entretanto, não deverá criar de forma independente:

* nova paleta;
* novo grid;
* nova tipografia;
* novo padrão de botão;
* novo sistema de modal;
* novo sistema de toast;
* nova sidebar;
* nova linguagem de dashboard.

Módulos deverão especializar conteúdo, não reinventar infraestrutura.

---

# 9. Fonte Oficial

O Design System deverá possuir uma única fonte oficial de documentação.

Estrutura:

```text id="ow1vjq"
docs/design-system/
```

Essa pasta deverá concentrar os documentos GDS.

---

# 10. Hierarquia dos Documentos

Os documentos deverão ser interpretados de forma complementar.

Exemplo:

```text id="3q69rk"
GDS-01
   ↓
Fundamentos

GDS-03 a GDS-07
   ↓
Tokens e base visual

GDS-08 a GDS-15
   ↓
Componentes

GDS-16 e GDS-17
   ↓
Requisitos transversais

GDS-18
   ↓
Boas práticas

GDS-19
   ↓
Governança
```

---

# 11. Ciclo de Vida do GDS

Toda evolução relevante deverá seguir:

```text id="kkr260"
Proposição
   ↓
Análise
   ↓
Aprovação
   ↓
Implementação
   ↓
Validação
   ↓
Documentação
   ↓
Publicação
   ↓
Monitoramento
```

---

# 12. Proposição

Uma proposta deverá existir quando houver necessidade de:

* novo componente;
* novo token;
* nova variante;
* nova tecnologia frontend;
* alteração global;
* depreciação;
* breaking change.

---

# 13. Análise

A análise deverá responder:

```text id="2rpjjr"
O problema é recorrente?

Existe solução já disponível?

Pode ser resolvido por composição?

Qual o impacto?

Existe risco de regressão?

Afeta acessibilidade?

Afeta segurança?

Afeta múltiplos módulos?
```

---

# 14. Aprovação

Alterações globais deverão ser aprovadas pela Engenharia antes da adoção em larga escala.

Alterações locais que reutilizem padrões existentes não necessitam criar processo de aprovação específico do GDS.

---

# 15. Implementação

A implementação deverá seguir a documentação aprovada.

Não deverá existir divergência deliberada entre:

```text id="dfgaxc"
Documentação
≠
Implementação
```

Quando houver diferença, uma das duas deverá ser corrigida.

---

# 16. Validação

Toda alteração global deverá ser verificada quanto a:

* visual;
* funcionalidade;
* acessibilidade;
* responsividade;
* compatibilidade;
* performance;
* segurança.

---

# 17. Documentação

Alterações relevantes deverão atualizar:

* documento do componente;
* versão;
* changelog quando aplicável;
* exemplos;
* regras;
* migração.

---

# 18. Publicação

Um padrão somente deverá ser considerado oficial após:

```text id="f4youp"
Aprovação
+
Implementação
+
Validação
+
Documentação
```

---

# 19. Monitoramento

Após adoção, deverá ser observado:

* regressões;
* duplicações;
* dificuldades de uso;
* inconsistências;
* impacto nos módulos.

---

# 20. Evolução

O GDS deverá evoluir de maneira contínua, porém controlada.

Estabilidade não significa imobilidade.

---

# 21. Tipos de Alteração

As alterações deverão ser classificadas.

```text id="gxjaek"
Corrective
Compatible
Evolutionary
Breaking
```

---

# 22. Alteração Corretiva

Corrige problema sem alterar contrato do componente.

Exemplos:

* contraste;
* foco;
* pequeno erro visual;
* bug de responsividade.

---

# 23. Alteração Compatível

Adiciona comportamento sem quebrar usos existentes.

Exemplo:

```text id="hlu6y7"
Card
+
nova opção opcional
```

---

# 24. Alteração Evolutiva

Representa ampliação significativa, mas ainda com estratégia de compatibilidade.

Exemplo:

* nova variante;
* nova composição;
* novo estado.

---

# 25. Breaking Change

É qualquer alteração que exija modificação dos consumidores existentes.

Exemplos:

* remoção de classe;
* alteração de markup obrigatório;
* mudança de API de componente;
* alteração de token removido;
* nova assinatura JavaScript incompatível.

Breaking changes deverão possuir plano de migração.

---

# 26. Versionamento

O GDS deverá utilizar versionamento semântico como referência conceitual:

```text id="tj8op0"
MAJOR.MINOR.PATCH
```

Exemplo:

```text id="47qn7m"
1.4.2
```

---

# 27. Versão Major

Aumentar quando houver breaking changes relevantes.

Exemplo:

```text id="bgh81r"
1.x.x
↓
2.0.0
```

---

# 28. Versão Minor

Aumentar quando houver nova funcionalidade compatível.

Exemplo:

```text id="ysqkxl"
1.2.0
↓
1.3.0
```

---

# 29. Versão Patch

Aumentar para correções compatíveis.

Exemplo:

```text id="c2qhrr"
1.3.1
↓
1.3.2
```

---

# 30. Changelog

Alterações relevantes deverão possuir histórico.

O changelog deverá informar:

* versão;
* data;
* alteração;
* impacto;
* migração quando aplicável.

---

# 31. Compatibilidade

A compatibilidade deverá ser considerada antes de qualquer alteração global.

Pergunta obrigatória:

```text id="32eoex"
Quais módulos utilizam este componente?
```

---

# 32. Compatibilidade Retroativa

Sempre que possível, novas versões deverão preservar usos existentes.

Quando isso não for possível, utilizar depreciação antes da remoção.

---

# 33. Componentes Legados

Componentes legados poderão continuar existindo temporariamente.

Entretanto, novos usos deverão preferir o padrão atual.

---

# 34. Depreciação

Fluxo:

```text id="dw3ukt"
Componente existente
       ↓
Novo padrão aprovado
       ↓
Componente marcado como deprecated
       ↓
Novos usos proibidos
       ↓
Migração gradual
```

---

# 35. Remoção

A remoção somente deverá ocorrer após:

* identificação dos consumidores;
* migração;
* testes;
* documentação;
* validação.

---

# 36. Migração

Mudanças que afetem consumidores deverão possuir orientação.

Exemplo:

```text id="50wf40"
Antes

classe antiga

Depois

classe oficial
```

---

# 37. Tokens

Design Tokens possuem impacto global e deverão possuir governança rigorosa.

Nenhum módulo deverá criar escala paralela de:

* cores;
* espaço;
* tipografia;
* radius;
* sombras;
* movimento.

---

# 38. Governança de Cores

Nova cor somente deverá ser criada quando:

1. existir necessidade semântica ou institucional;
2. nenhuma cor existente atender;
3. contraste for validado;
4. impacto for avaliado;
5. documentação for atualizada.

---

# 39. Governança de Tipografia

Não introduzir nova fonte sem decisão arquitetural.

Mudanças em:

* tamanho;
* peso;
* line-height;

deverão considerar impacto global.

---

# 40. Governança de Espaçamento

Não criar nova escala local.

Novos valores somente deverão ser adicionados quando houver necessidade recorrente real.

---

# 41. Governança de Grid

O grid oficial deverá permanecer baseado na infraestrutura documentada.

Sistemas paralelos de grid não deverão ser criados por módulo.

---

# 42. Governança de Iconografia

A biblioteca consolidada na implementação deverá permanecer uniforme.

Enquanto Font Awesome for o padrão efetivo da aplicação, novos componentes deverão reutilizá-la.

Trocar a biblioteca constitui decisão arquitetural global.

---

# 43. Governança de Componentes

Todo componente compartilhado deverá possuir:

* objetivo;
* anatomia;
* variantes;
* estados;
* responsividade;
* acessibilidade;
* restrições.

---

# 44. Botões

Novas variantes de botão deverão passar por análise de necessidade.

Não criar:

```text id="cjvrx6"
btn-financeiro
btn-secretaria
btn-eventos
```

quando variantes oficiais resolverem o problema.

---

# 45. Formulários

Novos tipos de campo deverão ser avaliados quanto a:

* frequência;
* validação;
* acessibilidade;
* responsividade;
* reutilização.

---

# 46. Cards

Novos tipos deverão justificar por que:

```text id="30vzln"
Card existente
+
composição
```

não é suficiente.

---

# 47. Tabelas

Variantes específicas somente deverão existir quando houver necessidade funcional recorrente.

---

# 48. Modais

Não criar implementação paralela de modal para um módulo.

---

# 49. Feedback

A plataforma deverá possuir um único sistema conceitual de:

* alerts;
* toasts;
* mensagens;
* estados.

---

# 50. Navegação

Sidebar, breadcrumb e menu representam infraestrutura global.

Alterações possuem impacto transversal.

---

# 51. Dashboards

Dashboards deverão reutilizar:

`dashboard_base.html`

quando compatíveis com essa arquitetura.

Infraestrutura compartilhada não deverá ser duplicada.

---

# 52. Acessibilidade

Regressão de acessibilidade deverá ser tratada como regressão de qualidade.

Não aprovar componente que introduza:

* perda de foco;
* contraste inadequado;
* navegação inacessível;
* ausência de label;
* dependência exclusiva de cor.

---

# 53. Movimento

Novos padrões de movimento deverão seguir o GDS-17.

Bibliotecas adicionais de animação somente deverão ser adotadas após avaliação global.

---

# 54. `design_system.css`

Arquivo central:

`static/css/design_system.css`

deverá ser tratado como infraestrutura crítica.

Alterações deverão evitar:

* remoções não planejadas;
* redefinições incompatíveis;
* tokens duplicados;
* regras globais excessivamente abrangentes.

---

# 55. Templates Compartilhados

Templates compartilhados possuem alto impacto.

Mudanças deverão considerar todos os consumidores.

---

# 56. `base.html`

`base.html` representa parte central da árvore estrutural.

Mudanças devem possuir revisão arquitetural.

---

# 57. `base_com_menu.html`

É a principal infraestrutura visual da Área de Gestão.

Alterações deverão ser testadas em múltiplos módulos.

---

# 58. `menu.html`

Mudanças deverão validar:

* navegação;
* permissões;
* responsividade;
* item ativo;
* foco;
* iconografia.

---

# 59. `dashboard_base.html`

Mudanças deverão validar:

* dashboard title;
* breadcrumb;
* filtros;
* conteúdo;
* sidebar;
* responsividade;
* JavaScript;
* anti-FOUC.

---

# 60. JavaScript Compartilhado

Scripts globais deverão possuir responsabilidade clara.

Não adicionar comportamento específico de um módulo em script global sem necessidade.

---

# 61. `dashboard-sidebar.js`

Arquivo:

`static/js/dashboard-sidebar.js`

constitui infraestrutura compartilhada.

Alterações deverão ser tratadas como mudança transversal.

Validar:

* abertura;
* fechamento;
* persistência;
* Local Storage;
* layout;
* responsividade;
* acessibilidade.

---

# 62. Bootstrap

Bootstrap é dependência estrutural importante.

Atualizações de versão deverão possuir análise específica.

Avaliar:

* breaking changes;
* markup;
* utilitários;
* JavaScript;
* componentes;
* acessibilidade;
* CSS.

---

# 63. Font Awesome

Atualização ou substituição deverá avaliar:

* nomes de ícones;
* compatibilidade;
* tamanho do bundle;
* templates existentes;
* acessibilidade.

---

# 64. HTMX

A adoção de HTMX deverá permanecer progressiva.

Novos padrões globais deverão documentar:

* eventos;
* indicadores;
* erros;
* swap;
* foco;
* URLs;
* segurança.

---

# 65. Alpine.js

A adoção deverá permanecer limitada a estado local leve.

Antes de criar padrão global com Alpine.js, validar sua necessidade.

---

# 66. Django Templates

Django Templates permanecem como base da renderização.

Mudanças no Design System deverão respeitar:

* herança;
* includes;
* partials;
* blocos;
* URLs nomeadas.

---

# 67. Progressive Enhancement

A governança deverá preservar:

```text id="tacqt3"
Backend funcional
      ↓
HTML
      ↓
CSS
      ↓
JS
      ↓
HTMX / Alpine.js
```

Não transformar dependências complementares em requisito estrutural sem decisão arquitetural.

---

# 68. Pull Requests

Pull Requests que alterem interface deverão considerar o GDS.

A descrição deverá informar quando houver:

* novo componente;
* novo estilo global;
* nova variante;
* alteração em template base;
* mudança de biblioteca.

---

# 69. Revisão Visual

A revisão deverá avaliar:

* consistência;
* hierarquia;
* espaçamento;
* alinhamento;
* estados;
* conteúdo.

---

# 70. Revisão Arquitetural

Obrigatória especialmente quando houver alteração em:

* layouts base;
* CSS global;
* scripts compartilhados;
* bibliotecas;
* tokens;
* componentes centrais.

---

# 71. Revisão de Acessibilidade

Avaliar:

* teclado;
* foco;
* contraste;
* semântica;
* labels;
* ARIA;
* movimento.

---

# 72. Revisão de Segurança

Avaliar:

* permissões;
* dados visíveis;
* endpoints;
* multi-tenant;
* informações sensíveis.

---

# 73. Revisão de Responsividade

Testar:

* desktop;
* notebook;
* tablet;
* smartphone.

---

# 74. Critérios de Aceite

Uma alteração do GDS somente deverá ser considerada pronta quando:

* necessidade estiver clara;
* implementação estiver concluída;
* documentação atualizada;
* testes realizados;
* compatibilidade avaliada;
* acessibilidade validada;
* impacto analisado.

---

# 75. Exceções

Exceções poderão existir.

Entretanto, não deverão ocorrer silenciosamente.

---

# 76. Processo de Exceção

A exceção deverá informar:

```text id="s4uql8"
Regra afetada

Motivo

Escopo

Duração

Risco

Alternativas avaliadas

Plano futuro
```

---

# 77. Exceções Temporárias

Devem possuir plano de remoção.

Não permitir que exceção temporária se torne padrão informal permanente.

---

# 78. Exceções Permanentes

Somente deverão existir quando o contexto realmente não puder seguir o padrão geral.

Nesse caso, a exceção deverá ser oficialmente documentada.

---

# 79. Documentação de Exceções

Exceções relevantes deverão possuir referência na documentação do componente ou arquitetura correspondente.

---

# 80. Multi-Tenant

Mudanças visuais que afetem seleção, exibição ou filtragem de contexto organizacional deverão possuir revisão de segurança.

Nenhum componente poderá depender do frontend para isolamento.

---

# 81. Permissões

Mudanças em ações deverão validar:

```text id="9e1d1r"
Visualização
Edição
Administração
```

conforme as regras reais do módulo.

---

# 82. Segurança

A governança do GDS deverá impedir padrões que incentivem práticas inseguras.

Exemplo:

```text id="nqlbd9"
Ocultar botão
=
autorização
```

é inválido.

---

# 83. Privacidade

Novos componentes deverão aplicar minimização de dados.

A existência de informação no backend não significa que ela deva aparecer na interface.

---

# 84. Secretaria

Alterações em componentes da Secretaria deverão considerar alto volume de:

* formulários;
* tabelas;
* dados pessoais;
* busca;
* filtros.

---

# 85. Financeiro

Alterações no Financeiro exigem atenção especial a:

* precisão;
* permissões;
* semântica;
* operações críticas;
* valores monetários.

---

# 86. Eventos

Alterações deverão preservar consistência em:

* datas;
* status;
* cards;
* tabelas;
* filtros.

---

# 87. Escola Bíblica

Componentes utilizados em:

* turmas;
* alunos;
* professores;
* frequência;

deverão reutilizar a linguagem global.

---

# 88. Comunicação

A governança deverá proteger a semântica de estados como:

```text id="ibco92"
Rascunho
Agendado
Enviado
Falha
```

quando aplicáveis à implementação.

---

# 89. Patrimônio

Não deverão existir componentes exclusivos sem necessidade recorrente.

---

# 90. Relatórios

Mudanças deverão considerar:

* tela;
* impressão;
* valores;
* tabelas;
* acessibilidade.

---

# 91. Administração

Configurações administrativas deverão permanecer consistentes com a Área de Gestão.

A Administração Técnica baseada no Django Admin continua separada arquiteturalmente.

---

# 92. Portal Público

O Portal Público poderá possuir componentes mais editoriais.

Entretanto, mudanças em:

* paleta;
* tipografia;
* identidade;
* componentes globais;

deverão continuar sob governança do GDS.

---

# 93. Auditoria

O GDS deverá ser auditado periodicamente.

---

# 94. Auditoria Visual

Procurar:

* botões divergentes;
* cores incorretas;
* espaçamentos inconsistentes;
* tabelas diferentes;
* cards duplicados;
* navegação divergente.

---

# 95. Auditoria Técnica

Procurar:

* CSS inline;
* hardcodes;
* scripts duplicados;
* componentes repetidos;
* tokens paralelos;
* bibliotecas redundantes.

---

# 96. Auditoria de Acessibilidade

Avaliar:

* foco;
* teclado;
* contraste;
* headings;
* formulários;
* tabelas;
* modais;
* feedback.

---

# 97. Auditoria de Componentes

Criar inventário periódico dos componentes existentes.

Cada componente deverá ser classificado como:

```text id="zwg081"
Oficial
Experimental
Deprecated
Legado
Removido
```

---

# 98. Métricas

A governança poderá acompanhar indicadores como:

* componentes duplicados;
* estilos inline;
* cores hardcoded;
* componentes deprecated;
* divergências visuais;
* regressões de acessibilidade;
* adoção de componentes oficiais.

Essas métricas deverão orientar melhoria e não burocracia.

---

# 99. Dívida Visual

Dívida visual deverá ser registrada e priorizada conforme impacto.

Exemplos:

* telas antigas fora do GDS;
* componentes duplicados;
* layouts inconsistentes.

---

# 100. Dívida Técnica

Dívida relacionada ao GDS poderá incluir:

* CSS duplicado;
* JavaScript duplicado;
* tokens inconsistentes;
* templates repetidos;
* dependências antigas.

---

# 101. Matriz de Responsabilidade

| Atividade                            | Responsável principal         |
| ------------------------------------ | ----------------------------- |
| Definir tokens                       | Engenharia                    |
| Aprovar componentes                  | Engenharia                    |
| Implementar componente compartilhado | Engenharia                    |
| Utilizar componente no módulo        | Equipe do módulo              |
| Testar funcionalidade                | Engenharia / módulo           |
| Revisar acessibilidade               | Engenharia / Qualidade        |
| Atualizar documentação               | Responsável pela alteração    |
| Aprovar breaking change              | Engenharia                    |
| Conduzir migração                    | Engenharia + módulos afetados |
| Auditar GDS                          | Engenharia / Qualidade        |

---

# 102. Processo para Novo Componente

Etapas:

```text id="knnvr8"
1. Identificar problema
2. Consultar GDS
3. Avaliar composição
4. Documentar proposta
5. Definir anatomia
6. Definir estados
7. Validar acessibilidade
8. Validar responsividade
9. Implementar
10. Testar
11. Documentar
12. Aprovar
```

---

# 103. Processo para Novo Token

Um novo token deverá possuir:

* finalidade;
* categoria;
* nome;
* valor;
* usos;
* impacto;
* justificativa.

Não criar token para uso único sem necessidade.

---

# 104. Processo para Nova Variante

Pergunta obrigatória:

```text id="rygynk"
Essa diferença possui significado
ou é apenas preferência estética?
```

Se for apenas estética local, não deverá gerar variante oficial automaticamente.

---

# 105. Processo para Nova Biblioteca

Antes de introduzir biblioteca frontend, avaliar:

* necessidade;
* peso;
* manutenção;
* compatibilidade;
* acessibilidade;
* licença;
* overlap com ferramentas existentes;
* impacto no bundle;
* curva de aprendizado.

Não adicionar biblioteca porque um único componente a utiliza.

---

# 106. Processo para Alteração Global

Alterações em:

* `design_system.css`;
* `base.html`;
* `base_com_menu.html`;
* `menu.html`;
* `dashboard_base.html`;
* scripts globais;

deverão seguir revisão transversal.

---

# 107. Processo para Breaking Change

Breaking change deverá possuir:

```text id="xs1xpt"
Motivação
+
Impacto
+
Plano de migração
+
Compatibilidade
+
Prazo
+
Documentação
+
Validação
```

A remoção imediata deverá ser evitada quando houver consumidores ativos.

---

# 108. Evidências Arquiteturais

## EA-GDS-GOV-001

O Design System possui documentação oficial própria.

## EA-GDS-GOV-002

A estilização central do GDS utiliza `static/css/design_system.css`.

## EA-GDS-GOV-003

A Área de Gestão reutiliza infraestrutura de templates compartilhados.

## EA-GDS-GOV-004

`base_com_menu.html` representa base importante da Área de Gestão.

## EA-GDS-GOV-005

Dashboards Premium utilizam `dashboard_base.html`.

## EA-GDS-GOV-006

Existe JavaScript compartilhado para sidebar em `dashboard-sidebar.js`.

## EA-GDS-GOV-007

Bootstrap participa da infraestrutura frontend.

## EA-GDS-GOV-008

Font Awesome está consolidado na implementação atual.

## EA-GDS-GOV-009

Django Templates constituem a base da renderização.

## EA-GDS-GOV-010

HTMX possui papel oficial na evolução das atualizações parciais.

## EA-GDS-GOV-011

Alpine.js possui papel oficial para estados locais leves, com adoção progressiva.

## EA-GDS-GOV-012

A Área de Gestão e o Django Admin possuem arquiteturas distintas.

## EA-GDS-GOV-013

O GereIgreja possui múltiplos módulos compartilhando infraestrutura visual.

## EA-GDS-GOV-014

Acessibilidade, responsividade e segurança constituem requisitos transversais do GDS.

---

# 109. Especificações Oficiais

## GDS-GOV-001

O GereIgreja Design System deverá possuir fonte oficial única.

## GDS-GOV-002

A Equipe de Engenharia será responsável pela governança do GDS.

## GDS-GOV-003

Mudanças globais deverão ser documentadas.

## GDS-GOV-004

Mudanças globais deverão avaliar impacto transversal.

## GDS-GOV-005

Breaking changes deverão possuir plano de migração.

## GDS-GOV-006

Componentes deprecated não deverão ser utilizados em novas implementações.

## GDS-GOV-007

A remoção de componente deverá ocorrer somente após avaliação dos consumidores.

## GDS-GOV-008

Tokens deverão permanecer centralizados.

## GDS-GOV-009

Não deverão existir escalas paralelas de tokens por módulo.

## GDS-GOV-010

`static/css/design_system.css` deverá ser tratado como infraestrutura crítica.

## GDS-GOV-011

Templates compartilhados deverão possuir revisão transversal.

## GDS-GOV-012

`dashboard-sidebar.js` deverá permanecer centralizado.

## GDS-GOV-013

Bibliotecas frontend não deverão ser introduzidas sem análise arquitetural quando possuírem impacto global.

## GDS-GOV-014

Bootstrap deverá permanecer subordinado à identidade visual do GDS.

## GDS-GOV-015

Font Awesome deverá permanecer consistente enquanto for a biblioteca consolidada da implementação.

## GDS-GOV-016

HTMX deverá evoluir de maneira controlada.

## GDS-GOV-017

Alpine.js deverá permanecer focado em estados locais leves.

## GDS-GOV-018

Django Templates deverão permanecer como base da renderização enquanto essa for a arquitetura oficial.

## GDS-GOV-019

Acessibilidade deverá fazer parte dos critérios de aprovação.

## GDS-GOV-020

Responsividade deverá fazer parte dos critérios de aprovação.

## GDS-GOV-021

Segurança deverá fazer parte dos critérios de aprovação.

## GDS-GOV-022

Isolamento multi-tenant deverá ser validado no backend.

## GDS-GOV-023

Exceções deverão ser documentadas quando relevantes.

## GDS-GOV-024

Exceções temporárias deverão possuir plano de remoção.

## GDS-GOV-025

Novos componentes deverão possuir documentação antes da adoção ampla.

## GDS-GOV-026

Novos tokens deverão possuir justificativa.

## GDS-GOV-027

Novas variantes deverão possuir significado funcional ou recorrência suficiente.

## GDS-GOV-028

O GDS deverá possuir auditorias periódicas.

## GDS-GOV-029

Dívida visual deverá ser tratada como dívida técnica.

## GDS-GOV-030

A plataforma deverá evitar múltiplas soluções oficiais para o mesmo problema.

---

# 110. Checklist de Governança

## Proposta

* [ ] problema identificado;
* [ ] componente existente avaliado;
* [ ] composição avaliada;
* [ ] impacto analisado;
* [ ] justificativa documentada.

## Design System

* [ ] tokens;
* [ ] cores;
* [ ] tipografia;
* [ ] espaçamento;
* [ ] grid;
* [ ] componentes relacionados.

## Arquitetura

* [ ] templates afetados;
* [ ] CSS afetado;
* [ ] JavaScript afetado;
* [ ] Bootstrap;
* [ ] Font Awesome;
* [ ] HTMX;
* [ ] Alpine.js.

## Impacto

* [ ] Secretaria;
* [ ] Financeiro;
* [ ] Eventos;
* [ ] Escola Bíblica;
* [ ] Comunicação;
* [ ] Patrimônio;
* [ ] Relatórios;
* [ ] Administração;
* [ ] Portal Público.

## Qualidade

* [ ] funcionalidade;
* [ ] visual;
* [ ] acessibilidade;
* [ ] responsividade;
* [ ] performance;
* [ ] segurança.

## Compatibilidade

* [ ] consumidores identificados;
* [ ] breaking change identificado;
* [ ] migração definida;
* [ ] legado analisado;
* [ ] depreciação analisada.

## Documentação

* [ ] GDS atualizado;
* [ ] versão atualizada;
* [ ] changelog;
* [ ] exemplos;
* [ ] regras;
* [ ] migração.

---

# 111. Checklist de Release

Antes de publicar uma nova versão do GDS:

* [ ] versão definida;
* [ ] alterações aprovadas;
* [ ] documentação consistente;
* [ ] implementação sincronizada;
* [ ] testes concluídos;
* [ ] componentes legados identificados;
* [ ] breaking changes documentados;
* [ ] migração publicada quando necessária;
* [ ] acessibilidade validada;
* [ ] responsividade validada;
* [ ] segurança validada;
* [ ] módulos críticos revisados;
* [ ] changelog atualizado.

---

# 112. Roadmap

## Fase 1 — Consolidação Documental

* concluir documentação inicial do GDS;
* revisar nomenclatura;
* alinhar referências;
* eliminar contradições entre documentos.

## Fase 2 — Inventário

Criar inventário de:

* tokens;
* componentes;
* templates;
* estilos;
* scripts;
* variantes.

## Fase 3 — Classificação

Classificar componentes como:

```text id="pcf79e"
Oficial
Experimental
Deprecated
Legado
```

## Fase 4 — Auditoria

Executar auditorias periódicas de:

* consistência;
* CSS;
* JavaScript;
* acessibilidade;
* responsividade.

## Fase 5 — Componentização

Consolidar componentes de maior reutilização.

Priorizar:

* botões;
* formulários;
* cards;
* tabelas;
* feedback;
* modais;
* dashboards.

## Fase 6 — Versionamento

Formalizar processo de:

* release;
* changelog;
* compatibilidade;
* migração.

## Fase 7 — Qualidade Automatizada

Avaliar automação para identificar:

* cores hardcoded;
* CSS inline;
* componentes deprecated;
* regressões;
* problemas de acessibilidade.

## Fase 8 — Evolução

Preparar governança para:

* PWA;
* aplicações móveis;
* temas;
* Dark Mode;
* White Label;
* novos produtos do ecossistema GereIgreja.

---

# 113. Documentos Relacionados

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
* GDS-18 — Boas Práticas
* GFE — GereIgreja Frontend Engineering
* GEA — GereIgreja Engineering Architecture
* GDF — Framework de Documentação
* GQF — Framework de Qualidade

---

# 114. Princípios Finais

O GereIgreja Design System deverá permanecer uma infraestrutura viva.

Sua governança deverá proteger simultaneamente:

```text id="erl2w3"
Consistência
+
Velocidade de desenvolvimento
+
Qualidade
+
Compatibilidade
+
Acessibilidade
+
Segurança
+
Evolução
```

Governança não deverá significar burocracia excessiva.

Seu objetivo é evitar que decisões locais gerem custos globais.

A regra de evolução deverá permanecer:

```text id="a7lccg"
Necessidade
   ↓
Consultar
   ↓
Reutilizar
   ↓
Compor
   ↓
Estender
   ↓
Criar quando necessário
   ↓
Validar
   ↓
Documentar
   ↓
Evoluir
```

O GDS deverá preservar uma experiência única em:

* Secretaria;
* Financeiro;
* Eventos;
* Escola Bíblica;
* Comunicação;
* Patrimônio;
* Relatórios;
* Configurações;
* demais módulos do GereIgreja.

Templates compartilhados deverão permanecer sob controle arquitetural.

`static/css/design_system.css` deverá permanecer como infraestrutura central da identidade visual.

`base_com_menu.html` deverá continuar representando uma das principais bases da Área de Gestão.

`dashboard_base.html` e `dashboard-sidebar.js` deverão permanecer centralizados para os Dashboards Premium enquanto fizerem parte da arquitetura oficial.

Bootstrap deverá permanecer uma infraestrutura, nunca uma identidade paralela.

Font Awesome deverá permanecer consistente enquanto for a biblioteca consolidada.

HTMX deverá evoluir atualizações parciais de forma progressiva.

Alpine.js deverá permanecer restrito a estados locais leves quando adotado.

Django Templates deverão continuar oferecendo a base funcional da interface enquanto essa permanecer a arquitetura oficial do GereIgreja.

A Administração Técnica baseada no Django Admin deverá permanecer claramente separada da Área de Gestão.

O objetivo final da governança é garantir que o GereIgreja possa crescer por muitos anos sem perder a identidade, a organização e a confiabilidade visual estabelecidas pelo Design System.

---

# 115. Status do Documento

**Pasta**

`docs/design-system/`

**Arquivo**

`19-Governanca.md`

**Documento**

`GDS-19`

**Código**

`GDS-GOVERNANCE`

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

**GDS-19 — Governança**
**GereIgreja Design System**
