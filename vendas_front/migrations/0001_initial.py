# Generated manually

from django.db import migrations

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bd2ap1', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_vendas_diarias AS
            SELECT
                v.data AS dia,
                COUNT(v.vendaid) AS total_vendas,
                SUM(v.totalvenda) AS valor_total
            FROM
                vendas v
            GROUP BY
                v.data;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS mv_vendas_diarias;"
        ),
    ]
