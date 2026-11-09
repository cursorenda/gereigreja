
from django import forms
from django.contrib import admin
from django.contrib.admin import widgets
from django.db import router
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from .services_mutations import delete_event, delete_events
from core.admin_mixins import DataInicioHierarchyMixin
from .models import Evento, ParticipacaoEvento

@admin.register(Evento)
class EventoAdmin(DataInicioHierarchyMixin, admin.ModelAdmin):
	list_display = ("titulo", "status_evento", "status_operacional", "data_inicio", "data_fim", "igreja", "criado_por")
	search_fields = ("titulo", "descricao", "local")
	list_filter = ("status_evento", "status_operacional", "igreja", "data_inicio")
	ordering = ("-data_inicio",)

	def formfield_for_manytomany(self, db_field, request, **kwargs):
		if db_field.name not in ("tipos_participantes", "status_participantes"):
			return super().formfield_for_manytomany(db_field, request, **kwargs)

		# These explicit throughs have no extra fields to populate. Let
		# formfield_for_dbfield handle the related widget and permissions.
		using = kwargs.get("using")
		if "widget" not in kwargs:
			if db_field.name in self.get_autocomplete_fields(request):
				kwargs["widget"] = widgets.AutocompleteSelectMultiple(db_field, self.admin_site, using=using)
			elif db_field.name in self.raw_id_fields:
				kwargs["widget"] = widgets.ManyToManyRawIdWidget(db_field.remote_field, self.admin_site, using=using)
			elif db_field.name in (*self.filter_vertical, *self.filter_horizontal):
				kwargs["widget"] = widgets.FilteredSelectMultiple(
					db_field.verbose_name, db_field.name in self.filter_vertical,
				)

		if "queryset" not in kwargs:
			queryset = self.get_field_queryset(using, db_field, request)
			if queryset is not None:
				kwargs["queryset"] = queryset

		field = db_field.formfield(**kwargs)
		if (
			isinstance(field.widget, forms.SelectMultiple)
			and field.widget.allow_multiple_selected
			and not isinstance(field.widget, (forms.CheckboxSelectMultiple, widgets.AutocompleteSelectMultiple))
		):
			hint = _("Hold down “Control”, or “Command” on a Mac, to select more than one.")
			field.help_text = format_lazy("{} {}", field.help_text, hint) if field.help_text else hint
		return field

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
