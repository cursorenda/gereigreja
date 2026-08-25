# 11 - GereIgreja Design System — Tabelas e Listagens (GDS-11)

> "As informações administrativas do GereIgreja devem ser apresentadas de forma clara, organizada e eficiente, permitindo que o usuário encontre, compreenda e gerencie dados sem esforço desnecessário."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel das Tabelas no GereIgreja
4. Princípios de Tabelas e Listagens
5. Anatomia da Tabela
6. Cabeçalho da Tabela
7. Colunas
8. Ordenação
9. Alinhamento
10. Formatação de Dados
11. Identificação de Registros
12. Status e Badges
13. Ações por Registro
14. Menu de Ações
15. Seleção de Registros
16. Seleção em Massa
17. Paginação
18. Quantidade de Registros
19. Busca
20. Filtros
21. Combinação de Busca e Filtros
22. Estado Inicial
23. Estado Vazio
24. Estado Sem Resultados
25. Estado de Carregamento
26. Estado de Erro
27. Atualização de Dados
28. Tabelas com HTMX
29. Tabelas com Alpine.js
30. Responsividade
31. Tabelas em Smartphones
32. Tabelas em Tablets
33. Tabelas em Desktop
34. Colunas Responsivas
35. Tabelas com Rolagem Horizontal
36. Tabelas e Acessibilidade
37. Navegação por Teclado
38. Leitores de Tela
39. Cabeçalhos Semânticos
40. Contraste e Estados Visuais
41. Dados Financeiros
42. Valores Monetários
43. Datas e Horários
44. Pessoas e Membros
45. Congregações
46. Eventos
47. Escola Bíblica
48. Comunicação
49. Administração
50. Tabelas de Lançamentos Financeiros
51. Tabelas de Receitas
52. Tabelas de Despesas
53. Tabelas de Membros
54. Tabelas de Congregações
55. Tabelas de Eventos
56. Tabelas de Turmas
57. Tabelas de Usuários
58. Tabelas de Comunicação
59. Relacionamento entre Tabela e Card
60. Tabela versus Card
61. Tabela versus Lista
62. Listagens Simples
63. Listagens com Ações
64. Listagens Hierárquicas
65. Agrupamento de Registros
66. Expansão de Registros
67. Detalhamento de Registro
68. Tabela e Modal
69. Tabela e Drawer
70. Tabela e Breadcrumb
71. Tabela e Sidebar
72. Permissões
73. Segurança no Backend
74. Multi-Tenant
75. Isolamento de Dados
76. Dados Sensíveis
77. Exclusão de Registros
78. Confirmação de Ações Críticas
79. Feedback após Operações
80. Estados de Sucesso
81. Estados de Aviso
82. Estados de Erro
83. Performance
84. Paginação no Backend
85. Querysets
86. Ordenação no Backend
87. Filtros no Backend
88. Busca no Backend
89. Prevenção de N+1 Queries
90. Carregamento Incremental
91. HTMX e Atualização Parcial
92. URLs e Parâmetros
93. Preservação de Filtros
94. Histórico de Navegação
95. Formulários dentro de Listagens
96. Exportação de Dados
97. Impressão
98. Relatórios
99. Tabelas do Portal Administrativo
100. Tabelas do Portal Público
101. Anti-Patterns
102. Regras de Implementação
103. Componentização
104. Tokens do GDS
105. CSS
106. Bootstrap
107. Templates Django
108. Testes Visuais
109. Testes Funcionais
110. Testes de Acessibilidade
111. Testes de Responsividade
112. Testes de Permissões
113. Testes de Segurança
114. Checklist de Implementação
115. Checklist por Módulo
116. Governança
117. Novos Componentes
118. Alterações
119. Compatibilidade
120. Roadmap
121. Especificações Oficiais
122. Princípios Finais
123. Documentos Relacionados
124. Status do Documento

---

# 1. Objetivo

Definir o padrão oficial para tabelas e listagens utilizadas no GereIgreja.

---

# 2. Escopo

Este documento deverá definir:

- tabelas administrativas;
- listagens;
- paginação;
- filtros;
- busca;
- ordenação;
- ações;
- estados;
- responsividade;
- acessibilidade;
- segurança;
- integração com Django;
- integração com HTMX;
- integração com Alpine.js;
- integração com o GDS.

---

# 3. Papel das Tabelas no GereIgreja

As tabelas serão utilizadas principalmente para dados estruturados e operacionais.

Exemplos:

- membros;
- visitantes;
- usuários;
- congregações;
- lançamentos financeiros;
- receitas;
- despesas;
- eventos;
- turmas;
- alunos;
- comunicações;
- registros administrativos.

---

# 4. Princípios de Tabelas e Listagens

As tabelas deverão priorizar:

