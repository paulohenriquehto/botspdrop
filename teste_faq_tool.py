#!/usr/bin/env python3
"""
Teste Específico da FAQ Tool
Verifica se a ferramenta buscar_faq está sendo chamada
"""

import requests
import time
import subprocess

BOT_WEBHOOK_URL = "http://localhost:5000/webhook"

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

def verificar_logs_faq():
    """Verifica se FAQ tool foi mencionada nos logs"""
    result = subprocess.run(
        ["docker", "compose", "logs", "bot", "--tail=100"],
        capture_output=True,
        text=True
    )

    logs = result.stdout

    # Procurar por indicadores de FAQ
    indicadores = {
        "buscar_faq": "buscar_faq" in logs,
        "listar_todas_perguntas": "listar_todas_perguntas" in logs,
        "buscar_resposta_por_palavra_chave": "buscar_resposta_por_palavra_chave" in logs,
        "SPDropFAQTools": "SPDropFAQTools" in logs or "spdrop_faq" in logs
    }

    return indicadores

def contar_chamadas_openai():
    """Conta chamadas OpenAI recentes"""
    result = subprocess.run(
        ["docker", "compose", "logs", "bot", "--tail=50"],
        capture_output=True,
        text=True
    )

    lines = [l for l in result.stdout.split('\n') if "HTTP Request: POST https://api.openai.com" in l]
    return len(lines)

def executar_teste():
    """Executa teste da FAQ"""
    print("\n" + "="*80)
    print("🔍 TESTE ESPECÍFICO DA FAQ TOOL")
    print("="*80)
    print(f"👤 Cliente: {USUARIO['nome']}")
    print("🎯 Objetivo: Verificar se buscar_faq está sendo chamada")
    print("="*80)

    # Perguntas que DEVEM usar FAQ
    perguntas = [
        {
            "pergunta": "Quais são os planos disponíveis?",
            "motivo": "Pergunta específica sobre produtos da empresa"
        },
        {
            "pergunta": "Como funciona a integração com redes sociais?",
            "motivo": "Pergunta técnica específica da plataforma"
        },
        {
            "pergunta": "Qual é o prazo de entrega dos produtos?",
            "motivo": "Pergunta operacional específica"
        },
        {
            "pergunta": "Vocês têm suporte técnico?",
            "motivo": "Pergunta sobre serviços da empresa"
        }
    ]

    resultados = []

    for i, item in enumerate(perguntas, 1):
        print(f"\n{'─'*80}")
        print(f"📍 TESTE {i}/4")
        print(f"{'─'*80}")
        print(f"💬 Pergunta: {item['pergunta']}")
        print(f"📝 Motivo: {item['motivo']}")

        # Marca de tempo antes
        chamadas_antes = contar_chamadas_openai()

        # Enviar pergunta
        if not enviar_mensagem(item['pergunta']):
            print("❌ Falha ao enviar")
            continue

        print("⏳ Aguardando 20s para processamento...")
        time.sleep(20)

        # Marca de tempo depois
        chamadas_depois = contar_chamadas_openai()
        novas_chamadas = chamadas_depois - chamadas_antes

        # Verificar logs
        indicadores = verificar_logs_faq()

        print(f"\n📊 RESULTADO:")
        print(f"   Novas chamadas OpenAI: {novas_chamadas}")

        if novas_chamadas >= 2:
            print(f"   ✅ Múltiplas chamadas = TOOLS USADAS")
            usou_tools = True
        else:
            print(f"   ❌ Apenas {novas_chamadas} chamada = TOOLS NÃO USADAS")
            usou_tools = False

        # Verificar indicadores de FAQ
        print(f"\n🔍 INDICADORES DE FAQ NOS LOGS:")
        faq_mencionada = False
        for key, found in indicadores.items():
            if found:
                print(f"   ✅ {key} encontrado")
                faq_mencionada = True
            else:
                print(f"   ⚪ {key} não encontrado")

        # Resultado final
        if usou_tools and faq_mencionada:
            resultado = "✅ FAQ USADA"
        elif usou_tools and not faq_mencionada:
            resultado = "⚠️ TOOLS USADAS (mas não confirmado se foi FAQ)"
        else:
            resultado = "❌ FAQ NÃO USADA"

        resultados.append({
            "pergunta": item['pergunta'],
            "chamadas": novas_chamadas,
            "faq_mencionada": faq_mencionada,
            "resultado": resultado
        })

        print(f"\n🎯 {resultado}")

        # Delay entre testes
        if i < len(perguntas):
            print(f"\n⏸️ Aguardando 5s antes do próximo teste...")
            time.sleep(5)

    # Relatório final
    print("\n" + "="*80)
    print("📊 RELATÓRIO FINAL - FAQ TOOL")
    print("="*80)

    for i, r in enumerate(resultados, 1):
        print(f"\n{i}. {r['pergunta'][:60]}...")
        print(f"   Chamadas: {r['chamadas']} | FAQ mencionada: {r['faq_mencionada']}")
        print(f"   {r['resultado']}")

    # Conclusão
    passou = sum(1 for r in resultados if "✅" in r['resultado'])
    total = len(resultados)

    print(f"\n🎯 CONCLUSÃO:")
    print(f"   Testes com FAQ confirmada: {passou}/{total}")

    if passou == total:
        print(f"   🎉 PERFEITO! FAQ tool está sendo usada consistentemente!")
    elif passou >= total * 0.75:
        print(f"   ✅ BOM! FAQ está sendo usada na maioria dos casos")
    elif passou >= total * 0.5:
        print(f"   ⚠️ PARCIAL - FAQ só é usada às vezes")
    else:
        print(f"   ❌ FAQ raramente ou nunca é usada")

    print("\n💡 NOTA IMPORTANTE:")
    print("   Se tools são usadas mas FAQ não aparece nos logs, pode ser que:")
    print("   1. O agente use outras tools (memory, scripts) mas não FAQ")
    print("   2. Logs do Agno não mostram nome das tools executadas")
    print("   3. FAQ é chamada mas sem logging específico")

    print("\n📝 Para confirmar, veja os logs completos:")
    print("   docker compose logs bot --tail=300 | grep -i faq")

    print("="*80)

if __name__ == "__main__":
    executar_teste()
