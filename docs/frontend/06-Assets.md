Pasta:
docs/frontend/

Arquivo:
06-Assets.md

Documento:
GFE-06

Código:
GFE-AST

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

# GFE-06 — Arquitetura de Assets

> *"Os Assets representam todos os recursos estáticos utilizados pelo Frontend do GereIgreja. Sua organização adequada garante desempenho, reutilização, escalabilidade e facilidade de manutenção."*

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia dos Assets
4. Arquitetura Geral
5. Organização Oficial
6. Estrutura de Diretórios
7. Tipos de Assets
8. Carregamento dos Assets
9. Bibliotecas Externas
10. Assets por Aplicação
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

Este documento define oficialmente a arquitetura dos Assets utilizados pelo Frontend do GereIgreja.

Seu objetivo é padronizar a organização dos arquivos estáticos, estabelecer regras para reutilização e facilitar a evolução da plataforma.

---

# 2. Escopo

Este documento aplica-se aos recursos estáticos utilizados pelo Frontend.

Inclui:

- CSS;
- JavaScript;
- imagens;
- ícones;
- fontes;
- arquivos auxiliares;
- bibliotecas externas;
- estrutura da pasta `static`.

Não inclui:

- Templates;
- Layouts;
- Componentes;
- Models;
- Views.

---

# 3. Filosofia dos Assets

Os Assets representam recursos compartilhados da interface.

Devem ser organizados de forma previsível, reutilizável e desacoplada da lógica de negócio.

Sempre que possível:

- reutilizar arquivos existentes;
- evitar duplicação;
- centralizar recursos comuns;
- manter nomes consistentes.

---

# 4. Arquitetura Geral

O GereIgreja utiliza como principal repositório de recursos estáticos a pasta:

```
static/
```

Estrutura conceitual:

```
static/

    css/

    js/

    img/

    fonts/

    secretaria/

    financeiro/

    eventos/

    ...
```

Embora existam Assets específicos de alguns Apps, a arquitetura prioriza recursos globais compartilhados.

---

# 5. Organização Oficial

A organização oficial dos Assets divide-se em duas categorias.

## Assets Compartilhados

Utilizados por toda a plataforma.

Exemplos:

- CSS globais;
- JavaScript compartilhado;
- imagens institucionais;
- ícones;
- logotipos.

---

## Assets Específicos

Pertencem exclusivamente a um módulo.

Exemplos:

```
secretaria/

financeiro/

eventos/
```

Esses Assets permanecem próximos ao domínio correspondente.

---

# 6. Estrutura de Diretórios

A estrutura atualmente adotada possui como base a pasta:

```
static/
```

Principais diretórios identificados:

```
css/

js/

img/
```

Também foram identificados diretórios específicos para determinados módulos.

Essa arquitetura permite coexistência entre recursos globais e específicos.

---

# 7. Tipos de Assets

O Frontend utiliza diferentes categorias de recursos.

## CSS

Responsável pela apresentação visual.

---

## JavaScript

Responsável pelo comportamento da interface.

---

## Imagens

Logotipos, banners, ilustrações e demais elementos gráficos.

---

## Ícones

O projeto utiliza oficialmente o Font Awesome como biblioteca principal de ícones.

---

## Fontes

Arquivos tipográficos utilizados pela plataforma.

Quando possível, utilizar carregamento otimizado.

---

# 8. Carregamento dos Assets

Todos os Assets locais deverão ser carregados utilizando a infraestrutura oficial do Django.

Exemplo:

```django
{% load static %}
```

Utilização:

```django
<link rel="stylesheet"
      href="{% static 'css/dashboard-base.css' %}">
```

ou

```django
<script
src="{% static 'js/dashboard-sidebar.js' %}">
</script>
```

Essa abordagem garante compatibilidade entre ambientes de desenvolvimento e produção.

---

# 9. Bibliotecas Externas

O GereIgreja também utiliza bibliotecas externas.

