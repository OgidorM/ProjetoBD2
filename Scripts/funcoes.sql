/*===============================================================================================
   FUNÇÕES ATUALIZADAS PARA O NOVO MODELO COM lugarsessao (estado por sessão)
================================================================================================*/

------------------------------------------------------------------------------------------------
-- 1. CALCULA TOTAL DE UMA VENDA
------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_calcular_total_venda(p_vendaid INT)
RETURNS NUMERIC AS $$
DECLARE
    v_total NUMERIC := 0;
BEGIN
    SELECT COALESCE(SUM(total_linha_), 0)
    INTO v_total
    FROM vendalinhas
    WHERE vendaid = p_vendaid;

    RETURN v_total;
END;
$$ LANGUAGE plpgsql;

------------------------------------------------------------------------------------------------
-- 2. VERIFICAR SE UM LUGAR DE SESSÃO ESTÁ LIVRE
------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_verificar_disponibilidade_lugar(
    p_sessaoid INT,
    p_lugarsessao INT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_estado VARCHAR(20);
BEGIN
    SELECT estado INTO v_estado
    FROM lugaresSessao
    WHERE sessaoid = p_sessaoid
      AND lugarsessaoid = p_lugarsessao;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'LugarSessao % não existe na sessão %', p_lugarsessao, p_sessaoid;
    END IF;

    RETURN v_estado = 'Livre';
END;
$$ LANGUAGE plpgsql;

------------------------------------------------------------------------------------------------
-- 3. MÉDIA DE AVALIAÇÃO DE UM FILME
------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_calcular_media_avaliacao_filme(p_filmeid INT)
RETURNS NUMERIC AS $$
DECLARE
    v_media NUMERIC;
BEGIN
    SELECT ROUND(AVG(a.avaliacaofilme)::NUMERIC, 2)
    INTO v_media
    FROM avaliacoes a
    JOIN vendas v ON a.vendaid = v.vendaid
    JOIN vendalinhas vl ON vl.vendaid = v.vendaid
    JOIN bilhetes b ON b.bilheteid = vl.bilheteid
    JOIN sessoes s ON s.sessaoid = b.sessaoid
    WHERE s.filmeid = p_filmeid;

    RETURN COALESCE(v_media, 0);
END;
$$ LANGUAGE plpgsql;

------------------------------------------------------------------------------------------------
-- 4. MÉDIA DE AVALIAÇÃO DE UM FUNCIONÁRIO
------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_calcular_media_avaliacao_funcionario(p_funcionarioid INT)
RETURNS NUMERIC AS $$
DECLARE
    v_media NUMERIC;
BEGIN
    SELECT ROUND(AVG(a.avaliacaofuncionario)::NUMERIC, 2)
    INTO v_media
    FROM avaliacoes a
    JOIN vendas v ON v.vendaid = a.vendaid
    WHERE v.funcionarioid = p_funcionarioid;

    RETURN COALESCE(v_media, 0);
END;
$$ LANGUAGE plpgsql;

------------------------------------------------------------------------------------------------
-- 5. MÉDIA DE AVALIAÇÃO DE UM CINEMA
------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_calcular_media_avaliacao_cinema(p_cinemaid INT)
RETURNS NUMERIC AS $$
DECLARE
    v_media NUMERIC;
BEGIN
    SELECT ROUND(AVG(a.avaliacaocinema)::NUMERIC, 2)
    INTO v_media
    FROM avaliacoes a
    JOIN vendas v ON a.vendaid = v.vendaid
    JOIN funcionarios f ON f.funcionarioid = v.funcionarioid
    WHERE f.cinemaid = p_cinemaid;

    RETURN COALESCE(v_media, 0);
END;
$$ LANGUAGE plpgsql;

------------------------------------------------------------------------------------------------
-- 6. PERCENTAGEM DE OCUPAÇÃO DE UMA SESSÃO
------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_verificar_capacidade_sessao(p_sessaoid INT)
RETURNS NUMERIC AS $$
DECLARE
    v_total INT;
    v_ocupados INT;
BEGIN
    SELECT COUNT(*) INTO v_total
    FROM lugaresSessao
    WHERE sessaoid = p_sessaoid;

    SELECT COUNT(*) INTO v_ocupados
    FROM lugaresSessao
    WHERE sessaoid = p_sessaoid
      AND estado = 'Ocupado';

    IF v_total = 0 THEN
        RETURN 0;
    END IF;

    RETURN ROUND((v_ocupados::NUMERIC / v_total::NUMERIC) * 100, 2);
END;
$$ LANGUAGE plpgsql;

------------------------------------------------------------------------------------------------
-- 7. OBTER LISTA DE SESSÕES ATIVAS PARA UM FILME
------------------------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_obter_sessoes_ativas_por_filme(INT);
CREATE OR REPLACE FUNCTION fn_obter_sessoes_ativas_por_filme(p_filmeid INT)
RETURNS TABLE(
    sessaoid INT,
    inicio TIMESTAMPTZ,
    fim TIMESTAMPTZ,
    nomesala VARCHAR,
    nomecinema VARCHAR,
    precosessao NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.sessaoid,
        s.inicio,
        s.fim,
        sa.nomesala,
        c.nomecinema,
        s.precosessao
    FROM sessoes s
    JOIN salas sa ON sa.salaid = s.salaid
    JOIN cinemas c ON c.cinemaid = sa.cinemaid
    WHERE s.filmeid = p_filmeid
      AND s.estadosessao = 'Ativa'
      AND s.fim > NOW()
    ORDER BY s.inicio;
END;
$$ LANGUAGE plpgsql;

------------------------------------------------------------------------------------------------
-- 8. VERIFICAR SE CLIENTE CUMPRE IDADE MÍNIMA DE UM FILME
------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_verificar_idade_minima_filme(
    p_clienteid INT,
    p_filmeid INT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_data_nasc DATE;
    v_classificacao TEXT;
    v_idade_min INT := 0;
    v_idade_cliente INT;
BEGIN
    -- Obter data de nascimento do cliente
    SELECT datanascimento INTO v_data_nasc
    FROM clientes
    WHERE clienteid = p_clienteid;

    IF v_data_nasc IS NULL THEN
        RAISE EXCEPTION 'Cliente % não tem data de nascimento definida.', p_clienteid;
    END IF;

    -- Obter classificação do filme
    SELECT ce.nomeclassificacao INTO v_classificacao
    FROM filmes f
    JOIN classificacoesetarias ce ON ce.classificacaoid = f.classificacaoetaria
    WHERE f.filmeid = p_filmeid;

    IF v_classificacao IS NULL THEN
        RAISE EXCEPTION 'Filme % não encontrado ou sem classificação.', p_filmeid;
    END IF;

    -- Determinar idade mínima a partir da classificação
    CASE v_classificacao
        WHEN 'Livre' THEN v_idade_min := 0;
        WHEN 'M/6'  THEN v_idade_min := 6;
        WHEN 'M/12' THEN v_idade_min := 12;
        WHEN 'M/16' THEN v_idade_min := 16;
        WHEN 'M/18' THEN v_idade_min := 18;
        ELSE v_idade_min := 0;
    END CASE;

    -- Calcular idade do cliente (anos completos)
    SELECT EXTRACT(YEAR FROM AGE(CURRENT_DATE, v_data_nasc))::INT
    INTO v_idade_cliente;

    RETURN v_idade_cliente >= v_idade_min;
END;
$$ LANGUAGE plpgsql;

------------------------------------------------------------------------------------------------
-- 9. HISTORICO DE VENDAS
------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_obter_historico_vendas_cliente(p_clienteid INT)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado JSON;
BEGIN
    SELECT 
        json_agg(
            json_build_object(
                'id', v.vendaid,
                'data', v.data,
                -- Usa o total da tabela, se for nulo chama a função
                'total', COALESCE(v.totalvenda, fn_calcular_total_venda(v.vendaid)),
                'rated', (v.avaliacao IS NOT NULL),
                'items', (
                    SELECT COALESCE(json_agg(
                        CASE 
                            -- CASO SEJA BILHETE
                            WHEN l.bilheteid IS NOT NULL THEN json_build_object(
                                'id', b.bilheteid,
                                'tipo', 'ticket',
                                'filme', f.titulo,
                                'sala', COALESCE(s.nomesala, 'Sala N/A'),
                                'data', sess.inicio,
                                'lugar', CONCAT(lug.fila, lug.numero),
                                'preco', l.precolinha
                            )
                            -- CASO SEJA PRODUTO
                            ELSE json_build_object(
                                'tipo', 'produto',
                                'nome', prod.nomeproduto,
                                'quantidade', l.quantidade,
                                'preco', l.precolinha
                            )
                        END
                    ), '[]'::json)
                    FROM linhavendas l
                    -- Joins para Bilhetes
                    LEFT JOIN bilhetes b ON l.bilheteid = b.bilheteid
                    LEFT JOIN sessoes sess ON b.sessaoid = sess.sessaoid
                    LEFT JOIN filmes f ON sess.filmeid = f.filmeid
                    LEFT JOIN salas s ON sess.salaid = s.salaid
                    LEFT JOIN lugares lug ON b.lugarid = lug.lugarid
                    -- Joins para Produtos
                    LEFT JOIN produtos prod ON l.produtoid = prod.produtoid
                    WHERE l.vendaid = v.vendaid
                )
            ) ORDER BY v.data DESC, v.vendaid DESC
        )
    INTO v_resultado
    FROM 
        vendas v
    WHERE 
        v.clienteid = p_clienteid;

    -- Se não encontrar vendas, v_resultado será NULL.
    -- Retornamos '[]' (array vazio) nesse caso.
    RETURN COALESCE(v_resultado, '[]'::json);
END;
$$;

------------------------------------------------------------------------------------------------
-- 10. LISTAR TODAS AS VENDAS
------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_listar_todas_vendas()
RETURNS JSON
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_resultado JSON;
BEGIN
    SELECT 
        json_agg(
            json_build_object(
                'id', v.vendaid,
                'cliente', COALESCE(c.nomecliente, 'Desconhecido'),
                'data', v.data,
                'total', COALESCE(v.totalvenda, 0),
                'items', (
                    SELECT COALESCE(json_agg(
                        CASE 
                            -- CASO SEJA BILHETE
                            WHEN vl.bilheteid IS NOT NULL THEN json_build_object(
                                'tipo', 'ticket',
                                'filme', f.titulo,
                                'sala', COALESCE(s.nomesala, 'Sala N/A'),
                                'data', sess.inicio,
                                'lugar', CONCAT(lug.fila, lug.numero),
                                'quantidade', vl.quantidade,
                                'preco', vl.precolinha
                            )
                            -- CASO SEJA PRODUTO
                            ELSE json_build_object(
                                'tipo', 'produto',
                                'nome', prod.nomeproduto,
                                'quantidade', vl.quantidade,
                                'preco', vl.precolinha
                            )
                        END
                    ), '[]'::json)
                    FROM vendalinhas vl
                    LEFT JOIN bilhetes b ON vl.bilheteid = b.bilheteid
                    LEFT JOIN sessoes sess ON b.sessaoid = sess.sessaoid
                    LEFT JOIN filmes f ON sess.filmeid = f.filmeid
                    LEFT JOIN salas s ON sess.salaid = s.salaid
                    LEFT JOIN lugares lug ON b.lugarid = lug.lugarid
                    LEFT JOIN produtos prod ON vl.produtoid = prod.produtoid
                    WHERE vl.vendaid = v.vendaid
                )
            ) ORDER BY v.data DESC, v.vendaid DESC
        )
    INTO v_resultado
    FROM vendas v
    LEFT JOIN clientes c ON v.clienteid = c.clienteid;

    RETURN COALESCE(v_resultado, '[]'::json);
END;
$$;



