Pasta:
docs/design-system/

Arquivo:
03-Cores.md

Documento:
GDS-03

Código:
GDS-CORES

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

# GDS-03 — Cores

> *"As cores do GereIgreja representam sua identidade visual. Elas comunicam organização, confiança, clareza e profissionalismo, além de orientar a interação do usuário com a plataforma."*

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia das Cores
4. Identidade Visual
5. Arquitetura de Design Tokens
6. Paleta Oficial
7. Cores Institucionais
8. Escala Brand
9. Paleta Neutra
10. Cores Semânticas
11. Estados Visuais
12. Casos Reais do GereIgreja
13. Relação com os Demais Frameworks

---

# 1. Objetivo

Este documento estabelece oficialmente o padrão de utilização das cores no GereIgreja.

Seu propósito é garantir consistência visual, acessibilidade e uniformidade em todos os módulos da plataforma.

Toda interface deverá utilizar exclusivamente as cores definidas neste documento.

---

# 2. Escopo

As diretrizes aqui definidas aplicam-se a:

- Área de Gestão;
- Portal Público;
- Landing Pages;
- Dashboards;
- Formulários;
- Tabelas;
- Cards;
- Modais;
- Alertas;
- Relatórios;
- Componentes reutilizáveis.

Não se aplicam à identidade visual de igrejas cadastradas na plataforma, que poderá evoluir futuramente para suportar personalização (White Label).

---

# 3. Filosofia das Cores

A paleta oficial do GereIgreja foi construída para transmitir:

- confiança;
- organização;
- serenidade;
- profissionalismo;
- clareza;
- modernidade.

As cores não possuem apenas função estética.

Elas comunicam significado, orientam decisões do usuário e reforçam a identidade da plataforma.

Toda utilização deverá possuir propósito funcional.

---

# 4. Identidade Visual

A identidade visual oficial utiliza o tom turquesa como elemento principal da marca.

Essa escolha representa:

- equilíbrio;
- segurança;
- crescimento;
- estabilidade;
- tecnologia;
- acolhimento.

As demais cores complementam essa identidade sem competir com a cor institucional.

---

# 5. Arquitetura de Design Tokens

Toda cor utilizada na interface deverá ser referenciada através de Design Tokens.

Exemplo conceitual:

Brand

↓

Semantic

↓

Component

↓

Screen

↓

Interface

Essa arquitetura evita duplicação de estilos e facilita futuras alterações visuais.

---

# 6. Paleta Oficial

A paleta oficial do GereIgreja é composta por quatro grupos principais.

- Institucionais;
- Neutras;
- Semânticas;
- Estados da Interface.

Nenhuma nova cor deverá ser introduzida sem documentação oficial.

---

# 7. Cores Institucionais

## Brand 700

Cor principal da identidade institucional.

HEX

```
#0D8281
```

Utilização:

- Botões primários;
- Links principais;
- Navegação ativa;
- Indicadores institucionais;
- Elementos de destaque.

---

## Brand 900

Versão escura da cor institucional.

HEX

```
#0A6665
```

Utilização:

- Hover;
- Active;
- Elementos de maior contraste;
- Cabeçalhos específicos;
- Estados pressionados.

---

## Brand Soft

Versão suave da identidade visual.

HEX

```
#DFF4F3
```

Utilização:

- fundos informativos;
- painéis leves;
- áreas destacadas;
- cards institucionais;
- indicadores positivos discretos.

---

# 8. Escala Brand

A identidade visual utiliza atualmente três níveis oficiais.

| Token | HEX | Utilização |
|--------|------|------------|
| Brand Soft | #DFF4F3 | Fundos suaves |
| Brand 700 | #0D8281 | Cor principal |
| Brand 900 | #0A6665 | Hover e contraste |

Escalas intermediárias poderão ser incorporadas futuramente sem alterar a identidade visual da plataforma.

---

# 9. Paleta Neutra

A paleta neutra constitui a base visual da interface.

---

## Background

HEX

```
#F1F5F9
```

Utilização:

- fundo principal das páginas;
- dashboards;
- áreas externas dos cards.

---

## Surface

HEX

```
#FFFFFF
```

Utilização:

- cards;
- modais;
- formulários;
- tabelas;
- painéis.

---

## Border

HEX

```
#D7E2E8
```

Utilização:

- separadores;
- linhas de tabelas;
- contornos;
- inputs.

---

## Text

HEX

```
#1E293B
```

Utilização:

- títulos;
- textos principais;
- menus;
- conteúdo.

---

## Text Muted

HEX

```
#64748B
```

Utilização:

- descrições;
- legendas;
- textos auxiliares;
- informações secundárias.

---

# 10. Cores Semânticas

As cores semânticas comunicam estados da interface.

---

## Success

HEX

```
#10B981
```

Representa:

