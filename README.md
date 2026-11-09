# GereIgreja

Plataforma web de gestão eclesiástica desenvolvida em Django, com suporte a múltiplas igrejas e módulos administrativos integrados.

O GereIgreja centraliza rotinas de Secretaria, Financeiro, Escola Bíblica Dominical, Eventos, Comunicação, Departamentos, Usuários, Configurações e outras capacidades da plataforma.

## Documentação oficial

A documentação técnica e funcional está centralizada em:

```text
docs/
```

Pontos de entrada:

```text
docs/README.md
→ apresentação da documentação

docs/00-Guia-de-Documentacao.md
→ governança documental

docs/INDEX.md
→ mapa global de famílias e autoridades
```

Para entender uma área específica, prefira o README da família correspondente em vez de links históricos isolados.

## Princípio documental

> Evoluir antes de criar. Consolidar antes de duplicar. Criar somente diante de uma lacuna demonstrável.

Documentos antigos, release notes e changelogs podem preservar caminhos históricos que já não existem na estrutura atual.

## Principais domínios funcionais

A documentação funcional vigente está em:

```text
docs/apps/
```

Principais áreas documentadas:

- Membros;
- Secretaria;
- Financeiro;
- Comunicação;
- Departamentos;
- Escola Bíblica Dominical;
- Eventos;
- Usuários;
- Configurações.

A ausência de um documento numerado não significa automaticamente ausência funcional nem autoriza sua criação.

## Arquitetura e engenharia

### Arquitetura

```text
docs/arquitetura/
```

Descreve como a plataforma está organizada atualmente.

### Backend

```text
docs/backend/
```

Define padrões de implementação Django, incluindo Core, Models, Services, Selectors, Views, Forms, Permissions, Middlewares, Tasks, Logging, Testing e Code Standards.

### Frontend

```text
docs/frontend/
```

Documenta estrutura da interface, layouts, templates, assets, CSS, JavaScript, HTMX, Alpine.js e dashboards.

### Design System

```text
docs/design-system/
```

É a fonte canônica da linguagem visual e dos padrões de UX.

### APIs

```text
docs/api/
```

Concentra contratos, segurança, versionamento, integrações e ciclo de vida das APIs.

## Segurança e multi-tenancy

Segurança é uma preocupação transversal da plataforma.

A documentação canônica está em:

```text
docs/frameworks/02-GAF-GereIgreja-Authentication-Framework.md
docs/frameworks/03-GSF-GereIgreja-Security-Framework.md
docs/seguranca/
```

Conceitos que devem permanecer distintos:

```text
Autenticação
→ quem é o usuário

Autorização
→ o que pode fazer

Tenant / igreja ativa
→ sobre quais dados pode operar
```

Controle visual no frontend não substitui autorização no backend.

## Infraestrutura e operação

### Infraestrutura

```text
docs/infraestrutura/
```

Ambientes, banco, observabilidade, backup, disaster recovery, capacidade, custos e prontidão operacional.

### Operações

```text
docs/operacoes/
```

Runbooks e procedimentos recorrentes.

### Deploy

```text
docs/deploy/
```

Procedimentos de implantação e publicação.

### Qualidade

```text
docs/qualidade/
```

Homologação, regressão, checklists, quality gates e critérios de aceite.

### Automação

```text
docs/automacao/
```

Automações operacionais ou de negócio com ciclo de vida próprio.

## Inteligência Artificial

A engenharia e governança de IA estão documentadas em:

```text
docs/ai/
```

A família GAI possui baseline oficial:

```text
GAI-01 ... GAI-35
```

O framework 1.0 está estruturalmente congelado; novos documentos `GAI-36+` exigem análise formal de lacuna.

## Usuário, produto e estratégia

```text
docs/usuario/
→ guias destinados ao usuário final

docs/produto/
→ iniciativas e especificações de produto

docs/estrategia-digital/
→ posicionamento, SEO, conteúdo, conversão e métricas
```

## Decisões, auditorias e histórico

