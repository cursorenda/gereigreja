# Operações — Runbooks e Procedimentos Operacionais

Operações  
↓  
Como manter serviços e integrações do GereIgreja funcionando no dia a dia.

Esta pasta reúne documentação operacional concreta.

O framework operacional oficial permanece em:

- `docs/frameworks/06-GOC-GereIgreja-Operations-Center.md`

A pasta `docs/operacoes/` não redefine o GOC. Ela contém runbooks, procedimentos de manutenção, rotação, monitoramento e resposta operacional.

## Finalidade da pasta

- manter runbooks executáveis;
- documentar procedimentos recorrentes de operação;
- registrar rotinas de manutenção;
- orientar diagnóstico e recuperação;
- documentar rotação de credenciais operacionais;
- organizar procedimentos específicos de integrações externas;
- reduzir dependência de conhecimento informal.

## Fronteira com outras famílias

### `docs/frameworks/`

Define princípios e política operacional por meio do GOC.

### `docs/operacoes/`

Define o procedimento concreto.

Exemplos:

- verificar saúde de uma integração;
- reestabelecer sessão;
- rotacionar API Key;
- diagnosticar falha operacional;
- executar rotina recorrente;
- recuperar serviço degradado.

### `docs/deploy/`

Define processo de publicação, configuração de ambiente e rollback de release.

Um checklist cujo foco principal é promover uma versão entre ambientes pertence preferencialmente a `deploy/`.

### `docs/qualidade/`

Define critérios de aprovação, homologação e gates.

Um checklist cujo objetivo é decidir se uma release pode ser aprovada pertence preferencialmente a `qualidade/`.

### `docs/seguranca/`

Define política de segurança e gestão de incidentes.

Um procedimento operacional de rotação de credencial pode permanecer aqui quando for um runbook executável, desde que respeite o GSF.

### `docs/auditoria/` e `docs/relatorios/`

Registram evidências e análises históricas.

Runbooks devem descrever procedimentos reutilizáveis, não apenas relatar o que aconteceu em uma ocasião passada.

## Regra para criar um novo documento

Antes de criar um arquivo em `docs/operacoes/`:

1. confirme que a atividade é operacional e recorrente;
2. verifique se já existe runbook equivalente;
3. defina pré-condições;
4. indique o serviço, integração ou módulo afetado;
5. descreva passos executáveis na ordem correta;
6. informe validações de sucesso;
7. registre sintomas e falhas conhecidas quando útil;
8. inclua rollback ou recuperação quando aplicável;
9. indique cuidados de segurança;
10. referencie documentação de deploy, qualidade e segurança sem duplicá-la.

## Padrão de nomenclatura

Para procedimentos específicos de módulo ou integração:

```text
MODULO_TEMA_TIPO.md
```

Exemplos:

```text
COMUNICACAO_WAHA_RUNBOOK.md
COMUNICACAO_ROTACAO_API_KEY_WAHA.md
```

Para procedimentos transversais:

```text
TEMA_TIPO.md
```

Exemplos:

```text
BACKUP_RUNBOOK.md
INCIDENTE_RUNBOOK.md
```

O nome deve refletir a finalidade operacional do documento.

## Índice atual

| Documento | Classificação |
|---|---|
| [COMUNICACAO_WAHA_RUNBOOK.md](COMUNICACAO_WAHA_RUNBOOK.md) | Runbook operacional da integração WAHA |
| [ROTACAO_API_KEY_WAHA.md](ROTACAO_API_KEY_WAHA.md) | Procedimento de rotação de credencial WAHA |
| [PLANO_AUTOMACOES_COMUNICACAO.md](PLANO_AUTOMACOES_COMUNICACAO.md) | Plano/evolução operacional — revisar classificação |
| [COMUNICACAO_DEPLOY_CHECKLIST.md](COMUNICACAO_DEPLOY_CHECKLIST.md) | Checklist de deploy — revisar destino |
| `DEPLOY_COMUNICACAO_CHECKLIST.md` | Duplicata exata do checklist acima — remover após validação local |

## Duplicidade identificada

Foram encontrados dois arquivos com conteúdo idêntico:

```text
COMUNICACAO_DEPLOY_CHECKLIST.md
DEPLOY_COMUNICACAO_CHECKLIST.md
```

Eles não devem coexistir como fontes independentes.

A recomendação é manter:

```text
COMUNICACAO_DEPLOY_CHECKLIST.md
```

porque segue o padrão já adotado no README antigo:

```text
MODULO_TEMA_TIPO.md
```

e remover a duplicata:

```text
DEPLOY_COMUNICACAO_CHECKLIST.md
```

somente após confirmar que nenhum link, automação ou documentação externa depende do nome antigo.

## Checklist de deploy de Comunicação

O conteúdo desse checklist mistura:

- pré-deploy;
- configuração de ambiente;
- staging;
- validação de segurança;
- pós-deploy;
- rollback.

Por natureza, ele está mais próximo de `docs/deploy/` do que de Operações.

Entretanto, não deve ser movido automaticamente enquanto não forem revisadas as referências existentes.

Até essa revisão, manter apenas uma cópia canônica.

## Plano de Automações de Comunicação

`PLANO_AUTOMACOES_COMUNICACAO.md` possui natureza de planejamento/evolução, não de runbook puro.

Deve permanecer temporariamente até ser avaliado contra:

- `docs/automacao/`;
- `docs/apps/04-Comunicacao.md`;
- documentação de roadmap/evolução.

Não criar outro documento equivalente antes dessa classificação.

## Relação com o GOC

O GOC é a autoridade normativa da operação.

Esta pasta é a camada executável.

```text
GOC
↓
define como a operação deve ser governada

docs/operacoes/
↓
define procedimentos concretos

logs / monitoramento / execução
↓
demonstram o estado operacional
```

## Estado atual

A pasta possui conteúdo operacional real, porém concentrado quase totalmente em Comunicação/WAHA.

Isso não justifica criar runbooks genéricos para todos os módulos.

Novos runbooks devem surgir apenas quando existir uma rotina operacional recorrente, um risco relevante ou uma necessidade real de suporte.

## Princípio de manutenção

Um runbook deve permitir que outra pessoa execute a operação com segurança sem depender do autor original.

Todo procedimento operacional deve responder:

```text
Quando executar?
Quais pré-condições existem?
Quais passos seguir?
Como saber se funcionou?
O que fazer se falhar?
Como voltar ao estado seguro?
```

Se essas respostas não estiverem claras, o documento ainda não é um runbook operacional suficiente.
