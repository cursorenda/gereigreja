# Modo Demonstração — GereIgreja

**Versão:** v1.9.0
**Status:** Versão publicada em produção
**Última atualização:** 01/05/2026

---

## Visão Geral

O modo demonstração permite que qualquer pessoa explore o sistema sem afetar dados reais. Ele cria um ambiente isolado (ministério "DEMONSTRAÇÃO") com usuários, igrejas, membros, lançamentos financeiros, eventos e notificações pré-populados. O acesso é feito via login sem senha — o visitante seleciona um perfil e entra automaticamente.

---

## App `demo`

| Item | Valor |
|---|---|
| Localização | `demo/` |
| Registro em INSTALLED_APPS | `'demo'` (`core/settings.py` linha 88) |
| Namespace de URL | `demo` |
| Prefixo de rota | `/demo/` |

### URLs disponíveis

| Nome | Caminho | View | Descrição |
|---|---|---|---|
| `demo:demo_login` | `/demo/login/` | `demo_login_view` | Página de seleção de perfil e login automático |
| `demo:demo_dashboard` | `/demo/dashboard/` | `demo_dashboard_view` | Redireciona para `secretaria:dashboard` |
| `demo:demo_trocar_perfil` | `/demo/trocar-perfil/` | `demo_trocar_perfil_view` | Troca o perfil logado sem sair do modo demo |
| `demo:demo_reset` | `/demo/resetar/` | `demo_reset_view` | Reseta e repovoa os dados demo (apenas `demo_admin`) |

---

## Usuários Demo

Criados pelo comando `popular_demo`. Todos usam a **senha `demo123`**.

| Username | Grupo Django | Email | is_staff | Perfil no formulário |
|---|---|---|---|---|
| `demo_admin` | Admin Ministerio | admin@demo.com | ✅ | `admin` / `administrador` |
| `demo_tesoureiro` | Tesoureiro | tesoureiro@demo.com | ✅ | `tesoureiro` |
| `demo_pastor` | Pastor Local | pastor@demo.com | ✅ | `pastor` |
| `demo_secretario` | Secretario Local | secretario@demo.com | ✅ | `secretario` |
| `demo_membro` | Membro Comum | membro@demo.com | ❌ | `membro` |

> **Importante:** Nenhum usuário demo é `is_superuser`. O `demo_admin` tem `is_staff=True` apenas para acesso ao Django Admin de suporte.

Todos os usuários demo têm um `PerfilUsuario` vinculado ao ministério "DEMONSTRAÇÃO" e com acesso a todas as igrejas do ministério demo.

---

## Dados Populados (`popular_demo`)

### Estrutura de Igrejas

```
Ministério DEMONSTRAÇÃO
└── Igreja Sede DEMO (sede)
    ├── Regional 1 DEMO (regional)
    │   ├── Congregação 1-1 DEMO (congregacao)
    │   ├── Congregação 1-2 DEMO (congregacao)
    │   └── Congregação 1-3 DEMO (congregacao)
    ├── Regional 2 DEMO (regional)
    │   ├── Congregação 2-1 DEMO ... (3 congregações)
    └── Regional 3 DEMO (regional)
        └── Congregação 3-1 DEMO ... (3 congregações)
```

**Total:** 1 sede + 3 regionais + 9 congregações = **13 igrejas**

### Assinatura

- Tipo: `gratuita`
- Validade: 10 anos a partir da criação (`data_fim = now + 3650 dias`)
- Garante acesso funcional sem restrições de assinatura.

### Membros (Secretaria)

- 10 membros por igreja → **130 pessoas** no total
- `TipoPessoa`: "Membro"
- `StatusPessoa`: "Ativo"
- CPF no formato `{pk_igreja:03d}.{i:03d}.000-00`
- Email no formato `{pk_igreja}_{i}@demo.com`

### Financeiro

Por cada uma das 13 igrejas:
- **1 conta bancária** — "Caixa DEMO" (tipo `caixa_fisico`, saldo inicial R$1.000)
- **3 receitas** — valores R$100, R$200, R$300
- **3 despesas** — valores R$50, R$100, R$150, categoria "Operacional DEMO"

### Eventos

Na Igreja Sede DEMO:
- "Culto de Celebração DEMO" (tipo `culto`)
- "Reunião de Líderes DEMO" (tipo `reuniao`)
- "Festa da Família DEMO" (tipo `festa`, 2 dias)

