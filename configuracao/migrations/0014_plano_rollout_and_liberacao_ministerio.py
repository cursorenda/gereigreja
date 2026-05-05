from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracao', '0013_add_url_biblia_harpa'),
    ]

    operations = [
        migrations.AddField(
            model_name='plano',
            name='contratacao_publica_liberada',
            field=models.BooleanField(default=False, help_text='Controla se este plano pode ser contratado por qualquer ministério fora da lista piloto.', verbose_name='Contratação pública liberada?'),
        ),
        migrations.AddField(
            model_name='plano',
            name='liberado_publicamente',
            field=models.BooleanField(default=False, help_text='Controla se este plano pode aparecer para todos os usuários nos fluxos do sistema.', verbose_name='Liberado publicamente?'),
        ),
        migrations.AddField(
            model_name='plano',
            name='ordem_liberacao',
            field=models.PositiveIntegerField(default=0, help_text='Ajuda a organizar o rollout gradual dos planos.', verbose_name='Ordem de liberação'),
        ),
        migrations.AlterField(
            model_name='plano',
            name='nome',
            field=models.CharField(choices=[('pioneiro', 'Pioneiro'), ('crescimento', 'Crescimento'), ('ministerio', 'Ministério'), ('rede', 'Rede')], max_length=50, unique=True, verbose_name='Nome do Plano'),
        ),
        migrations.CreateModel(
            name='LiberacaoPlanoMinisterio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pode_visualizar', models.BooleanField(default=True, verbose_name='Pode visualizar?')),
                ('pode_contratar', models.BooleanField(default=True, verbose_name='Pode contratar?')),
                ('acesso_beta', models.BooleanField(default=True, verbose_name='Acesso beta?')),
                ('ativo', models.BooleanField(default=True, verbose_name='Liberação ativa?')),
                ('observacao', models.TextField(blank=True, null=True, verbose_name='Observação')),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('ministerio', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='liberacoes_planos', to='configuracao.ministerio', verbose_name='Ministério')),
                ('plano', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='liberacoes_ministerios', to='configuracao.plano', verbose_name='Plano')),
            ],
            options={
                'verbose_name': 'Liberação de Plano por Ministério',
                'verbose_name_plural': 'Liberações de Planos por Ministério',
                'ordering': ['ministerio__nome_fantasia', 'plano__ordem_liberacao', 'plano__preco_mensal'],
                'unique_together': {('ministerio', 'plano')},
            },
        ),
    ]