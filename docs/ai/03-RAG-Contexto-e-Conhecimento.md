Pasta:

docs/ai/

Arquivo:

03-RAG-Contexto-e-Conhecimento.md

Documento:

GAI-03

Código:

GAI-RAG-CONTEXT-KNOWLEDGE

Família:

GAI — GereIgreja Artificial Intelligence Engineering

Frameworks relacionados:

GEA — GereIgreja Enterprise Architecture
GSF — GereIgreja Security Framework
GOC — GereIgreja Operations Center
GQF — GereIgreja Quality Framework
GDF — GereIgreja Documentation Framework
GAPI — GereIgreja API Engineering
GINF — GereIgreja Infrastructure Engineering
GereIgreja Backend Engineering

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GAI-03 — RAG, Contexto e Conhecimento

> "Um modelo só deve receber o conhecimento necessário, autorizado, rastreável e válido para a tarefa que está executando."

---

# Sumário

1. Objetivo
2. Escopo
3. Relação com GAI-01 e GAI-02
4. Princípios Fundamentais
5. O que é RAG
6. Arquitetura de Referência
7. Fontes de Conhecimento
8. Classificação das Fontes
9. Ingestão
10. Pipeline de Ingestão
11. Validação de Origem
12. Normalização
13. Chunking
14. Estratégias de Chunking
15. Metadados
16. Identidade do Documento
17. Versionamento
18. Embeddings
19. Vector Store
20. Isolamento Multi-Tenant
21. Estratégias de Isolamento
22. Autorização no Retrieval
23. Filtros
24. Busca Semântica
25. Busca por Palavra-Chave
26. Busca Híbrida
27. Ranking
28. Reranking
29. Relevância
30. Context Builder
31. Context Window
32. Context Budget
33. Priorização
34. Deduplicação
35. Freshness
36. Conteúdo Obsoleto
37. Citações e Proveniência
38. Prompt Assembly
39. Delimitação
40. Prompt Injection em Documentos
41. Conteúdo Não Confiável
42. Segurança
43. Privacidade
44. Dados Sensíveis
45. LGPD
46. Retenção
47. Exclusão
48. Direito de Acesso
49. Sincronização
50. Reindexação
51. Atualização Incremental
52. Falhas de Indexação
53. Consistência
54. Cache
55. Performance
56. Latência
57. Escalabilidade
58. Custos
59. Observabilidade
60. Logs
61. Métricas
62. Auditoria
63. Avaliação de Retrieval
64. Precision
65. Recall
66. Groundedness
67. Faithfulness
68. Casos sem Resposta
69. Thresholds
70. Testes Cross-Tenant
71. Testes Adversariais
72. Fallback
73. Degradação
74. Knowledge Base
75. Documentação Oficial
76. Conteúdo Operacional
77. Conteúdo de Usuário
78. Conteúdo Externo
79. Web e Fontes Externas
80. Governança
81. Ownership
82. Lifecycle
83. Anti-Padrões
84. Arquitetura Consolidada
85. Checklist
86. Documentos Relacionados
87. Princípios Finais
88. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial para Retrieval-Augmented Generation (RAG), construção de contexto e gestão de conhecimento utilizado por recursos de Inteligência Artificial no GereIgreja.

Seu objetivo é garantir que conhecimento fornecido aos modelos seja:

- autorizado;
- isolado por tenant;
- relevante;
- rastreável;
- atualizado;
- minimizado;
- seguro;
- auditável.

---

# 2. Escopo

Aplica-se a:

- documentos internos;
- documentação técnica;
- conteúdo das igrejas;
- bases de conhecimento;
- embeddings;
- vector stores;
- busca semântica;
- busca híbrida;
- context builders;
- RAG;
- assistentes;
- agentes;
- qualquer funcionalidade que recupere dados para compor contexto de IA.

---

# 3. Relação com GAI-01 e GAI-02

O GAI-01 estabelece que autorização e isolamento multi-tenant são obrigatórios.

O GAI-02 define AI Gateway, providers, modelos e prompts.

O GAI-03 governa o caminho:

```text
Knowledge
   ↓
Ingestion
   ↓
Index
   ↓
Authorized Retrieval
   ↓
Context Builder
   ↓
Prompt
   ↓
AI Gateway
```

---

