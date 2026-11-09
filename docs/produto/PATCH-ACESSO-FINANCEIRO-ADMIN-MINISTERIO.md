# Patch — Acesso do Admin Ministério ao Financeiro por Tipo de Igreja

Data: Setembro de 2026  
Status: PRONTO PARA IMPLEMENTAÇÃO

## 1. Valores reais confirmados

`configuracao/models.py` define:

```python
TIPO_IGREJA_CHOICES = [
    ('sede', 'Sede'),
    ('regional', 'Regional'),
    ('congregacao', 'Congregação'),
    ('independente', 'Independente'),
]
```

Logo, a regra funcional deve utilizar exatamente:

```python
'sede'
'independente'
```

como tipos elegíveis para `ADMIN_MINISTERIO`.

Não existe `subsede` no modelo atual.

## 2. Alteração em `contas/page_permissions.py`

### 2.1 Adicionar a constante

Próximo às demais constantes/regras locais do arquivo:

```python
TIPOS_IGREJA_FINANCEIRO_ADMIN_MINISTERIO = frozenset({
    'sede',
    'independente',
})
```

Esses valores correspondem diretamente aos choices de `Igreja.tipo_igreja`.

### 2.2 Adicionar a função

Antes de `PAGE_ACCESS_RULES`:

```python
def pode_acessar_financeiro(user, request=None, igreja=None):
    """
    Autoriza a entrada no módulo Financeiro.

    Regras:
    - Pastor Local e Tesoureiro preservam o comportamento atual.
    - Admin Ministério somente entra quando a igreja em contexto é
      Sede ou Independente.
    - A exceção de Admin Ministério exige igreja em contexto.
    - O módulo Financeiro precisa estar habilitado.
    - is_superuser não recebe bypass implícito nesta regra.
    """
    if not user or not user.is_authenticated:
        return False

    if not usuario_pode_usar_modulo(user, 'financeiro'):
        return False

    if user_tem_qualquer_grupo(user, [PASTOR_LOCAL, TESOUREIRO]):
        return True

    if not user_tem_grupo(user, ADMIN_MINISTERIO):
        return False

    igreja_contexto = igreja or getattr(request, 'igreja_ativa', None)

    if not igreja_contexto:
        return False

    return igreja_contexto.tipo_igreja in TIPOS_IGREJA_FINANCEIRO_ADMIN_MINISTERIO
```

### 2.3 Substituir a regra atual

Remover:

```python
'financeiro': lambda user: user_tem_qualquer_grupo(user, [
    PASTOR_LOCAL,
    TESOUREIRO,
]) and usuario_pode_usar_modulo(user, 'financeiro'),
```

Substituir por:

```python
'financeiro': pode_acessar_financeiro,
```

## 3. Compatibilidade com `user_can_access_page()`

`user_can_access_page()` já inspeciona a assinatura da regra e repassa `request` e/ou `igreja` quando esses parâmetros existem.

Portanto:

```python
def pode_acessar_financeiro(user, request=None, igreja=None):
```

é compatível com a arquitetura atual e não exige alteração em `core/decorators.py`.

## 4. Casos de teste obrigatórios

```text
Admin Ministério + Sede
→ PERMITIR

Admin Ministério + Independente
→ PERMITIR

Admin Ministério + Regional
→ NEGAR

Admin Ministério + Congregação
→ NEGAR

Admin Ministério + sem igreja ativa
→ NEGAR

Tesoureiro + Congregação permitida
→ preservar comportamento atual

Pastor Local + igreja local permitida
→ preservar comportamento atual

Membro Comum + Sede
→ NEGAR

Admin Ministério + Sede + módulo Financeiro desabilitado
→ NEGAR
```

O último caso é essencial para garantir que a nova regra não contorne `usuario_pode_usar_modulo()`.

## 5. Teste unitário recomendado

Criar ou incorporar em arquivo de testes já existente, reutilizando fixtures/factories do projeto.

O alvo principal deve ser:

```python
user_can_access_page(user, 'financeiro', request=request)
```

e, quando útil, diretamente:

```python
pode_acessar_financeiro(user, request=request)
```

## 6. Teste de integração

Validar pelo menos uma view real protegida por:

```python
@page_access_required('financeiro')
```

Resultados esperados:

```text
Admin Ministério + Sede
→ autorizado

Admin Ministério + Independente
→ autorizado

Admin Ministério + Regional
→ HTTP 403

Admin Ministério + Congregação
→ HTTP 403
```

Se a view redirecionar por regra funcional posterior, o teste deve distinguir:

```text
autorização da page_key
≠
resultado funcional final da view
```

## 7. Não alterar

Esta melhoria não exige alteração em:

```text
core/decorators.py
```

Também não deve adicionar:

```python
if user.is_superuser:
    return True
```

A arquitetura existente de `page_access_required()` está adequada.

## 8. Próxima auditoria após o patch

Depois da implementação e dos testes, revisar as ações internas do Financeiro para separar:

```text
entrada no módulo
≠
criar
≠
editar
≠
excluir
≠
fechar/reabrir caixa
≠
gerenciar contas bancárias
≠
aprovar
```

A concessão ao Admin Ministério não deve torná-lo automaticamente equivalente ao Tesoureiro.
