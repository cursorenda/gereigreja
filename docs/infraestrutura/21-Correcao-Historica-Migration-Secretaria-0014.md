Pasta:
docs/infraestrutura/

Arquivo:
21-Correcao-Historica-Migration-Secretaria-0014.md

Documento:
GINF-21

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

# 21 - Correcao historica da migration Secretaria 0014

## Sumario

1. Objetivo
2. Causa historica
3. Correcao
4. Compatibilidade
5. Documentos relacionados
6. Principios finais

## 1. Objetivo

Registrar a correcao de ordenacao em
`secretaria.0014_remove_membroscargos_cargo_and_more`.

## 2. Causa historica

A migration removia `membroscargos.cargo` antes de eliminar o
`unique_together` que referenciava `membro` e `cargo`. Durante a reconstrucao da
tabela no SQLite, o estado ainda continha a constraint apontando para um campo
ja removido, interrompendo o bootstrap.

## 3. Correcao

`AlterUniqueTogether(..., None)` passou a ocorrer antes dos `RemoveField`. As
demais operacoes permanecem iguais e continuam removendo exclusivamente os
models e tabelas legados `Cargos` e `MembrosCargos`.

## 4. Compatibilidade

Bancos que ja registraram a `0014` nao voltam a executa-la. Em bancos novos, a
ordenacao corrigida produz o mesmo schema funcional esperado: as tabelas
legadas sao removidas, enquanto `Cargo` e `MembroCargo` atuais sao preservados.
Nao ha backfill nem alteracao de dados atuais.

## 5. Documentos relacionados

- `docs/infraestrutura/20-Correcao-Historica-Migration-Secretaria-0008.md`
- `docs/infraestrutura/05-Banco-de-Dados-e-Persistencia.md`
- `docs/infraestrutura/19-Matriz-de-Ambientes-e-Comandos-Seguros.md`

## 6. Principios finais

Constraints devem ser removidas antes dos campos que as compoem, preservando a
reprodutibilidade da cadeia e o schema final historicamente esperado.

## Status

Correcao historica documentada e vigente.