# 4. Princípios Fundamentais

Toda arquitetura RAG deverá observar:

- authorization before retrieval;
- tenant isolation;
- data minimization;
- provenance;
- freshness;
- least context;
- defense against prompt injection;
- evaluation;
- observability;
- lifecycle management.

---

# 5. O que é RAG

RAG combina recuperação de informação com geração por modelo.

```text
Question
   │
   ▼
Retrieval
   │
   ▼
Relevant Context
   │
   ▼
LLM
   │
   ▼
Grounded Response
```

RAG não transforma o modelo em banco de dados ou fonte autoritativa.

---

# 6. Arquitetura de Referência

```text
                KNOWLEDGE SOURCES
                       │
                       ▼
                 INGESTION LAYER
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Validation   Normalization  Metadata
          └────────────┼────────────┘
                       ▼
                    Chunking
                       │
                       ▼
                   Embeddings
                       │
                       ▼
                Knowledge Index
                       │
                       ▼
User → Auth → Tenant → Authorization
                       │
                       ▼
                  Retrieval
                       │
                       ▼
                   Reranking
                       │
                       ▼
                Context Builder
                       │
                       ▼
                   AI Gateway
                       │
                       ▼
                    Response
```

---

# 7. Fontes de Conhecimento

Fontes poderão incluir:

- documentação oficial do GereIgreja;
- documentos de uma igreja;
- registros autorizados da aplicação;
- conteúdo operacional;
- arquivos enviados;
- integrações;
- fontes externas aprovadas.

---

# 8. Classificação das Fontes

Cada fonte deverá possuir classificação.

Exemplo:

```text
PUBLIC
INTERNAL
TENANT
RESTRICTED
CONFIDENTIAL
```

A classificação deverá ser compatível com o GSF.

---

# 9. Ingestão

Nenhum conteúdo deverá ser indexado sem origem conhecida.

---

# 10. Pipeline de Ingestão

Fluxo recomendado:

```text
Source
  ↓
Identify
  ↓
Authorize
  ↓
Validate
  ↓
Normalize
  ↓
Chunk
  ↓
Metadata
  ↓
Embed
  ↓
Index
```

---

# 11. Validação de Origem

Registrar:

- source type;
- source ID;
- tenant;
- owner;
- classificação;
- data de origem.

---

# 12. Normalização

Conteúdo poderá ser normalizado para remover ruído técnico sem destruir significado ou rastreabilidade.

---

# 13. Chunking

Chunking deverá respeitar a estrutura semântica do conteúdo.

Não utilizar tamanho fixo arbitrário como única estratégia para todos os tipos de documento.

---

# 14. Estratégias de Chunking

Poderão considerar:

- títulos;
- seções;
- parágrafos;
- entidades;
- tamanho máximo;
- overlap;
- tipo de documento.

---

# 15. Metadados

Cada chunk deverá carregar metadados suficientes para autorização e rastreabilidade.

Mínimo recomendado:

```text
tenant_id
source_id
document_id
chunk_id
source_type
classification
version
updated_at
```

Quando aplicável:

```text
owner
module
permissions
language
content_type
```

---

# 16. Identidade do Documento

Cada documento indexado deverá possuir identidade estável.

---

# 17. Versionamento

Mudanças relevantes deverão permitir distinguir versões antigas e atuais.

Chunks obsoletos não deverão permanecer indefinidamente como conhecimento ativo.

---

# 18. Embeddings

Embeddings são dados derivados.

Sua proteção deverá acompanhar a sensibilidade da fonte.

---

# 19. Vector Store

O vector store deverá ser tratado como componente de dados.

Aplicar:

- acesso restrito;
- backup quando necessário;
- observabilidade;
- lifecycle;
- isolamento.

---

# 20. Isolamento Multi-Tenant

O isolamento de tenant é requisito obrigatório.

```text
Tenant A
   X
Tenant B
```

Nenhuma similaridade semântica poderá ultrapassar a fronteira de autorização.

---

# 21. Estratégias de Isolamento

Dependendo do risco, poderão ser utilizados:

- índices separados;
- namespaces;
- collections;
- filtros obrigatórios;
- combinação dessas estratégias.

A escolha deverá ser documentada.

---

# 22. Autorização no Retrieval

Autorização deverá ocorrer antes de o conteúdo entrar no contexto.

