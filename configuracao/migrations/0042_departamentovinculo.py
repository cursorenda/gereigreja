from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('configuracao', '0041_departamentoministerial_departamento_departamento_ministerial'),
        ('secretaria', '10008_pessoa_naturalidade_cidade'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepartamentoVinculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_inicio', models.DateField(default=django.utils.timezone.localdate, verbose_name='Data de inicio')),
                ('data_fim', models.DateField(blank=True, null=True, verbose_name='Data de fim')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('cargo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vinculos_departamentais', to='secretaria.cargo', verbose_name='Cargo no departamento')),
                ('criado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vinculos_departamentais_criados', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('departamento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='vinculos', to='configuracao.departamento', verbose_name='Departamento')),
                ('encerrado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vinculos_departamentais_encerrados', to=settings.AUTH_USER_MODEL, verbose_name='Encerrado por')),
                ('membro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='vinculos_departamentais', to='secretaria.pessoa', verbose_name='Membro')),
            ],
            options={
                'verbose_name': 'Vinculo de departamento',
                'verbose_name_plural': 'Vinculos de departamentos',
                'ordering': ['departamento', 'membro__nome', '-data_inicio', '-id'],
            },
        ),
        migrations.AddConstraint(
            model_name='departamentovinculo',
            constraint=models.UniqueConstraint(condition=models.Q(('data_fim__isnull', True)), fields=('departamento', 'membro'), name='uniq_dep_vinculo_ativo_membro'),
        ),
        migrations.AddConstraint(
            model_name='departamentovinculo',
            constraint=models.CheckConstraint(condition=models.Q(('data_fim__isnull', True), ('data_fim__gte', models.F('data_inicio')), _connector='OR'), name='dep_vinculo_datas_validas'),
        ),
        migrations.AddIndex(
            model_name='departamentovinculo',
            index=models.Index(fields=['departamento', 'data_fim'], name='dep_vinculo_dep_fim_idx'),
        ),
        migrations.AddIndex(
            model_name='departamentovinculo',
            index=models.Index(fields=['membro', 'data_fim'], name='dep_vinculo_membro_fim_idx'),
        ),
    ]
