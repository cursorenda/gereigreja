Pasta:
docs/design-system/

Arquivo:
05-Espacamento.md

Documento:
GDS-05

Código:
GDS-SPACING

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

# GDS-05 — Espaçamento

> *"O espaçamento organiza a interface, estabelece hierarquia visual e melhora significativamente a experiência do usuário. No GereIgreja, o espaço em branco é tratado como um componente de design, e não como ausência de conteúdo."*

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia do Espaçamento
4. Princípios
5. Design Tokens
6. Escala Oficial
7. Margens
8. Padding
9. Gaps
10. Ritmo Vertical
11. Ritmo Horizontal
12. Casos Reais do GereIgreja
13. Relação com os Demais Frameworks

---

# 1. Objetivo

Este documento define oficialmente a arquitetura de espaçamento utilizada em toda a plataforma GereIgreja.

Seu objetivo é garantir:

- consistência visual;
- alinhamento uniforme;
- facilidade de leitura;
- organização da interface;
- reutilização de padrões;
- manutenção simplificada.

Todos os módulos deverão utilizar exclusivamente os padrões definidos neste documento.

---

# 2. Escopo

As diretrizes aqui estabelecidas aplicam-se a:

- Área de Gestão;
- Portal Público;
- Landing Pages;
- Dashboards;
- Formulários;
- Tabelas;
- Cards;
- Modais;
- Alertas;
- Menus;
- Componentes reutilizáveis.

---

# 3. Filosofia do Espaçamento

O espaço em branco possui função estrutural.

Sua finalidade é:

- separar grupos de informação;
- facilitar leitura;
- reduzir carga cognitiva;
- melhorar organização visual;
- destacar elementos importantes.

Interfaces excessivamente compactas dificultam a utilização.

Interfaces excessivamente espaçadas reduzem produtividade.

O equilíbrio deverá orientar toda implementação.

---

# 4. Princípios

Toda decisão relacionada ao espaçamento deverá respeitar:

- consistência;
- previsibilidade;
- simplicidade;
- alinhamento;
- proporcionalidade;
- reutilização.

Valores arbitrários não deverão ser utilizados.

---

# 5. Design Tokens

Todo espaçamento deverá utilizar Design Tokens oficiais.

Exemplo conceitual:

Spacing

↓

Layout

↓

Component

↓

Página

↓

Interface

Essa arquitetura elimina inconsistências entre módulos.

---

# 6. Escala Oficial

Escala oficial do GereIgreja.

| Token | Valor |
|--------|------:|
| Space-0 | 0 px |
| Space-1 | 4 px |
| Space-2 | 8 px |
| Space-3 | 12 px |
| Space-4 | 16 px |
| Space-5 | 20 px |
| Space-6 | 24 px |
| Space-8 | 32 px |
| Space-10 | 40 px |
| Space-12 | 48 px |
| Space-16 | 64 px |
| Space-20 | 80 px |

Toda interface deverá utilizar exclusivamente essa escala.

---

# 7. Margens

As margens definem o espaçamento externo dos elementos.

Devem ser utilizadas para:

- separar seções;
- organizar blocos;
- estruturar páginas;
- evitar agrupamentos excessivos.

Não utilizar margens arbitrárias.

---

## Margens Recomendadas

Entre seções:

```
Space-10
```

Entre componentes principais:

```
Space-8
```

Entre elementos relacionados:

```
Space-4
```

---

# 8. Padding

O padding define o espaçamento interno dos componentes.

Todos os componentes reutilizáveis deverão possuir padding consistente.

---

## Cards

Padding recomendado:

```
Space-6
```

---

## Modais

Padding recomendado:

```
Space-8
```

---

## Inputs

Padding interno:

```
Space-3
```

---

## Botões

Padding vertical:

```
Space-2
```

Padding horizontal:

```
Space-4
```

---

# 9. Gaps

Os gaps organizam elementos distribuídos em:

- Flexbox;
- CSS Grid;
- listas;
- grupos de botões.

Evitar utilização de margens para resolver problemas de layout quando o gap for suficiente.

---

Escalas recomendadas:

Pequeno

```
Space-2
```

---

Médio

```
Space-4
```

---

Grande

```
Space-6
```

---

# 10. Ritmo Vertical

Toda página deverá manter ritmo vertical consistente.

Ordem recomendada:

Título

↓

Descrição

↓

Filtros

↓

Conteúdo

↓

Ações

↓

Rodapé

