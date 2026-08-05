Pasta:
docs/frontend/

Arquivo:
05-Templates.md

Documento:
GFE-05

Código:
GFE-TPL

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

# GFE-05 — Arquitetura dos Templates

> *"Os Templates representam a camada responsável pela composição da interface do GereIgreja. Eles conectam a arquitetura dos Layouts aos componentes reutilizáveis, formando páginas consistentes, organizadas e escaláveis."*

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia dos Templates
4. Arquitetura Geral
5. Organização Oficial
6. Estrutura de Pastas
7. Hierarquia dos Templates
8. Herança de Templates
9. Includes
10. Partials
11. Convenções de Nomenclatura
12. Evidências Arquiteturais
13. Inventário Oficial
14. Especificações Oficiais
15. Boas Práticas
16. Anti-patterns
17. Checklist
18. Glossário
19. Roadmap
20. Documentos Relacionados

---

# 1. Objetivo

Este documento define oficialmente a arquitetura dos Templates utilizados pelo GereIgreja.

Seu objetivo é estabelecer padrões para organização, reutilização, manutenção e evolução da camada de apresentação.

Todo Template desenvolvido para o sistema deverá seguir as diretrizes aqui estabelecidas.

---

# 2. Escopo

Este documento aplica-se exclusivamente aos Templates HTML utilizados pelo Frontend.

Inclui:

- Templates Base;
- Templates dos módulos;
- Includes;
- Partials;
- Estrutura de diretórios;
- Convenções de nomenclatura;
- Regras de herança;
- Organização da camada de apresentação.

Não inclui:

- CSS;
- JavaScript;
- Componentes;
- Models;
- Views;
- APIs.

---

# 3. Filosofia dos Templates

O GereIgreja adota oficialmente a filosofia de Templates enxutos.

Cada Template deve possuir uma única responsabilidade.

Templates não devem conter:

- regras de negócio;
- processamento de dados;
- validações complexas;
- cálculos.

Toda lógica permanece no Backend.

A camada de Templates é exclusivamente responsável pela apresentação.

---

# 4. Arquitetura Geral

Os Templates do GereIgreja são organizados em múltiplos níveis.

Arquitetura simplificada:

```
Layout Base

↓

Template do Módulo

↓

Includes

↓

Partials

↓

HTML Final
```

Essa arquitetura favorece reutilização e reduz duplicação de código.

---

# 5. Organização Oficial

A estrutura oficial é dividida em quatro grupos principais.

## Layouts

Responsáveis pela estrutura global da interface.

Exemplos:

- base.html
- base_com_menu.html
- dashboard_base.html
- base_landing.html

---

## Templates

Representam páginas completas.

Exemplos:

```
dashboard.html

listar.html

detalhes.html

editar.html

criar.html
```

---

## Includes

Trechos reutilizáveis compartilhados.

Exemplos encontrados no projeto:

```
includes/

app_footer.html

auth_footer.html

footer_social_links.html

public_footer.html
```

---

## Partials

Fragmentos reutilizáveis menores.

Podem existir:

- globalmente;
- dentro de módulos específicos.

Essa abordagem permite que cada App mantenha seus próprios fragmentos reutilizáveis quando necessário.

---

# 6. Estrutura de Pastas

A organização atualmente utilizada segue o padrão abaixo.

```
templates/

    base.html

    base_com_menu.html

    dashboard_base.html

    base_landing.html

    includes/

    partials/

    secretaria/

    financeiro/

    membros/

    eventos/

    comunicacao/

    ...
```

Além da pasta global `partials`, alguns Apps possuem suas próprias subpastas de Partials.

Exemplo conceitual:

```
financeiro/

    partials/

secretaria/

    partials/
```

Essa arquitetura permite reutilização local sem poluir o repositório global de Templates.

---

# 7. Hierarquia dos Templates

Os Templates seguem uma cadeia de herança baseada na arquitetura oficial.

```
base.html

↓

base_com_menu.html

↓

dashboard_base.html

↓

Template do módulo

↓

Includes

↓

Partials
```

Cada nível possui responsabilidade própria.

