# Release v1.15.0 — Departamentos ministeriais, tenant Demo isolado e escopo de igreja

Data: 14/09/2026

## Destaques

- Departamentos ministeriais passam a existir como estrutura própria, com capacidades, classificação e vínculo explícito entre pessoa e departamento.
- Ambiente de demonstração passa a ser reconhecido pelo sistema, bloqueando envios reais de WhatsApp e e-mail a partir do tenant Demo.
- Escopo de igreja do usuário torna-se explícito e canônico: igreja ativa fora do escopo é descartada, e a seleção automática só ocorre quando existe exatamente uma igreja no escopo.
- Administrador do Ministério passa a abrir o Centro Ministerial após o login, em vez do portal do membro.
- Entrada no módulo Financeiro para Administrador do Ministério passa a depender de igreja ativa do tipo Sede ou Independente, sem conceder poderes internos equivalentes aos de Tesoureiro.
- Ambientes local, teste e teste de migration ficam separados do fluxo produtivo legado.

## Validação

- Testes focados executados e aprovados em `deploy`, `demo`, `contas` e integração de Financeiro para Administrador do Ministério.
- `python manage.py check --settings=core.settings_test` sem issues.
- Smoke test manual do fluxo Demo aprovado: Sede ativa expõe operação local e Financeiro; Regional e Congregação não expõem.
- Suíte completa do projeto ainda possui 4 falhas conhecidas e independentes desta versão, registradas em backlog local (Comunicação, EBD e API de localidades).

## Migrations

- `configuracao.0040_departamento_capacidades_e_classificacao`
- `configuracao.0041_departamentoministerial_departamento_departamento_ministerial`
- `configuracao.0042_departamentovinculo`
- `configuracao.0043_ministerio_is_demo`

Todas são aditivas. Nenhuma remove campo ou altera contrato existente.

## Riscos e observações

- `Ministerio.is_demo` é indexado; a marcação do tenant Demo histórico é feita por migration de dados idempotente.
- A validação de igreja ativa passa a depender do escopo canônico, o que pode remover igreja de sessões cujo vínculo foi alterado.
- As migrations históricas modificadas (`contas.0003`, `secretaria.0008`, `secretaria.0014`) são isoladas no registro de deploy.

## Publicação

- Tipo: MINOR
- Branch de publicação: `master`