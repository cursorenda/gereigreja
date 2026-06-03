from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escola_biblica', '0026_licao_evento_agenda'),
    ]

    operations = [
        migrations.AddField(
            model_name='frequencia',
            name='pontos_total',
            field=models.IntegerField(blank=True, help_text='Snapshot de pontos computado no momento do registro da chamada.', null=True, verbose_name='Pontos totais da aula'),
        ),
    ]