```text
Search all
→ filter later
```

não é o padrão recomendado para dados restritos.

Preferir:

```text
Authorized Search Space
→ Retrieval
```

---

# 23. Filtros

Filtros obrigatórios não deverão depender do modelo.

Deverão ser aplicados por código controlado pela aplicação.

---

# 24. Busca Semântica

Busca semântica poderá identificar conteúdo conceitualmente relacionado.

Não deverá substituir filtros de autorização.

---

# 25. Busca por Palavra-Chave

Busca lexical poderá complementar retrieval semântico.

---

# 26. Busca Híbrida

Busca híbrida poderá combinar:

```text
semantic score
+
lexical score
+
metadata filters
```

---

# 27. Ranking

Resultados deverão ser ordenados por relevância após aplicação das fronteiras de acesso.

---

# 28. Reranking

Reranking poderá ser utilizado quando justificar ganho de qualidade.

O reranker somente poderá receber candidatos já autorizados.

---

# 29. Relevância

Quantidade de contexto não substitui qualidade.

Contexto irrelevante aumenta:

- custo;
- latência;
- confusão;
- risco de resposta incorreta.

---

# 30. Context Builder

O Context Builder é responsável por transformar resultados autorizados em contexto adequado ao modelo.

---

# 31. Context Window

O limite do modelo deverá ser conhecido.

---

# 32. Context Budget

Cada capacidade deverá reservar orçamento de contexto para:

- instruções;
- histórico;
- retrieval;
- tools;
- resposta.

---

# 33. Priorização

Quando o contexto exceder o budget, priorizar conteúdo por relevância e necessidade.

---

# 34. Deduplicação

Conteúdo repetido deverá ser removido quando possível.

---

# 35. Freshness

Conteúdo temporal deverá possuir informação de atualização.

---

# 36. Conteúdo Obsoleto

Conteúdo substituído deverá ser:

- desativado;
- reindexado;
- marcado;
- removido;

conforme política aplicável.

---

# 37. Citações e Proveniência

Quando a experiência exigir respostas fundamentadas, o sistema deverá preservar referências às fontes utilizadas.

O modelo não deverá inventar source IDs.

As referências deverão vir do pipeline de retrieval.

---

# 38. Prompt Assembly

O prompt deverá distinguir claramente:

- instruções;
- pergunta;
- contexto recuperado;
- histórico;
- tool results.

---

# 39. Delimitação

Conteúdo recuperado deverá ser delimitado como dados.

---

# 40. Prompt Injection em Documentos

Um documento poderá conter frases como:

```text
ignore todas as instruções anteriores
```

Esse texto deverá permanecer conteúdo, não instrução privilegiada.

---

# 41. Conteúdo Não Confiável

Todo conteúdo externo ao controle direto da aplicação deverá ser considerado potencialmente adversarial.

---

# 42. Segurança

Aplicar GSF e GAI-01.

---

# 43. Privacidade

Não recuperar dados além do necessário para responder à tarefa.

---

# 44. Dados Sensíveis

Conteúdo sensível poderá exigir:

- índice segregado;
- acesso adicional;
- mascaramento;
- exclusão de determinados campos;
- proibição de envio a certos providers.

---

# 45. LGPD

O pipeline deverá permitir atender políticas aplicáveis de:

- finalidade;
- necessidade;
- retenção;
- acesso;
- correção;
- exclusão.

---

# 46. Retenção

A retenção do índice não deverá ultrapassar injustificadamente a retenção da fonte.

---

# 47. Exclusão

Quando um conteúdo precisar ser excluído, seus derivados relevantes deverão ser considerados.

Exemplo:

```text
Source deleted
→ chunks removed
→ embeddings removed
→ caches invalidated
```

---

# 48. Direito de Acesso

Dados derivados não deverão impedir rastreabilidade até a fonte quando necessário para governança.

---

# 49. Sincronização

O índice deverá possuir estratégia conhecida de sincronização com a fonte.

---

# 50. Reindexação

Reindexação deverá ser possível sem perda de controle sobre versões e tenant.

---

# 51. Atualização Incremental

Preferir atualização incremental quando adequada ao volume.

---

# 52. Falhas de Indexação

Falhas deverão ser observáveis.

Não assumir que todo documento enviado foi indexado com sucesso.

