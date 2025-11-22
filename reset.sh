#!/bin/bash

echo "🔥 RESET COMPLETO DO SPDROP"
echo "============================"
echo ""

# Parar todos os containers
echo "1️⃣ Parando todos os containers..."
docker-compose -f docker-compose.prod.yml down

# Remover TODOS os volumes (incluindo órfãos)
echo "2️⃣ Removendo volumes..."
docker-compose -f docker-compose.prod.yml down -v
docker volume prune -f

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "❌ ERRO: Arquivo .env não encontrado!"
    echo "Crie o arquivo .env antes de continuar."
    exit 1
fi

echo "3️⃣ Verificando variáveis do .env..."
source .env
echo "   POSTGRES_USER: $POSTGRES_USER"
echo "   POSTGRES_DB: $POSTGRES_DB"
echo "   POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:0:5}***"

# Subir containers
echo "4️⃣ Subindo containers com variáveis do .env..."
docker-compose -f docker-compose.prod.yml up -d

echo "5️⃣ Aguardando PostgreSQL ficar pronto..."
sleep 15

# Verificar status
echo "6️⃣ Status dos containers:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "✅ Reset completo! Agora execute: bash init-db.sh"
