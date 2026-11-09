# GereIgreja Design System — GDS

Design System  
↓  
Fonte canônica da linguagem visual, dos componentes e dos padrões de experiência do GereIgreja.

Esta pasta reúne a documentação oficial do GereIgreja Design System (GDS).

O GDS define **como a interface deve parecer e se comportar visualmente**.  
`docs/frontend/` define **como essa linguagem é implementada tecnicamente**.

## Finalidade

- identidade visual;
- princípios de design;
- cores, tipografia, espaçamento e grid;
- iconografia;
- botões, formulários, cards, tabelas, modais e feedback;
- navegação;
- dashboards;
- acessibilidade;
- animações;
- boas práticas;
- governança da evolução visual.

## Autoridade

```text
design-system/
→ aparência, linguagem visual e UX

frontend/
→ implementação em Templates, CSS, JS, HTMX e Alpine

apps/
→ regras funcionais

qualidade/
→ critérios e gates de validação
```

O GDS não define regra de negócio e não deve duplicar detalhes técnicos de implementação.

## Inventário real atual

```text
01-Introducao.md
02-Principios.md
03-Cores.md
04-Tipografia.md
05-Espacamento.md
06-Grid.md
07-Iconografia.md
08-Botoes.md
09-Formularios.md
10-Cards.md
11-GDS-Tabelas-e-Listagens.md
12-GDS-Modais-Dialogs-e-Confirmacoes.md
13-GDS-Alertas-Toasts-e-Feedback.md
14-Navegacao.md
15-Dashboards.md
16-Acessibilidade.md
17-Animacoes.md
18-Boas-Praticas.md
19-Governanca.md
```

O README anterior usava nomes simplificados e uma ordem antiga para alguns documentos. O índice deve refletir os **arquivos realmente existentes**.

## Relação com Frontend

```text
GDS define
→ padrão visual e comportamento esperado

Frontend implementa
→ templates, classes, CSS, JS e interação
```

Detalhes como organização de templates, nomes de arquivos CSS, HTMX, Alpine.js e partials pertencem ao Frontend.

## Formulários

```text
design-system/09-Formularios.md
→ apresentação e UX

backend/09-Forms.md
→ Django Forms

frontend/
→ composição técnica da interface
```

Essas fontes são complementares, não concorrentes.

## Dashboards

```text
design-system/15-Dashboards.md
→ padrão visual e UX

frontend/11-Dashboards.md
→ implementação técnica

apps/
→ dados e comportamento funcional
```

Por isso, Dashboard não deve existir como app documental independente.

## Acessibilidade

Acessibilidade é parte do Design System.

O GDS define requisitos de interface; `docs/qualidade/` pode concentrar checklists e evidências de validação.

## Relação com o Framework GDS

Existe também:

```text
docs/frameworks/01-GDS-GereIgreja-Design-System.md
```

A relação correta é:

```text
frameworks/01-GDS...
→ referência institucional e transversal

design-system/
→ detalhamento operacional do sistema visual
```

O framework deve apontar para esta família, não competir com ela.

## Relação com Governança antiga

`docs/governanca/07-Padroes-de-Templates.md` se sobrepõe ao GDS em componentes, formulários, tabelas, CSS, acessibilidade e padrões visuais.

A ação correta é:

```text
comparar com design-system/ e frontend/
↓
absorver conteúdo exclusivo ainda válido
↓
corrigir referências
↓
arquivar ou remover o legado
```

Não mover o arquivo inteiro para esta pasta.

## Roadmap antigo

O README anterior mencionava temas futuros como múltiplos temas, modo escuro, white-label e mobile.

Esses itens não devem ser tratados como capacidades atuais nem como documentos obrigatórios.

Planejamento só permanece como compromisso quando houver iniciativa formal correspondente.

## Regra para documento 20+

A família já possui cobertura alta em `01–19`.

Antes de criar `20+`:

1. demonstrar lacuna real;
2. verificar se o tema cabe em documento existente;
3. comparar com Frontend e Qualidade;
4. preferir evolução antes de criação;
5. atualizar índices apenas quando necessário.

A existência de `19-Governanca.md` não cria obrigação de `20`.

## Estado da família

```text
Status: CANÔNICA
Baseline real: 01–19
Cobertura: ALTA
Expansão automática: NÃO
Prioridade: coerência visual e aderência ao Frontend
```

## Princípio de manutenção

O GDS deve reduzir variação, não aumentar catálogo.

**Reutilizar antes de criar. Consolidar antes de especializar.**