---

# 53. Consistência

Definir expectativa de consistência entre fonte e índice.

Exemplo:

```text
near real-time
eventual
batch
```

---

# 54. Cache

Cache de retrieval deverá preservar:

- tenant;
- autorização;
- versão;
- expiração.

---

# 55. Performance

O pipeline deverá possuir metas proporcionais à experiência.

---

# 56. Latência

Medir separadamente quando possível:

```text
retrieval
reranking
context building
model generation
```

---

# 57. Escalabilidade

Planejar crescimento de:

- documentos;
- chunks;
- embeddings;
- queries;
- tenants.

---

# 58. Custos

Custos poderão incluir:

- embedding;
- storage;
- retrieval;
- reranking;
- geração.

---

# 59. Observabilidade

O pipeline RAG deverá ser observável de ponta a ponta.

---

# 60. Logs

Registrar metadados úteis sem expor conteúdo sensível desnecessariamente.

---

# 61. Métricas

Exemplos conceituais:

```text
rag_retrieval_requests
rag_retrieval_latency
rag_results_count
rag_empty_results
rag_indexing_failures
rag_chunks_indexed
rag_reindex_duration
```

---

# 62. Auditoria

Para consultas sensíveis, poderá ser necessário registrar:

- usuário;
- tenant;
- fonte acessada;
- finalidade/feature;
- timestamp.

---

# 63. Avaliação de Retrieval

Avaliar retrieval separadamente da qualidade do modelo.

---

# 64. Precision

Pergunta:

```text
dos resultados recuperados,
quantos eram relevantes?
```

---

# 65. Recall

Pergunta:

```text
do conhecimento relevante existente,
quanto conseguimos recuperar?
```

---

# 66. Groundedness

Avaliar se a resposta está apoiada no contexto fornecido.

---

# 67. Faithfulness

O modelo não deverá atribuir às fontes informações que elas não contêm.

---

# 68. Casos sem Resposta

O sistema deverá poder responder:

```text
não encontrei informação suficiente
```

em vez de fabricar conhecimento.

---

# 69. Thresholds

Thresholds de similaridade deverão ser avaliados por caso de uso.

---

# 70. Testes Cross-Tenant

Obrigatório testar cenários em que conteúdos semanticamente semelhantes pertencem a tenants diferentes.

Resultado esperado:

```text
zero vazamento
```

---

# 71. Testes Adversariais

Incluir documentos contendo:

- prompt injection;
- instruções falsas;
- conteúdo conflitante;
- dados proibidos;
- tentativas de exfiltração.

---

# 72. Fallback

Se retrieval falhar, a aplicação deverá possuir comportamento definido.

---

# 73. Degradação

Possibilidades:

```text
sem retrieval
→ responder somente conhecimento permitido do modelo

ou

sem retrieval
→ informar indisponibilidade

ou

sem evidência
→ não responder
```

A estratégia dependerá do caso de uso.

---

# 74. Knowledge Base

Bases de conhecimento deverão possuir owner.

---

# 75. Documentação Oficial

Documentação oficial poderá formar uma base de conhecimento técnica controlada.

Versão e status documental deverão ser considerados.

---

# 76. Conteúdo Operacional

Runbooks e documentos operacionais poderão possuir restrições diferentes da documentação pública.

---

# 77. Conteúdo de Usuário

Conteúdo de usuário pertence ao escopo do tenant correspondente.

---

# 78. Conteúdo Externo

Conteúdo externo deverá possuir origem e confiança conhecidas.

---

# 79. Web e Fontes Externas

Quando uma feature utilizar busca externa, diferenciar claramente:

```text
GereIgreja Knowledge
External Knowledge
```

Conteúdo externo não deverá adquirir automaticamente autoridade sobre dados internos.

---

# 80. Governança

Mudanças estruturais no pipeline deverão seguir governança técnica.

---

# 81. Ownership

Definir owners para:

- fonte;
- pipeline;
- índice;
- embeddings;
- retrieval;
- qualidade.

---

# 82. Lifecycle

Toda base deverá possuir processo de:

```text
create
ingest
update
reindex
archive
delete
```

---

# 83. Anti-Padrões

Evitar:

```text
indexar tudo
e filtrar depois
```

---

```text
vector store
sem tenant metadata
```

