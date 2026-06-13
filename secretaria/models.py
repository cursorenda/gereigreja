

from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid # Para nomes de arquivo únicos
import os   # Para manipulação de caminhos
from configuracao.models import Igreja
import logging
logger = logging.getLogger(__name__)

# --- MODELO GLOBAL DE TAG ---
class Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True, help_text="Nome da tag (ex: pai, batizado, doente)")
    cor = models.CharField(max_length=7, default="#2196F3", help_text="Cor em hexadecimal (ex: #FF0000)")
    descricao = models.TextField(blank=True, null=True, help_text="Descrição opcional da tag.")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tag de Pessoa"
        verbose_name_plural = "Tags de Pessoas"
        ordering = ['nome']

# --- NOVOS MODELOS ---
class TipoPessoa(models.Model):
    nome = models.CharField(max_length=100, unique=True, help_text="Ex: Membro, Visitante, Obreiro, Congregado, Novo Convertido")
    descricao = models.TextField(blank=True, null=True, help_text="Descrição adicional do tipo de pessoa.")
    # Se os tipos de pessoa forem específicos por ministério, adicione uma ForeignKey para Ministerio aqui.
    # Por simplicidade inicial, vamos considerar globais.

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tipo de Pessoa"
        verbose_name_plural = "Tipos de Pessoas"
        ordering = ['nome']


# --- MODELO DE PRESENÇA DE VISITANTE EM EVENTO ---
class PresencaVisitanteEvento(models.Model):
    membro = models.ForeignKey('Membro', on_delete=models.CASCADE, related_name='presencas_eventos', null=True)
    evento = models.ForeignKey('eventos.Evento', on_delete=models.CASCADE, related_name='visitantes_presentes')
    data_registro = models.DateTimeField(default=timezone.now)
    responsavel_registro = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='presencas_visitantes_registradas')

    class Meta:
        verbose_name = 'Presença de Pessoa em Evento'
        verbose_name_plural = 'Presenças de Pessoas em Eventos'
        unique_together = ('membro', 'evento')
        ordering = ['-data_registro']

    def __str__(self):
        return f"{self.membro.nome} em {self.evento.titulo} ({self.data_registro:%d/%m/%Y %H:%M})"
class StatusPessoa(models.Model):
    nome = models.CharField(max_length=100, unique=True, help_text="Ex: Ativo, Inativo, Em Disciplina, Desligado, Transferido, Falecido")
    descricao = models.TextField(blank=True, null=True, help_text="Descrição adicional do status.")
    cor_associada = models.CharField(
        max_length=7, blank=True, null=True, help_text="Cor em hexadecimal (ex: #FF0000) para UI."
    )
    # Se os status forem específicos por ministério, adicione uma ForeignKey para Ministerio aqui.

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Status da Pessoa"
        verbose_name_plural = "Status das Pessoas"
        ordering = ['nome']



# --- Função para upload_to da foto do Membro ---
def get_membro_foto_upload_path(instance, filename):
    """ Gera um caminho de upload único para as fotos das pessoas. """
    ext = os.path.splitext(filename)[1]
    # Cria um nome de arquivo único que não depende do PK do objeto.
    unique_filename = f"pessoa_foto_{uuid.uuid4().hex}{ext}"
    # Organiza em uma pasta pela igreja, se disponível.
    igreja_folder = f'igreja_{instance.igreja_id}' if instance.igreja_id else 'sem_igreja'
    return os.path.join('fotos_pessoas', igreja_folder, unique_filename)


