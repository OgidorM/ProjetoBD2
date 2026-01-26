-- ==============================================================
-- Vista simples: Mostra lugares livres e totais por sessão para cada filme
-- ==============================================================
CREATE OR REPLACE VIEW v_sessoes_lugares_livres_por_filme AS
SELECT
    f.filmeid,
    f.titulo AS filme,
    s.sessaoid,
    s.inicio,
    s.fim,
    sa.nomesala,
    c.nomecinema,
    COUNT(ls.lugarsessaoid) FILTER (WHERE ls.estado = 'Livre') AS lugares_livres,
    COUNT(ls.lugarsessaoid) AS lugares_totais
FROM filmes f
JOIN sessoes s ON s.filmeid = f.filmeid
JOIN salas sa ON sa.salaid = s.salaid
JOIN cinemas c ON c.cinemaid = sa.cinemaid
JOIN lugares l ON l.salaid = sa.salaid
JOIN lugaresSessao ls ON ls.lugarid = l.lugarid AND ls.sessaoid = s.sessaoid
GROUP BY f.filmeid, f.titulo, s.sessaoid, s.inicio, s.fim, sa.nomesala, c.nomecinema
ORDER BY f.titulo, s.inicio;

-- ==============================================================
-- Vista simples: Filmes por categoria com sessões futuras associadas
-- ==============================================================
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
LEFT JOIN sessoes s 
       ON s.filmeid = f.filmeid
      AND s.inicio > NOW()
      AND s.estadosessao = 'Ativa'
ORDER BY cat.nomecategoria, f.titulo, s.inicio;

-- ==============================================================
-- Vista simples: Mostra médias de avaliação e total de avaliações por filme
-- ==============================================================
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

-- ==============================================================
-- Vista simples: Quantidade vendida e faturação total por produto
-- ==============================================================
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

-- ==============================================================
-- Vista simples: Resumo por cinema – salas, filmes, vendas e faturação
-- ==============================================================
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

-- ==============================================================
-- Vista simples: Mostra todos os lugares livres por sessão
-- ==============================================================
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
JOIN lugaresSessao ls ON ls.lugarid = l.lugarid AND ls.sessaoid = s.sessaoid
WHERE ls.estado = 'Livre'
ORDER BY s.sessaoid, l.fila, l.numero;

-- ==============================================================
-- Vista materializada: Ranking de funcionários com vendas e avaliações
-- ==============================================================
DROP MATERIALIZED VIEW IF EXISTS mv_funcionarios_top;
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_funcionarios_top AS
SELECT
    f.funcionarioid,
    f.nomefuncionario,
    f.cargo,
    f.salario,
    c.nomecinema,
    ROUND(AVG(a.avaliacaofuncionario)::NUMERIC, 2) AS media_avaliacao,
    COUNT(v.vendaid) AS total_vendas,
    COALESCE(SUM(v.totalvenda), 0) AS total_faturado
FROM funcionarios f
JOIN cinemas c ON c.cinemaid = f.cinemaid
LEFT JOIN vendas v ON v.funcionarioid = f.funcionarioid
LEFT JOIN avaliacoes a ON a.vendaid = v.vendaid
GROUP BY f.funcionarioid, f.nomefuncionario, f.cargo, f.salario, c.nomecinema
ORDER BY media_avaliacao DESC, total_faturado DESC;
REFRESH MATERIALIZED VIEW mv_funcionarios_top;

-- ==============================================================
-- Vista materializada: Ocupação total das salas por sessão
-- ==============================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ocupacao_salas AS
SELECT
    s.salaid,
    sa.nomesala,
    s.sessaoid,
    COUNT(ls.lugarSessaoid) AS total_lugares,
    COUNT(ls.lugarSessaoid) FILTER (WHERE ls.estado = 'Ocupado') AS lugares_ocupados,
    COUNT(ls.lugarSessaoid) FILTER (WHERE ls.estado = 'Livre') AS lugares_livres
FROM sessoes s
JOIN salas sa ON sa.salaid = s.salaid
JOIN lugares l ON l.salaid = sa.salaid
JOIN lugaresSessao ls ON ls.lugarid = l.lugarid AND ls.sessaoid = s.sessaoid
GROUP BY s.sessaoid, s.salaid, sa.nomesala
ORDER BY sa.nomesala, s.sessaoid;
REFRESH MATERIALIZED VIEW mv_ocupacao_salas;

