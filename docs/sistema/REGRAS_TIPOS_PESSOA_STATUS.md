# 📋 Regras de Tipos de Pessoa e Status

**Data de Criação:** 10/03/2026  
**Última Atualização:** 10/03/2026  
**Versão:** 1.0

---

## 📌 Visão Geral

Este documento define as **regras de negócio** que governam as combinações válidas entre **Tipos de Pessoa** e **Status** no sistema GereIgreja.

---

## 🏛️ GRUPO 1: Corpo de Membros Oficial

### Tipos de Pessoa

| ID | Nome | Descrição |
|----|------|-----------|
| 1 | **Membro** | Pessoa oficialmente vinculada ao rol de membros da igreja |
| 3 | **Obreiro** | Membro com função de liderança ou serviço específico |

### Status Permitidos

✅ **TODOS os status são válidos:**

| ID | Status | Quando Usar |
|----|--------|-------------|
| 1 | **Ativo** | Membro participando regularmente das atividades |
| 2 | **Inativo** | Membro que parou de participar mas ainda consta no rol |
| 3 | **Em Disciplina** | Membro sob processo disciplinar eclesiástico |
| 4 | **Desligado** | Membro que foi oficialmente desligado da igreja (pedido ou disciplinar) |

#### 📝 Sub-Status de Inativo (Campo Documental)

Quando um **Membro** ou **Obreiro** está com status **Inativo**, existe um campo adicional **opcional** chamado `sub_status_inativo` para documentar o **motivo específico** da inatividade:

| Código | Sub-Status | Descrição | Exemplo de Uso |
|--------|------------|-----------|----------------|
| `FALECIDO` | **Falecido** | Membro faleceu | Manter registro histórico para estatísticas e memória da igreja |
| `MUDOU` | **Mudou (outro ministério ou denominação)** | Mudou-se para outra igreja/denominação | Ex: Membro que mudou para igreja batista |
| `TRANSFERIDO` | **Transferido (outra congregação do mesmo ministério)** | Transferido para congregação irmã | Ex: Membro transferido para sede ou regional |

**⚠️ IMPORTANTE:**
- Este campo é **APENAS para documentação, consulta futura e relatórios**
- **Não afeta** a lógica do sistema, validações ou permissões
- É **opcional** - pode-se deixar em branco se o motivo não for conhecido ou relevante
- Serve para **acompanhamento pastoral**, **estatísticas** e **planejamento estratégico**
- Útil para diferenciar "inativo temporário" de "saiu definitivamente"

**Casos de Uso Práticos:**

```
✅ Membro + Inativo + sub_status: FALECIDO
   → Membro falecido (mantém registro para estatísticas e histórico familiar)

✅ Obreiro + Inativo + sub_status: TRANSFERIDO
   → Obreiro transferido para congregação em outra cidade

✅ Membro + Inativo + sub_status: MUDOU
   → Membro que mudou para denominação Assembleia de Deus

✅ Membro + Inativo + sub_status: (vazio)
   → Membro afastado temporariamente (doença, trabalho, etc.) - sem motivo específico
```

**Relatórios Possíveis:**
- Quantos membros faleceram no ano?
- Quantos membros foram transferidos entre congregações?
- Quantos membros saíram para outras denominações?
- Taxa de retenção de membros (excluindo falecidos e transferidos)

### Justificativa

Membros e obreiros fazem parte do **rol oficial da igreja**, portanto estão sujeitos a:
- ✅ Processos disciplinares (quando houver desvio de conduta)
- ✅ Desligamento formal (pedido voluntário ou por disciplina)
- ✅ Mudanças de status conforme participação
- ✅ Direitos e deveres conforme estatuto da igreja

### Exemplos Válidos

```
✅ Membro + Ativo          → Membro participando normalmente
✅ Membro + Inativo        → Membro afastado temporariamente
✅ Membro + Em Disciplina  → Membro em processo disciplinar
✅ Membro + Desligado      → Ex-membro que saiu oficialmente
✅ Obreiro + Ativo         → Obreiro exercendo função
✅ Obreiro + Desligado     → Ex-obreiro que foi desligado
```

---

## 👥 GRUPO 2: Pessoas em Acompanhamento/Visitação

### Tipos de Pessoa

| ID | Nome | Descrição |
|----|------|-----------|
| 2 | **Novo Convertido** | Pessoa recém-convertida, em processo de integração |
| 4 | **Congregado** | Pessoa que frequenta mas ainda não é membro oficial |
| 5 | **Visitante** | Pessoa visitando a igreja ocasionalmente |

