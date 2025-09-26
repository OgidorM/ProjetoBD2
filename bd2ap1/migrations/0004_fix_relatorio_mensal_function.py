# migrations/0004_fix_relatorio_mensal_function.py
from django.db import migrations


class Migration(migrations.Migration):
    
    dependencies = [
        ('bd2ap1', '0003_fix_ocupacao_salas_view'),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Corrigir function relatorio_mensal (evitar funções agregadas aninhadas)
            CREATE OR REPLACE FUNCTION relatorio_mensal(
                p_mes INTEGER,
                p_ano INTEGER,
                p_cinemaid INTEGER DEFAULT NULL
            ) RETURNS TABLE(
                cinema VARCHAR(80),
                total_sessoes BIGINT,
                total_bilhetes BIGINT,
                receita_total NUMERIC,
                filme_mais_popular VARCHAR(120),
                taxa_ocupacao_media NUMERIC
            )
            LANGUAGE plpgsql AS $$
            BEGIN
                RETURN QUERY
                WITH vendas_periodo AS (
                    SELECT v.*, f.cinemaid
                    FROM vendas v
                    JOIN funcionarios f ON v.funcionarioid = f.funcionarioid
                    WHERE EXTRACT(MONTH FROM v.data) = p_mes
                    AND EXTRACT(YEAR FROM v.data) = p_ano
                    AND (p_cinemaid IS NULL OR f.cinemaid = p_cinemaid)
                ),
                stats AS (
                    SELECT 
                        c.cinemaid,
                        c.nomecinema,
                        COUNT(DISTINCT s.sessaoid) as sessoes,
                        COUNT(b.bilheteid) as bilhetes,
                        COALESCE(SUM(b.precobilhete), 0) as receita
                    FROM cinemas c
                    LEFT JOIN vendas_periodo vp ON c.cinemaid = vp.cinemaid
                    LEFT JOIN vendalinhas vl ON vp.vendaid = vl.vendaid
                    LEFT JOIN bilhetes b ON vl.bilheteid = b.bilheteid
                    LEFT JOIN sessoes s ON b.sessaoid = s.sessaoid
                    GROUP BY c.cinemaid, c.nomecinema
                ),
                ocupacao_stats AS (
                    SELECT 
                        c.cinemaid,
                        CASE 
                            WHEN COUNT(DISTINCT s.sessaoid) = 0 THEN 0::NUMERIC
                            ELSE ROUND(AVG(sa.capacidade), 2)
                        END as ocupacao_media
                    FROM cinemas c
                    LEFT JOIN vendas_periodo vp ON c.cinemaid = vp.cinemaid
                    LEFT JOIN vendalinhas vl ON vp.vendaid = vl.vendaid
                    LEFT JOIN bilhetes b ON vl.bilheteid = b.bilheteid
                    LEFT JOIN sessoes s ON b.sessaoid = s.sessaoid
                    LEFT JOIN salas sa ON s.salaid = sa.salaid
                    GROUP BY c.cinemaid
                ),
                filmes_populares AS (
                    SELECT DISTINCT ON (c.cinemaid)
                        c.cinemaid,
                        fil.titulo
                    FROM cinemas c
                    JOIN vendas_periodo vp ON c.cinemaid = vp.cinemaid
                    JOIN vendalinhas vl ON vp.vendaid = vl.vendaid
                    JOIN bilhetes b ON vl.bilheteid = b.bilheteid
                    JOIN sessoes s ON b.sessaoid = s.sessaoid
                    JOIN filmes fil ON s.filmeid = fil.filmeid
                    GROUP BY c.cinemaid, fil.filmeid, fil.titulo
                    ORDER BY c.cinemaid, COUNT(b.bilheteid) DESC
                )
                SELECT 
                    st.nomecinema,
                    st.sessoes,
                    st.bilhetes,
                    st.receita,
                    COALESCE(fp.titulo, 'N/A'::VARCHAR(120)),
                    COALESCE(os.ocupacao_media, 0::NUMERIC)
                FROM stats st
                LEFT JOIN filmes_populares fp ON st.cinemaid = fp.cinemaid
                LEFT JOIN ocupacao_stats os ON st.cinemaid = os.cinemaid
                WHERE st.sessoes > 0 OR st.bilhetes > 0 OR st.receita > 0;
            END;
            $$;
            """,
            "-- Rollback não necessário, apenas correção"
        ),
    ]