from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from contas.constants import PASTOR_LOCAL, SECRETARIO_LOCAL, user_is_admin, user_tem_qualquer_grupo
from configuracao.models import Departamento, DepartamentoVinculo
from core.utils import get_igrejas_selecionaveis
from secretaria.models import Cargo, Pessoa


class DepartamentoVinculoService:
    """Unico ponto de escrita para equipes de departamentos locais."""

    @staticmethod
    def _validar_usuario_operador(usuario, igreja):
        """Valida a operacao local no escopo canônico da igreja derivada."""
        if not getattr(usuario, 'is_authenticated', False):
            raise ValidationError('Usuario sem autorizacao para operar a equipe.')
        if user_is_admin(usuario):
            raise ValidationError('A administracao ministerial possui acesso somente leitura.')
        if not user_tem_qualquer_grupo(usuario, [PASTOR_LOCAL, SECRETARIO_LOCAL]):
            raise ValidationError('Usuario sem autorizacao para operar a equipe.')
        if not get_igrejas_selecionaveis(
            usuario,
            ministerio=igreja.ministerio,
        ).filter(pk=igreja.pk).exists():
            raise ValidationError('Igreja fora do escopo permitido para operar a equipe.')

    @staticmethod
    def _objetos_bloqueados(departamento, membro, cargo=None):
        departamento = Departamento.objects.select_for_update().select_related(
            'igreja__ministerio'
        ).get(pk=departamento.pk)
        membro = Pessoa.objects.select_for_update().get(pk=membro.pk)
        cargo_bloqueado = None
        if cargo is not None:
            cargo_bloqueado = Cargo.objects.select_for_update().get(pk=cargo.pk)
        return departamento, membro, cargo_bloqueado

    @classmethod
    @transaction.atomic
    def adicionar(cls, *, departamento, membro, cargo=None, usuario, data_inicio=None):
        departamento, membro, cargo = cls._objetos_bloqueados(departamento, membro, cargo)
        cls._validar_usuario_operador(usuario, departamento.igreja)
        if not departamento.ativo:
            raise ValidationError('A equipe so pode ser alterada em departamento ativo.')
        if departamento.igreja_id != membro.igreja_id:
            raise ValidationError('Membro e departamento devem pertencer a mesma igreja.')
        if DepartamentoVinculo.objects.select_for_update().filter(
            departamento=departamento,
            membro=membro,
            data_fim__isnull=True,
        ).exists():
            raise ValidationError('Este membro ja possui vinculo ativo com o departamento.')

        try:
            return DepartamentoVinculo.objects.create(
                departamento=departamento,
                membro=membro,
                cargo=cargo,
                data_inicio=data_inicio or timezone.localdate(),
                criado_por=usuario,
            )
        except IntegrityError as exc:
            raise ValidationError('Este membro ja possui vinculo ativo com o departamento.') from exc

    @classmethod
    @transaction.atomic
    def encerrar(cls, *, vinculo, usuario, data_fim=None):
        vinculo = DepartamentoVinculo.objects.select_for_update().select_related(
            'departamento__igreja__ministerio', 'membro'
        ).get(pk=vinculo.pk)
        cls._validar_usuario_operador(usuario, vinculo.departamento.igreja)
        if vinculo.data_fim is not None:
            raise ValidationError('Este vinculo ja esta encerrado.')

        data_encerramento = data_fim or timezone.localdate()
        if data_encerramento < vinculo.data_inicio:
            raise ValidationError('A data de fim nao pode ser anterior a data de inicio.')
        vinculo.data_fim = data_encerramento
        vinculo.encerrado_por = usuario
        vinculo.save(update_fields=['data_fim', 'encerrado_por', 'updated_at'])
        return vinculo

    @classmethod
    @transaction.atomic
    def trocar_cargo(cls, *, vinculo, novo_cargo, usuario, data_troca=None):
        vinculo = DepartamentoVinculo.objects.select_for_update().select_related(
            'departamento__igreja__ministerio', 'membro'
        ).get(pk=vinculo.pk)
        cls._validar_usuario_operador(usuario, vinculo.departamento.igreja)
        data_troca = data_troca or timezone.localdate()
        cls.encerrar(vinculo=vinculo, usuario=usuario, data_fim=data_troca)
        return cls.adicionar(
            departamento=vinculo.departamento,
            membro=vinculo.membro,
            cargo=novo_cargo,
            usuario=usuario,
            data_inicio=data_troca,
        )
