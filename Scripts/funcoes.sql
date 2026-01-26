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
                'id', v.VENDAID,
                'data', v.DATA,
                'total', COALESCE(v.TOTALVENDA, 0),
                
                -- CORREÇÃO 1: Verifica se existe registo na tabela AVALIACOES
                'rated', (a.AVALIACAOID IS NOT NULL),
                
                'items', (
                    SELECT COALESCE(json_agg(
                        CASE 
                            -- SE FOR BILHETE
                            WHEN l.BILHETEID IS NOT NULL THEN json_build_object(
                                'id', b.BILHETEID,
                                'tipo', 'ticket',
                                'filme', f.TITULO,
                                'sala', COALESCE(s.NOMESALA, 'Sala N/A'),
                                'data', sess.INICIO,
                                -- CORREÇÃO 2: Caminho correto para chegar à Fila/Número
                                -- Bilhete -> LugaresSessao -> Lugares
                                'lugar', CONCAT(lug.FILA, lug.NUMERO), 
                                'preco', l.PRECOLINHA
                            )
                            -- SE FOR PRODUTO
                            ELSE json_build_object(
                                'tipo', 'produto',
                                'nome', prod.NOMEPRODUTO,
                                'quantidade', l.QUANTIDADE,
                                'preco', l.PRECOLINHA
                            )
                        END
                    ), '[]'::json)
                    -- CORREÇÃO 3: Nome da tabela ajustado para VENDALINHAS
                    FROM VENDALINHAS l
                    
                    -- JOINS PARA BILHETES
                    LEFT JOIN BILHETES b ON l.BILHETEID = b.BILHETEID
                    LEFT JOIN SESSOES sess ON b.SESSAOID = sess.SESSAOID
                    LEFT JOIN FILMES f ON sess.FILMEID = f.FILMEID
                    LEFT JOIN SALAS s ON sess.SALAID = s.SALAID
                    
                    -- CORREÇÃO 4: Join Crítico para a nova tabela intermédia
                    LEFT JOIN LUGARESSESSAO ls ON b.LUGARID = ls.LUGARSESSAOID
                    LEFT JOIN LUGARES lug ON ls.LUGARID = lug.LUGARID
                    
                    -- JOIN PARA PRODUTOS
                    LEFT JOIN PRODUTOS prod ON l.PRODUTOID = prod.PRODUTOID
                    
                    WHERE l.VENDAID = v.VENDAID
                )
            ) ORDER BY v.DATA DESC, v.VENDAID DESC
        )
    INTO v_resultado
    FROM 
        VENDAS v
    -- CORREÇÃO 5: Left Join com a tabela separada de avaliações
    LEFT JOIN AVALIACOES a ON v.VENDAID = a.VENDAID
    WHERE 
        v.CLIENTEID = p_clienteid;

    -- Se não houver resultados, devolve array vazio
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

------------------------------------------------------------------------------------------------
-- 11. LISTAR SESSOES AGREGADAS
------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_listar_sessoes_agrupadas()
RETURNS JSON
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_resultado JSON;
BEGIN
    SELECT json_build_object(
        -- Grupo 1: Sessões Ativas (Que ainda não acabaram)
        'ativas', COALESCE(
            json_agg(dados ORDER BY (dados->>'inicio')::TIMESTAMP ASC) 
            FILTER (WHERE (dados->>'terminada')::boolean = false), 
            '[]'::json
        ),
        -- Grupo 2: Sessões Terminadas (Histórico)
        'terminadas', COALESCE(
            json_agg(dados ORDER BY (dados->>'fim')::TIMESTAMP DESC) 
            FILTER (WHERE (dados->>'terminada')::boolean = true), 
            '[]'::json
        )
    )
    INTO v_resultado
    FROM (
        SELECT json_build_object(
            'id', s.sessaoid,
            'filme', f.titulo,
            'cartaz', f.cartaz_url,
            'sala', sa.nomesala,
            'cinema', c.nomecinema,
            'inicio', s.inicio,
            'fim', s.fim,
            'preco', s.precosessao,
            'versao', s.versao,
            -- Cálculo direto da ocupação (Número de ocupados / Total * 100)
            'ocupacao', (
                SELECT CASE WHEN COUNT(*) = 0 THEN 0
                       ELSE ROUND((COUNT(*) FILTER (WHERE ls.estado = 'Ocupado')::NUMERIC / COUNT(*)::NUMERIC) * 100, 0)
                       END
                FROM lugaresSessao ls
                WHERE ls.sessaoid = s.sessaoid
            ),
            -- Flag auxiliar para separar os grupos
            'terminada', (s.fim < CURRENT_TIMESTAMP)
        ) AS dados
        FROM sessoes s
        JOIN filmes f ON s.filmeid = f.filmeid
        JOIN salas sa ON s.salaid = sa.salaid
        JOIN cinemas c ON sa.cinemaid = c.cinemaid
    ) sub;

    RETURN v_resultado;
