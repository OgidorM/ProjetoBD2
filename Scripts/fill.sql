-- Categorias
INSERT INTO categorias (nomecategoria) VALUES
('Ação'),('Comédia'),('Drama'),('Ficção Científica'),('Terror'),
('Romance'),('Aventura'),('Animação'),('Documentário'),('Suspense');

-- Cinemas
INSERT INTO cinemas (nomecinema,emailcinema,telefonecinema,moradacinema,codigopostalcinema,localidadecinema,ranking) VALUES
('Cinema City Porto','info@cinemacity.pt','220123456','Rua de Santa Catarina, 312','4000-447','Porto',0),
('NOS Colombo','colombo@nos.pt','217890123','Av. Lusíada, Centro Colombo','1500-392','Lisboa',0),
('UCI Gaia Shopping','gaia@uci.pt','223456789','Av. dos Descobrimentos, 549','4400-119','Vila Nova de Gaia',0),
('Cinemas Nos Forum Coimbra','coimbra@nos.pt','239876543','Rua do Brasil, 1','3030-175','Coimbra',0);

-- Classificações Etárias
INSERT INTO classificacoesetarias (nomeclassificacao) VALUES
('LIVRE'),('M/6'),('M/12'),('M/16'),('M/18');

-- Salas
INSERT INTO salas (cinemaid, nomesala, filas, colunas, tiposala) VALUES
(1, 'Sala 1', 10, 20, 'Standard'),
(1, 'Sala 2', 8, 15, 'Standard'),
(1, 'Sala 3', 9, 18, 'IMAX'),
(2, 'Sala A', 12, 25, 'Standard'),
(2, 'Sala B', 8, 15, 'Standard'),
(2, 'Sala C', 10, 30, 'IMAX'),
(3, 'Sala Premium', 6, 12, 'IMAX'),
(3, 'Sala Grande', 14, 20, 'Standard'),
(4, 'Sala Central', 9, 18, 'Standard'),
(4, 'Sala Digital', 7, 16, 'Standard');

-- Filmes
INSERT INTO filmes (categoriaid,cinemaid,titulo,datalancamento,duracao,produtora,fimexebicao,idioma,sinopse,classificacaoetaria,ranking) VALUES
(1,1,'Velozes e Furiosos 11','2025-05-15',140,'Universal Pictures','2026-03-31','PT','A família de Dominic Toretto enfrenta uma nova ameaça global.',3,0),
(2,1,'Super Mario Bros. O Filme','2025-04-10',92,'Nintendo/Illumination','2026-03-31','PT','Mario e Luigi embarcam numa aventura no Reino dos Cogumelos.',2,0),
(3,2,'Oppenheimer','2025-07-20',180,'Universal Pictures','2026-03-31','PT','A história do físico J. Robert Oppenheimer e a bomba atômica.',3,0),
(4,2,'Dune: Parte Dois','2025-03-01',166,'Warner Bros','2026-03-31','PT','Paul Atreides une-se aos Fremen numa guerra pela especiaria.',3,0),
(5,3,'Scream VI','2025-06-09',123,'Paramount Pictures','2026-03-31','PT','Ghostface regressa para aterrorizar uma nova geração.',4,0),
(6,3,'Titanic Re-Release','2025-02-14',195,'Paramount Pictures','2026-03-31','PT','O épico romance entre Jack e Rose no navio condenado.',3,0),
(7,4,'Indiana Jones 5','2025-06-30',154,'Lucasfilm','2026-03-31','PT','A última aventura do arqueólogo mais famoso do cinema.',3,0),
(8,4,'Toy Story 5','2025-06-16',100,'Pixar','2026-03-31','PT','Woody, Buzz e os brinquedos voltam numa nova aventura.',2,0);

-- Clientes
INSERT INTO clientes (nomecliente,emailcliente,telefonecliente,datanascimento,moradacliente,codigopostalcliente,localidadecliente,nif) VALUES
('João Silva','joao.silva@email.pt','912345678','1990-05-15','Rua das Flores, 123','4000-123','Porto','123456789'),
('Maria Santos','maria.santos@email.pt','923456789','1985-08-22','Av. da Liberdade, 456','1250-096','Lisboa','234567890'),
('Pedro Costa','pedro.costa@email.pt','934567890','1992-11-03','Rua Central, 789','4400-056','Vila Nova de Gaia','345678901'),
('Ana Oliveira','ana.oliveira@email.pt','945678901','1988-02-14','Praça da República, 12','3000-343','Coimbra','456789012'),
('Carlos Ferreira','carlos.ferreira@email.pt','956789012','1995-07-30','Rua do Comércio, 234','4000-567','Porto','567890123');

