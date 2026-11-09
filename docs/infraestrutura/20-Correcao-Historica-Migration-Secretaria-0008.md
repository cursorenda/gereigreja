Pasta:
docs/infraestrutura/

Arquivo:
20-Correcao-Historica-Migration-Secretaria-0008.md

Documento:
GINF-20

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

# 20 - Correcao historica da migration Secretaria 0008

## Sumario

1. Objetivo
2. Causa historica
3. Correcao
4. Compatibilidade
5. Documentos relacionados
6. Principios finais

## 1. Objetivo

Registrar a neutralizacao das operacoes duplicadas da migration
`secretaria.0008_remove_membroscargos_cargo_and_more`.

## 2. Causa historica

A migration `secretaria.0006_cargo_membrocargo_alter_membro_options_and_more`
ja cria os modelos e tabelas de `Cargo` e `MembroCargo`. A `0008` repetia os
mesmos `CreateModel`, fazendo um banco novo falhar ao tentar recriar
`secretaria_cargo` e `secretaria_membrocargo`.

## 3. Correcao

As dependencias e o nome da `0008` foram preservados, mas suas operacoes foram
transformadas em no-op. A cadeia continua registrando a migration normalmente,
sem executar alteracao de schema duplicada.

## 4. Compatibilidade

Em bancos nos quais a `0008` ja esta registrada, o Django nao volta a executa-la;
portanto, a neutralizacao nao modifica tabelas ou dados existentes. Em bancos
novos, `Cargo` e `MembroCargo` permanecem criados pela `0006`, permitindo que a
cadeia avance. Nao ha mudanca no schema funcional esperado nem backfill.

## 5. Documentos relacionados

- `docs/infraestrutura/05-Banco-de-Dados-e-Persistencia.md`
- `docs/infraestrutura/19-Matriz-de-Ambientes-e-Comandos-Seguros.md`
- `docs/backend/18-Testing.md`

## 6. Principios finais

Uma migration historica duplicada deve ser neutralizada no ponto que bloqueia o
bootstrap, preservando dependencias, dados existentes e o estado final esperado.

## Status

Correcao historica documentada e vigente.
