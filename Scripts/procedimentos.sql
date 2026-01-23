----------------------------------------------------------------------------------------------
-- 1. INSERIR FILME
----------------------------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE inserir_filme(
    p_categoriaid INT,
    p_cinemaid INT,
    p_titulo VARCHAR,
    p_datalanc DATE,
    p_duracao INT,
    p_produtora VARCHAR,
    p_fim DATE,
    p_idioma CHAR(4),
    p_sinopse TEXT,
    p_classificacaoid INT,
    p_ranking NUMERIC(2,1)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_dmin CONSTANT INT := 10;
    v_dmax CONSTANT INT := 300;
BEGIN
    -- Validar categoria
    PERFORM 1 FROM categorias WHERE categoriaid = p_categoriaid;
    IF NOT FOUND THEN RAISE EXCEPTION 'Categoria inválida.'; END IF;

    -- Validar cinema
    PERFORM 1 FROM cinemas WHERE cinemaid = p_cinemaid;
    IF NOT FOUND THEN RAISE EXCEPTION 'Cinema inválido.'; END IF;

    -- Validar classificação etária
    PERFORM 1 FROM classificacoesetarias WHERE classificacaoid = p_classificacaoid;
    IF NOT FOUND THEN RAISE EXCEPTION 'Classificação inválida.'; END IF;

    -- Validar duração
    IF p_duracao < v_dmin OR p_duracao > v_dmax THEN
        RAISE EXCEPTION 'Duração inválida (%).', p_duracao;
    END IF;

    INSERT INTO filmes (
        categoriaid, cinemaid, titulo, datalancamento, duracao,
        produtora, fimexebicao, idioma, sinopse, classificacaoetaria, ranking
    )
    VALUES (
        p_categoriaid, p_cinemaid, p_titulo, p_datalanc, p_duracao,
        p_produtora, p_fim, p_idioma, p_sinopse, p_classificacaoid, p_ranking
    );
END;
$$;

----------------------------------------------------------------------------------------------
-- 2. INSERIR SESSÃO (gera automaticamente LUGARESSESSAO via trigger)
----------------------------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE inserir_sessao(
    p_salaid INT,
    p_filmeid INT,
    p_inicio TIMESTAMP,
    p_fim TIMESTAMP,
    p_versao VARCHAR,
    p_estado VARCHAR,
    p_preco NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cin_sala INT;
    v_cin_filme INT;
BEGIN
    -- Validar sala
    PERFORM 1 FROM salas WHERE salaid = p_salaid;
    IF NOT FOUND THEN RAISE EXCEPTION 'Sala não existe.'; END IF;

    -- Validar filme
    PERFORM 1 FROM filmes WHERE filmeid = p_filmeid;
    IF NOT FOUND THEN RAISE EXCEPTION 'Filme não existe.'; END IF;

    -- Verificar cinemas
    SELECT cinemaid INTO v_cin_sala FROM salas WHERE salaid = p_salaid;
    SELECT cinemaid INTO v_cin_filme FROM filmes WHERE filmeid = p_filmeid;

    IF v_cin_sala <> v_cin_filme THEN
        RAISE EXCEPTION 'Filme e sala pertencem a cinemas diferentes.';
    END IF;

    -- Validar horário
    IF p_inicio >= p_fim THEN
        RAISE EXCEPTION 'Início >= fim.';
    END IF;

    INSERT INTO sessoes (
        salaid, filmeid, inicio, fim, versao, estadosessao, precosessao
    )
    VALUES (
        p_salaid, p_filmeid, p_inicio, p_fim, p_versao, p_estado, p_preco
    );
END;
$$;

----------------------------------------------------------------------------------------------
-- 3. INSERIR PRODUTO
----------------------------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE inserir_produto(
    p_nome VARCHAR,
    p_preco NUMERIC,
    p_stock INT,
    p_ativo BOOLEAN
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_min CONSTANT NUMERIC := 0.10;
    v_max CONSTANT NUMERIC := 100.0;
BEGIN
    -- Nome
    IF p_nome IS NULL OR LENGTH(TRIM(p_nome)) = 0 THEN
        RAISE EXCEPTION 'Nome vazio.';
    END IF;

    -- Produto duplicado
    IF EXISTS (SELECT 1 FROM produtos WHERE nomeproduto ILIKE p_nome) THEN
        RAISE EXCEPTION 'Produto já existe.';
    END IF;

    -- Preço
    IF p_preco < v_min OR p_preco > v_max THEN
        RAISE EXCEPTION 'Preço fora dos limites permitidos.';
    END IF;

    -- Stock
    IF p_stock < 0 THEN
        RAISE EXCEPTION 'Stock inválido.';
    END IF;

    INSERT INTO produtos (nomeproduto, precoproduto, stock, ativo)
    VALUES (p_nome, p_preco, p_stock, p_ativo);
END;
$$;

----------------------------------------------------------------------------------------------
-- 4. INSERIR AVALIAÇÃO
----------------------------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE inserir_avaliacao(
    p_vendaid INT,
    p_titulo VARCHAR,
    p_cinema INT,
    p_filme INT,
    p_func INT,
    p_coment VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_est VARCHAR;
BEGIN
    -- Verificar venda
    SELECT estadovenda INTO v_est FROM vendas WHERE vendaid = p_vendaid;
    IF NOT FOUND THEN RAISE EXCEPTION 'Venda não existe.'; END IF;

    IF v_est <> 'Concluída' THEN
        RAISE EXCEPTION 'Venda não está concluída.';
    END IF;

    -- Verificar duplicado
    IF EXISTS (SELECT 1 FROM avaliacoes WHERE vendaid = p_vendaid) THEN
        RAISE EXCEPTION 'Avaliação já existe para esta venda.';
    END IF;

    INSERT INTO avaliacoes (
        vendaid, tituloavaliacao, avaliacaocinema, avaliacaofilme,
        avaliacaofuncionario, comentario
    )
    VALUES (
        p_vendaid, p_titulo, p_cinema, p_filme, p_func, p_coment
    );
END;
$$;

----------------------------------------------------------------------------------------------
-- 5. INSERIR CINEMA
----------------------------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE inserir_cinema(
    p_nome VARCHAR,
    p_email VARCHAR,
    p_telefone VARCHAR,
    p_morada VARCHAR,
    p_codpostal CHAR(8),
    p_localidade VARCHAR,
    p_ranking NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM cinemas
        WHERE nomecinema ILIKE p_nome
          AND localidadecinema ILIKE p_localidade
    ) THEN
        RAISE EXCEPTION 'Cinema duplicado.';
    END IF;

    INSERT INTO cinemas (
        nomecinema, emailcinema, telefonecinema, moradacinema,
        codigopostalcinema, localidadecinema, ranking
    )
    VALUES (
        p_nome, p_email, p_telefone, p_morada,
        p_codpostal, p_localidade, p_ranking
    );
END;
$$;

----------------------------------------------------------------------------------------------
-- 6. INSERIR CLIENTE
----------------------------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE inserir_cliente(
    p_nome VARCHAR,
    p_email VARCHAR,
    p_telefone VARCHAR,
    p_datanasc DATE,
    p_morada VARCHAR,
    p_codpostal CHAR(8),
    p_localidade VARCHAR,
    p_nif VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM clientes WHERE emailcliente = p_email) THEN
        RAISE EXCEPTION 'Email duplicado.';
    END IF;

    IF EXISTS (SELECT 1 FROM clientes WHERE nif = p_nif) THEN
        RAISE EXCEPTION 'NIF duplicado.';
    END IF;

    INSERT INTO clientes (
        nomecliente, emailcliente, telefonecliente, datanascimento,
        moradacliente, codigopostalcliente, localidadecliente, nif
    )
    VALUES (
        p_nome, p_email, p_telefone, p_datanasc,
        p_morada, p_codpostal, p_localidade, p_nif
    );
END;
$$;

----------------------------------------------------------------------------------------------
-- 7. INSERIR SALA (corrigido e simplificado)
----------------------------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE inserir_sala(
    p_cinemaid INT,
    p_nome VARCHAR,
    p_filas INT,
    p_colunas INT,
    p_tipo VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_exists INT;
BEGIN
    -- Validar cinema
    SELECT cinemaid INTO v_exists
    FROM cinemas
    WHERE cinemaid = p_cinemaid;

    IF v_exists IS NULL THEN
        RAISE EXCEPTION 'Cinema inexistente.';
    END IF;

    -- Validar dimensões
    IF p_filas <= 0 OR p_colunas <= 0 THEN
        RAISE EXCEPTION 'Dimensões inválidas (filas e colunas > 0).';
    END IF;

    INSERT INTO salas (cinemaid, nomesala, filas, colunas, tiposala)
    VALUES (p_cinemaid, p_nome, p_filas, p_colunas, p_tipo);
END;
$$;

----------------------------------------------------------------------------------------------
-- 8. INSERIR BILHETE (corrigido de forma definitiva)
----------------------------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE inserir_bilhete(
    p_lugarsessao INT,
    p_sessaoid INT,
    p_preco NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_sessao INT;
    v_lugar INT;
BEGIN
    -- Obter sessão e lugar reais
    SELECT sessaoid, lugarid
    INTO v_sessao, v_lugar
    FROM lugaresSessao
    WHERE lugarsessaoid = p_lugarsessao;

    IF v_sessao IS NULL THEN
        RAISE EXCEPTION 'Lugar da sessão inexistente.';
    END IF;

    -- Validar sessão
    IF v_sessao <> p_sessaoid THEN
        RAISE EXCEPTION 'Lugar não pertence à sessão indicada.';
    END IF;

    INSERT INTO bilhetes (lugarid, sessaoid, precobilhete, emissao)
    VALUES (v_lugar, p_sessaoid, p_preco, NOW());
END;
$$;

----------------------------------------------------------------------------------------------
-- 9. REALIZAR VENDA UNIFICADA (Transação completa)
----------------------------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE realizar_venda_unificada(
    p_clienteid INT,
    p_funcionarioid INT,
    p_sessaoid INT,
    p_lugares_ids JSONB, -- Ex: '[1, 2, 3]'
    p_produtos JSONB,    -- Ex: '[{"id": 1, "qtd": 2}, ...]'
    INOUT p_vendaid INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_item JSONB;
    v_lugar_sessao_id INT;
    v_prod_id INT;
    v_qtd INT;
    v_preco NUMERIC;
    v_stock_atual INT;
    v_filmeid INT;
    v_idade_ok BOOLEAN;
    v_livre BOOLEAN;
    v_bilheteid INT;
    v_total NUMERIC := 0;
BEGIN
    -- 1. Criar Venda
    INSERT INTO vendas (clienteid, funcionarioid, data, estadovenda, totalvenda)
    VALUES (p_clienteid, p_funcionarioid, CURRENT_DATE, 'Concluída', 0)
    RETURNING vendaid INTO p_vendaid;

    -- 2. Processar Bilhetes (se houver sessão e lugares)
    IF p_sessaoid IS NOT NULL AND p_lugares_ids IS NOT NULL AND jsonb_array_length(p_lugares_ids) > 0 THEN
        -- Obter dados da sessão/filme
        SELECT filmeid, precosessao INTO v_filmeid, v_preco
        FROM sessoes WHERE sessaoid = p_sessaoid;

        IF v_filmeid IS NULL THEN
            RAISE EXCEPTION 'Sessão % não encontrada.', p_sessaoid;
        END IF;

        -- Verificar Idade
        v_idade_ok := fn_verificar_idade_minima_filme(p_clienteid, v_filmeid);
        IF NOT v_idade_ok THEN
            RAISE EXCEPTION 'Cliente não tem idade suficiente para este filme.';
        END IF;

        -- Loop Lugares
        FOR v_item IN SELECT * FROM jsonb_array_elements(p_lugares_ids)
        LOOP
            v_lugar_sessao_id := (v_item::TEXT)::INT;

            -- Verificar disponibilidade
            v_livre := fn_verificar_disponibilidade_lugar(p_sessaoid, v_lugar_sessao_id);
            IF NOT v_livre THEN
                RAISE EXCEPTION 'Lugar % já está ocupado.', v_lugar_sessao_id;
            END IF;

            -- Ocupar lugar
            UPDATE lugaresSessao SET estado = 'OCUPADO' WHERE lugarsessaoid = v_lugar_sessao_id;

            -- Criar Bilhete
            INSERT INTO bilhetes (lugarid, sessaoid, precobilhete, emissao)
            VALUES (v_lugar_sessao_id, p_sessaoid, v_preco, NOW())
            RETURNING bilheteid INTO v_bilheteid;

            -- Criar Linha de Venda
            INSERT INTO vendalinhas (vendaid, bilheteid, quantidade, precolinha, total_linha_)
            VALUES (p_vendaid, v_bilheteid, 1, v_preco, v_preco);
        END LOOP;
    END IF;

    -- 3. Processar Produtos
    IF p_produtos IS NOT NULL AND jsonb_array_length(p_produtos) > 0 THEN
        FOR v_item IN SELECT * FROM jsonb_array_elements(p_produtos)
        LOOP
            v_prod_id := (v_item->>'id')::INT;
            v_qtd := (v_item->>'qtd')::INT;

            -- Obter preço e stock
            SELECT precoproduto, stock INTO v_preco, v_stock_atual
            FROM produtos WHERE produtoid = v_prod_id;

            IF v_preco IS NULL THEN
                RAISE EXCEPTION 'Produto % não encontrado.', v_prod_id;
            END IF;

            IF v_stock_atual < v_qtd THEN
                RAISE EXCEPTION 'Stock insuficiente para o produto %.', v_prod_id;
            END IF;

            -- O trigger trg_atualizar_stock_produtos vai descontar o stock automaticamente
            -- quando inserirmos na vendalinhas.

            INSERT INTO vendalinhas (vendaid, produtoid, quantidade, precolinha, total_linha_)
            VALUES (p_vendaid, v_prod_id, v_qtd, v_preco, v_preco * v_qtd);
        END LOOP;
    END IF;

    -- O total da venda é atualizado automaticamente pelo trigger trg_calcular_total_venda
END;
$$;