O usuário deverá identificar naturalmente a organização da página.

---

# 11. Ritmo Horizontal

A distribuição horizontal deverá favorecer leitura.

Princípios:

- alinhamento consistente;
- colunas proporcionais;
- distância uniforme entre campos;
- agrupamentos lógicos.

Evitar desalinhamentos visuais.

---

# 12. Casos Reais do GereIgreja

## Dashboard

Os cards de indicadores deverão utilizar Space-6 internamente e Space-8 entre si.

---

## Cadastro de Membros

Campos relacionados deverão permanecer agrupados utilizando Space-4.

Grupos distintos deverão utilizar Space-8.

---

## Financeiro

Filtros deverão permanecer próximos da tabela.

Separação recomendada:

```
Space-6
```

---

## Escola Bíblica

Cards das turmas deverão utilizar o mesmo padding dos demais módulos.

---

## Comunicação

Listas de campanhas deverão utilizar ritmo vertical consistente.

---

# 13. Relação com os Demais Frameworks

Este documento complementa:

GDS-03 — Cores

GDS-04 — Tipografia

GFE — Frontend Engineering

Os documentos seguintes utilizarão esta escala como padrão oficial para todos os componentes reutilizáveis.

---

# 14. Espaçamento em Formulários

Os formulários do GereIgreja são utilizados diariamente por secretários, tesoureiros, pastores e administradores.

O espaçamento deverá facilitar o preenchimento e reduzir erros de operação.

---

## Estrutura Vertical

Ordem recomendada:

Label

↓

Campo

↓

Mensagem de ajuda

↓

Próximo campo

---

Espaçamento recomendado:

Label → Campo

```
Space-2
```

Campo → Mensagem

```
Space-1
```

Mensagem → Próximo Campo

```
Space-4
```

---

## Agrupamento de Campos

Campos relacionados deverão permanecer próximos.

Exemplos:

Dados Pessoais

- Nome
- Sexo
- Data de Nascimento

Dados de Contato

- Telefone
- Celular
- E-mail

Dados Ministeriais

- Congregação
- Cargo
- Departamento

Cada grupo deverá utilizar:

```
Space-8
```

---

# 15. Espaçamento em Tabelas

As tabelas representam um dos componentes mais utilizados da plataforma.

A organização visual deverá facilitar leitura rápida.

---

## Cabeçalho

Padding:

```
Space-4
```

---

## Linhas

Padding vertical:

```
Space-3
```

Padding horizontal:

```
Space-4
```

---

## Ações

Botões de ação deverão utilizar:

```
Gap Space-2
```

---

## Paginação

Separação da tabela:

```
Space-6
```

---

# 16. Espaçamento em Dashboards

Os dashboards concentram informações estratégicas.

O espaçamento deverá facilitar identificação dos indicadores.

---

## Cards

Padding interno:

```
Space-6
```

Distância entre cards:

```
Space-6
```

---

## Gráficos

Separação entre gráfico e título:

```
Space-4
```

Separação entre gráfico e legenda:

```
Space-4
```

---

## KPIs

Valor

↓

Descrição

↓

Indicador

Utilizar ritmo vertical consistente.

---

# 17. Containers

Toda página deverá utilizar containers padronizados.

Estrutura recomendada:

Página

↓

Container

↓

Seções

↓

Cards

↓

Componentes

↓

Conteúdo

Cada camada deverá respeitar a escala oficial.

---

# 18. Grid

O GereIgreja utiliza Bootstrap como base estrutural.

Todo grid deverá respeitar:

- alinhamento;
- gutters consistentes;
- distribuição proporcional;
- comportamento responsivo.

Nunca misturar grids diferentes na mesma página.

---

## Gutter Oficial

Desktop

```
24 px
```

Tablet

```
20 px
```

Smartphone

```
16 px
```

---

# 19. Responsividade

O espaçamento deverá adaptar-se automaticamente.

Desktop

Maior conforto visual.

Notebook

Pequenas reduções.

Tablet

Compactação moderada.

Smartphone

Redução dos espaçamentos externos, preservando legibilidade.

A prioridade será manter produtividade.

---

# 20. Evidências Arquiteturais

As diretrizes deste documento refletem a implementação oficial do GereIgreja.

---

## EA-GDS-026

Bootstrap fornece parte da estrutura de grid utilizada.

---

## EA-GDS-027

O Design System padroniza todos os espaçamentos adicionais.

---

## EA-GDS-028

Os componentes reutilizam uma escala única de spacing.

