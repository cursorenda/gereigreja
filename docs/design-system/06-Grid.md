Pasta:
docs/design-system/

Arquivo:
06-Grid.md

Documento:
GDS-06

Código:
GDS-GRID

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

# GDS-06 — Grid

> *"O sistema de Grid estabelece a estrutura espacial da interface do GereIgreja, permitindo páginas consistentes, responsivas e escaláveis em todos os módulos da plataforma."*

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia do Grid
4. Princípios
5. Arquitetura
6. Containers
7. Sistema de Colunas
8. Breakpoints
9. Gutters
10. Alinhamentos
11. Casos Reais do GereIgreja
12. Relação com os Demais Frameworks

---

# 1. Objetivo

Este documento define oficialmente a arquitetura de Grid utilizada pelo GereIgreja.

Seu propósito é padronizar a construção das interfaces da plataforma, garantindo:

- consistência visual;
- alinhamento entre componentes;
- excelente utilização do espaço disponível;
- comportamento responsivo;
- facilidade de manutenção;
- evolução sustentável da interface.

Toda página deverá seguir os padrões estabelecidos neste documento.

---

# 2. Escopo

As diretrizes deste documento aplicam-se a:

- Área de Gestão;
- Portal Público;
- Landing Pages;
- Dashboards;
- Formulários;
- Tabelas;
- Relatórios;
- Modais;
- Componentes reutilizáveis;
- Páginas administrativas.

---

# 3. Filosofia do Grid

O sistema de Grid organiza toda a interface do GereIgreja.

Sua função não é apenas posicionar elementos, mas estabelecer uma estrutura visual consistente que facilite:

- leitura;
- navegação;
- manutenção;
- reutilização;
- evolução da plataforma.

Layouts previsíveis reduzem a curva de aprendizagem do usuário.

---

# 4. Princípios

Toda implementação deverá respeitar os seguintes princípios.

- consistência;
- alinhamento;
- proporcionalidade;
- simplicidade;
- previsibilidade;
- responsividade;
- reutilização.

O Grid deverá permanecer invisível para o usuário, mas evidente para o desenvolvedor.

---

# 5. Arquitetura

A arquitetura oficial segue a seguinte hierarquia.

```
Viewport

↓

Container

↓

Row

↓

Column

↓

Card

↓

Componentes

↓

Conteúdo
```

Cada camada possui responsabilidade específica.

---

# 6. Containers

Os containers limitam a largura útil da interface.

Sua utilização garante alinhamento uniforme entre páginas.

Estrutura recomendada.

```
Container

↓

Header

↓

Breadcrumb

↓

Conteúdo

↓

Footer
```

Os containers deverão ser reutilizados por todos os módulos.

---

## Container Administrativo

Utilizado na Área de Gestão.

Características:

- largura ampla;
- foco em produtividade;
- excelente aproveitamento horizontal;
- suporte para dashboards.

---

## Container Público

Utilizado em:

- Home;
- Landing Pages;
- Blog;
- Funcionalidades;
- Planos;
- Contato.

Prioriza leitura e apresentação institucional.

---

# 7. Sistema de Colunas

O GereIgreja adota oficialmente o Grid de 12 colunas do Bootstrap.

Estrutura:

```
12 colunas

↓

6 + 6

↓

4 + 4 + 4

↓

3 + 3 + 3 + 3

↓

8 + 4

↓

9 + 3
```

Essa estrutura atende às necessidades atuais e futuras da plataforma.

---

## Distribuições Recomendadas

### Dashboard

```
3 + 3 + 3 + 3
```

KPIs.

---

### Dashboard Financeiro

```
8 + 4
```

Gráfico + Indicadores.

---

### Cadastro

```
6 + 6
```

Campos lado a lado.

---

### Relatórios

```
12
```

Largura integral.

---

### Portal Público

```
8 + 4

ou

9 + 3
```

Conteúdo principal e barra lateral.

---

# 8. Breakpoints

O sistema utiliza os breakpoints oficiais do Bootstrap.

| Breakpoint | Largura |
|------------|---------:|
| XS | <576 px |
| SM | ≥576 px |
| MD | ≥768 px |
| LG | ≥992 px |
| XL | ≥1200 px |
| XXL | ≥1400 px |

Novos breakpoints não deverão ser criados.

---

# 9. Gutters

Os gutters representam o espaçamento entre colunas.

Valores recomendados.

Desktop

```
24 px
```

Notebook

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