class Pessoa(models.Model):
    # Relacionamento com o usuário do sistema (caso exista)
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='membro_secretaria',
        verbose_name='Usuário do Sistema',
        help_text='Usuário do Django vinculado a este membro (opcional).'
    )
    # Removido db_column='Chave' - Deixe o Django gerenciar o nome da coluna
    chave = models.AutoField(primary_key=True)
    # O campo chave_or_uuid foi removido.


    # --- Campo ForeignKey para Igreja ---
    igreja = models.ForeignKey(
        Igreja, # Agora 'Igreja' é conhecido por causa do import
        on_delete=models.PROTECT,
        related_name='membros',
        verbose_name="Igreja"
    )
    # --- FIM ---
    nome = models.CharField(max_length=100)
    apelido = models.CharField(max_length=50, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True, unique=True)
    rg = models.CharField(max_length=20, blank=True, null=True)
    naturalidade = models.CharField(max_length=50, blank=True, null=True)
    nascimento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Feminino')], blank=True, null=True)
    estado_civil = models.CharField(max_length=20, choices=[('Solteiro', 'Solteiro'), ('Casado', 'Casado'), ('Divorciado', 'Divorciado'), ('Amasiado', 'Amasiado'), ('Viuvo', 'Viuvo')], blank=True, null=True)
    profissao = models.CharField(max_length=50, blank=True, null=True)
    escolaridade = models.CharField(max_length=50, choices=[('Ensino Fundamental Incompleto', 'Ensino Fundamental Incompleto'), ('Ensino Fundamental Completo', 'Ensino Fundamental Completo'), ('Ensino Médio Incompleto', 'Ensino Médio Incompleto'), ('Ensino Médio Completo', 'Ensino Médio Completo'), ('Ensino Superior Incompleto', 'Ensino Superior Incompleto'), ('Ensino Superior Completo', 'Ensino Superior Completo'), ('Pós-graduação', 'Pós-graduação'), ('Mestrado', 'Mestrado'), ('Sem Escolaridade', 'Sem Escolaridade'), ('Doutorado', 'Doutorado')], blank=True, null=True)
    nome_pai = models.CharField(max_length=100, blank=True, null=True)
    nome_mae = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True, null=True)
    pais = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    cidade = models.CharField(max_length=50, blank=True, null=True)
    bairro_distrito = models.CharField(max_length=50, blank=True, null=True)
    rua = models.CharField(max_length=100, blank=True, null=True)
    numero_casa = models.CharField(max_length=10, blank=True, null=True)
    nacionalidade = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nacionalidade") # NOVO CAMPO
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name="E-mail Pessoal") # NOVO CAMPO
    complemento = models.CharField(max_length=100, blank=True, null=True)
    # --- CAMPO TAGS ---
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='pessoas',
        verbose_name='Tags',
        help_text='Tags para segmentação flexível de membros (ex: batizado, líder, doente)'
    )
    # Grupo/Casa/Família: referenciar uma unidade residencial ou grupo familiar
    grupo_casa = models.ForeignKey(
        'GrupoCasa',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='pessoas',
        verbose_name='Grupo/Casa/Família',
        help_text='Vínculo opcional a um grupo/casa que agrega pessoas pelo mesmo endereço'
    )
    telefone = models.CharField(max_length=15, blank=True, null=True) # Adicionar máscara JS no template
    celular = models.CharField(max_length=15, blank=True, null=True, help_text="Celular com DDD")
    data_entrada = models.DateField(default=timezone.now, blank=True, null=True) # Usar default=timezone.now?

    # Sub status para membros inativos
    SUB_STATUS_INATIVO_CHOICES = [
        ('FALECIDO', 'Falecido'),
        ('MUDOU', 'Mudou (outro ministério ou denominação)'),
        ('TRANSFERIDO', 'Transferido (outra congregação do mesmo ministério)'),
    ]
    sub_status_inativo = models.CharField(
        max_length=20,
        choices=SUB_STATUS_INATIVO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Sub status (se inativo)",
        help_text="Preencha apenas se o status for inativo."
    )

    foto = models.ImageField(
        upload_to='fotos_pessoas/%Y/%m/%d/',
        null=True, blank=True,
        verbose_name="Foto da Pessoa"
    )
    # --- CAMPOS DE VISITANTE/ACOMPANHAMENTO ---
    data_primeira_visita = models.DateField(blank=True, null=True, verbose_name="Data da Primeira Visita")
    origem_visita = models.CharField(max_length=100, blank=True, null=True, verbose_name="Origem da Visita", help_text="Ex: Indicação, Redes Sociais, Evento, etc.")
    responsavel_acompanhamento = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='membros_acompanhados', verbose_name="Responsável pelo Acompanhamento")
    STATUS_ACOMPANHAMENTO_CHOICES = [
        ("novo_visitante", "Novo Visitante"),
        ("em_acompanhamento", "Em Acompanhamento"),
        ("retornou", "Retornou"),
        ("interessado_integracao", "Interessado em Integração"),
        ("convertido", "Convertido"),
        ("tornou_membro", "Tornou-se Membro"),
        ("nao_retornou", "Não Retornou"),
        ("encaminhado_ministerio", "Encaminhado para outro Ministério"),
        ("encerrado", "Encerrado")
    ]
    status_acompanhamento = models.CharField(max_length=30, choices=STATUS_ACOMPANHAMENTO_CHOICES, blank=True, null=True, verbose_name="Status do Acompanhamento")
    observacoes_visita = models.TextField(blank=True, null=True, verbose_name="Observações do Acompanhamento/Visita")

