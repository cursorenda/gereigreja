from django.db import migrations


def rename_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Lideranca Secretaria').update(name='Secretaria Ministerial')
    Group.objects.filter(name='Lideranca Financeira').update(name='Tesouraria Ministerial')


def reverse_rename_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Secretaria Ministerial').update(name='Lideranca Secretaria')
    Group.objects.filter(name='Tesouraria Ministerial').update(name='Lideranca Financeira')


class Migration(migrations.Migration):

    dependencies = [
        ('contas', '0005_add_consentimento_lgpd'),
    ]

    operations = [
        migrations.RunPython(rename_grupos, reverse_code=reverse_rename_grupos),
    ]