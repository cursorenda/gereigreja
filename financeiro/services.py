import re
import hashlib
import json
import unicodedata
from hashlib import sha256
from datetime import datetime, timedelta
from calendar import monthrange
from decimal import Decimal, ROUND_HALF_UP
from xml.etree import ElementTree as ET

from django.db import IntegrityError, connection, transaction
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Sum, Q
from django.urls import reverse
from django.utils import timezone

from .models import (
    ContaPagar,
    ContaPagarAutorizacaoEvento,
    DepartamentoFinanceiro,
    Despesas,
    FechamentoCaixa,
    FundoDepartamental,
    ImportacaoExtratoOFX,
    LancamentoExtratoOFX,
    PoliticaDepartamentoFinanceiro,
    PoliticaFinanceiraIgreja,
    Receitas,
    RecorrenciaContaPagar,
)
from configuracao.models import Departamento, Igreja
from configuracao.models import PerfilUsuario
from contas.constants import TESOUREIRO
from contas.constants import user_has_permission_level_or_higher
from notificacoes.models import Notificacao
from .selectors import (
    categoria_receita_por_evento,
    obter_conta_evento_efetiva_id,
    obter_evento_no_escopo,
)
from .policies import FUNDO_EVENTOS, categoria_receita_padrao_por_fundo
from .authorization import can_approve_payable, get_finance_approval_scope


PAYABLE_FINGERPRINT_SCHEMA_VERSION = 1
PAYABLE_FINGERPRINT_PREFIX = 'v1:sha256:'


