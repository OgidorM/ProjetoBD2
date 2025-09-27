/*==============================================================*/
/* DBMS: PostgreSQL 16                                         */
/*==============================================================*/
DROP TABLE IF EXISTS AVALIACOES CASCADE;
DROP TABLE IF EXISTS VENDALINHAS CASCADE;
DROP TABLE IF EXISTS VENDAS CASCADE;
DROP TABLE IF EXISTS BILHETES CASCADE;
DROP TABLE IF EXISTS LUGARES CASCADE;
DROP TABLE IF EXISTS SESSOES CASCADE;
DROP TABLE IF EXISTS SALAS CASCADE;
DROP TABLE IF EXISTS FILMES CASCADE;
DROP TABLE IF EXISTS FUNCIONARIOS CASCADE;
DROP TABLE IF EXISTS CLIENTES CASCADE;
DROP TABLE IF EXISTS PRODUTOS CASCADE;
DROP TABLE IF EXISTS CINEMAS CASCADE;
DROP TABLE IF EXISTS CATEGORIAS CASCADE;
DROP TABLE IF EXISTS CLASSIFICACOESETARIAS CASCADE;


/*==============================================================*/
/* Table: CATEGORIAS                                            */
/*==============================================================*/
CREATE TABLE CATEGORIAS (
   CATEGORIAID    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   NOMECATEGORIA  VARCHAR(80)  NOT NULL
);

/*==============================================================*/
/* Table: CINEMAS                                               */
/*==============================================================*/
CREATE TABLE CINEMAS (
   CINEMAID             INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   NOMECINEMA           VARCHAR(80)   NOT NULL,
   EMAILCINEMA          VARCHAR(254),
   TELEFONECINEMA       VARCHAR(20),
   MORADACINEMA         VARCHAR(120),
   CODIGOPOSTALCINEMA   CHAR(8),
   LOCALIDADECINEMA     VARCHAR(60)   NOT NULL,
   RANKING              NUMERIC(2,1)       DEFAULT 0.0 NOT NULL,
   CONSTRAINT CK_CINEMAS_RANKING CHECK (RANKING >= 0.0 AND RANKING <= 5.0)
);

/*==============================================================*/
/* Table: CLASSIFICACAOETARIA                                               */
/*==============================================================*/
CREATE TABLE CLASSIFICACOESETARIAS (
   CLASSIFICACAOID          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   NOMECLASSIFICACAO        CHAR(8)   NOT NULL
);