Estado atual identificado:

## Bootstrap

Utilizado oficialmente.

Responsável pela base responsiva da interface.

---

## Font Awesome

Utilizado amplamente em toda a plataforma.

Presente em:

- Área de Gestão;
- Área Pública;
- menus;
- dashboards;
- telas administrativas.

---

## HTMX

Definido como diretriz arquitetural.

A adoção prática ainda ocorre de forma gradual.

Até o momento da análise não foram identificados atributos HTMX utilizados em larga escala.

---

## Alpine.js

Também definido como diretriz oficial.

Sua utilização permanece planejada e gradual.

Ainda não foram identificadas marcações características em uso amplo.

---

## Vendor

Atualmente não existe uma pasta dedicada para bibliotecas de terceiros.

Grande parte das bibliotecas é carregada diretamente por CDN.

Essa estratégia reduz manutenção, porém depende da disponibilidade dos serviços externos.

---

# 10. Assets por Aplicação

Embora a arquitetura privilegie Assets globais, alguns módulos mantêm arquivos específicos.

Exemplo conceitual:

```
static/

    secretaria/

    financeiro/

    eventos/
```

Esses Assets não substituem os recursos compartilhados.

Seu uso deve restringir-se ao domínio correspondente.

---

# 11. Evidências Arquiteturais

Este documento foi elaborado com base na estrutura atualmente implementada no GereIgreja.

As evidências abaixo representam os principais diretórios e arquivos responsáveis pela arquitetura dos Assets.

---

## EA-AST-001

Diretório

```
static/
```

Responsabilidade

Repositório principal de todos os recursos estáticos da plataforma.

---

## EA-AST-002

Diretório

```
static/css/
```

Responsabilidade

Centralização das folhas de estilo compartilhadas.

---

## EA-AST-003

Diretório

```
static/js/
```

Responsabilidade

Centralização dos scripts JavaScript utilizados pelo Frontend.

---

## EA-AST-004

Diretório

```
static/img/
```

Responsabilidade

Armazenamento das imagens institucionais e recursos gráficos.

---

## EA-AST-005

Arquivo

```
dashboard-base.css
```

Responsabilidade

Folha de estilos oficial dos Dashboards Premium.

Utilizada por:

```
dashboard_base.html
```

---

## EA-AST-006

Arquivo

```
dashboard-sidebar.js
```

Responsabilidade

Gerenciamento do comportamento da Sidebar dos Dashboards.

Funções identificadas:

- abertura;
- fechamento;
- persistência via Local Storage;
- alternância do modo Full Width.

---

## EA-AST-007

Biblioteca

```
Bootstrap
```

Responsabilidade

Framework CSS utilizado como base responsiva da plataforma.

Situação:

**Oficial**

---

## EA-AST-008

Biblioteca

```
Font Awesome
```

Responsabilidade

Biblioteca oficial de ícones.

Situação:

**Utilização consolidada**

---

## EA-AST-009

Tecnologia

```
HTMX
```

Responsabilidade

Melhorar interações através de requisições parciais.

Situação atual:

Diretriz arquitetural oficial.

Adoção gradual.

---

## EA-AST-010

Tecnologia

```
Alpine.js
```

Responsabilidade

Interações leves da interface.

Situação atual:

Diretriz arquitetural.

Adoção gradual.

---

## EA-AST-011

Diretórios específicos

Exemplos identificados

```
static/secretaria/

static/financeiro/

static/eventos/
```

Responsabilidade

Assets específicos de determinados módulos.

---

# 12. Inventário Oficial

## Diretórios Compartilhados

| Diretório | Situação |
|-----------|----------|
| static/ | Oficial |
| static/css/ | Oficial |
| static/js/ | Oficial |
| static/img/ | Oficial |

---

## Arquivos Compartilhados

Arquivos atualmente identificados.

| Arquivo | Categoria |
|----------|-----------|
| dashboard-base.css | CSS |
| dashboard-sidebar.js | JavaScript |

