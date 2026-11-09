Pasta: docs/

Arquivo: INDEX.md

Documento: GDF-INDEX

Framework: GDF — GereIgreja Documentation Framework

Versão: 3.0

Status: Oficial

Responsável: Equipe de Engenharia

Última atualização: Setembro de 2026

# Índice Mestre da Documentação — GereIgreja

Este arquivo é o **mapa geral de navegação e autoridade** da documentação do GereIgreja.

Ele não substitui os READMEs das famílias nem deve reproduzir todos os arquivos existentes.

## 1. Autoridade documental

A hierarquia geral é:

```text
00-Guia-de-Documentacao.md
→ autoridade máxima de governança documental

INDEX.md
→ mapa global da documentação

README.md de cada família
→ escopo, fronteiras e índice local

documentos canônicos
→ regra vigente de cada domínio

registros históricos
→ evidência do que ocorreu, sem substituir regra vigente
```

Princípio central:

> **Evoluir antes de criar. Consolidar antes de duplicar. Criar somente diante de uma lacuna demonstrável.**

A existência de número disponível, pasta existente ou documento antigo não autoriza expansão automática.

## 2. Estrutura ativa da raiz

A árvore documental ativa é:

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

Pastas removidas ou consolidadas não devem reaparecer sem nova lacuna comprovada.

## 3. Frameworks internos

Pasta:

```text
frameworks/
```

Baseline oficial:

```text
01-GDS-GereIgreja-Design-System.md
02-GAF-GereIgreja-Authentication-Framework.md
03-GSF-GereIgreja-Security-Framework.md
04-GQF-GereIgreja-Quality-Framework.md
05-GDF-GereIgreja-Documentation-Framework.md
06-GOC-GereIgreja-Operations-Center.md
```

A família está fechada em seis frameworks.

```text
07+
→ somente diante de lacuna transversal real
```

## 4. Arquitetura e engenharia

### Arquitetura — `arquitetura/`

Fonte canônica da estrutura sistêmica vigente.

Baseline:

```text
01–09
```

Abrange plataforma, Backend, Frontend, banco de dados, APIs, Segurança, Multi-Tenancy e Core.

```text
adr/
→ por que uma decisão foi tomada

arquitetura/
→ como a arquitetura está organizada hoje
```

### Backend — `backend/`

Fonte canônica dos padrões de implementação backend.

Baseline:

```text
01–20
```

Abrange Core, Apps, Models, Services, Selectors, Managers, Views, Forms, Validators, Permissions, Middlewares, Signals, Tasks, Cache, Logging, Exceptions, Testing, Performance e Code Standards.

### Frontend — `frontend/`

Fonte canônica da engenharia da interface.

Baseline real:

```text
01–11
```

Documento transitório adicional:

```text
Migracao-CSS.md
```

A expansão antiga planejada até `20` não constitui obrigação documental.

### API — `api/`

Fonte canônica dos contratos e padrões de APIs.

Baseline:

```text
01–14
```

Abrange arquitetura, endpoints, autenticação/autorização/tenant, payloads, responses, filtros, versionamento, integrações, idempotência, rate limiting, segurança, observabilidade, testes, depreciação e mapa da família.

## 5. Segurança, infraestrutura e IA

### Segurança — `seguranca/`

Família canônica de controles especializados alinhados ao GSF e ao GAF.

Baseline:

```text
01–17
```

`14-Conformidade-e-LGPD.md` está restaurado e integra novamente a baseline.

`17-Mapa-e-Indice-da-Seguranca.md` é o mapa detalhado da família.

### Infraestrutura — `infraestrutura/`

Família canônica e madura de ambientes, plataforma, banco, observabilidade, backup, disaster recovery, automação de infraestrutura, capacidade, custos, operação e prontidão.

Baseline atual:

```text
01–21
```

`20` e `21` são registros históricos de correções de migrations e não devem ser usados como padrão para novas migrations.

### Inteligência Artificial — `ai/`

Família:

```text
GAI — GereIgreja Artificial Intelligence Engineering
```

Baseline oficial:

```text
GAI-01 ... GAI-35
```

Estado:

```text
GAI Framework 1.0
FAMILY BASELINE 1.0
FREEZE ESTRUTURAL
```

`35-Mapa-Mestre-Indice-e-Governanca-Documental-da-Familia-GAI.md` é o mapa documental oficial.

```text
GAI-36+
→ exige Gap Analysis formal
```

