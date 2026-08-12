from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0017_fechamentocaixa_fundo_departamental'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='despesas',
            name='aprovacao_status',
            field=models.CharField(
                choices=[('PENDENTE', 'Pendente'), ('APROVADA', 'Aprovada'), ('REJEITADA', 'Rejeitada')],
                default='APROVADA',
                max_length=20,
                verbose_name='Status de Aprovacao',
            ),
        ),
        migrations.AddField(
            model_name='despesas',
            name='aprovado_em',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Aprovado em'),
        ),
        migrations.AddField(
            model_name='despesas',
            name='aprovado_por',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='despesas_aprovadas',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Aprovado por',
            ),
        ),
        migrations.AddField(
            model_name='despesas',
            name='observacao_aprovacao',
            field=models.TextField(blank=True, null=True, verbose_name='Observacao da Aprovacao'),
        ),
    ]
