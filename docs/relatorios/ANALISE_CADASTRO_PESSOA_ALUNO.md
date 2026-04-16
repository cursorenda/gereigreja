# ANÁLISE: Cadastro de Pessoa (Secretaria) vs. Cadastro de Aluno (EBD)

**Data**: 13/04/2026  
**Escopo**: Apps `secretaria` e `escola_biblica`  
**Objetivo**: Identificar oportunidades de consolidação e melhorias no modelo de dados

---

## 1. ESTRUTURA ATUAL

### 1.1 App SECRETARIA - Modelo `Pessoa` (com proxy `Membro`)

**Localização**: `secretaria/models.py` (linhas ~90-290)

**Campos de dados pessoais**:
- `nome` (CharField, max_length=100) ⭐ #1 **CRÍTICO**
- `apelido` (CharField)
- `cpf` (CharField, unique)
- `rg` (CharField)
- `nascimento` (DateField) ⭐ #2 **CRÍTICO**
- `genero` (CharField, choices)
- `estado_civil` (CharField, choices)
- `profissao` (CharField)
- `escolaridade` (CharField, choices)
- `nome_pai`, `nome_mae` (CharField)

**Dados de localização/contato**:
- `telefone`, `celular` (CharField)
- `email` (EmailField)
- `cep`, `pais`, `estado`, `cidade`, `bairro_distrito`, `rua`, `numero_casa`, `complemento` (CharField)
- `grupo_casa` (ForeignKey para `GrupoCasa`) ⭐ **Vincula múltiplas pessoas ao mesmo endereço**

**Dados de acompanhamento pastoral**:
- `data_primeira_visita`, `origem_visita`, `status_acompanhamento` (CharField, choices)
- `responsavel_acompanhamento` (ForeignKey para User)
- `observacoes_visita` (TextField)

**Dados de filiação eclesial**:
- `tipo_pessoa` (ForeignKey para `TipoPessoa`: Membro, Visitante, Obreiro, etc.) ⭐ **STATUS ECLESIÁSTICO**
- `status_pessoa` (ForeignKey para `StatusPessoa`: Ativo, Inativo, Falecido, etc.) ⭐ **STATUS ECLESIAL DETALHADO**
- `tipo_entrada` (CharField, choices: Batismo, Aclamação, Carta, Outro)
- `sub_status_inativo` (CharField: Falecido, Mudou, Transferido)
- `data_entrada` (DateField)

**Relacionamentos**:
- `usuario` (OneToOne para Django User, optional) - Para acesso ao sistema
- `tags` (ManyToMany para `Tag`) - Para segmentação flexível
- `grupos_casa` (ForeignKey para `GrupoCasa`)
- `foto` (ImageField)

**Auditoria**:
- `criado_em`, `atualizado_em` (DateTimeField, auto_now_add/auto_now) ✅ **RASTREAMENTO COMPLETO**

**Total de campos**: ~45 (muito rico semanticamente)

---

### 1.2 App ESCOLA_BIBLICA - Modelo `CadastroAluno` (novo, criado na migration 0021)

**Localização**: `escola_biblica/models.py` (linhas ~151-189)

**Campos de dados pessoais**:
- `nome` (CharField, max_length=150) ⭐ **DUPLICADO COM PESSOA**
- `data_nascimento` (DateField, null=True) ⭐ **DUPLICADO COM PESSOA**

**Dados de responsável**:
- `responsavel` (CharField, max_length=150) ⭐ **DUPLICADO**
- `telefone_responsavel` (CharField, max_length=20) ⭐ **DUPLICADO**

**Adicionais**:
- `observacoes` (TextField)
- `ativo` (BooleanField)
- `igreja` (ForeignKey para Chiesa) - ⭐ **CONTEXT CRÍTICO**

**Auditoria**:
- `created_at`, `updated_at` (DateTimeField, auto_now_add/auto_now) ✅

**Total de campos**: 10 (minimalista, proposital para EBD)

