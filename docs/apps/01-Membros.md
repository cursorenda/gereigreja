Pasta:
docs/apps/

Arquivo:
01-Membros.md

Documento:
APP-01

Família:
Apps — Documentação Funcional

Versão:
1.1

Status:
Documentação funcional em consolidação

Responsável:
Equipe de Engenharia

Última atualização:
Setembro de 2026

# 01 — Membros

> O domínio de Membros descreve o ciclo de relacionamento cadastral das pessoas com a igreja, incluindo classificação, status, histórico e vínculos. Este documento separa comportamento implementado, convenções funcionais/históricas e lacunas ainda sujeitas a decisão futura.

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Conceitos Centrais
5. Tipos de Pessoa
6. Status
7. Substatus de Inatividade
8. Corpo de Membros Oficial
9. Pessoas em Acompanhamento
10. Transições de Tipo
11. Regras de Validade
12. Contexto de Igreja e Multi-Tenancy
13. Cargos e Vínculos
14. Integrações
15. Segurança e Privacidade
16. Auditoria e Histórico
17. Relatórios
18. Testes e Qualidade
19. Limites e Pontos a Validar
20. Documentos Relacionados
21. Princípios Finais
22. Status

---

# 1. Objetivo

Este documento consolida a documentação funcional em evolução do domínio Membros no GereIgreja, sem apresentar como implementadas regras que ainda sejam apenas históricas, convencionais ou planejadas.

Seu objetivo é registrar:

- como pessoas são classificadas;
- quais classificações e status estão documentados e qual é seu nível de enforcement;
- quais transições são trajetórias históricas ou comportamentos comprovados;
- como histórico e inatividade devem ser representados;
- como o contexto da igreja limita acesso e manipulação;
- como o domínio se relaciona com Secretaria, Eventos, Escola Bíblica, Departamentos e Usuários.

Este documento não substitui regras técnicas de Models, Forms, Services, permissões ou validações de Backend.

---

# 2. Escopo

O domínio de Membros cobre a representação funcional de pessoas cadastradas em uma igreja e de seu relacionamento documentado com essa igreja.

Inclui, conforme a documentação existente:

- Membro;
- Obreiro;
- Novo Convertido;
- Congregado;
- Visitante;
- status de participação;
- substatus documental de inatividade;
- progressão de relacionamento;
- desligamento;
- disciplina;
- transferência;
- acompanhamento;
- cargos e vínculos relacionados.

---

# 3. Papel deste Documento

Este é um documento funcional em consolidação para o domínio Membros. Ele não substitui o código como evidência de enforcement, nem transforma documentos históricos em regra vigente.

Sua relação com os demais documentos é:

```text
docs/apps/01-Membros.md
        ↓
Regras e conceitos funcionais
        ↓
docs/sistema/ (histórico/legado)
docs/backend/
docs/seguranca/
docs/qualidade/
docs/release-notes/
        ↓
Implementação, validação e histórico
```

Documentos especializados continuam sendo fontes de detalhe. Referências em `docs/sistema/` são históricas/legadas e não são autoridade normativa atual.

---

# 4. Conceitos Centrais

## Identidade e vínculos implementados

No código atual, os conceitos abaixo são distintos:

```text
Pessoa
→ entidade cadastral vinculada obrigatoriamente a uma Igreja.

Membro
→ proxy de compatibilidade de Pessoa; não é uma segunda identidade persistida independente.

User
→ conta autenticável do sistema.

PerfilUsuario
→ perfil organizacional do User: Ministério + igrejas_permitidas.

Cargo / MembroCargo
→ função e vínculo funcional da pessoa.

DepartamentoVinculo
→ vínculo departamental histórico/local.
```

Nenhum vínculo funcional — inclusive Cargo, MembroCargo ou DepartamentoVinculo — concede autorização, seleção de igreja ou escopo operacional por si só.

## Tipo e status

O GereIgreja distingue **tipo de pessoa** de **status**.

Esses conceitos não são equivalentes.

```text
Tipo
↓
Quem esta pessoa representa no relacionamento com a igreja?

Status
↓
Qual é sua situação atual dentro desse relacionamento?
```

Essa separação existe no cadastro atual e permite registrar mudanças de classificação e situação sem converter automaticamente uma mudança de estado em nova identidade.

---

# 5. Tipos de Pessoa

