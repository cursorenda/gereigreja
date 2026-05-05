# 🤖 Contexto Geral do Sistema Gereigreja — Para Agentes de IA

**Versão:** v1.9.2  
**Última Atualização:** 05/05/2026  
**Público-alvo:** Agentes de IA (GitHub Copilot, Claude, GPT, etc.)

---

## TL;DR — Leitura em 2 minutos

- **Stack:** Django 5.2 + Python 3.13, PostgreSQL (Supabase), Bootstrap 5, Stripe, Cloudinary, Render
- **Paradigma:** Multi-tenant (Ministério → Igreja → Membro), controle de acesso baseado em grupos Django
- **Venv:** `c:\Gereigreja\.venv` (Windows)
- **App principal para assinatura:** `configuracao/`
- **App principal para pessoas:** `secretaria/`
- **Permissões:** `contas/page_permissions.py` + `core/decorators.py`
- **Escopo multi-tenant:** `core/middleware.py` (`ActiveChurchMiddleware`) + `request.igreja_ativa`
- **Template base:** `templates/base_com_menu.html`
- **Hierarquia de plano:** `LiberacaoPlanoMinisterio` > `AssinaturaMinisterio.plano` > fallback `'pioneiro'`

---

## 1. Estrutura do Projeto

```
c:\Gereigreja\
├── agenda/          # Eventos de agenda pastoral
├── auditoria/       # Log de auditoria de ações
├── comunicacao/     # Comunicação em massa (e-mail, SMS, mural)
├── configuracao/    # Assinaturas, planos, ministério, igrejas, usuários
├── contas/          # Autenticação, grupos, permissões, convites
├── core/            # Middleware, decorators, utils, helpers globais
├── demo/            # Modo demonstração do sistema
├── escola_biblica/  # EBD: turmas, alunos, professores, frequência
├── eventos/         # Eventos, inscrições, participantes
├── financeiro/      # Receitas, despesas, contas, relatórios
├── notificacoes/    # Sistema de notificações internas
├── secretaria/      # CRUD de pessoas, famílias, visitantes, cargos, grupos
├── suporte/         # Tickets de suporte
├── templates/       # Templates globais (base, menu, partials)
├── tests/           # Testes centralizados (prefixo de app no nome)
└── docs/            # Documentação
```

---

## 2. Hierarquia Multi-Tenant

```
User (django.contrib.auth.User)
  └─ PerfilUsuario (configuracao)
       └─ Ministerio                 # Organização eclesiástica (ex: "Assembleia de Deus SP")
            ├─ AssinaturaMinisterio  # Plano e status de pagamento
            ├─ LiberacaoPlanoMinisterio  # Override de plano (beta/pilot)
            └─ Igreja (1..N)         # Sede / Regional / Congregação
                 └─ Pessoa (secretaria) # Membro, Visitante, etc.
```

**Hierarquia de igrejas:**
- `sede` → `regional` → `congregacao` | `independente`
- FK `igreja_superior` (auto-referência)
- `Igreja.get_descendants()` retorna todas as subordinadas recursivamente

**Acesso ao Ministério do usuário:**
```python
from configuracao.services_assinatura import obter_ministerio_do_usuario
ministerio = obter_ministerio_do_usuario(request.user)

# Ou via helper de view:
from core.utils import get_ministerio_or_error
ministerio = get_ministerio_or_error(request)  # levanta Http404 se não encontrado
```

---

## 3. Sistema de Permissões

### 13 grupos hierárquicos

| Nível | Grupos |
|-------|--------|
| Ministerial | Admin Ministerio, Pastor Regional, Tesoureiro |
| Local | Admin Org, Pastor Local, Secretario Local, Tesoureiro Local, Regente, Lider Eventos |
| EBD | Superintendente EBD, Secretaria EBD, Professor |
| Básico | Membro Comum |

### Padrão de proteção de views

```python
from django.contrib.auth.decorators import login_required
from core.decorators import page_access_required

@login_required
@page_access_required('financeiro')  # chave definida em contas/page_permissions.py
def minha_view(request):
    ...
```

