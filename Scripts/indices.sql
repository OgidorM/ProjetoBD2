-- ==============================================================
-- INDICES PARA VISTAS RELACIONADAS COM SESSÕES E LUGARES
-- ==============================================================

CREATE INDEX idx_sessoes_filmeid ON sessoes(filmeid);
CREATE INDEX idx_sessoes_salaid ON sessoes(salaid);

CREATE INDEX idx_lugares_salaid ON lugares(salaid);

CREATE INDEX idx_lugaresSessao_sessaoid ON lugaresSessao(sessaoid);
CREATE INDEX idx_lugaresSessao_lugarid ON lugaresSessao(lugarid);

-- ==============================================================
-- INDICES PARA PRODUTOS, VENDAS E AVALIAÇÕES
-- ==============================================================

CREATE INDEX idx_vl_produtoid ON vendalinhas(produtoid);
CREATE INDEX idx_vl_vendaid ON vendalinhas(vendaid);
CREATE INDEX idx_vl_bilheteid ON vendalinhas(bilheteid);
CREATE INDEX idx_avaliacoes_vendaid ON avaliacoes(vendaid);

-- ==============================================================
-- INDICES PARA FUNCIONÁRIOS E CLIENT4ES
-- ==============================================================
CREATE INDEX idx_vendas_funcionarioid ON vendas(funcionarioid);
CREATE INDEX idx_funcionarios_cinemaid ON funcionarios(cinemaid);
CREATE INDEX idx_funcionarios_email ON funcionarios(emailfuncionario);
CREATE INDEX idx_funcionarios_cargo ON funcionarios(cargo);

CREATE INDEX idx_vendas_clienteid ON vendas(clienteid);
CREATE UNIQUE INDEX idx_clientes_email ON clientes(emailcliente);
CREATE INDEX idx_clientes_telefone ON clientes(telefonecliente);
CREATE INDEX idx_clientes_nif ON clientes(nif);
CREATE INDEX idx_clientes_localidade ON clientes(localidadecliente);
CREATE INDEX idx_clientes_codigopostal ON clientes(codigopostalcliente);

-- ==============================================================
-- INDICES PARA FILMES
-- ==============================================================
CREATE INDEX idx_filmes_categoriaid ON filmes(categoriaid);
CREATE INDEX idx_filmes_cinemaid ON filmes(cinemaid);
