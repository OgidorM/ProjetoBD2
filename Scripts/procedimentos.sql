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