# ⚙️ Arquitetura — Sistema de Assinatura e Planos

**Versão:** v1.9.2  
**Última Atualização:** 05/05/2026  
**Público-alvo:** Desenvolvedores  
**Status:** Em produção

---

## 1. Visão Geral

O sistema de assinatura controla quais funcionalidades e capacidades cada ministério pode usar. A lógica é multi-camada:

```
Ministério
  └─ AssinaturaMinisterio (plano contratado + status de pagamento)
  └─ LiberacaoPlanoMinisterio (override de plano para beta/pilot)
  └─ HistoricoAssinatura (registro de eventos: mensalidade, cortesia, trial)
```

**Regra central de determinação do plano efetivo:**

```python
# configuracao/services_assinatura.py :: obter_plano_efetivo_ministerio()
# Prioridade:
# 1. LiberacaoPlanoMinisterio ativo (beta/pilot override)
# 2. AssinaturaMinisterio.plano (plano contratado)
# 3. Fallback: Plano com codigo_plano='pioneiro'
```

---

## 2. Modelos

### `Plano` (`configuracao/models.py`)

Define os planos disponíveis no sistema.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `codigo_plano` | CharField | Identificador único (ex: `'pioneiro'`, `'crescimento'`) |
| `nome` | CharField | Nome exibido |
| `preco_mensal` | DecimalField | 0 = gratuito |
| `preco_anual` | DecimalField | 0 = sem opção anual |
| `limite_membros` | IntegerField | 0 = ilimitado |
| `limite_igrejas` | IntegerField | 0 = ilimitado |
| `ordem_liberacao` | IntegerField | Posição na hierarquia (menor = mais básico) |
| `ativo` | BooleanField | Plano disponível no sistema |
| `is_visible` | BooleanField | Visível nos seletores internos |
| `liberado_publicamente` | BooleanField | Aparece na landing page pública |
| `contratacao_publica_liberada` | BooleanField | Pode ser contratado por qualquer ministério |
| `permite_modulo_*` | BooleanField | Flags de acesso a cada módulo |

### `AssinaturaMinisterio` (`configuracao/models.py`)

Registro da assinatura ativa de um ministério.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `ministerio` | FK | One-to-one com Ministério |
| `plano` | FK | Plano contratado |
| `status` | CharField | `'ativa'`, `'gratuita'`, `'vencida'`, `'pendente_pagamento'`, `'cancelada'` |
| `stripe_subscription_id` | CharField | ID da assinatura no Stripe |
| `data_inicio` | DateTimeField | Início da assinatura |
| `data_fim` | DateTimeField | Fim do período pago (null = recorrente) |
| `trial_ativo` | BooleanField | Se está no período de trial |
| `data_inicio_trial` | DateTimeField | Quando o trial começou |
| `dias_trial_totais` | IntegerField | Duração do trial (padrão: 14) |
| `data_inicio_cortesia` | DateTimeField | Início do período de cortesia |
| `dias_cortesia_totais` | IntegerField | Duração da cortesia (padrão: 3) |
| `data_fim_graca_inadimplencia` | DateTimeField | Até quando o acesso continua com pagamento em atraso |
| `tentativas_falha_pagamento` | IntegerField | Contador de falhas consecutivas no Stripe |

**Status regulares:** `{'ativa', 'gratuita'}` — definidos em `STATUS_ASSINATURA_REGULAR`

### `LiberacaoPlanoMinisterio` (`configuracao/models.py`)

Override manual de plano, usado para beta/pilot de novos planos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `ministerio` | FK | Ministério beneficiado |
| `plano` | FK | Plano liberado |
| `ativo` | BooleanField | Se a liberação está em vigor |
| `pode_visualizar` | BooleanField | Aparece nos seletores internos |
| `pode_contratar` | BooleanField | Pode assinar via checkout |

**Efeito:** Quando `ativo=True` e `pode_visualizar=True`, `obter_plano_efetivo_ministerio()` retorna este plano em vez do plano da assinatura.

