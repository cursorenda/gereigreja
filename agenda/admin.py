"""Admin para agenda de eventos."""
from django.contrib import admin

from core.admin_mixins import DataInicioHierarchyMixin

from .models import AgendaEvento


@admin.register(AgendaEvento)
class AgendaEventoAdmin(DataInicioHierarchyMixin, admin.ModelAdmin):
	list_display = (
		'titulo', 'tipo', 'data_inicio', 'data_fim', 'recorrente', 'frequencia', 'responsavel',
	)
	list_filter = (
		'tipo', 'recorrente', 'frequencia', 'data_inicio', 'responsavel',
	)
	search_fields = ('titulo', 'descricao', 'local')
	fieldsets = (
		(None, {
			'fields': ('titulo', 'descricao', 'tipo', 'local', 'responsavel')
		}),
		('Datas', {
			'fields': ('data_inicio', 'data_fim')
		}),
		('Recorrência', {
			'fields': (
				'recorrente', 'frequencia', 'intervalo', 'dia_semana', 'semana_mes', 'mes_ano', 'data_fim_recorrencia'
			),
			'classes': ('collapse',)
		}),
	)
	actions = ['duplicar_eventos']

	def duplicar_eventos(self, request, queryset):
		for obj in queryset:
			obj.pk = None
			obj.titulo = f"Cópia de {obj.titulo}"
			obj.save()
		self.message_user(request, "Eventos duplicados com sucesso.")
	duplicar_eventos.short_description = "Duplicar eventos selecionados"