-- Funcionários
INSERT INTO funcionarios (cinemaid,nomefuncionario,emailfuncionario,telefonefuncionario,cargo,admissao,salario,ranking) VALUES
(1,'Sofia Pereira','sofia.pereira@cinemacity.pt','967890123','Gerente','2023-01-15',1500.00,0),
(1,'Ricardo Alves','ricardo.alves@cinemacity.pt','978901234','Operador','2023-03-20',800.00,0),
(2,'Luísa Rodrigues','luisa.rodrigues@nos.pt','989012345','Supervisora','2022-11-10',1200.00,0),
(2,'Miguel Teixeira','miguel.teixeira@nos.pt','990123456','Operador','2024-02-01',780.00,0),
(3,'Carla Mendes','carla.mendes@uci.pt','901234567','Gerente','2023-06-15',1400.00,0),
(4,'Bruno Gonçalves','bruno.goncalves@nos.pt','912345670','Operador','2024-01-10',790.00,0);

-- Produtos
INSERT INTO produtos (nomeproduto, precoproduto, stock, ativo) VALUES
('Pipocas Grandes', 6.50, 100, true),
('Pipocas Médias', 5.00, 150, true),
('Pipocas Pequenas', 3.50, 200, true),
('Coca-Cola 500ml', 4.00, 120, true),
('Água 500ml', 2.50, 80, true),
('Nachos com Queijo', 7.00, 60, true),
('M&Ms', 3.00, 90, true),
('Chocolate Branco 100g', 3.50, 90, true),
('Hot Dog', 5.50, 40, true),
('Ice Tea', 3.50, 70, true);

-- Lugares (simplificado)
--Criados automaticamente com a sala

-- Sessoes
INSERT INTO sessoes (salaid, filmeid, inicio, fim, versao, estadosessao, precosessao) VALUES
(1, 2, '2025-12-10 18:00:00', '2025-12-10 19:32:00', 'PT', 'Ativa', 7.50),
(2, 3, '2025-12-25 21:00:00', '2025-12-25 23:55:00', 'EN', 'Ativa', 10.50),
(3, 4, '2025-11-08 20:00:00', '2025-11-08 22:46:00', 'PT', 'Ativa', 11.00),
(4, 5, '2025-11-22 22:00:00', '2025-11-23 00:03:00', 'PT', 'Ativa', 9.00),
(5, 6, '2025-12-12 19:00:00', '2025-12-12 22:15:00', 'EN', 'Ativa', 12.00),
(6, 7, '2025-12-28 21:00:00', '2025-12-28 23:34:00', 'PT', 'Ativa', 9.50),
(1, 8, '2026-01-10 16:00:00', '2026-01-10 17:40:00', 'PT', 'Ativa', 8.00);

-- Vendas
INSERT INTO vendas (clienteid,funcionarioid,data,estadovenda,totalvenda) VALUES
(1,1,'2025-09-23','Concluída',29.50),
(2,2,'2025-09-23','Concluída',16.00),
(3,3,'2025-09-23','Concluída',50.00),
(3,2,'2025-09-26','Concluída',51.00),
(2,1,'2025-10-26','Em curso',2.00);

-- Bilhetes (agora ligados logicamente a vendas)
INSERT INTO bilhetes (lugarid,sessaoid,precobilhete,EMISSAO) VALUES
(1,1,9.50,'2025-09-23 12:30:00'),
(2,2,10.50,'2025-09-23 14:00:00');

-- VendaLinhas (com lógica produto OU bilhete)
INSERT INTO vendalinhas (vendaid,produtoid,quantidade,total_linha_,precolinha) VALUES
(1,1,1,6.50,6.50),
(1,4,1,4.00,4.00),
(2,2,1,5.00,5.00),
(2,5,1,2.50,2.50);

INSERT INTO vendalinhas (vendaid,bilheteid,quantidade,total_linha_,precolinha) VALUES
(1,1,1,9.50,9.50),
(2,2,1,10.50,10.50);

-- Avaliações
INSERT INTO avaliacoes (vendaid,tituloavaliacao,avaliacaocinema,avaliacaofilme,avaliacaofuncionario,comentario) VALUES
(1,'Ótima Experiência',5,5,5,'Cinema confortável e bom atendimento.'),
(2,'Filme Muito Bom',4,5,5,'A qualidade da imagem foi excelente.'),
(3,'Som Poderia Melhorar',3,4,4,'Achei o som um pouco baixo.');