## 6. Design e experiência

### Design System — `design-system/`

Fonte canônica da linguagem visual e UX.

Baseline:

```text
01–19
```

A relação de autoridade é:

```text
frameworks/01-GDS...
→ referência institucional

design-system/
→ especificação visual detalhada

frontend/
→ implementação técnica
```

### Pastas consolidadas

Os antigos domínios abaixo foram consolidados e não fazem mais parte da árvore ativa:

```text
design/
ui/
templates/
```

Destino canônico de seus assuntos:

```text
design-system/
frontend/
```

Não recriar essas pastas para preservar nomes históricos.

## 7. Apps — documentação funcional

Pasta:

```text
apps/
```

Esta é a camada canônica para o **comportamento funcional vigente dos módulos de negócio**.

Documentos canônicos atuais:

```text
01-Membros.md
02-Secretaria.md
03-Financeiro.md
04-Comunicacao.md
05-Departamentos.md
06-EBD.md
07-Eventos.md
09-Usuarios.md
10-Configuracoes.md
```

Decisões importantes:

```text
08-Patrimonio.md
→ NÃO criar enquanto a implementação funcional não estiver comprovada

Dashboard
→ não é app documental independente

Core
→ não é app documental independente
```

Dashboards são tratados em Design System, Frontend e nos Apps correspondentes.

Core é tratado em Backend e Arquitetura.

## 8. Qualidade, operações, automação e deploy

### Qualidade — `qualidade/`

Camada operacional do GQF.

Responsável por checklists, homologação, regressão, critérios de aceite, quality gates e validação pré/pós-release.

Não redefine a política global de qualidade.

### Operações — `operacoes/`

Runbooks e procedimentos executáveis recorrentes alinhados ao GOC.

A pasta atualmente possui forte concentração em Comunicação/WAHA.

### Automação — `automacao/`

Documentação especializada de automações operacionais reais.

Não utilizar para simples ações em lote de interface.

### Deploy — `deploy/`

Família destinada a publicação e implantação de versões.

Contém também material histórico e alguns documentos ainda sujeitos a reclassificação.

A fronteira é:

```text
deploy/
→ como publicar uma versão

operacoes/
→ como operar continuamente

qualidade/
→ o que precisa ser validado

infraestrutura/
→ plataforma onde a versão executa
```

## 9. Usuário, produto e estratégia

### Usuário — `usuario/`

Documentação destinada ao usuário final.

Inclui manuais, jornadas e guias operacionais.

```text
apps/
→ o que o sistema faz

usuario/
→ como o usuário utiliza
```

Históricos de melhoria não devem competir com os manuais vigentes.

### Produto — `produto/`

Família válida, porém restrita.

Atualmente concentrada principalmente na iniciativa do Hinário.

```text
produto/
→ intenção e evolução da iniciativa

apps/
→ comportamento vigente após estabilização

usuario/
→ uso da funcionalidade entregue

release-notes/
→ versão em que foi entregue
```

### Estratégia Digital — `estrategia-digital/`

Família estratégica ativa.

Baseline atual:

```text
00–13
```

Abrange posicionamento, arquitetura informacional do site, páginas pilares, palavras-chave, conteúdo, clusters, links internos, SEO, conversão, roadmap, KPIs e autoridade.

Natureza:

```text
VIVA / TEMPORAL
```

Documentos estratégicos precisam ser revisados periodicamente.

### Marketing

A antiga pasta:

```text
marketing/
```

foi consolidada em `estrategia-digital/` e não faz parte da árvore ativa.

Campanhas operacionais futuras somente justificam uma nova família se houver volume e responsabilidade próprios que não caibam adequadamente em `estrategia-digital/`.

## 10. Registros, evidências e histórico

### ADR — `adr/`

Registros de decisões arquiteturais.

Um ADR explica contexto, decisão e consequências.

ADRs aceitos não devem ser silenciosamente reescritos quando uma decisão muda.

### Auditoria — `auditoria/`

Evidências de verificações efetivamente realizadas.

```text
qualidade/
→ procedimento reutilizável

auditoria/
→ resultado de uma execução
```

### Relatórios — `relatorios/`

Análises, investigações, diagnósticos e relatórios executivos.

Não constituem autoridade normativa por padrão.

### Release Notes — `release-notes/`

Histórico de versões e entregas.

Release notes são registros históricos e devem ser efetivamente imutáveis, salvo correção factual ou de referência.

