from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse


class Categoria(models.Model):
    nome = models.CharField('Nome', max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"{reverse('blog:lista')}?categoria={self.slug}"


class Post(models.Model):
    titulo = models.CharField('Título', max_length=200)
    slug = models.SlugField(unique=True, max_length=220, blank=True)
    resumo = models.TextField(
        'Resumo',
        max_length=300,
        help_text='Breve descrição exibida na listagem e nas metas SEO (máx. 300 caracteres).'
    )
    conteudo = models.TextField(
        'Conteúdo',
        help_text='Conteúdo completo. Suporta HTML básico (tags p, h2, h3, ul, li, strong, em, a).'
    )
    imagem_capa = models.ImageField(
        'Imagem de capa',
        upload_to='blog/',
        blank=True,
        null=True,
        help_text='Imagem exibida no topo do post e na listagem. Recomendado: 1200x630px.'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Categoria'
    )
    publicado_em = models.DateTimeField('Data de publicação', null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    publicado = models.BooleanField('Publicado', default=False)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-publicado_em']

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        if self.publicado and not self.publicado_em:
            self.publicado_em = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:detalhe', kwargs={'slug': self.slug})