/*==============================================================*/
/* Table: FILMES                                                */
/*==============================================================*/
CREATE TABLE FILMES (
   FILMEID              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   CATEGORIAID          INTEGER NOT NULL,
   CINEMAID             INTEGER NOT NULL,
   TITULO               VARCHAR(120)  NOT NULL,
   DATALANCAMENTO       DATE,
   DURACAO              INTEGER       NOT NULL,
   PRODUTORA            VARCHAR(80),
   FIMEXEBICAO          DATE,
   IDIOMA               CHAR(4),
   SINOPSE              TEXT,
   CLASSIFICACAOETARIA  INTEGER DEFAULT 1       NOT NULL,
   RANKING              NUMERIC(2,1)       DEFAULT 0.0 NOT NULL,
   CONSTRAINT FK_FILMES_PERTENCE_CATEGORI FOREIGN KEY (CATEGORIAID)
      REFERENCES CATEGORIAS (CATEGORIAID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
   CONSTRAINT FK_CINEMAS_EXIBEM_FILMES FOREIGN KEY (CINEMAID)
      REFERENCES CINEMAS (CINEMAID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
   CONSTRAINT FK_FILMES_TEM_CLASSETARIA FOREIGN KEY (CLASSIFICACAOETARIA)
      REFERENCES CLASSIFICACOESETARIAS (CLASSIFICACAOID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
   CONSTRAINT CK_FILMES_RANKING CHECK (RANKING >= 0.0 AND RANKING <= 5.0)
);

/*==============================================================*/
/* Table: SALAS                                                 */
/*==============================================================*/
CREATE TABLE SALAS (
   SALAID       INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   CINEMAID     INTEGER,
   NOMESALA     VARCHAR(80),
   CAPACIDADE   INTEGER      NOT NULL,
   TIPOSALA     VARCHAR(20)  NOT NULL,
   CONSTRAINT FK_SALAS_POSSUI2_CINEMAS FOREIGN KEY (CINEMAID)
      REFERENCES CINEMAS (CINEMAID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

/*==============================================================*/
/* Table: SESSOES                                               */
/*==============================================================*/
CREATE TABLE SESSOES (
   SESSAOID     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   SALAID       INTEGER,
   FILMEID      INTEGER,
   INICIO       TIMESTAMP     NOT NULL,
   FIM          TIMESTAMP     NOT NULL,
   VERSAO       VARCHAR(8)    NOT NULL,
   ESTADOSESSAO VARCHAR(20)   NOT NULL,
   PRECOSESSAO  NUMERIC(5,2),
   CONSTRAINT FK_SESSOES_ORIGINAM_FILMES FOREIGN KEY (FILMEID)
      REFERENCES FILMES (FILMEID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
   CONSTRAINT FK_SESSOES_HOSPEDAM_SALAS FOREIGN KEY (SALAID)
      REFERENCES SALAS (SALAID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

/*==============================================================*/
/* Table: LUGARES                                               */
/*==============================================================*/
CREATE TABLE LUGARES (
   LUGARID      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   SALAID       INTEGER,
   FILA         VARCHAR(4)   NOT NULL,
   NUMERO       INTEGER      NOT NULL,
   TIPOLUGAR    VARCHAR(20),
   ESTADOLUGAR  VARCHAR(20),
   CONSTRAINT FK_LUGARES_POSSUI_SALAS FOREIGN KEY (SALAID)
      REFERENCES SALAS (SALAID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

/*==============================================================*/
/* Table: CLIENTES                                              */
/*==============================================================*/
CREATE TABLE CLIENTES (
   CLIENTEID            INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   NOMECLIENTE          VARCHAR(80),
   EMAILCLIENTE         VARCHAR(254),
   TELEFONECLIENTE      VARCHAR(20),
   DATANASCIMENTO       DATE,
   MORADACLIENTE        VARCHAR(120),
   CODIGOPOSTALCLIENTE  CHAR(8),
   LOCALIDADECLIENTE    VARCHAR(60),
   NIF                  VARCHAR(15)
);

/*==============================================================*/
/* Table: FUNCIONARIOS                                          */
/*==============================================================*/
CREATE TABLE FUNCIONARIOS (
   FUNCIONARIOID        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   CINEMAID             INTEGER,
   NOMEFUNCIONARIO      VARCHAR(80)   NOT NULL,
   EMAILFUNCIONARIO     VARCHAR(254),
   TELEFONEFUNCIONARIO  VARCHAR(20),
   CARGO                VARCHAR(20)   NOT NULL,
   ADMISSAO            DATE          NOT NULL,
   SALARIO              NUMERIC(8,2)  NOT NULL,
   RANKING              NUMERIC(2,1)       DEFAULT 0.0 NOT NULL,
   CONSTRAINT FK_FUNCIONA_EMPREGAM_CINEMAS FOREIGN KEY (CINEMAID)
      REFERENCES CINEMAS (CINEMAID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
   CONSTRAINT CK_FUNCIONARIOS_RANKING CHECK (RANKING >= 0.0 AND RANKING <= 5.0)
);

/*==============================================================*/
/* Table: PRODUTOS                                              */
/*==============================================================*/
CREATE TABLE PRODUTOS (
   PRODUTOID    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   NOMEPRODUTO  VARCHAR(80)   NOT NULL,
   PRECOPRODUTO NUMERIC(5,2)  NOT NULL,
   STOCK        INTEGER       NOT NULL,
   ATIVO        BOOLEAN       NOT NULL
);

/*==============================================================*/
/* Table: VENDAS                                                */
/*==============================================================*/
CREATE TABLE VENDAS (
   VENDAID        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   CLIENTEID      INTEGER,
   FUNCIONARIOID  INTEGER,
   DATA           DATE,
   ESTADOVENDA    VARCHAR(20),
   TOTALVENDA     NUMERIC(8,2),
   CONSTRAINT FK_VENDAS_EFETUA_CLIENTES FOREIGN KEY (CLIENTEID)
      REFERENCES CLIENTES (CLIENTEID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
   CONSTRAINT FK_VENDAS_FAZ_FUNCIONA FOREIGN KEY (FUNCIONARIOID)
      REFERENCES FUNCIONARIOS (FUNCIONARIOID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

/*==============================================================*/
/* Table: BILHETES                                              */
/*==============================================================*/
CREATE TABLE BILHETES (
   BILHETEID    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   LUGARID      INTEGER,
   SESSAOID     INTEGER,
   PRECOBILHETE NUMERIC(5,2)  NOT NULL,
   EMISSAO      TIMESTAMP     NOT NULL,
   CONSTRAINT FK_BILHETES_PRODUZEM_SESSOES FOREIGN KEY (SESSAOID)
      REFERENCES SESSOES (SESSAOID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
   CONSTRAINT FK_BILHETES_PERTENCEM_LUGARES FOREIGN KEY (LUGARID)
      REFERENCES LUGARES (LUGARID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

/*==============================================================*/
/* Table: VENDALINHAS                                           */
/*==============================================================*/
CREATE TABLE VENDALINHAS (
   VENDALINHAID  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   VENDAID       INTEGER,
   PRODUTOID     INTEGER,
   BILHETEID	 INTEGER, 
   QUANTIDADE    INTEGER       NOT NULL,
   TOTAL_LINHA_	 NUMERIC(5,2),
   PRECOLINHA    NUMERIC(5,2),
   CONSTRAINT FK_VENDALIN_CONTEM_VENDAS FOREIGN KEY (VENDAID)
      REFERENCES VENDAS (VENDAID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
   CONSTRAINT FK_VENDALIN_CORRESPON_PRODUTOS FOREIGN KEY (PRODUTOID)
      REFERENCES PRODUTOS (PRODUTOID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
	CONSTRAINT FK_VENDALIN_CORRESPONDE_BILHETES FOREIGN KEY (BILHETEID)
      REFERENCES BILHETES (BILHETEID)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

/*==============================================================*/
/* Table: AVALIACOES                                              */
/*==============================================================*/
CREATE TABLE AVALIACOES (
   AVALIACAOID SERIAL PRIMARY KEY,
   VENDAID INTEGER UNIQUE NOT NULL,
   TITULOAVALIACAO VARCHAR(80) NOT NULL,
   AVALIACAOCINEMA INTEGER,
   AVALIACAOFILME INTEGER,
   AVALIACAOFUNCIONARIO INTEGER,
   COMENTARIO VARCHAR(1024),
   CONSTRAINT FK_AVALIACOES_VENDA FOREIGN KEY (VENDAID) 
      REFERENCES VENDAS (VENDAID)
      ON UPDATE NO ACTION
      ON DELETE CASCADE
);
