from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comunicacao', '0006_automacaoaniversariantes'),
    ]

    operations = [
        migrations.AddField(
            model_name='automacaoaniversariantes',
            name='followup_visitantes_ativo',
            field=models.BooleanField(default=False, verbose_name='Follow-up de visitantes ativo'),
        ),
        migrations.AddField(
            model_name='automacaoaniversariantes',
            name='followup_visitantes_dias_apos',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Dias apos a visita para follow-up'),
        ),
        migrations.AddField(
            model_name='automacaoaniversariantes',
            name='followup_visitantes_template',
            field=models.TextField(
                default='Ola {primeiro_nome}, foi uma alegria receber voce na {igreja}! Esperamos voce novamente no proximo encontro. Com carinho, equipe pastoral do {ministerio}.',
                verbose_name='Template WhatsApp follow-up visitante',
            ),
        ),
        migrations.AddField(
            model_name='automacaoaniversariantes',
            name='lembrete_eventos_ativo',
            field=models.BooleanField(default=False, verbose_name='Lembrete de eventos ativo'),
        ),
        migrations.AddField(
            model_name='automacaoaniversariantes',
            name='lembrete_eventos_template',
            field=models.TextField(
                default='{quando} teremos "{evento}" as {hora} na {igreja}. Esperamos voce!',
                verbose_name='Template WhatsApp lembrete de eventos',
            ),
        ),
    ]
