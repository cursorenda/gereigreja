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

## 7. Configurações Importantes do Django (`settings.py`)

  - **Segurança:**
    - `SECRET_KEY`: Carregada de variável de ambiente em produção.
    - `DEBUG`: `False` em produção (controlado por variável de ambiente).
    - `ALLOWED_HOSTS`: Lista de domínios permitidos para servir a aplicação.
  - **Aplicações Instaladas (`INSTALLED_APPS`):**
    - Apps principais: `secretaria`, `financeiro`, `configuracao`, `contas`, `eventos`, `comunicacao` (se ativos).
    - Apps Django padrão: admin, auth, sessions, staticfiles, humanize, sites, whitenoise.
  - **Middleware:**
    - Whitenoise para arquivos estáticos.
    - Middleware customizado para igreja ativa.
  - **Templates:** Diretório `BASE_DIR / 'templates'` configurado.
  - **Arquivos Estáticos e Mídia:**
    - `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT`, `STATICFILES_STORAGE` (Whitenoise).
    - `MEDIA_URL`, `MEDIA_ROOT`, `DEFAULT_FILE_STORAGE` (Cloudinary).
  - **Banco de Dados:** Supabase (PostgreSQL).
  - **Internacionalização:** `LANGUAGE_CODE = 'pt-br'`, `USE_I18N = True`, etc.
  - **Logging:** RotatingFileHandler, erros em `logs/django_errors.log`.
  - **Autenticação:**
    - `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`.
  - **Configuração de E-mail:**
    - Backend, host, porta, SSL/TLS, usuário/senha via variável de ambiente.
    - `DEFAULT_FROM_EMAIL`, `ADMINS`.
  - `SITE_ID = 1` (para `django.contrib.sites`).

## 8. Próximos Passos / Melhorias Planejadas

### 8.1. Melhorias Urgentes e Prioritárias
  - **Refinamento de Permissões:** Continuar ajustando níveis de acesso para diferentes papéis de usuário em todos os módulos.
  - **Dashboard Financeiro:** Incluir mais gráficos e indicadores financeiros relevantes.
  - **Autocadastro de Membros:** Implementar link/funcionalidade para membros se cadastrarem de forma independente, aguardando aprovação.
  - **Envio de E-mail:** Finalizar e testar exaustivamente a configuração de envio de e-mails (Brevo ou outro backend).
  - **Logo da Igreja/Ministério:** Permitir upload e exibição do logo da organização/igreja em locais chave (login, cabeçalhos, relatórios) via Cloudinary.
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


1. Otimização de Consultas:

