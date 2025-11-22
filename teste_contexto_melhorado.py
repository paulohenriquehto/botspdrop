#!/usr/bin/env python3
"""
Teste de Contexto MELHORADO - Verifica se o contexto é mantido entre interações

Este teste envia mensagens com delay de 15s entre elas para forçar
múltiplos processamentos e verificar se o contexto é mantido.
"""

import requests
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

BOT_WEBHOOK_URL = "http://localhost:5000/webhook"
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "spdrop_db",
    "user": "spdrop_user",
    "password": "spdrop_password"
}

# Usuário para teste
USUARIO_TESTE = {
    "nome": "Roberto Teste",
    "phone": "5511999888777",
}

# Fluxo de conversa que testa o contexto
CONVERSAS = [
    # Rodada 1 - Apresentação
    {
        "mensagens": ["Oi", "Quero conhecer a plataforma"],
        "verificar": "Deve perguntar se é assinante ou conhecer plataforma"
    },
    # Rodada 2 - Dar informação importante (nome)
    {
        "mensagens": ["Quero conhecer", "Meu nome é Roberto"],
        "verificar": "Deve chamar de Roberto nas próximas mensagens"
    },
    # Rodada 3 - Perguntar sobre planos
    {
        "mensagens": ["Quanto custa?", "Quais são os planos?"],
        "verificar": "Deve lembrar que nome é Roberto"
    },
    # Rodada 4 - Informar que NÃO tem dinheiro
    {
        "mensagens": ["Não tenho dinheiro agora", "Tá caro"],
        "verificar": "Deve lembrar contexto anterior e adaptar oferta"
    },
    # Rodada 5 - Mudar de ideia
    {
        "mensagens": ["Espera, consegui o dinheiro", "Quero o plano semestral"],
        "verificar": "Deve lembrar que antes disse não ter dinheiro"
    },
    # Rodada 6 - Teste de memória
    {
        "mensagens": ["Qual é meu nome mesmo?"],
        "verificar": "Deve responder 'Roberto'"
    },
    # Rodada 7 - Contexto longo
    {
        "mensagens": ["Quanto ficou o plano que eu escolhi?"],
        "verificar": "Deve lembrar que escolheu plano semestral"
    },
    # Rodada 8 - Referência a conversa anterior
    {
        "mensagens": ["Lembra que eu disse que não tinha dinheiro antes?"],
        "verificar": "Deve confirmar que lembra"
    },
]

def limpar_dados_teste():
    """Limpa dados de teste"""
    print("\n🧹 Limpando dados de teste...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        phone = USUARIO_TESTE["phone"]

        cur.execute("""
            DELETE FROM conversation_history
            WHERE customer_id IN (SELECT id FROM customers WHERE phone = %s)
        """, (phone,))

        cur.execute("""
            DELETE FROM sessions
            WHERE customer_id IN (SELECT id FROM customers WHERE phone = %s)
        """, (phone,))

        cur.execute("DELETE FROM customers WHERE phone = %s", (phone,))

        conn.commit()
        conn.close()
        print("✅ Dados limpos!")

    except Exception as e:
        print(f"⚠️ Erro ao limpar: {e}")

def criar_usuario():
    """Cria usuário no banco"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            INSERT INTO customers (name, phone, email, created_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (phone) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
        """, (USUARIO_TESTE["nome"], USUARIO_TESTE["phone"],
              f"{USUARIO_TESTE['phone']}@spdrop.com"))

        result = cur.fetchone()
        conn.commit()
        conn.close()

        return result['id'] if result else None

    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return None

def enviar_mensagem(mensagem):
    """Envia mensagem via webhook"""
    payload = {
        "from": f"{USUARIO_TESTE['phone']}@lid",
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

def verificar_contexto(customer_id):
    """Verifica conversas salvas"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT user_message, agent_response, timestamp
            FROM conversation_history
            WHERE customer_id = %s
            ORDER BY timestamp DESC
            LIMIT 20
        """, (customer_id,))

        conversas = cur.fetchall()
        conn.close()

        return conversas

    except Exception as e:
        print(f"❌ Erro ao verificar contexto: {e}")
        return []

