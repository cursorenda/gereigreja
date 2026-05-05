from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap para páginas estáticas públicas do Gereigreja."""
    protocol = 'https'

    # (name, priority, changefreq)
    _pages = [
        ('landing_page', 1.0, 'weekly'),
        ('blog:lista', 0.8, 'daily'),
        ('politica_privacidade', 0.3, 'monthly'),
        ('termos_condicoes', 0.3, 'monthly'),
    ]

    def items(self):
        return [name for name, _, _ in self._pages]

    def priority(self, item):
        return {name: p for name, p, _ in self._pages}.get(item, 0.5)

    def changefreq(self, item):
        return {name: cf for name, _, cf in self._pages}.get(item, 'monthly')

    def location(self, item):
        return reverse(item)


class BlogPostSitemap(Sitemap):
    """Sitemap dinâmico para posts publicados do blog."""
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        from blog.models import Post
        return Post.objects.filter(publicado=True)

    def lastmod(self, obj):
        return obj.atualizado_em

    def location(self, obj):
        return obj.get_absolute_url()
