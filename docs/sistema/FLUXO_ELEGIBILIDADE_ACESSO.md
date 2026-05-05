# 🔐 Fluxo de Elegibilidade e Acesso — Planos, Assinaturas e Módulos

**Versão:** v1.9.2  
**Última Atualização:** 05/05/2026  
**Público-alvo:** Desenvolvedores e IA  
**Arquivo de referência:** `configuracao/services_assinatura.py`, `configuracao/models.py`, `core/decorators.py`, `core/context_status_plano.py`

---

## TL;DR — Mapa de consulta em 30 segundos

```
PERGUNTA: "Este ministério pode usar o sistema?"
→ assinatura_esta_regular(assinatura, ministerio)

PERGUNTA: "Qual plano está em vigor?"
→ obter_plano_efetivo_ministerio(ministerio)
   └─ 1º: LiberacaoPlanoMinisterio (BETA/pilot) ← maior prioridade
   └─ 2º: AssinaturaMinisterio.plano (plano contratado)
   └─ 3º: Plano.codigo_plano='pioneiro' (fallback)

PERGUNTA: "O ministério pode usar este módulo?"
→ ministerio_pode_usar_modulo(ministerio, 'financeiro')
   └─ depende de: obter_plano_efetivo_ministerio() → plano.permite_modulo_*
```

---

## 1. Os 4 Componentes de Acesso

Existem **quatro camadas independentes** que juntas determinam o acesso de um ministério:

| # | Componente | Controla | Onde vive |
|---|------------|----------|-----------|
| 1 | **Elegibilidade Gratuita** | Se o ministério pode operar sem pagar | `Ministerio.verificar_elegibilidade_plano_gratuito()` |
| 2 | **Status da Assinatura** | Se o ministério está mensalidade em dia | `AssinaturaMinisterio.status` |
| 3 | **Períodos Especiais** | Cortesia, Trial, Graça por inadimplência | `AssinaturaMinisterio.*_ativo / data_*` |
| 4 | **Plano Efetivo (incl. BETA)** | Quais limites e módulos estão disponíveis | `LiberacaoPlanoMinisterio` + `AssinaturaMinisterio.plano` |

Esses componentes são **consultados em ordem de prioridade** pelas funções centrais. Veja o fluxo completo abaixo.

---

## 2. Fluxo Completo: `assinatura_esta_regular()`

Esta é a **função mais crítica do sistema**. Retorna `True` se o ministério pode acessar o sistema.

```
assinatura_esta_regular(assinatura, ministerio)
│
├─ assinatura is None?
│   └─ SIM → verificar_elegibilidade_plano_gratuito()
│              ├─ conta membros totais de todas as igrejas (status qualquer — BUG POTENCIAL, ver seção 6)
│              ├─ busca Plano.codigo_plano='pioneiro' para saber o limite
│              └─ retorna True se membros <= limite (ou limite == 0)
│
├─ trial_ativo=True AND is_trial_ativo() == False?
│   └─ Trial expirado → retorna FALSE (bloqueia acesso)
│
├─ is_trial_ativo() == True?
│   └─ Trial em vigor → retorna TRUE ✅
│
├─ status in {'ativa', 'gratuita'}?
│   └─ Assinatura regular → retorna TRUE ✅
│
├─ is_periodo_cortesia_valido() == True?
│   └─ Cortesia ativa e dentro de 3 dias → retorna TRUE ✅
│
├─ status == 'vencida' AND verificar_elegibilidade_plano_gratuito() == True?
│   └─ Assinatura vencida mas dentro dos limites gratuitos → retorna TRUE ✅
│
└─ Nenhuma condição atendida → retorna FALSE ❌
```

**Atenção:** O status `'pendente_pagamento'` (inadimplência com grace period) **não aparece** nesta função. O acesso durante o grace period é controlado separadamente em `assinatura_em_graca_inadimplencia()`. Isso significa que, durante a inadimplência, `assinatura_esta_regular()` pode retornar `False`, mas o decorator `verificar_assinatura_valida` NÃO verifica o grace period — existe uma inconsistência aqui (ver seção 6).