Toda a plataforma deverá compartilhar a mesma escala.

---

# 10. Alinhamentos

Os componentes deverão permanecer alinhados dentro do Grid.

Princípios:

- alinhamento vertical;
- alinhamento horizontal;
- consistência entre colunas;
- espaçamento uniforme.

Evitar desalinhamentos entre cards ou formulários.

---

# 11. Casos Reais do GereIgreja

## Dashboard Principal

Linha 1

```
4 KPIs
```

```
3 + 3 + 3 + 3
```

Linha 2

```
8 + 4
```

Gráfico financeiro + Eventos próximos.

---

## Cadastro de Membros

```
6 + 6
```

Nome

Telefone

---

```
6 + 6
```

Congregação

Departamento

---

## Secretaria

Filtros

```
12
```

Tabela

```
12
```

Paginação

```
12
```

---

## Financeiro

Resumo

```
3 + 3 + 3 + 3
```

Fluxo de Caixa

```
8 + 4
```

---

## Escola Bíblica

Turmas

```
4 + 4 + 4
```

---

## Comunicação

Campanhas

```
12
```

Indicadores

```
6 + 6
```

---

# 12. Relação com os Demais Frameworks

Este documento integra-se diretamente a:

- GDS-05 — Espaçamento
- GDS-04 — Tipografia
- GDS-03 — Cores
- GFE — Frontend Engineering
- Bootstrap 5

Toda implementação deverá permanecer compatível com os layouts oficiais definidos pelo Frontend Engineering.

---
# 13. Grid em Formulários

Os formulários representam um dos elementos mais importantes da Área de Gestão do GereIgreja.

O Grid deverá organizar os campos de maneira lógica, reduzindo o tempo de preenchimento e aumentando a produtividade dos usuários.

---

## Estrutura Recomendada

Cada formulário deverá ser dividido em grupos funcionais.

Exemplo:

```
Dados Pessoais

↓

Dados de Contato

↓

Dados Ministeriais

↓

Observações

↓

Ações
```

Cada grupo deverá ocupar uma linha independente.

---

## Distribuições Recomendadas

### Campo Único

```
12
```

Exemplos:

- Observações
- Endereço completo
- Biografia

---

### Dois Campos

```
6 + 6
```

Exemplos:

- Nome / CPF
- Telefone / Celular
- Cidade / Estado

---

### Três Campos

```
4 + 4 + 4
```

Exemplos:

- Dia
- Mês
- Ano

ou

- Banco
- Agência
- Conta

---

### Quatro Campos

```
3 + 3 + 3 + 3
```

Exemplos:

KPIs ou indicadores rápidos.

---

# 14. Grid em Dashboards

Os dashboards do GereIgreja deverão utilizar o Grid para destacar informações estratégicas.

---

## Linha de KPIs

Distribuição oficial:

```
3 + 3 + 3 + 3
```

Indicadores:

- Membros
- Congregações
- Eventos
- Financeiro

---

## Linha Principal

Distribuição:

```
8 + 4
```

Esquerda

Gráfico principal.

Direita

Resumo, eventos ou notificações.

---

## Linha Secundária

Distribuição:

```
6 + 6
```

Exemplo:

- Frequência
- Escola Bíblica

---

## Linha Completa

```
12
```

Utilizar para:

- tabelas;
- cronogramas;
- relatórios resumidos.

---

# 15. Grid em Tabelas

As tabelas deverão ocupar largura suficiente para garantir boa leitura.

Recomendação:

```
12
```

Filtros:

```
12
```

Tabela:

```
12
```

Paginação:

```
12
```

Quando houver painel lateral:

```
9 + 3
```

---

# 16. Grid em Modais

Os modais deverão utilizar Grid interno quando possuírem formulários extensos.

---

## Modal Pequeno

Campos:

```
12
```

---

## Modal Médio

Campos:

```
6 + 6
```

---

## Modal Grande

Estrutura:

```
8 + 4
```

Informações principais + painel auxiliar.

---

# 17. Grid em Relatórios

Relatórios priorizam leitura contínua.

Distribuição recomendada:

Cabeçalho

```
12
```

Filtros

```
12
```

Resumo

```
6 + 6
```

Tabela

```
12
```

Rodapé

```
12
```

---

# 18. Responsividade

Toda interface deverá adaptar automaticamente a distribuição das colunas.

---

## Desktop

Aproveitamento máximo do Grid.

---

## Notebook

Manter mesma estrutura sempre que possível.

---

## Tablet