END;
$$;

------------------------------------------------------------------------------------------------
-- 12. ATUALIZAR PERFIL UTILIZADOR
------------------------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_atualizar_perfil_user(INT, VARCHAR, VARCHAR, VARCHAR, VARCHAR);
CREATE OR REPLACE FUNCTION fn_atualizar_perfil_user(
    p_user_id INT,
    p_new_email VARCHAR,
    p_new_nif VARCHAR,
    p_new_phone VARCHAR,
    p_new_codigo_postal VARCHAR
)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_current_username VARCHAR;
    v_cliente_id INT;
BEGIN
    -- Obter username atual (apenas para resposta)
    SELECT username INTO v_current_username FROM auth_user WHERE id = p_user_id;

    -- A. Atualizar Email na tabela de Autenticação (auth_user)
    UPDATE auth_user
    SET email = p_new_email
    WHERE id = p_user_id;

    -- B. Obter o ID do cliente na tabela de perfil
    BEGIN
        SELECT cliente_dados_id INTO v_cliente_id
        FROM clienteprofile 
        WHERE user_id = p_user_id;
    EXCEPTION WHEN UNDEFINED_TABLE THEN
        v_cliente_id := NULL; 
    END;

    -- C. Atualizar Email, NIF e Telefone na tabela CLIENTES
    IF v_cliente_id IS NOT NULL THEN
        UPDATE clientes
        SET emailcliente = p_new_email,
            nif = p_new_nif,
            telefonecliente = p_new_phone,
            codigopostalcliente = p_new_codigo_postal
        WHERE clienteid = v_cliente_id;
    ELSE
        -- Fallback: Atualizar pelo nome antigo
        UPDATE clientes
        SET emailcliente = p_new_email,
            nif = p_new_nif,
            telefonecliente = p_new_phone,
            codigopostalcliente = p_new_codigo_postal
        WHERE nomecliente = v_current_username;
    END IF;

    -- Retornar os dados atualizados
    RETURN json_build_object(
        'status', 'success',
        'message', 'Profile updated successfully.',
        'username', v_current_username,
        'email', p_new_email,
        'nif', p_new_nif,
        'telefone', p_new_phone,
        'codigo_postal', p_new_codigo_postal
    );

EXCEPTION WHEN OTHERS THEN
    RETURN json_build_object('status', 'error', 'message', SQLERRM);
END;
$$;

------------------------------------------------------------------------------------------------
-- 13. LISTAR PRODUTOS DISPONIVEIS (API)
------------------------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_obter_produtos_api();
CREATE OR REPLACE FUNCTION fn_obter_produtos_api()
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado JSON;
BEGIN
    SELECT 
        -- 1. Agrega todas as linhas num único Array JSON [...]
        json_agg(
            -- 2. Constrói o objeto JSON para cada linha { ... }
            json_build_object(
                'produtoid', p.produtoid,
                'nomeproduto', p.nomeproduto,
                'precoproduto', p.precoproduto,
                'stock', p.stock,
                'ativo', p.ativo
            ) 
            ORDER BY p.nomeproduto ASC
        )
    INTO v_resultado
    FROM produtos p
    WHERE 
        p.ativo = true 
        AND p.stock > 0;

    -- 3. Se não houver produtos, retorna array vazio '[]' em vez de NULL
    RETURN COALESCE(v_resultado, '[]'::json);
END;
$$;

------------------------------------------------------------------------------------------------
-- 14. REALIZAR VENDA UNIFICADA (API)
------------------------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_realizar_venda_unificada;
CREATE OR REPLACE FUNCTION fn_realizar_venda_unificada(
    p_user_id INT,
    p_username VARCHAR,
    p_email VARCHAR,
    
    -- Parametros da Venda
    p_sessaoid INT,          
    p_lugares_ids JSONB,     
    p_produtos JSONB         
)
RETURNS INT 
LANGUAGE plpgsql
AS $$
DECLARE
    v_cliente_id INT;
    v_vendaid INT;
    
    -- Variáveis auxiliares
    v_item JSONB;
    v_preco NUMERIC;
    
    -- Variáveis para Bilhetes
    v_lugar_sessao_id INT;
    v_lugar_fisico_id INT;
    v_bilhete_id INT;
    v_estado_lugar VARCHAR;
    
    -- Variáveis para Produtos
    v_prod_id INT;
    v_qtd INT;
    v_stock_atual INT;
    v_preco_prod NUMERIC;