Cada evento tem **10 participações** de membros da sede, com `papel=PARTICIPANTE` e `status=CONFIRMADO`.

### Notificações

- **2 notificações** por usuário demo (5 usuários = 10 notificações)
- Tipos aleatórios entre: `info`, `aviso`, `financeiro`, `membro`, `alerta`, `sucesso`
- Alternância de leitura: 1 lida, 1 não lida por usuário
- **3 notificações enviadas** (`NotificacaoEnviada`) com destinatários fictícios

---

## Comando de Gerenciamento

### `popular_demo`

```bash
python manage.py popular_demo
```

Localização: `secretaria/management/commands/popular_demo.py`

- Usa `get_or_create` em todo lugar — seguro para executar múltiplas vezes (idempotente).
- Cria toda a estrutura descrita acima.
- Garante que assinatura e ministério estejam ativos mesmo se já existirem.

### `reset_demo` (via URL `/demo/resetar/`)

- Disponível apenas para o usuário `demo_admin` logado.
- Executa `manage.py reset_demo` seguido de `manage.py popular_demo` via `subprocess`.
- **Atenção:** o comando `reset_demo` em si não está implementado como management command no repositório atual — a view chama o subprocess mas o comando precisa ser criado separadamente para funcionar.

---

## Fluxo de Login Demo

```
Usuário acessa /demo/login/
    └── Seleciona perfil (Admin / Tesoureiro / Pastor / Secretário / Membro)
        └── POST → _resolve_demo_username(perfil) → username
            └── authenticate(username, password='demo123')
                └── login() → _demo_redirect_home(user)
                    ├── can_dashboard_secretaria? → secretaria:dashboard
                    └── não                      → secretaria:portal_membro
```

A função `_resolve_demo_username` normaliza o perfil (lowercase + remove acentos) antes de consultar o mapeamento.

A função `_demo_redirect_home(user)` (em `demo/views.py`) resolve o destino pós-login verificando a permissão `dashboard_secretaria`. Perfis sem essa permissão (ex: **Membro Comum**) são redirecionados para o Portal do Membro em vez do dashboard, evitando "Acesso Negado".

---

## Troca de Perfil

- O link **"Trocar perfil"** no banner amarelo de demonstração abre um **modal Bootstrap** diretamente na página atual — sem navegação para `/demo/trocar-perfil/`.
- O modal faz POST para a mesma URL `demo:demo_trocar_perfil`, mantendo o backend inalterado.
- A página `/demo/trocar-perfil/` ainda existe como fallback caso seja acessada diretamente.
- Após a troca, o redirecionamento usa `_demo_redirect_home(user)` (ver seção acima).

### Banner de Demonstração

O banner amarelo fixo no topo é renderizado em `templates/base_com_menu.html` para qualquer usuário cujo `username` começa com `demo_`. Contém:

| Item | Comportamento |
|---|---|
| **Trocar perfil** | Abre modal Bootstrap inline (sem navegação) |
| **Resetar dados** | Navega para `/demo/resetar/` (somente `demo_admin`) |

---

## Templates

| Template | Caminho |
|---|---|
| Login demo | `demo/templates/demo/demo_login.html` |
| Dashboard demo | `demo/templates/demo/demo_dashboard.html` |
| Trocar perfil | `demo/templates/demo/demo_trocar_perfil.html` |
| Reset | `demo/templates/demo/demo_reset.html` |

---

## Considerações de Segurança

- Os usuários demo são **facilmente identificáveis** pelo prefixo `demo_` — nunca devem ser criados em produção com dados reais.
- A senha `demo123` é pública por design; o ambiente demo deve ser isolado (ministério próprio, sem acesso a dados de clientes reais).
- A view `demo_reset_view` verifica `username == 'demo_admin'` antes de executar o reset.
- Em produção real (com clientes), o app `demo` pode ser desativado removendo `'demo'` de `INSTALLED_APPS` e a rota de `core/urls.py`.

---

## Referências

- `demo/views.py` — Views do modo demo
- `demo/urls.py` — Rotas do app
- `demo/apps.py` — Configuração do app
- `secretaria/management/commands/popular_demo.py` — Comando de população
- `core/settings.py` linha 88 — Registro em INSTALLED_APPS
- `core/urls.py` linha 60 — Inclusão das rotas
