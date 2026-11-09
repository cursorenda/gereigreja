# Especificação — Acesso Contextual do Admin Ministério ao Financeiro

Data: Setembro de 2026
Status: IMPLEMENTADA — Commit 8 em preparação
Prioridade: ALTA

## 1. Objetivo

O Commit 8 implementa uma regra de entrada contextual no módulo Financeiro.

Ela permite o acesso de usuários com o papel funcional `ADMIN_MINISTERIO` somente quando houver uma igreja concreta, autorizada no escopo canônico, dos tipos:

```text
Sede
Independente
```

A mudança preserva a elegibilidade histórica abstrata de `PASTOR_LOCAL` e `TESOUREIRO` quando não existe igreja concreta e o módulo Financeiro está habilitado.

Esta regra controla somente a entrada no módulo. Ela não concede automaticamente poderes equivalentes aos de Tesoureiro nem substitui os controles internos das Views, policies, querysets e operações financeiras.

## 2. Tipos de igreja considerados

Os tipos de igreja considerados pela regra são os valores reais normalizados de `Igreja`:

```text
Sede
Regional
Congregação
Independente
```

Para `ADMIN_MINISTERIO`, somente `Sede` e `Independente` são elegíveis. `Regional` e `Congregação` são negadas.

## 3. Regra funcional implementada

### Requisitos comuns

Antes de avaliar papel e contexto, a regra exige:

```text
usuário autenticado
+
módulo Financeiro habilitado
```

Usuário não autenticado é negado. Módulo Financeiro desabilitado também resulta em negação.

### Resolução de contexto

A igreja de contexto é resolvida nesta ordem:

```text
igreja= explícita
→ tem precedência

request.igreja_ativa
→ usada somente quando igreja= não foi informada
```

`Pessoa.igreja` não é fallback de autorização contextual. O vínculo de pessoa pode participar de outras resoluções do sistema, mas não transforma uma igreja em contexto financeiro autorizado nesta regra.

### Pastor Local e Tesoureiro

Sem igreja concreta:

```text
PASTOR_LOCAL ou TESOUREIRO
+
módulo Financeiro habilitado
+
sem igreja concreta
→ permitir elegibilidade abstrata histórica
```

Com igreja concreta, Pastor Local e Tesoureiro precisam ter a igreja no escopo canônico retornado por:

```python
get_igrejas_selecionaveis(
    user,
    ministerio=igreja_contexto.ministerio,
).filter(pk=igreja_contexto.pk).exists()
```

Igreja concreta fora desse escopo é negada. A regra não expande hierarquia nem usa `Pessoa.igreja` para compensar ausência de escopo canônico.

### Admin Ministério

`ADMIN_MINISTERIO` sempre exige igreja concreta. A entrada é permitida somente quando todos os requisitos abaixo são satisfeitos:

```text
ADMIN_MINISTERIO
+
módulo Financeiro habilitado
+
igreja concreta no escopo canônico
+
tipo ∈ {Sede, Independente}
→ permitir entrada no módulo
```

Portanto:

```text
Admin sem igreja concreta
→ negar

Admin + Regional
→ negar

Admin + Congregação
→ negar

Admin + igreja fora do escopo
→ negar
```

### Superuser

`is_superuser` não cria papel financeiro funcional implícito.

```text
is_superuser
≠
bypass automático de page access
```

Um superuser sem papel funcional reconhecido pela política é negado. Um superuser que também possua papel funcional válido segue a regra normal desse papel; este Commit 8 não cria semântica especial para superuser.

## 4. Princípio de segurança

O tipo da igreja não é uma permissão isolada. A decisão de entrada combina, conforme o papel:

```text
autenticação
+
módulo Financeiro habilitado
+
papel funcional reconhecido
+
contexto concreto, quando exigido
+
escopo canônico da igreja
+
tipo de igreja elegível para Admin Ministério
```

O controle de page access não substitui isolamento multi-tenant de dados. Views e operações financeiras continuam responsáveis por aplicar filtros, querysets e policies internos ao contexto autorizado.

## 5. Implementação aplicada

A política de entrada foi centralizada em:

```text
contas/page_permissions.py
```

`pode_acessar_financeiro(user, request=None, igreja=None)` aplica a autenticação, a habilitação do módulo, a resolução explícita de contexto e a validação canônica de escopo descritas nesta especificação.

`PAGE_ACCESS_RULES['financeiro']` delega para essa função.

O decorator existente `@page_access_required('financeiro')` continua sendo a porta de proteção das páginas financeiras e não precisou ser alterado.

## 6. Dispatcher contextual limitado

O dispatcher `user_can_access_page()` não foi tornado genérico ou reflexivo.

Somente a chave `financeiro` recebe o contexto adicional:

```python
rule(user, request=request, igreja=igreja)
```

As demais page keys continuam sendo invocadas como no comportamento anterior:

```python
rule(user)
```

Não há uso de `inspect.signature()` nem encaminhamento contextual genérico neste Commit 8.

### Secretaria

Este Commit 8 não altera a semântica de Secretaria por meio do dispatcher. As regras de Secretaria continuam recebendo somente `user` pelo dispatcher, sem `request` ou `igreja` encaminhados acidentalmente por esta mudança.

## 7. Contexto de sessão inválido

O middleware pode invalidar ou remover um contexto de igreja da sessão antes da avaliação da política de page access. Nessa situação, `request.igreja_ativa` pode estar ausente.