# --- NOVOS CAMPOS PARA TIPO E STATUS ---
    tipo_pessoa = models.ForeignKey(
        TipoPessoa,
        on_delete=models.PROTECT, # Alterado para PROTECT para evitar exclusão acidental
        null=False, # Tornando obrigatório
        blank=False, # Tornando obrigatório

        verbose_name="Tipo de Pessoa",
        related_name="membros"
    )
    status_pessoa = models.ForeignKey(
        StatusPessoa,
        on_delete=models.PROTECT, # Alterado para PROTECT
        null=False, # Tornando obrigatório
        blank=False, # Tornando obrigatório

        verbose_name="Status da Pessoa",
        related_name="membros_com_status"
    )

    # --- FIM NOVO CAMPO FOTO ---
    conjuge = models.CharField(max_length=100, blank=True, null=True)
    data_casamento = models.DateField(blank=True, null=True)
    # Adicionar outros campos conforme necessário

    # --- CAMPO TIPO DE ENTRADA (Somente para membros) ---
    TIPO_ENTRADA_CHOICES = [
        ('BATISMO', 'Batismo'),
        ('ACLAMACAO', 'Aclamação'),
        ('CARTA', 'Carta de Mudança'),
        ('OUTRO', 'Outro'),
    ]
    tipo_entrada = models.CharField(
        max_length=20,
        choices=TIPO_ENTRADA_CHOICES,
        blank=True, null=True,
        verbose_name="Tipo de Entrada (se membro)"
    )

    GRAU_ECLESIASTICO_CHOICES = [
        ('membro_comum', 'Membro Comum / Sem cargo ministerial'),
        ('diacono', 'Diácono / Diaconisa'),
        ('presbitero', 'Presbítero'),
        ('evangelista', 'Evangelista'),
        ('missionario', 'Missionário / Missionária'),
        ('pastor', 'Pastor / Pastora'),
    ]
    grau_eclesiastico = models.CharField(
        max_length=30,
        choices=GRAU_ECLESIASTICO_CHOICES,
        default=None,
        blank=True,
        null=True,
        verbose_name='Grau Eclesiástico'
    )
    
    # --- CAMPOS DE AUDITORIA ---
    criado_em = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
        verbose_name="Data/Hora de Cadastro",
        help_text="Data e hora em que a pessoa foi cadastrada no sistema"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
        verbose_name="Última Atualização",
        help_text="Data e hora da última modificação do cadastro"
    )
    # --- FIM CAMPOS DE AUDITORIA ---
    
    # Propriedade removida: agora a lógica de ativo para relatórios depende apenas de status_pessoa.nome == 'Ativo'
    @property
    def nome_completo(self):
        """Retorna o nome completo da pessoa."""
        parts = [self.nome]
        # Adicione outras partes do nome se existirem, ex: self.sobrenome
        # if self.sobrenome:
        #     parts.append(self.sobrenome)
        return " ".join(filter(None, parts))

    # --- FIM PROPRIEDADE ---

    _original_tipo_pessoa_id = None # Adicionado para rastrear tipo anterior

    def __init__(self, *args, **kwargs): # Adicionado __init__
        super().__init__(*args, **kwargs)
        # Armazena os valores originais ao carregar o objeto do banco
        self._original_tipo_pessoa_id = self.tipo_pessoa_id
        self._original_status_pessoa_id = self.status_pessoa_id


    
    def save(self, *args, **kwargs):
        current_user = kwargs.pop('user', None) # Espera um 'user' opcional de kwargs
        data_mudanca_tipo = kwargs.pop('data_mudanca_tipo', None) # Data customizada para mudança de tipo
        data_mudanca_status = kwargs.pop('data_mudanca_status', None) # Data customizada para mudança de status
        motivo_transicao = (kwargs.pop('motivo_transicao', '') or '').strip()

        tipo_nome_normalizado = ''
        if self.tipo_pessoa_id:
            try:
                tipo_nome_normalizado = (self.tipo_pessoa.nome or '').strip().lower()
            except Exception:
                tipo_nome_normalizado = ''

        if tipo_nome_normalizado and tipo_nome_normalizado != 'membro':
            self.grau_eclesiastico = None
        elif not self.grau_eclesiastico:
            self.grau_eclesiastico = 'membro_comum'

        is_new = self._state.adding
        changed_tipo = not is_new and self.tipo_pessoa_id != self._original_tipo_pessoa_id
        changed_status = not is_new and self.status_pessoa_id != self._original_status_pessoa_id
        changed_entrada = not is_new and hasattr(self, '_original_tipo_entrada') and self.tipo_entrada != self._original_tipo_entrada

        tipo_anterior_obj = None
        status_anterior_obj = None
        entrada_anterior = getattr(self, '_original_tipo_entrada', None)

        if not is_new:
            if changed_tipo and self._original_tipo_pessoa_id:
                try:
                    tipo_anterior_obj = TipoPessoa.objects.get(pk=self._original_tipo_pessoa_id)
                except TipoPessoa.DoesNotExist:
                    tipo_anterior_obj = None
            if changed_status and self._original_status_pessoa_id:
                try:
                    status_anterior_obj = StatusPessoa.objects.get(pk=self._original_status_pessoa_id)
                except StatusPessoa.DoesNotExist:
                    status_anterior_obj = None

        super().save(*args, **kwargs)

        # --- ADICIONAR LÓGICA PARA CRIAR StatusHistorico ---
        if is_new or changed_tipo or changed_status or changed_entrada:
            observ_parts = []
            if is_new:
                observ_parts.append("Registro inicial da pessoa.")
                if self.tipo_pessoa: observ_parts.append(f"Tipo definido como '{self.tipo_pessoa.nome}'.")
                if self.status_pessoa: observ_parts.append(f"Status definido como '{self.status_pessoa.nome}'.")
                if self.tipo_entrada: observ_parts.append(f"Tipo de entrada: '{self.get_tipo_entrada_display()}'.")
            else:
                if changed_tipo:
                    old_tipo_name = tipo_anterior_obj.nome if tipo_anterior_obj else "Nenhum"
                    new_tipo_name = self.tipo_pessoa.nome if self.tipo_pessoa else "Nenhum"
                    observ_parts.append(f"Tipo alterado de '{old_tipo_name}' para '{new_tipo_name}'.")
                if changed_status:
                    old_status_name = status_anterior_obj.nome if status_anterior_obj else "Nenhum"
                    new_status_name = self.status_pessoa.nome if self.status_pessoa else "Nenhum"
                    observ_parts.append(f"Status alterado de '{old_status_name}' para '{new_status_name}'.")
                if changed_entrada:
                    old_entrada = dict(self.TIPO_ENTRADA_CHOICES).get(entrada_anterior, entrada_anterior) or "Nenhum"
                    new_entrada = self.get_tipo_entrada_display() or "Nenhum"
                    observ_parts.append(f"Tipo de entrada alterado de '{old_entrada}' para '{new_entrada}'.")

            final_observacao = " ".join(observ_parts) if observ_parts else "Alteração registrada."
            if motivo_transicao:
                final_observacao = f"{final_observacao} Motivo informado: {motivo_transicao}"

            # Determina a data da transição
            # - Se houver apenas mudança de tipo: usa data_mudanca_tipo
            # - Se houver apenas mudança de status: usa data_mudanca_status
            # - Se houver ambas e as duas datas existirem: usa a mais recente
            data_transicao_final = None
            from datetime import datetime, time

            def _to_datetime(value):
                if not value:
                    return None
                if isinstance(value, datetime):
                    return value
                return datetime.combine(value, time(12, 0))

            dt_tipo = _to_datetime(data_mudanca_tipo) if changed_tipo else None
            dt_status = _to_datetime(data_mudanca_status) if changed_status else None

            # Regra hibrida de governanca de datas:
            # - primeira mudanca pode ficar sem data
            # - apos existir data historica registrada, mudancas sem data assumem hoje
            has_tipo_date_registered = False
            has_status_date_registered = False
            if changed_tipo and not dt_tipo:
                has_tipo_date_registered = StatusHistorico.objects.filter(
                    membro=self,
                    tipo_pessoa_anterior__isnull=False,
                    tipo_pessoa_novo__isnull=False,
                    data_transicao__isnull=False,
                ).exists()
                if has_tipo_date_registered:
                    dt_tipo = _to_datetime(timezone.localdate())

            if changed_status and not dt_status:
                has_status_date_registered = StatusHistorico.objects.filter(
                    membro=self,
                    status_pessoa_anterior__isnull=False,
                    status_pessoa_novo__isnull=False,
                    data_transicao__isnull=False,
                ).exists()
                if has_status_date_registered:
                    dt_status = _to_datetime(timezone.localdate())

            if dt_tipo and dt_status:
                data_transicao_final = dt_tipo if dt_tipo >= dt_status else dt_status
            elif dt_tipo:
                data_transicao_final = dt_tipo
            elif dt_status:
                data_transicao_final = dt_status

            try:
                historico_kwargs = {
                    'membro': self,
                    'tipo_pessoa_anterior': tipo_anterior_obj if not is_new else None,
                    'tipo_pessoa_novo': self.tipo_pessoa,
                    'status_pessoa_anterior': status_anterior_obj if not is_new else None,
                    'status_pessoa_novo': self.status_pessoa,
                    'registrado_por': current_user,
                    'observacao': final_observacao
                }
                # Adiciona data_transicao só se fornecida
                if data_transicao_final:
                    historico_kwargs['data_transicao'] = data_transicao_final
                
                StatusHistorico.objects.create(**historico_kwargs)
            except Exception as e:
                logger.error(f"  Error creating StatusHistorico for pessoa {self.pk} ({self.nome_completo}): {e}", exc_info=True)

        # Atualiza os valores originais para a próxima comparação de save
        self._original_tipo_pessoa_id = self.tipo_pessoa_id
        self._original_status_pessoa_id = self.status_pessoa_id
        self._original_tipo_entrada = self.tipo_entrada


    def __str__(self):
        return self.nome

