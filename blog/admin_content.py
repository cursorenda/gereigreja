from django.contrib import admin

from .models import Categoria, Post


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
            'description': 'Palavras-chave usadas na meta tag keywords da pagina de listagem desta categoria.'
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
        ('Conteudo', {
            'fields': ('titulo', 'slug', 'categoria', 'resumo', 'conteudo', 'imagem_capa')
        }),
        ('SEO', {
            'fields': ('palavras_chave',),
            'description': 'Palavras-chave separadas por virgula. Ex: gestao de igreja, cadastro de membros, sistema eclesiastico'
        }),
        ('Publicacao', {
            'fields': ('publicado', 'publicado_em')
        }),
        ('Informacoes', {
            'classes': ('collapse',),
            'fields': ('criado_em', 'atualizado_em'),
        }),
    )
