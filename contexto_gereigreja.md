Resumo do Projeto:

Objetivo Principal: Sistema de gestão eclesiástica para administrar organizações, igrejas, membros e finanças.

Tecnologias Chave (Versões Atuais):
- Python: 3.11.9 (no servidor de hospedagem)
- Django: 3.2.25 (escolhido pela compatibilidade com o PostgreSQL 10.23 da hospedagem, mas atualmente usando SQLite3 na hospedagem)
- Banco de Dados (Hospedagem): SQLite3 (configurado em `settings.py`)
- Banco de Dados (Desenvolvimento Local): SQLite3
- Servidor de Aplicação (Hospedagem): Gunicorn (conforme `requirements.txt`, provável uso pela hospedagem)
- Servidor Web (Hospedagem): (Ex: Apache ou Nginx - a ser confirmado com a BrasilLinkHost)
- Bibliotecas Python Principais: Whitenoise (para arquivos estáticos), Pillow (para imagens), num2words, GitPython (conforme `requirements.txt`).
- Frontend: (Ex: Bootstrap, Chart.js, JavaScript personalizado - a ser detalhado conforme o projeto)

Ambiente de Hospedagem:
- Provedor: BrasilLinkHost
- Endereço IP do Servidor: 199.167.147.66
- Sistema Operacional do Servidor: (Provavelmente Linux - a ser confirmado com a BrasilLinkHost)
- Versão do Python no Servidor: 3.11.9
- Versão do PostgreSQL Disponível no Servidor: 10.23 (motivo pelo qual o Django foi ajustado para 3.2.25, embora SQLite3 esteja em uso)
- Gerenciamento de Ambiente Python no Servidor: virtualenv (localizado em `/home/gerei1/virtualenv/gereigreja.site/3.11/`)
- Acesso ao Terminal no Servidor: Via SSH ou interface "Execute python script" no painel de controle da hospedagem.
- Configuração de Domínio (DNS): Domínio `gereigreja.site` registrado na GoDaddy, com nameservers (`ns1.brasillinkhost.com.br`, `ns2.brasillinkhost.com.br`, etc.) apontando para a BrasilLinkHost.

Estrutura de Diretórios Principal (Exemplo):


`settings.py` (Seção `INSTALLED_APPS`):
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
]
