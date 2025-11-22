#!/usr/bin/env python3
"""Teste rápido da FAQ com novas instruções"""
import requests
import time

BOT_WEBHOOK_URL = "http://localhost:5000/webhook"
USUARIO = {"phone": "5511999888777"}

def enviar(msg):
    payload = {
        "from": f"{USUARIO['phone']}@lid",
        "body": msg,
        "timestamp": int(time.time()),
        "hasMedia": False,
        "type": "chat"
    }
    try:
        requests.post(BOT_WEBHOOK_URL, json=payload, timeout=30)
        return True
    except:
        return False

print("\n🧪 TESTE RÁPIDO FAQ")
print("="*60)

# Teste 1: Pergunta sobre estoque (deve usar FAQ)
msg = "Vocês têm estoque próprio?"
print(f"\n📤 Enviando: {msg}")
enviar(msg)
print("⏳ Aguardando 20s...")
time.sleep(20)

# Verificar logs
import subprocess
result = subprocess.run(
    ["docker", "compose", "logs", "bot", "--tail=30"],
    capture_output=True, text=True
)

logs = result.stdout
chamadas = logs.count("HTTP Request: POST https://api.openai.com")

print(f"\n📊 Resultado:")
print(f"   Chamadas OpenAI: {chamadas}")
if chamadas >= 2:
    print(f"   ✅ Múltiplas chamadas = TOOLS USADAS!")
else:
    print(f"   ❌ Apenas {chamadas} = Tools não usadas")

# Mostrar trecho da resposta
if "Resposta do agente:" in logs:
    for line in logs.split('\n'):
        if "Resposta do agente:" in line:
            resposta = line.split("Resposta do agente:")[-1][:150]
            print(f"\n💬 Resposta: {resposta}...")
            break

print("="*60)
