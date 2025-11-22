#!/bin/bash

echo "📊 INICIALIZANDO BANCO DE DADOS"
echo "==============================="
echo ""

# Verificar se init.sql existe
if [ ! -f init.sql ]; then
    echo "⚠️  Arquivo init.sql não encontrado. Criando..."
    cat > init.sql << 'EOF'
-- Tabela de clientes
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de conversas
CREATE TABLE IF NOT EXISTS conversas (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_id VARCHAR(100)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_customer_phone ON customers(phone_number);
CREATE INDEX IF NOT EXISTS idx_conversas_customer ON conversas(customer_id);
CREATE INDEX IF NOT EXISTS idx_conversas_timestamp ON conversas(timestamp);

-- Tabela de usuários admin (para dashboard)
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF
    echo "✅ Arquivo init.sql criado"
fi

# Executar SQL no PostgreSQL
echo "1️⃣ Executando SQL no PostgreSQL..."
docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db < init.sql

# Verificar tabelas criadas
echo ""
echo "2️⃣ Verificando tabelas criadas:"
docker exec -it spdrop_postgres psql -U spdrop_user -d spdrop_db -c "\dt"

# Testar conexão do bot
echo ""
echo "3️⃣ Testando conexão do bot com PostgreSQL..."
docker exec spdrop_bot python3 -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    print('✅ Bot conectou com sucesso ao PostgreSQL!')
    conn.close()
except Exception as e:
    print(f'❌ Erro na conexão: {e}')
"

echo ""
echo "✅ Banco de dados inicializado!"
echo "Agora envie uma mensagem pelo WhatsApp para testar."
