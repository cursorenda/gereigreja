# Release notes — v1.15.0

Data: 09/11/2026

Tipo: MINOR

## Escopo

Esta versão entrega quatro frentes: estrutura de departamentos ministeriais, isolamento do tenant de demonstração, escopo canônico de igreja com revisão de permissões e separação segura dos ambientes local e de teste.

## Departamentos ministeriais

- Novo modelo `DepartamentoMinisterial`, com capacidades e classificação.
- Novo modelo de vínculo `DepartamentoVinculo` entre pessoa e departamento.
- Hub do departamento, visão "meus departamentos" e tela de gestão ministerial.
- Novo serviço `configuracao/services_departamentos.py`, centralizando as regras do domínio.
- Menu e design system atualizados para expor a nova camada.
- Migrations aditivas `configuracao.0040`, `0041` e `0042`.

## Isolamento do tenant Demo

- Novo campo `Ministerio.is_demo` (migration `configuracao.0043`), indexado.
- Envios reais de comunicação (WhatsApp e e-mail) são neutralizados quando o ministério é Demo.
- Novo serviço `core/services/email.py`, centralizando envio e neutralização.
- Comando `popular_demo` passa a marcar o tenant Demo explicitamente, em vez de depender de heurística.
- Removido o handler legado `enviar_whatsapp_novo_membro`, que referenciava símbolos não importados e provocava `NameError` no `post_save` de `secretaria.Pessoa`. A automação de boas-vindas permanece em `comunicacao.services`, executada por lote/cron com proteção de duplicidade.

## Escopo canônico de igreja e permissões

- Novo helper `core.utils.get_igrejas_selecionaveis()`, que define o escopo organizacional do seletor de igreja sem conceder permissão funcional.
- `ActiveChurchMiddleware` passa a validar a igreja ativa da sessão contra o escopo canônico. Igreja fora do escopo é removida da sessão, com registro em log.
- Seleção automática de igreja quando o usuário possui exatamente uma igreja no escopo.
- Cache por requisição para grupos do usuário, ministério do usuário e módulos permitidos, reduzindo consultas repetidas.
- Nova função `contas.page_permissions.pode_acessar_financeiro()`, que restringe a entrada de Administrador do Ministério no módulo Financeiro a igreja ativa do tipo Sede ou Independente, dentro do escopo canônico.

## Financeiro, Eventos e cadastro de pessoas

- As contas a pagar seguem a autorização configurada para cada igreja, com proteções contra pagamentos repetidos e operações fora do escopo.
- As lições da Escola Bíblica podem ser sincronizadas preservando eventos existentes.
- O histórico de pessoas permanece consistente com as mudanças de cadastro e o rodapé exibe a versão oficial.
- A limpeza do ambiente demo preserva a estrutura e é interrompida se detectar referências financeiras de fora do demo.

## Comportamento alterado

- Administrador do Ministério passa a abrir o Centro Ministerial (`configuracao:centro_ministerial`) após o login, em vez do portal do membro.
- Entrada no módulo Financeiro para Administrador do Ministério passa a exigir igreja ativa válida do tipo Sede ou Independente. Regional, Congregação, ausência de igreja ativa e igreja fora do escopo são negadas.
- Comportamento de Pastor Local e Tesoureiro no Financeiro permanece inalterado.
- Entrada no módulo Financeiro não concede poderes internos equivalentes aos de Tesoureiro.

## Correções

- Leitura da versão do `CHANGELOG.md` pelo módulo de deploy passa a reconhecer o formato canônico `# vX.Y.Z`. Antes, o parser não encontrava a versão e retornava `1.0.0`, produzindo incrementos incorretos.
- `secretaria.signals` deixa de tentar processar transição de status com `data_transicao` nula.

## Ambientes

- `manage.py` passa a usar `core.settings_local` como padrão, em vez de `core.settings`.
- Novos `core/settings_local.py` e `core/settings_test_migrations.py`.
- `core/settings_test.py` passa a herdar do ambiente local seguro, evitando carregar configuração produtiva antes dos overrides da suíte.

## Migrations relevantes

```text
configuracao.0040_departamento_capacidades_e_classificacao
configuracao.0041_departamentoministerial_departamento_departamento_ministerial
configuracao.0042_departamentovinculo
configuracao.0043_ministerio_is_demo
```

O intervalo também inclui Comunicação 0011, Eventos 0019 e Financeiro 0019 a 0024. Verificar o preflight de duplicidade em Financeiro 0023 antes da aplicação da restrição de unicidade 0024.

Migrations históricas modificadas nesta versão, isoladas para rastreabilidade:

```text
contas.0003_add_pastor_local_group
secretaria.0008_remove_membroscargos_cargo_and_more
secretaria.0014_remove_membroscargos_cargo_and_more
```

## Impactos operacionais

- A validação de igreja ativa passa a depender do escopo canônico. Sessões cujo vínculo de igreja foi alterado podem perder a igreja ativa e exigir nova seleção.
- A migration de dados de `0043` marca o tenant Demo histórico de forma idempotente.
- A aplicação das migrations é obrigatória antes de subir esta versão, pois o modelo `Ministerio` já referencia `is_demo`.

## Riscos e observações

- A suíte completa do projeto ainda apresenta quatro falhas conhecidas e independentes desta versão, registradas em backlog local: automação de e-mail em Comunicação, geração de cronograma da Escola Bíblica, API de localidades de Configuração e acesso de professor à própria turma na Escola Bíblica.
- A detecção de ambiente Demo depende de marcação explícita. Ministérios reais não são afetados.

## Referências técnicas

```text
core/services/email.py
core/utils.py
core/middleware.py
contas/page_permissions.py
contas/constants.py
configuracao/services_departamentos.py
configuracao/services_assinatura.py
```

## Publicação

Consultar `docs/deploy/Deploy-Release-v1.15.0.md`.