def build_payable_material_snapshot_v1(conta_pagar):
    """Builds the v1 material snapshot byte-compatible with migration 0020."""
    return {
        'fingerprint_schema_version': PAYABLE_FINGERPRINT_SCHEMA_VERSION,
        'igreja_id': int(conta_pagar.igreja_id),
        'fornecedor_id': int(conta_pagar.fornecedor_id),
        'valor': format(
            Decimal(conta_pagar.valor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            '.2f',
        ),
        'data_vencimento': conta_pagar.data_vencimento.isoformat(),
        'descricao': unicodedata.normalize('NFC', conta_pagar.descricao or '')
        .replace('\r\n', '\n')
        .replace('\r', '\n')
        .strip(),
    }


def compute_payable_material_fingerprint_v1(snapshot):
    """Returns the stable v1 SHA-256 fingerprint for a material snapshot."""
    canonical_json = json.dumps(
        snapshot,
        ensure_ascii=False,
        sort_keys=True,
        separators=(',', ':'),
    )
    return f'{PAYABLE_FINGERPRINT_PREFIX}{hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()}'


def refresh_payable_material_fingerprint(payable):
    material_snapshot = build_payable_material_snapshot_v1(payable)
    fingerprint = compute_payable_material_fingerprint_v1(material_snapshot)
    payable.current_material_fingerprint = fingerprint
    return fingerprint


def _resolve_payable_policy(igreja):
    policy, _ = PoliticaFinanceiraIgreja.objects.get_or_create(
        igreja=igreja,
        defaults={
            'approval_required': False,
            'segregation_level': PoliticaFinanceiraIgreja.LEVEL_1_SIMPLE,
            'version': 1,
        },
    )
    policy.full_clean()
    return policy


def _build_policy_snapshot(policy):
    return {
        'policy_id': policy.pk,
        'policy_version': policy.version,
        'approval_required': policy.approval_required,
        'segregation_level': policy.segregation_level,
    }


def _build_actor_snapshot(actor):
    if actor is None:
        return None, None

    return actor.pk, (actor.get_full_name() or actor.username)[:150]


def _validate_payable_domain_integrity(payable):
    """Ensures the payable relations belong to its ministry and church context."""
    errors = {}

    if payable.igreja.ministerio_id != payable.ministerio_id:
        errors['igreja'] = 'A igreja deve pertencer ao mesmo ministério da conta a pagar.'
    if payable.fornecedor.ministerio_id != payable.ministerio_id:
        errors['fornecedor'] = 'O fornecedor deve pertencer ao mesmo ministério da conta a pagar.'
    if payable.categoria_id and payable.categoria.ministerio_id != payable.ministerio_id:
        errors['categoria'] = 'A categoria deve pertencer ao mesmo ministério da conta a pagar.'
    if payable.conta_debito_id and payable.conta_debito.igreja_id != payable.igreja_id:
        errors['conta_debito'] = 'A conta de débito deve pertencer à mesma igreja da conta a pagar.'
    if payable.recorrencia_origem_id:
        if payable.recorrencia_origem.ministerio_id != payable.ministerio_id:
            errors['recorrencia_origem'] = 'A recorrência de origem deve pertencer ao mesmo ministério da conta a pagar.'
        elif payable.recorrencia_origem.igreja_id != payable.igreja_id:
            errors['recorrencia_origem'] = 'A recorrência de origem deve pertencer à mesma igreja da conta a pagar.'

    if errors:
        raise ValidationError(errors)


def _resolve_locked_payable_policy(igreja):
    """Resolve e bloqueia a política vigente usada em uma decisão formal."""
    policy = _resolve_payable_policy(igreja)
    return PoliticaFinanceiraIgreja.objects.select_for_update().get(pk=policy.pk)


def _validate_formal_payable_decision(payable, actor, policy):
    """Valida os guards comuns das decisões formais de autorização."""
    if payable.authorization_status is None:
        raise ValidationError('A conta a pagar não possui status de autorização para decisão formal.')
    if not policy.approval_required:
        raise ValidationError('A política vigente não exige aprovação; a conta requer reclassificação antes da decisão.')
    if payable.authorization_status != ContaPagar.AUTHORIZATION_PENDING:
        raise ValidationError('A decisão formal exige conta a pagar com autorização pendente.')
    if payable.status not in {'PEN', 'VEN'}:
        raise ValidationError('A decisão formal só é permitida para contas pendentes ou vencidas.')
    if payable.usuario_criacao_id and payable.usuario_criacao_id == actor.pk:
        raise PermissionDenied('O criador da conta a pagar não pode decidir sua própria submissão.')
    _validate_payable_domain_integrity(payable)


def _refresh_locked_payable_material_fingerprint(payable):
    """Recalcula a evidência material usando exclusivamente os dados persistidos sob lock."""
    material_snapshot = build_payable_material_snapshot_v1(payable)
    fingerprint = compute_payable_material_fingerprint_v1(material_snapshot)
    payable.current_material_fingerprint = fingerprint
    return material_snapshot, fingerprint


def _create_payable_decision_event(*, payable, event_type, actor, authorization_status_after,
                                   material_snapshot, fingerprint, policy, reason):
    actor_user_id_snapshot, actor_display_name_snapshot = _build_actor_snapshot(actor)
    ContaPagarAutorizacaoEvento.objects.create(
        conta_pagar=payable,
        event_type=event_type,
        actor=actor,
        actor_user_id_snapshot=actor_user_id_snapshot,
        actor_display_name_snapshot=actor_display_name_snapshot,
        authorization_status_before=ContaPagar.AUTHORIZATION_PENDING,
        authorization_status_after=authorization_status_after,
        financial_status_before=payable.status,
        financial_status_after=payable.status,
        material_fingerprint=fingerprint,
        material_snapshot=material_snapshot,
        policy_snapshot=_build_policy_snapshot(policy),
        reason=reason,
        correlation_id=None,
    )


def approve_payable(*, payable_id: int, actor):
    """Aprova uma ContaPagar pendente com capability, escopo local e evidência imutável."""
    if not getattr(actor, 'is_authenticated', False):
        raise PermissionDenied('A decisão formal exige um usuário autenticado.')
    if not can_approve_payable(actor):
        raise PermissionDenied('O usuário não possui permissão formal para decidir contas a pagar.')

    with transaction.atomic():
        payable = (
            ContaPagar.objects
            .select_for_update()
            .select_related(
                'igreja__ministerio', 'fornecedor', 'categoria', 'conta_debito',
                'recorrencia_origem', 'recorrencia_origem__igreja',
                'recorrencia_origem__ministerio',
            )
            .get(pk=payable_id)
        )
        if not get_finance_approval_scope(actor, payable.ministerio).filter(pk=payable.igreja_id).exists():
            raise PermissionDenied('O usuário não possui escopo local explícito para decidir esta conta a pagar.')

        policy = _resolve_locked_payable_policy(payable.igreja)
        _validate_formal_payable_decision(payable, actor, policy)
        material_snapshot, fingerprint = _refresh_locked_payable_material_fingerprint(payable)
        payable.authorization_status = ContaPagar.AUTHORIZATION_APPROVED
        payable.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_USER_APPROVAL
        payable.authorization_policy_version = policy.version
        payable.approved_material_fingerprint = fingerprint
        payable.approved_by = actor
        payable.approved_at = timezone.now()
        payable.rejected_by = None
        payable.rejected_at = None
        payable.current_rejection_reason = None
        payable.save(update_fields=[
            'current_material_fingerprint', 'authorization_status', 'authorization_origin',
            'authorization_policy_version', 'approved_material_fingerprint', 'approved_by',
            'approved_at', 'rejected_by', 'rejected_at', 'current_rejection_reason',
            'data_atualizacao',
        ])
        _create_payable_decision_event(
            payable=payable,
            event_type=ContaPagarAutorizacaoEvento.EVENT_APPROVED,
            actor=actor,
            authorization_status_after=ContaPagar.AUTHORIZATION_APPROVED,
            material_snapshot=material_snapshot,
            fingerprint=fingerprint,
            policy=policy,
            reason=None,
        )
        return payable


def reject_payable(*, payable_id: int, actor, reason: str):
    """Rejeita uma ContaPagar pendente com motivo e evidência material imutável."""
    normalized_reason = (reason or '').strip()
    if not normalized_reason:
        raise ValidationError('O motivo da rejeição é obrigatório.')
    if len(normalized_reason) > 1000:
        raise ValidationError('O motivo da rejeição deve ter no máximo 1000 caracteres.')
    if not getattr(actor, 'is_authenticated', False):
        raise PermissionDenied('A decisão formal exige um usuário autenticado.')
    if not can_approve_payable(actor):
        raise PermissionDenied('O usuário não possui permissão formal para decidir contas a pagar.')

    with transaction.atomic():
        payable = (
            ContaPagar.objects
            .select_for_update()
            .select_related(
                'igreja__ministerio', 'fornecedor', 'categoria', 'conta_debito',
                'recorrencia_origem', 'recorrencia_origem__igreja',
                'recorrencia_origem__ministerio',
            )
            .get(pk=payable_id)
        )
        if not get_finance_approval_scope(actor, payable.ministerio).filter(pk=payable.igreja_id).exists():
            raise PermissionDenied('O usuário não possui escopo local explícito para decidir esta conta a pagar.')

        policy = _resolve_locked_payable_policy(payable.igreja)
        _validate_formal_payable_decision(payable, actor, policy)
        material_snapshot, fingerprint = _refresh_locked_payable_material_fingerprint(payable)
        payable.authorization_status = ContaPagar.AUTHORIZATION_REJECTED
        payable.authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED
        payable.authorization_policy_version = policy.version
        payable.approved_material_fingerprint = None
        payable.approved_by = None
        payable.approved_at = None
        payable.rejected_by = actor
        payable.rejected_at = timezone.now()
        payable.current_rejection_reason = normalized_reason
        payable.save(update_fields=[
            'current_material_fingerprint', 'authorization_status', 'authorization_origin',
            'authorization_policy_version', 'approved_material_fingerprint', 'approved_by',
            'approved_at', 'rejected_by', 'rejected_at', 'current_rejection_reason',
            'data_atualizacao',
        ])
        _create_payable_decision_event(
            payable=payable,
            event_type=ContaPagarAutorizacaoEvento.EVENT_REJECTED,
            actor=actor,
            authorization_status_after=ContaPagar.AUTHORIZATION_REJECTED,
            material_snapshot=material_snapshot,
            fingerprint=fingerprint,
            policy=policy,
            reason=normalized_reason,
        )
        return payable


def create_payable(
    *,
    ministerio,
    igreja,
    fornecedor,
    descricao,
    valor,
    data_vencimento,
    data_emissao=None,
    categoria=None,
    numero_documento=None,
    conta_debito=None,
    forma_pagamento=None,
    recorrencia_origem=None,
    competencia=None,
    criado_automaticamente=False,
    observacoes=None,
    usuario_criacao=None,
    actor=None,
):
    """Creates a payable with its initial authorization classification and audit event."""
    with transaction.atomic():
        policy = _resolve_payable_policy(igreja)
        if policy.approval_required:
            authorization_status = ContaPagar.AUTHORIZATION_PENDING
            authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_POLICY_REQUIRED
        else:
            authorization_status = ContaPagar.AUTHORIZATION_NOT_REQUIRED
            authorization_origin = ContaPagar.AUTHORIZATION_ORIGIN_POLICY_NOT_REQUIRED

        payable_fields = {
            'ministerio': ministerio,
            'igreja': igreja,
            'fornecedor': fornecedor,
            'categoria': categoria,
            'descricao': descricao,
            'numero_documento': numero_documento,
            'valor': valor,
            'data_vencimento': data_vencimento,
            'status': 'PEN',
            'conta_debito': conta_debito,
            'forma_pagamento': forma_pagamento,
            'recorrencia_origem': recorrencia_origem,
            'competencia': competencia,
            'criado_automaticamente': criado_automaticamente,
            'authorization_status': authorization_status,
            'authorization_origin': authorization_origin,
            'authorization_policy_version': policy.version,
            'approved_material_fingerprint': None,
            'approved_by': None,
            'approved_at': None,
            'rejected_by': None,
            'rejected_at': None,
            'current_rejection_reason': None,
            'observacoes': observacoes,
            'usuario_criacao': usuario_criacao,
        }
        if data_emissao is not None:
            payable_fields['data_emissao'] = data_emissao

        payable = ContaPagar(
            **payable_fields,
        )
        _validate_payable_domain_integrity(payable)
        payable.full_clean()
        material_snapshot = build_payable_material_snapshot_v1(payable)
        fingerprint = compute_payable_material_fingerprint_v1(material_snapshot)
        payable.current_material_fingerprint = fingerprint
        payable.save()

        actor_user_id_snapshot, actor_display_name_snapshot = _build_actor_snapshot(actor)
        ContaPagarAutorizacaoEvento.objects.create(
            conta_pagar=payable,
            event_type=ContaPagarAutorizacaoEvento.EVENT_CREATED,
            actor=actor,
            actor_user_id_snapshot=actor_user_id_snapshot,
            actor_display_name_snapshot=actor_display_name_snapshot,
            authorization_status_before=None,
            authorization_status_after=authorization_status,
            financial_status_before=None,
            financial_status_after=payable.status,
            material_fingerprint=fingerprint,
            material_snapshot=material_snapshot,
            policy_snapshot=_build_policy_snapshot(policy),
            reason=None,
            correlation_id=None,
        )
        return payable


class DepartamentoFinanceiroService:
    """Servicos para gerar e sincronizar departamentos financeiros padrao."""

    DEPARTAMENTOS_PADRAO = (
        {
            'codigo': DepartamentoFinanceiro.CODIGO_LOCAL,
            'nome': 'Tesouraria Local',
            'ordem': 10,
            'politica': {
                'exige_nota_fiscal': True,
                'exige_envio_contabilidade': True,
                'permite_prestacao_local_simplificada': False,
                'exige_aprovacao_para_saida': True,
            },
        },
        {
            'codigo': DepartamentoFinanceiro.CODIGO_EVENTOS,
            'nome': 'Eventos',
            'ordem': 20,
            'politica': {
                'exige_nota_fiscal': False,
                'exige_envio_contabilidade': False,
                'permite_prestacao_local_simplificada': True,
                'exige_aprovacao_para_saida': False,
            },
        },
        {
            'codigo': DepartamentoFinanceiro.CODIGO_MISSOES,
            'nome': 'Missoes',
            'ordem': 30,
            'politica': {
                'exige_nota_fiscal': True,
                'exige_envio_contabilidade': True,
                'permite_prestacao_local_simplificada': False,
                'exige_aprovacao_para_saida': True,
            },
        },
        {
            'codigo': DepartamentoFinanceiro.CODIGO_ASSISTENCIA,
            'nome': 'Assistencia Social',
            'ordem': 40,
            'politica': {
                'exige_nota_fiscal': True,
                'exige_envio_contabilidade': True,
                'permite_prestacao_local_simplificada': False,
                'exige_aprovacao_para_saida': True,
            },
        },
    )

    @staticmethod
    def garantir_departamentos_padrao_para_igreja(igreja):
        """Cria/atualiza departamentos padrao para uma igreja de forma idempotente."""
        if not igreja:
            return {'departamentos_criados': 0, 'departamentos_atualizados': 0, 'politicas_criadas': 0}

        stats = {'departamentos_criados': 0, 'departamentos_atualizados': 0, 'politicas_criadas': 0}

        with transaction.atomic():
            for definicao in DepartamentoFinanceiroService.DEPARTAMENTOS_PADRAO:
                codigo = definicao['codigo']
                nome = definicao['nome']
                ordem = definicao['ordem']
                politica_defaults = definicao['politica']

                fundo, _ = FundoDepartamental.objects.get_or_create(
                    igreja=igreja,
                    codigo=codigo,
                    defaults={'nome_exibicao': nome, 'ativo': True},
                )

                departamento_central = None
                try:
                    if 'configuracao_departamento' in connection.introspection.table_names():
                        departamento_central, _ = Departamento.objects.get_or_create(
                            igreja=igreja,
                            codigo_interno=codigo,
                            defaults={
                                'nome_exibicao': nome,
                                'tipo_departamento': Departamento.TIPO_PADRAO,
                                'classificacao': (
                                    Departamento.CLASSIFICACAO_CONTEXTO_FINANCEIRO_SISTEMA
                                    if codigo in {
                                        DepartamentoFinanceiro.CODIGO_LOCAL,
                                        DepartamentoFinanceiro.CODIGO_EVENTOS,
                                    }
                                    else Departamento.CLASSIFICACAO_LEGADO_SUGERIDO
                                    if codigo in {
                                        DepartamentoFinanceiro.CODIGO_MISSOES,
                                        DepartamentoFinanceiro.CODIGO_ASSISTENCIA,
                                    }
                                    else Departamento.CLASSIFICACAO_ORGANIZACIONAL
                                ),
                                'ativo': True,
                                'ordem_exibicao': ordem,
                            },
                        )

                        if departamento_central.tipo_departamento != Departamento.TIPO_PADRAO:
                            departamento_central.tipo_departamento = Departamento.TIPO_PADRAO
                            departamento_central.save(update_fields=['tipo_departamento'])
                except Exception:
                    departamento_central = None

                departamento, created = DepartamentoFinanceiro.objects.get_or_create(
                    igreja=igreja,
                    codigo_interno=codigo,
                    defaults={
                        'nome_exibicao': nome,
                        'tipo_departamento': DepartamentoFinanceiro.TIPO_PADRAO,
                        'ativo': True,
                        'ordem_exibicao': ordem,
                        'departamento': departamento_central,
                        'fundo_departamental': fundo,
                    },
                )

                if created:
                    stats['departamentos_criados'] += 1
                else:
                    campos_update = []
                    if departamento.tipo_departamento != DepartamentoFinanceiro.TIPO_PADRAO:
                        departamento.tipo_departamento = DepartamentoFinanceiro.TIPO_PADRAO
                        campos_update.append('tipo_departamento')
                    if departamento_central and departamento.departamento_id != departamento_central.id:
                        departamento.departamento = departamento_central
                        campos_update.append('departamento')
                    if departamento.fundo_departamental_id != fundo.id:
                        departamento.fundo_departamental = fundo
                        campos_update.append('fundo_departamental')
                    if not departamento.nome_exibicao:
                        departamento.nome_exibicao = nome
                        campos_update.append('nome_exibicao')
                    if campos_update:
                        departamento.save(update_fields=campos_update)
                        stats['departamentos_atualizados'] += 1

                _, politica_created = PoliticaDepartamentoFinanceiro.objects.get_or_create(
                    departamento=departamento,
                    defaults=politica_defaults,
                )
                if politica_created:
                    stats['politicas_criadas'] += 1

        return stats

    @staticmethod
    def sincronizar_departamentos_padrao(igreja_ids=None):
        """Sincroniza departamentos padrao para todas igrejas (ou subconjunto)."""
        igrejas = Igreja.objects.all().order_by('id')
        if igreja_ids:
            igrejas = igrejas.filter(id__in=igreja_ids)

        total = {
            'igrejas_processadas': 0,
            'departamentos_criados': 0,
            'departamentos_atualizados': 0,
            'politicas_criadas': 0,
        }

        for igreja in igrejas.iterator():
            resultado = DepartamentoFinanceiroService.garantir_departamentos_padrao_para_igreja(igreja)
            total['igrejas_processadas'] += 1
            total['departamentos_criados'] += resultado['departamentos_criados']
            total['departamentos_atualizados'] += resultado['departamentos_atualizados']
            total['politicas_criadas'] += resultado['politicas_criadas']

        return total

    @staticmethod
    def fundos_visiveis_para_igrejas(igrejas):
        """Retorna fundos ativos e com departamento ativo, se existir vinculo departamental."""
        if not igrejas:
            return FundoDepartamental.objects.none()

        return FundoDepartamental.objects.filter(
            igreja__in=igrejas,
            ativo=True,
        ).filter(
            Q(departamento_financeiro__isnull=True) | Q(departamento_financeiro__ativo=True)
        ).order_by('igreja__nome_igreja', 'nome_exibicao')


class ReceitaFluxoService:
    """Orquestra preparacao de payload/contexto dos fluxos de receita."""

    @staticmethod
    def construir_post_data_receita_evento(raw_post_data, evento):
        post_data = raw_post_data.copy()
        conta_evento_efetiva_id = obter_conta_evento_efetiva_id(evento)
        post_data['igreja'] = str(evento.igreja_id)
        post_data['evento'] = str(evento.pk)
        post_data['categoria'] = categoria_receita_por_evento(evento)
        if conta_evento_efetiva_id:
            post_data['conta_bancaria'] = str(conta_evento_efetiva_id)
        return post_data, conta_evento_efetiva_id

    @staticmethod
    def construir_initial_receita_evento(evento):
        conta_evento_efetiva_id = obter_conta_evento_efetiva_id(evento)
        initial = {
            'igreja': evento.igreja,
            'evento': evento,
            'data': timezone.now().date(),
            'categoria': categoria_receita_por_evento(evento),
        }
        if conta_evento_efetiva_id:
            initial['conta_bancaria'] = conta_evento_efetiva_id
        return initial, conta_evento_efetiva_id

    @staticmethod
    def construir_contexto_receita_evento(form, ministerio, evento, conta_evento_efetiva_id):
        return {
            'form': form,
            'ministerio': ministerio,
            'titulo_pagina': f'Adicionar Entrada - {evento.titulo}',
            'ocultar_campo_igreja': True,
            'ocultar_campo_evento': True,
            'ocultar_campo_categoria': True,
            'ocultar_campo_conta_bancaria': bool(conta_evento_efetiva_id),
            'modo_evento': True,
            'evento_contexto': evento,
            'url_cancelar': reverse('eventos:detalhe_evento', kwargs={'pk': evento.pk}),
        }

    @staticmethod
    def resolver_igreja_padrao_receita_caixa_eventos(request, allowed_churches, is_admin):
        if request.igreja_ativa and (is_admin or allowed_churches.filter(pk=request.igreja_ativa.pk).exists()):
            return request.igreja_ativa
        if not is_admin and allowed_churches.count() == 1:
            return allowed_churches.first()
        return None

    @staticmethod
    def construir_post_data_receita_caixa_eventos(raw_post_data, igreja_padrao_para_form, allowed_churches):
        post_data = raw_post_data.copy()
        post_data['igreja'] = str(igreja_padrao_para_form.pk)
        post_data['categoria'] = post_data.get('categoria') or categoria_receita_padrao_por_fundo(FUNDO_EVENTOS)

        evento_id = post_data.get('evento')
        evento = obter_evento_no_escopo(allowed_churches, evento_id)
        conta_evento_efetiva_id = None

        if evento:
            post_data['categoria'] = categoria_receita_por_evento(evento)
            conta_evento_efetiva_id = obter_conta_evento_efetiva_id(evento)
            if conta_evento_efetiva_id:
                post_data['conta_bancaria'] = str(conta_evento_efetiva_id)
        elif getattr(igreja_padrao_para_form, 'conta_padrao_eventos_id', None) and not post_data.get('conta_bancaria'):
            post_data['conta_bancaria'] = str(igreja_padrao_para_form.conta_padrao_eventos_id)

        return post_data, evento, conta_evento_efetiva_id

    @staticmethod
    def aplicar_defaults_receita_fluxo_evento(receita):
        receita.categoria = categoria_receita_por_evento(receita.evento)
        if receita.evento_id:
            conta_evento_efetiva_id = obter_conta_evento_efetiva_id(receita.evento)
            if conta_evento_efetiva_id:
                receita.conta_bancaria_id = conta_evento_efetiva_id

    @staticmethod
    def construir_initial_receita_caixa_eventos(igreja_padrao_para_form):
        initial = {
            'igreja': igreja_padrao_para_form,
            'data': timezone.now().date(),
            'categoria': categoria_receita_padrao_por_fundo(FUNDO_EVENTOS),
        }
        if getattr(igreja_padrao_para_form, 'conta_padrao_eventos_id', None):
            initial['conta_bancaria'] = igreja_padrao_para_form.conta_padrao_eventos_id
        return initial

    @staticmethod
    def aplicar_defaults_receita_caixa_eventos(receita):
        from django.db import connection
        from django.db.utils import OperationalError, ProgrammingError
        from .models import FundoDepartamental

        try:
            if 'financeiro_fundodepartamental' in connection.introspection.table_names():
                fundo_eventos, _ = FundoDepartamental.objects.get_or_create(
                    igreja=receita.igreja,
                    codigo=FundoDepartamental.CODIGO_EVENTOS,
                    defaults={'nome_exibicao': 'Eventos'},
                )
                receita.fundo_departamental = fundo_eventos
        except (ProgrammingError, OperationalError):
            receita.fundo_departamental = None

        if receita.evento_id:
            ReceitaFluxoService.aplicar_defaults_receita_fluxo_evento(receita)
        elif not receita.conta_bancaria_id and getattr(receita.igreja, 'conta_padrao_eventos_id', None):
            receita.conta_bancaria_id = receita.igreja.conta_padrao_eventos_id


class FechamentoCaixaService:
    def __init__(self, data_inicio, data_fim, igreja=None, observacoes=''):
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.igreja = igreja
        self.observacoes = observacoes

    def buscar_dados(self):
        receitas = Receitas.objects.filter(
            data__gte=self.data_inicio,
            data__lte=self.data_fim,
            fechado=False,
        )
        despesas = Despesas.objects.filter(
            data__gte=self.data_inicio,
            data__lte=self.data_fim,
            fechado=False,
        )
        return receitas, despesas

    def calcular_totais(self, receitas_queryset, despesas_queryset):
        total_entradas = receitas_queryset.aggregate(Sum('valor')).get('valor__sum') or Decimal('0')
        total_saidas = despesas_queryset.aggregate(Sum('valor')).get('valor__sum') or Decimal('0')
        saldo_final = total_entradas - total_saidas
        return total_entradas, total_saidas, saldo_final

    def fechar_caixa(self, total_entradas, total_saidas, saldo_final):
        return FechamentoCaixa.objects.create(
            igreja=self.igreja,
            data_inicio=self.data_inicio,
            data_fim=self.data_fim,
            total_entradas=total_entradas,
            total_saidas=total_saidas,
            saldo_final=saldo_final,
            observacoes=self.observacoes,
            status='fechado',
        )


class OFXImportService:
    def parse(self, content):
        xml_content = self._normalizar_ofx_para_xml(content)
        root = ET.fromstring(xml_content)

        statement = root.find('.//BANKTRANLIST')
        if statement is None:
            raise ValueError('Arquivo OFX sem bloco BANKTRANLIST.')

        ledger_balance = root.find('.//LEDGERBAL/BALAMT')
        account_id = root.findtext('.//BANKACCTFROM/ACCTID')
        bank_id = root.findtext('.//BANKACCTFROM/BANKID')
        account_type = root.findtext('.//BANKACCTFROM/ACCTTYPE')
        start_date = self._parse_ofx_datetime(statement.findtext('DTSTART'))
        end_date = self._parse_ofx_datetime(statement.findtext('DTEND'))

        transactions = []
        for transaction in statement.findall('STMTTRN'):
            amount = Decimal(transaction.findtext('TRNAMT', '0').strip())
            posted_at = self._parse_ofx_datetime(transaction.findtext('DTPOSTED'))
            transaction_type = (transaction.findtext('TRNTYPE') or '').strip().upper()
            fit_id = (transaction.findtext('FITID') or '').strip()
            memo = (transaction.findtext('MEMO') or '').strip()
            checknum = (transaction.findtext('CHECKNUM') or '').strip()

            transactions.append({
                'tipo': 'entrada' if amount >= 0 else 'saida',
                'trn_type': transaction_type,
                'data': posted_at,
                'valor': amount,
                'fit_id': fit_id,
                'memo': memo,
                'documento': checknum,
            })

        return {
            'banco_id': (bank_id or '').strip(),
            'conta_id': (account_id or '').strip(),
            'tipo_conta': (account_type or '').strip(),
            'data_inicio': start_date,
            'data_fim': end_date,
            'saldo_final': Decimal(ledger_balance.text.strip()) if ledger_balance is not None and ledger_balance.text else Decimal('0.00'),
            'transacoes': transactions,
        }

    def importar_para_banco(self, content, conta_bancaria, usuario=None, arquivo_nome=''):
        parsed = self.parse(content)
        file_hash = sha256(content.encode('utf-8')).hexdigest()

        if ImportacaoExtratoOFX.objects.filter(conta_bancaria=conta_bancaria, hash_arquivo=file_hash).exists():
            raise ValueError('Este arquivo OFX ja foi importado para esta conta.')

        with transaction.atomic():
            importacao = ImportacaoExtratoOFX.objects.create(
                conta_bancaria=conta_bancaria,
                igreja=conta_bancaria.igreja,
                usuario=usuario,
                arquivo_nome=arquivo_nome,
                hash_arquivo=file_hash,
                banco_id=parsed['banco_id'],
                conta_id=parsed['conta_id'],
                tipo_conta=parsed['tipo_conta'],
                data_inicio=parsed['data_inicio'],
                data_fim=parsed['data_fim'],
                saldo_final=parsed['saldo_final'],
            )

            LancamentoExtratoOFX.objects.bulk_create([
                LancamentoExtratoOFX(
                    importacao=importacao,
                    data=transacao['data'],
                    tipo=transacao['tipo'],
                    trn_type=transacao['trn_type'],
                    valor=transacao['valor'],
                    fit_id=transacao['fit_id'],
                    memo=transacao['memo'],
                    documento=transacao['documento'],
                )
                for transacao in parsed['transacoes']
            ])

        return importacao

    def gerar_sugestoes_conciliacao(self, importacao, tolerancia_dias=3, limite_por_lancamento=3):
        lancamentos = importacao.lancamentos.filter(conciliado=False).order_by('data', 'id')
        sugestoes = []

        for lancamento in lancamentos:
            valor_base = abs(lancamento.valor)
            data_base = lancamento.data.date()
            data_inicio = data_base - timedelta(days=tolerancia_dias)
            data_fim = data_base + timedelta(days=tolerancia_dias)

            if lancamento.tipo == 'entrada':
                candidatos = Receitas.objects.filter(
                    igreja=importacao.igreja,
                    data__gte=data_inicio,
                    data__lte=data_fim,
                    valor=valor_base,
                ).order_by('data', 'id')
                tipo_objeto = 'receita'
            else:
                candidatos = Despesas.objects.filter(
                    igreja=importacao.igreja,
                    data__gte=data_inicio,
                    data__lte=data_fim,
                    valor=valor_base,
                ).order_by('data', 'id')
                tipo_objeto = 'despesa'

            candidatos_rankeados = []
            for candidato in candidatos:
                score = self._calcular_score_candidato(lancamento, candidato, importacao.conta_bancaria_id)
                candidatos_rankeados.append((score, candidato))

            candidatos_rankeados.sort(key=lambda item: item[0], reverse=True)
            melhores = [
                {
                    'id': candidato.id,
                    'tipo': tipo_objeto,
                    'data': candidato.data,
                    'valor': candidato.valor,
                    'score': score,
                }
                for score, candidato in candidatos_rankeados[:limite_por_lancamento]
            ]

            sugestoes.append(
                {
                    'lancamento_id': lancamento.id,
                    'fit_id': lancamento.fit_id,
                    'tipo': lancamento.tipo,
                    'valor': lancamento.valor,
                    'data': lancamento.data,
                    'memo': lancamento.memo,
                    'sugestoes': melhores,
                }
            )

        return sugestoes

    def confirmar_conciliacao(self, lancamento_id, tipo, referencia_id, usuario=None):
        tipo = (tipo or '').strip().lower()
        if tipo not in {'receita', 'despesa'}:
            raise ValueError('Tipo de conciliacao invalido. Use receita ou despesa.')

        with transaction.atomic():
            lancamento = (
                LancamentoExtratoOFX.objects
                .select_for_update()
                .select_related('importacao', 'importacao__igreja')
                .get(pk=lancamento_id)
            )

            if lancamento.conciliado:
                raise ValueError('Lancamento OFX ja conciliado.')

            if tipo == 'receita':
                referencia = Receitas.objects.filter(
                    pk=referencia_id,
                    igreja=lancamento.importacao.igreja,
                ).first()
            else:
                referencia = Despesas.objects.filter(
                    pk=referencia_id,
                    igreja=lancamento.importacao.igreja,
                ).first()

            if referencia is None:
                raise ValueError('Lancamento interno nao encontrado para conciliacao.')

            if abs(Decimal(referencia.valor)) != abs(Decimal(lancamento.valor)):
                raise ValueError('Valor do lancamento interno difere do valor OFX.')

            lancamento.conciliado = True
            lancamento.conciliado_tipo = tipo
            lancamento.conciliado_referencia_id = referencia.id
            lancamento.conciliado_por = usuario
            lancamento.conciliado_em = timezone.now()
            lancamento.save(update_fields=[
                'conciliado',
                'conciliado_tipo',
                'conciliado_referencia_id',
                'conciliado_por',
                'conciliado_em',
            ])

        return lancamento

    def desfazer_conciliacao(self, lancamento_id):
        with transaction.atomic():
            lancamento = (
                LancamentoExtratoOFX.objects
                .select_for_update()
                .get(pk=lancamento_id)
            )

            if not lancamento.conciliado:
                raise ValueError('Lancamento OFX ainda nao esta conciliado.')

            lancamento.conciliado = False
            lancamento.conciliado_tipo = ''
            lancamento.conciliado_referencia_id = None
            lancamento.conciliado_por = None
            lancamento.conciliado_em = None
            lancamento.save(update_fields=[
                'conciliado',
                'conciliado_tipo',
                'conciliado_referencia_id',
                'conciliado_por',
                'conciliado_em',
            ])

        return lancamento

    def conciliar_melhores_sugestoes(self, importacao, usuario=None, score_minimo=90, dry_run=False):
        sugestoes = self.gerar_sugestoes_conciliacao(importacao)
        total_conciliados = 0
        total_ignorados_score = 0
        total_erros = 0
        referencias_usadas = set()
        itens_selecionados = []
        quantidade_entradas = 0
        quantidade_saidas = 0
        total_entradas = Decimal('0')
        total_saidas = Decimal('0')

        def registrar_impacto(item_sugestao):
            nonlocal quantidade_entradas, quantidade_saidas, total_entradas, total_saidas
            tipo_ofx = item_sugestao.get('tipo')
            valor_ofx = abs(Decimal(item_sugestao.get('valor') or 0))
            if tipo_ofx == 'entrada':
                quantidade_entradas += 1
                total_entradas += valor_ofx
            else:
                quantidade_saidas += 1
                total_saidas += valor_ofx

        for item in sugestoes:
            candidatos = item.get('sugestoes') or []
            if not candidatos:
                continue

            melhor = candidatos[0]
            if melhor.get('score', 0) < score_minimo:
                total_ignorados_score += 1
                continue

            chave_referencia = (melhor.get('tipo'), melhor.get('id'))
            if chave_referencia in referencias_usadas:
                total_ignorados_score += 1
                continue

            itens_selecionados.append(
                {
                    'lancamento_id': item.get('lancamento_id'),
                    'fit_id': item.get('fit_id'),
                    'tipo_ofx': item.get('tipo'),
                    'data_ofx': item.get('data'),
                    'valor_ofx': item.get('valor'),
                    'memo': item.get('memo'),
                    'tipo_referencia': melhor.get('tipo'),
                    'referencia_id': melhor.get('id'),
                    'data_referencia': melhor.get('data'),
                    'valor_referencia': melhor.get('valor'),
                    'score': melhor.get('score', 0),
                }
            )

            if dry_run:
                referencias_usadas.add(chave_referencia)
                total_conciliados += 1
                registrar_impacto(item)
                continue

            try:
                self.confirmar_conciliacao(
                    lancamento_id=item.get('lancamento_id'),
                    tipo=melhor.get('tipo'),
                    referencia_id=melhor.get('id'),
                    usuario=usuario,
                )
                referencias_usadas.add(chave_referencia)
                total_conciliados += 1
                registrar_impacto(item)
            except Exception:
                total_erros += 1

        return {
            'total_conciliados': total_conciliados,
            'total_ignorados_score': total_ignorados_score,
            'total_erros': total_erros,
            'itens_selecionados': itens_selecionados,
            'resumo_impacto': {
                'quantidade_entradas': quantidade_entradas,
                'quantidade_saidas': quantidade_saidas,
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'total_movimentado': total_entradas + total_saidas,
                'saldo_previsto': total_entradas - total_saidas,
            },
        }

    def _calcular_score_candidato(self, lancamento, candidato, conta_bancaria_id):
        dias_diferenca = abs((lancamento.data.date() - candidato.data).days)
        score = 100 - (dias_diferenca * 10)

        candidato_conta_id = getattr(candidato, 'conta_bancaria_id', None)
        if candidato_conta_id and candidato_conta_id == conta_bancaria_id:
            score += 20

        memo = (lancamento.memo or '').lower()
        texto_candidato = ''
        if hasattr(candidato, 'descricao'):
            texto_candidato = (candidato.descricao or '').lower()
        else:
            texto_candidato = (getattr(candidato, 'observacao', '') or '').lower()

        if memo and texto_candidato and any(token in texto_candidato for token in memo.split() if len(token) >= 4):
            score += 5

        return score

    def _normalizar_ofx_para_xml(self, content):
        if not content or '<OFX>' not in content.upper():
            raise ValueError('Conteudo OFX invalido.')

        start_index = content.upper().find('<OFX>')
        body = content[start_index:]
        normalized_lines = []

        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            match = re.match(r'^<([A-Z0-9_]+)>([^<]+)$', line, flags=re.IGNORECASE)
            if match:
                tag_name = match.group(1)
                value = self._escape_xml(match.group(2).strip())
                normalized_lines.append(f'<{tag_name}>{value}</{tag_name}>')
            else:
                normalized_lines.append(line)

        return '\n'.join(normalized_lines)

    def _parse_ofx_datetime(self, value):
        if not value:
            return None

        digits = re.match(r'^(\d{8})(\d{6})?', value.strip())
        if not digits:
            raise ValueError(f'Data OFX invalida: {value}')

        date_part = digits.group(1)
        time_part = digits.group(2) or '000000'
        return datetime.strptime(f'{date_part}{time_part}', '%Y%m%d%H%M%S')

    def _escape_xml(self, value):
        return (
            value.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
        )


class RecorrenciaContaPagarService:
    """Gera contas a pagar a partir de recorrências de forma idempotente."""

    @staticmethod
    def _parse_competencia(competencia=None):
        if competencia:
            try:
                ano_str, mes_str = competencia.split('-')
                ano = int(ano_str)
                mes = int(mes_str)
            except (ValueError, TypeError):
                raise ValueError("Competencia invalida. Use o formato AAAA-MM.")
        else:
            hoje = timezone.localdate()
            ano = hoje.year
            mes = hoje.month

        if mes < 1 or mes > 12:
            raise ValueError("Mes da competencia invalido. Use um valor entre 01 e 12.")

        return ano, mes, f"{ano:04d}-{mes:02d}"

    @staticmethod
    def _calcular_data_vencimento(ano, mes, dia_vencimento):
        ultimo_dia_mes = monthrange(ano, mes)[1]
        dia_ajustado = min(dia_vencimento, ultimo_dia_mes)
        return datetime(ano, mes, dia_ajustado).date()

    def gerar_competencia(self, competencia=None, ministerio_id=None, igreja_id=None, dry_run=False):
        ano, mes, competencia_str = self._parse_competencia(competencia)
        recorrencias = RecorrenciaContaPagar.objects.filter(
            ativo=True,
            gerar_automaticamente=True,
        ).select_related('ministerio', 'igreja', 'fornecedor', 'categoria', 'conta_debito_padrao')

        if ministerio_id:
            recorrencias = recorrencias.filter(ministerio_id=ministerio_id)
        if igreja_id:
            recorrencias = recorrencias.filter(igreja_id=igreja_id)

        recorrencias = recorrencias.order_by('id')

        total_avaliadas = 0
        total_geradas = 0
        total_existentes = 0
        total_ignoradas = 0
        erros = []

        for recorrencia in recorrencias:
            total_avaliadas += 1
            try:
                if recorrencia.data_inicio and competencia_str < recorrencia.data_inicio.strftime('%Y-%m'):
                    total_ignoradas += 1
                    continue

                if recorrencia.data_fim and competencia_str > recorrencia.data_fim.strftime('%Y-%m'):
                    total_ignoradas += 1
                    continue

                data_vencimento = self._calcular_data_vencimento(ano, mes, recorrencia.dia_vencimento)
                data_emissao = datetime(ano, mes, 1).date()

                ja_existe = ContaPagar.objects.filter(
                    recorrencia_origem=recorrencia,
                    competencia=competencia_str,
                ).exists()

                if ja_existe:
                    total_existentes += 1
                    continue

                if dry_run:
                    total_geradas += 1
                    continue

                try:
                    with transaction.atomic():
                        create_payable(
                            ministerio=recorrencia.ministerio,
                            igreja=recorrencia.igreja,
                            fornecedor=recorrencia.fornecedor,
                            categoria=recorrencia.categoria,
                            descricao=recorrencia.descricao,
                            valor=recorrencia.valor,
                            data_emissao=data_emissao,
                            data_vencimento=data_vencimento,
                            conta_debito=recorrencia.conta_debito_padrao,
                            forma_pagamento=recorrencia.forma_pagamento_padrao,
                            recorrencia_origem=recorrencia,
                            competencia=competencia_str,
                            criado_automaticamente=True,
                            observacoes=recorrencia.observacoes,
                            usuario_criacao=recorrencia.usuario_criacao,
                            actor=None,
                        )
                        recorrencia.ultima_competencia_gerada = competencia_str
                        recorrencia.save(update_fields=['ultima_competencia_gerada', 'data_atualizacao'])
                        total_geradas += 1
                except ValidationError:
                    if ContaPagar.objects.filter(
                        recorrencia_origem=recorrencia,
                        competencia=competencia_str,
                    ).exists():
                        total_existentes += 1
                    else:
                        raise
                except IntegrityError:
                    total_existentes += 1
            except ValidationError:
                raise
            except Exception as exc:
                erros.append(f"Recorrencia {recorrencia.id}: {exc}")

        return {
            'competencia': competencia_str,
            'total_avaliadas': total_avaliadas,
            'total_geradas': total_geradas,
            'total_existentes': total_existentes,
            'total_ignoradas': total_ignoradas,
            'total_erros': len(erros),
            'erros': erros,
            'dry_run': dry_run,
        }


class AlertaVencimentoContaPagarService:
    """Gera notificações de alerta para contas a pagar próximas do vencimento ou vencidas."""

    @staticmethod
    def _tipo_alerta(dias_restantes):
        if dias_restantes < 0:
            return 'VENCIDA'
        if dias_restantes == 7:
            return 'D-7'
        if dias_restantes == 3:
            return 'D-3'
        if dias_restantes == 1:
            return 'D-1'
        return None

    @staticmethod
    def _usuarios_destino(conta):
        from financeiro.utils import get_allowed_churches_for_user

        perfis = PerfilUsuario.objects.filter(
            ministerio=conta.ministerio,
            user__is_active=True,
        ).select_related('user').distinct()

        usuarios = []
        for perfil in perfis:
            user = perfil.user
            if not user_has_permission_level_or_higher(user, TESOUREIRO):
                continue

            igrejas_permitidas = get_allowed_churches_for_user(user)
            if igrejas_permitidas.filter(pk=conta.igreja_id).exists():
                usuarios.append(user)

        return usuarios

    def enviar_alertas(self, dias_alerta=(7, 3, 1), incluir_vencidas=True, ministerio_id=None, igreja_id=None, dry_run=False):
        hoje = timezone.localdate()
        dias_alerta = tuple(sorted({int(d) for d in dias_alerta if int(d) >= 0}, reverse=True))
        limite_dias = max(dias_alerta) if dias_alerta else 0

        contas = ContaPagar.objects.filter(status__in=['PEN', 'VEN']).select_related(
            'ministerio', 'igreja', 'fornecedor'
        )

        if ministerio_id:
            contas = contas.filter(ministerio_id=ministerio_id)
        if igreja_id:
            contas = contas.filter(igreja_id=igreja_id)

        if incluir_vencidas:
            contas = contas.filter(data_vencimento__lte=hoje + timedelta(days=limite_dias))
        else:
            contas = contas.filter(data_vencimento__gte=hoje, data_vencimento__lte=hoje + timedelta(days=limite_dias))

        total_contas_avaliadas = 0
        total_notificacoes_criadas = 0
        total_notificacoes_existentes = 0
        total_contas_sem_destinatario = 0
        total_contas_fora_regra = 0
        erros = []

        for conta in contas.order_by('data_vencimento', 'id'):
            total_contas_avaliadas += 1
            try:
                dias_restantes = (conta.data_vencimento - hoje).days
                tipo_alerta = self._tipo_alerta(dias_restantes)

                if not tipo_alerta:
                    total_contas_fora_regra += 1
                    continue
                if tipo_alerta == 'VENCIDA' and not incluir_vencidas:
                    total_contas_fora_regra += 1
                    continue
                if tipo_alerta != 'VENCIDA' and dias_restantes not in dias_alerta:
                    total_contas_fora_regra += 1
                    continue

                usuarios_destino = self._usuarios_destino(conta)
                if not usuarios_destino:
                    total_contas_sem_destinatario += 1
                    continue

                marcador = f"[ALERTA-CP:{conta.id}:{tipo_alerta}]"
                for user in usuarios_destino:
                    ja_existe = Notificacao.objects.filter(
                        user=user,
                        ministerio=conta.ministerio,
                        notification_type='financeiro',
                        message__contains=marcador,
                    ).exists()

                    if ja_existe:
                        total_notificacoes_existentes += 1
                        continue

                    if dry_run:
                        total_notificacoes_criadas += 1
                        continue

                    Notificacao.objects.create(
                        user=user,
                        ministerio=conta.ministerio,
                        notification_type='financeiro',
                        message=(
                            f"{marcador} Conta a pagar '{conta.descricao}' ({conta.fornecedor.nome}) "
                            f"vence em {conta.data_vencimento.strftime('%d/%m/%Y')} "
                            f"(status: {conta.get_status_display()})."
                        ),
                        url=reverse('financeiro:lista_contas_pagar'),
                    )
                    total_notificacoes_criadas += 1
            except Exception as exc:
                erros.append(f"Conta {conta.id}: {exc}")

        return {
            'total_contas_avaliadas': total_contas_avaliadas,
            'total_notificacoes_criadas': total_notificacoes_criadas,
            'total_notificacoes_existentes': total_notificacoes_existentes,
            'total_contas_sem_destinatario': total_contas_sem_destinatario,
            'total_contas_fora_regra': total_contas_fora_regra,
            'total_erros': len(erros),
            'erros': erros,
            'dry_run': dry_run,
            'dias_alerta': dias_alerta,
            'incluir_vencidas': incluir_vencidas,
        }
