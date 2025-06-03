from django.db import models
from django.apps import apps
from django.utils import timezone
import uuid # Para nomes de arquivo únicos
import os   # Para manipulação de caminhos
from configuracao.models import Igreja # <--- ADICIONE ESTA LINHA

# --- Modelo Tiposstatus ---
class Tiposstatus(models.Model):
    status = models.CharField(
        max_length=50,
        unique=True, # Boa prática: Garante que não haja status duplicados
        verbose_name="Nome do Status" # Adiciona um nome mais amigável
    )
    # --- NOVO CAMPO ---
    considerar_ativo_relatorios = models.BooleanField(
        default=True, # Por padrão, status são considerados ativos para relatórios
        verbose_name="Considerar Ativo para Relatórios?",
        help_text="Marque se membros com este status devem ser incluídos nas contagens e gráficos gerais (Ex: Ativo). Desmarque para status como 'Inativo', 'Falecido', 'Transferido'."
    )
    # --- FIM NOVO CAMPO ---

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = "Tipo de Status"
        verbose_name_plural = "Tipos de Status"
        ordering = ['status'] # Ordenar alfabeticamente por padrão

# --- Função para upload_to da foto do Membro ---
def get_membro_foto_upload_path(instance, filename):
    """ Gera um caminho de upload único para as fotos dos membros. """
    ext = os.path.splitext(filename)[1] # Pega a extensão .jpg, .png, etc.
    unique_filename = f"membro_{instance.chave_or_uuid}_{uuid.uuid4().hex}{ext}"
    # Organiza as fotos em uma pasta por ID da igreja e depois por ID do membro (ou UUID se novo)
    return os.path.join('fotos_membros', f'igreja_{instance.igreja_id or "sem_igreja"}', unique_filename)





class Membro(models.Model):
    # Removido db_column='Chave' - Deixe o Django gerenciar o nome da coluna
    chave = models.AutoField(primary_key=True)

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
    cpf = models.CharField(max_length=14, blank=True, null=True, unique=True) # CPF deve ser único se preenchido
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
    complemento = models.CharField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    data_entrada = models.DateField(default=timezone.now, blank=True, null=True) # Usar default=timezone.now?
    status = models.ForeignKey(
        Tiposstatus,
        on_delete=models.SET_NULL, # Mantendo SET_NULL conforme seu modelo original
        blank=True,
        null=True,
        related_name='membros',
        verbose_name="Status Atual" # Adicionando verbose_name
    )
    foto = models.ImageField(
        upload_to=get_membro_foto_upload_path,
        null=True, blank=True,
        verbose_name="Foto do Membro"
    )
    # --- FIM NOVO CAMPO FOTO ---
    conjuge = models.CharField(max_length=100, blank=True, null=True)
    data_casamento = models.DateField(blank=True, null=True)
    # Adicionar outros campos conforme necessário

    # --- PROPRIEDADE OPCIONAL (Útil para templates/admin) ---
    @property
    def is_ativo_para_relatorios(self):
        """Verifica se o status do membro permite inclusão em relatórios."""
        if self.status:
            return self.status.considerar_ativo_relatorios
        # Defina o comportamento padrão se o membro não tiver status
        # False é geralmente mais seguro para relatórios
        return False
    # --- FIM PROPRIEDADE ---
    
    def save(self, *args, **kwargs):
        # Usado pela função de upload para ter um identificador antes do PK ser gerado
        self.chave_or_uuid = self.chave or uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Membro"
        verbose_name_plural = "Membros"
        ordering = ['nome'] # Ordenar por nome por padrão


class Cargos(models.Model):
    cargo = models.TextField(unique=True, blank=True, null=True)

    class Meta:
        # managed = False # Descomente se o Django NÃO deve gerenciar esta tabela
        db_table = 'cargos'
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"

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


class MembrosCargos(models.Model):
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE, blank=True, null=True)
    cargo = models.ForeignKey(Cargos, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'membros_cargos'
        verbose_name = "Cargo do Membro"
        verbose_name_plural = "Cargos dos Membros"
        unique_together = ('membro', 'cargo') # Evita duplicatas


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

class StatusHistorico(models.Model):
    membro = models.ForeignKey(Membro, on_delete=models.CASCADE)
    status_anterior = models.ForeignKey(Tiposstatus, related_name='status_anterior', on_delete=models.CASCADE)
    novo_status = models.ForeignKey(Tiposstatus, related_name='novo_status', on_delete=models.CASCADE)
    data_mudanca = models.DateTimeField(auto_now_add=True)

    class Meta:
        # managed = False # Se você quer que o Django gerencie, comente ou remova
        db_table = 'status_historico'
        verbose_name = "Histórico de Status"
        verbose_name_plural = "Históricos de Status"
        ordering = ['-data_mudanca'] # Ordenar por mais recente




#class Usuarios(models.Model):
 #   username = models.TextField(unique=True)
  #  password = models.TextField()

   # class Meta:
    #    db_table = 'usuarios' # NOME CORRETO DA TABELA
