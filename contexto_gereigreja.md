# Contexto do Projeto Gereigreja

## 1. Resumo do Projeto

  - **Objetivo Principal:** Sistema de gerenciamento eclesiástico completo, abrangendo secretaria, financeiro, configuração da organização, gestão de usuários e comunicação.
  - **Tecnologias Chave:**
    - Backend: Python com Django Framework.
    - Frontend: HTML, CSS (Bootstrap), JavaScript (jQuery, Chart.js).
    - Banco de Dados: SQLite3 (desenvolvimento e produção inicial).
    - Hospedagem: BrasilLinkHost (cPanel, Phusion Passenger).
    - Controle de Versão: Git e GitHub.

## 2. Ambiente de Hospedagem (BrasilLinkHost)

 - **Provedor:** BrasilLinkHost
   - **Endereço IP do Servidor:** 199.167.147.66
   - **Acesso ao Servidor:** SSH para o usuário `gerei1`.
   - **Diretório Raiz da Aplicação:** `/home/gerei1/gereigreja.site/`
   - **Ambiente Virtual Python:**
     - Localização: `/home/gerei1/virtualenv/gereigreja.site/3.11/`
     - Comando de ativação: `source /home/gerei1/virtualenv/gereigreja.site/3.11/bin/activate`
     - Versão do Python no Servidor: 3.11.9 (confirmar se é a mesma do ambiente virtual)
   - **Configuração do "Python App" no cPanel (via Phusion Passenger):**
     - Arquivo de Inicialização (Application startup file): `core/wsgi.py` (ou `passenger_wsgi.py` se criado especificamente para o Passenger, mas `core/wsgi.py` é o padrão do Django).
     - Ponto de Entrada (Application Entry point): `application` (variável padrão no `wsgi.py`).
     - Variáveis de Ambiente (configuradas no painel do cPanel):
       - `DJANGO_SETTINGS_MODULE`: `core.settings`
       - `DJANGO_SECRET_KEY`: (Valor único e secreto para produção)
       - `DJANGO_DEBUG`: `False`
       - `gereigreja_email_password`: (Senha do e-mail `nao-responda@gereigreja.site`)
       - **Importante:** A forma correta de definir no cPanel é `NOME_DA_VARIAVEL` e `VALOR_DA_VARIAVEL`.
   - **Banco de Dados:**
     - Tipo em Produção: SQLite3
     - Localização: `BASE_DIR / 'db.sqlite3'` (no servidor: `/home/gerei1/gereigreja.site/db.sqlite3`)
     - **Alerta Crítico:** O arquivo `db.sqlite3` **não deve** ser sobrescrito pelo deploy. Garantir que o `.gitignore` o ignore e que scripts de deploy (como o `.cpanel.yml`) não o copiem do ambiente de desenvolvimento.
   - **Arquivos Estáticos e de Mídia:**
     - `STATIC_URL = 'static/'`
     - `STATICFILES_DIRS = [BASE_DIR / 'static']` (para desenvolvimento)
     - `STATIC_ROOT = BASE_DIR / 'staticfiles_production'` (para onde o `collectstatic` copia em produção)
     - `MEDIA_URL = '/media/'`
     - `MEDIA_ROOT = BASE_DIR / 'media'`
     - Servidos pelo Whitenoise em produção (quando `DEBUG=False`).
   - **Logs da Aplicação:**
     - Configurados para `BASE_DIR / 'logs' / 'django_errors.log'`.
     - O diretório `logs/` precisa existir na raiz do projeto no servidor (`/home/gerei1/gereigreja.site/logs/`) e ter permissão de escrita pelo usuário da aplicação.
   - **Configuração de Domínio (DNS):** Domínio `gereigreja.site` registrado na GoDaddy, com nameservers apontando para a BrasilLinkHost.

## 3. Processo de Deploy

  - **Controle de Versão:** Código gerenciado com Git e hospedado no GitHub.
  - **Deploy no cPanel:**
    - Utiliza a funcionalidade "Git Version Control" do cPanel para clonar/atualizar o repositório no `DEPLOYPATH`.
    - **Arquivo `.cpanel.yml`:** Define tarefas pós-deploy:
      - Ativação do ambiente virtual.
      - Instalação/atualização de dependências (`pip install -r requirements.txt`).
      - Execução de migrações do banco de dados (`python manage.py migrate --noinput`).
      - Coleta de arquivos estáticos (`python manage.py collectstatic --noinput`).
      - Criação/atualização do arquivo `tmp/restart.txt` para reiniciar a aplicação Phusion Passenger.
  - **Autenticação Git:** Idealmente configurada com chaves SSH para acesso seguro ao repositório.