---

## 3. Fluxo Completo: `obter_plano_efetivo_ministerio()`

Determina **qual plano está em vigor** para fins de limites e módulos.

```
obter_plano_efetivo_ministerio(ministerio)
│
├─ [1º] LiberacaoPlanoMinisterio.filter(ministerio, ativo=True, pode_visualizar=True)
│         .order_by('-data_atualizacao', '-id').first()
│   ├─ Existe E plano.ativo == True?
│   └─ SIM → retorna este plano (BETA/pilot override)
│
├─ [2º] AssinaturaMinisterio.plano
│   ├─ Existe (não-null)?
│   └─ SIM → retorna plano da assinatura
│
└─ [3º] Plano.objects.filter(codigo_plano='pioneiro', ativo=True).first()
         └─ Fallback: sempre retorna Pioneiro (se existir no banco)
```

**Regra de ouro:** `LiberacaoPlanoMinisterio` **sempre sobrepõe** o plano contratado. Um ministério no plano Pioneiro com uma `LiberacaoPlanoMinisterio` ativa para o plano Rede operará **como se fosse o plano Rede** (limites e módulos).

---

## 4. Detalhamento de Cada Componente

### 4.1 Elegibilidade Gratuita (Plano Pioneiro — Grátis)

**Função:** `Ministerio.verificar_elegibilidade_plano_gratuito()`

**O que faz:**
- Conta o total de membros de todas as igrejas do ministério (via `igreja.membros.count()`)
- Busca o limite do plano com `codigo_plano='pioneiro'`
- Retorna `True` se `membros <= limite` ou `limite == 0`

**Quando é usado:**
1. Quando `assinatura is None` — ministério nunca teve assinatura
2. Quando `status == 'vencida'` — como "válvula de escape" para não bloquear ministérios pequenos

**Atenção crítica:** Esta função conta **todos os membros** (qualquer status), usando `igreja.membros.count()`. Já a função `contar_pessoas_ativas()` do service conta apenas `status='Ativo'`. Há inconsistência: o plano é limitado por "pessoas ativas" mas a elegibilidade gratuita verifica todos os membros.

---

### 4.2 Status da Assinatura

**Model:** `AssinaturaMinisterio.status`

| Status | Significado | `assinatura_esta_regular()` |
|--------|-------------|----------------------------|
| `'ativa'` | Paga e em dia (via Stripe) | ✅ TRUE |
| `'gratuita'` | Plano gratuito ou trial/cortesia ativo | ✅ TRUE |
| `'pendente_pagamento'` | Pagamento falhou, em grace period | ⚠️ FALSE (mas grace period pode liberar) |
| `'vencida'` | Expirada sem renovação | ⚠️ FALSE (salvo se elegível grátis) |
| `'cancelada'` | Cancelada pelo cliente ou sistema | ❌ FALSE |

**Como o status muda:**
```
Stripe webhook → invoice.payment_succeeded → 'ativa'
Stripe webhook → customer.subscription.deleted → 'cancelada'
Stripe webhook → invoice.payment_failed → 'pendente_pagamento' + define data_fim_graca_inadimplencia
Grace period expirou → view gerenciar_assinatura → downgrade para 'pioneiro' + status 'gratuita'
Trial iniciado → iniciar_trial() → status 'gratuita' + trial_ativo=True
Cortesia ativada → status 'gratuita' + periodo_cortesia_ativo=True
```

---

### 4.3 Período de Cortesia

**Fields em `AssinaturaMinisterio`:**
- `periodo_cortesia_ativo` (BooleanField)
- `data_inicio_cortesia` (DateTimeField)
- Duração: **3 dias** (hardcoded em `is_periodo_cortesia_valido()`)

**Verificação:**
```python
def is_periodo_cortesia_valido(self):
    if self.periodo_cortesia_ativo and self.data_inicio_cortesia:
        data_fim_cortesia = self.data_inicio_cortesia + timedelta(days=3)
        return timezone.now() < data_fim_cortesia
    return False
```

