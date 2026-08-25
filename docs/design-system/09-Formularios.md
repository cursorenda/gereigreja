Pasta:
docs/design-system/

Arquivo:
09-Formularios.md

Documento:
GDS-09

Código:
GDS-FORMS

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

# GDS-09 — Formulários

> "Um formulário bem projetado transforma uma tarefa administrativa complexa em uma sequência clara, previsível e segura de decisões."

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia dos Formulários
4. Princípios
5. Arquitetura dos Formulários
6. Estrutura Visual
7. Hierarquia de Campos
8. Labels
9. Campos de Texto
10. Campos Numéricos
11. Campos Financeiros
12. Datas e Horários
13. Seleção de Dados
14. Campos de Pesquisa
15. Checkboxes, Radios e Switches
16. Relação com os Demais Frameworks

---

# 1. Objetivo

Este documento define os padrões oficiais para criação, implementação, validação e manutenção de formulários no GereIgreja.

O objetivo é garantir que todos os formulários da plataforma apresentem:

- consistência visual;
- clareza;
- facilidade de preenchimento;
- segurança;
- acessibilidade;
- validação adequada;
- responsividade;
- comportamento previsível;
- integração consistente com Django, HTMX e Alpine.js.

Todo formulário novo deverá seguir as diretrizes estabelecidas neste documento.

---

# 2. Escopo

Este documento aplica-se a todos os formulários utilizados no GereIgreja, incluindo:

- cadastro de membros;
- cadastro de visitantes;
- cadastro de congregações;
- cadastro de usuários;
- cadastro de famílias;
- cadastro de ministérios;
- cadastro de departamentos;
- cadastro de eventos;
- cadastro de turmas da Escola Bíblica;
- lançamentos financeiros;
- receitas;
- despesas;
- contas;
- patrimônio;
- comunicação;
- relatórios;
- configurações;
- filtros;
- pesquisas;
- autenticação;
- recuperação de acesso;
- operações administrativas.

O padrão também deverá ser utilizado em formulários exibidos dentro de:

- páginas;
- cards;
- modais;
- drawers;
- páginas de configuração;
- fluxos de múltiplas etapas.

---

# 3. Filosofia dos Formulários

Os formulários do GereIgreja deverão reduzir o esforço necessário para registrar informações.

O sistema deverá conduzir o usuário naturalmente durante o preenchimento.

Um bom formulário deverá:

- apresentar somente os campos necessários;
- agrupar informações relacionadas;
- utilizar linguagem clara;
- informar o que é obrigatório;
- validar dados corretamente;
- apresentar erros próximos ao campo correspondente;
- preservar dados já preenchidos;
- evitar solicitações redundantes;
- funcionar corretamente em dispositivos móveis.

---

# 4. Princípios

Todo formulário deverá respeitar os seguintes princípios:

## 4.1 Clareza

O usuário deverá compreender imediatamente o que deve preencher.

---

## 4.2 Consistência

Campos semelhantes deverão possuir aparência e comportamento semelhantes em toda a plataforma.

---

## 4.3 Simplicidade

Evitar campos desnecessários.

---

## 4.4 Previsibilidade

O usuário deverá saber o que acontecerá após enviar o formulário.

---

## 4.5 Segurança

Dados sensíveis deverão receber tratamento adequado.

---

## 4.6 Acessibilidade

Todos os campos deverão ser utilizáveis por teclado e tecnologias assistivas.

---

## 4.7 Responsividade

O formulário deverá funcionar adequadamente em:

- desktop;
- notebook;
- tablet;
- smartphone.

---

# 5. Arquitetura dos Formulários

A estrutura padrão deverá seguir:

```text
Página
    │
    ├── Breadcrumb
    │
    ├── Título
    │
    ├── Descrição opcional
    │
    └── Formulário
          │
          ├── Seção
          │     ├── Campo
          │     ├── Campo
          │     └── Campo
          │
          ├── Seção
          │     ├── Campo
          │     └── Campo
          │
          └── Ações
                ├── Salvar
                └── Cancelar
````

Páginas internas deverão respeitar o padrão de breadcrumb definido no GDS.

Formato oficial:

```text
Home > Módulo > Página
```

---

# 6. Estrutura Visual

Um formulário deverá possuir hierarquia visual clara.

Estrutura recomendada:

```text
Título do formulário

Descrição

────────────────────────────

Seção 1
Descrição da seção

Campo
Campo
Campo

────────────────────────────

Seção 2
Descrição da seção

Campo
Campo

────────────────────────────

Ações

[Salvar] [Cancelar]
```

---

# 7. Hierarquia de Campos

Os campos deverão ser organizados de acordo com a importância e relação entre as informações.

Priorizar:

1. identificação;
2. informações principais;
3. informações complementares;
4. informações administrativas;
5. observações;
6. ações.

Evitar apresentar campos sem relação lógica na mesma seção.

---

# 8. Labels

Todo campo deverá possuir um `label` claro.

Exemplo:

```html
<label for="nome">
    Nome completo
