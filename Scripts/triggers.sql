/*==============================================================
    1 - Atualizar rankings (cinema, funcionario, filme)          
    Sempre que entra uma nova avaliacao, recalcula as medias 
==============================================================*/
CREATE OR REPLACE FUNCTION trg_atualizar_rankings_avaliacoes()
RETURNS TRIGGER AS $$
BEGIN
    /* Atualizar ranking dos CINEMAS */
    -- Vai buscar todas as avaliacoes deste cinema e faz a media
    UPDATE cinemas c
    SET ranking = (
        SELECT ROUND(AVG(a.avaliacaocinema)::numeric,1)
        FROM avaliacoes a
        JOIN vendas v   ON v.vendaid = a.vendaid
        JOIN funcionarios f ON f.funcionarioid = v.funcionarioid
        WHERE f.cinemaid = c.cinemaid
    )
    WHERE EXISTS (
        SELECT 1
        FROM avaliacoes a
        JOIN vendas v ON v.vendaid = a.vendaid
        JOIN funcionarios f ON f.funcionarioid = v.funcionarioid
        WHERE f.cinemaid = c.cinemaid
    );

    /* Atualizar ranking dos FUNCIONARIOS */
    -- Recalcula a nota do funcionario baseada nas vendas dele
    UPDATE funcionarios f
    SET ranking = (
        SELECT ROUND(AVG(a.avaliacaofuncionario)::numeric,1)
        FROM avaliacoes a
        JOIN vendas v ON v.vendaid = a.vendaid
        WHERE v.funcionarioid = f.funcionarioid
    )
    WHERE EXISTS (
        SELECT 1
        FROM avaliacoes a
        JOIN vendas v ON v.vendaid = a.vendaid
        WHERE v.funcionarioid = f.funcionarioid
    );

    /* Atualizar ranking dos FILMES */
    -- da venda associada à avaliação
    -- vai até ao filmes atraves do bilhete
    UPDATE filmes fi
    SET ranking = (
        SELECT ROUND(AVG(a.avaliacaofilme)::numeric,1)
        FROM avaliacoes a
        JOIN vendas v ON v.vendaid = a.vendaid
        JOIN vendalinhas vl ON vl.vendaid = v.vendaid
        JOIN bilhetes b ON b.bilheteid = vl.bilheteid
        JOIN sessoes s ON s.sessaoid = b.sessaoid
        WHERE s.filmeid = fi.filmeid
          AND a.avaliacaofilme IS NOT NULL
    )
    WHERE EXISTS (
        SELECT 1
        FROM avaliacoes a
        JOIN vendas v ON v.vendaid = a.vendaid
        JOIN vendalinhas vl ON vl.vendaid = v.vendaid
        JOIN bilhetes b ON b.bilheteid = vl.bilheteid
        JOIN sessoes s ON s.sessaoid = b.sessaoid
        WHERE s.filmeid = fi.filmeid
    );

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_atualizar_rankings_avaliacoes
AFTER INSERT OR UPDATE OR DELETE ON avaliacoes
FOR EACH STATEMENT
EXECUTE FUNCTION trg_atualizar_rankings_avaliacoes();


/*==============================================================
    2 - Garante notas validas em avaliacoes                      
    Garantir que as notas ficam entre 0 e 5      
==============================================================*/
CREATE OR REPLACE FUNCTION trg_validar_valores_avaliacoes()
RETURNS TRIGGER AS $$
BEGIN
    IF (NEW.avaliacaocinema IS NOT NULL AND (NEW.avaliacaocinema < 0 OR NEW.avaliacaocinema > 5))
       OR (NEW.avaliacaofilme IS NOT NULL AND (NEW.avaliacaofilme < 0 OR NEW.avaliacaofilme > 5))
       OR (NEW.avaliacaofuncionario IS NOT NULL AND (NEW.avaliacaofuncionario < 0 OR NEW.avaliacaofuncionario > 5))
    THEN
        RAISE EXCEPTION 'Valores de avaliação devem estar entre 0 e 5.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_valores_avaliacoes