def analisar_resposta(resposta, nome_usuario):
    """Analisa se a resposta mantém contexto"""
    problemas = []

    # Verificar se chama pelo nome
    if nome_usuario.lower() not in resposta.lower():
        problemas.append(f"⚠️ Não chamou pelo nome '{nome_usuario}'")

    # Verificar se resetou conversa
    if "você já é assinante" in resposta.lower() and "quer conhecer" in resposta.lower():
        problemas.append("⚠️ RESETOU CONVERSA - pergunta inicial novamente")

    return problemas

def executar_teste():
    """Executa teste completo"""
    print("\n" + "="*70)
    print("🧪 TESTE DE CONTEXTO MELHORADO")
    print("="*70)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 Usuário: {USUARIO_TESTE['nome']} ({USUARIO_TESTE['phone']})")
    print(f"💬 Total de rodadas: {len(CONVERSAS)}")
    print("="*70)

    # Limpar e criar usuário
    limpar_dados_teste()
    customer_id = criar_usuario()

    if not customer_id:
        print("❌ Falha ao criar usuário")
        return

    print(f"✅ Usuário criado (ID: {customer_id})\n")

    erros_contexto = []
    total_conversas_salvas = 0

    # Executar cada rodada
    for i, rodada in enumerate(CONVERSAS, 1):
        print(f"\n{'─'*70}")
        print(f"📍 RODADA {i}/{len(CONVERSAS)}")
        print(f"🎯 Verificação: {rodada['verificar']}")
        print(f"{'─'*70}")

        # Enviar mensagens da rodada
        for msg in rodada["mensagens"]:
            print(f"  👤 {USUARIO_TESTE['nome']}: {msg}")
            if not enviar_mensagem(msg):
                print(f"    ❌ Falha ao enviar")

        # Aguardar processamento (buffer 13s + processamento 5s)
        print(f"\n  ⏳ Aguardando processamento (20s)...")
        time.sleep(20)

        # Verificar resposta
        conversas = verificar_contexto(customer_id)

        if conversas:
            ultima_conversa = conversas[0]
            resposta = ultima_conversa['agent_response']

            print(f"\n  🤖 Gabi: {resposta[:200]}...")

            # Analisar contexto
            if i >= 2:  # A partir da rodada 2, deve chamar pelo nome
                problemas = analisar_resposta(resposta, USUARIO_TESTE['nome'])

                if problemas:
                    print(f"\n  ❌ PROBLEMAS ENCONTRADOS:")
                    for problema in problemas:
                        print(f"     {problema}")
                    erros_contexto.extend(problemas)
                else:
                    print(f"\n  ✅ Contexto mantido!")

            total_conversas_salvas = len(conversas)
        else:
            print(f"\n  ❌ Nenhuma conversa salva ainda!")

        # Delay entre rodadas
        if i < len(CONVERSAS):
            print(f"\n  ⏸️ Aguardando 5s antes da próxima rodada...")
            time.sleep(5)

    # Relatório final
    print("\n" + "="*70)
    print("📊 RELATÓRIO FINAL")
    print("="*70)
    print(f"✅ Rodadas completadas: {len(CONVERSAS)}")
    print(f"💾 Conversas salvas: {total_conversas_salvas}")
    print(f"⚠️ Problemas de contexto: {len(erros_contexto)}")

    if erros_contexto:
        print(f"\n❌ PROBLEMAS ENCONTRADOS ({len(erros_contexto)}):")
        for erro in set(erros_contexto):
            print(f"  {erro}")
    else:
        print(f"\n🎉 TESTE PASSOU! Contexto mantido em todas as rodadas!")

    print("="*70)

    # Mostrar últimas conversas
    print("\n📜 ÚLTIMAS 5 CONVERSAS:")
    conversas = verificar_contexto(customer_id)
    for i, conv in enumerate(conversas[:5], 1):
        print(f"\n  {i}. Usuário: {conv['user_message'][:80]}...")
        print(f"     Gabi: {conv['agent_response'][:80]}...")

if __name__ == "__main__":
    executar_teste()
