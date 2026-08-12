Pasta:
docs/design-system/

Arquivo:
07-Iconografia.md

Documento:
GDS-07

Código:
GDS-ICON

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

# GDS-07 — Iconografia

> *"Os ícones do GereIgreja devem comunicar ações, estados e funcionalidades de forma imediata, reforçando a usabilidade da plataforma sem competir com o conteúdo textual."*

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia da Iconografia
4. Princípios
5. Biblioteca Oficial
6. Identidade Visual
7. Tamanhos Oficiais
8. Espaçamento
9. Cores
10. Estados
11. Ícones Oficiais do GereIgreja
12. Relação com os Demais Frameworks

---

# 1. Objetivo

Este documento define oficialmente a arquitetura de iconografia utilizada em toda a plataforma GereIgreja.

Seu objetivo é padronizar o uso de ícones em todos os módulos, garantindo:

- consistência visual;
- reconhecimento imediato;
- excelente usabilidade;
- acessibilidade;
- facilidade de manutenção;
- reutilização de componentes.

Todo ícone utilizado na plataforma deverá seguir os padrões definidos neste documento.

---

# 2. Escopo

Este documento aplica-se a:

- Área de Gestão;
- Portal Público;
- Landing Pages;
- Dashboards;
- Formulários;
- Tabelas;
- Menus;
- Modais;
- Alertas;
- Relatórios;
- Componentes reutilizáveis.

---

# 3. Filosofia da Iconografia

Os ícones possuem função complementar.

Eles ajudam o usuário a localizar rapidamente ações e informações importantes.

Os ícones não substituem textos quando estes forem necessários para compreensão.

Toda iconografia deverá:

- reduzir esforço cognitivo;
- facilitar navegação;
- aumentar produtividade;
- manter identidade visual consistente.

---

# 4. Princípios

Toda utilização de ícones deverá respeitar:

- simplicidade;
- consistência;
- clareza;
- previsibilidade;
- acessibilidade;
- reutilização.

Evitar ícones meramente decorativos.

Cada ícone deverá possuir significado claro.

---

# 5. Biblioteca Oficial

O GereIgreja adota oficialmente:

# Bootstrap Icons

Como biblioteca principal.

Benefícios:

- excelente integração com Bootstrap;
- ampla cobertura de ícones;
- leveza;
- manutenção ativa;
- licença permissiva;
- excelente renderização.

Não deverão ser misturadas bibliotecas diferentes na mesma interface.

---

# 6. Identidade Visual

Os ícones fazem parte da identidade visual da plataforma.

Características desejadas:

- traços limpos;
- espessura uniforme;
- aparência moderna;
- excelente legibilidade;
- equilíbrio visual.

Os ícones deverão harmonizar com a tipografia e os componentes do Design System.

---

# 7. Tamanhos Oficiais

Escala oficial.

| Uso | Tamanho |
|------|---------:|
| XS | 12 px |
| Small | 16 px |
| Normal | 20 px |
| Medium | 24 px |
| Large | 32 px |
| XL | 48 px |

Toda interface deverá utilizar exclusivamente essa escala.

---

## Recomendações

Menus

16 px

Botões

16 ou 20 px

Breadcrumb

16 px

Cards

20 px

KPIs

24 px

Painéis

24 px

Ilustrações

32 ou 48 px

---

# 8. Espaçamento

Todo ícone deverá manter distância consistente do texto.

Recomendação:

Ícone

↓

Space-2

↓

Texto

Nunca posicionar ícones encostados ao conteúdo textual.

---

## Botões

Estrutura:

```
[ícone] Space-2 Texto
```

---

## Menus

Estrutura:

```
Ícone

Space-3

Texto
```

---

## Breadcrumb

Estrutura:

```
Ícone

Space-2

Texto
```

---

# 9. Cores

Os ícones deverão utilizar exclusivamente as cores oficiais do Design System.

---

## Primário