</label>
```

Não utilizar apenas placeholder como identificação permanente do campo.

---

## 8.1 Labels Objetivos

Preferir:

```text
Nome completo
Data de nascimento
Telefone
E-mail
Congregação
```

Evitar:

```text
Digite aqui
Informe o dado
Preencha o campo
```

---

## 8.2 Campos Obrigatórios

Campos obrigatórios deverão ser identificados de forma consistente.

Padrão recomendado:

```text
Nome completo *
```

ou utilizando indicação textual equivalente.

A indicação deverá ser compreensível também para usuários de tecnologias assistivas.

---

# 9. Campos de Texto

Os campos de texto deverão ser utilizados de acordo com a natureza da informação.

Exemplos:

```text
Nome
Sobrenome
Cidade
Bairro
Rua
Número
Complemento
Observações
```

---

## 9.1 Texto Curto

Utilizar para:

* nomes;
* códigos;
* títulos;
* identificadores.

---

## 9.2 Texto Longo

Utilizar `textarea` para:

* observações;
* descrições;
* justificativas;
* mensagens;
* informações complementares.

O campo deverá possuir altura adequada ao conteúdo esperado.

---

# 10. Campos Numéricos

Campos numéricos deverão aceitar somente valores compatíveis com sua finalidade.

Exemplos no GereIgreja:

* número de endereço;
* quantidade;
* idade;
* número de vagas;
* quantidade de alunos;
* quantidade de membros;
* valores numéricos de relatórios.

Sempre que possível, a validação deverá ocorrer tanto no frontend quanto no backend.

O backend deverá ser considerado a fonte final de validação.

---

# 11. Campos Financeiros

Campos financeiros deverão seguir o padrão monetário brasileiro.

Formato:

```text
R$ 0,00
```

Exemplos:

```text
R$ 50,00
R$ 1.250,00
R$ 10.000,50
```

Valores financeiros não deverão ser tratados como texto simples no backend.

A representação visual poderá utilizar máscara, mas o valor persistido deverá possuir estrutura adequada ao armazenamento e aos cálculos financeiros.

---

# 12. Datas e Horários

Datas deverão utilizar o padrão brasileiro na interface.

Formato apresentado ao usuário:

```text
DD/MM/AAAA
```

Exemplo:

```text
17/08/2026
```

Horários:

```text
HH:MM
```

Exemplo:

```text
18:30
```

Quando necessário, o sistema deverá utilizar controles apropriados para seleção de datas e horários.

---

# 13. Seleção de Dados

Utilizar componentes de seleção quando o conjunto de opções for previamente conhecido.

Exemplos:

```text
Congregação
Departamento
Ministério
Estado
Cidade
Status
Categoria
Forma de pagamento
```

---

## 13.1 Select

Utilizar `select` quando houver quantidade pequena ou moderada de opções.

---

## 13.2 Select com Pesquisa

Quando houver grande quantidade de opções, utilizar componente de seleção com pesquisa.

Exemplo:

```text
Selecione a congregação...

[Pesquisar]
```

Isso é especialmente importante para:

* membros;
* congregações;
* cidades;
* usuários;
* categorias;
* contas financeiras.

---

# 14. Campos de Pesquisa

Campos de pesquisa deverão possuir comportamento consistente.

Estrutura:

```text
[ 🔍 Pesquisar ]
```

Quando fizer parte de uma listagem, o campo deverá permitir filtrar os dados sem exigir etapas desnecessárias.

Filtros deverão manter seus valores enquanto o usuário navega pela interface, sempre que tecnicamente possível.

---

# 15. Checkboxes, Radios e Switches

Cada componente deverá ser utilizado de acordo com sua finalidade.

## Checkbox

Utilizar quando múltiplas opções puderem ser selecionadas.

Exemplo:

```text
☐ Receber notificações
☐ Receber comunicados
☐ Participar da Escola Bíblica
```

---

## Radio

Utilizar quando somente uma opção puder ser escolhida.

Exemplo:

```text
○ Masculino
○ Feminino
```

---

## Switch

Utilizar para estados binários que possam ser ativados ou desativados.

Exemplo:

```text
Notificações
[ Ativado ]
```

Não utilizar switch para seleção entre múltiplas opções.

---

# 16. Relação com os Demais Frameworks

O GDS-09 deverá ser utilizado em conjunto com:

* GDS-01 — GereIgreja Design System;
* GDS-03 — Paleta Oficial;
* GDS-05 — Espaçamentos;
* GDS-06 — Grid;
* GDS-07 — Iconografia;
* GDS-08 — Botões.

Também deverá permanecer compatível com:

* GEA — Arquitetura da Plataforma;
* GFE — Frontend Engineering;
* Django Forms;
* Templates Django;
* HTMX;
* Alpine.js;
* `static/css/design_system.css`.

Toda implementação deverá utilizar os tokens oficiais do Design System.

---


# 17. Campos de Identificação

Os campos de identificação são utilizados para registrar informações fundamentais das pessoas, entidades e registros administrativos do GereIgreja.

Devem priorizar:

- clareza;
- preenchimento rápido;
- validação;
- reutilização;
- prevenção de duplicidades.

---

## 17.1 Nome Completo

Utilizar:

```text
Nome completo *
````

