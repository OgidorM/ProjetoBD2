--1-----------------------------------------------------------------------------------------------
--Lugares livres de cada sessão por filme
CREATE OR REPLACE VIEW v_sessoes_lugares_livres_por_filme AS
SELECT
    f.filmeid,
    f.titulo AS filme,
    s.sessaoid,
    s.inicio,
    s.fim,
    sa.nomesala,
    c.nomecinema,
    COUNT(l.lugarid) FILTER (
        WHERE l.estadolugar = 'Disponível'
          AND b.bilheteid IS NULL
    ) AS lugares_livres,
    COUNT(l.lugarid) AS lugares_totais
FROM filmes f
JOIN sessoes s ON s.filmeid = f.filmeid
JOIN salas sa ON sa.salaid = s.salaid
JOIN cinemas c ON c.cinemaid = sa.cinemaid
JOIN lugares l ON l.salaid = sa.salaid
LEFT JOIN bilhetes b ON b.lugarid = l.lugarid AND b.sessaoid = s.sessaoid
GROUP BY f.filmeid, f.titulo, s.sessaoid, s.inicio, s.fim, sa.nomesala, c.nomecinema
ORDER BY f.titulo, s.inicio;

-----------------------------------------------------
--Todos os filmes por categoria mostrando as suas sessões futuras
CREATE OR REPLACE VIEW v_filmes_por_categoria_com_sessao AS
SELECT
    cat.categoriaid,
    cat.nomecategoria AS categoria,
    f.filmeid,
    COALESCE(f.titulo, 'N/A') AS titulo,
    COALESCE(f.duracao::TEXT, 'N/A') AS duracao,
    COALESCE(f.idioma, 'N/A') AS idioma,
    COALESCE(TO_CHAR(f.datalancamento, 'YYYY-MM-DD'), 'N/A') AS datalancamento,
    COALESCE(TO_CHAR(f.fimexebicao, 'YYYY-MM-DD'), 'N/A') AS fimexebicao,
    COALESCE(f.ranking::TEXT, 'N/A') AS ranking,
    s.sessaoid,
    TO_CHAR(s.inicio, 'YYYY-MM-DD HH24:MI') AS inicio_sessao,
    TO_CHAR(s.fim, 'YYYY-MM-DD HH24:MI') AS fim_sessao,
    s.precosessao
FROM categorias cat
LEFT JOIN filmes f ON f.categoriaid = cat.categoriaid
LEFT JOIN sessoes s ON s.filmeid = f.filmeid
                  AND s.inicio > NOW()
                  AND s.estadosessao = 'Ativa'
ORDER BY cat.nomecategoria, f.titulo, s.inicio;

--2-----------------------------------------------------------------------------------------------
--Mostra cada filme com a média das avaliações, número total de avaliações
CREATE OR REPLACE VIEW v_avaliacoes_por_filme AS
SELECT
    f.filmeid,
    f.titulo,
    COUNT(a.avaliacaoid) AS total_avaliacoes,
    ROUND(AVG(a.avaliacaofilme)::NUMERIC, 2) AS media_avaliacao_filme,
    ROUND(AVG(a.avaliacaocinema)::NUMERIC, 2) AS media_avaliacao_cinema,
    ROUND(AVG(a.avaliacaofuncionario)::NUMERIC, 2) AS media_avaliacao_funcionario
FROM filmes f
LEFT JOIN sessoes s ON s.filmeid = f.filmeid
LEFT JOIN bilhetes b ON b.sessaoid = s.sessaoid
LEFT JOIN vendalinhas vl ON vl.bilheteid = b.bilheteid
LEFT JOIN vendas v ON v.vendaid = vl.vendaid
LEFT JOIN avaliacoes a ON a.vendaid = v.vendaid
GROUP BY f.filmeid, f.titulo
ORDER BY f.titulo;

-----------------------------------------------------
--Mostra por produto a quantidade vendida e a faturação 
CREATE OR REPLACE VIEW v_produtos_vendidos AS
SELECT
    p.produtoid,
    p.nomeproduto,
    SUM(vl.quantidade) AS total_quantidade_vendida,
    COALESCE(SUM(vl.total_linha_), 0) AS total_faturado
FROM produtos p
LEFT JOIN vendalinhas vl ON vl.produtoid = p.produtoid
GROUP BY p.produtoid, p.nomeproduto
ORDER BY total_faturado DESC;

--3-----------------------------------------------------------------------------------------------
--Por cinema as suas salas, filmes, bilhetes vendidos e faturação
CREATE OR REPLACE VIEW v_cinemas_resumo AS
SELECT
    c.cinemaid,
    c.nomecinema,
    COUNT(DISTINCT sa.salaid) AS total_salas,
    COUNT(DISTINCT f.filmeid) AS total_filmes,
    COUNT(DISTINCT v.vendaid) AS total_vendas,    
	COUNT(DISTINCT b.bilheteid) AS total_bilhetes,              
    COALESCE(SUM(v.totalvenda), 0) AS total_faturado  
FROM cinemas c
LEFT JOIN salas sa ON sa.cinemaid = c.cinemaid
LEFT JOIN filmes f ON f.cinemaid = c.cinemaid
LEFT JOIN funcionarios fu ON fu.cinemaid = c.cinemaid
LEFT JOIN vendas v ON v.funcionarioid = fu.funcionarioid
LEFT JOIN vendalinhas vl ON vl.vendaid = v.vendaid AND vl.bilheteid IS NOT NULL
LEFT JOIN bilhetes b ON b.bilheteid = vl.bilheteid
GROUP BY c.cinemaid, c.nomecinema
ORDER BY total_faturado DESC;