A documentação funcional/histórica identifica as seguintes categorias principais:

| Tipo | Significado funcional |
|---|---|
| Membro | Pessoa oficialmente vinculada ao rol de membros |
| Obreiro | Pessoa reconhecida na convenção histórica como exercendo função de liderança ou serviço específico |
| Novo Convertido | Pessoa recém-convertida em processo de integração |
| Congregado | Pessoa que frequenta regularmente sem vínculo formal de membro |
| Visitante | Pessoa em contato ocasional ou inicial com a igreja |

Esses nomes são convenções/categorias atualmente documentadas. No código atual, `TipoPessoa` é um catálogo independente e livre; esta tabela não é enumeração técnica fechada nem `choices` rígidos do modelo.

---

# 6. Status

Os status abaixo aparecem na documentação funcional/histórica:

| Status | Significado |
|---|---|
| Ativo | Pessoa participando regularmente |
| Inativo | Pessoa que deixou de participar, sem necessariamente perder o histórico |
| Em Disciplina | Situação formal aplicável ao corpo de membros |
| Desligado | Vínculo formal encerrado |

Esses nomes não formam um catálogo técnico completo: `StatusPessoa` é um catálogo independente e livre no código atual. As combinações historicamente sugeridas entre tipo e status são tratadas na seção 11 como convenção, não como enforcement universal.

---

# 7. Substatus de Inatividade

O código possui o campo `sub_status_inativo` como informação complementar de inatividade.

Valores documentados:

- `FALECIDO`;
- `MUDOU`;
- `TRANSFERIDO`.

No modelo, os valores documentados são complementares ao status principal. No `MembroForm` legado há validação que exige substatus quando o status informado é “Inativo” e restringe os valores acima.

- opcional;
- usado para histórico;
- útil para relatórios;
- útil para acompanhamento;
- sem efeito direto em permissões.

Portanto:

```text
status = Inativo
+
substatus
=
contexto histórico adicional
```

O substatus não substitui o status principal. A aplicação universal da validação de obrigatoriedade não está comprovada: o `_CanonicalMembroForm` atual não reproduz claramente o mesmo `clean()` do formulário legado.

---

# 8. Corpo de Membros Oficial — Convenção Funcional/Histórica

A documentação histórica classifica como corpo oficial:

- Membro;
- Obreiro.

Para essas categorias, os seguintes status foram documentados como aplicáveis:

- Ativo;
- Inativo;
- Em Disciplina;
- Desligado.

A justificativa histórica é que essas pessoas fariam parte do rol oficial e poderiam estar sujeitas a processos formais de disciplina, desligamento e mudança de situação. Esta classificação não é uma matriz rígida comprovadamente aplicada pelo backend.

---

# 9. Pessoas em Acompanhamento — Convenção Funcional/Histórica

A documentação histórica agrupa como pessoas em acompanhamento:

- Novo Convertido;
- Congregado;
- Visitante.

Para esses tipos, os seguintes status foram historicamente associados:

- Ativo;
- Inativo.

Na mesma convenção histórica, os seguintes status foram tratados como não usuais:

- Em Disciplina;
- Desligado.

A lógica histórica é que essas pessoas ainda não pertenceriam formalmente ao rol oficial. Isso não é validação universal comprovada no cadastro atual.

---

# 10. Transições de Tipo

A documentação histórica apresenta o seguinte fluxo como progressão típica:

```text
Visitante
   ↓
Novo Convertido
   ↓
Congregado
   ↓
Membro
   ↓
Obreiro
```

Esse fluxo representa uma trajetória típica/histórica, não uma obrigação universal.

As transições descritas incluem:

- Visitante → Novo Convertido;
- Novo Convertido → Congregado;
- Congregado → Membro;
- Membro → Obreiro.

Não há máquina obrigatória de estados comprovada, enforcement de predecessor ou bloqueio comprovado de saltos entre essas categorias. Quando há criação ou mudança de tipo/status, `Pessoa.save()` registra o evento em `StatusHistorico`.

---

# 11. Matriz Tipo × Status — Convenção Funcional/Histórica

As combinações abaixo foram registradas historicamente como referências funcionais:

