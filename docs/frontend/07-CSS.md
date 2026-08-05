Pasta:
docs/frontend/

Arquivo:
07-CSS.md

Documento:
GFE-07

Código:
GFE-CSS

Framework:
GereIgreja Frontend Engineering (GFE)

Versão:
2.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Agosto de 2026

# GFE-07 — Arquitetura CSS

> *"O CSS do GereIgreja é responsável por transformar a arquitetura dos Layouts e Templates em uma interface consistente, acessível e escalável. Sua organização deve privilegiar reutilização, previsibilidade e facilidade de manutenção."*

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia do CSS
4. Arquitetura Geral
5. Organização Oficial
6. Estrutura dos Arquivos CSS
7. CSS Compartilhado
8. CSS dos Dashboards
9. Convenções de Nomenclatura
10. Integração com Bootstrap
11. Evidências Arquiteturais
12. Inventário Oficial
13. Especificações Oficiais
14. Boas Práticas
15. Anti-patterns
16. Checklist
17. Glossário
18. Roadmap
19. Documentos Relacionados

---

# 1. Objetivo

Este documento define oficialmente a arquitetura CSS utilizada pelo Frontend do GereIgreja.

Seu objetivo é padronizar a construção das folhas de estilo, estabelecer critérios para reutilização dos estilos e preservar a consistência visual da plataforma.

---

# 2. Escopo

Este documento aplica-se exclusivamente à camada CSS.

Inclui:

- organização dos arquivos;
- estilos compartilhados;
- estilos específicos;
- convenções de nomenclatura;
- integração com Bootstrap;
- integração com o Design System;
- regras de manutenção.

Não inclui:

- HTML;
- JavaScript;
- Templates;
- Layouts;
- Componentes.

---

# 3. Filosofia do CSS

A arquitetura CSS do GereIgreja segue alguns princípios fundamentais.

## Reutilização

Sempre reutilizar estilos existentes antes de criar novos.

---

## Simplicidade

As regras devem permanecer pequenas e objetivas.

---

## Organização

Cada arquivo deve possuir responsabilidade bem definida.

---

## Escalabilidade

Novos módulos deverão aproveitar a arquitetura existente.

---

## Compatibilidade

Os estilos devem funcionar de forma consistente em todos os módulos da plataforma.

---

# 4. Arquitetura Geral

A organização da camada CSS baseia-se em uma estrutura compartilhada.

Fluxo conceitual:

```
Design System

↓

Bootstrap

↓

CSS Compartilhado

↓

CSS dos Dashboards

↓

CSS dos Módulos

↓

Página Final
```

Essa arquitetura evita duplicação e facilita evolução futura.

---

# 5. Organização Oficial

Atualmente a organização privilegia arquivos compartilhados, mas o projeto ainda está em processo de migração gradual em relação a estilos legados e folhas de estilo mais antigas.

Estrutura conceitual:

```
static/

    css/

        dashboard-base.css

        ...

```

Outros arquivos específicos poderão existir quando pertencerem claramente a um módulo.

---

# 6. Estrutura dos Arquivos CSS

Os arquivos CSS deverão ser organizados conforme sua responsabilidade.

## CSS Global

Responsável pelos estilos reutilizados por toda a plataforma.

---

## CSS de Dashboards

Responsável exclusivamente pelos Dashboards Premium.

Arquivo identificado:

```
dashboard-base.css
```

---

## CSS Específico

Arquivos destinados exclusivamente a um determinado módulo.

Devem permanecer restritos ao domínio correspondente.

---

# 7. CSS Compartilhado

O CSS compartilhado representa a base visual da plataforma.

Seu objetivo é fornecer:

- identidade visual;
- padronização;
- reutilização;
- consistência entre módulos.

Sempre que possível novos estilos deverão ser incorporados ao CSS compartilhado. Em projetos com base mais antiga, essa migração pode acontecer de forma incremental, preservando compatibilidade com módulos já existentes.

---

# 8. CSS dos Dashboards

Os Dashboards Premium utilizam um arquivo dedicado.

Arquivo oficial:

```
dashboard-base.css
```

Esse arquivo é carregado automaticamente por:

```
dashboard_base.html
```

Sua responsabilidade inclui:

- estrutura dos dashboards;
- cabeçalhos;
- breadcrumbs;
- filtros;
- responsividade;
- comportamento Full Width;
- integração com a Sidebar.

---

# 9. Convenções de Nomenclatura

As classes CSS deverão utilizar nomes claros e consistentes.

Exemplos identificados:

```
fp-page

fp-header

fp-title

fp-breadcrumb

fp-filters

fp-menu-toggle
```

Essas classes representam a identidade visual dos Dashboards Premium.

Novas classes deverão seguir o mesmo padrão.

---

# 10. Integração com Bootstrap

O Bootstrap constitui a base responsiva da plataforma.

Sua utilização deverá priorizar:

- Grid;
- Espaçamentos;
- Utilitários;
- Responsividade.

Customizações deverão complementar o Bootstrap e não substituí-lo.

---

# 11. Evidências Arquiteturais