select * from v_cinemas_resumo

-----------------------------------------------------
--Funcionários ordenados pelo ranking médio de avaliações e faturação total
CREATE OR REPLACE VIEW v_funcionarios_top AS
SELECT
    f.funcionarioid,
    f.nomefuncionario,
    f.cargo,
    c.nomecinema,
    ROUND(AVG(a.avaliacaofuncionario)::NUMERIC, 2) AS media_avaliacao,
    COUNT(v.vendaid) AS total_vendas,
    COALESCE(SUM(v.totalvenda), 0) AS total_faturado
FROM funcionarios f
JOIN cinemas c ON c.cinemaid = f.cinemaid
LEFT JOIN vendas v ON v.funcionarioid = f.funcionarioid
LEFT JOIN avaliacoes a ON a.vendaid = v.vendaid
GROUP BY f.funcionarioid, f.nomefuncionario, f.cargo, c.nomecinema
ORDER BY media_avaliacao DESC, total_faturado DESC;


--4-----------------------------------------------------------------------------------------------
--Lista de lugares livres numa sessão
CREATE OR REPLACE VIEW v_sessoes_lugares_livres AS
SELECT
    s.sessaoid,
    f.titulo AS filme,
    sa.nomesala,
    c.nomecinema,
    l.fila,
    l.numero
FROM sessoes s
JOIN filmes f ON f.filmeid = s.filmeid
JOIN salas sa ON sa.salaid = s.salaid
JOIN cinemas c ON c.cinemaid = sa.cinemaid
JOIN lugares l ON l.salaid = sa.salaid
LEFT JOIN bilhetes b ON b.lugarid = l.lugarid AND b.sessaoid = s.sessaoid
WHERE b.bilheteid IS NULL 
  AND l.estadolugar = 'Disponível';

  Select * from v_sessoes_lugares_livres
  
-----------------------------------------------------
--Mostra capacidade, quantos lugares existem e quantos bilhetes já foram emitidos.
CREATE OR REPLACE VIEW v_ocupacao_salas AS
SELECT 
    sa.salaid,
    sa.nomesala,
    sa.capacidade,
    COUNT(l.lugarid) AS total_lugares,
    COUNT(b.bilheteid) AS lugares_ocupados,
    (COUNT(l.lugarid) - COUNT(b.bilheteid)) AS lugares_livres
FROM salas sa
JOIN lugares l ON sa.salaid = l.salaid
LEFT JOIN bilhetes b ON l.lugarid = b.lugarid
GROUP BY sa.salaid, sa.nomesala, sa.capacidade
ORDER BY sa.nomesala;


--views
--Mostra o total faturado por cliente e o número de bilhetes 
CREATE OR REPLACE VIEW v_clientes_resumo AS
SELECT
    cl.clienteid,
    cl.nomecliente,
    COUNT(DISTINCT v.vendaid) AS total_vendas,
    COALESCE(SUM(v.totalvenda), 0) AS total_gasto,
    COUNT(vl.bilheteid) AS total_bilhetes
FROM clientes cl
LEFT JOIN vendas v ON v.clienteid = cl.clienteid
LEFT JOIN vendalinhas vl ON vl.vendaid = v.vendaid AND vl.bilheteid IS NOT NULL
GROUP BY cl.clienteid, cl.nomecliente
ORDER BY total_gasto DESC;



--Mostra a categoria preferida de cada cliente
CREATE OR REPLACE VIEW v_categoria_preferida_por_cliente AS
SELECT
    cl.clienteid,
    cl.nomecliente,
    cat.categoriaid,
    cat.nomecategoria,
    COUNT(b.bilheteid) AS total_bilhetes
FROM clientes cl
JOIN vendas v ON v.clienteid = cl.clienteid
JOIN vendalinhas vl ON vl.vendaid = v.vendaid AND vl.bilheteid IS NOT NULL
JOIN bilhetes b ON b.bilheteid = vl.bilheteid
JOIN sessoes s ON s.sessaoid = b.sessaoid
JOIN filmes f ON f.filmeid = s.filmeid
JOIN categorias cat ON cat.categoriaid = f.categoriaid
GROUP BY cl.clienteid, cl.nomecliente, cat.categoriaid, cat.nomecategoria
HAVING COUNT(b.bilheteid) = (
    SELECT MAX(cnt) 
    FROM (
        SELECT COUNT(b2.bilheteid) AS cnt
        FROM vendas v2
        JOIN vendalinhas vl2 ON vl2.vendaid = v2.vendaid AND vl2.bilheteid IS NOT NULL
        JOIN bilhetes b2 ON b2.bilheteid = vl2.bilheteid
        JOIN sessoes s2 ON s2.sessaoid = b2.sessaoid
        JOIN filmes f2 ON f2.filmeid = s2.filmeid
        WHERE v2.clienteid = cl.clienteid
          AND f2.categoriaid = cat.categoriaid
        GROUP BY f2.categoriaid
    ) sub
)
ORDER BY cl.nomecliente, total_bilhetes DESC;
