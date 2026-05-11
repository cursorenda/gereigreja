"""Admin para modelos de cargos e atribuições."""
from django.contrib import admin

from .models import Cargo, MembroCargo, TransferenciaMembro


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'grupo_permissao')
    search_fields = ('nome',)
    autocomplete_fields = ['grupo_permissao']
    list_filter = ('grupo_permissao',)


@admin.register(MembroCargo)
class MembroCargoAdmin(admin.ModelAdmin):
    list_display = ('membro', 'cargo', 'data_inicio', 'data_fim')
    search_fields = ('membro__nome', 'cargo__nome')
    autocomplete_fields = ['membro', 'cargo']
    list_filter = ('cargo',)


@admin.register(TransferenciaMembro)
class TransferenciaMembroAdmin(admin.ModelAdmin):
    list_display = (
        'membro',
        'igreja_origem',
        'igreja_destino',
        'status',
        'data_solicitacao',
        'usuario_solicitante',
        'data_aprovacao',
        'usuario_aprovador',
    )
    list_filter = ('status', 'igreja_origem', 'igreja_destino')
    search_fields = ('membro__nome', 'motivo', 'observacao')
    autocomplete_fields = [
        'membro', 'igreja_origem', 'igreja_destino',
        'usuario_solicitante', 'usuario_aprovador'
    ]
    readonly_fields = ('data_solicitacao', 'data_aprovacao')
    ordering = ('-data_solicitacao',)
