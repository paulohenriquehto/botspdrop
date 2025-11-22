#!/bin/bash
# Monitor script for 20-user test

echo "=============================================="
echo "📊 MONITORAMENTO DO TESTE (20 USUÁRIOS)"
echo "=============================================="
echo ""

# Count unique users
echo "👥 Usuários ativos:"
docker compose logs bot --tail=500 | grep "Webhook recebido" | grep -oP '\d{12,}@lid' | sort -u | wc -l

echo ""
echo "📞 Últimas conversas:"
docker compose logs bot --tail=200 | grep "Webhook recebido" | grep -oP '\d{12,}@lid' | tail -10 | sort -u

echo ""
echo "📈 Chamadas OpenAI (últimos 5 min):"
docker compose logs bot --tail=500 --since 5m | grep "HTTP Request: POST https://api.openai.com" | wc -l

echo ""
echo "❌ Erros recentes:"
docker compose logs bot --tail=200 | grep -i "error\|exception\|traceback" | wc -l

echo ""
echo "💬 Últimas 3 respostas da Gabi:"
docker compose logs bot --tail=100 | grep "Resposta do agente" | tail -3 | sed 's/.*INFO - //'

echo ""
echo "=============================================="
