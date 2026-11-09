Pasta: docs/

Arquivo: 00-Guia-de-Documentacao.md

Documento: GDF-00

Framework: GDF — GereIgreja Documentation Framework

Versão: 1.2

Status: Oficial

Responsável: Equipe de Engenharia

Última atualização: Setembro de 2026

# 00 — Guia Oficial da Documentação

> A documentação do GereIgreja é parte da arquitetura da plataforma e deve possuir domínio, autoridade, finalidade e ciclo de vida claramente definidos.

# 1. Objetivo

Este documento estabelece as regras oficiais para criação, organização, manutenção, classificação e evolução da documentação do GereIgreja.

Seu objetivo é:

- preservar conhecimento relevante;
- reduzir duplicidade e contradições;
- definir autoridade documental por domínio;
- separar conteúdo normativo, técnico, funcional, operacional, histórico e evidencial;
- tornar a documentação navegável e sustentável;
- impedir criação de arquivos apenas para preencher sequências numéricas.

Este documento possui prioridade sobre qualquer outro documento cujo objeto seja a organização da própria documentação.

Quando houver conflito entre este guia e documentação especializada:

```text
GDF-00
→ define onde e como documentar

framework/documento especializado
→ define a regra técnica do domínio
```

# 2. Princípios de Governança Documental

A documentação deverá ser:

- organizada;
- objetiva;
- reutilizável;
- consistente;
- rastreável;
- evolutiva;
- navegável;
- orientada por domínio;
- proporcional à necessidade real;
- mantida junto com a evolução do sistema.

Todo documento deve permitir identificar:

- por que existe;
- a qual domínio pertence;
- qual problema resolve;
- quando deve ser utilizado;
- qual sua autoridade;
- quem o mantém;
- quais documentos o complementam.

## 2.1 Regra de necessidade

Um novo arquivo `.md` somente deverá ser criado quando existir **lacuna documental demonstrável**.

A existência de número disponível, pasta vazia ou padrão sequencial incompleto **não constitui justificativa** para criação.

## 2.2 Evoluir antes de criar

Antes de criar novo arquivo, considerar nesta ordem:

1. atualizar documento existente;
2. incluir seção em documento canônico;
3. criar referência cruzada;
4. reclassificar conteúdo existente;
5. consolidar duplicidade;
6. somente então criar novo documento.

Princípio oficial:

> **Evoluir antes de criar. Consolidar antes de duplicar. Criar somente diante de uma lacuna demonstrável.**

## 2.3 Documento canônico

Quando vários documentos tratarem do mesmo assunto, deverá existir uma fonte canônica clara.

Documentos especializados podem complementar a fonte canônica, mas não devem redefinir silenciosamente sua regra.

# 3. Estrutura Oficial da Pasta `docs/`

A estrutura documental ativa é:

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

Caminhos retirados da árvore ativa:

```text
administrador/
design/
marketing/
templates/
ui/
```

`administrador/` não corresponde a uma família documental vigente.

`design/`, `ui/` e `templates/` foram consolidados principalmente em:

```text
design-system/
frontend/
```

`marketing/` foi consolidado em:

```text
estrategia-digital/
```

Referências históricas a caminhos antigos podem permanecer em changelogs e releases, desde que não sejam apresentadas como estrutura vigente.

# 4. Classes de Documentação

## 4.1 Constitucional / Framework

Define princípios, políticas e padrões transversais.

Exemplo principal:

```text
frameworks/
```

Baseline atual:

```text
01-GDS
02-GAF
03-GSF
04-GQF
05-GDF
06-GOC
```

## 4.2 Normativa / Arquitetural / Técnica

Define como a plataforma deve ser estruturada ou implementada.

Exemplos:

```text
arquitetura/
backend/
frontend/
api/
seguranca/
infraestrutura/
design-system/
ai/
```

## 4.3 Funcional

Define comportamento dos módulos de negócio.

Exemplo:

```text
apps/
```

Responde:

```text
o que o módulo faz
```

e não:

```text
como implementar tecnicamente
```

## 4.4 Operacional

Define como validar, implantar, operar, automatizar, suportar ou recuperar a plataforma.