> **💡 NOTA SOBRE VISITANTE NA INTERFACE DE EVENTOS:**  
> O tipo "Visitante" **NÃO aparece** nos checkboxes de "Participantes Esperados" ao criar/editar eventos.  
> **Motivo:** Visitantes são imprevisíveis e cadastrados pela recepção no momento da chegada.  
> Não faz sentido definir "participantes esperados" para visitantes (sempre retornaria 0 pessoas).  
> Visitantes continuam existindo no sistema e podem ser cadastrados normalmente pela secretaria.

### Status Permitidos

⚠️ **APENAS 2 status são válidos:**

| ID | Status | Quando Usar |
|----|--------|-------------|
| 1 | **Ativo** | Pessoa frequentando regularmente |
| 2 | **Inativo** | Pessoa que parou de frequentar |

#### 📝 Sub-Status de Inativo (Campo Documental)

Quando uma pessoa está com status **Inativo**, existe um campo adicional **opcional** chamado `sub_status_inativo` para documentar o **motivo específico** da inatividade:

| Código | Sub-Status | Descrição |
|--------|------------|-----------|
| `FALECIDO` | **Falecido** | Pessoa faleceu |
| `MUDOU` | **Mudou (outro ministério ou denominação)** | Mudou-se para outra igreja/denominação |
| `TRANSFERIDO` | **Transferido (outra congregação do mesmo ministério)** | Transferido para outra congregação do mesmo ministério |

**⚠️ IMPORTANTE:**
- Este campo é **APENAS para documentação e consulta futura**
- **Não afeta** a lógica do sistema ou validações
- É **opcional** - pode-se deixar em branco
- Serve para **acompanhamento pastoral** e **relatórios futuros**
- Ajuda a entender **por que** a pessoa ficou inativa

**Exemplos de Uso:**
```
✅ Membro + Inativo + sub_status: FALECIDO 
   → Membro que faleceu (mantém no sistema para histórico)

✅ Congregado + Inativo + sub_status: MUDOU
   → Congregado que mudou para outra denominação

✅ Membro + Inativo + sub_status: TRANSFERIDO
   → Membro transferido para congregação irmã

✅ Visitante + Inativo + sub_status: (vazio)
   → Visitante que simplesmente parou de vir (sem especificar motivo)
```

**Quando NÃO usar:**
- ❌ Para status "Ativo", "Em Disciplina" ou "Desligado"
- ❌ Como validação de regras de negócio
- ❌ Para controlar permissões ou acessos

### Status PROIBIDOS

❌ **NÃO são válidos para este grupo:**

| ID | Status | Por que NÃO? |
|----|--------|-------------|
| 3 | **Em Disciplina** | Não fazem parte do rol oficial, logo não estão sob governo/disciplina da igreja |
| 4 | **Desligado** | Não podem ser "desligados" pois nunca foram membros oficiais |

### Justificativa

Estas pessoas **NÃO fazem parte do rol oficial** de membros, portanto:
- ❌ Não estão sob o governo eclesiástico formal
- ❌ Não podem ser disciplinadas formalmente (não assinaram compromisso de membro)
- ❌ Não podem ser "desligadas" (nunca foram oficialmente "ligadas")
- ✅ Apenas podem estar presentes (Ativo) ou ausentes (Inativo)

### Exemplos Válidos

```
✅ Congregado + Ativo         → Frequenta regularmente mas ainda não se tornou membro
✅ Congregado + Inativo       → Congregado que parou de vir
✅ Novo Convertido + Ativo    → Recém-convertido participando do discipulado
✅ Novo Convertido + Inativo  → Convertido que se afastou
✅ Visitante + Ativo          → Visitando regularmente
✅ Visitante + Inativo        → Visitou mas não voltou mais
```

### Exemplos INVÁLIDOS

```
❌ Congregado + Em Disciplina   → NÃO FAZ SENTIDO (não está sob disciplina da igreja)
❌ Congregado + Desligado       → NÃO FAZ SENTIDO (nunca foi membro para ser desligado)
❌ Visitante + Em Disciplina    → NÃO FAZ SENTIDO (visitante não está sob governo)
❌ Visitante + Desligado        → NÃO FAZ SENTIDO (visitante nunca foi membro)
❌ Novo Convertido + Desligado  → NÃO FAZ SENTIDO (ainda em integração)
```

---

