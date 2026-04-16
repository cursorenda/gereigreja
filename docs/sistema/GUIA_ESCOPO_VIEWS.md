# Guia de Escopo Hierarquico nas Views

## Objetivo

Padronizar o controle de escopo por igreja em todo o sistema, reduzindo logica duplicada e garantindo consistencia entre secretaria, financeiro e eventos.

## Arquitetura Atual

### Camada 1: Middleware automatico

Arquivo: `core/middleware.py` (`ActiveChurchMiddleware`)

Responsabilidades:

- Define `request.igrejas_permitidas` para toda requisicao autenticada.
- Valida e define `request.igreja_ativa` com base na sessao (`igreja_ativa_id`) e no escopo permitido.
- Limpa sessao quando a igreja ativa fica invalida.
- Define automaticamente igreja ativa quando o usuario tem acesso a apenas uma igreja.

### Camada 2: Decorator de compatibilidade

Arquivo: `core/decorators.py` (`inject_igrejas_permitidas`)

Comportamento atual:

- Se o middleware ja preencheu `request.igrejas_permitidas`, apenas reutiliza.
- Se nao preencheu (fallback), calcula usando `get_igrejas_permitidas`.

Resultado: nao ha quebra para views antigas e o custo de recalculo foi reduzido.

### Camada 3: Helpers de filtragem

- `core.utils.get_igrejas_permitidas(user, ministerio)`
- `core.decorators.filtrar_queryset_escopo(queryset, request, igreja_field='igreja')`

Use quando precisar de filtragem em funcoes auxiliares, CBVs ou querysets com relacoes.

## Padrao Recomendado para Novas Views

### Caso 1: View de listagem simples

```python
from core.decorators import inject_igrejas_permitidas

@login_required
@inject_igrejas_permitidas
def lista_membros(request):
    membros = Membro.objects.filter(igreja__in=request.igrejas_permitidas)
    return render(request, 'secretaria/lista_membros.html', {'membros': membros})
```

### Caso 2: Respeitar igreja ativa quando definida

```python
@login_required
@inject_igrejas_permitidas
def lista_receitas(request):
    allowed = request.igrejas_permitidas
    igreja_ativa = getattr(request, 'igreja_ativa', None)

    if igreja_ativa and allowed.filter(pk=igreja_ativa.pk).exists():
        qs = Receitas.objects.filter(igreja=igreja_ativa)
    elif igreja_ativa:
        qs = Receitas.objects.none()
    else:
        qs = Receitas.objects.filter(igreja__in=allowed)

    return render(request, 'financeiro/receitas/lista_receitas.html', {'receitas': qs})
```

### Caso 3: CBV ou lookup aninhado

```python
from core.decorators import filtrar_queryset_escopo

class CargoListView(ListView):
    model = Cargo

    def get_queryset(self):
        qs = super().get_queryset()
        return filtrar_queryset_escopo(qs, self.request, igreja_field='membro__igreja')
```

## Regras de Ouro

1. Nao compare objetos com `in allowed_churches`; use `allowed_churches.filter(pk=...).exists()`.
2. Nao recalcule escopo manual em toda view quando `request.igrejas_permitidas` ja estiver disponivel.
3. Em detalhes por `pk`, sempre aplique filtro por escopo no `get_object_or_404`.
4. Se `igreja_ativa` vier fora do escopo, retorne vazio (`.none()`) ou negue acesso explicitamente.

## Status de Implementacao

- Opcao 5 (refatoracao views principais): concluida.
- Opcao 6 (middleware automatico): concluida.
- Opcao 7 (documentacao): esta versao consolida o fluxo final.

## Checklist de Revisao para PR

- [ ] A view usa `request.igrejas_permitidas` diretamente ou via helper.
- [ ] Nao ha fallback manual duplicando hierarquia de permissao.
- [ ] Objetos por `pk` estao filtrados por escopo.
- [ ] `igreja_ativa` e validada com `exists()`.
- [ ] `manage.py check` executado com sucesso.

## Troubleshooting Rapido

### `request.igrejas_permitidas` vazio

- Verifique se o usuario tem perfil com ministerio.
- Verifique grupos e escopo no perfil.
- Verifique se `ActiveChurchMiddleware` esta habilitado em `MIDDLEWARE`.

### Igreja ativa sumiu da sessao

- O middleware remove automaticamente `igreja_ativa_id` quando a igreja sai do escopo do usuario.

### View antiga ainda funciona?

- Sim. O decorator `@inject_igrejas_permitidas` permanece compativel e reutiliza o valor do middleware.

---

Ultima atualizacao: Abril/2026
