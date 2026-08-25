````markdown
Pasta:
docs/design-system/

Arquivo:
10-Cards.md

Documento:
GDS-10

Código:
GDS-CARDS

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

# GDS-10 — Cards

> "Cards devem organizar informações relacionadas sem transformar a interface em uma coleção de caixas. No GereIgreja, cada card deve possuir propósito, hierarquia e comportamento claramente definidos."

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia dos Cards
4. Princípios
5. Arquitetura
6. Estrutura Oficial
7. Hierarquia Visual
8. Tipos de Cards
9. Cards de Indicadores
10. Cards de Resumo
11. Cards de Registros
12. Cards de Ações
13. Cards Financeiros
14. Cards de Eventos
15. Cards da Escola Bíblica
16. Cards de Comunicação
17. Relação com os Demais Frameworks

---

# 1. Objetivo

Este documento estabelece o padrão oficial para utilização de cards na plataforma GereIgreja.

Seu objetivo é garantir que informações relacionadas sejam agrupadas de maneira consistente, clara e visualmente organizada.

Os cards deverão contribuir para:

- organização da informação;
- leitura rápida;
- hierarquia visual;
- produtividade;
- responsividade;
- reutilização;
- acessibilidade;
- consistência entre módulos.

Cards não deverão ser utilizados apenas como elementos decorativos.

Todo card deverá possuir uma finalidade clara.

---

# 2. Escopo

Este documento aplica-se aos cards utilizados em:

- dashboards;
- Secretaria;
- Financeiro;
- Eventos;
- Escola Bíblica;
- Comunicação;
- Administração;
- Portal Público;
- relatórios;
- páginas de detalhes;
- listas;
- painéis de indicadores;
- atalhos de funcionalidades;
- resumos de registros.

Também se aplica a cards apresentados dentro de:

- páginas;
- modais;
- drawers;
- seções;
- grids responsivos.

---

# 3. Filosofia dos Cards

O card deve funcionar como uma unidade visual de informação.

Cada card deverá responder claramente a uma pergunta:

- O que esta informação representa?
- Por que ela está sendo apresentada?
- Qual é sua importância?
- Existe alguma ação relacionada?
- O usuário precisa interagir com ela?

Quando essas respostas não forem claras, o uso de um card deverá ser reconsiderado.

---

# 4. Princípios

Os cards do GereIgreja deverão seguir os seguintes princípios:

- propósito;
- simplicidade;
- hierarquia;
- consistência;
- legibilidade;
- baixo ruído visual;
- reutilização;
- acessibilidade;
- responsividade.

---

## 4.1 Propósito

Cada card deverá possuir uma função definida.

---

## 4.2 Hierarquia

Informações importantes deverão possuir maior destaque visual.

---

## 4.3 Consistência

Cards semelhantes deverão possuir estrutura semelhante em toda a plataforma.

---

## 4.4 Simplicidade

Evitar excesso de informações dentro de um único card.

---

## 4.5 Responsividade

O card deverá adaptar-se ao espaço disponível.

---

# 5. Arquitetura

A estrutura conceitual de um card poderá seguir:

```text
Card
 │
 ├── Header
 │     ├── Ícone opcional
 │     ├── Título
 │     └── Ações opcionais
 │
 ├── Body
 │     ├── Conteúdo principal
 │     └── Informações complementares
 │
 └── Footer opcional
       ├── Metadados
       └── Ações
````

Nem todo card deverá possuir todas as partes.

---

# 6. Estrutura Oficial

Estrutura recomendada:

```text
┌─────────────────────────────────────┐
│ Título                         ⋮    │
├─────────────────────────────────────┤
│                                     │
│ Conteúdo principal                  │
│                                     │
│ Informação complementar             │
│                                     │
├─────────────────────────────────────┤
│ Metadado              [Ação]        │
└─────────────────────────────────────┘
```

O card deverá utilizar somente as regiões necessárias.

Evitar headers ou footers vazios.

---

# 7. Hierarquia Visual

A hierarquia deverá seguir:

```text
Título
   ↓
Informação principal
   ↓
Informação secundária
   ↓
Metadados
   ↓
Ações
```

A informação mais importante deverá ser percebida primeiro.

---

# 8. Tipos de Cards

O GereIgreja poderá utilizar os seguintes tipos oficiais:

* Card de Indicador;
* Card de Resumo;
* Card de Registro;
* Card de Ação;
* Card Financeiro;
* Card de Evento;
* Card de Turma;
* Card de Comunicação;
* Card de Configuração;
* Card de Informação;
* Card de Status.

Novos tipos deverão ser documentados antes de serem introduzidos.

---

# 9. Cards de Indicadores

Cards de indicadores deverão apresentar números relevantes para o acompanhamento da gestão.

Exemplos:

```text
┌─────────────────────────────┐
│ Membros                     │
│                             │
│ 1.248                       │
│ +12 este mês                │
└─────────────────────────────┘
```

Indicadores poderão representar:

* quantidade de membros;
* visitantes;
* congregações;
* receitas;
* despesas;
* eventos;
* alunos;
* usuários;
* comunicados.

---

## 9.1 Estrutura

Um card de indicador deverá possuir:

```text
Título
Valor principal
Variação ou contexto opcional
Ícone opcional
```

---

## 9.2 Valor Principal

O número deverá possuir destaque visual superior às informações secundárias.

Exemplo:

```text
1.248
```

---

## 9.3 Contexto

Quando houver comparação, informar claramente o período.

Exemplo:

```text
+12 este mês
```

Evitar apresentar:

```text
+12
```

sem contexto quando o significado não for evidente.

---

# 10. Cards de Resumo

Utilizados para apresentar uma visão resumida de determinado módulo.

Exemplo:

```text
┌────────────────────────────────┐
│ Financeiro                     │
│                                │
│ Receitas       R$ 18.500,00    │
│ Despesas       R$ 11.200,00    │
│ Saldo          R$  7.300,00    │
│                                │
│ [Ver financeiro]               │
└────────────────────────────────┘
```

Esses cards deverão apresentar somente os dados mais relevantes.

---

# 11. Cards de Registros

Utilizados para representar registros individuais.

Exemplos:

* membro;
* evento;
* congregação;
* turma;
* lançamento financeiro.

Exemplo:

```text
┌────────────────────────────────┐
│ João da Silva                  │
│                                │
│ Congregação: Plautino Soares  │
│ Telefone: (33) 99999-9999     │
│ Status: Ativo                  │
│                                │
│ [Visualizar] [Editar]         │
└────────────────────────────────┘
```

Cards de registros não deverão substituir tabelas quando a comparação entre muitos registros for a principal necessidade.

---

# 12. Cards de Ações

Utilizados para oferecer atalhos para funcionalidades.

Exemplo:

```text
┌─────────────────────────────┐
│ +                           │
│ Novo Membro                 │
│ Cadastre um novo membro     │
│                             │
│ [Cadastrar]                 │
└─────────────────────────────┘
```

Devem possuir:

* título claro;
* descrição curta;
* ação evidente.

---

# 13. Cards Financeiros

Cards financeiros deverão possuir hierarquia visual adequada para valores monetários.

Exemplo:

```text
┌─────────────────────────────┐
│ Receitas                    │
│                             │
│ R$ 25.430,00                │
│ Agosto/2026                 │
└─────────────────────────────┘
```

Os valores deverão utilizar a representação monetária oficial do sistema.

Quando houver comparação:

```text
Receitas
R$ 25.430,00