## 🔄 Transições de Tipo

### Fluxo Normal de Progressão

```
Visitante (Ativo)
    ↓ (se converteu)
Novo Convertido (Ativo)
    ↓ (frequentou regularmente)
Congregado (Ativo)
    ↓ (fez curso de membros + batismo)
Membro (Ativo)
    ↓ (assumiu função de liderança)
Obreiro (Ativo)
```

### Observações Importantes

1. **Visitante → Novo Convertido:** Quando a pessoa se converte
2. **Novo Convertido → Congregado:** Quando começa a frequentar regularmente
3. **Congregado → Membro:** Quando oficialmente se torna membro (curso + batismo/profissão)
4. **Membro → Obreiro:** Quando assume função de liderança/serviço
5. **Qualquer tipo → Inativo:** Quando para de frequentar
6. **Membro/Obreiro → Em Disciplina:** Quando entra em processo disciplinar
7. **Membro/Obreiro → Desligado:** Quando é oficialmente desligado

---

## 🛡️ Validações no Sistema

### Frontend (Interface do Usuário)

**Implementado em:**
- `eventos/templates/eventos/criar_evento.html` - Sistema Híbrido de Participantes
- (Futuro) `secretaria/templates/secretaria/cadastro_membro.html`
- (Futuro) Outras telas de filtros

**Lógica:**
```javascript
// Mapeamento de tipos
const TIPOS_CORPO_MEMBROS = [1, 3];        // Membro, Obreiro
const TIPOS_ACOMPANHAMENTO = [2, 4, 5];     // Novo Convertido, Congregado, Visitante

// Status restritos (apenas para Corpo de Membros)
const STATUS_RESTRITOS = [3, 4];            // Em Disciplina, Desligado

// Regra
if (somente tipos de acompanhamento selecionados) {
    desabilitar status 3 e 4
    desmarcar se já estavam marcados
} else {
    habilitar todos os status
}
```

### Backend (Validação de Dados)

**Recomendação:** Adicionar validação no modelo `Membro` (futuro):

```python
# secretaria/models.py
class Membro(Pessoa):
    def clean(self):
        # Validar combinação tipo x status
        TIPOS_CORPO_MEMBROS = [1, 3]  # Membro, Obreiro
        STATUS_RESTRITOS = [3, 4]      # Em Disciplina, Desligado
        
        if self.tipo_pessoa_id not in TIPOS_CORPO_MEMBROS:
            if self.status_pessoa_id in STATUS_RESTRITOS:
                raise ValidationError(
                    f'{self.tipo_pessoa.nome} não pode ter status '
                    f'{self.status_pessoa.nome}. Apenas Membros e Obreiros '
                    f'podem estar em Disciplina ou Desligados.'
                )
```

---

## 📊 Auditoria de Dados Existentes

### Script para Identificar Combinações Inválidas

```python
# analise_combinacoes_invalidas.py
from secretaria.models import Membro

TIPOS_CORPO_MEMBROS = [1, 3]
STATUS_RESTRITOS = [3, 4]

invalidos = Membro.objects.exclude(
    tipo_pessoa_id__in=TIPOS_CORPO_MEMBROS
).filter(
    status_pessoa_id__in=STATUS_RESTRITOS
)

if invalidos.exists():
    print(f"⚠️  Encontradas {invalidos.count()} combinações inválidas:")
    for membro in invalidos:
        print(f"  - {membro.nome}: {membro.tipo_pessoa.nome} + {membro.status_pessoa.nome}")
else:
    print("✅ Nenhuma combinação inválida encontrada!")
```

---

## 🎯 Casos de Uso

### Cenário 1: Criando Evento para Membros em Dia

**Seleção:**
- Tipos: Membro, Obreiro
- Status: Ativo

**Resultado:** Lista todos os membros e obreiros ativos (em dia com a igreja)

---

### Cenário 2: Evento de Visitação/Integração

**Seleção:**
- Tipos: Visitante, Novo Convertido, Congregado
- Status: Ativo

**Resultado:** Lista pessoas em processo de integração que estão frequentando

**Interface:** Status "Em Disciplina" e "Desligado" ficam desabilitados automaticamente

---

### Cenário 3: Relatório de Membros Afastados

**Seleção:**
- Tipos: Membro, Obreiro
- Status: Inativo

**Resultado:** Lista membros oficiais que se afastaram (para acompanhamento)

---

### Cenário 4: Assembleia  (Apenas Membros Oficiais)

