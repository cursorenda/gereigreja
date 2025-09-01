from django.db import models
from django.utils import timezone # Adicionar este import
from django.utils import timezone
import uuid # Para nomes de arquivo únicos
import os   # Para manipulação de caminhos
from django.conf import settings # Para settings.AUTH_USER_MODEL
from configuracao.models import Igreja # <--- ADICIONE ESTA LINHA

import logging # Add this
logger = logging.getLogger(__name__) # Add this



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

class StatusPessoa(models.Model):
    nome = models.CharField(max_length=100, unique=True, help_text="Ex: Ativo, Inativo, Em Disciplina, Desligado, Transferido, Falecido")
    descricao = models.TextField(blank=True, null=True, help_text="Descrição adicional do status.")
    considerar_ativo_relatorios = models.BooleanField(
        default=True,
        help_text="Marque se pessoas com este status devem ser consideradas ativas em relatórios de membresia."
    )
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
    """ Gera um caminho de upload único para as fotos dos membros. """
    ext = os.path.splitext(filename)[1]
    # Cria um nome de arquivo único que não depende do PK do objeto.
    unique_filename = f"membro_foto_{uuid.uuid4().hex}{ext}"
    # Organiza em uma pasta pela igreja, se disponível.
    igreja_folder = f'igreja_{instance.igreja_id}' if instance.igreja_id else 'sem_igreja'
    return os.path.join('fotos_membros', igreja_folder, unique_filename)