BEGIN
    -- 1. LÓGICA DE CLIENTE    
    BEGIN
        SELECT cliente_dados_id INTO v_cliente_id
        FROM clienteprofile WHERE user_id = p_user_id;
    EXCEPTION WHEN UNDEFINED_TABLE THEN
        v_cliente_id := NULL;
    END;

    IF v_cliente_id IS NULL THEN
        SELECT clienteid INTO v_cliente_id FROM clientes WHERE nomecliente = p_username;
    END IF;

    -- C. Se ainda não existe, CRIA O CLIENTE agora mesmo
    IF v_cliente_id IS NULL THEN
        INSERT INTO clientes (nomecliente, emailcliente, datanascimento)
        VALUES (p_username, p_email, '2000-01-01') -- Data dummy obrigatória
        RETURNING clienteid INTO v_cliente_id;
    END IF;

    -- 2. CRIAR A VENDA (O Cabeçalho)
    INSERT INTO vendas (clienteid, data, estadovenda, totalvenda)
    VALUES (v_cliente_id, CURRENT_DATE, 'Concluída', 0)
    RETURNING vendaid INTO v_vendaid;

    -- 3. PROCESSAR BILHETES (Se houver sessão e lugares)
    IF p_sessaoid IS NOT NULL AND p_lugares_ids IS NOT NULL AND jsonb_array_length(p_lugares_ids) > 0 THEN
        
        -- Obter preço da sessão
        SELECT precosessao INTO v_preco FROM sessoes WHERE sessaoid = p_sessaoid;
        
        IF v_preco IS NULL THEN
            RAISE EXCEPTION 'Sessão % não encontrada.', p_sessaoid;
        END IF;

        -- Loop pelos IDs dos lugares (lugarsessaoid)
        FOR v_item IN SELECT * FROM jsonb_array_elements(p_lugares_ids)
        LOOP
            v_lugar_sessao_id := (v_item::text)::INT;

            -- Verificar se está livre e obter o ID físico do lugar
            SELECT estado, lugarid INTO v_estado_lugar, v_lugar_fisico_id
            FROM lugaressessao 
            WHERE lugarsessaoid = v_lugar_sessao_id;

            IF v_estado_lugar = 'Ocupado' THEN
                RAISE EXCEPTION 'O lugar % já foi ocupado por outra pessoa.', v_lugar_sessao_id;
            END IF;

            -- Marcar como Ocupado
            UPDATE lugaressessao SET estado = 'Ocupado' WHERE lugarsessaoid = v_lugar_sessao_id;

            -- Gerar Bilhete
            INSERT INTO bilhetes (lugarid, sessaoid, precobilhete, emissao)
            VALUES (v_lugar_fisico_id, p_sessaoid, v_preco, NOW())
            RETURNING bilheteid INTO v_bilhete_id;

            -- Adicionar à Venda
            INSERT INTO vendalinhas (vendaid, bilheteid, quantidade, precolinha, total_linha_)
            VALUES (v_vendaid, v_bilhete_id, 1, v_preco, v_preco);
        END LOOP;
    END IF;

    -- 4. PROCESSAR PRODUTOS/SNACKS (Se houver items)
    IF p_produtos IS NOT NULL AND jsonb_array_length(p_produtos) > 0 THEN
        
        FOR v_item IN SELECT * FROM jsonb_array_elements(p_produtos)
        LOOP
            v_prod_id := (v_item->>'id')::INT;
            v_qtd := (v_item->>'qtd')::INT;

            -- Verificar Stock e Preço
            SELECT precoproduto, stock INTO v_preco_prod, v_stock_atual
            FROM produtos WHERE produtoid = v_prod_id;

            IF v_stock_atual < v_qtd THEN
                RAISE EXCEPTION 'Stock insuficiente para o produto % (Disponível: %)', v_prod_id, v_stock_atual;
            END IF;

            UPDATE produtos SET stock = stock - v_qtd WHERE produtoid = v_prod_id;

            -- Adicionar à Venda
            INSERT INTO vendalinhas (vendaid, produtoid, quantidade, precolinha, total_linha_)
            VALUES (v_vendaid, v_prod_id, v_qtd, v_preco_prod, (v_preco_prod * v_qtd));
        END LOOP;
    END IF;
    RETURN v_vendaid;
