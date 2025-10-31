# Contexto do Projeto Gereigreja

## 1. Resumo do Projeto

  - **Objetivo Principal:** Sistema de gerenciamento eclesiástico completo, abrangendo secretaria, financeiro, configuração da organização, gestão de usuários e comunicação.
  - **Tecnologias Chave:**
    - Backend: Python com Django Framework.
    - Frontend: HTML, CSS (Bootstrap), JavaScript (jQuery, Chart.js).
  - Banco de Dados: Supabase (PostgreSQL).
    - Hospedagem: Render (deploy automatizado).
    - Armazenamento de Mídia: Cloudinary (imagens e arquivos de usuários).
    - Controle de Versão: Git e GitHub.

## 2. Ambiente de Hospedagem (Render)

- **Provedor:** Render
  - **Deploy:** Automatizado via GitHub (build e deploy contínuo).
  - **Configuração:**
    - Variáveis de ambiente configuradas no painel da Render (ex: `DJANGO_SETTINGS_MODULE`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, credenciais de e-mail, Cloudinary, Supabase, etc).
  - Banco de dados: Supabase (PostgreSQL).
    - Armazenamento de mídia: Cloudinary (configurado em `settings.py`).
    - Arquivos estáticos: Servidos via Whitenoise.
    - Logs: Gravados em `logs/django_errors.log`.
    - Domínio: gereigreja.site (DNS configurado para Render).

## 3. Processo de Deploy

  - **Controle de Versão:** Código gerenciado com Git e hospedado no GitHub.
  - **Deploy na Render:**
    - Deploy automatizado via integração GitHub/Render.
    - Build e deploy contínuo a cada push na branch principal.
    - Instalação de dependências, migrações e coleta de estáticos automatizadas pelo Render.
    - Variáveis de ambiente configuradas no painel da Render.

## 4. Estrutura dos Aplicativos Principais

  - **`core`**: Configurações centrais do projeto (`settings.py`, `urls.py` principal, `wsgi.py`), arquivos estáticos e templates base, utilitários e decorators globais.
  - **`secretaria`**: Gerenciamento de membros, tipos de pessoa, status, histórico de membros, cargos, e funcionalidades administrativas da secretaria.
  - **`financeiro`**: Gestão de receitas, despesas, categorias financeiras, contas bancárias, fechamentos de caixa, contas a pagar, fornecedores e relatórios financeiros.
  - **`configuracao`**: Gerenciamento da organização, igrejas, planos de assinatura, perfil do usuário, e atualizações do sistema.
  - **`contas`**: Autenticação de usuários (login, logout, registro), gerenciamento de convites, redefinição de senha e controle de papéis/permissões de usuários.
  - **Outros Apps (se existentes):** `eventos`, `comunicacao`.

