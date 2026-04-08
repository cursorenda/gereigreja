# Generated migration for HierarquiaPermissoes model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contas', '0002_permissionrequest'),
        ('configuracao', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HierarquiaPermissoes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nivel_superior', models.CharField(
                    choices=[
                        ('Admin Ministerio', 'Admin Ministério'),
                        ('Pastor Regional', 'Pastor Regional'),
                        ('Pastor Local', 'Pastor Local'),
                    ],
                    max_length=50,
                    verbose_name='Nível do Superior'
                )),
                ('data_vinculo', models.DateTimeField(auto_now_add=True, verbose_name='Data do Vínculo')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('usuario_subordinado', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='vinculos_subordinacao',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Usuário Subordinado'
                )),
                ('usuario_superior', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='vinculos_supervisao',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Usuário Superior'
                )),
                ('igreja', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='hierarquias_permissoes',
                    to='configuracao.igreja',
                    verbose_name='Igreja (Contexto)'
                )),
            ],
            options={
                'verbose_name': 'Hierarquia de Permissões',
                'verbose_name_plural': 'Hierarquias de Permissões',
                'ordering': ['-data_vinculo'],
                'unique_together': {('usuario_superior', 'usuario_subordinado', 'nivel_superior')},
            },
        ),
    ]
