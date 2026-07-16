from django.db import migrations


LEGACY_COLUMN = 'categoria_departamento'
TABLE_NAME = 'escola_biblica_classe'
DEFAULT_VALUE = 'INFANTIL'


def _column_names(schema_editor, table_name):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        description = connection.introspection.get_table_description(cursor, table_name)
    return {col.name for col in description}


def forwards(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor != 'postgresql':
        return

    table_names = set(connection.introspection.table_names())
    if TABLE_NAME not in table_names:
        return

    columns = _column_names(schema_editor, TABLE_NAME)
    if LEGACY_COLUMN not in columns:
        return

    with connection.cursor() as cursor:
        if 'departamento' in columns:
            cursor.execute(
                f"""
                UPDATE {TABLE_NAME}
                SET {LEGACY_COLUMN} = COALESCE(NULLIF(departamento, ''), %s)
                WHERE {LEGACY_COLUMN} IS NULL OR {LEGACY_COLUMN} = ''
                """,
                [DEFAULT_VALUE],
            )
        else:
            cursor.execute(
                f"""
                UPDATE {TABLE_NAME}
                SET {LEGACY_COLUMN} = %s
                WHERE {LEGACY_COLUMN} IS NULL OR {LEGACY_COLUMN} = ''
                """,
                [DEFAULT_VALUE],
            )

        cursor.execute(
            f"ALTER TABLE {TABLE_NAME} ALTER COLUMN {LEGACY_COLUMN} SET DEFAULT %s",
            [DEFAULT_VALUE],
        )


def backwards(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor != 'postgresql':
        return

    table_names = set(connection.introspection.table_names())
    if TABLE_NAME not in table_names:
        return

    columns = _column_names(schema_editor, TABLE_NAME)
    if LEGACY_COLUMN not in columns:
        return

    with connection.cursor() as cursor:
        cursor.execute(
            f"ALTER TABLE {TABLE_NAME} ALTER COLUMN {LEGACY_COLUMN} DROP DEFAULT"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('escola_biblica', '0028_backfill_frequencia_pontos_total'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