O sistema deverá preservar o nome informado pelo usuário, realizando apenas normalizações necessárias para validação ou pesquisa.

Não utilizar limite de caracteres excessivamente restritivo.

---

## 17.2 CPF

Quando aplicável, o CPF deverá utilizar máscara de apresentação:

```text
000.000.000-00
```

A validação deverá ocorrer no backend.

O sistema deverá evitar o cadastro de pessoas duplicadas quando o CPF estiver disponível e for utilizado como identificador.

---

## 17.3 CNPJ

Quando aplicável:

```text
00.000.000/0000-00
```

A validação deverá ocorrer no backend.

---

## 17.4 E-mail

O campo deverá utilizar:

```html
type="email"
```

quando apropriado.

Exemplo:

```text
E-mail
```

A interface deverá informar claramente quando o endereço estiver inválido.

---

## 17.5 Telefone

A interface deverá aceitar números de telefone brasileiros e apresentar máscara adequada.

Exemplos:

```text
(33) 3333-3333
(33) 99999-9999
```

A máscara deverá facilitar o preenchimento sem impedir a validação do número real.

---

# 18. Campos de Endereço

Os campos de endereço deverão ser agrupados em uma seção própria.

Estrutura recomendada:

```text
Endereço

CEP
Logradouro
Número
Complemento
Bairro
Cidade
Estado
```

---

## 18.1 CEP

Formato visual:

```text
00000-000
```

Quando possível, a aplicação poderá utilizar o CEP para auxiliar o preenchimento dos demais campos.

A informação retornada automaticamente deverá permanecer editável.

---

## 18.2 Estado

Utilizar seleção entre as unidades federativas brasileiras.

---

## 18.3 Cidade

Quando houver dependência do estado selecionado, a lista de cidades deverá ser atualizada de acordo com o estado.

O componente deverá evitar carregamento desnecessário de milhares de opções simultaneamente.

---

# 19. Campos de Membros

O cadastro de membros é uma das principais áreas de utilização dos formulários no GereIgreja.

O formulário deverá ser dividido logicamente.

Exemplo:

```text
Dados pessoais

Nome completo
CPF
Data de nascimento
Sexo
Estado civil

Contato

Telefone
Celular
E-mail

Endereço

CEP
Logradouro
Número
Complemento
Bairro
Cidade
Estado

Dados eclesiásticos

Congregação
Data de entrada
Data de batismo
Ministério
Departamento
Observações
```

As informações deverão ser agrupadas de acordo com sua finalidade.

---

# 20. Campos de Congregação

O formulário de congregação deverá possuir estrutura própria.

Exemplo:

```text
Dados da Congregação

Nome
Código
Endereço
Cidade
Estado
Telefone
E-mail
Responsável
Status
```

O campo de status deverá utilizar componente apropriado para representar estados como:

```text
Ativa
Inativa
```

A exclusão de uma congregação deverá ser tratada como ação administrativa crítica.

---

# 21. Formulários Financeiros

Os formulários financeiros exigem maior rigor de validação.

Exemplos:

* receitas;
* despesas;
* transferências;
* contas;
* categorias;
* centros de custo;
* formas de pagamento;
* lançamentos.

---

## 21.1 Lançamento Financeiro

Estrutura recomendada:

```text
Tipo
Data
Descrição
Categoria
Conta
Valor
Forma de pagamento
Observação
```

---

## 21.2 Valor

O campo deverá apresentar:

```text
Valor (R$)
```

Exemplo:

```text
R$ 1.250,00
```

O backend deverá armazenar o valor utilizando representação numérica apropriada para operações financeiras.

Não utilizar `float` para representar valores monetários quando isso puder introduzir imprecisão.

---

## 21.3 Categoria

A categoria deverá ser selecionada através de componente padronizado.

Quando houver grande quantidade de categorias, disponibilizar pesquisa.

---

## 21.4 Confirmação Financeira

Operações financeiras críticas deverão apresentar confirmação antes da execução quando houver possibilidade de:

* perda de dados;
* alteração de saldo;
* cancelamento;
* exclusão;
* estorno.

---

# 22. Formulários de Eventos

Os formulários de eventos deverão permitir registrar as informações necessárias para organização e divulgação.

Exemplo:

```text
Nome do evento
Descrição
Data
Horário
Local
Responsável
Categoria
Status
Observações
```

Quando aplicável, poderão existir:

```text
Data de início
Data de término
Horário de início
Horário de término
```

---

# 23. Formulários da Escola Bíblica

Os formulários da Escola Bíblica deverão contemplar as necessidades específicas do módulo.

Exemplos:

```text
Turma
Professor
Classe
Faixa etária
Dia
Horário
Sala
Status
```

Para matrícula:

```text
Aluno
Turma
Data da matrícula
Status
Observação
```

Os campos deverão evitar duplicidade de matrícula quando houver regras específicas para o mesmo aluno e turma.

---

# 24. Formulários de Comunicação

Os formulários de comunicação deverão deixar claro:

* destinatários;
* assunto;
* conteúdo;
* canal;
* agendamento;
* status.

