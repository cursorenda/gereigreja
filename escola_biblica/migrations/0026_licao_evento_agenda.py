from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0012_participacaoevento_tipo_inclusao'),
        ('escola_biblica', '0025_backfill_licao_periodo'),
    ]

    operations = [
        migrations.AddField(
            model_name='licao',
            name='evento_agenda',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='licoes_ebd',
                to='eventos.evento',
                verbose_name='Evento da Agenda',
            ),
        ),
    ]