**Quando é ativada:**
- Manualmente pelo admin do sistema via painel admin
- Ou pelo botão "Ativar Cortesia" na página de assinatura (view `gerenciar_assinatura`)
- Destinada a ministérios recém-criados para conhecer o sistema

**Observação:** A cortesia dura 3 dias fixos. Após expirar, `is_periodo_cortesia_valido()` retorna `False` automaticamente (sem necessidade de campo de expiração separado — calcula na hora).

**Registro no histórico:** Quando cortesia é ativada, deve-se criar um `HistoricoAssinatura(tipo='cortesia')`. Verificar se isso está implementado na view (a função de trial foi corrigida para registrar, mas a de cortesia pode não estar).

---

### 4.4 Período de Trial (Teste Grátis)

**Fields em `AssinaturaMinisterio`:**
- `trial_ativo` (BooleanField)
- `data_inicio_trial` (DateTimeField)
- `dias_trial_totais` (IntegerField, padrão: **14 dias**)

**Verificação:**
```python
def is_trial_ativo(assinatura):
    if not assinatura or not assinatura.trial_ativo:
        return False
    dias_totais = assinatura.dias_trial_totais or 14
    data_fim_trial = assinatura.data_inicio_trial + timedelta(days=dias_totais)
    return timezone.now() < data_fim_trial
```

**Comportamento especial:** Se `trial_ativo=True` mas o trial já expirou, `assinatura_esta_regular()` retorna **FALSE** explicitamente (linha `if assinatura.trial_ativo and not is_trial_ativo(assinatura): return False`). Isso evita que um trial expirado passe pelas verificações seguintes.

**Registro no histórico:** `iniciar_trial()` cria um `HistoricoAssinatura(tipo='trial')`. ✅ Implementado.

---

### 4.5 Graça por Inadimplência

**Fields em `AssinaturaMinisterio`:**
- `status = 'pendente_pagamento'`
- `data_fim_graca_inadimplencia` (DateTimeField)
- `tentativas_falha_pagamento` (IntegerField)

**Verificação:**
```python
def assinatura_em_graca_inadimplencia(assinatura):
    if not assinatura or assinatura.status != 'pendente_pagamento':
        return False
    return timezone.now() < assinatura.data_fim_graca_inadimplencia
```

**Fluxo:**
1. Stripe envia `invoice.payment_failed`
2. Webhook incrementa `tentativas_falha_pagamento`, define `data_fim_graca_inadimplencia`
3. O ministry permanece com acesso durante a graça
4. Ao acessar `gerenciar_assinatura`, se graça expirou → downgrade automático para Pioneiro

**Atenção:** O decorator `verificar_assinatura_valida` em `core/decorators.py` **não verifica** `assinatura_em_graca_inadimplencia()`. Ele chama apenas `assinatura_esta_regular()` que retorna `False` para `pendente_pagamento`. Isso significa que durante o grace period o decorator pode bloquear indevidamente — inconsistência (ver seção 6).

---

### 4.6 Liberação BETA / Pilot (`LiberacaoPlanoMinisterio`)

**Model:** `LiberacaoPlanoMinisterio`

| Campo | Função |
|-------|--------|
| `ministerio` (FK) | Qual ministério recebe a liberação |
| `plano` (FK) | Qual plano está sendo liberado |
| `ativo` | Se a liberação está em vigor |
| `pode_visualizar` | Plano aparece nos seletores para este ministério |
| `pode_contratar` | Ministério pode fazer checkout deste plano |
| `acesso_beta` | Flag para context processors (suprime alertas de irregularidade) |

**Como funciona:**
- É criada manualmente pelo desenvolvedor/admin via Django Admin
- Permite que ministérios específicos acessem planos ainda não liberados publicamente
- Sobrepõe completamente o plano da assinatura para fins de limites e módulos
- O campo `acesso_beta=True` é verificado em `context_status_plano.py` para **suprimir alertas de irregularidade** no banner do sistema

**Exemplo prático:**
- Ministério X está no plano Pioneiro (100 pessoas)
- Admin cria `LiberacaoPlanoMinisterio(ministerio=X, plano=Crescimento, ativo=True, pode_visualizar=True, acesso_beta=True)`
- `obter_plano_efetivo_ministerio(X)` retorna **Crescimento** (250 pessoas)
- Limites e módulos do Crescimento se aplicam, mesmo sem pagar pelo Crescimento

