#!/bin/bash

# Sair imediatamente se ocorrer um erro (exceto comandos que controlamos)
set -e

echo "=========================================="
echo "   🎥 CONFIGURAÇÃO DO PROJETO CINEMA 🍿   "
echo "=========================================="

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
    echo "# MONGO_URI=... (Opcional para logs)" >> .env
else
    echo "✅ Ficheiro .env existe."
fi

# Migrações
echo "🗄️  A aplicar migrações da base de dados..."
python manage.py migrate

# 2. Dados Iniciais
echo ""
echo "💾 2. Dados Iniciais"
echo "--------------------"
echo "Deseja limpar a BD e reinserir dados básicos? (s/n)"
echo "(Recomendado para primeira instalação ou reset)"
read -r reset_db

if [[ "$reset_db" =~ ^[Ss]$ ]]; then
    echo "⚠️  ATENÇÃO: Isto apagará TODAS as vendas e bilhetes!"
    echo "Tem a certeza? (digite 'sim' para confirmar)"
    read -r confirm
    if [ "$confirm" == "sim" ]; then
        echo "🧹 A limpar base de dados..."
        python manage.py clear_bd2ap1_tables
        echo "🌱 A semear dados básicos..."
        python manage.py seed_basic_data
        echo "✅ Dados reiniciados com sucesso."
        
        echo ""
        echo "Deseja criar um superutilizador (admin)? (s/n)"
        read -r criar_admin
        if [[ "$criar_admin" =~ ^[Ss]$ ]]; then
            python manage.py createsuperuser
        fi
    else
        echo "Operação cancelada."
    fi
else
    # Se não resetar, pergunta se quer apenas semear o básico caso esteja vazio
    echo "Deseja apenas garantir os dados básicos (sem apagar)? (s/n)"
    read -r semear
    if [[ "$semear" =~ ^[Ss]$ ]]; then
        python manage.py seed_basic_data
    fi
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
        echo "   Backend: http://localhost:8000"
        echo "   Frontend: http://localhost:5173"
        echo "   (Pressione Ctrl+C para parar)"
        
        python manage.py runserver &
        BACKEND_PID=$!
        
        cd frontend
        npm run dev -- --host &
        FRONTEND_PID=$!
        cd ..
        
        wait
        ;;
    2)
        echo "🔙 A iniciar Backend..."
        python manage.py runserver
        ;;
    3)
        if [ "$HAS_NODE" = false ]; then
            echo "❌ Não é possível iniciar o frontend sem Node.js."
            exit 1
        fi
        cd frontend
        npm run dev
        ;;
    *)
        echo "Adeus! 👋"
        ;;
esac