# Compatibilidade: manter a classe `Membro` como proxy para permitir
# que código existente que importa/usa `Membro` continue funcionando
# enquanto migramos referências para `Pessoa` de forma incremental.
class Membro(Pessoa):
    class Meta:
        proxy = True
        verbose_name = "Membro (compat)"
        verbose_name_plural = "Membros (compat)"


# --- Modelo para agrupar pessoas que moram no mesmo endereço / família / casa ---
class GrupoCasa(models.Model):
    igreja = models.ForeignKey(
        Igreja,
        on_delete=models.PROTECT,
        related_name='grupos_casa',
        verbose_name='Igreja'
    )
    nome = models.CharField(max_length=150, blank=True, null=True, help_text='Nome do grupo/casa ou responsável (opcional)')
    rua = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=50, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True, null=True)
    referencia = models.TextField(blank=True, null=True)
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   help_text='Usuário responsável por este grupo/casa (pastor/líder)')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Grupo / Casa / Família'
        verbose_name_plural = 'Grupos / Casas / Famílias'
        unique_together = (('igreja','rua','numero','complemento','cep'),)
        indexes = [
            models.Index(fields=['igreja','rua','numero','cep']),
        ]

    def __str__(self):
        if self.nome:
            return f"{self.nome} ({self.rua or ''} {self.numero or ''})"
        return f"{self.rua or 'Endereço não informado'} {self.numero or ''}"


