# 12 - GereIgreja Design System — Modais, Dialogs e Confirmações (GDS-12)

> "Toda interação que interrompe o fluxo do usuário deve possuir um propósito claro, comunicar o que está acontecendo e permitir uma decisão segura."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel dos Modais no GereIgreja
4. Princípios de Uso
5. Quando Utilizar um Modal
6. Quando Não Utilizar um Modal
7. Anatomia Oficial
8. Cabeçalho
9. Título
10. Botão de Fechamento
11. Corpo
12. Rodapé
13. Ações
14. Hierarquia das Ações
15. Botões Primários e Secundários
16. Ações Destrutivas
17. Confirmações
18. Confirmação de Exclusão
19. Confirmação de Operações Financeiras
20. Confirmação de Alterações Críticas
21. Modal de Cadastro
22. Modal de Edição
23. Modal de Visualização
24. Modal de Detalhes
25. Modal Informativo
26. Modal de Aviso
27. Modal de Erro
28. Modal de Sucesso
29. Modal com Formulário
30. Modal com Tabela
31. Modal com Listagem
32. Modal com Conteúdo Dinâmico
33. Modal com HTMX
34. Modal e Alpine.js
35. Modal e Bootstrap
36. Modal e Django Templates
37. Estados de Loading
38. Estados de Erro
39. Estados de Sucesso
40. Fechamento
41. Clique no Overlay
42. Tecla ESC
43. Foco
44. Navegação por Teclado
45. Acessibilidade
46. Leitores de Tela
47. Responsividade
48. Smartphone
49. Tablet
50. Desktop
51. Altura e Rolagem
52. Formulários Longos
53. Modais Financeiros
54. Modais de Secretaria
55. Modais de Eventos
56. Modais da Escola Bíblica
57. Modais de Comunicação
58. Modais Administrativos
59. Permissões
60. Segurança
61. Validação no Backend
62. Dados Sensíveis
63. Concorrência
64. Feedback após Operações
65. Toasts e Mensagens
66. Atualização Parcial
67. Preservação do Contexto
68. Breadcrumb e Modal
69. Sidebar e Modal
70. Tabelas e Modal
71. Cards e Modal
72. Confirmação em Duas Etapas
73. Operações Irreversíveis
74. Operações Financeiras Sensíveis
75. Exclusão Lógica
76. Exclusão Física
77. Cancelamento
78. Estorno
79. Estados de Permissão
80. Modal sem Permissão
81. Modal de Sessão
82. Modal de Aviso de Alterações
83. Modal de Saída
84. Modal de Ajuda
85. Modal de Detalhamento
86. Modal de Histórico
87. Modal de Auditoria
88. Performance
89. Carregamento sob Demanda
90. HTMX e Conteúdo Parcial
91. Evitar HTML Desnecessário
92. Anti-Patterns
93. Regras de Implementação
94. Tokens
95. CSS
96. Bootstrap
97. Django
98. HTMX
99. Alpine.js
100. Testes
101. Testes Funcionais
102. Testes Visuais
103. Testes de Acessibilidade
104. Testes de Responsividade
105. Testes de Permissão
106. Testes de Segurança
107. Checklist
108. Especificações Oficiais
109. Governança
110. Compatibilidade
111. Evolução
112. Documentos Relacionados
113. Princípios Finais
114. Status do Documento

---

# 1. Objetivo

O GDS-12 define o padrão oficial para modais, dialogs e confirmações utilizados no GereIgreja.

O objetivo é garantir que qualquer interação que interrompa temporariamente o fluxo principal do usuário seja:

- previsível;
- clara;
- acessível;
- responsiva;
- segura;
- consistente;
- integrada ao Design System.

---

# 2. Escopo

Este documento estabelece padrões para:

- modais;
- dialogs;
- confirmações;
- formulários em modal;
- visualização de detalhes;
- operações destrutivas;
- operações financeiras;
- mensagens de erro;
- mensagens de sucesso;
- conteúdo carregado dinamicamente;
- integração com HTMX;
- integração com Alpine.js;
- integração com Bootstrap.

---

# 3. Papel dos Modais no GereIgreja