Exemplo:

```text
Tipo de comunicação

Destinatários

Assunto

Mensagem

Data de envio

Horário

[Enviar]
[Agendar]
[Cancelar]
```

Quando uma mensagem for enviada imediatamente, a interface deverá apresentar confirmação clara antes da execução, especialmente em operações de grande alcance.

---

# 25. Validação

A validação dos formulários deverá ocorrer em duas camadas.

```text
Frontend
    ↓
Backend
```

A validação do frontend melhora a experiência.

A validação do backend garante a integridade dos dados.

A validação do frontend nunca deverá ser considerada mecanismo suficiente de segurança.

---

## 25.1 Validação em Tempo Real

Quando apropriado, o sistema poderá validar um campo durante o preenchimento.

Exemplos:

* CPF;
* e-mail;
* CEP;
* senha;
* campos obrigatórios.

A validação não deverá interromper desnecessariamente o usuário enquanto ele ainda estiver digitando.

---

## 25.2 Erros de Validação

A mensagem deverá aparecer próxima ao campo correspondente.

Exemplo:

```text
E-mail *

usuario@exemplo

⚠ Informe um endereço de e-mail válido.
```

A mensagem deverá explicar:

1. qual é o problema;
2. como corrigi-lo.

Evitar mensagens genéricas como:

```text
Erro!
```

ou:

```text
Valor inválido.
```

quando uma explicação melhor estiver disponível.

---

# 26. Estados dos Campos

Todo componente de formulário deverá considerar os estados necessários.

## Normal

Campo disponível para preenchimento.

## Focus

Campo atualmente selecionado.

## Filled

Campo preenchido corretamente.

## Disabled

Campo temporariamente indisponível.

## Readonly

Campo visível, mas não editável.

## Error

Campo contendo informação inválida.

## Success

Campo validado corretamente quando houver necessidade de apresentar esse estado.

## Loading

Campo aguardando resposta de uma operação assíncrona.

---

# 27. Mensagens de Erro

As mensagens deverão ser:

* claras;
* objetivas;
* próximas ao campo;
* úteis;
* orientadas à solução.

Exemplo:

```text
Senha *

123

⚠ A senha deve possuir pelo menos 8 caracteres.
```

Evitar:

```text
⚠ Erro de validação.
```

---

# 28. Preservação dos Dados

Quando ocorrer erro de validação, o sistema deverá preservar os valores já preenchidos sempre que possível.

O usuário não deverá precisar preencher novamente todo o formulário por causa de um erro em apenas um campo.

Em operações HTMX, a atualização parcial da interface deverá evitar perda desnecessária de dados.

---

# 29. Formulários com HTMX

O GereIgreja poderá utilizar HTMX para:

* submissão assíncrona;
* validação;
* atualização parcial;
* carregamento dependente;
* busca;
* filtros;
* inclusão de registros;
* edição;
* exclusão.

Exemplo conceitual:

```html
<form
    hx-post="/membros/novo/"
    hx-target="#form-container"
    hx-swap="outerHTML">
```

O comportamento deverá preservar a experiência do usuário e fornecer feedback adequado.

---

# 30. Formulários com Alpine.js

Alpine.js poderá ser utilizado para estados locais.

Exemplos:

* mostrar ou ocultar campos;
* alternar seções;
* controlar etapas;
* abrir componentes;
* controlar filtros;
* exibir campos condicionais.

Exemplo:

```html
<div x-data="{ mostrarEndereco: true }">
```

O Alpine.js não deverá substituir as regras de negócio do backend.

---

# 31. Django Forms

Quando o fluxo utilizar Django Forms, as regras de validação deverão permanecer alinhadas entre:

```text
Modelo
   ↓
Form
   ↓
View
   ↓
Template
```

O template deverá utilizar os padrões visuais definidos pelo GDS.

A existência de um componente visual padronizado não deverá eliminar a validação realizada pelo Django.

---

# 32. Formulários em Modais

Formulários simples poderão ser apresentados em modais.

Exemplos:

* adicionar categoria;
* criar pequena configuração;
* cadastrar item rápido;
* editar informação simples.

Formulários extensos deverão preferencialmente utilizar uma página própria.

Evitar colocar formulários complexos dentro de modais pequenos.

---

# 33. Formulários em Múltiplas Etapas

Quando o cadastro possuir grande quantidade de informações, poderá ser utilizado um fluxo em etapas.

Exemplo:

```text
1. Dados pessoais
        ↓
2. Contato
        ↓
3. Endereço
        ↓
4. Dados eclesiásticos
        ↓
5. Confirmação
```

O usuário deverá visualizar claramente:

* etapa atual;
* etapas concluídas;
* etapas restantes;
* possibilidade de retornar.

Os dados preenchidos deverão ser preservados entre as etapas.

---

# 34. Botões de Formulário

Os botões deverão seguir integralmente o:

```text
GDS-08 — Botões
```

Ações comuns:

```text
[Salvar]
[Salvar e Novo]
[Cancelar]
[Voltar]
[Próximo]
[Finalizar]
```

A ação principal deverá possuir maior destaque visual.

---

