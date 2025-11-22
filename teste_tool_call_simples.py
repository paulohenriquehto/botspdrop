#!/usr/bin/env python3
"""
Teste simples para verificar se as tools estão sendo chamadas
"""

import requests
import time

BOT_WEBHOOK_URL = "http://localhost:5000/webhook"

# Cliente Roberto que já tem histórico
USUARIO = {
    "nome": "Roberto Teste",
    "phone": "5511999888777",
}

def enviar_mensagem(mensagem):
    """Envia mensagem via webhook"""
    payload = {
        "from": f"{USUARIO['phone']}@lid",
        "body": mensagem,
        "timestamp": int(time.time()),
        "hasMedia": False,
        "type": "chat"
    }

    try:
        response = requests.post(BOT_WEBHOOK_URL, json=payload, timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TESTE SIMPLES DE TOOL CALL")
    print("="*70)
    print(f"👤 Cliente: {USUARIO['nome']} ({USUARIO['phone']})")
    print("="*70)

    msg = "Oi"
    print(f"\n📤 Enviando: {msg}")

    if enviar_mensagem(msg):
        print("✅ Mensagem enviada!")
        print("\n⏳ Aguarde 20s e verifique os logs do bot para ver se as tools foram chamadas:")
        print("   docker compose logs bot --tail=50 | grep -E '(tool|Tool|get_conversation_history)'")
    else:
        print("❌ Falha ao enviar mensagem")

    print("\n" + "="*70)