- clareza;
- densidade adequada;
- escaneabilidade;
- consistência;
- acessibilidade;
- performance;
- responsividade;
- segurança.

---

# 5. Anatomia da Tabela

Estrutura oficial:

```text
Título da página
Breadcrumb

Descrição / contexto

Busca + filtros + ações

Tabela
├── Cabeçalho
├── Registros
└── Paginação
````

---

# 6. Cabeçalho da Tabela

Definir:

* títulos das colunas;
* alinhamento;
* ordenação;
* ações;
* estados.

---

# 7. Colunas

Definir regras para:

* quantidade;
* largura;
* prioridade;
* responsividade;
* conteúdo;
* ocultação.

---

# 8. Ordenação

Definir:

* ascendente;
* descendente;
* coluna ativa;
* indicação visual;
* persistência;
* ordenação backend.

---

# 9. Alinhamento

Definir:

* texto;
* números;
* valores monetários;
* datas;
* ações;
* badges.

---

# 10. Formatação de Dados

Padronizar a apresentação de:

* nomes;
* datas;
* horários;
* números;
* valores;
* telefones;
* documentos;
* status.

---

# 11. Identificação de Registros

Definir como identificar registros sem criar excesso visual.

Exemplo:

```text
Nome
Informação secundária
```

---

# 12. Status e Badges

Utilizar os tokens semânticos do GDS:

* Success;
* Warning;
* Danger;
* estados neutros.

---

# 13. Ações por Registro

Definir:

* ação primária;
* ações secundárias;
* edição;
* visualização;
* exclusão;
* menus.

---

# 14. Menu de Ações

Padronizar menus contextuais.

---

# 15. Seleção de Registros

Definir checkbox e seleção individual.

---

# 16. Seleção em Massa

Definir:

* selecionar página;
* selecionar todos;
* ações em massa;
* confirmação;
* permissões.

---

# 17. Paginação

Definir o padrão oficial de paginação do GereIgreja.

---

# 18. Quantidade de Registros

Apresentar quantidade de registros de forma clara.

---

# 19. Busca

Definir:

* campo;
* placeholder;
* debounce;
* backend;
* limpeza;
* preservação de filtros.

---

# 20. Filtros

Definir filtros por:

* status;
* congregação;
* período;
* categoria;
* usuário;
* módulo.

---

# 21. Combinação de Busca e Filtros

Busca e filtros deverão funcionar de maneira previsível.

---

# 22. Estado Inicial

Definir a aparência antes da primeira consulta.

---

# 23. Estado Vazio

Exemplo:

```text
Nenhum membro cadastrado.

[Adicionar membro]
```

---

# 24. Estado Sem Resultados

Exemplo:

```text
Nenhum resultado encontrado.

