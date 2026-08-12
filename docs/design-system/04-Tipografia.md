Pasta:
docs/design-system/

Arquivo:
04-Tipografia.md

Documento:
GDS-04

Código:
GDS-TYPO

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

# GDS-04 — Tipografia

> *"A tipografia do GereIgreja deve comunicar clareza, organização e confiança, permitindo que o usuário encontre informações rapidamente e execute suas atividades com o menor esforço cognitivo possível."*

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia Tipográfica
4. Princípios
5. Famílias Tipográficas
6. Hierarquia Tipográfica
7. Escala Tipográfica
8. Pesos
9. Altura de Linha
10. Comprimento de Linha
11. Casos Reais do GereIgreja
12. Relação com os Demais Frameworks

---

# 1. Objetivo

Este documento define oficialmente os padrões tipográficos utilizados em toda a plataforma GereIgreja.

Seu objetivo é garantir:

- consistência visual;
- excelente legibilidade;
- acessibilidade;
- identidade visual uniforme;
- facilidade de manutenção.

Toda interface deverá utilizar exclusivamente os padrões definidos neste documento.

---

# 2. Escopo

Este documento aplica-se a:

- Área de Gestão;
- Portal Público;
- Landing Pages;
- Dashboards;
- Relatórios;
- Formulários;
- Tabelas;
- Componentes;
- Modais;
- Alertas;
- Comunicação visual.

---

# 3. Filosofia Tipográfica

A tipografia do GereIgreja prioriza produtividade.

O usuário permanece várias horas utilizando o sistema.

Por esse motivo a leitura deverá ser:

- confortável;
- rápida;
- previsível;
- consistente.

O objetivo da tipografia não é decorar a interface.

Seu papel é facilitar a leitura das informações.

---

# 4. Princípios

Toda decisão tipográfica deverá respeitar:

- simplicidade;
- clareza;
- consistência;
- acessibilidade;
- hierarquia visual;
- legibilidade.

Mudanças deverão preservar a identidade visual da plataforma.

---

# 5. Famílias Tipográficas

O GereIgreja utiliza duas famílias tipográficas oficiais.

---

## Fonte Principal

Utilizada em praticamente toda a interface.

Requisitos:

- excelente leitura em telas;
- ampla compatibilidade;
- boa renderização;
- suporte internacional.

Fonte oficial:

```
Inter
```

Fallback:

```
system-ui,
Segoe UI,
Roboto,
Helvetica,
Arial,
sans-serif
```

---

## Fonte Monoespaçada

Utilizada para:

- códigos;
- identificadores;
- logs;
- exemplos técnicos;
- documentação.

Fonte oficial:

```
JetBrains Mono
```

Fallback:

```
Consolas,
Courier New,
monospace
```

---

# 6. Hierarquia Tipográfica

Toda página deverá possuir hierarquia clara.

Estrutura recomendada:

```
H1

↓

H2

↓

H3

↓

Título de Card

↓

Texto Principal

↓

Texto Secundário

↓

Legenda
```

O usuário deverá identificar imediatamente a importância de cada informação.

---

# 7. Escala Tipográfica

Escala oficial:

| Elemento | Tamanho |
|-----------|----------|
| Display | 48px |
| H1 | 36px |
| H2 | 30px |
| H3 | 24px |
| H4 | 20px |
| H5 | 18px |
| H6 | 16px |
| Body Large | 18px |
| Body | 16px |
| Small | 14px |
| Caption | 12px |

Essa escala deverá ser reutilizada em toda a plataforma.

---

# 8. Pesos

Pesos oficiais.

| Peso | Utilização |
|-------|------------|
| 400 | Texto padrão |
| 500 | Destaques leves |
| 600 | Subtítulos |
| 700 | Títulos |
| 800 | Destaques especiais |

Evitar pesos diferentes sem necessidade.

---

# 9. Altura de Linha

Alturas recomendadas.

| Tipo | Line Height |
|------|--------------|
| H1 | 1.20 |
| H2 | 1.25 |
| H3 | 1.30 |
| Texto | 1.50 |
| Legendas | 1.45 |

