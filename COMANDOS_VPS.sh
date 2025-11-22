#!/bin/bash
# ============================================
# SCRIPT DE DEPLOY RÁPIDO - SPDROP v1.1
# ============================================
# Execute este script NA VPS após copiar os arquivos

set -e  # Para na primeira erro

echo "🚀 Iniciando deploy do SPDrop v1.1..."

# 1. Parar containers antigos
echo "📦 Parando containers..."
docker-compose -f docker-compose.prod.yml down -v
docker volume prune -f

# 2. Baixar imagens v1.1 do Docker Hub
echo "⬇️  Baixando imagens v1.1..."
docker-compose -f docker-compose.prod.yml pull

# 3. Subir containers
echo "🔄 Iniciando containers..."
docker-compose -f docker-compose.prod.yml up -d

# 4. Aguardar PostgreSQL ficar pronto
echo "⏳ Aguardando PostgreSQL inicializar..."
sleep 15

# 5. Criar tabelas
echo "🗄️  Criando tabelas no banco de dados..."
docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db < init.sql

# 6. Verificar tabelas
echo "✅ Verificando tabelas criadas..."
docker exec -it spdrop_postgres psql -U spdrop_user -d spdrop_db -c "\dt"

# 7. Status dos containers
echo "📊 Status dos containers:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "✅ Deploy concluído!"
echo ""
echo "📝 Próximos passos:"
echo "1. Envie 'oi' pelo WhatsApp para testar"
echo "2. Veja os logs: docker-compose -f docker-compose.prod.yml logs -f bot"
echo ""
