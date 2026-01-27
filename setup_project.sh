#!/bin/bash

# Sair imediatamente se ocorrer um erro (exceto comandos que controlamos)
set -e

echo "=========================================="
echo "   🎥 CONFIGURAÇÃO DO PROJETO CINEMA 🍿   "
echo "=========================================="

DB_NAME="cinemaDB"
DB_USER="postgres" # Ajuste se necessário ou deixe o sistema pedir
# Se quiser usar o usuario atual do sistema:
# DB_USER=$(whoami)

# 0. Verificar Pré-requisitos
echo ""
echo "🔍 0. A verificar pré-requisitos..."

# Verificar Python
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "❌ Erro: Python não encontrado. Por favor instale o Python."
    exit 1
fi
echo "✅ Python: $($PYTHON --version)"

# Verificar psql
if ! command -v psql &>/dev/null; then
    echo "❌ Erro: psql (PostgreSQL client) não encontrado."
    exit 1
fi
echo "✅ PostgreSQL client: $(psql --version)"

# Verificar Node.js/NPM
HAS_NODE=false
if command -v npm &>/dev/null; then
    echo "✅ NPM: $(npm --version)"
    HAS_NODE=true
else
    echo "⚠️  Aviso: NPM (Node.js) não encontrado. O Frontend não poderá ser iniciado."
fi

# 1. Configurar Backend
echo ""
echo "🔧 1. Configuração do Backend (Django)"
echo "--------------------------------------"

# Criar Ambiente Virtual
if [ ! -d "venv" ]; then
    echo "📦 A criar ambiente virtual (venv)..."
    $PYTHON -m venv venv
else
    echo "✅ Ambiente virtual detetado."
fi

# Ativar Ambiente Virtual
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip > /dev/null 2>&1

# Instalar Dependências
echo "⬇️  A instalar/atualizar dependências do Python..."
pip install -r requirements.txt

# Criar .env
if [ ! -f ".env" ]; then
    echo "📝 A criar ficheiro .env..."
    echo "SECRET_KEY=django-insecure-dev-key-change-in-production" > .env
    echo "DEBUG=True" >> .env
    echo "OMDB_API_KEY=30f195b7" >> .env
else
    echo "✅ Ficheiro .env existe."
fi

# 2. Base de Dados (SQL Scripts)
echo ""
echo "💾 2. Configuração da Base de Dados (Via SQL)"
echo "---------------------------------------------"
echo "Esta operação irá recriar as tabelas e preencher dados usando os scripts SQL."
echo "Scripts: create.sql, funcoes.sql, triggers.sql, fill.sql, etc."
echo "⚠️  ATENÇÃO: A base de dados '$DB_NAME' será modificada."
echo "Deseja continuar? (s/n)"
read -r reset_db