```text
Membro + Ativo
Membro + Inativo
Membro + Em Disciplina
Membro + Desligado

Obreiro + Ativo
Obreiro + Inativo
Obreiro + Em Disciplina
Obreiro + Desligado

Novo Convertido + Ativo
Novo Convertido + Inativo

Congregado + Ativo
Congregado + Inativo

Visitante + Ativo
Visitante + Inativo
```

Na mesma referência histórica, as combinações abaixo foram tratadas como não esperadas:

```text
Congregado + Em Disciplina
Congregado + Desligado
Visitante + Em Disciplina
Visitante + Desligado
Novo Convertido + Desligado
```

Esta matriz **não** descreve enforcement atual do backend: não há `Pessoa.clean()` impondo essas combinações e não foi localizada validação canônica universal para elas. Portanto, os termos “válido” e “inválido” não devem ser usados como descrição do comportamento atual.

A implementação de eventual matriz normativa, inclusive quais combinações devem ser bloqueadas, permanece uma decisão futura de produto e backend. O conhecimento histórico é preservado aqui apenas como contexto.

---

# 12. Contexto de Igreja e Multi-Tenancy

Pessoa pertence cadastralmente a uma Igreja e toda operação deve preservar esse contexto organizacional.

Operações de Membros devem respeitar:

- igreja ativa válida no escopo selecionável;
- `igreja_id`;
- permissões;
- escopo organizacional;
- relações permitidas.

Para perfis locais, o escopo de igreja depende de `PerfilUsuario.igrejas_permitidas`. O pertencimento ao mesmo Ministério não concede acesso local, a hierarquia de igrejas não expande escopo e igreja ativa não significa todas as igrejas disponíveis. Mesmo Admin Ministério não recebe operação local irrestrita.

Nenhuma ação deve permitir:

- visualizar pessoa de outro tenant;
- editar pessoa de outra igreja sem autorização;
- transferir vínculos sem regra explícita;
- usar parâmetros de interface como única barreira de segurança.

`DepartamentoVinculo` não concede seleção de igreja. Da mesma forma, Cargo e MembroCargo não concedem autorização automaticamente.

---

# 13. Cargos e Vínculos

O domínio de Membros se relaciona com cargos, funções e vínculos organizacionais.

É importante distinguir:

```text
Tipo de pessoa
≠
Cargo
≠
Permissão
```

Exemplo:

```text
Pessoa = Membro
Cargo = Tesoureiro
Permissão = derivada do sistema de autorização
```

Um cargo não deve alterar silenciosamente o tipo da pessoa.

Da mesma forma, tipo de pessoa, Cargo, MembroCargo e DepartamentoVinculo não concedem automaticamente acesso administrativo.

---

# 14. Integrações

## Secretaria

A Secretaria é o principal contexto operacional para cadastro, atualização e acompanhamento de pessoas.

## Eventos

Critérios de participantes podem usar tipo e status. Nos endpoints auditados, pessoas com tipo `Visitante` são excluídas desses critérios; também existe `PresencaVisitanteEvento` para registrar presença de visitante em evento.

## Escola Bíblica

`CadastroAluno` pode ser vinculado a `Pessoa`. Os vínculos auditados exigem que Pessoa e cadastro pertençam à mesma igreja.

## Departamentos

Pessoas podem possuir vínculos com departamentos e equipes por `DepartamentoVinculo`. Esse vínculo é local/histórico, deve respeitar a mesma igreja e não substitui a identidade cadastral nem concede autorização ou escopo.

## Usuários

`Pessoa.usuario` é opcional. Pessoa cadastrada, User autenticável e PerfilUsuario organizacional não são conceitos equivalentes.

---

# 15. Segurança e Privacidade

O domínio Membros contém dados pessoais e potencialmente sensíveis por contexto.

Deve seguir:

- GSF;
- Segurança de Dados e Privacidade;
- Conformidade e LGPD;
- arquitetura multi-tenant;
- menor privilégio.

Cuidados incluem:

- proteção de documentos pessoais;
- limitação de acesso;
- minimização;
- retenção;
- histórico;
- exportações;
- logs;
- relatórios;
- dados de crianças e adolescentes quando aplicável.

---

# 16. Auditoria e Histórico

## Implementado

O cadastro registra `StatusHistorico` na criação e em mudanças de tipo ou status de Pessoa.

## Desejável / não comprovado universalmente