Esses valores favorecem leitura prolongada.

---

# 10. Comprimento de Linha

Para melhorar a leitura recomenda-se:

- entre 50 e 80 caracteres por linha;
- evitar blocos excessivamente largos;
- preservar margens adequadas.

Em relatórios e documentação poderá haver pequenas variações.

---

# 11. Casos Reais do GereIgreja

---

## Dashboard

Indicadores principais deverão utilizar maior destaque tipográfico.

---

## Cadastro de Membros

Os títulos das seções deverão facilitar a localização das informações.

---

## Financeiro

Valores monetários deverão utilizar destaque moderado.

Jamais exagerado.

---

## Relatórios

Priorizar leitura contínua.

---

## Portal Público

Títulos principais deverão reforçar identidade institucional.

---

# 12. Relação com os Demais Frameworks

Este documento integra-se diretamente a:

GFE

Responsável pela implementação.

---

GDS

Responsável pela identidade visual.

---

Os próximos documentos complementarão esta especificação através da definição de:

- Espaçamento;
- Grid;
- Iconografia;
- Botões;
- Formulários.

---

# 13. Tipografia em Formulários

Os formulários representam uma das principais interfaces da Área de Gestão do GereIgreja.

A tipografia deverá facilitar o preenchimento e reduzir erros de interpretação.

---

## Labels

Os rótulos deverão:

- permanecer acima do campo;
- possuir peso 500;
- utilizar cor Text;
- manter alinhamento consistente.

Evitar labels excessivamente longos.

---

## Placeholders

Os placeholders possuem função auxiliar.

Devem utilizar:

- Text Muted;
- peso 400;
- linguagem objetiva.

Nunca substituir completamente o label.

---

## Mensagens de Validação

Mensagens de erro deverão:

- utilizar tamanho Small;
- permanecer próximas ao campo;
- utilizar a cor Danger.

Mensagens de sucesso poderão utilizar Success.

---

# 14. Tipografia em Tabelas

As tabelas concentram grande volume de informações.

A tipografia deverá priorizar leitura rápida.

---

## Cabeçalhos

Utilizar:

- peso 600;
- tamanho Small;
- Text;
- alinhamento consistente.

---

## Conteúdo

Utilizar:

- Body;
- peso 400;
- espaçamento confortável.

---

## Valores Numéricos

Sempre alinhar à direita.

Exemplos:

- valores financeiros;
- quantidades;
- totais;
- estatísticas.

---

# 15. Tipografia em Dashboards

Os dashboards apresentam indicadores estratégicos.

A tipografia deverá estabelecer hierarquia clara.

---

## KPIs

Utilizar destaque moderado.

Evitar tamanhos exagerados.

---

## Descrição

Utilizar Body ou Small.

---

## Indicadores Secundários

Utilizar Text Muted.

---

## Cards

Título

H5

Valor

H3

Descrição

Small

---

# 16. Tipografia em Relatórios

Relatórios possuem finalidade diferente dos dashboards.

Devem privilegiar leitura contínua.

---

## Títulos

Peso 700.

---

## Subtítulos

Peso 600.

---

## Conteúdo

Body.

---

## Rodapé

Small.

---

## Numeração

Sempre consistente em todo o documento.

---

# 17. Tipografia em Alertas

Os alertas comunicam informações importantes.

Sua tipografia deverá facilitar rápida identificação.

---

Success

Mensagem objetiva.

---

Warning

Explicação clara da situação.

---

Danger

Descrição do problema e possível ação corretiva.

---

Info

Texto curto e objetivo.

---

# 18. Responsividade

A tipografia deverá adaptar-se automaticamente aos diferentes dispositivos.

Prioridade:

Desktop

↓

Notebook

↓

Tablet

↓

Smartphone

Em telas menores poderá haver redução proporcional dos títulos, preservando a hierarquia visual.

---

# 19. Acessibilidade

Toda configuração tipográfica deverá favorecer leitura prolongada.

Recomenda-se:

- contraste adequado;
- altura de linha confortável;
- evitar blocos muito densos;
- evitar textos excessivamente pequenos;
- respeitar boas práticas WCAG.

