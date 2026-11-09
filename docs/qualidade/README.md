# Qualidade — Procedimentos e Evidências

Qualidade  
↓  
Como verificar se o GereIgreja atende aos critérios definidos pelo GQF.

Esta pasta reúne documentação operacional de qualidade.

O framework de qualidade oficial permanece em:

- `docs/frameworks/04-GQF-GereIgreja-Quality-Framework.md`

A pasta `docs/qualidade/` não redefine o GQF. Ela registra como os critérios de qualidade são aplicados, verificados e evidenciados na prática.

## Finalidade da pasta

- definir gates objetivos de aprovação e reprovação;
- manter checklists de homologação e release;
- documentar procedimentos de teste;
- registrar critérios de aceite;
- documentar verificações manuais quando necessárias;
- organizar evidências de qualidade reutilizáveis;
- apontar testes automatizados e suites relevantes sem duplicar sua implementação.

## Fronteira com outras famílias

### `docs/frameworks/`

Define princípios e políticas de qualidade por meio do GQF.

### `docs/qualidade/`

Define procedimentos concretos de validação.

Exemplos:

- checklist pré-release;
- roteiro de homologação;
- matriz de critérios de aceite;
- procedimento de regressão;
- gate mínimo para produção.

### `docs/auditoria/`

Registra evidências e auditorias históricas.

Uma auditoria pontual, relatório de achados ou fotografia de uma versão não deve permanecer em `qualidade/` apenas porque mede qualidade.

### `docs/backend/` e código

Documentam e implementam testes automatizados, arquitetura de testes, ferramentas e padrões técnicos.

`qualidade/` pode referenciar esses testes, mas não deve duplicar código ou convenções de engenharia.

### `docs/deploy/`

Documenta como publicar.

`qualidade/` define o que precisa estar validado antes da publicação.

## Tipos de documento adequados

São adequados nesta pasta:

- checklist de release;
- checklist de homologação;
- critérios de aceite;
- roteiro de testes manuais;
- plano de regressão;
- matriz de qualidade;
- gate de release;
- procedimento de validação pós-release;
- checklist específico de integração externa.

## Tipos que não devem ser criados aqui automaticamente

Evitar usar esta pasta como destino genérico para:

- framework ou política global de qualidade;
- documentação completa de CI/CD;
- arquitetura de testes;
- relatório histórico de auditoria;
- post-mortem;
- documentação de deploy;
- boas práticas genéricas de programação.

Esses assuntos devem permanecer nas famílias responsáveis e apenas ser referenciados quando necessário.

## Regra para criar um novo documento

Antes de criar um arquivo em `docs/qualidade/`:

1. confirme que existe uma necessidade de validação concreta;
2. verifique se o critério já está coberto pelo GQF ou por checklist existente;
3. identifique claramente o objeto da validação;
4. defina critérios objetivos de aprovação e reprovação;
5. indique responsáveis ou perfis envolvidos quando relevante;
6. informe pré-condições;
7. liste evidências esperadas;
8. referencie testes automatizados relacionados;
9. diferencie gate obrigatório de recomendação;
10. atualize este README e, quando necessário, `docs/INDEX.md`.

## Padrão de nomenclatura

Para documentos específicos de módulo:

```text
MODULO_TEMA_TIPO.md
```

Exemplos:

```text
COMUNICACAO_CHECKLIST_RELEASE_WAHA.md
FINANCEIRO_CHECKLIST_HOMOLOGACAO.md
EBD_ROTEIRO_REGRESSAO.md
```

Para documentos transversais:

```text
TEMA_TIPO.md
```

Exemplos:

```text
RELEASE_GATE.md
HOMOLOGACAO_CHECKLIST.md
REGRESSAO_PROCEDIMENTO.md
```

A numeração sequencial não é obrigatória nesta pasta, porque muitos documentos possuem natureza operacional e específica de módulo.

## Índice atual

| Documento | Tipo | Escopo | Status |
|---|---|---|---|
| [COMUNICACAO_CHECKLIST_RELEASE_WAHA.md](COMUNICACAO_CHECKLIST_RELEASE_WAHA.md) | Checklist de release | Comunicação / WAHA | Oficial |

## Situação atual da pasta

A pasta ainda possui cobertura documental limitada.

Isso não significa que devam ser criados vários arquivos preventivamente.

Novos documentos devem surgir a partir de necessidades reais de homologação, release, regressão ou controle de qualidade já identificadas no projeto.

A prioridade é consolidar procedimentos que hoje estejam dispersos em releases, runbooks ou documentação de sistema quando eles representarem um processo de qualidade recorrente.

## Relação com o GQF

O GQF é a autoridade normativa.

Esta pasta é a camada operacional.

```text
GQF
↓
define o que qualidade exige

docs/qualidade/
↓
define como verificar

testes / homologação / evidências
↓
demonstram o resultado
```

Nenhum arquivo desta pasta deve criar política global conflitante com o GQF.

## Princípio de manutenção

Qualidade deve ser verificável.

Todo checklist ou gate deve permitir responder objetivamente:

```text
O que será validado?
Como será validado?
Qual resultado aprova?
Qual resultado reprova?
Que evidência comprova a validação?
```

Se essas respostas não estiverem claras, o documento ainda não define um processo de qualidade suficientemente operacional.
