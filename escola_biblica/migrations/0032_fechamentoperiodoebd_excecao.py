from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escola_biblica', '0031_fechamentoperiodoebd'),
    ]

    operations = [
        migrations.AddField(
            model_name='fechamentoperiodoebd',
            name='motivo_excecao',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='fechamentoperiodoebd',
            name='tipo',
            field=models.CharField(choices=[('normal', 'Fechamento normal'), ('excecao', 'Fechamento com exceção')], default='normal', max_length=12),
        ),
    ]