### `HistoricoAssinatura` (`configuracao/models.py`)

Log imutável de eventos financeiros/de acesso.

```python
TIPOS = [
    ('mensalidade', 'Mensalidade'),   # Pagamento processado pelo Stripe
    ('cortesia', 'Cortesia'),          # Período de cortesia inicial (3 dias)
    ('trial', 'Teste Grátis'),         # Trial iniciado pelo usuário (14 dias)
]
STATUS = ['paga', 'expirada', 'a_vencer', 'vencida']
```

---

## 3. Services (`configuracao/services_assinatura.py`)

### Funções de resolução de plano

```python
obter_plano_efetivo_ministerio(ministerio) -> Optional[Plano]
# Plano que de fato está em uso (LiberacaoPlanoMinisterio > AssinaturaMinisterio > pioneiro)

obter_limite_pessoas_ativas(plano) -> int
# Retorna plano.limite_membros (0 = ilimitado)

contar_pessoas_ativas(ministerio) -> int
# SELECT COUNT(*) WHERE status='Ativo' em todas as igrejas do ministério

ministerio_pode_criar_igreja(ministerio) -> bool
# Verifica se igrejas_count < plano.limite_igrejas (0 = ilimitado)
```

### Funções de elegibilidade de assinatura

```python
assinatura_esta_regular(assinatura, ministerio) -> bool
# Retorna True se o ministério pode acessar o sistema
# Ordem de verificação:
# 1. Trial ativo e não expirado
# 2. status in {'ativa', 'gratuita'}
# 3. Período de cortesia válido
# 4. Status vencida mas dentro do limite do plano gratuito
```

### Trial e Cortesia

```python
iniciar_trial(ministerio) -> AssinaturaMinisterio
# Ativa trial de 14 dias + cria registro em HistoricoAssinatura

is_trial_ativo(assinatura) -> bool
dias_restantes_trial(assinatura) -> Optional[int]
assinatura_em_graca_inadimplencia(assinatura) -> bool
dias_restantes_graca(assinatura) -> Optional[int]
```

### Visibilidade e contratação de planos

```python
listar_planos_para_ministerio(ministerio) -> QuerySet[Plano]
# Planos que o ministério PODE VER (públicos + liberados especificamente)

ministerio_pode_visualizar_plano(ministerio, plano) -> bool
ministerio_pode_contratar_plano(ministerio, plano) -> bool
```

---

## 4. View principal (`configuracao/views.py`)

### `gerenciar_assinatura(request)`

View unificada que substitui a antiga `minha_assinatura`. A view `minha_assinatura` agora é apenas um redirect.

**Contexto gerado:**

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `ministerio` | Ministerio | Ministério do usuário logado |
| `assinatura_atual` | AssinaturaMinisterio\|None | Assinatura atual |
| `plano_efetivo` | Plano\|None | Plano em uso (considera liberação beta) |
| `plano_assinatura` | Plano\|None | Plano da assinatura (sem override) |
| `plano_efetivo_por_liberacao` | bool | True se plano veio de LiberacaoPlanoMinisterio |
| `liberacao_beta_ativa` | LiberacaoPlanoMinisterio\|None | Objeto da liberação se ativa |
| `pessoas_ativas` | int | Contagem de pessoas ativas |
| `limite_pessoas` | int | Limite do plano efetivo (0 = ilimitado) |
| `percentual_pessoas` | float | % de uso (cap 100) |
| `igrejas_ativas` | int | Quantidade de igrejas |
| `limite_igrejas` | int | Limite de igrejas do plano |
| `percentual_igrejas` | float | % de uso (cap 100) |
| `grace_dias_restantes` | int\|None | Dias restantes de graça |
| `invoices` | list | Faturas do Stripe (via API) |
| `planos_com_tipo` | list[dict] | Lista anotada de planos (ver abaixo) |
| `mostrar_opcao_cortesia` | bool | Se deve exibir botão de cortesia |
| `mostrar_opcao_trial` | bool | Se deve exibir botão de trial |

