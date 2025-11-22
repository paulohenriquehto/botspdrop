#!/bin/bash

echo "🚀 Iniciando Vanlu WhatsApp Bot..."
echo ""

# Subir todos os serviços
docker compose up -d

echo ""
echo "✅ Serviços iniciados!"
echo ""
echo "📋 Status dos containers:"
docker ps | grep vanlu

echo ""
echo "🔗 Links úteis:"
echo "  - WAHA API: http://localhost:3000"
echo "  - FastAPI Bot: http://localhost:5000"
echo "  - PostgreSQL: localhost:5432"
echo ""
echo "📱 Para conectar WhatsApp:"
echo "  1. Acesse: http://localhost:3000"
echo "  2. Crie uma sessão chamada 'default'"
echo "  3. Escaneie o QR Code"
echo ""
echo "📊 Para ver logs:"
echo "  docker logs -f vanlu_bot"
echo "  docker logs -f vanlu_waha"
echo ""
