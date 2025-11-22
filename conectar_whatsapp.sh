#!/bin/bash

echo "🚀 Conectando WhatsApp ao WAHA..."
echo ""

API_KEY="cd9049e24c614f1aab5192f92906b4ca"

# 1. Criar sessão
echo "1. Criando sessão 'default'..."
curl -X POST http://localhost:3000/api/sessions/start \
  -H "X-Api-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "default",
    "config": {
      "webhooks": [{
        "url": "http://bot:5000/webhook",
        "events": ["message"]
      }]
    }
  }'

echo ""
echo ""
echo "2. Aguardando 5 segundos..."
sleep 5

# 2. Pegar QR Code
echo ""
echo "3. Buscando QR Code..."
echo ""
curl http://localhost:3000/api/default/auth/qr \
  -H "X-Api-Key: $API_KEY"

echo ""
echo ""
echo "✅ QR Code gerado!"
echo ""
echo "📱 Agora:"
echo "1. Abra WhatsApp no celular"
echo "2. Vá em Menu → Dispositivos Conectados"
echo "3. Clique em 'Conectar um dispositivo'"
echo "4. Escaneie o QR Code acima"
echo ""
