--1-----------------------------------------------------------------------------------------------
-- Procedimentos 2x
--Inserir Filme
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
    p_ranking NUMERIC(2,1) DEFAULT 0.0
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_exists BOOLEAN;
    v_duracao_min CONSTANT INT := 10;   -- duração mínima
    v_duracao_max CONSTANT INT := 300;  -- duração máxima
BEGIN
    -- validar título
    IF p_titulo IS NULL OR LENGTH(TRIM(p_titulo)) = 0 THEN
        RAISE EXCEPTION 'Título do filme não pode ser vazio';
    END IF;

    -- validar categoria
    PERFORM 1 FROM categorias WHERE categoriaid = p_categoriaid;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Categoria % não existe', p_categoriaid;
    END IF;

    -- validar cinema
    PERFORM 1 FROM cinemas WHERE cinemaid = p_cinemaid;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Cinema % não existe', p_cinemaid;
    END IF;

    -- validar classificação etária
    PERFORM 1 FROM classificacoesetarias WHERE classificacaoid = p_classificacaoid;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Classificação etária % não existe', p_classificacaoid;
    END IF;

    -- validar duração
    IF p_duracao < v_duracao_min OR p_duracao > v_duracao_max THEN
        RAISE EXCEPTION 'Duração inválida: %. Deve estar entre % e % minutos',
            p_duracao, v_duracao_min, v_duracao_max;
    END IF;

    -- aviso para idiomas diferentes do normal
    IF p_idioma NOT IN ('PT', 'EN', 'ES', 'FR') THEN
        RAISE NOTICE 'Idioma "%" não é um dos habituais (PT, EN, ES, FR)', p_idioma;
    END IF;

    -- inserir filme
    INSERT INTO filmes (categoriaid, cinemaid, titulo, datalancamento,
                        duracao, produtora, fimexebicao, idioma, sinopse,
                        classificacaoetaria, ranking)
    VALUES (p_categoriaid, p_cinemaid, p_titulo, p_datalanc,
            p_duracao, p_produtora, p_fim, p_idioma, p_sinopse,
            p_classificacaoid, p_ranking);

    RAISE NOTICE 'Filme "%" inserido no cinema % (categoria %, duração % min)',
        p_titulo, p_cinemaid, p_categoriaid, p_duracao;
END;
$$;

-----------------------------------------------------
--Inserir Sessão
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
    v_exists BOOLEAN;
    v_preco_min CONSTANT NUMERIC := 1.0;   -- preço mínimo
    v_preco_max CONSTANT NUMERIC := 20.0;  -- preço máximo
BEGIN
    -- validar sala
    PERFORM 1 FROM salas WHERE salaid = p_salaid;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Sala % não existe', p_salaid;
    END IF;

    -- validar filme
    PERFORM 1 FROM filmes WHERE filmeid = p_filmeid;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Filme % não existe', p_filmeid;
    END IF;

	-- verificar se filme e sala pertencem ao mesmo cinema
    IF v_cinema_sala IS DISTINCT FROM v_cinema_filme THEN
        RAISE EXCEPTION 'Sala % (cinema %) não corresponde ao mesmo cinema do filme % (cinema %)',
            p_salaid, v_cinema_sala, p_filmeid, v_cinema_filme;
    END IF;

    -- validar datas
    IF p_inicio >= p_fim THEN
        RAISE EXCEPTION 'Início da sessão não pode ser >= fim';
    END IF;
    IF p_fim < NOW() THEN
        RAISE EXCEPTION 'Atenção: sessão já terminaria no passado (%).', p_fim;
    END IF;

    -- validar preço
    IF p_preco < v_preco_min OR p_preco > v_preco_max THEN
        RAISE EXCEPTION 'Preço inválido: %. Deve estar entre % e %',
            p_preco, v_preco_min, v_preco_max;
    END IF;

    -- aviso se estado não for "Ativa", "Cancelada" ou "Agendada"
    IF p_estado NOT IN ('Ativa', 'Cancelada', 'Agendada') THEN
        RAISE NOTICE 'Estado "%" não é um dos habituais (Ativa, Cancelada, Agendada)', p_estado;
    END IF;

    -- inserir sessão
    INSERT INTO sessoes (salaid, filmeid, inicio, fim, versao, estadosessao, precosessao)
    VALUES (p_salaid, p_filmeid, p_inicio, p_fim, p_versao, p_estado, p_preco);

    RAISE NOTICE 'Sessão inserida: Sala %, Filme %, Início %, Preço %€',
        p_salaid, p_filmeid, p_inicio, p_preco;
