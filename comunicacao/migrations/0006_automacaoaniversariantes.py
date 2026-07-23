from datetime import time

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracao', '0024_alter_historicoassinatura_tipo'),
        ('comunicacao', '0005_whatsapp_global_config'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutomacaoAniversariantes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('whatsapp_ativo', models.BooleanField(default=True, verbose_name='WhatsApp automatico ativo')),
                ('whatsapp_horario_envio', models.TimeField(default=time(9, 0), verbose_name='Horario do envio WhatsApp')),
                ('whatsapp_template', models.TextField(default='Feliz aniversario, {primeiro_nome}! Que o Senhor derrame paz, saude e alegria sobre sua vida. Com carinho, {ministerio}.', verbose_name='Template WhatsApp')),
                ('email_ativo', models.BooleanField(default=False, verbose_name='E-mail automatico ativo')),
                ('email_horario_envio', models.TimeField(default=time(8, 0), verbose_name='Horario do envio de e-mail')),
                ('email_assunto_template', models.CharField(default='Feliz aniversario, {primeiro_nome}!', max_length=160, verbose_name='Assunto do e-mail')),
                ('email_mensagem_template', models.TextField(default='<p>Ola, <strong>{nome}</strong>!</p><p>Desejamos um feliz aniversario, com paz, saude e a graca de Deus sobre sua vida.</p><p>Receba o carinho da equipe da {igreja} e de todo o {ministerio}.</p>', verbose_name='Mensagem do e-mail')),
                ('ultima_execucao_whatsapp', models.DateField(blank=True, null=True, verbose_name='Ultima execucao WhatsApp')),
                ('ultima_execucao_email', models.DateField(blank=True, null=True, verbose_name='Ultima execucao e-mail')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('ministerio', models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='automacao_aniversariantes', to='configuracao.ministerio', verbose_name='Ministerio')),
            ],
            options={
                'verbose_name': 'Automacao de aniversariantes',
                'verbose_name_plural': 'Automacoes de aniversariantes',
            },
        ),
    ]