-- ==============================================================
-- Vista simples: Filmes em exibição atualmente
-- ==============================================================
CREATE OR REPLACE VIEW v_filmes_em_exibicao AS
SELECT
    f.filmeid,
    f.titulo,
    f.fimexebicao,
    f.datalancamento,
    c.nomecinema
FROM filmes f
LEFT JOIN cinemas c ON c.cinemaid = f.cinemaid
WHERE (f.fimexebicao >= CURRENT_DATE OR f.fimexebicao IS NULL)
ORDER BY f.titulo;

-- ==============================================================
-- Vista materializada: Total de vendas por dia
-- ==============================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_vendas_diarias AS
SELECT
    data,
    COUNT(vendaid) AS total_transacoes,
    SUM(totalvenda) AS total_faturado
FROM vendas
GROUP BY data
ORDER BY data;
REFRESH MATERIALIZED VIEW mv_vendas_diarias;

-- ==============================================================
-- Vista Materializada: Histórico de compras por cliente
-- Mostra total gasto, num de compras e datas da primeira/ultima compra
-- ==============================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_historico_clientes AS
SELECT
    c.clienteid,
    c.nomecliente,
    c.emailcliente,
    c.localidadecliente,
    c.codigopostalcliente,
    COUNT(v.vendaid) AS total_compras,
    COALESCE(SUM(v.totalvenda), 0) AS total_gasto,
    COALESCE(ROUND(AVG(v.totalvenda)::NUMERIC, 2), 0) AS media_por_compra,
    MIN(v.data) AS primeira_compra,
    MAX(v.data) AS ultima_compra
FROM clientes c
LEFT JOIN vendas v ON v.clienteid = c.clienteid
GROUP BY
    c.clienteid,
    c.nomecliente,
    c.emailcliente,
    c.localidadecliente,
    c.codigopostalcliente
ORDER BY total_gasto DESC;
REFRESH MATERIALIZED VIEW mv_historico_clientes;

-- ==============================================================
-- Vista simples: Avaliações por cliente
-- ==============================================================
CREATE OR REPLACE VIEW v_avaliacoes_cliente AS
SELECT 
    a.avaliacaoid,
    a.vendaid,
    c.nomecliente AS cliente_nome,
    c.emailcliente AS cliente_email,
    a.tituloavaliacao,
    a.avaliacaocinema,
    a.avaliacaofilme,
    a.avaliacaofuncionario,
    a.comentario
FROM avaliacoes a
JOIN vendas v ON a.vendaid = v.vendaid
JOIN clientes c ON v.clienteid = c.clienteid
ORDER BY a.avaliacaoid DESC;

-- ==============================================================
-- Vista simples: Lista Global de Clientes
-- ==============================================================
CREATE OR REPLACE VIEW v_clientes_global AS
SELECT 
    clienteid,
    nomecliente,
    emailcliente,
    telefonecliente,
    nif,
    localidadecliente
FROM clientes
ORDER BY nomecliente;

-- ==============================================================
-- Vista simples: Mostra apenas os lugares ocupados e detalhes
-- ==============================================================
CREATE OR REPLACE VIEW v_lugares_sessao_detalhado AS
SELECT
    ls.sessaoid,
    ls.lugarsessaoid,
    ls.estado,
    l.lugarid,
    l.fila,
    l.numero,
    l.tipolugar
FROM lugaresSessao ls
JOIN lugares l ON l.lugarid = ls.lugarid
ORDER BY ls.sessaoid, l.fila, l.numero;

-- ==============================================================
-- Vista simples: Mostra apenas os produtos ativos e disponíveis
-- ==============================================================
CREATE OR REPLACE VIEW v_produtos_disponiveis AS
SELECT 
    produtoid,
    nomeproduto,
    precoproduto,
    stock,
    ativo
FROM produtos
WHERE 
    ativo = true 
    AND stock > 0
ORDER BY nomeproduto ASC;

-- ==============================================================
-- Vista simples: Mostra apenas as vendas e o ID do Django
-- ==============================================================
CREATE OR REPLACE VIEW v_vendas_users AS
SELECT 
    v.vendaid,
    v.clienteid,
    au.id AS user_id 
FROM vendas v
JOIN clientes c ON v.clienteid = c.clienteid
JOIN auth_user au ON au.username = c.nomecliente;
