# Documentação Oficial do GereIgreja

> A documentação é parte da arquitetura da plataforma e deve evoluir junto com o sistema.

Esta pasta reúne a documentação oficial do GereIgreja.

Seu objetivo é preservar conhecimento, definir autoridades por domínio, facilitar manutenção, orientar desenvolvimento e operação e registrar decisões, evidências e histórico sem misturar essas funções.

## Pontos de entrada

A navegação principal é:

```text
00-Guia-de-Documentacao.md
→ governança documental

README.md
→ apresentação e orientação inicial

INDEX.md
→ mapa global das famílias e autoridades
```

O `00-Guia-de-Documentacao.md` possui autoridade sobre **onde e como documentar**.

O `INDEX.md` mostra **onde encontrar cada domínio**.

Os READMEs das pastas mostram **como cada família está organizada**.

## Princípio central

> **Evoluir antes de criar. Consolidar antes de duplicar. Criar somente diante de uma lacuna demonstrável.**

A existência de uma pasta ou número disponível não justifica novos documentos.

## Estrutura ativa

```text
docs/
├── 00-Guia-de-Documentacao.md
├── INDEX.md
├── README.md
├── adr/
├── ai/
├── api/
├── apps/
├── arquitetura/
├── auditoria/
├── automacao/
├── backend/
├── deploy/
├── desenvolvimento/
├── design-system/
├── estrategia-digital/
├── frameworks/
├── frontend/
├── governanca/
├── infraestrutura/
├── operacoes/
├── produto/
├── qualidade/
├── relatorios/
├── release-notes/
├── seguranca/
├── sistema/
└── usuario/
```

Não fazem parte da árvore documental ativa:

```text
administrador/
design/
marketing/
templates/
ui/
```

Os conteúdos válidos dessas famílias antigas foram ou devem ser consolidados nos domínios canônicos correspondentes.

## Como a documentação se divide

```text
Frameworks
→ princípios e políticas transversais

Arquitetura
→ como o sistema se organiza

Backend / Frontend / API
→ como implementar

Design System
→ como a interface deve parecer e se comportar visualmente

Apps
→ o que os módulos fazem

Segurança / Infraestrutura / IA
→ controles e disciplinas técnicas especializadas

Qualidade / Operações / Automação / Deploy
→ como validar, operar e publicar

Usuário
→ como utilizar

Produto / Estratégia Digital
→ intenção de produto e estratégia externa

ADR / Auditoria / Relatórios / Release Notes
→ decisões, evidências, análises e histórico
```

## Frameworks da plataforma

A camada transversal oficial é:

```text
01-GDS — GereIgreja Design System
02-GAF — GereIgreja Authentication Framework
03-GSF — GereIgreja Security Framework
04-GQF — GereIgreja Quality Framework
05-GDF — GereIgreja Documentation Framework
06-GOC — GereIgreja Operations Center
```

Esses frameworks definem princípios gerais.

A aplicação detalhada permanece nas famílias especializadas.

## Famílias canônicas de engenharia

### Arquitetura

```text
docs/arquitetura/
```

Baseline atual:

```text
01–09
```

Define a estrutura sistêmica vigente.

Decisões arquiteturais com contexto, alternativas e consequências devem ser registradas em `docs/adr/`.

### Backend

```text
docs/backend/
```

Baseline:

```text
01–20
```

Define padrões Django e implementação no servidor.

### Frontend

```text
docs/frontend/
```

Baseline real:

```text
01–11
```

Define templates, layouts, componentes técnicos, assets, CSS, JavaScript, HTMX, Alpine.js e dashboards.

### API

```text
docs/api/
```

Baseline:

```text
01–14
```

Define contratos e padrões de APIs.

### Design System

```text
docs/design-system/
```

Baseline:

```text
01–19
```

É a fonte canônica da linguagem visual e UX.

```text
GDS Framework
→ Design System
→ Frontend
```

## Apps

```text
docs/apps/
```

É a fonte canônica do comportamento funcional vigente dos módulos.

Responde:

```text
o que o sistema faz
```

e não:

```text
como o código deve ser implementado
```

Documentação de Apps deve referenciar Backend, Frontend, API, Segurança e outras famílias técnicas quando necessário, sem duplicá-las.

## Segurança, Infraestrutura e IA

### Segurança

```text
docs/seguranca/
```

Baseline:

```text
01–17
```

Controles técnicos especializados alinhados ao GAF e GSF.

### Infraestrutura

```text
docs/infraestrutura/
```

Baseline:

```text
01–21
```