**Índices**:
```
(igreja, nome) - para buscas rápidas por nome
(ativo) - para filtros de alunos ativos
```

---

### 1.3 App ESCOLA_BIBLICA - Modelo `Aluno` (matrícula)

**Localização**: `escola_biblica/models.py` (linhas ~191+)

**Propósito**: Representa uma matrícula de um aluno em uma turma específica em um ano letivo

**Campos**:
- `cadastro` (ForeignKey para `CadastroAluno`) ⭐ **NOVO, ADICIONADO NA MIGRATION 0021**
- `nome`, `data_nascimento` (CharField/DateField) ⭐ **DENORMALIZADO DE CADASTROA ALUNO**
- `turma` (ForeignKey para `Turma`)
- `responsavel`, `telefone_responsavel` (CharField)
- `observacoes` (TextField)
- `ativo` (BooleanField)

**Auditoria**: `created_at`, `updated_at`

---

## 2. ANÁLISE: PROBLEMAS IDENTIFICADOS

### 2.1 ❌ DUPLICAÇÃO DE DADOS (Redundância)

| Campo | Pessoa | CadastroAluno | Aluno | Impacto |
|-------|--------|---------------|-------|--------|
| `nome` | ✅ | ✅ | ✅ | 🔴 **3x o mesmo dado** |
| `data_nascimento` | ✅ | ✅ | ✅ | 🔴 **3x o mesmo dado** |
| `responsavel` | ❌ | ✅ | ✅ | 🟡 **2x o mesmo dado** |
| `telefone_responsavel` | ❌ | ✅ | ✅ | 🟡 **2x o mesmo dado** |
| `email` | ✅ | ❌ | ❌ | Falta em EBD |
| `endereço completo` | ✅ | ❌ | ❌ | Falta em EBD |
| `foto` | ✅ | ❌ | ❌ | Falta em EBD |

**Consequências**:
- ❌ Inconsistência: Alguém atualiza nome em Pessoa mas não em CadastroAluno
- ❌ Sincronização manual: Código em `Aluno.save()` tenta sincronizar nome/data/responsável
- ❌ Complexidade de manutenção: Múltiplos pontos de verdade
- ❌ Overhead de storage: Dados replicados 2-3x

### 2.2 ❌ FALTA DE RELAÇÃO PESSOA ↔ CADASTROALUNO

**Situação atual**:
```
Pessoa (Secretaria)          CadastroAluno (EBD)
  ├─ Membro da Igreja           ├─ Aluno da Igreja
  ├─ Pode ter Tipo/Status       ├─ SEM Tipo/Status
  └─ Tem contato completo       └─ Tem APENAS responsável
  
  ❌ NÃO HÁ FK/RELAÇÃO ENTRE OS DOIS
```

**Consequências**:
- ❌ Um aluno da EBD pode estar em Secretaria (como Pessoa) mas o sistema não sabe disso
- ❌ Não posso saber "quais alunos de EBD também estão cadastrados em Secretaria"
- ❌ Não posso fazer relatórios cruzados (ex: alunos que são também membros da Igreja)
- ❌ Lógica de auto-matching em `Aluno.save()` é aproximada (nome + nascimento)

**Exemplo de cenário problemático**:
```
Sistema detecta:
  - Pessoa João Silva (nascido 01/01/2010) em Secretaria
  - CadastroAluno "João Silva" (nascido 01/01/2010) em EBD
  - Aluno "João Silva" matriculado em Turma X

Mas: Sistema NÃO sabe que é a mesma pessoa!
Resultado: Dados inconsistentes, múltiplas versões de "verdade"
```

### 2.3 ❌ CAMPOS CRÍTICOS DE SECRETARIA FALTAM EM EBD