BEFORE INSERT OR UPDATE ON avaliacoes
FOR EACH ROW
EXECUTE FUNCTION trg_validar_valores_avaliacoes();


/*==============================================================
    3 - TOTALVENDA sempre atualizado                             
    O total da venda atualiza sempre que são adicionadas coisas
/*==============================================================*/
CREATE OR REPLACE FUNCTION trg_calcular_total_venda()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE vendas
    SET totalvenda = (
        SELECT COALESCE(SUM(total_linha_),0)
        FROM vendalinhas
        WHERE vendaid = COALESCE(NEW.vendaid, OLD.vendaid)
    )
    WHERE vendaid = COALESCE(NEW.vendaid, OLD.vendaid);

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calcular_total_venda
AFTER INSERT OR UPDATE OR DELETE ON vendalinhas
FOR EACH ROW
EXECUTE FUNCTION trg_calcular_total_venda();


/*==============================================================
    4 - Reduz stock quando e vendido um produto                     
/*==============================================================*/
CREATE OR REPLACE FUNCTION trg_atualizar_stock_produtos()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.produtoid IS NOT NULL THEN
        UPDATE produtos
        SET stock = stock - NEW.quantidade
        WHERE produtoid = NEW.produtoid;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_atualizar_stock_produtos
AFTER INSERT ON vendalinhas
FOR EACH ROW
EXECUTE FUNCTION trg_atualizar_stock_produtos();


/*==============================================================
    5 - Verifica limites de exibicao do filme                    
    Nao abrir sessoes para filmes que nao estão em exibição ou já passaram
/*==============================================================*/
CREATE OR REPLACE FUNCTION trg_confirmar_limites_exibicao_filme()
RETURNS TRIGGER AS $$
DECLARE
    data_inicio DATE;
    data_fim DATE;
BEGIN
    SELECT f.datalancamento, f.fimexebicao
    INTO data_inicio, data_fim
    FROM filmes f
    WHERE f.filmeid = NEW.filmeid;

    IF NEW.inicio::DATE < data_inicio THEN
        RAISE EXCEPTION 'Sessão marcada antes do lançamento do filme.';
    END IF;

    IF data_fim IS NOT NULL AND NEW.fim::DATE > data_fim THEN
        RAISE EXCEPTION 'Sessão excede data limite de exibição.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_confirmar_limites_exibicao_filme
BEFORE INSERT OR UPDATE ON sessoes
FOR EACH ROW
EXECUTE FUNCTION trg_confirmar_limites_exibicao_filme();


/*==============================================================
    6 - Verifica inicio < fim do filme                            
    o filme nao pode acabar antes de comecar                
/*==============================================================*/
CREATE OR REPLACE FUNCTION trg_confirmar_inicio_menor_que_fim()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.inicio >= NEW.fim THEN
        RAISE EXCEPTION 'A data/hora de início deve ser anterior ao fim.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_confirmar_inicio_menor_que_fim
BEFORE INSERT OR UPDATE ON sessoes
FOR EACH ROW
EXECUTE FUNCTION trg_confirmar_inicio_menor_que_fim();


/*==============================================================
    7 - Impede sessoes sobrepostas na mesma sala                 
    Se a sala ja tem filme aquela hora, nao deixa marcar outro em cima        
/*==============================================================*/
CREATE OR REPLACE FUNCTION trg_verificar_datas_sessao()
RETURNS TRIGGER AS $$
DECLARE
    conflito INT;
BEGIN
    SELECT COUNT(*)
    INTO conflito
    FROM sessoes s
    WHERE s.salaid = NEW.salaid
      AND s.sessaoid <> COALESCE(NEW.sessaoid,0)
      -- OVERLAPS e magico: ve se dois periodos de tempo se tocam
      AND (NEW.inicio, NEW.fim) OVERLAPS (s.inicio, s.fim);

    IF conflito > 0 THEN
        RAISE EXCEPTION 'A sala % já tem uma sessão que se sobrepõe.', NEW.salaid;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_verificar_datas_sessao