O modal deverá ser utilizado como uma camada temporária de interação.

Ele deverá permitir que o usuário execute uma ação sem necessariamente abandonar o contexto atual.

Exemplo:

```text
Secretaria
    │
    ├── Lista de membros
    │
    └── [Adicionar membro]
             │
             ▼
        Modal de cadastro
````

Após concluir a operação, o usuário deverá retornar ao contexto anterior sempre que isso fizer sentido.

---

# 4. Princípios de Uso

Todo modal deverá seguir os princípios:

* propósito único;
* contexto preservado;
* conteúdo objetivo;
* ação clara;
* fechamento previsível;
* foco controlado;
* acessibilidade;
* segurança;
* responsividade.

---

# 5. Quando Utilizar um Modal

Um modal poderá ser utilizado para:

* cadastro rápido;
* edição rápida;
* confirmação;
* visualização curta;
* informações contextuais;
* ações que não exigem uma página inteira;
* operações pontuais.

Exemplo:

```text
Membros

[João Silva]
[Maria Souza]
[Pedro Santos]

[+ Adicionar membro]
```

Ao clicar em adicionar:

```text
┌──────────────────────────────────┐
│ Adicionar membro              X  │
├──────────────────────────────────┤
│ Nome                             │
│ [________________________]       │
│                                  │
│ Congregação                      │
│ [________________________]       │
│                                  │
│ [Cancelar] [Salvar membro]       │
└──────────────────────────────────┘
```

---

# 6. Quando Não Utilizar um Modal

Não utilizar modal para:

* páginas completas;
* formulários extremamente extensos;
* processos complexos;
* relatórios extensos;
* tabelas muito grandes;
* fluxos com múltiplas etapas;
* conteúdos que exigem navegação extensa.

Nesses casos, utilizar uma página própria ou outro componente adequado.

---

# 7. Anatomia Oficial

O modal deverá seguir uma estrutura consistente:

```text
┌──────────────────────────────────────┐
│ Cabeçalho                        X   │
├──────────────────────────────────────┤
│                                      │
│ Corpo                                │
│                                      │
├──────────────────────────────────────┤
│ Ações                                │
└──────────────────────────────────────┘
```

Estrutura conceitual:

```text
Modal
├── Header
│   ├── Title
│   └── Close
├── Body
└── Footer
    ├── Secondary Action
    └── Primary Action
```

---

# 8. Cabeçalho

O cabeçalho deverá identificar claramente a finalidade do modal.

---

# 9. Título

O título deverá ser objetivo.

Exemplos:

```text
Adicionar membro
Editar membro
Excluir membro
Registrar despesa
Visualizar evento
```

Evitar títulos genéricos como:

```text
Atenção
Informação
Janela
Mensagem
```

quando um título específico for possível.

---

# 10. Botão de Fechamento

O modal deverá possuir mecanismo claro de fechamento.

Quando houver botão de fechamento visual, ele deverá possuir identificação acessível.

---

# 11. Corpo

O corpo deverá conter somente o conteúdo necessário para concluir a tarefa.

---

# 12. Rodapé

O rodapé deverá concentrar as ações principais.

Exemplo:

```text
[Cancelar] [Salvar]
```

---

# 13. Ações

As ações deverão seguir a hierarquia do GDS.

A ação principal deverá ser visualmente distinguível.

---

# 14. Hierarquia das Ações

Exemplo:

```text
Cancelar     Salvar
```

O botão primário deverá representar a ação principal.

---

# 15. Botões Primários e Secundários

Utilizar os componentes oficiais de botões definidos no GDS.

Não criar estilos de botão exclusivos dentro do modal.

---

# 16. Ações Destrutivas

Ações destrutivas deverão utilizar a semântica `Danger`.

Exemplo:

```text
[Cancelar] [Excluir]
```

O botão de exclusão deverá comunicar claramente o risco.

---

# 17. Confirmações

Confirmações deverão explicar:

1. o que será feito;
2. qual registro será afetado;
3. consequência;
4. ação para cancelar;
5. ação para confirmar.

---

# 18. Confirmação de Exclusão

Exemplo:

```text
Excluir membro