### Regras centralizadas
- `contas/page_permissions.py` → `PAGE_ACCESS_RULES = { 'chave': [grupos...] }`
- `core/decorators.py` → `page_access_required`, `inject_igrejas_permitidas`

### Permissões de módulo por plano
- `configuracao/services_assinatura.py` → `ministerio_pode_usar_modulo(ministerio, modulo)`
- Campos `permite_modulo_*` no model `Plano`

---

## 4. Escopo Multi-Tenant (Igreja Ativa)

### Middleware: `core/middleware.py` (`ActiveChurchMiddleware`)

Injeta em **toda request autenticada**:
- `request.igrejas_permitidas` → QuerySet de igrejas acessíveis
- `request.igreja_ativa` → Igreja selecionada na sessão (ou única disponível)

### Padrão em views

```python
# Filtrar dados pela igreja ativa:
dados = Membro.objects.filter(igreja=request.igreja_ativa)

# Filtrar por todas as igrejas permitidas:
dados = Membro.objects.filter(igreja__in=request.igrejas_permitidas)

# Nunca acesse request.igreja_ativa sem verificar:
igreja_ativa = getattr(request, 'igreja_ativa', None)
```

### Funções utilitárias de escopo (secretaria)
```python
from secretaria.views._base import _membros_queryset_por_escopo, get_request_scoped_churches
igrejas = get_request_scoped_churches(request)
membros = _membros_queryset_por_escopo(request)
```

---

## 5. Sistema de Assinatura e Planos

### Determinação do plano efetivo
```python
# SEMPRE usar esta função — não acessar assinatura.plano diretamente
from configuracao.services_assinatura import obter_plano_efetivo_ministerio
plano = obter_plano_efetivo_ministerio(ministerio)
# Prioridade: LiberacaoPlanoMinisterio > AssinaturaMinisterio.plano > pioneiro (fallback)
```

### Verificar se assinatura está regular
```python
from configuracao.services_assinatura import assinatura_esta_regular, obter_assinatura_ministerio
assinatura = obter_assinatura_ministerio(ministerio)
regular = assinatura_esta_regular(assinatura, ministerio)
```

### Planos — campos críticos
- `codigo_plano` → identificador único (`'pioneiro'`, `'crescimento'`, `'ministerio'`, `'rede'`)
- `limite_membros` → 0 = ilimitado
- `limite_igrejas` → 0 = ilimitado
- `ordem_liberacao` → hierarquia (menor = mais básico)

### Verificar limites
```python
from configuracao.services_assinatura import contar_pessoas_ativas, obter_limite_pessoas_ativas
pessoas = contar_pessoas_ativas(ministerio)   # status='Ativo' em todas as igrejas
limite = obter_limite_pessoas_ativas(plano)   # 0 = ilimitado
excede = limite > 0 and pessoas > limite
```

### Tipos de período especial
- **Cortesia:** 3 dias, para ministérios recém-criados
- **Trial:** 14 dias, ativado pelo usuário, registra em `HistoricoAssinatura`
- **Graça por inadimplência:** dias após falha de pagamento antes do downgrade

---

## 6. Apps e Responsabilidades

