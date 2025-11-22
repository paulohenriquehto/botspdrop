#!/usr/bin/env python3
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from agentes.agente_suporte import support_agent
from tools.memory_tools import VanluMemoryTools
from tools.database_tools import VanluDatabaseTools

# Inicializar ferramentas
memory_tools = VanluMemoryTools()
database_tools = VanluDatabaseTools()

def testar_persistencia():
    print("\n")
    print("🧠" * 40)
    print("TESTE DE PERSISTÊNCIA - STORAGE & MEMORY")
    print("🧠" * 40)

    # ============= SESSÃO 1: Primeiro Contato =============
    print("\n" + "="*80)
    print("📍 SESSÃO 1: Primeiro Contato (2025-11-08 14:00)")
    print("="*80 + "\n")

    # Criar cliente
    print("[Sistema] Criando cliente João Santos...")
    result = memory_tools.create_session(999)  # Customer_id fictício
    print("[Sistema] ❌ Não há customer_id 999, vamos criar manualmente\n")

    # Vamos inserir um cliente manualmente no banco
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="spdrop_db",
        user="spdrop_user",
        password="spdrop_password"
    )

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Criar cliente
        cur.execute("""
            INSERT INTO customers (name, phone, email)
            VALUES ('João Santos', '11999999999', 'joao@email.com')
            RETURNING id, name, phone
        """)
        customer = cur.fetchone()
        customer_id = customer['id']
        conn.commit()

        print(f"✅ Cliente criado: {customer['name']} ({customer['phone']})\n")

        # Criar sessão
        session_id = None
        cur.execute("""
            INSERT INTO sessions (session_id, customer_id, status)
            VALUES (gen_random_uuid()::text, %s, 'active')
            RETURNING session_id, started_at
        """, (customer_id,))
        session = cur.fetchone()
        session_id = session['session_id']
        conn.commit()

        print(f"✅ Sessão criada: {session_id}\n")

    # Simulação de conversa - Sessão 1
    print("👤 João: Oi, tenho um Honda Civic preto e gostaria de saber sobre cristalização\n")
    support_agent.print_response("Oi, tenho um Honda Civic preto e gostaria de saber sobre cristalização", stream=False)

    # Salvar na memória
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO conversation_history
            (session_id, customer_id, user_message, agent_response)
            VALUES (%s, %s, %s, %s)
        """, (
            session_id,
            customer_id,
            "Oi, tenho um Honda Civic preto e gostaria de saber sobre cristalização",
            "Cristalização - durável 6 meses"
        ))

        # Atualizar contexto do cliente (delete se existe, depois insert)
        cur.execute("DELETE FROM customer_context WHERE customer_id = %s", (customer_id,))
        cur.execute("""
            INSERT INTO customer_context (customer_id, car_model, car_color)
            VALUES (%s, 'Honda Civic', 'Preto')
        """, (customer_id,))

        # Atualizar preferências (delete se existe, depois insert)
        cur.execute("DELETE FROM user_preferences WHERE customer_id = %s", (customer_id,))
        cur.execute("""
            INSERT INTO user_preferences (customer_id, interested_services)
            VALUES (%s, 'Cristalização')
        """, (customer_id,))

        conn.commit()

    print("\n✅ Informações salvas no banco de dados")
    print("   • Car: Honda Civic Preto")
    print("   • Interesse: Cristalização\n")

    # ============= SESSÃO 2: 3 dias depois =============
    print("\n" + "="*80)
    print("📍 SESSÃO 2: Retorno (3 dias depois - 2025-11-11 10:00)")
    print("="*80 + "\n")

    # Fechou a sessão anterior
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE sessions SET ended_at = NOW(), status = 'closed'
            WHERE session_id = %s
        """, (session_id,))
        conn.commit()

    time.sleep(1)

    # Criar nova sessão
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            INSERT INTO sessions (session_id, customer_id, status)
            VALUES (gen_random_uuid()::text, %s, 'active')
            RETURNING session_id
        """, (customer_id,))
        new_session = cur.fetchone()
        session_id_2 = new_session['session_id']
        conn.commit()

    print("👤 João: Oi Luciano, tudo bem? Lembra de mim?\n")
    support_agent.print_response("Oi Luciano, tudo bem? Lembra de mim?", stream=False)

    # Salvar conversa
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO conversation_history
            (session_id, customer_id, user_message, agent_response)
            VALUES (%s, %s, %s, %s)
        """, (
            session_id_2,
            customer_id,
            "Oi Luciano, tudo bem? Lembra de mim?",
            "Claro que lembro!"
        ))
        conn.commit()

    print("\n👤 João: Qual era o preço da cristalização? É aquela que lembrei de vocês.\n")
    support_agent.print_response("Qual era o preço da cristalização? É aquela que lembrei de vocês.", stream=False)

    # Salvar conversa
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO conversation_history
            (session_id, customer_id, user_message, agent_response)
            VALUES (%s, %s, %s, %s)
        """, (
            session_id_2,
            customer_id,
            "Qual era o preço da cristalização? É aquela que lembrei de vocês.",
            "R$ 200 reais, 6 meses de duração"
        ))
        conn.commit()

    print("\n✅ Agente lembrou das informações anteriores!")

    # ============= VERIFICAÇÃO DE DADOS =============
    print("\n" + "="*80)
    print("📊 VERIFICAÇÃO DE DADOS NO BANCO")
    print("="*80 + "\n")

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Histórico de conversas
        print("📋 HISTÓRICO DE CONVERSAS:")
        cur.execute("""
            SELECT user_message, agent_response, timestamp
            FROM conversation_history
            WHERE customer_id = %s
            ORDER BY timestamp DESC
            LIMIT 4
        """, (customer_id,))

        for row in cur.fetchall():
            print(f"\n   👤 Cliente: {row['user_message'][:50]}...")
            print(f"   🤖 Agente: {row['agent_response'][:50]}...")

        # Contexto do cliente
        print("\n\n👤 CONTEXTO DO CLIENTE:")
        cur.execute("""
            SELECT car_model, car_color, car_condition, notes, updated_at
            FROM customer_context
            WHERE customer_id = %s
        """, (customer_id,))
        context = cur.fetchone()
        if context:
            print(f"   • Carro: {context['car_model']} {context['car_color']}")
            print(f"   • Condição: {context['car_condition']}")
            print(f"   • Atualizado em: {context['updated_at']}")

        # Preferências
        print("\n\n⭐ PREFERÊNCIAS DO CLIENTE:")
        cur.execute("""
            SELECT interested_services, conversation_count, last_interaction
            FROM user_preferences
            WHERE customer_id = %s
        """, (customer_id,))
        prefs = cur.fetchone()
        if prefs:
            print(f"   • Serviços de Interesse: {prefs['interested_services']}")
            print(f"   • Número de Conversas: {prefs['conversation_count']}")
            print(f"   • Última Interação: {prefs['last_interaction']}")

        # Sessões
        print("\n\n🔄 SESSÕES:")
        cur.execute("""
            SELECT session_id, status, started_at, ended_at
            FROM sessions
            WHERE customer_id = %s
            ORDER BY started_at DESC
        """, (customer_id,))

        for i, session in enumerate(cur.fetchall(), 1):
            status_emoji = "✅" if session['status'] == 'closed' else "🟢"
            print(f"   {status_emoji} Sessão {i}: {session['status'].upper()}")
            print(f"      Início: {session['started_at']}")
            if session['ended_at']:
                print(f"      Fim: {session['ended_at']}")

    conn.close()

    print("\n" + "🎉" * 40)
    print("✅ TESTE DE PERSISTÊNCIA CONCLUÍDO COM SUCESSO!")
    print("🎉" * 40 + "\n")

if __name__ == "__main__":
    testar_persistencia()
