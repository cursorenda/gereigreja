
from django.db import models
from django.conf import settings
from secretaria.models import Membro
from configuracao.models import Igreja



class Evento(models.Model):
	quantidade_dias = models.PositiveIntegerField(
		default=1,
		verbose_name="Quantidade de dias do evento",
		help_text="Informe quantos dias o evento dura. Para eventos de um dia, deixe como 1."
	)
	incluir_todos_membros = models.BooleanField(
		default=False,
		verbose_name="Incluir todos os membros",
		help_text="Marque para incluir todos os membros da igreja como participantes esperados deste evento."
	)
	tipos_participantes = models.ManyToManyField(
		'secretaria.TipoPessoa',
		blank=True,
		related_name='eventos_por_tipo',
		verbose_name='Tipos de Pessoas Esperadas',
		help_text='Selecione os tipos de pessoas esperadas para este evento.'
	)
	status_participantes = models.ManyToManyField(
		'secretaria.StatusPessoa',
		blank=True,
		related_name='eventos_por_status',
		verbose_name='Status de Pessoas Esperadas',
		help_text='Selecione os status de pessoas esperadas para este evento.'
	)
	capa = models.ImageField(upload_to='eventos/capas/', blank=True, null=True, help_text="Imagem de capa do evento")

	TIPO_EVENTO_CHOICES = [
		("culto", "Culto"),
		("reuniao", "Reunião"),
		("festa", "Festa"),
		("feriado", "Feriado"),
		("estudo", "Estudo"),
		("outro", "Outro"),
	]

	igreja = models.ForeignKey(Igreja, on_delete=models.PROTECT, related_name='eventos')
	titulo = models.CharField(max_length=200)
	descricao = models.TextField(blank=True, null=True)
	tipo = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES, default="outro")
	local = models.CharField(max_length=200, blank=True, null=True)
	responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='eventos_responsavel')
	data_inicio = models.DateTimeField()
	data_fim = models.DateTimeField(blank=True, null=True)
	hora_termino = models.TimeField('Hora de término', blank=True, null=True)

	# Recorrência
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

	criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='eventos_criados')
	atualizado_em = models.DateTimeField(auto_now=True)
	criado_em = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.titulo} ({self.data_inicio:%d/%m/%Y %H:%M})"

	class Meta:
		ordering = ['-data_inicio']


class EventoAnexo(models.Model):
	evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='anexos')
	arquivo = models.FileField(upload_to='eventos/anexos/')
	nome = models.CharField(max_length=255, blank=True)
	enviado_em = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.nome or self.arquivo.name


class ParticipacaoEvento(models.Model):
	PAPEL_CHOICES = [
		('PARTICIPANTE', 'Participante'),
		('ORGANIZADOR', 'Organizador'),
		('PALESTRANTE', 'Palestrante'),
		('CONVIDADO', 'Convidado'),
	]
	STATUS_CHOICES = [
		('PENDENTE', 'Pendente'),
		('CONFIRMADO', 'Confirmado'),
		('RECUSADO', 'Recusado'),
		('AUSENTE', 'Ausente'),
		('PRESENTE', 'Presente'),
	]
	evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='participacoes')
	membro = models.ForeignKey(Membro, on_delete=models.CASCADE, related_name='participacoes_eventos', blank=True, null=True)
	convidado_nome = models.CharField(max_length=100, blank=True, null=True, help_text="Nome do convidado externo (se não for membro)")
	convidado_email = models.EmailField(blank=True, null=True)
	papel = models.CharField(max_length=20, choices=PAPEL_CHOICES, default='PARTICIPANTE')
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
	observacoes = models.TextField(blank=True, null=True)
	justificativa_falta = models.TextField(
		blank=True, null=True,
		verbose_name="Justificativa da falta",
		help_text="Motivo da ausência do participante neste evento."
	)
	confirmado_em = models.DateTimeField(blank=True, null=True)
	criado_em = models.DateTimeField(auto_now_add=True)
	atualizado_em = models.DateTimeField(auto_now=True)

	def __str__(self):
		if self.membro:
			return f"{self.membro} em {self.evento} ({self.get_papel_display()})"
		return f"{self.convidado_nome} (convidado) em {self.evento}"

	class Meta:
		unique_together = ('evento', 'membro', 'convidado_email')
		verbose_name = 'Participação em Evento'
		verbose_name_plural = 'Participações em Eventos'
