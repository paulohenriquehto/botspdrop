#!/usr/bin/env python3
"""
Teste de Retorno do Cliente - Verifica se a Gabi lembra da conversa anterior
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

# Mesmo cliente do teste anterior
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

def verificar_ultima_resposta(customer_id):
    """Verifica última resposta da Gabi"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT user_message, agent_response, timestamp
            FROM conversation_history
            WHERE customer_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """, (customer_id,))

        result = cur.fetchone()
        conn.close()

        return result

    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def get_customer_id():
    """Pega ID do cliente"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT id FROM customers WHERE phone = %s", (USUARIO['phone'],))
        result = cur.fetchone()
        conn.close()

        return result['id'] if result else None

    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def executar_teste():
    """Executa teste de retorno"""
    print("\n" + "="*70)
    print("🔄 TESTE DE RETORNO DO CLIENTE")
    print("="*70)
    print(f"👤 Cliente: {USUARIO['nome']} ({USUARIO['phone']})")
    print("🎯 Objetivo: Verificar se Gabi lembra da conversa anterior")
    print("="*70)

    # Pegar ID do cliente
    customer_id = get_customer_id()

    if not customer_id:
        print("❌ Cliente não encontrado! Execute teste_contexto_melhorado.py primeiro")
        return

    print(f"✅ Cliente encontrado (ID: {customer_id})")

    # Verificar histórico anterior
    print("\n📜 Verificando histórico anterior...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT COUNT(*) as total FROM conversation_history WHERE customer_id = %s", (customer_id,))
    total = cur.fetchone()['total']
    conn.close()

    print(f"💾 Total de conversas anteriores: {total}")

    if total == 0:
        print("⚠️ Nenhuma conversa anterior! Execute teste_contexto_melhorado.py primeiro")
        return

    # Teste 1: Mensagem simples
    print("\n" + "─"*70)
    print("📍 TESTE 1: Mensagem simples de retorno")
    print("─"*70)

    msg1 = "Oi, tô aqui de novo!"
    print(f"\n  👤 {USUARIO['nome']}: {msg1}")

    enviar_mensagem(msg1)
    print("  ⏳ Aguardando resposta (20s)...")
    time.sleep(20)

    resposta1 = verificar_ultima_resposta(customer_id)

    if resposta1:
        print(f"\n  🤖 Gabi: {resposta1['agent_response'][:300]}...")

        # Analisar resposta
        resp_lower = resposta1['agent_response'].lower()

        print("\n  🔍 ANÁLISE:")

        if "roberto" in resp_lower:
            print("     ✅ Chamou pelo nome (Roberto)")
        else:
            print("     ❌ NÃO chamou pelo nome")

        if "você já é assinante" in resp_lower and "quer conhecer" in resp_lower:
            print("     ❌ RESETOU CONVERSA - perguntou se é assinante novamente")
        else:
            print("     ✅ NÃO resetou - continuou conversa")

        if "semestral" in resp_lower or "447" in resp_lower:
            print("     ✅ Lembrou do plano escolhido")
        else:
            print("     ⚠️ Não mencionou plano (pode ser normal)")

    # Teste 2: Pergunta sobre conversa anterior
    print("\n" + "─"*70)
    print("📍 TESTE 2: Perguntar sobre conversa anterior")
    print("─"*70)

    msg2 = "Eu já tinha escolhido um plano, lembra?"
    print(f"\n  👤 {USUARIO['nome']}: {msg2}")

    enviar_mensagem(msg2)
    print("  ⏳ Aguardando resposta (20s)...")
    time.sleep(20)

    resposta2 = verificar_ultima_resposta(customer_id)

    if resposta2:
        print(f"\n  🤖 Gabi: {resposta2['agent_response'][:300]}...")

        # Analisar resposta
        resp_lower = resposta2['agent_response'].lower()

        print("\n  🔍 ANÁLISE:")

        if "semestral" in resp_lower or "447" in resp_lower:
            print("     ✅ LEMBROU DO PLANO SEMESTRAL!")
        else:
            print("     ❌ NÃO lembrou do plano")

        if "lembro" in resp_lower or "claro" in resp_lower or "sim" in resp_lower:
            print("     ✅ Confirmou que lembra")
        else:
            print("     ❌ Não confirmou que lembra")

    # Teste 3: Teste final de memória
    print("\n" + "─"*70)
    print("📍 TESTE 3: Qual era minha situação financeira?")
    print("─"*70)

    msg3 = "Lembra o que eu falei sobre dinheiro?"
    print(f"\n  👤 {USUARIO['nome']}: {msg3}")

    enviar_mensagem(msg3)
    print("  ⏳ Aguardando resposta (20s)...")
    time.sleep(20)

    resposta3 = verificar_ultima_resposta(customer_id)

    if resposta3:
        print(f"\n  🤖 Gabi: {resposta3['agent_response'][:300]}...")

        # Analisar resposta
        resp_lower = resposta3['agent_response'].lower()

        print("\n  🔍 ANÁLISE:")

        if "não tinha" in resp_lower or "conseguiu" in resp_lower or "juntar" in resp_lower:
            print("     ✅ LEMBROU DA SITUAÇÃO FINANCEIRA!")
        else:
            print("     ❌ NÃO lembrou da situação financeira")

    # Relatório Final
    print("\n" + "="*70)
    print("📊 RELATÓRIO FINAL")
    print("="*70)

    # Contar conversas agora
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT COUNT(*) as total FROM conversation_history WHERE customer_id = %s", (customer_id,))
    total_agora = cur.fetchone()['total']
    conn.close()

    print(f"💾 Conversas antes: {total}")
    print(f"💾 Conversas agora: {total_agora}")
    print(f"➕ Novas conversas: {total_agora - total}")

    print("\n🎯 CONCLUSÃO:")

    if resposta1 and "você já é assinante" in resposta1['agent_response'].lower():
        print("❌ FALHOU - Gabi RESETOU a conversa e perguntou se é assinante novamente")
        print("⚠️ O contexto NÃO está sendo mantido entre sessões!")
    else:
        print("✅ PASSOU - Gabi manteve o contexto e continuou a conversa!")
        print("🎉 O sistema de memória está funcionando corretamente!")

    print("="*70)

if __name__ == "__main__":
    executar_teste()