---

### 4.7 Módulos Ativos por Plano

Os módulos são **flags no model `Plano`**, globais para todos os ministérios que contrataram aquele plano:

| Campo no Plano | Módulo |
|----------------|--------|
| `permite_modulo_secretaria` | Secretaria |
| `permite_modulo_agenda` | Agenda |
| `permite_modulo_eventos` | Eventos |
| `permite_modulo_escola_biblica` | Escola Bíblica |
| `permite_modulo_financeiro` | Financeiro |
| `permite_modulo_comunicacao` | Comunicação em massa |
| `permite_suporte_tickets` | Suporte via tickets |
| `suporte_prioritario` | Suporte prioritário |

**Verificação:**
```python
ministerio_pode_usar_modulo(ministerio, 'financeiro')
# → obter_plano_efetivo_ministerio(ministerio)
# → getattr(plano, 'permite_modulo_financeiro', True)
```

**Importante:** Módulos são verificados **por plano**, não por ministério individualmente. Não existe uma tabela de override de módulo por ministério (exceto via `LiberacaoPlanoMinisterio` que troca o plano inteiro).

**Para override individual de módulo por ministério**: atualmente não existe. A única forma de dar acesso diferenciado a um ministério é via `LiberacaoPlanoMinisterio` apontando para um plano com os módulos desejados.

---

## 5. Diagrama Completo de Prioridades

```
REQUEST do usuário logado
│
├─ [A] Usuário é superusuário?
│   └─ SIM → Acesso total, sem verificações ✅
│
├─ [B] Ministério está ativo? (Ministerio.ativo)
│   └─ NÃO → PermissionDenied (get_ministerio_or_error lança erro)
│
├─ [C] LiberacaoPlanoMinisterio ativo + acesso_beta?
│   └─ SIM → Suprime alertas de irregularidade no banner (não bypassa o acesso)
│
├─ [D] assinatura_esta_regular()?
│   ├─ SIM → Acesso permitido ✅
│   └─ NÃO → Redirect para gerenciar_assinatura (decorator verificar_assinatura_valida)
│
└─ [E] Qual é o plano efetivo? (para limites e módulos)
    ├─ 1º: LiberacaoPlanoMinisterio ativo → plano BETA
    ├─ 2º: AssinaturaMinisterio.plano → plano contratado
    └─ 3º: Plano.codigo_plano='pioneiro' → fallback
```

**Ordem de avaliação dentro de `assinatura_esta_regular()`:**
```
1. assinatura is None → elegibilidade gratuita
2. trial expirado → BLOQUEIA
3. trial ativo → LIBERA
4. status 'ativa' ou 'gratuita' → LIBERA
5. período de cortesia válido → LIBERA
6. status 'vencida' + elegível grátis → LIBERA
7. qualquer outro → BLOQUEIA
```

---

## 6. Inconsistências e Problemas Identificados

### 6.1 ⚠️ Grace period não está conectado ao decorator de acesso

**Problema:** O decorator `verificar_assinatura_valida` (em `core/decorators.py`) chama apenas `assinatura_esta_regular()`, que retorna `False` para `status='pendente_pagamento'`. Portanto, um ministério em grace period por inadimplência **é bloqueado pelo decorator**, mesmo tendo dias de graça.

**Onde funciona corretamente:** `context_status_plano.py` verifica `assinatura_em_graca_inadimplencia()` e exibe o banner de aviso em vez de bloquear.

**Solução sugerida:** Adicionar verificação de grace period em `assinatura_esta_regular()`:
```python
# Adicionar antes do último return False:
if assinatura_em_graca_inadimplencia(assinatura):
    return True
```

---

### 6.2 ⚠️ `verificar_elegibilidade_plano_gratuito()` conta membros errados

**Problema:** A função usa `igreja.membros.count()` (todos os membros, qualquer status), enquanto os limites do plano são baseados em "pessoas ativas" (`contar_pessoas_ativas()` que filtra `status='Ativo'`).

