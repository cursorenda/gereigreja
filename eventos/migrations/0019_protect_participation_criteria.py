from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("eventos", "0018_alter_evento_tipo"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="EventoTipoParticipante",
                    fields=[
                        ("id", models.BigAutoField(primary_key=True, serialize=False)),
                        ("evento", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="+", to="eventos.evento")),
                        ("tipopessoa", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="secretaria.tipopessoa")),
                    ],
                    options={
                        "db_table": "eventos_evento_tipos_participantes",
                        "unique_together": {("evento", "tipopessoa")},
                    },
                ),
                migrations.CreateModel(
                    name="EventoStatusParticipante",
                    fields=[
                        ("id", models.BigAutoField(primary_key=True, serialize=False)),
                        ("evento", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="+", to="eventos.evento")),
                        ("statuspessoa", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="secretaria.statuspessoa")),
                    ],
                    options={
                        "db_table": "eventos_evento_status_participantes",
                        "unique_together": {("evento", "statuspessoa")},
                    },
                ),
                migrations.AlterField(
                    model_name="evento",
                    name="tipos_participantes",
                    field=models.ManyToManyField(
                        to="secretaria.tipopessoa", through="eventos.EventoTipoParticipante",
                        blank=True, related_name="eventos_por_tipo",
                        verbose_name="Tipos de Pessoas Esperadas",
                        help_text="Selecione os tipos de pessoas esperadas para este evento.",
                    ),
                ),
                migrations.AlterField(
                    model_name="evento",
                    name="status_participantes",
                    field=models.ManyToManyField(
                        to="secretaria.statuspessoa", through="eventos.EventoStatusParticipante",
                        blank=True, related_name="eventos_por_status",
                        verbose_name="Status de Pessoas Esperadas",
                        help_text="Selecione os status de pessoas esperadas para este evento.",
                    ),
                ),
            ],
        ),
    ]