+8,4% em relação a julho
```

As informações deverão deixar claro o período analisado.

---

# 14. Cards de Eventos

Cards de eventos deverão priorizar:

* nome;
* data;
* horário;
* local;
* status.

Exemplo:

```text
┌────────────────────────────────┐
│ Culto dos Jovens               │
│                                │
│ 01/08/2026                     │
│ 18:00                          │
│ Congregação Plautino Soares   │
│                                │
│ [Ver evento]                   │
└────────────────────────────────┘
```

Quando o evento possuir imagem, ela deverá complementar o conteúdo e não prejudicar a leitura das informações principais.

---

# 15. Cards da Escola Bíblica

Cards da Escola Bíblica poderão representar:

* turmas;
* professores;
* alunos;
* aulas;
* períodos.

Exemplo:

```text
┌────────────────────────────────┐
│ Classe de Adultos              │
│                                │
│ Professor: João Silva          │
│ Alunos: 24                     │
│ Domingo — 09:00               │
│                                │
│ [Ver turma]                    │
└────────────────────────────────┘
```

---

# 16. Cards de Comunicação

Cards de comunicação poderão representar:

* comunicados;
* campanhas;
* mensagens;
* agendamentos;
* status de envio.

Exemplo:

```text
┌────────────────────────────────┐
│ Reunião de domingo             │
│                                │
│ Destinatários: 128             │
│ Canal: E-mail                  │
│ Status: Agendado               │
│                                │
│ [Visualizar]                   │
└────────────────────────────────┘
```

---

# 17. Relação com os Demais Frameworks

O GDS-10 deverá ser utilizado em conjunto com:

* GDS-01 — GereIgreja Design System;
* GDS-03 — Paleta Oficial;
* GDS-04 — Tipografia;
* GDS-05 — Espaçamento;
* GDS-06 — Grid;
* GDS-07 — Iconografia;
* GDS-08 — Botões;
* GDS-09 — Formulários.

Também deverá permanecer compatível com:

* GEA — Arquitetura da Plataforma;
* GFE — Frontend Engineering;
* Bootstrap;
* Django Templates;
* HTMX;
* Alpine.js;
* `static/css/design_system.css`.

Toda implementação deverá utilizar os tokens oficiais do GereIgreja.

---

Vamos prosseguir com a **Parte 2 do GDS-10 — Cards**, mantendo o conteúdo inteiro em uma única caixa Markdown para você copiar diretamente.

````markdown id="58321"
# 18. Cards de Informação

Cards de informação são utilizados para apresentar informações complementares que auxiliam o usuário na compreensão de uma determinada funcionalidade.

Exemplos:

- orientações;
- informações administrativas;
- avisos contextuais;
- instruções;
- descrições;
- informações auxiliares.

Exemplo:

```text
┌────────────────────────────────────┐
│ Informação                         │
│                                    │
│ Os dados desta congregação serão   │
│ utilizados nos relatórios          │
│ administrativos.                  │
└────────────────────────────────────┘
````

Cards informativos não deverão competir visualmente com o conteúdo principal da página.

---

# 19. Cards de Status

Cards de status deverão representar claramente a situação de um registro ou processo.

Exemplos:

```text
Ativo
Inativo
Pendente
Concluído
Agendado
Cancelado
Em processamento
```

O status deverá utilizar os padrões semânticos oficiais do GDS.

Exemplo:

```text
┌─────────────────────────────┐
│ Cadastro                    │
│                             │
│ Status                      │
│ ● Ativo                     │
└─────────────────────────────┘
```

Não utilizar somente cor para comunicar o estado.

Sempre que necessário, utilizar também:

* texto;
* ícone;
* descrição;
* badge.

---

# 20. Cards com Imagem

Cards poderão utilizar imagens quando elas contribuírem para a compreensão ou identificação do conteúdo.

Exemplos:

* eventos;
* pessoas;
* congregações;
* campanhas;
* conteúdos públicos.

Estrutura:

```text
┌─────────────────────────────┐
│                             │
│          IMAGEM             │
│                             │
├─────────────────────────────┤
│ Título                      │
│ Descrição                   │
│ [Ação]                      │
└─────────────────────────────┘
```

A imagem não deverá ocupar espaço excessivo quando a informação textual for prioritária.

---

# 21. Cards Clicáveis

Um card poderá ser inteiramente clicável quando o objetivo principal for navegar para outra área.

Exemplo:

```text
┌─────────────────────────────┐
│ Secretaria                  │
│ Gerencie membros e dados    │
│ administrativos             │
└─────────────────────────────┘
```

Quando todo o card for clicável:

* a área de interação deverá ser claramente percebida;
* deverá existir estado de foco;
* deverá existir estado de hover;
* deverá funcionar por teclado;
* não deverá haver múltiplos destinos conflitantes dentro do mesmo card.

---

# 22. Cards com Múltiplas Ações

Quando houver mais de uma ação, as ações deverão ser claramente diferenciadas.

Exemplo:

```text
┌────────────────────────────────┐
│ João da Silva                  │
│                                │
│ Congregação: Plautino Soares  │
│                                │
│ [Visualizar] [Editar] [Excluir]│
└────────────────────────────────┘
```

A ação principal deverá possuir maior destaque.

A ação destrutiva deverá utilizar o padrão semântico `Danger`.

---

# 23. Cards Expansíveis

Cards poderão possuir conteúdo expansível quando houver informação secundária que não precise permanecer visível o tempo todo.

Exemplo:

```text
┌────────────────────────────────┐
│ Dados adicionais          ▼    │
├────────────────────────────────┤
│ Informações complementares     │
│                                │
│ Histórico                      │
│ Observações                    │
└────────────────────────────────┘
```

O estado deverá ser claramente comunicado.

O usuário deverá saber:

* se está aberto;
* se está fechado;
* como expandir;
* como recolher.

---

# 24. Cards em Dashboards

Dashboards do GereIgreja poderão utilizar cards para apresentar indicadores resumidos.

Uma estrutura típica poderá ser:

```text
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Membros      │ │ Visitantes   │ │ Eventos      │
│ 1.248        │ │ 86           │ │ 12           │
└──────────────┘ └──────────────┘ └──────────────┘
```

Os cards deverão permitir leitura rápida.

Evitar utilizar excesso de cards no primeiro nível do dashboard.

A quantidade deverá ser determinada pela relevância dos indicadores.

---

# 25. Grid de Cards

Cards deverão utilizar o sistema de grid oficial.

Exemplo conceitual:

```text
Desktop:

┌──────────┐ ┌──────────┐ ┌──────────┐
│ Card     │ │ Card     │ │ Card     │
└──────────┘ └──────────┘ └──────────┘

Tablet:

┌──────────┐ ┌──────────┐
│ Card     │ │ Card     │
└──────────┘ └──────────┘

Mobile:

┌─────────────────────┐
│ Card                │
└─────────────────────┘

┌─────────────────────┐
│ Card                │
└─────────────────────┘
```

A quantidade de colunas deverá adaptar-se à largura disponível.

---

# 26. Cards em Listagens

Cards podem ser utilizados em listagens quando a apresentação visual for mais importante do que a comparação tabular.

Exemplos:

* eventos;
* turmas;
* campanhas;
* congregações;
* conteúdos;
* atalhos.

Para grandes conjuntos de dados administrativos, tabelas deverão ser consideradas antes dos cards.

---

# 27. Cards versus Tabelas

Utilizar **cards** quando:

* cada registro possui informações relativamente independentes;
* a leitura individual é prioritária;
* existem poucas informações por registro;
* há necessidade de apresentação visual;
* a interface é predominantemente responsiva.

Utilizar **tabelas** quando:

* o usuário precisa comparar registros;
* existem muitas colunas;
* ordenação é importante;
* filtros são importantes;
* o usuário precisa analisar muitos registros simultaneamente.

Exemplo:

```text
Cards:
Membros apresentados individualmente.

Tabela:
Nome | Congregação | Telefone | Status | Data
```

Não utilizar cards para substituir tabelas simplesmente por preferência estética.

---

# 28. Anatomia do Card

A anatomia oficial poderá conter:

```text
Card
│
├── Header
│   ├── Ícone
│   ├── Título
│   └── Menu/Ação
│
├── Body
│   ├── Informação principal
│   ├── Informação secundária
│   └── Conteúdo
│
└── Footer
    ├── Metadados
    └── Ações
```

Os elementos são opcionais conforme o tipo de card.

---

# 29. Header

O header deverá ser utilizado quando houver necessidade de:

* título;
* identificação;
* ação contextual;
* status;
* ícone.

Exemplo:

```text
┌────────────────────────────────┐
│ 👤 Membros                ⋮    │
├────────────────────────────────┤
│ 1.248                          │
└────────────────────────────────┘
```

Evitar headers excessivamente altos.

---

# 30. Body

O body contém a informação principal do card.

Deverá possuir espaçamento adequado e hierarquia visual clara.

Evitar colocar grandes blocos de texto dentro de cards destinados à leitura rápida.

Quando houver grande quantidade de conteúdo, utilizar uma página ou componente apropriado.

---

# 31. Footer

O footer poderá conter:

* ações;
* metadados;
* data;
* status;
* links.

Exemplo:

```text
┌────────────────────────────────┐
│ Culto dos Jovens               │
│ 01/08/2026 — 18:00             │
├────────────────────────────────┤
│ Atualizado hoje       [Ver]    │
└────────────────────────────────┘
```

O footer deverá ser utilizado somente quando acrescentar valor.

---

# 32. Ícones em Cards

Ícones poderão auxiliar na identificação rápida do conteúdo.

Exemplos:

```text
Membros       → ícone de pessoas
Financeiro    → ícone financeiro
Eventos       → ícone de calendário
Comunicação   → ícone de mensagem
Escola Bíblica → ícone educacional
```

Os ícones deverão seguir o padrão de iconografia definido no GDS.

Não utilizar ícones decorativos em excesso.

---

# 33. Cores dos Cards

Os cards deverão utilizar a paleta oficial do GereIgreja.

Conforme definido no GDS-01:

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

Cards comuns deverão utilizar predominantemente:

```text
Surface
Border
Text
Text Muted
```

A cor institucional deverá ser utilizada para destacar ações ou informações relacionadas à identidade do GereIgreja.

---

# 34. Fundos Coloridos

Fundos coloridos deverão ser utilizados com moderação.

Não transformar cada card em uma cor diferente.

O uso de cores semânticas deverá possuir significado.

Exemplo:

```text
Success → situação positiva
Warning → atenção
Danger → situação crítica
```

A cor não deverá ser utilizada somente como decoração.

---

# 35. Bordas

Cards deverão utilizar o token oficial de borda.

Cor oficial:

```text
#D7E2E8
```

A espessura deverá permanecer consistente entre componentes equivalentes.

Evitar bordas excessivamente pesadas.

---

# 36. Sombras

Sombras deverão ser discretas.

O objetivo da sombra é criar hierarquia e separação entre superfícies, não produzir efeito visual exagerado.

Evitar:

```text
sombras muito fortes;
sombras coloridas;
múltiplas sombras;
efeitos 3D desnecessários.
```

---

# 37. Border Radius

O raio dos cards deverá seguir os tokens oficiais do Design System.

Não utilizar valores arbitrários em cada módulo.

Cards semelhantes deverão possuir o mesmo raio.

---

# 38. Espaçamento Interno

O conteúdo interno deverá utilizar a escala oficial de espaçamento.

Evitar:

```css
padding: 13px;
margin: 17px;
gap: 11px;
```

quando esses valores não estiverem definidos pelos tokens.

Preferir tokens oficiais.

---

# 39. Densidade

A densidade deverá ser definida de acordo com a finalidade.

### Card de indicador

Alta objetividade.

### Card de registro

Densidade moderada.

### Card informativo

Densidade menor.

### Card financeiro

Priorizar leitura do valor.

Cards administrativos não deverão ficar excessivamente espaçados a ponto de prejudicar a produtividade.

---

# 40. Tipografia

A tipografia deverá seguir o GDS-01.

Hierarquia recomendada:

```text
Título do card
        ↓
Valor principal
        ↓
Informação secundária
        ↓
Metadado
```

O valor principal de um indicador poderá possuir peso visual maior.

Textos auxiliares deverão utilizar `Text Muted`.

---

# 41. Estados Visuais

Todo card interativo deverá considerar os seguintes estados:

```text
Normal
Hover
Focus
Active
Disabled
Loading
Error
```

Cards puramente informativos poderão não possuir todos esses estados.

---

# 42. Estado Hover

Cards clicáveis poderão apresentar alteração visual discreta no hover.

O efeito deverá comunicar interatividade sem produzir movimento excessivo.

Exemplo conceitual:

```text
Normal
   ↓
leve mudança de superfície/borda/sombra
   ↓
Hover
```

Evitar transformações exageradas.

---

# 43. Estado Focus

Cards clicáveis deverão apresentar foco visível ao serem acessados por teclado.

O foco deverá ser compatível com o padrão global de acessibilidade do GereIgreja.

---

# 44. Estado Disabled

Quando um card estiver temporariamente indisponível, deverá comunicar claramente essa condição.

Exemplo:

```text
┌─────────────────────────────┐
│ Relatório                   │
│                             │
│ Disponível após fechamento  │
│ do período.                 │
└─────────────────────────────┘
```

Não depender apenas de redução de opacidade para comunicar indisponibilidade.

---

# 45. Estado Loading

Durante carregamentos, o card deverá apresentar estado de processamento.

Pode utilizar:

```text
Skeleton
```

ou outro indicador padronizado.

Exemplo:

```text
┌─────────────────────────────┐
│ ███████████                 │
│                             │
│ ███████████████             │
│ ███████                     │
└─────────────────────────────┘
```

O estado de loading deverá preservar aproximadamente a estrutura final do card para reduzir mudanças bruscas de layout.

---

# 46. Estado de Erro

Quando não for possível carregar o conteúdo:

```text
┌─────────────────────────────┐
│ Financeiro                  │
│                             │
│ Não foi possível carregar   │
│ os dados.                   │
│                             │
│ [Tentar novamente]          │
└─────────────────────────────┘
```

A mensagem deverá ser clara e, quando possível, oferecer uma ação de recuperação.

---

# 47. Responsividade

Cards deverão funcionar adequadamente em diferentes dispositivos.

---

## Desktop

Permitir múltiplas colunas quando houver espaço suficiente.

---

## Tablet

Reduzir a quantidade de colunas.

---

## Smartphone

Priorizar uma coluna.

Exemplo:

```text
┌─────────────────────────┐
│ Membros                 │
│ 1.248                   │
└─────────────────────────┘

┌─────────────────────────┐
│ Visitantes              │
│ 86                      │
└─────────────────────────┘
```

---

# 48. Cards em Telas Pequenas

Não reduzir o conteúdo a ponto de prejudicar sua leitura.

Evitar:

* textos cortados;
* botões impossíveis de tocar;
* ações escondidas sem indicação;
* excesso de informações horizontais.

Quando necessário, reorganizar o conteúdo verticalmente.

---

# 49. Acessibilidade

Cards deverão seguir as diretrizes de acessibilidade do GereIgreja.

---

## 49.1 Conteúdo Informativo

Cards informativos deverão possuir estrutura semântica adequada.

---

## 49.2 Cards Clicáveis

Se o card representar uma ação ou navegação, o mecanismo de interação deverá ser acessível.

Não transformar simplesmente uma `div` em elemento clicável sem considerar:

* teclado;
* foco;
* semântica;
* leitores de tela.

---

## 49.3 Cor

Não depender somente de cor para comunicar:

* sucesso;
* erro;
* status;
* disponibilidade.

---

# 50. Cards e HTMX

Cards poderão ser atualizados utilizando HTMX.

Exemplos:

* atualização de indicadores;
* alteração de status;
* atualização de listas;
* filtros;
* ações rápidas.

Quando um card for atualizado parcialmente, a interface deverá preservar contexto sempre que possível.

Exemplo conceitual:

```html
<div
    id="card-financeiro"
    hx-get="/financeiro/resumo/"
    hx-trigger="load"
    hx-swap="outerHTML">
</div>
```

O componente deverá possuir estados adequados durante o carregamento.

---

# 51. Cards e Alpine.js

Alpine.js poderá controlar comportamentos locais.

Exemplos:

* expansão;
* menus;
* filtros;
* seleção;
* exibição condicional.

Exemplo:

```html
<div x-data="{ aberto: false }">
```

Alpine.js não deverá concentrar regras de negócio.

---

# 52. Cards e Django Templates

Cards deverão ser implementados preferencialmente como componentes reutilizáveis.

Exemplo conceitual:

```text
templates/
    components/
        cards/
            indicator.html
            summary.html
            record.html
            action.html
```

A estrutura real deverá respeitar a arquitetura oficial do projeto.

Evitar duplicar HTML de cards semelhantes em múltiplos templates.

---

# 53. Cards e CSS

Os estilos deverão permanecer centralizados nos padrões do Design System.

Arquivo oficial indicado no GDS-01:

```text
static/css/design_system.css
```

Evitar:

```html
style="..."
```

quando o estilo puder ser representado por uma classe ou token oficial.

---

# 54. Cards e Tokens

Os cards deverão utilizar tokens para:

* cores;
* espaçamento;
* tipografia;
* bordas;
* radius;
* sombras;
* estados.

Não utilizar valores hardcoded quando existir token oficial equivalente.

---

# 55. Cards no Dashboard Principal

O dashboard principal deverá utilizar cards para indicadores de maior relevância.

Exemplos:

```text
Membros
Congregações
Visitantes
Receitas
Despesas
Eventos
Alunos
```

A seleção final dos indicadores deverá considerar a relevância para a gestão da igreja.

Não utilizar cards apenas para preencher espaço visual.

---

# 56. Cards da Secretaria

Na Secretaria, cards poderão apresentar:

* total de membros;
* membros ativos;
* visitantes;
* aniversariantes;
* novos membros;
* congregações;
* departamentos.

Exemplo:

