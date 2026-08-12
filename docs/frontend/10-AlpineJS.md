Pasta:
docs/frontend/

Arquivo:
10-AlpineJS.md

Documento:
GFE-10

Código:
GFE-ALPINE

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

# GFE-10 — Arquitetura Alpine.js

> *"O Alpine.js representa a camada oficial de comportamento declarativo do GereIgreja, sendo utilizado para interações leves da interface, preservando a filosofia Server Side Rendering (SSR) adotada pela plataforma."*

---

# Sumário

1. Objetivo
2. Escopo
3. Visão Estratégica
4. Filosofia Arquitetural
5. Estado Atual da Plataforma
6. Estado Futuro Desejado
7. Papel do Alpine.js
8. Integração com Django
9. Integração com Templates
10. Integração com HTMX
11. Integração com JavaScript
12. Princípios Arquiteturais
13. Casos Oficiais de Uso
14. Quando NÃO utilizar Alpine.js
15. Roadmap de Adoção
16. Evidências Arquiteturais
17. Especificações Oficiais
18. Boas Práticas
19. Anti-patterns
20. Checklist
21. Glossário
22. Documentos Relacionados

---

# 1. Objetivo

Este documento estabelece oficialmente a arquitetura de utilização do Alpine.js no Frontend do GereIgreja.

Seu objetivo é padronizar comportamentos locais da interface, reduzindo JavaScript imperativo e mantendo a simplicidade arquitetural da plataforma.

O Alpine.js deverá complementar o Django e o HTMX, nunca substituí-los.

---

# 2. Escopo

Aplica-se exclusivamente à Área de Gestão do GereIgreja.

Inclui:

- Dashboards;
- Formulários;
- Menus;
- Dropdowns;
- Abas;
- Modais;
- Componentes reutilizáveis;
- Cards;
- Widgets.

Não inclui:

- Administração Técnica (Django Admin);
- Backend;
- APIs;
- Regras de negócio.

---

# 3. Visão Estratégica

O Alpine.js foi escolhido como biblioteca oficial para interações leves da interface.

Sua adoção permite eliminar JavaScript repetitivo para comportamentos simples, mantendo integração natural com Django Templates.

Essa estratégia reduz complexidade, facilita manutenção e melhora a legibilidade dos Templates.

---

# 4. Filosofia Arquitetural

O Alpine.js deverá ser utilizado apenas para estados locais da interface.

Não deverá:

- executar regras de negócio;
- realizar validações de domínio;
- substituir Views Django;
- controlar navegação da aplicação.

Sua responsabilidade limita-se ao comportamento visual do componente.

---

# 5. Estado Atual da Plataforma

Durante a análise do projeto foi identificado que:

- Alpine.js já consta como diretriz oficial da arquitetura Frontend;
- sua adoção está prevista nos documentos GFE;
- até o momento não foram encontrados atributos como:

```
x-data
x-show
x-bind
x-model
x-on
```

nos Templates analisados.

Isso demonstra que a plataforma encontra-se preparada para sua adoção gradual.

---

# 6. Estado Futuro Desejado

No estado futuro, Alpine.js deverá controlar apenas estados locais da interface.

Exemplos:

- abrir e fechar menus;
- dropdowns;
- accordions;
- tabs;
- modais;
- painéis recolhíveis;
- filtros visuais;
- alternância de temas;
- exibição condicional de elementos.

Sem substituir JavaScript compartilhado quando este oferecer melhor reutilização.

---

# 7. Papel do Alpine.js

Arquitetura conceitual:

```
Usuário

↓

Template Django

↓

Alpine.js

↓

Atualização Local

↓

DOM
```

Não existe comunicação obrigatória com o servidor.

Toda alteração permanece restrita ao navegador.

---

# 8. Integração com Django

O Alpine.js deverá ser utilizado diretamente nos Templates Django.

A renderização do HTML continuará sendo responsabilidade do servidor.

O estado inicial do componente poderá ser definido através do contexto enviado pela View.

---

# 9. Integração com Templates

Os Templates continuam sendo a principal camada estrutural.

O Alpine.js poderá ser utilizado em:

- Components;
- Partials;
- Includes;
- Templates específicos.

Sempre preservando legibilidade e baixo acoplamento.

---

# 10. Integração com HTMX

HTMX e Alpine.js possuem responsabilidades complementares.

HTMX deverá comunicar-se com o servidor.

Alpine.js deverá controlar estados locais.

Exemplo:

HTMX

```
Atualizar tabela.
```

Alpine.js

```
Abrir painel de filtros.
```

Essa separação reduz sobreposição de tecnologias e facilita manutenção.

---

# 11. Integração com JavaScript

JavaScript compartilhado continuará responsável por:

- gráficos;
- infraestrutura;
- integrações externas;
- Local Storage;
- componentes reutilizáveis complexos.

Alpine.js deverá assumir apenas comportamentos leves.

Sempre que um comportamento crescer em complexidade, sua migração para JavaScript compartilhado deverá ser considerada.

---

# 12. Princípios Arquiteturais

Toda implementação Alpine.js deverá respeitar os seguintes princípios.

## Simplicidade

Cada componente deverá possuir comportamento simples e previsível.

---

## Responsabilidade Única

Cada bloco `x-data` deverá controlar apenas um componente.

---

## Reutilização

Sempre reutilizar Templates e Components existentes.

---

## Legibilidade

Evitar grandes blocos de lógica diretamente no HTML.

---

## Compatibilidade

Toda implementação deverá permanecer compatível com:

- Django Templates;
- Bootstrap;
- HTMX;
- JavaScript compartilhado;
- Design System.

---

# 13. Casos Oficiais de Uso

O Alpine.js deverá ser utilizado exclusivamente para controlar estados locais da interface.

Seu uso deve tornar o código mais simples, mais legível e mais reutilizável.

---

## 13.1 Dropdowns

O Alpine.js é a tecnologia oficial para controle de menus suspensos.

Exemplos:

- menu do usuário;
- ações rápidas;
- filtros;
- menus contextuais.

Fluxo:

```
Clique

↓

Alpine.js

↓

Abrir / Fechar

↓

Atualização Local
```

Nenhuma comunicação com o servidor será necessária.

---

## 13.2 Accordions

Painéis expansíveis deverão utilizar Alpine.js.

Exemplos:

- perguntas frequentes;
- detalhes financeiros;
- histórico;
- observações.

O estado expandido permanece apenas no navegador.

---

## 13.3 Abas (Tabs)

As abas representam um dos principais casos de uso.

Exemplos:

- Cadastro
- Histórico
- Financeiro
- Documentos
- Estatísticas

A mudança entre abas não deverá gerar requisições ao servidor quando todo o conteúdo já estiver disponível.

---

## 13.4 Modais

O Alpine.js poderá controlar:

- abertura;
- fechamento;
- animações;
- foco inicial;
- retorno do foco.

Caso o conteúdo precise ser carregado dinamicamente, o HTMX deverá realizar a requisição.

---

## 13.5 Menus

Menus laterais e menus secundários poderão utilizar Alpine.js.

Exemplos:

- expandir categorias;
- recolher grupos;
- destacar item ativo;
- alternar painéis.

---

## 13.6 Painéis Colapsáveis

Exemplos:

```
Filtros

↓

Mostrar / Ocultar
```

```
Resumo Financeiro

↓

Expandir
```

---

## 13.7 Alternância Visual

Alpine.js poderá controlar:

- exibir/ocultar senha;
- troca de ícones;
- alternância de temas;
- mostrar mais/menos;
- visualização compacta.

---

## 13.8 Componentes Reutilizáveis

Sempre que um componente reutilizável possuir estado local simples, Alpine.js deverá ser considerado.

Exemplos:

- Cards;
- Alertas;
- Toasts;
- Dropdowns;
- Abas;
- Painéis.

---

## 13.9 Dashboards

Nos Dashboards Premium, Alpine.js deverá controlar apenas estados locais.

Exemplos:

- abrir painel lateral;
- esconder filtros;
- alternar widgets;
- expandir gráficos.

A atualização dos dados continuará sendo responsabilidade do HTMX ou JavaScript compartilhado.

---

## 13.10 Formulários

Alpine.js poderá controlar:

- mostrar campos opcionais;
- exibir ajuda contextual;
- trocar etapas;
- validações visuais simples;
- contadores de caracteres.

As validações oficiais continuam sendo responsabilidade do Django.

---

# 14. Quando NÃO Utilizar Alpine.js

Nem todo comportamento deve utilizar Alpine.js.

Os cenários abaixo permanecem responsabilidade de outras camadas.

---

## 14.1 Comunicação com o Servidor

Toda comunicação deverá utilizar:

- Django;
- HTMX;
- JavaScript compartilhado.

Nunca Alpine.js.

---

## 14.2 Regras de Negócio

Exemplos:

- cálculo financeiro;
- permissões;
- autenticação;
- validações oficiais;
- geração de documentos.

Continuam pertencendo ao Backend.

---

## 14.3 Componentes Complexos

Exemplos:

- gráficos;
- mapas;
- calendários;
- upload avançado;
- editores ricos.

Esses componentes deverão permanecer em JavaScript dedicado.

---

## 14.4 Infraestrutura Compartilhada

Scripts como:

```
dashboard-sidebar.js
```

