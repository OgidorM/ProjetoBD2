# Generated manually

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('vendas_front', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DROP MATERIALIZED VIEW IF EXISTS mv_vendas_diarias;
            CREATE MATERIALIZED VIEW mv_vendas_diarias AS
            SELECT
                v.data AS data,
                COUNT(v.vendaid) AS total_transacoes,
                SUM(v.totalvenda) AS total_faturado
            FROM
                vendas v
            GROUP BY
                v.data;
            """,
            reverse_sql="""
            DROP MATERIALIZED VIEW IF EXISTS mv_vendas_diarias;
            CREATE MATERIALIZED VIEW mv_vendas_diarias AS
            SELECT
                v.data AS dia,
                COUNT(v.vendaid) AS total_vendas,
                SUM(v.totalvenda) AS valor_total
            FROM
                vendas v
            GROUP BY
                v.data;
            """
        ),
    ]
