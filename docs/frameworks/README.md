# Frameworks — Referenciais Estruturantes do GereIgreja

Frameworks  
↓  
Como a plataforma governa áreas transversais.

Esta pasta reúne os frameworks internos oficiais do GereIgreja.

Eles não documentam módulos de negócio específicos. Seu papel é estabelecer princípios, políticas e padrões transversais que orientam as demais famílias de documentação e a implementação da plataforma.

## Finalidade da pasta

- concentrar referenciais estruturantes;
- definir princípios e políticas comuns;
- evitar que cada módulo crie suas próprias regras para temas transversais;
- apontar a autoridade de cada área;
- reduzir duplicação entre arquitetura, segurança, qualidade, documentação e operação.

## Índice Oficial

| Nº | Framework | Documento | Responsabilidade principal |
|---:|---|---|---|
| 01 | GDS | [01-GDS-GereIgreja-Design-System.md](01-GDS-GereIgreja-Design-System.md) | Design System e linguagem visual |
| 02 | GAF | [02-GAF-GereIgreja-Authentication-Framework.md](02-GAF-GereIgreja-Authentication-Framework.md) | Autenticação e fundamentos de autorização |
| 03 | GSF | [03-GSF-GereIgreja-Security-Framework.md](03-GSF-GereIgreja-Security-Framework.md) | Segurança |
| 04 | GQF | [04-GQF-GereIgreja-Quality-Framework.md](04-GQF-GereIgreja-Quality-Framework.md) | Qualidade |
| 05 | GDF | [05-GDF-GereIgreja-Documentation-Framework.md](05-GDF-GereIgreja-Documentation-Framework.md) | Documentação |
| 06 | GOC | [06-GOC-GereIgreja-Operations-Center.md](06-GOC-GereIgreja-Operations-Center.md) | Operações |

## Relação com as demais famílias

Os frameworks definem a camada de referência.

```text
Framework
   ↓
Família especializada
   ↓
Implementação / procedimento / evidência
```

Exemplos:

```text
GDS
↓
design-system/
↓
frontend/
```

```text
GAF
↓
seguranca/ + backend/
↓
autenticação e autorização implementadas
```

```text
GSF
↓
seguranca/
↓
controles, políticas e evidências
```

```text
GQF
↓
qualidade/
↓
testes, homologação, checklists e gates
```

```text
GDF
↓
00-Guia-de-Documentacao.md + INDEX.md
↓
organização real da documentação
```

```text
GOC
↓
operacoes/
↓
runbooks e procedimentos operacionais
```

## Regra de Autoridade

Um framework define princípios transversais.

A documentação especializada detalha sua aplicação.

Um documento de módulo descreve apenas como aquela regra se manifesta no domínio.

Portanto:

- `frameworks/` não deve duplicar detalhes de implementação;
- famílias especializadas não devem redefinir princípios do framework;
- `apps/` não deve criar políticas globais próprias;
- documentos históricos não devem prevalecer sobre referenciais oficiais atuais.

## Sobre o GDF

O GDF é o framework responsável por definir como o conhecimento técnico deve ser registrado e estabelece padrões para arquitetura, engenharia, APIs, módulos, processos, operação, segurança e desenvolvimento.

O próprio GDF determina que documentos duplicados devem ser evitados e que cada documento deve permanecer em sua pasta oficial.

A governança documental operacional atual é complementada pelo arquivo raiz:

- `docs/00-Guia-de-Documentacao.md`

e pelo mapa:

- `docs/INDEX.md`

Quando houver divergência entre um exemplo estrutural antigo do GDF-05 e a árvore documental real atual, deve prevalecer a governança documental vigente e deliberadamente atualizada.

## Criação de Novos Frameworks

Um novo framework não deve ser criado apenas para completar numeração ou porque existe um novo tema.

Antes de propor outro framework, deve ser demonstrado que:

1. o tema é transversal a múltiplos domínios;
2. possui regras próprias suficientemente amplas;
3. não está coberto por um framework existente;
4. exige uma autoridade normativa independente;
5. sua criação reduzirá, e não aumentará, duplicação documental.

Na ausência dessas condições, o conteúdo deve evoluir dentro da família ou framework já responsável pelo tema.

## Estado da Família

A família atualmente possui seis frameworks oficiais:

```text
01 GDS
02 GAF
03 GSF
04 GQF
05 GDF
06 GOC
```

Não há lacuna numérica a preencher.

A família deve ser considerada **estável**.

Novos documentos `07+` somente devem surgir após análise formal de lacuna e decisão explícita de governança.

## Princípio de manutenção

Frameworks devem permanecer poucos, claros e estáveis.

**Evoluir o framework existente é preferível a criar uma nova autoridade concorrente.**
