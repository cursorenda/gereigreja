from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("secretaria", "0012_remove_membroscargos_cargo_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cargo",
            name="is_ebd",
            field=models.BooleanField(default=False, verbose_name="É da EBD?", help_text="Marque se este cargo pertence à Escola Bíblica Dominical."),
        ),
    ]
