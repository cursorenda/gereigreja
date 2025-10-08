from django.db import migrations

def set_igreja_for_agenda_eventos(apps, schema_editor):
    AgendaEvento = apps.get_model('agenda', 'AgendaEvento')
    Igreja = apps.get_model('configuracao', 'Igreja')
    # Seleciona a primeira igreja do ministério 1
    igreja = Igreja.objects.filter(ministerio_id=1).first()
    if igreja:
        AgendaEvento.objects.filter(igreja__isnull=True).update(igreja=igreja)

def reverse_func(apps, schema_editor):
    # Não é necessário desfazer
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('agenda', '0002_agendaevento_igreja'),
    ]

    operations = [
        migrations.RunPython(set_igreja_for_agenda_eventos, reverse_func),
    ]