- operação concluída;
- confirmação;
- recebimentos;
- sucesso.

Exemplos:

- Receita registrada;
- Cadastro salvo;
- Comunicação enviada.

---

## Warning

HEX

```
#D97706
```

Representa:

- atenção;
- pendências;
- validações;
- alertas.

Exemplos:

- Evento próximo;
- Cadastro incompleto;
- Aprovação pendente.

---

## Danger

HEX

```
#EF4444
```

Representa:

- erro;
- exclusão;
- falha;
- operação irreversível.

Exemplos:

- Excluir membro;
- Remover congregação;
- Cancelar lançamento financeiro.

---

# 11. Estados Visuais

Os componentes deverão utilizar estados consistentes.

Estados oficiais:

- Default;
- Hover;
- Focus;
- Active;
- Disabled;
- Success;
- Warning;
- Danger;
- Loading.

As cores deverão permanecer consistentes em todos os módulos.

---

# 12. Casos Reais do GereIgreja

As cores definidas neste documento refletem necessidades reais da plataforma.

### Dashboard Principal

Brand 700 utilizada em indicadores institucionais e ações principais.

---

### Secretaria

Success utilizada para confirmação de cadastro de membros.

---

### Tesouraria

Success para receitas.

Danger para despesas críticas ou exclusões.

Warning para lançamentos pendentes.

---

### Escola Bíblica

Brand Soft utilizada em painéis informativos.

---

### Comunicação

Brand 700 utilizada em ações de envio.

---

### Portal Público

Brand 700 reforça a identidade institucional em botões, menus e chamadas para ação.

---

# 13. Relação com os Demais Frameworks

Este documento integra-se diretamente aos seguintes frameworks:

GFE — GereIgreja Frontend Engineering

Responsável pela implementação técnica dos estilos.

---

GDS — GereIgreja Design System

Responsável pela identidade visual da plataforma.

---

Os próximos documentos detalharão a aplicação dessas cores em:

- Tipografia;
- Botões;
- Formulários;
- Cards;
- Alertas;
- Dashboards.

---
# 14. Escalas de Cores

Embora a identidade visual atual utilize apenas os níveis principais da paleta institucional, o Design System prevê uma arquitetura escalável para futuras evoluções.

Essa estrutura permitirá maior flexibilidade sem comprometer a identidade do GereIgreja.

Escala prevista:

| Token | Finalidade |
|--------|------------|
| Brand 50 | Fundos extremamente suaves |
| Brand 100 | Áreas informativas |
| Brand 200 | Destaques discretos |
| Brand 300 | Componentes secundários |
| Brand 400 | Estados intermediários |
| Brand 500 | Cor institucional alternativa |
| Brand 600 | Ênfase moderada |
| Brand 700 | Cor principal oficial |
| Brand 800 | Alto contraste |
| Brand 900 | Hover, Active e elementos escuros |

Atualmente, os tokens oficiais implementados são:

- Brand Soft
- Brand 700
- Brand 900

Os demais níveis permanecem reservados para evolução futura.

---

# 15. Aplicação das Cores

Cada grupo de cores possui finalidade específica.

---

## Cor Institucional

Utilizar em:

- botões primários;
- links;
- indicadores principais;
- elementos ativos;
- identidade da marca.

---

## Cores Neutras

Utilizar em:

- fundos;
- superfícies;
- separadores;
- textos;
- formulários;
- tabelas.

As cores neutras deverão predominar na interface.

---

## Cores Semânticas

Nunca deverão ser utilizadas apenas como decoração.

Cada uma comunica um significado específico.

Success → operação concluída.

Warning → atenção.

Danger → erro ou operação crítica.

---

# 16. Dashboards

Os dashboards concentram informações estratégicas.

As cores deverão facilitar a interpretação dos indicadores.

---

## KPIs

Utilizar:

Brand 700

Para:

- indicadores principais;
- totais;
- métricas gerais.

---

## Crescimento

Success

Exemplos:

- aumento de membros;
- crescimento financeiro;
- frequência elevada.

---

## Atenção

Warning

Exemplos:

- eventos próximos;
- pendências;
- aprovações.

---

## Problemas

Danger

Exemplos:

- despesas críticas;
- erros;
- inconsistências.

---

# 17. Gráficos

Os gráficos deverão utilizar paleta consistente.

Ordem recomendada:

1. Brand 700
2. Success
3. Warning
4. Danger
5. Brand Soft
6. Tons neutros

Evitar excesso de cores simultaneamente.

A informação deve permanecer legível.

---

# 18. Contraste

Toda combinação de cores deverá priorizar legibilidade.

Recomendações:

- textos escuros sobre fundos claros;
- evitar contraste insuficiente;
- preservar leitura em dispositivos móveis;
- respeitar boas práticas de acessibilidade.

Sempre que possível utilizar contraste compatível com WCAG AA.