A reutilização deve ocorrer preferencialmente através dessa hierarquia.

---

# 8. Herança de Templates

O GereIgreja utiliza oficialmente o mecanismo de herança do Django.

Exemplo:

```django
{% extends "base_com_menu.html" %}
```

ou

```django
{% extends "dashboard_base.html" %}
```

A utilização de herança reduz duplicação e facilita manutenção.

Novos Templates devem sempre herdar de um Layout oficial.

Evitar Templates independentes.

---

# 9. Includes

Includes representam regiões compartilhadas da interface.

São reutilizados através de:

```django
{% include %}
```

No projeto foram identificados Includes globais como:

- app_footer.html
- auth_footer.html
- footer_social_links.html
- public_footer.html

Novos Includes deverão ser adicionados apenas quando houver reutilização entre múltiplas páginas.

---

# 10. Partials

Partials representam pequenos fragmentos reutilizáveis.

Sua principal característica é possuir responsabilidade extremamente específica.

Exemplos:

- cabeçalho de tabela;
- filtros;
- cards;
- linhas de formulários;
- painéis;
- badges;
- indicadores;
- blocos de estatísticas.

O GereIgreja utiliza duas abordagens:

## Partials Globais

Compartilhados por diversos módulos.

Localizados em:

```
templates/partials/
```

---

## Partials Locais

Específicos de um único módulo.

Exemplo conceitual:

```
financeiro/partials/

secretaria/partials/

membros/partials/
```

Essa organização reduz acoplamento entre módulos.

---

# 11. Convenções de Nomenclatura

A padronização da nomenclatura dos Templates facilita a manutenção da plataforma e torna a navegação pelo projeto mais intuitiva.

Todos os Templates deverão utilizar nomes claros, descritivos e consistentes.

---

## 11.1 Templates de Página

Preferencialmente utilizar nomes relacionados à funcionalidade.

Exemplos:

```
dashboard.html

lista.html

detalhes.html

editar.html

criar.html

visualizar.html
```

Evitar:

```
pagina1.html

novo2.html

teste.html

modelo.html
```

---

## 11.2 Includes

Os Includes representam estruturas compartilhadas.

Exemplos:

```
app_footer.html

auth_footer.html

footer_social_links.html

public_footer.html
```

A nomenclatura deve indicar claramente sua finalidade.

---

## 11.3 Partials

Partials deverão utilizar prefixo "_" sempre que representarem fragmentos reutilizáveis.

Exemplos encontrados na arquitetura:

```
_aba_dados_cadastrais.html

_aba_contribuicoes.html

_form_fields.html

_form_pessoa_oficial.html

_form_membro_oficial.html
```

Essa convenção facilita a identificação de arquivos que não representam páginas completas.

---

## 11.4 Templates de Dashboards

Sempre que possível utilizar nomes consistentes.

Exemplos:

```
dashboard.html

dashboard_financeiro.html

dashboard_secretaria.html
```

---

# 12. Evidências Arquiteturais

Este documento foi elaborado com base na estrutura atualmente implementada no GereIgreja.

---

## EA-TPL-001

Diretório

```
templates/
```

Responsabilidade

Repositório principal dos Templates compartilhados.

---

## EA-TPL-002

Arquivo

```
base.html
```

Responsabilidade

Base principal da Área de Gestão.

---

## EA-TPL-003

Arquivo

```
base_com_menu.html
```

Responsabilidade

Layout autenticado utilizado pelos módulos internos.

---

## EA-TPL-004

Arquivo

```
dashboard_base.html
```

Responsabilidade

Base oficial para Dashboards.

---

## EA-TPL-005

Diretório

```
templates/includes/
```

Responsabilidade

Centralização dos Includes compartilhados.

---

## EA-TPL-006

Diretório

```
templates/partials/
```

Responsabilidade

Centralização dos Partials compartilhados.

---

## EA-TPL-007

Diretórios

```
*/templates/*/partials/
```

Responsabilidade

Partials específicos dos Apps.

---

## EA-TPL-008

Arquivos identificados

```
app_footer.html

auth_footer.html

footer_social_links.html

public_footer.html
```

Representam Includes globais da plataforma.

