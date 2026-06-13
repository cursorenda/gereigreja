from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secretaria', '10004_pessoa_grau_eclesiastico'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statushistorico',
            name='data_transicao',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
