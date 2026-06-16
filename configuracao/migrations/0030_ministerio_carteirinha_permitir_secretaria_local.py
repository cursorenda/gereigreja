from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracao', '0029_ministerio_logo_grande_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ministerio',
            name='carteirinha_permitir_secretaria_local',
            field=models.BooleanField(
                default=False,
                help_text='Se desmarcado, somente a secretaria ministerial/presidencia pode gerar e imprimir carteirinhas.',
                verbose_name='Permitir emissao da carteirinha pelas igrejas locais',
            ),
        ),
    ]
