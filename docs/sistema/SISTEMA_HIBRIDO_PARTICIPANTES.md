# Sistema Híbrido de Participantes - Gereigreja

## 📋 Visão Geral

O sistema agora usa uma abordagem **híbrida e inteligente** para gerenciar participantes de eventos, resolvendo o problema de listas desatualizadas em eventos futuros.

## 🎯 Como Funciona

### 1. **Critérios Automáticos** (Base Dinâmica)
Ao criar um evento, você define critérios:
```
Evento: "Culto de Natal - Dezembro 2026"
Critérios:
  ✓ Tipos: Membros + Obreiros
  ✓ Status: Ativo
```

### 2. **Geração Dinâmica**
Quando o evento acontece (ou você visualiza a lista):
- Sistema busca AUTOMATICAMENTE quem atende os critérios NAQUELE momento
- Se em Dezembro 2026 houver 45 pessoas ativas → 45 participantes
- Se alguém saiu da igreja → automaticamente não aparece mais

### 3. **Ajustes Manuais** (Flexibilidade)
Você pode modificar a lista:

**Adicionar manualmente:**
```
➕ Pastor Convidado (Visitante)
➕ Irmão de outro ministério
```

**Remover manualmente:**
```
➖ João Silva (vai viajar, mesmo sendo membro)
➖ Maria Santos (responsável infantil neste dia)
```

### 4. **Lista Final** (Híbrida)
```
Participantes do "Culto de Natal":
├─ 43 pessoas (critérios: Membros/Obreiros Ativos)
├─ + 2 adicionados manualmente (Pastor Convidado, Irmão Visitante)
├─ - 2 removidos manualmente (João, Maria)
└─ = 43 participantes esperados
```

## ✨ Vantagens

### ✅ **Atualização Automática**
- Membros que saírem da igreja → removidos automaticamente
- Novos membros que entrarem → incluídos automaticamente
- Mudanças de status → refletidas automaticamente

### ✅ **Casos Especiais**
- Adicionar visitantes importantes
- Remover quem não vai poder ir
- Incluir pessoas de outras igrejas

### ✅ **Histórico e Auditoria**
- Sistema registra quem foi adicionado manualmente e quando
- Registra quem foi removido manualmente e quando
- Diferencia inclusão automática de ajustes manuais

## 🔧 Estrutura Técnica

### Novo Campo: `tipo_inclusao`
```python
TIPO_INCLUSAO_CHOICES = [
    ('AUTOMATICA', 'Inclusão Automática (critérios)'),
    ('MANUAL_ADICIONADO', 'Adicionado Manualmente'),
    ('MANUAL_REMOVIDO', 'Removido Manualmente'),
]
```

### Método: `get_participantes_esperados()`
```python
def get_participantes_esperados(evento):
    # 1. Gera lista pelos critérios (dinâmico)
    pessoas_criterios = filtrar_por_tipos_e_status()
    
    # 2. Remove quem foi excluído manualmente
    removidos = lista_de_remocoes_manuais()
    pessoas_criterios = pessoas_criterios.exclude(removidos)
    
    # 3. Adiciona quem foi incluído manualmente
    adicionados = lista_de_adicoes_manuais()
    
    # 4. Retorna lista híbrida
    return pessoas_criterios + adicionados
```

## 📊 Exemplo Prático

### Cenário:
**Janeiro 2026:** Criar evento "Vigília de Ano Novo - 31/12/2026"
- Critérios: Membros + Obreiros com status Ativo
- Resultado: 50 pessoas

**Junho 2026:** Mudanças na congregação
- 5 pessoas saíram (Desligados)
- 3 novos membros entraram (Ativos)
- 1 membro foi disciplinado

**Dezembro 2026:** Visualizar lista do evento
- ❌ ANTES (sistema antigo): 50 pessoas (lista congelada)
  - Incluindo 5 desligados ❌
  - Sem os 3 novos ❌
  
- ✅ AGORA (sistema híbrido): 48 pessoas (lista atualizada)
  - Automaticamente removeu 5 desligados ✅
  - Automaticamente adicionou 3 novos ✅
  - Automaticamente removeu 1 disciplinado ✅
  - Mantém ajustes manuais (Pastor Convidado) ✅

## 🎯 Próximos Passos

1. ✅ **Modelo atualizado** (campo `tipo_inclusao` adicionado)
2. ✅ **Migration criada** (0012_participacaoevento_tipo_inclusao.py)
3. ✅ **Método de geração** (get_participantes_esperados implementado)
4. ⏳ **Interface de ajustes manuais** (adicionar/remover botões)
5. ⏳ **Endpoints AJAX** (adicionar/remover sem recarregar página)
6. ⏳ **Indicadores visuais** (badges mostrando origem: automático vs manual)

## 🚀 Status da Implementação

**Backend:** ✅ 100% Completo
- Modelo ParticipacaoEvento atualizado
- Lógica híbrida implementada
- Migration criada

**Frontend:** ⏳ 30% Completo
- Interface de seleção básica já existe
- Falta: botões adicionar/remover manuais
- Falta: indicadores visuais de tipo de inclusão

**Testes:** ⏳ Pendente
- Precisa rodar migration: `py manage.py migrate eventos`
- Testar criação de evento com critérios
- Testar ajustes manuais

## 📝 Observações

- **Retrocompatibilidade:** Participações existentes terão `tipo_inclusao='AUTOMATICA'` por padrão
- **Performance:** Método get_participantes_esperados() usa queries otimizadas com select_related
- **Segurança:** Filtro por igreja ativa já implementado na view autocomplete_convidados
- **Visitantes:** Sistema continua excluindo visitantes do filtro "Todas as pessoas da igreja"

## ✍️ Autor
Implementado em 10/03/2026
Sistema Gereigreja v1.0.x