Reduzir número de colunas.

Exemplo:

```
6 + 6

↓

12
```

---

## Smartphone

Toda informação deverá tornar-se vertical.

Exemplo:

```
3 + 3 + 3 + 3

↓

12

12

12

12
```

Nunca comprometer a leitura.

---

# 19. Layouts Administrativos

Os módulos administrativos deverão seguir a mesma organização estrutural.

Exemplos:

---

## Secretaria

```
Título

↓

Breadcrumb

↓

Filtros

↓

Tabela

↓

Paginação
```

---

## Financeiro

```
Resumo

↓

Gráficos

↓

Lançamentos

↓

Paginação
```

---

## Escola Bíblica

```
Indicadores

↓

Turmas

↓

Professores

↓

Alunos
```

---

## Comunicação

```
Campanhas

↓

Indicadores

↓

Histórico
```

---

## Configurações

```
Menu lateral

↓

Conteúdo

↓

Botões
```

---

# 20. Evidências Arquiteturais

As diretrizes deste documento refletem a arquitetura oficial do GereIgreja.

---

## EA-GDS-031

O Bootstrap constitui a base do sistema de Grid.

---

## EA-GDS-032

Toda a Área de Gestão utiliza Grid responsivo.

---

## EA-GDS-033

Os dashboards utilizam distribuição específica para KPIs.

---

## EA-GDS-034

Os layouts administrativos compartilham a mesma estrutura.

---

## EA-GDS-035

A arquitetura favorece futura expansão para PWA e aplicações móveis.

---

# 21. Especificações Oficiais

---

## GDS-GRID-001

Toda interface deverá utilizar o Grid oficial de 12 colunas.

---

## GDS-GRID-002

É proibido criar sistemas paralelos de Grid.

---

## GDS-GRID-003

Os breakpoints oficiais do Bootstrap deverão ser respeitados.

---

## GDS-GRID-004

Os containers oficiais deverão ser reutilizados.

---

## GDS-GRID-005

Os dashboards deverão utilizar distribuição padronizada.

---

## GDS-GRID-006

Os formulários deverão utilizar agrupamentos consistentes.

---

## GDS-GRID-007

As tabelas deverão privilegiar largura integral.

---

## GDS-GRID-008

Toda interface deverá permanecer responsiva.

---

## GDS-GRID-009

Novos layouts deverão respeitar a arquitetura existente.

---

## GDS-GRID-010

Toda evolução deverá preservar compatibilidade com o Design System.

---

# 22. Exemplos de Aplicação

## Dashboard Geral

```
3 | 3 | 3 | 3

↓

8 | 4

↓

6 | 6

↓

12
```

---

## Cadastro de Membros

```
6 | 6

↓

6 | 6

↓

12

↓

12
```

---

## Financeiro

```
3 | 3 | 3 | 3

↓

8 | 4

↓

12
```

---

## Portal Público

```
9 | 3

↓

12
```

---

## Página de Planos

```
4 | 4 | 4
```

---

## Blog

```
8 | 4
```

---

# 23. Boas Práticas

O Grid é um dos pilares da arquitetura visual do GereIgreja.

Sua utilização correta garante páginas organizadas, previsíveis e consistentes em todos os módulos da plataforma.

---

## Utilizar Sempre o Grid Oficial

Toda interface deverá utilizar o sistema oficial de 12 colunas.

Exemplos:

```
12

6 + 6

4 + 4 + 4

3 + 3 + 3 + 3

8 + 4

9 + 3
```

Evitar distribuições arbitrárias.

---

## Agrupar Informações Relacionadas

Campos pertencentes ao mesmo contexto deverão permanecer próximos.

Exemplos:

- Dados Pessoais
- Dados Ministeriais
- Dados Financeiros
- Contatos
- Endereços

O agrupamento reduz o tempo de preenchimento.

---

## Priorizar Leitura

O Grid deverá favorecer:

- leitura;
- localização de informações;
- produtividade;
- consistência visual.

---

## Utilizar Containers Oficiais

Não criar containers específicos para módulos individuais.

Todos deverão reutilizar a arquitetura oficial.

---

## Pensar Primeiro na Responsividade

Todo layout deverá ser planejado inicialmente considerando:

Desktop

↓

Notebook

↓

Tablet

↓

Smartphone

Não adaptar posteriormente.

Projetar responsivamente desde o início.

---

# 24. Anti-patterns

Os padrões abaixo não fazem parte da arquitetura oficial do GereIgreja.

---

