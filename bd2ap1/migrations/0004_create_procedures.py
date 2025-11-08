# Generated migration to create stored procedures

from django.db import migrations
from pathlib import Path


def load_procedures(apps, schema_editor):
    """Load and execute the procedures.sql file"""
    # Get the path to procedimentos.sql in the project root
    base_dir = Path(__file__).resolve().parent.parent.parent
    sql_file = base_dir / 'procedimentos.sql'
    
    if sql_file.exists():
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Execute the SQL
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(sql)
    else:
        raise FileNotFoundError(f"Could not find procedimentos.sql at {sql_file}")


def drop_procedures(apps, schema_editor):
    """Drop all procedures when reversing the migration"""
    sql = """
    DROP PROCEDURE IF EXISTS inserir_filme;
    DROP PROCEDURE IF EXISTS inserir_sessao;
    DROP PROCEDURE IF EXISTS inserir_produto;
    DROP PROCEDURE IF EXISTS inserir_avaliacao;
    DROP PROCEDURE IF EXISTS inserir_cinema;
    DROP PROCEDURE IF EXISTS inserir_cliente;
    DROP PROCEDURE IF EXISTS inserir_bilhete;
    DROP PROCEDURE IF EXISTS inserir_sala;
    """
    
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('bd2ap1', '0003_vendalinhas_bilheteid'),
    ]

    operations = [
        migrations.RunPython(load_procedures, reverse_code=drop_procedures),
    ]
