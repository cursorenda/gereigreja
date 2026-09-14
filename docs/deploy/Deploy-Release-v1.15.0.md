# Deploy & Release Guide — Gereigreja v1.15.0

## Objetivo

Publicar a versão v1.15.0: departamentos ministeriais, isolamento do tenant de demonstração, escopo canônico de igreja com revisão de permissões do Financeiro e separação segura dos ambientes local e de teste.

Esta é uma release **MINOR**. Todas as migrations são aditivas.

## Tipo de Versão

```text
MINOR (1.X.0)
```

Justificativa: introduz funcionalidade nova (departamentos ministeriais, campo `is_demo`, nova regra de acesso ao Financeiro) sem remover campo, renomear contrato existente ou quebrar comportamento para ministérios reais.

## Checklist de Pré-Deploy

- [ ] Backup do banco de produção criado e restore comprovado
- [ ] `python manage.py check --settings=core.settings_test` sem issues
- [ ] Testes focados da release aprovados
- [x] Migrations criadas e revisadas (não aplicadas em produção)
- [x] `CHANGELOG.md` atualizado com v1.15.0
- [x] Release note criada (`docs/release-notes/RELEASE_NOTES_v1.15.0.md`)
- [x] Release summary criado (`docs/release-notes/RELEASE_v1.15.0_SUMMARY.md`)
- [ ] Variáveis de ambiente conferidas no Render
- [ ] Janela de publicação definida fora de horário de pico
- [ ] Suíte completa executada, com as 4 falhas conhecidas registradas como aceitas para esta release

> Itens desmarcados dependem de execução no momento da publicação e de autorização explícita para ambiente produtivo.

## Escopo da Release

### Código Funcional

- `configuracao/models.py` — `DepartamentoMinisterial`, `DepartamentoVinculo`, `Ministerio.is_demo`
- `configuracao/services_departamentos.py` — novo serviço de domínio
- `configuracao/services_assinatura.py` — cache por requisição de ministério e módulos
- `configuracao/forms.py`, `views.py`, `urls.py`, `templatetags/grupo_tags.py`
- `core/services/email.py` — novo serviço de e-mail com neutralização Demo
- `core/utils.py` — `get_igrejas_selecionaveis()`
- `core/middleware.py` — validação canônica da igreja ativa
- `contas/page_permissions.py` — `pode_acessar_financeiro()`
- `contas/constants.py` — cache por requisição de grupos
- `demo/views.py` — landing do Administrador do Ministério
- `comunicacao/signals.py` — remoção do handler legado com `NameError`
- `comunicacao/models.py`, `selectors.py`, `services_whatsapp.py`
- `financeiro/forms.py`, `policies.py`, `services.py`, `utils.py`, `views.py`, `templatetags/financeiro_tags.py`
- `secretaria/signals.py`, `secretaria/management/commands/popular_demo.py`
- `deploy/views.py` — leitura correta da versão do `CHANGELOG.md`

### Templates e Design System

- `templates/base_com_menu.html`, `templates/menu.html`
- `static/css/design_system.css`
- `configuracao/templates/configuracao/departamentos/*`

### Migrations

Novas (aditivas):

```text
configuracao.0040_departamento_capacidades_e_classificacao
configuracao.0041_departamentoministerial_departamento_departamento_ministerial
configuracao.0042_departamentovinculo
configuracao.0043_ministerio_is_demo
```

Históricas modificadas (isoladas para rastreabilidade; revisar antes de aplicar em produção):

```text
contas.0003_add_pastor_local_group
secretaria.0008_remove_membroscargos_cargo_and_more
secretaria.0014_remove_membroscargos_cargo_and_more
```

### Testes

- `deploy/tests/` — parser de versão do CHANGELOG
- `demo/tests/` — landing pós-login
- `contas/tests/test_page_permissions.py` — regra de Financeiro
- `tests/test_financeiro_admin_integration.py` — integração via decorator real
- `configuracao/tests/*` — departamentos, hub, menu, hardening de igreja ativa, migration 0040
- `comunicacao/tests/test_signals.py`, `comunicacao/tests/test_whatsapp_demo_neutralization.py`
- `core/tests/test_email.py`
- `secretaria/tests/test_popular_demo_scope.py`
- `tests/test_secretaria_acesso_por_tipo_igreja.py`, `tests/test_secretaria_historico_tipo_status.py`, `tests/test_financeiro.py`

### Documentação

