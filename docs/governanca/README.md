# Governança — Diretrizes de Engenharia e Consolidação Documental

Governança  
↓  
Como princípios e decisões transversais orientam a engenharia do GereIgreja.

Esta pasta reúne documentos históricos e normativos de governança da engenharia.

Ela teve papel central na organização inicial dos padrões técnicos do projeto, mas hoje parte de seu conteúdo já possui famílias especializadas mais adequadas.

Por isso, `docs/governanca/` deve ser mantida como **camada de princípios e governança transversal**, enquanto documentos técnicos especializados devem ser gradualmente consolidados nas famílias canônicas correspondentes.

## Finalidade atual da pasta

- preservar princípios permanentes de engenharia;
- registrar diretrizes transversais;
- manter manifestos e fundamentos;
- conservar histórico de governança;
- servir como ponte entre princípios gerais e famílias especializadas;
- evitar que padrões antigos permaneçam como fontes concorrentes.

## O que mudou na arquitetura documental

O README histórico de Governança foi criado quando várias famílias atuais ainda não estavam consolidadas.

Naquele momento, ele tratava como “planejados” frameworks que hoje já existem oficialmente, como:

```text
GAF
GSF
GQF
GOC
```

Também listava uma estrutura de `docs/` que incluía pastas hoje removidas ou reorganizadas, como:

```text
design/
```

Portanto, a estrutura antiga não deve continuar sendo tratada como mapa oficial da documentação.

A autoridade atual sobre organização documental permanece em:

```text
docs/00-Guia-de-Documentacao.md
docs/INDEX.md
docs/frameworks/
```

## Fronteira com Frameworks

`docs/frameworks/` concentra os referenciais normativos oficiais especializados.

Exemplos:

```text
GDS
GAF
GSF
GQF
GDF
GOC
```

`docs/governanca/` não deve recriar esses frameworks.

Sua função é manter princípios gerais e documentos históricos de governança que ainda tenham valor transversal.

## Inventário atual

A pasta possui uma sequência histórica de documentos `00` a `15`.

Entre eles:

```text
00-Manifesto-Do-GereIgreja.md
01-Manifesto-da-Engenharia.md
02-Arquitetura-do-GereIgreja.md
04-Padroes-do-Django-Admin.md
05-Padroes-de-Models.md
06-Padroes-de-Views.md
07-Padroes-de-Templates.md
08-Padroes-de-URLs.md
09-Padroes-de-Forms.md
10-Padroes-de-Permissoes.md
11-Padroes-de-Seguranca.md
12-Padroes-de-Testes.md
13-Gestao-da-Documentacao.md
14-Checklist-de-Release.md
15-Auditoria-360-do-GereIgreja.md
```

A ausência de um número intermediário em qualquer instalação local não deve ser preenchida automaticamente.

## Classificação por destino canônico

### Permanecer em Governança

Documentos de princípios gerais e identidade técnica, como:

```text
00-Manifesto-Do-GereIgreja.md
01-Manifesto-da-Engenharia.md
```

podem permanecer aqui, desde que não conflitem com frameworks atuais.

### Comparar com Arquitetura

```text
02-Arquitetura-do-GereIgreja.md
```

deve ser comparado com:

```text
docs/arquitetura/
```

Se o conteúdo já estiver consolidado na família de Arquitetura, o documento de Governança deve ser tratado como histórico ou removido após consolidação.

### Comparar com Backend

```text
04-Padroes-do-Django-Admin.md
05-Padroes-de-Models.md
06-Padroes-de-Views.md
08-Padroes-de-URLs.md
09-Padroes-de-Forms.md
```

são padrões técnicos de implementação.

Hoje seu destino conceitual é:

```text
docs/backend/
```

ou outra família técnica especializada já existente.

Não manter duas fontes normativas com regras equivalentes.

### Comparar com Frontend

```text
07-Padroes-de-Templates.md
```

deve ser comparado com:

```text
docs/frontend/05-Templates.md
```