# 35. Responsividade

Formulários deverão adaptar sua estrutura conforme a largura disponível.

## Desktop

Campos relacionados poderão ser apresentados em múltiplas colunas.

Exemplo:

```text
Nome completo                 CPF
[____________________]        [____________]
```

---

## Tablet

Reduzir o número de colunas conforme necessário.

---

## Smartphone

Priorizar uma coluna:

```text
Nome completo
[________________________]

CPF
[________________________]

Telefone
[________________________]

[Salvar]
```

Campos nunca deverão ficar excessivamente estreitos.

---

````markdown
# 36. Acessibilidade

A acessibilidade dos formulários é requisito obrigatório do GereIgreja.

Todos os formulários deverão ser utilizáveis por pessoas com diferentes níveis de capacidade visual, motora, cognitiva e tecnológica.

---

## 36.1 Associação entre Label e Campo

Todo campo deverá possuir associação correta entre `label` e elemento de entrada.

Exemplo:

```html
<label for="nome">Nome completo</label>
<input id="nome" name="nome" type="text">
````

O atributo `for` deverá corresponder ao `id` do campo.

---

## 36.2 Navegação por Teclado

Todos os campos deverão ser acessíveis utilizando teclado.

A sequência deverá seguir a ordem lógica da interface.

Evitar alterações artificiais no fluxo de `Tab`.

---

## 36.3 Foco Visível

O campo em foco deverá apresentar indicação visual clara.

Nunca remover o foco sem fornecer alternativa visual equivalente.

---

## 36.4 Mensagens para Tecnologias Assistivas

Mensagens de erro deverão ser associadas ao campo correspondente.

Quando necessário, utilizar:

```html
aria-describedby
```

e mecanismos apropriados para comunicar alterações dinâmicas.

---

## 36.5 Campos Somente com Ícones

Não utilizar ícones como único identificador de uma função de formulário sem descrição acessível.

---

# 37. Segurança

Os formulários deverão considerar segurança desde sua implementação.

---

## 37.1 Validação no Backend

Nenhum dado enviado pelo usuário deverá ser considerado confiável apenas porque passou pela validação do frontend.

---

## 37.2 Proteção CSRF

Formulários que alteram dados deverão utilizar os mecanismos de proteção CSRF fornecidos pelo Django.

---

## 37.3 Dados Sensíveis

Informações sensíveis deverão receber tratamento adequado.

Exemplos:

* CPF;
* credenciais;
* informações financeiras;
* dados pessoais;
* informações administrativas.

Não expor dados sensíveis desnecessariamente em mensagens de erro, URLs ou elementos públicos.

---

## 37.4 Permissões

A interface não deverá ser considerada mecanismo de autorização.

Mesmo que um campo ou botão esteja oculto no frontend, a operação deverá ser protegida no backend.

---

# 38. Performance

Formulários deverão evitar operações desnecessárias.

---

## 38.1 Campos Dependentes

Quando um campo depender de outro, o carregamento deverá ocorrer somente quando necessário.

Exemplo:

```text
Estado
   ↓
Cidade
```

A seleção de um estado poderá atualizar as cidades disponíveis sem recarregar toda a página.

---

## 38.2 Grandes Listas

Não carregar milhares de opções em um `select` quando uma busca dinâmica for mais adequada.

Exemplos:

* membros;
* cidades;
* congregações;
* usuários;
* categorias.

---

## 38.3 Debounce

Campos de pesquisa com requisições automáticas deverão utilizar debounce quando apropriado para evitar excesso de requisições.

---

# 39. Feedback ao Usuário

Toda operação deverá fornecer retorno adequado.

---

## Sucesso

Exemplo:

```text
✓ Membro cadastrado com sucesso.
```

---

## Erro

Exemplo:

```text
⚠ Não foi possível salvar o membro. Verifique os campos destacados.
```

---

## Processamento

Exemplo:

```text
Salvando...
```

O usuário nunca deverá ficar sem saber se uma ação foi executada.

---

# 40. Formulários de Exclusão

A exclusão deverá ser tratada como operação crítica.

Antes da exclusão, quando necessário:

```text
Excluir membro?

Esta ação não poderá ser desfeita.

[Excluir] [Cancelar]
```

O botão `Excluir` deverá utilizar:

```text
Danger
```

conforme definido no GDS-08.

Quando tecnicamente aplicável, o sistema deverá priorizar exclusão lógica.

---

# 41. Formulários de Configuração

Formulários de configuração deverão agrupar opções relacionadas.

Exemplo:

```text
Configurações Gerais

Informações da Igreja

Nome
CNPJ
Telefone
E-mail

Configurações de Comunicação

E-mail
SMS
Notificações

Preferências

Fuso horário
Formato de data
Preferências de exibição
```

Evitar reunir configurações sem relação em uma única seção extensa.

---

# 42. Campos Condicionais

Campos condicionais deverão aparecer somente quando forem relevantes.

Exemplo:

```text
Forma de pagamento

( ) Dinheiro
( ) PIX
( ) Cartão
( ) Transferência
```

Se a opção escolhida exigir informação adicional:

```text
PIX