BEFORE INSERT OR UPDATE ON sessoes
FOR EACH ROW
EXECUTE FUNCTION trg_verificar_datas_sessao();


/*==============================================================
    8 - Verifica capacidade da sala antes de criar sessoes
    Ve se a sala existe mesmo e se tem lugares definidos antes de criar sessao
==============================================================*/
CREATE OR REPLACE FUNCTION trg_verificar_capacidade_sala()
RETURNS TRIGGER AS $$
DECLARE
    cap INT;
BEGIN
    SELECT capacidade INTO cap
    FROM salas
    WHERE salaid = NEW.salaid;

    IF cap IS NULL OR cap <= 0 THEN
        RAISE EXCEPTION 'A sala % não tem capacidade definida.', NEW.salaid;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_verificar_capacidade_sala
BEFORE INSERT ON sessoes
FOR EACH ROW
EXECUTE FUNCTION trg_verificar_capacidade_sala();


/*==============================================================
    9 - Criar lugares globais por sala                        
    mediante o numero de filas e colunas cria a mtriz de lugares
/*==============================================================*/
CREATE OR REPLACE FUNCTION gerar_lugares_automatica()
RETURNS TRIGGER AS $$
DECLARE
    fila_idx INT;
    col_idx INT;
    fila CHAR(1);
BEGIN
    FOR fila_idx IN 1..NEW.filas LOOP
        -- Truque ASCII para transformar numeros em letras (1=A, 2=B)
        fila := CHR(ASCII('A') + fila_idx - 1);

        FOR col_idx IN 1..NEW.colunas LOOP
            INSERT INTO lugares (salaid, fila, numero, tipolugar)
            VALUES (NEW.salaid, fila, col_idx, 'STANDARD');
        END LOOP;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_gerar_lugares_automatica
AFTER INSERT ON salas
FOR EACH ROW
EXECUTE FUNCTION gerar_lugares_automatica();


/*==============================================================*/
/* 10 - Atualizar capacidade da sala                            */
/* Conta quantos lugares criamos e diz a sala qual a sua        */
/* capacidade real. Mantem tudo sincronizado.                   */
/*==============================================================*/
CREATE OR REPLACE FUNCTION atualizar_capacidade_sala()
RETURNS TRIGGER AS $$
DECLARE
    total INT;
BEGIN
    SELECT COUNT(*) INTO total
    FROM lugares
    WHERE salaid = NEW.salaid;

    UPDATE salas
    SET capacidade = total
    WHERE salaid = NEW.salaid;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_atualizar_capacidade_sala
AFTER INSERT ON lugares
FOR EACH ROW
EXECUTE FUNCTION atualizar_capacidade_sala();


/*==============================================================
    11 - Copiar lugares para a sessao (estado LIVRE)             
    Isto prepara a sala para o filme. Copia o mapa da sala 
    para os lugares a sessao com o estado LIVRE 
/*==============================================================*/
CREATE OR REPLACE FUNCTION gerar_lugares_sessao()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO lugaresSessao (sessaoid, lugarid, estado)
    SELECT NEW.sessaoid, lugarid, 'LIVRE'
    FROM lugares
    WHERE salaid = NEW.salaid;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_gerar_lugares_sessao
AFTER INSERT ON sessoes
FOR EACH ROW
EXECUTE FUNCTION gerar_lugares_sessao();


/*==============================================================
    12 - Verificar se o lugar da sessao esta LIVRE               
    So deixa vender o bilhete se a cadeira estiver vazia
==============================================================*/
CREATE OR REPLACE FUNCTION trg_verificar_lugar_disponivel()
RETURNS TRIGGER AS $$
DECLARE
    estado_atual VARCHAR(20);
BEGIN
    SELECT estado INTO estado_atual
    FROM lugaresSessao
    WHERE lugarSessaoid = NEW.lugarid;

    IF estado_atual <> 'LIVRE' THEN
        RAISE EXCEPTION 'Lugar da sessão % não está livre.', NEW.lugarid;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_verificar_lugar_disponivel