| Campo | Necessário em EBD? | Mitigação Atual |
|-------|-------------------|-----------------|
| `email` | ✅ SIM (comunicações) | ❌ Manual |
| Endereço completo | ✅ SIM (visitas) | ❌ Manual + grupo_casa |
| `tipo_pessoa` | ✅ SIM (controle) | ❌ Nenhuma |
| `status_pessoa` | ✅ SIM (ativo/inativo) | ⚠️ Campo `ativo` separado |
| `foto` | 🈵 NICE-TO-HAVE | ❌ Nenhuma |
| `cpf` | 🈵 REGISTROS | ❌ Nenhuma |
| Responsável de acompanhamento | ✅ SIM (pastoral) | ❌ Nenhuma |

**Impacto prático**:
- Views de EBD precisam fazer joins complexos para acessar estas informações
- Relatórios precisam de lógica manual para cruzar dados
- Fluxos de comunicação/notificação não conseguem acessar email direto

### 2.4 ❌ CAMPOS ESPECÍFICOS DE EBD FALTAM EM SECRETARIA

| Campo | Localização | Necessário em Secretaria? |
|-------|-------------|--------------------------|
| `turma` (matrícula) | `Aluno` | 🈵 NICE-TO-HAVE (saber em qual turma é aluno) |
| `período letivo` | Implícito em Turma | ✅ SIM (história de matrículas por ano) |
| `história de matrículas` | `Aluno` (multiple rows) | ✅ SIM (fidelização) |

**Impacto**:
- Secretaria não sabe diretamente qual aluno está em qual turma de EBD
- Relatórios de fidelização incompletos

### 2.5 ❌ SINCRONIZAÇÃO PROBLEMÁTICA

**Código atual em `Aluno.save()` (migration 0021)**:
```python
def save(self, *args, **kwargs):
    if not self.cadastro_id:
        cadastro = self._obter_ou_criar_cadastro()  # ← LÓGICA APROXIMADA
        if cadastro is not None:
            self.cadastro = cadastro
    super().save(*args, **kwargs)
    self._sincronizar_cadastro()  # ← SINCRONIZAÇÃO MANUAL
```

**Problemas**:
- ❌ Se alguém muda `Pessoa.nome`, não atualiza CadastroAluno.nome automaticamente (sincronização uni-direcional)
- ❌ Se alguém muda `CadastroAluno.responsavel`, não atualiza `Pessoa` (pois não há FK)
- ❌ Lógica de matching por (nome, nascimento) é frágil (pode não encontrar em caso de de variação de nome)
- ❌ Sem teste de integração entre Pessoa ↔ CadastroAluno

### 2.6 ⚠️ NÃO HÁ AUDITORIA COMPLETA EM EBD

| Aspecto | Secretaria.Pessoa | EBD.CadastroAluno |
|--------|-------------------|-------------------|
| Criado em | ✅ auto_now_add | ✅ auto_now_add |
| Atualizado em | ✅ auto_now | ✅ auto_now |
| Criado por (User) | ❌ | ❌ |
| Atualizado por (User) | ❌ (mas tem `registrado_por` em StatusHistórico) | ❌ |
| Histórico de mudanças | ✅ StatusHistórico | ❌ |

**Impacto**:
- ❌ Em EBD, não sabemos quem criou ou modificou um aluno
- ❌ Sem log de mudanças de endereço/responsável
- ❌ Difícil rastreamento de dados para auditoria

---

## 3. MAPA CONCEITUAL ATUAL (VS. IDEAL)