Tem certeza de que deseja excluir o membro
"João Silva"?

Essa ação poderá impedir o acesso ao registro
dependendo das regras de exclusão aplicadas.

[Cancelar] [Excluir]
```

O texto deverá refletir o comportamento real da operação.

---

# 19. Confirmação de Operações Financeiras

Operações financeiras deverão possuir confirmação adequada quando forem relevantes ou potencialmente irreversíveis.

Exemplo:

```text
Estornar lançamento

Você está prestes a estornar:

Descrição:
Oferta especial

Valor:
R$ 500,00

Data:
02/08/2026

Deseja continuar?

[Cancelar] [Estornar lançamento]
```

O texto deverá corresponder exatamente à operação real implementada.

---

# 20. Confirmação de Alterações Críticas

Alterações com impacto relevante deverão ser confirmadas quando necessário.

---

# 21. Modal de Cadastro

Utilizar para operações pequenas e objetivas.

Exemplo:

```text
Adicionar congregação

Nome
[________________________]

Cidade
[________________________]

[Cancelar] [Salvar]
```

---

# 22. Modal de Edição

O modal deverá carregar os dados atuais do registro.

Exemplo:

```text
Editar congregação

Nome
[Congregação Plautino Soares]

Status
[Ativa ▼]

[Cancelar] [Salvar alterações]
```

---

# 23. Modal de Visualização

Quando não houver edição, o modal poderá apresentar informações somente para consulta.

---

# 24. Modal de Detalhes

Utilizar para informações complementares que não justificam uma página própria.

---

# 25. Modal Informativo

Utilizar para apresentar orientação ou informação contextual.

---

# 26. Modal de Aviso

Deverá informar uma situação que exige atenção.

Utilizar `Warning` quando apropriado.

---

# 27. Modal de Erro

Deverá explicar:

* o que aconteceu;
* o que o usuário pode fazer;
* se é possível tentar novamente.

Evitar mostrar detalhes internos do Django.

Não apresentar ao usuário:

```text
IntegrityError
ValidationError
Traceback
500 Internal Server Error
```

sem tratamento adequado.

---

# 28. Modal de Sucesso

Quando uma operação for concluída com sucesso, preferir feedback não intrusivo quando não houver necessidade de permanecer no modal.

Exemplo:

```text
Membro cadastrado com sucesso.
```

Se o modal não tiver mais função, poderá ser fechado automaticamente conforme o fluxo.

---

# 29. Modal com Formulário

Formulários dentro de modais deverão seguir o GDS-09.

Isso inclui:

* labels;
* campos;
* mensagens de validação;
* foco;
* botões;
* estados;
* acessibilidade.

O GDS-12 não deverá duplicar as regras completas de formulários.

---

# 30. Modal com Tabela

Evitar tabelas grandes dentro de modais.

Se a tabela exigir:

* filtros;
* paginação;
* muitas colunas;
* rolagem extensa;

preferir uma página dedicada.

---

# 31. Modal com Listagem

Listagens pequenas poderão ser utilizadas.

Exemplo:

```text
Selecionar congregação

[Buscar]

○ Engenheiro Caldas
○ Plautino Soares
○ Sobrália

[Cancelar] [Selecionar]
```

---

# 32. Modal com Conteúdo Dinâmico

Conteúdo poderá ser carregado conforme a necessidade.

Essa estratégia é especialmente relevante para evitar carregar grandes quantidades de HTML antes da interação.

---

# 33. Modal com HTMX

Quando o modal utilizar HTMX, o conteúdo poderá ser carregado sob demanda.

Exemplo conceitual:

```text
Clique
   ↓
HTMX request
   ↓
Django View
   ↓
Template parcial
   ↓
