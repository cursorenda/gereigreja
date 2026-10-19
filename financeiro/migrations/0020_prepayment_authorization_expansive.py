import hashlib
import json
import unicodedata
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


FINGERPRINT_SCHEMA_VERSION = 1
FINGERPRINT_PREFIX = 'v1:sha256:'
LEGACY_BATCH_SIZE = 500


def _normalizar_valor(valor):
    return format(Decimal(valor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), '.2f')


def _normalizar_descricao(valor):
    texto = unicodedata.normalize('NFC', valor or '')
    return texto.replace('\r\n', '\n').replace('\r', '\n').strip()


def _material_snapshot(conta):
    return {
        'fingerprint_schema_version': FINGERPRINT_SCHEMA_VERSION,
        'igreja_id': int(conta.igreja_id),
        'fornecedor_id': int(conta.fornecedor_id),
        'valor': _normalizar_valor(conta.valor),
        'data_vencimento': conta.data_vencimento.isoformat(),
        'descricao': _normalizar_descricao(conta.descricao),
    }


def _material_fingerprint(snapshot):
    canonical_json = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return f'{FINGERPRINT_PREFIX}{hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()}'


def backfill_prepayment_authorization(apps, schema_editor):
    Igreja = apps.get_model('configuracao', 'Igreja')
    PoliticaFinanceiraIgreja = apps.get_model('financeiro', 'PoliticaFinanceiraIgreja')
    ContaPagar = apps.get_model('financeiro', 'ContaPagar')
    ContaPagarAutorizacaoEvento = apps.get_model('financeiro', 'ContaPagarAutorizacaoEvento')

    legacy_max_pk = ContaPagar.objects.order_by('-pk').values_list('pk', flat=True).first()

    for igreja_id in Igreja.objects.values_list('id', flat=True).iterator(chunk_size=LEGACY_BATCH_SIZE):
        PoliticaFinanceiraIgreja.objects.get_or_create(
            igreja_id=igreja_id,
            defaults={
                'approval_required': False,
                'segregation_level': 'LEVEL_1_SIMPLE',
                'version': 1,
            },
        )

    if legacy_max_pk is None:
        return

    legacy_event_payable_ids = set(
        ContaPagarAutorizacaoEvento.objects.filter(
            conta_pagar_id__lte=legacy_max_pk,
            event_type='LEGACY_MIGRATED',
        ).values_list('conta_pagar_id', flat=True)
    )
    legacy_contas = ContaPagar.objects.filter(pk__lte=legacy_max_pk).order_by('pk')

    for conta in legacy_contas.iterator(chunk_size=LEGACY_BATCH_SIZE):
        snapshot = _material_snapshot(conta)
        fingerprint = _material_fingerprint(snapshot)
        ContaPagar.objects.filter(pk=conta.pk).update(
            authorization_status='NOT_REQUIRED',
            authorization_origin='LEGACY_MIGRATION',
            authorization_policy_version=None,
            current_material_fingerprint=fingerprint,
            approved_material_fingerprint=None,
            approved_by_id=None,
            approved_at=None,
            rejected_by_id=None,
            rejected_at=None,
            current_rejection_reason=None,
        )
        if conta.pk in legacy_event_payable_ids:
            continue
        ContaPagarAutorizacaoEvento.objects.create(
            conta_pagar_id=conta.pk,
            event_type='LEGACY_MIGRATED',
            actor_id=None,
            actor_user_id_snapshot=None,
            actor_display_name_snapshot=None,
            authorization_status_before=None,
            authorization_status_after='NOT_REQUIRED',
            financial_status_before=None,
            financial_status_after=conta.status,
            material_fingerprint=fingerprint,
            material_snapshot=snapshot,
            policy_snapshot={
                'origin': 'LEGACY_MIGRATION',
                'historical_policy_known': False,
                'policy_id': None,
                'policy_version': None,
                'approval_required': None,
                'segregation_level': None,
            },
            reason=None,
            correlation_id=None,
        )


