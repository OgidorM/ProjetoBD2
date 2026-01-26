----------------------------------------------------------------------------------------------
-- 1. INSERIR FILME
----------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS inserir_filme;
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
    p_ranking NUMERIC(2,1),
    p_cartaz_url VARCHAR,
    OUT p_novo_id INT
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
        produtora, fimexebicao, idioma, sinopse, classificacaoetaria, ranking, cartaz_url
    )
    VALUES (
        p_categoriaid, p_cinemaid, p_titulo, p_datalanc, p_duracao,
        p_produtora, p_fim, p_idioma, p_sinopse, p_classificacaoid, p_ranking, p_cartaz_url
    )
    RETURNING filmeid INTO p_novo_id;
END;
$$;

----------------------------------------------------------------------------------------------
-- 2. INSERIR SESSÃO (gera automaticamente LUGARESSESSAO via trigger)
----------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS inserir_sessao;
CREATE OR REPLACE PROCEDURE inserir_sessao(
    IN p_salaid INT,
    IN p_filmeid INT,
    IN p_inicio TIMESTAMP,
    IN p_fim TIMESTAMP,
    IN p_versao VARCHAR,
    IN p_estado VARCHAR,
    IN p_preco NUMERIC,
    OUT p_novo_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cin_sala INT;
    v_cin_filme INT;
BEGIN
    -- 1. Validar existência e obter IDs de Cinema
    SELECT cinemaid INTO v_cin_sala FROM salas WHERE salaid = p_salaid;
    IF NOT FOUND THEN RAISE EXCEPTION 'Sala não existe.'; END IF;

    SELECT cinemaid INTO v_cin_filme FROM filmes WHERE filmeid = p_filmeid;
    IF NOT FOUND THEN RAISE EXCEPTION 'Filme não existe.'; END IF;

    -- 2. Lógica de Atribuição de Cinema (Regra de Negócio)
    -- Se o filme não tem cinema, ganha o da sala.
    IF v_cin_filme IS NULL THEN
        UPDATE filmes SET cinemaid = v_cin_sala WHERE filmeid = p_filmeid;
    
    -- Se já tem, garantimos que não há mistura de cinemas
    ELSIF v_cin_sala <> v_cin_filme THEN
        RAISE EXCEPTION 'Conflito: O Filme pertence a um cinema diferente da Sala.';
    END IF;

    -- 3. Inserir (Os Triggers 5, 6 e 7 vão disparar AQUI)
    INSERT INTO sessoes (
        salaid, filmeid, inicio, fim, versao, estadosessao, precosessao
    )
    VALUES (
        p_salaid, p_filmeid, p_inicio, p_fim, p_versao, p_estado, p_preco
    )
    RETURNING sessaoid INTO p_novo_id;
END;
$$;

----------------------------------------------------------------------------------------------
-- 3. INSERIR PRODUTO
----------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS inserir_produto;
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
DROP PROCEDURE IF EXISTS inserir_avaliacao;
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
DROP PROCEDURE IF EXISTS inserir_cinema;
CREATE OR REPLACE PROCEDURE inserir_cinema(
    p_nome VARCHAR,
    p_email VARCHAR,
    p_telefone VARCHAR,
    p_morada VARCHAR,
    p_codpostal CHAR(8),
    p_localidade VARCHAR,
    p_ranking NUMERIC,
    OUT p_novo_id INT
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
    )
    RETURNING cinemaid INTO p_novo_id;
END;
$$;

----------------------------------------------------------------------------------------------
-- 6. INSERIR CLIENTE
----------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS inserir_cliente;
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
    IF p_email IS NULL OR LENGTH(TRIM(p_email)) = 0 THEN
        RAISE EXCEPTION 'Email obrigatório.';
    END IF;

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
    p_tipo VARCHAR,
    INOUT p_salaid INT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 1. Validações Simples
    IF NOT EXISTS (SELECT 1 FROM cinemas WHERE cinemaid = p_cinemaid) THEN
        RAISE EXCEPTION 'Cinema inexistente.';
    END IF;

    IF p_filas <= 0 OR p_colunas <= 0 THEN
        RAISE EXCEPTION 'Dimensões inválidas.';
    END IF;

    -- 2. Inserir apenas a Sala
    INSERT INTO salas (cinemaid, nomesala, filas, colunas, tiposala)
    VALUES (p_cinemaid, p_nome, p_filas, p_colunas, p_tipo)
    RETURNING salaid INTO p_salaid;

    -- 3. Confirmação
    RAISE NOTICE 'Sala % criada. Os lugares estão a ser gerados automaticamente pelos triggers.', p_salaid;
END;
$$;

----------------------------------------------------------------------------------------------
-- 8. INSERIR BILHETE (corrigido de forma definitiva)
----------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS inserir_bilhete;
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
-- 9. INSERIR FUNCIONÁRIO
----------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS inserir_funcionario;
CREATE OR REPLACE PROCEDURE inserir_funcionario(
    IN p_nome VARCHAR,
    IN p_email VARCHAR,
    IN p_telefone VARCHAR,
    IN p_cargo VARCHAR,
    IN p_salario NUMERIC(10, 2), -- Numeric é melhor para dinheiro que Float
    IN p_cinemaid INT,
    OUT p_novo_id INT -- Retorna o ID gerado
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 1. Validação: Email Obrigatório e Único
    IF p_email IS NULL OR LENGTH(TRIM(p_email)) = 0 THEN
        RAISE EXCEPTION 'O email é obrigatório.';
    END IF;

    IF EXISTS (SELECT 1 FROM funcionarios WHERE emailfuncionario = p_email) THEN
        RAISE EXCEPTION 'Este email já está registado num funcionário.';
    END IF;

    -- 2. Validação: Cinema (apenas se for fornecido ID)
    IF p_cinemaid IS NOT NULL THEN
        PERFORM 1 FROM cinemas WHERE cinemaid = p_cinemaid;
        IF NOT FOUND THEN 
            RAISE EXCEPTION 'O Cinema indicado não existe.'; 
        END IF;
    END IF;

    -- 3. Validação: Salário
    IF p_salario < 0 THEN
        RAISE EXCEPTION 'O salário não pode ser negativo.';
    END IF;

    -- 4. Inserção
    INSERT INTO funcionarios (
        nomefuncionario, 
        emailfuncionario, 
        telefonefuncionario, 
        cargo, 
        admissao, -- Automático
        salario, 
        cinemaid
    )
    VALUES (
        p_nome, 
        p_email, 
        p_telefone, 
        p_cargo, 
        CURRENT_DATE, -- Data de hoje no servidor SQL
        p_salario, 
        p_cinemaid
    )
    RETURNING funcionarioid INTO p_novo_id; -- Guarda o ID na variável de saída
END;
$$;

----------------------------------------------------------------------------------------------
-- 9. ALTERAR ESTADO SESSÃO
----------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS alterar_estado_sessao;
CREATE OR REPLACE PROCEDURE alterar_estado_sessao(
    p_sessaoid INT,
    p_novo_estado VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE sessoes
    SET estadosessao = p_novo_estado
    WHERE sessaoid = p_sessaoid;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Sessão % não encontrada.', p_sessaoid;
    END IF;
END;
$$;

----------------------------------------------------------------------------------------------
-- 10. INSERIR CATEGORIA
----------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS inserir_categoria;
CREATE OR REPLACE PROCEDURE inserir_categoria(
    IN p_nome VARCHAR,
    OUT p_novo_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 1. Validar input vazio
    IF p_nome IS NULL OR LENGTH(TRIM(p_nome)) = 0 THEN
        RAISE EXCEPTION 'O nome da categoria é obrigatório.';
    END IF;

    -- 2. Validar duplicados (Case insensitive opcional, aqui fiz exato)
    IF EXISTS (SELECT 1 FROM categorias WHERE nomecategoria = p_nome) THEN
        RAISE EXCEPTION 'Já existe uma categoria com esse nome.';
    END IF;

    -- 3. Inserir e Retornar ID
    INSERT INTO categorias (nomecategoria)
    VALUES (p_nome)
    RETURNING categoriaid INTO p_novo_id;
END;
$$;

----------------------------------------------------------------------------------------------
-- 11. ELIMINAR CATEGORIA
----------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS eliminar_categoria;
CREATE OR REPLACE PROCEDURE eliminar_categoria(p_categoriaid INT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_exists BOOLEAN;
    v_has_movies BOOLEAN;
BEGIN
    -- 1. Verificar se a categoria existe
    SELECT EXISTS(SELECT 1 FROM categorias WHERE categoriaid = p_categoriaid) INTO v_exists;
    
    IF NOT v_exists THEN
        RAISE EXCEPTION 'Categoria não encontrada.'; -- Erro 404
    END IF;

    -- 2. Verificar dependências (Se tem filmes associados)
    SELECT EXISTS(SELECT 1 FROM filmes WHERE categoriaid = p_categoriaid) INTO v_has_movies;

    IF v_has_movies THEN
        RAISE EXCEPTION 'Não é possível eliminar: Existem filmes associados a esta categoria.'; -- Erro 400
    END IF;

    -- 3. Eliminar
    DELETE FROM categorias WHERE categoriaid = p_categoriaid;
END;
$$;

----------------------------------------------------------------------------------------------
-- 12. CANCELAR BILHETE
----------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS cancelar_bilhete;
CREATE OR REPLACE PROCEDURE cancelar_bilhete(p_bilheteid INT)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 1. Verificar se o bilhete existe antes de tentar apagar
    IF NOT EXISTS (SELECT 1 FROM bilhetes WHERE bilheteid = p_bilheteid) THEN
        RAISE EXCEPTION 'Erro: O bilhete % não existe.', p_bilheteid;
    END IF;

    -- 2. Apagar primeiro a linha da venda (VendaLinhas) 
    DELETE FROM vendalinhas WHERE bilheteid = p_bilheteid;

    -- 3. Apagar o Bilhete (ativa o trigger)
    DELETE FROM bilhetes WHERE bilheteid = p_bilheteid;

    -- Opcional: Log ou mensagem de sucesso
    RAISE NOTICE 'Bilhete % cancelado e lugar libertado via Trigger.', p_bilheteid;
END;
$$;

----------------------------------------------------------------------------------------------
-- 13. ELIMINAR SESSÃO
----------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS eliminar_sessao;
CREATE OR REPLACE PROCEDURE eliminar_sessao(p_sessaoid INT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contagem_bilhetes INT;
    v_existe BOOLEAN;
BEGIN
    -- 1. Verificar se a sessão existe
    SELECT EXISTS(SELECT 1 FROM sessoes WHERE sessaoid = p_sessaoid) INTO v_existe;
    IF NOT v_existe THEN
        RAISE EXCEPTION 'Sessão não encontrada.'; -- Código para 404
    END IF;

    -- 2. Verificar se existem bilhetes vendidos
    SELECT COUNT(*) INTO v_contagem_bilhetes FROM bilhetes WHERE sessaoid = p_sessaoid;
    IF v_contagem_bilhetes > 0 THEN
        RAISE EXCEPTION 'Não é possível eliminar: existem bilhetes vendidos para esta sessão.'; -- Código para 400
    END IF;

    -- 3. Limpar LugaresSessao (Dependência obrigatória)
    DELETE FROM lugaressessao WHERE sessaoid = p_sessaoid;

    -- 4. Eliminar a sessão
    DELETE FROM sessoes WHERE sessaoid = p_sessaoid;
END;
$$;

----------------------------------------------------------------------------------------------
-- 14. ELIMINAR FILME
----------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS eliminar_filme;
CREATE OR REPLACE PROCEDURE eliminar_filme(p_filmeid INT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_existe BOOLEAN;
    v_tem_sessoes BOOLEAN;
BEGIN
    -- 1. Verificar se o filme existe
    SELECT EXISTS(SELECT 1 FROM filmes WHERE filmeid = p_filmeid) INTO v_existe;
    IF NOT v_existe THEN
        RAISE EXCEPTION 'Filme não encontrado.';
    END IF;

    -- 2. Verificar se existem sessões (mesmo que antigas)
    SELECT EXISTS(SELECT 1 FROM sessoes WHERE filmeid = p_filmeid) INTO v_tem_sessoes;
    IF v_tem_sessoes THEN
        RAISE EXCEPTION 'Não é possível eliminar: existem sessões associadas a este filme.';
    END IF;

    -- 3. Eliminar o filme
    DELETE FROM filmes WHERE filmeid = p_filmeid;
END;
$$;

----------------------------------------------------------------------------------------------
-- 15. DESATIVAR PRODUTO
----------------------------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE desativar_produto(p_produtoid INT)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE produtos SET ativo = FALSE WHERE produtoid = p_produtoid;
    IF NOT FOUND THEN RAISE EXCEPTION 'Produto não encontrado.'; END IF;
END;
$$;

----------------------------------------------------------------------------------------------
-- 16. AJUSTAR STOCK PRODUTO
----------------------------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE ajustar_stock_produto(
    p_produtoid INT, 
    p_variacao INT, 
    INOUT p_novo_stock INT DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE produtos 
    SET stock = stock + p_variacao 
    WHERE produtoid = p_produtoid
    RETURNING stock INTO p_novo_stock;

    IF p_novo_stock < 0 THEN RAISE EXCEPTION 'Stock insuficiente.'; END IF;
END;
$$;

----------------------------------------------------------------------------------------------
-- 17. EDITAR PRODUTO
----------------------------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE editar_produto(
    p_produtoid INT, 
    p_nome VARCHAR, 
    p_preco NUMERIC, 
    p_stock_total INT
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE produtos 
    SET nomeproduto = p_nome, 
        precoproduto = p_preco, 
        stock = p_stock_total
    WHERE produtoid = p_produtoid;
END;
$$;

-----------------------------------------------------------------------------------------------
-- 18. ELIMINAR CLIENTE
-----------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS eliminar_cliente;
CREATE OR REPLACE PROCEDURE eliminar_cliente(p_clienteid INT)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM clientes WHERE clienteid = p_clienteid;
    IF NOT FOUND THEN RAISE EXCEPTION 'Cliente não encontrado.'; END IF;
END;
$$;

-----------------------------------------------------------------------------------------------
-- 19. EDITAR CLIENTE
-----------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS editar_cliente;
CREATE OR REPLACE PROCEDURE editar_cliente(
    p_clienteid INT, 
    p_nome VARCHAR, 
    p_email VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE clientes 
    SET nomecliente = COALESCE(p_nome, nomecliente),
        emailcliente = COALESCE(p_email, emailcliente)
    WHERE clienteid = p_clienteid;
    
    IF NOT FOUND THEN RAISE EXCEPTION 'Cliente não encontrado.'; END IF;
END;
$$;

-----------------------------------------------------------------------------------------------
-- 20. ELIMINAR FUNCIONÁRIO
-----------------------------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE proc_eliminar_funcionario(p_id INT)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM funcionarios WHERE funcionarioid = p_id;
    IF NOT FOUND THEN RAISE EXCEPTION 'Funcionário não encontrado.'; END IF;
END;
$$;

-----------------------------------------------------------------------------------------------
-- 21. EDITAR FUNCIONÁRIO
-----------------------------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE editar_funcionario(
    p_id INT, 
    p_nome VARCHAR, 
    p_cargo VARCHAR, 
    p_salario NUMERIC
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_salario < 0 THEN RAISE EXCEPTION 'O salário não pode ser negativo.'; END IF;

    UPDATE funcionarios 
    SET nomefuncionario = COALESCE(p_nome, nomefuncionario),
        cargo = COALESCE(p_cargo, cargo),
        salario = COALESCE(p_salario, salario)
    WHERE funcionarioid = p_id;
    
    IF NOT FOUND THEN RAISE EXCEPTION 'Funcionário não encontrado.'; END IF;
END;
$$;