Modal
```

O backend continuará responsável por:

* autorização;
* validação;
* regras de negócio;
* persistência.

---

# 34. Modal e Alpine.js

Alpine.js poderá controlar comportamentos locais, como:

* abrir/fechar;
* estados simples;
* confirmação visual;
* pequenas interações.

Não utilizar Alpine.js para substituir regras de negócio do Django.

---

# 35. Modal e Bootstrap

Quando Bootstrap fizer parte da implementação frontend, os componentes de modal poderão ser utilizados como infraestrutura.

Entretanto, deverão respeitar:

* tokens do GDS;
* cores oficiais;
* espaçamentos;
* tipografia;
* acessibilidade;
* comportamento definido neste documento.

Bootstrap não deverá definir sozinho a identidade visual do GereIgreja.

---

# 36. Modal e Django Templates

Os templates deverão manter separação clara entre:

* estrutura;
* apresentação;
* dados;
* regras de negócio.

As regras de negócio deverão permanecer nas camadas apropriadas do backend.

---

# 37. Estados de Loading

Durante operações assíncronas, o usuário deverá perceber que a ação está em andamento.

Exemplo:

```text
[Salvando...]
```

O botão poderá ser temporariamente desabilitado para impedir submissões duplicadas.

---

# 38. Estados de Erro

O erro deverá permanecer próximo ao contexto da ação.

Exemplo:

```text
Não foi possível salvar o membro.

Verifique os campos destacados e tente novamente.
```

---

# 39. Estados de Sucesso

Após sucesso:

```text
Membro atualizado com sucesso.
```

A interface deverá atualizar o contexto necessário.

---

# 40. Fechamento

O modal deverá possuir comportamento previsível de fechamento.

---

# 41. Clique no Overlay

O fechamento pelo overlay poderá ser permitido em modais informativos ou simples.

Para operações críticas, formulários com alterações ou confirmações importantes, considerar impedir o fechamento acidental.

---

# 42. Tecla ESC

Quando tecnicamente apropriado, `ESC` deverá fechar o modal.

Exceções deverão existir apenas quando houver motivo claro.

---

# 43. Foco

Ao abrir:

```text
foco → modal
```

O foco deverá ser direcionado para um elemento adequado.

Ao fechar:

```text
modal fechado
     ↓
foco retorna ao elemento que iniciou a abertura
```

---

# 44. Navegação por Teclado

Usuários deverão conseguir navegar por:

* campos;
* botões;
* links;
* controles.

O foco não deverá escapar indevidamente para o conteúdo atrás do modal.

---

# 45. Acessibilidade

O modal deverá possuir:

* nome acessível;
* foco controlado;
* fechamento acessível;
* estrutura semântica;
* contraste adequado.

---

# 46. Leitores de Tela

Tecnologias assistivas deverão conseguir identificar:

* que um dialog foi aberto;
* seu título;
* seu conteúdo;
* suas ações.

---

# 47. Responsividade

O modal deverá adaptar-se ao tamanho da tela.

---

# 48. Smartphone

Em smartphones:

* evitar largura fixa;
* permitir rolagem vertical;
* manter ações acessíveis;
* evitar conteúdo comprimido.

---

# 49. Tablet

O modal deverá aproveitar o espaço disponível sem se tornar excessivamente largo.

---

# 50. Desktop

Em desktop, o modal deverá possuir largura proporcional ao conteúdo.

Não utilizar modais gigantes para tarefas simples.

---

# 51. Altura e Rolagem

Quando o conteúdo ultrapassar a altura disponível, a rolagem deverá ocorrer dentro da área adequada.

Evitar páginas inteiras atrás do modal rolando simultaneamente.

---

# 52. Formulários Longos

Se um formulário ficar longo demais para um modal confortável, considerar transferi-lo para uma página dedicada.

---

# 53. Modais Financeiros

No módulo Financeiro, modais poderão ser utilizados para:

* registrar lançamento;
* editar lançamento;
* visualizar detalhes;
* confirmar operações;
* apresentar informações complementares.

Operações financeiras deverão respeitar as permissões existentes.

---

# 54. Modais de Secretaria

Poderão ser utilizados para:

* cadastro rápido;
* edição;
* visualização;
* confirmação de ações.

---

# 55. Modais de Eventos

Poderão apresentar:

* detalhes;
* cadastro rápido;
* edição;
* confirmação.

---

# 56. Modais da Escola Bíblica

Poderão ser utilizados para:

* cadastro;
* edição;
* seleção;
* visualização;
* confirmação.

---

# 57. Modais de Comunicação

Poderão ser utilizados para:

* confirmação de envio;
* visualização de campanha;
* detalhes;
* configurações pontuais.

---

# 58. Modais Administrativos

Poderão ser utilizados para:

* edição de configurações;
* confirmação;
* permissões;
* visualização de informações.

---

# 59. Permissões

A existência de um botão que abre um modal não representa autorização.

O backend deverá validar a permissão da operação.

---

# 60. Segurança

Toda operação iniciada pelo modal deverá ser protegida no backend.

---

# 61. Validação no Backend

Nunca confiar somente na validação JavaScript.

O Django deverá validar:

* permissões;
* dados;
* regras de negócio;
* relacionamentos;
* integridade.

---

# 62. Dados Sensíveis

Modais não deverão expor:

* senhas;
* tokens;
* chaves;
* informações financeiras não autorizadas;
* dados pessoais além do necessário.

---

# 63. Concorrência

Quando um registro puder ser alterado por múltiplos usuários, o sistema deverá considerar possíveis alterações entre a abertura do modal e a submissão.

---

# 64. Feedback após Operações

O usuário deverá saber o resultado da ação.

---

# 65. Toasts e Mensagens

Quando o feedback puder ser apresentado sem interromper novamente o fluxo, preferir mensagens ou toasts padronizados pelo GDS.

Não abrir um segundo modal apenas para dizer:

```text
Operação concluída.
```

quando um feedback simples for suficiente.

---

# 66. Atualização Parcial

Após uma operação HTMX, atualizar somente a área necessária sempre que possível.

Exemplo:

```text
Modal
  ↓