class VisitaGrupoCasa(models.Model):
    grupo_casa = models.ForeignKey(GrupoCasa, on_delete=models.CASCADE, related_name='visitas')
    data = models.DateTimeField(default=timezone.now)
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    tipo = models.CharField(max_length=50, choices=[('visita','Visita'),('ligacao','Ligação'),('outro','Outro')], default='visita')
    resultado = models.CharField(max_length=100, blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)
    num_membros = models.PositiveIntegerField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Visita por Grupo/Casa'
        verbose_name_plural = 'Visitas por Grupo/Casa'

    def __str__(self):
        return f"Visita {self.grupo_casa} em {self.data:%d/%m/%Y %H:%M}"


# --- MODELOS DE CARGO E VÍNCULO ---
from django.contrib.auth.models import Group

class Cargo(models.Model):

    nome = models.CharField(max_length=100, unique=True)
    grupo_permissao = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL)
    is_ebd = models.BooleanField(
        default=False,
        verbose_name="É da EBD?",
        help_text="Marque se este cargo pertence à Escola Bíblica Dominical."
    )

    def __str__(self):
        return self.nome

class MembroCargo(models.Model):
    membro = models.ForeignKey('Membro', on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.membro} - {self.cargo} ({self.data_inicio} a {self.data_fim or 'atual'})"
    
    class Meta:
        verbose_name = "Membro"
        verbose_name_plural = "Membros"



