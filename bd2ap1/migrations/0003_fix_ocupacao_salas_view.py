# migrations/0003_fix_ocupacao_salas_view.py
from django.db import migrations


class Migration(migrations.Migration):
    
    dependencies = [
        ('bd2ap1', '0002_add_views_procedures_functions_triggers'),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Corrigir view para ocupação de salas (evitar divisão por zero)
            CREATE OR REPLACE VIEW v_ocupacao_salas AS
            SELECT 
                sa.salaid,
                c.nomecinema,
                sa.nomesala,
                sa.capacidade,
                sa.tiposala,
                COUNT(DISTINCT s.sessaoid) AS total_sessoes,
                COUNT(b.bilheteid) AS total_bilhetes_vendidos,
                CASE 
                    WHEN COUNT(DISTINCT s.sessaoid) = 0 THEN 0
                    ELSE ROUND((COUNT(b.bilheteid)::NUMERIC / (sa.capacidade * COUNT(DISTINCT s.sessaoid)) * 100), 2)
                END AS taxa_ocupacao_media
            FROM salas sa
            JOIN cinemas c ON sa.cinemaid = c.cinemaid
            LEFT JOIN sessoes s ON sa.salaid = s.salaid
            LEFT JOIN bilhetes b ON s.sessaoid = b.sessaoid
            GROUP BY sa.salaid, c.nomecinema, sa.nomesala, sa.capacidade, sa.tiposala
            ORDER BY taxa_ocupacao_media DESC;
            """,
            "-- Rollback não necessário, apenas correção"
        ),
    ]