def reverse_prepayment_authorization(apps, schema_editor):
    ContaPagar = apps.get_model('financeiro', 'ContaPagar')
    ContaPagarAutorizacaoEvento = apps.get_model('financeiro', 'ContaPagarAutorizacaoEvento')
    legacy_event_ids = ContaPagarAutorizacaoEvento.objects.filter(
        event_type='LEGACY_MIGRATED',
    ).values_list('conta_pagar_id', flat=True)
    ContaPagar.objects.filter(pk__in=legacy_event_ids).update(
        authorization_status=None,
        authorization_origin=None,
        authorization_policy_version=None,
        current_material_fingerprint=None,
        approved_material_fingerprint=None,
        approved_by_id=None,
        approved_at=None,
        rejected_by_id=None,
        rejected_at=None,
        current_rejection_reason=None,
    )
    ContaPagarAutorizacaoEvento.objects.filter(event_type='LEGACY_MIGRATED').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0019_despesas_criado_por'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PoliticaFinanceiraIgreja',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approval_required', models.BooleanField(default=False, verbose_name='Exige Aprovacao Pre-Pagamento')),
                ('segregation_level', models.CharField(choices=[('LEVEL_1_SIMPLE', 'Nivel 1 - Simples'), ('LEVEL_2_CONTROLLED', 'Nivel 2 - Controlado'), ('LEVEL_3_STRONG', 'Nivel 3 - Forte')], default='LEVEL_1_SIMPLE', max_length=20, verbose_name='Nivel de Segregacao')),
                ('version', models.PositiveIntegerField(default=1, verbose_name='Versao da Politica')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('igreja', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='politica_financeira', to='configuracao.igreja', verbose_name='Igreja')),
            ],
            options={'verbose_name': 'Politica Financeira da Igreja', 'verbose_name_plural': 'Politicas Financeiras das Igrejas'},
        ),
        migrations.AddField(model_name='contapagar', name='authorization_status', field=models.CharField(blank=True, choices=[('NOT_REQUIRED', 'Nao Requerida'), ('PENDING', 'Pendente'), ('APPROVED', 'Aprovada'), ('REJECTED', 'Rejeitada')], max_length=12, null=True, verbose_name='Status de Autorizacao')),
        migrations.AddField(model_name='contapagar', name='authorization_origin', field=models.CharField(blank=True, choices=[('POLICY_NOT_REQUIRED', 'Politica sem Aprovacao'), ('POLICY_REQUIRED', 'Politica com Aprovacao'), ('USER_APPROVAL', 'Aprovacao de Usuario'), ('LEGACY_MIGRATION', 'Migracao de Legado')], max_length=24, null=True, verbose_name='Origem da Autorizacao')),
        migrations.AddField(model_name='contapagar', name='authorization_policy_version', field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Versao da Politica de Autorizacao')),
        migrations.AddField(model_name='contapagar', name='current_material_fingerprint', field=models.CharField(blank=True, max_length=74, null=True, verbose_name='Fingerprint Material Atual')),
        migrations.AddField(model_name='contapagar', name='approved_material_fingerprint', field=models.CharField(blank=True, max_length=74, null=True, verbose_name='Fingerprint Material Aprovado')),
        migrations.AddField(model_name='contapagar', name='approved_at', field=models.DateTimeField(blank=True, null=True, verbose_name='Aprovado em')),
        migrations.AddField(model_name='contapagar', name='rejected_at', field=models.DateTimeField(blank=True, null=True, verbose_name='Rejeitado em')),
        migrations.AddField(model_name='contapagar', name='current_rejection_reason', field=models.TextField(blank=True, null=True, verbose_name='Motivo Atual da Rejeicao')),
        migrations.AddField(model_name='contapagar', name='approved_by', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contas_pagar_autorizadas', to=settings.AUTH_USER_MODEL, verbose_name='Aprovado por')),
        migrations.AddField(model_name='contapagar', name='rejected_by', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contas_pagar_rejeitadas', to=settings.AUTH_USER_MODEL, verbose_name='Rejeitado por')),
        migrations.CreateModel(
            name='ContaPagarAutorizacaoEvento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('CREATED', 'Criado'), ('EDITED', 'Editado'), ('APPROVAL_REQUESTED', 'Aprovacao Solicitada'), ('APPROVED', 'Aprovado'), ('REJECTED', 'Rejeitado'), ('APPROVAL_INVALIDATED', 'Aprovacao Invalidada'), ('CANCELLED', 'Cancelado'), ('PAID', 'Pago'), ('LEGACY_MIGRATED', 'Legado Migrado')], max_length=24, verbose_name='Tipo de Evento')),
                ('actor_user_id_snapshot', models.PositiveBigIntegerField(blank=True, null=True, verbose_name='ID Historico do Ator')),
                ('actor_display_name_snapshot', models.CharField(blank=True, max_length=150, null=True, verbose_name='Nome Historico do Ator')),
                ('occurred_at', models.DateTimeField(auto_now_add=True, verbose_name='Ocorrido em')),
                ('authorization_status_before', models.CharField(blank=True, choices=[('NOT_REQUIRED', 'Nao Requerida'), ('PENDING', 'Pendente'), ('APPROVED', 'Aprovada'), ('REJECTED', 'Rejeitada')], max_length=12, null=True, verbose_name='Status de Autorizacao Anterior')),
                ('authorization_status_after', models.CharField(choices=[('NOT_REQUIRED', 'Nao Requerida'), ('PENDING', 'Pendente'), ('APPROVED', 'Aprovada'), ('REJECTED', 'Rejeitada')], max_length=12, verbose_name='Status de Autorizacao Posterior')),
                ('financial_status_before', models.CharField(blank=True, choices=[('PEN', 'Pendente'), ('PAG', 'Paga'), ('VEN', 'Vencida'), ('CAN', 'Cancelada')], max_length=3, null=True, verbose_name='Status Financeiro Anterior')),
                ('financial_status_after', models.CharField(choices=[('PEN', 'Pendente'), ('PAG', 'Paga'), ('VEN', 'Vencida'), ('CAN', 'Cancelada')], max_length=3, verbose_name='Status Financeiro Posterior')),
                ('material_fingerprint', models.CharField(blank=True, max_length=74, null=True, verbose_name='Fingerprint Material')),
                ('material_snapshot', models.JSONField(blank=True, null=True, verbose_name='Snapshot Material')),
                ('policy_snapshot', models.JSONField(blank=True, null=True, verbose_name='Snapshot da Politica')),
                ('reason', models.TextField(blank=True, null=True, verbose_name='Motivo')),
                ('correlation_id', models.UUIDField(blank=True, null=True, verbose_name='ID de Correlacao')),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='eventos_autorizacao_conta_pagar', to=settings.AUTH_USER_MODEL, verbose_name='Ator')),
                ('conta_pagar', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='eventos_autorizacao', to='financeiro.contapagar', verbose_name='Conta a Pagar')),
            ],
            options={'verbose_name': 'Evento de Autorizacao de Conta a Pagar', 'verbose_name_plural': 'Eventos de Autorizacao de Contas a Pagar', 'ordering': ['-occurred_at', '-id']},
        ),
        migrations.RunPython(backfill_prepayment_authorization, reverse_prepayment_authorization),
    ]