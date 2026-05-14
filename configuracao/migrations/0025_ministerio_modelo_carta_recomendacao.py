from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracao', '0024_alter_historicoassinatura_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='ministerio',
            name='modelo_carta_recomendacao',
            field=models.CharField(
                choices=[
                    ('padrao', 'Padrao do sistema'),
                    ('vales_classico', 'Ministerio dos Vales (Classico)'),
                ],
                default='padrao',
                help_text='Define qual layout de carta de recomendacao sera usado por este ministerio.',
                max_length=40,
                verbose_name='Modelo da Carta de Recomendacao',
            ),
        ),
    ]
