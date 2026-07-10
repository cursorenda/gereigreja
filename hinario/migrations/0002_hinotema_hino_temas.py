from django.db import migrations, models


def criar_temas_padrao(apps, schema_editor):
    HinoTema = apps.get_model('hinario', 'HinoTema')

    temas = [
        ('Adoração', 'adoracao', 'Hinos de exaltação e adoração a Deus.'),
        ('Santa Ceia', 'santa-ceia', 'Hinos para momentos de ceia do Senhor.'),
        ('Céu', 'ceu', 'Hinos sobre esperança eterna e vida com Cristo.'),
        ('Evangelismo', 'evangelismo', 'Hinos voltados para convite e salvação.'),
        ('Missões', 'missoes', 'Hinos missionários e de envio.'),
        ('Batismo', 'batismo', 'Hinos para cultos e celebrações de batismo.'),
        ('Consagração', 'consagracao', 'Hinos de entrega, rendição e santificação.'),
        ('Gratidão', 'gratidao', 'Hinos de ações de graças e testemunho.'),
        ('Oração', 'oracao', 'Hinos para clamor, intercessão e comunhão.'),
        ('Comunhão', 'comunhao', 'Hinos de unidade e edificação da igreja.'),
    ]

    for nome, slug, descricao in temas:
        HinoTema.objects.update_or_create(
            slug=slug,
            defaults={
                'nome': nome,
                'descricao': descricao,
                'ativo': True,
            },
        )


def remover_temas_padrao(apps, schema_editor):
    HinoTema = apps.get_model('hinario', 'HinoTema')
    HinoTema.objects.filter(
        slug__in=[
            'adoracao',
            'santa-ceia',
            'ceu',
            'evangelismo',
            'missoes',
            'batismo',
            'consagracao',
            'gratidao',
            'oracao',
            'comunhao',
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('hinario', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HinoTema',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=80, unique=True, verbose_name='Nome do tema')),
                ('slug', models.SlugField(help_text='Identificador curto para filtros e URLs.', max_length=80, unique=True, verbose_name='Slug')),
                ('descricao', models.CharField(blank=True, max_length=180, null=True, verbose_name='Descrição')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo?')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': 'Tema de Hino',
                'verbose_name_plural': 'Temas de Hino',
                'ordering': ['nome'],
                'indexes': [models.Index(fields=['slug'], name='hinario_hin_slug_6d63db_idx'), models.Index(fields=['ativo'], name='hinario_hin_ativo_06e844_idx')],
            },
        ),
        migrations.AddField(
            model_name='hinoglobal',
            name='temas',
            field=models.ManyToManyField(blank=True, help_text='Classificação por tema: Adoração, Santa Ceia, Céu, etc.', related_name='hinos_globais', to='hinario.hinotema', verbose_name='Temas'),
        ),
        migrations.AddField(
            model_name='hinodaigreja',
            name='temas',
            field=models.ManyToManyField(blank=True, help_text='Classificação por tema: Adoração, Santa Ceia, Céu, etc.', related_name='hinos_igreja', to='hinario.hinotema', verbose_name='Temas'),
        ),
        migrations.RunPython(criar_temas_padrao, remover_temas_padrao),
    ]