### `secretaria/`
- CRUD de Pessoas (Membro, Visitante, etc.)
- Famílias, Visitantes, Acompanhamentos de visita
- Cargos e Ocupantes
- Grupos de Casa (células)
- Histórico de status e tipo
- Linha do Tempo
- **views/** modularizado em 9 arquivos (desde v1.9.2)

### `financeiro/`
- Receitas e Despesas
- Contas Bancárias
- Categorias financeiras
- Relatórios e permissões de caixa
- Ordenação por coluna nas listagens (desde v1.9.2)

### `comunicacao/`
- Envio em massa (e-mail, SMS)
- Mural de Avisos (acessível a todos os usuários, incluindo Membro Comum)
- Decorators: `@page_access_required('mural_avisos')` para leitura, `@page_access_required('comunicacao')` para escrita

### `notificacoes/`
- Sistema de notificações internas (extraído de `comunicacao/` na v1.8.80)
- Lista com filtro lidas/não lidas, ações em lote

### `configuracao/`
- Ministério e Igrejas
- Usuários e PerfilUsuario
- Planos e Assinaturas (Stripe)
- Onboarding
- Configurações do sistema (`ConfiguracaoSistema`)

### `contas/`
- Login/logout, registro, convites
- Grupos e permissões (management command `configurar_permissoes_grupos`)
- `page_permissions.py` → regras centrais de acesso a páginas

### `core/`
- Middleware (`ActiveChurchMiddleware`)
- Decorators (`page_access_required`, `inject_igrejas_permitidas`)
- Utils (`get_ministerio_or_error`, `get_igrejas_permitidas`)
- Context processors

### `escola_biblica/`
- Turmas, alunos, frequência
- Professores têm permissões específicas (`Professor` group)

---

## 7. Templates

### Hierarquia
```
templates/
├── base.html               # Base sem menu (login, etc.)
├── base_com_menu.html      # Base com sidebar + topnav (maioria das views)
│   └── menu.html           # Menu lateral (incluso dinamicamente)
└── partials/
    └── _messages.html      # Flash messages (incluído APENAS no base)
```

**ATENÇÃO:** `_messages.html` é incluído automaticamente pelo `base_com_menu.html`. **Nunca inclua novamente** em templates filhos — causa mensagens duplicadas.

### Convenções
- Filtros customizados: `{% load my_filters %}`, `{% load assinatura_extras %}`, `{% load financeiro_tags %}`
- Separador de milhar em IDs: usar `|unlocalize` para evitar formatação pt-BR quebrando JS
- Dados para JS: usar `{{ dados|json_script:"id" }}` em vez de interpolação direta
- `{% with var=True %}` NÃO pode estar dentro de `{% if %}...{% else %}...{% endif %}` — isso gera `TemplateSyntaxError`

---

## 8. Padrões de Código

### Related names importantes
```python
user.perfil                 # PerfilUsuario
user.membro_secretaria      # Pessoa (NÃO user.pessoa)
ministerio.assinatura       # AssinaturaMinisterio
ministerio.igrejas          # QuerySet[Igreja]
ministerio.perfis_usuarios  # QuerySet[PerfilUsuario]
igreja.ministerio           # Ministerio (FK)
ministerio.historicos_assinatura  # QuerySet[HistoricoAssinatura]
```

### Resolução de ministério
```python
# ORDEM DE RESOLUÇÃO em obter_ministerio_do_usuario():
# 1. user.perfil.ministerio
# 2. user.membro_secretaria.igreja.ministerio
# 3. Ministerio.objects.filter(administrador_principal=user).first()
```

### Queryset de pessoas ativas
```python
# "Pessoas ativas" = status exatamente 'Ativo' (case-sensitive)
Pessoa.objects.filter(
    igreja__ministerio=ministerio,
    status='Ativo'
)
```

---

## 9. Integração com Serviços Externos

| Serviço | Uso | Config |
|---------|-----|--------|
| **Stripe** | Assinaturas, checkout, billing portal, webhooks | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` |
| **PostgreSQL (Supabase)** | Banco de dados principal | `DATABASE_URL` |
| **Cloudinary** | Armazenamento de imagens/mídia | `CLOUDINARY_URL` |
| **Render** | Hospedagem e deploy | `.cpanel.yml`, `deploy/` |
| **AWS S3** | Armazenamento alternativo (scripts de teste disponíveis) | `AWS_*` vars |

---

## 10. Testes

- Centralizados em `tests/` (desde v1.9.1)
- Prefixo de app no nome: `test_secretaria_*.py`, `test_financeiro_*.py`, etc.
- Framework: `pytest` + `pytest-django`
- Config: `pytest.ini`
- Suite atual: **135 testes, 0 falhas** (v1.9.2)

```bash
# Rodar testes:
cd c:\Gereigreja
.venv\Scripts\activate
pytest tests/ -v
```

---

## 11. Validação de Template Django

```bash
# Verificar sintaxe do template sem precisar subir o servidor:
cd c:\Gereigreja
.venv\Scripts\python.exe -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','gereigreja.settings')
django.setup()
from django.template.loader import get_template
get_template('caminho/para/template.html')
print('Template OK')
"
```

---

## 12. Histórico de Versões Recentes

| Versão | Data | Destaque |
|--------|------|---------|
| **v1.9.2** | 03/05/2026 | Modularização da secretaria (9 módulos), correções multi-tenant, seletor de igrejas em árvore |
| **v1.9.1** | 02/05/2026 | Correções de templates, links legados (404), consolidação de testes em `tests/` |
| **v1.9.0** | 01/05/2026 | Portal do Membro, menu unificado, redirect inteligente pós-login |
| **v1.8.80** | 28/04/2026 | App `notificacoes` extraído de `comunicacao` |
| **v1.8.79** | 22/04/2026 | Lista de pessoas: colunas Tipo e Status separadas, ordenação clicável |
| **v1.8.78** | 21/04/2026 | Bulk edit de pessoas corrigido, middleware ajustado |
| **v1.8.77** | 19/04/2026 | Auto cadastro corrigido, onboarding aprimorado |
| **v1.8.75** | 16/04/2026 | Máscara CNPJ, seletor integrado |
| ≤ v1.8.67 | — | Ciclo longo: permissões, EBD, validações de cadastro |

---

## 13. Pontos de Atenção para IA

### Não fazer

1. **Não usar `{% with var=True %}` dentro de `{% if %}...{% else %}`** — gera `TemplateSyntaxError`. Calcule booleanos na view e passe no contexto.

2. **Não acessar `user.pessoa`** — o related name correto é `user.membro_secretaria`.

3. **Não filtrar pessoas por `status='ativo'`** — o valor correto é `'Ativo'` (primeira letra maiúscula, case-sensitive).

4. **Não ignorar `LiberacaoPlanoMinisterio`** — sempre usar `obter_plano_efetivo_ministerio()` para obter o plano real.

5. **Não incluir `_messages.html` em templates filhos** — o base já inclui.

6. **Não usar `request.igrejas_permitidas` sem verificar se o middleware rodou** — use `getattr(request, 'igrejas_permitidas', Igreja.objects.none())`.

7. **Não usar `Igreja.objects.filter(ministerio=m)` para listar igrejas de um usuário** — um usuário pode ter acesso restrito; usar `get_igrejas_permitidas(user, ministerio)`.

8. **Não renderizar IDs numéricos diretamente em JS com locale pt-BR ativo** — usar `|unlocalize` para evitar `1.118` em vez de `1118`.

### Padrões confirmados que funcionam

```python
# ✅ Resolver ministério
ministerio = get_ministerio_or_error(request)

# ✅ Obter plano efetivo
plano = obter_plano_efetivo_ministerio(ministerio)

# ✅ Checar acesso ao sistema
if not assinatura_esta_regular(assinatura, ministerio):
    return redirect('configuracao:gerenciar_assinatura')

# ✅ Contar pessoas ativas
total = contar_pessoas_ativas(ministerio)

# ✅ Proteger view por permissão
@login_required
@page_access_required('secretaria')
def minha_view(request):
    ...

# ✅ Filtrar por escopo de igreja
membros = Membro.objects.filter(igreja=request.igreja_ativa)
```

---

## 14. Arquivos de Contexto Complementares

| Arquivo | Conteúdo |
|---------|----------|
| `docs/ai/AI_CONTEXT_CHURCH_SELECTOR.md` | Detalhes do seletor de igreja e isolamento multi-tenant |
| `docs/sistema/ARQUITETURA_ASSINATURA_PLANOS.md` | Arquitetura técnica do sistema de assinatura |
| `docs/sistema/DECORATORS_SEGURANCA.md` | Decorators de segurança e padrões de proteção de views |
| `docs/sistema/GRUPOS_PERMISSOES.md` | Sistema de grupos e permissões |
| `docs/sistema/GUIA_ESCOPO_VIEWS.md` | Padrões de escopo multi-tenant em views |
| `CHANGELOG.md` | Histórico completo de todas as versões |
