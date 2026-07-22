Pasta:
docs/

Arquivo:
00-Guia-de-Documentacao.md

Documento:
GDF-00

Framework:
GDF — GereIgreja Documentation Framework

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# 00 - Guia Oficial da Documentação

> *"Uma documentação organizada transforma conhecimento em patrimônio permanente do projeto."*

---

# Sumário

1. Objetivo
2. Filosofia da Documentação
3. Estrutura Oficial da Pasta docs
4. Responsabilidade de Cada Pasta
5. Como Criar um Novo Documento
6. Convenção de Nomenclatura
7. Estrutura Padrão dos Documentos
8. Versionamento
9. Atualização da Documentação
10. O que NÃO Documentar
11. Relação entre as Pastas
12. Índices e READMEs
13. Checklist para Novos Documentos
14. Checklist para Revisões
15. Documentos Relacionados
16. Princípios Finais

---

# 1. Objetivo

Este documento estabelece as regras oficiais para criação, organização, manutenção e evolução da documentação técnica do GereIgreja.

Seu objetivo é garantir que toda documentação siga um padrão único, evitando duplicidade, inconsistências e perda de conhecimento.

Este documento possui prioridade sobre qualquer outro documento de documentação.

---

# 2. Filosofia da Documentação

A documentação do GereIgreja deverá ser:

- organizada;
- objetiva;
- reutilizável;
- consistente;
- rastreável;
- evolutiva;
- fácil de navegar.

Toda documentação deverá responder claramente:

- por que existe;
- onde pertence;
- quando deve ser utilizada;
- quem é responsável por sua manutenção.

---

# 3. Estrutura Oficial da Pasta docs

A estrutura oficial da documentação é:

```text
docs/

00-Guia-de-Documentacao.md
INDEX.md
README.md

apps/
api/
arquitetura/
backend/
frontend/
frameworks/
operacoes/
qualidade/
deploy/
adr/
contribuicao/
marketing/
seo/
```

Novas pastas deverão ser criadas apenas quando representarem um novo domínio de documentação.

---

# 4. Responsabilidade de Cada Pasta

## apps/

Documentação funcional dos Apps da plataforma.

Exemplo:

- Membros;
- Financeiro;
- Comunicação;
- Eventos.

Não documenta padrões técnicos.

---

## backend/

Documenta como o Backend deve ser desenvolvido.

Exemplo:

- Models;
- Services;
- Selectors;
- Managers;
- Views;
- Forms.

Não documenta módulos específicos.

---

## frontend/

Documenta padrões de interface, templates, JavaScript, HTMX, componentes e experiência do usuário.

---

## arquitetura/

Documenta a arquitetura geral da plataforma.

Exemplo:

- Plataforma;
- Banco de Dados;
- APIs;
- Segurança;
- Multi-Tenant.

---

## frameworks/

Contém os frameworks internos do GereIgreja.

Exemplo:

- GDS;
- GAF;
- GSF;
- GQF;
- GDF.

---

## api/

Documentação das APIs públicas e internas.

---

## operacoes/

Runbooks, procedimentos operacionais e administração da plataforma.

---

## qualidade/

Checklists, homologações, QA, testes manuais e processos de liberação.

---

## deploy/

Procedimentos de implantação da plataforma.

---

## adr/

Architecture Decision Records.

Cada decisão arquitetural relevante deverá possuir um ADR próprio.

---

## contribuicao/

Guias destinados aos desenvolvedores que colaboram com o projeto.

---

## marketing/

Materiais relacionados à divulgação e crescimento da plataforma.

---

## seo/

Estratégias de SEO e conteúdo institucional.

---

# 5. Como Criar um Novo Documento

Antes de criar um documento, verificar:

1. Já existe documento semelhante?
2. A pasta escolhida é realmente a correta?
3. O conteúdo pertence ao domínio daquela pasta?
4. O documento evitará duplicação?
5. Existe necessidade real de um novo documento?

Sempre priorizar evolução da documentação existente antes de criar novos arquivos.

---

# 6. Convenção de Nomenclatura

Todos os documentos deverão seguir:

```text
NN-Nome-do-Documento.md
```

Exemplos:

```text
01-Models.md

05-Services.md

08-Views.md

04-Comunicacao.md
```

Utilizar:

- letras sem acentos;
- palavras separadas por hífen;
- nomes curtos;
- numeração sequencial dentro da pasta.

---

# 7. Estrutura Padrão dos Documentos

Todo documento deverá conter:

- Pasta;
- Arquivo;
- Documento;
- Framework ou Seção;
- Versão;
- Status;
- Responsável;
- Última atualização;
- Título;
- Sumário;
- Conteúdo;
- Documentos Relacionados;
- Princípios Finais;
- Status.

Essa estrutura facilita leitura e manutenção.

---

# 8. Versionamento

Os documentos utilizarão versionamento simples.

Exemplo:

```text
Versão:
1.0
```

Mudanças significativas poderão gerar:

- 1.1
- 1.2
- 2.0

Sempre registrar a última atualização.

---

# 9. Atualização da Documentação

Toda alteração arquitetural relevante deverá ser acompanhada pela atualização da documentação correspondente.

A documentação deve evoluir junto com o sistema.

Documentação desatualizada é considerada um defeito do projeto.

---

# 10. O que NÃO Documentar

Evitar:

- código duplicado;
- tutoriais temporários;
- anotações pessoais;
- testes descartáveis;
- informações desatualizadas;
- conteúdo sem responsável.

Toda documentação deverá possuir valor permanente.

---

# 11. Relação entre as Pastas

Cada pasta possui responsabilidade própria.

Exemplo:

```text
Backend
↓

Como construir.

Apps
↓

O que foi construído.

Arquitetura
↓

Como tudo se organiza.

Operações
↓

Como operar.

Qualidade
↓

Como validar.

Frameworks
↓

Quais padrões seguir.
```

Nenhuma pasta deverá assumir responsabilidades de outra.

---

# 12. Índices e READMEs

Cada pasta deverá possuir um README.md contendo:

- objetivo;
- escopo;
- padrão de nomenclatura;
- índice dos documentos;
- orientações específicas.

O INDEX.md da raiz deverá servir como mapa geral da documentação.

---

# 13. Checklist para Novos Documentos

Antes de criar um documento verificar:

- pasta correta;
- nome padronizado;
- numeração disponível;
- estrutura oficial utilizada;
- ausência de duplicação;
- links atualizados;
- README da pasta revisado quando necessário.

---

# 14. Checklist para Revisões

Durante revisões verificar:

- consistência;
- atualização;
- links válidos;
- nomenclatura;
- estrutura;
- responsabilidade correta;
- ausência de redundância.

---

# 15. Documentos Relacionados

- README.md
- INDEX.md
- GDF — GereIgreja Documentation Framework
- GEA — GereIgreja Engineering Architecture
- GQF — GereIgreja Quality Framework

---

# 16. Princípios Finais

A documentação do GereIgreja é considerada parte integrante da arquitetura da plataforma.

Ela não é um complemento do código, mas um ativo estratégico que preserva conhecimento, orienta decisões e reduz custos de manutenção.

Todo novo documento deverá respeitar os princípios estabelecidos neste guia.

A qualidade da documentação refletirá diretamente na qualidade do software.

---

## ✅ Status

**Pasta:** `docs/`

**Arquivo:** `00-Guia-de-Documentacao.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento passa a ser a referência máxima para organização, criação e manutenção de toda a documentação do GereIgreja.