class Contatos(models.Model):
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE, blank=True, null=True)
    telefone_principal = models.TextField(blank=True, null=True)
    telefone_alternativo = models.TextField(blank=True, null=True)
    whatsapp = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    contato_emergencia_nome = models.TextField(blank=True, null=True)
    contato_emergencia_telefone = models.TextField(blank=True, null=True)
    contato_emergencia_parentesco = models.TextField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'contatos'
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"

class Eventos(models.Model):
    nome_evento = models.TextField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    data = models.DateField(blank=True, null=True)
    horario = models.TimeField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'eventos'
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"

class EventosParticipacao(models.Model):
    evento = models.ForeignKey(Eventos, on_delete=models.CASCADE, blank=True, null=True)
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE, blank=True, null=True)
    status_presenca = models.TextField(blank=True, null=True)
    justificativa = models.TextField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'eventos_participacao'
        verbose_name = "Participação em Evento"
        verbose_name_plural = "Participações em Eventos"


class Familia(models.Model):
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE, to_field='chave', blank=True, null=True)
    conjuge = models.TextField(blank=True, null=True)
    data_casamento = models.DateField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'familia'
        verbose_name = "Família (Cônjuge)"
        verbose_name_plural = "Famílias (Cônjuges)"


class Filhos(models.Model):
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE, blank=True, null=True)
    nome = models.TextField(blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    frequenta_igreja = models.BooleanField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'filhos'
        verbose_name = "Filho"
        verbose_name_plural = "Filhos"

#class Igrejas(models.Model):

# --- Modelo para eventos da linha do tempo dos membros ---
class TimelineEvent(models.Model):
    TIPO_EVENTO_CHOICES = [
        ("entrada", "Entrada"),
        ("mudanca_tipo", "Mudança de Tipo"),
        ("mudanca_status", "Mudança de Status"),
        ("outro", "Outro"),
    ]

    membro = models.ForeignKey('Membro', on_delete=models.CASCADE, related_name='eventos_linha_tempo')
    data = models.DateTimeField()
    tipo_evento = models.CharField(max_length=30, choices=TIPO_EVENTO_CHOICES)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f"{self.data:%d/%m/%Y} - {self.membro} - {self.get_tipo_evento_display()}"
 #   nome = models.TextField(blank=True, null=True)
  #  tipo = models.TextField(blank=True, null=True)
   # endereco = models.TextField(blank=True, null=True)
    #telefone = models.TextField(blank=True, null=True)
    #email = models.TextField(blank=True, null=True)
    #cnpj = models.TextField(blank=True, null=True)
    #logo = models.BinaryField(blank=True, null=True)
    #igreja_pai = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    #class Meta:
    #    db_table = 'igrejas' # NOME CORRETO DA TABELA

class InfoEclesiastica(models.Model):
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE, to_field='chave', blank=True, null=True)
    data_conversao = models.DateField(blank=True, null=True)
    data_batismo = models.DateField(blank=True, null=True)
    igreja_origem = models.TextField(blank=True, null=True)
    data_admissao = models.DateField(blank=True, null=True)
    forma_admissao = models.TextField(blank=True, null=True)
    ministerios = models.TextField(blank=True, null=True)
    dons_talentos = models.TextField(blank=True, null=True)
    tipo_membro = models.TextField(blank=True, null=True)
    cargo = models.TextField(blank=True, null=True)
    disponibilidade = models.TextField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'info_eclesiastica'
        verbose_name = "Informação Eclesiástica"
        verbose_name_plural = "Informações Eclesiásticas"