continuam pertencendo à infraestrutura JavaScript da plataforma.

---

## 14.5 Estados Compartilhados

Quando múltiplos componentes precisarem compartilhar estado, avaliar JavaScript compartilhado em vez de Alpine.js.

---

# 15. Roadmap de Adoção

A evolução ocorrerá progressivamente.

---

## Fase 1

Documentação.

Status:

Concluída.

---

## Fase 2

Primeiros componentes.

Prioridade:

- Dropdowns;
- Accordions;
- Tabs;
- Painéis.

---

## Fase 3

Expansão.

Aplicação em:

- Formulários;
- Dashboards;
- Widgets;
- Cards.

---

## Fase 4

Consolidação.

Todos os novos componentes leves deverão considerar Alpine.js como primeira opção.

---

## Fase 5

Otimização.

Redução de JavaScript repetitivo.

Maior reutilização.

Maior legibilidade.

---

# 16. Evidências Arquiteturais

Este documento foi elaborado considerando a arquitetura atual do GereIgreja.

---

## EA-ALPINE-001

Documentação oficial.

Os documentos GFE já estabelecem Alpine.js como tecnologia oficial para comportamentos leves.

---

## EA-ALPINE-002

Estado atual.

Durante a análise não foram encontrados atributos:

```
x-data

x-show

x-bind

x-model

x-on
```

nos Templates.

---

## EA-ALPINE-003

Arquitetura.

A organização baseada em:

- Templates;
- Includes;
- Partials;
- Componentes.

favorece adoção gradual.

---

## EA-ALPINE-004

Compatibilidade.

Toda estrutura existente permanece compatível com Alpine.js.

Não será necessária refatoração dos Layouts Base.

---

## EA-ALPINE-005

Integração.

Alpine.js deverá coexistir com:

- HTMX;
- Bootstrap;
- JavaScript compartilhado.

Sem substituir nenhuma dessas tecnologias.

---

# 17. Especificações Oficiais

## GFE-ALPINE-001

Utilizar Alpine.js apenas para estados locais.

---

## GFE-ALPINE-002

Não implementar regras de negócio.

---

## GFE-ALPINE-003

Cada componente deverá possuir responsabilidade única.

---

## GFE-ALPINE-004

Evitar lógica extensa dentro de `x-data`.

---

## GFE-ALPINE-005

Sempre reutilizar componentes existentes.

---

## GFE-ALPINE-006

Priorizar legibilidade dos Templates.

---

## GFE-ALPINE-007

Toda implementação deverá permanecer compatível com HTMX.

---

## GFE-ALPINE-008

Toda implementação deverá respeitar o Design System.

---

# 18. Boas Práticas

Durante o desenvolvimento recomenda-se:

- utilizar Alpine.js apenas para estados locais;
- manter componentes pequenos e independentes;
- utilizar um único `x-data` por responsabilidade;
- preferir propriedades simples e intuitivas;
- manter a lógica declarativa;
- reutilizar Components, Partials e Includes;
- documentar novos padrões;
- preservar compatibilidade com HTMX;
- preservar compatibilidade com Bootstrap;
- preservar compatibilidade com JavaScript compartilhado;
- manter o HTML legível.

---

# 19. Anti-patterns

Os padrões abaixo não fazem parte da arquitetura oficial.

---

## 19.1 Substituir JavaScript Compartilhado

Alpine.js não deverá substituir scripts de infraestrutura da plataforma.

Exemplo:

```
dashboard-sidebar.js
```

permanece responsabilidade da camada JavaScript.

---

## 19.2 Executar Regras de Negócio

Toda regra de negócio continua pertencendo ao Backend.

---

## 19.3 Componentes Gigantes

Evitar grandes blocos `x-data`.

Preferir múltiplos componentes pequenos.

---

## 19.4 Comunicação com Backend

Alpine.js não deverá realizar comunicação direta com o servidor quando HTMX oferecer solução mais adequada.

---

## 19.5 Duplicação de Estado

Evitar controlar o mesmo estado simultaneamente por:

- Alpine.js;
- JavaScript compartilhado;
- HTMX.

Cada responsabilidade deverá possuir apenas uma fonte de verdade.

---

## 19.6 HTML Poluído

Evitar excesso de:

```
x-show

x-bind

x-if

x-for

x-on

x-transition
```

em um único elemento.

---

## 19.7 Acoplamento Excessivo

Componentes Alpine.js não deverão depender da estrutura interna de outros componentes.

---

# 20. Matriz Oficial de Decisão

A tabela abaixo estabelece oficialmente qual tecnologia deverá ser utilizada em cada cenário do Frontend.