---

# 19. Acessibilidade

As cores nunca deverão ser o único meio de comunicar informação.

Sempre combinar:

- ícones;
- textos;
- badges;
- mensagens;
- indicadores visuais.

Exemplo inadequado:

"campo vermelho"

Exemplo recomendado:

"Campo obrigatório" acompanhado da indicação visual.

---

# 20. Casos de Uso

## Dashboard Financeiro

Receitas

Success

---

Despesas

Danger

---

Saldo Geral

Brand 700

---

Pendências

Warning

---

# Cadastro de Membros

Botão Salvar

Brand 700

---

Mensagem de sucesso

Success

---

Campos inválidos

Danger

---

Informações auxiliares

Text Muted

---

# Comunicação

Botão Enviar

Brand 700

---

Mensagem enviada

Success

---

Erro de envio

Danger

---

# Portal Público

Call To Action

Brand 700

---

Cards informativos

Surface

---

Fundos

Background

---

# 21. Evidências Arquiteturais

As diretrizes deste documento refletem a implementação atual do GereIgreja.

---

## EA-GDS-016

A identidade institucional utiliza o tom turquesa como cor principal da marca.

---

## EA-GDS-017

A estilização deverá utilizar Design Tokens centralizados.

---

## EA-GDS-018

Os componentes reutilizáveis compartilham a mesma paleta institucional.

---

## EA-GDS-019

Bootstrap constitui a base da interface, recebendo personalizações através do Design System.

---

## EA-GDS-020

Os recursos CSS compartilhados encontram-se centralizados em:

```
static/css/design_system.css
```

---

# 22. Especificações Oficiais

---

## GDS-COLOR-001

Toda cor utilizada deverá possuir Design Token oficial.

---

## GDS-COLOR-002

É proibido utilizar cores hardcoded em componentes reutilizáveis.

---

## GDS-COLOR-003

A cor institucional deverá representar ações primárias.

---

## GDS-COLOR-004

As cores semânticas deverão manter o mesmo significado em toda a plataforma.

---

## GDS-COLOR-005

Fundos deverão utilizar preferencialmente a paleta neutra.

---

## GDS-COLOR-006

Textos deverão priorizar legibilidade.

---

## GDS-COLOR-007

Gráficos deverão utilizar paleta padronizada.

---

## GDS-COLOR-008

Novas cores deverão ser documentadas antes da implementação.

---

## GDS-COLOR-009

A identidade visual deverá permanecer consistente entre Área Pública e Área de Gestão.

---

## GDS-COLOR-010

Toda evolução da paleta deverá preservar compatibilidade com a identidade institucional.

---

# 23. Uso Correto

✔ Utilizar Brand 700 em botões principais.

✔ Utilizar Success para confirmações.

✔ Utilizar Warning apenas para atenção.

✔ Utilizar Danger somente em erros ou ações críticas.

✔ Utilizar Surface para cards.

✔ Utilizar Background como fundo principal.

---

# 24. Uso Incorreto

✘ Utilizar Success para elementos decorativos.

✘ Utilizar Danger em ações positivas.

✘ Alterar a cor institucional por módulo.

✘ Utilizar múltiplas tonalidades sem padronização.

✘ Aplicar cores arbitrárias diretamente no HTML ou CSS.

✘ Quebrar a identidade visual entre módulos.

---

# 25. Boas Práticas

As cores representam uma das principais ferramentas de comunicação da interface do GereIgreja.

Toda implementação deverá observar as seguintes recomendações.

---

## Utilizar sempre os Design Tokens

Toda cor utilizada na plataforma deverá ser referenciada através dos tokens oficiais.

Exemplos:

- Brand 700
- Brand 900
- Brand Soft
- Background
- Surface
- Border
- Text
- Text Muted
- Success
- Warning
- Danger

Nunca utilizar valores HEX diretamente em componentes reutilizáveis.

---

## Priorizar a Paleta Neutra

A interface deverá ser predominantemente neutra.

As cores institucionais deverão ser utilizadas apenas para orientar o usuário e destacar ações importantes.

---

## Utilizar Cores Semânticas Corretamente

Cada cor possui significado específico.

Success

- operações concluídas;
- confirmações;
- indicadores positivos.

Warning

- atenção;
- pendências;
- validações.

Danger

- erros;
- exclusões;
- falhas;
- operações irreversíveis.

---

## Manter Consistência

Botões iguais deverão utilizar as mesmas cores.

Cards semelhantes deverão compartilhar a mesma identidade.

Dashboards deverão utilizar a mesma linguagem visual.

---

## Pensar em Acessibilidade

Sempre considerar:

- contraste;
- legibilidade;
- diferentes condições de iluminação;
- usuários com deficiência visual.

As cores nunca deverão ser o único meio de transmitir informação.

---

# 26. Anti-patterns

