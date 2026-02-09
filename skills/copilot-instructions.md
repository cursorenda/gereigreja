# Instruções do Copilot para Gereigreja

## Visão Geral do Projeto
- **Gereigreja** é uma aplicação web Django para gestão eclesiástica, com apps modulares para finanças, eventos, comunicação, configuração e gestão de membros.
- O projeto usa uma estrutura clássica do Django: cada app (ex: `financeiro`, `eventos`, `contas`, `configuracao`, `secretaria`) contém seus próprios `models.py`, `views.py`, `forms.py`, `urls.py` e `templates/`.
- As configurações principais e roteamento estão em `core/settings.py` e `core/urls.py`.

## Padrões e Convenções Principais
- **Estrutura dos Apps:** Cada app é autocontido. Templates são organizados em `templates/<app_name>/`.
- **Banco de Dados:** Usa Supabase (PostgreSQL) em produção. Backups são armazenados em `/backup/`.
- **Media & Static:** Arquivos de usuário ficam em `/media/`; arquivos estáticos em `/static/`, `/staticfiles/` e `/staticfiles_production/`.
- **Utilitários Customizados:** Lógica compartilhada geralmente fica em `utils.py` dentro de cada app.
- **Signals:** Alguns apps (ex: `financeiro`, `comunicacao`) usam Django signals para efeitos colaterais.
- **Templatetags:** Tags customizadas de template ficam em `<app>/templatetags/`.

## Fluxos de Trabalho do Desenvolvedor
- **Rodar Servidor:** `python manage.py runserver`
- **Migrações:** `python manage.py makemigrations` e `python manage.py migrate`
- **Criar Superusuário:** `python manage.py createsuperuser`
- **Testes:** Execute testes com `python manage.py test <app>` (ex: `python manage.py test financeiro`)
- **Arquivos Estáticos:** Colete com `python manage.py collectstatic`
- **Backups:** Backups manuais são armazenados em `/backup/` (veja scripts de backup se presentes).

## Pontos de Integração
- **Forms:** Cada app usa Django forms para validação e interfaces de admin.
- **Admin:** Lógica customizada de admin por app em `admin.py`.
- **Comunicação Entre Apps:** Use Django signals ou utilitários compartilhados para lógica cross-app.
- **Dependências Externas:** Todas as dependências Python estão listadas em `requirements.txt`.

## Notas Específicas do Projeto
- **Logging de Erros:** Logs são escritos em `logs/django_errors.log` e `erros.log`.
- **Data Dumps:** Dumps de dados JSON estão na raiz do projeto (ex: `datadump.json`).
- **Nomenclatura de Backups:** Backups são timestamped para rastreabilidade.
- **Debugging:** Use `debug.log` para output de debug customizado.

## Exemplos
- Para adicionar uma nova funcionalidade financeira, crie um model em `financeiro/models.py`, registre-o em `financeiro/admin.py` e adicione views/templates conforme necessário.
- Para lógica customizada de template, adicione uma templatetag em `financeiro/templatetags/` e carregue-a no seu template.

---

## Skills Disponíveis

Este arquivo faz parte do sistema de skills do Gereigreja. Para instruções específicas por módulo, consulte:

### Core
- **`financeiro/SKILL.md`** → Gestão financeira (receitas, despesas, contas, relatórios)
- **`secretaria/SKILL.md`** → Cadastro de pessoas, famílias, status de membros
- **`comunicacao/SKILL.md`** → E-mails, SMS, notificações em massa

### Administrativo
- **`configuracao/SKILL.md`** → Organizações, usuários, permissões, integrações
- **`deploy/SKILL.md`** → Versionamento, deploy, release notes
- **`backup/SKILL.md`** → Backup e restauração do banco PostgreSQL

### Ministérios
- **`eventos/SKILL.md`** → Gestão de eventos, inscrições, controle de presença
- **`escola-biblica/SKILL.md`** → Turmas, alunos, professores, frequência, aulas
- **`agenda/SKILL.md`** → Compromissos, reuniões, calendário da igreja

### Suporte
- **`suporte/SKILL.md`** → Tickets de atendimento, SLA, base de conhecimento

## Como o Agente Usa as Skills

1. **Leitura Inicial**: Agente lê apenas `name` e `description` de cada skill (progressive disclosure)
2. **Ativação Automática**: Quando detecta relevância, carrega o SKILL.md completo
3. **Execução**: Segue instruções, exemplos e boas práticas da skill
4. **Scripts Opcionais**: Se necessário, executa scripts na pasta `scripts/`

## Exemplo de Uso

**Usuário**: "Preciso criar um relatório financeiro de dezembro"

**Agente**:
1. Identifica keyword "financeiro" e "relatório" 
2. Ativa skill **gerenciando-financeiro**
3. Segue estrutura e exemplos do SKILL.md
4. Gera código usando os padrões definidos

---

**Para agentes de IA:**
- Respeite a estrutura modular dos apps—mantenha a lógica dentro do app relevante, a menos que seja uma preocupação cross-cutting.
- Ao atualizar models, sempre crie e aplique migrações.
- Use padrões existentes de utility e signal para lógica compartilhada ou de efeitos colaterais.
- Referencie convenções de backup e logging para quaisquer funcionalidades de dados ou tratamento de erros.
- **Consulte as skills específicas em `skills/<modulo>/SKILL.md` para instruções detalhadas por área.**
- **Priorize exemplos práticos**: Todas as skills têm código de exemplo (one-shot/few-shot learning)
- **Siga boas práticas**: Cada skill define padrões de código e validações obrigatórias
