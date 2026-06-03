from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracao', '0027_igreja_ebd_config_local'),
    ]

    operations = [
        migrations.AddField(
            model_name='igreja',
            name='ebd_pontos_biblia',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Opcional. Pontos atribuídos quando o aluno marca Bíblia na chamada.', null=True, verbose_name='Pontos por Bíblia'),
        ),
        migrations.AddField(
            model_name='igreja',
            name='ebd_pontos_oferta',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Opcional. Pontos atribuídos quando o aluno marca Oferta na chamada.', null=True, verbose_name='Pontos por Oferta'),
        ),
        migrations.AddField(
            model_name='igreja',
            name='ebd_pontos_presente',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Opcional. Pontos atribuídos quando o aluno está presente na chamada.', null=True, verbose_name='Pontos por Presença'),
        ),
        migrations.AddField(
            model_name='igreja',
            name='ebd_pontos_revista',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Opcional. Pontos atribuídos quando o aluno marca Revista na chamada.', null=True, verbose_name='Pontos por Revista'),
        ),
        migrations.AddField(
            model_name='igreja',
            name='ebd_pontos_visitante',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Opcional. Pontos atribuídos quando o aluno marca Visitante na chamada.', null=True, verbose_name='Pontos por Visitante'),
        ),
    ]