- Reorganização documental consolidada
- `docs/release-notes/RELEASE_NOTES_v1.15.0.md`
- `docs/release-notes/RELEASE_v1.15.0_SUMMARY.md`
- `docs/deploy/Deploy-Release-v1.15.0.md` — este arquivo

## Passos de Publicação

### 1. Verificação de Migrations Pendentes (somente leitura)

```bash
# Planejamento das migrations das apps afetadas
python manage.py migrate --plan configuracao
python manage.py migrate --plan contas
python manage.py migrate --plan secretaria
```

Executar com o settings de produção já definido no ambiente do Render, nunca com `core.settings_local`.

### 2. Preflight

```bash
python manage.py check
```

### 3. Commit e Push

```bash
git push origin master
```

O Render detectará o push em `master` e executará:

1. build com dependências;
2. `python manage.py migrate`;
3. `python manage.py collectstatic --noinput`;
4. restart do serviço.

## Validação Pós-Deploy (Checklist)

- [ ] Login de Administrador do Ministério abre o Centro Ministerial
- [ ] Seletor de igreja lista apenas igrejas do escopo canônico do usuário
- [ ] Igreja ativa fora do escopo é descartada e a sessão é limpa
- [ ] Usuário com exatamente uma igreja no escopo recebe seleção automática
- [ ] Financeiro abre para Administrador do Ministério com igreja ativa Sede
- [ ] Financeiro abre para Administrador do Ministério com igreja ativa Independente
- [ ] Financeiro nega Administrador do Ministério com igreja ativa Regional
- [ ] Financeiro nega Administrador do Ministério com igreja ativa Congregação
- [ ] Financeiro nega Administrador do Ministério sem igreja ativa
- [ ] Pastor Local e Tesoureiro mantêm o acesso ao Financeiro como antes
- [ ] Departamentos ministeriais: hub, meus departamentos e gestão carregam
- [ ] Ministério de demonstração não dispara WhatsApp nem e-mail reais
- [ ] `python manage.py check` retorna 0 issues
- [ ] Logs monitorados por 30 minutos após a publicação

## Comandos de Teste Local (Antes do Push)

```bash
# Suíte focada da release
python manage.py test deploy.tests --settings=core.settings_test
python manage.py test demo.tests --settings=core.settings_test
python manage.py test contas.tests.test_page_permissions --settings=core.settings_test
python manage.py test tests.test_financeiro_admin_integration --settings=core.settings_test
python manage.py test configuracao.tests --settings=core.settings_test
python manage.py test comunicacao.tests.test_signals --settings=core.settings_test
python manage.py test core.tests.test_email --settings=core.settings_test

# Verificação de integridade
python manage.py check --settings=core.settings_test
```

## Observações

- **Migrations aditivas**: as migrations novas apenas acrescentam campos e modelos. Não há remoção de campo nem renomeação de coluna.
- **Migrations históricas modificadas**: `contas.0003`, `secretaria.0008` e `secretaria.0014` foram ajustadas. Revisar o conteúdo antes de aplicar em produção e confirmar que nenhum ambiente já as aplicou em versão anterior divergente.
- **Poderes internos preservados**: a entrada de Administrador do Ministério no Financeiro não concede poderes equivalentes aos de Tesoureiro.
- **Tenant Demo**: a neutralização de comunicação depende de marcação explícita em `Ministerio.is_demo`. Ministérios reais não são afetados.
- **Escopo canônico de igreja**: a validação da igreja ativa passa a depender de `get_igrejas_selecionaveis()`. Sessões cujo vínculo foi alterado podem exigir nova seleção de igreja.
- **Falhas conhecidas da suíte completa**: quatro falhas independentes desta versão permanecem registradas em backlog local (Comunicação, Escola Bíblica e API de localidades).
- **Monitoramento**: verificar os logs da aplicação por 30 minutos após a publicação.

## Rollback (se necessário)

```bash
git revert HEAD
git push origin master
```

O Render republicará a versão anterior.

Reversão de schema (avaliar caso a caso, com backup e autorização explícita):

```bash
# Reverter as migrations novas de configuracao
python manage.py migrate configuracao 0039
```

> Atenção: `0043_ministerio_is_demo` possui reverse `noop` para a marcação de dados. A coluna pode ser removida, mas a marcação histórica não é desfeita automaticamente.

## Contato / Suporte

Dúvidas sobre deploy? Verifique `docs/deploy/` e `skills/deploy/SKILL.md`.

---

**Versão**: 1.15.0 | **Data**: 14/09/2026 | **Status**: Aguardando autorização para publicação