### Atual (Fragmentado)
```
┌─────────────────────────────────────────┐
│          App SECRETARIA                 │
├─────────────────────────────────────────┤
│  Pessoa (Master de dados pessoais)      │
│  ├─ nome, nascimento                    │ ← INFORMAÇÃO Master
│  ├─ contato completo (email, tel, end) │ ← INFORMAÇÃO ÚNICA
│  ├─ tipo/status eclesiástico            │ ← INFORMAÇÃO ÚNICA
│  ├─ foto, cpf, rg                       │ ← INFORMAÇÃO ÚNICA
│  └─ tags, grupo_casa, acompanhador      │ ← INFORMAÇÃO ÚNICA
└─────────────────────────────────────────┘
                    ❌ NÃO HÁ RELAÇÃO
                         DIRETA
┌─────────────────────────────────────────┐
│         App ESCOLA_BIBLICA              │
├─────────────────────────────────────────┤
│  CadastroAluno (Master de alunos EBD)   │
│  ├─ nome, nascimento ⭐ DUPLICADO       │
│  ├─ responsável ⭐ DUPLICADO             │
│  ├─ telefone_responsável ⭐ DUPLICADO   │
│  └─ observacões, ativo                  │ ← UNICO EM EBD
│                                         │
│  Aluno (Matrícula)                      │
│  ├─ cadastro → CadastroAluno            │
│  ├─ turma, ano_letivo                   │ ← UNICO EM EBD
│  └─ frequência, avaliações              │ ← UNICO EM EBD
└─────────────────────────────────────────┘
```

### Ideal (Consolidado - Proposta)
```
┌──────────────────────────────────────────────────┐
│         UNIFIED PERSON REGISTRY                  │
├──────────────────────────────────────────────────┤
│  Pessoa (Master global)                          │
│  ├─ DADOS PESSOAIS (nome, nascimento, cpf, rg)  │
│  ├─ CONTATO (email, tel, celular, endereço)     │
│  ├─ ECLESIÁSTICO (tipo, status, entrada)        │
│  ├─ AUDITORIA (criado_em, atualizado_em, foto)  │
│  └─ RELACIONAMENTOS                             │
│     ├─ usuario → Django User (optional)         │
│     ├─ grupo_casa → GrupoCasa (optional)        │
│     ├─ tags → Tag (M2M)                         │
│     ├─ registros_ebd → CadastroAluno (1-to-M)  │ ← NEW!
│     └─ matrículas → Aluno (1-to-M, indirect)    │ ← NEW!
└──────────────────────────────────────────────────┘
             ✅ RELAÇÃO EXPLÍCITA (FK)

┌──────────────────────────────────────────────────┐
│      EBD ENROLLMENT SUBDOMAIN                    │
├──────────────────────────────────────────────────┤
│  CadastroAluno (EBD Registry Entry) ← LIGHT      │
│  ├─ pessoa → Pessoa (FK) ← linked to master     │
│  ├─ igreja, observacoes_ebd, ativo_ebd         │
│  └─ período_chegada, origem_ebd                │
│                                                  │
│  Aluno (Enrollment)                             │
│  ├─ cadastro → CadastroAluno                    │
│  ├─ turma, ano_letivo                           │
│  ├─ frequência, avaliações, ofertas             │
│  └─ transferências                              │
└──────────────────────────────────────────────────┘
```

---

## 4. OPÇÕES DE MELHORIA

### OPÇÃO A: Consolidação Total (❌ NÃO RECOMENDADO - Muito Disruptiva)

**Descrição**: Remover `CadastroAluno` completamente e usar `Pessoa` diretamente como master para alunos de EBD.

**Pros**:
- ✅ Elimina duplicação total
- ✅ Relatórios unificados fáceis
- ✅ Uma fonte de verdade

**Contras**:
- 🔴 **MUITO DISRUPTIVA**: Quebra toda a lógica existente de EBD
- 🔴 Nem todo aluno de EBD quer estar em Secretaria
- 🔴 Exigiria refactor de ~50+ queries EBD
- 🔴 Risco de data loss
- 🔴 Privacidade: Aluno EBD seria "Membro" na Secretaria automaticamente

**Esforço**: 🔴🔴🔴 **MUITO ALTO (2-3 sprints)**

**Status**: ❌ **REJEITADO**

---

### OPÇÃO B: Link Opcional Simples (✅ RECOMENDADO)

**Descrição**: Adicionar FK opcional `Pessoa` em `CadastroAluno` para vincular quando aplicável, mantendo EBD standalone.

