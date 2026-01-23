--------------------------------------------------------------
-- UTILIZADOR ADMINISTRADOR
CREATE ROLE admin_bd 
WITH LOGIN PASSWORD 'admin123'
SUPERUSER;
--------------------------------------------------------------


--------------------------------------------------------------
-- UTILIZADOR DA APLICAÇÃO
CREATE ROLE app_user 
WITH LOGIN PASSWORD 'app123';

-- Permissao para se ligar à BD
GRANT CONNECT ON DATABASE "cinemaDB" TO app_user;

-- Permissao para usar o schema publico
GRANT USAGE ON SCHEMA public TO app_user;

-- Permissoes nas tabelas já existentes
GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO app_user;

GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_user;
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA public TO app_user;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Permissoes automaticas para tabelas criadas dps
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT ON SEQUENCES TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT EXECUTE ON FUNCTIONS TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT EXECUTE ON ROUTINES TO app_user;
--------------------------------------------------------------


--------------------------------------------------------------
-- UTILIZADOR ANALISTA (LEITURA)
CREATE ROLE analista 
WITH LOGIN PASSWORD 'analista123';

-- Permissao para se ligar à BD
GRANT CONNECT ON DATABASE "cinemaDB" TO analista;

-- Permissao para usar o schema publico
GRANT USAGE ON SCHEMA public TO analista;

-- Permissoes nas tabelas já existentes
GRANT SELECT 
ON ALL TABLES IN SCHEMA public 
TO analista;

-- Permissoes automaticas para tabelas criadas dps
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO analista;
--------------------------------------------------------------

SELECT rolname, rolsuper, rolcanlogin
FROM pg_roles
WHERE rolname IN ('admin_bd', 'app_user', 'analista');

