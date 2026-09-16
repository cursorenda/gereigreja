from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from configuracao.models import Departamento, DepartamentoCapacidade, DepartamentoMinisterial


class DepartamentoGestaoService:
    """Centraliza mutações das definições ministeriais e instâncias locais."""

    CODIGOS_TECNICOS = {'LOCAL', 'EVENTOS'}

    @staticmethod
    def _codigo_normalizado(codigo):
        codigo = (codigo or '').strip().upper().replace(' ', '_')
        if not codigo:
            raise ValidationError('Informe um código para o departamento ministerial.')
        return codigo

    @classmethod
    def _validar_definicao_no_ministerio(cls, definicao, ministerio):
        if definicao.ministerio_id != ministerio.id:
            raise ValidationError('Departamento ministerial fora do Ministério em contexto.')

    @staticmethod
    def _validar_departamento_na_igreja(departamento, igreja):
        if departamento.igreja_id != igreja.id:
            raise ValidationError('Departamento fora da igreja em contexto.')

    @classmethod
    @transaction.atomic
    def criar_definicao_ministerial(cls, *, ministerio, dados):
        codigo = cls._codigo_normalizado(dados.get('codigo'))
        if DepartamentoMinisterial.objects.filter(ministerio=ministerio, codigo=codigo).exists():
            raise ValidationError('Já existe um departamento ministerial com este código.')

        try:
            return DepartamentoMinisterial.objects.create(
                ministerio=ministerio,
                codigo=codigo,
                nome=dados['nome'],
                ativo=dados.get('ativo', False),
                ordem=dados.get('ordem', 100),
            )
        except IntegrityError as exc:
            raise ValidationError('Já existe um departamento ministerial com este código.') from exc

    @classmethod
    @transaction.atomic
    def atualizar_definicao_ministerial(cls, *, definicao, ministerio, dados):
        cls._validar_definicao_no_ministerio(definicao, ministerio)
        definicao = DepartamentoMinisterial.objects.select_for_update().get(pk=definicao.pk)
        cls._validar_definicao_no_ministerio(definicao, ministerio)

        codigo = cls._codigo_normalizado(dados.get('codigo'))
        if DepartamentoMinisterial.objects.filter(ministerio=ministerio, codigo=codigo).exclude(
            pk=definicao.pk
        ).exists():
            raise ValidationError('Já existe um departamento ministerial com este código.')

        definicao.codigo = codigo
        definicao.nome = dados['nome']
        definicao.ativo = dados.get('ativo', False)
        definicao.ordem = dados.get('ordem', 100)
        try:
            definicao.save(update_fields=['codigo', 'nome', 'ativo', 'ordem'])
        except IntegrityError as exc:
            raise ValidationError('Já existe um departamento ministerial com este código.') from exc
        return definicao

    @classmethod
    @transaction.atomic
    def confirmar_legado(cls, *, departamento, igreja):
        cls._validar_departamento_na_igreja(departamento, igreja)
        departamento = Departamento.objects.select_for_update().get(pk=departamento.pk)
        cls._validar_departamento_na_igreja(departamento, igreja)
        if (
            departamento.classificacao != Departamento.CLASSIFICACAO_LEGADO_SUGERIDO
            or departamento.departamento_ministerial_id is not None
        ):
            raise ValidationError('Departamento legado não encontrado para confirmação.')

        departamento.classificacao = Departamento.CLASSIFICACAO_ORGANIZACIONAL
        departamento.save(update_fields=['classificacao'])
        return departamento

    @classmethod
    @transaction.atomic
    def ativar_na_igreja(cls, *, definicao, igreja):
        cls._validar_definicao_no_ministerio(definicao, igreja.ministerio)
        if not definicao.ativo or definicao.codigo in cls.CODIGOS_TECNICOS:
            raise ValidationError('Definição ministerial indisponível para ativação local.')

        departamento = Departamento.objects.select_for_update().filter(
            igreja=igreja,
            departamento_ministerial=definicao,
        ).first()
        if departamento is not None:
            if departamento.ativo:
                return departamento, 'ja_ativo'
            departamento.ativo = True
            departamento.save(update_fields=['ativo', 'updated_at'])
            return departamento, 'reativado'

        colisao = Departamento.objects.select_for_update().filter(
            igreja=igreja,
            codigo_interno=definicao.codigo,
        ).first()
        pode_reutilizar = (
            colisao is not None
            and not colisao.departamento_ministerial_id
            and colisao.tipo_departamento == Departamento.TIPO_PADRAO
            and colisao.classificacao
            in {
                Departamento.CLASSIFICACAO_ORGANIZACIONAL,
                Departamento.CLASSIFICACAO_LEGADO_SUGERIDO,
            }
        )
        if colisao is not None and not pode_reutilizar:
            raise ValidationError('Ja existe um departamento local com este codigo. Nenhum dado foi alterado.')

        if pode_reutilizar:
            colisao.departamento_ministerial = definicao
            if not colisao.ativo:
                colisao.ativo = True
            colisao.full_clean()
            colisao.save(update_fields=['departamento_ministerial', 'ativo', 'updated_at'])
            return colisao, 'reutilizado'

        try:
            departamento = Departamento.objects.create(
                igreja=igreja,
                departamento_ministerial=definicao,
                codigo_interno=definicao.codigo,
                nome_exibicao=definicao.nome,
                tipo_departamento=Departamento.TIPO_PADRAO,
                classificacao=Departamento.CLASSIFICACAO_ORGANIZACIONAL,
                ativo=True,
                ordem_exibicao=definicao.ordem,
            )
        except IntegrityError:
            departamento = Departamento.objects.filter(
                igreja=igreja,
                departamento_ministerial=definicao,
            ).first()
            if departamento is None:
                raise ValidationError('Nao foi possivel ativar o departamento devido a um conflito de codigo local.')
            return departamento, 'ja_ativo'
        return departamento, 'criado'

    @classmethod
    @transaction.atomic
    def desativar_na_igreja(cls, *, departamento, igreja):
        cls._validar_departamento_na_igreja(departamento, igreja)
        departamento = Departamento.objects.select_for_update().get(pk=departamento.pk)
        cls._validar_departamento_na_igreja(departamento, igreja)
        if departamento.departamento_ministerial_id is None:
            raise ValidationError('Departamento ministerial não encontrado para desativação.')

        if departamento.ativo:
            departamento.ativo = False
            departamento.save(update_fields=['ativo', 'updated_at'])
        return departamento

    @classmethod
    @transaction.atomic
    def atualizar_capacidades(cls, *, departamento, igreja, capacidades):
        cls._validar_departamento_na_igreja(departamento, igreja)
        departamento = Departamento.objects.select_for_update().get(pk=departamento.pk)
        cls._validar_departamento_na_igreja(departamento, igreja)

        capacidades_ativas = set(capacidades or [])
        capacidades_validas = {
            codigo for codigo, _ in DepartamentoCapacidade.CAPACIDADE_CHOICES
        }
        invalidas = capacidades_ativas - capacidades_validas
        if invalidas:
            raise ValidationError('Capacidade inválida para o departamento.')

        for capacidade in capacidades_validas:
            DepartamentoCapacidade.objects.update_or_create(
                departamento=departamento,
                capacidade=capacidade,
                defaults={'ativa': capacidade in capacidades_ativas},
            )
        return departamento