Os comportamentos abaixo não fazem parte da arquitetura oficial do GereIgreja.

---

## 26.1 Cores Hardcoded

Evitar:

```css
color: #0D8281;
background: #10B981;
border-color: #EF4444;
```

Utilizar sempre Design Tokens.

---

## 26.2 Paletas Diferentes por Módulo

Não criar identidades próprias para:

- Secretaria;
- Financeiro;
- Escola Bíblica;
- Eventos;
- Comunicação;
- Patrimônio.

Toda a plataforma deverá compartilhar a mesma identidade visual.

---

## 26.3 Uso Decorativo das Cores

As cores não deverão ser utilizadas apenas por estética.

Toda cor deverá possuir função clara na interface.

---

## 26.4 Excesso de Destaques

Evitar utilizar Brand, Success, Warning e Danger simultaneamente em grande quantidade.

O excesso reduz a capacidade de percepção do usuário.

---

## 26.5 Falta de Contraste

Nunca utilizar combinações que dificultem a leitura.

A prioridade sempre será a legibilidade.

---

## 26.6 Quebra da Identidade

Alterações locais da paleta oficial não são permitidas.

Mudanças deverão ser documentadas previamente.

---

# 27. Checklist

Antes da aprovação de qualquer interface verificar.

---

## Identidade

- [ ] utiliza a paleta oficial?
- [ ] mantém identidade institucional?
- [ ] utiliza Brand corretamente?

---

## Tokens

- [ ] utiliza Design Tokens?
- [ ] evita cores hardcoded?
- [ ] utiliza CSS compartilhado?

---

## Semântica

- [ ] Success utilizado corretamente?
- [ ] Warning utilizado corretamente?
- [ ] Danger utilizado corretamente?

---

## Acessibilidade

- [ ] contraste adequado?
- [ ] leitura confortável?
- [ ] cores não são o único indicador?

---

## Consistência

- [ ] compatível com os demais módulos?
- [ ] dashboards seguem o padrão?
- [ ] componentes reutilizados?

---

## Documentação

- [ ] novas cores documentadas?
- [ ] tokens atualizados?
- [ ] Design System revisado?

---

# 28. Glossário

## Brand

Cor institucional oficial do GereIgreja.

---

## Design Token

Representação padronizada de uma propriedade visual reutilizável.

Exemplo:

- Brand 700;
- Surface;
- Border.

---

## Cor Semântica

Cor utilizada para comunicar significado funcional.

Exemplos:

Success

Warning

Danger

---

## Paleta Neutra

Conjunto de cores utilizado para:

- fundos;
- textos;
- superfícies;
- separadores.

---

## Contraste

Diferença entre cores que garante boa leitura dos elementos da interface.

---

## White Label

Funcionalidade futura que permitirá personalização visual para diferentes organizações sem comprometer a arquitetura do Design System.

---

# 29. Governança

A evolução da paleta oficial deverá ocorrer de forma controlada.

Toda alteração deverá observar os princípios abaixo.

---

## Documentação

Novas cores deverão ser documentadas antes da implementação.

---

## Compatibilidade

Mudanças deverão preservar compatibilidade com:

- GereIgreja Frontend Engineering;
- GereIgreja Design System;
- Bootstrap;
- componentes existentes.

---

## Centralização

Toda alteração deverá ocorrer através dos Design Tokens oficiais.

---

## Evolução

A expansão da paleta deverá preservar a identidade institucional baseada no tom turquesa.

---

# 30. Roadmap

## Curto Prazo

- consolidação dos Design Tokens;
- padronização completa da paleta oficial;
- eliminação de cores hardcoded.

---

## Médio Prazo

- escalas completas Brand 50–900;
- documentação visual das combinações;
- biblioteca oficial de temas para gráficos.

---

## Longo Prazo

- Dark Mode;
- White Label;
- temas institucionais;
- personalização por organização mantendo compatibilidade com o GDS.

---

# 31. Documentos Relacionados

## GereIgreja Design System

- README.md
- GDS-01 — Introdução
- GDS-02 — Princípios
- GDS-04 — Tipografia
- GDS-05 — Espaçamento
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

As cores constituem um dos pilares da identidade visual do GereIgreja.

Mais do que elementos estéticos, elas orientam a navegação, comunicam estados da interface, reforçam a identidade institucional e contribuem diretamente para a experiência do usuário.

A utilização consistente da paleta oficial garante que toda a plataforma mantenha uma aparência uniforme, profissional e preparada para evoluir de forma sustentável.

Toda implementação futura deverá utilizar exclusivamente os Design Tokens e as diretrizes estabelecidas neste documento.

---

# Status do Documento

**Pasta**

```
docs/design-system/
```

**Arquivo**

```
03-Cores.md
```

**Documento**

```
GDS-03
```

**Código**

```
GDS-CORES
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