BEFORE INSERT ON bilhetes
FOR EACH ROW
EXECUTE FUNCTION trg_verificar_lugar_disponivel();


/*==============================================================
    13 - Ocupa o lugar ao emitir bilhete                         
==============================================================*/
CREATE OR REPLACE FUNCTION trg_ocupar_lugar_apos_bilhete()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE lugaresSessao
    SET estado = 'OCUPADO'
    WHERE lugarSessaoid = NEW.lugarid;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_ocupar_lugar_apos_bilhete
AFTER INSERT ON bilhetes
FOR EACH ROW
EXECUTE FUNCTION trg_ocupar_lugar_apos_bilhete();


/*==============================================================
    14 - Liberta o lugar ao eliminar bilhete                     
/*==============================================================*/
CREATE OR REPLACE FUNCTION trg_libertar_lugar_apos_cancelamento_bilhete()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE lugaresSessao
    SET estado = 'LIVRE'
    WHERE lugarSessaoid = OLD.lugarid;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_libertar_lugar_apos_cancelamento_bilhete
AFTER DELETE ON bilhetes
FOR EACH ROW
EXECUTE FUNCTION trg_libertar_lugar_apos_cancelamento_bilhete();


/*==============================================================
    15 - Impedir bilhetes em sessoes terminadas ou nao ativas    
/*==============================================================*/
CREATE OR REPLACE FUNCTION trg_impedir_bilhete_para_sessao_terminada()
RETURNS TRIGGER AS $$
DECLARE
    estado VARCHAR(20);
    fim_s TIMESTAMP;
BEGIN
    SELECT estadosessao, fim INTO estado, fim_s
    FROM sessoes
    WHERE sessaoid = NEW.sessaoid;

    IF estado <> 'Ativa' OR fim_s < NOW() THEN
        RAISE EXCEPTION 'Sessão % não está ativa ou já terminou.', NEW.sessaoid;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_impedir_bilhete_para_sessao_terminada
BEFORE INSERT ON bilhetes
FOR EACH ROW
EXECUTE FUNCTION trg_impedir_bilhete_para_sessao_terminada();


/*==============================================================
    16 - Verificar idade minima para comprar bilhete             
    Mediante a data de nascimento verifica se encaixa na classificação do filme
/*==============================================================*/
CREATE OR REPLACE FUNCTION trg_verificar_idade_para_filme()
RETURNS TRIGGER AS $$
DECLARE
    data_nasc DATE;
    idade INT;
    classificacao CHAR(8);
    idade_min INT;
BEGIN
    -- Buscar data nascimento do cliente da venda
    SELECT c.datanascimento INTO data_nasc
    FROM clientes c
    JOIN vendas v ON v.vendaid = NEW.vendaid
    WHERE c.clienteid = v.clienteid;

    -- Calcula a idade real
    SELECT EXTRACT(YEAR FROM AGE(CURRENT_DATE, data_nasc))::INT INTO idade;

    -- Vai ver a classificacao etaria do filme deste bilhete
    SELECT ce.nomeclassificacao INTO classificacao
    FROM bilhetes b
    JOIN sessoes s ON s.sessaoid = b.sessaoid
    JOIN filmes f ON f.filmeid = s.filmeid
    JOIN classificacoesetarias ce ON ce.classificacaoid = f.classificacaoetaria
    WHERE b.bilheteid = NEW.bilheteid;

    -- Converte o texto M/16 em numero 16 para podermos comparar
    CASE classificacao
        WHEN 'M/6' THEN idade_min := 6;
        WHEN 'M/12' THEN idade_min := 12;
        WHEN 'M/16' THEN idade_min := 16;
        WHEN 'M/18' THEN idade_min := 18;
        ELSE idade_min := 0;
    END CASE;

    IF idade < idade_min THEN
        RAISE EXCEPTION 'Cliente tem % anos e não cumpre classificação %.', idade, classificacao;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_verificar_idade_para_filme
BEFORE INSERT ON vendalinhas
FOR EACH ROW
EXECUTE FUNCTION trg_verificar_idade_para_filme();