from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0016_departamentofinanceiro_departamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='fechamentocaixa',
            name='fundo_departamental',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='fechamentos_caixa',
                to='financeiro.fundodepartamental',
                verbose_name='Fundo Departamental (Opcional)',
            ),
        ),
    ]