```text
┌─────────────────────┐
│ Membros ativos      │
│                     │
│ 1.248               │
│                     │
│ [Ver membros]       │
└─────────────────────┘
```

---

# 57. Cards do Financeiro

No Financeiro, os cards poderão apresentar:

```text
Receitas
Despesas
Saldo
Contas a pagar
Contas a receber
```

Os valores deverão ser apresentados com precisão e contexto temporal.

---

# 58. Cards de Eventos

Os cards de eventos deverão priorizar:

```text
Evento
Data
Horário
Local
Status
```

Quando existir evento próximo, o sistema poderá destacá-lo de maneira contextual, sem exagero visual.

---

# 59. Cards da Escola Bíblica

Os cards poderão apresentar:

```text
Turmas
Alunos
Professores
Aulas
Frequência
```

O conteúdo deverá respeitar as permissões do usuário.

---

# 60. Cards de Comunicação

Poderão apresentar:

```text
Mensagens enviadas
Mensagens agendadas
Rascunhos
Falhas
Destinatários
```

Informações de status deverão utilizar semântica clara.

---

Claro, Pastor Julio. Vamos para a **Parte 3 do GDS-10 — Cards**. Mantendo tudo em **uma única caixa Markdown**, pronta para copiar e colar.

````markdown
# 61. Cards de Administração

Os cards utilizados em áreas administrativas deverão priorizar:

- clareza;
- identificação rápida;
- status;
- permissões;
- ações administrativas;
- informações relevantes para gestão.

Exemplo:

```text
┌────────────────────────────────┐
│ Usuários                       │
│                                │
│ 18 usuários cadastrados        │
│ 15 ativos                      │
│ 3 inativos                     │
│                                │
│ [Gerenciar usuários]           │
└────────────────────────────────┘
````

Informações administrativas deverão respeitar as permissões do usuário autenticado.

---

# 62. Cards de Congregações

Cards de congregações poderão apresentar informações resumidas sobre cada unidade.

Exemplo:

```text
┌────────────────────────────────┐
│ Congregação Plautino Soares   │
│                                │
│ Cidade: Sobrália              │
│ Membros: 248                  │
│ Status: Ativa                 │
│                                │
│ [Visualizar]                  │
└────────────────────────────────┘
```

Quando houver múltiplas congregações, os cards deverão permitir identificação rápida.

Não apresentar informações administrativas às quais o usuário não possua permissão de acesso.

---

# 63. Cards de Usuários

Cards de usuários poderão apresentar:

* nome;
* perfil;
* congregação;
* status;
* última atividade, quando aplicável;
* ações disponíveis.

Exemplo:

```text
┌────────────────────────────────┐
│ João da Silva                  │
│ Administrador                  │
│                                │
│ Congregação: Plautino Soares  │
│ Status: Ativo                  │
│                                │
│ [Editar] [Gerenciar]           │
└────────────────────────────────┘
```

Informações de autenticação e segurança nunca deverão ser exibidas diretamente no card.

---

# 64. Cards de Configuração

Cards de configuração deverão organizar funcionalidades relacionadas.

Exemplo:

```text
┌────────────────────────────────┐
│ Dados da Igreja                │
│                                │
│ Configure nome, endereço,      │
│ contatos e informações gerais. │
│                                │
│ [Configurar]                   │
└────────────────────────────────┘
```

Outro exemplo:

```text
┌────────────────────────────────┐
│ Comunicação                    │
│                                │
│ Configure e-mail, SMS e        │
│ notificações.                  │
│                                │
│ [Configurar]                   │
└────────────────────────────────┘
```

Cards de configuração deverão facilitar a descoberta das funcionalidades sem transformar a página em um conjunto excessivamente fragmentado de opções.

---

# 65. Cards de Perfil

Cards de perfil poderão apresentar informações resumidas de uma pessoa.

Exemplo:

```text
┌────────────────────────────────┐
│            [Foto]              │
│                                │
│ João da Silva                  │
│ Membro                         │
│                                │
│ Plautino Soares                │
│                                │
│ [Ver perfil]                   │
└────────────────────────────────┘
```

A imagem deverá ser opcional.

Quando não houver imagem, utilizar o mecanismo padrão de avatar definido pelo sistema.

---

# 66. Cards de Aniversariantes

Cards de aniversariantes poderão ser utilizados em dashboards ou páginas da Secretaria.

Exemplo:

```text
┌────────────────────────────────┐
│ Aniversariantes de hoje        │
│                                │
│ João da Silva                  │
│ Maria Oliveira                 │
│ Carlos Souza                   │
│                                │
│ [Ver aniversariantes]          │
└────────────────────────────────┘
```

O card deverá apresentar somente informações permitidas pelas regras de privacidade e pelo nível de acesso do usuário.

---

# 67. Cards de Visitantes

Cards relacionados a visitantes poderão apresentar:

* quantidade;
* novos visitantes;
* visitantes recentes;
* status de acompanhamento.

Exemplo:

```text
┌────────────────────────────────┐
│ Visitantes recentes            │
│                                │
│ 18                             │
│ +4 nesta semana                │
│                                │
│ [Ver visitantes]               │
└────────────────────────────────┘
```

O card não deverá apresentar dados pessoais desnecessários.

---

# 68. Cards de Departamentos

Cards poderão representar departamentos ou áreas de atuação da igreja.

Exemplo:

```text
┌────────────────────────────────┐
│ Departamento de Jovens         │
│                                │
│ 42 participantes               │
│ 3 responsáveis                │
│ Status: Ativo                  │
│                                │
│ [Ver departamento]             │
└────────────────────────────────┘
```

A estrutura deverá permanecer consistente entre departamentos semelhantes.

---

# 69. Cards de Relatórios

Cards de relatórios poderão ser utilizados para apresentar atalhos ou resumos.

Exemplo:

```text
┌────────────────────────────────┐
│ Relatório Financeiro           │
│                                │
│ Agosto de 2026                 │
│                                │
│ Receitas: R$ 25.430,00         │
│ Despesas: R$ 11.200,00         │
│                                │
│ [Abrir relatório]              │
└────────────────────────────────┘
```

Quando o objetivo principal for análise detalhada, o card deverá servir como entrada para o relatório completo.

Não tentar colocar um relatório inteiro dentro de um card.

---

# 70. Cards de Atalhos

Cards de atalhos deverão representar ações frequentes.

Exemplos:

```text
Novo membro
Novo evento
Novo lançamento
Nova turma
Nova comunicação
Novo usuário
```

Exemplo:

```text
┌────────────────────────────────┐
│ +                              │
│ Novo membro                    │
│ Cadastre uma nova pessoa.      │
└────────────────────────────────┘
```

A descrição deverá ser curta.

---

# 71. Cards de Ação Primária

Quando um card representar uma ação especialmente importante, a ação principal deverá possuir destaque.

Exemplo:

```text
┌────────────────────────────────┐
│ Fechamento mensal              │
│                                │
│ O período de agosto ainda      │
│ está aberto.                   │
│                                │
│ [Fechar período]               │
└────────────────────────────────┘
```

A ação não deverá ser escondida em menus quando for essencial para a tarefa.

---

# 72. Cards com Menu de Contexto

Quando houver diversas ações secundárias, poderá ser utilizado um menu contextual.

Exemplo:

```text
┌────────────────────────────────┐
│ Evento                     ⋮   │
│                                │
│ Culto dos Jovens               │
│ 01/08/2026 — 18:00             │
└────────────────────────────────┘
```

O menu poderá conter:

```text
Visualizar
Editar
Duplicar
Cancelar
Excluir
```

A ação `Excluir` deverá ficar visualmente separada das ações comuns quando apropriado.

---

# 73. Menu de Contexto e Acessibilidade

O botão do menu contextual deverá possuir nome acessível.

Não utilizar somente:

```html
<button>⋮</button>
```

sem uma descrição acessível.

Preferir uma implementação equivalente a:

```html
<button
    type="button"
    aria-label="Mais opções">
    ...
</button>
```

A implementação final deverá seguir os componentes oficiais do GereIgreja.

---

# 74. Cards com Links

Quando um card possuir link, o destino deverá ser previsível.

Exemplo:

```text
Card → Visualizar membro
```

Evitar cards em que diferentes áreas aparentemente levam para destinos diferentes sem indicação clara.

---

# 75. Cards Aninhados

Evitar cards dentro de cards.

Exemplo inadequado:

```text
┌─────────────────────────────────────┐
│ Card principal                      │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Card secundário                 │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

Esse padrão poderá gerar excesso de hierarquia visual e dificultar a compreensão da estrutura.

Quando necessário, utilizar:

* seções;
* divisores;
* listas;
* agrupamentos;
* componentes internos apropriados.

---

# 76. Cards Excessivamente Grandes

Cards não deverão ocupar uma área maior do que a necessária.

Evitar transformar um card em uma página inteira.

Quando houver:

* grande quantidade de texto;
* muitos campos;
* tabelas;
* múltiplas ações;
* históricos extensos;

deverá ser utilizado um componente ou página apropriada.

---

# 77. Cards Excessivamente Pequenos

Cards também não deverão ser reduzidos a ponto de comprometer:

* legibilidade;
* toque;
* identificação;
* hierarquia;
* compreensão.

O tamanho deverá ser determinado pelo conteúdo.

---

# 78. Consistência de Altura

Cards pertencentes ao mesmo grupo poderão utilizar altura consistente quando isso melhorar o alinhamento visual.

Exemplo:

```text
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Card          │ │ Card          │ │ Card          │
│               │ │               │ │               │
│ Conteúdo      │ │ Conteúdo      │ │ Conteúdo      │
│               │ │               │ │               │
└───────────────┘ └───────────────┘ └───────────────┘
```

Entretanto, não forçar alturas artificiais quando isso provocar:

* conteúdo cortado;
* grandes espaços vazios;
* perda de legibilidade.

---

# 79. Alinhamento

Cards apresentados em um mesmo grid deverão possuir alinhamento consistente.

Considerar:

* topo;
* títulos;
* valores;
* ações;
* rodapés.

Quando os cards possuírem estruturas diferentes, o alinhamento deverá preservar a hierarquia visual do conjunto.

---

# 80. Conteúdo Variável

O componente deverá suportar conteúdos de tamanhos diferentes.

Exemplo:

```text
Título curto

Título muito mais longo que precisa continuar legível
```

Não utilizar truncamento automático sem considerar o impacto na compreensão.

Quando truncar, disponibilizar mecanismo apropriado para visualizar o conteúdo completo.

---

# 81. Textos Longos

Cards destinados a informações resumidas deverão limitar a quantidade de texto.

Evitar:

```text
Lorem ipsum...
```

ou grandes parágrafos em cards operacionais.

Preferir:

```text
Título
Resumo curto
Ação
```

Quando o usuário precisar ler mais, direcioná-lo para a página detalhada.

---

# 82. Datas

Datas exibidas nos cards deverão utilizar o padrão de apresentação definido pela plataforma.

Exemplos:

```text
01/08/2026
01/08/2026 — 18:00
```

Datas relativas poderão ser utilizadas quando realmente ajudarem:

```text
Hoje
Amanhã
Ontem
```

Evitar misturar formatos sem necessidade.

---

# 83. Valores Monetários

Valores financeiros deverão seguir a representação monetária brasileira.

Exemplo:

```text
R$ 1.250,00
```

Evitar formatos inconsistentes:

```text
1250
R$1250
1.250
```

quando o contexto exigir representação monetária completa.

---

# 84. Números

Números de indicadores deverão utilizar formatação adequada ao tamanho.

Exemplo:

```text
1.248
12.450
125.000
```

Quando houver abreviação, ela deverá ser compreensível.

Exemplo:

```text
1,2 mil
```

Não utilizar abreviações ambíguas.

---

# 85. Status com Badge

Quando apropriado, o card poderá utilizar badge.

Exemplo:

```text
┌─────────────────────────────┐
│ Evento                      │
│                             │
│ Culto dos Jovens            │
│                             │
│ [Agendado]                  │
└─────────────────────────────┘
```

O badge deverá utilizar o componente oficial definido pelo Design System.

Não criar estilos independentes para cada card.

---

# 86. Cards e Breadcrumb

Cards fazem parte do conteúdo da página e não substituem o breadcrumb.

Uma página interna deverá manter:

```text
Home > Módulo > Página
```

O card poderá apresentar o conteúdo da página, mas não deverá assumir a função de localização estrutural.

---

# 87. Cards e Sidebar

Quando uma página possuir menu lateral, o padrão oficial de controle mostrar/ocultar sidebar deverá ser mantido.

Os cards deverão se adaptar à área de conteúdo disponível.

Quando a sidebar for recolhida, o grid de cards poderá utilizar o espaço adicional.

---

# 88. Cards e Permissões

A exibição de ações dentro dos cards deverá respeitar as permissões do usuário.

Exemplo:

Usuário sem permissão para excluir:

```text
[Visualizar] [Editar]
```

Usuário com permissão:

```text
[Visualizar] [Editar] [Excluir]
```

A segurança deverá ser aplicada também no backend.

Ocultar um botão não substitui a verificação de autorização no servidor.

---

# 89. Cards e Multi-Tenant

O GereIgreja é uma plataforma de gestão para igrejas e deverá respeitar o isolamento dos dados entre contextos organizacionais.

Cards não deverão exibir dados pertencentes a outra igreja, congregação ou contexto ao qual o usuário não possua acesso.

A filtragem deverá ocorrer no backend.

---

# 90. Cards e Dados Vazios

Quando um card não possuir dados, apresentar estado vazio contextual.

Exemplo:

```text
┌────────────────────────────────┐
│ Próximos eventos               │
│                                │
│ Nenhum evento agendado.        │
│                                │
│ [Criar evento]                 │
└────────────────────────────────┘
```

Evitar simplesmente apresentar:

```text
—
```

sem explicar o significado.

---

# 91. Cards e Dados Nulos

Valores ausentes deverão ser tratados de maneira consistente.

Exemplo:

```text
Telefone: Não informado
```

ou:

```text
Telefone: —
```

A escolha deverá ser consistente dentro do produto.

Não confundir:

* valor zero;
* valor vazio;
* valor não informado;
* valor não aplicável.

---

# 92. Cards e Erros de Permissão

Quando um usuário não tiver permissão para consultar determinado dado, o sistema deverá seguir a política de segurança da plataforma.

Não revelar informações sensíveis por meio de mensagens como:

```text
Você não pode visualizar os dados de João.
```

quando isso puder expor a existência de registros que o usuário não deveria conhecer.

---

# 93. Cards e Atualização de Dados

Quando um card apresentar dados dinâmicos, deverá ficar claro quando a informação foi atualizada quando isso for relevante.

Exemplo:

```text
Atualizado há 2 minutos
```

ou:

```text
Atualizado em 04/08/2026 às 09:05
```

Não apresentar informações potencialmente desatualizadas como se fossem em tempo real.

---

# 94. Cards com Atualização Automática

Cards que utilizarem atualização automática deverão evitar atualizações excessivamente frequentes.

Isso é especialmente importante para:

* indicadores financeiros;
* dashboards;
* relatórios;
* comunicação;
* contadores.

Quando a atualização ocorrer, evitar causar:

* deslocamento visual;
* perda de contexto;
* mudança inesperada de posição.

---

# 95. Skeleton dos Cards

Quando utilizado skeleton, a estrutura deverá representar aproximadamente o conteúdo final.

Exemplo:

```text
┌────────────────────────────────┐
│ █████████                     │
│                                │
│ █████████████████             │
│ █████████                     │
│                                │
│ ███████                       │
└────────────────────────────────┘
```

O skeleton deverá desaparecer assim que o conteúdo estiver disponível.

Não utilizar skeleton para operações instantâneas que não necessitam de carregamento perceptível.

---

# 96. Animações

Animações em cards deverão ser discretas.

Permitido:

* transição de hover;
* abertura suave;
* mudança de estado;
* carregamento.

Evitar:

* movimentos constantes;
* saltos;
* efeitos exagerados;
* animações que dificultem leitura.

A preferência de redução de movimento do usuário deverá ser respeitada quando aplicável.

---

# 97. Performance

A utilização de cards deverá considerar performance.

Evitar renderizar simultaneamente centenas ou milhares de cards quando uma tabela, paginação ou carregamento incremental for mais adequado.

Em listagens extensas, considerar:

* paginação;
* filtros;
* busca;
* carregamento progressivo;
* atualização parcial.

---

# 98. Cards em Mobile

Em dispositivos móveis:

* priorizar uma coluna;
* aumentar a área de toque;
* reorganizar ações;
* evitar excesso de texto horizontal;
* evitar menus inacessíveis;
* preservar a ordem de leitura.

Exemplo:

```text
Desktop:

[Card] [Card] [Card]

Mobile:

[Card]

[Card]

[Card]
```

---

# 99. Ações em Mobile

Quando houver muitas ações, não obrigar o usuário a utilizar uma linha horizontal que ultrapasse a largura da tela.

Preferir:

```text
[Visualizar]

[Editar]

Mais opções
```

ou:

```text
[Visualizar] [⋮]
```

conforme o contexto.

---

# 100. Regra de Ouro

Todo card do GereIgreja deverá responder claramente a três perguntas:

```text
O que é?

Qual informação é importante?

O que o usuário pode fazer?
```

Quando um card não responder a nenhuma dessas perguntas, seu uso deverá ser reconsiderado.

---


Sim, Pastor Julio. Vamos concluir o **GDS-10 — Cards** com a **Parte 4**, mantendo **todo o conteúdo dentro de uma única caixa Markdown**, como você pediu.

````markdown
# 101. Anti-Patterns

Os seguintes padrões são considerados inadequados para o GereIgreja e deverão ser evitados.

---

## 101.1 Card sem Propósito

Não criar cards apenas para preencher visualmente uma página.

Inadequado:

```text
┌─────────────────────┐
│ Informações         │
│                     │
│ Texto sem finalidade│
└─────────────────────┘
````

Todo card deverá possuir função definida.

---

## 101.2 Excesso de Cards

Evitar transformar uma página inteira em uma sequência interminável de cards.

Inadequado:

```text
Card
Card
Card
Card
Card
Card
Card
Card
Card
Card
```

Quando a quantidade de informações for grande, utilizar:

* tabelas;
* seções;
* filtros;
* paginação;
* agrupamentos;
* abas.

---

## 101.3 Card Dentro de Card

Evitar aninhamento excessivo de superfícies.

```text
Card
 └── Card
      └── Card
           └── Card
```

Esse padrão reduz a clareza da hierarquia visual.

---

## 101.4 Cores Excessivas

Não utilizar uma cor diferente para cada card.

Inadequado:

```text
Card azul
Card verde
Card amarelo
Card vermelho
Card roxo
Card laranja
```

As cores deverão possuir significado funcional.

---

## 101.5 Sombras Excessivas

Evitar sombras fortes que façam os cards parecerem elementos flutuantes sem necessidade.

---

## 101.6 Texto Excessivo

Não utilizar cards para apresentar grandes textos.

Quando o conteúdo exigir leitura prolongada, utilizar:

* página;
* seção;
* artigo;
* modal apropriado;
* componente de conteúdo.

---

## 101.7 Ícones Decorativos em Excesso

Ícones deverão auxiliar a compreensão.

Não utilizar ícones simplesmente para ocupar espaço.

---

## 101.8 Cards Interativos sem Indicação

Um card clicável deverá parecer clicável.

Não criar um card interativo que visualmente pareça somente informativo.

---

## 101.9 Card Inteiro Clicável com Ações Conflitantes

Evitar:

```text
Card inteiro → Visualizar

Dentro do card:
[Editar]
[Excluir]
```

sem definir corretamente a propagação e a semântica das interações.

Quando houver múltiplas ações, a estrutura deverá deixar claro o comportamento de cada área.

---

## 101.10 Informações Importantes Escondidas

Não colocar informações essenciais somente em:

* tooltip;
* menu;
* hover;
* ação secundária.

Informações essenciais deverão estar disponíveis de forma evidente.

---

# 102. Regras de Implementação

Os cards deverão ser implementados como componentes reutilizáveis.

A implementação deverá evitar duplicação de HTML e CSS.

---

## 102.1 Componente Base

Quando apropriado, deverá existir um componente base capaz de fornecer:

```text
Card
├── Header
├── Body
└── Footer
```

Tipos específicos poderão utilizar essa estrutura.

---

## 102.2 Variantes

Variantes deverão ser utilizadas somente quando houver necessidade real.

Exemplo conceitual:

```text
Card
├── default
├── indicator
├── summary
├── record
├── action
└── status
```

Não criar uma variante para pequenas diferenças visuais que possam ser resolvidas pelos tokens ou composição.

---

## 102.3 Composição

Preferir composição a duplicação.

Exemplo:

```text
Card
 ├── CardHeader
 ├── CardTitle
 ├── CardBody
 ├── CardMeta
 └── CardActions
```

A estrutura final deverá respeitar a arquitetura efetiva do projeto.

---

# 103. API Conceitual

Quando componentes forem implementados como componentes reutilizáveis, seus parâmetros deverão ser previsíveis.

Exemplo conceitual:

```text
Card
    title
    description
    icon
    status
    actions
    footer
    variant
```

Não criar parâmetros específicos para cada página quando uma composição mais genérica atender ao requisito.

---

# 104. Dados e Apresentação

O card deverá separar dados de apresentação sempre que possível.

O template não deverá concentrar regras complexas de negócio.

Exemplo inadequado:

```text
if usuário
    and usuário.congregação
    and usuário.status
    and data
    and permissão
    ...
```

Regras complexas deverão permanecer nas camadas apropriadas da aplicação.

O template deverá priorizar apresentação.

---

# 105. Reutilização entre Módulos

Cards equivalentes deverão ser reutilizados entre módulos.

Exemplo:

Um card de indicador poderá ser utilizado em:

* Secretaria;
* Financeiro;
* Escola Bíblica;
* Eventos.

Não criar uma implementação visual diferente para cada módulo quando o comportamento for o mesmo.

---

# 106. Personalização por Módulo

A personalização deverá ocorrer principalmente por:

* conteúdo;
* ícone;
* dados;
* variante;
* contexto.

Não deverá ocorrer por cópia completa do componente.

---

# 107. Cards e Bootstrap

Quando Bootstrap estiver presente na arquitetura do frontend, seus recursos poderão ser utilizados como base.

Entretanto, componentes deverão respeitar o GDS do GereIgreja.

Não utilizar classes Bootstrap de forma indiscriminada se isso resultar em:

* cores fora da paleta;
* espaçamentos inconsistentes;
* componentes visualmente incompatíveis;
* estilos duplicados.

O GDS possui precedência sobre estilos genéricos quando houver conflito.

---

# 108. Cards e CSS Customizado

CSS customizado poderá ser criado quando necessário.

Entretanto:

```text
Novo CSS
     ↓
verificar se já existe token
     ↓
verificar se já existe componente
     ↓
verificar se existe variante
     ↓
somente então criar nova regra
```

O objetivo é evitar crescimento descontrolado do CSS.

---

# 109. Tokens Oficiais

Os cards deverão utilizar tokens oficiais.

Exemplo conceitual:

```css
.card {
    background: var(--color-surface);
    border-color: var(--color-border);
    color: var(--color-text);
}
```

Os nomes exatos dos tokens deverão corresponder à implementação efetiva do `design_system.css`.

Não inventar novos nomes de tokens diretamente nos templates.

---

# 110. Documentação do Componente

Todo novo tipo de card deverá ser documentado.

A documentação deverá informar:

* nome;
* objetivo;
* estrutura;
* variantes;
* estados;
* comportamento;
* acessibilidade;
* exemplos;
* restrições;
* casos de uso.

---

# 111. Testes Visuais

Cards reutilizáveis deverão ser verificados em diferentes contextos.

Testar:

* conteúdo curto;
* conteúdo longo;
* ausência de dados;
* loading;
* erro;
* ações;
* mobile;
* tablet;
* desktop.

---

# 112. Testes de Acessibilidade

Verificar:

* navegação por teclado;
* foco;
* leitura por tecnologia assistiva;
* contraste;
* tamanho das áreas interativas;
* identificação das ações;
* ausência de dependência exclusiva de cor.

---

# 113. Testes de Responsividade

Cada componente deverá ser verificado pelo menos nos seguintes contextos:

```text
Desktop
Notebook
Tablet
Smartphone
```

O componente não deverá depender de uma largura específica.

---

# 114. Testes de Conteúdo

Os testes deverão utilizar conteúdo realista.

Não testar somente:

```text
Título
Texto
123
```

Testar também:

```text
Congregação Plautino Soares
Culto dos Jovens e Adolescentes
R$ 25.430,00
1.248 membros
```

Isso ajuda a identificar problemas de largura, quebra de linha e hierarquia.

---

# 115. Observabilidade

Quando cards apresentarem informações carregadas dinamicamente, erros de carregamento deverão ser identificáveis no fluxo técnico da aplicação.

A interface deverá apresentar uma mensagem adequada ao usuário sem expor detalhes internos do sistema.

Não apresentar:

```text
IntegrityError at /financeiro/
```

ao usuário final.

---

# 116. Tratamento de Erros

Quando uma atualização via HTMX falhar, o card deverá possuir uma estratégia de recuperação adequada.

Exemplo:

```text
Não foi possível atualizar os dados.

