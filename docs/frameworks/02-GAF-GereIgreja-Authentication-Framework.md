Pasta:
docs/frameworks/

Arquivo:
02-GAF-GereIgreja-Authentication-Framework.md

Documento:
GAF-02

Framework:
GAF — GereIgreja Authentication Framework

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# 02 - GereIgreja Authentication Framework (GAF)

> "A autenticação confirma quem é o usuário. A autorização define o que ele pode fazer."

---

# Sumário

1. Objetivo
2. O que é o GAF
3. Filosofia
4. Princípios
5. Arquitetura Geral
6. Autenticação
7. Autorização
8. Papéis (Roles)
9. Grupos
10. Permissões
11. Escopos
12. Herança de Permissões
13. Segurança
14. Auditoria
15. Evolução
16. Checklist
17. Documentos Relacionados
18. Princípios Finais

---

# 1. Objetivo

O GereIgreja Authentication Framework (GAF) estabelece o padrão oficial para autenticação, autorização e gerenciamento de permissões da plataforma.

Seu objetivo é garantir segurança, organização, escalabilidade e reutilização em todos os módulos do GereIgreja.

---

# 2. O que é o GAF

O GAF é o framework responsável por controlar todo o acesso à plataforma.

Ele define:

- autenticação;
- autorização;
- papéis;
- grupos;
- permissões;
- escopos;
- herança de permissões;
- auditoria de acesso.

Nenhum módulo deverá implementar um modelo próprio de autenticação.

---

# 3. Filosofia

Todo usuário deverá possuir apenas as permissões necessárias para executar seu trabalho.

O acesso sempre deverá seguir o princípio do menor privilégio.

Permissões nunca deverão ser concedidas por conveniência.

---

# 4. Princípios

O GAF baseia-se em:

- menor privilégio;
- separação de responsabilidades;
- autenticação obrigatória;
- autorização explícita;
- auditoria completa;
- simplicidade;
- reutilização;
- segurança por padrão.

---

# 5. Arquitetura Geral

Todo acesso seguirá o fluxo abaixo.

```text
Usuário
   │
   ▼
Login
   │
   ▼
Autenticação
   │
   ▼
Tenant
   │
   ▼
Grupo
   │
   ▼
Permissões
   │
   ▼
View
   │
   ▼
Service
```

Nenhuma operação deverá ignorar esse fluxo.

---

# 6. Autenticação

A autenticação identifica o usuário.

O GereIgreja utilizará os mecanismos oficiais do Django.

A arquitetura deverá permitir evolução para:

- MFA;
- OAuth2;
- JWT;
- SSO;
- Login Social.

---

# 7. Autorização

Após autenticado, todo usuário deverá possuir autorização explícita.

Toda View, API ou Service deverá validar permissões antes da execução.

Nunca confiar apenas na interface.

---

# 8. Papéis (Roles)

Os papéis representam funções organizacionais.

Exemplos:

- Administrador SaaS
- Suporte
- Pastor Presidente
- Pastor Regional
- Pastor Local
- Secretário
- Tesoureiro
- Superintendente
- Líder
- Professor
- Membro

Os papéis facilitam a organização das permissões.

---

# 9. Grupos

Os grupos representam conjuntos reutilizáveis de permissões.

Um grupo poderá conter dezenas de permissões.

Os usuários deverão receber permissões preferencialmente por grupos.

Permissões individuais deverão ser exceção.

---

# 10. Permissões

Cada permissão deverá representar uma única capacidade.

Exemplos:

- visualizar membros;
- cadastrar membros;
- editar membros;
- excluir membros;
- aprovar despesas;
- emitir relatórios.

Permissões deverão possuir nomes padronizados.

---

# 11. Escopos

O GereIgreja possui dois escopos principais.

## SaaS

Administração da plataforma.

## Igreja

Administração da organização.

Os escopos nunca deverão se misturar.

---

# 12. Herança de Permissões

Papéis superiores poderão herdar permissões dos níveis inferiores.

Exemplo:

```text
Pastor Presidente
        │
        ▼
Pastor Regional
        │
        ▼
Pastor Local
        │
        ▼
Líder
```

A herança deverá ser explícita e documentada.

---

# 13. Segurança

Todo mecanismo deverá considerar:

- bloqueio de sessões inválidas;
- proteção contra força bruta;
- expiração de sessão;
- alteração segura de senha;
- recuperação de acesso;
- autenticação segura.

---

# 14. Auditoria

Toda alteração relevante deverá ser registrada.

Exemplos:

- login;
- logout;
- alteração de permissões;
- troca de senha;
- criação de grupos;
- remoção de usuários.

---

# 15. Evolução

O framework deverá permitir expansão sem quebra de compatibilidade.

Novos papéis poderão ser criados.

Novos mecanismos de autenticação poderão ser incorporados.

A arquitetura deverá permanecer estável.

---

# 16. Checklist

Antes da publicação verificar:

- autenticação implementada;
- permissões revisadas;
- grupos definidos;
- herança documentada;
- auditoria ativa;
- testes previstos.

---

# 17. Documentos Relacionados

- GEA-07 — Arquitetura da Segurança
- GEA-08 — Arquitetura Multi-Tenant
- GDS — GereIgreja Design System
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework

---

# 18. Princípios Finais

O GAF centraliza toda a estratégia de autenticação e autorização do GereIgreja.

Sua adoção garante consistência entre os módulos, reduz riscos de segurança e facilita a administração da plataforma.

Toda funcionalidade deverá utilizar exclusivamente os mecanismos definidos neste framework.