## 5. Decisões de Design e Funcionalidades Implementadas Recentemente

  - **Backend de Mídia:**
    - Integração com Cloudinary para upload e armazenamento de imagens e arquivos de usuários.
    - Correção do backend de mídia no Django, forçando reload do storage após definição do DEFAULT_FILE_STORAGE.
    - Observação: durante a execução de testes automatizados, o projeto pode usar `core/settings_test.py` que altera o `DEFAULT_FILE_STORAGE` para `django.core.files.storage.FileSystemStorage` (evitando chamadas externas ao Cloudinary). Confirme esse comportamento antes de rodar testes que façam upload.
  - **Limpeza de Código:**
    - Remoção de prints e códigos de debug em toda a base para produção.
  - **Refatoração de Status de Membro:**
    - Divisão do conceito de "status" em `TipoPessoa` (quem é: Membro, Visitante, etc.) e `StatusPessoa` (situação: Ativo, Inativo, Disciplina, etc.).
    - Implementação de `StatusHistorico` para rastrear automaticamente as mudanças de `TipoPessoa` e `StatusPessoa` de um membro, incluindo quem fez a alteração e quando.
    - Interface para adicionar entradas manuais/retroativas no `StatusHistorico`.
  - **Permissões e Acesso:**
    - Uso de grupos do Django (`Admin Ministerio`, `Secretario`, `Tesoureiro`, `Lider`) para controlar o acesso às funcionalidades.
    - Decorator customizado `@check_permission` para verificar permissões de forma mais robusta.
    - Página de erro `403.html` personalizada para acessos não permitidos.
  - **Gerenciamento de Igrejas e Contexto Global:**
    - Implementação de um seletor global de "Igreja Ativa" na sessão do usuário, permitindo filtrar dados em diferentes módulos.
    - Lógica nos painéis de liderança para consolidar dados de igrejas subordinadas.
  - **Assinaturas e Planos:**
    - Modelos para `Plano` e `AssinaturaMinisterio`.
    - Funcionalidade para gerenciar assinaturas, incluindo plano gratuito e período de cortesia.
    - Decorator `@verificar_assinatura_valida` para proteger views.
  - **Melhorias na Interface de Usuário (UX):**
    - Reorganização de formulários (ex: cadastro de membros em seções).
    - Botão "Salvar e Continuar Editando".
    - Uso de DataTables para listagens.
    - Implementação de abas em páginas de edição complexas (ex: editar membro).
  - **Página de "Novidades e Atualizações do Sistema"**.
  - **Configuração de Envio de E-mail via Brevo (Sendinblue).**

## 6. Pontos de Atenção e Solução de Problemas Comuns

  - **Backend de Mídia não ativando:** Corrigido forçando reload do storage após definição do DEFAULT_FILE_STORAGE no settings.py.
  - **Erro `OperationalError: no such column: ...`:** Indica migrações pendentes. Resolvido com `python manage.py migrate`.
  - **Arquivos Estáticos/Mídia não carregando:** Verificar configuração do Whitenoise, Cloudinary e variáveis de ambiente.
  - **Permissões de Arquivo/Pasta:** Render gerencia permissões, mas garantir que diretórios de logs e mídia estejam configurados corretamente.
  - **Circular Imports:** Adiar avaliação de URLs para dentro de funções/decorators.


# Contexto do Projeto Gereigreja

Este documento foi reorganizado para facilitar a leitura por diferentes públicos: desenvolvedores, operadores (ops) e gestores do produto. Contém visão geral, instruções de desenvolvimento, operação, integrações e um runbook com passos críticos.

## Sumário (TOC)

