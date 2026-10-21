from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0021_reconcile_financial_policies'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contapagar',
            options={
                'ordering': ['data_vencimento', 'status'],
                'permissions': [('approve_contapagar', 'Pode aprovar ou rejeitar contas a pagar')],
                'verbose_name': 'Conta a Pagar',
                'verbose_name_plural': 'Contas a Pagar',
            },
        ),
    ]