```text
docs/adr/
→ decisões arquiteturais

docs/auditoria/
→ evidências de auditorias executadas

docs/relatorios/
→ análises e diagnósticos

docs/release-notes/
→ histórico de versões

CHANGELOG.md
→ histórico geral de mudanças
```

Registros históricos não substituem documentação canônica vigente.

## Tecnologias principais

O projeto utiliza, entre outras dependências:

- Python;
- Django 5.2;
- PostgreSQL em ambientes que utilizam o backend PostgreSQL;
- SQLite nos ambientes locais/testes configurados para esse fim;
- Bootstrap;
- JavaScript;
- HTMX;
- Alpine.js;
- Cloudinary;
- Render;
- Git e GitHub.

A lista exata de dependências deve ser consultada em:

```text
requirements.txt
```

## Ambiente local seguro

As regras operacionais para agentes e automações estão em:

```text
AGENTS.md
```

Settings previstos para cada contexto:

```text
core.settings_local
→ desenvolvimento e comandos locais

core.settings_test
→ testes Django

core.settings_test_migrations
→ testes reais de migrations
```

Não utilizar `core.settings` em comandos locais apenas por ausência de `--settings`.

Não acessar `.env`, PostgreSQL remoto, Supabase ou ambiente produtivo sem autorização explícita e alvo inequívoco.

## Instalação local

Fluxo geral:

```bash
git clone <URL_DO_REPOSITORIO>
cd Gereigreja

python -m venv .venv
```

Ative o ambiente virtual.

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Para desenvolvimento local, utilize os settings locais definidos pelo projeto.

Exemplo:

```bash
python manage.py runserver --settings=core.settings_local
```

## Testes

A referência operacional está em:

```text
docs/desenvolvimento/Como-Rodar-Testes.md
```

Execução Django:

```bash
python manage.py test --settings=core.settings_test
```

Quando aplicável, a suíte também pode ser executada com pytest conforme a configuração documentada do projeto.

Não executar migrations como efeito colateral de uma tarefa genérica de teste.

## Migrations

Migrations exigem atenção ao ambiente.

Antes de executar comandos relacionados a schema:

- confirme os settings;
- confirme o banco alvo;
- não presuma que a ausência de `--settings` é segura;
- não utilize produção sem autorização explícita;
- siga `AGENTS.md` e a documentação de infraestrutura correspondente.

## Estrutura documental resumida

```text
docs/
├── adr/
├── ai/
├── api/
├── apps/
├── arquitetura/
├── auditoria/
├── automacao/
├── backend/
├── deploy/
├── desenvolvimento/
├── design-system/
├── estrategia-digital/
├── frameworks/
├── frontend/
├── governanca/
├── infraestrutura/
├── operacoes/
├── produto/
├── qualidade/
├── relatorios/
├── release-notes/
├── seguranca/
├── sistema/
└── usuario/
```

Não fazem parte da árvore documental ativa:

```text
administrador/
design/
marketing/
templates/
ui/
```

## Famílias em consolidação

### `docs/governanca/`

Família válida, mas em consolidação. Alguns padrões técnicos antigos estão sendo absorvidos pelas famílias canônicas modernas.

### `docs/sistema/`

Família transitória.

```text
NOVOS DOCUMENTOS: NÃO
```

Seu conteúdo deve ser gradualmente consolidado nos domínios corretos.

## Versão e mudanças

Não mantenha uma versão fixa neste README.

Consulte:

```text
CHANGELOG.md
docs/release-notes/
```

para conhecer a evolução publicada e o histórico do sistema.

## Contribuição e manutenção

Antes de alterar o projeto:

1. leia `AGENTS.md`;
2. consulte `docs/README.md`;
3. localize o domínio no `docs/INDEX.md`;
4. leia a documentação canônica correspondente;
5. valide se código e documentação continuam coerentes;
6. atualize documentação quando a mudança alterar comportamento, arquitetura ou operação.

## Regra final

```text
Código
+
Documentação
+
Testes
+
Operação
=
Plataforma sustentável
```

A documentação oficial deve representar o sistema real, não uma versão idealizada ou histórica da plataforma.
