from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('bd2ap1', '0002_filmes_cartaz_url_alter_filmes_cinemaid'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION fn_gerar_detalhes_bilhete(p_bilheteid INT)
            RETURNS TABLE (
                bilhete_id INT,
                titulo_filme VARCHAR,
                nome_cinema VARCHAR,
                nome_sala VARCHAR,
                lugar_fila VARCHAR,
                lugar_numero INT,
                data_hora_inicio TIMESTAMP,
                preco_pago DECIMAL,
                emissao TIMESTAMPTZ
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    b.bilheteid,
                    f.titulo,
                    c.nomecinema,
                    s.nomesala,
                    l.fila,
                    l.numero,
                    sess.inicio,
                    b.precobilhete,
                    b.emissao
                FROM bilhetes b
                JOIN sessoes sess ON b.sessaoid = sess.sessaoid
                JOIN filmes f ON sess.filmeid = f.filmeid
                JOIN salas s ON sess.salaid = s.salaid
                JOIN lugares l ON b.lugarid = l.lugarid
                LEFT JOIN cinemas c ON s.cinemaid = c.cinemaid
                WHERE b.bilheteid = p_bilheteid;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS fn_gerar_detalhes_bilhete(INT);"
        ),
    ]