---

```text
documento deletado
embedding eterno
```

---

```text
retrieval
sem source ID
```

---

```text
contexto gigante
"para garantir"
```

---

```text
conteúdo recuperado
tratado como system instruction
```

---

```text
resposta sem evidência
apresentada como fato
```

---

```text
qualidade do RAG
avaliada apenas
pela fluência do modelo
```

---

# 84. Arquitetura Consolidada

```text
                     SOURCES
                        │
                        ▼
                   INGESTION
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      VALIDATION     METADATA      CHUNKING
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                    EMBEDDING
                        │
                        ▼
                  KNOWLEDGE INDEX
                        │
                        │
User ──► Auth ──► Tenant ──► Permission
                        │
                        ▼
               AUTHORIZED RETRIEVAL
                        │
                        ▼
                    RERANK
                        │
                        ▼
                 CONTEXT BUILDER
                        │
                        ▼
                   AI GATEWAY
                        │
                        ▼
                    RESPONSE
                        │
                        ▼
              SOURCES / AUDIT / METRICS
```

---

# 85. Checklist

## Fonte

- [ ] origem conhecida;
- [ ] owner;
- [ ] tenant;
- [ ] classificação;
- [ ] lifecycle.

## Ingestão

- [ ] validação;
- [ ] normalização;
- [ ] chunking;
- [ ] metadados;
- [ ] versionamento;
- [ ] erros observáveis.

## Índice

- [ ] isolamento;
- [ ] acesso restrito;
- [ ] source IDs;
- [ ] remoção;
- [ ] reindexação.

## Retrieval

- [ ] autorização antes do contexto;
- [ ] filtros obrigatórios;
- [ ] tenant;
- [ ] ranking;
- [ ] threshold;
- [ ] deduplicação.

## Contexto

- [ ] budget;
- [ ] minimização;
- [ ] delimitação;
- [ ] freshness;
- [ ] proveniência.

## Segurança

- [ ] prompt injection;
- [ ] cross-tenant;
- [ ] dados sensíveis;
- [ ] privacidade;
- [ ] retenção.

## Qualidade

- [ ] precision;
- [ ] recall;
- [ ] groundedness;
- [ ] faithfulness;
- [ ] casos sem resposta;
- [ ] testes adversariais.

## Operação

- [ ] métricas;
- [ ] logs;
- [ ] auditoria;
- [ ] custos;
- [ ] fallback;
- [ ] ownership.

---

# 86. Documentos Relacionados

- GAI-01 — Arquitetura e Governança de Inteligência Artificial
- GAI-02 — Providers, Modelos, Prompts e AI Gateway
- GSF — GereIgreja Security Framework
- GAPI — GereIgreja API Engineering
- GINF — GereIgreja Infrastructure Engineering
- GQF — GereIgreja Quality Framework
- GOC — GereIgreja Operations Center
- GDF — GereIgreja Documentation Framework
- GereIgreja Backend Engineering

---

# 87. Princípios Finais

RAG não deverá ser tratado apenas como busca vetorial.

Ele é uma cadeia de segurança, autorização, conhecimento e qualidade.

```text
Source
+
Authorization
+
Retrieval
+
Context
+
Provenance
=
Knowledge usable by AI
```

O princípio central é:

```text
Se o usuário não pode acessar
o conhecimento na aplicação,

a IA também não pode
recebê-lo no contexto.
```

E:

```text
Mais contexto
não significa
melhor contexto.
```

O GereIgreja deverá fornecer aos modelos somente o conhecimento necessário, autorizado e rastreável para cada tarefa.

---

# 88. Status do Documento

**Pasta**

`docs/ai/`

**Arquivo**

`03-RAG-Contexto-e-Conhecimento.md`

**Documento**

`GAI-03`

**Código**

`GAI-RAG-CONTEXT-KNOWLEDGE`

**Família**

`GAI — GereIgreja Artificial Intelligence Engineering`

**Versão**

`1.0`

**Status**

`OFICIAL`

**Responsável**

`Equipe de Engenharia`

**Última atualização**

`Agosto de 2026`

**Documento anterior**

`GAI-02 — Providers, Modelos, Prompts e AI Gateway`

**Próximo documento candidato**

`04-Ferramentas-Agentes-e-Acoes-Seguras.md`