Exemplos:

```text
qualidade/
operacoes/
deploy/
automacao/
desenvolvimento/
```

## 4.5 Usuário / Produto / Estratégia

Exemplos:

```text
usuario/
produto/
estrategia-digital/
```

## 4.6 Histórica / Evidencial / Decisória

Registra fatos, decisões, auditorias, análises e releases.

Exemplos:

```text
adr/
auditoria/
relatorios/
release-notes/
```

Essas séries são evolutivas e não possuem número final obrigatório.

# 5. Responsabilidade das Pastas

## `apps/`

Documentação funcional canônica dos módulos.

Deve cobrir, conforme aplicável:

- objetivo;
- atores;
- conceitos;
- entidades de negócio;
- regras;
- fluxos;
- permissões em perspectiva funcional;
- escopo por igreja/tenant;
- integrações;
- estados e transições;
- referências técnicas.

Não documenta padrões genéricos de implementação.

## `api/`

Contratos, padrões, segurança, versionamento, lifecycle e operação das APIs.

Baseline atual:

```text
01–14
```

## `arquitetura/`

Arquitetura sistêmica vigente.

Baseline atual:

```text
01–09
```

Decisões com contexto, alternativas e consequências devem preferencialmente ser registradas em `adr/`.

## `backend/`

Padrões de engenharia Django e implementação backend.

Baseline atual:

```text
01–20
```

## `frontend/`

Arquitetura e implementação da camada de apresentação.

Baseline atual:

```text
01–11
```

Documento transitório adicional:

```text
Migracao-CSS.md
```

## `frameworks/`

Camada constitucional/transversal da documentação.

Baseline atual:

```text
01–06
```

Não criar `07+` por continuidade numérica.

## `seguranca/`

Controles especializados de segurança, privacidade, multi-tenancy, aplicação, APIs, infraestrutura, incidentes, vulnerabilidades, conformidade e SDL.

Baseline atual:

```text
01–17
```

`14-Conformidade-e-LGPD.md` integra a baseline vigente.

## `infraestrutura/`

Ambientes, plataforma, observabilidade, continuidade, backup, automação de infraestrutura, capacidade, custos e prontidão.

Baseline atual:

```text
01–21
```

Registros históricos internos não devem ser usados como padrão para expansão normativa.

## `design-system/`

Fonte canônica da linguagem visual e UX.

Baseline atual:

```text
01–19
```

Relação:

```text
frameworks/GDS
→ design-system/
→ frontend/
```

## `ai/`

Família GAI — GereIgreja Artificial Intelligence Engineering.

Baseline oficial:

```text
GAI-01 ... GAI-35
```

Estado:

```text
GAI Framework 1.0
FREEZE ESTRUTURAL
```

`GAI-36+` exige Gap Analysis formal.

## `qualidade/`

Camada operacional do GQF:

- QA;
- homologação;
- regressão;
- testes manuais;
- quality gates;
- aceite;
- checklists de liberação.

## `operacoes/`

Runbooks, troubleshooting, suporte e procedimentos recorrentes alinhados ao GOC.

## `deploy/`

Procedimentos de implantação e publicação de versões.

Registros históricos de release devem ser distinguidos de procedimentos normativos de deploy.

## `automacao/`

Automações operacionais ou de negócio com lifecycle próprio.

Não usar para simples edição em lote de interface.

## `desenvolvimento/`

Guias locais de desenvolvimento que não pertençam melhor a Backend, Frontend ou Qualidade.

Escopo pequeno não constitui defeito.

## `usuario/`

Documentação destinada ao usuário final.

```text
apps/
→ o que o sistema faz

usuario/
→ como utilizar
```

## `produto/`

Especificações e evolução de iniciativas de produto.

Atualmente possui escopo restrito e fortemente concentrado em iniciativas específicas.

Não deve substituir `apps/` após estabilização funcional.

## `estrategia-digital/`

Estratégia de posicionamento, conteúdo, SEO, conversão, métricas e autoridade.

Baseline atual:

```text
00–13
```

Natureza:

```text
VIVA / TEMPORAL
```

Exige revisão periódica.

## `adr/`

Architecture Decision Records.

