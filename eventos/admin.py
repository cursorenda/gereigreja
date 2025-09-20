
from django.contrib import admin
from .models import Evento, ParticipacaoEvento

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
	list_display = ("titulo", "data_inicio", "data_fim", "igreja", "criado_por")
	search_fields = ("titulo", "descricao", "local")
	list_filter = ("igreja", "data_inicio")
	date_hierarchy = "data_inicio"
	ordering = ("-data_inicio",)

@admin.register(ParticipacaoEvento)
class ParticipacaoEventoAdmin(admin.ModelAdmin):
	list_display = ("evento", "membro", "convidado_nome", "papel", "status", "confirmado_em")
	search_fields = ("evento__titulo", "membro__nome", "convidado_nome", "convidado_email")
	list_filter = ("papel", "status", "evento")
	autocomplete_fields = ["evento", "membro"]
