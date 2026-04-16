# Testes Avançados de Permissões Hierárquicas – GereIgreja

Este arquivo sugere e exemplifica testes automatizados para cenários avançados de permissões, além dos básicos já validados.

---

## 1. Usuário com múltiplos grupos
- Usuário pertence a dois grupos de níveis diferentes (ex: Tesoureiro e Equipe de Eventos).
- Esperado: prevalece o grupo de maior privilégio.

## 2. Usuário inativo
- Usuário está em grupo correto, mas `is_active=False`.
- Esperado: acesso negado.

## 3. Grupo inexistente
- Checagem de permissão para grupo não cadastrado.
- Esperado: acesso negado, log de erro.

## 4. Usuário sem grupo, mas com `is_staff=True`
- Esperado: acesso negado.

## 5. Usuário comum (sem staff, sem grupo)
- Esperado: acesso negado.

## 6. Usuário superusuário e inativo
- `is_superuser=True`, `is_active=False`.
- Esperado: acesso total (padrão Django), mas pode ser customizado.

## 7. Usuário com permissão removida em tempo de execução
- Remover grupo do usuário e tentar acessar.
- Esperado: acesso negado imediatamente.

## 8. Usuário com múltiplos grupos do mesmo nível
- Ex: Tesoureiro e Superintendente EBD.
- Esperado: acesso concedido se qualquer grupo for suficiente.

## 9. Usuário com grupo abaixo do exigido
- Ex: Equipe de Eventos tentando acessar view de Tesoureiro.
- Esperado: acesso negado.

## 10. Usuário com grupo acima do exigido
- Ex: Admin Ministerio tentando acessar view de Tesoureiro.
- Esperado: acesso concedido.

---

## Exemplo de teste automatizado (pytest + Django)
```python
import pytest
from django.urls import reverse
from django.contrib.auth.models import User, Group
from contas.constants import TESOUREIRO, EQUIPE_EVENTOS, ADMIN_MINISTERIO

@pytest.mark.django_db
def test_usuario_multiplos_grupos(client):
    user = User.objects.create_user('multi@teste.com', password='123')
    group1 = Group.objects.get(name=TESOUREIRO)
    group2 = Group.objects.get(name=EQUIPE_EVENTOS)
    user.groups.add(group1, group2)
    user.is_staff = True
    user.save()
    client.login(username='multi@teste.com', password='123')
    resp = client.get(reverse('financeiro:alguma_view_restrita'))
    assert resp.status_code == 200  # Deve acessar pois é Tesoureiro
```

---

> Adapte os testes conforme suas views e regras. Execute sempre após alterações na lógica de permissão.

Última revisão: 01/04/2026