Ambientes, serviços, banco, observabilidade, backup, recuperação, capacidade, custos e operação da plataforma.

### Inteligência Artificial

```text
docs/ai/
```

Família GAI — GereIgreja Artificial Intelligence Engineering.

Baseline:

```text
GAI-01 ... GAI-35
```

Estado:

```text
GAI Framework 1.0
FREEZE ESTRUTURAL
```

Novos documentos `GAI-36+` exigem Gap Analysis formal.

## Operação e qualidade

### Qualidade

```text
docs/qualidade/
```

Camada operacional do GQF.

Concentra homologação, regressão, checklists, gates e critérios de aceite.

### Operações

```text
docs/operacoes/
```

Runbooks e procedimentos recorrentes alinhados ao GOC.

### Automação

```text
docs/automacao/
```

Automações operacionais ou de negócio com lifecycle próprio.

### Deploy

```text
docs/deploy/
```

Procedimentos de publicação e implantação.

Release histórica pertence a `release-notes/`.

## Usuário, produto e estratégia

### Usuário

```text
docs/usuario/
```

Guias destinados ao usuário final.

```text
apps/
→ comportamento vigente

usuario/
→ como utilizar
```

### Produto

```text
docs/produto/
```

Documentação de iniciativas de produto.

Atualmente possui escopo restrito e não deve substituir documentação funcional de Apps.

### Estratégia Digital

```text
docs/estrategia-digital/
```

Baseline atual:

```text
00–13
```

Posicionamento, conteúdo, SEO, conversão, métricas e autoridade digital.

É documentação estratégica e temporal, portanto exige revisão periódica.

## Decisões, evidências e histórico

```text
adr/
→ decisões arquiteturais

auditoria/
→ evidências de auditorias executadas

relatorios/
→ análises e diagnósticos

release-notes/
→ histórico de versões
```

Essas famílias não devem substituir documentação normativa.

## Famílias em consolidação

### Governança

```text
docs/governanca/
```

Status:

```text
VÁLIDA, EM CONSOLIDAÇÃO
```

Mantém manifestos e princípios, mas contém padrões técnicos antigos que devem ser comparados com as famílias canônicas modernas.

### Sistema

```text
docs/sistema/
```

Status:

```text
TRANSITÓRIA
NOVOS DOCUMENTOS: NÃO
```

Seu conteúdo deve ser gradualmente distribuído para as famílias corretas.

### Desenvolvimento

```text
docs/desenvolvimento/
```

Escopo pequeno para guias locais de desenvolvimento que não pertençam melhor a Backend, Frontend ou Qualidade.

## Ordem recomendada de leitura

Para quem está começando no projeto:

1. `../README.md`
2. `docs/README.md`
3. `docs/00-Guia-de-Documentacao.md`
4. `docs/INDEX.md`
5. `docs/arquitetura/README.md`
6. `docs/backend/README.md`
7. `docs/frontend/README.md`
8. `docs/apps/README.md`
9. frameworks e famílias especializadas conforme a tarefa.

Não existe uma ordem universal depois desse ponto. Segurança, API, Infraestrutura, Operações, Qualidade, IA e demais famílias devem ser consultadas conforme o domínio da mudança.

## Como navegar

Use:

```text
README desta pasta
→ orientação inicial

INDEX.md
→ mapa das famílias

README da família
→ escopo e documentos locais

documento canônico
→ regra vigente
```

O `INDEX.md` **não deve ser tratado como listagem completa de todos os arquivos**. Seu papel é mapear domínios, autoridades, baselines e pontos de entrada.

## Regra para decisões importantes

Nem toda decisão importante exige um novo arquivo.

A regra é:

```text
decisão altera regra existente
→ atualizar fonte canônica

decisão arquitetural com alternativas/consequências
→ considerar ADR

mudança entregue
→ registrar em release notes/changelog quando aplicável

evidência de verificação
→ auditoria/relatório
```

Criar um documento independente somente quando houver lifecycle e autoridade próprios.

## Filosofia de manutenção

Código e documentação devem evoluir juntos.

Documentação desatualizada é defeito.

Conhecimento histórico deve ser preservado sem ser confundido com regra vigente.

## Fontes centrais

```text
docs/00-Guia-de-Documentacao.md
docs/INDEX.md
docs/frameworks/05-GDF-GereIgreja-Documentation-Framework.md
```

## Estado

```text
README raiz de docs/
Status: OFICIAL
Papel: apresentação e orientação inicial
Autoridade de governança: GDF-00
Mapa global: INDEX.md
```
