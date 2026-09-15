from django.db import migrations, models


def marcar_tenant_demo_historico(apps, schema_editor):
    """
    Marca o tenant Demo historico com is_demo=True.

    Regra: combina suficiente para evitar falso positivo:
    - CNPJ reservado usado exclusivamente pelo popular_demo: '00.000.000/0001-00'
    - E administrador principal com username prefixado com 'admin_demo'

    Esta heurística existe SOMENTE nesta data migration historica.
    Runtime deve depender exclusivamente de Ministerio.is_demo.
    """
    Ministerio = apps.get_model('configuracao', 'Ministerio')
    User = apps.get_model('auth', 'User')

    # Busca o admin_demo user
    admin_demo = User.objects.filter(username='admin_demo').first()
    if not admin_demo:
        return

    # Marca apenas se atender AMBOS os criterios simultaneamente
    marcados = Ministerio.objects.filter(
        cnpj='00.000.000/0001-00',
        administrador_principal=admin_demo,
    ).update(is_demo=True)

    # Log para auditoria (visivel em migrate --verbosity 2)
    if marcados:
        print(f"  -> {marcados} tenant(s) Demo marcado(s) com is_demo=True")


class Migration(migrations.Migration):

    dependencies = [
        ('configuracao', '0042_departamentovinculo'),
    ]

    operations = [
        migrations.AddField(
            model_name='ministerio',
            name='is_demo',
            field=models.BooleanField(
                default=False,
                verbose_name='É ministério de demonstração',
                help_text='Identifica este ministério como ambiente de demonstração isolado. '
                          'Quando True, efeitos externos (WhatsApp/e-mail) são neutralizados.',
                db_index=True,
            ),
        ),
        migrations.RunPython(
            marcar_tenant_demo_historico,
            migrations.RunPython.noop,
        ),
    ]