## 4. Estrutura dos Aplicativos Principais

  - **`core`**: Configurações centrais do projeto (`settings.py`, `urls.py` principal, `wsgi.py`), arquivos estáticos e templates base, utilitários e decorators globais.
  - **`secretaria`**: Gerenciamento de membros, tipos de pessoa, status, histórico de membros, cargos, e funcionalidades administrativas da secretaria.
  - **`financeiro`**: Gestão de receitas, despesas, categorias financeiras, contas bancárias, fechamentos de caixa, contas a pagar, fornecedores e relatórios financeiros.
  - **`configuracao`**: Gerenciamento da organização, igrejas, planos de assinatura, perfil do usuário, e atualizações do sistema.
  - **`contas`**: Autenticação de usuários (login, logout, registro), gerenciamento de convites, redefinição de senha e controle de papéis/permissões de usuários.
  - **Outros Apps (se existentes):** `eventos`, `comunicacao`.

## 5. Decisões de Design e Funcionalidades Implementadas Recentemente

  - **Refatoração de Status de Membro:**
    - Divisão do conceito de "status" em `TipoPessoa` (quem é: Membro, Visitante, etc.) e `StatusPessoa` (situação: Ativo, Inativo, Disciplina, etc.).
    - Implementação de `StatusHistorico` para rastrear automaticamente as mudanças de `TipoPessoa` e `StatusPessoa` de um membro, incluindo quem fez a alteração e quando.
    - Interface para adicionar entradas manuais/retroativas no `StatusHistorico`.
  - **Permissões e Acesso:**
    - Uso de grupos do Django (`Admin Organizacao`, `Secretario`, `Tesoureiro`, `Lider`) para controlar o acesso às funcionalidades.
    - Decorator customizado `@check_permission` para verificar permissões de forma mais robusta.
    - Página de erro `403.html` personalizada para acessos não permitidos.
  - **Gerenciamento de Igrejas e Contexto Global:**
    - Implementação de um seletor global de "Igreja Ativa" na sessão do usuário, permitindo filtrar dados em diferentes módulos.
    - Lógica nos painéis de liderança para consolidar dados de igrejas subordinadas.
  - **Assinaturas e Planos:**
    - Modelos para `Plano` e `AssinaturaOrganizacao`.
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

  - **Erro `eval: line 17...` (cPanel):** Causado pela definição incorreta de variáveis de ambiente no cPanel. Corrigido ajustando os nomes e valores das variáveis para o formato simples.
  - **Erro `OperationalError: no such column: ...`:** Geralmente indica que as migrações não foram aplicadas no banco de dados de produção após uma alteração no modelo. Resolvido com `python manage.py migrate`.
  - **Erro "Index of /" (Servidor):** Pode ter várias causas:
    - Aplicação Django não iniciando devido a erros de configuração (ex: variáveis de ambiente, `settings.py`).
    - Arquivo de inicialização (`core/wsgi.py` ou `passenger_wsgi.py`) ausente ou incorreto.
    - Problemas com o Phusion Passenger (verificar logs do Passenger).
  - **Substituição do Banco de Dados de Produção:** Risco se o processo de deploy copiar arquivos indiscriminadamente. O `db.sqlite3` deve ser persistente no servidor.
  - **Arquivos Estáticos Não Carregando em Produção:** Verificar se `DEBUG=False`, se `collectstatic` foi executado, e se o Whitenoise está configurado corretamente.
  - **Permissões de Arquivo/Pasta no Servidor:** O usuário da aplicação precisa de permissão de escrita para `MEDIA_ROOT`, `STATIC_ROOT` (durante `collectstatic`), e o diretório de logs.
  - **Circular Imports:** Especialmente ao lidar com `reverse_lazy` em definições de módulo. Solucionado adiando a avaliação da URL para dentro da função/decorator.

