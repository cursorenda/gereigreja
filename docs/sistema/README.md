# Sistema — Documentação Técnica Legada e em Reclassificação

Sistema  
↓  
Conteúdo técnico histórico que ainda não foi completamente redistribuído para as famílias canônicas do GereIgreja.

Esta pasta não deve ser usada como destino padrão para nova documentação.

Ela reúne documentos técnicos acumulados ao longo da evolução do projeto, muitos deles criados antes da atual arquitetura documental.

Por isso, `docs/sistema/` deve ser tratada como uma área **transitória de consolidação e reclassificação**, não como uma família normativa.

## Finalidade atual da pasta

- preservar documentação técnica histórica ainda útil;
- impedir perda de contexto durante a reorganização documental;
- permitir reclassificação gradual para famílias canônicas;
- manter rastreabilidade de decisões e implementações antigas;
- evitar movimentações em massa sem revisão de referências.

## Regra principal

Não criar novos documentos em:

```text
docs/sistema/
```

salvo decisão explícita de governança documental.

Novo conteúdo deve ser criado diretamente na família responsável.

Exemplos:

```text
apps/
backend/
frontend/
arquitetura/
seguranca/
qualidade/
operacoes/
automacao/
relatorios/
auditoria/
deploy/
desenvolvimento/
```

## Por que a pasta não pode continuar como “documentação técnica geral”

O README histórico declarava que esta pasta continha “toda a documentação técnica do sistema”.

Essa definição não é mais válida.

Hoje o GereIgreja possui famílias especializadas e canônicas.

Manter `sistema/` como repositório técnico geral recriaria uma pasta-curinga e provocaria:

- duplicação;
- conflito entre fontes;
- regras funcionais fora de `apps/`;
- runbooks fora de `operacoes/`;
- auditorias fora de `auditoria/`;
- análises fora de `relatorios/`;
- documentação de testes fora de `desenvolvimento/` e `qualidade/`;
- decisões técnicas fora de arquitetura/backend.

## Estado atual

A pasta contém muitos documentos de naturezas diferentes.

Entre eles foram identificados exemplos como:

```text
SELETOR_IGREJA.md
CARGOS_SISTEMA.md
FINANCEIRO_FASE3A_SELECTORS_SERVICES.md
FINANCEIRO_FASE3B_POLITICA_CATEGORIAS.md
FINANCEIRO_FASE3C_FLUXO_SERVICES.md
FINANCEIRO_FASE4A_FILTRO_FUNDO_KPIS.md
FINANCEIRO_FASE4B_GESTAO_DEPARTAMENTOS_PREMIUM.md
FINANCEIRO_FUNDOS_DEPARTAMENTAIS_FASE1.md
FINANCEIRO_FUNDOS_DEPARTAMENTAIS_FASE2.md
ESCOLA_DOMINICAL_CONFIG_LOCAL_IGREJA.md
ESCOLA_DOMINICAL_HOMOLOGACAO_CONFIG_LOCAL_IGREJA.md
ESCOLA_DOMINICAL_GOVERNANCA_PERIODO.md
ESCOLA_DOMINICAL_ROADMAP_PREMIUM.md
EBD_RUNBOOK_FASE1.md
EBD_RUNBOOK_OPERACAO_SUPORTE.md
README_TESTS.md
AUDITORIA_PERMISSOES_PROFESSOR_EBD.md
```

Isso demonstra que a pasta acumula:

- regras funcionais;
- arquitetura técnica;
- planejamento;
- homologação;
- operação;
- auditoria;
- testes;
- histórico de implementação.

Esses conteúdos não pertencem à mesma família documental.

## Estratégia de saneamento

A reorganização deve ser gradual.

Para cada arquivo:

1. identificar a natureza real;
2. localizar a família canônica correspondente;
3. verificar se o conteúdo já foi consolidado em documento atual;
4. buscar referências ao caminho antigo;
5. decidir entre:
   - mover;
   - consolidar;
   - arquivar;
   - remover por duplicação;
