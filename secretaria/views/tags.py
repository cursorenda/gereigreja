"""
secretaria/views/tags.py
Views para gerenciamento de tags (criação, edição e exclusão).
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.decorators import page_access_required, verificar_assinatura_valida
from secretaria.forms import TagForm
from secretaria.models import Tag


@login_required
@verificar_assinatura_valida
@page_access_required('secretaria_tags')
def criar_tag(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('secretaria:lista_membros')
    else:
        form = TagForm()
    all_tags = Tag.objects.all().order_by('nome')
    return render(request, 'secretaria/criar_tag.html', {'form': form, 'all_tags': all_tags})


@login_required
@page_access_required('secretaria_tags')
def editar_tag(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tag atualizada com sucesso!')
            return redirect('secretaria:criar_tag')
    else:
        form = TagForm(instance=tag)
    return render(request, 'secretaria/editar_tag.html', {'form': form, 'tag': tag})


@login_required
@page_access_required('secretaria_tags')
def excluir_tag(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    if request.method == 'POST':
        tag.delete()
        messages.success(request, 'Tag excluída com sucesso!')
        return redirect('secretaria:criar_tag')
    return render(request, 'secretaria/excluir_tag.html', {'tag': tag})
