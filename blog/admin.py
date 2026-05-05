from django.contrib import admin
from .models import Post, Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug']
    prepopulated_fields = {'slug': ('nome',)}


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
        ('Publicação', {
            'fields': ('publicado', 'publicado_em')
        }),
        ('Informações', {
            'classes': ('collapse',),
            'fields': ('criado_em', 'atualizado_em'),
        }),
    )
