from django.db import migrations
from django.db.models import Count


def validate_unique_expense_mirror_origins(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Despesas = apps.get_model('financeiro', 'Despesas')
    duplicates = list(
        Despesas.objects.using(db_alias)
        .exclude(origem_conta_pagar_id__isnull=True)
        .values('origem_conta_pagar_id')
        .annotate(total=Count('id'))
        .filter(total__gt=1)
        .order_by('origem_conta_pagar_id')[:10]
    )

    if duplicates:
        sample = ', '.join(
            f"origem_conta_pagar_id={item['origem_conta_pagar_id']} (total={item['total']})"
            for item in duplicates
        )
        raise RuntimeError(
            'A constraint financeiro_unique_despesa_origem_conta_pagar não pode ser aplicada: '
            'existem ContaPagar com múltiplas Despesas espelho. É necessária investigação manual; '
            'nenhuma correção automática foi realizada. Amostra: '
            f'{sample}'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0022_contapagar_formal_decision_permission'),
    ]

    operations = [
        migrations.RunPython(validate_unique_expense_mirror_origins, migrations.RunPython.noop),
    ]
