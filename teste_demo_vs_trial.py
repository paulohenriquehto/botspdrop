#!/usr/bin/env python3
"""
Teste para verificar se Gabi diferencia corretamente:
- Conta DEMONSTRAÇÃO (para ver)
- Teste 7 DIAS (para usar)
"""

import requests
import time
import json
from datetime import datetime

WEBHOOK_URL = "http://localhost:5000/webhook"

# 10 cenários únicos de teste
CENARIOS_TESTE = [
    {
        "usuario": "Cliente 1 - Quer VER produtos",
        "phone": "5511999001111",
        "mensagens": [
            "Oi, gostaria de ver os produtos que vocês têm",
        ],
        "expectativa": "DEVE OFERECER CONTA DEMO 🎁",
        "verificar": ["williamsiva4545@gmail.com", "264588aB@", "demonstração"]
    },
    {
        "usuario": "Cliente 2 - Quer VER catálogo",
        "phone": "5511999002222",
        "mensagens": [
            "Quero conhecer o catálogo de vocês antes de decidir",
        ],
        "expectativa": "DEVE OFERECER CONTA DEMO 🎁",
        "verificar": ["williamsiva4545@gmail.com", "conta de demonstração"]
    },
    {
        "usuario": "Cliente 3 - Quer VER fornecedores",
        "phone": "5511999003333",
        "mensagens": [
            "Gostaria de ver os fornecedores que trabalham com vocês",
        ],
        "expectativa": "DEVE OFERECER CONTA DEMO 🎁",
        "verificar": ["app.spdrop.com.br", "demonstração"]
    },
    {
        "usuario": "Cliente 4 - Quer VER plataforma",
        "phone": "5511999004444",
        "mensagens": [
            "Quero ver como funciona a plataforma por dentro",
        ],
        "expectativa": "DEVE OFERECER CONTA DEMO 🎁",
        "verificar": ["demonstração", "williamsiva4545"]
    },
    {
        "usuario": "Cliente 5 - Quer TESTAR (qualificado)",
        "phone": "5511999005555",
        "mensagens": [
            "Tenho uma loja online e quero testar o dropshipping com vocês",
            "Paulo Silva",
            "123.456.789-00",
            "11999005555",
            "paulo.silva@email.com"
        ],
        "expectativa": "DEVE CRIAR TRIAL 7 DIAS 🆓 (após coletar dados)",
        "verificar": ["trial", "7 dias", "teste"]
    },
    {
        "usuario": "Cliente 6 - Curiosa sobre produtos",
        "phone": "5511999006666",
        "mensagens": [
            "Oi! Quero dar uma olhada nos produtos antes",
        ],
        "expectativa": "DEVE OFERECER CONTA DEMO 🎁",
        "verificar": ["demonstração", "williamsiva4545"]
    },
    {
        "usuario": "Cliente 7 - Pergunta técnica (FAQ)",
        "phone": "5511999007777",
        "mensagens": [
            "Como funciona a integração com o Mercado Livre?",
        ],
        "expectativa": "DEVE USAR FAQ + depois oferecer demo/trial",
        "verificar": ["integração", "Mercado Livre"]
    },
    {
        "usuario": "Cliente 8 - Quer conhecer primeiro",
        "phone": "5511999008888",
        "mensagens": [
            "Quero conhecer melhor a SPDrop antes de assinar",
        ],
        "expectativa": "DEVE OFERECER CONTA DEMO 🎁",
        "verificar": ["demonstração", "app.spdrop"]
    },
    {
        "usuario": "Cliente 9 - Já decidida, quer assinar",
        "phone": "5511999009999",
        "mensagens": [
            "Já sei o que é dropshipping, quero assinar o plano semestral",
        ],
        "expectativa": "DEVE ENVIAR LINK DE PAGAMENTO direto",
        "verificar": ["pay.kiwify", "semestral", "447"]
    },
    {
        "usuario": "Cliente 10 - Viu demo, quer testar agora",
        "phone": "5511999010000",
        "mensagens": [
            "Já vi a conta demo e adorei! Agora quero testar de verdade na minha loja",
            "Maria Santos",
            "987.654.321-00",
            "11999010000",
            "maria.santos@loja.com"
        ],
        "expectativa": "DEVE CRIAR TRIAL 7 DIAS 🆓",
        "verificar": ["trial", "7 dias"]
    },
]

