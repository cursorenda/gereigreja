from django.contrib import admin
from .models import Post, Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug']
    prepopulated_fields = {'slug': ('nome',)}
    fieldsets = (
        (None, {
            'fields': ('nome', 'slug')
        }),
        ('SEO', {
            'fields': ('palavras_chave',),
            'description': 'Palavras-chave usadas na meta tag keywords da página de listagem desta categoria.'
        }),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'publicado', 'publicado_em', 'criado_em']
    list_filter = ['publicado', 'categoria']
    search_fields = ['titulo', 'resumo', 'conteudo']
    prepopulated_fields = {'slug': ('titulo',)}
    list_editable = ['publicado']
    date_hierarchy = 'publicado_em'
    readonly_fields = ['criado_em', 'atualizado_em']
    fieldsets = (
        ('Conteúdo', {
            'fields': ('titulo', 'slug', 'categoria', 'resumo', 'conteudo', 'imagem_capa')
        }),
        ('SEO', {
            'fields': ('palavras_chave',),
            'description': 'Palavras-chave separadas por vírgula. Ex: gestão de igreja, cadastro de membros, sistema eclesiástico'
        }),
        ('Publicação', {
            'fields': ('publicado', 'publicado_em')
        }),
        ('Informações', {
            'classes': ('collapse',),
            'fields': ('criado_em', 'atualizado_em'),
        }),
    )
