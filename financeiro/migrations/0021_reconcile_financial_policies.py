from django.db import migrations


POLICY_RECONCILIATION_BATCH_SIZE = 500


def reconcile_financial_policies(apps, schema_editor):
    Igreja = apps.get_model('configuracao', 'Igreja')
    PoliticaFinanceiraIgreja = apps.get_model(
        'financeiro',
        'PoliticaFinanceiraIgreja',
    )

    for igreja_id in Igreja.objects.values_list('id', flat=True).iterator(
        chunk_size=POLICY_RECONCILIATION_BATCH_SIZE,
    ):
        PoliticaFinanceiraIgreja.objects.get_or_create(
            igreja_id=igreja_id,
            defaults={
                'approval_required': False,
                'segregation_level': 'LEVEL_1_SIMPLE',
                'version': 1,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0020_prepayment_authorization_expansive'),
    ]

    operations = [
        migrations.RunPython(
            reconcile_financial_policies,
            migrations.RunPython.noop,
        ),
    ]