e demais documentos da família Frontend.

Após consolidação, não deve existir como padrão concorrente.

### Comparar com Segurança

```text
10-Padroes-de-Permissoes.md
11-Padroes-de-Seguranca.md
```

devem ser comparados com:

```text
docs/frameworks/02-GAF-...
docs/frameworks/03-GSF-...
docs/seguranca/
```

A autoridade especializada atual deve prevalecer.

### Comparar com Qualidade

```text
12-Padroes-de-Testes.md
```

deve ser comparado com:

```text
docs/frameworks/04-GQF-...
docs/qualidade/
docs/desenvolvimento/Como-Rodar-Testes.md
```

O documento não deve permanecer como segunda política de qualidade.

### Gestão da Documentação

```text
13-Gestao-da-Documentacao.md
```

estabelece regras gerais de criação, organização e manutenção documental.

Essa responsabilidade hoje pertence a:

```text
docs/00-Guia-de-Documentacao.md
docs/frameworks/05-GDF-...
docs/INDEX.md
```

Portanto, `13-Gestao-da-Documentacao.md` deve ser considerado **legado normativo**.

Não deve prevalecer sobre o GDF ou o Guia atual.

### Checklist de Release

```text
14-Checklist-de-Release.md
```

é um documento operacional de qualidade/release.

Seu conteúdo aborda:

- preparação;
- código;
- banco;
- segurança;
- performance;
- interface;
- testes;
- documentação;
- deploy;
- pós-deploy;
- rollback.

Seu destino conceitual é principalmente:

```text
docs/qualidade/
```

com referências para:

```text
docs/deploy/
docs/seguranca/
```

Não mover automaticamente antes de revisar referências.

### Auditoria 360

```text
15-Auditoria-360-do-GereIgreja.md
```

define um processo recorrente de auditoria técnica.

Ele não é uma evidência de auditoria executada.

Portanto, seu destino conceitual é mais próximo de:

```text
docs/qualidade/
```

como procedimento recorrente, enquanto resultados concretos de auditoria pertencem a:

```text
docs/auditoria/
```

## Governança versus Auditoria

A distinção deve ser:

```text
governanca/
→ princípio transversal

qualidade/
→ procedimento recorrente de verificação

auditoria/
→ evidência de uma auditoria realmente executada
```

## Governança versus Frameworks

A relação correta é:

```text
governanca/
→ princípios gerais

frameworks/
→ autoridades normativas especializadas

famílias técnicas
→ aplicação concreta
```

Nenhum documento de Governança deve redefinir um framework oficial.

## Estratégia de saneamento

Esta pasta não deve ser apagada em massa.

Para cada documento:

1. identificar se é princípio, padrão técnico, processo ou histórico;
2. localizar a família canônica atual;
3. comparar conteúdo;
4. extrair apenas o que ainda for exclusivo;
5. atualizar referências;
6. classificar como:
   - manter;
   - consolidar;
   - mover;
   - arquivar;
   - remover;
7. somente depois retirar o arquivo antigo.

## Regra para novos documentos

Novos documentos em `docs/governanca/` devem ser raros.

Criar somente quando o conteúdo for realmente transversal e não pertencer a nenhum framework ou família especializada.

Não criar aqui:

```text
padrões de Models
padrões de Views
padrões de Templates
políticas de Segurança
checklists de Testes
checklists de Deploy
```

Esses temas já possuem destinos próprios.

## Estado da família

Classificação atual:

```text
Status: VÁLIDA, EM CONSOLIDAÇÃO
Papel: princípios e governança transversal
Conteúdo histórico: SIM
Sobreposição com famílias modernas: ALTA
Novos documentos: EXCEPCIONAIS
Extinção completa: NÃO recomendada neste momento
Redução gradual: SIM
```

## Princípio de manutenção

Governança deve definir **como a engenharia se orienta**, não repetir todos os padrões técnicos.

**Quanto mais especializada for a regra, mais especializada deve ser a sua fonte canônica.**
