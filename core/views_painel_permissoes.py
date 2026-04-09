from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .tests_painel_permissoes import lista_testes

@staff_member_required
@csrf_protect
def painel_permissoes_view(request):
    testes = lista_testes()
    resultado = None
    if request.method == 'POST':
        teste_escolhido = request.POST.get('teste')
        resultado = []
        if teste_escolhido == 'todos':
            for nome, func in testes:
                try:
                    status, msg = func(request.user)
                except Exception as e:
                    status, msg = False, f'Erro: {e}'
                resultado.append((nome, status, msg))
        else:
            for nome, func in testes:
                if nome == teste_escolhido:
                    try:
                        status, msg = func(request.user)
                    except Exception as e:
                        status, msg = False, f'Erro: {e}'
                    resultado.append((nome, status, msg))
                    break
    return render(request, 'admin/painel_permissoes.html', {'testes': testes, 'resultado': resultado})