Este documento foi elaborado com base na estrutura CSS atualmente implementada no GereIgreja.

As evidências abaixo representam os principais arquivos, convenções e recursos identificados durante a análise do Frontend.

---

## EA-CSS-001

Diretório

```
static/css/
```

Responsabilidade

Repositório oficial das folhas de estilo compartilhadas da plataforma.

---

## EA-CSS-002

Arquivo

```
dashboard-base.css
```

Responsabilidade

Folha de estilos oficial dos Dashboards Premium.

É carregada automaticamente por:

```
dashboard_base.html
```

---

## EA-CSS-003

Template

```
dashboard_base.html
```

Responsabilidade

Realiza o carregamento do CSS compartilhado dos dashboards através do bloco:

```django
{% block dashboard_css %}
```

Permitindo que cada dashboard carregue estilos adicionais quando necessário.

---

## EA-CSS-004

Convenção de Classes

Prefixo identificado:

```
fp-
```

Exemplos encontrados:

```
fp-page

fp-header

fp-title

fp-title-wrap

fp-breadcrumb

fp-filters

fp-filter-pill

fp-menu-toggle
```

Esse prefixo caracteriza a identidade visual dos Dashboards Premium.

---

## EA-CSS-005

Bootstrap

Responsabilidade

Base responsiva utilizada em toda a Área de Gestão.

Exemplos observados:

```
container

row

col

d-flex

gap-3

mb-1

align-items-center
```

---

## EA-CSS-006

Font Awesome

Integração direta com o CSS.

Exemplos observados:

```
fas fa-bars

fas fa-home
```

---

## EA-CSS-007

Área Pública

Os templates públicos utilizam folhas de estilo independentes da Área de Gestão, preservando identidade visual própria.

---

## EA-CSS-008

Administração Técnica

O Django Admin utiliza sua própria estrutura de estilos.

Não compartilha o CSS da Área de Gestão.

---

# 12. Inventário Oficial

## Diretórios

| Diretório | Situação |
|-----------|----------|
| static/css/ | Oficial |

---

## Arquivos Identificados

| Arquivo | Finalidade |
|----------|------------|
| dashboard-base.css | Dashboard Premium |

---

## Prefixos Oficiais

Atualmente identificados.

| Prefixo | Utilização |
|----------|------------|
| fp- | Dashboards Premium |

---

## Frameworks Integrados

| Framework | Situação |
|------------|----------|
| Bootstrap | Oficial |
| Font Awesome | Oficial |

---

## Organização Atual

A arquitetura CSS privilegia:

- estilos compartilhados;
- reutilização;
- integração com Bootstrap;
- organização por responsabilidade.

---

# 13. Especificações Oficiais

As regras abaixo estabelecem o padrão oficial para evolução da camada CSS.

---

## GFE-CSS-001

Todo CSS compartilhado deverá permanecer centralizado.

---

## GFE-CSS-002

Evitar duplicação de regras.

---

## GFE-CSS-003

Utilizar nomenclatura consistente para classes.

---

## GFE-CSS-004

Classes reutilizáveis deverão possuir responsabilidade única.

---

## GFE-CSS-005

Novos arquivos CSS deverão possuir documentação correspondente.

---

## GFE-CSS-006

Customizações deverão complementar o Bootstrap.

Não substituir sua arquitetura.

---

## GFE-CSS-007

Evitar utilização excessiva de seletores altamente específicos.

Priorizar classes reutilizáveis.

---

## GFE-CSS-008

Novas convenções de nomenclatura deverão ser aprovadas antes de se tornarem padrão.

---

# 14. Boas Práticas

Durante o desenvolvimento recomenda-se:

- reutilizar classes existentes;
- manter arquivos organizados;
- utilizar nomes descritivos;
- agrupar regras relacionadas;
- documentar novos estilos compartilhados;
- evitar duplicação de código;
- preservar compatibilidade com Bootstrap;
- preservar compatibilidade com o Design System;
- manter baixo acoplamento entre módulos;
- utilizar prefixos consistentes.

---

# 15. Anti-patterns

Os padrões abaixo não fazem parte da arquitetura oficial.

---

## 15.1 CSS Duplicado

Evitar repetir regras já existentes.

---

## 15.2 Classes Genéricas

Evitar nomes como:

```
.box

.item

.div1

.style2
```

Preferir nomes semânticos relacionados à função do elemento.

---

## 15.3 Uso Excessivo de !important

O uso de:

```css
!important
```

deverá ocorrer apenas em situações excepcionais e tecnicamente justificadas.

---

## 15.4 Mistura de Responsabilidades

Um único arquivo CSS não deverá concentrar estilos de múltiplos domínios distintos.

---

## 15.5 Seletores Excessivamente Complexos

Evitar seletores longos e altamente específicos.

Eles dificultam manutenção e reutilização.

---

## 15.6 Sobrescrever Bootstrap Sem Necessidade

Sempre que possível utilizar as capacidades nativas do Bootstrap antes de criar novas regras.

---

## 15.7 Inconsistência Visual

Novos estilos deverão preservar a identidade visual estabelecida pelo Design System do GereIgreja.

---
# 16. Checklist