A legibilidade possui prioridade sobre escolhas estéticas.

---

# 20. Evidências Arquiteturais

As diretrizes deste documento refletem a implementação atual do GereIgreja.

---

## EA-GDS-021

A interface utiliza tipografia sem serifa como padrão principal.

---

## EA-GDS-022

A renderização ocorre através de Django Templates.

---

## EA-GDS-023

Bootstrap fornece parte da escala tipográfica utilizada.

---

## EA-GDS-024

A identidade visual complementa Bootstrap através do Design System.

---

## EA-GDS-025

Os componentes reutilizam a mesma hierarquia tipográfica.

---

# 21. Especificações Oficiais

---

## GDS-TYPO-001

Toda interface deverá utilizar exclusivamente as famílias tipográficas oficiais.

---

## GDS-TYPO-002

É proibido utilizar fontes diferentes sem documentação oficial.

---

## GDS-TYPO-003

Toda página deverá possuir hierarquia tipográfica clara.

---

## GDS-TYPO-004

Textos deverão priorizar legibilidade.

---

## GDS-TYPO-005

Indicadores importantes deverão utilizar maior destaque visual.

---

## GDS-TYPO-006

Relatórios deverão privilegiar leitura contínua.

---

## GDS-TYPO-007

Formulários deverão utilizar labels consistentes.

---

## GDS-TYPO-008

A tipografia deverá adaptar-se aos diferentes dispositivos.

---

## GDS-TYPO-009

A acessibilidade deverá orientar toda decisão tipográfica.

---

## GDS-TYPO-010

Novos padrões deverão ser documentados antes da implementação.

---

# 22. Exemplos de Aplicação

## Dashboard Financeiro

```
Receita do Mês

R$ 18.450,00

+12% em relação ao mês anterior
```

Hierarquia:

- H5
- H3
- Small

---

## Cadastro de Membros

```
Dados Pessoais

Nome Completo

Telefone

E-mail
```

Hierarquia clara facilita preenchimento.

---

## Relatórios

```
Relatório Financeiro

Período

Resumo

Receitas

Despesas

Saldo
```

Os títulos estruturam naturalmente a leitura.

---

# 23. Boas Práticas

A tipografia constitui um dos principais elementos da experiência do usuário do GereIgreja.

Sua utilização deverá favorecer produtividade, legibilidade e consistência visual.

---

## Utilizar Sempre as Famílias Oficiais

Toda interface deverá utilizar exclusivamente as famílias tipográficas definidas pelo Design System.

Fonte principal:

```
Inter
```

Fonte monoespaçada:

```
JetBrains Mono
```

Novas fontes somente poderão ser incorporadas mediante aprovação da Engenharia.

---

## Respeitar a Hierarquia

A hierarquia tipográfica deverá comunicar naturalmente a importância das informações.

Sempre utilizar:

- H1 para títulos principais;
- H2 e H3 para organização da página;
- Body para conteúdo;
- Small para informações secundárias;
- Caption para observações e legendas.

---

## Manter Consistência

Elementos equivalentes deverão utilizar a mesma tipografia.

Exemplos:

- botões;
- tabelas;
- formulários;
- dashboards;
- relatórios;
- modais.

---

## Priorizar Legibilidade

Toda escolha tipográfica deverá favorecer leitura prolongada.

Evitar:

- excesso de negrito;
- textos muito pequenos;
- linhas excessivamente longas;
- baixo contraste.

---

## Reduzir Ruído Visual

A interface deverá transmitir organização.

Evitar:

- múltiplos tamanhos desnecessários;
- múltiplos pesos na mesma seção;
- excesso de estilos tipográficos.

---

# 24. Anti-patterns

Os padrões abaixo não fazem parte da arquitetura oficial do GereIgreja.

---

## 24.1 Fontes Diferentes

Não utilizar fontes diferentes entre módulos.

Toda a plataforma deverá compartilhar a mesma identidade tipográfica.

---

## 24.2 Hierarquia Inconsistente

Evitar páginas onde:

- subtítulos parecem títulos;
- títulos possuem menor destaque que textos;
- elementos importantes passam despercebidos.

---

## 24.3 Excesso de Negrito

O peso 700 deverá ser utilizado apenas quando necessário.

O excesso reduz sua eficácia.

---

## 24.4 Títulos Muito Grandes

Evitar títulos desproporcionais.

O objetivo é comunicar, não decorar.

---

## 24.5 Textos Muito Pequenos

Nunca reduzir o tamanho da fonte a ponto de comprometer a leitura.

---

## 24.6 Alinhamentos Irregulares

Manter alinhamento consistente entre:

- títulos;
- subtítulos;
- tabelas;
- formulários;
- dashboards.

---

# 25. Checklist

Antes da aprovação de qualquer interface verificar.

---

## Identidade

- [ ] utiliza a tipografia oficial?
- [ ] respeita a hierarquia?

---

## Legibilidade

- [ ] leitura confortável?
- [ ] contraste adequado?
- [ ] tamanho apropriado?

---

## Consistência

- [ ] títulos seguem o padrão?
- [ ] formulários seguem o padrão?
- [ ] dashboards seguem o padrão?
- [ ] tabelas seguem o padrão?

---

## Responsividade

- [ ] Desktop
- [ ] Notebook
- [ ] Tablet
- [ ] Smartphone

---

## Acessibilidade

- [ ] contraste adequado?
- [ ] altura de linha confortável?
- [ ] boa leitura prolongada?

---

## Documentação

- [ ] alterações documentadas?
- [ ] Design System atualizado?

---

# 26. Glossário

## Hierarquia Tipográfica

Organização visual dos textos de acordo com sua importância.

---

## Fonte Principal

Família utilizada na maior parte da interface.

---

## Fonte Monoespaçada

Fonte utilizada para:

- códigos;
- identificadores;
- documentação técnica;
- exemplos.

---

## Peso Tipográfico

Espessura visual da fonte.

Exemplos:

- 400
- 500
- 600
- 700

---

## Line Height

Espaçamento vertical entre linhas de texto.

---

## Escala Tipográfica

Conjunto oficial de tamanhos utilizados na plataforma.

---

# 27. Governança

Toda alteração tipográfica deverá preservar a identidade visual do GereIgreja.

---

## Documentação

Mudanças deverão ser documentadas antes da implementação.

---

## Compatibilidade

A tipografia deverá permanecer compatível com:

- Bootstrap;
- Django Templates;
- Design System;
- componentes existentes.

---

## Evolução

A evolução da escala tipográfica deverá preservar compatibilidade sempre que possível.

---

## Revisão

Os padrões tipográficos deverão ser revisados periodicamente para acompanhar a evolução da plataforma.

---

# 28. Roadmap

## Curto Prazo

- consolidação da escala tipográfica;
- padronização completa dos componentes;
- eliminação de inconsistências.

---

## Médio Prazo

- documentação visual da hierarquia;
- catálogo tipográfico oficial;
- refinamento para dashboards.

---

## Longo Prazo

- suporte completo a temas;
- otimizações para PWA;
- adaptação para aplicações móveis;
- evolução contínua da acessibilidade.

---

# 29. Documentos Relacionados

## GereIgreja Design System

- README.md
- GDS-01 — Introdução
- GDS-02 — Princípios
- GDS-03 — Cores
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

A tipografia oficial do GereIgreja constitui um elemento fundamental da identidade visual da plataforma.

Sua padronização garante interfaces mais organizadas, melhora significativamente a legibilidade, reduz a carga cognitiva dos usuários e fortalece a consistência entre todos os módulos do sistema.

Toda implementação futura deverá seguir rigorosamente as diretrizes estabelecidas neste documento, assegurando uma experiência uniforme para pastores, secretários, tesoureiros, professores, líderes e demais usuários da plataforma.

---

# Status do Documento

**Pasta**

```
docs/design-system/
```

**Arquivo**

```
04-Tipografia.md
```

**Documento**

```
GDS-04
```

**Código**

```
GDS-TYPO
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

