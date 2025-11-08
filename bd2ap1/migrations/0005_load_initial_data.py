# Generated migration to load initial data from fill.sql

from django.db import migrations
from pathlib import Path


def load_initial_data(apps, schema_editor):
    """Load and execute the fill.sql file"""
    # Get the path to fill.sql in the project root
    base_dir = Path(__file__).resolve().parent.parent.parent
    sql_file = base_dir / 'fill.sql'
    
    if sql_file.exists():
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Execute the SQL
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(sql)
    else:
        raise FileNotFoundError(f"Could not find fill.sql at {sql_file}")


def remove_initial_data(apps, schema_editor):
    """Remove all data when reversing the migration"""
    sql = """
    TRUNCATE TABLE avaliacoes CASCADE;
    TRUNCATE TABLE vendalinhas CASCADE;
    TRUNCATE TABLE bilhetes CASCADE;
    TRUNCATE TABLE vendas CASCADE;
    TRUNCATE TABLE produtos CASCADE;
    TRUNCATE TABLE funcionarios CASCADE;
    TRUNCATE TABLE clientes CASCADE;
    TRUNCATE TABLE sessoes CASCADE;
    TRUNCATE TABLE lugares CASCADE;
    TRUNCATE TABLE filmes CASCADE;
    TRUNCATE TABLE salas CASCADE;
    TRUNCATE TABLE cinemas CASCADE;
    TRUNCATE TABLE classificacoesetarias CASCADE;
    TRUNCATE TABLE categorias CASCADE;
    """
    
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('bd2ap1', '0004_create_procedures'),
    ]

    operations = [
        migrations.RunPython(load_initial_data, reverse_code=remove_initial_data),
    ]
