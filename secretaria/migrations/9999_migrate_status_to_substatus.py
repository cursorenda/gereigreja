from django.db import migrations

def migrate_status_to_substatus(apps, schema_editor):
    Pessoa = apps.get_model('secretaria', 'Pessoa')
    StatusPessoa = apps.get_model('secretaria', 'StatusPessoa')
    # Busca o id do status "Inativo"
    try:
        status_inativo = StatusPessoa.objects.get(nome__iexact='Inativo')
    except StatusPessoa.DoesNotExist:
        status_inativo = None
    if not status_inativo:
        return
    # Mapeamento de status antigos para sub status
    status_map = {
        'Falecido': 'FALECIDO',
        'Mudou': 'MUDOU',
        'Transferido': 'TRANSFERIDO',
    }
    for old_status, sub_status in status_map.items():
        try:
            status_antigo = StatusPessoa.objects.get(nome__iexact=old_status)
        except StatusPessoa.DoesNotExist:
            continue
        # Atualiza todas as pessoas com o status antigo
        for pessoa in Pessoa.objects.filter(status_pessoa=status_antigo):
            pessoa.status_pessoa = status_inativo
            pessoa.sub_status_inativo = sub_status
            pessoa.save()

class Migration(migrations.Migration):
    dependencies = [
        ('secretaria', '0026_pessoa_sub_status_inativo'),
    ]
    operations = [
        migrations.RunPython(migrate_status_to_substatus),
    ]