**Implementação**:
```python
class CadastroAluno(models.Model):
    # ... campos existentes ...
    pessoa = models.ForeignKey(
        'secretaria.Pessoa',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registros_ebd',
        verbose_name='Pessoa (Secretaria)',
        help_text='Vinculação opcional com registro em Secretaria'
    )
    
    def sincronizar_com_pessoa(self):
        """Sincroniza dados com Pessoa se vinculada"""
        if not self.pessoa:
            return
        self.nome = self.pessoa.nome
        self.data_nascimento = self.pessoa.nascimento
        # ... outros campos
        self.save()
```

**Auto-linking melhorado**:
```python
def _tentar_vincular_pessoa(self):
    """Tenta encontrar Pessoa correspondente por matching"""
    from secretaria.models import Pessoa
    
    nome_norm = normalize_name(self.nome)
    candidates = Pessoa.objects.filter(
        igreja=self.igreja,
        status_pessoa__nome='Ativo'  # Apenas Pessoas ativas
    )
    
    # Try (nome, data_nascimento)
    if self.data_nascimento:
        match = candidates.filter(
            nome__iexact=nome_norm,
            nascimento=self.data_nascimento
        ).first()
        if match and not match.registros_ebd.exists():
            return match
    
    # Try (nome, responsável, telefone)
    if self.responsavel:
        match = candidates.filter(
            nome__iexact=nome_norm,
            nome_pai__iexact=normalize_name(self.responsavel)
        ).first()
        if match:
            return match
    
    return None

def save(self, *args, **kwargs):
    # Try to auto-link if not yet linked
    if not self.pessoa_id:
        self.pessoa = self._tentar_vincular_pessoa()
    
    # Sync from Pessoa if linked
    if self.pessoa:
        self.nome = self.pessoa.nome
        self.data_nascimento = self.pessoa.nascimento
    
    super().save(*args, **kwargs)
```

**Django Admin**:
```python
@admin.register(CadastroAluno)
class CadastroAlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pessoa', 'igreja', 'ativo')
    list_filter = ('ativo', 'igreja')
    search_fields = ('nome', 'pessoa__nome')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Vinculação', {
            'fields': ('pessoa',),
            'description': 'Se vinculado, dados de Pessoa serão usados como master'
        }),
        ('EBD Específico', {
            'fields': ('nome', 'data_nascimento', 'chiesa', 'ativo')
        }),
        # ...
    )
```

**Pros**:
- ✅ **Compatível com existente**: Sem quebra de código
- ✅ Gradual: Pode-se vincular aos poucos
- ✅ Opcional: Alunos EBD que não estão em Secretaria permanecem desvinculados
- ✅ Fecha o gap de conhecimento: "Será que este aluno está em Secretaria?"
- ✅ Permite sincronização automática de dados quando vinculado
- ✅ Reduz duplicação gradualmente

**Contras**:
- 🟡 Ainda há duplicação enquanto não vinculado
- 🟡 Lógica de matching pode ter falsos negativos
- 🟡 Manual: Usuário pode vincular errado

**Esforço**: 🟢 **BAIXO (2-3 dias)**

**Status**: ✅ **RECOMENDADO PARA PHASE 1**

---

### OPÇÃO C: Campos Complementares em CadastroAluno

**Descrição**: Adicionar campos faltantes (email, endereço, tipo, status) diretamente em `CadastroAluno` para que EBD não dependa de Secretaria.

**Adições**:
```python
class CadastroAluno(models.Model):
    # ... existentes ...
    
    # Contato (novo)
    email = models.EmailField(blank=True)
    celular = models.CharField(max_length=15, blank=True)
    
    # Endereço (novo)
    cep = models.CharField(max_length=9, blank=True)
    rua = models.CharField(max_length=100, blank=True)
    numero = models.CharField(max_length=10, blank=True)
    bairro = models.CharField(max_length=50, blank=True)
    cidade = models.CharField(max_length=50, blank=True)
    estado = models.CharField(max_length=50, blank=True)
    
    # Tipo e Status EBD (novo)
    tipo_aluno = models.ForeignKey('TipoAluno', null=True, blank=True)
    status_aluno = models.ForeignKey('StatusAluno', null=True, blank=True)
    
    # Data de entrada em EBD
    data_primeira_aula = models.DateField(null=True, blank=True)
```