Quando não há igreja concreta após essa etapa, Pastor Local e Tesoureiro preservam sua elegibilidade abstrata histórica, desde que o módulo Financeiro esteja habilitado. Isso não significa autorização irrestrita sobre dados financeiros: o acesso a dados e operações permanece condicionado aos controles internos do backend.

Esta especificação não afirma que uma igreja inválida armazenada na sessão produz necessariamente `403` para Pastor Local ou Tesoureiro.

## 8. Limite da autorização de entrada

Entrada no módulo Financeiro não equivale a poderes internos de Tesoureiro:

```text
acesso ao módulo
≠
criar, editar, excluir, aprovar, transferir, fechar, reabrir ou exportar sem controles próprios
```

O Commit 8 não revisa nem declara cobertura de todas as operações internas do Financeiro. Cada operação continua sujeita à sua política, View, service, queryset e regra de negócio aplicáveis.

## 9. Cobertura efetivamente implementada

Os testes unitários em `contas/tests/test_page_permissions.py` comprovam, entre outros, os seguintes comportamentos:

| Cenário | Resultado comprovado |
|---|---|
| `AnonymousUser` | Negado |
| Módulo Financeiro desabilitado para Pastor/Tesoureiro | Negado |
| Pastor/Tesoureiro sem igreja concreta e módulo habilitado | Elegibilidade abstrata preservada |
| Pastor/Tesoureiro com igreja concreta permitida | Permitido |
| Pastor/Tesoureiro com igreja concreta fora do escopo | Negado |
| `request.igreja_ativa` permitida ou fora do escopo | Permitido ou negado conforme escopo |
| `igreja=` explícita versus `request.igreja_ativa` | A igreja explícita prevalece |
| `Pessoa.igreja` sem `PerfilUsuario`/escopo canônico | Não autoriza contexto concreto |
| Admin sem igreja concreta | Negado |
| Admin + Sede ou Independente no escopo | Permitido |
| Admin + Regional, Congregação ou igreja fora do escopo | Negado |
| Superuser sem papel funcional | Negado |
| Chave Financeiro no dispatcher | Recebe `request` e `igreja` |
| Regra comum no dispatcher | Recebe somente `user` |
| Regra de Secretaria no dispatcher | Não recebe contexto acidentalmente |
| Chave desconhecida | Negada |
| `TypeError` interno de regra comum | Propagado |

Os testes de integração em `tests/test_financeiro_admin_integration.py` exercitam o fluxo real protegido por `@page_access_required('financeiro')`, incluindo:

```text
Admin + Sede → 200
Admin + Independente → 200
Admin + Regional → 403
Admin + Congregação → 403
Admin sem igreja ativa → 403
Admin com igreja de outro ministério → 403
Pastor/Tesoureiro com igreja permitida → 200
Superuser sem papel funcional → 403
troca Sede → Congregação → Independente para Admin
→ 200 → 403 → 200
```

## 10. Evidências executadas

As validações realizadas para a implementação atual foram:

```text
contas.tests.test_page_permissions
→ 27 testes OK

tests.test_financeiro_admin_integration
→ 10 testes OK (validação isolada anterior)

contas.tests.test_page_permissions
+ tests.test_financeiro_admin_integration
→ 37 testes OK
```

As evidências registradas se limitam à política de entrada, ao dispatcher e aos cenários de integração listados. Elas não representam auditoria completa das permissões internas de todas as funcionalidades financeiras.

## 11. Arquivos envolvidos no Commit 8

Implementação e testes:

```text
contas/page_permissions.py
contas/tests/test_page_permissions.py
tests/test_financeiro_admin_integration.py
```

Documentação desta especificação:

```text
docs/produto/ESPECIFICACAO-ACESSO-FINANCEIRO-ADMIN-MINISTERIO.md
```

Não foram necessários ajustes em `core/decorators.py`, documentação transversal de Backend/Segurança/Usuários ou no documento amplo `docs/apps/03-Financeiro.md`.

## 12. Critérios e evidências atingidos

```text
1. Usuário não autenticado é negado.
2. Módulo Financeiro habilitado é requisito.
3. Igreja explícita prevalece sobre request.igreja_ativa.
4. Pessoa.igreja não é fallback contextual.
5. Pastor e Tesoureiro preservam elegibilidade abstrata sem igreja concreta.
6. Pastor e Tesoureiro são negados para igreja concreta fora do escopo.
7. Admin acessa Sede e Independente no escopo canônico.
8. Admin é negado sem contexto, em Regional, Congregação e fora do escopo.
9. Superuser não se torna papel financeiro implícito.
10. Dispatcher contextual é limitado a Financeiro.
11. Secretaria não recebe contexto por acidente no dispatcher.
12. Testes unitários e de integração cobrem os cenários de entrada e troca de contexto documentados.
```

## 13. Decisão final

Regra de entrada contextual do Admin Ministério:

```text
ADMIN_MINISTERIO
+
módulo Financeiro habilitado
+
igreja concreta no escopo canônico
+
tipo ∈ {Sede, Independente}
→ permite entrada no módulo
```

Para `Regional`, `Congregação`, ausência de igreja concreta ou igreja fora do escopo, não há concessão automática ao Admin Ministério.

Para Pastor Local e Tesoureiro, a compatibilidade abstrata sem igreja concreta é preservada; quando há igreja concreta, a entrada depende do escopo canônico. A autorização das operações financeiras internas permanece separada da autorização de entrada no módulo.