6. atualizar links;
7. somente então retirar o arquivo de `sistema/`.

Não fazer movimentação em massa por nome de arquivo.

## Critério de decisão

### Mover

Quando o documento continua útil e não existe equivalente canônico.

### Consolidar

Quando possui informação útil que deve ser incorporada a um documento canônico já existente.

### Arquivar

Quando seu valor é principalmente histórico.

### Remover

Quando o conteúdo está completamente duplicado, superado e sem valor histórico relevante.

## Exemplos de classificação

### `SELETOR_IGREJA.md`

Trata de contexto de igreja/tenant e seleção ativa.

Candidatos:

```text
arquitetura/
backend/
```

dependendo de sua ênfase real.

Não mover apenas pelo título.

### `CARGOS_SISTEMA.md`

Deve ser comparado com:

```text
docs/apps/09-Usuarios.md
docs/apps/10-Configuracoes.md
docs/seguranca/
```

antes de decidir seu destino.

### Documentos `FINANCEIRO_*`

Devem ser comparados primeiro com:

```text
docs/apps/03-Financeiro.md
docs/backend/
docs/relatorios/
```

Fases antigas podem ser históricas mesmo quando parte do conteúdo virou implementação atual.

### Documentos `ESCOLA_DOMINICAL_*` e `EBD_*`

Devem ser comparados com:

```text
docs/apps/06-EBD.md
docs/operacoes/
docs/qualidade/
docs/relatorios/
```

Runbooks pertencem conceitualmente a `operacoes/`.

Homologações recorrentes pertencem a `qualidade/`.

Roadmaps e fases antigas tendem a histórico/relatórios.

### `README_TESTS.md`

Não deve competir com:

```text
docs/desenvolvimento/Como-Rodar-Testes.md
```

Se o conteúdo útil já estiver consolidado, o arquivo deve ser removido ou arquivado, não mantido como segunda fonte.

## README histórico

O antigo `docs/sistema/README.md` definia regras gerais de documentação, nomenclatura, criação de arquivos e estrutura global de `docs/`.

Essa responsabilidade agora pertence a:

```text
docs/00-Guia-de-Documentacao.md
docs/INDEX.md
```

Portanto, este README não deve repetir governança global.

## Fonte de verdade documental

A hierarquia correta é:

```text
00-Guia-de-Documentacao.md
↓
define governança documental

INDEX.md
↓
mapeia as famílias

família especializada
↓
mantém documentação canônica

sistema/
↓
preserva temporariamente conteúdo legado ainda em saneamento
```

## Proibição de nova documentação genérica

Não utilizar nomes como:

```text
NOVO_SISTEMA.md
MELHORIAS_SISTEMA.md
IMPLEMENTACAO_SISTEMA.md
DOCUMENTACAO_GERAL.md
```

para novos conteúdos.

O domínio e a finalidade devem ser identificados antes da criação.

## Quando esta pasta poderá ser removida

`docs/sistema/` poderá ser extinta quando:

- todos os arquivos forem classificados;
- conteúdos canônicos tiverem sido consolidados;
- documentos históricos tiverem destino definido;
- links tiverem sido atualizados;
- não houver dependência documental legítima do caminho.

Não há obrigação de manter a pasta permanentemente.

## Estado de governança

Classificação atual:

```text
Status: TRANSITÓRIA
Novos documentos: NÃO
Conteúdo existente: revisar gradualmente
Autoridade normativa: NÃO
Possível extinção futura: SIM
```

## Princípio de manutenção

`docs/sistema/` não deve crescer.

A métrica de sucesso desta pasta é diminuir de tamanho de forma segura até que cada documento tenha um destino coerente.

**Consolidar antes de duplicar. Reclassificar antes de criar. Remover apenas depois de preservar o que ainda tem valor.**