---

## Bibliotecas Oficiais

| Biblioteca | Situação |
|-------------|----------|
| Bootstrap | Oficial |
| Font Awesome | Oficial |
| HTMX | Adoção Gradual |
| Alpine.js | Adoção Gradual |

---

## Organização Atual

O projeto utiliza predominantemente Assets compartilhados.

Assets específicos são utilizados apenas quando pertencem claramente a um domínio funcional.

Essa organização reduz duplicação de recursos.

---

# 13. Especificações Oficiais

As regras abaixo estabelecem o padrão oficial para evolução dos Assets do GereIgreja.

---

## GFE-AST-001

Todo Asset compartilhado deverá permanecer na estrutura global.

---

## GFE-AST-002

Assets específicos deverão permanecer restritos ao respectivo módulo.

---

## GFE-AST-003

Não duplicar arquivos CSS.

---

## GFE-AST-004

Não duplicar arquivos JavaScript.

---

## GFE-AST-005

Bibliotecas externas deverão possuir justificativa técnica para utilização.

---

## GFE-AST-006

Sempre utilizar o carregamento oficial do Django através de:

```django
{% load static %}
```

---

## GFE-AST-007

Evitar dependências desnecessárias de bibliotecas externas.

---

## GFE-AST-008

Toda nova categoria de Assets deverá ser documentada antes de tornar-se padrão.

---

# 14. Boas Práticas

Durante o desenvolvimento recomenda-se:

- reutilizar Assets existentes;
- manter nomenclatura consistente;
- utilizar carregamento via `{% static %}`;
- manter separação entre Assets globais e específicos;
- documentar novos recursos compartilhados;
- remover arquivos obsoletos;
- evitar duplicação de imagens;
- utilizar CSS compartilhado sempre que possível;
- utilizar JavaScript modular;
- preservar compatibilidade com o Design System.

---

# 15. Anti-patterns

Os padrões abaixo não fazem parte da arquitetura oficial do GereIgreja.

---

## 15.1 Duplicação de Assets

Evitar múltiplas versões do mesmo arquivo.

---

## 15.2 CSS Duplicado

Não copiar estilos entre módulos.

Sempre reutilizar os arquivos compartilhados.

---

## 15.3 JavaScript Duplicado

Scripts compartilhados deverão permanecer centralizados.

---

## 15.4 Assets Sem Utilização

Arquivos não utilizados deverão ser removidos.

A presença de Assets obsoletos aumenta o custo de manutenção.

---

## 15.5 Bibliotecas Desnecessárias

Evitar adicionar novas bibliotecas quando a funcionalidade já existir na plataforma.

---

## 15.6 Recursos Externos Excessivos

Embora CDNs sejam utilizados atualmente, evitar dependência excessiva de serviços externos quando houver alternativa local adequada.

---

## 15.7 Organização Inconsistente

Não criar novas estruturas de diretórios sem aprovação arquitetural.

Toda evolução deverá preservar a organização oficial dos Assets.

---
# 16. Checklist

Antes de criar, alterar ou remover um Asset, verificar os itens abaixo.

---

## Organização

- [ ] O Asset está na pasta correta?
- [ ] Existe recurso semelhante?
- [ ] A nomenclatura segue o padrão oficial?

---

## Reutilização

- [ ] O Asset pode ser compartilhado?
- [ ] Já existe arquivo equivalente?
- [ ] A duplicação foi evitada?

---

## CSS

- [ ] O estilo poderia ser incorporado ao CSS compartilhado?
- [ ] O arquivo permanece organizado?
- [ ] Não há regras duplicadas?

---

## JavaScript

- [ ] O código é reutilizável?
- [ ] Está desacoplado do módulo?
- [ ] Foi carregado através do bloco correto?

---

## Imagens

- [ ] O nome do arquivo é descritivo?
- [ ] A imagem possui resolução adequada?
- [ ] O formato escolhido é apropriado (SVG, PNG, WebP, JPG)?