### `_anotar_tipo_planos(planos, plano_efetivo, pessoas_ativas, igrejas_ativas)`

Helper que enriquece cada plano com metadados para o template:

```python
# Retorna lista de dicts:
{
    'plano': Plano,
    'tipo': 'atual' | 'recomendado' | 'upgrade' | 'downgrade',
    'excede_pessoas': bool,  # pessoas_ativas > plano.limite_membros (quando limite > 0)
    'excede_igrejas': bool,  # igrejas_ativas > plano.limite_igrejas (quando limite > 0)
    'excede_algum': bool,    # excede_pessoas or excede_igrejas
}
```

**Lógica de tipo:**
- `'atual'`: `plano.id == plano_efetivo.id`
- `'recomendado'`: primeiro plano com `ordem_liberacao > efetivo.ordem_liberacao`
- `'upgrade'`: demais planos acima do atual
- `'downgrade'`: planos abaixo do atual

**Lógica de excedência (regra chave):**
```python
excede_pessoas = bool(
    p.limite_membros          # campo existe e é positivo
    and p.limite_membros > 0  # não é ilimitado
    and pessoas_ativas > p.limite_membros
)
```
> Limite 0 = ilimitado → nunca excede.

---

## 5. Template (`configuracao/templates/configuracao/assinatura/gerenciar_assinatura.html`)

### Estrutura

```
1. Header: breadcrumb + botão "Portal de Cobrança"
2. Banners de estado (cortesia / trial / vencimento / irregularidade)
3. Row dois cartões:
   ├── Plano Atual (border-primary)
   └── Uso do Plano (progress bars + acordeão diagnóstico + módulos)
4. Cartões especiais (cortesia e trial — renderizados apenas quando disponíveis)
5. Card com abas Bootstrap:
   ├── Alterar Plano (loop em planos_com_tipo)
   ├── Faturas (invoices do Stripe)
   └── Histórico (HistoricoAssinatura)
6. Modal de cancelamento
```

### Cards de plano na aba "Alterar Plano"

Usam `item.excede_algum` diretamente (calculado na view, não no template), evitando `{% with %}` aninhado dentro de `{% if/else %}` que é inválido no Django.

```html
{% for item in planos_com_tipo %}
  {# item.tipo → visual do card (cor, faixa, badge) #}
  {# item.excede_algum → desabilita botões de assinatura #}
  {# item.excede_pessoas / item.excede_igrejas → detalhe do alerta #}
{% endfor %}
```

**Antipadrão evitado:** `{% with var=True %}...{% else %}...{% with var=False %}` dentro de `{% if/else %}` gera `TemplateSyntaxError: 'else', expected 'endwith'` no Django. Sempre calcule flags booleanas na view.

---

## 6. Integração com Stripe

### Fluxo de assinatura

```
POST /configuracao/assinatura/ (plano_id + ciclo_pagamento)
  └─ gerenciar_assinatura() (POST handler)
      ├─ Valida permissão de contratação
      ├─ Obtém/cria Stripe Customer
      ├─ Cria Checkout Session (modo 'subscription')
      └─ Redirect para Stripe Checkout URL
```

### Webhook (`/configuracao/stripe-webhook/`)

Processa eventos do Stripe e atualiza `AssinaturaMinisterio`:

| Evento Stripe | Ação |
|---------------|------|
| `checkout.session.completed` | Ativa assinatura, define status `'ativa'` |
| `invoice.payment_succeeded` | Renova assinatura, registra em `HistoricoAssinatura` |
| `invoice.payment_failed` | Incrementa `tentativas_falha_pagamento`, inicia grace period |
| `customer.subscription.deleted` | Status `'cancelada'` |

### Billing Portal

Abre o painel do Stripe onde o cliente pode gerenciar cartão, histórico e cancelamento. Gerado via `stripe.billing_portal.Session.create()`.