Brand 700

---

## Texto

Text

---

## Secundário

Text Muted

---

## Sucesso

Success

---

## Atenção

Warning

---

## Erro

Danger

---

## Informação

Info

---

Evitar cores arbitrárias.

---

# 10. Estados

Todo ícone interativo deverá possuir estados visuais.

---

Normal

Estado padrão.

---

Hover

Pequena alteração de cor.

---

Active

Destaque visual.

---

Focus

Compatível com navegação por teclado.

---

Disabled

Utilizar Text Muted.

Não alterar opacidade excessivamente.

---

# 11. Ícones Oficiais do GereIgreja

A seguir estão os ícones recomendados para os principais módulos.

| Módulo | Ícone Bootstrap |
|---------|----------------|
| Dashboard | bi-speedometer2 |
| Membros | bi-people |
| Congregações | bi-building |
| Ministérios | bi-diagram-3 |
| Departamentos | bi-diagram-2 |
| Financeiro | bi-cash-stack |
| Patrimônio | bi-box-seam |
| Eventos | bi-calendar-event |
| Comunicação | bi-megaphone |
| Escola Bíblica | bi-book |
| Agenda Pastoral | bi-calendar-week |
| Visitantes | bi-person-heart |
| Batismos | bi-droplet |
| Santa Ceia | bi-cup-hot |
| Relatórios | bi-file-earmark-bar-graph |
| Configurações | bi-gear |
| Perfil | bi-person-circle |
| Usuários | bi-person-badge |
| Segurança | bi-shield-lock |
| Auditoria | bi-clipboard-data |
| Backup | bi-cloud-arrow-up |
| Logs | bi-journal-code |

Esses ícones deverão ser reutilizados por toda a plataforma.

---

# 12. Relação com os Demais Frameworks

Este documento integra-se diretamente com:

- GDS-03 — Cores
- GDS-04 — Tipografia
- GDS-05 — Espaçamento
- GDS-06 — Grid
- GFE — Frontend Engineering

Toda implementação deverá permanecer compatível com os componentes oficiais do GereIgreja.

---
# 13. Iconografia em Botões

Os botões representam uma das principais áreas de interação do GereIgreja.

Os ícones deverão facilitar o reconhecimento imediato da ação executada.

---

## Estrutura

```
[ Ícone ] Space-2 Texto
```

O alinhamento deverá ser sempre centralizado verticalmente.

---

## Botões Primários

Utilizar ícones para ações principais.

Exemplos:

| Ação | Ícone |
|------|--------|
| Salvar | bi-floppy |
| Criar | bi-plus-circle |
| Confirmar | bi-check-circle |
| Enviar | bi-send |
| Finalizar | bi-check2-square |

---

## Botões Secundários

| Ação | Ícone |
|------|--------|
| Editar | bi-pencil-square |
| Visualizar | bi-eye |
| Imprimir | bi-printer |
| Exportar | bi-download |
| Compartilhar | bi-share |

---

## Botões de Perigo

| Ação | Ícone |
|------|--------|
| Excluir | bi-trash |
| Cancelar | bi-x-circle |
| Remover | bi-dash-circle |

Utilizar sempre a cor semântica Danger.

---

# 14. Iconografia em Menus

Toda navegação deverá utilizar ícones padronizados.

Estrutura recomendada:

```
Ícone

↓

Space-3

↓

Texto
```

---

## Sidebar da Área de Gestão

| Menu | Ícone |
|------|--------|
| Dashboard | bi-speedometer2 |
| Secretaria | bi-person-lines-fill |
| Membros | bi-people |
| Congregações | bi-building |
| Ministérios | bi-diagram-3 |
| Financeiro | bi-cash-stack |
| Patrimônio | bi-box-seam |
| Escola Bíblica | bi-book |
| Eventos | bi-calendar-event |
| Comunicação | bi-megaphone |
| Relatórios | bi-file-earmark-bar-graph |
| Configurações | bi-gear |