---

## Bibliotecas

- [ ] Existe justificativa para a utilização?
- [ ] A biblioteca já não existe no projeto?
- [ ] O impacto no desempenho foi avaliado?

---

## Documentação

- [ ] Inventário atualizado?
- [ ] Evidências atualizadas?
- [ ] Especificações preservadas?

---

# 17. Glossário

## Asset

Qualquer recurso estático utilizado pelo Frontend.

Exemplos:

- CSS;
- JavaScript;
- imagens;
- ícones;
- fontes;
- arquivos auxiliares.

---

## Asset Compartilhado

Recurso reutilizado por toda a plataforma.

Normalmente localizado na estrutura global de `static/`.

---

## Asset Específico

Recurso utilizado exclusivamente por um determinado módulo.

Permanece próximo ao domínio correspondente.

---

## CSS

Folha de estilos responsável pela apresentação visual da interface.

---

## JavaScript

Scripts responsáveis pelo comportamento dinâmico da interface.

---

## Font Awesome

Biblioteca oficial de ícones do GereIgreja.

Utilizada amplamente em menus, dashboards, formulários e componentes.

---

## Bootstrap

Framework CSS adotado como base da responsividade da plataforma.

---

## HTMX

Tecnologia oficialmente prevista para modernização gradual das interações entre Frontend e Backend.

No estado atual do projeto sua adoção é parcial.

---

## Alpine.js

Biblioteca destinada às interações leves da interface.

Também se encontra em adoção gradual.

---

## CDN

(Content Delivery Network)

Infraestrutura utilizada para distribuição de bibliotecas externas.

Atualmente o GereIgreja utiliza CDNs para parte das bibliotecas de terceiros.

---

## Local Storage

Mecanismo utilizado pelo navegador para armazenamento local.

Exemplo identificado:

Persistência do estado da Sidebar dos Dashboards.

---

# 18. Roadmap

A arquitetura de Assets foi projetada para evoluir continuamente sem comprometer a compatibilidade da plataforma.

---

## Curto Prazo

- Consolidação da organização atual;
- Revisão periódica dos Assets não utilizados;
- Padronização completa da nomenclatura;
- Expansão do inventário técnico.

---

## Médio Prazo

- Redução gradual de dependências externas;
- Melhor organização dos Assets específicos por módulo;
- Otimização das imagens institucionais;
- Evolução da modularização dos arquivos JavaScript.

---

## Longo Prazo

- Pipeline automatizado de otimização de Assets;
- Versionamento de recursos estáticos;
- Suporte ampliado a Progressive Web App (PWA);
- Estratégias avançadas de cache;
- Compressão automática de imagens;
- Otimização para Core Web Vitals.

Toda evolução deverá preservar a arquitetura oficial definida neste documento.

---

# 19. Documentos Relacionados

## GereIgreja Frontend Engineering

- README.md
- GFE-01 — Frontend Architecture
- GFE-02 — Estrutura de Pastas
- GFE-03 — Componentes
- GFE-04 — Layouts
- GFE-05 — Templates
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

Os Assets constituem a infraestrutura estática do Frontend do GereIgreja e desempenham papel fundamental na experiência do usuário, na identidade visual e no desempenho da plataforma.

A organização adotada privilegia recursos compartilhados, mantendo Assets específicos apenas quando realmente pertencem a um domínio funcional.

A utilização consistente da pasta `static`, do mecanismo `{% static %}` do Django, da separação entre recursos globais e específicos e da padronização das bibliotecas garante uma arquitetura previsível, escalável e de fácil manutenção.

Toda evolução futura deverá respeitar os princípios estabelecidos neste documento, preservando compatibilidade com os Layouts, Templates, Componentes e com o Design System oficial do GereIgreja.

---

# Status do Documento

**Pasta**

```
docs/frontend/
```

**Arquivo**

```
06-Assets.md
```

**Código**

```
GFE-AST
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

