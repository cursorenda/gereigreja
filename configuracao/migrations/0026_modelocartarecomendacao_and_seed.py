from django.db import migrations, models


def seed_modelos_carta(apps, schema_editor):
    Ministerio = apps.get_model('configuracao', 'Ministerio')
    ModeloCartaRecomendacao = apps.get_model('configuracao', 'ModeloCartaRecomendacao')

    ModeloCartaRecomendacao.objects.get_or_create(
        codigo='padrao',
        defaults={
            'nome': 'Padrao do sistema',
            'template_include': 'secretaria/documentos/modelos/_carta_recomendacao_padrao.html',
            'tipo': 'padrao',
            'ativo': True,
            'ordem': 10,
        },
    )

    ministerio_vales = Ministerio.objects.filter(nome_fantasia__icontains='vales').order_by('id').first()
    ModeloCartaRecomendacao.objects.get_or_create(
        codigo='vales_classico',
        defaults={
            'nome': 'Ministerio dos Vales (Classico)',
            'template_include': 'secretaria/documentos/modelos/_carta_recomendacao_vales_classico.html',
            'tipo': 'exclusivo',
            'ministerio': ministerio_vales,
            'ativo': True,
            'ordem': 20,
        },
    )


def unseed_modelos_carta(apps, schema_editor):
    ModeloCartaRecomendacao = apps.get_model('configuracao', 'ModeloCartaRecomendacao')
    ModeloCartaRecomendacao.objects.filter(codigo__in=['padrao', 'vales_classico']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('configuracao', '0025_ministerio_modelo_carta_recomendacao'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModeloCartaRecomendacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Identificador unico do modelo (ex: padrao, vales_classico).', max_length=60, unique=True, verbose_name='Codigo tecnico')),
                ('nome', models.CharField(max_length=120, verbose_name='Nome do modelo')),
                ('template_include', models.CharField(help_text='Caminho do include Django (ex: secretaria/documentos/modelos/_carta_recomendacao_padrao.html).', max_length=255, verbose_name='Template include')),
                ('tipo', models.CharField(choices=[('padrao', 'Padrao'), ('exclusivo', 'Exclusivo')], default='padrao', max_length=20)),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('ordem', models.PositiveIntegerField(default=100, verbose_name='Ordem')),
                ('ministerio', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='modelos_carta_exclusivos', to='configuracao.ministerio', verbose_name='Ministerio dono (quando exclusivo)')),
            ],
            options={
                'verbose_name': 'Modelo de Carta de Recomendacao',
                'verbose_name_plural': 'Modelos de Carta de Recomendacao',
                'ordering': ['ordem', 'nome'],
            },
        ),
        migrations.AlterField(
            model_name='ministerio',
            name='modelo_carta_recomendacao',
            field=models.CharField(blank=True, default='padrao', help_text='Codigo do modelo selecionado para carta de recomendacao.', max_length=40, verbose_name='Modelo da Carta de Recomendacao'),
        ),
        migrations.RunPython(seed_modelos_carta, unseed_modelos_carta),
    ]
