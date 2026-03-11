
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

	def get_participantes_esperados(self):
		"""
		Retorna lista de participantes esperados usando sistema híbrido:
		1. Gera lista baseada em critérios (tipos_participantes + status_participantes)
		2. Remove quem foi manualmente excluído
		3. Adiciona quem foi manualmente incluído
		"""
		from secretaria.models import Membro
		
		# Gerar lista baseada em critérios
		membros_criterios = Membro.objects.filter(igreja=self.igreja)
		
		# Aplicar filtros de tipo e status
		if self.tipos_participantes.exists():
			membros_criterios = membros_criterios.filter(tipo_pessoa__in=self.tipos_participantes.all())
		if self.status_participantes.exists():
			membros_criterios = membros_criterios.filter(status_pessoa__in=self.status_participantes.all())
		
		# Se incluir_todos_membros está marcado, ignora filtros de tipo
		if self.incluir_todos_membros:
			membros_criterios = Membro.objects.filter(igreja=self.igreja)
			if self.status_participantes.exists():
				membros_criterios = membros_criterios.filter(status_pessoa__in=self.status_participantes.all())
		
		# Remover os que foram manualmente excluídos
		removidos_ids = self.participacoes.filter(
			tipo_inclusao='MANUAL_REMOVIDO'
		).values_list('membro_id', flat=True)
		
		membros_criterios = membros_criterios.exclude(pk__in=removidos_ids)
		
		# Buscar os que foram manualmente adicionados
		adicionados_manualmente = self.participacoes.filter(
			tipo_inclusao='MANUAL_ADICIONADO'
		).select_related('membro')
		
		# Combinar: membros dos critérios + adicionados manualmente
		# Retorna QuerySet de membros dos critérios e lista de ParticipacaoEvento adicionados
		return membros_criterios.distinct(), adicionados_manualmente

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
	TIPO_INCLUSAO_CHOICES = [
		('AUTOMATICA', 'Inclusão Automática (critérios)'),
		('MANUAL_ADICIONADO', 'Adicionado Manualmente'),
		('MANUAL_REMOVIDO', 'Removido Manualmente'),
	]
	evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='participacoes')
	# Optional session: when an Evento spans multiple days we create
	# EventoSessao objects (one per day) and link participations to a specific
	# session so presence/absence can be tracked per day.
	sessao = models.ForeignKey('EventoSessao', on_delete=models.CASCADE, related_name='participacoes', blank=True, null=True)
	membro = models.ForeignKey(Membro, on_delete=models.CASCADE, related_name='participacoes_eventos', blank=True, null=True)
	convidado_nome = models.CharField(max_length=100, blank=True, null=True, help_text="Nome do convidado externo (se não for membro)")
	convidado_email = models.EmailField(blank=True, null=True)
	papel = models.CharField(max_length=20, choices=PAPEL_CHOICES, default='PARTICIPANTE')
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
	tipo_inclusao = models.CharField(
		max_length=20,
		choices=TIPO_INCLUSAO_CHOICES,
		default='AUTOMATICA',
		verbose_name='Tipo de Inclusão',
		help_text='Como este participante foi incluído no evento: automaticamente pelos critérios ou manualmente pelo usuário'
	)
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
		# Include sessao to allow one participation record per member per session.
		# sessao can be null (for legacy single-event behavior) so uniqueness is
		# enforced when sessao is set. Databases treat NULLs specially; consider
		# adding application-level checks if necessary.
		unique_together = ('evento', 'sessao', 'membro', 'convidado_email')
		verbose_name = 'Participação em Evento'
		verbose_name_plural = 'Participações em Eventos'


class EventoSessao(models.Model):
	"""Represents a single day/session of a multi-day Evento.

	Created automatically when an Evento is saved (see post_save signal below).
	"""
	evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='sessoes')
	numero = models.PositiveIntegerField(help_text='Número da sessão (1..N)')
	data_inicio = models.DateTimeField()
	data_fim = models.DateTimeField(blank=True, null=True)

	class Meta:
		ordering = ['evento', 'numero']
		unique_together = ('evento', 'numero')

	def __str__(self):
		return f"{self.evento.titulo} - Dia {self.numero} ({self.data_inicio:%d/%m/%Y})"


# Signal: quando um Evento é criado/atualizado, garante que as sessoes existam
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta, datetime
from django.utils import timezone


@receiver(post_save, sender=Evento)
def criar_sessoes_evento(sender, instance, created, **kwargs):
	"""Gera uma sessão por dia com base em `quantidade_dias` e `data_inicio`.

	Se as sessões já existirem para esse evento, não recriamos (evita perda de
	dados de presença). Caso queira forçar a recriação, remova as sessões
	existentes antes.
	"""
	if not instance.data_inicio:
		return
	# número de sessões que deveria existir
	total = max(1, instance.quantidade_dias or 1)
	existing = {s.numero: s for s in instance.sessoes.all()}
	for i in range(1, total + 1):
		if i in existing:
			# já existe, pular
			continue
		# calcular data_inicio da sessão i (offset de i-1 dias)
		session_start = instance.data_inicio + timedelta(days=(i - 1))
		# determinar data_fim: se hora_termino estiver setada, combine a data com hora
		if instance.hora_termino:
			try:
				# mantém timezone
				dt = session_start
				end_dt = datetime.combine(dt.date(), instance.hora_termino)
				if timezone.is_aware(dt):
					# interpretar end_dt na mesma timezone de data_inicio
					end_dt = timezone.make_aware(end_dt, timezone.get_current_timezone())
			except Exception:
				end_dt = session_start + timedelta(hours=3)
		else:
			end_dt = session_start + timedelta(hours=3)
		EventoSessao.objects.create(evento=instance, numero=i, data_inicio=session_start, data_fim=end_dt)