if [[ "$reset_db" =~ ^[Ss]$ ]]; then
    
    # Check database connection/existence
    if ! psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        echo "⚠️  Base de dados '$DB_NAME' não existe. A tentar criar..."
        createdb "$DB_NAME" || { echo "❌ Falha ao criar BD. Crie manualmente: createdb $DB_NAME"; exit 1; }
    fi

    echo "🔄 A executar scripts SQL..."
    
    # Ordem de execução
    # 1. Schema (create)
    # 2. Django System Tables (Auth, Admin...) - NECESSÁRIO POIS create.sql APAGA TUDO
    # 3. Objetos lógicos (functions, triggers, views, procedures)
    # 4. Dados (fill)
    
    psql -d "$DB_NAME" -f Scripts/create.sql
    
    # Garantir que o role admin_bd existe para podermos "logar como admin" nas migrações
    echo "🔑 A preparar utilizador administrador para migrações..."
    psql -d "$DB_NAME" -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'admin_bd') THEN CREATE ROLE admin_bd WITH LOGIN PASSWORD 'admin123' SUPERUSER; END IF; END \$\$;"

    echo "⚙️  A sincronizar Django (System Tables - como Admin)..."
    python manage.py migrate --database=admin admin
    python manage.py migrate --database=admin auth
    python manage.py migrate --database=admin contenttypes
    python manage.py migrate --database=admin sessions
    
    # Fingir migração da app principal (pois já criamos as tabelas via SQL)
    echo "🙈 A registar tabelas de domínio (Fake Migration - como Admin)..."
    python manage.py migrate --database=admin bd2ap1 --fake

    # Migrar todas as outras apps (incluindo Profiles, Cinemas, Vendas, etc.)
    echo "🚀 A aplicar migrações restantes (como Admin)..."
    python manage.py migrate --database=admin --fake-initial

    psql -d "$DB_NAME" -f Scripts/funcoes.sql
    psql -d "$DB_NAME" -f Scripts/procedimentos.sql
    psql -d "$DB_NAME" -f Scripts/triggers.sql
    psql -d "$DB_NAME" -f Scripts/vistas.sql
    psql -d "$DB_NAME" -f Scripts/fill.sql
    psql -d "$DB_NAME" -f Scripts/indices.sql
    psql -d "$DB_NAME" -f Scripts/exportações.sql
    psql -d "$DB_NAME" -f Scripts/users_roles.sql # Aplica permissões finais e ownerships
    
    echo "✅ SQL Scripts executados com sucesso."

    echo ""
    echo "Deseja criar um superutilizador (admin) do Django? (s/n)"
    read -r criar_admin
    if [[ "$criar_admin" =~ ^[Ss]$ ]]; then
        python manage.py createsuperuser --database=admin
    fi

else
    echo "⏩ Saltando configuração SQL."
    echo "   (Assumindo que a BD já está pronta)"
fi

# 3. Configurar Frontend
echo ""
echo "🎨 3. Configuração do Frontend"
echo "------------------------------"

if [ "$HAS_NODE" = true ]; then
    if [ -d "frontend" ]; then
        echo "Deseja instalar dependências do Frontend? (s/n)"
        read -r install_front
        if [[ "$install_front" =~ ^[Ss]$ ]]; then
            cd frontend
            echo "⬇️  A instalar pacotes NPM (pode demorar)..."
            npm install
            cd ..
        fi
    else
        echo "❌ Pasta 'frontend' não encontrada."
        HAS_NODE=false
    fi
else
    echo "⏩ Saltando configuração do frontend (Node não instalado)."
fi

# 4. Menu de Inicialização
echo ""
echo "🚀 TUDO PRONTO!"
echo "=========================================="
echo "1. Iniciar TUDO (Backend + Frontend)"
echo "2. Iniciar apenas Backend"
echo "3. Iniciar apenas Frontend"
echo "4. Sair"
echo "=========================================="
read -r opcao

cleanup() {
    echo ""
    echo "🛑 A encerrar servidores..."
    if [ -n "$BACKEND_PID" ]; then kill $BACKEND_PID 2>/dev/null; fi
    if [ -n "$FRONTEND_PID" ]; then kill $FRONTEND_PID 2>/dev/null; fi
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT

case $opcao in
    1)
        if [ "$HAS_NODE" = false ]; then
            echo "❌ Não é possível iniciar o frontend sem Node.js."
            exit 1
        fi
        
        echo "🌐 A iniciar Backend e Frontend..."
        echo "   Backend: http://0.0.0.0:8000 (Acessível na rede)"
        echo "   Frontend: http://localhost:5173"
        echo "   (Pressione Ctrl+C para parar)"
        
        # Run Django on 0.0.0.0 to allow network access
        python manage.py runserver 0.0.0.0:8000 &
        BACKEND_PID=$!
        
        cd frontend
        npm run dev -- --host &
        FRONTEND_PID=$!
        cd ..
        
        wait
        ;;
    2)
        echo "🔙 A iniciar Backend..."
        python manage.py runserver 0.0.0.0:8000
        ;;
    3)
        if [ "$HAS_NODE" = false ]; then
            echo "❌ Não é possível iniciar o frontend sem Node.js."
            exit 1
        fi
        cd frontend
        npm run dev -- --host
        ;;
    *)
        echo "Adeus! 👋"
        ;;
esac