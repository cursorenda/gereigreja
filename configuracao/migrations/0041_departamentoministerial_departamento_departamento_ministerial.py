from django.db import migrations, models
import django.db.models.deletion


CODIGOS_CANONICOS_INICIAIS = {'MISSOES', 'ASSISTENCIA'}


def criar_definicoes_ministeriais_iniciais(apps, schema_editor):
    Departamento = apps.get_model('configuracao', 'Departamento')
    DepartamentoMinisterial = apps.get_model('configuracao', 'DepartamentoMinisterial')

    candidatos = Departamento.objects.filter(
        classificacao__in=['ORGANIZACIONAL', 'LEGADO_SUGERIDO'],
        codigo_interno__in=CODIGOS_CANONICOS_INICIAIS,
        tipo_departamento='PADRAO',
    ).select_related('igreja__ministerio').order_by('igreja__ministerio_id', 'ordem_exibicao', 'id')

    definicoes = {}
    for departamento in candidatos.iterator():
        ministerio_id = departamento.igreja.ministerio_id
        chave = (ministerio_id, departamento.codigo_interno)
        definicao = definicoes.get(chave)
        if definicao is None:
            definicao, _ = DepartamentoMinisterial.objects.get_or_create(
                ministerio_id=ministerio_id,
                codigo=departamento.codigo_interno,
                defaults={
                    'nome': departamento.nome_exibicao,
                    'ativo': departamento.ativo,
                    'ordem': departamento.ordem_exibicao,
                },
            )
            definicoes[chave] = definicao
        Departamento.objects.filter(
            pk=departamento.pk,
            departamento_ministerial__isnull=True,
        ).update(departamento_ministerial_id=definicao.id)


class Migration(migrations.Migration):

    dependencies = [
        ('configuracao', '0040_departamento_capacidades_e_classificacao'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepartamentoMinisterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=40, verbose_name='Código')),
                ('nome', models.CharField(max_length=120, verbose_name='Nome')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('ordem', models.PositiveIntegerField(default=100, verbose_name='Ordem')),
                ('ministerio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departamentos_ministeriais', to='configuracao.ministerio', verbose_name='Ministério')),
            ],
            options={
                'verbose_name': 'Departamento ministerial',
                'verbose_name_plural': 'Departamentos ministeriais',
                'ordering': ['ministerio__nome_fantasia', 'ordem', 'nome'],
            },
        ),
        migrations.AddField(
            model_name='departamento',
            name='departamento_ministerial',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='departamentos_locais', to='configuracao.departamentoministerial', verbose_name='Definição ministerial'),
        ),
        migrations.AddConstraint(
            model_name='departamentoministerial',
            constraint=models.UniqueConstraint(fields=('ministerio', 'codigo'), name='uniq_departamento_ministerial_codigo'),
        ),
        migrations.AddIndex(
            model_name='departamentoministerial',
            index=models.Index(fields=['ministerio', 'ativo', 'ordem'], name='dep_ministerial_list_idx'),
        ),
        migrations.RunPython(criar_definicoes_ministeriais_iniciais, migrations.RunPython.noop),
    ]