Rastreabilidade de disciplina, desligamentos, transferências, alterações de vínculo e demais mudanças funcionais pode ser necessária ao domínio, mas não deve ser apresentada como cobertura automática universal sem evidência específica de implementação.

Exemplos:

- mudança de tipo;
- mudança de status;
- desligamento;
- disciplina;
- transferência;
- alteração de vínculo;
- correções de dados relevantes.

Um registro histórico não deve ser destruído apenas para representar o estado atual.

A estratégia exata de histórico pertence à implementação técnica, mas o requisito funcional é preservar contexto suficiente para auditoria e relatórios quando aplicável.

---

# 17. Relatórios

O modelo permite filtros e relatórios por tipo, status, substatus e igreja, quando a implementação concreta do relatório os utiliza:

- membros ativos;
- membros inativos;
- desligados;
- pessoas em disciplina;
- falecidos;
- transferidos;
- pessoas que mudaram de denominação;
- novos convertidos ativos;
- congregados;
- visitantes;
- evolução do corpo de membros;
- retenção.

Implementações concretas de relatórios devem respeitar tenant, filtros, período e permissões.

---

# 18. Testes e Qualidade

## Cobertura comprovada

Existem testes de escopo e acesso local para Secretaria, incluindo a exigência de escopo explícito de igreja para perfis locais.

## Qualidade desejada / roadmap

Caso uma matriz normativa ou máquina de transição seja implementada no futuro, deverão existir testes para combinações relevantes entre:

- tipo;
- status;
- tenant;
- permissão;
- transições;
- filtros;
- relatórios;
- integrações.

Cenários mínimos incluem:

- matriz tipo/status aprovada;
- transições permitidas e rejeitadas;
- acesso cruzado entre tenants bloqueado;
- mudança de tipo preservando consistência e histórico;
- comportamento de substatus após confirmação do formulário canônico;
- filtros de Eventos respeitando regra de tipos.

---

# 19. Limites e Pontos a Validar

Esta seção registra lacunas e decisões futuras; não cria regra de negócio vigente.

Entre eles:

1. definir, se necessário, matriz normativa de combinações tipo/status e seu enforcement universal;
2. definir, se necessário, transições obrigatórias, predecessores e bloqueio de saltos;
3. confirmar ou unificar o comportamento de substatus entre `MembroForm` legado e `_CanonicalMembroForm`;
4. validar cobertura específica para disciplina, desligamento, transferências e demais históricos funcionais;
5. manter integração entre Pessoa, Membro, User e PerfilUsuario alinhada à arquitetura vigente;
6. aplicar políticas de retenção e exclusão conforme GSF-14, não apenas documentos históricos.

Esses pontos devem ser validados antes de endurecer regras de produção.

---

# 20. Documentos Relacionados

- `docs/apps/README.md`
- `docs/apps/02-Secretaria.md`
- `docs/sistema/REGRAS_TIPOS_PESSOA_STATUS.md` — referência histórica/legada; não é autoridade normativa atual
- `docs/sistema/CARGOS_USUARIOS.md` — referência histórica/legada; não é autoridade normativa atual
- `docs/sistema/CARGOS_SISTEMA.md` — referência histórica/legada; não é autoridade normativa atual
- `docs/seguranca/08-Seguranca-de-Dados-e-Privacidade.md`
- `docs/seguranca/14-Conformidade-e-LGPD.md`
- `docs/backend/README.md`
- `docs/qualidade/README.md`

---

# 21. Princípios Finais

O domínio Membros deve preservar a diferença entre:

```text
quem a pessoa é no relacionamento com a igreja
+
qual é sua situação atual
+
quais funções exerce
+
quais permissões possui
```

Esses conceitos são relacionados, mas não equivalentes.

O objetivo é manter um cadastro coerente, histórico e seguro, sem acoplar identidade, cargo e autorização de forma indevida.

---

# 22. Status

**Pasta:** `docs/apps/`

**Arquivo:** `01-Membros.md`

**Documento:** `APP-01`

**Versão:** `1.1`

**Status:** **DOCUMENTAÇÃO FUNCIONAL EM CONSOLIDAÇÃO**

Este documento consolida comportamento implementado, convenções funcionais/históricas e lacunas identificadas no domínio Membros. Ele não substitui documentação técnica, não transforma referências legadas em autoridade normativa e não declara como vigente regra ainda não implementada.
