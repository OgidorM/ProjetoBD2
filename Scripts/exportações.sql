CREATE OR REPLACE FUNCTION exportar_fatura_pdf(p_venda_id INT)
RETURNS JSONB
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    RETURN (
        -- row_to_json: transforma a linha resultante num objeto JSON unico
        SELECT row_to_json(fatura_obj)
        FROM (
            SELECT 
                v.VENDAID AS "id_fatura",
                v.DATA AS "data_emissao",
                v.TOTALVENDA AS "total_pagar",
                v.ESTADOVENDA AS "estado",
                
                -- COALESCE: quando algum destes é NULL, fica com Consumidor Final e/ou 999999990
                COALESCE(c.NOMECLIENTE, 'Consumidor Final') AS "cliente_nome",
                COALESCE(c.NIF, '999999990') AS "cliente_nif",
                
                func.NOMEFUNCIONARIO AS "atendido_por",
                cin.NOMECINEMA AS "cinema_local",
                
                -- SUBQUERY DE ITENS
                -- Aqui é criada um array de produtos/bilhetes dentro do objeto fatura criado em cima
                (
                    SELECT json_agg(row_to_json(itens_lista))
                    FROM (
                        SELECT 
                            vl.QUANTIDADE AS "qtd",
                            vl.PRECOLINHA AS "preco_unit",
                            vl.TOTAL_LINHA_ AS "total_linha",
                            
                            -- CASE: Lógica condicional para o nome.
                            -- Verifica se é id de produto, senão é um bilhete
                            CASE 
                                WHEN vl.PRODUTOID IS NOT NULL THEN p.NOMEPRODUTO
                                ELSE CONCAT('Bilhete - ', f.TITULO) -- junta a string Bilhete com o Titulo
                            END AS "descricao"
                            
                        FROM VENDALINHAS vl
                        -- LEFT JOINS: porque a linha pode ser produto ou bilhete (entao um deles vai ser null)
                        LEFT JOIN PRODUTOS p ON vl.PRODUTOID = p.PRODUTOID
                        LEFT JOIN BILHETES b ON vl.BILHETEID = b.BILHETEID
                        LEFT JOIN SESSOES s ON b.SESSAOID = s.SESSAOID
                        LEFT JOIN FILMES f ON s.FILMEID = f.FILMEID
                        
                        -- garante que só usamos as linhas da venda específica (no parametro de entrada)
                        WHERE vl.VENDAID = v.VENDAID
                    ) itens_lista
                ) AS "itens_compra"

            FROM VENDAS v
            JOIN FUNCIONARIOS func ON v.FUNCIONARIOID = func.FUNCIONARIOID
            JOIN CINEMAS cin ON func.CINEMAID = cin.CINEMAID
            LEFT JOIN CLIENTES c ON v.CLIENTEID = c.CLIENTEID
            WHERE v.VENDAID = p_venda_id -- Filtra apenas a fatura pedida
        ) fatura_obj
    );
END;
$BODY$;


CREATE OR REPLACE FUNCTION exportar_faturas_por_data(p_data DATE DEFAULT CURRENT_DATE)
RETURNS JSONB
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    RETURN (
        -- json_agg: como sao esperadas várias faturas aqui é agrupado tudo numa lista principal
        SELECT json_agg(row_to_json(lista_faturas))
        FROM (
            SELECT 
                v.VENDAID AS "id_fatura",
                v.DATA AS "data_emissao",
                v.TOTALVENDA AS "total",
                v.ESTADOVENDA AS "estado",
                
                -- Se o cliente for null, aparece Consumidor Final para nao ficar vazio
                COALESCE(c.NOMECLIENTE, 'Consumidor Final') AS "cliente",
                func.NOMEFUNCIONARIO AS "vendedor",
                
                -- SUBQUERY agrupada (cilco para os itens)
                -- Para cada venda encontrada no loop principal, corremos isto para ir buscar os seus itens
                (
                    SELECT json_agg(row_to_json(itens_obj))
                    FROM (
                        SELECT 
                            vl.QUANTIDADE AS "qtd",
                            vl.TOTAL_LINHA_ AS "total_linha",
                            
                            -- Decide se mostramos o nome do produto ou do filme
                            CASE 
                                WHEN vl.PRODUTOID IS NOT NULL THEN p.NOMEPRODUTO
                                ELSE CONCAT('Bilhete: ', f.TITULO)
                            END AS "descricao"
                            
                        FROM VENDALINHAS vl
                        LEFT JOIN PRODUTOS p ON vl.PRODUTOID = p.PRODUTOID
                        LEFT JOIN BILHETES b ON vl.BILHETEID = b.BILHETEID
                        LEFT JOIN SESSOES s ON b.SESSAOID = s.SESSAOID
                        LEFT JOIN FILMES f ON s.FILMEID = f.FILMEID
                        
                        -- isto conecta a linha do produto a venda atual do loop principal
                        WHERE vl.VENDAID = v.VENDAID 
                    ) itens_obj
                ) AS "itens_compra"

            FROM VENDAS v
            JOIN FUNCIONARIOS func ON v.FUNCIONARIOID = func.FUNCIONARIOID
            LEFT JOIN CLIENTES c ON v.CLIENTEID = c.CLIENTEID
            -- filtro principal: so queremos as vendas do dia que passamos na funcao
            WHERE v.DATA = p_data 
        ) lista_faturas
    );
END;
$BODY$;


CREATE OR REPLACE FUNCTION exportar_bilhete_pdf(p_bilhete_id INT)
RETURNS JSONB
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    RETURN (
        -- row_to_json: so queremos um objeto simples com os dados deste bilhete
        SELECT row_to_json(dados_bilhete)
        FROM (
            SELECT 
                b.BILHETEID AS "id_bilhete",
                b.PRECOBILHETE AS "preco",
                f.TITULO AS "filme",
                f.DURACAO || ' min' AS "duracao", -- add min a frente do numero
                f.CLASSIFICACAOETARIA AS "classificacao_etaria", 
                
                -- TO_CHAR: formata as datas e horas para ficarem naquele formato dps no pdf
                TO_CHAR(s.INICIO, 'DD/MM/YYYY') AS "data_sessao",
                TO_CHAR(s.INICIO, 'HH24:MI') AS "hora_sessao",
                
                sa.NOMESALA AS "sala",
                c.NOMECINEMA AS "cinema",
                
                -- dados do Lugar
                l.FILA AS "fila",
                l.NUMERO AS "cadeira",
                
                b.EMISSAO AS "data_compra"
            FROM BILHETES b
            -- joins para chegar ao nome da sala, do cinema e do filme
            -- comecamos no bilhete, vai a sessao, depois filme, sala, cinema e lugar
            JOIN SESSOES s ON b.SESSAOID = s.SESSAOID
            JOIN FILMES f ON s.FILMEID = f.FILMEID
            JOIN SALAS sa ON s.SALAID = sa.SALAID
            JOIN CINEMAS c ON sa.CINEMAID = c.CINEMAID
            JOIN LUGARESSESSAO ls ON b.LUGARID = ls.LUGARSESSAOID
            JOIN LUGARES l ON ls.LUGARID = l.LUGARID
            
            -- So queremos os dados deste bilhete especifico
            WHERE b.BILHETEID = p_bilhete_id
        ) dados_bilhete
    );
END;
$BODY$;