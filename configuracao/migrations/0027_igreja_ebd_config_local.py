from django.db import migrations, models


def copiar_config_ebd_ministerio_para_igrejas(apps, schema_editor):
    Igreja = apps.get_model('configuracao', 'Igreja')
    ConfiguracaoSistema = apps.get_model('configuracao', 'ConfiguracaoSistema')

    configs_por_ministerio = {
        config.ministerio_id: config
        for config in ConfiguracaoSistema.objects.all()
        if config.ministerio_id is not None
    }

    igrejas = Igreja.objects.filter(ministerio_id__isnull=False)
    for igreja in igrejas.iterator():
        config = configs_por_ministerio.get(igreja.ministerio_id)
        if config is None:
            continue

        mudou = False
        if igreja.ebd_periodo is None and config.ebd_periodo is not None:
            igreja.ebd_periodo = config.ebd_periodo
            mudou = True
        if igreja.ebd_dia_semana is None and config.ebd_dia_semana is not None:
            igreja.ebd_dia_semana = config.ebd_dia_semana
            mudou = True
        if igreja.ebd_horario is None and config.ebd_horario is not None:
            igreja.ebd_horario = config.ebd_horario
            mudou = True

        if mudou:
            igreja.save(update_fields=['ebd_periodo', 'ebd_dia_semana', 'ebd_horario'])


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [
        ('configuracao', '0026_modelocartarecomendacao_and_seed'),
    ]

    operations = [
        migrations.AddField(
            model_name='igreja',
            name='ebd_dia_semana',
            field=models.IntegerField(
                blank=True,
                choices=[
                    (0, 'Segunda-feira'),
                    (1, 'Terça-feira'),
                    (2, 'Quarta-feira'),
                    (3, 'Quinta-feira'),
                    (4, 'Sexta-feira'),
                    (5, 'Sábado'),
                    (6, 'Domingo'),
                ],
                help_text='Opcional. Se preenchido, substitui o dia EBD herdado do ministério para esta igreja.',
                null=True,
                verbose_name='Dia da EBD (Igreja)',
            ),
        ),
        migrations.AddField(
            model_name='igreja',
            name='ebd_horario',
            field=models.TimeField(
                blank=True,
                help_text='Opcional. Se preenchido, substitui o horário EBD herdado do ministério para esta igreja.',
                null=True,
                verbose_name='Horário da EBD (Igreja)',
            ),
        ),
        migrations.AddField(
            model_name='igreja',
            name='ebd_periodo',
            field=models.CharField(
                blank=True,
                choices=[
                    ('trimestre', 'Trimestre'),
                    ('quadrimestre', 'Quadrimestre'),
                    ('semestre', 'Semestre'),
                    ('ano', 'Ano'),
                ],
                help_text='Opcional. Se preenchido, substitui o período EBD herdado do ministério para esta igreja.',
                max_length=20,
                null=True,
                verbose_name='Período da EBD (Igreja)',
            ),
        ),
        migrations.RunPython(copiar_config_ebd_ministerio_para_igrejas, noop_reverse),
    ]