END;
$$;

--2-----------------------------------------------------------------------------------------------
-- Procedimentos 2x
--Inserir Produto
CREATE OR REPLACE PROCEDURE inserir_produto(
    p_nome    VARCHAR,
    p_preco   NUMERIC,
    p_stock   INT,
    p_ativo   BOOLEAN DEFAULT TRUE
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_preco_min CONSTANT NUMERIC := 0.10;  -- preço mínimo 
    v_preco_max CONSTANT NUMERIC := 100.0; -- preço máximo 
    v_stock_max CONSTANT INT := 10000;     -- stock máximo 
BEGIN
    -- validar nome
    IF p_nome IS NULL OR LENGTH(TRIM(p_nome)) = 0 THEN
        RAISE EXCEPTION 'Nome do produto não pode ser vazio';
    END IF;

    -- validar preço
    IF p_preco IS NULL OR p_preco < v_preco_min OR p_preco > v_preco_max THEN
        RAISE EXCEPTION 'Preço inválido: %. Deve estar entre % e %',
            p_preco, v_preco_min, v_preco_max;
    END IF;

    -- validar stock
    IF p_stock IS NULL OR p_stock < 0 THEN
        RAISE EXCEPTION 'Stock inválido: %. Deve ser >= 0', p_stock;
    ELSIF p_stock > v_stock_max THEN
        RAISE NOTICE 'Stock elevado: % (máx. recomendado %)', p_stock, v_stock_max;
    END IF;

    -- verificar duplicados por nome
    IF EXISTS (SELECT 1 FROM produtos WHERE nomeproduto ILIKE p_nome) THEN
        RAISE NOTICE 'Já existe produto chamado "%". Será inserido assim mesmo.', p_nome;
    END IF;

    -- inserir produto
    INSERT INTO produtos (nomeproduto, precoproduto, stock, ativo)
    VALUES (p_nome, p_preco, p_stock, p_ativo);

    RAISE NOTICE 'Produto "%" inserido (preço: %, stock: %)', p_nome, p_preco, p_stock;
END;
$$;

-----------------------------------------------------
--Inserir Avaliação
CREATE OR REPLACE PROCEDURE inserir_avaliacao(
    p_vendaid INT,
    p_titulo  VARCHAR,
    p_cinema  INT,
    p_filme   INT,
    p_func    INT,
    p_coment  VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_estadovenda VARCHAR(20);
    v_min_nota CONSTANT INT := 1;
    v_max_nota CONSTANT INT := 5;
BEGIN
    -- verificar se venda existe e obter estado
    SELECT estadovenda
    INTO v_estadovenda
    FROM vendas
    WHERE vendaid = p_vendaid;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Venda % não existe', p_vendaid;
    END IF;

    -- validar se venda está concluída
    IF v_estadovenda <> 'Concluída' THEN
        RAISE EXCEPTION 'Venda % não está concluída (estado atual: "%")',
            p_vendaid, v_estadovenda;
    END IF;

    -- validar título
    IF p_titulo IS NULL OR LENGTH(TRIM(p_titulo)) = 0 THEN
        RAISE EXCEPTION 'Título da avaliação não pode ser vazio';
    END IF;

    -- validar notas
    IF p_cinema IS NOT NULL AND (p_cinema < v_min_nota OR p_cinema > v_max_nota) THEN
        RAISE EXCEPTION 'Avaliação do cinema inválida: %. Deve estar entre % e %',
            p_cinema, v_min_nota, v_max_nota;
    END IF;

    IF p_filme IS NOT NULL AND (p_filme < v_min_nota OR p_filme > v_max_nota) THEN
        RAISE EXCEPTION 'Avaliação do filme inválida: %. Deve estar entre % e %',
            p_filme, v_min_nota, v_max_nota;
    END IF;

    IF p_func IS NOT NULL AND (p_func < v_min_nota OR p_func > v_max_nota) THEN
        RAISE EXCEPTION 'Avaliação do funcionário inválida: %. Deve estar entre % e %',
            p_func, v_min_nota, v_max_nota;
    END IF;

    -- verificar se já existe avaliação para esta venda
    IF EXISTS (SELECT 1 FROM avaliacoes WHERE vendaid = p_vendaid) THEN
        RAISE EXCEPTION 'Já existe avaliação registada para a venda %', p_vendaid;
    END IF;

    -- inserir avaliação
    INSERT INTO avaliacoes (vendaid, tituloavaliacao, avaliacaocinema,
                            avaliacaofilme, avaliacaofuncionario, comentario)
    VALUES (p_vendaid, p_titulo, p_cinema, p_filme, p_func, p_coment);

    RAISE NOTICE 'Avaliação criada para venda %: "%"', p_vendaid, p_titulo;
END;
$$;

--3-----------------------------------------------------------------------------------------------
-- Procedimentos 2x
CREATE OR REPLACE PROCEDURE inserir_cinema(
    p_nome       VARCHAR,
    p_email      VARCHAR DEFAULT NULL,
    p_telefone   VARCHAR DEFAULT NULL,
    p_morada     VARCHAR DEFAULT NULL,
    p_codpostal  CHAR(8) DEFAULT NULL,
    p_localidade VARCHAR,
    p_ranking    NUMERIC(2,1) DEFAULT 0.0
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_max_ranking CONSTANT NUMERIC(2,1) := 5.0;
BEGIN
    -- validar nome
    IF p_nome IS NULL OR LENGTH(TRIM(p_nome)) = 0 THEN
        RAISE EXCEPTION 'Nome do cinema não pode ser vazio';
    END IF;

    -- verificar duplicados (mesmo nome + mesma localidade)
    IF EXISTS (
        SELECT 1 FROM cinemas
        WHERE nomecinema ILIKE p_nome
          AND localidadecinema ILIKE p_localidade
    ) THEN
        RAISE EXCEPTION 'Já existe um cinema chamado "%" em %', p_nome, p_localidade;
    END IF;

    -- validar código postal (formato simples NNNN-NNN)
    IF p_codpostal IS NOT NULL AND p_codpostal !~ '^[0-9]{4}-[0-9]{3}$' THEN
        RAISE NOTICE 'Código postal "%" não segue o formato NNNN-NNN', p_codpostal;
    END IF;

    -- validar ranking inicial
    IF p_ranking < 0 OR p_ranking > v_max_ranking THEN
        RAISE NOTICE 'Ranking inicial ajustado para 0. Valor inválido recebido: %', p_ranking;
        p_ranking := 0;
    END IF;

    -- inserir cinema
    INSERT INTO cinemas (nomecinema, emailcinema, telefonecinema,
                         moradacinema, codigopostalcinema,
                         localidadecinema, ranking)
    VALUES (p_nome, p_email, p_telefone, p_morada, p_codpostal, p_localidade, p_ranking);

    RAISE NOTICE 'Cinema "%" criado em % (ranking inicial: %)',
        p_nome, p_localidade, p_ranking;
END;
$$;

-----------------------------------------------------
--Inserir Cliente
CREATE OR REPLACE PROCEDURE inserir_cliente(
    p_nome       VARCHAR,
    p_email      VARCHAR,
    p_telefone   VARCHAR,
    p_datanasc   DATE,
    p_morada     VARCHAR,
    p_codpostal  CHAR(8),
    p_localidade VARCHAR,
    p_nif        VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_idade INT;
    v_idade_min CONSTANT INT := 12; -- idade mínima
BEGIN
    -- validar nome
    IF p_nome IS NULL OR LENGTH(TRIM(p_nome)) = 0 THEN
        RAISE EXCEPTION 'Nome do cliente não pode ser vazio';
    END IF;

    -- verificar duplicados por email
    IF EXISTS (SELECT 1 FROM clientes WHERE emailcliente ILIKE p_email) THEN
        RAISE EXCEPTION 'Já existe um cliente registado com o email %', p_email;
    END IF;

    -- verificar duplicados por NIF
    IF EXISTS (SELECT 1 FROM clientes WHERE nif = p_nif) THEN
        RAISE EXCEPTION 'Já existe um cliente registado com o NIF %', p_nif;
    END IF;

    -- validar código postal (NNNN-NNN)
    IF p_codpostal IS NOT NULL AND p_codpostal !~ '^[0-9]{4}-[0-9]{3}$' THEN
        RAISE NOTICE 'Código postal "%" não segue o formato NNNN-NNN', p_codpostal;
    END IF;

    -- validar idade mínima
    IF p_datanasc IS NOT NULL THEN
        SELECT DATE_PART('year', AGE(CURRENT_DATE, p_datanasc)) INTO v_idade;
        IF v_idade < v_idade_min THEN
            RAISE EXCEPTION 'Cliente deve ter pelo menos % anos (% anos fornecidos)',
                v_idade_min, v_idade;
        END IF;
    END IF;

    -- inserir cliente
    INSERT INTO clientes (nomecliente, emailcliente, telefonecliente,
                          datanascimento, moradacliente, codigopostalcliente,
                          localidadecliente, nif)
    VALUES (p_nome, p_email, p_telefone, p_datanasc,
            p_morada, p_codpostal, p_localidade, p_nif);

    RAISE NOTICE 'Cliente "%" criado com sucesso (NIF: %)', p_nome, p_nif;
END;
$$;

--4-----------------------------------------------------------------------------------------------
--Inserir sala
CREATE OR REPLACE PROCEDURE inserir_bilhete(p_lugarid INT, p_sessaoid INT, p_preco NUMERIC)
LANGUAGE plpgsql
AS $$
DECLARE
    v_salaid INT;
    v_salaid_lugar INT;
BEGIN
    -- verificar se a sessão existe
    IF NOT EXISTS (SELECT 1 FROM sessoes WHERE sessaoid = p_sessaoid) THEN
        RAISE EXCEPTION 'Sessão % não existe', p_sessaoid;
    END IF;

    -- obter sala da sessão
    SELECT salaid INTO v_salaid FROM sessoes WHERE sessaoid = p_sessaoid;

    -- obter sala do lugar
    SELECT salaid INTO v_salaid_lugar FROM lugares WHERE lugarid = p_lugarid;

    IF v_salaid IS DISTINCT FROM v_salaid_lugar THEN
        RAISE EXCEPTION 'Lugar % não pertence à sala da sessão %', p_lugarid, p_sessaoid;
    END IF;

    -- verificar se já existe bilhete para o mesmo lugar/sessão
    IF EXISTS (SELECT 1 FROM bilhetes WHERE lugarid = p_lugarid AND sessaoid = p_sessaoid) THEN
        RAISE EXCEPTION 'Lugar % já está ocupado na sessão %', p_lugarid, p_sessaoid;
    END IF;

    -- inserir bilhete
    INSERT INTO bilhetes (lugarid, sessaoid, precobilhete, emissao)
    VALUES (p_lugarid, p_sessaoid, p_preco, NOW());

    -- atualizar estado do lugar
    UPDATE lugares
    SET estadolugar = 'Ocupado'
    WHERE lugarid = p_lugarid;
END;
$$;

-----------------------------------------------------
--Inserir sala
CREATE OR REPLACE PROCEDURE inserir_sala(
    p_cinemaid INT,
    p_nomesala VARCHAR,
    p_capacidade INT,
    p_tiposala VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_exists BOOLEAN;
    v_max_capacidade CONSTANT INT := 1000;
BEGIN
    -- verificar se cinema existe
    SELECT TRUE INTO v_exists FROM cinemas WHERE cinemaid = p_cinemaid;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Cinema % não existe', p_cinemaid;
    END IF;

    -- validar capacidade
    IF p_capacidade <= 0 THEN
        RAISE EXCEPTION 'Capacidade inválida: %', p_capacidade;
    ELSIF p_capacidade > v_max_capacidade THEN
        RAISE EXCEPTION 'Capacidade demasiado elevada: % (máx. %)',
            p_capacidade, v_max_capacidade;
    END IF;

    -- verificar duplicados de nome de sala no mesmo cinema
    IF EXISTS (
        SELECT 1 FROM salas
        WHERE cinemaid = p_cinemaid AND nomesala ILIKE p_nomesala
    ) THEN
        RAISE EXCEPTION 'Já existe uma sala chamada "%" no cinema %',
            p_nomesala, p_cinemaid;
    END IF;

    -- aviso se tipo de sala não for um dos comuns
    IF p_tiposala NOT IN ('Standard', 'VIP', 'IMAX') THEN
        RAISE NOTICE 'Tipo de sala "%" não é habitual (Standard, VIP, IMAX)',
            p_tiposala;
    END IF;

    -- inserir sala
    INSERT INTO salas (cinemaid, nomesala, capacidade, tiposala)
    VALUES (p_cinemaid, p_nomesala, p_capacidade, p_tiposala);

    RAISE NOTICE 'Sala "%" criada para o cinema % (capacidade: %, tipo: %)',
        p_nomesala, p_cinemaid, p_capacidade, p_tiposala;
END;
$$;


-----------------------------------------------------
--Inserir categoria
CREATE OR REPLACE PROCEDURE inserir_categoria(
    p_nome VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_exists BOOLEAN;
BEGIN
    -- validar nome
    IF p_nome IS NULL OR LENGTH(TRIM(p_nome)) = 0 THEN
        RAISE EXCEPTION 'O nome da categoria não pode ser vazio';
    END IF;
    -- verificar se já existe categoria com o mesmo nome
    SELECT TRUE INTO v_exists
    FROM categorias
    WHERE nomecategoria ILIKE p_nome;
    IF FOUND THEN
        RAISE EXCEPTION 'Já existe uma categoria chamada "%"', p_nome;
    END IF;
    -- inserir categoria
    INSERT INTO categorias (nomecategoria)
    VALUES (p_nome);
    RAISE NOTICE 'Categoria "%" criada com sucesso', p_nome;
END;
$$;


-----------------------------------------------------
--Inserir funcionario
CREATE OR REPLACE PROCEDURE inserir_funcionario(
    p_cinemaid INT,
    p_nome VARCHAR,
    p_cargo VARCHAR,
    p_email VARCHAR DEFAULT NULL,
    p_telefone VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_exists BOOLEAN;
BEGIN
    -- validar nome
    IF p_nome IS NULL OR LENGTH(TRIM(p_nome)) = 0 THEN
        RAISE EXCEPTION 'O nome do funcionário não pode ser vazio';
    END IF;
    -- validar cargo
    IF p_cargo IS NULL OR LENGTH(TRIM(p_cargo)) = 0 THEN
        RAISE EXCEPTION 'O cargo do funcionário não pode ser vazio';
    END IF;
    -- verificar se cinema existe
    PERFORM 1 FROM cinemas WHERE cinemaid = p_cinemaid;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Cinema % não existe', p_cinemaid;
    END IF;
    -- verificar duplicados (nome + cinema)
    SELECT TRUE INTO v_exists
    FROM funcionarios
    WHERE nomefuncionario ILIKE p_nome
      AND cinemaid = p_cinemaid;
    IF FOUND THEN
        RAISE EXCEPTION 'Já existe um funcionário chamado "%" no cinema %', p_nome, p_cinemaid;
    END IF;
    -- inserir funcionário
    INSERT INTO funcionarios (cinemaid, nomefuncionario, cargo, emailfuncionario, telefonefuncionario)
    VALUES (p_cinemaid, p_nome, p_cargo, p_email, p_telefone);
    RAISE NOTICE 'Funcionário "%" inserido no cinema % com cargo "%"', p_nome, p_cinemaid, p_cargo;
END;
$$;