[Limpar filtros]
```

---

# 25. Estado de Carregamento

Definir skeleton ou indicador de carregamento.

---

# 26. Estado de Erro

Definir mensagem e ação de recuperação.

---

# 27. Atualização de Dados

Definir atualização após:

* criação;
* edição;
* exclusão;
* alteração de status;
* filtros;
* paginação.

---

# 28. Tabelas com HTMX

Definir como HTMX será utilizado para:

* busca;
* filtros;
* paginação;
* atualização de linhas;
* exclusão;
* atualização parcial.

---

# 29. Tabelas com Alpine.js

Alpine.js deverá ser utilizado somente para comportamento de interface que realmente necessite de estado local.

---

# 30. Responsividade

Definir comportamento por breakpoint.

---

# 31. Tabelas em Smartphones

Definir estratégias para:

* redução de colunas;
* prioridade;
* cards alternativos;
* rolagem;
* ações.

---

# 32. Tabelas em Tablets

Definir comportamento intermediário.

---

# 33. Tabelas em Desktop

Utilizar o espaço disponível sem gerar excesso de largura.

---

# 34. Colunas Responsivas

Classificar colunas como:

```text
Essencial
Importante
Secundária
Opcional
```

---

# 35. Tabelas com Rolagem Horizontal

A rolagem horizontal deverá ser utilizada somente quando necessária.

---

# 36. Tabelas e Acessibilidade

Definir:

* semântica;
* foco;
* teclado;
* leitores de tela;
* contraste.

---

# 37. Navegação por Teclado

Todos os elementos interativos deverão ser acessíveis.

---

# 38. Leitores de Tela

Utilizar cabeçalhos e relações semânticas apropriadas.

---

# 39. Cabeçalhos Semânticos

Utilizar corretamente:

```html
<table>
<thead>
<tbody>
<th>
<td>
```

quando uma tabela HTML verdadeira for apropriada.

---

# 40. Contraste e Estados Visuais

Estados não poderão depender somente de cor.

---

# 41. Dados Financeiros

Definir padrões específicos para o módulo Financeiro.

---

# 42. Valores Monetários

Utilizar padrão brasileiro:

```text
R$ 1.250,00
```

---

# 43. Datas e Horários

Padronizar datas e horários do GereIgreja.

---

# 44. Pessoas e Membros

Definir padrões para:

* nome;
* congregação;
* situação;
* contatos;
* ações.

---

# 45. Congregações

Definir listagens de congregações e informações relacionadas.

---

# 46. Eventos

Definir tabelas para:

* eventos;
* cultos;
* programações;
* datas;
* status.

---

# 47. Escola Bíblica

Definir listagens para:

* turmas;
* alunos;
* professores;
* frequência;
* atividades.

---

# 48. Comunicação

Definir listagens para:

* mensagens;
* campanhas;
* destinatários;
* status de envio.

---

# 49. Administração

Definir tabelas administrativas para:

* usuários;
* permissões;
* configurações;
* registros.

---

# 50. Tabelas de Lançamentos Financeiros

Definir estrutura específica para lançamentos.

---

# 51. Tabelas de Receitas

Definir:

* data;
* descrição;
* categoria;
* valor;
* congregação;
* status;
* ações.

---

# 52. Tabelas de Despesas

Definir estrutura equivalente respeitando a semântica financeira.

---

# 53. Tabelas de Membros

Definir estrutura específica para Secretaria.

---

# 54. Tabelas de Congregações

Definir identificação e status das congregações.

---

# 55. Tabelas de Eventos

Definir informações essenciais de eventos.

---

# 56. Tabelas de Turmas

Definir listagens da Escola Bíblica.

---

# 57. Tabelas de Usuários

Definir:

* nome;
* perfil;
* status;
* congregação;
* ações.

---

# 58. Tabelas de Comunicação

Definir:

* campanha;
* canal;
* quantidade;
* status;
* data;
* ações.

---

# 59. Relacionamento entre Tabela e Card

Definir quando cada componente deverá ser utilizado.

---

# 60. Tabela versus Card

Tabela:

```text
muitos registros + dados estruturados
```

Card:

```text
resumo + destaque + ações
```

---

# 61. Tabela versus Lista

Definir quando uma lista simples for suficiente.

---

# 62. Listagens Simples

Definir padrões para listas sem estrutura tabular complexa.

---

# 63. Listagens com Ações

Definir ações por item.

---

# 64. Listagens Hierárquicas

Definir registros pai/filho quando aplicável.

---

# 65. Agrupamento de Registros

Definir agrupamentos por:

* data;
* categoria;
* congregação;
* status.

---

# 66. Expansão de Registros

Definir linhas expansíveis quando necessário.

---

# 67. Detalhamento de Registro

Definir ligação entre listagem e página detalhada.

---

# 68. Tabela e Modal

Definir quando utilizar modal.

---

# 69. Tabela e Drawer

Definir quando utilizar drawer.

---

# 70. Tabela e Breadcrumb

Toda página interna deverá respeitar:

```text
Home > Módulo > Página
```

---

# 71. Tabela e Sidebar

A tabela deverá se adaptar à presença ou ausência da sidebar.

---

# 72. Permissões

Ações deverão respeitar permissões.

---

# 73. Segurança no Backend

Ocultar botão não substitui autorização no servidor.

---

# 74. Multi-Tenant

Os dados deverão permanecer isolados por contexto organizacional.

---

# 75. Isolamento de Dados

Definir regras para impedir vazamento entre igrejas e congregações.

---

# 76. Dados Sensíveis

Não exibir informações sensíveis sem autorização.

---

# 77. Exclusão de Registros

Definir comportamento para exclusão lógica ou física conforme o domínio.

---

# 78. Confirmação de Ações Críticas

Definir confirmação para ações destrutivas.

---

# 79. Feedback após Operações

Definir mensagens de sucesso e erro.

---

# 80. Estados de Sucesso

Utilizar semântica Success.

---

# 81. Estados de Aviso

Utilizar semântica Warning.

---

# 82. Estados de Erro

Utilizar semântica Danger.

---

# 83. Performance

Definir regras para grandes volumes de registros.

---

# 84. Paginação no Backend

Paginação deverá ocorrer preferencialmente no backend para grandes conjuntos.

---

# 85. Querysets

Querysets deverão ser construídos de maneira eficiente.

---

# 86. Ordenação no Backend

Ordenações relevantes deverão ocorrer no backend.

---

# 87. Filtros no Backend

Filtros deverão ser aplicados corretamente no queryset.

---

# 88. Busca no Backend

Buscas deverão evitar processamento desnecessário no cliente.

---

# 89. Prevenção de N+1 Queries

Utilizar estratégias apropriadas do Django quando relações forem exibidas.

---

# 90. Carregamento Incremental

Utilizar quando houver ganho real de performance ou experiência.

---

# 91. HTMX e Atualização Parcial

Atualizar somente a região necessária sempre que apropriado.

---

# 92. URLs e Parâmetros

Filtros, busca, paginação e ordenação deverão possuir URLs previsíveis quando aplicável.

---

# 93. Preservação de Filtros

Paginação e ações não deverão apagar filtros inesperadamente.

---

# 94. Histórico de Navegação

O usuário deverá conseguir retornar ao contexto anterior quando apropriado.

---

# 95. Formulários dentro de Listagens

Definir regras para edição rápida e ações inline.

---

# 96. Exportação de Dados

Definir regras para exportação de dados quando o módulo oferecer essa funcionalidade.

---

# 97. Impressão

Definir comportamento para impressão de listagens e relatórios.

---

# 98. Relatórios

Diferenciar tabela operacional de relatório.

---

# 99. Tabelas do Portal Administrativo

Aplicar o padrão completo do GDS.

---

# 100. Tabelas do Portal Público

Utilizar somente quando a estrutura tabular realmente melhorar a apresentação pública.

---

# 101. Anti-Patterns

Documentar padrões proibidos:

* tabelas excessivamente largas;
* excesso de colunas;
* ações sem contexto;
* cores arbitrárias;
* tabelas sem paginação quando necessário;
* filtros confusos;
* dados sensíveis expostos;
* ausência de estados;
* tabelas não responsivas.

---

# 102. Regras de Implementação

Definir padrões técnicos para implementação.

---

# 103. Componentização

Tabelas deverão utilizar componentes reutilizáveis quando aplicável.

---

# 104. Tokens do GDS

Toda estilização deverá utilizar tokens oficiais.

---

# 105. CSS

Utilizar:

```text
static/css/design_system.css
```

como referência oficial de tokens e estilos.

---

# 106. Bootstrap

Bootstrap poderá fornecer estrutura e comportamento base, mas não deverá quebrar a identidade do GDS.

---

# 107. Templates Django

Definir boas práticas para templates.

---

# 108. Testes Visuais

Testar diferentes conteúdos e estados.

---

# 109. Testes Funcionais

Testar:

* busca;
* filtros;
* ordenação;
* paginação;
* ações.

---

# 110. Testes de Acessibilidade

Verificar teclado, foco, contraste e semântica.

---

# 111. Testes de Responsividade

Testar:

* desktop;
* tablet;
* smartphone.

---

# 112. Testes de Permissões

Verificar cada perfil de acesso.

---

# 113. Testes de Segurança

Validar autorização diretamente no backend.

---

# 114. Checklist de Implementação

Checklist completo para publicação de tabelas.

---

# 115. Checklist por Módulo

Checklist específico para:

* Secretaria;
* Financeiro;
* Eventos;
* Escola Bíblica;
* Comunicação;
* Administração.

---

# 116. Governança

Definir responsabilidade da Engenharia sobre o padrão.

---

# 117. Novos Componentes

Definir processo para criação de novas variantes.

---

# 118. Alterações

Definir processo de alteração de componentes existentes.

---

# 119. Compatibilidade

Avaliar impacto nos módulos existentes.

---

# 120. Roadmap

Definir evolução das tabelas no GereIgreja.

---

# 121. Especificações Oficiais

Criar códigos:

```text
GDS-TABLE-001
GDS-TABLE-002
GDS-TABLE-003
...
```

para requisitos obrigatórios.

---

# 122. Princípios Finais

As tabelas do GereIgreja deverão permitir que o usuário:

* encontre;
* filtre;
* compreenda;
* compare;
* edite;
* acompanhe;
* gerencie

informações com segurança e eficiência.

---

# 123. Documentos Relacionados

* GDS-01 — GereIgreja Design System
* GDS-08 — Botões
* GDS-09 — Formulários
* GDS-10 — Cards
* GEA-02 — Arquitetura da Plataforma
* GEA-04 — Arquitetura do Frontend
* GDF — Framework de Documentação
* GQF — Framework de Qualidade

---

# 124. Status do Documento

Pasta:

docs/frameworks/

Arquivo:

11-GDS-Tabelas-e-Listagens.md

Documento:

GDS-11

Framework:

GDS — GereIgreja Design System

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

```

Essa será a **estrutura-mestra do GDS-11**. Na elaboração do conteúdo completo, vou desenvolver cada seção com as regras concretas do GereIgreja, principalmente nos pontos de **Django + QuerySets + HTMX + Alpine.js + Bootstrap + permissões + multi-tenant + módulos reais**, em vez de simplesmente preencher os tópicos com recomendações genéricas.
```