class Observacoes(models.Model):
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE, to_field='chave', blank=True, null=True)
    necessidades_especiais = models.TextField(blank=True, null=True)
    observacoes_medicas = models.TextField(blank=True, null=True)
    alergias = models.TextField(blank=True, null=True)
    observacoes_gerais = models.TextField(blank=True, null=True) # Mantido
    # caminho_foto = models.TextField(blank=True, null=True) # REMOVIDO - Foto agora está no modelo Membro
    caminho_documentos = models.TextField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'observacoes'
        verbose_name = "Observação"
        verbose_name_plural = "Observações"

class OutrosFamiliares(models.Model):
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE, blank=True, null=True)
    nome = models.TextField(blank=True, null=True)
    parentesco = models.TextField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'outros_familiares'
        verbose_name = "Outro Familiar"
        verbose_name_plural = "Outros Familiares"


# REMOVER ESTA DEFINIÇÃO ANTIGA DE StatusHistorico
# class StatusHistorico(models.Model):
#     membro = models.ForeignKey(Membro, on_delete=models.CASCADE)
#     status_anterior = models.ForeignKey(Tiposstatus, related_name='status_anterior', on_delete=models.CASCADE)
#     novo_status = models.ForeignKey(Tiposstatus, related_name='novo_status', on_delete=models.CASCADE)
#     data_mudanca = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         # managed = False # Se você quer que o Django gerencie, comente ou remova
#         db_table = 'status_historico'
#         verbose_name = "Histórico de Status"
#         verbose_name_plural = "Históricos de Status"
#         ordering = ['-data_mudanca'] # Ordenar por mais recente