**Impacto:** Um ministério com 120 membros (60 ativos) é considerado "fora do limite do Pioneiro (100)" mesmo tendo apenas 60 ativas, bloqueando o acesso quando a assinatura vence.

**Solução sugerida:** Substituir em `verificar_elegibilidade_plano_gratuito()`:
```python
# ATUAL:
total_membros += igreja.membros.count()

# CORRETO:
from secretaria.models import Membro
total_membros = Membro.objects.filter(
    igreja__ministerio=self,
    status_pessoa__nome__iexact='Ativo',
).count()
```

---

### 6.3 ⚠️ Cortesia não registra no HistoricoAssinatura

**Problema:** A função `iniciar_trial()` foi corrigida para criar registro em `HistoricoAssinatura(tipo='trial')`. Mas a ativação da cortesia (na view `gerenciar_assinatura`) provavelmente não cria um registro `tipo='cortesia'`.

**Como verificar:**
```python
# Na view gerenciar_assinatura, buscar o trecho que ativa cortesia:
# Deve existir algo como:
assinatura.periodo_cortesia_ativo = True
assinatura.data_inicio_cortesia = timezone.now()
# E verificar se logo após existe:
HistoricoAssinatura.objects.create(tipo='cortesia', ...)
```

---

### 6.4 ℹ️ `LiberacaoPlanoMinisterio` sobrepõe plano mas NÃO bypassa `assinatura_esta_regular()`

**Comportamento atual:** Se um ministério tem `LiberacaoPlanoMinisterio` ativo mas a assinatura está `'cancelada'`, o acesso é bloqueado (porque `assinatura_esta_regular()` retorna `False`). O campo `acesso_beta=True` apenas suprime o **banner de alerta** no template — não libera acesso.

**Isso pode ser intencional ou não.** Se a intenção do BETA é dar acesso irrestrito independente do status da assinatura, a função `assinatura_esta_regular()` precisaria verificar liberações beta:
```python
# Possível correção (se for intenção liberar acesso beta):
def assinatura_esta_regular(assinatura, ministerio):
    from configuracao.models import LiberacaoPlanoMinisterio
    if LiberacaoPlanoMinisterio.objects.filter(
        ministerio=ministerio, ativo=True, acesso_beta=True
    ).exists():
        return True
    # ... resto da lógica atual
```

---

### 6.5 ℹ️ Módulos não têm override por ministério

Atualmente não é possível dar acesso ao módulo de Comunicação só para um ministério sem que todos no mesmo plano tenham. O único mecanismo é criar um plano separado e usar `LiberacaoPlanoMinisterio`.

---

## 7. Onde cada verificação ocorre no código

| Ponto de verificação | Arquivo | Linha | O que verifica |
|---------------------|---------|-------|----------------|
| Decorator de proteção de views | `core/decorators.py` | ~20 | `assinatura_esta_regular()` → bloqueia acesso |
| Context processor global | `core/context_status_plano.py` | ~14 | Status completo → exibe banners no template |
| `get_ministerio_or_error()` | `core/utils.py` | ~126 | Envia notificação interna se irregular |
| View `gerenciar_assinatura` | `configuracao/views.py` | ~785 | Downgrade automático ao expirar grace period |
| Criação de pessoa ativa | `services_assinatura.py` | ~350 | `ministerio_pode_adicionar_pessoa_ativa()` |
| Criação de igreja | `services_assinatura.py` | ~364 | `ministerio_pode_criar_igreja()` |
| Cards de plano (template) | `gerenciar_assinatura.html` | ~430 | `item.excede_algum` → desabilita botões |

---

## 8. Fluxo Visual por Cenário

### Cenário A: Ministério novo, sem assinatura
```
assinatura is None
→ verificar_elegibilidade_plano_gratuito()
  → membros <= limite_pioneiro? → SIM → ACESSO ✅ (status: gratuita implícita)
  → membros > limite? → NÃO → BLOQUEIA → gerenciar_assinatura
plano_efetivo = Pioneiro (fallback)
módulos = conforme flags do Pioneiro
```

