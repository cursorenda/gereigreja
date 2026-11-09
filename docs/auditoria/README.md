# Auditoria — Evidências e Registros de Verificação

Auditoria  
↓  
O que foi verificado, registrado ou evidenciado em processos formais de controle do GereIgreja.

Esta pasta reúne documentos de auditoria e evidências formais.

Ela não deve ser confundida com:

- `docs/relatorios/` — análises e diagnósticos gerais;
- `docs/qualidade/` — procedimentos recorrentes de validação;
- `docs/seguranca/` — políticas e controles de segurança;
- `docs/apps/` — regras funcionais canônicas;
- `docs/release-notes/` — histórico de releases.

## Finalidade da pasta

- preservar evidências de auditoria;
- registrar resultados de verificações formais;
- manter resumos e checklists finais de auditorias executadas;
- documentar trilhas de implementação quando o objetivo principal for controle e rastreabilidade;
- registrar escopo, período, achados e conclusão de uma auditoria;
- permitir comprovar que determinada verificação ocorreu.

## O que caracteriza um documento de auditoria

Um documento pertence a esta pasta quando responde principalmente:

```text
O que foi auditado?
Em qual período?
Com quais critérios?
Que evidências foram verificadas?
Quais achados foram encontrados?
Qual foi a conclusão?
```

Nem todo documento que usa a palavra “auditoria” pertence automaticamente aqui.

Por exemplo:

- política de auditoria → `seguranca/`;
- implementação de logging → documentação técnica;
- relatório de análise comum → `relatorios/`;
- checklist recorrente → `qualidade/`;
- evidência final de uma auditoria executada → `auditoria/`.

## Índice atual

| Documento | Natureza | Situação |
|---|---|---|
| [PASSO_4_AUDITORIA_RESUMO.md](PASSO_4_AUDITORIA_RESUMO.md) | Resumo de implementação da trilha de auditoria de permissões | Histórico técnico / evidência |
| [PASSO_4_CHECKLIST_FINAL.md](PASSO_4_CHECKLIST_FINAL.md) | Checklist final do Passo 4 | Evidência de conclusão |
| [PASSO_4_RELATORIO_FINAL.md](PASSO_4_RELATORIO_FINAL.md) | Relatório final do Passo 4 | Evidência consolidada |

## Situação da família

A pasta atualmente representa um **conjunto histórico específico**, relacionado ao “Passo 4” da trilha de auditoria de permissões.

Portanto, ela ainda não constitui uma biblioteca ampla de auditorias do GereIgreja.

Isso é importante para evitar interpretar os três documentos atuais como política geral de auditoria.

## PASSO_4_AUDITORIA_RESUMO.md

O documento registra a implementação de recursos como:

- logging automático de alterações de grupos;
- registro de acessos negados;
- login/logout e sessões;
- middleware de auditoria;
- exportação CSV;
- análise de atividades suspeitas;
- acumulação de permissões;
- dashboards e relatórios.

Também registra como “completo” o Passo 4 em abril de 2026.

Esse status deve ser interpretado como conclusão declarada naquele momento.

Antes de reutilizar detalhes técnicos como verdade atual, deve-se validar o código vigente.

## Relação com Segurança

A trilha de auditoria de permissões é um controle de segurança.

A política e os requisitos gerais pertencem a:

```text
docs/seguranca/
```

Esta pasta deve preservar a evidência histórica de implementação/verificação.

A relação correta é:

```text
GSF / Segurança
↓
define o controle esperado

Implementação
↓
executa o controle

Auditoria
↓
registra evidência da verificação
```

## Relação com Relatórios

`docs/relatorios/` e `docs/auditoria/` são famílias próximas, mas com finalidades diferentes.

### Relatórios

Podem conter:

- análise exploratória;
- diagnóstico;
- recomendação;
- comparação;
- estudo técnico.

### Auditoria

Deve conter:

- escopo formal;
- critérios;
- evidências;
- verificação;
- achados;
- conclusão;
- status da auditoria.

Quando um documento apenas analisa um problema, o destino mais provável é `relatorios/`.

Quando registra formalmente o resultado de uma verificação, `auditoria/` é mais apropriado.

## Relação com Qualidade

Checklist de auditoria executada pode permanecer aqui como evidência.

Checklist reutilizável para futuras validações deve ficar em:

```text
docs/qualidade/
```

Assim:

```text
Checklist reutilizável
→ qualidade/

Checklist preenchido / evidência final
→ auditoria/
```

## Regra para criar um novo documento de auditoria

Antes de criar um arquivo nesta pasta:

1. defina o objeto auditado;
2. registre período ou data;
3. descreva o escopo;
4. liste critérios utilizados;
5. identifique evidências verificadas;
6. diferencie achado de recomendação;
7. registre conclusão;
8. informe limitações;
9. aponte ações corretivas quando houver;
10. referencie a política ou framework que motivou a auditoria.

## Nomenclatura

Não é obrigatório usar numeração sequencial.

Nomes devem refletir:

```text
ESCOPO + TIPO + PERÍODO
```

Exemplos:

```text
AUDITORIA_PERMISSOES_2026-Q3.md
AUDITORIA_MULTI_TENANT_2026.md
CHECKLIST_AUDITORIA_SEGURANCA_2026-09.md
```

Evitar títulos genéricos como:

```text
AUDITORIA_FINAL.md
RELATORIO_FINAL.md
CHECKLIST_FINAL.md
```

sem contexto suficiente.

Os arquivos atuais `PASSO_4_*` são históricos e não precisam ser renomeados retroativamente sem necessidade.

## Família contínua

`docs/auditoria/` é uma família **contínua**.

Não existe um número final de documentos.

Novos registros devem surgir apenas quando houver uma auditoria real executada.

## Retenção histórica

Auditorias antigas podem permanecer mesmo quando o sistema evolui.

Seu valor está em demonstrar:

- o estado observado naquele momento;
- o que foi verificado;
- o que foi considerado concluído;
- quais riscos existiam;
- quais ações foram tomadas.

Entretanto, um documento antigo não deve ser utilizado como especificação vigente sem validação.

## Possíveis reclassificações futuras

Alguns documentos espalhados pelo repositório podem ser candidatos a esta pasta se representarem evidência formal de auditoria.

Exemplos possíveis:

- auditorias pontuais de permissões;
- evidências de conformidade;
- verificações de isolamento multi-tenant;
- auditorias de segurança executadas;
- resultados formais de revisão.

Mas a reclassificação só deve ocorrer após análise individual.

## Princípio de manutenção

Auditoria deve preservar evidência, contexto e conclusão.

Todo documento desta pasta deve permitir responder:

```text
Quem ou o que foi auditado?
Quando?
Com quais critérios?
Que evidências foram verificadas?
Quais achados foram encontrados?
O que foi concluído?
Qual documento canônico representa o estado atual?
```

Se essas respostas não estiverem claras, o documento pode ser apenas um relatório ou nota histórica, não uma auditoria formal.