---

# 13. Inventário Oficial

## Layouts Base

| Template | Categoria |
|-----------|-----------|
| base.html | Layout Base |
| base_com_menu.html | Layout Autenticado |
| dashboard_base.html | Dashboard |
| base_landing.html | Público |

---

## Includes Compartilhados

Atualmente identificados:

```
app_footer.html

auth_footer.html

footer_social_links.html

public_footer.html
```

---

## Partials Compartilhados

Exemplos identificados:

```
_aba_acesso_sistema.html

_aba_acompanhamento_visita.html

_aba_cargos.html

_aba_contribuicoes.html

_aba_dados_cadastrais.html

_aba_tipo_status.html

_form_dados_cadastrais.html

_form_fields.html

_form_membro_oficial.html

_form_pessoa_oficial.html
```

---

## Partials Locais

O projeto também utiliza Partials específicos de determinados Apps.

Esses arquivos permanecem próximos ao domínio de negócio correspondente.

---

# 14. Especificações Oficiais

As regras abaixo estabelecem o padrão oficial para evolução dos Templates do GereIgreja.

---

## GFE-TPL-001

Todo Template deverá possuir responsabilidade única.

---

## GFE-TPL-002

Templates não deverão conter regras de negócio.

---

## GFE-TPL-003

Sempre que possível utilizar herança de templates.

---

## GFE-TPL-004

Fragmentos reutilizáveis deverão utilizar Includes ou Partials.

---

## GFE-TPL-005

Partials compartilhados deverão permanecer preferencialmente na estrutura global.

---

## GFE-TPL-006

Partials específicos deverão permanecer dentro do respectivo App.

---

## GFE-TPL-007

Templates deverão preservar compatibilidade com os Layouts oficiais.

---

## GFE-TPL-008

Toda nova estrutura deverá ser documentada antes de tornar-se padrão arquitetural.

---

# 15. Boas Práticas

Durante o desenvolvimento recomenda-se:

- utilizar herança de templates;
- manter Templates pequenos;
- reutilizar Includes;
- reutilizar Partials;
- evitar HTML duplicado;
- documentar novos Templates;
- manter compatibilidade com o Design System;
- preservar separação entre apresentação e lógica de negócio;
- utilizar nomes consistentes para arquivos.

---

# 16. Anti-patterns

Os padrões abaixo não fazem parte da arquitetura oficial do GereIgreja e deverão ser evitados durante o desenvolvimento.

---

## 16.1 Templates Monolíticos

Evitar Templates excessivamente grandes contendo múltiplas responsabilidades.

Sempre que possível dividir a interface em:

- Includes;
- Partials;
- Componentes reutilizáveis.

---

## 16.2 Duplicação de HTML

Não copiar estruturas inteiras entre páginas.

Sempre verificar se já existe:

- Include;
- Partial;
- Template semelhante.

A duplicação aumenta o custo de manutenção.

---

## 16.3 Regras de Negócio na Camada de Templates

Templates não deverão executar regras de negócio.

Evitar:

- cálculos complexos;
- decisões de domínio;
- lógica de permissão;
- processamento de dados.

Toda lógica pertence ao Backend.

---

## 16.4 Estruturas Não Padronizadas

Evitar criar diretórios ou organizações diferentes da arquitetura oficial.

A estrutura deve permanecer previsível para toda a equipe.

---

## 16.5 Includes Excessivamente Grandes

Includes representam fragmentos reutilizáveis.

Caso um Include cresça demasiadamente, avaliar sua divisão em múltiplos Partials.

---

## 16.6 Partials Compartilhados Indevidamente

Partials específicos de um único módulo não deverão ser promovidos para a estrutura global sem justificativa.

Antes da promoção verificar:

- reutilização;
- independência do domínio;
- ausência de dependências específicas.

---

## 16.7 Templates Independentes

Evitar Templates que não utilizem herança.

Preferir sempre:

```django
{% extends "base_com_menu.html" %}
```

ou

```django
{% extends "dashboard_base.html" %}
```

---

## 16.8 JavaScript Embutido

Evitar grandes blocos JavaScript diretamente nos Templates.