END;
$$;

------------------------------------------------------------------------------------------------
-- 15. LISTAR FILMES POR CINEMA (API)
------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_listar_filmes_api(
    p_cinema_id INT DEFAULT NULL
)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado JSON;
BEGIN
    SELECT 
        json_agg(
            json_build_object(
                'filmeid', f.filmeid,
                'titulo', f.titulo,
                'duracao', f.duracao,
                'sinopse', f.sinopse,
                'idioma', f.idioma,
                'cartaz', f.cartaz_url,
                'ranking', f.ranking,
                'datalancamento', f.datalancamento,
                'fimexebicao', f.fimexebicao,
                -- Dados das tabelas relacionadas (antigo select_related)
                'categoria', c.nomecategoria,
                'classificacao', ce.nomeclassificacao,
                'cinema', cin.nomecinema,
                'cinema_id', f.cinemaid
            ) ORDER BY f.titulo ASC
        )
    INTO v_resultado
    FROM filmes f
    LEFT JOIN categorias c ON f.categoriaid = c.categoriaid
    LEFT JOIN classificacoesetarias ce ON f.classificacaoetaria = ce.classificacaoid
    LEFT JOIN cinemas cin ON f.cinemaid = cin.cinemaid
    WHERE 
        -- Se p_cinema_id for NULL, traz todos. Se for preenchido, filtra.
        (p_cinema_id IS NULL OR f.cinemaid = p_cinema_id);

    RETURN COALESCE(v_resultado, '[]'::json);
END;
$$;

------------------------------------------------------------------------------------------------
-- 16. LISTAR SALAS (API)
------------------------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_listar_salas_api();
CREATE OR REPLACE FUNCTION fn_listar_salas_api()
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado JSON;
BEGIN
    SELECT 
        json_agg(
            json_build_object(
                'salaid', s.salaid,
                'nomesala', s.nomesala,
                'filas', s.filas,
                'colunas', s.colunas,
                'tiposala', s.tiposala,
                -- Calculamos a capacidade total diretamente no SQL
                'capacidade', (s.filas * s.colunas),
                -- Trazemos o nome do cinema (substitui o serializer relation)
                'cinema', c.nomecinema,
                'cinemaid', s.cinemaid
            ) ORDER BY c.nomecinema, s.nomesala
        )
    INTO v_resultado
    FROM salas s
    LEFT JOIN cinemas c ON s.cinemaid = c.cinemaid;

    -- Retorna lista vazia se não houver salas
    RETURN COALESCE(v_resultado, '[]'::json);
END;
$$;

------------------------------------------------------------------------------------------------
-- 17. LISTAR SESSÕES POR FILME (API)
------------------------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_listar_sessoes_por_filme(int);
CREATE OR REPLACE FUNCTION fn_listar_sessoes_por_filme(p_filmeid INT)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado JSON;
BEGIN
    SELECT 
        json_agg(
            json_build_object(
                -- Dados da Sessão (Campos do Model Sessoes)
                'sessaoid', s.sessaoid,
                'inicio', s.inicio,
                'fim', s.fim,
                'precosessao', s.precosessao,
                'versao', s.versao,
                'estadosessao', s.estadosessao,
                
                -- Dados Relacionados (Equivalente ao select_related 'salaid')
                'salaid', s.salaid,
                'nomesala', sa.nomesala,
                
                -- Dados Relacionados (Equivalente ao select_related 'salaid__cinemaid')
                'cinemaid', sa.cinemaid,
                'nomecinema', c.nomecinema
            ) ORDER BY s.inicio ASC -- Equivalente ao .order_by('inicio')
        )
    INTO v_resultado
    FROM sessoes s
    JOIN salas sa ON s.salaid = sa.salaid
    JOIN cinemas c ON sa.cinemaid = c.cinemaid
    WHERE 
        s.filmeid = p_filmeid
        AND s.estadosessao = 'Ativa'; -- Equivalente ao .filter(..., estadosessao='Ativa')

    -- Retorna lista vazia se não houver resultados
    RETURN COALESCE(v_resultado, '[]'::json);