class Membro(models.Model):
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
    telefone = models.CharField(max_length=15, blank=True, null=True) # Adicionar máscara JS no template
    data_entrada = models.DateField(default=timezone.now, blank=True, null=True) # Usar default=timezone.now?
    # O campo 'status' antigo foi removido.

    foto = models.ImageField(
        upload_to='fotos_membros/%Y/%m/%d/',
        null=True, blank=True,
        verbose_name="Foto do Membro"
    )

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

    # --- PROPRIEDADE OPCIONAL (Útil para templates/admin) ---
    @property
    def is_ativo_para_relatorios(self):
        """Verifica se o status_pessoa do membro permite inclusão em relatórios.""" # noqa: E501
        if self.status_pessoa: # Agora verifica o novo campo
            return self.status_pessoa.considerar_ativo_relatorios

        # Defina o comportamento padrão se o membro não tiver status
        # False é geralmente mais seguro para relatórios
        return False
    @property
    def nome_completo(self):
        """Retorna o nome completo do membro."""
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
        # logger.debug(f"Membro __init__ for {self.pk} ({self.nome_completo if self.pk else 'NEW'}): orig_tipo_id={self._original_tipo_pessoa_id}, orig_status_id={self._original_status_pessoa_id}") # noqa: E501


    
    def save(self, *args, **kwargs):
        current_user = kwargs.pop('user', None) # Espera um 'user' opcional de kwargs
        is_new = self._state.adding
        logger.debug(f"Membro SAVE for {self.pk}/{self.nome_completo if self.pk else 'NEW'}. is_new: {is_new}")
        logger.debug(f"  Current tipo_id: {self.tipo_pessoa_id}, Original tipo_id: {self._original_tipo_pessoa_id}")
        logger.debug(f"  Current status_id: {self.status_pessoa_id}, Original status_id: {self._original_status_pessoa_id}")

        changed_tipo = not is_new and self.tipo_pessoa_id != self._original_tipo_pessoa_id
        changed_status = not is_new and self.status_pessoa_id != self._original_status_pessoa_id

        logger.debug(f"  changed_tipo: {changed_tipo}, changed_status: {changed_status}")

        tipo_anterior_obj = None
        status_anterior_obj = None

        if not is_new:
            if changed_tipo and self._original_tipo_pessoa_id:
                
                
                try:
                    tipo_anterior_obj = TipoPessoa.objects.get(pk=self._original_tipo_pessoa_id)
                    logger.debug(f"  Fetched tipo_anterior_obj: {tipo_anterior_obj}")
                except TipoPessoa.DoesNotExist:
                    logger.warning(f"  TipoPessoa with pk={self._original_tipo_pessoa_id} not found for tipo_anterior_obj.") # noqa: E501
            if changed_status and self._original_status_pessoa_id:
                try:
                    status_anterior_obj = StatusPessoa.objects.get(pk=self._original_status_pessoa_id)
                    logger.debug(f"  Fetched status_anterior_obj: {status_anterior_obj}")
                except StatusPessoa.DoesNotExist:
                    logger.warning(f"  StatusPessoa with pk={self._original_status_pessoa_id} not found for status_anterior_obj.") # noqa: E501


        # A linha self.chave_or_uuid = self.chave or uuid.uuid4().hex foi removida.
        super().save(*args, **kwargs)

         # --- ADICIONAR LÓGICA PARA CRIAR StatusHistorico ---
        if is_new or changed_tipo or changed_status:
            logger.debug(f"  Creating StatusHistorico. is_new={is_new}, changed_tipo={changed_tipo}, changed_status={changed_status}") # noqa: E501
            
            observ_parts = []
            if is_new:
                observ_parts.append("Registro inicial do membro.")
                if self.tipo_pessoa: observ_parts.append(f"Tipo definido como '{self.tipo_pessoa.nome}'.")
                if self.status_pessoa: observ_parts.append(f"Status definido como '{self.status_pessoa.nome}'.")
            else:
                if changed_tipo:
                    old_tipo_name = tipo_anterior_obj.nome if tipo_anterior_obj else "Nenhum"
                    new_tipo_name = self.tipo_pessoa.nome if self.tipo_pessoa else "Nenhum"
                    observ_parts.append(f"Tipo alterado de '{old_tipo_name}' para '{new_tipo_name}'.")
                if changed_status:
                    old_status_name = status_anterior_obj.nome if status_anterior_obj else "Nenhum"
                    new_status_name = self.status_pessoa.nome if self.status_pessoa else "Nenhum"
                    observ_parts.append(f"Status alterado de '{old_status_name}' para '{new_status_name}'.")
            
            final_observacao = " ".join(observ_parts) if observ_parts else "Alteração de tipo/status registrada."

            try:
                StatusHistorico.objects.create(
                    membro=self,
                    tipo_pessoa_anterior=tipo_anterior_obj if not is_new else None,
                    tipo_pessoa_novo=self.tipo_pessoa,
                    status_pessoa_anterior=status_anterior_obj if not is_new else None,
                    status_pessoa_novo=self.status_pessoa,
                    registrado_por=current_user,
                    observacao=final_observacao
                )
                logger.info(f"  StatusHistorico created for membro {self.pk} ({self.nome_completo})")
            except Exception as e:
                logger.error(f"  Error creating StatusHistorico for membro {self.pk} ({self.nome_completo}): {e}", exc_info=True) # noqa: E501

        # --- FIM DA LÓGICA PARA CRIAR StatusHistorico ---
        # Atualiza os valores originais para a próxima comparação de save
        # ESTA PARTE É CRUCIAL PARA QUE O HISTÓRICO FUNCIONE EM SAVES SUBSEQUENTES
        self._original_tipo_pessoa_id = self.tipo_pessoa_id
        self._original_status_pessoa_id = self.status_pessoa_id
        # logger.debug(f"Membro SAVE end for {self.pk}: new orig_tipo_id={self._original_tipo_pessoa_id}, new orig_status_id={self._original_status_pessoa_id}") # noqa: E501


    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Membro"
        verbose_name_plural = "Membros"
        ordering = ['nome'] # Ordenar por nome por padrão
        indexes = [
            models.Index(fields=['nome'], name='nome_idx'),
            models.Index(fields=['cpf'], name='cpf_idx'),
            models.Index(fields=['igreja'], name='igreja_idx'), # Adicionei este índice
            models.Index(fields=['status_pessoa'], name='status_pessoa_idx'), # Adicionei este índice
            models.Index(fields=['tipo_pessoa'], name='tipo_pessoa_idx'), # Adicionei este índice
        ]


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
    data_transicao = models.DateTimeField(default=timezone.now) # MODIFICADO: Permite definir manualmente, default para agora
    observacao = models.TextField(blank=True, null=True)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-data_transicao']