### Cenário B: Assinatura ativa, plano Crescimento
```
assinatura.status = 'ativa'
→ ACESSO ✅
plano_efetivo = Crescimento (da AssinaturaMinisterio.plano)
módulos = conforme flags do Crescimento
```

### Cenário C: Ministério em trial de 14 dias
```
assinatura.trial_ativo = True, data_inicio_trial = hoje-5dias
→ is_trial_ativo() = True (ainda tem 9 dias)
→ ACESSO ✅
plano_efetivo = plano da assinatura (ou pioneiro se null)
módulos = conforme o plano efetivo
```

### Cenário D: Plano vencido, ministério pequeno (elegível grátis)
```
assinatura.status = 'vencida'
→ verificar_elegibilidade_plano_gratuito() = True (30 membros, limite=100)
→ ACESSO ✅ (com restrições do Pioneiro)
plano_efetivo = Pioneiro (fallback)
```

### Cenário E: Plano vencido, ministério grande (não elegível grátis)
```
assinatura.status = 'vencida'
→ verificar_elegibilidade_plano_gratuito() = False (150 membros, limite=100)
→ BLOQUEIA ❌ → redirect gerenciar_assinatura
```

### Cenário F: Ministério com LiberacaoPlanoMinisterio (BETA)
```
assinatura.status = 'gratuita', plano = Pioneiro
LiberacaoPlanoMinisterio(ativo=True, pode_visualizar=True, plano=Ministerio)
→ assinatura.status='gratuita' → ACESSO ✅
plano_efetivo = Ministério (por LiberacaoPlanoMinisterio — prioridade máxima)
módulos = conforme flags do plano Ministério
banner de irregularidade = SUPRIMIDO (acesso_beta=True)
```

### Cenário G: Assinatura pendente_pagamento (dentro do grace period)
```
assinatura.status = 'pendente_pagamento'
data_fim_graca_inadimplencia = hoje+5dias
→ assinatura_esta_regular() = FALSE ← BUG: não verifica grace period
→ decorator verificar_assinatura_valida → BLOQUEIA ❌ (BUG!)
→ context_status_plano.py → exibe banner de aviso (funciona corretamente)
```

> **⚠️ O cenário G está com bug:** ver seção 6.1

---

## 9. Resumo de Responsabilidades

| Função/Classe | Responsabilidade única |
|---------------|----------------------|
| `assinatura_esta_regular()` | Porta de entrada: acessa ou não? |
| `obter_plano_efetivo_ministerio()` | Qual plano usar para limites e módulos? |
| `ministerio_pode_usar_modulo()` | Este módulo está incluso no plano? |
| `contar_pessoas_ativas()` | Contagem oficial de pessoas ativas |
| `ministerio_pode_adicionar_pessoa_ativa()` | Validação antes de ativar uma pessoa |
| `ministerio_pode_criar_igreja()` | Validação antes de criar uma igreja |
| `verificar_assinatura_valida` (decorator) | Bloqueia views se acesso inválido |
| `status_plano_unificado` (context processor) | Exibe banners de alerta sem bloquear |
| `LiberacaoPlanoMinisterio` | Override manual de plano por ministério (BETA/pilot) |
| `Ministerio.verificar_elegibilidade_plano_gratuito()` | Válvula de escape para plano gratuito |

---

## 10. Checklist de Correções Prioritárias

- [ ] **P1 — CRÍTICO:** Adicionar `assinatura_em_graca_inadimplencia()` em `assinatura_esta_regular()` para não bloquear ministérios em grace period (ver 6.1)
- [ ] **P2 — MÉDIO:** Corrigir `verificar_elegibilidade_plano_gratuito()` para usar `contar_pessoas_ativas()` em vez de `membros.count()` (ver 6.2)
- [ ] **P3 — BAIXO:** Verificar se ativação de cortesia cria registro em `HistoricoAssinatura` (ver 6.3)
- [ ] **P4 — DECISÃO:** Definir se `LiberacaoPlanoMinisterio(acesso_beta=True)` deve bypassar `assinatura_esta_regular()` (ver 6.4)