END;
$$;

------------------------------------------------------------------------------------------------
-- 18. LISTAR LUGARES POR SESSÃO (API)
------------------------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_listar_lugares_sessao(int);
CREATE OR REPLACE FUNCTION fn_listar_lugares_sessao(p_sessaoid INT)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_exists BOOLEAN;
    v_resultado JSON;
BEGIN
    -- 1. VERIFICAÇÃO DE SEGURANÇA
    -- Verifica se a sessão existe mesmo
    PERFORM 1 FROM sessoes WHERE sessaoid = p_sessaoid;
    IF NOT FOUND THEN
        RETURN json_build_object('error', 'Sessão não encontrada');
    END IF;

    SELECT EXISTS (SELECT 1 FROM lugaressessao WHERE sessaoid = p_sessaoid) INTO v_exists;

    IF NOT v_exists THEN
        INSERT INTO lugaressessao (lugarid, sessaoid, estado)
        SELECT 
            l.lugarid, 
            p_sessaoid, 
            'Livre' -- Estado inicial
        FROM lugares l
        JOIN sessoes s ON s.salaid = l.salaid
        WHERE s.sessaoid = p_sessaoid;
    END IF;

    -- 3. LISTAGEM E SERIALIZAÇÃO
    SELECT json_agg(
        json_build_object(
            'lugarsessaoid', ls.lugarsessaoid,
            'estado', ls.estado,
            'sessaoid', ls.sessaoid,
            'lugar', json_build_object(
                'lugarid', l.lugarid,
                'fila', l.fila,
                'numero', l.numero,
                'tipolugar', l.tipolugar
            )
        ) ORDER BY l.fila ASC, l.numero ASC
    )
    INTO v_resultado
    FROM lugaressessao ls
    JOIN lugares l ON ls.lugarid = l.lugarid
    WHERE ls.sessaoid = p_sessaoid;

    RETURN COALESCE(v_resultado, '[]'::json);
END;
$$;

------------------------------------------------------------------------------------------------
-- 19. RESOLVER ID DO CLIENTE
------------------------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_resolver_cliente_id(varchar);
CREATE OR REPLACE FUNCTION fn_resolver_cliente_id(p_username VARCHAR)
RETURNS INT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_cliente_id INT;
BEGIN
    -- Procura diretamente na tabela Clientes pelo nome (Case Insensitive com ILIKE é mais seguro)
    SELECT clienteid INTO v_cliente_id
    FROM clientes
    WHERE nomecliente = p_username 
    LIMIT 1;

    -- Se achar retorna o ID, se não achar retorna NULL
    RETURN v_cliente_id;
END;
$$;

------------------------------------------------------------------------------------------------
-- 20. LISTAR CATEGORIAS (API)
------------------------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_listar_categorias();
CREATE OR REPLACE FUNCTION fn_listar_categorias()
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado JSON;
BEGIN
    SELECT 
        json_agg(
            json_build_object(
                'id', categoriaid,
                'name', nomecategoria
            ) ORDER BY categoriaid ASC -- Mantive a ordenação do seu código original
        )
    INTO v_resultado
    FROM categorias;

    -- Se a tabela estiver vazia, retorna array vazio []
    RETURN COALESCE(v_resultado, '[]'::json);
END;
$$;

------------------------------------------------------------------------------------------------
-- 21. LISTAR BILHETES POR SESSÃO (API)
------------------------------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_listar_bilhetes_sessao_admin(int);
CREATE OR REPLACE FUNCTION fn_listar_bilhetes_sessao_admin(p_sessaoid INT)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado JSON;
BEGIN
    SELECT 
        json_agg(
            json_build_object(
                'bilheteid', b.bilheteid,
                'lugar', (l.fila || l.numero),
                'cliente', COALESCE(c.nomecliente, 'N/A'),
                'venda_id', v.vendaid,
                'preco', b.precobilhete
            ) ORDER BY l.fila, l.numero
        )
    INTO v_resultado
    FROM bilhetes b
    JOIN lugares l ON b.lugarid = l.lugarid
    LEFT JOIN vendalinhas vl ON b.bilheteid = vl.bilheteid
    LEFT JOIN vendas v ON vl.vendaid = v.vendaid
    LEFT JOIN clientes c ON v.clienteid = c.clienteid
    WHERE b.sessaoid = p_sessaoid;

    RETURN COALESCE(v_resultado, '[]'::json);
END;
$$;