from django.conf import settings # Movido para perto da classe que o usa



class StatusHistorico(models.Model):
    # Esta é a definição CORRETA de StatusHistorico
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE, related_name='transicoes_status_secretaria') # related_name usado no template
    tipo_pessoa_anterior = models.ForeignKey(TipoPessoa, null=True, blank=True, on_delete=models.SET_NULL, related_name='historico_tipo_anterior')
    tipo_pessoa_novo = models.ForeignKey(TipoPessoa, null=True, blank=True, on_delete=models.SET_NULL, related_name='historico_tipo_novo')
    status_pessoa_anterior = models.ForeignKey(StatusPessoa, null=True, blank=True, on_delete=models.SET_NULL, related_name='historico_status_anterior')
    status_pessoa_novo = models.ForeignKey(StatusPessoa, null=True, blank=True, on_delete=models.SET_NULL, related_name='historico_status_novo')
    data_transicao = models.DateTimeField(null=True, blank=True, default=None)
    observacao = models.TextField(blank=True, null=True)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-data_transicao']


# --- MODELO DE ACOMPANHAMENTO DE VISITA ---
class AcompanhamentoVisita(models.Model):
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE, related_name='acompanhamentos_visita')
    data = models.DateTimeField(default=timezone.now)
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='acompanhamentos_realizados')
    # Referência opcional a uma visita registrada por GrupoCasa
    visita_grupo_casa = models.ForeignKey('VisitaGrupoCasa', null=True, blank=True, on_delete=models.SET_NULL, related_name='acompanhamentos')
    tipo_contato = models.CharField(max_length=50, choices=[
        ("ligacao", "Ligação"),
        ("visita", "Visita"),
        ("mensagem", "Mensagem"),
        ("evento", "Evento"),
        ("outro", "Outro")
    ], default="outro")
    resultado = models.CharField(max_length=100, blank=True, null=True, help_text="Ex: Compareceu, Não respondeu, Interessado, etc.")
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-data']
        verbose_name = "Acompanhamento de Visita"
        verbose_name_plural = "Acompanhamentos de Visita"

    def __str__(self):
        return f"{self.membro} - {self.get_tipo_contato_display()} em {self.data:%d/%m/%Y}"


class TransferenciaMembro(models.Model):
    STATUS_AGUARDANDO = 'aguardando'
    STATUS_APROVADA = 'aprovada'
    STATUS_RECUSADA = 'recusada'
    STATUS_CANCELADA = 'cancelada'

    STATUS_CHOICES = [
        (STATUS_AGUARDANDO, 'Aguardando aprovação'),
        (STATUS_APROVADA, 'Aprovada'),
        (STATUS_RECUSADA, 'Recusada'),
        (STATUS_CANCELADA, 'Cancelada'),
    ]

    membro = models.ForeignKey(
        Membro,
        on_delete=models.CASCADE,
        related_name='transferencias',
    )
    igreja_origem = models.ForeignKey(
        Igreja,
        on_delete=models.PROTECT,
        related_name='transferencias_saida',
    )
    igreja_destino = models.ForeignKey(
        Igreja,
        on_delete=models.PROTECT,
        related_name='transferencias_entrada',
    )
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    usuario_solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='transferencias_solicitadas',
    )
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    usuario_aprovador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transferencias_aprovadas',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AGUARDANDO)
    motivo = models.CharField(max_length=255, blank=True)
    observacao = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Transferência de Membro'
        verbose_name_plural = 'Transferências de Membros'
        ordering = ['-data_solicitacao']
        permissions = [
            ('transferir_membro', 'Pode solicitar transferência de membro para outra igreja do mesmo ministério'),
            ('aprovar_transferencia_membro', 'Pode aprovar ou recusar transferência de membro para sua igreja'),
        ]

    def __str__(self):
        return f"{self.membro} de {self.igreja_origem} para {self.igreja_destino} ({self.get_status_display()})"
