
from django.contrib import admin
from django.db import router
from .services_mutations import delete_event, delete_events
from core.admin_mixins import DataInicioHierarchyMixin
from .models import Evento, ParticipacaoEvento

@admin.register(Evento)
class EventoAdmin(DataInicioHierarchyMixin, admin.ModelAdmin):
	list_display = ("titulo", "status_evento", "status_operacional", "data_inicio", "data_fim", "igreja", "criado_por")
	search_fields = ("titulo", "descricao", "local")
	list_filter = ("status_evento", "status_operacional", "igreja", "data_inicio")
	ordering = ("-data_inicio",)

	def delete_model(self, request, obj):
		delete_event(obj)

	def delete_queryset(self, request, queryset):
		using = queryset._db or router.db_for_write(self.model)
		delete_events(queryset, using=using)

@admin.register(ParticipacaoEvento)
class ParticipacaoEventoAdmin(admin.ModelAdmin):
	list_display = ("evento", "membro", "convidado_nome", "papel", "status", "confirmado_em")
	search_fields = ("evento__titulo", "membro__nome", "convidado_nome", "convidado_email")
	list_filter = ("papel", "status", "evento")
	autocomplete_fields = ["evento", "membro"]