Todos os módulos deverão reutilizar esta nomenclatura.

---

# 15. Iconografia em Dashboards

Os dashboards utilizam ícones para reforçar KPIs e facilitar a leitura.

---

## Indicadores

Exemplos:

Membros

```
bi-people
```

Receitas

```
bi-cash-stack
```

Eventos

```
bi-calendar-event
```

Visitantes

```
bi-person-heart
```

Batismos

```
bi-droplet
```

---

## Cards

Estrutura:

```
Ícone

↓

Título

↓

Valor

↓

Descrição
```

Ícones não deverão competir visualmente com o indicador principal.

---

# 16. Iconografia em Formulários

Os ícones possuem função auxiliar.

Exemplos:

Pesquisar

```
bi-search
```

Calendário

```
bi-calendar3
```

Telefone

```
bi-telephone
```

E-mail

```
bi-envelope
```

Endereço

```
bi-geo-alt
```

Documento

```
bi-file-earmark-text
```

Evitar excesso de ícones nos formulários.

---

# 17. Iconografia em Tabelas

As tabelas deverão utilizar ícones exclusivamente para ações.

---

## Ações Individuais

Editar

```
bi-pencil
```

Visualizar

```
bi-eye
```

Excluir

```
bi-trash
```

Duplicar

```
bi-files
```

Histórico

```
bi-clock-history
```

---

## Status

Ativo

```
bi-check-circle-fill
```

Inativo

```
bi-slash-circle
```

Pendente

```
bi-hourglass-split
```

Cancelado

```
bi-x-circle
```

---

# 18. Iconografia em Alertas

Cada tipo de alerta deverá possuir um ícone padronizado.

| Tipo | Ícone |
|------|--------|
| Success | bi-check-circle-fill |
| Warning | bi-exclamation-triangle-fill |
| Danger | bi-x-octagon-fill |
| Info | bi-info-circle-fill |

Nunca utilizar ícones diferentes para o mesmo tipo de alerta.

---

# 19. Iconografia em Modais

Todo modal deverá possuir um ícone representando sua finalidade.

Exemplos:

Confirmação

```
bi-question-circle
```

Informação

```
bi-info-circle
```

Erro

```
bi-x-octagon
```

Sucesso

```
bi-check-circle
```

Configuração

```
bi-sliders
```

---

# 20. Responsividade

Os ícones deverão adaptar-se automaticamente ao dispositivo.

Desktop

20–24 px

Notebook

20 px

Tablet

20 px

Smartphone

16–20 px

Evitar ícones muito pequenos em dispositivos móveis.

---

# 21. Acessibilidade

Os ícones deverão seguir boas práticas de acessibilidade.

---

## Ícones Decorativos

Quando o ícone possuir apenas função estética:

```html
aria-hidden="true"
```

---

## Ícones Funcionais

Botões compostos apenas por ícones deverão possuir descrição acessível.

Exemplo:

```html
aria-label="Editar membro"
```

---

## Contraste

Os ícones deverão respeitar o contraste mínimo definido pelo GDS.

---

## Área de Clique

Botões compostos apenas por ícones deverão possuir área mínima aproximada de 44 × 44 px para facilitar interação em dispositivos móveis.

---

# 22. Evidências Arquiteturais

As diretrizes deste documento refletem a implementação oficial do GereIgreja.

---

## EA-GDS-036

Bootstrap Icons constitui a biblioteca oficial de iconografia.

---

## EA-GDS-037

Todos os módulos reutilizam a mesma biblioteca de ícones.

---

## EA-GDS-038

Os estados visuais seguem as cores semânticas do Design System.

---

## EA-GDS-039

A arquitetura evita múltiplas bibliotecas de ícones.

---

## EA-GDS-040

Os componentes reutilizam nomenclatura consistente em toda a plataforma.

---

# 23. Especificações Oficiais