Não manter neste INDEX uma lista manual de todas as versões.

## 11. Famílias em consolidação

### Governança — `governanca/`

Status:

```text
VÁLIDA, EM CONSOLIDAÇÃO
```

Papel atual: princípios permanentes de engenharia, manifestos e governança transversal.

Parte dos antigos padrões técnicos foi absorvida por famílias modernas.

Documentos antigos sobre Models, Views, Templates, Permissões, Segurança, Testes e Arquitetura devem ser comparados com as fontes canônicas atuais e gradualmente consolidados.

Não expandir a família como destino padrão para novos padrões especializados.

### Sistema — `sistema/`

Status:

```text
TRANSITÓRIA
NOVOS DOCUMENTOS: NÃO
```

A pasta acumulou conteúdo técnico, funcional, operacional e histórico de diferentes períodos.

Ela deve ser usada como fonte de consolidação, não como autoridade normativa.

Possível destino final:

```text
redução gradual
→ distribuição do conteúdo válido
→ arquivamento/remoção do residual
```

### Desenvolvimento — `desenvolvimento/`

Família pequena e válida para guias locais de desenvolvimento.

Exemplo atual:

```text
Como-Rodar-Testes.md
```

Não duplicar padrões de Backend ou Qualidade.

## 12. Estado das famílias

| Família | Estado |
|---|---|
| `frameworks/` | Canônica — 01–06 |
| `arquitetura/` | Canônica — 01–09 |
| `backend/` | Canônica — 01–20 |
| `frontend/` | Canônica — 01–11 |
| `api/` | Canônica — 01–14 |
| `seguranca/` | Canônica — 01–17 |
| `infraestrutura/` | Canônica — 01–21 |
| `ai/` | Canônica — GAI-01..35, baseline congelada |
| `design-system/` | Canônica — 01–19 |
| `apps/` | Canônica funcional |
| `qualidade/` | Válida — camada operacional |
| `operacoes/` | Válida — runbooks |
| `automacao/` | Válida — especializada |
| `deploy/` | Válida — com conteúdo ainda em saneamento |
| `usuario/` | Válida — orientação ao usuário |
| `produto/` | Válida, mas restrita |
| `estrategia-digital/` | Válida e estratégica — 00–13 |
| `adr/` | Válida — série decisória |
| `auditoria/` | Válida — evidencial |
| `relatorios/` | Válida — analítica/histórica |
| `release-notes/` | Válida — histórica |
| `governanca/` | Válida, em consolidação |
| `sistema/` | Transitória |
| `desenvolvimento/` | Válida, escopo pequeno |

## 13. Caminhos retirados da árvore ativa

Não são famílias ativas:

```text
administrador/
design/
marketing/
templates/
ui/
```

`administrador/` não foi encontrado na árvore documental vigente.

Os demais foram removidos ou consolidados em famílias atuais.

Referências históricas a esses caminhos podem permanecer em releases e changelogs quando necessário para preservar contexto, desde que não sejam apresentadas como caminhos vigentes.

## 14. Prioridades documentais vigentes

A prioridade não é criar novas famílias ou preencher numeração.

A sequência recomendada é:

1. manter `00-Guia-de-Documentacao.md`, `INDEX.md` e READMEs sincronizados;
2. concluir a consolidação dos padrões técnicos antigos de `governanca/`;
3. continuar a redução controlada de `sistema/`;
4. reclassificar conteúdo residual de `deploy/`, `operacoes/`, `qualidade/` e `relatorios/` quando houver sobreposição comprovada;
5. manter manuais de `usuario/` sincronizados com o produto real;
6. revisar periodicamente `estrategia-digital/` por sua natureza temporal;
7. auditar referências cruzadas das famílias maduras;
8. não expandir baselines maduras sem Gap Analysis.

## 15. Regra para manutenção deste índice

O `INDEX.md` deve registrar famílias ativas, autoridade de cada domínio, baselines importantes, estado documental, pontos de entrada, famílias transitórias, caminhos consolidados e riscos relevantes.

Listagens completas pertencem aos READMEs e mapas locais.

Sempre que uma pasta for criada, removida, renomeada ou tiver sua autoridade alterada, este índice deve ser revisado.

## Status

**Arquivo:** `docs/INDEX.md`  
**Documento:** `GDF-INDEX`  
**Versão:** `3.0`  
**Status:** **OFICIAL**