| Situação | Tecnologia Oficial |
|-----------|--------------------|
| Renderizar HTML | Django Templates |
| Regra de negócio | Django |
| Banco de dados | Django ORM |
| Atualização parcial da página | HTMX |
| Abrir dropdown | Alpine.js |
| Abrir modal | Alpine.js |
| Mostrar/Ocultar elemento | Alpine.js |
| Alternar abas | Alpine.js |
| Expandir painel | Alpine.js |
| Persistência Local | JavaScript |
| Local Storage | JavaScript |
| Gráficos | JavaScript |
| Bibliotecas externas | JavaScript |
| Dashboard Sidebar | JavaScript Compartilhado |
| Renderização inicial | Django |
| Formulários | Django + HTMX (quando aplicável) |
| Componentes reutilizáveis | Alpine.js |
| Dashboards | HTMX + JavaScript + Alpine.js |

---

## Fluxo Arquitetural Oficial

```
Django
│
├── Renderiza HTML
│
├── Executa regras de negócio
│
├── ORM
│
└── Templates
        │
        ├── HTMX
        │       │
        │       └── Comunicação com o servidor
        │
        ├── Alpine.js
        │       │
        │       └── Estado local da interface
        │
        └── JavaScript
                │
                ├── Infraestrutura
                ├── Bibliotecas
                ├── Dashboard
                └── Recursos avançados
```

Esta arquitetura constitui o padrão oficial do Frontend do GereIgreja.

---

# 21. Checklist

Antes de utilizar Alpine.js verificar:

## Arquitetura

- [ ] O comportamento é apenas local?
- [ ] Existe necessidade de Alpine.js?
- [ ] HTMX seria mais adequado?

---

## Simplicidade

- [ ] O componente permanece pequeno?
- [ ] O Template continua legível?

---

## Integração

- [ ] Compatível com Django?
- [ ] Compatível com HTMX?
- [ ] Compatível com Bootstrap?

---

## Reutilização

- [ ] O componente poderá ser reutilizado?
- [ ] Existe implementação semelhante?

---

## Documentação

- [ ] Segue o GFE?
- [ ] Segue o Design System?
- [ ] Segue os padrões oficiais?

---

# 22. Glossário

## Alpine.js

Biblioteca declarativa destinada ao controle de estados locais da interface.

---

## Estado Local

Informação utilizada exclusivamente por um componente visual.

Exemplos:

- aberto;
- fechado;
- ativo;
- selecionado.

---

## x-data

Diretiva responsável por inicializar um componente Alpine.js.

---

## x-show

Diretiva utilizada para exibir ou ocultar elementos.

---

## x-bind

Permite vincular atributos HTML ao estado do componente.

---

## x-on

Diretiva responsável por registrar eventos.

---

## Progressive Enhancement

Estratégia de evolução adotada pelo GereIgreja.

Novos recursos são adicionados sem comprometer a renderização tradicional do Django.

---

# 23. Governança da Arquitetura Alpine.js

Toda implementação deverá seguir os princípios abaixo.

- Alpine.js possui responsabilidade limitada.
- Não substituir JavaScript compartilhado.
- Não substituir HTMX.
- Não substituir Django.
- Toda nova convenção deverá ser documentada.
- A simplicidade sempre terá prioridade sobre soluções sofisticadas.

A governança garante consistência arquitetural e reduz o custo de manutenção da plataforma.

---

# 24. Documentos Relacionados

## GereIgreja Frontend Engineering

- README.md
- GFE-01 — Frontend Architecture
- GFE-02 — Estrutura de Pastas
- GFE-03 — Componentes
- GFE-04 — Layouts
- GFE-05 — Templates
- GFE-06 — Assets
- GFE-07 — CSS
- GFE-08 — JavaScript
- GFE-09 — HTMX
- GFE-11 — Dashboards

---

## Documentação Corporativa

- GereIgreja Design System (GDS)
- GereIgreja Documentation Framework (GDF)
- GereIgreja Quality Framework (GQF)

---

# Conclusão

O Alpine.js estabelece a camada oficial de comportamento declarativo do Frontend do GereIgreja.

Sua função é controlar exclusivamente estados locais da interface, mantendo a arquitetura baseada em Django Templates, Renderização no Servidor (SSR) e Progressive Enhancement.

A combinação entre Django, HTMX, Alpine.js e JavaScript compartilhado cria uma arquitetura moderna, organizada e sustentável, onde cada tecnologia possui responsabilidades claramente definidas.

Toda implementação futura deverá respeitar os princípios definidos neste documento, preservando simplicidade, reutilização, baixo acoplamento e compatibilidade com o Design System oficial da plataforma.

---

# Status do Documento

**Pasta**

```
docs/frontend/
```

**Arquivo**

```
10-AlpineJS.md
```

**Código**

```
GFE-ALPINE
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

