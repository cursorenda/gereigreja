from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('escola_biblica', '0030_alter_avaliacao_licao_protect'),
    ]

    operations = [
        migrations.CreateModel(
            name='FechamentoPeriodoEBD',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fechado_em', models.DateTimeField(auto_now_add=True)),
                ('fechado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fechamentos_periodo_ebd_realizados', to=settings.AUTH_USER_MODEL)),
                ('igreja', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fechamentos_ebd', to='configuracao.igreja')),
                ('periodo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fechamentos_por_igreja', to='escola_biblica.periodoebd')),
            ],
            options={
                'verbose_name': 'Fechamento de Período EBD',
                'verbose_name_plural': 'Fechamentos de Períodos EBD',
                'ordering': ['-fechado_em'],
            },
        ),
        migrations.AddConstraint(
            model_name='fechamentoperiodoebd',
            constraint=models.UniqueConstraint(fields=('periodo', 'igreja'), name='uq_fechamento_ebd_periodo_igreja'),
        ),
    ]
