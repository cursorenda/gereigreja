# ADR — Architecture Decision Records

ADR  
↓  
Decisões arquiteturais relevantes, duradouras e rastreáveis do GereIgreja.

Esta pasta registra decisões que alteram ou consolidam a arquitetura da plataforma.

Um ADR não é documentação funcional comum, plano de implementação, relatório ou release note. Seu objetivo é preservar **por que uma decisão arquitetural foi tomada**, quais alternativas foram consideradas e quais consequências passam a orientar o sistema.

## Finalidade da pasta

- registrar decisões arquiteturais relevantes;
- preservar contexto e motivação;
- documentar alternativas rejeitadas;
- explicitar consequências e restrições;
- evitar que decisões importantes existam apenas em código, chats ou memória da equipe;
- permitir rastrear mudanças arquiteturais ao longo do tempo.

## Quando criar um ADR

Criar um ADR somente quando houver uma decisão com impacto arquitetural relevante e duradouro.

Exemplos:

- nova fronteira entre domínios;
- mudança de modelo de autorização;
- decisão estrutural de multi-tenancy;
- introdução de uma nova abstração central;
- alteração relevante de dependências entre módulos;
- decisão de persistência ou integração difícil de reverter;
- substituição de uma abordagem arquitetural anterior.

Não criar ADR para:

- correção de bug;
- pequena refatoração;
- mudança puramente visual;
- atualização de texto;
- tarefa operacional;
- implementação já determinada por padrão existente;
- decisão local sem impacto arquitetural.

## Estrutura mínima de um ADR

Todo ADR deve registrar, no mínimo:

```text
Contexto
Decisão
Alternativas consideradas
Consequências
Status
Data
```

Quando aplicável, também registrar:

- impactos de segurança;
- impactos de multi-tenancy;
- compatibilidade;
- migração;
- riscos;
- controles obrigatórios;
- documentos relacionados.

## Status

Utilizar status explícito.

Valores recomendados:

```text
Proposto
Aceito
Rejeitado
Substituído
Obsoleto
```

### Proposto

Decisão ainda em avaliação.

### Aceito

Decisão aprovada e vigente.

### Rejeitado

Proposta analisada, mas não adotada.

### Substituído

Decisão anteriormente aceita, mas posteriormente substituída por outro ADR.

Quando possível, indicar:

```text
Substituído por: ADR-XX
```

### Obsoleto

Decisão que perdeu validade por mudança estrutural, sem necessariamente existir substituição direta.

## Imutabilidade

ADR aceito é um registro histórico.

Não reescrever silenciosamente um ADR antigo para refletir uma arquitetura nova.

Se a decisão mudar de forma relevante:

```text
ADR antigo
→ marcar como Substituído

novo ADR
→ registrar a nova decisão
```

Correções de typo, links ou esclarecimentos que não alterem a decisão são permitidos.

## Relação com Arquitetura

A relação correta é:

```text
ADR
↓
registra por que a decisão foi tomada

docs/arquitetura/
↓
documenta a arquitetura vigente
```

Quando um ADR for aceito, a documentação arquitetural correspondente deve refletir a decisão.

O ADR não substitui a documentação arquitetural canônica.

## Relação com Apps

`docs/apps/` descreve comportamento funcional vigente.

Um ADR pode explicar por que determinada estrutura de domínio foi escolhida, mas não deve substituir a documentação funcional do app.

Exemplo atual:

```text
ADR-01
↓
explica a decisão sobre DepartamentoVinculo

docs/apps/05-Departamentos.md
↓
documenta o comportamento funcional vigente
```

## Relação com Relatórios

Relatórios podem analisar possibilidades e recomendar mudanças.

ADR registra a decisão efetivamente tomada.

```text
relatorio/
→ analisa

ADR
→ decide

arquitetura/
→ documenta o estado vigente
```

## Relação com Release Notes

Release notes registram quando uma mudança foi entregue.

ADR registra por que a mudança arquitetural foi escolhida.

Não duplicar o conteúdo completo entre as duas famílias.

## Nomenclatura

Utilizar:

```text
NN-Nome-da-Decisao.md
```

Exemplo:

```text
01-DepartamentoVinculo-Historico-e-Cargo.md
```

A numeração é sequencial e não deve ser reutilizada.

O identificador interno correspondente deve seguir:

```text
ADR-01
ADR-02
ADR-03
...
```

## Índice atual

| ADR | Documento | Status |
|---|---|---|
| ADR-01 | [01-DepartamentoVinculo-Historico-e-Cargo.md](01-DepartamentoVinculo-Historico-e-Cargo.md) | Aceito |

## ADR-01 — DepartamentoVinculo, histórico e cargo único

O ADR atual resolve uma decisão arquitetural concreta relacionada aos departamentos locais.

Ele estabelece que:

- `DepartamentoVinculo` representa o vínculo de uma pessoa com o departamento;
- organização departamental não deve ser usada como mecanismo implícito de autorização;
- histórico deve ser preservado por datas de início e fim;
- o vínculo permanece subordinado ao departamento local.

A decisão já é referenciada pela documentação funcional de Departamentos e por documentação relacionada ao Financeiro.

Isso demonstra uso adequado da família ADR: a decisão é registrada uma vez e as demais famílias a referenciam.

## Regra de autoridade

Quando houver divergência:

```text
ADR aceito
→ autoridade sobre a decisão histórica

arquitetura vigente
→ autoridade sobre o estado estrutural atual

app canônico
→ autoridade sobre comportamento funcional atual
```

Se a arquitetura vigente contrariar um ADR aceito, deve existir explicação documental — normalmente um ADR posterior substituindo-o.

## Regra para novo ADR

Antes de criar:

1. confirmar que existe decisão arquitetural real;
2. verificar se não é apenas implementação de padrão já estabelecido;
3. registrar contexto;
4. listar alternativas relevantes;
5. justificar a opção escolhida;
6. documentar consequências positivas e negativas;
7. registrar impactos de segurança e multi-tenancy quando aplicável;
8. definir status;
9. atualizar este README;
10. atualizar a documentação arquitetural após aceitação.

## Estado da família

A pasta possui atualmente um ADR formal e corretamente estruturado.

Isso **não representa lacuna**.

O objetivo não é aumentar a quantidade de ADRs.

Novos registros devem surgir apenas quando decisões arquiteturais relevantes realmente ocorrerem.

## Princípio de manutenção

ADR existe para preservar decisões difíceis de reconstruir depois.

**Se a equipe precisaria perguntar “por que fizemos assim?” daqui a um ano, a decisão pode justificar um ADR.**
