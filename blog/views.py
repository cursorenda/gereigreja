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

    post_absolute_url = request.build_absolute_uri(post.get_absolute_url())
    post_og_image_url = ''
    post_og_image_width = None
    post_og_image_height = None
    post_og_image_alt = post.titulo
    if post.imagem_capa:
        post_og_image_url = request.build_absolute_uri(post.imagem_capa.url)
        try:
            post_og_image_width = post.imagem_capa.width
            post_og_image_height = post.imagem_capa.height
        except Exception:
            post_og_image_width = None
            post_og_image_height = None

    return render(request, 'blog/detalhe.html', {
        'post': post,
        'posts_relacionados': posts_relacionados,
        'post_absolute_url': post_absolute_url,
        'post_og_image_url': post_og_image_url,
        'post_og_image_width': post_og_image_width,
        'post_og_image_height': post_og_image_height,
        'post_og_image_alt': post_og_image_alt,
    })