---

## EA-GDS-029

Os layouts oficiais preservam ritmo visual consistente.

---

## EA-GDS-030

A arquitetura de componentes reduz duplicação de margens.

---

# 21. Especificações Oficiais

---

## GDS-SPACING-001

Todo espaçamento deverá utilizar exclusivamente a escala oficial.

---

## GDS-SPACING-002

É proibido utilizar valores arbitrários em componentes reutilizáveis.

---

## GDS-SPACING-003

Cards deverão utilizar padding padronizado.

---

## GDS-SPACING-004

Formulários deverão manter ritmo vertical consistente.

---

## GDS-SPACING-005

Tabelas deverão utilizar padding uniforme.

---

## GDS-SPACING-006

Dashboards deverão preservar espaçamento entre indicadores.

---

## GDS-SPACING-007

Containers deverão utilizar alinhamento consistente.

---

## GDS-SPACING-008

Responsividade deverá preservar a organização visual.

---

## GDS-SPACING-009

Novos componentes deverão reutilizar a escala oficial.

---

## GDS-SPACING-010

Toda evolução deverá preservar compatibilidade com o Design System.

---

# 22. Exemplos de Aplicação

## Dashboard

```
Título

Space-4

KPIs

Space-6

Gráficos

Space-8

Tabela
```

---

## Cadastro de Membros

```
Título

Space-6

Dados Pessoais

Space-8

Dados de Contato

Space-8

Dados Ministeriais

Space-8

Botões
```

---

## Financeiro

```
Título

Space-6

Filtros

Space-6

Tabela

Space-6

Paginação
```

---

## Comunicação

```
Título

Space-6

Filtros

Space-6

Campanhas

Space-6

Ações
```

---

# 23. Boas Práticas

O espaçamento é responsável por organizar visualmente toda a plataforma GereIgreja.

Sua utilização correta melhora significativamente a leitura, reduz a carga cognitiva do usuário e aumenta a percepção de qualidade da interface.

---

## Utilizar Exclusivamente a Escala Oficial

Todo espaçamento deverá utilizar os Design Tokens definidos neste documento.

Exemplos:

- Space-1
- Space-2
- Space-4
- Space-6
- Space-8
- Space-10

Evitar medidas arbitrárias.

---

## Manter Ritmo Visual

Toda página deverá apresentar ritmo consistente.

Exemplo:

Título

↓

Descrição

↓

Filtros

↓

Conteúdo

↓

Ações

↓

Rodapé

O usuário deverá compreender naturalmente a organização da interface.

---

## Agrupar Informações Relacionadas

Informações pertencentes ao mesmo contexto deverão permanecer próximas.

Exemplos:

- Dados pessoais;
- Dados ministeriais;
- Dados financeiros;
- Contatos;
- Endereços.

Separações excessivas prejudicam a leitura.

---

## Priorizar Espaços em Branco

O espaço em branco melhora significativamente a experiência do usuário.

Evitar interfaces excessivamente compactadas.

---

## Reutilizar Componentes

Cards, formulários, tabelas e modais deverão compartilhar o mesmo padrão de espaçamento.

A consistência reduz o tempo de aprendizagem da plataforma.

---

# 24. Anti-patterns

Os padrões abaixo não fazem parte da arquitetura oficial do GereIgreja.

---

## 24.1 Espaçamentos Arbitrários

Evitar:

```css
margin-top: 17px;
padding-left: 13px;
gap: 21px;
```

Utilizar apenas os Design Tokens oficiais.

---

## 24.2 Componentes Desalinhados

Não utilizar margens diferentes entre componentes equivalentes.

Todos deverão seguir a mesma escala.

---

## 24.3 Espaços Excessivos

Grandes áreas vazias reduzem produtividade.

O objetivo é proporcionar conforto visual sem desperdiçar espaço útil.

---

## 24.4 Interface Muito Compacta

Evitar componentes "colados".

A ausência de espaçamento dificulta leitura e aumenta erros de operação.

---

## 24.5 Misturar Escalas

Não utilizar diferentes escalas de espaçamento para resolver o mesmo problema.

A plataforma deverá possuir comportamento previsível.

---

## 24.6 Resolver Layout Apenas com Margens

Sempre que possível utilizar:

- Flexbox Gap;
- CSS Grid Gap;
- Containers;
- Grid Bootstrap.

Margens deverão ser utilizadas apenas quando realmente necessárias.

---

# 25. Checklist