## GDS-ICON-001

Utilizar exclusivamente Bootstrap Icons.

---

## GDS-ICON-002

Não misturar bibliotecas diferentes.

---

## GDS-ICON-003

Todo ícone funcional deverá possuir significado claro.

---

## GDS-ICON-004

Ícones deverão respeitar os tamanhos oficiais.

---

## GDS-ICON-005

Os estados deverão seguir o Design System.

---

## GDS-ICON-006

Ações equivalentes deverão utilizar o mesmo ícone.

---

## GDS-ICON-007

Ícones decorativos deverão ser ocultados das tecnologias assistivas.

---

## GDS-ICON-008

Botões compostos apenas por ícones deverão possuir `aria-label`.

---

## GDS-ICON-009

Novos ícones deverão ser documentados antes de sua utilização.

---

## GDS-ICON-010

Toda evolução deverá preservar a consistência da plataforma.

---

# 24. Boas Práticas

A iconografia oficial do GereIgreja deve atuar como um complemento visual à interface, tornando a navegação mais intuitiva sem substituir a informação textual.

---

## Utilizar Sempre a Biblioteca Oficial

Toda a plataforma deverá utilizar exclusivamente:

```
Bootstrap Icons
```

Isso garante:

- consistência visual;
- menor tamanho da aplicação;
- facilidade de manutenção;
- identidade única.

---

## Reutilizar os Mesmos Ícones

Uma mesma ação deverá utilizar sempre o mesmo ícone.

Exemplos:

Editar

```
bi-pencil-square
```

Excluir

```
bi-trash
```

Visualizar

```
bi-eye
```

Salvar

```
bi-floppy
```

Pesquisar

```
bi-search
```

O usuário deve reconhecer imediatamente cada ação.

---

## Priorizar Clareza

Os ícones deverão representar ações universalmente reconhecidas.

Evitar símbolos ambíguos.

---

## Utilizar Texto Sempre que Necessário

Ícones não substituem textos.

Exemplo recomendado:

```
💾 Salvar
```

Em vez de apenas:

```
💾
```

Exceto em ações muito conhecidas ou quando houver `tooltip` e `aria-label`.

---

## Manter Consistência de Tamanho

Dentro do mesmo contexto todos os ícones deverão possuir dimensões equivalentes.

Exemplo:

Menu lateral

```
16 px
```

Dashboard

```
24 px
```

Botões

```
16 ou 20 px
```

---

## Utilizar Espaçamento Adequado

Todo ícone deverá respeitar o padrão definido em:

```
GDS-05 — Espaçamento
```

---

# 25. Anti-patterns

Os padrões abaixo não fazem parte da arquitetura oficial do GereIgreja.

---

## 25.1 Misturar Bibliotecas

Não utilizar simultaneamente:

- Bootstrap Icons;
- Font Awesome;
- Heroicons;
- Material Icons;
- Feather Icons.

A plataforma deverá possuir uma única linguagem visual.

---

## 25.2 Mesmo Ícone para Ações Diferentes

Evitar utilizar um mesmo ícone para representar ações distintas.

Exemplo inadequado:

```
bi-pencil
```

Editar

↓

Configurações

↓

Permissões

Cada ação deverá possuir representação própria.

---

## 25.3 Ícones Decorativos em Excesso

Não adicionar ícones apenas para preencher espaço.

Todo ícone deverá possuir função clara.

---

## 25.4 Ícones Muito Pequenos

Evitar:

12 px

em botões ou menus principais.

A legibilidade deverá ser preservada.

---

## 25.5 Cores Arbitrárias

Não alterar manualmente as cores dos ícones.

Utilizar exclusivamente os tokens do Design System.

---

## 25.6 Falta de Acessibilidade

Botões compostos apenas por ícones não poderão existir sem descrição acessível.

Sempre utilizar:

```html
aria-label=""
```

quando necessário.

---

