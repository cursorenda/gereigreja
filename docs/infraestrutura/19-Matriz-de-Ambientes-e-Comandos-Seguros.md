Pasta:
docs/infraestrutura/

Arquivo:
19-Matriz-de-Ambientes-e-Comandos-Seguros.md

Documento:
GINF-19

Framework:
GINF - GereIgreja Infraestrutura

Versao:
1.0

Status:
Oficial

Responsavel:
Equipe de Engenharia

Ultima atualizacao:
Agosto de 2026

# 19 - Matriz de Ambientes e Comandos Seguros

## Sumario

1. Objetivo
2. Matriz oficial
3. Comandos seguros
4. Regras locais
5. Producao explicita
6. Documentos relacionados
7. Principios finais

## 1. Objetivo

Definir os settings e bancos permitidos em comandos locais, testes e producao, com negacao segura diante de ambiente ambiguo.

## 2. Matriz oficial

| Contexto | Settings | Banco | Uso |
|---|---|---|---|
| Desenvolvimento local | `core.settings_local` | SQLite local em `db.sqlite3` | `runserver`, `check` e comandos locais |
| Testes | `core.settings_test` | SQLite em memoria | Suite funcional e regressao |
| Testes de migrations | `core.settings_test_migrations` | SQLite em memoria | Validacao isolada da sequencia real de migrations |
| Producao | `core.settings` | PostgreSQL definido pelo ambiente produtivo | Somente processo produtivo explicitamente autorizado |

`manage.py` seleciona `core.settings_local` quando nenhum settings foi declarado. Um `DJANGO_SETTINGS_MODULE` ja definido ou `--settings` explicito continua tendo precedencia.

## 3. Comandos seguros

```powershell
python manage.py check
python manage.py runserver
python manage.py test --settings=core.settings_test
python manage.py test configuracao.tests --settings=core.settings_test
python manage.py test configuracao.tests.test_migration_0040_departamentos --settings=core.settings_test_migrations
```

Testes comuns sempre usam `core.settings_test`. Testes que precisam executar migrations reais usam exclusivamente `core.settings_test_migrations`.

## 4. Regras locais

- O fluxo local nao carrega `.env`.
- `core.settings_local` fixa SQLite e nao aceita host PostgreSQL remoto.
- Credenciais ou variaveis remotas presentes no processo nao mudam o banco local.
- A ausencia de `--settings` nunca autoriza producao.
- Ambiente ambiguo deve interromper a operacao.

## 5. Producao explicita

`core.settings` permanece temporariamente como settings produtivo legado. Ele nao deve ser usado em desenvolvimento, testes ou comandos do Codex.

Migration, backup ou diagnostico produtivo exige autorizacao explicita, identificacao inequivoca do ambiente, backup recuperavel, plano revisado e comando de alvo exato. Pedidos genericos para rodar migration, teste ou check nao concedem acesso a producao.

Nesta fase, WSGI, ASGI e o processo de deploy produtivo nao foram alterados.

## 6. Documentos relacionados

- `docs/infraestrutura/02-Ambientes-e-Configuracao.md`
- `docs/infraestrutura/05-Banco-de-Dados-e-Persistencia.md`
- `docs/infraestrutura/09-CI-CD-Deploy-e-Rollback.md`
- `docs/seguranca/09-Seguranca-de-Infraestrutura-e-Segredos.md`
- `docs/desenvolvimento/Como-Rodar-Testes.md`
- `AGENTS.md`

## 7. Principios finais

O ambiente local deve ser seguro sem depender da memoria do operador. Producao deve ser sempre uma escolha explicita, controlada e auditavel.

## Status

Documento oficial e vigente para a Fase 1 da segregacao de ambientes.