Explicam:

- contexto;
- alternativas;
- decisão;
- consequências.

ADR explica **por que**.

Arquitetura explica **como está hoje**.

## `release-notes/`

Histórico de releases.

É série histórica e não deve ser confundida com deploy.

## `auditoria/`

Evidências e resultados de verificações executadas.

Não constitui, por si só, fonte normativa.

## `relatorios/`

Relatórios, diagnósticos, análises e investigações.

Não constituem autoridade normativa por padrão.

## `sistema/`

Família transitória.

Status:

```text
NOVOS DOCUMENTOS: NÃO
AUTORIDADE NORMATIVA: NÃO
```

Conteúdo válido deve ser gradualmente consolidado nas famílias canônicas.

## `governanca/`

Família válida, em consolidação.

Mantém princípios e manifestos, mas possui padrões técnicos antigos que se sobrepõem a Backend, Arquitetura, Segurança, Qualidade e GDF.

Novos documentos são excepcionais.

Conteúdo legado deve ser comparado, absorvido quando exclusivo e ainda válido, e depois arquivado/removido quando apropriado.

# 6. Hierarquia de Autoridade

```text
Framework / Política
        ↓
Especificação normativa do domínio
        ↓
Arquitetura e padrões técnicos
        ↓
Documentação funcional
        ↓
Procedimentos operacionais
        ↓
Evidências e registros históricos
```

Exemplos:

```text
GDS → design-system → frontend
GAF/GSF → seguranca → backend/api/infraestrutura
GQF → qualidade → checklists/evidências
GOC → operacoes → runbooks
GDF → GDF-00 → INDEX/READMEs
```

Um registro histórico não altera uma regra normativa sem atualização explícita da fonte de autoridade.

# 7. Como Criar um Novo Documento

Antes da criação, verificar obrigatoriamente:

1. existe documento semelhante?
2. existe documento canônico que possa ser evoluído?
3. a pasta escolhida possui autoridade sobre o assunto?
4. o conteúdo é permanente o suficiente?
5. o novo documento reduz ambiguidade?
6. reduz duplicação?
7. possui lifecycle próprio?
8. exige atualização de README/INDEX?
9. já existe registro legado que pode ser consolidado?
10. a criação é realmente melhor que atualizar o existente?

Se a resposta não justificar arquivo independente, não criar.

# 8. Convenção de Nomenclatura

Para famílias normativas e funcionais sequenciais:

```text
NN-Nome-do-Documento.md
```

Preferências:

- sem acentos;
- palavras separadas por hífen;
- nomes objetivos;
- numeração coerente;
- evitar espaços;
- evitar variações inconsistentes de caixa.

Exceções históricas não devem ser renomeadas indiscriminadamente.

Renomear exige:

```text
verificar referências
→ atualizar links
→ preservar contexto histórico quando necessário
```

# 9. Estrutura Padrão dos Documentos

Documentos normativos e canônicos deverão conter, conforme aplicável:

- Pasta;
- Arquivo;
- Documento;
- Framework ou Seção;
- Versão;
- Status;
- Responsável;
- Última atualização;
- Título;
- Objetivo;
- Escopo;
- Conteúdo;
- Documentos relacionados;
- Regras/princípios finais.

Documentos históricos e evidenciais podem usar estrutura reduzida desde que permaneçam identificáveis e rastreáveis.

# 10. Versionamento e Baselines

Documentos normativos utilizam versionamento simples:

```text
1.0
1.1
1.2
2.0
```

Uma família pode ser declarada baseline fechada.

Isso significa:

- cobertura planejada concluída;
- novos números não são automáticos;
- mudanças podem ocorrer por atualização dos arquivos existentes;
- expansão exige lacuna real.

Exemplos atuais:

```text
Frameworks     → 01–06
Arquitetura    → 01–09
Backend        → 01–20
Frontend       → 01–11
API            → 01–14
Segurança      → 01–17
Infraestrutura → 01–21
Design System  → 01–19
GAI            → 01–35, freeze estrutural
```

# 11. Atualização e Ciclo de Vida

Documentos devem ser atualizados quando:

