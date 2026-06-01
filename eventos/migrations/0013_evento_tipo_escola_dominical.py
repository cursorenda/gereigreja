from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0012_participacaoevento_tipo_inclusao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='tipo',
            field=models.CharField(
                choices=[
                    ('culto', 'Culto'),
                    ('reuniao', 'Reunião'),
                    ('festa', 'Festa'),
                    ('feriado', 'Feriado'),
                    ('estudo', 'Estudo'),
                    ('escola_dominical', 'Escola Dominical'),
                    ('outro', 'Outro'),
                ],
                default='outro',
                max_length=20,
            ),
        ),
    ]