Chave PIX
[________________________]
```

A interface deverá explicar por que o novo campo apareceu.

---

# 43. Formulários de Busca e Filtros

Filtros deverão ser simples e rápidos.

Exemplo:

```text
Pesquisar membro
[________________________]

Congregação
[Todos ▼]

Status
[Todos ▼]

[Filtrar] [Limpar]
```

---

## 43.1 Preservação dos Filtros

Após uma ação como:

* paginação;
* ordenação;
* atualização parcial;
* edição;
* retorno à listagem;

os filtros deverão ser preservados quando isso fizer sentido para o fluxo.

---

## 43.2 Limpar Filtros

O botão `Limpar` deverá remover os filtros aplicados e retornar à consulta padrão.

---

# 44. Upload de Arquivos

Quando o sistema permitir envio de arquivos, o componente deverá informar:

* tipos aceitos;
* tamanho máximo;
* quantidade máxima;
* estado do upload;
* resultado da operação.

Exemplo:

```text
Foto do membro

[Selecionar arquivo]

Formatos aceitos: JPG, PNG
Tamanho máximo: 5 MB
```

O backend deverá validar novamente o arquivo recebido.

---

# 45. Formulários Financeiros — Regras Adicionais

Operações financeiras exigem maior rigor.

---

## 45.1 Valores

Não permitir valores inválidos ou ambíguos.

---

## 45.2 Datas

A data do lançamento deverá ser explicitamente informada.

---

## 45.3 Categoria

Todo lançamento deverá utilizar categoria válida quando essa informação for obrigatória.

---

## 45.4 Conta

A conta financeira deverá ser selecionada de forma clara.

---

## 45.5 Confirmação

Operações como:

* exclusão;
* estorno;
* encerramento;
* alterações relevantes;

deverão utilizar confirmação adequada.

---

# 46. Formulários de Membros — Regras Adicionais

O cadastro de membros deverá evitar duplicidade sempre que possível.

Antes de criar um novo membro, o sistema poderá auxiliar na identificação de registros existentes utilizando informações como:

* nome;
* CPF;
* telefone;
* e-mail.

A existência de possíveis duplicidades deverá ser apresentada de forma clara sem bloquear automaticamente um cadastro legítimo quando a regra de negócio permitir.

---

# 47. Formulários de Eventos — Regras Adicionais

Os formulários de eventos deverão validar:

* data;
* horário;
* período;
* local;
* status;
* informações obrigatórias.

Quando houver data inicial e final:

```text
Data inicial ≤ Data final
```

Quando houver horário inicial e final no mesmo período:

```text
Horário inicial < Horário final
```

As regras poderão variar conforme o tipo de evento.

---

# 48. Formulários da Escola Bíblica — Regras Adicionais

Os formulários deverão considerar:

* aluno;
* turma;
* professor;
* período;
* status;
* frequência;
* matrícula.

O sistema deverá evitar registros incompatíveis com as regras do módulo.

---

# 49. Formulários de Comunicação — Regras Adicionais

Antes do envio de uma comunicação, o sistema deverá apresentar informações suficientes para confirmação.

Exemplo:

```text
Destinatários: 128 pessoas

Canal: E-mail

Assunto:
Reunião de domingo

[Enviar agora]
```

Quando houver grande quantidade de destinatários, operações de envio deverão possuir mecanismos apropriados de processamento e acompanhamento.

---

# 50. Estados de Persistência

O formulário deverá distinguir claramente entre:

```text
Novo
```

```text
Editando
```

```text
Salvando
```

```text
Salvo
```

```text
Erro
```

```text
Excluído
```

O usuário deverá compreender em qual estado o registro se encontra.

---

# 51. Prevenção contra Duplo Envio

Após o envio de um formulário, o sistema deverá impedir múltiplos envios acidentais.

Exemplo:

```text
[Salvando...]
```

O botão deverá permanecer indisponível enquanto a operação estiver em andamento.

Isso é especialmente importante para:

* lançamentos financeiros;
* inscrições;
* matrículas;
* criação de membros;
* envio de comunicação;
* criação de eventos.

---

# 52. Autosave

O salvamento automático poderá ser utilizado quando houver benefício real para o usuário.

É especialmente adequado para:

* editores longos;
* rascunhos;
* mensagens;
* conteúdos que exigem preenchimento prolongado.

Não deverá ser utilizado indiscriminadamente em operações que exigem confirmação explícita.

---

# 53. Dirty State

Quando o usuário alterar informações e tentar sair sem salvar, o sistema poderá informar:

```text
Existem alterações não salvas.

Deseja realmente sair?

[Sair sem salvar] [Continuar editando]
```

Esse comportamento deverá ser utilizado principalmente em formulários extensos ou críticos.

---

# 54. Formulários Vazios

Quando não houver dados disponíveis para seleção, o componente deverá informar a situação.

Exemplo:

```text
Nenhuma congregação cadastrada.

Cadastre uma congregação para continuar.
```

Quando apropriado, disponibilizar ação contextual:

```text
[+ Criar congregação]
```

---

# 55. Formulários com Dependências

Quando um campo depender de outro, o estado deverá ser explícito.

Exemplo:

```text
Congregação
[Selecione uma congregação ▼]

