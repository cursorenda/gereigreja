from django.contrib import admin
from .models import Membro, Cargo, MembroCargo

@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = ("nome", "usuario")
    search_fields = ("nome", "usuario__username", "usuario__email")

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ("nome", "grupo_permissao")
    search_fields = ("nome",)

@admin.register(MembroCargo)
class MembroCargoAdmin(admin.ModelAdmin):
    list_display = ("membro", "cargo", "data_inicio", "data_fim")
    list_filter = ("cargo",)
    search_fields = ("membro__nome", "cargo__nome")