**Pros**:
- ✅ EBD fica completamente autossuficiente
- ✅ Sem dependência de Secretaria

**Contras**:
- 🔴 **Piora a duplicação**: Cada pessoa fica em Secretaria E CadastroAluno
- 🔴 Sincronização ainda mais complexa
- 🔴 Dois endereços, dois emails, dois tipos = confusão
- 🔴 Difícil manutenção

**Esforço**: 🟡 **MÉDIO (1-2 dias), mas resultado ruim**

**Status**: ❌ **NÃO RECOMENDADO** (piora problema)

---

### OPÇÃO D: Auditoria Completa em EBD

**Descrição**: Adicionar rastreamento de quem criou/modificou em CadastroAluno e Aluno.

**Adições**:
```python
class CadastroAluno(models.Model):
    # ... existentes ...
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    
    def save(self, user=None, *args, **kwargs):
        if not self.pk:
            self.criado_por = user
        self.atualizado_por = user
        super().save(*args, **kwargs)
```

**Pros**:
- ✅ Rastreabilidade completa
- ✅ Segurança e conformidade

**Contras**:
- 🟡 Requer passar `user` em todo `.save()`
- 🟡 Mudanças em bulk operations

**Esforço**: 🟢 **BAIXO (1 dia)**

**Status**: ✅ **RECOMENDADO PARA PHASE 2**

---

### OPÇÃO E: Modelo Unificado de Endereço (Bonus)

**Descrição**: Ao invés de duplicar `rua, numero, bairro, cidade`, usar FK para `GrupoCasa` em CadastroAluno também.

```python
class CadastroAluno(models.Model):
    # ... existentes ...
    grupo_casa = models.ForeignKey(
        'secretaria.GrupoCasa',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='Grupo/Casa/Endereço onde reside'
    )
```

**Pros**:
- ✅ Evita triplicação de endereço
- ✅ Visitação unificada
- ✅ Integração automática com GrupoCasa

**Contras**:
- 🟡 Aluno pode ter endereço diferente do responsável

**Esforço**: 🟢 **BAIXO (1 dia)**

**Status**: ✅ **RECOMENDADO PARA PHASE 2**

---

## 5. ROADMAP RECOMENDADO

### FASE 1: Vincular Pessoa ↔ CadastroAluno (1-2 sprints)

**Priority**: 🔴 **CRÍTICO**

**Tasks**:
1. ✅ Adicionar FK `pessoa` em `CadastroAluno` (nullable)
2. ✅ Migration: `0022_cadastroaluno_pessoa`
3. ✅ Auto-linking logic em `CadastroAluno.save()`
4. ✅ Admin: Mostrar `pessoa` em CadastroAlunoAdmin
5. ✅ View: Helper para vincular manualmente ex-alunos
6. ✅ Tests: `test_cadastro_aluno_vincula_pessoa`, etc.

**Ganho imediato**:
- ✅ Descobrir alunos EBD que estão em Secretaria
- ✅ Sincronizar nome/data_nascimento de Pessoa para CadastroAluno
- ✅ Relatórios: "Alunos que são Membros da Igreja"

---

### FASE 2: Auditoria + Endereço Unificado (1 sprint)

**Priority**: 🟡 **IMPORTANTE**

**Tasks**:
1. ✅ Adicionar `criado_por`, `atualizado_por` em CadastroAluno
2. ✅ Adicionar `grupo_casa` em CadastroAluno
3. ✅ Migration: `0023_cadastroaluno_auditoria_endereco`
4. ✅ Update views para passar `user` em `.save()`
5. ✅ Views EBD: Mostrar endereço de `grupo_casa` se existir

