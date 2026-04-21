# Gereigreja 🙏

Sistema completo de gestão eclesiástica desenvolvido em Django, oferecendo soluções integradas para administração de igrejas e organizações religiosas.

## 📋 Sobre o Sistema

**Gereigreja** é uma plataforma web robusta que centraliza a gestão de todos os aspectos administrativos de uma igreja, desde o cadastro de membros até o controle financeiro, passando por eventos, comunicação e recursos educacionais.

## ✨ Funcionalidades Principais

- **👥 Secretaria**: Gestão completa de membros, famílias, visitantes e acompanhamento de visitas
- **💰 Financeiro**: Controle de receitas, despesas, contas bancárias, categorias e relatórios
- **📅 Eventos**: Organização de eventos, controle de participantes e inscrições
- **📧 Comunicação**: Envio de e-mails, SMS e notificações para membros
- **📚 Escola Bíblica**: Gestão de turmas, alunos e materiais didáticos
- **⚙️ Configuração**: Administração de organizações, igrejas, usuários e permissões
- **🚀 Deploy**: Sistema automatizado de versionamento e publicação de atualizações

## � Sistema de Grupos e Permissões

O Gereigreja implementa um sistema robusto de controle de acesso baseado em **13 grupos hierárquicos**, cada um com permissões específicas para garantir que usuários acessem apenas as funcionalidades apropriadas aos seus cargos.

### Grupos Disponíveis (Hierarquia)

#### 🏛️ Nível Ministerial
- **Admin Ministerio**: Controle total sobre todas as organizações e igrejas
- **Pastor Regional**: Gestão de múltiplas igrejas dentro de uma organização
- **Tesoureiro**: Acesso dedicado ao módulo financeiro em nível ministerial

#### ⛪ Nível Local (Igreja)
- **Admin Org**: Administração completa da organização local
- **Pastor Local**: Gestão pastoral da igreja local
- **Secretario Local**: Gestão administrativa e de membros
- **Tesoureiro Local**: Controle financeiro da igreja
- **Regente**: Gestão do ministério de música e louvor
- **Lider Eventos**: Organização e coordenação de eventos

#### 📚 Escola Bíblica Dominical (EBD)
- **Superintendente EBD**: Gestão completa da escola bíblica
- **Secretaria EBD**: Apoio administrativo EBD
- **Professor**: Condução de turmas e classes

#### 👥 Membros
- **Membro Comum**: Acesso básico ao sistema

### Configuração Inicial

Após instalar o sistema, execute o comando para configurar automaticamente todos os grupos com suas permissões:

```bash
python manage.py configurar_permissoes_grupos
```

**Opções disponíveis:**
- `--reset`: Remove e recria todos os grupos
- `--dry-run`: Simula a configuração sem fazer mudanças

### Documentação Completa

Para detalhes sobre cada grupo, permissões específicas e guias de uso, consulte:
- **[docs/GRUPOS_PERMISSOES.md](docs/GRUPOS_PERMISSOES.md)** - Documentação completa do sistema de permissões

## 🆕 Melhorias Recentes (v1.8.78 — 21/04/2026)

- **Alteração em Massa de Pessoas (Bulk Edit):**
  - Corrigido bug de logout inesperado ao salvar alteração em massa.
  - Submit do modal agora aciona sempre o formulário correto, evitando conflitos com o form de logout.
  - Seleção de tags e campos harmonizada com cadastro/edição individual.
- **Mensagens Globais:**
  - Removido bloco de mensagens duplicado na lista de membros; apenas o global permanece.
- **Middleware/Contexto:**
  - Middleware ajustado para não exigir seleção de igreja para usuários de igreja única.
  - Selector de igreja oculto para esses usuários, evitando POSTs desnecessários.
- **UX:**
  - Ajustes em botões, modais e feedback visual para maior clareza e robustez.

Veja detalhes completos no [CHANGELOG.md](CHANGELOG.md) e na documentação de permissões/grupos.

##🛠️ Tecnologias

- **Backend**: Python 3.x + Django Framework
- **Frontend**: HTML5, CSS3 (Bootstrap), JavaScript (jQuery, Chart.js)
- **Banco de Dados**: PostgreSQL (Supabase)
- **Armazenamento**: Cloudinary (arquivos e mídia)
- **Hospedagem**: Render (deploy automatizado)
- **Controle de Versão**: Git + GitHub

## 📖 Documentação Técnica

### Arquitetura e Estrutura
- **[docs/ARQUITETURA_TEMPLATES.md](docs/ARQUITETURA_TEMPLATES.md)** - Arquitetura de templates e convenções de uso
- **[docs/GRUPOS_PERMISSOES.md](docs/GRUPOS_PERMISSOES.md)** - Sistema completo de permissões e grupos