[Tentar novamente]
```

A solução técnica poderá utilizar mecanismos globais ou específicos conforme a arquitetura da aplicação.

---

# 117. Performance de Imagens

Cards com imagens deverão considerar:

* tamanho adequado;
* compressão;
* dimensões;
* carregamento eficiente;
* `alt` quando necessário;
* lazy loading quando apropriado.

Não utilizar imagens enormes em cards pequenos.

---

# 118. Imagens Decorativas

Quando uma imagem for puramente decorativa, sua implementação deverá respeitar as práticas de acessibilidade.

Não adicionar descrições redundantes a imagens que não acrescentam informação.

---

# 119. Segurança Visual

Nunca exibir diretamente em cards:

* senhas;
* tokens;
* chaves privadas;
* credenciais;
* informações sensíveis desnecessárias.

Dados financeiros e pessoais deverão respeitar as permissões e regras de privacidade.

---

# 120. Dados Financeiros Sensíveis

Quando informações financeiras forem apresentadas em cards, considerar o nível de acesso.

Exemplo:

```text
Receitas
R$ 25.430,00
```

Somente usuários autorizados deverão acessar informações financeiras protegidas.

---

# 121. Cards e Auditoria

Quando o contexto exigir rastreabilidade, o card poderá apresentar informações como:

```text
Atualizado por: João Silva
Atualizado em: 04/08/2026 às 09:05
```

Essas informações deverão ser apresentadas somente quando agregarem valor ao fluxo.

---

# 122. Cards de Registros Excluídos

Registros logicamente excluídos, quando visíveis para usuários autorizados, deverão possuir indicação clara.

Exemplo:

```text
Status: Excluído
```

Não apresentar um registro excluído como se estivesse ativo.

---

# 123. Cards e Estados Semânticos

Os estados deverão seguir a semântica oficial.

Exemplo:

```text
Success
Warning
Danger
```

Não utilizar:

```text
verde = qualquer coisa positiva
amarelo = qualquer coisa diferente
vermelho = qualquer destaque
```

A cor deverá possuir significado previsível.

---

# 124. Cards e Tradução

Caso o sistema venha a suportar internacionalização, textos dos cards deverão estar preparados para tradução.

Não construir layouts que dependam de uma frase possuir determinado tamanho.

Exemplo inadequado:

```text
width: 100px;
```

para acomodar somente uma frase específica.

---

# 125. Cards e Conteúdo Dinâmico

Cards deverão suportar variação de:

* quantidade;
* tamanho;
* status;
* datas;
* nomes;
* valores;
* descrições.

O layout deverá permanecer estável diante de alterações normais dos dados.

---

# 126. Cards e Estados de Permissão

Um card poderá apresentar diferentes níveis de interação conforme a permissão.

Exemplo:

```text
Visualização:

[Visualizar]

Edição:

[Visualizar] [Editar]

Administração:

[Visualizar] [Editar] [Excluir]
```

A autorização deverá ser validada no backend.

---

# 127. Cards e Mobile First

Quando possível, o componente deverá ser projetado considerando primeiro a experiência em telas pequenas.

A partir dela, o layout poderá expandir para:

* tablet;
* notebook;
* desktop.

Isso reduz problemas de adaptação posteriores.

---

# 128. Cards e Touch

Elementos interativos deverão possuir área de toque adequada.

Evitar:

```text
⋮
```

como uma área extremamente pequena e difícil de tocar.

O botão deverá possuir área suficiente para interação confortável.

---

# 129. Cards e Contraste

O contraste deverá ser suficiente entre:

* texto e fundo;
* ícones e fundo;
* estados;
* badges;
* bordas quando relevantes.

O uso das cores oficiais não elimina a necessidade de verificar contraste.

---

# 130. Cards e Movimento Reduzido

Animações deverão respeitar preferências de redução de movimento quando aplicável.

O componente não deverá depender de animação para comunicar informação essencial.

---

# 131. Cards e Navegação

Quando um card representar navegação, o destino deverá ser coerente com o título e a descrição.

Exemplo:

```text
Membros
Gerencie os membros da igreja.

→ /secretaria/membros/
```

O texto deverá permitir ao usuário prever o resultado da ação.

---

# 132. Cards e SEO

Cards presentes em áreas administrativas autenticadas não possuem como objetivo principal SEO.

No Portal Público, entretanto, cards poderão contribuir para:

* organização do conteúdo;
* navegação;
* descoberta;
* estrutura semântica.

A semântica HTML deverá ser escolhida conforme o conteúdo.

---

# 133. Cards no Portal Público

Cards públicos poderão ser utilizados para:

* eventos;
* cultos;
* notícias;
* departamentos;
* informações da igreja;
* campanhas;
* conteúdos.

O visual deverá permanecer coerente com a identidade do GereIgreja quando o componente fizer parte da plataforma.

---

# 134. Cards e Eventos Públicos

Exemplo:

```text
┌────────────────────────────────┐
│        [Imagem do evento]      │
├────────────────────────────────┤
│ Festividade 2026               │
│                                │
│ 31/07 a 02/08/2026             │
│                                │
│ [Ver programação]              │
└────────────────────────────────┘
```

Cards públicos poderão possuir tratamento visual mais editorial, desde que permaneçam compatíveis com o GDS.

---

# 135. Cards de Destaque

Um card poderá ser utilizado para destacar uma informação importante.

Entretanto, destaque não deverá significar excesso de:

* cor;
* sombra;
* tamanho;
* animação.

A hierarquia deverá permanecer equilibrada.

---

# 136. Cards e Modais

Cards poderão aparecer dentro de modais quando necessário.

Entretanto, evitar:

```text
Modal
  └── Card
      └── Card
          └── Formulário
```

quando uma estrutura simples resolver o problema.

O componente deverá ser escolhido conforme a finalidade.

---

# 137. Cards e Drawers

Cards poderão ser apresentados em drawers quando fizer sentido para visualização contextual.

O drawer deverá manter sua própria hierarquia.

Não utilizar cards simplesmente porque existe espaço disponível.

---

# 138. Cards e Paginação

Quando uma listagem utilizar cards, grandes quantidades de registros deverão possuir paginação ou outro mecanismo de controle.

Exemplo:

```text
[Card] [Card] [Card]

[Card] [Card] [Card]

← Anterior    1  2  3    Próxima →
```

A solução final deverá seguir o padrão de paginação do GereIgreja.

---

# 139. Cards e Filtros

Quando cards forem utilizados em listagens filtráveis, os filtros deverão permanecer separados da área de conteúdo.

Exemplo:

```text
Filtros
[Congregação ▼] [Status ▼] [Pesquisar]

Resultados

[Card] [Card] [Card]
```

Evitar colocar filtros complexos dentro de cada card.

---

# 140. Cards e Ordenação

Quando a ordem dos cards tiver significado, a interface deverá comunicar o critério.

Exemplo:

```text
Ordenar por:
[Mais recentes ▼]
```

Não alterar a ordem silenciosamente sem contexto.

---

# 141. Cards e Busca

Quando houver grande quantidade de cards, disponibilizar busca quando necessário.

A busca deverá:

* possuir campo identificado;
* informar o que está sendo pesquisado;
* preservar filtros quando apropriado;
* apresentar estado vazio quando nenhum resultado for encontrado.

---

# 142. Estado de Nenhum Resultado

Exemplo:

```text
Nenhum membro encontrado.

Tente alterar os filtros ou os termos da pesquisa.
```

Quando possível:

```text
[Limpar filtros]
```

---

# 143. Estado de Primeiro Uso

Quando o módulo ainda não possuir registros, apresentar orientação contextual.

Exemplo:

```text
┌────────────────────────────────┐
│ Nenhum evento cadastrado       │
│                                │
│ Crie seu primeiro evento para  │
│ começar a organizar a agenda.  │
│                                │
│ [+ Criar evento]               │
└────────────────────────────────┘
```

Esse estado é especialmente importante para novos usuários.

---

# 144. Cards e Onboarding

Cards poderão ser utilizados em fluxos iniciais para apresentar funcionalidades.

Exemplo:

```text
Cadastre seus membros
Organize suas congregações
Configure seu financeiro
Crie seus primeiros eventos
```

O onboarding deverá permanecer objetivo e não transformar o dashboard em um tutorial permanente.

---

# 145. Cards e Ajuda Contextual

Quando houver funcionalidade complexa, um card informativo poderá orientar o usuário.

Exemplo:

```text
┌────────────────────────────────┐
│ Como funciona?                │
│                                │
│ Os lançamentos financeiros     │
│ serão considerados no relatório │
│ após serem confirmados.        │
└────────────────────────────────┘
```

A ajuda deverá ser curta e contextual.

---

# 146. Cards e Confirmação

Cards não deverão substituir modais de confirmação para operações críticas.

Exemplo:

```text
Card:
[Excluir]