Sempre que possível utilizar arquivos dedicados carregados através dos blocos apropriados.

---

## 16.9 CSS Embutido

Não utilizar grandes blocos CSS diretamente nas páginas.

O CSS deverá permanecer centralizado na estrutura oficial de Assets.

---

# 17. Checklist

Antes de criar ou alterar um Template verificar:

---

## Arquitetura

- [ ] Existe Template semelhante?
- [ ] Está utilizando Layout oficial?
- [ ] A responsabilidade está claramente definida?

---

## Organização

- [ ] O Template permanece pequeno?
- [ ] A estrutura está organizada?
- [ ] O HTML está legível?

---

## Reutilização

- [ ] Há Includes reutilizáveis?
- [ ] Há Partials reutilizáveis?
- [ ] Existe duplicação de código?

---

## Compatibilidade

- [ ] Compatível com os Layouts oficiais?
- [ ] Compatível com o Design System?
- [ ] Compatível com os padrões do Frontend?

---

## Documentação

- [ ] Evidências atualizadas?
- [ ] Inventário atualizado?
- [ ] Convenções respeitadas?

---

# 18. Glossário

## Template

Arquivo responsável pela apresentação visual de uma página.

Representa a principal unidade de renderização da interface.

---

## Layout

Template responsável pela estrutura principal da aplicação.

Serve como base para outros Templates.

---

## Include

Fragmento reutilizável incorporado através da diretiva:

```django
{% include %}
```

Utilizado para compartilhar regiões comuns da interface.

---

## Partial

Fragmento reutilizável de menor granularidade.

Pode existir:

- globalmente;
- dentro de um App específico.

---

## Herança de Templates

Mecanismo do Django utilizado para reutilizar estruturas através da diretiva:

```django
{% extends %}
```

---

## Template Base

Template responsável pela infraestrutura da renderização.

Exemplo:

```
base.html
```

---

## Template de Módulo

Template pertencente a um domínio específico da aplicação.

Exemplos:

- Secretaria;
- Financeiro;
- Eventos;
- Escola Bíblica.

---

## Dashboard

Template especializado para apresentação de indicadores e métricas.

Utiliza oficialmente:

```
dashboard_base.html
```

---

## Área de Gestão

Interface principal utilizada pelos usuários autenticados do GereIgreja.

---

## Administração Técnica

Interface administrativa baseada no Django Admin.

Mantém arquitetura independente da Área de Gestão.

---

# 19. Roadmap

A arquitetura de Templates foi projetada para evoluir de forma incremental.

---

## Curto Prazo

- Consolidação da estrutura atual;
- Padronização completa dos Templates;
- Expansão da documentação arquitetural.

---

## Médio Prazo

- Maior reutilização de Includes e Partials;
- Redução progressiva de duplicação de HTML;
- Ampliação da padronização entre módulos.

---

## Longo Prazo

- Integração gradual com HTMX;
- Utilização progressiva de Alpine.js;
- Evolução para componentes mais desacoplados;
- Suporte a múltiplos temas;
- Compatibilidade com futuras interfaces móveis.

Toda evolução deverá preservar a arquitetura oficial estabelecida neste documento.

---

# 20. Documentos Relacionados

## GereIgreja Frontend Engineering

- README.md
- GFE-01 — Frontend Architecture
- GFE-02 — Estrutura de Pastas
- GFE-03 — Componentes
- GFE-04 — Layouts
- GFE-06 — Assets
- GFE-07 — CSS
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

Os Templates constituem a camada responsável por transformar a arquitetura dos Layouts em páginas funcionais, organizadas e reutilizáveis.

A utilização consistente de herança de templates, Includes e Partials reduz duplicação de código, facilita a manutenção da plataforma e garante uniformidade visual entre todos os módulos do GereIgreja.

Toda nova implementação deverá respeitar os padrões estabelecidos neste documento, preservando a organização da camada de apresentação e assegurando a evolução sustentável do Frontend.

---

# Status do Documento

**Pasta**

```
docs/frontend/
```

**Arquivo**

```
05-Templates.md
```

**Código**

```
GFE-TPL
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