### Segurança e Conformidade
- **[docs/LGPD_IMPLEMENTACAO.md](docs/LGPD_IMPLEMENTACAO.md)** - Implementação de conformidade LGPD
- **[docs/DECORATORS_SEGURANCA.md](docs/DECORATORS_SEGURANCA.md)** - Decorators de segurança do sistema
- **[docs/AUDITORIA_PERMISSOES_SISTEMA_COMPLETO.md](docs/AUDITORIA_PERMISSOES_SISTEMA_COMPLETO.md)** - Auditoria completa de permissões

### Funcionalidades Específicas
- **[docs/SELETOR_IGREJA.md](docs/SELETOR_IGREJA.md)** - Sistema de seleção de igreja ativa
- **[docs/ANALISE_MENUS_BASEADOS_PERMISSOES.md](docs/ANALISE_MENUS_BASEADOS_PERMISSOES.md)** - Análise de menus e permissões

### Guias de Desenvolvimento
- **[CHAT_RESPOSTAS.md](CHAT_RESPOSTAS.md)** - Respostas detalhadas de análises e implementações
- **[skills/](skills/)** - Instruções para agente IA por módulo

## 📁 Estrutura do Projeto

```
Gereigreja/
├── skills/                    # Instruções para agente IA
│   ├── copilot-instructions.md
│   ├── contexto_gereigreja.md
│   ├── financeiro/
│   ├── deploy/
│   ├── backup/
│   ├── eventos/
│   ├── comunicacao/
│   ├── secretaria/
│   └── configuracao/
├── docs/                      # Documentação
│   └── release-notes/
├── core/                      # Configurações principais
├── financeiro/                # App de gestão financeira
├── secretaria/                # App de gestão de membros
├── eventos/                   # App de gestão de eventos
├── comunicacao/               # App de comunicação
├── escola_biblica/            # App de escola bíblica
├── configuracao/              # App de configuração
├── contas/                    # App de autenticação
├── deploy/                    # App de versionamento
├── templates/                 # Templates globais
├── static/                    # Arquivos estáticos
├── media/                     # Uploads de usuários
├── backup/                    # Backups do banco
├── logs/                      # Logs do sistema
├── manage.py
├── requirements.txt
├── README.md
├── CHANGELOG.md
└── README_TESTS.md
```

## 🚀 Como Começar

### Pré-requisitos

- Python 3.8+
- PostgreSQL
- Git

### Instalação

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/gereigreja.git
   cd gereigreja
   ```

2. **Crie e ative o ambiente virtual**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**:
   - Copie `.env.example` para `.env`
   - Configure as credenciais do banco, Cloudinary, e-mail, etc.

5. **Execute as migrações**:
   ```bash
   python manage.py migrate
   ```

6. **Crie um superusuário**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Rode o servidor**:
   ```bash
   python manage.py runserver
   ```

8. Acesse: `http://localhost:8000`

## 📚 Documentação

### Skills (Instruções para IA)
O diretório [`skills/`](skills/) contém instruções detalhadas por módulo para agentes de IA:
- [`skills/README.md`](skills/README.md) - Índice de todas as skills
- [`skills/copilot-instructions.md`](skills/copilot-instructions.md) - Instruções gerais
- [`skills/contexto_gereigreja.md`](skills/contexto_gereigreja.md) - Contexto do projeto
- [`skills/financeiro/SKILL.md`](skills/financeiro/SKILL.md) - Gestão financeira
- [`skills/deploy/SKILL.md`](skills/deploy/SKILL.md) - Deploy e versionamento
- [`skills/backup/SKILL.md`](skills/backup/SKILL.md) - Backup e restauração
- E mais...

### Documentação Adicional
- [`README_TESTS.md`](README_TESTS.md) - Informações sobre testes
- [`CHANGELOG.md`](CHANGELOG.md) - Histórico de mudanças
- [`docs/release-notes/`](docs/release-notes/) - Notas de versão

## 🔧 Comandos Úteis

```bash
# Rodar servidor de desenvolvimento
python manage.py runserver

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic

# Executar testes
python manage.py test

# Criar superusuário
python manage.py createsuperuser
```

## 📦 Deploy

O sistema usa deploy automatizado via Render com integração GitHub:
1. Push para a branch `main`
2. Render detecta mudanças
3. Build e deploy automáticos
4. Migrações e collectstatic executados

Veja [`skills/deploy/SKILL.md`](skills/deploy/SKILL.md) para mais detalhes.

## 🐛 Logs e Debugging

- Logs de erro: `logs/django_errors.log`
- Debug personalizado: `debug.log`
- Logs de backup: `backup_log.txt`

## 📈 Versão do Sistema

O sistema exibe automaticamente a versão atual nos rodapés, lendo do `CHANGELOG.md`.

**Template tag** disponível:
```django
{% load versao %}
{% get_versao_gereigreja as versao_sistema %}
Versão {{ versao_sistema }}
```

## 🤝 Suporte

Para dúvidas e suporte, entre em contato através da plataforma ou consulte a documentação em [`skills/`](skills/).

---

**Última atualização**: Março 2026  
**Versão**: v1.3.1
