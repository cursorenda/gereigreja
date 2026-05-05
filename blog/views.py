from django.shortcuts import get_object_or_404, render
from .models import Post, Categoria


def lista_posts(request):
    categoria_slug = request.GET.get('categoria')
    posts = Post.objects.filter(publicado=True).select_related('categoria')
    categoria_ativa = None

    if categoria_slug:
        categoria_ativa = get_object_or_404(Categoria, slug=categoria_slug)
        posts = posts.filter(categoria=categoria_ativa)

    categorias = Categoria.objects.filter(posts__publicado=True).distinct()

    return render(request, 'blog/lista.html', {
        'posts': posts,
        'categorias': categorias,
        'categoria_ativa': categoria_ativa,
    })


def detalhe_post(request, slug):
    post = get_object_or_404(Post, slug=slug, publicado=True)
    posts_relacionados = Post.objects.filter(
        publicado=True,
        categoria=post.categoria
    ).exclude(pk=post.pk)[:3]

    return render(request, 'blog/detalhe.html', {
        'post': post,
        'posts_relacionados': posts_relacionados,
    })
