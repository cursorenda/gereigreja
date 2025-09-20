from django.db import models
from django.contrib.auth import get_user_model

class AgendaEvento(models.Model):
	TIPO_EVENTO_CHOICES = [
		("culto", "Culto"),
		("reuniao", "Reunião"),
		("festa", "Festa"),
		("feriado", "Feriado"),
		("outro", "Outro"),
	]

	titulo = models.CharField(max_length=100)
	descricao = models.TextField(blank=True)
	tipo = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES, default="outro")
	local = models.CharField(max_length=100, blank=True)
	responsavel = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
	data_inicio = models.DateTimeField()
	data_fim = models.DateTimeField()

	# Recorrência: campos inspirados em RRULE (Google Agenda)
	recorrente = models.BooleanField(default=False)
	frequencia = models.CharField(
		max_length=10,
		choices=[
			("nenhuma", "Não recorrente"),
			("diaria", "Diária"),
			("semanal", "Semanal"),
			("mensal", "Mensal"),
			("anual", "Anual"),
		],
		default="nenhuma"
	)
	intervalo = models.PositiveIntegerField(default=1, help_text="Intervalo entre repetições (ex: 2 = a cada 2 semanas)")
	dia_semana = models.CharField(
		max_length=20,
		blank=True,
		help_text="Ex: 'MO,TU' para segunda e terça. Usado em recorrência semanal/mensal."
	)
	semana_mes = models.CharField(
		max_length=10,
		blank=True,
		help_text="Ex: '1', '2', '-1' (última semana). Usado em recorrência mensal."
	)
	mes_ano = models.CharField(
		max_length=20,
		blank=True,
		help_text="Ex: '1,6,12' para janeiro, junho, dezembro. Usado em recorrência anual."
	)
	data_fim_recorrencia = models.DateField(null=True, blank=True, help_text="Data final da recorrência")

	criado_em = models.DateTimeField(auto_now_add=True)
	atualizado_em = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.titulo