# 26. Checklist

Antes da publicação de qualquer interface verificar.

---

## Biblioteca

- [ ] utiliza Bootstrap Icons?
- [ ] evita bibliotecas paralelas?

---

## Consistência

- [ ] ações equivalentes utilizam o mesmo ícone?
- [ ] tamanhos seguem a escala oficial?
- [ ] cores seguem o GDS?

---

## Componentes

- [ ] menus padronizados?
- [ ] botões padronizados?
- [ ] dashboards padronizados?
- [ ] tabelas padronizadas?
- [ ] formulários padronizados?

---

## Acessibilidade

- [ ] `aria-hidden` aplicado quando necessário?
- [ ] `aria-label` aplicado em botões somente com ícones?
- [ ] contraste adequado?

---

## Documentação

- [ ] novos ícones documentados?
- [ ] nomenclatura atualizada?
- [ ] Design System atualizado?

---

# 27. Glossário

## Ícone

Elemento gráfico utilizado para representar visualmente uma ação, estado ou funcionalidade.

---

## Biblioteca de Ícones

Conjunto padronizado de ícones reutilizáveis.

No GereIgreja:

```
Bootstrap Icons
```

---

## Ícone Decorativo

Ícone utilizado apenas para reforço visual.

Não transmite informação essencial.

---

## Ícone Funcional

Ícone utilizado em ações do sistema.

Exemplo:

Editar

Excluir

Salvar

Pesquisar

---

## Tooltip

Mensagem exibida ao posicionar o cursor sobre um elemento.

---

## aria-label

Descrição textual utilizada por tecnologias assistivas.

---

# 28. Governança

Toda evolução da iconografia deverá preservar a identidade visual do GereIgreja.

---

## Documentação

Novos ícones deverão ser registrados antes de serem utilizados.

---

## Compatibilidade

A biblioteca oficial deverá permanecer compatível com:

- Bootstrap;
- Design System;
- Frontend Engineering;
- Componentes reutilizáveis.

---

## Padronização

Os mesmos ícones deverão ser reutilizados em toda a plataforma.

---

## Evolução

Novas funcionalidades deverão utilizar a arquitetura existente antes de propor novos padrões.

---

# 29. Roadmap

## Curto Prazo

- consolidação da biblioteca oficial;
- padronização completa dos módulos;
- eliminação de inconsistências.

---

## Médio Prazo

- catálogo visual oficial de ícones;
- biblioteca reutilizável por componente;
- documentação ilustrada.

---

## Longo Prazo

- suporte a temas claros e escuros;
- otimizações para PWA;
- adaptação para aplicações móveis;
- sincronização automática com futuras versões do Bootstrap Icons.

---

# 30. Documentos Relacionados

## GereIgreja Design System

- README.md
- GDS-01 — Introdução
- GDS-02 — Princípios
- GDS-03 — Cores
- GDS-04 — Tipografia
- GDS-05 — Espaçamento
- GDS-06 — Grid
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

A iconografia oficial do GereIgreja representa um elemento essencial da experiência do usuário, permitindo reconhecer ações, estados e funcionalidades de forma rápida e intuitiva.

Ao adotar exclusivamente o Bootstrap Icons e estabelecer regras claras para tamanhos, cores, espaçamentos, estados e acessibilidade, a plataforma garante uma identidade visual consistente, reduz a curva de aprendizado dos usuários e facilita a manutenção e evolução dos componentes.

Toda nova funcionalidade deverá reutilizar os padrões estabelecidos neste documento, preservando a uniformidade da interface em todos os módulos do GereIgreja.

---

# Status do Documento

**Pasta**

```text
docs/design-system/
```

**Arquivo**

```text
07-Iconografia.md
```

**Documento**

```text
GDS-07
```

**Código**

```text
GDS-ICON
```

**Versão**

```text
1.0
```

**Status**

```text
OFICIAL
```

---

**Fim do Documento**