## 7. Configurações Importantes do Django (`settings.py`)

  - **Segurança:**
    - `SECRET_KEY`: Carregada de variável de ambiente em produção.
    - `DEBUG`: `False` em produção (controlado por variável de ambiente).
    - `ALLOWED_HOSTS`: Lista de domínios permitidos para servir a aplicação.
  - **Aplicações Instaladas (`INSTALLED_APPS`):**
    ```python
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.humanize',
        'django.contrib.sites',
        'whitenoise.runserver_nostatic',
        # Seus Apps
        'secretaria',
        'financeiro',
        'configuracao',
        'contas',
        # Adicionar outros apps como 'eventos', 'comunicacao' se estiverem ativos
    ]
    ```
  - **Middleware:**
    - `whitenoise.middleware.WhiteNoiseMiddleware`: Para servir arquivos estáticos em produção.
    - `core.middleware.ActiveChurchMiddleware`: Para gerenciar a igreja ativa na sessão.
  - **Templates:** Diretório `BASE_DIR / 'templates'` configurado.
  - **Arquivos Estáticos e Mídia:**
    - `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT`.
    - `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`.
    - `MEDIA_URL`, `MEDIA_ROOT`.
  - **Banco de Dados:** Configurado para SQLite3.
  - **Internacionalização (`LANGUAGE_CODE = 'pt-br'`, `USE_I18N = True`, etc.).**
  - **Logging:** Configurado para `RotatingFileHandler`, salvando erros em `logs/django_errors.log`.
  - **Autenticação:**
    - `LOGIN_URL = '/accounts/login/'`
    - `LOGIN_REDIRECT_URL = '/'` (ou dashboard apropriado)
    - `LOGOUT_REDIRECT_URL = '/'`
  - **Configuração de E-mail:**
    - `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_SSL`/`TLS`.
    - `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (carregado de variável de ambiente).
    - `DEFAULT_FROM_EMAIL`, `ADMINS`.
  - `SITE_ID = 1` (para `django.contrib.sites`).

## 8. Próximos Passos / Melhorias Planejadas

### 8.1. Melhorias Urgentes e Prioritárias
  - **Refinamento de Permissões:** Continuar ajustando níveis de acesso para diferentes papéis de usuário em todos os módulos.
  - **Dashboard Financeiro:** Incluir mais gráficos e indicadores financeiros relevantes.
  - **Autocadastro de Membros:** Implementar link/funcionalidade para membros se cadastrarem de forma independente, aguardando aprovação.
  - **Envio de E-mail:** Finalizar e testar exaustivamente a configuração de envio de e-mails (Brevo) para convites, notificações, reset de senha, etc.
  - **Logo da Igreja/Organização:** Permitir upload e exibição do logo da organização/igreja em locais chave (login, cabeçalhos, relatórios).
  - **Contas Pagas no Fechamento de Caixa:** Garantir que as despesas originadas de "Contas a Pagar" sejam corretamente incluídas nos fechamentos de caixa.

### 8.2. Funcionalidades de Membros (Secretaria)
  - **Cadastro Detalhado:** Expandir com mais campos (histórico de cargos, cursos, etc.).
  - **Agrupamento Familiar:** Implementar funcionalidade para agrupar membros em famílias.
  - **Tags/Classificações:** Adicionar sistema de tags para status diversos (batizado, doente, necessita visita, etc.).
  - **Documentos:** Melhorar gestão de upload e visualização de certidões, cartas, etc.
  - **Linha do Tempo do Membro:** Visualização cronológica de eventos importantes (entrada, batismo, cargos, mudanças de status/tipo).

### 8.3. Funcionalidades Financeiras
  - **Dízimos e Ofertas:** Monitoramento aprimorado, relatórios de contribuintes.
  - **Reconhecimento de Dizimistas:** (Considerar gamificação ou relatórios específicos).
  - **Contas a Receber:** (Se aplicável, similar a Contas a Pagar).
  - **Orçamento:** Funcionalidade para criar e acompanhar orçamentos.
  - **Relatórios Financeiros Avançados:** Fluxo de caixa, DRE simplificado, comparativos entre períodos/igrejas.

### 8.4. Comunicação e Engajamento
  - **Sistema de Recados/Mural de Avisos Interno.**
  - **Integração WhatsApp/Email:** Para envios automáticos e segmentados.
  - **Jornada do Visitante/Membro:** Módulos para acompanhar o ciclo de vida do membro (Alcance, Recepção, Integração, Consolidação).
    - Pedidos de Oração.
    - Check-in em eventos/cultos.

### 8.5. Módulos Adicionais
  - **Gestão de Eventos e Agenda:** Calendário interativo, inscrições, lista de presença.
  - **Departamento Infantil:** Gestão específica (cadastro de crianças, turmas, responsáveis, controle de check-in/out).
  - **Biblioteca:** Módulo para catalogar e gerenciar empréstimos de livros/materiais.
  - **Pequenos Grupos/Células:** Cadastro, frequência, relatórios.
  - **Ensino (EBD, Cursos):** Cadastro de turmas, alunos, professores, frequência, material.

### 8.6. Melhorias Técnicas e de Usabilidade
  - **Otimização de Consultas:** Continuar uso de `select_related` e `prefetch_related`.
  - **Testes Automatizados:** Implementar testes unitários e de integração.
  - **Documentação:** Melhorar `docstrings` e documentação do projeto.
  - **Refatoração:** Dividir views longas, separar lógica de negócio.
  - **Interface do Usuário (UI/UX):** Melhorar buscas, paginação, feedback ao usuário.
  - **Segurança:** Revisão contínua, validação de dados, proteção contra vulnerabilidades comuns.
  - **Aplicativo Móvel:** Planejamento e desenvolvimento de um app para membros e liderança.

### 8.7. Página de Vendas e Marketing
  - Desenvolver página de vendas com estratégias de SEO.
  - Produzir conteúdo relevante e atualizado sobre gestão eclesiástica para atrair tráfego orgânico.

Este documento deve ser mantido atualizado conforme o projeto evolui.
