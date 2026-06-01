from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0013_evento_tipo_escola_dominical'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='cancelado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='cancelado_por',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='eventos_cancelados',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='evento',
            name='motivo_cancelamento',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='status_evento',
            field=models.CharField(
                choices=[('ativo', 'Ativo'), ('cancelado', 'Cancelado')],
                default='ativo',
                max_length=20,
            ),
        ),
    ]