- implementação muda;
- regra muda;
- autoridade muda;
- caminho muda;
- documento relacionado é removido;
- conteúdo deixa de representar o sistema real.

Documentação desatualizada é defeito.

Estados recomendados para famílias normativas:

```text
DRAFT
REVIEW
OFFICIAL
DEPRECATED
RETIRED
```

Famílias podem definir estados próprios quando houver justificativa.

# 12. O que Não Documentar

Evitar:

- duplicação de regras existentes;
- listas artificiais para completar sequência;
- intenção futura escrita como capacidade atual;
- caminhos inexistentes tratados como vigentes;
- código efêmero sem valor arquitetural;
- registros temporários sem necessidade de retenção;
- documentos criados apenas porque uma pasta está vazia;
- opinião antiga tratada como especificação atual.

# 13. Relação entre Camadas

Exemplo de separação:

```text
arquitetura/
→ como o sistema se organiza

backend/
→ como implementar no servidor

frontend/
→ como implementar a interface

design-system/
→ como a interface deve parecer

apps/
→ o que o domínio funcional faz

usuario/
→ como utilizar

qualidade/
→ como validar

operacoes/
→ como operar

deploy/
→ como publicar

release-notes/
→ o que foi entregue
```

# 14. Índices e READMEs

`INDEX.md` é o mapa global.

Cada pasta ativa deve possuir README quando isso agregar navegação e autoridade local.

O README deve:

- definir escopo;
- indicar fronteiras;
- apontar baseline;
- indicar documentos principais;
- evitar duplicar integralmente mapas especializados.

Quando existir documento de mapa próprio, o README deve apontar para ele.

Exemplos:

```text
ai/35-Mapa-Mestre...
seguranca/17-Mapa-e-Indice...
infraestrutura/18-Indice-e-Mapa...
api/14-Mapa-e-Indice...
```

# 15. Checklist para Novos Documentos

Antes de criar:

- [ ] lacuna comprovada;
- [ ] domínio correto;
- [ ] nenhum documento existente pode absorver;
- [ ] lifecycle independente;
- [ ] nome adequado;
- [ ] owner definido;
- [ ] referências planejadas;
- [ ] impacto em README/INDEX avaliado.

# 16. Checklist para Revisões

Ao revisar:

- [ ] ainda representa o sistema?
- [ ] conflito com documento mais novo?
- [ ] referências válidas?
- [ ] status correto?
- [ ] owner ainda existe?
- [ ] conteúdo duplicado?
- [ ] deve ser consolidado?
- [ ] deve ser arquivado ou retirado?

# 17. Reclassificação e Conteúdo Legado

Documentos legados não devem ser movidos ou apagados mecanicamente.

Sequência recomendada:

```text
identificar
↓
comparar
↓
extrair conteúdo exclusivo ainda válido
↓
atualizar fonte canônica
↓
corrigir referências
↓
classificar histórico residual
↓
arquivar ou remover
```

Documentos históricos podem preservar caminhos antigos quando isso for necessário para manter fidelidade histórica.

# 18. Famílias Removidas ou Consolidadas

Não são famílias ativas:

```text
design/
ui/
templates/
marketing/
administrador/
```

Destino principal:

```text
design/ + ui/ + templates/
→ design-system/ + frontend/

marketing/
→ estrategia-digital/
```

Não recriar esses diretórios por conveniência.

# 19. Documentos Relacionados

Fontes principais:

```text
docs/INDEX.md
docs/README.md
docs/frameworks/05-GDF-GereIgreja-Documentation-Framework.md
```

O `INDEX.md` deve permanecer sincronizado com este guia.

# 20. Princípios Finais

```text
Mais arquivos
≠
melhor documentação
```

A documentação deve crescer por necessidade, não por impulso de completude.

Princípios finais:

```text
Evoluir antes de criar.
Consolidar antes de duplicar.
Definir autoridade.
Preservar histórico sem confundi-lo com regra vigente.
Manter o mapa sincronizado.
Tratar obsolescência documental como defeito.
```

## Status

**Arquivo:** `docs/00-Guia-de-Documentacao.md`  
**Documento:** `GDF-00`  
**Versão:** `1.2`  
**Status:** **OFICIAL**
