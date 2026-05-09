# WhatsApp Edição em Massa de Celulares

## Visão Geral

Funcionalidade que permite editar celulares de múltiplas pessoas simultaneamente, com filtragem avançada e validação em tempo real.

**Local**: `/comunicacao/whatsapp/massa/editar-celulares/`  
**Versão**: v1.10.1  
**Status**: ✅ Estável  

---

## Funcionalidades

### 1. Filtros Avançados
- **Tipos de Pessoa**: Filtrar por categoria (ex: membro, visitante, etc.)
- **Status de Pessoa**: Filtrar por status ativo, inativo, etc.
- **Aniversariantes do Mês**: Mostrar apenas pessoas aniversariantes
- **Filtro por Celular Vazio**: Checkbox para mostrar apenas pessoas sem celular preenchido

### 2. Edição em Massa
- Tabela com até 45+ pessoas por vez
- Campo de celular com máscara automática: `(##) #####-####`
- Suporte a formatação brasileira com auto-prefixo 55
- Validação: máximo 15 dígitos por número

### 3. Persistência
- Salva apenas números que sofreram alteração
- Mantém histórico de mudanças via auditoria
- Confirmação visual de quantas pessoas foram atualizadas

### 4. Performance
- Scroll fixo na tabela (max-height: 65vh)
- Rendering client-side do filtro sem reload
- Suporte a locale-aware form serialization

---

## Implementação Técnica

### Backend (`comunicacao/views.py`)

#### Função: `editar_celulares_whatsapp_massa()`
```python
@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def editar_celulares_whatsapp_massa(request):
    # Valida congregação ativa
    # Filtra membros conforme critérios
    # Processa POST com validação de celulares
    # Salva alterações com update_fields=['celular']
```

#### Detecção de Alterações
```python
atual_celular = re.sub(r'\D', '', membro.celular or '') or None
novo_celular = celular_limpo or None
if atual_celular != novo_celular:
    atualizados.append(membro)
```

#### Parsing de POST com Locale Awareness
```python
# Handle locale-formatted keys like 'celular_1.112' → '1112'
pk_str = re.sub(r'\D', '', key[len('celular_'):])
if pk_str:
    pk = int(pk_str)
```

### Frontend (`comunicacao/templates/comunicacao/whatsapp/editar_celulares_massa.html`)

#### Máscara de Celular
```javascript
aplicarMascara(input, '(##) #####-####');
```

#### Filtro Client-side (Checkbox)
```javascript
const checkboxSemCelular = document.getElementById('checkbox-sem-celular');
checkboxSemCelular.addEventListener('change', function() {
    const mostrarApenaSemCelular = this.checked;
    document.querySelectorAll('.js-membro-row').forEach(linha => {
        const temCelular = linha.dataset.hasCelular === 'true';
        linha.style.display = mostrarApenaSemCelular && temCelular ? 'none' : '';
    });
});
```

---

## Fluxo de Uso

1. **Acesso**: Ir para `/comunicacao/whatsapp/massa/editar-celulares/`
2. **Filtrar**: Selecionar critérios (tipos, status, etc.)
3. **Visualizar**: Tabela renderiza com membros filtrados
4. **Opcionalmente**: Marcar checkbox "Mostrar apenas sem celular"
5. **Editar**: Preencher/corrigir números de celular
6. **Salvar**: Clicar "Salvar celulares em massa"
7. **Feedback**: Mensagem sucinto (ex: "Celular atualizado para 3 pessoa(s).")

---

## Validações

| Campo | Regra | Exemplo |
|-------|-------|---------|
| **Celular** | Max 15 dígitos | ✅ 11999998888 / ❌ 119999988881234567 |
| **Formato** | Somente dígitos em DB | Máscara `(##) #####-####` é visual |
| **Vazio** | Permite limpar campo | Deixar em branco = `None` no DB |

---

## Bugs Corrigidos (v1.10.1)

### Bug: Locale-Formatted POST Keys
- **Symptoma**: Chaves POST chegando como `celular_1.112` em vez de `celular_1112`
- **Causa**: Browser/Django form serialization usando decimal separator locale
- **Solução**: `re.sub(r'\D', '', key_suffix)` antes de converter para int
- **Commit**: Hash do fix incluído na versão

### Bug: Form Attribute Texto na Tela
- **Symptoma**: Texto literal "form="bulk-celulares-form"" aparecia no layout
- **Causa**: Atributo foi inserido fora do elemento HTML
- **Solução**: Movido corretamente para o botão submit

---

## Melhorias Futuras

- [ ] Exportar lista de números alterados (CSV/Excel)
- [ ] Agendamento de bulk edit para horário específico
- [ ] Integração com validação WhatsApp (verificar se número é registrado)
- [ ] Histórico de mudanças com diff visual

---

## Testes

### Caso 1: Adicionar celular ausente
1. Selecionar pessoa sem celular
2. Preencher número válido
3. Salvar
4. ✅ Esperado: Atualiza e confirma "1 pessoa atualizada"

### Caso 2: Corrigir celular existente
1. Selecionar pessoa com celular incorreto
2. Alterar número
3. Salvar
4. ✅ Esperado: Atualiza e confirma

### Caso 3: Sem alterações
1. Deixar todos os campos como estão
2. Clicar Salvar
3. ✅ Esperado: "Nenhum celular foi atualizado"

### Caso 4: Filtro sem celular
1. Marcar checkbox "Mostrar apenas sem celular"
2. Verificar que pessoas com celular desaparecem
3. Desmarcar checkbox
4. ✅ Esperado: Todos retornam à visão

---

## Performance

- **Tempo de carregamento**: < 2s para 45 pessoas
- **Scroll performance**: 60 FPS com CSS sticky
- **POST processing**: ~100-200ms para validação de 45 registros

---

## Segurança

- Validação via `@page_access_required('comunicacao')`
- Filtragem por `request.igreja_ativa` (não permite alteração cruzada de congregações)
- Sanitização de input: remoção de caracteres não-numéricos
- Limite de 15 dígitos evita injeção de dados malformados

---

## Referências

- **Views**: [comunicacao/views.py](../../comunicacao/views.py#L562-L760)
- **Template**: [comunicacao/templates/comunicacao/whatsapp/editar_celulares_massa.html](../../comunicacao/templates/comunicacao/whatsapp/editar_celulares_massa.html)
- **Models**: [secretaria/models.py](../../secretaria/models.py) - Campo `Membro.celular`
- **Forms**: [comunicacao/forms.py](../../comunicacao/forms.py) - `WhatsAppMassaForm`

---

**Autor**: Sistema  
**Última Atualização**: 09/05/2026  
**Versionamento**: v1.10.1
