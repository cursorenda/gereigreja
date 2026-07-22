Pasta:
docs/backend/

Arquivo:
11-Permissions.md

Documento:
GBE-11

Seção:
Backend

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# 11 - Permissions

> *"Permissões não servem apenas para impedir acessos indevidos. Elas representam as responsabilidades e os limites de atuação de cada usuário dentro da plataforma."*

---

# Sumário

1. Objetivo
2. Filosofia das Permissões
3. O Papel das Permissões no GereIgreja
4. Autenticação x Autorização
5. Fluxo Oficial de Autorização
6. Modelo de Segurança
7. Estrutura Oficial
8. Permissões do Django
9. Grupos
10. Papéis (Roles)
11. Boas Práticas
12. Documentos Relacionados
13. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para implementação das permissões no Backend do GereIgreja.

Seu propósito é garantir que todas as funcionalidades da plataforma respeitem um modelo único de autorização, reduzindo inconsistências e fortalecendo a segurança da aplicação.

---

# 2. Filosofia das Permissões

No GereIgreja, permissões representam **o que um usuário pode fazer**, e não quem ele é.

Elas devem ser:

- simples;
- previsíveis;
- reutilizáveis;
- auditáveis;
- centralizadas.

Nenhuma regra de autorização deverá ficar espalhada pela aplicação.

---

# 3. O Papel das Permissões no GereIgreja

As permissões controlam o acesso às funcionalidades da plataforma.

Exemplos:

- visualizar membros;
- cadastrar membros;
- editar eventos;
- excluir movimentações financeiras;
- aprovar solicitações;
- administrar usuários.

Toda ação protegida deverá possuir uma permissão correspondente.

---

# 4. Autenticação x Autorização

São conceitos distintos.

## Autenticação

Responde à pergunta:

> Quem é o usuário?

É responsabilidade do GAF.

---

## Autorização

Responde à pergunta:

> O usuário pode executar esta ação?

É responsabilidade das permissões.

Um usuário autenticado não possui automaticamente autorização para todas as operações.

---

# 5. Fluxo Oficial de Autorização

Todo acesso deverá seguir o fluxo abaixo.

```text
Usuário

↓

Login

↓

Autenticação

↓

Permissões

↓

View

↓

Service

↓

Resposta
```

Nenhuma View protegida deverá ser executada antes da verificação das permissões.

---

# 6. Modelo de Segurança

O GereIgreja utiliza um modelo baseado em:

- Usuários;
- Grupos;
- Permissões;
- Papéis funcionais;
- Escopo organizacional.

Esse modelo permite reutilização e facilita a administração da plataforma.

---

# 7. Estrutura Oficial

As permissões deverão ser organizadas por domínio.

Exemplo:

```text
membros.view_membro

membros.add_membro

membros.change_membro

membros.delete_membro
```

Outro exemplo:

```text
financeiro.view_lancamento

financeiro.add_lancamento

financeiro.aprovar_lancamento
```

A nomenclatura deverá seguir um padrão consistente em todos os Apps.

---

# 8. Permissões do Django

Sempre que possível utilizar o sistema nativo de permissões do Django.

As permissões personalizadas deverão ser declaradas explicitamente nos Models quando necessário.

Exemplo:

```python
class Meta:

    permissions = [

        ("aprovar_lancamento", "Pode aprovar lançamentos financeiros"),

        ("fechar_caixa", "Pode realizar fechamento de caixa"),
    ]
```

Permissões customizadas devem representar ações de negócio claramente identificáveis.

---

# 9. Grupos

Os grupos representam conjuntos de permissões.

Exemplos existentes no GereIgreja:

- Administrador Ministerial;
- Pastor Regional;
- Pastor Local;
- Secretário;
- Tesoureiro;
- Superintendente da EBD;
- Professor da EBD;
- Equipe de Eventos;
- Equipe de Mídia;
- Membro.

Os grupos facilitam a administração e reduzem a necessidade de configurar permissões individualmente.

---

# 10. Papéis (Roles)

Os papéis representam funções desempenhadas pelos usuários dentro da organização.

Um papel poderá estar associado a um ou mais grupos de permissões.

Essa abordagem permite flexibilidade sem comprometer a padronização da arquitetura.

---

# 11. Boas Práticas

- utilizar grupos sempre que possível;
- evitar permissões atribuídas diretamente a usuários;
- utilizar nomes padronizados;
- manter permissões reutilizáveis;
- revisar permissões durante o desenvolvimento de novas funcionalidades.

---

# 12. Documentos Relacionados

- GAF — GereIgreja Authentication Framework
- GSF — GereIgreja Security Framework
- GBE-08 — Views
- GBE-10 — Validators
- GEA-02 — Arquitetura da Plataforma

---

# 13. Princípios Finais

As permissões representam um dos principais mecanismos de segurança da plataforma.

Sua implementação deve ser consistente, centralizada e alinhada aos princípios definidos pelo GAF.

Toda funcionalidade protegida deverá possuir uma estratégia clara de autorização, preservando a segurança e a integridade do GereIgreja.

---

# 14. Implementação nas Views

As Views representam a primeira camada de proteção da aplicação.

Toda View que expuser dados ou funcionalidades protegidas deverá validar as permissões do usuário antes da execução da lógica de negócio.

Nunca confiar apenas na interface.

---

## Function Based Views (FBV)

Para Function Based Views utilizar preferencialmente os decorators oficiais.

Exemplo:

```python
@login_required
@permission_required(
    "membros.view_membro",
    raise_exception=True
)
def lista_membros(request):
    ...
```

Quando houver múltiplas permissões, utilizar composição clara e legível.

---

## Class Based Views (CBV)

Para Class Based Views utilizar preferencialmente:

```python
PermissionRequiredMixin
```

Exemplo:

```python
class MembroListView(
    PermissionRequiredMixin,
    ListView
):

    permission_required = (
        "membros.view_membro",
    )
```

Sempre declarar explicitamente as permissões necessárias.

---

## Múltiplas Permissões

Quando uma View exigir mais de uma permissão:

```python
permission_required = (

    "financeiro.view_lancamento",

    "financeiro.aprovar_lancamento",
)
```

Evitar verificações espalhadas ao longo do código.

Toda autorização deverá ocorrer antes da execução da View.

---

# 15. Permissões nos Services

Services representam a camada oficial de regras de negócio.

Mesmo que uma View valide permissões, um Service reutilizável poderá realizar validações adicionais quando houver risco de utilização por outras interfaces.

Exemplo:

```text
Painel Web

↓

Service

↑

API
```

Dessa forma, qualquer interface continuará respeitando as mesmas regras de autorização.

---

## Validação Defensiva

Sempre que uma operação crítica puder ser reutilizada por múltiplos pontos da aplicação, recomenda-se validar o contexto do usuário dentro do próprio Service.

Exemplos:

- fechamento financeiro;
- aprovação de lançamentos;
- alteração de permissões;
- exclusão em massa;
- geração de documentos oficiais.

---

# 16. Escopo Organizacional

O GereIgreja utiliza um modelo Multi-Tenant.

Assim, possuir uma permissão não significa possuir acesso irrestrito.

O usuário também deverá respeitar seu escopo organizacional.

Exemplo:

```text
Ministério

↓

Igreja

↓

Congregação

↓

Departamento
```

As permissões deverão ser interpretadas juntamente com o contexto organizacional.

---

## Exemplos

Um Secretário Local poderá:

- cadastrar membros da sua congregação.

Mas não poderá:

- alterar membros de outra congregação.

Mesmo possuindo a permissão:

```text
membros.change_membro
```

O escopo limita a atuação.

---

# 17. Permissões nas APIs

As APIs deverão utilizar as mesmas regras da aplicação Web.

Sempre que possível utilizar:

- Django Permissions;
- Classes de Permission do DRF;
- Permission Classes customizadas.

Nunca criar regras paralelas apenas para APIs.

O comportamento deverá ser idêntico em qualquer interface.

---

## Exemplo

```python
class PodeEditarMembro(BasePermission):

    def has_permission(self, request, view):

        ...
```

As regras deverão reutilizar o domínio de autorização existente.

---

# 18. Auditoria

Toda operação sensível deverá gerar registro de auditoria.

Exemplos:

- alteração de permissões;
- criação de usuários;
- redefinição de senha;
- fechamento financeiro;
- exportação de dados;
- exclusão de registros;
- alterações administrativas.

O registro deverá conter:

- usuário;
- data;
- horário;
- IP (quando disponível);
- operação realizada;
- objeto afetado.

---

# 19. Tratamento de Acesso Negado

Quando uma autorização falhar:

o sistema deverá:

- impedir a operação;
- registrar o evento quando necessário;
- apresentar mensagem amigável;
- nunca revelar detalhes internos.

Evitar mensagens técnicas.

Exemplo inadequado:

```text
PermissionDenied at /financeiro/lancamentos/...
```

Exemplo recomendado:

```text
Você não possui permissão para executar esta operação.
```

---

# 20. Boas Práticas

Sempre:

- centralizar regras de autorização;
- utilizar grupos;
- utilizar constantes quando necessário;
- reutilizar Permission Mixins;
- manter nomenclatura consistente;
- revisar permissões em Code Review.

Permissões fazem parte da arquitetura.

---

# 21. Anti-patterns

Evitar:

- verificar permissões apenas no Frontend;
- utilizar if espalhados pelo código;
- copiar verificações entre Views;
- conceder permissões diretamente ao usuário sem necessidade;
- ignorar escopo organizacional;
- criar permissões duplicadas.

Toda autorização deve possuir um único padrão oficial.

---

# 22. Checklist

Antes de publicar uma funcionalidade verificar:

- possui autenticação?
- possui autorização?
- utiliza grupos?
- respeita escopo?
- protege APIs?
- protege Views?
- protege Services quando necessário?
- registra auditoria?
- possui documentação?
- possui testes previstos?

---

# 23. Evolução Futura

A arquitetura foi projetada para suportar futuras evoluções.

Entre elas:

- Attribute Based Access Control (ABAC);
- políticas dinâmicas;
- delegação temporária de permissões;
- workflow de aprovações;
- permissões condicionais;
- auditoria avançada;
- integração com provedores externos de identidade.

Essas evoluções deverão preservar compatibilidade com o modelo atual.

---

# 24. Conformidade com o GAF

Este documento complementa o:

**GAF — GereIgreja Authentication Framework**

Enquanto o GAF define os princípios gerais de autenticação e autorização, este documento estabelece os padrões de implementação dessas regras no Backend.

Ambos devem evoluir de forma sincronizada.

---

## ✅ Status

**Pasta:** `docs/backend/`

**Arquivo:** `11-Permissions.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento estabelece o padrão oficial para implementação de permissões e autorização no Backend do GereIgreja, garantindo consistência, segurança e alinhamento com o GAF.