**Ganho**:
- ✅ Auditoria completa
- ✅ Endereço unificado para visitação

---

### FASE 3: Consultas Otimizadas (1 sprint)

**Priority**: 🟠 **IMPORTANTE**

**Tasks**:
1. ✅ Audit: Revisar ~50+ queries EBD
2. ✅ Otimizar: `select_related('pessoa', 'pessoa__grupo_casa')` onde aplicável
3. ✅ Relatrórios: Novo dashboard "Saúde EBD": matrículas vinculadas vs. não vinculadas
4. ✅ Tests: Performance baselines

**Ganho**:
- ✅ Queries mais eficientes
- ✅ Visibilidade do status de vinculação

---

## 6. IMPACTO ESPERADO (Ao implementar FASE 1)

### Antes (Atual)
```
EBD totalmente isolada de Secretaria
├─ CadastroAluno e Pessoa são silos separados
├─ Impossível saber: "João em EBD = João em Secretaria?"
└─ Duplicação contínua
```

### Depois (FASE 1)
```
EBD optionalmente vinculada a Secretaria
├─ CadastroAluno.pessoa FK → Pessoa (quando aplicável)
├─ Dados sincronizam: Pessoa.nome mudança? CadastroAluno atualiza
├─ Query: "SELECT * FROM CadastroAluno WHERE pessoa_id IS NOT NULL"
│   → Saber quais alunos EBD estão também em Secretaria
└─ Relatório: Alunos sem vinculação em Secretaria
```

### Métricas
- Redução de campos duplicados: de **1000+ rows** para **5-10 pontos de sincronização**
- Novas queries possíveis: **+15 relatórios novos**
- Acurácia de "Quem é este aluno?": **100 → 95%** (matching não perfeito)

---

## 7. RECOMENDAÇÃO FINAL

### ✅ IMPLEMENTAR: OPÇÃO B (Link Opcional) + FASE 1

**Razão**:
1. **Baixo risco**: Compatível com existente
2. **Alto valor**: Conecta dois silos, abre novas possibilidades
3. **Implementável rápido**: 2-3 dias sprint
4. **Fundação para futuro**: Permite evoluir para consolidação maior later

### Timeline
- **SEMANA PRÓXIMA**: Sprint FASE 1 (Opção B)
- **2 SEMANAS**: Sprint FASE 2 (Auditoria + Endereço)
- **3 SEMANAS**: Sprint FASE 3 (Otimizações)

---

## 8. PRÓXIMOS PASSOS

1. **Aprovação**: Validar com time se abordagem faz sentido
2. **Prototipagem**: Criar migration 0022 (FK `pessoa`)
3. **Implementação**: Auto-linking logic
4. **Testing**: 20+ casos de teste
5. **Rollout**: Gradual com monitoramento

---

## ANEXO: Queries de Diagnóstico

### Descobrir alunos não vinculados (pós-FASE 1)
```sql
SELECT ca.nome, ca.data_nascimento, COUNT(a.id) as matriculas
FROM escola_biblica_cadastroaluno ca
LEFT JOIN escola_biblica_aluno a ON ca.id = a.cadastro_id
WHERE ca.pessoa_id IS NULL  -- Não vinculado a Secretaria
GROUP BY ca.id
ORDER BY matriculas DESC;
```

### Descobrir Pessoa que poderia ter CadastroAluno
```sql
SELECT p.nome, p.nascimento, COUNT(ea.id) as alunos_ebd
FROM secretaria_pessoa p
LEFT JOIN escola_biblica_cadastroaluno ca ON p.chave = ca.pessoa_id
WHERE ca.id IS NULL
  AND LOWER(p.nome) IN (
    SELECT LOWER(nome) 
    FROM escola_biblica_cadastroaluno 
    WHERE pessoa_id IS NULL
  )
GROUP BY p.chave;
```

---

**Documento preparado para decisão arquitetural**  
**Última atualização**: 13/04/2026
