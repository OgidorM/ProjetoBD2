# migrations/0002_add_views_procedures_functions_triggers.py
from django.db import migrations


class Migration(migrations.Migration):
    
    dependencies = [
        ('bd2ap1', '0001_initial'),
    ]

    operations = [
        # ===================================================================
        # 1. VIEWS PARA RELATÓRIOS E CONSULTAS
        # ===================================================================
        
        migrations.RunSQL(
            """
            -- View para informações completas de sessões
            CREATE OR REPLACE VIEW v_sessoes_completas AS
            SELECT 
                s.sessaoid,
                c.nomecinema,
                sa.nomesala,
                f.titulo AS filme,
                cat.nomecategoria AS categoria,
                s.inicio,
                s.fim,
                s.versao,
                s.estadosessao,
                s.precosessao,
                sa.capacidade,
                COUNT(b.bilheteid) AS bilhetes_vendidos,
                (sa.capacidade - COUNT(b.bilheteid)) AS lugares_disponiveis,
                ROUND((COUNT(b.bilheteid)::NUMERIC / sa.capacidade * 100), 2) AS taxa_ocupacao
            FROM sessoes s
            JOIN salas sa ON s.salaid = sa.salaid
            JOIN cinemas c ON sa.cinemaid = c.cinemaid
            JOIN filmes f ON s.filmeid = f.filmeid
            JOIN categorias cat ON f.categoriaid = cat.categoriaid
            LEFT JOIN lugares l ON l.salaid = sa.salaid
            LEFT JOIN bilhetes b ON b.sessaoid = s.sessaoid
            GROUP BY s.sessaoid, c.nomecinema, sa.nomesala, f.titulo, cat.nomecategoria, 
                     s.inicio, s.fim, s.versao, s.estadosessao, s.precosessao, sa.capacidade;
            """,
            "DROP VIEW IF EXISTS v_sessoes_completas;"
        ),
        
        migrations.RunSQL(
            """
            -- View para análise de vendas
            CREATE OR REPLACE VIEW v_vendas_detalhadas AS
            SELECT 
                v.vendaid,
                v.data,
                c.nomecliente,
                f.nomefuncionario,
                cin.nomecinema,
                v.estadovenda,
                v.totalvenda,
                COUNT(DISTINCT vl.vendalinhaid) AS total_linhas,
                COUNT(DISTINCT b.bilheteid) AS total_bilhetes,
                SUM(CASE WHEN p.nomeproduto IS NOT NULL THEN vl.quantidade ELSE 0 END) AS produtos_vendidos
            FROM vendas v
            LEFT JOIN clientes c ON v.clienteid = c.clienteid
            LEFT JOIN funcionarios f ON v.funcionarioid = f.funcionarioid
            LEFT JOIN cinemas cin ON f.cinemaid = cin.cinemaid
            LEFT JOIN vendalinhas vl ON v.vendaid = vl.vendaid
            LEFT JOIN produtos p ON vl.produtoid = p.produtoid
            LEFT JOIN bilhetes b ON vl.bilheteid = b.bilheteid
            GROUP BY v.vendaid, v.data, c.nomecliente, f.nomefuncionario, cin.nomecinema, v.estadovenda, v.totalvenda;
            """,
            "DROP VIEW IF EXISTS v_vendas_detalhadas;"
        ),
        
        migrations.RunSQL(
            """
            -- View para ranking de filmes
            CREATE OR REPLACE VIEW v_filmes_popularidade AS
            SELECT 
                f.filmeid,
                f.titulo,
                cat.nomecategoria,
                c.nomecinema,
                f.ranking AS ranking_filme,
                COUNT(DISTINCT s.sessaoid) AS total_sessoes,
                COUNT(b.bilheteid) AS total_bilhetes_vendidos,
                COALESCE(SUM(b.precobilhete), 0) AS receita_total,
                ROUND(AVG(CASE WHEN av.avaliacaofilme IS NOT NULL THEN av.avaliacaofilme END), 2) AS avaliacao_media
            FROM filmes f
            JOIN categorias cat ON f.categoriaid = cat.categoriaid
            JOIN cinemas c ON f.cinemaid = c.cinemaid
            LEFT JOIN sessoes s ON f.filmeid = s.filmeid
            LEFT JOIN bilhetes b ON s.sessaoid = b.sessaoid
            LEFT JOIN vendalinhas vl ON b.bilheteid = vl.bilheteid
            LEFT JOIN vendas v ON vl.vendaid = v.vendaid
            LEFT JOIN avaliacoes av ON v.vendaid = av.vendaid
            GROUP BY f.filmeid, f.titulo, cat.nomecategoria, c.nomecinema, f.ranking
            ORDER BY total_bilhetes_vendidos DESC, receita_total DESC;
            """,
            "DROP VIEW IF EXISTS v_filmes_popularidade;"
        ),
        
        migrations.RunSQL(
            """
            -- View para ocupação de salas
            CREATE OR REPLACE VIEW v_ocupacao_salas AS
            SELECT 
                sa.salaid,
                c.nomecinema,
                sa.nomesala,
                sa.capacidade,
                sa.tiposala,
                COUNT(DISTINCT s.sessaoid) AS total_sessoes,
                COUNT(b.bilheteid) AS total_bilhetes_vendidos,
                ROUND((COUNT(b.bilheteid)::NUMERIC / (sa.capacidade * COUNT(DISTINCT s.sessaoid)) * 100), 2) AS taxa_ocupacao_media
            FROM salas sa
            JOIN cinemas c ON sa.cinemaid = c.cinemaid
            LEFT JOIN sessoes s ON sa.salaid = s.salaid
            LEFT JOIN bilhetes b ON s.sessaoid = b.sessaoid
            GROUP BY sa.salaid, c.nomecinema, sa.nomesala, sa.capacidade, sa.tiposala
            ORDER BY taxa_ocupacao_media DESC;
            """,
            "DROP VIEW IF EXISTS v_ocupacao_salas;"
        ),
        
        # ===================================================================
        # 2. PROCEDURES PARA GESTÃO DE SESSÕES
        # ===================================================================
        
        migrations.RunSQL(
            """
            -- Procedure para criar uma nova sessão
            CREATE OR REPLACE FUNCTION criar_sessao(
                p_salaid INTEGER,
                p_filmeid INTEGER,
                p_inicio TIMESTAMP,
                p_fim TIMESTAMP,
                p_versao VARCHAR(8),
                p_precosessao NUMERIC(5,2)
            ) RETURNS INTEGER
            LANGUAGE plpgsql AS $$
            DECLARE
                v_sessaoid INTEGER;
                v_conflito INTEGER;
            BEGIN
                -- Verificar conflitos de horário na sala
                SELECT COUNT(*) INTO v_conflito
                FROM sessoes
                WHERE salaid = p_salaid
                AND ((p_inicio BETWEEN inicio AND fim) OR (p_fim BETWEEN inicio AND fim)
                     OR (inicio BETWEEN p_inicio AND p_fim));
                
                IF v_conflito > 0 THEN
                    RAISE EXCEPTION 'Conflito de horário na sala para o período especificado';
                END IF;
                
                -- Inserir nova sessão
                INSERT INTO sessoes (salaid, filmeid, inicio, fim, versao, estadosessao, precosessao)
                VALUES (p_salaid, p_filmeid, p_inicio, p_fim, p_versao, 'Programada', p_precosessao)
                RETURNING sessaoid INTO v_sessaoid;
                
                RETURN v_sessaoid;
            END;
            $$;
            """,
            "DROP FUNCTION IF EXISTS criar_sessao(INTEGER, INTEGER, TIMESTAMP, TIMESTAMP, VARCHAR(8), NUMERIC(5,2));"
        ),
        
        migrations.RunSQL(
            """
            -- Procedure para processar venda de bilhetes
            CREATE OR REPLACE FUNCTION processar_venda_bilhetes(
                p_clienteid INTEGER,
                p_funcionarioid INTEGER,
                p_sessaoid INTEGER,
                p_lugares INTEGER[]
            ) RETURNS INTEGER
            LANGUAGE plpgsql AS $$
            DECLARE
                v_vendaid INTEGER;
                v_vendalinhaid INTEGER;
                v_lugar INTEGER;
                v_precosessao NUMERIC(5,2);
                v_total NUMERIC(8,2) := 0;
                v_lugar_ocupado INTEGER;
                v_bilheteid INTEGER;
            BEGIN
                -- Obter preço da sessão
                SELECT precosessao INTO v_precosessao
                FROM sessoes WHERE sessaoid = p_sessaoid;
                
                -- Verificar se os lugares estão disponíveis
                FOREACH v_lugar IN ARRAY p_lugares
                LOOP
                    SELECT COUNT(*) INTO v_lugar_ocupado
                    FROM bilhetes b
                    WHERE b.lugarid = v_lugar AND b.sessaoid = p_sessaoid;
                    
                    IF v_lugar_ocupado > 0 THEN
                        RAISE EXCEPTION 'Lugar % já está ocupado para esta sessão', v_lugar;
                    END IF;
                END LOOP;
                
                -- Criar venda
                INSERT INTO vendas (clienteid, funcionarioid, data, estadovenda)
                VALUES (p_clienteid, p_funcionarioid, CURRENT_DATE, 'Processada')
                RETURNING vendaid INTO v_vendaid;
                
                -- Criar bilhetes individuais e linha de venda para cada um
                FOREACH v_lugar IN ARRAY p_lugares
                LOOP
                    -- Criar bilhete
                    INSERT INTO bilhetes (lugarid, sessaoid, precobilhete, emicao)
                    VALUES (v_lugar, p_sessaoid, v_precosessao, NOW())
                    RETURNING bilheteid INTO v_bilheteid;
                    
                    -- Criar linha de venda para este bilhete
                    INSERT INTO vendalinhas (vendaid, bilheteid, quantidade, precolinha, total_linha_)
                    VALUES (v_vendaid, v_bilheteid, 1, v_precosessao, v_precosessao);
                    
                    v_total := v_total + v_precosessao;
                END LOOP;
                
                -- Atualizar total da venda
                UPDATE vendas SET totalvenda = v_total WHERE vendaid = v_vendaid;
                
                RETURN v_vendaid;
            END;
            $$;
            """,
            "DROP FUNCTION IF EXISTS processar_venda_bilhetes(INTEGER, INTEGER, INTEGER, INTEGER[]);"
        ),
        
        # ===================================================================
        # 3. FUNCTIONS PARA RELATÓRIOS E ESTATÍSTICAS
        # ===================================================================
        
        migrations.RunSQL(
            """
            -- Function para calcular receita por período
            CREATE OR REPLACE FUNCTION calcular_receita_periodo(
                p_data_inicio DATE,
                p_data_fim DATE,
                p_cinemaid INTEGER DEFAULT NULL
            ) RETURNS TABLE(
                cinema VARCHAR(80),
                total_vendas BIGINT,
                receita_bilhetes NUMERIC,
                receita_produtos NUMERIC,
                receita_total NUMERIC
            )
            LANGUAGE plpgsql AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    c.nomecinema,
                    COUNT(DISTINCT v.vendaid)::BIGINT,
                    COALESCE(SUM(CASE WHEN b.bilheteid IS NOT NULL THEN b.precobilhete ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN p.produtoid IS NOT NULL THEN vl.total_linha_ ELSE 0 END), 0),
                    COALESCE(SUM(v.totalvenda), 0)
                FROM vendas v
                JOIN funcionarios f ON v.funcionarioid = f.funcionarioid
                JOIN cinemas c ON f.cinemaid = c.cinemaid
                LEFT JOIN vendalinhas vl ON v.vendaid = vl.vendaid
                LEFT JOIN bilhetes b ON vl.bilheteid = b.bilheteid
                LEFT JOIN produtos p ON vl.produtoid = p.produtoid
                WHERE v.data BETWEEN p_data_inicio AND p_data_fim
                AND (p_cinemaid IS NULL OR c.cinemaid = p_cinemaid)
                GROUP BY c.cinemaid, c.nomecinema
                ORDER BY receita_total DESC;
            END;
            $$;
            """,
            "DROP FUNCTION IF EXISTS calcular_receita_periodo(DATE, DATE, INTEGER);"
        ),
        
        migrations.RunSQL(
            """
            -- Function para obter disponibilidade de lugares
            CREATE OR REPLACE FUNCTION obter_lugares_disponiveis(p_sessaoid INTEGER)
            RETURNS TABLE(
                lugarid INTEGER,
                fila VARCHAR(4),
                numero INTEGER,
                tipolugar VARCHAR(20),
                disponivel BOOLEAN
            )
            LANGUAGE plpgsql AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    l.lugarid,
                    l.fila,
                    l.numero,
                    l.tipolugar,
                    CASE WHEN b.bilheteid IS NULL THEN TRUE ELSE FALSE END
                FROM lugares l
                JOIN salas sa ON l.salaid = sa.salaid
                JOIN sessoes s ON sa.salaid = s.salaid
                LEFT JOIN bilhetes b ON l.lugarid = b.lugarid AND b.sessaoid = s.sessaoid
                WHERE s.sessaoid = p_sessaoid
                ORDER BY l.fila, l.numero;
            END;
            $$;
            """,
            "DROP FUNCTION IF EXISTS obter_lugares_disponiveis(INTEGER);"
        ),
        
        # ===================================================================
        # 4. TRIGGERS PARA VALIDAÇÕES E ATUALIZAÇÕES AUTOMÁTICAS
        # ===================================================================
        
        migrations.RunSQL(
            """
            -- Function para trigger de atualizar ranking de filmes
            CREATE OR REPLACE FUNCTION atualizar_ranking_filme()
            RETURNS TRIGGER AS $$
            DECLARE
                v_filmeid INTEGER;
                v_total_bilhetes INTEGER;
                v_novo_ranking NUMERIC(2,1);
            BEGIN
                -- Obter filme da sessão
                SELECT s.filmeid INTO v_filmeid
                FROM sessoes s
                WHERE s.sessaoid = NEW.sessaoid;
                
                -- Calcular total de bilhetes vendidos para o filme
                SELECT COUNT(*) INTO v_total_bilhetes
                FROM bilhetes b
                JOIN sessoes s ON b.sessaoid = s.sessaoid
                WHERE s.filmeid = v_filmeid;
                
                -- Calcular novo ranking baseado em vendas (exemplo simplificado)
                v_novo_ranking := LEAST(5.0, v_total_bilhetes / 100.0);
                
                -- Atualizar ranking do filme
                UPDATE filmes SET ranking = v_novo_ranking WHERE filmeid = v_filmeid;
                
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """,
            "DROP FUNCTION IF EXISTS atualizar_ranking_filme();"
        ),
        
        migrations.RunSQL(
            """
            -- Trigger para atualizar ranking de filmes baseado em vendas
            CREATE TRIGGER trigger_atualizar_ranking_filme
                AFTER INSERT ON bilhetes
                FOR EACH ROW
                EXECUTE FUNCTION atualizar_ranking_filme();
            """,
            "DROP TRIGGER IF EXISTS trigger_atualizar_ranking_filme ON bilhetes;"
        ),
        
        migrations.RunSQL(
            """
            -- Function para trigger de validar capacidade da sala
            CREATE OR REPLACE FUNCTION validar_capacidade_sala()
            RETURNS TRIGGER AS $$
            DECLARE
                v_capacidade INTEGER;
                v_bilhetes_vendidos INTEGER;
            BEGIN
                -- Obter capacidade da sala
                SELECT sa.capacidade INTO v_capacidade
                FROM salas sa
                JOIN sessoes s ON sa.salaid = s.salaid
                WHERE s.sessaoid = NEW.sessaoid;
                
                -- Contar bilhetes já vendidos para esta sessão
                SELECT COUNT(*) INTO v_bilhetes_vendidos
                FROM bilhetes
                WHERE sessaoid = NEW.sessaoid;
                
                IF v_bilhetes_vendidos >= v_capacidade THEN
                    RAISE EXCEPTION 'Capacidade máxima da sala excedida';
                END IF;
                
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """,
            "DROP FUNCTION IF EXISTS validar_capacidade_sala();"
        ),
        
        migrations.RunSQL(
            """
            -- Trigger para validar capacidade
            CREATE TRIGGER trigger_validar_capacidade
                BEFORE INSERT ON bilhetes
                FOR EACH ROW
                EXECUTE FUNCTION validar_capacidade_sala();
            """,
            "DROP TRIGGER IF EXISTS trigger_validar_capacidade ON bilhetes;"
        ),
        
        # ===================================================================
        # 5. PROCEDURES DE MANUTENÇÃO E ADMINISTRAÇÃO
        # ===================================================================
        
        migrations.RunSQL(
            """
            -- Procedure para limpar sessões antigas
            CREATE OR REPLACE FUNCTION limpar_sessoes_antigas(p_dias INTEGER DEFAULT 90)
            RETURNS INTEGER
            LANGUAGE plpgsql AS $$
            DECLARE
                v_deletadas INTEGER;
            BEGIN
                DELETE FROM sessoes 
                WHERE fim < (CURRENT_DATE - INTERVAL '1 day' * p_dias)
                AND estadosessao = 'Finalizada';
                
                GET DIAGNOSTICS v_deletadas = ROW_COUNT;
                RETURN v_deletadas;
            END;
            $$;
            """,
            "DROP FUNCTION IF EXISTS limpar_sessoes_antigas(INTEGER);"
        ),
        
        migrations.RunSQL(
            """
            -- Procedure para gerar relatório de desempenho mensal
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
                WITH stats AS (
                    SELECT 
                        c.cinemaid,
                        c.nomecinema,
                        COUNT(DISTINCT s.sessaoid) as sessoes,
                        COUNT(b.bilheteid) as bilhetes,
                        COALESCE(SUM(b.precobilhete), 0) as receita,
                        ROUND(AVG(
                            COUNT(b.bilheteid)::NUMERIC / sa.capacidade * 100
                        ), 2) as ocupacao
                    FROM cinemas c
                    LEFT JOIN funcionarios f ON c.cinemaid = f.cinemaid
                    LEFT JOIN vendas v ON f.funcionarioid = v.funcionarioid
                    LEFT JOIN vendalinhas vl ON v.vendaid = vl.vendaid
                    LEFT JOIN bilhetes b ON vl.bilheteid = b.bilheteid
                    LEFT JOIN sessoes s ON b.sessaoid = s.sessaoid
                    LEFT JOIN salas sa ON s.salaid = sa.salaid
                    WHERE EXTRACT(MONTH FROM v.data) = p_mes
                    AND EXTRACT(YEAR FROM v.data) = p_ano
                    AND (p_cinemaid IS NULL OR c.cinemaid = p_cinemaid)
                    GROUP BY c.cinemaid, c.nomecinema, sa.capacidade
                ),
                filmes_populares AS (
                    SELECT DISTINCT ON (c.cinemaid)
                        c.cinemaid,
                        fil.titulo
                    FROM cinemas c
                    JOIN salas sa ON c.cinemaid = sa.cinemaid
                    JOIN sessoes s ON sa.salaid = s.salaid
                    JOIN filmes fil ON s.filmeid = fil.filmeid
                    JOIN bilhetes b ON s.sessaoid = b.sessaoid
                    JOIN vendalinhas vl ON b.bilheteid = vl.bilheteid
                    JOIN vendas v ON vl.vendaid = v.vendaid
                    WHERE EXTRACT(MONTH FROM v.data) = p_mes
                    AND EXTRACT(YEAR FROM v.data) = p_ano
                    GROUP BY c.cinemaid, fil.filmeid, fil.titulo
                    ORDER BY c.cinemaid, COUNT(b.bilheteid) DESC
                )
                SELECT 
                    st.nomecinema,
                    st.sessoes,
                    st.bilhetes,
                    st.receita,
                    fp.titulo,
                    st.ocupacao
                FROM stats st
                LEFT JOIN filmes_populares fp ON st.cinemaid = fp.cinemaid;
            END;
            $$;
            """,
            "DROP FUNCTION IF EXISTS relatorio_mensal(INTEGER, INTEGER, INTEGER);"
        ),
        
        # ===================================================================
        # 6. ÍNDICES PARA OTIMIZAÇÃO DE PERFORMANCE
        # ===================================================================
        
        migrations.RunSQL(
            """
            -- Índices para melhorar performance das consultas
            CREATE INDEX IF NOT EXISTS idx_sessoes_data ON sessoes(inicio);
            CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data);
            CREATE INDEX IF NOT EXISTS idx_bilhetes_sessao ON bilhetes(sessaoid);
            CREATE INDEX IF NOT EXISTS idx_filmes_cinema ON filmes(cinemaid);
            CREATE INDEX IF NOT EXISTS idx_avaliacoes_vendas ON avaliacoes(vendaid);
            """,
            """
            DROP INDEX IF EXISTS idx_sessoes_data;
            DROP INDEX IF EXISTS idx_vendas_data;
            DROP INDEX IF EXISTS idx_bilhetes_sessao;
            DROP INDEX IF EXISTS idx_filmes_cinema;
            DROP INDEX IF EXISTS idx_avaliacoes_vendas;
            """
        ),
    ]