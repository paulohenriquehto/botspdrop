#!/usr/bin/env python3
import requests
import base64
import json

# Buscar QR code da Evolution API
response = requests.get(
    "http://localhost:8080/instance/connect/spdrop",
    headers={"apikey": "spdrop_evolution_key_2025"}
)

data = response.json()

if "base64" in data and data["base64"]:
    # Extrair base64 da imagem
    base64_str = data["base64"].replace("data:image/png;base64,", "")

    # Salvar imagem
    with open("whatsapp_qrcode.png", "wb") as f:
        f.write(base64.b64decode(base64_str))

    print("✅ QR Code salvo em: whatsapp_qrcode.png")
    print(f"📊 Contador: {data.get('count', 0)}")
    print("\n📱 Para conectar:")
    print("1. Abra WhatsApp no celular")
    print("2. Vá em Menu → Dispositivos Conectados")
    print("3. Clique em 'Conectar um dispositivo'")
    print("4. Escaneie o QR Code salvo em whatsapp_qrcode.png")
    print("\nOu acesse no navegador: http://localhost:8080/manager")
else:
    print("❌ QR Code não disponível")
    print(json.dumps(data, indent=2))