Departamento
[Selecione uma congregação primeiro]
```

O sistema não deverá apresentar uma lista aparentemente vazia sem explicar a causa.

---

# 56. Formulários e Breadcrumb

Páginas internas deverão seguir o padrão oficial:

```text
Home > Módulo > Página
```

Exemplo:

```text
Home > Secretaria > Novo Membro
```

Isso permite que o usuário compreenda sua localização dentro da plataforma.

---

# 57. Formulários e Menu Lateral

Quando houver sidebar, a página deverá oferecer o controle padrão de mostrar/ocultar menu definido pelo GDS.

O controle deverá permanecer próximo ao título da página quando aplicável.

---

# 58. Evidências Arquiteturais

As regras deste documento deverão permanecer alinhadas à arquitetura real do GereIgreja.

---

## EA-GDS-051

Os formulários deverão utilizar os tokens oficiais definidos pelo Design System.

---

## EA-GDS-052

A estilização deverá utilizar:

```text
static/css/design_system.css
```

quando o componente depender dos estilos globais do GDS.

---

## EA-GDS-053

A validação final dos dados deverá ocorrer no backend.

---

## EA-GDS-054

Django deverá permanecer responsável pelas regras de negócio e persistência.

---

## EA-GDS-055

HTMX poderá ser utilizado para interações assíncronas e atualizações parciais.

---

## EA-GDS-056

Alpine.js deverá ser utilizado para comportamentos locais de interface.

---

## EA-GDS-057

Acessibilidade deverá fazer parte da implementação do componente, e não ser adicionada posteriormente.

---

# 59. Especificações Oficiais

## GDS-FORM-001

Todo formulário deverá possuir identificação clara.

---

## GDS-FORM-002

Todo campo deverá possuir `label` associado.

---

## GDS-FORM-003

Campos obrigatórios deverão ser identificados claramente.

---

## GDS-FORM-004

A validação deverá ocorrer no backend.

---

## GDS-FORM-005

Erros deverão ser apresentados próximos aos campos correspondentes.

---

## GDS-FORM-006

O sistema deverá preservar dados preenchidos quando ocorrer erro de validação, sempre que possível.

---

## GDS-FORM-007

Formulários deverão utilizar componentes oficiais do GereIgreja.

---

## GDS-FORM-008

Formulários deverão utilizar tokens do Design System.

---

## GDS-FORM-009

Formulários deverão ser responsivos.

---

## GDS-FORM-010

Formulários deverão ser acessíveis por teclado.

---

## GDS-FORM-011

Campos somente com ícones deverão possuir descrição acessível.

---

## GDS-FORM-012

Operações assíncronas deverão apresentar estado de processamento.

---

## GDS-FORM-013

Operações críticas deverão possuir confirmação quando necessário.

---

## GDS-FORM-014

Ações financeiras deverão utilizar validações específicas.

---

## GDS-FORM-015

O frontend não deverá ser considerado mecanismo de segurança.

---

## GDS-FORM-016

Novos componentes de formulário deverão ser documentados antes de sua adoção.

---

# 60. Checklist Geral

Antes da publicação de qualquer formulário, verificar:

## Estrutura

* [ ] possui título;
* [ ] possui descrição quando necessária;
* [ ] possui breadcrumb;
* [ ] campos estão agrupados logicamente;
* [ ] ações estão claramente identificadas.

## Campos

* [ ] todos possuem labels;
* [ ] obrigatórios estão identificados;
* [ ] tipos de campo são adequados;
* [ ] máscaras são utilizadas quando necessárias;
* [ ] placeholders não substituem labels.

## Validação

* [ ] frontend validado;
* [ ] backend validado;
* [ ] mensagens de erro claras;
* [ ] dados preservados após erro;
* [ ] regras específicas do módulo implementadas.

## Interação

* [ ] estado normal;
* [ ] focus;
* [ ] disabled;
* [ ] readonly;
* [ ] error;
* [ ] loading;
* [ ] success quando aplicável.

## Segurança

* [ ] CSRF;
* [ ] permissões;
* [ ] validação backend;
* [ ] proteção de dados sensíveis;
* [ ] upload validado quando aplicável.

## Responsividade

* [ ] desktop;
* [ ] notebook;
* [ ] tablet;
* [ ] smartphone.

## Acessibilidade

* [ ] teclado;
* [ ] foco visível;
* [ ] labels associados;
* [ ] mensagens acessíveis;
* [ ] contraste;
* [ ] áreas de toque adequadas.

## Engenharia

* [ ] utiliza Design System;
* [ ] utiliza `design_system.css`;
* [ ] utiliza Django corretamente;
* [ ] HTMX aplicado quando apropriado;
* [ ] Alpine.js aplicado somente quando necessário;
* [ ] não possui CSS inline desnecessário;
* [ ] não duplica componentes existentes.

---

# 61. Glossário

## Campo

Elemento utilizado para entrada ou seleção de informações.

## Label

Texto que identifica um campo.

## Placeholder

Texto auxiliar apresentado dentro de um campo vazio.

## Validation

Processo de verificação da validade dos dados.

## Máscara

Formatação visual aplicada durante o preenchimento.

## Input

Campo destinado à entrada de dados.

## Select

Componente utilizado para seleção de uma opção.

## Checkbox

Componente utilizado para seleção independente de múltiplas opções.

## Radio

Componente utilizado para selecionar uma opção entre alternativas mutuamente exclusivas.

## Switch

Componente utilizado para representar um estado binário.

## HTMX

Tecnologia utilizada para interações assíncronas entre frontend e servidor.

## Alpine.js

Biblioteca utilizada para comportamentos locais de interface.

## Django Forms

Sistema do Django utilizado para construção e validação de formulários.

## Dirty State

Estado no qual o formulário possui alterações ainda não persistidas.

## Soft Delete

Estratégia na qual um registro é marcado como excluído sem necessariamente ser removido fisicamente do banco de dados.

---

# 62. Governança

Os componentes de formulário fazem parte da infraestrutura oficial do GereIgreja Design System.

Alterações deverão ser centralizadas e documentadas.

---

## 62.1 Novos Componentes

Um novo componente somente deverá ser criado quando:

1. componentes existentes não atenderem ao requisito;
2. houver necessidade recorrente;
3. existir justificativa de UX;
4. houver compatibilidade com o GDS;
5. houver aprovação da Engenharia.

---

## 62.2 Alterações Globais

Alterações em:

* campos;
* labels;
* espaçamentos;
* bordas;
* cores;
* tipografia;
* estados;
* validações visuais;

deverão ser tratadas como alterações do Design System quando afetarem componentes globais.

---

## 62.3 Compatibilidade

As alterações deverão considerar os módulos:

* Secretaria;
* Financeiro;
* Eventos;
* Escola Bíblica;
* Comunicação;
* Administração;
* Portal Público.

---

# 63. Roadmap

## Fase 1 — Padronização

* consolidar componentes;
* eliminar estilos duplicados;
* padronizar mensagens;
* padronizar validações visuais;
* revisar formulários existentes.

---

## Fase 2 — Componentização

Criar componentes reutilizáveis para:

* input;
* textarea;
* select;
* select com pesquisa;
* checkbox;
* radio;
* switch;
* date picker;
* time picker;
* currency input;
* upload;
* mensagens de erro;
* mensagens de sucesso.

---

## Fase 3 — Integração

Integrar oficialmente os componentes com:

* Django Forms;
* Bootstrap;
* HTMX;
* Alpine.js;
* Design Tokens;
* `static/css/design_system.css`.

---

## Fase 4 — Evolução

Criar uma biblioteca interna de componentes de formulário reutilizáveis para todos os módulos do GereIgreja.

---

# 64. Documentos Relacionados

## GereIgreja Design System

```text
GDS-01 — Introdução
GDS-02 — Princípios
GDS-03 — Cores
GDS-04 — Tipografia
GDS-05 — Espaçamento
GDS-06 — Grid
GDS-07 — Iconografia
GDS-08 — Botões
GDS-09 — Formulários
GDS-10 — Cards
GDS-11 — Tabelas
GDS-12 — Alertas
GDS-13 — Modais
GDS-14 — Navegação
GDS-15 — Dashboards
GDS-16 — Acessibilidade
GDS-17 — Animações
GDS-18 — Boas Práticas
GDS-19 — Governança
```

## GereIgreja Frontend Engineering

```text
GFE-01 — Frontend Architecture
GFE-02 — Estrutura de Pastas
GFE-03 — Componentes
GFE-04 — Layouts
GFE-05 — Templates
GFE-06 — Assets
GFE-07 — CSS
GFE-08 — JavaScript
GFE-09 — HTMX
GFE-10 — Alpine.js
GFE-11 — Dashboards
```

---

# 65. Conclusão

Os formulários constituem uma das principais interfaces operacionais do GereIgreja.

É por meio deles que informações de membros, congregações, eventos, Escola Bíblica, comunicação, configurações e operações financeiras são registradas e mantidas.

Por esse motivo, a qualidade dos formulários influencia diretamente a confiabilidade dos dados e a experiência dos usuários.

O GDS-09 estabelece uma linguagem única para:

* apresentação dos campos;
* organização das informações;
* validação;
* feedback;
* acessibilidade;
* segurança;
* responsividade;
* integração com o backend;
* operações assíncronas.

Todos os novos formulários deverão utilizar os padrões definidos neste documento.

Formulários existentes deverão ser gradualmente adaptados ao padrão oficial sempre que forem modificados.

Nenhum módulo deverá criar uma linguagem própria de campos ou validações sem justificativa e aprovação da Engenharia.

O objetivo final é proporcionar ao usuário uma experiência consistente em toda a plataforma, independentemente do módulo utilizado.

---

# Status do Documento

Pasta:

```text
docs/design-system/
```

Arquivo:

```text
09-Formularios.md
```

Documento:

```text
GDS-09
```

Código:

```text
GDS-FORMS
```

Versão:

```text
1.0
```

Status:

```text
OFICIAL
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