---

## 7. Grace Period (Graça por Inadimplência)

Quando o pagamento falha (`invoice.payment_failed`):

1. `tentativas_falha_pagamento` é incrementado
2. `data_fim_graca_inadimplencia` é definida (N dias de graça configurável)
3. Durante a graça: `assinatura_esta_regular()` retorna `True`
4. Após expirar: na próxima requisição à view `gerenciar_assinatura`, ocorre downgrade automático para o plano `'pioneiro'`

```python
# Verificação no início da view:
if assinatura_atual.status == 'pendente_pagamento' and assinatura_atual.data_fim_graca_inadimplencia:
    if timezone.now() > assinatura_atual.data_fim_graca_inadimplencia:
        # Downgrade automático para Pioneiro
        plano_pioneiro = Plano.objects.get(codigo_plano='pioneiro')
        assinatura_atual.plano = plano_pioneiro
        assinatura_atual.status = 'gratuita'
        assinatura_atual.save(...)
```

---

## 8. Histórico de Alterações Recentes

### Sessão 05/05/2026

| Arquivo | Mudança |
|---------|---------|
| `configuracao/views.py` | `_anotar_tipo_planos()` agora recebe `pessoas_ativas` e `igrejas_ativas` e pré-calcula `excede_*` flags para cada plano |
| `configuracao/views.py` | `minha_assinatura` view convertida em redirect para `gerenciar_assinatura` |
| `configuracao/views.py` | Import de `contar_pessoas_ativas` adicionado (corrigia `NameError`) |
| `configuracao/services_assinatura.py` | `iniciar_trial()` agora cria registro em `HistoricoAssinatura` com `tipo='trial'` |
| `configuracao/models.py` | `HistoricoAssinatura.TIPOS` inclui `('trial', 'Teste Grátis')` |
| `gerenciar_assinatura.html` | Template unificado: mesclou `minha_assinatura` e `gerenciar_assinatura` em uma única página |
| `gerenciar_assinatura.html` | Removido `{% include 'partials/_messages.html' %}` (duplicava flash messages do base template) |
| `gerenciar_assinatura.html` | Adicionado acordeão "Como este cálculo foi feito" no card de Uso do Plano |
| `gerenciar_assinatura.html` | Cards de plano usam `item.excede_algum` (calculado na view) em vez de `{% with %}` |
| `gerenciar_assinatura.html` | Banner de cortesia: condição `and not mostrar_opcao_cortesia` para evitar duplicata |
| `gerenciar_assinatura.html` | Selos de plano: `atual`, `recomendado`, `upgrade`, `downgrade` em cada card |

---

## 9. Checklist de Manutenção

Ao modificar planos ou assinaturas:

- [ ] Atualizar `ordem_liberacao` ao adicionar novos planos (afeta lógica de `tipo` nos cards)
- [ ] Verificar se `codigo_plano='pioneiro'` existe — é usado como fallback obrigatório
- [ ] Testar template com `python manage.py shell -c "from django.template.loader import get_template; get_template('configuracao/assinatura/gerenciar_assinatura.html')"`
- [ ] Não usar `{% with %}` aninhado em `{% if/else %}` no Django (inválido)
- [ ] Ao adicionar novos tipos em `HistoricoAssinatura.TIPOS`, criar migration

---

## 10. Relacionamentos Relevantes

```python
# Acessar plano efetivo de um ministério:
from configuracao.services_assinatura import obter_plano_efetivo_ministerio
plano = obter_plano_efetivo_ministerio(ministerio)

# Verificar se está regular:
from configuracao.services_assinatura import assinatura_esta_regular, obter_assinatura_ministerio
assinatura = obter_assinatura_ministerio(ministerio)
regular = assinatura_esta_regular(assinatura, ministerio)

# Contar pessoas ativas:
from configuracao.services_assinatura import contar_pessoas_ativas
total = contar_pessoas_ativas(ministerio)
```