**Seleção:**
- Tipos: Membro, Obreiro
- Status: Ativo, Em Disciplina

**Resultado:** Todos os membros com direito a voto (ativos) e os que estão em disciplina (para registro)

---

## 🔗 Documentos Relacionados

- `SISTEMA_HIBRIDO_PARTICIPANTES.md` - Sistema de participantes dinâmicos
- `README.md` - Visão geral do projeto
- `CHAT_RESPOSTAS.md` - Histórico de decisões e análises

---

## 📝 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| 10/03/2026 | 1.0 | Criação do documento | GitHub Copilot |

---

## ❓ Dúvidas Frequentes

### P: Um membro que saiu da igreja deve ser Inativo ou Desligado?

**R:** Depende:
- **Inativo:** Membro que se afastou mas não pediu desligamento formal
- **Desligado:** Membro que foi oficialmente desligado (pedido ou disciplina)

### P: Congregado que parou de vir deve ser marcado como?

**R:** **Inativo**. Congregado não pode ser "desligado" pois nunca foi membro oficial.

### P: Posso ter Visitante em Disciplina?

**R:** **NÃO**. Visitante não está sob governo da igreja, logo não pode ser disciplinado formalmente.

### P: Como faço quando Congregado vira Membro?

**R:** Altere o **Tipo de Pessoa** de "Congregado" para "Membro" no cadastro. O sistema registrará a transição.

### P: Quando devo usar o campo "Sub-Status de Inativo"?

**R:** Use quando quiser **documentar o motivo específico** da inatividade. Exemplos:
- Membro faleceu → FALECIDO
- Membro mudou para outra denominação → MUDOU
- Membro transferido para congregação irmã → TRANSFERIDO
- Membro afastado temporariamente → deixe em branco

**Importante:** Este campo é **opcional** e serve apenas para consulta futura e relatórios.

### P: Devo usar "Sub-Status: TRANSFERIDO" ou Status "Desligado"?

**R:** Depende da política da igreja:

| Situação | Recomendação |
|----------|--------------|
| Transferência dentro do mesmo ministério | **Inativo + sub_status: TRANSFERIDO** (pessoa ainda pertence ao ministério) |
| Saída definitiva para outra denominação | **Desligado** ou **Inativo + sub_status: MUDOU** |
| Afastamento temporário | **Inativo** (sem sub_status) |

### P: O que fazer quando membro falece?

**R:** Duas opções:

**Opção 1 (Recomendada):**
- Status: **Inativo**
- Sub-Status: **FALECIDO**
- **Vantagem:** Mantém registro completo no sistema para estatísticas e histórico

**Opção 2:**
- Status: **Desligado**
- **Vantagem:** Membro não aparece mais em listas de membros ativos

**Nota:** A Opção 1 é melhor para fins históricos, familiares e estatísticas da igreja.

### P: O campo "Sub-Status de Inativo" afeta relatórios ou permissões?

**R:** **NÃO**. Este campo é **puramente documental**. Ele:
- ❌ **Não afeta** quem pode acessar o sistema
- ❌ **Não afeta** listas de participantes de eventos
- ❌ **Não afeta** validações automáticas
- ✅ **Serve apenas** para documentação e consultas futuras
- ✅ **Pode ser usado** em relatórios customizados (se implementado)

### P: Posso deixar o "Sub-Status de Inativo" em branco?

**R:** **SIM!** O campo é **opcional**. Use apenas se for relevante documentar o motivo específico da inatividade. 

Exemplos de quando **não precisa preencher**:
- Membro afastado temporariamente (doença, trabalho)
- Motivo desconhecido ou não especificado

### P: Por que o tipo "Visitante" não aparece ao criar/editar eventos?

**R:** **Visitante está OCULTO na interface de "Participantes Esperados"** por decisão de design:

**Motivos:**
- ✅ Visitantes são **imprevisíveis** - impossível definir "participantes esperados"
- ✅ Sempre retorna **0 pessoas** (confunde usuário)
- ✅ Recepção **cadastra visitantes no momento da chegada** (não antes)
- ✅ Não faz sentido lógico esperar visitantes específicos

**Observações:**
- Visitantes **continuam existindo** no sistema normalmente
- Podem ser **cadastrados pela secretaria** a qualquer momento
- Apenas **não aparecem nos checkboxes** de participantes de eventos
- Esta regra **não afeta** outras funcionalidades do sistema
- Simples afastamento sem causa definida

---

**Fim do Documento**