Salvar
  ↓
Django
  ↓
Sucesso
  ↓
Fechar modal
  ↓
Atualizar tabela
```

---

# 67. Preservação do Contexto

Após fechar o modal, preservar:

* página atual;
* filtros;
* busca;
* ordenação;
* contexto do usuário;

quando tecnicamente apropriado.

---

# 68. Breadcrumb e Modal

O modal não substitui o breadcrumb da página.

A página principal continuará respeitando:

```text
Home > Módulo > Página
```

---

# 69. Sidebar e Modal

O modal deverá aparecer corretamente independentemente de a sidebar estar:

* aberta;
* fechada;
* recolhida;
* adaptada ao mobile.

---

# 70. Tabelas e Modal

O modal poderá ser aberto a partir de uma tabela.

Exemplo:

```text
Membros

João Silva     [Editar]
Maria Souza    [Editar]

             ↓

       Modal de edição
```

---

# 71. Cards e Modal

Cards poderão abrir modais para ações rápidas.

---

# 72. Confirmação em Duas Etapas

Operações de alto risco poderão exigir confirmação adicional quando houver justificativa.

Exemplo:

```text
Excluir registro

Digite EXCLUIR para confirmar.

[Cancelar] [Confirmar]
```

Não utilizar essa técnica para operações comuns.

---

# 73. Operações Irreversíveis

Operações irreversíveis deverão comunicar claramente essa característica.

---

# 74. Operações Financeiras Sensíveis

Operações como estorno, cancelamento ou alterações relevantes deverão possuir confirmação adequada ao risco real.

---

# 75. Exclusão Lógica

Quando o domínio utilizar exclusão lógica, a mensagem deverá refletir isso.

Não informar "excluído permanentemente" quando o registro apenas foi marcado como inativo.

---

# 76. Exclusão Física

Quando houver exclusão física real, a interface deverá deixar a consequência clara.

---

# 77. Cancelamento

Cancelar uma operação deverá possuir semântica clara.

---

# 78. Estorno

Estorno não deverá ser tratado visualmente como simples exclusão.

É uma operação de natureza financeira e deverá possuir comunicação própria.

---

# 79. Estados de Permissão

O usuário poderá:

```text
Visualizar
Editar
Administrar
```

conforme suas permissões.

---

# 80. Modal sem Permissão

Quando o usuário não possuir autorização, a ação deverá ser impedida pelo backend.

Não confiar somente em ocultar o botão.

---

# 81. Modal de Sessão

Se houver necessidade de informar expiração de sessão, a experiência deverá ser clara e não destruir dados em edição.

---

# 82. Modal de Aviso de Alterações

Quando o usuário estiver prestes a abandonar alterações não salvas, poderá ser apresentado um aviso.

---

# 83. Modal de Saída

Utilizar somente quando houver risco real de perda de dados ou alteração.

Não interromper navegação normal sem necessidade.

---

# 84. Modal de Ajuda

Ajuda contextual pequena poderá utilizar modal.

Conteúdo extenso deverá possuir página própria.

---

# 85. Modal de Detalhamento

Utilizar quando o usuário precisar consultar informações adicionais sem perder o contexto.

---

# 86. Modal de Histórico

Quando houver histórico disponível para determinada entidade, ele poderá ser apresentado em modal se o volume for pequeno.

Históricos extensos deverão utilizar página ou componente apropriado.

---

# 87. Modal de Auditoria

Informações de auditoria deverão ser exibidas somente para usuários autorizados.

---

# 88. Performance

Modais não deverão carregar grandes quantidades de dados desnecessariamente.

---

# 89. Carregamento sob Demanda

Quando o conteúdo for pesado ou pouco utilizado, considerar carregamento sob demanda.

---

# 90. HTMX e Conteúdo Parcial

HTMX poderá ser utilizado para buscar o conteúdo do modal somente quando o usuário solicitar.

---

# 91. Evitar HTML Desnecessário

Não renderizar dezenas de modais completos escondidos na página quando eles puderem ser carregados sob demanda.

---

# 92. Anti-Patterns

Evitar:

* modal dentro de modal;
* modal gigantesco;
* formulário excessivamente longo;
* excesso de confirmações;
* botão de fechar pouco visível;
* ausência de foco;
* foco escapando;
* ações destrutivas sem confirmação;
* mensagens genéricas;
* HTML duplicado;
* JavaScript excessivo;
* regra de negócio no frontend;
* exposição de dados sensíveis.

---

# 93. Regras de Implementação

Os modais deverão utilizar componentes reutilizáveis.

---

# 94. Tokens

Utilizar os tokens oficiais definidos pelo GDS.

---

# 95. CSS

A estilização deverá utilizar:

```text
static/css/design_system.css
```

Não criar cores específicas para um modal isolado.

---

# 96. Bootstrap

Bootstrap poderá fornecer a infraestrutura do componente, mas o GDS determinará a aparência final.

---

# 97. Django

O Django continuará sendo responsável por:

* validação;
* autorização;
* regras de negócio;
* persistência;
* resposta.

---

# 98. HTMX

HTMX deverá ser utilizado quando oferecer ganho real de experiência ou manutenção.

---

# 99. Alpine.js

Alpine.js deverá permanecer restrito a comportamentos locais de interface.

---

# 100. Testes

Todo novo modal deverá ser testado antes da publicação.

---

# 101. Testes Funcionais

Verificar:

* abrir;
* fechar;
* salvar;
* cancelar;
* validar;
* erro;
* sucesso;
* atualização.

---

# 102. Testes Visuais

Verificar:

* título;
* espaçamento;
* botões;
* bordas;
* sombra;
* responsividade;
* estados.

---

# 103. Testes de Acessibilidade

Verificar:

* teclado;
* foco;
* ESC;
* leitor de tela;
* contraste;
* nome acessível.

---

# 104. Testes de Responsividade

Verificar:

```text
Smartphone
Tablet
Notebook
Desktop
```

---

# 105. Testes de Permissão

Testar o comportamento com diferentes níveis de acesso.

---

# 106. Testes de Segurança

Tentar executar a operação diretamente no endpoint sem permissão.

O backend deverá impedir a operação.

---

# 107. Checklist

Antes da publicação:

* [ ] possui finalidade clara;
* [ ] título adequado;
* [ ] botão de fechamento;
* [ ] ações claras;
* [ ] botão primário;
* [ ] botão secundário;
* [ ] Danger para ações destrutivas;
* [ ] foco controlado;
* [ ] teclado;
* [ ] acessibilidade;
* [ ] responsividade;
* [ ] loading;
* [ ] erro;
* [ ] sucesso;
* [ ] permissões;
* [ ] validação backend;
* [ ] segurança;
* [ ] tokens GDS;
* [ ] CSS oficial;
* [ ] integração correta com Django;
* [ ] HTMX quando aplicável;
* [ ] Alpine.js somente quando necessário;
* [ ] Bootstrap compatível com GDS.

---

# 108. Especificações Oficiais

## GDS-MODAL-001

Todo modal deverá possuir finalidade clara.

## GDS-MODAL-002

Todo modal deverá possuir título adequado quando necessário.

## GDS-MODAL-003

Todo modal deverá possuir mecanismo de fechamento acessível.

## GDS-MODAL-004

O foco deverá ser controlado corretamente.

## GDS-MODAL-005

O usuário deverá conseguir navegar por teclado.

## GDS-MODAL-006

Ações destrutivas deverão utilizar semântica Danger.

## GDS-MODAL-007

Operações críticas deverão ser protegidas por confirmação quando necessário.

## GDS-MODAL-008

Toda operação deverá ser validada no backend.

## GDS-MODAL-009

Modais deverão respeitar permissões.

## GDS-MODAL-010

Modais deverão respeitar o GDS.

## GDS-MODAL-011

Modais deverão ser responsivos.

## GDS-MODAL-012

Modais não deverão ser utilizados para páginas completas.

## GDS-MODAL-013

Modais não deverão conter conteúdo excessivamente extenso.

## GDS-MODAL-014

Conteúdo dinâmico poderá utilizar HTMX quando apropriado.

## GDS-MODAL-015

Alpine.js não deverá conter regras de negócio.

## GDS-MODAL-016

Bootstrap não deverá substituir as regras visuais do GDS.

## GDS-MODAL-017

Dados sensíveis deverão permanecer protegidos.

## GDS-MODAL-018

Após uma operação, o contexto do usuário deverá ser preservado quando possível.

## GDS-MODAL-019

Modais deverão possuir estados de erro quando aplicável.

## GDS-MODAL-020

Modais deverão possuir estados de carregamento quando aplicável.

---

# 109. Governança

A manutenção do padrão de modais será responsabilidade da Equipe de Engenharia.

Novos padrões deverão ser documentados antes de serem adotados em larga escala.

---

# 110. Compatibilidade

Antes de alterar o componente global de modal, avaliar impacto em:

* Secretaria;
* Financeiro;
* Eventos;
* Escola Bíblica;
* Comunicação;
* Administração;
* Portal Público.

---

# 111. Evolução

O componente deverá evoluir sem quebrar fluxos existentes.

Mudanças estruturais deverão considerar compatibilidade retroativa sempre que possível.

---

# 112. Documentos Relacionados

* GDS-01 — GereIgreja Design System
* GDS-08 — Botões
* GDS-09 — Formulários
* GDS-10 — Cards
* GDS-11 — Tabelas e Listagens
* GEA-02 — Arquitetura da Plataforma
* GEA-04 — Arquitetura do Frontend
* GDF — Framework de Documentação
* GQF — Framework de Qualidade

---

# 113. Princípios Finais

O modal deverá ser utilizado como ferramenta de foco, e não como mecanismo padrão para qualquer interação.

No GereIgreja, cada modal deverá:

* preservar contexto;
* reduzir complexidade;
* comunicar claramente a ação;
* proteger o usuário;
* respeitar permissões;
* preservar dados;
* seguir o Design System;
* funcionar em diferentes dispositivos;
* ser acessível.

A melhor implementação será aquela que resolve a necessidade com a menor interrupção possível do fluxo principal.

---

# 114. Status do Documento

Pasta:

```text
docs/frameworks/
```

Arquivo:

```text
12-GDS-Modais-Dialogs-e-Confirmacoes.md
```

Documento:

```text
GDS-12
```

Framework:

```text
GDS — GereIgreja Design System
```

Versão:

```text
1.0
```

Status:

```text
Oficial
```

Responsável:

```text
Equipe de Engenharia
```

Última atualização:

```text
Agosto de 2026
```

---

# Fim do Documento

GDS-12 — Modais, Dialogs e Confirmações

GereIgreja Design System

```
```
