from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escola_biblica', '0029_fix_legacy_categoria_departamento_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avaliacao',
            name='licao',
            field=models.ForeignKey(on_delete=models.PROTECT, to='escola_biblica.licao'),
        ),
    ]
