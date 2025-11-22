#!/usr/bin/env python3
"""
Teste de Múltiplas Ferramentas Simultâneas
Verifica se o agente consegue chamar 1, 2, 3 e 4 tools ao mesmo tempo
"""

import requests
import time
import psycopg2
from psycopg2.extras import RealDictCursor

BOT_WEBHOOK_URL = "http://localhost:5000/webhook"
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "spdrop_db",
    "user": "spdrop_user",
    "password": "spdrop_password"
}

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

def contar_chamadas_openai():
    """Conta chamadas à API OpenAI nos últimos 30 segundos"""
    import subprocess
    result = subprocess.run(
        ["docker", "compose", "logs", "bot", "--tail=50"],
        capture_output=True,
        text=True
    )

    lines = result.stdout.split('\n')

    # Filtrar apenas logs dos últimos 30s
    recent_lines = [l for l in lines if "HTTP Request: POST https://api.openai.com" in l]

    return len(recent_lines)

def analisar_logs_ferramentas():
    """Analisa logs para ver quais ferramentas foram chamadas"""
    import subprocess
    result = subprocess.run(
        ["docker", "compose", "logs", "bot", "--tail=100"],
        capture_output=True,
        text=True
    )

    logs = result.stdout

    # Procurar por indicadores de tool calls
    tools_detectadas = {
        "memory_tools": 0,
        "faq_tools": 0,
        "conversation_scripts": 0,
        "trial_tools": 0
    }

    # Contar menções a cada toolkit
    if "get_conversation_history" in logs or "get_important_memories" in logs:
        tools_detectadas["memory_tools"] += 1
    if "buscar_faq" in logs or "listar_todas_perguntas" in logs:
        tools_detectadas["faq_tools"] += 1
    if "buscar_por_perfil" in logs or "buscar_por_etapa" in logs:
        tools_detectadas["conversation_scripts"] += 1
    if "create_trial_user" in logs or "get_trial_users" in logs:
        tools_detectadas["trial_tools"] += 1

    return tools_detectadas

def executar_teste():
    """Executa teste progressivo"""
    print("\n" + "="*80)
    print("🧪 TESTE DE MÚLTIPLAS FERRAMENTAS SIMULTÂNEAS")
    print("="*80)
    print(f"👤 Cliente: {USUARIO['nome']} ({USUARIO['phone']})")
    print("🎯 Objetivo: Verificar se agente chama 1, 2, 3 e 4 tools juntas")
    print("="*80)

    testes = [
        {
            "nome": "TESTE 1: 1 Tool (Memory)",
            "mensagem": "Oi",
            "esperado": "Deve chamar get_conversation_history + get_important_memories",
            "tools_esperadas": ["memory_tools"]
        },
        {
            "nome": "TESTE 2: 2 Tools (Memory + FAQ)",
            "mensagem": "Como funciona o dropshipping?",
            "esperado": "Deve chamar memory + buscar_faq",
            "tools_esperadas": ["memory_tools", "faq_tools"]
        },
        {
            "nome": "TESTE 3: 3 Tools (Memory + FAQ + Scripts)",
            "mensagem": "Me mostre um exemplo de conversa de vendas",
            "esperado": "Deve chamar memory + faq + buscar_exemplo_completo",
            "tools_esperadas": ["memory_tools", "faq_tools", "conversation_scripts"]
        },
        {
            "nome": "TESTE 4: 4 Tools (Todas)",
            "mensagem": "Quero fazer o teste grátis de 7 dias, meu CPF é 123.456.789-00 e email teste@example.com",
            "esperado": "Deve chamar memory + faq + scripts + create_trial_user",
            "tools_esperadas": ["memory_tools", "faq_tools", "conversation_scripts", "trial_tools"]
        }
    ]

    resultados = []

    for i, teste in enumerate(testes, 1):
        print(f"\n{'─'*80}")
        print(f"📍 {teste['nome']}")
        print(f"{'─'*80}")
        print(f"💬 Mensagem: {teste['mensagem']}")
        print(f"🎯 Esperado: {teste['esperado']}")

        # Enviar mensagem
        if not enviar_mensagem(teste['mensagem']):
            print("❌ Falha ao enviar mensagem")
            continue

        # Aguardar processamento
        print(f"⏳ Aguardando 25s para processamento...")
        time.sleep(25)

        # Contar chamadas OpenAI
        chamadas = contar_chamadas_openai()
        print(f"\n📊 ANÁLISE:")
        print(f"   Chamadas OpenAI detectadas: {chamadas}")

        if chamadas >= 2:
            print(f"   ✅ Múltiplas chamadas = TOOLS FORAM USADAS")
        else:
            print(f"   ❌ Apenas {chamadas} chamada = TOOLS NÃO FORAM USADAS")

        # Análise qualitativa (baseada em múltiplas chamadas)
        if chamadas >= 2:
            resultado = "✅ PASSOU"
        elif chamadas == 1:
            resultado = "❌ FALHOU"
        else:
            resultado = "⚠️ INDETERMINADO"

        resultados.append({
            "teste": teste['nome'],
            "chamadas": chamadas,
            "resultado": resultado
        })

        print(f"   {resultado}")

        # Delay entre testes
        if i < len(testes):
            print(f"\n⏸️ Aguardando 5s antes do próximo teste...")
            time.sleep(5)

    # Relatório final
    print("\n" + "="*80)
    print("📊 RELATÓRIO FINAL")
    print("="*80)

    for r in resultados:
        print(f"{r['resultado']} {r['teste']}")
        print(f"   Chamadas OpenAI: {r['chamadas']}")

    # Conclusão
    passou = sum(1 for r in resultados if "✅" in r['resultado'])
    total = len(resultados)

    print(f"\n🎯 CONCLUSÃO:")
    print(f"   Testes que passaram: {passou}/{total}")

    if passou == total:
        print(f"   🎉 SUCESSO TOTAL! Agente consegue usar múltiplas tools!")
    elif passou >= total * 0.75:
        print(f"   ✅ BOM! Maioria dos testes passou")
    elif passou >= total * 0.5:
        print(f"   ⚠️ PARCIAL - Alguns testes falharam")
    else:
        print(f"   ❌ FALHOU - Maioria dos testes falhou")

    print("\n💡 DICA: Veja os logs completos com:")
    print("   docker compose logs bot --tail=200 | grep -E '(HTTP.*openai|tool)'")
    print("="*80)

if __name__ == "__main__":
    executar_teste()