## 24.1 Grid Paralelo

Não criar sistemas próprios de Grid.

Bootstrap constitui a base oficial.

---

## 24.2 Colunas Arbitrárias

Evitar:

```
5 + 7

2 + 10

1 + 11
```

quando não houver justificativa arquitetural.

Priorizar distribuições padronizadas.

---

## 24.3 Layout Inconsistente

Não alterar a organização de páginas semelhantes.

Exemplo:

Cadastro de membros

↓

Cadastro de congregações

↓

Cadastro de departamentos

Todos deverão compartilhar a mesma estrutura.

---

## 24.4 Cards Desalinhados

Todos os cards deverão manter alinhamento vertical e horizontal.

---

## 24.5 Excesso de Colunas

Evitar dividir a tela em muitas colunas pequenas.

A leitura deverá permanecer confortável.

---

## 24.6 Quebra da Responsividade

Nunca fixar larguras absolutas que impeçam adaptação para dispositivos móveis.

---

# 25. Checklist

Antes da aprovação de qualquer interface verificar.

---

## Estrutura

- [ ] utiliza Grid oficial?
- [ ] utiliza containers oficiais?
- [ ] utiliza gutters padronizados?

---

## Responsividade

- [ ] Desktop
- [ ] Notebook
- [ ] Tablet
- [ ] Smartphone

---

## Organização

- [ ] agrupamentos corretos?
- [ ] alinhamentos consistentes?
- [ ] distribuição proporcional?

---

## Componentes

- [ ] dashboards seguem o padrão?
- [ ] formulários seguem o padrão?
- [ ] tabelas seguem o padrão?
- [ ] modais seguem o padrão?

---

## Arquitetura

- [ ] compatível com Bootstrap?
- [ ] compatível com GFE?
- [ ] compatível com GDS?

---

## Documentação

- [ ] alterações registradas?
- [ ] novos padrões documentados?
- [ ] documentação atualizada?

---

# 26. Glossário

## Grid

Sistema responsável pela organização espacial da interface.

---

## Container

Elemento responsável por limitar a largura útil da página.

---

## Row

Linha utilizada para distribuir colunas.

---

## Column

Unidade estrutural do Grid.

---

## Breakpoint

Largura utilizada para adaptação responsiva.

---

## Gutter

Espaçamento entre colunas.

---

## Responsividade

Capacidade da interface adaptar-se automaticamente aos diferentes dispositivos.

---

# 27. Governança

Toda evolução do sistema de Grid deverá preservar a consistência da plataforma.

---

## Documentação

Novas regras deverão ser documentadas antes da implementação.

---

## Compatibilidade

O Grid deverá permanecer compatível com:

- Bootstrap;
- Design System;
- Frontend Engineering;
- Componentes reutilizáveis.

---

## Centralização

Toda alteração deverá ocorrer através da arquitetura oficial.

---

## Evolução

A arquitetura deverá suportar:

- novos módulos;
- novos dashboards;
- PWA;
- aplicações móveis;
- futuras expansões da plataforma.

---

# 28. Roadmap

## Curto Prazo

- consolidação da arquitetura de Grid;
- padronização completa das páginas administrativas;
- eliminação de layouts inconsistentes.

---

## Médio Prazo

- biblioteca oficial de layouts;
- catálogo de exemplos;
- documentação visual do Grid.

---

## Longo Prazo

- otimizações para PWA;
- suporte a aplicações móveis;
- templates White Label;
- integração completa com futuras bibliotecas de componentes.

---

# 29. Documentos Relacionados

## GereIgreja Design System

- README.md
- GDS-01 — Introdução
- GDS-02 — Princípios
- GDS-03 — Cores
- GDS-04 — Tipografia
- GDS-05 — Espaçamento
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

O sistema de Grid do GereIgreja constitui a base estrutural de toda a interface da plataforma.

Ao padronizar containers, colunas, gutters, breakpoints e distribuições, o projeto garante interfaces previsíveis, altamente responsivas e consistentes entre todos os módulos, desde a Área de Gestão até o Portal Público.

Toda nova tela, componente ou funcionalidade deverá utilizar exclusivamente a arquitetura definida neste documento, assegurando evolução sustentável, facilidade de manutenção e uma experiência uniforme para todos os usuários.

---

# Status do Documento

**Pasta**

```
docs/design-system/
```

**Arquivo**

```
06-Grid.md
```

**Documento**

```
GDS-06
```

**Código**

```
GDS-GRID
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