↓

Modal:

Deseja realmente excluir este registro?

[Cancelar] [Excluir]
```

---

# 147. Cards e Ações Destrutivas

Ações como:

* excluir;
* cancelar;
* estornar;
* remover;

deverão utilizar a semântica `Danger`.

Não utilizar vermelho para ações normais.

---

# 148. Cards e Estado de Processamento

Quando uma ação do card estiver sendo processada:

```text
[Salvando...]
```

ou:

```text
[Processando...]
```

O usuário deverá perceber que a operação está em andamento.

Evitar permitir múltiplos cliques que gerem operações duplicadas.

---

# 149. Cards e Feedback Pós-Ação

Após uma ação:

```text
Card
 ↓
Ação executada
 ↓
Atualização do conteúdo
 ↓
Feedback
```

Exemplo:

```text
Membro atualizado com sucesso.
```

Quando possível, atualizar somente a área necessária utilizando HTMX.

---

# 150. Regra Final de Design

O card não deverá ser tratado como um simples retângulo visual.

No GereIgreja, ele é um componente de organização da informação.

Seu uso deverá sempre considerar:

```text
Conteúdo
+
Hierarquia
+
Contexto
+
Interação
+
Acessibilidade
+
Responsividade
+
Consistência
```

---

# 151. Especificações Oficiais

## GDS-CARD-001

Todo card deverá possuir finalidade definida.

## GDS-CARD-002

Cards deverão utilizar tokens oficiais do GDS.

## GDS-CARD-003

Cards equivalentes deverão possuir estrutura visual consistente.

## GDS-CARD-004

Cards não deverão ser utilizados como substitutos universais de tabelas.

## GDS-CARD-005

Cards interativos deverão possuir estado de foco visível.

## GDS-CARD-006

Cards interativos deverão ser acessíveis por teclado.

## GDS-CARD-007

Cards deverão ser responsivos.

## GDS-CARD-008

Cards não deverão depender exclusivamente de cor para comunicar estados.

## GDS-CARD-009

Cards deverão respeitar as permissões do usuário.

## GDS-CARD-010

A segurança das operações deverá ser aplicada no backend.

## GDS-CARD-011

Cards deverão utilizar os padrões de espaçamento oficiais.

## GDS-CARD-012

Cards deverão utilizar a paleta oficial.

## GDS-CARD-013

Cards deverão evitar conteúdo excessivo.

## GDS-CARD-014

Cards deverão evitar aninhamento desnecessário.

## GDS-CARD-015

Cards deverão possuir tratamento para estados vazios quando aplicável.

## GDS-CARD-016

Cards dinâmicos deverão possuir estados de loading e erro quando necessário.

## GDS-CARD-017

Cards deverão evitar duplicação de componentes.

## GDS-CARD-018

Novos tipos de cards deverão ser documentados.

## GDS-CARD-019

Cards deverão permanecer compatíveis com a arquitetura frontend oficial.

## GDS-CARD-020

Cards deverão preservar a identidade visual do GereIgreja.

---

# 152. Checklist de Implementação

Antes de publicar um card, verificar:

## Estrutura

* [ ] possui finalidade clara;
* [ ] possui título quando necessário;
* [ ] possui conteúdo principal definido;
* [ ] possui ações claramente identificadas;
* [ ] não possui elementos desnecessários.

## Design

* [ ] utiliza paleta oficial;
* [ ] utiliza tokens;
* [ ] utiliza espaçamento oficial;
* [ ] utiliza tipografia oficial;
* [ ] utiliza bordas oficiais;
* [ ] utiliza radius oficial;
* [ ] utiliza sombras de forma adequada.

## Interação

* [ ] estado normal;
* [ ] hover quando aplicável;
* [ ] focus;
* [ ] active;
* [ ] disabled quando aplicável;
* [ ] loading quando aplicável;
* [ ] erro quando aplicável.

## Acessibilidade

* [ ] foco visível;
* [ ] navegação por teclado;
* [ ] contraste adequado;
* [ ] ações identificadas;
* [ ] não depende somente de cor;
* [ ] imagens possuem tratamento adequado.

## Responsividade

* [ ] desktop;
* [ ] notebook;
* [ ] tablet;
* [ ] smartphone;
* [ ] ações adaptadas;
* [ ] conteúdo não é cortado.

## Dados

* [ ] estado vazio;
* [ ] estado de erro;
* [ ] estado de loading;
* [ ] dados nulos;
* [ ] conteúdo longo;
* [ ] valores monetários;
* [ ] datas.

## Segurança

* [ ] permissões respeitadas;
* [ ] dados sensíveis protegidos;
* [ ] backend valida operações;
* [ ] usuário não recebe informações indevidas.

## Engenharia

* [ ] componente reutilizável;
* [ ] sem duplicação;
* [ ] CSS centralizado;
* [ ] `design_system.css` utilizado;
* [ ] HTMX utilizado quando apropriado;
* [ ] Alpine.js utilizado somente quando necessário;
* [ ] regras de negócio fora do template.

---

# 153. Documentos Relacionados

## Design System

```text
01-GereIgreja-Design-System.md
02-...
03-...
04-...
05-...
06-...
07-...
08-Botoes.md
09-Formularios.md
10-Cards.md
```

## Arquitetura

```text
GEA-02 — Arquitetura da Plataforma
GEA-04 — Arquitetura do Frontend
```

## Frontend

```text
GFE — GereIgreja Frontend Engineering
```

## Qualidade

```text
GQF — Framework de Qualidade
```

---

# 154. Governança

O padrão de cards deverá ser mantido pela Equipe de Engenharia.

Alterações estruturais deverão ser documentadas.

Nenhum módulo deverá criar uma versão paralela de um card existente sem justificativa técnica ou de experiência do usuário.

---

## 154.1 Novos Cards

Para propor um novo tipo de card, documentar:

```text
Nome
Objetivo
Problema resolvido
Casos de uso
Estrutura
Estados
Responsividade
Acessibilidade
Dependências
Exemplos
```

---

## 154.2 Alterações

Alterações em componentes compartilhados deverão considerar o impacto em todos os módulos que utilizam o componente.

---

## 154.3 Compatibilidade

Antes de alterar um card global, verificar:

* Secretaria;
* Financeiro;
* Eventos;
* Escola Bíblica;
* Comunicação;
* Administração;
* Portal Público.

---

# 155. Roadmap

## Fase 1 — Consolidação

* identificar cards existentes;
* eliminar duplicações;
* mapear variantes;
* padronizar tokens;
* padronizar estados.

---

## Fase 2 — Componentização

Criar componentes reutilizáveis para:

* card base;
* card de indicador;
* card de resumo;
* card de registro;
* card de ação;
* card de status;
* card financeiro;
* card de evento.

---

## Fase 3 — Integração

Integrar os cards com:

* Django Templates;
* Django Forms quando necessário;
* HTMX;
* Alpine.js;
* Bootstrap;
* Design Tokens;
* `static/css/design_system.css`.

---

## Fase 4 — Documentação

Criar catálogo interno dos componentes.

Cada componente deverá possuir:

* exemplo;
* variantes;
* estados;
* comportamento;
* acessibilidade;
* restrições.

---

## Fase 5 — Evolução

Criar uma biblioteca interna de componentes reutilizáveis para toda a plataforma.

---

# 156. Princípios Finais

Os cards do GereIgreja deverão:

* organizar;
* resumir;
* orientar;
* facilitar decisões;
* apresentar ações;
* reduzir complexidade.

Eles não deverão:

* substituir indiscriminadamente tabelas;
* criar excesso de caixas;
* utilizar cores sem significado;
* esconder informações importantes;
* dificultar a navegação;
* comprometer acessibilidade;
* duplicar componentes existentes.

A utilização correta de cards deverá tornar a interface mais clara sem torná-la visualmente pesada.

O objetivo final é permitir que o usuário compreenda rapidamente as informações da gestão da igreja e execute as ações necessárias com segurança e eficiência.

---

# Status do Documento

Pasta:

```text
docs/design-system/
```

Arquivo:

```text
10-Cards.md
```

Documento:

```text
GDS-10
```

Código:

```text
GDS-CARDS
```

Framework:

```text
GereIgreja Design System (GDS)
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

# Fim do Documento

GDS-10 — Cards
GereIgreja Design System

```
```