Antes da aprovação de qualquer interface verificar.

---

## Organização

- [ ] ritmo visual consistente?
- [ ] alinhamentos corretos?
- [ ] agrupamentos lógicos?

---

## Design Tokens

- [ ] utiliza apenas Space Tokens?
- [ ] evita valores arbitrários?
- [ ] reutiliza componentes existentes?

---

## Componentes

- [ ] cards padronizados?
- [ ] formulários consistentes?
- [ ] tabelas consistentes?
- [ ] dashboards consistentes?

---

## Responsividade

- [ ] Desktop
- [ ] Notebook
- [ ] Tablet
- [ ] Smartphone

---

## Arquitetura

- [ ] compatível com Bootstrap?
- [ ] compatível com o Design System?
- [ ] compatível com GFE?

---

## Documentação

- [ ] alterações documentadas?
- [ ] novos padrões registrados?
- [ ] documentação revisada?

---

# 26. Glossário

## Espaçamento

Distância entre elementos da interface.

---

## Margin

Espaçamento externo de um componente.

---

## Padding

Espaçamento interno de um componente.

---

## Gap

Distância entre elementos distribuídos por Flexbox ou Grid.

---

## Ritmo Vertical

Organização das informações ao longo do eixo vertical da página.

---

## Ritmo Horizontal

Distribuição consistente dos elementos ao longo do eixo horizontal.

---

## Design Token

Representação reutilizável de uma propriedade visual.

Exemplos:

- Space-4
- Space-6
- Space-8

---

# 27. Governança

Toda alteração relacionada ao espaçamento deverá preservar a consistência visual do GereIgreja.

---

## Documentação

Novos padrões deverão ser documentados antes da implementação.

---

## Compatibilidade

Toda evolução deverá permanecer compatível com:

- Bootstrap;
- Design System;
- Frontend Engineering;
- Componentes reutilizáveis.

---

## Centralização

Os Design Tokens deverão permanecer centralizados.

Não criar escalas paralelas.

---

## Evolução

A arquitetura deverá crescer sem comprometer a consistência já estabelecida.

---

# 28. Roadmap

## Curto Prazo

- consolidação da escala oficial;
- padronização completa dos componentes;
- eliminação de margens arbitrárias.

---

## Médio Prazo

- documentação visual dos espaçamentos;
- biblioteca oficial de layouts;
- catálogo de exemplos.

---

## Longo Prazo

- adaptação para múltiplos temas;
- otimização para PWA;
- padronização para aplicações móveis;
- integração completa com futuras bibliotecas de componentes.

---

# 29. Documentos Relacionados

## GereIgreja Design System

- README.md
- GDS-01 — Introdução
- GDS-02 — Princípios
- GDS-03 — Cores
- GDS-04 — Tipografia
- GDS-06 — Grid
- GDS-07 — Iconografia
- GDS-08 — Botões
- GDS-09 — Formulários
- GDS-10 — Cards
- GDS-11 — Tabelas
- GDS-12 — Alertas
- GDS-13 — Modais
- GDS-14 — Navegação
- GDS-15 — Dashboards
- GDS-16 — Acessibilidade
- GDS-17 — Animações
- GDS-18 — Boas Práticas
- GDS-19 — Governança

---

## GereIgreja Frontend Engineering

- GFE-01 — Frontend Architecture
- GFE-02 — Estrutura de Pastas
- GFE-03 — Componentes
- GFE-04 — Layouts
- GFE-05 — Templates
- GFE-06 — Assets
- GFE-07 — CSS
- GFE-08 — JavaScript
- GFE-09 — HTMX
- GFE-10 — Alpine.js
- GFE-11 — Dashboards

---

# Conclusão

O sistema oficial de espaçamento do GereIgreja representa um dos pilares da consistência visual da plataforma.

A utilização de uma escala única de Design Tokens garante alinhamentos previsíveis, melhora a organização das interfaces, reduz a duplicação de estilos e facilita a manutenção de todo o ecossistema do GereIgreja.

Todo novo componente, layout ou módulo deverá utilizar exclusivamente os padrões definidos neste documento, assegurando uma experiência uniforme e profissional para todos os usuários.

---

# Status do Documento

**Pasta**

```
docs/design-system/
```

**Arquivo**

```
05-Espacamento.md
```

**Documento**

```
GDS-05
```

**Código**

```
GDS-SPACING
```

**Versão**

```
1.0
```

**Status**

```
OFICIAL
```

---

**Fim do Documento**