- [Quickstart (desenvolvimento)](#quickstart)
- [Operação / Produção](#operacao)
- [Infra & Deploy (Render, DB, Storage)](#infra-deploy)
- [Integrações externas (Stripe, Brevo, Cloudinary)](#integracoes-externas)
- [Desenvolvimento e CI (tests, settings_test, commands)](#desenvolvimento-ci)
- [Apps e arquitetura (resumo por app)](#apps-e-arquitetura)
- [Runbook (migrate, backup, restore, testes de webhooks)](#runbook)
- [Contribuição e convenções](#contribuicao)
- [Roadmap / Melhorias planejadas](#roadmap)
- [Apêndice: inventário técnico (commands, templatetags, backups)](#apendice)

### Como usar este documento

- O TOC acima contém links diretos para cada seção principal.
- Em cada grande seção há um link "↑ Voltar ao Sumário" que retorna ao topo.
- Para contribuições, crie PRs pequenos e focados (um tópico por PR).

---

<a id="quickstart"></a>
## Quickstart (desenvolvimento)

Rápido para começar em um ambiente local (Windows / PowerShell):

1. Criar e ativar virtualenv e instalar dependências:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Criar `.env` a partir de um exemplo (não comitar valores reais):

```powershell
copy .env.example .env
# editar .env com credenciais locais (usar chaves de teste para Stripe/Cloudinary)
```

3. Rodar migrações locais e servidor:

```powershell
python manage.py migrate
python manage.py runserver
```

4. Testes (por app):

```powershell
python manage.py test secretaria
python manage.py test
```

Nota: `core/settings_test.py` usa `FileSystemStorage` e SQLite em memória para evitar acessos externos durante testes.

---

[↑ Voltar ao Sumário](#sumário-toc)

<a id="operacao"></a>
## Operação / Produção

Seções e checklists para operadores:

- Variáveis de ambiente obrigatórias (ver seção Deploy/Infra).
- Backups: mantenha cópias regulares dos dumps em `backup/` e scripts de exportação.
- Logs: em produção os logs são coletados pelo provider (Render). Em dev os logs ficam em `logs/django_errors.log`.
- Deploy: pipeline automatizado por push -> Render; revisar logs de build se falhar.

---

[↑ Voltar ao Sumário](#sumário-toc)

<a id="infra-deploy"></a>
## Infra & Deploy

### Render

- Deploy contínuo via integração GitHub/Render. A Render injeta `RENDER_EXTERNAL_HOSTNAME` quando aplicável.
- Confirme as variáveis de ambiente abaixo no painel da Render antes do deploy:
  - `DJANGO_SETTINGS_MODULE` (ex.: `core.settings`)
  - `DJANGO_SECRET_KEY`
  - `DJANGO_DEBUG` = 'False'
  - Cloudinary: `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
  - Supabase/Postgres: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
  - Stripe: `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
  - Email: `gereigreja_email_password` (ou variável equivalente usada em `settings.py`)

### Database (Supabase/Postgres)

- Configurações centralizadas em `core/settings.py`.
- Antes de aplicar migrações em produção: faça backup do banco e execute `python manage.py migrate --plan` para revisar alterações.

### Storage (Cloudinary)

- Produção: `DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'` (em `core/settings.py`).
- Testes/CI: `core/settings_test.py` troca o backend para `django.core.files.storage.FileSystemStorage`.
- Atenção: mudar `DEFAULT_FILE_STORAGE` altera URLs e pode exigir migração de arquivos.

---

[↑ Voltar ao Sumário](#sumário-toc)

<a id="integracoes-externas"></a>
## Integrações externas

### Stripe

- Onde: modelos e admin em `configuracao` (campos `stripe_price_id_mensal`, `stripe_price_id_anual`).
- Variáveis: `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`.
- Testes e webhooks: use `stripe-cli`/ngrok para testar webhooks localmente.

### Brevo / Sendinblue (SMTP)

- Configurado em `core/settings.py` (EMAIL_HOST = 'smtp-relay.brevo.com').
- Variável de senha: `gereigreja_email_password`.

### Cloudinary

- SDKs e assets JS em `staticfiles_production/cloudinary/js/`.
- As credenciais são carregadas via variáveis de ambiente.

---

[↑ Voltar ao Sumário](#sumário-toc)

<a id="desenvolvimento-ci"></a>
## Desenvolvimento e CI

### Settings de teste

- `core/settings_test.py` usa SQLite em memória e `FileSystemStorage` para evitar uploads externos.

### Management commands (inventário rápido)

- `secretaria/management/commands/test_create_visitante.py` — simula criar visitante + registrar presença.
- `secretaria/management/commands/converter_dump.py` — utilitário de importação/conversão de dumps.
- `financeiro/management/commands/copiar_globais_para_ministerios.py` — utilitário financeiro.
- `core/management/commands/enviar_notificacoes.py` — envio de notificações programadas.
- `configuracao/management/commands/atribuir_permissoes_admin_ministerio.py` — configura permissões nos ministérios.

Execute `python manage.py <comando> --help` para ver opções.

### Templatetags e utilitários

- Diretórios: `financeiro/templatetags`, `secretaria/templatetags`, `configuracao/templatetags`, `eventos/templatetags`.
- Documentar tags/filters mais importantes conforme for necessário (apêndice).

---

[↑ Voltar ao Sumário](#sumário-toc)

<a id="apps-e-arquitetura"></a>
## Apps e arquitetura (resumo por app)

- `core`: configurações globais, middleware, context processors.
- `secretaria`: cadastro de membros, visitantes, registros de presença, histórico de status.
- `financeiro`: receitas, despesas, contas, relatórios.
- `configuracao`: planos, assinaturas, gerenciamento de ministérios e configurações globais.
- `contas`: autenticação e permissões.
- `eventos`, `comunicacao`, `agenda`, `escola_biblica`, `suporte`: módulos com responsabilidades específicas.

Detalhes e pontos de entrada (views/urls) podem ser consultados diretamente nos arquivos `*/views.py` e `*/urls.py`.

---

[↑ Voltar ao Sumário](#sumário-toc)

<a id="runbook"></a>
## Runbook operacional (passos rápidos)

1. Backup do banco (antes de mudanças críticas)
   - Gerar dump e copiar para storage seguro (`backup/` ou storage externo).

2. Aplicar migrations com segurança:

```powershell
python manage.py migrate --plan
# revise o plano, então:
python manage.py migrate
```

3. Restaurar dump (em staging):

 - criar database de staging
 - carregar dump com `pg_restore` ou `python manage.py loaddata` conforme formato

4. Testar webhooks Stripe localmente:

```powershell
stripe listen --forward-to localhost:8000/webhooks/stripe
```

5. Limpar storage temporário entre runs de teste (se usar FileSystemStorage).

---

[↑ Voltar ao Sumário](#sumário-toc)

<a id="seguranca"></a>
## Segurança e dados sensíveis

- Não commitar `.env` nem backups contendo dados sensíveis.
- Redigir ou remover dados sensíveis de fixtures antes de compartilhar.

---

[↑ Voltar ao Sumário](#sumário-toc)

<a id="contribuicao"></a>
## Contribuição

- Recomenda-se adicionar `CONTRIBUTING.md` e `DEPLOY.md` no repositório.
- Convenções mínimas sugeridas:
  - Branches: `feature/<descrição>`, `bugfix/<descrição>`, `docs/<descrição>`.
  - Commits: `tipo: escopo - mensagem` (ex.: `feat(secretaria): adicionar validação de CPF`).

---

[↑ Voltar ao Sumário](#sumário-toc)

<a id="roadmap"></a>
## Roadmap / Melhorias planejadas (resumo)

- Otimização de consultas (`select_related` / `prefetch_related`).
- Testes automatizados mais robustos.
- Dashboard financeiro com indicadores.
- Autocadastro de membros, melhorias em UX, módulos adicionais (biblioteca, infantil, etc.).

---

[↑ Voltar ao Sumário](#sumário-toc)

<a id="apendice"></a>
## Apêndice — inventário técnico

- Management commands: ver `*/management/commands/`.
- Templatetags: ver `*/templatetags/`.
- Backups: arquivos `backup_*.json`, `*.dump`, `backup/`.
- Notas rápidas:
  - `SITE_ID = 2` está definido em `core/settings.py`.
  - `DEFAULT_FILE_STORAGE` em produção aponta para Cloudinary.

---

[↑ Voltar ao Sumário](#sumário-toc)

Este documento foi reorganizado para facilitar navegação e manutenção. Se quiser, posso também gerar arquivos separados (`CONTRIBUTING.md`, `DEPLOY.md`, `BACKUPS.md`) e commitar na mesma branch.


``` 

### Contribuição e convenções

- Sugestão de arquivos a adicionar no repo (se aceitar): `CONTRIBUTING.md`, `DEPLOY.md`, `BACKUPS.md`.
- Convenções sugeridas:
  - Branches de feature: `feature/<descrição>`; docs: `docs/<descrição>`.
  - Commit messages: prefira `type: escopo - descrição breve` (ex.: `docs: atualizar contexto_gereigreja.md`).

### Observações finais

- Para qualquer alteração estrutural (storage, DB, deploy), criar um backup e testar em staging antes de mover para produção.
- Se quiser, eu aplico essa expansão no `contexto_gereigreja.md` (já está na branch `docs/contexto-update`) e faço commit — feito; se desejar, gero o patch completo para aplicar localmente.



