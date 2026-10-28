from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0023_preflight_despesa_origem_conta_pagar_uniqueness'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='despesas',
            constraint=models.UniqueConstraint(
                fields=('origem_conta_pagar',),
                name='financeiro_unique_despesa_origem_conta_pagar',
            ),
        ),
    ]