Antes de criar, alterar ou remover regras CSS, verificar os itens abaixo.

---

## Organização

- [ ] O arquivo CSS correto está sendo utilizado?
- [ ] A alteração pertence realmente a este arquivo?
- [ ] O CSS permanece organizado por responsabilidade?

---

## Reutilização

- [ ] Já existe classe equivalente?
- [ ] Foi evitada duplicação?
- [ ] O estilo pode ser reutilizado por outros módulos?

---

## Bootstrap

- [ ] A solução poderia utilizar classes nativas do Bootstrap?
- [ ] Houve necessidade real de customização?
- [ ] Nenhuma classe do Bootstrap foi sobrescrita desnecessariamente?

---

## Responsividade

- [ ] Funciona em Desktop?
- [ ] Funciona em Notebook?
- [ ] Funciona em Tablet?
- [ ] Funciona em Smartphone?

---

## Performance

- [ ] Foram evitados seletores excessivamente complexos?
- [ ] O CSS permanece pequeno e organizado?
- [ ] Não existem regras mortas?

---

## Design System

- [ ] Mantém a identidade visual?
- [ ] Mantém consistência entre módulos?
- [ ] Preserva os padrões oficiais?

---

## Documentação

- [ ] Inventário atualizado?
- [ ] Evidências atualizadas?
- [ ] Especificações preservadas?

---

# 17. Glossário

## CSS Compartilhado

Conjunto de estilos reutilizados por diversos módulos da plataforma.

---

## CSS Específico

Arquivo destinado exclusivamente a um determinado módulo.

Não deve ser utilizado por outros domínios sem necessidade.

---

## Dashboard CSS

Folha de estilos utilizada pelos Dashboards Premium.

Arquivo oficial:

```
dashboard-base.css
```

---

## Bootstrap

Framework CSS utilizado como base da responsividade e dos componentes visuais do GereIgreja.

---

## Classe CSS

Identificador reutilizável aplicado aos elementos HTML para definição de estilos.

---

## Prefixo

Convenção utilizada para agrupar classes pertencentes a um mesmo contexto.

Exemplo identificado:

```
fp-
```

Utilizado pelos Dashboards Premium.

---

## Responsividade

Capacidade da interface adaptar-se automaticamente aos diferentes tamanhos de tela.

---

## Design System

Conjunto de padrões visuais e de experiência que orienta toda a construção da interface do GereIgreja.

---

## CSS Modular

Estratégia em que cada arquivo possui responsabilidade específica, reduzindo acoplamento e facilitando manutenção.

---

# 18. Roadmap

A arquitetura CSS do GereIgreja foi projetada para evoluir continuamente mantendo compatibilidade com os módulos existentes.

---

## Curto Prazo

- Consolidação dos estilos compartilhados;
- Revisão da organização dos arquivos CSS;
- Padronização completa das convenções de nomenclatura;
- Expansão da documentação técnica.

---

## Médio Prazo

- Redução de regras duplicadas;
- Ampliação da reutilização entre módulos;
- Evolução gradual da arquitetura CSS;
- Maior integração com os Componentes oficiais.

---

## Longo Prazo

- Sistema oficial de temas;
- Suporte a White Label;
- Tokens visuais centralizados;
- Otimização para Core Web Vitals;
- Automatização de validações CSS;
- Evolução contínua do Design System.

Toda evolução deverá preservar compatibilidade com a arquitetura oficial estabelecida neste documento.

---

# 19. Documentos Relacionados

## GereIgreja Frontend Engineering

- README.md
- GFE-01 — Frontend Architecture
- GFE-02 — Estrutura de Pastas
- GFE-03 — Componentes
- GFE-04 — Layouts
- GFE-05 — Templates
- GFE-06 — Assets
- GFE-08 — JavaScript
- GFE-09 — HTMX
- GFE-10 — Alpine.js
- GFE-11 — Dashboards

---

## Documentação Corporativa

- GereIgreja Design System (GDS)
- GereIgreja Documentation Framework (GDF)
- GereIgreja Quality Framework (GQF)

---

# Conclusão

A arquitetura CSS do GereIgreja estabelece os princípios responsáveis pela identidade visual da plataforma, garantindo consistência, reutilização e facilidade de manutenção.

A organização baseada em estilos compartilhados, integração com Bootstrap, utilização de convenções de nomenclatura e separação clara de responsabilidades permite que novos módulos sejam desenvolvidos mantendo a mesma experiência visual em toda a plataforma.

O arquivo `dashboard-base.css` representa atualmente a principal implementação dessa arquitetura, servindo como base para os Dashboards Premium e demonstrando a padronização adotada pelo projeto.

Toda evolução futura deverá respeitar os princípios definidos neste documento, preservando compatibilidade com os Layouts, Templates, Componentes, Assets e com o Design System oficial do GereIgreja.

---

# Status do Documento

**Pasta**

```
docs/frontend/
```

**Arquivo**

```
07-CSS.md
```

**Código**

```
GFE-CSS
```

**Versão**

```
2.0
```

**Status**

```
OFICIAL
```

---

**Fim do Documento**