def enviar_mensagem(phone, message):
    """Envia mensagem para o webhook"""
    payload = {
        "from": phone,
        "body": message,
        "id": f"msg_{int(time.time() * 1000)}",
        "fromMe": False,
        "timestamp": int(time.time()),
        "hasMedia": False,
        "type": "chat"
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=60)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return False

def executar_teste():
    """Executa todos os cenários de teste"""
    print("=" * 80)
    print("🧪 TESTE: GABI - Conta Demo vs Trial 7 Dias")
    print("=" * 80)
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    resultados = []

    for idx, cenario in enumerate(CENARIOS_TESTE, 1):
        print(f"\n{'='*80}")
        print(f"📱 CENÁRIO {idx}/10: {cenario['usuario']}")
        print(f"📞 Telefone: {cenario['phone']}")
        print(f"✅ Expectativa: {cenario['expectativa']}")
        print(f"{'='*80}\n")

        sucesso_cenario = True

        for msg_idx, mensagem in enumerate(cenario['mensagens'], 1):
            print(f"  👤 Usuário ({msg_idx}/{len(cenario['mensagens'])}): {mensagem}")

            if enviar_mensagem(cenario['phone'], mensagem):
                print(f"  ✅ Mensagem enviada ao webhook")
                # Aguardar processamento e resposta da Gabi
                time.sleep(8)  # 8 segundos para processar + responder
            else:
                print(f"  ❌ Falha ao enviar mensagem")
                sucesso_cenario = False
                break

            # Delay entre mensagens do mesmo usuário
            if msg_idx < len(cenario['mensagens']):
                time.sleep(3)

        resultado = {
            "cenario": cenario['usuario'],
            "phone": cenario['phone'],
            "expectativa": cenario['expectativa'],
            "sucesso": sucesso_cenario
        }
        resultados.append(resultado)

        # Delay entre diferentes usuários (sessões separadas)
        if idx < len(CENARIOS_TESTE):
            print(f"\n  ⏳ Aguardando 5s antes do próximo cenário...\n")
            time.sleep(5)

    # Relatório final
    print("\n" + "=" * 80)
    print("📊 RELATÓRIO FINAL")
    print("=" * 80)

    for idx, resultado in enumerate(resultados, 1):
        status = "✅" if resultado['sucesso'] else "❌"
        print(f"{status} Cenário {idx}: {resultado['cenario']}")
        print(f"   Expectativa: {resultado['expectativa']}")
        print(f"   Telefone: {resultado['phone']}")
        print()

    sucessos = sum(1 for r in resultados if r['sucesso'])
    print(f"Total: {sucessos}/{len(resultados)} cenários executados com sucesso")
    print(f"\nFim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Verifique as conversas no banco de dados")
    print("2. Confirme se Gabi ofereceu DEMO para cenários 1-4, 6, 8")
    print("3. Confirme se Gabi criou TRIAL para cenários 5, 10")
    print("4. Confirme se Gabi enviou LINK para cenário 9")
    print("5. Confirme se Gabi usou FAQ para cenário 7")

    print("\n💡 COMANDO PARA VERIFICAR:")
    print("docker exec -i spdrop_postgres psql -U spdrop_user -d spdrop_db -c \"SELECT c.id, c.name, c.phone, COUNT(ch.id) as msgs FROM customers c LEFT JOIN conversation_history ch ON c.id = ch.customer_id WHERE c.phone LIKE '5511999%' GROUP BY c.id ORDER BY c.id DESC LIMIT 10;\"")

if __name__ == "__main__":
    try:
        executar_teste()
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
