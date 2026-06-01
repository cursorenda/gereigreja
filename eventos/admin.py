
from django.contrib import admin
from core.admin_mixins import DataInicioHierarchyMixin
from .models import Evento, ParticipacaoEvento

@admin.register(Evento)
class EventoAdmin(DataInicioHierarchyMixin, admin.ModelAdmin):
	list_display = ("titulo", "status_evento", "data_inicio", "data_fim", "igreja", "criado_por")
	search_fields = ("titulo", "descricao", "local")
	list_filter = ("status_evento", "igreja", "data_inicio")
	ordering = ("-data_inicio",)

@admin.register(ParticipacaoEvento)
class ParticipacaoEventoAdmin(admin.ModelAdmin):
	list_display = ("evento", "membro", "convidado_nome", "papel", "status", "confirmado_em")
	search_fields = ("evento__titulo", "membro__nome", "convidado_nome", "convidado_email")
	list_filter = ("papel", "status", "evento")
	autocomplete_fields = ["evento", "membro"]
